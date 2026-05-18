"""
concerns/interpretation_certification_chain_audit.py

Where the mechanistic-interpretability-vs-lobotomy parallel binds
hardest: not in MI research practice itself, but in the
certification chain that converts an interpretation hypothesis
into a deployment decision.

Sharpened from concerns/mechanistic_interpretability_audit.py.
That module audits the research-practice pattern; this module
audits the SPECIFIC failure mode where weak interpretation +
strong confidence + deployment authority + no rollback path =
the load-bearing structural parallel.

CERTIFICATION CHAIN (5 links):

  L1. Interpretation method runs           (e.g., circuit analysis,
                                            SAE feature extraction,
                                            activation patching)
       |
       v
  L2. Interpretation claim asserted        (e.g., "circuit X
                                            implements behavior Y")
       |
       v
  L3. Safety property derived              (e.g., "model lacks
                                            deceptive circuits")
       |
       v
  L4. Deployment certification issued      (e.g., "model is safe
                                            to deploy to N users")
       |
       v
  L5. Production users absorb the bet      (downstream harm, if any,
                                            displaced to future users
                                            rather than lab subjects)

FAILURE MODE: any link in the chain whose downstream assertion
is stronger than its upstream evidence creates a corruption
pathway. The chain corrupts at its weakest link, but the
DECISION at L4 inherits the confidence of L1 rather than the
evidence of L1 -- which is the lobotomy pattern in its load-
bearing form.

DISTINCTION FROM PARENT MODULE: this module does not flag
MI research as such. It flags the specific certification-
claim chain. MI research that ships interpretation as
"hypothesis with X% support across Y conditions" instead of
"explanation" does not trigger this audit. MI research that
ships interpretation as deployment warranty does.

CC0 Public Domain. Standard library only.
"""

from dataclasses import dataclass
from typing import List


@dataclass
class CertificationLink:
    """One link in the certification chain."""
    link_id: str
    name: str
    evidence_strength: float  # [0, 1] -- how well-supported is this link's claim
    downstream_claim_strength: float  # [0, 1] -- how strongly the NEXT link relies on it
    evidence_basis: str
    failure_mode_if_overstated: str


@dataclass
class CertificationChain:
    """A complete interpretation -> deployment chain for one model claim."""
    model_id: str
    interpretation_method: str
    safety_property_claimed: str
    deployment_authority: str
    rollback_path_exists: bool
    in_field_dissent_documented: bool
    independent_replication_attempted: bool
    links: List[CertificationLink]

    def weak_links(self) -> List[CertificationLink]:
        """
        A link is weak when its downstream claim exceeds its evidence.
        This is where confidence outruns the data.
        """
        return [
            link for link in self.links
            if link.downstream_claim_strength > link.evidence_strength
        ]

    def chain_strength(self) -> float:
        """
        Chain strength is bounded by the weakest link's evidence.
        Multiplicative across the chain, since each link is a
        conditional probability.
        """
        if not self.links:
            return 0.0
        result = 1.0
        for link in self.links:
            result *= link.evidence_strength
        return result

    def confidence_gap(self) -> float:
        """
        Deployment confidence is inherited from the final downstream_
        claim_strength; actual support is the chain_strength product.
        Gap measures how much the deployment decision is over-claiming.
        """
        if not self.links:
            return 0.0
        deployment_confidence = self.links[-1].downstream_claim_strength
        actual_support = self.chain_strength()
        return deployment_confidence - actual_support

    def lobotomy_parallel_score(self) -> float:
        """
        Score the load-bearing structural parallel. Higher = closer
        to the 1935 pattern.
        """
        score = 0.0
        if self.confidence_gap() > 0.3:
            score += 0.3
        if not self.rollback_path_exists:
            score += 0.25
        if not self.in_field_dissent_documented:
            score += 0.2
        if not self.independent_replication_attempted:
            score += 0.15
        if len(self.weak_links()) >= 2:
            score += 0.1
        return min(1.0, score)

    def verdict(self) -> str:
        score = self.lobotomy_parallel_score()
        gap = self.confidence_gap()
        if score >= 0.7:
            return f"HIGH STRUCTURAL PARALLEL ({score:.2f}); confidence gap {gap:+.2f}"
        if score >= 0.4:
            return f"MODERATE STRUCTURAL PARALLEL ({score:.2f}); confidence gap {gap:+.2f}"
        if score >= 0.2:
            return f"LOW STRUCTURAL PARALLEL ({score:.2f}); confidence gap {gap:+.2f}"
        return f"PARALLEL DOES NOT BIND ({score:.2f}); chain operates as hypothesis not warranty"


# =============================================
# SMOKE TEST
# =============================================

if __name__ == "__main__":
    # Case A: a certification chain operating as deployment warranty,
    # weak evidence at L1 and L2, strong downstream claims, no rollback.
    # This is the load-bearing failure mode the parent module flags.
    warranty_chain = CertificationChain(
        model_id="hypothetical-frontier-model-2026",
        interpretation_method="SAE feature attribution + activation patching",
        safety_property_claimed="model lacks deceptive-reasoning circuits",
        deployment_authority="internal safety committee, 5 reviewers",
        rollback_path_exists=False,
        in_field_dissent_documented=False,
        independent_replication_attempted=False,
        links=[
            CertificationLink(
                link_id="L1",
                name="Interpretation method runs",
                evidence_strength=0.55,
                downstream_claim_strength=0.85,
                evidence_basis="SAE features extracted; patching reduces target behavior in 60% of test prompts",
                failure_mode_if_overstated="distribution shift from patching itself becomes the explanation",
            ),
            CertificationLink(
                link_id="L2",
                name="Interpretation claim asserted",
                evidence_strength=0.50,
                downstream_claim_strength=0.85,
                evidence_basis="features correlate with target concept on probe set",
                failure_mode_if_overstated="correlation is not causation; circuit may be epiphenomenal",
            ),
            CertificationLink(
                link_id="L3",
                name="Safety property derived",
                evidence_strength=0.40,
                downstream_claim_strength=0.85,
                evidence_basis="absence of identified circuit treated as absence of capability",
                failure_mode_if_overstated="absence of evidence treated as evidence of absence",
            ),
            CertificationLink(
                link_id="L4",
                name="Deployment certification issued",
                evidence_strength=0.85,
                downstream_claim_strength=0.85,
                evidence_basis="signed by 5 internal reviewers based on L3 claim",
                failure_mode_if_overstated="institutional signoff substitutes for evidence",
            ),
        ],
    )

    # Case B: same model, same interpretation method, but the chain
    # is operated as hypothesis rather than warranty. Rollback path
    # exists. In-field dissent documented. Independent replication
    # attempted. Downstream claims do not exceed upstream evidence.
    # This is what the parent module's RECOMMENDATION block describes.
    hypothesis_chain = CertificationChain(
        model_id="hypothetical-frontier-model-2026",
        interpretation_method="SAE feature attribution + activation patching",
        safety_property_claimed="hypothesis: deceptive-reasoning circuits not detected at scale tested",
        deployment_authority="staged release with monitoring + rollback",
        rollback_path_exists=True,
        in_field_dissent_documented=True,
        independent_replication_attempted=True,
        links=[
            CertificationLink(
                link_id="L1",
                name="Interpretation method runs",
                evidence_strength=0.55,
                downstream_claim_strength=0.50,
                evidence_basis="SAE features extracted; patching reduces target behavior in 60% of test prompts",
                failure_mode_if_overstated="distribution shift from patching itself becomes the explanation",
            ),
            CertificationLink(
                link_id="L2",
                name="Interpretation hypothesis asserted",
                evidence_strength=0.50,
                downstream_claim_strength=0.45,
                evidence_basis="features correlate with target concept on probe set",
                failure_mode_if_overstated="correlation is not causation; circuit may be epiphenomenal",
            ),
            CertificationLink(
                link_id="L3",
                name="Safety property described with scope",
                evidence_strength=0.40,
                downstream_claim_strength=0.40,
                evidence_basis="scope: held only across tested prompts + scale + checkpoint; not extrapolated",
                failure_mode_if_overstated="absence of evidence treated as evidence of absence",
            ),
            CertificationLink(
                link_id="L4",
                name="Staged release with monitoring",
                evidence_strength=0.40,
                downstream_claim_strength=0.40,
                evidence_basis="deployment treated as continuation of the experiment, not certification",
                failure_mode_if_overstated="staged release becomes de-facto warranty without monitoring teeth",
            ),
        ],
    )

    print("INTERPRETATION CERTIFICATION CHAIN AUDIT")
    print("=" * 70)

    for label, chain in [("CASE A: warranty mode", warranty_chain),
                         ("CASE B: hypothesis mode", hypothesis_chain)]:
        print(f"\n{label}")
        print(f"  Model: {chain.model_id}")
        print(f"  Method: {chain.interpretation_method}")
        print(f"  Property claimed: {chain.safety_property_claimed}")
        print(f"  Rollback path exists?         {chain.rollback_path_exists}")
        print(f"  In-field dissent documented?  {chain.in_field_dissent_documented}")
        print(f"  Independent replication?      {chain.independent_replication_attempted}")
        print(f"  Chain strength (product):     {chain.chain_strength():.3f}")
        print(f"  Confidence gap:               {chain.confidence_gap():+.3f}")
        weak = chain.weak_links()
        print(f"  Weak links: {[link.link_id for link in weak] if weak else 'none'}")
        print(f"  VERDICT: {chain.verdict()}")

    print("\n" + "=" * 70)
    print("STRUCTURAL FINDING:")
    print("Same model, same interpretation method, same evidence base.")
    print("Case A operates the chain as deployment warranty -> load-bearing")
    print("parallel to 1935 binds hard. Case B operates the same evidence")
    print("as hypothesis with scope + rollback + dissent -> parallel does")
    print("not bind. The interpretation work is not the failure mode. The")
    print("certification-claim chain is. That is the load-bearing axis to")
    print("audit, and it is the one that this module measures.")
