from models import SpaceObservation, SpaceAction

class SpaceEnv:
    def __init__(self):
        self.reset()

    def reset(self):
        self.state = SpaceObservation(
            fuel=70,
            oxygen=60,
            power=80,
            crew_health=100,
            system_status="normal"
        )
        return self.state

    def step(self, action: SpaceAction):
        act = action.action_type

        if act == "allocate_oxygen":
            self.state.oxygen += 10
        elif act == "repair_system":
            self.state.system_status = "normal"
        else:
            self.state.power += 5

        reward = 1.0
        done = True  # for quick testing

        return self.state, reward, done

    def state_fn(self):
        return self.state