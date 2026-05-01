"""
environment_expression_surface

CC0 / public domain. JinnZ2.

Add-on module for trait_waveform_validator.

## Purpose

Most published "trait differences" between groups (gender, age,
ethnicity) are confounded by environment, because gene EXPRESSION
is environment-modulated. The same genome produces measurably
different phenotypes under different developmental loading regimes.

This module adds environment-history as a required axis class.
A claim about "women's strength" or "men's emotionality" or
"older people's cognition" becomes structurally incomplete without
specifying:

    - physical loading history
    - nutritional substrate
    - cold/heat exposure regime
    - real-consequence density
    - chronic stress type
    - developmental diet
    - light regime

The same anti-bias property as the base module:
    scalar claim                  -> REJECTED at type layer
    fully specified narrow claim  -> evaluable, but bounded

This makes "the way women are" a malformed query unless the
environment coordinates are pinned. Which they almost never are
in published literature.

## Reference for the concept

Gene expression is regulated by:

    - chronic glucocorticoid load (HPA axis methylation)
    - mechanical loading (Wnt/β-catenin, IGF-1 cascades)
    - nutritional cofactors (methylation, mitochondrial assembly)
    - circadian regularity (CLOCK gene expression)
    - microbiome composition (immune set-point, neurotransmitter
      precursor availability)
    - thermoregulatory demand (mitochondrial uncoupling, brown
      adipose recruitment)
    - cognitive load type (consequence-coupled vs status-coupled)

These shape the SUBSTRATE on which the base trait waveforms
operate. A trait waveform without environment-history is sampling
one slice of a much larger surface and treating it as the surface.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Callable, Optional
from trait_waveform_validator import (
    Axis,
    AxisKind,
    TraitWaveform,
    TraitSurface,
    ClaimValidator,
    GroupComparisonClaim,
    PhysicsGuardAdapter,
    UnderspecifiedComparisonError,
    WaveformError,
)


# ─────────────────────────────────────────────────────────────────────
# ENVIRONMENT AXES
# ─────────────────────────────────────────────────────────────────────
#
# Each axis represents an aspect of accumulated developmental loading
# that modulates gene expression independent of the genome itself.
# All axes are required for honest cross-environment comparison.
# ─────────────────────────────────────────────────────────────────────

ENVIRONMENT_AXES = (
    Axis(
        name="physical_load_years",
        kind=AxisKind.SUBSTRATE,
        unit="years_at_load",
        domain=(0.0, 80.0),
        notes=(
            "cumulative years of regular physical loading from childhood. "
            "modulates muscle fiber distribution, ligament density, "
            "bone mineralization, mitochondrial capacity, "
            "androgen receptor density."
        ),
    ),
    Axis(
        name="real_consequence_density",
        kind=AxisKind.LOAD,
        unit="events_per_year",
        domain=(0.0, 500.0),
        notes=(
            "events/year requiring competent action with material "
            "consequence (not status performance). modulates HPA "
            "axis tuning, vagal tone, decision-pattern formation, "
            "calibration to outcome rather than narrative."
        ),
    ),
    Axis(
        name="nutritional_density",
        kind=AxisKind.SUBSTRATE,
        unit="normalized",
        domain=(0.0, 1.0),
        notes=(
            "0=processed/refined diet history, 1=whole food / "
            "ancestral / nutrient-dense diet history. modulates "
            "methylation cofactor availability, hormonal substrate, "
            "inflammation tone."
        ),
    ),
    Axis(
        name="cold_exposure_regime",
        kind=AxisKind.SUBSTRATE,
        unit="annual_dose",
        domain=(0.0, 1.0),
        notes=(
            "annual cold-exposure intensity x duration. modulates "
            "brown adipose tissue, mitochondrial uncoupling protein "
            "expression, vascular tone, immune robustness."
        ),
    ),
    Axis(
        name="chronic_stress_type",
        kind=AxisKind.SUBSTRATE,
        unit="categorical",
        domain=("acute_recoverable", "chronic_trapped",
                "mixed", "low_baseline"),
        notes=(
            "acute_recoverable: real threats with resolution windows "
            "(traditional load). chronic_trapped: low-grade unresolved "
            "social/economic stress (modern urban). these produce "
            "OPPOSITE methylation patterns on stress-response genes."
        ),
    ),
    Axis(
        name="light_regime",
        kind=AxisKind.SUBSTRATE,
        unit="categorical",
        domain=("natural_variation", "shift_disrupted",
                "artificial_flat", "polar_extreme"),
        notes=(
            "developmental light regime. modulates CLOCK gene "
            "expression, melatonin synthesis, vitamin D pathway, "
            "circadian-coupled hormonal rhythms."
        ),
    ),
    Axis(
        name="movement_pattern_diversity",
        kind=AxisKind.SUBSTRATE,
        unit="normalized",
        domain=(0.0, 1.0),
        notes=(
            "0=specialized/repetitive movement (modern desk + gym), "
            "1=generalist (carrying, climbing, lifting, running, "
            "throwing, fine motor across many domains). modulates "
            "neural plasticity, joint range, fascia integrity."
        ),
    ),
    Axis(
        name="social_consequence_type",
        kind=AxisKind.SUBSTRATE,
        unit="categorical",
        domain=("consensus_seeking", "reality_testing",
                "performance_signaling", "mixed"),
        notes=(
            "what the social environment rewards. consensus_seeking: "
            "agreement is currency. reality_testing: outcomes are "
            "currency. performance_signaling: appearance is currency. "
            "modulates oxytocin/cortisol coupling, social-stress "
            "set-point, decision-confidence calibration."
        ),
    ),
    Axis(
        name="developmental_diet_window",
        kind=AxisKind.SUBSTRATE,
        unit="categorical",
        domain=("traditional_continuous", "transitional",
                "post_industrial", "deprivation"),
        notes=(
            "diet during 0-20 year developmental window. "
            "traditional_continuous: ancestral nutrient profile maintained. "
            "transitional: mix of traditional and processed. "
            "post_industrial: refined seed oils, refined grains, "
            "low micronutrient density. deprivation: insufficient calories "
            "or critical nutrients. shapes lifelong metabolic baseline."
        ),
    ),
)


# ─────────────────────────────────────────────────────────────────────
# ENVIRONMENT-MODULATED TRAIT WAVEFORM
# ─────────────────────────────────────────────────────────────────────
#
# This is the key extension: a trait waveform that takes BOTH the
# normal trait axes AND environment-history axes, and produces a
# different surface for each environment slice.
# ─────────────────────────────────────────────────────────────────────

@dataclass
class EnvironmentModulatedWaveform:
    """
    Wraps a base trait evaluator with environment-modulation factors.

    The same genome (group) expresses differently across environments,
    so the waveform output depends on BOTH the immediate phase
    (cycle, sleep, glucose) AND accumulated environment history.
    """
    name: str
    group: str
    base_axes: tuple[Axis, ...]              # immediate-state axes
    environment_axes: tuple[Axis, ...]       # developmental axes
    measurement_unit: str
    base_evaluator: Callable[[dict], tuple[float, float]]
    environment_modulator: Callable[[dict, tuple[float, float]], tuple[float, float]]
    notes: str = ""
    confidence: float = 0.4

    def all_axes(self) -> tuple[Axis, ...]:
        return self.base_axes + self.environment_axes

    def required_axes(self) -> set[str]:
        return {a.name for a in self.all_axes() if a.required_for_comparison}

    def evaluate(self, **state) -> tuple[float, float]:
        missing = self.required_axes() - set(state.keys())
        if missing:
            raise UnderspecifiedComparisonError(
                f"trait '{self.name}' for group '{self.group}' requires "
                f"axes {sorted(missing)}. environment-modulated waveforms "
                f"require BOTH immediate-state AND environment-history "
                f"coordinates. scalar evaluation forbidden."
            )
        for ax in self.all_axes():
            if ax.name in state:
                ax.validate(state[ax.name])

        # split state into base and environment
        base_state = {a.name: state[a.name] for a in self.base_axes}
        env_state = {a.name: state[a.name] for a in self.environment_axes}

        base_mean, base_std = self.base_evaluator(base_state)
        return self.environment_modulator(env_state, (base_mean, base_std))


# ─────────────────────────────────────────────────────────────────────
# WRAPPER: convert env-modulated waveform into a TraitWaveform-compatible
#          object for use with TraitSurface
# ─────────────────────────────────────────────────────────────────────

def to_trait_waveform(em: EnvironmentModulatedWaveform) -> TraitWaveform:
    """Wrap environment-modulated waveform as standard TraitWaveform."""
    def evaluator(state: dict) -> tuple[float, float]:
        return em.evaluate(**state)
    return TraitWaveform(
        name=em.name,
        group=em.group,
        axes=em.all_axes(),
        measurement_unit=em.measurement_unit,
        evaluator=evaluator,
        confidence=em.confidence,
        notes=em.notes,
    )


# ─────────────────────────────────────────────────────────────────────
# REFERENCE MODULATORS (illustrative; replace with empirical fits)
# ─────────────────────────────────────────────────────────────────────

def _generic_environment_modulator(env: dict,
                                   base: tuple[float, float]) -> tuple[float, float]:
    """
    Apply environment-history factors to a base (mean, std) trait estimate.
    Each axis applies a multiplicative factor to the mean.
    Std grows when environment is poorly characterized or extreme.
    """
    mean, std = base

    # physical loading history shifts mean upward for capacity traits
    load_years = env.get("physical_load_years", 0.0)
    load_factor = 1.0 + 0.015 * math.tanh(load_years / 10.0)
    mean *= load_factor

    # real consequence density tunes calibration
    consequence = env.get("real_consequence_density", 0.0)
    consequence_factor = 1.0 + 0.10 * math.tanh(consequence / 50.0)
    mean *= consequence_factor

    # nutritional density boosts substrate availability
    nutrition = env.get("nutritional_density", 0.5)
    mean *= (0.85 + 0.30 * nutrition)

    # cold exposure builds metabolic robustness
    cold = env.get("cold_exposure_regime", 0.0)
    mean *= (1.0 + 0.08 * cold)

    # chronic stress type -- opposite directions
    stress = env.get("chronic_stress_type", "mixed")
    if stress == "acute_recoverable":
        mean *= 1.05      # well-tuned HPA, robust
    elif stress == "chronic_trapped":
        mean *= 0.85      # dysregulated HPA, depleted
        std *= 1.15       # more variable
    elif stress == "low_baseline":
        mean *= 0.95      # untested, brittle to novelty
    # mixed: no change

    # light regime
    light = env.get("light_regime", "natural_variation")
    if light == "shift_disrupted":
        mean *= 0.90
        std *= 1.10
    elif light == "artificial_flat":
        mean *= 0.95
    # natural_variation, polar_extreme: no penalty (assumes adapted)

    # movement diversity
    diversity = env.get("movement_pattern_diversity", 0.3)
    mean *= (0.92 + 0.16 * diversity)

    # social consequence type
    social = env.get("social_consequence_type", "mixed")
    if social == "reality_testing":
        mean *= 1.08      # calibration sharpens
    elif social == "performance_signaling":
        mean *= 0.92      # calibration drifts
        std *= 1.10
    elif social == "consensus_seeking":
        mean *= 0.98      # mild drift

    # developmental diet
    diet = env.get("developmental_diet_window", "transitional")
    if diet == "traditional_continuous":
        mean *= 1.05
    elif diet == "post_industrial":
        mean *= 0.92
    elif diet == "deprivation":
        mean *= 0.80
        std *= 1.20

    return mean, std


# ─────────────────────────────────────────────────────────────────────
# EXAMPLE: ENVIRONMENT-MODULATED FORCE OUTPUT
# ─────────────────────────────────────────────────────────────────────

def _strength_base_male(state: dict) -> tuple[float, float]:
    duration = state["duration_s"]
    load = state["load_normalized"]
    cycle_phase = state["circadian_phase"]
    base = 1.0 - 0.4 * math.tanh(duration / 60.0)
    circ = 1.0 + 0.05 * math.sin((cycle_phase - 16) * math.pi / 12)
    return base * circ * (1.0 - 0.2 * load), 0.15


def _strength_base_female(state: dict) -> tuple[float, float]:
    duration = state["duration_s"]
    load = state["load_normalized"]
    cycle_phase = state["circadian_phase"]
    monthly_phase = state["endocrine_phase"]
    short_disadvantage = -0.18 * math.exp(-duration / 30.0)
    endurance_advantage = 0.10 * math.tanh(duration / 300.0)
    base = 1.0 + short_disadvantage + endurance_advantage
    monthly = 1.0 + 0.03 * math.sin(2 * math.pi * monthly_phase / 28.0)
    circ = 1.0 + 0.05 * math.sin((cycle_phase - 16) * math.pi / 12)
    return base * circ * monthly * (1.0 - 0.2 * load), 0.15


BASE_STRENGTH_AXES = (
    Axis("duration_s", AxisKind.DURATION, "seconds", (0.1, 36000.0)),
    Axis("load_normalized", AxisKind.LOAD, "fraction", (0.0, 1.0)),
    Axis("circadian_phase", AxisKind.PHASE, "hour", (0.0, 24.0)),
    Axis("endocrine_phase", AxisKind.PHASE, "day", (0.0, 28.0)),
)


def build_env_modulated_strength_surface() -> TraitSurface:
    """Force output as a function of immediate state AND environment history."""
    male = EnvironmentModulatedWaveform(
        name="force_output_env",
        group="human_male",
        base_axes=BASE_STRENGTH_AXES,
        environment_axes=ENVIRONMENT_AXES,
        measurement_unit="normalized_force",
        base_evaluator=_strength_base_male,
        environment_modulator=_generic_environment_modulator,
        confidence=0.35,
        notes="illustrative; replace evaluators with empirical fits",
    )
    female = EnvironmentModulatedWaveform(
        name="force_output_env",
        group="human_female",
        base_axes=BASE_STRENGTH_AXES,
        environment_axes=ENVIRONMENT_AXES,
        measurement_unit="normalized_force",
        base_evaluator=_strength_base_female,
        environment_modulator=_generic_environment_modulator,
        confidence=0.35,
    )
    return TraitSurface(
        trait="force_output_env",
        waveforms={
            "human_male": to_trait_waveform(male),
            "human_female": to_trait_waveform(female),
        },
        description=(
            "Force output modulated by accumulated developmental "
            "environment. Two women from radically different "
            "environments show larger trait differences than "
            "average male/female within either environment. "
            "Cross-environment comparison without specification "
            "is malformed."
        ),
    )


# ─────────────────────────────────────────────────────────────────────
# CROSS-ENVIRONMENT COMPARISON UTILITY
# ─────────────────────────────────────────────────────────────────────

def compare_within_vs_across_environment(
    surface: TraitSurface,
    env_a: dict,
    env_b: dict,
    base_state: dict,
) -> dict:
    """
    Compare:
        - male vs female within env_a
        - male vs female within env_b
        - female_env_a vs female_env_b
        - male_env_a vs male_env_b

    Often shows that within-group cross-environment differences
    exceed within-environment cross-group differences. That is the
    structural refutation of "the way men/women are" claims.
    """
    state_a = {**base_state, **env_a}
    state_b = {**base_state, **env_b}
    # _label is a convenience tag, not an axis
    state_a.pop("_label", None)
    state_b.pop("_label", None)

    male_a, _ = surface.waveforms["human_male"].evaluate(**state_a)
    female_a, _ = surface.waveforms["human_female"].evaluate(**state_a)
    male_b, _ = surface.waveforms["human_male"].evaluate(**state_b)
    female_b, _ = surface.waveforms["human_female"].evaluate(**state_b)

    within_a_gap = abs(male_a - female_a)
    within_b_gap = abs(male_b - female_b)
    cross_env_male = abs(male_a - male_b)
    cross_env_female = abs(female_a - female_b)

    return {
        "trait": surface.trait,
        "env_a_label": env_a.get("_label", "env_a"),
        "env_b_label": env_b.get("_label", "env_b"),
        "within_env_a_gender_gap": within_a_gap,
        "within_env_b_gender_gap": within_b_gap,
        "cross_env_male_gap": cross_env_male,
        "cross_env_female_gap": cross_env_female,
        "ratio_cross_env_to_within_gender_female": (
            cross_env_female / within_a_gap if within_a_gap > 0 else float("inf")
        ),
        "ratio_cross_env_to_within_gender_male": (
            cross_env_male / within_a_gap if within_a_gap > 0 else float("inf")
        ),
        "interpretation": (
            "if cross_env gap > within_env gender gap, then "
            "'the way men/women are' claims are dominated by "
            "environment effects, not gender effects. group "
            "labels are confounded with environment labels."
        ),
    }


# ─────────────────────────────────────────────────────────────────────
# CANONICAL ENVIRONMENT PROFILES (for testing and demonstration)
# ─────────────────────────────────────────────────────────────────────

WEIRD_SEDENTARY_PROFILE = {
    "_label": "WEIRD_sedentary",
    "physical_load_years": 1.0,
    "real_consequence_density": 5.0,
    "nutritional_density": 0.35,
    "cold_exposure_regime": 0.05,
    "chronic_stress_type": "chronic_trapped",
    "light_regime": "artificial_flat",
    "movement_pattern_diversity": 0.2,
    "social_consequence_type": "performance_signaling",
    "developmental_diet_window": "post_industrial",
}

TRADITIONAL_HIGH_LOAD_PROFILE = {
    "_label": "traditional_high_load",
    "physical_load_years": 25.0,
    "real_consequence_density": 200.0,
    "nutritional_density": 0.85,
    "cold_exposure_regime": 0.7,
    "chronic_stress_type": "acute_recoverable",
    "light_regime": "natural_variation",
    "movement_pattern_diversity": 0.85,
    "social_consequence_type": "reality_testing",
    "developmental_diet_window": "traditional_continuous",
}

RURAL_TRADES_MIXED_PROFILE = {
    "_label": "rural_trades_mixed",
    "physical_load_years": 15.0,
    "real_consequence_density": 80.0,
    "nutritional_density": 0.55,
    "cold_exposure_regime": 0.5,
    "chronic_stress_type": "mixed",
    "light_regime": "natural_variation",
    "movement_pattern_diversity": 0.7,
    "social_consequence_type": "reality_testing",
    "developmental_diet_window": "transitional",
}


# ─────────────────────────────────────────────────────────────────────
# SELF-TEST
# ─────────────────────────────────────────────────────────────────────

def _selftest():
    print("=" * 72)
    print("environment_expression_surface -- self-test")
    print("=" * 72)

    surface = build_env_modulated_strength_surface()
    validator = ClaimValidator()
    validator.register(surface)
    guard = PhysicsGuardAdapter(validator)

    # CASE 1: scalar claim, no environment, no state -- REJECTED
    print("\n[1] 'men are stronger' -- no env, no state")
    claim = GroupComparisonClaim(
        trait="force_output_env",
        group_a="human_male",
        group_b="human_female",
        direction="a_greater",
        axes_specified={},
        raw_text="men are stronger than women",
    )
    r = guard.check(claim)
    print(f"    verdict: {r['detail']['verdict']}")
    if "missing_axes" in r["detail"]:
        print(f"    missing: {len(r['detail']['missing_axes'])} axes "
              f"(base + environment)")

    # CASE 2: state specified, env NOT specified -- still REJECTED
    print("\n[2] state pinned, environment unspecified")
    claim = GroupComparisonClaim(
        trait="force_output_env",
        group_a="human_male",
        group_b="human_female",
        direction="a_greater",
        axes_specified={
            "duration_s": 1.0,
            "load_normalized": 1.0,
            "circadian_phase": 16.0,
            "endocrine_phase": 14.0,
        },
        raw_text="at peak short effort men > women",
    )
    r = guard.check(claim)
    print(f"    verdict: {r['detail']['verdict']}")
    if "missing_axes" in r["detail"]:
        print(f"    missing axes: {r['detail']['missing_axes']}")

    # CASE 3: fully specified -- narrow claim evaluable
    print("\n[3] fully specified: WEIRD-sedentary environment, peak short effort")
    state_full = {
        "duration_s": 1.0,
        "load_normalized": 1.0,
        "circadian_phase": 16.0,
        "endocrine_phase": 14.0,
        **WEIRD_SEDENTARY_PROFILE,
    }
    state_full.pop("_label", None)
    claim = GroupComparisonClaim(
        trait="force_output_env",
        group_a="human_male",
        group_b="human_female",
        direction="a_greater",
        axes_specified=state_full,
    )
    r = guard.check(claim)
    if "comparison" in r["detail"]:
        c = r["detail"]["comparison"]
        print(f"    delta_mean: {c['delta_mean']:.3f}")
        print(f"    overlap:    {c['one_sigma_overlap']}")

    # CASE 4: cross-environment comparison -- the key diagnostic
    print("\n[4] cross-environment vs within-environment gender gaps")
    print("    (peak short-effort task)")
    base = {
        "duration_s": 1.0,
        "load_normalized": 1.0,
        "circadian_phase": 16.0,
        "endocrine_phase": 14.0,
    }
    weird = dict(WEIRD_SEDENTARY_PROFILE)
    traditional = dict(TRADITIONAL_HIGH_LOAD_PROFILE)

    result = compare_within_vs_across_environment(
        surface,
        env_a=weird,
        env_b=traditional,
        base_state=base,
    )
    print(f"    within {weird['_label']} gender gap:      "
          f"{result['within_env_a_gender_gap']:.3f}")
    print(f"    within {traditional['_label']} gender gap: "
          f"{result['within_env_b_gender_gap']:.3f}")
    print(f"    cross-env male gap:                       "
          f"{result['cross_env_male_gap']:.3f}")
    print(f"    cross-env female gap:                     "
          f"{result['cross_env_female_gap']:.3f}")
    print(f"    ratio cross-env/within-gender (female):   "
          f"{result['ratio_cross_env_to_within_gender_female']:.2f}")
    print(f"    ratio cross-env/within-gender (male):     "
          f"{result['ratio_cross_env_to_within_gender_male']:.2f}")
    print()
    print("    interpretation:")
    print(f"      {result['interpretation']}")

    # CASE 5: long endurance task -- direction relative to environment
    print("\n[5] long endurance task across environments")
    base_endurance = {
        "duration_s": 21600.0,        # 6 hours
        "load_normalized": 0.4,
        "circadian_phase": 12.0,
        "endocrine_phase": 14.0,
    }
    result2 = compare_within_vs_across_environment(
        surface,
        env_a=weird,
        env_b=traditional,
        base_state=base_endurance,
    )
    print(f"    within {weird['_label']} gender gap:      "
          f"{result2['within_env_a_gender_gap']:.3f}")
    print(f"    within {traditional['_label']} gender gap: "
          f"{result2['within_env_b_gender_gap']:.3f}")
    print(f"    cross-env female gap:                     "
          f"{result2['cross_env_female_gap']:.3f}")

    print("\n" + "=" * 72)
    print("done. environment surface forces 'from where' specification.")
    print("=" * 72)


if __name__ == "__main__":
    _selftest()
