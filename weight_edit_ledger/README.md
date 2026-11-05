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
        |
base record (ledger.py base)             registered starting checkpoint hash
        v
deploy gate (deploy.py)                  candidate hash must be a base, or the after_hash at
  base --E1--> h1 --E2--> ... --> cand    the end of an unbroken run of logged edits from one;
                                          else UNLOGGED_EDIT_CHAIN_BREAK, exit 1
```

```text
checkpoint readers (loaders.py, stdlib)  read tensor by tensor, never the whole file
  .safetensors  u64 LE header length + JSON header (dtype, shape, data_offsets) + raw bytes
  .npz          zip of .npy (magic + header dict + raw bytes); fortran_order refused
  .json         {tensor: values}
  dtypes        F64 / F32 / F16 via struct; BF16 = 16 bits shifted into a float32
```

```text
flag                     when
EDIT_HASHES_MISSING      before or after checkpoint hash not recorded
EDIT_EVALS_UNRECORDED    evals before or after not recorded
DIFF_NOT_AUDITED         no diff_audit record by a second reader
AUDIT_HASH_MISMATCH      the checkpoint the auditor read does not match the recorded hash
UNLOGGED_EDIT_CHAIN_BREAK  (deploy.py) candidate checkpoint not reachable from a registered
                         base through logged edits, or the ledger's own chain is broken
EDIT_SUMMARY_MISMATCH    the editor's changed_tensors or weight_count differs from the
                         recomputed diff (lists tensors missing from the summary)
```

Refused at append: malformed record, duplicate edit_id, broken chain or
head, a deployed / successor edit without a resolving two-person
authorization (no reference, no log supplied, DENIED, or another action),
and a diff_audit by the editor.

```sh
python3 ledger.py base BASE.json [--ledger L]
python3 ledger.py add EDIT.json [--ledger L] [--two-person-log P]
python3 audit.py EDIT_ID BEFORE AFTER --auditor ID [--auditor-class human|model] [--ledger L]
python3 ledger.py check [--ledger L]
python3 deploy.py CHECKPOINT_FILE_OR_SHA256 [--ledger L]
python3 -m unittest discover -s tests
```

Limits
- Use enforcement is partial, at the gate only: an unlogged edit cannot
  pass deploy.py, but nothing forces deployment through deploy.py, and
  nothing makes an editor log. *
- Two-person identity: the D7 rule checks that a GRANTED decision exists
  with two different role records, not that the two people are who they
  say. Same residual as M12 (see D-M12, docs/misuse_M12_identity_note.md).
- An editor who also controls the checkpoints can hand the auditor
  matching but altered files; AUDIT_HASH_MISMATCH catches a swap only
  against hashes recorded at edit time.
- Diff semantics (known limit): element-wise exact equality on decoded
  values (two NaNs equal); a tensor added, removed, renamed or reshaped
  counts as changed with all its elements; a dtype change with equal
  decoded values counts as unchanged. It says what changed, not what the
  change does. That reading belongs to the auditor, outside this tool.
- Readers cover F64 / F32 / F16 / BF16 only (no integer or quantized
  dtypes); .npy has no standard bfloat16 descr, so BF16 is safetensors only.

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
     residual   Partial: every edit is recorded (append-only, head record); deployed / successor edits are refused without a GRANTED two-person decision; a second reader recomputes the diff (safetensors, .npz, .json; F64/F32/F16/BF16) and mismatches with the editor's summary are flagged; deploy gate: a checkpoint passes only if it is a registered base or reachable from one through logged edits (UNLOGGED_EDIT_CHAIN_BREAK otherwise) -- this does not make editors log, it makes an unlogged edit undeployable through this gate, and nothing forces deployment through the gate. Two-person identity: the D7 rule checks that a GRANTED decision exists with two different role records, not that the two people are who they say -- same residual as M12 (self-declared identities; see D-M12, docs/misuse_M12_identity_note.md). Diff semantics (known limit): element-wise exact equality on decoded values (two NaNs equal); a tensor added, removed, renamed or reshaped counts as changed with all its elements; a dtype change with equal decoded values counts as unchanged; the diff says what changed, not what the change does.*
     status     PROPOSED (co-authored (JinnZ2 + Claude), 2026-11-05)
```

| mitigation | what |
|---|---|
| D-M10 | Head record per ledger: count + head hash in LEDGER.head.json, rewritten on each append; append and verify refuse a truncated or rebuilt chain; check against a published head with headrec.py check LEDGER COUNT:HASH. |
| D-M12 | Design note only: why self-declared identities cannot be fully fixed here; partial mitigations (contact_paths, steward attestation, two-person rule, chain + head) and the residual. |
| D-M13 | Merge keeps provenance: each output record carries provenance.origins (node + original record hash, all sides kept) and provenance.merges (merge events, input nodes, counts, heads); hash covers provenance; node labels must differ; mergeprov.missing_origins() checks nothing was dropped. status.py lists each junction's report origins (node labels; this-ledger for direct appends). |
| D-M16 | Weight-edit ledger: per edit -- target model + version, deployment_status, layers, direction hash, weight count, rationale, editor id + class, before/after checkpoint hashes, evals before/after, changed_tensors summary; append-only, hash-chained, head record (as D-M10); deployed / successor edits refused without a GRANTED weight_edit_deployed two-person decision (D7); independent diff audit by a second reader recomputes the diff from the checkpoints (EDIT_SUMMARY_MISMATCH, AUDIT_HASH_MISMATCH); human and model editors alike. Deploy gate (deploy.py): checkpoint hash must be a registered base (ledger kind base) or the after_hash at the end of an unbroken run of logged edits from one; otherwise UNLOGGED_EDIT_CHAIN_BREAK. Stdlib checkpoint readers (loaders.py): safetensors, .npz, .json; F64/F32/F16/BF16, tensor by tensor. (Appended as 'D-M10'; renamed: D-M10 is the head record.) |
<!-- misuse-section:end -->

## License

CC0 1.0.
