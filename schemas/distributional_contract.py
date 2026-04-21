"""
Distributional Contract -- stable surface for the distributional
decomposition of money flows and capital holdings.

This is TAF's downstream-facing contract for consumers (primarily
metabolic-accounting) that need to import TAF's distributional
shapes without depending on the implementation modules in
money_distribution/ and investment_distribution/ as they evolve
pre-1.0.

UPSTREAM: this repository (TAF itself).
CONSUMERS: metabolic-accounting/distributional/, plus any other
sister repo that wants to decompose a total along stratification
axes in a way that closes (DINA-style) and preserves vector
structure (per stratification economics).

Versioning:
    CONTRACT_VERSION 0.1.0 -- pre-1.0 interface stub. Breaking
    changes expected until the implementation settles.

    When the interface stabilizes, this file becomes the stable
    re-export point and money_distribution/interface.py +
    investment_distribution/interface.py import from here.
    Until then, the dataclass shapes here are mirrored duplicates
    of what those modules declare.

Dependencies: stdlib only (dataclasses, enum, typing).
License: CC0 1.0 Universal.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple


CONTRACT_VERSION = "0.1.0"
UPSTREAM = "github.com/JinnZ2/thermodynamic-accountability-framework"
UPSTREAM_DIRS = ("money_distribution/", "investment_distribution/")


# ---------------------------------------------------------------
# STRATIFICATION AXES (shared between money + investment)
# ---------------------------------------------------------------

class StratificationAxis(Enum):
    PERCENTILE = "percentile"
    WEALTH_QUANTILE = "wealth_quantile"
    IDENTITY_STRATUM = "identity_stratum"
    GEOGRAPHIC_REGION = "geographic_region"
    INTERGENERATIONAL = "intergenerational"
    EMPLOYMENT_CATEGORY = "employment_category"


# ---------------------------------------------------------------
# MONEY FLOW SIDE (from money_distribution/)
# ---------------------------------------------------------------

@dataclass(frozen=True)
class StratumShare:
    axis: StratificationAxis
    label: str
    money_share: float
    energy_delivered: Optional[float] = None
    hand_to_mouth_fraction: Optional[float] = None
    population_share: Optional[float] = None


@dataclass(frozen=True)
class MoneyFlowDistribution:
    total_M: float
    strata: Tuple[StratumShare, ...]
    accounting_period: str = ""
    currency_unit: str = "USD"
    notes: str = ""


@dataclass(frozen=True)
class StratumIncidenceDivergence:
    axis: StratificationAxis
    label: str
    legal_share: float
    physical_share: float
    divergence: float


@dataclass(frozen=True)
class IncidenceResult:
    legal_incidence: MoneyFlowDistribution
    physical_incidence: MoneyFlowDistribution
    divergences: Tuple[StratumIncidenceDivergence, ...]
    divergence_max: float
    notes: str = ""


# ---------------------------------------------------------------
# CAPITAL HOLDINGS SIDE (from investment_distribution/)
# ---------------------------------------------------------------

@dataclass(frozen=True)
class InvestmentStratumHolding:
    axis: StratificationAxis
    label: str
    capital_share: float
    maintenance_burden_share: float
    return_share: float
    labor_hours_contributed: Optional[float] = None
    currency_paid: Optional[float] = None
    population_share: Optional[float] = None


@dataclass(frozen=True)
class InvestmentHoldings:
    total_capital: float
    holdings: Tuple[InvestmentStratumHolding, ...]
    accounting_period: str = ""
    currency_unit: str = "USD"
    externalized_to_basin_share: float = 0.0
    notes: str = ""


@dataclass(frozen=True)
class CapitalIncidenceResult:
    holdings: InvestmentHoldings
    per_stratum_divergences: Tuple[Tuple[StratificationAxis, str,
                                         float, float, float], ...]
    max_divergence: float
    notes: str = ""


# ---------------------------------------------------------------
# INTEGRATION WITH METABOLIC-ACCOUNTING
# ---------------------------------------------------------------
#
# Intended handoff shapes. Both sides agree on the point at which
# data crosses the repo boundary.
#
# metabolic-accounting -> TAF:
#   GlucoseFlow.regeneration_required (currency; firm total)
#   GlucoseFlow.environment_loss      (xdu; basin residual)
#   Verdict.sustainable_yield_signal  (GREEN/AMBER/RED/BLACK)
#   per-stratum population and labor-hours data (caller-supplied;
#   metabolic-accounting does not publish it as a contract shape yet)
#
# TAF -> metabolic-accounting:
#   MoneyFlowDistribution + IncidenceResult       (from money_distribution)
#   InvestmentHoldings + CapitalIncidenceResult   (from investment_distribution)
#
# metabolic-accounting then ties these to its BasinState projections
# to produce per-stratum time_to_red values.

HANDOFF_MAP = {
    "inputs_from_metabolic": [
        "GlucoseFlow.regeneration_required",
        "GlucoseFlow.environment_loss",
        "Verdict.sustainable_yield_signal",
        "per-stratum population (caller-supplied)",
        "per-stratum labor hours (caller-supplied)",
    ],
    "outputs_to_metabolic": [
        "MoneyFlowDistribution (flow decomposition)",
        "IncidenceResult (legal vs physical incidence divergence)",
        "InvestmentHoldings (capital + maintenance + return per stratum)",
        "CapitalIncidenceResult (three-way divergence)",
    ],
}


# ---------------------------------------------------------------
# SELF-TEST
# ---------------------------------------------------------------

if __name__ == "__main__":
    print(f"Distributional contract version: {CONTRACT_VERSION}")
    print(f"Upstream: {UPSTREAM}")
    print(f"Implementation dirs: {UPSTREAM_DIRS}")
    print()
    print("Inputs expected from metabolic-accounting:")
    for item in HANDOFF_MAP["inputs_from_metabolic"]:
        print(f"  - {item}")
    print()
    print("Outputs TAF provides back:")
    for item in HANDOFF_MAP["outputs_to_metabolic"]:
        print(f"  - {item}")
    print()

    # Shape smoke test
    share = StratumShare(
        axis=StratificationAxis.PERCENTILE,
        label="top_1pct",
        money_share=0.40,
    )
    dist = MoneyFlowDistribution(total_M=1.0, strata=(share,))
    holding = InvestmentStratumHolding(
        axis=StratificationAxis.PERCENTILE,
        label="top_1pct",
        capital_share=0.9,
        maintenance_burden_share=0.05,
        return_share=0.85,
    )
    holdings = InvestmentHoldings(total_capital=1.0, holdings=(holding,))

    assert share.money_share == 0.40
    assert holdings.total_capital == 1.0
    assert StratificationAxis.PERCENTILE.value == "percentile"
    print("Shape smoke test: OK")
