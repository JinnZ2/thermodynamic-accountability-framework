import { useState, useMemo, useRef, useEffect } from “react”;

// ── DOMAIN DEFINITIONS ──
const DOMAINS = {
P: { bg: “#E91E63”, fg: “#FFF”, label: “Physiological”, desc: “Sleep, thermal, nutrition, circadian” },
C: { bg: “#FF9800”, fg: “#000”, label: “Cognitive”, desc: “Decision quality, pattern recognition, SA” },
M: { bg: “#607D8B”, fg: “#FFF”, label: “Mechanical”, desc: “Vehicle state, maintenance, system familiarity” },
E: { bg: “#4FC3F7”, fg: “#000”, label: “Environmental”, desc: “Weather, road, traffic, vibration” },
T: { bg: “#EF5350”, fg: “#FFF”, label: “Temporal”, desc: “HOS phase, cumulative fatigue, recovery debt” },
S: { bg: “#AB47BC”, fg: “#FFF”, label: “Social”, desc: “Isolation, comms frequency, support network” },
I: { bg: “#FF6D00”, fg: “#000”, label: “Institutional”, desc: “Compliance pressure, monitoring friction” },
};

const DTag = ({ d, size = 10 }) => {
const c = DOMAINS[d];
return c ? (
<span style={{
display: “inline-block”, background: c.bg, color: c.fg,
borderRadius: 3, padding: `0px ${size * 0.5}px`, fontSize: size,
fontWeight: 700, fontFamily: “monospace”, marginRight: 3,
}}>[{d}]</span>
) : null;
};

// ── INSTITUTIONAL INTERFERENCE PATTERNS ──
// These are the ways monitoring systems degrade the thing they measure
const INTERFERENCE_PATTERNS = [
{
id: “idle-shutoff”,
name: “180s Idle Shutoff”,
institutional: “Designed to reduce fuel waste and emissions”,
reality: [
{ domain: “P”, effect: “Fragments sleep cycles during mandatory rest. Cab temp oscillates 15-25°F per cycle. REM interruption cascades into next shift.” },
{ domain: “C”, effect: “Each restart requires conscious attention. 4-6 restarts/night = cumulative cognitive drain before shift starts.” },
{ domain: “M”, effect: “Thermal cycling on engine: starter wear, battery drain, oil pressure spikes on cold restart.” },
{ domain: “T”, effect: “ELD records ‘rest period’ as adequate. Actual recovery: 40-60% of nominal due to fragmentation.” },
],
cascade: “System designed to save fuel creates sleep-deprived operators who then consume more fuel through degraded driving efficiency, take longer routes due to impaired decision-making, and generate higher maintenance costs from thermal cycling damage.”,
},
{
id: “fatigue-camera”,
name: “Fatigue Camera (DMS)”,
institutional: “Monitors eye closure, head position, yawn detection”,
reality: [
{ domain: “C”, effect: “Flags mirror-scanning and instrument checks as ‘drowsiness.’ Operator learns to minimize visual scanning to avoid alerts.” },
{ domain: “P”, effect: “False alerts during normal blink patterns create cortisol spikes. Chronic false-positive stress.” },
{ domain: “S”, effect: “Operator feels surveilled, not supported. Trust degradation with institution.” },
{ domain: “I”, effect: “Alert data feeds compliance scoring. Driver with high situational awareness gets lower score than disengaged driver staring straight ahead.” },
],
cascade: “Camera optimizes for a proxy (eye openness) that inversely correlates with actual safety behavior (scanning). Operators who adapt to the camera become less safe. Operators who ignore it get flagged.”,
},
{
id: “eld-hos”,
name: “ELD / HOS Rigid Enforcement”,
institutional: “14hr on-duty window, 11hr drive limit, 30min break mandate”,
reality: [
{ domain: “T”, effect: “Clock runs during dock delays operator doesn’t control. 2hr dock wait = 2hr less driving capacity. No distinction between active work and passive waiting.” },
{ domain: “C”, effect: “Approaching HOS limit creates time pressure that degrades decision quality. Operator pushes through marginal conditions to ‘make the clock.’” },
{ domain: “P”, effect: “30min break mandate forces stops at suboptimal circadian moments. May interrupt flow state during peak alertness.” },
{ domain: “E”, effect: “Cannot extend 15 minutes to clear a weather system. Must stop in dangerous location because clock expired.” },
{ domain: “M”, effect: “Rushed pre-trip inspections when clock is tight. Maintenance behaviors are first thing sacrificed under time pressure.” },
],
cascade: “Fixed temporal box ignores all other domain states. An operator who slept 9 hours, ate well, and is at peak circadian alertness at hour 10.5 must stop. An operator who slept 4 hours fragmented by idle shutoff and is in physiological crisis at hour 6 is ‘compliant.’ The metric measures time, not capacity.”,
},
{
id: “lane-departure”,
name: “Lane Departure Warning”,
institutional: “Alerts when vehicle crosses lane markings without signal”,
reality: [
{ domain: “C”, effect: “On rural 2-lane roads, deliberate lane positioning to avoid shoulder hazards (deer, gravel, ice) triggers false alerts.” },
{ domain: “P”, effect: “Chronic false alerts create habituation. When real departure occurs, alert is ignored (boy-who-cried-wolf).” },
{ domain: “E”, effect: “Snow-covered or faded lane markings cause system to oscillate between active and inactive. Unreliable in the conditions where it’s most needed.” },
{ domain: “I”, effect: “Alert frequency feeds safety scoring. Rural routes with poor markings generate worse scores than highway routes, penalizing operators on harder assignments.” },
],
cascade: “System calibrated for interstate conditions applied to rural corridors. Generates noise that degrades the operator’s actual threat-detection capacity through habituation and attention fragmentation.”,
},
{
id: “speed-governor”,
name: “Speed Governor / Limiter”,
institutional: “Caps vehicle speed at 65-68 mph for fuel/safety”,
reality: [
{ domain: “T”, effect: “Eliminates ability to recover time on open highway segments. Every delay becomes permanent.” },
{ domain: “E”, effect: “Cannot accelerate to merge safely or clear a hazard zone. Speed differential with traffic creates its own risk.” },
{ domain: “C”, effect: “Operator loses a control variable. Reduced agency degrades engagement and situational ownership.” },
{ domain: “P”, effect: “Extended time at constant speed + constant RPM = increased vibration fatigue and monotony-induced drowsiness.” },
],
cascade: “Removes operator’s ability to modulate the one variable (speed) that trades off against multiple domains. Forces the system into a rigid state where all adaptation must happen in other, less controllable domains.”,
},
];

// ── LHRI COMPUTATION ENGINE ──
const SHIFT_PHASES = [
{ label: “Pre-Shift”, range: [0, 0], desc: “Rest period, preparation” },
{ label: “Ramp-Up”, range: [0.5, 2], desc: “Circadian activation, warming” },
{ label: “Peak”, range: [2, 6], desc: “Optimal cognitive/physical state” },
{ label: “Plateau”, range: [6, 9], desc: “Sustained but declining capacity” },
{ label: “Decline”, range: [9, 10.5], desc: “Accelerating degradation” },
{ label: “Critical”, range: [10.5, 11], desc: “Minimum safe capacity” },
];

const computeLHRI = (inputs) => {
const {
sleepHours, sleepQuality, // P
shiftHour, consecutiveDays, lastFullRest, // T
weatherSeverity, roadType, nightDriving, // E
isolationDays, lastHumanContact, // S
vehicleCondition, maintenanceCurrent, // M
compliancePressure, monitoringLevel, // I
} = inputs;

// ── PHYSIOLOGICAL [P] ──
// Sleep debt accumulates non-linearly
const sleepDebt = Math.max(0, 7.5 - sleepHours) * (1 + (1 - sleepQuality) * 0.5);
const circadianPhase = shiftHour < 2 ? 0.7 : shiftHour < 6 ? 1.0 : shiftHour < 9 ? 0.85 : shiftHour < 10.5 ? 0.65 : 0.4;
const thermalStress = inputs.cabTemp < 60 ? (60 - inputs.cabTemp) / 40 : inputs.cabTemp > 85 ? (inputs.cabTemp - 85) / 30 : 0;
const pScore = Math.max(0, Math.min(1,
1.0 - (sleepDebt * 0.12) - thermalStress * 0.15
)) * circadianPhase;

// ── COGNITIVE [C] ──
// Derived from P, T, E, and institutional interference
const fatigueLoad = (1 - pScore) * 0.4 + (shiftHour / 11) * 0.3;
const interferenceLoad = monitoringLevel * 0.08; // each monitoring system adds cognitive tax
const environmentalLoad = weatherSeverity * 0.1 + (nightDriving ? 0.1 : 0) + (roadType === “rural” ? 0.05 : 0);
const cScore = Math.max(0, Math.min(1,
1.0 - fatigueLoad - interferenceLoad - environmentalLoad
));

// ── MECHANICAL [M] ──
const mScore = Math.max(0, Math.min(1,
(vehicleCondition / 10) * 0.6 + (maintenanceCurrent ? 0.4 : 0.1)
));

// ── ENVIRONMENTAL [E] ──
const eScore = Math.max(0, Math.min(1,
1.0 - weatherSeverity * 0.25 - (nightDriving ? 0.15 : 0) - (roadType === “rural” ? 0.1 : roadType === “state-highway” ? 0.05 : 0)
));

// ── TEMPORAL [T] ──
const shiftFatigue = shiftHour < 6 ? shiftHour / 6 * 0.3 : 0.3 + (shiftHour - 6) / 5 * 0.7;
const cumulativeFatigue = Math.min(1, consecutiveDays / 7 * 0.4 + Math.max(0, 48 - lastFullRest) / 48 * 0.3);
const tScore = Math.max(0, Math.min(1,
1.0 - shiftFatigue * 0.5 - cumulativeFatigue * 0.5
));

// ── SOCIAL [S] ──
const isolationDecay = Math.min(1, isolationDays / 14);
const contactRecency = Math.min(1, lastHumanContact / 48);
const sScore = Math.max(0, Math.min(1,
1.0 - isolationDecay * 0.4 - contactRecency * 0.3
));

// ── INSTITUTIONAL [I] ──
// Higher score = less institutional interference
const iScore = Math.max(0, Math.min(1,
1.0 - compliancePressure * 0.15 - monitoringLevel * 0.1
));

// ── COMPOSITE LHRI ──
// Not a simple average — uses minimum-weighted approach
// The weakest domain drags the composite disproportionately
const scores = { P: pScore, C: cScore, M: mScore, E: eScore, T: tScore, S: sScore, I: iScore };
const values = Object.values(scores);
const minScore = Math.min(…values);
const avgScore = values.reduce((a, b) => a + b, 0) / values.length;

// LHRI = 60% weighted average + 40% minimum (bottleneck-weighted)
const lhri = avgScore * 0.6 + minScore * 0.4;

// Stress levels per domain (0-3)
const stress = {};
Object.entries(scores).forEach(([k, v]) => {
stress[k] = v > 0.7 ? 0 : v > 0.5 ? 1 : v > 0.3 ? 2 : 3;
});

// Institutional misclassification detection
const misclassifications = [];
if (pScore > 0.7 && shiftHour > 10) {
misclassifications.push({
type: “false-negative”,
message: “ELD shows operator near HOS limit, but physiological state is strong. System would force stop during peak remaining capacity.”,
domains: [“T”, “P”, “I”],
});
}
if (pScore < 0.4 && shiftHour < 6) {
misclassifications.push({
type: “false-positive”,
message: “ELD shows operator well within HOS limits, but physiological state is critically degraded. System shows ‘compliant’ for a dangerously fatigued operator.”,
domains: [“T”, “P”, “I”],
});
}
if (cScore > 0.6 && monitoringLevel >= 3) {
misclassifications.push({
type: “interference”,
message: “Cognitive capacity is good but being actively degraded by monitoring system load. Each additional alert/camera/sensor adds attention tax.”,
domains: [“C”, “I”],
});
}
if (isolationDays > 5 && compliancePressure > 2) {
misclassifications.push({
type: “compounding”,
message: “Extended isolation + high compliance pressure. Operator may be masking degradation to avoid institutional consequences.”,
domains: [“S”, “I”, “P”],
});
}

// Shift phase
const phase = SHIFT_PHASES.find(p => shiftHour >= p.range[0] && shiftHour <= p.range[1]) || SHIFT_PHASES[SHIFT_PHASES.length - 1];

// Active interference patterns
const activeInterference = INTERFERENCE_PATTERNS.filter(p => {
if (p.id === “idle-shutoff” && (inputs.cabTemp < 55 || inputs.cabTemp > 90)) return true;
if (p.id === “fatigue-camera” && monitoringLevel >= 2) return true;
if (p.id === “eld-hos” && shiftHour > 8) return true;
if (p.id === “lane-departure” && (roadType === “rural” || weatherSeverity >= 2)) return true;
if (p.id === “speed-governor” && shiftHour > 6) return true;
return false;
});

return {
scores,
stress,
lhri,
lhriLevel: lhri > 0.7 ? 0 : lhri > 0.5 ? 1 : lhri > 0.3 ? 2 : 3,
phase,
misclassifications,
activeInterference,
bottleneck: Object.entries(scores).reduce((a, b) => a[1] < b[1] ? a : b)[0],
};
};

// ── UI COMPONENTS ──
const Slider = ({ label, value, onChange, min, max, step, unit, color = “#00ff88”, marks }) => (

  <div style={{ margin: "5px 0" }}>
    <div style={{
      display: "flex", justifyContent: "space-between",
      fontSize: 10, fontFamily: "monospace", color: "#777", marginBottom: 1,
    }}>
      <span>{label}</span>
      <span style={{ color, fontWeight: 700, fontSize: 11 }}>{value}{unit}</span>
    </div>
    <input type="range" min={min} max={max} step={step} value={value}
      onChange={e => onChange(parseFloat(e.target.value))}
      style={{ width: "100%", height: 3, appearance: "none", background: "#222", borderRadius: 2, accentColor: color }}
    />
    {marks && (
      <div style={{ display: "flex", justifyContent: "space-between", fontSize: 8, color: "#444", fontFamily: "monospace" }}>
        {marks.map((m, i) => <span key={i}>{m}</span>)}
      </div>
    )}
  </div>
);

const Toggle = ({ label, value, onChange }) => (

  <div style={{
    display: "flex", alignItems: "center", justifyContent: "space-between",
    padding: "3px 0", fontSize: 10, fontFamily: "monospace", color: "#777",
  }}>
    <span>{label}</span>
    <button onClick={() => onChange(!value)} style={{
      background: value ? "#00E67633" : "#1a1a1a",
      border: `1px solid ${value ? "#00E676" : "#333"}`,
      color: value ? "#00E676" : "#555",
      borderRadius: 3, padding: "1px 8px", fontSize: 9,
      cursor: "pointer", fontFamily: "monospace",
    }}>{value ? "YES" : "NO"}</button>
  </div>
);

const SelectRow = ({ label, value, onChange, options }) => (

  <div style={{ margin: "5px 0" }}>
    <div style={{ fontSize: 10, fontFamily: "monospace", color: "#777", marginBottom: 2 }}>{label}</div>
    <div style={{ display: "flex", gap: 3 }}>
      {options.map(o => (
        <button key={o.value} onClick={() => onChange(o.value)} style={{
          flex: 1, padding: "3px 4px", fontSize: 9, fontFamily: "monospace",
          background: value === o.value ? (o.color || "#FFD740") + "33" : "#111",
          border: `1px solid ${value === o.value ? (o.color || "#FFD740") : "#333"}`,
          color: value === o.value ? (o.color || "#FFD740") : "#555",
          borderRadius: 3, cursor: "pointer", fontWeight: value === o.value ? 700 : 400,
        }}>{o.label}</button>
      ))}
    </div>
  </div>
);

// ── RESILIENCE GAUGE ──
const ResilienceGauge = ({ lhri, level, bottleneck }) => {
const colors = [”#00E676”, “#FFD740”, “#FF8F00”, “#EF5350”];
const labels = [“RESILIENT”, “CAUTION”, “DEGRADED”, “CRITICAL”];
const pct = lhri * 100;
const angle = -90 + (lhri * 180);

return (
<div style={{ textAlign: “center”, padding: “8px 0” }}>
<svg viewBox=“0 0 200 120” style={{ width: “100%”, maxWidth: 220 }}>
{/* Background arc */}
<path d="M 20 100 A 80 80 0 0 1 180 100" fill="none" stroke="#1a1a1a" strokeWidth={12} strokeLinecap="round" />
{/* Colored segments */}
<path d="M 20 100 A 80 80 0 0 1 60 34" fill="none" stroke="#EF535055" strokeWidth={12} strokeLinecap="round" />
<path d="M 60 34 A 80 80 0 0 1 100 20" fill="none" stroke="#FF8F0055" strokeWidth={12} strokeLinecap="round" />
<path d="M 100 20 A 80 80 0 0 1 140 34" fill="none" stroke="#FFD74055" strokeWidth={12} strokeLinecap="round" />
<path d="M 140 34 A 80 80 0 0 1 180 100" fill="none" stroke="#00E67655" strokeWidth={12} strokeLinecap="round" />
{/* Needle */}
<line
x1={100} y1={100}
x2={100 + Math.cos(angle * Math.PI / 180) * 65}
y2={100 + Math.sin(angle * Math.PI / 180) * 65}
stroke={colors[level]} strokeWidth={2.5} strokeLinecap=“round”
/>
<circle cx={100} cy={100} r={4} fill={colors[level]} />
{/* Value */}
<text x={100} y={90} textAnchor="middle" fill={colors[level]}
fontSize={22} fontFamily="monospace" fontWeight={800}
>{Math.round(pct)}</text>
<text x={100} y={105} textAnchor="middle" fill="#666"
fontSize={8} fontFamily="monospace"
>LHRI</text>
</svg>
<div style={{
fontSize: 12, fontWeight: 800, color: colors[level],
fontFamily: “monospace”, letterSpacing: 1,
marginTop: -4,
}}>{labels[level]}</div>
<div style={{ fontSize: 9, color: “#666”, fontFamily: “monospace”, marginTop: 2 }}>
Bottleneck: <DTag d={bottleneck} size={9} /> {DOMAINS[bottleneck]?.label}
</div>
</div>
);
};

// ── DOMAIN RADAR ──
const DomainRadar = ({ scores }) => {
const keys = Object.keys(scores);
const n = keys.length;
const cx = 100, cy = 100, r = 75;

// Animated interpolation
const displayRef = useRef({…scores});
const targetRef = useRef({…scores});
const animRef = useRef(null);
const [displayScores, setDisplayScores] = useState({…scores});

useEffect(() => {
targetRef.current = {…scores};
const animate = () => {
let needsUpdate = false;
const next = {};
keys.forEach(k => {
const current = displayRef.current[k] || 0;
const target = targetRef.current[k] || 0;
const diff = target - current;
if (Math.abs(diff) > 0.002) {
next[k] = current + diff * 0.12;
needsUpdate = true;
} else {
next[k] = target;
}
});
displayRef.current = next;
setDisplayScores({…next});
if (needsUpdate) {
animRef.current = requestAnimationFrame(animate);
}
};
animRef.current = requestAnimationFrame(animate);
return () => { if (animRef.current) cancelAnimationFrame(animRef.current); };
}, [scores]);

const getPoint = (i, val) => {
const angle = (Math.PI * 2 * i) / n - Math.PI / 2;
return {
x: cx + Math.cos(angle) * r * val,
y: cy + Math.sin(angle) * r * val,
};
};

const polygonPoints = keys.map((k, i) => {
const p = getPoint(i, displayScores[k] || 0);
return `${p.x},${p.y}`;
}).join(” “);

return (
<svg viewBox=“0 0 200 200” style={{ width: “100%”, maxWidth: 200 }}>
{[0.25, 0.5, 0.75, 1.0].map(v => (
<polygon key={v}
points={keys.map((_, i) => {
const p = getPoint(i, v);
return `${p.x},${p.y}`;
}).join(” “)}
fill=“none” stroke=”#1a1a1a” strokeWidth={0.5}
/>
))}
{keys.map((k, i) => {
const p = getPoint(i, 1);
const lp = getPoint(i, 1.18);
const dc = DOMAINS[k];
return (
<g key={k}>
<line x1={cx} y1={cy} x2={p.x} y2={p.y} stroke="#222" strokeWidth={0.5} />
<text x={lp.x} y={lp.y + 3} textAnchor=“middle”
fill={dc?.bg || “#666”} fontSize={8} fontFamily=“monospace” fontWeight={700}
>[{k}]</text>
</g>
);
})}
<polygon points={polygonPoints}
fill="#00E67615" stroke="#00E676" strokeWidth={1.5}
/>
{keys.map((k, i) => {
const dv = displayScores[k] || 0;
const p = getPoint(i, dv);
const color = dv > 0.7 ? “#00E676” : dv > 0.5 ? “#FFD740” : dv > 0.3 ? “#FF8F00” : “#EF5350”;
return (
<circle key={k} cx={p.x} cy={p.y} r={3} fill={color} stroke="#000" strokeWidth={0.5} />
);
})}
</svg>
);
};

// ── INTERFERENCE DETAIL ──
const InterferenceCard = ({ pattern }) => (

  <div style={{
    background: "#0f0808", border: "1px solid #FF6D00",
    borderLeft: "3px solid #FF6D00", borderRadius: 4,
    padding: "8px 10px", margin: "6px 0",
  }}>
    <div style={{
      fontSize: 11, fontWeight: 700, color: "#FF6D00",
      fontFamily: "monospace", marginBottom: 4,
    }}>⚡ {pattern.name}</div>
    <div style={{
      fontSize: 9, color: "#666", fontFamily: "monospace",
      marginBottom: 6, fontStyle: "italic",
    }}>Institutional claim: "{pattern.institutional}"</div>
    {pattern.reality.map((r, i) => (
      <div key={i} style={{
        fontSize: 10, color: "#bbb", fontFamily: "monospace",
        padding: "2px 0", lineHeight: 1.5,
      }}>
        <DTag d={r.domain} size={9} /> {r.effect}
      </div>
    ))}
    <div style={{
      marginTop: 6, padding: "4px 8px", background: "#1a0a0a",
      borderRadius: 3, fontSize: 10, color: "#EF5350",
      fontFamily: "monospace", lineHeight: 1.5,
    }}>
      CASCADE: {pattern.cascade}
    </div>
  </div>
);

// ── MISCLASSIFICATION ALERT ──
const MisclassAlert = ({ mc }) => {
const colors = {
“false-negative”: “#FFD740”,
“false-positive”: “#EF5350”,
“interference”: “#FF6D00”,
“compounding”: “#AB47BC”,
};
const icons = {
“false-negative”: “⚠”,
“false-positive”: “🔴”,
“interference”: “⚡”,
“compounding”: “🔗”,
};
const c = colors[mc.type] || “#888”;
return (
<div style={{
background: c + “11”, border: `1px solid ${c}`,
borderRadius: 4, padding: “6px 10px”, margin: “4px 0”,
}}>
<div style={{
fontSize: 10, fontWeight: 700, color: c,
fontFamily: “monospace”, display: “flex”, alignItems: “center”, gap: 6,
}}>
{icons[mc.type]} MISCLASSIFICATION: {mc.type.toUpperCase().replace(”-”, “ “)}
<span style={{ marginLeft: “auto”, display: “flex”, gap: 2 }}>
{mc.domains.map(d => <DTag key={d} d={d} size={9} />)}
</span>
</div>
<div style={{
fontSize: 10, color: “#aaa”, fontFamily: “monospace”,
marginTop: 4, lineHeight: 1.5,
}}>{mc.message}</div>
</div>
);
};

// ── COMPARISON VIEW ──
const ComparisonView = ({ state }) => {
// What conventional systems “see” vs LHRI
const hosPosition = state.phase.label;
const eldStatus = state.scores.T < 0.3 ? “VIOLATION RISK” : “COMPLIANT”;
const cameraStatus = state.scores.C > 0.5 ? “NO ALERT” : “POSSIBLE ALERT”;
const lhriStatus = state.lhriLevel === 0 ? “RESILIENT” : state.lhriLevel === 1 ? “CAUTION” : state.lhriLevel === 2 ? “DEGRADED” : “CRITICAL”;

const lhriColors = [”#00E676”, “#FFD740”, “#FF8F00”, “#EF5350”];

return (
<div style={{ fontFamily: “monospace” }}>
<div style={{
display: “grid”, gridTemplateColumns: “1fr 1fr”, gap: 8,
}}>
{/* CONVENTIONAL */}
<div style={{
background: “#0a0a14”, border: “1px solid #333”,
borderRadius: 4, padding: “10px”,
}}>
<div style={{ fontSize: 10, color: “#666”, textTransform: “uppercase”, letterSpacing: 1, marginBottom: 8 }}>
CONVENTIONAL VIEW
</div>
<div style={{ fontSize: 10, color: “#888”, marginBottom: 4 }}>
ELD: <span style={{ color: eldStatus === “COMPLIANT” ? “#00E676” : “#EF5350”, fontWeight: 700 }}>{eldStatus}</span>
</div>
<div style={{ fontSize: 10, color: “#888”, marginBottom: 4 }}>
DMS Camera: <span style={{ color: cameraStatus === “NO ALERT” ? “#00E676” : “#FFD740”, fontWeight: 700 }}>{cameraStatus}</span>
</div>
<div style={{ fontSize: 10, color: “#888”, marginBottom: 4 }}>
Lane Dept: <span style={{ color: “#00E676”, fontWeight: 700 }}>NO ALERT</span>
</div>
<div style={{ fontSize: 10, color: “#888”, marginBottom: 4 }}>
Speed: <span style={{ color: “#00E676”, fontWeight: 700 }}>COMPLIANT</span>
</div>
<div style={{
marginTop: 8, padding: “4px 8px”,
background: “#00E67611”, border: “1px solid #00E67644”,
borderRadius: 3, fontSize: 11, color: “#00E676”,
fontWeight: 700, textAlign: “center”,
}}>SYSTEM SAYS: OK ✓</div>
</div>

```
    {/* LHRI */}
    <div style={{
      background: "#0a0a14", border: `1px solid ${lhriColors[state.lhriLevel]}44`,
      borderRadius: 4, padding: "10px",
    }}>
      <div style={{ fontSize: 10, color: "#666", textTransform: "uppercase", letterSpacing: 1, marginBottom: 8 }}>
        LHRI VIEW
      </div>
      {Object.entries(state.scores).map(([k, v]) => {
        const color = v > 0.7 ? "#00E676" : v > 0.5 ? "#FFD740" : v > 0.3 ? "#FF8F00" : "#EF5350";
        return (
          <div key={k} style={{ display: "flex", alignItems: "center", gap: 4, marginBottom: 3 }}>
            <DTag d={k} size={8} />
            <div style={{ flex: 1, height: 4, background: "#1a1a1a", borderRadius: 2 }}>
              <div style={{ width: `${v * 100}%`, height: "100%", background: color, borderRadius: 2, transition: "width 0.3s" }} />
            </div>
            <span style={{ fontSize: 8, color, minWidth: 22, textAlign: "right" }}>{Math.round(v * 100)}</span>
          </div>
        );
      })}
      <div style={{
        marginTop: 8, padding: "4px 8px",
        background: lhriColors[state.lhriLevel] + "11",
        border: `1px solid ${lhriColors[state.lhriLevel]}44`,
        borderRadius: 3, fontSize: 11, color: lhriColors[state.lhriLevel],
        fontWeight: 700, textAlign: "center",
      }}>LHRI: {lhriStatus} ({Math.round(state.lhri * 100)})</div>
    </div>
  </div>

  {state.misclassifications.length > 0 && (
    <div style={{ marginTop: 8 }}>
      <div style={{ fontSize: 9, color: "#666", textTransform: "uppercase", letterSpacing: 1, marginBottom: 4 }}>
        DETECTED MISCLASSIFICATIONS
      </div>
      {state.misclassifications.map((mc, i) => (
        <MisclassAlert key={i} mc={mc} />
      ))}
    </div>
  )}
</div>
```

);
};

// ── MAIN ──
export default function LHRIDashboard() {
// Physiological
const [sleepHours, setSleepHours] = useState(7);
const [sleepQuality, setSleepQuality] = useState(0.7);
const [cabTemp, setCabTemp] = useState(68);

// Temporal
const [shiftHour, setShiftHour] = useState(4);
const [consecutiveDays, setConsecutiveDays] = useState(3);
const [lastFullRest, setLastFullRest] = useState(36);

// Environmental
const [weatherSeverity, setWeatherSeverity] = useState(0);
const [roadType, setRoadType] = useState(“interstate”);
const [nightDriving, setNightDriving] = useState(false);

// Social
const [isolationDays, setIsolationDays] = useState(2);
const [lastHumanContact, setLastHumanContact] = useState(8);

// Mechanical
const [vehicleCondition, setVehicleCondition] = useState(8);
const [maintenanceCurrent, setMaintenanceCurrent] = useState(true);

// Institutional
const [compliancePressure, setCompliancePressure] = useState(2);
const [monitoringLevel, setMonitoringLevel] = useState(3);

const state = useMemo(() => computeLHRI({
sleepHours, sleepQuality, cabTemp,
shiftHour, consecutiveDays, lastFullRest,
weatherSeverity, roadType, nightDriving,
isolationDays, lastHumanContact,
vehicleCondition, maintenanceCurrent,
compliancePressure, monitoringLevel,
}), [sleepHours, sleepQuality, cabTemp, shiftHour, consecutiveDays, lastFullRest,
weatherSeverity, roadType, nightDriving, isolationDays, lastHumanContact,
vehicleCondition, maintenanceCurrent, compliancePressure, monitoringLevel]);

const [activeTab, setActiveTab] = useState(“comparison”);

return (
<div style={{
display: “flex”, flexDirection: “column”, height: “100vh”,
background: “#050508”, color: “#ccc”, fontFamily: “monospace”,
overflow: “hidden”,
}}>
{/* HEADER */}
<div style={{
display: “flex”, alignItems: “center”, gap: 12,
padding: “8px 16px”, borderBottom: “1px solid #1a1a1a”,
background: “#0a0a10”,
}}>
<span style={{ fontSize: 14, fontWeight: 800, color: “#E91E63”, letterSpacing: 1 }}>
LHRI
</span>
<span style={{ fontSize: 10, color: “#555” }}>
Longitudinal Human Resilience Index
</span>
<div style={{
marginLeft: “auto”, fontSize: 10, color: “#666”,
}}>
Shift Phase: <span style={{ color: “#FFD740”, fontWeight: 700 }}>{state.phase.label}</span>
<span style={{ color: “#444”, marginLeft: 6 }}>({state.phase.desc})</span>
</div>
</div>

```
  <div style={{ display: "flex", flex: 1, overflow: "hidden" }}>
    {/* LEFT: INPUTS */}
    <div style={{
      width: 220, minWidth: 220, background: "#0a0a10",
      borderRight: "1px solid #1a1a1a", padding: "8px 10px",
      overflowY: "auto", fontSize: 10,
    }}>
      <div style={{ fontSize: 9, color: "#E91E63", textTransform: "uppercase", letterSpacing: 1.5, marginBottom: 6 }}>
        [P] PHYSIOLOGICAL
      </div>
      <Slider label="Sleep (last night)" value={sleepHours} onChange={setSleepHours}
        min={0} max={10} step={0.5} unit="hr" color="#E91E63" marks={["0", "5", "10"]} />
      <Slider label="Sleep Quality" value={sleepQuality} onChange={setSleepQuality}
        min={0} max={1} step={0.1} unit="" color="#E91E63" marks={["poor", "", "good"]} />
      <Slider label="Cab Temp" value={cabTemp} onChange={setCabTemp}
        min={20} max={110} step={1} unit="°F" color="#E91E63" marks={["20", "65", "110"]} />

      <div style={{ fontSize: 9, color: "#EF5350", textTransform: "uppercase", letterSpacing: 1.5, marginTop: 10, marginBottom: 6 }}>
        [T] TEMPORAL
      </div>
      <Slider label="Current Shift Hour" value={shiftHour} onChange={setShiftHour}
        min={0} max={11} step={0.5} unit="hr" color="#EF5350" marks={["0", "5.5", "11"]} />
      <Slider label="Consecutive Days" value={consecutiveDays} onChange={setConsecutiveDays}
        min={1} max={7} step={1} unit="d" color="#EF5350" marks={["1", "4", "7"]} />
      <Slider label="Hours Since Full Rest" value={lastFullRest} onChange={setLastFullRest}
        min={8} max={72} step={2} unit="hr" color="#EF5350" marks={["8", "40", "72"]} />

      <div style={{ fontSize: 9, color: "#4FC3F7", textTransform: "uppercase", letterSpacing: 1.5, marginTop: 10, marginBottom: 6 }}>
        [E] ENVIRONMENTAL
      </div>
      <SelectRow label="Weather" value={weatherSeverity} onChange={setWeatherSeverity}
        options={[
          { value: 0, label: "Clear", color: "#00E676" },
          { value: 1, label: "Adv", color: "#FFD740" },
          { value: 2, label: "Warn", color: "#FF8F00" },
          { value: 3, label: "Severe", color: "#EF5350" },
        ]} />
      <SelectRow label="Road Type" value={roadType} onChange={setRoadType}
        options={[
          { value: "interstate", label: "Interstate" },
          { value: "us-highway", label: "US Hwy" },
          { value: "state-highway", label: "State" },
          { value: "rural", label: "Rural" },
        ]} />
      <Toggle label="Night Driving" value={nightDriving} onChange={setNightDriving} />

      <div style={{ fontSize: 9, color: "#AB47BC", textTransform: "uppercase", letterSpacing: 1.5, marginTop: 10, marginBottom: 6 }}>
        [S] SOCIAL
      </div>
      <Slider label="Days Isolated" value={isolationDays} onChange={setIsolationDays}
        min={0} max={14} step={1} unit="d" color="#AB47BC" marks={["0", "7", "14"]} />
      <Slider label="Last Human Contact" value={lastHumanContact} onChange={setLastHumanContact}
        min={0} max={48} step={2} unit="hr" color="#AB47BC" marks={["0", "24", "48"]} />

      <div style={{ fontSize: 9, color: "#607D8B", textTransform: "uppercase", letterSpacing: 1.5, marginTop: 10, marginBottom: 6 }}>
        [M] MECHANICAL
      </div>
      <Slider label="Vehicle Condition" value={vehicleCondition} onChange={setVehicleCondition}
        min={1} max={10} step={1} unit="/10" color="#607D8B" marks={["1", "5", "10"]} />
      <Toggle label="Maintenance Current" value={maintenanceCurrent} onChange={setMaintenanceCurrent} />

      <div style={{ fontSize: 9, color: "#FF6D00", textTransform: "uppercase", letterSpacing: 1.5, marginTop: 10, marginBottom: 6 }}>
        [I] INSTITUTIONAL
      </div>
      <Slider label="Compliance Pressure" value={compliancePressure} onChange={setCompliancePressure}
        min={0} max={5} step={1} unit="/5" color="#FF6D00" marks={["low", "", "high"]} />
      <Slider label="Monitoring Systems Active" value={monitoringLevel} onChange={setMonitoringLevel}
        min={0} max={5} step={1} unit="" color="#FF6D00" marks={["0", "3", "5"]} />
    </div>

    {/* CENTER */}
    <div style={{ flex: 1, display: "flex", flexDirection: "column", overflow: "hidden" }}>
      {/* GAUGE + RADAR ROW */}
      <div style={{
        display: "flex", gap: 8, padding: "8px 16px",
        borderBottom: "1px solid #1a1a1a",
        alignItems: "center", justifyContent: "center",
      }}>
        <div style={{ flex: 1, maxWidth: 240 }}>
          <ResilienceGauge lhri={state.lhri} level={state.lhriLevel} bottleneck={state.bottleneck} />
        </div>
        <div style={{ flex: 1, maxWidth: 200 }}>
          <DomainRadar scores={state.scores} />
        </div>
      </div>

      {/* TABS */}
      <div style={{
        display: "flex", gap: 0, borderBottom: "1px solid #1a1a1a", background: "#0a0a0a",
      }}>
        {[
          ["comparison", "Conventional vs LHRI"],
          ["interference", "Interference Patterns"],
          ["domains", "Domain Detail"],
        ].map(([id, label]) => (
          <button key={id} onClick={() => setActiveTab(id)} style={{
            flex: 1, padding: "7px", fontSize: 10, fontFamily: "monospace",
            background: activeTab === id ? "#111" : "transparent",
            border: "none",
            borderBottom: activeTab === id ? "2px solid #E91E63" : "2px solid transparent",
            color: activeTab === id ? "#E91E63" : "#555",
            cursor: "pointer", fontWeight: activeTab === id ? 700 : 400,
          }}>
            {label}
            {id === "interference" && state.activeInterference.length > 0 && (
              <span style={{
                marginLeft: 4, background: "#FF6D00", color: "#000",
                borderRadius: "50%", padding: "0 4px", fontSize: 8, fontWeight: 700,
              }}>{state.activeInterference.length}</span>
            )}
            {id === "comparison" && state.misclassifications.length > 0 && (
              <span style={{
                marginLeft: 4, background: "#EF5350", color: "#FFF",
                borderRadius: "50%", padding: "0 4px", fontSize: 8, fontWeight: 700,
              }}>{state.misclassifications.length}</span>
            )}
          </button>
        ))}
      </div>

      {/* TAB CONTENT */}
      <div style={{ flex: 1, overflowY: "auto", padding: "12px 16px" }}>
        {activeTab === "comparison" && <ComparisonView state={state} />}

        {activeTab === "interference" && (
          <div>
            <div style={{ fontSize: 9, color: "#666", textTransform: "uppercase", letterSpacing: 1.5, marginBottom: 8 }}>
              ACTIVE INTERFERENCE PATTERNS ({state.activeInterference.length})
            </div>
            {state.activeInterference.length === 0 ? (
              <div style={{ fontSize: 11, color: "#444", textAlign: "center", padding: "20px 0" }}>
                No interference patterns active at current state.
              </div>
            ) : (
              state.activeInterference.map(p => <InterferenceCard key={p.id} pattern={p} />)
            )}
            <div style={{
              marginTop: 12, padding: "8px 10px", background: "#0a0a14",
              border: "1px solid #222", borderRadius: 4,
              fontSize: 9, color: "#555", fontFamily: "monospace", lineHeight: 1.6,
            }}>
              Interference patterns activate when current conditions match the scenario
              where institutional monitoring systems actively degrade operator capacity.
              Each pattern shows the institutional claim, the actual multi-domain effect,
              and the cascade — how the "solution" becomes the problem.
            </div>
          </div>
        )}

        {activeTab === "domains" && (
          <div>
            {Object.entries(state.scores).map(([k, v]) => {
              const dc = DOMAINS[k];
              const color = v > 0.7 ? "#00E676" : v > 0.5 ? "#FFD740" : v > 0.3 ? "#FF8F00" : "#EF5350";
              const labels = ["NOMINAL", "CAUTION", "WARNING", "CRITICAL"];
              const level = v > 0.7 ? 0 : v > 0.5 ? 1 : v > 0.3 ? 2 : 3;
              return (
                <div key={k} style={{
                  padding: "8px 10px", marginBottom: 6,
                  background: "#0a0a10", border: `1px solid ${color}22`,
                  borderLeft: `3px solid ${dc?.bg || "#666"}`,
                  borderRadius: 4,
                }}>
                  <div style={{
                    display: "flex", alignItems: "center", gap: 8,
                    marginBottom: 4,
                  }}>
                    <DTag d={k} />
                    <span style={{ fontSize: 11, color: "#ccc", fontWeight: 700, flex: 1 }}>{dc?.label}</span>
                    <span style={{ fontSize: 10, color, fontWeight: 700 }}>
                      {Math.round(v * 100)} — {labels[level]}
                    </span>
                  </div>
                  <div style={{
                    height: 6, background: "#1a1a1a", borderRadius: 3, overflow: "hidden",
                  }}>
                    <div style={{
                      width: `${v * 100}%`, height: "100%",
                      background: `linear-gradient(90deg, ${color}88, ${color})`,
                      borderRadius: 3, transition: "width 0.3s",
                    }} />
                  </div>
                  <div style={{ fontSize: 9, color: "#555", marginTop: 3 }}>{dc?.desc}</div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  </div>
</div>
```

);
}
