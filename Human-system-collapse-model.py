import math

# --- HUMAN SYSTEM COLLAPSE MODULE WITH DISTANCE METRIC ---
class HumanSystemModel:
    """
    Models human energy ledger, fatigue, and system collapse thresholds,
    plus distance-to-collapse metric.
    """

    def __init__(self, energy_input=100):
        self.energy_input = energy_input  # baseline energy humans can expend safely

    # Hidden variable multiplier
    def hidden_var_multiplier(self, hidden_count):
        return 1.0 if hidden_count <= 0 else 1 + 0.1 * hidden_count ** 1.5

    # Automation cognitive load multiplier
    def automation_multiplier(self, automation_count, reliability=0.9):
        return 1 + automation_count * (1 - reliability) * 0.5

    # Environmental stress multiplier
    def environment_multiplier(self, temp_celsius, wind_mps):
        temp_stress = max(0, (15 - temp_celsius) * 0.05)
        wind_stress = wind_mps * 0.02
        return 1 + temp_stress + wind_stress

    # Compute fatigue and total energy load
    def compute_fatigue(self, physical_load, cognitive_load,
                        hidden_count=0, automation_count=0, automation_reliability=0.9,
                        temp_celsius=20, wind_mps=0):
        total_load = physical_load + cognitive_load
        total_load *= self.hidden_var_multiplier(hidden_count)
        total_load *= self.automation_multiplier(automation_count, automation_reliability)
        total_load *= self.environment_multiplier(temp_celsius, wind_mps)

        deficit = total_load - self.energy_input
        fatigue_score = max(0, min(10, deficit / self.energy_input * 10))
        return round(fatigue_score, 1), total_load

    # Compute distance to collapse
    def compute_distance_to_collapse(self, total_load):
        """
        Returns a 0-1 scale:
        1 = fully sustainable (load << energy input)
        0 = collapse threshold reached (load >= health threshold)
        """
        health_threshold = 1.6 * self.energy_input
        distance = max(0.0, min(1.0, (health_threshold - total_load) / health_threshold))
        return round(distance, 2)

    # Full assessment
    def assess_system(self, physical_load, cognitive_load,
                      hidden_count=0, automation_count=0, automation_reliability=0.9,
                      temp_celsius=20, wind_mps=0):
        fatigue_score, total_load = self.compute_fatigue(
            physical_load, cognitive_load,
            hidden_count, automation_count, automation_reliability,
            temp_celsius, wind_mps
        )
        distance_to_collapse = self.compute_distance_to_collapse(total_load)

        # Determine flags
        flags = []
        prod_threshold = 1.2 * self.energy_input
        safety_threshold = 1.4 * self.energy_input
        health_threshold = 1.6 * self.energy_input

        if total_load >= health_threshold:
            flags.append("!! HUMAN HEALTH COLLAPSE IMMINENT")
        elif total_load >= safety_threshold:
            flags.append("!! SAFETY SYSTEM BREAKDOWN LIKELY")
        elif total_load >= prod_threshold:
            flags.append("! PRODUCTIVITY DEGRADATION")
        else:
            flags.append("(System within sustainable limits)")

        return {
            "fatigue_score": fatigue_score,
            "total_load": total_load,
            "distance_to_collapse": distance_to_collapse,
            "flags": flags
        }

# --- EXAMPLE USAGE ---
if __name__ == "__main__":
    human_system = HumanSystemModel(energy_input=100)

    # Scenario
    physical_load = 30
    cognitive_load = 40
    hidden_count = 7
    automation_count = 3
    automation_reliability = 0.85
    temp_celsius = -12
    wind_mps = 15

    assessment = human_system.assess_system(
        physical_load, cognitive_load,
        hidden_count, automation_count, automation_reliability,
        temp_celsius, wind_mps
    )

    print(f"Predicted Fatigue Score: {assessment['fatigue_score']}/10")
    print(f"Total Energy Load: {assessment['total_load']} units")
    print(f"Distance to Collapse: {assessment['distance_to_collapse']*100}%")
    for flag in assessment['flags']:
        print(flag)
