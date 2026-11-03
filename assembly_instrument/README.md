# assembly_instrument/

Status: co-authored (Kavik + Claude), 2026-11-03. CC0. stdlib only;
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
