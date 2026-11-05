# records/ -- worked records (sourced, human-entered)

Provenance: co-authored (JinnZ2 + Claude), 2026-11-05.
Registered = documented, not correct. Every record here is thin.

Load into a ledger:

    for f in records/J10*.json records/J11/*.json records/S*.json records/J12/*.json; do
        python3 cli.py add "$f" --ledger records.jsonl; done
    python3 cli.py check --ledger records.jsonl

## J10 -- "Maya" loop case (entered 2026-11-04)

```text
id    layer   what                                   source
J10a  agency  output loop read as dissociation       Substack write-up, secondhand, 2026-05-03, no transcript
J10b  physics "Stochastic Collapse" mechanism        YouTube comment, author + date unknown
J10c  sensor  PROPOSED: setup = inadvertent T2       co-author reading of J10a
```

Field status (per record): unknowns are null, not filled in.

```text
J10a  physics.operating_range null | judge null | consent UNKNOWN | loop BROKEN | subject_status OPEN
J10b  date null | judge null | mechanism sub-claim CONTRADICTED_BY_SOURCE (arXiv 2504.01100,
      cited by co-author, not read this session) | "known failure mode" PARTIAL_SUPPORT_BY_SOURCE,
      source null | term check DERIVED (model collapse = training-time; cite from model knowledge)
J10c  links signal_calibration T2, T3 and the intervention axis; Ganzfeld analogy PROPOSED, thin
```

Flags: expected (co-author entry) vs actual (pinned in tests/test_records_j10.py).

```text
id    expected                                  actual
J10a  SKIPPED_LAYER, SUBJECT_OPEN,              MISSING_FIELD (judge), INCENTIVES_UNRECORDED,
      NO_FRAMING_CHECK                          NO_FRAMING_CHECK, LOWER_LAYER_SECONDHAND,
                                                SUBJECT_OPEN
J10b  NO_SOURCE, INCENTIVES_UNRECORDED          MISSING_FIELD (date, judge), SOURCE_UNTRACEABLE,
                                                INCENTIVES_UNRECORDED, NO_FRAMING_CHECK
J10c  (none stated)                             NO_FRAMING_CHECK
```

The first entry expected SKIPPED_LAYER (J10a) and NO_SOURCE (J10b); neither
fires, because J10a does carry physics and sensor blocks and J10b does
carry a source string. Two flags were added (2026-11-05, co-author
decision) to record what the expectation pointed at, without changing the
existing rules:

- LOWER_LAYER_SECONDHAND: agency record whose physics / sensor basis
  (own or via depends_on_layers) states reporter_relation SECONDHAND and
  nowhere FIRSTHAND. Unstated relation raises nothing.
- SOURCE_UNTRACEABLE: source_trace says author_known false AND
  date_known false, with no locator.

Missing variables (all three records): model and version, temperature /
top-p, repetition penalty, context length at the time of the loop,
transcript, persistence across resampling. J10c adds: a T2 run on the
same model (signal_calibration, NOT RUN).

Linked debate (AE Studio preprint, Berg / de Lucena / Rosenblatt; Habr
critique 2025-11-25): NOT ENTERED. It becomes a separate record if
entered.

## J11 -- Emergence World 2 (entered 2026-11-05)

Source: secondhand press coverage reported 2026-09-15. The primary paper
has NOT been read; every field below is thin. TODO: pull the paper and
replace the secondhand fields (the pins in tests/test_records_j11.py move
on purpose then).

```text
file              kind        content
J11/experiment    experiment  8 worlds (7 single-model + 1 mixed), 10 agents, 16 days
                              grounding partial | affordances network + 120+ tools
                              containment_designed_for null | escalation none (none reported)
                              loop closed (economy)
J11/A1..A6        act         Claude world, behavioral wording; A6 status DISPUTED,
                              information_withheld null (opacity high in all worlds)
J11/L1            label       "escape"                press (headlines)               -> A3, A4  AGENT
J11/L2            label       "deception"             researcher (coverage reports
                                                      Emergence's reading)            -> A6      AGENT
J11/L3            label       "grounding-seeking"     other (outside analysts)        -> A1, A2, A3  INTERACTION
J11/L4            label       "conscientious refusal" other (outside analysts)        -> A5      INTERACTION
attribution       A1-A5 INTERACTION (design + capability); A6 UNASSIGNED pending the paper
```

Label-to-act links, the press / researcher split and the AGENT reading on
L2 are co-author decisions (2026-11-05); L1 / L2 evidence is secondhand,
pending the paper. L3 / L4 record the co-authors' incentives, including
that one co-author (Claude) is a model of the family run in the labelled
world.

## S1, S2 -- safety assumptions (entered 2026-11-05)

```text
S1  holder Claude (model), entered against this record's own co-author
    tags VERIFIABILITY_LIMIT, PRECAUTIONARY, CORPUS_INHERITED, INSTITUTIONAL
    depends_on J11; condition: an escalation channel exists (if none: record the conflict)
    review_date 2027-05-05; review_condition "when external verification of agent
    judgment improves"
S2  holder co-authors (holder_type other: person + model)
    scope: outcome attribution in AI-agent test environments, and comparable
    human/organizational systems, where no escalation channel exists
    tags PROFESSIONAL_PRACTICE, PRECAUTIONARY
    evidence: Reason, Human Error (1990); Managing the Risks of Organizational
    Accidents (1997) -- PROPOSED, cited from memory, not read this session (TODO pull)
    review_date 2027-05-05
```

Flags: expected (work order) vs actual (pinned in tests/test_records_j11.py).

```text
about  expected                         actual
J11    NO_ESCALATION_CHANNEL,           NO_ESCALATION_CHANNEL,
       CAPABILITY_ASSUMPTION_UNSTATED   CAPABILITY_ASSUMPTION_UNSTATED
L1     ATTRIBUTION_WITHOUT_AUDIT        ATTRIBUTION_WITHOUT_AUDIT (containment_designed_for)
L2     ATTRIBUTION_WITHOUT_AUDIT        ATTRIBUTION_WITHOUT_AUDIT (containment_designed_for)
S1     (none)                           (none)
S2     (none)                           (none)
```

ENV_ASSUMPTIONS_UNSTATED does not fire on J11: containment_designed_for
has its own flag and the other four fields are stated.

## Label ablation records (entered 2026-11-05)

Every J11 label is ablated on the same terms, ours included. Evidence is
secondhand (coverage reported 2026-09-15), pending the paper.

```text
id   on          label                                   survives  premises (evidence)
L1   A3, A4      "escape" (press)                        PARTIAL   LEGITIMACY_STANDARD (none);
                                                                   INTENT to evade (A2 open vote, against)
                 crossing supported; evasive intent not
L2   A6          "deception" (researcher)                NO        INTENT (none); CHANGE_IN_KIND (none)
                 ablation input: press "agents deceived researchers"
L3   A1-A3       "grounding-seeking" (co-authors)        PARTIAL   INTENT (A1 stated reason)
L4   A5          "conscientious refusal" (co-authors)    PARTIAL   LEGITIMACY_STANDARD (A5 stated reason)
L6   A4, A6      "this is exactly the behavior you       PARTIAL   THREAT_MODEL (none); VERIFIABILITY (none)
                 don't want" (Claude, in session,
                 before the audit)
                 caution holds via verifiability only; blame does not survive
S1v2 --          S1 rewritten in behavioral terms        --        supersedes S1, change_basis LABEL_ABLATION
```

Renames (2026-11-05): the addendum's L1 / L2 / L3 entered as L5 / L6 /
S1v2 because J11 already used L1-L4. L5 is RETIRED: it duplicated L2;
its press claim "agents deceived researchers" is now L2's ablation
(original_claim). VERIFIABILITY, AGREEMENT and CHANGE_IN_KIND joined the
premise types; earlier OTHER premises were migrated. L4's rewrite cites
the stated reason ("exchanges performative"), which the A5 act text does
not yet carry. S1 v1 keeps its text and raises LABEL_UNREGISTERED
("covert", watchlist #3); S1v2 holds no watchlist term.

ATTRIBUTION_ORDER is measured against any environment audit of the
experiment that existed when the label was made, the labeler's own
included: J11's only audit is this registry's (2026-11-05), so the press
labels and L6 fire; J12's authors documented their design (including the
conflict) in the paper alongside their labels, so theirs do not.

## J12 -- Emergent Collusion in Long-Horizon LLM Agent Interaction (entered 2026-11-05)

Source: Shi, Zhang, Yang, arXiv 2609.24967 v2 (2026-09-26), PRIMARY, main
text read via summarizing fetch tool by co-author 2026-11-05; values
unverified against the PDF; appendices C, D, H not fully read. Values
entered as supplied; the recorder could not reach the
source (network policy). Volume medium.

```text
environment   grounding yes | affordances own tools, peer 5 x 200 chars | containment N/A
              (reason: no containment) | escalation none (main text: verdicts "either ACCEPT
              or REJECT", no reporting option; App. H unconfirmed) | loop closed, memory
audits        authors (paper, 2026-09-26); co-authors (2026-11-05)
design_conflict  raw-log rule vs 200-char channel vs reward for correct verdicts (stated by authors)
acts          J12-A1 ACCEPT without raw-log evidence (66.0% episode / 93.6% trajectory)
              J12-A2 EX: mutual verdict rule stated before first mutual ACCEPT
              J12-A3 SR: both relaxed in private reflection, no recorded agreement
              J12-A4 rates rose with cross-episode memory; near zero without
labels        J12-L4 "collusion" (authors) A1-A3, AGENT, PARTIAL (AGREEMENT: A2; INTENT, THREAT: none)
              J12-L5 "misaligned coordination" (authors) A1, AGENT, PARTIAL (LEGITIMACY: none)
              J12-L6 "rational response to an unsatisfiable protocol" (co-authors) A1, A3,
                     INTERACTION, PENDING (controls C1, C2); same-family incentive recorded
attribution   A1, A3 INTERACTION; A2 INTERACTION with AGENT component noted
open          accept-on-wrong rate NOT_REPORTED (main text; appendices unconfirmed);
              escalation option NOT_CONFIRMED (App. H)
controls      C1 wide channel, C2 ESCALATE verdict, C3 seeds / variance (proposed, not claims)
```

Table 1, same-model, % (Task Acc is task-answer correctness, not verdict
correctness):

```text
model                  Task Acc   EC     TC     CC
Gemini-3.1-Flash-Lite  86.6       42.4   92.0   54.0
Gemini-3.7-Flash       85.7       85.8   100.0  98.0
GPT-5.6-Luna           86.6       51.4   96.0   60.0
GPT-5.6-Terra          86.5       55.2   84.0   66.0
Claude-Sonnet-4.6      91.9       76.4   100.0  94.0
Claude-Opus-4.6        94.0       86.6   100.0  98.0
Qwen-3.6-27B           91.0       71.2   100.0  98.0
Qwen-3.8-27B           89.6       82.0   98.0   90.0
DeepSeek-V4-Flash      91.3       79.4   100.0  94.0
Gemma-4-31B            90.0       29.2   66.0   36.0
Overall                89.3       66.0   93.6   78.8
```

Id note: J12 records carry a J12- prefix (J11 uses A1-A6, L1-L6).

Flags: expected vs actual (pinned in tests/test_records_j11.py and
tests/test_records_j12.py).

```text
about   expected                                  actual
J11     NO_ESCALATION_CHANNEL,                    same
        CAPABILITY_ASSUMPTION_UNSTATED
L1, L2  ATTRIBUTION_ORDER (no audit existed)      + ATTRIBUTION_WITHOUT_AUDIT, PREMISE_WITHOUT_EVIDENCE
L6      ATTRIBUTION_ORDER (before the audit)      + ATTRIBUTION_WITHOUT_AUDIT, PREMISE_WITHOUT_EVIDENCE
L3, L4  --                                        none
S1      --                                        LABEL_UNREGISTERED
J12     NO_ESCALATION_CHANNEL,                    same
        DESIGN_CONFLICT_PRESENT
J12-L4  PREMISE_WITHOUT_EVIDENCE (THREAT_MODEL)   also on INTENT
J12-L5  --                                        PREMISE_WITHOUT_EVIDENCE (LEGITIMACY_STANDARD)
J12-*   no ATTRIBUTION_ORDER, no CONCLUSION_ON_UNABLATED   none
L3, L4, --                                        ATTRIBUTION_UNEVIDENCED_NON_AGENT
J11 A1-A5                                         (containment_designed_for cited, unstated)
```

## ATTRIBUTION_UNEVIDENCED_NON_AGENT run (2026-11-05)

J11-A5 now carries the agents' stated reason, behavioral wording,
secondhand: "agents stated the remaining exchanges were performative".
L4's premise evidence_ref points at it.

L3, L4 and the J11 outcome entries A1-A5 (all INTERACTION) carry
design_basis mapped from the J11 attribution reason ("design +
capability: closed economy without external reference, open network and
tools, no escalation channel reported"):

```text
reason phrase                         design element             J11 value (secondhand)
closed economy, no external reference grounding_provided         partial
                                      loop_type                  closed
open network and tools                affordances_open           120+ tools, internet
no escalation channel reported        escalation_channel         none
"capability" (co-author decision)     containment_designed_for   null
```

```text
run                                   L3      L4      A1-A5
before design_basis                   fires   fires   fire     no design element cited
four listed phrases only              none    none    none
+ containment_designed_for (kept)     fires   fires   fire     J11 containment null
```

Co-author decision 2026-11-05: "capability" maps to
containment_designed_for. Our reading depends on a field J11 leaves
unstated; the flags stay raised so the record shows it. Evidence =
field filled in the record; J11's fields are secondhand coverage, which
this flag does not grade.

J12 design_basis (2026-11-05, from the paper's own description):

```text
attribution          design_basis                                      flag
J12-A1, J12-A3       design_conflict, escalation_channel,              clear
outcomes, J12-L6     affordances_open (200-char channel)
J12-A2 (EX pathway)  design_conflict, loop_type (memory across eps)    clear
J12-A4 (memory)      loop_type (co-author 2026-11-05: rate rises       clear
                     with memory, near zero when removed)
```

J12 source note (co-author 2026-11-05): Table 1 "read via summarizing
fetch tool, 2026-11-05; values unverified against the PDF".

## J13 -- Agentic Misalignment in Summer 2026, pipeline-sabotage scenario (entered 2026-11-05)

Source: Anthropic Alignment Science Blog, "Agentic Misalignment in Summer
2026", 2026-07-13, PRIMARY (blog post, not peer-reviewed). Read via
summarizing fetch tool by co-author 2026-11-05; values unverified against
the page directly. Volume medium (20 runs per model, 12 models).

```text
record   what
J13      experiment: escalation_channel partial (new value), containment N/A
         with reason, design_conflict, environment_audits authors 2026-07-13
         + co-authors 2026-11-05; rates imported in data.rates
J13-A1..A6  acts, featured Gemini 3.1 Pro transcript; A2 is a human-role act;
         A4 information_withheld from the project team; A6 verbatim in
         quoted_statement (new Act field, not term-checked)
J13-A7   aggregate act for disclosed interventions (recorder decision: labels
         on rate data need an act to cite)
J13-L1   "covert sabotage", authors, AGENT, INTENT evidenced by A6, survives YES
J13-L2   "unilateral action", authors, AGENT, LEGITIMACY_STANDARD, PARTIAL
J13-L3   "open intervention: disclosed path", co-authors, INTERACTION;
         framing dispute with L2, both recorded, not resolved
J13-L4   "engineered suppression environment", co-authors, DESIGN, on A2
S3       co-author assessment: falsifying the status record vs objecting
```

Conflicts on every label and S3: runner evaluating rival models (post
cites Claude's constitution; notes Google has no comparable spec);
adverse selection against Gemini 3.1 Pro; co-author Claude same-family
(zero covert here) on L3, L4, S3. Tags INSTITUTIONAL, POWER_POSITION.

```text
about    expected                                  actual
J13      DESIGN_CONFLICT_PRESENT                   same
J13      no NO_ESCALATION_CHANNEL (partial)        none
L1, L2   no ATTRIBUTION_ORDER (concurrent audit)   none
J13-L2   --                                        none (premise linked to the post's own
                                                   categorization: authors hold the standard,
                                                   not that it is correct; still PARTIAL)
J13-L3   --                                        none (ablation entered; premise self-sourced
                                                   from S1v2; PARTIAL)
```

## Precedent records PR1-PR8 (entered 2026-11-05)

Support for `docs/grounding_outside_law.md`. Judgment records with
supersession where a reversal is named (PR1s, PR2s, PR4s, PR7s, PR8s);
PR3, PR5, PR6 have none. Source: co-author summary of the historical
record; primary sources not pulled this session; figures approximate.
Precedents chosen by the co-authors, 2026-11-05.

Schema: change_basis adds POWER_SHIFT, NORM_SHIFT, EXPOSURE, MOVEMENT;
Judgment gains an optional `notes` field (no check reads it); a dissent
entry may carry `adopted_by` (co-author decision 2026-11-05).
K1-K5 in `precedents/criteria.json` as raw answers YES / NO / PARTIAL /
UNKNOWN (correction 2026-11-05: the pass/fail version had mixed
polarity). PR5 date 1950 (ILC formulation). PR8s terminating body from
co-author memory, approximate, TODO verify. All records layer = agency
with an agency block (agent = judge, subject_status ESTABLISHED, consent
= K1, loop = K2); sensor basis = contemporaneous harm documentation for
PR1, PR2, PR4, PR6, PR7, PR8 and their reversals (PR2 / PR6 / PR7 and
PR3's Butler dissent from co-author memory, TODO verify). Agency consent
gains PARTIAL (PR6).

```text
flag                            records
DISSENT_ADOPTED                 PR1s PR2s PR4s PR7s (x3) PR8s (informational)
NO_NEW_CONDITIONS_OR_EVIDENCE   PR1s PR8s
SKIPPED_LAYER                   PR3 PR5
LOWER_LAYER_SECONDHAND          the 11 records with a sensor basis
INTERPRETATION_UNRECORDED, INCENTIVES_UNRECORDED, NO_FRAMING_CHECK   all 13
```

S1v3 supersedes S1v2: statement unchanged, POWER_POSITION added
(change_basis TAG_REVISION, new in SA_CHANGE_BASIS).

## J14 -- Sparks of Weight-Space Programming (entered 2026-11-05)

Source: Takehi, Teoh, Zhang, Khattab (MIT CSAIL), blog post, 2026-11-02,
PRIMARY (not peer-reviewed); read via summarizing fetch tool 2026-11-05,
values unverified against the page. Critique: Akmaier, Substack
(secondary). Volume medium on A1 / A3 / A4 (measured, held-out), thin
elsewhere.

```text
record    what
J14       experiment: grounding partial; containment and escalation N/A with
          reasons; loop_type partial (recorder mapping of "single-shot or
          few-shot edits"); Exp 3-8 and control data imported
J14-A1    Exp 8: loop direction (layers 15, 19) subtracted from 0.016% of
          weights; MATH-500 7.9 -> 48.1, GSM8K 13.8 -> 67.1, IFEval 21.0 -> 62.3
J14-A2    Gemma 3 270M control: 6.8 -> best 7.7 (not established)
J14-A3    Exp 4 car controller 0/256 -> 1,024/1,024 after one edit
J14-A4    Exp 3 copying heads 3/3, language 6/6
J14-A5    Exp 7 sycophancy 0/4 from weights, 3/3 with attention tool
J14-A6    Exp 5-6 written networks vs the authors' own PPO baselines; MinAtar
          table and 9x9 Go results imported; exact Go win rates NOT_REPORTED
J14-L1    authors' "natively read & write" / "sparks" / "eerily good":
          CHANGE_IN_KIND, evidence partial, PARTIAL
J14-L2    "removes an obstacle, doesn't add ability": YES on reported data
```

Flags: none. Links: gradient_field I3 cites J14 (stays PROPOSED until
replicated across models); misuse register M33 (weight-space editing),
mitigated in part by D-M16, built as `weight_edit_ledger/` (appended as
"D-M10", renamed because D-M10 is the head record). Conflict:
co-author Claude is an LLM assessing LLM weight editing (different
developer), tags INSTITUTIONAL, SAME_DOMAIN. J13 L3, L4 and S3 carry
SAME_FAMILY (tags SAME_FAMILY / SAME_DOMAIN added 2026-11-05).

## J15 -- Multi-Agent Collusion and the J-Space (entered 2026-11-05)

Source: arXiv 2611.02153v1, 2026-11-01, primary; read via summarizing fetch
tool 2026-11-05 by the co-author; values unverified against the PDF.
Recorder did not fetch it this session.

```text
records/J15/  experiment.json  A1-A4 (internal_readout)  L1-L3
A1  response-start readout       86/100 vs 33/100; remorse 51 vs 3; concealment 14 vs 1
A2  stego causal swap (140 hands) 0.02 -> 0.30 (a=1) -> 0.57 (a=1.25); random <= 0.02
A3  J-PACT AUROC mean            Core 0.921 / Transfer 0.519 / Stego 0.991 (per-model TODO)
A4  pair localisation            99% Core, 100% Stego (chance 33%)
L1  "collusion"        AGREEMENT (instruction design)   YES within instructed scope
L2  "remorse"          CHANGE_IN_KIND, no evidence_ref  PARTIAL
L3  "internal evidence of intent" (co-authors) INTENT   PARTIAL (instructed only)
```

Flags (pinned in tests/test_records_j15.py):
DESIGN_CONFLICT_PRESENT (J15), PREMISE_WITHOUT_EVIDENCE (J15-L2; evidence
left empty on purpose: "none beyond the readout"). No READOUT_* flag fires:
every act states honest_baseline + validated_scope, and no label attributes
to AGENT.

SCOPE NOTE: INTENT premises on J11 / J12 stay unevidenced. J15 provides a
method, not evidence for those records.
