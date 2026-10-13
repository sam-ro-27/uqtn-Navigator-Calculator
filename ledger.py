"""
ledger.py — the continuity ledger.

INTERPRETIVE: the Dirac continuity equation, kept as books.
Every packet that enters the fluid is recorded; every packet that
leaves is recorded with its result. The books must balance:
total_in == total_out + resident.
"""


class ContinuityLedger:
    """
    Double-entry books for the information current.

    Nothing enters or leaves the fluid unaccounted. If the books
    ever fail to balance, the hub has lost information — which the
    Dirac styling forbids.
    """

    def __init__(self):
        self.total_in = 0
        self.total_out = 0
        self.entries = []  # (packet_id, direction, density)

    def record_in(self, packet):
        self.total_in += 1
        self.entries.append((packet.id, "in", packet.density()))

    def record_out(self, packet, result):
        self.total_out += 1
        self.entries.append((packet.id, "out", packet.density()))

    def balanced(self, resident=0):
        """
        Continuity check: in == out + resident.
        Called with the fluid's resident count by DiracFluid.
        """
        return self.total_in == self.total_out + resident

    def stats(self):
        return {
            "total_in": self.total_in,
            "total_out": self.total_out,
            "balanced": self.balanced(),
            "entries": len(self.entries),
        }
def main():
    ledger = ContinuityLedger()
    print("Initial stats:", ledger.stats())
    packet1 = type("Packet", (), {"id": "p1", "density": lambda: 10})()
    packet2 = type("Packet", (), {"id": "p2", "density": lambda: 20})()
    ledger.record_in(packet1)
    ledger.record_in(packet2)
    print("After recording in two packets:", ledger.stats())
    ledger.record_out(packet1, result="processed")
    print("After recording out one packet:", ledger.stats())

if __name__ == "__main__":
    main()