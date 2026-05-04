# calibration/ <-> metrology/

calibration/ holds the GENERAL audit machinery:

- architecture_mismatch.py        substrate vs language primary
- calibration_audit.py            5-dim Q1-Q5 environment audit
- observation_dependence.py       witness-dependence coefficient
- adaptation_debt.py              friction-removal -> fragility
- recency_bias_detector.py        6-pattern temporal-bias gate
- pipeline.py                     unified runner

metrology/ is the FIRST DOMAIN INSTANCE of that machinery,
applied to Earth-systems extreme-weather trend claims. It is
not a parallel framework; it is calibration/ specialized.

New domains (forestry, fisheries, hydrology, finance, etc.)
should follow the metrology/ pattern: a domain folder that
instantiates calibration/'s general checks against
domain-specific reference systems.

## Pattern for a new domain folder

1. Reference registry of pre-corruption observation systems
   (cf. `metrology/pre1900_engineering_registry.py`)
2. Observer-bias model for the domain's measurement history
   (cf. `metrology/observer_bias.py`)
3. Convergence matrix of M-checks (measurement layer) and
   F-checks (framework layer) appropriate to the domain
   (cf. `metrology/domain_convergence_matrix.py`)
4. Trend / claim corruption calculator combining M and F
   (cf. `metrology/trend_corruption_calculator.py`)
5. Constraint-recovery module extracting machine-readable
   physical constraints from validated observation systems
   (cf. `metrology/constraint_recovery_framework.py`)

calibration/ provides the substrate. metrology/ shows the shape
a domain instantiation takes. Future domains follow the same
shape, not a parallel one.
