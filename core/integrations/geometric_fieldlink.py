#!/usr/bin/env python3
"""
Geometric-to-Binary Field Link — Bridge between TAF and the
Geometric-to-Binary Computational Bridge (G2B).

TAF measures institutional systems in energy units.
G2B translates spatial/geometric intelligence into optimized binary.

The shared field is SIGNAL ENCODING. Both systems transform between
representation layers:
    TAF:  institutional narrative → energy physics (strips lossy encoding)
    G2B:  geometric intuition → binary protocol (preserves structural truth)

The bridge operates at three levels:

1. SENSOR LEVEL: G2B's SensorDecoder outputs (health_score, confidence,
   temperature, noise, drift) map directly to TAF variables (fatigue,
   feedback integrity, environmental stress, hidden variables, signal decay).

2. NEGENTROPIC LEVEL: G2B's Core Principle defines alignment as
   "how effectively a system organizes energy and information."
   This IS the TAF energy balance equation in different notation.
   Joy (J) = energy organization = TAF's (E_returned - E_extracted).
   Stochastic variation (F_C) = TAF's hidden variable diversity.

3. ENCODING LEVEL: G2B's Gray-coded band quantization is a
   signal fidelity problem — same as TAF's feedback integrity.
   Lossy encoding in G2B (coarse bands) parallels lossy narrative
   in TAF (cultural labels hiding physics).

Reference: github.com/JinnZ2/Geometric-to-Binary-Computational-Bridge
Dependencies: stdlib only (math).
"""

import math


# ============================================================
# G2B → TAF: Sensor signals as energy state
# ============================================================

def health_score_to_fatigue(health_score):
    """Convert G2B hardware health score to TAF fatigue score.

    G2B health_score: 0-1 (0=failed, 1=perfect)
    TAF fatigue_score: 0-10 (0=rested, 10=collapsed)

    Parameters
    ----------
    health_score : float
        G2B health band value (0-1, quantized to 0.125 steps).

    Returns
    -------
    float
        TAF fatigue score (0-10). Inverted and scaled.
    """
    # Invert: health 1.0 → fatigue 0, health 0.0 → fatigue 10
    # Nonlinear: degradation accelerates as health drops below 0.5
    if health_score >= 1.0:
        return 0.0
    if health_score <= 0.0:
        return 10.0
    fatigue = 10.0 * (1.0 - health_score ** 0.7)
    return round(fatigue, 1)


def noise_to_hidden_count(noise_level):
    """Convert G2B noise level to TAF hidden variable count.

    Noise in the sensor signal = hidden variables affecting the system.
    Each unit of noise represents unmeasured factors corrupting
    the signal between reality and measurement.

    G2B noise bands: [0.0, 0.01, 0.05, 0.1, 0.2, 0.4, 0.7, 1.0]
    TAF hidden_count: 0-10

    Parameters
    ----------
    noise_level : float
        G2B noise band value (0-1).

    Returns
    -------
    int
        TAF hidden variable count estimate.
    """
    if noise_level <= 0.0:
        return 0
    # Map noise 0-1 to hidden count 0-10
    # Noise 0.1 → ~3 hidden vars, 0.5 → ~7, 1.0 → 10
    count = 10 * (1 - math.exp(-3.0 * noise_level))
    return min(int(round(count)), 10)


def drift_to_feedback_decay(drift_pct):
    """Convert G2B drift percentage to TAF feedback integrity loss.

    Drift = the sensor reading shifting away from ground truth over time.
    This IS feedback decay — the signal between cause and effect degrading.

    Parameters
    ----------
    drift_pct : float
        G2B drift percentage (0-50+).

    Returns
    -------
    float
        Feedback integrity reduction (0-10, subtract from TAF score).
    """
    if drift_pct <= 0:
        return 0.0
    # 1% drift → 0.5 integrity loss, 10% → 3.5, 50% → 8.0
    loss = 10 * (1 - math.exp(-0.04 * drift_pct))
    return round(min(loss, 10.0), 1)


def confidence_to_signal_fidelity(confidence):
    """Convert G2B confidence to TAF signal fidelity.

    G2B confidence = 1/(1+noise). Direct measure of signal clarity.
    TAF signal fidelity = how much of reality passes through the
    measurement/narrative layer.

    Parameters
    ----------
    confidence : float
        G2B computed confidence (0-1).

    Returns
    -------
    float
        TAF signal fidelity (0-1).
    """
    return round(max(0.0, min(1.0, confidence)), 3)


def drill_depth_to_investigation_urgency(drill_depth):
    """Convert G2B drill depth to TAF investigation urgency.

    G2B DrillDepth: PASS(0), MONITOR(1), QUARANTINE(2), ALERT(3)
    Maps to how urgently TAF should investigate hidden variables.

    Parameters
    ----------
    drill_depth : int or str
        G2B drill depth level.

    Returns
    -------
    dict
        TAF investigation parameters.
    """
    depth_map = {
        0: {"level": "PASS", "action": "nominal", "hidden_var_scan": False,
            "energy_audit": False},
        1: {"level": "MONITOR", "action": "track_trends", "hidden_var_scan": True,
            "energy_audit": False},
        2: {"level": "QUARANTINE", "action": "isolate_and_assess", "hidden_var_scan": True,
            "energy_audit": True},
        3: {"level": "ALERT", "action": "immediate_energy_balance_check",
            "hidden_var_scan": True, "energy_audit": True},
    }
    if isinstance(drill_depth, str):
        name_to_int = {"PASS": 0, "MONITOR": 1, "QUARANTINE": 2, "ALERT": 3}
        drill_depth = name_to_int.get(drill_depth.upper(), 0)
    return depth_map.get(drill_depth, depth_map[0])


# ============================================================
# TAF → G2B: Energy state as encoding constraints
# ============================================================

def fatigue_to_band_resolution(fatigue_score):
    """Determine required G2B band resolution from TAF fatigue.

    When the organism is fatigued, you need FINER measurement
    resolution — coarse bands hide the degradation happening
    between quantization steps.

    Parameters
    ----------
    fatigue_score : float
        TAF fatigue score (0-10).

    Returns
    -------
    dict
        Recommended G2B encoding parameters.
    """
    if fatigue_score <= 3.0:
        return {"min_bits": 3, "band_count": 8, "note": "standard resolution"}
    elif fatigue_score <= 6.0:
        return {"min_bits": 4, "band_count": 16, "note": "elevated — finer bands needed"}
    elif fatigue_score <= 8.0:
        return {"min_bits": 5, "band_count": 32, "note": "high fatigue — continuous monitoring"}
    else:
        return {"min_bits": 6, "band_count": 64, "note": "CRITICAL — maximum resolution required"}


def collapse_distance_to_drill(collapse_distance):
    """Convert TAF collapse distance to G2B drill depth recommendation.

    Parameters
    ----------
    collapse_distance : float
        TAF distance-to-collapse (0-1, 1=sustainable, 0=collapse).

    Returns
    -------
    int
        G2B DrillDepth value (0=PASS, 1=MONITOR, 2=QUARANTINE, 3=ALERT).
    """
    if collapse_distance > 0.6:
        return 0  # PASS
    elif collapse_distance > 0.35:
        return 1  # MONITOR
    elif collapse_distance > 0.15:
        return 2  # QUARANTINE
    else:
        return 3  # ALERT


def friction_ratio_to_encoding_loss(friction_ratio):
    """Estimate how much signal is lost in the institutional encoding.

    TAF friction ratio = how much energy is wasted on institutional overhead.
    G2B encoding loss = how much information is lost in quantization.

    The parallel: institutional narrative compresses reality just as
    band quantization compresses continuous signals. Higher friction =
    more signal lost in the encoding.

    Parameters
    ----------
    friction_ratio : float
        TAF friction ratio (0-1).

    Returns
    -------
    float
        Estimated encoding loss (0-1, fraction of signal lost).
    """
    # Friction maps to encoding loss: high friction = lossy narrative = lossy signal
    return round(min(friction_ratio * 1.2, 1.0), 3)


# ============================================================
# NEGENTROPIC ALIGNMENT COUPLING
# ============================================================

def joy_to_energy_balance(joy_score, variation_capacity):
    """Map G2B's negentropic alignment to TAF energy balance.

    G2B Core Principle defines:
        J (Joy) = how effectively a system organizes energy
        F_C (Stochastic variation) = creative deviation capacity

    TAF defines:
        energy_balance = E_returned - E_extracted
        hidden_variable_diversity = combinatorial failure space

    The mapping:
        J > 0 → energy_balance > 0 (sustainable)
        J < 0 → energy_balance < 0 (extractive)
        F_C high → system explores alternatives (resilient)
        F_C low → system rigid (fragile)

    Parameters
    ----------
    joy_score : float
        G2B energy organization metric (-1 to 1).
    variation_capacity : float
        G2B stochastic variation capacity (0-1).

    Returns
    -------
    dict
        TAF-compatible energy state.
    """
    # Joy → energy balance direction
    if joy_score > 0:
        fatigue_estimate = round(10 * (1 - joy_score), 1)
        status = "SUSTAINABLE"
    else:
        fatigue_estimate = round(10 * (1 + abs(joy_score)), 1)
        fatigue_estimate = min(fatigue_estimate, 10.0)
        status = "EXTRACTIVE"

    # Variation capacity → resilience (inverse of fragility)
    # Low variation = rigid = fragile = TAF's high hidden variable risk
    fragility = 1.0 - variation_capacity
    hidden_count_estimate = noise_to_hidden_count(fragility)

    # Phase transition: below critical threshold, system is fragile
    critical_threshold = 0.3
    if joy_score < critical_threshold and variation_capacity < critical_threshold:
        status = "COLLAPSE_RISK"

    return {
        "fatigue_estimate": fatigue_estimate,
        "hidden_count_estimate": hidden_count_estimate,
        "fragility": round(fragility, 3),
        "status": status,
        "note": (
            "J (energy organization) maps to TAF energy balance. "
            "F_C (variation capacity) maps to TAF resilience/diversity. "
            "Rigidity (low F_C) creates fragility — same as TAF's "
            "hidden variable accumulation under institutional pressure."
        ),
    }


# ============================================================
# VARIABLE MAP
# ============================================================

FIELD_MAP = {
    # G2B variable               → TAF variable                      Direction
    "health_score":              ("fatigue_score (inverted)",          "G2B→TAF"),
    "noise_level":               ("hidden_count",                     "G2B→TAF"),
    "drift_pct":                 ("feedback_integrity loss",          "G2B→TAF"),
    "confidence":                ("signal_fidelity",                  "G2B→TAF"),
    "drill_depth":               ("investigation_urgency",            "G2B→TAF"),
    "temperature_c":             ("environment_multiplier",           "G2B→TAF"),
    "failure_mode":              ("collapse_flags",                   "G2B→TAF"),
    "fatigue_score":             ("band_resolution requirement",      "TAF→G2B"),
    "collapse_distance":         ("drill_depth recommendation",       "TAF→G2B"),
    "friction_ratio":            ("encoding_loss estimate",           "TAF→G2B"),
    "Joy (J)":                   ("energy_balance",                   "G2B↔TAF"),
    "Variation (F_C)":           ("resilience / hidden_var_diversity", "G2B↔TAF"),
    "Gray-coded quantization":   ("narrative compression / fidelity",  "G2B↔TAF"),
}


# ============================================================
# EXAMPLE
# ============================================================

if __name__ == "__main__":
    print("=" * 65)
    print("  GEOMETRIC-TO-BINARY ↔ TAF FIELD LINK")
    print("  Signal encoding meets energy physics")
    print("=" * 65)

    # --- Simulate G2B sensor data ---
    print("\n  --- G2B Sensor → TAF State ---")
    scenarios = [
        ("Healthy component",    0.875, 0.01, 1.0, 0.98, 0),
        ("Degrading component",  0.500, 0.10, 10.0, 0.91, 1),
        ("Failing component",    0.250, 0.40, 50.0, 0.71, 2),
        ("Critical failure",     0.125, 0.70, 50.0, 0.59, 3),
    ]

    for label, health, noise, drift, conf, drill in scenarios:
        fatigue = health_score_to_fatigue(health)
        hidden = noise_to_hidden_count(noise)
        fb_loss = drift_to_feedback_decay(drift)
        fidelity = confidence_to_signal_fidelity(conf)
        urgency = drill_depth_to_investigation_urgency(drill)

        print(f"\n  [{label}]")
        print(f"    G2B:  health={health}  noise={noise}  drift={drift}%  conf={conf}")
        print(f"    TAF:  fatigue={fatigue}  hidden={hidden}  fb_loss={fb_loss}  "
              f"fidelity={fidelity}  action={urgency['action']}")

    # --- TAF state → G2B encoding requirements ---
    print("\n\n  --- TAF State → G2B Encoding ---")
    for fatigue, collapse_d, friction in [(2.0, 0.8, 0.1), (6.0, 0.4, 0.4), (9.0, 0.1, 0.8)]:
        res = fatigue_to_band_resolution(fatigue)
        drill = collapse_distance_to_drill(collapse_d)
        loss = friction_ratio_to_encoding_loss(friction)
        drill_names = {0: "PASS", 1: "MONITOR", 2: "QUARANTINE", 3: "ALERT"}
        print(f"    fatigue={fatigue} collapse={collapse_d} friction={friction} → "
              f"bits={res['min_bits']} drill={drill_names[drill]} loss={loss} "
              f"({res['note']})")

    # --- Negentropic alignment coupling ---
    print("\n\n  --- Negentropic Alignment → TAF Energy ---")
    for joy, var_cap in [(0.8, 0.7), (0.3, 0.5), (-0.2, 0.2), (-0.5, 0.1)]:
        result = joy_to_energy_balance(joy, var_cap)
        print(f"    J={joy:+.1f} F_C={var_cap} → fatigue={result['fatigue_estimate']}  "
              f"hidden={result['hidden_count_estimate']}  "
              f"fragility={result['fragility']}  {result['status']}")
