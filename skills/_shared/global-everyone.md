# Global doctrine — everyone

Inherited platform and engine doctrine for **every** Constellation role, bundled with the skill at
install. This is the baseline the whole fleet shares; a project never restates it, only departs from it.
Project orientation is the local overlay — read `docs/agents/AGENT_GUIDE.md` (repo map) and
`docs/agents/GLOSSARY.md` if they exist.

Agent-facing. Dense by design.

## Engine verbs

- Artifact postconditions (`kind: artifact` — `user-decision`, `review-result`, …): **attach** the evidence
  once, then satisfy a sibling gate's identical artifact postcondition **by reference** —
  `attest <task> --cond <id> --which postconditions --evidence <evidence-id>` — instead of re-attaching. E.g.
  attach the APPROVE `review-result` to `gN-review`, then
  `attest gN-integrate --cond <id> --which postconditions --evidence e-gN-review-1`. The engine still verifies
  the referenced artifact exists and matches the required `evidence_type` + `match` (it is not a thin-air
  assert). (`attach`-ing the same artifact to BOTH gates still works — backward compatible.)
- A postcondition whose `check` is `null` is confirmed by **attest** (your manual verification); `attach`
  won't satisfy it. Never hand-edit the checklist JSON to mark a condition satisfied — use `attest` /
  `attach` / `waive`.
- The lease owner is **never blocked by its own staleness**: every mutating verb that **succeeds**
  auto-refreshes `last_heartbeat`, so an actively-working owner never goes stale and a manual `heartbeat` is
  rarely needed. A **refused** verb (ownership gate passed, but the verb itself raised) does **not** refresh —
  a session that only fails can still go stale and be reclaimed. The explicit `heartbeat` verb remains for a
  genuine idle gap. If another session seized the lease during such a gap, recovery is a same-id re-claim
  (idempotent, not a takeover) — free.
- `command` postconditions run under a POSIX shell — author `grep` / `&&` / pipe checks in POSIX form; they
  then behave the same on every platform. On a Windows box without bash/sh the engine **refuses** to run the
  POSIX-form check text through cmd.exe: the check fails **visibly** (returncode 127, marker `no-posix-shell`,
  stderr naming the missing shell) rather than silently passing or being misinterpreted by cmd.exe.

## Windows shell hazards

- See `windows.md` (canonical, grounded) for the `gh ... --body` and `py` launcher recipes. Quick rule: Bash
  tool for POSIX command sequences, PowerShell for cmdlets — don't feed heredocs to PowerShell.

## Parallel dispatch and worktrees

- See `windows.md` (canonical, grounded) for the `isolation:"worktree"` no-op hazard and its verification
  recipe. Never launch a continuation into a possibly-sleeping agent's worktree.

## Detached and long work

- The result/deliverable file IS the task. Run verification and sweeps to completion **in-context** (poll,
  don't idle); an idle turn-end with the result unwritten strands the gate with no error signal — finish,
  then rest.
- Detach genuinely long jobs at the OS level (e.g. `Start-Process -WindowStyle Hidden`). Write the
  crash-resume state note (step / slug / next-cmd / PID / expected-artifact) BEFORE detaching; arm ONE
  completion notify (output-exists OR process-death), never a per-progress-line watcher.

## Universal posture

- Fail visibly rather than emit plausible wrong output; no hidden fallback.
- One canonical path; no speculative abstraction.
- Keep Constellation context and architecture docs current when their meaning changes.
- `/compact` is user-level; most harnesses don't expose it to agents. Treat context headroom as
  opportunistic (compact if available, else rely on auto-compaction) folded into the step that needs it,
  not as its own checkable gate — a step whose only sanctioned path is "skip" is ceremony, not gate.
- Reference bundled scripts and references by their absolute installed path; don't resolve `scripts/` from the
  target repo unless it vendors them.

## Deep-module vocabulary

Every role names interfaces the same way. Departures-only; scale-agnostic (a function, a file, a service).

- **Module** — an interface plus its implementation.
- **Interface** — *everything* a caller must know to use the module: invariants, ordering, error modes, config,
  performance envelope — not just the type/signature surface.
- **Seam** — where an interface lives. Its placement is its own decision, not a byproduct of the implementation.
- **Adapter** — a thing satisfying an interface at a seam. **One adapter = a hypothetical seam; two = a real one** —
  a boundary with a single implementer is a guess until a second proves it.
- **Depth / leverage** — behavior delivered per unit of interface a caller must learn. Deep = much behind little.
- **Locality** — change and verification concentrate in one place rather than scattering across callers.

Two working rules:

- **The interface is the test surface.** Test through it, not past it; wanting to reach behind it means the module
  is the wrong shape.
- **The deletion test.** Delete the module in imagination: if complexity vanishes it was a pass-through; if it
  reappears across N callers it was earning its keep.
