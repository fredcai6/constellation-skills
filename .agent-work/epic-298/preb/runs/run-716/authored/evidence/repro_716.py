"""Reproduce issue #716 against the CANONICAL constellation-skills sources.

Read-only: imports the two scripts, exercises the two named parsers/matchers
with a nested work_id (`epic-659/665`), prints observed vs expected. Creates
nothing outside a tempdir.
"""
import sys, tempfile
from pathlib import Path

SCRIPTS = Path(r"C:\Programs\constellation-skills\scripts")
sys.path.insert(0, str(SCRIPTS))

import run_crew as RC
import verify_agent_feedback as VAF

WORK_ID = "epic-659/665"

# --- defect 1: session-name parse ------------------------------------------ #
name = RC.session_name(WORK_ID, "g1", "implementer", 1)
print(f"session_name          = {name}")
with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    reg = RC.registry_path(WORK_ID, root)
    reg.parent.mkdir(parents=True, exist_ok=True)
    RC.save_registry(reg, [{"session_name": name, "work_id": WORK_ID, "status": "running"}])
    print(f"registry written at   = {reg.relative_to(root)}")
    try:
        entries = RC.load_registry_for_resume(name, root)
    except Exception as exc:  # noqa: BLE001
        entries = f"RAISED {type(exc).__name__}: {exc}"
    print(f"load_registry_for_resume -> {entries}")
    print(f"  EXPECTED: the 1 entry above. DEFECT if []/raise.")

    # what work_id does the current parser think it is?
    parts = name.split("/")
    print(f"  parser takes parts[1] = {parts[1]!r}  (true work_id = {WORK_ID!r})")

# --- defect 2: archive-dir match ------------------------------------------- #
with tempfile.TemporaryDirectory() as td:
    agent_work = Path(td) / ".agent-work"
    # the layout the spine's `<date>-<work-id>` imperative produces verbatim
    pkg = agent_work / "archive" / f"2026-07-25-{WORK_ID}"
    pkg.mkdir(parents=True)
    print(f"\narchive package       = {pkg.relative_to(agent_work)}")
    found = VAF._current_run_archive_dirs(agent_work, WORK_ID)
    print(f"_current_run_archive_dirs -> {found}")
    print("  EXPECTED: the package above. DEFECT if [].")

    # control: slashless work_id still matches (back-compat baseline)
    ctl = agent_work / "archive" / "2026-07-25-issue-9"
    ctl.mkdir(parents=True)
    print(f"control (slashless)   -> {VAF._current_run_archive_dirs(agent_work, 'issue-9')}")

# --- adjacent: _entry_block prefix collision under nested ids --------------- #
text = "## 2026-07-25 - epic-659/665\n- a\n\n## 2026-07-26 - epic-659/670\n- b\n"
blk = VAF._entry_block(text, "epic-659")
print(f"\n_entry_block(text, 'epic-659') first line -> {blk.splitlines()[0]!r}")
print("  NOTE: a parent work_id substring-matches a CHILD's heading.")
