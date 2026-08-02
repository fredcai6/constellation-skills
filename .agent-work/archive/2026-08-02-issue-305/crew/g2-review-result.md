# Reviewer Result — g2-review (issue #305, epic #298)

**VERDICT: BLOCK** — 3 blockers, all in the `reopens` / two-witness reconciliation area.
Everything else in the gate is sound and, more importantly, *mutation-proven* sound.

Survey: `.agent-work/issue-305/g2-review/review.json` (16 items, all visited, consolidated
`BLOCK`, 5 findings). Fowler record: `.agent-work/issue-305/g2-review/fowler-pass.json`
(`verify_fowler_pass.py` exits 0). Crew id
`constellation/issue-305/g2-review/reviewer/attempt-1`.

---

## 1. HUNT 1 — your proof, and the fix shape

### Is the proof sound? **Yes. And the defect is LIVE, not latent.**

I audited the route rather than re-running the claim. `skip`-after-escalation is not
merely *a* reachable continuation — **it is the only one**, which makes your route
canonical rather than convenient:

- `skip` (`checklist_engine.py:1765-1769`) has **no status guard at all**. It skips
  anything, blocked included.
- `resume` refuses (`:1811-1817`) — **confirmed**. The escalation branch sets
  `status_detail` with **no** `prior_status`, and `resume` requires
  `prior in ("pending","in-progress")`. Its own refusal text names the sanctioned exit:
  *"use `reopen`/`skip` or a human decision, not `resume`."*
- `reopen` refuses a `blocked` gate (needs `complete`).
- `start` refuses too, and this is the load-bearing bit: `TERMINAL = {"complete","skipped"}`,
  so a **blocked gate is non-terminal** and `active_id()` keeps returning it. No later gate
  can be started while the escalated one sits there.
- `amend --drop` refuses a non-pending gate.

So the only way past a cap-escalated gate is to make it terminal, and `skip` is the only
verb that does. Your route is the **unique** one. **LIVE.**

### One measurement your proof did not make — it narrows the defect without weakening it

I built an independent repro that reaches the over-count through the **`reopen` seam**
instead, with no `skip` at all (2 gates, cap 1, `reopen b` → `advance b` → `reopen b`
ESCALATES → `reopen a`). **It came back green** — snapshot `reopens: 2`, ground truth 2 —
even though the journal held 3 `reopen` lines and `rework_total` was 2 at the end.

Why: the journal line for the *in-flight* verb is written by `main()` **after** the verb
returns, so at a `reopen` seam the journal witness is short by exactly one. The arithmetic:

| seam | journal witness at emit | rework witness | `max` | over-count |
|---|---|---|---|---|
| `start` | `T + E` | `T` | `T + E` | **`E`** |
| `reopen` | `T + E − 1` | `T` | `T + E − 1` | **`E − 1`** |

(`T` = true reopens, `E` = escalations.) So a **single** escalation is exactly cancelled at
a `reopen` seam and is only visible at a `start` seam — which is precisely the seam your
repro uses. Your proof is correct and lands on the only seam where `E=1` shows. It is
narrower than "the field over-counts everywhere," and that is worth stating in the PR body.

### Ruling on fix shape: **B**, with a hard condition

**Option A's load-bearing premise is CONFIRMED.** I verified it at source, since you flagged
it as yours. The escalation appends a distinctive `cl["blockers"]` entry
(`blocker: "rework cap N exceeded: ..."`, `next_action: "escalate; do not re-dispatch"`),
and **nothing can remove it**: `resume` refuses the gate *before* reaching its blockers
filter, `amend --drop` refuses a non-pending gate, and `skip` leaves `blockers` untouched.
Escalations are durably countable, and A is arithmetically sound at **both** seams
(`max(T, T) = T` and `max(T−1, T) = T`).

**I still rule for B — drop the journal witness, use `_rework_total()` alone:**

1. **A fixes the instance; B removes the class.** A keeps the over-counting witness and
   compensates by string-matching engine-authored, human-readable text *from
   `episode_capture.py`* — a new cross-module coupling in the module explicitly ruled not to
   change engine behaviour. Reword the escalation message and A silently regresses to
   over-counting, with no test to catch it (see B2 below).
2. **The docstring's stated reason for the journal does not survive.** You asked me to check
   this: it does not. *"At the first mutating verb of a run there is no journal file yet"* is
   an argument against a journal-**only** source. `_rework_total()` is not journal-anything —
   it reads in-memory and returns `0`, never `None`, for any well-formed checklist. B has no
   first-mutating-verb gap at all.
3. **B deletes `find_spine_path` + `journal_reopens`** (~60 lines, including a
   `work_id`-AND-`items` disambiguation heuristic with an untested silent-`None` branch)
   whose only consumer is a `max()` that nothing discriminates.

**B's honest cost:** it loses the amend-drops-a-gate recovery. That path is reachable (a
`reopen` cascade resets a downstream gate to `pending`, and a `pending` gate with
`rework_count > 0` *is* droppable), and B under-counts there. A preserves it. I weigh that
below (1)–(3) because it is an **under**-count on a narrow path that is untested today either
way, and under-counting is the direction the field's own doctrine already concedes.

**C rejected** — the witnesses legitimately disagree in the amend case, so refusing would
blank the field in ordinary runs.

**Hard condition on whichever you pick:** it must ship with a test that **mutation M5 fails**.
That is the real deliverable here, not the arithmetic — see B2.

**Constraint respected:** both A and B live entirely in `episode_capture.py`. Neither
touches how `reopen()`/`main()` journal.

---

## 2. HUNT 1 class sweep — every writing branch

### `rework-count` — **CLEAN**
- **Only writer:** `reopen()`'s success branch, `:1880`, `+1`.
- The escalation branch `:1870-1879` **deliberately does not touch it** — which is exactly
  why this field is right and `reopens` is wrong. Same event, two witnesses, one honest.
- `amend --add` initialises `0`; `amend --drop` / `--rescope` refuse any non-pending gate.
- Nothing decrements. The only loss is a whole task disappearing, which surfaces as a
  **refusal**, not a wrong value.

### `failed-commands` — **CLEAN**
- **Only writer:** `_check_condition`'s `command` branch, `:771`. The `git-change-policy`
  branch writes type `artifact-policy`, not `command-output` — so it cannot contaminate.
- **Nothing anywhere deletes evidence** (grepped). `reopen` *supersedes*, never removes, and
  the composer deliberately counts superseded items.
- Survives a refusal as documented: the evidence item is appended before the raise and
  `main()` persists on the error path.
- Re-running a failing check appends another item, so a retried `advance` inflates the count.
  **This is stated intent, not a defect** — `test_failed_commands_tracks_real_non_zero_command_checks`
  pins exactly that as `2`.

### `refusals` — **NOT CLEAN. This is the same class as HUNT 1.**

**A foreign session's refusal increments the owning run's tally.** Measured, not reasoned:

```
claim --session-id own            -> refusals: 0
start a --session-id own          -> refusals: 0   (success does not move it)
start a --session-id own          -> refusals: 1   (real refusal)
start b --session-id SOMEONE-ELSE -> refusals: 2   <-- lease conflict, exit 1, NOT this run
```

The field is **file-scoped**, not run-scoped — yet both `docs/CHECKLIST_SCHEMA.md` ("the
refusals this checklist's **run** has taken") and `episode_capture.py:452-455`
("`refusals` is run-scoped") assert otherwise. This is your HUNT 1 class exactly: *a witness
assumed attributable to this run, movable in the over-counting direction by a party outside
it.* And in a constellation it is not exotic — any teammate, Commander poll, or stale-lease
retry against a crew's checklist does it. Every `MUTATING_VERB` refusal from a wrong or
absent `--session-id` counts. (`current` and `--dry-run` are correctly excluded — both
verified.)

---

## 3. HUNT 2

### Per-field derivation trace — all eleven DERIVED, and proven by mutation, not inspection

| field | source | non-default value confirmed live |
|---|---|---|
| `run` | checklist `work_id` | ✓ |
| `project` | parent of `git rev-parse --git-common-dir` | **refuses** outside a repo ✓ |
| `role` | `engine_session.claimed_by` | ✓ |
| `spine-step` | imported `active_id()`, not re-derived | ✓ |
| `rework-count` | task counter | 1 ✓ |
| `failed-commands` | engine-written `command-output` evidence | 1 and 2 ✓ |
| `reopens` | two witnesses | 1 and 2 ✓ (**defective — §1**) |
| `context-manifest-ref` | manifest's own blob OID | matches `git hash-object` in the world ✓ |
| `artifact-ref` | engine's `_collect_changed_files` | ✓ |
| `refusals` | armed counter | 1 and 2 ✓ (**scoping defective — §2**) |

`project` **refuses rather than guesses** with no git — confirmed in the world (my temp-dir
repro emitted no `project` key), and it correctly avoids `durable_root()`, which would have
named the epic worktree `e298-305`. `validate_delta()` was relied on for nothing but shape.

### `refusals` — additivity, schema match, and the did-NOT-move proof

- **Additive — proven in the world.** I built a genuine pre-counter checklist (claimed, then
  the `refusals` key deleted) and drove it: `current` still exits 0, a successful `start`
  still works, **a real refusal leaves the key ABSENT** rather than writing `1`,
  `mechanical_fields()` refuses the field, and a manifest still builds. Every reader works.
- **Did NOT move on success — proven.** After a successful `start` the counter stayed `0`;
  the next (refused) `start` took it to exactly `1`; a `--dry-run` refusal left it at `1`.
  This is the case a one-sided test misses and it is genuinely covered
  (`test_a_successful_verb_does_not_move_the_counter`).
- **Arming placement correct:** `cl.setdefault("refusals", 0)` sits *after* `claim`'s
  idempotent-resume early return (`:931`), so a same-session re-claim cannot backdate a `0`
  over refusals that really happened.
- **`docs/CHECKLIST_SCHEMA.md` does NOT match the implementation on two points:**
  1. *"It is written by the CLI boundary alone, never by a verb function"* — but the arming
     write `cl.setdefault("refusals", 0)` is **inside `claim()`, a verb function**. The doc's
     own next bullet says "Armed by `claim`", so it contradicts itself one line later.
  2. It justifies run-scoping because a refusal does not always name a task, citing
     "an unknown item id, a lease conflict, **a malformed verb**" — but **a malformed verb
     exits through argparse with code 2 before the checklist is ever loaded**, so it is never
     counted. Measured: `checklist_engine.py frobnicate a` → exit 2, counter unmoved.
  3. And per §2, "run-scoped" should read "checklist-scoped", with the cross-session
     contamination stated.

  Per your own ruling these are shipped defects, not nits — the schema doc was a condition of
  the counter being in scope.

### My independent mutation — 7 call-site mutations, none of them the implementer's

Every one breaks a **call site**, not a callee. **6 caught, 1 survived.** All reverted;
`git diff --stat scripts/` is empty.

| # | mutation (call site) | result |
|---|---|---|
| M1 | delete the `emit_mechanical_snapshot(...)` call inside `emit_step_manifest` | **CAUGHT** |
| M2 | delete the `refusals` increment in `main()`'s refusal path | **CAUGHT** |
| M3 | delete the `setdefault` arming in `claim()` | **CAUGHT** |
| M4 | `fields["failed-commands"] = 0` (plausible constant) | **CAUGHT** |
| M6 | `fields["rework-count"] = 0` (plausible constant) | **CAUGHT** |
| M7 | `project_name(base_dir) or 'constellation-skills'` (guess, don't refuse) | **CAUGHT** |
| **M5** | **`reopens = _rework_total(checklist)`** — drop the two-witness `max` | **SURVIVED (63 passed)** |

**M1 is the answer to "is the wiring ceremonial?" — it is not.** Deleting the call site goes
red. Likewise the constant-returning defect this whole gate exists to catch (M4, M6) and the
refuse-don't-guess doctrine (M7) are genuinely excluded.

**M5 is a blocker.** Replacing the *entire* two-witness reconciliation with `_rework_total`
alone leaves **all 63 episode tests green**. The `max()` — the most intricate part of the
composer, the exact locus of the HUNT 1 defect, and the sole reason `find_spine_path` and
`journal_reopens` exist — has **no discriminating test whatsoever**. The implementer cited
`test_reopens_is_run_scoped_where_rework_count_is_step_scoped` as pinning a run where the two
differ (2 vs 1); that test distinguishes **run** scope from **step** scope, and run-scoped
`_rework_total` also sums to 2, so it does not touch the journal witness at all.

Consequence for §1: whichever fix you pick lands on code that no test currently constrains.
That is why the discriminating test, not the arithmetic, is the deliverable.

### `docs/EPISODE_STORE.md:781` — **TRUE as written** ✓

Confirmed against `apply_episode_delta._validate_create` (`:865-925`): `agent_supplied` is
required, must contain **exactly** the five `AGENT_SUPPLIED_KINDS` (extras rejected in both
directions), and each payload is validated non-empty. So "a complete episode cannot exist
without an agent asserting..." is literally enforced, and the rewrite no longer promises the
automated creation `_validate_create` forbids.

### `#344` latency claim — **TRUE and correctly stated** ✓

Both halves live in `scripts/` and reach real runs only through installed bundles. The
run's own emitted snapshot carries `refused: ["refusals"]`, which is that latency made
visible rather than papered over. Both rejected mitigations (default-to-0, self-create-on-first-refusal)
would indeed have fabricated.

### Both-sides / multi-element audit — mostly met, one real gap

- `failed-commands`: both sides ✓ (a failing check counted; a passing check explicitly not)
  **and** multi-element ✓ (asserted `2`).
- `refusals`: both sides ✓ (refusal moves it; success does not) plus the absence case.
- `project`: repo / linked-worktree-under-epic-lease / non-repository ✓.
- **GAP:** `find_spine_path`'s predicate is `matches[0] if len(matches) == 1 else None` — a
  collection quantifier whose **2-or-more branch no test reaches**, and there is no zero-match
  case either. That branch is the guard against reading another run's journal as this one's,
  and **multi-checklist work areas are live in this very repo**:
  `.agent-work/issue-305/` holds both `spine.json` and `execute.json` with journals.
- Lesser: `test_reopens_is_refused_only_when_no_witness_can_be_read` admits in its own
  docstring that `mechanical_fields` never reaches the branch it tests (it exercises the
  helper directly — honest, but note it); and `refusals >= 0` has no non-int/negative case.

---

## 4. HUNT 3 — your three claims: **all three CONFIRMED**, plus the collision ruling

1. **`write_manifest` returns `Path(path)`** ✓ — it ends `return destination` where
   `destination = Path(path)`. The collapsed `return destination` is value-identical to the
   old `return cm.write_manifest(...)`. The collapse also preserves write-if-absent, since
   the guard tests the same `destination` object the write uses.
2. **`emit_mechanical_snapshot` swallows its failures** ✓ (`:562-563`, `except Exception:
   return None`), so a broken snapshot cannot be misreported as a failed **manifest** via the
   stub path. **One precision correction:** it swallows every `Exception`, not every
   `BaseException` — a `KeyboardInterrupt`/`SystemExit` still propagates. That is correct and
   matches `emit_step_manifest`'s own `except`, but your wording was slightly stronger than
   the code.
3. **The asymmetry is documented and justified** ✓ (`:514-521`), and the justification holds:
   the pin is over the **manifest's** bytes, so refreshing the snapshot costs the manifest's
   guarantee nothing.

### The collision you did not rule on: **right by DESIGN, not by accident**

`snapshot_path` collides across a start/reopen pair and a `reopen` destroys the original
activation reading. I confirmed nothing depends on the original:

- **No reader exists.** Grepping `scripts/` finds no consumer of the `mechanical/` path
  outside the writer itself.
- **The frozen record survives.** `context-manifest-ref` pins the **manifest**, not the
  snapshot, so the delivery record the pin protects is untouched by the overwrite.
- **The docstring states the consequence plainly** before anyone can be surprised by it: what
  lands is a step-*activation* reading, and `reopen` refreshes it with the previous attempt's
  totals.

That is design, not accident. **Observation, not a blocker:** because it is by design, the
original activation reading is unrecoverable, so any future consumer wanting
activation-vs-completion deltas needs a second seam on `advance` — which the docstring
correctly declines to add here.

---

## 5. Deviations

**None material.** Every hunt was implementable as written. Three notes:

- **HUNT 1** told me not to re-prove the defect, and I did not. I audited the *route* and
  built a **different** repro to test the boundary of your claim — which is how the
  `reopen`-seam masking surfaced. That is within "audit my proof, not the claim."
- **Where the code contradicted the handoff, I said so:** the handoff's HUNT 3 claim (ii)
  ("swallows every exception") is `Exception`, not `BaseException`. Immaterial, stated for
  completeness. Nothing else contradicted.
- **`#359` not re-raised.** I did check whether the scope is wider than the four named
  surveys, per your instruction; I found no evidence that it is.

**Deliberately not raised as findings** (rulings in force): the seam placement, the
episode-store location, `#327`, `#362`, `#359`.

## Triage candidates

1. **`refusals` is checklist-scoped, not run-scoped** — cross-session contamination (§2).
   Needs either session-filtered counting or a doc correction; the field's meaning changes
   either way.
2. **`find_spine_path`'s multi-match branch is untested** and live multi-checklist work areas
   exist in-repo (§3). Moot if fix B is taken — the function goes away.
3. **Shotgun surgery on the eleven-field group** — spelled out in five places
   (`mechanical_fields`, `REQUIRED_MECHANICAL_FIELDS`, `apply_episode_delta`'s three
   constants, `query_episodes._FIELD_READERS`, the prose) with no mechanism that fails when
   one is missed. Latent while the group is frozen; file it against unfreezing.
4. **Falsified invariants still shipped in prose:** `episode_capture.py:365-369` and
   `test_a_missing_journal_is_covered_by_the_second_witness`'s docstring both assert "neither
   can over-count." Both must be corrected with the fix — a *wrong* comment is a correctness
   defect.

## 6. Suite

```
cd C:/Programs/constellation-skills-wt/e298-305 && python -m pytest -q
1470 passed, 2 skipped, 472 subtests passed in 70.60s (0:01:10)
```

Matches the handoff exactly. (The implementer result says **471** subtests where the handoff
and my run both say **472** — immaterial, but one of those was transcribed rather than read.)

**CI-pin hazard checked directly rather than assumed.** The new code uses
`Path.write_text(newline=)` (3.10+, safe) and **not** `Path.read_text(newline=)` (3.13+ — the
API that passed locally and failed CI on PR #320). Verified by running both under `py`
3.12.13, the CI pin: `write_text` OK, `read_text` raises `TypeError`. All four changed `.py`
files parse under 3.12 syntax. A local green is still not the gate.

## Workflow Feedback

- **The handoff was the best-calibrated one I have worked from this epic.** Marking HUNT 1
  as already-proven and asking for three *specific* things instead saved real runway, and
  "treat my claims as claims" plus naming which one you actually measured is what made me
  build the boundary repro rather than re-run yours. Keep both.
- **One gap:** the handoff gave a Survey State Location but not the survey *shape*. I
  extended the template with nine hunt-specific items; had I not, the three hunts would have
  been crammed into `r3-evidence`/`r4-quality` and the engine would have recorded far less.
  Consider naming the expected extra checks when a gate has named hunts.
- **`--finding` with backticks is genuinely hazardous** as warned; I wrote every finding
  backtick-free. Worth promoting from a Standing Constraint to something the engine rejects.
- **`docs/agents/engine-config.json` does not exist** in this worktree (only
  `ORCHESTRATOR_CONTEXT.md`), yet both the survey template and the g1 survey reference it as
  `config_ref`. Harmless — the engine falls back to defaults — but it is a dangling reference
  two reviewers have now inherited.
