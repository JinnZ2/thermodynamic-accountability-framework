# Community-to-community AI coordination layer

Operator append, recorded verbatim, 2026-11-03. Implementation map:
`coordination_register.json` (risk -> code -> backup -> experiment).

```text
APPEND — community-to-community AI coordination layer (co-authored, 2026-11-03)

DESIGN: communities act locally (speed); AIs carry cross-community coordination
(matching surplus↔gap, sequencing interconnects); humans in each community hold
authority. Government action = optional parallel input, never prerequisite.

RISKS
R1 coordination→control drift: whoever runs the AI layer becomes the new center *
R2 channel loss: AI-to-AI links fail in outage (power, towers, spectrum) 
R3 ledger poisoning: false reports or a compromised node rewrite methods/holdings
R4 schema divergence: communities' AIs read records differently → mismatched trades
R5 over-reliance: humans stop keeping manual capability; AI outage = paralysis
R6 inventory exposure: shared holdings data reveals who has fuel/food → target risk *
R7 compounding error across communities: one bad junction propagates network-wide

SPOTS NEEDING EXPERIMENTATION / DOCUMENTATION
E1 structural guard against R1 (rotation? multiple independent AI nodes? consent gates?) **
E2 low-power comms that actually hold for months: mesh, packet radio, sat — test in winter
E3 human reporting rate under stress (will people send the one line?) **
E4 how much holdings detail to share vs. keep local (R6 tradeoff) **
E5 trust formation between communities BEFORE event — what agreements work
E6 matching performance: AI vs. human coordinators on same scenario (tabletop exercise)

BACKUPS (degraded modes)
B1 AI link down → same records on paper, carried by runners / read over voice radio
B2 node compromised → append-only hash chain; other nodes reject unchained edits
B3 schema mismatch → plain-language fallback line on every record
B4 no network at all → each community runs standalone on its own L0/L1 holdings
B5 human override always: any community can refuse an AI-proposed exchange

Asterisks = thin volume.
```

## Append 2 (R8 outside actors), recorded verbatim, 2026-11-03

Instruction with it: "Wherever is best for AI". Recorded decision: this
repo moved into thermodynamic-accountability-framework as
`community_black_start/` (history kept), beside `assembly_instrument/`.

```text
APPEND — community-to-community AI coordination layer (co-authored, 2026-11-03)

RISK
R8 outside actors: any devastation draws outside agendas (states, groups,
   profiteers) exploiting desperation — funding/arming factions,
   disinformation, poisoned field reports, buying influence via aid.
   Standing variable, not edge case.

DEFENSES (map to existing pieces)
D1 activation: parallel community/state/federal activation lowers desperation
   → shrinks recruitable surface
D2 trust vetting: necessity-built trust-assessment skills (registry category)
   screen newcomers, aid offers, intermediaries
D3 ledger poisoning guard: single source can raise caution, never rewrite;
   corroboration from independent reporters required (see feedback loop task)
D4 aid provenance: tag every outside resource with source + conditions attached;
   flag aid that carries control terms
D5 info hygiene: claims about other communities need direct-contact confirmation
   before action (counters engineered inter-community distrust)

EXPERIMENTATION / DOCUMENTATION
E7 historical cases of outside exploitation in disasters/collapse (Bosnia, Somalia,
   others) → pattern library of entry methods **
E8 detection signals: what early infiltration looks like in a small community **

BACKUP
B6 any community can quarantine a node or source from its ledger without
   network-wide consensus

Asterisks = thin volume.
```

## Append 3 (R9 insider threat, D6-D11), recorded verbatim, 2026-11-04

The message as received ends at "5. proportionality." with no further
text. Item 5 was built from the D11 line alone; see `proportionality.py`.

```text
FRAME
Bad actors harvest instability; they don't create it. Defense = flatten the
gradients they pull on (desperation, info gaps, chokepoints, grievance,
unequal rules, dependency, posturing). Defense must not run hotter than the
threat; excess control creates the next gradient.

RISK
R9 insider threat: a trusted role (stock keeper, ledger operator, comms,
   switching, coordinator) is bought, coerced, exhausted, or acts on its own
   agenda. Includes slow drift: gradual control accumulation by one role.
   Standing variable, not edge case. Pairs with R1 (control drift) and R8.

DEFENSES
D6 no chokepoints: critical stocks (fuel, food, medical) split across ≥2 sites
   with ≥2 keyholders each; no single role holds a full inventory; coordination
   runs on ≥2 independent nodes.
D7 two-person rule: release of critical stock, energizing/switching, ledger
   quarantine actions, and accepting aid with flagged terms each need two
   roles from different households. Neither person can be the other's
   dependent. (Same principle as nuclear custody.)
D8 scheduled bulletins: plain-language public status on a fixed cadence
   (what's restored, what's next, what each household can do). Missing a
   bulletin is itself a flag. Feeds the POPULATION SEES/DOES column.
D9 grievance channel: every grievance logged with a response deadline;
   unanswered past the deadline → escalates visibly. Outcomes published
   without personal identifiers.
D10 rotation: stock, ledger, comms roles rotate on a set schedule; handoff
   protocol applies (doing / did / observed / deferred).
D11 proportionality: every enforcement action records the threat it answers
   and its scope; action broader than the logged threat gets flagged
   (guards against elite panic and collective punishment).

CODE (stdlib only, null-safe, phone-runnable)
1. roles.py: Role(id, name, household_id, critical: bool, rotation_days,
   last_rotated). check_rotation() lists overdue roles.
   concentration_report(): flags any household or person holding >1
   critical role, or any critical role with a single holder.
2. two_person.py: authorize(action, role_a, role_b) → denied if same
   household, same dependency network, or either role overdue for rotation.
   Every authorization is appended to the ledger (hash-chained).
3. bulletins.py: schedule + log; missed_bulletins() returns gaps.
   Bulletin template has required fields: restored, next_step, household_role,
   date. A bulletin that's missing a field doesn't count as published.
4. grievance.py: Grievance(id, category, logged, deadline, status,
   outcome_public). overdue() lists past-deadline items. No personal IDs.
5. proportionality.
```
