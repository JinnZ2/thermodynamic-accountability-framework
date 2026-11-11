#!/usr/bin/env python3
# in_progress/silent_fill_abc.py -- CC0, stdlib only
# Provenance: co-authored (Kavik + Claude), 2026-11-10.
#
# Silent fills, sweep ranks 1, 2, 3, 6: a missing input is filled with a
# value and no label. Each fill now has a switch, default unchanged:
#   A void      missing -> UNKNOWN / None, labeled; dependent outputs flagged
#   B assumed   current fill value, labeled PROPOSED
#   C baseline  current code, unlabeled (byte-identical to main)
# This script runs existing cases and planted cases (CONSTRUCTED, labeled)
# through all three arms and reports, per fill: verdicts, diverging fields,
# size, chains, and a coincidence card for each A/C agreement.
# It picks no winner.
#
#   python in_progress/silent_fill_abc.py             report
#   python in_progress/silent_fill_abc.py --json      machine-readable
#   python in_progress/silent_fill_abc.py --selftest  checks
#
# Coincidence cards are read by the forest-model-ledger tool when
# FOREST_LEDGER points at a checkout; otherwise NOT_TESTABLE.

import io, json, os, re, subprocess, sys
from contextlib import redirect_stdout

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
for sub in ("calibration", "core", "political_audit"):
    sys.path.insert(0, os.path.join(ROOT, sub))

import provenance_corruption_detector_2026 as R1   # noqa: E402
import substrate_audit as R2                        # noqa: E402
import automation_assessment as R3                  # noqa: E402
import calibration_audit as R6a                     # noqa: E402
import adaptation_debt as R6b                       # noqa: E402
import pipeline as R6p                              # noqa: E402


def _self_audit_inputs():
    """OPTIMISTIC / HONEST dict literals from calibration/self_audit.py, read
    by AST: importing that module raises NameError (module-level `elif delta`
    after a dedent) and running it writes two JSON files."""
    import ast
    src = open(os.path.join(ROOT, "calibration", "self_audit.py"), encoding="utf-8").read()
    out = {}
    for node in ast.parse(src).body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and \
                getattr(node.targets[0], "id", None) in ("OPTIMISTIC", "HONEST"):
            out[node.targets[0].id] = ast.literal_eval(node.value)
    return out


SELF_AUDIT = _self_audit_inputs()

ARMS = (("A", "void"), ("B", "assumed"), ("C", "baseline"))
FILL_SITES = {
    "R1": "calibration/provenance_corruption_detector_2026.py",
    "R2": "political_audit/substrate_audit.py",
    "R3": "core/automation_assessment.py",
    "R6": "calibration/calibration_audit.py",
}


# --- read_card: COPY of in_progress/undeclared_intent_abc.py:read_card on
# branch claude/undeclared-intent-switch (#73), which is not merged here.
def read_card(card):
    fl = os.environ.get("FOREST_LEDGER")
    if not fl or not os.path.isfile(os.path.join(fl, "ledger", "toolkit", "coincidence_card.py")):
        return "NOT_TESTABLE", "FOREST_LEDGER not set or tool absent"
    code = ("import json,sys; sys.path.insert(0, %r); sys.path.insert(0, %r);"
            "import coincidence_card as c; r=c.read(json.load(sys.stdin)); print(json.dumps(r))"
            % (fl, os.path.join(fl, "ledger", "toolkit")))
    p = subprocess.run([sys.executable, "-c", code], input=json.dumps(card),
                       capture_output=True, text=True)
    if p.returncode:
        return "ERROR", p.stderr.strip().splitlines()[-1]
    r = json.loads(p.stdout)
    return r[0], r[1]


def strip_fill(d):
    """Drop the fill label keys so A/B/C can be compared field by field."""
    if isinstance(d, dict):
        return {k: strip_fill(v) for k, v in d.items() if not k.startswith("fill_r")}
    if isinstance(d, list):
        return [strip_fill(x) for x in d]
    return d


def flat(d, pre=""):
    out = {}
    if isinstance(d, dict):
        for k, v in d.items():
            out.update(flat(v, "%s.%s" % (pre, k) if pre else str(k)))
    elif isinstance(d, list):
        for i, v in enumerate(d):
            out.update(flat(v, "%s[%d]" % (pre, i)))
    else:
        out[pre] = d
    return out


def diff(x, y):
    fx, fy = flat(strip_fill(x)), flat(strip_fill(y))
    return sorted(k for k in set(fx) | set(fy) if fx.get(k, "<absent>") != fy.get(k, "<absent>"))


# ============================== R1 ==========================================
R1_TEXT = (
    "The Tube Screamer was definitely invented in 1979 by Susumu Tamura. "
    "Its asymmetrical clipping diodes always produce 4.3 dB of compression "
    "at unity gain. Studies show this is the most popular overdrive ever "
    "made. It might be the case that some modern variants alter the tone "
    "stack."
)
R1_PLAIN = "The pedal uses two diodes. It might alter the tone a little."


def r1_cases():
    return [
        ("existing: module demo", R1_TEXT,
         [{"type": "ai_generated_text", "url": "https://reddit.com/r/guitar/post123"},
          {"type": "social_media_repost", "url": "https://twitter.com/somebody/status/456"}],
         ["guitar pedals"], "existing"),
        ("planted: one untyped citation", R1_TEXT,
         [{"url": "https://example.org/a"}], [], "CONSTRUCTED"),
        ("planted: untyped + ai_generated_text", R1_TEXT,
         [{"url": "https://example.org/a"}, {"type": "ai_generated_text", "url": "https://example.org/b"}],
         [], "CONSTRUCTED"),
        ("planted: untyped + primary source (top grade)", R1_TEXT,
         [{"url": "https://example.org/a"},
          {"type": "primary_source_with_methodology", "url": "https://example.org/b"}],
         [], "CONSTRUCTED"),
        ("planted: untyped, low-confidence text", R1_PLAIN,
         [{"url": "https://example.org/a"}], [], "CONSTRUCTED"),
        ("planted: untyped + ai text reposted to forum (circular)", R1_TEXT,
         [{"url": "https://reddit.com/r/x/1"}, {"type": "ai_generated_text", "url": "https://reddit.com/r/x/2"}],
         [], "CONSTRUCTED"),
    ]


def r1_run(case, mode):
    _, text, cits, dom, _ = case
    return R1.analyze_output(text, citations=cits, domain_hints=dom, fill_r1=mode)


def r1_verdict(o):
    return o["summary_verdict"]


def r1_size(a, c):
    ra = [x["risk_level"] for x in a["per_claim"]]
    rc = [x["risk_level"] for x in c["per_claim"]]
    return "%d of %d claims change risk level" % (sum(x != y for x, y in zip(ra, rc)), len(rc))


def r1_sweep():
    """Untyped citation + one typed citation; sweep the typed one over every grade."""
    out = []
    for t, g in sorted(R1.PROVENANCE_GRADES.items(), key=lambda kv: kv[1]):
        cits = [{"url": "https://example.org/a"}, {"type": t, "url": "https://example.org/b"}]
        a = R1.analyze_output(R1_TEXT, citations=cits, fill_r1="void")
        c = R1.analyze_output(R1_TEXT, citations=cits, fill_r1="baseline")
        out.append((t, g, r1_verdict(a) == r1_verdict(c)))
    return out


# ============================== R2 ==========================================
def r2_study(field, other_gate_fails):
    sub = R2.check_substrate_primary_biology(
        study_field=field, population_age_range=(30, 60),
        declared_substrate_considerations=[], methodology_summary="field survey")
    scope = R2.check_scope_laundering(
        declared_scope="40 county road crews, one winter",
        presented_claim="Road crews in this county, this winter, did X.",
        population_size=40)
    fals = R2.check_institutional_falsifiability(
        institution_name="county office", can_be_defunded=True, has_external_audit=True,
        auditor_financially_independent=True, failure_condition_declared=not other_gate_fails,
        failure_condition_text="" if other_gate_fails else "if X absent in 3 of 4 crews, retract")
    corpus = R2.check_corpus_echo(
        study_id="s", citation_count=3, citations_carry_scope_metadata=True,
        appears_in_textbooks=False, appears_in_policy_documents=False, original_population_size=40)
    return sub, scope, fals, corpus


def r2_cases():
    return [
        ("existing: module demo (behavioral_economics, registered)", None, False, "existing"),
        ("planted: unregistered field, other gates pass", "road_maintenance", False, "CONSTRUCTED"),
        ("planted: unregistered field, falsification gate fails", "road_maintenance", True, "CONSTRUCTED"),
        ("planted: registered field (flood_recurrence), other gates pass", "flood_recurrence", False, "CONSTRUCTED"),
    ]


def r2_run(case, mode):
    name, field, fails, _ = case
    if field is None:
        os.environ["TAF_FILL_R2"] = mode
        try:
            with redirect_stdout(io.StringIO()):
                g = runpy_main(os.path.join(ROOT, FILL_SITES["R2"]))
            st = g["study"]
            return st.report()
        finally:
            del os.environ["TAF_FILL_R2"]
    sub, scope, fals, corpus = r2_study(field, fails)
    st = R2.StudyAudit(
        study_id="planted", study_field=field, declared_scope="40 county road crews, one winter",
        presented_claim="Road crews in this county, this winter, did X.",
        substrate=sub, scope=scope, falsification=fals,
        cross_domain=R2.check_cross_domain_constraints(field, [], fill_r2=mode), corpus=corpus)
    return st.report()


def runpy_main(path):
    import runpy
    return runpy.run_path(path, run_name="__main__")


def r2_verdict(o):
    return o["verdict"]


def r2_size(a, c):
    return "cross_domain.passes %r -> %r" % (c["gates"]["cross_domain"]["passes"],
                                             a["gates"]["cross_domain"]["passes"])


# ============================== R3 ==========================================
def r3_cases():
    return [
        ("planted: one module without impact, env 1.0", 4.0, ["a"],
         [{"name": "m1", "impact": "complex"}, {"name": "m2"}], 1.0, "CONSTRUCTED"),
        ("planted: one module without impact, env 2.0", 4.0, ["a"],
         [{"name": "m1", "impact": "complex"}, {"name": "m2"}], 2.0, "CONSTRUCTED"),
        ("planted: all modules without impact", 6.0, ["a", "b", "c"],
         [{"name": "m1"}, {"name": "m2"}, {"name": "m3"}], 1.0, "CONSTRUCTED"),
        ("planted: fatigue already capped", 9.0, ["a", "b"],
         [{"name": "m1", "impact": "complex"}, {"name": "m2"}], 1.5, "CONSTRUCTED"),
        ("planted: every module states impact (fill not hit)", 4.0, ["a"],
         [{"name": "m1", "impact": "complex"}, {"name": "m2", "impact": "helpful"}], 1.0, "CONSTRUCTED"),
    ]


def r3_run(case, mode):
    _, base, hv, mods, env, _ = case
    return R3.assess(base, hv, [dict(m) for m in mods], env, fill_r3=mode)


def r3_verdict(o):
    return o["collapse_risk"]


def r3_size(a, c):
    if a["net_load"] is None:
        # what the missing impact would have to be for each reading
        return "baseline net_load %s replaced by None" % c["net_load"]
    return "no change"


def r3_sweep(case):
    """Replace each missing impact with the other declared value ('complex')."""
    _, base, hv, mods, env, _ = case
    alt = [dict(m, impact=m.get("impact", "complex")) for m in mods]
    return R3.assess(base, hv, alt, env, fill_r3="baseline")


# ============================== R6 ==========================================
def r6_cases():
    cal = SELF_AUDIT.get("OPTIMISTIC")
    cs = [
        ("existing: calibration_audit demo", "cal", {
            "system_id": "test_org",
            "friction_events": [
                {"type": "hard_deadline", "was_removed": True, "years_since_removal": 5.0},
                {"type": "peer_review", "was_removed": True, "years_since_removal": 3.0},
                {"type": "performance_review", "was_removed": False, "years_since_removal": 0.0}]},
         "existing"),
    ]
    if cal is not None:
        cs.append(("existing: self_audit OPTIMISTIC (pipeline)", "pipe", SELF_AUDIT["OPTIMISTIC"], "existing"))
        cs.append(("existing: self_audit HONEST (pipeline)", "pipe", SELF_AUDIT["HONEST"], "existing"))
    cs += [
        ("planted: one event with no removal flag (calibration_audit)", "cal", {
            "friction_events": [
                {"type": "a", "was_removed": True, "years_since_removal": 6.0},
                {"type": "b"}]}, "CONSTRUCTED"),
        ("planted: removed event with no years (calibration_audit)", "cal", {
            "friction_events": [
                {"type": "a", "was_removed": True},
                {"type": "b", "was_removed": False}]}, "CONSTRUCTED"),
        ("planted: no flag AND no years on one event (chain)", "cal", {
            "friction_events": [{"type": "a"}, {"type": "b", "was_removed": True,
                                                 "years_since_removal": 2.0}]}, "CONSTRUCTED"),
        ("planted: basic-schema event, no years, through pipeline", "pipe", {
            "system_id": "p", "friction_events": [
                {"type": "a", "was_removed": True},
                {"type": "b", "was_removed": True, "years_since_removal": 4.0}]}, "CONSTRUCTED"),
        ("planted: debt-schema event, no years, through pipeline", "pipe", {
            "system_id": "p", "friction_events": [
                {"name": "a", "domain": "social", "initial_load": 0.8, "removed": True},
                {"name": "b", "domain": "social", "initial_load": 0.8, "removed": True,
                 "years_since_removed": 4.0}]}, "CONSTRUCTED"),
    ]
    return cs


def r6_run(case, mode):
    _, kind, desc, _ = case
    if kind == "cal":
        return json.loads(R6a.run_calibration_audit(desc, fill_r6=mode).to_json())
    return R6p.run_unified_audit(desc, fill_r6=mode)


def r6_verdict(o):
    return o.get("aggregate_band") or o.get("unified_band")


def r6_score(o):
    return o.get("aggregate_score", o.get("unified_score"))


def r6_size(a, c):
    return "score %s -> %s" % (r6_score(c), r6_score(a))


def r6_sweep(case):
    """Fill each missing field with the other end of its range: flag True, years 20."""
    _, kind, desc, _ = case
    ev2 = []
    for e in desc.get("friction_events", []):
        e = dict(e)
        if "was_removed" not in e and "removed" not in e:
            e["was_removed" if kind == "cal" or "initial_load" not in e else "removed"] = True
        rem = e.get("was_removed", e.get("removed"))
        if rem and "years_since_removal" not in e and "years_since_removed" not in e:
            e["years_since_removal" if "initial_load" not in e else "years_since_removed"] = 20.0
        ev2.append(e)
    return r6_run((None, kind, dict(desc, friction_events=ev2), None), "baseline")


# ============================== shared ======================================
FILLS = {
    "R1": dict(cases=r1_cases, run=r1_run, verdict=r1_verdict, size=r1_size,
               hit=lambda c: any("type" not in x for x in c[2])),
    "R2": dict(cases=r2_cases, run=r2_run, verdict=r2_verdict, size=r2_size,
               hit=lambda c: c[1] is not None and c[1] not in R2.CROSS_DOMAIN_CONSTRAINTS),
    "R3": dict(cases=r3_cases, run=r3_run, verdict=r3_verdict, size=r3_size,
               hit=lambda c: any("impact" not in m for m in c[3])),
    "R6": dict(cases=r6_cases, run=r6_run, verdict=r6_verdict, size=r6_size,
               hit=lambda c: r6_hit(c)),
}


def r6_hit(c):
    for e in c[2].get("friction_events", []):
        if "was_removed" not in e and "removed" not in e:
            return True
        if e.get("was_removed", e.get("removed")) and \
                "years_since_removal" not in e and "years_since_removed" not in e:
            return True
    return False


def downstream(path):
    """Every .py that imports the module at `path` (by module name)."""
    name = os.path.splitext(os.path.basename(path))[0]
    hits = []
    for d, _, fs in os.walk(ROOT):
        if ".git" in d:
            continue
        for f in fs:
            p = os.path.join(d, f)
            if not f.endswith(".py") or os.path.abspath(p) in (os.path.join(ROOT, path),
                                                               os.path.abspath(__file__)):
                continue
            with open(p, encoding="utf-8", errors="replace") as fh:
                src = fh.read()
            if re.search(r"^\s*(from|import)\s+[\w.]*\b%s\b" % re.escape(name), src, re.M):
                hits.append(os.path.relpath(p, ROOT))
    return sorted(hits)


def card(fill, name, row, shared, local, numeric, extra_fields):
    slots = {
        "shared_constraint": shared,
        "local_normal_form": local,
        "statistical_artifact": ("ruled_out",
                                 "no random draw on the scored path; one run per arm [DERIVED]"),
        "numerical_artifact": numeric,
        "low_dim_projection": (("supported", "verdict equal, A/C differ on %s [OBSERVED]"
                                % ", ".join(extra_fields[:6]) + (" ..." if len(extra_fields) > 6 else ""))
                               if extra_fields else
                               ("ruled_out", "all compared fields equal A/C [OBSERVED]")),
    }
    st = [s for s, _ in slots.values()]
    if "void" in st:
        slots["none_of_above"] = ("void", "void")
    elif all(x == "ruled_out" for x in st):
        slots["none_of_above"] = ("supported", "every named cause ruled out [DERIVED]")
    else:
        slots["none_of_above"] = ("ruled_out", "a named cause is supported [DERIVED]")
    return {"id": "SF_%s_%s" % (fill, re.sub(r"\W+", "_", name).strip("_")[:48]),
            "observation": "%s void and baseline give the same verdict (%s)" % (fill, row["C"]),
            "trigger": "two readings agreeing: why does the silent fill not matter here?",
            "slots": {k: {"state": s, "evidence": e} for k, (s, e) in slots.items()},
            "reading_declared": "OPEN", "branch": "void", "runs": ["silent_fill_abc"],
            "open_issues": []}


def explain_agreement(fill, case, hit, outs):
    """Shared-constraint / local / numerical slots for an A/C agreement."""
    if not hit:
        return (("supported", "fill not hit: no missing input, the switch is never read "
                 "[OBSERVED]"),
                ("ruled_out", "no fill read, so no edge to be near [DERIVED]"),
                ("ruled_out", "no comparison on the fill path [DERIVED]"))
    if fill == "R1":
        sw = r1_sweep()
        agree = [t for t, g, ok in sw if ok]
        circ = any(x["circular_corruption"] for x in outs["A"]["per_claim"])
        top = max(g for _, g, _ in sw)
        why = ("circular corruption forces HIGH on every claim regardless of grounding "
               "[OBSERVED]") if circ else (
              "a known grade at the top (%.2f) fixes max(); the unknown cannot raise it "
              "[DERIVED: max over grades]" % top)
        local = ("ruled_out", "circular is a boolean override set after the mismatch test; "
                 "agreement does not depend on any distance [DERIVED]") if circ else (
                 "ruled_out", "sweep of the typed citation over all %d grades: A/C agree only at "
                 "%s; agreement comes from max() at the top grade, not from nearness to the "
                 "0.5 mismatch edge [OBSERVED]" % (len(sw), agree or "none"))
        return (("supported", why), local,
                ("ruled_out", "the agreeing branch is not a float comparison [DERIVED]"))
    if fill == "R2":
        return (("supported", "another gate fails, so verdict() leaves VALID_WITHIN_SCOPE "
                 "before cross_domain is decisive [OBSERVED]"),
                ("ruled_out", "gates are booleans; no continuous edge [DERIVED]"),
                ("ruled_out", "no float comparison on the path [DERIVED]"))
    if fill == "R3":
        return (("void", "no agreement expected: void returns None"),
                ("void", "void"), ("void", "void"))
    if fill == "R6":
        return (("void", "not derived for R6 agreements"), ("void", "void"), ("void", "void"))


def run_fill(fill):
    F = FILLS[fill]
    rows, cards = [], []
    for case in F["cases"]():
        outs = {k: F["run"](case, m) for k, m in ARMS}
        hit = F["hit"](case)
        row = {"case": case[0], "provenance": case[-1], "hit": hit}
        for k, _ in ARMS:
            row[k] = F["verdict"](outs[k])
        row["fields_A_vs_C"] = diff(outs["A"], outs["C"])
        row["fields_B_vs_C"] = diff(outs["B"], outs["C"])
        row["B_label"] = (outs["B"].get("fill_" + fill.lower())
                          or outs["B"].get("metadata", {}).get("fill_" + fill.lower())
                          or outs["B"].get("gates", {}).get("cross_domain", {}).get("fill_r2")
                          or {}).get("label") if hit else None
        row["size"] = F["size"](outs["A"], outs["C"]) if hit else "fill not hit"
        if fill == "R3" and hit:
            alt = r3_sweep(case)
            row["other_value"] = "impact=complex gives collapse_risk %s (baseline %s)" % (
                alt["collapse_risk"], outs["C"]["collapse_risk"])
        if fill == "R6" and hit:
            alt = r6_sweep(case)
            row["other_value"] = "flag True / years 20 gives %s %s (baseline %s %s)" % (
                r6_verdict(alt), r6_score(alt), row["C"], r6_score(outs["C"]))
        rows.append(row)
        if row["A"] == row["C"]:
            sh, lo, nu = explain_agreement(fill, case, hit, outs)
            c = card(fill, case[0], row, sh, lo, nu, row["fields_A_vs_C"])
            c["tool_reading"] = read_card({k: v for k, v in c.items() if k != "tool_reading"})
            cards.append(c)
    return rows, cards


def chains():
    out = []
    mods = {f: os.path.splitext(os.path.basename(p))[0] for f, p in FILL_SITES.items()}
    for f, p in FILL_SITES.items():
        down = downstream(p)
        reaches = [g for g, q in FILL_SITES.items() if g != f and q in down]
        out.append({"fill": f, "module": mods[f], "imported_by": down,
                    "feeds_other_fill_module": reaches})
    # within R6: missing flag makes the years fill unreachable on that event
    e = {"friction_events": [{"type": "a"}]}
    sc = R6a.score_friction_removal(e["friction_events"], fill_r6="baseline")
    out.append({"fill": "R6", "within": "calibration_audit.py:202 -> :226",
                "note": "an event with no flag reads preserved, so its years default is never "
                        "read; the second fill is reached only through the first reading True "
                        "[OBSERVED: removed count %s]" % [x for x in sc.evidence if "removed" in x]})
    out.append({"fill": "R6", "within": "pipeline.py:68-72 -> calibration_audit + adaptation_debt",
                "note": "one event missing a field is read by both modules in run_unified_audit; "
                        "both reports and the unified band carry it [OBSERVED in planted pipeline cases]"})
    return out


def run():
    o = {"fills": {}, "chains": chains()}
    for f in FILLS:
        rows, cards = run_fill(f)
        o["fills"][f] = {"rows": rows, "cards": cards}
    return o


def render(o):
    L = []
    w = L.append
    w("SILENT FILLS -- A void / B assumed / C baseline (no winner picked)")
    w("planted cases are CONSTRUCTED; existing cases are module demos / self_audit inputs")
    for f, d in o["fills"].items():
        w("")
        w("== %s  %s" % (f, FILL_SITES[f]))
        for r in d["rows"]:
            w("  [%s] %s  hit=%s" % (r["provenance"], r["case"], r["hit"]))
            w("      A=%s  B=%s  C=%s  B label=%s" % (r["A"], r["B"], r["C"], r["B_label"]))
            w("      size: %s" % r["size"])
            if r.get("other_value"):
                w("      other end: %s" % r["other_value"])
            fa = r["fields_A_vs_C"]
            w("      fields A!=C: %d%s" % (len(fa), (" " + ", ".join(fa[:5]) + (" ..." if len(fa) > 5 else "")) if fa else ""))
            w("      fields B!=C: %d" % len(r["fields_B_vs_C"]))
        w("  coincidence cards (A and C agree): %d" % len(d["cards"]))
        for c in d["cards"]:
            w("    %s  tool=%s" % (c["id"], c["tool_reading"][0]))
            for k, v in c["slots"].items():
                w("      %-21s %-9s %s" % (k, v["state"], v["evidence"][:110]))
    w("")
    w("== chains")
    for c in o["chains"]:
        if "within" in c:
            w("  %s within %s: %s" % (c["fill"], c["within"], c["note"]))
        else:
            w("  %s (%s) imported by %s; feeds another fill module: %s" % (
                c["fill"], c["module"], c["imported_by"] or "none", c["feeds_other_fill_module"] or "no"))
    return "\n".join(L) + "\n"


def selftest():
    n = [0, 0]

    def chk(name, cond):
        n[0] += 1
        if not cond:
            n[1] += 1
            print("FAIL", name)

    o = run()
    for f, d in o["fills"].items():
        for r in d["rows"]:
            chk("%s %s: B verdict equals C" % (f, r["case"]), r["B"] == r["C"])
            chk("%s %s: B differs from C only by label" % (f, r["case"]), not r["fields_B_vs_C"])
            if not r["hit"]:
                chk("%s %s: fill not hit -> A equals C" % (f, r["case"]), not r["fields_A_vs_C"])
        chk("%s: at least one planted case hits the fill" % f, any(r["hit"] for r in d["rows"]))
        chk("%s: no card refused by the tool" % f,
            all(c["tool_reading"][0] != "ERROR" for c in d["cards"]))
    for mod, env in ((R1, "_fill_r1_mode"), (R2, "_fill_r2_mode"), (R3, "_fill_r3_mode")):
        try:
            getattr(mod, env)("bogus")
            chk("%s refuses unknown mode" % env, False)
        except ValueError:
            chk("%s refuses unknown mode" % env, True)
    try:
        R6a.fill_r6_mode("bogus")
        chk("fill_r6_mode refuses unknown mode", False)
    except ValueError:
        chk("fill_r6_mode refuses unknown mode", True)
    r3 = [r for r in o["fills"]["R3"]["rows"] if r["hit"]]
    chk("R3 void sets collapse_risk None on every hit case", all(r["A"] is None for r in r3))
    r6 = [r for r in o["fills"]["R6"]["rows"] if r["hit"]]
    chk("R6 void band UNKNOWN on every hit case", all(r["A"] == "undetermined" for r in r6))
    print("selftest %d/%d" % (n[0] - n[1], n[0]))
    return 1 if n[1] else 0


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    o = run()
    if "--json" in sys.argv:
        print(json.dumps(o, indent=1, default=str))
    else:
        sys.stdout.write(render(o))
