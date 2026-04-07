#!/usr/bin/env python3
"""
HAAS-Q Field Link — Bidirectional bridge between TAF and HAAS-Q.

TAF (this repo) models the energy physics of organisms under institutional load.
HAAS-Q (github.com/JinnZ2/HAAS) models the control environment where humans,
automated machinery, and AI systems operate together.

This module creates the formal coupling:

    TAF → HAAS-Q:  fatigue, collapse distance, parasitic debt → risk amplification
    HAAS-Q → TAF:  spatial risk, alerts, control overrides → cognitive/metabolic load

The shared field is ENERGY. Both systems measure in compatible units.
TAF asks: "Is the organism's energy budget sustainable?"
HAAS-Q asks: "Is the control environment safe?"
The fieldlink couples them: an unsafe environment drains the organism,
and a drained organism makes the environment less safe.

Reference: HAAS-Q energy.py already ports TAF equations into HAAS-Q's
simulation loop via HumanEnergyState. This module provides the reverse
path plus the coupled feedback loop.
"""

import math
from datetime import datetime


# ============================================================
# HAAS-Q → TAF: Control environment signals as energy load
# ============================================================

def risk_field_cognitive_load(risk_score, confidence, latency_ms=0):
    """Convert HAAS-Q risk field state into TAF cognitive load units.

    HAAS-Q risk = f(energy * uncertainty * latency * proximity).
    High risk + low confidence = high vigilance demand = cognitive energy drain.

    Parameters
    ----------
    risk_score : float
        HAAS-Q computed risk (0-1 scale).
    confidence : float
        AI controller confidence after sensor noise (0-1 scale).
    latency_ms : float
        Control loop latency in milliseconds. Adds uncertainty.

    Returns
    -------
    float
        Cognitive load contribution (energy units, additive to TAF cognitive_load).
    """
    # Vigilance cost: inversely proportional to confidence
    confidence_safe = max(confidence, 0.01)
    vigilance = risk_score / confidence_safe

    # Latency uncertainty adds monitoring burden
    latency_factor = 1 + latency_ms / 1000.0

    # Scale to TAF energy units (0-50 range, matching physical/cognitive load scale)
    load = vigilance * latency_factor * 25.0
    return round(min(load, 50.0), 1)


def alert_metabolic_cost(alerts, metabolic_spike=2.0, attention_cost=1.5):
    """Convert HAAS-Q alert signals into TAF metabolic load.

    Each alert type has a different energy signature:
    - CRITICAL: full cortisol spike + attention capture
    - LOW_CONFIDENCE: sustained anxiety (moderate but persistent)
    - HUMAN_AI_MISMATCH: cognitive dissonance (high cognitive cost)
    - DRIFT_RECALIBRATION: reorientation cost

    Parameters
    ----------
    alerts : list of str
        Active HAAS-Q alert strings from check_alerts().
    metabolic_spike : float
        Base metabolic cost per critical alert.
    attention_cost : float
        Base attention/cognitive cost per alert.

    Returns
    -------
    dict
        Breakdown of metabolic, cognitive, and trust costs.
    """
    weights = {
        "CRITICAL": {"metabolic": 1.0, "cognitive": 1.0, "trust": 0.0},
        "LOW_CONFIDENCE": {"metabolic": 0.3, "cognitive": 0.8, "trust": 0.15},
        "HUMAN_AI_MISMATCH": {"metabolic": 0.5, "cognitive": 1.2, "trust": 0.25},
        "DRIFT_RECALIBRATION": {"metabolic": 0.2, "cognitive": 0.6, "trust": 0.1},
    }

    total_metabolic = 0.0
    total_cognitive = 0.0
    total_trust_erosion = 0.0

    for alert in alerts:
        w = weights.get(alert, {"metabolic": 0.4, "cognitive": 0.5, "trust": 0.05})
        total_metabolic += metabolic_spike * w["metabolic"]
        total_cognitive += attention_cost * w["cognitive"]
        total_trust_erosion += w["trust"]

    return {
        "metabolic_load": round(total_metabolic, 2),
        "cognitive_load": round(total_cognitive, 2),
        "trust_erosion": round(min(total_trust_erosion, 1.0), 3),
        "total_energy_cost": round(total_metabolic + total_cognitive, 2),
    }


def control_override_load(override_count, threshold=3):
    """Cognitive cost of human-AI control disagreements.

    When a human overrides AI decisions (or vice versa), each override
    creates cognitive friction — the operator must maintain two mental
    models simultaneously. Cost is nonlinear (same pattern as hidden
    variable multiplier).

    Parameters
    ----------
    override_count : int
        Number of control overrides in the current window.
    threshold : int
        Normal override count below which cost is minimal.

    Returns
    -------
    float
        Cognitive load addition (energy units).
    """
    excess = max(0, override_count - threshold)
    if excess == 0:
        return 0.0
    # Same nonlinear pattern as TAF hidden variable multiplier
    return round(0.1 * excess ** 1.5 * 10, 1)


# ============================================================
# TAF → HAAS-Q: Energy state as risk amplifier
# ============================================================

def fatigue_risk_amplifier(fatigue_score):
    """Convert TAF fatigue score to HAAS-Q risk multiplier.

    HAAS-Q risk.py applies fatigue as: risk * (1 + fatigue_score * 0.05).
    This function provides the TAF-side computation of that multiplier
    with additional nonlinearity at high fatigue.

    Parameters
    ----------
    fatigue_score : float
        TAF fatigue score (0-10 scale).

    Returns
    -------
    float
        Risk amplification multiplier (>= 1.0).
    """
    # Linear region (fatigue 0-7): matches HAAS-Q's 0.05 coefficient
    # Nonlinear region (fatigue 7-10): accelerating degradation
    if fatigue_score <= 7.0:
        return round(1.0 + fatigue_score * 0.05, 3)
    # Exponential tail above 7
    linear_part = 7.0 * 0.05
    excess = fatigue_score - 7.0
    nonlinear_part = 0.05 * excess + 0.02 * excess ** 2
    return round(1.0 + linear_part + nonlinear_part, 3)


def collapse_distance_to_zone(collapse_distance):
    """Map TAF collapse distance to HAAS-Q zone level.

    HAAS-Q uses GREEN/YELLOW/RED zones for spatial risk.
    TAF collapse distance (0-1) maps naturally:
    - GREEN:  collapse_distance > 0.6 (sustainable)
    - YELLOW: 0.2 < collapse_distance <= 0.6 (degrading)
    - RED:    collapse_distance <= 0.2 (unsafe)

    Parameters
    ----------
    collapse_distance : float
        TAF distance-to-collapse (0-1 scale).

    Returns
    -------
    str
        HAAS-Q zone level string.
    """
    if collapse_distance > 0.6:
        return "GREEN"
    elif collapse_distance > 0.2:
        return "YELLOW"
    else:
        return "RED"


def energy_debt_to_drift(cumulative_debt, debt_threshold=5.0):
    """Convert TAF parasitic energy debt into HAAS-Q drift index.

    Accumulated institutional friction (unpaid work, systemic failures)
    erodes operator calibration over time. This manifests as drift in
    HAAS-Q's sensor/control model.

    Parameters
    ----------
    cumulative_debt : float
        TAF parasitic energy debt (from data_logger).
    debt_threshold : float
        Debt level at which drift reaches maximum.

    Returns
    -------
    float
        HAAS-Q drift index (0-1 scale).
    """
    if cumulative_debt <= 0:
        return 0.0
    drift = 1.0 - math.exp(-0.5 * cumulative_debt / debt_threshold)
    return round(min(drift, 1.0), 3)


# ============================================================
# COUPLED FEEDBACK LOOP
# ============================================================

class FieldLink:
    """Bidirectional TAF ↔ HAAS-Q coupling.

    Maintains the shared energy field between both systems.
    Each step:
    1. HAAS-Q spatial risk/alerts → TAF load adjustments
    2. TAF fatigue/collapse → HAAS-Q risk amplification
    3. Accumulated friction → drift feedback

    This is the formal coupling that makes both frameworks
    thermodynamically consistent: you cannot have a "safe"
    environment with a collapsing operator, and you cannot
    have a healthy operator in an unsafe environment.
    """

    def __init__(self, energy_input=100.0):
        # TAF state
        self.energy_input = energy_input
        self.base_physical_load = 30.0
        self.base_cognitive_load = 40.0
        self.cumulative_debt = 0.0
        self.cumulative_ai_tax = 0.0
        self.step_count = 0

        # Current computed state
        self.fatigue_score = 0.0
        self.total_load = 0.0
        self.collapse_distance = 1.0
        self.risk_amplifier = 1.0
        self.zone_level = "GREEN"
        self.drift_index = 0.0
        self.history = []

    def step(self, haas_risk=0.0, haas_confidence=1.0, haas_alerts=None,
             override_count=0, friction_events=0, hidden_count=0,
             automation_count=1, automation_reliability=0.9,
             temp_celsius=20.0, wind_mps=0.0, latency_ms=0):
        """Execute one coupled TAF ↔ HAAS-Q step.

        Parameters
        ----------
        haas_risk : float
            HAAS-Q computed risk score (0-1).
        haas_confidence : float
            HAAS-Q AI confidence (0-1).
        haas_alerts : list of str or None
            Active HAAS-Q alerts.
        override_count : int
            Human-AI control overrides this step.
        friction_events : int
            Institutional friction events this step.
        hidden_count : int
            Hidden variable count for TAF multiplier.
        automation_count : int
            Number of automation systems.
        automation_reliability : float
            Automation reliability (0-1).
        temp_celsius : float
            Ambient temperature.
        wind_mps : float
            Wind speed.
        latency_ms : float
            Control loop latency.

        Returns
        -------
        dict
            Full coupled state for this step.
        """
        if haas_alerts is None:
            haas_alerts = []

        self.step_count += 1

        # --- HAAS-Q → TAF: environment signals become load ---
        env_cognitive = risk_field_cognitive_load(haas_risk, haas_confidence, latency_ms)
        alert_cost = alert_metabolic_cost(haas_alerts)
        override_load = control_override_load(override_count)

        self.cumulative_ai_tax += alert_cost["total_energy_cost"]

        # Parasitic debt from friction
        if friction_events > 0:
            debt = friction_events * 0.15
            self.cumulative_debt += debt

        # Effective loads (base + environment-induced)
        effective_cognitive = (
            self.base_cognitive_load
            + env_cognitive
            + alert_cost["cognitive_load"]
            + override_load
            + self.cumulative_ai_tax * 0.1  # accumulated tax bleeds in
        )
        effective_physical = self.base_physical_load

        # --- TAF core computation ---
        # Hidden variable multiplier
        hv_mult = 1.0
        if hidden_count > 0:
            hv_mult = 1 + 0.1 * hidden_count ** 1.5

        # Automation load multiplier
        auto_mult = 1 + automation_count * (1 - automation_reliability) * 0.5

        # Environment multiplier
        temp_stress = max(0.0, (15 - temp_celsius) * 0.05)
        wind_stress = wind_mps * 0.02
        env_mult = 1 + temp_stress + wind_stress

        base_load = effective_physical + effective_cognitive
        self.total_load = base_load * hv_mult * auto_mult * env_mult

        deficit = self.total_load - self.energy_input
        self.fatigue_score = round(max(0.0, min(10.0, deficit / self.energy_input * 10)), 1)

        # Collapse distance
        health_limit = 1.6 * self.energy_input
        self.collapse_distance = round(
            max(0.0, min(1.0, (health_limit - self.total_load) / health_limit)), 3
        )

        # --- TAF → HAAS-Q: energy state becomes risk signal ---
        self.risk_amplifier = fatigue_risk_amplifier(self.fatigue_score)
        self.zone_level = collapse_distance_to_zone(self.collapse_distance)
        self.drift_index = energy_debt_to_drift(self.cumulative_debt)

        # Collapse flags
        flags = []
        if self.total_load >= 1.6 * self.energy_input:
            flags.append("HEALTH_COLLAPSE_IMMINENT")
        elif self.total_load >= 1.4 * self.energy_input:
            flags.append("SAFETY_BREAKDOWN_LIKELY")
        elif self.total_load >= 1.2 * self.energy_input:
            flags.append("PRODUCTIVITY_DEGRADATION")

        snapshot = {
            "step": self.step_count,
            "fatigue_score": self.fatigue_score,
            "total_load": round(self.total_load, 1),
            "collapse_distance": self.collapse_distance,
            "risk_amplifier": self.risk_amplifier,
            "zone_level": self.zone_level,
            "drift_index": self.drift_index,
            "cumulative_ai_tax": round(self.cumulative_ai_tax, 2),
            "cumulative_debt": round(self.cumulative_debt, 2),
            "flags": flags,
            "multipliers": {
                "hidden_variables": round(hv_mult, 2),
                "automation": round(auto_mult, 2),
                "environment": round(env_mult, 2),
            },
            "haas_inputs": {
                "risk": haas_risk,
                "confidence": haas_confidence,
                "alerts": haas_alerts,
                "overrides": override_count,
            },
        }
        self.history.append(snapshot)
        return snapshot

    def summary(self):
        """Return a summary of the coupled simulation."""
        if not self.history:
            return {"steps": 0, "status": "no data"}

        fatigue_values = [h["fatigue_score"] for h in self.history]
        collapse_values = [h["collapse_distance"] for h in self.history]

        return {
            "steps": self.step_count,
            "final_fatigue": self.fatigue_score,
            "peak_fatigue": max(fatigue_values),
            "mean_fatigue": round(sum(fatigue_values) / len(fatigue_values), 1),
            "final_collapse_distance": self.collapse_distance,
            "min_collapse_distance": min(collapse_values),
            "final_zone": self.zone_level,
            "cumulative_ai_tax": round(self.cumulative_ai_tax, 2),
            "cumulative_debt": round(self.cumulative_debt, 2),
            "drift_index": self.drift_index,
            "flags": self.history[-1]["flags"],
        }


# ============================================================
# VARIABLE MAP: TAF ↔ HAAS-Q shared namespace
# ============================================================

FIELD_MAP = {
    # TAF variable            → HAAS-Q variable              Direction
    "fatigue_score":          ("HumanEnergyState.fatigue_score", "TAF→HAAS"),
    "collapse_distance":      ("HumanEnergyState.collapse_distance", "TAF→HAAS"),
    "total_load":             ("HumanEnergyState.total_load", "TAF→HAAS"),
    "hidden_count":           ("sensor_noise → hidden_count", "HAAS→TAF"),
    "automation_reliability": ("brake_efficiency", "HAAS→TAF"),
    "parasitic_debt":         ("cumulative_friction_cost", "TAF→HAAS"),
    "risk_amplifier":         ("fatigue_degradation in compute_risk", "TAF→HAAS"),
    "zone_level":             ("ZoneLevel (GREEN/YELLOW/RED)", "TAF→HAAS"),
    "drift_index":            ("drift_index in check_alerts", "TAF→HAAS"),
    "haas_risk":              ("compute_risk() output", "HAAS→TAF"),
    "haas_confidence":        ("compute_confidence() output", "HAAS→TAF"),
    "haas_alerts":            ("check_alerts() output", "HAAS→TAF"),
    "override_count":         ("human-AI mismatch counter", "HAAS→TAF"),
    "ghost_friction":         ("ghost_friction_cost() / AI-tax", "bidirectional"),
}


# ============================================================
# EXAMPLE: Coupled simulation
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("  HAAS-Q ↔ TAF FIELD LINK — Coupled Simulation")
    print("=" * 60)

    link = FieldLink(energy_input=100.0)

    # Simulate 10 steps of a warehouse shift with escalating conditions
    scenarios = [
        # (risk, confidence, alerts, overrides, friction, hidden, auto, rel, temp, wind, latency)
        (0.1, 0.95, [],                          0, 0, 2, 1, 0.95, 18, 0, 50),
        (0.2, 0.90, [],                          0, 0, 2, 1, 0.95, 18, 0, 50),
        (0.3, 0.85, ["LOW_CONFIDENCE"],           0, 1, 3, 2, 0.90, 15, 2, 80),
        (0.4, 0.75, ["LOW_CONFIDENCE"],           1, 1, 3, 2, 0.88, 12, 5, 100),
        (0.5, 0.65, ["CRITICAL"],                 2, 2, 4, 2, 0.85, 10, 8, 120),
        (0.6, 0.55, ["CRITICAL", "DRIFT_RECALIBRATION"], 3, 2, 5, 3, 0.80, 8, 10, 150),
        (0.7, 0.50, ["CRITICAL", "HUMAN_AI_MISMATCH"],   4, 3, 6, 3, 0.75, 5, 12, 180),
        (0.8, 0.40, ["CRITICAL", "HUMAN_AI_MISMATCH"],   5, 3, 7, 3, 0.70, 2, 15, 200),
        (0.9, 0.30, ["CRITICAL", "LOW_CONFIDENCE", "HUMAN_AI_MISMATCH"], 6, 4, 8, 4, 0.65, 0, 18, 250),
        (0.95, 0.20, ["CRITICAL", "LOW_CONFIDENCE", "HUMAN_AI_MISMATCH", "DRIFT_RECALIBRATION"], 8, 5, 9, 4, 0.60, -5, 20, 300),
    ]

    for i, s in enumerate(scenarios):
        result = link.step(
            haas_risk=s[0], haas_confidence=s[1], haas_alerts=s[2],
            override_count=s[3], friction_events=s[4], hidden_count=s[5],
            automation_count=s[6], automation_reliability=s[7],
            temp_celsius=s[8], wind_mps=s[9], latency_ms=s[10],
        )
        zone_marker = {"GREEN": ".", "YELLOW": "!", "RED": "X"}[result["zone_level"]]
        print(
            f"  Step {result['step']:2d} [{zone_marker}] "
            f"fatigue={result['fatigue_score']:4.1f}  "
            f"collapse_dist={result['collapse_distance']:.3f}  "
            f"risk_amp={result['risk_amplifier']:.3f}  "
            f"drift={result['drift_index']:.3f}  "
            f"zone={result['zone_level']}"
        )
        if result["flags"]:
            for flag in result["flags"]:
                print(f"         ⚠ {flag}")

    print("\n" + "-" * 60)
    print("  SUMMARY")
    print("-" * 60)
    s = link.summary()
    for k, v in s.items():
        print(f"  {k}: {v}")
