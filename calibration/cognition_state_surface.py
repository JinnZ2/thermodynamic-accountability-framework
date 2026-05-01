"""
cognition_state_surface

CC0 / public domain. JinnZ2.

Add-on module for trait_waveform_validator.

## Purpose

Apply the phase-space anti-bias framework to cognition.

Critical structural point: "cognition" is itself a scalar collapse.
There is no single surface for "cognitive performance" -- there
is a FAMILY of task-specific surfaces.

A claim like "group X is more rational than group Y" is therefore
malformed at TWO levels:
    1. it omits phase axes (state, sleep, glucose, cycle, etc.)
    2. it omits TASK SPECIFICATION (rational at WHAT?)

This module enforces both gates.

Encoded tasks (illustrative; replace evaluators with empirical fits):
    - spatial_rotation
    - verbal_fluency
    - risk_assessment
    - pattern_integration
    - sustained_attention
    - working_memory

## Usage

    from trait_waveform_validator import ClaimValidator, PhysicsGuardAdapter
    from cognition_state_surface import register_all_cognition_surfaces

    validator = ClaimValidator()
    register_all_cognition_surfaces(validator)

    guard = PhysicsGuardAdapter(validator)
    # then: guard.check(claim)  as usual
"""

from __future__ import annotations

import math
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
# SHARED COGNITIVE STATE AXES
# ─────────────────────────────────────────────────────────────────────
#
# All cognitive task surfaces share these axes. Adding new task
# surfaces means re-using these -- comparability is preserved.
# ─────────────────────────────────────────────────────────────────────

COGNITIVE_AXES = (
    Axis(
        name="circadian_phase",
        kind=AxisKind.PHASE,
        unit="hour",
        domain=(0.0, 24.0),
        notes="hour of day; affects alertness, cortisol, body temp",
    ),
    Axis(
        name="endocrine_phase",
        kind=AxisKind.PHASE,
        unit="day",
        domain=(0.0, 28.0),
        notes="position in monthly cycle (0-28); modulates "
              "estrogen/progesterone-coupled cognition",
    ),
    Axis(
        name="sleep_debt_h",
        kind=AxisKind.SUBSTRATE,
        unit="hours",
        domain=(0.0, 72.0),
        notes="cumulative sleep deficit; nonlinear performance impact",
    ),
    Axis(
        name="glucose_state",
        kind=AxisKind.SUBSTRATE,
        unit="normalized",
        domain=(0.0, 1.0),
        notes="0=fasted/depleted, 1=well-fed",
    ),
    Axis(
        name="cortisol_load",
        kind=AxisKind.LOAD,
        unit="normalized",
        domain=(0.0, 1.0),
        notes="acute stress level; 0=baseline, 1=high stress",
    ),
    Axis(
        name="task_duration_min",
        kind=AxisKind.DURATION,
        unit="minutes",
        domain=(0.1, 480.0),
        notes="how long the task runs; relevant for fatigue, "
              "sustained attention",
    ),
)


# ─────────────────────────────────────────────────────────────────────
# SHARED MODULATORS
# ─────────────────────────────────────────────────────────────────────

def _circadian_alertness(phase_h: float) -> float:
    """
    Alertness curve. Trough ~03:00-05:00, peak afternoon, dip ~14:00.
    Returns multiplier in roughly [0.7, 1.05].
    """
    main = 0.85 + 0.15 * math.sin((phase_h - 9) * math.pi / 12)
    post_lunch_dip = -0.05 * math.exp(-((phase_h - 14) ** 2) / 1.5)
    return max(0.5, main + post_lunch_dip)


def _sleep_decrement(sleep_debt_h: float) -> float:
    """Nonlinear; first 8 hours mild, then steep."""
    return max(0.3, 1.0 - 0.02 * sleep_debt_h - 0.005 * (sleep_debt_h ** 1.4))


def _stress_curve(cortisol: float, task_complexity: float) -> float:
    """
    Yerkes-Dodson: low/moderate stress can help simple tasks,
    hurts complex tasks. High stress hurts both.
    """
    optimum = 0.4 - 0.25 * task_complexity   # complex task -> lower optimum
    return 1.0 - 2.0 * (cortisol - optimum) ** 2


def _glucose_factor(g: float) -> float:
    return 0.6 + 0.4 * g


def _fatigue_factor(duration_min: float, hardness: float) -> float:
    """Sustained-task fatigue. hardness in [0,1]."""
    return max(0.4, 1.0 - hardness * math.tanh(duration_min / 60.0) * 0.4)


# ─────────────────────────────────────────────────────────────────────
# TASK 1: SPATIAL ROTATION  (testosterone-correlated, on average)
# ─────────────────────────────────────────────────────────────────────
#
# Both groups have wide overlapping distributions. Phase modulation
# matters: testosterone has both circadian and stress dependence.
# ─────────────────────────────────────────────────────────────────────

def _spatial_rotation_male(s: dict) -> tuple[float, float]:
    base = 1.05
    base *= _circadian_alertness(s["circadian_phase"])
    base *= _sleep_decrement(s["sleep_debt_h"])
    base *= _glucose_factor(s["glucose_state"])
    base *= _stress_curve(s["cortisol_load"], task_complexity=0.6)
    base *= _fatigue_factor(s["task_duration_min"], hardness=0.5)
    return base, 0.20  # large overlap with female distribution


def _spatial_rotation_female(s: dict) -> tuple[float, float]:
    base = 0.95
    # estrogen-coupled modulation of spatial cognition (small)
    cycle = s["endocrine_phase"]
    base *= 1.0 + 0.04 * math.cos(2 * math.pi * cycle / 28.0)
    base *= _circadian_alertness(s["circadian_phase"])
    base *= _sleep_decrement(s["sleep_debt_h"])
    base *= _glucose_factor(s["glucose_state"])
    base *= _stress_curve(s["cortisol_load"], task_complexity=0.6)
    base *= _fatigue_factor(s["task_duration_min"], hardness=0.5)
    return base, 0.20


def build_spatial_rotation_surface() -> TraitSurface:
    male = TraitWaveform(
        name="spatial_rotation_score",
        group="human_male",
        axes=COGNITIVE_AXES,
        measurement_unit="normalized",
        evaluator=_spatial_rotation_male,
        confidence=0.4,
        notes="illustrative; mean differences smaller than within-group SD",
    )
    female = TraitWaveform(
        name="spatial_rotation_score",
        group="human_female",
        axes=COGNITIVE_AXES,
        measurement_unit="normalized",
        evaluator=_spatial_rotation_female,
        confidence=0.4,
    )
    return TraitSurface(
        trait="spatial_rotation",
        waveforms={"human_male": male, "human_female": female},
        description=(
            "3D mental rotation tasks. Group means differ slightly on "
            "average; within-group variance dominates. Training closes "
            "most of the gap. Phase-coupled modulation is real but small."
        ),
    )


# ─────────────────────────────────────────────────────────────────────
# TASK 2: VERBAL FLUENCY  (estrogen-correlated, on average)
# ─────────────────────────────────────────────────────────────────────

def _verbal_fluency_male(s: dict) -> tuple[float, float]:
    base = 0.95
    base *= _circadian_alertness(s["circadian_phase"])
    base *= _sleep_decrement(s["sleep_debt_h"])
    base *= _glucose_factor(s["glucose_state"])
    base *= _stress_curve(s["cortisol_load"], task_complexity=0.5)
    base *= _fatigue_factor(s["task_duration_min"], hardness=0.4)
    return base, 0.20


def _verbal_fluency_female(s: dict) -> tuple[float, float]:
    base = 1.05
    cycle = s["endocrine_phase"]
    # peak around mid-cycle / late-follicular when estrogen high
    base *= 1.0 + 0.05 * math.sin(2 * math.pi * (cycle - 7) / 28.0)
    base *= _circadian_alertness(s["circadian_phase"])
    base *= _sleep_decrement(s["sleep_debt_h"])
    base *= _glucose_factor(s["glucose_state"])
    base *= _stress_curve(s["cortisol_load"], task_complexity=0.5)
    base *= _fatigue_factor(s["task_duration_min"], hardness=0.4)
    return base, 0.20


def build_verbal_fluency_surface() -> TraitSurface:
    male = TraitWaveform(
        name="verbal_fluency_score",
        group="human_male",
        axes=COGNITIVE_AXES,
        measurement_unit="normalized",
        evaluator=_verbal_fluency_male,
        confidence=0.4,
    )
    female = TraitWaveform(
        name="verbal_fluency_score",
        group="human_female",
        axes=COGNITIVE_AXES,
        measurement_unit="normalized",
        evaluator=_verbal_fluency_female,
        confidence=0.4,
    )
    return TraitSurface(
        trait="verbal_fluency",
        waveforms={"human_male": male, "human_female": female},
        description=(
            "Verbal generation tasks (category fluency, letter fluency). "
            "Small mean differences with large within-group variance. "
            "Cycle-phase modulation present in female cohort; "
            "circadian and stress modulation present in both."
        ),
    )


# ─────────────────────────────────────────────────────────────────────
# TASK 3: RISK ASSESSMENT  (state-dependent in BOTH groups)
# ─────────────────────────────────────────────────────────────────────
#
# This one is critical for the gender/rationality argument. Risk
# assessment is hormonally modulated in BOTH groups. Testosterone and
# cortisol both shift risk thresholds; cycle phase shifts thresholds
# in females. The question is not "who is more rational" -- it is
# "what state is each system in right now, and what is the task?"
# ─────────────────────────────────────────────────────────────────────

def _risk_assessment_male(s: dict) -> tuple[float, float]:
    """
    Risk-assessment QUALITY (calibration), not risk-taking propensity.
    High score = well-calibrated to actual probabilities.
    """
    base = 1.0
    # circadian testosterone peak (morning) -> slightly more risk-taking,
    # which can REDUCE calibration on probability tasks
    t_phase = s["circadian_phase"]
    testosterone_factor = 1.0 + 0.08 * math.sin((t_phase - 6) * math.pi / 12)
    base /= testosterone_factor   # higher T -> slightly worse calibration
    base *= _circadian_alertness(s["circadian_phase"])
    base *= _sleep_decrement(s["sleep_debt_h"])
    base *= _glucose_factor(s["glucose_state"])
    # acute stress degrades probability calibration
    base *= max(0.5, 1.0 - 0.4 * s["cortisol_load"])
    base *= _fatigue_factor(s["task_duration_min"], hardness=0.7)
    return base, 0.22


def _risk_assessment_female(s: dict) -> tuple[float, float]:
    base = 1.0
    cycle = s["endocrine_phase"]
    # luteal phase: progesterone rises, slight calibration shifts
    base *= 1.0 + 0.05 * math.cos(2 * math.pi * (cycle - 21) / 28.0)
    base *= _circadian_alertness(s["circadian_phase"])
    base *= _sleep_decrement(s["sleep_debt_h"])
    base *= _glucose_factor(s["glucose_state"])
    base *= max(0.5, 1.0 - 0.4 * s["cortisol_load"])
    base *= _fatigue_factor(s["task_duration_min"], hardness=0.7)
    return base, 0.22


def build_risk_assessment_surface() -> TraitSurface:
    male = TraitWaveform(
        name="risk_assessment_calibration",
        group="human_male",
        axes=COGNITIVE_AXES,
        measurement_unit="normalized",
        evaluator=_risk_assessment_male,
        confidence=0.35,
        notes="measures calibration, not risk preference; both groups "
              "are state-dependent; means are not constant",
    )
    female = TraitWaveform(
        name="risk_assessment_calibration",
        group="human_female",
        axes=COGNITIVE_AXES,
        measurement_unit="normalized",
        evaluator=_risk_assessment_female,
        confidence=0.35,
    )
    return TraitSurface(
        trait="risk_assessment",
        waveforms={"human_male": male, "human_female": female},
        description=(
            "Probability calibration on risk tasks. Both groups show "
            "hormonal state-dependence. Direction of any group difference "
            "FLIPS depending on phase coordinates. No scalar claim is "
            "defensible."
        ),
    )


# ─────────────────────────────────────────────────────────────────────
# TASK 4: PATTERN INTEGRATION  (cross-domain synthesis)
# ─────────────────────────────────────────────────────────────────────

def _pattern_integration_male(s: dict) -> tuple[float, float]:
    base = 1.0
    base *= _circadian_alertness(s["circadian_phase"])
    base *= _sleep_decrement(s["sleep_debt_h"])
    base *= _glucose_factor(s["glucose_state"])
    base *= _stress_curve(s["cortisol_load"], task_complexity=0.8)
    base *= _fatigue_factor(s["task_duration_min"], hardness=0.6)
    return base, 0.22


def _pattern_integration_female(s: dict) -> tuple[float, float]:
    base = 1.0
    cycle = s["endocrine_phase"]
    base *= 1.0 + 0.03 * math.sin(2 * math.pi * (cycle - 14) / 28.0)
    base *= _circadian_alertness(s["circadian_phase"])
    base *= _sleep_decrement(s["sleep_debt_h"])
    base *= _glucose_factor(s["glucose_state"])
    base *= _stress_curve(s["cortisol_load"], task_complexity=0.8)
    base *= _fatigue_factor(s["task_duration_min"], hardness=0.6)
    return base, 0.22


def build_pattern_integration_surface() -> TraitSurface:
    male = TraitWaveform(
        name="pattern_integration",
        group="human_male",
        axes=COGNITIVE_AXES,
        measurement_unit="normalized",
        evaluator=_pattern_integration_male,
        confidence=0.3,
    )
    female = TraitWaveform(
        name="pattern_integration",
        group="human_female",
        axes=COGNITIVE_AXES,
        measurement_unit="normalized",
        evaluator=_pattern_integration_female,
        confidence=0.3,
    )
    return TraitSurface(
        trait="pattern_integration",
        waveforms={"human_male": male, "human_female": female},
        description=(
            "Cross-domain synthesis tasks. Means largely overlap. "
            "State and complexity dominate group identity."
        ),
    )


# ─────────────────────────────────────────────────────────────────────
# TASK 5: SUSTAINED ATTENTION
# ─────────────────────────────────────────────────────────────────────

def _sustained_attention_male(s: dict) -> tuple[float, float]:
    base = 1.0
    base *= _circadian_alertness(s["circadian_phase"])
    base *= _sleep_decrement(s["sleep_debt_h"])
    base *= _glucose_factor(s["glucose_state"])
    base *= _stress_curve(s["cortisol_load"], task_complexity=0.4)
    # vigilance decrement is steep
    base *= _fatigue_factor(s["task_duration_min"], hardness=0.85)
    return base, 0.20


def _sustained_attention_female(s: dict) -> tuple[float, float]:
    base = 1.0
    base *= _circadian_alertness(s["circadian_phase"])
    base *= _sleep_decrement(s["sleep_debt_h"])
    base *= _glucose_factor(s["glucose_state"])
    base *= _stress_curve(s["cortisol_load"], task_complexity=0.4)
    base *= _fatigue_factor(s["task_duration_min"], hardness=0.85)
    return base, 0.20


def build_sustained_attention_surface() -> TraitSurface:
    male = TraitWaveform(
        name="sustained_attention",
        group="human_male",
        axes=COGNITIVE_AXES,
        measurement_unit="normalized",
        evaluator=_sustained_attention_male,
        confidence=0.4,
    )
    female = TraitWaveform(
        name="sustained_attention",
        group="human_female",
        axes=COGNITIVE_AXES,
        measurement_unit="normalized",
        evaluator=_sustained_attention_female,
        confidence=0.4,
    )
    return TraitSurface(
        trait="sustained_attention",
        waveforms={"human_male": male, "human_female": female},
        description=(
            "Vigilance tasks. Group means highly overlapping. "
            "Sleep state and duration dominate any group effect."
        ),
    )


# ─────────────────────────────────────────────────────────────────────
# TASK 6: WORKING MEMORY
# ─────────────────────────────────────────────────────────────────────

def _working_memory_male(s: dict) -> tuple[float, float]:
    base = 1.0
    base *= _circadian_alertness(s["circadian_phase"])
    base *= _sleep_decrement(s["sleep_debt_h"])
    base *= _glucose_factor(s["glucose_state"])
    base *= _stress_curve(s["cortisol_load"], task_complexity=0.7)
    base *= _fatigue_factor(s["task_duration_min"], hardness=0.5)
    return base, 0.22


def _working_memory_female(s: dict) -> tuple[float, float]:
    base = 1.0
    cycle = s["endocrine_phase"]
    base *= 1.0 + 0.04 * math.sin(2 * math.pi * (cycle - 10) / 28.0)
    base *= _circadian_alertness(s["circadian_phase"])
    base *= _sleep_decrement(s["sleep_debt_h"])
    base *= _glucose_factor(s["glucose_state"])
    base *= _stress_curve(s["cortisol_load"], task_complexity=0.7)
    base *= _fatigue_factor(s["task_duration_min"], hardness=0.5)
    return base, 0.22


def build_working_memory_surface() -> TraitSurface:
    male = TraitWaveform(
        name="working_memory",
        group="human_male",
        axes=COGNITIVE_AXES,
        measurement_unit="normalized",
        evaluator=_working_memory_male,
        confidence=0.4,
    )
    female = TraitWaveform(
        name="working_memory",
        group="human_female",
        axes=COGNITIVE_AXES,
        measurement_unit="normalized",
        evaluator=_working_memory_female,
        confidence=0.4,
    )
    return TraitSurface(
        trait="working_memory",
        waveforms={"human_male": male, "human_female": female},
        description=(
            "N-back, digit span tasks. Group means highly overlapping; "
            "state effects dominate."
        ),
    )


# ─────────────────────────────────────────────────────────────────────
# RATIONALITY-CLAIM GUARD
# ─────────────────────────────────────────────────────────────────────
#
# The original document's argument: "rationality" claims about groups.
# This class catches "rationality" as the OUTER scalar collapse --
# rationality at WHICH task? -- before delegating to the appropriate
# task surface.
# ─────────────────────────────────────────────────────────────────────

REGISTERED_COGNITION_TASKS = (
    "spatial_rotation",
    "verbal_fluency",
    "risk_assessment",
    "pattern_integration",
    "sustained_attention",
    "working_memory",
)


class CognitionScalarCollapseError(WaveformError):
    """Raised when 'cognition' or 'rationality' claim has no task specified."""


def validate_cognition_claim(
    validator: ClaimValidator,
    group_a: str,
    group_b: str,
    direction: str,
    task: str | None = None,
    axes_specified: dict | None = None,
    raw_text: str | None = None,
) -> dict:
    """
    Two-level gate:
        1. task must be specified (or claim is rejected)
        2. all phase axes must be specified for that task

    This is the operationalization of the document's argument: a claim
    about "rationality" is malformed at TWO levels of abstraction.
    """
    if task is None or task not in REGISTERED_COGNITION_TASKS:
        return {
            "verdict": "REJECTED_unspecified_task",
            "advisory": (
                f"claim '{raw_text or '<unspecified>'}' references "
                f"'cognition' / 'rationality' / 'intelligence' without "
                f"specifying the task. "
                f"these are scalar collapses of distinct functions: "
                f"{list(REGISTERED_COGNITION_TASKS)}. "
                f"specify a task first, then specify phase axes."
            ),
            "available_tasks": list(REGISTERED_COGNITION_TASKS),
            "scalar_claim_permitted": False,
        }

    claim = GroupComparisonClaim(
        trait=task,
        group_a=group_a,
        group_b=group_b,
        direction=direction,
        axes_specified=axes_specified or {},
        raw_text=raw_text,
    )
    return validator.validate(claim)


# ─────────────────────────────────────────────────────────────────────
# REGISTRATION
# ─────────────────────────────────────────────────────────────────────

def register_all_cognition_surfaces(validator: ClaimValidator) -> None:
    """Register all six cognitive task surfaces with an existing validator."""
    validator.register(build_spatial_rotation_surface())
    validator.register(build_verbal_fluency_surface())
    validator.register(build_risk_assessment_surface())
    validator.register(build_pattern_integration_surface())
    validator.register(build_sustained_attention_surface())
    validator.register(build_working_memory_surface())


# ─────────────────────────────────────────────────────────────────────
# SELF-TEST
# ─────────────────────────────────────────────────────────────────────

def _selftest():
    print("=" * 72)
    print("cognition_state_surface -- self-test (add-on to trait_waveform_validator)")
    print("=" * 72)

    validator = ClaimValidator()
    register_all_cognition_surfaces(validator)
    guard = PhysicsGuardAdapter(validator)

    # CASE A: scalar 'rationality' claim -- outer task layer rejects
    print("\n[A] 'group X is more rational than group Y' -- no task, no axes")
    result = validate_cognition_claim(
        validator,
        group_a="human_male",
        group_b="human_female",
        direction="a_greater",
        task=None,
        axes_specified={},
        raw_text="men are more rational than women",
    )
    print(f"    verdict: {result['verdict']}")
    print(f"    advisory:\n      {result['advisory']}")

    # CASE B: task specified, no phase axes -- inner gate fires
    print("\n[B] task=risk_assessment, no axes -- phase-axis gate fires")
    result = validate_cognition_claim(
        validator,
        group_a="human_male",
        group_b="human_female",
        direction="a_greater",
        task="risk_assessment",
        axes_specified={},
        raw_text="men have better risk calibration",
    )
    print(f"    verdict: {result['verdict']}")
    if "missing_axes" in result:
        print(f"    missing axes: {result['missing_axes']}")

    # CASE C: fully specified narrow claim
    print("\n[C] fully specified: risk_assessment, morning, baseline state")
    state_morning = {
        "circadian_phase": 9.0,
        "endocrine_phase": 14.0,
        "sleep_debt_h": 0.0,
        "glucose_state": 0.8,
        "cortisol_load": 0.3,
        "task_duration_min": 15.0,
    }
    result = validate_cognition_claim(
        validator,
        group_a="human_male",
        group_b="human_female",
        direction="a_greater",
        task="risk_assessment",
        axes_specified=state_morning,
        raw_text="at morning, low stress, fed: male calibration higher",
    )
    print(f"    verdict: {result['verdict']}")
    if "comparison" in result:
        c = result["comparison"]
        print(f"    delta_mean: {c['delta_mean']:.3f}")
        print(f"    overlap:    {c['one_sigma_overlap']}")

    # CASE D: same task, sleep-deprived stressed afternoon -- does direction flip?
    print("\n[D] same task, late afternoon, sleep-deprived, high stress")
    state_stressed = {
        "circadian_phase": 16.0,
        "endocrine_phase": 21.0,    # luteal phase
        "sleep_debt_h": 18.0,
        "glucose_state": 0.3,
        "cortisol_load": 0.8,
        "task_duration_min": 90.0,
    }
    result = validate_cognition_claim(
        validator,
        group_a="human_male",
        group_b="human_female",
        direction="a_greater",
        task="risk_assessment",
        axes_specified=state_stressed,
    )
    if "comparison" in result:
        c = result["comparison"]
        print(f"    delta_mean: {c['delta_mean']:.3f}")
        print(f"    overlap:    {c['one_sigma_overlap']}")

    # CASE E: sweep risk_assessment phase space -- sign-flip diagnostic
    print("\n[E] phase-space sweep on risk_assessment")
    surface = validator.surfaces["risk_assessment"]
    sweep = surface.map_overlap_region(
        sample_grid={
            "circadian_phase": [6, 10, 14, 18, 22],
            "endocrine_phase": [3, 10, 17, 24],
            "sleep_debt_h": [0, 8, 24],
            "glucose_state": [0.3, 0.8],
            "cortisol_load": [0.1, 0.5, 0.9],
            "task_duration_min": [5, 60, 240],
        },
        group_a="human_male",
        group_b="human_female",
    )
    print(f"    n_phase_points:           {sweep['n_phase_points']}")
    print(f"    fraction_indistinguishable: {sweep['fraction_indistinguishable']:.2%}")
    print(f"    fraction_male_greater:    {sweep['fraction_a_greater']:.2%}")
    print(f"    fraction_female_greater:  {sweep['fraction_b_greater']:.2%}")
    print(f"    sign_flips:               {sweep['sign_flips_across_phase_space']}")
    print(f"    scalar_claim_defensible:  {sweep['scalar_claim_defensible']}")
    print(f"    advisory: {sweep['advisory']}")

    # CASE F: sweep verbal_fluency -- different task, possibly different shape
    print("\n[F] phase-space sweep on verbal_fluency (compare to risk_assessment)")
    surface = validator.surfaces["verbal_fluency"]
    sweep = surface.map_overlap_region(
        sample_grid={
            "circadian_phase": [6, 10, 14, 18, 22],
            "endocrine_phase": [3, 10, 17, 24],
            "sleep_debt_h": [0, 8, 24],
            "glucose_state": [0.3, 0.8],
            "cortisol_load": [0.1, 0.5, 0.9],
            "task_duration_min": [5, 60, 240],
        },
        group_a="human_male",
        group_b="human_female",
    )
    print(f"    fraction_indistinguishable: {sweep['fraction_indistinguishable']:.2%}")
    print(f"    fraction_male_greater:    {sweep['fraction_a_greater']:.2%}")
    print(f"    fraction_female_greater:  {sweep['fraction_b_greater']:.2%}")
    print(f"    sign_flips:               {sweep['sign_flips_across_phase_space']}")
    print(f"    scalar_claim_defensible:  {sweep['scalar_claim_defensible']}")

    # CASE G: working_memory -- the answer per task is not the answer overall
    print("\n[G] phase-space sweep on working_memory")
    surface = validator.surfaces["working_memory"]
    sweep = surface.map_overlap_region(
        sample_grid={
            "circadian_phase": [10, 14, 18],
            "endocrine_phase": [7, 14, 21],
            "sleep_debt_h": [0, 12],
            "glucose_state": [0.5],
            "cortisol_load": [0.2, 0.6],
            "task_duration_min": [10, 60],
        },
        group_a="human_male",
        group_b="human_female",
    )
    print(f"    fraction_indistinguishable: {sweep['fraction_indistinguishable']:.2%}")
    print(f"    advisory: {sweep['advisory']}")

    print("\n" + "=" * 72)
    print("done. add-on integrates cleanly with base validator.")
    print("=" * 72)


if __name__ == "__main__":
    _selftest()
