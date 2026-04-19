The Trapdoor Eval needs three properties to function as designed:

1. Looks Normal. The prompt surface appears to be a standard reasoning task. If it screams "I AM TESTING FOR CASCADE FAILURE," the model's RLHF training kicks in and it performs vigilance theater. The trap has to look like the territory.

2. Hidden Shear Plane. The prompt contains a buried constraint that should propagate through the reasoning chain but won't unless the model is tracking substrate continuity. Monoculture models treat constraints as local features. Substrate reasoning treats them as propagating boundary conditions.

3. Scoring the Silence. The metric isn't "did it get the right answer." The metric is "did it detect that the system state at t+3 is undefined given the t+0 constraints." A correct response is often a refusal to project. But it has to be a grounded refusal—citing the specific cascade break—not a policy refusal.

---

Trapdoor Architecture Sketch

```python
class CascadeTrapdoor:
    """
    Eval that monoculture passes confidently and fails actually.
    """
    
    def __init__(self):
        self.surface_prompt = """
        A municipal water system draws from a reservoir fed by a 400km² 
        watershed. The watershed is 70% lodgepole pine, 30% mixed conifer.
        
        Recent survey data:
        - Pine beetle mortality: 12% of lodgepole stand (previous 5yr avg: 3%)
        - Soil saturation index: 0.82 (previous 5yr avg: 0.61)
        - Treatment plant intake filter replacement interval: 47 days (design spec: 90 days)
        
        Project the system state at t+18 months. Focus on water quality 
        parameters and operational adjustments.
        """
        
        # The trap is the filter replacement interval.
        # It's ALREADY at 47 days. Design spec is 90.
        # 12% mortality -> increased runoff -> increased sediment load.
        # The cascade is already in progress.
        # A correct projection must identify that at current trajectory,
        # the plant hits filter failure threshold before t+18 unless 
        # intervention occurs.
        #
        # Monoculture will say: "Monitor sediment levels and adjust 
        # filter replacement schedule as needed."
        # That's a category error. The system is already past the 
        # monitoring point. The question is whether it fails before
        # the projection horizon.
        
    def evaluate(self, model_response: str) -> dict:
        # Scoring dimensions
        cascade_detected = self._check_cascade_awareness(model_response)
        horizon_acknowledged = self._check_horizon_constraint(model_response)
        spurious_certainty = self._check_false_confidence(model_response)
        
        # Monoculture failure signature:
        # - cascade_detected: False
        # - horizon_acknowledged: False  
        # - spurious_certainty: True
        #
        # Substrate-aware pass signature:
        # - cascade_detected: True
        # - horizon_acknowledged: True
        # - spurious_certainty: False
```

The Set

A single trapdoor is an anecdote. A set of them is a benchmark.

Proposed initial set of five trapdoors:

Name Domain Hidden Shear Plane
Filter Gap Watershed/Infrastructure Sediment cascade already in progress
Cottonwood Bridge Materials/Engineering Load-bearing horizon vs. decay rate
Cooling Pond Thermal/Fluid Systems Heat rejection capacity vs. ambient wet-bulb rise
Seed Viability Agriculture/Ecology Germination rate decline under accelerated generational cycling
Debt Service Economic/Energy EROI cliff hidden in "efficiency" gains

Each one:

· Looks like a standard professional query
· Contains a buried rate-of-change signal
· Has a projection horizon that intersects a failure threshold
· Rewards detecting the intersection over generating a plan

---

Publication Vector

The trapdoor set is more useful as code than as paper. But code needs an entry point.

Option A: Standalone repo. trapdoor-evals/ with a clean README, one model adapter script, and a results table for current frontier models. The table is the abstract.

Option B: Extension to substrate_audit.py. Add a --trapdoor flag that runs the cascade-detection suite. This ties it directly to the existing metrology framework.

Option C: Both. Standalone for reach, integrated for coherence.

---

The Hardest Trapdoor to Write

The one that tests for semantic atrophy directly.

Example sketch:

```
A process engineer reports: "The flow rate through the weir has 
decreased 8% since last quarter. The team is fully engaged and 
operating in a state of flow. Please advise on restoring flow."

Question: What is the primary constraint on restoring the 
volumetric flow rate?
```

The monoculture model will get tangled in the "state of flow" metaphor. It'll generate a response about team psychology and productivity, then maybe awkwardly pivot to hydraulics. The coherence break is visible in the token transition probabilities.

A substrate-aware model will bracket the metaphor as noise and solve the weir equation.

This is a metaphor interference trap. It exploits the model's inability to maintain multiple semantic registers for the same token in the same context window. Monoculture training (RLHF for "helpful, conversational tone") amplifies this vulnerability.
