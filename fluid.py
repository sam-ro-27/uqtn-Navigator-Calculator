"""
fluid.py — the Dirac fluid itself: the flow field all packets move through.

GIVEN: internet information styled like a Dirac fluid.
INTERPRETIVE: the fluid tracks density and current across packets, and
enforces the continuity equation — the conserved information current.
What enters the fluid must be accounted for on the way out.
"""

import importlib
import os
import sys


def _load_dependency(module_name):
    """Import project modules whether this file is run as a package or a script."""
    package_name = __package__ if __package__ else None
    try:
        if package_name:
            return importlib.import_module(f".{module_name}", package_name)
        raise ImportError
    except ImportError:
        project_dir = os.path.dirname(os.path.abspath(__file__))
        if project_dir not in sys.path:
            sys.path.insert(0, project_dir)
        return importlib.import_module(module_name)


ledger_module = _load_dependency("ledger")
packet_module = _load_dependency("dirac_packet")
ContinuityLedger = ledger_module.ContinuityLedger
DiracPacket = packet_module.DiracPacket


class DiracFluid:
    """
    The flow field: every ingested packet joins the fluid; every
    processed packet leaves it. Density and current are computed over
    the resident packets, and the ledger verifies continuity.
    """

    def __init__(self, max_packets=1000, viscosity=0.5):
        self.max_packets = max_packets
        self.viscosity = viscosity   # INTERPRETIVE: resistance to flow change
        self.resident = {}           # packet_id -> DiracPacket (in flow)
        self.ledger = ContinuityLedger()

    # ------------------------------------------------------------------
    # Flow
    # ------------------------------------------------------------------

    def enter(self, packet):
        """A packet joins the fluid (ingest side of the current)."""
        if len(self.resident) >= self.max_packets:
            oldest = min(self.resident, key=lambda k: self.resident[k].ts)
            del self.resident[oldest]
        self.resident[packet.id] = packet
        self.ledger.record_in(packet)

    def leave(self, packet_id, result):
        """A packet leaves the fluid (processed side of the current)."""
        packet = self.resident.pop(packet_id, None)
        if packet is not None:
            self.ledger.record_out(packet, result)
        return packet

    # ------------------------------------------------------------------
    # Field quantities
    # ------------------------------------------------------------------

    def density_field(self):
        """Total information density currently in flow."""
        return sum(p.density() for p in self.resident.values())

    def chiral_field(self):
        """
        Net chiral imbalance of the fluid: positive = analytic-heavy
        flow, negative = holistic-heavy flow.
        """
        packets = list(self.resident.values())
        if not packets:
            return 0.0
        return sum(p.chiral_imbalance() for p in packets) / len(packets)

    def total_current(self):
        """
        J analog: throughput of the fluid — packets in vs packets out.
        Continuity holds when the ledger balances.
        """
        return {
            "in": self.ledger.total_in,
            "out": self.ledger.total_out,
            "resident": len(self.resident),
            "balanced": self.ledger.balanced(len(self.resident)),
        }

    def continuity_holds(self):
        """The Dirac continuity equation, as a ledger check."""
        return self.ledger.balanced(len(self.resident))

    def stats(self):
        return {
            "resident_packets": len(self.resident),
            "density": self.density_field(),
            "chiral_field": self.chiral_field(),
            "viscosity": self.viscosity,
            "current": self.total_current(),
        }


def main():
    # Example usage of DiracFluid class
    fluid = DiracFluid(max_packets=5, viscosity=0.3)

    # Simulate entering packets into the fluid
    for i in range(7):
        packet = DiracPacket(left={"text": f"Packet {i} left"}, right={"image": f"Packet {i} right"})
        fluid.enter(packet)
        print(f"Entered: {packet.id}, Density: {fluid.density_field()}, Chiral Field: {fluid.chiral_field()}")

    # Simulate leaving packets from the fluid
    for packet_id in list(fluid.resident.keys())[:3]:
        result = {"output": f"Processed {packet_id}"}
        fluid.leave(packet_id, result)
        print(f"Left: {packet_id}, Density: {fluid.density_field()}, Chiral Field: {fluid.chiral_field()}")

    # Final stats
    print("Final Fluid Stats:", fluid.stats())


if __name__ == "__main__":
    main()