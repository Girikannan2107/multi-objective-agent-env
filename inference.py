import asyncio
import os
from typing import List, Optional

from openai import OpenAI

from server.my_env_environment import MyEnvironment
from models import SpaceAction


# =========================
# ENV VARIABLES
# =========================
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
API_KEY = os.getenv("HF_TOKEN")

TASK_NAME = "space-mission"
BENCHMARK = "space_env"

MAX_STEPS = 10
SUCCESS_SCORE_THRESHOLD = 0.3


# =========================
# LOGGING (STRICT FORMAT)
# =========================
def log_start(task: str, env: str, model: str):
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]):
    error_val = error if error else "null"
    done_val = str(done).lower()

    print(
        f"[STEP] step={step} action={action} reward={reward:.2f} done={done_val} error={error_val}",
        flush=True
    )


def log_end(success: bool, steps: int, score: float, rewards: List[float]):
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)

    print(
        f"[END] success={str(success).lower()} steps={steps} score={score:.2f} rewards={rewards_str}",
        flush=True
    )


# =========================
# SIMPLE AGENT (LLM + RULE)
# =========================
def get_action(client: OpenAI, state: dict):
    try:
        prompt = f"""
You are controlling a spacecraft energy allocation system.

Current Mission State:
{state}

Goal:
Allocate the EXACT required percentage of power to the 'life_support' system to maximize reward.

Return JSON only:
{{
  "steps": ["Observation of needs", "Calculated allocation"],
  "output": "XX%", 
  "action": "allocate_power"
}}
"""

        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=100
        )

        text = (completion.choices[0].message.content or "").strip()

    except Exception:
        text = "fallback"

    # Try to parse the LLM response
    llm_data = {}
    if text != "fallback":
        try:
            import json
            # Extract JSON if it's wrapped in triple backticks
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
            llm_data = json.loads(text)
        except Exception:
            llm_data = {}

    # fallback logic based on real state structure
    try:
        # Defaults for the Space Mission environment
        fallback_action = "allocate_power"
        fallback_output = "40%"

        if state.get("emergency", False):
            fallback_action = "allocate_power"
        
        power = state.get("power_available", 0)
        if power < 50:
            fallback_action = "allocate_power"
    except Exception:
        fallback_action = "allocate_power"
        fallback_output = "0%"

    # Final action selection
    action_str = llm_data.get("action", fallback_action)
    output_str = llm_data.get("output", fallback_output)

    # structured output for logging
    action_output = {
        "steps": llm_data.get("steps", ["analyze", "decide", "execute"]),
        "output": output_str,
        "action": action_str
    }

    return action_output, action_str


# =========================
# MAIN LOOP
# =========================
async def main():
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)

    env = MyEnvironment()

    rewards = []
    steps_taken = 0
    success = False
    score = 0.0

    log_start(TASK_NAME, BENCHMARK, MODEL_NAME)

    try:
        obs = env.reset()
        # The environment returns the actual task state in metadata["state"]
        state_dict = obs.metadata.get("state", {})

        for step in range(1, MAX_STEPS + 1):

            action_output, action_str = get_action(client, state_dict)

            # Map the LLM's structured output to the SpaceAction model
            action = SpaceAction(
                action_type=action_str,
                action=action_output.get("action", ""),
                output=action_output.get("output", "")
            )

            obs = env.step(action)
            
            # Update state for next step feedback (if environment was multi-step)
            state_dict = obs.metadata.get("state", {})
            
            reward = float(obs.reward or 0.0)
            done = obs.done
            error = None

            rewards.append(reward)
            steps_taken = step

            log_step(
                step=step,
                action=str(action_output),
                reward=reward,
                done=done,
                error=error
            )

            if done:
                break

        score = sum(rewards) / (len(rewards) or 1)
        score = min(max(score, 0.0), 1.0)

        success = score >= SUCCESS_SCORE_THRESHOLD

    finally:
        log_end(success, steps_taken, score, rewards)


if __name__ == "__main__":
    asyncio.run(main())