"""
right_hemisphere.py — the holistic hemisphere.

GIVEN: right hemisphere duty = holistic channel
(vision, pattern, whole-scene reads).
"""

import importlib.util
from pathlib import Path


def _load_hemisphere_class():
    """Resolve the sibling Hemisphere module without package-only imports."""
    current_dir = Path(__file__).resolve().parent
    candidates = [
        current_dir / "hemisphere.py",
        current_dir.parent / "hemisphere.py",
    ]

    for candidate in candidates:
        if not candidate.exists():
            continue
        spec = importlib.util.spec_from_file_location(
            "_dynamic_hemisphere",
            candidate,
        )
        if spec is None or spec.loader is None:
            continue
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if hasattr(module, "Hemisphere"):
            return module.Hemisphere

    raise ImportError("Unable to locate hemisphere.py next to right_hemisphere.py")


Hemisphere = _load_hemisphere_class()


class RightHemisphere(Hemisphere):
    """
    RIGHT hemisphere: the holistic mind of the hub.

    Handles the right-chiral component of each packet:
      - vision frames and scenes
      - patterns and spatial layout
      - whole-impression reads

    Extension points (spacious by design): override any of these
    to deepen the holistic duty without touching the hub.
    """

    side = "right"
    duty = "holistic"

    def process(self, component):
        result = super().process(component)
        result["output"] = {
            "impression": self.impression(component),
            "patterns": self.pattern_notes(component),
        }
        self.last_result = result
        return result

    # ------------------------------------------------------------------
    # Holistic duties — confirm mode calls live models, else heuristics
    # ------------------------------------------------------------------

    def impression(self, component):
        """Whole-scene read: what is present, in one breath."""
        # Confirm mode, real image bytes present: live vision call.
        image_bytes = self._extract_image_bytes(component)
        if self.confirm_mode and image_bytes:
            seen = self._vision_describe(image_bytes)
            if seen:
                self._mark_confirmed()
                return {"confirmed": True, "impression": seen}
        # Confirm mode, description text present: live impression read.
        desc = self._describe_component(component)
        if self.confirm_mode and desc:
            reply = self._generate(
                "Give a whole-scene impression of the following in one "
                "sentence.\n\n" + desc[:4000]
            )
            if reply:
                self._mark_confirmed()
                return {"confirmed": True, "impression": reply}
        # Heuristic fallback (fast scaffolding).
        if isinstance(component, dict):
            keys = list(component.keys())
            return {"confirmed": False, "present": keys, "count": len(keys)}
        return {"confirmed": False, "present": ["unstructured"], "count": 1}

    def pattern_notes(self, component):
        """Pattern-level notes: live model read in confirm mode."""
        desc = self._describe_component(component)
        if self.confirm_mode and desc:
            reply = self._generate(
                "Note the patterns in the following in one short sentence.\n\n"
                + desc[:4000]
            )
            if reply:
                self._mark_confirmed()
                return {"confirmed": True, "note": reply}
        return {
            "confirmed": False,
            "note": "pattern pass complete",
            "detail": desc[:200],
        }

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _describe_component(self, component):
        """Flatten the holistic component to descriptive text."""
        if isinstance(component, dict):
            parts = []
            for key, value in component.items():
                if isinstance(value, (bytes, bytearray)):
                    parts.append(f"{key}: <image bytes>")
                else:
                    parts.append(f"{key}: {value}")
            return "; ".join(parts)
        if isinstance(component, (bytes, bytearray)):
            return "<image bytes>"
        return str(component)

    def _extract_image_bytes(self, component):
        """Pull raw image bytes out of the component, if present."""
        if isinstance(component, (bytes, bytearray)):
            return bytes(component)
        if isinstance(component, dict):
            for key in ("image", "frame", "picture", "photo"):
                value = component.get(key)
                if isinstance(value, (bytes, bytearray)):
                    return bytes(value)
        return None

    def _vision_describe(self, image_bytes, timeout=120.0):
        """Live vision-model description of raw image bytes."""
        try:
            import base64
            import httpx  # lazy
        except ImportError:
            return ""
        try:
            b64 = base64.b64encode(image_bytes).decode("ascii")
            r = httpx.post(
                self.ollama_url,
                json={
                    "model": self.model,
                    "prompt": (
                        "Describe this scene in one short sentence. "
                        "Do not invent details you cannot see."
                    ),
                    "images": [b64],
                    "stream": False,
                    "keep_alive": "30m",
                },
                timeout=timeout,
            )
            if r.status_code != 200:
                return ""
            try:
                data = r.json()
            except ValueError:
                return ""
            if isinstance(data, dict):
                return (data.get("response") or "").strip()
            return ""
        except Exception:
            return ""

    def _generate(self, prompt, timeout=120.0):
        """Live model generation of text prompt."""
        try:
            import httpx  # lazy
        except ImportError:
            return ""
        try:
            r = httpx.post(
                self.ollama_url,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "keep_alive": "30m",
                },
                timeout=timeout,
            )
            if r.status_code != 200:
                return ""
            try:
                data = r.json()
            except ValueError:
                return ""
            if isinstance(data, dict):
                return (data.get("response") or "").strip()
            return ""
        except Exception:
            return ""

    def _mark_confirmed(self):
        """Mark the last result as confirmed by a live model call."""
        if self.last_result is not None:
            self.last_result["confirmed"] = True

    def stats(self):
        """Return a dict of the hemisphere's current state."""
        return {
            "side": self.side,
            "duty": self.duty,
            "confirm_mode": self.confirm_mode,
            "ollama_url": self.ollama_url,
        }


def main():
    # Example usage of RightHemisphere class
    right_hemisphere = RightHemisphere(model="llama3.2:latest")

    # Simulate processing a DiracPacket
    packet = {
        "left": {"text": "Analyze this sentence."},
        "right": {"image": b"\x89PNG..."},
    }

    right_result = right_hemisphere.process(packet["right"])
    print("Right Hemisphere Result:", right_result)
    print("Right Hemisphere Stats:", right_hemisphere.stats())


if __name__ == "__main__":
    main()