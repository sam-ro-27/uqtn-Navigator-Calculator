import abc
from pathlib import Path


class Memory(abc.ABC):
    @abc.abstractmethod
    def store(self, key, value):
        pass

    @abc.abstractmethod
    def retrieve(self, key):
        pass


class FileMemory(Memory):
    def __init__(self, filename="memory.txt"):
        self.filename = Path(filename)

    def store(self, key, value):
        records = self._load_all()
        records[key] = value
        self._save_all(records)

    def retrieve(self, key):
        records = self._load_all()
        return records.get(key, None)

    def _load_all(self):
        records = {}
        if self.filename.exists():
            for line in self.filename.read_text(encoding="utf-8").splitlines():
                if "=" in line:
                    k, v = line.split("=", 1)
                    records[k] = v
        return records

    def _save_all(self, records):
        lines = [f"{k}={v}" for k, v in records.items()]
        self.filename.write_text("\n".join(lines), encoding="utf-8")

def all_items(self):
    return self._load_all()


def main():
    memory = FileMemory("core_memory.txt")
    print(memory.retrieve("PROJECT"))
    print(memory.retrieve("IDENTIFIER"))
    print(memory.retrieve("CORE_EQUATION"))
if __name__ == "__main__":
    main()