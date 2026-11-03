# Dependency-Chain Energy Accounting Standard (DCEA) v0.1

Co-authored. CC0. Status: PROPOSED draft.

Tags: OBSERVED = field report. DERIVED = literature or calculation. PROPOSED = design choice. Asterisks mark thin volume: more asterisks means thinner.

## 1. Purpose

The standard records where the energy behind a unit of output, or a unit of currency spent, actually goes. It traces the full dependency chain, so that denominators can't be moved by incentive, fashion or politics.

It also tests labels against structure. A firm that calls itself "self-made" or "independent" can be checked against its measured dependency ratio, and a cooperative can be identified as one.

## 2. Why existing standards fall short (DERIVED)

- **ISO 14040/14044 (LCA):** the user picks the system boundary. That choice is the loophole.
- **Mine-mouth EROI:** stops at the site. Extended EROI (Murphy & Hall) counts delivery and use and comes out lower.
- **GHG Protocol Scope 3:** follows the supply chain, but the unit is carbon, not energy.
- **EEIO tables (EXIOBASE etc.):** give sector averages per dollar. Useful as a fallback, but they hide firm-level dependencies.

## 3. Core rules (PROPOSED)

- **R1 Fixed boundary.** The chain is followed until every node closes, either at primary energy or at a stamped boundary with a reason. No boundary may be chosen for convenience.
- **R2 Stand-alone cost.** Shared or pooled services (cloud, outsourcing, shared infrastructure) are charged at what the firm would need to run them alone, as if the pool did not exist. Pooling savings go on the pool operator's ledger, not the firm's.
- **R3 Scope stamp on every number:** time window, place, partners, rules in force, conditions, source. A number without a stamp can't be compared.
- **R4 Break marking.** Any rule, code, index or rebasing change starts a new segment. Segments are reconciled only through a stated common denominator, never by sharing a label.
- **R5 Failure-backup cost.** Count the energy of the manual backup when automation fails, multiplied by observed event frequency. Count the automation's own energy separately.
- **R6 Recurring debts.** Corrosion, maintenance, recertification and rework are charged per unit of time or throughput, not once.
- **R7 Dry work.** Exploration, failed studies and dry holes are charged to the output that eventually succeeds.
- **R8 Financial structure.** Accounting, entity maintenance, shells, transfers and audits are physical loads. They are charged at stand-alone compute plus staff, offices and travel.
- **R9 Single-source flag.** Any node with one supplier is flagged as a fragility point, in addition to its energy cost.
- **R10 Provenance.** Every node carries its tag (OBSERVED / DERIVED / PROPOSED) and a volume mark.
- **R11 Unknown is a slot, not a zero.** An unmeasured node is recorded as PENDING, never as 0. The count of PENDING nodes is reported alongside the result.
- **R12 True market price.** Subsidies, grants, tax breaks, incentives and loss claims are charged back to the firm at true market price. They move cost onto someone else's ledger; they don't remove it. Each one is listed as a transfer node with its source (who paid), and reported both with and without the transfer, so the unsubsidized figure is always visible.
- **R13 Physical base rate.** Currency is itself a frozen equation, and price indices drift with method changes. Every monetary figure is stamped with its date and converted to energy (MJ) at that date's rate, so comparisons happen in joules, not dollars. Labor hours and a fixed physical basket are kept as cross-checks. Worker pay is reported the same way, as **homeostasis coverage**: the share of the worker's homeostatic needs (food, water, shelter, heat, health, rest) that a period's pay can buy at that date and place. Coverage of 1.0 means pay exactly maintains the organism; the full list of needs is PROPOSED and open for calibration.

**R13 detail: homeostasis coverage (PROPOSED)**

- **Unit: organism-day.** Physiological anchors with body-driven ranges: food energy (about 8–12 MJ/day), water (about 2–4 L/day), heat budget (watts to hold 37 °C at that climate and shelter), clean air (radon and other hazards below limits), sleep (about 7–9 h), sanitation and care.\*
- **Minimum rule.** Coverage = the lowest single need covered (Liebig's law of the minimum), never the average. A house without heat, or food with unsafe air, fails.
- **Place-bound.** Each need is costed where the job requires the worker to live, in that season.
- **Year-round.** Coverage is measured across the full year, including lean and cold seasons, not at the peak.
- **Skill curve.** Self-provision rates are reported at several skill levels, novice to lifelong. A measured field rate (about two weeks of food from two hours of gathering in a good spring or summer window, skill trained from childhood: OBSERVED) is an upper reference point, not the norm.
- **Time cost.** Paid hours displace hours of self-provision and skill-building. Both are counted.
- **Open:** dependents (children, elders) and bodies with higher needs (illness, pregnancy, age) change the denominator, so coverage is per household. How to weight needs that can't substitute for each other is unresolved.\*\*

**R12 detail: cost of access to work (PROPOSED)**

- **Worker-paid inputs** the job requires (water, food on the road, clothing, safety gear, boots, masks, idling fuel for heat or cooling, air protection) are transfer nodes onto the worker's ledger. Real wage = pay minus these, before homeostasis coverage is tested.
- **Allowance check.** A stated allowance is tested against the actual local price where the job is, stamped by date. Field case (OBSERVED): $100 boot allowance against about $212 for the required steel-toe boots locally; the cheaper option meant a detour of about 50 miles, whose fuel and hours also count.
- **Tax leak.** If a reimbursement is paid through payroll as taxable wages, the after-tax amount is what counts as reimbursed. The tax taken is a further transfer.
- **Compliance vs function.** Gear provided for the audit but not usable (ill-fitting masks, one-size vests) is logged separately from functional gear the worker bought. Only functional gear counts toward the need being covered.
- **Hiring-term routes.** "Provide your own" terms and contractor classification are logged as the mechanism by which the cost moved.

**R13 detail: known deviations in official denominators (logged 2026-11-02)**

Each row is a way an official number departs from what a person actually pays. Every price used under R13 is checked against this list.

| Deviation | Official number | Ground check | Tag |
| --- | --- | --- | --- |
| Shelf vs captive market | BLS bananas $0.656/lb (Sept 2026), about $0.25–0.30 each | truck stop: 2 for $1.56, about $0.78 each (2.6–3x) | OBSERVED + DERIVED |
| Captive-market markup | not captured | truck stops earn thin fuel margins, profit in-store; markup stacks delivery at $6.55 diesel, refrigeration, staff; cereal $7.57–9.57; zoning keeps stops out of towns, no walkable alternative | OBSERVED |
| Skill/time to reach index price | BLS includes sale prices; substitution follows cheaper choices\* | reaching the BLS price takes couponing, timed shopping, restricted food choice | OBSERVED |
| Healthy-diet floor | FAO CoHD US 2025: $2.86/person/day (estimated) | no ground price found at that level; cheapest item per food group, national average prices | DERIVED (her FAOSTAT download) |
| Bulk assumption | CoHD assumes bulk-price access | weekly pay and monthly SNAP force small purchases; low-income households pay more per unit (Orhun & Palazzolo 2019); SNAP cycle runs short by month end | OBSERVED + DERIVED |
| Kitchen, storage, cooking time | assumed present | absent on the road; small in high-rises (Japan); time poverty buys back as fast food | OBSERVED |
| Access to the store | not counted | China: walk or bike, bulk carried home, room to store. Japan: dense markets, small storage. US: car-dependent; about 19M in low-income, low-access tracts (USDA 2015)\* | OBSERVED + DERIVED |
| Subsidized shelf prices | lowers US CoHD | farm subsidies move cost to another ledger; charge back under R12\* | PROPOSED |
| Cross-country method mismatch | China listed as simple (4.59) and weighted (3.68) averages; US one figure | earlier search snippets gave China 3.13, Japan 5.98 vs file 3.68–4.59, 8.27; PPP base year not stated | PENDING |
| Average hides distribution | US food = about 11% of disposable income | lowest-income fifth about 30%+;\* dollar share, not nutrient content | DERIVED |
| Expected vs current price level | NY Fed SCE, Michigan measure expected inflation | no published side-by-side of what people pay vs the index; no utilities category (Consumer Reports Oct 2026: about 1 in 5 cut groceries to pay electricity) | GAP |

Rule: an official price enters R13 only with its method stamp and the matching ground check. Where no ground check exists, the node is PENDING.

## 4. Outputs (PROPOSED)

- **Full-chain EROI** = energy delivered ÷ total chain energy.
- **Site EROI**, for comparison, with the gap between it and full-chain EROI reported.
- **Dependency ratio** = external stand-alone energy ÷ total chain energy.
- **Label check:** stated independence claim vs dependency ratio. Thresholds are left open for calibration.
- **Fragility list:** single-source nodes and failure-backup nodes.
- **PENDING count:** the share of the chain that is unmeasured. This is a finding, not an error.

## 5. Worked example: one barrel of WTI (skeleton)

Node inputs are OBSERVED from field experience (pipe hauling, salt water pump-offs). Numbers are left PENDING until they are sourced. Literature anchors are DERIVED and thin.

| Node | Content | Tag | Note |
| --- | --- | --- | --- |
| Exploration | seismic, satellite, ground tests, leasing, permits, geologist studies that find nothing | OBSERVED | R7 dry work\*\* |
| Finance overhead | fund juggling, entities, accounting | OBSERVED | R8, stand-alone servers |
| Drilling equipment | specialty bits (PDC: synthetic diamond on tungsten carbide), purpose-built rigs | OBSERVED + DERIVED | R9 single-source |
| Drilling labor | hard conditions, injuries | OBSERVED | fatality rate above all-industry average (NIOSH)\* |
| Trucking | flatbed pipe and steel loads | OBSERVED | trips per well: PENDING\*\* |
| Digital overhead | SCADA, LACT, software, sensors, cyber | OBSERVED | stand-alone compute, R2 |
| Produced water | radioactive brine (NORM), pits, spills, well contamination, injection | OBSERVED + DERIVED | water-to-oil ratio: PENDING\*\* |
| Corrosion | tank spigots and valves eaten through, frequent replacement | OBSERVED | R6 recurring |
| Failed automation | level pumps fail; 3–4 truck pump-offs a day in floods | OBSERVED | R5, frequency rising |
| Event rechecks | storms and floods force full system rechecks | OBSERVED | R5 |
| Gathering + pipeline | automated, pumping energy | OBSERVED | PENDING |
| Refining |  | — | PENDING |

## 6. Calculator (stdlib Python)

```python
# dcea.py — CC0, co-authored, stdlib only
from dataclasses import dataclass, field

@dataclass
class Node:
    name: str
    energy_mj: float | None      # None = PENDING (R11), never 0
    tag: str                     # OBSERVED / DERIVED / PROPOSED
    stamp: dict                  # R3: window, place, partners, rules, source
    external: bool = False       # supplied by another firm (R2)
    single_source: bool = False  # R9
    recurring_per_year: bool = False  # R6
    volume: int = 0              # asterisks: 0 = solid
    children: list = field(default_factory=list)

def walk(n):
    yield n
    for c in n.children:
        yield from walk(c)

def account(root, delivered_mj, site_names=()):
    nodes = list(walk(root))
    known = [n for n in nodes if n.energy_mj is not None]
    pending = [n.name for n in nodes if n.energy_mj is None]
    total = sum(n.energy_mj for n in known)
    ext = sum(n.energy_mj for n in known if n.external)
    site = sum(n.energy_mj for n in known if n.name in site_names)
    unstamped = [n.name for n in nodes if not n.stamp]
    return {
        "full_chain_eroi": delivered_mj / total if total else None,
        "site_eroi": delivered_mj / site if site else None,
        "dependency_ratio": ext / total if total else None,
        "pending": pending,
        "pending_share": len(pending) / len(nodes),
        "fragility": [n.name for n in nodes if n.single_source],
        "unstamped": unstamped,  # R3 violation list
        "note": "lower bound on chain energy while pending > 0",
    }
```

The calculator walks the tree, never counts a PENDING node as zero, and reports full-chain and site EROI side by side, together with the dependency ratio, the fragility list and any unstamped numbers.

## 7. Open

- Thresholds for the label check: unset, PROPOSED to calibrate on real cases.
- Common-denominator method for cross-segment reconciliation (R4): energy units first, with the differential-glyph method to be written.
- WTI node numbers: to be sourced, each with a stamp.
