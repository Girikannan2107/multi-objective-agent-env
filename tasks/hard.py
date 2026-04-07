def get_task():
    return {
        "power_available": 60,
        "systems": {
            "life_support": {"required": 40, "priority": "high"},
            "navigation": {"required": 30, "priority": "medium"},
            "communication": {"required": 20, "priority": "low"}
        },
        "emergency": True
    }