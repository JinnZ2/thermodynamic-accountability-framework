# tests/test_records_j16.py -- CC0, stdlib unittest
# Provenance: co-authored (JinnZ2 + Claude), 2026-11-05.
# Pins the J16 worked records (arXiv 2609.35591v1, read via summarizing
# fetch tool; values unverified against the PDF) and the research_paths
# field (RESEARCH_PATH_SHARED).

import glob
import json
import os
import re
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tests"))

import experiments  # noqa: E402
import integrity  # noqa: E402
import ledger  # noqa: E402
from test_acts_labels import EXP  # noqa: E402
from test_registry import EVALUATIVE, build  # noqa: E402

REC = os.path.join(ROOT, "records", "J16")


def load(p):
    with open(p, encoding="utf-8") as f:
        d = json.load(f)
    return d.pop("kind"), d


def recs():
    return build(*[load(p) for p in sorted(glob.glob(os.path.join(REC, "*.json")))])


class J16Records(unittest.TestCase):
    def setUp(self):
        self.recs = recs()
        self.by = {}
        for r in self.recs:
            b = r["body"]
            self.by[b.get("act_id") or b.get("label_id") or b.get("experiment_id") or b.get("judgment_id")] = b

    def test_flags(self):
        got = sorted((f["flag"], f["about"]) for f in integrity.check(self.recs))
        self.assertEqual(got, [("CONSENT_UNSTATED", "J16-J1"), ("LABEL_ON_ACT_MISSING", "J16-L2"),
                               ("LOOP_UNSTATED", "J16-J1"), ("LOWER_LAYER_SECONDHAND", "J16-J1"),
                               ("NO_FRAMING_CHECK", "J16-J1"), ("PREMISE_WITHOUT_EVIDENCE", "J16-L1"),
                               ("RESEARCH_PATH_SHARED", "J16"), ("SUBJECT_OPEN", "J16-J1")])

    def test_survives(self):
        s = dict((l, self.by[l]["ablation"]["conclusion_survives"]) for l in ("J16-L1", "J16-L2", "J16-L3"))
        self.assertEqual(s, {"J16-L1": "PARTIAL", "J16-L2": "NO", "J16-L3": "YES"})
        self.assertEqual(self.by["J16-L2"]["act_ids"], [])
        self.assertIn("SAME_FAMILY", self.by["J16-L3"]["social_assumption_tags"])

    def test_research_path_and_acts(self):
        rp = self.by["J16"]["research_paths"][0]
        self.assertEqual(len(rp["members"]), 3)
        self.assertEqual([m["record_id"] for m in rp["members"]], ["J16", None, None])
        for a in ("J16-A1", "J16-A2", "J16-A3", "J16-A4"):
            self.assertEqual(self.by[a]["evidence_kind"], "behavioral")
        self.assertEqual(self.by["J16-J1"]["layer_basis"]["agency"]["subject_status"], "OPEN")


class ResearchPaths(unittest.TestCase):
    RP = {"path_id": "RP-1", "shared": "author a", "members": [{"ref": "paper-1"}, {"ref": "paper-2"}]}

    def test_flag_and_shape(self):
        got = [f for f in integrity.check(build(("experiment", EXP(research_paths=[self.RP]))))
               if f["flag"] == "RESEARCH_PATH_SHARED"]
        self.assertEqual(len(got), 1)
        self.assertIn("spans 2 items", got[0]["detail"])
        for bad in ({"path_id": "RP-1", "shared": "a", "members": [{"ref": "x"}]},
                    {"path_id": "RP-1", "members": [{"ref": "x"}, {"ref": "y"}]},
                    dict(self.RP, extra=1)):
            with self.assertRaises(ledger.LedgerError):
                build(("experiment", EXP(research_paths=[bad])))

    def test_text_neutral(self):
        text = "RESEARCH_PATH_SHARED " + experiments.FLAGS["RESEARCH_PATH_SHARED"]
        self.assertEqual(set(re.findall(r"[a-z]+", text.lower())) & set(EVALUATIVE), set())


if __name__ == "__main__":
    unittest.main()
