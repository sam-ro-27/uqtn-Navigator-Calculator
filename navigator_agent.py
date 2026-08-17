# navigator_agent.py
"""
Zetari.AI / UQTN Navigator agent.

Connects:
- uqtn_core.NavigatorState
- uqtn_core.coherence_state
- zeta_lattice.ZetaLattice
- state history
- optional project registry
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from uqtn_core import NavigatorState, coherence_state
from zeta_lattice import ZetaLattice


def utc_now() -> str:
    """Return a UTC timestamp suitable for history records."""
    return datetime.now(timezone.utc).isoformat()


@dataclass
class NavigatorAgent:
    """Local UQTN navigation and zeta-lattice agent."""

    name: str = "Navigator"
    state: Optional[NavigatorState] = None
    lattice: ZetaLattice = field(default_factory=ZetaLattice.init_default)
    history: List[Dict[str, Any]] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Create a default state when none is supplied."""
        if self.state is None:
            self.state = NavigatorState()

    def step(self, description: str) -> Dict[str, Any]:
        """
        Perform one local navigation/computation step.

        The same current state is used for:
        - MER calculation
        - coherence classification
        - zeta-lattice propagation
        - history recording
        """
        if self.state is None:
            raise RuntimeError("Navigator state has not been initialized.")

        mer = float(self.state.mer)
        state_label = coherence_state(mer)
        activations = self.lattice.propagate(mer)

        record: Dict[str, Any] = {
            "timestamp": utc_now(),
            "agent": self.name,
            "description": description,
            "agency": float(self.state.agency),
            "resistance": float(self.state.resistance),
            "mer": mer,
            "coherence_state": state_label,
            "zeta_activations": activations,
        }

        self.history.append(record)
        return record

    def current_status(self) -> Dict[str, Any]:
        """Return the current state without propagating the lattice."""
        if self.state is None:
            raise RuntimeError("Navigator state has not been initialized.")

        mer = float(self.state.mer)

        return {
            "timestamp": utc_now(),
            "agent": self.name,
            "agency": float(self.state.agency),
            "resistance": float(self.state.resistance),
            "mer": mer,
            "coherence_state": coherence_state(mer),
            "history_count": len(self.history),
        }

    def run(self, descriptions: List[str]) -> List[Dict[str, Any]]:
        """Run multiple navigation steps."""
        return [self.step(description) for description in descriptions]

    def clear_history(self) -> None:
        """Clear only the in-memory history."""
        self.history.clear()

    def export_history(self, path: str | Path) -> Path:
        """Save agent history as readable JSON."""
        import json

        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(self.history, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        return output_path


def build_default_agent() -> NavigatorAgent:
    """Create the default Zetari.AI UQTN Navigator."""
    return NavigatorAgent(
        name="Navigator",
        state=NavigatorState(),
        lattice=ZetaLattice.init_default(),
    )


def main() -> None:
    """Run a local smoke test."""
    agent = build_default_agent()

    record = agent.step(
        "Initial Zetari.AI UQTN navigation and zeta-lattice test"
    )

    print("Zetari.AI / UQTN Navigator")
    print("-" * 30)
    print(f"Agent: {record['agent']}")
    print(f"Agency: {record['agency']}")
    print(f"Resistance: {record['resistance']}")
    print(f"MER: {record['mer']}")
    print(f"Coherence: {record['coherence_state']}")
    print(f"Zeta activations: {record['zeta_activations']}")


if __name__ == "__main__":
    main()