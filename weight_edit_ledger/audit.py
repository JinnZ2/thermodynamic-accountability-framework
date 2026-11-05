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
# Checkpoint formats (loaders.py, stdlib only): .safetensors, .npz, .json
# {tensor: values}. Tensors are read one at a time from each side. The hash
# is sha256 of the checkpoint file's bytes, read in chunks.
#
# Diff semantics (known limit, recorded as written): element-wise exact
# equality on decoded values (two NaNs count as equal); a tensor added,
# removed, renamed or reshaped counts as changed with all its elements (the
# larger size); a dtype change with equal decoded values counts as
# unchanged. It says what changed, not what the change does.
#
#   python3 audit.py EDIT_ID BEFORE AFTER --auditor ID [--auditor-class human|model] [--ledger L]

import sys

import ledger
import loaders

file_hash = loaders.file_hash


class _Dict(object):
    def __init__(self, d):
        self.d = d

    def names(self):
        return sorted(self.d)

    def shape(self, k):
        return [len(self.d[k])]

    def read(self, k):
        return list(self.d[k])


def load_json(path):
    return loaders.JsonReader(path).d


def _same(x, y):
    return x == y or (x != x and y != y)


def diff(before, after):
    """before / after: {name: flat values} or readers (names / shape / read).
    -> (changed tensor names, changed weight count). Reads one tensor per side
    at a time. A tensor added, removed or reshaped counts as changed, with all
    its elements (the larger size)."""
    rb = _Dict(before) if isinstance(before, dict) else before
    ra = _Dict(after) if isinstance(after, dict) else after
    nb, na = set(rb.names()), set(ra.names())
    names, count = [], 0
    for k in sorted(nb | na):
        if k not in nb or k not in na or rb.shape(k) != ra.shape(k):
            sizes = [loaders._count(r.shape(k)) for r, s in ((rb, nb), (ra, na)) if k in s]
            names.append(k)
            count += max(sizes)
            continue
        n = sum(1 for x, y in zip(rb.read(k), ra.read(k)) if not _same(x, y))
        if n:
            names.append(k)
            count += n
    return names, count


def run(path, edit_id, before_path, after_path, auditor_id, auditor_class="human", date=None, load=None):
    """load: optional path -> {name: flat values}; default picks a reader by
    extension (loaders.open_checkpoint)."""
    opener = load or loaders.open_checkpoint
    names, count = diff(opener(before_path), opener(after_path))
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
        sys.stderr.write("usage: audit.py EDIT_ID BEFORE AFTER (.safetensors | .npz | .json) --auditor ID [--ledger L]\n")
        return 2
    try:
        rec = run(path, argv[0], argv[1], argv[2], who, cls)
    except (ledger.LedgerError, loaders.LoaderError) as e:
        print(str(e))
        return 1
    b = rec["body"]
    print("diff_audit %s: %d tensor(s), %d weight(s) changed" % (b["edit_id"], len(b["changed_tensors"]), b["weight_count"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
