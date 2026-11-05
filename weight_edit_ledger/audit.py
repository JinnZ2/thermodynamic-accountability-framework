#!/usr/bin/env python3
# audit.py -- CC0, stdlib only, python >= 3.7
# Provenance: co-authored (JinnZ2 + Claude), 2026-11-05.
#
# Independent diff audit (D-M16). A second reader -- never the editor --
# recomputes the diff from the two checkpoints and records what it found.
# ledger.check() then compares the record with the editor's summary
# (EDIT_SUMMARY_MISMATCH, AUDIT_HASH_MISMATCH). J13's lesson: a summary can
# omit changes, so the diff is recomputed, not read from the summary.
#
# Checkpoint format here: JSON {tensor_name: number | nested list of numbers}.
# Real checkpoints (safetensors, .npz, ...) need a loader that yields the
# same {name: flat values} mapping; pass it as load=. The hash is sha256 of
# the checkpoint file's bytes.
#
#   python3 audit.py EDIT_ID BEFORE.json AFTER.json --auditor ID [--auditor-class human|model] [--ledger L]

import hashlib
import json
import sys

import ledger


def file_hash(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def _flat(v):
    if isinstance(v, list):
        out = []
        for x in v:
            out.extend(_flat(x))
        return out
    return [v]


def load_json(path):
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    return dict((k, _flat(v)) for k, v in d.items())


def diff(before, after):
    """-> (changed tensor names, changed weight count). A tensor added, removed
    or reshaped counts as changed, with all its elements (the larger size)."""
    names, count = [], 0
    for k in sorted(set(before) | set(after)):
        a, b = before.get(k), after.get(k)
        if a is None or b is None or len(a) != len(b):
            names.append(k)
            count += max(len(a or []), len(b or []))
            continue
        n = sum(1 for x, y in zip(a, b) if x != y)
        if n:
            names.append(k)
            count += n
    return names, count


def run(path, edit_id, before_path, after_path, auditor_id, auditor_class="human", date=None, load=load_json):
    names, count = diff(load(before_path), load(after_path))
    body = {"edit_id": edit_id, "auditor_id": auditor_id, "auditor_class": auditor_class, "date": date,
            "before_hash_found": file_hash(before_path), "after_hash_found": file_hash(after_path),
            "changed_tensors": names, "weight_count": count, "notes": None}
    return ledger.append(path, "diff_audit", body)


def main(argv):
    argv = list(argv)
    path = ledger._opt(argv, "--ledger") or "weight_edits.jsonl"
    who = ledger._opt(argv, "--auditor")
    cls = ledger._opt(argv, "--auditor-class") or "human"
    if len(argv) != 3 or not who:
        sys.stderr.write("usage: audit.py EDIT_ID BEFORE.json AFTER.json --auditor ID [--ledger L]\n")
        return 2
    try:
        rec = run(path, argv[0], argv[1], argv[2], who, cls)
    except ledger.LedgerError as e:
        print(str(e))
        return 1
    b = rec["body"]
    print("diff_audit %s: %d tensor(s), %d weight(s) changed" % (b["edit_id"], len(b["changed_tensors"]), b["weight_count"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
