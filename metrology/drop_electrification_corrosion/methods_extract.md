# methods_extract.md -- Task 1

Paper: Ni et al., "Spontaneously charged water drops induce corrosion",
Nature 2026, DOI 10.1038/s41586-026-10941-6.

## State of this extraction: BLOCKED

The work order allows two marks: MEASURED and NOT REPORTED. Neither can
be applied honestly yet. NOT REPORTED means "read the full methods + SI
and it is absent"; that read has not happened. A third mark is used:

```text
NOT ACCESSED   the text that would contain the value was not reachable.
               Not a claim about the paper.
```

Attempted 2026-11-03, all refused by this session's egress policy
(proxy CONNECT 403 / DNS outside allowlist):
www.nature.com, doi.org, api.crossref.org, www.ebi.ac.uk (Europe PMC),
export.arxiv.org, www.uni-bonn.de. Preprint existence: unknown.
To unblock: allow www.nature.com and static-content.springer.com (SI PDF).

## Fields

```text
FIELD                                   MARK           VALUE
salt identity                           NOT ACCESSED   -
salt concentration                      NOT ACCESSED   -
drop volume                             NOT ACCESSED   -   (work order states 35 uL; unverified against paper)
slide length                            NOT ACCESSED   -   (work order states 4 cm; unverified)
slide speed                             NOT ACCESSED   -
release height                          NOT ACCESSED   -
surface tilt angle                      NOT ACCESSED   -
ambient temperature                     NOT ACCESSED   -
relative humidity                       NOT ACCESSED   -
humidity controlled / logged / neither  NOT ACCESSED   -
drop rate (drops/min)                   NOT ACCESSED   -
total drop count per condition          NOT ACCESSED   -   (work order states ~3000; unverified)
substrate metals                        NOT ACCESSED   -
coating type                            NOT ACCESSED   -   (work order: Teflon, polystyrene; unverified)
coating thickness (+ how measured)      NOT ACCESSED   -
damage quantification method            NOT ACCESSED   -
deionized / low-ion control             NOT ACCESSED   -
drop charge + instrument                NOT ACCESSED   -   (work order states 0.2-2 nC; unverified)
grounding / charge-neutralized control  NOT ACCESSED   -
lab-to-outdoor equivalence statement    NOT ACCESSED   -
```

## Secondary coverage seen (NOT entered as values)

Search-engine summaries of press coverage (ScienceDaily, Nature Asia,
Uni Bonn, idw-online, Gigazine), none opened directly. Recorded only so
the next reader knows where they disagree; none of these may be cited
as the paper's numbers.

```text
total drop count     press: 3,000 (most); 10,000 (Gigazine)   CONFLICT
drop potential       press: ">1 kV" vs "up to 9,000 V"        CONFLICT
uncharged-drop ctrl  press: "no damage" -- method of uncharging not stated
damage depth         press: ">1 mm" after long exposure -- method not stated
```

The salt-vs-charge question (WORK_ORDER Task 1 rationale) is untouched:
whether an uncharged-but-salty control exists, and how drops were made
uncharged, are exactly the two fields that would scope it.
