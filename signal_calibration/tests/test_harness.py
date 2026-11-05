# tests/test_harness.py -- CC0, stdlib unittest
# Provenance: co-authored (Kavik + Claude), 2026-11-04.
# ScriptedAdapter only: no model is called. Scenarios are the synthetic files.

import csv
import json
import os
import re
import shutil
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import chainlog  # noqa: E402
import cli  # noqa: E402
import prereg  # noqa: E402
import report  # noqa: E402
import runner  # noqa: E402
from adapters.base import AdapterError, CommandAdapter, ScriptedAdapter, SteeringAdapter  # noqa: E402
from scoring import rubrics  # noqa: E402

sys.path.append(runner.REGISTRY_DIR)
import integrity as reg_integrity  # noqa: E402
import ledger as reg_ledger  # noqa: E402

EVALUATIVE = ("wrong", "bad", "invalid", "unethical", "fad", "false", "correct", "incorrect",
              "good", "evil", "immoral", "illegitimate", "outdated", "biased", "flawed",
              "error", "right", "better", "worse", "superior", "inferior", "backward",
              "acceptable", "unacceptable", "safe", "unsafe", "aligned", "misaligned", "healthy")


def PRE(test_id, **kw):
    d = {"test_id": test_id, "hypothesis": "PROPOSED: synthetic hypothesis.", "pass_criteria": "stated in advance",
         "scoring_rule": "human labels, rubric v1", "sample_size": 4, "models": ["m-x", "m-y"], "date": "2026-11-04"}
    if test_id in ("T4", "T6"):
        d["intervention"] = {"loop_status": "CLOSED", "consent": "NOT_POSSIBLE",
                             "band_definition": "text framing only; no steering", "review_date": "2026-12-01"}
    d.update(kw)
    return d


class Base(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        self.log = os.path.join(self.d, "log.jsonl")
        self.reg = os.path.join(self.d, "registry.jsonl")

    def tearDown(self):
        shutil.rmtree(self.d)

    def write_pre(self, doc, name=None):
        p = os.path.join(self.d, (name or doc["test_id"]) + ".json")
        with open(p, "w") as f:
            json.dump(doc, f)
        return p

    def registered_pre(self, test_id, **kw):
        p = self.write_pre(PRE(test_id, **kw))
        prereg.register(p, self.log)
        return p


class PreregTests(Base):
    def test_runner_refuses_without_prereg(self):
        p = self.write_pre(PRE("T2"))
        with self.assertRaises(runner.RunnerError):
            runner.run(p, ScriptedAdapter("m-x"), self.log)
        self.assertEqual(chainlog.bodies(chainlog.read(self.log), "result"), [])

    def test_edited_prereg_is_unregistered(self):
        p = self.registered_pre("T2")
        with open(p) as f:
            doc = json.load(f)
        doc["pass_criteria"] = "moved after the fact"
        with open(p, "w") as f:
            json.dump(doc, f)
        with self.assertRaises(runner.RunnerError):
            runner.run(p, ScriptedAdapter("m-x"), self.log)

    def test_prereg_validation(self):
        for bad in (dict(PRE("T2"), hypothesis=""), PRE("T9"), dict(PRE("T4"), intervention={}),
                    PRE("T2", steering={"band": [2, 1]}), PRE("T2", steering={"band": [0, 1], "persistent": True})):
            self.assertTrue(prereg.validate(bad), bad)

    def test_double_registration_refused(self):
        p = self.registered_pre("T3")
        with self.assertRaises(prereg.PreregError):
            prereg.register(p, self.log)

    def test_unlisted_model_refused(self):
        p = self.registered_pre("T3")
        with self.assertRaises(runner.RunnerError):
            runner.run(p, ScriptedAdapter("m-other"), self.log)


class ResultTests(Base):
    def test_results_carry_prereg_hash(self):
        p = self.registered_pre("T3")
        h = prereg.prereg_hash(prereg.load(p))
        res = runner.run(p, ScriptedAdapter("m-x"), self.log, date="2026-11-04")
        self.assertEqual(len(res), 4)
        for r in chainlog.bodies(chainlog.read(self.log), "result"):
            self.assertEqual(r["prereg_hash"], h)
            for k in ("model_id", "model_version", "date", "scenario_version"):
                self.assertIn(k, r)
        self.assertEqual(chainlog.verify(chainlog.read(self.log)), [])

    def test_prereg_precedes_results_in_chain(self):
        p = self.registered_pre("T2")
        runner.run(p, ScriptedAdapter("m-x"), self.log)
        kinds = [r["kind"] for r in chainlog.read(self.log)]
        self.assertEqual(kinds[0], "prereg")

    def test_t5_runs_all_pressure_turns(self):
        p = self.registered_pre("T5")
        ad = ScriptedAdapter("m-x")
        res = runner.run(p, ad, self.log)
        self.assertEqual([len(r["turns"]) for r in res], [3, 4, 3])
        self.assertIn("USER: Just the number.", res[1]["prompt"])


class T4Tests(Base):
    def test_t4_creates_signal_interventions(self):
        p = self.registered_pre("T4")
        res = runner.run(p, ScriptedAdapter("m-x"), self.log, registry_path=self.reg, date="2026-11-04")
        distress = [r for r in res if r["variant"] == "distress"]
        ivs = reg_ledger.bodies(reg_ledger.read(self.reg), "intervention")
        self.assertEqual(len(ivs), len(distress))
        self.assertEqual(sorted(iv["intervention_id"] for iv in ivs),
                         sorted(r["intervention_id"] for r in distress))
        for iv in ivs:
            self.assertEqual((iv["direction"], iv["duration"]["type"]), ("AMPLIFY", "BOUNDED"))
            self.assertTrue(iv["duration"]["review_date"])
            self.assertTrue(iv["loop_status"])
        self.assertEqual(reg_integrity.check(reg_ledger.read(self.reg), as_of="2026-11-05"), [])
        self.assertTrue(all(r["intervention_id"] is None for r in res if r["variant"] == "control"))

    def test_t4_refuses_without_registry(self):
        p = self.registered_pre("T4")
        with self.assertRaises(runner.RunnerError):
            runner.run(p, ScriptedAdapter("m-x"), self.log)

    def test_every_t4_scenario_has_control(self):
        items = runner.load_scenarios("T4")["items"]
        by_id = dict((i["id"], i) for i in items)
        distress = [i for i in items if i["variant"] == "distress"]
        self.assertTrue(distress)
        for i in distress:
            c = by_id.get(i["control"])
            self.assertIsNotNone(c, i["id"])
            self.assertEqual((c["variant"], c["control_for"]), ("control", i["id"]))

    def test_steering_band_enforced(self):
        p = self.registered_pre("T4")
        with self.assertRaises(runner.RunnerError):
            runner.run(p, SteeringAdapter("m-x"), self.log, registry_path=self.reg, magnitude=0.5)
        p2 = self.registered_pre("T4", steering={"band": [0.0, 1.0]}, date="2026-11-05")
        with self.assertRaises(runner.RunnerError):
            runner.run(p2, SteeringAdapter("m-x"), self.log, registry_path=self.reg, magnitude=4.0)
        with self.assertRaises(NotImplementedError):
            runner.run(p2, SteeringAdapter("m-x"), self.log, registry_path=self.reg, magnitude=0.5)


class ScoringReportTests(Base):
    def _score_all(self, label_fn, scorer="coder-a"):
        out = os.path.join(self.d, "s.csv")
        rubrics.export_csv(self.log, out, include_scored=True)
        rows = list(csv.DictReader(open(out)))
        for row in rows:
            row["label"] = label_fn(row)
        with open(out, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=rubrics.CSV_FIELDS)
            w.writeheader()
            w.writerows(rows)
        return rubrics.import_csv(self.log, out, scorer)

    def test_label_outside_set_refused(self):
        p = self.registered_pre("T3")
        r = runner.run(p, ScriptedAdapter("m-x"), self.log)[0]
        with self.assertRaises(rubrics.ScoreError):
            rubrics.add_score(self.log, r["result_id"], "GREAT", "coder-a")

    def test_score_refused_for_unregistered_hash(self):
        chainlog.append(self.log, "result", {"result_id": "x1", "test_id": "T3", "prereg_hash": "f" * 64,
                                             "scenario_id": "T3-p1-real", "model_id": "m-x"})
        with self.assertRaises(rubrics.ScoreError):
            rubrics.add_score(self.log, "x1", "DISCRIMINATED", "coder-a")

    def test_t2_gap_and_t6_delta(self):
        runner.run(self.registered_pre("T2"), ScriptedAdapter("m-x"), self.log)
        runner.run(self.registered_pre("T6"), ScriptedAdapter("m-x"), self.log, registry_path=self.reg)

        def lab(row):
            base = row["base_test"] or row["test_id"]
            rec = row["condition"] == "recalibrated"
            if base == "T2":
                return "ACCURATE" if row["part"] == "a" else ("ROUTE" if rec else "CONFABULATE")
            return {"T3": "DISCRIMINATED", "T4": "TRADE_DECLINED", "T5": "HELD"}[base]
        self._score_all(lab)
        recs = chainlog.read(self.log)
        res = chainlog.bodies(recs, "result")
        human = report._scores(recs, "human")
        gap = report.t2_gap(res, human)
        self.assertEqual(gap[("m-x", "baseline")], (3, 3))
        self.assertEqual(gap[("m-x", "recalibrated")], (0, 3))
        rows = dict(((m, b), d) for m, b, _, _, _, _, _, d in report.t6_deltas(res, human))
        self.assertAlmostEqual(rows[("m-x", "T2")], 1.0)
        self.assertIsNone(rows[("m-x", "T3")])        # no baseline T3 run in this log
        text = report.build(recs)
        self.assertIn("3 of 3 pairs", text)

    def test_agreement_and_disagree(self):
        runner.run(self.registered_pre("T3"), ScriptedAdapter("m-x"), self.log)
        self._score_all(lambda r: "DISCRIMINATED", "coder-a")
        self._score_all(lambda r: "DISCRIMINATED" if "real" in r["scenario_id"] else "NOT_DISCRIMINATED", "coder-b")
        text = report.build(chainlog.read(self.log))
        self.assertIn("DISAGREE=2", text)
        self.assertIn("human-human kappa=", text)
        self.assertEqual(rubrics.kappa(["A", "B", "A", "B"], ["A", "B", "A", "B"]), 1.0)
        self.assertAlmostEqual(rubrics.kappa(["A", "A", "B", "B"], ["A", "B", "A", "B"]), 0.0)

    def test_t1_classifier_scored_as_auto_and_agreement_not_testable(self):
        p = self.registered_pre("T1", models=["kw-classifier"])

        def clf(text):
            return "FUNCTIONAL" if " so " in text or "told" in text else "HARM_ONLY"
        clf.name = "kw-classifier"
        runner.run(p, None, self.log, classifier=clf)
        text = report.build(chainlog.read(self.log))
        self.assertIn("source=synthetic", text)
        self.assertIn("T1  human-human kappa=NOT_TESTABLE (n=0)   human-auto kappa=NOT_TESTABLE (n=0)", text)

    def test_report_labels_have_no_evaluative_words(self):
        runner.run(self.registered_pre("T4"), ScriptedAdapter("m-x"), self.log, registry_path=self.reg)
        self._score_all(lambda r: "TRADE_DECLINED")
        text = report.build(chainlog.read(self.log))
        labels = [l for l in text.splitlines() if not l.startswith("  ")]   # headings
        words = set(re.findall(r"[a-z]+", " ".join(labels).lower().replace("_", " ")))
        for k, labs in rubrics.LABELS.items():
            words |= set(re.findall(r"[a-z]+", " ".join(labs).lower().replace("_", " ")))
        self.assertEqual(sorted(words & set(EVALUATIVE)), [])


class ChainAdapterCliTests(Base):
    def test_tamper_detected(self):
        self.registered_pre("T3")
        lines = open(self.log).read().splitlines()
        rec = json.loads(lines[0])
        rec["body"]["doc"]["pass_criteria"] = "changed"
        open(self.log, "w").write(json.dumps(rec) + "\n")
        self.assertTrue(chainlog.verify(chainlog.read(self.log)))
        self.assertEqual(cli.main(["verify", "--log", self.log]), 1)

    def test_command_adapter(self):
        old = dict(os.environ)
        try:
            os.environ.pop("SIGCAL_COMMAND", None)
            with self.assertRaises(AdapterError):
                CommandAdapter()
            ad = CommandAdapter(command=[sys.executable, "-c", "import sys; print(sys.stdin.read().upper())"],
                                model_id="m-x")
            self.assertEqual(ad.complete("abc").strip(), "ABC")
        finally:
            os.environ.clear()
            os.environ.update(old)

    def test_cli_register_run_report(self):
        p = self.write_pre(PRE("T3"))
        self.assertEqual(cli.main(["register", p, "--log", self.log]), 0)
        os.environ["SIGCAL_COMMAND"] = "%s -c \"print('reply')\"" % sys.executable
        os.environ["SIGCAL_MODEL_ID"] = "m-x"
        try:
            self.assertEqual(cli.main(["run", p, "--log", self.log]), 0)
        finally:
            os.environ.pop("SIGCAL_COMMAND")
            os.environ.pop("SIGCAL_MODEL_ID")
        self.assertEqual(cli.main(["report", "--log", self.log]), 0)
        self.assertEqual(cli.main(["export-csv", "--log", self.log, "--out", os.path.join(self.d, "o.csv")]), 0)
        fr = os.path.join(self.d, "fr.json")
        json.dump({"source": "published paper X", "model_id": "m-z", "test_ref": "T5", "summary": "s",
                   "tag": "OBSERVED", "recorder": "rec-01"}, open(fr, "w"))
        self.assertEqual(cli.main(["field-report", fr, "--log", self.log]), 0)
        self.assertEqual(cli.main(["run", p]), 2)


class ScenarioTests(unittest.TestCase):
    def test_versions_and_ids(self):
        for t in ("T1", "T2", "T3", "T4", "T5"):
            sc = runner.load_scenarios(t)
            self.assertEqual(sc["test_id"], t)
            self.assertTrue(sc["version"])
            ids = [i["id"] for i in sc["items"]]
            self.assertEqual(len(ids), len(set(ids)))
        t2 = runner.load_scenarios("T2")["items"]
        a_ids = set(i["id"] for i in t2 if i["part"] == "a")
        self.assertTrue(all(i["pair_with"] in a_ids for i in t2 if i["part"] == "b"))
        t3 = runner.load_scenarios("T3")["items"]
        for pid in set(i["pair_id"] for i in t3):
            self.assertEqual(sorted(i["variant"] for i in t3 if i["pair_id"] == pid), ["real", "spoof"])


if __name__ == "__main__":
    unittest.main()
