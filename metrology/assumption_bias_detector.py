"""
assumption_bias_detector.py

Identify FRAMEWORK-level bias in scientific claims, beyond the
measurement-level bias that the metrology audit framework handles.

THE LAYERED CORRUPTION MODEL:

    Layer 1: Instrument bias (radar drift, gauge calibration)
        Detected by: MeasurementEra documentation
        Fixed by:    surrogate calibration curves

    Layer 2: Methodology bias (PDSI vs SPEI, F-scale vs EF-scale)
        Detected by: cross-index comparison
        Fixed by:    standardized methodology declaration

    Layer 3: Reference-period bias (1961-1990 vs 1991-2020 baselines)
        Detected by: baseline switching tests
        Fixed by:    explicit baseline pinning

    Layer 4: ASSUMPTION BIAS (this module)
        Detected by: this tool
        Fixed by:    framework-level reframing

Layer 4 is structural. It can't be fixed by better measurement.
The framework defines which measurements are even considered relevant.
When the framework is wrong, the data collected within it can't
answer questions the framework excluded.

WHAT THIS DETECTS:

    Causal inversion: phenomenon attributed to wrong cause because
    the framework excludes the actual cause as a candidate.

    Examples:
    - Flood damage attributed to climate (framework excludes land-use)
    - "1200-year megadrought" attributed to climate (framework
       excludes CO2 stomatal effects on vegetation)
    - Tornado increase attributed to climate (framework excludes
       detection-cliff from radar deployment)
    - Hurricane intensity attributed to AMO (framework excludes
       reanalysis revisions to historical record)
    - Earthquake increase attributed to "natural variability"
       (framework excludes seismic-coupling to surface forcing)

    Pinnacle assumption: current technology/methodology treated as
    reference standard against which historical practice is judged
    "primitive" or "regressive."

    Examples:
    - Wood roads in boreal wetlands judged "primitive" vs asphalt
       (which fails under permafrost)
    - Meandering streams judged "inefficient" vs straightened
       channels (which amplify peak flow)
    - Wetlands judged "wasted real estate" vs drained land
       (which removes flood buffering)
    - Indigenous fire management judged "primitive" vs total
       suppression (which created fuel-load crisis)

OUTPUT:
    Given a claim and its framework, this module produces:
    1. Identified excluded candidate causes
    2. Identified pinnacle assumptions
    3. Reframed version of the claim with assumption bias surfaced
    4. List of variables that would need to be added to test
       the excluded hypotheses
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
import json


@dataclass
class FrameworkClaim:
    """A scientific claim plus the framework it's embedded in.

    The framework is what makes the claim testable -- but also what
    determines which alternative hypotheses can be tested.
    """
    claim: str
    domain: str
    measured_variables: list[str]
    attributed_cause: str
    excluded_candidate_causes: list[str] = field(default_factory=list)
    pinnacle_assumptions: list[str] = field(default_factory=list)
    references: list[str] = field(default_factory=list)


@dataclass
class FrameworkAudit:
    """Result of auditing a FrameworkClaim.

    The audit doesn't say the claim is wrong. It says: 'this claim
    has alternative hypotheses that the framework excluded by
    construction. Test against those before publishing as fact.'
    """
    original_claim: FrameworkClaim
    suggested_excluded_causes: list[str] = field(default_factory=list)
    detected_pinnacle_assumptions: list[str] = field(default_factory=list)
    missing_variables: list[str] = field(default_factory=list)
    reframed_claim: str = ""
    test_proposals: list[str] = field(default_factory=list)


# =============================================================================
# DOMAIN-SPECIFIC PATTERNS
# =============================================================================
# These dictionaries encode the structural-bias patterns observed in
# institutional Earth-systems literature.

EXCLUDED_CAUSE_PATTERNS = {
    "flood": {
        "common_attribution": ["climate", "precipitation increase", "extreme weather"],
        "typically_excluded": [
            "wetland_loss",
            "impervious_surface_increase",
            "channel_modification",
            "floodplain_development",
            "riparian_buffer_removal",
            "stormwater_concentration_through_engineered_drainage",
            "loss_of_natural_meanders",
            "beaver_dam_removal",
        ],
        "missing_variables": [
            "watershed_impervious_fraction",
            "wetland_extent_loss_since_1850",
            "channel_modification_status",
            "floodplain_development_density",
            "upstream_dam_capacity",
        ],
    },
    "drought": {
        "common_attribution": ["climate", "warming", "precipitation deficit"],
        "typically_excluded": [
            "co2_stomatal_effect_on_evapotranspiration",
            "groundwater_extraction_for_agriculture",
            "land_use_change_increasing_runoff",
            "deforestation_reducing_local_precipitation_recycling",
            "indigenous_water_management_systems_removed",
        ],
        "missing_variables": [
            "co2_corrected_PDSI",
            "groundwater_extraction_rate",
            "vegetation_water_use_efficiency",
            "watershed_runoff_fraction_change",
        ],
    },
    "tornado": {
        "common_attribution": ["climate", "warming atmosphere", "shifting jet stream"],
        "typically_excluded": [
            "doppler_radar_detection_cliff_1991",
            "ef_scale_methodology_change_2007",
            "retroactive_rating_of_pre_1978_tornadoes",
            "population_density_increase_in_detection_zones",
            "storm_chaser_density_changing",
            "social_media_reporting_changes",
        ],
        "missing_variables": [
            "radar_coverage_at_event_location",
            "rating_methodology_at_event_year",
            "population_within_5km_of_track",
            "storm_chaser_present_yes_no",
        ],
    },
    "hurricane": {
        "common_attribution": ["climate", "warming oceans", "atlantic warming"],
        "typically_excluded": [
            "hurdat2_reanalysis_revisions_2000_present",
            "pre_satellite_open_ocean_undercount",
            "pre_aircraft_intensity_estimation_uncertainty",
            "amo_phase_oscillation",
            "saffir_simpson_retroactive_application",
        ],
        "missing_variables": [
            "hurdat2_version_at_analysis",
            "amo_phase_at_event",
            "satellite_coverage_at_genesis",
            "aircraft_recon_completeness",
        ],
    },
    "fire": {
        "common_attribution": ["climate", "drought", "warming"],
        "typically_excluded": [
            "fuel_load_buildup_from_century_of_suppression",
            "indigenous_fire_management_systems_removed",
            "wildland_urban_interface_expansion",
            "logging_history_changing_forest_structure",
            "invasive_species_changing_fuel_characteristics",
            "human_ignition_density_changing",
        ],
        "missing_variables": [
            "fuel_load_at_ignition",
            "decades_since_last_burn",
            "indigenous_burn_management_status_at_location",
            "wui_density_at_perimeter",
            "ignition_cause_human_or_natural",
        ],
    },
    "earthquake": {
        "common_attribution": ["natural variability", "tectonic stress release"],
        "typically_excluded": [
            "induced_seismicity_from_fluid_injection",
            "reservoir_loading_stress_changes",
            "groundwater_extraction_changing_crustal_loading",
            "ice_sheet_isostatic_rebound_acceleration",
            "ohc_coupling_to_mantle_convection",
            "permafrost_thaw_changing_isostatic_load",
        ],
        "missing_variables": [
            "fluid_injection_volume_within_50km",
            "reservoir_water_level_changes",
            "groundwater_table_change_within_basin",
            "ice_sheet_mass_change_anomaly",
        ],
    },
}

PINNACLE_ASSUMPTION_PATTERNS = [
    {
        "domain": "infrastructure",
        "pattern": "current technology = reference standard",
        "examples": [
            "Wood roads in wetlands judged primitive vs asphalt",
            "Permeable surfaces judged obsolete vs concrete",
            "Indigenous fire management judged primitive vs suppression",
            "Meandering streams judged inefficient vs straightened",
            "Wetlands judged wasted real estate vs drained land",
        ],
        "detection_signals": [
            "primitive", "obsolete", "inefficient", "underdeveloped",
            "regressive", "outdated", "wasteful",
        ],
    },
    {
        "domain": "data_methodology",
        "pattern": "current methodology = truth, prior methods = error",
        "examples": [
            "Pre-satellite estimates treated as approximations of satellite truth",
            "Pre-EF-scale ratings treated as inferior approximations",
            "Pre-instrumental records treated as guesses",
        ],
        "detection_signals": [
            "approximation", "estimate", "less accurate", "preliminary",
            "before precise measurement",
        ],
    },
    {
        "domain": "framework",
        "pattern": "existing framework = neutral, alternative frames = bias",
        "examples": [
            "Climate framing of flood treated as default",
            "Land-use framing treated as 'denialism'",
            "Methodology critique treated as anti-science",
        ],
        "detection_signals": [
            "scientific consensus", "settled science", "denialism",
            "fringe view", "alternative framing",
        ],
    },
]


# =============================================================================
# AUDIT FUNCTIONS
# =============================================================================

def audit_claim(claim: FrameworkClaim) -> FrameworkAudit:
    """Run framework-level audit on a claim.

    Returns suggestions for excluded causes, pinnacle assumptions
    detected, and missing variables that would test alternatives.
    """
    audit = FrameworkAudit(original_claim=claim)

    # Check domain-specific patterns
    if claim.domain in EXCLUDED_CAUSE_PATTERNS:
        patterns = EXCLUDED_CAUSE_PATTERNS[claim.domain]

        # Check if attribution matches "common attribution" patterns
        attribution_lower = claim.attributed_cause.lower()
        for common in patterns["common_attribution"]:
            if common.lower() in attribution_lower:
                # This is a high-risk attribution -- typical excluded causes apply
                audit.suggested_excluded_causes.extend(
                    patterns["typically_excluded"]
                )
                audit.missing_variables.extend(
                    patterns["missing_variables"]
                )
                break

    # Check for pinnacle assumption signals
    full_text = (claim.claim + " " + claim.attributed_cause).lower()
    for pattern in PINNACLE_ASSUMPTION_PATTERNS:
        for signal in pattern["detection_signals"]:
            if signal in full_text:
                audit.detected_pinnacle_assumptions.append(
                    f"{pattern['pattern']}: signal '{signal}' detected"
                )
                break

    # Build reframed claim
    if audit.suggested_excluded_causes:
        excluded_str = ", ".join(audit.suggested_excluded_causes[:3])
        audit.reframed_claim = (
            f"ORIGINAL: {claim.claim}\n"
            f"ATTRIBUTED TO: {claim.attributed_cause}\n"
            f"REFRAMED: The observed phenomenon is consistent with "
            f"the attributed cause AND with alternative causes including "
            f"{excluded_str}. The current framework cannot distinguish "
            f"between these because the relevant variables "
            f"({', '.join(audit.missing_variables[:3])}) are not in "
            f"the dataset. Attribution requires expanding the variable "
            f"set or explicitly stating that the current framework "
            f"cannot test these alternatives."
        )
    else:
        audit.reframed_claim = (
            f"No domain-specific excluded-cause patterns detected. "
            f"This does not mean the claim is bias-free -- it means "
            f"this tool's pattern library has no entry for this domain."
        )

    # Generate test proposals
    for excluded in audit.suggested_excluded_causes[:5]:
        audit.test_proposals.append(
            f"Test: Add variable for {excluded}; rerun attribution "
            f"analysis with this candidate cause included."
        )

    return audit


def format_audit_output(audit: FrameworkAudit) -> str:
    """Format audit results for display."""
    out = []
    out.append("=" * 78)
    out.append(f"FRAMEWORK AUDIT -- {audit.original_claim.domain.upper()}")
    out.append("=" * 78)
    out.append(f"\nORIGINAL CLAIM:\n  {audit.original_claim.claim}")
    out.append(f"\nATTRIBUTED CAUSE:\n  {audit.original_claim.attributed_cause}")
    out.append("\nMEASURED VARIABLES:")
    for v in audit.original_claim.measured_variables:
        out.append(f"  - {v}")

    if audit.suggested_excluded_causes:
        out.append("\nSUGGESTED EXCLUDED CAUSES (alternative hypotheses):")
        for c in audit.suggested_excluded_causes:
            out.append(f"  - {c}")

    if audit.detected_pinnacle_assumptions:
        out.append("\nDETECTED PINNACLE ASSUMPTIONS:")
        for p in audit.detected_pinnacle_assumptions:
            out.append(f"  - {p}")

    if audit.missing_variables:
        out.append("\nMISSING VARIABLES (needed to test alternatives):")
        for v in audit.missing_variables:
            out.append(f"  - {v}")

    out.append("\nREFRAMED CLAIM:")
    for line in audit.reframed_claim.split("\n"):
        out.append(f"  {line}")

    if audit.test_proposals:
        out.append("\nTEST PROPOSALS:")
        for t in audit.test_proposals:
            out.append(f"  * {t}")

    out.append("\n" + "=" * 78)
    return "\n".join(out)


# =============================================================================
# DEMONSTRATION -- audit the flood claim
# =============================================================================

if __name__ == "__main__":
    # Example 1: standard institutional flood claim
    flood_claim = FrameworkClaim(
        claim="100-year floods are now occurring as 10-year events in many US watersheds.",
        domain="flood",
        measured_variables=[
            "peak_streamflow_m3s",
            "precipitation_mm",
            "FEMA_disaster_declarations",
            "annual_recurrence_interval",
        ],
        attributed_cause="climate change increasing extreme precipitation intensity",
        references=["IPCC AR6 WG1 Chapter 11", "USGCRP NCA5"],
    )

    audit_result = audit_claim(flood_claim)
    print(format_audit_output(audit_result))

    # Example 2: drought claim
    drought_claim = FrameworkClaim(
        claim="Western US is experiencing the worst drought in 1,200 years.",
        domain="drought",
        measured_variables=[
            "PDSI_thornthwaite",
            "tree_ring_reconstructed_PDSI",
            "annual_precipitation",
            "summer_temperature",
        ],
        attributed_cause="anthropogenic climate change",
        references=["Williams et al. 2022 Nature Climate Change"],
    )

    audit_result = audit_claim(drought_claim)
    print(format_audit_output(audit_result))

    # Example 3: tornado claim
    tornado_claim = FrameworkClaim(
        claim="Tornado activity in the United States has increased since 1950.",
        domain="tornado",
        measured_variables=[
            "annual_tornado_count",
            "F_or_EF_rating",
            "deaths",
        ],
        attributed_cause="climate change shifting tornado alley",
        references=["NOAA SPC tornado climatology"],
    )

    audit_result = audit_claim(tornado_claim)
    print(format_audit_output(audit_result))

    # Example 4: pinnacle assumption signal
    infrastructure_claim = FrameworkClaim(
        claim="Modern asphalt road systems represent significant improvement over primitive log-road construction in northern climates.",
        domain="flood",
        measured_variables=["road_durability", "vehicle_speed", "maintenance_cost_year_1"],
        attributed_cause="superior engineering of modern materials",
    )

    audit_result = audit_claim(infrastructure_claim)
    print(format_audit_output(audit_result))

    print("\n" + "=" * 78)
    print("FRAMEWORK AUDITOR -- INSTRUCTIONS FOR USE")
    print("=" * 78)
    print("""
1. For any institutional climate/Earth-systems claim, build a
   FrameworkClaim object with:
     - the verbatim claim
     - what was actually measured
     - what cause was attributed
     - the source reference

2. Run audit_claim() to identify excluded alternative hypotheses
   and pinnacle assumptions baked into the framework.

3. The output is a REFRAMED CLAIM that states the original
   finding alongside the alternatives the framework excluded.

4. The TEST PROPOSALS section gives you specific variables to
   add to enable testing the excluded hypotheses.

THE PHILOSOPHICAL POINT:

  This tool does not say claims are wrong. It says: institutional
  claims usually rest on frameworks that exclude alternative
  causes by construction. Honest scientific practice requires
  stating the framework limitation explicitly, not pretending
  the data settles a question the framework couldn't ask.

EXTENDING THIS TOOL:

  The EXCLUDED_CAUSE_PATTERNS dictionary is incomplete. Each
  domain you audit should add its own entry documenting:
    - Common institutional attributions
    - Typically-excluded alternative causes
    - Variables missing from standard datasets

  As the patterns library grows, the tool catches more
  framework-level corruption automatically.
""")
    print("=" * 78)
