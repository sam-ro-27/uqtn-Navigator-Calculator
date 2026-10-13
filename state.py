"""
state.py — fluid state snapshots for the frontend and state panel.

Produces a plain-dict snapshot of the hub: densities, currents,
hemisphere throughput, and continuity. Shaped to sit alongside the
Krimoxous navigator state (environmental / emotional / mental /
physical / resistance) without disturbing it.
"""


def fluid_state_snapshot(central):
    """
    Snapshot the whole hub as a JSON-safe dict.

    Keys are deliberately flat and numeric where possible so a
    state panel can render them directly.
    """
    stats = central.stats()
    fluid = stats["fluid"]
    current = fluid["current"]

    return {
        "dirac_cycles": stats["cycles"],
        "fluid_density": round(fluid["density"], 2),
        "fluid_chiral_field": round(fluid["chiral_field"], 4),
        "fluid_viscosity": fluid["viscosity"],
        "current_in": current["in"],
        "current_out": current["out"],
        "current_resident": current["resident"],
        "continuity_holds": stats["continuity_holds"],
        "left_processed": stats["left"]["processed"],
        "right_processed": stats["right"]["processed"],
        "coupling_exchanges": stats["coupling"]["exchanges"],
    }

def main():
    # Example usage of fluid_state_snapshot function
    from central import DiracInternetCentral

    central = DiracInternetCentral()
    snapshot = fluid_state_snapshot(central)
    print(snapshot)

if __name__ == "__main__":
    main()