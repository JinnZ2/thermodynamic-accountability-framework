"""
game_theory/information_completeness_audit.py

PROBLEM: "Rational actor" requires "relevant information."
But no one defines what "relevant" means or verifies it's available.

EXAMPLE: Economic model for "optimal" policy
- First-order effect: policy increases GDP
- Second-order effect: policy increases inequality
- Third-order effect: inequality destabilizes political system
- Fourth-order effect: destabilized system collapses institutions
- Fifth-order effect: institutional collapse enables predation on vulnerable populations

If your "rational decision" is based only on first-order data (GDP up),
you're not rational. You're willfully blind to consequences.

WORSE: If second-order data is *available* but you're not *allowed*
to see it (suppressed, classified, inconvenient), then you were never
working with "relevant information." You were working with
*curated* information.

That's not rationality. That's rationalization.

Companion to game_theory/rationality_audit.py: rationality_audit
examined the "rational actor" definition; this module examines the
"relevant information" assumption beneath it. Sister to core/
formalized_dissent_esp.py (the structural mechanism that prevents
information curation upstream of the decision) and political_audit/
consensus_speed_audit.py (the empirical signature of decisions made
on curated rather than complete information).

CC0 Public Domain. Standard library only.
"""

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class InformationChain:
    """Map of information dependencies for a decision."""
    decision: str
    order_0_data: Dict[str, str]
    order_1_effects: Dict[str, str]
    order_2_effects: Dict[str, str]
    order_3_effects: Dict[str, str]
    order_n_effects: Dict[str, str]
    data_accessibility: Dict[str, bool]
    data_suppression: List[str]
    decision_made_on: List[str]


class RationalityDepthAudit:
    """
    How deep does the decision-maker look?
    """

    def audit_decision(self, chain: InformationChain) -> Dict:
        """
        Returns: depth of analysis vs. actual consequences.
        """

        considered_depth = len([d for d in chain.decision_made_on if d])

        relevant_depth = len([e for e in chain.order_n_effects.values() if e])

        ignored_available = [
            order for order, accessible in chain.data_accessibility.items()
            if accessible and order not in chain.decision_made_on
        ]

        suppressed = chain.data_suppression

        return {
            "decision": chain.decision,
            "analysis_depth_orders": considered_depth,
            "actual_relevance_depth_orders": relevant_depth,
            "depth_gap": relevant_depth - considered_depth,
            "ignored_available_data": ignored_available,
            "suppressed_data": suppressed,
            "is_rational": (
                considered_depth >= relevant_depth and
                len(ignored_available) == 0 and
                len(suppressed) == 0
            ),
            "rationality_verdict": (
                "RATIONAL" if considered_depth >= relevant_depth
                else f"IRRATIONAL (stopped at order {considered_depth}, effects extend to order {relevant_depth})"
            ),
        }


# =============================================
# SMOKE TEST
# =============================================

if __name__ == "__main__":
    policy_chain = InformationChain(
        decision="Increase resource extraction to boost GDP",
        order_0_data={
            "GDP_growth": "+3%",
            "Jobs_created": "5000",
            "Revenue": "$500M",
        },
        order_1_effects={
            "Ecosystem_degradation": "40% species loss in region",
            "Water_contamination": "3 aquifers polluted",
            "Worker_health": "20% respiratory illness spike",
        },
        order_2_effects={
            "Healthcare_costs": "+$200M/year (externalized to public)",
            "Agricultural_collapse": "soil toxicity, crop failure",
            "Migration_pressure": "50k people displaced",
        },
        order_3_effects={
            "Political_instability": "disenfranchised population destabilizes governance",
            "Remediation_cost": "+$2B/year for 20 years",
            "Insurance_system_failure": "ecological risk uninsurable",
        },
        order_n_effects={
            "Regime_shift": "ecosystem collapse, region becomes uninhabitable",
            "Cultural_loss": "indigenous knowledge systems destroyed",
            "Intergenerational_harm": "children born into contaminated landscape",
        },
        data_accessibility={
            "order_0": True,
            "order_1": True,
            "order_2": True,
            "order_3": True,
            "order_n": False,
        },
        data_suppression=[
            "order_1: Ecological impact report classified",
            "order_2: Healthcare cost projections suppressed",
            "order_3: Political stability models excluded from policy review",
        ],
        decision_made_on=["order_0"],
    )

    audit = RationalityDepthAudit()
    result = audit.audit_decision(policy_chain)

    print(f"Decision: {result['decision']}")
    print(f"Analysis depth: order {result['analysis_depth_orders']}")
    print(f"Actual relevance depth: order {result['actual_relevance_depth_orders']}")
    print(f"Gap: {result['depth_gap']} orders of magnitude")
    print(f"Ignored available data: {result['ignored_available_data']}")
    print(f"Suppressed data: {result['suppressed_data']}")
    print(f"Verdict: {result['rationality_verdict']}")
