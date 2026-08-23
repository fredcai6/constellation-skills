"""Coverage guard for #567 lane N -- `ROLE_MODEL_TIERS` must declare every
role live doctrine actually hands a model-tier-bearing dispatch artifact.

THE DEFECT THIS GUARDS AGAINST, EXACTLY. Wave 3 (#633) added `resolve_model`
and `ROLE_MODEL_TIERS` to `scripts/run_crew.py`, keyed by hand from the role
names someone expected the corpus to use. The very next dispatch this epic
needed -- a Commander running under a frozen Admiral launch order -- was
refused: `commander-delegated` was not in the table, even though its own
principal document, `skills/admiral/templates/LAUNCH_ORDER.template.md`,
carries a `**Model tier (required):**` field that every such dispatch names.
The table's key set was drawn from memory, not measured against the doctrine
that actually hands roles a tier to resolve. This file is the measurement.

WHAT COUNTS AS "a role live doctrine hands a model tier" -- three signals,
each read from a real, load-bearing document rather than typed by hand:

  1. `skills/*/templates/*_HANDOFF.template.md` -- a role's own bounded
     handoff contract. When that file's body contains a `## Suggested Model
     Tier` field (case-insensitively matched as "model tier", so a reword
     of the heading still counts), the role is the file's own name stem,
     stripped of `_HANDOFF.template.md` and lower-cased --
     `IMPLEMENTER_HANDOFF.template.md` -> `implementer`. Measured today:
     `IMPLEMENTER_HANDOFF.template.md` and `REVIEWER_HANDOFF.template.md`
     both carry the field; `CRITIC_HANDOFF.template.md` and
     `PROTOTYPE_HANDOFF.template.md` do not (see "What this does not
     enforce" below for what that absence means).

  2. `skills/*/SKILL.md` -- a role whose own doctrine names a ratified
     `LAUNCH_ORDER` as its "frozen principal" (the exact phrase
     `skills/commander-delegated/SKILL.md` uses: "The ratified `LAUNCH_ORDER`
     is your frozen principal"). `LAUNCH_ORDER.template.md` is asserted, in
     this same file, to carry a `Model tier (required)` field, so a role
     that takes its orders from one is a role a tier gets resolved for. The
     found role is that SKILL.md's own `name: constellation-<slug>`
     frontmatter, never the phrase's surrounding prose -- reading a self-
     declaration is what keeps this signal from drifting if the file moves
     or is renamed.

  3. `specs/*.spine.toml` -- a role's own compiled-spine spec (`generate_spine.py`
     input; door doctrine's home per `test_cli_retirement_guard.py`'s own
     `SPEC_SUFFIXES` note). One file per role, named `<role>.spine.toml`.

These three are unioned into one scanned set, then asserted to be a SUBSET of
`ROLE_MODEL_TIERS["claude"]`'s declared keys -- never asserted equal, and
never asserted to cover every skill in the corpus (see below).

WHY SUBSET, NOT EQUALITY. `ROLE_MODEL_TIERS["claude"]` may legitimately
declare more than this scan finds -- `admiral`, `cartographer`, `critic` and
`explorer` are declared today and none of the three signals above reaches
them (a Commander dispatches Cartographer as a bare "subagent" table row with
no per-role handoff artifact; Admiral is a human-invoked top tier; Critic's
own `CRITIC_HANDOFF.template.md` carries no model-tier field; Explorer
dispatches excursions through `run_crew.py` but hands them an
`EXCURSION_BRIEF`, which carries no model-tier field either -- its row is a
human ruling, not a scanned one). That is not a gap
in this guard -- declaring a role ahead of doctrine naming one for it is
harmless. What the guard cannot tolerate is the reverse: a role doctrine
DOES hand a tier-bearing artifact to, silently missing from the table. Subset
is the exact shape of that asymmetry.

TWO HAZARDS THIS FILE IS BUILT TO SURVIVE (LAUNCH_ORDER.md, "Your task"):

  * NOT TRIVIALLY GREEN. A scan that matches nothing passes vacuously.
    `TestTheWalkIsNotVacuous` floors every one of the three walks and the
    union at counts measured on this tree, so a narrowed glob, a moved
    file, or a retyped field name reads red instead of clean.
  * NOT RED ON ARCHIVE NOISE. All three walks are rooted at `skills/` and
    `specs/` exclusively -- `.agent-work/**` (a live run's own launch
    orders, which legitimately quote "Model tier (required)" and
    "LAUNCH_ORDER" constantly, being records of what was said rather than
    doctrine) and `docs/superpowers/plans/**` are never globbed, so neither
    can ever enter the scanned set. `TestTheWalkStaysInsideDoctrine` pins
    that every matched path is doctrine, not a run's own record.

WHAT THIS DOES NOT ENFORCE, STATED RATHER THAN GLOSSED (mirrors
`test_cli_retirement_guard.py`'s own section of the same name):

  * `scout`, `interrogator`, `curator`, `docent`, `charter`,
    `diagnose`, `replan`, `to-initial-issues`, `triage`, `workbench`,
    `write-a-skill`, `how-to-talk` -- every one of these is a real skill
    (`skills/*/SKILL.md` self-registers all of them), and several are
    genuinely dispatched as subagents (`checklist-engine.md` names
    `scout` alongside `cartographer` in its "dispatch a subagent" list).
    None carries a model-tier-bearing artifact of its own today -- no
    `*_HANDOFF.template.md`, no "frozen principal" LAUNCH_ORDER claim, no
    `specs/*.spine.toml` -- so none of the three signals reaches them, and
    this guard is silent on whether they should eventually be declared.
    `tests/test_crew_launcher.py::test_unknown_role_under_known_harness_refuses_by_name_branch_one`
    pins `scout`'s refusal as today's correct, intentional behaviour; this
    file does not contest that pin.
  * `prototyper` IS dispatched via its own bounded contract
    (`PROTOTYPE_HANDOFF.template.md`, `commander-core.md`'s "Prototyper
    escape hatch", `references/crew-dispatch.md`'s mechanics) -- but that
    handoff carries no "Suggested Model Tier" field the way
    `IMPLEMENTER_HANDOFF.template.md` and `REVIEWER_HANDOFF.template.md`
    do, so signal 1 does not find it. This is a real, measured gap of the
    SAME SHAPE as the `commander-delegated` defect this file exists to
    catch, and it is reported (not silently declared -- no human ruling
    grounds a tier for it) in `.agent-work/567-n/RETURN.md`.
  * The `codex` and `local` harness rows are out of scope entirely -- this
    file's assertions are scoped to `ROLE_MODEL_TIERS["claude"]` only, per
    `decision:harness-dimension-is-required` (LAUNCH_ORDER.md, "Standing
    hazards").
"""

from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUN_CREW = ROOT / "scripts" / "run_crew.py"


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


RC = _load_module("run_crew_for_role_tier_coverage", RUN_CREW)

# --------------------------------------------------------------------------- #
# Signal 1: a role's own bounded HANDOFF template carries a model-tier field.
# --------------------------------------------------------------------------- #

_HANDOFF_STEM_RE = re.compile(r"^([A-Z][A-Z0-9]*)_HANDOFF\.template\.md$")
_MODEL_TIER_RE = re.compile(r"model tier", re.IGNORECASE)

HANDOFF_FILES = sorted(ROOT.glob("skills/*/templates/*_HANDOFF.template.md"))
HANDOFF_ROLES = {
    m.group(1).lower()
    for f in HANDOFF_FILES
    if (m := _HANDOFF_STEM_RE.match(f.name)) and _MODEL_TIER_RE.search(f.read_text(encoding="utf-8"))
}

# --------------------------------------------------------------------------- #
# Signal 2: a role whose own SKILL.md names a ratified LAUNCH_ORDER -- itself
# proven (below, as a real assertion, not a comment) to carry a required
# model-tier field -- as its frozen principal.
# --------------------------------------------------------------------------- #

LAUNCH_ORDER_TEMPLATE = ROOT / "skills" / "admiral" / "templates" / "LAUNCH_ORDER.template.md"
_REQUIRED_MODEL_TIER_RE = re.compile(r"model tier.{0,40}required|required.{0,40}model tier", re.IGNORECASE)
assert _REQUIRED_MODEL_TIER_RE.search(LAUNCH_ORDER_TEMPLATE.read_text(encoding="utf-8")), (
    "LAUNCH_ORDER.template.md no longer carries a 'Model tier (required)' field -- signal 2's whole "
    "premise (a role naming this document as its principal thereby receives a required tier) is void; "
    "re-derive the signal rather than leaving it pointed at a field that moved or was reworded"
)

_FROZEN_PRINCIPAL_RE = re.compile(
    r"LAUNCH_ORDER.{0,60}(?:is\s+)?your\s+frozen\s+principal", re.IGNORECASE | re.DOTALL
)
_SKILL_NAME_RE = re.compile(r"^name:\s*constellation-([a-z0-9-]+)\s*$", re.M)

SKILL_FILES = sorted(ROOT.glob("skills/*/SKILL.md"))
PRINCIPAL_ROLES = {
    m.group(1)
    for f in SKILL_FILES
    if _FROZEN_PRINCIPAL_RE.search(text := f.read_text(encoding="utf-8"))
    for m in [_SKILL_NAME_RE.search(text)]
    if m
}

# --------------------------------------------------------------------------- #
# Signal 3: specs/*.spine.toml -- one compiled-spine spec file per role,
# named <role>.spine.toml. Door doctrine's home, per test_cli_retirement_
# guard.py's own SPEC_SUFFIXES note ("door doctrine lands" in specs/*.toml).
# --------------------------------------------------------------------------- #

SPEC_FILES = sorted(ROOT.glob("specs/*.spine.toml"))
SPEC_ROLES = {f.name.removesuffix(".spine.toml") for f in SPEC_FILES}

SCANNED_ROLES = HANDOFF_ROLES | PRINCIPAL_ROLES | SPEC_ROLES

ALL_WALKED_PATHS = HANDOFF_FILES + SKILL_FILES + SPEC_FILES + [LAUNCH_ORDER_TEMPLATE]


def _census() -> str:
    return (
        f"{len(HANDOFF_FILES)} HANDOFF templates, {len(SKILL_FILES)} SKILL.md files, "
        f"{len(SPEC_FILES)} specs/*.spine.toml files -> scanned roles {sorted(SCANNED_ROLES)}"
    )


class TestTheWalkIsNotVacuous:
    """A guard that loops must assert what it looped over (CREW_CONTEXT.md,
    Verification Discipline) -- a narrowed glob or a retyped field name must
    read red, not silently clean."""

    def test_the_handoff_walk_reaches_real_templates(self):
        assert len(HANDOFF_FILES) >= 4, (
            f"only {len(HANDOFF_FILES)} skills/*/templates/*_HANDOFF.template.md files found -- "
            f"measured 4 (IMPLEMENTER, REVIEWER, CRITIC, PROTOTYPE) when this guard was written, "
            f"so a count this low means the glob narrowed and signal 1 is reading nothing"
        )

    def test_the_skill_walk_reaches_the_full_registry(self):
        assert len(SKILL_FILES) >= 15, (
            f"only {len(SKILL_FILES)} skills/*/SKILL.md files found -- measured 20 when this guard "
            f"was written, so a count this low means the glob narrowed and signal 2 is reading nothing"
        )

    def test_the_specs_walk_reaches_real_specs(self):
        assert len(SPEC_FILES) >= 1, (
            "no specs/*.spine.toml file found -- this is where signal 3 and door doctrine both live "
            "(test_cli_retirement_guard.py's SPEC_SUFFIXES note); an empty walk here means specs/ "
            "stopped being scanned at all"
        )

    def test_the_union_finds_real_roles(self):
        assert len(SCANNED_ROLES) >= 2, (
            f"the three signals together found only {sorted(SCANNED_ROLES)} -- measured "
            f"{{'commander-delegated', 'implementer', 'reviewer'}} when this guard was written, so a "
            f"result this small means a signal broke silently rather than doctrine actually shrinking. "
            f"{_census()}"
        )

    def test_handoff_signal_finds_its_two_known_members(self):
        """The g1-review-style fixture floor: the two roles whose Suggested
        Model Tier field made this signal worth writing must still be found,
        not just some non-empty set."""
        assert {"implementer", "reviewer"} <= HANDOFF_ROLES, (
            f"signal 1 no longer finds implementer/reviewer via their own HANDOFF template's "
            f"model-tier field -- found {sorted(HANDOFF_ROLES)}"
        )

    def test_principal_signal_finds_commander_delegated(self):
        """The exact defect this file exists to catch: commander-delegated's
        own SKILL.md names LAUNCH_ORDER as its frozen principal, and
        LAUNCH_ORDER carries a required model-tier field."""
        assert "commander-delegated" in PRINCIPAL_ROLES, (
            f"signal 2 no longer finds commander-delegated -- found {sorted(PRINCIPAL_ROLES)}. "
            f"This is the exact role whose gap this whole lane exists to fix; if the scan stopped "
            f"finding it, the guard has gone vacuous on its own motivating case"
        )


class TestTheWalkStaysInsideDoctrine:
    """Every glob is rooted at skills/ or specs/ by construction -- this pins
    that construction so a future edit widening a glob (e.g. to `**/*.md`)
    cannot silently drag in .agent-work/**'s own launch orders, which quote
    'Model tier (required)' and 'frozen principal' constantly and legitimately
    as records of what was said, not as doctrine live agents read."""

    def test_no_walked_path_reaches_agent_work_or_plans(self):
        strays = [
            p for p in ALL_WALKED_PATHS
            if ".agent-work" in p.parts or "docs" in p.parts and "superpowers" in p.parts
        ]
        assert not strays, f"walk reached archive/record paths it must not: {strays}"

    def test_every_walked_path_is_under_skills_or_specs(self):
        offenders = [
            p for p in ALL_WALKED_PATHS
            if p.relative_to(ROOT).parts[0] not in ("skills", "specs")
        ]
        assert not offenders, f"walk reached a path outside skills/ and specs/: {offenders}"


class TestTheSignalPredicatesThemselves:
    """Each signal is judged on a fixture before it is trusted on the corpus,
    same discipline test_cli_retirement_guard.py uses for its own patterns."""

    def test_model_tier_pattern_is_case_insensitive_and_reword_tolerant(self):
        assert _MODEL_TIER_RE.search("## Suggested Model Tier")
        assert _MODEL_TIER_RE.search("the model tier this dispatch runs at")
        assert not _MODEL_TIER_RE.search("tier list, no model mentioned")

    def test_frozen_principal_pattern_catches_the_real_sentence(self):
        assert _FROZEN_PRINCIPAL_RE.search(
            "The ratified `LAUNCH_ORDER` is your frozen principal and the Admiral is..."
        )

    def test_frozen_principal_pattern_leaves_the_producer_side_alone(self):
        """admiral/SKILL.md PRODUCES a LAUNCH_ORDER (`Every dispatch carries a
        completed templates/LAUNCH_ORDER.template.md`) -- that is not the same
        claim as CONSUMING one as a principal, and the pattern must tell them
        apart or every dispatcher of a launch order becomes a false positive."""
        assert not _FROZEN_PRINCIPAL_RE.search(
            "Every dispatch carries a completed `templates/LAUNCH_ORDER.template.md`. "
            "Paste prior-wave verdict text."
        )
        assert "admiral" not in PRINCIPAL_ROLES, (
            "signal 2 fired on admiral's own SKILL.md, which PRODUCES a LAUNCH_ORDER rather than "
            "taking one as its principal -- the producer/consumer distinction has broken"
        )


class TestDeclaredRolesCoverEveryScannedRole:
    """The guard proper. Every role live doctrine hands a model-tier-bearing
    dispatch artifact must resolve under the `claude` harness -- the
    `codex`/`local` rows are out of scope by `decision:harness-dimension-
    is-required` and are never asserted against here."""

    def test_every_scanned_role_is_declared_under_claude(self):
        declared = set(RC.ROLE_MODEL_TIERS["claude"].keys())
        gap = SCANNED_ROLES - declared
        assert not gap, (
            f"{sorted(gap)} live doctrine hands a model-tier-bearing dispatch artifact to, but "
            f"ROLE_MODEL_TIERS['claude'] does not declare -- resolve_model will refuse this role by "
            f"name exactly as it refused commander-delegated before this lane. {_census()}. "
            f"Declared: {sorted(declared)}"
        )

    def test_the_assertion_can_actually_fail(self):
        """Trust-but-verify: prove the subset check above is a real predicate,
        not a tautology, against a local fixture -- never the real table."""
        fixture_declared = {"implementer"}  # deliberately missing "reviewer"
        gap = SCANNED_ROLES - fixture_declared
        assert gap, "the subset check passed against a table known to be incomplete -- it is not testing anything"
        assert "reviewer" in gap
