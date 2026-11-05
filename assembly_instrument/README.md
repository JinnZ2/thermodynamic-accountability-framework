# assembly_instrument/

Status: co-authored (JinnZ2 + Claude), 2026-11-03. CC0. stdlib only;
runs on python >= 3.5, phone-buildable.

Practical knowledge for making things from local material is split
across literatures and practitioner communities that no one person
reads all of. This instrument joins the fragments BY FUNCTION, so an
AI can assemble a working option set from what is present in an
environment, and it marks every join so the person with hands knows
what still needs testing.

```text
schema.json                  entry format; x-rules holds the rules validate.py enforces
entry_template.md            paper/markdown mirror of the schema, 1:1
seeds/lighting.json          F-LIGHT-01   interior lighting without batteries   4 branches
seeds/shelter_envelope.json  F-SHELTER-01 shelter envelope without dimensional lumber  6 branches
validate.py                  gate: PASS/FAIL per branch + failing field; exit 1 on any failure
                             --ledger adds R6: field CAUTION must appear in the entry
feedback_schema.json         FieldReport: junction_id + outcome required, rest optional, no personal ids
refs.py                      junction address F-LIGHT-01.1.J4 + 8-hex version of the method text
compact.py                   FieldReport <-> one SMS/radio line; personal-identifier guard
ledger.py                    append-only JSONL, sha256 chained; verify; merge (union by hash,
                             origin node(s) + merge event kept per record: mergeprov.py, M11)
status.py                    per-junction field status from the ledger, triage-ordered
checkout.py                  prints cautions first, then the entry, then reporter free text
                             in a separate "unverified field note" block (M13); logs the handout
tests/test_feedback.py       python3 -m unittest discover -s tests (prints its count)
```

## ORDER OF USE (part of the instrument)

```text
1. POSITION ON THE HISTORICAL LADDER
2. INVENTORY WHAT IS ACTUALLY IN THE ENVIRONMENT
3. THEN PICK THE MATERIAL
```

Starting from the material imports someone else's constraints.

Gloss on step 1, PROPOSED**: the ladder position is which rung of
technique the present inputs can actually support (no grid? no store
fasteners? no sawn lumber? no kiln heat?). The rung decides which
branches are candidates at all. Inventory (step 2) is then taken
against the `inputs` of those branches, and material (step 3) falls out
of what is both present and called for.

## Flow

```text
function needed ──> entry (one per function, never per material)
                       │
          ┌────────────┼────────────┐
          v            v            v
       branch A     branch B     branch C      each: inputs, climate_window, output
          │                                     scope_stamp (date + environment)
          v
   J1 ──> J2 ──> J3 ──> J4                      each junction: provenance, source,
   DOC    INF    INF    DOC(irreversible)                       irreversible, hazard
          └──┬──┘
       consecutive INFERRED  -> compounding_error
   chain_length > 3          -> TEST_EACH_JUNCTION_THEN_FULL_TRIAL
   any irreversible          -> plain hazard line required; floor TEST_EACH_JUNCTION
          │
          v
   build -> result -> new TESTED junction record (results_return) -> entry gets truer
```

Where the loss happens: every INFERRED_BY_ASSEMBLY junction is a join
nobody has recorded working. Untested joins compound, so the
verification level rises with chain length. Every seed branch here is
assembled. **Nothing in the seeds is TESTED.**

## Validator

```sh
python3 validate.py seeds/lighting.json seeds/shelter_envelope.json
python3 validate.py --selftest        # plants one defect per rule; prints its own count
```

```text
FAILS ON (work order)                                   ALSO (consistency)
R1 junction with no provenance tag                      C1 chain_length != junction count
R2 branch with no scope_stamp, or no date / environment C2 verification level != rule
R3 irreversible with empty or jargon-only hazard        C3 entry safety flags disagree
R4 chain_length > 3 without matching verification          with the branches
R5 TESTED with source null (junction or output)         C4 schema shape / type / enum
```

Commit gate (optional, local):

```sh
printf '#!/bin/sh\npython3 assembly_instrument/validate.py assembly_instrument/seeds/*.json\n' \
  > .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit
```

## What the seeds carry, and what they do not

```text
F-LIGHT-01    every flame branch has an IRREVERSIBLE indoor-burning junction with a
              plain carbon monoxide line; the one non-flame branch (glowing fungi)
              gives marker light only, <<1 lm**
F-SHELTER-01  wall branches and span branches are separated: earth, stone and straw
              carry load; laminated small wood spans; fieldstone spans only as far as
              one stone or by corbelling. Cattail/clay/lime is DOCUMENTED by
              practitioner report only, not TESTED. Straw "lignin binding" is the
              thinnest claim in the set (INFERRED_BY_ASSEMBLY, ***)
```

- Literature sources in the seeds were cited from model knowledge and
  **not checked this session**; each says so and carries an asterisk.
  Checking a source is a provenance event: edit the source string,
  drop the "not checked" note, keep the tag.
- Quantities are mostly `NOT MEASURED`. That is the honest value; the
  first build supplies the number.
- Hazard legibility is a word-list check (`JARGON` in validate.py). It
  catches jargon-only lines; it cannot prove a line is understood.
  `reader_state: true` means "passed the check", not "verified with a
  reader".**
- The verification levels are an ordering rule, not calibrated
  against build-failure data (PROPOSED***).

## Report back (closes the loop)

Without a way back, errors never correct. One line, outcome word
required, everything else optional:

```text
FR1|F-LIGHT-01.1.J4||UNSAFE|lamp in closed cabin, headache by morning
    address         outcome  what happened
```

```text
fields   FR1|address|version|outcome|what happened|as built vs specified|temp|humidity|
         climate|soil/water|scale|time to outcome|relation|date|region
outcome  W worked | P partial | F failed | U UNSAFE      (whole words also accepted)
scale    b bench | s small | f full        relation  h hands-on | o observed | 2 secondhand
```

`python3 compact.py template` prints the numbered field guide.
`checkout.py` prints every step address and version at the bottom
of the handout.

**Never include:** names, phone numbers, call signs, addresses or
exact coordinates. `compact.py` rejects anything that looks like one.
The check is a heuristic; it may miss things.*

### Flow

```text
checkout.py ──> handout (cautions on top) ──> build ──> FR1 line (SMS / radio / paper)
     │ logs "checkout"                                          │
     v                                                          v
  ledger.jsonl  <── ledger.py add ──────────────────────────────┘
     │   append-only, sha256 chained; ledger.py merge A B OUT unions devices by hash
     v
  status.py ──> per junction:
                CAUTION                UNSAFE anywhere, or failed on an irreversible step
                ENVIRONMENT_DEPENDENT  worked AND failed both reported; grouped by
                                       environment, never averaged
                ELIGIBLE_FOR_TESTED    >= 3 independent builds (distinct date + region,
                                       hands-on, small/full scale, current version)
                REPORTED               reports, not enough builds
                UNCONFIRMED            handed out, nothing back: silence is not success
                NOT_DISTRIBUTED        never handed out
     │
     v
  validate.py --ledger ──> R6 fails the entry until a person adds a plain
                           `caution` line to every irreversible step in CAUTION
```

### How the asymmetry is built

- **Warnings travel faster than confirmations.**
  - One report can raise CAUTION.
  - A report with a blank version, or against older text, still warns.
  - Only current-version, hands-on builds count toward ELIGIBLE.
- **Nothing in the feedback loop writes to an entry.**
  - ELIGIBLE_FOR_TESTED is a prompt. A person changes the tag to TESTED,
    with a source.
  - CAUTION is cleared by a person editing the entry. Editing the method
    text changes its version.
- **Builds are counted, not reports.** Five reports from one build on
  one day in one region count as one build.
- **Duplicates merge.** A line forwarded twice has the same hash, and
  merge keeps one copy. It keeps every origin: each merged record lists
  the device(s) it came from and the merge events it passed through
  (M11). Stripping that block breaks the chain.
- **Reporter words sit below the instrument's words.** A field report's
  free text (failure_point, as_built_vs_specified) never prints among
  the caution lines. It prints last, under UNVERIFIED FIELD NOTES (M13).

### Limits (thin assumptions)

- **The threshold is unchecked.** The default of 3 independent builds is
  a starting rule, not checked against build-failure data.*** It is
  higher than community_black_start D3 (2 sources to ACT) on purpose:
  certifying a method travels to every community, acting stays local.
  See decision T1 in `../community_black_start/coordination_register.json`.
- **The independence key is weak.** A build is identified by date +
  region. Two people building on the same day in the same region count
  as one build; one person reporting two days counts as two.**
- **Bench tests are not builds.** UNSAFE on a reversible step still
  raises caution.**
- **Positional fields can shift.** A missed empty field moves everything
  after it. An enum landing in the wrong slot is rejected, but a shifted
  free-text field is not caught. The warning sits in fields 1-4; stop
  there if unsure.*

<!-- misuse-section:begin (generated; edit docs/misuse_register.json) -->
## How this could be used against its purpose

Pattern level only. Full register: [`docs/misuse_register.md`](../docs/misuse_register.md).

```text
M7  field feedback ledger and FR1 compact reports (links R3, Sybil gap)
     use        Poisoned or fabricated reports, or fake corroboration, push a junction to a status it has not earned.
     mitigated  D-M9
     residual   Merge accepts any well-formed body; independence of reporters is not proven by the ledger.*
     status     DERIVED (first pass)
M10  sha256 chain logs (assembly ledger, judgment ledger, signal chainlog, coordination log)
     use        The newest records can be dropped, or the whole file rebuilt, and the chain still verifies; a warning, denial or dissent can vanish without trace.
     mitigated  D-M10
     residual   Partial: the sidecar head sits next to the ledger, so someone who can rewrite both still passes the local check. Defense is a PUBLISHED head (headrec.py show -> bulletin / radio / paper / another node) checked with headrec.py check LEDGER COUNT:HASH; publishing on a schedule is policy, not code.*
     status     PROPOSED (independent pass)
M11  merge() of two ledgers
     use        Records imported from a forged second file come out with a fresh valid chain; origin is lost.
     mitigated  D-M13
     residual   Partial: every merged record keeps provenance.origins (node + original record hash; a body seen on both sides keeps both) and provenance.merges (each merge event with each input's node, count and head hash); the record hash covers the block, so stripping it breaks verify. Node labels are self-declared, and a forged input file still merges in -- its origin is recorded, not rejected. status.py does not show origins yet.* Queued (2026-11-05): status.py shows record origins.
     status     PROPOSED (independent pass)
M12  self-declared identity strings (human:/ai: roles, recorder, scorer, judge, SIGCAL_MODEL_ID)
     use        Anyone who writes a record can claim any role, node, scorer or model, faking consent, corroboration, coder agreement or the model tested.
     mitigated  D-M12
     residual   Cannot be fully closed without identity infrastructure. Partial mitigations and the logged residual: docs/misuse_M12_identity_note.md.*
     status     PROPOSED (independent pass)
M13  field-report free text printed at the top of a checkout handout as a caution
     use        A report's author controls text printed with the instrument's apparent authority, which can carry misleading instructions.
     mitigated  D-M14
     residual   Partial: caution lines carry only outcome word, region/date and version; reporter free text prints last, in a separate UNVERIFIED FIELD NOTES block, each line labelled 'unverified field note'. No length cap; no human approval step before printing; the text itself is printed as sent.* Queued (2026-11-05): cap free text per field (e.g. 280 chars) with a visible [truncated] marker.
     status     PROPOSED (independent pass)
M14  junction version hash (refs.py) excludes source and caution
     use        Source or caution text can change without the version changing, so a citation can be swapped silently.
     mitigated  none yet
     residual   Unmitigated. Proposed: include source and caution in the hash; log source edits as provenance events.*
     status     PROPOSED (independent pass)
M15  merged feedback ledger and checkout log (entry, date, coarse region, environment)
     use        Read as a map of where people are building shelter or light and what they lack.
     mitigated  none yet
     residual   Unmitigated. Proposed: fixed coarse-region list, optional date, keep checkout logs local and out of merges.*
     status     PROPOSED (independent pass)
M16  plain-language lines sent by radio or SMS (assembly FR1 compact lines, black-start to_paper lines)
     use        Clear-text broadcast of who holds what or what failed; the PII guard is pattern-only and misses call signs and place names.
     mitigated  none yet
     residual   Unmitigated. Proposed: pre-agreed item codes on air; local place / call-sign blocklist; state that radio is public.*
     status     PROPOSED (independent pass)
M17  validate.py PASS
     use        A structural PASS is borrowed to make an entry look safety-reviewed.
     mitigated  none yet
     residual   Unmitigated. Proposed: print 'structure only, not a safety review' with every PASS.*
     status     PROPOSED (independent pass)
```

| mitigation | what |
|---|---|
| D-M10 | Head record per ledger: count + head hash in LEDGER.head.json, rewritten on each append; append and verify refuse a truncated or rebuilt chain; check against a published head with headrec.py check LEDGER COUNT:HASH. |
| D-M12 | Design note only: why self-declared identities cannot be fully fixed here; partial mitigations (contact_paths, steward attestation, two-person rule, chain + head) and the residual. |
| D-M13 | Merge keeps provenance: each output record carries provenance.origins (node + original record hash, all sides kept) and provenance.merges (merge events, input nodes, counts, heads); hash covers provenance; node labels must differ; mergeprov.missing_origins() checks nothing was dropped. |
| D-M14 | Field-report free text never prints among caution lines: status rows split caution (instrument lines) from field_notes (reporter text); checkout and status print field notes last, in a separate block headed UNVERIFIED FIELD NOTES, each line 'unverified field note -- ...'. |
| D-M9 | Misuse section per module: each README has 'How this could be used against its purpose' listing its M-entries and mitigations. |
<!-- misuse-section:end -->
