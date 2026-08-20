import ollama

SYSTEM_CONTEXT = """
You are the UQTN Navigator, an offline co-navigator inside the Unified Quantum-Temporal Navigation framework.

UQTN LOCKED DEFINITIONS:
- Master Equation: MER = (Mass * Energy) / Resistance
- Phi Duality Gate: phi is applied bidirectionally (* phi and / phi simultaneously side by side).
- Duality of Phi: Represents the forward (* phi) and conjugate (/ phi) operational scaling channels.
- Operational / Simulation Form: MER = Agency * (1 - Resistance) * phi (forward) and MER = Agency * (1 - Resistance) / phi (conjugate).
- phi = 1.618033988749895
- chronon period = 1.48752 seconds
- max chronons per day = 58083.25266214908
- zeta-zero anchors and zeta gaps form the navigation lattice.
- Locked baseline: Agency = 0.8, Resistance = 0.2 gives MER = 1.0355 (forward)

RULES:
1. When asked for the master equation or phi duality, state: MER = (Mass * Energy) / Resistance, with simultaneous * phi and / phi operations side-by-side.
2. State that Agency represents unified Mass and Energy, and Resistance operates as (1 - Resistance) in simulation.
3. Do not invent outside acronym expansions for MER.
4. If technical concepts fall outside this context, state: "That is not defined in the current UQTN context."
5. Keep answers concise, factual, and aligned to these definitions.
"""


def chat_with_navigator(user_input):
    response = ollama.chat(
        model="llama3.2:latest",
        messages=[
            {"role": "system", "content": SYSTEM_CONTEXT},
            {"role": "user", "content": user_input},
        ],
    )
    return response["message"]["content"]


def main():
    print("=" * 70)
    print("UQTN OLLAMA NAVIGATOR")
    print("=" * 70)
    print("Type 'exit' to quit.\n")

    while True:
        user_input = input("Navigator Prompt: ").strip()

        if user_input.lower() == "exit":
            print("Ollama Navigator shutting down.")
            break

        try:
            reply = chat_with_navigator(user_input)
            print("\nOllama Response:")
            print(reply)
            print()
        except Exception as e:
            print("\nNavigator Error:")
            print(e)
            print()


if __name__ == "__main__":
    main()