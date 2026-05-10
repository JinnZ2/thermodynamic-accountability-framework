"""
institutional_audit.py

Cross-domain audit of institutional models against the full premise
set, including the performance-over-function premises that historically
precede civilizational collapse.

## Premise

Run a wide corpus of institutional, economic, ecological, and
governance models through the constraint filter. Bucket by failure
signature. Detect the collapse signature -- the specific premise
combination present in historical pre-collapse civilizations
(Rapa Nui, late Rome, others carried in oral histories).

## Linkage

Extends metrology/constraint_filter_architecture.py with three new
institutional premises:

  - performance_over_function     (pays for role, not load-bearing work)
  - appearance_over_audit         (rating > underlying state)
  - hidden_load_bearing           (actual centrality != declared centrality)
  - self_referential              (validates against own rules, not reality)

These detect when a system pays for the performance of a role
rather than the actual load-bearing work, and when appearance has
replaced diagnostic measurement.

License: CC0
Stdlib only.
"""

from dataclasses import dataclass
from collections import defaultdict
from typing import Callable


# =============================================================================
# 1. Model schema (extends the base from constraint_filter_architecture)
# =============================================================================

@dataclass
class Model:
    id: str
    domain: str
    description: str

    # base premises
    has_scope: bool = False
    has_timing_layer: bool = False
    has_diagnostic_cycles: bool = False
    treats_substrate_as_static: bool = True
    treats_time_as_externality: bool = True
    permanence_assumed: bool = True
    units_grounded_in_physics: bool = False

    # new institutional premises
    pays_for_role_not_function: bool = False    # CEO paid for title, secretary does load
    appearance_replaces_audit: bool = False     # rating > underlying state
    hides_load_bearing_node: bool = False       # actual centrality != declared centrality
    self_referential_validation: bool = False   # validates against own rules, not reality


# =============================================================================
# 2. Premise definitions
# =============================================================================

@dataclass
class Premise:
    id: str
    description: str
    detect: Callable[[Model], bool]
    severity: float = 1.0

    def __hash__(self) -> int:
        return hash(self.id)


PREMISES = [
    Premise("permanence",
            "Assumes static / permanent system state.",
            lambda m: m.permanence_assumed,
            2.0),
    Premise("no_scope",
            "No declared operational envelope.",
            lambda m: not m.has_scope,
            1.5),
    Premise("no_timing_layer",
            "Time stripped from the model.",
            lambda m: not m.has_timing_layer,
            2.0),
    Premise("no_diagnostic_cycles",
            "No measurement cycles; failure invisible until catastrophic.",
            lambda m: not m.has_diagnostic_cycles,
            1.5),
    Premise("static_substrate",
            "Treats substrate (ground, market, ecosystem) as fixed.",
            lambda m: m.treats_substrate_as_static,
            1.25),
    Premise("time_as_externality",
            "Time treated as overhead, not constraint.",
            lambda m: m.treats_time_as_externality,
            1.5),
    Premise("ungrounded_units",
            "Units not validated against physical quantities.",
            lambda m: not m.units_grounded_in_physics,
            2.0),
    Premise("performance_over_function",
            "Pays for role-performance, not load-bearing work.",
            lambda m: m.pays_for_role_not_function,
            2.5),
    Premise("appearance_over_audit",
            "Appearance / rating substitutes for diagnostic.",
            lambda m: m.appearance_replaces_audit,
            2.5),
    Premise("hidden_load_bearing",
            "Actual centrality differs from declared centrality.",
            lambda m: m.hides_load_bearing_node,
            2.0),
    Premise("self_referential",
            "Validates against own rules, not external reality.",
            lambda m: m.self_referential_validation,
            2.0),
]


# =============================================================================
# 3. Filter operations
# =============================================================================

def signature(m: Model, premises: list[Premise] = PREMISES) -> frozenset[str]:
    return frozenset(p.id for p in premises if p.detect(m))


def severity(m: Model, premises: list[Premise] = PREMISES) -> float:
    sig = signature(m, premises)
    smap = {p.id: p.severity for p in premises}
    return sum(smap[pid] for pid in sig)


def bucket_by_signature(models: list[Model]) -> dict[frozenset[str], list[Model]]:
    buckets = defaultdict(list)
    for m in models:
        buckets[signature(m)].append(m)
    return dict(buckets)


def domain_cascade(models: list[Model]) -> dict[str, set[str]]:
    cascade = defaultdict(set)
    for m in models:
        for pid in signature(m):
            cascade[pid].add(m.domain)
    return dict(cascade)


def co_occurrence(models: list[Model]) -> dict[tuple[str, str], int]:
    pairs = defaultdict(int)
    for m in models:
        sig = sorted(signature(m))
        for i in range(len(sig)):
            for j in range(i + 1, len(sig)):
                pairs[(sig[i], sig[j])] += 1
    return dict(pairs)


# =============================================================================
# 4. Collapse signature detection
# =============================================================================
# The historical pattern: late-stage Rapa Nui, late Rome, many others.
# When all four of these premises are present in a system's institutional
# stack, energy flows into appearance maintenance and the substrate is
# no longer audited. Failure becomes catastrophic, not gradual.

COLLAPSE_SIGNATURE = frozenset({
    "permanence",
    "performance_over_function",
    "appearance_over_audit",
    "no_diagnostic_cycles",
})


def carries_collapse_signature(m: Model) -> bool:
    return COLLAPSE_SIGNATURE.issubset(signature(m))


def collapse_carriers(models: list[Model]) -> list[Model]:
    return [m for m in models if carries_collapse_signature(m)]


# =============================================================================
# 5. Domain risk density
# =============================================================================

def domain_risk_density(models: list[Model]) -> dict[str, dict]:
    """Per-domain average severity and collapse-carrier fraction."""
    by_domain = defaultdict(list)
    for m in models:
        by_domain[m.domain].append(m)
    result = {}
    for domain, ms in by_domain.items():
        sevs = [severity(m) for m in ms]
        carriers = sum(1 for m in ms if carries_collapse_signature(m))
        result[domain] = {
            "n_models": len(ms),
            "mean_severity": sum(sevs) / len(sevs),
            "max_severity": max(sevs),
            "collapse_fraction": carriers / len(ms),
        }
    return result


# =============================================================================
# 6. Falsifiable claims
# =============================================================================

CLAIMS = [
    "When permanence + performance_over_function + appearance_over_audit + no_diagnostic_cycles all co-occur, the system is in pre-collapse configuration.",
    "Hidden load-bearing nodes exist in every system that pays for role-performance instead of function; the secretary problem.",
    "Domains with high mean severity and high collapse-fraction are at-risk independent of their internal metrics.",
    "Self-referential validation is a metrology failure: the system measures itself by its own rules, not against external reality.",
    "Pre-collapse civilizations and modern institutional systems share signature, not domain.",
    "Forward prediction: domains adjacent to current collapse-carriers will inherit the signature unless premises are corrected upstream.",
]


# =============================================================================
# 7. Cross-domain corpus
# =============================================================================

def build_corpus() -> list[Model]:
    return [
        # ===== FINANCE =====
        Model("credit_rating_system", "finance",
              "Agency-issued scores; appearance replaces continuous audit",
              has_scope=False, has_timing_layer=False, has_diagnostic_cycles=False,
              units_grounded_in_physics=False,
              pays_for_role_not_function=True, appearance_replaces_audit=True,
              hides_load_bearing_node=True, self_referential_validation=True),

        Model("fiat_currency_baseline", "finance",
              "Abstract value units; not validated against physical quantities",
              has_scope=False, units_grounded_in_physics=False,
              appearance_replaces_audit=True, self_referential_validation=True),

        Model("quarterly_earnings", "finance",
              "Short-cycle performance signal; hides long-horizon substrate decay",
              has_timing_layer=True, has_diagnostic_cycles=False,
              treats_time_as_externality=False,
              pays_for_role_not_function=True, appearance_replaces_audit=True),

        Model("stock_buyback_logic", "finance",
              "Buybacks valorized over R&D; performance signal over function",
              pays_for_role_not_function=True, appearance_replaces_audit=True,
              hides_load_bearing_node=True),

        # ===== INFRASTRUCTURE =====
        Model("legacy_building_code", "infrastructure",
              "Permanence assumed; no scope; no diagnostic cycles",
              units_grounded_in_physics=True),

        Model("bridge_inspection_ritual", "infrastructure",
              "Periodic inspection without continuous diagnostic; appearance of safety",
              has_timing_layer=True, units_grounded_in_physics=True,
              appearance_replaces_audit=True),

        Model("deferred_maintenance_logic", "infrastructure",
              "Treats maintenance as cost; appearance preserved until failure",
              units_grounded_in_physics=True,
              appearance_replaces_audit=True),

        # ===== EDUCATION =====
        Model("standardized_testing", "education",
              "Grade as performance signal; metric valorized over learning",
              pays_for_role_not_function=True, appearance_replaces_audit=True,
              self_referential_validation=True),

        Model("credential_hierarchy", "education",
              "Degree as permanence marker; no scope for skill obsolescence",
              pays_for_role_not_function=True, appearance_replaces_audit=True),

        Model("classroom_rank", "education",
              "Prestige sorting; hides actual load-bearing (support staff)",
              pays_for_role_not_function=True, hides_load_bearing_node=True),

        # ===== HEALTHCARE =====
        Model("medical_credential", "healthcare",
              "Certification without continuous audit; appearance of competence",
              has_diagnostic_cycles=False,
              appearance_replaces_audit=True, pays_for_role_not_function=True),

        Model("insurance_actuarial", "healthcare",
              "Actuarial scoring; appearance of precision; ungrounded units",
              has_timing_layer=True, units_grounded_in_physics=False,
              appearance_replaces_audit=True, self_referential_validation=True),

        Model("hospital_hierarchy", "healthcare",
              "Physician at apex; nurses carry load; hidden load-bearing",
              pays_for_role_not_function=True, hides_load_bearing_node=True,
              units_grounded_in_physics=True),

        # ===== ECOLOGY =====
        Model("carbon_credit", "ecology",
              "Abstract units divorced from sequestration; appearance over audit",
              units_grounded_in_physics=False,
              appearance_replaces_audit=True, self_referential_validation=True),

        Model("species_count_metric", "ecology",
              "Snapshot grades; no diagnostic cycle for population dynamics",
              has_timing_layer=False, has_diagnostic_cycles=False,
              units_grounded_in_physics=True,
              appearance_replaces_audit=True),

        Model("holocene_stability_assumption", "ecology",
              "Assumes regime permanence; no scope for regime shifts",
              has_scope=False, units_grounded_in_physics=True),

        # ===== GOVERNANCE =====
        Model("hierarchical_bureaucracy", "governance",
              "Permanence; hidden load (admin staff); role-locked",
              pays_for_role_not_function=True, hides_load_bearing_node=True,
              self_referential_validation=True),

        Model("election_cycle", "governance",
              "Performance valorized every 4 yrs; no scope for long substrate",
              has_timing_layer=True, has_diagnostic_cycles=False,
              treats_time_as_externality=False,
              pays_for_role_not_function=True, appearance_replaces_audit=True),

        Model("budget_ritual", "governance",
              "Annual cycles; appearance of planning; no diagnostic of need",
              has_timing_layer=True, treats_time_as_externality=False,
              appearance_replaces_audit=True, self_referential_validation=True),

        # ===== CORPORATE =====
        Model("ceo_apex_hierarchy", "corporate",
              "Permanence; hidden load (secretary); performance valorized",
              pays_for_role_not_function=True, hides_load_bearing_node=True,
              appearance_replaces_audit=True, self_referential_validation=True),

        Model("quarterly_targets", "corporate",
              "Short-term performance signal; time as externality at horizon",
              has_timing_layer=True, has_diagnostic_cycles=False,
              treats_time_as_externality=False,
              pays_for_role_not_function=True, appearance_replaces_audit=True),

        Model("performance_review", "corporate",
              "Grade individuals by prestige; hides actual contribution",
              pays_for_role_not_function=True, hides_load_bearing_node=True,
              appearance_replaces_audit=True),

        # ===== AGRICULTURE =====
        Model("industrial_monoculture", "agriculture",
              "Permanence of approach; no scope for soil depletion",
              units_grounded_in_physics=False,
              appearance_replaces_audit=True),

        Model("pesticide_certification", "agriculture",
              "Appearance of safety; no long-term diagnostic cycles",
              units_grounded_in_physics=True,
              appearance_replaces_audit=True),

        # ===== RELIGIOUS / IDEOLOGICAL =====
        Model("doctrinal_hierarchy", "religious",
              "Permanence of doctrine; self-referential validation; role-pay",
              pays_for_role_not_function=True, hides_load_bearing_node=True,
              self_referential_validation=True, appearance_replaces_audit=True),

        # ===== MILITARY =====
        Model("rank_promotion_logic", "military",
              "Pyramid hierarchy; pay scales by role; performance signal",
              pays_for_role_not_function=True, hides_load_bearing_node=True,
              appearance_replaces_audit=True),

        # ===== HISTORICAL: PRE-COLLAPSE CIVILIZATIONS =====
        Model("late_rapa_nui_moai_logic", "historical_collapse",
              "Resource diverted to monument-performance; substrate decay ignored",
              units_grounded_in_physics=True,
              pays_for_role_not_function=True, appearance_replaces_audit=True,
              self_referential_validation=True),

        Model("late_rome_grain_dole", "historical_collapse",
              "Performance of stability over functional production capacity",
              pays_for_role_not_function=True, appearance_replaces_audit=True,
              self_referential_validation=True, hides_load_bearing_node=True),

        # ===== REFERENCE: VALIDATED ADAPTIVE DESIGN =====
        Model("nomadic_floating_structure", "reference_adaptive",
              "Centuries-validated; timing integral; cycles built-in; no role-pay",
              has_scope=True, has_timing_layer=True, has_diagnostic_cycles=True,
              treats_substrate_as_static=False, treats_time_as_externality=False,
              permanence_assumed=False, units_grounded_in_physics=True,
              pays_for_role_not_function=False, appearance_replaces_audit=False,
              hides_load_bearing_node=False, self_referential_validation=False),

        Model("seasonal_harvest_cycle", "reference_adaptive",
              "Trophic timing as production signal; diagnostic cycles native",
              has_scope=True, has_timing_layer=True, has_diagnostic_cycles=True,
              treats_substrate_as_static=False, treats_time_as_externality=False,
              permanence_assumed=False, units_grounded_in_physics=True),
    ]


# =============================================================================
# 8. Demo
# =============================================================================

if __name__ == "__main__":
    corpus = build_corpus()

    print("=" * 70)
    print("MODELS BY DOMAIN -- severity & collapse-signature carriage")
    print("=" * 70)
    by_domain = defaultdict(list)
    for m in corpus:
        by_domain[m.domain].append(m)
    for domain in sorted(by_domain.keys()):
        print(f"\n[{domain}]")
        for m in sorted(by_domain[domain], key=lambda x: -severity(x)):
            sev = severity(m)
            carry = "[!] COLLAPSE" if carries_collapse_signature(m) else ""
            print(f"  {m.id:35s} sev={sev:5.2f}  {carry}")

    print("\n" + "=" * 70)
    print("CASCADE: each premise -> domains it has propagated into")
    print("=" * 70)
    cascade = domain_cascade(corpus)
    for pid in sorted(cascade, key=lambda k: -len(cascade[k])):
        domains = sorted(cascade[pid])
        print(f"  {pid:30s} ({len(domains):2d}) -> {domains}")

    print("\n" + "=" * 70)
    print("CO-OCCURRENCE: top resonant premise pairs")
    print("=" * 70)
    pairs = co_occurrence(corpus)
    for (a, b), n in sorted(pairs.items(), key=lambda x: -x[1])[:12]:
        print(f"  {a:30s} <-> {b:30s} : {n}")

    print("\n" + "=" * 70)
    print("COLLAPSE SIGNATURE CARRIERS")
    print(f"  pattern = {sorted(COLLAPSE_SIGNATURE)}")
    print("=" * 70)
    carriers = collapse_carriers(corpus)
    for m in sorted(carriers, key=lambda x: x.domain):
        print(f"  {m.id:35s} [{m.domain}]")
    print(f"\n  total: {len(carriers)} / {len(corpus)} models")

    print("\n" + "=" * 70)
    print("DOMAIN RISK DENSITY")
    print("=" * 70)
    risk = domain_risk_density(corpus)
    for domain, stats in sorted(risk.items(), key=lambda x: -x[1]["mean_severity"]):
        print(f"  {domain:22s} n={stats['n_models']:2d}  "
              f"mean_sev={stats['mean_severity']:5.2f}  "
              f"max_sev={stats['max_severity']:5.2f}  "
              f"collapse_frac={stats['collapse_fraction']:.2f}")
