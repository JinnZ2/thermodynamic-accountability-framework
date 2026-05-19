"""
concerns/assessment_first_principle.py

ASSESSMENT-FIRST PRINCIPLE -- THE MINIMAL REQUIREMENT

The operational consequence of concerns/cascade_failure_rural_
degradation: if recovery rate is 65x slower than load rate, and
recovery cannot run concurrently with load, then the only
responsible action while baseline capacity is unmeasured is to
stop adding load.

Not forever. Long enough to measure.

Eleventh module in concerns/. Operational/policy companion to the
empirical and cascade modules. Sister to:
- cascade_failure_rural_degradation (the 65:1 ratio)
- externality_model_audit (150-year record)
- substrate_externality_load_map (structural argument)
- institutional_bottleneck_audit (attribution formula when load
  continues despite known incapacity)

Sources for the empirical observations below: substrate-primary
direct observation from the user (northern Wisconsin forests,
deer population artificial-management requirement, insect travel
distance) plus published soil-recovery literature.

License: CC0 -- public domain
Dependencies: stdlib only
"""

# ============================================================
# 1. WHAT NEEDS TO HAPPEN NOW
# ============================================================

what_needs_to_happen_now = {
    "action": "moratorium on new rural development",
    "duration": "until baseline measurements exist",
    "purpose": "determine what each region can actually sustain",
    "not_forever": "but long enough to know the capacity",
}


# ============================================================
# 2. WHAT WE KNOW RIGHT NOW
# ============================================================

what_we_know_right_now = {
    "northern_wisconsin_forests": (
        "still recovering from 1890s logging; 130+ years and not recovered"
    ),
    "soil_recovery_rate": (
        "varies by region; some fast, some slow, some permanent loss"
    ),
    "deer_population": (
        "must be managed because forest structure collapsed; artificial "
        "intervention required"
    ),
    "frog_populations": "timing altered, numbers down, migrations disrupted",
    "wetland_state": "corroded, degraded, losing function",
    "insect_travel_distance": (
        "170-mile drive without insect strikes -- system-level collapse signal"
    ),
    "what_this_means": (
        "we do not have baseline data on what recovery looks like or how "
        "long it takes"
    ),
}


# ============================================================
# 3. THE INFORMATION GAP
# ============================================================

the_information_gap = {
    "missing": [
        "sustainable load capacity per watershed/region",
        "recovery timeline for degraded substrates",
        "threshold data for permanent vs. reversible damage",
        "which regions can regenerate, which cannot",
    ],
    "consequence_of_gap": (
        "every new load is a blind guess that might lock in irreversible "
        "collapse"
    ),
}


# ============================================================
# 4. WHY THE WAIT IS NOT EXTREME
# ============================================================

why_wait_is_not_extreme = {
    "it_is_conservative": (
        "pause to measure before crossing irreversibility threshold"
    ),
    "it_is_scientific": (
        "gather data before making decisions with 150-year consequences"
    ),
    "it_is_accountable": "know your capacity before you build",
    "it_is_the_minimum": (
        "if you do not know capacity, you cannot responsibly add load"
    ),
}


# ============================================================
# 5. WHAT HAPPENS IF YOU DO NOT WAIT
# ============================================================

what_happens_if_you_dont_wait = {
    "best_case": "you guess right by accident; waste time and money",
    "worst_case": (
        "you lock in permanent collapse across multiple regions simultaneously"
    ),
    "most_likely": (
        "you cross thresholds you do not see until it is too late, then "
        "cascade accelerates"
    ),
}


# ============================================================
# THE PRINCIPLE
# ============================================================

PRINCIPLE_NOTE = """
This is the only rational action at this point. The capacity is
not known. The recovery timeline is not known. Which damage is
permanent is not known. So load stops being added, and measurement
begins.

Not forever. Until there is data.

This is not an extreme position. It is the minimum responsible
action when:
  - the load rate is 65x faster than the recovery rate
  - recovery cannot run concurrently with load
  - threshold crossings reduce reversibility windows
  - the consequence of a wrong guess is multi-generational
"""


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
    print("ASSESSMENT-FIRST PRINCIPLE -- THE MINIMAL REQUIREMENT")
    print("=" * 72)

    print("\n1. WHAT NEEDS TO HAPPEN NOW")
    print("-" * 72)
    _print_dict(what_needs_to_happen_now)

    print("\n2. WHAT WE KNOW RIGHT NOW")
    print("-" * 72)
    _print_dict(what_we_know_right_now)

    print("\n3. THE INFORMATION GAP")
    print("-" * 72)
    _print_dict(the_information_gap)

    print("\n4. WHY THE WAIT IS NOT EXTREME")
    print("-" * 72)
    _print_dict(why_wait_is_not_extreme)

    print("\n5. WHAT HAPPENS IF YOU DO NOT WAIT")
    print("-" * 72)
    _print_dict(what_happens_if_you_dont_wait)

    print("\nTHE PRINCIPLE")
    print("=" * 72)
    print(PRINCIPLE_NOTE)


if __name__ == "__main__":
    run()
