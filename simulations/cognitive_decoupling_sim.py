"""
cognitive_decoupling_sim.py
===========================
Thermodynamic Accountability Framework — Cognitive Decoupling Simulation

Models the psychological dimension of the framework: the bifurcation of
human cognition into 𝒞-coupled (direct perception) and 𝒜(t)-mediated
(abstract/symbolic) modes, and the dynamics of the anchoring population.

Core structure from ToWorkOn.md:

  Biological baseline (bonobos/dolphins):
    Direct 𝒞-coupled interaction, no compression required.

  Human divergence:
    Integration now requires 𝒜(t) admissibility.
    Perception routed through Π_econ metrics, social media, LLM summaries.

  Cognitive modes:
    𝒞-coupled: embodied, relational, spatial, narrative
    𝒜(t)-mediated: abstract, symbolic, compressed, scored

  Anchoring population:
    Dyslexic, indigenous, neurodivergent, repair-based, oral cultures.
    Preserve direct 𝒞-coupling as cultural/neurological infrastructure.
    Only mode capable of detecting D(t) drift.

  Compression compatibility gradient:
    Schooling → credentialing → screen mediation → urban displacement
    → LLM normalization: five-stage shift from 𝒞-coupling to 𝒜(t) mediation.

Four simulation panels:
  1. Population Bifurcation: 𝒞-coupled vs. 𝒜(t)-mediated fractions
  2. Compression Compatibility Gradient: five-stage shift dynamics
  3. Anchoring Population Dynamics: size, D(t) detection capacity, erosion
  4. Perceptual Decoupling: fraction unable to detect D(t) drift

CC0. Requires: numpy, matplotlib, taf_primitives
"""

from __future__ import annotations

import random
from dataclasses import dataclass

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np

from taf_primitives import (
    CognitiveState,
    perceptual_decoupling, clamp, logistic_growth,
    D_CEILING,
)


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 1: COGNITIVE DECOUPLING MODEL
# ─────────────────────────────────────────────────────────────────────────────

# Five-stage compression compatibility shift (from ToWorkOn.md)
COMPRESSION_STAGES = [
    ("Schooling",          0.15),   # symbolic abstraction over embodied cognition
    ("Credentialing",      0.25),   # value by admissibility, not direct operability
    ("Screen mediation",   0.20),   # perception routed through interface
    ("Urban displacement", 0.20),   # relationships as transactions, not presence
    ("LLM normalization",  0.20),   # compressed outputs treated as knowledge
]


@dataclass
class CognitiveSimState:
    """Full cognitive simulation state."""
    t: int = 0
    frac_coupled:       float = 0.55   # start with majority still 𝒞-coupled
    frac_mediated:      float = 0.40
    frac_anchoring:     float = 0.05   # anchoring population (neurological/cultural)
    compression_compat: float = 0.40   # avg compression compatibility with 𝒜(t)
    D_perceptual:       float = 0.20   # fraction who cannot detect D(t)
    detection_capacity: float = 0.80   # anchoring pop's ability to detect D(t)
    # Stage completion fractions
    stage_completions: list = None

    def __post_init__(self):
        if self.stage_completions is None:
            self.stage_completions = [0.0] * len(COMPRESSION_STAGES)


def cognitive_decoupling_sim(
    t_max: int = 100,
    # Drift rates
    mediation_rate:     float = 0.008,  # rate of shift from coupled → mediated
    anchoring_erosion:  float = 0.002,  # rate of anchoring pop erosion
    compat_growth:      float = 0.006,  # compression compatibility growth
    schema_norm_rate:   float = 0.005,  # schema normalization (𝒜(t) as reality)
    # External D(t) (from legal/economic systems — drives perceptual decoupling)
    D_external_0:       float = 0.15,
    D_external_growth:  float = 0.007,
    rng_seed:           int   = 23,
) -> dict:
    """
    Simulate cognitive bifurcation and anchoring population dynamics.
    """
    rng = random.Random(rng_seed)
    state = CognitiveSimState()

    D_external = D_external_0
    schema_normalization = 0.10

    t_series              = []
    frac_coupled_series   = []
    frac_mediated_series  = []
    frac_anchoring_series = []
    compat_series         = []
    D_perceptual_series   = []
    detection_cap_series  = []
    D_external_series     = []
    schema_norm_series    = []

    # Stage completion series (one per stage)
    stage_series = [[] for _ in COMPRESSION_STAGES]

    # Anchoring detection signal: can the anchoring pop's signal
    # reach the broader system?
    detection_signal_series = []

    for i in range(t_max):
        t_series.append(i)
        frac_coupled_series.append(round(state.frac_coupled, 4))
        frac_mediated_series.append(round(state.frac_mediated, 4))
        frac_anchoring_series.append(round(state.frac_anchoring, 4))
        compat_series.append(round(state.compression_compat, 4))
        D_perceptual_series.append(round(state.D_perceptual, 4))
        detection_cap_series.append(round(state.detection_capacity, 4))
        D_external_series.append(round(D_external, 4))
        schema_norm_series.append(round(schema_normalization, 4))

        for j, stage_comp in enumerate(state.stage_completions):
            stage_series[j].append(round(stage_comp, 4))

        # Detection signal: anchoring pop size × detection capacity
        # Reduced by schema normalization (mediated pop can't hear it)
        det_signal = (state.frac_anchoring * state.detection_capacity *
                      (1.0 - schema_normalization))
        detection_signal_series.append(round(det_signal, 4))

        # ── Update compression stages ─────────────────────────────────────
        # Each stage progresses at a rate proportional to mediation_rate
        # and the fraction already mediated (social contagion)
        for j, (stage_name, stage_weight) in enumerate(COMPRESSION_STAGES):
            rate = mediation_rate * stage_weight * (1 + state.frac_mediated * 0.5)
            state.stage_completions[j] = clamp(
                state.stage_completions[j] + rate + rng.gauss(0, 0.002)
            )

        # ── Population shift: coupled → mediated ──────────────────────────
        # Rate driven by average stage completion and schema normalization
        avg_stage = sum(s * w for s, (_, w) in
                        zip(state.stage_completions, COMPRESSION_STAGES))
        shift = (mediation_rate * avg_stage * (1 + schema_normalization * 0.3) +
                 rng.gauss(0, 0.002))
        shift = min(shift, state.frac_coupled * 0.05)  # can't shift more than 5% at once

        state.frac_coupled  = clamp(state.frac_coupled  - shift, 0.01, 1.0)
        state.frac_mediated = clamp(state.frac_mediated + shift, 0.0,  1.0)

        # Normalize (anchoring is fixed neurologically/culturally, erodes slowly)
        total = state.frac_coupled + state.frac_mediated + state.frac_anchoring
        if total > 1.0:
            excess = total - 1.0
            state.frac_coupled  = clamp(state.frac_coupled  - excess * 0.5, 0.01, 1.0)
            state.frac_mediated = clamp(state.frac_mediated - excess * 0.5, 0.0,  1.0)

        # ── Anchoring population erosion ──────────────────────────────────
        # Slow erosion from institutional pressure, schooling mandates
        # Partially offset by repair/oral/indigenous community persistence
        erosion = anchoring_erosion * (1 + schema_normalization * 0.2) + rng.gauss(0, 0.001)
        state.frac_anchoring = clamp(state.frac_anchoring - erosion, 0.005, 0.20)

        # ── Compression compatibility growth ──────────────────────────────
        state.compression_compat = clamp(
            state.compression_compat + compat_growth + rng.gauss(0, 0.003)
        )

        # ── Schema normalization ──────────────────────────────────────────
        # 𝒜(t) outputs increasingly treated as reality
        schema_normalization = clamp(
            schema_normalization + schema_norm_rate + rng.gauss(0, 0.002)
        )

        # ── Perceptual decoupling ─────────────────────────────────────────
        state.D_perceptual = perceptual_decoupling(
            state.frac_mediated, D_external, schema_normalization
        )

        # ── Detection capacity of anchoring population ────────────────────
        # Erodes as they become institutionally marginalized
        state.detection_capacity = clamp(
            state.detection_capacity - 0.001 - schema_normalization * 0.002 +
            rng.gauss(0, 0.003),
            0.10, 1.0
        )

        # ── External D(t) grows ───────────────────────────────────────────
        D_external = clamp(D_external + D_external_growth + rng.gauss(0, 0.002),
                           0.0, D_CEILING)

        state.t = i + 1

    return {
        "t":                t_series,
        "frac_coupled":     frac_coupled_series,
        "frac_mediated":    frac_mediated_series,
        "frac_anchoring":   frac_anchoring_series,
        "compression_compat": compat_series,
        "D_perceptual":     D_perceptual_series,
        "detection_cap":    detection_cap_series,
        "D_external":       D_external_series,
        "schema_norm":      schema_norm_series,
        "detection_signal": detection_signal_series,
        "stages":           stage_series,
        "stage_names":      [s[0] for s in COMPRESSION_STAGES],
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

STAGE_COLORS = [ACCENT, ACCENT3, ACCENT5, ACCENT4, ACCENT2]


def style_ax(ax, title: str):
    ax.set_facecolor(BG)
    for spine in ax.spines.values():
        spine.set_edgecolor(GRID_C)
    ax.tick_params(colors=TEXT_C, labelsize=9)
    ax.xaxis.label.set_color(TEXT_C)
    ax.yaxis.label.set_color(TEXT_C)
    ax.set_title(title, color=TITLE_C, fontsize=10.5, fontweight="bold", pad=9)
    ax.grid(color=GRID_C, linestyle="--", linewidth=0.5, alpha=0.6)


def run_and_plot(output_path: str = "cognitive_decoupling_sim.png") -> dict:
    data = cognitive_decoupling_sim()
    t    = data["t"]

    fig = plt.figure(figsize=(18, 14))
    fig.patch.set_facecolor(FIG_BG)
    gs  = gridspec.GridSpec(2, 2, figure=fig, hspace=0.42, wspace=0.30)

    # ── Panel 1: Population Bifurcation ───────────────────────────────────────
    ax1 = fig.add_subplot(gs[0, 0])
    style_ax(ax1, "1. Population Bifurcation: 𝒞-Coupled vs. 𝒜(t)-Mediated")

    ax1.stackplot(t,
                  data["frac_anchoring"],
                  data["frac_coupled"],
                  data["frac_mediated"],
                  labels=["Anchoring population\n(dyslexic, indigenous, neurodivergent, repair)",
                          "𝒞-coupled (embodied, relational)",
                          "𝒜(t)-mediated (abstract, symbolic, scored)"],
                  colors=[ACCENT4, ACCENT3, ACCENT2],
                  alpha=0.75)

    ax1.set_xlabel("Time (generational cycles)")
    ax1.set_ylabel("Population Fraction  (0–1)")
    ax1.set_ylim(0, 1.0)
    ax1.legend(fontsize=7.5, facecolor=BG, edgecolor=GRID_C, labelcolor=TEXT_C,
               loc="center left")

    # ── Panel 2: Compression Compatibility Gradient ───────────────────────────
    ax2 = fig.add_subplot(gs[0, 1])
    style_ax(ax2, "2. Compression Compatibility Gradient: Five-Stage Shift")

    for j, (stage_name, _) in enumerate(COMPRESSION_STAGES):
        ax2.plot(t, data["stages"][j], color=STAGE_COLORS[j], lw=1.8,
                 label=f"Stage {j+1}: {stage_name}")

    ax2.plot(t, data["compression_compat"], color="white", lw=2.5, linestyle="--",
             label="Overall compression compatibility")

    ax2.set_xlabel("Time (generational cycles)")
    ax2.set_ylabel("Stage Completion  (0–1)")
    ax2.set_ylim(-0.02, 1.05)
    ax2.legend(fontsize=7.5, facecolor=BG, edgecolor=GRID_C, labelcolor=TEXT_C)

    # ── Panel 3: Anchoring Population Dynamics ────────────────────────────────
    ax3 = fig.add_subplot(gs[1, 0])
    style_ax(ax3, "3. Anchoring Population: Size, Detection Capacity, Signal Reach")

    ax3.plot(t, data["frac_anchoring"], color=ACCENT4, lw=2,
             label="Anchoring population fraction")
    ax3.plot(t, data["detection_cap"],  color=ACCENT3, lw=2,
             label="Detection capacity (ability to detect D(t))")
    ax3.plot(t, data["detection_signal"], color=ACCENT, lw=2,
             label="Detection signal reaching broader system")

    ax3.fill_between(t,
                     np.array(data["detection_cap"]),
                     np.array(data["detection_signal"]),
                     alpha=0.12, color=ACCENT2,
                     label="Signal lost to schema normalization")

    ax3.set_xlabel("Time (generational cycles)")
    ax3.set_ylabel("Normalized Value  (0–1)")
    ax3.set_ylim(-0.02, 1.05)
    ax3.legend(fontsize=7.5, facecolor=BG, edgecolor=GRID_C, labelcolor=TEXT_C)

    # ── Panel 4: Perceptual Decoupling ────────────────────────────────────────
    ax4 = fig.add_subplot(gs[1, 1])
    style_ax(ax4, "4. Perceptual Decoupling: Fraction Unable to Detect D(t) Drift")

    ax4.plot(t, data["D_perceptual"],  color=ACCENT2, lw=2.5,
             label="D_perceptual — cannot detect D(t)")
    ax4.plot(t, data["D_external"],    color=ACCENT5, lw=2,
             label="D_external — actual system decoupling")
    ax4.plot(t, data["schema_norm"],   color=ACCENT4, lw=1.5, linestyle="--",
             label="Schema normalization (𝒜(t) mistaken for reality)")
    ax4.plot(t, data["frac_mediated"], color=ACCENT,  lw=1.5, linestyle=":",
             label="Mediated fraction (input to D_perceptual)")

    ax4.fill_between(t,
                     np.array(data["D_perceptual"]),
                     np.array(data["D_external"]),
                     where=np.array(data["D_external"]) > np.array(data["D_perceptual"]),
                     alpha=0.10, color=ACCENT5,
                     label="Undetected D(t) gap")

    # Annotate the crossover where D_perceptual > D_external
    # (more people can't detect it than the actual decoupling warrants)
    cross = next((i for i, (dp, de) in enumerate(
        zip(data["D_perceptual"], data["D_external"])) if dp > de), None)
    if cross:
        ax4.axvline(cross, color=WARN_C, lw=1.2, linestyle="--", alpha=0.8)
        ax4.annotate(f"D_perceptual > D_external\nt = {cross}\n(system appears more\nstable than it is)",
                     xy=(cross, data["D_perceptual"][cross]),
                     xytext=(cross + 5, 0.35),
                     color=WARN_C, fontsize=8,
                     arrowprops=dict(arrowstyle="->", color=WARN_C, lw=1))

    ax4.set_xlabel("Time (generational cycles)")
    ax4.set_ylabel("Normalized Value  (0–1)")
    ax4.set_ylim(-0.02, 1.05)
    ax4.legend(fontsize=7.5, facecolor=BG, edgecolor=GRID_C, labelcolor=TEXT_C,
               loc="upper left")

    fig.suptitle(
        "Thermodynamic Accountability Framework — Cognitive Decoupling & Anchoring Population Dynamics",
        color=TITLE_C, fontsize=13, fontweight="bold", y=0.99
    )

    plt.savefig(output_path, dpi=150, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"[TAF-COG] Figure saved → {output_path}")
    return data


# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import os
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "cognitive_decoupling_sim.png")
    data = run_and_plot(out)

    print(f"\n  𝒞-coupled fraction:    {data['frac_coupled'][0]:.3f} → {data['frac_coupled'][-1]:.3f}")
    print(f"  𝒜(t)-mediated:         {data['frac_mediated'][0]:.3f} → {data['frac_mediated'][-1]:.3f}")
    print(f"  Anchoring population:  {data['frac_anchoring'][0]:.3f} → {data['frac_anchoring'][-1]:.3f}")
    print(f"  D_perceptual:          {data['D_perceptual'][0]:.3f} → {data['D_perceptual'][-1]:.3f}")
    print(f"  Detection signal:      {data['detection_signal'][0]:.3f} → {data['detection_signal'][-1]:.3f}")
    print(f"  Schema normalization:  {data['schema_norm'][0]:.3f} → {data['schema_norm'][-1]:.3f}")
