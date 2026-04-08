import random

# ---------------------------
# TASK 1 — EASY
# ---------------------------
def task_easy():
    return {
        "difficulty": "easy",
        "power_available": 100,
        "systems": {
            "life_support": {"required": 40, "priority": "high"}
        },
        "emergency": False
    }

# ---------------------------
# TASK 2 — MEDIUM
# ---------------------------
def task_medium():
    return {
        "difficulty": "medium",
        "power_available": 80,
        "systems": {
            "life_support": {"required": 50, "priority": "high"},
            "navigation": {"required": 30, "priority": "medium"}
        },
        "emergency": False
    }

# ---------------------------
# TASK 3 — HARD
# ---------------------------
def task_hard():
    return {
        "difficulty": "hard",
        "power_available": 60,
        "systems": {
            "life_support": {"required": 55, "priority": "high"},
            "navigation": {"required": 20, "priority": "medium"}
        },
        "emergency": True
    }

# ---------------------------
# RANDOM TASK PICKER
# ---------------------------
def get_dynamic_task():
    tasks = [task_easy, task_medium, task_hard]
    return random.choice(tasks)()