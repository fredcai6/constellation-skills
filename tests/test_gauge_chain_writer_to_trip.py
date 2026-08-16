"""The Context Governor chain, traversed end to end with REAL OS subprocesses:

    gauge WRITER hook -> gauge.json -> gauge_reader.read() -> thresholds_for
    -> the engine's Trip advisory

This is the repo's first test where the record reaching Trip is one the WRITER
actually produced. Every other "real file wiring" test hand-authors the
`gauge.json` it reads, so it carries whatever fill the test author typed -- a
wrong-but-well-formed reading survives all of them. Here the number the engine
renders has to trace character-for-character back to a record a separate OS
process wrote from a real transcript.

Scope of the coverage claim (decision:boundary-is-hook-process-not-harness):
this reaches from the hook's PROCESS ENTRY to a Trip verdict. The harness ->
hook segment (settings.json wiring, CLAUDE_PROJECT_DIR delivery) is an owned
null, tracked elsewhere. Hence `..._chain_writer_to_trip`, not `..._e2e`.

CONTAINMENT IS THE FIRST THING IN THIS FILE, AND IT IS NOT HYGIENE.
`spine_rail.resolve_project_dir()` is literally
`Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())`. An unfenced
subprocess therefore resolves the project dir to the developer's own checkout
and writes the LIVE `.agent-work/.spine-rail-binding.json` -- manufacturing the
exact multi-spine failure this epic exists to investigate, on the investigator.
That has already happened to this repo once (#271). So every subprocess this
file spawns is fenced by `_run_fenced`, which pins BOTH halves of that `or`:
`CLAUDE_PROJECT_DIR` and `cwd`, at a per-test tmpdir. The fence is asserted by
`test_containment_subprocesses_resolve_project_dir_to_the_tmpdir` and by
`test_containment_repo_agent_work_untouched_by_the_chain` -- proven, not
assumed. NEVER relax the fence to make something pass.

One traced record proves the chain is CONNECTED. It cannot prove the chain is
still MEASURING -- a saturated, frozen or dead instrument passes a
single-point test perfectly, returning the same number whatever it is fed. So
section (4) drives the writer once per rung of an ascending token LADDER and
reads the chain back after every write, asserting only that the series is
ordered, that it MOVES, that each rung's Reading is that rung's own, and that
the engine's advisory band ascends through each boundary exactly once.

Sections (1)-(4) all trace a record that EXISTS. Section (5) traces the other
outcome: a run that produces NO reading at all. Silence must never be bare --
"nothing was written" and "something PREVENTED writing" have to stay
distinguishable at the gate boundary, so the writer's own diagnosis of its own
skip has to survive all the way to the text an agent actually reads. That
section is also the first place in this repo where the engine is fed a
`gauge-skip.json` the HOOK really produced: every other test of that sidecar
hand-builds the file it then reads, which can only prove the reader parses what
its own author typed.

NO THRESHOLD VALUES LIVE HERE, including in the fixture and in the ladder. Any
band comes from `thresholds_for`'s returned pair at test time; no numeric
constant expressing acceptable context is typed anywhere in this file. The
ladder's rungs are token counts, not thresholds: nothing asserts which band any
individual rung lands in, only the shape of the whole series.

No conditional skip: `scripts/verify_skip_guard.py` fails the build on an
undocumented skip, and a test that quietly does not run is how a broken
instrument hides. Every test here runs unconditionally.
"""

import importlib.util
import json
import math
import os
import shutil
import subprocess
import sys
from collections import namedtuple
from datetime import datetime, timedelta, timezone
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
_HOOKS_DIR = _REPO_ROOT / "scripts" / "hooks"
_SPINE_RAIL = _HOOKS_DIR / "spine_rail.py"
_GAUGE_WRITER_HOOK = _HOOKS_DIR / "gauge_writer_hook.py"
_ENGINE = _REPO_ROOT / "scripts" / "checklist_engine.py"
_GAUGE_READER = _REPO_ROOT / "scripts" / "gauge_reader.py"
_SPINE_TEMPLATE = (
    _REPO_ROOT / "skills" / "implementer" / "templates" / "IMPLEMENTER_PLAN.template.json"
)

_FIXTURES = Path(__file__).resolve().parent / "fixtures"
_MAINCHAIN_FIXTURE = _FIXTURES / "real_mainchain_transcript.jsonl"
_SUBAGENT_FIXTURE = _FIXTURES / "real_subagent_transcript.jsonl"


def _load(name, path):
    """Explicit file-path module loading -- this repo has no conftest.py and
    adds none; see tests/test_gauge_writer.py and tests/test_gauge_reader.py
    for the same idiom.

    The `sys.modules` registration is not decoration: `gauge_reader` defines a
    `@dataclass`, and `dataclasses` resolves field types through
    `sys.modules[cls.__module__]`. An unregistered module makes that lookup
    `None` and the import blows up at collection time. tests/test_gauge_reader.py
    registers for the same reason.
    """
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


sr = _load("spine_rail", _SPINE_RAIL)
gw = _load("gauge_writer_hook", _GAUGE_WRITER_HOOK)
gr = _load("gauge_reader", _GAUGE_READER)


# --------------------------------------------------------------------------- #
# (1) CONTAINMENT
# --------------------------------------------------------------------------- #

def _subprocess_env(tmp_path):
    """The fence, half one: an EXPLICIT env dict pinning `CLAUDE_PROJECT_DIR`
    at the per-test tmpdir.

    Copied from `os.environ` rather than built from scratch because Windows
    process creation needs the parent's `PATH` and `SYSTEMROOT`; both are
    re-asserted below so a future refactor of the copy cannot silently drop
    them. `PYTHONIOENCODING` keeps the child's UTF-8 I/O deterministic on a
    Windows console codepage.

    An inherited real `CLAUDE_PROJECT_DIR` (this suite runs inside a live
    Claude Code session that sets one) is OVERWRITTEN, never merged -- that
    inherited value points at the developer's own checkout, which is precisely
    what must never be reachable from here.
    """
    env = dict(os.environ)
    env["CLAUDE_PROJECT_DIR"] = str(tmp_path)
    env["PYTHONIOENCODING"] = "utf-8"
    for key in ("PATH", "SYSTEMROOT"):
        inherited = os.environ.get(key)
        if inherited is not None:
            env[key] = inherited
    return env


def _run_fenced(argv, tmp_path, stdin_text=None):
    """The fence, half two: `cwd` also pinned at the tmpdir, because
    `resolve_project_dir()` falls back to `os.getcwd()` when the env var is
    absent -- fencing only one half leaves the other live.

    `subprocess.run` reaps the child before returning and no handle is kept, so
    `tmp_path` cleanup cannot fail on a still-open handle (a real Windows
    failure mode, and CI is windows-latest).
    """
    return subprocess.run(
        argv,
        input=stdin_text,
        capture_output=True,
        text=True,
        env=_subprocess_env(tmp_path),
        cwd=str(tmp_path),
    )


_FENCE_PROBE = (
    "import importlib.util, json, os, sys\n"
    "spec = importlib.util.spec_from_file_location('spine_rail', sys.argv[1])\n"
    "mod = importlib.util.module_from_spec(spec)\n"
    "spec.loader.exec_module(mod)\n"
    "print(json.dumps({'project_dir': str(mod.resolve_project_dir()),\n"
    "                  'cwd': os.getcwd()}))\n"
)


def _snapshot_repo_agent_work():
    """Identity of every file under the REPO ROOT's `.agent-work/`, as
    `{path: (size, mtime_ns)}`. Empty dict when the directory does not exist.

    This is the negative half of the containment proof: not "the fence is
    configured" but "nothing under the live `.agent-work/` moved". A directory
    that does not exist and is not created also compares equal, so the check
    holds in a clean checkout as well as this worktree.
    """
    root = _REPO_ROOT / ".agent-work"
    if not root.exists():
        return {}
    snapshot = {}
    for path in root.rglob("*"):
        try:
            if path.is_file():
                stat = path.stat()
                snapshot[str(path)] = (stat.st_size, stat.st_mtime_ns)
        except OSError:
            # An unreadable entry is recorded by name alone rather than
            # dropped -- its disappearance would still show up as a diff.
            snapshot[str(path)] = None
    return snapshot


def test_containment_subprocesses_resolve_project_dir_to_the_tmpdir(tmp_path):
    """The fence, asserted directly at the mechanism it fences.

    A fresh subprocess launched through `_run_fenced` loads the REAL
    `spine_rail` and reports what `resolve_project_dir()` -- the function every
    binding and gauge write is keyed off -- actually returns. It must be the
    tmpdir, and it must not be the repo root or anything under it.
    """
    proc = _run_fenced(
        [sys.executable, "-c", _FENCE_PROBE, str(_SPINE_RAIL)], tmp_path
    )
    assert proc.returncode == 0, proc.stderr
    seen = json.loads(proc.stdout)
    project_dir = Path(seen["project_dir"]).resolve()
    cwd = Path(seen["cwd"]).resolve()

    assert project_dir == tmp_path.resolve()
    # Both halves of `CLAUDE_PROJECT_DIR or os.getcwd()` are pinned, so
    # dropping either one still leaves the subprocess inside the tmpdir.
    assert cwd == tmp_path.resolve()
    assert project_dir != _REPO_ROOT
    assert _REPO_ROOT not in project_dir.parents


# --------------------------------------------------------------------------- #
# (2) A REAL MAIN-CHAIN TRANSCRIPT CAPTURE
# --------------------------------------------------------------------------- #
#
# The numerator path was previously validated only against
# `golden_transcript.jsonl`, which is hand-built: it proves the writer parses
# the shape its own author imagined, not the shape Claude Code emits
# (decision:capture-real-mainchain-content-stripped).
#
# `real_subagent_transcript.jsonl` cannot serve as that specimen. Every one of
# its lines is `isSidechain: true` -- the ONE shape the writer is required to
# IGNORE -- so pinning a main-chain reader against it can only fail if someone
# ADDS a key, which is vacuous. `test_subagent_fixture_is_all_sidechain...`
# below re-proves that property rather than trusting the claim.
#
# `real_mainchain_transcript.jsonl` is genuinely captured from a live Claude
# Code transcript on a real session and then stripped to ONLY the keys the
# writer reads. `message.content` and every other field are dropped, so no
# conversation text is committed.

# The exact fields `gauge_writer_hook.find_latest_usage` requires. They are
# typed here (not imported) BECAUSE that is the pin: the hook holds them as a
# literal tuple inside a function, so this is an independent statement of the
# contract, not a tautology against the same constant.
_WRITER_REQUIRED_TOP = frozenset({"type", "isSidechain", "timestamp", "message"})
_WRITER_REQUIRED_MESSAGE = frozenset({"model", "usage"})
_WRITER_REQUIRED_USAGE = frozenset({
    "input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens",
})


def _capture_records():
    lines = [
        line for line in
        _MAINCHAIN_FIXTURE.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    return [json.loads(line) for line in lines]


def test_capture_pins_writer_required_fields_as_a_subset_of_the_captured_keys():
    """SUPERSET DIRECTION, deliberately.

    The assertion is `required <= captured`, so it FAILS the day a re-capture
    shows a RENAMED or REMOVED field -- which is the drift that actually breaks
    the writer. The inverse (`captured <= required`) can only fail when someone
    ADDS a key, which breaks nothing and is exactly the vacuous pin a cold
    critic caught on the previous version of this plan.

    A live-format note that argues for this direction: the transcripts these
    records came from are Claude Code `version 2.1.219`, while
    docs/GAUGE_WRITER_HOOK.md records `2.1.214`. The format has already drifted
    once with every required field intact -- so the doc's version string is not
    evidence of anything, and this pin is.
    """
    records = _capture_records()
    assert records, "the capture must not be empty"

    for record in records:
        assert _WRITER_REQUIRED_TOP <= set(record)
        assert _WRITER_REQUIRED_MESSAGE <= set(record["message"])
        assert _WRITER_REQUIRED_USAGE <= set(record["message"]["usage"])

        # main-chain is the whole point of this specimen: the field must be
        # PRESENT and literally false, not merely falsy-by-absence.
        assert record["isSidechain"] is False
        assert record["type"] == "assistant"


def test_capture_carries_no_conversation_content():
    """The committed capture holds ONLY what the writer reads.

    Equality (not subset) in this direction is the privacy guarantee: any key
    beyond the whitelist -- `message.content` above all -- fails the test, so
    conversation text cannot re-enter the fixture through a careless
    re-capture.
    """
    for record in _capture_records():
        assert set(record) == _WRITER_REQUIRED_TOP
        assert set(record["message"]) == _WRITER_REQUIRED_MESSAGE
        assert set(record["message"]["usage"]) == _WRITER_REQUIRED_USAGE
        assert "content" not in record["message"]


def test_real_writer_produces_a_record_from_the_main_chain_capture():
    """The specimen is USABLE, not merely well-shaped.

    `compute_record` is the writer's own numerator path. Against this capture
    it must return a real record and no uncalibrated flag -- i.e. the captured
    model is one the writer has a window for, and the usage fields parse.
    """
    record, uncalibrated = gw.compute_record(str(_MAINCHAIN_FIXTURE))

    assert uncalibrated is None
    assert record is not None
    assert set(record) == set(gr.REQUIRED_FIELDS)
    assert record["model"] == _capture_records()[-1]["message"]["model"]


def test_subagent_fixture_is_all_sidechain_and_yields_no_record():
    """Re-proves the claim this gate's specimen choice rests on, rather than
    inheriting it: every line of the older fixture is a sidechain entry, so the
    writer -- correctly -- finds nothing in it. That is why it cannot be the
    main-chain pin."""
    lines = [
        line for line in
        _SUBAGENT_FIXTURE.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert lines
    assert all(json.loads(line).get("isSidechain") is True for line in lines)

    record, uncalibrated = gw.compute_record(str(_SUBAGENT_FIXTURE))
    assert record is None
    assert uncalibrated is None


# --------------------------------------------------------------------------- #
# (3) THE CHAIN
# --------------------------------------------------------------------------- #

_SESSION_ID = "chain-writer-to-trip-session"
_WORK_ID = "chainwork"


def _fresh_transcript(tmp_path, *, sampled_at, total_tokens=None, model=None):
    """The committed capture, re-stamped at `sampled_at`, written into the fence.

    Only `timestamp` is rewritten (and, for the ladder, the usage totals --
    see below). Every other field is the captured original, because the
    transcript SHAPE is what this chain is testing and rebuilding it by hand
    would reintroduce exactly the hand-authored specimen this gate exists to
    replace.

    The rewrite is necessary, not convenient: `gauge_reader.read()` resolves
    staleness from the record's own `observed_at`, which the writer copies
    straight from the transcript's `timestamp`. A committed capture is stale
    the day after it is taken, so a chain driven off the frozen timestamps
    would prove only that the reader rejects old records. Staling it back is a
    fault injection this gate performs deliberately -- see
    `test_chain_stale_transcript_yields_no_reading`.

    `total_tokens` is the ladder's one input knob. The writer's numerator is
    the SUM of the record's three usage fields, so the total is applied by
    adjusting the bulk field (`cache_read_input_tokens`) and leaving the other
    two at their captured values -- the sum is exactly `total_tokens` while all
    three fields stay live, so a writer that stopped summing one of them still
    reads wrong. It is applied to EVERY record, not just the latest, so the
    rung's fill does not depend on which record the writer happens to select;
    which record it selected is pinned separately and deliberately, by the
    `observed_at` assertion in `_climb_ladder` (only the LAST line carries
    `sampled_at` exactly).

    `model` is section (6)'s one extra knob: it re-stamps the captured records
    with a DIFFERENT model name so the same real transcript shape can be driven
    once per calibrated model. Like `total_tokens` it rewrites a single field
    and leaves the rest of the capture untouched, and like `total_tokens` it is
    applied to EVERY record so the outcome cannot depend on which one the
    writer happens to select.
    """
    records = _capture_records()
    step = timedelta(seconds=1)
    lines = []
    for offset, record in enumerate(reversed(records)):
        stamped = json.loads(json.dumps(record))  # deep copy; never mutate the fixture
        stamped["timestamp"] = (
            (sampled_at - offset * step).isoformat().replace("+00:00", "Z")
        )
        if model is not None:
            stamped["message"]["model"] = model
        if total_tokens is not None:
            usage = stamped["message"]["usage"]
            bulk = (
                total_tokens
                - usage["input_tokens"]
                - usage["cache_creation_input_tokens"]
            )
            # Loud rather than silent: a rung smaller than the capture's own
            # fixed overhead would otherwise write a negative token count and
            # still sum correctly, hiding a nonsense transcript behind a
            # passing assertion.
            assert bulk >= 0, (
                f"rung {total_tokens} is below the captured record's fixed "
                f"usage overhead; raise the rung rather than writing a "
                f"negative token count"
            )
            usage["cache_read_input_tokens"] = bulk
        lines.append(json.dumps(stamped))
    lines.reverse()  # oldest first, latest last -- as a real transcript grows

    path = tmp_path / "transcript.jsonl"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def _spine_tree(tmp_path, work_id):
    """A real `.agent-work/<work_id>/` tree inside the fence, holding a spine.

    The spine is a COPY OF THE REAL VENDORED TEMPLATE, not a hand-built dict.
    A hand-built spine omits `tasks` and the engine raises `KeyError` -- so a
    hand-built one would be testing a shape the engine never actually drives.

    The `.agent-work/<work_id>/` shape is not decoration either: the writer's
    own `_is_contained` refuses any candidate whose grandparent directory is
    not named `.agent-work`, so a tree built anywhere else would be dropped
    before the writer ever reached the branch under test.
    """
    work = tmp_path / ".agent-work" / work_id
    work.mkdir(parents=True, exist_ok=True)

    spine = work / "spine.json"
    spine.write_text(_SPINE_TEMPLATE.read_text(encoding="utf-8"), encoding="utf-8")
    return spine


def _work_tree(tmp_path, *, bind_to=None):
    """`_spine_tree` plus a binding from `_SESSION_ID` to exactly one spine.

    The binding is written by the REAL `spine_rail.save_binding`, never by
    hand-authored JSON: the binding format is a live coupling between two
    hooks, and hand-authoring it would pin this test to a format the writer no
    longer reads. `project_dir` is passed EXPLICITLY as `tmp_path`, so this
    in-process call is fenced by argument, the same way the subprocesses are
    fenced by env + cwd.

    `bind_to` repoints the binding at some other spine path (the fault
    injection in `test_chain_binding_pointing_elsewhere_writes_no_gauge`);
    by default the binding names this tree's own spine.

    `engine_session` is the ENGINE LEASE NAME the binding entry carries, and
    since #600 it is what NAMES the gauge file the writer produces. It is None
    here, and that is a deliberate fixture choice rather than an omission: this
    spine is never claimed, so the engine that reads it at the far end of the
    chain HAS NO LEASE and therefore no owner either. Binding a lease name to a
    spine nobody claimed would make the writer produce `gauge-<owner>.json`
    while the leaseless engine read `gauge.json` -- a mismatch invented by the
    fixture, not one production can reach, since the entry's `engine_session`
    is parsed from the very `claim --session-id` that creates the lease. Both
    ends unowned IS a real configuration (the live binding store carries
    `engine_session: null` entries right now) and it is exactly R3's path, so
    these tests now pin the LEASELESS chain end to end. The OWNED chain is
    pinned separately, by
    `test_chain_owner_keyed_reading_reaches_the_leased_engine` below.
    """
    spine = _spine_tree(tmp_path, _WORK_ID)

    bound = Path(bind_to) if bind_to is not None else spine
    sr.save_binding(tmp_path, {
        _SESSION_ID: {
            str(bound.resolve()): {
                "spine": str(bound.resolve()),
                "engine_session": None,
                "worktree": str(tmp_path),
                "claimed_at": datetime.now(timezone.utc).isoformat(),
            }
        }
    })
    return spine


def _run_writer_hook(tmp_path, transcript_path, session_id=_SESSION_ID, *,
                     hook=_GAUGE_WRITER_HOOK):
    """The WRITER, as a genuine fresh OS process -- never an in-process call.

    decision:verify-by-fresh-process. An in-process call would inherit this
    interpreter's imports, cwd, and env, so it could pass while the real hook
    (which the harness spawns cold, with only a stdin payload and an env var to
    orient it) fails. The payload is exactly what Claude Code delivers on
    PostToolUse: a session id and a transcript path.

    `session_id` is a parameter only so section (5) can drive the SAME writer
    under its own distinct id; every caller in sections (1)-(4) keeps the
    default and is unchanged.

    `hook` is section (7)'s knob: it points the SAME invocation at a different
    copy of the writer. It defaults to the shipped hook, so nothing outside
    section (7) changes, and the fence applies identically either way.
    """
    payload = json.dumps({
        "session_id": session_id,
        "transcript_path": str(transcript_path),
    })
    return _run_fenced(
        [sys.executable, str(hook)], tmp_path, stdin_text=payload
    )


def _run_engine_current(tmp_path, spine, *, engine=_ENGINE):
    """The ENGINE, as a genuine fresh OS process, on the read-only verb that
    carries the Trip advisory. `current` never persists, so this cannot mutate
    the spine it reads.

    `engine` is section (7)'s knob, exactly like `_run_writer_hook`'s `hook`:
    it points the same invocation at a different copy of the engine, and
    defaults to the shipped one."""
    return _run_fenced(
        [sys.executable, str(engine), "--file", str(spine), "current"], tmp_path
    )


def test_chain_writer_process_to_trip_advisory(tmp_path):
    """THE GATE: one record, produced by the writer PROCESS, traced all the way
    to the number the engine renders at a gate boundary.

    Every link is the real component: the real transcript shape, the real
    binding writer, the writer hook as a cold subprocess, the real reader, the
    real threshold table, the real engine CLI. Nothing in this test hands the
    downstream stage the value the upstream stage was supposed to produce --
    which is the exact hole this gate closes, since every prior "real file
    wiring" test hand-authors the gauge.json it reads.
    """
    sampled_at = datetime.now(timezone.utc)
    transcript = _fresh_transcript(tmp_path, sampled_at=sampled_at)
    spine = _work_tree(tmp_path)
    gauge = spine.parent / "gauge.json"

    # --- writer, as a fresh process -----------------------------------------
    proc = _run_writer_hook(tmp_path, transcript)

    # FAIL-OPEN, proven at the real process boundary rather than asserted of a
    # function's return value: the hook must exit clean and say NOTHING on
    # stdout, because anything it prints is interpreted by the harness as hook
    # output and anything non-zero can disturb the tool call it rides on.
    assert proc.returncode == 0, proc.stderr
    assert proc.stdout == ""

    assert gauge.exists(), f"the writer process wrote no gauge.json (stderr: {proc.stderr})"
    written = json.loads(gauge.read_text(encoding="utf-8"))

    # The record is FROZEN at exactly four fields, and the reader's own
    # REQUIRED_FIELDS is the statement of that contract -- so this compares the
    # writer's actual output against the reader's actual expectation, with no
    # third hand-typed list in the middle to drift from either.
    assert set(written) == set(gr.REQUIRED_FIELDS)

    # --- reader ---------------------------------------------------------------
    # ONE assertion carries four properties at once: `read()` returns a Reading
    # only when the record is fresh, well-formed, in-range AND calibrated. Any
    # of those failing collapses to None by construction.
    reading = gr.read(gauge)
    assert reading is not None
    assert reading.model == written["model"]
    assert reading.fill_fraction == written["fill_fraction"]

    # --- thresholds -----------------------------------------------------------
    # Derived at test time from the real table. NO numeric bound is typed here
    # or anywhere in this file (decision:no-threshold-values) -- and this is a
    # FIXTURE-VALIDITY guard, not a correctness claim about the engine's
    # banding. The band assertion itself belongs to g2, where a ladder makes it
    # strictly stronger; re-implementing the engine's own comparison here could
    # not fail unless the engine's branch structure changed.
    soft, hard = gr.thresholds_for(reading.model)
    assert soft <= reading.fill_fraction, (
        "the committed capture no longer reads at or above the soft band, so "
        "the engine renders no advisory and this chain has nothing to trace; "
        "re-capture a busier main-chain sample rather than weakening the test"
    )

    # --- Trip, via the real engine CLI as a fresh process ---------------------
    engine = _run_engine_current(tmp_path, spine)
    assert engine.returncode == 0, engine.stderr

    # CHARACTER-FOR-CHARACTER. The engine renders `{fill:.0%}`; the fill it
    # formats must be the one THIS writer process computed, so the expected
    # string is built from the bytes on disk, not from a literal.
    rendered = "CONTEXT {:.0%}".format(written["fill_fraction"])
    assert rendered in engine.stdout, (
        f"expected {rendered!r} traced from the writer's own record; "
        f"engine said:\n{engine.stdout}\n{engine.stderr}"
    )


def test_containment_repo_agent_work_untouched_by_the_chain(tmp_path):
    """The negative half of the containment proof, run against the WHOLE chain.

    Not "the fence is configured" but "nothing under the live `.agent-work/`
    moved" -- the failure this guards against is silent corruption of a real
    binding file, which no amount of passing assertions elsewhere would reveal.
    Sizes and mtimes are compared, so an in-place rewrite of identical length
    is still caught.
    """
    before = _snapshot_repo_agent_work()

    transcript = _fresh_transcript(tmp_path, sampled_at=datetime.now(timezone.utc))
    spine = _work_tree(tmp_path)
    _run_writer_hook(tmp_path, transcript)
    _run_engine_current(tmp_path, spine)

    assert _snapshot_repo_agent_work() == before

    # And the artefacts the chain DID produce all live inside the fence.
    assert (spine.parent / "gauge.json").exists()
    assert sr.binding_path(tmp_path).exists()
    assert tmp_path in sr.binding_path(tmp_path).resolve().parents


def test_chain_binding_pointing_elsewhere_writes_no_gauge(tmp_path):
    """Repointing the binding at a different spine breaks the chain at the
    session -> spine link, and the writer skips rather than guessing.

    This is the standing, committed form of one of this gate's fault
    injections: it proves the gauge.json the chain test reads is genuinely
    located through the binding, not found by luck.

    THE POSITIVE CONTROL AT THE END IS LOAD-BEARING, not tidiness. Every
    assertion in the negative half is satisfied by a writer that never ran at
    all: a hook that crashed before doing anything also exits 0-ish-looking,
    prints nothing, and leaves no gauge.json. So the negative direction alone
    proves nothing about the binding. Rebinding correctly and re-running the
    SAME writer against the SAME transcript in the SAME tmpdir isolates the
    binding as the only variable -- the gauge's absence above is then
    attributable to the repointed binding and to nothing else.
    """
    transcript = _fresh_transcript(tmp_path, sampled_at=datetime.now(timezone.utc))
    elsewhere = tmp_path / ".agent-work" / "someone-elses-work" / "spine.json"
    elsewhere.parent.mkdir(parents=True, exist_ok=True)
    spine = _work_tree(tmp_path, bind_to=elsewhere)

    proc = _run_writer_hook(tmp_path, transcript)

    assert proc.returncode == 0, proc.stderr
    assert proc.stdout == ""
    assert not (spine.parent / "gauge.json").exists()

    # --- positive control: same writer, same transcript, correct binding ----
    _work_tree(tmp_path)  # rewrites the binding back onto this tree's own spine
    control = _run_writer_hook(tmp_path, transcript)

    assert control.returncode == 0, control.stderr
    assert (spine.parent / "gauge.json").exists(), (
        "the writer produced no gauge.json even with a CORRECT binding, so the "
        "absence asserted above is not evidence about the binding at all -- "
        f"writer stderr: {control.stderr}"
    )


def test_chain_stale_transcript_yields_no_reading(tmp_path):
    """A transcript sampled long ago produces a gauge record the reader
    REFUSES, so no advisory is rendered.

    The staleness offset is derived from the reader's own `DEFAULT_MAX_AGE`,
    not typed -- the same discipline the threshold constraint imposes. This is
    the committed form of the third fault injection, and it proves the chain's
    freshness link is real: the writer still writes, but nothing downstream
    trusts it.
    """
    stale_at = datetime.now(timezone.utc) - (gr.DEFAULT_MAX_AGE * 2)
    transcript = _fresh_transcript(tmp_path, sampled_at=stale_at)
    spine = _work_tree(tmp_path)
    gauge = spine.parent / "gauge.json"

    proc = _run_writer_hook(tmp_path, transcript)
    assert proc.returncode == 0, proc.stderr
    assert gauge.exists()  # the WRITER is untroubled by age; the READER judges it

    assert gr.read(gauge) is None

    engine = _run_engine_current(tmp_path, spine)
    assert engine.returncode == 0, engine.stderr
    assert "CONTEXT {:.0%}".format(
        json.loads(gauge.read_text(encoding="utf-8"))["fill_fraction"]
    ) not in engine.stdout


# --------------------------------------------------------------------------- #
# (4) THE LADDER -- is the instrument still MEASURING?
# --------------------------------------------------------------------------- #
#
# The chain test above proves ONE record traces end to end. One point cannot
# distinguish a working gauge from a saturated, frozen, or dead one: a chain
# that returns the same number for every input passes a single-point test
# perfectly. So the writer is driven ONCE PER RUNG of an ascending token
# ladder, each rung a fresh transcript with its own fresh `observed_at`, and
# the on-disk `gauge.json` is read back through the real `gauge_reader.read()`
# after every write.
#
# Nothing here asserts a NUMBER. Every assertion is on the ORDERING of the
# series and on the fact that it moves (decision:no-threshold-values holds
# across this whole file, fixture included). No history artefact and no schema
# change are involved either (decision:ladder-over-history): the record stays
# exactly four fields and the distribution lives in the repeated driving, not
# in a persisted sidecar.

_LADDER_TOKENS = (
    # ORDINARY RUNGS -- arbitrary ascending token counts, deliberately NOT
    # derived from MODEL_WINDOWS and deliberately not chosen to sit at any
    # threshold. Nothing is asserted about which band any individual rung
    # lands in; only the shape of the whole series is.
    9_000,
    45_000,
    96_000,
    132_000,
    210_000,
    640_000,
    # THE SATURATING TOP RUNG -- and here the carve-out, which is load-bearing.
    # This one IS derived from MODEL_WINDOWS, because the window is the
    # structural boundary of the writer's own clamp
    # (`fill = max(0.0, min(1.0, total_tokens / window))`), not a statement
    # about how full is acceptable. One token past the widest window saturates
    # the clamp for EVERY calibrated model, permanently.
    #
    # A typed magnitude here would look identical today and rot invisibly: the
    # day a wider-window model is added it would stop saturating anything, and
    # the "not all identical" assertion below would STILL PASS, because the
    # lower rungs keep moving. The rung would silently degrade into a no-op --
    # precisely the class of defect this whole file exists to catch.
    max(gw.MODEL_WINDOWS.values()) + 1,
)

# One observation of the whole chain at one rung.
_Rung = namedtuple("_Rung", "total_tokens sampled_at reading band")

# The engine's own BRANCH MARKERS, which is the only externally visible thing
# that distinguishes the two advisory bands: `_trip_advisory` renders the same
# `CONTEXT {fill:.0%}` prefix on BOTH the `>= hard` and the `>= soft` branch,
# so classifying on the prefix would see one band where there are two. These
# are branch labels, not thresholds -- no acceptable-context value is named.
_HARD_MARKER = "(>= hard)"
_SOFT_MARKER = "(>= soft)"

_BAND_NONE = "no-advisory"
_BAND_SOFT = "soft"
_BAND_HARD = "hard"

# The order the bands must appear in as context fills. A statement of INTENT,
# not a recomputation: nothing here consults `thresholds_for`, so this cannot
# quietly agree with an engine that has its comparison backwards.
_ASCENDING_BANDS = (_BAND_NONE, _BAND_SOFT, _BAND_HARD)


def _band_of(engine_stdout):
    """Classify the engine's ACTUAL advisory output into one of three bands.

    Read off the real rendered text, never recomputed -- the whole point of
    assertion (d) is to observe the engine's own branching from outside it.
    """
    hard = _HARD_MARKER in engine_stdout
    soft = _SOFT_MARKER in engine_stdout

    assert not (hard and soft), (
        f"the engine rendered BOTH band markers at once, so its branches are "
        f"no longer mutually exclusive:\n{engine_stdout}"
    )
    if hard:
        return _BAND_HARD
    if soft:
        return _BAND_SOFT
    # A CONTEXT line with neither marker means a band was rendered that this
    # classifier cannot see -- silently calling that "no advisory" would let
    # the ordering assertion below pass over a band it never actually
    # observed.
    assert "CONTEXT " not in engine_stdout, (
        f"the engine rendered a CONTEXT advisory carrying neither band "
        f"marker; the classifier is blind to it:\n{engine_stdout}"
    )
    return _BAND_NONE


def _ladder_stamps(count):
    """A distinct, ascending, all-FRESH sampling moment per rung.

    Distinct is the point: a rung whose Reading carries the PREVIOUS rung's
    `observed_at` is a rung the reader never actually re-read. All of them stay
    within the reader's freshness horizon (they run backwards from `now` by
    seconds), so nothing here is accidentally testing staleness -- that is
    `test_chain_stale_transcript_yields_no_reading`'s job.
    """
    now = datetime.now(timezone.utc)
    step = timedelta(seconds=5)
    return [now - (count - 1 - index) * step for index in range(count)]


def _climb_ladder(tmp_path):
    """Drive the REAL writer process once per ascending rung, reading the chain
    back after each write. Returns one `_Rung` per rung, in ascending order.

    Every subprocess goes through `_run_fenced`; the fence is never relaxed for
    the ladder, which spawns more processes than anything else in this file and
    is therefore the single largest containment exposure here.

    ASSERTION (c) LIVES HERE, per rung, on purpose: each Reading must carry
    THIS rung's own `observed_at`. That is what makes every series-level
    assertion downstream trustworthy -- without it, a writer that silently
    stopped writing would leave the previous rung's file on disk and the
    reader would happily return a stale Reading, so the series could look
    perfectly well-ordered while measuring nothing at all.
    """
    spine = _work_tree(tmp_path)
    gauge = spine.parent / "gauge.json"
    stamps = _ladder_stamps(len(_LADDER_TOKENS))

    rungs = []
    for total_tokens, sampled_at in zip(_LADDER_TOKENS, stamps):
        transcript = _fresh_transcript(
            tmp_path, sampled_at=sampled_at, total_tokens=total_tokens
        )
        proc = _run_writer_hook(tmp_path, transcript)
        assert proc.returncode == 0, proc.stderr
        assert proc.stdout == ""

        reading = gr.read(gauge)
        assert reading is not None, (
            f"rung {total_tokens}: the chain produced no Reading "
            f"(gauge.json present: {gauge.exists()}; writer stderr: {proc.stderr})"
        )
        # (c) -- this rung's OWN sampled moment, not the last one's.
        assert reading.observed_at == sampled_at, (
            f"rung {total_tokens}: the Reading carries {reading.observed_at}, "
            f"not this rung's {sampled_at} -- the reader saw a leftover record, "
            f"so nothing downstream of here is measuring this rung"
        )

        # The advisory the ENGINE actually renders for this rung, from a fresh
        # process on the read-only verb -- the same real CLI the chain test
        # uses, so the band is observed at the surface an agent really sees.
        engine = _run_engine_current(tmp_path, spine)
        assert engine.returncode == 0, engine.stderr

        rungs.append(_Rung(total_tokens, sampled_at, reading, _band_of(engine.stdout)))

    return rungs


def test_ladder_fill_series_is_non_decreasing_and_actually_moves(tmp_path):
    """(a) + (b): the instrument tracks its input, and it is not stuck.

    (a) ascending tokens must never produce a LOWER fill -- an inverted or
    scrambled numerator shows up here immediately.

    (b) is the one that catches the failure this issue is named for: a chain
    whose output does not move when its input does is saturated, frozen, or
    dead, not measuring. A wrong ratio is caught by (b) BEFORE it saturates --
    while the reading is still a plausible-looking number that simply never
    changes.

    Neither assertion names a value. `sorted` and `set` are the entire
    vocabulary; no bound on acceptable context is expressed or implied.
    """
    fills = [rung.reading.fill_fraction for rung in _climb_ladder(tmp_path)]

    assert fills == sorted(fills), (
        f"ascending token counts produced a non-monotonic fill series: {fills}"
    )
    assert len(set(fills)) > 1, (
        f"every rung of an ascending ladder read the SAME fill ({fills[0]}) -- "
        f"the chain is saturated, frozen or dead, not measuring"
    )


def test_ladder_band_ordering_crosses_each_boundary_exactly_once(tmp_path):
    """(d) BAND ORDERING: as context fills, the engine's advisory must go
    no-advisory -> SOFT -> HARD, each boundary crossed exactly once, never
    regressing.

    This is deliberately NOT "the band matches what I recompute from
    `thresholds_for`". That comparison re-implements `_trip_advisory`'s own
    body, so it agrees with the engine by construction and cannot fail unless
    the engine's branch STRUCTURE changes -- it would happily bless an
    inverted comparison, because the recomputation would be inverted too.

    Collapsing the observed sequence to its runs and demanding it equal the
    ascending order carries four properties in one equality:

      * every band FIRES at least once -- a threshold table in which some band
        can never be reached shortens the collapsed sequence;
      * each boundary is crossed EXACTLY ONCE -- a repeat leaves a duplicate
        run behind;
      * the band never REGRESSES -- going back down leaves the runs out of
        order;
      * soft and hard are not SWAPPED -- an inverted comparison, or a
        `thresholds_for` returning its pair the wrong way round, reverses the
        sequence.

    No value is named anywhere; the rungs know nothing about the thresholds
    and the thresholds are never read.
    """
    bands = [rung.band for rung in _climb_ladder(tmp_path)]

    collapsed = tuple(
        band for index, band in enumerate(bands)
        if index == 0 or band != bands[index - 1]
    )
    assert collapsed == _ASCENDING_BANDS, (
        f"the advisory band sequence across an ascending ladder was {bands}, "
        f"which collapses to {collapsed}; expected exactly {_ASCENDING_BANDS}"
    )


# --------------------------------------------------------------------------- #
# (5) ZERO RECORDS -- is the silence still LOCALIZED?
# --------------------------------------------------------------------------- #
#
# Everything above traces a record that EXISTS. The chain's other outcome is a
# run that writes NO reading at all, and that outcome has its own contract: a
# run producing no reading must stay distinguishable from a run with nothing to
# report. Bare silence collapses the two, and a governor that has gone quiet
# for a reason it already knows is indistinguishable from one that is simply
# idle -- which is how a miscalibration survives unnoticed.
#
# The cause staged here is the real one this epic is investigating: ONE session
# id bound to MORE THAN ONE spine. `resolve_gauge_path` then returns several
# candidates, and `handle_post_tool_use` cannot tell which spine the latest
# usage record belongs to. It refuses to guess -- no gauge.json to any of them
# (decision:gauge-write-skips-on-multiple-bindings) -- but it does know exactly
# WHY it refused, so it fans a `gauge-skip.json` out to EVERY candidate
# (decision:skip-sidecar-fanout-and-clear). A diagnostic fact about the
# writer's own decision is shared by all N candidates and, unlike a reading, is
# never a fabricated or misattributed value, which is what makes fan-out safe
# here and unsafe for gauge.json.
#
# THE SIDECAR UNDER ASSERTION IS PRODUCED BY THE WRITER PROCESS, NEVER BY THIS
# TEST (decision:sidecar-is-half-the-chain). Every other test in this repo that
# feeds the engine a gauge-skip.json hand-builds it, so it can only prove the
# reader parses what its own author typed -- the same hole section (2) closed
# for gauge.json. Nothing below writes a sidecar; deleting the writer call must
# take these tests RED rather than leaving them passing on a file the test
# itself wrote.
#
# assert-don't-repair: the ambiguous binding, the fan-out, and the parent
# directories `_atomic_write_json` creates on the way (#287) are the SHIPPED
# behaviour under test. This section states what the code does. It does not
# improve it.
#
# CONTAINMENT IS AT ITS MOST DANGEROUS HERE, because this section deliberately
# MANUFACTURES the multi-spine binding the file's opening docstring warns
# about. Unfenced it would write the developer's live
# `.agent-work/.spine-rail-binding.json` and reproduce the very failure this
# epic exists to investigate, on the investigator. So the binding is written
# through `save_binding` with `project_dir` passed EXPLICITLY as `tmp_path`,
# every subprocess goes through `_run_fenced` unrelaxed, and
# `test_chain_ambiguous_binding_writes_no_gauge_and_flags_every_candidate`
# re-asserts `_snapshot_repo_agent_work()` equality around the manufactured
# ambiguity itself rather than trusting the file-level containment tests.

# A session id used NOWHERE else, deliberately: it makes "did this test's
# binding escape into a real checkout?" answerable by a single grep for this
# one string, with no risk of matching section (3)'s traffic.
_AMBIGUOUS_SESSION_ID = "chain-ambiguous-binding-session"

# Three candidates, matching the live capture this gate was cut from
# (.agent-work/governor-264/evidence/binding-at-264-dispatch.json). The COUNT
# is a fixture choice, not a bound -- nothing below compares it to a limit; the
# cardinality assertions all read it back from `len(spines)`.
_AMBIGUOUS_WORK_IDS = ("ambiguous-work-a", "ambiguous-work-b", "ambiguous-work-c")


def _bind_session_to(tmp_path, spines):
    """Bind `_AMBIGUOUS_SESSION_ID` to EXACTLY the given spines, through the
    real `spine_rail.save_binding`.

    Same discipline as `_work_tree`: the nested `session_id -> {abs_spine_path:
    entry}` shape is a live coupling between two hooks, so it is produced by
    the shipped writer rather than hand-authored here -- a hand-built map would
    pin this test to a format `load_binding` may already have stopped reading.
    Keying by the RESOLVED ABSOLUTE spine path is what lets one session id hold
    several bindings at once (decision:key-binding-by-spine-path-not-worktree-
    or-cwd), which is the whole condition under test.

    `project_dir` is `tmp_path`: this in-process call is fenced BY ARGUMENT,
    the way the subprocesses are fenced by env + cwd. Passing anything else
    here writes a real checkout's binding file.
    """
    sr.save_binding(tmp_path, {
        _AMBIGUOUS_SESSION_ID: {
            str(spine.resolve()): {
                "spine": str(spine.resolve()),
                # None for the same reason `_work_tree` binds None (#600): none
                # of these spines is ever claimed, so none of them has an owner
                # at the reading end either. It also keeps this the HARDEST
                # version of the ambiguity: unowned candidates are precisely the
                # ones the writer still cannot attribute, so the skip under test
                # is reached by the cause it names rather than by a distinct-
                # owners shortcut.
                "engine_session": None,
                "worktree": str(tmp_path),
                "claimed_at": datetime.now(timezone.utc).isoformat(),
            }
            for spine in spines
        }
    })


def _ambiguous_work_trees(tmp_path):
    """N real spine trees inside the fence, ALL bound to one session id."""
    spines = [_spine_tree(tmp_path, work_id) for work_id in _AMBIGUOUS_WORK_IDS]
    _bind_session_to(tmp_path, spines)
    return spines


def _hook_written_skip(spine):
    """The `gauge-skip.json` sitting beside this spine's gauge path, read back
    through the REAL `gauge_reader.skip_reason`.

    Deliberately the reader's own parser rather than a `json.loads` here: it is
    the consumer the engine actually calls, so this asserts the sidecar is
    legible to the code that has to act on it, not merely well-formed JSON.
    `skip_reason` fails safe to None on absent/corrupt/malformed input, so a
    missing or unparseable sidecar arrives as None rather than an exception.
    """
    return gr.skip_reason(spine.parent / "gauge.json")


def test_chain_ambiguous_binding_writes_no_gauge_and_flags_every_candidate(tmp_path):
    """THE ZERO-RECORDS GATE: a run that produces no reading, and says so.

    The transcript here is the SAME live capture every other test in this file
    drives, freshly stamped -- so the writer had a perfectly usable record to
    report. Nothing about the input is empty. Only the session -> spine binding
    is ambiguous, and that alone is what suppresses the reading; the positive
    control at the end proves it by rebinding and getting a gauge.json out of
    the identical writer, transcript, tmpdir and session id.
    """
    before = _snapshot_repo_agent_work()

    spines = _ambiguous_work_trees(tmp_path)
    transcript = _fresh_transcript(tmp_path, sampled_at=datetime.now(timezone.utc))

    # The instant before the writer starts. Every sidecar's own `observed_at`
    # must land at or after this, which is what makes the files below THIS
    # RUN's output rather than anything left lying around.
    launched_at = datetime.now(timezone.utc)
    proc = _run_writer_hook(tmp_path, transcript, session_id=_AMBIGUOUS_SESSION_ID)

    # (1) FAIL-OPEN, at the real process boundary. A skip is a normal outcome,
    # not an error: the hook rides a live tool call, so a non-zero exit or any
    # stdout chatter would disturb the call it is attached to.
    # decision:fail-open-is-inviolable.
    assert proc.returncode == 0, proc.stderr
    assert proc.stdout == ""

    # (2) NO reading anywhere. Not "not at the one we looked at" -- at NONE of
    # them, which is the actual contract: writing to any single candidate would
    # be a guess, and writing to all of them would spread one agent's reading
    # across unrelated spines.
    for spine in spines:
        assert not (spine.parent / "gauge.json").exists(), (
            f"the writer wrote a reading to {spine.parent} despite not knowing "
            f"which of {len(spines)} bound spines it belonged to"
        )

    # (3) ...but the silence is FLAGGED, at every candidate, by the hook.
    flags = []
    for spine in spines:
        info = _hook_written_skip(spine)
        assert info is not None, (
            f"no readable gauge-skip.json beside {spine.parent}; the writer "
            f"skipped silently instead of localizing the cause "
            f"(writer stderr: {proc.stderr})"
        )
        assert info["reason"] == "ambiguous-binding"

        # The cardinality the HOOK observed, carried through to the reader.
        # This is a count the writer emits, not a bound anyone imposes:
        # nothing here compares it to a limit, only to the number of spines
        # this fixture actually bound.
        assert info["candidate_count"] == len(spines)

        # Produced by THIS run. Without this a leftover sidecar from any
        # earlier write would satisfy every assertion above.
        assert info["observed_at"] >= launched_at, (
            f"the sidecar beside {spine.parent} is stamped "
            f"{info['observed_at']}, before this writer run started at "
            f"{launched_at} -- it is a leftover, not this run's output"
        )
        flags.append(info)

    # ONE EVENT, one timestamp. The hook computes a single `now` and stamps
    # every candidate with it, so N identical stamps is a signature only the
    # real fan-out produces -- N separate writes (or N hand-authored files)
    # would drift apart.
    assert len({info["observed_at"] for info in flags}) == 1, (
        f"the candidates carry different observed_at values ({flags}), so they "
        f"were not written as one fan-out of a single ambiguity event"
    )

    # CONTAINMENT, re-asserted around the manufactured ambiguity itself. This
    # is the one test in the file that deliberately builds the multi-spine
    # binding, so it does not inherit the file-level containment proof -- it
    # restates it locally, and shows the binding it DID write lives in the
    # fence.
    assert _snapshot_repo_agent_work() == before
    assert tmp_path in sr.binding_path(tmp_path).resolve().parents

    # --- positive control: same writer, same transcript, ONE candidate ------
    # Load-bearing, exactly as in
    # `test_chain_binding_pointing_elsewhere_writes_no_gauge`: every assertion
    # above is also satisfied by a writer that died on startup. Rebinding the
    # SAME session id to ONE of the SAME spines and re-running the SAME writer
    # over the SAME transcript leaves cardinality as the only variable, so the
    # absence of a reading above is attributable to the ambiguity and to
    # nothing else.
    _bind_session_to(tmp_path, spines[:1])
    control = _run_writer_hook(tmp_path, transcript, session_id=_AMBIGUOUS_SESSION_ID)

    assert control.returncode == 0, control.stderr
    assert (spines[0].parent / "gauge.json").exists(), (
        "the writer produced no gauge.json even with an UNAMBIGUOUS binding "
        "over this same transcript, so the absence asserted above is not "
        f"evidence about the binding at all -- writer stderr: {control.stderr}"
    )


def test_chain_ambiguous_binding_silence_is_surfaced_by_the_engine(tmp_path):
    """The far end of the zero-records chain: the engine SAYS the gauge is
    silent, and says why, instead of rendering nothing.

    This is the first test in the repo to hand the engine a `gauge-skip.json`
    it did not write itself -- the file the engine reads here came out of the
    writer subprocess a few lines above.

    The comparison is against a spine with NO sidecar, driven through the same
    CLI in the same tmpdir. That contrast IS the protected intent: a gate
    boundary where a reading was PREVENTED must not read like one where there
    was simply nothing to report.
    """
    spines = _ambiguous_work_trees(tmp_path)
    # Not bound to the session, so the writer never touches it: this is what
    # ordinary "nothing to report" silence looks like at a gate boundary.
    unflagged = _spine_tree(tmp_path, "unflagged-work")
    transcript = _fresh_transcript(tmp_path, sampled_at=datetime.now(timezone.utc))

    proc = _run_writer_hook(tmp_path, transcript, session_id=_AMBIGUOUS_SESSION_ID)
    assert proc.returncode == 0, proc.stderr

    flagged = spines[0]
    info = _hook_written_skip(flagged)
    assert info is not None, f"the writer wrote no sidecar to flag (stderr: {proc.stderr})"

    # The two sidecars that would MASK this one are absent, so what the engine
    # renders below is attributable to the skip flag alone. `_no_reading_advisory`
    # dispatches uncalibrated -> skip-reason -> stale-record and returns the
    # FIRST non-empty result, and the whole dispatcher is only reached when
    # `_read_gauge` returns None -- so a fresh gauge.json here would hide the
    # skip flag entirely (#286, not this gate's to fix).
    assert not (flagged.parent / "gauge.json").exists()
    assert not (flagged.parent / gw.UNCALIBRATED_FILENAME).exists()

    engine = _run_engine_current(tmp_path, flagged)
    assert engine.returncode == 0, engine.stderr

    # The engine speaks up at all...
    assert "CONTEXT GAUGE SILENT" in engine.stdout, (
        f"the engine rendered bare silence over a hook-produced "
        f"gauge-skip.json:\n{engine.stdout}\n{engine.stderr}"
    )

    # ...and the CARDINALITY it reports is traced character-for-character back
    # through the reader to the number the writer process itself observed --
    # built from the sidecar on disk, never from a literal, the same way
    # section (3) traces the rendered fill.
    rendered = "{} candidate spines".format(info["candidate_count"])
    assert rendered in engine.stdout, (
        f"expected {rendered!r}, traced from the sidecar the writer wrote; "
        f"engine said:\n{engine.stdout}"
    )

    # No reading was written, so no reading may be rendered. Without this the
    # test would pass just as happily over an engine that invented a number.
    assert "CONTEXT " not in engine.stdout.replace("CONTEXT GAUGE SILENT", "")

    # --- the contrast that makes the silence MEAN something -----------------
    # Same CLI, same tmpdir, same spine template -- only the sidecar differs.
    # If this spine also announced a silent gauge, the announcement above would
    # be noise the engine emits everywhere rather than a localized diagnosis.
    quiet = _run_engine_current(tmp_path, unflagged)
    assert quiet.returncode == 0, quiet.stderr
    assert _hook_written_skip(unflagged) is None
    assert "CONTEXT GAUGE SILENT" not in quiet.stdout, (
        f"a spine the writer never flagged announces a silent gauge too, so "
        f"the announcement distinguishes nothing:\n{quiet.stdout}"
    )


# --------------------------------------------------------------------------- #
# (6) THE CLAMP -- what `gauge_reader.FILL_CEILING` is actually pinned to
# --------------------------------------------------------------------------- #
#
# `FILL_CEILING` is a TYPED LITERAL on the reader's side and this file is the
# only place that can honestly say so. The reader must not import
# `gauge_writer_hook` -- it ships bundled into every install while the
# harness-specific hook does not, and that portability seam is the whole reason
# the gauge is a file format rather than a function call. So the reader cannot
# reach the clamp it is mirroring, and the constant cannot be derived.
#
# What it CAN be is a DRIFT PIN: exactly the bargain `ModelTableSyncTests`
# already makes between `_PROFILES` and `MODEL_WINDOWS`. Only the TEST imports
# both modules, and it obtains the ceiling by EXECUTING the writer rather than
# by reading the writer's source or re-typing its bound. If someone changes the
# clamp, this goes red; nothing else in the repo would notice.
#
# It also closes g2's review triage tc1: the ladder's saturating top rung is
# currently DRIVEN but its result is never OBSERVED, so nothing today asserts
# that saturating actually saturates.

# The same magnitude the ladder's top rung uses, reused rather than re-derived
# -- one token past the widest calibrated window, which saturates the clamp for
# EVERY model in the table permanently (see `_LADDER_TOKENS`' carve-out for why
# this one magnitude is derived from MODEL_WINDOWS while the ordinary rungs are
# not). Reusing it means a wider-window model cannot make this test stop
# saturating without making the ladder stop saturating too.
_SATURATING_TOKENS = _LADDER_TOKENS[-1]


def test_writer_clamp_saturates_at_the_readers_fill_ceiling(tmp_path):
    """FILL_CEILING, obtained by EXECUTION rather than by re-typing.

    Iterates `MODEL_WINDOWS` BY KEY and never reads a value out of it into an
    assertion: computing an expected fill from the same table the writer
    divides by would re-implement `compute_record` and agree with it by
    construction. The only inputs are the model names and one saturating token
    count; the only outputs asserted are that all the fills AGREE and that what
    they agree on is the reader's constant.

    Both assertions are load-bearing and neither implies the other. A writer
    that clamped per-model to something window-dependent would still be
    self-consistent for one model but would fail the agreement check; a writer
    that clamped every model to the same WRONG value would pass agreement and
    fail the ceiling check.
    """
    fills = {}
    for model in gw.MODEL_WINDOWS:
        transcript = _fresh_transcript(
            tmp_path,
            sampled_at=datetime.now(timezone.utc),
            total_tokens=_SATURATING_TOKENS,
            model=model,
        )
        record, uncalibrated = gw.compute_record(str(transcript))

        assert uncalibrated is None, (
            f"{model}: the writer reported no window for a model that is a KEY "
            f"of its own MODEL_WINDOWS table"
        )
        assert record is not None, f"{model}: the writer produced no record"
        fills[model] = record["fill_fraction"]

    assert len(fills) == len(gw.MODEL_WINDOWS)

    assert len(set(fills.values())) == 1, (
        f"a token count past EVERY calibrated window produced different fills "
        f"per model ({fills}), so the clamp is not a single shared ceiling"
    )
    observed = fills[next(iter(fills))]
    assert observed == gr.FILL_CEILING, (
        f"the writer's clamp saturates at {observed!r} but the reader's "
        f"FILL_CEILING is {gr.FILL_CEILING!r}. The reader cannot import the "
        f"writer to find this out, so this test IS the pin -- update the "
        f"constant to the executed value rather than weakening the assertion"
    )


# --------------------------------------------------------------------------- #
# (7) WINDOW INVARIANCE -- the trip is a function of ABSOLUTE tokens
# --------------------------------------------------------------------------- #
#
# `_PROFILES` stores ABSOLUTE token caps and `thresholds_for` divides them by
# the reader's window; the writer divides the token count by ITS window. When
# the two tables agree, the window CANCELS:
#
#     fill >= hard   <=>   tokens / window >= hard_cap / window   <=>   tokens >= hard_cap
#
# So today a consistently-wrong window corrupts ONLY THE DISPLAYED PERCENTAGE,
# never the verdict. That is a real and valuable property -- it is why #252's
# five-times-wrong window could not, on the current code, cause a wrongful
# block -- and NOTHING IN THE REPO ASSERTS IT. It holds by construction, which
# is exactly the kind of property a refactor deletes without noticing: the day
# someone stores typed fractions again instead of absolute caps, the window
# stops cancelling and the #252 hole re-opens SILENTLY, with every existing
# test still green.
#
# This section makes that loud. It runs the chain twice over the same absolute
# token counts -- once on the shipped toolchain, once on a copy whose windows
# are all scaled -- and asserts the engine's advisory BAND is identical at
# every token count while the displayed FILL genuinely moves.
#
# NO SHIPPED FILE IS EDITED to build this. The scaled world is a materialized
# COPY inside the fence; see `_scaled_toolchain`.

# Any factor but 1 works. 2 is the smallest that separates the two worlds, and
# a factor (rather than a replacement table) is what makes the scaling a
# transformation OF the shipped tables rather than a second hand-typed copy of
# them.
_WINDOW_SCALE = 2


def _with_epilogue(source, epilogue):
    """Append `epilogue` to module `source`, ahead of any `__main__` guard.

    Placement is not cosmetic. `gauge_writer_hook.py` ends in
    `sys.exit(main(...))` under its guard, so an epilogue appended after it
    would never execute when the module is run AS A SCRIPT -- which is exactly
    how this file drives the writer. The scaling would silently not happen and
    the invariance test would compare the shipped chain to itself and pass.
    """
    marker = '\nif __name__ == "__main__":'
    if marker not in source:
        return source + epilogue
    head, tail = source.split(marker, 1)
    return head + epilogue + marker + tail


def _scaled_toolchain(tmp_path):
    """A COPY of the chain's four shipped modules, with every window scaled.

    Four files is the whole file-relative closure, and nothing else needs
    copying: `checklist_engine.py` loads `gauge_reader.py` from its own
    directory, and `gauge_writer_hook.py` loads `spine_rail.py` from its own
    directory. Everything else either is stdlib or is located from the spine
    path passed in at run time.

    THE SCALING IS A TRANSFORMATION OF THE SHIPPED TABLES, NOT A REPLACEMENT
    FOR THEM: the epilogue rewrites each table as a comprehension over whatever
    the shipped module just defined. So it cannot drift from the real tables,
    it cannot silently scale a row that no longer exists, and a model added
    tomorrow is scaled tomorrow with no edit here.

    Returns `(engine_path, writer_hook_path)` for the scaled world.
    """
    root = tmp_path / "scaled-toolchain"
    hooks = root / "hooks"
    hooks.mkdir(parents=True, exist_ok=True)

    # Unmodified -- the engine and the binding rail carry no window of their own.
    shutil.copyfile(_ENGINE, root / "checklist_engine.py")
    shutil.copyfile(_SPINE_RAIL, hooks / "spine_rail.py")

    (root / "gauge_reader.py").write_text(
        _with_epilogue(
            _GAUGE_READER.read_text(encoding="utf-8"),
            f"\n\n_PROFILES = {{model: (window * {_WINDOW_SCALE}, soft_cap, hard_cap)\n"
            f"             for model, (window, soft_cap, hard_cap) in _PROFILES.items()}}\n",
        ),
        encoding="utf-8",
    )
    (hooks / "gauge_writer_hook.py").write_text(
        _with_epilogue(
            _GAUGE_WRITER_HOOK.read_text(encoding="utf-8"),
            f"\n\nMODEL_WINDOWS = {{model: window * {_WINDOW_SCALE}\n"
            f"                 for model, window in MODEL_WINDOWS.items()}}\n",
        ),
        encoding="utf-8",
    )

    return root / "checklist_engine.py", hooks / "gauge_writer_hook.py"


# The capture's own model, and the ABSOLUTE token counts that straddle its two
# band boundaries. Read off the real table at test time, never typed
# (decision:no-threshold-values): these are the caps the table already holds,
# not a bound this file imposes, and a re-calibration moves the probes with it.
_CAPTURE_MODEL = _capture_records()[-1]["message"]["model"]
_, _CAPTURE_SOFT_CAP, _CAPTURE_HARD_CAP = gr._PROFILES[_CAPTURE_MODEL]

# One token below each cap and exactly at it -- the tightest probe pair that
# LOCATES a flip rather than merely sampling around it.
_INVARIANCE_PROBES = (
    _CAPTURE_SOFT_CAP - 1,
    _CAPTURE_SOFT_CAP,
    _CAPTURE_HARD_CAP - 1,
    _CAPTURE_HARD_CAP,
)


def _chain_at_token_counts(tmp_path, *, engine, writer_hook):
    """Drive the whole chain once per probe through the GIVEN toolchain, and
    report `{total_tokens: (band, fill)}`.

    Keyed by ABSOLUTE TOKEN COUNT, which is the entire point: the question this
    section asks is "at what token count does the band flip", and a dict keyed
    by tokens answers it directly for whichever toolchain produced it.

    Same fence, same spine tree, same session id, same transcript shape as
    every other test here -- the toolchain is the only variable.
    """
    spine = _work_tree(tmp_path)
    gauge = spine.parent / "gauge.json"

    observed = {}
    for total_tokens in _INVARIANCE_PROBES:
        transcript = _fresh_transcript(
            tmp_path,
            sampled_at=datetime.now(timezone.utc),
            total_tokens=total_tokens,
        )
        proc = _run_writer_hook(tmp_path, transcript, hook=writer_hook)
        assert proc.returncode == 0, proc.stderr
        assert proc.stdout == ""
        assert gauge.exists(), (
            f"{total_tokens} tokens: the writer wrote no gauge.json "
            f"(stderr: {proc.stderr})"
        )

        engine_proc = _run_engine_current(tmp_path, spine, engine=engine)
        assert engine_proc.returncode == 0, engine_proc.stderr

        fill = json.loads(gauge.read_text(encoding="utf-8"))["fill_fraction"]
        observed[total_tokens] = (_band_of(engine_proc.stdout), fill)
    return observed


def test_window_invariance_the_band_is_a_function_of_absolute_tokens(tmp_path):
    """THE REGRESSION PIN: scale BOTH windows, and the token count at which
    each band flips must not move.

    What this locks is the cancellation described in this section's header --
    the property that makes a consistently-wrong window a DISPLAY defect rather
    than a decision defect. A refactor back to typed fractions breaks it, and
    breaks it here, loudly, instead of re-opening #252 in silence.

    TWO CONTROLS, both load-bearing, because the headline equality is easy to
    satisfy vacuously:

      * THE STRADDLE CONTROL. If every probe landed in the same band, the two
        worlds would agree trivially and the test would assert nothing. So the
        shipped world must be observed crossing BOTH boundaries.

      * THE SCALING CONTROL. If `_scaled_toolchain` silently failed to scale
        anything -- a `__main__`-guard placement bug, a renamed table, a
        copy that was never written -- the "two" worlds would be one world
        compared to itself, and the equality would hold for the worst possible
        reason. So the FILL must be observed genuinely MOVING, by exactly the
        scale factor, at every probe. That is the same finding stated
        positively: the number a human reads changes; the verdict does not.
    """
    shipped = _chain_at_token_counts(
        tmp_path, engine=_ENGINE, writer_hook=_GAUGE_WRITER_HOOK)

    scaled_engine, scaled_writer = _scaled_toolchain(tmp_path)
    scaled = _chain_at_token_counts(
        tmp_path, engine=scaled_engine, writer_hook=scaled_writer)

    # --- the straddle control, FIRST: without it the equality below is vacuous
    shipped_bands = {band for band, _fill in shipped.values()}
    assert shipped_bands == set(_ASCENDING_BANDS), (
        f"the probes {_INVARIANCE_PROBES} did not straddle both boundaries in "
        f"the shipped world -- they only produced {sorted(shipped_bands)}, so "
        f"comparing the two worlds proves nothing about where a band flips"
    )

    # --- the scaling control: the two worlds really are different worlds -----
    for total_tokens in _INVARIANCE_PROBES:
        _, shipped_fill = shipped[total_tokens]
        _, scaled_fill = scaled[total_tokens]
        assert scaled_fill < shipped_fill, (
            f"{total_tokens} tokens read as {scaled_fill} in the 'scaled' world "
            f"and {shipped_fill} in the shipped one -- the displayed fill did "
            f"not move, so the toolchain copy was never actually scaled and "
            f"this test is comparing the shipped chain to itself"
        )
        assert math.isclose(scaled_fill * _WINDOW_SCALE, shipped_fill, rel_tol=1e-12), (
            f"{total_tokens} tokens: the scaled world read {scaled_fill}, which "
            f"is not the shipped {shipped_fill} divided by {_WINDOW_SCALE} -- "
            f"something other than the window changed between the two runs"
        )

    # --- THE PIN ------------------------------------------------------------
    # Compared per ABSOLUTE TOKEN COUNT, so this says exactly what it means:
    # the band each token count lands in is unchanged by scaling the window.
    shipped_bands_by_tokens = {t: band for t, (band, _f) in shipped.items()}
    scaled_bands_by_tokens = {t: band for t, (band, _f) in scaled.items()}
    assert scaled_bands_by_tokens == shipped_bands_by_tokens, (
        f"scaling every window by {_WINDOW_SCALE} MOVED the token count at "
        f"which a band flips: shipped {shipped_bands_by_tokens} vs scaled "
        f"{scaled_bands_by_tokens}. The trip verdict is no longer a function "
        f"of absolute tokens alone, which is precisely the condition that let "
        f"a wrong window mis-scale the governor in #252"
    )


# --- #600: the OWNED chain, writer process to leased engine ------------------
#
# The chain above is the LEASELESS one (R3): nothing claims the spine, the
# binding entry names no lease, and both ends agree on the unowned `gauge.json`.
# This is its counterpart, and it is the one that covers the new behaviour --
# the writer names the record for its owner and a LEASED engine, computing that
# same name independently from its own lease, finds it.
#
# The two names are the same string by construction: the binding entry's
# `engine_session` is parsed from the very `claim --session-id X` that creates
# the lease, and the lease holds that same X. That is the claim under test, and
# it is worth a process boundary because the two sides compute it in different
# processes from different inputs -- an in-process test could share a cached
# module and never notice a drift that would take the whole fleet's governor
# dark in production.

_OWNED_SESSION_ID = "chain-owner-to-trip-session"
_OWNED_WORK_ID = "chainwork-owned"
_OWNED_ENGINE_SESSION = "chain-owner-session"
# DRIFT PIN, not a derivation: hand-computed from the owner-key algorithm, so
# this asserts the name rather than agreeing with whatever the code produces.
# The algorithm itself is pinned in tests/test_gauge_reader.py.
_OWNED_GAUGE = "gauge-chain-owner-session-88570f7146b4.json"


def test_chain_owner_keyed_reading_reaches_the_leased_engine(tmp_path):
    """One record, written by the writer PROCESS under an owner-keyed name, read
    back by the engine PROCESS from a name it computed independently.

    ORDERING MATTERS AND IS NOT INCIDENTAL: the claim happens BEFORE the
    transcript is sampled, so the reading is `observed_at >= claimed_at` and is
    this session's own. Sampling first would make it pre-claim, and #601's
    comparison would correctly decline it -- which is the SEQUENTIAL half of the
    fix doing its job, not a failure, but it would leave this test unable to say
    anything about the CONCURRENT half it exists for.
    """
    spine = _spine_tree(tmp_path, _OWNED_WORK_ID)

    # --- the lease, through the real engine CLI as a fresh process -----------
    claimed = _run_fenced(
        [sys.executable, str(_ENGINE), "--file", str(spine), "claim",
         "--session-id", _OWNED_ENGINE_SESSION, "--claimed-by", "agent"],
        tmp_path)
    assert claimed.returncode == 0, claimed.stderr

    # The binding entry carries the SAME name the claim above carried, which is
    # what production does -- spine_rail parses it out of that very command.
    sr.save_binding(tmp_path, {
        _OWNED_SESSION_ID: {
            str(spine.resolve()): {
                "spine": str(spine.resolve()),
                "engine_session": _OWNED_ENGINE_SESSION,
                "worktree": str(tmp_path),
                "claimed_at": datetime.now(timezone.utc).isoformat(),
            }
        }
    })

    transcript = _fresh_transcript(tmp_path, sampled_at=datetime.now(timezone.utc))
    proc = _run_writer_hook(tmp_path, transcript, session_id=_OWNED_SESSION_ID)
    assert proc.returncode == 0, proc.stderr
    assert proc.stdout == ""

    gauge = spine.parent / _OWNED_GAUGE
    assert gauge.exists(), (
        f"the writer process wrote no owner-keyed gauge; the directory holds "
        f"{sorted(p.name for p in spine.parent.iterdir())} "
        f"(writer stderr: {proc.stderr})")
    # the folder-owned file this issue exists to remove is NOT written
    assert not (spine.parent / "gauge.json").exists()

    written = json.loads(gauge.read_text(encoding="utf-8"))
    # the record NAMES its owner, and that name is the one in the filename --
    # the filename removes the collision, the field makes a mismatch detectable
    assert written["owner"] == gauge.name[len("gauge-"):-len(".json")]
    assert set(gr.REQUIRED_FIELDS) <= set(written)

    # --- Trip, via the real engine CLI as a fresh process --------------------
    # The engine was never told the filename. It recomputes it from the lease it
    # is holding, so a rendered band is proof both processes agreed.
    engine = _run_engine_current(tmp_path, spine)
    assert engine.returncode == 0, engine.stderr
    reading = gr.read(gauge)
    assert reading is not None
    soft, _hard = gr.thresholds_for(reading.model)
    assert soft <= reading.fill_fraction, (
        "the committed capture no longer reads at or above the soft band, so "
        "the engine renders no advisory and this chain has nothing to trace")
    assert "CONTEXT" in engine.stdout, (
        f"the leased engine rendered no band from the owner-keyed reading it "
        f"should have found at {gauge.name} -- writer and engine have drifted "
        f"apart on how they name an owner. stdout: {engine.stdout}")
