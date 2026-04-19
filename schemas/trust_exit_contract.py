#!/usr/bin/env python3
"""
Trust-Exit Contract -- stable surface published by trust-exit-model.

This module mirrors the shapes that github.com/JinnZ2/trust-exit-model has
committed to as stable: names, fields, types, ranges, and enum ordering.
It is the contract TAF imports so it can ingest trust-exit-model output
without depending on the trust-exit-model package at runtime.

Scope of stability (the trust-exit side guarantees):
    - TrustPhase: 5-member IntEnum, names + ordering fixed.
    - TrustState: {trust_level, phase, violations_count}, immutable,
      plus recovery_potential in [0,1] (property on the source side).
    - CustomerSegment: 2-member Enum (DOER, GAMBLER).
    - Customer: the listed public fields below.
    - Derived scalars: NEV, LTV, fingerprint_score in [0,1], is_znp,
      gate_failure_profile {emission, capture, retention, dominant_gate}.

Explicitly NOT part of the contract (calibration knobs, may change
without a version bump on the trust-exit side):
    - alpha/beta decay constants in trust_degradation.
    - 0.80 / 0.50 / 0.25 / 0.05 phase-boundary thresholds.
    - 0.60 ZNP fingerprint cutoff.

Versioning: breaking changes on the trust-exit side bump CONTRACT_VERSION
major. Field additions with backward-compatible defaults bump minor.

Dependencies: stdlib only (dataclasses, enum, typing).
License: CC0 1.0 Universal (public domain).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, IntEnum
from typing import Any


# Semantic version of THIS contract mirror. Bumped when the trust-exit
# side announces a breaking change to its stable surface.
CONTRACT_VERSION = "1.0.0"

# Name of the upstream project whose shape this mirrors.
UPSTREAM = "github.com/JinnZ2/trust-exit-model"


# ============================================================
# ENUMS
# ============================================================

class TrustPhase(IntEnum):
    """Trust phases, ordered worst-to-best in integer value.

    Ordering is part of the contract: lower int = healthier. This lets
    consumers use `<` / `>` comparisons without looking up names.

    Mapping to TAF distance-to-collapse (see core/integrations/
    trust_exit_fieldlink.py) collapses TERMINAL and FINAL_EXIT onto
    distance 0.0 because both have recovery_potential = 0.
    """
    FULL_TRUST = 0
    EARLY_EROSION = 1
    CRITICAL_THRESHOLD = 2
    TERMINAL = 3
    FINAL_EXIT = 4


class CustomerSegment(Enum):
    """Two-segment customer classification.

    DOER: zero-tolerance; one trust violation triggers permanent exit.
    GAMBLER: manipulation-tolerant; rationalizes and remains.
    """
    DOER = "doer"
    GAMBLER = "gambler"


# ============================================================
# STATE OBJECTS
# ============================================================

@dataclass(frozen=True)
class TrustState:
    """Immutable snapshot of a customer's trust position.

    recovery_potential is carried as a field on the wire (for JSON
    interchange) even though the upstream defines it as a property.
    Consumers should treat it as read-only and trust the upstream
    value rather than recomputing.

    Invariants (upstream-guaranteed):
        0.0 <= trust_level <= 1.0
        0.0 <= recovery_potential <= 1.0
        violations_count >= 0
        recovery_potential == 0.0 when phase in {TERMINAL, FINAL_EXIT}
    """
    trust_level: float
    phase: TrustPhase
    violations_count: int
    recovery_potential: float = 0.0

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "TrustState":
        return cls(
            trust_level=float(d["trust_level"]),
            phase=TrustPhase[d["phase"]] if isinstance(d["phase"], str)
                  else TrustPhase(int(d["phase"])),
            violations_count=int(d["violations_count"]),
            recovery_potential=float(d.get("recovery_potential", 0.0)),
        )


@dataclass(frozen=True)
class GateFailureProfile:
    """Which accountability gate is failing and how hard.

    Each score is in [0,1]. dominant_gate names the gate with the
    highest score (the bottleneck).
    """
    emission_score: float
    capture_score: float
    retention_score: float
    dominant_gate: str

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "GateFailureProfile":
        return cls(
            emission_score=float(d["emission_score"]),
            capture_score=float(d["capture_score"]),
            retention_score=float(d["retention_score"]),
            dominant_gate=str(d["dominant_gate"]),
        )


@dataclass(frozen=True)
class Customer:
    """Customer-level public surface.

    Public fields (contract-stable):
        customer_id            -- opaque identifier, stringifiable
        segment                -- CustomerSegment
        trust_state            -- TrustState snapshot
        monthly_revenue        -- currency units, caller-defined
        tenure_months          -- non-negative integer
        social_reach           -- non-negative integer (audience size)
        manipulation_tolerance -- float in [0,1]; 0 = Doer-like
        violation_history      -- ordered sequence of event identifiers;
                                  shape of individual events is NOT in
                                  the contract, only the sequence itself
    """
    customer_id: str
    segment: CustomerSegment
    trust_state: TrustState
    monthly_revenue: float
    tenure_months: int
    social_reach: int
    manipulation_tolerance: float
    violation_history: tuple = field(default_factory=tuple)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Customer":
        seg = d["segment"]
        if isinstance(seg, str):
            segment = CustomerSegment(seg.lower())
        else:
            segment = CustomerSegment(seg)
        return cls(
            customer_id=str(d["customer_id"]),
            segment=segment,
            trust_state=TrustState.from_dict(d["trust_state"]),
            monthly_revenue=float(d["monthly_revenue"]),
            tenure_months=int(d["tenure_months"]),
            social_reach=int(d["social_reach"]),
            manipulation_tolerance=float(d["manipulation_tolerance"]),
            violation_history=tuple(d.get("violation_history", ())),
        )


# ============================================================
# DERIVED SCALARS (shape-stable; values may retune with calibration)
# ============================================================

@dataclass(frozen=True)
class TrustExitDerived:
    """Shape-stable derived scalars emitted by trust-exit-model.

    Field presence, names, and ranges are contract. Numeric values are
    subject to recalibration without a contract version bump.

    Fields:
        nev               -- Net Extraction Value (currency; may be negative)
        ltv               -- Lifetime value (currency; non-negative)
        fingerprint_score -- Zero-Nudge Population score in [0,1]
        is_znp            -- bool; upstream computes this from fingerprint_score
                             against its calibration cutoff
        gate_failure      -- GateFailureProfile
    """
    nev: float
    ltv: float
    fingerprint_score: float
    is_znp: bool
    gate_failure: GateFailureProfile

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "TrustExitDerived":
        return cls(
            nev=float(d["nev"]),
            ltv=float(d["ltv"]),
            fingerprint_score=float(d["fingerprint_score"]),
            is_znp=bool(d["is_znp"]),
            gate_failure=GateFailureProfile.from_dict(d["gate_failure"]),
        )


# ============================================================
# TOP-LEVEL PAYLOAD
# ============================================================

@dataclass(frozen=True)
class TrustExitPayload:
    """Envelope bundling a Customer snapshot with its derived scalars.

    This is the shape TAF's trust_exit_fieldlink ingests. Carries the
    contract version so consumers can gate on compatibility.
    """
    contract_version: str
    customer: Customer
    derived: TrustExitDerived

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "TrustExitPayload":
        return cls(
            contract_version=str(d.get("contract_version", "0.0.0")),
            customer=Customer.from_dict(d["customer"]),
            derived=TrustExitDerived.from_dict(d["derived"]),
        )

    def is_compatible(self, expected_major: int = 1) -> bool:
        """Check major-version compatibility with this consumer."""
        try:
            major = int(self.contract_version.split(".")[0])
        except (ValueError, IndexError):
            return False
        return major == expected_major


# ============================================================
# SELF-TEST
# ============================================================

if __name__ == "__main__":
    # Minimal round-trip example showing the shape TAF expects.
    sample = {
        "contract_version": CONTRACT_VERSION,
        "customer": {
            "customer_id": "c-0001",
            "segment": "doer",
            "trust_state": {
                "trust_level": 0.55,
                "phase": "EARLY_EROSION",
                "violations_count": 1,
                "recovery_potential": 0.4,
            },
            "monthly_revenue": 120.0,
            "tenure_months": 18,
            "social_reach": 250,
            "manipulation_tolerance": 0.1,
            "violation_history": ("v-2026-03-12",),
        },
        "derived": {
            "nev": -3661.0,
            "ltv": 4200.0,
            "fingerprint_score": 0.82,
            "is_znp": True,
            "gate_failure": {
                "emission_score": 0.7,
                "capture_score": 0.3,
                "retention_score": 0.6,
                "dominant_gate": "emission",
            },
        },
    }

    payload = TrustExitPayload.from_dict(sample)
    print(f"Contract mirror version: {CONTRACT_VERSION}")
    print(f"Upstream:                {UPSTREAM}")
    print(f"Payload version:         {payload.contract_version}")
    print(f"Compatible (major=1):    {payload.is_compatible(1)}")
    print(f"Segment:                 {payload.customer.segment.name}")
    print(f"Phase:                   {payload.customer.trust_state.phase.name}")
    print(f"Phase ordering (int):    {int(payload.customer.trust_state.phase)}")
    print(f"Recovery potential:      {payload.customer.trust_state.recovery_potential}")
    print(f"NEV:                     {payload.derived.nev}")
    print(f"is_znp:                  {payload.derived.is_znp}")
    print(f"Dominant gate:           {payload.derived.gate_failure.dominant_gate}")
