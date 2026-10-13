"""
central.py — Dirac Internet Central: the hub itself.

GIVEN:
  - Internet information styled like a Dirac fluid.
  - Left and right hemispheres form the cognitive layer.

This is where everything meets: ingest -> fluid -> hemispheres ->
coupling -> ledger. One spacious room with the whole works.
"""

from typing import Any

try:
    from .config import DiracConfig as _DiracConfig
    from .coupling import CorpusCallosum as _Corpus_Callosum
    from .fluid import DiracFluid as _Dirac_Fluid
    from .ingest import Ingestor as _Ingest
    from .left_hemisphere import LeftHemisphere as _Left_Hemisphere
    from .right_hemisphere import RightHemisphere as Right_Hemisphere
except ImportError:  # pragma: no cover - fallback for direct/script execution
    class _FallbackDiracConfig:
        def __init__(self, **kwargs):
            self.max_packets = kwargs.get("max_packets", 32)
            self.viscosity = kwargs.get("viscosity", 0.7)
            self.left_model = kwargs.get("left_model", "default")
            self.right_model = kwargs.get("right_model", "default")
            self.confirm_mode = kwargs.get("confirm_mode", False)
            self.ollama_url = kwargs.get("ollama_url", None)
            self.coupling_bandwidth = kwargs.get("coupling_bandwidth", 1.0)

    _DiracConfig = _FallbackDiracConfig

    class _DiracPacket:
        def __init__(self, packet_id: Any, left: Any, right: Any, payload: Any):
            self.id = packet_id
            self.left = left
            self.right = right
            self._payload = payload

        def to_dict(self):
            if isinstance(self._payload, dict):
                return self._payload
            return {"id": self.id, "left": self.left, "right": self.right}

    class _Ingestor:
        def ingest(self, raw):
            packet = raw
            if hasattr(packet, "left") and hasattr(packet, "right") and hasattr(packet, "id"):
                return packet
            if isinstance(packet, dict):
                return _DiracPacket(
                    packet_id=id(packet),
                    left=packet.get("left", packet.get("text", packet)),
                    right=packet.get("right", packet.get("image", packet)),
                    payload=packet,
                )
            return _DiracPacket(packet_id=id(packet), left=packet, right=packet, payload={"value": packet})

        def stats(self):
            return {"type": "fallback"}

    class _DiracFluid:
        def __init__(self, **kwargs):
            self.max_packets = kwargs.get("max_packets", 32)
            self.viscosity = kwargs.get("viscosity", 0.7)
            self._ledger = []

        def enter(self, packet):
            self._ledger.append({"in": packet})

        def leave(self, packet_id, fused):
            self._ledger.append({"id": packet_id, "out": fused})

        def continuity_holds(self):
            return True

        def stats(self):
            return {"max_packets": self.max_packets, "viscosity": self.viscosity}

    class _LeftHemisphere:
        def __init__(self, **kwargs):
            self.model = kwargs.get("model")
            self.confirm_mode = kwargs.get("confirm_mode", False)
            self.ollama_url = kwargs.get("ollama_url")

        def process(self, payload):
            return payload

        def stats(self):
            return {"model": self.model, "confirm_mode": self.confirm_mode}

    class _RightHemisphere(_LeftHemisphere):
        pass

    class _CorpusCallosum:
        def __init__(self, **kwargs):
            self.bandwidth = kwargs.get("bandwidth", 1.0)

        def exchange(self, left_result, right_result):
            return {"left": left_result, "right": right_result, "bandwidth": self.bandwidth}

        def stats(self):
            return {"bandwidth": self.bandwidth}

DiracConfig = _DiracConfig
Ingestor = _Ingestor
DiracFluid = _DiracFluid
LeftHemisphere = _LeftHemisphere
RightHemisphere = _RightHemisphere
CorpusCallosum = _CorpusCallosum


class DiracInternetCentral:
    """
    The central hub.

    Flow of one cycle:
      1. ingestor   splits raw internet info into a DiracPacket
      2. fluid      admits the packet (continuity: recorded in)
      3. left       processes the analytic component
      4. right      processes the holistic component
      5. coupling   fuses the two readings (corpus callosum)
      6. fluid      releases the packet (continuity: recorded out)

    The vortex module is NOT wired here — UNRULED, dormant.
    """

    def __init__(self, config=None):
        self.config = config or DiracConfig()
        self.ingestor = Ingestor()
        self.fluid = DiracFluid(
            max_packets=self.config.max_packets,
            viscosity=self.config.viscosity,
        )
        self.left = LeftHemisphere(
            model=self.config.left_model,
            confirm_mode=self.config.confirm_mode,
            ollama_url=self.config.ollama_url,
        )
        self.right = RightHemisphere(
            model=self.config.right_model,
            confirm_mode=self.config.confirm_mode,
            ollama_url=self.config.ollama_url,
        )
        self.coupling = CorpusCallosum(
            bandwidth=self.config.coupling_bandwidth
        )
        self.cycles = 0

    # ------------------------------------------------------------------
    # The cycle
    # ------------------------------------------------------------------

    def cycle(self, raw):
        """
        Run one full hub cycle on a raw internet payload.
        Returns the fused whole-mind reading.
        """
        packet = self.ingestor.ingest(raw)
        self.fluid.enter(packet)

        left_result = self.left.process(packet.left)
        right_result = self.right.process(packet.right)

        fused = self.coupling.exchange(left_result, right_result)

        self.fluid.leave(packet.id, fused)
        self.cycles += 1

        return {
            "packet": packet.to_dict(),
            "fused": fused,
            "continuity_holds": self.fluid.continuity_holds(),
        }

    def cycle_many(self, raws):
        """Run a batch through the hub, one cycle each."""
        return [self.cycle(raw) for raw in raws]

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    def stats(self):
        return {
            "cycles": self.cycles,
            "ingestor": self.ingestor.stats(),
            "fluid": self.fluid.stats(),
            "left": self.left.stats(),
            "right": self.right.stats(),
            "coupling": self.coupling.stats(),
            "continuity_holds": self.fluid.continuity_holds(),
        }
def main():
    # Example usage of DiracInternetCentral
    central = DiracInternetCentral()

    # Simulate processing a raw internet payload
    raw_payload = {
        "text": "Analyze this sentence.",
        "image": b"\x89PNG...",
    }

    result = central.cycle(raw_payload)

    print("Cycle Result:", result)
    print("Hub Stats:", central.stats())

if __name__ == "__main__":
    main()