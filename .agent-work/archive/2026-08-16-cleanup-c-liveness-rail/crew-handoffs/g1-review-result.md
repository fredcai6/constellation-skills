# Review Result

## Assigned Gate
g1 (issue #599)

## Result
APPROVE

## Handoff compliance
The change does exactly what the handoff asked, within its allowed scope. `entry_liveness(entry, now, alive=None) -> "active"|"stale"|"unknown"` was added at `scripts/run_crew.py:264` and wired into `active_duplicate` (`:330`) so a `"stale"` verdict frees the launch slot (`continue`) while `"active"`/`"unknown"` still block (`return entry`) — fail-toward-active. Verified every close-criteria item by reading the function body directly, not the docstring:

1. `entry_liveness` returns exactly one of `"active"`, `"stale"`, `"unknown"` — confirmed, no fourth path.
2. Literal three buckets in order: pid truthy → `alive(pid)`; pid falsy AND `entry_backend(entry) == BACKEND_EXTERNAL` → heartbeat-age vs `HEARTBEAT_STALE_SECONDS`; else → `"unknown"` directly with no heartbeat lookup attempted (`test_liveness_legacy_bucket_no_pid_no_backend_is_unknown_no_heartbeat_lookup` pins this).
3. Bucket 3 does not reuse `recover_crews.classify_entry`'s `pid=None` mapping — `grep -n "recover_crews\|classify_entry" scripts/run_crew.py` shows zero import/call, only pre-existing comment mentions of the module name.
4. `active_duplicate`'s policy matches exactly: `"stale"` → `continue`; `"active"`/`"unknown"` → `return entry`.
5. No write path sets `abandoned`/`status: "abandoned"` anywhere in the diff — only `is_abandoned()` reads are used; the `"stale"` branch is a bare `continue`.
6. `HEARTBEAT_STALE_SECONDS = 28800` is a named module constant (`:52`) with an evidence-cited comment, not a magic number.
7. `git diff --stat cbd18faf~1 cbd18faf -- scripts/recover_crews.py` — empty, reproduced myself.
8. `git show cbd18faf --stat` — only `scripts/run_crew.py` and `tests/test_crew_launcher.py`.
9. `process_alive`'s own `def` block/docstring/body is untouched — `git show cbd18faf -- scripts/run_crew.py | grep -A2 "^-.*def process_alive"` returns nothing.

## Scope drift
None. Both files touched are inside allowed scope; the test file's changes are purely additive (a new `EntryLivenessTests` class plus the `timedelta` import it needs). `test_duplicate_active_lock_is_refused` (line 677) is byte-identical to before — its fixture (no `pid`/`backend` key) is exactly the bucket-3 case, and it still passes unmodified. `scripts/recover_crews.py`, `scripts/hooks/spine_rail.py`, and the other fenced files show zero diff.

## Evidence verdict
Required evidence is present and demonstrates the behavior; test mode is test-after (no TDD required for this change class, and the handoff/CREW_CONTEXT do not require it here) — satisfied.

Independently reproduced, not just trusted:
- `find . -name __pycache__ -type d -exec rm -rf {} + ; env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q tests/test_crew_launcher.py` → **181 passed in 0.60s**, matching the pasted evidence exactly.
- Cross-checked both numbers cited in the `HEARTBEAT_STALE_SECONDS` comment against the real archived registries named: (a) `.agent-work/archive/2026-08-15-epic-568-441/crew-runs.json`'s `constellation/epic-568-441/g1/implementer/attempt-1` entry — `started_at`/`last_heartbeat` both `2026-08-14T18:10:25.409092+00:00`, field-for-field identical to the test fixture `_external_phantom_entry`; (b) `.agent-work/archive/2026-08-15-epic-568-510/crew-runs.post-archive.json`'s `constellation/epic-568-510/g2-repair/commander/attempt-1` entry, `status: "completed"`, `started_at` → `completed_at` = 12602.96s, matching the comment's "~3h30m (12602s)" to the second. The 8h constant's justification is real measured data, not fabricated.
- **Adversarial mutation check**: temporarily replaced `active_duplicate`'s `if entry_liveness(entry, now, alive) == "stale": continue` with a bare `return entry` (always-block), reran the suite — `test_evidence_1_cli_dead_pid_frees_the_slot` and `test_evidence_3_external_phantom_past_8h_frees_the_slot` both failed exactly as expected (`AssertionError: ... is not None`). Restored the file (`git status --porcelain scripts/run_crew.py` empty afterward) and reran — 181 passed again. This proves the load-bearing tests are not vacuously green.

## Code/doc quality
Meets the inherited rules. `entry_liveness` is genuinely pure (only caller-supplied `now`/`alive`; the `alive = process_alive` line is a default-sentinel name-binding, not a call; `active_duplicate`'s own `datetime.now(timezone.utc)` is confined to its own `now=None` resolution). `now`/`alive` are keyword-only, so every existing positional caller (the CLI, `test_duplicate_active_lock_is_refused`) needs zero code changes. Naming/docstring conventions match the surrounding file (which itself favors dense rationale comments throughout — 96 docstrings in the module).

**Fowler refactoring pass** (`.agent-work/cleanup-c-liveness-rail/FOWLER_PASS.json`, `verify_fowler_pass.py` exit 0): all 12 baseline smells visited. 10 `absent`. 2 `overridden`, both with a logged repo standard + reason:
- **primitive-obsession** — `entry_liveness`/`active_duplicate` read `entry["pid"]`/`["last_heartbeat"]`/`["started_at"]` as raw dict fields. Overridden: this matches the module's pre-existing convention (every registry row is a plain dict round-tripped through JSON via `load_registry`/`save_registry`; `is_abandoned`, `entry_backend` do the same). A typed `Entry` class introduced only here would fragment one representation into two.
- **long-parameter-list** — `active_duplicate` grew from 5 to 7 params. Overridden: the 2 new ones are keyword-only, default to the real clock/process check, and mirror the `process_alive` test-injection-seam precedent already documented in this file (`:971`); keyword-only placement is also what the handoff's own zero-caller-change constraint required.
- 0 smells flagged.

## Map impact verdict
Map orientation is DEGRADED-UNPARSEABLE at baseline (zero authored map anchors corpus-wide, per the handoff) — no map artifact exists for this change to reconcile against or diverge from.
- **Evidence supports claimed change:** yes, per Evidence verdict above.
- **Constraints not violated:** yes — `process_alive` reused not modified; no-abandonment-by-inference honored (no write path found).
- **Notes match the diff:** yes — the implementer's Map Impact notes (structural placement, capability change, constraints touched) were checked directly against the file and match.
- **Decision candidates surfaced:** n/a — the three-bucket rule, 8h window, and fail-toward-active mapping were pre-decided in the handoff's Decision anchors; none needed re-derivation.
- **Durable context routed:** yes — see Out-of-scope observations below (re-flagged as `tc1` in the survey so it is not dropped at this gate boundary).

## Reconciliation check
No divergence from recorded architecture — there is no map artifact for this gate to reconcile against (DEGRADED-UNPARSEABLE, discharged per the handoff's own note).

## Blockers
- none

## Out-of-scope observations
- External-backend registry entries' `last_heartbeat` is written once at dispatch and never updated again (confirmed by inspecting `build_entry`'s external-backend construction). `HEARTBEAT_STALE_SECONDS` therefore really measures time-since-dispatch, not time-since-last-observed-life; a genuinely healthy long-running external crew nearing 8h will eventually misread as stale purely from age. Already named by the implementer's own `g1-implement-result.md`; re-flagged here as triage candidate `tc1` in the survey so it survives to Commander/Triage. Candidate: a periodic heartbeat-writer for external-backend entries. Not required for this gate — the handoff explicitly excluded building it.

## Workflow Feedback

- **Handoff gaps:** none of substance. The handoff was unusually complete — Decision anchors with `@grade` tags, exact archived-registry file paths for the required evidence (which let me independently re-verify the cited numbers rather than trust them), and explicit stop conditions.
- **Context rediscovered:** none — the handoff's Map Anchors and Required Evidence sections carried everything needed; no separate digging was required to locate the archived registries.
- **Instructions improvised around:** the dispatch stated "external backend — no MCP spine door bound to you, do not attempt spine_* tool calls." Env inspection confirmed `SPINE_FILE`/`SPINE_SESSION` were in fact bound, but to the parent Commander's own spine (`SPINE_SESSION=constellation/cleanup-c-liveness-rail/execute/commander`), not to this reviewer's own survey — exactly the "MCP door... who it is NOT for" case the workbench reference names. Per the skill's own instructions for "nothing bound to you," built and drove an own `review.json` survey through the CLI `checklist_engine.py` instead, at the path the handoff named (`.agent-work/cleanup-c-liveness-rail/g1-review/review.json`), claimed/released its own session lease under this reviewer's own session id.
- **What would have made this easier:** none beyond the note above — the handoff's evidence-item numbering (1-6) mapped cleanly onto the survey's own r-items, and having the exact archive file paths pre-named turned "verify the evidence is real" from a search task into a direct read-and-compare.

## Return status
complete
