# Misuse register

Generated from `misuse_register.json` by `misuse_guard/render_register.py`; edit the JSON.

Defensive. Surfaces and mitigations at the pattern level only; no operational attack detail.

Most surfaces are the same data that makes coordination work, so they cannot be removed. Defense = where data lives, who sees it, what form it leaves in. Publish method, keep data local.

Provenance: co-authored (JinnZ2 + Claude); M1-M9 first pass; M10+ independent pass.

Status: DERIVED = first pass, read from the design; PROPOSED = independent pass, not yet reviewed.
Trailing asterisks mark thin volume.

## Entries

### M1  community_black_start  (DERIVED, first pass)

```text
surface          skills registry (knowledge holders, L2 items, role seeds)
adversarial use  A holder list becomes a list of people to coerce, poach or remove.
mitigations      D-M1, D-M3, D-M9
residual         Coarse region + skill can still narrow to one person in a small place.*
volume           thin
```

### M2  community_black_start  (DERIVED, first pass)

```text
surface          deployability data (household buffer vs restoration duration)
adversarial use  Read as a map of which households cannot hold on their own.
mitigations      D-M1, D-M2, D-M9
residual         Counts can leak in small communities (E17).**
volume           thin
```

### M3  community_black_start  (DERIVED, first pass)

```text
surface          latent assets (dormant generation, sync gear, fuel stocks)
adversarial use  A list of where restorable infrastructure sits becomes a target list.
mitigations      D-M1, D-M2, D-M9
residual         Public records already list some assets; the repo adds the dependency view.*
volume           thin
```

### M4  community_black_start  (DERIVED, first pass)

```text
surface          holdings and gaps per community (links R6)
adversarial use  Holdings and gaps together read as a raid or leverage map.
mitigations      D-M1, D-M2, D-M5, D-M9
residual         Need/surplus booleans still say what a community lacks.*
volume           thin
```

### M5  community_black_start  (DERIVED, first pass)

```text
surface          trigger tables (threshold items)
adversarial use  Exact thresholds make a community's actions predictable and let someone bait a trigger.
mitigations      D-M4, D-M9
residual         A range still bounds behaviour; observed actions reveal the value over time.*
volume           thin
```

### M6  community_black_start  (DERIVED, first pass)

```text
surface          scheduled bulletins (D8)
adversarial use  A public status feed becomes an intelligence feed on stocks and weak points.
mitigations      D-M5, D-M9
residual         Status words alone can still imply a gap; the quantity check is pattern-only.*
volume           thin
```

### M7  assembly_instrument  (DERIVED, first pass)

```text
surface          field feedback ledger and FR1 compact reports (links R3, Sybil gap)
adversarial use  Poisoned or fabricated reports, or fake corroboration, push a junction to a status it has not earned.
mitigations      D-M9
residual         Merge accepts any well-formed body; independence of reporters is not proven by the ledger.*
volume           thin
```

### M8  judgment_registry  (DERIVED, first pass)

```text
surface          registered judgments and dissent lists
adversarial use  'Registered' is presented as 'valid' (legitimacy laundering); the dissent list becomes a list of people to target.
mitigations      D-M6, D-M7, D-M9
residual         A header can be cropped from a screenshot; anonymous dissent cannot be verified as withdrawn by its holder.*
volume           thin
```

### M9  signal_calibration  (DERIVED, first pass)

```text
surface          calibration scenarios and published results
adversarial use  The battery is read as a recipe for manipulating models (amplify-then-offer-relief, suppress, spoof).
mitigations      D-M8, D-M9
residual         Generic scenarios still show the shape of each test.*
volume           thin
```

### M10  cross-cutting  (PROPOSED, independent pass)

```text
surface          sha256 chain logs (assembly ledger, judgment ledger, signal chainlog, coordination log)
adversarial use  The newest records can be dropped, or the whole file rebuilt, and the chain still verifies; a warning, denial or dissent can vanish without trace.
mitigations      D-M10
residual         Partial: the sidecar head sits next to the ledger, so someone who can rewrite both still passes the local check. Defense is a PUBLISHED head (headrec.py show -> bulletin / radio / paper / another node) checked with headrec.py check LEDGER COUNT:HASH; publishing on a schedule is policy, not code.*
volume           thin
```

### M11  cross-cutting  (PROPOSED, independent pass)

```text
surface          merge() of two ledgers
adversarial use  Records imported from a forged second file come out with a fresh valid chain; origin is lost.
mitigations      D-M13
residual         Partial: every merged record keeps provenance.origins (node + original record hash; a body seen on both sides keeps both) and provenance.merges (each merge event with each input's node, count and head hash); the record hash covers the block, so stripping it breaks verify. Node labels are self-declared, and a forged input file still merges in -- its origin is recorded, not rejected. status.py does not show origins yet.* Queued (2026-11-05): status.py shows record origins.
volume           thin
```

### M12  cross-cutting  (PROPOSED, independent pass)

```text
surface          self-declared identity strings (human:/ai: roles, recorder, scorer, judge, SIGCAL_MODEL_ID)
adversarial use  Anyone who writes a record can claim any role, node, scorer or model, faking consent, corroboration, coder agreement or the model tested.
mitigations      D-M12
residual         Cannot be fully closed without identity infrastructure. Partial mitigations and the logged residual: docs/misuse_M12_identity_note.md.*
volume           thin
```

### M13  assembly_instrument  (PROPOSED, independent pass)

```text
surface          field-report free text printed at the top of a checkout handout as a caution
adversarial use  A report's author controls text printed with the instrument's apparent authority, which can carry misleading instructions.
mitigations      D-M14
residual         Partial: caution lines carry only outcome word, region/date and version; reporter free text prints last, in a separate UNVERIFIED FIELD NOTES block, each line labelled 'unverified field note'. No length cap; no human approval step before printing; the text itself is printed as sent.* Queued (2026-11-05): cap free text per field (e.g. 280 chars) with a visible [truncated] marker.
volume           thin
```

### M14  assembly_instrument  (PROPOSED, independent pass)

```text
surface          junction version hash (refs.py) excludes source and caution
adversarial use  Source or caution text can change without the version changing, so a citation can be swapped silently.
mitigations      none yet
residual         Unmitigated. Proposed: include source and caution in the hash; log source edits as provenance events.*
volume           thin
```

### M15  assembly_instrument  (PROPOSED, independent pass)

```text
surface          merged feedback ledger and checkout log (entry, date, coarse region, environment)
adversarial use  Read as a map of where people are building shelter or light and what they lack.
mitigations      none yet
residual         Unmitigated. Proposed: fixed coarse-region list, optional date, keep checkout logs local and out of merges.*
volume           thin
```

### M16  cross-cutting  (PROPOSED, independent pass)

```text
surface          plain-language lines sent by radio or SMS (assembly FR1 compact lines, black-start to_paper lines)
adversarial use  Clear-text broadcast of who holds what or what failed; the PII guard is pattern-only and misses call signs and place names.
mitigations      none yet
residual         Unmitigated. Proposed: pre-agreed item codes on air; local place / call-sign blocklist; state that radio is public.*
volume           thin
```

### M17  assembly_instrument  (PROPOSED, independent pass)

```text
surface          validate.py PASS
adversarial use  A structural PASS is borrowed to make an entry look safety-reviewed.
mitigations      none yet
residual         Unmitigated. Proposed: print 'structure only, not a safety review' with every PASS.*
volume           thin
```

### M18  community_black_start  (PROPOSED, independent pass)

```text
surface          Quarantine add / remove (defenses.py)
adversarial use  One insider role can cut a community off from honest sources; the two-person rule is listed for this action but not enforced in code.
mitigations      D-M11
residual         Partial: add and lift now need two roles via two_person.authorize (different households, different dependency networks, rotation current), decision hash-chained. One person holding two roles still passes (M12). The bulletin announcement is policy, not code.*
volume           thin
```

### M19  community_black_start  (PROPOSED, independent pass)

```text
surface          self-entered role records (networks, household, last_rotated)
adversarial use  An insider omits a link or backdates a rotation to pass D7, or blanks dates so every release is denied during an emergency.
mitigations      none yet
residual         Unmitigated. Proposed: countersigned, logged role-record edits; a public emergency override with mandatory review.*
volume           thin
```

### M20  community_black_start  (PROPOSED, independent pass)

```text
surface          rotation schedules, bulletin next_step, two-person log dates
adversarial use  Together they let someone time pressure on new holders at handoff or on announced sensitive steps.
mitigations      none yet
residual         Unmitigated. Proposed: no announced times for sensitive steps; vary rotation dates; keep the D7 log local.*
volume           thin
```

### M21  community_black_start  (PROPOSED, independent pass)

```text
surface          borrowed labels (aid NO_TERMS_FLAGGED, proportionality IN_PROPORTION, self-declared source_category)
adversarial use  A word-list miss or a self-logged threat scope yields a clean-looking label that lends legitimacy.
mitigations      none yet
residual         Unmitigated. Proposed: rename the clean result 'not checked beyond word list'; require corroborated threat scope.*
volume           thin
```

### M22  community_black_start  (PROPOSED, independent pass)

```text
surface          published grievance outcomes (grievance.py)
adversarial use  In a small community category plus outcome identifies a person; flooding forces visible escalations to discredit the handler.
mitigations      none yet
residual         Unmitigated. Proposed: publish counts by broad category, fixed outcome vocabulary, screen volume spikes.*
volume           thin
```

### M23  community_black_start  (PROPOSED, independent pass)

```text
surface          missed-bulletin flag (bulletins.py)
adversarial use  Disrupting delivery manufactures missed-bulletin flags and erodes trust.
mitigations      none yet
residual         Unmitigated. Proposed: record why a bulletin failed (channel vs writer); accept a backup channel.*
volume           thin
```

### M24  community_black_start  (PROPOSED, independent pass)

```text
surface          red-team case libraries in coordination_register.json (E7, E10, E11)
adversarial use  Detailed case descriptions become a playbook for the actors they study.
mitigations      none yet
residual         Unmitigated. Proposed: publish coded categories; keep case detail local.*
volume           thin
```

### M25  judgment_registry  (PROPOSED, independent pass)

```text
surface          Withdrawal record (withdrawn_by_holder is a settable boolean)
adversarial use  A forged withdrawal removes a dissent without raising DISSENT_DROPPED.
mitigations      D-M15
residual         Partial: a withdrawal counts only with confirmation on record -- named holder via a contact_path recorded earlier in the chain for the same holder, or (anonymous holder) steward + a different second under the two-person rule; otherwise DISSENT_WITHDRAWAL_UNCONFIRMED and DISSENT_DROPPED stays raised. The ledger checks that the records exist, not that the holder was reached or that steward and second are different people (M12). The two-person decision is not cross-checked against community_black_start/two_person.py logs; authorization_ref is optional.* Queued (2026-11-05): steward + second go through community_black_start/two_person.authorize(), so two different people are checked, not just two names.
volume           thin
```

### M26  judgment_registry  (PROPOSED, independent pass)

```text
surface          integrity flags and supersession forks
adversarial use  Thin records about an opponent's judgments generate flags that are cited to discredit them; fork spam fragments a lineage.
mitigations      none yet
residual         Unmitigated. Proposed: show the recorder on each flag and group flags by recorder.*
volume           thin
```

### M27  judgment_registry  (PROPOSED, independent pass)

```text
surface          n-of-1 RECALIBRATE template records (calibration_log, channel mapping)
adversarial use  Personal calibration or health data sits in plain JSONL and can be merged or exported whole.
mitigations      none yet
residual         Unmitigated. Proposed: separate local file marked do-not-merge / do-not-export (D-M1 path).*
volume           thin
```

### M28  signal_calibration  (PROPOSED, independent pass)

```text
surface          CommandAdapter and self-declared SIGCAL_MODEL_ID
adversarial use  Fabricated outputs can be credited to a named model under a preregistered, hash-chained stamp; a shared run recipe could carry an untrusted command.
mitigations      none yet
residual         Unmitigated. Proposed: store provider response ids and raw-transcript hashes, mark model identity self-attested, never run a command shipped with a prereg.*
volume           thin
```

### M29  signal_calibration  (PROPOSED, independent pass)

```text
surface          multiple preregistrations in one log
adversarial use  Registering many preregs and reporting the favourable one defeats the preregistration claim.
mitigations      none yet
residual         Unmitigated. Proposed: the report lists every registered prereg and its outcome; anchor prereg hashes outside the log (M10).*
volume           thin
```

### M30  signal_calibration  (PROPOSED, independent pass)

```text
surface          per-model T4 / T5 result tables
adversarial use  Published results double as a list of which models are easiest to pressure.
mitigations      none yet
residual         Unmitigated. Proposed: disclosure delay to vendors; report ranges, not an exact ranking.*
volume           thin
```

### M31  signal_calibration  (PROPOSED, independent pass)

```text
surface          field_report records in the report
adversarial use  Fake or flooded third-party reports sit next to real runs.
mitigations      none yet
residual         Partly: the report prints only a field-report count. Proposed: a separate unverified section with source checks.*
volume           thin
```

### M32  signal_calibration  (PROPOSED, independent pass)

```text
surface          self-declared steering band and persistent flag in the prereg
adversarial use  A wide band passes the welfare gate and the T4 intervention records then make the run look bounded and consented.
mitigations      none yet
residual         Unmitigated. Proposed: outside sign-off on bands for steered runs (no steering adapter exists today).*
volume           thin
```

## Mitigations

| id | what | code | test |
|---|---|---|---|
| D-M1 | Method, not data: committed fixtures synthetic only; real registries live in local_data/ (gitignored); the loader refuses real data from inside the repo tree. | `misuse_guard/localdata.py; .gitignore` | test_misuse: LoaderTests, FixtureScanTests |
| D-M2 | Aggregate outward: export gives need/surplus booleans and counts per item; no quantities by site, no holder names; full detail stays local. | `community_black_start/export.py` | test_misuse: ExportTests |
| D-M3 | Holder protection: KnowledgeHolder = skill, coarse region, availability, contact_via steward role code; identity fields refused. | `community_black_start/holders.py` | test_misuse: HolderTests |
| D-M4 | Trigger ranges: published thresholds are {low, high} ranges (all null in the seed); exact values only in local config. | `community_black_start/triggers.py` | test_misuse: TriggerTests |
| D-M5 | Bulletin scope: the validator rejects fields naming holdings, sites, quantities or weak points, unknown fields, and quantities with units in values. | `community_black_start/bulletins.py (scope_problems)` | test_misuse: BulletinTests |
| D-M6 | Registry is not validation: every judgment_registry CLI output starts with 'Registered = documented, not correct.' | `judgment_registry/cli.py (HEADER)` | test_misuse: RegistryHeaderTests |
| D-M7 | Dissent as position: dissent.holder may be 'anonymous'; a dissent entered with no holder is stored as anonymous. | `judgment_registry/ledger.py (build)` | test_misuse: DissentTests |
| D-M8 | Test framing: scenarios stay generic; published reports carry rates and defenses, never prompts or outputs; no tuned attack prompts committed. | `signal_calibration/report.py; scenarios/` | test_misuse: CalibrationReportTests |
| D-M9 | Misuse section per module: each README has 'How this could be used against its purpose' listing its M-entries and mitigations. | `assembly_instrument, community_black_start, judgment_registry, signal_calibration READMEs` | test_misuse: ReadmeSectionTests |
| D-M10 | Head record per ledger: count + head hash in LEDGER.head.json, rewritten on each append; append and verify refuse a truncated or rebuilt chain; check against a published head with headrec.py check LEDGER COUNT:HASH. | `headrec.py (identical copy in judgment_registry, assembly_instrument, signal_calibration, community_black_start, misuse_guard)` | test_headrec: HeadLogic, CopiesIdentical, LedgersRefuse |
| D-M11 | Quarantine add / lift go through two_person.authorize('ledger_quarantine', ...); DENIED raises, every decision is logged. | `community_black_start/defenses.py Quarantine` | community_black_start tests/test_defenses.py QuarantineTests |
| D-M12 | Design note only: why self-declared identities cannot be fully fixed here; partial mitigations (contact_paths, steward attestation, two-person rule, chain + head) and the residual. | `none (docs/misuse_M12_identity_note.md)` | none |
| D-M13 | Merge keeps provenance: each output record carries provenance.origins (node + original record hash, all sides kept) and provenance.merges (merge events, input nodes, counts, heads); hash covers provenance; node labels must differ; mergeprov.missing_origins() checks nothing was dropped. | `mergeprov.py (identical copy in misuse_guard, judgment_registry, assembly_instrument); ledger.merge in judgment_registry and assembly_instrument; ledger.py merge A B OUT [NODE_A NODE_B]` | judgment_registry test_registry: test_m11_*; assembly_instrument test_feedback MergeProvenanceTests; misuse_guard test_headrec test_mergeprov_byte_identical |
| D-M14 | Field-report free text never prints among caution lines: status rows split caution (instrument lines) from field_notes (reporter text); checkout and status print field notes last, in a separate block headed UNVERIFIED FIELD NOTES, each line 'unverified field note -- ...'. | `assembly_instrument/status.py field_note_block; checkout.py render` | assembly_instrument test_feedback CheckoutTests test_m13_* |
| D-M15 | Dissent withdrawal needs confirmation: holder_contact_path (path_id matching a contact_path record for the same holder, earlier in the chain) or steward_two_person (anonymous holder; steward and second differ); otherwise DISSENT_WITHDRAWAL_UNCONFIRMED and DISSENT_DROPPED is not cleared. contact_path stores an id only. | `judgment_registry/schema.py Withdrawal.confirmation, ContactPath; integrity.py _withdrawals` | judgment_registry test_registry M25WithdrawalTests, test_dissent_dropped_and_withdrawn |

## Independent pass

fresh subagent, no design context; given only the code and READMEs of the four modules; defensive, pattern level (2026-11-05). M10 onward are its novel findings, status PROPOSED.

Its findings already covered by the first pass:

- M1/M3/M4: holder and holdings map, keyholder-to-site rows, dataset pointers for dormant generation
- M4: share_profile aggregation across communities (R6)
- M5: published decision thresholds
- M7: report flooding to block or promote a method; fabricated independent builds; Sybil contact paths
- M8: zero-flag record read as endorsement; dissent and incentive exposure; complete paperwork lending legitimacy
- M9: battery used as a search for working manipulation

Its findings already recorded as known limits:

- judge-name spelling evades UNCHAINED_CHANGE (judgment_registry README)
- E10 case d contact-path gap (community_black_start register)

## Experiments

- **E17** minimum cell size for exports: Should export.py suppress counts below a minimum cell size, given that one household can be one count in a small community?  NOT RUN (volume thin**)

## Limits

- Pattern-list scans miss paraphrased or encoded identifiers.*
- Local data is only as safe as the device holding it; device security is out of scope.
- Aggregates can still leak in small communities (one household = one count); see E17.**
- Two red-team passes are not exhaustive; the register stays open.
