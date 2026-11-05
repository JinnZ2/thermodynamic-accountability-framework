# tests/test_loaders_deploy.py -- CC0, stdlib unittest
# Provenance: co-authored (JinnZ2 + Claude), 2026-11-05.
# Checkpoint readers (safetensors, .npz; F32 / F16 / BF16) on tiny synthetic
# files written by loaders.py itself, and the deploy gate
# (UNLOGGED_EDIT_CHAIN_BREAK). No external libraries.

import io
import json
import os
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tests"))

import audit  # noqa: E402
import deploy  # noqa: E402
import ledger  # noqa: E402
import loaders  # noqa: E402
from test_weight_edits import Tmp  # noqa: E402

T_BEFORE = {"l1.w": ("F32", [2, 2], [0.5, -1.0, 2.0, 0.25]),
            "l2.w": ("F16", [3], [1.0, 0.5, -2.0]),
            "l3.w": ("BF16", [2], [1.0, -3.0])}
T_AFTER = {"l1.w": ("F32", [2, 2], [0.5, 0.0, 2.0, 0.25]),
           "l2.w": ("F16", [3], [1.0, 0.5, -2.0]),
           "l3.w": ("BF16", [2], [1.0, 4.0])}      # 2 weights, 2 tensors


class Loaders(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.dir)

    def p(self, n):
        return os.path.join(self.dir, n)

    def roundtrip(self, path, write, t=T_BEFORE):
        write(path, t)
        r = loaders.open_checkpoint(path)
        self.assertEqual(r.names(), sorted(t))
        for k, (dt, shape, vals) in t.items():
            self.assertEqual((r.dtype(k), r.shape(k), r.read(k)), (dt, shape, vals))

    def test_safetensors_roundtrip(self):
        self.roundtrip(self.p("a.safetensors"), lambda p, t: loaders.write_safetensors(p, t, {"format": "pt"}))

    def test_safetensors_layout(self):
        path = self.p("a.safetensors")
        loaders.write_safetensors(path, T_BEFORE)
        with open(path, "rb") as f:
            (hlen,) = struct.unpack("<Q", f.read(8))
            hdr = json.loads(f.read(hlen))
        self.assertEqual(hdr["l1.w"]["data_offsets"], [0, 16])
        self.assertEqual(hdr["l3.w"]["dtype"], "BF16")

    def test_npz_roundtrip_plain_and_compressed(self):
        t = dict((k, v) for k, v in T_BEFORE.items() if v[0] != "BF16")
        self.roundtrip(self.p("a.npz"), loaders.write_npz, t)
        loaders.write_npz(self.p("c.npz"), t, compressed=True)
        self.assertEqual(loaders.open_checkpoint(self.p("c.npz")).read("l1.w"), [0.5, -1.0, 2.0, 0.25])

    def test_npz_bf16_not_writable(self):
        # .npy has no standard bfloat16 descr; safetensors does
        with self.assertRaises(loaders.LoaderError):
            loaders.write_npz(self.p("b.npz"), {"x": ("BF16", [1], [1.0])})

    def test_bf16_bit_shift(self):
        raw = struct.pack("<H", 0x3F80)                 # top half of float32 1.0
        self.assertEqual(loaders.decode(raw, "BF16"), [1.0])
        self.assertEqual(loaders.encode([1.0], "BF16"), raw)
        self.assertEqual(loaders.decode(loaders.encode([1.0078125], "BF16"), "BF16"), [1.0078125])

    def test_refusals(self):
        with self.assertRaises(loaders.LoaderError):
            loaders.decode(b"\x00\x00\x00\x00", "I32")
        with self.assertRaises(loaders.LoaderError):
            loaders.open_checkpoint(self.p("x.bin"))
        bad = self.p("bad.safetensors")
        loaders.write_safetensors(bad, T_BEFORE)
        with open(bad, "rb") as f:
            data = f.read()
        with open(bad, "wb") as f:
            f.write(data[:-3])
        with self.assertRaises(loaders.LoaderError):
            loaders.open_checkpoint(bad).read("l3.w")

    def test_reads_one_tensor_at_a_time(self):
        path = self.p("a.safetensors")
        loaders.write_safetensors(path, T_BEFORE)
        r = loaders.open_checkpoint(path)
        self.assertFalse(hasattr(r, "data"))
        self.assertEqual(r.read("l2.w"), [1.0, 0.5, -2.0])

    def test_diff_on_safetensors_and_nan(self):
        b, a = self.p("b.safetensors"), self.p("a.safetensors")
        loaders.write_safetensors(b, T_BEFORE)
        loaders.write_safetensors(a, T_AFTER)
        self.assertEqual(audit.diff(loaders.open_checkpoint(b), loaders.open_checkpoint(a)), (["l1.w", "l3.w"], 2))
        n = float("nan")
        self.assertEqual(audit.diff({"x": [n, 1.0]}, {"x": [n, 1.0]}), ([], 0))


class DeployGate(Tmp):
    def base(self, h=None, bid="B0"):
        return ledger.append(self.led, "base", {"base_id": bid, "base_hash": h or self.hb, "target_model": "model-m",
                                                "target_version": "v1", "registered_by": "op-1", "date": "2026-11-05"})

    def test_base_itself_reachable(self):
        self.base()
        res = deploy.gate(self.led, self.hb)
        self.assertEqual((res["ok"], res["base"], res["edits"]), (True, "B0", []))

    def test_logged_run_reachable(self):
        self.base()
        ledger.append(self.led, "edit", self.edit())
        h2 = "2" * 64
        ledger.append(self.led, "edit", self.edit(edit_id="E2", before_hash=self.ha, after_hash=h2))
        res = deploy.gate(self.led, h2)
        self.assertEqual((res["ok"], res["edits"]), (True, ["E1", "E2"]))
        self.assertIn("DIFF_NOT_AUDITED", [f["flag"] for f in res["notes"]])

    def test_unlogged_edit_breaks_chain(self):
        self.base()
        ledger.append(self.led, "edit", self.edit())
        # E2 starts from a hash no logged edit produced: an unlogged edit sits between
        ledger.append(self.led, "edit", self.edit(edit_id="E2", before_hash="9" * 64, after_hash="2" * 64))
        res = deploy.gate(self.led, "2" * 64)
        self.assertEqual((res["ok"], res["flag"]), (False, "UNLOGGED_EDIT_CHAIN_BREAK"))
        self.assertFalse(deploy.gate(self.led, "7" * 64)["ok"])

    def test_no_base_registered(self):
        ledger.append(self.led, "edit", self.edit())
        self.assertFalse(deploy.gate(self.led, self.ha)["ok"])

    def test_broken_ledger_fails_gate(self):
        self.base()
        ledger.append(self.led, "edit", self.edit())
        with open(self.led, encoding="utf-8") as f:
            lines = f.readlines()
        with open(self.led, "w", encoding="utf-8") as f:
            f.writelines(lines[:1])
        res = deploy.gate(self.led, self.hb)
        self.assertFalse(res["ok"])
        self.assertIn("ledger chain broken", res["detail"])

    def test_duplicate_base_refused(self):
        self.base()
        with self.assertRaises(ledger.LedgerError):
            self.base(bid="B1")
        with self.assertRaises(ledger.LedgerError):
            ledger.append(self.led, "base", {"base_id": "B2"})

    def test_cli_file_and_hash(self):
        self.base()
        ledger.append(self.led, "edit", self.edit())
        buf = io.StringIO()
        with redirect_stdout(buf):
            self.assertEqual(deploy.main([self.a, "--ledger", self.led]), 0)
            self.assertEqual(deploy.main(["5" * 64, "--ledger", self.led]), 1)
        self.assertIn("via 1 logged edit(s): E1", buf.getvalue())
        self.assertIn("UNLOGGED_EDIT_CHAIN_BREAK", buf.getvalue())

    def test_audit_cli_on_npz(self):
        b, a = os.path.join(self.dir, "b.npz"), os.path.join(self.dir, "a.npz")
        t = dict((k, v) for k, v in T_BEFORE.items() if v[0] != "BF16")
        loaders.write_npz(b, t)
        t2 = dict(t, **{"l1.w": ("F32", [2, 2], [0.5, 0.0, 2.0, 0.25])})
        loaders.write_npz(a, t2)
        ledger.append(self.led, "edit", self.edit(before_hash=loaders.file_hash(b), after_hash=loaders.file_hash(a),
                                                  changed_tensors=["l1.w"], weight_count=1))
        r = subprocess.run([sys.executable, os.path.join(ROOT, "audit.py"), "E1", b, a, "--auditor", "aud-1",
                            "--ledger", self.led], stdout=subprocess.PIPE, universal_newlines=True)
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertEqual([f["flag"] for f in ledger.check(ledger.read(self.led))], [])

    def test_flag_text_neutral(self):
        from test_weight_edits import EVALUATIVE
        words = set(re.findall(r"[a-z]+", " ".join(list(deploy.FLAGS) + list(deploy.FLAGS.values())).lower()))
        self.assertEqual(words & set(EVALUATIVE), set())


if __name__ == "__main__":
    unittest.main()
