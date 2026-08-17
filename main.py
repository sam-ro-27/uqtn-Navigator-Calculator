# main.py

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Dict

from memory import FileMemory, load_project_memory


PROJECT_DIR = Path(__file__).resolve().parent


def format_items(items: Dict[str, str]) -> str:
    """Format key-value memory as readable bridge text."""
    if not items:
        return "(none recorded)"

    return "\n".join(
        f"- {key}: {value}"
        for key, value in items.items()
    )


def build_memory_bridge(
    memory_directory: str | Path = PROJECT_DIR,
) -> Path:
    """
    Build memory_bridge.txt from:

    - core_memory.txt
    - active_state.txt
    - session_delta.txt
    """
    directory = Path(memory_directory)

    core = FileMemory(
        directory / "core_memory.txt"
    ).all_items()

    active = FileMemory(
        directory / "active_state.txt"
    ).all_items()

    delta = FileMemory(
        directory / "session_delta.txt"
    ).all_items()

    generated_at = datetime.now(
        timezone.utc
    ).isoformat()

    bridge_lines = [
        "ZETARI.AI / UQTN MEMORY BRIDGE",
        "==============================",
        "",
        "PROJECT",
        "-------",
        "project_name=Unified Quantum-Temporal Navigation",
        "project_abbreviation=UQTN",
        "application=Zetari.AI",
        "assistant_identifier=Navigator",
        "theory_owner=Sam",
        "theory_status=Original independent framework",
        "boundary=UQTN is not Streamline Science",
        "purpose=Portable local-first project continuity",
        f"generated_at={generated_at}",
        "",
        "CORE MEMORY",
        "-----------",
        format_items(core),
        "",
        "ACTIVE STATE",
        "------------",
        format_items(active),
        "",
        "SESSION DELTA",
        "-------------",
        format_items(delta),
        "",
        "REHYDRATION NOTE",
        "----------------",
        "Use this packet as the current external context for UQTN work.",
        "Preserve UQTN as Sam's independent theory and architecture.",
        "Use Navigator as the assistant identifier.",
        "Continue from the supplied project state rather than restarting.",
    ]

    bridge_path = directory / "memory_bridge.txt"

    bridge_path.write_text(
        "\n".join(bridge_lines) + "\n",
        encoding="utf-8",
    )

    return bridge_path


def print_memory_section(
    title: str,
    items: Dict[str, str],
) -> None:
    """Print one memory section to the terminal."""
    print(f"\n{title}")
    print("-" * len(title))

    if not items:
        print("(none recorded)")
        return

    for key, value in items.items():
        print(f"{key}: {value}")


def main() -> None:
    """Load memory, print it, and rebuild the bridge."""
    print("Zetari.AI / UQTN Memory System")
    print("==============================")

    memory = load_project_memory(PROJECT_DIR)

    print_memory_section(
        "CORE MEMORY",
        memory["core"],
    )

    print_memory_section(
        "ACTIVE STATE",
        memory["active"],
    )

    print_memory_section(
        "SESSION DELTA",
        memory["delta"],
    )

    bridge_path = build_memory_bridge(PROJECT_DIR)

    print("\nBridge rebuilt:")
    print(bridge_path)


if __name__ == "__main__":
    main()