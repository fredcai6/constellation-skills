# scripts.checklist_engine
scripts/checklist_engine.py, 2739 lines, 25 holes

Workbench checklist engine: work one gated/survey plan through its gates.

The engine holds the canonical state; an agent transacts with it one step at a
time. It enforces *mechanism* (ordering, evidence shape, the rework cap, the
consolidation consistency guard) and never judges quality. See
docs/CHECKLIST_SCHEMA.md.

imports stdlib: __future__.annotations, argparse, copy, datetime.datetime, datetime.timedelta, datetime.timezone, hashlib, importlib.util, json, os, pathlib.Path, pathlib.PureWindowsPath, re, shutil, subprocess, sys
imports third-party: episode_capture.emit_step_manifest
imported by: none found

```python
GATED = 'gated'
SURVEY = 'survey'
STATUS_VALUES = ('pending', 'in-progress', 'blocked', 'complete', 'skipped')
TERMINAL = {'complete', 'skipped'}
DEFAULT_REWORK_CAP = 3
DEFAULT_LEASE_STALE_SECONDS = 1800
MUTATING_VERBS = {'start', 'advance', 'record', 'consolidate', 'skip', 'block', 'resume', 'reopen', 'app...
_gauge_reader = _load_gauge_reader()
RAIL_VERBS = {'claim', 'current', 'start', 'advance', 'attest', 'attach'}
_RAIL_STRINGS = {'early': "Work the engine never saw did not happen. Run the step's checks, then `attes...
_RAIL_CURRENT_MIDFLIGHT_POINTER = 'the ACTIVE line above'
_RECOVERY_TAIL = 'Do not edit the JSON — use the engine.'
_STATE_CONTRACT_VERSION = 1
_AMEND_ID_RE = re.compile('^[a-z0-9][a-z0-9-]*$')
```

- [_utf8_stdio](_utf8_stdio.md) function: Captured stdio on Windows falls back to cp1252; checklist text with
- [_load_gauge_reader](_load_gauge_reader.md) function: HOLE: no docstring
- [EngineError](EngineError.md) class: A refusal: the requested transition is not allowed. No exit-0.
  - [EngineError.__init__](EngineError.__init__.md) method: HOLE: no docstring
- [_now](_now.md) function: Current UTC time as an ISO-8601 string. The single module-level time
- [_parse_ts](_parse_ts.md) function: Parse an ISO-8601 timestamp, tolerating a trailing 'Z'. Returns a
- [lease_stale_seconds](lease_stale_seconds.md) function: HOLE: no docstring
- [load](load.md) function: HOLE: no docstring
- [save](save.md) function: HOLE: no docstring
- [load_config](load_config.md) function: Resolve config: inline `config` wins; else follow `config_ref` to a file
- [rework_cap](rework_cap.md) function: HOLE: no docstring
- [task](task.md) function: HOLE: no docstring
- [active_id](active_id.md) function: First item (in order) that is not yet terminal.
- [_rail_position](_rail_position.md) function: Derive the decision-point position for a gated checklist and the tokens its
- [_rail](_rail.md) function: Return the doctrine block to append at a decision point, or ``""`` when no
- [_rail_prefix](_rail_prefix.md) function: The doctrine rail as a FRONT-loaded prefix (#227 gate g3, items 2/4):
- [recovery_for](recovery_for.md) function: A recovery line naming a runnable exit command for a state-caused
- [_new_evidence_id](_new_evidence_id.md) function: HOLE: no docstring
- [_find_evidence](_find_evidence.md) function: Find an evidence item by id across ALL tasks' evidence lists. Evidence ids
- [_glob_to_regex](_glob_to_regex.md) function: Translate a path glob into an anchored regex. `**` matches across path
- [_glob_match](_glob_match.md) function: Match a POSIX-style path against a glob pattern with recursive `**`.
- [evaluate_git_change_policy](evaluate_git_change_policy.md) function: PURE policy evaluation. Returns a list of human-readable violations
- [_git](_git.md) function: HOLE: no docstring
- [repo_revision](repo_revision.md) function: The repo's HEAD commit and whether its working tree is dirty relative to it
- [_collect_changed_files](_collect_changed_files.md) function: Thin git collector: gather `{path, size, binary}` for the changed files.
- [_bash_candidates_from_git](_bash_candidates_from_git.md) function: Candidate bash.exe paths derived from a git executable path. Windows
- [_find_posix_shell](_find_posix_shell.md) function: Locate a POSIX shell to run `command` checks under: bash on Windows, sh on
- [_run_check_command](_run_check_command.md) function: Run a `command`-kind check. Route it through a POSIX shell when one is found
- [_check_condition](_check_condition.md) function: Verify one condition. command -> run it; artifact -> presence/match;
- [_is_stale](_is_stale.md) function: A lease is stale when its `last_heartbeat` is older than the configured
- [_active_lease](_active_lease.md) function: The lease iff it is present and `status: active`; else None. A released
- [_refresh_owner_heartbeat](_refresh_owner_heartbeat.md) function: Stamp liveness: if `session_id` owns the active lease, advance its
- [require_session](require_session.md) function: The actor-authority gate. Mutating verbs are session-gated only ONCE an
- [claim](claim.md) function: Claim ownership of the checklist for `session_id`.
- [heartbeat](heartbeat.md) function: Refresh the active lease's `last_heartbeat`. Only the owning session may
- [release](release.md) function: Close the lease (`status: released`). Only the owning session may release,
- [_lease_line](_lease_line.md) function: Human-readable active-lease summary for `current`, or None if no lease.
- [_append_why](_append_why.md) function: Append one why-record to the top-level append-only `why_trail` and return
- [_append_reopen_marker](_append_reopen_marker.md) function: Append a reopen-marker to `why_trail`: the append-only way a `reopen`
- [_latest_why_record](_latest_why_record.md) function: The live why-record: the newest `why_trail` entry that is a real (non-
- [_digest](_digest.md) function: The live digest text: the latest non-mechanical, non-superseded `why`, or
- [has_pending_refresh_request](has_pending_refresh_request.md) function: Pure predicate: True iff a pending `refresh-request` targets `gate`.
- [_why_suffix](_why_suffix.md) function: The why-capture lines appended to `current`: a `DIGEST:` line carrying the
- [_gauge_path](_gauge_path.md) function: The gauge file for this checklist: `.agent-work/<work_id>/gauge.json`, a
- [_read_gauge](_read_gauge.md) function: Read a fresh `Reading` for this checklist, or None. Fail-safe: an absent
- [_refresh_attach_hint](_refresh_attach_hint.md) function: The exact `attach` command that raises a refresh-request for `gate` — the
- [_uncalibrated_advisory](_uncalibrated_advisory.md) function: A visible notice that the context governor is OFF for this run because
- [_format_age](_format_age.md) function: Render a timedelta as whole seconds/minutes/hours — pure arithmetic and
- [_skip_reason_advisory](_skip_reason_advisory.md) function: A visible notice that the writer hook POSITIVELY LOCALIZED why no
- [_stale_record_advisory](_stale_record_advisory.md) function: When `read()` itself rejected the gauge file at this path (e.g. it is
- [_no_reading_advisory](_no_reading_advisory.md) function: Dispatch across every localizable "why is there no reading" cause, in
- [_trip_advisory](_trip_advisory.md) function: The Trip advisory suffix for the read-only `current` at a gate boundary
- [_trip_hard_gate](_trip_hard_gate.md) function: Trip HARD backstop at the `advance` gate boundary: REFUSE to advance when
- [_condition_kind](_condition_kind.md) function: The condition's check kind for display: the literal `check.kind`, or
- [_condition_open](_condition_open.md) function: True iff the condition is NOT (yet) recorded as satisfied. Reads the
- [_condition_view](_condition_view.md) function: HOLE: no docstring
- [_attestable](_attestable.md) function: `attest` accepts a qualitative (`check: null`) condition unconditionally,
- [_blocking_conditions](_blocking_conditions.md) function: The subset of `conds` that WILL make `start()`/`advance()` refuse right
- [_next_verbs](_next_verbs.md) function: Legal-from-here move templates for the active task, hand-derived from
- [state](state.md) function: Pure state projection: `cl -> StateView`. Read-only — see the INV-2
- [_anchor_category_items](_anchor_category_items.md) function: Normalize one `anchors` dict category's value to a list of strings.
- [_render_anchor_lines](_render_anchor_lines.md) function: Format the `anchors` field for display. Three shapes appear in the
- [render_human](render_human.md) function: Human adapter: format a StateView as the text agents read from
- [current](current.md) function: HOLE: no docstring
- [start](start.md) function: HOLE: no docstring
- [advance](advance.md) function: HOLE: no docstring
- [record](record.md) function: HOLE: no docstring
- [consolidate](consolidate.md) function: HOLE: no docstring
- [skip](skip.md) function: HOLE: no docstring
- [block](block.md) function: HOLE: no docstring
- [resume](resume.md) function: Move a resolved `block` forward: return a blocked gate to the status it held
- [_reset_conditions](_reset_conditions.md) function: Reset each condition to unsatisfied and drop the markers that would let a
- [_supersede_evidence](_supersede_evidence.md) function: Mark every evidence item on task `t` superseded by a reopen of `iid`.
- [reopen](reopen.md) function: Reopen a complete gate for rework. Increments `rework_count`, escalates
- [_build_amend_task](_build_amend_task.md) function: Build a full pending task from an `add` op, mirroring `append()`'s shape.
- [amend](amend.md) function: Intentional mid-stream re-planning of a GATED checklist. Apply a delta of
  - [amend._floor](amend._floor.md) method: 1 + index of the last non-pending (frozen) gate; 0 if none. A new gate
- [append](append.md) function: HOLE: no docstring
- [attest](attest.md) function: Satisfy a condition by attestation.
- [waive](waive.md) function: Human override: explicitly satisfy a condition by waiver, auditable.
- [attach](attach.md) function: HOLE: no docstring
- [flag_candidate](flag_candidate.md) function: HOLE: no docstring
- [parse_args](parse_args.md) function: HOLE: no docstring
  - [parse_args.add_session](parse_args.add_session.md) method: HOLE: no docstring
- [build_payload](build_payload.md) function: Assemble an attach payload without forcing JSON through the shell.
- [dispatch](dispatch.md) function: HOLE: no docstring
- [_run_verb](_run_verb.md) function: Execute a mutating verb and return its message, or raise EngineError if the
- [journal_path](journal_path.md) function: The journal sidecar for a spine file: ``<spine>.journal`` (so
- [_all_evidence_ids](_all_evidence_ids.md) function: HOLE: no docstring
- [_journal_hash](_journal_hash.md) function: SHA-256 over the entry's canonical (sorted, hash-excluded) JSON. The
- [_read_journal_tail](_read_journal_tail.md) function: (next seq, last hash) for an existing journal, or (1, "") when absent/empty.
- [append_journal_entry](append_journal_entry.md) function: Append one hash-chained line to the spine's journal for a successful
- [main](main.md) function: HOLE: no docstring
