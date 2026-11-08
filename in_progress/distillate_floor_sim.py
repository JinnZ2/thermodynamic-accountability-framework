#!/usr/bin/env python3
"""
distillate_floor_sim.py -- stdlib-only skeleton for the US distillate floor.

Structure is fixed; values are plugged in. Every term carries:
  value or (low, high) range, unit, STATUS, source, as-of date.

STATUS
  MEASURED     published value, sourced and dated
  DERIVED      computed from published values (method in source field)
  UNMEASURED   no open data; run as a range, never as a point
  PLACEHOLDER  no source at all; range is a stand-in to be replaced
  CENSORED     threshold where past responses fired before the break;
               usable only as a bound, never as the break point

What it reports (states, not verdicts):
  - usable barrels above the operating floor
  - days of cover with no inflow, days to floor at a net draw rate
  - first gate to close: fuel floor or DEF on hand
  - tornado ranking: which non-measured term the outcome swings on most
    = where measurement is worth the effort
  - Monte Carlo spread over ranges (uniform sampling is an ASSUMPTION of
    the run, not a probability about the world)

Usage:
  python3 distillate_floor_sim.py              # default run
  python3 distillate_floor_sim.py --shock 0.8 15   # lose 0.8 M b/d for 15 days
  python3 distillate_floor_sim.py --runs 50000 --seed 7
  python3 distillate_floor_sim.py --selftest

Co-authored. CC0.
"""
import math
import random
import statistics
import sys

CAP_DAYS = 365.0  # report ceiling when draw <= 0 (no depletion at that rate)

# ---------------------------------------------------------------- terms
# Edit values here. Ranges as (low, high). Point values as v.
TERMS = {
    "stock_total": dict(
        v=99.3, unit="M bbl", status="MEASURED",
        src="EIA WPSR distillate stocks, week ending", date="2026-10-30"),
    "demand": dict(
        v=4.175, unit="M b/d", status="MEASURED",
        src="EIA WPSR distillate product supplied, 4-wk avg", date="2026-10-30"),
    "pipeline_fill": dict(
        lo=28.0, hi=30.0, unit="M bbl", status="DERIVED",
        src="EIA annual total minus refinery+terminal+NGP stocks, 2022-2025",
        date="2025-12"),
    "tank_bottoms": dict(
        lo=9.0, hi=26.0, unit="M bbl", status="UNMEASURED",
        src="upper bound = 2016 shell-in-operation minus working (refineries+terminals); "
            "gap includes top contingency, so bottoms are SOME part of it",
        date="2016-09-30"),
    "terminal_working_min": dict(
        lo=0.0, hi=25.0, unit="M bbl", status="PLACEHOLDER",
        src="no open source: stock terminals need to keep loading trucks",
        date=None),
    "process_holdup": dict(
        lo=0.0, hi=10.0, unit="M bbl", status="PLACEHOLDER",
        src="no open source: distillate held in hydrotreaters / process units",
        date=None),
    "net_draw": dict(
        lo=0.0, hi=0.7, unit="M b/d", status="PLACEHOLDER",
        src="anchor: last week -3.5 M bbl = 0.5 M b/d (EIA WPSR 10/23->10/30); "
            "range is a stand-in for production - demand - net exports",
        date="2026-10-30"),
    "def_days_on_hand": dict(
        lo=7.0, hi=35.0, unit="days", status="PLACEHOLDER",
        src="no open US figure; Australia Dec 2021 had ~35 days on hand at intervention "
            "(CENSORED precedent, not a US value)",
        date=None),
}

NON_POINT = ("DERIVED", "UNMEASURED", "PLACEHOLDER")


# ---------------------------------------------------------------- helpers
def is_point(t):
    return "v" in t


def mid(t):
    return t["v"] if is_point(t) else (t["lo"] + t["hi"]) / 2.0


def validate(terms):
    """Refuse malformed terms. Returns list of problems (empty = ok)."""
    problems = []
    for name, t in terms.items():
        st = t.get("status")
        if st not in ("MEASURED", "DERIVED", "UNMEASURED", "PLACEHOLDER", "CENSORED"):
            problems.append(f"{name}: unknown status {st!r}")
        if st in ("UNMEASURED", "PLACEHOLDER") and is_point(t):
            problems.append(f"{name}: {st} term given as a point; must be a range")
        if not is_point(t):
            if "lo" not in t or "hi" not in t:
                problems.append(f"{name}: range needs lo and hi")
            elif t["lo"] > t["hi"]:
                problems.append(f"{name}: lo > hi")
        if st == "CENSORED":
            problems.append(f"{name}: CENSORED values are bounds only; "
                            "not accepted as model inputs")
        if not t.get("src"):
            problems.append(f"{name}: missing source field")
    return problems


# ---------------------------------------------------------------- model
def days_to_floor(usable, draw, shock_loss=0.0, shock_days=0.0):
    """Days until usable barrels hit zero.
    draw: baseline net draw (M b/d). shock adds shock_loss M b/d for shock_days."""
    if usable <= 0:
        return 0.0
    d1 = draw + shock_loss
    if shock_days > 0 and d1 > 0:
        used_in_shock = d1 * shock_days
        if used_in_shock >= usable:
            return usable / d1
        usable -= used_in_shock
        elapsed = shock_days
    else:
        elapsed = 0.0
    if draw <= 0:
        return CAP_DAYS
    return min(CAP_DAYS, elapsed + usable / draw)


def evaluate(x, shock_loss=0.0, shock_days=0.0):
    """x: dict name -> number. Returns dict of outputs."""
    static_floor = x["pipeline_fill"] + x["tank_bottoms"] + x["process_holdup"]
    operating_floor = static_floor + x["terminal_working_min"]
    usable = x["stock_total"] - operating_floor
    cover = max(0.0, usable) / x["demand"] if x["demand"] > 0 else CAP_DAYS
    dtf = days_to_floor(usable, x["net_draw"], shock_loss, shock_days)
    # Gate compares SAME BASIS: both sides with resupply stopped.
    # (DEF days on hand is a no-resupply figure; comparing it to fuel days
    #  with production still running would be a mixed basis.)
    gate_days = min(cover, x["def_days_on_hand"])
    gate = "FUEL FLOOR" if cover <= x["def_days_on_hand"] else "DEF"
    return dict(static_floor=static_floor, operating_floor=operating_floor,
                usable=usable, cover_days_no_inflow=cover,
                days_to_floor=dtf, first_gate=gate, first_gate_days=gate_days)


def point_inputs(terms):
    return {k: mid(t) for k, t in terms.items()}


def tornado(terms, output="first_gate_days", shock_loss=0.0, shock_days=0.0):
    """One-at-a-time swing for every non-point term, others at midpoint."""
    base = point_inputs(terms)
    rows = []
    for name, t in terms.items():
        if is_point(t):
            continue
        lo_x = dict(base, **{name: t["lo"]})
        hi_x = dict(base, **{name: t["hi"]})
        a = evaluate(lo_x, shock_loss, shock_days)[output]
        b = evaluate(hi_x, shock_loss, shock_days)[output]
        rows.append((abs(b - a), name, a, b, t["status"]))
    rows.sort(reverse=True)
    return rows


def monte_carlo(terms, runs=20000, seed=1, shock_loss=0.0, shock_days=0.0):
    rng = random.Random(seed)
    gate_days, usable, gates = [], [], {"FUEL FLOOR": 0, "DEF": 0}
    below = 0
    for _ in range(runs):
        x = {k: (t["v"] if is_point(t) else rng.uniform(t["lo"], t["hi"]))
             for k, t in terms.items()}
        out = evaluate(x, shock_loss, shock_days)
        gate_days.append(out["first_gate_days"])
        usable.append(out["usable"])
        gates[out["first_gate"]] += 1
        if out["usable"] <= 0:
            below += 1
    return dict(gate_days=gate_days, usable=usable, gates=gates,
                frac_at_or_below_floor=below / runs, runs=runs)


def pct(xs, p):
    s = sorted(xs)
    k = (len(s) - 1) * p
    f, c = math.floor(k), math.ceil(k)
    return s[f] if f == c else s[f] + (s[c] - s[f]) * (k - f)


# ---------------------------------------------------------------- report
def report(terms, runs, seed, shock_loss, shock_days):
    probs = validate(terms)
    if probs:
        print("REFUSED -- fix terms first:")
        for p in probs:
            print("  -", p)
        return 2

    print("TERMS")
    for k, t in terms.items():
        val = f"{t['v']}" if is_point(t) else f"{t['lo']}-{t['hi']}"
        print(f"  {k:22s} {val:>12s} {t['unit']:7s} {t['status']:11s} "
              f"{t.get('date') or 'no date'}")
    if shock_days:
        print(f"\nSHOCK  extra draw {shock_loss} M b/d for {shock_days} days")

    m = evaluate(point_inputs(terms), shock_loss, shock_days)
    print("\nMIDPOINT RUN (every range at its middle)")
    for k in ("static_floor", "operating_floor", "usable",
              "cover_days_no_inflow", "days_to_floor", "first_gate_days"):
        print(f"  {k:22s} {m[k]:8.1f}")
    print(f"  {'first_gate':22s} {m['first_gate']:>8s}")

    labels = {
        "cover_days_no_inflow": "fuel days above floor, resupply stopped",
        "days_to_floor": "fuel days to floor at net draw (+shock)",
        "first_gate_days": "first gate, resupply stopped (fuel vs DEF)",
    }
    for out_name, label in labels.items():
        print(f"\nTORNADO  {out_name}  ({label}; others at midpoint)")
        print("  rank  term                    at low   at high   swing  status")
        rows = [r for r in tornado(terms, out_name, shock_loss, shock_days)
                if r[0] > 1e-9]
        for i, (sw, name, a, b, st) in enumerate(rows, 1):
            print(f"  {i:>4}  {name:22s} {a:7.1f}  {b:8.1f}  {sw:6.1f}  {st}")
    print("  -> top rows = where measuring is worth the effort"
          "\n  (terms with zero swing on an output are left off that table)")

    mc = monte_carlo(terms, runs, seed, shock_loss, shock_days)
    g = mc["gate_days"]
    print(f"\nSPREAD  {runs} runs, uniform over ranges (assumption of the run)")
    print(f"  first_gate_days  p5 {pct(g, .05):6.1f}  p50 {pct(g, .5):6.1f}  "
          f"p95 {pct(g, .95):6.1f}")
    u = mc["usable"]
    print(f"  usable M bbl     p5 {pct(u, .05):6.1f}  p50 {pct(u, .5):6.1f}  "
          f"p95 {pct(u, .95):6.1f}")
    print(f"  share of runs with stock at/below operating floor: "
          f"{mc['frac_at_or_below_floor']:.1%}")
    print(f"  first gate to close: FUEL FLOOR {mc['gates']['FUEL FLOOR']}  "
          f"DEF {mc['gates']['DEF']}")
    print("\nNOT IN MODEL: regional split (PADD 1 floor), heating-oil competition,"
          "\n  waiver fuel usable only by pre-2007 fleet, cold-flow, allocation order.")
    return 0


# ---------------------------------------------------------------- selftest
def selftest():
    ok = 0
    total = 0

    def check(cond, label):
        nonlocal ok, total
        total += 1
        if cond:
            ok += 1
        else:
            print("FAIL:", label)

    check(validate(TERMS) == [], "default terms validate")
    bad = dict(TERMS, x=dict(v=1.0, unit="", status="UNMEASURED", src="s"))
    check(any("must be a range" in p for p in validate(bad)),
          "unmeasured point refused")
    cen = dict(TERMS, x=dict(lo=1, hi=2, unit="", status="CENSORED", src="s"))
    check(any("CENSORED" in p for p in validate(cen)), "censored input refused")
    nos = dict(TERMS, x=dict(lo=1, hi=2, unit="", status="UNMEASURED", src=""))
    check(any("missing source" in p for p in validate(nos)), "missing source refused")
    inv = dict(TERMS, x=dict(lo=3, hi=2, unit="", status="UNMEASURED", src="s"))
    check(any("lo > hi" in p for p in validate(inv)), "inverted range refused")

    check(days_to_floor(10, 1) == 10, "simple depletion")
    check(days_to_floor(10, 0) == CAP_DAYS, "no draw -> cap")
    check(days_to_floor(-1, 1) == 0, "already below floor")
    # 10 usable; 2 days at draw 1+1 uses 4 -> 6 left at draw 1 -> 2 + 6 = 8
    check(abs(days_to_floor(10, 1, 1, 2) - 8) < 1e-9, "shock then baseline")
    check(abs(days_to_floor(10, 0, 5, 5) - 2) < 1e-9, "floor hit inside shock")

    x = point_inputs(TERMS)
    out = evaluate(x)
    check(abs(out["usable"] - (x["stock_total"] - out["operating_floor"])) < 1e-9,
          "usable = stock - operating floor")
    check(out["first_gate_days"] <= out["cover_days_no_inflow"],
          "gate <= fuel cover (same no-resupply basis)")

    rows = tornado(TERMS)
    check(all(not is_point(TERMS[r[1]]) for r in rows), "tornado skips measured")
    check(rows == sorted(rows, reverse=True), "tornado sorted by swing")

    a = monte_carlo(TERMS, 500, 3)["gate_days"]
    b = monte_carlo(TERMS, 500, 3)["gate_days"]
    check(a == b, "seeded runs reproduce")

    print(f"selftest {ok}/{total}")
    return 0 if ok == total else 1


# ---------------------------------------------------------------- cli
def main(argv):
    if "--selftest" in argv:
        return selftest()
    runs, seed, shock_loss, shock_days = 20000, 1, 0.0, 0.0
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--runs":
            runs = int(argv[i + 1]); i += 2
        elif a == "--seed":
            seed = int(argv[i + 1]); i += 2
        elif a == "--shock":
            shock_loss = float(argv[i + 1]); shock_days = float(argv[i + 2]); i += 3
        else:
            print("unknown arg:", a); return 2
    return report(TERMS, runs, seed, shock_loss, shock_days)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
