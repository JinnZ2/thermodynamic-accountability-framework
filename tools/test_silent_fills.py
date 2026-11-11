#!/usr/bin/env python3
# tools/test_silent_fills.py -- CC0, stdlib only, python >= 3.7
# Provenance: co-authored (Kavik + Claude), 2026-11-11.
#
# Missing-input test family for docs/expiry_register.json silent_fills.
# One case per SILENT_FILL row. Each case omits the input that row names,
# runs the code in baseline mode, and asserts:
#   1. the CURRENT output (pinned; this file changes no verdict), and
#   2. that the row's stated file:line actually executed (line trace).
# A further test fails if a register row has no case here, or a case
# names no row, so the family cannot fall out of step with the register.
#
#   python tools/test_silent_fills.py
#   python tools/test_silent_fills.py --hits   per-row hit counts, incl. existing suites

import json
import math
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for sub in ("calibration", "political_audit", "core"):
    sys.path.insert(0, os.path.join(ROOT, sub))
for v in ("TAF_FILL_R1", "TAF_FILL_R2", "TAF_FILL_R3", "TAF_FILL_R6"):
    os.environ.pop(v, None)  # baseline only

import provenance_corruption_detector_2026 as R1   # noqa: E402
import substrate_audit as R2                       # noqa: E402  (political_audit/)
import automation_assessment as R3                 # noqa: E402
import calibration_audit as CA                     # noqa: E402
import adaptation_debt as AD                       # noqa: E402
import pipeline as PL                              # noqa: E402

assert R2.__file__.endswith(os.path.join("political_audit", "substrate_audit.py")), R2.__file__

REG = os.path.join(ROOT, "docs", "expiry_register.json")


def rows():
    with open(REG, encoding="utf-8") as f:
        return {r["id"]: r for r in json.load(f)["silent_fills"]["rows"]}


def traced(fn, fired=None):
    """Run fn, return (result, set of (relpath, line) executed).
    With fired={(relpath, line): predicate(locals)}, also record into
    fired_hits the lines where the predicate held (the input was absent)."""
    hits = set()
    traced.fired_hits = set()

    def tracer(frame, event, arg):
        if event == "line":
            p = os.path.relpath(os.path.abspath(frame.f_code.co_filename), ROOT)
            key = (p.replace(os.sep, "/"), frame.f_lineno)
            hits.add(key)
            if fired and key in fired:
                try:
                    if fired[key](frame.f_locals):
                        traced.fired_hits.add(key)
                except Exception:
                    pass
        return tracer

    old = sys.gettrace()
    sys.settrace(tracer)
    try:
        out = fn()
    finally:
        sys.settrace(old)
    return out, hits


def _basic_desc(event):
    return {"system_id": "missing-input case", "friction_events": [event]}


# id -> (callable with the input omitted, expected current output)
CASES = {
    "SF-R1": (lambda: R1.grounding_score("Output rose.", [{"url": "u"}]), 0.10),
    "SF-R1b": (lambda: R1.grounding_score("Output rose.", [{"type": "not_a_listed_type"}]), 0.10),
    "SF-R1c": (lambda: R1.grounding_score("Output rose 45 percent.", []), 0.10),
    "SF-R1d": (lambda: R1.grounding_score("output rose.", []), 0.30),
    "SF-R2": (lambda: R2.check_cross_domain_constraints("unregistered_field", []).passes, True),
    "SF-R3": (lambda: R3.automation_entropy([{"name": "m"}], []), -2),
    "SF-R6a": (lambda: CA._is_removed({}), False),
    "SF-R6b": (lambda: CA.score_friction_removal([{"was_removed": True}]).score, 0.0),
    "SF-R6c": (lambda: PL.run_unified_audit(_basic_desc({"type": "t"}))
               ["module_reports"]["adaptation_debt"]["aggregate_band"], None),
    "SF-R6d": (lambda: PL.run_unified_audit(_basic_desc({"type": "t", "was_removed": True}))
               ["module_reports"]["adaptation_debt"]["aggregate_band"], None),
    "SF-R6e": (lambda: AD.compute_event_debt({}), 0.0),
    "SF-R6f": (lambda: AD.compute_event_debt({"removed": True}), 0.5),
    "SF-AD1": (lambda: AD.compute_event_debt({"removed": True, "years_since_removed": 1.0,
                                              "domain": "physical"}), 1.04 * 0.5),
    "SF-AD2": (lambda: AD.compute_event_debt({"removed": True, "years_since_removed": 1.0,
                                              "initial_load": 1.0}), 1.08),
    "SF-AD3": (lambda: AD.compute_event_debt({"removed": True, "years_since_removed": 1.0,
                                              "initial_load": 1.0, "domain": "not_listed"}), 1.08),
}

# pipeline cases pin the band read back from the module report; filled in below
_PIPELINE_BAND = {"SF-R6c", "SF-R6d"}


class SilentFillCoverage(unittest.TestCase):
    maxDiff = None

    def test_every_row_has_a_case(self):
        self.assertEqual(sorted(rows()), sorted(CASES))

    def test_each_case_hits_its_line_and_pins_current_output(self):
        reg = rows()
        for rid, (fn, expected) in sorted(CASES.items()):
            with self.subTest(row=rid):
                out, hits = traced(fn)
                r = reg[rid]
                self.assertIn((r["file"], r["line"]), hits,
                              "%s: %s:%d not executed" % (rid, r["file"], r["line"]))
                if rid in _PIPELINE_BAND:
                    self.assertEqual(out, PINNED_BAND[rid])
                elif isinstance(expected, float):
                    self.assertTrue(math.isclose(out, expected, rel_tol=1e-12),
                                    "%s: %r != %r" % (rid, out, expected))
                else:
                    self.assertEqual(out, expected)

    def test_fired_predicates_cover_every_row(self):
        self.assertEqual(sorted(FIRED), sorted(rows()))

    def test_each_case_fires_its_fill(self):
        reg = rows()
        for rid, (fn, _) in sorted(CASES.items()):
            with self.subTest(row=rid):
                key = (reg[rid]["file"], reg[rid]["line"])
                traced(fn, fired={key: FIRED[rid]})
                self.assertIn(key, traced.fired_hits, "%s: input present at the line" % rid)

    def test_trace_is_not_silent(self):
        """Null test: a case that does not reach a row's line is caught."""
        _, hits = traced(lambda: R1.grounding_score("x", [{"type": "ai_generated_text"}]))
        r = rows()["SF-R1c"]
        self.assertNotIn((r["file"], r["line"]), hits)


# Current bands, pinned (baseline). Recorded 2026-11-11 from this tree.
PINNED_BAND = {"SF-R6c": "calibrating", "SF-R6d": "mauling"}


def _no(d, *keys):
    return isinstance(d, dict) and not any(k in d for k in keys)


# Per row: does the omitted input really miss at the line? (locals at that line)
FIRED = {
    "SF-R1": lambda L: any(isinstance(c, dict) and "type" not in c for c in L.get("citations") or []),
    "SF-R1b": lambda L: any(isinstance(c, dict) and c.get("type") not in R1.PROVENANCE_GRADES
                            for c in L.get("citations") or []),
    "SF-R1c": lambda L: True,
    "SF-R1d": lambda L: True,
    "SF-R2": lambda L: L.get("field_key") not in R2.CROSS_DOMAIN_CONSTRAINTS,
    "SF-R3": lambda L: _no(L.get("module"), "impact"),
    "SF-R6a": lambda L: _no(L.get("e"), "was_removed", "removed"),
    "SF-R6b": lambda L: _no(L.get("e"), "years_since_removal", "years_since_removed"),
    "SF-R6c": lambda L: _no(L.get("e"), "was_removed", "removed"),
    "SF-R6d": lambda L: _no(L.get("e"), "years_since_removal", "years_since_removed"),
    "SF-R6e": lambda L: _no(L.get("event"), "removed"),
    "SF-R6f": lambda L: _no(L.get("event"), "years_since_removed"),
    "SF-AD1": lambda L: _no(L.get("event"), "initial_load"),
    "SF-AD2": lambda L: _no(L.get("event"), "domain"),
    "SF-AD3": lambda L: _no(L.get("event"), "compounding_rate"),
}


def hit_counts():
    """Per row: how many tests in the existing calibration suites execute
    the row's LINE (the line runs whether or not the input was supplied, so
    this is an upper bound on fills fired), and how many cases in this
    family hit it with the input omitted (the fill fires)."""
    import importlib
    reg = rows()
    targets = {}
    for rid, r in reg.items():
        targets.setdefault((r["file"], r["line"]), []).append(rid)
    counts = {rid: {"existing": 0, "existing_fired": 0, "this_family": 0} for rid in reg}
    suites = [("existing", importlib.import_module(m)) for m in ("test_calibration", "test_audit_family")]
    for label, mod in suites:
        for test in _iter(unittest.defaultTestLoader.loadTestsFromModule(mod)):
            for rid, r in reg.items():
                key = (r["file"], r["line"])
                res = unittest.TestResult()
                _, hits = traced(lambda: test.run(res), fired={key: FIRED[rid]})
                if key in hits:
                    counts[rid][label] += 1
                if key in traced.fired_hits:
                    counts[rid][label + "_fired"] += 1
    for rid, (fn, _) in CASES.items():
        _, hits = traced(fn)
        for key, rids in targets.items():
            if key in hits:
                for r2 in rids:
                    counts[r2]["this_family"] += 1
    return counts


def _iter(suite):
    for t in suite:
        if isinstance(t, unittest.TestSuite):
            yield from _iter(t)
        else:
            yield t


if __name__ == "__main__":
    if "--hits" in sys.argv:
        sys.argv.remove("--hits")
        import io
        import contextlib
        with contextlib.redirect_stdout(io.StringIO()):
            c = hit_counts()
        print("existing = tests in test_calibration + test_audit_family that execute the line")
        print("this_family = cases here that execute the line (each row's own case omits its input)")
        print("existing_fired = of those, tests where the input was absent at the line")
        print("%-8s %9s %15s %12s" % ("row", "existing", "existing_fired", "this_family"))
        for rid in sorted(c):
            print("%-8s %9d %15d %12d" % (rid, c[rid]["existing"], c[rid]["existing_fired"], c[rid]["this_family"]))
        sys.exit(0)
    unittest.main()
