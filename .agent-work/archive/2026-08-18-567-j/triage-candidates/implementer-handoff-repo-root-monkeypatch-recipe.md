# Triage candidate: implementer-handoff test-recipe wording for def-time-bound defaults

**Found at:** g1-review (`tc1` in `.agent-work/567-j/g1-review/review.json`),
surfaced by both the implementer and independently confirmed by the reviewer.

**What happened:** the g1-implement handoff's literal Close Criteria test
recipe ("Monkeypatch `installer.REPO_ROOT` ... so it resolves via the real
`default_mcp_config_path()`") does not work: `default_mcp_config_path(repo_root:
Path = REPO_ROOT)` binds its default argument at `def`-time, so patching the
`REPO_ROOT` module global afterward never reaches the function's already-bound
default. Patching `REPO_ROOT` directly is worse — `install_skills` reads it
directly (not as a bound default) to locate the real `skills/`/`scripts/`
source trees, so patching it breaks the install half of the same call with a
`FileNotFoundError`. The implementer found the working pattern instead:
`mock.patch.object`-style patching of `default_mcp_config_path.__defaults__`
itself, restored in `finally`.

**Why it matters:** `scripts/install_constellation.py` has at least three
other functions gated the same def-time-bound-default way off `REPO_ROOT`
(`validate_required_scripts`, `source_hook_path`,
`discover_skills`/`SOURCE_ROOT`). Any future handoff asking a crew to test
one of these by "monkeypatch `REPO_ROOT`" will hit the identical dead end and
have to rediscover the `__defaults__` pattern from scratch.

**Recommendation (not mine to decide or file):** update the shared
implementer-handoff-authoring guidance (or a testing reference doc) to name
the `func.__defaults__` patch pattern for any function with a module-level
default bound at import time, instead of the bare "monkeypatch the module
global" phrasing that reads as sufficient but isn't.

**Disposition:** staged only, per `decision:no-issue-filing-mid-run`. Filed
nowhere; the human or Admiral routes this from here.
