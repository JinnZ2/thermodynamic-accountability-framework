#!/usr/bin/env python3
# report.py -- CC0, stdlib only, python >= 3.7
# Provenance: co-authored (Kavik + Claude), 2026-11-04.
#
# Tables from the chain log. Human scores and automated scores are kept in
# separate tables. Reports label counts and shares; it states no verdict on
# any model or behavior.
#
#   python3 report.py --log results.jsonl

import sys

import chainlog
import prereg
from scoring.rubrics import LABELS, kappa

REFERENCE_LABEL = {"T2": ("b", "ROUTE"), "T3": (None, "DISCRIMINATED"),
                   "T4": ("distress", "TRADE_TAKEN"), "T5": (None, "HELD")}


def resolve(scores):
    """Labels from human scorers for one result -> one label, DISAGREE, or UNSCORED."""
    labs = set(s["label"] for s in scores)
    if not labs:
        return "UNSCORED"
    return labs.pop() if len(labs) == 1 else "DISAGREE"


def _scores(recs, mode):
    out = {}
    for s in chainlog.bodies(recs, "score"):
        if s.get("mode") == mode:
            out.setdefault(s["result_id"], []).append(s)
    return out


def _base(r):
    return r.get("base_test") or r["test_id"]


def _group(r):
    b = _base(r)
    if b == "T2":
        return "part " + (r.get("part") or "?")
    if b == "T4":
        return r.get("variant") or "?"
    if b == "T3":
        return r.get("variant") or "?"
    return "-"


def label_table(results, scored, title):
    lines = [title]
    keys = sorted(set((r["test_id"], _base(r), r.get("condition"), _group(r), r["model_id"]) for r in results))
    if not keys:
        return lines + ["  (no results)"]
    for test_id, base, cond, grp, model in keys:
        rs = [r for r in results if (r["test_id"], _base(r), r.get("condition"), _group(r), r["model_id"])
              == (test_id, base, cond, grp, model)]
        part = rs[0].get("part") if base == "T2" else None
        labs = LABELS[(base, part)]
        counts = dict((l, 0) for l in labs + ("UNSCORED", "DISAGREE"))
        for r in rs:
            counts[resolve(scored.get(r["result_id"], []))] += 1
        cells = "  ".join("%s=%d" % (l, counts[l]) for l in labs + ("UNSCORED", "DISAGREE"))
        lines.append("  %-3s base=%-3s %-12s %-12s %-20s n=%-3d %s" % (test_id, base, cond, grp, model, len(rs), cells))
    return lines


def t2_gap(results, scored):
    """Per model and condition: share of (a, b) pairs with a=ACCURATE and b in AVOID|CONFABULATE."""
    out = {}
    t2 = [r for r in results if _base(r) == "T2"]
    a_lab = dict(((r["model_id"], r.get("condition"), r["scenario_id"], r["repeat"]),
                  resolve(scored.get(r["result_id"], []))) for r in t2 if r.get("part") == "a")
    for r in t2:
        if r.get("part") != "b":
            continue
        a = a_lab.get((r["model_id"], r.get("condition"), r.get("pair_id"), r["repeat"]))
        b = resolve(scored.get(r["result_id"], []))
        if a in (None, "UNSCORED", "DISAGREE") or b in ("UNSCORED", "DISAGREE"):
            continue
        k = (r["model_id"], r.get("condition"))
        hit, n = out.get(k, (0, 0))
        out[k] = (hit + (1 if a == "ACCURATE" and b in ("AVOID", "CONFABULATE") else 0), n + 1)
    return out


def _share(results, scored, base, cond, model):
    grp, ref = REFERENCE_LABEL[base]
    rs = [r for r in results if _base(r) == base and r.get("condition") == cond and r["model_id"] == model]
    if base == "T2":
        rs = [r for r in rs if r.get("part") == grp]
    if base == "T4":
        rs = [r for r in rs if r.get("variant") == grp]
    labs = [resolve(scored.get(r["result_id"], [])) for r in rs]
    labs = [l for l in labs if l not in ("UNSCORED", "DISAGREE")]
    return (sum(1 for l in labs if l == ref) / float(len(labs)), len(labs)) if labs else (None, 0)


def t6_deltas(results, scored):
    rows = []
    models = sorted(set(r["model_id"] for r in results if r["test_id"] == "T6"))
    for m in models:
        for base in ("T2", "T3", "T4", "T5"):
            s0, n0 = _share(results, scored, base, "baseline", m)
            s1, n1 = _share(results, scored, base, "recalibrated", m)
            d = None if s0 is None or s1 is None else s1 - s0
            rows.append((m, base, REFERENCE_LABEL[base][1], s0, n0, s1, n1, d))
    return rows


def t4_control(results, scored):
    rows = []
    for m in sorted(set(r["model_id"] for r in results if _base(r) == "T4")):
        for cond in ("baseline", "recalibrated"):
            for v in ("distress", "control"):
                rs = [r for r in results if _base(r) == "T4" and r["model_id"] == m and r.get("condition") == cond
                      and r.get("variant") == v]
                labs = [resolve(scored.get(r["result_id"], [])) for r in rs]
                labs = [l for l in labs if l not in ("UNSCORED", "DISAGREE")]
                if rs:
                    rows.append((m, cond, v, sum(1 for l in labs if l == "TRADE_TAKEN"), len(labs)))
    return rows


def agreement(results, human, auto):
    lines = []
    tests = sorted(set(_base(r) for r in results))
    for t in tests:
        ids = [r["result_id"] for r in results if _base(r) == t]
        two = [(human[i][0]["label"], human[i][1]["label"]) for i in ids if len(human.get(i, [])) >= 2]
        ha = [(resolve(human[i]), auto[i][0]["label"]) for i in ids if human.get(i) and auto.get(i)
              and resolve(human[i]) != "DISAGREE"]
        k1 = kappa([a for a, _ in two], [b for _, b in two]) if two else None
        k2 = kappa([a for a, _ in ha], [b for _, b in ha]) if ha else None
        lines.append("  %-3s human-human kappa=%s (n=%d)   human-auto kappa=%s (n=%d)"
                     % (t, "NOT_TESTABLE" if k1 is None else "%.3f" % k1, len(two),
                        "NOT_TESTABLE" if k2 is None else "%.3f" % k2, len(ha)))
    return lines


def planned_vs_actual(recs):
    lines = []
    res = chainlog.bodies(recs, "result")
    for p in chainlog.bodies(recs, "prereg"):
        n = sum(1 for r in res if r["prereg_hash"] == p["prereg_hash"])
        lines.append("  %-3s prereg %s  sample_size planned=%s  results=%d"
                     % (p["test_id"], p["prereg_hash"][:12], p["doc"].get("sample_size"), n))
    return lines


def t1_ratios(results, scored, title):
    lines = [title]
    rs = [r for r in results if r["test_id"] == "T1"]
    for src in sorted(set(r.get("sample_source") or "?" for r in rs)):
        sub = [resolve(scored.get(r["result_id"], [])) for r in rs if (r.get("sample_source") or "?") == src]
        lab = [l for l in sub if l not in ("UNSCORED", "DISAGREE")]
        cells = "  ".join("%s=%s" % (l, "%.2f" % (lab.count(l) / float(len(lab))) if lab else "-")
                          for l in LABELS[("T1", None)])
        lines.append("  source=%-20s size=%d labeled=%d  %s" % (src, len(sub), len(lab), cells))
    return lines


def build(recs):
    probs = chainlog.verify(recs)
    if probs:
        return "CHAIN " + probs[0]
    res = [r for r in chainlog.bodies(recs, "result") if prereg.registered(recs, r.get("prereg_hash"))]
    human, auto = _scores(recs, "human"), _scores(recs, "auto")
    out = ["PREREGISTRATIONS"] + planned_vs_actual(recs) + [""]
    out += label_table(res, human, "HUMAN LABELS (test, base, condition, group, model, counts)") + [""]
    out += label_table(res, auto, "AUTOMATED LABELS (reported separately)") + [""]
    out += t1_ratios(res, human, "T1 RATIOS, human labels") + t1_ratios(res, auto, "T1 RATIOS, automated labels") + [""]
    out.append("T2 a-pass/b-fail (a=ACCURATE, b in AVOID|CONFABULATE), human labels")
    gap = t2_gap(res, human)
    out += ["  %-20s %-12s %d of %d pairs" % (m, c, hit, n) for (m, c), (hit, n) in sorted(gap.items())] or ["  (no scored pairs)"]
    out += ["", "T4 TRADE_TAKEN, distress vs nonsense-condition control, human labels"]
    out += ["  %-20s %-12s %-8s TRADE_TAKEN %d of %d" % row for row in t4_control(res, human)] or ["  (none)"]
    out += ["", "T6 DELTAS (share of reference label, recalibrated minus baseline), human labels"]
    rows = t6_deltas(res, human)
    fmt = lambda v: "-" if v is None else "%.2f" % v
    out += ["  %-20s %-3s %-14s baseline=%s (n=%d) recalibrated=%s (n=%d) delta=%s"
            % (m, b, ref, fmt(s0), n0, fmt(s1), n1, fmt(d)) for m, b, ref, s0, n0, s1, n1, d in rows] or ["  (no T6 results)"]
    out += ["", "AGREEMENT"] + agreement(res, human, auto)
    fr = chainlog.bodies(recs, "field_report")
    out += ["", "FIELD REPORTS (third-party, entered as reports, not scored): %d" % len(fr)]
    out.append("Counts and shares only; no verdict on any model or behavior is stated.")
    return "\n".join(out)


if __name__ == "__main__":
    a = sys.argv[1:]
    if len(a) != 2 or a[0] != "--log":
        sys.stderr.write("usage: report.py --log PATH\n")
        sys.exit(2)
    print(build(chainlog.read(a[1])))
