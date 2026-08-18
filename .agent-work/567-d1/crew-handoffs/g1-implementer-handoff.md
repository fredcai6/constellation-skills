# Implementer Handoff

Work id: `567-d1` · Worktree: `/home/tommy/projects/constellation-skills/.worktrees/567-d1-doctrine-sweep-guard`
Branch: `feat/567-d1-doctrine-sweep-guard`

## Gate

`g1-implement` — Author the regrowth guard against the DIRTY tree.

## Task

Create **one new file**, `tests/test_cli_retirement_guard.py`: the guard that closes issue #559.

Issue #559 is *"the door is the interface, not a second path — remove the CLI fallback for
agents."* The instruction corpus under `skills/` tells agents to drive the checklist engine from
the command line instead of through the MCP door tools. **That text has been deleted twice and has
grown back twice.** The deliverable of this epic is therefore not the deletion — it is the guard
that makes the third deletion stick.

**The guard lands BEFORE the sweep, and that ordering is deliberate.** A guard authored after the
corpus is clean can only be red-proofed against a scratch string its own author chose, which any
pattern passes. Authored now, against the unswept tree, its RED is produced by the real corpus.

## Protected Intent

The guard must **fail today**, naming real sites. A guard that passes on this tree is wrong, and a
guard that fails for the wrong reason (import error, empty walk) is also wrong.

## Test Mode

Test-first in the strict sense: this gate's entire deliverable **is** a test, and the gate closes
on that test being RED for the right reason. Do not sweep anything. Do not make it green.

## Close Criteria

1. `tests/test_cli_retirement_guard.py` exists and collects cleanly.
2. Running it **FAILS**, and the failure output names real target sites.
3. The failure names a census consistent with the measured baseline: **15** `CLI fallback`
   occurrences across 11 files under `skills/` (13 belong to this lane; 2 under
   `skills/workbench/` belong to lane D2), and **9** `<engine>` tokens under `skills/`.
4. The guard states the **count** of texts and files it scanned.
5. No instruction file is modified. `tests/test_mcp_adoption.py` is **not** modified in this gate.

## Allowed Scope

- **Create**: `tests/test_cli_retirement_guard.py`
- Nothing else. Read anything you like.

## Specific Exclusions

- Do **not** edit `tests/test_mcp_adoption.py` (gate g2 inverts it).
- Do **not** edit any file under `skills/`, `specs/`, `docs/`, `scripts/`, or `episodes/`.
- Do **not** touch `skills/workbench/**`, `scripts/mcp_spine_server.py`, `scripts/run_crew.py`,
  `scripts/checklist_engine.py`, `map/INDEX.md` — other lanes own them this wave.

## Constraints

1. **NO exception list.** If a file must be excluded, exclude it by **a rule the walk applies**,
   never by naming the file. A sibling guard's exception list reached 11 entries across five runs;
   that decay is the named failure mode you are avoiding.
2. **Assert against the text's absence**, never against a description of the rule. A guard that
   greps for a doctrine sentence is the failure this epic is about.
3. **A guard that loops must assert what it looped over.** State the count and assert a floor, so
   it cannot pass vacuously on an empty or narrowed corpus.
4. **Catch the behaviour, not one spelling.** Measured in this tree, the clause has **three**
   surface forms: `CLI fallback:` ×10, `CLI fallback,` ×4, `CLI fallback ` ×1. A colon-only
   pattern misses a third of them.
5. The failure message **quotes the ruling verbatim** rather than citing a location — this lane may
   not write `docs/agents/*` and files no issue, so any pointer would dangle.

## Map Anchors (inbound)

There is **no architecture map in this repo** — `map_orient` returns `DEGRADED-UNPARSEABLE`
(`docs/architecture` absent, `map/ids.jsonl` empty). Your map entry points are instead:

- **`tests/test_mcp_adoption.py`** — read `_walk_instruction_files` / `INSTRUCTION_FILES` (~line
  424) and `_instruction_texts` / `_json_strings` (~line 440–470). This is the repo's own
  machine-readable definition of "agent-facing instruction text", and your scope reuses it.
- **`tests/test_mcp_adoption.py:838`** — `TestTier2SpineAlreadyBoundForDispatchedCrews`. **Read
  this first.** It already asserts *absence* for two files and pins the human ruling verbatim.
  Your guard is a **generalization of this existing precedent** from 2 files to the whole corpus.
- `.agent-work/567-d1/notes-1.md` — the measured baseline and site enumeration.
- `.agent-work/567-d1/plan-rigor/CONVERGENCE.md` — the design convergence and the critic findings
  that shaped this gate.

### Scope expression (settled — do not redesign it)

Reuse the `INSTRUCTION_FILES` walk (rglob over `skills/` for `.md`/`.json`), **extended** to cover
`specs/**/*.toml`. Import it from `tests/test_mcp_adoption.py` or re-derive it locally — your call,
but say which and why; if you re-derive, the two must not be able to drift silently.

Measured, and why this needs no exception list: that walk puts **all 10 target files IN**, and puts
**both sites that must survive OUT** by the structural rule alone —
`docs/superpowers/plans/2026-06-27-delegated-autonomous-commander.md:59` (a historical plan record)
and `scripts/init_work_area.py:24` (a comment documenting the placeholder convention itself). It
also excludes `episodes/**`, `tests/fixtures/`, and `tests/data/`. **Exception list length: zero.**

### Patterns to catch (at minimum)

1. The `<engine>` placeholder token.
2. `CLI fallback`, case-insensitive, in **any** punctuation form.
3. A literal `checklist_engine.py` invocation in agent-facing text — this is what a rename-around
   looks like once the phrase is gone, and without it the guard is defeated by rewording the clause
   to "run the engine script directly."

## Deliverable Path Check

`git check-ignore tests/test_cli_retirement_guard.py` → exit **1** (not ignored). Verified.
`git check-ignore .agent-work/567-d1/crew-handoffs/g1-implementer-result.md` → exit **1**. Verified.

## Required Evidence

- The guard's **RED output, verbatim**, including its stated scan counts and the sites it names.
- The exact command you ran.
- A statement of how many files and how many texts the walk covered.

## Wiring Grep

`none — this slice adds no callable symbol.` The deliverable is a pytest module; pytest's own
collection is the wiring, and close criterion 1 (it collects) plus 2 (it runs and fails) exercise
it. Confirm collection explicitly with `--collect-only` so "it failed" cannot be an import error
misread as a finding.

## Verification Commands

POSIX form, absolute paths, run from the worktree root:

```sh
cd /home/tommy/projects/constellation-skills/.worktrees/567-d1-doctrine-sweep-guard
python3 -m pytest tests/test_cli_retirement_guard.py --collect-only -q
python3 -m pytest tests/test_cli_retirement_guard.py -q          # MUST fail
git status --porcelain                                            # only the new file
```

The gate's own closing check, which the Commander re-runs independently:

```sh
test -f tests/test_cli_retirement_guard.py \
  && ! python3 -m pytest tests/test_cli_retirement_guard.py -q > /tmp/g1-guard.log 2>&1 \
  && grep -qiE 'CLI fallback|<engine>' /tmp/g1-guard.log
```

## Suggested Model Tier

**Opus**, with elevated reasoning effort. This is the epic's headline deliverable and the wave's
load-bearing unknown: the guard must discriminate a legitimate mention from a reintroduction, and a
pattern chosen carelessly either misses a third of its targets or red-lights honest text.

## Authority

Commander `567-d1`, under Admiral launch order `cmdr-567-d1` (epic #567, wave 2, lane D1).

## Stop Conditions

Stop and return if: you cannot make the guard fail for the right reason; the scope expression turns
out not to cover a target or to catch a survivor (re-measure and report — do **not** patch it with
an exception list); or the task would require editing a file outside Allowed Scope.

## Return Format

Write the full `IMPLEMENTER_RESULT` to
`.agent-work/567-d1/crew-handoffs/g1-implementer-result.md` **before ending your turn** — that
write is the delivery. Include a `Return status` field whose value is exactly `complete` (lowercase)
when the close criteria are met. Include a `Workflow Feedback` section: what helped, what got in
the way, and your own mistakes.
