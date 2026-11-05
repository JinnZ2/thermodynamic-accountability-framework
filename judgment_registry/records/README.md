# records/ -- worked records (sourced, human-entered)

Provenance: co-authored (JinnZ2 + Claude), 2026-11-05.
Registered = documented, not correct. Every record here is thin.

Load into a ledger:

    for f in records/J10*.json; do python3 cli.py add "$f" --ledger records.jsonl; done
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
