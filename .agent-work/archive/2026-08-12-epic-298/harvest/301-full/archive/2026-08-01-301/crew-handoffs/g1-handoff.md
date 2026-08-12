# Implementer Handoff

## Gate
`g1` — episode record grammar and store doctrine (issue #301, epic-298)

## Task

Write **`docs/EPISODE_STORE.md`**: the record grammar, the partition, the retirement policy,
and the Stratum A mapping for a durable episode store — plus establish the store directory at
a **git-tracked** path with at least one tracked file so the layout survives a commit.

This gate ships **no executable code**. It freezes the contract that gates g2 (the validated
writer) and g3 (retrieval) build against.

## Protected Intent

In priority order — these are pre-ruled obligations, not preferences:

1. **Non-foreclosure.** An episode must be expressible as assertions under the Stratum A truth
   model **without rewriting the record later**. A design that satisfies this only by a future
   migration has *not* satisfied it.
2. **Durability past consolidation.** Retired never means deleted. The structured episode
   outlives its consolidation so rhymes stay findable across runs.
3. **The partition is explicit** — visible in the file, not implied by field naming.
4. **The agent-supplied half stays deliberately small.** Agent effort is a real cost.

## Test Mode

**Inspection-only.** The deliverable is prose plus a directory; there is no runtime behavior to
test at this gate. The operative invariants are pre-authored as the close criteria below so you
verify a frozen chain rather than inventing test-shaped proxies (grep-for-marker checks and the
like). Do **not** add tests to `tests/` in this gate — g2 and g3 own the test surface.

## Close Criteria

Each is a gate postcondition I will verify. Prove each one.

- **C2 — the partition is documented as literal section headings**, enumerating which fields
  belong to which bin. A reader must never infer bin membership from a field's name.
  - *Mechanically captured* (zero agent effort, from engine/harness state): run/project, role,
    active spine step, context manifest reference at a revision, refusals, reopens, rework
    counts, failed commands, artifact references.
  - *Agent-supplied* (deliberately small): task intent, expected behavior, observed behavior,
    impact/cost, workaround.
- **C3 — the retirement POLICY is stated, and the retirement LAYOUT is left open.**
  - Policy (settled, document it): retired means **excluded from ordinary rhyme-search and
    RETAINED in history**; never deletion or truncation; a non-empty reason is **required**.
  - Layout (**HELD — do not choose**): whether retiring **moves the file** between `active/`
    and `retired/`, or **changes a status field** filtered negatively. Document it as a named
    **open seam**, state both options and their trade-offs, choose **neither**, and say it is
    held for human ratification and will be bound at gate g4.
- **C4 — a concrete field-by-field Stratum A mapping**, against a worked example, not a
  promise. Map each of: identified assertion, source, supporting evidence, challenging
  evidence, qualitative strength (weak/medium/strong). Show **lifecycle standing as a separate
  dimension from belief strength**.
- **C5 — per-field assertion addressability in the agent-supplied bin only.** Each of the five
  agent-supplied fields is individually addressable with its own lifecycle standing, so one can
  be **disputed while another stays active, with no rewrite of the record**. Mechanical facts
  stay flat `- key: value` lines and carry **no** strength and **no** standing.
- **C6 — the store lives at a GIT-TRACKED path, and the doc says why.** See "The tracked-path
  requirement" below. Store root resolves through **one named seam**; it must **not** call
  `durable_root()`.
- **C7 — the doc states the store is mechanical and never guesses**: no ranking, no similarity,
  no embedding. Finding that two episodes *rhyme* is a downstream LLM sensor job owned at issue
  #308; the store's job is to hand that sensor a clean, complete, enumerable candidate set. The
  doc also states the obligation on issue #300's projection manifest: an enumerable set of
  `(loaded-artifact-id, canonical-revision)` pairs.
- **C8 — choose the episode-id scheme ON ITS OWN MERITS and record the reasoning.** Do **not**
  cite it as a panel finding: that unanimity claim was retracted (only 2 of 4 design candidates
  used run-id + sequence; the other two used descriptive slugs). Decide it fresh and say why.
- **C9 — the doc states how cross-worktree sharing actually works**: through **git itself**
  (commit on a branch, merge to main, visible in every worktree and every later clone). Say
  explicitly that this needs no `durable_root()`, is unaffected by the epic-lease exception,
  and is unaffected by the read-only fence on the main checkout because each commander writes
  only its own worktree.

## The tracked-path requirement — read this carefully, it is the gate's sharpest constraint

I verified at HEAD:

```
$ git check-ignore .agent-work/episodes/ ; echo $?     # 0  -> IGNORED
$ git ls-files .agent-work/ | wc -l                    # 0  -> nothing under it is in git
$ git check-ignore episodes/ ; echo $?                 # 1  -> NOT ignored, trackable
```

`.gitignore` line 1 is `.agent-work/`. **Nothing under it is in git — `LESSONS.md` itself is
not in git.**

The four design candidates all placed the store at `.agent-work/episodes/`. That would make the
store *not* Markdown in git and destroy it when the worktree is swept — violating
`decision:markdown-in-git`, the one settled, human-given storage ruling. They inherited the
location from `LESSONS.md`, which is a deliberately **transitory inbox** ("where lessons pass
through, not where they live"). The episode store is the **opposite**: it must outlive its
consolidation.

**So: put the store at a tracked path.** Use repo-root **`episodes/`** unless you have a
concrete reason for another tracked location — if you deviate, say why. Because git does not
track empty directories, ship at least one tracked file under it (a `README.md` explaining the
directory is ideal — a bare `.gitkeep` is acceptable but less useful).

## Allowed Scope

- `docs/EPISODE_STORE.md` (new)
- `episodes/` (new directory) plus its one tracked file
- No other files.

## Specific Exclusions

- **Do NOT modify `.agent-work/LESSONS.md` or `scripts/apply_lessons_delta.py`** (owned by the
  live lessons machinery; cutover is ruled at issue #308, not here). Read them as prior art.
- **Do NOT design issue #300's projection manifest** — running concurrently in another
  worktree. You may state an *obligation* on it; you may not specify it.
- **Do NOT build capture wiring** (issue #305) or **consolidation / rhyme-search** (issue #308).
- **Do NOT choose the retirement layout** (held for human ratification; bound at g4).
- **Do NOT write executable code or tests** in this gate.
- Do not create `docs/agents/engine-config.json` — its absence is a sanctioned degradation.

## Constraints

- **Markdown in git only.** No database, no query language, no backend, no index server.
  "Queryable" means findable by deterministic means over Markdown in git.
- **The stochastic boundary (spec B0.1):** stochastic work happens upstream of canon; between
  canonical truth and an agent's active surface every transformation is deterministic and
  attributable. The store is the **mechanical** half and never guesses.
- **Suspected cause and proposed remedy are separate, OPTIONAL assertions** — not ordinary
  fields of either bin. An episode with no diagnosis is complete and valid.
- Rhyme with `apply_lessons_delta.py`'s Markdown grammar where it earns its keep (`- field:
  value` lines, append-only history entries, a validated all-or-nothing delta as the only write
  path). Depart where the episode store's different job demands it — and **say so explicitly**
  when you depart.

## Map Anchors (inbound)

- **Structural:** `scripts/apply_lessons_delta.py` (699 lines — the neighbour whose grammar and
  write seam this rhymes with; **read, never edit**); `scripts/agent_work_root.py` →
  `durable_root()` (**read to understand why it is NOT used here**); new: `docs/EPISODE_STORE.md`,
  `episodes/`.
- **Capability:** episode capture and retrieval — created by this run; zero prior art at HEAD
  (`grep -ril "episode\|stratum\|rhyme"` returns nothing).
- **Constraints:** `constraint:markdown-in-git`; `constraint:stochastic-boundary-B0.1`;
  `constraint:retired-is-excluded-not-deleted`.
- **Decision anchors:**
  - `decision:episode-store-shape` — the record shape and retirement mechanism.
    `@grade: settled/human · leans g1,g2,g3,g4 · settle: held for Tommy; NOT yours to choose`
  - `decision:agent-bin-gets-assertion-addressability-mechanical-bin-does-not`
    `@grade: guess · leans g1,g2 · settle: at #308, whether a consolidation ever needs to dispute a mechanical fact`
  - `decision:store-lives-at-a-tracked-path` — commander decision under latitude this gate.
    `@grade: settled/measured · leans g1 · settle: git ls-files episodes returns non-empty`
- **Evidence expectations:** `claim:the-partition-is-documented-not-implied`;
  `claim:non-foreclosure-is-shown-not-promised`.
- **Map confidence flags:** issue #300's manifest is live and unverified in a concurrent
  worktree — state it as an **obligation**, never assume its implementation.

## Deliverable Path Check

- **Committed** — `docs/EPISODE_STORE.md`; `git check-ignore docs/EPISODE_STORE.md` exits **1**
  (not ignored). Verified before dispatch.
- **Committed** — `episodes/` and its tracked file; `git check-ignore episodes/` exits **1**.
  Verified before dispatch.
- Both are **new** files: they are untracked until staged, so `git diff` shows nothing and they
  appear only in `git status` until added.

## Required Evidence

**Load-bearing — prove these rigorously:**

1. The Stratum A mapping (C4) and the per-field addressability (C5), shown against a **worked
   example** of a real filled-in episode as it would appear on disk. Include a concrete
   walk-through of disputing one agent-supplied field while a sibling stays active, showing
   what changes and what does not.
2. The tracked-path requirement (C6): paste the output of `git check-ignore episodes/; echo $?`
   and `git status --short episodes/` showing the file is present and stageable.
3. The retirement layout is genuinely left open (C3) — quote the section where both options are
   stated and neither chosen.

**Confirmatory — a spot-check suffices:** C2, C7, C8, C9.

## Verification Commands

```bash
git check-ignore episodes/ ; echo "exit=$?"     # expect exit=1 (NOT ignored)
git status --short episodes/ docs/EPISODE_STORE.md
python -m pytest tests/ -q                       # expect unchanged green: 1157 passed, 2 skipped
```

Note: use `python`, **not** `py` — on this host `py` resolves to a runtime with no pytest and
reports "No module named pytest", which reads like a broken suite.

## Suggested Model Tier

`simple bounded` — the hard design choices are already made or explicitly held; this gate turns
a settled contract into prose plus a directory.

## Authority

**Already decided — do not re-litigate:**
- Markdown in git (human ruling, supersedes an earlier exploration finding favoring a graph DB).
- The store lives at a git-tracked path (commander decision under latitude, this gate).
- The partition, the retirement *policy*, and the non-foreclosure obligation (pre-ruled).
- The store is mechanical; rhyme detection is downstream at #308.

**You must NOT decide alone — stop and return instead:**
- The retirement **layout** (file-move vs status-field). Held for human ratification.
- The overall record shape, if you find yourself wanting to depart materially from the
  partition + optional-diagnosis + per-field-addressable-agent-bin structure above.
- Anything requiring a change to `LESSONS.md`, `apply_lessons_delta.py`, or issue #300.

**You may decide** (log it): the episode-id scheme (C8, decide on merit); the exact field names
and their ordering; the doc's structure; whether the tracked file under `episodes/` is a README
or a `.gitkeep`.

## Stop Conditions

Stop and return if: allowed scope must be exceeded; a specific exclusion must be touched;
required evidence cannot be produced; or a decision outside the given authority is needed —
especially if satisfying the non-foreclosure obligation seems to require choosing the
retirement layout (it should not; if it does, that is a finding I need).

## Return Format

Return **IMPLEMENTER_RESULT**: completed slice, files changed, test mode satisfied, evidence
produced (with the pasted command output above), assumptions used, stop conditions hit,
out-of-scope observations, and **workflow feedback** — what in this handoff or the workflow made
the work harder than it needed to be. The workflow-feedback section is harvested into the run's
lesson pool; please do not leave it empty.
