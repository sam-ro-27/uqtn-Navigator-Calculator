"""
ingest.py — intake: raw internet information becomes DiracPackets.

The ingestor is the mouth of the hub. It takes raw material —
text, images, or mixed payloads — and performs the chiral split
into left (analytic) and right (holistic) components.
"""

from .dirac_packet import DiracPacket


class Ingestor:
    """
    Turns raw internet information into fluid-ready packets.

    Split convention (GIVEN hemisphere duties):
      text / data / code / sequence -> LEFT
      image / frame / pattern       -> RIGHT
    Everything else rides along in meta.
    """

    def __init__(self):
        self.ingested = 0

    def ingest(self, raw):
        """One raw payload -> one DiracPacket."""
        packet = DiracPacket.chiral_split(raw)
        self.ingested += 1
        return packet

    def ingest_many(self, raws):
        """A batch of raw payloads -> a list of DiracPackets."""
        return [self.ingest(raw) for raw in raws]

    def stats(self):
        return {"ingested": self.ingested}
def main():
    # Example usage of Ingestor class
    ingestor = Ingestor()

    # Simulate ingesting raw internet information
    raw_data = [
        {"text": "Analyze this sentence."},
        {"image": b"\x89PNG..."},
        {"text": "Another text payload."},
        {"image": b"\x89PNG..."},
        {"text": "Final text payload."},
    ]

    packets = ingestor.ingest_many(raw_data)
    for i, packet in enumerate(packets):
        print(f"Packet {i}: {packet.to_dict()}")

    print("Ingestor Stats:", ingestor.stats())

if __name__ == "__main__":
    main()