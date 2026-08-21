from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
from pathlib import Path


worktree = Path("/tmp/constellation-20260820-636")
sys.path.insert(0, str(worktree / "scripts"))
spec = importlib.util.spec_from_file_location("review_run_crew_636", worktree / "scripts" / "run_crew.py")
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

identity = "constellation/issue-636/gate/implementer/attempt-1"
disk_y = {
    "session_name": identity,
    "crew_id": identity,
    "worktree": "/worktree/y",
    "marker": "Y",
    "status": "running",
}
seed_x = {
    "session_name": identity,
    "crew_id": identity,
    "worktree": "/worktree/x",
    "marker": "X",
    "status": "running",
}

with tempfile.TemporaryDirectory() as tmp:
    registry = Path(tmp) / "crew-runs.json"
    registry.write_text(json.dumps([disk_y]) + "\n", encoding="utf-8", newline="\n")

    def complete(entry: dict) -> None:
        entry["status"] = "completed"

    _, chosen, _ = module.mutate_registry_entry(registry, identity, complete, seed=seed_x)
    persisted = module.load_registry(registry)

print("chosen_marker=", chosen["marker"])
print("persisted=", [(entry["marker"], entry["worktree"], entry["status"]) for entry in persisted])
assert chosen["marker"] == "X", "transaction mutated same-session entry in wrong worktree"
assert len(persisted) == 2
