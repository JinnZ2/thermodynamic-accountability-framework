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
schema.py      Judgment / Application / Transfer / Withdrawal; shape check at the door
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
Application  {application_id, judgment_id, scope, environment, date, recorder, source}
Transfer     {application_id, reason, recorder, source}   why it was carried to a new scope
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
```

The last two are additions to the specified list: both are integrity
gaps the chain itself can show. UNCHAINED_CHANGE keys on the same judge,
because two judges on one scope coexist and are not a replacement. That
reading is ours.*

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

## License

CC0 1.0 Universal.
