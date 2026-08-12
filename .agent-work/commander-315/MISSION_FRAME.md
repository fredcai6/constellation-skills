# Mission Frame — commander-315 (issue #315, command-check cwd)

## Intent

A `command`-kind postcondition must run where the spine lives, not where the
launching process happened to stand. Today `scripts/checklist_engine.py:787`
calls `subprocess.run([shell, "-c", command], capture_output=True, text=True)`
with no `cwd=`, so the check inherits the launcher's cwd.

This frame is **not** shrunk-as-trivial. The change is one line of behaviour but
it moves a **resolution rule** that every `command` check in the corpus reads,
so the frame's job here is the blast radius, not the mechanism.

## Map confidence, staleness, disputes

The map is **DEGRADED-UNPARSEABLE**, anchor count 0, discharged at the context
step with three hash-pinned substitutes (receipt:
`.agent-work/commander-315/map-orientation.json`). `docs/architecture/` does not
exist; `map/INDEX.md` is an unfilled template and `map/ids.jsonl` is empty.

Consequence for this plan, stated rather than silently absorbed: there are no
map anchors from which to read who references `_run_check_command`. **The blast
radius was therefore enumerated by command over the template corpus** instead of
read off the map. That substitution is the plan's response to the degraded area,
per the context step's requirement not to author gates that trust an unverified
map.

## Structural anchors (the hash-pinned substitutes)

- `docs/CHECKLIST_SCHEMA.md` — the checklist contract. Lines 39-41 already
  record this exact defect and, decisively, name the anchor the corpus assumes:
  *"A `command` check receives no `cwd`... Every command the generator emits is
  therefore anchored `cd <repo-root> && ..."*
- `docs/CHECKLIST_ENGINE_DESIGN.md` — engine design rationale.
- `docs/agents/ORCHESTRATOR_CONTEXT.md` — project doctrine overlay.

## Affected capabilities

- Postcondition verification for every `gated` checklist (`advance`, `start`).
- Survey item verification (`record --result pass` runs the same
  `_check_condition`).
- Every role spine that ships with a `command` check: admiral, commander,
  explorer, implementer, interrogator, reviewer.

## Governing constraints and assumptions

- **Preserve the POSIX-shell routing and the visible `returncode 127` /
  `no-posix-shell` failure path** (LAUNCH_ORDER pre-ruling
  "preserve-no-posix-shell-behavior"). `cwd=` is added only to the
  branch that already calls `subprocess.run`; the synthetic-failure branch is
  untouched.
- **`scripts/hooks/spine_rail.py` and `scripts/agent_work_root.py` are
  forbidden** this wave (LAUNCH_ORDER pre-ruling "engine-core-serialized"). The
  fix does not need them — see the decision below.
- The engine must not acquire a hard dependency on `git` being installed for a
  check to run.

## Decision anchors and decision pressure

**The one real judgment in this issue: what does `cwd` resolve TO?**

`base_dir` (already threaded to `_check_condition`) is the **spine's directory**,
e.g. `.agent-work/<work-id>/`. That is not the repo root, and the gap between
them is the entire blast radius.

| candidate | consequence |
|---|---|
| **A** — `cwd = base_dir` (spine dir) | breaks **all 17** cwd-dependent shipped checks at once; `.agent-work/<work-id>/` sits two levels below the root every check assumes. Turns a one-line fix into a corpus rewrite and invalidates every archived spine. |
| **B** — `cwd = repo/worktree root enclosing the spine` | all 17 resolve correctly; **zero template repairs**. Matches `docs/CHECKLIST_SCHEMA.md:39-41` and matches `scripts/generate_spine.py:946`, which already probes candidate checks with `cwd=str(repo_root)`. |
| **C** — no change (honest null) | rejected: the defect reproduces live, on both the filed fail-open and an unfiled false-red. |

**Chosen: B.** Not from taste — from the measurement in `notes-1.md`: **zero**
shipped checks are authored spine-dir-relative, and all 17 cwd-dependent ones are
repo-root-relative. B is the only option under which the corpus is already
correct.

**Sub-decision — how to find the root.** Walk up from `base_dir` for a `.git`
entry, accepting both a directory (plain checkout) and a **file** (linked
worktree). Pure filesystem, no subprocess, no git-on-PATH dependency.

**Rejected: `agent_work_root.durable_root()`.** It deliberately redirects a
linked worktree to the MAIN checkout. A check must verify its **own** worktree's
files; durable_root would make this worktree's gates inspect the Admiral's
checkout — the exact cross-agent confusion epic 568 exists to remove. It is also
a forbidden file this wave. Not used, not edited, not depended on.

**Sub-decision — fallback when no `.git` is found** (spine in a bare temp dir,
which is what most engine tests build): fall back to the inherited cwd, i.e.
exactly today's behaviour. Conservative: no existing test that builds a spine
outside a repo changes meaning.

## Claims and evidence surfaces

- **Claim:** the fail-open reproduces. **Evidence:**
  `.agent-work/commander-315/repro_315.py`, exit 1 before the fix, showing a
  decoy file in the launcher's cwd advancing gate gA.
- **Claim (not filed, found here):** the same defect also causes a **false-red** —
  the project's own file is invisible to a check launched from elsewhere. Same
  repro, gate gB.
- **Claim:** zero template repairs are needed under candidate B. **Evidence:**
  the by-command enumeration in `notes-1.md`.

## Out of scope

- Restoring the degraded architecture map (no `docs/architecture/`).
- The **authoring-side** weakness the enumeration exposed: 11 of 17 checks are
  cwd-dependent only because they invoke a script whose `--root` defaults to
  cwd. This fix makes them correct, but they remain fragile to a future caller.
  Triage candidate, not this issue.
- `scripts/hooks/spine_rail.py`, `scripts/agent_work_root.py` — forbidden.
