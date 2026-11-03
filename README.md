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
items.json        seed: 28 items across L0-L3; every unknown number null, volume thin
chain.py          load, validate, level check, criticality, single points, order
community.py      Community(name, holders, buffer_hours); gaps(), interconnect()
cli.py            command line
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
python3 -m unittest discover -s tests     # 21 tests
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
2  Single points of failure: household_buffer (19 dependents), people_deployable
   (18), spare_relays (2). The top two are people, not equipment.
3  15 level inversions: town water, sewer and medical items sit on L1 power,
   fuel and transport; town water also sits on L2 chlorine; dormant hydro needs
   L2 knowledge holders.
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
