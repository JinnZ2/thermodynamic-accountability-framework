#!/usr/bin/env python3
# corruption_chain.py -- CC0, stdlib-only
# TAF composition layer. Chains independent audit verdicts into one read:
#   corruption(trend) = corruption(measurement) x corruption(framework) x ...
# Multiplicative: a clean layer (factor 1.0) passes through untouched; any
# corrupt layer inflates the product. Direction (under/over-estimation) is
# tracked and reconciled, because two underestimations COMPOUND while an
# under x over is a COINCIDENTAL offset, not a correction -- never trusted.
#
# Feeds directly from warning_time_audit.audit() and
# thermal_sensor_degradation_audit.audit(), or any GREEN/YELLOW/RED flag.
# Refutation protocol: recomputed every call, no stored verdict.

# ---------------------------------------------------------------
# CONVENTIONS
#   factor >= 1.0   1.0 = faithful; higher = more corrupt
#   direction       +1 UNDERESTIMATE (reads safe while state fails)
#                   -1 OVERESTIMATE  (reads alarmed early / conservative)
#                    0 neutral / unknown
# ---------------------------------------------------------------
FLAG_FACTOR = {"GREEN": 1.0, "YELLOW": 2.0, "RED": 5.0}

def _cap(x, lo=1.0, hi=50.0):
    return max(lo, min(hi, x))

# ---------------------------------------------------------------
# LAYER 1: ADAPTERS -- extract (factor, direction, source) from each
# module's native output. Prefer quantitative signal; fall back to flag.
# ---------------------------------------------------------------
def from_warning_time(out, name="framework/warning-time"):
    # quantitative: warning_lost_frac -> f = 1/(1-lost)
    v = out.get("verdict", {})
    lost = v.get("warning_lost_frac", 0.0)
    lost = lost if isinstance(lost, (int, float)) else 0.0
    f = _cap(1.0 / (1.0 - lost)) if lost < 1.0 else 50.0
    # direction from curve sign: concave(+) underestimates
    d = out.get("curve", {}).get("signed_deviation", 0.0)
    direction = 1 if d > 0.02 else (-1 if d < -0.02 else 0)
    return {"source": name, "factor": round(f, 3),
            "direction": direction, "basis": "warning_lost_frac + curve"}

def from_thermal_sensor(out, name="measurement/sensor", direction=1):
    # quantitative: electronics drift %; worst flag as backstop.
    drift = out.get("electronics", {}).get("projected_drift_pct", 0.0)
    f_drift = _cap(1.0 + drift)          # 100% drift -> factor 2.0
    flags = [out.get("verdict", "GREEN")]
    f_flag = max(FLAG_FACTOR.get(fl, 1.0) for fl in flags)
    f = _cap(max(f_drift, f_flag))
    # sensor bias under sustained heat/wet-bulb reads the stressor LOW
    return {"source": name, "factor": round(f, 3),
            "direction": direction, "basis": "sensor drift + verdict flag"}

def from_flag(flag, direction=0, name="layer"):
    return {"source": name, "factor": FLAG_FACTOR.get(flag, 1.0),
            "direction": direction, "basis": "flag only"}

# ---------------------------------------------------------------
# LAYER 2: COMPOSE -- multiplicative product + direction reconciliation
# ---------------------------------------------------------------
def compose(layers):
    product = 1.0
    for L in layers:
        product *= L["factor"]
    product = round(product, 3)

    dirs = [L["direction"] for L in layers if L["direction"] != 0]
    if not dirs:
        net_dir, coupling = 0, "neutral"
    elif all(x == dirs[0] for x in dirs):
        net_dir = dirs[0]
        coupling = "COMPOUNDING (same direction -- errors reinforce)"
    else:
        net_dir = 0
        coupling = ("MIXED (under x over) -- apparent cancellation is "
                    "COINCIDENTAL, not corrected. Do NOT trust the offset.")
    return product, net_dir, coupling

# ---------------------------------------------------------------
# LAYER 3: VERDICT
# ---------------------------------------------------------------
def _dir_word(d):
    return {1: "UNDERESTIMATE (reads safe while true state fails)",
            -1: "OVERESTIMATE (reads alarmed early)",
            0: "indeterminate"}[d]

def chain(layers):
    product, net_dir, coupling = compose(layers)
    if product < 1.5:
        flag = "GREEN"
    elif product < 3.0:
        flag = "YELLOW"
    else:
        flag = "RED"
    # mixed direction with a large product is its own hazard: the trend
    # looks moderate because two corruptions mask each other.
    masked = (net_dir == 0 and product >= 1.5 and
              any(L["direction"] != 0 for L in layers))
    return {
        "layers": layers,
        "trend_corruption_factor": product,
        "net_direction": _dir_word(net_dir),
        "coupling": coupling,
        "masking_risk": masked,
        "flag": flag,
        "read": (("MASKED: composite trend looks calmer than the substrate "
                  "-- offsetting corruptions hide a live failure. ")
                 if masked else "") +
                ("clean chain" if flag == "GREEN"
                 else "corrupt trend: act on substrate, not on proxy"),
        "falsify": ("co-observe true state against the full proxy chain "
                    "across one decline; total lag/bias should track the "
                    f"product factor {product}x if this verdict holds. "
                    "Break any single layer's assumption and the product "
                    "must move accordingly."),
    }

if __name__ == "__main__":
    import json
    # Compose two clean measurements through one corrupt framework:
    # sensor reads slightly low (heat drift) + SDM framework underestimates
    # loss badly (concave). Same direction -> compounding.
    measurement = from_flag("YELLOW", direction=1, name="measurement/sensor")
    framework = from_warning_time({
        "curve": {"signed_deviation": 0.18},
        "verdict": {"warning_lost_frac": 0.62},
    }, name="framework/SDM-linear-assumption")
    result = chain([measurement, framework])
    print(json.dumps(result, indent=1))
