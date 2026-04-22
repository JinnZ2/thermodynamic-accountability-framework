"""
liability_routing_sim.py
========================
Thermodynamic Accountability Simulation — Liability Routing & Schema Decoupling

Implements the node-edge model from ToWorkOn.md:

  Liability Realized ∝ Q × Eₐ × X − Z

Where:
  Q   = Attribution clarity (causal compressibility)
  Eₐ  = Enforcement accessibility
  X   = Event surface area (deployment scale)
  Z   = Shielding (legal, insurance, jurisdictional)

Simulates:
  1. Liability routing through a deployment graph
  2. Q degradation over time under AI-driven diffusion
  3. Instability threshold: F/Q > R × Eₐ
  4. Schema evolution with reality decoupling D(t)
  5. Visualization of all four dynamics

CC0. Requires: numpy, matplotlib
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 1: NODE DEFINITIONS
# ─────────────────────────────────────────────────────────────────────────────

class NodeType(Enum):
    HUMAN_OPERATOR   = "human_operator"       # High Q, high Eₐ
    CORPORATE_ENTITY = "corporate_entity"     # Low Q, medium Eₐ
    OFFSHORE_SUB     = "offshore_subsidiary"  # Very low Q, low Eₐ
    AI_SYSTEM        = "ai_system"            # Near-zero Q, near-zero Eₐ
    INSURANCE_POOL   = "insurance_pool"       # Medium Q, medium Eₐ (capped)
    REGULATOR        = "regulator"            # High Eₐ, finite R
    PUBLIC           = "public"               # Absorbs residual (socialized cost)


@dataclass
class Node:
    """
    A node in the liability enforcement graph.

    Q   : Attribution clarity  (0 = completely diffuse, 1 = perfectly clear)
    Ea  : Enforcement accessibility (0 = unreachable, 1 = fully reachable)
    Z   : Shielding factor     (0 = no shield, 1 = impenetrable)
    R   : Resolution capacity  (max liability units resolved per cycle)
    """
    name: str
    node_type: NodeType
    Q: float          # 0–1
    Ea: float         # 0–1
    Z: float          # 0–1
    R: float          # resolution capacity per cycle
    backlog: float = 0.0
    total_received: float = 0.0
    total_resolved: float = 0.0
    total_reflected: float = 0.0

    @property
    def effective_shield(self) -> float:
        """Fraction of liability that is deflected away from this node."""
        return self.Z

    def receive(self, liability: float) -> float:
        """
        Attempt to resolve incoming liability.
        Returns the amount that could NOT be resolved (reflected/backlogged).
        """
        self.total_received += liability
        # Shielding deflects a fraction before resolution even begins
        deflected = liability * self.effective_shield
        net = liability - deflected

        # Resolution capacity limits how much can be processed this cycle
        resolved = min(net, self.R)
        remainder = net - resolved

        self.total_resolved += resolved
        self.backlog += remainder
        self.total_reflected += deflected + remainder

        return deflected + remainder  # returns unresolved amount


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 2: DEPLOYMENT GRAPH
# ─────────────────────────────────────────────────────────────────────────────

def build_standard_graph(ai_Q: float = 0.05) -> list[Node]:
    """
    Build a standard liability routing graph.
    Nodes are ordered from event origin to final socialized cost.

    ai_Q controls how diffuse the AI node's attribution is.
    Lower ai_Q = more AI-driven Q degradation.
    """
    return [
        Node("AI System",          NodeType.AI_SYSTEM,        Q=ai_Q,  Ea=0.05, Z=0.90, R=5.0),
        Node("Cloud Provider",     NodeType.CORPORATE_ENTITY, Q=0.20,  Ea=0.30, Z=0.70, R=15.0),
        Node("Operating Corp",     NodeType.CORPORATE_ENTITY, Q=0.35,  Ea=0.45, Z=0.60, R=20.0),
        Node("Parent Corp",        NodeType.CORPORATE_ENTITY, Q=0.25,  Ea=0.35, Z=0.75, R=10.0),
        Node("Insurance Pool",     NodeType.INSURANCE_POOL,   Q=0.50,  Ea=0.60, Z=0.40, R=30.0),
        Node("Regulator",          NodeType.REGULATOR,        Q=0.80,  Ea=0.85, Z=0.10, R=25.0),
        Node("Public (Socialized)", NodeType.PUBLIC,           Q=1.00,  Ea=0.01, Z=0.00, R=1e9),
    ]


def route_liability(graph: list[Node], initial_liability: float) -> dict:
    """
    Route a liability event through the graph.
    At each node, unresolved liability propagates to the next node.
    Returns a summary of where liability landed.
    """
    remaining = initial_liability
    trace = []

    for node in graph:
        if remaining <= 0.001:
            break
        reflected = node.receive(remaining)
        resolved_here = remaining - reflected
        trace.append({
            "node": node.name,
            "received": round(remaining, 4),
            "resolved": round(resolved_here, 4),
            "reflected": round(reflected, 4),
        })
        remaining = reflected

    # Whatever is left after the full graph is socialized
    if remaining > 0.001:
        graph[-1].receive(remaining)
        trace.append({
            "node": graph[-1].name + " (overflow)",
            "received": round(remaining, 4),
            "resolved": round(remaining, 4),
            "reflected": 0.0,
        })

    return {
        "trace": trace,
        "initial": initial_liability,
        "total_resolved": sum(t["resolved"] for t in trace),
        "total_reflected": sum(t["reflected"] for t in trace),
    }


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 3: Q DEGRADATION OVER TIME
# ─────────────────────────────────────────────────────────────────────────────

def q_degradation_curve(
    t_max: int = 50,
    q0_corporate: float = 0.45,
    q0_ai: float = 0.80,
    corporate_decay_rate: float = 0.015,
    ai_decay_rate: float = 0.055,
    rng_seed: int = 42,
) -> dict:
    """
    Simulate Q degradation over time for corporate and AI-driven systems.

    Corporate Q degrades slowly (procedural complexity).
    AI Q degrades rapidly (computational diffusion of causality).

    Returns time series for both.
    """
    rng = random.Random(rng_seed)
    t = list(range(t_max))

    q_corp = []
    q_ai = []
    q_c = q0_corporate
    q_a = q0_ai

    for _ in t:
        q_corp.append(max(0.0, q_c))
        q_ai.append(max(0.0, q_a))
        # Corporate: slow procedural decay with noise
        q_c -= corporate_decay_rate + rng.gauss(0, 0.005)
        # AI: fast computational decay with noise
        q_a -= ai_decay_rate + rng.gauss(0, 0.010)

    return {"t": t, "q_corporate": q_corp, "q_ai": q_ai}


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 4: INSTABILITY THRESHOLD — F/Q vs R×Eₐ
# ─────────────────────────────────────────────────────────────────────────────

def instability_threshold_sim(
    t_max: int = 60,
    F0: float = 2.0,
    F_growth: float = 0.10,
    Q0: float = 0.85,
    Q_decay: float = 0.022,
    R: float = 12.0,
    Ea: float = 0.70,
    rng_seed: int = 7,
) -> dict:
    """
    Simulate the instability threshold over time.

    Instability when: F/Q > R × Eₐ

    F grows (AI deployment velocity).
    Q decays (attribution diffusion).
    R × Eₐ is the enforcement supply (treated as slowly declining).
    """
    rng = random.Random(rng_seed)
    t = list(range(t_max))

    F_series = []
    Q_series = []
    demand_series = []   # F/Q
    supply_series = []   # R × Eₐ
    threshold_crossed = None

    F = F0
    Q = Q0
    R_cur = R
    Ea_cur = Ea

    for i in t:
        F_series.append(round(F, 3))
        Q_series.append(round(max(Q, 0.001), 4))
        demand = F / max(Q, 0.001)
        supply = R_cur * Ea_cur
        demand_series.append(round(demand, 3))
        supply_series.append(round(supply, 3))

        if threshold_crossed is None and demand > supply:
            threshold_crossed = i

        # Update for next step
        F *= (1 + F_growth + rng.gauss(0, 0.01))
        Q = max(0.001, Q - Q_decay + rng.gauss(0, 0.005))
        # Institutional capacity erodes slowly under overload
        if demand > supply:
            R_cur = max(1.0, R_cur - 0.05)
            Ea_cur = max(0.10, Ea_cur - 0.005)

    return {
        "t": t,
        "F": F_series,
        "Q": Q_series,
        "demand": demand_series,
        "supply": supply_series,
        "threshold_crossed_at": threshold_crossed,
    }


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 5: SCHEMA EVOLUTION WITH REALITY DECOUPLING D(t)
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class SchemaState:
    """Tracks the state of the legal/institutional schema over time."""
    t: int = 0
    # Representational breadth: fraction of physical reality that is schema-compatible
    breadth: float = 0.80
    # Coupling coefficient between physical Q and legal Q
    coupling: float = 0.90
    # Structural alignment pressure (corporate/state capture)
    S: float = 0.30
    # Infrastructure constraint (technical lock-in)
    infra: float = 0.20
    # Litigation pressure (expansion force from below)
    litigation: float = 0.15
    # Administrative compression (contraction force from within)
    admin_compression: float = 0.10


def schema_evolution_sim(
    t_max: int = 80,
    initial_state: Optional[SchemaState] = None,
    rng_seed: int = 13,
) -> dict:
    """
    Simulate schema evolution under reality decoupling D(t).

    ΔSchema(t) = f( D(t)·{litigation, admin_feedback}, S, infrastructure )

    D(t) is a correlation breakdown operator — not a scalar weight.
    It degrades the stable mapping between physical events and legal representations.

    Returns time series of:
      - schema breadth (fraction of physical reality that is legally representable)
      - coupling (covariance between Q_phys and Q_leg)
      - Q_phys (physical causality)
      - Q_leg (legally representable causality)
    """
    rng = random.Random(rng_seed)
    if initial_state is None:
        initial_state = SchemaState()

    state = initial_state
    t = list(range(t_max))

    breadth_series = []
    coupling_series = []
    q_phys_series = []
    q_leg_series = []
    D_series = []

    q_phys = 0.85  # Physical causality is relatively stable
    q_leg = state.breadth * state.coupling * q_phys

    for i in t:
        breadth_series.append(round(state.breadth, 4))
        coupling_series.append(round(state.coupling, 4))
        q_phys_series.append(round(q_phys, 4))
        q_leg_series.append(round(q_leg, 4))

        # D(t): decoupling strength — grows as infrastructure locks in
        D = min(0.95, state.infra * 0.6 + state.S * 0.4)
        D_series.append(round(D, 4))

        # Litigation pressure: slow expansion from below, gated by D(t)
        expansion = state.litigation * (1 - D) * rng.uniform(0.8, 1.2)

        # Administrative compression: contraction from within
        compression = state.admin_compression * rng.uniform(0.9, 1.1)

        # Structural alignment: asymmetric shaping toward cost-minimizing structures
        s_pressure = state.S * 0.02 * rng.uniform(0.5, 1.5)

        # Infrastructure lock-in grows slowly over time
        state.infra = min(0.95, state.infra + 0.003)

        # Net schema breadth change
        delta_breadth = expansion - compression - s_pressure
        state.breadth = max(0.05, min(1.0, state.breadth + delta_breadth))

        # Coupling degrades as infrastructure diverges from physical reality
        delta_coupling = -D * 0.018 - s_pressure * 0.4
        state.coupling = max(0.05, min(0.98, state.coupling + delta_coupling))

        # Q_phys is stable (physical reality doesn't update to match schema)
        q_phys = max(0.50, q_phys - 0.001 + rng.gauss(0, 0.005))

        # Q_leg tracks schema breadth × coupling × Q_phys
        q_leg = state.breadth * state.coupling * q_phys

        state.t = i + 1

    return {
        "t": t,
        "breadth": breadth_series,
        "coupling": coupling_series,
        "q_phys": q_phys_series,
        "q_leg": q_leg_series,
        "D": D_series,
    }


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 6: VISUALIZATION
# ─────────────────────────────────────────────────────────────────────────────

def run_and_plot(output_path: str = "liability_routing_sim.png"):
    """Run all four simulations and produce a single composite figure."""

    # ── Run simulations ──────────────────────────────────────────────────────
    # 1. Liability routing trace
    graph_baseline = build_standard_graph(ai_Q=0.05)
    routing_result = route_liability(graph_baseline, initial_liability=100.0)

    # 2. Q degradation
    q_data = q_degradation_curve(t_max=50)

    # 3. Instability threshold
    inst_data = instability_threshold_sim(t_max=60)

    # 4. Schema evolution
    schema_data = schema_evolution_sim(t_max=80)

    # ── Layout ───────────────────────────────────────────────────────────────
    fig = plt.figure(figsize=(18, 14))
    fig.patch.set_facecolor("#0d1117")
    gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.42, wspace=0.35)

    ACCENT   = "#58a6ff"
    ACCENT2  = "#f78166"
    ACCENT3  = "#3fb950"
    ACCENT4  = "#d2a8ff"
    BG       = "#161b22"
    GRID_C   = "#30363d"
    TEXT_C   = "#c9d1d9"
    TITLE_C  = "#e6edf3"

    def style_ax(ax, title):
        ax.set_facecolor(BG)
        for spine in ax.spines.values():
            spine.set_edgecolor(GRID_C)
        ax.tick_params(colors=TEXT_C, labelsize=9)
        ax.xaxis.label.set_color(TEXT_C)
        ax.yaxis.label.set_color(TEXT_C)
        ax.set_title(title, color=TITLE_C, fontsize=11, fontweight="bold", pad=10)
        ax.grid(color=GRID_C, linestyle="--", linewidth=0.5, alpha=0.6)

    # ── Plot 1: Liability Routing Waterfall ───────────────────────────────────
    ax1 = fig.add_subplot(gs[0, 0])
    style_ax(ax1, "1. Liability Routing Through Deployment Graph")

    trace = routing_result["trace"]
    node_names = [t["node"] for t in trace]
    received   = [t["received"]  for t in trace]
    resolved   = [t["resolved"]  for t in trace]
    reflected  = [t["reflected"] for t in trace]

    x = np.arange(len(node_names))
    width = 0.35
    ax1.bar(x - width/2, received,  width, label="Received",  color=ACCENT,  alpha=0.85)
    ax1.bar(x + width/2, resolved,  width, label="Resolved",  color=ACCENT3, alpha=0.85)
    ax1.bar(x + width/2, reflected, width, label="Reflected", color=ACCENT2, alpha=0.65,
            bottom=resolved)

    ax1.set_xticks(x)
    ax1.set_xticklabels(node_names, rotation=28, ha="right", fontsize=7.5)
    ax1.set_ylabel("Liability Units", color=TEXT_C)
    ax1.legend(fontsize=8, facecolor=BG, edgecolor=GRID_C, labelcolor=TEXT_C)
    ax1.annotate(
        f"Initial: {routing_result['initial']:.0f}  |  "
        f"Total Resolved: {routing_result['total_resolved']:.1f}  |  "
        f"Total Reflected: {routing_result['total_reflected']:.1f}",
        xy=(0.02, 0.97), xycoords="axes fraction",
        fontsize=7.5, color=TEXT_C, va="top"
    )

    # ── Plot 2: Q Degradation ─────────────────────────────────────────────────
    ax2 = fig.add_subplot(gs[0, 1])
    style_ax(ax2, "2. Attribution Clarity (Q) Degradation Over Time")

    t_q = q_data["t"]
    ax2.plot(t_q, q_data["q_corporate"], color=ACCENT,  linewidth=2,
             label="Corporate Q (procedural decay)")
    ax2.plot(t_q, q_data["q_ai"],        color=ACCENT2, linewidth=2,
             label="AI-driven Q (computational decay)")
    ax2.axhline(0.0, color=GRID_C, linestyle="--", linewidth=1)

    # Mark where AI Q hits near-zero
    ai_q = q_data["q_ai"]
    zero_cross = next((i for i, v in enumerate(ai_q) if v <= 0.05), None)
    if zero_cross:
        ax2.axvline(zero_cross, color=ACCENT2, linestyle=":", linewidth=1.2, alpha=0.7)
        ax2.annotate(f"Q≈0 at t={zero_cross}",
                     xy=(zero_cross, 0.05), color=ACCENT2, fontsize=8,
                     xytext=(zero_cross + 2, 0.15),
                     arrowprops=dict(arrowstyle="->", color=ACCENT2, lw=1))

    ax2.set_xlabel("Time (operational cycles)")
    ax2.set_ylabel("Attribution Clarity Q  (0=diffuse, 1=clear)")
    ax2.set_ylim(-0.05, 1.0)
    ax2.legend(fontsize=8, facecolor=BG, edgecolor=GRID_C, labelcolor=TEXT_C)

    # ── Plot 3: Instability Threshold ─────────────────────────────────────────
    ax3 = fig.add_subplot(gs[1, 0])
    style_ax(ax3, "3. Instability Threshold: F/Q vs R×Eₐ")

    t_i = inst_data["t"]
    ax3.plot(t_i, inst_data["demand"], color=ACCENT2, linewidth=2,
             label="Attribution Demand  F/Q")
    ax3.plot(t_i, inst_data["supply"], color=ACCENT3, linewidth=2,
             label="Enforcement Supply  R×Eₐ")

    tc = inst_data["threshold_crossed_at"]
    if tc is not None:
        ax3.axvline(tc, color="#f0e68c", linestyle="--", linewidth=1.5, alpha=0.8)
        ax3.annotate(f"Threshold crossed\nt = {tc}",
                     xy=(tc, inst_data["demand"][tc]),
                     xytext=(tc + 3, inst_data["demand"][tc] * 0.85),
                     color="#f0e68c", fontsize=8,
                     arrowprops=dict(arrowstyle="->", color="#f0e68c", lw=1))
        # Shade the enforcement deficit region
        t_arr = np.array(t_i)
        d_arr = np.array(inst_data["demand"])
        s_arr = np.array(inst_data["supply"])
        ax3.fill_between(t_arr, d_arr, s_arr,
                         where=(d_arr > s_arr), alpha=0.15, color=ACCENT2,
                         label="Enforcement Deficit")

    ax3.set_xlabel("Time (operational cycles)")
    ax3.set_ylabel("Ratio")
    ax3.legend(fontsize=8, facecolor=BG, edgecolor=GRID_C, labelcolor=TEXT_C)

    # ── Plot 4: Schema Decoupling ─────────────────────────────────────────────
    ax4 = fig.add_subplot(gs[1, 1])
    style_ax(ax4, "4. Schema Evolution & Reality Decoupling D(t)")

    t_s = schema_data["t"]
    ax4.plot(t_s, schema_data["q_phys"],   color=ACCENT3, linewidth=2,
             label="Q_phys  (physical causality)")
    ax4.plot(t_s, schema_data["q_leg"],    color=ACCENT,  linewidth=2,
             label="Q_leg   (legally representable)")
    ax4.plot(t_s, schema_data["coupling"], color=ACCENT4, linewidth=1.5,
             linestyle="--", label="Coupling  (D(t) inverse)")
    ax4.plot(t_s, schema_data["breadth"],  color="#ffa657", linewidth=1.5,
             linestyle=":", label="Schema Breadth")

    # Gap between Q_phys and Q_leg
    t_arr = np.array(t_s)
    ax4.fill_between(t_arr,
                     np.array(schema_data["q_phys"]),
                     np.array(schema_data["q_leg"]),
                     alpha=0.12, color=ACCENT2, label="Decoupling Gap")

    ax4.set_xlabel("Time (schema update cycles)")
    ax4.set_ylabel("Normalized Value  (0–1)")
    ax4.set_ylim(0, 1.05)
    ax4.legend(fontsize=7.5, facecolor=BG, edgecolor=GRID_C, labelcolor=TEXT_C,
               loc="lower left")

    # ── Super-title ───────────────────────────────────────────────────────────
    fig.suptitle(
        "Thermodynamic Accountability Framework — Liability Routing & Schema Decoupling",
        color=TITLE_C, fontsize=14, fontweight="bold", y=0.98
    )

    plt.savefig(output_path, dpi=150, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"[TAF-SIM] Figure saved → {output_path}")

    return {
        "routing": routing_result,
        "q_degradation": q_data,
        "instability": inst_data,
        "schema": schema_data,
    }


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 7: TEXT REPORT
# ─────────────────────────────────────────────────────────────────────────────

def print_report(results: dict):
    """Print a structured text report of all simulation results."""

    print("\n" + "=" * 72)
    print("  THERMODYNAMIC ACCOUNTABILITY FRAMEWORK — SIMULATION REPORT")
    print("=" * 72)

    # ── 1. Liability Routing ──────────────────────────────────────────────────
    r = results["routing"]
    print("\n── 1. LIABILITY ROUTING TRACE ──────────────────────────────────────")
    print(f"  Initial liability: {r['initial']:.1f} units")
    print(f"  {'Node':<30} {'Received':>10} {'Resolved':>10} {'Reflected':>10}")
    print(f"  {'-'*62}")
    for t in r["trace"]:
        print(f"  {t['node']:<30} {t['received']:>10.2f} {t['resolved']:>10.2f} "
              f"{t['reflected']:>10.2f}")
    print(f"\n  Total resolved:  {r['total_resolved']:>8.2f}")
    print(f"  Total reflected: {r['total_reflected']:>8.2f}")
    pct = r['total_reflected'] / r['initial'] * 100
    print(f"  Reflection rate: {pct:.1f}%  ← fraction that never reached resolution")

    # ── 2. Q Degradation ─────────────────────────────────────────────────────
    q = results["q_degradation"]
    print("\n── 2. Q DEGRADATION ────────────────────────────────────────────────")
    print(f"  Corporate Q at t=0: {q['q_corporate'][0]:.3f}  |  "
          f"at t=final: {q['q_corporate'][-1]:.3f}")
    print(f"  AI-driven Q at t=0: {q['q_ai'][0]:.3f}  |  "
          f"at t=final: {q['q_ai'][-1]:.3f}")
    ai_zero = next((i for i, v in enumerate(q["q_ai"]) if v <= 0.05), None)
    if ai_zero:
        print(f"  AI Q reaches near-zero (≤0.05) at cycle: {ai_zero}")

    # ── 3. Instability Threshold ──────────────────────────────────────────────
    inst = results["instability"]
    print("\n── 3. INSTABILITY THRESHOLD ────────────────────────────────────────")
    tc = inst["threshold_crossed_at"]
    if tc is not None:
        print(f"  Threshold crossed at cycle: {tc}")
        print(f"  F/Q at crossing: {inst['demand'][tc]:.2f}")
        print(f"  R×Eₐ at crossing: {inst['supply'][tc]:.2f}")
        deficit_cycles = sum(1 for d, s in zip(inst["demand"], inst["supply"]) if d > s)
        print(f"  Cycles in enforcement deficit: {deficit_cycles} / {len(inst['t'])}")
    else:
        print("  Threshold NOT crossed within simulation window.")

    # ── 4. Schema Decoupling ──────────────────────────────────────────────────
    s = results["schema"]
    print("\n── 4. SCHEMA EVOLUTION & REALITY DECOUPLING ────────────────────────")
    print(f"  Schema breadth at t=0: {s['breadth'][0]:.3f}  |  "
          f"at t=final: {s['breadth'][-1]:.3f}")
    print(f"  Coupling at t=0:       {s['coupling'][0]:.3f}  |  "
          f"at t=final: {s['coupling'][-1]:.3f}")
    print(f"  Q_phys at t=final:     {s['q_phys'][-1]:.3f}")
    print(f"  Q_leg  at t=final:     {s['q_leg'][-1]:.3f}")
    gap = s['q_phys'][-1] - s['q_leg'][-1]
    print(f"  Decoupling gap (Q_phys − Q_leg): {gap:.3f}")
    print(f"  → {gap/s['q_phys'][-1]*100:.1f}% of physical causality is legally non-representable")

    print("\n" + "=" * 72)
    print("  INTERPRETATION")
    print("=" * 72)
    print("""
  The simulation demonstrates four coupled failure modes:

  1. ROUTING: Liability is not absorbed by nodes — it is deflected.
     High-shield nodes (AI, offshore subsidiaries) reflect the majority
     of liability upstream or downstream until it lands as socialized cost.

  2. Q DEGRADATION: AI-driven attribution diffusion collapses Q far faster
     than corporate procedural complexity. Once Q → 0, the liability
     equation (Q × Eₐ × X − Z) produces near-zero realized liability
     regardless of the scale of harm.

  3. INSTABILITY: The F/Q ratio (attribution demand) grows exponentially
     while R×Eₐ (enforcement supply) stagnates or declines under overload.
     The threshold crossing marks the point of permanent enforcement deficit.

  4. DECOUPLING: Schema evolution is not neutral. Structural alignment (S)
     and infrastructure lock-in drive the schema to optimize for minimum
     representational complexity. The gap between Q_phys and Q_leg grows
     monotonically — physical reality continues to occur, but an increasing
     fraction of it is legally non-existent.

  The attractor state is a self-consistent representational system that
  maintains procedural legitimacy while processing an ever-narrowing slice
  of actual harm.
""")


# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import os
    out_dir = os.path.dirname(os.path.abspath(__file__))
    img_path = os.path.join(out_dir, "liability_routing_sim.png")

    results = run_and_plot(output_path=img_path)
    print_report(results)
