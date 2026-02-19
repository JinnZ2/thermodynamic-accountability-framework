import numpy as np
import networkx as nx

# --------------------------
# NODE AND ROLE DEFINITION
# --------------------------

class WorkerNode:
    def __init__(self, name, role_type, risk_env, horizon):
        self.name = name
        self.role_type = role_type           # e.g., 'safety', 'physical', 'network', 'admin'
        self.risk_env = risk_env             # 'high', 'medium', 'low'
        self.horizon = horizon               # 'short', 'shift', 'longitudinal'
        
        # State variables
        self.E_active = 0.0                  # Energy cost of tasks
        self.D_static = 0.0                  # Degradation from inactivity
        self.R_risk = 0.0                    # Risk accumulated
        self.F_cognitive = 0.0               # Cognitive fatigue
        self.S_network = 0.0                  # Social / network contribution
        
        self.C_total = 0.0                    # Total cost over time
        self.history = []                     # Track time-series for analysis
    
    def step(self, E_active_delta=0, move=True, network_effect=0, fatigue_delta=0, risk_delta=0):
        """Update the node state for one time step"""
        self.E_active += E_active_delta
        # Degradation if stationary
        self.D_static += 0.1 if not move else -0.05
        # Risk grows with fatigue
        self.R_risk += risk_delta + self.F_cognitive * 0.1
        # Cognitive fatigue accumulation
        self.F_cognitive += fatigue_delta - (0.05 if move else 0)
        # Network contribution
        self.S_network += network_effect
        
        # Compute total cost for this timestep
        self.C_total = self.E_active + self.D_static + self.R_risk + self.F_cognitive - self.S_network
        
        # Record state
        self.history.append({
            'E_active': self.E_active,
            'D_static': self.D_static,
            'R_risk': self.R_risk,
            'F_cognitive': self.F_cognitive,
            'S_network': self.S_network,
            'C_total': self.C_total
        })

# --------------------------
# ORGANIZATION NETWORK
# --------------------------

class Organization:
    def __init__(self):
        self.network = nx.Graph()   # Social and operational network
        self.nodes = {}
    
    def add_worker(self, worker: WorkerNode):
        self.nodes[worker.name] = worker
        self.network.add_node(worker.name)
    
    def add_connection(self, name1, name2, weight=1.0):
        self.network.add_edge(name1, name2, weight=weight)
    
    def step_all(self, time_step=1):
        """Simulate one time step across all workers"""
        for name, worker in self.nodes.items():
            # Example dynamics: move and interact with neighbors
            neighbors = list(self.network.neighbors(name))
            network_effect = sum([self.nodes[n].S_network for n in neighbors]) * 0.05
            move = np.random.rand() > 0.2  # 80% chance worker is moving or active
            
            # Random fatigue or risk events (can be customized)
            fatigue_delta = np.random.rand() * 0.1
            risk_delta = np.random.rand() * 0.05
            E_active_delta = np.random.rand() * 0.2 if move else 0
            
            worker.step(
                E_active_delta=E_active_delta,
                move=move,
                network_effect=network_effect,
                fatigue_delta=fatigue_delta,
                risk_delta=risk_delta
            )

# --------------------------
# SIMULATION RUN
# --------------------------

def run_simulation(org: Organization, steps=100):
    for t in range(steps):
        org.step_all()
    
    # Collect LHRI outputs
    lhri_scores = {name: worker.C_total for name, worker in org.nodes.items()}
    return lhri_scores

# --------------------------
# EXAMPLE SETUP
# --------------------------

# Create organization
org = Organization()

# Add workers
org.add_worker(WorkerNode('Alice', 'safety', 'high', 'shift'))
org.add_worker(WorkerNode('Bob', 'network', 'medium', 'longitudinal'))
org.add_worker(WorkerNode('Charlie', 'physical', 'medium', 'shift'))

# Connect network
org.add_connection('Alice', 'Bob')
org.add_connection('Bob', 'Charlie')

# Run simulation
scores = run_simulation(org, steps=50)

# Output LHRI-style scores
for name, score in scores.items():
    print(f"{name}: LHRI total cost={score:.2f}")
