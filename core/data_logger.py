class EnergyAccounting:
    def __init__(self, hourly_metabolic_rate=1.0):
        self.metabolic_rate = hourly_metabolic_rate # Base mammal energy
        
    def calculate_parasitic_load(self, unpaid_hours, friction_events):
        """
        unpaid_hours: Hours worked but not compensated (Metabolic theft)
        friction_events: Integer count of systemic failures (Yard search, flats, etc.)
        """
        # Energy extracted without resource replenishment
        energy_debt = unpaid_hours * self.metabolic_rate
        
        # Friction adds "heat" which increases the metabolic cost of the remaining work
        friction_multiplier = 1 + (friction_events * 0.15)
        total_life_energy_tax = energy_debt * friction_multiplier
        
        return total_life_energy_tax

# Case Study: The 70-Hour Week
taf_log = EnergyAccounting()
debt = taf_log.calculate_parasitic_load(unpaid_hours=30, friction_events=5)

print(f"Total Life Energy Tax: {debt} units of Sovereign Entropy")
