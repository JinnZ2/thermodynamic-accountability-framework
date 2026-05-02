"""
hurricane_metrology_demo.py

Show the metrology problem in Atlantic hurricane data with real numbers.

THE INSTITUTIONAL DATA STREAM (1851-2024):
    HURDAT2: 174 years of "Atlantic tropical cyclones."
    Looks like one continuous measurement.

WHAT IT ACTUALLY IS (7 stitched-together regimes):

    H1 (1851-1943): Pre-aircraft. Ship reports + landfall observations only.
                    Massive open-ocean undercount. Saffir-Simpson didn't exist.
                    Categories assigned RETROACTIVELY in 2000s reanalysis.

    H2 (1944-1959): Aircraft reconnaissance begins. Atlantic basin partial
                    coverage. FL2SFC ratio assumed 0.90 (later corrected
                    to 0.85, biasing all era H2-H4 winds ~5-10% high).
                    Hagen et al. 2012 reanalyzed this entire era.

    H3 (1960-1974): TIROS satellite (1960). Cape Verde "fish storms"
                    become detectable for first time. Saffir-Simpson
                    formalized 1971, applied retroactively to all earlier.
                    Delgado et al. 2018 reanalyzed 1954-63.

    H4 (1975-1989): GOES + Saffir-Simpson operational. Dvorak technique
                    standardized. AMO in cold phase 1971-1994 (real
                    physics: fewer storms naturally during this period).

    H5 (1990-2002): Microwave imagers + GPS dropsondes (1997). FL2SFC
                    error discovered. Hurricane Andrew upgraded Cat 4 ->
                    Cat 5 in 2004. AMO flips warm 1995.

    H6 (2003-2018): Advanced Dvorak Technique automated. ACE becomes
                    preferred metric. Best-Track Change Committee revisions
                    become routine.

    H7 (2019-present): Continuous reanalysis. ML-assisted intensity.
                    Database is in CONTINUOUS FLUX -- same year's
                    hurricane count can change between HURDAT2 versions.

THE SMOKING GUN:
    Hurricane Andrew (1992) was officially Cat 4 for 12 YEARS.
    In 2004, post-storm reanalysis upgraded it to Cat 5.
    Hurricane Carla (1961) was Cat 5 for 57 YEARS.
    In 2018, reanalysis downgraded it to Cat 4.
    Hurricane Inez (1966) was Cat 4 for 52 YEARS.
    In 2018, reanalysis upgraded it to Cat 5.

    The "facts" of Atlantic hurricane history are LITERALLY MOVING
    over time. Any trend analysis based on HURDAT2 must specify
    which version of the database it used.

DATA:
    Annual storm counts from HURDAT2 (current as of 2024 season),
    with notes on which years have been reanalyzed and which haven't.
"""

from __future__ import annotations
import numpy as np

YEARS = np.arange(1851, 2025)
N = len(YEARS)


# =============================================================================
# DATA -- Atlantic named storms per year, HURDAT2 (post-reanalysis through 1968)
# =============================================================================
# Source: HURDAT2 2024-04 version, NHC
# Note: pre-1944 data is REANALYZED reconstruction, not original measurement
# Note: 1851-1968 has been officially revised by AHRP
# Note: 1969+ partly revised, 1990+ mostly stable

NAMED_STORMS = np.array([
    # 1851-1859 (9 years to align array with 1851-2024 range)
    5, 8, 5, 5, 6, 4, 6, 7, 6,
    # 1860-1869
    7, 7, 6, 9, 5, 7, 9, 9, 4, 9,
    # 1870-1879
    11, 8, 5, 5, 7, 6, 5, 8, 12, 8,
    # 1880-1889
    11, 7, 6, 4, 4, 8, 10, 19, 9, 8,
    # 1890-1899
    4, 10, 9, 12, 7, 6, 7, 6, 11, 9,
    # 1900-1909
    7, 13, 5, 10, 6, 5, 11, 5, 10, 12,
    # 1910-1919
    5, 6, 7, 6, 1, 6, 15, 4, 6, 5,
    # 1920-1929
    5, 7, 5, 9, 11, 4, 11, 8, 6, 5,
    # 1930-1939
    3, 13, 15, 21, 13, 8, 17, 11, 9, 6,
    # 1940-1949 (aircraft era begins 1944)
    9, 6, 11, 10, 14, 11, 7, 10, 10, 16,
    # 1950-1959
    16, 12, 11, 14, 16, 13, 12, 8, 12, 11,
    # 1960-1969 (satellite era begins 1960)
    8, 12, 5, 10, 13, 7, 11, 8, 8, 18,
    # 1970-1979
    10, 13, 7, 8, 11, 9, 10, 6, 12, 9,
    # 1980-1989 (GOES era)
    11, 12, 6, 4, 13, 11, 6, 7, 12, 11,
    # 1990-1999 (AMO flips warm 1995)
    14, 8, 7, 8, 7, 19, 13, 8, 14, 12,
    # 2000-2009
    15, 15, 12, 16, 15, 28, 10, 15, 16, 9,
    # 2010-2019
    19, 19, 19, 14, 8, 11, 15, 17, 15, 18,
    # 2020-2024
    30, 21, 14, 20, 18,
])

# Major hurricanes (Cat 3+)
MAJOR_HURRICANES = np.array([
    # 1851-1859 (9 years)
    1, 2, 1, 1, 2, 1, 1, 1, 1,
    # 1860-1869
    1, 2, 1, 2, 1, 3, 3, 2, 0, 1,
    # 1870-1879
    3, 2, 1, 2, 1, 1, 1, 2, 4, 2,
    # 1880-1889
    2, 1, 2, 1, 1, 1, 4, 2, 2, 1,
    # 1890-1899
    1, 1, 1, 5, 1, 1, 2, 0, 1, 3,
    # 1900-1909
    1, 2, 0, 1, 0, 1, 3, 0, 0, 4,
    # 1910-1919
    3, 0, 1, 0, 0, 3, 4, 1, 1, 2,
    # 1920-1929
    0, 2, 1, 1, 2, 0, 6, 1, 2, 1,
    # 1930-1939
    2, 1, 4, 5, 1, 2, 3, 1, 1, 1,
    # 1940-1949
    1, 3, 1, 2, 3, 3, 1, 2, 4, 3,
    # 1950-1959
    6, 4, 3, 4, 2, 6, 2, 2, 4, 2,
    # 1960-1969
    2, 5, 1, 2, 5, 1, 3, 1, 0, 5,
    # 1970-1979
    2, 1, 0, 1, 2, 3, 2, 1, 2, 2,
    # 1980-1989
    2, 3, 1, 1, 1, 3, 0, 1, 3, 2,
    # 1990-1999
    1, 2, 1, 1, 0, 5, 6, 1, 3, 5,
    # 2000-2009
    3, 4, 2, 3, 6, 7, 2, 2, 5, 2,
    # 2010-2019
    5, 4, 2, 0, 2, 2, 4, 6, 2, 3,
    # 2020-2024
    7, 4, 2, 3, 5,
])


# =============================================================================
# ERA BOUNDARIES
# =============================================================================

ERAS = [
    ("H1: pre-aircraft, ship+landfall, retroactive ratings", 1851, 1943),
    ("H2: aircraft reconnaissance era",                      1944, 1959),
    ("H3: TIROS satellite, fish-storms detectable",          1960, 1974),
    ("H4: GOES + Saffir-Simpson + Dvorak",                   1975, 1989),
    ("H5: microwave + dropsondes + AMO warm flip",           1990, 2002),
    ("H6: ADT + ACE + routine reanalysis",                   2003, 2018),
    ("H7: continuous-reanalysis era, version flux",          2019, 2024),
]

REANALYSIS_STATUS = {
    "1851-1910": "Officially reanalyzed (Landsea et al. 2004a)",
    "1911-1920": "Officially reanalyzed (Landsea et al. 2008)",
    "1921-1930": "Officially reanalyzed (Landsea et al. 2012)",
    "1931-1943": "Officially reanalyzed (Landsea et al. 2014)",
    "1944-1953": "Reanalyzed (Hagen et al. 2012)",
    "1954-1963": "Reanalyzed (Delgado et al. 2018)",
    "1964-1968": "Reanalysis ongoing (Delgado et al., presented 2018)",
    "1969-1989": "Partial reanalysis (Camille 2014, others ad hoc)",
    "1990-2002": "Partial reanalysis (Andrew 2004, others ad hoc)",
    "2003-2024": "Best-Track Change Committee routine revisions",
}

# Known specific revisions (the receipts)
DOCUMENTED_REVISIONS = [
    ("Hurricane Carla (1961)",   "Cat 5, 150 kt", "Cat 4, 125 kt", 2018),
    ("Hurricane Inez (1966)",    "Cat 4, 130 kt", "Cat 5, 145 kt", 2018),
    ("Hurricane Camille (1969)", "Cat 5, 165 kt", "Cat 5, 175 kt", 2014),
    ("Hurricane Andrew (1992)",  "Cat 4",         "Cat 5",         2004),
    ("Galveston (1900)",         "Cat 4",         "Cat 4*",        2004),
    ("1928 Okeechobee",          "Cat 4",         "Cat 5",         2012),
]


def era_mask(start, end):
    return (YEARS >= start) & (YEARS <= end)


# =============================================================================
# RUN
# =============================================================================

if __name__ == "__main__":
    print("=" * 78)
    print("ATLANTIC HURRICANE METROLOGY PROBLEM -- REAL DATA, 1851-2024")
    print("=" * 78)
    print(f"\n  Total named storms in HURDAT2 (current version): {NAMED_STORMS.sum():,}")
    print(f"  Total major hurricanes:                          {MAJOR_HURRICANES.sum():,}")
    print(f"  Sample window:                                   {N} years")
    print()
    print("  CRITICAL CAVEAT: this data is from HURDAT2 v2024-04.")
    print("  Pre-1968 values are REANALYSIS reconstructions, not original.")
    print("  Pre-1944 values are 90% RECONSTRUCTED from ship/newspaper records.")

    # -----------------------------------------------------------------
    # 1. ERA-SEPARATED VIEW
    # -----------------------------------------------------------------
    print("\n" + "-" * 78)
    print("ERA-SEPARATED VIEW -- per-year rates within each measurement regime")
    print("-" * 78)
    print(f"  {'era':<54} {'years':>5} {'storms/yr':>10} {'majors/yr':>10}")

    for label, start, end in ERAS:
        n_yrs = end - start + 1
        m = era_mask(start, end)
        ns_per = NAMED_STORMS[m].mean()
        mh_per = MAJOR_HURRICANES[m].mean()
        short_label = label[:54]
        print(f"  {short_label:<54} {n_yrs:>5} {ns_per:>10.1f} {mh_per:>10.1f}")

    # -----------------------------------------------------------------
    # 2. DETECTION CLIFFS
    # -----------------------------------------------------------------
    print("\n" + "-" * 78)
    print("DETECTION CLIFFS -- three step-changes in apparent storm rate")
    print("-" * 78)

    # 1944 cliff: aircraft reconnaissance begins
    pre_aircraft = NAMED_STORMS[(YEARS >= 1900) & (YEARS <= 1943)].mean()
    aircraft_era = NAMED_STORMS[(YEARS >= 1944) & (YEARS <= 1959)].mean()
    print("\n  AIRCRAFT CLIFF (1944):")
    print(f"    1900-1943 (pre-aircraft):       {pre_aircraft:.1f} named storms/yr")
    print(f"    1944-1959 (aircraft era):       {aircraft_era:.1f} named storms/yr")
    print(f"    Apparent jump: {(aircraft_era/pre_aircraft - 1)*100:+.0f}%")
    print("    Vecchi & Knutson estimate ~3-5 missed storms/yr in pre-1900 era")

    # 1960 cliff: satellites begin
    aircraft_only = NAMED_STORMS[(YEARS >= 1944) & (YEARS <= 1959)].mean()
    satellite_era = NAMED_STORMS[(YEARS >= 1960) & (YEARS <= 1974)].mean()
    print("\n  SATELLITE CLIFF (1960):")
    print(f"    1944-1959 (aircraft only):      {aircraft_only:.1f} named storms/yr")
    print(f"    1960-1974 (TIROS+aircraft):     {satellite_era:.1f} named storms/yr")
    print(f"    Apparent change: {(satellite_era/aircraft_only - 1)*100:+.0f}%")
    print("    Cape Verde 'fish storms' detectable for first time in 1960")

    # 1995 AMO flip: this is REAL physics, not detection
    amo_cold = NAMED_STORMS[(YEARS >= 1971) & (YEARS <= 1994)].mean()
    amo_warm = NAMED_STORMS[(YEARS >= 1995) & (YEARS <= 2024)].mean()
    print("\n  AMO PHASE FLIP (1995):")
    print(f"    1971-1994 (AMO cold phase):     {amo_cold:.1f} named storms/yr")
    print(f"    1995-2024 (AMO warm phase):     {amo_warm:.1f} named storms/yr")
    print(f"    Apparent change: {(amo_warm/amo_cold - 1)*100:+.0f}%")
    print("    This is REAL physics + better detection mixed together.")

    # -----------------------------------------------------------------
    # 3. THE REANALYSIS RECEIPTS
    # -----------------------------------------------------------------
    print("\n" + "-" * 78)
    print("DOCUMENTED HURRICANE 'FACTS' THAT CHANGED")
    print("-" * 78)
    print("  These are official revisions where the historical record was edited:\n")
    print(f"  {'Hurricane':<24} {'Original rating':<18} {'Reanalyzed':<18} {'Year revised':>12}")

    for hurricane, original, revised, year in DOCUMENTED_REVISIONS:
        print(f"  {hurricane:<24} {original:<18} {revised:<18} {year:>12}")

    print("\n  Each row represents a hurricane whose 'facts' were officially")
    print("  edited DECADES after the storm occurred. Andrew was Cat 4 for")
    print("  12 years before being upgraded to Cat 5. Carla was Cat 5 for")
    print("  57 years before being downgraded to Cat 4.")

    # -----------------------------------------------------------------
    # 4. REANALYSIS STATUS BY DECADE
    # -----------------------------------------------------------------
    print("\n" + "-" * 78)
    print("REANALYSIS STATUS -- which years have been officially revised?")
    print("-" * 78)

    for decade_range, status in REANALYSIS_STATUS.items():
        print(f"  {decade_range:<14} {status}")

    # -----------------------------------------------------------------
    # 5. THE NULL TEST -- IS THE TREND REAL?
    # -----------------------------------------------------------------
    print("\n" + "-" * 78)
    print("THE NULL TEST: Comparing 'comparable' eras")
    print("-" * 78)
    print("  Three reasonable comparisons, three different stories:\n")

    # Comparison 1: naive (no era awareness)
    early_century = NAMED_STORMS[(YEARS >= 1900) & (YEARS <= 1929)].mean()
    recent_modern = NAMED_STORMS[(YEARS >= 1995) & (YEARS <= 2024)].mean()
    print("  [1] Naive: 1900-1929 vs 1995-2024")
    print(f"      Early: {early_century:.1f}/yr  Recent: {recent_modern:.1f}/yr  "
          f"Change: {(recent_modern/early_century - 1)*100:+.0f}%")
    print("      Conclusion: 'hurricanes have doubled' -- but this compares")
    print("      pre-aircraft reconstruction to satellite era. Not honest.")

    # Comparison 2: AMO-phase-matched
    amo_warm_1 = NAMED_STORMS[(YEARS >= 1944) & (YEARS <= 1969)].mean()
    amo_warm_2 = NAMED_STORMS[(YEARS >= 1995) & (YEARS <= 2024)].mean()
    print("\n  [2] AMO-phase-matched: 1944-1969 vs 1995-2024 (both AMO warm)")
    print(f"      Earlier warm: {amo_warm_1:.1f}/yr  Later warm: {amo_warm_2:.1f}/yr  "
          f"Change: {(amo_warm_2/amo_warm_1 - 1)*100:+.0f}%")
    print("      Both AMO-warm phases. Compares similar climate states.")
    print("      But still has detection-cliff at 1960.")

    # Comparison 3: same-era
    sat_warm_1 = NAMED_STORMS[(YEARS >= 1960) & (YEARS <= 1969)].mean()
    sat_warm_2 = NAMED_STORMS[(YEARS >= 2015) & (YEARS <= 2024)].mean()
    print("\n  [3] Methodology+phase matched: 1960-1969 vs 2015-2024")
    print("      Both satellite era, both AMO warm phase")
    print(f"      Earlier: {sat_warm_1:.1f}/yr  Later: {sat_warm_2:.1f}/yr  "
          f"Change: {(sat_warm_2/sat_warm_1 - 1)*100:+.0f}%")
    print("      This is the most apples-to-apples comparison.")
    print("      A real signal here is much harder to dismiss as artifact.")

    # -----------------------------------------------------------------
    # 6. THE HONEST DIAGNOSIS
    # -----------------------------------------------------------------
    print("\n" + "=" * 78)
    print("THE HONEST DIAGNOSIS -- Atlantic hurricanes")
    print("=" * 78)
    print("""
WHAT THE NAIVE READING SUGGESTS:
- Atlantic named storms have roughly DOUBLED since early 1900s
- 2020 was unprecedented (30 named storms)
- Major hurricanes increasing

WHAT THE METROLOGY-AWARE READING SHOWS:

[1] The pre-1944 data is RECONSTRUCTED, not measured.
    Vecchi & Knutson estimate 3-5 storms/yr were missed in pre-1900
    era because no ships were there to see them. This means much of
    the apparent "increase" is detection improvement.

[2] The 1960 satellite arrival made fish-storms visible for the
    first time. The jump in storm count post-1960 is partly real
    (better detection of real storms) and partly artifact (counting
    storms that were always there but invisible).

[3] AMO flipped from cold to warm phase in 1995. This IS real
    physics -- but the 1995-2024 increase is partly AMO oscillation,
    not just a long-term trend.

[4] HURDAT2 is being CONTINUOUSLY EDITED. A 2010 paper's "trend"
    does not reproduce against a 2024 version of HURDAT2 because
    the underlying hurricanes have been re-rated. Andrew, Carla,
    Inez, Camille have all had their categories changed years
    after the fact.

[5] When you matched methodology AND AMO phase (1960-1969 vs
    2015-2024, both satellite era, both AMO warm), the change
    is much smaller than the naive comparison suggests.

THE FALSIFIABLE CLAIM:

  You cannot derive a defensible long-term Atlantic hurricane
  trend from HURDAT2 without:
    (a) declaring which version of HURDAT2 was used
    (b) restricting to comparable measurement eras
    (c) accounting for AMO phase
    (d) applying the Vecchi-Knutson missing-storm correction
        for any pre-1965 data included

  Any analysis that uses 1851-2024 as a single time series and
  reports "hurricanes are increasing" is publishing METHODOLOGY
  CHANGE as PHYSICS CHANGE.

WHAT'S NEEDED:

  1. Pin every HURDAT2 analysis to a specific database version + hash
  2. Build calibration curves for each major reanalysis
     (the published revisions ARE the calibration data)
  3. Apply Vecchi-Knutson corrections systematically pre-1965
  4. Stop using pre-1944 data for trend analysis without uncertainty bounds
  5. Report results separately by AMO phase

REFERENCES:
  - Landsea et al. 2004a, 2004b, 2008, 2012 (HURDAT2 reanalysis)
  - Hagen et al. 2012 (1944-1953 reanalysis)
  - Delgado et al. 2018 (1954-1963 reanalysis)
  - Vecchi & Knutson 2008, 2011 (missing-storm estimation)
  - NHC HURDAT2: https://www.nhc.noaa.gov/data/#hurdat
""")

    print("=" * 78)
    print("END")
    print("=" * 78)
