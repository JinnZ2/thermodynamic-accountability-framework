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
