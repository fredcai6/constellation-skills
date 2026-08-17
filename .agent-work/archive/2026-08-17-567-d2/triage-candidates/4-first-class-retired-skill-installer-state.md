# Triage candidate: install_constellation.py has no supported "templates-only, no taught procedure" skill state

**Found during:** 567-d2 understand (interrogation q3/q4).

**What:** `scripts/install_constellation.py`'s `discover_skills()` requires
every non-underscore-prefixed `skills/*` directory to carry a parseable
`SKILL.md` with `name`+`description` frontmatter, or the **whole installer**
raises `InstallError` -- not scoped to the one directory. There is no supported
way to ship a directory of templates/scripts under `skills/<name>/` with no
taught-procedure `SKILL.md` at all. This lane worked around it (kept a
minimal, present `SKILL.md`), but a first-class "retired/templates-only skill"
state (e.g. a frontmatter flag `retired: true` that `discover_skills()` and any
skill-listing UI both respect, still requiring `name`+`description` but
signaling "do not offer this for invocation") would be a cleaner fix than every
future retirement re-deriving the same minimal-stub workaround.

**Why this lane didn't build it:** "New installer mechanism" is explicitly a
`float`, not `yours`, in this lane's Inherited Latitude table -- this is
exactly that float, named rather than built.

**Suggested disposition:** recommend-and-defer -- a candidate for a small,
scoped issue if the corpus expects more skills to retire into templates-only
packages the way workbench just did.
