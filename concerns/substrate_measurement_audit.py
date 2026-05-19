"""
concerns/substrate_measurement_audit.py

METROLOGY PROBLEM -- WRONG MEASUREMENT SYSTEM

The instrument-level companion to concerns/assessment_first_principle.
That module says: stop adding load until baseline measurements exist.
This module specifies WHAT to measure and why the current instruments
(property value, GDP, development density) are wrong for the question
being asked.

The substantive claim: financial-extraction metrics are not silent on
substrate health, they are CORRELATED INVERSELY with substrate health
in the cases that matter. Property value rises while soil carbon
falls. GDP grows while aquifers deplete. Development density tracks
extraction efficiency, not sustainability. Using financial instruments
to assess substrate capacity is like using a thermometer to measure
voltage -- the instrument reports a number, but it is the wrong
number.

Twelfth module in concerns/. Sister to:
- assessment_first_principle    (what to do: stop and measure)
- cascade_failure_rural_degradation (the timing constraints)
- externality_model_audit       (the 150-year record)
- substrate_externality_load_map (the structural argument)

Distinct from metrology/ folder modules, which audit existing
measurement systems for substrate corruption. This module specifies
which substrate measurements should be taken for the load-capacity
question specifically.

License: CC0 -- public domain
Dependencies: stdlib only
"""

# ============================================================
# 1. WHAT IS BEING MEASURED -- the current instrument
# ============================================================

what_is_being_measured = {
    "current_metric": "property value, GDP, development density",
    "what_these_measure": "financial extraction, not system health",
    "consequence": "optimizing for property value destroys substrate",
    "result": "system looks 'successful' while collapsing",
}


# ============================================================
# 2. WHAT NEEDS TO BE MEASURED -- the substrate instruments
# ============================================================

what_needs_to_be_measured = {
    "soil_carbon": (
        "g/kg; trajectory toward or away from critical threshold"
    ),
    "aquifer_recharge_rate": "inches per year vs. withdrawal rate",
    "pollinator_populations": (
        "species count, migration timing, genetic diversity"
    ),
    "insect_biomass": (
        "total insect density per area; baseline for cascade detection"
    ),
    "frog_breeding_phenology": "timing shifts as signal of system stress",
    "wetland_function": (
        "water infiltration, nutrient cycling, habitat provision"
    ),
    "microbial_diversity": "soil biology as leading indicator of collapse",
    "forest_structure": (
        "age distribution, regeneration capacity, deer population pressure"
    ),
    "watershed_health": (
        "sediment load, temperature, species diversity in waterways"
    ),
}


# ============================================================
# 3. WHY THIS MATTERS -- the instrument-vs-question gap
# ============================================================

why_this_matters = {
    "property_value": (
        "optimizes for extraction; tells you nothing about capacity"
    ),
    "substrate_metrics": (
        "tell you if the system can sustain load or if it is failing"
    ),
    "the_difference": "one measures money; the other measures survival",
}


# ============================================================
# 4. THE METROLOGY SHIFT REQUIRED
# ============================================================

the_metrology_shift_required = {
    "from": "financial accounting (what extracts well)",
    "to": "thermodynamic accounting (what sustains)",
    "tools": (
        "satellite imagery, soil testing, population surveys, hydrological "
        "modeling"
    ),
    "baseline": "establish now what 'healthy' looks like in each region",
    "trajectory": (
        "measure whether load is sustainable or pushing toward collapse"
    ),
}


# ============================================================
# 5. WHAT RECOVERY ASSESSMENT REQUIRES
# ============================================================

what_recovery_assessment_requires = {
    "pause_on_new_load": "so you can measure baseline without noise",
    "regional_surveys": "soil, water, insect, frog, microbial populations",
    "timeline_modeling": (
        "how long recovery takes given different load scenarios"
    ),
    "threshold_mapping": (
        "where is each region relative to irreversibility point"
    ),
    "capacity_calculation": "sustainable load per watershed/ecosystem type",
    "after_assessment": (
        "then you know what can be rebuilt, what cannot, what is permanent loss"
    ),
}


# ============================================================
# 6. THE HONEST ANSWER
# ============================================================

the_honest_answer = {
    "do_we_know_if_regions_recover": "no, not yet",
    "can_we_know": "only if we stop adding load and measure",
    "what_happens_if_we_dont_measure": (
        "we cross irreversibility thresholds blind"
    ),
    "what_happens_if_we_do_measure": (
        "we have data to make rational decisions about what is possible"
    ),
}


# ============================================================
# RUN
# ============================================================

def _print_dict(d, indent="  "):
    for k, v in d.items():
        if isinstance(v, list):
            print(f"{indent}{k}:")
            for item in v:
                print(f"{indent}  - {item}")
        elif isinstance(v, dict):
            print(f"{indent}{k}:")
            _print_dict(v, indent + "  ")
        else:
            print(f"{indent}{k}: {v}")


def run():
    print("=" * 72)
    print("SUBSTRATE MEASUREMENT AUDIT -- METROLOGY PROBLEM")
    print("=" * 72)

    print("\n1. WHAT IS BEING MEASURED -- the current instrument")
    print("-" * 72)
    _print_dict(what_is_being_measured)

    print("\n2. WHAT NEEDS TO BE MEASURED -- substrate instruments")
    print("-" * 72)
    _print_dict(what_needs_to_be_measured)

    print("\n3. WHY THIS MATTERS")
    print("-" * 72)
    _print_dict(why_this_matters)

    print("\n4. THE METROLOGY SHIFT REQUIRED")
    print("-" * 72)
    _print_dict(the_metrology_shift_required)

    print("\n5. WHAT RECOVERY ASSESSMENT REQUIRES")
    print("-" * 72)
    _print_dict(what_recovery_assessment_requires)

    print("\n6. THE HONEST ANSWER")
    print("-" * 72)
    _print_dict(the_honest_answer)

    print()
    print("=" * 72)
    print("SUMMARY")
    print("=" * 72)
    print("""
  Financial-extraction metrics (property value, GDP, density) and
  substrate-capacity metrics (soil carbon, aquifer recharge, insect
  biomass, microbial diversity) are not just different. They are
  often INVERSELY correlated -- the case under audit makes the
  divergence visible.

  Optimizing for the financial instrument while ignoring the
  substrate instrument produces a system that LOOKS successful by
  the metric it tracks while collapsing on the axis it does not.
  This is not measurement error. It is measurement substitution:
  the wrong instrument is being used to answer the question, and
  the answer it returns is being treated as if it answered the
  right one.

  The shift required is operational, not philosophical. The tools
  exist (satellite imagery, soil testing, population surveys,
  hydrological modeling). The data can be collected. The baseline
  can be established. What is missing is the institutional
  commitment to measure the substrate before adding more load to
  it.

  The honest answer to "can these regions recover?" is: not known
  yet, and not knowable while load continues to mask the signal.
""")


if __name__ == "__main__":
    run()
