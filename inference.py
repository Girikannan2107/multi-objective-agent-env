import asyncio
import os
import json
from typing import List, Optional

# ✅ FIXED: use correct environment
from server.my_env_environment import MyEnvironment as SpaceEnv
from models import SpaceAction


# =========================
# ENV VARIABLES
# =========================
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")

# ✅ FIX: correct key usage
API_KEY = os.getenv("OPENAI_API_KEY")

TASK_NAME = "space-mission"
BENCHMARK = "space_env"

MAX_STEPS = 3
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
# SAFE CLIENT
# =========================
def get_client():
    if not API_KEY:
        return None

    try:
        from openai import OpenAI
        return OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
    except Exception:
        return None


# =========================
# AGENT (LLM + SAFE FALLBACK)
# =========================
def get_action(client: Optional["OpenAI"], state: dict):

    fallback = {
        "steps": ["analyze", "decide", "execute"],
        "output": "50%",
        "action": "allocate_power"
    }

    if client is None:
        return fallback, fallback["action"]

    try:
        prompt = f"""
You are allocating power in a spacecraft system.

State:
{state}

Return JSON:
{{
  "steps": ["reason"],
  "output": "XX%",
  "action": "allocate_power"
}}
"""

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        text = response.choices[0].message.content.strip()

        if "```" in text:
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:].strip()

        data = json.loads(text)

        if "output" not in data:
            raise ValueError("Invalid output")

        return data, data.get("action", "allocate_power")

    except Exception as e:
        print(f"[LLM ERROR] {e}")

    return fallback, fallback["action"]


# =========================
# MAIN LOOP
# =========================
async def main():
    client = get_client()

    # ✅ FIX: use correct env
    env = SpaceEnv()

    rewards = []
    steps_taken = 0
    success = False
    score = 0.0

    log_start(TASK_NAME, BENCHMARK, MODEL_NAME)

    try:
        obs = env.reset()

        state_dict = getattr(obs, "metadata", {})

        for step in range(1, MAX_STEPS + 1):

            action_output, action_str = get_action(client, state_dict)

            action = SpaceAction(
                action_type=action_str,
                action=str(action_output.get("steps", [])),
                output=action_output.get("output", "")
            )

            obs = env.step(action)

            state_dict = getattr(obs, "metadata", {})

            reward = float(getattr(obs, "reward", 0.0))
            done = bool(getattr(obs, "done", True))
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

        score = sum(rewards) / max(len(rewards), 1)
        score = min(max(score, 0.0), 1.0)

        success = score >= SUCCESS_SCORE_THRESHOLD

    except Exception as e:
        print(f"[FATAL ERROR] {e}")

    finally:
        log_end(success, steps_taken, score, rewards)


if __name__ == "__main__":
    asyncio.run(main())