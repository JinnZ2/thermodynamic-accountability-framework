# misuse_guard/tests/test_headrec.py -- CC0, stdlib unittest
# Provenance: co-authored (JinnZ2 + Claude), 2026-11-05.
# M10: head record per ledger. Synthetic ledgers only. Each ledger module is
# exercised in a subprocess (flat module names collide across folders).

import filecmp
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "misuse_guard"))

import headrec  # noqa: E402

PY = sys.executable
COPIES = ("judgment_registry", "assembly_instrument", "signal_calibration", "community_black_start")


def chain(n):
    return [{"hash": "h%02d" % i} for i in range(n)]


class HeadLogic(unittest.TestCase):
    def test_states(self):
        c = chain(3)
        hd = headrec.head_of(c)
        self.assertEqual(headrec.check(c, hd), [])
        self.assertEqual(headrec.check(c + [{"hash": "h03"}], hd), [])          # grown past an older head
        self.assertIn("truncated", headrec.check(c[:2], hd)[0])
        self.assertIn("rebuilt", headrec.check([{"hash": "x"}] * 3, hd)[0])
        self.assertIn("no head", headrec.check(c, None)[0])
        self.assertEqual(headrec.check([], None), [])
        self.assertEqual(headrec.check(c, headrec.parse("3:h02")), [])
        self.assertIn("malformed", headrec.check(c, {"count": "x"})[0])


class CopiesIdentical(unittest.TestCase):
    def test_byte_identical(self):
        src = os.path.join(ROOT, "misuse_guard", "headrec.py")
        for d in COPIES:
            self.assertTrue(filecmp.cmp(src, os.path.join(ROOT, d, "headrec.py"), shallow=False), d)


# Each snippet: append 3 records, then (a) truncate -> append refused,
# (b) rebuild from scratch (valid chain, 1 record) -> append refused.
SNIPPETS = {
    "judgment_registry": (
        "import ledger as L\n"
        "B=lambda i: {'judgment_id': 'j%d' % i}\n"
        "add=lambda p,i: L.append(p, 'judgment', B(i))\n"
        "ERR=L.LedgerError\n"),
    "signal_calibration": (
        "import chainlog as L\n"
        "add=lambda p,i: L.append(p, 'field_report', {'n': i})\n"
        "ERR=L.ChainError\n"),
    "community_black_start": (
        "import coordination as L\n"
        "add=lambda p,i: L.append_log(p, {'n': i, 'plain': 'Synthetic test record for the head check, number %d.' % i})\n"
        "ERR=L.CoordinationError\n"),
}
BODY = (
    "import os, sys\n"
    "p=sys.argv[1]\n"
    "for i in range(3): add(p, i)\n"
    "lines=open(p).read().splitlines()\n"
    "open(p,'w').write('\\n'.join(lines[:2])+'\\n')\n"
    "try:\n    add(p, 9); print('TRUNC_ACCEPTED')\nexcept ERR as e:\n    print('TRUNC_REFUSED')\n"
    "h=p+'.head.json'; saved=open(h).read()\n"
    "os.remove(p); os.remove(h)\n"
    "for i in (7, 8, 9): add(p, i)\n"          # rebuilt: valid 3-record chain, new content
    "open(h,'w').write(saved)\n"               # published (older) head put back
    "try:\n    add(p, 8); print('REBUILD_ACCEPTED')\nexcept ERR as e:\n    print('REBUILD_REFUSED')\n"
)


class LedgersRefuse(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def run_snippet(self, folder, code):
        p = os.path.join(self.tmp, folder + ".jsonl")
        out = subprocess.run([PY, "-c", code, p], cwd=os.path.join(ROOT, folder),
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        self.assertEqual(out.returncode, 0, out.stderr)
        return out.stdout.split()

    def test_truncate_and_rebuild_refused(self):
        for folder, pre in SNIPPETS.items():
            self.assertEqual(self.run_snippet(folder, pre + BODY), ["TRUNC_REFUSED", "REBUILD_REFUSED"], folder)

    def test_assembly_ledger(self):
        code = (
            "import sys, ledger as L\n"
            "p=sys.argv[1]\n"
            "def mk(ns):\n"
            "    out=[]\n"
            "    for n in ns:\n"
            "        out.append(L._record('checkout', {'n': n}, out[-1]['hash'] if out else L.GENESIS))\n"
            "    return out\n"
            "recs=mk([0, 1, 2]); L.write_new(p, recs)\n"
            "print('OK' if L.head_problems(p, L.read(p))==[] else 'BAD')\n"
            "print('TRUNC' if L.head_problems(p, recs[:2]) else 'MISSED')\n"
            "print('REBUILT' if L.head_problems(p, mk([5, 6, 7])) else 'MISSED')\n")
        self.assertEqual(self.run_snippet("assembly_instrument", code), ["OK", "TRUNC", "REBUILT"])


class NothingTrackedInLocalData(unittest.TestCase):
    def test_git_tracks_nothing_under_local_data(self):
        if shutil.which("git") is None or not os.path.isdir(os.path.join(ROOT, ".git")):
            self.skipTest("no git checkout")
        out = subprocess.run(["git", "ls-files", "local_data"], cwd=ROOT,
                             stdout=subprocess.PIPE, universal_newlines=True)
        self.assertEqual(out.stdout.strip(), "")


if __name__ == "__main__":
    unittest.main()
