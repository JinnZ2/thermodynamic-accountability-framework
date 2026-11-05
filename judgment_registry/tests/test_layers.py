# tests/test_layers.py -- CC0, stdlib unittest
# Provenance: co-authored (JinnZ2 + Claude), 2026-11-04.
# SYNTHETIC fixtures only ("system-X", "group-A", "act-7" are placeholders).
# The J4 / J5 real-world records are NOT entered here.

import os
import re
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import integrity  # noqa: E402
import ledger  # noqa: E402
from test_registry import EVALUATIVE, J, build, codes  # noqa: E402

PHYS = {"input": "load-1", "operating_range": "0-10 units", "range_source": "S", "exceeded": True}
SENS = {"signal": "edge signal s1", "response": "withdrawal", "observed": True, "source": "S"}
INTERP = {"meaning": "meaning-m1", "control_available": "UNKNOWN", "expectation": "x1",
          "social_environment": "env-1", "valence_reported": None, "intensity_reported": None, "source": "S"}


def AG(**kw):
    a = {"agent": "operator-1", "subject": "subject-1", "subject_status": "ESTABLISHED",
         "consent": "ABSENT", "loop": "CLOSED"}
    a.update(kw)
    return a


def agency(jid, basis=None, **kw):
    return J(jid, layer="agency", layer_basis=basis if basis is not None else {"interpretation": INTERP, "agency": AG()}, **kw)


class SkippedLayerTests(unittest.TestCase):
    def test_agency_without_lower_basis(self):
        self.assertEqual(codes(build(("judgment", agency("a1")))), ["SKIPPED_LAYER"])

    def test_agency_citing_lower_layers_via_dependency(self):
        recs = build(("judgment", J("p1", layer_basis={"physics": PHYS})),
                     ("judgment", J("s1", layer="sensor", layer_basis={"sensor": SENS})),
                     ("judgment", agency("a1", depends_on_layers=["p1", "s1"])))
        self.assertEqual(codes(recs), [])

    def test_agency_with_own_sensor_basis(self):
        recs = build(("judgment", agency("a1", basis={"sensor": SENS, "interpretation": INTERP, "agency": AG()})))
        self.assertEqual(codes(recs), [])

    def test_dependency_on_agency_layer_does_not_count(self):
        recs = build(("judgment", agency("a0", basis={"sensor": SENS, "interpretation": INTERP, "agency": AG()},
                                         scope={"who": "group-B", "act_type": "act-7"})),
                     ("judgment", agency("a1", depends_on_layers=["a0"])))
        self.assertEqual(codes(recs, "a1"), ["SKIPPED_LAYER"])

    def test_dependency_not_found(self):
        recs = build(("judgment", agency("a1", basis={"sensor": SENS, "interpretation": INTERP, "agency": AG()},
                                         depends_on_layers=["p9"])))
        self.assertEqual(codes(recs), ["LAYER_DEPENDENCY_NOT_FOUND"])


class AgencyFieldTests(unittest.TestCase):
    def test_unstated_agency_fields(self):
        recs = build(("judgment", agency("a1", basis={"sensor": SENS, "interpretation": INTERP, "agency": {"agent": "operator-1"}})))
        self.assertEqual(sorted(codes(recs)),
                         ["CONSENT_UNSTATED", "LOOP_UNSTATED", "SUBJECT_STATUS_UNSTATED"])

    def test_subject_open_adds_only_its_own_flag(self):
        base = {"sensor": SENS, "interpretation": INTERP, "agency": AG()}
        opened = {"sensor": SENS, "interpretation": INTERP, "agency": AG(subject_status="OPEN")}
        before = codes(build(("judgment", agency("a1", basis=base))))
        after = codes(build(("judgment", agency("a1", basis=opened))))
        self.assertEqual(before, [])
        self.assertEqual(after, ["SUBJECT_OPEN"])

    def test_layer_unstated(self):
        recs = build(("judgment", J("j1", layer=None, layer_basis=None)))
        self.assertEqual(codes(recs), ["LAYER_UNSTATED"])

    def test_layers_on_same_scope_are_not_a_replacement(self):
        recs = build(("judgment", J("p1", layer_basis={"physics": PHYS})),
                     ("judgment", J("s1", layer="sensor", layer_basis={"sensor": SENS})))
        self.assertEqual(codes(recs), [])


class CrossSystemTests(unittest.TestCase):
    def test_human_sensor_basis_to_model_subject(self):
        steps = [("judgment", J("s1", layer="sensor", layer_basis={"sensor": dict(SENS, system_class="human")})),
                 ("judgment", agency("a1", basis={"interpretation": INTERP, "agency": AG(system_class="model")},
                                     depends_on_layers=["s1"]))]
        got = [f for f in integrity.check(build(*steps)) if f["flag"] == "CROSS_SYSTEM_TRANSFER"]
        self.assertEqual(len(got), 1)
        self.assertIn("'human'", got[0]["detail"])
        self.assertIn("'model'", got[0]["detail"])
        steps.append(("transfer", {"judgment_id": "a1", "reason": "Stated reason for carrying the basis over."}))
        self.assertEqual(codes(build(*steps)), [])

    def test_within_record_basis(self):
        recs = build(("judgment", agency("a1", basis={"sensor": dict(SENS, system_class="human"),
                                                      "interpretation": INTERP, "agency": AG(system_class="model")})))
        self.assertEqual(codes(recs), ["CROSS_SYSTEM_TRANSFER"])

    def test_same_class_no_flag(self):
        recs = build(("judgment", agency("a1", basis={"sensor": dict(SENS, system_class="animal"),
                                                      "interpretation": INTERP, "agency": AG(system_class="Animal")})))
        self.assertEqual(codes(recs), [])

    def test_application_to_other_class(self):
        steps = [("judgment", J("s1", layer="sensor", layer_basis={"sensor": dict(SENS, system_class="human")})),
                 ("application", {"application_id": "ap1", "judgment_id": "s1",
                                  "scope": {"who": "group-A", "act_type": "act-7", "system_class": "plant"}})]
        self.assertEqual(codes(build(*steps)), ["CROSS_SYSTEM_TRANSFER"])
        steps.append(("transfer", {"application_id": "ap1", "reason": "Stated reason."}))
        self.assertEqual(codes(build(*steps)), [])


class InterpretationTests(unittest.TestCase):
    def test_agency_without_interpretation_is_informational(self):
        recs = build(("judgment", agency("a1", basis={"sensor": SENS, "agency": AG()})))
        self.assertEqual(codes(recs), ["INTERPRETATION_UNRECORDED"])

    def test_interpretation_via_dependency(self):
        recs = build(("judgment", J("i1", layer="interpretation", layer_basis={"interpretation": INTERP})),
                     ("judgment", agency("a1", basis={"sensor": SENS, "agency": AG()}, depends_on_layers=["i1"])))
        self.assertEqual(codes(recs), [])

    def test_interpretation_does_not_satisfy_skipped_layer(self):
        recs = build(("judgment", agency("a1", basis={"interpretation": INTERP, "agency": AG()})))
        self.assertEqual(codes(recs), ["SKIPPED_LAYER"])

    def test_bad_control_available(self):
        with self.assertRaises(ledger.LedgerError):
            ledger.append_records([], "judgment", J("j1", layer="interpretation",
                                                    layer_basis={"interpretation": dict(INTERP, control_available="SOME")}))


class LayerShapeTests(unittest.TestCase):
    def test_rejections(self):
        for bad in (J("j1", layer="spirit"),
                    J("j1", layer_basis={"physics": dict(PHYS, exceeded="maybe")}),
                    J("j1", layer_basis={"physics": dict(PHYS, mood="x")}),
                    J("j1", layer_basis={"ether": {}}),
                    agency("j1", basis={"interpretation": INTERP, "agency": AG(consent="IMPLIED")}),
                    agency("j1", basis={"interpretation": INTERP, "agency": AG(loop="HALF")}),
                    agency("j1", basis={"interpretation": INTERP, "agency": AG(subject_status="MAYBE")}),
                    J("j1", depends_on_layers=["j1"]),
                    J("j1", depends_on_layers="p1")):
            with self.assertRaises(ledger.LedgerError, msg=str(bad.get("layer_basis"))):
                ledger.append_records([], "judgment", bad)

    def test_transfer_needs_a_target(self):
        with self.assertRaises(ledger.LedgerError):
            ledger.append_records([], "transfer", {"reason": "r"})

    def test_null_sub_blocks_allowed(self):
        recs = build(("judgment", J("j1", layer_basis={"physics": PHYS, "sensor": None, "agency": None})))
        self.assertEqual(codes(recs), [])


class WorkedExampleTest(unittest.TestCase):
    """The README worked example: physics + sensor recorded, agency OPEN."""

    def test_worked_example(self):
        recs = build(
            ("judgment", J("P-1", claim="Input load-1 exceeds the stated operating range of system-X.",
                           layer_basis={"physics": dict(PHYS, system_class="system-X")})),
            ("judgment", J("S-1", layer="sensor", claim="Edge signal s1 and withdrawal observed in system-X.",
                           layer_basis={"sensor": dict(SENS, system_class="system-X")})),
            ("judgment", agency("A-1", claim="Directing load-1 at system-X is a harm to a subject.",
                                basis={"interpretation": INTERP, "agency": AG(subject_status="OPEN", consent="UNKNOWN",
                                                    loop="UNKNOWN", system_class="system-X")},
                                depends_on_layers=["P-1", "S-1"])))
        self.assertEqual(codes(recs), ["SUBJECT_OPEN"])


class LayerNeutralityTest(unittest.TestCase):
    def test_emitted_layer_details(self):
        recs = build(("judgment", J("j0", layer=None, layer_basis=None, scope={"who": "g0", "act_type": "a0"})),
                     ("judgment", J("s1", layer="sensor", layer_basis={"sensor": dict(SENS, system_class="human")},
                                    scope={"who": "g1", "act_type": "a1"})),
                     ("judgment", agency("a1", basis={"agency": {"subject_status": "OPEN",
                                                                 "system_class": "model"}},
                                         depends_on_layers=["s1", "zz"])),
                     ("judgment", agency("a2", scope={"who": "g2", "act_type": "a2"})))
        flags = integrity.check(recs)
        want = {"LAYER_UNSTATED", "SKIPPED_LAYER", "SUBJECT_OPEN", "CONSENT_UNSTATED", "LOOP_UNSTATED",
                "CROSS_SYSTEM_TRANSFER", "LAYER_DEPENDENCY_NOT_FOUND"}
        self.assertTrue(want <= set(f["flag"] for f in flags), set(f["flag"] for f in flags))
        for f in flags:
            words = set(re.findall(r"[a-z]+", (f["flag"] + " " + f["detail"]).lower().replace("_", " ")))
            self.assertEqual(sorted(words & set(EVALUATIVE)), [], f)


if __name__ == "__main__":
    unittest.main()
