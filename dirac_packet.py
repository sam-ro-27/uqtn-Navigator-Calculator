"""
dirac_packet.py — the two-component information packet.

GIVEN: internet information styled like a Dirac fluid.
INTERPRETIVE: each packet is a spinor-like state with a left (analytic)
and right (holistic) component, after the A/B sublattice pseudospin of
the Dirac fluid's carriers.
"""

import time
import uuid


class DiracPacket:
    """
    One unit of internet information.

    Attributes:
        left:   analytic component  -> processed by the LEFT hemisphere
        right:  holistic component  -> processed by the RIGHT hemisphere
        id:     unique packet id (continuity ledger key)
        ts:     ingest timestamp
    """

    def __init__(self, left=None, right=None, meta=None):
        self.id = uuid.uuid4().hex[:12]
        self.ts = time.time()
        self.left = left or {}
        self.right = right or {}
        self.meta = meta or {}

    # ------------------------------------------------------------------
    # Spinor math (INTERPRETIVE): density and overlap of the two components
    # ------------------------------------------------------------------

    def _mass(self, component):
        """Scalar 'mass' of one component: its information content size."""
        if isinstance(component, dict):
            return sum(len(str(v)) for v in component.values())
        return len(str(component))

    def density(self):
        """
        |psi|^2 analog: total information density of the packet.
        Sum of both chiral components.
        """
        return self._mass(self.left) + self._mass(self.right)

    def chiral_imbalance(self):
        """
        (L - R) / (L + R): which hemisphere dominates this packet.
        +1 = purely analytic, -1 = purely holistic, 0 = balanced.
        """
        l, r = self._mass(self.left), self._mass(self.right)
        total = l + r
        if total == 0:
            return 0.0
        return (l - r) / total

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self):
        return {
            "id": self.id,
            "ts": self.ts,
            "left": self.left,
            "right": self.right,
            "meta": self.meta,
            "density": self.density(),
            "chiral_imbalance": self.chiral_imbalance(),
        }

    @classmethod
    def chiral_split(cls, raw):
        """
        Split raw internet information into (left, right) components.

        Convention (GIVEN hemisphere duties):
          text / data / sequence  -> left  (analytic)
          image / pattern / scene -> right (holistic)
        """
        left = {}
        right = {}
        meta = {}
        if isinstance(raw, dict):
            for key, value in raw.items():
                k = key.lower()
                if k in ("text", "data", "code", "sequence", "message", "prompt"):
                    left[key] = value
                elif k in ("image", "images", "frame", "pattern", "scene", "video"):
                    right[key] = value
                else:
                    meta[key] = value
        else:
            left["text"] = raw
        return cls(left=left, right=right, meta=meta)
