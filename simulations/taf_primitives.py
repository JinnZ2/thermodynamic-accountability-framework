"""
taf_primitives.py
=================
Thermodynamic Accountability Framework — Shared Primitives

Canonical equations, dataclasses, and helper functions shared across
all TAF simulation modules. Import this; do not duplicate.

Canonical equation references (ToWorkOn.md / ValuationToDo.md):

  Q_eff  = D(t) × Q_raw / A(t, schema)
  ΔSchema(t) = f( D(t)·{litigation, admin}, S, infrastructure )
  D(t)   = distance between 𝒞 and span(𝒜(t))
  𝒜(t)  = f(S, E, C, L)
  Instability: F / Q > R × Eₐ

CC0. Requires: stdlib only (dataclasses, typing, math).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional


# ─────────────────────────────────────────────────────────────────────────────
# VERSION
# ─────────────────────────────────────────────────────────────────────────────

PRIMITIVES_VERSION = "1.0.0"


# ─────────────────────────────────────────────────────────────────────────────
# CANONICAL CONSTANTS (default calibration values)
# ─────────────────────────────────────────────────────────────────────────────

# Instability threshold baseline: R × Eₐ
DEFAULT_R_EA: float = 8.4

# Minimum Q before enforcement collapses entirely
Q_FLOOR: float = 0.001

# Maximum D(t) (full decoupling)
D_CEILING: float = 0.98

# Pre-emptive exclusion threshold: fraction of Q_phys that becomes
# schema-incompatible before the system crosses from post-hoc to
# pre-emptive schema regime
PREEMPTIVE_THRESHOLD: float = 0.55


# ─────────────────────────────────────────────────────────────────────────────
# CORE DATACLASSES
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class QState:
    """
    Partitioned causal compressibility state.

    Q_phys : Physical causality — exists in the world regardless of schema
    Q_leg  : Legally representable causality — exists in schema space
    D      : Decoupling operator — controls covariance between Q_phys and Q_leg
             D → 0: high coupling (legal tracks reality)
             D → 1: full decoupling (legal evolves independently)
    """
    Q_phys: float = 0.80
    Q_leg:  float = 0.75
    D:      float = 0.10

    @property
    def gap(self) -> float:
        """Physical causality not representable in schema."""
        return max(0.0, self.Q_phys - self.Q_leg)

    @property
    def Q_eff(self) -> float:
        """
        Effective Q available for enforcement.
        Q_eff = D_coupling × Q_leg  (D_coupling = 1 - D)
        """
        return max(Q_FLOOR, (1.0 - self.D) * self.Q_leg)

    @property
    def preemptive_regime(self) -> bool:
        """True when schema has crossed from post-hoc to pre-emptive."""
        return self.gap > PREEMPTIVE_THRESHOLD * self.Q_phys


@dataclass
class SchemaState:
    """
    State of the representational schema at time t.

    width          : Breadth of representable causal forms (0–1)
    S_alignment    : Structural power alignment (corporate/state capture)
    A_t            : Administrative processing time (shaped by S)
    litigation_P   : Litigation pressure (expansion force from below)
    admin_feedback : Administrative optimization pressure (compression)
    infra_lock     : Infrastructure lock-in (path dependence, 0–1)
    preemptive     : Whether schema is now pre-emptive (not post-hoc)
    """
    width:          float = 0.80
    S_alignment:    float = 0.35
    A_t:            float = 1.0
    litigation_P:   float = 0.20
    admin_feedback: float = 0.15
    infra_lock:     float = 0.30
    preemptive:     bool  = False


@dataclass
class AdmissibilityField:
    """
    𝒜(t) — the dynamic filtering field over compression operators.

    S : Structural power alignment
    E : Enforcement feasibility
    C : Computational cost of maintaining representation
    L : Legacy institutional encoding (path dependence)

    span_fraction : Fraction of 𝒞 (physical causal field) that is
                    currently representable under 𝒜(t)
    """
    S: float = 0.35   # structural alignment (0=neutral, 1=fully captured)
    E: float = 0.70   # enforcement feasibility
    C: float = 0.30   # computational cost (higher = more compression)
    L: float = 0.40   # legacy lock-in
    span_fraction: float = 0.75  # fraction of 𝒞 reachable by span(𝒜(t))

    @property
    def D_t(self) -> float:
        """
        D(t) = distance between 𝒞 and span(𝒜(t)).
        Approximated as 1 - span_fraction.
        """
        return max(0.0, min(D_CEILING, 1.0 - self.span_fraction))

    def admissibility_weight(self, compression_type: str) -> float:
        """
        Return the admissibility weight for a given compression operator type.
        Higher weight = more likely to survive 𝒜(t) filtering.

        compression_type: 'legal', 'economic', 'schema', 'embodied'
        """
        weights = {
            "legal":    max(0.0, self.E * (1 - self.S * 0.5)),
            "economic": max(0.0, (1 - self.C) * (1 - self.S * 0.3)),
            "schema":   max(0.0, self.L * self.S),
            "embodied": max(0.0, (1 - self.L) * (1 - self.S)),
        }
        return weights.get(compression_type, 0.0)


@dataclass
class CognitiveState:
    """
    Population-level cognitive coupling state.

    frac_coupled    : Fraction of population in direct 𝒞-coupled mode
    frac_mediated   : Fraction in 𝒜(t)-mediated mode
    frac_anchoring  : Fraction serving as reality anchors
                      (dyslexic, indigenous, neurodivergent, repair-based)
    compression_compat : Average compression compatibility with 𝒜(t)
                         (higher = more schema-aligned)
    D_perceptual    : Perceptual decoupling — fraction who cannot detect D(t)
    """
    frac_coupled:       float = 0.40
    frac_mediated:      float = 0.55
    frac_anchoring:     float = 0.05
    compression_compat: float = 0.55
    D_perceptual:       float = 0.35


# ─────────────────────────────────────────────────────────────────────────────
# CANONICAL EQUATIONS
# ─────────────────────────────────────────────────────────────────────────────

def Q_effective(Q_raw: float, D: float, A_t: float, schema_cost: float = 1.0) -> float:
    """
    Q_eff = D_coupling × Q_raw / A(t, schema)

    D_coupling = 1 - D  (higher D → less coupling → lower Q_eff)
    A_t        = administrative processing time (shaped by S)
    schema_cost = additional schema-admissibility cost multiplier
    """
    D_coupling = max(0.0, 1.0 - D)
    return max(Q_FLOOR, D_coupling * Q_raw / max(0.01, A_t * schema_cost))


def instability_signal(F: float, Q: float, R_Ea: float = DEFAULT_R_EA) -> float:
    """
    Enforcement instability signal: F / Q - R × Eₐ.
    Positive → above instability threshold.
    """
    return (F / max(Q_FLOOR, Q)) - R_Ea


def delta_schema(
    D: float,
    litigation_P: float,
    admin_feedback: float,
    S: float,
    infra_constraint: float,
) -> float:
    """
    ΔSchema(t) = f( D(t)·{litigation, admin}, S, infrastructure )

    Returns signed change in schema width:
      + expansion (litigation wins, novel causal forms admitted)
      - contraction (admin compression, S capture, infra lock)

    D gates the reality input: higher D → less litigation signal reaches schema.
    S biases toward contraction.
    infra_constraint caps possible schema forms.
    """
    # Reality-gated expansion pressure (litigation filtered by D)
    expansion = (1.0 - D) * litigation_P * 0.04

    # Contraction pressure from admin optimization + S capture + infra
    contraction = (
        admin_feedback * 0.025 +
        S * 0.030 +
        infra_constraint * 0.015
    )

    return expansion - contraction


def admissibility_span(S: float, E: float, C: float, L: float) -> float:
    """
    Approximate span(𝒜(t)) as a fraction of 𝒞.

    Higher S → narrower span (captured schema)
    Higher E → wider span (more enforcement feasibility)
    Higher C → narrower span (cost excludes complex representations)
    Higher L → narrower span (legacy lock-in freezes schema)
    """
    base = E * (1.0 - S * 0.6) * (1.0 - C * 0.4) * (1.0 - L * 0.3)
    return max(0.02, min(0.98, base))


def perceptual_decoupling(
    frac_mediated: float,
    D_t: float,
    schema_normalization: float,
) -> float:
    """
    D_perceptual: fraction of population that cannot detect D(t).

    Grows with mediated fraction, D(t), and schema normalization
    (the degree to which 𝒜(t) outputs are treated as reality).
    """
    return min(0.98, frac_mediated * D_t * (1.0 + schema_normalization * 0.5))


# ─────────────────────────────────────────────────────────────────────────────
# UTILITY HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, value))


def logistic_growth(x: float, k: float = 10.0, x0: float = 0.5) -> float:
    """Standard logistic function for threshold-crossing dynamics."""
    return 1.0 / (1.0 + math.exp(-k * (x - x0)))


def sigmoid_decay(t: int, half_life: int, initial: float = 1.0) -> float:
    """Exponential decay with half-life in time steps."""
    return initial * math.exp(-math.log(2) * t / max(1, half_life))
