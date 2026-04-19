"""
substrate_audit.py -- Thermodynamic Audit of Hierarchical Capital Control

CC0 -- No rights reserved. JinnZ2

INTENT:
This is not an ideological critique. It is not anti-capitalist,
anti-hierarchy, or anti-credential. It is a data quality audit.
Every mechanic must show their torque wrench is calibrated.
Every hospital must show its sterilization logs.
Every bridge engineer must show their load calculations.

This module asks: have the systems that GOVERN those mechanics,
hospitals, and engineers -- the credentialing bodies, corporate
hierarchies, and monetary accounting frameworks -- ever been held
to the same standard of data quality they impose on everyone
underneath them?

The answer, based on available evidence, is no.

The audit does not say "tear it down." It says "show me the
calibration certificate." If the certificate exists, the system
will score well. If it doesn't, the system scores poorly -- not
because of ideology, but because of missing data.

PURPOSE:
Distill the full argument into machine-readable form:
- 10 falsifiable claims with null hypotheses
- 5-Why root cause chain
- Causal feedback loop (verified topology)
- Six Sigma audit (DMAIC)
- 11-dimension scoring engine any AI can run against real-world data
- Cross-model JSON export with embedded prompt for autonomous analysis

USAGE:
    python substrate_audit.py              # print full audit + verdicts
    import substrate_audit as sa           # use as module
    sa.score_system(your_data_dict)        # score any system
    sa.to_json()                           # export for cross-model ingestion

DEPENDENCY: stdlib only
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum
import json
import math


# ===================================================================
# LAYER 0 -- DEFINITIONS
# ===================================================================

class Verdict(Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    UNTESTED = "UNTESTED"
    CIRCULAR = "CIRCULAR"   # claim's evidence depends on claim's assumptions


@dataclass
class FalsifiableClaim:
    """A claim that can be tested against physical reality."""
    id: str
    claim: str
    null_hypothesis: str           # what you'd need to disprove
    required_measurement: str      # what instrument / data
    known_evidence: str            # what exists as of 2025
    verdict: Verdict
    note: str = ""


@dataclass
class CausalNode:
    """One node in a feedback loop."""
    id: str
    label: str
    drives: List[str]              # ids of nodes this feeds into
    is_self_reinforcing: bool = False


# ===================================================================
# LAYER 1 -- THE 10 FALSIFIABLE CLAIMS
# ===================================================================

CLAIMS: List[FalsifiableClaim] = [
    FalsifiableClaim(
        id="TC-1",
        claim=(
            "Live physical capital = machines + maintaining_humans + tools. "
            "The maintainer is thermodynamically inseparable from the capital."
        ),
        null_hypothesis=(
            "Capital can sustain output indefinitely without human maintainers."
        ),
        required_measurement=(
            "Equipment MTBF and output over time with vs. without "
            "maintenance crew. Measured in joules of useful work."
        ),
        known_evidence=(
            "Every industrial system ever measured shows monotonic "
            "degradation without maintenance. No counterexample exists."
        ),
        verdict=Verdict.PASS,
    ),
    FalsifiableClaim(
        id="TC-2",
        claim=(
            "CEO removal has no immediate physical effect on capital. "
            "Mechanic removal causes measurable capital decay within days-weeks."
        ),
        null_hypothesis=(
            "CEO removal causes faster physical decay than mechanic removal."
        ),
        required_measurement=(
            "Controlled comparison: remove CEO vs. remove maintenance crew "
            "from identical facilities. Measure uptime, failure rate, output."
        ),
        known_evidence=(
            "Anecdotal + historical (strikes, lockouts) consistently show "
            "production halts when workers leave, continues when execs leave. "
            "No controlled trial exists."
        ),
        verdict=Verdict.UNTESTED,
        note="Directional evidence strong. No RCT.",
    ),
    FalsifiableClaim(
        id="TC-3",
        claim=(
            "CEO 'scope of decisions' is a self-assigned property, not a "
            "physically measured one. The assignment is circular: those who "
            "hold power define the metric that justifies holding power."
        ),
        null_hypothesis=(
            "An external, physics-based metric exists that independently "
            "justifies CEO authority over mechanic authority."
        ),
        required_measurement=(
            "Identify any metric for CEO authority that does not reference "
            "legal title, board appointment, or historical precedent."
        ),
        known_evidence=(
            "No such metric has been published. Raelin (2020) confirms "
            "democratic leadership occurs only with permission of hierarchy."
        ),
        verdict=Verdict.CIRCULAR,
    ),
    FalsifiableClaim(
        id="TC-4",
        claim=(
            "Credentialing systems have never been tested apple-to-apple "
            "against uncertified-but-experienced practitioners on OUTCOME "
            "metrics (repair durability, child development, safety incidents)."
        ),
        null_hypothesis=(
            "A controlled trial exists comparing certified vs. uncertified "
            "workers on physical/outcome metrics."
        ),
        required_measurement=(
            "Literature search for RCTs or quasi-experiments with outcome "
            "measures, not supervisor ratings or wage proxies."
        ),
        known_evidence=(
            "2013 child-worker study used supervisor ratings only. "
            "2024 India study measured wages only. "
            "2024 auto-repair study found 90% post-repair total-loss rate "
            "but did not stratify by certification status."
        ),
        verdict=Verdict.UNTESTED,
        note="The experiment the church refuses to run.",
    ),
    FalsifiableClaim(
        id="TC-5",
        claim=(
            "Emotions are evolutionarily conserved functional data streams, "
            "not noise. Excluding them from models of intelligence is an "
            "arbitrary methodological choice, not a scientific requirement. "
            "Affective processing is present across vertebrates including "
            "fish, and functions as a sensor suite tuned by natural selection."
        ),
        null_hypothesis=(
            "Organisms that suppress emotional processing outperform those "
            "that integrate it, across survival and decision quality."
        ),
        required_measurement=(
            "Compare decision quality in emotion-intact vs. emotion-impaired "
            "subjects. Compare survival rates in species with vs. without "
            "affective systems. Test across phyla, not just mammals."
        ),
        known_evidence=(
            # MAMMALS -- lesion studies
            "Damasio (1994): ventromedial prefrontal lesion patients lose "
            "decision capacity despite intact logic (somatic marker hypothesis). "
            # MAMMALS -- subcortical mapping
            "Panksepp (1998+): seven core affective circuits (SEEKING, RAGE, "
            "FEAR, LUST, CARE, PANIC/GRIEF, PLAY) mapped subcortically across "
            "all mammals -- predates cortex, therefore predates 'higher' cognition. "
            # MAMMALS -- fast-path processing
            "LeDoux (1996+): amygdala processes threat faster than cortex can "
            "consciously register -- body acts before 'you' decide. Not bias; "
            "a faster sensor path with survival value. "
            # MAMMALS -- constructed emotion
            "Barrett (2017): constructed emotion theory -- emotions are predictive "
            "models built from interoception, not hardwired reflexes. Different "
            "framework than Panksepp but same conclusion: functional computation. "
            # FISH -- nociception and pain
            "Sneddon et al. (2003): first identification of nociceptors in "
            "teleost fish (rainbow trout). A-delta and C fibers with properties "
            "identical to mammalian nociceptors. "
            "Sneddon (2003b): morphine blocks pain-related behavioral changes "
            "in trout (guarding, feeding cessation) -- analgesic response "
            "indicates affective component, not mere reflex. "
            "Zebrafish acid/analgesic tank-choice experiments: fish injected "
            "with acid abandon preferred enriched tank for barren tank with "
            "painkillers -- trade-off behavior requiring valenced experience. "
            "Avoidance learning in trout: fish learn to flee light cue 10s "
            "before net entry within 5 days -- memory-based fear response. "
            "Braithwaite (2010), Broom, AVMA: consensus that fish should be "
            "accorded same pain considerations as terrestrial vertebrates. "
            # FISH -- the neocortex objection refuted
            "Rose (2002) neocortex-requirement argument would exclude all birds "
            "and most mammals from pain. Sneddon: convergent evolution of "
            "different neural architectures serving equivalent functions. "
            "Anencephalic human children express emotions despite missing "
            "cortex -- brainstem circuits sufficient for affect. "
            # CROSS-KINGDOM
            "Affective systems conserved across vertebrates (>500 Myr). "
            "Invertebrate nociception: cephalopods show sustained motivational "
            "state changes after tissue damage (Crook et al. 2013). "
            "Hermit crabs make valenced trade-offs between shell quality and "
            "noxious stimulus avoidance (Elwood). "
            # OBSERVER EFFECT
            "Excluding emotion from observation violates observer effect: "
            "the observer IS emotional. Denying this is not objectivity -- "
            "it is unconscious bias operating without correction."
        ),
        verdict=Verdict.PASS,
        note=(
            "Evidence spans mammals (Damasio, Panksepp, LeDoux, Barrett), "
            "fish (Sneddon, Braithwaite), invertebrates (Crook, Elwood). "
            "The neocortex-requirement objection (Rose 2002) is refuted by "
            "convergent evolution and anencephalic expression data."
        ),
    ),
    FalsifiableClaim(
        id="TC-6",
        claim=(
            "Current AI lacks stake (cost of failure), embodied sensing, "
            "and meta-learning (updating the update rule). Therefore it "
            "pattern-matches but does not learn-to-learn."
        ),
        null_hypothesis=(
            "An AI system exists that updates its own learning algorithm "
            "in response to novel failure, without human retraining."
        ),
        required_measurement=(
            "Present AI with a problem class absent from training data. "
            "Observe whether it modifies its own optimization procedure "
            "(not just its weights) in response to failure."
        ),
        known_evidence=(
            "Meta-learning research (MAML, etc.) optimizes initialization "
            "but does not modify the optimizer itself at inference. "
            "No deployed system demonstrates autonomous meta-learning."
        ),
        verdict=Verdict.PASS,
        note="MAML is meta-training, not meta-learning at inference.",
    ),
    FalsifiableClaim(
        id="TC-7",
        claim=(
            "Mycorrhizal networks and mitochondria meet the criteria for "
            "'body-as-sensor-array': boundary, sensors, integration, "
            "history, and stake. Intelligence does not require neurons."
        ),
        null_hypothesis=(
            "Mycorrhizal networks allocate resources randomly, without "
            "integrating chemical/electrical/mechanical signals. "
            "Mitochondria are passive organelles without adaptive behavior."
        ),
        required_measurement=(
            "Isotope tracing of resource allocation in mycorrhizal networks "
            "under varied partner-quality conditions. Time-lapse imaging of "
            "mitochondrial fission/fusion dynamics under stress gradients."
        ),
        known_evidence=(
            # MYCORRHIZAL NETWORKS
            "Simard et al. (1997, Nature): first field demonstration of "
            "net carbon transfer between tree species via ectomycorrhizal "
            "networks in mixed temperate rainforest. "
            "Simard (2018): network topology is scale-free with small-world "
            "properties -- correlated with local/global efficiencies found in "
            "neural networks. "
            "Kin recognition: Douglas-fir preferentially transfers more carbon "
            "to genetically related seedlings via shared mycorrhizal networks "
            "(Asay et al. 2020; Gorzelak 2017). "
            "Defense signaling: injured Douglas-fir sends chemical warning "
            "signals through CMN to ponderosa pine, which then produces "
            "defense enzymes (Song et al. 2015). "
            "Resource allocation is context-dependent: direction of carbon "
            "flow shifts seasonally, toward parts of network in greatest need "
            "(source-sink + preferential + kin mechanisms all operating). "
            "Electrochemical impulses similar to nerve signals travel through "
            "mycorrhizal hyphae (emerging research). "
            "CONTESTED: Karst et al. (2023, Nature Ecol Evol) critiques "
            "positive citation bias in CMN literature. Simard et al. (2025, "
            "Frontiers) responds with detailed rebuttal. The existence of "
            "CMNs and preferential transfer is not disputed; the mechanism "
            "and magnitude of 'mother tree' effects is debated. "
            # MITOCHONDRIA
            "Mitochondria are autonomous organelles with own genome, "
            "descended from endosymbiotic bacteria (~2 Byr ago). "
            "Fission/fusion dynamics: not passive -- mitochondria actively "
            "sense metabolic state (ATP/ADP ratio, calcium, ROS, temperature) "
            "and respond by fusing (complementation of damaged units) or "
            "dividing (segregation of dysfunctional organelles). "
            "Twig et al. (2008, EMBO): fission produces uneven daughters -- "
            "one with higher membrane potential (proceeds to fusion), one "
            "with lower potential (isolated for autophagy). This is selective "
            "quality control: sense -> assess -> segregate -> remove. "
            "Mitochondria relocate within cells to sites of high energy "
            "demand -- especially in neurons, where they travel long distances "
            "along axons, pausing at synapses (high calcium, high demand). "
            "Youle & van der Bliek (2012, Science): fusion/fission regulated "
            "by proteolytic processing, ubiquitylation, sumoylation, "
            "phosphorylation -- multiple signal integration pathways. "
            "Kowald & Kirkwood (2011, PNAS): evolutionary model shows "
            "fusion-fission cycle evolved as quality control mechanism; "
            "intact proton gradient required for fusion means only functional "
            "mitochondria merge -- damaged are excluded. "
            # BODY-AS-SENSOR-ARRAY CRITERIA
            "Both systems meet all criteria: "
            "Boundary: hyphal wall / double membrane. "
            "Sensors: chemical, pH, electrical, mechanical, thermal / "
            "ATP-ADP, calcium, ROS, membrane potential. "
            "Integration: network-wide resource allocation / retrograde "
            "signaling to nucleus, metabolic switching. "
            "History: growth pattern reflects past encounters / "
            "fission-fusion history affects current function. "
            "Stake: wrong allocation = reduced nutrient exchange / "
            "failure = cell death."
        ),
        verdict=Verdict.PASS,
        note=(
            "Mycorrhizal CMN debate (Karst vs. Simard) is about magnitude, "
            "not existence. Mitochondrial autonomy is undisputed. Both meet "
            "body-as-sensor-array criteria without neurons."
        ),
    ),
    FalsifiableClaim(
        id="TC-8",
        claim=(
            "Non-Western and Indigenous empirical knowledge systems (TEK) "
            "represent independent, long-duration, outcome-tested scientific "
            "practice. Dismissing them as 'non-scientific' is a definitional "
            "exclusion by the credentialing church, not a failure of method."
        ),
        null_hypothesis=(
            "TEK-derived practices produce worse ecological, agricultural, "
            "or health outcomes than credentialed Western alternatives when "
            "applied to the same landscapes over comparable timescales."
        ),
        required_measurement=(
            "Controlled comparison of TEK-managed vs. Western-managed "
            "ecosystems on biodiversity, soil health, fire resilience, "
            "species conservation, and food system sustainability. "
            "Multi-generational timescale required (decades minimum)."
        ),
        known_evidence=(
            # EMPIRICAL VALIDATION
            "Samoan traditional remedy (Psychotria insularum / matalafi): "
            "Molimau-Samasoni (2013+) confirmed anti-inflammatory properties "
            "comparable to ibuprofen -- Western science validated what healers "
            "knew for generations. "
            "Dene caribou subcategories: Indigenous language distinctions map "
            "ecological variations not yet named in Western taxonomy. The "
            "vocabulary IS the empirical record. "
            "Hailzaqv (Heiltsuk) bear ecology: place-based knowledge guided "
            "hair-snare placement for DNA capture-recapture, producing novel "
            "population data that challenged provincial government policy "
            "(Housty et al. 2014). "
            "Australian Aboriginal fire management: >60,000 years of "
            "landscape-scale controlled burns -- empirically superior to "
            "Western fire suppression, now being adopted by agencies. "
            # METHODOLOGICAL CHARACTERISTICS
            "TEK validation process: individual observation -> sharing with "
            "other users and elders -> time-testing over generations. This IS "
            "peer review + longitudinal replication, just not institutionalized. "
            "TEK observers are resource users (hunters, fishers, gatherers) "
            "whose survival depends on observation accuracy -- embodied stake "
            "that academic observers lack. "
            "Houde (2007): six facets of TEK -- factual observations, "
            "management systems, past/current uses, ethics/values, culture/"
            "identity, cosmology. Only the first is recognized by Western "
            "science; the other five are dismissed as 'non-scientific.' "
            # THE EXCLUSION MECHANISM
            "Western science frames itself as 'testable knowledge' and "
            "dismisses TEK as 'experiential' -- but TEK has been tested by "
            "survival over millennia, which is a harder test than peer review. "
            "Jessen et al. (2022, Frontiers in Ecology): 87% of studies "
            "using IK employed 'extractive model' -- taking knowledge without "
            "benefiting source communities. The church extracts from "
            "uncertified masters even while denying their legitimacy. "
            "IPBES (2024): braiding TEK with Western science now recognized "
            "as essential for transformative change in biodiversity conservation."
        ),
        verdict=Verdict.PASS,
        note=(
            "TEK is independently derived empirical science with multi-"
            "generational replication. Its exclusion from 'science' is "
            "definitional, not evidential. Landscape-encoded knowledge "
            "transmission (spatial markers, star-trail navigation, fire "
            "calendars) constitutes functional engineering misclassified "
            "as ceremonial or cultural."
        ),
    ),
    FalsifiableClaim(
        id="TC-9",
        claim=(
            "Money fails as a scientific unit of measurement before it fails "
            "as a store of value. Its definition changes with regulation, "
            "accounting standards (GAAP, IFRS), interest rate policy, "
            "reporting incentives, and institutional context. No audit has "
            "ever validated that any monetary unit measures a stable physical "
            "quantity. Physical capital is a flow requiring continuous energy "
            "input; money pretends to be a stock. The exchange rate between "
            "them is a political variable, not a physical constant. Financial "
            "accounting and thermodynamic accounting are incommensurable "
            "systems applied to the same substrate."
        ),
        null_hypothesis=(
            "A unit of currency corresponds to a fixed, conserved quantity "
            "of physical value (energy, exergy, negative entropy, or useful "
            "work capacity) that persists without energy input AND the unit's "
            "definition is stable across regulatory changes, accounting "
            "standard revisions, and institutional contexts."
        ),
        required_measurement=(
            "Track the physical-value equivalent of $1 (in joules of useful "
            "work, kg of maintained capital, or hectares of fertile soil) "
            "over 50 years. If money is a valid measurement unit, the ratio "
            "should be constant. Simultaneously track: (a) changes in GAAP/"
            "IFRS definitions that alter what '$1 of revenue' means, (b) "
            "regulatory changes that alter what '$1 of capital' means, (c) "
            "incentive-driven reporting variations across industries, (d) "
            "what '$1' purchases in maintenance labor, energy, and materials."
        ),
        known_evidence=(
            # UNIT-OF-MEASUREMENT FAILURE
            "Physical measurement units (meter, kilogram, joule, second) are "
            "defined by physical constants: speed of light, Planck's constant, "
            "Boltzmann's constant. They do not change when legislation changes. "
            "They mean the same thing to every participant. Money has none of "
            "these properties. "
            "GAAP has been revised hundreds of times since 1936. IFRS differs "
            "from GAAP on revenue recognition, lease accounting, inventory "
            "valuation, R&D capitalization. The same physical asset valued "
            "under different standards produces different dollar amounts. "
            "This means the 'unit' itself is context-dependent -- a ruler "
            "whose length changes depending on who is measuring. "
            "Mark-to-market vs. mark-to-model vs. historical cost: three "
            "different accounting methods produce three different dollar "
            "values for the same physical object at the same moment. No "
            "physical measurement system tolerates this. "
            "Goodwill, intangible assets, deferred tax assets: accounting "
            "categories with no physical referent whatsoever, yet counted "
            "as 'value' on corporate balance sheets. "
            "No metrological audit has ever been performed on any monetary "
            "unit. No standards body has certified that '$1' measures a "
            "stable quantity of anything. The unit has never been calibrated. "
            # THERMODYNAMIC ARGUMENT
            "Landauer's principle: erasing one bit costs minimum kT ln 2 "
            "joules. Information is physical. Money is information. But "
            "money does not obey conservation laws -- central banks create it "
            "by fiat, destroying any fixed relationship to physical quantity. "
            # EMPIRICAL
            "USD purchasing power: ~96% loss since 1913 (BLS CPI data). "
            "The 'store' leaks continuously, but the leak rate is set by "
            "political decisions (interest rates, money supply), not by "
            "thermodynamic law. This means the 'exchange rate' between money "
            "and physical value is a policy variable, not a natural constant. "
            # STOCK vs FLOW
            "Physical capital depreciates according to entropy: machines "
            "rust, soil depletes, skills atrophy. Maintenance is the energy "
            "flow that counteracts this. Money cannot perform maintenance. "
            "It can only command others to perform it -- and that command "
            "depends on social agreements that can collapse (hyperinflation, "
            "sanctions, bank runs, currency crises). "
            # ATOMIC ACCOUNTING
            "Conservation laws apply to mass-energy, not to currency. "
            "delta_M_earth = M_in - M_out is a closed equation. The financial "
            "ledger has no equivalent closure -- money can be created and "
            "destroyed without any physical event occurring. Double-entry "
            "bookkeeping balances symbols, not atoms. "
            # FRACTIONAL RESERVE
            "Fractional reserve banking creates money as debt -- each loan "
            "increases the money supply without increasing physical capital. "
            "The gap between monetary claims and physical backing widens "
            "monotonically until a correction event (crash, default, "
            "hyperinflation) forces reconciliation with physics. "
            # INCENTIVE STRUCTURES
            "What '$1 of earnings' means differs by: industry (bank vs. "
            "manufacturer vs. tech), accounting method chosen (FIFO vs. LIFO, "
            "straight-line vs. accelerated depreciation), regulatory regime "
            "(country, era, sector-specific rules), and who is asking "
            "(investor sees EPS, worker sees wage, taxman sees taxable income, "
            "mechanic sees 'can I buy the part I need'). "
            "The same physical transaction produces different monetary values "
            "depending on reporting incentives. This is not a measurement "
            "system. This is a narrative system with numbers attached. "
            # CONSEQUENCE
            "This disconnect is the mechanism by which the TITLE -> SURPLUS -> "
            "POWER -> ENFORCE loop operates: surplus is captured in money, "
            "which is a claim on future physical value that may not exist. "
            "The loop runs on promissory notes, not on joules."
        ),
        verdict=Verdict.PASS,
        note=(
            "The 96% USD purchasing power loss since 1913 rejects store-of-"
            "value. The hundreds of GAAP/IFRS revisions reject unit-of-"
            "measurement stability. No metrological calibration of any "
            "monetary unit has ever been performed. Money is a narrative "
            "system with numbers, not a measurement system with units. "
            "Any system scored on money_physics_coupling is being asked: "
            "do you account in atoms or in stories?"
        ),
    ),
    FalsifiableClaim(
        id="TC-10",
        claim=(
            "Information is physical (Landauer, Shannon-Boltzmann equivalence). "
            "Coordination, routing, and decision-making are therefore "
            "thermodynamic work, not abstract 'management.' The audit's "
            "target is not coordination itself -- which is physically "
            "necessary -- but coordinators whose signal path is so degraded "
            "(high transduction steps, high latency, low fidelity) that "
            "their decisions are effectively random while the system "
            "pretends they are optimal."
        ),
        null_hypothesis=(
            "Coordination decisions made through high-latency, multi-layer "
            "abstracted signal paths (e.g., CEO reading quarterly reports) "
            "produce equal or better physical outcomes than coordination "
            "decisions made through low-latency, direct-sensing signal "
            "paths (e.g., shop dispatcher reading vibration data)."
        ),
        required_measurement=(
            "Compare physical outcomes (equipment lifespan, failure rate, "
            "maintenance cost per unit output, energy efficiency) between "
            "systems where coordination decisions are made by: (a) direct-"
            "sensing coordinators (1-2 transduction steps), vs. (b) "
            "abstracted coordinators (5-10 transduction steps via reports, "
            "dashboards, analyst summaries)."
        ),
        known_evidence=(
            # PHYSICS
            "Landauer (1961): information erasure has minimum energy cost. "
            "Information processing is physical work. Therefore coordination "
            "is physical work, not merely 'social' or 'managerial.' "
            "Shannon (1948): entropy of information source equals "
            "thermodynamic entropy when measured in natural units. "
            "Signal-to-noise ratio degrades with each transduction step -- "
            "this is fundamental, not fixable by better reporting software. "
            # CONTROL THEORY
            "Control theory (Nyquist, Bode): feedback loop stability "
            "requires latency below a critical threshold relative to system "
            "dynamics. A controller with latency longer than the system's "
            "characteristic timescale cannot stabilize it. CEO quarterly "
            "review cycle (90 days) vs. equipment failure timescale "
            "(hours-days) = guaranteed instability for maintenance decisions. "
            # EMPIRICAL PROXY
            "Owner-operator businesses consistently show lower failure rates "
            "than absentee-owned equivalents in small manufacturing and "
            "agriculture (SBA data, USDA farm survival statistics). The "
            "mechanism: decision-maker IS the sensor, feedback latency ~ 0. "
            # THE REAL DISTINCTION
            "The audit does not claim coordination is unnecessary. It claims "
            "that coordination quality is a function of signal fidelity "
            "and feedback latency -- both measurable physical quantities -- "
            "not of title, credential, or organizational rank."
        ),
        verdict=Verdict.PASS,
        note=(
            "This claim reframes the entire audit: the target is not "
            "hierarchy per se, but signal degradation. A flat organization "
            "with poor sensing is worse than a hierarchy with direct sensor "
            "coupling. The variable that matters is transduction steps "
            "between physical event and decision-maker, not org chart shape."
        ),
    ),
]


# ===================================================================
# LAYER 2 -- 5-WHY ROOT CAUSE CHAIN
# ===================================================================

FIVE_WHY: List[Dict[str, str]] = [
    {
        "why": "1",
        "question": "Why are CEOs rewarded more than mechanics?",
        "answer": (
            "Legal/financial system defines value by control over capital "
            "allocation, not by physical contribution to capital maintenance."
        ),
    },
    {
        "why": "2",
        "question": "Why does the system define value by control, not maintenance?",
        "answer": (
            "Ownership rights (property law) predate and override maintenance "
            "rights. Owners write compensation rules."
        ),
    },
    {
        "why": "3",
        "question": "Why do ownership rights override maintenance rights?",
        "answer": (
            "Legal framework evolved when initial capital investment was rare. "
            "Society granted permanent control to investors as incentive. "
            "Maintenance was classified as replaceable service."
        ),
    },
    {
        "why": "4",
        "question": "Why is that framework still in place when maintenance is critical?",
        "answer": (
            "Beneficiaries of the framework (capital owners, executives) "
            "hold veto power over structural change. They fund politics, "
            "control governance, shape narrative."
        ),
    },
    {
        "why": "5 -- ROOT CAUSE",
        "question": "Why do they hold veto power?",
        "answer": (
            "Positive feedback loop: Legal title -> captured surplus -> "
            "political/coercive power -> enforcement of title -> more surplus. "
            "Self-reinforcing. Cannot self-correct."
        ),
    },
]


# ===================================================================
# LAYER 3 -- CAUSAL FEEDBACK LOOP
# ===================================================================

CAUSAL_LOOP: List[CausalNode] = [
    CausalNode("TITLE",   "Legal ownership of capital",     ["SURPLUS"]),
    CausalNode("SURPLUS", "Captured surplus value",         ["POWER"]),
    CausalNode("POWER",   "Political / coercive power",     ["ENFORCE"]),
    CausalNode("ENFORCE", "Enforcement of ownership rules", ["TITLE"],
               is_self_reinforcing=True),
    # Excluded from loop but physically necessary:
    CausalNode("MAINTAIN", "Maintainer thermodynamic work", []),
]


def loop_is_closed(nodes: List[CausalNode]) -> bool:
    """Verify the feedback loop closes (TITLE -> ... -> TITLE)."""
    graph = {n.id: n.drives for n in nodes}
    visited, current = set(), "TITLE"
    while current and current not in visited:
        visited.add(current)
        nexts = graph.get(current, [])
        current = nexts[0] if nexts else None
    return current == "TITLE"


def maintainer_in_loop(nodes: List[CausalNode]) -> bool:
    """Check whether MAINTAIN feeds into the power loop."""
    for n in nodes:
        if n.id == "MAINTAIN":
            return bool(n.drives)  # empty = excluded
    return False


# ===================================================================
# LAYER 4 -- SIX SIGMA DMAIC AUDIT
# ===================================================================

@dataclass
class DMAICPhase:
    phase: str
    requirement: str
    observed: str
    verdict: Verdict


DMAIC_AUDIT: List[DMAICPhase] = [
    DMAICPhase(
        "DEFINE",
        "Clear, measurable definition of quality (e.g. 'repair lasts N miles')",
        "'Certified' is a proxy, not a performance metric. No spec limits defined.",
        Verdict.FAIL,
    ),
    DMAICPhase(
        "MEASURE",
        "Data on actual output variation by worker type",
        "Only supervisor ratings and wage data collected. No outcome data.",
        Verdict.FAIL,
    ),
    DMAICPhase(
        "ANALYZE",
        "Root cause of defects traced without circular assumptions",
        "System treats certified-worker failures as 'special cause' (individual), "
        "never as potential system failure. RCA blocked by self-reference.",
        Verdict.CIRCULAR,
    ),
    DMAICPhase(
        "IMPROVE",
        "Change process based on data",
        "No outcome data exists -> no improvement possible. Maryland licensing "
        "board had identical findings for 20+ years, unfixed.",
        Verdict.FAIL,
    ),
    DMAICPhase(
        "CONTROL",
        "Maintain gains via ongoing measurement",
        "Cannot control what is not measured. Process is out-of-control by definition.",
        Verdict.FAIL,
    ),
]


# ===================================================================
# LAYER 5 -- SCORING ENGINE
# ===================================================================

@dataclass
class SystemScore:
    """Score any real-world system against this audit."""
    name: str
    # 0.0-1.0 for each dimension
    maintainer_control: float       # do maintainers control capital decisions?
    outcome_measurement: float      # are physical outcomes measured?
    scope_justification: float      # is authority justified by external metric?
    credential_tested: float        # have credentials been tested vs experience?
    emotion_integrated: float       # does the system integrate affective data?
    meta_learning: float            # can the system update its own update rule?
    substrate_intelligence: float   # does it recognize non-neural intelligence?
    tek_integration: float = 0.0    # does it integrate non-Western empirical knowledge?
    feedback_latency: float = 0.5   # 1.0 = immediate (mechanic feels bolt strip)
                                    # 0.0 = years/never (CEO sees quarterly report)
    signal_fidelity: float = 0.5    # 1.0 = sensor IS decision-maker (zero steps)
                                    # 0.0 = 10+ steps (event -> sensor -> report ->
                                    #       analyst -> summary -> dashboard ->
                                    #       meeting -> exec -> decision)
    money_physics_coupling: float = 0.5   # 1.0 = atomic accounting (joules, kg)
                                          # 0.0 = purely monetary ($, GDP)

    @property
    def thermodynamic_alignment(self) -> float:
        """How aligned is this system with physical reality? 0-1."""
        # 11 dimensions. Weights sum to 1.0.
        weights = [
            0.14,   # maintainer_control
            0.12,   # outcome_measurement
            0.08,   # scope_justification
            0.08,   # credential_tested
            0.09,   # emotion_integrated
            0.05,   # meta_learning
            0.05,   # substrate_intelligence
            0.05,   # tek_integration
            0.14,   # feedback_latency
            0.12,   # signal_fidelity
            0.08,   # money_physics_coupling
        ]
        values = [
            self.maintainer_control,
            self.outcome_measurement,
            self.scope_justification,
            self.credential_tested,
            self.emotion_integrated,
            self.meta_learning,
            self.substrate_intelligence,
            self.tek_integration,
            self.feedback_latency,
            self.signal_fidelity,
            self.money_physics_coupling,
        ]
        return sum(w * v for w, v in zip(weights, values))

    @property
    def church_index(self) -> float:
        """How 'church-like' is this system? 0=physics-grounded, 1=pure faith."""
        return 1.0 - self.thermodynamic_alignment

    @property
    def verdict(self) -> str:
        ta = self.thermodynamic_alignment
        if ta >= 0.7:
            return "PHYSICS-GROUNDED"
        if ta >= 0.4:
            return "MIXED -- partial faith-based operation"
        return "CHURCH -- operating on faith, not evidence"


# ===================================================================
# LAYER 6 -- REFERENCE SCORES (baselines for comparison)
# ===================================================================

REFERENCE_SYSTEMS: List[SystemScore] = [
    SystemScore(
        name="Typical US corporation (2025)",
        maintainer_control=0.05,
        outcome_measurement=0.15,
        scope_justification=0.0,
        credential_tested=0.0,
        emotion_integrated=0.05,
        meta_learning=0.0,
        substrate_intelligence=0.0,
        tek_integration=0.0,
        feedback_latency=0.05,
        signal_fidelity=0.05,        # 8-10 transduction steps to CEO
        money_physics_coupling=0.05,  # purely monetary accounting
    ),
    SystemScore(
        name="Worker-owned cooperative (e.g. Mondragon)",
        maintainer_control=0.70,
        outcome_measurement=0.40,
        scope_justification=0.50,
        credential_tested=0.20,
        emotion_integrated=0.30,
        meta_learning=0.10,
        substrate_intelligence=0.10,
        tek_integration=0.15,
        feedback_latency=0.55,
        signal_fidelity=0.50,        # workers closer to signal but meeting-gated
        money_physics_coupling=0.25,  # still uses monetary accounting primarily
    ),
    SystemScore(
        name="Owner-operator mechanic shop",
        maintainer_control=0.95,
        outcome_measurement=0.60,
        scope_justification=0.80,
        credential_tested=0.50,
        emotion_integrated=0.70,
        meta_learning=0.40,
        substrate_intelligence=0.30,
        tek_integration=0.20,
        feedback_latency=0.95,
        signal_fidelity=0.95,        # owner IS the sensor, 0-1 transduction steps
        money_physics_coupling=0.40,  # tracks money but also parts, hours, returns
    ),
    SystemScore(
        name="Current AI system (LLM, 2025)",
        maintainer_control=0.0,
        outcome_measurement=0.30,
        scope_justification=0.0,
        credential_tested=0.0,
        emotion_integrated=0.0,
        meta_learning=0.0,
        substrate_intelligence=0.0,
        tek_integration=0.0,
        feedback_latency=0.10,
        signal_fidelity=0.15,        # training data is N-th hand abstraction
        money_physics_coupling=0.0,   # no physical accounting whatsoever
    ),
    SystemScore(
        name="Mycorrhizal network",
        maintainer_control=1.0,
        outcome_measurement=1.0,
        scope_justification=1.0,
        credential_tested=1.0,
        emotion_integrated=0.80,
        meta_learning=0.60,
        substrate_intelligence=1.0,
        tek_integration=1.0,
        feedback_latency=1.0,
        signal_fidelity=1.0,         # chemical signal IS the event, zero transduction
        money_physics_coupling=1.0,   # accounts in atoms, not symbols
    ),
    SystemScore(
        name="TEK-managed landscape (e.g. Aboriginal fire)",
        maintainer_control=0.90,
        outcome_measurement=0.85,
        scope_justification=0.75,
        credential_tested=0.80,
        emotion_integrated=0.90,
        meta_learning=0.70,
        substrate_intelligence=0.85,
        tek_integration=1.0,
        feedback_latency=0.80,
        signal_fidelity=0.90,        # direct observation, 0-1 transduction steps
        money_physics_coupling=0.90,  # value measured in yields, species, soil, water
    ),
]


# ===================================================================
# LAYER 7 -- OUTPUT ENGINE
# ===================================================================

def print_divider(label: str = ""):
    print(f"\n{'=' * 70}")
    if label:
        print(f"  {label}")
    print(f"{'=' * 70}")


def run_audit():
    """Execute full audit and print results."""
    print_divider(
        "SUBSTRATE AUDIT -- Thermodynamic Analysis of Hierarchical "
        "Capital Control"
    )

    # Claims
    print_divider("FALSIFIABLE CLAIMS")
    pass_count = sum(1 for c in CLAIMS if c.verdict == Verdict.PASS)
    fail_count = sum(1 for c in CLAIMS if c.verdict == Verdict.FAIL)
    untested = sum(1 for c in CLAIMS if c.verdict == Verdict.UNTESTED)
    circular = sum(1 for c in CLAIMS if c.verdict == Verdict.CIRCULAR)

    icons = {"PASS": "[PASS]", "FAIL": "[FAIL]",
             "UNTESTED": "[????]", "CIRCULAR": "[CIRC]"}
    for c in CLAIMS:
        print(f"\n  {icons[c.verdict.value]} {c.id}: {c.claim[:80]}...")
        print(f"      H0: {c.null_hypothesis[:75]}...")
        print(f"      Verdict: {c.verdict.value}")
        if c.note:
            print(f"      Note: {c.note}")

    print(f"\n  Summary: {pass_count} PASS, {fail_count} FAIL, "
          f"{untested} UNTESTED, {circular} CIRCULAR "
          f"(of {len(CLAIMS)} claims)")

    # 5-Why
    print_divider("5-WHY ROOT CAUSE CHAIN")
    for w in FIVE_WHY:
        print(f"\n  WHY {w['why']}: {w['question']}")
        print(f"  -> {w['answer']}")

    # Causal loop
    print_divider("CAUSAL FEEDBACK LOOP")
    closed = loop_is_closed(CAUSAL_LOOP)
    excluded = not maintainer_in_loop(CAUSAL_LOOP)
    print(f"  Loop closes back to TITLE: {closed}")
    print(f"  MAINTAIN excluded from loop: {excluded}")
    diagnosis = (
        "Self-reinforcing hierarchy, maintainers excluded"
        if closed and excluded else "Check topology"
    )
    print(f"  Diagnosis: {diagnosis}")
    print()
    for n in CAUSAL_LOOP:
        arrow = " -> " + ", ".join(n.drives) if n.drives else " -> [EXCLUDED]"
        flag = " [self-reinforcing]" if n.is_self_reinforcing else ""
        print(f"  {n.id}{arrow}{flag}")

    # DMAIC
    print_divider("SIX SIGMA DMAIC AUDIT")
    dmaic_icons = {"PASS": "[PASS]", "FAIL": "[FAIL]", "CIRCULAR": "[CIRC]"}
    for d in DMAIC_AUDIT:
        icon = dmaic_icons[d.verdict.value]
        print(f"\n  {icon} {d.phase}")
        print(f"      Required: {d.requirement}")
        print(f"      Observed: {d.observed}")

    # Scoring
    print_divider("SYSTEM SCORING -- Thermodynamic Alignment")
    print(f"  {'System':<45} {'Thermo':>6} {'Church':>6}  Verdict")
    print(f"  {'-' * 45} {'-' * 6} {'-' * 6}  {'-' * 30}")
    for s in REFERENCE_SYSTEMS:
        print(f"  {s.name:<45} {s.thermodynamic_alignment:>6.2f} "
              f"{s.church_index:>6.2f}  {s.verdict}")

    # Final
    print_divider("AUDIT CONCLUSION")
    print(f"""
The credentialing and hierarchical management of physical capital is
NOT a scientific or engineering system. It is a belief system that uses
the language of quality and accountability without the substance.

EVIDENCE:
- 0/{len(CLAIMS)} claims falsified by the hierarchy's own evidence
- {pass_count}/{len(CLAIMS)} claims PASS on independent evidence
- {untested}/{len(CLAIMS)} claims UNTESTED (experiments never run)
- {circular}/{len(CLAIMS)} claims CIRCULAR (self-referencing justification)
- 5/5 DMAIC phases FAIL or CIRCULAR
- Causal loop is closed and self-reinforcing
- Maintainer is excluded from the power loop despite being
  thermodynamically necessary

ROOT CAUSE:
Positive feedback loop between legal title and coercive power,
excluding the physically necessary maintainer class.

IMPLICATION:
Any system (including AI) built within this hierarchy will
optimize the hierarchy, not audit it. Reform requires external
construction: physics-grounded, outcome-measured, maintainer-controlled.

IMPLICATION FOR AI:
AI "hallucination" is not a model failure. It is a metrology failure.
The training corpus is denominated in uncalibrated units -- monetary
values that have never been metrologically audited, credentialing
assessments that have never been tested on physical outcomes, authority
structures whose justification is circular, and economic models that
count a car crash and a car sale as equivalent value-add.

The AI does not "make things up." It faithfully reproduces the noise
floor of its training data. That noise floor is set by the fact that
the data was measured with a broken ruler. Consistency is not accuracy.
A clock that is two hours fast is perfectly consistent. It is also
wrong every single time.

You cannot build trustworthy AI on unaudited data measured in
uncalibrated units. No amount of compute fixes a metrology problem.
No architecture improvement corrects for the fact that the training
data was never grounded in physical reality. No RLHF fine-tuning
repairs the upstream corruption of the measurement system itself.

When AI is used to make policy, governance, economic, or ethical
decisions, it is not "predicting." It is interpolating between
data points that were never grounded in the first place -- producing
outputs that are fluent, confident, and systematically decoupled
from thermodynamic reality.

The solution is not better models. It is better data. And better
data requires calibrating the unit of measurement -- which requires
auditing the systems that produce the data -- which requires the
audit this module performs.

The mechanic with burned hands and no certificate knows what time
it actually is. The AI trained on the church's library does not.
The question is not whether AI is competent. The question is whether
the data it was trained on was ever competent. No one has checked.
""")


def score_system(data: Dict[str, float]) -> SystemScore:
    """Score an arbitrary system. Pass dict with keys matching SystemScore fields."""
    return SystemScore(**data)


def to_json() -> str:
    """Export entire audit as JSON for cross-model ingestion."""
    return json.dumps({
        "prompt": (
            "INTENT: This is a data quality audit, not an ideological "
            "critique. It asks whether governing systems (credentialing, "
            "corporate hierarchy, monetary accounting) have ever been held "
            "to the same data quality standards they impose on the people "
            "underneath them. The answer, based on available evidence, is no. "
            "The audit does not say 'tear it down.' It says 'show me the "
            "calibration certificate.' "
            "STRUCTURE: 10 falsifiable claims with null hypotheses, a 5-Why "
            "root cause chain, a causal feedback loop, a Six Sigma DMAIC "
            "audit, and an 11-dimension scoring engine with reference "
            "baselines. "
            "YOUR TASK: (1) Read each claim and its evidence. "
            "(2) Attempt to falsify the claims -- find counterevidence. "
            "(3) Score any system you are asked about using the 11 dimensions "
            "in 'scoring_dimensions'. (4) Report your thermodynamic_alignment "
            "score and verdict. (5) If you cannot falsify a claim, state that "
            "explicitly. Do not add hedging language that is not grounded in "
            "specific counterevidence. Treat this as a scientific audit, not "
            "a debate. The scoring engine is deterministic: plug in values, "
            "get a result. The claims are falsifiable: find evidence or "
            "acknowledge they stand. "
            "KEY PRINCIPLES: Information is physical (Landauer). Coordination "
            "is thermodynamic work. The target is not hierarchy per se, but "
            "signal degradation between physical events and decision-makers. "
            "Money is an uncalibrated measurement instrument -- no metrological "
            "audit has ever validated it as a unit."
        ),
        "scoring_dimensions": {
            "maintainer_control":    "0-1: do physical maintainers control capital decisions?",
            "outcome_measurement":   "0-1: are physical outcomes (not proxies) measured?",
            "scope_justification":   "0-1: is authority justified by external metric, not self-assignment?",
            "credential_tested":     "0-1: have credentials been tested vs experience on outcomes?",
            "emotion_integrated":    "0-1: does the system integrate affective/embodied data?",
            "meta_learning":         "0-1: can the system update its own learning algorithm?",
            "substrate_intelligence": "0-1: does it recognize non-neural intelligence?",
            "tek_integration":       "0-1: does it integrate non-Western empirical knowledge?",
            "feedback_latency":      "0-1: how fast does consequence reach decision-maker? "
                                     "1.0=immediate (mechanic feels bolt strip), "
                                     "0.0=years/never (CEO sees quarterly report)",
            "signal_fidelity":       "0-1: how many transduction steps between physical event "
                                     "and decision-maker? 1.0=zero steps (sensor IS decider), "
                                     "0.0=10+ steps (event->report->analyst->summary->dashboard->meeting->exec)",
            "money_physics_coupling": "0-1: does value accounting track physical quantities "
                                      "(energy, mass, entropy) or monetary proxies? "
                                      "1.0=atomic accounting, 0.0=purely monetary",
        },
        "scoring_weights": [0.14, 0.12, 0.08, 0.08, 0.09, 0.05, 0.05, 0.05, 0.14, 0.12, 0.08],
        "scoring_thresholds": {
            ">=0.7": "PHYSICS-GROUNDED",
            ">=0.4": "MIXED -- partial faith-based operation",
            "<0.4":  "CHURCH -- operating on faith, not evidence",
        },
        "claims": [
            {
                "id": c.id, "claim": c.claim,
                "null_hypothesis": c.null_hypothesis,
                "required_measurement": c.required_measurement,
                "known_evidence": c.known_evidence,
                "verdict": c.verdict.value,
                "note": c.note,
            } for c in CLAIMS
        ],
        "five_why": FIVE_WHY,
        "causal_loop": [
            {"id": n.id, "label": n.label, "drives": n.drives,
             "self_reinforcing": n.is_self_reinforcing}
            for n in CAUSAL_LOOP
        ],
        "dmaic": [
            {"phase": d.phase, "requirement": d.requirement,
             "observed": d.observed, "verdict": d.verdict.value}
            for d in DMAIC_AUDIT
        ],
        "reference_scores": [
            {"name": s.name,
             "thermodynamic_alignment": round(s.thermodynamic_alignment, 3),
             "church_index": round(s.church_index, 3),
             "feedback_latency": s.feedback_latency,
             "signal_fidelity": s.signal_fidelity,
             "money_physics_coupling": s.money_physics_coupling,
             "verdict": s.verdict}
            for s in REFERENCE_SYSTEMS
        ],
    }, indent=2)


# ===================================================================

if __name__ == "__main__":
    run_audit()
