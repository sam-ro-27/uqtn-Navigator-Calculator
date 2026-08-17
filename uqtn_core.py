# uqtn_core.py
"""
Core Navigator state model for Zetari.AI / UQTN.

This module provides:
- NavigatorState
- Agency calculation
- Navigator MER calculation
- navigation-time calculation
- coherence classification

Parallel UQTN MER branches are calculated separately in uqtn_math.py.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from math import isclose
from typing import Any, Dict


PHI = 1.618033988749895
CONSCIOUSNESS_RATE = 5.6
MIN_RESISTANCE = 1e-4


@dataclass
class NavigatorState:
    """
    Current local Navigator state.

    Energy values are normalized to the range 0.0–1.0.
    Resistance is constrained to a minimum positive value.
    """

    env: float = 0.2
    emo: float = 0.2
    ment: float = 0.2
    phys: float = 0.2
    resistance: float = 0.2
    nav_time: float = 0.0
    depletion_rate: float = 0.0

    def __post_init__(self) -> None:
        """Normalize and validate state values."""
        self.env = self._clamp(self.env)
        self.emo = self._clamp(self.emo)
        self.ment = self._clamp(self.ment)
        self.phys = self._clamp(self.phys)
        self.resistance = max(
            float(self.resistance),
            MIN_RESISTANCE,
        )
        self.nav_time = max(float(self.nav_time), 0.0)
        self.depletion_rate = max(
            float(self.depletion_rate),
            0.0,
        )

    @staticmethod
    def _clamp(value: float) -> float:
        """Clamp an energy value to the normalized range."""
        return min(1.0, max(0.0, float(value)))

    @property
    def agency(self) -> float:
        """Calculate raw agency from the four state dimensions."""
        return (
            self.env
            + self.emo
            + self.ment
            + self.phys
        )

    @property
    def mer(self) -> float:
        """
        Calculate the Navigator MER used by the core state engine.

        MER = (Agency / Resistance) × φ
        """
        resistance = max(
            self.resistance,
            MIN_RESISTANCE,
        )

        return (self.agency / resistance) * PHI

    @property
    def ea_time(self) -> float:
        """
        Return the current generated navigation time.

        The current implementation treats nav_time as the
        accumulated local navigation time.
        """
        return self.nav_time

    @property
    def effective_time_rate(self) -> float:
        """Return navigation time scaled by the locked rate."""
        return self.nav_time * CONSCIOUSNESS_RATE

    def advance_time(self, seconds: float) -> None:
        """Advance navigation time and apply depletion."""
        seconds = max(float(seconds), 0.0)

        self.nav_time += seconds

        depletion = self.depletion_rate * seconds

        self.ment = self._clamp(self.ment - depletion)
        self.phys = self._clamp(self.phys - depletion)

    def update(
        self,
        *,
        env: float | None = None,
        emo: float | None = None,
        ment: float | None = None,
        phys: float | None = None,
        resistance: float | None = None,
        nav_time: float | None = None,
        depletion_rate: float | None = None,
    ) -> None:
        """Update only supplied state values."""
        if env is not None:
            self.env = self._clamp(env)

        if emo is not None:
            self.emo = self._clamp(emo)

        if ment is not None:
            self.ment = self._clamp(ment)

        if phys is not None:
            self.phys = self._clamp(phys)

        if resistance is not None:
            self.resistance = max(
                float(resistance),
                MIN_RESISTANCE,
            )

        if nav_time is not None:
            self.nav_time = max(float(nav_time), 0.0)

        if depletion_rate is not None:
            self.depletion_rate = max(
                float(depletion_rate),
                0.0,
            )

    def copy(self) -> "NavigatorState":
        """Return an independent state snapshot."""
        return replace(self)

    def to_dict(self) -> Dict[str, float]:
        """Export the state and calculated values as a dictionary."""
        return {
            "env": self.env,
            "emo": self.emo,
            "ment": self.ment,
            "phys": self.phys,
            "resistance": self.resistance,
            "nav_time": self.nav_time,
            "depletion_rate": self.depletion_rate,
            "agency": self.agency,
            "mer": self.mer,
            "ea_time": self.ea_time,
            "effective_time_rate": self.effective_time_rate,
        }


def coherence_state(
    mer: float,
    phi: float = PHI,
) -> str:
    """
    Classify Navigator coherence from MER.

    Threshold behavior:
    - MER <= 0: inactive
    - MER > phi: coherent navigation
    - MER ~= phi: critical threshold
    - MER < phi: fatigue/decoherence
    """
    mer = float(mer)
    phi = float(phi)

    if mer <= 0:
        return "no_agency: navigator not active"

    if mer > phi:
        return "above_phi: coherent navigation (keep going)"

    if isclose(
        mer,
        phi,
        rel_tol=1e-6,
        abs_tol=1e-6,
    ):
        return (
            "at_phi: critical threshold "
            "(minimum viable momentum)"
        )

    return (
        "below_phi: decoherence + fatigue "
        "(delegate or rest)"
    )


def build_default_state() -> NavigatorState:
    """Create the default Zetari.AI Navigator state."""
    return NavigatorState()


def main() -> None:
    """Run a core Navigator state smoke test."""
    state = build_default_state()

    print("Zetari.AI / UQTN Core")
    print("-" * 26)
    print(f"Agency: {state.agency:.6f}")
    print(f"Resistance: {state.resistance:.6f}")
    print(f"MER: {state.mer:.6f}")
    print(f"Coherence: {coherence_state(state.mer)}")
    print(f"Navigation time: {state.nav_time:.6f}")
    print(f"Consciousness-time rate: {CONSCIOUSNESS_RATE}")
    print(f"State dictionary: {state.to_dict()}")


if __name__ == "__main__":
    main()