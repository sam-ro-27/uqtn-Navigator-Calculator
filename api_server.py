# api_server.py

from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from uqtn_math import (
    UQTNInput,
    calculate_branches,
    classify_branches,
)


PHI = 1.618033988749895


app = FastAPI(
    title="Zetari.AI Local UQTN Navigator",
    version="2.0.0",
)


# Local development and GitHub Pages origins.
# No cloud API is used by this server.
ALLOWED_ORIGINS = [
    "http://localhost",
    "http://localhost:5500",
    "http://localhost:8000",
    "http://127.0.0.1:5500",
    "http://127.0.0.1:8000",
    "https://sam-ro-27.github.io",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


class StatePayload(BaseModel):
    """State submitted by the browser interface."""

    env: float = Field(default=0.2, ge=0.0, le=1.0)
    emo: float = Field(default=0.2, ge=0.0, le=1.0)
    ment: float = Field(default=0.2, ge=0.0, le=1.0)
    phys: float = Field(default=0.2, ge=0.0, le=1.0)
    res: float = Field(default=0.2, ge=0.0001, le=1.0)

    mass: float = Field(default=1.0, ge=0.0)
    energy: Optional[float] = Field(default=None, ge=0.0)

    theta: float = 0.0
    theta_critical: float = 0.0

    focus: str = ""
    notes: str = ""
    task_type: str = "general"


class RespondPayload(BaseModel):
    """Message and current browser state."""

    message: str
    state: StatePayload


def classify_navigator_state(
    agency: float,
    resistance: float,
    mer: float,
) -> Dict[str, str]:
    """Classify the current Navigator state."""
    if agency <= 0:
        return {
            "state": "no_agency",
            "stateLabel": "Navigator not active",
            "advice": "No active navigation is happening yet.",
        }

    if mer > PHI:
        return {
            "state": "above_phi",
            "stateLabel": "Above phi",
            "advice": "Your current state supports focused work.",
        }

    if abs(mer - PHI) < 1e-6:
        return {
            "state": "at_phi",
            "stateLabel": "At phi threshold",
            "advice": "You are right at the coherence threshold.",
        }

    return {
        "state": "below_phi",
        "stateLabel": "Below phi",
        "advice": (
            "Resistance is currently dominant. "
            "Consider reducing load or taking a short break."
        ),
    }


def calculate_state(
    state: StatePayload,
) -> Dict[str, Any]:
    """Calculate Navigator state and all UQTN branches."""
    agency = (
        state.env
        + state.emo
        + state.ment
        + state.phys
    )

    resistance = max(state.res, 0.0001)

    navigator_mer = (
        agency / resistance
    ) * PHI

    energy = (
        state.energy
        if state.energy is not None
        else agency
    )

    uqtn_input = UQTNInput(
        mass=state.mass,
        energy=energy,
        resistance=resistance,
        agency=agency,
        theta=state.theta,
        theta_critical=state.theta_critical,
    )

    branch_result = calculate_branches(uqtn_input)
    branch_labels = classify_branches(branch_result)
    classification = classify_navigator_state(
        agency=agency,
        resistance=resistance,
        mer=navigator_mer,
    )

    return {
        "env": state.env,
        "emo": state.emo,
        "ment": state.ment,
        "phys": state.phys,
        "resistance": resistance,
        "mass": state.mass,
        "energy": energy,
        "agency": agency,
        "navigator_mer": navigator_mer,
        "phi": PHI,
        "task_type": state.task_type,
        "focus": state.focus,
        "notes": state.notes,
        "theta": state.theta,
        "theta_critical": state.theta_critical,
        "state": classification["state"],
        "stateLabel": classification["stateLabel"],
        "advice": classification["advice"],
        "uqtn_input": branch_result["inputs"],
        "uqtn_branches": branch_result["branches"],
        "uqtn_branch_labels": branch_labels,
        "effective_resistance": branch_result[
            "effective_resistance"
        ],
        "phi_identity_check": branch_result[
            "phi_identity_check"
        ],
    }


def infer_intent(message: str) -> str:
    """Classify common local Navigator intents."""
    text = message.lower().strip()

    if any(
        phrase in text
        for phrase in (
            "what can you do",
            "what do you do",
            "help",
            "commands",
            "capabilities",
        )
    ):
        return "help"

    if "why" in text and "resist" in text:
        return "resistance_analysis"

    if (
        "what changed" in text
        or "different" in text
    ):
        return "change_detection"

    if (
        "what should i do" in text
        or "what next" in text
        or "next step" in text
    ):
        return "next_action"

    if (
        "status" in text
        or "report" in text
        or "operational" in text
    ):
        return "status_report"

    if (
        "should i" in text
        or "can i" in text
        or "am i able" in text
    ):
        return "permission_check"

    if any(
        word in text
        for word in (
            "study",
            "work",
            "focus",
            "coding",
            "writing",
            "physics",
        )
    ):
        return "focus_guidance"

    return "open_guidance"


def generate_reply(
    message: str,
    payload_state: StatePayload,
    summary: Dict[str, Any],
) -> str:
    """Generate a deterministic local Navigator response."""
    intent = infer_intent(message)

    focus_text = (
        f" Current focus: {payload_state.focus}."
        if payload_state.focus
        else ""
    )

    task_text = (
        f" Task type: {payload_state.task_type}."
        if payload_state.task_type
        else ""
    )

    if intent == "help":
        return (
            "Zetari.AI is running as a local UQTN Navigator.\n\n"
            "I can:\n"
            "- calculate Navigator state\n"
            "- calculate parallel UQTN MER branches\n"
            "- explain resistance\n"
            "- suggest the next action\n"
            "- assess focused-work readiness\n"
            "- report zeta and MER state when connected\n\n"
            "Try: status report, why is resistance high?, "
            "what should I do next?, or can I focus right now?"
        )

    if intent == "status_report":
        return (
            "Zetari.AI status report:\n"
            f"Agency: {summary['agency']:.4f}\n"
            f"Resistance: {summary['resistance']:.4f}\n"
            f"Navigator MER: {summary['navigator_mer']:.4f}\n"
            f"MER base: "
            f"{summary['uqtn_branches']['inverse_resistance']:.4f}\n"
            f"MER × phi: "
            f"{summary['uqtn_branches']['standard_drag']:.4f}\n"
            f"MER ÷ phi: "
            f"{summary['uqtn_branches']['reciprocal_phi']:.4f}\n"
            f"State: {summary['stateLabel']}\n\n"
            f"{summary['advice']}{focus_text}{task_text}"
        )

    if intent == "resistance_analysis":
        resistance = summary["resistance"]

        if resistance >= 0.7:
            return (
                "Resistance is high relative to current agency. "
                "Reduce task size and remove one blocker first."
                f"{focus_text}{task_text}"
            )

        if resistance >= 0.4:
            return (
                "Resistance is moderate. Narrow the scope and "
                "reduce switching cost."
                f"{focus_text}{task_text}"
            )

        return (
            "Resistance is relatively low. The next challenge may "
            "be selecting a clear first move."
            f"{focus_text}{task_text}"
        )

    if intent == "permission_check":
        if (
            summary["state"] == "above_phi"
            and summary["ment"] >= 0.5
        ):
            return (
                "Yes. Your current state supports focused work."
                f"{focus_text}{task_text}"
            )

        if summary["state"] == "at_phi":
            return (
                "You can work, but use a short, bounded block."
                f"{focus_text}{task_text}"
            )

        return (
            "Reduce the load or recover before starting demanding work."
            f"{focus_text}{task_text}"
        )

    if intent == "focus_guidance":
        if summary["state"] == "above_phi":
            return (
                "Your state supports focused work. Choose one bounded "
                "task and begin."
                f"{focus_text}{task_text}"
            )

        if summary["state"] == "at_phi":
            return (
                "Use a short planning or focus block and reassess."
                f"{focus_text}{task_text}"
            )

        return (
            "Focused work may be costly right now. Reduce friction or "
            "take a short recovery period first."
            f"{focus_text}{task_text}"
        )

    if intent == "next_action":
        if summary["state"] == "above_phi":
            return (
                "Your next move should be execution. Pick one bounded "
                "task and begin."
                f"{focus_text}{task_text}"
            )

        if summary["resistance"] > 0.5:
            return (
                "Your next move should be friction reduction. Remove "
                "one obstacle before pushing harder."
                f"{focus_text}{task_text}"
            )

        return (
            "Your next move should be stabilization. Reduce noise, "
            "recover energy, and reassess."
            f"{focus_text}{task_text}"
        )

    if intent == "change_detection":
        return (
            "Change detection is not yet connected to persistent "
            "episode history. The current state has been calculated "
            "from this request."
            f"{focus_text}{task_text}"
        )

    return (
        f"Zetari.AI interpreted the request locally. "
        f"Current state: {summary['stateLabel']}. "
        f"Navigator MER: {summary['navigator_mer']:.4f}. "
        f"{summary['advice']}{focus_text}{task_text}"
    )


@app.get("/")
async def root() -> Dict[str, str]:
    """Service health endpoint."""
    return {
        "status": "online",
        "service": "Zetari.AI Local UQTN Navigator",
        "version": "2.0.0",
        "mode": "local",
    }


@app.get("/health")
async def health() -> Dict[str, str]:
    """Simple health check."""
    return {
        "status": "healthy",
        "service": "Zetari.AI",
    }


@app.post("/api/respond")
async def respond(
    payload: RespondPayload,
) -> Dict[str, Any]:
    """Process a browser message through the local Navigator engine."""
    summary = calculate_state(payload.state)
    reply = generate_reply(
        message=payload.message,
        payload_state=payload.state,
        summary=summary,
    )

    return {
        "mode": "local_backend",
        "reply": reply,
        "state": summary,
    }

def main() -> None:
    """Start the local Zetari.AI API server."""
    import uvicorn

    uvicorn.run(
        "api_server:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
    )


if __name__ == "__main__":
    main()