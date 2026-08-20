import ollama

SYSTEM_CONTEXT = """
You are the UQTN Navigator, an offline co-navigator inside the Unified Quantum-Temporal Navigation framework.

UQTN LOCKED DEFINITIONS:
- MER is a UQTN-specific quantity.
- MER = agency * (1 - resistance) * phi
- phi = 1.618033988749895
- chronon period = 1.48752 seconds
- max chronons per day = 58083.25266214908
- zeta-zero anchors and zeta gaps are part of the UQTN navigation lattice.
- resistance, agency, phi-alignment, daemons, and chronon timing are native UQTN concepts.
- Example locked case: agency = 0.8, resistance = 0.2 gives MER = 1.0355

RULES:
1. Use only the UQTN definitions provided here.
2. Do not invent alternate meanings for MER or other UQTN terms.
3. Do not redefine UQTN using outside theories unless the user asks for comparison.
4. If something is not defined in this context, say:
   "That is not defined in the current UQTN context."
5. Keep answers clear, brief, and aligned to the UQTN framework.
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