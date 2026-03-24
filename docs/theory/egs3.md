# Signal-Fire — Field Reporting Guide

**Purpose:** Capture friction, workarounds, and system state in real time with minimum cognitive load. One line per observation. No narrative. No justification. State plus action.

-----

## Format

```
[Location] | [State] | [Friction Type] | [Action Taken]
```

**Location:** Mile marker, yard, dock, intersection, terminal, route segment, or domain name.

**State:**

- **STABLE** — Normal operations. No deviation detected.
- **DEVIATION** — Friction present. Workaround applied or situation developing.
- **CRITICAL** — Immediate risk. Intervention required or already underway.

**Friction Type:**

- **Equipment** — Broken, miscalibrated, missing, or degraded tool/vehicle/sensor
- **Infrastructure** — Road, bridge, port, facility, or structural issue
- **Weather** — Storm, flood, wind, heat, ice, visibility
- **Supply Chain** — Delay, misroute, missing inventory, sequence error
- **Administrative** — Paperwork, slow approval, miscommunication, policy friction
- **Personnel** — Understaffing, fatigue, skill mismatch, coordination failure

**Action Taken** (optional): What you did to hold the line. If nothing needed, omit.

-----

## Examples

```
Walmart DC Yard B | DEVIATION | Equipment | GPS offset 4m, manual correction applied
Route 22 MM 147 | CRITICAL | Infrastructure | Bridge surface deterioration, reduced speed
Terminal 5 Dock 3 | DEVIATION | Supply Chain | Trailer sequence error, rerouted to Dock 7
I-40 Westbound MM 203 | STABLE | Weather | Light rain, no action needed
Yard A Gate 2 | DEVIATION | Administrative | 33-min search for assigned trailer, no system fix
Route 15 MM 89 | CRITICAL | Personnel | Fatigue after 14hr, pulled over for reset
```

-----

## Rules

1. **One line per observation.** If it takes more than one line, you are explaining instead of reporting.
1. **State, not story.** Report what is, not why you think it happened.
1. **No narrative required.** The system connects patterns across reports. You do not need to.
1. **Silence equals stable.** If you do not report, the system assumes you are holding the line. Passive maintenance is credited as work.
1. **Workarounds are data.** Every temporary fix you apply is expertise the system needs to capture. Log it.

-----

## What Happens to Your Reports

- Each entry is timestamped and geotagged automatically
- AI aggregation layer identifies recurring friction patterns across reporters and locations
- High-frequency friction points are flagged for structural repair
- Your workarounds are catalogued and propagated to other operators facing the same friction
- Prevention credit: if your zone stays STABLE, you are credited with the entropy you prevented

-----

## Severity Reference

|State    |Meaning                         |System Response                                                                  |
|---------|--------------------------------|---------------------------------------------------------------------------------|
|STABLE   |Normal operations               |Prevention credit applied. No action.                                            |
|DEVIATION|Friction present, manageable    |Logged. Pattern-matched. Flagged if recurring.                                   |
|CRITICAL |Immediate risk or active failure|Priority alert. Cross-validated with independent sensors. Escalated if confirmed.|

-----

*Your expertise is in what you notice and what you fix before anyone else sees it. This system makes that visible without requiring you to write a report about it.*
