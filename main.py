try:
    import memory  # type: ignore
except (ImportError, ModuleNotFoundError):
    memory = None

load_lines = getattr(memory, "load_lines", None) if memory else None
if callable(load_lines):
    try:
        print(load_lines())
    except Exception:
        print([])
else:
    print([])


def dump_memory(mem):
    fn = getattr(mem, "all_items", None)
    if callable(fn):
        try:
            return fn()
        except Exception:
            pass

    fn = getattr(mem, "items", None)
    if callable(fn):
        try:
            return fn()
        except Exception:
            pass

    return []

def build_memory_bridge():
    if memory is None:
        return {"core": None, "active": None, "delta": None}

    FileMemory = getattr(memory, "FileMemory", None)
    if not callable(FileMemory):
        return {"core": None, "active": None, "delta": None}

    core = FileMemory("core_memory.txt")
    active = FileMemory("active_state.txt")
    delta = FileMemory("session_delta.txt")

    return {
        "core": core,
        "active": active,
        "delta": delta
    }

def main():
    if memory is None:
        print("Error: memory module not available")
        return
    
    bridge = build_memory_bridge()
    print("CORE:", dump_memory(bridge["core"]))
    print("ACTIVE:", dump_memory(bridge["active"]))
    print("DELTA:", dump_memory(bridge["delta"]))

if __name__ == "__main__":
    main()