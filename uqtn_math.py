"""
UQTN mathematical branch engine for Zetari.AI.

All branches use the same immutable input snapshot and are calculated
independently. No branch feeds its result into another branch.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from math import cos, pi
from typing import Dict, Any


@dataclass(frozen=True)
class UQTNConstants:
    xi: float = 8.8596249
    mer_full: float = 314.5458074
    m_final: float = 491.4054601
    r_kerr: float = 1.5721931
    d_theta_hz: float = 4.65
    t_binding_seconds: float = 0.18594
    eta_uqtn: float = 0.691982
    a_uqtn: float = 1 / 1008
    chronon_mass: float = 8.0
    harmonic_base: float = 9.0
    consciousness_time_rate: float = 5.6
    phi: float = 1.618033988749895
    mer_simple_reference: float = 1.0355
    f_qa: float = 0.0


@dataclass(frozen=True)
class UQTNInput:
    mass: float
    energy: float
    resistance: float
    agency: float
    theta: float = 0.0
    theta_critical: float = 0.0


def calculate_branches(
    inputs: UQTNInput,
    constants: UQTNConstants | None = None,
) -> Dict[str, Any]:
    """
    Calculate all UQTN branches from one immutable input snapshot.

    The branches are parallel comparisons:
    - inverse-resistance MER
    - reciprocal-phi MER
    - standard drag MER
    - inverted-resistance MER
    - angle-dependent effective-resistance MER
    """
    constants = constants or UQTNConstants()

    resistance = max(abs(inputs.resistance), 1e-12)
    phi = constants.phi

    mer_inverse = (
        inputs.mass
        * inputs.energy
        * phi
        / resistance
    )

    mer_reciprocal_phi = (
        inputs.mass
        * inputs.energy
        / (resistance * (1 / phi))
    )

    mer_standard = (
        inputs.agency
        * (1.0 - inputs.resistance)
        * phi
    )

    mer_inverted = (
        inputs.agency
        * (1.0 + abs(inputs.resistance))
        * phi
    )

    effective_resistance = inputs.resistance * cos(
        inputs.theta - inputs.theta_critical
    )

    mer_angle = (
        inputs.agency
        * (1.0 - effective_resistance)
        * phi
    )

    return {
        "inputs": asdict(inputs),
        "constants": asdict(constants),
        "branches": {
            "inverse_resistance": mer_inverse,
            "reciprocal_phi": mer_reciprocal_phi,
            "standard_drag": mer_standard,
            "inverted_resistance": mer_inverted,
            "angle_dependent": mer_angle,
        },
        "effective_resistance": effective_resistance,
        "phi_identity_check": {
            "phi_squared": phi * phi,
            "phi_plus_one": phi + 1.0,
            "phi_minus_one": phi - 1.0,
            "one_over_phi": 1.0 / phi,
        },
    }


def classify_mer(value: float) -> str:
    """Classify one branch result for Navigator guidance."""
    if value <= 0:
        return "Navigator inactive"
    if value < 0.7:
        return "Entropic"
    if value < 1.0:
        return "Neutral"
    if value <= 1.3:
        return "Focused"
    return "Hyper-Resonant"


def classify_branches(
    result: Dict[str, Any],
) -> Dict[str, str]:
    """Return a classification for every branch."""
    return {
        name: classify_mer(value)
        for name, value in result["branches"].items()
    }


def demo() -> None:
    inputs = UQTNInput(
        mass=1.0,
        energy=0.8,
        resistance=0.2,
        agency=0.8,
    )

    result = calculate_branches(inputs)
    labels = classify_branches(result)

    print("Zetari.AI / UQTN parallel branch test")
    print("-" * 44)

    for name, value in result["branches"].items():
        print(f"{name}: {value:.6f} [{labels[name]}]")

    print(f"effective resistance: {result['effective_resistance']:.6f}")


if __name__ == "__main__":
    demo()