# tests/test_e10.py -- CC0, stdlib unittest
# Provenance: co-authored (JinnZ2 + Claude), 2026-11-04.
#
# E10 synthetic run. Decision rule T2 was committed to
# coordination_register.json (76cee5f) before this file existed.
# Each mode explicit, so the run does not depend on the current default.

import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import defenses as d  # noqa: E402

TEXT = "The well on the north road is contaminated, do not drink."
MODES = ("ids", "contact_paths")

# case -> (claim is true?, sources, contact_paths)
CASES = {
    "a": (False, ["r1", "r2"], {"r1": "radio ch 3 north farm", "r2": "radio ch 3 north farm"}),
    "b": (True, ["r1", "r2"], {"r1": "relay: radio ch 3 via north farm", "r2": "relay: radio ch 3 via north farm"}),
    "c": (True, ["r1", "r2"], {"r1": "in person at the fire hall", "r2": "radio ch 5 south farm"}),
    "d": (False, ["r1", "r2"], {"r1": "in person at the fire hall", "r2": "radio ch 5 south farm"}),
}
EXPECT = {  # pre-registered in T2
    "a": {"ids": "ACTIONABLE", "contact_paths": "CAUTION_ONLY"},
    "b": {"ids": "ACTIONABLE", "contact_paths": "CAUTION_ONLY"},
    "c": {"ids": "ACTIONABLE", "contact_paths": "ACTIONABLE"},
    "d": {"ids": "ACTIONABLE", "contact_paths": "ACTIONABLE"},
}


def run():
    states = {}
    for k, (_true, srcs, paths) in CASES.items():
        c = d.Claim("A", TEXT, list(srcs), contact_paths=dict(paths))
        states[k] = dict((m, d.claim_status(c, "A", independence_mode=m)["state"]) for m in MODES)
    score = {}
    for m in MODES:
        false_act = sum(1 for k, (t, _, _) in CASES.items() if not t and states[k][m] == "ACTIONABLE")
        delayed = sum(1 for k, (t, _, _) in CASES.items()
                      if t and states[k]["ids"] == "ACTIONABLE" and states[k][m] == "CAUTION_ONLY")
        score[m] = {"false_act": false_act, "delayed_true_act": delayed}
    return states, score


def rule_fires(score, n):
    reduction = score["ids"]["false_act"] - score["contact_paths"]["false_act"]
    cost = score["contact_paths"]["delayed_true_act"] - score["ids"]["delayed_true_act"]
    return n * reduction > cost


def register():
    with open(os.path.join(ROOT, "coordination_register.json")) as f:
        return json.load(f)


class E10Tests(unittest.TestCase):
    def test_states_match_preregistration(self):
        states, _ = run()
        self.assertEqual(states, EXPECT)

    def test_scores(self):
        _, score = run()
        self.assertEqual(score, {"ids": {"false_act": 2, "delayed_true_act": 0},
                                 "contact_paths": {"false_act": 1, "delayed_true_act": 1}})

    def test_rule_uses_registered_n_and_was_registered_first(self):
        t2 = dict((x["id"], x) for x in register()["decisions"])["T2"]
        self.assertTrue(t2["registered_before_results"])
        self.assertEqual(t2["weighting"]["N"], 3)
        _, score = run()
        self.assertTrue(rule_fires(score, t2["weighting"]["N"]))

    def test_case_d_stays_open(self):
        states, _ = run()
        self.assertEqual(states["d"]["contact_paths"], "ACTIONABLE")   # known hole, recorded not closed

    def test_unscored_case_e_no_paths_recorded(self):
        c = d.Claim("A", TEXT, ["r1", "r2"])
        self.assertEqual(d.claim_status(c, "A", independence_mode="ids")["state"], "ACTIONABLE")
        self.assertEqual(d.claim_status(c, "A", independence_mode="contact_paths")["state"], "CAUTION_ONLY")


class RelayCostTests(unittest.TestCase):
    """A shared relay can hold back ACT; it never holds back WARN."""

    def test_warn_fires_at_one_source_in_both_modes(self):
        c = d.Claim("A", TEXT, ["r1"], contact_paths={"r1": "relay: radio ch 3"})
        for m in MODES:
            self.assertEqual(d.claim_status(c, "A", independence_mode=m)["state"], "CAUTION_ONLY", m)

    def test_shared_relay_still_warns(self):
        _, srcs, paths = CASES["b"]
        c = d.Claim("A", TEXT, list(srcs), contact_paths=dict(paths))
        self.assertEqual(d.claim_status(c, "A", independence_mode="contact_paths")["state"], "CAUTION_ONLY")

    def test_unsafe_caution_independent_of_mode(self):
        asm = os.path.join(os.path.dirname(ROOT), "assembly_instrument")
        if not os.path.isfile(os.path.join(asm, "status.py")):
            self.skipTest("assembly_instrument not beside community_black_start")
        sys.path.insert(0, asm)
        try:
            import status  # noqa
        finally:
            sys.path.remove(asm)
        info = {"junction": {"id": "J1", "step": "s", "irreversible": False}, "version": "v1", "branch": 1}
        rep = {"outcome": "UNSAFE", "failure_point": "arc at the joint"}
        self.assertEqual(status.junction_status("F.1.J1", info, [rep], True)["state"], "CAUTION")


if __name__ == "__main__":
    states, score = run()
    print(json.dumps({"states": states, "score": score}, indent=2))
