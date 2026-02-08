import datetime

class TAF_Engine:
    def __init__(self):
        self.entropy_threshold = 0.15 # Acceptable friction
        
    def analyze_event(self, planned_miles, actual_miles, search_time_min, mechanical_failure=False):
        # 1. Calculate Institutional Friction (Heat)
        # Time spent searching is energy diverted from the primary mission (resource acquisition)
        heat_leak = search_time_min / 60 
        
        # 2. Mammal Stress (Prediction Error)
        # If the system said the trailer was there, but it wasn't, dissonance is high.
        prediction_error = 1.0 if search_time_min > 20 else 0.0
        
        # 3. Functional Reality
        if mechanical_failure:
            heat_leak *= 2  # Mechanical entropy compounds biological fatigue
            
        return {
            "System_Efficiency": f"{1 - (heat_leak / 14):.2%}", # 14-hour clock baseline
            "Mammal_Status": "Homeostasis" if prediction_error == 0 else "High Prediction Error (Frustration)",
            "Root_Cause": "Data Fidelity Failure" if search_time_min > 0 else "Optimal Flow"
        }

# Initializing the Test
taf = TAF_Engine()
# Simulation: 30 min search for a trailer with flat tires
log_entry = taf.analyze_event(planned_miles=500, actual_miles=0, search_time_min=30, mechanical_failure=True)

print(f"--- TAF DIAGNOSTIC ---\nEfficiency: {log_entry['System_Efficiency']}\nStatus: {log_entry['Mammal_Status']}\nCause: {log_entry['Root_Cause']}")
