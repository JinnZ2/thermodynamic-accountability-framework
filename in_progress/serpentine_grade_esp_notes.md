# Serpentine grade -- ESP rollover trigger, notes in progress

Opened 2026-09-24. Live-scoping notes, not a module. Status tags follow
`labor_thermodynamics/driver_hours_evidence_register.py` (OBSERVED /
SECONDARY / DERIVED / PROPOSED / UNMEASURED / UNREAD).

Links into the register:
- FAULT B ("response sign inverted", already filed) = the anomaly-sign
  note under `COMPETENCE_MEASURAND` and row 2 of `TIMESCALE_MISMATCH`.
- The trapped-rig and closure costs extend gate G4 (door-to-door
  accounting) and QH.
- `DESCENT_RECORD` follows the same rule as `BEHAVIOUR_RECORD_SCHEMA`:
  record behaviour and state, not the label.

```
SERPENTINE GRADE — TWO BODIES, ONE SENSOR SITE

   road reversal ──► TRACTOR (cab on air-ride mounts)  ◄── sensor site
                        │   short relaxation time
                        │   reverses FIRST
                        │   oscillation ACCUMULATES here
                        │
                   fifth wheel  ── partial roll decoupling
                        │
                     TRAILER  (high CG, the mass that actually rolls)
                            lags the tractor
                            oscillation NOT reflected here     [OBSERVED, operator]

   trigger reads:  cab signal ↑  →  "rollover risk"  →  BRAKE
   physical state: trailer quiet →  brake pushes load onto trailer
                                 →  rollover risk actually ↑


FAULT A  measured body ≠ at-risk body        [DERIVED from OBSERVED]
         Same class as the fifth-wheel "attached" proxy: the sensor
         reads an observable that comes apart from the state that
         matters, silently.
         Tractor-mounted stability systems estimating trailer state
         from tractor lateral/roll signal — SECONDARY, as far as
         known; separate trailer-mounted roll systems exist. Which
         one your units run: UNREAD.

FAULT B  response sign inverted               [already filed]
         Braking removes the momentum that was holding the combination
         and loads the trailer into the next reversal.


# PROPOSED — needs a trailer-side channel; sign test, not a threshold
def classify(cab_roll, trailer_roll, curve_reversal_period_s):
    if cab_roll_high and trailer_roll_low:
        return "GEOMETRIC_CAB_MODE"   # serpentine accumulation, no trigger
    if trailer_roll_high:
        return "TRAILER_ROLL_RISK"    # the case the trigger was built for
    # phase check: cab leads trailer by ~one reversal on serpentine;
    # a real trailer roll event does not show cab-leads-trailer
    ...


GAP-1  sensor mount location + estimation method for the units you run   [UNREAD]
GAP-2  paired cab/trailer roll traces on a serpentine grade              [UNMEASURED]
       cheapest version: two phone IMUs, cab + trailer, one descent,
       compare amplitude and phase
GAP-3  event logs: does the trigger record trailer state at all,
       or only the tractor signal it acted on?                           [UNREAD]


ENVELOPE MAP                        grade = 0        grade 9–13% descending
                                  ─────────────    ────────────────────────
single turn (90° on flat)         │ WORKS         │  untested
continuous reversals (serpentine) │ untested/mild │  FAILS  ◄── interaction cell


DOWNGRADE alone         trailer PUSHES the tractor → braking shifts load
                        forward and into the coupling
SERPENTINE alone        cab oscillation accumulates, but with no push
                        from behind the combination tracks
BOTH                    push + accumulating cab signal + brake response
                        → trailer loaded into the next reversal
                                                        [DERIVED from OBSERVED]


finding           rollover trigger performs correctly
test conditions   flat grade, single turns                  [OBSERVED, operator]
validity range    grade ≈ 0; serpentine × downgrade NOT covered
status            RATED inside envelope / UNRATED in the interaction cell


FLAT                                 DOWNGRADE 9–13%
────                                 ───────────────
frame baseline ≈ level               frame pitched forward + down
threshold headroom = full            baseline already offset toward threshold
                                     trailer mass pushing through fifth wheel
                                     front axle loaded, drives lightened

   signal = baseline + oscillation
   flat:      0      + osc  → under threshold
   downhill:  offset + osc  → crosses threshold sooner       [DERIVED]


gravity along road ──► frame forward/down  (pre-load)
        + serpentine ──► cab oscillation accumulates
        = reading nears threshold with trailer quiet
        → trigger BRAKES
        → more forward pitch, more trailer push into the coupling
        → the brake response adds to the load it read as danger
                                              [DERIVED from OBSERVED]


# PROPOSED
baseline = f(grade, load, speed)           # expected frame attitude on this descent
signal   = cab_reading - baseline          # oscillation relative to the loaded state,
                                           # not relative to level ground
if signal > threshold and trailer_roll_high:
    respond()


axis check                                                     DERIVED
  grade (pitch)       contaminates the LONGITUDINAL axis
  bank + body roll    contaminate the LATERAL axis  ← the one the roll trigger reads

  serpentine curves are usually superelevated (banked), and the bank
  flips sign at every reversal
  → on your grades the lateral channel gets a gravity term that
    reverses with each curve, on top of the accumulating oscillation
  → grade adds the forward load transfer; bank adds the sensor error


"not compensated"
  documented:  no grade/pitch sensor in the Bendix set; sensor zeroed level;
               bank contamination is a known false-trigger source;
               compensation exists in patents
  unknown:     whether the EC-80 algorithm estimates bank/grade from
               wheel speed + yaw + lateral                      [UNREAD —
               proprietary]
  checkable:   event logs via ACom diagnostics — does a logged roll
               intervention carry a bank or grade estimate, or only raw
               lateral accel?
               the two-phone test from before, plus phone GPS elevation
               for grade


SAME DESCENT, TWO INSTRUMENTS
  phone gyro (cab)      → like every other run down those hills   [OBSERVED]
  ESP (frame, zeroed    → rollover risk, BRAKE                    [OBSERVED]
       level)
  → a quantity the phone didn't see as unusual crossed the
    ESP threshold
  → candidates: gravity/bank term in the ESP lateral channel,
    frame-vs-cab mount difference, or the controller's model  [DERIVED — not separable
                                                                from this one pair]


curve N ──► ESP brakes ──► you THROTTLE against it (keep momentum,
                           pull the trailer straight)
          ──► trailer settles
          ──► you BRAKE, manually        ◄─ window: settle → next reversal
curve N+1

window width = reversal period − trailer settling time           [DERIVED]
  → narrows with steeper grade and tighter curve spacing
  → the system's intervention consumed part of the window before
    you could use it


ESP event log (probable, format UNREAD):
  t0  roll intervention
  t1  driver throttle DURING intervention   → reads as driver fighting the system
  t2  driver brake                          → reads as delayed driver braking
actual sequence: correction of the intervention, then braking inside the
                 stable window
→ the case the machine_side_rule was written for: an early, correct action
  scored as error before the hazard window closed


sensor false trigger ──► docked as driver event
      ──► driver avoids the trigger's operating range (25–35)
      ──► hazard shifts to third parties (queue, passing, oncoming)
      ──► any resulting crash is attributed to the passing driver,
          not to the trigger or to the scoring rule


dataset                                        use
  earlier runs, normal speed + ESP events      trigger-onset speed per curve
  current runs, 25–35, no/fewer events         lower bound of trigger envelope
  → together: the speed at which the trigger starts firing on each grade
    = the measured edge of the validation envelope, per road     [PROPOSED]


ORDER 1  sensor false trigger → docked as a driver event
ORDER 2  truck at 25–35 → queue → impatient passes
ORDER 3  passer pulls out from behind the truck
         truck = occluder: blocks the passer's view of the road ahead
         buggy ahead or oncoming: slowest, least protected vehicle
         closing speed high, sight distance cut by the truck
         → near-miss or crash, the buggy absorbing the energy
                                                    [OBSERVED → DERIVED chain]


passer car      ~1.5 t   accelerating to clear the truck
buggy           horse + light frame, walking pace, no crush structure
truck           80,000 lb blind wall between them
→ the interaction happens where the passer has the least information
  and the buggy has no mass to absorb it


crash report → passing driver: unsafe pass           (recorded)
            → buggy: visibility/lighting             (often recorded)
            → truck: slow vehicle, lawful            (maybe noted)
            → ESP trigger + scoring rule             (never recorded)
the root input has no field in the crash form        [DERIVED]


GAP  buggy crash / near-miss locations  ×  truck grades where speed drops
     buggy crash data: exists at state level (WI, PA, OH)   [not searched]
     truck slowdown locations: your recordings + telematics
     join: UNMEASURED


LOOP CLOSURE
  trigger → slow truck → passer → incident AHEAD
                                     │
  truck, loaded, descending ─────────┘  now approaching the scene
     │
     ├─ LOAD      sudden stop on 9–13% serpentine: brake heat, load shift,
     │            delay on food freight (cold-chain clock running)
     ├─ MACHINE   hard braking on the grade = the exact regime where the
     │            trigger misbehaves; the ESP now acts during the
     │            emergency stop
     ├─ COMPANY   truck on scene: witness, delay, a claim that "the slow
     │            truck caused it" (liability exposure)
     └─ DRIVER    stop the rig on a grade, trailer behind, scene ahead
                                                    [DERIVED from OBSERVED]


where the cost lands               in the safety score?
  third parties (passer, buggy)    no
  load / delivery                  no  (logged as delay)
  equipment wear, brake heat       no  (maintenance line)
  company liability                no  (claims line)
  driver                           the docks avoided, while the cost
                                   paid elsewhere goes unrecorded
the score still reads: no event                             [DERIVED]


INTERSTATE INCIDENT                 TWO-LANE (DRIFTLESS) INCIDENT
  lanes left open: often 1+           lanes left: 0, both directions blocked
  shoulder: yes                       shoulder: little or none on grades
  detour: parallel routes             detour: ridge/valley terrain, few
                                        parallel roads → long reroutes
  responder access: separate          responders use the SAME blocked road
  queue: absorbed by capacity         queue on a grade: stopped trucks
                                        holding brakes, secondary-crash risk
                                                    [DERIVED — terrain-specific]


HOS window          keeps burning while parked in the queue
cold chain          reefer clock and fuel running
delivery windows    missed downstream, chain of reschedules
equipment           held on a grade, brake/park load
every other truck   same, for every carrier caught in the closure


GAP  do carrier cost models price the RELOCATED risk?
  likely counted:   claims when their truck is at fault
  likely not:       closures their truck contributed to but wasn't party to;
                    delay cost from someone else's incident ahead
  status:           UNMEASURED — not searched; carrier cost models
                    are internal


TRAPPED-RIG COST, per hour held                  STATUS
  mobility         no backing, no turnaround on   OBSERVED
                   a two-lane grade; the scene
                   sets the clock
  fuel, engine     ~0.8 gal/h idling             SECONDARY, as far as known,
  fuel, APU        ~0.2–0.3 gal/h                  not searched
  engine wear      idle hours logged as engine   industry rule of thumb:
                   hours with no miles             ~1 idle h ≈ 25–35 mi wear
                                                   [thin]
  aftertreatment   low-load idling → soot load,  DERIVED
                   DPF regen demand
  APU wear         runtime hours, service        DERIVED
                   intervals
  output           zero


cost of closure = Σ over every trapped vehicle (idle fuel + wear + HOS + cargo)
                × closure duration
closure duration on a two-lane grade ≫ interstate (single access, no detour)
→ one incident → a multi-vehicle, multi-carrier sink with no productive work


ROUTE REDUNDANCY TO THE DROP
  access roads          1–2                             OBSERVED
  alternate             ~3 h out of route               OBSERVED
  N_eff (routes)        ≈1: both roads cross the same terrain,
                        often the same grade class      DERIVED
  → one closure = every company truck on that approach
    trapped or diverted together


independent delays:   trucks fail one at a time; the fleet absorbs it
correlated closure:   k trucks × same hours × same drop
                      → the drop's receiving window missed by several
                        loads at once
                      → reroutes at +3 h each, burning HOS; some drivers
                        run out of hours before delivery
                      → dispatch reshuffles the next day's loads
                                                        [DERIVED]


single truck         ~ hours × (fuel + wear + HOS)
fleet on the route   ~ k × that, all simultaneous, plus a 3 h reroute each,
                       plus a receiver backlog
scoring view         0 events recorded for any of them


REGION               TERRAIN DRIVER            NETWORK SHAPE              STATUS
UP (Michigan)        snowbelt, long gaps       sparse, long single        general knowledge,
                     between towns             corridors                    not searched
Driftless            unglaciated steep         serpentine grades, valley  OBSERVED (operator)
                     valleys                   roads, buggy traffic
St. Croix riverway   river valley, bluffs      few crossings → funnels    general knowledge
Upper MN / WI        lakes, forest, wetland    roads route around water   general knowledge
                                               → few parallel links


V1  grade × curvature       serpentine descents              → trigger envelope
V2  access count            1–2 roads to many drops          → closure traps
V3  alternate distance      hours, not minutes               → reroute cost
V4  slow/vulnerable users   buggies, farm equipment,          → passing hazard
                            snowmobile crossings
V5  winter duration         ice on the same grades           → sensor degradation
                                                              + margin gone


assumed:   flat or gentle grade, gridded network, multi-lane, spare
           capacity, short detours       (where testing and fleet density are)
actual:    V1–V5 stacked in the same corridors
→ the regions with the least routing slack get the system tuned for
  the most slack                                    [DERIVED]


STATUS UPDATE
  V1–V5 pattern       OBSERVED across multiple regions, single operator
  scope               one driver, many corridors (N_regions > 1, N_operators = 1)
  next scope step     other operators on the same corridor classes
                      → does the same trigger/slowdown/pass chain show up?


# PROPOSED — one row per descent
DESCENT_RECORD = dict(
    region, road_id, grade_pct, curve_reversals,     # V1
    access_count_to_drop,                            # V2
    alternate_route_hours,                           # V3
    slow_users_present,        # buggy/farm/sled      V4
    surface_state,             # dry/wet/snow/ice     V5
    speed_mph, esp_event_ts,   # trigger timing
    gyro_file,                 # your cab trace
    downstream_event,          # pass/near-miss/incident/closure, or none
)
```
