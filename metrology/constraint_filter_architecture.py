"""
constraint_filter_architecture.py

Sort models, frameworks, and regulations into containers by their
upstream premise failures. Backproject and forward-project to see
how a corrupted axiom cascades across domains.

## Premise

Most domain models do not fail at the equation level. They fail at
the premise level -- the unstated assumptions inherited from the
audit they were built on. Sorting models by *failure signature*
rather than by domain reveals which axioms are most systemically
corrupt. The kaleidoscope view: geometry of how false premises
pull on each other across domains.

## Linkage

Pairs with core/timing_as_constraint.py (thermodynamic scope) and
substrate_audit / calibration_audit modules. Failure signatures
detected here are the upstream cause of the metrology gap those
modules diagnose downstream.

License: CC0
Stdlib only.
"""

from dataclasses import dataclass, field
from collections import defaultdict
from typing import Callable


# =============================================================================
# 1. Premise: an axiom a model implicitly or explicitly relies on
# =============================================================================

@dataclass
class Premise:
    """
    A named axiom. Has a test function that returns True if the
    model carries this premise (i.e. depends on it being true).
    """
    id: str
    description: str
    detect: Callable[["Model"], bool]
    falsity_severity: float = 1.0   # weight: how corrupting is this premise

    def __hash__(self) -> int:
        return hash(self.id)


# =============================================================================
# 2. Model: any framework, regulation, equation set, or theory
# =============================================================================

@dataclass
class Model:
    id: str
    domain: str                        # e.g. "building_codes", "economics"
    description: str
    declared_assumptions: set[str] = field(default_factory=set)
    has_scope: bool = False
    has_timing_layer: bool = False
    has_diagnostic_cycles: bool = False
    treats_substrate_as_static: bool = True
    treats_time_as_externality: bool = True
    permanence_assumed: bool = True
    units_grounded_in_physics: bool = False
    extra: dict = field(default_factory=dict)


# =============================================================================
# 3. Built-in premise filters (extensible -- not exhaustive)
# =============================================================================

def _no_scope(m: Model) -> bool:
    return not m.has_scope


def _no_timing(m: Model) -> bool:
    return not m.has_timing_layer


def _no_cycles(m: Model) -> bool:
    return not m.has_diagnostic_cycles


def _static_substrate(m: Model) -> bool:
    return m.treats_substrate_as_static


def _time_as_externality(m: Model) -> bool:
    return m.treats_time_as_externality


def _permanence_assumed(m: Model) -> bool:
    return m.permanence_assumed


def _units_ungrounded(m: Model) -> bool:
    return not m.units_grounded_in_physics


DEFAULT_PREMISES = [
    Premise(
        "permanence",
        "Assumes permanent / static system state.",
        _permanence_assumed,
        2.0,
    ),
    Premise(
        "no_scope",
        "No declared operational scope.",
        _no_scope,
        1.5,
    ),
    Premise(
        "no_timing_layer",
        "Time stripped from the model.",
        _no_timing,
        2.0,
    ),
    Premise(
        "no_diagnostic_cycles",
        "No measurement cycles; failure invisible until catastrophic.",
        _no_cycles,
        1.5,
    ),
    Premise(
        "static_substrate",
        "Treats substrate (ground, market, ecosystem) as fixed.",
        _static_substrate,
        1.25,
    ),
    Premise(
        "time_as_externality",
        "Time treated as overhead, not constraint.",
        _time_as_externality,
        1.5,
    ),
    Premise(
        "ungrounded_units",
        "Measurement units not validated against physical quantities.",
        _units_ungrounded,
        2.0,
    ),
]


# =============================================================================
# 4. Filter: run a model through a premise-set, return its failure signature
# =============================================================================

def signature(model: Model, premises: list[Premise]) -> frozenset[str]:
    """A model's failure signature is the set of corrupt premises it carries."""
    return frozenset(p.id for p in premises if p.detect(model))


def severity(sig: frozenset[str], premises: list[Premise]) -> float:
    pmap = {p.id: p.falsity_severity for p in premises}
    return sum(pmap.get(pid, 1.0) for pid in sig)


# =============================================================================
# 5. Sort: bucket models by signature
# =============================================================================

def bucket_by_signature(
    models: list[Model],
    premises: list[Premise],
) -> dict[frozenset[str], list[Model]]:
    buckets: dict[frozenset[str], list[Model]] = defaultdict(list)
    for m in models:
        buckets[signature(m, premises)].append(m)
    return dict(buckets)


def bucket_by_single_premise(
    models: list[Model],
    premises: list[Premise],
) -> dict[str, list[Model]]:
    """One bucket per premise; a model can appear in multiple buckets."""
    buckets: dict[str, list[Model]] = defaultdict(list)
    for m in models:
        for p in premises:
            if p.detect(m):
                buckets[p.id].append(m)
    return dict(buckets)


# =============================================================================
# 6. Cascade map: which domains share which premise failures
# =============================================================================

def domain_cascade(
    models: list[Model],
    premises: list[Premise],
) -> dict[str, set[str]]:
    """
    For each premise, list the set of domains it has propagated into.
    A premise touching many domains = systemic corruption,
    not a local domain bug.
    """
    cascade: dict[str, set[str]] = defaultdict(set)
    for m in models:
        for p in premises:
            if p.detect(m):
                cascade[p.id].add(m.domain)
    return {k: v for k, v in cascade.items()}


# =============================================================================
# 7. Geometry: resonance pairs (premises that co-occur)
# =============================================================================

def co_occurrence_matrix(
    models: list[Model],
    premises: list[Premise],
) -> dict[tuple[str, str], int]:
    """
    Count pairs of premises that appear together in the same model.
    High co-occurrence = resonance -- these axioms travel together
    and likely share an upstream source.
    """
    pairs: dict[tuple[str, str], int] = defaultdict(int)
    pids = [p.id for p in premises]
    for m in models:
        sig = signature(m, premises)
        present = [pid for pid in pids if pid in sig]
        for i in range(len(present)):
            for j in range(i + 1, len(present)):
                key = tuple(sorted((present[i], present[j])))
                pairs[key] += 1
    return dict(pairs)


# =============================================================================
# 8. Backproject: given a corrupt premise, find candidate origin domains
# =============================================================================

def backproject_origin(
    premise_id: str,
    models: list[Model],
    premises: list[Premise],
    origin_hint: dict[str, str] | None = None,
) -> dict:
    """
    Find earliest / most-pervasive carrier of a premise.
    origin_hint maps domain -> approx origin year, if known.
    """
    carriers = [
        m for m in models
        if any(p.id == premise_id and p.detect(m) for p in premises)
    ]
    domains = sorted({m.domain for m in carriers})
    earliest_domain = None
    if origin_hint:
        dated = [(d, origin_hint[d]) for d in domains if d in origin_hint]
        if dated:
            earliest_domain = min(dated, key=lambda x: x[1])[0]
    return {
        "premise": premise_id,
        "n_carrying_models": len(carriers),
        "domains_affected": domains,
        "earliest_domain": earliest_domain,
    }


# =============================================================================
# 9. Forward project: given a premise, predict next domains likely to fail
# =============================================================================

def forward_predict(
    premise_id: str,
    cascade: dict[str, set[str]],
    candidate_domains: list[str],
) -> list[str]:
    """
    Domains not yet observed carrying the premise but adjacent to
    domains that do. Pure structural projection -- co-occurrence
    of premise across many domains suggests systemic axiom transfer
    and the candidate list is at risk.
    """
    affected = cascade.get(premise_id, set())
    if not affected:
        return []
    # Heuristic: any candidate not yet in `affected` is at-risk
    return [d for d in candidate_domains if d not in affected]


# =============================================================================
# 10. Falsifiable claims
# =============================================================================

CLAIMS = [
    "Models sharing a failure signature share an upstream premise; sort by signature, not by domain.",
    "Premise co-occurrence across domains is non-random; high co-occurrence pairs travel together because they share an audit origin.",
    "A premise touching N domains with N large is systemic, not local; fixing individual models cannot resolve it.",
    "Backprojection from premise to earliest carrying domain is a candidate origin, not a proof.",
    "Forward prediction is structural, not statistical: domains adjacent to carriers are at risk.",
    "Severity-weighted signatures order models by audit corruption, independent of domain prestige.",
    "Two models with identical equations but different premises produce different physics over time.",
]


# =============================================================================
# 11. Demo: small corpus of models across domains
# =============================================================================

if __name__ == "__main__":
    corpus = [
        Model(
            id="india_nbc_1970",
            domain="building_codes",
            description="National Building Code 1970 (India), legacy",
            has_scope=False, has_timing_layer=False, has_diagnostic_cycles=False,
            treats_substrate_as_static=True, treats_time_as_externality=True,
            permanence_assumed=True, units_grounded_in_physics=True,
        ),
        Model(
            id="us_ibc_legacy",
            domain="building_codes",
            description="US International Building Code, legacy assumptions",
            has_scope=False, has_timing_layer=False, has_diagnostic_cycles=False,
            treats_substrate_as_static=True, treats_time_as_externality=True,
            permanence_assumed=True, units_grounded_in_physics=True,
        ),
        Model(
            id="dsge_macro",
            domain="economics",
            description="DSGE macroeconomic models",
            has_scope=False, has_timing_layer=True, has_diagnostic_cycles=False,
            treats_substrate_as_static=True, treats_time_as_externality=False,
            permanence_assumed=True, units_grounded_in_physics=False,
        ),
        Model(
            id="ipcc_baseline",
            domain="climate",
            description="Climate baseline regime (Holocene assumption)",
            has_scope=True, has_timing_layer=True, has_diagnostic_cycles=True,
            treats_substrate_as_static=False, treats_time_as_externality=False,
            permanence_assumed=True, units_grounded_in_physics=True,
        ),
        Model(
            id="industrial_ag_yield",
            domain="agriculture",
            description="Industrial agricultural yield model",
            has_scope=False, has_timing_layer=False, has_diagnostic_cycles=False,
            treats_substrate_as_static=True, treats_time_as_externality=True,
            permanence_assumed=True, units_grounded_in_physics=False,
        ),
        Model(
            id="industrial_workforce_cert",
            domain="labor",
            description="Certification-signal-as-capacity workforce model",
            has_scope=False, has_timing_layer=False, has_diagnostic_cycles=False,
            treats_substrate_as_static=True, treats_time_as_externality=True,
            permanence_assumed=True, units_grounded_in_physics=False,
        ),
        Model(
            id="nomadic_floating_structure",
            domain="indigenous_engineering",
            description="Floating structures on permafrost / rising water (validated)",
            has_scope=True, has_timing_layer=True, has_diagnostic_cycles=True,
            treats_substrate_as_static=False, treats_time_as_externality=False,
            permanence_assumed=False, units_grounded_in_physics=True,
        ),
    ]

    sigs = {m.id: signature(m, DEFAULT_PREMISES) for m in corpus}
    sevs = {m.id: severity(sigs[m.id], DEFAULT_PREMISES) for m in corpus}
    print("== Failure signatures ==")
    for mid, sig in sigs.items():
        print(f"  {mid:35s} severity={sevs[mid]:>4.2f}  {sorted(sig)}")

    print("\n== Buckets by full signature ==")
    for sig, models in bucket_by_signature(corpus, DEFAULT_PREMISES).items():
        print(f"  {sorted(sig)} -> {[m.id for m in models]}")

    print("\n== Cascade: premise -> domains affected ==")
    cascade = domain_cascade(corpus, DEFAULT_PREMISES)
    for pid, domains in sorted(cascade.items()):
        print(f"  {pid:25s} domains={sorted(domains)}")

    print("\n== Co-occurrence (premise resonance) ==")
    pairs = co_occurrence_matrix(corpus, DEFAULT_PREMISES)
    for (a, b), n in sorted(pairs.items(), key=lambda x: -x[1])[:8]:
        print(f"  {a} <-> {b}: {n}")

    print("\n== Backproject 'permanence' ==")
    bp = backproject_origin(
        "permanence", corpus, DEFAULT_PREMISES,
        origin_hint={
            "building_codes": 1900, "economics": 1970, "agriculture": 1945,
            "labor": 1950, "climate": 1990,
        },
    )
    print(f"  {bp}")

    print("\n== Forward predict 'permanence' risk ==")
    candidates = [
        "urban_planning", "insurance", "infrastructure_investment",
        "ecological_forecasting", "education",
    ]
    risk = forward_predict("permanence", cascade, candidates)
    print(f"  at-risk_domains={risk}")
