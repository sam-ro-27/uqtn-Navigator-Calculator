"""
left_hemisphere.py — the analytic hemisphere.

GIVEN: left hemisphere duty = analytic channel
(text, data, logic, sequential reasoning).
"""

from typing import cast

try:
    from .hemisphere import Hemisphere as BaseHemisphere  # pyright: ignore[reportMissingImports]
except ImportError:  # pragma: no cover - fallback for direct script execution
    try:
        from hemisphere import Hemisphere as BaseHemisphere  # pyright: ignore[reportMissingImports]
    except ImportError:  # pragma: no cover - final fallback
        class BaseHemisphere:
            """Minimal fallback used only when the base hemisphere is unavailable."""

            def __init__(self, *args, **kwargs):
                _ = args
                self.confirm_mode = kwargs.get("confirm_mode", False)
                self.model = kwargs.get("model")
                self.last_result = None

            def process(self, component):
                return {"component": component, "output": {}}

            def _generate(self, prompt):
                _ = prompt
                return ""

            def _mark_confirmed(self):
                self.confirm_mode = True

            def stats(self):
                return {"status": "fallback"}

BaseHemisphere = cast(type, BaseHemisphere)


class Hemisphere(BaseHemisphere):
    """Compatibility wrapper around the imported or fallback base class."""

    pass


class LeftHemisphere(Hemisphere):
    """
    LEFT hemisphere: the analytic mind of the hub.

    Handles the left-chiral component of each packet:
      - text and language
      - code and data
      - sequential / logical structure

    Extension points (spacious by design): override any of these
    to deepen the analytic duty without touching the hub.
    """

    side = "left"
    duty = "analytic"

    def _safe_reply(self, prompt):
        """Normalize model output into a text string when the base implementation
        returns a non-string or a typed `Never`-incompatible value."""
        try:
            reply = self._generate(prompt)
        except Exception:
            return ""
        if reply is None:
            return ""
        return str(reply) if not isinstance(reply, str) else reply

    def process(self, component):
        result = super().process(component)
        result["output"] = {
            "analysis": self.analyze(component),
            "terms": self.extract_terms(component),
        }
        self.last_result = result
        return result

    # ------------------------------------------------------------------
    # Analytic duties — override to deepen
    # ------------------------------------------------------------------

    def analyze(self, component):
        """Structural analysis of the analytic component."""
        text = str(component)
        # Confirm mode: live model read (the full stack, live-tested).
        if self.confirm_mode and text.strip():
            reply = self._safe_reply(
                "Analyze the following text structurally. Reply in two short "
                "lines: line 1 the core claim, line 2 the key structure.\n\n"
                + text[:4000]
            )
            if reply:
                self._mark_confirmed()
                return {
                    "confirmed": True,
                    "reading": reply,
                    "chars": len(text),
                    "words": len(text.split()),
                }
        # Heuristic fallback (fast scaffolding).
        return {
            "confirmed": False,
            "chars": len(text),
            "words": len(text.split()),
        }

    def extract_terms(self, component):
        """Salient terms: live model list in confirm mode, heuristic otherwise."""
        text = str(component)
        if self.confirm_mode and text.strip():
            reply = self._safe_reply(
                "List the salient key terms in the following text as a "
                "comma-separated list, nothing else.\n\n" + text[:4000]
            )
            if reply:
                self._mark_confirmed()
                return [t.strip() for t in reply.split(",") if t.strip()][:20]
        words = str(component).split()
        seen = []
        for w in words:
            w = w.strip(".,!?;:\"'()").lower()
            if len(w) > 4 and w not in seen:
                seen.append(w)
        return seen[:20]
def main():
    # Example usage of LeftHemisphere class
    left_hemisphere = LeftHemisphere(model="llama3.2:latest")

    # Simulate processing a DiracPacket
    packet = {
        "left": {"text": "Analyze this sentence."},
        "right": {"image": b"\x89PNG..."},
    }

    left_result = left_hemisphere.process(packet["left"])
    print("Left Hemisphere Result:", left_result)
    print("Left Hemisphere Stats:", left_hemisphere.stats())

if __name__ == "__main__":
    main()