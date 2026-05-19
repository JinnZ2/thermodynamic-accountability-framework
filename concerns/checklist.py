"""
concerns/checklist.py

Router that takes a described situation and points at the
concerns/ modules that apply.

Use case: someone is evaluating a specific situation (a deployment
decision, a quantitative harm projection, a regulatory question)
and wants to know which audit modules to run, in what order, and
why. This module answers that without composing the audits itself
-- it produces a checklist the reader works through manually,
since each underlying audit needs its own situation-specific
inputs.

Tenth+1 module in concerns/. Index module, not an audit.

License: CC0 -- public domain
Dependencies: stdlib only
"""

from dataclasses import dataclass, field
from typing import List, Optional


# ============================================================
# SITUATION DESCRIPTOR
# ============================================================

@dataclass
class Situation:
    """A described situation to evaluate."""
    description: str

    # ---- claim characteristics ----
    has_quantitative_harm_claim: bool = False
    """E.g. 'this policy will cause N deaths' or 'this practice
    affects M people'. If True, the cascade modules apply."""

    has_structural_pattern_claim: bool = False
    """E.g. 'this practice follows the same pattern as X'. If True,
    the credentialed-harm catalog applies."""

    has_certification_claim: bool = False
    """E.g. 'this intervention is safe / aligned / ready to deploy'.
    If True, the certification-chain audit applies."""

    # ---- domain characteristics ----
    involves_physical_substrate: bool = False
    """Touches soil, water, energy, biological systems."""

    involves_regulatory_authority: bool = False
    """An institution or rule-making body has authority to
    modify the situation."""

    involves_deployment_decision: bool = False
    """A specific go/no-go decision is being made (not just a
    research question)."""

    # ---- evidence characteristics ----
    has_calibration_anchor: bool = False
    """Can be compared against a published empirical case."""

    has_citation_chain: bool = False
    """Claims trace back to documented sources."""

    # ---- measurement characteristics ----
    measurement_substitution_suspected: bool = False
    """Current metric in use is suspected of measuring extraction
    or financial proxy rather than the substrate property the
    question is actually about (e.g. property value used to
    assess regional sustainability)."""

    baseline_unknown: bool = False
    """Sustainable load capacity is not measured; decisions are
    being made without knowing what the substrate can absorb."""


# ============================================================
# AUDIT RECOMMENDATION
# ============================================================

@dataclass
class AuditRecommendation:
    module: str
    reason: str
    order: int  # smaller = run earlier
    optional: bool = False


# ============================================================
# ROUTER
# ============================================================

def recommend_audits(situation: Situation) -> List[AuditRecommendation]:
    """Return the audit modules that apply to this situation."""
    recs: List[AuditRecommendation] = []

    # Empirical-record framing comes first if there's any
    # structural-pattern element. Without anchoring to the
    # historical record, structural claims drift toward analogy
    # rather than auditable comparison.
    if situation.has_structural_pattern_claim or situation.involves_deployment_decision:
        recs.append(AuditRecommendation(
            module="credentialed_harm_cascade.py",
            reason=(
                "Anchor the structural-pattern claim against the 90-year "
                "empirical catalog (6 cases: lobotomy, thalidomide, DDT, "
                "leaded gas, opioids, MI). If the claim matches one of "
                "those patterns, the catalog gives the historical-arc "
                "timing. If it does not match any, the pattern claim "
                "needs more support before deployment-decision-grade use."
            ),
            order=1,
        ))

    if situation.involves_physical_substrate:
        recs.append(AuditRecommendation(
            module="externality_model_audit.py",
            reason=(
                "150-year empirical record on what happens to physical "
                "substrate under continuous load. Use as the long-arc "
                "reference for any current-case substrate claim."
            ),
            order=2,
        ))
        recs.append(AuditRecommendation(
            module="cascade_failure_rural_degradation.py",
            reason=(
                "Threshold timing (5-10 / 10-20 / 15-25 year cascade "
                "thresholds) and the 65:1 loss-to-formation ratio. Use "
                "to check whether current load is compatible with "
                "physical recovery rates -- and whether thresholds in "
                "the cascade have already been crossed."
            ),
            order=3,
        ))

    # Cascade modeling for quantitative-claim situations
    if situation.has_quantitative_harm_claim:
        recs.append(AuditRecommendation(
            module="hormuz_cascade_audit.py",
            reason=(
                "5-layer physical cascade with calibration anchors "
                "(Sudan 2024, Ukraine 2023). Build a CascadeRun "
                "matching the situation; the audit_claims list shows "
                "which constraints the projection must satisfy to be "
                "physically reachable."
            ),
            order=4,
        ))
        if situation.involves_deployment_decision:
            recs.append(AuditRecommendation(
                module="leverage_analysis_v2.py",
                reason=(
                    "Once a cascade is parameterized, this module ranks "
                    "interventions by lives-saved per unit effort across "
                    "multiple operating points. Useful when the question "
                    "is not 'what's the projection' but 'where should "
                    "the marginal action go'."
                ),
                order=5,
            ))

    # Load-bearing failure node identification
    if situation.involves_regulatory_authority:
        recs.append(AuditRecommendation(
            module="institutional_bottleneck_audit.py",
            reason=(
                "When the cascade has a regulatory chokepoint that "
                "blocks a physical redundancy, the load-bearing failure "
                "node is institutional rather than physical. The "
                "attribution-formula section gives the legal/moral "
                "standard for assigning consequence to the regulator."
            ),
            order=6,
        ))
        recs.append(AuditRecommendation(
            module="substrate_externality_load_map.py",
            reason=(
                "Structural argument for cases where 'optimization' "
                "discourse hides externalized substrate cost. Pairs "
                "with institutional_bottleneck_audit when the "
                "regulatory structure is what permits the externality."
            ),
            order=7,
        ))

    # Certification-chain diagnostic
    if situation.has_certification_claim or situation.involves_deployment_decision:
        recs.append(AuditRecommendation(
            module="interpretation_certification_chain_audit.py",
            reason=(
                "Score the chain from method -> claim -> safety property "
                "-> deployment certification. Flags links where the "
                "downstream claim exceeds upstream evidence. This is the "
                "operational diagnostic that distinguishes warranty-mode "
                "from hypothesis-mode at the decision point."
            ),
            order=8,
        ))
        recs.append(AuditRecommendation(
            module="mechanistic_interpretability_audit.py",
            reason=(
                "Structural-pattern parent for the certification-chain "
                "diagnostic. Use to evaluate whether the 6-axis lobotomy "
                "parallel binds, but operate the parallel carefully -- "
                "see the disanalogy notes in the module docstring."
            ),
            order=9,
            optional=True,
        ))

    # Current-case empirical record
    if situation.has_citation_chain:
        recs.append(AuditRecommendation(
            module="data_center_siting_playbook.py",
            reason=(
                "Sourced current-case record (2025-2026 data center "
                "siting). Use as the format reference for documenting a "
                "current case with citation discipline -- 7 layers, "
                "sources per claim."
            ),
            order=10,
            optional=True,
        ))

    # Operational/policy consequence when load-vs-capacity gap exists
    if situation.baseline_unknown or (
        situation.involves_physical_substrate and situation.involves_deployment_decision
    ):
        recs.append(AuditRecommendation(
            module="assessment_first_principle.py",
            reason=(
                "When sustainable load capacity is unmeasured and the "
                "loss-to-formation arithmetic forbids concurrent recovery, "
                "stopping new load until baseline exists is the minimum "
                "responsible action, not an extreme position. Module "
                "names the four conditions under which the pause becomes "
                "load-bearing rather than precautionary."
            ),
            order=11,
        ))

    # Instrument selection when measurement substitution is at issue
    if situation.measurement_substitution_suspected or situation.baseline_unknown:
        recs.append(AuditRecommendation(
            module="substrate_measurement_audit.py",
            reason=(
                "When financial-extraction metrics (property value, GDP, "
                "density) are being used to assess substrate capacity, "
                "the wrong instrument is reporting the wrong number. "
                "This module specifies the 9 substrate instruments "
                "(soil carbon, aquifer recharge, insect biomass, etc) "
                "that answer the actual question, and the operational "
                "tools that already exist to collect that data."
            ),
            order=12,
        ))

    recs.sort(key=lambda r: r.order)
    return recs


# ============================================================
# SMOKE TEST -- three reference situations
# ============================================================

if __name__ == "__main__":
    cases = [
        Situation(
            description=(
                "Proposed siting of an N-MW data center in a rural "
                "watershed with state regulatory authority"
            ),
            has_structural_pattern_claim=True,
            involves_physical_substrate=True,
            involves_regulatory_authority=True,
            involves_deployment_decision=True,
            has_citation_chain=True,
        ),
        Situation(
            description=(
                "An AI lab claims its frontier model has been "
                "interpretability-audited and lacks deceptive circuits"
            ),
            has_structural_pattern_claim=True,
            has_certification_claim=True,
            involves_deployment_decision=True,
        ),
        Situation(
            description=(
                "A published projection that a supply-chain disruption "
                "will cause 100M+ excess deaths within 24 months"
            ),
            has_quantitative_harm_claim=True,
            has_calibration_anchor=True,
            involves_physical_substrate=True,
            involves_regulatory_authority=True,
        ),
        Situation(
            description=(
                "A region's regulators report rising property values and "
                "GDP growth while local observers report soil loss, "
                "insect collapse, and well failure"
            ),
            measurement_substitution_suspected=True,
            baseline_unknown=True,
            involves_physical_substrate=True,
        ),
    ]

    for i, case in enumerate(cases, 1):
        print("=" * 72)
        print(f"CASE {i}: {case.description}")
        print("=" * 72)
        recs = recommend_audits(case)
        if not recs:
            print("  No audits matched. Add more situation descriptors.")
            continue
        for rec in recs:
            tag = " (optional)" if rec.optional else ""
            print(f"\n  [{rec.order}] {rec.module}{tag}")
            print(f"      {rec.reason}")
        print()
