dependence.py — witness-dependence coefficient for skill inventories

Source: Independent Animal’s Creed, Principle II (2026).
License: CC0.
Dependencies: stdlib only.

Core claim (falsifiable):
Skill that requires no witness cannot be audited, automated, or taken.
Therefore: witness_dependence is a measure of fragility under system failure.

Energy-flow:
skill_log (events over time)
│
▼
┌──────────────────────────────────────┐
│ classify: witnessed / silent         │
│ classify: certified / uncertified    │
│ classify: recorded / unrecorded      │
└──────────────────────────────────────┘
│
▼
witness_dependence = f(observation_signal)
calibration_reserve = 1 - witness_dependence

Input schema:
{
“entity_id”: str,                        # person, team, org
“skill_log”: [
{
“skill”: str,
“timestamp”: str (ISO),
“context”: “witnessed”|“silent”|“recorded”|“certified”|“uncertified”,
“consequence_real”: bool
