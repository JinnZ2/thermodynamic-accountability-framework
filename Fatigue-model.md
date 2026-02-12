#!/usr/bin/env python3
“””
Thermodynamic Analysis Engine v1
Strip any decision, claim, or policy down to energy fundamentals.
No ideology. No villains. Just flows, gaps, and hidden variables.

Usage: python thermo_engine.py
“””

import json
from datetime import datetime

def clear():
print(”\n” * 2)

def header():
print(”=” * 60)
print(”  THERMODYNAMIC ANALYSIS ENGINE v1”)
print(”  No narratives. Just energy flows.”)
print(”=” * 60)

def get_input(prompt, required=True, allow_list=False):
“”“Get user input, optionally as comma-separated list.”””
while True:
val = input(f”\n  {prompt}\n  > “).strip()
if val or not required:
if allow_list and val:
return [v.strip() for v in val.split(”,”) if v.strip()]
return val if val else “Unknown / Not stated”
print(”  (Required field - press enter to mark as Unknown)”)
return “Unknown / Not stated”

def score_feedback_integrity(delay, hidden_count, gap_score):
“””
Score how intact the feedback loop is.
0 = completely broken, 10 = tight feedback.
“””
score = 10.0
# Delay penalty
delay_penalties = {
“immediate”: 0, “days”: 1, “weeks”: 2,
“months”: 3, “years”: 5, “generational”: 8
}
score -= delay_penalties.get(delay, 4)
# Hidden variable penalty
score -= min(hidden_count * 0.75, 4)
# Decision-consequence gap penalty
score -= gap_score * 0.3
return max(round(score, 1), 0)

def assess_gap(deciders, consequence_bearers):
“””
Assess decision-consequence gap.
Returns 0-10 scale. Higher = more decoupled.
“””
print(”\n  — DECISION-CONSEQUENCE GAP —”)
print(f”  Who decides:           {’, ‘.join(deciders)}”)
print(f”  Who bears consequence:  {’, ’.join(consequence_bearers)}”)

```
overlap = set(d.lower() for d in deciders) & set(c.lower() for c in consequence_bearers)
if overlap:
    print(f"  Overlap detected:      {', '.join(overlap)}")

print("\n  How much overlap between deciders and consequence bearers?")
print("  0 = complete overlap (same people)")
print("  10 = total separation (no overlap)")
gap = ""
while not gap:
    gap = input("  Gap score [0-10]: ").strip()
    try:
        gap = float(gap)
        if 0 <= gap <= 10:
            return gap
        print("  Enter a number 0-10")
        gap = ""
    except ValueError:
        print("  Enter a number 0-10")
        gap = ""
```

def run_analysis():
“”“Main analysis loop.”””
header()

```
print("\n  Paste a decision, claim, policy, or proposal.")
print("  (Can be a sentence, paragraph, headline, whatever.)")
subject = get_input("SUBJECT OF ANALYSIS:")

print("\n" + "-" * 60)
print("  ENERGY FLOW MAPPING")
print("-" * 60)

energy_in = get_input(
    "What energy/resources go IN?\n"
    "  (money, labor, fuel, materials, attention, time...)\n"
    "  Comma-separated:",
    allow_list=True
)

energy_out = get_input(
    "What energy/resources come OUT?\n"
    "  (products, services, waste, heat, pollution, debt...)\n"
    "  Comma-separated:",
    allow_list=True
)

who_benefits = get_input(
    "Who captures the OUTPUT value?\n"
    "  Comma-separated:",
    allow_list=True
)

waste = get_input(
    "What is the WASTE / unaccounted cost?\n"
    "  (externalities, deferred maintenance, health costs,\n"
    "   environmental damage, human fatigue...)\n"
    "  Comma-separated:",
    allow_list=True
)

print("\n" + "-" * 60)
print("  DECISION STRUCTURE")
print("-" * 60)

deciders = get_input(
    "Who DECIDES? (individuals, roles, institutions)\n"
    "  Comma-separated:",
    allow_list=True
)

consequence_bearers = get_input(
    "Who ABSORBS CONSEQUENCE if it goes wrong?\n"
    "  Comma-separated:",
    allow_list=True
)

gap_score = assess_gap(deciders, consequence_bearers)

print("\n" + "-" * 60)
print("  FEEDBACK INTEGRITY")
print("-" * 60)

print("\n  What's the TIME DELAY between decision and consequence?")
delays = ["immediate", "days", "weeks", "months", "years", "generational"]
for i, d in enumerate(delays):
    print(f"    {i + 1}. {d}")
delay_choice = ""
while not delay_choice:
    delay_choice = input("  Choice [1-6]: ").strip()
    try:
        delay_choice = delays[int(delay_choice) - 1]
    except (ValueError, IndexError):
        print("  Enter 1-6")
        delay_choice = ""

hidden = get_input(
    "What HIDDEN VARIABLES are missing from the narrative?\n"
    "  (data not collected, people not consulted,\n"
    "   costs not measured, signals not received...)\n"
    "  Comma-separated:",
    allow_list=True
)
hidden_count = len(hidden) if isinstance(hidden, list) else 0

feedback_score = score_feedback_integrity(delay_choice, hidden_count, gap_score)

# --- ANALYSIS OUTPUT ---
clear()
print("=" * 60)
print("  THERMODYNAMIC ANALYSIS REPORT")
print("=" * 60)
print(f"\n  Subject: {subject}")
print(f"  Date:    {datetime.now().strftime('%Y-%m-%d %H:%M')}")

print(f"\n  {'─' * 56}")
print(f"  ENERGY FLOWS")
print(f"  {'─' * 56}")
print(f"  IN:    {', '.join(energy_in) if isinstance(energy_in, list) else energy_in}")
print(f"  OUT:   {', '.join(energy_out) if isinstance(energy_out, list) else energy_out}")
print(f"  WASTE: {', '.join(waste) if isinstance(waste, list) else waste}")
print(f"  VALUE CAPTURED BY: {', '.join(who_benefits) if isinstance(who_benefits, list) else who_benefits}")

print(f"\n  {'─' * 56}")
print(f"  DECISION-CONSEQUENCE MAP")
print(f"  {'─' * 56}")
print(f"  DECIDERS:              {', '.join(deciders) if isinstance(deciders, list) else deciders}")
print(f"  CONSEQUENCE BEARERS:   {', '.join(consequence_bearers) if isinstance(consequence_bearers, list) else consequence_bearers}")
print(f"  GAP SCORE:             {gap_score}/10", end="")
if gap_score >= 7:
    print("  !! SEVERE DECOUPLING")
elif gap_score >= 4:
    print("  ! SIGNIFICANT GAP")
else:
    print("  (acceptable)")

print(f"\n  {'─' * 56}")
print(f"  FEEDBACK INTEGRITY")
print(f"  {'─' * 56}")
print(f"  DELAY:             {delay_choice}")
print(f"  HIDDEN VARIABLES:  {hidden_count} identified")
if isinstance(hidden, list):
    for h in hidden:
        print(f"    - {h}")
print(f"  FEEDBACK SCORE:    {feedback_score}/10", end="")
if feedback_score <= 3:
    print("  !! FEEDBACK LOOP BROKEN")
elif feedback_score <= 5:
    print("  ! DEGRADED FEEDBACK")
else:
    print("  (functional)")

# Compound risk
print(f"\n  {'─' * 56}")
print(f"  COMPOUND RISK ASSESSMENT")
print(f"  {'─' * 56}")
compound_risk = round((gap_score * 0.4 + (10 - feedback_score) * 0.4 + hidden_count * 0.2), 1)
compound_risk = min(compound_risk, 10)
print(f"  COMPOUND RISK:     {compound_risk}/10", end="")
if compound_risk >= 7:
    print("  !! CASCADING FAILURE LIKELY")
elif compound_risk >= 4:
    print("  ! COMPOUNDING PROBABLE")
else:
    print("  (manageable)")

# Narrative check
print(f"\n  {'─' * 56}")
print(f"  NARRATIVE vs REALITY CHECK")
print(f"  {'─' * 56}")
narrative_flags = []
if gap_score >= 5:
    narrative_flags.append("Deciders insulated from consequence — look for blame-shifting narratives")
if hidden_count >= 3:
    narrative_flags.append(f"{hidden_count} hidden variables — narrative likely oversimplified")
if feedback_score <= 4:
    narrative_flags.append("Broken feedback — error correction not possible through stated channels")
if isinstance(waste, list) and len(waste) >= 2:
    narrative_flags.append("Multiple unaccounted costs — true price is hidden")
if not narrative_flags:
    narrative_flags.append("Narrative appears reasonably aligned with energy flows")

for flag in narrative_flags:
    print(f"  >> {flag}")

print(f"\n{'=' * 60}")
print(f"  END ANALYSIS")
print(f"{'=' * 60}")

# Save option
print("\n  Save report to file? (y/n)")
if input("  > ").strip().lower() == "y":
    fname = f"thermo_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(fname, "w") as f:
        f.write(f"THERMODYNAMIC ANALYSIS REPORT\n")
        f.write(f"Subject: {subject}\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
        f.write(f"Energy In: {', '.join(energy_in) if isinstance(energy_in, list) else energy_in}\n")
        f.write(f"Energy Out: {', '.join(energy_out) if isinstance(energy_out, list) else energy_out}\n")
        f.write(f"Waste: {', '.join(waste) if isinstance(waste, list) else waste}\n")
        f.write(f"Value Captured By: {', '.join(who_benefits) if isinstance(who_benefits, list) else who_benefits}\n\n")
        f.write(f"Deciders: {', '.join(deciders) if isinstance(deciders, list) else deciders}\n")
        f.write(f"Consequence Bearers: {', '.join(consequence_bearers) if isinstance(consequence_bearers, list) else consequence_bearers}\n")
        f.write(f"Gap Score: {gap_score}/10\n")
        f.write(f"Feedback Delay: {delay_choice}\n")
        f.write(f"Hidden Variables: {hidden_count}\n")
        f.write(f"Feedback Score: {feedback_score}/10\n")
        f.write(f"Compound Risk: {compound_risk}/10\n\n")
        f.write(f"Narrative Flags:\n")
        for flag in narrative_flags:
            f.write(f"  - {flag}\n")
    print(f"  Saved to {fname}")

print("\n  Run another analysis? (y/n)")
if input("  > ").strip().lower() == "y":
    clear()
    run_analysis()
```

if **name** == “**main**”:
run_analysis()
