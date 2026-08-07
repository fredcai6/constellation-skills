# scripts.install_constellation:write_template_working_copies
function, scripts/install_constellation.py:1203, 49 lines

```python
def write_template_working_copies(skills: Sequence[Skill], project_root: Path, *, only: set[tuple[str, str]], out: Callable[[str], object]) -> int
```

Seed editable project-local template working copies (flat, never clobbered).

The pristine `.baseline/` is only the reconcile anchor; these flat copies at
`.agent-work/templates/<name>` are what a project actually edits and commits —
the half of the versioned-template model the baseline alone does not provide.
Skills resolve a template project-local-first (`.agent-work/templates/<name>`,
falling back to the bundled copy), so without a working copy a template edit
has nowhere to live but the installed skill (which a reinstall overwrites).

Seeds copies ONLY for `only` — the (skill, template) keys that entered baseline
tracking this run (every template on a fresh seed, only the genuinely-new ones
on a reinstall). This deliberately does NOT backfill a working copy for every
template a project lacks one for: a frozen copy of a template the project never
customizes reads as false `project-customized` drift and masks later upstream
changes the project should adopt. Copies are taken from the bundled source in
token form (identical to the baseline, so they read `up-to-date`); existing
copies — Charter seeds or prior edits — are never overwritten. Returns the
number newly seeded.

calls internal: write_template_working_copies.out
calls stdlib: builtins.sorted, shutil.copy2
reads stdlib: shutil (module)
unresolved: 5 calls (dispatch-unknown-base), 5 reads (dispatch-unknown-base)

referenced by: 2 sites, this module only
