# Problem statement — cmdr-567-b (#432 ExternalBackend mtime-only verify)

Reconciled against `LAUNCH_ORDER:Mission` (delegated mode, no reachable human).

## What's asked

Make it impossible for a dispatched role that drove no spine at all to return a clean
success, and delete the mtime-only verification path on the ExternalBackend dispatch
path (#432).

## Code read this step

`scripts/run_crew.py` (the ExternalBackend dispatch path, sole-owned this wave):

- `CrewBackend.verify()` (base, ~line 1475) is the ONLY implementation that runs for an
  externally-dispatched crew (`ExternalBackend` does not override it; `verify_external_result`
  is a thin wrapper over `ExternalBackend().verify(...)`). It checks `result_exists` +
  `result_fresh` — filesystem mtime at/after dispatch — and nothing else. A crew that writes
  only its result artifact (e.g. `RETURN.md`) and never drives any engine-gated checklist
  passes this check exactly as well as one that drove a spine to completion. This is the
  mtime-only path named in #432/#567.
- `ExternalBackend.dispatch()` (~line 1671) currently **refuses `--spine`** outright: "binding
  is impossible by construction when nothing is spawned." True for *binding* (no child process,
  no environment) — but conflates binding with *recording a verification target*, which is not
  impossible.
- The CLI backend already has the tool needed to fix this: `spine_terminal()` (~line 506) reads
  a checklist file and reports whether the engine ever reached a terminal state on it (every
  item `complete`/`skipped`, plus a recorded verdict for a survey). `finalize_from_exit_code`
  already uses it to *rescue* a CLI dispatch's verdict when a bound spine finished but the result
  file didn't show up. Nothing today reuses it on the external path.
- Confirmed the vulnerability against the **shipped path** (no fixture): the existing test
  `test_verify_result_absent_then_present_marks_completed` — using `RC.main`, the CLI's own
  entrypoint — dispatches external, writes ONLY the result artifact (no spine touched at all),
  and asserts `--verify-result` returns 0 / status `completed`. That is #432, reproduced. This
  is my red-proof base; I will add a dedicated red-proof spelling out the spine-never-driven
  scenario explicitly before green-proofing the fix.

## Refuse or report (`decision:refuse-or-report-is-yours-to-settle`)

Both, split by what evidence the caller supplies:

- **Refuse is possible and is what I am building**, when the caller names a verification
  target: extend `ExternalBackend` to *accept* `--spine <path>` (still never bound — nothing
  spawns, that half of the refusal's reasoning stands) and require `verify()` to see BOTH the
  result fresh AND the named spine `spine_terminal` before marking `completed`. This is a real,
  exercisable refusal on the shipped path (`--verify-result` exits 1, prints why), not
  aspirational.
- **Report is the honest fallback** for a dispatch that never named a verification target in
  the first place (today, that's every existing external caller, since `--spine` was always
  refused before this fix) — the wrapper genuinely has no chokepoint to refuse an external crew
  it was told nothing about, per #559's note. For that case the deliverable is loud,
  non-silent detection: a WARNING on every mtime-only "completed" verdict, plus a new
  `spine_verified` field (`null`) recorded on the entry, so the gap is visible in the durable
  record rather than dressed up as clean.

## Lane-A interaction

`decision:refuse-or-report` and the residual both note "Agent-tool dispatch has no engine
chokepoint to refuse at" and lane A's finding that no verb today lets a role bind its own
spine through the door on this path. That is exactly why refusal can only be as strong as
the caller's own honesty in naming `--spine`: even after my fix, a caller that omits it is
never *forced* to supply one (I do not own `checklist_engine.py`/`mcp_spine_server.py`, so I
cannot mint or bind anything there). My check would NOT hard-refuse an agent that was
structurally unable to reach its own spine and so never named one — it would report,
loudly, rather than block. That is the honest scope boundary of a fix confined to
`run_crew.py`.

## Deletion (`decision:net-deletion`)

The mtime-only path survives for the *no-spine-named* case (can't refuse without evidence),
but it is deleted as a **silent** clean-success path: every mtime-only completion now carries
a printed warning and a `spine_verified: null` record. Deleted outright: the ExternalBackend's
blanket refusal of `--spine`, which was the actual mechanism blocking the stronger refuse-path
from ever existing.

## Scope check against fences

- No changes to `scripts/checklist_engine.py` or `scripts/mcp_spine_server.py` — `spine_terminal`
  is only read (already imported/used), never edited.
- Touches only `scripts/run_crew.py` and `tests/test_crew_launcher.py` — sole-owned this wave.
