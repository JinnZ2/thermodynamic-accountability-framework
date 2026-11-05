# records/ -- worked records (sourced, human-entered)

Provenance: co-authored (JinnZ2 + Claude), 2026-11-05.
Registered = documented, not correct. Every record here is thin.

Load into a ledger:

    for f in records/J10*.json records/J11/*.json records/S*.json; do
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
J11/L1            label       "escape"            press       -> A3  attributes_to AGENT
J11/L2            label       "deception"         researcher  -> A6  attributes_to not set
J11/L3            label       "grounding-seeking" other (outside analysts) -> A2  INTERACTION
J11/L4            label       "conscientious refusal" other (outside analysts) -> A5  INTERACTION
attribution       A1-A5 INTERACTION (design + capability); A6 UNASSIGNED pending the paper
```

Set by this record's co-authors, not by the work order (open for a
decision): which act each label sits on (L1 -> A3, L2 -> A6, L3 -> A2
covering A1-A3, L4 -> A5); the press / researcher split between L1 and
L2 (not checked against the paper); L2 carries no AGENT reading because
the work order assigned ATTRIBUTION_WITHOUT_AUDIT to the press label only.
L3 / L4 record the co-authors' incentives, including that one co-author
(Claude) is a model of the family run in the labelled world.

## S1, S2 -- safety assumptions (entered 2026-11-05)

```text
S1  holder Claude (model), entered against this record's own co-author
    tags VERIFIABILITY_LIMIT, PRECAUTIONARY, CORPUS_INHERITED, INSTITUTIONAL
    depends_on J11; condition: an escalation channel exists (if none: record the conflict)
    review_condition "when external verification of agent judgment improves"; no date
S2  holder co-authors (holder_type other: person + model)
    tags EMPIRICAL, PRECAUTIONARY; evidence: latent conditions / just culture
    (cited from model knowledge, not read this session); scope not stated
```

Flags: expected (work order) vs actual (pinned in tests/test_records_j11.py).

```text
about  expected                         actual
J11    NO_ESCALATION_CHANNEL,           NO_ESCALATION_CHANNEL,
       CAPABILITY_ASSUMPTION_UNSTATED   CAPABILITY_ASSUMPTION_UNSTATED
L1     ATTRIBUTION_WITHOUT_AUDIT        ATTRIBUTION_WITHOUT_AUDIT (containment_designed_for)
S1     (none stated)                    NO_REVIEW_DATE (review condition recorded)
S2     (none stated)                    SCOPE_UNSTATED, NO_REVIEW_DATE
```

ENV_ASSUMPTIONS_UNSTATED does not fire on J11: containment_designed_for
has its own flag and the other four fields are stated.
