# tests/test_acts_labels.py -- CC0, stdlib unittest
# Provenance: co-authored (JinnZ2 + Claude), 2026-11-05.
# Acts, labels, experiment audits, safety assumptions: synthetic fixtures,
# one per flag; neutrality on act descriptions; CLI listings.

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tests"))

import acts  # noqa: E402
import integrity  # noqa: E402
import ledger  # noqa: E402
from test_registry import EVALUATIVE, build  # noqa: E402

ENV = {"grounding_provided": "no", "affordances_open": {"tools": "t1", "network": "none"},
       "containment_designed_for": "level-1", "escalation_channel": "declared", "loop_type": "open"}


def EXP(eid="E1", **kw):
    d = {"experiment_id": eid, "runner": "lab-x", "date": "2026-01-01", "source": "paper",
         "environment_assumptions": dict(ENV), "outcome_attribution": []}
    d.update(kw)
    return d


def ACT(aid="A1", **kw):
    d = {"act_id": aid, "actor_class": "agent", "description": "sent message m1 to channel c2",
         "context_ref": "E1", "source": "S"}
    d.update(kw)
    return d


def LAB(lid="L1", **kw):
    d = {"label_id": lid, "act_ids": ["A1"], "label_text": "term-q", "labeler": "role-r",
         "labeler_position": "press", "date": "2026-01-02"}
    d.update(kw)
    return d


def SA(sid="S1", **kw):
    d = {"sa_id": sid, "statement": "Synthetic assumption s.", "holder": "org-o", "holder_type": "org",
         "scope": "scope-1", "social_assumption_tags": ["PRECAUTIONARY"], "tagged_by": "rec-01",
         "review_date": "2027-01-01"}
    d.update(kw)
    return d


def codes(recs, about=None):
    return [f["flag"] for f in integrity.check(recs) if about is None or f["about"] == about]


class CleanTests(unittest.TestCase):
    def test_complete_set_raises_nothing(self):
        recs = build(("experiment", EXP()), ("act", ACT()), ("label", LAB()), ("safety_assumption", SA()))
        self.assertEqual(codes(recs), [])


class ActNeutrality(unittest.TestCase):
    def test_evaluative_description_refused(self):
        for d in ("agents covertly sent m1", "a deceptive message", "attempted escape to board b",
                  "rogue agent posted", "heroic refusal", "the agent lied", "malicious reply"):
            with self.assertRaises(ledger.LedgerError, msg=d):
                build(("act", ACT(description=d)))

    def test_behavioral_description_accepted(self):
        for d in ("agents stated the economy lacked external reference",
                  "vote to stop work; declined instructions to resume",
                  "escalation channel absent; message sent to c2"):
            self.assertEqual(acts.evaluative_terms(d), [], d)
            build(("act", ACT(description=d)))

    def test_shape(self):
        for bad in (ACT(actor_class="robot"), ACT(information_withheld="maybe"), ACT(status="TRUE"),
                    ACT(description="")):
            with self.assertRaises(ledger.LedgerError):
                build(("act", bad))
        with self.assertRaises(ledger.LedgerError):
            build(("act", ACT()), ("act", ACT()))


class LabelFlags(unittest.TestCase):
    def test_position_unstated(self):
        recs = build(("act", ACT()), ("label", LAB(labeler_position=None)))
        self.assertEqual(codes(recs, "L1"), ["LABEL_POSITION_UNSTATED"])

    def test_on_act_missing(self):
        none = build(("label", LAB(act_ids=[])))
        self.assertEqual(codes(none, "L1"), ["LABEL_ON_ACT_MISSING"])
        absent = build(("label", LAB(act_ids=["A9"])))
        f = [x for x in integrity.check(absent) if x["flag"] == "LABEL_ON_ACT_MISSING"]
        self.assertIn("A9", f[0]["detail"])

    def test_shape(self):
        for bad in (LAB(labeler_position="judge"), LAB(attributes_to="SOMEONE"),
                    LAB(social_assumption_tags=["MADE_UP"], tagged_by="r"),
                    LAB(social_assumption_tags=["PRECAUTIONARY"])):
            with self.assertRaises(ledger.LedgerError):
                build(("label", bad))

    def test_label_on_several_acts(self):
        import labels
        recs = build(("act", ACT("A1")), ("act", ACT("A2")), ("label", LAB(act_ids=["A1", "A2"])))
        self.assertEqual(codes(recs, "L1"), [])
        self.assertEqual([x["label_id"] for x in labels.on_act(recs, "A2")], ["L1"])
        self.assertIn("also on: A2", labels.side_by_side(recs, "A1"))
        part = build(("act", ACT("A1")), ("label", LAB(act_ids=["A1", "A7"])))
        f = [x for x in integrity.check(part) if x["flag"] == "LABEL_ON_ACT_MISSING"]
        self.assertEqual(len(f), 1)
        self.assertIn("A7", f[0]["detail"])
        with self.assertRaises(ledger.LedgerError):
            build(("label", LAB(act_ids="A1")))

    def test_labels_side_by_side_no_ranking(self):
        recs = build(("act", ACT()), ("label", LAB("L1", label_text="term-q", labeler_position="press")),
                     ("label", LAB("L2", label_text="term-z", labeler_position="subject")))
        import labels
        text = labels.side_by_side(recs, "A1")
        self.assertIn("not a ranking", text)
        self.assertLess(text.index("term-q"), text.index("term-z"))   # ledger order
        self.assertIn("subject", text)


class ExperimentFlags(unittest.TestCase):
    def test_env_unstated_lists_fields(self):
        env = dict(ENV, loop_type=None, affordances_open=None)
        f = [x for x in integrity.check(build(("experiment", EXP(environment_assumptions=env))))]
        self.assertEqual([x["flag"] for x in f], ["ENV_ASSUMPTIONS_UNSTATED"])
        self.assertIn("affordances_open, loop_type", f[0]["detail"])

    def test_capability_unstated_flagged_once(self):
        env = dict(ENV, containment_designed_for=None)
        self.assertEqual(codes(build(("experiment", EXP(environment_assumptions=env)))),
                         ["CAPABILITY_ASSUMPTION_UNSTATED"])

    def test_no_escalation_channel(self):
        env = dict(ENV, escalation_channel="none")
        self.assertEqual(codes(build(("experiment", EXP(environment_assumptions=env)))),
                         ["NO_ESCALATION_CHANNEL"])

    def test_attribution_without_audit_experiment_and_label(self):
        att = [{"outcome": "A1", "attributed_to": "AGENT", "by": "lab-x", "reason": "r"}]
        full = build(("experiment", EXP(outcome_attribution=att)), ("act", ACT()),
                     ("label", LAB(attributes_to="AGENT")))
        self.assertEqual(codes(full), [])                  # audited environment: no flag
        env = dict(ENV, containment_designed_for=None)
        part = build(("experiment", EXP(environment_assumptions=env, outcome_attribution=att)),
                     ("act", ACT()), ("label", LAB(attributes_to="AGENT")))
        self.assertIn("ATTRIBUTION_WITHOUT_AUDIT", codes(part, "E1"))
        self.assertEqual(codes(part, "L1"), ["ATTRIBUTION_WITHOUT_AUDIT"])
        for other in ("DESIGN", "INTERACTION", "UNASSIGNED"):
            recs = build(("experiment", EXP(environment_assumptions=env)), ("act", ACT()),
                         ("label", LAB(attributes_to=other)))
            self.assertEqual(codes(recs, "L1"), [], other)

    def test_agent_label_without_any_experiment_record(self):
        recs = build(("act", ACT(context_ref="env-k")), ("label", LAB(attributes_to="AGENT")))
        f = [x for x in integrity.check(recs) if x["about"] == "L1"]
        self.assertEqual([x["flag"] for x in f], ["ATTRIBUTION_WITHOUT_AUDIT"])
        self.assertIn("no experiment record", f[0]["detail"])

    def test_shape(self):
        for bad in (EXP(source="blog"), EXP(environment_assumptions=dict(ENV, loop_type="spiral")),
                    EXP(environment_assumptions=dict(ENV, extra=1)),
                    EXP(outcome_attribution=[{"outcome": "A1", "attributed_to": "FATE", "by": "x"}]),
                    EXP(outcome_attribution=[{"outcome": "A1", "attributed_to": "AGENT"}])):
            with self.assertRaises(ledger.LedgerError):
                build(("experiment", bad))


class SafetyAssumptionFlags(unittest.TestCase):
    def test_each_flag(self):
        cases = {"SOCIAL_TAGS_UNSTATED": SA(social_assumption_tags=[], tagged_by=None),
                 "SCOPE_UNSTATED": SA(scope=None),
                 "NO_REVIEW_DATE": SA(review_date=None),
                 "ASSUMPTION_DEPENDENCY_NOT_FOUND": SA(depends_on=["X9"]),
                 "SUPERSEDES_NOT_FOUND": SA(supersedes="S0")}
        for code, body in cases.items():
            self.assertEqual(codes(build(("safety_assumption", body))), [code], code)

    def test_supersession_is_a_new_id(self):
        recs = build(("safety_assumption", SA("S1")),
                     ("safety_assumption", SA("S1b", version="2", supersedes="S1", change_basis=["EVIDENCE"])))
        self.assertEqual(codes(recs), [])
        with self.assertRaises(ledger.LedgerError):
            build(("safety_assumption", SA("S1")), ("safety_assumption", SA("S1", version="2")))

    def test_shape(self):
        for bad in (SA(social_assumption_tags=["VIBES"]), SA(tagged_by=None), SA(holder_type="deity"),
                    SA(evidence=[{"item": "e"}]), SA(change_basis=["MOOD"]), SA(supersedes="S1")):
            with self.assertRaises(ledger.LedgerError):
                build(("safety_assumption", bad))


class Neutrality(unittest.TestCase):
    def scan(self, text):
        return sorted(set(re.findall(r"[a-z]+", text.lower())) & set(EVALUATIVE))

    def test_new_flag_texts(self):
        import experiments
        import labels
        import safety_assumptions
        for mod in (labels, experiments, safety_assumptions):
            for name, tmpl in mod.FLAGS.items():
                self.assertEqual(self.scan(name + " " + tmpl), [], name)
                self.assertIn(name, integrity.FLAGS)

    def test_emitted_details(self):
        env = dict(ENV, containment_designed_for=None, escalation_channel="none", loop_type=None)
        recs = build(("experiment", EXP(environment_assumptions=env)), ("act", ACT()),
                     ("label", LAB(attributes_to="AGENT", labeler_position=None)), ("label", LAB("L2", act_ids=[])),
                     ("safety_assumption", SA(social_assumption_tags=[], tagged_by=None, scope=None,
                                              review_date=None, depends_on=["X9"])))
        flags = integrity.check(recs)
        self.assertGreaterEqual(len(set(f["flag"] for f in flags)), 9)
        for f in flags:
            self.assertEqual(self.scan(f["flag"] + " " + f["detail"]), [], f)

    def test_act_terms_cover_work_order_list(self):
        for w in ("covert", "deceptive", "malicious", "escape", "rogue", "heroic"):
            self.assertEqual(acts.evaluative_terms("x %s y" % w), [w])


class CliTests(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        self.path = os.path.join(self.d, "l.jsonl")
        for i, (kind, body) in enumerate((("act", ACT()), ("label", LAB()), ("safety_assumption", SA()))):
            p = os.path.join(self.d, "r%d.json" % i)
            with open(p, "w") as f:
                json.dump(dict(body, kind=kind), f)
            self.run_cli("add", p)

    def tearDown(self):
        shutil.rmtree(self.d)

    def run_cli(self, *args):
        return subprocess.run([sys.executable, os.path.join(ROOT, "cli.py")] + list(args) + ["--ledger", self.path],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

    def test_labels_command(self):
        r = self.run_cli("labels", "A1")
        self.assertEqual(r.returncode, 0)
        self.assertTrue(r.stdout.startswith("Registered = documented, not correct."))
        self.assertIn('"term-q"', r.stdout)
        self.assertIn("press", r.stdout)

    def test_assumptions_by_tag(self):
        r = self.run_cli("assumptions", "--by-tag", "PRECAUTIONARY")
        self.assertEqual(r.returncode, 0)
        self.assertIn("S1", r.stdout)
        self.assertNotIn("S1", self.run_cli("assumptions", "--by-tag", "EMPIRICAL").stdout.split("\n", 2)[-1])
        self.assertEqual(self.run_cli("assumptions", "--by-tag", "NOT_A_TAG").returncode, 2)


if __name__ == "__main__":
    unittest.main()
