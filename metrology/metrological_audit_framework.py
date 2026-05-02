"""
metrological_audit_framework.py

CANONICAL DATA STRUCTURE for Earth-systems measurement audit.

Goal:    Stop publishing measurement-drift artifacts as physical findings.
Method:  Every measurement carries its own provenance, uncertainty,
         methodology, and known bias. Unknowns are marked explicitly,
         never guessed.

Storage: Plain text (JSON-serializable). Survives format rot because
         it can be parsed by any tool in any future language. The schema is
         additive -- new columns can be appended forever, old rows stay valid
         with NaN/unknown for newly-added columns.

Three core classes:
    1. MeasurementEra            -- defines what instrument/methodology was
                                    in use during a date range, with
                                    documented bias.
    2. CalibrationVectorEntry    -- one row of the matrix. One event.
                                    Carries all variables it has, marks
                                    unknowns.
    3. SurrogateCalibrationCurve -- transfer function from a surrogate
                                    measurement (e.g. newspaper report)
                                    to the true physical value, derived
                                    from modern dual-stream data and
                                    applied backward.

Designed to be pure-stdlib Python. No external dependencies.
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Optional, Any
import json
import math


# =============================================================================
# 1. MEASUREMENT ERA
# =============================================================================

@dataclass
class MeasurementEra:
    """A defined period of stable measurement methodology.

    When the methodology changes, a new era begins. Eras are non-overlapping
    in time. Every CalibrationVectorEntry references exactly one era for
    each variable it measures.
    """
    name: str                      # e.g. "WSR-88D + EF-scale (2007-present)"
    domain: str                    # e.g. "tornado_intensity"
    start_year: int
    end_year: Optional[int]        # None means "still active"
    instrument: str                # e.g. "WSR-88D Doppler radar"
    methodology: str               # e.g. "EF-scale 28 DI + 8 DoD damage survey"
    uncertainty_model: str         # e.g. "rating +/-0.3 EF, vorticity +/-0.008 s^-1"
    known_biases: list[str] = field(default_factory=list)
    source_documents: list[str] = field(default_factory=list)
    notes: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "MeasurementEra":
        return cls(**d)


# =============================================================================
# 2. CALIBRATION VECTOR ENTRY (one row of the matrix)
# =============================================================================

# Sentinel values
UNKNOWN = None      # variable was not measured (instrument didn't exist)
INFINITE_UNC = math.inf   # variable measured but uncertainty unbounded


@dataclass
class MeasuredValue:
    """A single measurement with full provenance.

    NEVER store a bare number. Always store this wrapper so the
    measurement carries its own audit trail.
    """
    value: Optional[float]              # the measurement; None = unknown
    unit: str                           # e.g. "EF_rating", "acres", "vorticity_s^-1"
    uncertainty: float                  # +/- value, in same unit. inf = unbounded
    measurement_era_name: str           # which era's methodology applied
    derivation_method: str = "direct"   # "direct" | "surrogate_calibrated" |
                                        # "physics_inferred" | "newspaper_archive"
    calibration_curve_applied: Optional[str] = None
    data_quality: str = "raw"           # "raw" | "legacy_reconstructed" |
                                        # "model_inferred" | "estimated_with_dark_data"
    schema_version: str = "1.0"

    def to_dict(self) -> dict:
        d = asdict(self)
        # JSON can't serialize math.inf; replace with sentinel string
        if d["uncertainty"] == math.inf:
            d["uncertainty"] = "inf"
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "MeasuredValue":
        d = dict(d)
        if d.get("uncertainty") == "inf":
            d["uncertainty"] = math.inf
        return cls(**d)


@dataclass
class CalibrationVectorEntry:
    """One event in the canonical archive. One tornado, one fire, one quake.

    The variables dict is OPEN -- new variables can be added at any time
    without breaking old entries. Old entries simply have no key for
    variables that didn't exist in their era. Readers MUST handle missing
    keys gracefully (treat as UNKNOWN).
    """
    event_id: str                       # globally unique, e.g. "fire_us_1894_hinckley_mn"
    domain: str                         # "wildfire" | "tornado" | "earthquake" | etc
    timestamp: str                      # ISO 8601, with uncertainty separate
    timestamp_uncertainty_seconds: float
    location_lat: Optional[float]
    location_lon: Optional[float]
    location_uncertainty_meters: float
    variables: dict[str, MeasuredValue] = field(default_factory=dict)
    notes: str = ""
    schema_version: str = "1.0"

    def get(self, variable_name: str) -> Optional[MeasuredValue]:
        """Return measurement for a variable, or None if not measured."""
        return self.variables.get(variable_name)

    def set(self, variable_name: str, mv: MeasuredValue) -> None:
        """Add or update a measurement for a variable."""
        self.variables[variable_name] = mv

    def to_dict(self) -> dict:
        d = asdict(self)
        d["variables"] = {k: v.to_dict() for k, v in self.variables.items()}
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "CalibrationVectorEntry":
        d = dict(d)
        vars_dict = d.pop("variables", {})
        entry = cls(**d, variables={})
        for name, mv_dict in vars_dict.items():
            entry.variables[name] = MeasuredValue.from_dict(mv_dict)
        return entry

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)


# =============================================================================
# 3. SURROGATE CALIBRATION CURVE
# =============================================================================

@dataclass
class SurrogateCalibrationCurve:
    """Transfer function from a surrogate measurement to the true physical
    value, derived from modern dual-stream data.

    Example: in 2007-2024, we have BOTH official EF ratings AND newspaper
    reports for the same tornadoes. Build a curve: newspaper_report -> true_EF
    with documented bias and spread. Apply that curve backward to 1880-1950
    where we ONLY have newspaper reports.

    Curve representation: piecewise linear with explicit uncertainty.
    """
    surrogate_name: str                 # e.g. "newspaper_archive_1880-1950"
    target_variable: str                # e.g. "tornado_EF_rating"
    surrogate_unit: str                 # e.g. "newspaper_descriptive_score_1to5"
    target_unit: str                    # e.g. "EF_rating"
    breakpoints: list[tuple[float, float, float]] = field(default_factory=list)
    # Each breakpoint: (surrogate_value, mean_target_value, target_uncertainty)
    n_calibration_samples: int = 0
    derivation_method: str = "modern_dual_stream"
    derivation_notes: str = ""

    def apply(self, surrogate_value: float) -> tuple[float, float]:
        """Apply curve to a surrogate measurement.

        Returns (estimated_target_value, uncertainty).
        Uses linear interpolation between breakpoints.
        Uncertainty includes both curve-fitting error and base spread.
        """
        bps = sorted(self.breakpoints, key=lambda b: b[0])
        if not bps:
            return (math.nan, math.inf)

        # Below or above range: use endpoint with inflated uncertainty
        if surrogate_value <= bps[0][0]:
            return (bps[0][1], bps[0][2] * 1.5)
        if surrogate_value >= bps[-1][0]:
            return (bps[-1][1], bps[-1][2] * 1.5)

        # Interpolate
        for i in range(len(bps) - 1):
            s_lo, t_lo, u_lo = bps[i]
            s_hi, t_hi, u_hi = bps[i + 1]
            if s_lo <= surrogate_value <= s_hi:
                frac = (surrogate_value - s_lo) / (s_hi - s_lo)
                t_est = t_lo + frac * (t_hi - t_lo)
                u_est = u_lo + frac * (u_hi - u_lo)
                return (t_est, u_est)
        return (math.nan, math.inf)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "SurrogateCalibrationCurve":
        d = dict(d)
        d["breakpoints"] = [tuple(b) for b in d.get("breakpoints", [])]
        return cls(**d)


# =============================================================================
# DEMONSTRATION -- minimum viable example
# =============================================================================

if __name__ == "__main__":
    # Define a measurement era for clean-era tornado intensity
    era_ef = MeasurementEra(
        name="WSR-88D + EF-scale (2007-present)",
        domain="tornado_intensity",
        start_year=2007,
        end_year=None,
        instrument="WSR-88D Doppler radar + ground damage survey",
        methodology="EF-scale 28 Damage Indicators, 8 Degrees of Damage",
        uncertainty_model="EF rating +/-0.3, vorticity +/-0.008 s^-1",
        known_biases=[
            "rural tornadoes still under-rated when no damage indicators present",
            "EF5 threshold revised downward from F5 (200+ vs 261-318 mph)",
        ],
        source_documents=[
            "https://www.spc.noaa.gov/efscale/",
            "WSR-88D Operational Manual NWSI 10-1306",
        ],
    )

    # Define a legacy era for comparison
    era_fujita = MeasurementEra(
        name="Pre-Doppler + Fujita scale (1950-1990)",
        domain="tornado_intensity",
        start_year=1950,
        end_year=1990,
        instrument="Ground spotters, photographs, damage surveys",
        methodology="Fujita F-scale subjective damage rating",
        uncertainty_model="rating +/-0.8 F, vorticity unmeasured",
        known_biases=[
            "rural tornadoes systematically under-detected",
            "F-scale wind speeds later found to be ~30% too high",
            "F5 ratings inflated relative to modern EF5 standard",
            "weak tornadoes (F0/F1) under-counted in sparse population areas",
        ],
        source_documents=[
            "Fujita 1971 SMRP Research Paper 91",
            "SPC Tornado Database Documentation",
        ],
    )

    # Build a sample entry: 2011 Joplin tornado (clean era)
    joplin = CalibrationVectorEntry(
        event_id="tornado_us_20110522_joplin_mo",
        domain="tornado",
        timestamp="2011-05-22T22:34:00Z",
        timestamp_uncertainty_seconds=60,
        location_lat=37.0842,
        location_lon=-94.5133,
        location_uncertainty_meters=20,
    )
    joplin.set("ef_rating", MeasuredValue(
        value=5.0,
        unit="EF_rating",
        uncertainty=0.3,
        measurement_era_name=era_ef.name,
        derivation_method="direct",
        data_quality="raw",
    ))
    joplin.set("path_length", MeasuredValue(
        value=22.1,
        unit="miles",
        uncertainty=0.2,
        measurement_era_name=era_ef.name,
        derivation_method="direct",
        data_quality="raw",
    ))
    joplin.set("peak_vorticity", MeasuredValue(
        value=0.142,
        unit="s^-1",
        uncertainty=0.008,
        measurement_era_name=era_ef.name,
        derivation_method="direct",
        data_quality="raw",
    ))

    # Build a legacy entry: 1925 Tri-State tornado
    # Many variables are unknown (instruments didn't exist).
    # Some are derived from newspaper accounts via surrogate calibration.
    tristate = CalibrationVectorEntry(
        event_id="tornado_us_19250318_tristate",
        domain="tornado",
        timestamp="1925-03-18T18:00:00Z",
        timestamp_uncertainty_seconds=900,  # +/-15 min from newspaper accounts
        location_lat=37.7,
        location_lon=-89.2,
        location_uncertainty_meters=2000,
    )
    # F-scale rating from later expert review -- has its own era
    tristate.set("ef_rating", MeasuredValue(
        value=5.0,
        unit="EF_rating",
        uncertainty=0.8,
        measurement_era_name=era_fujita.name,
        derivation_method="legacy_reconstructed",
        calibration_curve_applied="fujita_to_ef_recalibration_1971_2007",
        data_quality="legacy_reconstructed",
    ))
    tristate.set("path_length", MeasuredValue(
        value=219.0,
        unit="miles",
        uncertainty=15.0,  # large; based on damage track survey
        measurement_era_name=era_fujita.name,
        derivation_method="newspaper_archive",
        data_quality="legacy_reconstructed",
    ))
    # peak_vorticity not set -- instrument didn't exist
    # Reader will see: tristate.get("peak_vorticity") -> None -> UNKNOWN

    # Demonstrate a surrogate calibration curve
    # Hypothetical: newspaper "severity adjective" 1-5 -> true EF rating
    newspaper_curve = SurrogateCalibrationCurve(
        surrogate_name="newspaper_severity_adjective_1880-1950",
        target_variable="ef_rating",
        surrogate_unit="severity_score_1to5",
        target_unit="EF_rating",
        breakpoints=[
            (1.0, 0.5, 0.5),   # "small"        -> ~EF0.5 +/- 0.5
            (2.0, 1.5, 0.6),   # "moderate"     -> ~EF1.5 +/- 0.6
            (3.0, 2.5, 0.7),   # "severe"       -> ~EF2.5 +/- 0.7
            (4.0, 3.5, 0.8),   # "violent"      -> ~EF3.5 +/- 0.8
            (5.0, 4.5, 0.9),   # "catastrophic" -> ~EF4.5 +/- 0.9
        ],
        n_calibration_samples=0,  # placeholder -- must be derived from real data
        derivation_method="placeholder_template",
        derivation_notes="Stub curve. Populate from modern dual-stream "
                         "(newspaper text + official EF rating, 2007-2024).",
    )

    # Demonstrate applying the curve
    estimated_ef, uncertainty = newspaper_curve.apply(3.5)

    # Print what we built
    print("=" * 70)
    print("METROLOGICAL AUDIT FRAMEWORK -- DEMONSTRATION")
    print("=" * 70)
    print()
    print("ERAS DEFINED:")
    print(f"  [{era_ef.start_year}-now]  {era_ef.name}")
    print(f"  [{era_fujita.start_year}-{era_fujita.end_year}]  {era_fujita.name}")
    print()
    print("SAMPLE CLEAN-ERA ENTRY (Joplin 2011):")
    print(joplin.to_json())
    print()
    print("SAMPLE LEGACY ENTRY (Tri-State 1925):")
    print(tristate.to_json())
    print()
    print("note: peak_vorticity is absent because instrument didn't exist.")
    print(f"       reader gets: {tristate.get('peak_vorticity')!r}")
    print()
    print("SURROGATE CURVE APPLIED:")
    print(f"  newspaper severity 3.5 -> estimated EF {estimated_ef:.2f} "
          f"+/- {uncertainty:.2f}")
    print()
    print("=" * 70)
    print("FRAMEWORK READY. POPULATE WITH REAL DATA.")
    print("=" * 70)
