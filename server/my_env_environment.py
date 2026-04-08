from uuid import uuid4

from openenv.core.env_server.interfaces import Environment
from openenv.core.env_server.types import State

try:
    from models import SpaceAction, SpaceObservation
except ImportError:
    from ..models import SpaceAction, SpaceObservation

import random
from .tasks import get_dynamic_task


class MyEnvironment(Environment):

    SUPPORTS_CONCURRENT_SESSIONS: bool = True

    def __init__(self):
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self._reset_count = 0
        self.env_data = {}

    # ---------------------------
    # RESET → INITIAL STATE
    # ---------------------------
    def reset(self) -> SpaceObservation:

        self._state = State(episode_id=str(uuid4()), step_count=0)
        self._reset_count += 1
        
        # Call the Dynamic Task Generator (No mocked data)
        self.env_data = get_dynamic_task()

        return SpaceObservation(
            done=False,
            reward=0.0,
            power=self.env_data.get("power_available", 0),
            system_status="active",
            metadata={"message": f"Global reset #{self._reset_count} | Dynamic mission loaded", "state": self.env_data}
        )

    # ---------------------------
    # REWARD FUNCTION (SMART)
    # ---------------------------
    def compute_reward(self, action):

        try:
            allocated = int(action.output.replace("%", ""))
        except:
            return -1.0

        correct = self.env_data["systems"]["life_support"]["required"]

        # ❌ Wrong action type
        if action.action != "allocate_power":
            return -1.0

        # ✅ Perfect
        if allocated == correct:
            return 1.0

        # 🟡 Partial (close)
        if abs(allocated - correct) <= 10:
            return 0.5

        # 🔴 Wrong
        return -1.0

    # ---------------------------
    # STEP FUNCTION
    # ---------------------------
    def step(self, action: SpaceAction) -> SpaceObservation:

        self._state.step_count += 1

        reward = self.compute_reward(action)

        done = True  # single-step task

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
            },
        )

    # ---------------------------
    # STATE PROPERTY
    # ---------------------------
    @property
    def state(self) -> State:
        return self._state