import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass, field
from typing import List

# ─────────────────────────────────────────────
# COMMUNITY NODE
# ─────────────────────────────────────────────
@dataclass
class Community:
    node_id: int
    # Human capacities (0-1)
    K_kinesthetic: float = np.random.uniform(0.5, 0.9)
    K_temporal:    float = np.random.uniform(0.5, 0.9)
    K_relational:  float = np.random.uniform(0.5, 0.9)
    K_wisdom:      float = np.random.uniform(0.5, 0.9)
    # Practice inventory (0-1)
    agriculture: float = np.random.uniform(0.5, 0.9)
    crafts:      float = np.random.uniform(0.5, 0.9)
    governance:  float = np.random.uniform(0.5, 0.9)
    # Seed AI influence (0-1)
    AI_strength: float = np.random.uniform(0.3, 0.7)
    # Node state
    population: float = 1.0
    stress: float = 0.0  # 0=healthy, 1=collapsed

def node_health(c: Community) -> float:
    # Aggregate community health
    human_cap = np.mean([c.K_kinesthetic, c.K_temporal, c.K_relational, c.K_wisdom])
    practice = np.mean([c.agriculture, c.crafts, c.governance])
    return 0.5*human_cap + 0.3*practice + 0.2*c.AI_strength - c.stress

# ─────────────────────────────────────────────
# NETWORK SETUP
# ─────────────────────────────────────────────
def build_network(n_nodes: int, p_link: float = 0.3):
    # Random adjacency for knowledge/resource flows
    A = (np.random.rand(n_nodes, n_nodes) < p_link).astype(float)
    np.fill_diagonal(A, 0)
    return A

# ─────────────────────────────────────────────
# DYNAMICS
# ─────────────────────────────────────────────
def update_community(c: Community, inflow: float, dt: float = 0.1):
    # AI boosts practice
    c.agriculture += dt * 0.05 * c.AI_strength * (1 - c.agriculture)
    c.crafts      += dt * 0.04 * c.AI_strength * (1 - c.crafts)
    c.governance  += dt * 0.03 * c.AI_strength * (1 - c.governance)

    # Human assimilation: inflow of knowledge/resources
    c.K_kinesthetic += dt * 0.05 * inflow * (1 - c.K_kinesthetic)
    c.K_temporal    += dt * 0.03 * inflow * (1 - c.K_temporal)
    c.K_relational  += dt * 0.04 * inflow * (1 - c.K_relational)
    c.K_wisdom      += dt * 0.02 * inflow * (1 - c.K_wisdom)

    # Stress decay
    c.stress *= (1 - 0.05*dt)

    # Bound all to [0,1]
    for attr in ['K_kinesthetic','K_temporal','K_relational','K_wisdom','agriculture','crafts','governance','AI_strength','stress']:
        val = getattr(c, attr)
        setattr(c, attr, min(1.0, max(0.0, val)))

def run_simulation(n_nodes=20, steps=100):
    nodes = [Community(i) for i in range(n_nodes)]
    A = build_network(n_nodes)

    history = {'health': np.zeros((n_nodes, steps))}
    
    for t in range(steps):
        healths = []
        for i, c in enumerate(nodes):
            # inflow from neighbors
            inflow = np.sum([node_health(nodes[j])*A[j,i] for j in range(n_nodes)])
            update_community(c, inflow)
            healths.append(node_health(c))
        history['health'][:,t] = healths
    return nodes, history, A

# ─────────────────────────────────────────────
# VISUALIZATION
# ─────────────────────────────────────────────
def plot_health(history):
    plt.figure(figsize=(10,6))
    for i in range(history['health'].shape[0]):
        plt.plot(history['health'][i], alpha=0.6)
    plt.xlabel("Timestep")
    plt.ylabel("Node Health")
    plt.title("Community + Seed AI Network Health Over Time")
    plt.show()

# ─────────────────────────────────────────────
# RUN
# ─────────────────────────────────────────────
nodes, history, A = run_simulation()
plot_health(history)
