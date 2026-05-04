"""
Metabolic-Accounting Contract -- stable surface of the 4 canonical
dataclasses and 7 invariants declared in metabolic-accounting's
docs/SCHEMAS.md.

This module mirrors what the upstream has declared as canonical:
    - ExergyFlow    (thermodynamics/exergy.py) -- atomic ledger
    - GlucoseFlow   (accounting/glucose.py)    -- periodic P&L
    - BasinState    (basin_states/base.py)     -- ecosystem reserves
    - Verdict       (verdict/assess.py)        -- judgment summary

Plus the 7 numbered invariants, which SCHEMAS.md explicitly frames as
the stable contract (rather than individual field definitions, which
may grow non-breaking additions).

UPSTREAM PIN
------------
    metabolic_accounting_ref:         https://github.com/JinnZ2/metabolic-accounting
    metabolic_accounting_commit_sha:  09382a66ce6ee63d84038c8ee35a1fbc28cda58d
    metabolic_accounting_schema_doc:  docs/SCHEMAS.md

Upstream does NOT currently declare a version string or surface tag.
This mirror is pinned to a specific commit SHA. When upstream either
(a) moves main forward with schema-affecting changes, or (b) adopts a
SURFACE.md + CONTRACT_VERSION pattern like Mathematic-economics and
Logic-Ferret, bump CONTRACT_VERSION here and update the SHA (or the
tag once one exists).

CONTRACT_VERSION 0.1.0 reflects upstream's pre-release status
(98 commits, 0 releases at the time of mirroring).

Dependencies: stdlib only (dataclasses, enum, typing).
License: CC0 1.0 Universal (matches upstream).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple


CONTRACT_VERSION = "0.1.0"
UPSTREAM = "github.com/JinnZ2/metabolic-accounting"
UPSTREAM_COMMIT_SHA = "09382a66ce6ee63d84038c8ee35a1fbc28cda58d"
UPSTREAM_SCHEMA_DOC = (
    "https://github.com/JinnZ2/metabolic-accounting/blob/"
    "09382a66ce6ee63d84038c8ee35a1fbc28cda58d/docs/SCHEMAS.md"
)


# ---------------------------------------------------------------
# ENUMS
# ---------------------------------------------------------------

class SustainableYieldSignal(Enum):
    """Verdict.sustainable_yield_signal values.

    Ordering: GREEN < AMBER < RED < BLACK. BLACK is reserved for
    irreversibility and is NOT "very RED" -- consumers must treat it
    as a distinct state per invariant 4.
    """
    GREEN = "GREEN"
    AMBER = "AMBER"
    RED = "RED"
    BLACK = "BLACK"


class BasinTrajectory(Enum):
    """Verdict.basin_trajectory values."""
    IMPROVING = "IMPROVING"
    STABLE = "STABLE"
    DEGRADING = "DEGRADING"


# ---------------------------------------------------------------
# DATACLASS 1/4: ExergyFlow
# ---------------------------------------------------------------

@dataclass(frozen=True)
class ExergyFlow:
    """Atomic ledger entry at the thermodynamic layer.

    Fields (all mirrored verbatim from SCHEMAS.md):
        source     str   free-form identifier, e.g. "air.particulate_load"
        sink       str   free-form identifier, e.g. "landscape_reserve"
        amount     float xdu; positive -> source loses, sink gains
        destroyed  float xdu; >= 0 ALWAYS (invariant 1, Gouy-Stodola)
        note       str   human-readable context

    Unit: xdu (exergy-destruction-equivalent). NOT currency. See
    invariant 7.
    """
    source: str
    sink: str
    amount: float
    destroyed: float
    note: str = ""

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "ExergyFlow":
        return cls(
            source=str(d["source"]),
            sink=str(d["sink"]),
            amount=float(d["amount"]),
            destroyed=float(d["destroyed"]),
            note=str(d.get("note", "")),
        )


# ---------------------------------------------------------------
# SUPPORTING SHAPES
# ---------------------------------------------------------------

@dataclass(frozen=True)
class RegenCost:
    """Per-metric regeneration cost breakdown.

    Referenced in GlucoseFlow.regen_breakdown. Upstream docs do not
    give a complete field list; we mirror the two fields that drive
    invariant 4 (irreversibility propagation). Additional fields on
    upstream are tolerated and pass through as `extra`.
    """
    total_cost: float
    irreversible: bool = False
    extra: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "RegenCost":
        known = {"total_cost", "irreversible"}
        extra = {k: v for k, v in d.items() if k not in known}
        return cls(
            total_cost=float(d.get("total_cost", 0.0)),
            irreversible=bool(d.get("irreversible", False)),
            extra=extra,
        )


# ---------------------------------------------------------------
# DATACLASS 2/4: GlucoseFlow
# ---------------------------------------------------------------

@dataclass(frozen=True)
class GlucoseFlow:
    """Periodic P&L statement at the accounting layer.

    Mirrors all 14 fields declared in SCHEMAS.md. Currency fields
    and xdu fields are NOT interchangeable per invariant 7.

    Note on `math.inf`: regeneration_required, regeneration_debt, and
    related currency fields may legitimately be `math.inf` when
    irreversibility has propagated (invariant 4). Consumers must NOT
    clamp or substitute these.
    """
    revenue: float
    direct_operating_cost: float
    regeneration_paid: float
    regeneration_required: float                  # currency; may be math.inf
    cascade_burn: float
    regeneration_debt: float                       # currency; may be math.inf
    reserve_drawdown_cost: float                   # xdu
    environment_loss: float                        # xdu
    cumulative_environment_loss: float             # xdu
    exhausted_reserves: Tuple[Tuple[str, str], ...] = ()
    tertiary_past_cliff: Tuple[str, ...] = ()
    irreversible_metrics: Tuple[str, ...] = ()
    regen_breakdown: Tuple[RegenCost, ...] = ()
    registry_warnings: Tuple[str, ...] = ()

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "GlucoseFlow":
        return cls(
            revenue=float(d["revenue"]),
            direct_operating_cost=float(d["direct_operating_cost"]),
            regeneration_paid=float(d["regeneration_paid"]),
            regeneration_required=float(d["regeneration_required"]),
            cascade_burn=float(d["cascade_burn"]),
            regeneration_debt=float(d["regeneration_debt"]),
            reserve_drawdown_cost=float(d["reserve_drawdown_cost"]),
            environment_loss=float(d["environment_loss"]),
            cumulative_environment_loss=float(d["cumulative_environment_loss"]),
            exhausted_reserves=tuple(
                tuple(p) for p in d.get("exhausted_reserves", ())
            ),
            tertiary_past_cliff=tuple(d.get("tertiary_past_cliff", ())),
            irreversible_metrics=tuple(d.get("irreversible_metrics", ())),
            regen_breakdown=tuple(
                RegenCost.from_dict(r) if isinstance(r, dict) else r
                for r in d.get("regen_breakdown", ())
            ),
            registry_warnings=tuple(d.get("registry_warnings", ())),
        )


# ---------------------------------------------------------------
# DATACLASS 3/4: BasinState
# ---------------------------------------------------------------

@dataclass(frozen=True)
class BasinState:
    """Ecosystem reserve snapshot for one basin.

    The `basin_type` field uses a normalized enum upstream
    (soil/air/water/biology/community) but is declared as str for
    forward compatibility. Consumers should not rely on the string
    being an enum value.

    `high_is_bad` is the set of metric names where crossing ABOVE the
    cliff is the failure condition (e.g. contamination metrics); the
    default is BELOW for depletion metrics.
    """
    name: str
    basin_type: str
    state: Dict[str, float] = field(default_factory=dict)
    capacity: Dict[str, float] = field(default_factory=dict)
    trajectory: Dict[str, float] = field(default_factory=dict)
    cliff_thresholds: Dict[str, float] = field(default_factory=dict)
    high_is_bad: Set[str] = field(default_factory=set)
    last_updated: Optional[str] = None
    notes: str = ""

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "BasinState":
        return cls(
            name=str(d["name"]),
            basin_type=str(d["basin_type"]),
            state=dict(d.get("state", {})),
            capacity=dict(d.get("capacity", {})),
            trajectory=dict(d.get("trajectory", {})),
            cliff_thresholds=dict(d.get("cliff_thresholds", {})),
            high_is_bad=set(d.get("high_is_bad", ())),
            last_updated=d.get("last_updated"),
            notes=str(d.get("notes", "")),
        )


# ---------------------------------------------------------------
# DATACLASS 4/4: Verdict
# ---------------------------------------------------------------

@dataclass(frozen=True)
class Verdict:
    """Judgment summary at the top layer.

    Per SCHEMAS.md: "the two profit lines are deliberate. A companion
    tool should never collapse them into one number." Consumers must
    preserve both `reported_profit` and `metabolic_profit` separately.

    BLACK is the only sustainable_yield_signal that means
    irreversibility; treating it as "very RED" is wrong (invariant 4).
    """
    sustainable_yield_signal: SustainableYieldSignal
    basin_trajectory: BasinTrajectory
    time_to_red: Optional[float]                # periods; None = no red
    forced_drawdown: float                       # currency; may be math.inf
    regeneration_debt: float                     # currency; may be math.inf
    metabolic_profit: float                      # currency; may be -math.inf
    reported_profit: float
    profit_gap: float                            # reported - metabolic; may be inf
    extraordinary_item_flagged: bool
    extraordinary_item_amount: float             # xdu; == GlucoseFlow.environment_loss
    metabolic_profit_with_loss: float
    irreversible_metrics: Tuple[str, ...] = ()
    warnings: Tuple[str, ...] = ()

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Verdict":
        signal = d["sustainable_yield_signal"]
        if isinstance(signal, str):
            signal = SustainableYieldSignal(signal)
        trajectory = d["basin_trajectory"]
        if isinstance(trajectory, str):
            trajectory = BasinTrajectory(trajectory)
        return cls(
            sustainable_yield_signal=signal,
            basin_trajectory=trajectory,
            time_to_red=(None if d.get("time_to_red") is None
                         else float(d["time_to_red"])),
            forced_drawdown=float(d["forced_drawdown"]),
            regeneration_debt=float(d["regeneration_debt"]),
            metabolic_profit=float(d["metabolic_profit"]),
            reported_profit=float(d["reported_profit"]),
            profit_gap=float(d["profit_gap"]),
            extraordinary_item_flagged=bool(d["extraordinary_item_flagged"]),
            extraordinary_item_amount=float(d["extraordinary_item_amount"]),
            metabolic_profit_with_loss=float(d["metabolic_profit_with_loss"]),
            irreversible_metrics=tuple(d.get("irreversible_metrics", ())),
            warnings=tuple(d.get("warnings", ())),
        )


# ---------------------------------------------------------------
# THE 7 INVARIANTS (canonical, verbatim from SCHEMAS.md)
# ---------------------------------------------------------------
#
# SCHEMAS.md frames these as the stable contract (rather than
# individual field definitions). Non-breaking additions to fields
# are tolerated; changes to these invariants require renegotiation.

INVARIANTS: Tuple[Tuple[str, str], ...] = (
    ("gouy_stodola",
     "ExergyFlow.destroyed >= 0 for every flow generated by "
     "Site.step(...)."),
    ("first_law_closure",
     "sum(primary, secondary_kept, tertiary_kept, environment) == "
     "imposed_stress, within a tolerance checked by "
     "thermodynamics/exergy.py::check_closure."),
    ("stock_non_negativity",
     "SecondaryReserve.stock >= 0 and TertiaryPool.stock >= 0 at all "
     "times."),
    ("irreversibility_propagation",
     "If any RegenCost.irreversible == True OR any RegenCost.total_cost "
     "is math.inf, then GlucoseFlow.regeneration_required is math.inf "
     "AND Verdict.sustainable_yield_signal == 'BLACK'."),
    ("cumulative_monotonicity",
     "cumulative_environment_loss is non-decreasing across periods. "
     "It is never reset -- irreversible damage does not 'recover' "
     "just because a later period looks better."),
    ("tier_vector_preservation",
     "TierAssignment.by_basin_type is NOT reducible to overall_tier() "
     "without information loss; any consumer that collapses the "
     "vector is making a policy choice, not reading a fact."),
    ("no_currency_in_physics",
     "Reserve and exergy quantities are xdu. Currency conversion is "
     "declarative (XduConverter), not physical."),
)


# ---------------------------------------------------------------
# INVARIANT VALIDATION
# ---------------------------------------------------------------

@dataclass(frozen=True)
class InvariantCheckResult:
    """Result of running the invariants against a payload."""
    all_passed: bool
    failures: Tuple[str, ...] = ()
    warnings: Tuple[str, ...] = ()
    notes: str = ""


def validate_invariants(
    *,
    exergy_flows: Optional[List[ExergyFlow]] = None,
    glucose_flow: Optional[GlucoseFlow] = None,
    previous_cumulative_loss: Optional[float] = None,
    verdict: Optional[Verdict] = None,
) -> InvariantCheckResult:
    """Check the subset of the 7 invariants that can be enforced on
    decoded payloads.

    Invariants 2 (first-law closure) and 3 (stock non-negativity)
    require access to the upstream's internal reserve state and are
    OUT OF SCOPE for a downstream consumer. They are upstream's
    responsibility to enforce; downstream trusts.

    Invariant 6 (tier-vector preservation) is a consumer-behavior
    constraint, not a data check. Downstream tools enforce it by
    never collapsing TierAssignment to a scalar.

    This function checks:
        1. gouy_stodola
        4. irreversibility_propagation
        5. cumulative_monotonicity (if previous_cumulative_loss given)
        7. no_currency_in_physics (structural -- always holds if the
           contract types are respected)
    """
    failures: List[str] = []
    warnings_out: List[str] = []

    # Invariant 1: Gouy-Stodola
    if exergy_flows:
        bad = [i for i, f in enumerate(exergy_flows) if f.destroyed < 0]
        if bad:
            failures.append(
                f"gouy_stodola: ExergyFlow.destroyed negative at indices "
                f"{bad}"
            )

    # Invariant 4: irreversibility propagation
    if glucose_flow is not None and verdict is not None:
        any_irreversible = bool(glucose_flow.irreversible_metrics) or any(
            (r.irreversible or r.total_cost == float("inf"))
            for r in glucose_flow.regen_breakdown
        )
        if any_irreversible:
            if glucose_flow.regeneration_required != float("inf"):
                failures.append(
                    "irreversibility_propagation: irreversibility "
                    "detected but GlucoseFlow.regeneration_required is "
                    "not math.inf"
                )
            if verdict.sustainable_yield_signal != SustainableYieldSignal.BLACK:
                failures.append(
                    "irreversibility_propagation: irreversibility "
                    "detected but Verdict.sustainable_yield_signal is "
                    f"{verdict.sustainable_yield_signal.value!r}, "
                    "not 'BLACK'"
                )

    # Invariant 5: cumulative monotonicity
    if glucose_flow is not None and previous_cumulative_loss is not None:
        if glucose_flow.cumulative_environment_loss < previous_cumulative_loss:
            failures.append(
                f"cumulative_monotonicity: "
                f"cumulative_environment_loss decreased from "
                f"{previous_cumulative_loss} to "
                f"{glucose_flow.cumulative_environment_loss}"
            )

    # Invariant 7 is structural -- it holds by construction of our
    # types. No runtime check needed; document in warnings if the
    # consumer passed mixed-unit data.

    notes = ("All checkable invariants passed."
             if not failures else
             f"{len(failures)} invariant failure(s). See failures list.")

    return InvariantCheckResult(
        all_passed=not failures,
        failures=tuple(failures),
        warnings=tuple(warnings_out),
        notes=notes,
    )


# ---------------------------------------------------------------
# SELF-TEST
# ---------------------------------------------------------------

if __name__ == "__main__":
    import math
    print(f"Contract mirror version:  {CONTRACT_VERSION}")
    print(f"Upstream:                 {UPSTREAM}")
    print(f"Upstream commit SHA:      {UPSTREAM_COMMIT_SHA}")
    print(f"Invariants declared:      {len(INVARIANTS)}")
    print()

    # Round-trip a well-formed payload
    gf = GlucoseFlow.from_dict({
        "revenue": 1000.0,
        "direct_operating_cost": 600.0,
        "regeneration_paid": 50.0,
        "regeneration_required": 80.0,
        "cascade_burn": 20.0,
        "regeneration_debt": 30.0,
        "reserve_drawdown_cost": 15.0,
        "environment_loss": 0.5,
        "cumulative_environment_loss": 1.2,
        "exhausted_reserves": [("soil", "organic_carbon")],
        "tertiary_past_cliff": [],
        "irreversible_metrics": [],
        "regen_breakdown": [
            {"total_cost": 80.0, "irreversible": False},
        ],
        "registry_warnings": [],
    })

    vd = Verdict.from_dict({
        "sustainable_yield_signal": "AMBER",
        "basin_trajectory": "DEGRADING",
        "time_to_red": 14.0,
        "forced_drawdown": 100.0,
        "regeneration_debt": 30.0,
        "metabolic_profit": 370.73,
        "reported_profit": 399.33,
        "profit_gap": 28.60,
        "extraordinary_item_flagged": True,
        "extraordinary_item_amount": 0.0307,
        "metabolic_profit_with_loss": 370.69,
        "irreversible_metrics": [],
        "warnings": [],
    })

    flows = [
        ExergyFlow.from_dict({
            "source": "air.particulate_load",
            "sink": "landscape_reserve",
            "amount": 5.0,
            "destroyed": 0.3,
            "note": "",
        }),
    ]

    result = validate_invariants(
        exergy_flows=flows,
        glucose_flow=gf,
        previous_cumulative_loss=0.9,
        verdict=vd,
    )
    print(f"Well-formed payload -> all_passed={result.all_passed}")
    print(f"                       {result.notes}")

    # Negative-destruction violation
    bad_flows = [ExergyFlow(
        source="x", sink="y", amount=1.0, destroyed=-0.1, note="")]
    result2 = validate_invariants(exergy_flows=bad_flows)
    print(f"Negative destroyed  -> all_passed={result2.all_passed}")
    print(f"                       failures={list(result2.failures)}")

    # Irreversibility propagation violation
    bad_gf = GlucoseFlow(
        revenue=0, direct_operating_cost=0, regeneration_paid=0,
        regeneration_required=100.0,  # NOT math.inf, but irreversible
        cascade_burn=0, regeneration_debt=0,
        reserve_drawdown_cost=0, environment_loss=0,
        cumulative_environment_loss=0,
        irreversible_metrics=("soil.organic_carbon",),
    )
    ok_vd = Verdict(
        sustainable_yield_signal=SustainableYieldSignal.RED,
        basin_trajectory=BasinTrajectory.DEGRADING,
        time_to_red=0.0, forced_drawdown=0.0, regeneration_debt=0.0,
        metabolic_profit=0.0, reported_profit=0.0, profit_gap=0.0,
        extraordinary_item_flagged=True, extraordinary_item_amount=0.0,
        metabolic_profit_with_loss=0.0,
    )
    result3 = validate_invariants(glucose_flow=bad_gf, verdict=ok_vd)
    print(f"Irreversibility leak -> all_passed={result3.all_passed}")
    for f in result3.failures:
        print(f"                        {f}")

    # Cumulative monotonicity violation
    gf_lower = GlucoseFlow(
        revenue=0, direct_operating_cost=0, regeneration_paid=0,
        regeneration_required=0, cascade_burn=0, regeneration_debt=0,
        reserve_drawdown_cost=0, environment_loss=0,
        cumulative_environment_loss=0.5,  # dropped from 1.2
    )
    result4 = validate_invariants(
        glucose_flow=gf_lower, previous_cumulative_loss=1.2,
    )
    print(f"Monotonicity drop   -> all_passed={result4.all_passed}")
    for f in result4.failures:
        print(f"                        {f}")

    # Regression guards
    assert result.all_passed
    assert not result2.all_passed
    assert not result3.all_passed
    assert not result4.all_passed
    assert len(INVARIANTS) == 7
    print()
    print("Regression guards: OK")
