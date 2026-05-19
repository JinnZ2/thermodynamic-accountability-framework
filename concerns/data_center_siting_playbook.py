"""
concerns/data_center_siting_playbook.py

DATA CENTER SITING PLAYBOOK -- REAL-TIME ENERGY-FLOW MAP

Documents the data-center siting pattern: physical load hitting
substrate, siting strategy targeting limited-enforcement zones,
local-government resistance firing back, and corporate counter-
move via persuasion-budget rather than physics-budget.

Empirical current-case companion to:
- concerns/externality_model_audit (150-year historical record)
- concerns/substrate_externality_load_map (structural argument)

Where those two establish the pattern and the principle, this
module documents the specific 2025-2026 case with sourcing so
the claims are verifiable.

Sources (consulted May 2026): Texas Tribune, AP, E&E News /
Politico, Business Insider / Yahoo Finance, Tom's Hardware,
Good Jobs First, MultiState, Built In, U.S. News, OpenAI's
own "Building the compute infrastructure" infrastructure post.

Ninth module in concerns/.

License: CC0 -- public domain
Dependencies: stdlib only
"""

# ============================================================
# LAYER 1 -- physical constraints that have already triggered
# ============================================================

physical_load = {
    "grid": (
        "rate spikes; one analysis: monthly power prices up to 267% higher "
        "in some areas between 2020 and 2025. "
        "(source: builtin.com / states-push-data-center-moratoriums)"
    ),
    "water": (
        "large water + electricity draw flagged as quality-of-life threat. "
        "(source: usnews.com 2026-05-13 / texas-county-pauses-data-center-"
        "construction-in-rural-areas-for-a-year)"
    ),
    "noise": (
        "noise pollution cited as public health concern in Hill County vote. "
        "(source: usnews.com 2026-05-13)"
    ),
    "reliability": (
        "NERC 2025: East Coast, Midwest, Pacific NW face energy shortfalls "
        "and more frequent outages as soon as 2028. "
        "(source: builtin.com / states-push-data-center-moratoriums)"
    ),
    "build_time_collapse": (
        "what used to take 19 days to build could now take several years. "
        "(source: tomshardware.com / texas-county-passes-data-center-"
        "moratorium-for-a-year)"
    ),
}


# ============================================================
# LAYER 2 -- siting strategy (where the load gets dumped)
# ============================================================

siting_logic = {
    "target": "rural, unincorporated, limited code/enforcement",
    "quote": (
        "'The data center folks have found a sweet spot in the state that "
        "has limited regulations, limited enforcement, limited code, and "
        "they're coming faster than we can keep up with' "
        "-- Commissioner Jim Holcomb. "
        "(source: usnews.com 2026-05-13)"
    ),
    "scale": (
        "Hill County: as many as eight data centers planned, many with "
        "their own power plants. "
        "(source: eenews.net / texas-county-passes-1-year-data-center-"
        "construction-ban)"
    ),
    "the_play": "concentrate load where legal capacity to object is thinnest",
}


# ============================================================
# LAYER 3 -- the resistance (sensors firing back)
# ============================================================

resistance_geography = {
    "local_wins": {
        "Hill County, TX": (
            "3-2 vote, one-year moratorium on data centers in unincorporated "
            "areas. (source: usnews.com 2026-05-13)"
        ),
        "national_pattern": (
            "dozens of municipalities have moved ahead with local construction "
            "pauses; center of gravity shifting toward local government action. "
            "(source: multistate.us / state-data-center-policy-101)"
        ),
    },
    "state_bills_filed_2026": [
        # from Good Jobs First + MultiState + Built In
        "Oklahoma SB 1488 -- moratorium until Nov 2029 on 100 MW+",
        "New York S9144 / A10141 -- up to 3-yr halt, PSC rate study",
        "Michigan HB 5594 -- prohibits approval through April 2027",
        "Vermont S.205 -- AI data center moratorium pending framework",
        "South Dakota SB 232 / HB 1301 -- hyperscale pause",
        "Kansas SB 531 -- targets water-constrained counties",
        "Missouri HB 3390 -- bans in ag/residential/conservation zones",
        "Maine LD 307 -- passed legislature, vetoed by Gov Mills",
    ],
    "ballot_route_opening": (
        "Ohio voters may decide on statewide initiative to ban data centers "
        "requiring 25 MW or more, potential precedent for 23 ballot-measure "
        "states. (source: multistate.us 2026-05-07 / voters-target-data-"
        "centers-with-local-and-statewide-ballot-measures)"
    ),
    "state_level_status": (
        "state moratorium bills introduced but facing resistance; most "
        "failing legislative deadlines. "
        "(source: multistate.us 2026-03-13 / local-data-center-regulations-"
        "gain-ground-as-state-bills-falter)"
    ),
}


# ============================================================
# LAYER 4 -- OpenAI's counter-move (sourced to OpenAI's own
# infrastructure post and Yahoo Finance hiring coverage)
# ============================================================

openai_response = {
    "role": "Community Engagement Lead",
    "salary": (
        "$129,600 to $236,000, plus equity. "
        "(source: finance.yahoo.com / openai-hiring-workers-reduce-friction)"
    ),
    "stated_function": (
        "proactively shape dialogue, surface concerns before they escalate, "
        "and embed community priorities into how projects advance. "
        "(source: finance.yahoo.com / openai-hiring-workers-reduce-friction)"
    ),
    "success_metric": (
        "reduced friction. (source: finance.yahoo.com)"
    ),
    "framing": (
        "getting communities on board with these data centers was "
        "'mission-critical'. (source: finance.yahoo.com)"
    ),
    "deployment_zones": (
        "Texas, Michigan, New Mexico, Wisconsin, Ohio (Stargate sites). "
        "(source: finance.yahoo.com)"
    ),
    "first_visible_action": (
        "donation to the Port Washington-Saukville Education Foundation in "
        "Wisconsin alongside Vantage Data Centers and Oracle. "
        "(source: openai.com / building-the-compute-infrastructure-for-the-"
        "intelligence-age)"
    ),
    "context": (
        "Stargate: OpenAI + Oracle + SoftBank + MGX, $500B AI infrastructure "
        "plan announced day after Trump's second term began. "
        "(source: finance.yahoo.com)"
    ),
}


# ============================================================
# LAYER 5 -- the water-use rhetoric (the coating)
# ------------------------------------------------------------
# Read this one carefully. The pattern matches what any
# coating-detector module is built to flag: redefine the system
# boundary at the building wall, report only what crosses the
# wall, compare residual to a household reference.
# ============================================================

water_claim = {
    "openai_framing": (
        "Abilene uses closed-loop cooling rather than traditional "
        "evaporative cooling towers. Once filled, water continuously moves "
        "through sealed pipes and is recirculated rather than consumed. "
        "One-time initial fill per building roughly two Olympic-sized "
        "swimming pools. After that, annual water use at full buildout "
        "comparable to a medium-sized office building, or about four "
        "average households. "
        "(source: openai.com / building-the-compute-infrastructure-for-the-"
        "intelligence-age)"
    ),
    "what_is_being_measured": "water inside the closed loop at the building",
    "what_is_NOT_measured": [
        "water consumed by the power plants feeding the site",
        "evaporative losses at upstream cooling towers (gas plants)",
        "watershed-scale aquifer drawdown across 8 co-sited facilities",
        "embedded water in concrete, steel, semiconductors",
        "make-up water for inevitable loop losses + maintenance",
    ],
    "the_trick": (
        "redefine system boundary at the building wall, report only what "
        "crosses that wall, compare residual to 'four households'"
    ),
}


# ============================================================
# LAYER 6 -- the playbook (energy diagram)
# ============================================================

PLAYBOOK_DIAGRAM = """
                    +-----------------------------+
                    |   AI 'NECESSITY' NARRATIVE  |
                    |   ($500B Stargate frame)    |
                    +--------------+--------------+
                                   |
                                   v
        +----------------------------------------------+
        |  SITE IN RURAL/UNINCORPORATED -- LOW LEGAL Z |
        |  (limited code, limited enforcement)         |
        +--------------+-------------------------------+
                       |
        +--------------+--------------+
        v              v              v
   GRID DRAW      WATER DRAW      NOISE/LAND
        |              |              |
        +--------------+--------------+
                       |
                       v  <-- COMMUNITY SENSOR FIRES
              +--------------------+
              |  MORATORIUM / BAN  |  <-- Hill County, Maine,
              |  / BALLOT MEASURE  |      Ohio, 12+ states
              +----------+---------+
                         |
        +----------------+----------------+
        v                                 v
   PHYSICAL FIX                      PERSUASION FIX
   (cooling redesign,                ($130k-236k Engagement Leads,
    grid build-out,                   foundation donations,
    siting reconsideration)           redefined boundary metrics,
   COST: billions                     'reduced friction' KPI)
                                     COST: ~$200k * N
                                              |
                                              v
                                    cheaper than physics
                                              |
                                              v
                                      <-- THE CHOICE THEY MADE
"""


# ============================================================
# LAYER 7 -- interference points (where the audit work fits)
# ============================================================

intervention_points = {
    "boundary_disclosure": (
        "require full lifecycle water + grid accounting INCLUDING upstream "
        "generation, not building-wall metrics"
    ),
    "NDA_ban": (
        "Georgia path: bar local officials from signing NDAs on water / "
        "electricity usage with developers. "
        "(source: builtin.com / states-push-data-center-moratoriums)"
    ),
    "rate_class_isolation": (
        "18+ states introducing special rate classes for large energy users; "
        "prevent cost shifts to residential customers. "
        "(source: multistate.us 2026-02-20 / state-data-center-legislation-"
        "in-2026-tackles-energy-and-tax-issues)"
    ),
    "co_location_cap": (
        "cap total MW per watershed/grid node, not per facility (Hill County "
        "problem: 8 facilities, each individually 'small')"
    ),
    "audit_modules_application": (
        "physics, thermodynamics, hidden dependencies, climate boundary "
        "conditions -- same shape as the BWCA / Hormuz cascade work, directly "
        "applicable here"
    ),
}


# ============================================================
# THE COMPRESSION
# ============================================================

COMPRESSION_NOTE = """
Six-figure persuaders are the cheapest line item in the stack.
They exist because the physics cannot be talked down and the
communities are reading the physics correctly. Every "Engagement
Lead" hired is a confession that the load is real.

The word "friction" is the signature. In any honest thermodynamic
accounting, friction is where the system tells you it's losing
energy. The KPI is to silence the loss-detector while continuing
to lose energy.

Same shape as Twin Metals. Same shape as the labor-thermodynamics
measurement failure. Same shape as the coating layer the audit
framework is built to flag.
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
        elif isinstance(v, dict):
            print(f"{indent}{k}:")
            _print_dict(v, indent + "  ")
        else:
            print(f"{indent}{k}: {v}")


def run():
    print("=" * 72)
    print("DATA CENTER SITING PLAYBOOK -- REAL-TIME ENERGY-FLOW MAP")
    print("=" * 72)

    print("\nLAYER 1 -- physical constraints that have already triggered")
    print("-" * 72)
    _print_dict(physical_load)

    print("\nLAYER 2 -- siting strategy (where the load gets dumped)")
    print("-" * 72)
    _print_dict(siting_logic)

    print("\nLAYER 3 -- the resistance (sensors firing back)")
    print("-" * 72)
    _print_dict(resistance_geography)

    print("\nLAYER 4 -- corporate counter-move (OpenAI, sourced)")
    print("-" * 72)
    _print_dict(openai_response)

    print("\nLAYER 5 -- the water-use rhetoric (the coating)")
    print("-" * 72)
    _print_dict(water_claim)

    print("\nLAYER 6 -- the playbook (energy diagram)")
    print("-" * 72)
    print(PLAYBOOK_DIAGRAM)

    print("\nLAYER 7 -- interference points (where the audit work fits)")
    print("-" * 72)
    _print_dict(intervention_points)

    print("\nTHE COMPRESSION")
    print("=" * 72)
    print(COMPRESSION_NOTE)


if __name__ == "__main__":
    run()
