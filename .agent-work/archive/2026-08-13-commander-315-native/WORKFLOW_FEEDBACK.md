# Workflow feedback — `commander-315-native`

The run stayed on the Commander/crew checklists and used MCP for every engine interaction. It did
not use the checklist-engine CLI. The cold recovery protocol worked: the same job files and
session were reclaimed, crew recovery was checked before dispatch, and existing results were
integrated instead of rerun.

The main improvisations were harness-facing. Native spine tools were unavailable to the already
running Codex host, so every door was driven through manual newline-delimited stdio JSON-RPC.
Claude hit its weekly quota before reviewer work, so the documented external backend was paired
with Codex implementer/reviewer agents. The mandated patch helper could not initialize in the
sibling worktree because of a bwrap loopback error; bounded apply-patch sessions from an escalated
worktree shell worked for the Commander, while crews used reversible git patches and verified
production hashes.

The strongest positive signal was independent review doing real work. The first follow-up was
green under tests that always supplied an absolute temporary root, but the reviewer exercised the
actual CLI defaults and found that `crew_cwd('.', Path('.'))` still returned a relative path. The
bounded repair and fresh re-review closed that gap. Another harness-only false red appeared when
the engine-owned suite inherited `SPINE_*` from the MCP door; exact environment reproduction made
the cause clear enough for a one-check Admiral-ratified amendment without a waiver.

Crew feedback also identified smaller instruction gaps: external launches supplied a parent and
an already-instantiated survey without binding the role's own spine, a third state not named by
the implementer skill; manual MCP envelopes were absent from handoffs; generic plan imperatives
still contained placeholders; generated map artifacts were required by the bar but omitted from
one handoff's allowed-file list; and re-review criteria cited prior check IDs without restating
their imperatives. These did not block the outcome, but they cost reconstruction and local
judgment. Each distinct observed event is captured in `episode-delta.json`.
