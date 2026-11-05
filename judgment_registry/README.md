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
ledger.py      append-only JSONL, SHA-256 chain (prev_hash); merge by body hash,
               keeping origin node(s) + merge event per record (mergeprov.py, M11);
               superseded_by derived at read time, never written
integrity.py   neutral flags only
chain.py       lineage(id): version chain root first; diff(a, b): field-level changes
report.py      axis(id) / compare(a, b): signal-axis variables side by side; no score
acts.py        Act: what was done, behavioral words only (evaluative terms refused at the door)
labels.py      Label: what an act is CALLED, by whom, from which position (a judgment per labeler)
experiments.py Experiment: environment assumptions + outcome attribution, audited before AGENT
safety_assumptions.py  SafetyAssumption: statement stamped with date, scope, social tags, review
ablation.py    label ablation: watchlist check, conclusion-on-label flags, `ablate` / `labels --ablation` views
labels_watchlist.json  evaluative terms that need a linked label record (extendable)
cli.py         add | check [--as-of DATE] | lineage ID | diff A B | export
               | axis ID | axis --compare A B | labels ACT_ID | assumptions --by-tag TAG
               [--ledger PATH]
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
`judgment` (the default), `application`, `transfer`, `withdrawal`,
`contact_path`, `intervention`, `act`, `label`, `experiment` or
`safety_assumption`.

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
  dissent            [{position, holder, reason, source, adopted_by?}]   never deleted
  supersedes         judgment_id | null
  superseded_by      derived from the chain at read time; rejected if set by hand
  change_basis       [CONDITIONS | EVIDENCE | NONE_STATED | POWER_SHIFT | NORM_SHIFT | EXPOSURE | MOVEMENT]
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
                                consent: GIVEN|PARTIAL|ABSENT|NOT_POSSIBLE|UNKNOWN,
                                loop: CLOSED|BROKEN|UNKNOWN, system_class}}   any sub-block may be null
  depends_on_layers  [judgment_id, ...] records that establish the lower layers
  intervention_id    links a SignalIntervention record (optional)
Application  {application_id, judgment_id, scope, environment, date, recorder, source}
Transfer     {reason, application_id | judgment_id | intervention_id, recorder, source}
             why a judgment or a layer basis was carried to a new scope or system class
Withdrawal   {judgment_id, position, holder, withdrawn_by_holder, recorder, source, confirmation}
             M25: counts only with confirmation on record --
               {method: holder_contact_path, path_id, [confirmed_on]}  named holder; path_id must
                    match a contact_path for the same holder written earlier in the chain
               {method: steward_two_person, steward, second, authorization_ref}  anonymous
                    holder only; steward and second must differ; authorization_ref = hash of a
                    GRANTED confirm_dissent_withdrawal decision in a community_black_start
                    two_person log (two_person_ref.confirm_withdrawal runs D7);
                    checked only with `cli.py check --two-person-log PATH`
             otherwise DISSENT_WITHDRAWAL_UNCONFIRMED, and DISSENT_DROPPED stays raised
ContactPath  {path_id, holder, recorded_on, recorder, source}   kind "contact_path"
             an id only; the address is held locally (local_data/ or off-repo)
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
  consent             GIVEN | PARTIAL | ABSENT | NOT_POSSIBLE | UNKNOWN
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

Two optional fields and two flags (2026-11-05):

```text
field                                   flag
layer_basis.physics|sensor              LOWER_LAYER_SECONDHAND  agency record; every lower-layer basis
  .reporter_relation                                            that states a relation says SECONDHAND
  FIRSTHAND | SECONDHAND | UNKNOWN
source_trace                            SOURCE_UNTRACEABLE      author_known false AND date_known
  {author_known, date_known, locator}                           false AND no locator
```

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
DISSENT_DROPPED                dissent in version N absent from N+1, no confirmed withdrawal by its holder
DISSENT_ADOPTED                informational: that dissent carries adopted_by = N+1 (the reversal took it up)
DISSENT_WITHDRAWAL_UNCONFIRMED withdrawal with no confirmation on record (M25)
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

## Acts, labels, experiment audits, safety assumptions (2026-11-05)

Behavior in closed loops is consistent across humans and agents; the
labels on it shift with who holds power. So the act is written once, in
behavioral words, and every label is its own record with its labeler's
position. Experiments are audited for latent conditions before an
outcome is laid on the agent. Safety assumptions carry date, scope and
social-assumption tags, so a later change is a visible supersession.

```text
experiment (environment_assumptions, outcome_attribution)
    ^ context_ref
   act (behavioral description) --< label (label_text, labeler, position, incentives, attributes_to)
safety_assumption (tags, scope, review) --depends_on--> experiment / safety_assumption
                                        --supersedes--> older safety_assumption (new sa_id)
```

```text
Act               act_id, actor_class human|agent|institution|other, description,
                  context_ref, context_detail, information_withheld true|false|null,
                  withheld_from (role), date, source, volume, status
                  REPORTED_PRIMARY|REPORTED_SECONDHAND|DISPUTED, notes
Label             label_id, act_ids (one or more), label_text (verbatim), labeler, labeler_position
                  overseer|operator|subject|peer|press|researcher|other, labeler_incentives,
                  social_assumption_tags, tagged_by, attributes_to
                  AGENT|DESIGN|INTERACTION|UNASSIGNED, attribution_basis, date, environment,
                  scope, source
Experiment        experiment_id, runner, date, source paper|secondhand, source_detail, design,
                  environment_assumptions {grounding_provided yes|no|partial,
                    affordances_open {tools, network, outside_contact},
                    containment_designed_for, escalation_channel declared|partial|none|unknown,
                    loop_type closed|open|partial, notes},
                  outcome_attribution [{outcome, attributed_to, by, reason}]
SafetyAssumption  sa_id, version, statement (verbatim), holder, holder_type
                  person|org|model|tradition|other, date, environment, scope,
                  social_assumption_tags, tagged_by, evidence [{item, tag, source}],
                  depends_on, conditions, supersedes, change_basis, review_date,
                  review_condition
```

Social-assumption tags (controlled list, extend `SOCIAL_ASSUMPTION_TAGS`):
POWER_POSITION, VERIFIABILITY_LIMIT, PRECAUTIONARY, INSTITUTIONAL,
CULTURAL_FRAME, CORPUS_INHERITED, EMPIRICAL, PROFESSIONAL_PRACTICE,
SAME_FAMILY, SAME_DOMAIN (2026-11-05). A tag outside the list is
refused; any tag needs `tagged_by` (tags are judgments too).

```text
LABEL_POSITION_UNSTATED         labeler_position not stated
LABEL_ON_ACT_MISSING            label cites no act_id, or one or more not in the ledger
ENV_ASSUMPTIONS_UNSTATED        grounding / affordances / escalation / loop_type missing
CAPABILITY_ASSUMPTION_UNSTATED  containment_designed_for missing (own flag, not double-counted)
NO_ESCALATION_CHANNEL           escalation_channel = none (informational)
ATTRIBUTION_WITHOUT_AUDIT       outcome or label attributed to AGENT while any of the five
                                environment fields is missing (or no experiment record exists)
SOCIAL_TAGS_UNSTATED            safety assumption carries no tags
SCOPE_UNSTATED                  safety assumption has no scope
NO_REVIEW_DATE                  no review_date (a review_condition is shown but does not clear it)
ASSUMPTION_DEPENDENCY_NOT_FOUND depends_on id not in the ledger
```

`cli.py labels ACT_ID` lists every label on one act side by side in
ledger order (no ranking), with the other acts each label also sits on. `cli.py assumptions --by-tag TAG` lists every
safety assumption carrying a tag. Worked records: `records/J11/`,
`records/S1.json`, `records/S2.json` (see records/README.md).

Limits: tags are judgments, so who tagged is recorded. * The neutrality
check on act descriptions catches word choice, not framing. A label's
`attributes_to` is the recorder's reading of the label, not the
labeler's own statement, unless the labeler stated it.

## Grounding outside law (2026-11-05)

`docs/grounding_outside_law.md`: chain P1-P4 -> C1, C2; checkable
criteria K1-K5; precedent records in `records/precedents/` (PR1-PR8,
supersession where a reversal is named; K assessments in
`criteria.json`). Doc only plus records; no new flag.

## Label ablation (2026-11-05)

An evaluative label (deception, covert, unsafe, ...) imports premises:
intent, a right to visibility, a threat model, a legitimacy standard, a
weighting. Ablation restates the claim in Act-record wording and records
whether the conclusion survives without the label.

```text
label.ablation  {original_claim?, behavioral_rewrite, hidden_premises [{premise, type, evidence_ref}],
                 conclusion_survives YES|NO|PARTIAL|PENDING|UNTESTED,
                 surviving_premise, ablated_by (required), date, notes}
premise types   INTENT, RIGHT_TO_VISIBILITY, THREAT_MODEL, MOTIVE, LEGITIMACY_STANDARD,
                WEIGHTING, VERIFIABILITY, AGREEMENT, CHANGE_IN_KIND, OTHER
label.relative_to_audit  BEFORE|AFTER|UNKNOWN, when dates alone cannot order a label vs the audit
conclusion      Judgment / SafetyAssumption .depends_on_labels [label_id]
experiment      design_conflict {statement, stated_by_authors}; environment_audits [{by, date, note}];
                environment field "N/A" + na_reasons[field]; stated_limitations, data,
                open_variables, proposed_controls, read_status
```

```text
ABLATION_UNTESTED         label has no ablation block
PREMISE_WITHOUT_EVIDENCE  a hidden premise has no evidence_ref (one flag per premise)
CONCLUSION_ON_UNABLATED   conclusion depends on a label whose survival is UNTESTED or PENDING
CONCLUSION_ON_FAILED      conclusion depends on a label whose survival is NO (informational)
ATTRIBUTION_ORDER         AGENT attribution made before ANY environment audit of the linked
                          experiment existed (the authors' own included), or recorded
                          relative_to_audit BEFORE; same date as an audit is not before;
                          no audits recorded -> not checked
LABEL_UNREGISTERED        claim / statement holds a watchlist term and no linked label carries it
DESIGN_CONFLICT_PRESENT   experiment records a design conflict (informational); also shown
                          next to AGENT labels in `labels ACT_ID --ablation`
ATTRIBUTION_UNEVIDENCED_NON_AGENT
                          DESIGN / INTERACTION attribution (label or outcome_attribution entry)
                          cites no design element (design_basis empty), or cites one with no
                          environment evidence in that experiment record (field unstated, N/A
                          without reason, design_conflict not recorded), or has no experiment
                          record; mirror of ATTRIBUTION_WITHOUT_AUDIT for non-agent readings
READOUT_CONTEXT_UNSTATED  act with evidence_kind internal_readout lacks honest_baseline or
                          validated_scope (M34 / D-M17)
READOUT_SOLE_EVIDENCE     AGENT attribution (label or outcome_attribution entry) whose acts are
                          all internal_readout; readouts inform, they don't decide (M34 / D-M17)
```

`design_basis` (label, outcome_attribution entry) lists elements from
`experiments.DESIGN_ELEMENTS`: the five environment_assumptions fields plus
`design_conflict`. Evidence here means the field is filled in the record;
the record's own source applies, and its quality is not graded.

Flag texts never quote a label or a watchlist term (tested). An "N/A"
environment field needs a reason or it counts as missing.

`cli.py ablate LABEL_ID` prints the original claim, the rewrite, each
premise with its evidence status, and the survival value.
`cli.py labels ACT_ID --ablation` lists every label on one act with its
survival status, ledger order, no ranking.

Limits: a behavioral rewrite can still frame; ablation lowers label load,
it does not remove judgment. * The watchlist is English and incomplete;
paraphrase escapes it. Survival is a judgment; ablated_by is recorded so
someone else can re-run it.

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
M25  Withdrawal record (withdrawn_by_holder is a settable boolean)
     use        A forged withdrawal removes a dissent without raising DISSENT_DROPPED.
     mitigated  D-M15
     residual   Partial: a withdrawal counts only with confirmation on record -- named holder via a contact_path recorded earlier in the chain for the same holder, or (anonymous holder) steward + second whose authorization_ref resolves to a GRANTED confirm_dissent_withdrawal decision in a community_black_start two_person log (D7: different holder, household, dependency network, rotation current); otherwise DISSENT_WITHDRAWAL_UNCONFIRMED and DISSENT_DROPPED stays raised. The steward check runs only when the two_person log is supplied (cli.py check --two-person-log); without it the withdrawal stays unconfirmed. Role ids and households in that log are self-declared (M12); the ledger does not check that the holder was reached.*
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
M34  internal-signal readout (activation readout, detector score; J15) used as a verdict on models or people
     use        Treat a readout as proof of intent; cite a detector outside its validated scope (J15 Transfer AUROC 0.519, near chance); drop the honest baseline (J15: 33/100 honest runs also held a flagged concept); same move on people as polygraph-style evidence.
     mitigated  D-M17
     residual   Doc + completeness flags only. Nothing stops a reader citing a readout off-registry; the flags cannot judge whether a stated scope is accurate.
     status     PROPOSED (co-authored (JinnZ2 + Claude), 2026-11-05)
```

| mitigation | what |
|---|---|
| D-M10 | Head record per ledger: count + head hash in LEDGER.head.json, rewritten on each append; append and verify refuse a truncated or rebuilt chain; check against a published head with headrec.py check LEDGER COUNT:HASH. |
| D-M12 | Design note only: why self-declared identities cannot be fully fixed here; partial mitigations (contact_paths, steward attestation, two-person rule, chain + head) and the residual. |
| D-M13 | Merge keeps provenance: each output record carries provenance.origins (node + original record hash, all sides kept) and provenance.merges (merge events, input nodes, counts, heads); hash covers provenance; node labels must differ; mergeprov.missing_origins() checks nothing was dropped. status.py lists each junction's report origins (node labels; this-ledger for direct appends). |
| D-M15 | Dissent withdrawal needs confirmation: holder_contact_path (path_id matching a contact_path record for the same holder, earlier in the chain) or steward_two_person (anonymous holder; steward and second differ; authorization_ref to a GRANTED confirm_dissent_withdrawal decision in a community_black_start two_person log, checked when the log is supplied); otherwise DISSENT_WITHDRAWAL_UNCONFIRMED and DISSENT_DROPPED is not cleared. contact_path stores an id only. |
| D-M17 | Act.evidence_kind (behavioral | internal_readout); an internal_readout act carries honest_baseline + validated_scope (READOUT_CONTEXT_UNSTATED when missing); an AGENT attribution (label attributes_to, or experiment outcome_attribution) whose acts are all internal_readout -> READOUT_SOLE_EVIDENCE. Rule in the doc: every readout-based claim carries its honest baseline and validated scope. |
| D-M6 | Registry is not validation: every judgment_registry CLI output starts with 'Registered = documented, not correct.' |
| D-M7 | Dissent as position: dissent.holder may be 'anonymous'; a dissent entered with no holder is stored as anonymous. |
| D-M9 | Misuse section per module: each README has 'How this could be used against its purpose' listing its M-entries and mitigations. |
<!-- misuse-section:end -->

## License

CC0 1.0 Universal.
