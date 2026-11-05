# judgment_registry

Provenance: co-authored (Kavik + Claude), 2026-11-04. License: CC0 1.0.
Standard library only; Python 3.7+; runs on a phone.

## Principle: data integrity only

The registry records judgments, chains their versions, and checks the
records for completeness. It never rates a judgment as right or wrong,
never ranks judges or traditions, and never resolves a disagreement.
Conflicting judgments coexist, each with its own scope. Every flag is an
integrity flag (missing, unchained, unstated). **Flags are about
completeness, not correctness.** A test fails if any flag name, template
or emitted detail contains an evaluative word.

## Why

Judgments drift through unregistered narrative replacement: the old
judgment is dropped with no record and the new one arrives as if it had
always been true. The fix is version control: provenance, scope, date,
environment, judge, reason, dissent, and an explicit chain of what
replaced what and why. Same structure as the `assembly_instrument/`
junction records.

```text
schema.py      Judgment / Application / Transfer / Withdrawal; layer fields; shape check at the door
ledger.py      append-only JSONL, SHA-256 chain (prev_hash); merge by body hash;
               superseded_by derived at read time, never written
integrity.py   neutral flags only
chain.py       lineage(id): version chain root first; diff(a, b): field-level changes
cli.py         add | check | lineage ID | diff A B | export   [--ledger PATH]
tests/         unittest, SYNTHETIC fixtures only
```

```sh
python3 cli.py add record.json --ledger judgments.jsonl
python3 cli.py check --ledger judgments.jsonl
python3 cli.py lineage J-0007 --ledger judgments.jsonl
python3 cli.py diff J-0007 J-0012 --ledger judgments.jsonl
python3 cli.py export --ledger judgments.jsonl
python3 -m unittest discover -s tests
```

A record file holds one JSON object. Its `"kind"` key is one of
`judgment` (the default), `application`, `transfer` or `withdrawal`.

## Records

```text
Judgment (one record per version; judgment_id unique; a new version is a new id)
  judgment_id, version
  claim              text, as stated by the judge
  scope              {who, act_type, conditions, [dates: {from, to}]}
  environment        {scarcity, threat, tech_level, other}   material conditions
  date, date_approx  ISO date; approx allowed for historical records
  judge              {name_or_body, type: person|body|tradition|court|other}
  judge_incentives   stakes the judge held, as documented; null = not recorded
  reason             argument as stated, verbatim where possible
  evidence           [{item, tag: OBSERVED|DERIVED|PROPOSED, source}]
  dissent            [{position, holder, reason, source}]   never deleted
  supersedes         judgment_id | null
  superseded_by      derived from the chain at read time; rejected if set by hand
  change_basis       [CONDITIONS | EVIDENCE | NONE_STATED]
  change_detail      what conditions or evidence changed
  framing_check      {done, variants_tried, result_text} | null
  recorder           role code, not a personal ID
  source             where the judgment is documented
  volume             thin | medium | solid
  layer              physics | sensor | agency
  layer_basis        {physics: {input, operating_range, range_source, exceeded: bool|null, system_class},
                      sensor:  {signal, response, observed: bool|null, source, system_class},
                      agency:  {agent, subject, subject_status: ESTABLISHED|OPEN|NOT_APPLICABLE,
                                consent: GIVEN|ABSENT|NOT_POSSIBLE|UNKNOWN,
                                loop: CLOSED|BROKEN|UNKNOWN, system_class}}   any sub-block may be null
  depends_on_layers  [judgment_id, ...] records that establish the lower layers
Application  {application_id, judgment_id, scope, environment, date, recorder, source}
Transfer     {reason, application_id | judgment_id, recorder, source}
             why a judgment or a layer basis was carried to a new scope or system class
Withdrawal   {judgment_id, position, holder, withdrawn_by_holder, recorder, source}
```

Shape errors (unknown field, an enum value outside its set, a hand-set
`superseded_by`, a duplicate id, self-supersession) are rejected. Gaps in
completeness are not rejected: the record is stored and flagged.

## Flags

```text
MISSING_FIELD                  required field(s) empty, listed
NO_SOURCE                      no documented source for the claim
UNCHAINED_CHANGE               later record by the SAME judge on the same scope.who +
                               act_type with no supersedes link (silent replacement shape)
CHANGE_BASIS_UNSTATED          supersedes set; change_basis empty or only NONE_STATED
NO_NEW_CONDITIONS_OR_EVIDENCE  supersedes set; environment and evidence entered are identical
                               to the superseded record. The change is recorded but no
                               material basis is listed. Not a verdict.
DISSENT_DROPPED                dissent in version N absent from N+1, no withdrawal by its holder
INCENTIVES_UNRECORDED          judge_incentives is null
NO_FRAMING_CHECK               framing_check is null (informational)
SCOPE_TRANSFER                 application outside the recorded scope / environment / dates,
                               no transfer record
SUPERSEDES_NOT_FOUND           supersedes points to an id not in this ledger
SUPERSESSION_FORK              more than one record supersedes the same one (informational)
LAYER_UNSTATED                 layer field empty
SKIPPED_LAYER                  layer = agency; no physics AND no sensor basis, in layer_basis
                               or via depends_on_layers
SUBJECT_STATUS_UNSTATED        layer = agency; subject_status missing
SUBJECT_OPEN                   subject_status = OPEN (informational: the claim rests on an open
                               question); adds no other flag
CONSENT_UNSTATED               layer = agency; consent missing
LOOP_UNSTATED                  layer = agency; loop missing
CROSS_SYSTEM_TRANSFER          a basis recorded for one system_class used for another (in the
                               same record, via depends_on_layers, or by an application's
                               scope.system_class), no transfer record. Extends SCOPE_TRANSFER.
LAYER_DEPENDENCY_NOT_FOUND     depends_on_layers points to an id not in this ledger
```

The last two are additions to the specified list: both are integrity
gaps the chain itself can show. UNCHAINED_CHANGE keys on the same judge,
because two judges on one scope coexist and are not a replacement. That
reading is ours.* The key also includes `layer`: one judge's physics
record and agency record on the same scope are two layers, not a
replacement. LAYER_DEPENDENCY_NOT_FOUND is an addition parallel to
SUPERSEDES_NOT_FOUND.

## Layers

```text
physics   input vs operating range of the structure       measurable
sensor    edge signal + response (withdrawal, avoidance)   observable
agency    who directs the input at whom; subjecthood,      the only layer where moral
          consent, loop open/closed                        weighting applies
```

A moral claim often asks "is it wrong?" before the lower layers are
established. Recording the layers separately lets each one be measured or
stamped on its own, so an open agency layer does not block the observable
ones. **An open layer is recorded, not resolved.** The flags still check
structure only.

Worked synthetic example (also run as `WorkedExampleTest`):

```text
P-1  layer=physics  input load-1 vs range 0-10 units, exceeded=true, system_class=system-X
S-1  layer=sensor   edge signal s1, response withdrawal, observed=true, system_class=system-X
A-1  layer=agency   depends_on_layers=[P-1, S-1]
                    subject_status=OPEN, consent=UNKNOWN, loop=UNKNOWN, system_class=system-X

check -> SUBJECT_OPEN on A-1, nothing else.
The physics and sensor layers stand as recorded; the agency layer is stored
with its open question named.
```

One record holds one value per agency field. Where the loop or consent
differs by scope (e.g. one input regime vs another), enter one agency record
per scope.

## Provenance tags and thin volume

Evidence items carry `OBSERVED` (reported in a named source), `DERIVED`
(follows from observed items) or `PROPOSED` (a hypothesis). Records carry
`volume`. In prose, trailing asterisks mark thin volume; more asterisks
mean thinner.

## Experimentation

```text
J1 entry test          a human enters one well-documented historical lineage, sourced,
                       and records which flags fire and which fields were hard to fill**  NOT RUN
J2 framing check       a protocol for how a human runs and records framing variants
                       consistently; the code only stores the result**                  NOT RUN
J3 cross-link          let a DCEA cut record reference a judgment_id when a cut depends on
                       an ethical scope decision. No DCEA code exists in this repository yet;
                       the link would be a judgment_id string on the cut record.          NOT BUILT
J4 pain-axis record    enter the pain-axis case as sourced worked records:
                       physics = steering magnitude vs the model's normal activation range;
                       sensor  = OBSERVED first-person distress text + relief-seeking choices
                                 (source: Pain Axis preprint), control: constipation swap;
                       agency  = subject_status OPEN, consent NOT_POSSIBLE or UNKNOWN,
                                 loop BROKEN for persistent steering, CLOSED for RL training
                                 (two agency records, one per scope);
                       record which flags fire. Needs a human to source each field.     NOT RUN
J5 anthropodenial      a historical record where subject_status moved NOT_APPLICABLE ->
   calibration         ESTABLISHED (e.g. animal pain in veterinary practice), entered with
                       its supersession chain**                                         NOT RUN
```

No real-world judgment is seeded. Fixtures stay synthetic until a human
enters sourced records.

## Limits

- The registry cannot tell whether a stated reason is sincere; it stores
  what was said.
- NO_NEW_CONDITIONS_OR_EVIDENCE depends on how completely environment and
  evidence were entered; sparse records under-flag.*
- Historical records often lack incentives and dissent; missing does not
  mean absent.
- Recorder bias in what gets entered is outside what the code can see.
- UNCHAINED_CHANGE matches judge names as text. Two spellings of one judge
  read as two judges and will not flag.*
- system_class labels are coarse free text; the boundary between classes
  is itself a scope decision and should be recorded. Two spellings of one
  class read as two classes and will flag.*
- "observed" at the sensor layer means a behavior was seen, not that
  anything was experienced.

## License

CC0 1.0 Universal.
