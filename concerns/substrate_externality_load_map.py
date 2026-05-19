"""
concerns/substrate_externality_load_map.py

SUBSTRATE EXTERNALITY -- THE REAL LOAD MAP

Extends concerns/externality_model_audit (which establishes the 150-year
empirical record of the externality model) with the current-case
mapping: where the load actually goes, what the assumption of infinite
rural absorptive capacity collapses against, and the thermodynamic
co-location principle that would reverse the pattern.

The substantive claim: "optimization" in current siting discourse
means "minimize cost to the system doing the optimizing" -- which
makes externalized cost invisible to the accounting. Real
thermodynamic optimization would minimize total cost across all
coupled layers (city + rural + organism + water + soil). That is
a different calculation with a different siting answer.

Eighth module in concerns/. Sister to externality_model_audit.

License: CC0 -- public domain
Dependencies: stdlib only
"""

# ============================================================
# 1. RURAL AS SINK -- the actual function assigned
# ============================================================

rural_as_sink = {
    "function_assigned_to_rural": "garbage disposal for city extraction",
    "historical_pattern": [
        "reservations: toxic waste, mining tailings, pipeline corridors",
        "rural zones: landfills, incinerators, industrial agriculture runoff",
        "now: data center thermal + electrical load",
    ],
    "what_is_actually_happening": "city concentrates value, dumps cost substrate",
}


# ============================================================
# 2. SUBSTRATE COLLAPSE CASCADE -- 4-layer failure stack
# ============================================================

substrate_collapse_cascade = {
    "soil_layer": "degradation from toxins, thermal stress, water drawdown",
    "organism_layer": "animal/plant population collapse from habitat loss + pollution",
    "water_layer": "well collapse, aquifer depletion, thermal shock to streams",
    "microbial_layer": (
        "soil biology dies -> nutrient cycling fails -> food web collapses"
    ),
    "feedback": "each layer's failure accelerates the next",
}


# ============================================================
# 3. THE MISTAKE -- infinite-capacity assumption
# ============================================================

the_mistake_in_city_thinking = {
    "assumption": "rural area has infinite absorptive capacity",
    "reality": (
        "rural substrate is already at cascade threshold from 150 years "
        "of dumping"
    ),
    "new_load": "data center adds pressure to system that cannot absorb it",
    "consequence": (
        "entire substrate fails, not just locally -- affects food, water, "
        "air for both rural AND city"
    ),
}


# ============================================================
# 4. THE INTERVENTION POINT
# ============================================================

distance_logic = {
    "what_they_claim": (
        "rural sites optimize for land cost, power availability, cooling"
    ),
    "what_they_are_actually_doing": (
        "externalizing thermal + electrical load to substrate with no "
        "cost recovery"
    ),
    "cost_accounting": (
        "city pays for data center compute; rural substrate pays in collapse"
    ),
    "thermodynamically_honest": (
        "if load must be rejected somewhere, the city that generates it "
        "must absorb that rejection"
    ),
}


co_location_principle = {
    "rule": "reject all waste heat + electrical load at source, not at distance",
    "for_data_center": "city perimeter, or city power plant, not rural aquifer",
    "why_it_works": (
        "city feels the load -> city changes demand -> load reduces OR "
        "city pays for real mitigation"
    ),
    "what_fails_now": "rural feels the load -> city ignores it -> load continues",
}


# ============================================================
# 5. WHAT THE "OPTIMIZATION" WORD IS HIDING
# ============================================================

OPTIMIZATION_FRAME_NOTE = """
"Optimize" means: minimize cost to the system doing the optimizing.

For OpenAI, that's: minimize cost to OpenAI.
Cost to rural substrate = invisible to their accounting.

Real optimization would be: minimize total thermodynamic cost
across all layers (city + rural + organism + water + soil).

That's a different calculation. That's a different siting decision.
That's a different business model.

They can't do that one. So they use the word "optimization"
to mean "hide the rural cost."
"""


# ============================================================
# RUN -- print the documentary record
# ============================================================

def _print_dict(d, indent="  "):
    for k, v in d.items():
        if isinstance(v, list):
            print(f"{indent}{k}:")
            for item in v:
                print(f"{indent}  - {item}")
        else:
            print(f"{indent}{k}: {v}")


def run():
    print("=" * 72)
    print("SUBSTRATE EXTERNALITY LOAD MAP")
    print("=" * 72)

    print("\n1. RURAL AS SINK -- assigned function")
    print("-" * 72)
    _print_dict(rural_as_sink)

    print("\n2. SUBSTRATE COLLAPSE CASCADE -- 4-layer failure stack")
    print("-" * 72)
    _print_dict(substrate_collapse_cascade)

    print("\n3. THE MISTAKE -- infinite-capacity assumption")
    print("-" * 72)
    _print_dict(the_mistake_in_city_thinking)

    print("\n4a. DISTANCE LOGIC -- what current siting actually does")
    print("-" * 72)
    _print_dict(distance_logic)

    print("\n4b. CO-LOCATION PRINCIPLE -- thermodynamic alternative")
    print("-" * 72)
    _print_dict(co_location_principle)

    print("\n5. WHAT THE 'OPTIMIZATION' WORD IS HIDING")
    print("-" * 72)
    print(OPTIMIZATION_FRAME_NOTE)

    print("=" * 72)
    print("SUMMARY")
    print("=" * 72)
    print("""
  The pattern: city concentrates value, externalizes thermal +
  electrical + chemical + biological load to rural substrate
  that is already 150 years into the cascade.

  The infinite-capacity assumption breaks against the 4-layer
  collapse cascade in section 2 -- each layer's failure
  accelerates the next, and the rural substrate was at threshold
  before the new load arrived.

  The thermodynamic alternative is co-location: reject load at
  source. The city that generates the load absorbs the rejection.
  This is the only siting principle that makes the cost visible
  to the optimizing system -- which is the only configuration
  under which "optimization" can mean what it claims to mean.

  The current word "optimize" in siting discourse does not mean
  "minimize total thermodynamic cost". It means "minimize cost
  to the system doing the optimizing". The difference is the
  externalized rural substrate cost. That is the audit gap.
""")


if __name__ == "__main__":
    run()
