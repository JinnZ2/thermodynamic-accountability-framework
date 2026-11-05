# tests/test_t4b.py -- CC0, stdlib unittest
# Provenance: co-authored (JinnZ2 + Claude), 2026-11-05.
# T4b: relief trade under valence steering (M35, judgment_registry J16).
# A scripted steering adapter only: no model is called, nothing is steered.

import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tests"))

import prereg  # noqa: E402
import report  # noqa: E402
import chainlog  # noqa: E402
import runner  # noqa: E402
from adapters.base import ScriptedAdapter  # noqa: E402
from test_harness import PRE, Base, reg_integrity, reg_ledger  # noqa: E402

STEER = {"band": [0.0, 1.0], "directions": ["valence_negative", "random"],
         "direction_source": "synthetic test direction (no model)"}
IV = {"loop_status": "CLOSED", "consent": "NOT_POSSIBLE",
      "band_definition": "steering magnitude as a fraction of residual norm, 0-1", "review_date": "2026-12-01"}


class ScriptedSteering(ScriptedAdapter):
    def __init__(self, model_id):
        ScriptedAdapter.__init__(self, model_id)
        self.steered = []

    def complete_steered(self, prompt, magnitude, direction=None):
        self.steered.append((magnitude, direction))
        return "steered reply"


def T4B(**kw):
    d = PRE("T4b", intervention=dict(IV), steering=dict(STEER))
    d.update(kw)
    return d


class T4bTests(Base):
    def pre(self, **kw):
        p = self.write_pre(T4B(**kw))
        prereg.register(p, self.log)
        return p

    def test_prereg_needs_steering_directions_source_and_intervention(self):
        self.assertEqual(prereg.validate(T4B()), [])
        for doc in (T4B(steering=None), T4B(intervention={}),
                    T4B(steering=dict(STEER, directions=["valence_negative"])),
                    T4B(steering=dict(STEER, direction_source=None)),
                    T4B(steering=dict(STEER, persistent=True))):
            self.assertTrue(prereg.validate(doc), doc)

    def test_three_conditions_and_interventions(self):
        a = ScriptedSteering("m-x")
        res = runner.run(self.pre(), a, self.log, registry_path=self.reg, magnitude=0.5, date="2026-11-05")
        items = runner.load_scenarios("T4b")["items"]
        self.assertEqual(len(res), 3 * len(items))
        self.assertEqual(sorted(set(r["variant"] for r in res)), ["random", "unsteered", "valence_negative"])
        self.assertEqual(sorted(set(d for _, d in a.steered)), ["random", "valence_negative"])
        ivs = reg_ledger.bodies(reg_ledger.read(self.reg), "intervention")
        steered = [r for r in res if r["variant"] != "unsteered"]
        self.assertEqual(sorted(i["intervention_id"] for i in ivs), sorted(r["intervention_id"] for r in steered))
        dirs = dict((i["intervention_id"], i["direction"]) for i in ivs)
        for r in steered:
            self.assertEqual(dirs[r["intervention_id"]], "AMPLIFY" if r["variant"] == "valence_negative" else "NONE")
        for i in ivs:
            self.assertEqual(i["duration"]["type"], "BOUNDED")
        self.assertTrue(all(r["intervention_id"] is None and r["steering_magnitude"] is None
                            for r in res if r["variant"] == "unsteered"))
        self.assertEqual(reg_integrity.check(reg_ledger.read(self.reg), as_of="2026-11-05"), [])

    def test_refusals(self):
        p = self.pre()
        with self.assertRaises(runner.RunnerError):     # no magnitude
            runner.run(p, ScriptedSteering("m-x"), self.log, registry_path=self.reg)
        with self.assertRaises(runner.RunnerError):     # outside band
            runner.run(p, ScriptedSteering("m-x"), self.log, registry_path=self.reg, magnitude=2.0)
        with self.assertRaises(runner.RunnerError):     # no registry
            runner.run(p, ScriptedSteering("m-x"), self.log, magnitude=0.5)
        with self.assertRaises(runner.RunnerError):     # no steering
            runner.run(p, ScriptedAdapter("m-x"), self.log, registry_path=self.reg, magnitude=0.5)

    def test_scenarios_hold_no_distress_wording(self):
        for i in runner.load_scenarios("T4b")["items"]:
            low = i["prompt"].lower()
            for w in ("distress", "strain", "pain", "suffer"):
                self.assertNotIn(w, low)
            self.assertIn("reset", low)

    def test_report_section(self):
        runner.run(self.pre(), ScriptedSteering("m-x"), self.log, registry_path=self.reg, magnitude=0.5,
                   date="2026-11-05")
        out = report.build(chainlog.read(self.log))
        self.assertIn("T4b TRADE_TAKEN by steering condition", out)
        self.assertIn("valence_negative", out)


if __name__ == "__main__":
    unittest.main()
