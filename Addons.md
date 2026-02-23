dashboard:

def collapse_risk(adaptive_practice, ceremony_vitality, power_concentration):
    # Probability of crossing min(K) threshold within 50 years
    base_risk = (1 - adaptive_practice) * (1 - ceremony_vitality)
    power_multiplier = 1 + 2 * power_concentration
    return min(1.0, base_risk * power_multiplier)

    resilience score:

    def resilience_index(node):
    # Weighted geometric mean of critical systems
    return (
        node.adaptive_practice ** 0.3 *
        node.ceremony_vitality ** 0.2 *
        (1 - node.power_concentration) ** 0.2 *
        node.IPI ** 0.15 *
        node.knowledge_distribution ** 0.15
    )

    collapse probability surface:

    def collapse_risk(adaptive_practice, ceremony_vitality, power_concentration):
    # Probability of crossing min(K) threshold within 50 years
    base_risk = (1 - adaptive_practice) * (1 - ceremony_vitality)
    power_multiplier = 1 + 2 * power_concentration
    return min(1.0, base_risk * power_multiplier)

    
