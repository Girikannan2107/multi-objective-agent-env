from openenv.core.env_server.types import Action, Observation
from pydantic import Field

class SpaceAction(Action):
    action_type: str = Field(..., description="Type of action to perform")
    action: str = Field(default="", description="Description of the action")
    output: str = Field(default="", description="The specific value allocated")

class SpaceObservation(Observation):
    fuel: int = Field(default=0)
    oxygen: int = Field(default=0)
    power: int = Field(default=0)
    crew_health: int = Field(default=100)
    system_status: str = Field(default="normal")