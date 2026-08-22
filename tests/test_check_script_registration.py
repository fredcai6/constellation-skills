"""Registration lint + vocabulary rule for issue #345 ("built but not wired").

Epic-569 wave w1-wiring's census (docs/CHECK_SCRIPT_CENSUS.md) found 17 of 26
check-shaped scripts genuinely live (either wired into a shipped template's
`command` check, a CI workflow step, a hook, another live script's own call,
or a pytest test that asserts its check function against the real repo), 8
unwired (built, usually tested, but nothing outside their own test suite
invokes them, and no test asserts them against the real repo either), and 1
dead (deleted this same wave). That population is NOT mostly dead code, so
the honest-null "delete and ship no lint" outcome does not apply -- the
population supports building the smallest mechanism that works, per #345's
own options (1) and (2). This is that mechanism, and it runs here, in pytest
-- a `command`-kind
check in a shipped template was considered and rejected as the wiring seam:
the population this lint watches is scripts/, not any one role's spine, so a
template check would be arbitrarily attached to one role's gate for a
repo-wide property. pytest is itself CI-gated (.github/workflows/ci.yml runs
`pytest tests/ -q`) and is "the real gate" per this repo's own doctrine
(docs/agents/ORCHESTRATOR_CONTEXT.md), so this is not the "another unwired
checker" #345 explicitly forbids -- it fails the suite, visibly, on the
negative case proven below.

Two checks, per #345's decision:registration-lint-shape (leans g2, guess-
graded, confirmed rather than overturned by the census -- the unwired
population is unwired because nothing checks registration, not because
"nobody knew they existed": most have their own dedicated tests and doc
references):

1. RegistrationLint (option 1) -- every scripts/{verify,check,prove,measure}_*.py
   must be wired into a real `command`-kind check in a shipped
   skills/*/templates/*.json, OR be on ALLOWLIST below with a stated reason.
   Ships BLOCKING, not report-only (decision:report-only-names-its-trigger):
   the census already did the adjudication work for every currently-shipped
   script, so there is nothing left to stage.

2. VocabularyRule (option 2) -- bans the phrase "mechanically enforced" and a
   bare claim that something "is RAILed"/"RAIL-enforced" from skills/ and
   docs/ prose outside the small set of files that legitimately describe the
   engine's own literal `RAIL:` refusal-message mechanism. A repo-wide sweep
   at authoring time (this wave) found ZERO current violations of either
   phrase -- this ships as a preventive floor against future drift, not a fix
   for a measured-live defect, and is cheap enough that "build both 1 and 2"
   costs nothing extra.
"""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
TEMPLATES_GLOB = "skills/*/templates/*.json"

_SCRIPT_PREFIXES = ("verify_", "check_", "prove_", "measure_")


def _check_shaped_scripts() -> set[str]:
    """Every scripts/{verify,check,prove,measure}_*.py basename, live-enumerated
    -- never a hardcoded list, so a script added or removed after this lint
    shipped is picked up automatically rather than silently un-checked."""
    return {
        p.name for p in SCRIPTS_DIR.iterdir()
        if p.is_file() and p.suffix == ".py" and p.name.startswith(_SCRIPT_PREFIXES)
    }


def _command_check_texts() -> list[str]:
    """Every `command` string inside a `"kind": "command"` check block, across
    every shipped skills/*/templates/*.json. Walks the real JSON structure
    (pre/postconditions on every task) rather than grepping raw text, so a
    script name appearing only in an unrelated comment or statement string
    is never mistaken for a wired check."""
    texts: list[str] = []
    for path in sorted(ROOT.glob(TEMPLATES_GLOB)):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        tasks = data.get("tasks", {})
        if not isinstance(tasks, dict):
            continue
        for task in tasks.values():
            if not isinstance(task, dict):
                continue
            for key in ("preconditions", "postconditions"):
                for cond in task.get(key) or []:
                    if not isinstance(cond, dict):
                        continue
                    check = cond.get("check")
                    if isinstance(check, dict) and check.get("kind") == "command":
                        cmd = check.get("command")
                        if isinstance(cmd, str):
                            texts.append(cmd)
    return texts


def _template_registered_scripts() -> set[str]:
    """The subset of check-shaped scripts named inside a real command-check's
    command text -- the "live, mechanically gated" bucket from
    docs/CHECK_SCRIPT_CENSUS.md's own methodology."""
    texts = _command_check_texts()
    scripts = _check_shaped_scripts()
    return {name for name in scripts if any(name in t for t in texts)}


# Every check-shaped script NOT wired into a shipped template's command check,
# each with the one-line reason docs/CHECK_SCRIPT_CENSUS.md's census recorded
# (full evidence there; this is the stated-reason half of #345's option 1, not
# a restatement of the whole census). A script landing here that genuinely
# has no reason is exactly what this lint exists to stop shipping silently.
ALLOWLIST: dict[str, str] = {
    # Live via a path other than a shipped template's command check --
    # allowlisted here because THIS lint's registration surface is
    # templates/*.json specifically; each is still "live" in
    # docs/CHECK_SCRIPT_CENSUS.md's fuller reachability sense.
    "verify_skip_guard.py": "live via .github/workflows/ci.yml's Skip guard step, not a template check",
    "verify_worktree_isolation.py": "live via scripts/spine_lifecycle.py's open_work() self-verify call",
    "verify_issue_set.py": "live via scripts/file_issue_set.py's own call, itself named in skills/to-initial-issues/SKILL.md",
    "verify_episode_observations.py": "live via scripts/apply_episode_delta.py's write-time guard import",
    "verify_declared_dispatch.py": "live only on generate_spine.py's compiler path (MCP spine_open), not the template-instantiation path any shipped role uses",
    # Live via a pytest test that asserts the script's check/scan function
    # against the REAL repo unconditionally (docs/CHECK_SCRIPT_CENSUS.md
    # category 5) -- genuinely enforced every suite run, just not through a
    # template command check, which is this lint's own narrower surface.
    "verify_context_declaration.py": "live via tests/test_context_declaration_lint.py's real-corpus assertions, not a template command check",
    "verify_coverage_ledger.py": "live via tests/test_verify_coverage_ledger.py::test_real_repo_ledger_passes, not a template command check",
    "verify_retirement.py": "live via tests/test_retirement_guard.py::test_canon_is_clean (vr.scan(REPO_ROOT) == []), not a template command check",
    "verify_skill_registered.py": "live via tests/test_write_a_skill.py's real-corpus assertions, not a template command check; also prose-instructed in skills/write-a-skill/SKILL.md",
    "check_template_overlay_freshness.py": "live via tests/test_check_template_overlay_freshness.py::test_real_repo_overlay_has_no_stale_templates, not a template command check",
    # Genuinely unwired: built, tested, documented, still relevant -- not
    # wired into any command check today, and no test asserts against the
    # real repo either. Recorded here with the census's reason rather than
    # silently passing; wiring any of these is a future call for whoever
    # owns that capability, not this lint's job.
    "verify_diagnosis.py": "prose-instructed only (skills/diagnose/SKILL.md step 3), not command-gated",
    "verify_epic_418_demo.py": "unwired historical epic-418 acceptance-demo generator; only caller is itself unwired",
    "verify_installed_bundles.py": "referenced only in installer comments, never called; own tests use a temp install root",
    "verify_iterative_planning_acceptance.py": "unwired frozen acceptance suite for the still-live iterative-planning feature; nothing re-runs it",
    "check_corpus_freshness.py": "referenced only in installer comments, never called; own tests use a synthetic marker",
    "check_role_spine_bookends.py": "referenced only in a sibling script's docstring, never called; own tests use a temp repo",
    "check_skill_freshness.py": "named only in installer's printed human-facing messages, never called; own tests use temp install roots",
    "measure_overread.py": "deliberately manual measurement instrument, cited across epic-567 launch orders and doctrine",
}


class RegistrationLint(unittest.TestCase):
    """#345 option 1: every check-shaped script is wired into a real
    command-kind check, or explicitly allowlisted with a stated reason. A
    script satisfying neither fails this test by name -- the exact
    "built but not wired, and nobody had to notice" gap #345 is about."""

    def test_every_check_shaped_script_is_registered_or_allowlisted(self):
        scripts = _check_shaped_scripts()
        registered = _template_registered_scripts()
        unaccounted = scripts - registered - set(ALLOWLIST)
        self.assertEqual(
            unaccounted, set(),
            f"script(s) {sorted(unaccounted)} are neither wired into a "
            f"shipped skills/*/templates/*.json command check nor on "
            f"tests/test_check_script_registration.py's ALLOWLIST with a "
            f"stated reason -- add a real command check, or add an "
            f"allowlist entry naming why it stays unwired",
        )

    def test_allowlist_entries_are_still_real_scripts(self):
        # The reverse direction: an allowlist entry for a script that no
        # longer exists (renamed, deleted) is dead weight in the allowlist
        # itself -- the same drift-goes-unnoticed shape this lint exists to
        # catch, one level up.
        scripts = _check_shaped_scripts()
        stale = set(ALLOWLIST) - scripts
        self.assertEqual(
            stale, set(),
            f"ALLOWLIST entry/entries {sorted(stale)} name a script that no "
            f"longer exists under scripts/ -- remove the stale entry",
        )

    def test_allowlist_entries_are_not_secretly_template_registered(self):
        # If a script gains a real command check later, it should be REMOVED
        # from the allowlist, not left there as a dead duplicate reason --
        # otherwise the allowlist silently stops being an accurate account of
        # what is actually unwired.
        registered = _template_registered_scripts()
        stale = registered & set(ALLOWLIST)
        self.assertEqual(
            stale, set(),
            f"script(s) {sorted(stale)} are now wired into a template "
            f"command check AND still listed on ALLOWLIST -- remove the "
            f"now-redundant allowlist entry",
        )

    def test_negative_self_test_catches_an_unregistered_synthetic_script(self):
        # Proof this can actually fail, not just pass by construction: a
        # synthetic script name in neither the registered set nor the
        # allowlist must be flagged.
        scripts = _check_shaped_scripts() | {"verify_totally_synthetic_zzqx.py"}
        registered = _template_registered_scripts()
        unaccounted = scripts - registered - set(ALLOWLIST)
        self.assertIn("verify_totally_synthetic_zzqx.py", unaccounted)


# --- vocabulary rule (#345 option 2) ----------------------------------------

_BANNED_PHRASES = ("mechanically enforced",)
# Bare "RAIL" claims, excluding the doctrine files that legitimately name the
# engine's own literal `RAIL:` refusal-message prefix -- swept and confirmed
# at authoring time (this wave): only these two files use the word at all
# under skills/ or docs/, and both describe the real mechanism, not a false
# claim about an unwired check.
_RAIL_WORD_RE = re.compile(r"\bRAIL\b")
_LEGITIMATE_RAIL_FILES = {
    "skills/_shared/checklist-engine.md",
    "docs/CHECKLIST_ENGINE_DESIGN.md",
}


def _prose_files():
    for base in ("skills", "docs"):
        for path in sorted((ROOT / base).rglob("*.md")):
            yield path


class VocabularyRule(unittest.TestCase):
    """#345 option 2: ban prose that claims something "is mechanically
    enforced" or "is RAILed" outside the files that legitimately describe the
    engine's own RAIL mechanism. A repo-wide sweep at authoring time found
    ZERO violations -- this is a preventive floor, not a fix for a currently-
    measured defect, and ships anyway because it is cheap and #345 asks for
    both options when a mechanism is warranted."""

    def test_no_mechanically_enforced_claims(self):
        offenders = []
        for path in _prose_files():
            text = path.read_text(encoding="utf-8")
            for phrase in _BANNED_PHRASES:
                if phrase in text.lower():
                    offenders.append(str(path.relative_to(ROOT)))
        self.assertEqual(
            offenders, [],
            f"file(s) {offenders} use a banned enforcement claim "
            f"({_BANNED_PHRASES!r}) -- state what actually checks it "
            f"(a command-kind check, a named human) instead",
        )

    def test_no_bare_rail_claims_outside_legitimate_doctrine_files(self):
        offenders = []
        for path in _prose_files():
            rel = str(path.relative_to(ROOT))
            if rel in _LEGITIMATE_RAIL_FILES:
                continue
            text = path.read_text(encoding="utf-8")
            if _RAIL_WORD_RE.search(text):
                offenders.append(rel)
        self.assertEqual(
            offenders, [],
            f"file(s) {offenders} use the word RAIL outside the doctrine "
            f"files that describe the engine's own RAIL: mechanism "
            f"({sorted(_LEGITIMATE_RAIL_FILES)}) -- a bare RAIL claim "
            f"elsewhere reads as 'this is mechanically enforced' without "
            f"naming the command that enforces it",
        )

    def test_negative_self_test_catches_a_synthetic_mechanically_enforced_claim(self):
        offenders = []
        synthetic_text = "This check is mechanically enforced by nothing."
        for phrase in _BANNED_PHRASES:
            if phrase in synthetic_text.lower():
                offenders.append("synthetic")
        self.assertEqual(offenders, ["synthetic"])
