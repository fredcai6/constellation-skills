import subprocess, sys

ENGINE = r"C:\Users\fredc\.claude\skills\constellation-interrogator\scripts\checklist_engine.py"
FILE = ".agent-work/issue-716/interrogation.json"
SESSION = "interrogator-issue-716"


def eng(*args):
    r = subprocess.run([sys.executable, ENGINE, "--file", FILE, *args, "--session-id", SESSION],
                       capture_output=True, text=True, encoding="utf-8")
    print(f"[{r.returncode}] {(r.stdout or '').strip()[-400:]} {(r.stderr or '').strip()[-400:]}")


eng("start", "zc-consolidate")
eng("record", "zc-consolidate", "--result", "pass", "--finding",
    "Interrogation record written to .agent-work/issue-716/interrogation-record.json; "
    "verify_interrogation.py exits 0 (mode=delegated, questions=9, consolidated=True). "
    "Sign-off is the dispatching principal's standing delegation in the engagement brief, "
    "quoted verbatim; the three Commander-taken decisions (q5 archive-matcher-not-convention, "
    "q7 _entry_block tie-break in scope, q9 new scripts/work_id.py) are each surfaced in the "
    "mission frame with their rejected alternative so the principal can reverse any one.")
eng("consolidate", "--summary",
    "RESOLVED UNDERSTANDING (issue #716). CAPABILITY: constellation's commander/admiral tooling must "
    "identify a run by a work_id that may contain '/', because this repo's own nested "
    "Commander-under-Admiral convention is epic-<N>/<issue>. Two shared-machinery sites assume it "
    "cannot. (1) run_crew.load_registry_for_resume parses the work_id out of a session name as "
    "session.split('/')[1], dropping every segment after the first — the lookup then reads a "
    "nonexistent registry and returns [], which is indistinguishable from 'no crews yet'. "
    "(2) verify_agent_feedback._current_run_archive_dirs matches a single-level path.name against the "
    "work_id, unsatisfiable when the package is nested N levels below archive/. Both reproduce today "
    "(evidence/repro_716.py). A third, unnamed instance of the same root: _entry_block substring-matches "
    "a work_id in a '## ' heading, so a parent epic id matches a child's entry. "
    "FIX SHAPE: one shared, installable helper module both scripts import — right-anchored session-name "
    "parsing (last three segments are gate/role/attempt, so work_id = parts[1:-3] joined) and "
    "relative-path archive matching (the existing name==id / endswith('-'+id) rule generalized to N "
    "segments, plus tolerance for a flattened name). Every change is strictly widening: the slashless "
    "case stays byte-identical. "
    "GOVERNING CONSTRAINTS: the fix lives in C:/Programs/constellation-skills (f1Brainz is a consumer "
    "only, needs no source change); the installer must carry the new module as a runtime companion of "
    "both call sites or it silently fails to install in commander/commander-delegated/admiral/explorer — "
    "the documented gauge_reader.py drift — and the existing companion guard test is blind to plain "
    "imports, so it needs widening too. EVIDENCE SURFACE: constellation-skills/tests/, whose current "
    "coverage is slashless-only, which is why this shipped. "
    "OUT OF SCOPE: changing the '<date>-<work-id>' archive naming convention; any f1Brainz source change; "
    "any change to what the engine or the spine templates say.")
eng("release")
