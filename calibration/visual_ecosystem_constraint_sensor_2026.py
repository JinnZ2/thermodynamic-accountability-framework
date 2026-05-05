"""
VISUAL_ECOSYSTEM_CONSTRAINT_SENSOR_2026

Encodes direct visual ecosystem observations into constraint specifications
without narrative translation.

Operator passes terse structured observations:
  - color palette (health signature)
  - growth pattern and stage (phenological state)
  - fragility (herbivory load indicator)
  - spatial distribution (disturbance topology)
  - novel structures (recent disturbance markers)
  - topographic / hydrological context (rules out gradient-driven causes)

System matches against constraint signatures and returns:
  - candidate constraint violations
  - cascade risk classification (transient_lag vs degradation vs collapse)
  - estimated recalibration window
  - missing ecological functions

Domain-specific application of:
  - calibration/constraint_sensor_framework_2026.py
      (general substrate-primary input layer)

Sister to:
  - calibration/vibration_constraint_sensor_2026.py
      (mechanical-domain instance)

Standard library only. CC0 Public Domain.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict


# =============================================================================
# CONTROLLED VOCABULARY
# =============================================================================

COLOR_SIGNATURES = [
    "green_full_saturation",         # healthy mid-season
    "green_pale",                    # nutrient or water stress
    "gray_dominant",                 # winter dormancy or chronic stress
    "gray_with_green_tips",          # delayed budding
    "yellow_chlorotic",              # nutrient deficiency or root damage
    "brown_dieback",                 # mortality signature
    "red_purple_anthocyanin",        # cold, drought, or pathogen stress
    "mottled_uneven",                # patchy disease or herbivore load
]

GROWTH_STAGES = [
    "dormant",
    "bud_starting",
    "bud_swollen",
    "leaf_emerging",
    "leaf_full",
    "flowering",
    "fruiting",
    "senescing",
    "no_growth_expected_for_season",
]

FRAGILITY_CLASSES = [
    "robust",                        # turgid, intact, no breakage
    "moderate_robust",
    "fragile_visible_breakage",      # snapping, broken stems visible
    "wilting_no_breakage",
    "wilting_with_breakage",
    "partially_consumed",            # active herbivory signature
    "skeletal_remains",              # post-collapse
]

SPATIAL_PATTERNS = [
    "uniform",                              # consistent across area
    "gradient_topographic",                 # follows elevation/slope
    "gradient_road_proximity",              # decays with distance from road
    "gradient_water_proximity",             # follows hydrological feature
    "patchy_random",                        # no clear spatial logic
    "patchy_correlated_with_disturbance",   # tied to specific feature
    "edge_effect_only",                     # boundaries differ from interior
    "trail_aligned",                        # follows path of regular use
]

DISTURBANCE_MARKERS = [
    "none_observed",
    "vehicle_tracks_recent",
    "vehicle_tracks_old",
    "structure_new_unoccupied",   # like RV placed but not used
    "structure_new_active",
    "structure_old_established",
    "construction_active",
    "logging_recent",
    "fire_recent",
    "fire_old",
    "flooding_recent",
    "chemical_spill_signature",
    "compaction_visible",
]

PREDATOR_PRESENCE = [
    "active_birds_visible",
    "raptor_perches_used",
    "scat_or_tracks_present",
    "calls_audible",
    "no_visible_activity",
    "absent_should_be_present",
    "unknown_not_assessed",
]

CASCADE_CLASSIFICATIONS = [
    "stable_no_cascade",
    "transient_lag_recalibration_expected",
    "moderate_disruption_recovery_likely",
    "degradation_partial_permanent",
    "collapse_threshold_approached",
    "collapse_in_progress",
]


# =============================================================================
# OBSERVATION RECORD
# =============================================================================

@dataclass
class VisualEcosystemObservation:
    color_signature: str
    growth_stage: str
    fragility: str
    spatial_pattern: str
    disturbance_marker: str
    predator_presence: str
    location_label: str
    topographic_position: Optional[str] = None     # "upslope", "valley", "flat"
    elevated_above_road_runoff: Optional[bool] = None
    novel_structure_recent: Optional[bool] = None
    novel_structure_distance_m: Optional[float] = None
    season: Optional[str] = None                   # "early_spring", "summer"
    operator_confidence: float = 1.0
    notes: Optional[str] = None

    def validate(self):
        if self.color_signature not in COLOR_SIGNATURES:
            raise ValueError(
                f"color_signature must be in {COLOR_SIGNATURES}"
            )
        if self.growth_stage not in GROWTH_STAGES:
            raise ValueError(f"growth_stage must be in {GROWTH_STAGES}")
        if self.fragility not in FRAGILITY_CLASSES:
            raise ValueError(f"fragility must be in {FRAGILITY_CLASSES}")
        if self.spatial_pattern not in SPATIAL_PATTERNS:
            raise ValueError(
                f"spatial_pattern must be in {SPATIAL_PATTERNS}"
            )
        if self.disturbance_marker not in DISTURBANCE_MARKERS:
            raise ValueError(
                f"disturbance_marker must be in {DISTURBANCE_MARKERS}"
            )
        if self.predator_presence not in PREDATOR_PRESENCE:
            raise ValueError(
                f"predator_presence must be in {PREDATOR_PRESENCE}"
            )


# =============================================================================
# CONSTRAINT SIGNATURE LIBRARY
# =============================================================================

CONSTRAINT_SIGNATURES = [
    {
        "signature": {
            "color_signature": "gray_with_green_tips",
            "growth_stage": "bud_starting",
            "fragility": "fragile_visible_breakage",
            "predator_presence": "absent_should_be_present",
            "disturbance_marker": "structure_new_unoccupied",
        },
        "constraint_violation":
            "predator_corridor_disrupted_by_novel_structure",
        "cascade_class": "transient_lag_recalibration_expected",
        "recalibration_window": "weeks_to_months",
        "missing_function":
            "predator_suppression_of_emerging_herbivores",
        "permanent_damage_risk":
            "low_unless_phenological_window_missed",
    },
    {
        "signature": {
            "color_signature": "gray_dominant",
            "growth_stage": "no_growth_expected_for_season",
            "fragility": "skeletal_remains",
            "spatial_pattern": "uniform",
        },
        "constraint_violation": "winter_dormancy_or_chronic_collapse",
        "cascade_class": "unknown_requires_seasonal_context",
        "recalibration_window": "n/a",
        "missing_function": "to_be_determined",
        "permanent_damage_risk": "unknown",
    },
    {
        "signature": {
            "color_signature": "yellow_chlorotic",
            "fragility": "wilting_no_breakage",
            "spatial_pattern": "gradient_road_proximity",
        },
        "constraint_violation": "road_runoff_chemical_or_salt_stress",
        "cascade_class": "degradation_partial_permanent",
        "recalibration_window": "growing_seasons",
        "missing_function": "soil_chemistry_buffering",
        "permanent_damage_risk": "moderate_to_high",
    },
    {
        "signature": {
            "color_signature": "brown_dieback",
            "fragility": "skeletal_remains",
            "spatial_pattern": "patchy_correlated_with_disturbance",
            "disturbance_marker": "fire_recent",
        },
        "constraint_violation": "fire_damage_recovery_phase",
        "cascade_class": "moderate_disruption_recovery_likely",
        "recalibration_window": "1_to_5_years",
        "missing_function": "soil_seed_bank_germination",
        "permanent_damage_risk": "moderate",
    },
    {
        "signature": {
            "color_signature": "mottled_uneven",
            "fragility": "partially_consumed",
            "predator_presence": "no_visible_activity",
        },
        "constraint_violation": "herbivore_overload_predator_absent",
        "cascade_class": "moderate_disruption_recovery_likely",
        "recalibration_window": "growing_seasons",
        "missing_function": "predator_population_regulating_herbivores",
        "permanent_damage_risk": "moderate",
    },
    {
        "signature": {
            "color_signature": "green_pale",
            "fragility": "wilting_no_breakage",
            "spatial_pattern": "gradient_water_proximity",
        },
        "constraint_violation": "hydrological_stress",
        "cascade_class": "transient_lag_recalibration_expected",
        "recalibration_window": "season_dependent_on_precipitation",
        "missing_function": "water_availability",
        "permanent_damage_risk": "low_to_moderate",
    },
    {
        "signature": {
            "color_signature": "gray_with_green_tips",
            "growth_stage": "bud_starting",
            "spatial_pattern": "trail_aligned",
        },
        "constraint_violation":
            "predator_or_pollinator_corridor_concentrated_to_trail_only",
        "cascade_class": "transient_lag_recalibration_expected",
        "recalibration_window": "weeks_to_months",
        "missing_function": "off_trail_predator_or_pollinator_access",
        "permanent_damage_risk": "low",
    },
]


def match_constraint(obs: VisualEcosystemObservation) -> List[Dict]:
    """
    Compare observation against constraint signature library.
    Returns ranked candidates with match scores.
    """
    obs_dict = asdict(obs)
    matches = []
    for entry in CONSTRAINT_SIGNATURES:
        sig = entry["signature"]
        n_fields = len(sig)
        n_match = sum(1 for k, v in sig.items() if obs_dict.get(k) == v)
        if n_match == 0:
            continue
        score = n_match / n_fields
        matches.append({
            "constraint_violation": entry["constraint_violation"],
            "cascade_class": entry["cascade_class"],
            "recalibration_window": entry["recalibration_window"],
            "missing_function": entry["missing_function"],
            "permanent_damage_risk": entry["permanent_damage_risk"],
            "match_score": round(score, 2),
            "matched_fields": n_match,
            "total_signature_fields": n_fields,
        })
    matches.sort(key=lambda x: -x["match_score"])
    return matches


# =============================================================================
# RULE-OUT CHECKS (eliminate gradient-driven causes)
# =============================================================================

def rule_out_salt_runoff(obs: VisualEcosystemObservation) -> Tuple[bool, str]:
    """
    Check if salt runoff is plausible given topography.
    Returns (ruled_out, reason).
    """
    if obs.elevated_above_road_runoff is True:
        return True, "elevated_above_road_runoff_excludes_salt_path"
    if obs.spatial_pattern == "gradient_road_proximity":
        return False, "spatial_pattern_consistent_with_road_chemistry"
    return False, "insufficient_information"


def rule_out_hydrology(obs: VisualEcosystemObservation) -> Tuple[bool, str]:
    """
    Check if hydrological gradient explains pattern.
    Returns (ruled_out, reason).
    """
    if obs.spatial_pattern == "gradient_water_proximity":
        return False, "spatial_pattern_consistent_with_hydrological_cause"
    if obs.spatial_pattern in (
        "patchy_correlated_with_disturbance",
        "trail_aligned",
    ):
        return True, "spatial_pattern_inconsistent_with_uniform_hydrology"
    return False, "insufficient_information"


# =============================================================================
# DEMO
# =============================================================================

if __name__ == "__main__":
    print("VISUAL ECOSYSTEM CONSTRAINT SENSOR -- Demo")
    print("=" * 60)

    # Operator observation: gray shrubs with green tips, just budding,
    # fragile breakage visible, predators absent, recent unoccupied RV
    # nearby, elevated above road runoff, trail-aligned growth pattern.
    obs = VisualEcosystemObservation(
        color_signature="gray_with_green_tips",
        growth_stage="bud_starting",
        fragility="fragile_visible_breakage",
        spatial_pattern="trail_aligned",
        disturbance_marker="structure_new_unoccupied",
        predator_presence="absent_should_be_present",
        location_label="ditch_alongside_two_lane_road_mile_marker_unknown",
        topographic_position="elevated_above_ditch",
        elevated_above_road_runoff=True,
        novel_structure_recent=True,
        novel_structure_distance_m=15.0,
        season="early_spring",
        operator_confidence=0.9,
    )
    obs.validate()

    print("\nObservation:")
    for k, v in asdict(obs).items():
        print(f"  {k}: {v}")

    print("\nRule-out checks:")
    salt_out, salt_reason = rule_out_salt_runoff(obs)
    hydro_out, hydro_reason = rule_out_hydrology(obs)
    print(f"  salt_ruled_out:  {salt_out} ({salt_reason})")
    print(f"  hydro_ruled_out: {hydro_out} ({hydro_reason})")

    print("\nCandidate constraint violations:")
    candidates = match_constraint(obs)
    for c in candidates:
        print(f"  [{c['match_score']*100:.0f}% match] "
              f"{c['constraint_violation']}")
        print(f"     cascade_class:         {c['cascade_class']}")
        print(f"     recalibration_window:  {c['recalibration_window']}")
        print(f"     missing_function:      {c['missing_function']}")
        print(f"     permanent_damage_risk: {c['permanent_damage_risk']}")
        print()

    if not candidates:
        print("  no signature match; observation logged for catalog extension")
