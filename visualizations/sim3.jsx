import { useState, useEffect, useCallback, useRef } from “react”;

// ═══════════════════════════════════════════════════════════════
// CONSTANTS
// ═══════════════════════════════════════════════════════════════

const NEEDS = [“safety”, “autonomy”, “connection”, “meaning”, “resources”];

const ENERGY = {
BASE_METABOLIC_COST: 0.5,
EMPATHY_COST: 0.3,
RESILIENCE_GAIN: 0.2,
};

const MOTIVATION_TYPES = {
self: { label: “Self-Max”, color: “#e05252”, icon: “◆”, weight: { self: 1.0, other: 0.0, future: 0.0, community: 0.0 } },
relational: { label: “Relational”, color: “#52b4e0”, icon: “◇”, weight: { self: 0.3, other: 0.5, future: 0.1, community: 0.1 } },
communal: { label: “Communal”, color: “#52e088”, icon: “○”, weight: { self: 0.15, other: 0.2, future: 0.15, community: 0.5 } },
sacred: { label: “Sacred-Val”, color: “#e0a852”, icon: “✧”, weight: { self: 0.1, other: 0.2, future: 0.3, community: 0.4 } },
kinship: { label: “Kinship”, color: “#b490e0”, icon: “△”, weight: { self: 0.1, other: 0.3, future: 0.35, community: 0.25 } },
};

const ENV_EVENTS = [
{ name: “Drought”, effect: { tension: 0.3, resources: -20 }, duration: 8, prob: 0.02 },
{ name: “Market Collapse”, effect: { tension: 0.2, resources: -30 }, duration: 12, prob: 0.015 },
{ name: “Migration”, effect: { tension: 0.15, connection: -10 }, duration: 10, prob: 0.02 },
{ name: “Regime Change”, effect: { tension: 0.4, safety: -25 }, duration: 15, prob: 0.01 },
{ name: “Climate Shock”, effect: { tension: 0.25, resources: -15, safety: -10 }, duration: 20, prob: 0.015 },
{ name: “Trade Opening”, effect: { tension: -0.15, resources: 15 }, duration: 10, prob: 0.025 },
{ name: “Cultural Exchange”, effect: { tension: -0.1, connection: 15 }, duration: 8, prob: 0.03 },
{ name: “Abundance”, effect: { tension: -0.2, resources: 20 }, duration: 6, prob: 0.025 },
];

const SCENARIOS = {
resource: { name: “Resource Negotiation”, desc: “Competing for water, land, trade routes”, tension: 0.4, icon: “⛏”, enforcementBias: 0.6, structuralJustice: 0.3 },
territorial: { name: “Territorial Dispute”, desc: “Overlapping sovereignty, historical grievances”, tension: 0.7, icon: “🗺”, enforcementBias: 0.7, structuralJustice: 0.2 },
cultural: { name: “Cultural Friction”, desc: “Value collision — autonomy vs collective, sacred vs secular”, tension: 0.5, icon: “🌀”, enforcementBias: 0.5, structuralJustice: 0.4 },
crisis: { name: “Active Crisis”, desc: “Military escalation, humanitarian emergency”, tension: 0.9, icon: “🔥”, enforcementBias: 0.8, structuralJustice: 0.1 },
trade: { name: “Trade Agreement”, desc: “Economic interdependence, asymmetric power”, tension: 0.3, icon: “⚖”, enforcementBias: 0.5, structuralJustice: 0.5 },
};

// ═══════════════════════════════════════════════════════════════
// AGENT FACTORY
// ═══════════════════════════════════════════════════════════════

function createAgent(id, framework, motivationType = “self”, powerOverrides = {}) {
const isNvc = framework === “nvc”;
const isHawk = motivationType === “self”;
return {
id, framework, motivationType,
motWeights: { …MOTIVATION_TYPES[motivationType].weight },
needs: Object.fromEntries(NEEDS.map(n => [n, 35 + Math.random() * 30])),
utility: 50, utilityHistory: [50], needsHistory: [],
empathyBandwidth: isNvc ? 0.5 + Math.random() * 0.2 : 0.15 + Math.random() * 0.1,
connectionCapacity: isNvc ? 0.5 + Math.random() * 0.15 : 0.2,
selfAwareness: isNvc ? 0.5 : 0.2,
neuroplasticity: isNvc ? 0.3 : 0.05,
cooperateRate: isHawk ? 0.4 : motivationType === “communal” ? 0.75 : 0.55,
cooperateHistory: [],
motDrift: [],
// Energy layer
internalEnergy: 60 + Math.random() * 20,
socialEnergy: 40 + Math.random() * 20,
internalEnergyHistory: [],
socialEnergyHistory: [],
burnoutAccumulator: 0,
// Power layer
power: {
material: isNvc ? 0.3 : (isHawk ? 0.7 : 0.4),
institutional: isNvc ? 0.2 : 0.5,
narrative: isNvc ? 0.4 : 0.5,
mobility: isNvc ? 0.4 : 0.6,
…powerOverrides,
},
// Phase tracking
phase: “active”, // active | strained | burnout | collapsed
phaseHistory: [],
};
}

function getPhase(agent) {
if (agent.internalEnergy < 10) return “collapsed”;
if (agent.burnoutAccumulator > 15) return “burnout”;
if (agent.internalEnergy < 30 || agent.socialEnergy < 20) return “strained”;
return “active”;
}

function powerIndex(agent) {
const p = agent.power;
return (p.material + p.institutional + p.narrative + p.mobility) / 4;
}

// ═══════════════════════════════════════════════════════════════
// INTERACTION ENGINES
// ═══════════════════════════════════════════════════════════════

function classicalInteract(a1, a2, env) {
const t = env.tension;
const eb = env.enforcementBias;

// Metabolic cost
[a1, a2].forEach(a => {
a.internalEnergy = Math.max(0, a.internalEnergy - ENERGY.BASE_METABOLIC_COST * (1 + t));
});

const noise1 = (Math.random() - 0.5) * t * 0.3;
const noise2 = (Math.random() - 0.5) * t * 0.3;
const c1 = Math.random() < (a1.cooperateRate + noise1);
const c2 = Math.random() < (a2.cooperateRate + noise2);

let raw1, raw2;
if (c1 && c2) { raw1 = 3; raw2 = 3; }
else if (c1 && !c2) { raw1 = 0; raw2 = 5; }
else if (!c1 && c2) { raw1 = 5; raw2 = 0; }
else { raw1 = 1; raw2 = 1; }

raw1 *= (1 - t * 0.3);
raw2 *= (1 - t * 0.3);

// Power-weighted payoffs — enforcement bias amplifies high-power gains
const pi1 = powerIndex(a1);
const pi2 = powerIndex(a2);
raw1 *= (1 + eb * (pi1 - 0.5));
raw2 *= (1 + eb * (pi2 - 0.5));

// Motivation-weighted utility
const cW = (raw1 + raw2) / 10;
const eff1 = a1.motWeights.self * raw1 + a1.motWeights.other * raw2 + a1.motWeights.community * cW;
const eff2 = a2.motWeights.self * raw2 + a2.motWeights.other * raw1 + a2.motWeights.community * cW;

// Minimal adaptation
if (!c2) a1.cooperateRate = Math.max(0.05, a1.cooperateRate - 0.03);
if (c2) a1.cooperateRate = Math.min(0.95, a1.cooperateRate + 0.01);
if (!c1) a2.cooperateRate = Math.max(0.05, a2.cooperateRate - 0.03);
if (c1) a2.cooperateRate = Math.min(0.95, a2.cooperateRate + 0.01);

a1.cooperateHistory.push(c1 ? 1 : 0);
a2.cooperateHistory.push(c2 ? 1 : 0);

for (const need of NEEDS) {
a1.needs[need] = Math.max(5, Math.min(100, a1.needs[need] + (c2 ? 1 : -2) - t * 1.5));
a2.needs[need] = Math.max(5, Math.min(100, a2.needs[need] + (c1 ? 1 : -2) - t * 1.5));
}

[a1, a2].forEach(a => {
const avg = Object.values(a.needs).reduce((s, v) => s + v, 0) / NEEDS.length;
a.utility = Math.max(0, Math.min(100, avg));
const dE = (avg - 50) / 100 * ENERGY.RESILIENCE_GAIN;
a.internalEnergy = Math.max(0, Math.min(100, a.internalEnergy + dE));
a.socialEnergy = Math.max(0, Math.min(100, a.socialEnergy + (c1 && c2 ? 0.5 : -0.8) - t * 0.3));
a.internalEnergyHistory.push(a.internalEnergy);
a.socialEnergyHistory.push(a.socialEnergy);
a.utilityHistory.push(a.utility);
a.needsHistory.push({ …a.needs });
a.phase = getPhase(a);
a.phaseHistory.push(a.phase);
});
}

function nvcInteract(a1, a2, env) {
const t = env.tension;
const eb = env.enforcementBias;
const sj = env.structuralJustice;

// 0. Metabolic cost
[a1, a2].forEach(a => {
a.internalEnergy = Math.max(0, a.internalEnergy - ENERGY.BASE_METABOLIC_COST * (1 + t));
});

// 1. Self-empathy
const clarity1 = a1.selfAwareness * (0.6 + Math.random() * 0.4);
const clarity2 = a2.selfAwareness * (0.6 + Math.random() * 0.4);

// 2. Felt empathic reception
const felt1 = a2.empathyBandwidth * (1 - t * 0.4) * clarity1;
const felt2 = a1.empathyBandwidth * (1 - t * 0.4) * clarity2;

// Energy cost of feeling under stress
[[a2, felt1], [a1, felt2]].forEach(([agent, felt]) => {
const cost = ENERGY.EMPATHY_COST * felt * (1 + t) * (1 + (1 - agent.power.mobility));
agent.internalEnergy = Math.max(0, agent.internalEnergy - cost);
});

// 3. Enacted empathy — structural gate
const enacted1 = felt1 * a2.power.institutional * (sj + (1 - eb));
const enacted2 = felt2 * a1.power.institutional * (sj + (1 - eb));
const mutualUnderstanding = (enacted1 + enacted2) / 2;

// 4. Creative space
const creative = mutualUnderstanding * a1.connectionCapacity * a2.connectionCapacity;

// 5. Needs with structural gate
const structuralGate = 0.3 * sj + 0.7 * (1 - eb);

for (const need of NEEDS) {
const d1 = Math.max(0, 70 - a1.needs[need]);
const d2 = Math.max(0, 70 - a2.needs[need]);
const gain = creative * structuralGate * 0.4;

```
// Motivation diversity bonus — different types find more creative solutions
const otherW1 = a1.motWeights.other + a1.motWeights.community * 0.5;
const otherW2 = a2.motWeights.other + a2.motWeights.community * 0.5;

a1.needs[need] = Math.min(100, a1.needs[need] + d1 * gain * (1 + otherW2 * 0.3));
a2.needs[need] = Math.min(100, a2.needs[need] + d2 * gain * (1 + otherW1 * 0.3));
a1.needs[need] = Math.max(5, a1.needs[need] - t * 2);
a2.needs[need] = Math.max(5, a2.needs[need] - t * 2);
```

}

// 6. Neuroplasticity — gated by structure
if (mutualUnderstanding > 0.3 && structuralGate > 0.3) {
[a1, a2].forEach(a => {
a.empathyBandwidth = Math.min(1, a.empathyBandwidth + a.neuroplasticity * 0.02);
a.connectionCapacity = Math.min(1, a.connectionCapacity + a.neuroplasticity * 0.015);
a.selfAwareness = Math.min(1, a.selfAwareness + a.neuroplasticity * 0.01);
a.burnoutAccumulator = Math.max(0, a.burnoutAccumulator - 0.3);
});
// Motivation drift through contact
if (a2.motWeights.future > 0.2) {
a1.motWeights.future = Math.min(0.5, a1.motWeights.future + 0.002);
a1.motWeights.self = Math.max(0.05, a1.motWeights.self - 0.001);
}
if (a1.motWeights.community > 0.3) {
a2.motWeights.community = Math.min(0.6, a2.motWeights.community + 0.002);
a2.motWeights.self = Math.max(0.05, a2.motWeights.self - 0.001);
}
} else if (mutualUnderstanding > 0.2 && structuralGate < 0.15) {
// BURNOUT — empathy hitting structural wall
[a1, a2].forEach(a => {
a.connectionCapacity = Math.max(0.1, a.connectionCapacity - 0.012);
a.burnoutAccumulator += 0.5;
a.internalEnergy = Math.max(0, a.internalEnergy - 0.3);
});
} else {
[a1, a2].forEach(a => {
a.empathyBandwidth = Math.max(0.1, a.empathyBandwidth - 0.008);
});
}

[a1, a2].forEach(a => { a.motDrift.push({ …a.motWeights }); });

// 7. Utility and energy feedback
[a1, a2].forEach(a => {
const avg = Object.values(a.needs).reduce((s, v) => s + v, 0) / NEEDS.length;
a.utility = avg;
const dE = (avg - 50) / 100 * ENERGY.RESILIENCE_GAIN;
a.internalEnergy = Math.max(0, Math.min(100, a.internalEnergy + dE));
a.socialEnergy = Math.max(0, Math.min(100,
a.socialEnergy + mutualUnderstanding * 2 * structuralGate - t
));
a.internalEnergyHistory.push(a.internalEnergy);
a.socialEnergyHistory.push(a.socialEnergy);
a.utilityHistory.push(a.utility);
a.needsHistory.push({ …a.needs });
a.phase = getPhase(a);
a.phaseHistory.push(a.phase);
});

return { mutualUnderstanding, creative, felt: [felt1, felt2], enacted: [enacted1, enacted2], structuralGate };
}

function mixedInteract(nvcAgent, classAgent, env) {
const t = env.tension;
const eb = env.enforcementBias;
const sj = env.structuralJustice;

[nvcAgent, classAgent].forEach(a => {
a.internalEnergy = Math.max(0, a.internalEnergy - ENERGY.BASE_METABOLIC_COST * (1 + t));
});

const nvcClarity = nvcAgent.selfAwareness * (0.7 + Math.random() * 0.3);
const classCoops = Math.random() < classAgent.cooperateRate;

const feltRead = nvcAgent.empathyBandwidth * (1 - t * 0.3) * nvcClarity * 0.7;

// Energy cost to NVC agent
nvcAgent.internalEnergy = Math.max(0,
nvcAgent.internalEnergy - ENERGY.EMPATHY_COST * feltRead * (1 + t)
);

// Leverage — can empathy move the world?
const leverage = nvcAgent.power.narrative * nvcAgent.power.institutional * (sj + (1 - eb));
const effectiveRead = feltRead * leverage;

if (classCoops) {
const partial = effectiveRead * nvcAgent.connectionCapacity * 0.6;
for (const need of NEEDS) {
const d = Math.max(0, 70 - nvcAgent.needs[need]);
nvcAgent.needs[need] = Math.min(100, nvcAgent.needs[need] + d * partial * 0.2);
nvcAgent.needs[need] = Math.max(5, nvcAgent.needs[need] - t * 1.5);
}
classAgent.utility = Math.min(100, classAgent.utility + 2 * (1 + classAgent.power.material));

```
if (effectiveRead > 0.25) {
  classAgent.cooperateRate = Math.min(0.9, classAgent.cooperateRate + 0.004 * sj);
}
nvcAgent.burnoutAccumulator = Math.max(0, nvcAgent.burnoutAccumulator - 0.1);
```

} else {
for (const need of NEEDS) {
nvcAgent.needs[need] = Math.max(5, nvcAgent.needs[need] - t * 3);
}
classAgent.utility = Math.min(100, classAgent.utility + 3 * (1 + classAgent.power.material));
nvcAgent.empathyBandwidth = Math.max(0.1, nvcAgent.empathyBandwidth - 0.005 * (1 + eb));
nvcAgent.burnoutAccumulator += 0.3 * (1 + eb);
}

[nvcAgent, classAgent].forEach(a => {
const avg = Object.values(a.needs).reduce((s, v) => s + v, 0) / NEEDS.length;
if (a.framework === “nvc”) a.utility = avg;
const dE = (avg - 50) / 100 * ENERGY.RESILIENCE_GAIN;
a.internalEnergy = Math.max(0, Math.min(100, a.internalEnergy + dE));
a.socialEnergy = Math.max(0, Math.min(100, a.socialEnergy + (classCoops ? 0.3 : -1) - t * 0.3));
a.internalEnergyHistory.push(a.internalEnergy);
a.socialEnergyHistory.push(a.socialEnergy);
a.utilityHistory.push(a.utility);
a.needsHistory.push({ …a.needs });
a.phase = getPhase(a);
a.phaseHistory.push(a.phase);
});

return { classCoops, feltRead, effectiveRead, leverage };
}

// ═══════════════════════════════════════════════════════════════
// ENVIRONMENT
// ═══════════════════════════════════════════════════════════════

function createEnv(scenario) {
const sc = SCENARIOS[scenario];
return {
tension: sc.tension, baseTension: sc.tension,
enforcementBias: sc.enforcementBias, structuralJustice: sc.structuralJustice,
activeEvents: [], eventLog: [],
tensionHistory: [sc.tension],
ebHistory: [sc.enforcementBias], sjHistory: [sc.structuralJustice],
needsMod: Object.fromEntries(NEEDS.map(n => [n, 0])),
volatile: true,
};
}

function tickEnv(env, step) {
if (env.volatile) {
for (const tmpl of ENV_EVENTS) {
if (Math.random() < tmpl.prob) {
env.activeEvents.push({ …tmpl, startStep: step, endStep: step + tmpl.duration });
env.eventLog.push({ …tmpl, step });
}
}
}

let tMod = 0;
const nMod = Object.fromEntries(NEEDS.map(n => [n, 0]));
env.activeEvents = env.activeEvents.filter(e => {
if (step > e.endStep) return false;
tMod += e.effect.tension || 0;
for (const n of NEEDS) if (e.effect[n]) nMod[n] += e.effect[n];
return true;
});

env.tension = Math.max(0, Math.min(1, env.baseTension + tMod));
env.needsMod = nMod;
env.tensionHistory.push(env.tension);
env.ebHistory.push(env.enforcementBias);
env.sjHistory.push(env.structuralJustice);
}

function applyEnvNeeds(agent, env) {
for (const n of NEEDS) {
if (env.needsMod[n]) agent.needs[n] = Math.max(5, Math.min(100, agent.needs[n] + env.needsMod[n] * 0.1));
}
}

// ═══════════════════════════════════════════════════════════════
// PHASE DETECTION
// ═══════════════════════════════════════════════════════════════

function detectRegime(agents, env) {
const avgEnergy = agents.reduce((s, a) => s + a.internalEnergy, 0) / agents.length;
const avgSocial = agents.reduce((s, a) => s + a.socialEnergy, 0) / agents.length;
const avgEmpathy = agents.reduce((s, a) => s + a.empathyBandwidth, 0) / agents.length;
const avgBurnout = agents.reduce((s, a) => s + a.burnoutAccumulator, 0) / agents.length;
const sg = 0.3 * env.structuralJustice + 0.7 * (1 - env.enforcementBias);

if (avgEmpathy > 0.5 && sg > 0.4 && avgBurnout < 5) return { regime: “empathy-works”, color: “#52e088”, label: “Empathy Works” };
if (avgEmpathy > 0.4 && sg < 0.2 && avgBurnout > 8) return { regime: “burnout”, color: “#e05252”, label: “Empathy Burns Out” };
if (sg > 0.5 && avgEmpathy < 0.3) return { regime: “structure-only”, color: “#e0a852”, label: “Structure Alone (Brittle)” };
if (avgEmpathy > 0.5 && sg > 0.3 && avgEnergy > 40) return { regime: “resilient”, color: “#52b4e0”, label: “Empathy + Structure = Resilient” };
if (avgEnergy < 20) return { regime: “collapse”, color: “#e05252”, label: “System Collapse” };
return { regime: “transitional”, color: “#8890a0”, label: “Transitional” };
}

// ═══════════════════════════════════════════════════════════════
// VIS COMPONENTS
// ═══════════════════════════════════════════════════════════════

const C = {
bg: “#08090d”, surface: “#0f1117”, surfaceAlt: “#151820”,
border: “#1e222d”, borderLight: “#282e3a”,
classical: “#e05252”, nvc: “#52b4e0”, green: “#52e088”,
accent: “#e0a852”, purple: “#b490e0”, pink: “#e070a0”,
text: “#c8cdd8”, textDim: “#4e5565”, textMid: “#7a8294”,
danger: “#e05252”, safe: “#52e088”,
};

function Spark({ data, color, w = 180, h = 32, area = false }) {
if (!data || data.length < 2) return <svg width={w} height={h} />;
const max = Math.max(…data, 1); const min = Math.min(…data, 0);
const range = max - min || 1;
const pts = data.map((v, i) => [(i / (data.length - 1)) * w, h - ((v - min) / range) * (h - 4) - 2]);
const line = pts.map(p => p.join(”,”)).join(” “);
return (
<svg width={w} height={h} style={{ display: “block” }}>
{area && <polygon points={`0,${h} ${line} ${w},${h}`} fill={color + “10”} />}
<polyline points={line} fill="none" stroke={color} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
</svg>
);
}

function Radar({ needs, size = 105, color }) {
if (!needs) return null;
const cx = size / 2, cy = size / 2, r = size / 2 - 13;
const vals = NEEDS.map(n => (needs[n] || 0) / 100);
const s = (Math.PI * 2) / NEEDS.length;
const poly = (rad) => NEEDS.map((_, i) => `${cx + Math.cos(i * s - Math.PI / 2) * rad},${cy + Math.sin(i * s - Math.PI / 2) * rad}`).join(” “);
const dp = vals.map((v, i) => `${cx + Math.cos(i * s - Math.PI / 2) * r * v},${cy + Math.sin(i * s - Math.PI / 2) * r * v}`).join(” “);
return (
<svg width={size} height={size}>
{[0.33, 0.66, 1].map(sc => <polygon key={sc} points={poly(r * sc)} fill=“none” stroke={C.border} strokeWidth=“0.5” />)}
{NEEDS.map((n, i) => <text key={n} x={cx + Math.cos(i * s - Math.PI / 2) * (r + 10)} y={cy + Math.sin(i * s - Math.PI / 2) * (r + 10)} textAnchor=“middle” dominantBaseline=“middle” fill={C.textDim} fontSize=“7” fontFamily=”‘JetBrains Mono’,monospace”>{n.slice(0, 4)}</text>)}
<polygon points={dp} fill={color + “20”} stroke={color} strokeWidth=“1.5” />
</svg>
);
}

function G({ label, value, max = 100, color }) {
return (
<div style={{ marginBottom: 4 }}>
<div style={{ display: “flex”, justifyContent: “space-between”, fontSize: 9, fontFamily: “‘JetBrains Mono’,monospace”, color: C.textDim, marginBottom: 1 }}>
<span>{label}</span><span style={{ color }}>{value.toFixed(1)}</span>
</div>
<div style={{ height: 3, background: C.border, borderRadius: 2, overflow: “hidden” }}>
<div style={{ height: “100%”, width: `${Math.min(100, (value / max) * 100)}%`, background: color, borderRadius: 2, transition: “width 0.2s” }} />
</div>
</div>
);
}

function MotBar({ weights }) {
const keys = [“self”, “other”, “future”, “community”];
const colors = { self: C.classical, other: C.nvc, future: C.accent, community: C.green };
const total = keys.reduce((s, k) => s + (weights[k] || 0), 0) || 1;
return (
<div>
<div style={{ display: “flex”, height: 6, borderRadius: 2, overflow: “hidden”, border: `1px solid ${C.border}` }}>
{keys.map(k => <div key={k} style={{ width: `${(weights[k] / total) * 100}%`, background: colors[k], transition: “width 0.3s” }} />)}
</div>
<div style={{ display: “flex”, gap: 6, marginTop: 2 }}>
{keys.map(k => <span key={k} style={{ fontSize: 7, fontFamily: “‘JetBrains Mono’,monospace”, color: colors[k] }}>{k.slice(0, 3)} {((weights[k] / total) * 100).toFixed(0)}%</span>)}
</div>
</div>
);
}

function PhaseBadge({ phase }) {
const colors = { active: C.green, strained: C.accent, burnout: C.pink, collapsed: C.danger };
return (
<span style={{
display: “inline-block”, padding: “1px 6px”, borderRadius: 3,
fontSize: 8, fontFamily: “‘JetBrains Mono’,monospace”, fontWeight: 600,
background: (colors[phase] || C.textDim) + “20”,
color: colors[phase] || C.textDim,
border: `1px solid ${(colors[phase] || C.textDim) + "40"}`,
}}>{phase.toUpperCase()}</span>
);
}

function RegimeBadge({ regime }) {
return (
<div style={{
padding: “6px 10px”, borderRadius: 4,
background: regime.color + “12”,
border: `1px solid ${regime.color}40`,
fontSize: 12, fontFamily: “‘JetBrains Mono’,monospace”,
fontWeight: 600, color: regime.color,
textAlign: “center”,
}}>
◈ {regime.label}
</div>
);
}

function EventBadge({ event }) {
const pos = (event.effect.tension || 0) < 0;
return (
<span style={{
display: “inline-block”, padding: “1px 6px”, borderRadius: 3,
fontSize: 8, fontFamily: “‘JetBrains Mono’,monospace”,
background: (pos ? C.green : C.danger) + “15”,
color: pos ? C.green : C.danger,
border: `1px solid ${(pos ? C.green : C.danger) + "30"}`,
marginRight: 3,
}}>{event.name}</span>
);
}

// Agent panel
function AgentPanel({ agent, color, label }) {
return (
<div style={{ flex: 1 }}>
<div style={{ display: “flex”, justifyContent: “space-between”, alignItems: “center”, marginBottom: 4 }}>
<span style={{ fontSize: 10, fontFamily: “‘JetBrains Mono’,monospace”, color }}>
{MOTIVATION_TYPES[agent.motivationType]?.icon} {label}
</span>
<PhaseBadge phase={agent.phase} />
</div>
<div style={{ fontSize: 18, fontWeight: 600, fontFamily: “‘JetBrains Mono’,monospace”, color, marginBottom: 4 }}>
{agent.utility.toFixed(1)}
</div>
<G label="Internal Energy" value={agent.internalEnergy} color={C.accent} />
<G label="Social Energy" value={agent.socialEnergy} color={C.purple} />
<G label=“Power Index” value={powerIndex(agent) * 100} color={C.textMid} />
{agent.framework === “nvc” && (
<>
<G label=“Empathy BW” value={agent.empathyBandwidth * 100} color={C.nvc} />
<G label="Burnout" value={agent.burnoutAccumulator} max={20} color={C.pink} />
</>
)}
{agent.framework === “classical” && (
<G label=“Coop Rate” value={agent.cooperateRate * 100} color={C.classical} />
)}
<div style={{ marginTop: 4 }}><MotBar weights={agent.motWeights} /></div>
</div>
);
}

// ═══════════════════════════════════════════════════════════════
// MAIN APP
// ═══════════════════════════════════════════════════════════════

export default function ConflictSimV3() {
const [scenario, setScenario] = useState(“resource”);
const [running, setRunning] = useState(false);
const [speed, setSpeed] = useState(60);
const [step, setStep] = useState(0);

// Config overrides
const [ebOverride, setEbOverride] = useState(null);
const [sjOverride, setSjOverride] = useState(null);
const [volatile, setVolatile] = useState(true);
const [cMot1, setCMot1] = useState(“self”);
const [cMot2, setCMot2] = useState(“self”);
const [nMot1, setNMot1] = useState(“relational”);
const [nMot2, setNMot2] = useState(“kinship”);

// State
const [cA, setCA] = useState(null);
const [cB, setCB] = useState(null);
const [nA, setNA] = useState(null);
const [nB, setNB] = useState(null);
const [mN, setMN] = useState(null); // mixed nvc
const [mC, setMC] = useState(null); // mixed classical
const [env, setEnv] = useState(null);
const [nvcRegime, setNvcRegime] = useState(null);

const intervalRef = useRef(null);

const init = useCallback(() => {
setCA(createAgent(“C1”, “classical”, cMot1));
setCB(createAgent(“C2”, “classical”, cMot2));
setNA(createAgent(“N1”, “nvc”, nMot1));
setNB(createAgent(“N2”, “nvc”, nMot2));
setMN(createAgent(“MN”, “nvc”, nMot1));
setMC(createAgent(“MC”, “classical”, cMot1, { material: 0.7, institutional: 0.6 }));
const e = createEnv(scenario);
e.volatile = volatile;
if (ebOverride !== null) e.enforcementBias = ebOverride;
if (sjOverride !== null) e.structuralJustice = sjOverride;
setEnv(e);
setStep(0);
setNvcRegime(null);
}, [scenario, volatile, cMot1, cMot2, nMot1, nMot2, ebOverride, sjOverride]);

useEffect(() => { init(); }, [init]);

const tick = useCallback(() => {
if (!cA || !nA || !env) return;
tickEnv(env, step);
if (ebOverride !== null) env.enforcementBias = ebOverride;
if (sjOverride !== null) env.structuralJustice = sjOverride;

```
[cA, cB, nA, nB, mN, mC].forEach(a => applyEnvNeeds(a, env));

classicalInteract(cA, cB, env);
nvcInteract(nA, nB, env);
mixedInteract(mN, mC, env);

setNvcRegime(detectRegime([nA, nB], env));

setCA({ ...cA }); setCB({ ...cB });
setNA({ ...nA }); setNB({ ...nB });
setMN({ ...mN }); setMC({ ...mC });
setEnv({ ...env });
setStep(s => s + 1);
```

}, [cA, cB, nA, nB, mN, mC, env, step, ebOverride, sjOverride]);

useEffect(() => {
if (running) intervalRef.current = setInterval(tick, speed);
return () => clearInterval(intervalRef.current);
}, [running, tick, speed]);

if (!cA || !nA || !env) return null;

const sc = SCENARIOS[scenario];
const pnl = { background: C.surface, border: `1px solid ${C.border}`, borderRadius: 5, padding: 12 };
const lbl = { fontFamily: “‘JetBrains Mono’,monospace”, fontSize: 8, color: C.textDim, textTransform: “uppercase”, letterSpacing: “0.1em”, marginBottom: 6 };
const sel = { background: C.surface, border: `1px solid ${C.border}`, color: C.textMid, padding: “2px 5px”, borderRadius: 3, fontFamily: “‘JetBrains Mono’,monospace”, fontSize: 9 };

const cTotal = cA.utility + cB.utility;
const nTotal = nA.utility + nB.utility;
const mTotal = mN.utility + mC.utility;
const cTH = cA.utilityHistory.map((v, i) => v + (cB.utilityHistory[i] || 0));
const nTH = nA.utilityHistory.map((v, i) => v + (nB.utilityHistory[i] || 0));
const mTH = mN.utilityHistory.map((v, i) => v + (mC.utilityHistory[i] || 0));

const sg = 0.3 * env.structuralJustice + 0.7 * (1 - env.enforcementBias);

return (
<div style={{ background: C.bg, color: C.text, minHeight: “100vh”, padding: “14px 16px”, fontFamily: “‘Inter’,sans-serif” }}>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=DM+Sans:wght@400;500;700&display=swap" rel="stylesheet" />

```
  {/* HEADER */}
  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 12 }}>
    <div>
      <h1 style={{ fontFamily: "'DM Sans',sans-serif", fontSize: 16, fontWeight: 700, margin: 0, letterSpacing: "-0.02em" }}>
        Conflict Resolution Dynamics
      </h1>
      <div style={{ fontFamily: "'JetBrains Mono',monospace", fontSize: 9, color: C.textDim, marginTop: 2 }}>
        Energy · Power · Structure · Neuroplasticity — v3
      </div>
    </div>
    <div style={{ display: "flex", gap: 4, alignItems: "center" }}>
      <button onClick={() => setRunning(!running)} style={{
        background: running ? C.danger + "18" : C.green + "18",
        border: `1px solid ${running ? C.danger : C.green}`,
        color: running ? C.danger : C.green,
        padding: "4px 12px", borderRadius: 3, cursor: "pointer",
        fontFamily: "'JetBrains Mono',monospace", fontSize: 9, fontWeight: 600,
      }}>{running ? "■ PAUSE" : "▶ RUN"}</button>
      <button onClick={tick} disabled={running} style={{
        background: "transparent", border: `1px solid ${C.border}`,
        color: C.textDim, padding: "4px 8px", borderRadius: 3,
        cursor: running ? "default" : "pointer",
        fontFamily: "'JetBrains Mono',monospace", fontSize: 9, opacity: running ? 0.3 : 1,
      }}>STEP</button>
      <button onClick={() => { setRunning(false); init(); }} style={{
        background: "transparent", border: `1px solid ${C.border}`,
        color: C.textDim, padding: "4px 8px", borderRadius: 3, cursor: "pointer",
        fontFamily: "'JetBrains Mono',monospace", fontSize: 9,
      }}>RESET</button>
      <select value={speed} onChange={e => setSpeed(Number(e.target.value))} style={sel}>
        <option value={150}>Slow</option><option value={60}>Med</option><option value={15}>Fast</option>
      </select>
    </div>
  </div>

  {/* SCENARIO + CONFIG */}
  <div style={{ display: "grid", gridTemplateColumns: "auto 1fr", gap: 8, marginBottom: 10 }}>
    <div style={{ ...pnl, display: "flex", gap: 4, flexWrap: "wrap", padding: "8px 10px", alignItems: "center" }}>
      {Object.entries(SCENARIOS).map(([k, s]) => (
        <button key={k} onClick={() => { setScenario(k); setRunning(false); setEbOverride(null); setSjOverride(null); }}
          style={{
            background: scenario === k ? C.surfaceAlt : "transparent",
            border: `1px solid ${scenario === k ? C.accent : C.border}`,
            color: scenario === k ? C.accent : C.textDim,
            padding: "3px 8px", borderRadius: 3, cursor: "pointer",
            fontFamily: "'JetBrains Mono',monospace", fontSize: 9,
          }}>{s.icon} {s.name}</button>
      ))}
    </div>

    <div style={{ ...pnl, display: "flex", gap: 12, flexWrap: "wrap", alignItems: "center", padding: "8px 10px" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 4 }}>
        <span style={{ fontSize: 9, color: C.textDim, fontFamily: "'JetBrains Mono',monospace" }}>Volatile</span>
        <button onClick={() => setVolatile(!volatile)} style={{
          background: volatile ? C.accent + "20" : C.border,
          border: `1px solid ${volatile ? C.accent : C.border}`,
          color: volatile ? C.accent : C.textDim,
          padding: "2px 6px", borderRadius: 3, cursor: "pointer",
          fontFamily: "'JetBrains Mono',monospace", fontSize: 8,
        }}>{volatile ? "ON" : "OFF"}</button>
      </div>

      <div style={{ display: "flex", alignItems: "center", gap: 3 }}>
        <span style={{ fontSize: 9, color: C.danger, fontFamily: "'JetBrains Mono',monospace" }}>EnfBias</span>
        <input type="range" min={0} max={100} value={(ebOverride !== null ? ebOverride : sc.enforcementBias) * 100}
          onChange={e => setEbOverride(e.target.value / 100)} style={{ width: 60, accentColor: C.danger }} />
        <span style={{ fontSize: 9, color: C.danger, fontFamily: "'JetBrains Mono',monospace" }}>{((ebOverride !== null ? ebOverride : env.enforcementBias) * 100).toFixed(0)}%</span>
      </div>

      <div style={{ display: "flex", alignItems: "center", gap: 3 }}>
        <span style={{ fontSize: 9, color: C.green, fontFamily: "'JetBrains Mono',monospace" }}>StrJustice</span>
        <input type="range" min={0} max={100} value={(sjOverride !== null ? sjOverride : sc.structuralJustice) * 100}
          onChange={e => setSjOverride(e.target.value / 100)} style={{ width: 60, accentColor: C.green }} />
        <span style={{ fontSize: 9, color: C.green, fontFamily: "'JetBrains Mono',monospace" }}>{((sjOverride !== null ? sjOverride : env.structuralJustice) * 100).toFixed(0)}%</span>
      </div>

      <div style={{ display: "flex", alignItems: "center", gap: 3 }}>
        <span style={{ fontSize: 8, color: C.classical, fontFamily: "'JetBrains Mono',monospace" }}>C:</span>
        <select value={cMot1} onChange={e => setCMot1(e.target.value)} style={sel}>
          {Object.entries(MOTIVATION_TYPES).map(([k, v]) => <option key={k} value={k}>{v.icon} {v.label}</option>)}
        </select>
        <span style={{ fontSize: 8, color: C.textDim }}>v</span>
        <select value={cMot2} onChange={e => setCMot2(e.target.value)} style={sel}>
          {Object.entries(MOTIVATION_TYPES).map(([k, v]) => <option key={k} value={k}>{v.icon} {v.label}</option>)}
        </select>
      </div>

      <div style={{ display: "flex", alignItems: "center", gap: 3 }}>
        <span style={{ fontSize: 8, color: C.nvc, fontFamily: "'JetBrains Mono',monospace" }}>N:</span>
        <select value={nMot1} onChange={e => setNMot1(e.target.value)} style={sel}>
          {Object.entries(MOTIVATION_TYPES).map(([k, v]) => <option key={k} value={k}>{v.icon} {v.label}</option>)}
        </select>
        <span style={{ fontSize: 8, color: C.textDim }}>v</span>
        <select value={nMot2} onChange={e => setNMot2(e.target.value)} style={sel}>
          {Object.entries(MOTIVATION_TYPES).map(([k, v]) => <option key={k} value={k}>{v.icon} {v.label}</option>)}
        </select>
      </div>
    </div>
  </div>

  {/* ENVIRONMENT STRIP */}
  <div style={{ ...pnl, marginBottom: 10, padding: "6px 10px", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
      <span style={{ fontSize: 9, fontFamily: "'JetBrains Mono',monospace", color: C.textDim }}>STEP {step}</span>
      <div style={{ display: "flex", flexWrap: "wrap", gap: 2 }}>
        {env.activeEvents.map((e, i) => <EventBadge key={i} event={e} />)}
        {env.activeEvents.length === 0 && <span style={{ fontSize: 8, color: C.textDim, fontFamily: "'JetBrains Mono',monospace" }}>— quiet —</span>}
      </div>
    </div>
    <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
      <div style={{ textAlign: "right" }}>
        <Spark data={env.tensionHistory} color={C.accent} w={80} h={16} area />
        <div style={{ fontSize: 8, color: C.accent, fontFamily: "'JetBrains Mono',monospace" }}>tension {(env.tension * 100).toFixed(0)}%</div>
      </div>
      <div style={{ fontSize: 9, fontFamily: "'JetBrains Mono',monospace", color: C.textDim }}>
        gate <span style={{ color: sg > 0.4 ? C.green : sg > 0.2 ? C.accent : C.danger }}>{(sg * 100).toFixed(0)}%</span>
      </div>
      {nvcRegime && <RegimeBadge regime={nvcRegime} />}
    </div>
  </div>

  {/* THREE COLUMNS */}
  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 10 }}>

    {/* CLASSICAL */}
    <div style={pnl}>
      <div style={{ ...lbl, color: C.classical }}>● CLASSICAL</div>
      <div style={{ display: "flex", gap: 10, marginBottom: 8 }}>
        <AgentPanel agent={cA} color={C.classical} label={`A1 ${MOTIVATION_TYPES[cMot1].label}`} />
        <AgentPanel agent={cB} color={C.classical} label={`A2 ${MOTIVATION_TYPES[cMot2].label}`} />
      </div>
      <Spark data={cTH} color={C.classical} w={260} h={40} area />
      <div style={{ display: "flex", justifyContent: "space-between", marginTop: 2 }}>
        <span style={{ fontSize: 8, color: C.textDim, fontFamily: "'JetBrains Mono',monospace" }}>Combined Welfare</span>
        <span style={{ fontSize: 10, color: C.classical, fontFamily: "'JetBrains Mono',monospace", fontWeight: 600 }}>{cTotal.toFixed(1)}</span>
      </div>
      <div style={{ display: "flex", gap: 4, marginTop: 6 }}>
        <Radar needs={cA.needs} size={85} color={C.classical} />
        <Radar needs={cB.needs} size={85} color={C.classical} />
      </div>
      <div style={{ marginTop: 6, fontSize: 8, fontFamily: "'JetBrains Mono',monospace", color: C.textDim, lineHeight: 1.5 }}>
        <Spark data={cA.internalEnergyHistory} color={C.accent} w={120} h={14} />
        <span>Internal Energy ↑ (avg {((cA.internalEnergy + cB.internalEnergy) / 2).toFixed(0)})</span>
      </div>
    </div>

    {/* NVC */}
    <div style={pnl}>
      <div style={{ ...lbl, color: C.nvc }}>● NVC-SUBSTRATE</div>
      <div style={{ display: "flex", gap: 10, marginBottom: 8 }}>
        <AgentPanel agent={nA} color={C.nvc} label={`A1 ${MOTIVATION_TYPES[nMot1].label}`} />
        <AgentPanel agent={nB} color={C.nvc} label={`A2 ${MOTIVATION_TYPES[nMot2].label}`} />
      </div>
      <Spark data={nTH} color={C.nvc} w={260} h={40} area />
      <div style={{ display: "flex", justifyContent: "space-between", marginTop: 2 }}>
        <span style={{ fontSize: 8, color: C.textDim, fontFamily: "'JetBrains Mono',monospace" }}>Combined Welfare</span>
        <span style={{ fontSize: 10, color: C.nvc, fontFamily: "'JetBrains Mono',monospace", fontWeight: 600 }}>{nTotal.toFixed(1)}</span>
      </div>
      <div style={{ display: "flex", gap: 4, marginTop: 6 }}>
        <Radar needs={nA.needs} size={85} color={C.nvc} />
        <Radar needs={nB.needs} size={85} color={C.nvc} />
      </div>
      <div style={{ marginTop: 6, display: "flex", gap: 8 }}>
        <div style={{ flex: 1 }}>
          <Spark data={nA.internalEnergyHistory} color={C.accent} w={120} h={14} />
          <span style={{ fontSize: 8, fontFamily: "'JetBrains Mono',monospace", color: C.textDim }}>Int Energy {((nA.internalEnergy + nB.internalEnergy) / 2).toFixed(0)}</span>
        </div>
        <div style={{ flex: 1 }}>
          <Spark data={nA.socialEnergyHistory} color={C.purple} w={120} h={14} />
          <span style={{ fontSize: 8, fontFamily: "'JetBrains Mono',monospace", color: C.textDim }}>Soc Energy {((nA.socialEnergy + nB.socialEnergy) / 2).toFixed(0)}</span>
        </div>
      </div>
    </div>

    {/* MIXED */}
    <div style={pnl}>
      <div style={{ ...lbl, color: C.purple }}>● MIXED (NVC vs Classical)</div>
      <div style={{ display: "flex", gap: 10, marginBottom: 8 }}>
        <AgentPanel agent={mN} color={C.nvc} label="NVC Agent" />
        <AgentPanel agent={mC} color={C.classical} label="Classical Agent" />
      </div>
      <Spark data={mTH} color={C.purple} w={260} h={40} area />
      <div style={{ display: "flex", justifyContent: "space-between", marginTop: 2 }}>
        <span style={{ fontSize: 8, color: C.textDim, fontFamily: "'JetBrains Mono',monospace" }}>Combined Welfare</span>
        <span style={{ fontSize: 10, color: C.purple, fontFamily: "'JetBrains Mono',monospace", fontWeight: 600 }}>{mTotal.toFixed(1)}</span>
      </div>
      <div style={{ display: "flex", gap: 4, marginTop: 6 }}>
        <Radar needs={mN.needs} size={85} color={C.nvc} />
        <Radar needs={mC.needs} size={85} color={C.classical} />
      </div>
      <div style={{ marginTop: 6, fontSize: 8, fontFamily: "'JetBrains Mono',monospace", color: C.textDim, lineHeight: 1.6 }}>
        FELT → ENACTED gap: {step > 5 ? `NVC agent feeling at ${(mN.empathyBandwidth * 100).toFixed(0)}% bandwidth but structural leverage at ${(mN.power.narrative * mN.power.institutional * (env.structuralJustice + (1 - env.enforcementBias)) * 100).toFixed(0)}%` : "...measuring..."}
      </div>
    </div>
  </div>

  {/* BOTTOM PANELS */}
  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 10, marginTop: 10 }}>
    {/* Welfare comparison */}
    <div style={pnl}>
      <div style={lbl}>WELFARE DIVERGENCE</div>
      <div style={{ display: "flex", gap: 8, marginBottom: 4 }}>
        <Spark data={cTH} color={C.classical} w={85} h={30} area />
        <Spark data={nTH} color={C.nvc} w={85} h={30} area />
        <Spark data={mTH} color={C.purple} w={85} h={30} area />
      </div>
      <div style={{ display: "flex", justifyContent: "space-between", fontSize: 9, fontFamily: "'JetBrains Mono',monospace" }}>
        <span style={{ color: C.classical }}>C {cTotal.toFixed(0)}</span>
        <span style={{ color: C.nvc }}>N {nTotal.toFixed(0)}</span>
        <span style={{ color: C.purple }}>M {mTotal.toFixed(0)}</span>
      </div>
      {step > 20 && <div style={{ marginTop: 6, fontSize: 9, fontFamily: "'JetBrains Mono',monospace", color: C.accent }}>
        Δ(N-C) = {(nTotal - cTotal).toFixed(1)}
      </div>}
    </div>

    {/* Structural dynamics */}
    <div style={pnl}>
      <div style={lbl}>STRUCTURAL DYNAMICS</div>
      <G label="Enforcement Bias (favors power)" value={env.enforcementBias * 100} color={C.danger} />
      <G label="Structural Justice" value={env.structuralJustice * 100} color={C.green} />
      <G label="Structural Gate (combined)" value={sg * 100} color={sg > 0.4 ? C.green : sg > 0.2 ? C.accent : C.danger} />
      <div style={{ marginTop: 4, fontSize: 8, fontFamily: "'JetBrains Mono',monospace", color: C.textDim, lineHeight: 1.5 }}>
        {sg < 0.2 && "⚠ Gate nearly closed — empathy cannot materialize as structural change. Burnout pathway active."}
        {sg >= 0.2 && sg < 0.4 && "Gate partially open — NVC has limited leverage. Watch burnout accumulator."}
        {sg >= 0.4 && "Gate open — empathy can translate to structural outcomes. Growth pathway active."}
      </div>
    </div>

    {/* Event log */}
    <div style={pnl}>
      <div style={lbl}>EVENT LOG</div>
      <div style={{ fontSize: 8, fontFamily: "'JetBrains Mono',monospace", color: C.textDim, lineHeight: 1.7, maxHeight: 90, overflow: "auto" }}>
        {env.eventLog.length === 0 && "Awaiting perturbations..."}
        {env.eventLog.slice(-8).reverse().map((e, i) => (
          <div key={i}>
            <span style={{ color: (e.effect.tension || 0) < 0 ? C.green : C.danger }}>{(e.effect.tension || 0) < 0 ? "+" : "−"}</span>{" "}
            <span style={{ color: C.textMid }}>{e.name}</span>{" "}
            <span style={{ color: C.textDim }}>@{e.step}</span>
          </div>
        ))}
      </div>
    </div>
  </div>

  {/* INSIGHT */}
  {step > 25 && (
    <div style={{ ...pnl, marginTop: 10, borderColor: C.accent + "25" }}>
      <div style={{ ...lbl, color: C.accent }}>⚡ PHASE MAP</div>
      <div style={{ fontSize: 10, fontFamily: "'JetBrains Mono',monospace", color: C.textDim, lineHeight: 1.8 }}>
        {nvcRegime && nvcRegime.regime === "burnout" && (
          <div style={{ color: C.pink }}>→ BURNOUT REGIME: NVC agents feeling empathy but structural gate is closed. Empathy training without structural change = exploitation with better language.</div>
        )}
        {nvcRegime && nvcRegime.regime === "empathy-works" && (
          <div style={{ color: C.green }}>→ EMPATHY WORKS: Structural gate open + empathy bandwidth growing. NVC can translate feeling into material change.</div>
        )}
        {nvcRegime && nvcRegime.regime === "structure-only" && (
          <div style={{ color: C.accent }}>→ STRUCTURE ALONE: Rules constrain abuse but agents aren't growing. Stable but brittle — first perturbation breaks it.</div>
        )}
        {nvcRegime && nvcRegime.regime === "resilient" && (
          <div style={{ color: C.nvc }}>→ RESILIENT COOPERATION: Empathy + structure + energy = self-reinforcing. This is the only regime that survives perturbation AND grows.</div>
        )}
        {nvcRegime && nvcRegime.regime === "collapse" && (
          <div style={{ color: C.danger }}>→ SYSTEM COLLAPSE: Internal energy depleted. Agents cannot sustain participation regardless of framework.</div>
        )}
        {cA.cooperateRate < 0.25 && cB.cooperateRate < 0.25 && (
          <div style={{ marginTop: 4 }}>→ Classical defection spiral active. "Rational" agents producing irrational system outcome.</div>
        )}
        {mN.burnoutAccumulator > 10 && (
          <div style={{ marginTop: 4, color: C.pink }}>→ Mixed NVC agent approaching burnout. Empathy under power asymmetry without structural justice = self-destruction.</div>
        )}
        <div style={{ marginTop: 6, color: C.textMid, borderTop: `1px solid ${C.border}`, paddingTop: 6 }}>
          Try: Crank enforcement bias to 90%, structural justice to 10%, run 100 steps.
          Then flip them. Same agents, same empathy — different structure → different world.
          The point: "empathy training" without changing enforcement bias just leads to nicer language over the same harm.
        </div>
      </div>
    </div>
  )}
</div>
```

);
}
