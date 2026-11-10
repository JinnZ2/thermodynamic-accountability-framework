"""Branch experiment, 2026-11-10: the undeclared-intent case in
core/regulatory_scope_audit.py, run three ways. Reports; picks no winner.

  A void      intent_still_applicable = None; dependent outputs flagged
  B assumed   True, labeled PROPOSED on every output it reaches
  C baseline  current code, unlabeled (control; byte-identical to main)

The switch is consulted only when intent_check is None. Cases:
  demo   the module's own __main__ demo, run with runpy (its objects, not copies)
  cross  the demo's two regulations x two situations (audit_many)
  card   the four shapes the Simulators law-audit-card tests feed TAF

For every case where A and B agree on the verdict, a coincidence card is
filled (six slots, the forest-model-ledger format) and, when that tool is
reachable (FOREST_LEDGER=<path to forest-model-ledger>), read by it in a
subprocess. Labels: OBSERVED (printed by the run), DERIVED (follows from the
code, shown by a check here), PROPOSED (a reading). Void slots stay void.

    python3 in_progress/undeclared_intent_abc.py
    python3 in_progress/undeclared_intent_abc.py --selftest
CC0. Stdlib only.
"""
import io, json, os, re, runpy, subprocess, sys
from contextlib import redirect_stdout

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
MOD = os.path.join(ROOT, "core", "regulatory_scope_audit.py")
MODES = (("A", "void"), ("B", "assumed"), ("C", "baseline"))


def load():
    with redirect_stdout(io.StringIO()):
        g = runpy.run_path(MOD, run_name="__main__")
    return g


def demo_stdout(mode):
    env = dict(os.environ, TAF_UNDECLARED_INTENT=mode)
    return subprocess.run([sys.executable, MOD], env=env, capture_output=True,
                          text=True, check=True).stdout


def tag(summary):
    return re.match(r"\[([^\]]+)\]", summary).group(1)


def reading(g, reg, sit, mode, intent=None):
    ic = None if intent is None else (lambda _r, _s: intent)
    a = g["audit"](reg, sit, ic, undeclared_intent=mode)
    rec = g["build_response_record"](sit, [a], "x", "x", "x", "x").serialize()
    return {"verdict": tag(a.summary()), "summary": a.summary(),
            "intent_still_applicable": a.intent_still_applicable,
            "intent_label": a.intent_label,
            "record.intent_preserved": rec["intent_preserved"],
            "record.intent_undeclared": rec.get("intent_undeclared", [])}


def cases(g):
    R, S, V = g["Regulation"], g["Situation"], g["ScopeVar"]
    card_reg = R(id="R", title="", jurisdiction="", year_enacted=0,
                 first_principle_intent="p", scope=[V("d", (0.0, 10.0))])
    def cs(d):
        return S(id="s", location="", description="", conditions={"d": d})
    sep, br, hs, fb = g["septic_rule"], g["bridge_permit_rule"], g["homestead"], g["footbridge"]
    return [
        ("demo-1 septic x homestead", sep, hs, None, "demo a1"),
        ("demo-2 bridge x footbridge", br, fb, None, "demo a2"),
        ("cross-1 septic x footbridge", sep, fb, None, "audit_many cross"),
        ("cross-2 bridge x homestead", br, hs, None, "audit_many cross"),
        ("card-1 d=5 intent None", card_reg, cs(5.0), None, "law-audit-card test_derive"),
        ("card-2 d=50 intent False", card_reg, cs(50.0), False, "law-audit-card test_derive"),
        ("card-3 d=50 intent True", card_reg, cs(50.0), True, "law-audit-card test_derive"),
        ("card-4 d=50 intent None", card_reg, cs(50.0), None,
         "law-audit-card test_undeclared (card.py returns VOID before calling TAF)"),
    ]


OUT_FIELDS = ("verdict", "intent_still_applicable", "intent_label",
              "record.intent_preserved", "record.intent_undeclared", "summary")


def diff(x, y):
    return [f for f in OUT_FIELDS if x[f] != y[f]]


def removal_test(g, reg, sit):
    """Flip a DECLARED intent True/False: does the verdict move? If not, the
    intent slot does not reach this verdict at all."""
    t = reading(g, reg, sit, "baseline", True)["verdict"]
    f = reading(g, reg, sit, "baseline", False)["verdict"]
    return t, f


def coincidence_card(name, reg, sit, intent, rows, flip):
    a, b = rows["A"], rows["B"]
    fields_differ = diff(a, b)
    intent_reaches = flip[0] != flip[1]
    slots = {}
    if intent is not None:
        slots["shared_constraint"] = ("supported",
            "intent declared (%r): audit() returns before the switch is read, so A, B, C "
            "read one value [DERIVED: same code path; all 6 fields equal]" % intent)
    elif not intent_reaches:
        slots["shared_constraint"] = ("supported",
            "summary() tests in_scope before intent; flipping a declared intent True/False "
            "gives %s / %s [OBSERVED]" % flip)
    else:
        slots["shared_constraint"] = ("ruled_out", "flip moves the verdict: %s / %s [OBSERVED]" % flip)
    slots["local_normal_form"] = ("void", "void")
    slots["statistical_artifact"] = ("ruled_out",
        "no random draw anywhere in audit(); one run per mode is the whole population [DERIVED]")
    slots["numerical_artifact"] = ("ruled_out",
        "the intent slot is a bool/None; no float enters the comparison [DERIVED]")
    if fields_differ:
        slots["low_dim_projection"] = ("supported",
            "verdict tag equal, but A and B differ on %s [OBSERVED]" % ", ".join(fields_differ))
    else:
        slots["low_dim_projection"] = ("ruled_out", "all 6 output fields equal under A and B [OBSERVED]")
    # forest rule: none_of_above is derived -- void while any cause slot is void
    st = [s for s, _ in slots.values()]
    if "void" in st:
        slots["none_of_above"] = ("void", "void")
    elif all(x == "ruled_out" for x in st):
        slots["none_of_above"] = ("supported", "every named cause ruled out [DERIVED]")
    else:
        slots["none_of_above"] = ("ruled_out", "a named cause is supported [DERIVED]")
    return {"id": "UIA_" + re.sub(r"\W+", "_", name).strip("_"),
            "observation": "A and B give the same verdict (%s)" % a["verdict"],
            "trigger": "two readings agreeing: why does intent not matter here?",
            "slots": {k: {"state": s, "evidence": e} for k, (s, e) in slots.items()},
            "reading_declared": "OPEN",
            "branch": "void", "runs": ["undeclared_intent_abc"],
            "open_issues": ["local_normal_form not looked at: no threshold sweep near the scope edge"]}


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


def downstream():
    """Every .py in the repo that imports this module, other than itself."""
    hits = []
    for d, _, fs in os.walk(ROOT):
        if ".git" in d:
            continue
        for f in fs:
            p = os.path.join(d, f)
            if not f.endswith(".py") or p in (MOD, os.path.abspath(__file__)):
                continue
            with open(p, encoding="utf-8", errors="replace") as fh:
                src = fh.read()
            if re.search(r"^\s*(from|import)\s+[\w.]*regulatory_scope_audit", src, re.M):
                hits.append(os.path.relpath(p, ROOT))
    return sorted(hits)


def run():
    g = load()
    out = {"cases": [], "cards": [], "demo_stdout_diff": {}, "downstream_importers": downstream()}
    base = demo_stdout("baseline").splitlines()
    for letter, m in MODES:
        lines = demo_stdout(m).splitlines()
        out["demo_stdout_diff"][letter] = [i + 1 for i, (p, q) in enumerate(zip(base, lines)) if p != q] + \
            ([("len", len(base), len(lines))] if len(base) != len(lines) else [])
    for name, reg, sit, intent, src in cases(g):
        rows = {L: reading(g, reg, sit, m, intent) for L, m in MODES}
        flip = removal_test(g, reg, sit)
        c = {"case": name, "source": src, "intent_declared": intent, "rows": rows,
             "A_vs_B": diff(rows["A"], rows["B"]), "A_vs_C": diff(rows["A"], rows["C"]),
             "B_vs_C": diff(rows["B"], rows["C"]),
             "summary_chars": {L: len(rows[L]["summary"]) for L in rows},
             "removal_test_verdict_true_false": flip}
        out["cases"].append(c)
        if rows["A"]["verdict"] == rows["B"]["verdict"]:
            card = coincidence_card(name, reg, sit, intent, rows, flip)
            card["tool_reading"] = read_card({k: v for k, v in card.items() if k != "tool_reading"})
            out["cards"].append(card)
    return out


def render(o):
    w = print
    w("UNDECLARED-INTENT A/B/C  (A void | B assumed+PROPOSED | C baseline = main)")
    w("No winner is picked. OBSERVED = printed by this run; DERIVED = follows from code.")
    w("")
    w("demo stdout, lines differing from C [OBSERVED]:")
    for L in "ABC":
        w("  %s: %s" % (L, o["demo_stdout_diff"][L] or "none"))
    w("")
    for c in o["cases"]:
        w("%s   (%s; intent declared: %s)" % (c["case"], c["source"], c["intent_declared"]))
        for L in "ABC":
            r = c["rows"][L]
            w("  %s  %-34s intent=%-5s label=%-8s preserved=%d undeclared=%s" % (
                L, r["verdict"], r["intent_still_applicable"], r["intent_label"] or "-",
                len(r["record.intent_preserved"]), r["record.intent_undeclared"] or "-"))
        n = len(OUT_FIELDS)
        w("  diverge A/B: %d of %d %s | A/C: %d %s | B/C: %d %s" % (
            len(c["A_vs_B"]), n, c["A_vs_B"], len(c["A_vs_C"]), c["A_vs_C"], len(c["B_vs_C"]), c["B_vs_C"]))
        w("  summary chars A/B/C: %(A)d / %(B)d / %(C)d" % c["summary_chars"])
        w("  removal test (declared True / False): %s / %s [OBSERVED]" % tuple(c["removal_test_verdict_true_false"]))
        w("")
    w("coincidence cards (cases where A and B give the same verdict):")
    for k in o["cards"]:
        w("  %s  tool reading: %s %s" % (k["id"], k["tool_reading"][0], k["tool_reading"][1]))
        for s, v in k["slots"].items():
            w("    %-20s %-9s %s" % (s, v["state"], v["evidence"]))
    w("")
    imp = o["downstream_importers"]
    w("downstream .py importing core/regulatory_scope_audit.py [OBSERVED]: %s" % (imp or "none"))
    w("  so TAF's test suites cannot move under the switch; the module's own demo and")
    w("  external callers (Simulators law-audit-card/card.py, via TAF_PATH) are the cases. [DERIVED]")


def selftest():
    ok = []
    def chk(n, c):
        ok.append((n, bool(c))); print(("PASS " if c else "FAIL ") + n)
    o = run()
    by = {c["case"]: c for c in o["cases"]}
    chk("C demo stdout identical to baseline", o["demo_stdout_diff"]["C"] == [])
    chk("A and B demo stdout differ from C", o["demo_stdout_diff"]["A"] and o["demo_stdout_diff"]["B"])
    chk("declared intent: A=B=C on all fields", all(
        not by[n]["A_vs_B"] and not by[n]["A_vs_C"] for n in by if by[n]["intent_declared"] is not None))
    chk("void never writes True", all(c["rows"]["A"]["intent_still_applicable"] is not True
                                       for c in o["cases"] if c["intent_declared"] is None))
    chk("assumed carries PROPOSED wherever it diverges from C", all(
        c["rows"]["B"]["intent_label"] == "PROPOSED" for c in o["cases"] if c["B_vs_C"]))
    chk("out-of-scope undeclared: A verdict is INTENT UNDECLARED", all(
        c["rows"]["A"]["verdict"] == "OUT OF SCOPE -- INTENT UNDECLARED" for c in o["cases"]
        if c["intent_declared"] is None and c["rows"]["C"]["verdict"] != "IN SCOPE"))
    chk("every A=B verdict case has a card", len(o["cards"]) == sum(
        1 for c in o["cases"] if c["rows"]["A"]["verdict"] == c["rows"]["B"]["verdict"]))
    chk("no card refused by the coincidence tool", all(k["tool_reading"][0] != "ERROR" for k in o["cards"]))
    chk("unknown mode refused", _refuses())
    bad = [n for n, c in ok if not c]
    print("checks: %d   failed: %d" % (len(ok), len(bad)))
    return 0 if not bad else 1


def _refuses():
    g = load()
    try:
        g["audit"](g["septic_rule"], g["homestead"], undeclared_intent="maybe")
    except ValueError:
        return True
    return False


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    if "--json" in sys.argv:
        print(json.dumps(run(), indent=1, default=str))
    else:
        render(run())
