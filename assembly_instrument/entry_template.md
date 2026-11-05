# Entry template -- mirrors schema.json

Status: co-authored (Kavik + Claude), 2026-11-03. CC0.

Fill this on paper or in a text editor, then transcribe to
`seeds/<function>.json` and run `python3 validate.py seeds/<function>.json`.
Every field below maps 1:1 to a key in `schema.json`. Thin claims get
trailing asterisks (more = thinner).

```text
STEP 0  (before this template) -- ORDER OF USE, see README:
        ladder position -> inventory of what is present -> then material
```

---

```text
schema_version   0.1.0
status           co-authored
function_id      F-____-__
function         <what is NEEDED, as a requirement -- not a material>
requirement_note <what the requirement is underneath the familiar answer>
```

## safety_scope (entry level, all five required)

```text
results_return     <how a build failure gets reported back into this entry>
irreversibility    true | false   <- true iff ANY junction below is irreversible
compounding_error  true | false   <- true iff any branch chain_length > 3
                                     OR 2+ consecutive INFERRED_BY_ASSEMBLY junctions
local_validity     climate:         <bounds>
                   soil:            <bounds>
                   water_chemistry: <bounds>
                   altitude:        <bounds>
reader_state       true | false   <- true iff every irreversible hazard line is plain
                                     language an untrained reader can act on
```

## branch (repeat per candidate way)

```text
name             <short name>

inputs
  materials      <list>
  tools          <list>
  skills         <list>

climate_window
  works          <conditions where it works>
  fails          <conditions where it fails>

output
  delivers       <what it actually delivers, plain>
  quantities     quantity | value (string; "NOT MEASURED" is allowed) | units
                 | provenance | source

junctions        one row per joining step, in build order
  id   step                       provenance             source        irreversible  hazard
  J1   <step>                     TESTED|DOCUMENTED|     <citation or  true|false    <plain line,
                                  INFERRED_BY_ASSEMBLY    practitioner,               REQUIRED if
                                                          or null>                    irreversible>

scope_stamp
  date           YYYY-MM-DD                       <- required
  environment    climate / soil / water_chemistry / altitude   <- required
  conditions     <what the claim was established under>

chain_length     <count of junctions>

verification_required
  level          SINGLE_BUILD_CHECK                  chain 0-1
                 TEST_EACH_JUNCTION                  chain 2-3, or any irreversible junction
                 TEST_EACH_JUNCTION_THEN_FULL_TRIAL  chain > 3
  reason         <why this level>

notes            <optional>
```

## Hazard line rules (checked by validate.py)

```text
- required, non-empty, whenever irreversible is true
- at least 8 plain words; jargon (e.g. "CO", "asphyxiation", "ventilate per code")
  no more than 25% of the words
- says what can happen to a body, and the one or two things that prevent it
- no method vocabulary: a reader with no training must be able to act on it
```

## Provenance ladder (no silent upgrades)

```text
INFERRED_BY_ASSEMBLY  joined here by function; nobody has recorded this join working
DOCUMENTED            recorded in a named source; not built by this instrument
TESTED                built and checked by a named source under the stamped conditions
                      -- source may NEVER be null
```

A claim moves up only with a new source. A failed build is recorded
as a TESTED junction that failed; it is never deleted.
