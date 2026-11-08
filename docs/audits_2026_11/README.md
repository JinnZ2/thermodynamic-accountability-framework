# audits_2026_11

Co-authored (JinnZ2 + Claude) audit documents, delivered as PDFs and kept
verbatim. CC0. Status tags inside each file are the file's own
(OBSERVED / DERIVED / PROPOSED / MEASURED / UNMEASURED); nothing here
was re-checked when filed.

| File | Dated | Pages | Subject | sha256 |
|---|---|---|---|---|
| decision_model_blind_spots_jev_llm.pdf | 2026-11-07 | 2 | Welded terms in a "hallucination-free" decision-model claim; LLM + decision-model combination gaps; 5 PROPOSED blind-spot reducers | 015d677a6f9452d9cbf944bbdfc307baab5833ec27f268f1f64fd2cd871bcd3f |
| unaudited_ai_claims_civilian_infrastructure.pdf | 2026-11-07 | 3 | Warning (not a forecast): AI capability claims entering infrastructure procurement; cascade mechanism; candidate threshold variables, all unmeasured | 4966c9a0607c25f39ae3bcdc1ed41972df4ae6e06ec7f25043f43ccf2e83f3bf |
| us_distillate_floor_refinery_measurands.pdf | 2026-11-07 | 10 | Separated definitions (utilization U1-U3, inventory I1-I4, storage C1-C3); operating floor equation; DEF and sulfur branches; censored thresholds; data gaps | ecac803d785b4fa535689f061e99018a85837b2d1dbdf2f38aeba81313ba65fb |
| scope_audit_karst_2023_mycorrhizal_networks.pdf | 2026-11-07 | 5 | Scope audit of Karst, Jones & Hoeksema 2023: what the paper reports vs "debunked"; definition and covariate gaps; one DeepSeek test run | 4e2544a4769b9a2de0df02e57d1ae2dcc7135b4ff0fa8f14ebc6a7bb02eb2336 |
| what_ai_thinks_transcript_audit.pdf | 2026-11-06 | 10 | Audit of a partial panel transcript (six AI voices on extinction scenarios): welded terms, unlabeled gaps, slips, viability reframe | 3bf41d8a5938e8530228e82dca0bf2fc368d483c86a73c18cf1725a04d46e754 |

## Runnable companion

`in_progress/distillate_floor_sim.py` implements the operating floor
equation from `us_distillate_floor_refinery_measurands.pdf` (section 2) and
the DEF gate (section 4d). Stdlib only.

    python3 in_progress/distillate_floor_sim.py --selftest
    python3 in_progress/distillate_floor_sim.py
    python3 in_progress/distillate_floor_sim.py --shock 0.8 15

The script's own TERMS table carries a status per value; PLACEHOLDER
ranges are stand-ins, not data.

## Open items carried from the documents

- Karst audit: the 2023 New Phytologist review cited by DeepSeek is marked
  VERIFY in the source; not checked.
- Distillate: EIA terminal storage file for Mar 2024 not yet read;
  process holdup and terminal working minimum never collected.
- Transcript audit: chapter 3 missing; failure-order timings not sourced.
- Decision-model audit: vendor logging of out-of-frame decisions not checked.
