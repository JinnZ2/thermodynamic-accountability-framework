"""
investment_distribution/interface.py

Interface-stub for the distributional decomposition of capital
holdings and regeneration-cost liability. See
investment_distribution/README.md for the literature grounding
(DINA, HANK, stratification economics, incidence, Piketty r > g)
and the integration path with metabolic-accounting.

STATUS: pre-1.0, interface only. Shares the StratificationAxis enum
with money_distribution (imported from the shared contract at
schemas/distributional_contract.py once that is populated; for now
duplicated here to keep the two directories importable in isolation
during the pre-1.0 interface stabilization).

License: CC0 1.0 Universal. Stdlib only.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple

# Re-exported for convenience so this module is importable standalone.
# Once schemas/distributional_contract.py is the canonical home, this
# file will import from there instead.
import sys
import pathlib
_MONEY_DIR = pathlib.Path(__file__).resolve().parent.parent / "money_distribution"
sys.path.insert(0, str(_MONEY_DIR))
from interface import StratificationAxis   # noqa: E402


# ---------------------------------------------------------------
# INVESTMENT HOLDINGS: who holds capital, who maintains it,
# who captures returns
# ---------------------------------------------------------------

@dataclass(frozen=True)
class InvestmentStratumHolding:
    """One stratum's position in the capital ownership table.

    Three quantities that CLASSICAL accountability keeps aligned on
    the same stratum and that PARASITIC extraction drives apart:

        capital_share            -- fraction of capital legally held
        maintenance_burden_share -- fraction of regeneration cost
                                    physically borne by this stratum
                                    (labor hours + currency paid)
        return_share             -- fraction of capital returns
                                    captured by this stratum
    """
    axis: StratificationAxis
    label: str
    capital_share: float                  # 0-1
    maintenance_burden_share: float       # 0-1
    return_share: float                   # 0-1
    labor_hours_contributed: Optional[float] = None   # absolute, hours
    currency_paid: Optional[float] = None              # absolute, currency
    population_share: Optional[float] = None           # 0-1


@dataclass(frozen=True)
class InvestmentHoldings:
    """Full capital-ownership decomposition for one period.

    Invariants:
        sum(h.capital_share)            == 1.0  on each axis
        sum(h.maintenance_burden_share) == 1.0  on each axis (modulo
                                                the externalized_to_basin
                                                residual; see below)
        sum(h.return_share)             == 1.0  on each axis
    """
    total_capital: float                  # currency
    holdings: Tuple[InvestmentStratumHolding, ...]
    accounting_period: str = ""
    currency_unit: str = "USD"
    # Part of the maintenance burden that no stratum paid -- the basin
    # absorbed it as drawdown. Ties to metabolic-accounting's
    # GlucoseFlow.environment_loss. When externalized_to_basin_share
    # is > 0, the sum of maintenance_burden_share across strata is
    # < 1.0 by exactly this residual.
    externalized_to_basin_share: float = 0.0
    notes: str = ""

    def axes_present(self) -> Tuple[StratificationAxis, ...]:
        return tuple(sorted({h.axis for h in self.holdings},
                            key=lambda a: a.value))

    def holdings_for_axis(
        self, axis: StratificationAxis
    ) -> Tuple[InvestmentStratumHolding, ...]:
        return tuple(h for h in self.holdings if h.axis == axis)

    def closure_ok(self, tolerance: float = 1e-6) -> bool:
        """All three shares close to 1.0 on each axis (maintenance
        closes to 1.0 minus externalized_to_basin_share)."""
        for axis in self.axes_present():
            items = self.holdings_for_axis(axis)
            if abs(sum(h.capital_share for h in items) - 1.0) > tolerance:
                return False
            if abs(sum(h.return_share for h in items) - 1.0) > tolerance:
                return False
            expected_maint = 1.0 - self.externalized_to_basin_share
            if abs(sum(h.maintenance_burden_share for h in items)
                   - expected_maint) > tolerance:
                return False
        return True


# ---------------------------------------------------------------
# REGENERATION COST DISTRIBUTION
# ---------------------------------------------------------------

@dataclass(frozen=True)
class RegenerationCostBreakdown:
    """Per-stratum regeneration cost, split by payment mode.

    The total regeneration cost required by the basins equals:
        sum(currency_paid + labor_cost_equivalent) + externalized_to_basin

    When externalized_to_basin > 0, the firm's reported profit is
    overstated relative to metabolic profit by exactly that amount
    (per metabolic-accounting GlucoseFlow semantics). This module
    exposes WHO among the strata paid what.
    """
    axis: StratificationAxis
    label: str
    currency_paid: float                  # absolute, currency units
    labor_hours_contributed: float        # absolute, hours
    labor_cost_equivalent: float          # currency-equivalent of the
                                          # labor hours at caller-supplied
                                          # rate
    population_share: Optional[float] = None


# ---------------------------------------------------------------
# CAPITAL INCIDENCE RESULT
# ---------------------------------------------------------------

@dataclass(frozen=True)
class CapitalIncidenceResult:
    """Three-way divergence: legal ownership vs maintenance burden
    vs returns captured.

    Interpretation:
        max_divergence == 0.0  -- classical accountability: one
                                  stratum holds, maintains, captures
        max_divergence > 0.1   -- meaningful parasitic flow
        max_divergence > 0.3   -- severe; substrate_audit would
                                  return CHURCH-verdict on this system
    """
    holdings: InvestmentHoldings
    per_stratum_divergences: Tuple[Tuple[StratificationAxis, str,
                                         float, float, float], ...]
    # each tuple: (axis, label, ownership_vs_maintenance_delta,
    #              ownership_vs_return_delta,
    #              maintenance_vs_return_delta)
    max_divergence: float
    notes: str = ""


def compute_capital_incidence(
    holdings: InvestmentHoldings,
) -> CapitalIncidenceResult:
    """Compute the three-way divergence per stratum."""
    deltas = []
    max_abs = 0.0
    for h in holdings.holdings:
        own_maint = h.capital_share - h.maintenance_burden_share
        own_return = h.capital_share - h.return_share
        maint_return = h.maintenance_burden_share - h.return_share
        deltas.append((h.axis, h.label, own_maint, own_return, maint_return))
        for v in (own_maint, own_return, maint_return):
            if abs(v) > max_abs:
                max_abs = abs(v)

    notes = ""
    if holdings.externalized_to_basin_share > 0:
        notes = (f"Basin absorbs {holdings.externalized_to_basin_share:.1%} "
                 "of maintenance; ties to metabolic-accounting "
                 "GlucoseFlow.environment_loss.")

    return CapitalIncidenceResult(
        holdings=holdings,
        per_stratum_divergences=tuple(deltas),
        max_divergence=round(max_abs, 4),
        notes=notes,
    )


# ---------------------------------------------------------------
# SELF-TEST
# ---------------------------------------------------------------

if __name__ == "__main__":
    # Classical accountability: capital, maintenance, and returns all
    # aligned on the owner-operator stratum.
    aligned = InvestmentHoldings(
        total_capital=1_000_000.0,
        holdings=(
            InvestmentStratumHolding(
                axis=StratificationAxis.PERCENTILE,
                label="owner_operator",
                capital_share=1.0,
                maintenance_burden_share=1.0,
                return_share=1.0,
            ),
        ),
    )

    # Parasitic structure: top holds capital and captures returns;
    # labor bears maintenance; basin absorbs the rest.
    parasitic = InvestmentHoldings(
        total_capital=1_000_000.0,
        holdings=(
            InvestmentStratumHolding(
                axis=StratificationAxis.PERCENTILE,
                label="top_1pct",
                capital_share=0.90,
                maintenance_burden_share=0.05,
                return_share=0.85,
            ),
            InvestmentStratumHolding(
                axis=StratificationAxis.PERCENTILE,
                label="bottom_99pct",
                capital_share=0.10,
                maintenance_burden_share=0.80,
                return_share=0.15,
            ),
        ),
        externalized_to_basin_share=0.15,
    )

    for label, h in [("aligned", aligned), ("parasitic", parasitic)]:
        print(f"--- {label} ---")
        print(f"  closure_ok: {h.closure_ok()}")
        r = compute_capital_incidence(h)
        print(f"  max_divergence: {r.max_divergence}")
        if r.notes:
            print(f"  note: {r.notes}")
