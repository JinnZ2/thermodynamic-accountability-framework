"""
institutional_audit_protocol.py

Executable form of the Institutional Thermodynamic Audit Protocol.
Four gates: Falsification, Thermodynamic, Audit Trail, Credential Validity.
An institution must pass all four to be classified VIABLE.

Pairs with institution_scientific_spec.py -- that module defines what
an institution IS. This module defines how to AUDIT one against
substrate-primary, scientific-method criteria.

Verdict ladder:
    VIABLE         all four gates pass
    MARGINAL       three gates pass, one weak
    SUBSIDIZED     thermodynamic gate fails (net energy negative,
                   sustained by external subsidy or coercion)
    PARASITIC      thermodynamic gate fails AND audit trail gate fails
                   (no accountability AND consuming more than producing)
    UNFALSIFIABLE  falsification gate fails (no condition could
                   ever prove this institution wrong)

License: CC0. Stdlib only.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


# =============================================================================
# DECLARED FIELDS (institution self-reports these)
# =============================================================================

@dataclass
class InstitutionDeclaration:
    """What the institution says about itself."""
    name: str
    purpose_declared: str
    scope_declared: str
    time_frame_declared: str  # "perpetual" is a red flag


# =============================================================================
# GATE 1: FALSIFICATION
# =============================================================================

@dataclass
class FalsificationGate:
    """Can this institution be proven wrong?"""
    how_could_it_be_wrong: str
    measurement_that_would_prove_failure: str
    time_horizon_for_test: str  # e.g., "5 years", "1 generation"
    who_measures: str  # "external", "self", "none"

    def passes(self) -> bool:
        """Gate passes only if all four fields are substantively
        answered AND the measurer is external."""
        if not all([
            self.how_could_it_be_wrong,
            self.measurement_that_would_prove_failure,
            self.time_horizon_for_test,
            self.who_measures,
        ]):
            return False
        if self.who_measures.strip().lower() in ("self", "none", ""):
            return False
        if self.time_horizon_for_test.strip().lower() in (
            "perpetual", "indefinite", "never", ""
        ):
            return False
        return True

    def weakness_notes(self) -> List[str]:
        notes = []
        if not self.how_could_it_be_wrong:
            notes.append("no failure condition declared")
        if not self.measurement_that_would_prove_failure:
            notes.append("no measurable failure signal")
        if self.who_measures.strip().lower() == "self":
            notes.append("self-measurement = not falsifiable in practice")
        if self.time_horizon_for_test.strip().lower() in (
            "perpetual", "indefinite"
        ):
            notes.append("perpetual time horizon = unfalsifiable")
        return notes


# =============================================================================
# GATE 2: THERMODYNAMIC
# =============================================================================

@dataclass
class ThermodynamicGate:
    """Does the institution return more than it consumes?"""
    energy_in_joules: float
    energy_out_joules: float
    parasitic_load_joules: float
    narrative_masking_present: bool
    sustains_without_external_subsidy: bool

    def net_balance(self) -> float:
        return self.energy_out_joules - (
            self.energy_in_joules + self.parasitic_load_joules
        )

    def parasitic_ratio(self) -> float:
        total = self.energy_in_joules + self.parasitic_load_joules
        if total <= 0:
            return 0.0
        return self.parasitic_load_joules / total

    def passes(self) -> bool:
        if self.net_balance() <= 0:
            return False
        if not self.sustains_without_external_subsidy:
            return False
        if self.parasitic_ratio() > 0.5:
            return False
        return True

    def verdict_label(self) -> str:
        if self.net_balance() > 0 and self.sustains_without_external_subsidy:
            return "thermodynamically_viable"
        if not self.sustains_without_external_subsidy:
            return "subsidized"
        return "net_negative"


# =============================================================================
# GATE 3: AUDIT TRAIL
# =============================================================================

@dataclass
class AuditTrailGate:
    """Is there a real, external accountability mechanism?"""
    last_external_audit: Optional[datetime]
    auditor_independent_of_institution: bool
    results_published_publicly: bool
    results_falsifiable: bool      # could the audit have produced a "fail"?
    can_be_defunded: bool          # is there any mechanism to stop it?
    adjusts_based_on_measurement: bool  # vs defending narrative

    def passes(self) -> bool:
        if self.last_external_audit is None:
            return False
        if not self.auditor_independent_of_institution:
            return False
        if not self.results_published_publicly:
            return False
        if not self.results_falsifiable:
            return False
        if not self.can_be_defunded:
            return False
        if not self.adjusts_based_on_measurement:
            return False
        return True

    def weakness_notes(self) -> List[str]:
        notes = []
        if self.last_external_audit is None:
            notes.append("no external audit on record")
        if not self.auditor_independent_of_institution:
            notes.append("auditor financially dependent on institution")
        if not self.results_published_publicly:
            notes.append("audit results not public = ceremonial")
        if not self.results_falsifiable:
            notes.append("audit cannot produce a fail = ceremonial")
        if not self.can_be_defunded:
            notes.append(
                "cannot be defunded = politically shielded, not accountable"
            )
        if not self.adjusts_based_on_measurement:
            notes.append("defends narrative instead of adjusting")
        return notes


# =============================================================================
# GATE 4: CREDENTIAL VALIDITY
# =============================================================================

@dataclass
class CredentialValidityGate:
    """Does this institution's authority claim survive first-principles audit?"""
    authority_granted_by: str          # who decided this institution has authority?
    measurement_used_to_grant: str     # by what measurement?
    tested_in: str                     # "field", "lab_only", "narrative_only"
    years_validated_under_real_conditions: float
    thermodynamically_viable_or_subsidized: str  # "viable" or "subsidized"

    def passes(self) -> bool:
        if not self.authority_granted_by:
            return False
        if self.authority_granted_by.strip().lower() in (
            "self", "the institution itself", ""
        ):
            return False
        if self.tested_in.strip().lower() in (
            "lab_only", "narrative_only", ""
        ):
            return False
        if self.years_validated_under_real_conditions < 5:
            return False
        if self.thermodynamically_viable_or_subsidized.strip().lower() != "viable":
            return False
        return True

    def weakness_notes(self) -> List[str]:
        notes = []
        if self.authority_granted_by.strip().lower() in (
            "self", "the institution itself"
        ):
            notes.append("self-granted authority = circular")
        if self.tested_in.strip().lower() == "lab_only":
            notes.append(
                "lab-only validation does not prove field viability "
                "(Point Pleasant Bridge problem)"
            )
        if self.tested_in.strip().lower() == "narrative_only":
            notes.append("authority based on narrative, not measurement")
        if self.years_validated_under_real_conditions < 5:
            notes.append(
                f"only {self.years_validated_under_real_conditions} years "
                "in real conditions = insufficient sample"
            )
        if self.thermodynamically_viable_or_subsidized.strip().lower() == "subsidized":
            notes.append("authority maintained by subsidy, not function")
        return notes


# =============================================================================
# COMPLETE AUDIT
# =============================================================================

class Verdict(Enum):
    VIABLE = "viable"
    MARGINAL = "marginal"
    SUBSIDIZED = "subsidized"
    PARASITIC = "parasitic"
    UNFALSIFIABLE = "unfalsifiable"


@dataclass
class InstitutionalAudit:
    declaration: InstitutionDeclaration
    falsification: FalsificationGate
    thermodynamic: ThermodynamicGate
    audit_trail: AuditTrailGate
    credential: CredentialValidityGate

    def verdict(self) -> Verdict:
        f = self.falsification.passes()
        t = self.thermodynamic.passes()
        a = self.audit_trail.passes()
        c = self.credential.passes()

        if not f:
            return Verdict.UNFALSIFIABLE
        if not t and not a:
            return Verdict.PARASITIC
        if not t:
            return Verdict.SUBSIDIZED
        if all([f, t, a, c]):
            return Verdict.VIABLE
        return Verdict.MARGINAL

    def report(self) -> Dict[str, Any]:
        return {
            "institution": self.declaration.name,
            "purpose_declared": self.declaration.purpose_declared,
            "scope_declared": self.declaration.scope_declared,
            "time_frame_declared": self.declaration.time_frame_declared,
            "gates": {
                "falsification": {
                    "passes": self.falsification.passes(),
                    "weaknesses": self.falsification.weakness_notes(),
                },
                "thermodynamic": {
                    "passes": self.thermodynamic.passes(),
                    "net_balance_joules": self.thermodynamic.net_balance(),
                    "parasitic_ratio": round(
                        self.thermodynamic.parasitic_ratio(), 3
                    ),
                    "label": self.thermodynamic.verdict_label(),
                },
                "audit_trail": {
                    "passes": self.audit_trail.passes(),
                    "weaknesses": self.audit_trail.weakness_notes(),
                },
                "credential": {
                    "passes": self.credential.passes(),
                    "weaknesses": self.credential.weakness_notes(),
                },
            },
            "verdict": self.verdict().value,
        }


# =============================================================================
# SMOKE TEST
# =============================================================================

if __name__ == "__main__":
    # Worked example: a generic regulatory body that fails three gates
    audit = InstitutionalAudit(
        declaration=InstitutionDeclaration(
            name="Example Regulatory Agency",
            purpose_declared="Protect public from harm in domain X",
            scope_declared="All commercial activity in domain X",
            time_frame_declared="perpetual",
        ),
        falsification=FalsificationGate(
            how_could_it_be_wrong="",
            measurement_that_would_prove_failure="",
            time_horizon_for_test="perpetual",
            who_measures="self",
        ),
        thermodynamic=ThermodynamicGate(
            energy_in_joules=1_000_000.0,
            energy_out_joules=200_000.0,
            parasitic_load_joules=600_000.0,
            narrative_masking_present=True,
            sustains_without_external_subsidy=False,
        ),
        audit_trail=AuditTrailGate(
            last_external_audit=None,
            auditor_independent_of_institution=False,
            results_published_publicly=False,
            results_falsifiable=False,
            can_be_defunded=False,
            adjusts_based_on_measurement=False,
        ),
        credential=CredentialValidityGate(
            authority_granted_by="self",
            measurement_used_to_grant="enabling legislation",
            tested_in="narrative_only",
            years_validated_under_real_conditions=0,
            thermodynamically_viable_or_subsidized="subsidized",
        ),
    )

    from json import dumps
    print(dumps(audit.report(), indent=2, default=str))
    print(f"\nVERDICT: {audit.verdict().value.upper()}")

# =============================================================================
# GATE 5: STRUCTURAL CONTINUITY (The "Slippery Case" Gate)
# =============================================================================

@dataclass
class ContinuityGate:
    """Does the institution's identity survive its internal turnover?"""
    invariant_declared: str            # The "mechanical soul" that must stay same
    personnel_turnover_percent: float   # % change in membership since last audit
    ownership_shifted: bool             # Has control changed?
    last_structural_audit: Optional[datetime]

    def calculate_drift(self) -> float:
        # High turnover + ownership change = High Drift
        drift = self.personnel_turnover_percent / 100.0
        if self.ownership_shifted:
            drift += 0.5
        return min(drift, 1.0)

    def passes(self) -> bool:
        # A drift > 0.7 suggests the institution is a 're-skin' of a failure
        if self.calculate_drift() > 0.7:
            return False
        if not self.invariant_declared:
            return False
        return True

