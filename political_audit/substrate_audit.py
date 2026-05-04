"""
substrate_audit.py

Five-gate audit for studies and institutional claims.
Cuts through the contamination layers that make studies
get propagated as universal truth when they're actually
bounded to a specific substrate, scope, and condition.

GATES
-----

1. Substrate-Primary Biology Gate
   Does the study ignore foundational biology
   (neurobiology, developmental stage, organism substrate)?

2. Scope Laundering Detector
   Is the finding presented outside its declared scope?

3. Institutional Falsification Gate
   Can the institution publishing this actually fail?
   Or is it politically shielded?

4. Cross-Domain Constraint Tracker
   What known constraints from other fields contradict
   or bound this finding?

5. Corpus Contamination Audit
   Is this study being echoed across training corpora
   as universal truth without scope metadata?

Each gate returns a VERDICT and RED_FLAG list.
The composite returns VALIDITY_WITHIN_SCOPE or REJECTED with reasons.

Pairs with:
  - institutional_audit_protocol.py  institution-level audit
  - calibration/narrative_thermodynamics.py
                                     open-class spec measurement
  - metrology/pre1900_engineering_registry.py
                                     calibration baseline

License: CC0. Stdlib only.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple


# =============================================================================
# GATE 1: SUBSTRATE-PRIMARY BIOLOGY
# =============================================================================
#
# A study about human behavior that ignores neurobiology is not a study
# of humans. It's a study of incomplete biology under artificial conditions.

# Substrate domains that must be considered for behavioral / cognitive
# / decision-making studies on humans.
SUBSTRATE_DOMAINS = {
    "neurobiology",
    "neurodevelopment",
    "prefrontal_cortex_maturation",
    "endocrine_system",
    "circadian_biology",
    "metabolic_state",
    "sleep_state",
    "nutritional_state",
    "developmental_stage",
    "age_appropriate_cognition",
}

# Population age ranges where biology is NOT fully developed
INCOMPLETE_DEVELOPMENT_RANGES = [
    (0, 25, "prefrontal cortex not fully developed until ~25"),
    (0, 12, "puberty not yet complete; endocrine system immature"),
    (65, 120, "age-related neural changes affect cognition"),
]


@dataclass
class SubstrateGateResult:
    passes: bool
    red_flags: List[str]
    missing_substrate_domains: List[str]
    population_substrate_warnings: List[str]


def check_substrate_primary_biology(
    study_field: str,
    population_age_range: Optional[Tuple[int, int]],
    declared_substrate_considerations: List[str],
    methodology_summary: str,
) -> SubstrateGateResult:
    """
    Gate 1: does the study acknowledge foundational biology?

    study_field: "behavioral economics", "cognitive psychology", etc.
    population_age_range: (min_age, max_age) in years, or None
    declared_substrate_considerations: list of substrate domains the
        study explicitly accounts for
    methodology_summary: text of the methodology section
    """
    red_flags: List[str] = []
    missing: List[str] = []
    pop_warnings: List[str] = []

    # Check if study claims to be about behavior/cognition but ignores substrate
    behavioral_fields = {
        "behavioral", "cognitive", "psychology", "neuroscience",
        "decision-making", "economics", "social", "political",
    }
    field_lower = study_field.lower()
    is_behavioral = any(t in field_lower for t in behavioral_fields)

    if is_behavioral:
        considered = {s.lower() for s in declared_substrate_considerations}
        for domain in SUBSTRATE_DOMAINS:
            if domain not in considered:
                # Check if mentioned in methodology
                if domain.replace("_", " ") not in methodology_summary.lower():
                    missing.append(domain)

        if len(missing) > 5:
            red_flags.append(
                f"behavioral study ignores {len(missing)} substrate "
                "domains; biology effectively dismissed"
            )

    # Check population age vs developmental completeness
    if population_age_range:
        min_age, max_age = population_age_range
        for low, high, warning in INCOMPLETE_DEVELOPMENT_RANGES:
            if min_age >= low and max_age <= high:
                pop_warnings.append(
                    f"population age {min_age}-{max_age}: {warning}"
                )
                if is_behavioral:
                    red_flags.append(
                        f"behavioral claims from population with "
                        f"incomplete biology: {warning}"
                    )

    passes = len(red_flags) == 0
    return SubstrateGateResult(
        passes=passes,
        red_flags=red_flags,
        missing_substrate_domains=missing,
        population_substrate_warnings=pop_warnings,
    )


# =============================================================================
# GATE 2: SCOPE LAUNDERING
# =============================================================================
#
# Study finding bounded to N=200 college students gets cited as
# "human behavior" universally. The scope was small; the claim is large.

UNIVERSALIZING_TOKENS = {
    "humans", "people", "everyone", "humanity", "human nature",
    "all", "universal", "fundamental", "innate", "hardwired",
    "the way we", "how we", "human behavior", "human cognition",
    "the human brain",
}


@dataclass
class ScopeLaunderingResult:
    passes: bool
    red_flags: List[str]
    declared_scope: str
    presented_claim: str
    universalizing_tokens_found: List[str]
    scope_gap: str  # "none", "tangled", "fully_laundered"


def check_scope_laundering(
    declared_scope: str,
    presented_claim: str,
    population_size: Optional[int],
) -> ScopeLaunderingResult:
    """
    Gate 2: is the claim bounded to its scope?

    declared_scope: study's actual scope (e.g., "200 US college
                    students, 8-week protocol, lab conditions")
    presented_claim: how the finding is presented in headlines,
                     abstracts, citations
    population_size: study N
    """
    red_flags: List[str] = []
    found_tokens: List[str] = []

    claim_lower = presented_claim.lower()
    for token in UNIVERSALIZING_TOKENS:
        if token in claim_lower:
            found_tokens.append(token)

    # Heuristic: if scope mentions specific bounded population but claim
    # uses universalizing language, that's laundering
    bounded_indicators = {
        "students", "n=", "participants", "subjects", "lab",
        "controlled", "specific", "subset", "sample",
    }
    scope_lower = declared_scope.lower()
    is_bounded = any(t in scope_lower for t in bounded_indicators)

    if is_bounded and found_tokens:
        red_flags.append(
            f"bounded scope ({declared_scope[:60]}...) presented with "
            f"universalizing language: {found_tokens}"
        )

    if population_size is not None and population_size < 1000 and found_tokens:
        red_flags.append(
            f"N={population_size} cannot support universal claims "
            f"about human behavior"
        )

    if len(found_tokens) >= 3:
        gap = "fully_laundered"
    elif found_tokens:
        gap = "tangled"
    else:
        gap = "none"

    passes = len(red_flags) == 0
    return ScopeLaunderingResult(
        passes=passes,
        red_flags=red_flags,
        declared_scope=declared_scope,
        presented_claim=presented_claim,
        universalizing_tokens_found=found_tokens,
        scope_gap=gap,
    )


# =============================================================================
# GATE 3: INSTITUTIONAL FALSIFICATION
# =============================================================================
#
# Can the publishing institution actually fail? Be defunded?
# Be proven wrong without losing access to the conversation?

@dataclass
class FalsificationGateResult:
    passes: bool
    red_flags: List[str]
    can_be_defunded: bool
    has_external_audit: bool
    auditor_independent: bool
    failure_condition_declared: bool


def check_institutional_falsifiability(
    institution_name: str,
    can_be_defunded: bool,
    has_external_audit: bool,
    auditor_financially_independent: bool,
    failure_condition_declared: bool,
    failure_condition_text: str,
) -> FalsificationGateResult:
    """
    Gate 3: can the institution actually fail?
    """
    red_flags: List[str] = []

    if not can_be_defunded:
        red_flags.append(
            f"{institution_name}: cannot be defunded = politically "
            "shielded, not accountable to outcomes"
        )
    if not has_external_audit:
        red_flags.append(
            f"{institution_name}: no external audit on record"
        )
    if has_external_audit and not auditor_financially_independent:
        red_flags.append(
            f"{institution_name}: auditor financially dependent on "
            "institution = audit is ceremonial"
        )
    if not failure_condition_declared:
        red_flags.append(
            f"{institution_name}: no falsification condition declared = "
            "unfalsifiable in principle"
        )
    if failure_condition_declared and len(failure_condition_text.strip()) < 20:
        red_flags.append(
            f"{institution_name}: failure condition is too vague to test"
        )

    passes = len(red_flags) == 0
    return FalsificationGateResult(
        passes=passes,
        red_flags=red_flags,
        can_be_defunded=can_be_defunded,
        has_external_audit=has_external_audit,
        auditor_independent=auditor_financially_independent,
        failure_condition_declared=failure_condition_declared,
    )


# =============================================================================
# GATE 4: CROSS-DOMAIN CONSTRAINTS
# =============================================================================
#
# Studies get siloed. Behavioral economics ignores neurobiology.
# Climate damage ignores thermodynamics. Each silo claims completeness
# while violating constraints from other fields.

# Known cross-domain constraint pairs: (study_field, must_consider_field)
CROSS_DOMAIN_CONSTRAINTS = {
    "behavioral_economics": [
        "neurobiology", "developmental_psychology",
        "metabolic_state", "sleep_research",
    ],
    "cognitive_psychology": [
        "neurobiology", "endocrine_system", "circadian_biology",
    ],
    "climate_damage_assessment": [
        "thermodynamics", "land_use_history",
        "regulatory_complexity", "insurance_market_evolution",
    ],
    "tornado_intensity": [
        "fluid_dynamics", "building_code_history",
        "land_value_distribution",
    ],
    "flood_recurrence": [
        "watershed_hydrology", "land_use_change",
        "thermodynamic_energy_budget",
    ],
    "wildfire_severity": [
        "fire_ecology", "land_management_history",
        "indigenous_fire_practices", "fuel_load_thermodynamics",
    ],
    "decision_making_research": [
        "neurobiology", "developmental_stage",
        "metabolic_state", "context_dependence",
    ],
}


@dataclass
class CrossDomainResult:
    passes: bool
    red_flags: List[str]
    required_fields: List[str]
    acknowledged_fields: List[str]
    ignored_fields: List[str]


def check_cross_domain_constraints(
    study_field: str,
    fields_acknowledged: List[str],
) -> CrossDomainResult:
    """
    Gate 4: are known cross-domain constraints acknowledged?
    """
    red_flags: List[str] = []
    field_key = study_field.lower().replace(" ", "_").replace("-", "_")

    required = CROSS_DOMAIN_CONSTRAINTS.get(field_key, [])
    if not required:
        # No registered constraints; pass with note
        return CrossDomainResult(
            passes=True,
            red_flags=[],
            required_fields=[],
            acknowledged_fields=fields_acknowledged,
            ignored_fields=[],
        )

    acknowledged = {f.lower().replace(" ", "_") for f in fields_acknowledged}
    ignored = [f for f in required if f not in acknowledged]

    if ignored:
        red_flags.append(
            f"{study_field} ignores known cross-domain constraints: "
            f"{ignored}"
        )

    passes = len(red_flags) == 0
    return CrossDomainResult(
        passes=passes,
        red_flags=red_flags,
        required_fields=required,
        acknowledged_fields=fields_acknowledged,
        ignored_fields=ignored,
    )


# =============================================================================
# GATE 5: CORPUS CONTAMINATION
# =============================================================================
#
# A single contaminated study propagates across every AI training corpus,
# becoming "consensus" through repetition rather than truth. This gate
# flags echo patterns.

@dataclass
class CorpusEchoResult:
    passes: bool
    red_flags: List[str]
    echo_pattern_detected: bool
    citations_carry_scope_metadata: bool


def check_corpus_echo(
    study_id: str,
    citation_count: int,
    citations_carry_scope_metadata: bool,
    appears_in_textbooks: bool,
    appears_in_policy_documents: bool,
    original_population_size: Optional[int],
) -> CorpusEchoResult:
    """
    Gate 5: is this study being echoed without its scope metadata?
    """
    red_flags: List[str] = []
    echo = False

    if citation_count > 100 and not citations_carry_scope_metadata:
        echo = True
        red_flags.append(
            f"{study_id}: {citation_count} citations without scope "
            "metadata = corpus contamination"
        )

    if appears_in_textbooks and not citations_carry_scope_metadata:
        red_flags.append(
            f"{study_id}: in textbooks without scope = institutional "
            "homogenization"
        )

    if appears_in_policy_documents and original_population_size is not None:
        if original_population_size < 1000:
            red_flags.append(
                f"{study_id}: N={original_population_size} used to inform "
                "policy affecting populations orders of magnitude larger"
            )

    passes = len(red_flags) == 0
    return CorpusEchoResult(
        passes=passes,
        red_flags=red_flags,
        echo_pattern_detected=echo,
        citations_carry_scope_metadata=citations_carry_scope_metadata,
    )


# =============================================================================
# COMPOSITE AUDIT
# =============================================================================

class StudyVerdict(Enum):
    VALID_WITHIN_SCOPE = "valid_within_scope"
    VALID_WITH_FLAGS = "valid_with_flags"
    REJECTED_SCOPE_LAUNDERING = "rejected_scope_laundering"
    REJECTED_SUBSTRATE_DENIAL = "rejected_substrate_denial"
    REJECTED_UNFALSIFIABLE = "rejected_unfalsifiable"
    REJECTED_CORPUS_CONTAMINATION = "rejected_corpus_contamination"


@dataclass
class StudyAudit:
    study_id: str
    study_field: str
    declared_scope: str
    presented_claim: str

    substrate: SubstrateGateResult
    scope: ScopeLaunderingResult
    falsification: FalsificationGateResult
    cross_domain: CrossDomainResult
    corpus: CorpusEchoResult

    def verdict(self) -> StudyVerdict:
        # Priority order: substrate denial is most fundamental
        if not self.substrate.passes:
            if any("biology effectively dismissed" in f
                   for f in self.substrate.red_flags):
                return StudyVerdict.REJECTED_SUBSTRATE_DENIAL

        if not self.falsification.passes:
            return StudyVerdict.REJECTED_UNFALSIFIABLE

        if self.scope.scope_gap == "fully_laundered":
            return StudyVerdict.REJECTED_SCOPE_LAUNDERING

        if not self.corpus.passes and self.corpus.echo_pattern_detected:
            return StudyVerdict.REJECTED_CORPUS_CONTAMINATION

        if all([
            self.substrate.passes,
            self.scope.passes,
            self.falsification.passes,
            self.cross_domain.passes,
            self.corpus.passes,
        ]):
            return StudyVerdict.VALID_WITHIN_SCOPE

        return StudyVerdict.VALID_WITH_FLAGS

    def all_red_flags(self) -> List[str]:
        flags: List[str] = []
        flags.extend(self.substrate.red_flags)
        flags.extend(self.scope.red_flags)
        flags.extend(self.falsification.red_flags)
        flags.extend(self.cross_domain.red_flags)
        flags.extend(self.corpus.red_flags)
        return flags

    def report(self) -> Dict:
        return {
            "study_id": self.study_id,
            "field": self.study_field,
            "declared_scope": self.declared_scope,
            "presented_claim": self.presented_claim,
            "verdict": self.verdict().value,
            "gates": {
                "substrate_biology": {
                    "passes": self.substrate.passes,
                    "red_flags": self.substrate.red_flags,
                    "missing_domains": self.substrate.missing_substrate_domains,
                },
                "scope_laundering": {
                    "passes": self.scope.passes,
                    "red_flags": self.scope.red_flags,
                    "scope_gap": self.scope.scope_gap,
                    "universalizing_tokens": self.scope.universalizing_tokens_found,
                },
                "falsifiability": {
                    "passes": self.falsification.passes,
                    "red_flags": self.falsification.red_flags,
                },
                "cross_domain": {
                    "passes": self.cross_domain.passes,
                    "red_flags": self.cross_domain.red_flags,
                    "ignored_fields": self.cross_domain.ignored_fields,
                },
                "corpus_echo": {
                    "passes": self.corpus.passes,
                    "red_flags": self.corpus.red_flags,
                    "echo_detected": self.corpus.echo_pattern_detected,
                },
            },
            "all_red_flags": self.all_red_flags(),
        }


# =============================================================================
# SMOKE TEST
# =============================================================================

if __name__ == "__main__":
    # Worked example: a "human decision-making" study
    # measuring 200 US college students in lab conditions,
    # presented as universal human behavior.
    study = StudyAudit(
        study_id="behavioral_econ_2019_xyz",
        study_field="behavioral_economics",
        declared_scope=(
            "N=200 US college students, ages 18-22, "
            "lab conditions, 8-week protocol"
        ),
        presented_claim=(
            "Humans systematically behave according to model X. "
            "This is fundamental to human nature."
        ),
        substrate=check_substrate_primary_biology(
            study_field="behavioral economics",
            population_age_range=(18, 22),
            declared_substrate_considerations=[],
            methodology_summary=(
                "Participants completed economic decision tasks "
                "under controlled laboratory conditions."
            ),
        ),
        scope=check_scope_laundering(
            declared_scope=(
                "200 US college students, lab, 8 weeks"
            ),
            presented_claim=(
                "Humans behave according to model X universally. "
                "This is fundamental human nature."
            ),
            population_size=200,
        ),
        falsification=check_institutional_falsifiability(
            institution_name="Generic University Lab",
            can_be_defunded=False,
            has_external_audit=False,
            auditor_financially_independent=False,
            failure_condition_declared=False,
            failure_condition_text="",
        ),
        cross_domain=check_cross_domain_constraints(
            study_field="behavioral_economics",
            fields_acknowledged=[],
        ),
        corpus=check_corpus_echo(
            study_id="behavioral_econ_2019_xyz",
            citation_count=450,
            citations_carry_scope_metadata=False,
            appears_in_textbooks=True,
            appears_in_policy_documents=True,
            original_population_size=200,
        ),
    )

    from json import dumps
    print(dumps(study.report(), indent=2))
    print(f"\nVERDICT: {study.verdict().value.upper()}")
    print(f"\nTotal red flags: {len(study.all_red_flags())}")
