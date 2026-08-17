# navigator_agent.py

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from uqtn_core import NavigatorState, coherence_state
from zeta_lattice import ZetaLattice


HISTORY_FILE = Path("navigator_history.json")


def utc_now() -> str:
    """Return an ISO-8601 UTC timestamp."""
    return datetime.now(timezone.utc).isoformat()


@dataclass
class NavigatorAgent:
    """Local Zetari.AI / UQTN Navigator agent."""

    name: str = "Navigator"
    state: Optional[NavigatorState] = None
    lattice: ZetaLattice = field(
        default_factory=ZetaLattice.init_default
    )
    history: List[Dict[str, Any]] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Create a valid default NavigatorState when needed."""
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

    def step(self, description: str) -> Dict[str, Any]:
        """
        Perform one local navigation/computation step.

        The same state snapshot is used for:
        - MER calculation
        - coherence classification
        - zeta-lattice propagation
        - history recording
        """
        if self.state is None:
            raise RuntimeError("Navigator state is not initialized.")

        mer = float(self.state.mer)
        state_label = coherence_state(mer)
        activations = self.lattice.propagate(mer)

        record: Dict[str, Any] = {
            "timestamp": utc_now(),
            "agent": self.name,
            "description": description,
            "env": float(self.state.env),
            "emo": float(self.state.emo),
            "ment": float(self.state.ment),
            "phys": float(self.state.phys),
            "agency": float(self.state.agency),
            "resistance": float(self.state.resistance),
            "nav_time": float(self.state.nav_time),
            "depletion_rate": float(self.state.depletion_rate),
            "mer": mer,
            "coherence_state": state_label,
            "zeta_activations": activations,
        }

        self.history.append(record)
        return record

    def current_status(self) -> Dict[str, Any]:
        """Return the current state without propagating the lattice."""
        if self.state is None:
            raise RuntimeError("Navigator state is not initialized.")

        mer = float(self.state.mer)

        return {
            "timestamp": utc_now(),
            "agent": self.name,
            "env": float(self.state.env),
            "emo": float(self.state.emo),
            "ment": float(self.state.ment),
            "phys": float(self.state.phys),
            "agency": float(self.state.agency),
            "resistance": float(self.state.resistance),
            "nav_time": float(self.state.nav_time),
            "depletion_rate": float(self.state.depletion_rate),
            "mer": mer,
            "coherence_state": coherence_state(mer),
            "history_count": len(self.history),
        }

    def run(self, descriptions: List[str]) -> List[Dict[str, Any]]:
        """Run multiple navigation steps."""
        return [self.step(description) for description in descriptions]

    def clear_history(self) -> None:
        """Clear the in-memory navigation history."""
        self.history.clear()

    def save_history(
        self,
        path: str | Path = HISTORY_FILE,
    ) -> Path:
        """Save navigation history to a JSON file."""
        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        output_path.write_text(
            json.dumps(
                self.history,
                indent=2,
                ensure_ascii=False,
                default=str,
            ),
            encoding="utf-8",
        )

        return output_path


def build_default_agent() -> NavigatorAgent:
    """Build a default Zetari.AI UQTN Navigator."""
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
    """Run a local Navigator smoke test."""
    agent = build_default_agent()

    record = agent.step(
        "Initial Zetari.AI UQTN Navigator test"
    )

    print("Zetari.AI / UQTN Navigator")
    print("-" * 32)
    print(f"Agent: {record['agent']}")
    print(f"Environmental energy: {record['env']}")
    print(f"Emotional energy: {record['emo']}")
    print(f"Mental energy: {record['ment']}")
    print(f"Physical energy: {record['phys']}")
    print(f"Agency: {record['agency']}")
    print(f"Resistance: {record['resistance']}")
    print(f"Navigation time: {record['nav_time']}")
    print(f"Depletion rate: {record['depletion_rate']}")
    print(f"MER: {record['mer']}")
    print(f"Coherence: {record['coherence_state']}")
    print(f"Zeta activations: {record['zeta_activations']}")

    history_path = agent.save_history()
    print(f"History saved to: {history_path}")


if __name__ == "__main__":
    main()