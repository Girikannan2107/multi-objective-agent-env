from uuid import uuid4
from openenv.core.env_server.interfaces import Environment
from openenv.core.env_server.types import State

from models import SpaceAction, SpaceObservation
from server.tasks import get_dynamic_task


class MyEnvironment(Environment):

    SUPPORTS_CONCURRENT_SESSIONS: bool = True

    def __init__(self):
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self._reset_count = 0
        self.env_data = {}

    # ---------------------------
    # RESET (FIXED FOR PHASE 2)
    # ---------------------------
    def reset(self) -> SpaceObservation:
        try:
            self._state = State(episode_id=str(uuid4()), step_count=0)
            self._reset_count += 1

            self.env_data = get_dynamic_task()

            return SpaceObservation(
                done=False,
                reward=0.1,  # ✅ MUST NOT BE 0
                power=self.env_data.get("power_available", 0),
                system_status="active",
                metadata={
                    "message": f"Reset #{self._reset_count}",
                    "state": self.env_data,
                    "instruction": self.env_data.get("instruction", "")
                }
            )

        except Exception as e:
            return SpaceObservation(
                done=False,
                reward=0.1,
                power=0,
                system_status="error",
                metadata={"error": str(e), "state": {}}
            )

    # ---------------------------
    # REWARD USING TASK GRADER (PHASE 2 FIX)
    # ---------------------------
    def compute_reward(self, action: SpaceAction) -> float:

        grader = self.env_data.get("grader")

        if grader:
            try:
                return float(grader(action, self))
            except Exception:
                return 0.1

        return 0.1

    # ---------------------------
    # STEP FUNCTION
    # ---------------------------
    def step(self, action: SpaceAction) -> SpaceObservation:
        try:
            self._state.step_count += 1

            reward = self.compute_reward(action)

            return SpaceObservation(
                done=True,
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
            return SpaceObservation(
                done=True,
                reward=0.1,
                power=0,
                system_status="error",
                metadata={"error": str(e), "state": {}}
            )

    # ---------------------------
    # STATE
    # ---------------------------
    @property
    def state(self) -> State:
        return self._state