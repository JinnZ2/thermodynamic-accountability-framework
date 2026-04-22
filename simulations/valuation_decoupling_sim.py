"""
valuation_decoupling_sim.py
===========================
Thermodynamic Accountability Framework — Valuation Decoupling Simulation

Models the economic analogue of the liability routing system from
liability_routing_sim.py, their cross-system coupling, and the
combined attractor state.

Core structure from ToWorkOn.md:

  Valuation Decoupling:
    Price = f(liquidity, expectation_density, narrative_coherence)
    NOT f(eROI, material_throughput, real_demand)

  The shared invariant with legal decoupling:
    Both systems optimize internal consistency under partial constraint
    visibility, producing persistent divergence from physical reality.

  Cross-system coupling:
    Legal Q degradation → enforcement deficit → reduced constraint
    feedback → valuation decoupling accelerates.
    Valuation decoupling → capital flows to low-Q structures →
    legal Q degrades further.

Six simulation panels:
  1. Price vs. Constraint: valuation decoupling over time
  2. eROI Erosion: energy return on investment vs. financial return
  3. Stability Illusion: internal coherence metrics vs. thermodynamic distance
  4. Cross-System Coupling: legal Q ↔ valuation D(t) feedback loop
  5. Combined Attractor State: phase portrait of the dual-decoupling system
  6. Crisis Anatomy: constraint breach event — correction and drift resumption

CC0. Requires: numpy, matplotlib
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Optional

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
import numpy as np


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 1: VALUATION DECOUPLING MODEL
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class ValuationState:
    """
    State of the financial valuation system at time t.

    price_index       : Financial representation of value (normalized to 1.0 at t=0)
    constraint_index  : Physical constraint-bound productivity (normalized to 1.0 at t=0)
    eROI              : Energy return on investment (net energy / energy invested)
    liquidity         : Capital accessibility (amplifies price independent of constraints)
    narrative_strength: Coordinated belief structure coupling (self-reinforcing)
    credit_leverage   : Debt-extended demand / real demand ratio
    D_econ            : Economic decoupling function (0=coupled, 1=fully decoupled)
    """
    t: int = 0
    price_index: float = 1.0
    constraint_index: float = 1.0
    eROI: float = 8.0          # Historical avg ~8:1 for industrial economy
    liquidity: float = 1.0
    narrative_strength: float = 0.60
    credit_leverage: float = 3.0
    D_econ: float = 0.15       # Initial decoupling (already partially decoupled)
    # Internal coherence metrics (schema-internal stability signals)
    volatility: float = 0.08
    clearing_efficiency: float = 0.95
    # Thermodynamic distance (how far price is from constraint-bound value)
    thermo_distance: float = 0.0


def valuation_decoupling_sim(
    t_max: int = 100,
    eROI_initial: float = 8.0,
    eROI_decay: float = 0.04,       # eROI erodes as cheap energy depletes
    liquidity_growth: float = 0.025,
    narrative_growth: float = 0.015,
    credit_growth: float = 0.030,
    S_alignment: float = 0.35,      # structural alignment (corporate/state capture)
    rng_seed: int = 42,
) -> dict:
    """
    Simulate valuation decoupling over time.

    Price is driven by liquidity × narrative × credit (internal factors).
    Constraint-bound value is driven by eROI × material throughput (physical).
    D_econ grows as the gap between these two systems widens.
    """
    rng = random.Random(rng_seed)
    state = ValuationState(eROI=eROI_initial)

    t_series = []
    price_series = []
    constraint_series = []
    eROI_series = []
    D_econ_series = []
    gap_series = []
    thermo_dist_series = []
    volatility_series = []
    clearing_series = []
    liquidity_series = []
    narrative_series = []

    for i in range(t_max):
        t_series.append(i)
        price_series.append(round(state.price_index, 4))
        constraint_series.append(round(state.constraint_index, 4))
        eROI_series.append(round(state.eROI, 4))
        D_econ_series.append(round(state.D_econ, 4))
        gap_series.append(round(state.price_index - state.constraint_index, 4))
        thermo_dist_series.append(round(state.thermo_distance, 4))
        volatility_series.append(round(state.volatility, 4))
        clearing_series.append(round(state.clearing_efficiency, 4))
        liquidity_series.append(round(state.liquidity, 4))
        narrative_series.append(round(state.narrative_strength, 4))

        # ── Physical constraint evolution ──────────────────────────────────
        # eROI decays as cheap energy depletes; material throughput follows
        state.eROI = max(0.5, state.eROI - eROI_decay + rng.gauss(0, 0.02))
        # Constraint index tracks eROI (physical productivity)
        eROI_norm = state.eROI / eROI_initial
        state.constraint_index = max(0.1, eROI_norm * (1 + rng.gauss(0, 0.01)))

        # ── Financial valuation evolution ──────────────────────────────────
        # Price is driven by liquidity × narrative × credit leverage
        state.liquidity = min(5.0, state.liquidity * (1 + liquidity_growth + rng.gauss(0, 0.008)))
        state.narrative_strength = min(0.98, state.narrative_strength + narrative_growth + rng.gauss(0, 0.005))
        state.credit_leverage = min(20.0, state.credit_leverage * (1 + credit_growth + rng.gauss(0, 0.010)))

        # Price reflects internal factors, not physical constraints
        price_driver = (state.liquidity * state.narrative_strength *
                        math.log1p(state.credit_leverage) / math.log1p(3.0))
        state.price_index = max(0.1, price_driver * (1 + rng.gauss(0, 0.015)))

        # ── Decoupling function D_econ ─────────────────────────────────────
        # D_econ is the correlation breakdown between price and constraints
        gap = state.price_index - state.constraint_index
        # Grows with gap, structural alignment, and credit leverage
        D_increment = (
            0.003 * max(0, gap) +
            S_alignment * 0.004 +
            math.log1p(state.credit_leverage) * 0.001
        )
        state.D_econ = min(0.98, state.D_econ + D_increment)

        # ── Thermodynamic distance ─────────────────────────────────────────
        # How far price is from constraint-bound value
        state.thermo_distance = max(0, state.price_index - state.constraint_index)

        # ── Internal coherence metrics (schema-internal stability) ─────────
        # Volatility stays low (circuit breakers, margin requirements)
        state.volatility = max(0.02, 0.08 + rng.gauss(0, 0.01))
        # Clearing efficiency stays high (internal protocols work fine)
        state.clearing_efficiency = min(0.99, 0.95 + rng.gauss(0, 0.005))

        state.t = i + 1

    return {
        "t": t_series,
        "price": price_series,
        "constraint": constraint_series,
        "eROI": eROI_series,
        "D_econ": D_econ_series,
        "gap": gap_series,
        "thermo_distance": thermo_dist_series,
        "volatility": volatility_series,
        "clearing": clearing_series,
        "liquidity": liquidity_series,
        "narrative": narrative_series,
    }


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 2: CROSS-SYSTEM COUPLING
# ─────────────────────────────────────────────────────────────────────────────

def cross_system_coupling_sim(
    t_max: int = 100,
    Q_legal_0: float = 0.75,
    D_econ_0: float = 0.15,
    legal_decay_base: float = 0.015,
    econ_decouple_base: float = 0.008,
    coupling_strength: float = 0.35,  # how strongly the two systems feed each other
    rng_seed: int = 7,
) -> dict:
    """
    Simulate the bidirectional coupling between legal Q degradation
    and economic valuation decoupling.

    Legal Q degradation → enforcement deficit → reduced constraint
    feedback into valuation → D_econ accelerates.

    D_econ growth → capital flows to low-Q structures (offshore,
    AI-intermediated, complex derivatives) → legal Q degrades faster.

    Returns time series for both systems and their coupling signal.
    """
    rng = random.Random(rng_seed)

    Q_legal = Q_legal_0
    D_econ = D_econ_0

    t_series = []
    Q_legal_series = []
    D_econ_series = []
    # Enforcement deficit: F/Q - R×Eₐ (normalized)
    enforcement_deficit_series = []
    # Constraint feedback signal reaching valuation system
    constraint_feedback_series = []
    # Capital flow to low-Q structures
    low_Q_capital_flow_series = []
    # Combined system stress
    combined_stress_series = []

    # Baseline enforcement parameters (from liability_routing_sim)
    F_base = 2.0
    F_growth = 0.10
    R_Ea = 8.4  # R × Eₐ baseline

    F = F_base

    for i in range(t_max):
        t_series.append(i)
        Q_legal_series.append(round(max(Q_legal, 0.001), 4))
        D_econ_series.append(round(min(D_econ, 0.98), 4))

        # Enforcement deficit
        demand = F / max(Q_legal, 0.001)
        supply = R_Ea
        deficit = max(0, demand - supply) / supply  # normalized
        enforcement_deficit_series.append(round(deficit, 4))

        # Constraint feedback to valuation: how much physical reality
        # can reach the valuation system (gated by enforcement deficit)
        constraint_feedback = max(0.01, 1.0 - D_econ) * max(0.01, 1.0 - deficit * 0.1)
        constraint_feedback_series.append(round(constraint_feedback, 4))

        # Capital flow to low-Q structures (grows with D_econ)
        low_Q_flow = D_econ * (1 + deficit * 0.2) * rng.uniform(0.9, 1.1)
        low_Q_capital_flow_series.append(round(min(1.0, low_Q_flow), 4))

        # Combined system stress
        combined_stress = (1 - Q_legal) * D_econ
        combined_stress_series.append(round(combined_stress, 4))

        # ── Update Q_legal ─────────────────────────────────────────────────
        # Base decay + amplification from capital flowing to low-Q structures
        legal_decay = (legal_decay_base +
                       coupling_strength * low_Q_flow * 0.02 +
                       rng.gauss(0, 0.004))
        Q_legal = max(0.001, Q_legal - legal_decay)

        # ── Update D_econ ──────────────────────────────────────────────────
        # Base growth + amplification from enforcement deficit
        # (less enforcement → less constraint feedback → more decoupling)
        econ_decouple = (econ_decouple_base +
                         coupling_strength * deficit * 0.015 +
                         rng.gauss(0, 0.003))
        D_econ = min(0.98, D_econ + econ_decouple)

        # ── Update F (event frequency) ─────────────────────────────────────
        F *= (1 + F_growth + rng.gauss(0, 0.01))

        # ── R×Eₐ erodes under overload ─────────────────────────────────────
        if deficit > 0:
            R_Ea = max(1.0, R_Ea - 0.03)

    return {
        "t": t_series,
        "Q_legal": Q_legal_series,
        "D_econ": D_econ_series,
        "enforcement_deficit": enforcement_deficit_series,
        "constraint_feedback": constraint_feedback_series,
        "low_Q_capital_flow": low_Q_capital_flow_series,
        "combined_stress": combined_stress_series,
    }


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 3: COMBINED ATTRACTOR STATE (PHASE PORTRAIT)
# ─────────────────────────────────────────────────────────────────────────────

def attractor_phase_portrait(
    n_trajectories: int = 8,
    t_max: int = 80,
    rng_seed: int = 13,
) -> dict:
    """
    Generate phase portrait trajectories in (Q_legal, D_econ) space.
    Multiple starting conditions all converge toward the same attractor:
    Q_legal → 0, D_econ → 1 (maximum decoupling, zero attribution clarity).

    Returns list of (Q_legal_trajectory, D_econ_trajectory) pairs.
    """
    rng = random.Random(rng_seed)
    trajectories = []

    # Starting conditions spread across the phase space
    starts = [
        (0.90, 0.05),  # High Q, low decoupling (healthy start)
        (0.75, 0.15),
        (0.60, 0.25),
        (0.80, 0.10),
        (0.50, 0.35),
        (0.40, 0.45),
        (0.70, 0.20),
        (0.30, 0.55),  # Already partially degraded
    ]

    for start_Q, start_D in starts[:n_trajectories]:
        Q = start_Q
        D = start_D
        Q_traj = [Q]
        D_traj = [D]

        # Per-trajectory parameter variation: different decay/growth rates
        # to produce visibly distinct paths before convergence
        q_decay_base = rng.uniform(0.008, 0.022)
        d_growth_base = rng.uniform(0.005, 0.016)
        coupling_q = rng.uniform(0.015, 0.040)
        coupling_d = rng.uniform(0.010, 0.035)

        for _ in range(t_max):
            # Q decays faster when D is high
            dQ = -(q_decay_base + D * coupling_q + rng.gauss(0, 0.003))
            # D grows faster when Q is low
            dD = (d_growth_base + (1 - Q) * coupling_d + rng.gauss(0, 0.003))

            Q = max(0.001, Q + dQ)
            D = min(0.98, D + dD)
            Q_traj.append(round(Q, 4))
            D_traj.append(round(D, 4))

        trajectories.append({"Q": Q_traj, "D": D_traj,
                              "start": (start_Q, start_D)})

    return {"trajectories": trajectories}


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 4: CRISIS ANATOMY
# ─────────────────────────────────────────────────────────────────────────────

def crisis_anatomy_sim(
    t_max: int = 120,
    crisis_at: int = 65,
    rng_seed: int = 99,
) -> dict:
    """
    Simulate a constraint breach event (crisis) and the system's response.

    Before crisis: price drifts from constraints; D_econ grows.
    Crisis: thermodynamic reality intrudes — price corrects sharply.
    After crisis: schema absorbs shock; drift resumes.
    The system learns to absorb reality shocks without coupling to reality.
    """
    rng = random.Random(rng_seed)

    t_series = []
    price_series = []
    constraint_series = []
    D_econ_series = []
    schema_response_series = []  # institutional/schema response intensity
    coupling_restoration_series = []  # how much coupling is restored post-crisis

    price = 1.0
    constraint = 1.0
    D_econ = 0.10
    eROI = 8.0
    liquidity = 1.0
    schema_response = 0.0
    coupling_restoration = 0.0

    in_crisis = False
    crisis_duration = 0
    post_crisis_drift_resumed = False

    for i in range(t_max):
        t_series.append(i)
        price_series.append(round(price, 4))
        constraint_series.append(round(constraint, 4))
        D_econ_series.append(round(D_econ, 4))
        schema_response_series.append(round(schema_response, 4))
        coupling_restoration_series.append(round(coupling_restoration, 4))

        if i < crisis_at:
            # Pre-crisis: normal decoupling drift
            eROI = max(0.5, eROI - 0.04 + rng.gauss(0, 0.01))
            constraint = max(0.1, eROI / 8.0)
            liquidity = min(5.0, liquidity * (1 + 0.025 + rng.gauss(0, 0.005)))
            price = liquidity * 0.65 * (1 + rng.gauss(0, 0.012))
            D_econ = min(0.95, D_econ + 0.008 + rng.gauss(0, 0.002))
            schema_response = 0.0
            coupling_restoration = 0.0

        elif i == crisis_at:
            # Crisis onset: constraint breach overwhelms abstraction layers
            in_crisis = True
            crisis_duration = 0
            price = constraint * 1.1  # sharp correction toward constraint
            D_econ = max(0.05, D_econ - 0.30)  # temporary coupling restoration
            schema_response = 0.85
            coupling_restoration = 0.45
            liquidity = liquidity * 0.55  # liquidity shock

        elif in_crisis:
            crisis_duration += 1
            # Crisis: schema tools deployed (liquidity injection, circuit breakers)
            schema_response = max(0.0, schema_response - 0.08)
            coupling_restoration = max(0.0, coupling_restoration - 0.04)
            # Price stabilizes via schema tools, not constraint coupling
            liquidity = min(5.0, liquidity * (1 + 0.06 + rng.gauss(0, 0.010)))
            price = max(constraint * 0.9, price * (1 + 0.04 + rng.gauss(0, 0.015)))
            # D_econ begins recovering (decoupling resumes)
            D_econ = min(0.95, D_econ + 0.015 + rng.gauss(0, 0.003))
            constraint = max(0.1, constraint - 0.002)  # physical reality unchanged

            if crisis_duration >= 15:
                in_crisis = False
                post_crisis_drift_resumed = True

        else:
            # Post-crisis: drift resumes, often faster than before
            eROI = max(0.5, eROI - 0.05 + rng.gauss(0, 0.01))
            constraint = max(0.1, eROI / 8.0)
            liquidity = min(6.0, liquidity * (1 + 0.030 + rng.gauss(0, 0.008)))
            price = liquidity * 0.70 * (1 + rng.gauss(0, 0.015))
            D_econ = min(0.98, D_econ + 0.010 + rng.gauss(0, 0.002))
            schema_response = 0.0
            coupling_restoration = 0.0

    return {
        "t": t_series,
        "price": price_series,
        "constraint": constraint_series,
        "D_econ": D_econ_series,
        "schema_response": schema_response_series,
        "coupling_restoration": coupling_restoration_series,
        "crisis_at": crisis_at,
    }


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 5: VISUALIZATION
# ─────────────────────────────────────────────────────────────────────────────

def run_and_plot(output_path: str = "valuation_decoupling_sim.png"):
    """Run all simulations and produce a six-panel composite figure."""

    # ── Run simulations ──────────────────────────────────────────────────────
    val_data    = valuation_decoupling_sim(t_max=100)
    cross_data  = cross_system_coupling_sim(t_max=100)
    phase_data  = attractor_phase_portrait(n_trajectories=8, t_max=80)
    crisis_data = crisis_anatomy_sim(t_max=120, crisis_at=65)

    # ── Layout ───────────────────────────────────────────────────────────────
    fig = plt.figure(figsize=(20, 18))
    fig.patch.set_facecolor("#0d1117")
    gs = gridspec.GridSpec(3, 2, figure=fig, hspace=0.46, wspace=0.32)

    ACCENT   = "#58a6ff"
    ACCENT2  = "#f78166"
    ACCENT3  = "#3fb950"
    ACCENT4  = "#d2a8ff"
    ACCENT5  = "#ffa657"
    BG       = "#161b22"
    GRID_C   = "#30363d"
    TEXT_C   = "#c9d1d9"
    TITLE_C  = "#e6edf3"
    WARN_C   = "#f0e68c"

    def style_ax(ax, title):
        ax.set_facecolor(BG)
        for spine in ax.spines.values():
            spine.set_edgecolor(GRID_C)
        ax.tick_params(colors=TEXT_C, labelsize=9)
        ax.xaxis.label.set_color(TEXT_C)
        ax.yaxis.label.set_color(TEXT_C)
        ax.set_title(title, color=TITLE_C, fontsize=10.5, fontweight="bold", pad=9)
        ax.grid(color=GRID_C, linestyle="--", linewidth=0.5, alpha=0.6)

    # ── Panel 1: Price vs. Constraint ─────────────────────────────────────────
    ax1 = fig.add_subplot(gs[0, 0])
    style_ax(ax1, "1. Price vs. Constraint-Bound Value")

    t = val_data["t"]
    ax1.plot(t, val_data["price"],      color=ACCENT2, lw=2,
             label="Price Index  (liquidity × narrative × credit)")
    ax1.plot(t, val_data["constraint"], color=ACCENT3, lw=2,
             label="Constraint Index  (eROI-bound productivity)")
    ax1.fill_between(t,
                     np.array(val_data["price"]),
                     np.array(val_data["constraint"]),
                     where=np.array(val_data["price"]) > np.array(val_data["constraint"]),
                     alpha=0.15, color=ACCENT2, label="Valuation Gap")
    ax1.plot(t, val_data["D_econ"], color=ACCENT4, lw=1.5, linestyle="--",
             label="D_econ (decoupling operator)")
    ax1.set_xlabel("Time (market cycles)")
    ax1.set_ylabel("Normalized Value")
    ax1.legend(fontsize=7.5, facecolor=BG, edgecolor=GRID_C, labelcolor=TEXT_C)

    # ── Panel 2: eROI Erosion vs. Financial Return ────────────────────────────
    ax2 = fig.add_subplot(gs[0, 1])
    style_ax(ax2, "2. eROI Erosion vs. Financial Return Proxy")

    eROI_arr = np.array(val_data["eROI"])
    price_arr = np.array(val_data["price"])
    # Financial return proxy: price growth rate (rolling 5-period)
    fin_return = np.convolve(np.gradient(price_arr), np.ones(5)/5, mode='same') * 10 + 1

    ax2_twin = ax2.twinx()
    ax2_twin.set_facecolor(BG)
    ax2_twin.tick_params(colors=TEXT_C, labelsize=9)
    ax2_twin.yaxis.label.set_color(ACCENT2)
    ax2_twin.spines["right"].set_edgecolor(ACCENT2)
    ax2_twin.spines["left"].set_edgecolor(GRID_C)
    ax2_twin.spines["top"].set_edgecolor(GRID_C)
    ax2_twin.spines["bottom"].set_edgecolor(GRID_C)

    ax2.plot(t, eROI_arr, color=ACCENT3, lw=2, label="eROI (thermodynamic)")
    ax2.axhline(1.0, color=GRID_C, linestyle=":", lw=1, alpha=0.7)
    ax2.annotate("eROI = 1.0\n(break-even)", xy=(5, 1.05), color=TEXT_C, fontsize=7.5)
    ax2_twin.plot(t, fin_return, color=ACCENT2, lw=1.5, linestyle="--",
                  label="Financial Return Proxy")

    ax2.set_xlabel("Time (market cycles)")
    ax2.set_ylabel("eROI  (net energy / invested energy)", color=ACCENT3)
    ax2_twin.set_ylabel("Financial Return Proxy", color=ACCENT2)

    lines1, labels1 = ax2.get_legend_handles_labels()
    lines2, labels2 = ax2_twin.get_legend_handles_labels()
    ax2.legend(lines1 + lines2, labels1 + labels2,
               fontsize=7.5, facecolor=BG, edgecolor=GRID_C, labelcolor=TEXT_C)

    # ── Panel 3: Stability Illusion ───────────────────────────────────────────
    ax3 = fig.add_subplot(gs[1, 0])
    style_ax(ax3, "3. Stability Illusion: Internal Coherence vs. Thermodynamic Distance")

    ax3.plot(t, val_data["volatility"],  color=ACCENT3, lw=2,
             label="Internal Volatility (low = schema-stable)")
    ax3.plot(t, val_data["clearing"],    color=ACCENT,  lw=2,
             label="Clearing Efficiency (high = schema-functional)")
    ax3.plot(t, val_data["D_econ"],      color=ACCENT4, lw=1.5, linestyle="--",
             label="D_econ (left axis)")

    ax3_twin = ax3.twinx()
    ax3_twin.set_facecolor(BG)
    ax3_twin.tick_params(colors=ACCENT2, labelsize=9)
    ax3_twin.yaxis.label.set_color(ACCENT2)
    for sp in ax3_twin.spines.values():
        sp.set_edgecolor(GRID_C)
    ax3_twin.spines["right"].set_edgecolor(ACCENT2)
    ax3_twin.plot(t, val_data["thermo_distance"], color=ACCENT2, lw=2,
                  label="Thermodynamic Distance (right axis)")
    ax3_twin.set_ylabel("Thermodynamic Distance  (price − constraint)", color=ACCENT2)

    ax3.annotate("Schema-internal metrics\nstay flat and healthy",
                 xy=(50, 0.95), color=ACCENT3, fontsize=8,
                 xytext=(30, 0.75),
                 arrowprops=dict(arrowstyle="->", color=ACCENT3, lw=1))
    ax3_twin.annotate("Thermodynamic distance\ngrows unchecked →",
                      xy=(85, val_data["thermo_distance"][85]),
                      color=ACCENT2, fontsize=8,
                      xytext=(55, val_data["thermo_distance"][85] * 0.6),
                      arrowprops=dict(arrowstyle="->", color=ACCENT2, lw=1))

    ax3.set_xlabel("Time (market cycles)")
    ax3.set_ylabel("Internal Coherence Metric  (0–1)")
    lines1, labs1 = ax3.get_legend_handles_labels()
    lines2, labs2 = ax3_twin.get_legend_handles_labels()
    ax3.legend(lines1 + lines2, labs1 + labs2,
               fontsize=7.5, facecolor=BG, edgecolor=GRID_C, labelcolor=TEXT_C,
               loc="center left")

    # ── Panel 4: Cross-System Coupling ────────────────────────────────────────
    ax4 = fig.add_subplot(gs[1, 1])
    style_ax(ax4, "4. Cross-System Coupling: Legal Q ↔ Economic D(t)")

    ct = cross_data["t"]
    ax4.plot(ct, cross_data["Q_legal"],            color=ACCENT,  lw=2,
             label="Legal Q (attribution clarity)")
    ax4.plot(ct, cross_data["D_econ"],             color=ACCENT2, lw=2,
             label="Economic D(t) (valuation decoupling)")
    ax4.plot(ct, cross_data["constraint_feedback"], color=ACCENT3, lw=1.5,
             linestyle="--", label="Constraint Feedback Signal")
    ax4.plot(ct, cross_data["low_Q_capital_flow"],  color=ACCENT5, lw=1.5,
             linestyle=":", label="Capital Flow → Low-Q Structures")
    ax4.fill_between(ct,
                     np.array(cross_data["Q_legal"]),
                     np.array(cross_data["D_econ"]),
                     where=np.array(cross_data["D_econ"]) > np.array(cross_data["Q_legal"]),
                     alpha=0.10, color=ACCENT2, label="Dual Deficit Zone")

    # Mark crossover
    crossover = next((i for i, (q, d) in enumerate(
        zip(cross_data["Q_legal"], cross_data["D_econ"])) if d > q), None)
    if crossover:
        ax4.axvline(crossover, color=WARN_C, linestyle="--", lw=1.2, alpha=0.8)
        ax4.annotate(f"D_econ > Q_legal\nt = {crossover}",
                     xy=(crossover, cross_data["D_econ"][crossover]),
                     xytext=(crossover + 5, 0.7),
                     color=WARN_C, fontsize=8,
                     arrowprops=dict(arrowstyle="->", color=WARN_C, lw=1))

    ax4.set_xlabel("Time (operational cycles)")
    ax4.set_ylabel("Normalized Value  (0–1)")
    ax4.set_ylim(-0.05, 1.05)
    ax4.legend(fontsize=7.5, facecolor=BG, edgecolor=GRID_C, labelcolor=TEXT_C,
               loc="center right")

    # ── Panel 5: Phase Portrait — Combined Attractor ──────────────────────────
    ax5 = fig.add_subplot(gs[2, 0])
    style_ax(ax5, "5. Phase Portrait: Dual-Decoupling Attractor State")

    cmap = plt.cm.plasma
    n_traj = len(phase_data["trajectories"])
    for idx, traj in enumerate(phase_data["trajectories"]):
        color = cmap(idx / max(n_traj - 1, 1))
        ax5.plot(traj["Q"], traj["D"], color=color, lw=1.8, alpha=0.85)
        # Start marker
        ax5.scatter(traj["Q"][0], traj["D"][0], color=color, s=60, zorder=5,
                    marker="o", edgecolors="white", linewidths=0.5)
        # Mid-trajectory arrow
        mid = len(traj["Q"]) // 2
        ax5.annotate("", xy=(traj["Q"][mid], traj["D"][mid]),
                     xytext=(traj["Q"][mid - 3], traj["D"][mid - 3]),
                     arrowprops=dict(arrowstyle="->", color=color, lw=1.5))

    # Attractor region
    ax5.axhspan(0.88, 1.0, alpha=0.08, color=ACCENT2, label="Attractor Region\n(Q→0, D→1)")
    ax5.axvspan(0.0, 0.08, alpha=0.08, color=ACCENT2)

    # Diagonal: D_econ = 1 - Q_legal (equal decoupling line)
    q_line = np.linspace(0, 1, 100)
    ax5.plot(q_line, 1 - q_line, color=GRID_C, lw=1, linestyle=":",
             label="D = 1 − Q  (symmetric decoupling)")

    ax5.set_xlabel("Legal Q  (attribution clarity)", color=TEXT_C)
    ax5.set_ylabel("Economic D(t)  (valuation decoupling)", color=TEXT_C)
    ax5.set_xlim(-0.02, 1.0)
    ax5.set_ylim(-0.02, 1.05)
    ax5.legend(fontsize=7.5, facecolor=BG, edgecolor=GRID_C, labelcolor=TEXT_C)

    # ── Panel 6: Crisis Anatomy ───────────────────────────────────────────────
    ax6 = fig.add_subplot(gs[2, 1])
    style_ax(ax6, "6. Crisis Anatomy: Constraint Breach, Schema Response, Drift Resumption")

    ct2 = crisis_data["t"]
    ca  = crisis_data["crisis_at"]

    ax6.plot(ct2, crisis_data["price"],      color=ACCENT2, lw=2,
             label="Price Index")
    ax6.plot(ct2, crisis_data["constraint"], color=ACCENT3, lw=2,
             label="Constraint Index")
    ax6.plot(ct2, crisis_data["D_econ"],     color=ACCENT4, lw=1.5,
             linestyle="--", label="D_econ")
    ax6.plot(ct2, crisis_data["schema_response"], color=ACCENT5, lw=1.5,
             linestyle=":", label="Schema Response Intensity")
    ax6.plot(ct2, crisis_data["coupling_restoration"], color=ACCENT, lw=1.5,
             linestyle="-.", label="Coupling Restoration (temporary)")

    # Shade pre-crisis, crisis, post-crisis
    ax6.axvspan(0, ca, alpha=0.04, color=ACCENT3, label="Pre-Crisis Drift")
    ax6.axvspan(ca, ca + 15, alpha=0.12, color=ACCENT2, label="Crisis Window")
    ax6.axvspan(ca + 15, max(ct2), alpha=0.04, color=ACCENT4, label="Post-Crisis Drift Resumes")

    ax6.axvline(ca, color=WARN_C, lw=1.5, linestyle="--")
    ax6.annotate("Constraint\nbreach", xy=(ca, 0.9),
                 xytext=(ca - 18, 0.85), color=WARN_C, fontsize=8,
                 arrowprops=dict(arrowstyle="->", color=WARN_C, lw=1))

    ax6.set_xlabel("Time (cycles)")
    ax6.set_ylabel("Normalized Value")
    ax6.legend(fontsize=7.5, facecolor=BG, edgecolor=GRID_C, labelcolor=TEXT_C,
               loc="upper left", ncol=2)

    # ── Super-title ───────────────────────────────────────────────────────────
    fig.suptitle(
        "Thermodynamic Accountability Framework — Valuation Decoupling & Cross-System Coupling",
        color=TITLE_C, fontsize=13.5, fontweight="bold", y=0.99
    )

    plt.savefig(output_path, dpi=150, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"[TAF-VAL] Figure saved → {output_path}")

    return {
        "valuation": val_data,
        "cross_system": cross_data,
        "phase": phase_data,
        "crisis": crisis_data,
    }


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 6: TEXT REPORT
# ─────────────────────────────────────────────────────────────────────────────

def print_report(results: dict):
    """Print a structured text report of all simulation results."""

    print("\n" + "=" * 72)
    print("  THERMODYNAMIC ACCOUNTABILITY FRAMEWORK")
    print("  VALUATION DECOUPLING SIMULATION REPORT")
    print("=" * 72)

    # ── 1. Valuation Decoupling ───────────────────────────────────────────────
    v = results["valuation"]
    print("\n── 1. VALUATION DECOUPLING ─────────────────────────────────────────")
    print(f"  Price Index at t=0:      {v['price'][0]:.3f}  |  "
          f"at t=final: {v['price'][-1]:.3f}")
    print(f"  Constraint Index at t=0: {v['constraint'][0]:.3f}  |  "
          f"at t=final: {v['constraint'][-1]:.3f}")
    print(f"  eROI at t=0:             {v['eROI'][0]:.2f}   |  "
          f"at t=final: {v['eROI'][-1]:.2f}")
    print(f"  D_econ at t=0:           {v['D_econ'][0]:.3f}  |  "
          f"at t=final: {v['D_econ'][-1]:.3f}")
    final_gap = v['price'][-1] - v['constraint'][-1]
    print(f"  Valuation gap at t=final: {final_gap:.3f}")
    print(f"  → Price is {final_gap / max(v['constraint'][-1], 0.001) * 100:.0f}% above "
          f"constraint-bound value at end of simulation")

    # ── 2. Cross-System Coupling ──────────────────────────────────────────────
    c = results["cross_system"]
    print("\n── 2. CROSS-SYSTEM COUPLING ────────────────────────────────────────")
    print(f"  Legal Q at t=0:  {c['Q_legal'][0]:.3f}  |  at t=final: {c['Q_legal'][-1]:.3f}")
    print(f"  D_econ at t=0:   {c['D_econ'][0]:.3f}  |  at t=final: {c['D_econ'][-1]:.3f}")
    crossover = next((i for i, (q, d) in enumerate(
        zip(c["Q_legal"], c["D_econ"])) if d > q), None)
    if crossover:
        print(f"  D_econ exceeds Q_legal at cycle: {crossover}")
    print(f"  Constraint feedback at t=final:  {c['constraint_feedback'][-1]:.3f}")
    print(f"  Low-Q capital flow at t=final:   {c['low_Q_capital_flow'][-1]:.3f}")
    print(f"  Combined system stress at t=final: {c['combined_stress'][-1]:.3f}")

    # ── 3. Phase Portrait ─────────────────────────────────────────────────────
    p = results["phase"]
    print("\n── 3. PHASE PORTRAIT — ATTRACTOR CONVERGENCE ──────────────────────")
    for i, traj in enumerate(p["trajectories"]):
        print(f"  Trajectory {i+1}: start ({traj['start'][0]:.2f}, {traj['start'][1]:.2f}) "
              f"→ end ({traj['Q'][-1]:.3f}, {traj['D'][-1]:.3f})")

    # ── 4. Crisis Anatomy ─────────────────────────────────────────────────────
    cr = results["crisis"]
    ca = cr["crisis_at"]
    print("\n── 4. CRISIS ANATOMY ───────────────────────────────────────────────")
    print(f"  Crisis at cycle: {ca}")
    print(f"  Price at crisis onset:  {cr['price'][ca]:.3f}")
    print(f"  Constraint at crisis:   {cr['constraint'][ca]:.3f}")
    print(f"  D_econ pre-crisis:      {cr['D_econ'][ca-1]:.3f}")
    print(f"  D_econ at crisis:       {cr['D_econ'][ca]:.3f}  (temporary coupling restoration)")
    print(f"  D_econ post-crisis:     {cr['D_econ'][-1]:.3f}  (drift resumes)")
    pre_gap  = cr['price'][ca-1] - cr['constraint'][ca-1]
    post_gap = cr['price'][-1]   - cr['constraint'][-1]
    print(f"  Valuation gap pre-crisis:  {pre_gap:.3f}")
    print(f"  Valuation gap post-crisis: {post_gap:.3f}")
    print(f"  → Post-crisis gap is {post_gap/max(pre_gap,0.001)*100:.0f}% of pre-crisis gap")
    print(f"    (schema absorbs shock; drift resumes at higher baseline)")

    print("\n" + "=" * 72)
    print("  IMPLICATIONS")
    print("=" * 72)
    print("""
  The simulation reveals four structural implications:

  1. PRICE AS PROJECTION OPERATOR
     Price does not measure constraint-bound value. It measures capital
     accessibility × expectation density × narrative coherence. The gap
     between price and constraint-bound productivity grows monotonically
     as long as liquidity and narrative reinforcement exceed constraint
     signal strength. This is not mispricing. It is the correct output
     of a system optimizing for internal coherence.

  2. STABILITY ILLUSION
     Internal coherence metrics (volatility, clearing efficiency) remain
     healthy throughout the decoupling process. The system appears to be
     functioning correctly while drifting arbitrarily far from physical
     constraints. Stability is defined by the schema, not by correspondence
     to thermodynamic reality.

  3. CROSS-SYSTEM AMPLIFICATION
     Legal Q degradation and economic D(t) are not independent. Capital
     flows to low-Q structures (AI-intermediated, offshore, complex
     derivatives) accelerate legal Q decay. Reduced enforcement reduces
     constraint feedback to valuation systems, accelerating D_econ growth.
     The two systems form a positive feedback loop converging toward the
     same attractor: Q → 0, D → 1.

  4. CRISIS AS SCHEMA EVENT, NOT REALITY EVENT
     When constraint breach occurs, the system responds with schema tools
     (liquidity injection, circuit breakers, central bank backstops). These
     restore internal coherence without restoring constraint coupling.
     D_econ temporarily decreases, then resumes growth at a higher baseline.
     The system learns to absorb reality shocks without coupling to reality.
     Each crisis cycle leaves the system more decoupled than before.
""")


# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import os
    out_dir = os.path.dirname(os.path.abspath(__file__))
    img_path = os.path.join(out_dir, "valuation_decoupling_sim.png")

    results = run_and_plot(output_path=img_path)
    print_report(results)
