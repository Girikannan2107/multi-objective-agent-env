# Space Mission: Multi-Objective Agent Environment

An autonomous agent-environment framework for spacecraft resource management, built using the **OpenEnv** framework.

## 🚀 Overview

This repository contains a functional "Space Mission" environment designed to evaluate an agent's ability to manage critical spacecraft resources. Unlike static test environments, this project features a **dynamic evaluation system** that randomizes task difficulty and system requirements during each reset.

### The Mission
The agent acts as the spacecraft's Energy Management System (EMS). It must analyze the current power reserves and allocate specific energy percentages to critical systems (Life Support, Navigation, Communication) to maximize crew safety and mission success.

---

## 🛠 Project Architecture

| Component | Description |
| :--- | :--- |
| `inference.py` | The main evaluation script. Runs the agent-environment loop and generates standardized logs. |
| `server/my_env_environment.py` | Core environment logic. Implements rewards, state transitions, and task loading. |
| `tasks/` | Dynamic scenario library (`easy.py`, `medium.py`, `hard.py`) for variable difficulty. |
| `models.py` | Pydantic data models for structured Actions and Observations. |
| `Dockerfile` | Containerization for both the environment server and the inference pipeline. |

---

## 🏗 Environment Dynamics

### State Space (`SpaceObservation`)
The environment provides the following real-time data:
- **Power Available**: Total remaining kilowatts.
- **System Requirements**: A mapping of systems (Life Support, etc.) to their specific power needs.
- **Emergency Status**: Boolean flag indicating if critical repairs are required.

### Action Space (`SpaceAction`)
The agent communicates its plan via:
- **Action Type**: String category (e.g., `allocate_power`).
- **Action Description**: Detailed plan for execution.
- **Output**: The specific numerical allocation (e.g., `"40%"`).

### Reward Calculation
The environment uses a **precision-based reward grader**:
- **1.00 (Perfect)**: Exact match between allocation and system requirement.
- **0.50 (Partial)**: Allocation within ±10% of the requirement.
- **-1.00 (Failure)**: Incorrect action type or wildly inaccurate allocation.

---

## 🚦 Getting Started

### 1. Installation
Ensure you have the environment framework installed:
```bash
pip install openenv-core openai
```

### 2. Configure API Key
The agent uses **Qwen-2.5-72B-Instruct** via Hugging Face. Set your token as an environment variable:
```powershell
$env:HF_TOKEN = "your_token_here"
```

### 3. Run Evaluation
Execute the baseline inference script to test the agent:
```bash
python inference.py
```

---

## 📊 Grading & Logs

This project implements strict logging standards for evaluation compatibility. Each run produces standardized output:
- `[START]`: Mission initialization details.
- `[STEP]`: Action details, rewards, and system feedback.
- `[END]`: Final success metrics and aggregate scores.

---

## 📦 Deployment

To build and run the environment in a clean container:
```bash
docker build -t space-mission-env .
docker run space-mission-env
```

Created as part of the **Meta Hackathon - OpenEnv Track**.
