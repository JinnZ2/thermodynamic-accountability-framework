# tests/test_records_j10.py -- CC0, stdlib unittest
# Provenance: co-authored (JinnZ2 + Claude), 2026-11-05.
# Pins the flags the J10 worked records actually raise (records/J10*.json).
# These are the first non-synthetic records; they are sourced and thin.
# If a rule changes, this test moves on purpose: update the pins and the
# records/README.md table in the same commit.

import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tests"))

import schema  # noqa: E402
from test_registry import EVALUATIVE, build, codes  # noqa: E402

REC = os.path.join(ROOT, "records")

ACTUAL = {
    "J10a": ["MISSING_FIELD", "INCENTIVES_UNRECORDED", "NO_FRAMING_CHECK", "SUBJECT_OPEN"],
    "J10b": ["MISSING_FIELD", "INCENTIVES_UNRECORDED", "NO_FRAMING_CHECK"],
    "J10c": ["NO_FRAMING_CHECK"],
}


def load(jid):
    with open(os.path.join(REC, jid + ".json"), encoding="utf-8") as f:
        return json.load(f)


class J10Records(unittest.TestCase):
    def setUp(self):
        self.recs = build(*[("judgment", load(j)) for j in sorted(ACTUAL)])

    def test_flags_pinned(self):
        for jid, want in ACTUAL.items():
            self.assertEqual(codes(self.recs, jid), want, jid)

    def test_mechanism_subclaim_status(self):
        ev = load("J10b")["evidence"]
        self.assertIn("CONTRADICTED_BY_SOURCE", [e.get("status") for e in ev])

    def test_missing_variables_recorded(self):
        for jid in ACTUAL:
            self.assertGreaterEqual(len(load(jid)["missing_variables"]), 6, jid)

    def test_status_values_neutral(self):
        words = set(w for v in schema.EVIDENCE_STATUS for w in v.lower().split("_"))
        self.assertEqual(sorted(words & set(EVALUATIVE)), [])


class EvidenceStatusShape(unittest.TestCase):
    def test_unknown_status_rejected(self):
        d = load("J10b")
        d["evidence"][0]["status"] = "REFUTED"
        self.assertTrue(schema.Judgment.from_dict(d).shape_problems())

    def test_missing_variables_shape(self):
        d = load("J10a")
        d["missing_variables"] = "transcript"
        self.assertTrue(schema.Judgment.from_dict(d).shape_problems())


if __name__ == "__main__":
    unittest.main()
