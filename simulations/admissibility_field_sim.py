"""
admissibility_field_sim.py
==========================
Thermodynamic Accountability Framework — Admissibility Field Simulation

Models 𝒜(t) as a dynamic filtering field over compression operators,
and D(t) as the distance between the physical causal field 𝒞 and
span(𝒜(t)) — the formal closure from ValuationToDo.md.

Core structure:

  Physical causal field 𝒞: high-dimensional, continuous, non-bounded
  Compression operators Πᵢ: {Π_legal, Π_econ, Π_schema, Π_embodied}
  Admissibility field 𝒜(t) = f(S, E, C, L)
  D(t) = distance(𝒞, span(𝒜(t))) = 1 - span_fraction

  The selector is not an agent. It is the equilibrium of the
  compression constraint field itself.

Four simulation panels:
  1. 𝒜(t) Components: S, E, C, L over time and their effect on span
  2. Compression Operator Survival: admissibility weights for each Πᵢ
  3. D(t) as span(𝒜(t)) narrows: fraction of 𝒞 becoming unrepresentable
  4. Operator Algebra: the three-layer formal structure over time

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
    AdmissibilityField,
    admissibility_span, clamp, logistic_growth,
    Q_FLOOR, D_CEILING,
)


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 1: ADMISSIBILITY FIELD MODEL
# ─────────────────────────────────────────────────────────────────────────────

def admissibility_field_sim(
    t_max: int = 100,
    # Initial 𝒜(t) components
    S_0: float = 0.30,   # structural alignment
    E_0: float = 0.72,   # enforcement feasibility
    C_0: float = 0.25,   # computational cost
    L_0: float = 0.28,   # legacy lock-in
    # Drift rates
    S_growth:   float = 0.008,   # S grows (capture accelerates)
    E_decay:    float = 0.006,   # E decays (enforcement erodes)
    C_growth:   float = 0.005,   # C grows (complexity increases)
    L_growth:   float = 0.004,   # L grows (lock-in accumulates)
    rng_seed:   int   = 31,
) -> dict:
    """
    Simulate the admissibility field 𝒜(t) and its compression operator
    weights over time.

    Returns time series for all 𝒜(t) components, span(𝒜(t)), D(t),
    and admissibility weights for each compression operator.
    """
    rng = random.Random(rng_seed)

    S = S_0
    E = E_0
    C = C_0
    L = L_0

    t_series       = []
    S_series       = []
    E_series       = []
    C_series       = []
    L_series       = []
    span_series    = []
    D_t_series     = []

    # Compression operator admissibility weights
    w_legal_series    = []
    w_econ_series     = []
    w_schema_series   = []
    w_embodied_series = []

    # Span components: how much of 𝒞 is reachable by each operator
    reach_legal_series    = []
    reach_econ_series     = []
    reach_schema_series   = []
    reach_embodied_series = []

    # Formal three-layer tracking
    # Layer 1: Physical 𝒞 (always 1.0 — reference)
    # Layer 2: Compression coverage (weighted sum of operator reaches)
    # Layer 3: Admissible model class (span(𝒜(t)))
    layer2_series = []
    layer3_series = []

    for i in range(t_max):
        t_series.append(i)
        S_series.append(round(S, 4))
        E_series.append(round(E, 4))
        C_series.append(round(C, 4))
        L_series.append(round(L, 4))

        # ── Compute span(𝒜(t)) ────────────────────────────────────────────
        span = admissibility_span(S, E, C, L)
        span_series.append(round(span, 4))
        D_t = max(0.0, min(D_CEILING, 1.0 - span))
        D_t_series.append(round(D_t, 4))

        # ── Admissibility weights for each Πᵢ ─────────────────────────────
        # Π_legal: gated by enforcement feasibility, reduced by S capture
        w_legal = clamp(E * (1 - S * 0.55) + rng.gauss(0, 0.01))
        # Π_econ: gated by cost, reduced by S (but S also benefits econ operators)
        w_econ  = clamp((1 - C) * (1 - S * 0.25) + rng.gauss(0, 0.01))
        # Π_schema: grows with S and L (schema operators are S-aligned)
        w_schema = clamp(L * S + rng.gauss(0, 0.01))
        # Π_embodied: shrinks with L and S (embodied knowledge is schema-incompatible)
        w_embodied = clamp((1 - L) * (1 - S) * 0.8 + rng.gauss(0, 0.01))

        w_legal_series.append(round(w_legal, 4))
        w_econ_series.append(round(w_econ, 4))
        w_schema_series.append(round(w_schema, 4))
        w_embodied_series.append(round(w_embodied, 4))

        # ── Fraction of 𝒞 reachable by each operator ─────────────────────
        # Reach = admissibility weight × operator coverage fraction
        # (operators have different inherent coverage of 𝒞)
        reach_legal    = w_legal    * 0.35   # legal covers ~35% of 𝒞 at best
        reach_econ     = w_econ     * 0.30   # econ covers ~30%
        reach_schema   = w_schema   * 0.20   # schema covers ~20% (narrow but stable)
        reach_embodied = w_embodied * 0.60   # embodied covers ~60% (broadest, least admissible)

        reach_legal_series.append(round(reach_legal, 4))
        reach_econ_series.append(round(reach_econ, 4))
        reach_schema_series.append(round(reach_schema, 4))
        reach_embodied_series.append(round(reach_embodied, 4))

        # ── Three-layer formal structure ───────────────────────────────────
        # Layer 2: compression coverage (union of operator reaches, capped at 1)
        layer2 = clamp(reach_legal + reach_econ + reach_schema + reach_embodied, 0, 1)
        layer2_series.append(round(layer2, 4))
        # Layer 3: admissible model class = span(𝒜(t))
        layer3_series.append(round(span, 4))

        # ── Update 𝒜(t) components ────────────────────────────────────────
        S = clamp(S + S_growth + rng.gauss(0, 0.003), 0.0, 0.98)
        E = clamp(E - E_decay  + rng.gauss(0, 0.004), 0.02, 1.0)
        C = clamp(C + C_growth + rng.gauss(0, 0.003), 0.0, 0.98)
        L = clamp(L + L_growth + rng.gauss(0, 0.002), 0.0, 0.98)

    return {
        "t":              t_series,
        "S":              S_series,
        "E":              E_series,
        "C":              C_series,
        "L":              L_series,
        "span":           span_series,
        "D_t":            D_t_series,
        "w_legal":        w_legal_series,
        "w_econ":         w_econ_series,
        "w_schema":       w_schema_series,
        "w_embodied":     w_embodied_series,
        "reach_legal":    reach_legal_series,
        "reach_econ":     reach_econ_series,
        "reach_schema":   reach_schema_series,
        "reach_embodied": reach_embodied_series,
        "layer2":         layer2_series,
        "layer3":         layer3_series,
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


def run_and_plot(output_path: str = "admissibility_field_sim.png") -> dict:
    data = admissibility_field_sim()
    t    = data["t"]

    fig = plt.figure(figsize=(18, 14))
    fig.patch.set_facecolor(FIG_BG)
    gs  = gridspec.GridSpec(2, 2, figure=fig, hspace=0.42, wspace=0.30)

    # ── Panel 1: 𝒜(t) Components ─────────────────────────────────────────────
    ax1 = fig.add_subplot(gs[0, 0])
    style_ax(ax1, "1. 𝒜(t) Components: S, E, C, L and span(𝒜(t))")

    ax1.plot(t, data["S"],    color=ACCENT2, lw=2, label="S — structural alignment (↑ bad)")
    ax1.plot(t, data["E"],    color=ACCENT3, lw=2, label="E — enforcement feasibility (↓ bad)")
    ax1.plot(t, data["C"],    color=ACCENT5, lw=2, label="C — computational cost (↑ bad)")
    ax1.plot(t, data["L"],    color=ACCENT4, lw=2, label="L — legacy lock-in (↑ bad)")
    ax1.plot(t, data["span"], color=ACCENT,  lw=2.5, linestyle="--",
             label="span(𝒜(t)) — fraction of 𝒞 representable")

    ax1.fill_between(t, np.array(data["span"]), 1.0,
                     alpha=0.10, color=ACCENT2,
                     label="Non-representable region of 𝒞")

    ax1.set_xlabel("Time (cycles)")
    ax1.set_ylabel("Normalized Value  (0–1)")
    ax1.set_ylim(-0.02, 1.05)
    ax1.legend(fontsize=7.5, facecolor=BG, edgecolor=GRID_C, labelcolor=TEXT_C)

    # ── Panel 2: Compression Operator Survival ────────────────────────────────
    ax2 = fig.add_subplot(gs[0, 1])
    style_ax(ax2, "2. Compression Operator Survival: Admissibility Weights for Πᵢ")

    ax2.plot(t, data["w_legal"],    color=ACCENT,  lw=2,
             label="Π_legal — legal causal narratives")
    ax2.plot(t, data["w_econ"],     color=ACCENT3, lw=2,
             label="Π_econ — value compressions")
    ax2.plot(t, data["w_schema"],   color=ACCENT2, lw=2,
             label="Π_schema — AI/institutional grammars")
    ax2.plot(t, data["w_embodied"], color=ACCENT4, lw=2,
             label="Π_embodied — direct 𝒞-coupled knowledge")

    # Annotate the inversion point where Π_schema > Π_embodied
    inv = next((i for i, (s, e) in enumerate(
        zip(data["w_schema"], data["w_embodied"])) if s > e), None)
    if inv:
        ax2.axvline(inv, color=WARN_C, lw=1.2, linestyle="--", alpha=0.8)
        ax2.annotate(f"Π_schema > Π_embodied\nt = {inv}",
                     xy=(inv, data["w_schema"][inv]),
                     xytext=(inv + 5, 0.55),
                     color=WARN_C, fontsize=8,
                     arrowprops=dict(arrowstyle="->", color=WARN_C, lw=1))

    ax2.set_xlabel("Time (cycles)")
    ax2.set_ylabel("Admissibility Weight  (0–1)")
    ax2.set_ylim(-0.02, 1.05)
    ax2.legend(fontsize=7.5, facecolor=BG, edgecolor=GRID_C, labelcolor=TEXT_C)

    # ── Panel 3: D(t) as span(𝒜(t)) narrows ──────────────────────────────────
    ax3 = fig.add_subplot(gs[1, 0])
    style_ax(ax3, "3. D(t) = distance(𝒞, span(𝒜(t))): Fraction of Reality Becoming Unrepresentable")

    ax3.fill_between(t, np.array(data["D_t"]), 0,
                     alpha=0.20, color=ACCENT2, label="D(t) — unrepresentable region")
    ax3.fill_between(t, 1.0, np.array(data["D_t"]),
                     alpha=0.10, color=ACCENT3, label="span(𝒜(t)) — representable region")
    ax3.plot(t, data["D_t"],   color=ACCENT2, lw=2.5, label="D(t)")
    ax3.plot(t, data["span"],  color=ACCENT3, lw=2,   label="span(𝒜(t))")
    ax3.plot(t, data["reach_embodied"], color=ACCENT4, lw=1.5, linestyle="--",
             label="Embodied reach (excluded from span)")

    ax3.set_xlabel("Time (cycles)")
    ax3.set_ylabel("Fraction of 𝒞  (0–1)")
    ax3.set_ylim(-0.02, 1.05)
    ax3.legend(fontsize=7.5, facecolor=BG, edgecolor=GRID_C, labelcolor=TEXT_C)

    # ── Panel 4: Three-Layer Formal Structure ─────────────────────────────────
    ax4 = fig.add_subplot(gs[1, 1])
    style_ax(ax4, "4. Three-Layer Operator Algebra: 𝒞 → Πᵢ → 𝒜(t)")

    # Layer 1: Physical 𝒞 (always 1.0)
    ax4.axhline(1.0, color=ACCENT3, lw=2.5, linestyle="-",
                label="Layer 1: Physical 𝒞 (always 1.0)")
    # Layer 2: Compression coverage (union of operator reaches)
    ax4.plot(t, data["layer2"], color=ACCENT5, lw=2,
             label="Layer 2: Compression coverage (∪ Πᵢ reaches)")
    # Layer 3: Admissible model class = span(𝒜(t))
    ax4.plot(t, data["layer3"], color=ACCENT,  lw=2,
             label="Layer 3: Admissible model class = span(𝒜(t))")

    # Shade the two loss regions
    ax4.fill_between(t, 1.0, np.array(data["layer2"]),
                     alpha=0.10, color=ACCENT5,
                     label="Compression loss (𝒞 → Πᵢ)")
    ax4.fill_between(t, np.array(data["layer2"]), np.array(data["layer3"]),
                     alpha=0.12, color=ACCENT2,
                     label="Admissibility loss (Πᵢ → 𝒜(t))")

    ax4.annotate("Compression loss\n(𝒞 → Πᵢ)",
                 xy=(60, (1.0 + data["layer2"][60]) / 2),
                 color=ACCENT5, fontsize=8)
    ax4.annotate("Admissibility loss\n(Πᵢ → 𝒜(t))",
                 xy=(70, (data["layer2"][70] + data["layer3"][70]) / 2),
                 color=ACCENT2, fontsize=8)

    ax4.set_xlabel("Time (cycles)")
    ax4.set_ylabel("Fraction of 𝒞  (0–1)")
    ax4.set_ylim(-0.02, 1.10)
    ax4.legend(fontsize=7.5, facecolor=BG, edgecolor=GRID_C, labelcolor=TEXT_C,
               loc="lower left")

    fig.suptitle(
        "Thermodynamic Accountability Framework — Admissibility Field 𝒜(t) & D(t) Operator",
        color=TITLE_C, fontsize=13, fontweight="bold", y=0.99
    )

    plt.savefig(output_path, dpi=150, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"[TAF-ADMISS] Figure saved → {output_path}")
    return data


# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import os
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "admissibility_field_sim.png")
    data = run_and_plot(out)

    print(f"\n  span(𝒜(t)):   {data['span'][0]:.3f} → {data['span'][-1]:.3f}")
    print(f"  D(t):          {data['D_t'][0]:.3f} → {data['D_t'][-1]:.3f}")
    print(f"  w_legal:       {data['w_legal'][0]:.3f} → {data['w_legal'][-1]:.3f}")
    print(f"  w_schema:      {data['w_schema'][0]:.3f} → {data['w_schema'][-1]:.3f}")
    print(f"  w_embodied:    {data['w_embodied'][0]:.3f} → {data['w_embodied'][-1]:.3f}")
    print(f"  Layer 2 (compression coverage): {data['layer2'][0]:.3f} → {data['layer2'][-1]:.3f}")
    print(f"  Layer 3 (admissible class):     {data['layer3'][0]:.3f} → {data['layer3'][-1]:.3f}")
