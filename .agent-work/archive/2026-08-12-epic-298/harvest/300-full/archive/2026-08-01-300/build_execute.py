"""Author execute.json for issue #300, after cold-plan-critic triage.

All 19 cold-critic findings dispositioned in .agent-work/300/PLAN_CRITIC_DISPOSITION.md.
Every `command` postcondition in this file is executed verbatim in bash before the plan freezes.
"""
import json
from pathlib import Path

ROOT = Path(r"C:/Programs/constellation-skills-wt/298-300")
OUT = ROOT / ".agent-work" / "300" / "execute.json"

PYT = "python -m pytest"          # B2: `py -m pytest` has no pytest on this host. Measured.
SPINE_T = "skills/commander/templates/COMMANDER_SPINE.template.json"

E0_IMP = (
    "Confirm the frozen plan's intent and scope, then attest c1. READ FIRST, in this order: "
    ".agent-work/300/PROBLEM_STATEMENT.md, .agent-work/300/MISSION_FRAME.md, "
    ".agent-work/300/DIT-COMPARISON.md (the design-it-twice comparison this plan implements), and "
    ".agent-work/300/PLAN_CRITIC_DISPOSITION.md (the cold critic's findings and how each was "
    "disposed). The ratified intent is the launch order at "
    "C:/Programs/constellation-skills/.agent-work/epic-298/launch-orders/LAUNCH_ORDER-300.md. "
    "LOCALIZATION (do not go looking for these): this is a skill-source repo. docs/agents/ and "
    "docs/architecture/ do NOT exist here and their absence is BY DESIGN, not a gap to fix - there "
    "is no ORCHESTRATOR_CONTEXT.md, no GLOSSARY.md, no engine-config.json and no Cartographer "
    "packet in this worktree. The mission frame states the substituted structural record "
    "(docs/CHECKLIST_ENGINE_DESIGN.md, docs/CHECKLIST_SCHEMA.md, docs/CONSTELLATION_OVERVIEW.md); "
    "use it. The checklist config_ref names a path that is absent for the same reason; the engine "
    "degrades it to built-in defaults. Do NOT create any of those files. "
    "SHELL: every command postcondition in this plan assumes cwd = the worktree root "
    "C:/Programs/constellation-skills-wt/298-300 (the engine does not pass cwd= to command checks). "
    "Use `python -m pytest`, never `py -m pytest` - `py` resolves to a runtime with no pytest on "
    "this host."
)


def task(tid, title, imperative, pre, post, constraints, anchors):
    return {
        "id": tid, "title": title, "imperative": imperative,
        "preconditions": pre, "postconditions": post, "constraints": constraints,
        "anchors": anchors, "directives": None, "child_checklist": None,
        "status": "pending", "status_detail": {}, "result": None, "finding": None,
        "evidence": [], "rework_count": 0,
    }


def cond(cid, statement, check=None, override=False):
    c = {"id": cid, "statement": statement, "check": check, "satisfied": False}
    if override:
        c["override_policy"] = {"allowed": True, "authority": "human", "reason_required": True}
    return c


def cmd(c):
    return {"kind": "command", "command": c}


def art(kind, match=None):
    d = {"kind": "artifact", "evidence_type": kind}
    if match:
        d["match"] = match
    return d


APPROVE = art("review-result", {"verdict": "APPROVE"})

CONSTRAINTS_ALL = [
    "constraint:stochastic-boundary - no LLM inference at assembly time; the record is a pure "
    "function of (canon, selector state).",
    "constraint:markdown-in-git - no database, no query language, no new backend.",
    "constraint:delivery-not-use - record what was made available at which revision. Access "
    "tracing and transcript analysis are OUT OF SCOPE by the issue's own words.",
    "constraint:extend-dont-parallel - select via the engine's EXISTING active_id(); exactly one "
    "selector exists after this change.",
    "constraint:windows-corpus - every file write pins newline='\\n'; never rely on text-mode "
    "translation. CRLF, filesystem ordering and locale are the named irreproducibility sources.",
    "constraint:no-foreclosure - every manifest row must stay expressible as a Stratum A assertion "
    "(subject + source) later.",
    "SHELL: all command postconditions assume cwd = the worktree root. Use `python -m pytest`; "
    "`py` resolves to a runtime with no pytest on this host (measured).",
    "Project doctrine: a mechanism/workflow behaviour change requires targeted automated tests "
    "PLUS the relevant broader suite; both commands are named in the postconditions.",
]

ANCHORS_CORE = {
    "structural": [
        "scripts/checklist_engine.py - active_id() (:184) is THE selector and is reused, not "
        "duplicated; state()/render_human()/_STATE_CONTRACT_VERSION (:1336-1471) are the seam and "
        "the versioning idiom this change mirrors",
        "scripts/context_manifest.py - NEW: the producer, importing active_id from checklist_engine",
        SPINE_T + " - gains the context_refs declaration on its context step",
        "tests/test_checklist_engine.py - the broader suite that must stay green",
    ],
    "capability": [
        "capability:spine-keyed-context-delivery - deterministic SELECTION exists today; the "
        "declaration, the assembly and the record do not",
    ],
    "constraint": [
        "constraint:stochastic-boundary", "constraint:markdown-in-git",
        "constraint:delivery-not-use", "constraint:extend-dont-parallel",
        "constraint:windows-corpus", "constraint:no-foreclosure",
        "assumption:5 - VERIFIED THIS RUN to be weaker than the spec reads: the spine's gate notes "
        "ground deterministic SELECTION only; assembly is genuinely unbuilt",
    ],
    "decision": [
        "decision:rev-is-lf-normalised-blob-oid - revision identity is the git blob OID of "
        "LF-normalised bytes computed in-process; never a commit SHA, never a git subprocess "
        "@grade: settled/measured - leans g1-implement - settle: already settled; three "
        "independent panel authors each verified equality with git hash-object on real files "
        "including CRLF twins",
        "decision:declaration-field-is-context_refs - the declaration is an OPTIONAL ordered list "
        "named context_refs on the spine task; absent means empty. Named context_refs rather than "
        "context because tasks['context']['context'] is legal but unreadable. "
        "@grade: settled/measured - leans g1-implement",
        "decision:no-globs-order-is-content - never enumerate the filesystem; declaration order IS "
        "content and is never sorted @grade: settled/measured - leans g1-implement",
        "decision:producer-is-a-sibling-module - the producer lives in scripts/context_manifest.py "
        "and IMPORTS active_id from checklist_engine rather than being inlined, keeping the "
        "engine's diff small while leaving exactly one selector. This is an extension, not a "
        "parallel path. @grade: guess - leans g1-implement - settle: if the reviewer finds the "
        "import seam creates a second effective selector, inline it into checklist_engine.py",
    ],
    "evidence": [
        "claim:revision-identity-present - the computed identity equals git hash-object / "
        "git rev-parse HEAD:<path> for a tracked clean file, and is still produced for dirty, "
        "untracked, gitignored and out-of-repo files",
        "claim:manifest-on-every-assembly - proved by driving the REAL producer through the "
        "engine's own active_id() selector, never a hand-injected fixture",
        "claim:deterministic-across-environments - a CLEAN SECOND CHECKOUT (git worktree add at "
        "the same commit, different path, mutated LC_ALL/LANG/PYTHONHASHSEED) produces "
        "byte-identical output",
    ],
    "confidence_flags": [
        "scripts/agent_work_root.py - VERIFIED live this run to return the WORKTREE, not the main "
        "checkout, while an Admiral lease is active. Any durable root token must account for it.",
        "lesson:windows-subprocess-env-does-not-shadow-path-resolution - on Windows, passing env= "
        "into subprocess.run does NOT change which executable an unqualified name resolves to. The "
        "locale arm of the determinism test must therefore assert it actually took effect inside "
        "the child, not assume it did.",
    ],
}

INH = "g1-implement anchors - the same structural/capability/constraint/decision/evidence anchors"

ANCHORS_AOT = {
    "structural": [
        "scripts/context_projection.py - NEW: the ahead-of-time generator and its --check mode",
        "skills/commander/CONTEXT_PROJECTION.json - NEW: the committed reviewable artifact",
        "tests/test_install_constellation.py, tests/test_spine_provenance_check.py - these read "
        "skills/commander/ and the spine template; adding a file there is exactly what they exist "
        "to catch, so the FULL suite must run, not a -k filter",
    ],
    "capability": [
        "capability:reviewable-doctrine-diff - the ahead-of-time-generation bullet of spec B2 "
        "('a versioned script builds the projection, so every doctrine change produces a reviewable "
        "diff of what agents will actually see'). This is NOT the kernel-plus-fragments break, "
        "which is the out-of-scope part of B2.",
    ],
    "constraint": [
        "constraint:determinism-is-the-acceptance-test", "constraint:windows-corpus",
    ],
    "decision": [
        "decision:committed-artifact-rev-from-object-db - in the COMMITTED artifact rev resolves "
        "ONLY from the git object DB (untracked -> null), so the artifact is identical on any "
        "machine; in the RUN manifest it resolves from the bytes actually delivered. Same row "
        "shape, two truth-sources. @grade: guess - leans g2-implement - settle: generate in this "
        "worktree and in a clean second checkout and byte-compare; they must be identical",
        "decision pressure: whether the committed artifact belongs to #300 at all, or defers to "
        "issue H - this is the FLOATED convergence choice and is NOT this gate's to settle. The "
        "cold critic independently observed that no acceptance criterion of #300 names a committed "
        "artifact; that observation has been relayed upward.",
    ],
    "evidence": [
        "claim:committed-artifact-is-environment-independent",
        "adversarial fixtures REQUIRED: a stale committed artifact must NOT silently PASS; an "
        "untracked-vs-absent file must not make two environments disagree; a declaration-order "
        "permutation MUST register as drift",
    ],
    "confidence_flags": [
        "This is the ONE gate contingent on the floated convergence choice. If the Admiral rules "
        "the committed artifact out of #300, amend this gate via the engine's `amend` verb - never "
        "hand-edit. Deleting it now leaves #300 whole: the declaration, the run manifest and the "
        "cross-environment determinism evidence all live in g1.",
    ],
}

ANCHORS_DOC = {
    "structural": [
        "docs/CHECKLIST_SCHEMA.md - the Task table gains a context_refs row",
        "docs/CHECKLIST_ENGINE_DESIGN.md - the projection-port narrative this change extends",
        SPINE_T + " - the imperative prose, which KEEPS its non-mechanical rules",
        ".agent-work/300/OBLIGATIONS-301.md - NEW: what #301 may and may not rely on",
    ],
    "capability": ["capability:spine-keyed-context-delivery"],
    "constraint": [
        "decision:prose-stays-plus-lint - the imperative KEEPS the rules a path list cannot express "
        "(the substitute-and-record rule; 'a missing engine-config is a sanctioned degradation, do "
        "NOT create the overlay file'). Deleting them is a behaviour change to every Commander run.",
    ],
    "decision": [
        "decision:prose-stays-plus-lint @grade: settled/measured - leans g3-implement",
    ],
    "evidence": [
        "Doc-only gate: the invariant chain is PRE-AUTHORED as explicit postconditions below so the "
        "crew verifies a frozen chain rather than improvising a grep-for-marker proxy.",
        "claim:consumable-as-episode-context-field - owned by c7/c8 below, not left to prose",
    ],
    "confidence_flags": [],
}

items, tasks = [], []


def add(t):
    items.append(t["id"])
    tasks.append(t)


add(task("e0-context", "Load execution context", E0_IMP, [],
         [cond("c1", "frozen intent, mission frame, design comparison and critic disposition read; "
                     "plan intent and scope confirmed")],
         [], None))

# ------------------------------------------------------------------ g1
add(task(
    "g1-implement",
    "Run-time half: revision identity, context_refs declaration, producer, run manifest, "
    "first real declaration, cross-environment determinism",
    "Fill skills/commander/templates/IMPLEMENTER_HANDOFF.template.md and dispatch a "
    "constellation-implementer subagent. Put the crew's own driven plan file in its OWN "
    "subdirectory .agent-work/300/g1-implement/ - a plan file in the work-id root resolves to the "
    "SAME gauge.json as this spine and can trip the Context Governor on a reading that has nothing "
    "to do with the fresh crew. SCOPE: (1) the revision-identity function - git blob OID of "
    "LF-normalised bytes, computed in-process, no git subprocess; (2) the OPTIONAL ordered "
    "context_refs declaration on the spine task object, absent meaning empty; (3) the pure producer "
    "in scripts/context_manifest.py, selecting via the EXISTING active_id() imported from "
    "checklist_engine; (4) the run-local manifest, with every varying fact quarantined under a "
    "single `run` key that is the entire exclusion set; (5) THE FIRST REAL DECLARATION on the "
    "Commander spine template's context step, listing the files that step's imperative already "
    "names; (6) the cross-environment determinism test. There is NO new CLI verb - the manifest is "
    "a JSON file and needs no print surface. Wait for and integrate the IMPLEMENTER_RESULT.",
    [],
    [
        cond("c1", "IMPLEMENTER_RESULT returned", art("implementer-result")),
        cond("c2", "targeted tests green: the identity function equals git hash-object on a real "
                   "tracked file; CRLF/LF twins of identical content produce the SAME rev; AND a "
                   "manifest is produced by driving the REAL producer through the engine's "
                   "active_id() selector, not a hand-built fixture",
             cmd(f"{PYT} tests/test_context_manifest.py -q")),
        cond("c3", "cross-environment determinism: a clean second checkout (git worktree add at the "
                   "same commit, different path, mutated LC_ALL/LANG/PYTHONHASHSEED) yields "
                   "byte-identical output. NOTE the honest limit: same OS and same filesystem - "
                   "this exercises path/locale/hash-ordering, not a cross-OS rebuild.",
             cmd(f"{PYT} tests/test_context_determinism.py -q")),
        cond("c4", "the first real declaration exists on the Commander spine template (this check "
                   "FAILS at HEAD today - verified before freezing)",
             cmd(f"grep -q 'context_refs' {SPINE_T}")),
        cond("c5", "broader engine suite still green (mechanism change -> targeted PLUS broader)",
             cmd(f"{PYT} tests/test_checklist_engine.py -q")),
        cond("c6", "no filesystem enumeration and no unpinned text write in the new producer - the "
                   "two constraints the mission frame calls load-bearing are mechanically checked, "
                   "not merely asserted in a constraints array",
             cmd(f"{PYT} tests/test_context_manifest.py -q -k "
                 "'no_globs or newline_pinned' --no-header")),
    ],
    CONSTRAINTS_ALL + [
        "context_refs is OPTIONAL. A spine without it produces an EMPTY manifest and must NOT "
        "crash - every existing spine keeps working untouched.",
        "No globs, no directory patterns, no os.listdir, no sorted() over paths anywhere in the "
        "producer. Declaration order is content.",
        "Do NOT concatenate file contents. This is a manifest, not an archive.",
        "Do NOT add a CLI verb (cut by the cold critic as YAGNI; it would touch the engine's "
        "persistence control flow for a convenience print).",
    ],
    ANCHORS_CORE,
))

add(task(
    "g1-review", "Run-time half: review",
    "Fill skills/commander/templates/REVIEWER_HANDOFF.template.md and dispatch a "
    "constellation-reviewer. Instruct it SPECIFICALLY to hunt the round-trip-blindness class: a "
    "test that parses the real shipped artifacts proves those artifacts are clean, NOT that the "
    "tool is correct. Require adversarial fixtures that make the tool return a WRONG answer - a "
    "false FAIL on valid input and a silent PASS on invalid input - and do NOT accept a re-run of "
    "the suite as a substitute. It must also confirm: the producer reuses the EXISTING active_id() "
    "and no second selector exists; the determinism test really creates a SEPARATE checkout rather "
    "than running twice in the same tree, and its locale mutation demonstrably took effect inside "
    "the child process; and every file write pins newline='\\n'. Wait for and integrate the "
    "REVIEW_RESULT.",
    [cond("p1", "g1-implement returned a result with targeted, determinism and broader suites green")],
    [cond("c1", "REVIEW_RESULT returned", art("review-result"))],
    ["Never bias the reviewer toward approval; a BLOCK is a successful review."],
    {"inherits": INH},
))

add(task(
    "g1-integrate", "Run-time half: integrate",
    "Check the verdict. On APPROVE, verify the crew's side-effects against the world YOURSELF: "
    "confirm the IMPLEMENTER_RESULT is fresh (scripts/run_crew.py --verify-result, not a stale "
    "leftover), re-run the pasted evidence in your own hands, and confirm the postconditions pass. "
    "On BLOCK, return for rework or raise a blocker. Log out-of-scope finds as triage candidates "
    "and harvest the result's Workflow Feedback section into the lesson-candidate pool.",
    [cond("p1", "g1-review returned a verdict")],
    [
        cond("c1", "the whole targeted set re-runs green in the Commander's own hands",
             cmd(f"{PYT} tests/test_context_manifest.py tests/test_context_determinism.py "
                 "tests/test_checklist_engine.py -q"), override=True),
        cond("c2", "reviewer verdict is APPROVE", APPROVE),
    ],
    [], None,
))

# ------------------------------------------------------------------ g2
add(task(
    "g2-implement",
    "Ahead-of-time half: the committed projection artifact and its generator (CONTINGENT)",
    "CONTINGENT GATE - do not start until the floated convergence choice has landed. If the Admiral "
    "rules the committed artifact out of #300's scope, amend this gate through the engine's `amend` "
    "verb; never hand-edit the plan. Deleting it leaves #300 whole - the declaration, the run "
    "manifest and the determinism evidence all live in g1. Fill the handoff and dispatch, with the "
    "crew's plan file under .agent-work/300/g2-implement/. SCOPE: (1) scripts/context_projection.py "
    "- generate the committed per-role artifact, plus a --check mode that regenerates from current "
    "canon and compares; (2) skills/commander/CONTEXT_PROJECTION.json, content-only with ZERO "
    "varying fields. In the committed artifact rev resolves ONLY from the git object DB, so an "
    "untracked file is null and the artifact is byte-identical on any machine; the run manifest "
    "keeps resolving from the bytes actually delivered.",
    [cond("p1", "g1 integrated: identity function, context_refs declaration, producer and the "
                "first real declaration all exist and are reviewed")],
    [
        cond("c1", "IMPLEMENTER_RESULT returned", art("implementer-result")),
        cond("c2", "adversarial fixtures green: a stale committed artifact does NOT silently PASS; "
                   "an untracked-vs-absent file cannot make two environments disagree; a "
                   "declaration-order permutation DOES register as drift",
             cmd(f"{PYT} tests/test_context_projection.py -q")),
        cond("c3", "the generator is idempotent on its own output. NECESSARY, NOT SUFFICIENT - "
                   "generator and checker are the same code reading the same filesystem, so a "
                   "generator that produces garbage deterministically also passes this. The "
                   "discriminating evidence is c2 and g1.c3, not this.",
             cmd("py scripts/context_projection.py --check")),
        cond("c4", "FULL suite green - not a -k filter. test_install_constellation.py and "
                   "test_spine_provenance_check.py read skills/commander/ and the spine template "
                   "and are exactly what a new file there must not break.",
             cmd(f"{PYT} tests/ -q")),
    ],
    CONSTRAINTS_ALL + [
        "The exclusion set stays structurally separate from content: the committed artifact has NO "
        "run key at all.",
        "A round-trip over the real corpus is NOT sufficient evidence on its own.",
    ],
    ANCHORS_AOT,
))

add(task(
    "g2-review", "Ahead-of-time half: review",
    "Dispatch a constellation-reviewer. It must attack the determinism claim rather than re-run it: "
    "confirm the untracked-vs-absent fixture cannot disagree between environments, that a "
    "declaration-order permutation registers as drift, and that a stale artifact does not silently "
    "PASS. It must also state plainly whether the committed artifact serves any of #300's three "
    "acceptance criteria, or only spec B2's reviewable-diff purpose - the cold plan critic raised "
    "that and it is relevant to the Admiral's ruling.",
    [cond("p1", "g2-implement returned a result with its fixtures and the full suite green")],
    [cond("c1", "REVIEW_RESULT returned", art("review-result"))],
    [], {"inherits": "g2-implement anchors"},
))

add(task(
    "g2-integrate", "Ahead-of-time half: integrate",
    "Check the verdict, verify side-effects against the world yourself, re-run the evidence in your "
    "own hands, log triage candidates, harvest workflow feedback.",
    [cond("p1", "g2-review returned a verdict")],
    [
        cond("c1", "the full suite re-runs green in the Commander's own hands",
             cmd(f"{PYT} tests/ -q"), override=True),
        cond("c2", "reviewer verdict is APPROVE", APPROVE),
    ],
    [], None,
))

# ------------------------------------------------------------------ g3
add(task(
    "g3-implement",
    "Doctrine, the declaration-vs-prose lint, and the #301 obligations statement",
    "Doc-and-lint gate. The invariant chain is PRE-AUTHORED in the postconditions below so the crew "
    "verifies a frozen chain rather than improvising a grep-for-marker proxy. Fill the handoff and "
    "dispatch, crew plan file under .agent-work/300/g3-implement/. SCOPE: (1) the mechanical lint "
    "pinning every declared context_refs path against the step's imperative prose, WITH a negative "
    "test proving it rejects a divergent fixture; (2) one row in the docs/CHECKLIST_SCHEMA.md Task "
    "table for context_refs; (3) the docs/CHECKLIST_ENGINE_DESIGN.md narrative extension describing "
    "the manifest beside the existing state projection; (4) .agent-work/300/OBLIGATIONS-301.md - an "
    "explicit two-part statement of what issue #301 MAY rely on and what it MAY NOT, plus a shape "
    "test asserting a produced run manifest is a JSON value assignable to an episode `context` "
    "field with no transformation.",
    [cond("p1", "g1 integrated (and g2, if the convergence choice kept it in scope)")],
    [
        cond("c1", "IMPLEMENTER_RESULT returned", art("implementer-result")),
        cond("c2", "the lint is green over the real shipped spine templates",
             cmd(f"{PYT} tests/test_context_declaration_lint.py -q")),
        cond("c3", "the lint actually FIRES on a divergent fixture. This is the discriminating "
                   "check: a lint that only passes on a clean corpus is not evidence. The named "
                   "test must exist and pass - a missing file or missing test id exits 4 and FAILS, "
                   "which is correct.",
             cmd(f"{PYT} tests/test_context_declaration_lint.py::"
                 "test_divergent_declaration_is_rejected -q")),
        cond("c4", "INVARIANT - the substitute-and-record rule SURVIVES verbatim in the context "
                   "step's imperative",
             cmd(f"grep -q 'substitute the closest repo doctrine' {SPINE_T}")),
        cond("c5", "INVARIANT - the sanctioned-degradation rule SURVIVES verbatim",
             cmd(f"grep -q 'sanctioned degradation' {SPINE_T}")),
        cond("c6", "INVARIANT - context_refs is documented as a Task-table ROW (anchored on the "
                   "table pipe, not the English word 'context', which already appears 10 times in "
                   "that file). This check FAILS at HEAD today - verified before freezing.",
             cmd("grep -qE '^\\| *`?context_refs`?' docs/CHECKLIST_SCHEMA.md")),
        cond("c7", "the #301 obligations artifact exists and states BOTH halves - what may be "
                   "relied on and what may not",
             cmd("test -f .agent-work/300/OBLIGATIONS-301.md && "
                 "grep -qi 'may rely' .agent-work/300/OBLIGATIONS-301.md && "
                 "grep -qi 'may not' .agent-work/300/OBLIGATIONS-301.md")),
        cond("c8", "the third acceptance criterion is mechanically owned: a produced run manifest "
                   "loads as JSON and is assignable to an episode `context` field untransformed",
             cmd(f"{PYT} tests/test_context_manifest.py -q -k 'episode_context_field' --no-header")),
    ],
    CONSTRAINTS_ALL + [
        "DO NOT delete the rules the imperative carries that a path list cannot express. The prose "
        "stays; the lint pins it.",
        "Never hand-edit .agent-work/LESSONS.md; structured deltas via apply_lessons_delta.py only.",
    ],
    ANCHORS_DOC,
))

add(task(
    "g3-review", "Doctrine and lint: review",
    "Dispatch a constellation-reviewer. It must confirm each pre-authored invariant by RUNNING the "
    "command, not by reading the diff; hunt round-trip blindness on the lint specifically by "
    "authoring its own divergent fixture and confirming the lint fails on it; and check that the "
    "#301 obligations statement makes claims the code actually keeps - in particular that nothing "
    "in it promises USE when the manifest only records DELIVERY.",
    [cond("p1", "g3-implement returned a result with the invariant chain green")],
    [cond("c1", "REVIEW_RESULT returned", art("review-result"))],
    [], {"inherits": "g3-implement anchors"},
))

add(task(
    "g3-integrate", "Doctrine and lint: integrate",
    "Check the verdict, verify side-effects yourself, re-run the invariant commands in your own "
    "hands, log triage candidates, harvest workflow feedback. This is the LAST gate that mutates "
    "doctrine, so the committed artifact's freshness is re-established here rather than left at the "
    "state g2 found it in.",
    [cond("p1", "g3-review returned a verdict")],
    [
        cond("c1", "the FULL suite re-runs green - no -k filter, because this change touches "
                   "skills/commander/ and the spine template and six test modules that read them "
                   "do not survive a 'context or checklist_engine' filter",
             cmd(f"{PYT} tests/ -q"), override=True),
        cond("c2", "reviewer verdict is APPROVE", APPROVE),
        cond("c3", "the committed projection is still fresh AFTER the doctrine edits (re-established "
                   "last, not left at g2's state). Waive with reason if g2 was amended out.",
             cmd("py scripts/context_projection.py --check"), override=True),
    ],
    [], None,
))

# ------------------------------------------------------------------ g4
add(task(
    "g4-cold-panel",
    "Full cold-panel review over the complete change (spec B0.4 review class)",
    "REASONING GATE - no implementer crew; this gate dispatches critics, not builders. "
    "Crew-waiver reason: the deliverable is an adjudicated finding set over work independent "
    "reviewers have already approved gate by gate; a fourth builder would add nothing. "
    "decision:full-cold-panel makes independent agentic review at FULL PANEL depth the floor for "
    "#300 - a light single-reviewer pass is not permitted. Dispatch THREE critics in parallel, each "
    "reading the DIFF and the mission frame ONLY, with no authoring context and no gate results: "
    "(1) intent-fit - does the change serve delivery-not-use observability, and has it quietly "
    "widened toward access tracing; (2) testability - can each pathway be exercised AND falsified, "
    "and does the determinism evidence prove the tool correct rather than the corpus clean; "
    "(3) simplicity/YAGNI - what can be deleted, which field does not earn its place. Each writes "
    "to .agent-work/300/cold-panel/CRITIC-<lens>.md. Triage EVERY finding explicitly - edit, reopen "
    "the owning gate, or reject with a reason; a critic never self-triages. Record every finding "
    "and its disposition in .agent-work/300/COLD_PANEL_DISPOSITION.md, ending with a line "
    "'UNTRIAGED: 0' only once that is actually true.",
    [cond("p1", "every implementing gate integrated")],
    [
        cond("c1", "three critic reports exist at their named paths and are non-empty - panel depth "
                   "is evidenced by artifacts, not asserted",
             cmd("test -s .agent-work/300/cold-panel/CRITIC-intent-fit.md && "
                 "test -s .agent-work/300/cold-panel/CRITIC-testability.md && "
                 "test -s .agent-work/300/cold-panel/CRITIC-simplicity.md")),
        cond("c2", "every finding carries an explicit disposition; the disposition count is derived "
                   "from the reports, not hand-typed",
             cmd("py -c \"import pathlib,sys,re; d=pathlib.Path('.agent-work/300'); "
                 "p=d/'COLD_PANEL_DISPOSITION.md'; t=p.read_text(encoding='utf-8') if p.exists() "
                 "else ''; n=len(re.findall(r'(?im)^\\s*[-*|]?\\s*disposition\\s*[:|]', t)); "
                 "sys.exit(0 if n>0 and 'UNTRIAGED: 0' in t else 1)\"")),
    ],
    ["Panel depth is the floor, not a target to negotiate down.",
     "Findings are triaged by the Commander only because no human is reachable; the disposition "
     "record is surfaced to the Admiral at return."],
    {
        "structural": ["the complete diff of branch epic-298/300 against main"],
        "capability": ["capability:spine-keyed-context-delivery",
                       "capability:reviewable-doctrine-diff"],
        "constraint": ["decision:full-cold-panel - spec B0.4 puts #300 in the full cold-panel "
                       "review class @grade: settled/inherited - leans g4-cold-panel"],
        "decision": ["decision:full-cold-panel @grade: settled/inherited - leans g4-cold-panel"],
        "evidence": ["every claim in the mission frame's Claims / Evidence Surfaces section"],
        "confidence_flags": [],
    },
))

plan = {
    "work_id": "300", "type": "gated",
    "config_ref": "docs/agents/engine-config.json",
    "items": items, "tasks": {t["id"]: t for t in tasks},
    "consolidation": None, "triage_candidates": [], "blockers": [],
}
OUT.write_text(json.dumps(plan, indent=2, ensure_ascii=False) + "\n",
               encoding="utf-8", newline="\n")
print(f"wrote {OUT}: {len(items)} items")
for i in items:
    print("  -", i)
