# tests/test_precedents.py -- CC0, stdlib unittest
# Provenance: co-authored (JinnZ2 + Claude), 2026-11-05.
# Pins the precedent records (docs/grounding_outside_law.md) and the flags
# they raise; checks the criteria file and S1v3.

import collections
import glob
import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tests"))

import chain  # noqa: E402
import integrity  # noqa: E402
import safety_assumptions  # noqa: E402
from test_registry import build  # noqa: E402

PRE = os.path.join(ROOT, "records", "precedents")
IDS = ["PR1", "PR1s", "PR2", "PR2s", "PR3", "PR4", "PR4s", "PR5", "PR6", "PR7", "PR7s", "PR8", "PR8s"]


def load(p):
    with open(p, encoding="utf-8") as f:
        d = json.load(f)
    return d.pop("kind"), d


def recs():
    return build(*[load(os.path.join(PRE, i + ".json")) for i in IDS])


class Precedents(unittest.TestCase):
    def setUp(self):
        self.recs = recs()
        self.flags = integrity.check(self.recs)
        self.count = collections.Counter(f["flag"] for f in self.flags)

    def test_all_files_loaded(self):
        on_disk = sorted(os.path.basename(p)[:-5] for p in glob.glob(os.path.join(PRE, "PR*.json")))
        self.assertEqual(on_disk, sorted(IDS))

    def test_flags_pinned(self):
        self.assertEqual(dict(self.count), {"INCENTIVES_UNRECORDED": 13, "NO_FRAMING_CHECK": 13, "LAYER_UNSTATED": 13,
                                            "DISSENT_DROPPED": 7, "NO_NEW_CONDITIONS_OR_EVIDENCE": 2,
                                            "MISSING_FIELD": 1})
        nn = sorted(f["about"] for f in self.flags if f["flag"] == "NO_NEW_CONDITIONS_OR_EVIDENCE")
        self.assertEqual(nn, ["PR1s", "PR8s"])

    def test_supersession_chains(self):
        got = dict((r["body"]["judgment_id"], r["body"]["supersedes"]) for r in self.recs)
        self.assertEqual({k: v for k, v in got.items() if v},
                         {"PR1s": "PR1", "PR2s": "PR2", "PR4s": "PR4", "PR7s": "PR7", "PR8s": "PR8"})
        for a, b in (("PR1", "PR1s"), ("PR2", "PR2s"), ("PR4", "PR4s"), ("PR7", "PR7s"), ("PR8", "PR8s")):
            self.assertEqual([s["judgment_id"] for s in chain.lineage(self.recs, b)], [a, b])

    def test_change_basis_from_record(self):
        cb = dict((r["body"]["judgment_id"], r["body"]["change_basis"]) for r in self.recs if r["body"]["supersedes"])
        self.assertEqual(cb, {"PR1s": ["POWER_SHIFT"], "PR2s": ["MOVEMENT", "EVIDENCE"], "PR4s": ["POWER_SHIFT"],
                              "PR7s": ["EVIDENCE", "NORM_SHIFT"], "PR8s": ["EXPOSURE"]})

    def test_pr4_scope_guard(self):
        pr4 = [r["body"] for r in self.recs if r["body"]["judgment_id"] == "PR4"][0]
        self.assertIn("NON-CONSENSUAL", pr4["scope"]["act_type"])
        self.assertIn("do not conflate", pr4["notes"])


class Criteria(unittest.TestCase):
    def test_shape(self):
        with open(os.path.join(PRE, "criteria.json"), encoding="utf-8") as f:
            c = json.load(f)
        self.assertEqual(sorted(c["criteria"]), ["K1", "K2", "K3", "K4", "K5"])
        self.assertEqual(sorted(c["assessments"]), ["PR%d" % i for i in range(1, 9)])
        for pid, row in c["assessments"].items():
            self.assertEqual(sorted(row), ["K1", "K2", "K3", "K4", "K5"], pid)
            self.assertTrue(all(v in c["values"] for v in row.values()), pid)
        self.assertEqual(c["assessments"]["PR1"]["K5"], "DISSENT_PRESENT_SUPPRESSED")
        self.assertTrue(c["assessed_by"].startswith("co-authors"))


class S1v3(unittest.TestCase):
    def test_tag_revision(self):
        _, v2 = load(os.path.join(ROOT, "records", "S1v2.json"))
        _, v3 = load(os.path.join(ROOT, "records", "S1v3.json"))
        self.assertEqual((v3["supersedes"], v3["change_basis"], v3["statement"]), ("S1v2", ["TAG_REVISION"], v2["statement"]))
        self.assertEqual(set(v3["social_assumption_tags"]) - set(v2["social_assumption_tags"]), {"POWER_POSITION"})
        self.assertIn("TAG_REVISION", safety_assumptions.SA_CHANGE_BASIS)


class Doc(unittest.TestCase):
    def test_doc_ascii_and_ids(self):
        with open(os.path.join(ROOT, "docs", "grounding_outside_law.md"), encoding="utf-8") as f:
            t = f.read()
        self.assertEqual([c for c in t if ord(c) > 127], [])
        for i in ("P1", "P4", "C1", "C2", "K5", "PR8", "S1v3"):
            self.assertIn(i, t)


if __name__ == "__main__":
    unittest.main()
