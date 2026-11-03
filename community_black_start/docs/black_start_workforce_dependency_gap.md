# Black Start Workforce Dependency Gap

Co-authored (Kavik + Claude), 2026-11-03. CC0. Tags: OBSERVED / DERIVED / PROPOSED. Thin-volume claims marked with asterisks (more = thinner).

## 1. The gap

- Black start restoration takes months, sometimes many months. Plans assume the grid is the thing restored and load is a passive endpoint.
- Rural areas supply the raw materials other places need, and the workers who know how the machines run live there.
- Those workers can only show up if their households survive without them. Restoration speed depends on the workforce; the workforce's survival depends on buffers that policy removed. The loop runs on the same timescale as the restoration: months, in winter.
- Double bind: small-town workers hit hardest by forced electrification are the same people the factories and the restoration need.
- Assumption to audit: that a black start happens when somebody flips a switch.

## 2. Denominator

- Population undercount (Nature Communications 2026) is the right input for service and mortality questions and the WRONG input for restoration order.
- Proposed restoration denominator: TIME EACH SEGMENT CAN HOLD WITHOUT GRID POWER (buffer duration). Connected industrial load tracked separately from people.
- Rural electrical draw at restart is mostly industrial, extraction, processing, hospitals and care facilities, not houses. Rural households run fewer suburban appliances; many have wood, propane, alternative heat; well pumps are intermittent.
- Rural preparation is a control strategy for long lead times with no backup in reach: batched trips, home inventory, buffers sized for the worst gap, repair over replacement, redundancy where one failure strands you.

### Measurand problems in the statistics

- RECS-based analysis: rural household electricity \~50% higher than urban (15,258 vs 10,290 kWh/yr). Scope: national average includes the electrically heated Southeast; annual consumption is not restart peak.
- Same label, different boundary: a rural household may carry a farm, shop or repair work on the house meter; a suburban one does not. Farm accounts on separate meters fall outside.
- Rural classification conflicts: Census urban = 5,000+ (2,500 before 2020), so Cloquet is urban and Carlton is rural; OMB by county and commuting; RUCA by tract; USDA thresholds up to 20,000-35,000. Boondock acreage and small towns land in the same bin.

## 3. Mandated electrification of passive systems

Pattern: a requirement removes a passive or non-electric function, metered load rises, and the no-power fallback is deleted.

- HEAT, by code: coal, fuel-oil and wood furnaces replaced with grid heat in uninsulated old buildings. Efficiency gain on paper, kWh real.
- SANITATION, by municipal mandate: Superior requires sewer connection even with working well and septic. Gravity septic needs no power; sewer adds pumps at the house and plant draw utility-side.
- FIRE, by insurance and lending: wood stoves and cook stoves restricted. On record: air-district install rules, burn bans, sole-source exemptions. Through the loan: FHA/VA/USDA appraisals require a permanent non-wood primary heat source. Carrier practice not public.\*
- Incentive gradient: the loan selects for households with least margin. Converts a labor-paid input into a cash-paid one, and the resilience loss rides along.

## 4. Dependency layers (bootstrap chain)

- L0 no grid needed: knowledge holders; drawings and patterns; scrap iron and steel; coke or charcoal; deployable workers.
- L1 cupola foundry: coke, scrap, patterns, molders, blower (diesel, belt or manual). Output: rough castings.
- L2 machine shop: diesel or water-driven power, machinists who read drawings. Output: finished parts.
- L3 dam rehab: parts, millwrights, operators, working gates and penstocks. Output: local hydro.
- L4 island power: feeds back to foundry and shop (loop closes), hospitals, care facilities, fuel pumps, comms.
- L5 raw-material industry (lumber, smelting, shipbuilding) and freight: materials and fuel for main-grid black start.
- Main-grid chain: self-starting generation with on-site fuel; fuel resupply (pumps need power); comms and SCADA on hours of battery; operators, switching crews, dispatchers; cold load pickup in small blocks. Fails at people and fuel before engineering.
- Loops: fuel pumps need power, power needs fuel. Dam powers the shop that makes dam parts. Restoration needs rural materials; rural workers need heat to supply them.
- Single points of failure: the knowledge holders (aging out) and the first fuel stock before L4.

### Latent assets inventory

- Dormant or disconnected hydro along the Mississippi, St. Louis, St. Croix, Cloquet area, Green Bay area. Per site: facility type, output, horsepower, tooling, old parts.
- Industrial on-site generation (e.g. USG and local mills) able to island nearby feeders.
- Data leads: USACE National Inventory of Dams; ORNL/DOE non-powered dam assessment (\~12 GW national potential\*\*); FERC license history; Historic American Engineering Record drawings; state historical societies.
- "Nobody makes it anymore" describes the supply chain, not what is physically possible. Local foundries are the only supply chain left in a black start.

### Rail

- Steam needs no grid and no diesel: moves coal, castings, food, crews; a locomotive boiler can serve as stationary power.
- Steam parts: boiler tubes, flues, staybolts, firebox sheets need certified boiler work; bearings, brasses, grates, valve parts, injectors fit local foundry and machine shops. Engine condition per site is an inventory step.
- Modern diesels cannot convert to steam. US freight lines have no overhead wire. Biodiesel blends (B20) work; B100 gels in Minnesota winter; feedstocks soybean oil, rendering fat, used cooking oil; stockpile methanol and lye.
- Blackout-priority corridors modeled on STRACNET/STRAHNET; planned staging sidings so diesel consists park before fuel runs out; mapped water and coal stops.
- Water: old railroad water towers and elevated stock tanks (Wyoming, Montana); windmill refill needs no power; boiler water treatment on the stock list.

### Sanitation as energy node

- Treatment plants with digesters make biogas; some already run generators on it. Energy-positive examples: Strass (Austria), Marselisborg (Denmark).
- Design principle: grid-connected, island-capable.
- Winter heat backup for digesters: wood-fired or other hot-water boilers.
- Gap: energy balance for a mid-size US plant islanded through a northern winter.\*

## 5. Trigger table

Columns: THRESHOLD | ACTION | DEBT CARRIED FORWARD | HANDOFF

- Diesel at set days remaining | plants shed to essentials (lift pumps, disinfection, digester heat and mixing); route biogas to pre-installed dual-fuel gensets; scrub H2S; stop flaring, store gas; engine waste heat to digester | deferred maintenance on gensets | certified plant operator takes over from improvised crew
- Diesel at set level on rail | diesel consists to staging sidings; corridor switches to steam or biodiesel | raw boiler water means extra blowdown now, tube work later | heritage crew to certified boiler operator
- Early days, any system | run on what is on hand (improvised filtration, hand-made parts) | each shortcut logged with a due date | upgrade at next trigger
- Capability arrives | handoff protocol | debt ledger transfers with the task | receiver sets timing

PROGRESSIVE TRIGGERS: waiting for the ideal design pushes delay down the whole chain. Improvise now, log what you owe, pay it back at the next trigger.

HANDOFF PROTOCOL: the task never stops during transfer (hand stays on the bleed). Transfer in order: doing now, did before, observed, deferred. Receiver takes over when ready. Liability cover needed for emergency improvisers, as for first responders.

POSITION INDEX: name the rung on the historical ladder (1700s, 1800s, 1880s, 1920s, streetlights). The next rung and its requirements are already known, along with the error record. Floor is horses and hand tools; that rung is currently occupied (Amish). Substitution layer under each rung: the rung names the function, the environment picks the material.

## 6. Workforce variables

- DEPLOYABILITY: can this person's household run without them, no grid, for the restoration duration. Not recorded anywhere; checkable by survey.
- DEPENDENCY NETWORK: who must be covered for this person to be deployable. Not legal family: exes who co-parent, new partners, elderly parents, siblings, custody schedules. Military dependent definitions miss these.
- SKILL CONCENTRATION: how many people in the household can keep it alive without the grid. If one, and that one is the operator, every callout forces a choice.
- PRIORITY ORDERING: home versus community obligation when they conflict. In Pentecostal and evangelical practice, family comes first; a man holding the protector role will stay home. Same planning factor for Orthodox Jewish observance and others. Lead: override clauses for life-saving work (pikuach nefesh) and whether a community reads restoration as covered.
- Divided attention: an operator present but worried about home has a higher error rate in switching and cold load pickup.
- Pay premiums fail: wage buys labor, not the household; there is no functioning market to spend it in. Mutual aid works for regional storms because help comes from outside; a wide black start removes the outside.
- Unattached pool is transient: median first marriage for men \~30; \~40% of US births to unmarried parents; tenure median \~2.7 yrs ages 25-34 vs \~9.8 ages 55-64. Seasoned operators carry rare-event experience, tacit pattern recognition, networks.
- Cheaper play: keep seasoned operators deployable by covering their dependency networks.
- Families moved with operators: honors religious duty and the work. Criterion must be the dependency network, applied the same to everyone. Pre-registered per-operator relocation plans; provisioning sized per network. Precedent: hospital staff families during Katrina.
- Breadth plus depth: paired crews (senior depth, junior breadth); drills where the junior redoes what the senior ran; regional drill consortium so job-hopping carries drill-certified skill. Regional baseline black-start skill set across all companies. Next step: compare NERC EOP-005 regional drill requirements against an operator-level baseline that moves with the person.
- Training: stages, triggers, debt ledger and handoff as a shared module in FEMA NIMS/ICS, NERC certification, trade continuing education. NIMS resource typing could type the knowledge-holder pools; COOP plans are where dependency networks, latent assets and trigger tables belong.

## 7. Knowledge-holder inventory

- Old timers: dam and boiler operators, millwrights, patternmakers, molders, machinists who work from drawings. Capture now: filmed walkthroughs on equipment, part drawings and foundry patterns, list of which local shops make which parts.
- Hobbyist casters: backyard foundries on charcoal, propane or waste oil; small parts only.
- Antique steam and threshermen clubs, blacksmith guilds, model engineering clubs.
- Heritage rail crews (Duluth area as starting point).
- Navy boiler technicians, old (BT rating) and current (Machinist's Mate); findable through veterans' rosters.
- Composite earth builders (fiber, clay, lime); thinnest-documented pool.

## 8. Social layer

- Usual plans assume the outside supply chain survives and only local nodes fail. In a wide black start the outside is also dark.
- Build from the floor up: what can be made locally with no grid. The country's own development path is the existence proof.
- Starting locally and building outward reduces unrest: a community acting has information, a role, and visible progress. A community waiting sees another town lit up.
- Guards have dependency networks too. Security is a legitimacy problem: a stock the town draws from locally first, then outward, gives every locality something to protect. Provisioning guards' households is what makes the post viable.
- Bought loyalty needs constant upkeep and scales badly; built capacity scales well.
- People carry deprivation if the trajectory is visible and they have a role: next step named, each household's part, sequence outward. Missing trigger-table column: what the population can see and do at each stage.
- Basic organism needs come first; a plan that depends on people overriding them is built against a known force.
- Cases with the same pattern regardless of side: Bosnia, Puerto Rico, Morocco, Somalia.

## 9. General schema: ladder, forward and backward triggers

The method applies to any prolonged emergency, not only the grid. Find your rung, step up when a trigger clears, step down when one fails, and carry the debt ledger and handoff through every move.

### The ladder (position index)

Each rung names the function level, what it needs, what it enables, and the error record learned there. Every rung was occupied once, so each is reachable from the one below. The ladder gives sequence, not timing; some rungs relied on conditions now gone (old-growth timber, local ore grades), so the substitution layer applies.

| Rung | Needs | Enables | Error record carried forward |
| --- | --- | --- | --- |
| R0 Muscle and hand tools (pre-1700s floor; Amish occupied) | people, animals, hand tools, local material | food, water by hand, shelter, fire heat | fire in enclosed spaces, contaminated water |
| R1 Water and wind mechanical (1700s) | mill sites, millwrights, wood and stone | grinding, sawing, pumping, small forge work | dam failure, gearing breakage |
| R2 Coal steam and cupola foundry (1800s) | coal or coke, boiler makers, patternmakers, molders | castings, rail, stationary power, freight | boiler explosions before pressure standards |
| R3 Local DC and hydro islands (1880s) | dynamos, dam turbines, line crews | lighting, machine shops, pumps on wire | electrocution, fire from overloaded wiring |
| R4 Regional AC grid and diesel (1920s) | transformers, transmission, diesel fuel, dispatch | streetlights, town grids, motor freight | cascading outages, single-source dependence |
| R5 Interconnected grid with SCADA (present) | full supply chain, comms, certified crews | everything current | brittleness when the outside fails |

### Forward triggers (step up)

A step up happens when ALL of these clear for the next rung: inputs on hand for a set duration (fuel days, parts, water); at least one knowledge holder for that rung present; current rung's debt ledger reviewed so no deferred item is critical; and a fallback ready if the new rung fails. Step up one rung at a time.

### Backward triggers (step down)

A step down happens when ANY of these fail: an input falls below its threshold (fuel, water, coolant, parts); the knowledge holder is lost (injury, exhaustion, leaves); a deferred debt item comes due and cannot be paid; or a safety limit is crossed (boiler pressure, line fault, contamination). Stepping down is planned, not a collapse: shed to essentials, move to the rung below, keep its systems warm. Log why, and what must clear to step back up.

### Every move carries

- DEBT LEDGER: each improvised stage logs what it deferred and its due date; the ledger travels with the task.
- HANDOFF PROTOCOL: task never stops during transfer; doing, did, observed, deferred; receiver sets timing.
- SUBSTITUTION LAYER: the rung names the function; the environment picks the material.
- POPULATION COLUMN: what people can see and do at this rung, so the trajectory is visible.

### Generic trigger row (fill per system)

| Field | Meaning |
| --- | --- |
| System | what is being run (power, water, sanitation, freight, heat) |
| Current rung | position on the ladder |
| Forward threshold | what must clear to step up |
| Backward threshold | what failure forces a step down |
| Action | what happens when it fires |
| Debt carried | what is deferred and when it comes due |
| Handoff | who takes over and under what conditions |
| Population sees and does | the visible role for people at this stage |

## 10. Open gaps

- Where utility restoration crews actually live versus buffered households.\*
- Carrier underwriting practice on wood heat.\*
- Islanded winter energy balance for a mid-size treatment plant.\*
- Condition of regional steam engines and dormant dam parts.
- Dual-fuel diesel savings at plants.\*
- Whether outside-help-free restoration timelines exist in any regional plan.
