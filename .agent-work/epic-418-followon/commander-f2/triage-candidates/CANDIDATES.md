# Triage candidates — commander-f2

All `recommend-and-defer`. **Nothing here was filed as an issue**: no filing authority was
sought or granted this run, and the launch order routes cheap mid-wave finds to the Admiral
rather than having them implemented inside a wave under measurement.

## tc1 — `map_orient.py` cannot parse a generated code map (Admiral filed as #548)

`ANCHOR_RE` admits only `struct:`/`capability:`/`event:`/`constraint:`/`assumption:`/
`claim:`/`decision:` — the vocabulary of a hand-written architecture packet. A generated
code map contains none by construction, so every Commander in this epic runs
`DEGRADED-UNPARSEABLE` against a map that is present, complete and freshness-tested.

**The sharper half is the verdict string, not the parse.** `map_orient.py:447` returns the
literal `"content but no citable anchor id (unfilled template?)"`. That parenthetical is a
**guess about the file's state, printed inside a verdict**, and I repeated it one tier up as
an observation without opening the file. A tool that reports a defective world and a healthy
one alike, plus a plausible explanation that makes checking feel unnecessary.

## tc2 — the `notes-<n>.md` convention has no location, and the retirement guard is right (Admiral filed as #550)

`tests/test_retirement_guard.py::test_canon_is_clean` fires on any new **shipped** site
naming the episode store. The launch-order template names `notes-1.md` without naming a
directory, and prior runs put such files at the repo root. Mine went red with 6
`unapproved-store-mention` violations. **The guard must not be relaxed** — it exists because
a root-level file discussing `apply_episode_delta.py` is how the retired playbook comes back.
It is selective in the worst way: it fires precisely on runs that touch the episode store, so
the better a run behaves at closeout the likelier it trips. Resolved here by moving the
artifact into the run's own work area, not by widening a frozen census.

## tc3 — backticks in engine string arguments execute (Admiral filed as #551)

A reviewer put backticks around a command name inside a double-quoted `--finding`; the shell
substituted it and ran `code_map build`, rewriting a tracked file. It caught this itself,
reverted, and disclosed it. The engine's evidence verbs invite prose, prose about commands
invites backticks, every documented example uses double quotes, and double quotes do not
protect backticks in any shell we run. **The journal records the text after substitution, so
the record does not show what was typed.** A `--finding-file` was proposed, mirroring what
`gh pr create -F` already forced on this repo.

## tc4 — the code map stales on every test addition (#544)

Adding or removing a test moves a module's entity count and turns
`tests/test_code_map.py::MapTreeFreshnessTests` red. It bit **three times** in this one run,
the third after I had already been told to rebuild as part of committing. A generated,
committed, freshness-tested artifact with no rebuild hook is a trap for every gate that adds
a test.

## tc5 — `episode_capture.manifest_root()` doubles a path for a deeper nested work-id

Two crew members hit `\.agent-work/<epic>/<commander>/<epic>/<commander>/…` for a scratch
spine under an evidence directory with a `--work-id` passed anyway. The Admiral measured
this and it is a **documented scope boundary, not a #543 regression**: `manifest_root`'s
strip is conditional on the directory ending in the work-id, and the docstring says
explicitly that a checklist not sitting under its own work-id "is a different question than
this one, and guessing at it is how the doubled path was written in the first place."
Recorded against #546. It behaves badly at a boundary it honestly declined to guess at —
worth knowing before C launches with nested work-ids.

## tc6 — promote the identity rule into `docs/agents/*` or `docs/CHECKLIST_ENGINE_DESIGN.md`

`IDENTITY_TRADE.md` states a fleet-wide rule: *identity may be bound to a container only at
the granularity that container genuinely separates; a seam below it fails closed, or defers
to a per-call path where one exists.* It is currently a run artifact under `.agent-work/`.
Promoting an observation into `docs/agents/*` is **the human's call** under this repo's own
binding doctrine, so it is routed, not written. The second seam (`spine_rail.py`, #549) is
what makes it a rule rather than a trade.

## tc7 — the CLI arm is uninstrumented, so future DC5-style comparisons are asymmetric

g2 instrumented the door's own rejections and deliberately did not instrument the CLI: a CLI
shape rejection exits inside `argparse` **before** `load(path)` runs, so the engine does not
know which spine was meant and there is no run to attribute it to. The asymmetry is
structural, not budgetary — but it means a future measurement would compare an instrumented
door against an uninstrumented CLI. Recorded as a cost, not paid.

## tc8 — g3 remains open, and adoption is unverified on Windows (#553)

Deferred by Admiral ruling. `install_constellation.py` still has **zero** MCP references; a
real project-scope install during g4b shipped neither `.mcp.json` nor `mcp_spine_server.py`
(verified by `ls`, not assumed). The committed `.mcp.json` hardcodes `"command": "python3"` —
the defect #538/#540 fixed everywhere else, shipped in the one file adoption depends on, and
unresolvable on the owner's box where `py` is an extensionless `sh` wrapper PowerShell cannot
execute and `python` is not on PATH. **Adoption must not be reported as achieved on Windows.**

## tc9 — `evidence/g4b/run_arm_2.sh` overwrote arm 1's stderr file

`evidence/g4b/run_arm_2.sh:37` redirects arm 2's stderr to `"${DIR}/arm-mcp/record.err"` —
**arm 1's** directory — while its stdout correctly goes to `arm-mcp-2/record.jsonl`. The
file at `arm-mcp/record.err` therefore carries arm 2's stderr under arm 1's name (mtime
02:12, arm 2's run window; arm 1's own `record.jsonl` is 02:09), and `arm-mcp-2/` has no
`record.err` at all. Arm 1's stderr is gone and cannot be reconstructed.

**No claim depends on it.** Every count in `MEASUREMENT.md` and `RUN_SUMMARY.md` comes from
the `.jsonl` records, which are correctly separated per arm. This is recorded so a later
reader does not treat `arm-mcp/record.err` as arm 1 evidence, and so the copy-paste hazard in
the arm scripts (three near-identical files differing in one path each) is on the list rather
than in someone's memory.
