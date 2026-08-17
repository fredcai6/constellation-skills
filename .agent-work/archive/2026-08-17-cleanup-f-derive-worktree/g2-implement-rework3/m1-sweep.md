# C1 — the claim-level sweep, run and reported

Run by `constellation/cleanup-f-derive-worktree/g2/implementer/attempt-4` on the
tree at `84d949eb` **before** any repair. Raw output: `m1-sweep-raw.txt`.
Classification output: `m1-classification.txt`.

## The commands

```bash
py .agent-work/cleanup-f-derive-worktree/g2-implement-rework3/sweep_claims.py \
  > .agent-work/cleanup-f-derive-worktree/g2-implement-rework3/m1-sweep-raw.txt

py .agent-work/cleanup-f-derive-worktree/g2-implement-rework3/classify_hits.py \
  > .agent-work/cleanup-f-derive-worktree/g2-implement-rework3/m1-classification.txt
```

## What the sweep matches, and why it is not a symbol grep

`sweep_claims.py` never mentions `worktree_from_spine_path`. It matches the two
**claims**, over every git-tracked text file (10224 scanned), on a rendering of
each file with comment markers (`#`, `//`, `*`, `>`) stripped and whitespace
collapsed — so a claim that wraps across two comment lines or two docstring
lines is one sentence to the patterns. That wrap is exactly why the reviewer's
B1 survived three passes: `main()`'s stale sentence breaks after "derived".

| family | patterns |
|---|---|
| derive | `deriv\w*.{0,160}?worktree` · `worktree.{0,160}?\bderiv\w*` · `worktree … (computed\|resolved\|inferred\|read) … from … (spine\|checklist) … path` · `from … spine's own path` |
| ownership | `ownership guard` · `ownership is the lease` · `lease … (is\|was\|remains) … ownership` · `ownership … is … the lease` · `as it always was` |

The script prints the file count and the per-family hit count and **fails** on
zero of either, so a sweep that looped over nothing cannot read like a clean
sweep. `classify_hits.py` fails on any live hit it has no class for, so a hit
this gate never looked at cannot pass silently either.

## Hit count

| zone | derive | ownership | total |
|---|---|---|---|
| **live** (everything outside the record zone) | 52 | 12 | **64** |
| record: `.agent-work/` | 1448 | 74 | 1522 |
| record: `episodes/` | 2 | 0 | 2 |
| record: `map/` | 1 | 0 | 1 |
| **all** | **1503** | **86** | **1589** |

**The record zone is not repaired, by design.** `.agent-work/`, `episodes/` and
`map/` hold dated records of what was said at the time — launch orders, floats,
rulings, predecessor results, archived epics, harvested episodes, and a
generated map. Editing them would falsify the record rather than repair a
claim; `.agent-work/rulings/` is fenced by the handoff outright, and `map/` is
regenerated, never hand-edited. They are counted here, not touched.

## The 64 live hits, classified

Full per-hit listing with reasons: `m1-classification.txt`. Totals:

| class | hits |
|---|---|
| stale → **repaired** | 6 |
| correct claim, **consumer count harmonized** | 4 |
| already correct → left as-is | 6 |
| **fenced** (g3 / lane A) → reported, not edited | 19 |
| unrelated to either family | 29 |

### stale → repaired (6 hit-lines = 4 claims, in 2 files)

| hit | claim |
|---|---|
| `scripts/checklist_engine.py:3498`, `:3499` | derive — `main()`'s load-time block: "Both are gone: the worktree is derived from the spine's own path where it is needed…" |
| `scripts/checklist_engine.py:3507`, `:3508` | ownership — "The lease, which is the actual ownership guard, is enforced inside `dispatch()` as it always was." |
| `scripts/spine_lifecycle.py:92` | derive — `build_origin`: "(#609 — a spine's worktree is derived from its path…" |
| `scripts/spine_lifecycle.py:94` | ownership — "…and ownership is the lease)." |

These are the three passages the reviewer named. **The sweep found no fourth
stale claim in either family** anywhere in the live zone.

### correct claim, consumer count harmonized (4)

`scripts/checklist_engine.py:95`, `docs/CHECKLIST_SCHEMA.md:128`,
`tests/test_spine_origin_isolation.py:44`, `tests/test_worktree_derivation.py:1`.

Each already says the true thing — the lexical rule is not retired, only the
engine's copy of it is. Three of them then said the deletion "removed all
**three** of its consumers" and the fourth said it "had **two** consumers when
it was written". Per the handoff's constraint and `FLOAT_TO_ADMIRAL-2` N2, all
four now carry the canonical reading in one identical wording: **two real
consumers, plus a third withdrawn before it ever existed.**

### already correct → left as-is (6)

`scripts/checklist_engine.py:106` and `tests/test_spine_origin_isolation.py:27`
carry R1's narrowing verbatim. `tests/test_spine_origin_isolation.py:51` and
`:448` and `tests/test_worktree_derivation.py:112` state true things about the
hook's rule and the deletion.

`tests/test_worktree_derivation.py:8` — "It never answers 'is this mine':
ownership is the lease, and among spines sharing one tree the discriminator is
binding-key provenance (2026-08-16 worktree-is-location ruling)" — is
**deliberately left exactly as it stands.** It is not the guard-removal claim
R1 narrowed: it says what the *derivation* answers, in the
worktree-is-location frame, which `ADMIRAL_RULING-1` did not touch and which is
`@grade: settled/human`. It is also the **single repo-wide citation of the
2026-08-16 ruling** that C8 requires kept at exactly one.

### fenced → reported, not edited (19)

`scripts/hooks/spine_rail.py:721`, `:1171` and 17 hits in
`tests/test_spine_rail.py` (`:874 :885 :903 :904 :909 :911 :925 :930 :944 :945
:946 :947 :950 :1917 :1918 :2654 :2656`). Both files are **g3's**. Two of the
`test_spine_rail.py` hits (`:903`, `:904`) are the known stale references to
the deleted engine twin. Nothing edited.

### unrelated (29)

`docs/GAUGE_WRITER_HOOK.md` (4 — the gauge hook derives a worktree root from
`git worktree list`), `scripts/mcp_spine_server.py` (6) and
`tests/test_mcp_lifecycle.py` (2) (lane A — the door's own git-based
derivations), `notes-1.md` (2 — another run's working notes),
`scripts/episode_capture.py` + `tests/test_episode_fields.py` (2 — a derived
*project name*), `scripts/spine_lifecycle.py:230`/`:231` (2 — `git worktree`
arguments this call derived), `tests/test_spine_lifecycle.py` (2),
`tests/test_iterative_planning_doctrine.py` (1),
`tests/test_worktree_derivation.py:268/:270/:274` (3),
`scripts/checklist_engine.py:982` (1),
`docs/superpowers/plans/2026-06-24-lease-owner-liveness.md` (2),
`scripts/install_constellation.py:546` + `tests/test_install_constellation.py:4067`
(2 — "as pure as it always was", a different subject).

One of these is worth reporting rather than dropping:
`tests/test_worktree_derivation.py:270` still reasons about
`origin_worktree_refusal`'s purity, and that predicate was deleted. It is a
stale reference to a deleted symbol, **not** a claim in either assigned family
— the same class of residue the handoff fences to g3 in the two `spine_rail`
files. Raised as an out-of-scope observation rather than edited here.
