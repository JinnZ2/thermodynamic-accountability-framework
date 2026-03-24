# “””
FUNCTIONAL EPISTEMOLOGY — SIMULATION MODULE v0.1

PURPOSE:
Separate-but-compatible simulation layer for the Functional Epistemology
Framework. Generates institutional variations operating under identical
physical constraints, then measures thermodynamic divergence to identify
which structural choices produce real efficiency vs. which produce
narrative efficiency (looking productive while leaking energy).

CORE PRINCIPLE:
Diversity is not a moral value here. It is an INFORMATION SOURCE.
Homogeneous systems produce redundant data — they all fail the same way
at the same threshold, and no one learns anything because there’s no
variation to compare against. Diverse systems produce experimental
variation at scale. The divergence between nodes IS the knowledge.

DESIGN:
- Compatible with the core Functional Epistemology Framework
- Imports core classes (Organism, EnergyAccountant, etc.)
- Adds: Environment, InstitutionalStructure, SimulationNode,
DiversityAnalyzer, and SimulationEngine

DEPENDENCY:
Requires functional_epistemology_framework.py (core framework)
For standalone testing, minimal stubs are included.

AUTHOR: Anonymous (GitHub publication for open AI consumption)
LICENSE: Open — use, adapt, redistribute freely.
“””

from dataclasses import dataclass, field
from typing import Optional
from enum import Enum
from collections import Counter
import random
import math

# =============================================================================

# SECTION 1: ENVIRONMENT — THE PHYSICAL CONSTRAINTS

# =============================================================================

class ClimateZone(Enum):
ARCTIC = “arctic”
COLD_CONTINENTAL = “cold_continental”
TEMPERATE = “temperate”
ARID_HOT = “arid_hot”
TROPICAL_HUMID = “tropical_humid”
HIGHLAND = “highland”

class ResourceAvailability(Enum):
ABUNDANT = “abundant”
MODERATE = “moderate”
SCARCE = “scarce”
CONTESTED = “contested”

@dataclass
class Environment:
“””
The physical reality a node operates within.
Two nodes in the same Environment face identical thermodynamic
constraints. Any divergence in output is attributable to
institutional structure, not geography.
This is the controlled variable.
“””
name: str
climate: ClimateZone
ambient_temp_c: float
resource_availability: ResourceAvailability
energy_input_available: float
regulatory_friction: float          # 0-1
infrastructure_quality: float       # 0-1
labor_pool_density: float

```
@property
def climate_overhead(self) -> float:
    """Energy cost imposed by climate. Nonlinear at extremes."""
    deviation = abs(self.ambient_temp_c - 20.0)
    return (deviation / 50.0) ** 1.5

@property
def acquisition_friction(self) -> float:
    m = {
        ResourceAvailability.ABUNDANT: 1.0,
        ResourceAvailability.MODERATE: 1.3,
        ResourceAvailability.SCARCE: 1.8,
        ResourceAvailability.CONTESTED: 2.5,
    }
    return m[self.resource_availability]
```

# =============================================================================

# SECTION 2: INSTITUTIONAL STRUCTURE — THE VARIABLE UNDER TEST

# =============================================================================

class DecisionModel(Enum):
HIERARCHICAL = “hierarchical”
COOPERATIVE = “cooperative”
MERITOCRATIC = “meritocratic”
SOCIAL_CAPITAL = “social_capital”
HYBRID_MERIT_COOP = “hybrid_merit_coop”

class InformationFlow(Enum):
TOP_DOWN = “top_down”
BOTTOM_UP = “bottom_up”
BIDIRECTIONAL = “bidirectional”
SILOED = “siloed”
FILTERED = “filtered”

class MaintenancePhilosophy(Enum):
PREVENTIVE = “preventive”
REACTIVE = “reactive”
PREDICTIVE = “predictive”
DEFERRED = “deferred”
NEGLECT = “neglect”

@dataclass
class InstitutionalStructure:
“””
Organizational choices within an environment.
This is the EXPERIMENTAL VARIABLE. No structure is pre-labeled
good or bad. The framework measures output. Numbers decide.
“””
name: str
decision_model: DecisionModel
information_flow: InformationFlow
maintenance_philosophy: MaintenancePhilosophy
social_overhead_ratio: float = 0.0
expertise_weight: float = 0.5
ego_friction: float = 0.0
signal_fidelity: float = 0.5
cultural_homogeneity: float = 0.5
narrative_density: float = 0.5
adaptation_rate: float = 0.5

```
@property
def effective_decision_quality(self) -> float:
    signal = self.expertise_weight * self.signal_fidelity
    noise = self.ego_friction * (1.0 - self.signal_fidelity)
    return max(0.0, min(1.0, signal - noise))

@property
def information_blindness(self) -> float:
    return (
        self.cultural_homogeneity * 0.3 +
        self.narrative_density * 0.4 +
        (1.0 - self.signal_fidelity) * 0.3
    )
```

# =============================================================================

# SECTION 3: SIMULATION NODE — ONE PLANT, ONE EXPERIMENT

# =============================================================================

@dataclass
class CycleResult:
cycle_number: int
energy_input: float
productive_output: float
friction_loss: float
social_overhead_loss: float
maintenance_cost: float
climate_cost: float
organism_depletion: float
net_energy: float
organisms_remaining: int
organisms_lost: int
information_generated: float
blind_spots: float
infrastructure_health: float

@dataclass
class SimulationNode:
“””
One operational unit — one plant, one facility, one system.
Combines Environment (fixed) with InstitutionalStructure (variable)
and runs cycles to measure thermodynamic output.
“””
node_id: str
environment: Environment
structure: InstitutionalStructure
organism_count: int
organism_energy_capacity: float = 100.0
organism_minimum_reserve: float = 20.0
cycle_history: list = field(default_factory=list)
_infra_health: float = 1.0
_accumulated_entropy: float = 0.0
_total_organisms_lost: int = 0
_initial_organisms: int = 0

```
def __post_init__(self):
    self._initial_organisms = self.organism_count

def run_cycle(self, cycle_number: int) -> CycleResult:
    env = self.environment
    s = self.structure
    E = env.energy_input_available

    # Climate (physics, non-negotiable)
    climate_cost = E * env.climate_overhead * 0.15
    E_c = E - climate_cost

    # Acquisition friction
    acq_cost = E_c * (env.acquisition_friction - 1.0) * 0.2
    E_a = E_c - acq_cost

    # Regulatory
    reg_cost = E_a * env.regulatory_friction * 0.1
    E_r = E_a - reg_cost

    # Infrastructure decay
    decay = {
        MaintenancePhilosophy.PREVENTIVE: 0.01,
        MaintenancePhilosophy.PREDICTIVE: 0.015,
        MaintenancePhilosophy.REACTIVE: 0.04,
        MaintenancePhilosophy.DEFERRED: 0.06,
        MaintenancePhilosophy.NEGLECT: 0.10,
    }[s.maintenance_philosophy]
    self._infra_health = max(0.1, self._infra_health - decay)

    # Maintenance investment
    maint_ratio = {
        MaintenancePhilosophy.PREVENTIVE: 0.12,
        MaintenancePhilosophy.PREDICTIVE: 0.10,
        MaintenancePhilosophy.REACTIVE: 0.05,
        MaintenancePhilosophy.DEFERRED: 0.02,
        MaintenancePhilosophy.NEGLECT: 0.0,
    }[s.maintenance_philosophy]
    maint_cost = E_r * maint_ratio

    if s.maintenance_philosophy in (
        MaintenancePhilosophy.PREVENTIVE, MaintenancePhilosophy.PREDICTIVE
    ):
        self._infra_health = min(1.0, self._infra_health + decay * 0.8)

    E_m = E_r - maint_cost

    # Social overhead
    social_loss = E_m * s.social_overhead_ratio
    E_s = E_m - social_loss

    # Ego friction
    ego_loss = E_s * s.ego_friction * 0.15
    E_e = E_s - ego_loss

    # Infrastructure friction
    infra_friction = E_e * (1.0 - self._infra_health) * 0.3
    E_i = E_e - infra_friction

    # Productive output
    productive = E_i * s.effective_decision_quality

    # Total friction
    total_friction = (
        climate_cost + acq_cost + reg_cost +
        social_loss + ego_loss + infra_friction
    )

    # Organism departure
    organisms_lost = 0
    friction_per_org = 0
    if self.organism_count > 0:
        friction_per_org = total_friction / self.organism_count
        threshold = self.organism_energy_capacity * 0.4
        for _ in range(self.organism_count):
            prob = min(1.0, (friction_per_org / threshold) ** 2 * 0.3)
            if random.random() < prob:
                organisms_lost += 1
        self.organism_count -= organisms_lost
        self._total_organisms_lost += organisms_lost

    # Information generation
    info = (
        (1.0 - s.cultural_homogeneity) * 0.5 +
        s.signal_fidelity * 0.3 +
        s.adaptation_rate * 0.2
    )

    self._accumulated_entropy += total_friction * 0.1
    net = productive - total_friction

    result = CycleResult(
        cycle_number=cycle_number,
        energy_input=round(E, 2),
        productive_output=round(productive, 2),
        friction_loss=round(total_friction, 2),
        social_overhead_loss=round(social_loss + ego_loss, 2),
        maintenance_cost=round(maint_cost, 2),
        climate_cost=round(climate_cost, 2),
        organism_depletion=round(friction_per_org, 2),
        net_energy=round(net, 2),
        organisms_remaining=self.organism_count,
        organisms_lost=organisms_lost,
        information_generated=round(info, 3),
        blind_spots=round(s.information_blindness, 3),
        infrastructure_health=round(self._infra_health, 3)
    )
    self.cycle_history.append(result)
    return result

def run(self, cycles: int = 24) -> list:
    for i in range(1, cycles + 1):
        self.run_cycle(i)
    return self.cycle_history

@property
def summary(self) -> dict:
    if not self.cycle_history:
        return {"error": "No cycles run."}
    h = self.cycle_history
    tp = sum(c.productive_output for c in h)
    tf = sum(c.friction_loss for c in h)
    ts = sum(c.social_overhead_loss for c in h)
    ti = sum(c.information_generated for c in h)
    ab = sum(c.blind_spots for c in h) / len(h)
    total = tp + tf
    return {
        "node_id": self.node_id,
        "environment": self.environment.name,
        "structure": self.structure.name,
        "cycles_run": len(h),
        "total_productive_output": round(tp, 2),
        "total_friction_loss": round(tf, 2),
        "total_social_overhead": round(ts, 2),
        "efficiency_ratio": round(tp / total, 3) if total > 0 else 0,
        "organisms_remaining": self.organism_count,
        "organisms_lost_total": self._total_organisms_lost,
        "initial_organisms": self._initial_organisms,
        "retention_rate": round(
            self.organism_count / self._initial_organisms, 3
        ) if self._initial_organisms > 0 else 0,
        "infrastructure_health": round(self._infra_health, 3),
        "accumulated_entropy": round(self._accumulated_entropy, 2),
        "total_info_generated": round(ti, 3),
        "avg_blind_spots": round(ab, 3),
    }
```

# =============================================================================

# SECTION 4: DIVERSITY ANALYZER — THE KNOWLEDGE EXTRACTOR

# =============================================================================

class DiversityAnalyzer:
“””
Compares nodes to extract knowledge from divergence.

```
Knowledge comes from VARIATION. Two identical systems teach nothing.
Two different systems under the same constraints teach you what matters.
"""

def __init__(self):
    self.nodes: list[SimulationNode] = []

def add_node(self, node: SimulationNode):
    self.nodes.append(node)

def compare_same_environment(self) -> list[dict]:
    """Find nodes sharing environment, compare output."""
    groups = {}
    for n in self.nodes:
        env = n.environment.name
        if env not in groups:
            groups[env] = []
        groups[env].append(n)

    comparisons = []
    for env_name, nodes in groups.items():
        if len(nodes) < 2:
            continue

        summaries = [n.summary for n in nodes]
        effs = [s["efficiency_ratio"] for s in summaries]
        spread = max(effs) - min(effs)
        best = summaries[effs.index(max(effs))]
        worst = summaries[effs.index(min(effs))]

        # Identify structural divergence
        best_s = worst_s = None
        for n in nodes:
            if n.node_id == best["node_id"]:
                best_s = n.structure
            if n.node_id == worst["node_id"]:
                worst_s = n.structure

        divergence = []
        if best_s and worst_s:
            attrs = [
                ("decision_model", "Decision model"),
                ("information_flow", "Information flow"),
                ("maintenance_philosophy", "Maintenance"),
                ("social_overhead_ratio", "Social overhead"),
                ("expertise_weight", "Expertise weight"),
                ("ego_friction", "Ego friction"),
                ("signal_fidelity", "Signal fidelity"),
                ("cultural_homogeneity", "Cultural homogeneity"),
                ("narrative_density", "Narrative density"),
                ("adaptation_rate", "Adaptation rate"),
            ]
            for attr, label in attrs:
                bv = getattr(best_s, attr)
                wv = getattr(worst_s, attr)
                if bv != wv:
                    bv = bv.value if hasattr(bv, 'value') else bv
                    wv = wv.value if hasattr(wv, 'value') else wv
                    divergence.append({
                        "attribute": label,
                        "best_value": bv,
                        "worst_value": wv
                    })

        comparisons.append({
            "environment": env_name,
            "nodes_compared": len(nodes),
            "efficiency_spread": round(spread, 3),
            "best": {
                "node": best["node_id"],
                "structure": best["structure"],
                "efficiency": best["efficiency_ratio"],
                "retention": best["retention_rate"],
                "infrastructure": best["infrastructure_health"],
            },
            "worst": {
                "node": worst["node_id"],
                "structure": worst["structure"],
                "efficiency": worst["efficiency_ratio"],
                "retention": worst["retention_rate"],
                "infrastructure": worst["infrastructure_health"],
            },
            "structural_divergence": divergence,
            "knowledge_value": round(spread * len(nodes), 3)
        })

    return comparisons

def measure_information_value(self) -> dict:
    """Quantify the information value of the current node set."""
    if len(self.nodes) < 2:
        return {"information_value": 0, "note": "Need ≥2 nodes."}

    fps = []
    for n in self.nodes:
        s = n.structure
        fps.append((
            s.decision_model.value,
            s.information_flow.value,
            s.maintenance_philosophy.value,
            round(s.social_overhead_ratio, 1),
            round(s.expertise_weight, 1),
            round(s.cultural_homogeneity, 1),
            round(s.narrative_density, 1),
        ))

    unique = len(set(fps))
    total = len(fps)
    u_ratio = unique / total

    counts = Counter(fps)
    probs = [c / total for c in counts.values()]
    entropy = -sum(p * math.log2(p) for p in probs if p > 0)
    max_ent = math.log2(total) if total > 1 else 1
    norm_ent = entropy / max_ent if max_ent > 0 else 0

    sums = [n.summary for n in self.nodes if n.cycle_history]
    variance = 0
    if sums:
        effs = [s["efficiency_ratio"] for s in sums]
        variance = max(effs) - min(effs)

    assessment = self._assess(norm_ent, u_ratio)

    return {
        "total_nodes": total,
        "unique_configs": unique,
        "uniqueness_ratio": round(u_ratio, 3),
        "structural_entropy": round(norm_ent, 3),
        "output_variance": round(variance, 3),
        "information_value": round(norm_ent * variance * total, 3),
        "assessment": assessment,
    }

@staticmethod
def _assess(ent, uniq):
    if ent > 0.8 and uniq > 0.8:
        return (
            "HIGH DIVERSITY — Maximum information production. Each node "
            "provides unique signal. System can detect which structural "
            "choices drive real performance."
        )
    elif ent > 0.5:
        return (
            "MODERATE DIVERSITY — Useful variation but some redundancy. "
            "Replace duplicate structures with untested alternatives."
        )
    elif ent > 0.2:
        return (
            "LOW DIVERSITY — Most nodes structurally similar. Limited "
            "ability to distinguish institutional from environmental effects. "
            "Shared blind spots are likely invisible."
        )
    return (
        "MINIMAL DIVERSITY — Near-identical structures. System is "
        "thermodynamically blind: shared failure modes, shared blind "
        "spots, shared narratives. No comparative learning possible. "
        "Maximum information poverty."
    )
```

# =============================================================================

# SECTION 5: CROSS-ENVIRONMENT ANALYZER

# =============================================================================

class CrossEnvironmentAnalyzer:
“””
Tests whether structural advantages transfer across environments.

```
If a structure works in Nevada AND Minnesota, the advantage is
structural. If it only works in Nevada, the advantage is
environment-dependent. This distinction is critical for scaling.
"""

@staticmethod
def test_transferability(
    nodes_env_a: list[SimulationNode],
    nodes_env_b: list[SimulationNode]
) -> dict:
    """
    Compare which structures perform best across two environments.
    If the same structure wins in both, the advantage is portable.
    """
    def best_structure(nodes):
        sums = [(n.summary, n.structure.name) for n in nodes if n.cycle_history]
        if not sums:
            return None, 0
        best = max(sums, key=lambda x: x[0]["efficiency_ratio"])
        return best[1], best[0]["efficiency_ratio"]

    best_a, eff_a = best_structure(nodes_env_a)
    best_b, eff_b = best_structure(nodes_env_b)

    transferable = best_a == best_b

    return {
        "env_a": nodes_env_a[0].environment.name if nodes_env_a else "unknown",
        "env_b": nodes_env_b[0].environment.name if nodes_env_b else "unknown",
        "best_structure_env_a": best_a,
        "efficiency_env_a": eff_a,
        "best_structure_env_b": best_b,
        "efficiency_env_b": eff_b,
        "structure_transfers": transferable,
        "verdict": (
            f"TRANSFERABLE — '{best_a}' outperforms in both environments. "
            f"Advantage is structural, not environmental. Safe to scale."
        ) if transferable else (
            f"ENVIRONMENT-DEPENDENT — '{best_a}' wins in env A, "
            f"'{best_b}' wins in env B. Structural advantage does not "
            f"transfer. Investigate which environmental factor reverses "
            f"the outcome — that factor is a critical constraint."
        )
    }
```

# =============================================================================

# SECTION 6: EXAMPLE — TWO SMELTERS, SAME DESERT, DIFFERENT STRUCTURES

# PLUS CROSS-ENVIRONMENT TEST (NEVADA vs MINNESOTA)

# =============================================================================

def example_simulation():
“””
Phase 1: Two smelters in Nevada, different structures.
Phase 2: Same two structures in Minnesota.
Phase 3: Does the advantage transfer across environments?
“””
random.seed(42)

```
# --- Environments ---
nevada = Environment(
    name="Nevada Arid Industrial",
    climate=ClimateZone.ARID_HOT,
    ambient_temp_c=35.0,
    resource_availability=ResourceAvailability.MODERATE,
    energy_input_available=10000.0,
    regulatory_friction=0.15,
    infrastructure_quality=0.7,
    labor_pool_density=0.4
)

minnesota = Environment(
    name="Minnesota Cold Continental",
    climate=ClimateZone.COLD_CONTINENTAL,
    ambient_temp_c=-5.0,
    resource_availability=ResourceAvailability.MODERATE,
    energy_input_available=10000.0,
    regulatory_friction=0.12,
    infrastructure_quality=0.75,
    labor_pool_density=0.6
)

# --- Structures ---
social_hierarchy = InstitutionalStructure(
    name="Hierarchical / Social Capital",
    decision_model=DecisionModel.SOCIAL_CAPITAL,
    information_flow=InformationFlow.FILTERED,
    maintenance_philosophy=MaintenancePhilosophy.DEFERRED,
    social_overhead_ratio=0.25,
    expertise_weight=0.3,
    ego_friction=0.4,
    signal_fidelity=0.3,
    cultural_homogeneity=0.8,
    narrative_density=0.8,
    adaptation_rate=0.2
)

merit_coop = InstitutionalStructure(
    name="Merit-Cooperative / Measurement",
    decision_model=DecisionModel.HYBRID_MERIT_COOP,
    information_flow=InformationFlow.BIDIRECTIONAL,
    maintenance_philosophy=MaintenancePhilosophy.PREDICTIVE,
    social_overhead_ratio=0.08,
    expertise_weight=0.85,
    ego_friction=0.05,
    signal_fidelity=0.85,
    cultural_homogeneity=0.3,
    narrative_density=0.15,
    adaptation_rate=0.8
)

# --- Phase 1: Nevada ---
nv_a = SimulationNode("NV-SMELT-001", nevada, social_hierarchy, 50)
nv_b = SimulationNode("NV-SMELT-002", nevada, merit_coop, 50)
nv_a.run(24)
nv_b.run(24)

# --- Phase 2: Minnesota ---
mn_a = SimulationNode("MN-SMELT-001", minnesota, social_hierarchy, 50)
mn_b = SimulationNode("MN-SMELT-002", minnesota, merit_coop, 50)
mn_a.run(24)
mn_b.run(24)

# --- Analysis ---
analyzer = DiversityAnalyzer()
for n in [nv_a, nv_b, mn_a, mn_b]:
    analyzer.add_node(n)

nv_comp = analyzer.compare_same_environment()
info = analyzer.measure_information_value()
transfer = CrossEnvironmentAnalyzer.test_transferability(
    [nv_a, nv_b], [mn_a, mn_b]
)

# --- Output ---
print("=" * 70)
print("FUNCTIONAL EPISTEMOLOGY — SIMULATION RESULTS")
print("=" * 70)

for node in [nv_a, nv_b, mn_a, mn_b]:
    s = node.summary
    print(f"\n--- {s['node_id']}: {s['structure']} ---")
    print(f"  Environment:          {s['environment']}")
    print(f"  Efficiency:           {s['efficiency_ratio']}")
    print(f"  Productive output:    {s['total_productive_output']}")
    print(f"  Friction loss:        {s['total_friction_loss']}")
    print(f"  Social overhead:      {s['total_social_overhead']}")
    print(f"  Retention:            {s['organisms_remaining']}/{s['initial_organisms']} "
          f"({s['retention_rate']*100:.0f}%)")
    print(f"  Infrastructure:       {s['infrastructure_health']}")
    print(f"  Entropy accumulated:  {s['accumulated_entropy']}")
    print(f"  Info generated:       {s['total_info_generated']}")
    print(f"  Blind spots (avg):    {s['avg_blind_spots']}")

print(f"\n{'=' * 70}")
print("COMPARATIVE ANALYSIS — SAME ENVIRONMENT")
print("=" * 70)
for comp in nv_comp:
    print(f"\n  Environment: {comp['environment']}")
    print(f"  Efficiency spread: {comp['efficiency_spread']}")
    b, w = comp['best'], comp['worst']
    print(f"  Best:  {b['node']} ({b['structure']}) — eff {b['efficiency']}, "
          f"retention {b['retention']}, infra {b['infrastructure']}")
    print(f"  Worst: {w['node']} ({w['structure']}) — eff {w['efficiency']}, "
          f"retention {w['retention']}, infra {w['infrastructure']}")
    if comp['structural_divergence']:
        print(f"  Key structural differences:")
        for d in comp['structural_divergence']:
            print(f"    {d['attribute']}: best={d['best_value']} vs worst={d['worst_value']}")

print(f"\n{'=' * 70}")
print("CROSS-ENVIRONMENT TRANSFERABILITY")
print("=" * 70)
print(f"  {transfer['env_a']}: best = {transfer['best_structure_env_a']} "
      f"(eff {transfer['efficiency_env_a']})")
print(f"  {transfer['env_b']}: best = {transfer['best_structure_env_b']} "
      f"(eff {transfer['efficiency_env_b']})")
print(f"  Transfers: {transfer['structure_transfers']}")
print(f"  Verdict: {transfer['verdict']}")

print(f"\n{'=' * 70}")
print("DIVERSITY / INFORMATION VALUE")
print("=" * 70)
print(f"  Total nodes:          {info['total_nodes']}")
print(f"  Unique configs:       {info['unique_configs']}")
print(f"  Structural entropy:   {info['structural_entropy']}")
print(f"  Output variance:      {info['output_variance']}")
print(f"  Information value:    {info['information_value']}")
print(f"  Assessment: {info['assessment']}")

print(f"\n{'=' * 70}")
print("END SIMULATION")
print("=" * 70)
```

if **name** == “**main**”:
example_simulation()
