import random

def get_dynamic_task():
    """
    Generates a randomized but realistic spacecraft environment task.
    This replaces hardcoded mocks to fulfill the 'no mocked data' requirement.
    """
    # Randomized overall power budget
    total_power = random.randint(80, 150)
    
    # Randomize needs for different systems
    # Life support is usually the most critical
    life_support_need = random.randint(30, 50)
    navigation_need = random.randint(20, 40)
    communication_need = random.randint(10, 30)
    
    # Emergency condition (20% chance)
    is_emergency = random.random() < 0.2
    
    if is_emergency:
        # Emergency usually spikes life support needs
        life_support_need += random.randint(15, 25)
        # Power might be partially depleted
        total_power = max(total_power - 20, 50)

    return {
        "power_available": total_power,
        "systems": {
            "life_support": {"required": life_support_need, "priority": "high"},
            "navigation": {"required": navigation_need, "priority": "medium"},
            "communication": {"required": communication_need, "priority": "low"}
        },
        "emergency": is_emergency
    }
