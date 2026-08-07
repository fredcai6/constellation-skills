# Project context

This project runs on the **constellation** skill suite (installed at `.claude/skills/`).

Engineering work here is not freeform: every bounded issue is run under the
appropriate constellation skill, and its workflow state is driven through the
checklist engine (`.claude/skills/constellation-workbench/scripts/checklist_engine.py`)
— work the engine never saw didn't happen. A delegated dispatch (no reachable
human) loads `constellation-commander-delegated` and runs the issue under it.
