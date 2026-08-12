"""Drive the issue-716 interrogation survey through the engine, one question at a time."""
import subprocess, sys
from pathlib import Path

ENGINE = r"C:\Users\fredc\.claude\skills\constellation-interrogator\scripts\checklist_engine.py"
FILE = ".agent-work/issue-716/interrogation.json"
SESSION = "interrogator-issue-716"


def eng(*args):
    cmd = [sys.executable, ENGINE, "--file", FILE, *args, "--session-id", SESSION]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    tail = (r.stdout or "").strip().splitlines()[-1:] + (r.stderr or "").strip().splitlines()[-1:]
    print(f"  [{r.returncode}] {' | '.join(tail)}")
    return r.returncode


QA = [
    ("q1",
     "ANSWER (fact): canonical home is the constellation-skills repo, C:/Programs/constellation-skills/scripts/ "
     "— run_crew.py and verify_agent_feedback.py both live there. The ~/.claude/skills/constellation-*/scripts/ "
     "copies are INSTALL OUTPUT: install_constellation.py:515-518 shutil.copy2's each script named in "
     "SKILL_SCRIPT_BUNDLES (install_constellation.py:104-121) into <skill>/scripts/. f1Brainz needs NO source "
     "change: it neither vendors nor imports these scripts, it only invokes the INSTALLED copies from spine "
     "check-commands by absolute path. EVIDENCE: glob **/run_crew.py + **/verify_agent_feedback.py under "
     "constellation-skills returns scripts/ plus only .agent-work/ eval-harness copies.",
     "q1 resolved from the filesystem: the whole run's file-ownership scope sits in constellation-skills, not f1Brainz."),

    ("q2",
     "ANSWER (fact): BOTH still reproduce on canonical HEAD, and BOTH fail in the worst way for the caller. "
     "Repro .agent-work/issue-716/evidence/repro_716.py, run 2026-08-01: "
     "(1) run_crew.load_registry_for_resume('constellation/epic-659/665/g1/implementer/attempt-1') returns [] "
     "— it takes parts[1]='epic-659' and reads a registry path that does not exist; load_registry() treats a "
     "missing file as an EMPTY registry (run_crew.py:106-113), so the wrong-work-id lookup is indistinguishable "
     "from 'no crews yet'. The eventual REFUSED message names the session, never the parse. "
     "(2) verify_agent_feedback._current_run_archive_dirs(agent_work, 'epic-659/665') returns [] against a real "
     "package at archive/2026-07-25-epic-659/665 — while the slashless control 'issue-9' matches. At --phase "
     "archive that surfaces as 'no archived run package found', i.e. it blames the operator for not archiving. "
     "So both are MISLEADING failures, not clean errors: the regression tests must assert the POSITIVE match, "
     "not merely that an error is raised.",
     "q2 resolved by live reproduction against canonical sources: both defects current, both fail misleadingly rather than loudly."),

    ("q3",
     "ANSWER (fact): yes — unambiguous from the RIGHT. session_name() (run_crew.py:83-88) emits "
     "'constellation/{work_id}/{gate}/{role}/attempt-{n}'. gate and role are CLI-supplied single tokens "
     "(--gate/--role, run_crew.py:770-771) used verbatim as filename stems in run_log_paths() "
     "(run_crew.py:99-103), so a '/' in either would already break log capture on every platform; attempt is "
     "'attempt-<int>'. Therefore the last three segments are fixed and work_id = '/'.join(parts[1:-3]). For a "
     "slashless work_id parts has exactly 5 elements and parts[1:-3] == [parts[1]], so the right-anchored parse "
     "is BYTE-IDENTICAL to today's behavior on every currently-working name — it only adds correctness.",
     "q3 resolved from the grammar: a right-anchored parse is exact and strictly backward compatible."),

    ("q4",
     "ANSWER (fact): NESTED. No script performs the archive move — the commander spine's archive imperative does "
     "it in prose: 'Move .agent-work/<work-id>/ to .agent-work/archive/<date>-<work-id>/'. Interpolated verbatim "
     "for work_id 'epic-659/665' that is archive/2026-07-25-epic-659/665/ — a TWO-level path whose leaf .name is "
     "'665' and whose first segment is '2026-07-25-epic-659'. _current_run_archive_dirs uses a single-level "
     "iterdir() and compares path.name (verify_agent_feedback.py:72-80), so neither test can ever hold. "
     "Corollary the matcher must respect: for an N-segment work_id the package sits N levels below archive/, and "
     "the existing rule (name == work_id OR name.endswith('-'+work_id)) is exactly the N=1 case of a "
     "relative-path rule.",
     "q4 resolved: the on-disk layout the doctrine text actually produces is nested, which fixes what the matcher must find."),

    ("q5",
     "ANSWER (decision, self-decided under the engagement's standing delegation): OPTION A — generalize the "
     "MATCHER, leave the '<date>-<work-id>' archive convention untouched. Rationale: (i) blast radius — A "
     "changes one helper plus its call site; B rewrites the archive sentence in commander, commander-delegated "
     "and admiral spine templates and orphans any archive already on disk; (ii) the failure being fixed is "
     "'an agent had to remember a rule', and B ADDS a rule every future agent must remember (sanitize '/' before "
     "naming the archive dir) while A makes the naive interpolation correct; (iii) A is a strict superset — the "
     "N=1 case is bit-identical to today. Mitigation for B's one real advantage (no first-segment ambiguity "
     "between '<date>-epic-659' and a literal work_id 'epic-659'): the relative-path rule requires the segment "
     "COUNT to equal the work_id's, so a 1-segment work_id can never match a 2-level package. The matcher will "
     "additionally TOLERATE a flattened name, so a future move to B needs no third change.",
     "q5 decided: generalize the matcher (Option A); the archive naming convention is left alone deliberately."),

    ("q6",
     "ANSWER (fact): via install_constellation.py, and it needs an explicit edit or the helper silently fails to "
     "install. SKILL_SCRIPT_BUNDLES (install_constellation.py:104-121) is a per-skill copy list: run_crew.py "
     "ships to commander AND explorer; verify_agent_feedback.py ships to commander AND admiral. A sibling module "
     "not named anywhere is simply not copied, and the import fails at runtime in the install — which is EXACTLY "
     "the gauge_reader.py drift the installer's own comment (lines 77-86) documents as having left the Context "
     "Governor inert in every install since it shipped. The right lever already exists: SCRIPT_RUNTIME_COMPANIONS "
     "(line 87) + expand_script_bundle() (line 93), applied at discovery so every install path inherits it. "
     "GAP: the pinning test (tests/test_install_constellation.py:1185-1198) only parses checklist_engine.py for "
     "the 'parent / \"x.py\"' dynamic-load idiom — a plain 'from work_id import ...' is invisible to it, so the "
     "existing guard would NOT catch this new companion going missing.",
     "q6 resolved: the installer needs a companion entry, and its guard test is blind to plain imports — both must be addressed."),

    ("q7",
     "ANSWER (decision, self-decided under the engagement's standing delegation): IN SCOPE, bounded. "
     "_entry_block (verify_agent_feedback.py:24-39) matches 'work_id in line' against '## ' headings; the repro "
     "shows _entry_block(text,'epic-659') returning the heading for 'epic-659/665'. Under this repo's "
     "epic-<N>/<issue> convention a parent's id is ALWAYS a prefix of its children's, so an Admiral verifying its "
     "own epic feedback can silently pass on a child's entry — the same nested-id root the issue names, in the "
     "same file, reachable by the same helper. Bound it to a STRICTLY-WIDENING disambiguation: when more than one "
     "heading matches, prefer the most specific (longest work_id token in the heading); a single match behaves "
     "exactly as today. No heading that resolves correctly now may change.",
     "q7 decided: in scope as a strictly-widening tie-break only; no currently-passing heading may change resolution."),

    ("q8",
     "ANSWER (fact): C:/Programs/constellation-skills/tests/ — unittest-style modules run under pytest, with a "
     "file per script: test_crew_launcher.py (run_crew), test_verify_agent_feedback.py, "
     "test_install_constellation.py, test_agent_work_root.py. f1Brainz's ORCHESTRATOR_CONTEXT evidence table "
     "(DB-canonical, physics/evo/data regions, region suites) governs f1Brainz src/ and does NOT bind this "
     "change. Existing coverage is slashless-only: test_crew_launcher.py exercises session names of the form "
     "'constellation/issue-1/g1/reviewer/attempt-1'; test_verify_agent_feedback.py's archive tests all use "
     "'2026-06-10-issue-9'. A new tests/test_work_id.py is the natural home for the shared helper, mirroring "
     "test_agent_work_root.py.",
     "q8 resolved: constellation-skills/tests is the evidence surface; existing coverage is slashless-only, which is why this shipped."),

    ("q9",
     "ANSWER (decision, self-decided under the engagement's standing delegation): a NEW module, "
     "scripts/work_id.py. Rationale: agent_work_root.py has one job — resolve the durable checkout root — and it "
     "is NOT bundled to explorer, which does carry run_crew.py; folding the parser in would either under-install "
     "the helper or force agent_work_root.py into explorer's bundle for a reason unrelated to its purpose. A "
     "separate module also gives the deletion test a clean answer (delete it and the same string-parsing bug "
     "reappears in two places) and gives the two call sites ONE seam — which is what the issue asked for. "
     "Cost accepted: one new installable artifact, wired via SCRIPT_RUNTIME_COMPANIONS so it propagates to every "
     "skill carrying either script without hand-editing four bundles.",
     "q9 decided: a new scripts/work_id.py module, wired as a runtime companion of both call sites."),
]

for qid, finding, why in QA:
    print(qid)
    eng("start", qid)
    eng("record", qid, "--result", "pass", "--finding", finding)
    eng("advance", qid, "--why", why)
