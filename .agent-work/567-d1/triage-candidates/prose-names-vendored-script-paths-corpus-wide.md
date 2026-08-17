# Skill prose names bundled scripts by a repo-relative path, 91 sites across 27 files

Measured at gate `g4` of `567-d1`, while widening #526's defect 1 ("the phrasing should resolve the
entry point from the repo rather than assume a layout"):

```
$ grep -rnoE '(python[0-9]* )?(-m )?scripts/[A-Za-z_/]+\.py' skills/ | grep -v 'skill-dir'
91 sites across 27 files   (82 across 26 outside the fenced skills/workbench/)
```

Engine-run **command checks** are already clean — 16 of 17 use a `<*-skill-dir>` resolver token, and
`g4` fixed the one that did not (`REVIEW_SURVEY.template.json` `r6-fowler.c1`). This candidate is the
other half: **prose** that tells an agent to run `scripts/<name>.py`, which is only correct where the
target repo vendors `scripts/` at its root — true in this repo, false in a consuming project, where
the script lives under the installed skill directory.

`references/global-everyone.md` already carries the rule this contradicts:

> Reference bundled scripts and references by their absolute installed path; don't resolve `scripts/`
> from the target repo unless it vendors them.

**Not acted on:** at 91 sites this is the corpus's own convention, so changing one skill's prose
creates inconsistency and changing all of it is a corpus-wide decision with a real chance of a
mechanical sweep going wrong across three template copies each. It also needs a ruling first: either
the prose adopts the resolver-token form the command checks use, or the rule in `global-everyone.md`
is relaxed to say prose may name the vendored path because a reader resolves it by judgment. That is
Curator or Charter work, not a `g4` edit. Recorded for routing at epic closeout.
