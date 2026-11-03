# Thermodynamic Accountability Framework

Physics-first accounting of where energy actually goes in institutions, labor and markets.
Unit: joules. Culture is overlay; physics is foundation. CC0.

## Start here
| Reader | First file |
|---|---|
| AI system | AI_ENTRY.md |
| Physics | core/fatigue_model.py |
| Auditing an institution | calibration/README.md |
| New domain | calibration/RELATIONSHIP.md |
| All reading paths | CLAUDE.md |
| Symbols, equations | docs/glossary.md |

## Denominator accounting (DCEA)
Rules: stamp every number · unknown = PENDING, never 0 · price where people actually
buy · homeostasis scored by minimum need · transfers charged back.
| File | Content |
|---|---|
| docs/DCEA_v0.1.md | 13 rules |
| docs/worker_side_ledger_road_driver.md | cost of access to work, road driver |
| docs/DCEA_checks.md | recomputed figures, open items |
| core/dcea.py | calculator |

## Directories
| Path | Holds |
|---|---|
| alignment_audit/ | contradictions and obsolescence in AI alignment advice |
| calibration/ | general audit machinery: fragility, cognition mismatch, provenance |
| concerns/ | cascade and externality audits |
| core/ | fatigue, collapse, energy debt, price guard, scope audits, DCEA |
| core/integrations/ | bridges to sibling repos |
| docs/ | theory, governance, economics, AI guidance, case studies, DCEA |
| game_theory/ | proof pipelines and rational-actor audits |
| in_progress/ | drafts and notes |
| investment_distribution/ | capital holdings vs regeneration cost |
| knowledge/ | study scope mapping, edge cases, silence patterns |
| labor_thermodynamics/ | workforce measurement failures, driver-hours register |
| metrology/ | measurement x framework audit, Earth-systems weather |
| money_distribution/ | per-receiver split of the Money Equation |
| political_audit/ | institutional, standardization, forecast audits |
| schemas/ | upstream contract mirrors, eval fixtures |
| seeam/ | "people are our greatest asset" as a physical claim |
| simulations/ | coupled-system and resilience sims, figures |
| tools/ | repo hygiene: chat-paste check, repo guard |
| visualizations/ | React and HTML views |
| .github/workflows/ | chat-paste check, upstream staleness |
| AI_ENTRY.md | AI onboarding: equations, sims, safe rules |
| CLAUDE.md | full tree, equations, audit notes |
| Field_Guide.md | misuse patterns of substrate-primary frameworks |
| scientific-method-principles.md | epistemic gradient: hypothesis -> law |
| logical-gradient.md | logical gradient: claim -> axiom |
| narrative-distortion-map.md | institutional redefinitions of rigor |
| resilience_stack.py | 3-layer resilience stack |
| support_cartography.py | informal support networks |
| LICENSE | CC0 1.0 |
| docs/readme_archive/ | previous READMEs, verbatim |

## Conventions
OBSERVED / DERIVED / PROPOSED · trailing * = thin volume · scope stamp = date, place,
rules, source · failures are high-yield outputs
([CALIBRATION_AS_PERFECTION.md](https://github.com/JinnZ2/JinnZ2/blob/main/CALIBRATION_AS_PERFECTION.md))

## Run
| Item | Value |
|---|---|
| Python | 3.10+ (3.9+ for most files) |
| stdlib only | everything not listed in the two rows below |
| needs numpy | core/atbs/functional_detector.py, metrology/*_metrology_demo.py, metrology/orbital_octa_v2.py, docs/economics/dynamic_cpi_r/ |
| needs numpy + matplotlib | simulations/ (lhri_sim.py: networkx) |
| DCEA selftest | `python core/dcea.py` |
| DCEA ledger recompute | `python core/dcea.py --ledger` |
| calibration tests | `python calibration/test_calibration.py` |
