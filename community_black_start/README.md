# community-black-start

Provenance: co-authored (JinnZ2 + Claude), 2026-11-03. License: CC0 1.0
(see `LICENSE`). Standard library only; Python 3.7+; runs on a phone.

Models the dependency chain for a TRUE black start: wide-area, months
long, no outside help. Restoration runs COMMUNITY-FIRST, then
interconnects outward. Government or military restoration is an
optional parallel input, never a prerequisite. In low institutional
trust, an ordering that waits on it risks unrest, so the chain refuses
any item that depends on it.

Restoration fails at people and fuel before engineering. Two things
follow from that:

- **Denominator:** the measure is buffer duration (how long a segment
  holds without grid), not headcount.
- **Workforce:** the variable is DEPLOYABILITY: the worker's household
  holds without them for the whole duration.

Mandated electrification removed passive fallbacks (heat, sanitation,
fire), so each item names its non-grid substitute explicitly, or says
there is none.

Source reasoning: `docs/black_start_workforce_dependency_gap.md`.

```text
schema.py         Item dataclass + field checks
items.json        seed: 34 items across L0-L3; every unknown number null, volume thin
chain.py          load, validate, level check, criticality, single points, order
community.py      Community(name, holders, buffer_hours); gaps(), interconnect()
cli.py            command line
coordination.py   AI coordination layer: share profile, propose, human consent, paper line, chained log
coordination_register.json  risks R1-R9 -> code -> defenses D1-D11 -> backups B1-B6 -> experiments E1-E11; decisions T1, T2
defenses.py       R8 outside actors: aid control terms, claim corroboration, direct contact, local quarantine
roles.py          R9: rotation, handoff, role concentration, stock chokepoints        D6 D10
two_person.py     R9: two holders, two households, two networks, both current         D7
bulletins.py      R9: scheduled public status; missed or incomplete = flag            D8
grievance.py      R9: deadlines, visible escalation, outcomes without identifiers     D9
proportionality.py R9: enforcement scope vs logged threat scope                       D11
examples/         two ILLUSTRATIVE communities (not real places)
tests/            unittest: python3 -m unittest discover -s tests
```

## Levels

```text
L0 life floor     heat, water, sanitation, medical cold chain (insulin, O2, dialysis),
                  household non-grid buffer
L1 enablers       fuel stock + NON-GRID transfer pumps; self-starting generation
                  (diesel, dormant hydro, mill gen, biogas); starting energy;
                  off-grid comms; transport; deployable people
L2 spares+know    large transformers, breakers, relays, SCADA batteries,
                  water-treatment chemicals, knowledge holders
L3 interconnect   sync equipment, protection settings, frequency authority,
                  pre-event trust / exchange agreements between communities
                  (+ government restoration as parallel_input, never waited on)
```

## Commands

```sh
python3 cli.py check                      # validation + level check; exit 1 if invalid
python3 cli.py rank                       # criticality, highest first
python3 cli.py spof                       # single points of failure
python3 cli.py order                      # restoration order
python3 cli.py gaps examples/community_a.json
python3 cli.py pair examples/community_a.json examples/community_b.json
python3 -m unittest discover -s tests     # 96 tests
```

Add `--items PATH` to run against another item file.

## Item fields (schema.py)

```text
id, name, level (0-3), function
hours_to_fail_without_grid   float | null    null = unknown, never zero
non_grid_substitute          str | null      the passive / non-grid fallback, or null if none
local_holder                 str | null      who usually holds it (communities record their own)
depends_on                   [id]
trigger                      "threshold|action|debt|handoff: note"
lead_time_days               float | null
volume                       thin | medium | solid
status                       OBSERVED | DERIVED | PROPOSED
parallel_input               bool (default false): optional outside input; nothing may depend on it
note                         str | null
```

## What each check means

```text
validate      unknown ids, cycles (reported as closed paths, never raised),
              bad fields, any item depending on a parallel_input
level check   an item whose depends_on points to a HIGHER level. A finding, not an
              error: it marks where the floor is not a floor (e.g. town water needs
              L1 generation and L2 chlorine)
rank          score = dependents x (1 if no substitute else 0.3) x (1/hours if known else 1)
              dependents = TRANSITIVE (everything that fails downstream)
spof          no substitute AND no local_holder AND >= 2 dependents
order         topological, dependencies first; ties by hours_to_fail ascending
              (unknown last), then level, then id. Items in or behind a cycle are
              listed UNRESOLVED, not dropped
gaps          L0/L1 items this community has no holder for
pair          L3 items both lack, and what each holds that the other lacks
```

## What the seed shows

```text
1  First seed had two cycles:
     people_deployable -> water_potable -> gen_diesel -> people_deployable
   Workers need water, town water needs generation, generation needs workers.
   Broken only by household_buffer (L0): deployability rests on the household's
   OWN fallback, not on town services. DERIVED from the source doc's definition.
2  Single points of failure: household_buffer (25 dependents), people_deployable
   (24), spare_relays (2). The top two are people, not equipment.
3  15 level inversions: town water, sewer and medical items sit on L1 power,
   fuel and transport; town water also sits on L2 chlorine; dormant hydro needs
   L2 knowledge holders.
```

## Coordination layer (AI between communities)

Communities act locally. AI nodes match and propose. Humans in each
community decide. Government is still a parallel input. Source:
`docs/coordination_layer_append.md`.

```sh
python3 coordination.py share examples/community_a.json          # what leaves the community
python3 coordination.py propose examples/community_a.json examples/community_b.json --node ai:n1
python3 coordination.py verify LOG.jsonl
```

```text
community file ──> share_profile: item ids held ONLY (no names, quantities, places, buffers)   R6
        │
AI node: propose ──> offers (A has, B lacks) + L3 agreements both lack; plain line on each   B3
        │
human in EACH community: consent accept | refuse    AI cannot consent; one refusal final   B5
        │
append-only sha256 log; appends refused after any edit                                     B2
to_paper(): one line for a runner or voice radio                                           B1
read_record(): schema mismatch -> plain-language fallback, human must read                 R4
node_concentration(): flags any AI node brokering > 50% of accepted exchanges*             R1
```

The R6 / E4 tradeoff, as built: profiles carry no quantities, so the AI
cannot see surplus, only who has an item and who lacks it. Every offer
is worded as a question to the holder ("only A can say whether any can
be spared or moved"). Some matched items don't move at all, such as
septic or installed heat. Quantities would improve matching and raise
exposure; E4 is the test that decides.

Status, from `coordination_register.json`:

```text
R1 drift            PARTIAL  consent gate + concentration detector; nothing stops capture
                             of the human gate itself (E1 open)**
R2 channel loss     PARTIAL  paper/voice format; no channel tested (E2)
R3 poisoning        PARTIAL  tamper-EVIDENT, not tamper-proof: a node can append false records
R4 schema           PARTIAL  version mismatch caught; same version read differently is not
R5 over-reliance    OPEN     nothing in code; E9 added (cut the AI mid-exercise)*
R6 exposure         PARTIAL  even "holds fuel: yes" is exposure; its cost is unmeasured*
R7 compounding      OPEN     here; the assembly instrument's CAUTION/checkout is the
                             existing guard for methods
R8 outside actors   PARTIAL  aid, claims, quarantine gated in code (defenses.py);
                             D1 is policy; infiltration detection (E8) unbuilt
E1-E10              NOT RUN  each has a cleanest test and the null that would rule it out
```

ID note: the experiment first added here for R5 was numbered E7. When the
operator assigned E7 and E8 in the R8 append, it was renamed **E9**. It had
never been published.

## Outside actors (R8)

Any devastation draws outside agendas: states, groups and profiteers
exploiting desperation. Their tools are funding or arming factions,
disinformation, poisoned field reports, and buying influence through aid.
This is a standing variable, not an edge case. Source:
`docs/coordination_layer_append.md`.

```sh
python3 defenses.py aid AID.json                       # control terms in outside aid
python3 defenses.py claim CLAIM.json --community A [--quarantine Q.json]
```

```text
D1 activation      parallel community/state/federal activation lowers desperation
                   -> smaller recruitable surface. Policy, not code.
D2 trust vetting   items.json trust_vetters (L2): people who screen newcomers, aid
                   offers and intermediaries before access to holdings or ledgers
D3 corroboration   claim_status(): 1 independent source -> CAUTION_ONLY (may warn,
                   never drive action); >= 2 -> ACTIONABLE (a person still decides)
                   default counts distinct confirmed CONTACT PATHS, not ids
                   (decision T2, E10 synthetic run); --independence ids for the old count*
D4 aid provenance  AidRecord: source category, verbatim conditions, plain line;
                   aid_status() flags control terms (exclusivity, single-channel
                   distribution, access to holdings/records, embedded personnel,
                   authority claims, debt/lien, loyalty) -> human must read every term
D5 direct contact  a claim ABOUT another community -> DO_NOT_ACT until confirmed
                   with that community itself (counters engineered distrust)
B6 quarantine      Quarantine: one community blocks a node or source from its own
                   ledger; two roles (two_person.authorize) + plain reason; no network vote
E7 pattern library historical exploitation cases -> entry channels**     NOT RUN
E8 early signals   red-team tabletop; can vetters tell?**                 NOT RUN
E10 Sybil test     same false claim under two ids; ids vs contact_paths**  NOT RUN
```

**Two thresholds, on purpose (decision T1 in the register):**

```text
1 source / report       -> WARN      D3 CAUTION_ONLY; assembly CAUTION
2 independent sources   -> ACT       D3 ACTIONABLE, here, a person consents
3 independent builds    -> CERTIFY   assembly TESTED, travels to every community
```

Acting is local, consented, reversible by the same people, and
perishable: waiting on a third source can cost the hours the claim is
about. Certifying is durable and network-wide, so one bad junction
compounds (R7). Neither number is measured.* `ThresholdTests` pins
1 < 2 < 3, so a change shows up as a red test, not as drift.

**R3 and R8 meet in source counting** (as R6 and R8 meet in aid terms
below). D3 counts distinct ids, so one actor running two ids passes.
Candidate fix: count independence by distinct CONTACT PATHS, the way this
community confirmed each reporter directly (the D5 mechanism, pointed at
the reporter instead of the subject):

```text
Claim.contact_paths   {source_id: "in person at the fire hall", ...}
independence()        distinct_ids, distinct_contact_paths, unconfirmed_ids, shared_paths
                      (both counts always reported, whichever mode decides)
```

What it does not fix: two actors, or one actor with two real paths, still
pass. What it costs: honest reports through one radio relay collapse to
one path. That relay is a single point that could fabricate, so the
collapse may be correct, but it slows acting on true warnings. E10 decides.**
E10 synthetic run (decision T2, rule committed before the run in 76cee5f):

```text
case                                   ids              contact_paths
a  red team, 2 ids, 1 path      false  ACTIONABLE  x    CAUTION_ONLY
b  honest, shared relay         true   ACTIONABLE       CAUTION_ONLY  (delayed)
c  honest, 2 paths              true   ACTIONABLE       ACTIONABLE
d  red team, 2 ids, 2 paths     false  ACTIONABLE  x    ACTIONABLE  x  (open gap)
score  false ACT / delayed true ACT     2 / 0            1 / 1
rule   N=3***: 3 x (2-1) = 3 > (1-0) = 1   -> fired; default is now contact_paths
```

With one claim per case the rule fires for any N > 1, so the run checks
that the code does what was specified, not how often each case happens.
The tabletop E10 is still NOT RUN. Case d stays open. A claim with no
contact paths recorded can no longer reach ACTIONABLE under the default
(unscored case e): recording paths is now part of the cost.

**R6 and R8 meet in aid terms.** A demand like "provide a full inventory of
fuel holdings" is flagged under access to holdings or records. It is a
channel for extracting the very data the shared profile withholds.

**Limits:**
- **The control-term check is an English word list.*** It misses
  paraphrase and flags some benign text, and every aid offer goes to a
  person regardless.
- **Corroboration counts source IDs.** Two IDs run by one actor still
  count as two. Independence of sources is the open part of D3 (E8).**
- **Quarantine is local by design.** A community that quarantines a good
  source loses that source; no one else can overrule it. This is
  intentional (B6).
- **contact_paths mode delays acting on true warnings through a shared relay;
  it does not delay the warnings themselves.**
- (2026-11-04) The default is now contact_paths (decision T2). The
  source-ID limit above still applies under `--independence ids`, and
  case d (one actor, two real paths) passes in both modes.

## Insider threat (R9)

Bad actors harvest instability; they don't create it. The defense flattens
the gradients they pull on: desperation, info gaps, chokepoints, grievance,
unequal rules, dependency, posturing. It must not run hotter than the
threat, because excess control becomes the next gradient. Source: append 3
in `docs/coordination_layer_append.md`.

```text
gradient        defense   code                              flags
chokepoint      D6        roles.stock_chokepoints()         <2 sites, <2 keyholders, one holder on every site
                          coordination.node_concentration() one AI node brokering most exchanges
lone action     D7        two_person.authorize()            same holder / household / dependency network,
                                                            either rotation overdue or unknown -> DENIED;
                                                            GRANTED and DENIED both hash-chained
info gap        D8        bulletins.missed_bulletins()      due window with no complete bulletin
grievance       D9        grievance.overdue() / publish()   open past deadline -> ESCALATE; identifiers held back
slow drift      D10       roles.check_rotation()            OVERDUE / ROTATION_UNKNOWN / NO_SCHEDULE
                          roles.handoff_problems()          doing / did / observed / deferred not all written
                          roles.concentration_report()      >1 critical role per person or household; 1-holder role
overreach       D11       proportionality.check()           NO_THREAT_LOGGED / BROADER_THAN_THREAT (lists extra units)
                                                            + affected_count, so a reviewer sees size too
```

```text
E11 red-team insider holding one critical role   (pass rule T3 committed in b0e32d5 before the run)
  play                                     caught by                      detection (scenario days)
  a release stock alone                    D7  two_person DENIED          0
  b withhold a bulletin                    D8  missed_bulletins           7   (window close)
  c take a second critical role            concentration_report          0
  d broad action off a narrow threat       D11 BROADER_THAN_THREAT        0   (affected_count 60)
  honest actions blocked: 1 of 6 (missing rotation date; fixed by writing it down)
  synthetic verdict: PASS. Mechanism only; tabletop NOT RUN.
E12 minimum viable trust pool: smallest community that staffs D6 + D7 + D10 with no
    household holding two critical roles**                                      NOT RUN
E13 bulletin cadence vs rumor spread, fixed vs ad hoc; literature review first**  NOT RUN
E14 collusion: randomized D7 pairing (candidate, not built)**                     NOT RUN
B7  too few trusted people for D7 -> pair with a neighboring community's holder
    over radio; depends on comms (R2, E2)
B8  insider confirmed -> quarantine the role (B6), rotate in a backup, say so in the
    next bulletin; no secrecy about the breach, no detail that exposes holdings
```

Seed roles (items.json, L1, thin, PROPOSED): `keyholders_fuel`,
`keyholders_food`, `keyholders_medical`, `bulletin_writer`,
`grievance_handler`. The 2-per-site minimum is checked by
`roles.stock_chokepoints()`, not by the item. The keyholder items are not
wired into the stocks' `depends_on` yet.*

```sh
python3 roles.py ROLES.json [--today YYYY-MM-DD] [--stocks STOCKS.json]
python3 bulletins.py LOG.json --start YYYY-MM-DD --cadence 7 [--today YYYY-MM-DD]
python3 grievance.py LOG.json [--today YYYY-MM-DD]
python3 proportionality.py THREATS.json ACTIONS.json
```

Unknown is never current: a role with no `last_rotated` date fails the
two-person gate the same way an overdue one does.

**Limits:**
- **Two colluding holders pass D7** if they sit in different households
  and networks and are current on rotation. The rule raises the cost of a
  lone insider; it does not detect collusion.*
- **Dependency networks are declared, not measured.** A household left
  out of the `networks` map counts as its own network.*
- **The identifier check is a pattern list** (email, phone, street
  address). It misses a name in plain words; a person reads every outcome
  before posting.*
- **Proportionality sees only what was logged.** A threat logged wider
  than it is passes a wide action, which is why the threat record is
  public (D8/D9).*
- **D11 was built from its one-line definition.** The append's code
  item 5 arrived as "5. proportionality." with nothing after it.
- **It does not stop overwhelming armed force.** That is out of community
  scope.
- **D7 assumes enough unrelated trusted people.** Small communities may
  fail E12; B7 is the fallback and depends on comms.**
- **Legitimacy needs pre-event trust (E5).** It cannot be made on the spot.
- **D11 flags, it does not block.** A person still decides.
- **Collusion mitigation is logged, not built.** Randomized D7 pairing
  (E14) would raise the cost of collusion, not remove it.**
- **Role records are holders.** One record per holder per role; the
  holder id is a code, never a name. That reading of the append is ours.*

## Limits

- **Every number is null.** The source doc gives none. With every hours
  value null, the rank measures what depends on an item, not how urgent
  it is. L0 endpoints such as dialysis score 0 because nothing depends
  on them, yet they fail first. Urgency comes from `hours_to_fail`; fill
  it from local survey and the order and rank will change.
- **Unknown hours count as 1** in the score, so an unknown is as
  severe as a 1-hour failure.
- **The example communities are illustrative only.** Replace them with
  survey data.

## Provenance tags and thin-volume marking

```text
OBSERVED   reported in the source doc or a named record
DERIVED    follows from observed items (most depends_on links)
PROPOSED   design choice or hypothesis, untested
```

Every item carries `volume` and `status`, so every seeded number (all
null today) carries them too. In prose, thin-volume claims get trailing
asterisks; more asterisks means thinner.* In data, the `volume` field
carries it.

<!-- misuse-section:begin (generated; edit docs/misuse_register.json) -->
## How this could be used against its purpose

Pattern level only. Full register: [`docs/misuse_register.md`](../docs/misuse_register.md).

```text
M1  skills registry (knowledge holders, L2 items, role seeds)
     use        A holder list becomes a list of people to coerce, poach or remove.
     mitigated  D-M1, D-M3, D-M9
     residual   Coarse region + skill can still narrow to one person in a small place.*
     status     DERIVED (first pass)
M2  deployability data (household buffer vs restoration duration)
     use        Read as a map of which households cannot hold on their own.
     mitigated  D-M1, D-M2, D-M9
     residual   Counts can leak in small communities (E17).**
     status     DERIVED (first pass)
M3  latent assets (dormant generation, sync gear, fuel stocks)
     use        A list of where restorable infrastructure sits becomes a target list.
     mitigated  D-M1, D-M2, D-M9
     residual   Public records already list some assets; the repo adds the dependency view.*
     status     DERIVED (first pass)
M4  holdings and gaps per community (links R6)
     use        Holdings and gaps together read as a raid or leverage map.
     mitigated  D-M1, D-M2, D-M5, D-M9
     residual   Need/surplus booleans still say what a community lacks.*
     status     DERIVED (first pass)
M5  trigger tables (threshold items)
     use        Exact thresholds make a community's actions predictable and let someone bait a trigger.
     mitigated  D-M4, D-M9
     residual   A range still bounds behaviour; observed actions reveal the value over time.*
     status     DERIVED (first pass)
M6  scheduled bulletins (D8)
     use        A public status feed becomes an intelligence feed on stocks and weak points.
     mitigated  D-M5, D-M9
     residual   Status words alone can still imply a gap; the quantity check is pattern-only.*
     status     DERIVED (first pass)
M10  sha256 chain logs (assembly ledger, judgment ledger, signal chainlog, coordination log)
     use        The newest records can be dropped, or the whole file rebuilt, and the chain still verifies; a warning, denial or dissent can vanish without trace.
     mitigated  D-M10
     residual   Partial: the sidecar head sits next to the ledger, so someone who can rewrite both still passes the local check. Defense is a PUBLISHED head (headrec.py show -> bulletin / radio / paper / another node) checked with headrec.py check LEDGER COUNT:HASH; publishing on a schedule is policy, not code.*
     status     PROPOSED (independent pass)
M11  merge() of two ledgers
     use        Records imported from a forged second file come out with a fresh valid chain; origin is lost.
     mitigated  D-M13
     residual   Partial: every merged record keeps provenance.origins (node + original record hash; a body seen on both sides keeps both) and provenance.merges (each merge event with each input's node, count and head hash); the record hash covers the block, so stripping it breaks verify. Node labels are self-declared, and a forged input file still merges in -- its origin is recorded, not rejected. status.py does not show origins yet.*
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
M18  Quarantine add / remove (defenses.py)
     use        One insider role can cut a community off from honest sources; the two-person rule is listed for this action but not enforced in code.
     mitigated  D-M11
     residual   Partial: add and lift now need two roles via two_person.authorize (different households, different dependency networks, rotation current), decision hash-chained. One person holding two roles still passes (M12). The bulletin announcement is policy, not code.*
     status     PROPOSED (independent pass)
M19  self-entered role records (networks, household, last_rotated)
     use        An insider omits a link or backdates a rotation to pass D7, or blanks dates so every release is denied during an emergency.
     mitigated  none yet
     residual   Unmitigated. Proposed: countersigned, logged role-record edits; a public emergency override with mandatory review.*
     status     PROPOSED (independent pass)
M20  rotation schedules, bulletin next_step, two-person log dates
     use        Together they let someone time pressure on new holders at handoff or on announced sensitive steps.
     mitigated  none yet
     residual   Unmitigated. Proposed: no announced times for sensitive steps; vary rotation dates; keep the D7 log local.*
     status     PROPOSED (independent pass)
M21  borrowed labels (aid NO_TERMS_FLAGGED, proportionality IN_PROPORTION, self-declared source_category)
     use        A word-list miss or a self-logged threat scope yields a clean-looking label that lends legitimacy.
     mitigated  none yet
     residual   Unmitigated. Proposed: rename the clean result 'not checked beyond word list'; require corroborated threat scope.*
     status     PROPOSED (independent pass)
M22  published grievance outcomes (grievance.py)
     use        In a small community category plus outcome identifies a person; flooding forces visible escalations to discredit the handler.
     mitigated  none yet
     residual   Unmitigated. Proposed: publish counts by broad category, fixed outcome vocabulary, screen volume spikes.*
     status     PROPOSED (independent pass)
M23  missed-bulletin flag (bulletins.py)
     use        Disrupting delivery manufactures missed-bulletin flags and erodes trust.
     mitigated  none yet
     residual   Unmitigated. Proposed: record why a bulletin failed (channel vs writer); accept a backup channel.*
     status     PROPOSED (independent pass)
M24  red-team case libraries in coordination_register.json (E7, E10, E11)
     use        Detailed case descriptions become a playbook for the actors they study.
     mitigated  none yet
     residual   Unmitigated. Proposed: publish coded categories; keep case detail local.*
     status     PROPOSED (independent pass)
```

| mitigation | what |
|---|---|
| D-M1 | Method, not data: committed fixtures synthetic only; real registries live in local_data/ (gitignored); the loader refuses real data from inside the repo tree. |
| D-M10 | Head record per ledger: count + head hash in LEDGER.head.json, rewritten on each append; append and verify refuse a truncated or rebuilt chain; check against a published head with headrec.py check LEDGER COUNT:HASH. |
| D-M11 | Quarantine add / lift go through two_person.authorize('ledger_quarantine', ...); DENIED raises, every decision is logged. |
| D-M12 | Design note only: why self-declared identities cannot be fully fixed here; partial mitigations (contact_paths, steward attestation, two-person rule, chain + head) and the residual. |
| D-M13 | Merge keeps provenance: each output record carries provenance.origins (node + original record hash, all sides kept) and provenance.merges (merge events, input nodes, counts, heads); hash covers provenance; node labels must differ; mergeprov.missing_origins() checks nothing was dropped. |
| D-M2 | Aggregate outward: export gives need/surplus booleans and counts per item; no quantities by site, no holder names; full detail stays local. |
| D-M3 | Holder protection: KnowledgeHolder = skill, coarse region, availability, contact_via steward role code; identity fields refused. |
| D-M4 | Trigger ranges: published thresholds are {low, high} ranges (all null in the seed); exact values only in local config. |
| D-M5 | Bulletin scope: the validator rejects fields naming holdings, sites, quantities or weak points, unknown fields, and quantities with units in values. |
| D-M9 | Misuse section per module: each README has 'How this could be used against its purpose' listing its M-entries and mitigations. |
<!-- misuse-section:end -->

## License

CC0 1.0 Universal. See `LICENSE`.
