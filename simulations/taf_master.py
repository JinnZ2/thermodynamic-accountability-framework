"""
taf_master.py
=============
Thermodynamic Accountability Framework — Master Orchestrator

Single entry point for the entire TAF simulation suite.
Runs all modules, produces a unified 12-panel composite figure,
and prints a full cross-system report.

Module registry:
  1. liability_routing_sim     — Q degradation, instability threshold, schema D(t)
  2. valuation_decoupling_sim  — price/constraint, eROI, cross-system coupling, crisis
  3. schema_evolution_sim      — ΔSchema(t), Q partition, A(t) reflexivity
  4. admissibility_field_sim   — 𝒜(t) components, Πᵢ survival, D(t) operator
  5. cognitive_decoupling_sim  — population bifurcation, anchoring dynamics

Usage:
  python3 taf_master.py                    # run all, save composite + individual figures
  python3 taf_master.py --modules schema admiss   # run subset
  python3 taf_master.py --no-individual    # skip individual figures
  python3 taf_master.py --report-only      # print report, no figures

CC0. Requires: numpy, matplotlib, all TAF sim modules in same directory.
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from typing import Optional

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np

# ── Add simulations directory to path ────────────────────────────────────────
SIM_DIR = os.path.dirname(os.path.abspath(__file__))
if SIM_DIR not in sys.path:
    sys.path.insert(0, SIM_DIR)

# ── Import all simulation modules ─────────────────────────────────────────────
from taf_primitives import (
    DEFAULT_R_EA, PREEMPTIVE_THRESHOLD, D_CEILING,
)
from liability_routing_sim import (
    q_degradation_curve,
    instability_threshold_sim,
    schema_evolution_sim as schema_D_sim,
)
from valuation_decoupling_sim import (
    valuation_decoupling_sim,
    cross_system_coupling_sim,
    crisis_anatomy_sim,
)
from schema_evolution_sim import (
    schema_evolution_sim,
)
from admissibility_field_sim import (
    admissibility_field_sim,
)
from cognitive_decoupling_sim import (
    cognitive_decoupling_sim,
)


# ─────────────────────────────────────────────────────────────────────────────
# STYLE CONSTANTS
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


def style_ax(ax, title: str, fontsize: float = 9.5):
    ax.set_facecolor(BG)
    for spine in ax.spines.values():
        spine.set_edgecolor(GRID_C)
    ax.tick_params(colors=TEXT_C, labelsize=8)
    ax.xaxis.label.set_color(TEXT_C)
    ax.yaxis.label.set_color(TEXT_C)
    ax.set_title(title, color=TITLE_C, fontsize=fontsize,
                 fontweight="bold", pad=7)
    ax.grid(color=GRID_C, linestyle="--", linewidth=0.4, alpha=0.5)


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 1: RUN ALL SIMULATIONS
# ─────────────────────────────────────────────────────────────────────────────

def run_all_simulations(verbose: bool = True) -> dict:
    """Run all TAF simulation modules and return their data."""
    results = {}

    def run(name, fn, *args, **kwargs):
        if verbose:
            print(f"  [TAF-MASTER] Running {name}...", end=" ", flush=True)
        t0 = time.time()
        results[name] = fn(*args, **kwargs)
        if verbose:
            print(f"done ({time.time() - t0:.2f}s)")

    # Liability routing
    run("Q_decay",      q_degradation_curve)
    run("instability",  instability_threshold_sim)
    run("schema_D",     schema_D_sim)

    # Valuation decoupling
    run("valuation",    valuation_decoupling_sim, t_max=100)
    run("cross_system", cross_system_coupling_sim, t_max=100)
    run("crisis",       crisis_anatomy_sim, t_max=120, crisis_at=65)

    # Schema evolution
    run("schema_evo",   schema_evolution_sim, t_max=120)

    # Admissibility field
    run("admiss",       admissibility_field_sim, t_max=100)

    # Cognitive decoupling
    run("cognitive",    cognitive_decoupling_sim, t_max=100)

    return results


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 2: COMPOSITE 12-PANEL FIGURE
# ─────────────────────────────────────────────────────────────────────────────

def build_composite_figure(results: dict, output_path: str):
    """
    Build a 12-panel composite figure spanning all five simulation modules.

    Layout (4 rows × 3 cols):
      Row 1: Liability routing | Q degradation | Instability threshold
      Row 2: Valuation gap     | Cross-system coupling | Crisis anatomy
      Row 3: Schema width/Q    | ΔSchema forces | A(t) reflexivity
      Row 4: 𝒜(t) span/D(t)   | Πᵢ survival   | Cognitive bifurcation
    """
    fig = plt.figure(figsize=(24, 26))
    fig.patch.set_facecolor(FIG_BG)
    gs  = gridspec.GridSpec(4, 3, figure=fig, hspace=0.50, wspace=0.28)

    # ── Row 1: Liability Routing ──────────────────────────────────────────────

    # Panel 1.1: Q Degradation (AI vs. Corporate)
    ax = fig.add_subplot(gs[0, 0])
    style_ax(ax, "1. Q Degradation: AI vs. Corporate")
    qd = results["Q_decay"]
    t  = list(range(len(qd["q_ai"])))
    ax.plot(t, qd["q_ai"],        color=ACCENT2, lw=2, label="AI Q (fast decay)")
    ax.plot(t, qd["q_corporate"], color=ACCENT3, lw=2, label="Corporate Q (slow decay)")
    ax.set_xlabel("Deployment cycles"); ax.set_ylabel("Q")
    ax.legend(fontsize=7, facecolor=BG, edgecolor=GRID_C, labelcolor=TEXT_C)

    # Panel 1.2: Instability Threshold
    ax = fig.add_subplot(gs[0, 1])
    style_ax(ax, "2. Instability Threshold: F/Q vs. R×Eₐ")
    ins = results["instability"]
    t   = list(range(len(ins["demand"])))
    # demand = F/Q, supply = R*Ea
    ax.plot(t, ins["demand"], color=ACCENT2, lw=2, label="F/Q (demand)")
    ax.plot(t, ins["supply"], color=ACCENT3, lw=1.5, linestyle="--", label="R×Eₐ (supply)")
    cross = ins.get("threshold_crossed_at")
    if cross is not None:
        ax.fill_between(t, ins["demand"], ins["supply"],
                        where=[d > s for d, s in zip(ins["demand"], ins["supply"])],
                        alpha=0.15, color=ACCENT2)
        ax.axvline(cross, color=WARN_C, lw=1, linestyle=":")
        ax.annotate(f"t={cross}", xy=(cross, ins["supply"][cross] + 0.5),
                    color=WARN_C, fontsize=7.5)
    ax.set_xlabel("Cycles"); ax.set_ylabel("F/Q")
    # Cap y-axis for readability — exponential growth is the point, not the magnitude
    ax.set_ylim(0, max(ins["supply"]) * 8)
    ax.legend(fontsize=7, facecolor=BG, edgecolor=GRID_C, labelcolor=TEXT_C)

    # Panel 1.3: Schema Decoupling D(t) — Legal
    ax = fig.add_subplot(gs[0, 2])
    style_ax(ax, "3. Schema Decoupling: Q_phys vs. Q_leg")
    sd = results["schema_D"]
    t  = list(range(len(sd["q_phys"])))
    ax.plot(t, sd["q_phys"], color=ACCENT3, lw=2, label="Q_phys")
    ax.plot(t, sd["q_leg"],  color=ACCENT2, lw=2, label="Q_leg")
    ax.fill_between(t, sd["q_phys"], sd["q_leg"],
                    alpha=0.15, color=ACCENT2, label="Decoupling gap")
    ax.set_xlabel("Cycles"); ax.set_ylabel("Q")
    ax.legend(fontsize=7, facecolor=BG, edgecolor=GRID_C, labelcolor=TEXT_C)

    # ── Row 2: Valuation Decoupling ───────────────────────────────────────────

    # Panel 2.1: Price vs. Constraint
    ax = fig.add_subplot(gs[1, 0])
    style_ax(ax, "4. Price vs. Constraint-Bound Value")
    vd = results["valuation"]
    t  = vd["t"]
    ax.plot(t, vd["price"],      color=ACCENT2, lw=2, label="Price")
    ax.plot(t, vd["constraint"], color=ACCENT3, lw=2, label="Constraint")
    ax.fill_between(t,
                    np.array(vd["price"]),
                    np.array(vd["constraint"]),
                    where=np.array(vd["price"]) > np.array(vd["constraint"]),
                    alpha=0.12, color=ACCENT2)
    ax.set_xlabel("Market cycles"); ax.set_ylabel("Normalized Value")
    ax.legend(fontsize=7, facecolor=BG, edgecolor=GRID_C, labelcolor=TEXT_C)

    # Panel 2.2: Cross-System Coupling
    ax = fig.add_subplot(gs[1, 1])
    style_ax(ax, "5. Cross-System Coupling: Legal Q ↔ Economic D(t)")
    cs = results["cross_system"]
    t  = cs["t"]
    ax.plot(t, cs["Q_legal"], color=ACCENT,  lw=2, label="Legal Q")
    ax.plot(t, cs["D_econ"],  color=ACCENT2, lw=2, label="Economic D(t)")
    ax.plot(t, cs["constraint_feedback"], color=ACCENT3, lw=1.5,
            linestyle="--", label="Constraint feedback")
    crossover = next((i for i, (q, d) in enumerate(
        zip(cs["Q_legal"], cs["D_econ"])) if d > q), None)
    if crossover:
        ax.axvline(crossover, color=WARN_C, lw=1, linestyle="--")
        ax.annotate(f"D>Q t={crossover}", xy=(crossover, 0.5),
                    color=WARN_C, fontsize=7.5)
    ax.set_xlabel("Cycles"); ax.set_ylabel("Normalized (0–1)")
    ax.legend(fontsize=7, facecolor=BG, edgecolor=GRID_C, labelcolor=TEXT_C)

    # Panel 2.3: Crisis Anatomy
    ax = fig.add_subplot(gs[1, 2])
    style_ax(ax, "6. Crisis Anatomy: Breach, Response, Drift Resumption")
    cr = results["crisis"]
    t  = cr["t"]
    ca = cr["crisis_at"]
    ax.plot(t, cr["price"],      color=ACCENT2, lw=2, label="Price")
    ax.plot(t, cr["constraint"], color=ACCENT3, lw=2, label="Constraint")
    ax.plot(t, cr["D_econ"],     color=ACCENT4, lw=1.5, linestyle="--", label="D_econ")
    ax.axvspan(ca, ca + 15, alpha=0.10, color=ACCENT2)
    ax.axvline(ca, color=WARN_C, lw=1.2, linestyle="--")
    ax.annotate("Crisis", xy=(ca, 0.9), color=WARN_C, fontsize=7.5)
    ax.set_xlabel("Cycles"); ax.set_ylabel("Normalized Value")
    ax.legend(fontsize=7, facecolor=BG, edgecolor=GRID_C, labelcolor=TEXT_C)

    # ── Row 3: Schema Evolution ───────────────────────────────────────────────

    # Panel 3.1: Schema Width & Q Partition
    ax = fig.add_subplot(gs[2, 0])
    style_ax(ax, "7. Schema Width & Q Partition")
    se = results["schema_evo"]
    t  = se["t"]
    ax.plot(t, se["schema_width"], color=ACCENT,  lw=2, label="Schema width")
    ax.plot(t, se["Q_phys"],       color=ACCENT3, lw=2, label="Q_phys")
    ax.plot(t, se["Q_leg"],        color=ACCENT2, lw=2, label="Q_leg")
    ax.fill_between(t, np.array(se["Q_phys"]), np.array(se["Q_leg"]),
                    alpha=0.12, color=ACCENT2, label="Q gap")
    pt = se["preemptive_t"]
    if pt:
        ax.axvline(pt, color=WARN_C, lw=1, linestyle="--")
        ax.annotate(f"Pre-emptive t={pt}", xy=(pt, 0.6),
                    color=WARN_C, fontsize=7.5)
    ax.set_xlabel("Cycles"); ax.set_ylabel("Normalized (0–1)")
    ax.legend(fontsize=7, facecolor=BG, edgecolor=GRID_C, labelcolor=TEXT_C)

    # Panel 3.2: ΔSchema Force Decomposition
    ax = fig.add_subplot(gs[2, 1])
    style_ax(ax, "8. ΔSchema(t) Force Decomposition")
    ax.plot(t, se["expansion"],    color=ACCENT3, lw=2, label="Expansion (litigation)")
    ax.plot(t, se["contraction"],  color=ACCENT2, lw=2, label="Contraction (S + admin + infra)")
    ax.plot(t, se["delta_schema"], color=ACCENT,  lw=1.5, linestyle="--", label="Net ΔSchema")
    ax.axhline(0, color=GRID_C, lw=1, linestyle=":")
    ax.fill_between(t, np.array(se["delta_schema"]), 0,
                    where=np.array(se["delta_schema"]) < 0,
                    alpha=0.10, color=ACCENT2)
    ax.set_xlabel("Cycles"); ax.set_ylabel("ΔSchema Magnitude")
    ax.legend(fontsize=7, facecolor=BG, edgecolor=GRID_C, labelcolor=TEXT_C)

    # Panel 3.3: A(t) Reflexivity
    ax = fig.add_subplot(gs[2, 2])
    style_ax(ax, "9. A(t) Reflexivity: S-Shaped Administrative Time")
    ax.plot(t, se["A_t"],        color=ACCENT5, lw=2, label="A(t)")
    ax.plot(t, se["Q_eff"],      color=ACCENT2, lw=2, label="Q_eff")
    ax.plot(t, se["instability"], color=ACCENT,  lw=1.5, linestyle="--",
            label="Instability signal")
    ax.axhline(0, color=GRID_C, lw=1, linestyle=":")
    ax.fill_between(t, np.array(se["instability"]), 0,
                    where=np.array(se["instability"]) > 0,
                    alpha=0.08, color=ACCENT)
    ax.set_xlabel("Cycles"); ax.set_ylabel("Value")
    # Cap y-axis: instability signal grows exponentially; cap at 5x A(t) max for readability
    a_max = max(se["A_t"])
    ax.set_ylim(-a_max * 0.5, a_max * 5)
    ax.legend(fontsize=7, facecolor=BG, edgecolor=GRID_C, labelcolor=TEXT_C)

    # ── Row 4: Admissibility Field & Cognitive ────────────────────────────────

    # Panel 4.1: 𝒜(t) Span and D(t)
    ax = fig.add_subplot(gs[3, 0])
    style_ax(ax, "10. 𝒜(t) Span and D(t) = distance(𝒞, span(𝒜(t)))")
    ad = results["admiss"]
    t  = ad["t"]
    ax.plot(t, ad["span"],  color=ACCENT3, lw=2, label="span(𝒜(t))")
    ax.plot(t, ad["D_t"],   color=ACCENT2, lw=2, label="D(t)")
    ax.fill_between(t, np.array(ad["D_t"]), 0,
                    alpha=0.15, color=ACCENT2, label="Unrepresentable 𝒞")
    ax.set_xlabel("Cycles"); ax.set_ylabel("Fraction of 𝒞  (0–1)")
    ax.legend(fontsize=7, facecolor=BG, edgecolor=GRID_C, labelcolor=TEXT_C)

    # Panel 4.2: Compression Operator Survival
    ax = fig.add_subplot(gs[3, 1])
    style_ax(ax, "11. Compression Operator Survival: Πᵢ Admissibility Weights")
    ax.plot(t, ad["w_legal"],    color=ACCENT,  lw=2, label="Π_legal")
    ax.plot(t, ad["w_econ"],     color=ACCENT3, lw=2, label="Π_econ")
    ax.plot(t, ad["w_schema"],   color=ACCENT2, lw=2, label="Π_schema")
    ax.plot(t, ad["w_embodied"], color=ACCENT4, lw=2, label="Π_embodied")
    ax.set_xlabel("Cycles"); ax.set_ylabel("Admissibility Weight  (0–1)")
    ax.legend(fontsize=7, facecolor=BG, edgecolor=GRID_C, labelcolor=TEXT_C)

    # Panel 4.3: Cognitive Bifurcation
    ax = fig.add_subplot(gs[3, 2])
    style_ax(ax, "12. Cognitive Bifurcation & Perceptual Decoupling")
    cg = results["cognitive"]
    t  = cg["t"]
    ax.stackplot(t,
                 cg["frac_anchoring"],
                 cg["frac_coupled"],
                 cg["frac_mediated"],
                 colors=[ACCENT4, ACCENT3, ACCENT2],
                 alpha=0.70,
                 labels=["Anchoring", "𝒞-coupled", "𝒜(t)-mediated"])
    ax.plot(t, cg["D_perceptual"], color="white", lw=2, linestyle="--",
            label="D_perceptual")
    ax.set_xlabel("Generational cycles"); ax.set_ylabel("Fraction / D_perceptual")
    ax.legend(fontsize=7, facecolor=BG, edgecolor=GRID_C, labelcolor=TEXT_C,
              loc="upper left")

    # ── Super-title ───────────────────────────────────────────────────────────
    fig.suptitle(
        "Thermodynamic Accountability Framework — Full System Composite\n"
        "Liability · Valuation · Schema Evolution · Admissibility Field · Cognitive Decoupling",
        color=TITLE_C, fontsize=14, fontweight="bold", y=0.995
    )

    plt.savefig(output_path, dpi=130, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"[TAF-MASTER] Composite figure saved → {output_path}")


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 3: FULL CROSS-SYSTEM REPORT
# ─────────────────────────────────────────────────────────────────────────────

def print_full_report(results: dict):
    """Print a structured cross-system summary report."""

    sep = "=" * 72
    sub = "─" * 72

    print(f"\n{sep}")
    print("  THERMODYNAMIC ACCOUNTABILITY FRAMEWORK")
    print("  FULL SYSTEM REPORT")
    print(sep)

    # ── 1. Liability Routing ──────────────────────────────────────────────────
    print(f"\n{sub}")
    print("  MODULE 1: LIABILITY ROUTING & Q DEGRADATION")
    print(sub)
    qd = results["Q_decay"]
    print(f"  AI Q:         {qd['q_ai'][0]:.3f} → {qd['q_ai'][-1]:.4f}  "
          f"(near-zero at cycle {next((i for i,v in enumerate(qd['q_ai']) if v < 0.05), 'N/A')})")
    print(f"  Corporate Q:  {qd['q_corporate'][0]:.3f} → {qd['q_corporate'][-1]:.3f}")
    ins = results["instability"]
    cross = ins.get("threshold_crossed_at")
    print(f"  Instability threshold crossed at: cycle {cross}")

    # ── 2. Valuation Decoupling ───────────────────────────────────────────────
    print(f"\n{sub}")
    print("  MODULE 2: VALUATION DECOUPLING")
    print(sub)
    vd = results["valuation"]
    gap = vd["price"][-1] - vd["constraint"][-1]
    print(f"  Price:       {vd['price'][0]:.3f} → {vd['price'][-1]:.3f}")
    print(f"  Constraint:  {vd['constraint'][0]:.3f} → {vd['constraint'][-1]:.3f}")
    print(f"  Final gap:   {gap:.3f}  ({gap/max(vd['constraint'][-1],0.001)*100:.0f}% above constraint)")
    print(f"  eROI:        {vd['eROI'][0]:.2f} → {vd['eROI'][-1]:.2f}")
    cs = results["cross_system"]
    crossover = next((i for i, (q, d) in enumerate(
        zip(cs["Q_legal"], cs["D_econ"])) if d > q), None)
    print(f"  D_econ > Q_legal crossover: cycle {crossover}")
    cr = results["crisis"]
    ca = cr["crisis_at"]
    pre  = cr["price"][ca-1] - cr["constraint"][ca-1]
    post = cr["price"][-1]   - cr["constraint"][-1]
    print(f"  Crisis at cycle {ca}: post-crisis gap = {post/max(pre,0.001)*100:.0f}% of pre-crisis gap")

    # ── 3. Schema Evolution ───────────────────────────────────────────────────
    print(f"\n{sub}")
    print("  MODULE 3: SCHEMA EVOLUTION")
    print(sub)
    se = results["schema_evo"]
    print(f"  Schema width:  {se['schema_width'][0]:.3f} → {se['schema_width'][-1]:.3f}")
    print(f"  Q_phys:        {se['Q_phys'][0]:.3f} → {se['Q_phys'][-1]:.3f}")
    print(f"  Q_leg:         {se['Q_leg'][0]:.3f} → {se['Q_leg'][-1]:.3f}")
    print(f"  Q_eff:         {se['Q_eff'][0]:.3f} → {se['Q_eff'][-1]:.3f}")
    print(f"  A(t):          {se['A_t'][0]:.3f} → {se['A_t'][-1]:.3f}  (S-shaped growth)")
    print(f"  Pre-emptive threshold crossed at: cycle {se['preemptive_t']}")
    print(f"  Final instability signal: {se['instability'][-1]:.3f}")

    # ── 4. Admissibility Field ────────────────────────────────────────────────
    print(f"\n{sub}")
    print("  MODULE 4: ADMISSIBILITY FIELD 𝒜(t)")
    print(sub)
    ad = results["admiss"]
    print(f"  span(𝒜(t)):    {ad['span'][0]:.3f} → {ad['span'][-1]:.3f}")
    print(f"  D(t):          {ad['D_t'][0]:.3f} → {ad['D_t'][-1]:.3f}")
    print(f"  Π_legal:       {ad['w_legal'][0]:.3f} → {ad['w_legal'][-1]:.3f}")
    print(f"  Π_schema:      {ad['w_schema'][0]:.3f} → {ad['w_schema'][-1]:.3f}")
    print(f"  Π_embodied:    {ad['w_embodied'][0]:.3f} → {ad['w_embodied'][-1]:.3f}")
    print(f"  Layer 2 (compression coverage): {ad['layer2'][0]:.3f} → {ad['layer2'][-1]:.3f}")
    print(f"  Layer 3 (admissible class):     {ad['layer3'][0]:.3f} → {ad['layer3'][-1]:.3f}")
    inv = next((i for i, (s, e) in enumerate(
        zip(ad["w_schema"], ad["w_embodied"])) if s > e), None)
    print(f"  Π_schema > Π_embodied at: cycle {inv}")

    # ── 5. Cognitive Decoupling ───────────────────────────────────────────────
    print(f"\n{sub}")
    print("  MODULE 5: COGNITIVE DECOUPLING")
    print(sub)
    cg = results["cognitive"]
    print(f"  𝒞-coupled:     {cg['frac_coupled'][0]:.3f} → {cg['frac_coupled'][-1]:.3f}")
    print(f"  𝒜(t)-mediated: {cg['frac_mediated'][0]:.3f} → {cg['frac_mediated'][-1]:.3f}")
    print(f"  Anchoring pop: {cg['frac_anchoring'][0]:.3f} → {cg['frac_anchoring'][-1]:.3f}")
    print(f"  D_perceptual:  {cg['D_perceptual'][0]:.3f} → {cg['D_perceptual'][-1]:.3f}")
    print(f"  Detection signal: {cg['detection_signal'][0]:.3f} → {cg['detection_signal'][-1]:.3f}")
    print(f"  Schema normalization: {cg['schema_norm'][0]:.3f} → {cg['schema_norm'][-1]:.3f}")

    # ── Cross-System Summary ──────────────────────────────────────────────────
    print(f"\n{sep}")
    print("  CROSS-SYSTEM SUMMARY")
    print(sep)
    print("""
  All five modules converge on the same structural dynamic:

  LEGAL SYSTEM: Q degrades under AI deployment. Enforcement threshold
  crossed early. Schema crosses from post-hoc to pre-emptive. A(t) is
  endogenously shaped by S, making delay a feature not a bug.

  ECONOMIC SYSTEM: Price decouples from constraint-bound value under
  liquidity × narrative × credit. eROI erodes while financial return
  stays elevated. Crisis events restore internal coherence without
  restoring constraint coupling. Post-crisis gap exceeds pre-crisis gap.

  SCHEMA EVOLUTION: ΔSchema(t) is asymmetric. Contraction is cheaper
  and faster than expansion. D(t) gates reality input to schema update,
  making schema evolution increasingly self-referential. Q splits into
  Q_phys and Q_leg; the gap is the non-representable region.

  ADMISSIBILITY FIELD: 𝒜(t) narrows as S grows, E decays, C rises, L
  locks in. span(𝒜(t)) shrinks. D(t) = 1 - span grows. Π_embodied
  (direct 𝒞-coupled knowledge) loses admissibility first. Π_schema
  (AI/institutional grammars) gains admissibility. The selector is not
  an agent — it is the equilibrium of the compression constraint field.

  COGNITIVE LAYER: Population bifurcates into 𝒞-coupled and 𝒜(t)-
  mediated modes. Anchoring population (dyslexic, indigenous, repair-
  based) preserves direct 𝒞-coupling but erodes under institutional
  pressure. D_perceptual grows faster than D_external — the system
  appears more stable than it is. Detection signal reaching the broader
  system collapses as schema normalization increases.

  SHARED INVARIANT: All five systems exhibit the same terminal dynamic.
  Representational regimes optimize internal consistency under partial
  constraint visibility. Stability is defined by the schema, not by
  correspondence to physical reality. The attractor state is:
  Q → 0, D → 1, span(𝒜(t)) → 0, D_perceptual → 1.
""")
    print(sep)


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 4: INDIVIDUAL FIGURE DISPATCH
# ─────────────────────────────────────────────────────────────────────────────

def run_individual_figures(results: dict, out_dir: str):
    """Run each module's own plotting function to produce individual figures."""
    from schema_evolution_sim    import run_and_plot as schema_plot
    from admissibility_field_sim import run_and_plot as admiss_plot
    from cognitive_decoupling_sim import run_and_plot as cog_plot
    try:
        from valuation_decoupling_sim import run_and_plot as val_plot
        val_plot(os.path.join(out_dir, "valuation_decoupling_sim.png"))
    except Exception as e:
        print(f"  [TAF-MASTER] valuation individual figure skipped: {e}")

    print("[TAF-MASTER] Generating individual module figures...")
    schema_plot(os.path.join(out_dir, "schema_evolution_sim.png"))
    admiss_plot(os.path.join(out_dir, "admissibility_field_sim.png"))
    cog_plot(os.path.join(out_dir, "cognitive_decoupling_sim.png"))


# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="TAF Master Orchestrator — run all simulations"
    )
    parser.add_argument("--no-individual", action="store_true",
                        help="Skip individual module figures")
    parser.add_argument("--report-only", action="store_true",
                        help="Print report only, no figures")
    parser.add_argument("--output-dir", default=None,
                        help="Output directory (default: same as script)")
    args = parser.parse_args()

    out_dir = args.output_dir or SIM_DIR

    print("\n" + "=" * 72)
    print("  THERMODYNAMIC ACCOUNTABILITY FRAMEWORK — MASTER ORCHESTRATOR")
    print("=" * 72)

    results = run_all_simulations(verbose=True)

    if not args.report_only:
        composite_path = os.path.join(out_dir, "taf_composite.png")
        build_composite_figure(results, composite_path)

        if not args.no_individual:
            run_individual_figures(results, out_dir)

    print_full_report(results)


if __name__ == "__main__":
    main()
