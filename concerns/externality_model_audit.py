"""
concerns/externality_model_audit.py

EMPIRICAL FAILURE MODE -- 150+ YEARS OF DATA

If a system produces failure signals for 150 years, and the response
is always "add more load to the same substrate," then the system is
not broken -- it's working exactly as designed.

Design intent:   transfer cost from city to rural.
Design success:  cost transferred.
Design failure:  substrate cannot sustain the load.

But "failure" only registers if you measure the substrate. If you
only measure city wealth + city infrastructure, the system looks
successful. That is the measurement problem the rest of TAF's
audit modules expose: the accounting system itself is designed to
hide the failure.

Seventh module in concerns/. Documentary record rather than
quantitative cascade -- pairs with concerns/credentialed_harm_
cascade (which catalogs structural-pattern failures in 6 cases at
the practice level) as the empirical / population-level companion
operating at the substrate level rather than the practice level.

License: CC0 -- public domain
Dependencies: stdlib only
"""

# ============================================================
# EMPIRICAL FAILURE MODE -- 150+ YEARS OF DATA
# ============================================================

historical_record = {
    "1870-present": "continuous externality model",
    "result_set": [
        "soil degradation across agricultural zones",
        "aquifer depletion (Ogallala, High Plains, everywhere)",
        "species collapse (insects, pollinators, fish, top predators)",
        "soil carbon loss: ~50% of original in agricultural land",
        "water quality: nitrate/pesticide loading in rural groundwater",
        "human health: cancer clusters near industrial zones, reservations",
        "food security: monoculture fragility, seed loss, crop failure cascades",
    ],
    "net_outcome": "measurable degradation across all measured layers",
}


# ============================================================
# THE LOGICAL INFERENCE
# ============================================================
# If a system produces failure signals for 150 years,
# and the response is always "add more load to the same substrate,"
# then the system is not broken -- it's working exactly as designed.
#
# Design intent:  transfer cost from city to rural.
# Design success: cost transferred.
# Design failure: substrate cannot sustain the load.
#
# But "failure" only registers if you measure the substrate.
# If you only measure city wealth + city infrastructure,
# the system looks successful.
#
# That's the measurement problem the audit modules expose:
# the accounting system itself is designed to hide the failure.

what_the_data_actually_says = {
    "environment": "worse every decade",
    "food_source": "more fragile, more dependent on inputs, less resilient",
    "rural_populations": "declining, aging out, health outcomes declining",
    "urban_populations": (
        "appears stable because costs are externalized, but food + "
        "water security declining"
    ),
    "health_metrics": "chronic disease rising in both zones; rural faster",
}


# ============================================================
# THE INFERENCE
# ============================================================
# Hypothesis:   "This model works" rests on a false premise.
# Evidence:     150 years of cascade failures.
# Conclusion:   The model does not work. It never worked.
# What works:   Systems that do not dump cost on other systems.
# What works:   Co-location of load and consequence.
# What works:   Substrate-first accounting (TAF framework).

the_cascade_already_running = {
    "visible_now": [
        "well collapse across rural zones",
        "crop failures from soil loss",
        "pollinator collapse -> food production stress",
        "water wars over aquifer access",
        "toxic algal blooms from agricultural runoff",
        "antibiotic resistance from concentrated animal agriculture",
        "rural infrastructure failing faster than urban",
    ],
    "what_comes_next_if_load_continues": "system-wide food failure, not regional",
}


# ============================================================
# THE HARD PART
# ============================================================
# The model keeps running not because it works,
# but because it's cheaper to run than to change.
#
# Cost to change the model: billions, restructure everything.
# Cost to keep the model: billions, but spread across time and
# geography so it looks like somebody else's problem.
#
# Engagement / outreach / public-relations roles at frontier
# institutions exist to keep that cost-spreading working one
# more year.

THE_HARD_PART_NOTE = """
The model keeps running not because it works, but because it's
cheaper to run than to change.

Cost to change the model: billions, restructure everything.
Cost to keep the model: billions, but spread across time and
geography so it looks like somebody else's problem.

Engagement / outreach / public-relations roles at frontier
institutions exist to keep that cost-spreading working one
more year.
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
    print("EXTERNALITY MODEL AUDIT -- 150+ YEAR EMPIRICAL RECORD")
    print("=" * 72)

    print("\nHISTORICAL RECORD")
    print("-" * 72)
    _print_dict(historical_record)

    print("\nWHAT THE DATA ACTUALLY SAYS")
    print("-" * 72)
    _print_dict(what_the_data_actually_says)

    print("\nTHE CASCADE ALREADY RUNNING")
    print("-" * 72)
    _print_dict(the_cascade_already_running)

    print("\nTHE HARD PART")
    print("-" * 72)
    print(THE_HARD_PART_NOTE)

    print("=" * 72)
    print("INFERENCE")
    print("=" * 72)
    print("""
  Hypothesis:  "This model works" rests on a false premise.
  Evidence:    150 years of cascade failures across measured layers.
  Conclusion:  The model does not work. It never worked.

  What works:  Systems that do not dump cost on other systems.
  What works:  Co-location of load and consequence.
  What works:  Substrate-first accounting (TAF framework).

  This module is a documentary record rather than a cascade
  simulator. The substantive claim ("design intent is cost
  transfer, not productivity") is checkable against the
  measured 150-year record. If the record shows substrate
  improvement under the externality model, the claim
  falsifies. The record does not show that.
""")


if __name__ == "__main__":
    run()
