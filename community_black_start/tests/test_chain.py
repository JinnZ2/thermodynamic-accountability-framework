# tests/test_chain.py -- CC0, stdlib unittest
# Provenance: co-authored (Kavik + Claude).
#   python -m unittest discover -s tests

import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import chain  # noqa: E402
import community  # noqa: E402
from schema import Item, item_from_dict  # noqa: E402


def mk(id, level=1, deps=None, sub=None, holder=None, hours=None, **kw):
    return Item(id=id, name=id, level=level, function="f", depends_on=deps or [],
                non_grid_substitute=sub, local_holder=holder,
                hours_to_fail_without_grid=hours, trigger="threshold: t", **kw)


def graph(*its):
    return {i.id: i for i in its}


class SeedTests(unittest.TestCase):
    def setUp(self):
        self.items = chain.load()

    def test_seed_is_valid(self):
        rep = chain.validate(self.items)
        self.assertTrue(chain.is_clean(rep), rep)

    def test_every_level_present(self):
        self.assertEqual({i.level for i in self.items.values()}, {0, 1, 2, 3})

    def test_unknown_numbers_are_null_and_thin(self):
        for i in self.items.values():
            if i.hours_to_fail_without_grid is None and i.lead_time_days is None:
                continue
            self.assertIn(i.volume, ("thin", "medium", "solid"))
            self.assertIn(i.status, ("OBSERVED", "DERIVED", "PROPOSED"))

    def test_government_never_a_prerequisite(self):
        par = [i.id for i in self.items.values() if i.parallel_input]
        self.assertTrue(par)
        for i in self.items.values():
            self.assertFalse(set(i.depends_on) & set(par), i.id)

    def test_seed_level_inversions_are_reported(self):
        inv = {(a, d) for a, _, d, _ in chain.level_check(self.items)}
        self.assertIn(("water_potable", "fuel_stock"), inv)
        self.assertIn(("water_potable", "water_chem_chlorine"), inv)

    def test_seed_order_is_complete(self):
        seq, stuck = chain.order(self.items)
        self.assertEqual(stuck, [])
        self.assertEqual(len(seq), len(self.items))


class ValidationTests(unittest.TestCase):
    def test_unknown_id_reported(self):
        rep = chain.validate(graph(mk("a", deps=["ghost"])))
        self.assertEqual(rep["unknown_ids"], [("a", "ghost")])

    def test_cycle_reported_not_raised(self):
        g = graph(mk("a", deps=["b"]), mk("b", deps=["c"]), mk("c", deps=["a"]), mk("d", deps=["a"]))
        rep = chain.validate(g)
        self.assertEqual(len(rep["cycles"]), 1)
        self.assertEqual(set(rep["cycles"][0]), {"a", "b", "c"})
        seq, stuck = chain.order(g)
        self.assertEqual(seq, [])
        self.assertEqual(stuck, ["a", "b", "c", "d"])

    def test_self_loop_is_a_cycle(self):
        self.assertTrue(chain.find_cycles(graph(mk("a", deps=["a"]))))

    def test_parallel_input_as_prereq_fails(self):
        g = graph(mk("gov", level=3, parallel_input=True), mk("a", deps=["gov"]))
        self.assertEqual(chain.validate(g)["parallel_as_prereq"], [("a", "gov")])

    def test_bad_fields(self):
        bad = Item(id="x", name="x", level=7, function="f", trigger="soon", volume="huge",
                   status="LIKELY", hours_to_fail_without_grid=-1)
        p = " ".join(bad.problems())
        for word in ("level", "volume", "status", "trigger", "hours_to_fail"):
            self.assertIn(word, p)

    def test_null_safe_construction(self):
        it = item_from_dict({"id": "z", "depends_on": None, "junk": 1})
        self.assertEqual(it.depends_on, [])
        g = graph(it)
        chain.validate(g)
        chain.rank(g)
        chain.spof(g)
        chain.order(g)
        chain.level_check(g)


class ScoringTests(unittest.TestCase):
    def setUp(self):
        # a <- b <- c ; a <- d
        self.g = graph(mk("a", level=1), mk("b", level=1, deps=["a"]),
                       mk("c", level=0, deps=["b"]), mk("d", level=0, deps=["a"]))

    def test_transitive_dependents(self):
        dep = chain.dependents(self.g)
        self.assertEqual(dep["a"], {"b", "c", "d"})
        self.assertEqual(dep["b"], {"c"})

    def test_criticality_formula(self):
        self.assertEqual(chain.criticality(mk("x"), 3), 3.0)
        self.assertAlmostEqual(chain.criticality(mk("x", sub="hand pump"), 3), 0.9)
        self.assertAlmostEqual(chain.criticality(mk("x", hours=4.0), 3), 0.75)
        self.assertAlmostEqual(chain.criticality(mk("x", sub="s", hours=2.0), 4), 0.6)

    def test_rank_order(self):
        self.assertEqual(chain.rank(self.g)[0]["id"], "a")

    def test_level_check_flags_upward_only(self):
        g = graph(mk("hi", level=2), mk("lo", level=0, deps=["hi"]), mk("top", level=3, deps=["lo"]))
        self.assertEqual(chain.level_check(g), [("lo", 0, "hi", 2)])

    def test_spof_rule(self):
        g = dict(self.g)
        self.assertEqual([r["id"] for r in chain.spof(g)], ["a"])
        g["a"] = mk("a", level=1, holder="co-op")
        self.assertEqual(chain.spof(g), [])
        g["a"] = mk("a", level=1, sub="hand crank")
        self.assertEqual(chain.spof(g), [])

    def test_order_deps_first_and_hours_tiebreak(self):
        g = graph(mk("root"), mk("slow", deps=["root"], hours=100.0),
                  mk("fast", deps=["root"], hours=2.0), mk("unknown", deps=["root"]))
        seq, _ = chain.order(g)
        self.assertEqual(seq, ["root", "fast", "slow", "unknown"])


class CommunityTests(unittest.TestCase):
    def setUp(self):
        self.items = chain.load()
        ex = os.path.join(ROOT, "examples")
        self.a = community.load_community(os.path.join(ex, "community_a.json"))
        self.b = community.load_community(os.path.join(ex, "community_b.json"))

    def test_gaps_are_l0_l1_unheld(self):
        g = community.gaps(self.a, self.items)
        ids = {r["id"] for r in g}
        self.assertTrue(all(r["level"] in (0, 1) for r in g))
        self.assertNotIn("heat_space", ids)
        self.assertIn("water_potable", ids)

    def test_interconnect(self):
        r = community.interconnect(self.a, self.b, self.items)
        self.assertIn("frequency_authority", r["both_lack_L3"])
        self.assertNotIn("sync_equipment", r["both_lack_L3"])
        self.assertNotIn("gov_parallel_restoration", r["both_lack_L3"])
        self.assertIn("fuel_stock", r["a_offers_b"])
        self.assertIn("water_potable", r["b_offers_a"])
        self.assertNotIn("comms_offgrid", r["a_offers_b"] + r["b_offers_a"])

    def test_empty_community_null_safe(self):
        c = community.Community(name="empty")
        self.assertTrue(community.gaps(c, self.items))
        community.interconnect(c, c, self.items)


if __name__ == "__main__":
    unittest.main()
