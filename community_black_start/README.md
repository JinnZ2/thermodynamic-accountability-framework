# community-black-start

Provenance: co-authored (Kavik + Claude), 2026-11-03. License: CC0 1.0
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
items.json        seed: 29 items across L0-L3; every unknown number null, volume thin
chain.py          load, validate, level check, criticality, single points, order
community.py      Community(name, holders, buffer_hours); gaps(), interconnect()
cli.py            command line
coordination.py   AI coordination layer: share profile, propose, human consent, paper line, chained log
coordination_register.json  risks R1-R8 -> code -> defenses D1-D5 -> backups B1-B6 -> experiments E1-E9
defenses.py       R8 outside actors: aid control terms, claim corroboration, direct contact, local quarantine
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
python3 -m unittest discover -s tests     # 53 tests
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
2  Single points of failure: household_buffer (20 dependents), people_deployable
   (19), spare_relays (2). The top two are people, not equipment.
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
E1-E9               NOT RUN  each has a cleanest test and the null that would rule it out
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
D4 aid provenance  AidRecord: source category, verbatim conditions, plain line;
                   aid_status() flags control terms (exclusivity, single-channel
                   distribution, access to holdings/records, embedded personnel,
                   authority claims, debt/lien, loyalty) -> human must read every term
D5 direct contact  a claim ABOUT another community -> DO_NOT_ACT until confirmed
                   with that community itself (counters engineered distrust)
B6 quarantine      Quarantine: one community blocks a node or source from its own
                   ledger; human role + plain reason; no network vote
E7 pattern library historical exploitation cases -> entry channels**     NOT RUN
E8 early signals   red-team tabletop; can vetters tell?**                 NOT RUN
```

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
```

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

## License

CC0 1.0 Universal. See `LICENSE`.
