from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional


PHI = 1.618033988749895

app = FastAPI(title="Timescout Backend", version="1.1.0")

origins = [
    "http://localhost",
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    "http://127.0.0.1:8000",
    "http://localhost:8000",
    "https://sam-ro-27.github.io",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class StatePayload(BaseModel):
    env: float
    emo: float
    ment: float
    phys: float
    res: float
    focus: Optional[str] = ""
    notes: Optional[str] = ""


class RespondPayload(BaseModel):
    message: str
    state: StatePayload


def classify_state(state: StatePayload):
    agency = state.env + state.emo + state.ment + state.phys
    resistance = max(state.res, 0.0001)
    mer = (agency / resistance) * PHI

    if agency <= 0:
        state_name = "no_agency"
        state_label = "Navigator not active"
        advice = "No active navigation is happening yet."
    elif mer > PHI:
        state_name = "above_phi"
        state_label = "Above phi"
        advice = "You are in a coherent state for focused work."
    elif abs(mer - PHI) < 1e-6:
        state_name = "at_phi"
        state_label = "At phi threshold"
        advice = "You are right at the threshold."
    else:
        state_name = "below_phi"
        state_label = "Below phi"
        advice = "Fatigue or decoherence is more likely right now."

    return {
        "agency": agency,
        "mer": mer,
        "state": state_name,
        "stateLabel": state_label,
        "advice": advice,
    }


def infer_intent(message: str):
    text = message.lower().strip()

    if any(phrase in text for phrase in [
        "what can you do",
        "what do you do",
        "help",
        "commands",
        "anything else",
        "capabilities",
    ]):
        return "help"

    if "why" in text and "resist" in text:
        return "resistance_analysis"

    if "what changed" in text or "different" in text:
        return "change_detection"

    if "what should i do" in text or "what next" in text or "next step" in text:
        return "next_action"

    if "status" in text or "report" in text:
        return "status_report"

    if "should i" in text or "can i" in text:
        return "permission_check"

    if "study" in text or "work" in text or "focus" in text:
        return "focus_guidance"

    return "open_guidance"


def generate_reply(message: str, state: StatePayload):
    summary = classify_state(state)
    intent = infer_intent(message)

    focus_text = f" Your current focus is {state.focus}." if state.focus else ""
    notes_text = " Your notes suggest there is contextual friction in play." if state.notes else ""

    if intent == "help":
        return (
            "Here are some things I can do right now:\n"
            "- status report\n"
            "- explain resistance\n"
            "- suggest what to do next\n"
            "- check whether your current state supports focused work\n"
            "- reflect your current MER and state classification\n\n"
            "Try prompts like: 'status report', 'why is resistance high?', "
            "'what should I do next?', or 'can I focus right now?'"
        )

    if intent == "status_report":
        return (
            f"Status report:\n"
            f"Agency: {summary['agency']:.4f}\n"
            f"Resistance: {max(state.res, 0.0001):.4f}\n"
            f"Phi: {PHI:.4f}\n"
            f"MER: {summary['mer']:.4f}\n"
            f"State: {summary['stateLabel']}\n\n"
            f"{summary['advice']}{focus_text}{notes_text}"
        )

    if intent == "resistance_analysis":
        if state.res >= 0.7:
            return (
                f"Resistance is high relative to your current agency.{focus_text} "
                f"Reduce the task size and remove one blocker first."
            )
        if state.res >= 0.4:
            return (
                f"Resistance is moderate.{focus_text} "
                f"Narrow the scope and reduce switching cost."
            )
        return (
            f"Resistance is relatively low right now.{focus_text} "
            f"The issue may be less about drag and more about picking a first move."
        )

    if intent == "permission_check":
        if summary["state"] == "above_phi" and state.ment >= 0.5:
            return f"Yes. Your current state supports focused work.{focus_text}"
        if summary["state"] == "at_phi":
            return f"You can work, but use shorter focus blocks.{focus_text}"
        return f"You may want to reduce the load or recover first.{focus_text}"

    if intent == "focus_guidance":
        if summary["state"] == "above_phi" and state.ment >= 0.5:
            return f"Your state supports focused work right now.{focus_text}"
        if summary["state"] == "at_phi":
            return f"You can probably focus, but keep the work block short and bounded.{focus_text}"
        return f"Focused work may be costly right now.{focus_text} Recovery or friction reduction would be better first."

    if intent == "next_action":
        if summary["state"] == "above_phi":
            return (
                f"Your next move should be execution, not more analysis.{focus_text} "
                f"Pick one bounded task and begin."
            )
        if state.res > 0.5:
            return (
                f"Your next move should be friction reduction.{focus_text} "
                f"Remove one obstacle before pushing harder."
            )
        return (
            f"Your next move should be stabilization.{focus_text} "
            f"Recover energy, reduce noise, and reassess."
        )

    if intent == "change_detection":
        return (
            f"Change detection is not online yet in the backend memory layer.{focus_text} "
            f"The next step is wiring persistent episode comparison."
        )

    return (
        f"You are currently {summary['stateLabel'].lower()} with MER {summary['mer']:.4f}. "
        f"{summary['advice']}{focus_text}{notes_text}"
    )


@app.get("/")
async def root():
    return {
        "status": "online",
        "service": "Timescout Backend",
        "version": "1.1.0",
    }


@app.post("/api/respond")
async def respond(payload: RespondPayload):
    reply = generate_reply(payload.message, payload.state)
    summary = classify_state(payload.state)

    return {
        "mode": "backend",
        "reply": reply,
        "state": summary,
    }