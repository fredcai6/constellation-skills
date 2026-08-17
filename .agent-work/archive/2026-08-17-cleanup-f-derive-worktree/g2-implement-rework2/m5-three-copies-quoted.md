# C7 — the three repaired passages, side by side

The sentence that changed is the one that pointed at
`checklist_engine.worktree_from_spine_path` as the thing that now answers
location. It is replaced in all three copies by the same two statements: the
engine reads no location at all, and the rule itself survives in the hook with
the case table as its specification, re-landing with its consumer in #610's
wave.

Rework 1's leaseless narrowing (R1) and the supersession citation of the
2026-08-15 worktree-identity ruling are untouched in all three — they are ruled
statements, and `check_three_copies.py` still requires every one of their
clauses.

---

## 1. `scripts/checklist_engine.py` — module header comment

```
# side. THE ENGINE NOW READS NO LOCATION AT ALL, ambient or derived. There is no
# second value that can disagree with the first, and no ambient reading a check
# command could forge by `cd`-ing first, because the engine no longer asks the
# question anywhere.
#
# The lexical rule that derives a worktree from a spine's path is NOT retired --
# only the engine's copy of it is. The rule lives in the stdlib-only hook, as
# `spine_rail._worktree_from_spine`, and `tests/test_worktree_derivation.py`'s
# case table is its specification. The engine-side copy was deleted in #609 g2
# under `ADMIRAL_RULING-2` N2: three sound decisions in a row removed all three
# of its consumers, and a definition nothing calls is not shipped. It re-lands in
# #610's wave together with #315 -- the consumer that threads `cwd` into the
# engine's check runner -- and re-derives against that same table.
```

## 2. `tests/test_spine_origin_isolation.py` — module docstring

```
guard is not the same as no guard. The engine now reads no location at all,
ambient or derived: there is no second value that can disagree with the first,
and no ambient reading a check command could forge by `cd`-ing first, because
the engine no longer asks the question anywhere.

The lexical rule that derives a worktree from a spine's path is NOT retired --
only the engine's copy of it is. The rule lives in the stdlib-only hook, as
`spine_rail._worktree_from_spine`, and `tests/test_worktree_derivation.py`'s
case table is its specification. The engine-side copy was deleted in #609 g2
under `ADMIRAL_RULING-2` N2: three sound decisions in a row removed all three of
its consumers, and a definition nothing calls is not shipped. It re-lands in
#610's wave together with #315 -- the consumer that threads `cwd` into the
engine's check runner -- and re-derives against that same table.
```

## 3. `docs/CHECKLIST_SCHEMA.md` — the `origin` section

```
What the comparison genuinely had, coverage over every verb and an expected side
a spine's own text could not edit, it had over a *location* question the engine
no longer asks: **the engine reads no location, ambient or derived.** There is
no second value that can disagree with the first, and no ambient reading a check
command could forge by `cd`-ing first, because the engine no longer asks the
question anywhere.

The lexical rule that derives a worktree from a spine's path is **not** retired
— only the engine's copy of it is. The rule lives in the stdlib-only hook, as
`spine_rail._worktree_from_spine`, and `tests/test_worktree_derivation.py`'s
case table is its specification. The engine-side copy was deleted in #609 g2
under `ADMIRAL_RULING-2` N2: three sound decisions in a row removed all three of
its consumers, and a definition nothing calls is not shipped. It re-lands in
#610's wave together with #315 — the consumer that threads `cwd` into the
engine's check runner — and re-derives against that same table.
```

---

## The drift check, and the fact that it caught real drift

`check_three_copies.py` was inherited from the rework-1 implementer and updated
here: its `derivation-kept` clause required all three copies to name
`checklist_engine.worktree_from_spine_path`, which is now a false claim, so it
was replaced by six clauses covering the repaired sentence, and the old pointer
was added to `FORBIDDEN`.

It did not pass first time — it caught exactly the partial repair it exists to
catch:

```
DRIFT: scripts/checklist_engine.py: missing required clause 'deleted-under-the-ruling' (/deleted in #609 g2 under admiral_ruling-2 n2/)
DRIFT: tests/test_spine_origin_isolation.py: missing required clause 're-lands-with-its-consumer' (/re-lands in #610's wave together with #315/)
checked 72 clause-assertions across 3 copies
```

The first was genuine drift: the engine header said "deleted **here**" where the
other two said "deleted in #609 g2 under `ADMIRAL_RULING-2` N2". Repaired to
match.

The second was a defect in the checker, not in the prose. Its normalizer stripped
a leading `#` as a comment marker, so a docstring line that wrapped with `#610`
first was silently read as `610` and the clause looked absent. Issue references
are part of the claim, so the normalizer now declines to strip a `#` followed by
a digit. That is a repair to the check, not a loosening of it: no clause was
weakened, and the same run still fails on the real drift above.

After both repairs:

```
checked 72 clause-assertions across 3 copies
OK: all three copies carry the same narrowed claim
```
