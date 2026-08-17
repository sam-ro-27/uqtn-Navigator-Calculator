from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from uqtn_core import NavigatorState, coherence_state
from uqtn_math import UQTNInput, calculate_branches, classify_branches
from zeta_lattice import ZetaLattice

HISTORY_FILE = Path("navigator_history.json")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class NavigatorAgent:
    """Local Zetari.AI / UQTN Navigator agent."""

    name: str = "Navigator"
    state: Optional[NavigatorState] = None
    lattice: ZetaLattice = field(default_factory=ZetaLattice.init_default)
    history: List[Dict[str, Any]] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.state is None:
            self.state = NavigatorState(
                env=0.2,
                emo=0.2,
                ment=0.2,
                phys=0.2,
                resistance=0.2,
                nav_time=0.0,
                depletion_rate=0.0,
            )

    def build_uqtn_input(self) -> UQTNInput:
        if self.state is None:
            raise RuntimeError("Navigator state is not initialized.")

        return UQTNInput(
            mass=1.0,
            energy=float(self.state.agency),
            resistance=float(self.state.resistance),
            agency=float(self.state.agency),
        )
    
    def step(self, description: str) -> Dict[str, Any]:
        if self.state is None:
            raise RuntimeError("Navigator state is not initialized.")

        navigator_mer = float(self.state.mer)
        coherence = coherence_state(navigator_mer)
        uqtn_result = calculate_branches(self.build_uqtn_input())
        branch_labels = classify_branches(uqtn_result)
        activations = self.lattice.propagate(navigator_mer)

        record: Dict[str, Any] = {
            "timestamp": utc_now(),
            "agent": self.name,
            "description": description,
            "navigator_state": {
                "env": float(self.state.env),
                "emo": float(self.state.emo),
                "ment": float(self.state.ment),
                "phys": float(self.state.phys),
                "agency": float(self.state.agency),
                "resistance": float(self.state.resistance),
                "nav_time": float(self.state.nav_time),
                "depletion_rate": float(self.state.depletion_rate),
                "mer": navigator_mer,
                "coherence_state": coherence,
            },
            "uqtn_input": uqtn_result["inputs"],
            "uqtn_constants": uqtn_result["constants"],
            "uqtn_branches": uqtn_result["branches"],
            "uqtn_branch_labels": branch_labels,
            "effective_resistance": uqtn_result["effective_resistance"],
            "phi_identity_check": uqtn_result["phi_identity_check"],
            "zeta_activations": activations,
        }

        self.history.append(record)
        return record

    def current_status(self) -> Dict[str, Any]:
        if self.state is None:
            raise RuntimeError("Navigator state is not initialized.")

        navigator_mer = float(self.state.mer)
        uqtn_result = calculate_branches(self.build_uqtn_input())

        return {
            "timestamp": utc_now(),
            "agent": self.name,
            "navigator_mer": navigator_mer,
            "coherence_state": coherence_state(navigator_mer),
            "uqtn_branches": uqtn_result["branches"],
            "branch_labels": classify_branches(uqtn_result),
            "history_count": len(self.history),
        }

    def run(self, descriptions: List[str]) -> List[Dict[str, Any]]:
        return [self.step(description) for description in descriptions]

    def clear_history(self) -> None:
        self.history.clear()

    def save_history(self, path: str | Path = HISTORY_FILE) -> Path:
        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(self.history, indent=2, ensure_ascii=False, default=str),
            encoding="utf-8",
        )
        return output_path


def build_default_agent() -> NavigatorAgent:
    default_state = NavigatorState(
        env=0.2,
        emo=0.2,
        ment=0.2,
        phys=0.2,
        resistance=0.2,
        nav_time=0.0,
        depletion_rate=0.0,
    )

    return NavigatorAgent(
        name="Navigator",
        state=default_state,
        lattice=ZetaLattice.init_default(),
    )


def main() -> None:
    agent = build_default_agent()
    record = agent.step("Integrated Zetari.AI UQTN Navigator test")
    navigator = record["navigator_state"]

    print("Zetari.AI / UQTN Navigator")
    print("-" * 36)
    print(f"Agent: {record['agent']}")
    print(f"Agency: {navigator['agency']}")
    print(f"Resistance: {navigator['resistance']}")
    print(f"Navigator MER: {navigator['mer']}")
    print(f"Coherence: {navigator['coherence_state']}")
    print("\nUQTN parallel branches:")

    for name, value in record["uqtn_branches"].items():
        label = record["uqtn_branch_labels"][name]
        print(f"{name}: {float(value):.6f} [{label}]")

    print(f"\nEffective resistance: {record['effective_resistance']:.6f}")
    print(f"Zeta activations: {record['zeta_activations']}")
    print(f"History saved to: {agent.save_history()}")


if __name__ == "__main__":
    main()
