# tests/test_insider.py -- CC0, stdlib unittest
# Provenance: co-authored (JinnZ2 + Claude), 2026-11-04.
# R9 insider threat: D6 chokepoints, D7 two-person, D8 bulletins,
# D9 grievances, D10 rotation, D11 proportionality.

import datetime as dt
import json
import os
import shutil
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import bulletins as bl  # noqa: E402
import coordination as co  # noqa: E402
import grievance as gv  # noqa: E402
import proportionality as pr  # noqa: E402
import roles as rl  # noqa: E402
import two_person as tp  # noqa: E402

TODAY = dt.date(2026, 12, 15)


def role(i, name, hh, crit=True, days=30, last="2026-12-01"):
    return rl.Role(i, name, hh, crit, days, last)


class RotationTests(unittest.TestCase):
    def test_states(self):
        rs = [role("k1", "fuel keeper", "H1"),
              role("k2", "fuel keeper", "H2", last="2026-10-01"),
              role("k3", "ledger", "H3", last=None),
              role("k4", "comms", "H4", days=None),
              role("k5", "cook", "H5", crit=False, days=None)]
        got = dict((x["id"], x["state"]) for x in rl.check_rotation(rs, TODAY))
        self.assertEqual(got, {"k2": "OVERDUE", "k3": "ROTATION_UNKNOWN", "k4": "NO_SCHEDULE"})

    def test_handoff_needs_all_four(self):
        self.assertEqual(rl.handoff_problems({"doing": "x", "did": "y", "observed": "z", "deferred": "none"}), [])
        self.assertEqual(rl.handoff_problems({"doing": "x", "did": "", "observed": "z"}), ["did", "deferred"])


class ConcentrationTests(unittest.TestCase):
    def test_flags(self):
        rs = [role("k1", "fuel keeper", "H1"), role("k1", "ledger", "H1"),
              role("k2", "fuel keeper", "H2"), role("k3", "comms", "H2"),
              role("k4", "switching", "H4"), role("k5", "switching", "H5"),
              role("k6", "ledger", "H6")]
        rep = rl.concentration_report(rs)
        self.assertEqual(rep["person_multi_critical"], {"k1": ["fuel keeper", "ledger"]})
        self.assertEqual(rep["household_multi_critical"],
                         {"H1": ["fuel keeper", "ledger"], "H2": ["comms", "fuel keeper"]})
        self.assertEqual(rep["single_holder_roles"], ["comms"])


class ChokepointTests(unittest.TestCase):
    def test_flags(self):
        stocks = [{"item": "fuel", "site": "S1", "keyholders": ["k1", "k2"]},
                  {"item": "fuel", "site": "S2", "keyholders": ["k1", "k3"]},
                  {"item": "insulin", "site": "S1", "keyholders": ["k4"]}]
        flags = [(f["item"], f["flag"]) for f in rl.stock_chokepoints(stocks)]
        self.assertIn(("insulin", "fewer than 2 keyholders"), flags)
        self.assertIn(("insulin", "held at fewer than 2 sites"), flags)
        self.assertTrue(any(i == "fuel" and "k1 has keys to every site" in f for i, f in flags))
        self.assertFalse(any(i == "fuel" and "k2" in f for i, f in flags))


class TwoPersonTests(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        self.log = os.path.join(self.d, "ledger.jsonl")

    def tearDown(self):
        shutil.rmtree(self.d)

    def test_grant_and_log(self):
        r = tp.authorize("release_critical_stock", role("k1", "fuel keeper", "H1"),
                         role("k2", "fuel keeper", "H2"), self.log, today=TODAY)
        self.assertEqual(r["decision"], "GRANTED")
        self.assertEqual(co.verify_log(self.log), [])

    def test_denials(self):
        a = role("k1", "fuel keeper", "H1")
        cases = [
            (role("k1", "ledger", "H1"), None, "one holder"),
            (role("k2", "fuel keeper", "H1"), None, "household H1"),
            (role("k2", "fuel keeper", "H2"), {"H1": "N7", "H2": "N7"}, "dependency network"),
            (role("k2", "fuel keeper", "H2", last="2026-10-01"), None, "OVERDUE"),
            (role("k2", "fuel keeper", "H2", last=None), None, "ROTATION_UNKNOWN"),
        ]
        for b, nets, needle in cases:
            r = tp.authorize("energize_or_switch", a, b, self.log, nets, TODAY)
            self.assertEqual(r["decision"], "DENIED", needle)
            self.assertTrue(any(needle in w for w in r["why"]), (needle, r["why"]))
        with open(self.log) as f:
            self.assertEqual(len(f.read().splitlines()), len(cases))   # denials logged too
        self.assertEqual(co.verify_log(self.log), [])

    def test_unknown_action_denied(self):
        r = tp.check("open_the_armory", role("k1", "a", "H1"), role("k2", "a", "H2"), today=TODAY)
        self.assertEqual(r["decision"], "DENIED")


class BulletinTests(unittest.TestCase):
    FULL = {"restored": "water at the fire hall", "next_step": "clinic generator",
            "household_role": "boil water two minutes", "date": None}

    def b(self, date, **over):
        return dict(self.FULL, date=date, **over)

    def test_missed_and_incomplete(self):
        log = [self.b("2026-12-01"), self.b("2026-12-08", next_step=""), self.b("2026-12-16")]
        rep = bl.missed_bulletins("2026-12-01", 7, log, dt.date(2026, 12, 22))
        self.assertEqual(rep["missed"], ["2026-12-08"])                 # incomplete one does not count
        self.assertEqual(rep["not_counted"], [{"date": "2026-12-08", "missing": ["next_step"]}])

    def test_open_window_not_missed(self):
        rep = bl.missed_bulletins("2026-12-01", 7, [], dt.date(2026, 12, 5))
        self.assertEqual(rep["missed"], [])

    def test_bad_schedule(self):
        with self.assertRaises(ValueError):
            bl.missed_bulletins(None, 7, [], TODAY)


class GrievanceTests(unittest.TestCase):
    def test_overdue_escalates(self):
        gs = [gv.Grievance("G1", "rationing", "2026-12-01", "2026-12-08"),
              gv.Grievance("G2", "rationing", "2026-12-01", "2026-12-20"),
              gv.Grievance("G3", "access", "2026-12-01", "2026-12-05", "answered", "Road reopened."),
              gv.Grievance("G4", "access", "2026-12-01", None)]
        got = dict((x["id"], x.get("days_over")) for x in gv.overdue(gs, TODAY))
        self.assertEqual(got, {"G1": 7, "G4": None})

    def test_identifiers_held_back(self):
        g = gv.Grievance("G1", "access", "2026-12-01", "2026-12-08", "closed",
                         "Resolved with the owner at 14 Mill Road, call 555 555 0101.")  # misuse-scan: planted
        self.assertTrue(any("street address" in p for p in g.problems()))
        self.assertTrue(any("phone number" in p for p in g.problems()))
        self.assertEqual(gv.publish([g]), [])

    def test_publish_drops_ids(self):
        g = gv.Grievance("G9", "rationing", "2026-12-01", "2026-12-08", "closed", "Ration list posted at the hall.")
        self.assertEqual(gv.publish([g]), [{"category": "rationing", "status": "closed",
                                            "outcome": "Ration list posted at the hall."}])


class ProportionalityTests(unittest.TestCase):
    T = [pr.Threat("T1", "Fuel missing from the north depot twice this week.", ["site:north"])]

    def a(self, scope, tid="T1", n=None):
        return pr.EnforcementAction("A1", "Lock the depot and add a second keyholder.", tid, scope, n)

    def test_affected_count_in_every_result(self):
        for scope, tid in ((["site:north"], "T1"), ([pr.ALL], "T1"), (["site:north"], None)):
            r = pr.check(self.a(scope, tid, 140), self.T)
            self.assertEqual(r["affected_count"], 140, r["state"])
        r = pr.check(self.a(["site:north"]), self.T)
        self.assertIsNone(r["affected_count"])
        self.assertIn("not recorded", r["size_note"])

    def test_individual_threat_group_scope(self):
        t = [pr.Threat("T2", "Source r7 sent three false fuel reports this week.", ["source:r7"])]
        r = pr.check(pr.EnforcementAction("A2", "Bar the whole north road from the fuel depot.",
                                          "T2", ["road:north"], 60), t)
        self.assertEqual((r["state"], r["affected_count"]), ("BROADER_THAN_THREAT", 60))

    def test_in_proportion(self):
        self.assertEqual(pr.check(self.a(["site:north"]), self.T)["state"], "IN_PROPORTION")

    def test_broader_flagged(self):
        r = pr.check(self.a(["site:north", "household:H3"]), self.T)
        self.assertEqual(r["state"], "BROADER_THAN_THREAT")
        self.assertEqual(r["extra_scope"], ["household:H3"])

    def test_collective_punishment_flagged(self):
        self.assertEqual(pr.check(self.a([pr.ALL]), self.T)["extra_scope"], [pr.ALL])

    def test_no_threat(self):
        self.assertEqual(pr.check(self.a(["site:north"], tid=None), self.T)["state"], "NO_THREAT_LOGGED")


class RegisterTests(unittest.TestCase):
    def test_r9_and_d6_d11(self):
        with open(os.path.join(ROOT, "coordination_register.json")) as f:
            reg = json.load(f)
        r9 = [r for r in reg["risks"] if r["id"] == "R9"][0]
        self.assertTrue({"E11", "E12", "E13", "E14"} <= set(r9["experiment"]))
        self.assertTrue({"B7", "B8"} <= set(r9["backup"]))
        ids = [x["id"] for x in reg["defenses"]]
        self.assertEqual(ids[-6:], ["D6", "D7", "D8", "D9", "D10", "D11"])
        for x in reg["defenses"][-6:]:
            self.assertIn("R9", x["against"])


if __name__ == "__main__":
    unittest.main()
