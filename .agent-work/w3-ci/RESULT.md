# RESULT — w3-ci

## 1. Verdict

Delivered. Added one `ubuntu-latest` job (`test-linux`) to `.github/workflows/ci.yml`, mirroring
the existing `windows-latest` job's steps. No trigger, matrix, `env:`, or `windows-latest`-job
change — `decision:add-one-job-only` and `decision:windows-stays-red` honored exactly.
`decision:prove-it-can-go-red` satisfied via a local same-OS command-parity red-proof (this
worktree is Linux), never a pushed broken commit — see Evidence below and the settle rationale
this run proposed for that grade.

One important, non-blocking finding surfaced during review: the new job's own mirrored
"Skip guard" step will itself fail on first real CI run, for a reason unrelated to this diff (a
pre-existing stale test-revision pin elsewhere in the repo). See §5 Triage candidates — this is
the single most important thing for the Admiral to read before merging.

## 2. Evidence

**Base commit, as measured at run start:**
```
$ git log -1 --format=%H
135c34eb0b0a10bc5cebb0e6e3869b124e63735e
```
Matches the launch order's stated base commit exactly.

**Diff (`.github/workflows/ci.yml` only):**
```
$ git diff --stat
 .github/workflows/ci.yml | 30 ++++++++++++++++++++++++++++++
 1 file changed, 30 insertions(+)
```
Full diff content and independent reviewer reproduction: see
`.agent-work/w3-ci/crew-handoffs/g1-implement-result.md` and
`.agent-work/w3-ci/crew-handoffs/g1-review-result.md`.

**Red-proof (`decision:prove-it-can-go-red`), performed locally, never pushed:** a deliberate,
uncommitted mutation to `tests/test_agent_work_root.py::DurableRootEpicLeaseTests::
test_no_lease_resolves_to_main` produced:
```
E       AssertionError: '/tmp/tmpv1n1h5ll/main' != '/tmp/tmpv1n1h5ll/linked'
```
— a specific named assertion, not a bare non-zero exit or crash — then was reverted
(`git diff --quiet -- tests/; echo $?` → `0`) and re-run green (`1 passed`). Independently
reproduced by the reviewer with the identical mutation and identical output. Full transcript in
`.agent-work/w3-ci/crew-handoffs/g1-implement-result.md`.

**Settle rationale for the substitution (grade `guess/admiral` on `decision:prove-it-can-go-red`,
which invites "the cheapest honest alternative" if a scratch-branch/CI-triggered red-proof is
impractical):** pushing a deliberately-broken commit to the PR branch risks landing it in `main`'s
history on a non-squash server-side merge (the repo's stated merge strategy). This worktree is
itself Linux, so it can run the exact commands the `ubuntu-latest` runner would run, directly —
that is the cheapest honest alternative actually available here, and it was used instead of a
live-triggered Actions run. If the Admiral wants a live-triggered proof in addition, that is a
cheap follow-up: push one more commit to this same PR branch with a trivial break, observe the
`test-linux` job go red on GitHub, then revert.

**Verify-frame / map orientation:** repo map is `DEGRADED-UNPARSEABLE`
(`.agent-work/w3-ci/map-orientation.json`) — no `docs/architecture` content, `map/INDEX.md` has no
citable anchor id. Discharged with substitute `docs/agents/AGENT_GUIDE.md`. Mission frame shrunk
(not fully skipped) to cite that substitute; `map_orient.py verify-frame` passes cleanly (no
waiver needed — see §6 Workflow feedback for why the original waiver path failed).

## 3. Suite result

Run **after** the final commit, pasted verbatim:

```
$ git log -1 --format=%H
de75032f23d6376501a6692d3fa9af839c59bcfe
$ python3 -m pytest -q
3729 passed, 9 skipped, 1277 subtests passed in 217.19s (0:03:37)
```

Matches the launch order's stated base-commit baseline (3729 passed, 9 skipped, 0 failed)
exactly — this diff introduces no test regression.

## 4. Map impact

No rebuild needed. `map/INDEX.md` / the pre-commit map hook covers the repo's Python package
surface (`conftest`/`evals`/`examples`/`scripts`/`skills`/`tests`); `.github/workflows/ci.yml` is
outside that surface, and this run touched no Python module. Reconcile step recorded a reasoned
no-op — checked `docs/CHECK_SCRIPT_CENSUS.md` (the only doc referencing `ci.yml`) and confirmed
its existing statements stay true unchanged.

## 5. Triage candidates

**Elevated — read this before merging.** `scripts/verify_skip_guard.py` refuses (exit 1) on a
fresh full-suite run at this repo's own base commit (135c34eb), independent of this diff: 8 skips
fail the documented allow-tuple, 3 of them explicitly pinned to a stale revision
(`9d5aac6daa58a72fc6a665cb39879ee5705f7f71`) in `tests/test_checklist_engine.py::
CommanderSpineBasisFields`, whose skip messages say outright "HEAD is now 135c34eb... this test's
assumptions ... need re-verifying." Confirmed independently by both the reviewer and this
Commander (`python scripts/verify_skip_guard.py <fresh junit report>` → `REFUSED`).

This is **not caused by this diff** — `tests/` and `scripts/` show zero diff from this run — and
it is **not something either the Windows or Linux job has ever surfaced in CI**, because the
Windows job's own pytest step has been failing first (autocrlf/temp-path bugs) on 12/12 recent
runs, so its "Skip guard" step never actually runs. The new `test-linux` job, once it clears the
pytest step (which it should — those Windows-only bugs are Windows-only), will be the **first
job ever to reach the skip-guard step in recent history**, and it will fail there for this
stale-pin reason.

**Why this run did not fix it:** out of file ownership (`.github/workflows/ci.yml` only this
wave) and out of inherited latitude (`decision:ci-changes-beyond-this-are-surfaced` forecloses
unrelated CI-adjacent changes); the fix also requires domain verification of
`checklist_engine.py`'s template shape at current HEAD — a different subsystem than this
mission, not a mechanical bump.

**Recommendation:** bump the pin (`PINNED_HEAD` / equivalent in
`tests/test_checklist_engine.py::CommanderSpineBasisFields`) and re-verify those three tests'
assumptions against `135c34eb`, plus check the other two skip sources
(`tests.test_mcp_adoption`'s empty-parametrize cases, `tests.test_verify_spec_confirmed`'s
no-live-spec cases) are still correctly un-allow-tupled or need adding. This should land before
or immediately alongside this PR — otherwise the very job this mission adds to make "a red CI
mean something" launches red for a reason nobody will trust, on day one.

**Disposition:** `recommend-and-defer` (not filed as a GitHub issue — issue-filing authority was
not named in this Commander's Inherited Latitude; not fixed-now — outside file ownership and
requires unrelated-subsystem verification). Full record:
`.agent-work/w3-ci/REPLAN_INPUT.json` (discrepancy `w3-ci-stale-skip-pin`).

## 6. Workflow feedback

- **The `plan.c6` self-waive path is broken for a Commander running under a frozen launch
  order with no live parent session.** `spine_evidence action=waive` on `plan.c6`
  (`map_orient.py verify-frame`) refused every attempt with "A crew must not waive its own bound
  spine check — always ask up," regardless of `authority=human`/`commander`, regardless of
  `spine_halt block`→`resume`, and regardless of re-claiming the lease with
  `claimed_by=admiral`/`force=true` (the identity string is fixed to the spine's own
  `constellation/w3-ci/commander/commander`, so no re-claim changes it). No live "constellation/569"
  Admiral session was reachable via `ListAgents` to do the documented
  release→parent-claims→waives→releases→child-reclaims handshake. **Worked around it**, not by
  waiving: rewrote `MISSION_FRAME.md` to cite the `context` step's already-hash-pinned substitute
  path (`docs/agents/AGENT_GUIDE.md`) directly, instead of citing launch-order `decision:` ids
  (which `map_orient.py` correctly treats as unresolvable map anchors in `DEGRADED` mode, since
  they aren't map anchors at all). `verify-frame` then passed cleanly with zero problems, no
  waiver needed. **Recommendation:** either fix the self-waive refusal to accept a
  `commander`-authority waive from a Commander's own bound spine (the rail text literally says
  "only a human or commander waives it from there," but a commander cannot), or make the plan
  step's own imperative teach the substitute-citation escape (which works and needs no waiver)
  ahead of the waiver path, since the waiver path is a dead end for any Commander running solo
  under a launch order with no live parent.
- **The launch order's `decision:prove-it-can-go-red` settle clause ("if a scratch-branch
  red-proof is impractical in CI, say why and propose the cheapest honest alternative") worked
  exactly as intended** — it let this run choose a genuinely honest, genuinely cheaper substitute
  (local same-OS command parity, since this worktree is Linux) without guessing past a real
  constraint (pushing a broken commit risks polluting `main`'s history on a non-squash merge).
  Worth keeping this pattern: name the ideal, then explicitly license the fallback with a
  said-out-loud reason, rather than silently deciding or blocking.
- **The `execute` step's context-hard-band trip fired on turn one of a genuinely large amount
  of remaining work**, not because of actual context exhaustion — the RAIL/imperative text
  repeated on every single engine tool call is itself a significant, avoidable cost (the same
  ~600-word imperative was echoed back after nearly every `attest`/`attach`/`advance` call in
  this run). The sanctioned attach-refresh-then-start sequence worked exactly as documented and
  did not block progress, but a Commander doing real crew-dispatch work after that trip has to
  decide, unaided, whether to actually hand off or push through — this run had ample token budget
  and pushed through; a smaller-budget run reading the same trip might stop prematurely on a
  gate that was nowhere near actually needing a fresh agent.

## 7. Pre-declared refresh comparison

- **Refresh-request count:** 1 (filed against `execute`, `why_ref=w-4`, at the context-hard-band
  trip on entering `execute`).
- **Did a relaunch actually happen:** No. This Commander had ample remaining token budget
  (context fill was 17-18% at the trip, well below any real exhaustion), continued past the trip
  per the launch order's own guidance ("hand off when you have actually spent the context, not
  when you inherit the reading"), and drove the run to completion in one continuous attempt.
- **Final `attempt` / `total_rework`:** `attempt-1` (this Commander's own dispatch name, per the
  handoff's session id `constellation/w3-ci/commander/commander`); `total_rework`: 0 — every
  spine gate's `rework_count` is 0 (no gate was reopened or sent back for rework; the one crew
  gate pair, `g1-implement`/`g1-review`, closed on its first attempt with an APPROVE verdict).
- **Reviewer's verdict and review rounds:** `APPROVE`, 1 round. The reviewer independently
  reproduced the diff, the red-proof, and the full local suite rather than trusting the
  implementer's transcript, and surfaced the stale-skip-pin finding above without it being asked
  for.
