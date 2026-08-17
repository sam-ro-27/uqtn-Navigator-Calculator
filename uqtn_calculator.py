# uqtn_calculator.py
"""
Zetari.AI / UQTN Calculator

Provides:
- reusable calculation functions
- parallel UQTN MER branches
- Navigator coherence classification
- optional interactive terminal mode

The calculator can be imported by:
- navigator_agent.py
- api_server.py
- tests
- command-line use
"""

from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict

from uqtn_core import PHI, NavigatorState, coherence_state
from uqtn_math import (
    UQTNInput,
    calculate_branches,
    classify_branches,
)


def calculate_navigator_state(
    env: float,
    emo: float,
    ment: float,
    phys: float,
    resistance: float,
    nav_time: float = 0.0,
    depletion_rate: float = 0.0,
) -> Dict[str, Any]:
    """
    Calculate a complete Navigator state.

    This function is reusable by the terminal calculator,
    API server, Navigator agent, and tests.
    """
    state = NavigatorState(
        env=env,
        emo=emo,
        ment=ment,
        phys=phys,
        resistance=resistance,
        nav_time=nav_time,
        depletion_rate=depletion_rate,
    )

    uqtn_input = UQTNInput(
        mass=1.0,
        energy=state.agency,
        resistance=state.resistance,
        agency=state.agency,
    )

    branch_result = calculate_branches(uqtn_input)
    branch_labels = classify_branches(branch_result)

    return {
        "navigator_state": state.to_dict(),
        "coherence_state": coherence_state(state.mer),
        "uqtn_input": branch_result["inputs"],
        "uqtn_constants": branch_result["constants"],
        "uqtn_branches": branch_result["branches"],
        "uqtn_branch_labels": branch_labels,
        "effective_resistance": branch_result[
            "effective_resistance"
        ],
        "phi_identity_check": branch_result[
            "phi_identity_check"
        ],
    }


def print_results(result: Dict[str, Any]) -> None:
    """Print a complete formatted calculation result."""
    state = result["navigator_state"]
    branches = result["uqtn_branches"]
    labels = result["uqtn_branch_labels"]

    print("\nRESULTS")
    print("=======")

    print(f"Agency: {state['agency']:.6f}")
    print(f"Resistance: {state['resistance']:.6f}")
    print(f"Phi: {PHI:.15f}")
    print(f"Navigator MER: {state['mer']:.6f}")
    print(f"Coherence: {result['coherence_state']}")

    print("\nPARALLEL UQTN BRANCHES")
    print("======================")

    for name, value in branches.items():
        print(
            f"{name}: "
            f"{float(value):.6f} "
            f"[{labels[name]}]"
        )

    print("\nEFFECTIVE RESISTANCE")
    print("====================")
    print(
        f"{result['effective_resistance']:.6f}"
    )


def read_float(prompt: str, minimum: float | None = None) -> float:
    """Read and validate one numeric terminal value."""
    while True:
        try:
            value = float(input(prompt))

            if minimum is not None and value < minimum:
                print(
                    f"Enter a value greater than or equal to {minimum}."
                )
                continue

            return value

        except ValueError:
            print("Please enter a valid number.")


def interactive_calculator() -> None:
    """Run the original interactive calculator style."""
    print("ZETARI.AI / UQTN NAVIGATOR CALCULATOR")
    print("=====================================")
    print("Enter energy domains on a 0–1 scale.")

    env = read_float(
        "Environmental energy: ",
        minimum=0.0,
    )

    emo = read_float(
        "Emotional energy: ",
        minimum=0.0,
    )

    ment = read_float(
        "Mental energy: ",
        minimum=0.0,
    )

    phys = read_float(
        "Physical energy: ",
        minimum=0.0,
    )

    resistance = read_float(
        "Resistance R: ",
        minimum=0.0001,
    )

    nav_time = read_float(
        "Navigation time [default 0]: ",
        minimum=0.0,
    )

    depletion_rate = read_float(
        "Depletion rate [default 0]: ",
        minimum=0.0,
    )

    result = calculate_navigator_state(
        env=env,
        emo=emo,
        ment=ment,
        phys=phys,
        resistance=resistance,
        nav_time=nav_time,
        depletion_rate=depletion_rate,
    )

    print_results(result)


def demo() -> None:
    """Run a non-interactive smoke test."""
    result = calculate_navigator_state(
        env=0.2,
        emo=0.2,
        ment=0.2,
        phys=0.2,
        resistance=0.2,
    )

    print_results(result)


if __name__ == "__main__":
    interactive_calculator()