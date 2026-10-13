"""
coupling.py — the corpus callosum of the hub.

INTERPRETIVE: the two hemispheres are joined by a coupling channel,
after the corpus callosum joining brain hemispheres. Each cycle the
coupling fuses a bounded amount of left/right output so neither
hemisphere reasons in isolation.
"""

from collections import deque


class CorpusCallosum:
    """
    Inter-hemisphere exchange.

    Bandwidth-bounded: at most `bandwidth` fused exchanges are kept
    in recent history. The fusion itself is deliberately simple —
    a meeting point the user can deepen later.
    """

    def __init__(self, bandwidth=10):
        self.bandwidth = bandwidth
        self.recent = deque(maxlen=bandwidth)
        self.exchanges = 0

    def exchange(self, left_result, right_result):
        """
        Fuse one left output and one right output into a single
        whole-mind reading. Returns the fused dict.
        """
        fused = {
            "analytic": (left_result or {}).get("output"),
            "holistic": (right_result or {}).get("output"),
            "fused_note": self._fuse_note(left_result, right_result),
        }
        self.recent.append(fused)
        self.exchanges += 1
        return fused

    def _fuse_note(self, left_result, right_result):
        """One-line meeting point of the two readings."""
        l = (left_result or {}).get("duty", "left")
        r = (right_result or {}).get("duty", "right")
        return f"{l} reading joined with {r} reading"

    def stats(self):
        return {
            "bandwidth": self.bandwidth,
            "exchanges": self.exchanges,
            "recent_kept": len(self.recent),
        }
def main():
    # Example usage of CorpusCallosum class
    callosum = CorpusCallosum(bandwidth=5)

    # Simulate left and right hemisphere results
    left_result = {
        "side": "left",
        "duty": "analytic",
        "output": {"analysis": {"chars": 20, "words": 4}, "terms": ["analyze", "sentence"]},
    }
    right_result = {
        "side": "right",
        "duty": "holistic",
        "output": {"impression": {"present": ["image"], "count": 1}, "patterns": {"note": "pattern pass complete"}},
    }

    fused_result = callosum.exchange(left_result, right_result)

    print("Fused Result:", fused_result)
    print("Corpus Callosum Stats:", callosum.stats())

if __name__ == "__main__":
    main()