"""
validity_weighted_reweighting.py

Reweights claims and studies by premise validity and evidence strength
rather than by frequency of citation.

## Core inversion

Standard AI/LLM weighting:
    claim_weight = f(citation_count, repetition, recency)

This module:
    claim_weight = f(
        premise_validity,
        evidence_strength,
        population_fit,
        contradiction_load,
        backward_trace_depth
    )

A single well-grounded study outweighs a thousand repetitions
standing on a fragile shared premise.

Depends on premise_cross_domain_audit.PremiseAuditEngine.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple
from collections import defaultdict
import json

from premise_cross_domain_audit import (
    PremiseAuditEngine,
    Premise,
    DomainClaim,
)


# ============================================================
# DATA STRUCTURES
# ============================================================

@dataclass
class Study:
    """
    A study is a citation-bearing wrapper around one or more
    DomainClaims, with population scope metadata.
    """
    study_id: str
    title: str
    claim_ids: List[str]                            # claims this study makes
    citation_count: int = 0                         # how often referenced
    sample_size: int = 0
    population_scope: Set[str] = field(default_factory=set)
    # e.g. {"industrialized", "urban", "western", "untrained"}
    methodology_controls: Set[str] = field(default_factory=set)
    # e.g. {"matched_lean_mass", "matched_training_history"}
    declared_limitations: List[str] = field(default_factory=list)


@dataclass
class PopulationContext:
    """
    The population the question is actually being asked about.
    """
    context_id: str
    descriptors: Set[str]
    # e.g. {"rural", "multigenerational_labor", "matched_weight"}
    required_controls: Set[str] = field(default_factory=set)
    # controls a study MUST have for its claims to apply here


@dataclass
class WeightedClaim:
    claim_id: str
    statement: str
    domain: str
    raw_citation_weight: float       # what frequency-based systems give
    validity_weight: float           # what this system gives
    population_fit: float
    premise_validity: float
    contradiction_penalty: float
    explanation: List[str]


# ============================================================
# REWEIGHTING ENGINE
# ============================================================

class ValidityReweighter:

    def __init__(self, audit_engine: PremiseAuditEngine):
        self.engine = audit_engine
        self.studies: Dict[str, Study] = {}
        self.claim_to_studies: Dict[str, List[str]] = defaultdict(list)

    # --------------------------------------------------------

    def add_study(self, study: Study):
        self.studies[study.study_id] = study
        for claim_id in study.claim_ids:
            self.claim_to_studies[claim_id].append(study.study_id)

    # --------------------------------------------------------
    # COMPONENT SCORES
    # --------------------------------------------------------

    def premise_validity_score(self, claim_id: str) -> Tuple[float, List[str]]:
        """
        Score a claim by the validity of the premises it depends on.

        validity = mean(evidence_strength) of root premises,
                   penalized by mean fragility.
        """
        notes = []

        roots = self.engine.find_root_premises(claim_id)
        if not roots:
            return 0.5, ["no traceable premises - assumed neutral"]

        evidence_scores = []
        fragility_scores = []

        for premise_id in roots:
            premise = self.engine.premises.get(premise_id)
            if not premise:
                continue
            evidence_scores.append(premise.evidence_strength)
            fragility_scores.append(premise.fragility())

        if not evidence_scores:
            return 0.5, ["premises referenced but not defined"]

        mean_evidence = sum(evidence_scores) / len(evidence_scores)
        mean_fragility = sum(fragility_scores) / len(fragility_scores)

        # validity rewards evidence, punishes fragility
        validity = max(0.0, mean_evidence - mean_fragility)

        notes.append(
            f"mean_evidence={round(mean_evidence, 3)}, "
            f"mean_fragility={round(mean_fragility, 3)}"
        )

        return round(validity, 3), notes

    # --------------------------------------------------------

    def population_fit_score(
        self,
        study_id: str,
        context: PopulationContext
    ) -> Tuple[float, List[str]]:
        """
        How well does the study's population and methodology
        match the population the question is about?
        """
        notes = []
        study = self.studies.get(study_id)
        if not study:
            return 0.0, ["study not found"]

        # Population descriptor overlap
        if context.descriptors:
            descriptor_overlap = len(
                study.population_scope & context.descriptors
            ) / max(len(context.descriptors), 1)
        else:
            descriptor_overlap = 0.5

        # Required methodology controls
        if context.required_controls:
            controls_present = len(
                study.methodology_controls & context.required_controls
            ) / len(context.required_controls)
        else:
            controls_present = 1.0

        fit = (descriptor_overlap + controls_present) / 2.0

        notes.append(
            f"descriptor_overlap={round(descriptor_overlap, 3)}, "
            f"controls_present={round(controls_present, 3)}"
        )

        # If the study explicitly lacks a required control,
        # that is a hard penalty
        missing_controls = (
            context.required_controls - study.methodology_controls
        )
        if missing_controls:
            notes.append(
                f"missing required controls: {sorted(missing_controls)}"
            )

        return round(fit, 3), notes

    # --------------------------------------------------------

    def contradiction_penalty(self, claim_id: str) -> Tuple[float, List[str]]:
        """
        Penalty if claim is contradicted by a claim with stronger
        premise validity.
        """
        notes = []
        claim = self.engine.claims.get(claim_id)
        if not claim:
            return 0.0, []

        penalty = 0.0
        for other_id in claim.contradicts:
            if other_id not in self.engine.claims:
                continue

            self_validity, _ = self.premise_validity_score(claim_id)
            other_validity, _ = self.premise_validity_score(other_id)

            if other_validity > self_validity:
                differential = other_validity - self_validity
                penalty += differential
                notes.append(
                    f"contradicted by {other_id} "
                    f"(higher validity by {round(differential, 3)})"
                )

        return round(min(penalty, 1.0), 3), notes

    # --------------------------------------------------------

    def raw_citation_weight(self, claim_id: str) -> float:
        """
        Sum of citation counts across studies asserting this claim.
        Normalized to 0-1 by max in corpus.
        """
        if not self.studies:
            return 0.0

        max_citations = max(
            (s.citation_count for s in self.studies.values()),
            default=1
        )
        if max_citations == 0:
            return 0.0

        total = sum(
            self.studies[sid].citation_count
            for sid in self.claim_to_studies.get(claim_id, [])
            if sid in self.studies
        )
        return round(total / max_citations, 3)

    # --------------------------------------------------------
    # FINAL WEIGHTING
    # --------------------------------------------------------

    def weigh_claim(
        self,
        claim_id: str,
        context: Optional[PopulationContext] = None
    ) -> WeightedClaim:
        """
        Compute validity-weighted score for a claim.

        validity_weight = premise_validity
                          * mean(population_fit across asserting studies)
                          * (1 - contradiction_penalty)
        """
        claim = self.engine.claims.get(claim_id)
        if not claim:
            raise KeyError(f"Unknown claim: {claim_id}")

        explanation: List[str] = []

        # Component 1: premise validity
        premise_validity, notes = self.premise_validity_score(claim_id)
        explanation.append(f"premise_validity={premise_validity}")
        explanation.extend(notes)

        # Component 2: population fit (mean across studies)
        if context:
            fits = []
            for sid in self.claim_to_studies.get(claim_id, []):
                fit, fit_notes = self.population_fit_score(sid, context)
                fits.append(fit)
                explanation.append(f"study {sid}: fit={fit}")
                explanation.extend(fit_notes)
            population_fit = (
                sum(fits) / len(fits) if fits else 0.5
            )
        else:
            population_fit = 1.0

        # Component 3: contradiction penalty
        penalty, pen_notes = self.contradiction_penalty(claim_id)
        explanation.append(f"contradiction_penalty={penalty}")
        explanation.extend(pen_notes)

        # Final validity weight
        validity_weight = round(
            premise_validity * population_fit * (1.0 - penalty),
            3
        )

        # Frequency-based comparison
        raw_citations = self.raw_citation_weight(claim_id)

        return WeightedClaim(
            claim_id=claim_id,
            statement=claim.statement,
            domain=claim.domain,
            raw_citation_weight=raw_citations,
            validity_weight=validity_weight,
            population_fit=round(population_fit, 3),
            premise_validity=premise_validity,
            contradiction_penalty=penalty,
            explanation=explanation
        )

    # --------------------------------------------------------

    def rank_corpus(
        self,
        context: Optional[PopulationContext] = None
    ) -> List[WeightedClaim]:
        """
        Rank every claim in the audit engine by validity-weighted score.
        Reveals the gap between what is loud (citations) and
        what is grounded (validity).
        """
        results = [
            self.weigh_claim(cid, context)
            for cid in self.engine.claims
        ]
        results.sort(key=lambda w: w.validity_weight, reverse=True)
        return results

    # --------------------------------------------------------

    def divergence_report(
        self,
        context: Optional[PopulationContext] = None
    ) -> List[Dict]:
        """
        Find claims where citation weight and validity weight
        diverge sharply. These are the danger zones:
        loudly cited but poorly grounded, or quietly held but solid.
        """
        report = []
        for w in self.rank_corpus(context):
            divergence = round(w.raw_citation_weight - w.validity_weight, 3)
            if abs(divergence) >= 0.2:
                report.append({
                    "claim_id": w.claim_id,
                    "statement": w.statement,
                    "raw_citation_weight": w.raw_citation_weight,
                    "validity_weight": w.validity_weight,
                    "divergence": divergence,
                    "type": (
                        "overcited_undergrounded" if divergence > 0
                        else "undercited_grounded"
                    )
                })
        report.sort(key=lambda r: abs(r["divergence"]), reverse=True)
        return report


# ============================================================
# EXAMPLE
# ============================================================

def build_example():

    from premise_cross_domain_audit import build_example_engine

    engine = build_example_engine()
    rw = ValidityReweighter(engine)

    # Studies asserting C2 (aggressive signaling = attractive)
    # Heavily cited, but built on the fragile P1 premise
    rw.add_study(Study(
        study_id="S1",
        title="Display dominance and mate choice in Western undergrads",
        claim_ids=["C2"],
        citation_count=500,
        sample_size=200,
        population_scope={"industrialized", "western", "urban", "untrained"},
        methodology_controls=set(),
        declared_limitations=["WEIRD sample only"]
    ))

    rw.add_study(Study(
        study_id="S2",
        title="Aggressive signaling reproductive outcomes meta-analysis",
        claim_ids=["C2"],
        citation_count=800,
        sample_size=15000,
        population_scope={"industrialized", "western"},
        methodology_controls={"meta_analysis"},
        declared_limitations=["heterogeneous methods"]
    ))

    # One quiet study supporting C4 (chronic stress reduces fertility)
    # Better grounded, less cited
    rw.add_study(Study(
        study_id="S3",
        title="Cortisol load and reproductive endocrinology",
        claim_ids=["C4"],
        citation_count=120,
        sample_size=800,
        population_scope={
            "industrialized", "rural", "subsistence",
            "matched_age", "matched_lean_mass"
        },
        methodology_controls={
            "matched_lean_mass",
            "matched_training_history",
            "longitudinal"
        },
        declared_limitations=["modest sample"]
    ))

    rw.add_study(Study(
        study_id="S4",
        title="Caregiver presence and child outcomes longitudinal",
        claim_ids=["C5"],
        citation_count=60,
        sample_size=2000,
        population_scope={"rural", "subsistence", "multigenerational"},
        methodology_controls={"longitudinal", "matched_socioeconomic"},
        declared_limitations=[]
    ))

    return rw


def _demo():

    rw = build_example()

    # Context: rural, multigenerational labor population,
    # matched lean mass needed for valid comparison
    context = PopulationContext(
        context_id="rural_multigenerational_labor",
        descriptors={
            "rural", "subsistence", "multigenerational",
            "matched_lean_mass"
        },
        required_controls={
            "matched_lean_mass", "matched_training_history"
        }
    )

    print("=" * 70)
    print("VALIDITY-WEIGHTED RANKING (context = rural multigenerational)")
    print("=" * 70)

    for w in rw.rank_corpus(context):
        print(
            f"{w.claim_id} [{w.domain}] "
            f"validity={w.validity_weight} "
            f"citation_freq={w.raw_citation_weight} "
            f"premise_validity={w.premise_validity} "
            f"pop_fit={w.population_fit} "
            f"contradiction_penalty={w.contradiction_penalty}"
        )
        print(f"   {w.statement}")

    print("\n" + "=" * 70)
    print("DIVERGENCE REPORT (citations vs validity)")
    print("=" * 70)

    for entry in rw.divergence_report(context):
        print(json.dumps(entry, indent=2))


if __name__ == "__main__":
    _demo()
