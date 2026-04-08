from fastapi import FastAPI
from server.my_env_environment import MyEnvironment

app = FastAPI()

env = MyEnvironment()


@app.post("/reset")
def reset():
    return env.reset()


@app.post("/step")
def step(action: dict):
    return env.step(action)


def main():
    import uvicorn
    uvicorn.run("server.app:app", host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()