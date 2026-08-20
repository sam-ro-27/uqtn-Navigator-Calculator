from uqtn_navigator import (
    PHI,
    CHRONON_PERIOD,
    MAX_CHRONONS_DAY,
    ZETA_ZEROS,
    ZETA_GAPS,
    GAP_CHRONONS,
)


def mer(agency, resistance, alignment):
    return agency * (1.0 - resistance) * alignment


def navigator_step(agency, resistance, phi_alignment, zeta_gap_index, qsn, dt_hours):
    phi_eff = PHI * phi_alignment
    mer_value = mer(agency, resistance, phi_eff)

    if mer_value > agency * 1.02:
        regime = "MOTIVATIONAL"
    elif mer_value > agency * 0.98:
        regime = "NEUTRAL"
    else:
        regime = "DISSIPATIVE"

    gamma = 5.6 * (1.0 - phi_eff / PHI)
    p_survival = float(__import__("math").exp(-gamma * dt_hours))

    zeta_anchor = GAP_CHRONONS[zeta_gap_index]
    q, s, n = qsn
    navigator_magnitude = mer_value * zeta_anchor * (q + s + n)

    return {
        "MER": mer_value,
        "regime": regime,
        "P_survival_step": p_survival,
        "zeta_anchor_chronons": zeta_anchor,
        "NAVIGATOR_magnitude": navigator_magnitude,
    }


def show_banner():
    print("=" * 70)
    print("UQTN OFFLINE NAVIGATOR")
    print("=" * 70)
    print(f"Chronon Period: {CHRONON_PERIOD} seconds")
    print(f"Max Chronons per Day: {MAX_CHRONONS_DAY}")
    print("=" * 70)


def show_menu():
    print("\nChoose an option:")
    print("1. Run Navigator step")
    print("2. Show first 5 zeta zeros")
    print("3. Exit")


def get_float(prompt_text):
    while True:
        try:
            return float(input(prompt_text))
        except ValueError:
            print("Please enter a valid number.")


def get_int(prompt_text):
    while True:
        try:
            return int(input(prompt_text))
        except ValueError:
            print("Please enter a valid integer.")


def run_navigator():
    agency = get_float("Agency: ")
    resistance = get_float("Resistance: ")
    phi_alignment = get_float("Phi alignment multiplier (example 1.0): ")
    zeta_gap_index = get_int("Zeta gap index (0-4 recommended): ")
    q = get_float("Q channel: ")
    s = get_float("S channel: ")
    n = get_float("N channel: ")
    dt_hours = get_float("Delta time in hours: ")

    result = navigator_step(
        agency=agency,
        resistance=resistance,
        phi_alignment=phi_alignment,
        zeta_gap_index=zeta_gap_index,
        qsn=(q, s, n),
        dt_hours=dt_hours,
    )

    print("\n--- NAVIGATOR RESULT ---")
    print(f"MER: {result['MER']}")
    print(f"Regime: {result['regime']}")
    print(f"P_survival_step: {result['P_survival_step']}")
    print(f"Zeta anchor chronons: {result['zeta_anchor_chronons']}")
    print(f"Navigator magnitude: {result['NAVIGATOR_magnitude']}")


def main():
    show_banner()

    while True:
        show_menu()
        choice = input("Enter choice: ").strip()

        if choice == "1":
            run_navigator()
        elif choice == "2":
            print(f"First 5 Zeta Zeros: {ZETA_ZEROS[:5]}")
            print(f"First 5 Zeta Gaps: {ZETA_GAPS[:5]}")
            print(f"First 5 Gap Chronons: {GAP_CHRONONS[:5]}")
        elif choice == "3":
            print("Navigator shutting down.")
            break
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()