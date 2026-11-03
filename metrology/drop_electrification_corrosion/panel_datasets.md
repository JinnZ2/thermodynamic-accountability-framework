# panel_datasets.md -- Task 3

Status: co-authored.

Outdoor exposure datasets, sorted by SHELTERED CONTROLS
(YES > PARTIAL > UNCLEAR > NO).

## Provenance: every field is (snippet)

Search-engine snippets only, 2026-11-03. No primary page was opened:
www.fhwa.dot.gov and ri.se (ICP Materials) were refused by this
session's egress policy, so the other primary hosts were not tried
(rosap.ntl.bts.gov, ntrs.nasa.gov, opus4.kobv.de, core.ac.uk). URLs are
the documents the snippets point to. NOT FOUND means not found in the
snippets, not absent from the source.

Tag for every table cell: OBSERVED** (search snippet, primary page not
opened). Cells marked CONFLICT or inferred in the notes: OBSERVED***.
Flags F2/F3 below are DERIVED** (an absence across snippets, not a
proven absence). Fill tests and nulls: gaps.md section T3.

## Flags (standing)

```text
F1  NONE of these log drop charge. They cannot confirm mechanism.
    They supply the real-world damage rate the lab must match.
F2  NO public dataset found with POLYMER-COATED COPPER + sheltered control.
    Closest pair:  bare Cu sheltered/open (ICP, #1)
                 + coated steel sheltered/open (AISI, #3)
F3  ICP painted steel is explicitly NOT sheltered (#15) -- "expected
    lifetime in sheltered position is much longer than 4 years".
    That sentence is itself a datum: shelter extends coating life.
F4  rain conductivity (bulk ion, not charge) was measured beside
    exposure at 2 sites: umezawa_12_2017.pdf (YNU, JP), imeko PWC-2006
    (Amazon, BR). These feed the ion axis (B2), not the charge axis.
```

## Table

```text
#   DATASET                         SHELTER   SUBSTRATE / COATING              TILT                    YEARS          METRIC                 ACCESS            RAIN/TOW LOGGED
--  ------------------------------  --------  -------------------------------  ----------------------  -------------  ---------------------  ----------------  ------------------------------
1   ICP Materials Cu/bronze (RISE)  YES box   Cu, bronze / bare                NOT FOUND               1987-present   mass loss              PDF tables; raw   wet-deposition term in DRF ->
                                                                                                                                             request (unconf)  precip likely; TOW NOT FOUND
2   BAM Germany (Babutzka 2022)     YES       steel Zn Cu Al / bare            ISO 9223-9226 (angle?)  1 yr + 5 yr    mass loss              open PDF          NOT FOUND
3   AISI coil-coated (Lawson 1998)  YES 4ft   steel / prepainted coil          5 deg; vert S;          3 yr           NOT FOUND (scribe/     open PDF          NOT FOUND
                                    overhang                                   vert N sheltered                       edge creep likely)
4   NRL Key West F-1/F-14           YES 4in   C1010 steel / bare               vertical                NOT FOUND      mass loss g/m2/d       proceedings;      30-min T/RH/rain/TOW on a
                                    acrylic                                                                                                  raw request       related AMPP rack (same rack?)
5   NJDOT bridges (Rutgers CAIT)    PARTIAL   steel / overcoat, zinc-rich      bridge geometry         NOT FOUND      NOT FOUND              PDF report        NOT FOUND
                                    fascia vs interior
6   FHWA-RD-92-055 weathering stl   UNCLEAR   weathering steel / maint coats   NOT FOUND               4 yr           NOT FOUND              PDF (rosap)       NOT FOUND
7   FHWA-HRT-11-046 one-coat        UNCLEAR   steel / 8 one-coat + controls    NOT FOUND               18-24 mo       D7087 creep, D5162     PDF tables        NOT FOUND
8   FHWA-HRT-12-044 100-year        UNCLEAR   steel / candidate systems        NOT FOUND               6-10 mo        D1654 D7087 D4541 ...  PDF               NOT FOUND
9   ISO CORRAG                      UNCLEAR   Al Cu steel Zn / bare            NOT FOUND               12 yr          mass loss              ASTM DS71 (paid)  T, RH implied (TOW model fit)
10  MICAT + PATINA                  UNCLEAR   steel Zn Cu Al bare; PATINA:     NOT FOUND               1988-1994;     mass loss; EIS         papers            met + SO2 + salinity; TOW likely
                                              10 paints, coil coats                                    PATINA 8 yr
11  NASA KSC Beachside              UNCLEAR   steel / NASA-STD-5008 candidates 30 vs 45 deg CONFLICT   18 mo - 5 yr   ASTM D610              NTRS summaries;   YES: weather stn incl. rainfall
                                                                                                                                             per-panel request kscweather archive
12  Kure Beach / ASTM G01 1976      UNCLEAR   41 materials; metallic-coated    NOT FOUND               21 yr          NOT FOUND              ASTM STP (paid)   NOT FOUND
13  Q-Lab FL (25d27'N 80d20'W) / AZ UNCLEAR   client panels                    45 deg S std            client         client                 PROPRIETARY       supplied to clients
14  FHWA LTBP / InfoBridge + NBI    UNCLEAR   bridge elements CS1-CS4          n/a                     NBI years      condition state        download          NOT FOUND
15  ICP painted / coil-coated steel NO        steel / alkyd 2x~80 um; alkyd    NOT FOUND               1997-2001; 8y  spread from cut        PDF (nilu)        as #1
                                              melamine coil
--  Guttman & Sereda STP 435 (1959) unranked  steel Cu Zn / bare               NOT FOUND               NOT FOUND      mass loss + PANEL TOW  ASTM STP          panel TOW, SO2, Cl MEASURED
```

Site coordinates: NOT FOUND for all except Q-Lab Florida (stated
25d27'N 80d20'W). Task 2 needs coordinates; ICP site table is at
researchgate.net/publication/319214164 (not opened).

## Sources (snippet targets)

```text
1   ncbi.nlm.nih.gov/pmc/articles/PMC5578335/ ; hindawi.com/journals/ijc/2012/496321/
    ri.se/en/icp-materials/documents/icp-materials-reports
2   opus4.kobv.de/opus4-bam/files/56509/Mater+Corros_2022_Babutzka.pdf
3   core.ac.uk/download/229099574.pdf ; scholarsmine.mst.edu (isccss article 1548)
4   sto.nato.int ... MP-AVT-373-10P.pdf ; mdpi.com/2624-5558/4/1/1
    store.ampp.org/naval-aviation-environmental-severity-correlation-50444
5   njdottechtransfer.net ... FHWA-NJ-2018-006.pdf ; trid.trb.org/View/2132216
6   rosap.ntl.bts.gov/view/dot/861
7   fhwa.dot.gov/publications/research/infrastructure/bridge/11046/11046.pdf
8   fhwa.dot.gov/publications/research/infrastructure/structures/bridge/12044/12044.pdf
9   store.astm.org/ds71-eb.html
10  revistademetalurgia.revistas.csic.es (articles 725, 1120)
11  public.ksc.nasa.gov/corrosion/atmospheric-exposure/ ; kscweather.ksc.nasa.gov/wxarchive/Reports/Corrosion
    ntrs.nasa.gov/api/citations/20140012573/downloads/20140012573.pdf
12  store.astm.org/stp10905s.html
13  q-lab.com document library LL-9025, LL-9000
14  infobridge.fhwa.dot.gov ; fhwa.dot.gov/bridge/nbi/element.cfm
15  nilu.no/dnn-file/39-2000-jfh/?ext=pdf
```

## Next

```text
1  unblock hosts; open #1 env-parameter table, #3 data tables, #7/#8 rack geometry, #2
2  ask RISE whether any lacquered / polymer-coated Cu was ever exposed (fills F2)
3  #4 + #11 are the only sites with logged rainfall beside panels -> first
   Task 2 targets once coordinates are confirmed
```
