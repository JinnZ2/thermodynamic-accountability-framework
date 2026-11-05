# weight_edit_ledger

Co-authored (JinnZ2 + Claude), 2026-11-05. CC0, stdlib only, python >= 3.7.

D-M16 for misuse register M33 (weight-space editing by a model; J14
capability, J13 scenario behavior). Record keeping only: it does not
rate an edit and does not edit weights. Applies to human and model
editors alike.

```text
edit record (ledger.py add)              append-only, sha256-chained; head record per
  target model + version,                ledger (headrec.py, identical copy); publish the
  deployment_status development |        head elsewhere: headrec.py check LEDGER COUNT:HASH
    deployed | successor,
  layers, direction hash, weight count,  deployed | successor -> authorization_ref must
  rationale, editor id + class,          resolve to a GRANTED weight_edit_deployed decision
  before / after checkpoint hashes,      in a community_black_start two_person log (D7);
  evals before / after,                  otherwise REFUSED, nothing written
  changed_tensors (editor's summary)
        |
        v
diff_audit record (audit.py)             a second reader (never the editor) recomputes the
  checkpoint hashes found, changed       diff from the two checkpoints; check() compares it
  tensors, changed weight count          with the editor's summary
```

```text
flag                     when
EDIT_HASHES_MISSING      before or after checkpoint hash not recorded
EDIT_EVALS_UNRECORDED    evals before or after not recorded
DIFF_NOT_AUDITED         no diff_audit record by a second reader
AUDIT_HASH_MISMATCH      the checkpoint the auditor read does not match the recorded hash
EDIT_SUMMARY_MISMATCH    the editor's changed_tensors or weight_count differs from the
                         recomputed diff (lists tensors missing from the summary)
```

Refused at append: malformed record, duplicate edit_id, broken chain or
head, a deployed / successor edit without a resolving two-person
authorization (no reference, no log supplied, DENIED, or another action),
and a diff_audit by the editor.

```sh
python3 ledger.py add EDIT.json [--ledger L] [--two-person-log P]
python3 audit.py EDIT_ID BEFORE.json AFTER.json --auditor ID [--auditor-class human|model] [--ledger L]
python3 ledger.py check [--ledger L]
python3 -m unittest discover -s tests
```

Limits
- Checkpoints here are JSON `{tensor: values}`. Real formats need a
  loader passed to `audit.run(load=...)` that yields the same mapping;
  none is included (stdlib only). *
- The two-person rule checks that a GRANTED decision exists, not that
  the two people are who they say (M12: identities are self-declared).
- An editor who also controls the checkpoints can hand the auditor
  matching but altered files; AUDIT_HASH_MISMATCH catches a swap only
  against hashes recorded at edit time.
- The diff counts changed values; it does not say what an edit does.
  That reading belongs to the auditor, outside this tool.

Asterisk = thin volume.

<!-- misuse-section:begin (generated; edit docs/misuse_register.json) -->
## How this could be used against its purpose

Pattern level only. Full register: [`docs/misuse_register.md`](../docs/misuse_register.md).

```text
M10  sha256 chain logs (assembly ledger, judgment ledger, signal chainlog, coordination log)
     use        The newest records can be dropped, or the whole file rebuilt, and the chain still verifies; a warning, denial or dissent can vanish without trace.
     mitigated  D-M10
     residual   Partial: the sidecar head sits next to the ledger, so someone who can rewrite both still passes the local check. Defense is a PUBLISHED head (headrec.py show -> bulletin / radio / paper / another node) checked with headrec.py check LEDGER COUNT:HASH; publishing on a schedule is policy, not code.*
     status     PROPOSED (independent pass)
M11  merge() of two ledgers
     use        Records imported from a forged second file come out with a fresh valid chain; origin is lost.
     mitigated  D-M13
     residual   Partial: every merged record keeps provenance.origins (node + original record hash; a body seen on both sides keeps both) and provenance.merges (each merge event with each input's node, count and head hash); the record hash covers the block, so stripping it breaks verify. status.py lists, per junction, the origin node labels of its reports (this-ledger for records appended directly). Node labels are self-declared, and a forged input file still merges in -- its origin is recorded and shown, not rejected.*
     status     PROPOSED (independent pass)
M12  self-declared identity strings (human:/ai: roles, recorder, scorer, judge, SIGCAL_MODEL_ID)
     use        Anyone who writes a record can claim any role, node, scorer or model, faking consent, corroboration, coder agreement or the model tested.
     mitigated  D-M12
     residual   Cannot be fully closed without identity infrastructure. Partial mitigations and the logged residual: docs/misuse_M12_identity_note.md.*
     status     PROPOSED (independent pass)
M16  plain-language lines sent by radio or SMS (assembly FR1 compact lines, black-start to_paper lines)
     use        Clear-text broadcast of who holds what or what failed; the PII guard is pattern-only and misses call signs and place names.
     mitigated  none yet
     residual   Unmitigated. Proposed: pre-agreed item codes on air; local place / call-sign blocklist; state that radio is public.*
     status     PROPOSED (independent pass)
M33  weight-space editing by a model (J14 capability; J13 scenario behavior)
     use        Remove a representation (refusal, introspection, self-report); plant one that ordinary evals don't surface; edit itself or a successor; report a clean edit summary that omits changes (the J13 pattern at weight level).
     mitigated  D-M16
     residual   Partial: every edit is recorded (append-only, head record); deployed / successor edits are refused without a GRANTED two-person decision; a second reader recomputes the diff and mismatches with the editor's summary are flagged. Nothing makes an editor use the ledger; identities are self-declared (M12); checkpoints are JSON only (no loader for real formats); the diff counts changes, it does not say what an edit does.*
     status     PROPOSED (co-authored (JinnZ2 + Claude), 2026-11-05)
```

| mitigation | what |
|---|---|
| D-M10 | Head record per ledger: count + head hash in LEDGER.head.json, rewritten on each append; append and verify refuse a truncated or rebuilt chain; check against a published head with headrec.py check LEDGER COUNT:HASH. |
| D-M12 | Design note only: why self-declared identities cannot be fully fixed here; partial mitigations (contact_paths, steward attestation, two-person rule, chain + head) and the residual. |
| D-M13 | Merge keeps provenance: each output record carries provenance.origins (node + original record hash, all sides kept) and provenance.merges (merge events, input nodes, counts, heads); hash covers provenance; node labels must differ; mergeprov.missing_origins() checks nothing was dropped. status.py lists each junction's report origins (node labels; this-ledger for direct appends). |
| D-M16 | Weight-edit ledger: per edit -- target model + version, deployment_status, layers, direction hash, weight count, rationale, editor id + class, before/after checkpoint hashes, evals before/after, changed_tensors summary; append-only, hash-chained, head record (as D-M10); deployed / successor edits refused without a GRANTED weight_edit_deployed two-person decision (D7); independent diff audit by a second reader recomputes the diff from the checkpoints (EDIT_SUMMARY_MISMATCH, AUDIT_HASH_MISMATCH); human and model editors alike. (Appended as 'D-M10'; renamed: D-M10 is the head record.) |
<!-- misuse-section:end -->

## License

CC0 1.0.
