"""
schema_evolution_sim.py
=======================
Thermodynamic Accountability Framework — Schema Evolution Simulation

Models ΔSchema(t): how representational space changes over time under
the competing pressures of litigation, administrative optimization,
structural alignment S, and infrastructure lock-in.

Core dynamics from ToWorkOn.md:

  ΔSchema(t) = f( D(t)·{litigation, admin feedback}, S, infrastructure )

  Q splits into Q_phys (physical causality) and Q_leg (legally representable).
  D(t) controls covariance between them.

  A(t) is endogenous: shaped by S, not a neutral institutional pivot.
  The reflexivity loop: low Q → S shapes A(t) upward → higher A(t) →
  lower Q_eff → lower effective Q → loop repeats.

  Pre-emptive exclusion threshold: when schema crosses from post-hoc
  (descriptive) to pre-emptive (generative constraint), Q_non-representable
  becomes structurally unrecoverable.

Four simulation panels:
  1. Schema Width & Q Partition over time
  2. A(t) Reflexivity: S-shaped administrative time vs. enforcement capacity
  3. Pre-emptive Exclusion Threshold crossing
  4. ΔSchema(t) force decomposition (litigation vs. contraction pressures)

CC0. Requires: numpy, matplotlib, taf_primitives
"""

from __future__ import annotations

import random
from typing import Optional

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np

from taf_primitives import (
    QState, SchemaState,
    Q_effective, instability_signal,
    clamp, logistic_growth, sigmoid_decay,
    Q_FLOOR, D_CEILING, PREEMPTIVE_THRESHOLD, DEFAULT_R_EA,
)


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 1: SCHEMA EVOLUTION MODEL
# ─────────────────────────────────────────────────────────────────────────────

def schema_evolution_sim(
    t_max: int = 120,
    schema_width_0: float = 0.80,
    Q_phys_0: float = 0.85,
    Q_leg_0: float = 0.78,
    D_0: float = 0.08,
    S_alignment: float = 0.40,
    litigation_P_0: float = 0.25,
    admin_feedback_0: float = 0.18,
    infra_lock_0: float = 0.25,
    A_t_0: float = 1.0,
    A_t_S_sensitivity: float = 0.35,
    F_0: float = 2.0,
    F_growth: float = 0.08,
    R_Ea_0: float = DEFAULT_R_EA,
    rng_seed: int = 17,
) -> dict:
    rng = random.Random(rng_seed)

    schema_width    = schema_width_0
    Q_phys          = Q_phys_0
    Q_leg           = Q_leg_0
    D               = D_0
    A_t             = A_t_0
    F               = F_0
    R_Ea            = R_Ea_0
    litigation_P    = litigation_P_0
    admin_feedback  = admin_feedback_0
    infra_lock      = infra_lock_0

    t_series              = []
    schema_width_series   = []
    Q_phys_series         = []
    Q_leg_series          = []
    Q_eff_series          = []
    Q_gap_series          = []
    D_series              = []
    A_t_series            = []
    instability_series    = []
    preemptive_series     = []
    delta_schema_series   = []
    expansion_series      = []
    contraction_series    = []
    F_series              = []
    R_Ea_series           = []

    preemptive_crossed = False
    preemptive_t       = None

    for i in range(t_max):
        t_series.append(i)

        schema_width_series.append(round(schema_width, 4))
        Q_phys_series.append(round(Q_phys, 4))
        Q_leg_series.append(round(Q_leg, 4))
        Q_eff_val = Q_effective(Q_leg, D, A_t)
        Q_eff_series.append(round(Q_eff_val, 4))
        Q_gap = max(0.0, Q_phys - Q_leg)
        Q_gap_series.append(round(Q_gap, 4))
        D_series.append(round(D, 4))
        A_t_series.append(round(A_t, 4))
        instab = instability_signal(F, Q_eff_val, R_Ea)
        instability_series.append(round(instab, 4))
        F_series.append(round(F, 4))
        R_Ea_series.append(round(R_Ea, 4))

        in_preemptive = Q_gap > PREEMPTIVE_THRESHOLD * Q_phys
        preemptive_series.append(1 if in_preemptive else 0)
        if in_preemptive and not preemptive_crossed:
            preemptive_crossed = True
            preemptive_t = i

        # ΔSchema(t)
        expansion   = max(0.0, (1.0 - D) * litigation_P * 0.04)
        contraction = (
            admin_feedback * 0.025
            + S_alignment  * 0.030
            + infra_lock   * 0.015
        )
        dS = expansion - contraction + rng.gauss(0, 0.005)
        delta_schema_series.append(round(dS, 5))
        expansion_series.append(round(expansion, 5))
        contraction_series.append(round(contraction, 5))

        # Update schema width
        schema_width = clamp(schema_width + dS, 0.02, 0.98)

        # Q_leg tracks schema width
        Q_leg = clamp(Q_leg + dS * 0.6 + rng.gauss(0, 0.004), Q_FLOOR, Q_phys)

        # Q_phys decays slowly
        Q_phys = clamp(Q_phys - 0.003 + rng.gauss(0, 0.003), Q_FLOOR, 1.0)

        # D grows with Q gap
        D = clamp(
            D + Q_gap * 0.008 + S_alignment * 0.003 + rng.gauss(0, 0.002),
            0.0, D_CEILING
        )

        # A(t) reflexivity — capped at 20x baseline (realistic enforcement backlog max)
        A_t_growth = (
            A_t_S_sensitivity * S_alignment * 0.02
            + max(0, min(instab, 5.0)) * 0.003
            + rng.gauss(0, 0.008)
        )
        A_t = max(0.5, min(20.0, A_t + A_t_growth))

        # Litigation pressure
        litigation_P = clamp(
            litigation_P + max(0, instab) * 0.003 - A_t * 0.002 + rng.gauss(0, 0.005),
            0.02, 0.80
        )

        # Admin feedback
        admin_feedback = clamp(
            admin_feedback + 0.001 + rng.gauss(0, 0.003),
            0.05, 0.60
        )

        # Infrastructure lock-in
        infra_lock = clamp(infra_lock + 0.003 + rng.gauss(0, 0.002), 0.0, 0.95)

        # F grows
        F *= (1 + F_growth + rng.gauss(0, 0.01))

        # R × Ea erodes under enforcement overload
        if instab > 0:
            R_Ea = max(1.0, R_Ea - 0.04)

    return {
        "t":              t_series,
        "schema_width":   schema_width_series,
        "Q_phys":         Q_phys_series,
        "Q_leg":          Q_leg_series,
        "Q_eff":          Q_eff_series,
        "Q_gap":          Q_gap_series,
        "D":              D_series,
        "A_t":            A_t_series,
        "instability":    instability_series,
        "preemptive":     preemptive_series,
        "delta_schema":   delta_schema_series,
        "expansion":      expansion_series,
        "contraction":    contraction_series,
        "F":              F_series,
        "R_Ea":           R_Ea_series,
        "preemptive_t":   preemptive_t,
    }


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 2: VISUALIZATION
# ─────────────────────────────────────────────────────────────────────────────

BG      = "#161b22"
GRID_C  = "#30363d"
TEXT_C  = "#c9d1d9"
TITLE_C = "#e6edf3"
WARN_C  = "#f0e68c"
ACCENT  = "#58a6ff"
ACCENT2 = "#f78166"
ACCENT3 = "#3fb950"
ACCENT4 = "#d2a8ff"
ACCENT5 = "#ffa657"
FIG_BG  = "#0d1117"


def style_ax(ax, title: str):
    ax.set_facecolor(BG)
    for spine in ax.spines.values():
        spine.set_edgecolor(GRID_C)
    ax.tick_params(colors=TEXT_C, labelsize=9)
    ax.xaxis.label.set_color(TEXT_C)
    ax.yaxis.label.set_color(TEXT_C)
    ax.set_title(title, color=TITLE_C, fontsize=10.5, fontweight="bold", pad=9)
    ax.grid(color=GRID_C, linestyle="--", linewidth=0.5, alpha=0.6)


def run_and_plot(output_path: str = "schema_evolution_sim.png") -> dict:
    data = schema_evolution_sim()
    t    = data["t"]
    pt   = data["preemptive_t"]

    fig = plt.figure(figsize=(18, 14))
    fig.patch.set_facecolor(FIG_BG)
    gs  = gridspec.GridSpec(2, 2, figure=fig, hspace=0.42, wspace=0.30)

    # Panel 1: Schema Width & Q Partition
    ax1 = fig.add_subplot(gs[0, 0])
    style_ax(ax1, "1. Schema Width & Q Partition")
    ax1.plot(t, data["schema_width"], color=ACCENT,  lw=2, label="Schema Width")
    ax1.plot(t, data["Q_phys"],       color=ACCENT3, lw=2, label="Q_phys")
    ax1.plot(t, data["Q_leg"],        color=ACCENT2, lw=2, label="Q_leg")
    ax1.plot(t, data["Q_eff"],        color=ACCENT4, lw=1.5, linestyle="--", label="Q_eff")
    ax1.fill_between(t, np.array(data["Q_phys"]), np.array(data["Q_leg"]),
                     alpha=0.15, color=ACCENT2, label="Q_non-representable gap")
    if pt:
        ax1.axvline(pt, color=WARN_C, lw=1.5, linestyle="--")
        ax1.annotate(f"Pre-emptive\nt = {pt}", xy=(pt, 0.55), xytext=(pt + 5, 0.65),
                     color=WARN_C, fontsize=8,
                     arrowprops=dict(arrowstyle="->", color=WARN_C, lw=1))
    ax1.set_xlabel("Time (cycles)"); ax1.set_ylabel("Normalized Value (0-1)")
    ax1.set_ylim(-0.02, 1.05)
    ax1.legend(fontsize=7.5, facecolor=BG, edgecolor=GRID_C, labelcolor=TEXT_C)

    # Panel 2: A(t) Reflexivity
    ax2 = fig.add_subplot(gs[0, 1])
    style_ax(ax2, "2. A(t) Reflexivity: S-Shaped Administrative Time")
    ax2_twin = ax2.twinx()
    ax2_twin.set_facecolor(BG)
    ax2_twin.tick_params(colors=ACCENT2, labelsize=9)
    for sp in ax2_twin.spines.values():
        sp.set_edgecolor(GRID_C)
    ax2_twin.spines["right"].set_edgecolor(ACCENT2)
    ax2.plot(t, data["A_t"],         color=ACCENT5, lw=2, label="A(t) (left)")
    ax2.plot(t, data["instability"],  color=ACCENT,  lw=1.5, linestyle="--",
             label="Instability signal (left)")
    ax2.axhline(0, color=GRID_C, lw=1, linestyle=":")
    ax2_twin.plot(t, data["Q_eff"], color=ACCENT2, lw=2, label="Q_eff (right)")
    ax2_twin.set_ylabel("Q_eff", color=ACCENT2)
    ax2.fill_between(t, np.array(data["instability"]), 0,
                     where=np.array(data["instability"]) > 0,
                     alpha=0.10, color=ACCENT, label="Enforcement deficit")
    lines1, labs1 = ax2.get_legend_handles_labels()
    lines2, labs2 = ax2_twin.get_legend_handles_labels()
    ax2.legend(lines1 + lines2, labs1 + labs2,
               fontsize=7.5, facecolor=BG, edgecolor=GRID_C, labelcolor=TEXT_C)
    ax2.set_xlabel("Time (cycles)"); ax2.set_ylabel("A(t) / Instability Signal")

    # Panel 3: Pre-emptive Exclusion
    ax3 = fig.add_subplot(gs[1, 0])
    style_ax(ax3, "3. Pre-Emptive Exclusion: Q Partition Dynamics")
    ax3.plot(t, data["Q_phys"], color=ACCENT3, lw=2, label="Q_phys")
    ax3.plot(t, data["Q_leg"],  color=ACCENT2, lw=2, label="Q_leg")
    ax3.plot(t, data["Q_gap"],  color=ACCENT5, lw=2, label="Q_gap")
    ax3.plot(t, data["D"],      color=ACCENT4, lw=1.5, linestyle="--", label="D(t)")
    Q_phys_arr = np.array(data["Q_phys"])
    ax3.plot(t, Q_phys_arr * PREEMPTIVE_THRESHOLD, color=WARN_C, lw=1, linestyle=":",
             label=f"Pre-emptive threshold ({PREEMPTIVE_THRESHOLD:.0%} x Q_phys)")
    if pt:
        ax3.axvspan(pt, max(t), alpha=0.06, color=ACCENT2, label="Pre-emptive regime")
        ax3.axvline(pt, color=WARN_C, lw=1.5, linestyle="--")
        ax3.annotate("Schema becomes\npre-emptive here",
                     xy=(pt, data["Q_gap"][pt]), xytext=(pt + 6, data["Q_gap"][pt] + 0.08),
                     color=WARN_C, fontsize=8,
                     arrowprops=dict(arrowstyle="->", color=WARN_C, lw=1))
    ax3.set_xlabel("Time (cycles)"); ax3.set_ylabel("Normalized Q Value (0-1)")
    ax3.set_ylim(-0.02, 1.05)
    ax3.legend(fontsize=7.5, facecolor=BG, edgecolor=GRID_C, labelcolor=TEXT_C,
               loc="center right")

    # Panel 4: ΔSchema Force Decomposition
    ax4 = fig.add_subplot(gs[1, 1])
    style_ax(ax4, "4. Delta Schema(t) Force Decomposition")
    ax4.plot(t, data["expansion"],    color=ACCENT3, lw=2, label="Expansion (litigation, D-gated)")
    ax4.plot(t, data["contraction"],  color=ACCENT2, lw=2, label="Contraction (admin + S + infra)")
    ax4.plot(t, data["delta_schema"], color=ACCENT,  lw=1.5, linestyle="--", label="Net delta Schema(t)")
    ax4.axhline(0, color=GRID_C, lw=1, linestyle=":")
    ax4.fill_between(t, np.array(data["delta_schema"]), 0,
                     where=np.array(data["delta_schema"]) < 0,
                     alpha=0.12, color=ACCENT2, label="Net contraction zone")
    ax4.fill_between(t, np.array(data["delta_schema"]), 0,
                     where=np.array(data["delta_schema"]) >= 0,
                     alpha=0.08, color=ACCENT3, label="Net expansion zone")
    crossover = next((i for i, v in enumerate(data["delta_schema"]) if v < 0), None)
    if crossover:
        ax4.axvline(crossover, color=WARN_C, lw=1.2, linestyle="--", alpha=0.8)
        ax4.annotate(f"Contraction dominates\nt = {crossover}",
                     xy=(crossover, data["delta_schema"][crossover]),
                     xytext=(crossover + 5, 0.005),
                     color=WARN_C, fontsize=8,
                     arrowprops=dict(arrowstyle="->", color=WARN_C, lw=1))
    ax4.set_xlabel("Time (cycles)"); ax4.set_ylabel("Delta Schema Magnitude")
    ax4.legend(fontsize=7.5, facecolor=BG, edgecolor=GRID_C, labelcolor=TEXT_C)

    fig.suptitle(
        "Thermodynamic Accountability Framework — Schema Evolution & Q Partition",
        color=TITLE_C, fontsize=13, fontweight="bold", y=0.99
    )
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"[TAF-SCHEMA] Figure saved -> {output_path}")
    return data


# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import os
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schema_evolution_sim.png")
    data = run_and_plot(out)
    pt = data["preemptive_t"]
    print(f"\n  Schema width:  {data['schema_width'][0]:.3f} -> {data['schema_width'][-1]:.3f}")
    print(f"  Q_phys:        {data['Q_phys'][0]:.3f} -> {data['Q_phys'][-1]:.3f}")
    print(f"  Q_leg:         {data['Q_leg'][0]:.3f} -> {data['Q_leg'][-1]:.3f}")
    print(f"  Q_eff:         {data['Q_eff'][0]:.3f} -> {data['Q_eff'][-1]:.3f}")
    print(f"  D(t):          {data['D'][0]:.3f} -> {data['D'][-1]:.3f}")
    print(f"  A(t):          {data['A_t'][0]:.3f} -> {data['A_t'][-1]:.3f}")
    print(f"  Pre-emptive threshold crossed at: t = {pt}")
    print(f"  Final instability signal: {data['instability'][-1]:.3f}")
