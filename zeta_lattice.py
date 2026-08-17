# zeta_lattice.py

from __future__ import annotations

from dataclasses import dataclass, field
from math import cos, sin, sqrt
from typing import Dict, List, Tuple


# First non-trivial Riemann zeta-zero imaginary parts.
# These are used as spectral anchor values in the UQTN lattice model.
ZETA_ZEROS: List[float] = [
    14.134725141734693,
    21.022039638771554,
    25.010857580145688,
    30.424876125859513,
    32.93506158773919,
]


@dataclass(frozen=True)
class ZetaNode:
    """One spectral anchor in the UQTN zeta lattice."""

    index: int
    value: float
    coordinates: Tuple[float, float, float]
    anchor_strength: float = 1.0


@dataclass
class ZetaLattice:
    """
    Local UQTN zeta-anchor lattice.

    Nodes represent spectral anchors.
    Edges represent bidirectional connection capacity.
    Propagation distributes Navigator MER across the connected lattice.
    """

    nodes: Dict[int, ZetaNode]
    edges: Dict[Tuple[int, int], float]
    damping: float = 0.15
    propagation_gain: float = 1.0
    last_activations: Dict[int, float] = field(default_factory=dict)

    @classmethod
    def init_default(
        cls,
        zeros: List[float] | None = None,
    ) -> "ZetaLattice":
        """Build the default bidirectional near-neighbor lattice."""
        values = zeros if zeros is not None else ZETA_ZEROS

        nodes: Dict[int, ZetaNode] = {}

        for index, value in enumerate(values):
            nodes[index] = ZetaNode(
                index=index,
                value=float(value),
                coordinates=cls._embed_zero(
                    value=float(value),
                    index=index,
                    total=len(values),
                ),
                anchor_strength=1.0,
            )

        edges: Dict[Tuple[int, int], float] = {}

        for index in range(len(values) - 1):
            weight = cls._edge_weight(
                float(values[index]),
                float(values[index + 1]),
            )

            edges[(index, index + 1)] = weight
            edges[(index + 1, index)] = weight

        return cls(
            nodes=nodes,
            edges=edges,
        )

    @staticmethod
    def _embed_zero(
        value: float,
        index: int,
        total: int,
    ) -> Tuple[float, float, float]:
        """
        Create a deterministic three-dimensional embedding.

        This is a computational coordinate mapping for the lattice model,
        not a claim that the embedding is a physical measurement.
        """
        radius = 1.0 + (value / 100.0)
        angle = (2.0 * 3.141592653589793 * index) / max(total, 1)

        x = radius * cos(angle)
        y = radius * sin(angle)
        z = value / 100.0

        return x, y, z

    @staticmethod
    def _edge_weight(value_a: float, value_b: float) -> float:
        """Assign a stable connection weight from spectral spacing."""
        spacing = abs(value_b - value_a)

        if spacing == 0:
            return 1.0

        return 1.0 / (1.0 + spacing)

    def neighbors(self, node_index: int) -> Dict[int, float]:
        """Return connected neighbors and their edge weights."""
        result: Dict[int, float] = {}

        for (source, target), weight in self.edges.items():
            if source == node_index:
                result[target] = weight

        return result

    def total_edge_weight(self, node_index: int) -> float:
        """Return the total outgoing edge weight for one node."""
        return sum(self.neighbors(node_index).values())

    def normalize(
        self,
        activations: Dict[int, float],
    ) -> Dict[int, float]:
        """Normalize node activations while preserving empty-state safety."""
        if not activations:
            return {}

        maximum = max(abs(value) for value in activations.values())

        if maximum == 0:
            return {index: 0.0 for index in activations}

        return {
            index: value / maximum
            for index, value in activations.items()
        }

    def propagate(
        self,
        navigator_mer: float,
    ) -> Dict[int, float]:
        """
        Propagate Navigator MER across every lattice node.

        The result remains compatible with NavigatorAgent:
            Dict[node_index, activation]

        Activation combines:
        - Navigator MER
        - node anchor strength
        - spectral value
        - local lattice connectivity
        - damping
        """
        if not self.nodes:
            self.last_activations = {}
            return {}

        total_nodes = len(self.nodes)
        safe_mer = float(navigator_mer)

        raw: Dict[int, float] = {}

        for index, node in self.nodes.items():
            local_flux = self.total_edge_weight(index)
            spectral_factor = 1.0 / (1.0 + node.value / 100.0)

            raw[index] = (
                safe_mer
                * self.propagation_gain
                * node.anchor_strength
                * spectral_factor
                * (1.0 + local_flux)
                * (1.0 - self.damping)
                / max(total_nodes, 1)
            )

        self.last_activations = self.normalize(raw)
        return self.last_activations

    def propagate_steps(
        self,
        initial: Dict[int, float],
        steps: int = 1,
    ) -> Dict[int, float]:
        """
        Perform repeated neighbor diffusion.

        This keeps the lattice evolution separate from the initial
        Navigator MER injection.
        """
        activations = {
            index: float(initial.get(index, 0.0))
            for index in self.nodes
        }

        for _ in range(max(steps, 0)):
            updated: Dict[int, float] = {}

            for index in self.nodes:
                current = activations.get(index, 0.0)
                incoming = 0.0

                for neighbor, weight in self.neighbors(index).items():
                    incoming += activations.get(neighbor, 0.0) * weight

                updated[index] = (
                    current * (1.0 - self.damping)
                    + incoming * self.damping
                )

            activations = self.normalize(updated)

        self.last_activations = activations
        return activations

    def activation_summary(self) -> Dict[str, float]:
        """Return summary statistics for the most recent propagation."""
        if not self.last_activations:
            return {
                "total": 0.0,
                "maximum": 0.0,
                "minimum": 0.0,
                "mean": 0.0,
            }

        values = list(self.last_activations.values())

        return {
            "total": float(sum(values)),
            "maximum": float(max(values)),
            "minimum": float(min(values)),
            "mean": float(sum(values) / len(values)),
        }

    def to_dict(self) -> Dict[str, object]:
        """Export lattice configuration and current activations."""
        return {
            "nodes": {
                str(index): {
                    "index": node.index,
                    "value": node.value,
                    "coordinates": node.coordinates,
                    "anchor_strength": node.anchor_strength,
                }
                for index, node in self.nodes.items()
            },
            "edges": {
                f"{source},{target}": weight
                for (source, target), weight in self.edges.items()
            },
            "damping": self.damping,
            "propagation_gain": self.propagation_gain,
            "last_activations": self.last_activations,
        }


def main() -> None:
    """Run a local zeta-lattice smoke test."""
    lattice = ZetaLattice.init_default()

    activations = lattice.propagate(
        navigator_mer=6.47213595499958
    )

    print("Zetari.AI / UQTN Zeta Lattice")
    print("-" * 34)
    print(f"Nodes: {len(lattice.nodes)}")
    print(f"Edges: {len(lattice.edges)}")
    print(f"Activations: {activations}")
    print(f"Summary: {lattice.activation_summary()}")

    print("\nNode coordinates:")

    for index, node in lattice.nodes.items():
        print(
            f"{index}: "
            f"zero={node.value:.6f}, "
            f"coordinates={node.coordinates}"
        )


if __name__ == "__main__":
    main()