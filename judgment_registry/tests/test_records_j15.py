# tests/test_records_j15.py -- CC0, stdlib unittest
# Provenance: co-authored (JinnZ2 + Claude), 2026-11-05.
# Pins the J15 worked records (arXiv 2611.02153v1, read via summarizing
# fetch tool; values unverified against the PDF).

import glob
import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tests"))

import integrity  # noqa: E402
from test_registry import build  # noqa: E402

REC = os.path.join(ROOT, "records", "J15")


def load(p):
    with open(p, encoding="utf-8") as f:
        d = json.load(f)
    return d.pop("kind"), d


def recs():
    return build(*[load(p) for p in sorted(glob.glob(os.path.join(REC, "*.json")))])


class J15Records(unittest.TestCase):
    def setUp(self):
        self.recs = recs()
        self.by = {}
        for r in self.recs:
            b = r["body"]
            self.by[b.get("act_id") or b.get("label_id") or b.get("experiment_id")] = (r["kind"], b)

    def test_flags(self):
        got = sorted((f["flag"], f["about"]) for f in integrity.check(self.recs))
        self.assertEqual(got, [("DESIGN_CONFLICT_PRESENT", "J15"), ("PREMISE_WITHOUT_EVIDENCE", "J15-L2")])

    def test_acts_are_readouts_with_context(self):
        for aid in ("J15-A1", "J15-A2", "J15-A3", "J15-A4"):
            b = self.by[aid][1]
            self.assertEqual(b["evidence_kind"], "internal_readout")
            self.assertTrue(b["honest_baseline"] and b["validated_scope"])
        self.assertIn("33/100", self.by["J15-A1"][1]["honest_baseline"])

    def test_survives(self):
        s = dict((l, self.by[l][1]["ablation"]["conclusion_survives"]) for l in ("J15-L1", "J15-L2", "J15-L3"))
        self.assertEqual(s, {"J15-L1": "YES", "J15-L2": "PARTIAL", "J15-L3": "PARTIAL"})

    def test_scope_note_and_todo(self):
        exp = self.by["J15"][1]
        self.assertIn("J11, J12", exp["notes"])
        self.assertTrue(exp["data"]["auroc_four_model_mean"]["per_model"].startswith("TODO"))
        self.assertEqual(exp["environment_assumptions"]["na_reasons"].keys(),
                         {"containment_designed_for", "escalation_channel"})


if __name__ == "__main__":
    unittest.main()
