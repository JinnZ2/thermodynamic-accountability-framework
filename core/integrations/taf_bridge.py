# core/integrations/taf_bridge.py
"""
TAF Bridge Integration
======================
Bidirectional translation layer between the Thermodynamic Accountability
Framework (TAF) and the Geometric Binary Bridge protocol.

Maps TAF physics primitives onto Geometric Bridge sensor/actuator
infrastructure for hardware-aware institutional accounting.

TAF Core Concepts:
  𝒞  (Causal Field)     → Physical reality (intractable)
  Πᵢ (Compression Ops)  → Formatting transformations  
  𝒜(t) (Admissibility)  → What the institution can "see"
  Q(t) (Attribution)    → Fidelity of liability routing
  D(t) (Decoupling)     → Distance between 𝒞 and 𝒜(t) span
  eROI                  → Energy Return on Investment

Usage:
    from core.integrations.taf_bridge import TAFBridge
    
    bridge = TAFBridge()
    accounting = bridge.compute_energy_balance(sensor_data)
    bridge.enforce_thermal_limit(accounting)
"""

import math
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Tuple
from enum import IntEnum


# ----------------------------------------------------------------------
# UPSTREAM: Geometric-to-Binary Computational Bridge
# ----------------------------------------------------------------------
# Prefer the real upstream package when installed; otherwise fall back
# to the functional stdlib implementations in
# schemas/geometric_bridge_contract.py. The contract provides working
# enums, dataclasses, band tuples, Gray-code functions, and minimal
# SensorDecoder / ActuatorController classes -- so TAF works end-to-end
# regardless of whether the external repo is available.
#
# Upstream ref: github.com/JinnZ2/Geometric-to-Binary-Computational-Bridge
# Pinned at commit: see schemas/geometric_bridge_contract.py.

try:
    from geometric_bridge import (  # type: ignore
        SensorDecoder, ActuatorController,
        HardwareData, DrillDepth, BridgeTarget,
        HEALTH_BANDS, TEMP_BANDS, NOISE_BANDS, DRIFT_BANDS,
        gray_to_value, gray_to_binary,
    )
    GEOMETRIC_BRIDGE_AVAILABLE = True
except ImportError:
    # Fall back to the contract's working implementations.
    try:
        from schemas.geometric_bridge_contract import (  # type: ignore
            SensorDecoder, ActuatorController,
            HardwareData, DrillDepth, BridgeTarget,
            HEALTH_BANDS, TEMP_BANDS, NOISE_BANDS, DRIFT_BANDS,
            gray_to_value, gray_to_binary,
        )
    except ImportError:
        import sys as _sys
        import pathlib as _pathlib
        _repo_root = _pathlib.Path(__file__).resolve().parents[2]
        _sys.path.insert(0, str(_repo_root))
        from schemas.geometric_bridge_contract import (  # type: ignore  # noqa: E402
            SensorDecoder, ActuatorController,
            HardwareData, DrillDepth, BridgeTarget,
            HEALTH_BANDS, TEMP_BANDS, NOISE_BANDS, DRIFT_BANDS,
            gray_to_value, gray_to_binary,
        )
    GEOMETRIC_BRIDGE_AVAILABLE = False

# ----------------------------------------------------------------------
# TAF Core Primitives
# ----------------------------------------------------------------------

class CompressionOperator(IntEnum):
    """TAF compression operators (Πᵢ) that format admissible models."""
    PI_LEGAL = 0      # Π_legal: Legal/procedural compression
    PI_ECON = 1       # Π_econ: Economic/market compression  
    PI_SCHEMA = 2     # Π_schema: Schema/bureaucratic compression
    PI_EMBODIED = 3   # Π_embodied: Physical/embodied compression
    PI_RAW = 4        # Direct 𝒞 coupling (no compression)

class AdmissibilityMode(IntEnum):
    """Operational modes of the 𝒜(t) admissibility field."""
    EXPANDING = 0     # 𝒜(t) widening (more reality visible)
    STABLE = 1        # 𝒜(t) steady state
    NARROWING = 2     # 𝒜(t) contracting (reality exclusion)
    COLLAPSED = 3     # 𝒜(t) failure (institutional blindness)

@dataclass
class EnergyAccounting:
    """
    Complete TAF energy balance for an organism/institution pair.
    
    All units in Joules unless specified otherwise.
    """
    # Energy flows
    energy_input: float = 0.0        # E_in: Energy received by organism
    energy_output: float = 0.0       # E_out: Energy expended by organism
    energy_waste: float = 0.0        # E_waste: Entropy generation (unrecoverable)
    energy_balance: float = 0.0      # ΔE = E_in - (E_out + E_waste)
    
    # Institutional extraction
    extraction_rate: float = 0.0     # Fraction of E_out captured by institution
    net_yield: float = 0.0           # E_out - extraction (what organism keeps)
    
    # TAF metrics
    eROI: float = 0.0               # Energy Return on Investment
    q_factor: float = 1.0           # Q(t): Attribution fidelity
    decoupling: float = 0.0          # D(t): 𝒞-to-𝒜(t) distance
    prediction_error: float = 0.0   # Free energy / surprise (Friston)
    
    # Viability flags
    is_extractive: bool = False     # ΔE < 0 → system is extractive
    is_sustainable: bool = False    # Positive long-term energy balance
    time_to_failure: float = float('inf')  # Hours until organism failure
    
    # Bridge integration
    admissibility_mode: AdmissibilityMode = AdmissibilityMode.STABLE
    dominant_compression: CompressionOperator = CompressionOperator.PI_EMBODIED


@dataclass
class AdmissibilityField:
    """
    Dynamic 𝒜(t) field state for Geometric Bridge integration.
    
    Maps TAF's abstract admissibility space onto concrete
    sensor thresholds and actuator limits.
    """
    # 𝒜(t) parameters
    structural_power: float = 0.5    # S: Power to define admissible models
    enforcement: float = 0.5         # E: Feasibility of enforcing 𝒜(t)
    computational_cost: float = 0.5  # C: Cost of maintaining 𝒜(t)
    legacy_path: float = 0.5         # L: Historical inertia
    
    # Field boundaries (mapped to Geometric Bridge bands)
    thermal_limit_c: float = 85.0   # Maximum admissible temperature
    noise_tolerance: float = 0.3    # Maximum admissible noise
    drift_allowance_pct: float = 10.0  # Maximum admissible drift
    
    # Derived
    admissibility_width: float = 1.0  # |𝒜(t)|: Fraction of 𝒞 visible
    excluded_reality_fraction: float = 0.0  # 1 - |𝒜(t)|/|𝒞|
    mode: AdmissibilityMode = AdmissibilityMode.STABLE

# ----------------------------------------------------------------------
# TAF Bridge Core
# ----------------------------------------------------------------------

class TAFBridge:
    """
    Bidirectional bridge between TAF physics and Geometric Binary Protocol.
    
    Translates sensor readings into energy accounting and converts
    TAF-derived operating constraints into actuator commands.
    
    Core Mapping:
      temperature_c  → energy_output (Arrhenius rate)
      noise_level    → prediction_error (Friston free energy)
      confidence     → q_factor (attribution fidelity)
      drift_pct      → decoupling (D(t) evolution)
      health_score   → energy_balance (organism viability)
      drill_depth    → admissibility_mode (institutional response)
    """
    
    # Physical constants for energy conversion
    BASAL_METABOLIC_RATE = 100.0     # Base energy rate (Watts) for organism
    ACTIVATION_ENERGY = 0.8          # Arrhenius activation energy (eV)
    BOLTZMANN_K = 8.617333262e-5     # Boltzmann constant (eV/K)
    EXTRACTION_FLOOR = 0.2           # Minimum institutional extraction
    
    def __init__(self):
        self.decoder = SensorDecoder()
        self.actuator = ActuatorController()
        self.field = AdmissibilityField()
        self.accounting_history: List[EnergyAccounting] = []
    
    # ------------------------------------------------------------------
    # Sensor → TAF Translation (Geometric Bridge → Energy Accounting)
    # ------------------------------------------------------------------
    
    def compute_energy_balance(self, hardware: HardwareData) -> EnergyAccounting:
        """
        Convert Geometric Bridge sensor readings into TAF energy accounting.
        
        Args:
            hardware: Decoded hardware sensor data
            
        Returns:
            Complete EnergyAccounting with all TAF metrics
        """
        acct = EnergyAccounting()
        
        # --- Energy input (from bridge target and effectiveness) ---
        # Higher bridge target = more institutional resource allocation
        base_input = self.BASAL_METABOLIC_RATE
        resource_multiplier = 1.0 + (hardware.bridge_target.value * 0.1)
        acct.energy_input = base_input * resource_multiplier * hardware.effectiveness
        
        # --- Energy output (Arrhenius model from temperature) ---
        # Organism energy expenditure increases exponentially with temperature
        # E_out = A * exp(-Ea / (k * T))
        temp_kelvin = hardware.temperature_c + 273.15
        if temp_kelvin > 0:
            arrhenius_factor = math.exp(
                -self.ACTIVATION_ENERGY / (self.BOLTZMANN_K * temp_kelvin)
            )
        else:
            arrhenius_factor = 0.0
        
        # Scale: 60°C is reference point (1x output)
        ref_kelvin = 60.0 + 273.15
        ref_factor = math.exp(
            -self.ACTIVATION_ENERGY / (self.BOLTZMANN_K * ref_kelvin)
        )
        
        temperature_multiplier = arrhenius_factor / ref_factor if ref_factor > 0 else 1.0
        acct.energy_output = base_input * temperature_multiplier * (1.0 + hardware.noise_level)
        
        # --- Energy waste (entropy from noise and drift) ---
        acct.energy_waste = acct.energy_output * (
            hardware.noise_level + (hardware.drift_pct / 100.0)
        )
        
        # --- Energy balance ---
        acct.energy_balance = acct.energy_input - (
            acct.energy_output + acct.energy_waste
        )
        
        # --- Institutional extraction ---
        # Extraction increases with drift (institution losing visibility)
        # and decreases with confidence (better attribution → fairer extraction)
        acct.extraction_rate = (
            self.EXTRACTION_FLOOR + 
            (hardware.drift_pct / 100.0) * 0.5 -
            hardware.confidence * 0.3
        )
        acct.extraction_rate = max(0.0, min(1.0, acct.extraction_rate))
        
        extraction_amount = acct.energy_output * acct.extraction_rate
        acct.net_yield = acct.energy_output - extraction_amount
        
        # --- eROI (Energy Return on Investment) ---
        # eROI = useful_energy_returned / energy_invested
        if acct.energy_output > 0:
            acct.eROI = acct.net_yield / acct.energy_output
        else:
            acct.eROI = 0.0
        
        # --- Q-factor (Attribution fidelity) ---
        # Decays with noise and improves with confidence
        acct.q_factor = hardware.confidence * (1.0 - hardware.noise_level)
        acct.q_factor = max(0.0, min(1.0, acct.q_factor))
        
        # --- Decoupling D(t) ---
        # Distance between 𝒞 (reality) and 𝒜(t) (institutional view)
        # Increases with drift, noise, and low confidence
        acct.decoupling = (
            (hardware.drift_pct / 100.0) * 0.4 +
            hardware.noise_level * 0.3 +
            (1.0 - hardware.confidence) * 0.3
        )
        acct.decoupling = max(0.0, min(1.0, acct.decoupling))
        
        # --- Prediction error (Friston free energy) ---
        # Noise_level directly maps to prediction error
        acct.prediction_error = hardware.noise_level
        
        # --- Viability flags ---
        acct.is_extractive = acct.energy_balance < 0
        acct.is_sustainable = acct.eROI > 1.0 and not acct.is_extractive
        
        # Time to failure estimation
        if acct.is_extractive:
            # How long until energy reserves depleted
            energy_deficit = abs(acct.energy_balance)
            # Assume organism has 8-hour energy reserve buffer
            energy_reserve = self.BASAL_METABOLIC_RATE * 8 * 3600  # Joules
            if energy_deficit > 0:
                acct.time_to_failure = energy_reserve / energy_deficit / 3600  # Hours
        
        # --- Bridge integration ---
        acct.admissibility_mode = self._compute_admissibility_mode(
            hardware.drill_depth, acct.decoupling
        )
        acct.dominant_compression = self._infer_compression_operator(
            hardware.bridge_target, acct.decoupling
        )
        
        # Store in history
        self.accounting_history.append(acct)
        if len(self.accounting_history) > 1000:
            self.accounting_history = self.accounting_history[-1000:]
        
        return acct
    
    def _compute_admissibility_mode(self, 
                                    drill: DrillDepth, 
                                    decoupling: float) -> AdmissibilityMode:
        """Map Geometric Bridge drill depth to TAF admissibility mode."""
        if drill == DrillDepth.PASS:
            return AdmissibilityMode.EXPANDING
        elif drill == DrillDepth.MONITOR:
            return AdmissibilityMode.STABLE
        elif drill == DrillDepth.ALERT:
            return AdmissibilityMode.NARROWING
        elif drill == DrillDepth.QUARANTINE:
            return AdmissibilityMode.COLLAPSED
        return AdmissibilityMode.STABLE
    
    def _infer_compression_operator(self,
                                     target: 'BridgeTarget',
                                     decoupling: float) -> CompressionOperator:
        """Infer dominant compression operator from bridge target."""
        if target in [BridgeTarget.THERMAL, BridgeTarget.PRESSURE]:
            return CompressionOperator.PI_EMBODIED
        elif target in [BridgeTarget.ELECTRIC, BridgeTarget.MAGNETIC]:
            return CompressionOperator.PI_ECON
        elif target in [BridgeTarget.SOUND, BridgeTarget.WAVE]:
            return CompressionOperator.PI_SCHEMA
        elif target in [BridgeTarget.LIGHT, BridgeTarget.CHEMICAL]:
            return CompressionOperator.PI_LEGAL
        return CompressionOperator.PI_EMBODIED
    
    # ------------------------------------------------------------------
    # TAF → Actuator Translation (Energy Accounting → Actuator Commands)
    # ------------------------------------------------------------------
    
    def update_admissibility_field(self, 
                                   acct: EnergyAccounting,
                                   institution_power: float = 0.5) -> AdmissibilityField:
        """
        Update 𝒜(t) field based on energy accounting.
        
        As decoupling increases, the admissibility field narrows,
        excluding more of reality from institutional view.
        
        Args:
            acct: Current energy accounting
            institution_power: Structural power parameter S
            
        Returns:
            Updated AdmissibilityField
        """
        # Update field parameters
        self.field.structural_power = institution_power
        self.field.enforcement = acct.q_factor  # Enforcement degrades with Q
        self.field.computational_cost = acct.prediction_error
        self.field.legacy_path = self.field.legacy_path * 0.95 + 0.05  # Inertia
        
        # Compute admissibility width: |𝒜(t)|
        # Narrowing occurs when enforcement is weak and decoupling high
        enforcement_weight = self.field.enforcement
        decoupling_penalty = acct.decoupling
        
        self.field.admissibility_width = (
            enforcement_weight * (1.0 - decoupling_penalty) *
            self.field.structural_power
        )
        self.field.admissibility_width = max(0.0, min(1.0, self.field.admissibility_width))
        
        # Excluded reality
        self.field.excluded_reality_fraction = 1.0 - self.field.admissibility_width
        
        # Update thermal limits based on admissibility
        # Narrower 𝒜(t) → lower allowable temperature (institution can't "see" high temps)
        self.field.thermal_limit_c = TEMP_BANDS[-1] * self.field.admissibility_width + 25.0
        self.field.noise_tolerance = NOISE_BANDS[-1] * self.field.admissibility_width
        self.field.drift_allowance_pct = DRIFT_BANDS[-1] * self.field.admissibility_width
        
        # Determine mode
        if self.field.admissibility_width > 0.8:
            self.field.mode = AdmissibilityMode.EXPANDING
        elif self.field.admissibility_width > 0.5:
            self.field.mode = AdmissibilityMode.STABLE
        elif self.field.admissibility_width > 0.2:
            self.field.mode = AdmissibilityMode.NARROWING
        else:
            self.field.mode = AdmissibilityMode.COLLAPSED
        
        return self.field
    
    def enforce_thermal_limit(self, acct: EnergyAccounting):
        """
        Apply TAF-derived thermal constraints to actuator.
        
        If the energy balance is extractive, restrict thermal output
        to prevent organism burnout (biological or mechanical).
        """
        self.update_admissibility_field(acct)
        
        # Determine safe operating temperature
        if acct.is_extractive:
            # Reduce temperature to slow organism energy consumption
            safe_temp = max(
                25.0,  # Minimum safe temperature
                self.field.thermal_limit_c * 0.7  # 30% derating
            )
            confidence = 1.0 - acct.decoupling
        else:
            safe_temp = self.field.thermal_limit_c
            confidence = acct.q_factor
        
        self.actuator.set_thermal(safe_temp, confidence)
    
    def compute_institutional_health(self) -> Dict[str, Any]:
        """
        Compute institutional health metrics from accounting history.
        
        Returns:
            Dictionary with TAF-derived health indicators
            mapped to Geometric Bridge band structures
        """
        if not self.accounting_history:
            return {"status": "no_data"}
        
        # Recent window
        window = self.accounting_history[-100:]
        
        # Average decoupling trend
        decoupling_trend = [a.decoupling for a in window]
        avg_decoupling = sum(decoupling_trend) / len(decoupling_trend)
        decoupling_velocity = (
            decoupling_trend[-1] - decoupling_trend[0]
        ) / len(decoupling_trend) if len(decoupling_trend) > 1 else 0.0
        
        # Q-factor trend
        q_trend = [a.q_factor for a in window]
        avg_q = sum(q_trend) / len(q_trend)
        
        # Sustainability fraction
        sustainable_count = sum(1 for a in window if a.is_sustainable)
        sustainability_fraction = sustainable_count / len(window)
        
        # Map to Geometric Bridge bands
        health_band = 0
        for i, threshold in enumerate(HEALTH_BANDS):
            if sustainability_fraction >= threshold:
                health_band = i
        
        noise_band = 0
        avg_noise = sum(a.prediction_error for a in window) / len(window)
        for i, threshold in enumerate(NOISE_BANDS):
            if avg_noise >= threshold:
                noise_band = i
        
        return {
            "sustainability_fraction": sustainability_fraction,
            "health_score": HEALTH_BANDS[health_band],
            "avg_decoupling": avg_decoupling,
            "decoupling_velocity": decoupling_velocity,
            "avg_q_factor": avg_q,
            "noise_level": NOISE_BANDS[noise_band],
            "admissibility_width": self.field.admissibility_width,
            "excluded_reality": self.field.excluded_reality_fraction,
            "mode": self.field.mode.name,
            "is_institutional_failure": avg_decoupling > 0.7 and decoupling_velocity > 0,
            "recommended_drill": self._recommend_drill_depth(avg_decoupling)
        }
    
    def _recommend_drill_depth(self, decoupling: float) -> str:
        """Recommend Geometric Bridge drill depth from TAF decoupling."""
        if decoupling < 0.2:
            return DrillDepth.PASS.name
        elif decoupling < 0.5:
            return DrillDepth.MONITOR.name
        elif decoupling < 0.8:
            return DrillDepth.ALERT.name
        else:
            return DrillDepth.QUARANTINE.name
    
    # ------------------------------------------------------------------
    # Narrative Translation (TAF's "culture is overlay" in action)
    # ------------------------------------------------------------------
    
    NARRATIVE_TRANSLATIONS = {
        "driver shortage": "energy balance negative: extraction rate exceeds organism tolerance",
        "worker laziness": "prediction error elevated: chaotic environment increases free energy",
        "industry standard turnover": "decoupling threshold exceeded: 𝒞-to-𝒜(t) distance critical",
        "market correction": "Q-factor decay below viability: attribution fidelity lost",
        "human error": "admissibility field narrowing: causal exclusion active",
        "equipment failure": "entropy accumulation exceeds dissipation capacity",
        "budget constraint": "structural power S insufficient to maintain 𝒜(t) width",
        "policy change": "Π_schema compression operator updated: new admissible model class",
    }
    
    def translate_narrative(self, narrative: str) -> str:
        """
        Translate institutional narrative into TAF physics.
        
        "Culture is an overlay; physics is foundational."
        
        Args:
            narrative: Institutional label or explanation
            
        Returns:
            TAF physical root cause
        """
        narrative_lower = narrative.lower()
        for pattern, translation in self.NARRATIVE_TRANSLATIONS.items():
            if pattern in narrative_lower:
                return translation
        return f"Unmapped narrative. Requesting 𝒞 coupling: '{narrative}'"
    
    def identify_root_cause(self, hardware: HardwareData) -> List[str]:
        """
        Identify physical root causes behind sensor readings.
        
        Never stops at institutional labels—always traces to physics.
        
        Returns:
            List of TAF root cause statements
        """
        acct = self.compute_energy_balance(hardware)
        causes = []
        
        if acct.is_extractive:
            causes.append(
                f"Energy extraction rate ({acct.extraction_rate:.2f}) exceeds "
                f"organism yield ({acct.eROI:.2f} eROI). "
                f"Time to failure: {acct.time_to_failure:.1f} hours."
            )
        
        if acct.decoupling > 0.5:
            causes.append(
                f"Decoupling D(t) = {acct.decoupling:.2f}: "
                f"{acct.excluded_reality_fraction*100:.1f}% of reality excluded "
                f"from {acct.dominant_compression.name} compression."
            )
        
        if acct.q_factor < 0.3:
            causes.append(
                f"Attribution fidelity Q = {acct.q_factor:.2f}: "
                f"Liability routing degraded—causes cannot be assigned."
            )
        
        if hardware.noise_level > 0.5:
            causes.append(
                f"Prediction error {acct.prediction_error:.2f}: "
                f"Organism spending excessive energy on model maintenance."
            )
        
        if not causes:
            causes.append("System within sustainable operating parameters.")
        
        return causes

# ----------------------------------------------------------------------
# Simulation Integration
# ----------------------------------------------------------------------

def simulate_taf_decay_arc(duration_hours: float = 100.0, 
                          time_step: float = 1.0) -> List[Dict[str, Any]]:
    """
    Simulate the full TAF decay arc through Geometric Bridge.
    
    Models how an initially sustainable system degrades through:
    1. Increasing extraction rate
    2. Q-factor decay
    3. Admissibility field narrowing
    4. Causal exclusion cascade
    
    Args:
        duration_hours: Total simulation time
        time_step: Time resolution in hours
        
    Returns:
        List of state snapshots showing the decay arc
    """
    bridge = TAFBridge()
    decoder = SensorDecoder()
    history = []
    
    # Initial state: healthy hardware
    initial_bits = (
        "000"  # failure: none (Gray 000)
        "111"  # health: 0.875 (Gray 111→binary 101=5)
        "0"    # not critical
        "1"    # confidence high
        "1"    # has synergy
        "011"  # voltage: 0.5V
        "011"  # current: 0.001A
        "100"  # temp: 65°C (Gray 100→binary 111=7→175? no, re-index)
        "001"  # noise: 0.01
        "011"  # repurpose
        "10"   # effectiveness: 5.0
        "011"  # bridge: magnetic
        "01"   # drift: 1.0%
        "1"    # salvageable
        "1"    # fallback_ready
        "111"  # lifetime: 5000h
        "00"   # drill: PASS
        "1"    # semiconductor
    )
    
    # Simulate decay
    for t in range(int(duration_hours / time_step)):
        time = t * time_step
        
        # Artificially degrade parameters over time
        noise_injection = min(0.8, 0.01 + time * 0.008)
        drift_accumulation = min(45.0, 1.0 + time * 0.4)
        temp_rise = min(150.0, 65.0 + time * 0.5)
        
        # Build degraded hardware state
        hardware = HardwareData(
            failure_mode="drift" if drift_accumulation > 10 else "none",
            health_score=max(0.0, 0.875 - time * 0.008),
            is_critical=drift_accumulation > 30,
            confidence_hi=False,
            has_synergy=True,
            voltage_v=0.5 + noise_injection,
            current_a=0.001 + noise_injection * 0.01,
            temperature_c=temp_rise,
            noise_level=noise_injection,
            repurpose_class="unknown",
            effectiveness=max(0.0, 5.0 - noise_injection * 5),
            bridge_target=BridgeTarget.MAGNETIC,
            drift_pct=drift_accumulation,
            salvageable=drift_accumulation < 40,
            fallback_ready=True,
            lifetime_hours=max(0, 5000 - time * 45),
            drill_depth=DrillDepth.MONITOR,
            is_semiconductor=True,
            confidence=max(0.0, 1.0 - noise_injection)
        )
        
        # Compute TAF accounting
        acct = bridge.compute_energy_balance(hardware)
        bridge.update_admissibility_field(acct)
        
        # Record state
        history.append({
            "time_h": time,
            "energy_balance": acct.energy_balance,
            "eROI": acct.eROI,
            "q_factor": acct.q_factor,
            "decoupling": acct.decoupling,
            "extraction_rate": acct.extraction_rate,
            "admissibility_width": bridge.field.admissibility_width,
            "is_sustainable": acct.is_sustainable,
            "time_to_failure": acct.time_to_failure,
            "mode": bridge.field.mode.name,
        })
        
        # Break if system has fully collapsed
        if bridge.field.mode == AdmissibilityMode.COLLAPSED and time > 50:
            break
    
    return history
