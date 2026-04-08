try:
    from openenv.core.env_server.http_server import create_app
except ImportError as e:
    raise ImportError(
        "openenv is required for the web interface. Install with 'pip install openenv-core'."
    ) from e

try:
    from models import SpaceAction, SpaceObservation
    from server.my_env_environment import MyEnvironment
except ImportError:
    from ..models import SpaceAction, SpaceObservation
    from .my_env_environment import MyEnvironment

# Create the app with web interface and README integration
# Using create_app ensures compatibility with OpenEnv evaluation clients
app = create_app(
    MyEnvironment,
    SpaceAction,
    SpaceObservation,
    env_name="space-mission",
    max_concurrent_envs=1,
)

def main():
    import uvicorn
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    
    uvicorn.run(app, host="0.0.0.0", port=args.port)

if __name__ == "__main__":
    main()