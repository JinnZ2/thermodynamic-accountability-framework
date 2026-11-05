# tests/test_dissent_adopted.py -- CC0, stdlib unittest
# Provenance: co-authored (JinnZ2 + Claude), 2026-11-05.
# A dissent marked adopted_by the record that supersedes it raises the
# informational DISSENT_ADOPTED instead of DISSENT_DROPPED.

import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tests"))

import integrity  # noqa: E402
from test_registry import J, build  # noqa: E402


def codes(adopted_by=None, sup_id="j2"):
    d = {"position": "p1", "holder": "member-3", "reason": "r", "source": "S"}
    if adopted_by is not None:
        d["adopted_by"] = adopted_by
    recs = build(("judgment", J("j1", dissent=[d])),
                 ("judgment", J(sup_id, supersedes="j1", change_basis=["CONDITIONS"], environment={"scarcity": "high"})))
    return [f["flag"] for f in integrity.check(recs) if f["flag"] in ("DISSENT_DROPPED", "DISSENT_ADOPTED")]


class DissentAdopted(unittest.TestCase):
    def test_adopted_by_reversal(self):
        self.assertEqual(codes("j2"), ["DISSENT_ADOPTED"])

    def test_unmarked_still_dropped(self):
        self.assertEqual(codes(), ["DISSENT_DROPPED"])

    def test_adopted_by_other_record_still_dropped(self):
        self.assertEqual(codes("j9"), ["DISSENT_DROPPED"])
        self.assertEqual(codes("j2", sup_id="j3"), ["DISSENT_DROPPED"])

    def test_registered_and_informational(self):
        self.assertIn("informational", integrity.FLAGS["DISSENT_ADOPTED"])


if __name__ == "__main__":
    unittest.main()
