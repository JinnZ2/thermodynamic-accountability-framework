import { useState, useEffect, useCallback, useRef } from “react”;

// ═══════════════════════════════════════════════════════════════
// CONSTANTS & TYPES
// ═══════════════════════════════════════════════════════════════

const NEEDS = [“safety”, “autonomy”, “connection”, “meaning”, “resources”];

const MOTIVATION_TYPES = {
self: { label: “Self-Maximizing”, color: “#e05252”, icon: “◆”, weight: { self: 1.0, other: 0.0, future: 0.0, community: 0.0 } },
relational: { label: “Relational”, color: “#52b4e0”, icon: “◇”, weight: { self: 0.3, other: 0.5, future: 0.1, community: 0.1 } },
communal: { label: “Communal”, color: “#52e088”, icon: “○”, weight: { self: 0.15, other: 0.2, future: 0.15, community: 0.5 } },
sacred: { label: “Sacred-Value”, color: “#e0a852”, icon: “✧”, weight: { self: 0.1, other: 0.2, future: 0.3, community: 0.4 } },
kinship: { label: “Kinship/Land”, color: “#b490e0”, icon: “△”, weight: { self: 0.1, other: 0.3, future: 0.35, community: 0.25 } },
};

const ENV_EVENTS = [
{ name: “Drought/Scarcity”, effect: { tension: 0.3, resources: -20 }, duration: 8, prob: 0.02 },
{ name: “Market Collapse”, effect: { tension: 0.2, resources: -30 }, duration: 12, prob: 0.015 },
{ name: “Migration Influx”, effect: { tension: 0.15, connection: -10 }, duration: 10, prob: 0.02 },
{ name: “Regime Change”, effect: { tension: 0.4, safety: -25 }, duration: 15, prob: 0.01 },
{ name: “Climate Shock”, effect: { tension: 0.25, resources: -15, safety: -10 }, duration: 20, prob: 0.015 },
{ name: “Trade Opening”, effect: { tension: -0.15, resources: 15 }, duration: 10, prob: 0.025 },
{ name: “Cultural Exchange”, effect: { tension: -0.1, connection: 15 }, duration: 8, prob: 0.03 },
{ name: “Harvest/Abundance”, effect: { tension: -0.2, resources: 20 }, duration: 6, prob: 0.025 },
];

// ═══════════════════════════════════════════════════════════════
// AGENT FACTORY
// ═══════════════════════════════════════════════════════════════

function createAgent(id, framework, motivationType = “self”) {
const base = {
id,
framework, // “classical” | “nvc”
motivationType,
motWeights: { …MOTIVATION_TYPES[motivationType].weight },
needs: Object.fromEntries(NEEDS.map(n => [n, 35 + Math.random() * 30])),
utility: 50,
utilityHistory: [50],
needsHistory: [],
// Neuroplastic properties
empathyBandwidth: framework === “nvc” ? 0.5 + Math.random() * 0.2 : 0.15 + Math.random() * 0.1,
connectionCapacity: framework === “nvc” ? 0.5 + Math.random() * 0.15 : 0.2,
selfAwareness: framework === “nvc” ? 0.5 : 0.2,
neuroplasticity: framework === “nvc” ? 0.3 : 0.05,
// Classical properties
cooperateRate: motivationType === “self” ? 0.4 : motivationType === “communal” ? 0.75 : 0.55,
cooperateHistory: [],
// Transformation tracking
motDrift: [],
resilienceScore: 50,
resilienceHistory: [50],
};
base.needsHistory.push({ …base.needs });
return base;
}

// ═══════════════════════════════════════════════════════════════
// INTERACTION ENGINE
// ═══════════════════════════════════════════════════════════════

function computeEffectiveUtility(agent, selfPayoff, otherPayoff, communityWelfare, futureDiscount) {
const w = agent.motWeights;
return (
w.self * selfPayoff +
w.other * otherPayoff +
w.community * communityWelfare * 0.5 +
w.future * futureDiscount * selfPayoff
);
}

function classicalInteract(a1, a2, env) {
const t = env.tension;

// Decide based on cooperate rate + noise
const noise1 = (Math.random() - 0.5) * t * 0.3;
const noise2 = (Math.random() - 0.5) * t * 0.3;
const c1 = Math.random() < (a1.cooperateRate + noise1);
const c2 = Math.random() < (a2.cooperateRate + noise2);

// Raw payoffs
let raw1, raw2;
if (c1 && c2) { raw1 = 3; raw2 = 3; }
else if (c1 && !c2) { raw1 = 0; raw2 = 5; }
else if (!c1 && c2) { raw1 = 5; raw2 = 0; }
else { raw1 = 1; raw2 = 1; }

// Environmental modulation
raw1 *= (1 - t * 0.3);
raw2 *= (1 - t * 0.3);

// Effective utility through motivation lens
const communityW = (raw1 + raw2) / 10;
const eff1 = computeEffectiveUtility(a1, raw1, raw2, communityW, 0.8);
const eff2 = computeEffectiveUtility(a2, raw2, raw1, communityW, 0.8);

// Update — classical agents barely adapt
const adapt1 = a1.neuroplasticity;
if (!c2) a1.cooperateRate = Math.max(0.05, a1.cooperateRate - 0.03 * (1 - adapt1));
if (c2) a1.cooperateRate = Math.min(0.95, a1.cooperateRate + 0.01 * (1 + adapt1));
if (!c1) a2.cooperateRate = Math.max(0.05, a2.cooperateRate - 0.03 * (1 - adapt1));
if (c1) a2.cooperateRate = Math.min(0.95, a2.cooperateRate + 0.01 * (1 + adapt1));

a1.cooperateHistory.push(c1 ? 1 : 0);
a2.cooperateHistory.push(c2 ? 1 : 0);

// Needs affected by environment
for (const need of NEEDS) {
a1.needs[need] = Math.max(5, Math.min(100, a1.needs[need] + (c2 ? 1 : -2) - t * 1.5));
a2.needs[need] = Math.max(5, Math.min(100, a2.needs[need] + (c1 ? 1 : -2) - t * 1.5));
}

const avg1 = Object.values(a1.needs).reduce((s, v) => s + v, 0) / NEEDS.length;
const avg2 = Object.values(a2.needs).reduce((s, v) => s + v, 0) / NEEDS.length;
a1.utility = avg1 * 0.4 + eff1 * 12;
a2.utility = avg2 * 0.4 + eff2 * 12;
a1.utility = Math.max(0, Math.min(100, a1.utility));
a2.utility = Math.max(0, Math.min(100, a2.utility));
a1.utilityHistory.push(a1.utility);
a2.utilityHistory.push(a2.utility);
a1.needsHistory.push({ …a1.needs });
a2.needsHistory.push({ …a2.needs });

// Resilience = ability to maintain welfare under perturbation
const vol1 = a1.utilityHistory.length > 3 ? Math.abs(a1.utilityHistory[a1.utilityHistory.length - 1] - a1.utilityHistory[a1.utilityHistory.length - 3]) : 0;
a1.resilienceScore = Math.max(0, Math.min(100, 100 - vol1 * 3 - t * 20));
a2.resilienceScore = Math.max(0, Math.min(100, 100 - vol1 * 3 - t * 20));
a1.resilienceHistory.push(a1.resilienceScore);
a2.resilienceHistory.push(a2.resilienceScore);

return { cooperated: [c1, c2], payoffs: [eff1, eff2] };
}

function nvcInteract(a1, a2, env) {
const t = env.tension;

// Self-empathy: identify own needs
const clarity1 = a1.selfAwareness * (0.6 + Math.random() * 0.4);
const clarity2 = a2.selfAwareness * (0.6 + Math.random() * 0.4);

// Empathic reception — degraded by tension, enhanced by bandwidth
const reception1to2 = a1.empathyBandwidth * clarity1 * (1 - t * 0.35);
const reception2to1 = a2.empathyBandwidth * clarity2 * (1 - t * 0.35);

const mutualUnderstanding = (reception1to2 + reception2to1) / 2;

// Creative solution space — expands with connection
const creative = mutualUnderstanding * a1.connectionCapacity * a2.connectionCapacity;

// Motivation-weighted need satisfaction
for (const need of NEEDS) {
const deficit1 = Math.max(0, 75 - a1.needs[need]);
const deficit2 = Math.max(0, 75 - a2.needs[need]);

```
// NVC finds solutions that meet both parties' needs simultaneously
// Weighted by motivation type — communal/relational agents open more creative space
const otherWeight1 = a1.motWeights.other + a1.motWeights.community * 0.5;
const otherWeight2 = a2.motWeights.other + a2.motWeights.community * 0.5;

const boost1 = deficit1 * creative * (0.25 + otherWeight2 * 0.2);
const boost2 = deficit2 * creative * (0.25 + otherWeight1 * 0.2);

a1.needs[need] = Math.min(100, a1.needs[need] + boost1);
a2.needs[need] = Math.min(100, a2.needs[need] + boost2);

// Tension cost
a1.needs[need] = Math.max(5, a1.needs[need] - t * 1.5);
a2.needs[need] = Math.max(5, a2.needs[need] - t * 1.5);
```

}

// NEUROPLASTICITY — the key differentiator
if (mutualUnderstanding > 0.25) {
const np1 = a1.neuroplasticity;
const np2 = a2.neuroplasticity;
a1.empathyBandwidth = Math.min(1, a1.empathyBandwidth + np1 * 0.018);
a2.empathyBandwidth = Math.min(1, a2.empathyBandwidth + np2 * 0.018);
a1.connectionCapacity = Math.min(1, a1.connectionCapacity + np1 * 0.012);
a2.connectionCapacity = Math.min(1, a2.connectionCapacity + np2 * 0.012);
a1.selfAwareness = Math.min(1, a1.selfAwareness + np1 * 0.008);
a2.selfAwareness = Math.min(1, a2.selfAwareness + np2 * 0.008);

```
// Motivation can drift through contact — sacred-value and kinship agents
// influence others toward longer-term thinking
if (a2.motWeights.future > 0.2) {
  a1.motWeights.future = Math.min(0.5, a1.motWeights.future + 0.002);
  a1.motWeights.self = Math.max(0.05, a1.motWeights.self - 0.001);
}
if (a1.motWeights.community > 0.3) {
  a2.motWeights.community = Math.min(0.6, a2.motWeights.community + 0.002);
  a2.motWeights.self = Math.max(0.05, a2.motWeights.self - 0.001);
}
```

} else {
a1.empathyBandwidth = Math.max(0.1, a1.empathyBandwidth - 0.008);
a2.empathyBandwidth = Math.max(0.1, a2.empathyBandwidth - 0.008);
}

a1.motDrift.push({ …a1.motWeights });
a2.motDrift.push({ …a2.motWeights });

const avg1 = Object.values(a1.needs).reduce((s, v) => s + v, 0) / NEEDS.length;
const avg2 = Object.values(a2.needs).reduce((s, v) => s + v, 0) / NEEDS.length;
a1.utility = avg1;
a2.utility = avg2;
a1.utilityHistory.push(a1.utility);
a2.utilityHistory.push(a2.utility);
a1.needsHistory.push({ …a1.needs });
a2.needsHistory.push({ …a2.needs });

const vol1 = a1.utilityHistory.length > 3 ? Math.abs(a1.utility - a1.utilityHistory[a1.utilityHistory.length - 3]) : 0;
a1.resilienceScore = Math.max(0, Math.min(100, 100 - vol1 * 2 - t * 10 + creative * 30));
a2.resilienceScore = Math.max(0, Math.min(100, 100 - vol1 * 2 - t * 10 + creative * 30));
a1.resilienceHistory.push(a1.resilienceScore);
a2.resilienceHistory.push(a2.resilienceScore);

return { mutualUnderstanding, creative };
}

// ═══════════════════════════════════════════════════════════════
// ENVIRONMENT ENGINE
// ═══════════════════════════════════════════════════════════════

function createEnvironment(baseTension = 0.3) {
return {
tension: baseTension,
baseTension,
activeEvents: [],
eventLog: [],
tensionHistory: [baseTension],
needsMod: Object.fromEntries(NEEDS.map(n => [n, 0])),
volatile: true,
};
}

function tickEnvironment(env, step) {
if (!env.volatile) {
env.tensionHistory.push(env.tension);
return;
}

// Check for new events
for (const template of ENV_EVENTS) {
if (Math.random() < template.prob) {
const event = {
…template,
startStep: step,
endStep: step + template.duration,
};
env.activeEvents.push(event);
env.eventLog.push({ …event, step });
}
}

// Apply active events
let tensionMod = 0;
const needsMod = Object.fromEntries(NEEDS.map(n => [n, 0]));

env.activeEvents = env.activeEvents.filter(e => {
if (step > e.endStep) return false;
tensionMod += e.effect.tension || 0;
for (const need of NEEDS) {
if (e.effect[need]) needsMod[need] += e.effect[need];
}
return true;
});

env.tension = Math.max(0, Math.min(1, env.baseTension + tensionMod));
env.needsMod = needsMod;
env.tensionHistory.push(env.tension);
}

function applyEnvToNeeds(agent, env) {
for (const need of NEEDS) {
if (env.needsMod[need]) {
agent.needs[need] = Math.max(5, Math.min(100, agent.needs[need] + env.needsMod[need] * 0.1));
}
}
}

// ═══════════════════════════════════════════════════════════════
// VISUALIZATION
// ═══════════════════════════════════════════════════════════════

const C = {
bg: “#0a0c10”,
surface: “#111318”,
surfaceHover: “#181c24”,
border: “#222733”,
borderLight: “#2d3340”,
classical: “#e05252”,
nvc: “#52b4e0”,
green: “#52e088”,
accent: “#e0a852”,
purple: “#b490e0”,
text: “#c8cdd8”,
textDim: “#5c6370”,
textMid: “#8890a0”,
danger: “#e05252”,
safe: “#52e088”,
};

function Spark({ data, color, w = 200, h = 36, showArea = false }) {
if (!data || data.length < 2) return <svg width={w} height={h} />;
const max = Math.max(…data, 1);
const min = Math.min(…data, 0);
const range = max - min || 1;
const pts = data.map((v, i) => {
const x = (i / (data.length - 1)) * w;
const y = h - ((v - min) / range) * (h - 6) - 3;
return [x, y];
});
const line = pts.map(p => p.join(”,”)).join(” “);
const area = `0,${h} ${line} ${w},${h}`;
return (
<svg width={w} height={h} style={{ display: “block” }}>
{showArea && <polygon points={area} fill={color + “12”} />}
<polyline points={line} fill="none" stroke={color} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
</svg>
);
}

function Radar({ needs, size = 120, color }) {
if (!needs) return null;
const cx = size / 2, cy = size / 2, r = size / 2 - 14;
const vals = NEEDS.map(n => (needs[n] || 0) / 100);
const step = (Math.PI * 2) / NEEDS.length;
const poly = (radius) => NEEDS.map((_, i) => {
const a = i * step - Math.PI / 2;
return `${cx + Math.cos(a) * radius},${cy + Math.sin(a) * radius}`;
}).join(” “);
const dataPts = vals.map((v, i) => {
const a = i * step - Math.PI / 2;
return `${cx + Math.cos(a) * r * v},${cy + Math.sin(a) * r * v}`;
}).join(” “);
return (
<svg width={size} height={size}>
{[0.33, 0.66, 1].map(s => <polygon key={s} points={poly(r * s)} fill=“none” stroke={C.border} strokeWidth=“0.5” />)}
{NEEDS.map((n, i) => {
const a = i * step - Math.PI / 2;
return <text key={n} x={cx + Math.cos(a) * (r + 11)} y={cy + Math.sin(a) * (r + 11)} textAnchor=“middle” dominantBaseline=“middle” fill={C.textDim} fontSize=“7” fontFamily=”‘JetBrains Mono’,monospace”>{n.slice(0, 4).toUpperCase()}</text>;
})}
<polygon points={dataPts} fill={color + “20”} stroke={color} strokeWidth=“1.5” />
</svg>
);
}

function Gauge({ label, value, max = 100, color, small = false }) {
const pct = Math.min(100, (value / max) * 100);
return (
<div style={{ marginBottom: small ? 4 : 6 }}>
<div style={{ display: “flex”, justifyContent: “space-between”, fontSize: small ? 9 : 10, fontFamily: “‘JetBrains Mono’,monospace”, color: C.textDim, marginBottom: 2 }}>
<span>{label}</span>
<span style={{ color }}>{value.toFixed(small ? 0 : 1)}</span>
</div>
<div style={{ height: small ? 3 : 4, background: C.border, borderRadius: 2, overflow: “hidden” }}>
<div style={{ height: “100%”, width: `${pct}%`, background: color, borderRadius: 2, transition: “width 0.2s” }} />
</div>
</div>
);
}

function MotivationBar({ weights, size = “normal” }) {
const h = size === “small” ? 6 : 10;
const keys = [“self”, “other”, “future”, “community”];
const colors = { self: C.classical, other: C.nvc, future: C.accent, community: C.green };
const total = keys.reduce((s, k) => s + (weights[k] || 0), 0) || 1;
return (
<div>
<div style={{ display: “flex”, height: h, borderRadius: 3, overflow: “hidden”, border: `1px solid ${C.border}` }}>
{keys.map(k => (
<div key={k} style={{ width: `${(weights[k] / total) * 100}%`, background: colors[k], transition: “width 0.3s” }} />
))}
</div>
{size !== “small” && (
<div style={{ display: “flex”, gap: 8, marginTop: 3 }}>
{keys.map(k => (
<span key={k} style={{ fontSize: 8, fontFamily: “‘JetBrains Mono’,monospace”, color: colors[k] }}>
{k.slice(0, 4)} {((weights[k] / total) * 100).toFixed(0)}%
</span>
))}
</div>
)}
</div>
);
}

function EventBadge({ event }) {
const isPositive = (event.effect.tension || 0) < 0;
return (
<span style={{
display: “inline-block”,
padding: “2px 7px”,
borderRadius: 3,
fontSize: 9,
fontFamily: “‘JetBrains Mono’,monospace”,
background: isPositive ? C.green + “18” : C.danger + “18”,
color: isPositive ? C.green : C.danger,
border: `1px solid ${isPositive ? C.green + "30" : C.danger + "30"}`,
marginRight: 4,
marginBottom: 3,
}}>
{event.name}
</span>
);
}

// ═══════════════════════════════════════════════════════════════
// MAIN APP
// ═══════════════════════════════════════════════════════════════

export default function ConflictResolutionSim() {
// Config
const [baseTension, setBaseTension] = useState(0.4);
const [envVolatile, setEnvVolatile] = useState(true);
const [classicalMot1, setClassicalMot1] = useState(“self”);
const [classicalMot2, setClassicalMot2] = useState(“self”);
const [nvcMot1, setNvcMot1] = useState(“relational”);
const [nvcMot2, setNvcMot2] = useState(“kinship”);

// State
const [cA, setCA] = useState(null);
const [cB, setCB] = useState(null);
const [nA, setNA] = useState(null);
const [nB, setNB] = useState(null);
const [env, setEnv] = useState(null);
const [step, setStep] = useState(0);
const [running, setRunning] = useState(false);
const [speed, setSpeed] = useState(80);
const intervalRef = useRef(null);

const init = useCallback(() => {
setCA(createAgent(“C1”, “classical”, classicalMot1));
setCB(createAgent(“C2”, “classical”, classicalMot2));
setNA(createAgent(“N1”, “nvc”, nvcMot1));
setNB(createAgent(“N2”, “nvc”, nvcMot2));
const e = createEnvironment(baseTension);
e.volatile = envVolatile;
setEnv(e);
setStep(0);
}, [baseTension, envVolatile, classicalMot1, classicalMot2, nvcMot1, nvcMot2]);

useEffect(() => { init(); }, [init]);

const tick = useCallback(() => {
if (!cA || !nA || !env) return;

```
tickEnvironment(env, step);
applyEnvToNeeds(cA, env);
applyEnvToNeeds(cB, env);
applyEnvToNeeds(nA, env);
applyEnvToNeeds(nB, env);

classicalInteract(cA, cB, env);
nvcInteract(nA, nB, env);

setCA({ ...cA });
setCB({ ...cB });
setNA({ ...nA });
setNB({ ...nB });
setEnv({ ...env });
setStep(s => s + 1);
```

}, [cA, cB, nA, nB, env, step]);

useEffect(() => {
if (running) intervalRef.current = setInterval(tick, speed);
return () => clearInterval(intervalRef.current);
}, [running, tick, speed]);

if (!cA || !nA || !env) return null;

const panel = { background: C.surface, border: `1px solid ${C.border}`, borderRadius: 6, padding: 14 };
const label = { fontFamily: “‘JetBrains Mono’,monospace”, fontSize: 9, color: C.textDim, textTransform: “uppercase”, letterSpacing: “0.1em”, marginBottom: 6 };
const bigNum = (v, color) => <span style={{ fontFamily: “‘JetBrains Mono’,monospace”, fontSize: 20, fontWeight: 600, color }}>{v.toFixed(1)}</span>;

const cTotal = cA.utility + cB.utility;
const nTotal = nA.utility + nB.utility;
const cTotalHist = cA.utilityHistory.map((v, i) => v + (cB.utilityHistory[i] || 0));
const nTotalHist = nA.utilityHistory.map((v, i) => v + (nB.utilityHistory[i] || 0));

const selectStyle = {
background: C.surface,
border: `1px solid ${C.border}`,
color: C.textMid,
padding: “3px 6px”,
borderRadius: 3,
fontFamily: “‘JetBrains Mono’,monospace”,
fontSize: 10,
};

return (
<div style={{ background: C.bg, color: C.text, minHeight: “100vh”, padding: “16px 20px”, fontFamily: “‘Inter’,sans-serif” }}>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=DM+Sans:wght@400;500;700&display=swap" rel="stylesheet" />

```
  {/* HEADER */}
  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 16 }}>
    <div>
      <h1 style={{ fontFamily: "'DM Sans',sans-serif", fontSize: 18, fontWeight: 700, margin: 0 }}>
        Conflict Resolution Dynamics v2
      </h1>
      <div style={{ fontFamily: "'JetBrains Mono',monospace", fontSize: 10, color: C.textDim, marginTop: 3 }}>
        Three axiom failures exposed — volatile environment · diverse motivation · neuroplastic agents
      </div>
    </div>
    <div style={{ display: "flex", gap: 6, alignItems: "center" }}>
      <button onClick={() => setRunning(!running)} style={{
        background: running ? C.danger + "20" : C.green + "20",
        border: `1px solid ${running ? C.danger : C.green}`,
        color: running ? C.danger : C.green,
        padding: "5px 14px", borderRadius: 4, cursor: "pointer",
        fontFamily: "'JetBrains Mono',monospace", fontSize: 10, fontWeight: 600,
      }}>
        {running ? "■ PAUSE" : "▶ RUN"}
      </button>
      <button onClick={tick} disabled={running} style={{
        background: "transparent", border: `1px solid ${C.border}`,
        color: C.textDim, padding: "5px 10px", borderRadius: 4,
        cursor: running ? "default" : "pointer",
        fontFamily: "'JetBrains Mono',monospace", fontSize: 10,
        opacity: running ? 0.3 : 1,
      }}>STEP</button>
      <button onClick={() => { setRunning(false); init(); }} style={{
        background: "transparent", border: `1px solid ${C.border}`,
        color: C.textDim, padding: "5px 10px", borderRadius: 4, cursor: "pointer",
        fontFamily: "'JetBrains Mono',monospace", fontSize: 10,
      }}>RESET</button>
      <select value={speed} onChange={e => setSpeed(Number(e.target.value))} style={selectStyle}>
        <option value={200}>Slow</option>
        <option value={80}>Med</option>
        <option value={20}>Fast</option>
      </select>
    </div>
  </div>

  {/* CONFIG ROW */}
  <div style={{ ...panel, marginBottom: 12, display: "flex", gap: 20, flexWrap: "wrap", alignItems: "center", padding: "10px 14px" }}>
    <div style={label}>
      AXIOM CONTROLS
    </div>

    <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
      <span style={{ fontSize: 10, color: C.textDim, fontFamily: "'JetBrains Mono',monospace" }}>Env Volatility</span>
      <button onClick={() => { setEnvVolatile(!envVolatile); }} style={{
        background: envVolatile ? C.accent + "25" : C.border,
        border: `1px solid ${envVolatile ? C.accent : C.border}`,
        color: envVolatile ? C.accent : C.textDim,
        padding: "2px 8px", borderRadius: 3, cursor: "pointer",
        fontFamily: "'JetBrains Mono',monospace", fontSize: 9,
      }}>{envVolatile ? "ON — Unstable" : "OFF — Stable (classical assumption)"}</button>
    </div>

    <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
      <span style={{ fontSize: 10, color: C.textDim, fontFamily: "'JetBrains Mono',monospace" }}>Base Tension</span>
      <input type="range" min={0} max={100} value={baseTension * 100}
        onChange={e => setBaseTension(e.target.value / 100)}
        style={{ width: 80, accentColor: C.accent }} />
      <span style={{ fontSize: 10, color: C.accent, fontFamily: "'JetBrains Mono',monospace" }}>{(baseTension * 100).toFixed(0)}%</span>
    </div>

    <div style={{ display: "flex", alignItems: "center", gap: 4 }}>
      <span style={{ fontSize: 10, color: C.classical, fontFamily: "'JetBrains Mono',monospace" }}>Classical Mots:</span>
      <select value={classicalMot1} onChange={e => setClassicalMot1(e.target.value)} style={selectStyle}>
        {Object.entries(MOTIVATION_TYPES).map(([k, v]) => <option key={k} value={k}>{v.label}</option>)}
      </select>
      <span style={{ fontSize: 9, color: C.textDim }}>vs</span>
      <select value={classicalMot2} onChange={e => setClassicalMot2(e.target.value)} style={selectStyle}>
        {Object.entries(MOTIVATION_TYPES).map(([k, v]) => <option key={k} value={k}>{v.label}</option>)}
      </select>
    </div>

    <div style={{ display: "flex", alignItems: "center", gap: 4 }}>
      <span style={{ fontSize: 10, color: C.nvc, fontFamily: "'JetBrains Mono',monospace" }}>NVC Mots:</span>
      <select value={nvcMot1} onChange={e => setNvcMot1(e.target.value)} style={selectStyle}>
        {Object.entries(MOTIVATION_TYPES).map(([k, v]) => <option key={k} value={k}>{v.label}</option>)}
      </select>
      <span style={{ fontSize: 9, color: C.textDim }}>vs</span>
      <select value={nvcMot2} onChange={e => setNvcMot2(e.target.value)} style={selectStyle}>
        {Object.entries(MOTIVATION_TYPES).map(([k, v]) => <option key={k} value={k}>{v.label}</option>)}
      </select>
    </div>
  </div>

  {/* ENVIRONMENT STRIP */}
  <div style={{ ...panel, marginBottom: 12, padding: "8px 14px" }}>
    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
        <div style={label}>ENVIRONMENT — Step {step}</div>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 2 }}>
          {env.activeEvents.map((e, i) => <EventBadge key={i} event={e} />)}
          {env.activeEvents.length === 0 && <span style={{ fontSize: 9, color: C.textDim, fontFamily: "'JetBrains Mono',monospace" }}>— stable —</span>}
        </div>
      </div>
      <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
        <span style={{ fontSize: 9, color: C.textDim, fontFamily: "'JetBrains Mono',monospace" }}>TENSION</span>
        <Spark data={env.tensionHistory} color={C.accent} w={120} h={20} showArea />
        <span style={{ fontSize: 12, fontWeight: 600, color: env.tension > 0.6 ? C.danger : env.tension > 0.3 ? C.accent : C.green, fontFamily: "'JetBrains Mono',monospace" }}>
          {(env.tension * 100).toFixed(0)}%
        </span>
      </div>
    </div>
  </div>

  {/* MAIN COMPARISON */}
  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>

    {/* CLASSICAL */}
    <div style={panel}>
      <div style={{ ...label, color: C.classical, marginBottom: 10 }}>● CLASSICAL GAME THEORY</div>

      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 8 }}>
        <div>
          {bigNum(cA.utility, C.classical)}
          <div style={{ fontSize: 9, color: C.textDim }}>Agent 1 · {MOTIVATION_TYPES[classicalMot1].icon} {MOTIVATION_TYPES[classicalMot1].label}</div>
        </div>
        <div style={{ textAlign: "center" }}>
          {bigNum(cTotal, C.text)}
          <div style={{ fontSize: 9, color: C.textDim }}>combined</div>
        </div>
        <div style={{ textAlign: "right" }}>
          {bigNum(cB.utility, C.classical)}
          <div style={{ fontSize: 9, color: C.textDim }}>Agent 2 · {MOTIVATION_TYPES[classicalMot2].icon} {MOTIVATION_TYPES[classicalMot2].label}</div>
        </div>
      </div>

      <Spark data={cTotalHist} color={C.classical} w={320} h={50} showArea />

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10, marginTop: 10 }}>
        <div>
          <div style={{ fontSize: 9, color: C.textDim, marginBottom: 4 }}>MOTIVATION A1</div>
          <MotivationBar weights={cA.motWeights} size="small" />
        </div>
        <div>
          <div style={{ fontSize: 9, color: C.textDim, marginBottom: 4 }}>MOTIVATION A2</div>
          <MotivationBar weights={cB.motWeights} size="small" />
        </div>
      </div>

      <div style={{ display: "flex", gap: 8, marginTop: 10 }}>
        <Radar needs={cA.needs} size={100} color={C.classical} />
        <div style={{ flex: 1 }}>
          <Gauge label="Coop Rate A1" value={cA.cooperateRate * 100} color={C.classical} small />
          <Gauge label="Coop Rate A2" value={cB.cooperateRate * 100} color={C.classical} small />
          <Gauge label="Resilience" value={(cA.resilienceScore + cB.resilienceScore) / 2} color={C.accent} small />
          <Gauge label="Inequality" value={Math.abs(cA.utility - cB.utility)} color={C.danger} small />
        </div>
        <Radar needs={cB.needs} size={100} color={C.classical} />
      </div>

      <div style={{ marginTop: 8, padding: "6px 8px", background: C.classical + "0a", borderRadius: 3, fontSize: 9, fontFamily: "'JetBrains Mono',monospace", color: C.textDim, lineHeight: 1.6 }}>
        AGENTS: {cA.neuroplasticity < 0.1 ? "Static — cannot transform" : "Minimal adaptation"}<br />
        MOTIVATION: {classicalMot1 === classicalMot2 && classicalMot1 === "self" ? "Both self-maximizing (classical default)" : "Diverse — BUT framework can't leverage it"}<br />
        ENV RESPONSE: Brittle — no creative adaptation capacity
      </div>
    </div>

    {/* NVC */}
    <div style={panel}>
      <div style={{ ...label, color: C.nvc, marginBottom: 10 }}>● NVC-SUBSTRATE DYNAMICS</div>

      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 8 }}>
        <div>
          {bigNum(nA.utility, C.nvc)}
          <div style={{ fontSize: 9, color: C.textDim }}>Agent 1 · {MOTIVATION_TYPES[nvcMot1].icon} {MOTIVATION_TYPES[nvcMot1].label}</div>
        </div>
        <div style={{ textAlign: "center" }}>
          {bigNum(nTotal, C.text)}
          <div style={{ fontSize: 9, color: C.textDim }}>combined</div>
        </div>
        <div style={{ textAlign: "right" }}>
          {bigNum(nB.utility, C.nvc)}
          <div style={{ fontSize: 9, color: C.textDim }}>Agent 2 · {MOTIVATION_TYPES[nvcMot2].icon} {MOTIVATION_TYPES[nvcMot2].label}</div>
        </div>
      </div>

      <Spark data={nTotalHist} color={C.nvc} w={320} h={50} showArea />

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10, marginTop: 10 }}>
        <div>
          <div style={{ fontSize: 9, color: C.textDim, marginBottom: 4 }}>MOTIVATION A1 (drifts)</div>
          <MotivationBar weights={nA.motWeights} size="small" />
        </div>
        <div>
          <div style={{ fontSize: 9, color: C.textDim, marginBottom: 4 }}>MOTIVATION A2 (drifts)</div>
          <MotivationBar weights={nB.motWeights} size="small" />
        </div>
      </div>

      <div style={{ display: "flex", gap: 8, marginTop: 10 }}>
        <Radar needs={nA.needs} size={100} color={C.nvc} />
        <div style={{ flex: 1 }}>
          <Gauge label="Empathy BW" value={(nA.empathyBandwidth + nB.empathyBandwidth) / 2 * 100} color={C.nvc} small />
          <Gauge label="Connection" value={(nA.connectionCapacity + nB.connectionCapacity) / 2 * 100} color={C.green} small />
          <Gauge label="Resilience" value={(nA.resilienceScore + nB.resilienceScore) / 2} color={C.accent} small />
          <Gauge label="Self-Awareness" value={(nA.selfAwareness + nB.selfAwareness) / 2 * 100} color={C.purple} small />
        </div>
        <Radar needs={nB.needs} size={100} color={C.nvc} />
      </div>

      <div style={{ marginTop: 8, padding: "6px 8px", background: C.nvc + "0a", borderRadius: 3, fontSize: 9, fontFamily: "'JetBrains Mono',monospace", color: C.textDim, lineHeight: 1.6 }}>
        AGENTS: Neuroplastic — empathy and connection grow through use<br />
        MOTIVATION: Diverse AND framework leverages diversity as creative resource<br />
        ENV RESPONSE: Adaptive — perturbation drives innovation, not collapse
      </div>
    </div>
  </div>

  {/* BOTTOM — COMPARATIVE */}
  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 12, marginTop: 12 }}>

    <div style={panel}>
      <div style={label}>WELFARE DIVERGENCE</div>
      <div style={{ display: "flex", gap: 12 }}>
        <Spark data={cTotalHist} color={C.classical} w={130} h={40} showArea />
        <Spark data={nTotalHist} color={C.nvc} w={130} h={40} showArea />
      </div>
      <div style={{ display: "flex", justifyContent: "space-between", marginTop: 4, fontSize: 9, fontFamily: "'JetBrains Mono',monospace" }}>
        <span style={{ color: C.classical }}>● Classical {cTotal.toFixed(0)}</span>
        <span style={{ color: C.accent }}>Δ {(nTotal - cTotal).toFixed(1)}</span>
        <span style={{ color: C.nvc }}>● NVC {nTotal.toFixed(0)}</span>
      </div>
    </div>

    <div style={panel}>
      <div style={label}>RESILIENCE UNDER PERTURBATION</div>
      <Spark data={cA.resilienceHistory.map((v, i) => v)} color={C.classical} w={130} h={18} />
      <Spark data={nA.resilienceHistory.map((v, i) => v)} color={C.nvc} w={130} h={18} />
      <div style={{ fontSize: 9, fontFamily: "'JetBrains Mono',monospace", color: C.textDim, marginTop: 4 }}>
        {envVolatile ? "Volatile env active — watch NVC absorb shocks" : "Stable env — toggle volatility to stress-test"}
      </div>
    </div>

    <div style={panel}>
      <div style={label}>EVENT LOG (last 5)</div>
      <div style={{ fontSize: 9, fontFamily: "'JetBrains Mono',monospace", color: C.textDim, lineHeight: 1.8 }}>
        {env.eventLog.length === 0 && "No events yet..."}
        {env.eventLog.slice(-5).reverse().map((e, i) => (
          <div key={i}>
            <span style={{ color: (e.effect.tension || 0) < 0 ? C.green : C.danger }}>
              {(e.effect.tension || 0) < 0 ? "+" : "−"}
            </span>{" "}
            <span style={{ color: C.textMid }}>{e.name}</span>{" "}
            <span style={{ color: C.textDim }}>@ step {e.step}</span>
          </div>
        ))}
      </div>
    </div>
  </div>

  {/* INSIGHT */}
  {step > 30 && (
    <div style={{ ...panel, marginTop: 12, borderColor: C.accent + "30" }}>
      <div style={{ ...label, color: C.accent }}>⚡ STRUCTURAL OBSERVATIONS</div>
      <div style={{ fontSize: 11, fontFamily: "'JetBrains Mono',monospace", color: C.textDim, lineHeight: 1.8 }}>
        {nTotal > cTotal + 10 && <div>→ NVC welfare lead of {(nTotal - cTotal).toFixed(0)} units — creative solution space exceeds payoff matrix bounds</div>}
        {nTotal < cTotal && <div>→ Classical leading short-term — but check resilience and trajectory slope</div>}
        {env.eventLog.length > 2 && <div>→ {env.eventLog.length} environmental perturbations so far — classical framework has no adaptation mechanism for these</div>}
        {nA.empathyBandwidth > 0.7 && <div>→ NVC empathy bandwidth above 0.7 — agents entering high-creative-space regime where novel solutions emerge</div>}
        {cA.cooperateRate < 0.3 && cB.cooperateRate < 0.3 && <div>→ Classical cooperation collapsed — defection spiral. "Rational" substrate producing system-irrational outcome</div>}
        {nA.motWeights.future > 0.15 && nvcMot1 !== "sacred" && nvcMot1 !== "kinship" && (
          <div>→ NVC Agent 1 motivation drifting toward future-orientation through contact with Agent 2 — the agents are teaching each other</div>
        )}
        <div style={{ marginTop: 6, color: C.textMid }}>
          Core: Classical game theory optimizes within fixed constraints. NVC-substrate transforms the constraints themselves.
          {envVolatile && " Under volatile conditions, the framework that can't adapt is the framework that breaks."}
        </div>
      </div>
    </div>
  )}
</div>
```

);
}
