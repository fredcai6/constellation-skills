# SALVAGE — the census that was cut, preserved not deleted

**Status: HALTED BY SCOPE CUT, not failed.** Tommy stopped this work on 2026-08-03:

> *"that seems like we're making our life hard to come up with metrics too early. right now we're just
> reworking the substrate, we're not aiming to idealize any particular metric."*

The objection is that the measurement is **premature in kind** — the substrate is still being reworked,
so a metric built now measures something still changing shape underneath it. It is **not** a judgement
that the instrument was wrong.

**Nothing here is deleted, and nothing here is load-bearing for `B2_GATE_EVIDENCE.md`.** The verdict was
written from evidence held independently of this directory. These files exist so a future run inherits a
spec instead of re-deriving one. See the filed issue for the design and the cost estimate.

## What it got to before it was stopped

It **passed its blocking external oracle** — reproducing `TREND_SNAPSHOT` §1 at tag
`baseline/304-trend-snapshot` exactly, on all four figures:

```json
"baseline_oracle": {
  "expected": {"corpus_files":100,"corpus_words":63681,"skillmd_files":19,"skillmd_words":15831},
  "measured": {"corpus_files":100,"corpus_words":63681,"skillmd_files":19,"skillmd_words":15831},
  "reproduced": true }
```

That is the one check the instrument could not fake, and it passed. Counts it asserted:

| | |
|---|---|
| census rows | **187** (184 `rev-list` commits touching `skills/` + 3 unioned off-line baselines) |
| deletion events | **234** |
| roles at HEAD | **19** (`_shared` excluded) |
| unresolved reference tokens at HEAD | **10** |

It did **not** complete verification (`m5-verify`) and it never wrote `TRENDS.md`. **Treat `trends.json`
as unreviewed.** No independent reviewer ever hand-recomputed a revision against it, which was to be the
second external oracle.

## One observation, clearly labelled

Over the 3-commit window the census puts gross word deltas at **+43 added / −16 deleted** on
`NARROW-ALWAYS-LOADED` and **+179 / −106** on `CONDITIONALLY-LOADED` — i.e. **≈87% of deleted words in
the window came out of the conditionally-loaded bin.** That is the direction hypothesis **H1** predicted
(`PRE_REGISTRATION.md` §2).

**This is NOT presented as a finding and the verdict does not rest on it.** n=3 cannot support it, no
reviewer checked it, and it was produced by a gate that was cut. It is recorded because *deleting an
observation because its gate was cancelled* would be the same laundering this run spent its whole
pre-registration guarding against.

## Files

- `measure_surface.py` (60 KB) — the walker: no checkout, `ls-tree --long` + `cat-file --batch`
- `trends.json` (586 KB) — 187 rows, unreviewed
- `panel.json` (18 KB) — the pre-registered interpretation panel
- `test_measure_surface.py` (14 KB) — fixture tests
