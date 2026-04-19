"""
Mathematic-Economics Contract -- stable surface of the 13 canonical
equations published by github.com/JinnZ2/Mathematic-economics.

This module mirrors only what the upstream has declared as canonical
and stable: the equation IDs, their formulas as text, their variable
names and units, and the structure of their falsification specs. It
does NOT mirror calibration knobs (thresholds, current_measured_value,
weighting coefficients) -- those change without breaking the contract.

ME's CLAUDE.md is explicit: "the 13 core equations and composite
indices (OSDI) are canonical and must not be altered without explicit
justification." This contract is a declared mirror of those exact 13;
edits here that change semantics should be paired with an upstream
issue.

Versioning:
    CONTRACT_VERSION 1.0.0 = pin against ME at the time of writing.
    Breaking changes to ME's equation list, formulas, or variable
    names bump major. Calibration retunes do NOT bump.

Dependencies: stdlib only (dataclasses, enum, typing).
License: CC0 1.0 Universal (public domain), preserved from upstream.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


CONTRACT_VERSION = "1.0.0"
UPSTREAM = "github.com/JinnZ2/Mathematic-economics"


# ---------------------------------------------------------------
# EQUATION IDs (canonical, fixed)
# ---------------------------------------------------------------

class EquationID(Enum):
    """The 13 canonical equations. Names and order are part of the contract."""
    VE_VL = "VE_VL"      # Value Extraction to Value Labor Ratio
    SID   = "SID"        # Socialist Infrastructure Dependency
    RI    = "RI"         # Risk Inequality
    DI    = "DI"         # Democracy Index
    LWR   = "LWR"        # Labor Wealth Ratio
    MSI   = "MSI"        # Money Socialist Index
    BSC   = "BSC"        # Bailout Socialism Coefficient
    MM    = "MM"         # Money Multiplier
    ISR   = "ISR"        # Infrastructure Subsidy Ratio
    OSDI  = "OSDI"       # Overall Socialist Dependence Index (composite)
    UFR   = "UFR"        # Upward Flow Rate
    ER    = "ER"         # Extraction Rate
    HHI   = "HHI"        # Herfindahl-Hirschman Index
    SD    = "SD"         # Semantic Drift Rate


# ---------------------------------------------------------------
# CORE SHAPES
# ---------------------------------------------------------------

@dataclass(frozen=True)
class DataSource:
    """One data source backing an equation's measurement."""
    name: str           # e.g., "FRED", "BLS"
    series_id: str      # API series identifier (e.g., "PRS85006173")
    api: str = ""       # endpoint or API short name
    notes: str = ""

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "DataSource":
        return cls(
            name=str(d["name"]),
            series_id=str(d.get("series_id", d.get("table", ""))),
            api=str(d.get("api", "")),
            notes=str(d.get("notes", "")),
        )


@dataclass(frozen=True)
class FalsificationSpec:
    """How to refute the measurement."""
    method: str         # human-readable description of the test
    counter_data: str = ""   # what data would refute the claim
    threshold_text: str = "" # natural-language threshold (NOT a calibration knob)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "FalsificationSpec":
        if isinstance(d, str):
            return cls(method=d)
        return cls(
            method=str(d.get("method", "")),
            counter_data=str(d.get("counter_data", "")),
            threshold_text=str(d.get("threshold_text", "")),
        )


@dataclass(frozen=True)
class EquationDef:
    """Stable shape of one equation. Contract surface."""
    id: EquationID
    name: str                       # full title
    formula: str                    # mathematical expression as text
    description: str = ""
    variables: tuple = ()           # ordered tuple of variable names
    units: str = ""                 # output units (free text; "ratio", "rate", etc.)
    data_sources: tuple = ()        # tuple[DataSource, ...]
    falsification: FalsificationSpec = field(
        default_factory=lambda: FalsificationSpec(method="")
    )

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "EquationDef":
        eid = d["id"]
        if isinstance(eid, str):
            eid = EquationID(eid)
        sources = tuple(DataSource.from_dict(s) for s in d.get("data_sources", ()))
        falsification = FalsificationSpec.from_dict(d.get("falsification", {}))
        variables = d.get("variables", ())
        if isinstance(variables, dict):
            variables = tuple(variables.keys())
        else:
            variables = tuple(variables)
        return cls(
            id=eid,
            name=str(d["name"]),
            formula=str(d["formula"]),
            description=str(d.get("description", "")),
            variables=variables,
            units=str(d.get("units", "")),
            data_sources=sources,
            falsification=falsification,
        )


# ---------------------------------------------------------------
# THE 13 CANONICAL EQUATIONS (declared mirror)
# ---------------------------------------------------------------
#
# Formulas verbatim from upstream equations.yaml. Edits here that
# change semantics MUST be paired with an upstream issue. Calibration
# knobs (numeric thresholds, current_measured_value) are deliberately
# absent -- those are not part of the contract.

CANONICAL_EQUATIONS: dict[EquationID, EquationDef] = {
    EquationID.VE_VL: EquationDef(
        id=EquationID.VE_VL,
        name="Value Extraction to Value Labor Ratio",
        formula="VE / VL",
        description="Extracted value (capital returns, rents) divided by "
                    "value created by labor.",
        variables=("VE", "VL"),
        units="ratio",
    ),
    EquationID.SID: EquationDef(
        id=EquationID.SID,
        name="Socialist Infrastructure Dependency",
        formula="C / (C + P)",
        description="Collective infrastructure share of total infrastructure "
                    "use (collective + private).",
        variables=("C", "P"),
        units="fraction 0-1",
    ),
    EquationID.RI: EquationDef(
        id=EquationID.RI,
        name="Risk Inequality",
        formula="(Risk_workers / N_workers) / (Risk_investors / N_investors)",
        description="Per-capita risk burden of workers relative to investors.",
        variables=("Risk_workers", "N_workers", "Risk_investors", "N_investors"),
        units="ratio",
    ),
    EquationID.DI: EquationDef(
        id=EquationID.DI,
        name="Democracy Index",
        formula="Var(P_1, P_2, ..., P_n)  where  P_i = W_i * I_i",
        description="Variance of effective political power across the "
                    "population. P_i is wealth W_i times institutional "
                    "leverage I_i. Higher variance = less democratic.",
        variables=("P_i", "W_i", "I_i"),
        units="variance (lower is more democratic)",
    ),
    EquationID.LWR: EquationDef(
        id=EquationID.LWR,
        name="Labor Wealth Ratio",
        formula="WL / WO",
        description="Wealth held by labor (wage-earner aggregate) divided by "
                    "wealth held by ownership (capital-holder aggregate).",
        variables=("WL", "WO"),
        units="ratio",
    ),
    EquationID.MSI: EquationDef(
        id=EquationID.MSI,
        name="Money Socialist Index",
        formula="government_created_money / total_money_supply",
        description="Fraction of total money supply that originated from "
                    "government issuance (vs commercial-bank credit creation).",
        variables=("government_created_money", "total_money_supply"),
        units="fraction 0-1",
    ),
    EquationID.BSC: EquationDef(
        id=EquationID.BSC,
        name="Bailout Socialism Coefficient",
        formula="government_rescue_funds / private_losses",
        description="Public recapitalization funds delivered to private "
                    "entities, normalized by the private losses incurred.",
        variables=("government_rescue_funds", "private_losses"),
        units="ratio",
    ),
    EquationID.MM: EquationDef(
        id=EquationID.MM,
        name="Money Multiplier",
        formula="1 / reserve_requirement",
        description="Maximum credit-money expansion factor under fractional-"
                    "reserve banking. Higher = more leverage.",
        variables=("reserve_requirement",),
        units="dimensionless multiplier",
    ),
    EquationID.ISR: EquationDef(
        id=EquationID.ISR,
        name="Infrastructure Subsidy Ratio",
        formula="market_value_of_public_infrastructure_used / cost_paid",
        description="Hidden subsidy: market value of public infrastructure "
                    "consumed by a private entity, divided by what they "
                    "actually paid for that use.",
        variables=("market_value_of_public_infrastructure_used", "cost_paid"),
        units="ratio",
    ),
    EquationID.OSDI: EquationDef(
        id=EquationID.OSDI,
        name="Overall Socialist Dependence Index",
        formula="weighted_composite(SID, MSI, ISR, BSC, MM)",
        description="Composite index capturing total dependence of the "
                    "ostensibly-private sector on collective infrastructure, "
                    "money creation, public assets, bailouts, and leverage.",
        variables=("SID", "MSI", "ISR", "BSC", "MM"),
        units="weighted index 0-1",
    ),
    EquationID.UFR: EquationDef(
        id=EquationID.UFR,
        name="Upward Flow Rate",
        formula="d(top_1pct_wealth)/dt / d(bottom_50pct_wealth)/dt",
        description="Time derivative of top-1% wealth divided by time "
                    "derivative of bottom-50% wealth. > 1 = upward "
                    "redistribution outpacing broad accumulation.",
        variables=("top_1pct_wealth", "bottom_50pct_wealth"),
        units="ratio of rates",
    ),
    EquationID.ER: EquationDef(
        id=EquationID.ER,
        name="Extraction Rate",
        formula="(revenue - labor_costs) / revenue",
        description="Fraction of revenue retained after labor compensation.",
        variables=("revenue", "labor_costs"),
        units="fraction 0-1",
    ),
    EquationID.HHI: EquationDef(
        id=EquationID.HHI,
        name="Herfindahl-Hirschman Index",
        formula="sum(market_share_i ** 2)",
        description="Standard market-concentration index. Sum of squared "
                    "market shares (in percent). Higher = more concentrated.",
        variables=("market_share_i",),
        units="index 0-10000 (squared percent)",
    ),
    EquationID.SD: EquationDef(
        id=EquationID.SD,
        name="Semantic Drift Rate",
        formula="|Definition(t2) - Definition(t1)| / (t2 - t1)",
        description="Rate at which a term's empirical referent diverges "
                    "from its earlier referent. Diachronic word-embedding "
                    "distance per unit time.",
        variables=("Definition_t1", "Definition_t2", "t1", "t2"),
        units="distance per unit time",
    ),
}


# ---------------------------------------------------------------
# PAYLOAD ENVELOPE
# ---------------------------------------------------------------

@dataclass(frozen=True)
class EquationMeasurement:
    """A single measured value for one equation at one point in time."""
    equation_id: EquationID
    value: float
    timestamp: str = ""           # ISO-8601 if available, free text otherwise
    measurement_notes: str = ""

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "EquationMeasurement":
        eid = d["equation_id"]
        if isinstance(eid, str):
            eid = EquationID(eid)
        return cls(
            equation_id=eid,
            value=float(d["value"]),
            timestamp=str(d.get("timestamp", "")),
            measurement_notes=str(d.get("measurement_notes", "")),
        )


@dataclass(frozen=True)
class EconomicsPayload:
    """Envelope carrying a measurement bundle from ME for TAF to consume.

    A consumer that imports this contract gets: the canonical equation
    definitions (CANONICAL_EQUATIONS), plus the shape for receiving
    measurements (EquationMeasurement). Calibration thresholds are
    NOT part of the payload -- the consumer applies its own thresholds.
    """
    contract_version: str
    measurements: tuple                   # tuple[EquationMeasurement, ...]
    source_commit: str = ""               # ME commit SHA the measurements came from

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "EconomicsPayload":
        ms = tuple(
            EquationMeasurement.from_dict(m) for m in d.get("measurements", ())
        )
        return cls(
            contract_version=str(d.get("contract_version", "0.0.0")),
            measurements=ms,
            source_commit=str(d.get("source_commit", "")),
        )

    def is_compatible(self, expected_major: int = 1) -> bool:
        """Check major-version compatibility."""
        try:
            major = int(self.contract_version.split(".")[0])
        except (ValueError, IndexError):
            return False
        return major == expected_major

    def lookup(self, equation_id: EquationID) -> "EquationMeasurement | None":
        """Find the most recent measurement for one equation, or None."""
        matches = [m for m in self.measurements if m.equation_id == equation_id]
        if not matches:
            return None
        # Last in the tuple wins (caller is responsible for ordering).
        return matches[-1]


# ---------------------------------------------------------------
# SELF-TEST
# ---------------------------------------------------------------

if __name__ == "__main__":
    print(f"Contract mirror version: {CONTRACT_VERSION}")
    print(f"Upstream:                {UPSTREAM}")
    print(f"Canonical equations:     {len(CANONICAL_EQUATIONS)}")
    print()

    print("Equation roster:")
    for eid, eq in CANONICAL_EQUATIONS.items():
        print(f"  {eid.value:6}  {eq.name}")
    print()

    # Round-trip a payload
    sample = {
        "contract_version": CONTRACT_VERSION,
        "source_commit": "abc1234",
        "measurements": [
            {"equation_id": "ER",   "value": 0.62, "timestamp": "2024-Q4"},
            {"equation_id": "UFR",  "value": 1.45, "timestamp": "2024-Q4"},
            {"equation_id": "MSI",  "value": 0.18, "timestamp": "2024-Q4"},
            {"equation_id": "HHI",  "value": 3500, "timestamp": "2024-Q4"},
            {"equation_id": "SD",   "value": 0.022, "timestamp": "2024",
             "measurement_notes": "term: 'capitalism'"},
        ],
    }

    payload = EconomicsPayload.from_dict(sample)
    print(f"Payload version:         {payload.contract_version}")
    print(f"Compatible (major=1):    {payload.is_compatible(1)}")
    print(f"Source commit:           {payload.source_commit}")
    print(f"Measurements:            {len(payload.measurements)}")
    print()

    er = payload.lookup(EquationID.ER)
    print(f"ER lookup -> value={er.value}, ts={er.timestamp}")

    # Regression guards
    # Upstream README describes "13 equations + OSDI composite". The
    # contract enumerates all 14 IDs since OSDI is required to decode
    # ME payloads even though it's a derived composite.
    assert len(CANONICAL_EQUATIONS) == 14
    assert EquationID.OSDI.value == "OSDI"
    assert payload.lookup(EquationID.LWR) is None  # not in sample
    print("Regression guards: OK")

