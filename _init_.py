"""
Dirac Internet Central — v0.1.0.

GIVEN (user rulings):
  - Internet information is styled like a Dirac fluid.
  - Left and right hemispheres form the cognitive layer.
  - Left = analytic channel, Right = holistic channel.

INTERPRETIVE (assistant proposal, user-approved for this build):
  - Spinor split: every information packet is a two-component
    (left / right) state, after the A/B sublattice pseudospin of
    the Dirac fluid.
  - Conserved information current with a continuity ledger:
    nothing enters or leaves unaccounted.

UNRULED:
  - vortex.py is present but DORMANT. Do not wire it into the hub
    until the user rules on it.
"""

# pyright: reportMissingImports=false
# cspell:ignore Spinor sublattice pseudospin Callosum Ingestor Krimoxous Dirac

from importlib import import_module
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .api import dirac_router
    from .bridge import KrimoxousBridge
    from .central import DiracInternetCentral
    from .config import DiracConfig
    from .coupling import CorpusCallosum
    from .dirac_packet import DiracPacket
    from .fluid import DiracFluid
    from .hemisphere import Hemisphere
    from .ingest import Ingestor
    from .ledger import ContinuityLedger
    from .left_hemisphere import LeftHemisphere
    from .right_hemisphere import RightHemisphere
    from .state import fluid_state_snapshot
    from .vortex import Vortex

__version__ = "0.1.0"

_EXPORTS = {
    "DiracInternetCentral": ".central",
    "DiracConfig": ".config",
    "DiracPacket": ".dirac_packet",
    "DiracFluid": ".fluid",
    "Hemisphere": ".hemisphere",
    "LeftHemisphere": ".left_hemisphere",
    "RightHemisphere": ".right_hemisphere",
    "CorpusCallosum": ".coupling",
    "Ingestor": ".ingest",
    "ContinuityLedger": ".ledger",
    "KrimoxousBridge": ".bridge",
    "Vortex": ".vortex",
    "fluid_state_snapshot": ".state",
    "dirac_router": ".api",
}


def __getattr__(name: str) -> Any:
    if name not in _EXPORTS:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    module = import_module(_EXPORTS[name], package=__name__)
    value = getattr(module, name)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(_EXPORTS))


__all__ = [
    "DiracInternetCentral",
    "DiracConfig",
    "DiracPacket",
    "DiracFluid",
    "Hemisphere",
    "LeftHemisphere",
    "RightHemisphere",
    "CorpusCallosum",
    "Ingestor",
    "ContinuityLedger",
    "KrimoxousBridge",
    "Vortex",
    "fluid_state_snapshot",
    "dirac_router",
]
