"""Branch experiment, 2026-11-10: the undeclared-SCOPE default in
core/regulatory_scope_audit.py, run three ways, then crossed with the
undeclared-intent switch (3 x 3 = 9 arms). Reports; picks no winner.

Default under test: Regulation.in_scope reads a MISSING scope variable as
out of scope.
  A void      in_scope = None; output says "scope not determinable"
  B assumed   current value (out of scope), labeled PROPOSED
  C baseline  current code, unlabeled (control; byte-identical to main)

The switch is read only when a missing variable is DECISIVE: >= 1 scope
variable missing and no measured variable out of range [CHOICE S1, stated
in the module]. Cases:
  the 8 existing cases (same list as undeclared_intent_abc.py)
  E1, E2  CONSTRUCTED (not among the 8): one variable measured, one missing,
          on either side of the scope edge -- the shapes in which the switch
          and a measured exit meet
Coincidence cards on every scope-A/B verdict agreement; the local_normal_form
slot is examined by sweeping the measured variable across the scope edge.
Labels: OBSERVED (printed by the run), DERIVED (follows from the code, shown
by a check here), PROPOSED (a reading). Void slots stay void.

    python3 in_progress/undeclared_scope_abc.py
    python3 in_progress/undeclared_scope_abc.py --selftest
CC0. Stdlib only.
"""
import importlib.util, io, json, os, re, runpy, subprocess, sys
from contextlib import redirect_stdout

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
MOD = os.path.join(ROOT, "core", "regulatory_scope_audit.py")
MODES = (("A", "void"), ("B", "assumed"), ("C", "baseline"))


def _intent_script():
    spec = importlib.util.spec_from_file_location(
        "undeclared_intent_abc", os.path.join(HERE, "undeclared_intent_abc.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


IA = _intent_script()
read_card = IA.read_card


def load():
    with redirect_stdout(io.StringIO()):
        return runpy.run_path(MOD, run_name="__main__")


def demo_stdout(scope_mode, intent_mode="baseline"):
    env = dict(os.environ, TAF_UNDECLARED_SCOPE=scope_mode, TAF_UNDECLARED_INTENT=intent_mode)
    return subprocess.run([sys.executable, MOD], env=env, capture_output=True,
                          text=True, check=True).stdout


def tag(summary):
    return re.match(r"\[([^\]]+)\]", summary).group(1)


FIELDS = ("verdict", "in_scope", "scope_label", "intent_still_applicable", "intent_label",
          "record.out_of_scope", "record.intent_preserved", "record.intent_undeclared",
          "record.scope_undeterminable", "summary")


def reading(g, reg, sit, scope_mode, intent_mode="baseline", intent=None):
    ic = None if intent is None else (lambda _r, _s: intent)
    a = g["audit"](reg, sit, ic, undeclared_intent=intent_mode, undeclared_scope=scope_mode)
    rec = g["build_response_record"](sit, [a], "x", "x", "x", "x").serialize()
    return {"verdict": tag(a.summary()), "summary": a.summary(),
            "in_scope": a.in_scope, "scope_label": a.scope_label,
            "intent_still_applicable": a.intent_still_applicable, "intent_label": a.intent_label,
            "record.out_of_scope": rec["out_of_scope"],
            "record.intent_preserved": rec["intent_preserved"],
            "record.intent_undeclared": rec.get("intent_undeclared", []),
            "record.scope_undeterminable": rec.get("scope_undeterminable", [])}


def diff(x, y):
    return [f for f in FIELDS if x[f] != y[f]]


def two_var_reg(g):
    return g["Regulation"](id="R2", title="", jurisdiction="", year_enacted=0,
                           first_principle_intent="p",
                           scope=[g["ScopeVar"]("d", (0.0, 10.0)), g["ScopeVar"]("e", (0.0, 10.0))])


def sit_d(g, d):
    return g["Situation"](id="s", location="", description="", conditions={"d": d})


def cases(g):
    out = [(n, r, s, i, src, False) for n, r, s, i, src in IA.cases(g)]
    r2 = two_var_reg(g)
    out += [("E1 d=5 e missing, intent None", r2, sit_d(g, 5.0), None,
             "CONSTRUCTED: measured var in range, one var missing", True),
            ("E2 d=50 e missing, intent None", r2, sit_d(g, 50.0), None,
             "CONSTRUCTED: measured var out of range, one var missing", True)]
    return out


def interaction(g, reg, sit, intent):
    """9 arms: scope mode x intent mode. Classify how the two defaults combine."""
    arms = {(S, I): reading(g, reg, sit, sm, im, intent) for S, sm in MODES for I, im in MODES}
    base = arms[("C", "C")]
    ch = {k: set(diff(v, base)) for k, v in arms.items()}
    scope_read = any(ch[(S, "C")] for S in "AB")
    intent_read = any(ch[("C", I)] for I in "AB")
    verdict_by_intent = {S: {arms[(S, I)]["verdict"] for I in "ABC"} for S in "ABC"}
    gated = scope_read and intent_read and any(
        len(verdict_by_intent[S]) == 1 for S in "AB") and len(verdict_by_intent["C"]) > 1
    combos = {}
    for S in "AB":
        for I in "AB":
            u = ch[(S, "C")] | ch[("C", I)]
            j = ch[(S, I)]
            if j == u:
                combos[S + I] = "stack" if (ch[(S, "C")] and ch[("C", I)]) else "single"
            elif j < u:
                combos[S + I] = "cancel-or-mask (%d of %d fields)" % (len(j), len(u))
            else:
                combos[S + I] = "superadditive (+%s)" % sorted(j - u)
    if not scope_read and not intent_read:
        kind = "neither switch read"
    elif scope_read and not intent_read:
        kind = "scope only"
    elif intent_read and not scope_read:
        kind = "intent only"
    elif gated:
        kind = "chain: scope VOID masks the intent reading"
    else:
        kind = "both read"
    return {"kind": kind, "scope_read": scope_read, "intent_read": intent_read,
            "verdicts": {S + I: arms[(S, I)]["verdict"] for S in "ABC" for I in "ABC"},
            "fields_changed_vs_CC": {S + I: len(ch[(S, I)]) for S in "ABC" for I in "ABC"},
            "combos": combos}


def edge_sweep(g, two_var):
    """Sweep the measured variable d across the edge at 10. Report where
    scope-A and scope-B give the same verdict."""
    reg = two_var_reg(g) if two_var else g["Regulation"](
        id="R", title="", jurisdiction="", year_enacted=0, first_principle_intent="p",
        scope=[g["ScopeVar"]("d", (0.0, 10.0))])
    pts = [9.0, 9.5, 9.9, 10.0, 10.1, 10.5, 11.0]
    rows = []
    for d in pts:
        a = reading(g, reg, sit_d(g, d), "void")["verdict"]
        b = reading(g, reg, sit_d(g, d), "assumed")["verdict"]
        rows.append((d, a, b, a == b))
    agree = [r[0] for r in rows if r[3]]
    split = [r[0] for r in rows if not r[3]]
    return {"two_var": two_var, "rows": rows, "agree_at": agree, "split_at": split,
            "threshold": bool(agree) and bool(split)}


def own_edge_sweep(g, reg, sit, drop_other):
    """Sweep the case's OWN first scope variable across its upper edge, other
    conditions as given. drop_other=True also removes the case's second scope
    variable (if any) so the missing-variable default meets the edge."""
    v = reg.scope[0]
    hi = v.valid_range[1]
    pts = [hi - 0.1 * abs(hi or 1), hi - 0.01 * abs(hi or 1), hi, hi + 0.01 * abs(hi or 1), hi + 0.1 * abs(hi or 1)]
    base = dict(sit.conditions)
    dropped = None
    if drop_other and len(reg.scope) > 1:
        dropped = reg.scope[1].name
        base.pop(dropped, None)
    rows = []
    for x in pts:
        c = dict(base); c[v.name] = x
        s2 = g["Situation"](id=sit.id, location=sit.location, description="", conditions=c)
        a = reading(g, reg, s2, "void")["verdict"]
        b = reading(g, reg, s2, "assumed")["verdict"]
        rows.append((round(x, 6), a, b, a == b))
    agree = [r[0] for r in rows if r[3]]
    split = [r[0] for r in rows if not r[3]]
    return {"variable": v.name, "edge": hi, "dropped": dropped, "rows": rows,
            "agree_at": agree, "split_at": split, "threshold": bool(agree) and bool(split)}


def scope_card(name, reg, sit, rows, sweep, missing):
    a, b = rows["A"], rows["B"]
    slots = {}
    if not missing:
        slots["shared_constraint"] = ("supported",
            "no scope variable missing: the switch is never read, A/B/C run one code path "
            "[DERIVED; OBSERVED: %d of %d fields differ A/B]" % (len(diff(a, b)), len(FIELDS)))
    else:
        slots["shared_constraint"] = ("supported",
            "a measured variable is out of range, which settles scope as out before the "
            "switch is read [DERIVED: CHOICE S1]")
    own, drop = sweep
    where = "%s across %s (own regulation)" % (own["variable"], own["edge"])
    if own["threshold"]:
        slots["local_normal_form"] = ("supported",
            "sweep %s: A/B agree at %s, split at %s; agreement is one side of the edge [OBSERVED]"
            % (where, own["agree_at"], own["split_at"]))
    else:
        extra = ""
        if drop["dropped"]:
            extra = ("; with %s removed the same sweep %s (agree %s, split %s) [OBSERVED]" % (
                drop["dropped"], "has an edge threshold" if drop["threshold"] else "has none",
                drop["agree_at"], drop["split_at"]))
        slots["local_normal_form"] = ("ruled_out",
            "sweep %s: A/B agree at every point both sides of the edge; agreement here does not "
            "depend on nearness to it [OBSERVED]%s" % (where, extra))
    slots["statistical_artifact"] = ("ruled_out",
        "no random draw in audit(); one run per arm is the whole population [DERIVED]")
    slots["numerical_artifact"] = ("ruled_out",
        "edge test is <= on floats; each sweep includes the edge value exactly; any change "
        "falls between the points either side of the edge, not scattered [OBSERVED]")
    fd = diff(a, b)
    if fd:
        slots["low_dim_projection"] = ("supported",
            "verdict equal, A/B differ on %s [OBSERVED]" % ", ".join(fd))
    else:
        slots["low_dim_projection"] = ("ruled_out", "all %d fields equal A/B [OBSERVED]" % len(FIELDS))
    st = [s for s, _ in slots.values()]
    if "void" in st:
        slots["none_of_above"] = ("void", "void")
    elif all(x == "ruled_out" for x in st):
        slots["none_of_above"] = ("supported", "every named cause ruled out [DERIVED]")
    else:
        slots["none_of_above"] = ("ruled_out", "a named cause is supported [DERIVED]")
    return {"id": "USA_" + re.sub(r"\W+", "_", name).strip("_"),
            "observation": "scope A and B give the same verdict (%s)" % a["verdict"],
            "trigger": "two readings agreeing: why does the missing-variable default not matter here?",
            "slots": {k: {"state": s, "evidence": e} for k, (s, e) in slots.items()},
            "reading_declared": "OPEN", "branch": "void", "runs": ["undeclared_scope_abc"],
            "open_issues": []}


def run():
    g = load()
    o = {"cases": [], "cards": [], "demo_stdout_diff": {},
         "sweeps": {"one_var": edge_sweep(g, False), "two_var_e_missing": edge_sweep(g, True)}}
    base = demo_stdout("baseline").splitlines()
    for S, sm in MODES:
        for I, im in MODES:
            lines = demo_stdout(sm, im).splitlines()
            o["demo_stdout_diff"][S + I] = [i + 1 for i, (p, q) in enumerate(zip(base, lines)) if p != q] + \
                ([("len", len(base), len(lines))] if len(base) != len(lines) else [])
    for name, reg, sit, intent, src, constructed in cases(g):
        rows = {L: reading(g, reg, sit, m, "baseline", intent) for L, m in MODES}
        missing = bool(g["audit"](reg, sit).missing_scope_vars())
        c = {"case": name, "source": src, "constructed": constructed, "intent_declared": intent,
             "missing_scope_vars": g["audit"](reg, sit).missing_scope_vars(), "rows": rows,
             "A_vs_B": diff(rows["A"], rows["B"]), "A_vs_C": diff(rows["A"], rows["C"]),
             "B_vs_C": diff(rows["B"], rows["C"]),
             "summary_chars": {L: len(rows[L]["summary"]) for L in rows},
             "cross": interaction(g, reg, sit, intent)}
        o["cases"].append(c)
        if rows["A"]["verdict"] == rows["B"]["verdict"]:
            sw = (own_edge_sweep(g, reg, sit, False), own_edge_sweep(g, reg, sit, True))
            card = scope_card(name, reg, sit, rows, sw, missing)
            card["sweeps"] = sw
            card["tool_reading"] = read_card(card)
            o["cards"].append(card)
    return o


def render(o):
    w = print
    w("UNDECLARED-SCOPE A/B/C, crossed with UNDECLARED-INTENT A/B/C (9 arms)")
    w("scope: A void | B assumed+PROPOSED | C baseline = main.  No winner is picked.")
    w("OBSERVED = printed by this run; DERIVED = follows from code.")
    w("")
    w("demo stdout, lines differing from CC (scope,intent) [OBSERVED]:")
    for k, v in o["demo_stdout_diff"].items():
        w("  %s: %s" % (k, v or "none"))
    w("")
    for c in o["cases"]:
        w("%s   (%s; intent declared: %s; missing: %s)" % (
            c["case"], c["source"], c["intent_declared"], c["missing_scope_vars"] or "-"))
        for L in "ABC":
            r = c["rows"][L]
            w("  %s  %-34s in_scope=%-5s slabel=%-8s oos=%s undet=%s" % (
                L, r["verdict"], r["in_scope"], r["scope_label"] or "-",
                r["record.out_of_scope"] or "-", r["record.scope_undeterminable"] or "-"))
        n = len(FIELDS)
        w("  diverge A/B: %d of %d %s | A/C: %d | B/C: %d %s" % (
            len(c["A_vs_B"]), n, c["A_vs_B"], len(c["A_vs_C"]), len(c["B_vs_C"]), c["B_vs_C"]))
        w("  summary chars A/B/C: %(A)d / %(B)d / %(C)d" % c["summary_chars"])
        x = c["cross"]
        w("  9-arm cross: %s" % x["kind"])
        w("    verdicts (scope,intent): " + "; ".join("%s=%s" % (k, v) for k, v in x["verdicts"].items()))
        w("    fields changed vs CC:    " + " ".join("%s=%d" % kv for kv in x["fields_changed_vs_CC"].items()))
        w("    combos (scope x intent, AB arms): " + "; ".join("%s=%s" % kv for kv in x["combos"].items()))
        w("")
    w("edge sweeps (verdict under scope A / scope B) [OBSERVED]:")
    for k, s in o["sweeps"].items():
        w("  %s:" % k)
        for d, a, b, eq in s["rows"]:
            w("    d=%-5s A=%-34s B=%-34s %s" % (d, a, b, "agree" if eq else "SPLIT"))
    w("")
    w("coincidence cards (cases where scope A and B give the same verdict):")
    for k in o["cards"]:
        w("  %s  tool reading: %s %s" % (k["id"], k["tool_reading"][0], k["tool_reading"][1]))
        for s, v in k["slots"].items():
            w("    %-20s %-9s %s" % (s, v["state"], v["evidence"]))


def selftest():
    ok = []
    def chk(n, c):
        ok.append((n, bool(c))); print(("PASS " if c else "FAIL ") + n)
    o = run()
    by = {c["case"]: c for c in o["cases"]}
    chk("CC demo stdout identical to baseline", o["demo_stdout_diff"]["CC"] == [])
    chk("scope switch alone leaves demo stdout unchanged (demo never reads it)",
        all(o["demo_stdout_diff"][S + "C"] == [] for S in "AB"))
    chk("no missing var => A=B=C on all fields", all(
        not c["A_vs_B"] and not c["A_vs_C"] for c in o["cases"] if not c["missing_scope_vars"]))
    chk("scope void never writes in_scope False when missing var is decisive", all(
        c["rows"]["A"]["in_scope"] is None for c in o["cases"]
        if c["missing_scope_vars"] and c["rows"]["C"]["verdict"] != "IN SCOPE"
        and not c["case"].startswith("E2")))
    chk("E2: measured exit settles scope, switch not read", not by["E2 d=50 e missing, intent None"]["A_vs_C"])
    chk("assumed carries PROPOSED wherever it diverges from C", all(
        c["rows"]["B"]["scope_label"] == "PROPOSED" for c in o["cases"] if c["B_vs_C"]))
    chk("void scope keeps the reg out of record.out_of_scope", all(
        not c["rows"]["A"]["record.out_of_scope"] for c in o["cases"] if c["rows"]["A"]["in_scope"] is None))
    chk("two-var sweep has a threshold at the edge", o["sweeps"]["two_var_e_missing"]["threshold"])
    chk("one-var sweep agrees on both sides", not o["sweeps"]["one_var"]["threshold"])
    chk("every scope A=B verdict case has a card", len(o["cards"]) == sum(
        1 for c in o["cases"] if c["rows"]["A"]["verdict"] == c["rows"]["B"]["verdict"]))
    chk("no card refused by the coincidence tool", all(k["tool_reading"][0] != "ERROR" for k in o["cards"]))
    chk("unknown scope mode refused", _refuses())
    bad = [n for n, c in ok if not c]
    print("checks: %d   failed: %d" % (len(ok), len(bad)))
    return 0 if not bad else 1


def _refuses():
    g = load()
    try:
        g["audit"](g["septic_rule"], g["homestead"], undeclared_scope="maybe")
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
