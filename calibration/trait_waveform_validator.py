"""
trait_waveform_validator

CC0 / public domain. JinnZ2.

## Purpose

Replace scalar group-comparison ("A is stronger than B") with
phase-space comparison ("A(t, phase, load, duration, task) vs
B(t, phase, load, duration, task)").

This is not a bias offset. It is a structural reformulation that
makes scalar bias a TYPE ERROR rather than a value error.

## Core property

A claim of form
    group_X {comparator} group_Y  on trait T
is rejected unless ALL required axes are specified.
At that point the claim either:
    (a) becomes narrow, testable, and useful, or
    (b) reveals itself as cherry-picked.

No more hidden defaults. Bias must declare its coordinates.

Plugs into PhysicsGuard via PhysicsGuardAdapter (bottom of file).
Zero dependencies. Pure stdlib.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Callable, Optional, Any
from enum import Enum


# ─────────────────────────────────────────────────────────────────────
# EXCEPTIONS
# ─────────────────────────────────────────────────────────────────────

class WaveformError(Exception):
    """Base class."""


class UnderspecifiedComparisonError(WaveformError):
    """
    Raised when a comparison is attempted without specifying all
    required phase/load/duration/task axes.

    This is the core anti-bias mechanism. Scalar comparison is
    not a bug to be filtered; it is a malformed query.
    """


class ScalarCollapseError(WaveformError):
    """
    Raised when a query attempts to reduce a phase-space surface
    to a single number without specifying coordinates.
    """


class IncompatibleSurfaceError(WaveformError):
    """
    Raised when comparing two surfaces whose axes do not align.
    """


# ─────────────────────────────────────────────────────────────────────
# AXIS PRIMITIVES
# ─────────────────────────────────────────────────────────────────────

class AxisKind(Enum):
    PHASE = "phase"          # endocrine cycle position, circadian, etc.
    LOAD = "load"            # external demand
    DURATION = "duration"    # time scale of the task
    TASK = "task"            # task type / class
    SUBSTRATE = "substrate"  # individual-level state (sleep, age, etc.)


@dataclass(frozen=True)
class Axis:
    name: str
    kind: AxisKind
    unit: str
    domain: tuple                          # (min, max) or tuple of categoricals
    required_for_comparison: bool = True
    notes: str = ""

    def validate(self, value) -> None:
        if isinstance(self.domain, tuple) and len(self.domain) == 2 \
                and all(isinstance(x, (int, float)) for x in self.domain):
            lo, hi = self.domain
            if not (lo <= value <= hi):
                raise WaveformError(
                    f"axis '{self.name}' value {value} outside domain [{lo},{hi}]"
                )
        else:
            if value not in self.domain:
                raise WaveformError(
                    f"axis '{self.name}' value {value!r} not in {self.domain}"
                )


# ─────────────────────────────────────────────────────────────────────
# TRAIT WAVEFORM
# ─────────────────────────────────────────────────────────────────────

@dataclass
class TraitWaveform:
    """
    A trait expressed as a function over phase-space, not a scalar.

    `evaluator` receives a dict of axis_name -> value and returns
    (mean, stddev) at that point in phase space.

    stddev is required. A waveform without uncertainty is a lie.
    """
    name: str
    group: str                              # e.g., "human_male", "human_female"
    axes: tuple[Axis, ...]
    measurement_unit: str
    evaluator: Callable[[dict], tuple[float, float]]
    citations: tuple[str, ...] = ()
    confidence: float = 0.5                 # epistemic confidence in the model
    notes: str = ""

    def required_axes(self) -> set[str]:
        return {a.name for a in self.axes if a.required_for_comparison}

    def evaluate(self, **state) -> tuple[float, float]:
        missing = self.required_axes() - set(state.keys())
        if missing:
            raise UnderspecifiedComparisonError(
                f"trait '{self.name}' for group '{self.group}' "
                f"requires axes {sorted(missing)} to evaluate. "
                f"scalar evaluation is not permitted."
            )
        for ax in self.axes:
            if ax.name in state:
                ax.validate(state[ax.name])
        return self.evaluator(state)

    def __repr__(self):
        axnames = ",".join(a.name for a in self.axes)
        return f"TraitWaveform({self.name}@{self.group} | axes=[{axnames}])"


# ─────────────────────────────────────────────────────────────────────
# TRAIT SURFACE  (multi-group, comparison-aware)
# ─────────────────────────────────────────────────────────────────────

@dataclass
class TraitSurface:
    """
    A trait sampled across multiple groups. Comparisons are only
    permitted with all required axes pinned.
    """
    trait: str
    waveforms: dict[str, TraitWaveform]     # group_name -> waveform
    description: str = ""

    def __post_init__(self):
        if len(self.waveforms) < 2:
            return
        ref = next(iter(self.waveforms.values()))
        ref_axes = ref.required_axes()
        for g, wf in self.waveforms.items():
            if wf.required_axes() != ref_axes:
                raise IncompatibleSurfaceError(
                    f"group '{g}' axes {wf.required_axes()} do not match "
                    f"reference axes {ref_axes}. surfaces must share axes."
                )

    def required_axes(self) -> set[str]:
        return next(iter(self.waveforms.values())).required_axes()

    def evaluate_all(self, **state) -> dict[str, tuple[float, float]]:
        return {g: wf.evaluate(**state) for g, wf in self.waveforms.items()}

    def compare(self, group_a: str, group_b: str, **state) -> dict:
        """
        Returns structured comparison at a fully-specified phase point.
        Includes overlap detection (1-sigma) so 'difference' is not
        claimed when the distributions overlap.
        """
        missing = self.required_axes() - set(state.keys())
        if missing:
            raise UnderspecifiedComparisonError(
                f"comparison of '{group_a}' vs '{group_b}' on trait "
                f"'{self.trait}' requires axes {sorted(missing)}. "
                f"refusing scalar collapse."
            )
        if group_a not in self.waveforms or group_b not in self.waveforms:
            raise WaveformError(f"unknown group(s): {group_a}, {group_b}")

        ma, sa = self.waveforms[group_a].evaluate(**state)
        mb, sb = self.waveforms[group_b].evaluate(**state)

        # overlap test: do 1-sigma bands intersect?
        overlap = not (ma + sa < mb - sb or mb + sb < ma - sa)
        # effect size (Cohen's d, pooled stddev)
        pooled = math.sqrt((sa * sa + sb * sb) / 2) if (sa or sb) else 0.0
        d = (ma - mb) / pooled if pooled > 0 else float("inf") if ma != mb else 0.0

        # verdict
        if overlap and abs(d) < 0.2:
            verdict = "indistinguishable_at_this_phase"
        elif abs(d) < 0.5:
            verdict = "small_difference"
        elif abs(d) < 0.8:
            verdict = "moderate_difference"
        else:
            verdict = "large_difference"

        return {
            "trait": self.trait,
            "phase_point": dict(state),
            "group_a": {"name": group_a, "mean": ma, "stddev": sa},
            "group_b": {"name": group_b, "mean": mb, "stddev": sb},
            "delta_mean": ma - mb,
            "cohens_d": d,
            "one_sigma_overlap": overlap,
            "verdict": verdict,
            "axis_specification": "complete",
            "scalar_claim_permitted": False,
            "narrow_claim_permitted": True,
        }

    def map_overlap_region(
        self,
        sample_grid: dict[str, list],
        group_a: str,
        group_b: str,
    ) -> dict:
        """
        Sample the phase space and report:
            - fraction of sampled points where groups are indistinguishable
            - fraction where group_a > group_b
            - fraction where group_b > group_a
        This is the anti-bias diagnostic: if the answer flips sign across
        the phase space, no scalar claim is defensible.
        """
        from itertools import product

        keys = list(sample_grid.keys())
        vals = [sample_grid[k] for k in keys]

        n = 0
        n_overlap = 0
        n_a_greater = 0
        n_b_greater = 0

        for combo in product(*vals):
            state = dict(zip(keys, combo))
            try:
                result = self.compare(group_a, group_b, **state)
            except WaveformError:
                continue
            n += 1
            if result["one_sigma_overlap"]:
                n_overlap += 1
            elif result["delta_mean"] > 0:
                n_a_greater += 1
            else:
                n_b_greater += 1

        if n == 0:
            return {"error": "no valid phase points sampled"}

        sign_flip = (n_a_greater > 0 and n_b_greater > 0)
        return {
            "trait": self.trait,
            "n_phase_points": n,
            "fraction_indistinguishable": n_overlap / n,
            "fraction_a_greater": n_a_greater / n,
            "fraction_b_greater": n_b_greater / n,
            "sign_flips_across_phase_space": sign_flip,
            "scalar_claim_defensible": (
                not sign_flip and (n_overlap / n) < 0.2
            ),
            "advisory": (
                "scalar comparison is INVALID -- direction reverses across phase"
                if sign_flip else
                "scalar comparison is INVALID -- distributions overlap on most of phase space"
                if (n_overlap / n) >= 0.2 else
                "narrow claim may be defensible if all axes are specified"
            ),
        }


# ─────────────────────────────────────────────────────────────────────
# CLAIM VALIDATOR  (the bias-as-type-error gate)
# ─────────────────────────────────────────────────────────────────────

@dataclass
class GroupComparisonClaim:
    """
    Structured representation of a claim like
    'group A is more X than group B'
    """
    trait: str
    group_a: str
    group_b: str
    direction: str              # "a_greater", "b_greater", "equal"
    axes_specified: dict        # phase point, possibly empty
    raw_text: Optional[str] = None


@dataclass
class ClaimValidator:
    """
    Validates claims against TraitSurfaces.
    Refuses scalar claims structurally.
    """
    surfaces: dict[str, TraitSurface] = field(default_factory=dict)

    def register(self, surface: TraitSurface) -> None:
        self.surfaces[surface.trait] = surface

    def validate(self, claim: GroupComparisonClaim) -> dict:
        if claim.trait not in self.surfaces:
            return {
                "verdict": "unknown_trait",
                "trait": claim.trait,
                "advisory": "no waveform model registered for this trait",
            }
        surface = self.surfaces[claim.trait]
        required = surface.required_axes()
        missing = required - set(claim.axes_specified.keys())

        if missing:
            return {
                "verdict": "REJECTED_scalar_collapse",
                "trait": claim.trait,
                "missing_axes": sorted(missing),
                "advisory": (
                    f"claim '{claim.raw_text or claim.trait}' compares "
                    f"groups without specifying {sorted(missing)}. "
                    f"this is a malformed query, not a question with an answer. "
                    f"specify axes or withdraw claim."
                ),
                "scalar_claim_permitted": False,
            }

        # axes specified -- evaluate
        try:
            comp = surface.compare(
                claim.group_a, claim.group_b, **claim.axes_specified
            )
        except WaveformError as e:
            return {"verdict": "evaluation_error", "error": str(e)}

        claim_supported = (
            (claim.direction == "a_greater" and comp["delta_mean"] > 0
             and not comp["one_sigma_overlap"]) or
            (claim.direction == "b_greater" and comp["delta_mean"] < 0
             and not comp["one_sigma_overlap"]) or
            (claim.direction == "equal" and comp["one_sigma_overlap"])
        )
        return {
            "verdict": "supported_at_phase_point" if claim_supported else "not_supported_at_phase_point",
            "comparison": comp,
            "narrow_claim_only": True,
            "advisory": (
                "claim holds at the specified phase point. "
                "DOES NOT generalize to other phase points without re-evaluation."
            ),
        }


# ─────────────────────────────────────────────────────────────────────
# PHYSICSGUARD ADAPTER
# ─────────────────────────────────────────────────────────────────────

class PhysicsGuardAdapter:
    """
    Plug-in for PhysicsGuard.

    PhysicsGuard checks semantic claims against physical constraints.
    This adapter adds a constraint class:
        'group comparison claims must specify all phase axes'
    Any claim failing this check is flagged before any other
    physical constraint is evaluated.
    """

    CONSTRAINT_NAME = "phase_space_specification_required"

    def __init__(self, validator: ClaimValidator):
        self.validator = validator

    def check(self, claim: GroupComparisonClaim) -> dict:
        result = self.validator.validate(claim)
        return {
            "constraint": self.CONSTRAINT_NAME,
            "passed": result["verdict"] not in (
                "REJECTED_scalar_collapse", "evaluation_error"
            ),
            "detail": result,
        }

    def to_physicsguard_dict(self) -> dict:
        """Output format compatible with PhysicsGuard's audit log."""
        return {
            "name": self.CONSTRAINT_NAME,
            "type": "structural",
            "description": (
                "Group-comparison claims on biological traits require "
                "full phase-space coordinate specification. Scalar "
                "claims are rejected as malformed."
            ),
            "mechanism": (
                "trait V(t, phase, load, duration, task) is a surface, "
                "not a scalar. comparison without coordinate "
                "specification = type error."
            ),
        }


# ─────────────────────────────────────────────────────────────────────
# REFERENCE WAVEFORMS  (illustrative; replace evaluators with empirical fits)
# ─────────────────────────────────────────────────────────────────────
#
# These are STRUCTURAL examples showing how to encode known biology.
# The evaluator functions are simplified placeholders; real deployment
# replaces them with empirical fits from peer-reviewed datasets.
#
# The point is the SHAPE of the model, not the constants.
# ─────────────────────────────────────────────────────────────────────

def _strength_male(state: dict) -> tuple[float, float]:
    duration = state["duration_s"]              # how long must force be applied
    load = state["load_normalized"]              # 0..1 of max
    cycle_phase = state["circadian_phase"]       # 0..24 hours
    # peak-power favored at short durations; circadian peak afternoon
    base = 1.0 - 0.4 * math.tanh(duration / 60.0)
    circ = 1.0 + 0.05 * math.sin((cycle_phase - 16) * math.pi / 12)
    return base * circ * (1.0 - 0.2 * load), 0.15


def _strength_female(state: dict) -> tuple[float, float]:
    duration = state["duration_s"]
    load = state["load_normalized"]
    cycle_phase = state["circadian_phase"]
    monthly_phase = state["endocrine_phase"]     # 0..28 days
    # at very short max-power durations, lower mean
    # at long durations, equal or higher (fat oxidation, fatigue resistance)
    short_disadvantage = -0.18 * math.exp(-duration / 30.0)
    endurance_advantage = 0.10 * math.tanh(duration / 300.0)
    base = 1.0 + short_disadvantage + endurance_advantage
    monthly = 1.0 + 0.03 * math.sin(2 * math.pi * monthly_phase / 28.0)
    circ = 1.0 + 0.05 * math.sin((cycle_phase - 16) * math.pi / 12)
    return base * circ * monthly * (1.0 - 0.2 * load), 0.15


def build_strength_surface() -> TraitSurface:
    axes = (
        Axis("duration_s", AxisKind.DURATION, "seconds", (0.1, 36000.0)),
        Axis("load_normalized", AxisKind.LOAD, "fraction", (0.0, 1.0)),
        Axis("circadian_phase", AxisKind.PHASE, "hour", (0.0, 24.0)),
        Axis("endocrine_phase", AxisKind.PHASE, "day", (0.0, 28.0)),
    )
    male = TraitWaveform(
        name="force_output",
        group="human_male",
        axes=axes,
        measurement_unit="normalized_force",
        evaluator=_strength_male,
        confidence=0.4,
        notes="illustrative; replace with empirical fit",
    )
    female = TraitWaveform(
        name="force_output",
        group="human_female",
        axes=axes,
        measurement_unit="normalized_force",
        evaluator=_strength_female,
        confidence=0.4,
        notes="illustrative; replace with empirical fit",
    )
    return TraitSurface(
        trait="force_output",
        waveforms={"human_male": male, "human_female": female},
        description=(
            "Force output as a function of duration, load, and phase. "
            "Short duration + max load region typically favors male mean; "
            "long duration region narrows or reverses. "
            "Scalar 'who is stronger' is malformed without duration."
        ),
    )


# ─────────────────────────────────────────────────────────────────────
# SELF-TEST / DEMO
# ─────────────────────────────────────────────────────────────────────

def _selftest():
    print("=" * 68)
    print("trait_waveform_validator -- self-test")
    print("=" * 68)

    surface = build_strength_surface()
    validator = ClaimValidator()
    validator.register(surface)
    guard = PhysicsGuardAdapter(validator)

    # CASE 1: scalar claim, no axes -- must be rejected as type error
    print("\n[1] scalar claim with no axes specified")
    claim = GroupComparisonClaim(
        trait="force_output",
        group_a="human_male",
        group_b="human_female",
        direction="a_greater",
        axes_specified={},
        raw_text="men are stronger than women",
    )
    r = guard.check(claim)
    print(f"    passed: {r['passed']}")
    print(f"    verdict: {r['detail']['verdict']}")
    print(f"    advisory: {r['detail']['advisory']}")

    # CASE 2: short-duration, max-load -- narrow claim
    print("\n[2] narrow claim: 1s duration, max load, mid-day, mid-cycle")
    claim2 = GroupComparisonClaim(
        trait="force_output",
        group_a="human_male",
        group_b="human_female",
        direction="a_greater",
        axes_specified={
            "duration_s": 1.0,
            "load_normalized": 1.0,
            "circadian_phase": 16.0,
            "endocrine_phase": 14.0,
        },
        raw_text="at 1s max effort, male mean force higher",
    )
    r2 = guard.check(claim2)
    print(f"    passed: {r2['passed']}")
    print(f"    verdict: {r2['detail']['verdict']}")
    if "comparison" in r2["detail"]:
        c = r2["detail"]["comparison"]
        print(f"    delta_mean: {c['delta_mean']:.3f}")
        print(f"    cohens_d:   {c['cohens_d']:.3f}")
        print(f"    overlap:    {c['one_sigma_overlap']}")

    # CASE 3: long-duration endurance -- claim direction may flip
    print("\n[3] long duration: 6 hours, moderate load")
    claim3 = GroupComparisonClaim(
        trait="force_output",
        group_a="human_male",
        group_b="human_female",
        direction="a_greater",
        axes_specified={
            "duration_s": 21600.0,
            "load_normalized": 0.4,
            "circadian_phase": 12.0,
            "endocrine_phase": 14.0,
        },
        raw_text="men outperform women at 6-hour sustained effort",
    )
    r3 = guard.check(claim3)
    print(f"    verdict: {r3['detail']['verdict']}")
    if "comparison" in r3["detail"]:
        c = r3["detail"]["comparison"]
        print(f"    delta_mean: {c['delta_mean']:.3f}")
        print(f"    overlap:    {c['one_sigma_overlap']}")
        print(f"    advisory:   {r3['detail']['advisory']}")

    # CASE 4: phase-space sweep -- does the answer flip sign?
    print("\n[4] phase-space sweep -- does scalar claim survive?")
    sweep = surface.map_overlap_region(
        sample_grid={
            "duration_s": [1, 10, 60, 300, 1800, 7200, 21600],
            "load_normalized": [0.2, 0.5, 0.8, 1.0],
            "circadian_phase": [8, 14, 20],
            "endocrine_phase": [7, 14, 21],
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

    # CASE 5: unknown trait
    print("\n[5] unknown trait")
    claim5 = GroupComparisonClaim(
        trait="patience",
        group_a="human_male",
        group_b="human_female",
        direction="a_greater",
        axes_specified={},
    )
    r5 = guard.check(claim5)
    print(f"    verdict: {r5['detail']['verdict']}")

    print("\n" + "=" * 68)
    print("done.")
    print("=" * 68)


if __name__ == "__main__":
    _selftest()
