# Landing-zone stability — measured, not assumed

Human ruling this answers: *"middle point sounds fine, I could buy local
regeneration, but if we think we can choose a stable landing zone we should."*

So "stable" had to be **measured**. The measurement carries a negative control,
or it would be one more check that cannot fail — the theme this whole run kept
hitting.

## Method

Landing zone candidate = every `INDEX.md` + `ids.jsonl` (116 files).
Body pages = everything else (3,893 files). Total tree: 4,009 files.

- **Arm A — body-only edit.** Reword an existing function docstring in
  `scripts/code_map/discovery.py`. No signature, no symbol, no shape change.
  Rebuild. Expect the landing zone byte-identical if it is stable.
- **Arm B — negative control, shape edit.** Add a new top-level function to the
  same module. Rebuild. The landing zone **must** change. If it does not, arm A
  proves nothing: an inert landing zone is not a stable one.

Script: `landing_zone_measure.py` (session tmp). Both arms reverted; tree
restored byte-identical; source revert byte-clean under `git diff --quiet`.

## Result

| | landing zone (116) | root `INDEX.md` + `ids.jsonl` (2) | body pages |
|---|---|---|---|
| Arm A (body edit) | **1 changed** — `scripts.code_map.discovery/INDEX.md` | **unchanged** | 1 changed |
| Arm B (shape edit) | 2 changed — root + module INDEX | **2 changed** | 1 added |

**The 116-file landing zone is NOT stable.** A single reworded docstring
rewrites its module `INDEX.md`, because the module index carries each entity's
summary line. That is not a defect — the module index is *supposed* to show
summaries — but it means the 116-file zone churns on ordinary editing.

**The 2-file root zone IS stable, and the negative control fires on it.** Root
`INDEX.md` survives a body edit untouched and changes on a shape edit, which is
exactly the discrimination we needed. `ids.jsonl` is empty in this repo and
trivially stable: no anchor id has ever been authored here, which is the same
fact g6 established when it found zero anchors in the only real corpus.

## Consequence

The preferred branch of the ruling is available, just far smaller than the plan
assumed: **commit `map/INDEX.md` + `map/ids.jsonl`, regenerate the rest
locally.** This satisfies "if we can choose a stable landing zone we should"
against a measured definition of stable, and it fully retires critic F9's
repo-doubling objection — 2 tracked files, not 3,975.

**The honest caveat, stated rather than smoothed over:** the committed entry
point resolves, but its links into `<module>/INDEX.md` do not until a build has
run. Crews get a real starting page and a one-command regeneration
(`python -m scripts.code_map build --root .`), not a fully browsable tree.
That is the "local regeneration" the ruling already said it could buy, applied
to the body rather than to the whole map.
