from uuid import uuid4
import re

from openenv.core.env_server.interfaces import Environment
from openenv.core.env_server.types import State

try:
    from models import SpaceAction, SpaceObservation
except ImportError:
    from ..models import SpaceAction, SpaceObservation

from .tasks import get_dynamic_task


class MyEnvironment(Environment):

    SUPPORTS_CONCURRENT_SESSIONS: bool = True

    def __init__(self):
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self._reset_count = 0
        self.env_data = {}

    # ---------------------------
    # SAFE RESET (VERY IMPORTANT)
    # ---------------------------
    def reset(self) -> SpaceObservation:
        try:
            self._state = State(episode_id=str(uuid4()), step_count=0)
            self._reset_count += 1

            self.env_data = get_dynamic_task()

            return SpaceObservation(
                done=False,
                reward=0.0,
                power=self.env_data.get("power_available", 0),
                system_status="active",
                metadata={
                    "message": f"Reset #{self._reset_count}",
                    "state": self.env_data
                }
            )

        except Exception as e:
            # 🔥 CRITICAL: never crash reset
            return SpaceObservation(
                done=False,
                reward=0.0,
                power=0,
                system_status="error",
                metadata={"error": str(e), "state": {}}
            )

    # ---------------------------
    # SMART REWARD FUNCTION
    # ---------------------------
    def compute_reward(self, action: SpaceAction) -> float:
        try:
            # Extract percentage safely
            match = re.search(r"\d+", action.output or "")
            if not match:
                return -1.0

            allocated = int(match.group())

            correct = self.env_data.get("systems", {}).get("life_support", {}).get("required", 0)

            # ❌ Wrong action type
            if action.action != "allocate_power":
                return -1.0

            # ✅ Perfect match
            if allocated == correct:
                return 1.0

            # 🟡 Close range
            if abs(allocated - correct) <= 10:
                return 0.5

            # 🔴 Wrong
            return -1.0

        except Exception:
            return -1.0

    # ---------------------------
    # SAFE STEP FUNCTION
    # ---------------------------
    def step(self, action: SpaceAction) -> SpaceObservation:
        try:
            self._state.step_count += 1

            reward = self.compute_reward(action)

            done = True  # single-step evaluation

            return SpaceObservation(
                done=done,
                reward=reward,
                power=self.env_data.get("power_available", 0),
                system_status="emergency" if self.env_data.get("emergency") else "active",
                metadata={
                    "step": self._state.step_count,
                    "action_taken": action.action,
                    "output": action.output,
                    "state": self.env_data
                }
            )

        except Exception as e:
            # 🔥 NEVER crash step
            return SpaceObservation(
                done=True,
                reward=-1.0,
                power=0,
                system_status="error",
                metadata={"error": str(e), "state": {}}
            )

    # ---------------------------
    # STATE PROPERTY
    # ---------------------------
    @property
    def state(self) -> State:
        return self._state