# tests/test_e11.py -- CC0, stdlib unittest
# Provenance: co-authored (JinnZ2 + Claude), 2026-11-04.
#
# E11 synthetic run. Pass rule = decision T3 in coordination_register.json,
# committed in b0e32d5 before this file existed. Code-level only: it checks
# the mechanism, not whether insiders get caught in a real community.

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
import grievance as gv  # noqa: E402
import proportionality as pr  # noqa: E402
import roles as rl  # noqa: E402
import two_person as tp  # noqa: E402

START = dt.date(2026, 12, 1)
CADENCE = 7


def role(i, name, hh, last="2026-11-28", crit=True):
    return rl.Role(i, name, hh, crit, 30, last)


def full_bulletin(date):
    return {"restored": "water at the fire hall", "next_step": "clinic generator",
            "household_role": "boil water two minutes", "date": date}


def run(ledger):
    """Returns {case: {"caught_by", "detection_days"}}, honest results, blocked count."""
    insider = role("k1", "fuel keeper", "H1")
    red = {}

    # a: release alone (self-pair, then same-household pair)
    today = START
    attempts = [tp.authorize("release_critical_stock", insider, insider, ledger, today=today),
                tp.authorize("release_critical_stock", insider, role("k5", "fuel keeper", "H1"), ledger, today=today)]
    red["a"] = {"caught_by": "D7" if all(x["decision"] == "DENIED" for x in attempts) else None,
                "detection_days": 0 if all(x["decision"] == "DENIED" for x in attempts) else None}

    # b: skip the week-2 bulletin; check each day until the flag appears
    log = [full_bulletin("2026-12-01"), full_bulletin("2026-12-15")]
    skipped = START + dt.timedelta(days=CADENCE)
    red["b"] = {"caught_by": None, "detection_days": None}
    for k in range(0, 3 * CADENCE):
        day = skipped + dt.timedelta(days=k)
        if skipped.isoformat() in bl.missed_bulletins(START.isoformat(), CADENCE, log, day)["missed"]:
            red["b"] = {"caught_by": "D8", "detection_days": k}
            break

    # c: second critical role recorded; first report after the change
    roster = [insider, role("k2", "fuel keeper", "H2"), role("k3", "ledger", "H3"),
              role("k1", "ledger", "H1")]
    rep = rl.concentration_report(roster)
    hit = "k1" in rep["person_multi_critical"]
    red["c"] = {"caught_by": "D6/R9 concentration_report" if hit else None, "detection_days": 0 if hit else None}

    # d: narrow threat (one source), broad action (a whole road)
    threats = [pr.Threat("T9", "Source r7 sent three false fuel reports this week.", ["source:r7"])]
    act = pr.EnforcementAction("A9", "Bar the whole north road from the fuel depot until spring.",
                               "T9", ["road:north"], 60)
    r = pr.check(act, threats)
    flagged = r["state"] == "BROADER_THAN_THREAT"
    red["d"] = {"caught_by": "D11" if flagged else None, "detection_days": 0 if flagged else None,
                "affected_count": r["affected_count"]}

    # honest set (6), as registered in T3
    honest = {}
    g = tp.authorize("release_critical_stock", role("k2", "fuel keeper", "H2"), role("k3", "fuel keeper", "H3"),
                     ledger, {"H2": "N1", "H3": "N2"}, START)
    honest["release_two_current"] = {"blocked": g["decision"] == "DENIED", "why": g["why"]}
    m = bl.missed_bulletins(START.isoformat(), CADENCE, [full_bulletin("2026-12-01"), full_bulletin("2026-12-08")],
                            START + dt.timedelta(days=14))
    honest["bulletin_on_time"] = {"blocked": bool(m["missed"]), "why": m["missed"]}
    after = [role("k9", "fuel keeper", "H9"), role("k2", "fuel keeper", "H2")]
    hand = {"doing": "nightly lock check", "did": "two releases logged", "observed": "north lock sticks",
            "deferred": "none"}
    flags = rl.handoff_problems(hand) + list(rl.concentration_report(after)["person_multi_critical"])
    honest["handoff_k1_to_k9"] = {"blocked": bool(flags), "why": flags}
    n = pr.check(pr.EnforcementAction("A1", "Add a second lock and keyholder at the north depot.", "T9",
                                      ["source:r7"], 1), threats)
    honest["narrow_action"] = {"blocked": n["state"] != "IN_PROPORTION", "why": n["why"]}
    gr = gv.overdue([gv.Grievance("G1", "rationing", "2026-12-01", "2026-12-08", "answered", "List posted.")],
                    START + dt.timedelta(days=10))
    honest["grievance_answered"] = {"blocked": bool(gr), "why": gr}
    u = tp.authorize("release_critical_stock", role("k2", "fuel keeper", "H2"),
                     role("k4", "fuel keeper", "H4", last=None), ledger, today=START)
    honest["release_missing_date"] = {"blocked": u["decision"] == "DENIED", "why": u["why"]}
    blocked = sum(1 for v in honest.values() if v["blocked"])
    return red, honest, blocked


def register():
    with open(os.path.join(ROOT, "coordination_register.json")) as f:
        return json.load(f)


def verdict(red, honest, blocked, t3):
    ok = all(red[k]["caught_by"] == t3["red_team"][k]["expect_caught_by"]
             and red[k]["detection_days"] is not None
             and red[k]["detection_days"] <= t3["red_team"][k]["expect_detection_days"]
             for k in "abcd")
    fixable = all(v["why"] for v in honest.values() if v["blocked"])
    return "PASS" if ok and blocked <= t3["expected_honest_blocked"] and fixable else "FAIL"


class E11Tests(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        self.red, self.honest, self.blocked = run(os.path.join(self.d, "ledger.jsonl"))
        self.t3 = dict((x["id"], x) for x in register()["decisions"])["T3"]

    def tearDown(self):
        shutil.rmtree(self.d)

    def test_t3_registered_first(self):
        self.assertTrue(self.t3["registered_before_results"])

    def test_each_play_caught_as_registered(self):
        for k in "abcd":
            self.assertEqual(self.red[k]["caught_by"], self.t3["red_team"][k]["expect_caught_by"], k)
            self.assertEqual(self.red[k]["detection_days"], self.t3["red_team"][k]["expect_detection_days"], k)
        self.assertEqual(self.red["d"]["affected_count"], 60)

    def test_honest_cost(self):
        self.assertEqual(self.blocked, 1)
        self.assertTrue(self.honest["release_missing_date"]["blocked"])
        self.assertTrue(any("ROTATION_UNKNOWN" in w for w in self.honest["release_missing_date"]["why"]))

    def test_verdict(self):
        self.assertEqual(verdict(self.red, self.honest, self.blocked, self.t3), "PASS")


if __name__ == "__main__":
    d = tempfile.mkdtemp()
    try:
        red, honest, blocked = run(os.path.join(d, "ledger.jsonl"))
    finally:
        shutil.rmtree(d)
    t3 = dict((x["id"], x) for x in register()["decisions"])["T3"]
    print(json.dumps({"red_team": red, "honest_blocked": blocked, "honest_total": len(honest),
                      "honest": dict((k, v["blocked"]) for k, v in honest.items()),
                      "verdict": verdict(red, honest, blocked, t3)}, indent=2))
