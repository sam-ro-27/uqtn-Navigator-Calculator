"""
vortex.py — attention vortices in the Dirac fluid.

STATUS: UNRULED — DORMANT BY DEFAULT.

This module is the assistant's proposal, not the user's ruling:
in the Dirac fluid, vortices form where flow curls around an
obstacle. Here, a vortex is where information circles a hard
problem before resolving — attention pooling.

DO NOT wire this into the hub until the user rules on it.
Enable only via DiracConfig(vortex_enabled=True) after his ruling.
"""


class Vortex:
    """
    A standing whirlpool in the information flow.

    Packets caught in a vortex orbit a `topic` for a bounded number
    of cycles instead of flowing straight through. When the orbit
    completes, the accumulated reading is released downstream.
    """

    DORMANT = True  # flip only on user ruling

    def __init__(self, topic, max_orbits=3):
        self.topic = topic
        self.max_orbits = max_orbits
        self.orbits = 0
        self.caught = []

    def catch(self, packet):
        """Pull a packet into the vortex orbit."""
        if self.DORMANT:
            return False
        self.caught.append(packet)
        return True

    def turn(self):
        """
        Advance one orbit. Returns the released accumulation when
        max_orbits is reached, else None (still circling).
        """
        if self.DORMANT or not self.caught:
            return None
        self.orbits += 1
        if self.orbits >= self.max_orbits:
            released = {
                "topic": self.topic,
                "orbits": self.orbits,
                "packets": [p.id for p in self.caught],
                "density": sum(p.density() for p in self.caught),
            }
            self.caught = []
            self.orbits = 0
            return released
        return None

    def stats(self):
        return {
            "dormant": self.DORMANT,
            "topic": self.topic,
            "orbits": self.orbits,
            "caught": len(self.caught),
        }
def main():
    # Example usage of Vortex class
    vortex = Vortex(topic="hard_problem", max_orbits=3)

    # Simulate catching packets
    for i in range(5):
        packet = type("Packet", (object,), {"id": f"packet_{i}", "density": i + 1})()
        vortex.catch(packet)
        released = vortex.turn()
        if released:
            print(f"Released from vortex: {released}")

if __name__ == "__main__":
    main()