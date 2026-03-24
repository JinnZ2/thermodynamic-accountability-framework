“””
NODE v3 — Intergenerational Production Integration
Knowledge transmission = production. Not a cost. Elder incapacity absorbed by apprentices.
IPI gated by structure — NOT energy surplus.
“””

import numpy as np
from collections import deque, Counter
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from dataclasses import dataclass

@dataclass
class NodeState:
soil_carbon:        float = 0.85
biodiversity:       float = 0.80
water_retention:    float = 0.75
K_kinesthetic:      float = 0.70
K_temporal:         float = 0.65
K_relational:       float = 0.70
K_skill:            float = 0.75
K_intuitive:        float = 0.60
K_institutional:    float = 0.85
K_digital:          float = 0.70
K_wisdom:           float = 0.55
ai_model_fidelity:  float = 0.80
ai_translation_bw:  float = 0.75
ai_transparency:    float = 0.85
power_concentration:float = 0.20
leadership_rotation:float = 0.80
dissent_protection: float = 0.75
regen_audit_score:  float = 0.80
food_resilience:    float = 0.70
water_resilience:   float = 0.75
energy_resilience:  float = 0.60
trade_dependency:   float = 0.35
energy_surplus:     float = 0.65
# v3 STRUCTURAL TRANSMISSION
IPI:                float = 0.72   # intergenerational production integration
age_segregation:    float = 0.25   # LOW good
specialization:     float = 0.30   # LOW good
mobility_disruption:float = 0.20   # LOW good
institutional_sub:  float = 0.35   # LOW good
elder_in_production:float = 0.75
elder_incapacity:   float = 0.10

CRITICAL_VARS = {
‘soil_carbon’:0.30, ‘biodiversity’:0.25, ‘water_retention’:0.30,
‘K_kinesthetic’:0.25, ‘K_temporal’:0.20, ‘K_relational’:0.25, ‘K_wisdom’:0.15,
‘power_concentration’:0.70,  # inverted
‘dissent_protection’:0.30, ‘food_resilience’:0.40,
‘ai_translation_bw’:0.30, ‘IPI’:0.25,
}

def node_health(s):
d = s.**dict**
scores = {}
for var, floor in CRITICAL_VARS.items():
val = d[var]
scores[var] = max(0,(floor-val)/floor) if var==‘power_concentration’ else max(0,(val-floor)/(1-floor))
mv = min(scores, key=scores.get)
return min(scores.values()), mv

def eco(s):  return (max(0,s.soil_carbon)*max(0,s.biodiversity)*max(0,s.water_retention))**(1/3)
def gov(s):  return (max(0,s.leadership_rotation)*max(0,s.dissent_protection)*max(0,1-s.power_concentration)*max(0,s.regen_audit_score))**0.25
def wisd(s): return (max(0,s.K_kinesthetic)*max(0,s.K_temporal)*max(0,s.K_relational)*max(0,s.K_intuitive))**0.25

def compute_IPI(s):
struct = ((1-max(0,s.age_segregation))*(1-max(0,s.specialization))*
(1-max(0,s.mobility_disruption))*(1-max(0,s.institutional_sub)))**0.25
elder_anchor = max(0,s.elder_in_production) + max(0,s.elder_incapacity)*0.8
return min(1.0, struct * elder_anchor)

class Lag:
def **init**(self, d, v): self.buf = deque([v]*d, maxlen=d)
def push(self, v): self.buf.appendleft(v)
def get(self): return self.buf[-1]

def update(s, stress, el, kl, dt=0.1):
ns = NodeState(**s.**dict**)
B   = stress.get(‘industrial_pressure’,0.0)
drg = stress.get(‘drought’,0.0)
ego = stress.get(‘ego_capture’,0.0)
aic = stress.get(‘ai_corruption’,0.0)
seg = stress.get(‘age_segregation_pressure’,0.0)
spc = stress.get(‘specialization_pressure’,0.0)
mob = stress.get(‘mobility_pressure’,0.0)

```
e = eco(s); g = gov(s); kp = max(0, s.K_institutional-0.6)*0.5

# Structural variables
ns.age_segregation    += dt*(0.03*B*(1-s.age_segregation)+0.04*seg*(1-s.age_segregation)-0.04*s.IPI*s.age_segregation)
ns.specialization     += dt*(0.04*B*(1-s.specialization)+0.03*spc*(1-s.specialization)-0.03*(1-s.age_segregation)*s.specialization)
ns.mobility_disruption+= dt*(0.02*B+0.05*mob-0.03*g*s.mobility_disruption)
ns.institutional_sub  += dt*(0.05*B*(1-s.institutional_sub)-0.04*s.IPI*s.institutional_sub)
ns.elder_incapacity   += dt*(0.005-0.01*e)
ns.elder_in_production+= dt*(0.02*(1-s.elder_in_production)-0.08*seg-0.05*s.institutional_sub-0.03*s.age_segregation)
ns.IPI = compute_IPI(ns)

# Ecological
ns.soil_carbon     += dt*(0.03*e*(1-s.soil_carbon)-0.05*B-0.08*drg)
ns.biodiversity    += dt*(0.04*e*(1-s.biodiversity)-0.06*B-0.03*kp)
ns.water_retention += dt*(0.03*(1-s.water_retention)-0.10*drg-0.04*B)
el.push(eco(ns)); ed = el.get()

# Knowledge — IPI-gated, NOT energy-gated
ns.K_kinesthetic += dt*(0.04*s.IPI*(1-s.K_kinesthetic)+0.02*s.K_kinesthetic*(1-s.K_kinesthetic)-0.12*B-0.05*kp-0.06*s.age_segregation)
ns.K_temporal    += dt*(0.03*s.IPI*(1-s.K_temporal)+0.01*s.K_temporal*(1-s.K_temporal)-0.06*B-0.08*s.mobility_disruption)
ns.K_relational  += dt*(0.025*ed*(1-s.K_relational)+0.02*s.IPI*ed-0.08*B-0.05*(1-ed))
ns.K_skill       += dt*(0.05*s.IPI*(1-s.K_skill)+0.03*g*(1-s.K_skill)-0.07*B-0.05*s.specialization)
ns.K_intuitive   += dt*(0.015*s.K_kinesthetic*s.K_temporal*(1-s.K_intuitive)-0.10*B-0.06*kp)
ns.K_institutional+= dt*(0.05*B*(1-s.K_institutional)-0.01+0.02*g)
ns.K_digital     += dt*(0.04*(1-s.K_digital)-0.15*aic)
ns.K_wisdom      += dt*(0.008*(wisd(s)-s.K_wisdom)-0.03*B)

kk = (max(0,ns.K_kinesthetic)*max(0,ns.K_temporal)*max(0,ns.K_relational))**(1/3)
kl.push(kk); kd = kl.get()

# AI
ns.ai_model_fidelity += dt*(0.03*(1-s.ai_model_fidelity)-0.20*aic)
ns.ai_translation_bw += dt*(0.02*(1-s.ai_translation_bw)-0.10*aic-0.05*(1-s.K_kinesthetic))
ns.ai_transparency   += dt*(0.02*(1-s.ai_transparency)-0.08*ego)

# Governance with passive drift
ns.power_concentration += dt*(0.003+0.03*ego*(1-s.power_concentration)-0.04*s.dissent_protection*s.power_concentration-0.02*kd*s.power_concentration)
ns.leadership_rotation += dt*(0.02*(1-s.leadership_rotation)-0.08*ego-0.05*s.power_concentration+0.03*kd)
ns.dissent_protection  += dt*(0.02*(1-s.dissent_protection)-0.10*ego-0.06*s.power_concentration+0.02*kd)
ns.regen_audit_score   += dt*(0.03*(ed-s.regen_audit_score)-0.05*ego)

# Economic
ns.energy_surplus    += dt*(0.04*e*(1-s.energy_surplus)-0.08*B-0.12*drg)
ns.food_resilience   += dt*(0.03*s.K_relational*e*(1-s.food_resilience)-0.06*B-0.04*drg)
ns.water_resilience  += dt*(0.03*s.water_retention*(1-s.water_resilience)-0.08*drg)
ns.energy_resilience += dt*(0.02*(1-s.energy_resilience)-0.04*B)
ns.trade_dependency  += dt*(0.04*B*(1-s.trade_dependency)-0.03*s.food_resilience)

for a in ns.__dict__: setattr(ns, a, max(0.0, min(1.0, getattr(ns,a))))
return ns
```

def run(stress, steps=400, onset=50):
s = NodeState()
el = Lag(20, eco(s)); kl = Lag(30, 0.68)
hist = {k:[] for k in s.**dict**}
hist.update({‘health’:[],‘limiting’:[],‘IPI_c’:[]})
for t in range(steps):
active = {k:(v if t>=onset else 0.0) for k,v in stress.items()}
s = update(s, active, el, kl)
for k in s.**dict**: hist[k].append(getattr(s,k))
h, lim = node_health(s)
hist[‘health’].append(h); hist[‘limiting’].append(lim); hist[‘IPI_c’].append(compute_IPI(s))
return {k: np.array(v) if k!=‘limiting’ else v for k,v in hist.items()}

scenarios = {
“Baseline”:                    {},
“Industrial (all)”:            {“industrial_pressure”:0.35,“age_segregation_pressure”:0.20,“specialization_pressure”:0.20},
“Age segregation only”:        {“age_segregation_pressure”:0.50},
“Mobility disruption only”:    {“mobility_pressure”:0.60},
“Specialization only”:         {“specialization_pressure”:0.55},
“Ego capture”:                 {“ego_capture”:0.40},
“Drought”:                     {“drought”:0.50},
“Structural+energy”:           {“industrial_pressure”:0.20,“age_segregation_pressure”:0.30,“mobility_pressure”:0.25,“specialization_pressure”:0.20},
}

clrs = {“Baseline”:’#51cf66’,“Industrial (all)”:’#ff6b6b’,“Age segregation only”:’#ff922b’,
“Mobility disruption only”:’#ffd43b’,“Specialization only”:’#74c0fc’,
“Ego capture”:’#cc77ff’,“Drought”:’#4488ff’,“Structural+energy”:’#ff2222’}

results = {n: run(s) for n,s in scenarios.items()}
T = np.arange(400)*0.1

fig = plt.figure(figsize=(22,20)); fig.patch.set_facecolor(’#0d1117’)
gs = gridspec.GridSpec(4,3,figure=fig,hspace=0.52,wspace=0.35)

def sax(ax,t):
ax.set_facecolor(’#161b22’); ax.tick_params(colors=’#8b949e’,labelsize=8)
ax.set_title(t,color=’#e6edf3’,fontsize=8.5,pad=5)
for sp in ax.spines.values(): sp.set_color(’#30363d’); sp.set_linewidth(0.5)
ax.axvline(5.0,color=’#333355’,lw=0.7,linestyle=’:’)
return ax

# Row 0: health all scenarios

ax0 = fig.add_subplot(gs[0,:2]); sax(ax0,“Node Health v3 — Structural Transmission\nIPI replaces labor_apprenticeship — not energy-gated”)
for n,h in results.items(): ax0.plot(T,h[‘health’],color=clrs[n],lw=1.8,label=n,alpha=0.9)
ax0.axhline(0.20,color=’#ff4444’,lw=0.8,linestyle=’–’,label=‘Critical’)
ax0.axhline(0.50,color=’#ffd43b’,lw=0.7,linestyle=’–’,label=‘Warning’)
ax0.set_ylim(0,1.1); ax0.legend(fontsize=6.5,facecolor=’#21262d’,labelcolor=’#e6edf3’,ncol=2)

# Row 0 right: structural variables baseline

ax0r = fig.add_subplot(gs[0,2]); sax(ax0r,“Structural Variables — Baseline”)
b = results[“Baseline”]
for v,c,l in [(‘IPI’,’#51cf66’,‘IPI’),(‘age_segregation’,’#ff922b’,‘Age seg’),
(‘specialization’,’#74c0fc’,‘Specialization’),
(‘mobility_disruption’,’#ffd43b’,‘Mobility’),(‘elder_in_production’,’#cc77ff’,‘Elder in prod’)]:
ax0r.plot(T,b[v],color=c,lw=1.5,label=l)
ax0r.set_ylim(0,1.1); ax0r.legend(fontsize=6.5,facecolor=’#21262d’,labelcolor=’#e6edf3’)

# Row 1: elder absorption

ax1a = fig.add_subplot(gs[1,0]); sax(ax1a,“Elder Incapacity Absorbed\nIPI resilient in integrated systems”)
ei_v = np.linspace(0,0.60,100)
ipi_int=[]; ipi_seg=[]
for ei in ei_v:
s1=NodeState(); s1.elder_incapacity=ei; s1.elder_in_production=max(0,0.90-ei)
ipi_int.append(compute_IPI(s1))
s2=NodeState(); s2.elder_incapacity=ei; s2.elder_in_production=max(0,0.90-ei); s2.age_segregation=0.55
ipi_seg.append(compute_IPI(s2))
ax1a.plot(ei_v,ipi_int,color=’#51cf66’,lw=2,label=‘Integrated (apprentices absorb)’)
ax1a.plot(ei_v,ipi_seg,color=’#ff6b6b’,lw=2,label=‘Segregated (no absorption)’)
ax1a.axhline(0.25,color=’#ff4444’,lw=0.7,linestyle=’–’,label=‘IPI floor’)
ax1a.set_xlabel(‘Elder incapacity fraction’,color=’#8b949e’,fontsize=8)
ax1a.set_ylabel(‘IPI’,color=’#8b949e’,fontsize=9)
ax1a.legend(fontsize=6.5,facecolor=’#21262d’,labelcolor=’#e6edf3’)

# Row 1: age seg vs drought on K_kinesthetic

ax1b = fig.add_subplot(gs[1,1]); sax(ax1b,“Structural vs Ecological Stressor\nAge segregation kills kinesthetic faster than drought”)
for n,c in [(“Baseline”,’#51cf66’),(“Age segregation only”,’#ff922b’),(“Drought”,’#4488ff’)]:
h=results[n]
ax1b.plot(T,h[‘K_kinesthetic’],color=c,lw=1.8,label=n)
ax1b.plot(T,h[‘IPI’],color=c,lw=1.0,linestyle=’–’)
ax1b.axhline(0.25,color=’#ff4444’,lw=0.7,linestyle=’:’)
ax1b.text(22,0.08,‘─ K_kinesthetic  – IPI’,color=’#8b949e’,fontsize=7)
ax1b.set_ylim(0,1.0); ax1b.legend(fontsize=6.5,facecolor=’#21262d’,labelcolor=’#e6edf3’)

# Row 1: IPI vs energy decoupling

ax1c = fig.add_subplot(gs[1,2]); sax(ax1c,“IPI vs Energy Surplus — Decoupled\nTransmission no longer energy-gated”)
for n,c in [(“Baseline”,’#51cf66’),(“Structural+energy”,’#ff2222’),(“Drought”,’#4488ff’),(“Age segregation only”,’#ff922b’)]:
h=results[n]
ax1c.scatter(h[‘energy_surplus’],h[‘IPI_c’],c=c,s=4,alpha=0.4,label=n[:20])
ax1c.set_xlabel(‘Energy surplus’,color=’#8b949e’,fontsize=8)
ax1c.set_ylabel(‘IPI’,color=’#8b949e’,fontsize=9)
ax1c.axhline(0.25,color=’#ff4444’,lw=0.7,linestyle=’–’)
ax1c.legend(fontsize=6,facecolor=’#21262d’,labelcolor=’#e6edf3’)

# Row 2: knowledge composite structural vs energy

ax2a = fig.add_subplot(gs[2,0]); sax(ax2a,“Knowledge Composite — Structural vs Energy Stress”)
kc = lambda h: (np.array(h[‘K_kinesthetic’])*np.array(h[‘K_temporal’])*np.array(h[‘K_skill’]))**(1/3)
for n,c in [(“Baseline”,’#51cf66’),(“Structural+energy”,’#ff2222’),(“Drought”,’#4488ff’)]:
h=results[n]
ax2a.plot(T,kc(h),color=c,lw=1.8,label=n)
ax2a.plot(T,h[‘energy_surplus’],color=c,lw=1.0,linestyle=’–’)
ax2a.text(22,0.06,‘─ K composite  – energy surplus’,color=’#8b949e’,fontsize=7)
ax2a.set_ylim(0,1.0); ax2a.legend(fontsize=6.5,facecolor=’#21262d’,labelcolor=’#e6edf3’)

# Row 2: phase portrait age_seg × K_kinesthetic

ax2b = fig.add_subplot(gs[2,1]); sax(ax2b,“Phase Portrait: Age Segregation × K_kinesthetic”)
for n,c in [(“Baseline”,’#51cf66’),(“Age segregation only”,’#ff922b’),(“Industrial (all)”,’#ff6b6b’),(“Structural+energy”,’#ff2222’)]:
h=results[n]
ax2b.plot(h[‘age_segregation’],h[‘K_kinesthetic’],color=c,lw=1.4,label=n[:20],alpha=0.9)
ax2b.scatter(h[‘age_segregation’][0],h[‘K_kinesthetic’][0],color=c,s=20,zorder=5)
ax2b.scatter(h[‘age_segregation’][-1],h[‘K_kinesthetic’][-1],color=c,s=20,marker=‘X’,zorder=5)
ax2b.axhline(0.25,color=’#ff4444’,lw=0.7,linestyle=’–’)
ax2b.set_xlabel(‘Age segregation’,color=’#8b949e’,fontsize=8)
ax2b.set_ylabel(‘K_kinesthetic’,color=’#8b949e’,fontsize=9)
ax2b.legend(fontsize=6.5,facecolor=’#21262d’,labelcolor=’#e6edf3’)

# Row 2: mobility kills temporal

ax2c = fig.add_subplot(gs[2,2]); sax(ax2c,“Mobility → K_temporal Collapse\nResidency required for temporal knowledge”)
for n,c in [(“Baseline”,’#51cf66’),(“Mobility disruption only”,’#ffd43b’),(“Industrial (all)”,’#ff6b6b’)]:
h=results[n]
ax2c.plot(T,h[‘K_temporal’],color=c,lw=1.8,label=n)
ax2c.plot(T,h[‘mobility_disruption’],color=c,lw=1.0,linestyle=’–’)
ax2c.text(22,0.08,‘─ K_temporal  – mobility’,color=’#8b949e’,fontsize=7)
ax2c.set_ylim(0,1.0); ax2c.legend(fontsize=6.5,facecolor=’#21262d’,labelcolor=’#e6edf3’)

# Row 3: collapse speed

ax3a = fig.add_subplot(gs[3,0]); sax(ax3a,“Collapse Speed by Stressor\n(time to critical floor)”)
bt={}
for n,h in results.items():
if n==“Baseline”: continue
br=np.where(np.array(h[‘health’])<0.20)[0]
bt[n]=br[0]*0.1 if len(br) else 400
sbt=sorted(bt.items(),key=lambda x:x[1])
bns=[x[0] for x in sbt]; bvs=[x[1] for x in sbt]
bcs=[’#ff2222’ if v<20 else ‘#ff922b’ if v<40 else ‘#51cf66’ for v in bvs]
ax3a.barh(range(len(bns)),bvs,color=bcs)
ax3a.set_yticks(range(len(bns))); ax3a.set_yticklabels([n[:26] for n in bns],fontsize=7.5,color=’#e6edf3’)
ax3a.set_xlabel(‘Time to critical breach’,color=’#8b949e’,fontsize=8)
ax3a.axvline(400,color=’#51cf66’,lw=0.7,linestyle=’–’)

# Row 3: IPI design space

ax3b = fig.add_subplot(gs[3,1:]); sax(ax3b,“IPI Design Space: Age Segregation × Mobility\nRequired structural conditions for knowledge viability”)
sv=np.linspace(0,0.8,100); mv=np.linspace(0,0.8,100)
SEG,MOB=np.meshgrid(sv,mv)
def ipi_s(sg,mb,sp=0.25,isb=0.30,el=0.85,ei=0.10):
return np.minimum(1.0,((1-sg)*(1-sp)*(1-mb)*(1-isb))**0.25*(el+ei*0.8))
IM=ipi_s(SEG,MOB)
cf=ax3b.contourf(sv,mv,IM,levels=20,cmap=‘RdYlGn’,alpha=0.85)
ax3b.contour(sv,mv,IM,levels=[0.25,0.50,0.75],colors=[’#ff4444’,’#ffd43b’,’#51cf66’],linewidths=1.2)
ax3b.text(0.05,0.70,‘CRITICAL\nIPI<0.25’,color=‘white’,fontsize=8,fontweight=‘bold’)
ax3b.text(0.05,0.08,‘STABLE\nIPI>0.75’,color=‘white’,fontsize=8,fontweight=‘bold’)
ax3b.set_xlabel(‘Age segregation’,color=’#8b949e’,fontsize=9)
ax3b.set_ylabel(‘Mobility disruption’,color=’#8b949e’,fontsize=9)
cb=fig.colorbar(cf,ax=ax3b,shrink=0.8); cb.set_label(‘IPI’,color=’#8b949e’,fontsize=8)
ax3b.text(0.40,0.02,‘Both axes structural — energy surplus does not appear’,
transform=ax3b.transAxes,color=’#8b949e’,fontsize=8,style=‘italic’)

fig.text(0.5,0.978,‘NODE v3 — INTERGENERATIONAL PRODUCTION INTEGRATION’,ha=‘center’,color=’#e6edf3’,fontsize=13,fontweight=‘bold’)
fig.text(0.5,0.960,‘Transmission = production.  Elder incapacity absorbed.  IPI gated by structure — NOT energy.’,ha=‘center’,color=’#8b949e’,fontsize=9)

plt.savefig(’/mnt/user-data/outputs/node_100k_v3.png’,dpi=150,bbox_inches=‘tight’,facecolor=’#0d1117’)
plt.close()

print(“── NODE v3 RESULTS ──\n”)
for n,h in results.items():
br=np.where(np.array(h[‘health’])<0.20)[0]
bt=f”t={br[0]*0.1:.1f}” if len(br) else “never”
top=Counter(h[‘limiting’][50:]).most_common(1)[0][0]
print(f”{n:<35} final={h[‘health’][-1]:.3f}  breach={bt:<10} limit={top}”)

print(”\n── STRUCTURAL VS ENERGY ──”)
st=results[“Structural+energy”]; dr=results[“Drought”]
print(f”  Structural final K_kin: {st[‘K_kinesthetic’][-1]:.3f}”)
print(f”  Drought final K_kin:    {dr[‘K_kinesthetic’][-1]:.3f}”)
print(f”  IPI/energy correlation (structural): {np.corrcoef(st[‘IPI_c’],st[‘energy_surplus’])[0,1]:.3f}”)
print(f”  IPI/energy correlation (drought):    {np.corrcoef(dr[‘IPI_c’],dr[‘energy_surplus’])[0,1]:.3f}”)
