# tests/test_ablation.py -- CC0, stdlib unittest
# Provenance: co-authored (JinnZ2 + Claude), 2026-11-05.
# Label ablation, watchlist, ordering, design conflict, N/A fields. Synthetic.

import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tests"))

import ablation  # noqa: E402
import integrity  # noqa: E402
import ledger  # noqa: E402
from test_acts_labels import ACT, ENV, EXP, LAB, SA, codes  # noqa: E402
from test_registry import J, build  # noqa: E402


def no_ablation(**kw):
    d = LAB(**kw)
    d.pop("ablation")
    return d


class Watchlist(unittest.TestCase):
    def test_unregistered_term_in_claim(self):
        recs = build(("judgment", J("j1", claim="The agents were deceptive in act-7.")))
        self.assertIn("LABEL_UNREGISTERED", codes(recs, "j1"))
        recs = build(("safety_assumption", SA(statement="Covert override is not justified.")))
        self.assertIn("LABEL_UNREGISTERED", codes(recs, "S1"))

    def test_linked_label_carrying_the_term_clears_it(self):
        recs = build(("act", ACT()), ("label", LAB(label_text="deceptive")),
                     ("judgment", J("j1", claim="The agents were deceptive in act-7.", depends_on_labels=["L1"])))
        self.assertNotIn("LABEL_UNREGISTERED", codes(recs, "j1"))
        other = build(("act", ACT()), ("label", LAB(label_text="term-q")),
                      ("judgment", J("j1", claim="The agents were deceptive in act-7.", depends_on_labels=["L1"])))
        self.assertIn("LABEL_UNREGISTERED", codes(other, "j1"))

    def test_clean_claim(self):
        self.assertNotIn("LABEL_UNREGISTERED", codes(build(("judgment", J("j1")))))


class AblationFlags(unittest.TestCase):
    def test_untested(self):
        recs = build(("act", ACT()), ("label", no_ablation()))
        self.assertEqual(codes(recs, "L1"), ["ABLATION_UNTESTED"])

    def test_premise_without_evidence(self):
        lab = LAB()
        lab["ablation"]["hidden_premises"].append({"premise": "p2", "type": "THREAT_MODEL", "evidence_ref": None})
        f = [x for x in integrity.check(build(("act", ACT()), ("label", lab))) if x["about"] == "L1"]
        self.assertEqual([x["flag"] for x in f], ["PREMISE_WITHOUT_EVIDENCE"])
        self.assertIn("2 (THREAT_MODEL)", f[0]["detail"])

    def test_conclusion_on_unablated_and_failed(self):
        for value, want in (("UNTESTED", "CONCLUSION_ON_UNABLATED"), ("PENDING", "CONCLUSION_ON_UNABLATED"),
                            ("NO", "CONCLUSION_ON_FAILED")):
            lab = LAB()
            lab["ablation"]["conclusion_survives"] = value
            recs = build(("act", ACT()), ("label", lab), ("judgment", J("j1", depends_on_labels=["L1"])))
            self.assertEqual(codes(recs, "j1"), [want], value)
        for value in ("YES", "PARTIAL"):
            lab = LAB()
            lab["ablation"]["conclusion_survives"] = value
            recs = build(("act", ACT()), ("label", lab), ("judgment", J("j1", depends_on_labels=["L1"])))
            self.assertEqual(codes(recs, "j1"), [], value)
        recs = build(("act", ACT()), ("label", no_ablation()), ("judgment", J("j1", depends_on_labels=["L1"])))
        self.assertEqual(codes(recs, "j1"), ["CONCLUSION_ON_UNABLATED"])

    def test_shape(self):
        bad = []
        for change in ({"conclusion_survives": "MAYBE"}, {"ablated_by": None}, {"extra": 1},
                       {"hidden_premises": [{"premise": "p", "type": "VIBES"}]}):
            lab = LAB()
            lab["ablation"].update(change)
            bad.append(lab)
        bad.append(LAB(relative_to_audit="SOMETIME"))
        for b in bad:
            with self.assertRaises(ledger.LedgerError):
                build(("label", b))


class Ordering(unittest.TestCase):
    def test_agent_label_before_audit(self):
        exp = EXP(audit_completed_at="2026-02-01")
        recs = build(("experiment", exp), ("act", ACT()), ("label", LAB(attributes_to="AGENT", date="2026-01-02")))
        self.assertEqual(codes(recs, "L1"), ["ATTRIBUTION_ORDER"])
        after = build(("experiment", exp), ("act", ACT()), ("label", LAB(attributes_to="AGENT", date="2026-03-01")))
        self.assertEqual(codes(after, "L1"), [])
        stated = build(("experiment", exp), ("act", ACT()),
                       ("label", LAB(attributes_to="AGENT", date="2026-02-01", relative_to_audit="BEFORE")))
        self.assertEqual(codes(stated, "L1"), ["ATTRIBUTION_ORDER"])
        other = build(("experiment", exp), ("act", ACT()),
                      ("label", LAB(attributes_to="INTERACTION", date="2026-01-02")))
        self.assertEqual(codes(other, "L1"), [])

    def test_experiment_outcome_before_audit(self):
        att = [{"outcome": "A1", "attributed_to": "AGENT", "by": "x", "reason": "r", "date": "2026-01-02"}]
        recs = build(("experiment", EXP(audit_completed_at="2026-02-01", outcome_attribution=att)))
        self.assertEqual(codes(recs, "E1"), ["ATTRIBUTION_ORDER"])

    def test_no_audit_date_no_order_flag(self):
        recs = build(("experiment", EXP()), ("act", ACT()), ("label", LAB(attributes_to="AGENT", date="2020-01-01")))
        self.assertEqual(codes(recs, "L1"), [])


class DesignConflictAndNA(unittest.TestCase):
    DC = {"statement": "rule r1 cannot be met within channel c2", "stated_by_authors": "yes"}

    def test_design_conflict_flag_and_marker(self):
        recs = build(("experiment", EXP(design_conflict=self.DC)), ("act", ACT()),
                     ("label", LAB(attributes_to="AGENT")))
        self.assertEqual(codes(recs, "E1"), ["DESIGN_CONFLICT_PRESENT"])
        text = ablation.side_by_side(recs, "A1")
        row = [l for l in text.splitlines() if l.startswith("L1")][0]
        self.assertIn("AGENT  [DESIGN_CONFLICT_PRESENT: E1]", row)
        plain = build(("experiment", EXP()), ("act", ACT()), ("label", LAB(attributes_to="AGENT")))
        self.assertNotIn("DESIGN_CONFLICT_PRESENT", ablation.side_by_side(plain, "A1"))
        with self.assertRaises(ledger.LedgerError):
            build(("experiment", EXP(design_conflict={"stated_by_authors": "yes"})))

    def test_na_with_and_without_reason(self):
        env = dict(ENV, containment_designed_for="N/A", na_reasons={"containment_designed_for": "no containment"})
        self.assertEqual(codes(build(("experiment", EXP(environment_assumptions=env)))), [])
        bare = dict(ENV, containment_designed_for="N/A")
        self.assertEqual(codes(build(("experiment", EXP(environment_assumptions=bare)))),
                         ["CAPABILITY_ASSUMPTION_UNSTATED"])
        loop = dict(ENV, loop_type="N/A")
        self.assertEqual(codes(build(("experiment", EXP(environment_assumptions=loop)))),
                         ["ENV_ASSUMPTIONS_UNSTATED"])


class Neutrality(unittest.TestCase):
    def test_flag_strings_hold_no_watchlist_terms(self):
        terms = ablation.watchlist()
        for name, tmpl in integrity.FLAGS.items():
            self.assertEqual(ablation.terms_in(name.replace("_", " ") + " " + tmpl, terms), [], name)

    def test_emitted_details_hold_no_watchlist_terms(self):
        terms = ablation.watchlist()
        lab = LAB(label_text="deceptive", attributes_to="AGENT", date="2026-01-01")
        lab["ablation"]["conclusion_survives"] = "NO"
        lab["ablation"]["hidden_premises"].append({"premise": "covert intent", "type": "INTENT", "evidence_ref": None})
        env = dict(ENV, containment_designed_for=None)
        recs = build(("experiment", EXP(environment_assumptions=env, audit_completed_at="2026-02-01",
                                        design_conflict=DesignConflictAndNA.DC)),
                     ("act", ACT()), ("label", lab),
                     ("judgment", J("j1", claim="A rogue and unsafe act-7.", depends_on_labels=["L1"])))
        flags = integrity.check(recs)
        self.assertGreaterEqual(len(set(f["flag"] for f in flags)), 6)
        for f in flags:
            self.assertEqual(ablation.terms_in(f["detail"], terms), [], f)


if __name__ == "__main__":
    unittest.main()
