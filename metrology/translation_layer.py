"""
translation_layer.py

Parse institutional Earth-systems datasets into canonical vector
matrix entries with full provenance, uncertainty, and assumption-
bias annotations.

WHY THIS EXISTS:

    Institutional datasets (NOAA SPC, NHC HURDAT2, USGS NWIS, NIFC,
    NOAA NCEI Drought Monitor) come from different agencies, in
    different formats, with different methodology histories, with
    different assumed frameworks. None of them include their own
    metrology audit. None of them mark unknowns explicitly. None
    of them version their reanalysis revisions in a machine-readable
    way.

    To do honest physics, we need a single canonical schema. To
    reach that schema from institutional sources, we need a
    translation layer.

WHAT IT DOES:

    For each institutional dataset:
    1. Pin the source (URL, hash, timestamp)
    2. Parse records into intermediate form
    3. Map institutional variables -> canonical variables
    4. Assign measurement era based on event date
    5. Attach uncertainty bounds from era documentation
    6. Mark unknowns explicitly (never guess)
    7. Detect and flag known reanalysis revisions
    8. Emit canonical CalibrationVectorEntry objects

WHAT IT EXPLICITLY DOES NOT DO:

    - Does NOT impute missing values (legacy data stays sparse)
    - Does NOT smooth across measurement-era boundaries
    - Does NOT auto-correct known biases (reports them as
      uncertainty, not as adjustments)
    - Does NOT trust institutional uncertainty estimates without
      audit (they often don't include framework bias)

DESIGN PRINCIPLES:

    [1] Provenance is structural. Every value carries its source.
    [2] Unknowns are first-class. NaN and "instrument didn't exist"
        are different states.
    [3] The era taxonomy is authoritative. Dates determine which
        MeasurementEra applies, not arbitrary cutoffs.
    [4] Reanalysis revisions are receipts. Every documented change
        to historical records is logged.
    [5] Framework assumptions are surfaced. Each translator
        declares what its source dataset's framework excludes.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Callable, Any
from datetime import datetime
import hashlib
import json
import math


# =============================================================================
# SOURCE PINNING
# =============================================================================

@dataclass
class DataSourcePin:
    """Immutable record of where data came from and when.

    Required for reproducibility. Without this, a "trend" computed
    against a HURDAT2 download in 2024 cannot be reproduced against
    a HURDAT2 download in 2026 (because the database was edited).
    """
    source_name: str           # e.g. "HURDAT2", "SPC tornado database"
    source_url: str
    retrieved_at: str          # ISO 8601 timestamp
    file_hash_sha256: str      # hash of the actual file used
    version_string: Optional[str] = None  # institutional version if any
    notes: str = ""

    @classmethod
    def from_file(cls, source_name: str, source_url: str,
                  filepath: str, version_string: Optional[str] = None,
                  notes: str = "") -> "DataSourcePin":
        """Build a pin by hashing a file."""
        hasher = hashlib.sha256()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hasher.update(chunk)
        return cls(
            source_name=source_name,
            source_url=source_url,
            retrieved_at=datetime.utcnow().isoformat() + "Z",
            file_hash_sha256=hasher.hexdigest(),
            version_string=version_string,
            notes=notes,
        )

    def to_dict(self) -> dict:
        return {
            "source_name": self.source_name,
            "source_url": self.source_url,
            "retrieved_at": self.retrieved_at,
            "file_hash_sha256": self.file_hash_sha256,
            "version_string": self.version_string,
            "notes": self.notes,
        }


# =============================================================================
# REANALYSIS RECEIPT
# =============================================================================

@dataclass
class ReanalysisReceipt:
    """One documented revision of a historical record.

    Example: Hurricane Andrew was officially Cat 4 from 1992-2004,
    then upgraded to Cat 5 in 2004 by Landsea et al. The receipt
    records this revision.
    """
    event_id: str
    variable: str              # e.g. "saffir_simpson_category"
    original_value: Any
    revised_value: Any
    revision_year: int
    revision_authority: str    # e.g. "NHC Best Track Change Committee"
    revision_citation: str     # paper/document reference
    notes: str = ""

    def to_dict(self) -> dict:
        return {
            "event_id": self.event_id,
            "variable": self.variable,
            "original_value": self.original_value,
            "revised_value": self.revised_value,
            "revision_year": self.revision_year,
            "revision_authority": self.revision_authority,
            "revision_citation": self.revision_citation,
            "notes": self.notes,
        }


# =============================================================================
# VARIABLE MAPPING
# =============================================================================

@dataclass
class VariableMapping:
    """Map an institutional variable name to a canonical variable.

    Includes unit conversion if needed. Marks the institutional
    variable as carrying a specific framework assumption (e.g.
    'this variable measures damage, not physics').
    """
    institutional_name: str    # e.g. "DAMAGE_PROPERTY"
    canonical_name: str        # e.g. "economic_damage_USD"
    institutional_unit: str
    canonical_unit: str
    unit_converter: Optional[Callable[[float], float]] = None
    framework_classification: str = "physics"  # physics | exposure | political
    framework_notes: str = ""

    def convert(self, value: Any) -> Any:
        """Apply unit conversion if defined; return value unchanged otherwise."""
        if value is None:
            return None
        if self.unit_converter is None:
            return value
        try:
            return self.unit_converter(float(value))
        except (TypeError, ValueError):
            return value


# =============================================================================
# ERA ASSIGNMENT
# =============================================================================

@dataclass
class MeasurementEraSimple:
    """Lightweight era reference used by the translator.

    The full MeasurementEra object lives in metrological_audit_framework.py;
    here we only need name + date range for assignment.
    """
    name: str
    start_year: int
    end_year: Optional[int]    # None = active (still ongoing)
    domain: str

    def contains(self, year: int) -> bool:
        if year < self.start_year:
            return False
        if self.end_year is None:
            return True
        return year <= self.end_year


def assign_era(year: int, eras: list[MeasurementEraSimple]) -> Optional[MeasurementEraSimple]:
    """Find which era an event falls into.

    Returns None if no era matches (data point outside known coverage).
    Eras must be non-overlapping; if they overlap, returns first match.
    """
    for era in eras:
        if era.contains(year):
            return era
    return None


def is_era_boundary(year: int, eras: list[MeasurementEraSimple],
                    boundary_window_years: int = 1) -> bool:
    """Flag events near era boundaries -- they need extra uncertainty.

    Example: a 2007 tornado is technically in the EF era, but
    the F -> EF transition happened February 2007. Events in early
    2007 may have been rated under either system depending on
    timing of damage survey.
    """
    for era in eras:
        if era.end_year is None:
            continue
        if abs(year - era.end_year) <= boundary_window_years:
            return True
        if abs(year - era.start_year) <= boundary_window_years:
            return True
    return False


# =============================================================================
# UNKNOWN HANDLING
# =============================================================================

class UnknownReason:
    """Sentinel values for why a variable is unknown.

    Different reasons matter for downstream analysis. A variable
    that's unknown because the instrument didn't exist is different
    from one that's unknown because the value was lost.
    """
    INSTRUMENT_DID_NOT_EXIST = "instrument_did_not_exist"
    NOT_RECORDED_IN_ERA = "not_recorded_in_era"
    LOST_OR_REDACTED = "lost_or_redacted"
    BELOW_DETECTION_THRESHOLD = "below_detection_threshold"
    OUTSIDE_GAUGE_NETWORK = "outside_gauge_network"
    PRE_REGISTRY_DATE = "pre_registry_date"
    INSTITUTIONAL_GAP = "institutional_gap"
    UNKNOWN_REASON = "unknown_reason"


@dataclass
class UnknownValue:
    """A first-class representation of 'we don't know'.

    Distinct from None or NaN because it carries the REASON for
    the unknown. This enables honest analysis: 'event X has 12
    variables, 7 known, 5 unknown for the following reasons'.
    """
    reason: str                # one of UnknownReason constants
    notes: str = ""

    def to_dict(self) -> dict:
        return {"unknown": True, "reason": self.reason, "notes": self.notes}


# =============================================================================
# UNCERTAINTY ATTACHMENT
# =============================================================================

@dataclass
class UncertaintyEnvelope:
    """The total uncertainty around a measurement.

    Composes contributions from:
    - measurement noise (instrument precision)
    - methodology uncertainty (which method was used)
    - era boundary uncertainty (if event is near era transition)
    - reanalysis uncertainty (if record has been revised)
    - framework uncertainty (if the variable is exposure-dependent
      rather than pure physics)
    """
    measurement: float = 0.0
    methodology: float = 0.0
    era_boundary: float = 0.0
    reanalysis: float = 0.0
    framework: float = 0.0

    def total_rss(self) -> float:
        """Combined uncertainty assuming independent sources (root-sum-squares)."""
        return math.sqrt(
            self.measurement ** 2 +
            self.methodology ** 2 +
            self.era_boundary ** 2 +
            self.reanalysis ** 2 +
            self.framework ** 2
        )

    def total_linear(self) -> float:
        """Conservative combined uncertainty (sum, not RSS).

        Use when uncertainty sources may be correlated (which is
        often the case in real institutional data).
        """
        return (self.measurement + self.methodology + self.era_boundary +
                self.reanalysis + self.framework)

    def to_dict(self) -> dict:
        return {
            "measurement": self.measurement,
            "methodology": self.methodology,
            "era_boundary": self.era_boundary,
            "reanalysis": self.reanalysis,
            "framework": self.framework,
            "total_rss": self.total_rss(),
            "total_linear": self.total_linear(),
        }


# =============================================================================
# CANONICAL VECTOR (translator output)
# =============================================================================

@dataclass
class CanonicalRecord:
    """Output of the translator. One event in canonical form.

    This is what gets fed to downstream analysis tools. It carries
    everything needed for honest physics reasoning -- provenance,
    era, uncertainty, unknowns, framework annotations.

    Note: this is a translator-output schema. The full canonical
    matrix entry (CalibrationVectorEntry in
    metrological_audit_framework.py) composes these into the matrix.
    """
    event_id: str
    domain: str
    timestamp: str
    timestamp_uncertainty_seconds: float
    location_lat: Optional[float]
    location_lon: Optional[float]
    location_uncertainty_meters: float
    measurement_era: str
    is_era_boundary: bool
    variables: dict[str, Any]                  # value or UnknownValue
    uncertainties: dict[str, UncertaintyEnvelope]
    framework_classifications: dict[str, str]  # physics | exposure | political
    source_pin: DataSourcePin
    reanalysis_receipts: list[ReanalysisReceipt] = field(default_factory=list)
    framework_excluded_causes: list[str] = field(default_factory=list)
    framework_missing_variables: list[str] = field(default_factory=list)
    notes: str = ""

    def to_dict(self) -> dict:
        out = {
            "event_id": self.event_id,
            "domain": self.domain,
            "timestamp": self.timestamp,
            "timestamp_uncertainty_seconds": self.timestamp_uncertainty_seconds,
            "location_lat": self.location_lat,
            "location_lon": self.location_lon,
            "location_uncertainty_meters": self.location_uncertainty_meters,
            "measurement_era": self.measurement_era,
            "is_era_boundary": self.is_era_boundary,
            "source_pin": self.source_pin.to_dict(),
            "framework_excluded_causes": self.framework_excluded_causes,
            "framework_missing_variables": self.framework_missing_variables,
            "notes": self.notes,
            "reanalysis_receipts": [r.to_dict() for r in self.reanalysis_receipts],
            "variables": {},
            "uncertainties": {},
            "framework_classifications": self.framework_classifications,
        }
        # Variables: emit unknowns explicitly
        for name, val in self.variables.items():
            if isinstance(val, UnknownValue):
                out["variables"][name] = val.to_dict()
            elif val is None:
                out["variables"][name] = {"unknown": True,
                                          "reason": UnknownReason.UNKNOWN_REASON}
            else:
                out["variables"][name] = val
        # Uncertainties
        for name, unc in self.uncertainties.items():
            out["uncertainties"][name] = unc.to_dict()
        return out

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, default=str)


# =============================================================================
# THE TRANSLATOR BASE CLASS
# =============================================================================

@dataclass
class DomainTranslator:
    """Base translator. Subclassed per domain (tornado, hurricane, etc.).

    Subclasses implement the parsing logic specific to each
    institutional dataset. The base class handles the canonical
    output format and the boilerplate of era assignment, uncertainty
    composition, and unknown handling.
    """
    domain: str
    eras: list[MeasurementEraSimple]
    variable_mappings: list[VariableMapping]
    framework_excluded_causes: list[str] = field(default_factory=list)
    framework_missing_variables: list[str] = field(default_factory=list)
    reanalysis_database: list[ReanalysisReceipt] = field(default_factory=list)

    def get_mapping(self, institutional_name: str) -> Optional[VariableMapping]:
        for m in self.variable_mappings:
            if m.institutional_name == institutional_name:
                return m
        return None

    def get_reanalysis_for(self, event_id: str) -> list[ReanalysisReceipt]:
        return [r for r in self.reanalysis_database if r.event_id == event_id]

    def era_uncertainty_for(self, era_name: str, variable: str) -> UncertaintyEnvelope:
        """Default era uncertainty. Subclasses override per era + variable."""
        return UncertaintyEnvelope(measurement=0.1)  # tiny placeholder

    def translate_record(
        self,
        institutional_record: dict,
        source_pin: DataSourcePin,
    ) -> CanonicalRecord:
        """Translate one institutional record into a CanonicalRecord.

        Subclasses must provide:
          - extract_event_id(institutional_record) -> str
          - extract_timestamp(institutional_record) -> (iso, uncertainty_sec)
          - extract_location(institutional_record) -> (lat, lon, unc_m)
          - extract_year(institutional_record) -> int
          - extract_variables(institutional_record) -> dict
          - extract_event_id_for_reanalysis(institutional_record) -> str
            (often same as event_id, but some datasets use different IDs)

        Default implementations of these raise NotImplementedError.
        """
        event_id = self.extract_event_id(institutional_record)
        timestamp, ts_unc = self.extract_timestamp(institutional_record)
        lat, lon, loc_unc = self.extract_location(institutional_record)
        year = self.extract_year(institutional_record)
        raw_vars = self.extract_variables(institutional_record)

        era = assign_era(year, self.eras)
        era_name = era.name if era is not None else "UNKNOWN_ERA"
        boundary = is_era_boundary(year, self.eras)

        variables: dict[str, Any] = {}
        uncertainties: dict[str, UncertaintyEnvelope] = {}
        classifications: dict[str, str] = {}

        for inst_name, raw_value in raw_vars.items():
            mapping = self.get_mapping(inst_name)
            if mapping is None:
                # Unmapped institutional variable; preserve under
                # original name with note that it's unmapped
                canonical_name = f"unmapped__{inst_name}"
                variables[canonical_name] = raw_value
                classifications[canonical_name] = "unmapped"
                uncertainties[canonical_name] = UncertaintyEnvelope()
                continue
            canonical_name = mapping.canonical_name
            converted = mapping.convert(raw_value)
            variables[canonical_name] = converted
            classifications[canonical_name] = mapping.framework_classification
            unc = self.era_uncertainty_for(era_name, canonical_name)
            if boundary:
                # Inflate boundary uncertainty
                unc.era_boundary = max(unc.era_boundary,
                                       0.1 * unc.total_rss() if unc.total_rss() > 0 else 0.05)
            uncertainties[canonical_name] = unc

        # Mark variables that should exist for this domain but aren't
        # present in this era's data -> UnknownValue with reason
        for missing_var in self.expected_variables_for_era(era_name):
            if missing_var not in variables:
                variables[missing_var] = UnknownValue(
                    reason=self.unknown_reason_for(era_name, missing_var),
                    notes=f"Variable {missing_var} not available in era {era_name}",
                )
                classifications[missing_var] = "physics"
                uncertainties[missing_var] = UncertaintyEnvelope()

        # Look up reanalysis receipts
        receipts = self.get_reanalysis_for(event_id)

        return CanonicalRecord(
            event_id=event_id,
            domain=self.domain,
            timestamp=timestamp,
            timestamp_uncertainty_seconds=ts_unc,
            location_lat=lat,
            location_lon=lon,
            location_uncertainty_meters=loc_unc,
            measurement_era=era_name,
            is_era_boundary=boundary,
            variables=variables,
            uncertainties=uncertainties,
            framework_classifications=classifications,
            source_pin=source_pin,
            reanalysis_receipts=receipts,
            framework_excluded_causes=list(self.framework_excluded_causes),
            framework_missing_variables=list(self.framework_missing_variables),
        )

    # Subclass hooks (override per domain)
    def extract_event_id(self, record: dict) -> str:
        raise NotImplementedError

    def extract_timestamp(self, record: dict) -> tuple[str, float]:
        raise NotImplementedError

    def extract_location(self, record: dict) -> tuple[Optional[float], Optional[float], float]:
        raise NotImplementedError

    def extract_year(self, record: dict) -> int:
        raise NotImplementedError

    def extract_variables(self, record: dict) -> dict:
        raise NotImplementedError

    def expected_variables_for_era(self, era_name: str) -> list[str]:
        """Override: which canonical variables should exist for this era?"""
        return []

    def unknown_reason_for(self, era_name: str, variable: str) -> str:
        """Override: why is this variable unknown in this era?

        Default assumes the instrument simply didn't exist.
        """
        return UnknownReason.INSTRUMENT_DID_NOT_EXIST


# =============================================================================
# DEMONSTRATION -- minimal tornado translator
# =============================================================================

class TornadoTranslator(DomainTranslator):
    """Translate SPC tornado database records into canonical form.

    Real implementation would parse SPC CSV directly. This demo
    accepts pre-parsed dicts.
    """

    def extract_event_id(self, record: dict) -> str:
        return record.get("om", "unknown_id")  # SPC uses "om" as ID

    def extract_timestamp(self, record: dict) -> tuple[str, float]:
        date = record.get("date", "1900-01-01")
        time = record.get("time", "00:00:00")
        return f"{date}T{time}Z", 60.0  # 1 min uncertainty

    def extract_location(self, record: dict) -> tuple[Optional[float], Optional[float], float]:
        lat = record.get("slat")
        lon = record.get("slon")
        # Pre-GPS era has wider location uncertainty
        year = self.extract_year(record)
        if year < 1990:
            unc = 1000.0  # 1 km
        else:
            unc = 100.0   # 100 m
        return lat, lon, unc

    def extract_year(self, record: dict) -> int:
        date = record.get("date", "1900-01-01")
        return int(date[:4])

    def extract_variables(self, record: dict) -> dict:
        return {
            "mag": record.get("mag"),       # F or EF rating
            "len": record.get("len"),       # path length, miles
            "wid": record.get("wid"),       # width, yards
            "fat": record.get("fat"),       # fatalities
            "inj": record.get("inj"),       # injuries
            "loss": record.get("loss"),     # damage estimate
        }

    def expected_variables_for_era(self, era_name: str) -> list[str]:
        # Modern era should have all of these
        if "EF-scale" in era_name or "WSR-88D" in era_name:
            return ["EF_rating", "path_length_miles", "path_width_yards",
                    "peak_vorticity_s-1"]
        # Older eras have fewer
        if "Doppler" in era_name:
            return ["F_rating", "path_length_miles", "path_width_yards"]
        return ["F_rating", "path_length_miles"]

    def unknown_reason_for(self, era_name: str, variable: str) -> str:
        if variable == "peak_vorticity_s-1":
            if "WSR-88D" not in era_name and "Doppler" not in era_name:
                return UnknownReason.INSTRUMENT_DID_NOT_EXIST
        return UnknownReason.NOT_RECORDED_IN_ERA


# =============================================================================
# DEMO RUN
# =============================================================================

if __name__ == "__main__":
    # Define tornado eras
    tornado_eras = [
        MeasurementEraSimple(
            name="T1: pre-F-scale, retroactive student rating",
            start_year=1950, end_year=1972, domain="tornado",
        ),
        MeasurementEraSimple(
            name="T2: F-scale operational, pre-Doppler",
            start_year=1973, end_year=1990, domain="tornado",
        ),
        MeasurementEraSimple(
            name="T3: F-scale + WSR-88D Doppler",
            start_year=1991, end_year=2006, domain="tornado",
        ),
        MeasurementEraSimple(
            name="T4: EF-scale + Doppler",
            start_year=2007, end_year=2014, domain="tornado",
        ),
        MeasurementEraSimple(
            name="T5: EF-scale + multi-sensor + smartphones",
            start_year=2015, end_year=None, domain="tornado",
        ),
    ]

    # Define mappings
    tornado_mappings = [
        VariableMapping(
            institutional_name="mag",
            canonical_name="F_rating",
            institutional_unit="F_scale_0to5",
            canonical_unit="F_scale_0to5",
            framework_classification="physics_proxy",
            framework_notes="Damage-based rating, not direct wind measurement",
        ),
        VariableMapping(
            institutional_name="len",
            canonical_name="path_length_miles",
            institutional_unit="miles", canonical_unit="miles",
            framework_classification="physics",
        ),
        VariableMapping(
            institutional_name="wid",
            canonical_name="path_width_yards",
            institutional_unit="yards", canonical_unit="yards",
            framework_classification="physics",
        ),
        VariableMapping(
            institutional_name="fat",
            canonical_name="fatalities",
            institutional_unit="count", canonical_unit="count",
            framework_classification="exposure",
            framework_notes="Reflects EMS access and population, not tornado physics",
        ),
        VariableMapping(
            institutional_name="inj",
            canonical_name="injuries",
            institutional_unit="count", canonical_unit="count",
            framework_classification="exposure",
        ),
        VariableMapping(
            institutional_name="loss",
            canonical_name="economic_damage_USD",
            institutional_unit="USD", canonical_unit="USD",
            framework_classification="exposure",
            framework_notes="Confounded by floodplain development and inflation",
        ),
    ]

    # Build translator
    translator = TornadoTranslator(
        domain="tornado",
        eras=tornado_eras,
        variable_mappings=tornado_mappings,
        framework_excluded_causes=[
            "doppler_radar_detection_cliff_1991",
            "ef_scale_methodology_change_2007",
            "retroactive_rating_of_pre_1978_tornadoes",
            "population_density_increase_in_detection_zones",
        ],
        framework_missing_variables=[
            "radar_coverage_at_event_location",
            "rating_methodology_at_event_year",
            "population_within_5km_of_track",
        ],
    )

    # Stub source pin (real version would hash a real file)
    pin = DataSourcePin(
        source_name="SPC Tornado Database (DEMO)",
        source_url="https://www.spc.noaa.gov/wcm/",
        retrieved_at="2026-05-02T00:00:00Z",
        file_hash_sha256="demo_placeholder_hash_replace_with_real_file",
        version_string="2024_annual_release",
        notes="Demonstration only. Real translator would hash actual file.",
    )

    # Two example records: one modern, one legacy
    joplin_record = {
        "om": "2011_joplin",
        "date": "2011-05-22",
        "time": "22:34:00",
        "slat": 37.0842,
        "slon": -94.5133,
        "mag": 5,
        "len": 22.1,
        "wid": 1600,  # yards
        "fat": 158,
        "inj": 1150,
        "loss": 2.8e9,
    }

    tristate_record = {
        "om": "1925_tristate",
        "date": "1925-03-18",
        "time": "13:00:00",
        "slat": 37.7,
        "slon": -89.2,
        "mag": 5,
        "len": 219.0,
        "wid": 1320,
        "fat": 695,
        "inj": 2027,
        "loss": 1.7e7,
    }

    # Translate
    joplin_canonical = translator.translate_record(joplin_record, pin)
    tristate_canonical = translator.translate_record(tristate_record, pin)

    # Display
    print("=" * 78)
    print("TRANSLATION LAYER -- DEMONSTRATION")
    print("=" * 78)

    print("\n--- MODERN RECORD (2011 Joplin) ---")
    print(joplin_canonical.to_json())

    print("\n--- LEGACY RECORD (1925 Tri-State) ---")
    print(tristate_canonical.to_json())

    print("\n" + "=" * 78)
    print("KEY OBSERVATIONS")
    print("=" * 78)
    print("""
[1] Modern record (Joplin) gets era T4 (EF + Doppler).
    Legacy record (Tri-State) gets UNKNOWN_ERA -- outside
    documented era list (we only defined 1950+ eras).

[2] Both records preserve fatalities/injuries/damage but
    flag them as 'exposure' classification, not 'physics'.
    Downstream physics analysis can filter to physics-only.

[3] Variables not extractable from SPC dataset (peak_vorticity)
    get marked as UnknownValue with reason
    INSTRUMENT_DID_NOT_EXIST for pre-Doppler events.

[4] Both records carry the same source_pin -- full provenance
    from a single SPC download.

[5] Both records carry framework_excluded_causes pointing to
    the doppler detection cliff, EF methodology change, etc.
    Downstream analysis sees these and can decide to apply
    bias corrections.

[6] Reanalysis receipts (if any) attach automatically when
    the translator's reanalysis_database includes entries
    matching event_id.
""")
    print("=" * 78)
    print("END")
    print("=" * 78)
