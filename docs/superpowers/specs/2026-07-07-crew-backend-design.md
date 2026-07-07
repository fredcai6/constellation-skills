# Pluggable crew-launch backend

Status: design for build · 2026-07-07 · issue #53

## Context

`run-crew-cli-launcher-misfit` (f1Brainz, 10 recurrences, recurrence-debt): `scripts/run_crew.py` was
written for a headless `claude` CLI that does not exist inside the Agent-tool harness. So every fleet running
under that harness re-derives the same workaround by hand — dispatch the implementer/reviewer as an in-process
Agent-tool subagent, then reach for only the wrapper's *durable* properties (a registry record, the
duplicate-guard, exists-AND-fresh verification).

The wrapper already grew a second code path for this — `--dispatch external`
(`record_external_attempt` + `verify_external_result`) — alongside the original CLI-spawn path
(`launch_crew` / `resume_crew`). The two paths share the pure helpers (`session_name`, `run_log_paths`,
`_relativize`, `result_fresh`, `result_exists`) but are **not unified behind one interface**: they are
parallel functions selected by a `--dispatch` flag, and the entry-construction + finalize-from-exit-code
logic is near-duplicated across `launch_crew`, `resume_crew`, and `record_external_attempt`.

**Ratified direction** (human, wave-2 checkpoint of epic 20260706-dogfood-audit, over the cheaper
formalize-external-dispatch-only option): build a **true pluggable backend abstraction** — a crew-launch
backend interface with exactly two implementations behind ONE result contract.

## Decisions

1. **Two backends, one contract, no third.** A `CrewBackend` interface with exactly two concrete
   implementations — `CliBackend` (spawn a headless `claude` CLI subprocess) and `ExternalBackend`
   (record-only; the crew is dispatched out-of-band as an Agent-tool subagent). No speculative third backend;
   the interface is proven by exactly these two real implementations (pre-ruling).

2. **The result contract is backend-invariant.** Every backend honors the same four durable properties:
   (a) a durable `crew-runs.json` entry recorded *before/at* dispatch; (b) the duplicate-guard on an active
   `work-id/gate/role/worktree` lock; (c) result verification that is **exists-AND-fresh** — the single
   `result_fresh(result, root, since)` from PR #63, judged against the entry's `started_at`, reused verbatim,
   never forked; (d) deterministic stdout/stderr/result path layout. A backend may *dispatch* differently but
   may never weaken this contract.

3. **One `finalize_from_exit_code` helper.** The near-duplicate "set completed_at / last_heartbeat / status /
   exit_code / result_present / result_fresh from (child exit code, result freshness since dispatch)" tail —
   currently copy-pasted across `launch_crew`, `resume_crew`, and (in reduced form) `verify_external_result`
   — is extracted into ONE helper both backends call. Entry *construction* is likewise consolidated into one
   `build_entry(...)`. This is the consolidation the wave-1 triage candidate named (finalize logic shared by
   launch_crew / resume_crew / record_external_attempt).

4. **Backend selection: explicit override wins, else auto-detect.** A pure
   `select_backend(explicit, *, launcher, which=shutil.which) -> CrewBackend`:
   - `explicit in {"cli","external"}` → that backend (explicit override always wins);
   - `explicit in {None, "auto"}` → **auto-detect**: `which(launcher)` finds the CLI on PATH → `cli`
     available → choose `cli`; else choose `external`.

   Auto-detection is first-class and directly tested. The CLI wires it **backward-compatibly** (Decision 5).

5. **Backward compatibility (hard pre-ruling).** Existing `--dispatch {spawn,external}` invocations and every
   already-recorded `crew-runs.json` entry keep working, byte-for-byte:
   - `--dispatch` is retained as the legacy selector and keeps its default `spawn`. `spawn` maps to the `cli`
     backend, `external` maps to the `external` backend. So an existing call with no new flag resolves to the
     exact same backend it does today (default `spawn` → `cli`; explicit `--dispatch external` → `external`).
   - A new `--backend {auto,cli,external}` flag is the canonical selector. When given it wins over `--dispatch`
     (explicit override). `--backend auto` opts into auto-detection. When `--backend` is omitted the CLI
     resolves the backend from `--dispatch` (never silently auto-detecting), so no existing invocation changes
     behavior.
   - Recorded entries: new entries carry a `backend` field (`"cli"|"external"`). Legacy entries without it are
     inferred — `dispatch == "external"` → external, else cli. External entries keep their existing
     `dispatch: "external"` marker so today's tooling and records still parse.

6. **Recovery is backend-invariant in classification, backend-specific in action** (launch-order pre-ruling:
   "recovery may be 'report unrecoverable, relaunch' where the harness can't resume"). `recover_crews.py`
   classification stays uniform — it already judges each entry from status + pid-liveness + exists-AND-fresh
   result (`_default_result_present` uses `result_fresh`), which is backend-agnostic. The *resume action*
   differs and the report says which applies:
   - **CLI backend** — `resume()` relaunches the subprocess with the stored session/handoff and finalizes
     (today's `resume_crew`).
   - **External backend** — a dispatching agent cannot be resumed by the wrapper: in-process Agent-tool
     teammates cannot spawn background subagents, so external dispatch is **synchronous** and recovery is
     out-of-band. `resume()` reports **unrecoverable-by-wrapper** with the recorded guidance: SendMessage to
     the crew's `agentId` to resume it in place (skills/_shared/windows.md §2), else `--abandon … --relaunch`.
     This asymmetry is pre-authorized by the launch order, so it forces no Admiral float; the uniform
     *contract* (a recoverable/unrecoverable signal + exists-AND-fresh verification) still holds.

## Interface

```python
class CrewBackend:                       # base/Protocol; name in {"cli","external"}
    name: str
    def dispatch(self, spec, *, root, entries) -> tuple[int | None, dict]:
        """Record the durable entry (running) BEFORE work. cli: spawn subprocess
        then finalize_from_exit_code -> (exit_code, entry). external: record-only,
        no subprocess -> (None, entry); caller verifies later."""
    def verify(self, entries, session, *, root) -> tuple[bool, dict]:
        """exists-AND-fresh against the entry's started_at; finalize to completed
        on fresh, else leave running. Uniform across backends."""
    def resume(self, session, *, root, entries) -> tuple[int, dict]:
        """cli: relaunch subprocess + finalize. external: unrecoverable-by-wrapper
        (raise CrewLaunchError guiding SendMessage-to-agentId / abandon+relaunch)."""
```

Shared module-level helpers stay pure and are reused by both backends (no forking): `build_entry`,
`finalize_from_exit_code`, `session_name`, `run_log_paths`, `_relativize`, `result_exists`, `result_fresh`,
`active_duplicate`, `next_attempt`, registry I/O. `launch_process` remains the single subprocess seam
(monkeypatched in tests); `ExternalBackend` never touches it.

## Build slices

- **g2 — abstraction core (pure refactor + consolidation).** Introduce `CrewBackend`, `CliBackend`,
  `ExternalBackend`, `build_entry`, and `finalize_from_exit_code`. Re-express `launch_crew` / `resume_crew` /
  `record_external_attempt` / `verify_external_result` on top of the backends (kept as thin wrappers for
  backward compat, or the CLI calls backends directly). No new user-facing selection surface. **All existing
  behavior and tests stay green** — this slice changes structure, not behavior.
- **g3 — selection + recover uniformity + tests.** Add `select_backend` + the `--backend {auto,cli,external}`
  flag (Decisions 4–5); make `recover_crews.py` annotate each entry's backend-specific resume action while
  keeping classification uniform; add tests for selection precedence (explicit override vs auto-detect on
  PATH presence/absence) and the backend-invariant result contract.

## Out of scope

No third backend. No change to `checklist_engine.py`, gate advancement, or git integration — the wrapper stays
the process/launch layer only. The commander-skill crew-dispatch doctrine lines are updated only to name the
pluggable backend (this run's file ownership), not the reconcile/context/archive or closeout lines.
