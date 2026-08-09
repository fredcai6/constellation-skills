# g4 evidence: the top-index second tier on three corpora

Scripts: `g4_cross_corpus.py` (tier 1, all three), `g4_cross_corpus_subtier.py`
(tier 2 detail on f1Brainz). Both build into a scratch temp dir via
`--artifacts`/`--out`; neither writes into the corpus root. `git status`
before/after is identical for every corpus (checked programmatically).

## Tier 1 (package overview) on all three

| corpus | modules | entities | package overview |
|---|---|---|---|
| constellation-skills | 111 | 3728 | evals: 12 modules, 54 entities / scripts: 49 modules, 905 entities / tests: 50 modules, 2769 entities |
| f1Brainz | 1227 | 15037 | docs: 2/3, run_2025_collection: 1/0, run_tests: 1/17, scripts: 235/1702, src: 440/4228, tests: 548/9087 |
| superCoolSpaceSim | 0 | 0 | (no mappable modules found) -- a C++/Obj-C repo, zero tracked `.py` files |

No bucket is "one giant bucket" (constellation-skills' largest is `tests` at
45% of entities; f1Brainz's largest is `tests` at 60%, still split 6 ways
structurally) and none is "N buckets of one" (superCoolSpaceSim correctly
reports nothing to route, not N empty headings).

## Tier 2 (subpackage grouping) on f1Brainz -- the "one giant `src/` bucket" trap

f1Brainz uses the `src/` layout constellation-skills does NOT have. A tier
keyed only to the top-level segment would leave `src` a single 440-module,
4228-entity bucket -- exactly the degenerate shape the handoff warns about.
Tier 2 splits it on the corpus's OWN subpackage structure, with no threshold:

```
## src (440 modules, 4228 entities)
  ### src.analysis (2 modules, 8 entities)
  ### src.calibration (7 modules, 39 entities)
  ### src.common (4 modules, 28 entities)
  ### src.compound_prior (24 modules, 332 entities)
  ### src.data (18 modules, 194 entities)
  ### src.evo_predictor (119 modules, 1278 entities)
  ### src.fantasy_scoring (16 modules, 229 entities)
  ### src.latent_power (25 modules, 233 entities)
  ### src.models (5 modules, 113 entities)
  ### src.physics (161 modules, 1398 entities)
  ### src.preprocessing (18 modules, 117 entities)
  ### src.publishing (2 modules, 5 entities)
  ### src.reporting (17 modules, 100 entities)
  ### src.simulation (6 modules, 40 entities)
  ### src.strategy (6 modules, 27 entities)
  ### src.utils (9 modules, 87 entities)
```

`tests` (548 modules) splits into 8 subpackages (`unit`, `integration`,
`fixtures`, `regression`, `known_answer`, `property`, `oracles`, `benchmark`).
`tests.unit` still holds 505 of 548 -- an honest report of this repo's own
test-organization convention (most of its tests really are filed as "unit"),
not a tier defect; the same corpus-shape honesty this repo's own flat `tests/`
package reports for the same reason.

`scripts` (235 modules) splits out one real subpackage (`scripts.fusion_replay`,
10 modules) and lists the rest loose, which is what the corpus's own layout is:
mostly flat, one nested exception.

`superCoolSpaceSim` has zero subpackages to show, by construction (zero
Python modules).

## No absolute-count threshold in the tier logic

The only size-shaped comparisons the new code contains:

```
scripts/code_map/render.py:526:
    subpkgs = {module_group_key(m) for m in mods if len(m.split(".")) >= 3}
```

`len(m.split(".")) >= 3` is a property of ONE module's own dotted name (does
it have a subpackage segment at all?), not a threshold on corpus size -- it
reads the same whether the corpus has 3 modules or 30,000. `f1Brainz`'s
`src.publishing` group (2 modules) and this repo's own synthetic
`pkg.sub` fixture (1 module, `TopIndexSecondTierTests`) both prove no
MINIMUM group size gates the grouping either. Grepped and confirmed: no other
`len(...) > N` / `>= N` comparison touches the package/subpackage grouping
path (see the grep in the g4-implement-RESULT.md evidence section).
