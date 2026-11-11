"""
test_unknown_axis.py -- UNKNOWN is a coverage axis, not a severity.

Planted known-answer cases (a)/(b)/(c) from unknown_axis_cases.PLANTED,
plus the two print rules. stdlib unittest. CC0.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from unified_audit import (run_full_audit, _aggregate_status,
                           _STATUS_RANK, NOT_DETERMINABLE)
from unknown_axis_cases import PLANTED, CASES, BEFORE, render


class TestPlanted(unittest.TestCase):

    def test_planted_answers(self):
        for cid, _src, kw, exp in PLANTED:
            with self.subTest(case=cid):
                r = run_full_audit(system_id=cid, **kw)
                self.assertEqual(r.severity, exp["severity"])
                self.assertEqual(len(r.coverage), exp["coverage_count"])

    def test_b_prints_both_axes(self):
        _cid, _s, kw, _e = PLANTED[1]
        r = run_full_audit(**kw)
        self.assertEqual(r.overall_status, "GREEN+COVERAGE(3)")
        self.assertNotEqual(r.overall_status, "GREEN")
        self.assertIn("Coverage: 3", r.summary)

    def test_coverage_entries_carry_expiry(self):
        _cid, _s, kw, _e = PLANTED[1]
        r = run_full_audit(**kw)
        self.assertEqual(sorted(e["input"] for e in r.coverage),
                         ["K_cred", "hidden_count", "long_tail_risk"])
        for e in r.coverage:
            self.assertIn("pr77", e["expiry_condition"])
            self.assertIn("pr78", e["expiry_condition"])


class TestRules(unittest.TestCase):

    def test_unknown_not_in_rank_table(self):
        self.assertNotIn("UNKNOWN", _STATUS_RANK)

    def test_aggregate_ignores_unmeasured(self):
        self.assertEqual(_aggregate_status(["UNKNOWN", "GREEN"]), "GREEN")
        self.assertEqual(_aggregate_status(["UNKNOWN"]), NOT_DETERMINABLE)
        self.assertEqual(_aggregate_status([]), NOT_DETERMINABLE)
        self.assertEqual(_aggregate_status(["not_a_label"]), NOT_DETERMINABLE)
        self.assertEqual(_aggregate_status(["RED", "UNKNOWN"]), "RED")

    def test_single_color_never_alone_with_coverage(self):
        for cid, _src, kw in CASES:
            r = run_full_audit(system_id=cid, **kw)
            if r.coverage:
                self.assertNotIn(r.overall_status, ("GREEN", "YELLOW", "RED"))

    def test_existing_cases_changed_count(self):
        changed = []
        for cid, _src, kw in CASES:
            r = run_full_audit(system_id=cid, **kw)
            if r.overall_status != BEFORE[cid]:
                changed.append(cid)
        self.assertEqual(changed, ["T1_empty"])

    def test_generated_doc_current(self):
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "..", "docs", "UNKNOWN_AXIS.md")
        with open(path) as fh:
            self.assertEqual(fh.read(), render(None))


if __name__ == "__main__":
    unittest.main()
