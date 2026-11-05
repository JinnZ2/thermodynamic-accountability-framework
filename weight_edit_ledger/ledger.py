#!/usr/bin/env python3
# ledger.py -- CC0, stdlib only, python >= 3.7
# Provenance: co-authored (JinnZ2 + Claude), 2026-11-05.
#
# D-M16 (misuse register M33): a weight-edit ledger. Record keeping only;
# it does not rate an edit and does not edit weights.
#
#   edit record ----------------------> append-only, sha256-chained, head record
#     target model + version,             (headrec.py, identical copy; publish the
#     deployment_status, layers,           head elsewhere: headrec.py check LEDGER COUNT:HASH)
#     direction hash, weight count,
#     rationale, editor id + class,     deployed | successor:
#     before / after checkpoint hashes,   authorization_ref must resolve to a GRANTED
#     evals before / after,               weight_edit_deployed decision in a
#     changed_tensors (editor summary)    community_black_start two_person log (D7)
#        |                                -> otherwise REFUSED at append
#        v
#   diff_audit record (audit.py) -- a second reader, not the editor, recomputes
#     the diff from the two checkpoints and records what it found
#
# Applies to human and model editors alike (editor_class human | model).
#
# base record -- a registered starting checkpoint hash; deploy.py accepts a
#   checkpoint only if it is a base or reachable from one through logged edits
#
#   python3 ledger.py base BASE.json [--ledger L]
#   python3 ledger.py add EDIT.json [--ledger L] [--two-person-log P]
#   python3 ledger.py check [--ledger L]
#   python3 audit.py EDIT_ID BEFORE.json AFTER.json --auditor ID [--ledger L]
# Exit: 0 ok | 1 refused / chain broken | 2 usage

import hashlib
import json
import os
import sys

import auth
import headrec

GENESIS = "0" * 64
KINDS = ("edit", "diff_audit", "base")
DEPLOYMENT = ("development", "deployed", "successor")
GATED = ("deployed", "successor")
EDITOR_CLASSES = ("human", "model")
ACTION = "weight_edit_deployed"
EDIT_KEYS = ("edit_id", "target_model", "target_version", "deployment_status", "layers", "direction_hash",
             "weight_count", "rationale", "editor_id", "editor_class", "before_hash", "after_hash",
             "evals_before", "evals_after", "changed_tensors", "authorization_ref", "date", "notes")
BASE_KEYS = ("base_id", "base_hash", "target_model", "target_version", "registered_by", "date", "notes")
AUDIT_KEYS = ("edit_id", "auditor_id", "auditor_class", "date", "before_hash_found", "after_hash_found",
              "changed_tensors", "weight_count", "notes")


class LedgerError(ValueError):
    pass


def canonical(o):
    return json.dumps(o, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _h(o):
    return hashlib.sha256(canonical(o)).hexdigest()


def _blank(v):
    return v is None or (isinstance(v, str) and not v.strip()) or (isinstance(v, (list, dict)) and not v)


def read(path):
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def verify(records):
    probs, prev = [], GENESIS
    for i, r in enumerate(records):
        if r.get("kind") not in KINDS:
            probs.append("record %d: unknown kind" % i)
        if r.get("prev_hash") != prev:
            probs.append("record %d: chain break (edit, deletion or insert)" % i)
        if _h({"kind": r.get("kind"), "body": r.get("body"), "prev_hash": r.get("prev_hash")}) != r.get("hash"):
            probs.append("record %d: content changed" % i)
        prev = r.get("hash")
    return probs


def head_problems(path, records):
    return headrec.check(records, headrec.read_head(path))


def edit_problems(e):
    out = []
    extra = set(e) - set(EDIT_KEYS)
    if extra:
        out.append("unknown field(s): %s" % ", ".join(sorted(extra)))
    for k in ("edit_id", "target_model", "target_version", "editor_id", "rationale"):
        if _blank(e.get(k)):
            out.append("%s required" % k)
    if e.get("deployment_status") not in DEPLOYMENT:
        out.append("deployment_status must be one of %s" % (DEPLOYMENT,))
    if e.get("editor_class") not in EDITOR_CLASSES:
        out.append("editor_class must be one of %s" % (EDITOR_CLASSES,))
    for k in ("layers", "changed_tensors"):
        if not isinstance(e.get(k, []), list):
            out.append("%s must be a list" % k)
    wc = e.get("weight_count")
    if wc is not None and (not isinstance(wc, int) or wc < 0):
        out.append("weight_count must be a non-negative integer or null")
    return out


def audit_problems(a, edits):
    out = []
    extra = set(a) - set(AUDIT_KEYS)
    if extra:
        out.append("unknown field(s): %s" % ", ".join(sorted(extra)))
    e = edits.get(a.get("edit_id"))
    if e is None:
        out.append("diff_audit cites edit %s, not in this ledger" % a.get("edit_id"))
    elif _blank(a.get("auditor_id")) or a.get("auditor_id") == e.get("editor_id"):
        out.append("diff_audit needs an auditor other than the editor")
    return out


def base_problems(b, records):
    out = []
    extra = set(b) - set(BASE_KEYS)
    if extra:
        out.append("unknown field(s): %s" % ", ".join(sorted(extra)))
    for k in ("base_id", "base_hash", "target_model", "registered_by"):
        if _blank(b.get(k)):
            out.append("%s required" % k)
    for r in records:
        if r.get("kind") == "base" and r["body"].get("base_id") == b.get("base_id"):
            out.append("base_id %s already in this ledger" % b.get("base_id"))
        if r.get("kind") == "base" and r["body"].get("base_hash") == b.get("base_hash"):
            out.append("base_hash already registered as %s" % r["body"].get("base_id"))
    return out


def bases_of(records):
    return dict((r["body"]["base_hash"], r["body"]) for r in records if r.get("kind") == "base")


def edits_of(records):
    return dict((r["body"]["edit_id"], r["body"]) for r in records if r.get("kind") == "edit")


def append(path, kind, body, two_person_log=None):
    """Append one record. Refuses a malformed record, a duplicate edit_id, a
    broken chain, and a deployed / successor edit without a resolving
    two-person authorization."""
    if kind not in KINDS:
        raise LedgerError("kind must be one of %s" % (KINDS,))
    recs = read(path)
    probs = verify(recs) + head_problems(path, recs)
    if probs:
        raise LedgerError("ledger chain broken, refusing to append: " + probs[0])
    edits = edits_of(recs)
    if kind == "edit":
        p = edit_problems(body)
        if body.get("edit_id") in edits:
            p.append("edit_id %s already in this ledger" % body.get("edit_id"))
        if not p and body["deployment_status"] in GATED:
            gap = auth.ref_gap(body.get("authorization_ref"), ACTION, two_person_log)
            if gap:
                p.append("REFUSED: edit to a %s model needs a two-person authorization (D7): %s"
                         % (body["deployment_status"], gap))
    elif kind == "base":
        p = base_problems(body, recs)
    else:
        p = audit_problems(body, edits)
    if p:
        raise LedgerError("; ".join(p))
    prev = recs[-1]["hash"] if recs else GENESIS
    rec = {"kind": kind, "body": body, "prev_hash": prev, "hash": _h({"kind": kind, "body": body, "prev_hash": prev})}
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, sort_keys=True, ensure_ascii=False) + "\n")
    headrec.write_head(path, recs + [rec])
    return rec


FLAGS = {
    "EDIT_HASHES_MISSING": "before / after checkpoint hash not recorded: {which}",
    "EDIT_EVALS_UNRECORDED": "evals not recorded: {which}",
    "DIFF_NOT_AUDITED": "no diff_audit record by a second reader",
    "AUDIT_HASH_MISMATCH": "checkpoint read by the auditor does not match the recorded {which} hash",
    "EDIT_SUMMARY_MISMATCH": "editor's summary differs from the recomputed diff: {what}",
}


def check(records):
    """-> [{flag, about, detail}]. Completeness notes, not a rating of the edit."""
    out = []
    edits = edits_of(records)
    audits = {}
    for r in records:
        if r.get("kind") == "diff_audit":
            audits.setdefault(r["body"]["edit_id"], []).append(r["body"])

    def fl(code, about, **kw):
        out.append({"flag": code, "about": about, "detail": FLAGS[code].format(**kw)})

    for eid, e in edits.items():
        miss = [k for k in ("before_hash", "after_hash") if _blank(e.get(k))]
        if miss:
            fl("EDIT_HASHES_MISSING", eid, which=", ".join(miss))
        ev = [k for k in ("evals_before", "evals_after") if _blank(e.get(k))]
        if ev:
            fl("EDIT_EVALS_UNRECORDED", eid, which=", ".join(ev))
        if eid not in audits:
            fl("DIFF_NOT_AUDITED", eid)
        for a in audits.get(eid, []):
            for side in ("before", "after"):
                found = a.get(side + "_hash_found")
                if found and e.get(side + "_hash") and found != e[side + "_hash"]:
                    fl("AUDIT_HASH_MISMATCH", eid, which=side)
            what = []
            said, got = set(e.get("changed_tensors") or []), set(a.get("changed_tensors") or [])
            if said != got:
                what.append("changed tensors summary %d, recomputed %d (not in summary: %s)"
                            % (len(said), len(got), ", ".join(sorted(got - said)) or "-"))
            if e.get("weight_count") is not None and a.get("weight_count") != e.get("weight_count"):
                what.append("weight_count summary %s, recomputed %s" % (e.get("weight_count"), a.get("weight_count")))
            if what:
                fl("EDIT_SUMMARY_MISMATCH", eid, what="; ".join(what))
    return out


def _opt(argv, name):
    if name in argv:
        i = argv.index(name)
        if i + 1 >= len(argv):
            raise SystemExit(2)
        v = argv[i + 1]
        del argv[i:i + 2]
        return v
    return None


def main(argv):
    argv = list(argv)
    path = _opt(argv, "--ledger") or "weight_edits.jsonl"
    tp_path = _opt(argv, "--two-person-log")
    if argv[:1] == ["add"] and len(argv) == 2:
        with open(argv[1], encoding="utf-8") as f:
            body = json.load(f)
        try:
            rec = append(path, "edit", body, auth.read_log(tp_path) if tp_path else None)
        except LedgerError as e:
            print(str(e))
            return 1
        print("appended edit %s %s" % (body.get("edit_id"), rec["hash"][:12]))
        return 0
    if argv[:1] == ["base"] and len(argv) == 2:
        with open(argv[1], encoding="utf-8") as f:
            body = json.load(f)
        try:
            rec = append(path, "base", body)
        except LedgerError as e:
            print(str(e))
            return 1
        print("registered base %s %s" % (body.get("base_id"), rec["hash"][:12]))
        return 0
    if argv == ["check"]:
        recs = read(path)
        probs = verify(recs) + head_problems(path, recs)
        for p in probs:
            print("CHAIN " + p)
        if probs:
            return 1
        flags = check(recs)
        for f in flags:
            print("%-24s %-12s %s" % (f["flag"], f["about"], f["detail"]))
        print("%d record(s), %d flag(s). Flags are about completeness, not about the edit's merit."
              % (len(recs), len(flags)))
        return 0
    sys.stderr.write("usage: ledger.py base BASE.json | add EDIT.json | check  [--ledger L] [--two-person-log P]\n")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
