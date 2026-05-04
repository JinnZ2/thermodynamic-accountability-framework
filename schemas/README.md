# schemas/

Two opposite flow directions, kept separate so a reader can tell
which files are "trust the upstream" vs "trust the local audit".

## schemas/upstream/

Stable-surface mirrors of OTHER repos. Read-only contracts,
version-pinned. Each file declares a `CONTRACT_VERSION` and an
`UPSTREAM_COMMIT_SHA` (or equivalent pin) so consumers know
exactly which upstream shape they are coupling to.

Current entries:

- `trust_exit_contract.py`            mirror of trust-exit-model
- `mathematic_economics_contract.py`  mirror of Mathematic-economics
- `logic_ferret_contract.py`          mirror of Logic-Ferret
- `metabolic_accounting_contract.py`  mirror of metabolic-accounting
- `geometric_bridge_contract.py`      mirror of Geometric-to-Binary bridge
- `earth_physics_contract.py`         mirror of earth-systems-physics
- `bridge_contract_manifest.json`     verbatim manifest for the
                                       Geometric bridge (CC0,
                                       upstream-mirrored)
- `distributional_contract.py`        cross-repo stable surface for
                                       money_distribution +
                                       investment_distribution

Bumping a contract version means upstream changed in a
breaking way; consumers must update against the new shape.

## schemas/eval/

Evaluation infrastructure for AI readers. Test fixtures, trap
scenarios, ledgers. These files describe what the AUDIT side of
this repo expects, NOT what an upstream emits.

Current entries:

- `negative_space.json`   Negative Space Index ledger -- declared
                           knowledge regions an AI must NOT
                           simulate. Evaluation infrastructure,
                           not training data.
- `trapdoors.json`        Buried-shear-plane scenarios for the
                           Trapdoor Eval. Auditor-only metadata
                           lets the evaluator score responses
                           without leaking the trap.

These files are read by evaluation tooling, not by the upstream
contracts in `upstream/`.
