## Material exception — w2x-mcp-unproven

**The wave-2 transition recorded C's entry condition as met. It is not.**

What was measured: one dispatched agent drove one role spine to done through the door, on Linux, having found the tools via `ToolSearch` against `--allowedTools`. What was claimed from it: that agents now run the spine through the door, which was C's gate.

What is also true, and was known before the ruling:

- `.mcp.json` hardcodes `"command": "python3"`. The python.org Windows installer ships `python.exe` and `py`, not `python3.exe`, and App Execution Aliases route a bare `python3` to a Store stub. On the repo owner's own machine `py` is an extensionless `#!/bin/sh` wrapper PowerShell cannot execute and `python` is not on PATH. **The door does not launch there.**
- `install_constellation.py` has **zero** MCP references. A fresh install never wires the door at all.
- All three acceptance arms loaded a skills corpus predating the adoption edits, so **whether the role-spine instructions cause adoption is unmeasured** — the accepting arm found the door by tool discovery.

**The Admiral error is the ranking, not the measurement.** The owner asked *"with reinstall will we start driving through the mcp server?"* I classified that as a question rather than an instruction, deprioritised the installer criterion on that basis, then measured mid-wave that the answer was no, filed #553 saying so, and recorded `advance` anyway. The evidence that contradicted the ranking existed before the ruling was made.

**Decision: replan.** The current wave becomes making the door launchable and proving it on Windows CI — the door serves correctly once started, so the defect is the launch line, not the server. C returns to the forecast behind an entry condition stated as a property that can be checked: the door launches from a fresh install on Windows and POSIX, proven in CI.
