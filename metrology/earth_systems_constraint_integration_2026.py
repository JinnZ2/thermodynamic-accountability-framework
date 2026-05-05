"""
EARTH_SYSTEMS_CONSTRAINT_INTEGRATION_2026

Constraint layer module for earth-systems-physics coupled differential equations.

Integrates three observational findings invalidating prior model assumptions:

  1. Glacier mass loss acceleration (Birmingham 2025/2026, NASA GRACE 2002-2025)
  2. Ecosystem collapse timescale compression (Nature Sustainability)
  3. West Antarctic iron-fertilization carbon-sink invalidation (Sherrell et al, 2026)

Function: provides validity checks, fallback flags, and cascade-trigger
thresholds for use as constraint inputs to coupled solvers.

CC0 Public Domain. Standard library only.
"""

# =============================================================================
# LAYER 1: GLACIER AND ICE SHEET DYNAMICS
# Source: Univ. Birmingham 2026 (Nature Reviews), NASA GRACE/GRACE-FO,
#         NOAA Arctic Report Card 2025, WGMS, ICIMOD
# =============================================================================

GLACIER_LOSS_2025_GT = 408                  # gigatons; excludes Greenland/Antarctica
GLACIER_LOSS_2025_UNCERTAINTY_GT = 132      # +/- 132 Gt
GLACIER_LOSS_RANK_HALF_CENTURY = 2          # 2nd highest annual loss on record

GREENLAND_LOSS_2002_2025_AVG_GT_YR = 264    # NASA GRACE long-term mean
GREENLAND_LOSS_2025_GT = 129                # NOAA single-year value
GREENLAND_LOSS_2003_2024_AVG_GT_YR = 219    # NOAA historical average
GREENLAND_LOSS_2024_2025_HYDRO_YR_GT = 139  # +/- 79 Gt (hydrological year)

ANTARCTICA_LOSS_2002_2025_AVG_GT_YR = 135   # NASA GRACE long-term mean

CUMULATIVE_GLACIER_LOSS_SINCE_1975_GT = 9000  # WGMS, non-ice-sheet

SLR_FROM_GLACIER_2025_MM = 1.1              # 2025 hydro year contribution
SLR_PROJECTION_2100_M_HIGH_EMISSION = 2.2   # high-emission scenario
SLR_PROJECTION_2150_M_HIGH_EMISSION = 3.9

# Rotational coupling: polar mass loss alters moment of inertia
NORTH_POLE_DRIFT_BY_2100_FT = 90            # latitude shift estimate


# =============================================================================
# LAYER 2: ECOSYSTEM COLLAPSE TIMESCALE COMPRESSION
# Source: Willcock et al., Nature Sustainability,
#         "Earlier collapse of Anthropocene ecosystems driven by
#          multiple faster and noisier drivers"
# Models tested: Chilika lagoon fishery, Easter Island community,
#                forest dieback, lake water quality
# =============================================================================

# Single primary stressor: collapse occurs at baseline projected timeline.
# Add additional stresses and/or noise: collapse compresses 38-81% closer
# to present day.

COLLAPSE_COMPRESSION_MIN_PCT = 38
COLLAPSE_COMPRESSION_MAX_PCT = 81

# Implication: linear single-stressor projections systematically underestimate
# collapse proximity. Compound stressors are the rule, not the exception.

# Stockholm Resilience / Global Tipping Points Report 2025:
# Coral reef tipping point CROSSED -- mass bleaching outpacing recovery.
CORAL_TIPPING_POINT_CROSSED_2025 = True
PLANETARY_BOUNDARIES_BREACHED_OF_9 = 7      # incl. ocean acidification (new 2025)

# Cascade thresholds (RCP 8.5 high-emissions trajectory):
DISRUPTION_TROPICAL_OCEAN_BY_YEAR = 2030
DISRUPTION_TROPICAL_FOREST_BY_YEAR = 2050
DISRUPTION_POLAR_ENV_BY_YEAR = 2050

# Species-loss probability at warming thresholds:
PCT_ASSEMBLAGES_LOSING_20PCT_SPECIES_AT_4C = 15
PCT_ASSEMBLAGES_LOSING_20PCT_SPECIES_AT_2C = 2

# Domino-coupled tipping elements (Stockholm Resilience):
COUPLED_TIPPING_ELEMENTS = [
    "Greenland_Ice_Sheet",
    "West_Antarctic_Ice_Sheet",
    "AMOC",                 # Atlantic Meridional Overturning Circulation
    "Amazon_Rainforest",
    "Boreal_Permafrost",
    "Coral_Reefs_Warm_Water",
]

# Negative feedback loop (Greenland Ice Sheet -> AMOC) NO LONGER
# considered sufficient to stabilize the system.
GREENLAND_AMOC_NEGATIVE_FEEDBACK_RELIABLE = False


# =============================================================================
# LAYER 3: WEST ANTARCTIC IRON-FERTILIZATION INVALIDATION
# Source: Sherrell et al, Rutgers / Dotson Ice Shelf 2022 expedition,
#         published 2026; corroborated by Struve (Oldenburg) sediment-core work.
# =============================================================================

IRON_FERTILIZATION_HYPOTHESIS_STATUS = "INVALIDATED"

# Old assumption: meltwater discharge supplies primary iron to Southern Ocean,
# triggering algae blooms and CO2 drawdown -> negative (cooling) feedback.
# Field reality: meltwater iron contribution minimal; iron sourced from
# deep ocean water and resuspended sediments.

IRON_PRIMARY_SOURCE_OLD = "ice_meltwater_discharge"
IRON_PRIMARY_SOURCE_OBSERVED = "deep_ocean_water_and_sediments"

# Sediment core evidence (south of Antarctic Polar Front):
# iron supply HIGHEST during warm intervals -- delivered by calving icebergs,
# not meltwater -- and HIGH iron did NOT accelerate algae growth as expected.

IRON_FROM_DUST_DOMINANT_NORTH_OF_POLAR_FRONT = True
IRON_FROM_ICEBERGS_DOMINANT_SOUTH_OF_POLAR_FRONT = True
HIGH_IRON_TRIGGERED_BLOOM_AS_PREDICTED = False

# Net consequence: prior coupled-model assumption of glacier-melt
# negative carbon feedback is removed. System loses an assumed
# self-stabilizing mechanism.

ASSUMED_FEEDBACK_SIGN = "negative_cooling"
OBSERVED_FEEDBACK_SIGN = "neutral_to_positive_warming"


# =============================================================================
# CONSTRAINT VALIDATION FUNCTIONS
# =============================================================================

INVALIDATED_ASSUMPTIONS = {
    "iron_fertilization_carbon_sink":
        "INVALIDATED 2026: West Antarctic field data; meltwater iron minimal",
    "linear_single_stressor_collapse_timeline":
        "INVALIDATED: compound stressors compress timeline 38-81% (Willcock et al)",
    "greenland_amoc_negative_feedback_stabilizes_system":
        "INVALIDATED: domino coupling overrides single-loop stabilization",
    "coral_reefs_resilient":
        "INVALIDATED 2025: tipping point crossed; mass bleaching > recovery",
    "linear_extrapolation_of_glacier_loss":
        "INVALIDATED: 2025 = 2nd highest annual loss in 50 years; nonlinear",
}


def constraint_validity_check(model_assumption_key):
    """
    Returns (is_valid, status_message) for a named model assumption.
    Use to flag stale assumptions in coupled solver before propagating state.
    """
    key = model_assumption_key.lower().strip()
    if key in INVALIDATED_ASSUMPTIONS:
        return False, INVALIDATED_ASSUMPTIONS[key]
    return True, "CONDITIONAL: no recorded invalidation; verify against latest observation"


def cascade_trigger_check(system_label, year):
    """
    Returns (is_triggered, status) for cascade thresholds under
    high-emissions trajectory. Use as early-warning gate in solver.
    """
    s = system_label.lower()
    if "tropical_ocean" in s and year >= DISRUPTION_TROPICAL_OCEAN_BY_YEAR - 4:
        return True, "ABRUPT_DISRUPTION_WINDOW_OPEN"
    if "tropical_forest" in s and year >= DISRUPTION_TROPICAL_FOREST_BY_YEAR - 5:
        return True, "ABRUPT_DISRUPTION_WINDOW_APPROACHING"
    if "polar" in s and year >= DISRUPTION_POLAR_ENV_BY_YEAR - 5:
        return True, "ABRUPT_DISRUPTION_WINDOW_APPROACHING"
    if "coral" in s:
        return True, "TIPPING_POINT_ALREADY_CROSSED_2025"
    return False, "WITHIN_PROJECTED_STABLE_RANGE"


def apply_collapse_compression(baseline_years_to_collapse, n_active_stressors):
    """
    Adjusts a baseline single-stressor collapse timeline to account for
    compound-stressor compression observed in Willcock et al.
    n_active_stressors >= 2 triggers compression range 38-81%.
    Returns (min_years, max_years) compressed timeline.
    """
    if n_active_stressors < 2:
        return baseline_years_to_collapse, baseline_years_to_collapse
    min_factor = 1.0 - (COLLAPSE_COMPRESSION_MAX_PCT / 100.0)  # 0.19
    max_factor = 1.0 - (COLLAPSE_COMPRESSION_MIN_PCT / 100.0)  # 0.62
    return (
        baseline_years_to_collapse * min_factor,
        baseline_years_to_collapse * max_factor,
    )


def remove_iron_fertilization_carbon_sink(carbon_budget_dict):
    """
    Strips the assumed glacial-melt iron -> algae bloom -> CO2 drawdown
    flux from a carbon budget dict. Sets that pathway to zero.
    Caller must re-balance their budget after.
    """
    out = dict(carbon_budget_dict)
    keys_to_zero = [
        k for k in out
        if "iron_fertilization" in k.lower()
        or "meltwater_iron_drawdown" in k.lower()
        or "glacial_iron_co2_sink" in k.lower()
    ]
    for k in keys_to_zero:
        out[k] = 0.0
    return out, keys_to_zero


# =============================================================================
# OBSERVATIONAL PRECEDENCE FLAGS
# Empirical field signals (insect biomass crash, monarch migration
# absence, salamander pond collapse, predator-prey phase shifts,
# bird migration timing drift) lead linear-model predictions.
# Set these flags when integrating into coupled-equation solvers.
# =============================================================================

OBSERVATION_PRECEDES_LINEAR_MODEL = True
LINEAR_MODEL_DEPRECATED_FOR_COUPLED_SYSTEMS = True
NONLINEAR_COUPLING_REQUIRED = True
COMPOUND_STRESSOR_DEFAULT = True   # treat as default, not exception


# =============================================================================
# SMOKE TEST
# =============================================================================

if __name__ == "__main__":
    print("EARTH SYSTEMS CONSTRAINT INTEGRATION (2026 vintage)")
    print("=" * 60)

    print("\n-- Glacier dynamics --")
    print(f"  2025 non-ice-sheet glacier loss: "
          f"{GLACIER_LOSS_2025_GT} +/- {GLACIER_LOSS_2025_UNCERTAINTY_GT} GT "
          f"(rank #{GLACIER_LOSS_RANK_HALF_CENTURY} in last 50y)")
    print(f"  Greenland avg loss rate (2002-2025): "
          f"{GREENLAND_LOSS_2002_2025_AVG_GT_YR} GT/yr")
    print(f"  Antarctica avg loss rate (2002-2025): "
          f"{ANTARCTICA_LOSS_2002_2025_AVG_GT_YR} GT/yr")
    print(f"  Cumulative glacier loss since 1975: "
          f"{CUMULATIVE_GLACIER_LOSS_SINCE_1975_GT} GT")

    print("\n-- Ecosystem collapse compression --")
    print(f"  Compound stressors compress timeline by "
          f"{COLLAPSE_COMPRESSION_MIN_PCT}-{COLLAPSE_COMPRESSION_MAX_PCT}%")
    print(f"  Coral tipping point crossed (2025): "
          f"{CORAL_TIPPING_POINT_CROSSED_2025}")
    print(f"  Planetary boundaries breached: "
          f"{PLANETARY_BOUNDARIES_BREACHED_OF_9}/9")
    print(f"  Coupled tipping elements: {len(COUPLED_TIPPING_ELEMENTS)}")

    print("\n-- Iron-fertilization feedback --")
    print(f"  Status: {IRON_FERTILIZATION_HYPOTHESIS_STATUS}")
    print(f"  Old source: {IRON_PRIMARY_SOURCE_OLD}")
    print(f"  Observed:   {IRON_PRIMARY_SOURCE_OBSERVED}")
    print(f"  Sign flip:  {ASSUMED_FEEDBACK_SIGN} -> {OBSERVED_FEEDBACK_SIGN}")

    print("\n-- constraint_validity_check() --")
    for assumption in [
        "iron_fertilization_carbon_sink",
        "linear_single_stressor_collapse_timeline",
        "coral_reefs_resilient",
        "stationarity_2030",  # not in INVALIDATED dict
    ]:
        ok, note = constraint_validity_check(assumption)
        print(f"  {assumption}: valid={ok}\n    -> {note}")

    print("\n-- cascade_trigger_check() --")
    for system, year in [
        ("tropical_ocean_coral_reef", 2028),
        ("tropical_forest_amazon", 2046),
        ("polar_arctic_sea_ice", 2046),
        ("temperate_forest", 2049),
        ("coral_reef_great_barrier", 2025),
    ]:
        triggered, label = cascade_trigger_check(system, year)
        print(f"  {system} @ {year}: triggered={triggered} ({label})")

    print("\n-- apply_collapse_compression() --")
    for stressors in [1, 2, 4]:
        lo, hi = apply_collapse_compression(50, stressors)
        print(f"  baseline=50y, n_stressors={stressors}: "
              f"compressed -> {lo:.1f}y to {hi:.1f}y")

    print("\n-- remove_iron_fertilization_carbon_sink() --")
    sample_budget = {
        "fossil_emissions_GtC_yr": 9.5,
        "land_sink_GtC_yr": -3.2,
        "ocean_sink_GtC_yr": -2.8,
        "iron_fertilization_carbon_sink_GtC_yr": -0.15,
        "meltwater_iron_drawdown_GtC_yr": -0.05,
    }
    rebalanced, zeroed = remove_iron_fertilization_carbon_sink(sample_budget)
    print(f"  Zeroed pathways: {zeroed}")
    print(f"  Rebalanced budget: {rebalanced}")
