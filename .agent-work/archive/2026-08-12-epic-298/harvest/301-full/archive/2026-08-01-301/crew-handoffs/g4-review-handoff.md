# Reviewer Handoff

## Gate
`g4` — bind the ratified retirement layout + retirement-dependent retrieval (issue #301)

**Full cold-panel review class. Do not downgrade because the remaining diff is small** — this
gate binds a decision a human personally ratified after it was deliberately held open across
three prior gates, and it is the last gate before merge.

## What was implemented

The retirement layout was held for human ratification through g1–g3. Tommy ruled, verbatim:

> *"move the file, prefer to keep files clean of history unless they're historical. archives are
> available strats."*

So **Option A**: retiring an episode **moves** `episodes/active/<id>.md` →
`episodes/retired/<id>.md`. Option B (a `status` field filtered negatively) was rejected and its
adapters removed. The ruling's second half was treated as a design principle: `retired/` is a
genuine **archive**, not a second live search space — so `include_retired` defaults to **False**
on every retrieval primitive, making the archive opt-in.

Changed: `scripts/apply_episode_delta.py`, `scripts/query_episodes.py`,
`tests/test_episode_store.py`, `docs/EPISODE_STORE.md`, `episodes/` (new `active/`, `retired/`).

## How to inspect

```bash
cd C:/Programs/constellation-skills-wt/298-301
git status --short
git diff scripts/ tests/ docs/
cat docs/EPISODE_STORE.md      # §7 is the ratified contract
```

Implementer's result: `.agent-work/301/crew-handoffs/g4-result.md`. Its handoff:
`.agent-work/301/crew-handoffs/g4-handoff.md`.

## Close criteria

- **C2** Option A bound at the single seam set and nowhere else; no call site inlines a
  directory check.
- **C3** a retired episode is **absent** from ordinary retrieval **and present** in
  history-inclusive retrieval — both directions.
- **C4** an adversarial fixture proves retrieval does not silently omit.
- **C5** the #308 companion is not precluded: with one cluster member retired, its still-active
  neighbours stay findable and the retired one stays reachable history-inclusively.
- **C6** the store is never left half-retired.

## HUNT THESE SPECIFICALLY

**1. The relocated silent-omission class — the highest-value target.** Option A makes the *old*
trap structurally impossible (membership is a directory fact, not a parsed field). It does **not**
remove the class; it relocates it. The implementer claims three new traps, each with a fixture
mutation-verified by substituting a naive implementation into the seam and observing red:
- a flat glob that misses the subdirectory (naive returns `[]`, indistinguishable from an empty
  store);
- a history-inclusive enumeration that forgets to union both directories (naive returns half —
  non-empty and plausible-looking, which is the dangerous kind);
- a stray file at the old flat path, belonging to neither set (naive silently absent from both).

**Verify each fixture actually catches what it claims, then hunt a fourth.** Ask specifically:
what else changed meaning when membership moved from *file content* to *file location*? Consider
case-insensitive filesystems, a directory that does not exist yet, a file present in **both**
`active/` and `retired/`, symlinks, and an episode id that collides with a non-episode filename.

**2. `include_retired=False` as the default.** This is the ruling's archive principle made
mechanical. Check it is genuinely the default on every primitive that takes it, and that `fetch`
correctly does **not** take it — the implementer's reasoning is that a lookup by name is not a
search, and a `consolidated-into:` cross-reference would dangle otherwise. Is that reasoning
sound? Can you construct a case where the asymmetry surprises a caller?

**3. Half-retirement safety (C6).** Three claimed layers: unrepresentable by construction;
compensated via snapshot-and-rollback in `commit()` with faults injected at both placement steps;
and the residual hard-kill case made loud by refusing an id present in both directories. **Test
the third** — create an episode in both directories and confirm readers *and* the writer refuse
rather than silently picking one.

**4. The one change beyond a pure adapter swap.** The implementer moved a destination-routing
branch out of `write_plan()` (which branched on `ep.status`) and into `destination_for()`,
calling it "an inlined layout check wearing a delegation's clothes." Verify that move is
behaviour-preserving and that it was genuinely necessary for C2 rather than opportunistic
refactoring.

**5. Doc accuracy.** `docs/EPISODE_STORE.md` §7 must now describe what shipped, not the open
seam. §§8/10 previously described retirement-dependent retrieval as if it existed — verify they
now match reality. §9's "identical file content" claim (misleading at byte level, contradicted by
`test_working_tree_bytes_are_not_the_cross_worktree_identity`) must be corrected. Confirm Option
B survives as *rejected-with-reason* rather than being deleted — the reasoning is why the seams
exist and is worth keeping.

**6. Over-correction check.** Does the store now carry machinery it does not need? Is
`NON_EPISODE_FILENAMES` the right mechanism, or does an allowlist of filenames reintroduce a
drift risk of its own — the same shape as the character-list guard this run already replaced
once?

## Scope

Review only. **Do not edit any repo file.** Probe scripts go outside the repo or under
`.agent-work/`. Leave nothing stray in `scripts/`, `tests/`, or `episodes/` — and note that a
stray file under `episodes/` is now itself a tested failure mode, so cleaning up after yourself
is load-bearing here.

## Exclusions

- Do not re-litigate the retirement layout. It is ratified by the human; Option A is settled.
- Do not re-litigate the record grammar (frozen at g1, reviewed three times) or the writer's
  validation design (approved at g2).
- Do not build or ask for capture wiring (#305) or consolidation (#308).
- Do not propose changes to `LESSONS.md`, `apply_lessons_delta.py`, or #300's manifest.

## Evidence produced (reproduce it)

I independently verified all of these before dispatching you:

```bash
grep -c "_LAYOUT_ADAPTER\|_LAYOUT_OPTION" scripts/*.py     # 0 — Option B adapters gone
grep -n "ACTIVE_DIR\|RETIRED_DIR" scripts/query_episodes.py # no output — zero literals in retrieval
grep -n "ACTIVE_DIR\|RETIRED_DIR" scripts/apply_episode_delta.py  # 11 uses, all lines 460-639
python -m pytest tests/test_episode_store.py -q             # 94 passed, 1 skipped
python -m pytest tests/ -q                                  # 1251 passed, 3 skipped
py -m unittest tests.test_episode_store                     # OK on 3.12, the CI floor
git add -An episodes                                        # READMEs under episodes/, active/, retired/
```

The three g2 negation fixtures still exit non-zero. **Note on the skip count:** locally 3, on CI
2 — the third is my own `FloorInterpreterPortabilityTests` skipping because `py` resolves to 3.14
inside a pytest subprocess. On CI the runner *is* 3.12 so it runs. Expected, not a defect.

Use `python`, **not** `py`, for pytest.

## Return format

Return **REVIEW_RESULT** with a literal `VERDICT: APPROVE` or `VERDICT: BLOCK`, findings ranked
most-serious-first with severities, what you verified as fine, what you could not check and why,
and Workflow Feedback.

Reserve `BLOCK` for an unmet close criterion or a defect you **demonstrate** — especially a
fourth silent-omission trap, or a half-retirement window that actually corrupts the store.
`APPROVE`-with-findings is right if the criteria are met and the rest are refinements; say which
issue or gate carries each leftover. This is the last gate before merge, so a finding you route
downstream needs a home.
