#!/usr/bin/env python3
# validate.py -- CC0, stdlib only (json, re, sys, os, copy). Runs on python >= 3.5.
# Status: co-authored (Kavik + Claude), 2026-11-03.
#
# Gate for assembly-instrument entries. Reads an entry, checks its
# shape against schema.json, then the junction rules. Prints
# PASS/FAIL per branch with the failing field. Exit nonzero on any
# failure, so it can gate a commit.
#
#   entry.json ──> structure (schema.json subset) ──┐
#                                                   ├──> per-branch verdict
#   each branch ──> RULES R1..R5 (work order) ──────┤      PASS / FAIL field: reason
#                ──> C1..C4 (consistency) ──────────┘
#   entry ──────> safety_scope flags recomputed, compared
#
#   R1 junction with no provenance tag
#   R2 branch with no scope_stamp, or missing date OR environment
#   R3 irreversible: true with empty or jargon-only hazard line
#   R4 chain_length above threshold without matching verification_required
#   R5 branch tagged TESTED anywhere with source: null
#   R6 (with --ledger) irreversible junction whose field status is CAUTION
#      but the entry carries no plain-language `caution` line for it
#   C1 chain_length != number of junctions
#   C2 verification_required level != rule (at any length)
#   C3 entry safety flags (irreversibility, compounding_error,
#      reader_state) disagree with what the branches imply
#   C4 structure: required field missing / wrong type / bad enum
#
# Exit: 0 all pass | 1 any failure | 2 usage / unreadable input
#
#   python3 validate.py seeds/lighting.json seeds/shelter_envelope.json
#   python3 validate.py --selftest

import copy
import json
import os
import re
import sys

from refs import junction_ref

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_SCHEMA = os.path.join(HERE, "schema.json")

PROVENANCE = ("TESTED", "DOCUMENTED", "INFERRED_BY_ASSEMBLY")
LEVELS = ("SINGLE_BUILD_CHECK", "TEST_EACH_JUNCTION", "TEST_EACH_JUNCTION_THEN_FULL_TRIAL")

# Words a reader without training may not know. A hazard line that is
# mostly these, or has too few other words, is not legible.
JARGON = set("""
co co2 monoxide ppm ppb lel uel mpa kpa psi asphyxiant asphyxiation hypoxia
hypoxic anoxia anoxic toxicity exothermic endothermic caustic alkaline alkali
ph pyrolysis pyrolytic volatile volatiles voc vocs sds msds ppe osha niosh
ansi iso astm ventilate ventilation mitigate mitigation exposure threshold
tlv idlh stel protocol compliance hazmat carboxyhemoglobin flashpoint
autoignition combustion combustible particulate particulates respirable
silicosis dermal ocular contraindicated slaking calcination hydration
deflagration overpressure ignition egress lockout tagout
""".split())
MIN_PLAIN_WORDS = 8
MAX_JARGON_SHARE = 0.25


def load_rules(schema):
    r = schema.get("x-rules", {})
    return {"threshold": int(r.get("verification_threshold", 3))}


# ---------------------------------------------------------------
# structure: a small subset of JSON Schema draft-07
#   type, required, properties, items, enum, minLength, minItems,
#   minimum, $ref (#/definitions/...)
# ---------------------------------------------------------------
_TYPES = {
    "object": dict, "array": list, "string": str, "boolean": bool,
    "null": type(None),
}


def _is_type(v, t):
    if t == "integer":
        return isinstance(v, int) and not isinstance(v, bool)
    if t == "number":
        return isinstance(v, (int, float)) and not isinstance(v, bool)
    return isinstance(v, _TYPES[t])


def check_structure(node, sch, root, path, errs):
    if "$ref" in sch:
        ref = sch["$ref"]
        target = root
        for part in ref.lstrip("#/").split("/"):
            target = target[part]
        return check_structure(node, target, root, path, errs)
    t = sch.get("type")
    if t is not None:
        ts = t if isinstance(t, list) else [t]
        if not any(_is_type(node, x) for x in ts):
            errs.append((path, "C4 type: expected %s" % "/".join(ts)))
            return
    if "enum" in sch and node not in sch["enum"]:
        errs.append((path, "C4 enum: %r not in %s" % (node, sch["enum"])))
    if isinstance(node, str) and len(node) < sch.get("minLength", 0):
        errs.append((path, "C4 minLength %d" % sch["minLength"]))
    if isinstance(node, int) and not isinstance(node, bool) and "minimum" in sch and node < sch["minimum"]:
        errs.append((path, "C4 minimum %s" % sch["minimum"]))
    if isinstance(node, dict):
        for k in sch.get("required", []):
            if k not in node:
                errs.append((path + "." + k, "C4 required field missing"))
        for k, sub in sch.get("properties", {}).items():
            if k in node:
                check_structure(node[k], sub, root, path + "." + k, errs)
    if isinstance(node, list):
        if len(node) < sch.get("minItems", 0):
            errs.append((path, "C4 minItems %d" % sch["minItems"]))
        if "items" in sch:
            for i, it in enumerate(node):
                check_structure(it, sch["items"], root, "%s[%d]" % (path, i), errs)


# ---------------------------------------------------------------
# rules
# ---------------------------------------------------------------
def legible(hazard):
    """(ok, reason). Plain-language check for an irreversible hazard."""
    if hazard is None or not str(hazard).strip():
        return False, "empty"
    words = [w.lower() for w in re.findall(r"[A-Za-z][A-Za-z']*", hazard)]
    if not words:
        return False, "no words"
    jar = [w for w in words if w in JARGON]
    plain = len(words) - len(jar)
    if plain < MIN_PLAIN_WORDS:
        return False, "jargon-only or too short (%d plain words < %d)" % (plain, MIN_PLAIN_WORDS)
    if float(len(jar)) / len(words) > MAX_JARGON_SHARE:
        return False, "jargon share %.0f%% > %.0f%% (%s)" % (
            100.0 * len(jar) / len(words), 100 * MAX_JARGON_SHARE, ", ".join(sorted(set(jar))))
    return True, ""


def required_level(chain_length, any_irreversible, threshold):
    if chain_length > threshold:
        lvl = 2
    elif chain_length >= 2:
        lvl = 1
    else:
        lvl = 0
    if any_irreversible:
        lvl = max(lvl, 1)
    return LEVELS[lvl]


def check_branch(b, threshold):
    """List of (field, reason) failures for one branch."""
    fails = []
    js = b.get("junctions") if isinstance(b.get("junctions"), list) else []
    # R1
    for i, j in enumerate(js):
        jid = j.get("id", str(i)) if isinstance(j, dict) else str(i)
        if not isinstance(j, dict) or j.get("provenance") not in PROVENANCE:
            fails.append(("junctions[%s].provenance" % jid, "R1 no provenance tag"))
    # R2
    st = b.get("scope_stamp")
    if not isinstance(st, dict):
        fails.append(("scope_stamp", "R2 missing scope_stamp"))
    else:
        if not str(st.get("date") or "").strip():
            fails.append(("scope_stamp.date", "R2 date required"))
        env = st.get("environment")
        if not isinstance(env, dict) or not any(str(v).strip() for v in env.values()):
            fails.append(("scope_stamp.environment", "R2 environment required"))
    # R3
    any_irrev = False
    for i, j in enumerate(js):
        if isinstance(j, dict) and j.get("irreversible") is True:
            any_irrev = True
            ok, why = legible(j.get("hazard"))
            if not ok:
                fails.append(("junctions[%s].hazard" % j.get("id", i), "R3 irreversible with hazard " + why))
    # C1
    cl = b.get("chain_length")
    if cl != len(js):
        fails.append(("chain_length", "C1 chain_length %r != %d junctions" % (cl, len(js))))
    # R4 / C2
    n = len(js)
    need = required_level(n, any_irrev, threshold)
    vr = b.get("verification_required") if isinstance(b.get("verification_required"), dict) else {}
    have = vr.get("level")
    if have != need:
        code = "R4 chain_length %d above threshold %d" % (n, threshold) if n > threshold else "C2 rule"
        fails.append(("verification_required.level", "%s: requires %s, has %r" % (code, need, have)))
    # R5
    for i, j in enumerate(js):
        if isinstance(j, dict) and j.get("provenance") == "TESTED" and j.get("source") is None:
            fails.append(("junctions[%s].source" % j.get("id", i), "R5 TESTED with source null"))
    for k, q in enumerate((b.get("output") or {}).get("quantities") or []):
        if isinstance(q, dict) and q.get("provenance") == "TESTED" and not q.get("source"):
            fails.append(("output.quantities[%d].source" % k, "R5 TESTED with source null"))
    return fails


def implied_flags(entry, threshold):
    irrev = compound = False
    legible_all = True
    for b in entry.get("branches") or []:
        js = [j for j in (b.get("junctions") or []) if isinstance(j, dict)]
        run = 0
        if len(js) > threshold:
            compound = True
        for j in js:
            run = run + 1 if j.get("provenance") == "INFERRED_BY_ASSEMBLY" else 0
            if run >= 2:
                compound = True
            if j.get("irreversible") is True:
                irrev = True
                if not legible(j.get("hazard"))[0]:
                    legible_all = False
    return {"irreversibility": irrev, "compounding_error": compound, "reader_state": legible_all}


def validate_entry(entry, schema, cautions=None):
    """-> (entry_fails, {branch_name: [fails]})"""
    threshold = load_rules(schema)["threshold"]
    serrs = []
    check_structure(entry, schema, schema, "entry", serrs)
    per_branch = {}
    entry_fails = []
    for path, why in serrs:
        m = re.match(r"entry\.branches\[(\d+)\]", path)
        if m:
            per_branch.setdefault(int(m.group(1)), []).append((path, why))
        else:
            entry_fails.append((path, why))
    results = {}
    for i, b in enumerate(entry.get("branches") or []):
        name = b.get("name", "branch[%d]" % i) if isinstance(b, dict) else "branch[%d]" % i
        fails = list(per_branch.get(i, []))
        if isinstance(b, dict):
            fails += check_branch(b, threshold)
            for j in b.get("junctions") or []:
                if not (isinstance(j, dict) and j.get("irreversible") is True and cautions):
                    continue
                ref = junction_ref(entry, i, j)
                if ref in cautions and not legible(j.get("caution"))[0]:
                    fails.append(("junctions[%s].caution" % j.get("id"),
                                  "R6 field status CAUTION on irreversible step %s; entry must carry a "
                                  "plain caution line (%s)" % (ref, "; ".join(cautions[ref])[:120])))
        results[name] = fails
    ss = entry.get("safety_scope")
    if isinstance(ss, dict):
        for k, v in implied_flags(entry, threshold).items():
            if ss.get(k) is not v:
                entry_fails.append(("safety_scope." + k, "C3 declared %r, branches imply %r" % (ss.get(k), v)))
    return entry_fails, results


def report(path, entry_fails, results, out=sys.stdout):
    bad = bool(entry_fails)
    out.write("== %s\n" % path)
    for f, why in entry_fails:
        out.write("  FAIL entry  %s: %s\n" % (f, why))
    for name, fails in results.items():
        if fails:
            bad = True
            for f, why in fails:
                out.write("  FAIL %s  %s: %s\n" % (name, f, why))
        else:
            out.write("  PASS %s\n" % name)
    return bad


# ---------------------------------------------------------------
# selftest: plant one defect per rule into a passing copy
# ---------------------------------------------------------------
GOOD_HAZARD = ("Burning anything indoors makes a gas you cannot see or smell that can "
               "kill people while they sleep. Keep outside air coming in and put the "
               "flame out before anyone sleeps.")


def _good_entry():
    env = {"climate": "temperate", "soil": "n/a", "water_chemistry": "n/a", "altitude": "n/a"}
    return {
        "schema_version": "0.1.0", "status": "co-authored", "function_id": "T",
        "function": "test function",
        "safety_scope": {"results_return": "report back", "irreversibility": True,
                         "compounding_error": False, "local_validity": env, "reader_state": True},
        "branches": [{
            "name": "b1",
            "inputs": {"materials": ["x"], "tools": [], "skills": []},
            "climate_window": {"works": "w", "fails": "f"},
            "output": {"delivers": "d", "quantities": []},
            "junctions": [
                {"id": "J1", "step": "s1", "provenance": "DOCUMENTED", "source": "src",
                 "irreversible": False, "hazard": None},
                {"id": "J2", "step": "s2", "provenance": "INFERRED_BY_ASSEMBLY", "source": None,
                 "irreversible": True, "hazard": GOOD_HAZARD},
            ],
            "scope_stamp": {"date": "2026-11-03", "environment": env, "conditions": "c"},
            "chain_length": 2,
            "verification_required": {"level": "TEST_EACH_JUNCTION", "reason": "r"},
        }],
    }


def selftest(schema):
    checks = []

    def run(label, mutate, expect_code):
        e = _good_entry()
        if mutate:
            mutate(e)
        ef, res = validate_entry(e, schema)
        msgs = [w for _, w in ef] + [w for fs in res.values() for _, w in fs]
        if expect_code is None:
            ok = not msgs
        else:
            ok = any(m.startswith(expect_code) for m in msgs)
        checks.append((label, ok, msgs))

    b = lambda e: e["branches"][0]
    run("clean entry passes", None, None)
    run("R1 junction without provenance", lambda e: b(e)["junctions"][0].pop("provenance"), "R1")
    run("R1 junction with bogus provenance", lambda e: b(e)["junctions"][0].update(provenance="LIKELY"), "R1")
    run("R2 no scope_stamp", lambda e: b(e).pop("scope_stamp"), "R2")
    run("R2 no date", lambda e: b(e)["scope_stamp"].update(date=""), "R2")
    run("R2 no environment", lambda e: b(e)["scope_stamp"].pop("environment"), "R2")
    run("R3 irreversible, empty hazard", lambda e: b(e)["junctions"][1].update(hazard=""), "R3")
    run("R3 irreversible, null hazard", lambda e: b(e)["junctions"][1].update(hazard=None), "R3")
    run("R3 irreversible, jargon-only hazard",
        lambda e: b(e)["junctions"][1].update(hazard="CO asphyxiation hazard; ventilate per code."), "R3")
    run("R3 jargon-heavy hazard",
        lambda e: b(e)["junctions"][1].update(
            hazard="Combustion exposure CO monoxide asphyxiation hypoxia: ventilate, mitigate, avoid in small rooms ok"), "R3")

    def long_chain(e):
        js = b(e)["junctions"]
        for k in range(3, 6):
            js.append({"id": "J%d" % k, "step": "s", "provenance": "DOCUMENTED", "source": "x",
                       "irreversible": False, "hazard": None})
        b(e)["chain_length"] = len(js)
        e["safety_scope"]["compounding_error"] = True
    run("R4 chain 5 > 3 with TEST_EACH_JUNCTION", long_chain, "R4")
    run("R5 TESTED with source null",
        lambda e: b(e)["junctions"][0].update(provenance="TESTED", source=None), "R5")
    run("R5 TESTED output quantity, no source",
        lambda e: b(e)["output"]["quantities"].append(
            {"quantity": "q", "value": "1", "units": "u", "provenance": "TESTED", "source": None}), "R5")
    run("C1 chain_length mismatch", lambda e: b(e).update(chain_length=7), "C1")
    run("C2 over-claimed SINGLE_BUILD_CHECK with irreversible junction",
        lambda e: b(e)["verification_required"].update(level="SINGLE_BUILD_CHECK"), "C2")
    run("C3 irreversibility flag false while junction irreversible",
        lambda e: e["safety_scope"].update(irreversibility=False), "C3")
    run("C3 reader_state true with illegible hazard",
        lambda e: b(e)["junctions"][1].update(hazard="CO"), "C3")

    def two_inferred(e):
        b(e)["junctions"][0].update(provenance="INFERRED_BY_ASSEMBLY", source=None)
    run("C3 compounding_error false with 2 consecutive INFERRED", two_inferred, "C3")
    run("C4 missing function", lambda e: e.pop("function"), "C4")
    run("C4 status not co-authored", lambda e: e.update(status="final"), "C4")

    # R6: ledger CAUTION on an irreversible junction must appear in the entry
    e = _good_entry()
    ref = junction_ref(e, 0, e["branches"][0]["junctions"][1])
    caut = {ref: ["UNSAFE: room filled with smoke [N-MN, 2026-12-01]"]}
    ef, res = validate_entry(e, schema, caut)
    msgs = [w for fs in res.values() for _, w in fs]
    checks.append(("R6 CAUTION on irreversible step missing from entry", any(m.startswith("R6") for m in msgs), msgs))
    e["branches"][0]["junctions"][1]["caution"] = ("A field report says this step filled a room with smoke. "
                                                    "Check the air supply before anyone sleeps near it.")
    ef, res = validate_entry(e, schema, caut)
    msgs = [w for fs in res.values() for _, w in fs]
    checks.append(("R6 passes once entry carries plain caution", not msgs, msgs))
    e["branches"][0]["junctions"][1]["caution"] = "CO asphyxiation hazard"
    ef, res = validate_entry(e, schema, caut)
    msgs = [w for fs in res.values() for _, w in fs]
    checks.append(("R6 jargon-only caution still fails", any(m.startswith("R6") for m in msgs), msgs))

    # seeds must pass
    for name in ("seeds/lighting.json", "seeds/shelter_envelope.json"):
        p = os.path.join(HERE, name)
        try:
            with open(p) as f:
                ent = json.load(f)
            ef, res = validate_entry(ent, schema)
            msgs = [w for _, w in ef] + [w for fs in res.values() for _, w in fs]
            checks.append(("seed %s passes" % name, not msgs, msgs))
        except (IOError, ValueError) as ex:
            checks.append(("seed %s readable" % name, False, [str(ex)]))

    nbad = 0
    for label, ok, msgs in checks:
        print(("PASS " if ok else "FAIL ") + label)
        if not ok:
            nbad += 1
            for m in msgs[:5]:
                print("       " + m)
    print("%d checks, %d failed" % (len(checks), nbad))
    return 1 if nbad else 0


def main(argv):
    schema_path = DEFAULT_SCHEMA
    if "--schema" in argv:
        i = argv.index("--schema")
        schema_path = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
    ledger_path = None
    if "--ledger" in argv:
        i = argv.index("--ledger")
        if i + 1 >= len(argv):
            sys.stderr.write("--ledger needs a path\n")
            return 2
        ledger_path = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
    try:
        with open(schema_path) as f:
            schema = json.load(f)
    except (IOError, ValueError) as ex:
        sys.stderr.write("cannot read schema %s: %s\n" % (schema_path, ex))
        return 2
    if argv[:1] == ["--selftest"]:
        return selftest(schema)
    if not argv or argv[0] in ("-h", "--help"):
        sys.stderr.write("usage: validate.py ENTRY.json [ENTRY.json ...] [--ledger LEDGER] | --selftest [--schema PATH]\n")
        return 2
    bad = False
    for p in argv:
        try:
            with open(p) as f:
                entry = json.load(f)
        except (IOError, ValueError) as ex:
            sys.stderr.write("cannot read %s: %s\n" % (p, ex))
            return 2
        cautions = None
        if ledger_path:
            import ledger as _ledger
            import status as _status
            recs = _ledger.read(ledger_path)
            lp = _ledger.verify(recs)
            if lp:
                sys.stderr.write("ledger broken: %s\n" % lp[0])
                return 1
            cautions = dict((k, v["caution"]) for k, v in _status.caution_refs([entry], recs).items())
        ef, res = validate_entry(entry, schema, cautions)
        bad = report(p, ef, res) or bad
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
