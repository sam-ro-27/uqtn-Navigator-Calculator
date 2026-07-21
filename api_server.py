# api_server.py

from fastapi import FastAPI
from pydantic import BaseModel
from navigator_agent import NavigatorAgent
from uqtn_core import NavigatorState

app = FastAPI()

class InputPayload(BaseModel):
    env: float
    emo: float
    ment: float
    phys: float
    resistance: float
    nav_time: float
    depletion_rate: float
    description: str

@app.post("/uqtn/step")
def uqtn_step(payload: InputPayload):
    state = NavigatorState(
        env=payload.env,
        emo=payload.emo,
        ment=payload.ment,
        phys=payload.phys,
        resistance=payload.resistance,
        nav_time=payload.nav_time,
        depletion_rate=payload.depletion_rate,
    )
    agent = NavigatorAgent(name="Navigator", state=state)
    record = agent.step(description=payload.description)
    return record