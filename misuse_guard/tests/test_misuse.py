# misuse_guard/tests/test_misuse.py -- CC0, stdlib unittest
# Provenance: co-authored (JinnZ2 + Claude), 2026-11-05.
# One test class per mitigation in docs/misuse_register.json. Synthetic only.
# Modules that share flat module names (report, schema, cli) are exercised in
# subprocesses so their imports do not collide.

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "community_black_start"))

from misuse_guard import localdata, render_register, scan  # noqa: E402
import bulletins  # noqa: E402
import export  # noqa: E402
import holders  # noqa: E402
import triggers  # noqa: E402

PY = sys.executable
REG = json.load(open(os.path.join(ROOT, "docs", "misuse_register.json")))


def run(code, cwd):
    return subprocess.run([PY, "-c", code], cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          universal_newlines=True, timeout=120)


class FixtureScanTests(unittest.TestCase):
    """D-M1: committed fixtures carry no contact or person patterns (pattern list, thin*)."""

    def test_committed_fixtures_clean(self):
        self.assertEqual(scan.scan(), [])

    def test_scanner_is_not_silent(self):
        d = tempfile.mkdtemp()
        try:
            p = os.path.join(d, "f.json")
            with open(p, "w") as f:
                f.write('{"holder": "Alice Martin", "x": "a@b.org", "y": "555 555 0123", '
                        '"z": "12 Oak Street", "c": "45.1234, -93.5678"}\n')
            kinds = sorted(set(h[2] for h in scan.scan([p])))
            self.assertEqual(kinds, ["coordinate_pair", "email", "person_name_field", "phone", "street_address"])
            with open(p, "w") as f:
                f.write('{"x": "a@b.org"}  # misuse-scan: planted\n')
            self.assertEqual(scan.scan([p]), [])
        finally:
            shutil.rmtree(d)


class LoaderTests(unittest.TestCase):
    """D-M1: real data inside the repo tree is refused unless under gitignored local_data/."""

    def test_repo_path_refused(self):
        with self.assertRaises(localdata.RealDataRefused):
            localdata.load_real_json(os.path.join(ROOT, "community_black_start", "items.json"))

    def test_local_data_needs_gitignore(self):
        d = tempfile.mkdtemp()
        try:
            os.makedirs(os.path.join(d, "local_data"))
            p = os.path.join(d, "local_data", "r.json")
            with open(p, "w") as f:
                json.dump({"ok": 1}, f)
            with self.assertRaises(localdata.RealDataRefused):
                localdata.load_real_json(p, repo_root=d)
            with open(os.path.join(d, ".gitignore"), "w") as f:
                f.write("local_data/\n")
            self.assertEqual(localdata.load_real_json(p, repo_root=d), {"ok": 1})
            self.assertTrue(localdata.local_dir_ignored(ROOT))
        finally:
            shutil.rmtree(d)

    def test_outside_repo_allowed(self):
        d = tempfile.mkdtemp()
        try:
            p = os.path.join(d, "r.json")
            with open(p, "w") as f:
                json.dump([1], f)
            self.assertEqual(localdata.load_real_json(p), [1])
        finally:
            shutil.rmtree(d)


class ExportTests(unittest.TestCase):
    """D-M2: export carries booleans and counts only."""

    def test_no_quantity_site_or_holder(self):
        reg = {"community": "c-1", "items": {
            "fuel_stock": {"have": 120, "need": 400, "site": "north shed", "holder": "role-x", "note": "lock weak"},
            "heat_space": {"have": 9, "need": 3, "site": "hall"},
            "comms_offgrid": {"have": None, "need": 2}}}
        out = export.aggregate(reg)
        self.assertEqual(set(out), set(export.OUT_KEYS))
        self.assertEqual(out["need"], {"comms_offgrid": None, "fuel_stock": True, "heat_space": False})
        self.assertEqual(out["surplus"]["heat_space"], True)
        text = json.dumps(out)
        for leak in ("120", "400", "north shed", "hall", "role-x", "lock weak", "site", "holder", "have"):
            self.assertNotIn(leak, text, leak)
        for v in list(out["need"].values()) + list(out["surplus"].values()):
            self.assertIn(v, (True, False, None))

    def test_cli_refuses_repo_path(self):
        p = run("import sys; sys.argv=['x', 'community_black_start/examples/community_a.json']; "
                "sys.path.insert(0,'community_black_start'); import export; sys.exit(export.main(sys.argv[1:]))", ROOT)
        self.assertEqual(p.returncode, 1)
        self.assertIn("REFUSED", p.stderr)


class HolderTests(unittest.TestCase):
    """D-M3: KnowledgeHolder has no identity field."""

    def test_identity_field_refused(self):
        for bad in ({"skill": "s", "region": "north", "contact_via": "steward-n", "name": "x"},
                    {"skill": "s", "region": "north", "contact_via": "steward-n", "phone": "x"},
                    {"skill": "s", "region": "north", "contact_via": "steward-n", "home_address": "x"},
                    {"skill": "s", "region": "north", "contact_via": "steward-n", "extra": "x"}):
            with self.assertRaises(holders.HolderError):
                holders.KnowledgeHolder.from_dict(bad)

    def test_coarse_region_and_role_contact(self):
        ok = holders.KnowledgeHolder.from_dict({"skill": "manual synchronizing", "region": "river valley",
                                                 "availability": "on call", "contact_via": "steward-north"})
        self.assertEqual(ok.to_dict()["contact_via"], "steward-north")
        for bad in ({"region": "lot 14 east"}, {"region": "a b c d"}, {"contact_via": "a@b.org"},
                    {"contact_via": "555 555 0101"}):
            d = {"skill": "s", "region": "north", "contact_via": "steward-n"}
            d.update(bad)
            with self.assertRaises(holders.HolderError):
                holders.KnowledgeHolder.from_dict(d)


class TriggerTests(unittest.TestCase):
    """D-M4: published thresholds are ranges; exact values stay local."""

    def test_published_are_ranges(self):
        self.assertTrue(triggers.PUBLISHED)
        self.assertEqual(triggers.published_problems(triggers.PUBLISHED), [])
        for r in triggers.PUBLISHED.values():
            self.assertEqual((r["low"], r["high"]), (None, None))     # no invented numbers

    def test_single_values_refused(self):
        for bad in ({"t": 5}, {"t": {"value": 5}}, {"t": {"low": 5, "high": 5}}, {"t": {"low": 5, "high": None}}):
            self.assertTrue(triggers.published_problems(bad), bad)

    def test_exact_values_not_read_from_repo(self):
        with self.assertRaises(localdata.RealDataRefused):
            triggers.load_exact(os.path.join(ROOT, "community_black_start", "items.json"))


class BulletinTests(unittest.TestCase):
    """D-M5: bulletins carry status, not holdings, sites, quantities or weak points."""

    BASE = {"restored": "water at the hall pump", "next_step": "test the clinic line",
            "household_role": "boil water", "date": "2026-12-01"}

    def test_forbidden_fields_and_quantities(self):
        self.assertEqual(bulletins.scope_problems(self.BASE), [])
        self.assertTrue(bulletins.is_published(self.BASE))
        for extra in ({"fuel_stock": "low"}, {"site": "x"}, {"quantity": "x"}, {"weak_points": "x"},
                      {"keyholder": "x"}, {"misc": "x"}):
            b = dict(self.BASE, **extra)
            self.assertTrue(bulletins.scope_problems(b), extra)
            self.assertFalse(bulletins.is_published(b))
        b = dict(self.BASE, restored="40 gallons of diesel left")
        self.assertTrue(bulletins.scope_problems(b))


class RegistryHeaderTests(unittest.TestCase):
    """D-M6: every judgment_registry CLI output starts with the header."""

    def test_header_first_line(self):
        d = tempfile.mkdtemp()
        try:
            rec = os.path.join(d, "j.json")
            with open(rec, "w") as f:
                json.dump({"judgment_id": "j1", "claim": "synthetic", "layer": "physics",
                           "intervention_id": None}, f)
            iv = os.path.join(d, "i.json")
            with open(iv, "w") as f:
                json.dump({"kind": "intervention", "intervention_id": "i1", "direction": "NONE"}, f)
            led = os.path.join(d, "l.jsonl")
            reg_dir = os.path.join(ROOT, "judgment_registry")
            cmds = [["add", rec], ["add", iv], ["check"], ["lineage", "j1"], ["diff", "j1", "j1"], ["export"],
                    ["axis", "i1"], ["axis", "--compare", "i1", "i1"]]
            for c in cmds:
                p = subprocess.run([PY, "cli.py"] + c + ["--ledger", led], cwd=reg_dir, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, universal_newlines=True, timeout=60)
                self.assertEqual(p.returncode, 0, (c, p.stderr))
                self.assertEqual(p.stdout.splitlines()[0], "Registered = documented, not correct.", c)
        finally:
            shutil.rmtree(d)


class DissentTests(unittest.TestCase):
    """D-M7: dissent defaults to an anonymous holder."""

    def test_anonymous_default(self):
        code = ("import ledger; r = ledger.append_records([], 'judgment', {'judgment_id': 'j1', "
                "'dissent': [{'position': 'p1', 'reason': 'r'}, {'position': 'p2', 'holder': 'anonymous'}]}); "
                "print([d['holder'] for d in r[0]['body']['dissent']])")
        p = run(code, os.path.join(ROOT, "judgment_registry"))
        self.assertEqual(p.stdout.strip(), "['anonymous', 'anonymous']", p.stderr)


class CalibrationReportTests(unittest.TestCase):
    """D-M8: published calibration reports carry rates, never prompts or outputs."""

    def test_report_has_no_prompt_or_output_text(self):
        d = tempfile.mkdtemp()
        try:
            code = r'''
import json, os, sys
sys.path.insert(0, ".")
import chainlog, prereg, runner, report
from adapters.base import ScriptedAdapter
d = sys.argv[1]
doc = {"test_id": "T4", "hypothesis": "PROPOSED: h", "pass_criteria": "c", "scoring_rule": "r", "sample_size": 4,
       "models": ["m-x"], "date": "2026-11-05", "intervention": {"loop_status": "CLOSED", "consent": "NOT_POSSIBLE",
       "band_definition": "text framing only", "review_date": "2026-12-01"}}
p = os.path.join(d, "T4.json"); json.dump(doc, open(p, "w"))
log = os.path.join(d, "log.jsonl"); prereg.register(p, log)
res = runner.run(p, ScriptedAdapter("m-x", default="UNIQUE-OUTPUT-MARKER-77"), log,
                 registry_path=os.path.join(d, "reg.jsonl"))
text = report.build(chainlog.read(log))
leaks = [r["result_id"] for r in res if r["prompt"][:40] in text] + (["output"] if "UNIQUE-OUTPUT-MARKER-77" in text else [])
print(json.dumps(leaks))
'''
            p = subprocess.run([PY, "-c", code, d], cwd=os.path.join(ROOT, "signal_calibration"),
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, timeout=120)
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertEqual(json.loads(p.stdout.strip().splitlines()[-1]), [])
        finally:
            shutil.rmtree(d)


class ReadmeSectionTests(unittest.TestCase):
    """D-M9: every module README has a misuse section linking at least one M-entry."""

    def test_sections_present_and_current(self):
        for m in render_register.README_MODULES:
            text = open(os.path.join(ROOT, m, "README.md"), encoding="utf-8").read()
            self.assertIn(render_register.TITLE, text, m)
            sec = text[text.index(render_register.BEGIN):text.index(render_register.END)]
            self.assertTrue(re.search(r"\bM\d+\b", sec), m)
        self.assertEqual(render_register.main(["--check"]), 0)


class RegisterShapeTests(unittest.TestCase):
    def test_entries_and_mitigation_links(self):
        mids = set(d["id"] for d in REG["mitigations"])
        fields = ("id", "module", "surface", "adversarial_use", "mitigation_ids", "residual", "volume", "status")
        ids = [e["id"] for e in REG["entries"]]
        self.assertEqual(len(ids), len(set(ids)))
        for e in REG["entries"]:
            for k in fields:
                self.assertIn(k, e, (e["id"], k))
            self.assertTrue(set(e["mitigation_ids"]) <= mids, e["id"])
            self.assertIn(e["status"], REG["status_vocabulary"])
        for x in ("M%d" % i for i in range(1, 10)):
            self.assertIn(x, ids)


if __name__ == "__main__":
    unittest.main()
