# memory.py

from __future__ import annotations

import abc
from pathlib import Path
from typing import Dict, Optional


class Memory(abc.ABC):
    """Abstract interface for local project memory."""

    @abc.abstractmethod
    def store(self, key: str, value: str) -> None:
        """Store or update one key-value item."""
        raise NotImplementedError

    @abc.abstractmethod
    def retrieve(self, key: str) -> Optional[str]:
        """Retrieve one value by key."""
        raise NotImplementedError

    @abc.abstractmethod
    def all_items(self) -> Dict[str, str]:
        """Return every stored key-value item."""
        raise NotImplementedError


class FileMemory(Memory):
    """
    Plain-text key-value memory.

    File format:

        PROJECT=UQTN
        IDENTIFIER=Navigator
        CORE_EQUATION=MER=(Mass*Energy)/Resistance

    Blank lines and lines beginning with # are ignored.
    """

    def __init__(self, filename: str | Path = "memory.txt"):
        self.filename = Path(filename)

    def store(self, key: str, value: str) -> None:
        """Store or update one memory item."""
        key = str(key).strip()
        value = str(value).strip()

        if not key:
            raise ValueError("Memory key cannot be empty.")

        records = self._load_all()
        records[key] = value
        self._save_all(records)

    def retrieve(self, key: str) -> Optional[str]:
        """Retrieve one value or return None when missing."""
        return self._load_all().get(str(key).strip())

    def all_items(self) -> Dict[str, str]:
        """Return all key-value memory items."""
        return self._load_all()

    def update(self, values: Dict[str, str]) -> None:
        """Store multiple memory items."""
        records = self._load_all()

        for key, value in values.items():
            key = str(key).strip()

            if not key:
                raise ValueError("Memory key cannot be empty.")

            records[key] = str(value).strip()

        self._save_all(records)

    def clear(self) -> None:
        """Remove all memory items from the file."""
        self._save_all({})

    def _load_all(self) -> Dict[str, str]:
        """Load key-value records from the text file."""
        records: Dict[str, str] = {}

        if not self.filename.exists():
            return records

        for line_number, raw_line in enumerate(
            self.filename.read_text(
                encoding="utf-8"
            ).splitlines(),
            start=1,
        ):
            line = raw_line.strip()

            if not line or line.startswith("#"):
                continue

            if "=" not in line:
                raise ValueError(
                    f"Invalid memory line {line_number} "
                    f"in {self.filename}: expected key=value"
                )

            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()

            if not key:
                raise ValueError(
                    f"Empty memory key on line {line_number} "
                    f"in {self.filename}"
                )

            records[key] = value

        return records

    def _save_all(self, records: Dict[str, str]) -> None:
        """Write all records to the memory file."""
        self.filename.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        lines = [
            f"{key}={value}"
            for key, value in records.items()
        ]

        content = "\n".join(lines)

        if content:
            content += "\n"

        self.filename.write_text(
            content,
            encoding="utf-8",
        )


def load_project_memory(
    memory_directory: str | Path = ".",
) -> Dict[str, Dict[str, str]]:
    """Load the primary UQTN memory files."""
    directory = Path(memory_directory)

    files = {
        "core": "core_memory.txt",
        "active": "active_state.txt",
        "delta": "session_delta.txt",
    }

    return {
        name: FileMemory(directory / filename).all_items()
        for name, filename in files.items()
    }


def main() -> None:
    """Run a local memory smoke test."""
    memory = FileMemory("core_memory.txt")

    print("UQTN / Zetari.AI File Memory")
    print("-" * 30)

    print(f"PROJECT: {memory.retrieve('PROJECT')}")
    print(f"IDENTIFIER: {memory.retrieve('IDENTIFIER')}")
    print(f"CORE_EQUATION: {memory.retrieve('CORE_EQUATION')}")

    print("\nAll stored items:")
    for key, value in memory.all_items().items():
        print(f"{key}={value}")


if __name__ == "__main__":
    main()