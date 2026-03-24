#!/usr/bin/env python3
"""
Thermodynamic Automation Assessment Engine v2
Maps hidden variables, human energy, and automation as dynamic entropy.
Calculates fatigue, collapse risk, and system stress numerically.
"""

import math
from datetime import datetime

# -----------------------------
# Utility functions
# -----------------------------
def clear():
    print("\n" * 2)

def header(title="THERMODYNAMIC AUTOMATION ASSESSMENT"):
    print("=" * 60)
    print(f"  {title}")
    print("  Modeling humans, hidden variables, and automation entropy")
    print("=" * 60)

def get_input(prompt, required=True, allow_list=False):
    """Get user input, optionally as a list"""
    while True:
        val = input(f"\n  {prompt}\n  > ").strip()
        if val or not required:
            if allow_list and val:
                return [v.strip() for v in val.split(",") if v.strip()]
            return val if val else "Unknown / Not stated"
        print("  (Required field - press enter to mark as Unknown)")

# -----------------------------
# Core functions
# -----------------------------
def calculate_hidden_entropy(hidden_vars):
    """
    Maps hidden variables to a numeric entropy load (0-10 per variable)
    Uses log scaling for combinatorial effects.
    """
    count = len(hidden_vars) if isinstance(hidden_vars, list) else 0
    if count == 0:
        return 0.0
    return round(10 * (1 - math.exp(-0.35 * count)), 1)

def automation_entropy(automation_modules, hidden_vars, environment_factor=1.0):
    """
    Automation can reduce load (negative) or increase it (positive) depending on complexity and hidden variables.
    environment_factor: multiplier for environmental stress (1.0 = normal, >1 = extreme)
    """
    if not automation_modules:
        return 0.0
    base_entropy = 0
    for module in automation_modules:
        # default assumption: each module reduces load by 0-3, but edge complexity flips it
        # User provides 'impact' for each module: "helpful" or "complex"
        impact = module.get("impact", "helpful")
        if impact == "helpful":
            delta = -2  # reduces load
        else:
            delta = 3 * environment_factor  # adds entropy under stress
        base_entropy += delta
    return base_entropy

def total_human_load(base_human_energy, hidden_vars, automation_modules, environment_factor=1.0):
    hidden_load = calculate_hidden_entropy(hidden_vars)
    auto_load = automation_entropy(automation_modules, hidden_vars, environment_factor)
    net_load = base_human_energy + hidden_load + auto_load
    return max(net_load, 0)

def fatigue_score(net_load, energy_capacity=10.0):
    """
    Maps net human load to fatigue score (0=fully rested, 10=critical overload)
    """
    score = (net_load / energy_capacity) * 10
    return min(round(score, 1), 10)

def collapse_risk(fatigue, hidden_entropy):
    """
    Maps fatigue + hidden variable load to a 0-10 collapse risk
    """
    baseline = fatigue * 0.5 + hidden_entropy * 0.5
    return min(round(baseline, 1), 10)

# -----------------------------
# Example run
# -----------------------------
def run_example():
    header()

    # Base human energy (arbitrary 0-10 scale)
    base_human_energy = float(get_input("Base human energy for shift (0-10):"))

    # Hidden variables
    hidden_vars = get_input(
        "List hidden variables to account for (comma-separated):", allow_list=True
    )

    # Automation modules
    automation_modules = []
    while True:
        add_auto = get_input("Add automation module? (y/n):", required=True)
        if add_auto.lower() != "y":
            break
        name = get_input("Module name:")
        impact = get_input("Impact on load? (helpful / complex):")
        automation_modules.append({"name": name, "impact": impact})

    # Environment factor (1=normal, >1=extreme)
    environment_factor = float(get_input("Environment stress multiplier (1=normal):"))

    # Compute
    hidden_entropy = calculate_hidden_entropy(hidden_vars)
    net_load = total_human_load(base_human_energy, hidden_vars, automation_modules, environment_factor)
    fatigue = fatigue_score(net_load)
    risk = collapse_risk(fatigue, hidden_entropy)

    # Report
    print("\n" + "-"*60)
    print("THERMODYNAMIC AUTOMATION REPORT")
    print("-"*60)
    print(f"Hidden Variables Count: {len(hidden_vars)}")
    if hidden_vars:
        for v in hidden_vars:
            print(f"  - {v}")
    print(f"Net Human Load: {net_load}/10")
    print(f"Estimated Fatigue Score: {fatigue}/10")
    print(f"Estimated Collapse Risk: {risk}/10")
    print("-"*60)

if __name__ == "__main__":
    run_example()
