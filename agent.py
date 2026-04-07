import os
from langchain_openai import ChatOpenAI


def create_llm():
    # map hackathon variables → LangChain
    os.environ["OPENAI_API_KEY"] = os.getenv("HF_TOKEN", "")
    os.environ["OPENAI_BASE_URL"] = os.getenv("API_BASE_URL", "")

    return ChatOpenAI(
        model=os.getenv("MODEL_NAME", "gpt-4o-mini"),
        temperature=0
    )


def decide_action(llm, state_dict: dict) -> str:
    prompt = f"""
You are controlling a spacecraft.

State:
{state_dict}

Actions:
- allocate_oxygen
- allocate_power
- repair_system

Rules:
- If oxygen < 40 → allocate_oxygen
- If system_status is critical → repair_system
- Otherwise → allocate_power

Return ONLY the action name.
"""

    try:
        response = llm.invoke(prompt)
        action = response.content.strip().lower()
    except Exception:
        action = "allocate_power"

    # safety fallback
    if "oxygen" in action:
        return "allocate_oxygen"
    elif "repair" in action:
        return "repair_system"
    else:
        return "allocate_power"