# Implementer Handoff

## Gate
`g2-implement` — work-id `r418-460`, issue #460, worktree `C:/Programs/constellation-skills-wt/r418-460`, branch `epic-418/b-460-episodes-observations`.

## Task
Rewrite every prescriptive agent-supplied statement in `episodes/active/` as a record of what
happened, using **only** the `restate-assertion` op (shipped by gate g1) through
`python scripts/apply_episode_delta.py --store-root episodes`.

## Protected Intent
`episodes/` is a store of **things that happened**. A record that tells a future agent what to do is
the retired learning playbook growing back inside the store that replaced it. This gate removes the
instructions **without inventing facts** — a synthesised past-tense claim the record cannot support
is a falsification of the store and is the one unrecoverable failure of this gate. Leaving a
statement alone and reporting it is always available and is a correct outcome.

## Test Mode
Inspection-driven, not TDD. The deliverable is a set of writer deltas plus the resulting store
content. The existing suite must stay green; the correctness of each restatement is proved by
citing the record's own grounding, not by a test.

## Scope
Examine **all 48 records** in `episodes/active/`.

- **32 pre-#447 records are in scope for rewriting:** `issue-304-g3-*` (5), `issue-308-*` (25),
  `issue-309-*` (2).
- **16 `issue-447-*` records are believed already to honour the constraint — CHECK them and report
  the result. Do not assume it.**

Report the count as **"48 examined / 32 in scope / N restated"**.

## The Wording Standard (Commander-set; this gate applies it, it does not relitigate it)
A statement is an **OBSERVATION** when it says what was done, by whom or by what, in the run being
recorded — past tense, a real subject, no second person, no forward-aimed modal.

A statement is an **INSTRUCTION** when it is in imperative mood (a bare base-form verb opening a
sentence or clause with no subject), addresses a reader (`you`, `your`), or carries a deontic modal
aimed forward (`must`, `should`, `always`, `never` used as a directive).

**One deliberate exemption — do not "fix" it.** `task-intent` is written in the bare infinitive by
house convention: "Fix the STATE_NOTE-fallback wording gap..." is the form the store's own canonical
worked record uses at `docs/EPISODE_STORE.md:171`. That is the format, not drift. Leave `task-intent`
alone unless it addresses a reader in the second person.

**Worked contrast — use it as the model:**

- BEFORE (`issue-308-001.a5`, prescriptive): "Give the harness the same fail-safe discipline as the
  production code under test: wrap per-iteration work in try/except with a guaranteed stop-signal in
  `finally`, and mark helper threads daemon=True as a backstop."
- AFTER-SHAPE (`issue-447-005.a5`, observational): "The run paired each `-k` gate with an unfiltered
  whole-file and whole-suite run, and that pairing is what caught both defects."

Same information. No imperative mood, no second person, no forward-aimed modal.

## The hard rule — do not invent facts
Rewrite **only** into what the record itself supports. Every episode carries `task-intent`,
`expected-behavior`, `observed-behavior` and `impact-cost` alongside the `workaround`; read them and
use them to ground what actually happened. **Read the whole record before restating any assertion
in it.**

Where a statement's grounding does **not** support a factual rewrite — typically because it was
written as advice and the record never says whether it was applied — **leave it alone** and list it
as **UNGROUNDED**, with the episode id, assertion id, and the specific reason the record cannot
support a factual restatement. Gate g3 has an exception mechanism for exactly these.

Reporting an ungrounded record is a correct outcome. Synthesising a past-tense claim the record
cannot support is not.

## Also check, do not synthesise
The other agent-supplied kinds (`expected-behavior`, `observed-behavior`, `impact-cost`) and the
diagnosis assertions (`suspected-cause`, `proposed-remedy`) carry the same drift.
**`proposed-remedy` is the one most likely to.** Restate the ones that plainly instruct **and** are
grounded; report the rest.

## Doctrine candidates — collect, never promote
Several of these workarounds state what look like genuine rules that belong in `docs/agents/*`.
Collect each one into the IMPLEMENTER_RESULT: episode id, assertion id, the rule as stated, and why
it looks like doctrine.

**Do not write any of them into `docs/agents/*`. Do not create any new file to hold them.** That
boundary is absolute — promotion into doctrine is the human's decision, and a new file that
accumulates distilled advice for future agents is the retirement this issue protects, undone.

## Allowed Scope
- `episodes/active/*.md` — **only** through `python scripts/apply_episode_delta.py --store-root episodes`.
- Delta JSON files you author, written under `.agent-work/r418-460/deltas/` (local scratch, tracked
  under `.agent-work/` — keep them, they are your evidence).

## Specific Exclusions
- **Never hand-edit a file under `episodes/`.** No `Edit`, no `Write`, no `sed`. The writer is the
  only write path, and a hand-edit is an unrecoverable breach of this gate.
- **Do not touch `episodes/retired/`** — it is an archive, not a live search space, and it is empty.
- **Do not modify `scripts/apply_episode_delta.py`.** g1 shipped it and it is reviewed. If you find
  a defect in it, stop and report rather than patching it here.
- **Do not edit `docs/EPISODE_STORE.md`** — that is gate g4.
- **Do not edit anything under `docs/agents/`** (owned by the human).
- **Do not edit `scripts/checklist_engine.py` (#433), `scripts/collect_feedback.py` (#464), or
  `scripts/verify_worktree_precondition_coverage.py` (#436)** — concurrent siblings own these.
- Never create a file whose basename contains `findings`.

## Constraints
- **Pass `--store-root episodes` on EVERY `apply_episode_delta.py` invocation.** The default resolves
  against the *installed skill directory*: without it the writer silently builds a store at
  `~/.claude/skills/constellation-admiral/episodes`, outside the repo, while every gate reports
  green. Verify after your first write that `git status --short episodes/` actually shows changes.
- The `restate-assertion` op takes `id`, `assertion`, `statement`, `history`. `statement` must be a
  single line (the writer refuses newlines). `history` is the **reason** for the restatement — the
  writer quotes the original verbatim itself; do not paste the original into `history`.
- Dry-run first (`--dry-run`) and read the log before writing.
- Test command is exactly `FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests`. **Never `py` for
  pytest.** Capture the **real** exit code. Expected baseline after g1: **1742 passed, 4 skipped,
  672 subtests, exit 0** (plus any test g1's rework added — report what you actually see).
- Windows host; forward-slash absolute paths.

## Map Anchors (inbound)
- **Structural:** `docs/EPISODE_STORE.md` — record grammar and write-path doctrine (hash-pinned
  substitute; this repo ships no packet map). `episodes/README.md` — `active/` is the ordinary set,
  `retired/` the archive. `scripts/apply_episode_delta.py` — the only write path.
- **Capability:** episode record content in `episodes/active/`.
- **Constraints/assumptions:** an episode records what happened and is never read back as a rule
  (`docs/agents/ORCHESTRATOR_CONTEXT.md`, "The Retired Learning Playbook").
  `docs/EPISODE_STORE.md` §5 — the record grows rather than getting rewritten; `restate-assertion`
  answers that by preserving the original wording verbatim in the assertion's own history.
- **Decision anchors:** rewrite through `restate-assertion` rather than annotating with
  `amend-assertion`. `@grade: settled/inherited · leans g1-implement` — Commander decision under
  LO-460's Inherited Latitude, ratified by the Admiral. Not yours to unsettle.
  Which observed rules deserve `docs/agents/*` doctrine: **floated to the human, never decided
  here.** `@grade: settled/human`
- **Evidence expectations:** `FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests` with the real exit
  code; the 48 / 32 / N count.
- **Map confidence flags:** no packet map exists (`map_orient` DEGRADED-NO-MAP, discharged with four
  hash-pinned substitutes).

## Deliverable Path Check
- **Committed** — `episodes/active/*.md`; `git check-ignore episodes/active` exits **1** (not
  ignored). These are tracked files; your restatements appear in `git diff`.
- **Committed** — your delta JSON under `.agent-work/r418-460/deltas/`; `.agent-work/` is tracked in
  this repo (verified: `git check-ignore .agent-work` exits 1). They are evidence, not scratch.

## Required Evidence

**Load-bearing — prove rigorously:**
1. The **48 / 32 / N** count, derived by command over the directory, not by recall.
2. For **every** assertion you restated: episode id, assertion id, the BEFORE text, the AFTER text,
   and **the specific grounding in that same record** (which sibling assertion, quoted) that makes
   the AFTER factually true. A restatement with no cited grounding will be sent back.
3. The **UNGROUNDED list**: episode id, assertion id, and the specific reason the record cannot
   support a factual restatement.
4. The **doctrine-candidate list**: episode id, assertion id, the rule as stated, why it looks like
   doctrine.
5. `git diff --stat episodes/` and confirmation that **no file under `episodes/` was hand-edited**
   (state how you know — e.g. every change traceable to a named delta file).

**Confirmatory — a spot-check suffices:**
6. The delta files used and the exact writer invocations (each showing `--store-root episodes`).
7. `FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests` with the real exit code.

## Wiring Grep
`none — this slice adds no callable symbol; it changes stored records through an existing writer.`

## Verification Commands

```bash
cd C:/Programs/constellation-skills-wt/r418-460
FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
git diff --stat episodes/
git status --short episodes/
```

## Suggested Model Tier
Stronger (Opus). The judgment — is this sentence an observation or an instruction, and does the
record support the past-tense claim I am about to write — is the whole difficulty of this gate, and
getting it wrong writes falsehoods into the store.

## Authority
Yours: which specific records are prescriptive under the stated standard; the exact AFTER wording;
which are ungrounded; the delta file structure.

Not yours under any framing: the wording standard itself; promoting anything into `docs/agents/*`;
creating any file that accumulates advice for future agents; hand-editing `episodes/`; changing
`scripts/apply_episode_delta.py`.

## Stop Conditions
Stop and return if: `episodes/` would have to be hand-edited; the writer refuses an op you believe is
correct; you cannot ground a restatement and are tempted to synthesise one (report it UNGROUNDED
instead — that is not a stop, it is the designed outcome); scope must be exceeded; the suite goes
red for any reason other than your own work.

## Return Format
Write **IMPLEMENTER_RESULT** to
`C:/Programs/constellation-skills-wt/r418-460/.agent-work/r418-460/crew-handoffs/g2-implement-result.md`:
completed slice, files changed, evidence produced (items 1-7 above, with the per-restatement
grounding table), assumptions used, stop conditions hit, out-of-scope observations, workflow
feedback. That file is what the Commander verifies; a result returned only as chat text does not
count.
