Fatigue Model


import math
from datetime import datetime

# --- FATIGUE MODULE ---
class FatigueModel:
    """
    Computes human fatigue as energy deficit across physical, cognitive,
    environmental, and system-hidden-variable dimensions.
    """

    def __init__(self, energy_input=100):
        self.energy_input = energy_input

    def hidden_var_multiplier(self, hidden_vars_count):
        if hidden_vars_count <= 0:
            return 1.0
        return 1 + 0.1 * hidden_vars_count ** 1.5  # nonlinear effect

    def automation_multiplier(self, automation_count, reliability=0.9):
        return 1 + automation_count * (1 - reliability) * 0.5

    def environment_multiplier(self, temp_celsius, wind_mps):
        temp_stress = max(0, (15 - temp_celsius) * 0.05)
        wind_stress = wind_mps * 0.02
        return 1 + temp_stress + wind_stress

    def compute(self,
                physical_load,
                cognitive_load,
                hidden_vars_count=0,
                automation_count=0,
                automation_reliability=0.9,
                temp_celsius=20,
                wind_mps=0):
        total_load = physical_load + cognitive_load
        total_load *= self.hidden_var_multiplier(hidden_vars_count)
        total_load *= self.automation_multiplier(automation_count, automation_reliability)
        total_load *= self.environment_multiplier(temp_celsius, wind_mps)

        deficit = total_load - self.energy_input
        fatigue_score = max(0, min(10, deficit / self.energy_input * 10))
        return round(fatigue_score, 1)

# --- INTEGRATION INTO ANALYSIS ---
def compute_compound_risk_with_fatigue(gap_score, feedback_score, hidden_count,
                                       physical_load, cognitive_load,
                                       automation_count, automation_reliability,
                                       temp_celsius, wind_mps):

    # Existing compound risk
    tail_risk = 10 * (1 - math.exp(-0.35 * hidden_count))
    baseline_risk = (gap_score * 0.5 + (10 - feedback_score) * 0.5)
    compound_risk = round(baseline_risk * (1 + tail_risk / 10), 1)
    compound_risk = min(compound_risk, 10)

    # Fatigue score
    fatigue_model = FatigueModel(energy_input=100)
    fatigue_score = fatigue_model.compute(
        physical_load=physical_load,
        cognitive_load=cognitive_load,
        hidden_vars_count=hidden_count,
        automation_count=automation_count,
        automation_reliability=automation_reliability,
        temp_celsius=temp_celsius,
        wind_mps=wind_mps
    )

    return compound_risk, fatigue_score

# --- EXAMPLE USAGE ---
if __name__ == "__main__":
    # Example scenario based on your lived system
    gap_score = 7               # decoupling of decision & consequence
    feedback_score = 4          # delayed/broken feedback
    hidden_count = 7            # hidden variables

    physical_load = 30          # effort to operate truck, compensate mechanical/road issues
    cognitive_load = 40         # attention, route planning, automation oversight
    automation_count = 3        # lane assist, adaptive cruise, alert systems
    automation_reliability = 0.85
    temp_celsius = -12
    wind_mps = 15

    compound_risk, fatigue_score = compute_compound_risk_with_fatigue(
        gap_score, feedback_score, hidden_count,
        physical_load, cognitive_load,
        automation_count, automation_reliability,
        temp_celsius, wind_mps
    )

    print(f"Compound System Risk: {compound_risk}/10")
    print(f"Embodied Fatigue Score: {fatigue_score}/10")


#!/usr/bin/env python3
“””
Thermodynamic Analysis Engine v2
With Integrated Operator Fatigue Model

Strip any decision, claim, or policy down to energy fundamentals.
Model the human energy cost that institutions never account for.
No ideology. No villains. Just flows, gaps, hidden variables, and real fatigue.

Usage: python thermo_engine.py
“””

import math
import json
from datetime import datetime

# ============================================================

# CORE SCORING FUNCTIONS

# ============================================================

def long_tail_risk(hidden_count):
“””
Hidden variables are the logarithmic factor for long tail risk.
Each additional hidden variable multiplies the space of possible
failure modes — combinatorial explosion of interaction effects.
Returns 0-10 scale where the curve goes nonlinear fast.
“””
if hidden_count == 0:
return 0.0
risk = 10 * (1 - math.exp(-0.35 * hidden_count))
return round(min(risk, 10), 1)

def score_feedback_integrity(delay, hidden_count, gap_score):
“””
Score how intact the feedback loop is.
0 = completely broken, 10 = tight feedback.
“””
score = 10.0
delay_penalties = {
“immediate”: 0, “days”: 1, “weeks”: 2,
“months”: 3, “years”: 5, “generational”: 8
}
score -= delay_penalties.get(delay, 4)
score -= min(hidden_count * 0.5, 3)
score -= gap_score * 0.3
return max(round(score, 1), 0)

# ============================================================

# OPERATOR FATIGUE MODEL

# ============================================================

class FatigueModel:
“””
Compute real-world human fatigue as a function of:
- Physical load
- Cognitive load
- Environmental stress
- Hidden variables / system inefficiencies
- Automation monitoring burden
- Energy input (sleep, food, thermal comfort)

```
This models what HOS regulations miss: the ACTUAL energy
expenditure of operating in complex environments, not just
hours awake.
"""

def __init__(self, energy_input=100):
    self.energy_input = energy_input

def compute_hidden_variable_multiplier(self, hidden_vars_count):
    """Hidden variables increase energy demand nonlinearly."""
    if hidden_vars_count <= 0:
        return 1.0
    return 1 + 0.1 * hidden_vars_count ** 1.5

def compute_automation_load(self, automation_count, reliability=0.9):
    """
    Each automation system adds cognitive load proportional to
    unreliability. Unreliable automation isn't reducing load —
    it's adding monitoring burden.
    """
    return 1 + automation_count * (1 - reliability) * 0.5

def compute_environment_multiplier(self, temp_celsius, wind_mps):
    """Cold and wind increase physical and cognitive energy expenditure."""
    temp_stress = max(0, (15 - temp_celsius) * 0.05)
    wind_stress = wind_mps * 0.02
    return 1 + temp_stress + wind_stress

def compute_fatigue_score(self, physical_load, cognitive_load,
                           hidden_vars_count=0, automation_count=0,
                           automation_reliability=0.9,
                           temp_celsius=20, wind_mps=0):
    """Returns fatigue score on 0-10 scale with breakdown."""
    total_load = physical_load + cognitive_load

    hv_mult = self.compute_hidden_variable_multiplier(hidden_vars_count)
    auto_mult = self.compute_automation_load(automation_count, automation_reliability)
    env_mult = self.compute_environment_multiplier(temp_celsius, wind_mps)

    adjusted_load = total_load * hv_mult * auto_mult * env_mult
    deficit = adjusted_load - self.energy_input
    fatigue_score = max(0, min(10, deficit / self.energy_input * 10))

    return {
        "fatigue_score": round(fatigue_score, 1),
        "base_load": total_load,
        "adjusted_load": round(adjusted_load, 1),
        "energy_input": self.energy_input,
        "deficit": round(deficit, 1),
        "multipliers": {
            "hidden_variables": round(hv_mult, 2),
            "automation": round(auto_mult, 2),
            "environment": round(env_mult, 2),
            "combined": round(hv_mult * auto_mult * env_mult, 2)
        }
    }
```

# ============================================================

# INPUT HELPERS

# ============================================================

def clear():
print(”\n” * 2)

def header():
print(”=” * 60)
print(”  THERMODYNAMIC ANALYSIS ENGINE v2”)
print(”  With Operator Fatigue Model”)
print(”  No narratives. Just energy flows.”)
print(”=” * 60)

def get_input(prompt, required=True, allow_list=False):
while True:
val = input(f”\n  {prompt}\n  > “).strip()
if val or not required:
if allow_list and val:
return [v.strip() for v in val.split(”,”) if v.strip()]
return val if val else “Unknown / Not stated”
print(”  (Required field - press enter to mark as Unknown)”)
return “Unknown / Not stated”

def get_number(prompt, low, high):
while True:
val = input(f”  {prompt} [{low}-{high}]: “).strip()
try:
val = float(val)
if low <= val <= high:
return val
print(f”  Enter a number {low}-{high}”)
except ValueError:
print(f”  Enter a number {low}-{high}”)

def get_yes_no(prompt):
val = input(f”\n  {prompt} (y/n): “).strip().lower()
return val == “y”

# ============================================================

# MAIN ANALYSIS — SYSTEM / DECISION

# ============================================================

def run_system_analysis():
“”“Thermodynamic analysis of any decision, claim, or policy.”””
print(”\n  Paste a decision, claim, policy, or proposal.”)
print(”  (Can be a sentence, paragraph, headline, whatever.)”)
subject = get_input(“SUBJECT OF ANALYSIS:”)

```
print("\n" + "-" * 60)
print("  ENERGY FLOW MAPPING")
print("-" * 60)

energy_in = get_input(
    "What energy/resources go IN?\n"
    "  (money, labor, fuel, materials, attention, time...)\n"
    "  Comma-separated:", allow_list=True)

energy_out = get_input(
    "What energy/resources come OUT?\n"
    "  (products, services, waste, heat, pollution, debt...)\n"
    "  Comma-separated:", allow_list=True)

who_benefits = get_input(
    "Who captures the OUTPUT value?\n"
    "  Comma-separated:", allow_list=True)

waste = get_input(
    "What is the WASTE / unaccounted cost?\n"
    "  (externalities, deferred maintenance, health costs,\n"
    "   environmental damage, human fatigue...)\n"
    "  Comma-separated:", allow_list=True)

print("\n" + "-" * 60)
print("  DECISION STRUCTURE")
print("-" * 60)

deciders = get_input(
    "Who DECIDES? (individuals, roles, institutions)\n"
    "  Comma-separated:", allow_list=True)

consequence_bearers = get_input(
    "Who ABSORBS CONSEQUENCE if it goes wrong?\n"
    "  Comma-separated:", allow_list=True)

# Gap assessment
print("\n  --- DECISION-CONSEQUENCE GAP ---")
d_str = ", ".join(deciders) if isinstance(deciders, list) else deciders
c_str = ", ".join(consequence_bearers) if isinstance(consequence_bearers, list) else consequence_bearers
print(f"  Who decides:           {d_str}")
print(f"  Who bears consequence:  {c_str}")
print("\n  How much overlap between deciders and consequence bearers?")
print("  0 = complete overlap (same people)")
print("  10 = total separation (no overlap)")
gap_score = get_number("Gap score", 0, 10)

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
    "  Comma-separated:", allow_list=True)
hidden_count = len(hidden) if isinstance(hidden, list) else 0
```




import math

class FatigueModel:
    """
    Compute real-world human fatigue as a function of:
    - Physical load
    - Cognitive load
    - Environmental stress
    - Hidden variables/system inefficiencies
    - Energy input (sleep, food, thermal comfort)
    """

    def __init__(self, energy_input=100):
        """
        energy_input: baseline human energy available (arbitrary units)
        """
        self.energy_input = energy_input  # baseline replenished energy

    def compute_hidden_variable_multiplier(self, hidden_vars_count):
        """
        Hidden variables increase energy demand nonlinearly (logarithmic multiplier)
        """
        if hidden_vars_count <= 0:
            return 1.0
        return 1 + 0.1 * hidden_vars_count ** 1.5  # adjust exponent to tune sensitivity

    def compute_automation_load(self, automation_count, reliability=0.9):
        """
        Each automation system adds cognitive load proportional to unreliability
        - reliability: fraction of system you can trust (0-1)
        """
        load_multiplier = 1 + automation_count * (1 - reliability) * 0.5
        return load_multiplier

    def compute_environment_multiplier(self, temp_celsius, wind_mps):
        """
        Environmental stress multiplier:
        - Cold and wind increase physical and cognitive energy expenditure
        """
        temp_stress = max(0, (15 - temp_celsius) * 0.05)  # colder = more stress
        wind_stress = wind_mps * 0.02  # each m/s adds extra load
        return 1 + temp_stress + wind_stress

    def compute_fatigue_score(
        self,
        physical_load,
        cognitive_load,
        hidden_vars_count=0,
        automation_count=0,
        automation_reliability=0.9,
        temp_celsius=20,
        wind_mps=0,
    ):
        """
        Returns a fatigue score on 0-10 scale
        """
        # Base total energy expenditure
        total_load = physical_load + cognitive_load

        # Apply multipliers
        hv_multiplier = self.compute_hidden_variable_multiplier(hidden_vars_count)
        auto_multiplier = self.compute_automation_load(automation_count, automation_reliability)
        env_multiplier = self.compute_environment_multiplier(temp_celsius, wind_mps)

        total_load *= hv_multiplier * auto_multiplier * env_multiplier

        # Energy deficit
        deficit = total_load - self.energy_input
        fatigue_score = max(0, min(10, deficit / self.energy_input * 10))  # scale 0-10

        return round(fatigue_score, 1)

# --- Example usage ---
if __name__ == "__main__":
    fatigue = FatigueModel(energy_input=100)

    score = fatigue.compute_fatigue_score(
        physical_load=30,         # arbitrary units for truck driving effort
        cognitive_load=40,        # mental load from route planning, monitoring automation, etc
        hidden_vars_count=7,      # snow, ice, infrastructure decay, unpredictable human behavior, procedural changes, service changes, info gaps
        automation_count=3,       # lane assist, cruise, braking alerts
        automation_reliability=0.85,
        temp_celsius=-12,
        wind_mps=15
    )

    print(f"Predicted fatigue score: {score}/10")


import math

# --- EXTENDED FATIGUE & SYSTEM COLLAPSE MODULE ---
class HumanSystemModel:
    """
    Models human energy ledger, fatigue, and system collapse thresholds
    based on physical/cognitive load, hidden variables, environmental stress,
    automation overhead, and energy input.
    """

    def __init__(self, energy_input=100):
        self.energy_input = energy_input

    # Hidden variable multiplier (nonlinear)
    def hidden_var_multiplier(self, hidden_count):
        if hidden_count <= 0:
            return 1.0
        return 1 + 0.1 * hidden_count ** 1.5

    # Automation cognitive load
    def automation_multiplier(self, automation_count, reliability=0.9):
        return 1 + automation_count * (1 - reliability) * 0.5

    # Environmental stress
    def environment_multiplier(self, temp_celsius, wind_mps):
        temp_stress = max(0, (15 - temp_celsius) * 0.05)
        wind_stress = wind_mps * 0.02
        return 1 + temp_stress + wind_stress

    # Compute fatigue score
    def compute_fatigue(self, physical_load, cognitive_load,
                        hidden_count=0, automation_count=0, automation_reliability=0.9,
                        temp_celsius=20, wind_mps=0):
        total_load = physical_load + cognitive_load
        total_load *= self.hidden_var_multiplier(hidden_count)
        total_load *= self.automation_multiplier(automation_count, automation_reliability)
        total_load *= self.environment_multiplier(temp_celsius, wind_mps)

        deficit = total_load - self.energy_input
        fatigue_score = max(0, min(10, deficit / self.energy_input * 10))
        return round(fatigue_score, 1), total_load

    # Compute human-system collapse risk
    def compute_collapse_risk(self, physical_load, cognitive_load,
                              hidden_count=0, automation_count=0, automation_reliability=0.9,
                              temp_celsius=20, wind_mps=0):
        fatigue_score, total_load = self.compute_fatigue(
            physical_load, cognitive_load,
            hidden_count, automation_count, automation_reliability,
            temp_celsius, wind_mps
        )

        # Define thresholds
        # Productivity collapse if load > 120% of energy_input
        # Safety collapse if load > 140% of energy_input
        # Health collapse if load > 160% of energy_input
        prod_threshold = 1.2 * self.energy_input
        safety_threshold = 1.4 * self.energy_input
        health_threshold = 1.6 * self.energy_input

        collapse_flags = []
        if total_load >= health_threshold:
            collapse_flags.append("!! HUMAN HEALTH COLLAPSE IMMINENT")
        elif total_load >= safety_threshold:
            collapse_flags.append("!! SAFETY SYSTEM BREAKDOWN LIKELY")
        elif total_load >= prod_threshold:
            collapse_flags.append("! PRODUCTIVITY DEGRADATION")
        else:
            collapse_flags.append("(System within sustainable limits)")

        return fatigue_score, total_load, collapse_flags

# --- EXAMPLE USAGE ---
if __name__ == "__main__":
    human_system = HumanSystemModel(energy_input=100)

    # Scenario based on your real-world hidden-variable-heavy system
    physical_load = 30       # truck operation, compensating for mechanical/road issues
    cognitive_load = 40      # attention, route planning, automation oversight
    hidden_count = 7         # snow, ice, infrastructure decay, unpredictable actors, procedural changes, info gaps
    automation_count = 3     # lane assist, adaptive cruise, alerts
    automation_reliability = 0.85
    temp_celsius = -12
    wind_mps = 15

    fatigue_score, total_load, collapse_flags = human_system.compute_collapse_risk(
        physical_load, cognitive_load,
        hidden_count, automation_count, automation_reliability,
        temp_celsius, wind_mps
    )

    print(f"Predicted Fatigue Score: {fatigue_score}/10")
    print(f"Total Energy Load: {round(total_load,1)} units (Energy Input: {human_system.energy_input})")
    for flag in collapse_flags:
        print(flag)
