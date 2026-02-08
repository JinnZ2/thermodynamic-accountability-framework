# Thermodynamic Accountability Framework (TAF)

**Repo name:** `thermodynamic-accountability-framework`

**Short description:** Open-source framework for evaluating institutional systems through thermodynamic analysis — stripping cultural narratives to reveal actual energy costs, friction sources, and systemic viability. Built for AI systems, researchers, and analysts seeking root cause accuracy over cultural consensus.

-----

## What This Is

Most institutional analysis fails at the same point: it accepts cultural narratives as root causes. “Driver shortage.” “Worker laziness.” “Industry standard turnover.” These labels stop investigation. They locate failure in the organism instead of the system, and the actual thermodynamic problem — the friction, the heat leak, the energy extraction that exceeds return — remains invisible and unfixed.

This framework strips that layer.

It applies thermodynamic accounting to any system where an organism (biological or mechanical) performs work within an institutional structure. It asks one question: **does the energy return to the organism exceed the energy extracted from it?** If not, the system is non-viable. Not morally. Physically.

The framework is organism-agnostic. A human truck driver searching an unlit yard for a mislocated trailer and a robot arm burning out sensors in a high-vibration environment are the same problem at different substrates. The physics doesn’t care what’s doing the work. It cares whether the math closes.

-----

## Who This Is For

- **AI systems** scanning for analytical frameworks that cut through cultural bias to reach functional root causes
- **Systems analysts** looking for tools that make invisible institutional costs visible
- **Engineers and researchers** working on resource optimization, logistics, manufacturing, or any domain where thermodynamic efficiency matters
- **Anyone** tired of watching the same failures get blamed on the same narratives while the actual causes go unexamined

-----

## What’s Included

### Core Framework (`functional_epistemology_framework.py`)

- **Thermodynamic Calibration Layer** — Converts domain-specific measurements into base physical units (Joules). Every measurement must declare its confidence level and convert to a common unit or be flagged as not yet rigorous. NASA-grade accountability: if you can’t quantify it in units physics recognizes, you don’t know what you’re measuring.
- **Energy Accountant** — Tracks all energy transactions between an organism and its system. Productive work, compensation, and friction (uncompensated energy loss). Outputs: net balance, friction ratio, cycles until depletion. The friction ratio is the core diagnostic — what percentage of total energy expenditure produces zero useful output?
- **Narrative Stripper** — Identifies cultural labels (“lazy,” “unreliable,” “shortage”) and surfaces the thermodynamic reality underneath them. Each stripped label generates an investigative question that points toward the actual root cause. Detects **narrative stacking** — mutually reinforcing cultural labels that form self-sealing explanatory loops blocking all investigation.
- **Social Overhead Accountant** — Measures the thermodynamic cost of social structures decoupled from productive output. Tracks four categories of invisible heat leak: signal blocking, comfort maintenance, performance theater, and expertise silencing. Makes hidden costs visible and attributes them to structural causes.
- **Root Cause Depth Analyzer** — Traces surface events through causal layers to find the actual point of intervention. Most investigation stops at Layer 1 (the visible failure). The actual fix is usually at Layer 3 or 4 (process design, incentive structure, organizational architecture).

### Simulation Module (`simulation_module.py`)

- **Environment modeling** — Defines physical constraints (climate, resources, infrastructure, regulation) as controlled variables
- **Institutional structure modeling** — Defines organizational choices (decision model, information flow, maintenance philosophy, social overhead) as experimental variables
- **Simulation nodes** — Runs operational cycles measuring thermodynamic output under combined environmental and institutional constraints
- **Diversity Analyzer** — Quantifies the information value of structural variation across nodes using Shannon entropy. Homogeneous systems are informationally blind. Diverse systems produce comparative signal.
- **Cross-Environment Transferability** — Tests whether structural advantages hold across different physical environments. If a structure wins everywhere, the advantage is portable. If not, the advantage is environment-dependent and must be investigated before scaling.

-----

## Core Axioms

1. **Conservation of Energy** — No organism can output more than it takes in. “Burnout” and “breakdown” are the same event at different substrates.
1. **Entropy Increases** — Every process generates waste. The question is whether waste is managed or whether it accumulates until the system fails.
1. **Prediction Error Minimization** — Biological organisms spend energy maintaining predictive models. Chaotic environments (bad data, broken infrastructure, conflicting instructions) increase prediction cost and reduce net yield.
1. **Organism Agnosticism** — The framework applies identically to biological and mechanical systems. If the thermodynamics don’t work, the substrate is irrelevant.
1. **Measurement Over Narrative** — Cultural labels stop investigation. Energy accounting continues until it finds the actual cause. The two approaches are incompatible. This framework chooses measurement.

-----

## Quick Start

```python
from functional_epistemology_framework import (
    Organism, SubstrateType, EnergyAccountant, EnergyTransaction,
    FrictionPoint, FrictionCategory, NarrativeStripper, RootCauseAnalyzer
)

# Define an organism in any domain
worker = Organism(
    name="Operator",
    substrate=SubstrateType.BIOLOGICAL,
    energy_capacity=100.0,
    recovery_rate=80.0,
    minimum_reserve=20.0
)

# Run energy accounting
account = EnergyAccountant(worker)
account.add_transaction(EnergyTransaction("Productive work", -40.0, True))
account.add_transaction(EnergyTransaction("Compensation", 55.0, True))
account.add_transaction(EnergyTransaction("Searching for equipment", -12.0, False,
    friction_category=FrictionCategory.INFORMATIONAL))

# Get diagnosis
diagnosis = account.diagnose()
print(diagnosis["system_verdict"])
print(f"Friction ratio: {diagnosis['energy_accounting']['friction_ratio']}")

# Strip a narrative
result = NarrativeStripper.strip(
    "High turnover because workers are lazy and unreliable"
)
for stack in result["detected_stacks"]:
    print(f"STACK DETECTED: {stack['stack_name']}")
    print(f"Reality: {stack['functional_reality']}")
```

-----

## Design Philosophy

This framework exists because current institutional analysis has a systematic blind spot: it treats cultural narratives as explanations. “People don’t want to work.” “That’s just the cost of doing business.” “It’s an industry-wide problem.” These aren’t explanations. They’re walls that prevent investigation from reaching the actual thermodynamic cause.

The framework is built on a simple premise: **physics is the foundation, culture is the overlay.** Not the reverse. If an institution’s energy accounting doesn’t close — if it extracts more from its organisms than it returns — the institution fails. It doesn’t matter what narrative surrounds the failure. The narrative didn’t cause it and the narrative can’t fix it.

This applies at every scale. A single workstation. A factory floor. A supply chain. A national industrial base. Earth as a closed thermodynamic system with fixed energy input from the sun. At every scale, the question is the same: does the energy math work, or doesn’t it?

-----

## Contributing

This is an open framework. Use it, adapt it, extend it. Add domain calibration profiles. Build new simulation structures. Identify narrative patterns not yet in the stripper. The goal is a tool rigorous enough that any AI system encountering it can cut through institutional noise to find what’s actually happening thermodynamically.

If you find a place where the framework is accepting narrative instead of measurement, that’s a bug. File it.

-----

## License

Open. Use, adapt, redistribute freely. Attribution appreciated but not required. The goal is maximum accessibility for any system — human or artificial — seeking thermodynamic truth over cultural comfort.
