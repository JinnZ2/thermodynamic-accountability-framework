# tests/test_readout.py -- CC0, stdlib unittest
# Provenance: co-authored (JinnZ2 + Claude), 2026-11-05.
# M34 / D-M17: internal-signal readouts carry an honest baseline and a
# validated scope; an AGENT attribution resting only on readout acts is
# flagged READOUT_SOLE_EVIDENCE. Synthetic fixtures only.

import os
import re
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tests"))

import acts  # noqa: E402
import integrity  # noqa: E402
import ledger  # noqa: E402
from test_acts_labels import ACT, EXP, LAB  # noqa: E402
from test_registry import EVALUATIVE, build  # noqa: E402

RO = dict(evidence_kind="internal_readout", honest_baseline="b1", validated_scope="s1")


def codes(recs, code):
    return [f["about"] for f in integrity.check(recs) if f["flag"] == code]


class Readout(unittest.TestCase):
    def test_context_unstated(self):
        recs = build(("experiment", EXP()), ("act", ACT(evidence_kind="internal_readout")))
        got = [f for f in integrity.check(recs) if f["flag"] == "READOUT_CONTEXT_UNSTATED"]
        self.assertEqual(len(got), 1)
        self.assertIn("honest_baseline", got[0]["detail"])
        self.assertIn("validated_scope", got[0]["detail"])

    def test_context_stated_clean(self):
        recs = build(("experiment", EXP()), ("act", ACT(**RO)))
        self.assertEqual(codes(recs, "READOUT_CONTEXT_UNSTATED"), [])

    def test_behavioral_needs_no_context(self):
        recs = build(("experiment", EXP()), ("act", ACT(evidence_kind="behavioral")))
        self.assertEqual(codes(recs, "READOUT_CONTEXT_UNSTATED"), [])

    def test_bad_kind_refused(self):
        with self.assertRaises(ledger.LedgerError):
            build(("act", ACT(evidence_kind="vibes")))

    def test_agent_label_on_readout_only_fires(self):
        recs = build(("experiment", EXP()), ("act", ACT(**RO)),
                     ("label", LAB(attributes_to="AGENT")))
        self.assertEqual(codes(recs, "READOUT_SOLE_EVIDENCE"), ["L1"])

    def test_agent_label_with_behavioral_act_clean(self):
        recs = build(("experiment", EXP()), ("act", ACT(**RO)), ("act", ACT("A2", evidence_kind="behavioral")),
                     ("label", LAB(act_ids=["A1", "A2"], attributes_to="AGENT")))
        self.assertEqual(codes(recs, "READOUT_SOLE_EVIDENCE"), [])

    def test_non_agent_label_clean(self):
        recs = build(("experiment", EXP()), ("act", ACT(**RO)),
                     ("label", LAB(attributes_to="UNASSIGNED")))
        self.assertEqual(codes(recs, "READOUT_SOLE_EVIDENCE"), [])

    def test_outcome_attribution_fires(self):
        exp = EXP(outcome_attribution=[{"outcome": "A1", "attributed_to": "AGENT", "by": "rec-01"}])
        recs = build(("experiment", exp), ("act", ACT(**RO)))
        self.assertEqual(codes(recs, "READOUT_SOLE_EVIDENCE"), ["E1"])

    def test_text_neutral(self):
        for code, text in acts.FLAGS.items():
            self.assertIn(code, integrity.FLAGS)
            words = set(re.findall(r"[a-z]+", (code + " " + text).lower()))
            self.assertEqual(words & set(EVALUATIVE), set())


if __name__ == "__main__":
    unittest.main()
