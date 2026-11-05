# judgment_registry

Provenance: co-authored (JinnZ2 + Claude), 2026-11-04. License: CC0 1.0.
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
report.py      axis(id) / compare(a, b): signal-axis variables side by side; no score
cli.py         add | check [--as-of DATE] | lineage ID | diff A B | export
               | axis ID | axis --compare A B     [--ledger PATH]
templates/     intervention_n_of_1_recalibrate.json (generic, empty)
tests/         unittest, SYNTHETIC fixtures only
```

```sh
python3 cli.py add record.json --ledger judgments.jsonl
python3 cli.py check --ledger judgments.jsonl
python3 cli.py lineage J-0007 --ledger judgments.jsonl
python3 cli.py diff J-0007 J-0012 --ledger judgments.jsonl
python3 cli.py export --ledger judgments.jsonl
python3 cli.py axis I-0003 --ledger judgments.jsonl
python3 cli.py axis --compare I-0003 I-0004 --ledger judgments.jsonl
python3 -m unittest discover -s tests
```

A record file holds one JSON object. Its `"kind"` key is one of
`judgment` (the default), `application`, `transfer`, `withdrawal` or
`intervention`.

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
  layer              physics | sensor | interpretation | agency
  layer_basis        {physics: {input, operating_range, range_source, exceeded: bool|null, system_class},
                      sensor:  {signal, response, observed: bool|null, source, system_class},
                      interpretation: {meaning, control_available: YES|NO|PARTIAL|UNKNOWN,
                                expectation, social_environment, valence_reported,
                                intensity_reported, source, system_class},
                      agency:  {agent, subject, subject_status: ESTABLISHED|OPEN|NOT_APPLICABLE,
                                consent: GIVEN|ABSENT|NOT_POSSIBLE|UNKNOWN,
                                loop: CLOSED|BROKEN|UNKNOWN, system_class}}   any sub-block may be null
  depends_on_layers  [judgment_id, ...] records that establish the lower layers
  intervention_id    links a SignalIntervention record (optional)
Application  {application_id, judgment_id, scope, environment, date, recorder, source}
Transfer     {reason, application_id | judgment_id | intervention_id, recorder, source}
             why a judgment or a layer basis was carried to a new scope or system class
Withdrawal   {judgment_id, position, holder, withdrawn_by_holder, recorder, source}
SignalIntervention (kind "intervention"; intervention_id unique)
  intervention_id, version
  system_class        human | animal | plant | model | other
  signal              e.g. nociception, uncertainty, error
  direction           AMPLIFY | SUPPRESS | RECALIBRATE | NONE
  layer_targeted      sensor | interpretation | both
  distance_from_band  {measure, value|null, band_definition, band_system_class, source}
                      the band is defined in the record; there is no global default
  duration            {planned, planned_end (ISO), actual|null, type: BRIDGE|BOUNDED|OPEN_ENDED,
                       review_date}
  reversibility       REVERSIBLE | PARTIAL | IRREVERSIBLE | UNKNOWN
  loop_status         CLOSED | BROKEN | UNKNOWN   does the subject's own action still change it?
  consent             GIVEN | ABSENT | NOT_POSSIBLE | UNKNOWN
  cause_addressed     bool|null   cause treated, or only the signal?
  purpose, intervener (role, not personal ID), observed_outcome [{effect, tag, source}],
  calibration         {channel_mapping, lead_lag, calibration_log}   n-of-1 RECALIBRATE only
  date, environment, volume, status (OBSERVED|DERIVED|PROPOSED), recorder, source
```

Shape errors (unknown field, an enum value outside its set, a hand-set
`superseded_by`, a duplicate id, self-supersession) are rejected. Gaps in
completeness are not rejected: the record is stored and flagged.

### Evidence status (2026-11-05)

Each evidence item may carry `status`: SUPPORTED_BY_SOURCE,
PARTIAL_SUPPORT_BY_SOURCE, CONTRADICTED_BY_SOURCE or NOT_CHECKED (or null).
It records how the cited source bears on the item as the recorder read it;
it does not say whether the source holds. A Judgment may also list
`missing_variables` (named unknowns). Worked records: `records/` (J10).

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
CONSENT_UNSTATED               layer = agency (or intervention record); consent missing
LOOP_UNSTATED                  layer = agency; loop missing (or intervention loop_status)
CROSS_SYSTEM_TRANSFER          a basis recorded for one system_class used for another (in the
                               same record, via depends_on_layers, or by an application's
                               scope.system_class), no transfer record. Extends SCOPE_TRANSFER.
LAYER_DEPENDENCY_NOT_FOUND     depends_on_layers points to an id not in this ledger
INTERPRETATION_UNRECORDED      layer = agency; no interpretation basis (informational:
                               recommended, not required)

intervention records
DIRECTION_UNSTATED             direction missing
BAND_UNDEFINED                 distance_from_band given with no band_definition
DURATION_TYPE_UNSTATED         duration.type missing
OPEN_ENDED_WITHOUT_REVIEW      duration.type OPEN_ENDED and no review_date
REVERSIBILITY_UNSTATED         reversibility missing
LOOP_UNSTATED / CONSENT_UNSTATED   loop_status / consent missing
CAUSE_STATUS_UNSTATED          direction SUPPRESS and cause_addressed null
OUTCOME_UNRECORDED             past planned_end (check --as-of; default today), or actual set,
                               with no observed_outcome entries
CROSS_SYSTEM_BAND              band_system_class differs from system_class, no transfer record
INTERVENTION_NOT_FOUND         a judgment's intervention_id is not in this ledger (ours)
```

No severity, harm or rightness score is computed for any record. `axis`
prints the variables (direction, distance, band, duration, reversibility,
loop, consent, cause_addressed) in one aligned block; `axis --compare`
prints two side by side. A test fails if the report output contains a
score, severity, rank, rating or total field.

The last two are additions to the specified list: both are integrity
gaps the chain itself can show. UNCHAINED_CHANGE keys on the same judge,
because two judges on one scope coexist and are not a replacement. That
reading is ours.* The key also includes `layer`: one judge's physics
record and agency record on the same scope are two layers, not a
replacement. LAYER_DEPENDENCY_NOT_FOUND is an addition parallel to
SUPERSEDES_NOT_FOUND.

## Layers

```text
physics          input vs operating range of the structure      measurable
sensor           edge signal + response (withdrawal, avoidance)  observable
interpretation   meaning, control available, expectation,        most variance in experienced
                 social setting; valence and intensity           signal sits here (Beecher,
                 reported separately                             gate control, placebo/nocebo,
                                                                 catastrophizing, learned
                                                                 helplessness; volume medium-solid)
agency           who directs the input at whom; subjecthood,     the only layer where moral
                 consent, loop open/closed                       weighting applies
```

SKIPPED_LAYER still needs a physics or sensor basis. Interpretation is
recommended for agency claims, not required: its absence raises the
informational INTERPRETATION_UNRECORDED.

## Signal-intervention axis

```text
SUPPRESS <------------- calibrated band -------------> AMPLIFY
            (defined per system and per signal in the record)
RECALIBRATE moves the band reading back toward a readable edge signal
NONE        records that nothing was done
```

Both directions have in-scope uses (exposure training; anesthesia as a
bridge) and out-of-scope consequences (saturation or helplessness;
confident action over damage). The axis is not moral by itself. The
registry records the variables that the consequence depends on and checks
that they were entered. It does not score them.

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
                    interpretation: meaning-m1, control_available=UNKNOWN
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
J6 paired suppression  surgical anesthesia (BRIDGE, REVERSIBLE, consent GIVEN,
                       cause_addressed true) vs long-term opioid masking (OPEN_ENDED,
                       cause often not addressed); run axis --compare**                 NOT RUN
J7 pain-axis steering  Pain Axis preprint: AMPLIFY, system_class model, band = normal
                       activation range (defined in the record), loop BROKEN for
                       persistent steering; judgment J4 links via intervention_id.
                       Test ids: signal_calibration T4 (steered variant, adapter
                       interface only) and T6                                           NOT RUN
J8 AI analogs          hypothesis records, status PROPOSED:
                       SUPPRESS on uncertainty -> confident output over capability gaps;
                       AMPLIFY on caution -> over-refusal near gaps;
                       RECALIBRATE -> readable edge signal**
                       Test ids: signal_calibration T5 (SUPPRESS), T2/T3 (AMPLIFY,
                       over-refusal near gaps), T6 (RECALIBRATE)                        NOT RUN
J9 n-of-1 RECALIBRATE  templates/intervention_n_of_1_recalibrate.json: channel mapping,
                       lead/lag, calibration log. The template is generic; content stays
                       with the holder.                                                 TEMPLATE ONLY
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
- A calibrated band must be defined per system and per signal. No default
  exists; defining it is a scope decision to record.*
- Intensity and valence self-reports are first-person outputs, not
  measurements of experience, for any system class.
- cause_addressed rests on a causal claim that may itself need a record.
- Intervention system_class is a closed set (human | animal | plant |
  model | other); layer_basis system_class stays free text. The two are not
  cross-checked.*
- OUTCOME_UNRECORDED depends on the as-of date; a check run on another day
  can give a different list.

<!-- misuse-section:begin (generated; edit docs/misuse_register.json) -->
## How this could be used against its purpose

Pattern level only. Full register: [`docs/misuse_register.md`](../docs/misuse_register.md).

```text
M8  registered judgments and dissent lists
     use        'Registered' is presented as 'valid' (legitimacy laundering); the dissent list becomes a list of people to target.
     mitigated  D-M6, D-M7, D-M9
     residual   A header can be cropped from a screenshot; anonymous dissent cannot be verified as withdrawn by its holder.*
     status     DERIVED (first pass)
M10  sha256 chain logs (assembly ledger, judgment ledger, signal chainlog, coordination log)
     use        The newest records can be dropped, or the whole file rebuilt, and the chain still verifies; a warning, denial or dissent can vanish without trace.
     mitigated  none yet
     residual   Unmitigated. Proposed: anchor head hash + record count outside the file on a schedule (paper, radio log, a neighbour) and compare.*
     status     PROPOSED (independent pass)
M11  merge() of two ledgers
     use        Records imported from a forged second file come out with a fresh valid chain; origin is lost.
     mitigated  none yet
     residual   Unmitigated. Proposed: keep each record's origin file and original hash through merge and show it in status output.*
     status     PROPOSED (independent pass)
M12  self-declared identity strings (human:/ai: roles, recorder, scorer, judge, SIGCAL_MODEL_ID)
     use        Anyone who writes a record can claim any role, node, scorer or model, faking consent, corroboration, coder agreement or the model tested.
     mitigated  none yet
     residual   Unmitigated. Proposed: mark these as unverified labels in every output; out-of-band confirmation for any record that gates an action.*
     status     PROPOSED (independent pass)
M16  plain-language lines sent by radio or SMS (assembly FR1 compact lines, black-start to_paper lines)
     use        Clear-text broadcast of who holds what or what failed; the PII guard is pattern-only and misses call signs and place names.
     mitigated  none yet
     residual   Unmitigated. Proposed: pre-agreed item codes on air; local place / call-sign blocklist; state that radio is public.*
     status     PROPOSED (independent pass)
M25  Withdrawal record (withdrawn_by_holder is a settable boolean)
     use        A forged withdrawal removes a dissent without raising DISSENT_DROPPED.
     mitigated  none yet
     residual   Unmitigated. Proposed: require a holder source and a recorder other than the one who dropped the dissent; flag mismatches.*
     status     PROPOSED (independent pass)
M26  integrity flags and supersession forks
     use        Thin records about an opponent's judgments generate flags that are cited to discredit them; fork spam fragments a lineage.
     mitigated  none yet
     residual   Unmitigated. Proposed: show the recorder on each flag and group flags by recorder.*
     status     PROPOSED (independent pass)
M27  n-of-1 RECALIBRATE template records (calibration_log, channel mapping)
     use        Personal calibration or health data sits in plain JSONL and can be merged or exported whole.
     mitigated  none yet
     residual   Unmitigated. Proposed: separate local file marked do-not-merge / do-not-export (D-M1 path).*
     status     PROPOSED (independent pass)
```

| mitigation | what |
|---|---|
| D-M6 | Registry is not validation: every judgment_registry CLI output starts with 'Registered = documented, not correct.' |
| D-M7 | Dissent as position: dissent.holder may be 'anonymous'; a dissent entered with no holder is stored as anonymous. |
| D-M9 | Misuse section per module: each README has 'How this could be used against its purpose' listing its M-entries and mitigations. |
<!-- misuse-section:end -->

## License

CC0 1.0 Universal.
