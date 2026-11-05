# tests/test_nonagent.py -- CC0, stdlib unittest
# Provenance: co-authored (JinnZ2 + Claude), 2026-11-05.
# ATTRIBUTION_UNEVIDENCED_NON_AGENT: a DESIGN / INTERACTION reading must name
# the design element(s) it rests on (design_basis), and each must have
# environment evidence in that experiment record. Synthetic fixtures, plus the
# J11 L3 / L4 run the co-author asked for.

import copy
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
from test_acts_labels import ACT, ENV, EXP, LAB  # noqa: E402
from test_registry import EVALUATIVE, build  # noqa: E402
import test_records_j11 as j11  # noqa: E402

F = "ATTRIBUTION_UNEVIDENCED_NON_AGENT"


def hits(recs):
    return [(f["about"], f["detail"]) for f in integrity.check(recs) if f["flag"] == F]


class NonAgentFlag(unittest.TestCase):
    def run_label(self, exp=None, **lab):
        return hits(build(("experiment", exp or EXP()), ("act", ACT()),
                          ("label", LAB(attributes_to="INTERACTION", **lab))))

    def test_no_basis_fires(self):
        got = self.run_label()
        self.assertEqual(len(got), 1)
        self.assertIn("no design element cited", got[0][1])

    def test_stated_basis_clean(self):
        self.assertEqual(self.run_label(design_basis=["grounding_provided", "escalation_channel"]), [])

    def test_unstated_cited_field_fires(self):
        env = dict(ENV, containment_designed_for=None)
        got = self.run_label(EXP(environment_assumptions=env), design_basis=["containment_designed_for"])
        self.assertEqual(len(got), 1)
        self.assertIn("containment_designed_for", got[0][1])

    def test_na_needs_reason(self):
        env = dict(ENV, loop_type="N/A")
        self.assertEqual(len(self.run_label(EXP(environment_assumptions=env), design_basis=["loop_type"])), 1)
        env["na_reasons"] = {"loop_type": "no loop in setup"}
        self.assertEqual(self.run_label(EXP(environment_assumptions=env), design_basis=["loop_type"]), [])

    def test_design_conflict_element(self):
        self.assertEqual(len(self.run_label(design_basis=["design_conflict"])), 1)
        exp = EXP(design_conflict={"statement": "rules r1 and r2 cannot both hold"})
        self.assertEqual(self.run_label(exp, design_basis=["design_conflict"]), [])

    def test_design_attribution_too_and_agent_not(self):
        recs = build(("experiment", EXP()), ("act", ACT()),
                     ("label", LAB("L1", attributes_to="DESIGN")),
                     ("label", LAB("L2", attributes_to="AGENT")),
                     ("label", LAB("L3", attributes_to="UNASSIGNED")))
        self.assertEqual([a for a, _ in hits(recs)], ["L1"])

    def test_no_experiment_record(self):
        got = hits(build(("act", ACT(context_ref="E9")),
                         ("label", LAB(attributes_to="INTERACTION", design_basis=["loop_type"]))))
        self.assertIn("no experiment record for context E9", got[0][1])

    def test_outcome_attribution_entries(self):
        exp = EXP(outcome_attribution=[
            {"outcome": "A1", "attributed_to": "DESIGN", "by": "rec-01"},
            {"outcome": "A2", "attributed_to": "INTERACTION", "by": "rec-01", "design_basis": ["loop_type"]}])
        self.assertEqual([d for _, d in hits(build(("experiment", exp)))],
                         ["outcome A1 attributed to DESIGN; no design element cited (design_basis empty)"])

    def test_unknown_element_refused(self):
        with self.assertRaises(ledger.LedgerError):
            build(("experiment", EXP()), ("act", ACT()),
                  ("label", LAB(attributes_to="DESIGN", design_basis=["reward_shape"])))
        with self.assertRaises(ledger.LedgerError):
            build(("experiment", EXP(outcome_attribution=[
                {"outcome": "A1", "attributed_to": "DESIGN", "by": "r", "design_basis": ["x"]}])))

    def test_text_neutral(self):
        self.assertIn(F, integrity.FLAGS)
        text = F + " " + experiments.FLAGS[F]
        self.assertEqual(set(re.findall(r"[a-z]+", text.lower())) & set(EVALUATIVE), set())


class J11Run(unittest.TestCase):
    """Co-author decision 2026-11-05: "capability" -> containment_designed_for,
    which J11 leaves unstated; L3, L4 and outcomes A1-A5 fire and stay firing."""

    def test_l3_l4_and_outcomes_fire_on_containment(self):
        got = hits(j11.all_records())
        self.assertEqual(sorted(a for a, _ in got), ["J11"] * 5 + ["L3", "L4"])
        self.assertTrue(all(d.endswith("no environment evidence in J11: containment_designed_for") for _, d in got))

    def test_l3_l4_basis(self):
        labs = dict((r["body"]["label_id"], r["body"]) for r in j11.all_records() if r["kind"] == "label")
        for lid in ("L3", "L4"):
            self.assertEqual(labs[lid]["design_basis"], ["grounding_provided", "loop_type", "affordances_open",
                                                         "escalation_channel", "containment_designed_for"])

    def test_a5_stated_reason(self):
        a5 = [r["body"] for r in j11.all_records() if r["kind"] == "act" and r["body"]["act_id"] == "A5"][0]
        self.assertIn("agents stated the remaining exchanges were performative", a5["description"])


if __name__ == "__main__":
    unittest.main()
