# Workbench Checklist Engine

The engine is the deterministic state machine an agent transacts with **one step at a time**. It holds canonical state and enforces *mechanism* — ordering, evidence shape, the rework cap, the consolidation guard — and never judges quality. An agent does not re-read and self-manage a checklist; it asks the engine what to do, does it, and reports back.

Tool: `python <skill-dir>/scripts/checklist_engine.py --file <checklist.json> <verb>`. Installed copies rewrite that command to an absolute path; run that absolute path and do not resolve `scripts/` from the target repo unless that repo vendors the script. In this source repo, the same script lives at `scripts/checklist_engine.py`. Schema: `docs/CHECKLIST_SCHEMA.md`. Model: `docs/CHECKLIST_ENGINE_DESIGN.md`.

## This is mandatory, not advisory

When you have loaded a role skill, you **must** drive its checklist through the engine to completion. The checklist *is* the workflow. Run every step in order, close each gate through the engine, and do not improvise, skip, or do the work outside the checklist. If a step needs another role, dispatch it (below) — do not just describe it.

## Instantiate from the project template

When creating a checklist, prefer the project-specific template at `.agent-work/templates/<name>` if it exists; otherwise use the bundled `skills/<role>/templates/<name>`. A project-scope install seeds an editable working copy of every template there (never clobbering existing edits), so this is the home a project edits and commits; Charter and later runs customize them, and `check_skill_freshness.py` reconciles them against the `.baseline/` when the skill upstream changes. If a project-local copy carries `<…-skill-dir>` tokens, resolve them to the installed skill directory (the path your own SKILL.md already uses).

**Dogfooding on the skill-source repo.** When the repo you are working on *is* the constellation-skills source, instantiate the work area with `--skill-dir <repo-root>` so the spine's `<…-skill-dir>/scripts/` command postconditions resolve to the repo's own **vendored** `./scripts/` rather than a globally-installed copy; template paths still come from `skills/<role>/templates/` by judgment (scripts at the repo root, templates under the skill dir). The globally-installed skill copy and the repo's own source copy of a template or script **can diverge** — drive the engine from the repo's own copy and diff the two when in doubt; nothing in the Skill-tool invocation flags which copy governs.

## Dispatch: subagent vs your own context

A delegated checklist runs in one of two ways:

- **Bounded, autonomous work** (implementer, reviewer, cartographer, scout): dispatch a **subagent**. Hand it the context it needs and its checklist; it works and returns evidence or a consolidated result.
- **Work that talks to the human** (interrogator, and any `user-decision` checkpoint): run it in **your own context** by loading that skill and driving its checklist. A subagent cannot reach the human, so it cannot interrogate. The role split still holds — it is a separate checklist — it just runs in the human-reachable context.

If your environment has no nested subagents, keep the orchestration (Commander) in the one human-reachable context and dispatch only the leaf workers.

## One agent, one plan

A checklist is one plan one agent works through — not the whole hierarchy in one file. Delegation is **by reference**: a gate sets `child_checklist: <work-id>` pointing at a separate plan; the sub-agent drives its own checklist. Every agent (Commander, implementer, reviewer) has its own.

## Two types

- **`gated`** — execution. Ordered; satisfy each item to advance; a failure **blocks** (rework). Used by the Commander spine, Commander's execute.json, the implementer's own plan.
- **`survey`** — verification/inquiry. Visit every item; **append** more from context; a failure is **recorded, never blocks**; then **consolidate** into one result. Used by the reviewer (→ APPROVE/BLOCK + findings) and the Interrogator (→ resolved understanding).

## Verb loop

```
current                          # which step am I on (an imperative)
start <id>                       # begin it; engine checks preconditions
  ... do the work ...
advance <id>                     # gated: engine runs command checks / verifies artifact shape, then closes
record <id> --result pass|fail   # survey: record the check; never blocks
consolidate [--verdict ...]      # survey: every item visited -> hand up a result
```

Other verbs: `skip <id> --reason` (OBE), `block <id> --blocker ... --authority ... --next ...` (bubbles to parent), `reopen <id> --reason` (gated rework; escalates at the cap; **cascades** — resets every downstream `complete`/`in-progress` gate to `pending` and marks the target's + each cascaded gate's evidence `superseded`, which is **retained** for audit but inert for re-satisfaction, so the reopened work needs fresh evidence), `append <id> --title --imperative` (survey only — `<id>` is the NEW leaf's own id, a flat sibling, NOT an anchor id to nest a check under an existing item; anchoring under an existing id is refused as "already exists". E.g. `append r5 --title ... --imperative ...` adds sibling r5; to group per-criterion checks, append siblings r4a..r4f and attest an umbrella item separately), `amend --delta <file> --reason ... --authority human` (gated only: intentional mid-run re-plan — a validated, all-or-nothing delta of `add`/`drop`/`rescope` ops on **pending** gates, logged to `amendments`), `attest <id> --cond <id>` (assert a qualitative precondition — trust but verify), `attach <id> --type <t> --field K=V` (record evidence; use `--field` or `--payload-file` to avoid passing JSON through the shell — e.g. `attach g1 --type review-result --field verdict=APPROVE`), `waive <id> --cond <id> --authority human --reason "..."` (human override of a check — see below), `flag-candidate --from <id> --statement` (out-of-scope discovery). Note the survey-verb flag asymmetry: `record` takes `--result`/`--finding` (per-check), while `consolidate` takes `--verdict`/`--summary` (whole-survey).

## Session lease: who owns the checklist state

The engine enforces **actor authority** over a checklist's state so a resumed or duplicated parent session cannot concurrently mutate the same plan. One session leases the checklist; mutating verbs then require that session's id.

```
claim     --session-id <id> --claimed-by <role> [--worktree .] [--force --reason "..."]
heartbeat --session-id <id>
release   --session-id <id>
```

- `claim` takes the lease. The **same** `session_id` re-claiming is idempotent (it just refreshes the heartbeat) — safe to call on resume. A **different** active session is refused; take over only with `--force --reason "..."`, which records the prior session for audit.
- `heartbeat` proactively refreshes your lease — only needed for an idle wait where no mutating verb will fire (mutating verbs refresh it for you); `release` closes it when you are done.
- **Once a lease exists, every mutating verb needs `--session-id <id>` matching the active lease** (`start`, `advance`, `record`, `consolidate`, `skip`, `block`, `reopen`, `append`, `amend`, `attest`, `waive`, `attach`, `flag-candidate`). Pass it on each call. Read-only `current` needs no session and shows the active lease.
- A lease goes **stale** if its heartbeat lapses (config `lease_stale_seconds`, default 1800s). Staleness gates **non-owners only**: as the **owner** you are never blocked by your own staleness — every mutating verb you issue refreshes the heartbeat, so a long step or idle gap self-heals on your next verb (no re-claim, no takeover record). A **different** session must `claim` the stale lease (same id, or `--force --reason`) before mutating — the engine refuses it and tells it to claim.
- A checklist with **no lease** behaves exactly as before: mutating verbs work without `--session-id`. Only claim a lease when your workflow wires it (the Commander spine claims at `init`, releases at `archive`).

## Obey refusals

The engine answers illegal moves with an imperative, e.g. `REFUSED: g1: postconditions unmet ['c1']`. Treat that as the next instruction — fix the named gap, do not work around it. The refusal *is* the gate.

## Waive: human override of a check

A `command`/`artifact` postcondition that won't pass normally **blocks the gate** — that is correct, and your default is to fix the work, not route around the check. The one sanctioned exception is when the **human** decides a specific check is non-blocking. Do not edit the JSON to mark the condition satisfied; use the engine:

```
waive <id> --cond <cond-id> [--which postconditions] --authority human --reason "why it's accepted"
```

- It requires a non-empty `--authority` (who is accepting the risk) and a `--reason` (always, when the condition's `override_policy.reason_required` is set or you use `--force`). The reason becomes durable, auditable evidence (`type: waiver`).
- It is **refused unless the condition declares an `override_policy` with `allowed: true`** — you cannot waive a check that the plan author never marked waivable. To override that refusal deliberately, pass `--force`; force still demands authority + reason and is recorded as `forced: true`. Treat `--force` as a last resort and surface it to the human.
- After a waiver, `advance` succeeds and its message names the waived conditions (e.g. `g1 -> complete (WAIVED postconditions ['c1'])`). The waiver is **not** re-run away at advance, and it is cleared if the gate is later `reopen`ed.

The engine does not judge whether a waiver is wise — it only refuses *accidental* advancement and records who authorized the exception. Waiving is a human decision you carry out through the engine, not one you make for the human.

## Mechanism the engine guarantees

- **Ordering** — cannot start a later gate before the active one (gated).
- **Evidence shape** — `command` postconditions must exit 0; `artifact` postconditions need a matching evidence item present. Quality is judged by the reviewer/human, not the engine. `command` checks run under a POSIX shell (bash) so authored `grep`/`&&`/pipe checks behave the same on every platform; the `command-output` evidence's `shell` field records which shell ran it — `posix`, or `cmd-fallback` on a Windows box with no bash (where a POSIX-only check visibly fails rather than silently false-FAILing).
- **Artifact-output guardrails** — a `git-change-policy` postcondition collects the staged (`git diff --cached`) or branch (`git diff <base>...HEAD`) diff and refuses advance when a changed file violates an inline policy: matches a `deny_glob` (e.g. `records/**`, `*.parquet`), exceeds `max_file_bytes`, or is a binary/blob addition when `require_human_waiver_for_binary` is set — unless the path matches an `allow_glob`, which exempts it from the size/binary checks (a deny always wins). It is purely mechanical (globs/size/binary), records an `artifact-policy` evidence item listing the violations, and is **waivable** by a human via `waive` (the condition carries an `override_policy`). The Commander spine's `archive` gate uses it (postcondition `c4`) to refuse closeout on suspicious artifacts unless the human accepts the risk. The policy values are the per-project rigor dial — tune them on the check in the project's templates. See `docs/CHECKLIST_SCHEMA.md` for the field table and full semantics.
- **Rework cap** — `reopen` counts; on the (cap+1)th it stops re-dispatching and escalates to the parent. The cap is set at Charter time.
- **Consolidation guard** — `consolidate` refuses `APPROVE` while any item is `fail`, unless an explicit `--override-reason` is given.

## Bubble-up channels

`triage_candidates` (out-of-scope work to capture; Triage drains them at clean-up) and `blockers` (stuck items needing authority). Both surface to the **parent agent** first; the parent escalates to the human only if it cannot resolve them.

## Context-read step

Every checklist opens with a context-read item so the agent pulls the right baseline (gated: read, then `attest`; survey: read, then `record pass`). Each agent reads its **inherited global doctrine** (bundled with the skill at `references/global-*.md`) first, then the project's thin **local deltas** if they exist:

- **High tier** (Commander, Cartographer, Scout): `references/global-orchestrator.md` + `references/global-everyone.md`, then `docs/agents/ORCHESTRATOR_CONTEXT.md` + `GLOSSARY.md` + relevant Cartographer packets if present.
- **Crew tier** (implementer, reviewer): `references/global-crew.md` + `references/global-everyone.md`, then `docs/agents/CREW_CONTEXT.md` + `GLOSSARY.md` + the handoff + packet if present.

The global buckets are inherited and identical across projects; the project files carry only departures, so a missing `docs/agents/*` degrades gracefully to global-only. Engine config (rework cap, replan policy, human checkpoints) comes from `docs/agents/engine-config.json` via each checklist's `config_ref`.

Division of labor: the **skill** (its bundled global doctrine) says how to approach the job, the **checklist** says exactly what to do, the **Charter context files** say the project-specific deltas.

## Template set

Copy into `.agent-work/<work-id>/`, fill placeholders, then drive with the engine:

| template | type | role |
|---|---|---|
| `skills/commander/templates/COMMANDER_SPINE.template.json` | gated | Commander spine (understand/plan/execute/cleanup) |
| `skills/commander/templates/EXECUTE_PLAN.template.json` | gated | Commander's frozen gate plan; three tasks per gate (implement/review/integrate) |
| `skills/interrogator/templates/INTERROGATION.template.json` | survey | the Interrogator's question survey |
| `skills/reviewer/templates/REVIEW_SURVEY.template.json` | survey | the reviewer's verification survey |
| `skills/implementer/templates/IMPLEMENTER_PLAN.template.json` | gated | the implementer's own working plan |
| `skills/charter/templates/ENGINE_CONFIG.template.json` | — | Charter writes it to `docs/agents/engine-config.json` |
