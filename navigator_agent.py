# navigator_agent.py

from dataclasses import dataclass, field
from typing import List, Dict
from uqtn_core import NavigatorState, coherence_state
from zeta_lattice import ZetaLattice

@dataclass
class NavigatorAgent:
    name: str
    state: NavigatorState
    lattice: ZetaLattice = field(default_factory=ZetaLattice.init_default)
    history: List[Dict] = field(default_factory=list)

    def step(self, description: str) -> Dict:
        """
        One navigation/computation step:
        - compute MER and coherence
        - propagate MER into zeta lattice
        - log what happened
        """
        mer = self.state.mer
        state_label = coherence_state(mer)
        activations = self.lattice.propagate(mer)

        record = {
            "description": description,
            "agency": self.state.agency,
            "resistance": self.state.resistance,
            "mer": mer,
            "coherence_state": state_label,
            "zeta_activations": activations,
        }
        self.history.append(record)
        return record