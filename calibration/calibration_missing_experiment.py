"""
calibration_missing_experiment.py -- what should a missing calibration
dimension score?  An experiment; calibration_audit.py is not changed.

calibration_audit scores a dimension with no input as 0.5 (bite_source,
skin_in_game, witness_dependence, adaptation_debt) or 0.0
(memorialization_extinction). Registered as SILENT_FILL SF02, SF04-SF07
in silent_fill_register.py. Three readings, none picked:

    A  void      a missing dimension is left out of the aggregate; all
                 missing -> NOT_MEASURED
    B  assumed   a missing dimension takes the value in ASSUMED below,
                 labelled PROPOSED and reported as assumed. The table is
                 seeded with today's fills so B equals C until edited
                 (to be edited by Kavik)
    C  baseline  current behaviour

A dimension counts as missing when its input list is absent or empty.
SF03 (events present, all counts zero) is not switched here.

stdlib only. CC0.
"""

from __future__ import annotations

from schema import Band, CalibrationReport

NOT_MEASURED = "NOT_MEASURED"

# dimension -> input key in system_desc (calibration_audit.run_calibration_audit)
DIM_INPUT = {
    "bite_source": "feedback_events",
    "skin_in_game": "decisions",
    "witness_dependence": "skills_observed",
    "memorialization_extinction": "memorialized_skills",
    "adaptation_debt": "friction_events",
}

# PROPOSED -- seeded with the current fills; edit to change variant B.
ASSUMED = {
    "bite_source": 0.5,
    "skin_in_game": 0.5,
    "witness_dependence": 0.5,
    "memorialization_extinction": 0.0,
    "adaptation_debt": 0.5,
}


def missing_dims(desc: dict) -> list[str]:
    return [d for d, k in DIM_INPUT.items() if not desc.get(k)]


def calibration_score(desc: dict, variant: str):
    """(score or None, band value, missing dims) for calibration_audit."""
    from calibration_audit import run_calibration_audit
    rep = run_calibration_audit(desc)
    miss = set(missing_dims(desc))
    scores = []
    for d in rep.dimensions:
        if d.name in miss:
            if variant == "A":
                continue
            if variant == "B":
                scores.append(ASSUMED[d.name])
                continue
        scores.append(d.score)
    if not scores:
        return (None, NOT_MEASURED, sorted(miss))
    agg, band = CalibrationReport.aggregate(scores)
    return (agg, band.value, sorted(miss))


def pipeline_score(desc: dict, variant: str):
    """unified_score / band with the calibration module under `variant`."""
    from pipeline import run_unified_audit
    rep = run_unified_audit(desc)
    cal, _b, _m = calibration_score(desc, variant)
    others = [m["aggregate_score"] for n, m in rep["module_reports"].items()
              if n != "calibration"]
    scores = ([cal] if cal is not None else []) + others
    if not scores:
        return (None, NOT_MEASURED)
    s = sum(scores) / len(scores)
    return (s, Band.from_score(s).value)


def rows():
    from calibration_cases import cases
    out = []
    for cid, _src, desc in cases():
        r = {"case": cid, "missing": missing_dims(desc)}
        for v in "ABC":
            r[f"cal_{v}"] = calibration_score(desc, v)[:2]
            r[f"pipe_{v}"] = pipeline_score(desc, v)
        out.append(r)
    return out


def _f(sb):
    s, b = sb
    return b if s is None else f"{s:.4f} {b}"


def render() -> str:
    lines = ["| case | missing dims | calibration A / B / C | pipeline A / B / C | bands move? |",
             "|---|---|---|---|---|"]
    for r in rows():
        cal = " / ".join(_f(r[f"cal_{v}"]) for v in "ABC")
        pipe = " / ".join(_f(r[f"pipe_{v}"]) for v in "ABC")
        moves = []
        for k in ("cal", "pipe"):
            bands = {r[f"{k}_{v}"][1] for v in "ABC"}
            if len(bands) > 1:
                moves.append(k)
        lines.append(f"| {r['case']} | {', '.join(r['missing']) or '-'} | {cal} | "
                     f"{pipe} | {', '.join(moves) or 'no'} |")
    return "\n".join(lines) + "\n"


def selftest() -> int:
    from pipeline import run_unified_audit
    from calibration_cases import cases
    checks, bad = 0, []
    for cid, _s, desc in cases():
        checks += 1
        c = pipeline_score(desc, "C")
        ref = run_unified_audit(desc)
        if c[1] != ref["unified_band"] or abs(c[0] - ref["unified_score"]) > 1e-3:
            bad.append(f"C != current on {cid}")
        checks += 1
        if calibration_score(desc, "B") != calibration_score(desc, "C"):
            bad.append(f"seeded B != C on {cid}")
    checks += 1
    if calibration_score({"system_id": "x"}, "A")[1] != NOT_MEASURED:
        bad.append("A all-missing not NOT_MEASURED")
    print(f"checks: {checks}   failed: {len(bad)}")
    for b in bad:
        print("  FAIL", b)
    return 1 if bad else 0


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    print(render())
