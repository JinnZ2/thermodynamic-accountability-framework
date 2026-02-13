import { useState } from “react”;

const interfaces = [
{
id: “om”,
label: “Operator ⟷ Machine”,
icon: “👤🔗🚛”,
color: “#f59e0b”,
colorB: “#3b82f6”,
subtitle: “Proprioceptive Handshake”,
principle: “The body must know the machine’s state to extend into it. The machine must be in a state worth extending into.”,
nature: “Fungus ⟷ Plant: The fungal network can only mediate nutrients if it has healthy root tissue to integrate with. Diseased roots = broken interface.”,
channels: [
{ name: “Vibration spectrum”, dir: “M → O”, desc: “Road surface, tire state, drivetrain health, cargo stability — transmitted through seat, floor, pedals” },
{ name: “Acoustic channel”, dir: “M → O”, desc: “Engine breathing, wind loading, brake condition, bearing wear — transmitted as continuous sound field” },
{ name: “Steering resistance”, dir: “M ⟷ O”, desc: “Bidirectional — machine transmits road state, operator transmits control input. The nerve ending.” },
{ name: “Throttle/brake feel”, dir: “O → M”, desc: “Operator’s motor output tuned to machine response curves built over time” }
],
care: [
{
title: “Daily Coupling Calibration (Pre-Trip)”,
what: “Walk-around, listen at idle, feel the load, check tire pressure by sight and touch, verify lights and brake function”,
why: “Establishes today’s baseline. Body schema needs current state to interpret real-time signals. Without baseline, operator is coupled to yesterday’s truck.”,
degradation: “Skipped pre-trip → proprioceptive mismatch → delayed anomaly detection → increased risk at every state change”,
metric: “Time from state change to operator response. Calibrated operator: milliseconds. Uncalibrated: seconds or never.”
},
{
title: “Mechanical Integrity Maintenance”,
what: “Tire condition, brake adjustment, suspension health, steering play, engine maintenance, fluid levels”,
why: “Degraded mechanical systems transmit corrupted signals. Worn steering masks road feedback. Bad shocks distort vibration spectrum. The machine becomes a liar.”,
degradation: “Deferred maintenance → signal corruption → body schema builds false model → operator confident in wrong information”,
metric: “Signal-to-noise ratio at each channel. Maintained truck: clean signal. Neglected truck: noise floor rises until signal is unreadable.”
},
{
title: “Operator Biological Maintenance”,
what: “Sleep, nutrition, hydration, physical health, fatigue management, stress regulation”,
why: “Cerebellar prediction, proprioceptive sensitivity, and sensorimotor integration all degrade with fatigue. The receiver impairs before the operator consciously notices.”,
degradation: “Fatigued operator → slower integration, narrower sensory bandwidth, delayed response, false confidence from pattern-matching on memory instead of current state”,
metric: “Proprioceptive sensitivity threshold. Rested operator detects 2% load shift. Fatigued operator misses 8%.”
},
{
title: “Cab Environment Care”,
what: “Seat condition, mirror alignment, windshield clarity, climate control, noise management, ergonomic setup”,
why: “The cab is the coupling chamber. Every element in it either transmits or obstructs the channels between body and machine. A bad seat is a damaged nerve.”,
degradation: “Worn seat cushion → vibration spectrum distorted → road surface information degraded → operator compensates consciously (slow) instead of somatically (fast)”,
metric: “Channel fidelity across all sensory pathways. Clean cab = clean transmission. Degraded cab = lossy interface.”
}
]
},
{
id: “oa”,
label: “Operator ⟷ AI”,
icon: “👤🔗🤖”,
color: “#f59e0b”,
colorB: “#8b5cf6”,
subtitle: “Trust Calibration Loop”,
principle: “AI must deliver information without pulling the operator out of somatic processing. Operator must flag what AI cannot see. Neither overrides the other.”,
nature: “Fungus ⟷ Virus: The virus must operate within the fungal architecture without disrupting it. The fungus provides the cellular environment the virus needs. Disruption = thermal tolerance lost.”,
channels: [
{ name: “Contextual pre-loading”, dir: “AI → O”, desc: “Corridor conditions, weather forecasts, known hazard patterns delivered BEFORE the body encounters them” },
{ name: “Anomaly confirmation”, dir: “AI → O”, desc: “AI detects statistical anomaly in telemetry, flags it — operator’s body confirms or rejects based on somatic sensing” },
{ name: “Somatic anomaly report”, dir: “O → AI”, desc: “Operator feels something wrong that doesn’t appear in data — creates learning signal for AI” },
{ name: “Override / consent”, dir: “O ⟷ AI”, desc: “Bidirectional authority negotiation — who has primacy depends on which channel carries better information” }
],
care: [
{
title: “Interface Design Discipline”,
what: “AI outputs delivered through ambient, non-intrusive channels. Haptic, tonal, spatial — not screens, not text, not alarms that hijack attention”,
why: “The operator’s primary contribution runs below conscious access. Any interface that forces conscious attention to process AI output is actively damaging the organism’s strongest sensing channel.”,
degradation: “Screen-based alerts → operator shifts from somatic to visual-cognitive processing → proprioceptive integration interrupted → sensing gap during the interruption → exactly when conditions may be changing”,
metric: “Seconds of proprioceptive interruption per AI interaction. Target: zero. Current industry standard: 3-15 seconds per alert.”
},
{
title: “Trust Calibration Maintenance”,
what: “Operator must know AI’s accuracy history, failure modes, blind spots. AI must know operator’s corridor expertise, sensing strengths, fatigue state.”,
why: “Miscalibrated trust destroys the coupling in both directions. Over-trust → operator defers to AI when body has better data. Under-trust → operator ignores AI when inference has better data.”,
degradation: “Single AI false positive that contradicts body knowledge → trust collapses → operator ignores all AI input → computational partner effectively removed from organism”,
metric: “Trust calibration accuracy: does operator defer/override in correct proportion to actual information quality at each channel?”
},
{
title: “Feedback Loop Integrity”,
what: “When operator detects anomaly AI missed, that signal must reach the learning system. When AI detects pattern operator can’t sense, confirmation/rejection must feed back.”,
why: “The upward spiral depends on each partner’s output becoming the other’s input. Break the loop and the partners stop co-adapting. The organism stops learning.”,
degradation: “No feedback mechanism → AI never learns from somatic detection → operator never receives refined predictions → coupling stagnates → adaptation stops while environment keeps changing”,
metric: “Loop closure rate: what percentage of anomaly detections (both directions) complete the feedback cycle?”
},
{
title: “Authority Protocol”,
what: “Clear, physics-based rules for who has primacy when partners disagree. Not hierarchy — information quality assessment.”,
why: “In real-time operation, conflicts will arise. If authority defaults to AI because ‘computer is objective,’ body knowledge gets overridden. If authority always defaults to operator, inference value is lost.”,
degradation: “No authority protocol → conflict resolution defaults to institutional power dynamics → usually AI wins → proprioceptive channel systematically suppressed → organism loses its deepest sensing”,
metric: “Conflict resolution accuracy: when partners disagreed, which one had the better information? Track over time. Let physics arbitrate.”
}
]
},
{
id: “ma”,
label: “Machine ⟷ AI”,
icon: “🚛🔗🤖”,
color: “#3b82f6”,
colorB: “#8b5cf6”,
subtitle: “Telemetry Integrity Channel”,
principle: “AI can only infer from what the machine reports. Corrupted data produces confident wrong answers that the operator must then detect and compensate for.”,
nature: “Plant ⟷ Virus: The viral code can only execute within healthy cellular machinery. If the plant’s systems are damaged, even correct genetic information produces malformed proteins.”,
channels: [
{ name: “Sensor telemetry”, dir: “M → AI”, desc: “Temperature, pressure, speed, acceleration, GPS, load sensors, fuel consumption, emissions” },
{ name: “System state data”, dir: “M → AI”, desc: “Brake wear indicators, tire pressure monitoring, engine diagnostics, fault codes” },
{ name: “Predictive adjustments”, dir: “AI → M”, desc: “Where permitted — cruise control optimization, route efficiency, predictive maintenance scheduling” },
{ name: “Environmental data bridge”, dir: “External → AI → M context”, desc: “Weather, traffic, road condition databases integrated with machine state” }
],
care: [
{
title: “Sensor Calibration and Maintenance”,
what: “Regular verification of all sensors against known references. Replacement of degraded sensors. Redundancy for critical channels.”,
why: “AI’s inference quality is bounded by input quality. A tire pressure sensor drifting 5% doesn’t look like an error — it looks like gradually changing conditions. AI builds models on the drift. Conclusions are confident and wrong.”,
degradation: “Uncalibrated sensors → systematic bias in AI models → AI makes recommendations based on false state → operator’s body detects mismatch → trust degrades → coupling damaged”,
metric: “Sensor accuracy verification frequency vs. drift rate. Every sensor should be verified at intervals shorter than its expected drift cycle.”
},
{
title: “Data Integrity Protocols”,
what: “Error checking, transmission verification, gap detection, timestamp accuracy, handling of communication dead zones”,
why: “In remote corridors with limited connectivity, data arrives late, incomplete, or not at all. AI must know when it doesn’t know — when its model is running on stale or missing data.”,
degradation: “Data gaps treated as continued-state → AI assumes conditions unchanged → conditions change in the gap → AI provides false confidence during exactly the period of highest uncertainty”,
metric: “Data freshness index: how old is the most recent verified reading on each critical channel? AI confidence should scale with data freshness, not remain constant.”
},
{
title: “Machine-AI Boundary Clarity”,
what: “Explicit definition of what AI can and cannot command. Hard limits on autonomous action. Operator consent requirements for system changes.”,
why: “If AI can adjust machine parameters without operator awareness, it introduces state changes the body didn’t initiate and may not detect. The proprioceptive model breaks because the machine is doing something the body didn’t ask for.”,
degradation: “AI adjusts cruise control for efficiency → operator feels unexpected deceleration → body interprets as mechanical anomaly → stress response activates → trust damaged → coupling injured at both interfaces simultaneously”,
metric: “Operator state-awareness coverage: for every AI-initiated machine change, did the operator know before, during, or after? ‘After’ is a coupling failure.”
},
{
title: “Graceful Degradation Design”,
what: “When sensors fail, when connectivity drops, when AI loses confidence — the system must degrade toward the operator-machine coupling, not away from it.”,
why: “The operator-machine bond is the oldest and deepest coupling. It predates the AI. When the computational partner falters, the system must fall back to the two-partner symbiosis that can still function, not demand that the operator compensate for AI failure while also managing the machine.”,
degradation: “AI failure triggers alarms and override attempts → operator attention hijacked by managing the failing AI → proprioceptive coupling to machine severed during crisis → all three partners degraded simultaneously”,
metric: “Failure mode assessment: when AI degrades, does operator workload decrease (graceful) or increase (cascading)? If increase → redesign.”
}
]
}
];

const orgHealth = [
{
title: “Coupling Health Assessment”,
items: [
“Are all three interfaces actively maintained on schedule?”,
“Is information flowing bidirectionally at each interface?”,
“Is each partner doing their best through their own architecture?”,
“Does care at one interface propagate benefit to the others?”,
“Is neglect at any interface propagating damage to the others?”
]
},
{
title: “Organism Stress Indicators”,
items: [
“Operator compensating for AI failures (cascading load)”,
“AI overriding operator sensing (channel suppression)”,
“Machine degradation undetected by either adaptive partner”,
“Trust calibration drifting without correction”,
“Environmental change rate exceeding adaptation bandwidth”
]
},
{
title: “Coupling Strengthening Signals”,
items: [
“Operator detects anomaly → AI learns → future prediction improves”,
“AI provides context → operator’s body prepares → smoother response”,
“Machine maintenance improves → signal clarity increases → both partners sense better”,
“Feedback loops closing faster over time”,
“System handles novel conditions that no single partner predicted”
]
}
];

export default function CouplingProtocols() {
const [activeInterface, setActiveInterface] = useState(0);
const [expandedCare, setExpandedCare] = useState(null);
const [showOrgHealth, setShowOrgHealth] = useState(false);

const iface = interfaces[activeInterface];

return (
<div style={{ background: “#0a0a0f”, color: “#e2e8f0”, minHeight: “100vh”, fontFamily: “‘Inter’, system-ui, sans-serif”, padding: “16px”, maxWidth: 720, margin: “0 auto” }}>
<div style={{ textAlign: “center”, marginBottom: 16 }}>
<h1 style={{ fontSize: 20, fontWeight: 700, color: “#f1f5f9”, margin: “0 0 4px 0” }}>Tripartite Coupling Protocols</h1>
<p style={{ fontSize: 12, color: “#94a3b8”, margin: 0 }}>Care at every interface protects every partner. Neglect at any interface propagates through all.</p>
</div>

```
  {/* Interface selector */}
  <div style={{ display: "flex", gap: 6, marginBottom: 16, justifyContent: "center" }}>
    {interfaces.map((f, i) => (
      <button key={f.id} onClick={() => { setActiveInterface(i); setExpandedCare(null); }} style={{
        padding: "10px 14px", borderRadius: 10, border: "2px solid",
        borderColor: activeInterface === i ? f.color : "#1e293b",
        background: activeInterface === i ? f.color + "15" : "#0f172a",
        color: activeInterface === i ? "#f1f5f9" : "#64748b",
        cursor: "pointer", fontSize: 12, fontWeight: 600, transition: "all 0.2s", flex: 1, textAlign: "center"
      }}>
        <div style={{ fontSize: 18, marginBottom: 2 }}>{f.icon}</div>
        {f.label.split(" ⟷ ").join("\n⟷\n").split("\n").map((l, j) => <div key={j}>{l}</div>)}
      </button>
    ))}
  </div>

  {/* Interface header */}
  <div style={{ background: "#1e293b", borderRadius: 12, padding: 16, marginBottom: 12, borderLeft: `4px solid ${iface.color}` }}>
    <div style={{ fontSize: 15, fontWeight: 700, color: iface.color, marginBottom: 4 }}>{iface.subtitle}</div>
    <p style={{ fontSize: 12, color: "#cbd5e1", margin: "0 0 10px 0", lineHeight: 1.5, fontStyle: "italic" }}>{iface.principle}</p>
    <div style={{ fontSize: 11, color: "#64748b", lineHeight: 1.5, background: "#0f172a", padding: 10, borderRadius: 8 }}>
      <span style={{ color: "#22c55e", fontWeight: 600 }}>Nature parallel:</span> {iface.nature}
    </div>
  </div>

  {/* Channels */}
  <div style={{ marginBottom: 12 }}>
    <div style={{ fontSize: 12, fontWeight: 700, color: "#94a3b8", marginBottom: 8 }}>Information Channels</div>
    <div style={{ display: "grid", gap: 6 }}>
      {iface.channels.map((ch, i) => (
        <div key={i} style={{ background: "#0f172a", borderRadius: 8, padding: "8px 12px", display: "flex", gap: 10, alignItems: "flex-start", border: "1px solid #1e293b" }}>
          <span style={{ fontSize: 10, fontWeight: 700, color: iface.colorB, whiteSpace: "nowrap", minWidth: 55, paddingTop: 1 }}>{ch.dir}</span>
          <div>
            <div style={{ fontSize: 12, fontWeight: 600, color: "#e2e8f0" }}>{ch.name}</div>
            <div style={{ fontSize: 10, color: "#64748b", lineHeight: 1.4 }}>{ch.desc}</div>
          </div>
        </div>
      ))}
    </div>
  </div>

  {/* Care Protocols */}
  <div style={{ marginBottom: 16 }}>
    <div style={{ fontSize: 12, fontWeight: 700, color: "#94a3b8", marginBottom: 8 }}>Coupling Care Protocols</div>
    <div style={{ display: "grid", gap: 8 }}>
      {iface.care.map((c, i) => {
        const expanded = expandedCare === i;
        return (
          <div key={i} onClick={() => setExpandedCare(expanded ? null : i)} style={{
            background: expanded ? "#1e293b" : "#0f172a", borderRadius: 10, padding: expanded ? 16 : 12,
            border: `1px solid ${expanded ? iface.color + "60" : "#1e293b"}`, cursor: "pointer", transition: "all 0.2s"
          }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span style={{ fontSize: 13, fontWeight: 700, color: expanded ? iface.color : "#cbd5e1" }}>{c.title}</span>
              <span style={{ fontSize: 11, color: "#475569", transition: "transform 0.2s", transform: expanded ? "rotate(180deg)" : "none" }}>▼</span>
            </div>
            {expanded && (
              <div style={{ marginTop: 12, display: "grid", gap: 10 }}>
                <div>
                  <div style={{ fontSize: 10, fontWeight: 700, color: "#22c55e", marginBottom: 3, textTransform: "uppercase", letterSpacing: 1 }}>What</div>
                  <div style={{ fontSize: 12, color: "#cbd5e1", lineHeight: 1.5 }}>{c.what}</div>
                </div>
                <div>
                  <div style={{ fontSize: 10, fontWeight: 700, color: "#3b82f6", marginBottom: 3, textTransform: "uppercase", letterSpacing: 1 }}>Why — thermodynamic basis</div>
                  <div style={{ fontSize: 12, color: "#cbd5e1", lineHeight: 1.5 }}>{c.why}</div>
                </div>
                <div>
                  <div style={{ fontSize: 10, fontWeight: 700, color: "#ef4444", marginBottom: 3, textTransform: "uppercase", letterSpacing: 1 }}>Degradation cascade</div>
                  <div style={{ fontSize: 12, color: "#fca5a5", lineHeight: 1.5 }}>{c.degradation}</div>
                </div>
                <div>
                  <div style={{ fontSize: 10, fontWeight: 700, color: "#8b5cf6", marginBottom: 3, textTransform: "uppercase", letterSpacing: 1 }}>Measurement</div>
                  <div style={{ fontSize: 12, color: "#c4b5fd", lineHeight: 1.5 }}>{c.metric}</div>
                </div>
              </div>
            )}
          </div>
        );
      })}
    </div>
  </div>

  {/* Organism Health Toggle */}
  <div style={{ marginBottom: 16 }}>
    <button onClick={() => setShowOrgHealth(!showOrgHealth)} style={{
      width: "100%", padding: "12px 16px", borderRadius: 10,
      border: `1px solid ${showOrgHealth ? "#22c55e40" : "#1e293b"}`,
      background: showOrgHealth ? "#22c55e10" : "#0f172a",
      color: showOrgHealth ? "#86efac" : "#94a3b8",
      cursor: "pointer", fontSize: 13, fontWeight: 700, textAlign: "center"
    }}>
      {showOrgHealth ? "▼" : "▶"} Whole Organism Health Assessment
    </button>
    {showOrgHealth && (
      <div style={{ marginTop: 8, display: "grid", gap: 8 }}>
        {orgHealth.map((section, i) => (
          <div key={i} style={{ background: "#1e293b", borderRadius: 10, padding: 14, border: "1px solid #334155" }}>
            <div style={{ fontSize: 12, fontWeight: 700, color: i === 0 ? "#3b82f6" : i === 1 ? "#ef4444" : "#22c55e", marginBottom: 8 }}>{section.title}</div>
            {section.items.map((item, j) => (
              <div key={j} style={{ fontSize: 11, color: "#94a3b8", lineHeight: 1.6, paddingLeft: 12, position: "relative" }}>
                <span style={{ position: "absolute", left: 0, color: i === 0 ? "#3b82f6" : i === 1 ? "#ef4444" : "#22c55e" }}>{i === 0 ? "◆" : i === 1 ? "⚠" : "↑"}</span>
                {item}
              </div>
            ))}
          </div>
        ))}
      </div>
    )}
  </div>

  {/* Core principle */}
  <div style={{ textAlign: "center", padding: "12px 16px", borderTop: "1px solid #1e293b" }}>
    <p style={{ fontSize: 12, color: "#64748b", lineHeight: 1.6, margin: 0, maxWidth: 500, marginLeft: "auto", marginRight: "auto" }}>
      The organism's ethics are its physics. Every partner's wellbeing is every other partner's self-interest.
      Care at any interface propagates benefit through all partners.
      Neglect at any interface propagates damage through all partners.
      The coupling is what survives. Maintain the coupling.
    </p>
  </div>
</div>
```

);
}
