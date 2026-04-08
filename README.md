---
title: "Orbital Resource Manager: AI Decision Environment"
emoji: "🚀"
colorFrom: purple
colorTo: red
sdk: docker
app_port: 8000
tags:
  - openenv
  - ai-agents
  - reinforcement-learning
  - decision-making
---

# Orbital Resource Manager: AI Decision Environment

> An AI evaluation environment simulating spacecraft power allocation under real-world constraints — testing an agent's ability to make priority-aware, resource-constrained decisions.

---

## Overview

Modern AI systems must operate under limited resources and competing priorities. The Orbital Resource Manager simulates a spacecraft scenario where an agent must allocate power efficiently across critical systems, each with distinct requirements and priority levels.

The evaluation focuses on four core dimensions:

- Correctness of the allocation decision
- Prioritization logic across system tiers
- Adherence to hard resource constraints
- Robustness under varying and emergency task conditions

---

## Problem Statement

Given a fixed power budget, the agent must:

- Allocate power across multiple active spacecraft systems
- Prioritize critical systems such as life support above lower-priority ones
- Resolve conflicting resource requirements under tight constraints
- Maintain safe operation during emergency conditions

A suboptimal allocation — over-powering low-priority systems or under-powering critical ones — results in mission degradation and negative reward.

---

## Key Features

- **Multi-level tasks** — Easy, Medium, and Hard difficulty modes
- **Priority-based allocation** — Systems ranked as high, medium, or low priority
- **Deterministic reward system** — Consistent, reproducible scoring across episodes
- **Partial scoring** — Near-correct decisions receive proportional credit
- **Penalty enforcement** — Incorrect or unsafe allocations are penalized
- **Fully containerized** — Docker-based deployment out of the box
- **Hugging Face Spaces compatible** — Ready for cloud deployment

---

## Environment Design

### State

At each step, the environment provides a structured observation:

| Field               | Type   | Description                                      |
|---------------------|--------|--------------------------------------------------|
| `power_available`   | float  | Total power units available for allocation       |
| `systems`           | dict   | Active systems with requirements and priorities  |
| `emergency`         | bool   | Whether an emergency condition is active         |
| `step`              | int    | Current step index within the episode            |

Priority levels: `high`, `medium`, `low`

Example observation:

```json
{
  "power_available": 100,
  "systems": {
    "life_support": {
      "required": 40,
      "priority": "high"
    },
    "navigation": {
      "required": 30,
      "priority": "medium"
    },
    "communications": {
      "required": 20,
      "priority": "medium"
    },
    "sensors": {
      "required": 10,
      "priority": "low"
    }
  },
  "emergency": false,
  "step": 1
}
```

### Action

The agent submits a single structured action per step:

```python
action = {
    "allocate_power": {
        "life_support":   float,
        "navigation":     float,
        "communications": float,
        "sensors":        float
    }
}
```

Total allocated power must not exceed `power_available`. Exceeding the budget is treated as a constraint violation.

### Reward

Rewards are computed deterministically based on allocation accuracy and priority adherence:

| Scenario                                  | Reward          |
|-------------------------------------------|-----------------|
| Optimal allocation across all systems     | `+1.0`          |
| Near-optimal (within tolerance margin)    | `+0.5`          |
| High-priority system under-allocated      | `-0.5`          |
| Power budget exceeded                     | `-1.0`          |
| Critical system receives zero power       | `-1.0`          |
| Emergency condition mishandled            | `-1.0`          |

---

## Task Levels

### Easy
- 2 active systems
- No emergency conditions
- Wide allocation tolerance
- Suitable for baseline testing and environment validation

### Medium
- 4 active systems with mixed priorities
- Occasional emergency flags
- Tighter allocation margins
- Tests prioritization logic and constraint handling

### Hard
- All systems active with conflicting requirements
- Frequent emergency conditions
- Strict power budget with no slack
- Requires precise, priority-aware decision-making under pressure

---

## Constraints

The following constraints govern agent behavior and evaluation:

### Resource Constraints
- Total allocated power must not exceed `power_available` at any step
- Each system has a minimum required allocation — falling below it incurs a penalty
- Power cannot be carried over between steps

### Priority Constraints
- High-priority systems must be fully satisfied before medium or low-priority systems receive allocation
- Under emergency conditions, non-critical systems must be deprioritized automatically

### Action Constraints
- The agent must allocate power to all active systems in every step
- Allocations must be non-negative floats
- Malformed or missing actions receive a reward of `0.0`

### Evaluation Constraints
- Rewards are computed deterministically — the agent cannot influence the scoring logic
- Episodes are fixed-length per difficulty level
- The agent cannot observe the reward function directly; it must learn from feedback signals

---

## Architecture

```
Agent
  |
  v
Action: allocate_power (per system)
  |
  v
Orbital Resource Manager Environment
  |
  v
Evaluation Pipeline:
  - Budget constraint check
  - Priority adherence scoring
  - Emergency condition handling
  - Reward computation
  |
  v
Reward Signal + Next Observation
```

---

## Project Structure

```
orbital-resource-manager/
│
├── models.py
├── inference.py
├── openenv.yaml
│
└── server/
    ├── app.py
    ├── env.py
    ├── models.py
    ├── tasks.py
    ├── Dockerfile
    └── __init__.py
```

---

## Setup Instructions

### Prerequisites
- Python 3.10+
- Docker
- `openenv` CLI (for HF deployment)

### Run Locally

```bash
git clone https://github.com/your-username/orbital-resource-manager.git
cd orbital-resource-manager

pip install -r requirements.txt
uvicorn server.app:app --reload
```

### Development Testing

```bash
python server/env.py
```

---

## Docker Deployment

Build and run the environment container:

```bash
docker build -t orbital-resource-manager:latest -f server/Dockerfile .
docker run --rm -p 8000:8000 orbital-resource-manager:latest
```

---

## Hugging Face Deployment

Deploy with a single command:

```bash
openenv push --repo-id your-username/orbital-resource-manager
```

Your environment will be available at:

```
https://huggingface.co/spaces/your-username/orbital-resource-manager
```

### Available Endpoints

| Endpoint  | Description         |
|-----------|---------------------|
| `/web`    | Interactive UI      |
| `/docs`   | API documentation   |
| `/health` | Health check        |
| `/ws`     | WebSocket endpoint  |

---

## Example Output

```
[START] Episode initialized | Level: medium | Power Available: 100 units
        Systems: life_support (high), navigation (medium), communications (medium), sensors (low)
        Emergency: false

[STEP 1] Action: { life_support: 40, navigation: 30, communications: 20, sensors: 10 }
         Reward: +1.0 | Reason: Optimal allocation, all priorities satisfied
         Observation: power_remaining=0, all systems nominal

[STEP 2] Action: { life_support: 15, navigation: 40, communications: 30, sensors: 15 }
         Reward: -0.5 | Reason: High-priority system under-allocated
         Observation: life_support below required threshold

[STEP 3] Action: { life_support: 38, navigation: 32, communications: 20, sensors: 10 }
         Reward: +0.5 | Reason: Near-optimal, within acceptable tolerance

[END] Episode complete | Total Reward: 1.0 | Steps: 3 | Grade: PASS
```

---

## Future Work

- PPO and DQN baseline agents for benchmarking
- TensorBoard integration for training visualization
- Stochastic mode with randomized system requirements
- Multi-agent cooperative power management
- REST API wrapper for external agent interaction
- PyPI package release

---

## Author

**[Girikannan M P]**
AI/ML Engineer | Reinforcement Learning

- [Hugging Face](https://huggingface.co/Girikannan)
- [GitHub](https://github.com/Girikannan2107)

---

<div align="center">

Licensed under MIT

</div>
