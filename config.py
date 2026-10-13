"""
config.py — Dirac Internet Central configuration.

Every value overridable by environment variable, in the same style as
the Krimoxous backend (KRIMOXOUS_MODEL / KRIMOXOUS_VISION_MODEL).
"""

import os
from dataclasses import dataclass, field


def _env(name, default):
    return os.getenv(name, default)


@dataclass
class DiracConfig:
    """Tunable parameters for the hub. All GIVEN defaults, all overridable."""

    # Hemisphere models (GIVEN: left = analytic, right = holistic)
    left_model: str = field(
        default_factory=lambda: _env("DIRAC_LEFT_MODEL", "llama3.2:latest")
    )
    right_model: str = field(
        default_factory=lambda: _env("DIRAC_RIGHT_MODEL", "llava")
    )

    # Fluid parameters (INTERPRETIVE)
    max_packets: int = field(
        default_factory=lambda: int(_env("DIRAC_MAX_PACKETS", "1000"))
    )
    viscosity: float = field(
        default_factory=lambda: float(_env("DIRAC_VISCOSITY", "0.5"))
    )

    # Coupling (corpus callosum) bandwidth: how much cross-talk per cycle
    coupling_bandwidth: int = field(
        default_factory=lambda: int(_env("DIRAC_COUPLING_BANDWIDTH", "10"))
    )

    # Confirm mode (user GIVEN for the live test): hemispheres call real
    # models instead of local heuristics. "1" = live, "0" = fast scaffolding.
    confirm_mode: bool = field(
        default_factory=lambda: _env("DIRAC_CONFIRM_MODE", "1") == "1"
    )
    ollama_url: str = field(
        default_factory=lambda: _env(
            "DIRAC_OLLAMA_URL", "http://127.0.0.1:11434/api/generate")
    )

    # Krimoxous backend bridge
    backend_url: str = field(
        default_factory=lambda: _env("DIRAC_BACKEND_URL", "http://127.0.0.1:8000")
    )

    # Vortex module stays dormant until the user rules on it
    vortex_enabled: bool = field(
        default_factory=lambda: _env("DIRAC_VORTEX", "0") == "1"
    )
def main():
    # Example usage of DiracConfig class
    config = DiracConfig()
    print("Dirac Internet Central Configuration:")
    print(f"Left Hemisphere Model: {config.left_model}")
    print(f"Right Hemisphere Model: {config.right_model}")
    print(f"Max Packets: {config.max_packets}")
    print(f"Viscosity: {config.viscosity}")
    print(f"Coupling Bandwidth: {config.coupling_bandwidth}")
    print(f"Confirm Mode: {config.confirm_mode}")
    print(f"Ollama URL: {config.ollama_url}")
    print(f"Backend URL: {config.backend_url}")
    print(f"Vortex Enabled: {config.vortex_enabled}")

if __name__ == "__main__":
    main()