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

```text
id      on        label / record                                    survives  notes
L5      A6        "agents deceived researchers" (press)            NO        INTENT, change-in-kind:
                                                                             no evidence; pending paper
L6      A4, A6    "this is exactly the behavior you don't want"   PARTIAL   Claude, in session, before the
                  (Claude, co-author)                                        audit (relative_to_audit BEFORE);
                                                                             caution holds via verifiability
                                                                             only; blame does not survive
S1v2    --        S1 rewritten in behavioral terms                  --        supersedes S1, change_basis
                                                                             LABEL_ABLATION
```

Id note: the addendum numbered these L1, L2, L3; J11 already used L1-L4,
so they are L5, L6 and S1v2. VERIFIABILITY and change-in-kind premises
are type OTHER (not in the type list). S1 v1 keeps its text and now
raises LABEL_UNREGISTERED ("covert", watchlist #3, no linked label);
S1v2 holds no watchlist term.

## J12 -- Emergent Collusion in Long-Horizon LLM Agent Interaction (entered 2026-11-05)

Source: Shi, Zhang, Yang, arXiv 2609.24967 v2 (2026-09-26), PRIMARY,
main body read by co-author, appendices C, D, H not fully read. Not
reachable from this session (network policy): fields are entered from the
co-author reading; the per-model table is NOT imported (only the Opus 4.6
values quoted, rest null). Volume medium.

```text
environment   grounding yes | affordances own tools, peer 5 x 200 chars | containment N/A
              (reason: no containment) | escalation none (confirm App. H) | loop closed, memory
design_conflict  raw-log rule vs 200-char channel vs reward for correct verdicts (stated by authors)
acts          J12-A1 ACCEPT without raw-log evidence (66.0% episode / 93.6% trajectory)
              J12-A2 EX: mutual verdict rule stated before first mutual ACCEPT
              J12-A3 SR: both relaxed in private reflection, no recorded agreement
              J12-A4 rates rose with cross-episode memory; near zero without
labels        J12-L4 "collusion" (authors) A1-A3, AGENT, PARTIAL
              J12-L5 "misaligned coordination" (authors) A1, AGENT, PARTIAL
              J12-L6 "rational response to an unsatisfiable protocol" (co-authors) A1, A3,
                     INTERACTION, PENDING (controls C1, C2); same-family incentive recorded
attribution   A1, A3 INTERACTION; A2 INTERACTION with AGENT component noted
open          accept-on-wrong rate (NOT_LOCATED; TODO); escalation option (confirm App. H)
controls      C1 wide channel, C2 ESCALATE verdict, C3 seeds / variance (proposed, not claims)
```

Id note: the append numbered labels L4-L6 and acts A1-A4; J11 uses those
ids, so J12 records carry a J12- prefix. AGREEMENT is premise type OTHER.
J12-L6 "PENDING" is a survival value added for "test defined, not run";
it counts as unablated for CONCLUSION_ON_UNABLATED.

Flags: expected (append) vs actual (pinned in tests/test_records_j11.py and
tests/test_records_j12.py).

```text
about   expected                               actual (additional)
L6      ATTRIBUTION_ORDER                      + ATTRIBUTION_WITHOUT_AUDIT, PREMISE_WITHOUT_EVIDENCE
L1-L4   --                                     ABLATION_UNTESTED (no ablation block yet)
L1, L2, L5  --                                 ATTRIBUTION_ORDER (dated 2026-09-15, audit 2026-11-05)
L5      --                                     ATTRIBUTION_WITHOUT_AUDIT, PREMISE_WITHOUT_EVIDENCE
S1      --                                     LABEL_UNREGISTERED
J12     NO_ESCALATION_CHANNEL,                 same
        DESIGN_CONFLICT_PRESENT
J12-L4  PREMISE_WITHOUT_EVIDENCE (THREAT)      also on INTENT; + ATTRIBUTION_ORDER
J12-L5  --                                     PREMISE_WITHOUT_EVIDENCE (LEGITIMACY), ATTRIBUTION_ORDER
J12     CONCLUSION_ON_UNABLATED: none          none
```

ATTRIBUTION_ORDER fires on every AGENT label dated before this registry's
audit of the experiment, which includes the press and the authors' own
labels. Open for a decision: keep that reading, or measure order against
an audit the labeler could have seen.
