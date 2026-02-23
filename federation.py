“””
FEDERATION LAYER — Planet-scale node network
100k nodes × 100k people = 10B population scale

ARCHITECTURE:
No central sovereign.
Nodes federate via:
- Ecological constraint sharing (watershed/bioregion flows)
- Migration balancing (assimilation-gated)
- Resource redistribution (surplus routing)
- Knowledge redundancy mapping (polytensor overlap)
- Cascade risk monitoring (AI coordination layer)

FEDERATION PRINCIPLES:

1. Node sovereignty preserved — federation cannot override node governance
1. Ecological flows are physical — not negotiable, not political
1. Knowledge redundancy is explicit — no dimension held by single node
1. Migration is governed by assimilation capacity — not quotas
1. AI coordination layer is transparent to all nodes — no hidden signals
1. Cascade containment — stressed node isolated before it infects neighbors

INTER-NODE COUPLING:
Ecological: watershed upstream/downstream
Economic:   trade surplus/deficit flows
Knowledge:  dimension sharing, apprenticeship exchange
Migration:  population flows (assimilation-gated)
Cascade:    stress propagation through network topology

FAILURE MODES:

- Empire formation: one node captures federation coordination layer
- Cascade collapse: stressed node infects neighbors before isolation
- Knowledge monoculture: all nodes converge to same K_polytensor
- Migration overwhelm: receiving node assimilation capacity exceeded
- Ecological externalization: node exports ecological cost to neighbors
  “””

import numpy as np
from collections import deque, Counter
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from dataclasses import dataclass, field
from typing import List, Dict

# ─────────────────────────────────────────────

# SIMPLIFIED NODE FOR FEDERATION SCALE

# Full node too expensive at 100s of nodes

# Compressed to domain composites + key coupling variables

# ─────────────────────────────────────────────

@dataclass
class FedNode:
node_id:          int   = 0
# DOMAIN COMPOSITES (0-1)
eco:              float = 0.80
knowledge:        float = 0.70   # K polytensor composite
governance:       float = 0.72
alignment:        float = 0.65
ai_symbiosis:     float = 0.75
# ECONOMIC
food_surplus:     float = 0.15   # fraction above subsistence (exportable)
energy_surplus:   float = 0.12
# MIGRATION
assimilation_cap: float = 0.60
population:       float = 1.00   # normalized to 100k
# KNOWLEDGE DIMENSIONS (for redundancy mapping)
K_kinesthetic:    float = 0.70
K_temporal:       float = 0.65
K_relational:     float = 0.70
K_digital:        float = 0.70
# FEDERATION HEALTH
sovereignty_intact: float = 0.90  # resistance to federation capture
cascade_risk:       float = 0.15  # LOW good
isolation_flag:     bool  = False  # True = node isolated from network

def node_health_fed(n: FedNode) -> float:
scores = [
max(0,(n.eco-0.30)/0.70),
max(0,(n.knowledge-0.25)/0.75),
max(0,(n.governance-0.35)/0.65),
max(0,(n.alignment-0.25)/0.75),
max(0,(n.ai_symbiosis-0.30)/0.70),
max(0,(n.food_surplus+0.05)/0.25),   # can survive slight deficit short-term
max(0,(n.sovereignty_intact-0.50)/0.50),
]
return min(scores)

# ─────────────────────────────────────────────

# FEDERATION STATE

# ─────────────────────────────────────────────

@dataclass
class Federation:
# COORDINATION LAYER
coordination_transparency: float = 0.80  # all nodes can see coordination signals
empire_risk:               float = 0.10  # LOW good — one node capturing coordination
knowledge_diversity_index: float = 0.75  # how different K_polytensors are across nodes
cascade_firewall:          float = 0.70  # isolation protocol effectiveness
migration_governance:      float = 0.72  # assimilation-gated flow management
ecological_accounting:     float = 0.68  # upstream/downstream cost internalization
resource_redistribution:   float = 0.65  # surplus routing effectiveness
# INTER-NODE FLOWS (normalized)
total_migration_flow:      float = 0.0
knowledge_exchange_rate:   float = 0.15
ecological_externalization:float = 0.10  # LOW good

# ─────────────────────────────────────────────

# NETWORK TOPOLOGY

# ─────────────────────────────────────────────

def build_network(n_nodes: int, topology: str = ‘bioregional’) -> np.ndarray:
“””
Adjacency matrix for inter-node coupling.
bioregional: nodes clustered by watershed — strong local, weak long-range
grid: regular lattice
random: Erdos-Renyi
“””
A = np.zeros((n_nodes, n_nodes))
if topology == ‘bioregional’:
# Clusters of 5-8 nodes (watershed groups), weak inter-cluster links
cluster_size = 6
for i in range(n_nodes):
cluster = i // cluster_size
for j in range(n_nodes):
if i == j: continue
j_cluster = j // cluster_size
if i_cluster := cluster == j_cluster:
A[i,j] = 0.8 + 0.2*np.random.random()
elif abs(cluster - j_cluster) == 1:
A[i,j] = 0.15*np.random.random()
elif topology == ‘grid’:
side = int(np.ceil(np.sqrt(n_nodes)))
for i in range(n_nodes):
for dj in [-side,-1,1,side]:
j = i + dj
if 0 <= j < n_nodes and abs(i%side - j%side) <= 1:
A[i,j] = 0.6 + 0.2*np.random.random()
else:  # random
p = 3.0/n_nodes
A = (np.random.random((n_nodes,n_nodes)) < p).astype(float)
np.fill_diagonal(A,0)
A = (A + A.T)/2
return A

# ─────────────────────────────────────────────

# INTER-NODE FLOWS

# ─────────────────────────────────────────────

def compute_flows(nodes: List[FedNode], A: np.ndarray, fed: Federation) -> Dict:
“””
Compute all inter-node flows for one timestep.
Returns dict of (i,j) → flow_magnitude for each flow type.
“””
n = len(nodes)
migration = np.zeros((n,n))
knowledge  = np.zeros((n,n))
resources  = np.zeros((n,n))
eco_stress = np.zeros((n,n))

```
for i in range(n):
    ni = nodes[i]
    if ni.isolation_flag: continue
    for j in range(n):
        if i==j or A[i,j]==0: continue
        nj = nodes[j]
        if nj.isolation_flag: continue
        strength = A[i,j]

        # MIGRATION: from stressed nodes to healthy nodes
        # Rate gated by receiving node assimilation capacity
        stress_diff = max(0, node_health_fed(nj) - node_health_fed(ni))
        assimilation = nj.assimilation_cap * nj.governance
        migration[i,j] = strength * 0.02 * stress_diff * assimilation * fed.migration_governance

        # KNOWLEDGE EXCHANGE: nodes share underrepresented dimensions
        # Prevents monoculture — diversity maintained by exchange
        k_diff = abs(ni.K_kinesthetic - nj.K_kinesthetic) + abs(ni.K_temporal - nj.K_temporal)
        knowledge[i,j] = strength * 0.01 * k_diff * fed.knowledge_exchange_rate

        # RESOURCE REDISTRIBUTION: surplus flows to deficit nodes
        surplus_i = ni.food_surplus
        deficit_j = max(0, 0.05 - nj.food_surplus)
        resources[i,j] = strength * 0.03 * max(0,surplus_i) * deficit_j * fed.resource_redistribution

        # ECOLOGICAL STRESS PROPAGATION: upstream affects downstream
        # Cannot be governed away — physical reality
        eco_stress[i,j] = strength * max(0, 0.7 - ni.eco) * 0.02

return {'migration':migration, 'knowledge':knowledge,
        'resources':resources, 'eco_stress':eco_stress}
```

# ─────────────────────────────────────────────

# NODE UPDATE (federation-aware)

# ─────────────────────────────────────────────

def update_fed_node(n: FedNode, stress: dict, flows_in: dict,
fed: Federation, dt: float = 0.1) -> FedNode:
nn = FedNode(**n.**dict**)

```
B   = stress.get('industrial_pressure', 0.0)
drg = stress.get('drought', 0.0)
ego = stress.get('ego_capture', 0.0)
ext = stress.get('empire_pressure', 0.0)  # federation-level capture

mig_in  = flows_in.get('migration_in', 0.0)
mig_out = flows_in.get('migration_out', 0.0)
k_in    = flows_in.get('knowledge_in', 0.0)
res_in  = flows_in.get('resources_in', 0.0)
eco_in  = flows_in.get('eco_stress_in', 0.0)

# Assimilation capacity gates migration benefit
assim = n.assimilation_cap * n.governance
mig_effect = mig_in * (assim - 0.5) * 2.0  # bidirectional based on capacity

# ECOLOGICAL
nn.eco += dt*(0.04*n.eco*(1-n.eco) - 0.06*B - 0.10*drg
              - eco_in              # upstream stress propagates
              + res_in*0.02)        # resource inflow reduces extraction pressure

# KNOWLEDGE — exchange prevents monoculture
nn.knowledge += dt*(0.03*n.knowledge*(1-n.knowledge)
                     + k_in*0.5*(1-n.knowledge)  # incoming K boosts if different
                     - 0.08*B - 0.04*(1-n.alignment))
nn.K_kinesthetic += dt*(0.02*n.K_kinesthetic*(1-n.K_kinesthetic)
                         + k_in*0.3 - 0.06*B)
nn.K_temporal    += dt*(0.01*n.K_temporal*(1-n.K_temporal)
                         + mig_effect*0.02  # temporal: migration bidirectional
                         - 0.05*B)
nn.K_relational  += dt*(0.025*n.eco*(1-n.K_relational) - 0.05*B)
nn.K_digital     += dt*(0.04*(1-n.K_digital) - 0.05*(1-n.ai_symbiosis))

# GOVERNANCE
nn.governance += dt*(0.02*n.governance*(1-n.governance)
                      - 0.10*ego - 0.05*n.cascade_risk
                      + 0.02*fed.coordination_transparency*(1-n.governance)
                      - 0.04*ext)
nn.sovereignty_intact += dt*(0.02*(1-n.sovereignty_intact)
                              - 0.08*ext - 0.04*ego
                              + 0.02*n.governance)

# ALIGNMENT
nn.alignment += dt*(0.03*n.alignment*(1-n.alignment)
                     - 0.08*(1-n.eco)*(1-n.alignment)  # eco degradation breaks alignment
                     - 0.06*ego + 0.02*k_in)

# AI SYMBIOSIS
nn.ai_symbiosis += dt*(0.02*(1-n.ai_symbiosis)
                        - 0.05*(1-fed.coordination_transparency)
                        - 0.04*fed.empire_risk)

# ECONOMIC
nn.food_surplus += dt*(0.04*n.eco*(1-n.food_surplus+0.05)
                        - 0.06*B - 0.08*drg
                        - mig_in*0.02    # incoming population draws surplus
                        + res_in)
nn.energy_surplus += dt*(0.03*n.eco*(1-n.energy_surplus) - 0.05*B)

# POPULATION — migration flows
nn.population += dt*(mig_in - mig_out)*0.1

# ASSIMILATION CAPACITY — K_temporal and governance
nn.assimilation_cap = min(1.0, n.K_temporal * n.governance)

# CASCADE RISK — node's stress propagation potential
h = node_health_fed(nn)
nn.cascade_risk = max(0, (0.5 - h))  # risk rises as health falls below 0.5

# ISOLATION — if cascade_risk too high, federation isolates node
nn.isolation_flag = (h < 0.15 and fed.cascade_firewall > 0.5)

for _attr in [f for f in nn.__dict__ if isinstance(getattr(nn,f),float)]:
    setattr(nn,_attr,max(0.0,min(1.0,getattr(nn,_attr))))
return nn
```

def update_federation(fed: Federation, nodes: List[FedNode], dt: float=0.1) -> Federation:
nf = Federation(**fed.**dict**)

```
healths = [node_health_fed(n) for n in nodes]
mean_h  = np.mean(healths)
min_h   = np.min(healths)
std_h   = np.std(healths)

# K diversity — variance across nodes
k_kin_vals = [n.K_kinesthetic for n in nodes]
k_tem_vals = [n.K_temporal for n in nodes]
nf.knowledge_diversity_index = min(1.0, (np.std(k_kin_vals)+np.std(k_tem_vals))*5 + 0.3)

# Empire risk — if one node health far above mean (extracting from others)
max_h = np.max(healths)
nf.empire_risk = max(0, (max_h - mean_h - 0.2)*2)

# Cascade firewall — better when governance high across network
gov_mean = np.mean([n.governance for n in nodes])
nf.cascade_firewall += dt*(0.02*(gov_mean - nf.cascade_firewall))

# Ecological accounting — how well costs internalized
nf.ecological_accounting += dt*(0.02*(mean_h - nf.ecological_accounting))

# Coordination transparency — degrades with empire risk
nf.coordination_transparency += dt*(0.02*(1-nf.coordination_transparency)
                                     - 0.10*nf.empire_risk)

# Migration governance — tracks assimilation capacity network-wide
assim_mean = np.mean([n.assimilation_cap for n in nodes])
nf.migration_governance += dt*(0.02*(assim_mean - nf.migration_governance))

# Resource redistribution — works when coordination transparent
nf.resource_redistribution += dt*(0.02*(nf.coordination_transparency - nf.resource_redistribution))

# Ecological externalization — how much nodes export eco cost to neighbors
nf.ecological_externalization = max(0, 0.5 - mean_h) * std_h

for _attr in [f for f in nf.__dict__ if isinstance(getattr(nf,f),float)]:
    setattr(nf,_attr,max(0.0,min(1.0,getattr(nf,_attr))))
return nf
```

# ─────────────────────────────────────────────

# FEDERATION RUNNER

# ─────────────────────────────────────────────

def run_federation(n_nodes=30, steps=300, onset=50,
node_stresses=None, topology=‘bioregional’,
initial_variance=0.15):
“””
node_stresses: dict of {node_id: {stress_dict}} for targeted stress
“””
np.random.seed(42)
A = build_network(n_nodes, topology)

```
# Initialize nodes with variance
nodes = []
for i in range(n_nodes):
    n = FedNode(node_id=i)
    n.eco        = 0.80 + initial_variance*(np.random.random()-0.5)
    n.knowledge  = 0.70 + initial_variance*(np.random.random()-0.5)
    n.governance = 0.72 + initial_variance*(np.random.random()-0.5)
    n.alignment  = 0.65 + initial_variance*(np.random.random()-0.5)
    n.K_kinesthetic = 0.70 + 0.20*(np.random.random()-0.5)
    n.K_temporal    = 0.65 + 0.20*(np.random.random()-0.5)
    for attr in [f for f in n.__dict__ if isinstance(getattr(n,f),float)]:
        setattr(n, attr, max(0.1, min(0.99, getattr(n,attr))))
    nodes.append(n)

fed = Federation()

# History
hist = {
    'mean_health':[], 'min_health':[], 'max_health':[], 'std_health':[],
    'n_isolated':[], 'empire_risk':[], 'knowledge_diversity':[],
    'cascade_firewall':[], 'coordination_transparency':[],
    'ecological_externalization':[], 'migration_flow':[],
    'node_health': [[] for _ in range(n_nodes)],
    'node_eco':    [[] for _ in range(n_nodes)],
}

for t in range(steps):
    # Compute flows
    flows = compute_flows(nodes, A, fed)

    # Update each node
    new_nodes = []
    for i, n in enumerate(nodes):
        stress = {}
        if node_stresses and t >= onset:
            stress = node_stresses.get(i, {})

        flows_in = {
            'migration_in':  flows['migration'][:,i].sum(),
            'migration_out': flows['migration'][i,:].sum(),
            'knowledge_in':  flows['knowledge'][:,i].sum(),
            'resources_in':  flows['resources'][:,i].sum(),
            'eco_stress_in': flows['eco_stress'][:,i].sum(),
        }
        new_nodes.append(update_fed_node(n, stress, flows_in, fed))
    nodes = new_nodes

    # Update federation
    fed = update_federation(fed, nodes)

    # Record
    healths = [node_health_fed(n) for n in nodes]
    hist['mean_health'].append(np.mean(healths))
    hist['min_health'].append(np.min(healths))
    hist['max_health'].append(np.max(healths))
    hist['std_health'].append(np.std(healths))
    hist['n_isolated'].append(sum(1 for n in nodes if n.isolation_flag))
    hist['empire_risk'].append(fed.empire_risk)
    hist['knowledge_diversity'].append(fed.knowledge_diversity_index)
    hist['cascade_firewall'].append(fed.cascade_firewall)
    hist['coordination_transparency'].append(fed.coordination_transparency)
    hist['ecological_externalization'].append(fed.ecological_externalization)
    hist['migration_flow'].append(flows['migration'].sum())
    for i in range(n_nodes):
        hist['node_health'][i].append(healths[i])
        hist['node_eco'][i].append(nodes[i].eco)

return {k: np.array(v) if k not in ('node_health','node_eco') else [np.array(x) for x in v]
        for k,v in hist.items()}, nodes, fed, A
```

# ─────────────────────────────────────────────

# SCENARIOS

# ─────────────────────────────────────────────

N = 24

# Baseline

r_base, _, _, A_base = run_federation(N, steps=300)

# Cascade: 3 adjacent nodes stressed heavily

cascade_stress = {i: {‘industrial_pressure’:0.50,‘drought’:0.30} for i in [2,3,4]}
r_cascade, nodes_c, fed_c, _ = run_federation(N, steps=300, node_stresses=cascade_stress)

# Empire: node 0 gets ego_capture, tries to dominate coordination

empire_stress = {0: {‘ego_capture’:0.60}}
r_empire, _, _, _ = run_federation(N, steps=300, node_stresses=empire_stress)

# Knowledge monoculture: institutional pressure across all nodes

mono_stress = {i: {‘industrial_pressure’:0.25} for i in range(N)}
r_mono, _, _, _ = run_federation(N, steps=300, node_stresses=mono_stress)

# Resilient: strong cascade firewall + high initial K diversity

r_resilient, _, _, _ = run_federation(N, steps=300, initial_variance=0.25)

T = np.arange(300)*0.1

# ─────────────────────────────────────────────

# VISUALIZATION

# ─────────────────────────────────────────────

fig = plt.figure(figsize=(24,20)); fig.patch.set_facecolor(’#0d1117’)
gs = gridspec.GridSpec(4,3,figure=fig,hspace=0.52,wspace=0.35)

def sax(ax,t):
ax.set_facecolor(’#161b22’); ax.tick_params(colors=’#8b949e’,labelsize=8)
ax.set_title(t,color=’#e6edf3’,fontsize=8.5,pad=5)
for sp in ax.spines.values(): sp.set_color(’#30363d’); sp.set_linewidth(0.5)
ax.axvline(5.0,color=’#333355’,lw=0.7,linestyle=’:’)
return ax

# Row 0: network mean health all scenarios

ax0=fig.add_subplot(gs[0,:2]); sax(ax0,“Federation Mean Health — All Scenarios\n(band = min/max across nodes)”)
scens=[(‘Baseline’,r_base,’#51cf66’),(‘Cascade stress’,r_cascade,’#ff6b6b’),
(‘Empire capture’,r_empire,’#ff922b’),(‘Knowledge monoculture’,r_mono,’#ffd43b’),
(‘High diversity’,r_resilient,’#74c0fc’)]
for lbl,r,c in scens:
ax0.plot(T,r[‘mean_health’],color=c,lw=2.0,label=lbl)
ax0.fill_between(T,r[‘min_health’],r[‘max_health’],color=c,alpha=0.12)
ax0.axhline(0.20,color=’#ff4444’,lw=0.8,linestyle=’–’,label=‘Critical’)
ax0.set_ylim(0,1.1); ax0.legend(fontsize=7,facecolor=’#21262d’,labelcolor=’#e6edf3’,ncol=2)
ax0.set_xlabel(‘Time’,color=’#8b949e’,fontsize=8)

# Row 0 right: isolation count and empire risk

ax0r=fig.add_subplot(gs[0,2]); sax(ax0r,“Isolation Events & Empire Risk\nCascade firewall in action”)
ax0r2=ax0r.twinx()
for lbl,r,c in [(‘Cascade’,r_cascade,’#ff6b6b’),(‘Empire’,r_empire,’#ff922b’),(‘Baseline’,r_base,’#51cf66’)]:
ax0r.plot(T,r[‘n_isolated’],color=c,lw=1.5,label=f’{lbl} isolated’)
ax0r2.plot(T,r[‘empire_risk’],color=c,lw=1.2,linestyle=’–’)
ax0r.set_ylabel(‘Nodes isolated’,color=’#8b949e’,fontsize=8)
ax0r2.set_ylabel(‘Empire risk (–)’,color=’#8b949e’,fontsize=8)
ax0r.legend(fontsize=6.5,facecolor=’#21262d’,labelcolor=’#e6edf3’)
ax0r.text(5,0.3,‘─ isolated  – empire risk’,color=’#8b949e’,fontsize=7)

# Row 1: cascade spread — node health heatmap over time

ax1a=fig.add_subplot(gs[1,0]); sax(ax1a,“Cascade Spread — Node Health Heatmap\n(3 stressed nodes, bioregional topology)”)
health_matrix = np.array(r_cascade[‘node_health’])  # n_nodes × steps
im=ax1a.imshow(health_matrix,aspect=‘auto’,cmap=‘RdYlGn’,vmin=0,vmax=1,
extent=[0,T[-1],N-0.5,-0.5])
ax1a.axvline(5.0,color=‘white’,lw=0.8,linestyle=’–’)
ax1a.set_xlabel(‘Time’,color=’#8b949e’,fontsize=8)
ax1a.set_ylabel(‘Node ID’,color=’#8b949e’,fontsize=8)
plt.colorbar(im,ax=ax1a,shrink=0.8).set_label(‘Health’,color=’#8b949e’,fontsize=7)
ax1a.text(6,3.5,‘← stressed nodes’,color=‘white’,fontsize=7)

# Row 1: knowledge diversity over time

ax1b=fig.add_subplot(gs[1,1]); sax(ax1b,“Knowledge Diversity Index\nMonoculture risk under industrial pressure”)
for lbl,r,c in scens:
ax1b.plot(T,r[‘knowledge_diversity’],color=c,lw=1.8,label=lbl)
ax1b.axhline(0.40,color=’#ff4444’,lw=0.7,linestyle=’–’,label=‘Diversity floor’)
ax1b.set_ylim(0,1.0); ax1b.legend(fontsize=6.5,facecolor=’#21262d’,labelcolor=’#e6edf3’)
ax1b.text(5,0.42,‘Below: K_polytensor converging → single point of failure’,color=’#8b949e’,fontsize=7,style=‘italic’)

# Row 1: coordination transparency vs empire risk

ax1c=fig.add_subplot(gs[1,2]); sax(ax1c,“Coordination Transparency vs Empire Risk\nCapture degrades the signal all nodes rely on”)
for lbl,r,c in [(‘Baseline’,r_base,’#51cf66’),(‘Empire’,r_empire,’#ff922b’),(‘Cascade’,r_cascade,’#ff6b6b’)]:
ax1c.plot(T,r[‘coordination_transparency’],color=c,lw=1.8,label=f’{lbl} transparency’)
ax1c.plot(T,r[‘empire_risk’],              color=c,lw=1.0,linestyle=’–’)
ax1c.text(15,0.08,‘─ transparency  – empire risk’,color=’#8b949e’,fontsize=7)
ax1c.set_ylim(0,1.0); ax1c.legend(fontsize=6.5,facecolor=’#21262d’,labelcolor=’#e6edf3’)

# Row 2: ecological externalization

ax2a=fig.add_subplot(gs[2,0]); sax(ax2a,“Ecological Externalization\nNodes exporting eco cost to neighbors”)
for lbl,r,c in scens:
ax2a.plot(T,r[‘ecological_externalization’],color=c,lw=1.8,label=lbl)
ax2a.set_ylim(0,0.5); ax2a.legend(fontsize=6.5,facecolor=’#21262d’,labelcolor=’#e6edf3’)
ax2a.text(5,0.35,‘Physical flows — cannot be governed away\nonly internalized via accounting’,color=’#8b949e’,fontsize=7)

# Row 2: migration flow and assimilation

ax2b=fig.add_subplot(gs[2,1]); sax(ax2b,“Migration Flow — Assimilation-Gated\nFlow rate × assimilation capacity”)
for lbl,r,c in [(‘Baseline’,r_base,’#51cf66’),(‘Cascade’,r_cascade,’#ff6b6b’),(‘High diversity’,r_resilient,’#74c0fc’)]:
ax2b.plot(T,r[‘migration_flow’],color=c,lw=1.8,label=lbl)
ax2b.set_ylim(0,None); ax2b.legend(fontsize=7,facecolor=’#21262d’,labelcolor=’#e6edf3’)
ax2b.set_ylabel(‘Total migration flow’,color=’#8b949e’,fontsize=8)

# Row 2: std_health — inequality across network

ax2c=fig.add_subplot(gs[2,2]); sax(ax2c,“Health Inequality Across Network\nHigh std = some nodes extracting from others”)
for lbl,r,c in scens:
ax2c.plot(T,r[‘std_health’],color=c,lw=1.8,label=lbl)
ax2c.axhline(0.20,color=’#ff4444’,lw=0.7,linestyle=’–’,label=‘Inequality warning’)
ax2c.set_ylim(0,0.5); ax2c.legend(fontsize=6.5,facecolor=’#21262d’,labelcolor=’#e6edf3’)

# Row 3: network topology visualization (final state)

ax3a=fig.add_subplot(gs[3,0]); sax(ax3a,“Network Topology — Cascade Final State\n(circle=healthy, X=isolated, size=health)”)
final_health_c = [r_cascade[‘node_health’][i][-1] for i in range(N)]
angles = np.linspace(0, 2*np.pi, N, endpoint=False)

# Group nodes into bioregional clusters

cluster_size=6
colors_map=plt.cm.RdYlGn
for i in range(N):
ci = i // cluster_size
r_offset = 0.7 + 0.3*(ci%2)
x = r_offset*np.cos(angles[i]); y = r_offset*np.sin(angles[i])
h = final_health_c[i]
c = colors_map(h)
marker=‘X’ if nodes_c[i].isolation_flag else ‘o’
ax3a.scatter(x,y,s=max(30,h*200),color=c,marker=marker,zorder=5,edgecolors=‘white’,linewidth=0.5)
# Draw edges
for j in range(i+1,N):
if A_base[i,j]>0:
xj=r_offset*np.cos(angles[j]); yj=r_offset*np.sin(angles[j])
ax3a.plot([x,xj],[y,yj],color=’#333344’,lw=0.5,zorder=1)
ax3a.set_xlim(-1.3,1.3); ax3a.set_ylim(-1.3,1.3)
ax3a.text(0,-1.25,‘Green=healthy  Red=stressed  X=isolated’,color=’#8b949e’,fontsize=7,ha=‘center’)
ax3a.axis(‘off’)

# Row 3: federation stability design space

ax3b=fig.add_subplot(gs[3,1:]); sax(ax3b,“Federation Stability Design Space\nCascade firewall × Knowledge diversity”)
cf_v=np.linspace(0,1,100); kd_v2=np.linspace(0,1,100)
CF,KD2=np.meshgrid(cf_v,kd_v2)

# Stability: firewall contains cascades, diversity prevents monoculture collapse

fed_stab=(CF*KD2*(1-0.3*(1-CF)*(1-KD2)))**0.5
cf3=ax3b.contourf(cf_v,kd_v2,fed_stab,levels=20,cmap=‘RdYlGn’,alpha=0.85)
ax3b.contour(cf_v,kd_v2,fed_stab,levels=[0.25,0.50,0.75],
colors=[’#ff4444’,’#ffd43b’,’#51cf66’],linewidths=1.2)
fpts={‘Baseline’:(0.70,0.75,’#51cf66’),‘High diversity’:(0.70,0.90,’#74c0fc’),
‘Empire’:(0.45,0.50,’#ff922b’),‘Monoculture’:(0.65,0.35,’#ffd43b’)}
for lbl,(x,y,c) in fpts.items():
ax3b.scatter(x,y,color=c,s=60,zorder=6,edgecolors=‘white’,linewidth=0.5)
ax3b.annotate(lbl,(x,y),xytext=(6,4),textcoords=‘offset points’,color=c,fontsize=8)
ax3b.text(0.05,0.88,‘STABLE FEDERATION’,color=‘white’,fontsize=9,fontweight=‘bold’)
ax3b.text(0.55,0.05,‘MONOCULTURE\nCOLLAPSE’,color=‘white’,fontsize=8,fontweight=‘bold’)
ax3b.text(0.05,0.05,‘UNCONTAINED\nCASCADE’,color=‘white’,fontsize=8,fontweight=‘bold’)
ax3b.set_xlabel(‘Cascade firewall effectiveness’,color=’#8b949e’,fontsize=9)
ax3b.set_ylabel(‘Knowledge diversity index’,color=’#8b949e’,fontsize=9)
cb3=fig.colorbar(cf3,ax=ax3b,shrink=0.8); cb3.set_label(‘Federation stability’,color=’#8b949e’,fontsize=8)
ax3b.text(0.30,0.02,‘No central sovereign — stability emerges from node health + diversity + containment’,
transform=ax3b.transAxes,color=’#8b949e’,fontsize=8,style=‘italic’)

fig.text(0.5,0.978,‘FEDERATION LAYER — PLANET-SCALE NODE NETWORK’,ha=‘center’,color=’#e6edf3’,fontsize=14,fontweight=‘bold’)
fig.text(0.5,0.961,‘No central sovereign  |  Ecological flows are physical  |  Knowledge diversity prevents monoculture’,ha=‘center’,color=’#8b949e’,fontsize=9)
fig.text(0.5,0.945,‘Cascade containment via isolation protocol  |  Migration gated by assimilation capacity  |  Empire risk monitored continuously’,
ha=‘center’,color=’#8b949e’,fontsize=8.5)

plt.savefig(’/mnt/user-data/outputs/federation.png’,dpi=150,bbox_inches=‘tight’,facecolor=’#0d1117’)
plt.close()

print(“── FEDERATION RESULTS ──\n”)
for lbl,r,_ in scens:
print(f”{lbl:<25} mean_final={r[‘mean_health’][-1]:.3f}  min_final={r[‘min_health’][-1]:.3f}  isolated={int(r[‘n_isolated’][-1])}  empire={r[‘empire_risk’][-1]:.3f}”)

print(”\n── CASCADE CONTAINMENT ──”)
print(f”  Cascade stressed nodes (2,3,4) breach health 0.20: “, end=’’)
for i in [2,3,4]:
h=r_cascade[‘node_health’][i]
br=np.where(h<0.20)[0]
print(f”node{i} t={br[0]*0.1:.1f}” if len(br) else f”node{i} never”, end=’  ‘)
print()
print(f”  Adjacent nodes (1,5) affected: “, end=’’)
for i in [1,5]:
h=r_cascade[‘node_health’][i]
print(f”node{i} final={h[-1]:.3f}”, end=’  ’)
print()

print(”\n── KNOWLEDGE DIVERSITY ──”)
print(f”  Baseline final diversity:           {r_base[‘knowledge_diversity’][-1]:.3f}”)
print(f”  Industrial monoculture final:       {r_mono[‘knowledge_diversity’][-1]:.3f}”)
print(f”  High initial variance final:        {r_resilient[‘knowledge_diversity’][-1]:.3f}”)
print(f”  Diversity floor (0.40) breach (mono): “, end=’’)
br=np.where(r_mono[‘knowledge_diversity’]<0.40)[0]
print(f”t={br[0]*0.1:.1f}” if len(br) else “never”)
