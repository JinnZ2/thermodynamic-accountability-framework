"""
standardization_audit.py

Audits any claim that standardization "worked" by measuring
what got eliminated, suppressed, or made invisible to support
the chosen standard.

Most standardization claims rely on measuring only the chosen
system's outputs while hiding:

    - what alternatives were eliminated
    - whose innovation pathways closed
    - what communities lost access
    - what the thermodynamic balance actually is
    - whether the comparison was ever fair

This module makes those costs visible.

Six gates:

    1. Innovation Suppression
    2. Comparative Fairness
    3. Community Impact
    4. Monopoly Enabling
    5. Resilience Cost (cascade failure risk)
    6. Thermodynamic Balance

Pairs with:
    - political_audit/substrate_audit.py
    - political_audit/institutional_audit_protocol.py
    - calibration/narrative_thermodynamics.py

License: CC0. Stdlib only.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


# =============================================================================
# DECLARATION (the standardization being audited)
# =============================================================================

@dataclass
class StandardizationCase:
    """The standardization being audited."""
    name: str
    chosen_system: str
    eliminated_alternatives: List[str]
    year_standardized: int
    declared_benefit: str  # what proponents claim it accomplished


# =============================================================================
# GATE 1: INNOVATION SUPPRESSION
# =============================================================================
#
# When one path is standardized, alternative paths stop receiving
# funding, research, and development. The cost is invisible because
# the alternatives never developed enough to be measured.

@dataclass
class InnovationSuppressionGate:
    """Did standardization halt development of alternatives?"""
    alternative_dev_halted_year: Optional[int]
    years_since_development_stopped: int
    alternative_funding_after_standard: str  # "zero", "minimal", "ongoing"
    researchers_displaced_estimate: int
    rediscovery_attempts: List[str]  # cases where alt was later found valuable

    def passes(self) -> bool:
        if self.alternative_funding_after_standard.lower() == "ongoing":
            return True
        if self.years_since_development_stopped < 10:
            return True
        return False

    def suppression_cost_notes(self) -> List[str]:
        notes = []
        if self.years_since_development_stopped >= 50:
            notes.append(
                f"alternative development halted "
                f"{self.years_since_development_stopped}+ "
                "years; potential capability unknown"
            )
        if self.alternative_funding_after_standard.lower() == "zero":
            notes.append("zero funding for alternatives = forced monoculture")
        if self.researchers_displaced_estimate > 100:
            notes.append(
                f"~{self.researchers_displaced_estimate} researchers "
                "redirected or displaced from alternative path"
            )
        if self.rediscovery_attempts:
            notes.append(
                f"alternative being rediscovered now: "
                f"{self.rediscovery_attempts} "
                "(evidence the suppression was premature)"
            )
        return notes


# =============================================================================
# GATE 2: COMPARATIVE FAIRNESS
# =============================================================================
#
# Was the chosen system genuinely tested against alternatives,
# or did it win because it had institutional/financial advantages?

@dataclass
class ComparativeFairnessGate:
    """Was the comparison between chosen and alternative actually fair?"""
    same_funding_level: bool
    same_development_time: bool
    same_regulatory_treatment: bool
    same_publication_standards: bool
    head_to_head_studies_exist: bool
    head_to_head_count: int

    def passes(self) -> bool:
        return all([
            self.same_funding_level,
            self.same_development_time,
            self.same_regulatory_treatment,
            self.same_publication_standards,
            self.head_to_head_studies_exist,
        ])

    def fairness_violations(self) -> List[str]:
        violations = []
        if not self.same_funding_level:
            violations.append(
                "unequal funding = chosen system had financial advantage"
            )
        if not self.same_development_time:
            violations.append(
                "unequal development time = alternative never matured"
            )
        if not self.same_regulatory_treatment:
            violations.append(
                "regulatory framework favored chosen system"
            )
        if not self.same_publication_standards:
            violations.append(
                "publication bias hid negative results for chosen system"
            )
        if not self.head_to_head_studies_exist:
            violations.append(
                "no head-to-head studies = superiority claim unfounded"
            )
        elif self.head_to_head_count < 5:
            violations.append(
                f"only {self.head_to_head_count} head-to-head studies = "
                "insufficient sample"
            )
        return violations


# =============================================================================
# GATE 3: COMMUNITY IMPACT
# =============================================================================
#
# Standardization affects communities asymmetrically. Some gain
# (monopoly holders, institutions). Some lose (people whose
# alternatives were eliminated, regions whose local solutions
# were suppressed).

@dataclass
class CommunityImpactGate:
    """Who gained, who lost, who lost access to alternatives?"""
    primary_beneficiaries: List[str]
    primary_cost_bearers: List[str]
    communities_lost_alternatives: List[str]
    benefit_distribution: str  # "concentrated", "mixed", "broadly_shared"
    cost_distribution: str

    def passes(self) -> bool:
        if self.benefit_distribution.lower() == "concentrated":
            return False
        if (
            self.cost_distribution.lower() == "broadly_shared"
            and self.benefit_distribution.lower() == "concentrated"
        ):
            return False
        if len(self.communities_lost_alternatives) > 0:
            return False
        return True

    def impact_notes(self) -> List[str]:
        notes = []
        if self.benefit_distribution.lower() == "concentrated":
            notes.append(
                f"benefits concentrated in: {self.primary_beneficiaries}"
            )
        if self.cost_distribution.lower() == "broadly_shared":
            notes.append(
                f"costs distributed across: {self.primary_cost_bearers}"
            )
        if self.communities_lost_alternatives:
            notes.append(
                f"communities denied alternatives: "
                f"{self.communities_lost_alternatives}"
            )
        return notes


# =============================================================================
# GATE 4: MONOPOLY ENABLING
# =============================================================================
#
# Standardization frequently functions as a monopoly mechanism:
# one company/institution captures the standard, alternatives are
# legally or technically excluded, and the standard-holder extracts
# rent indefinitely.

@dataclass
class MonopolyEnablingGate:
    """Did standardization enable monopoly control?"""
    primary_controllers: List[str]
    market_share_concentrated: bool  # >70% controlled by top players
    regional_alternatives_eliminated: bool
    legal_protection_for_standard: bool  # patents, regulations protect it
    rent_extraction_documented: bool

    def passes(self) -> bool:
        red_flags = sum([
            self.market_share_concentrated,
            self.regional_alternatives_eliminated,
            self.legal_protection_for_standard,
            self.rent_extraction_documented,
        ])
        return red_flags <= 1

    def monopoly_notes(self) -> List[str]:
        notes = []
        if self.market_share_concentrated:
            notes.append(
                f"market concentrated in {self.primary_controllers} "
                "(>70% control)"
            )
        if self.regional_alternatives_eliminated:
            notes.append("regional/local alternatives systematically removed")
        if self.legal_protection_for_standard:
            notes.append(
                "legal/regulatory protection prevents alternatives from competing"
            )
        if self.rent_extraction_documented:
            notes.append(
                "standard-holders extract ongoing rent from forced adoption"
            )
        return notes


# =============================================================================
# GATE 5: RESILIENCE COST (cascade failure risk)
# =============================================================================
#
# Diversity provides resilience. Standardization removes diversity.
# A single point of failure becomes possible. When the standard fails,
# everything dependent on it fails simultaneously.

@dataclass
class ResilienceCostGate:
    """How vulnerable to cascade failure does standardization make the system?"""
    single_point_of_failure_present: bool
    redundancy_eliminated: bool
    cascade_failure_examples: List[str]
    recovery_pathway_available: bool
    diversity_remaining_pct: float  # 0.0 = full monoculture

    def passes(self) -> bool:
        if self.single_point_of_failure_present:
            return False
        if self.diversity_remaining_pct < 0.3:
            return False
        if not self.recovery_pathway_available:
            return False
        return True

    def resilience_notes(self) -> List[str]:
        notes = []
        if self.single_point_of_failure_present:
            notes.append(
                "single point of failure exists = catastrophic risk"
            )
        if self.redundancy_eliminated:
            notes.append("redundant alternatives eliminated by standardization")
        if self.cascade_failure_examples:
            notes.append(
                f"documented cascade failures: {self.cascade_failure_examples}"
            )
        if self.diversity_remaining_pct < 0.3:
            notes.append(
                f"only {self.diversity_remaining_pct*100:.0f}% diversity "
                "remaining = monoculture"
            )
        if not self.recovery_pathway_available:
            notes.append(
                "no recovery pathway if standard fails = no resilience"
            )
        return notes


# =============================================================================
# GATE 6: THERMODYNAMIC BALANCE
# =============================================================================
#
# Does the standardization actually save energy/resources, or does
# it just shift costs to places that aren't measured?

@dataclass
class ThermodynamicBalanceGate:
    """Net energy/resource cost of standardization, all costs counted."""
    energy_saved_by_standard_joules: float
    energy_cost_of_maintenance_joules: float
    energy_cost_of_lost_alternatives_joules: float  # estimated
    energy_cost_of_cascade_failures_joules: float   # historical
    full_lifecycle_audited: bool

    def net_balance(self) -> float:
        return (
            self.energy_saved_by_standard_joules
            - self.energy_cost_of_maintenance_joules
            - self.energy_cost_of_lost_alternatives_joules
            - self.energy_cost_of_cascade_failures_joules
        )

    def passes(self) -> bool:
        if not self.full_lifecycle_audited:
            return False
        return self.net_balance() > 0

    def balance_notes(self) -> List[str]:
        notes = []
        if not self.full_lifecycle_audited:
            notes.append(
                "full lifecycle NOT audited; net benefit unverified"
            )
        balance = self.net_balance()
        if balance < 0:
            notes.append(
                f"net thermodynamic cost: {abs(balance):.2e} J "
                "(standardization is energy-negative)"
            )
        elif balance > 0:
            notes.append(
                f"net thermodynamic benefit: {balance:.2e} J"
            )
        return notes


# =============================================================================
# COMPOSITE AUDIT
# =============================================================================

class StandardizationVerdict(Enum):
    GENUINELY_BENEFICIAL = "genuinely_beneficial"
    BENEFICIAL_WITHIN_NARROW_SCOPE = "beneficial_within_narrow_scope"
    UNVERIFIED_CLAIM = "unverified_claim"
    MONOPOLY_ENABLING = "monopoly_enabling"
    INNOVATION_SUPPRESSING = "innovation_suppressing"
    NET_HARMFUL = "net_harmful"


@dataclass
class StandardizationAudit:
    case: StandardizationCase
    innovation: InnovationSuppressionGate
    fairness: ComparativeFairnessGate
    community: CommunityImpactGate
    monopoly: MonopolyEnablingGate
    resilience: ResilienceCostGate
    thermodynamic: ThermodynamicBalanceGate

    def verdict(self) -> StandardizationVerdict:
        gates_passed = sum([
            self.innovation.passes(),
            self.fairness.passes(),
            self.community.passes(),
            self.monopoly.passes(),
            self.resilience.passes(),
            self.thermodynamic.passes(),
        ])

        # Priority verdicts (worst-case wins)
        if not self.thermodynamic.passes() and \
                self.thermodynamic.net_balance() < 0:
            return StandardizationVerdict.NET_HARMFUL
        if not self.monopoly.passes():
            return StandardizationVerdict.MONOPOLY_ENABLING
        if not self.innovation.passes() and \
                self.innovation.years_since_development_stopped > 50:
            return StandardizationVerdict.INNOVATION_SUPPRESSING
        if not self.fairness.passes():
            return StandardizationVerdict.UNVERIFIED_CLAIM

        if gates_passed == 6:
            return StandardizationVerdict.GENUINELY_BENEFICIAL
        if gates_passed >= 4:
            return StandardizationVerdict.BENEFICIAL_WITHIN_NARROW_SCOPE
        return StandardizationVerdict.UNVERIFIED_CLAIM

    def all_red_flags(self) -> List[str]:
        flags = []
        flags.extend(self.innovation.suppression_cost_notes())
        flags.extend(self.fairness.fairness_violations())
        flags.extend(self.community.impact_notes())
        flags.extend(self.monopoly.monopoly_notes())
        flags.extend(self.resilience.resilience_notes())
        flags.extend(self.thermodynamic.balance_notes())
        return flags

    def report(self) -> Dict:
        return {
            "case": self.case.name,
            "chosen": self.case.chosen_system,
            "eliminated": self.case.eliminated_alternatives,
            "year_standardized": self.case.year_standardized,
            "declared_benefit": self.case.declared_benefit,
            "verdict": self.verdict().value,
            "gates": {
                "innovation_suppression": {
                    "passes": self.innovation.passes(),
                    "notes": self.innovation.suppression_cost_notes(),
                },
                "comparative_fairness": {
                    "passes": self.fairness.passes(),
                    "violations": self.fairness.fairness_violations(),
                },
                "community_impact": {
                    "passes": self.community.passes(),
                    "notes": self.community.impact_notes(),
                },
                "monopoly_enabling": {
                    "passes": self.monopoly.passes(),
                    "notes": self.monopoly.monopoly_notes(),
                },
                "resilience_cost": {
                    "passes": self.resilience.passes(),
                    "notes": self.resilience.resilience_notes(),
                },
                "thermodynamic_balance": {
                    "passes": self.thermodynamic.passes(),
                    "net_balance_joules": self.thermodynamic.net_balance(),
                    "notes": self.thermodynamic.balance_notes(),
                },
            },
            "all_red_flags": self.all_red_flags(),
        }


# =============================================================================
# WORKED EXAMPLE: AC/DC ELECTRICAL STANDARDIZATION
# =============================================================================

if __name__ == "__main__":
    ac_dc_audit = StandardizationAudit(
        case=StandardizationCase(
            name="AC/DC electrical grid standardization",
            chosen_system="Alternating Current (AC)",
            eliminated_alternatives=["Direct Current (DC)"],
            year_standardized=1893,
            declared_benefit=(
                "Long-distance transmission efficiency, "
                "universal grid compatibility"
            ),
        ),
        innovation=InnovationSuppressionGate(
            alternative_dev_halted_year=1893,
            years_since_development_stopped=133,
            alternative_funding_after_standard="minimal",
            researchers_displaced_estimate=500,
            rediscovery_attempts=[
                "DC for data centers (2010s)",
                "DC for solar/renewable integration (2015s)",
                "HVDC long-distance transmission (2000s)",
                "DC microgrids (2020s)",
            ],
        ),
        fairness=ComparativeFairnessGate(
            same_funding_level=False,
            same_development_time=False,
            same_regulatory_treatment=False,
            same_publication_standards=False,
            head_to_head_studies_exist=False,
            head_to_head_count=0,
        ),
        community=CommunityImpactGate(
            primary_beneficiaries=[
                "Westinghouse", "GE", "centralized utilities"
            ],
            primary_cost_bearers=[
                "ratepayers", "regional grid operators",
                "renewable integration efforts"
            ],
            communities_lost_alternatives=[
                "regional DC grids",
                "communities suited to local DC generation",
                "renewable-rich regions",
            ],
            benefit_distribution="concentrated",
            cost_distribution="broadly_shared",
        ),
        monopoly=MonopolyEnablingGate(
            primary_controllers=[
                "Westinghouse", "GE", "regulated utility monopolies"
            ],
            market_share_concentrated=True,
            regional_alternatives_eliminated=True,
            legal_protection_for_standard=True,
            rent_extraction_documented=True,
        ),
        resilience=ResilienceCostGate(
            single_point_of_failure_present=True,
            redundancy_eliminated=True,
            cascade_failure_examples=[
                "2003 Northeast blackout",
                "2021 Texas grid failure",
                "2025 Iberian Peninsula blackout",
            ],
            recovery_pathway_available=False,
            diversity_remaining_pct=0.05,
        ),
        thermodynamic=ThermodynamicBalanceGate(
            energy_saved_by_standard_joules=1.0e18,
            energy_cost_of_maintenance_joules=8.0e17,
            energy_cost_of_lost_alternatives_joules=5.0e17,
            energy_cost_of_cascade_failures_joules=2.0e17,
            full_lifecycle_audited=False,
        ),
    )

    from json import dumps
    print(dumps(ac_dc_audit.report(), indent=2))
    print(f"\nVERDICT: {ac_dc_audit.verdict().value.upper()}")
    print(f"\nTotal red flags: {len(ac_dc_audit.all_red_flags())}")
