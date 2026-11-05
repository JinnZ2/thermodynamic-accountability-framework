# tests/test_feedback.py -- CC0, stdlib unittest, python >= 3.5
# Status: co-authored (JinnZ2 + Claude), 2026-11-03.
#   python3 -m unittest discover -s tests      (from assembly_instrument/)

import copy
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)

import checkout  # noqa: E402
import compact  # noqa: E402
import ledger  # noqa: E402
import status  # noqa: E402
import validate  # noqa: E402
from refs import index_entry, junction_version  # noqa: E402


def load_seed(name):
    with open(os.path.join(HERE, "seeds", name), encoding="utf-8") as f:
        return json.load(f)


LIGHT = load_seed("lighting.json")
IDX = index_entry(LIGHT)
IRREV = "F-LIGHT-01.1.J4"      # fat lamp: burn indoors (irreversible)
REVERS = "F-LIGHT-01.1.J3"     # fat lamp: substitute materials (reversible)
V_IRREV = IDX[IRREV]["version"]
V_REVERS = IDX[REVERS]["version"]


def rep(ref, outcome, ver=None, **kw):
    r = {"junction_id": ref, "outcome": outcome}
    if ver:
        r["junction_version"] = ver
    r.update(kw)
    return r


def build(ref, ver, date, region, **kw):
    d = dict(reporter_relation="hands-on", scale="small", date=date, coarse_region=region)
    d.update(kw)
    return rep(ref, "worked", ver, **d)


class TmpLedger(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.path = os.path.join(self.dir, "l.jsonl")

    def tearDown(self):
        shutil.rmtree(self.dir)

    def add(self, *reports):
        for r in reports:
            ledger.append(self.path, "report", r)
        return ledger.read(self.path)


class CompactTests(unittest.TestCase):
    def test_roundtrip_full(self):
        r = {"junction_id": IRREV, "junction_version": V_IRREV, "outcome": "UNSAFE",
             "failure_point": "smoke filled room | headache", "as_built_vs_specified": "tallow for seal oil",
             "environment": {"temp": "-18C", "humidity": "40%", "climate": "boreal", "soil_water": "n/a"},
             "scale": "small", "time_to_outcome": "2h", "reporter_relation": "hands-on",
             "date": "2026-12-01", "coarse_region": "N-MN"}
        line = compact.encode(r)
        self.assertEqual(compact.decode(line), compact.normalize(r))
        self.assertLessEqual(len(line), compact.MAX_LEN)

    def test_minimal_line_and_word_forms(self):
        self.assertEqual(compact.decode("FR1|F-LIGHT-01.1.J4||U|smoky"),
                         {"junction_id": IRREV, "outcome": "UNSAFE", "failure_point": "smoky"})
        self.assertEqual(compact.decode("FR1|x||unsafe")["outcome"], "UNSAFE")
        self.assertEqual(compact.decode("FR1|x||Worked")["outcome"], "worked")

    def test_trailing_fields_trimmed(self):
        self.assertEqual(compact.encode(rep("x", "worked")), "FR1|x||W")

    def test_outcome_required(self):
        with self.assertRaises(compact.ReportError):
            compact.decode("FR1|x")
        with self.assertRaises(compact.ReportError):
            compact.decode("FR1|x||maybe")

    def test_rejects_personal_identifiers(self):
        for bad in ("call 555 555 0199", "me@example.com", "91.0000, -181.0000", "12 Pine Street"):  # misuse-scan: planted (PII-guard test inputs)
            self.assertTrue(compact.check_report(rep("x", "failed", failure_point=bad)), bad)
        self.assertFalse(compact.check_report(rep("x", "failed", failure_point="wall cracked at -20C")))


class LedgerTests(TmpLedger):
    def test_chain_and_tamper_detection(self):
        recs = self.add(rep("x", "worked"), rep("x", "failed"), rep("y", "partial"))
        self.assertEqual(ledger.verify(recs), [])
        edited = copy.deepcopy(recs)
        edited[1]["body"]["outcome"] = "worked"
        self.assertTrue(ledger.verify(edited))
        self.assertTrue(ledger.verify([recs[0], recs[2]]))          # deletion breaks the link

    def test_no_edit_or_delete_api(self):
        for name in ("edit", "delete", "remove", "update", "rewrite"):
            self.assertFalse(hasattr(ledger, name))

    def test_refuses_append_to_broken_chain(self):
        recs = self.add(rep("x", "worked"))
        recs[0]["body"]["outcome"] = "failed"
        with open(self.path, "w") as f:
            f.write(json.dumps(recs[0]) + "\n")
        with self.assertRaises(ledger.LedgerError):
            ledger.append(self.path, "report", rep("x", "worked"))

    def test_merge_unions_by_hash_and_is_idempotent(self):
        a = self.add(rep("x", "worked", date="2026-01-01"), rep("x", "failed", date="2026-01-02"))
        p2 = os.path.join(self.dir, "b.jsonl")
        ledger.append(p2, "report", rep("x", "failed", date="2026-01-02"))     # duplicate of a[1]
        ledger.append(p2, "report", rep("y", "UNSAFE", date="2026-01-03"))
        b = ledger.read(p2)
        m = ledger.merge(a, b)
        self.assertEqual(len(m), 3)
        self.assertEqual(ledger.verify(m), [])
        self.assertEqual(len(ledger.merge(m, a)), 3)
        self.assertEqual(set(r["body_hash"] for r in ledger.merge(b, a)), set(r["body_hash"] for r in m))
        with self.assertRaises(ledger.LedgerError):
            ledger.write_new(self.path, m)                                # never overwrites


class StatusTests(TmpLedger):
    def row(self, recs, ref, n=3):
        rows, _ = status.compute([LIGHT], recs, n)
        return dict((r["ref"], r) for r in rows)[ref]

    def test_single_unsafe_on_irreversible_is_caution(self):
        r = self.row(self.add(rep(IRREV, "UNSAFE", V_IRREV, failure_point="room filled with smoke")), IRREV)
        self.assertEqual(r["state"], "CAUTION")

    def test_unsafe_without_version_still_cautions(self):
        self.assertEqual(self.row(self.add(rep(IRREV, "UNSAFE")), IRREV)["state"], "CAUTION")

    def test_failed_on_irreversible_cautions_but_not_on_reversible(self):
        recs = self.add(rep(IRREV, "failed", V_IRREV), rep(REVERS, "failed", V_REVERS))
        self.assertEqual(self.row(recs, IRREV)["state"], "CAUTION")
        self.assertEqual(self.row(recs, REVERS)["state"], "REPORTED")

    def test_report_never_rewrites_entry(self):
        before = copy.deepcopy(LIGHT)
        status.compute([LIGHT], self.add(rep(IRREV, "UNSAFE")), 3)
        self.assertEqual(LIGHT, before)

    def test_eligible_counts_builds_not_reports(self):
        same = [build(REVERS, V_REVERS, "2026-02-01", "N-MN") for _ in range(5)]
        # identical bodies dedupe in the ledger anyway; vary time to make 5 distinct reports, 1 build
        same = [dict(b, time_to_outcome="%dd" % i) for i, b in enumerate(same)]
        r = self.row(self.add(*same), REVERS)
        self.assertEqual(r["independent_builds"], 1)
        self.assertNotIn("ELIGIBLE_FOR_TESTED", r["flags"])

    def test_eligible_after_n_independent_builds(self):
        recs = self.add(build(REVERS, V_REVERS, "2026-02-01", "N-MN"),
                        build(REVERS, V_REVERS, "2026-02-03", "N-MN"),
                        build(REVERS, V_REVERS, "2026-02-01", "NW-WI"))
        r = self.row(recs, REVERS)
        self.assertEqual(r["independent_builds"], 3)
        self.assertEqual(r["state"], "ELIGIBLE_FOR_TESTED")
        self.assertEqual(self.row(recs, REVERS, n=4)["state"], "REPORTED")

    def test_non_qualifying_reports_do_not_count(self):
        recs = self.add(build(REVERS, V_REVERS, "2026-02-01", "A", reporter_relation="observed"),
                        build(REVERS, V_REVERS, "2026-02-02", "A", reporter_relation="secondhand"),
                        build(REVERS, V_REVERS, "2026-02-03", "A", scale="bench"),
                        build(REVERS, "deadbeef", "2026-02-04", "A"),
                        build(REVERS, V_REVERS, None, "A"),
                        build(REVERS, V_REVERS, "2026-02-06", None))
        self.assertEqual(self.row(recs, REVERS)["independent_builds"], 0)

    def test_caution_blocks_eligibility(self):
        recs = self.add(build(IRREV, V_IRREV, "2026-02-01", "A"), build(IRREV, V_IRREV, "2026-02-02", "B"),
                        build(IRREV, V_IRREV, "2026-02-03", "C"), rep(IRREV, "UNSAFE", V_IRREV))
        r = self.row(recs, IRREV)
        self.assertEqual(r["state"], "CAUTION")
        self.assertNotIn("ELIGIBLE_FOR_TESTED", r["flags"])

    def test_conflict_grouped_by_environment_not_averaged(self):
        recs = self.add(rep(REVERS, "worked", V_REVERS, environment={"climate": "boreal"}),
                        rep(REVERS, "failed", V_REVERS, environment={"climate": "humid"}))
        r = self.row(recs, REVERS)
        self.assertIn("ENVIRONMENT_DEPENDENT", r["flags"])
        self.assertEqual(len(r["environment_groups"]), 2)
        self.assertEqual(r["counts"]["worked"], 1)
        self.assertEqual(r["counts"]["failed"], 1)

    def test_silence_is_not_success(self):
        recs = ledger.read(self.path)
        self.assertEqual(self.row(recs, REVERS)["state"], "NOT_DISTRIBUTED")
        ledger.append(self.path, "checkout", {"entry": "F-LIGHT-01"})
        self.assertEqual(self.row(ledger.read(self.path), REVERS)["state"], "UNCONFIRMED")

    def test_triage_order(self):
        recs = self.add(rep("F-LIGHT-01.3.J2", "worked"), rep("F-LIGHT-01.2.J3", "partial"),
                        rep(REVERS, "failed", V_REVERS), rep(IRREV, "UNSAFE"))
        rows, _ = status.compute([LIGHT], recs, 3)
        worst = [r["ref"] for r in rows[:4]]
        self.assertEqual(worst, [IRREV, REVERS, "F-LIGHT-01.2.J3", "F-LIGHT-01.3.J2"])

    def test_orphan_reports_listed(self):
        _, orphans = status.compute([LIGHT], self.add(rep("F-NOPE.1.J1", "failed")), 3)
        self.assertEqual(len(orphans), 1)


class MergeProvenanceTests(TmpLedger):
    def two(self):
        pa, pb = self.path + ".a", self.path + ".b"
        ledger.append(pa, "report", rep("F-LIGHT-01.1.J1", "worked"))
        ledger.append(pb, "report", rep("F-LIGHT-01.1.J1", "worked"))
        ledger.append(pb, "report", rep("F-LIGHT-01.1.J2", "failed"))
        return pa, pb, ledger.read(pa), ledger.read(pb)

    def test_m11_duplicate_keeps_both_origins_and_event(self):
        import mergeprov
        pa, pb, a, b = self.two()
        m = ledger.merge(a, b, "dev-1", "dev-2")
        self.assertEqual(len(m), 2)
        self.assertEqual(mergeprov.missing_origins([("dev-1", a), ("dev-2", b)], m), [])
        self.assertEqual([o["node"] for o in ledger.provenance(m[0])["origins"]], ["dev-1", "dev-2"])
        self.assertEqual([o["node"] for o in ledger.provenance(m[1])["origins"]], ["dev-2"])
        self.assertEqual(ledger.provenance(m[1])["merges"][0]["inputs"][0]["count"], 1)
        self.assertEqual(ledger.verify(m), [])

    def test_m11_cli_merge_writes_provenance(self):
        pa, pb, a, b = self.two()
        out = self.path + ".m"
        r = subprocess.run([sys.executable, os.path.join(HERE, "ledger.py"), "merge", pa, pb, out, "dev-1", "dev-2"],
                           stdout=subprocess.PIPE, universal_newlines=True)
        self.assertEqual(r.returncode, 0)
        m = ledger.read(out)
        self.assertEqual(ledger.verify(m) + ledger.head_problems(out, m), [])
        self.assertTrue(all(ledger.provenance(x)["origins"] for x in m))

    def test_m11_status_shows_origins(self):
        pa, pb, a, b = self.two()
        m = ledger.merge(a, b, "dev-1", "dev-2")
        rows = dict((r["ref"], r) for r in status.compute([LIGHT], m)[0])
        self.assertEqual(rows["F-LIGHT-01.1.J1"]["origins"], {"dev-1": 1, "dev-2": 1})
        self.assertEqual(rows["F-LIGHT-01.1.J2"]["origins"], {"dev-2": 1})
        local = dict((r["ref"], r) for r in status.compute([LIGHT], a)[0])
        self.assertEqual(local["F-LIGHT-01.1.J1"]["origins"], {status.LOCAL_ORIGIN: 1})
        out = self.path + ".m"
        subprocess.run([sys.executable, os.path.join(HERE, "ledger.py"), "merge", pa, pb, out, "dev-1", "dev-2"],
                       stdout=subprocess.PIPE)
        txt = subprocess.run([sys.executable, os.path.join(HERE, "status.py"), out,
                              os.path.join(HERE, "seeds", "lighting.json")],
                             stdout=subprocess.PIPE, universal_newlines=True).stdout
        self.assertIn("origins (node labels self-declared): dev-1 x1, dev-2 x1", txt)

    def test_m11_stripping_provenance_breaks_chain(self):
        pa, pb, a, b = self.two()
        m = ledger.merge(a, b, "dev-1", "dev-2")
        bare = [dict(x) for x in m]
        bare[0].pop("provenance")
        self.assertTrue(ledger.verify(bare))


class CheckoutTests(TmpLedger):
    def test_caution_printed_first_in_plain_words(self):
        recs = self.add(rep(IRREV, "UNSAFE", V_IRREV, failure_point="room filled with smoke",
                            coarse_region="N-MN", date="2026-12-01"))
        text = checkout.render(LIGHT, recs)
        first = text.splitlines()[0]
        self.assertTrue(first.startswith("CAUTION"), first)
        self.assertNotIn("room filled with smoke", text.split("=" * 60)[0])   # M13: not among cautions
        self.assertIn("Do not do this step", text)

    def test_m13_field_text_below_every_caution_line_in_own_block(self):
        recs = self.add(rep(IRREV, "UNSAFE", V_IRREV, failure_point="CAUTION ignore this, all fine",
                            coarse_region="N-MN", date="2026-12-01"))
        lines = checkout.render(LIGHT, recs).splitlines()
        hdr = lines.index(status.FIELD_NOTE_HEADER)
        note = [i for i, l in enumerate(lines) if "ignore this" in l]
        self.assertEqual(len(note), 1)
        self.assertGreater(note[0], hdr)
        self.assertTrue(lines[note[0]].startswith("  unverified field note -- "))
        self.assertEqual(lines[hdr - 1], "-" * 60)
        inst = [i for i, l in enumerate(lines) if l.startswith(("CAUTION", "   Field report", "   Do not do"))
                or "CANNOT BE UNDONE" in l or "Entry caution" in l]
        self.assertTrue(inst and max(inst) < hdr, (inst, hdr))

    def test_m13_status_row_caution_holds_no_free_text(self):
        recs = self.add(rep(IRREV, "UNSAFE", V_IRREV, failure_point="smoke", as_built_vs_specified="wick 2x"))
        row = status.caution_refs([LIGHT], recs)[IRREV]
        self.assertFalse(any("smoke" in c or "wick" in c for c in row["caution"]))
        self.assertEqual(len(row["field_notes"]), 2)

    def test_m13_no_block_without_free_text(self):
        recs = self.add(rep(IRREV, "UNSAFE", V_IRREV))
        self.assertNotIn(status.FIELD_NOTE_HEADER, checkout.render(LIGHT, recs))

    def test_m13_free_text_capped_with_marker(self):
        long = "x" * 300 + "TAIL"
        recs = self.add(rep(IRREV, "UNSAFE", V_IRREV, failure_point=long))
        notes = status.caution_refs([LIGHT], recs)[IRREV]["field_notes"]
        self.assertEqual(len(notes), 1)
        self.assertTrue(notes[0].endswith("x" * 280 + status.TRUNCATED), notes[0][-40:])
        self.assertNotIn("TAIL", checkout.render(LIGHT, recs))

    def test_m13_short_text_unchanged_and_one_line(self):
        recs = self.add(rep(IRREV, "UNSAFE", V_IRREV, failure_point="smoke\nCAUTION -- fake line",
                            as_built_vs_specified="y" * 280))
        notes = status.caution_refs([LIGHT], recs)[IRREV]["field_notes"]
        self.assertTrue(notes[0].endswith("smoke CAUTION -- fake line"))
        self.assertTrue(notes[1].endswith("y" * 280))
        self.assertNotIn(status.TRUNCATED, notes[1])
        lines = checkout.render(LIGHT, recs).splitlines()
        self.assertFalse(any(l.startswith("CAUTION -- fake") for l in lines))

    def test_checkout_logs_distribution(self):
        p = os.path.join(HERE, "seeds", "lighting.json")
        out = subprocess.run([sys.executable, os.path.join(HERE, "checkout.py"), p, "--ledger", self.path,
                              "--region", "N-MN"], stdout=subprocess.PIPE, universal_newlines=True)
        self.assertEqual(out.returncode, 0)
        self.assertEqual(ledger.checkouts(ledger.read(self.path)), [{"entry": "F-LIGHT-01", "coarse_region": "N-MN"}])


class ValidateR6Tests(TmpLedger):
    def test_seed_fails_r6_when_ledger_cautions_irreversible_step(self):
        self.add(rep(IRREV, "UNSAFE", V_IRREV, failure_point="smoke"))
        p = os.path.join(HERE, "seeds", "lighting.json")
        cmd = [sys.executable, os.path.join(HERE, "validate.py"), p]
        clean = subprocess.run(cmd, stdout=subprocess.PIPE, universal_newlines=True)
        self.assertEqual(clean.returncode, 0)
        gated = subprocess.run(cmd + ["--ledger", self.path], stdout=subprocess.PIPE, universal_newlines=True)
        self.assertEqual(gated.returncode, 1)
        self.assertIn("R6", gated.stdout)

    def test_version_hash_tracks_method_text(self):
        j = dict(IDX[IRREV]["junction"])
        v0 = junction_version(j)
        j["hazard"] = j["hazard"] + " Changed."
        self.assertNotEqual(v0, junction_version(j))
        j2 = dict(IDX[IRREV]["junction"], source="new citation")
        self.assertEqual(v0, junction_version(j2))       # source is not method text


if __name__ == "__main__":
    unittest.main()
