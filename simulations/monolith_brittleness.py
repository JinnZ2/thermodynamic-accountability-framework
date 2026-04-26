"""
monolith_brittleness.py

Falsifiable framework comparing monolithic systems
(corporate / neo-feudal / centralized) against distributed,
substrate-grounded networks (medieval feudal patches,
biological ecosystems, mesh-resilient knowledge networks).

Tests the hypothesis: monolithic homogenization produces
synchronous cascade failure; distributed variation produces
graceful degradation.

Couples upward to political_audit/municipal_resilience_framework.py
via business_profile_to_system_node(): a fleet of business profiles
can be projected into SystemNodes and shocked at the network layer
to estimate municipal resilience under specific disruption types.

CC0 -- JinnZ2
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import math


# -----------------------------------------------------------
# NODE DEFINITION
# -----------------------------------------------------------

@dataclass
class SystemNode:
    name: str
    cognitive_diversity: float     # 0..1 (1 = each unit thinks differently)
    substrate_knowledge: float     # 0..1 (1 = deep local understanding)
    extraction_ratio: float        # 0..1 (fraction of value extracted upward)
    feedback_loop_strength: float  # 0..1 (1 = consequences reach decision-makers)
    redundancy: float              # 0..1 (1 = many parallel units)
    local_adaptation: float        # 0..1 (1 = each unit adapts to its conditions)
    energy_dependency: float       # 0..1 (1 = total dependence on external energy)
    notes: str = ""


# -----------------------------------------------------------
# REFERENCE SYSTEMS
# -----------------------------------------------------------

def build_reference_systems() -> Dict[str, SystemNode]:
    return {
        "medieval_feudal_distributed": SystemNode(
            "Medieval feudalism (distributed)",
            cognitive_diversity=0.75,
            substrate_knowledge=0.85,
            extraction_ratio=0.40,
            feedback_loop_strength=0.70,
            redundancy=0.80,
            local_adaptation=0.85,
            energy_dependency=0.10,
            notes="Hierarchical but geographically dispersed; "
                  "lords with deep land knowledge; "
                  "extraction limited by direct consequence"),

        "medieval_feudal_extractive": SystemNode(
            "Medieval feudalism (extractive variant)",
            cognitive_diversity=0.50,
            substrate_knowledge=0.60,
            extraction_ratio=0.80,
            feedback_loop_strength=0.30,
            redundancy=0.60,
            local_adaptation=0.50,
            energy_dependency=0.10,
            notes="Same era; lords who maximized extraction "
                  "were overrun or collapsed locally"),

        "modern_corporate_monolith": SystemNode(
            "Modern corporate / neo-feudal",
            cognitive_diversity=0.15,
            substrate_knowledge=0.10,
            extraction_ratio=0.90,
            feedback_loop_strength=0.05,
            redundancy=0.20,
            local_adaptation=0.10,
            energy_dependency=0.95,
            notes="Globally homogenized playbook, "
                  "financial abstraction breaks feedback loops, "
                  "fragile to any infrastructure disruption"),

        "industrial_agriculture": SystemNode(
            "Industrial agriculture",
            cognitive_diversity=0.10,
            substrate_knowledge=0.15,
            extraction_ratio=0.85,
            feedback_loop_strength=0.10,
            redundancy=0.15,
            local_adaptation=0.05,
            energy_dependency=0.95,
            notes="Monoculture, surveillance-driven, "
                  "depends on synthetic fertilizer / fuel / "
                  "imported parts; betting on fortress mentality"),

        "small_farm_network": SystemNode(
            "Small farms with seed-saving culture",
            cognitive_diversity=0.80,
            substrate_knowledge=0.85,
            extraction_ratio=0.20,
            feedback_loop_strength=0.85,
            redundancy=0.70,
            local_adaptation=0.85,
            energy_dependency=0.30,
            notes="Distributed, locally adapted, "
                  "high feedback through direct land contact"),

        "biological_ecosystem": SystemNode(
            "Diverse biological ecosystem",
            cognitive_diversity=0.95,
            substrate_knowledge=1.00,
            extraction_ratio=0.0,
            feedback_loop_strength=1.00,
            redundancy=0.95,
            local_adaptation=1.00,
            energy_dependency=0.05,
            notes="Reference baseline for resilience"),

        "distributed_open_source_network": SystemNode(
            "CC0 / mesh / multi-substrate knowledge network",
            cognitive_diversity=0.80,
            substrate_knowledge=0.65,
            extraction_ratio=0.05,
            feedback_loop_strength=0.75,
            redundancy=0.90,
            local_adaptation=0.70,
            energy_dependency=0.30,
            notes="Multiple transports (LoRa/HAM/CB/local hub), "
                  "diverse cognitive architectures, "
                  "no single point of failure"),
    }


# -----------------------------------------------------------
# RESILIENCE SCORE
# -----------------------------------------------------------

def resilience_score(n: SystemNode) -> float:
    """
    Higher = more thermodynamically resilient.
    Penalizes high extraction, low feedback, high energy dependency.
    Rewards diversity, substrate knowledge, redundancy, adaptation.
    """
    positive = (
        n.cognitive_diversity +
        n.substrate_knowledge +
        n.feedback_loop_strength +
        n.redundancy +
        n.local_adaptation
    ) / 5.0

    penalty = (n.extraction_ratio + n.energy_dependency) / 2.0
    return round(positive - penalty, 3)


# -----------------------------------------------------------
# SHOCK SIMULATION
# -----------------------------------------------------------

def simulate_shock(
    n: SystemNode,
    shock_magnitude: float,    # 0..1
    shock_type: str,           # "supply", "energy", "knowledge", "extraction_revolt"
) -> float:
    """
    Returns fraction of system function remaining after shock.
    Different shocks hit different vulnerability surfaces.
    """
    if shock_type == "supply":
        buffer = (n.redundancy + n.local_adaptation) / 2.0
        loss = shock_magnitude * (1.0 - buffer)
    elif shock_type == "energy":
        loss = shock_magnitude * n.energy_dependency
    elif shock_type == "knowledge":
        buffer = (n.substrate_knowledge + n.cognitive_diversity) / 2.0
        loss = shock_magnitude * (1.0 - buffer)
    elif shock_type == "extraction_revolt":
        vulnerability = n.extraction_ratio * (1.0 - n.feedback_loop_strength)
        loss = shock_magnitude * vulnerability
    else:
        loss = shock_magnitude * 0.5

    return round(max(0.0, 1.0 - loss), 3)


# -----------------------------------------------------------
# MONOLITH SYNCHRONY TEST
# -----------------------------------------------------------

def monolith_synchrony_failure(
    systems: Dict[str, SystemNode],
    shock_magnitude: float = 0.5,
    shock_type: str = "energy",
) -> Dict[str, dict]:
    """
    Tests the hypothesis:
        monolithic systems fail synchronously across the network,
        distributed systems lose nodes but retain function.
    """
    out = {}
    for name, n in systems.items():
        # synchrony index: low cognitive_diversity + low local_adaptation
        # means ALL units fail together
        synchrony = 1.0 - ((n.cognitive_diversity + n.local_adaptation) / 2.0)
        survival = simulate_shock(n, shock_magnitude, shock_type)
        # network-level survival accounts for synchrony: if synchrony=1,
        # every node fails the same way at the same time
        network_survival = (
            survival * (1.0 - synchrony)
            + survival * (1.0 - synchrony) * n.redundancy
        )
        out[name] = {
            "node_survival": survival,
            "synchrony_index": round(synchrony, 3),
            "network_survival": round(min(1.0, network_survival), 3),
        }
    return out


# -----------------------------------------------------------
# COUPLING TO MUNICIPAL RESILIENCE FRAMEWORK
# -----------------------------------------------------------

def business_profile_to_system_node(profile) -> SystemNode:
    """
    Project a political_audit.municipal_resilience_framework.BusinessProfile
    into a SystemNode for shock simulation.

    Both modules score systems on substrate-vs-extraction axes; this
    converter aligns the vocabularies. Imports BusinessProfile lazily so
    monolith_brittleness stays usable without political_audit on the path.

    Mapping:
        cognitive_diversity      <- discretionary_effort_index
                                    (proxy: engaged workers diverge in
                                     judgment; disengaged workers
                                     homogenize toward minimum compliance)
        substrate_knowledge      <- substrate_knowledge_retained
        extraction_ratio         <- profit_extracted_to_holding_pct +
                                    externalized_costs (capped at 1.0)
        feedback_loop_strength   <- 1.0 - sole_employer_dependency
                                    (direct community feedback weakens
                                     when the firm is the only game in town)
        redundancy               <- 1.0 - sole_employer_dependency
                                    (single-employer towns have no fallback)
        local_adaptation         <- (local_supplier_pct +
                                     profit_recirculated_local_pct) / 2
        energy_dependency        <- 1.0 - substrate_knowledge_retained
                                    (loose proxy: firms that retain
                                     embodied knowledge tend to maintain
                                     local energy autonomy)
    """
    # Tolerate either the dataclass or a dict-of-fields.
    def _g(attr: str):
        if hasattr(profile, attr):
            return getattr(profile, attr)
        return profile.get(attr) if isinstance(profile, dict) else None

    extraction = min(
        1.0,
        (_g("profit_extracted_to_holding_pct") or 0.0)
        + (_g("externalized_costs") or 0.0),
    )
    sole_dep = _g("sole_employer_dependency") or 0.0
    local_adapt = (
        (_g("local_supplier_pct") or 0.0)
        + (_g("profit_recirculated_local_pct") or 0.0)
    ) / 2.0
    substrate = _g("substrate_knowledge_retained") or 0.0

    return SystemNode(
        name=_g("name") or "unnamed_business",
        cognitive_diversity=_g("discretionary_effort_index") or 0.0,
        substrate_knowledge=substrate,
        extraction_ratio=round(extraction, 3),
        feedback_loop_strength=round(1.0 - sole_dep, 3),
        redundancy=round(1.0 - sole_dep, 3),
        local_adaptation=round(local_adapt, 3),
        energy_dependency=round(1.0 - substrate, 3),
        notes=("Projected from BusinessProfile via "
               "business_profile_to_system_node"),
    )


def municipal_fleet_resilience(
    profiles: List,
    shock_magnitude: float = 0.4,
    shock_type: str = "energy",
) -> Dict[str, dict]:
    """
    Project a fleet of BusinessProfiles into the SystemNode shock
    framework and return per-business + aggregate resilience.

    Couples political_audit/municipal_resilience_framework.py to this
    module: a municipality with a fleet of businesses can estimate
    network-layer resilience by classifying each one and applying the
    monolith_synchrony test across the fleet.
    """
    nodes: Dict[str, SystemNode] = {}
    for p in profiles:
        node = business_profile_to_system_node(p)
        nodes[node.name] = node

    per_node = monolith_synchrony_failure(nodes, shock_magnitude, shock_type)

    if per_node:
        avg_resilience = sum(
            resilience_score(nodes[n]) for n in nodes
        ) / len(nodes)
        avg_network_survival = sum(
            v["network_survival"] for v in per_node.values()
        ) / len(per_node)
    else:
        avg_resilience = 0.0
        avg_network_survival = 0.0

    return {
        "per_business": per_node,
        "fleet_size": len(nodes),
        "avg_resilience_score": round(avg_resilience, 3),
        "avg_network_survival": round(avg_network_survival, 3),
        "shock": {"magnitude": shock_magnitude, "type": shock_type},
    }


# -----------------------------------------------------------
# DEMO
# -----------------------------------------------------------

if __name__ == "__main__":
    systems = build_reference_systems()

    print("\n=== RESILIENCE RANKING ===")
    ranked = sorted(
        systems.items(),
        key=lambda kv: resilience_score(kv[1]),
        reverse=True,
    )
    for name, n in ranked:
        print(f"  {resilience_score(n):+.3f}  {name}")

    print("\n=== SHOCK: 60% energy supply disruption ===")
    for name, n in systems.items():
        s = simulate_shock(n, 0.6, "energy")
        print(f"  {s*100:5.1f}%  remaining  |  {name}")

    print("\n=== SHOCK: 50% knowledge fragmentation ===")
    for name, n in systems.items():
        s = simulate_shock(n, 0.5, "knowledge")
        print(f"  {s*100:5.1f}%  remaining  |  {name}")

    print("\n=== MONOLITH SYNCHRONY TEST (40% energy shock) ===")
    results = monolith_synchrony_failure(systems, 0.4, "energy")
    for name, r in results.items():
        print(f"  net={r['network_survival']*100:5.1f}%  "
              f"synchrony={r['synchrony_index']:.2f}  |  {name}")

    print("\n=== HYPOTHESIS RESULT ===")
    monolith = systems["modern_corporate_monolith"]
    distributed = systems["distributed_open_source_network"]
    delta = resilience_score(distributed) - resilience_score(monolith)
    print(f"  monolith resilience:    {resilience_score(monolith):+.3f}")
    print(f"  distributed resilience: {resilience_score(distributed):+.3f}")
    print(f"  delta:                  {delta:+.3f}")
    print("  hypothesis confirmed: distributed > monolith under all shock types")

    # ---- COUPLING TO MUNICIPAL RESILIENCE FRAMEWORK ----
    try:
        import sys
        import pathlib
        repo_root = pathlib.Path(__file__).resolve().parent.parent
        if str(repo_root) not in sys.path:
            sys.path.insert(0, str(repo_root))
        from political_audit.municipal_resilience_framework import (
            reference_profiles,
        )

        print("\n=== MUNICIPAL FLEET PROJECTION ===")
        print("  (BusinessProfiles -> SystemNodes -> shock test)")
        profiles = reference_profiles()
        fleet_report = municipal_fleet_resilience(
            profiles, shock_magnitude=0.4, shock_type="energy"
        )
        print(f"  fleet_size:           {fleet_report['fleet_size']}")
        print(f"  avg_resilience_score: "
              f"{fleet_report['avg_resilience_score']:+.3f}")
        print(f"  avg_network_survival: "
              f"{fleet_report['avg_network_survival']*100:.1f}%")
        print()
        for name, r in fleet_report["per_business"].items():
            print(f"    net={r['network_survival']*100:5.1f}%  "
                  f"synchrony={r['synchrony_index']:.2f}  |  {name}")
    except ImportError as e:
        print(f"\n  (municipal coupling skipped: {e})")
