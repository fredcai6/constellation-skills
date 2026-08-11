## Current planning truth — material exception after wave 2

**The door is built, serves correctly, and does not launch where the owner works.** `initialize` returns `serverInfo`, `tools/list` returns all 7 tools, and a real `spine_status` call returns real engine content — so the server is sound. The defect is its launch line: `.mcp.json` hardcodes `"command": "python3"`, which resolves on neither the owner's Windows box nor anything without a `python3` on PATH, and `install_constellation.py` has zero MCP references so a fresh install never wires it.

**C (#421) does not launch, and its entry condition is restated as something checkable:** the door launches from a fresh install on Windows and POSIX, proven in CI — not "an agent drove it once on one platform". The previous transition recorded that condition as met; that was wrong and this record supersedes it.

**The current wave is one issue:** finish #542's installer criterion. Reuse the per-machine interpreter resolution the installer already carries from #539/#540, which hard-stops when nothing probes rather than stamping a known-broken name. No literal interpreter anywhere in the shipped path.

**Also unmeasured, and now forecast rather than claimed:** whether role-spine instructions *cause* adoption. All three acceptance arms loaded a corpus predating the edits and the accepting arm found the door through `ToolSearch`. That is recorded as unmeasured, not as a negative, and it needs a launchable door before it can be measured honestly.

**E (#423) is out of this epic** at the human's direction.
