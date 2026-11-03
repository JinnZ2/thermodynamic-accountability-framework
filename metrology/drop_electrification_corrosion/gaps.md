# gaps.md

Status: co-authored.

Every field that is NOT REPORTED, NOT ACCESSED, NOT FOUND, stubbed, or
otherwise missing. For each: the cleanest test that fills it, and the
null result that would rule it out (show the field or assumption does
not matter, or that the gap is a real absence).

Format per row:
```text
ID  FIELD
    FILL  cleanest test or read
    NULL  result that rules it out / closes it as irrelevant
```

## Bottleneck order

```text
B1  counting rule   impact vs runoff drop counts differ x20-160 (DERIVED)  -> T2.4-T2.6
B2  ion load        decides mechanism class; no per-site rain chemistry   -> T1.1, T2.9, H1
B3  shelter         only paired sheltered/open isolates rain              -> T3.3, T3.4
B4  network         every OBSERVED field below is blocked by egress, not by absence
```

## T1 -- paper methods (all NOT ACCESSED; read the paper + SI first)

The first FILL for every T1 row is the same: read Methods + SI of
DOI 10.1038/s41586-026-10941-6. The FILL listed is the bench test to run
if the paper does NOT REPORT the field.

```text
T1.1  salt identity + concentration
      FILL  repeat the lab run at 3+ concentrations of one salt (e.g. NaCl at 0, 1, 10, 100 mM)
            at fixed charge; then swap salt at fixed ionic strength
      NULL  damage independent of concentration at fixed charge -> salt is not the driver
            at lab scale; field index needs no ion axis

T1.2  drop volume            FILL  gravimetric: weigh N drops from the dispenser
                             NULL  damage per drop flat across 10-50 uL -> size term drops out of weight()
T1.3  slide length           FILL  vary 1-8 cm at fixed drop/charge, record q and damage
                             NULL  q and damage flat in length -> slide_exponent = 0
T1.4  slide speed            FILL  high-speed video along the track
                             NULL  damage flat across tilt-induced speed range -> speed not a parameter
T1.5  release height         FILL  vary height at fixed everything else
                             NULL  q flat in height -> impact energy not in weight()
T1.6  tilt angle             FILL  run at 2 tilts bracketing outdoor rack angles (30, 45 deg)
                             NULL  same damage per drop at both -> tilt only enters via cos() projection
T1.7  ambient temperature    FILL  climate-chamber runs at 10, 25, 40 C
                             NULL  q and damage flat in T -> t_slope_per_c = 0
T1.8  RH (+ controlled/logged)
      FILL  chamber runs at RH 30, 60, 90 % with q measured per drop; this sets weight(RH)
      NULL  q and damage flat across RH -> weight() collapses to a constant; index == rain depth
T1.9  drop rate              FILL  vary interval (1 s to 10 min) at fixed count
                             NULL  damage depends on count only -> no drying/recovery term needed
T1.10 total count per condition
      FILL  dose series: pinhole onset vs count (500..10000)   (press reports 3000 and 10000: CONFLICT)
      NULL  no monotonic onset -> "drops to pinhole" is not a usable dose unit
T1.11 substrate metals       FILL  run on Cu, steel, Zn, Al under same coating
                             NULL  Cu-only effect -> outdoor steel datasets (most of T3) cannot be matched
T1.12 coating type + thickness (+ method)
      FILL  profilometry / ellipsometry thickness; run 2 thicknesses
      NULL  pinhole count independent of thickness -> defect-site, not penetration, process
T1.13 damage quantification  FILL  state metric (count, area, depth) + imaging (optical/SEM/EIS)
                             NULL  n/a: without it lab and field metrics cannot be put on one axis
T1.14 DI / low-ion control   FILL  identical run with deionized water (charge typically HIGHER)
      NULL  DI drops produce no damage despite higher charge -> solute required (supports
            electrochemistry class over charge separation alone)
T1.15 drop charge + instrument
      FILL  Faraday cup / electrometer at track end, per drop
      NULL  damage uncorrelated with measured q across drops -> charge not the dose variable
T1.16 grounding / neutralized control
      FILL  same salt drops, grounded substrate or ionizer-neutralized drops
      NULL  neutralized salty drops damage equally -> charge not required (mechanism class:
            solute electrochemistry). Cleanest single discriminator in this file.
T1.17 lab-to-outdoor equivalence statement
      FILL  read discussion section
      NULL  none stated -> field relevance stays INFERRED (as tagged everywhere here)
```

## T3 -- outdoor datasets (all OBSERVED** snippet-only)

```text
T3.1  site coordinates (13 of 14 sites NOT FOUND)
      FILL  open the report site tables (ICP: researchgate 319214164; AISI PDF; NRL, KSC, LaQue)
      NULL  site published only as a city -> distance_km gets a city-radius floor, band WIDE
T3.2  site elevation (13 of 14 NOT FOUND)
      FILL  report table, else a DEM lookup at confirmed coordinates (DERIVED)
      NULL  |site - station| < 50 m everywhere -> elevation term drops from the band
T3.3  sheltered controls on POLYMER-COATED Cu (none found)
      FILL  ask RISE (ICP Materials) whether lacquered/coated Cu was ever exposed sheltered
      NULL  confirmed never exposed -> no direct field target; bracket with bare Cu (ICP #1)
            + coated steel (AISI #3)
T3.4  sheltered status UNCLEAR rows (#6-#14)
      FILL  read rack/position descriptions (FHWA 11-046, 12-044, RD-92-055; KSC; LaQue)
      NULL  open-only -> row cannot separate rain; keep as damage-rate target only
T3.5  panel tilt (NOT FOUND most rows; KSC 30 vs 45 deg CONFLICT)
      FILL  rack spec in report; KSC site documentation
      NULL  tilt known to be ISO default 45 deg across rows -> cos() term is a constant
T3.6  damage metric (NOT FOUND #3, #5, #6, #12)
      FILL  report methods sections
      NULL  metrics incompatible across rows -> gradient_check runs per metric only (as built)
T3.7  rain / time-of-wetness logged at site
      FILL  ICP env-parameter table; KSC wxarchive; NRL 30-min log; STP 435 panel TOW
      NULL  not logged -> nearest-station substitution is the only path (band applies)
T3.8  raw data access (most request-only / paywalled / proprietary)
      FILL  data requests to RISE, NRL, NASA KSC; ASTM DS71 purchase
      NULL  refused -> only report-table summary rates usable; n per metric shrinks
```

## T2 -- pipeline parameters (stubs; no number is a default)

```text
T2.1  weight(RH, T) form + params  (rh_ref_pct, rh_form, rh_slope_per_pct, rh_half_pct,
                                    t_ref_c, t_slope_per_c)
      FILL  T1.7 + T1.8 bench series -> fit q(RH, T) on LAB data only (never on field damage:
            that would make the built-in check circular)
      NULL  q flat in RH and T -> weight == const; index carries no information beyond rain depth
T2.2  wet-hour threshold (WET_THRESHOLD_MM = 0.0, named)
      FILL  rerun at 0.0, 0.2, 1.0 mm
      NULL  index ranks of sites unchanged -> threshold not load-bearing
T2.3  multi-hour precip spreading (frac_rain_from_multihour column)
      FILL  compare a station-year with dense 1-h reports vs same year using only 6-h totals
      NULL  index within band at frac -> 1 -> spreading acceptable
T2.4  drop_volume_ul (sliding drop volume outdoors)
      FILL  photograph runoff drops on a tilted coated panel in rain; volume from contact width
      NULL  outdoor slide-drop volume ~ lab 35 uL -> lab volume transfers
T2.5  catchment_m2 (panel area feeding one slide track)
      FILL  dye-trace runoff paths on a rack panel
      NULL  n/a: a geometry choice; must be declared, never defaulted
T2.6  runoff_fraction (share leaving as discrete sliding drops vs film/splash/evaporation)
      FILL  collect and count drops at panel lower edge vs gauge rain on the panel area
      NULL  fraction ~1 -> runoff rule == volume rule; fraction << 1 -> drop count overstated
T2.7  counting rule itself (impact vs runoff; x20-160 apart)
      FILL  T2.6 field count; lab equivalent: is damage per IMPACT or per SLIDE?
      NULL  damage scales with slides only -> impact count irrelevant (and vice versa)
T2.8  uncertainty band rule  (PROPOSED***, uncalibrated)
      FILL  co-located gauge at 2+ panel sites vs nearest station; fit band vs distance/dz/terrain
      NULL  station-site index difference does not grow with distance -> band rule is decoration
T2.9  ion_factor  (PROPOSED*** slot, not in the index)
      FILL  NADP/NTN weekly Na+, Cl- at sites; T1.1 bench series sets the form
      NULL  T1.1 shows no concentration dependence -> slot stays empty
T2.10 station selection (nearest with >= min_years record)
      FILL  compare index from nearest vs 2nd-nearest station at the same site
      NULL  difference inside band -> nearest is adequate
T2.11 NOAA parser vs live data  (fixture-tested only)
      FILL  run on one real station-year; compare annual rain to the station's published total
      NULL  within a few % -> parser trusted
```

## CHECK -- built-in gradient check (NOT_TESTABLE)

```text
C1  per-site damage rate on one metric, >= 5 TIGHT and >= 5 WIDE sites
    FILL  T3.1 coordinates + T3.6 metric + T3.8 data, then run with NOAA reachable
    NULL  rho_TIGHT not > rho_WIDE by >= 0.2 -> index not measuring what it claims
          (verdict NO_GRADIENT; recorded, not tuned away)
C2  confound: tight sites (flat, near airports) may differ in coating system / age / SO2
    FILL  stratify by coating system within metric; check SO2/chloride per site (ICP/MICAT carry these)
    NULL  gradient survives stratification -> confound not driving it
```

## H -- carried hypothesis (PROPOSED***, not tested here)

```text
H1  charge separation peaks in low-conductivity water while electrochemical attack rises
    with ions -> damage per drop worst at mid ion concentration.
    FILL  bench: damage per drop vs ion concentration (0 .. seawater) with q measured per drop
    NULL  monotonic damage vs concentration (no interior maximum) -> H1 rejected
    Field echo (only after bench): mid-salinity sites (near-coastal, not beachfront) over-
    represented among high damage-per-index sites. INFERRED even if seen.
```
