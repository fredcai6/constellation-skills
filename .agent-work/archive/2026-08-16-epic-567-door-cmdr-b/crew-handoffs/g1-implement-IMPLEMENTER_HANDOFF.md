# Implementer Handoff

## Gate
g1

## Task
Close #432 on the ExternalBackend crew-dispatch path in `scripts/run_crew.py`: a crew that
writes only a fresh result artifact and never drives any engine-gated checklist must no
longer verify as a clean `completed` success — **by default**, not only when a caller
happens to opt in to a stronger check. This handoff supersedes an earlier draft; a cold
plan critic found the first design left the dominant case (no spine target known) as a
silent-ish clean pass, missing the mission's own bar. The design below is revised to fix
that. Read the whole handoff before starting — the ordering/polarity below is easy to get
backwards.

### The three changes, in `scripts/run_crew.py`

**1. `ExternalBackend.dispatch()`** (~line 1671): stop refusing `--spine`. Accept it,
record it on the entry (the `spine=` param is already threaded through
`record_external_attempt`/`CrewSpec`/`build_entry` — nothing to add there). `--spine` here
is **verification-only**: still never bound into an environment (nothing spawns, so
nothing can be bound) — keep that half of the existing reasoning, drop only the refusal.
Keep `_require_handoff` unconditional (external always needs a handoff, spine or not —
unchanged). Rewrite the class docstring and the "UNBOUND MCP door" warning: they currently
say `--spine` is refused; that becomes false.

**2. `ExternalBackend.verify()` — new OVERRIDE, not a `CrewBackend` base-class change.**
`CliBackend` never calls `.verify()` operationally (it uses `finalize_from_exit_code`
instead — confirm this with a grep before relying on it, per Constraints). Leave
`CrewBackend.verify()` exactly as-is. Add `def verify(...)` on `ExternalBackend` that:

- Reads `spine = entry.get("spine")` — **never `entry["spine"]`**; some fixtures in the
  test suite build entry dicts with no `"spine"` key at all, not `None`.
- Computes `result_ok`/`present` from `result_exists`/`result_fresh` **only when
  `entry.get("result") is not None`** — a spine-only external dispatch (`result=None`,
  `spine=<path>`, legal per `CrewSpec.__post_init__`, newly REACHABLE on this backend
  because step 1 stops refusing `--spine`) must never call `result_exists(None, root)` /
  `result_fresh(None, ...)` (both crash on `Path(None)`). When `result is None`, treat
  `present = False`, `result_ok` as not applicable — completion is judged solely on the
  spine below.
- Takes two NEW optional parameters (threaded from new CLI flags on `--verify-result`,
  see change 3): `verify_spine: str | None` and `accept_mtime_only_risk: str | None` (the
  reason string, or `None`). `effective_spine = verify_spine if verify_spine is not None
  else spine` — the verify-time flag wins when both are given (the dispatcher usually only
  learns the crew's real plan/spine path after it returns, so verify-time is the more
  reliable source; dispatch-time `--spine` stays useful for the rarer case where the path
  is genuinely known upfront, e.g. a `spine_open`-minted sub-dispatch).
- **Verdict logic** (this is the part the critic found wrong in the first draft — read
  carefully):
  ```
  if effective_spine is not None:
      drove = spine_terminal(effective_spine, root)      # already imported; read-only reuse
      entry["spine_verified"] = drove
      fresh = drove and (result_ok if entry.get("result") is not None else True)
      # AND, never rescue/OR: a fresh result must never excuse an undriven spine.
  elif accept_mtime_only_risk is not None:
      entry["spine_verified"] = None
      entry["mtime_only_risk_accepted"] = {"reason": accept_mtime_only_risk, "at": <now, ISO>}
      fresh = result_ok        # result must exist for this branch to be reachable at all --
                                # see CrewSpec.__post_init__: result=None requires spine given,
                                # and this branch only runs when effective_spine IS None.
  else:
      # DEFAULT: no spine evidence, no explicit accepted risk -- REFUSE. This is the fix.
      entry["spine_verified"] = False
      fresh = False
  ```
  Note the polarity: the OLD draft made the no-evidence case default to mtime-only PASS
  with a warning. The NEW default is REFUSE. The escape hatch
  (`accept_mtime_only_risk`) is what makes today's mtime-only-pass behavior still
  *reachable*, but only as an explicit, reasoned, recorded choice — never the default.
- On the `accept_mtime_only_risk` branch reaching `fresh=True`: print the acceptance to
  **BOTH stdout and stderr** (not stderr-only — a caller that only captures stdout, e.g.
  piping to a log, must not miss this). Include the word `RISK` and the reason verbatim.
- Sets `entry["result_present"]`/`entry["result_fresh"]` from whatever was actually
  computed (False/False when `result is None`), same as today's shape.
- On `fresh`: mark `completed` (`status`, `completed_at`, `last_heartbeat`) exactly as the
  base class does. Otherwise leave `running` (unchanged — the duplicate-guard must keep
  holding).
- Saves the registry, returns `(fresh, entry)` — same signature/contract as the base.

**3. CLI wiring** (`build_parser`/`main`, ~line 1901/1991):
- Add `--verify-spine PATH` (help: "verify this checklist file reached a terminal state,
  checked independently of any --spine given at dispatch — use when the crew's actual
  plan/spine path was only learned after it returned").
- Add `--accept-mtime-only-risk REASON` (help: "explicit, recorded override: accept a
  fresh result artifact alone as completion when no spine target is available to check —
  required reason, printed loudly, never silent; see #432").
- In the `args.verify_result` branch: pass both new args through to
  `ExternalBackend().verify(...)` (or whatever wrapper you route through — keep
  `verify_external_result`'s existing signature working for callers that don't need the
  new flags, e.g. via new optional kwargs with `None` defaults, back-compat).
- **New refusal message**, distinguishable from the existing STALE/absent ones, checked
  **before** falling back to those: when `entry.get("spine_verified") is False`
  (evidence was named but not terminal) OR the verdict hit the new bare "no evidence, no
  override" default branch, print a `REFUSED:` line naming which case it is (spine never
  reached terminal, naming the path; vs. no spine evidence and no
  `--accept-mtime-only-risk` given, naming both flags as the way forward) and cite #432 in
  the "no evidence" message specifically.

## Protected Intent
A dispatched role that drove no spine at all must never read as an unqualified clean
success on the ExternalBackend path **by default**. The old mtime-only pass must still be
*reachable* for a genuinely unavoidable case, but only as a loud, reasoned, recorded
choice — never silent, never the default.

## Test Mode
TDD required. `decision:the-check-must-be-able-to-fail` / `decision:test-the-shipped-path`
(both settled/doctrine this wave): every new assertion is proven red against the shipped
`RC.main` entrypoint before it is proven green.

## Close Criteria
- `ExternalBackend.dispatch()` accepts `--spine`. `test_external_dispatch_refuses_spine`
  (currently asserting the old refusal) is **rewritten** to assert accept-and-record —
  name this explicitly as an intentional scenario change, not scope creep.
- **Red-proof, default-refuse (the core fix):** dispatch external with NO `--spine`, write
  only a fresh result artifact, call `--verify-result <session>` with neither
  `--verify-spine` nor `--accept-mtime-only-risk` — via `RC.main` — must now REFUSE (exit
  1). Show this failing against pre-fix code (today's behavior returns 0/`completed` —
  this is `test_verify_result_absent_then_present_marks_completed`'s own scenario; that
  existing test's final assertion (`code_present == 0`) is now WRONG under the new
  contract and must be **rewritten** — name this explicitly, this is the single most
  important test change in this gate).
- **Red-proof, named-spine-not-terminal:** dispatch external with `--spine <path>` naming a
  spine file that exists but was never advanced past `init` (mirrors #432's actual
  evidence). Fresh result written. `--verify-result` must REFUSE.
- **Green-proof, named-spine-terminal:** same setup, spine driven to a genuinely terminal
  state (see `spine_terminal`'s own docstring at ~line 506 for what "terminal" requires —
  a minimal hand-built terminal-shaped fixture is fine, does not need the real engine).
  `--verify-result` must report `completed`.
- **Green-proof, verify-time override:** dispatch with NO `--spine`; at verify time pass
  `--verify-spine <path>` naming a spine driven to terminal by then — must report
  `completed`, proving the verify-time flag is consulted independently of dispatch-time
  state.
- **Green-proof, explicit accepted risk:** dispatch with NO `--spine`; verify with
  `--accept-mtime-only-risk "reason text"` and a fresh result — must report `completed`,
  and the printed output (capture BOTH stdout and stderr) must contain the reason text and
  the word `RISK`. Registry entry carries `mtime_only_risk_accepted`.
- **Spine-only external dispatch, no crash:** `result=None`, `--spine <path>` given at
  dispatch, driven to terminal — `--verify-result` (no result artifact involved at all)
  reports `completed`. Also prove the pre-guard version would have crashed (or reason
  about it in `IMPLEMENTER_RESULT` if a literal pre-fix repro is impractical) — this is
  the crash the critic flagged; show the guard actually prevents it.
- `test_verify_is_uniform_across_backends` and
  `BackendInvariantContractTests.test_both_backends_verify_exists_and_fresh_identically`
  currently assert `CliBackend().verify()` and `ExternalBackend().verify()` behave
  identically with no spine evidence given. That is now **intentionally false** — CLI
  keeps the old mtime-only base-class behavior (`CliBackend` never calls `.verify()`
  operationally in production, but the test still exercises the shared method directly);
  `ExternalBackend.verify()` now default-refuses without evidence. **Rewrite both tests**
  to assert the CLI side unchanged and the external side now refusing by default (or add a
  new escape param confirming the override path also brings it back to `completed`) — name
  this divergence explicitly in `IMPLEMENTER_RESULT` as an intentional narrowing of the
  prior "backend-invariant verify" contract (`docs/superpowers/specs/
  2026-07-07-crew-backend-design.md` Decision 2), justified by #432 evidence; do not
  silently delete the old assertions without saying so.
- Full suite green except the tests named above as intentional rewrites (list every one by
  name in `IMPLEMENTER_RESULT`).

## Allowed Scope
- `scripts/run_crew.py`
- `tests/test_crew_launcher.py` — pre-authorized to add new tests and to rewrite the named
  tests above (their old scenarios are exactly what this change now forbids/changes).

## Specific Exclusions
- `scripts/checklist_engine.py` and `scripts/mcp_spine_server.py` — **fenced, lane A this
  wave**. Read-only reuse of already-imported `checklist_engine` functions is fine (as
  `spine_terminal` already does). If the fix genuinely needs an edit inside either file,
  STOP and report — hard stop condition.
- `CliBackend`'s own dispatch/resume path and `finalize_from_exit_code`'s OR/rescue
  semantics are untouched — out of scope.
- Do not make `--spine` mandatory at **dispatch** time (floated to the Admiral separately,
  see MISSION_FRAME.md decision pressure) — the verify-time default-refuse above is this
  gate's actual mechanism, not a dispatch-time requirement.

## Constraints
- `ExternalBackend.verify()` is an **override**, not a `CrewBackend` base-class edit —
  confirm with `grep -n "\.verify(" scripts/run_crew.py tests/test_crew_launcher.py`
  that `CliBackend` never calls `.verify()` in production code (only in tests) before
  relying on this scoping.
- Use `.get("spine")` / `.get("result")`, never bracket access, for these two entry reads.
- AND semantics (never rescue/OR) when both a result and a spine are in play — restated
  because it is the polarity-inverse of `finalize_from_exit_code` in the same file and easy
  to copy backwards.
- The accepted-risk message must print to **both** stdout and stderr.
- State in `IMPLEMENTER_RESULT`, explicitly, that this intentionally narrows
  `docs/superpowers/specs/2026-07-07-crew-backend-design.md`'s Decision 2
  ("the result contract is backend-invariant ... never forked") for the specific new
  spine-evidence dimension on `ExternalBackend` only — the base freshness/existence
  contract itself stays byte-for-byte shared (unforked), this is an *additional* gate
  layered on top for one backend, not a fork of the existing one.

## Map Anchors (inbound)
- **Map entry point:** none — no `docs/architecture` map exists in this repo (confirmed
  DEGRADED at `context`).
- **Structural:** `scripts/run_crew.py:CrewBackend.verify` (~L1475, read-only, unchanged),
  `scripts/run_crew.py:ExternalBackend.dispatch` (~L1671),
  `scripts/run_crew.py:spine_terminal` (~L506, read-only reuse),
  `scripts/run_crew.py:finalize_from_exit_code` (~L1212, read-only polarity precedent),
  `scripts/run_crew.py:CrewSpec.__post_init__` (~L1360, read-only — confirms `result=None`
  + `spine` given is already legal).
- **Decision anchors:** all six in MISSION_FRAME.md's "Decision Anchors & Decision
  Pressure" section — carry their `@grade: guess · leans g1-implement · settle: ...` tags
  forward into your own evidence/reasoning; none are settled yet, all lean on this gate's
  red/green proofs to become `settled/measured`.

## Deliverable Path Check
- **Committed** — `scripts/run_crew.py`; `git check-ignore scripts/run_crew.py` exits 1
  (not ignored) — confirmed by the Commander before dispatch.
- **Committed** — `tests/test_crew_launcher.py`; `git check-ignore tests/test_crew_launcher.py`
  exits 1 (not ignored) — confirmed by the Commander before dispatch.

## Required Evidence
- Every red-proof's failure output, pasted verbatim, run against pre-fix code.
- Every green-proof's passing output, pasted verbatim, run after the fix.
- Full suite: `cd /home/tommy/projects/constellation-skills/.worktrees/567-b-external-backend && python -m pytest tests/test_crew_launcher.py -q`
  — paste the summary line. Any failure outside the explicitly-named rewritten tests is a
  stop condition.
- The exact list of every test whose scenario (not just assertions) was intentionally
  changed, with a one-line reason each.

## Wiring Grep
```bash
cd /home/tommy/projects/constellation-skills/.worktrees/567-b-external-backend && grep -rn "spine_verified\|verify_spine\|accept_mtime_only_risk\|mtime_only_risk_accepted" scripts/run_crew.py tests/test_crew_launcher.py
```
State the count of production write/read sites vs. test assertion sites found for each
symbol.

## Verification Commands
```bash
cd /home/tommy/projects/constellation-skills/.worktrees/567-b-external-backend && python -m pytest tests/test_crew_launcher.py -q
```

## Suggested Model Tier
simple bounded — one file, clear existing precedent (`finalize_from_exit_code`) for the
polarity to mirror-invert, narrow blast radius, though the default-refuse redesign now
touches more test scenarios than the first draft — still bounded, not open-ended.

## Authority
Design (default-refuse, verify-time `--verify-spine`, explicit reasoned
`--accept-mtime-only-risk` override, AND semantics, `ExternalBackend`-only override) is
already decided by the dispatching Commander after a cold-critic revision pass — see
MISSION_FRAME.md / PLAN_ALTERNATIVES.md ("Revision after cold critic"). Do not re-litigate
the design; implement it. Where it proves unbuildable against the actual code, stop and
report rather than silently choosing a different shape.

## Stop Conditions
Stop and return if: the fix needs an edit inside `checklist_engine.py` or
`mcp_spine_server.py`; the design proves unbuildable against `spine_terminal`'s actual
contract; any existing test other than the ones named above as intentional rewrites needs
its scenario (not just assertions) changed to stay green.

## Return Format
Return IMPLEMENTER_RESULT per `templates/IMPLEMENTER_RESULT.template.md`, written to
`.agent-work/epic-567-door/cmdr-b/crew-handoffs/g1-implement-implementer-result.md` before
ending your turn.
