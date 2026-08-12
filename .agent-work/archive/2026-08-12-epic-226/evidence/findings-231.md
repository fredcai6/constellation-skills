# Findings — issue #231 (epic-226 item E)

Sole writer: commander-231. Worktree: `C:/Programs/constellation-wt-231` (branch `issue-231`).

## PR-7 re-verification (before planning)

Re-grepped all three named gaps against current code at plan time; no drift since
launch-order authoring:

- **(a)** `skills/prototyper/templates/PROTOTYPE_RESULT.template.md` had a freeform
  `## Answer` field, no enum. **Genuine gap**, confirmed by reading the file directly.
- **(b)** `skills/prototyper/SKILL.md` section "Closeout: disposition is mandatory" listed
  exactly `deleted | absorbed | parked-with-owner`. `grep -rn "captured-to-worktree"
  skills/ docs/` returned zero hits repo-wide. **Genuine gap.**
- **(c)** `grep -n -i "prototyp\|PROTOTYPE_HANDOFF\|excursion"
  skills/commander/references/commander-core.md` returned zero hits. **Genuine gap.**

## PR-6 re-confirmation (canonical doctrine target)

Read `scripts/install_constellation.py` lines 98-124: `_GLOBAL_EVERYONE`,
`_GLOBAL_ORCHESTRATOR`, `_GLOBAL_CREW`, `_GLOBAL_ALL_TIERS` name exactly
`global-everyone.md`, `global-orchestrator.md`, `global-crew.md`,
`design-it-twice-brief.md`, `windows.md` (plus role-specific extras for `curator`/
`write-a-skill`). `commander-core.md` is not a member of any tuple keyed to the
`commander`/`commander-delegated` roles, so it is the commander skill's own owned
doctrine file -- install-time regeneration never touches it. Confirmed: item (c)'s
edit target is `skills/commander/references/commander-core.md`, exactly as PR-6 states.

## Design-it-twice judgment (plan step)

Per the launch order's own note ("most likely: no, but say so explicitly"): skipped
both plan-alternatives and the cold plan critic, recorded as named untaken roads in
`execute.json`'s plan attestations (c4/c5). Reason: three small additive vocabulary
extensions to an existing contract (a 3rd verdict value with a revive-condition
subfield, a 4th disposition value, one doctrine bullet in an established bullet
family) -- no new load-bearing interface, no genuine design fork to compare candidates
on. This is a judgment call, not a silent skip; recorded here and in the verdict.

## Round-trip proof mechanism decision

Inherited Latitude authorized deciding whether to add a first-class
`evidence_type: prototype-result` to the engine, or to prove the round-trip via the
engine's existing generic `artifact`/`match` field-checking. Decided: the generic
mechanism, with `prototype-result` used as a plain string tag exactly like
`user-decision`/`review-result` elsewhere in this repo's shipped spines -- zero engine
code changes, and `scripts/checklist_engine.py` is fenced this wave (#227 owns it) so
adding a first-class kind was not an option regardless. Confirmed sufficient by
`tests/test_prototyper_templates.py`'s two round-trip tests (positive: real values ->
`advance` succeeds; negative: an off-vocabulary value -> `advance` refused).

## Out-of-scope discoveries

None found. Zero triage candidates surfaced across g1-vocab, g2-seam, g3-implement,
g3-review, or the Commander's own reconcile/triage passes.

## Fencing note (feedback/archive mechanism)

Confirmed empirically that `agent_work_root.durable_root()`, called from this worktree,
resolves to the worktree itself (not the main checkout) because epic-226's Admiral
lease is `active` in `.agent-work/epic-226/spine.json` (the built-in "active epic
lease" exception in `agent_work_root.py`). This meant the delegated-commander skill's
documented `staged-feedback/<work-id>/` + `FENCE.md` workaround was not needed -- the
plain `AGENT_FEEDBACK.md`/`LESSONS.md` write, made worktree-local, already satisfies
`verify_agent_feedback.py` on its own.

`AGENT_FEEDBACK.md` and `LESSONS.md` were deliberately written at the worktree's
agent-work ROOT (`C:/Programs/constellation-wt-231/.agent-work/`), not inside
`commander-231/`, so the archive step's directory move did not carry them along --
they remain at `C:/Programs/constellation-wt-231/.agent-work/AGENT_FEEDBACK.md` and
`C:/Programs/constellation-wt-231/.agent-work/LESSONS.md`.

**This needs Admiral harvest**: those two files live in the `issue-231` worktree, not
the shared main-checkout `.agent-work/`. Before that worktree is swept, the Admiral
should fold the `commander-231` AGENT_FEEDBACK entry and the
`lesson:from-child-refusal-undiscoverable-from-error` lesson-delta into the shared
`.agent-work/AGENT_FEEDBACK.md` / `.agent-work/LESSONS.md` in the main checkout --
otherwise this run's workflow signal is lost when the worktree is removed.
