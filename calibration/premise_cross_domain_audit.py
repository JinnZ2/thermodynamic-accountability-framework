"""
premise_cross_domain_audit.py

Cross-domain premise tracing and repercussion analysis framework.

## Purpose

Detect:

1. Shared hidden premises across domains
2. Contradictions between domains
3. Premise propagation chains (forward and backward)
4. Repercussion cascades when a premise changes
5. Confidence-weighted fragility (high belief + weak evidence = danger)
6. Circular dependency chains

No external dependencies.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict, deque
import json


# ============================================================
# DATA STRUCTURES
# ============================================================

@dataclass
class Premise:
    premise_id: str
    statement: str
    confidence: float = 0.5          # how strongly believed
    evidence_strength: float = 0.5   # how well grounded in evidence
    source_domains: Set[str] = field(default_factory=set)
    tags: Set[str] = field(default_factory=set)

    def fragility(self) -> float:
        """
        High belief + weak evidence = maximum fragility.
        This is the danger-zone signal: premises people accept
        without grounding, which propagate widely before being checked.
        """
        return round(self.confidence * (1.0 - self.evidence_strength), 3)


@dataclass
class DomainClaim:
    domain: str
    claim_id: str
    statement: str
    depends_on: List[str] = field(default_factory=list)
    supports: List[str] = field(default_factory=list)
    contradicts: List[str] = field(default_factory=list)


@dataclass
class Repercussion:
    affected_domain: str
    affected_claim: str
    severity: float
    explanation: str


# ============================================================
# AUDIT ENGINE
# ============================================================

class PremiseAuditEngine:

    def __init__(self):
        self.premises: Dict[str, Premise] = {}
        self.claims: Dict[str, DomainClaim] = {}

        self.domain_index = defaultdict(list)
        self.premise_to_claims = defaultdict(list)

    # --------------------------------------------------------

    def add_premise(self, premise: Premise):
        self.premises[premise.premise_id] = premise

    # --------------------------------------------------------

    def add_claim(self, claim: DomainClaim):
        self.claims[claim.claim_id] = claim
        self.domain_index[claim.domain].append(claim.claim_id)

        for p in claim.depends_on:
            self.premise_to_claims[p].append(claim.claim_id)

    # --------------------------------------------------------

    def detect_cross_domain_premises(self) -> Dict[str, List[str]]:
        """
        Find premises used across multiple domains.
        """
        result = {}

        for premise_id, claim_ids in self.premise_to_claims.items():
            domains = sorted({
                self.claims[c].domain
                for c in claim_ids
                if c in self.claims
            })

            if len(domains) >= 2:
                result[premise_id] = domains

        return result

    # --------------------------------------------------------

    def detect_contradictions(self) -> List[Tuple[str, str]]:
        """
        Return claim contradiction pairs.
        """
        contradictions = []

        for claim_id, claim in self.claims.items():
            for other in claim.contradicts:
                if other in self.claims:
                    contradictions.append((claim_id, other))

        return contradictions

    # --------------------------------------------------------

    def premise_dependency_graph(self) -> Dict[str, List[str]]:
        """
        Build premise -> claims graph.
        """
        graph = defaultdict(list)

        for premise_id, claim_ids in self.premise_to_claims.items():
            graph[premise_id].extend(claim_ids)

        return dict(graph)

    # --------------------------------------------------------
    # FORWARD PROPAGATION (premise -> claims -> supported claims)
    # --------------------------------------------------------

    def propagate_premise_failure(
        self,
        failed_premise_id: str,
        decay: float = 0.85,
        use_confidence: bool = True
    ) -> List[Repercussion]:
        """
        Simulate systemic impact when a premise becomes invalid.

        If use_confidence is True, initial severity is weighted by
        the premise's fragility score (high confidence + low evidence
        produces highest severity, because such premises propagate
        widely before being validated).
        """
        repercussions = []

        visited = set()
        queue = deque()

        # Initial severity weighted by fragility
        if use_confidence and failed_premise_id in self.premises:
            premise = self.premises[failed_premise_id]
            # Use max(fragility, 0.1) so a well-evidenced premise still
            # cascades meaningfully if it does fail
            initial_severity = max(premise.fragility(), 0.1)
        else:
            initial_severity = 1.0

        queue.append((failed_premise_id, initial_severity))

        while queue:

            current, severity = queue.popleft()

            # Cycle guard
            if current in visited:
                continue

            visited.add(current)

            # premise -> claims
            if current in self.premise_to_claims:

                for claim_id in self.premise_to_claims[current]:

                    claim = self.claims[claim_id]

                    repercussions.append(
                        Repercussion(
                            affected_domain=claim.domain,
                            affected_claim=claim.statement,
                            severity=round(severity, 3),
                            explanation=(
                                f"Claim depends on failed premise "
                                f"'{failed_premise_id}'."
                            )
                        )
                    )

                    # propagate into supported claims
                    for next_claim in claim.supports:
                        queue.append((next_claim, severity * decay))

            # claim -> supported claims
            elif current in self.claims:

                claim = self.claims[current]

                for next_claim in claim.supports:
                    queue.append((next_claim, severity * decay))

        return sorted(
            repercussions,
            key=lambda r: r.severity,
            reverse=True
        )

    # --------------------------------------------------------
    # BACKWARD PROPAGATION (claim -> premises it inherited)
    # --------------------------------------------------------

    def find_root_premises(
        self,
        suspect_claim_id: str
    ) -> Dict[str, List[str]]:
        """
        Trace backward from a suspect claim to find all premises
        it ultimately depends on, plus the trace path.

        Use case: you observe a claim that contradicts lived data.
        This surfaces the hidden premises that produced it.

        Returns:
            {
                "premise_id": [path_of_claim_ids_back_to_premise],
                ...
            }
        """
        roots: Dict[str, List[str]] = {}
        visited: Set[str] = set()

        def trace(node_id: str, path: List[str]):

            if node_id in visited:
                return

            visited.add(node_id)

            # Hit a premise -> record path
            if node_id in self.premises:
                roots[node_id] = list(path)
                return

            # Walk back through claim dependencies
            if node_id in self.claims:
                claim = self.claims[node_id]

                for dep in claim.depends_on:
                    trace(dep, path + [node_id])

        trace(suspect_claim_id, [])

        return roots

    # --------------------------------------------------------

    def trace_contradiction_roots(self) -> List[Dict]:
        """
        For every contradiction pair, surface the root premises
        on each side. If the same premise appears on both sides,
        the contradiction is self-inflicted from a shared assumption.
        If different premises, the contradiction is between competing
        assumption frameworks.
        """
        results = []

        for a, b in self.detect_contradictions():

            roots_a = self.find_root_premises(a)
            roots_b = self.find_root_premises(b)

            shared = sorted(set(roots_a.keys()) & set(roots_b.keys()))
            only_a = sorted(set(roots_a.keys()) - set(roots_b.keys()))
            only_b = sorted(set(roots_b.keys()) - set(roots_a.keys()))

            results.append({
                "claim_a": a,
                "claim_b": b,
                "shared_premises": shared,
                "premises_only_in_a": only_a,
                "premises_only_in_b": only_b,
                "type": (
                    "self_inflicted" if shared and not (only_a or only_b)
                    else "framework_conflict" if (only_a and only_b)
                    else "asymmetric"
                )
            })

        return results

    # --------------------------------------------------------
    # CYCLE DETECTION
    # --------------------------------------------------------

    def detect_cycles(self) -> List[List[str]]:
        """
        Find circular dependency chains in the claim graph
        (claim -> supports -> ... -> back to claim).

        Uses iterative DFS with path tracking.
        """
        cycles: List[List[str]] = []
        seen_cycles: Set[Tuple[str, ...]] = set()

        def normalize(cycle: List[str]) -> Tuple[str, ...]:
            # Rotate so smallest element is first, for dedup
            if not cycle:
                return tuple()
            min_idx = cycle.index(min(cycle))
            rotated = cycle[min_idx:] + cycle[:min_idx]
            return tuple(rotated)

        for start in self.claims:

            stack: List[Tuple[str, List[str], Set[str]]] = [
                (start, [start], {start})
            ]

            while stack:

                node, path, on_path = stack.pop()

                claim = self.claims.get(node)
                if not claim:
                    continue

                for nxt in claim.supports:

                    if nxt in on_path:
                        # Cycle found - extract it
                        idx = path.index(nxt)
                        cycle = path[idx:]
                        key = normalize(cycle)

                        if key not in seen_cycles:
                            seen_cycles.add(key)
                            cycles.append(cycle)

                    elif nxt in self.claims:
                        new_on_path = on_path | {nxt}
                        stack.append(
                            (nxt, path + [nxt], new_on_path)
                        )

        return cycles

    # --------------------------------------------------------

    def hidden_assumption_density(self) -> Dict[str, float]:
        """
        Estimate how assumption-loaded each domain is.
        """
        scores = {}

        for domain, claim_ids in self.domain_index.items():

            total_dependencies = 0

            for claim_id in claim_ids:
                total_dependencies += len(
                    self.claims[claim_id].depends_on
                )

            if claim_ids:
                scores[domain] = round(
                    total_dependencies / len(claim_ids),
                    3
                )
            else:
                scores[domain] = 0.0

        return scores

    # --------------------------------------------------------

    def epistemic_fragility_report(self) -> Dict:

        cross_domain = self.detect_cross_domain_premises()

        fragility = []

        for premise_id, domains in cross_domain.items():

            premise = self.premises[premise_id]
            blast_radius = len(self.premise_to_claims[premise_id])

            # Risk is amplified by belief/evidence asymmetry
            base_risk = blast_radius * len(domains)
            weighted_risk = round(
                base_risk * (1 + premise.fragility()),
                3
            )

            fragility.append({
                "premise_id": premise_id,
                "statement": premise.statement,
                "domains": domains,
                "blast_radius": blast_radius,
                "confidence": premise.confidence,
                "evidence_strength": premise.evidence_strength,
                "fragility_score": premise.fragility(),
                "risk_score": weighted_risk
            })

        fragility.sort(
            key=lambda x: x["risk_score"],
            reverse=True
        )

        return {
            "cross_domain_premises": fragility,
            "contradictions": self.detect_contradictions(),
            "contradiction_roots": self.trace_contradiction_roots(),
            "domain_assumption_density":
                self.hidden_assumption_density(),
            "cycles": self.detect_cycles()
        }

    # --------------------------------------------------------

    def export_json(self) -> str:

        payload = {
            "premises": {
                k: {
                    "statement": v.statement,
                    "confidence": v.confidence,
                    "evidence_strength": v.evidence_strength,
                    "fragility": v.fragility(),
                    "source_domains": sorted(list(v.source_domains)),
                    "tags": sorted(list(v.tags)),
                }
                for k, v in self.premises.items()
            },
            "claims": {
                k: {
                    "domain": v.domain,
                    "statement": v.statement,
                    "depends_on": v.depends_on,
                    "supports": v.supports,
                    "contradicts": v.contradicts,
                }
                for k, v in self.claims.items()
            }
        }

        return json.dumps(payload, indent=2)


# ============================================================
# EXAMPLE
# ============================================================

def build_example_engine() -> PremiseAuditEngine:

    engine = PremiseAuditEngine()

    # --------------------------------------------------------
    # PREMISES
    # --------------------------------------------------------

    # High confidence, low evidence = high fragility
    engine.add_premise(
        Premise(
            premise_id="P1",
            statement=(
                "Male dominance behavior increases reproductive fitness."
            ),
            confidence=0.8,
            evidence_strength=0.45,
            source_domains={
                "evolutionary_psychology",
                "economics",
                "dating_culture",
            },
            tags={"dominance", "status", "reproduction"}
        )
    )

    # Moderate confidence, strong evidence = robust
    engine.add_premise(
        Premise(
            premise_id="P2",
            statement=(
                "Protective cooperative behavior improves long-term "
                "offspring survival."
            ),
            confidence=0.72,
            evidence_strength=0.8,
            source_domains={
                "anthropology",
                "developmental_psychology",
                "biology",
            },
            tags={"cooperation", "offspring", "protection"}
        )
    )

    # --------------------------------------------------------
    # CLAIMS
    # --------------------------------------------------------

    engine.add_claim(
        DomainClaim(
            domain="economics",
            claim_id="C1",
            statement=(
                "Competitive dominance produces optimal leadership."
            ),
            depends_on=["P1"],
            supports=["C3"]
        )
    )

    engine.add_claim(
        DomainClaim(
            domain="social_media",
            claim_id="C2",
            statement=(
                "Aggressive signaling increases male attractiveness."
            ),
            depends_on=["P1"],
            contradicts=["C4"]
        )
    )

    engine.add_claim(
        DomainClaim(
            domain="organizational_behavior",
            claim_id="C3",
            statement=(
                "High-pressure dominance cultures improve productivity."
            ),
            depends_on=["P1"]
        )
    )

    engine.add_claim(
        DomainClaim(
            domain="biology",
            claim_id="C4",
            statement=(
                "Chronic stress and aggression can reduce fertility."
            ),
            depends_on=["P2"],
            contradicts=["C2"]
        )
    )

    engine.add_claim(
        DomainClaim(
            domain="developmental_psychology",
            claim_id="C5",
            statement=(
                "Stable caregiving environments improve child outcomes."
            ),
            depends_on=["P2"]
        )
    )

    return engine


# ============================================================
# SELF TEST
# ============================================================

def _demo():

    engine = build_example_engine()

    print("=" * 70)
    print("CROSS DOMAIN PREMISES")
    print("=" * 70)

    cross = engine.detect_cross_domain_premises()

    for premise_id, domains in cross.items():
        print(f"{premise_id}: {domains}")

    print("\n" + "=" * 70)
    print("CONTRADICTIONS")
    print("=" * 70)

    for a, b in engine.detect_contradictions():
        print(f"{a} <-> {b}")

    print("\n" + "=" * 70)
    print("BACKWARD TRACE: roots of suspect claim C2")
    print("=" * 70)

    roots = engine.find_root_premises("C2")

    for premise_id, path in roots.items():
        print(f"{premise_id} via path: {path}")

    print("\n" + "=" * 70)
    print("CONTRADICTION ROOT ANALYSIS")
    print("=" * 70)

    for entry in engine.trace_contradiction_roots():
        print(json.dumps(entry, indent=2))

    print("\n" + "=" * 70)
    print("FRAGILITY REPORT")
    print("=" * 70)

    report = engine.epistemic_fragility_report()

    print(json.dumps(report, indent=2))

    print("\n" + "=" * 70)
    print("PREMISE FAILURE CASCADE (confidence-weighted)")
    print("=" * 70)

    cascade = engine.propagate_premise_failure("P1")

    for r in cascade:
        print(
            f"[{r.severity}] "
            f"{r.affected_domain} -> "
            f"{r.affected_claim}"
        )

    print("\n" + "=" * 70)
    print("CYCLE DETECTION")
    print("=" * 70)

    cycles = engine.detect_cycles()
    if cycles:
        for c in cycles:
            print(" -> ".join(c))
    else:
        print("No cycles detected.")

    print("\n" + "=" * 70)
    print("EXPORT")
    print("=" * 70)

    print(engine.export_json())


if __name__ == "__main__":
    _demo()
