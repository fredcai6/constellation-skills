# Mission frame — r418-460 (issue #460)

## Intent

The episode store holds records of what happened. Most of the 32 pre-#447 records in
`episodes/active/` carry a `workaround` assertion written as an instruction to a future agent.
Rewrite those as observations through the store's only write path, keep it true with something
that can fail, and hand every record that states a genuine *rule* to the human as a doctrine
candidate rather than promoting it.

## Map confidence, staleness, disputes

`map_orient.py orient` returned **DEGRADED-NO-MAP**: this skill-source repo ships no
`docs/architecture/` packet map, no generated map, no index. The verdict was discharged at the
context step with four hash-pinned substitutes. Every anchor below is one of them.

## Structural anchors (all hash-pinned substitutes from the orientation receipt)

- `docs/EPISODE_STORE.md` — the store's record grammar, seam set, and write-path doctrine.
- `episodes/README.md` — the store layout: `active/` is the ordinary set, `retired/` the archive.
- `docs/agents/ORCHESTRATOR_CONTEXT.md` — "The Retired Learning Playbook", the governing doctrine.
- `README.md` — repo entrypoint.

## Affected capabilities

- **Episode write path.** `scripts/apply_episode_delta.py` — the only writer. Today it has three
  ops: `create`, `amend-assertion`, `retire`.
- **Episode content.** `episodes/active/` — 48 records: 32 pre-#447 (`issue-304-g3-*` ×5,
  `issue-308-*` ×25, `issue-309-*` ×2) and 16 `issue-447-*`.
- **Store tests.** `tests/test_episode_store.py`.

## Governing constraints and assumptions

- **Episodes are not prescriptions** (the LO pre-ruling `record-not-rule`). An episode records what happened and is never
  read back as a rule (`docs/agents/ORCHESTRATOR_CONTEXT.md`).
- **Only write path.** Never hand-edit under `episodes/`; every change goes through
  `scripts/apply_episode_delta.py`, and every invocation passes `--store-root episodes` — the
  default resolves against the installed skill directory and would silently build a store outside
  the repo while every gate reported green.
- **The record grows; it is not rewritten** (`docs/EPISODE_STORE.md` §5). Stated precisely, because
  a cold critic caught this frame overclaiming it: §5's worked example changes only
  `lifecycle-standing` and deliberately leaves `statement` untouched, and its prose says an episode
  "never needs rewriting later". §5 is therefore **not** support for restating a statement — it is
  the constraint a restatement has to answer to. This run answers it by preserving the original
  wording verbatim in the assertion's own history, and by reconciling §5 in the g4 doc edit.
- **No successor playbook.** No new file that accumulates distilled advice for future agents.
- **Promotion into `docs/agents/*` is the human's call.** Not this run's, under any framing.
- **Fences.** This run does not touch `scripts/checklist_engine.py`,
  `scripts/collect_feedback.py`, or `scripts/verify_worktree_precondition_coverage.py`.

## Decision anchors and decision pressure

- **Decided (inherited latitude): add a `restate-assertion` op.** `amend-assertion` changes only
  `lifecycle-standing`; it has no `statement` field and cannot perform the rewrite the issue asks
  for. `restate-assertion` replaces one assertion's statement and appends a history line carrying
  the original wording verbatim.
- **Decision pressure, floated not decided: doctrine promotion.** Several workarounds state rules
  that look like they belong in `docs/agents/*`. Collected as candidates and returned.
- **Open question the guard gate settles by measurement:** can a command reliably tell an
  observation from an instruction? The LO pre-ruling `honest-null-on-the-check` says attempt it
  and measure the false-positive rate over the canon records; a measured "no" is a real finding.

## Claims and evidence surfaces

- `FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests`, real exit code captured.
- The guard must be observed **refusing** a record that plainly instructs, not merely passing on
  the corpus as it stands (LO pre-ruling `the-guard-must-be-able-to-fail`).
- Count of records examined and restated, out of 32.

## Out of scope

`episodes/retired/` (an archive, not a live search space). The K3 store-quality cluster (#399,
#342, #360, #361, #379, #405). Any edit to `docs/agents/*`. Anything that functions as a
successor playbook.
