"""
money_distribution/interface.py

Interface-stub for the distributional decomposition of the Money
Equation's per-receiver term p_i. See money_distribution/README.md
for the literature grounding (DINA, HANK, stratification economics,
incidence analysis) and the integration path with
metabolic-accounting.

STATUS: pre-1.0, interface only. No empirical data pipelines, no
HANK elasticity models, no policy simulation. Types and shapes are
declared so metabolic-accounting and other consumers can depend on
them via schemas/distributional_contract.py while the implementation
grows.

License: CC0 1.0 Universal. Stdlib only.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Tuple


# ---------------------------------------------------------------
# STRATIFICATION AXES
# ---------------------------------------------------------------
#
# Per stratification economics (Darity, Hamilton), stratification is
# multi-axis and NOT reducible to a single scalar. The module accepts
# a list of axes and returns an independent decomposition per-axis.
# A consumer that collapses the vector to a scalar (Gini, Theil,
# decile ratio) is making a policy choice, not reading a fact --
# consistent with metabolic-accounting invariant 6
# (tier-vector preservation).

class StratificationAxis(Enum):
    PERCENTILE = "percentile"                   # DINA-standard percentiles
    WEALTH_QUANTILE = "wealth_quantile"         # wealth rather than income
    IDENTITY_STRATUM = "identity_stratum"       # stratification-economics
                                                # (race/ethnicity/gender/...)
    GEOGRAPHIC_REGION = "geographic_region"     # regional / urban-rural
    INTERGENERATIONAL = "intergenerational"     # cohort by birth year
    EMPLOYMENT_CATEGORY = "employment_category" # HANK-style: hand-to-mouth,
                                                # wealthy-hand-to-mouth,
                                                # non-hand-to-mouth


# ---------------------------------------------------------------
# STRATUM SHARE
# ---------------------------------------------------------------

@dataclass(frozen=True)
class StratumShare:
    """One stratum's share of total money flow M.

    Legal-claim vs physical-delivery divergence is the whole point:
    `money_share` is what the stratum RECEIVES as monetary claim;
    `energy_delivered` is what the stratum ACTUALLY CONSUMES in
    physical terms (joules of work performed, food, shelter, etc.).
    When the two diverge, parasitic extraction is occurring.

    Fields:
        axis                which stratification axis this share lives on
        label               stratum identifier (e.g. "top_1pct",
                            "bottom_50pct", "US_South_rural"). Format
                            is stratification-scheme-specific; TAF
                            does not enforce.
        money_share         fraction of total M this stratum received,
                            in [0.0, 1.0]
        energy_delivered    joules delivered to this stratum in the
                            accounting period (>= 0). Null when
                            energy-side data is not available.
        hand_to_mouth_fraction
                            HANK-style: fraction of the stratum that
                            consumes near-all receipts in-period
                            versus accumulating as wealth. In [0, 1],
                            or None when unknown.
        population_share    fraction of total population in this
                            stratum, in [0.0, 1.0]. Used to compute
                            per-capita views.
    """
    axis: StratificationAxis
    label: str
    money_share: float
    energy_delivered: Optional[float] = None       # joules
    hand_to_mouth_fraction: Optional[float] = None  # 0-1
    population_share: Optional[float] = None        # 0-1


# ---------------------------------------------------------------
# MONEY FLOW DISTRIBUTION
# ---------------------------------------------------------------

@dataclass(frozen=True)
class MoneyFlowDistribution:
    """Full decomposition of a single period's money flow across strata.

    Invariants (DINA-style closure):
        sum(s.money_share for s in strata if s.axis == A) == 1.0
          for each axis A that appears in strata (modulo tolerance).
        Each money_share in [0.0, 1.0].

    The closure_ok() method checks these. Consumers should call it
    before trusting the distribution.
    """
    total_M: float                           # currency units
    strata: Tuple[StratumShare, ...]         # per-stratum breakdown
    accounting_period: str = ""              # free-form label
    currency_unit: str = "USD"
    notes: str = ""

    def axes_present(self) -> Tuple[StratificationAxis, ...]:
        return tuple(sorted({s.axis for s in self.strata},
                            key=lambda a: a.value))

    def shares_for_axis(
        self, axis: StratificationAxis
    ) -> Tuple[StratumShare, ...]:
        return tuple(s for s in self.strata if s.axis == axis)

    def closure_ok(self, tolerance: float = 1e-6) -> bool:
        """DINA-style check: shares on each axis sum to 1.0."""
        for axis in self.axes_present():
            total = sum(s.money_share for s in self.shares_for_axis(axis))
            if abs(total - 1.0) > tolerance:
                return False
        return True

    def range_ok(self) -> bool:
        """Every money_share must be in [0.0, 1.0]."""
        return all(0.0 <= s.money_share <= 1.0 for s in self.strata)


# ---------------------------------------------------------------
# INCIDENCE RESULT
# ---------------------------------------------------------------

@dataclass(frozen=True)
class StratumIncidenceDivergence:
    """Per-stratum comparison of legal vs physical incidence."""
    axis: StratificationAxis
    label: str
    legal_share: float           # from legal-claim distribution
    physical_share: float        # from energy-delivered distribution
    divergence: float            # legal_share - physical_share
    # Positive divergence = stratum receives MORE monetary claim than
    # physical delivery warrants (parasitic gain). Negative = stratum
    # receives LESS monetary claim than physical delivery warrants
    # (parasitic loss bearer).


@dataclass(frozen=True)
class IncidenceResult:
    """Legal vs physical incidence comparison.

    The central insight: in a physics-grounded accounting system the
    legal incidence (who gets paid) and physical incidence (who
    receives energy delivery) should coincide. When they drift apart,
    parasitic extraction is occurring and the delta quantifies it.

    Interpretation:
        divergence_max == 0.0 -- no parasitic extraction
        divergence_max > 0.1  -- meaningful parasitic flow
        divergence_max > 0.3  -- severe; consumer should flag
    """
    legal_incidence: MoneyFlowDistribution
    physical_incidence: MoneyFlowDistribution
    divergences: Tuple[StratumIncidenceDivergence, ...]
    divergence_max: float        # max abs(divergence) across strata
    notes: str = ""


# ---------------------------------------------------------------
# STUBS FOR DOWNSTREAM ENTRY POINTS
# ---------------------------------------------------------------

def compute_incidence(
    legal: MoneyFlowDistribution,
    physical: MoneyFlowDistribution,
) -> IncidenceResult:
    """Skeletal implementation: align strata by (axis, label) and
    compute per-stratum divergence.

    Both distributions must cover the same axes+labels; mismatched
    labels are dropped from the comparison with a note.
    """
    legal_map = {(s.axis, s.label): s.money_share for s in legal.strata}
    phys_map = {(s.axis, s.label): s.money_share for s in physical.strata}

    divergences: List[StratumIncidenceDivergence] = []
    dropped: List[str] = []
    for key in sorted(set(legal_map) | set(phys_map)):
        if key in legal_map and key in phys_map:
            delta = legal_map[key] - phys_map[key]
            axis, label = key
            divergences.append(StratumIncidenceDivergence(
                axis=axis, label=label,
                legal_share=legal_map[key],
                physical_share=phys_map[key],
                divergence=delta,
            ))
        else:
            dropped.append(f"{key[0].value}:{key[1]}")

    divergence_max = (
        max((abs(d.divergence) for d in divergences), default=0.0)
    )
    notes = ""
    if dropped:
        notes = f"Dropped unmatched strata: {dropped}"

    return IncidenceResult(
        legal_incidence=legal,
        physical_incidence=physical,
        divergences=tuple(divergences),
        divergence_max=divergence_max,
        notes=notes,
    )


# ---------------------------------------------------------------
# SELF-TEST
# ---------------------------------------------------------------

if __name__ == "__main__":
    # Construct a minimal two-stratum distribution to verify shapes.
    legal = MoneyFlowDistribution(
        total_M=1_000_000.0,
        strata=(
            StratumShare(
                axis=StratificationAxis.PERCENTILE,
                label="top_1pct",
                money_share=0.40,
            ),
            StratumShare(
                axis=StratificationAxis.PERCENTILE,
                label="bottom_99pct",
                money_share=0.60,
            ),
        ),
        accounting_period="2024",
    )
    physical = MoneyFlowDistribution(
        total_M=1_000_000.0,
        strata=(
            StratumShare(
                axis=StratificationAxis.PERCENTILE,
                label="top_1pct",
                money_share=0.10,
                energy_delivered=1e9,
            ),
            StratumShare(
                axis=StratificationAxis.PERCENTILE,
                label="bottom_99pct",
                money_share=0.90,
                energy_delivered=9e9,
            ),
        ),
        accounting_period="2024",
    )

    print(f"legal closure_ok:    {legal.closure_ok()}")
    print(f"physical closure_ok: {physical.closure_ok()}")
    print(f"legal range_ok:      {legal.range_ok()}")

    result = compute_incidence(legal, physical)
    print(f"divergence_max:      {result.divergence_max:.3f}")
    for d in result.divergences:
        print(f"  {d.label:15s} legal={d.legal_share:.2f}  "
              f"physical={d.physical_share:.2f}  "
              f"divergence={d.divergence:+.3f}")
