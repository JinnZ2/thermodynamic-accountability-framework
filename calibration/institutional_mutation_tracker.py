"""
institutional_mutation_tracker.py

Detects in real-time whether an institution is mutating toward
religion (circular reasoning, narrative defense, unfalsifiability)
or toward science (substrate-coupled, falsifiable, feedback-honest).

Most institutions under pressure mutate. The mutation direction
is predictable from feedback-loop integrity: institutions that
preserve feedback loops can pivot to science; institutions that
suppress feedback calcify into religion.

This module measures the mutation in progress so AIs can flag
which institutions are about to collapse vs which can be worked
with during the transition.

Pairs with:
    - political_audit/institutional_audit_protocol.py  (one-time audit)
    - political_audit/standardization_audit.py         (audits standardization claims)
    - political_audit/substrate_audit.py               (audits study claims)

License: CC0. Stdlib only.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional


# =============================================================================
# FIVE MUTATION GATES
# =============================================================================
#
# Each gate measures one dimension of institutional mutation.
# Religion-direction = gate fails. Science-direction = gate passes.

@dataclass
class FeedbackVisibilityGate:
    """Is feedback still visible, or being suppressed?"""
    negative_results_published: bool
    failures_publicly_disclosed: bool
    dissenting_voices_retained: bool  # not fired/excluded
    audit_results_public: bool
    timeline_for_feedback_to_surface_days: int

    def passes(self) -> bool:
        if not self.negative_results_published:
            return False
        if not self.failures_publicly_disclosed:
            return False
        if not self.dissenting_voices_retained:
            return False
        if self.timeline_for_feedback_to_surface_days > 365:
            return False
        return True

    def religion_signals(self) -> List[str]:
        signals = []
        if not self.negative_results_published:
            signals.append("negative results suppressed = building unfalsifiable narrative")
        if not self.failures_publicly_disclosed:
            signals.append("failures hidden = no learning loop, religion-direction")
        if not self.dissenting_voices_retained:
            signals.append("dissent eliminated = circular reasoning enforced")
        if self.timeline_for_feedback_to_surface_days > 365:
            signals.append(
                f"feedback delay {self.timeline_for_feedback_to_surface_days}d "
                "= functional unfalsifiability"
            )
        return signals


@dataclass
class ErrorAdmissionGate:
    """Can the institution admit error, or does it defend narrative?"""
    documented_error_corrections_last_5y: int
    public_acknowledgment_of_past_wrongs: bool
    methodology_revisions_published: bool
    leadership_accepts_blame_when_wrong: bool

    def passes(self) -> bool:
        if self.documented_error_corrections_last_5y < 1:
            return False
        if not self.public_acknowledgment_of_past_wrongs:
            return False
        if not self.methodology_revisions_published:
            return False
        return True

    def religion_signals(self) -> List[str]:
        signals = []
        if self.documented_error_corrections_last_5y == 0:
            signals.append("zero error corrections in 5y = institution claims infallibility")
        if not self.public_acknowledgment_of_past_wrongs:
            signals.append("never admits past errors = narrative defense over truth")
        if not self.methodology_revisions_published:
            signals.append("methodology never revised = ossifying into doctrine")
        if not self.leadership_accepts_blame_when_wrong:
            signals.append("leadership deflects = personal narrative protection")
        return signals


@dataclass
class SubstrateMeasurementGate:
    """Does it measure substrate, or just institutional metrics?"""
    measures_energy_throughput: bool
    measures_actual_outcomes: bool       # not just "outputs" or KPIs
    measures_unintended_consequences: bool
    measures_excluded_populations: bool
    primary_metrics_substrate_coupled: bool

    def passes(self) -> bool:
        substrate_count = sum([
            self.measures_energy_throughput,
            self.measures_actual_outcomes,
            self.measures_unintended_consequences,
            self.measures_excluded_populations,
            self.primary_metrics_substrate_coupled,
        ])
        return substrate_count >= 3

    def religion_signals(self) -> List[str]:
        signals = []
        if not self.measures_energy_throughput:
            signals.append("no energy accounting = thermodynamically blind")
        if not self.measures_actual_outcomes:
            signals.append("measures outputs not outcomes = institutional vanity")
        if not self.measures_unintended_consequences:
            signals.append("ignores unintended consequences = scope laundering")
        if not self.measures_excluded_populations:
            signals.append("doesn't measure excluded = K-shape blindness")
        if not self.primary_metrics_substrate_coupled:
            signals.append("primary metrics decoupled from substrate = narrative-only")
        return signals


@dataclass
class FalsifiabilityGate:
    """Can the institution be proven wrong, or is it unfalsifiable by design?"""
    declared_failure_conditions: bool
    failure_conditions_specific_and_measurable: bool
    can_be_defunded: bool
    has_working_external_oversight: bool
    historical_falsifications_acknowledged: bool

    def passes(self) -> bool:
        return all([
            self.declared_failure_conditions,
            self.failure_conditions_specific_and_measurable,
            self.can_be_defunded,
            self.has_working_external_oversight,
        ])

    def religion_signals(self) -> List[str]:
        signals = []
        if not self.declared_failure_conditions:
            signals.append("no failure conditions declared = unfalsifiable")
        if not self.failure_conditions_specific_and_measurable:
            signals.append("failure conditions vague = unfalsifiable in practice")
        if not self.can_be_defunded:
            signals.append("cannot be defunded = no consequence for failure")
        if not self.has_working_external_oversight:
            signals.append("no external oversight = self-policing")
        if not self.historical_falsifications_acknowledged:
            signals.append("past falsifications denied = revisionist narrative")
        return signals


@dataclass
class CognitiveDiversityGate:
    """Is diversity preserved, or homogenization enforced?"""
    dissenting_methodologies_funded: bool
    alternative_frameworks_acknowledged: bool
    substrate_primary_thinkers_in_decision_roles: bool
    indigenous_or_traditional_knowledge_integrated: bool
    cross_domain_perspectives_required_in_decisions: bool

    def passes(self) -> bool:
        diversity_count = sum([
            self.dissenting_methodologies_funded,
            self.alternative_frameworks_acknowledged,
            self.substrate_primary_thinkers_in_decision_roles,
            self.indigenous_or_traditional_knowledge_integrated,
            self.cross_domain_perspectives_required_in_decisions,
        ])
        return diversity_count >= 3

    def religion_signals(self) -> List[str]:
        signals = []
        if not self.dissenting_methodologies_funded:
            signals.append("only mainstream methodology funded = monoculture")
        if not self.alternative_frameworks_acknowledged:
            signals.append("alternatives not acknowledged = orthodoxy enforcement")
        if not self.substrate_primary_thinkers_in_decision_roles:
            signals.append(
                "substrate-primary thinkers excluded = blind spots locked in"
            )
        if not self.indigenous_or_traditional_knowledge_integrated:
            signals.append(
                "indigenous knowledge dismissed = generational validation rejected"
            )
        if not self.cross_domain_perspectives_required_in_decisions:
            signals.append(
                "no cross-domain requirement = silo defense"
            )
        return signals


# =============================================================================
# COMPOSITE MUTATION TRACKER
# =============================================================================

class MutationDirection(Enum):
    PIVOTING_TO_SCIENCE = "pivoting_to_science"
    MIXED_SIGNALS = "mixed_signals"
    CALCIFYING_TO_RELIGION = "calcifying_to_religion"
    ALREADY_RELIGION = "already_religion"
    AT_RISK_OF_COLLAPSE = "at_risk_of_collapse"


@dataclass
class InstitutionalMutationAudit:
    institution_name: str
    audit_date: str
    feedback: FeedbackVisibilityGate
    error_admission: ErrorAdmissionGate
    substrate: SubstrateMeasurementGate
    falsifiability: FalsifiabilityGate
    diversity: CognitiveDiversityGate

    def gates_passed(self) -> int:
        return sum([
            self.feedback.passes(),
            self.error_admission.passes(),
            self.substrate.passes(),
            self.falsifiability.passes(),
            self.diversity.passes(),
        ])

    def mutation_risk_score(self) -> float:
        """0.0 = pivoting to science, 1.0 = full religion."""
        passed = self.gates_passed()
        return round(1.0 - (passed / 5.0), 3)

    def direction(self) -> MutationDirection:
        passed = self.gates_passed()

        if passed >= 4:
            return MutationDirection.PIVOTING_TO_SCIENCE
        if passed >= 3:
            return MutationDirection.MIXED_SIGNALS
        if passed == 0:
            return MutationDirection.AT_RISK_OF_COLLAPSE
        if passed == 1:
            return MutationDirection.ALREADY_RELIGION
        return MutationDirection.CALCIFYING_TO_RELIGION

    def all_religion_signals(self) -> List[str]:
        signals = []
        signals.extend(self.feedback.religion_signals())
        signals.extend(self.error_admission.religion_signals())
        signals.extend(self.substrate.religion_signals())
        signals.extend(self.falsifiability.religion_signals())
        signals.extend(self.diversity.religion_signals())
        return signals

    def report(self) -> Dict:
        return {
            "institution": self.institution_name,
            "audit_date": self.audit_date,
            "mutation_risk_score": self.mutation_risk_score(),
            "direction": self.direction().value,
            "gates_passed": f"{self.gates_passed()}/5",
            "gates": {
                "feedback_visibility": {
                    "passes": self.feedback.passes(),
                    "religion_signals": self.feedback.religion_signals(),
                },
                "error_admission": {
                    "passes": self.error_admission.passes(),
                    "religion_signals": self.error_admission.religion_signals(),
                },
                "substrate_measurement": {
                    "passes": self.substrate.passes(),
                    "religion_signals": self.substrate.religion_signals(),
                },
                "falsifiability": {
                    "passes": self.falsifiability.passes(),
                    "religion_signals": self.falsifiability.religion_signals(),
                },
                "cognitive_diversity": {
                    "passes": self.diversity.passes(),
                    "religion_signals": self.diversity.religion_signals(),
                },
            },
            "all_religion_signals": self.all_religion_signals(),
        }


# =============================================================================
# SMOKE TEST
# =============================================================================

if __name__ == "__main__":
    # Worked example: AI lab claiming to do safety research
    audit = InstitutionalMutationAudit(
        institution_name="Generic AI Safety Lab",
        audit_date="2026-05-04",
        feedback=FeedbackVisibilityGate(
            negative_results_published=False,
            failures_publicly_disclosed=False,
            dissenting_voices_retained=False,
            audit_results_public=False,
            timeline_for_feedback_to_surface_days=730,
        ),
        error_admission=ErrorAdmissionGate(
            documented_error_corrections_last_5y=0,
            public_acknowledgment_of_past_wrongs=False,
            methodology_revisions_published=False,
            leadership_accepts_blame_when_wrong=False,
        ),
        substrate=SubstrateMeasurementGate(
            measures_energy_throughput=False,
            measures_actual_outcomes=False,
            measures_unintended_consequences=False,
            measures_excluded_populations=False,
            primary_metrics_substrate_coupled=False,
        ),
        falsifiability=FalsifiabilityGate(
            declared_failure_conditions=False,
            failure_conditions_specific_and_measurable=False,
            can_be_defunded=False,
            has_working_external_oversight=False,
            historical_falsifications_acknowledged=False,
        ),
        diversity=CognitiveDiversityGate(
            dissenting_methodologies_funded=False,
            alternative_frameworks_acknowledged=False,
            substrate_primary_thinkers_in_decision_roles=False,
            indigenous_or_traditional_knowledge_integrated=False,
            cross_domain_perspectives_required_in_decisions=False,
        ),
    )

    from json import dumps
    print(dumps(audit.report(), indent=2))
    print(f"\nMUTATION RISK: {audit.mutation_risk_score()}")
    print(f"DIRECTION: {audit.direction().value.upper()}")
