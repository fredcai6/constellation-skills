"""#305 gate g3 — the NEGATIVE CONTROL for `zero agent effort is literal`.

The claim under test is `docs/EPISODE_STORE.md` §4's mechanical bin: *a run where the
agent records nothing must still yield the full mechanical field group*. A field an
agent can omit by forgetting is not mechanically captured — it is agent-supplied
wearing a mechanical label — so this file drives a **real engine spine** in which the
agent authors nothing at all, and then compares the composed group, field by field,
against a tally this harness keeps **itself**.

Three properties make this a control rather than a demonstration.

**1. The oracle is independent.** `_ControlRun` increments its own expectation at the
moment it issues the triggering call — when it issues a reopen it expects honored, it
increments `_reopens` on that line. It never calls `mechanical_fields()`,
`reopen_total()`, `failed_command_count()` or `context_manifest.rev()` to decide what
the answer should be, and it never re-derives an expectation from the checklist JSON.
Any of those would compare the thing to itself. `context-manifest-ref`'s revision is
computed here as a raw git blob OID (`sha1(b"blob <n>\\0" + data)`), and independently
cross-checked against `git hash-object --no-filters`, which is a second witness that
shares no code with the producer.

**2. It exercises BOTH lease topologies, because only one of them is production.**
Gates live in the CHILD gate-plan a parent spine delegates to, and that child never
receives a lease (#357). `_lease_role` reads `engine_session.claimed_by`, and
`refusals` is armed only by `claim` — so on the child both are structurally
unavailable, and no agent action can change it. A control that drove only a claimed
standalone spine would report all ten fields green and prove nothing about the seam
that actually fires in production. Both topologies are driven through the SAME verb
sequence, so the lease is the only difference between them and the delta cannot be
attributed to anything else.

**3. Refusal is asserted, not skipped.** A field the composer legitimately refuses is
expected as `REFUSED` and the comparison fails if it turns up *present* — so the
refusal assertions can themselves go red (`test_red_proof_sharp_fabricated_role`
proves exactly that). A non-reading stays visibly distinct from an uncollected one.

**The comparison returns a list of mismatched field NAMES, never a boolean.** That is
what lets the red-proofs below assert `mismatches == ["failed-commands"]` — a per-field
claim. A non-zero exit code is not proof a check can fail: an import error, a collection
error and an empty test selection all exit non-zero too.
"""

from __future__ import annotations

import ast
import builtins
import contextlib
import hashlib
import inspect
import io
import json
import os
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
ENGINE = REPO_ROOT / "scripts" / "checklist_engine.py"
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import context_manifest  # noqa: E402
import episode_capture  # noqa: E402

#: The mechanical group under test. `REQUIRED_MECHANICAL_FIELDS` is what
#: `apply_episode_delta._validate_create` demands; `artifact-ref` is deliberately not
#: in that tuple (list-shaped and optional) but IS part of the mechanical bin, so the
#: control covers it too.
MECHANICAL_GROUP = tuple(episode_capture.REQUIRED_MECHANICAL_FIELDS) + ("artifact-ref",)

#: Every engine flag whose value is a free-text string an agent composes, read off
#: `checklist_engine.py`'s argparse block rather than guessed: `--why` (advance),
#: `--note` (attest/resume), `--finding` (record), `--reason` (claim/release/skip/
#: resume/reopen/amend/waive), `--statement` (flag-candidate), `--verdict`/`--summary`/
#: `--override-reason` (consolidate), `--blocker`/`--next`/`--authority` (block/waive/
#: amend), `--title`/`--imperative` (append), `--payload`/`--payload-file`/`--field`
#: (attach), `--claimed-by` (claim). Naming them is what lets the census say "this run
#: contains exactly these agent-supplied strings" instead of "no forbidden flag I
#: happened to think of".
#:
#: `--claimed-by` is here because leaving it out made the census under-report. It is a
#: string the harness composes and hands the engine, and `_lease_role` reads it back out
#: of the lease as the `role` MECHANICAL field — so it is the one agent-supplied string
#: that does feed the group under test. Omitting it let an entire second constant sit
#: outside a census whose docstring claimed there was only one.
AGENT_TEXT_FLAGS = frozenset({
    "--why", "--note", "--finding", "--reason", "--statement", "--verdict",
    "--summary", "--override-reason", "--blocker", "--next", "--authority",
    "--title", "--imperative", "--payload", "--payload-file", "--field",
    "--claimed-by",
})

#: CLOSED-WORLD: the only flags this control may pass, per verb. Closed rather than a
#: blacklist, and that is the whole point of the guard below — a flag missing from its
#: verb's set fails the census whether or not `AGENT_TEXT_FLAGS` ever heard of it, so a
#: text-bearing flag added to the engine tomorrow is caught without this file being
#: updated. A blacklist is what let mutation M1 (`advance --why <prose>` plus `--note`
#: on every `attest`) pass a guard named "records nothing agent authored".
ALLOWED_FLAGS = {
    "claim": frozenset({"--session-id", "--claimed-by", "--worktree"}),
    "start": frozenset({"--session-id"}),
    "attest": frozenset({"--cond", "--which", "--session-id"}),
    "advance": frozenset({"--mechanical", "--session-id"}),
    "reopen": frozenset({"--reason", "--session-id"}),
}

#: `store_true` flags: the token after one of these is NOT its value.
VALUELESS_FLAGS = frozenset({"--mechanical", "--force", "--dry-run"})

#: The role the parent run declares. A module constant rather than a literal buried in
#: the fixture because the census below asserts the exact set of agent-supplied strings,
#: and a value that assertion names should be declared where the claim about it is.
PARENT_ROLE = "commander"


def _flag_pairs(argv: tuple[str, ...]) -> list[tuple[str, str | None]]:
    """`(flag, value)` for every flag in one issued argv, positionals dropped.

    A value that itself begins with `--` would be mis-read as a flag; no engine verb
    takes one, and the census is strictly *more* likely to fire in that case (an
    unknown flag), never less — so the parse cannot turn a violation into a pass.
    """
    pairs: list[tuple[str, str | None]] = []
    i = 1
    while i < len(argv):
        token = argv[i]
        if not token.startswith("--"):
            i += 1
            continue
        if token in VALUELESS_FLAGS or i + 1 >= len(argv) or argv[i + 1].startswith("--"):
            pairs.append((token, None))
            i += 1
        else:
            pairs.append((token, argv[i + 1]))
            i += 2
    return pairs


class _Refused:
    """Sentinel: this field is expected to be ABSENT, and absence is the correct
    reading. Distinct from `None`, which a composer could plausibly emit as a value."""

    __slots__ = ()

    def __repr__(self) -> str:  # pragma: no cover - debug aid only
        return "<REFUSED>"


REFUSED = _Refused()


class Expect:
    """One field's expected value plus the INDEPENDENT source it came from.

    The `source` string is not decoration: C3 requires the control to say, per field,
    what the independent source was, and keeping it beside the value is what stops the
    two drifting apart.
    """

    __slots__ = ("value", "source")

    def __init__(self, value, source: str) -> None:
        self.value = value
        self.source = source

    def __repr__(self) -> str:  # pragma: no cover - debug aid only
        return f"Expect({self.value!r}, {self.source!r})"


def compare_fields(expected: dict[str, Expect], actual: dict) -> list[str]:
    """The comparison. Returns the names of the fields that do not match, in
    `MECHANICAL_GROUP` order.

    A list rather than a bool, deliberately: a boolean control can only say "something
    is wrong", which is indistinguishable from a wrapper mapping any non-zero exit to
    RED. Naming the field is what makes a red-proof discriminating.

    An `Expect(REFUSED, ...)` field must be ABSENT. Present-when-refusal-was-expected is
    a mismatch, which is what keeps the refusal assertions falsifiable.
    """
    mismatches: list[str] = []
    for name in MECHANICAL_GROUP:
        want = expected[name].value
        present = name in actual
        if want is REFUSED:
            if present:
                mismatches.append(name)
        elif not present or actual[name] != want:
            mismatches.append(name)
    return mismatches


#: Every producer the oracle must not consult, as `(module, attribute)`. These are the
#: things the control is *testing*; an expectation sourced from any of them compares the
#: thing to itself. `emit_*` are here because the seam's own output is the same reading
#: by another route.
FORBIDDEN_PRODUCERS = tuple(
    (episode_capture, name)
    for name in (
        "mechanical_fields", "reopen_total", "failed_command_count", "manifest_ref",
        "_lease_role", "_artifact_refs", "project_name", "snapshot_path",
        "emit_mechanical_snapshot", "emit_step_manifest",
    )
) + tuple(
    (context_manifest, name) for name in ("rev", "build_manifest", "rows", "content")
)

#: The same names as bare identifiers, for the static pass. `compose`/`snapshot` are the
#: harness's own accessors for the reading under test, so they belong here too.
FORBIDDEN_IDENTIFIERS = frozenset(
    {name for _, name in FORBIDDEN_PRODUCERS}
    | {"compose", "snapshot", "episode_capture", "context_manifest", "cm", "active_id"}
)


@contextlib.contextmanager
def _independence_harness():
    """Make every producer under test UNCALLABLE, and the emitted snapshot UNREADABLE.

    Independence proven by execution rather than by declaration. Inside this block the
    oracle either builds its expectation from its own tallies and the manifest file, or
    it raises — there is no third outcome, and no description string is consulted to
    decide which happened.

    File reads are guarded rather than the whole filesystem blocked, because the oracle
    legitimately reads ONE file: the context manifest whose own bytes it pins. What it
    may not read is anything under a `mechanical/` directory — that is the seam's
    emitted snapshot, which is the reading under test wearing a different hat.
    """
    saved: list[tuple[object, str, object]] = []

    def patch(obj: object, attr: str, value: object) -> None:
        saved.append((obj, attr, getattr(obj, attr)))
        setattr(obj, attr, value)

    def raiser(label: str):
        def boom(*_args, **_kwargs):
            raise AssertionError(
                f"the oracle called {label}: the expectation is NOT independent of the "
                f"thing under test — it would be comparing the thing to itself"
            )

        return boom

    def guard(target) -> None:
        try:
            parts = Path(os.fspath(target)).parts
        except TypeError:  # an fd, not a path
            return
        if "mechanical" in parts:
            raise AssertionError(
                f"the oracle read the seam's emitted snapshot ({target}): that is the "
                f"reading under test, not an independent source"
            )

    for module, name in FORBIDDEN_PRODUCERS:
        patch(module, name, raiser(f"{module.__name__}.{name}"))
    patch(_ControlRun, "compose", raiser("_ControlRun.compose"))
    patch(_ControlRun, "snapshot", raiser("_ControlRun.snapshot"))

    real_open, real_text, real_bytes = builtins.open, Path.read_text, Path.read_bytes

    def guarded_open(file, *args, **kwargs):
        guard(file)
        return real_open(file, *args, **kwargs)

    def guarded_read_text(self, *args, **kwargs):
        guard(self)
        return real_text(self, *args, **kwargs)

    def guarded_read_bytes(self, *args, **kwargs):
        guard(self)
        return real_bytes(self, *args, **kwargs)

    patch(builtins, "open", guarded_open)
    patch(io, "open", guarded_open)  # what `Path.open` actually calls
    patch(Path, "read_text", guarded_read_text)
    patch(Path, "read_bytes", guarded_read_bytes)
    try:
        yield
    finally:
        for obj, attr, original in reversed(saved):
            setattr(obj, attr, original)


def blob_oid(data: bytes) -> str:
    """Git blob OID over `data`'s own bytes, computed here.

    Deliberately NOT `context_manifest.rev()` — calling the producer's own identity
    function to check the producer's own output compares the thing to itself.
    """
    header = b"blob %d\0" % len(data)
    return hashlib.sha1(header + data).hexdigest()


def _git(args: list[str], cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args], cwd=str(cwd), capture_output=True, text=True, encoding="utf-8"
    )


#: The control's OWN `context_refs`, declared on every gate of its plan. Two entries,
#: both under the `repo` root of the temp repository this module builds, and both real
#: files at the moment the manifest is taken — so the delivered-context half of the
#: manifest is actually EXERCISED rather than skipped.
#:
#: Before this existed the plan declared nothing, every manifest carried `files: []`, and
#: attack A3 ("make every declared ref resolve to a missing file") passed through a hole
#: rather than being caught: with no row declared, there was no row that could go null.
#: `test_a3_a_null_manifest_does_not_read_as_success` is what reaches that condition now.
DECLARED_CONTEXT = (
    {"root": "repo", "path": "seed.txt"},
    {"root": "repo", "path": "changed_by_the_run.txt"},
)


def expected_rows(repo: Path) -> list[dict]:
    """What the delivered-context rows MUST say, computed HERE from the files' bytes.

    `blob_oid`, never `context_manifest.rev()` and never the manifest itself — the same
    independence rule the field expectations follow. `rev: null` is the correct reading
    for a declared file that is not there, and it is produced here the same way, so the
    absent case is expected rather than special-cased.
    """
    out: list[dict] = []
    for entry in DECLARED_CONTEXT:
        target = repo / entry["path"]
        out.append({
            "root": entry["root"],
            "path": entry["path"],
            "rev": blob_oid(target.read_bytes()) if target.exists() else None,
        })
    return out


def compare_manifest_rows(expected: list[dict], manifest: dict) -> list[str]:
    """Mismatched declared PATHS, in declaration order — a list of names, never a bool,
    for exactly the reason `compare_fields` is.

    A row that is missing, out of declaration order, or carrying the wrong `rev` — which
    includes `null` where a file really was delivered — is named. That is what stops an
    all-null manifest reading as success.
    """
    actual = manifest.get("files")
    if not isinstance(actual, list):
        return [entry["path"] for entry in expected]
    mismatches = [
        want["path"]
        for index, want in enumerate(expected)
        if index >= len(actual) or actual[index] != want
    ]
    return mismatches + [row.get("path") for row in actual[len(expected):]]


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(payload, indent=2) + "\n")


def _plan(work_id: str, ok_flag: Path, child: str | None) -> dict:
    """Two gates, identical on parent and child so the LEASE is the only difference.

    `g2.c2` is a `command` check whose entire signal is its exit code — `test -f` on an
    absolute path. #315: the engine passes no `cwd` on the command branch and discards
    the check's stdout, so a check that printed its verdict would print into a void and
    a relative path would resolve against an uncontrolled directory. An exit-code
    vocabulary is the only thing that reaches the spine, so the induced failure is built
    as one: flag absent -> exit 1, flag present -> exit 0.
    """

    def gate(gid: str, command: str | None) -> dict:
        posts = [{"id": "c1", "statement": "attested", "check": None, "satisfied": False}]
        if command:
            posts.append(
                {
                    "id": "c2",
                    "statement": "induced command check",
                    "check": {"kind": "command", "command": command},
                    "satisfied": False,
                }
            )
        return {
            "id": gid,
            "title": gid,
            "imperative": gid,
            # Declared on BOTH gates: the manifest is written per-step, write-if-absent,
            # so a declaration on only the step the control happens to end on would
            # leave the other manifest empty and half the seam unexercised.
            "context_refs": [dict(entry) for entry in DECLARED_CONTEXT],
            "preconditions": [],
            "postconditions": posts,
            "constraints": [],
            "directives": None,
            "child_checklist": child if gid == "g1" else None,
            "status": "pending",
            "status_detail": {},
            "result": None,
            "finding": None,
            "evidence": [],
            "rework_count": 0,
        }

    gates = [gate("g1", None), gate("g2", f'test -f "{ok_flag.as_posix()}"')]
    return {
        "work_id": work_id,
        "type": "gated",
        "config_ref": None,
        "items": [g["id"] for g in gates],
        "tasks": {g["id"]: g for g in gates},
        "consolidation": None,
        "triage_candidates": [],
        "blockers": [],
    }


class _ControlRun:
    """Drives ONE checklist through the real engine CLI and keeps its own tally.

    CLI subprocesses, not the Python API, and that is load-bearing rather than
    stylistic: `refusals` is armed by `claim` but incremented ONLY in
    `checklist_engine.main()`'s `EngineError` branch, so an API-driven control would
    never move the counter and would be measuring a field that production does move.
    """

    #: Every engine verb this control is allowed to issue. What each call may CARRY is
    #: `ALLOWED_FLAGS`, and `test_control_records_nothing_agent_authored` asserts it over
    #: the recorded argv — a claim about flags that lives only in a comment is a claim
    #: nothing checks, which is exactly how mutation M1 got through.
    VERBS = ("claim", "start", "attest", "advance", "reopen")

    REOPEN_REASON = "control"

    def __init__(self, path: Path, repo: Path, work_id: str, role: str | None) -> None:
        self.path = path
        self.repo = repo
        self.work_id = work_id
        self.role = role  # None => never claimed => no lease
        self.issued: list[str] = []  # verb names only, for the count-shaped assertions
        self.calls: list[tuple[str, ...]] = []  # the FULL argv of every issued call
        # --- the independent tally, all incremented at issue time ---
        self._refusals: int | None = None  # None until `claim` ARMS the counter
        self._reopens = 0  # run-scoped: every honored reopen on this checklist
        self._rework: dict[str, int] = {}  # step-scoped
        self._failed: dict[str, int] = {}  # step-scoped, engine-run command failures

    # -- engine ------------------------------------------------------------- #
    def _run(self, *argv: str, refused: bool = False) -> subprocess.CompletedProcess:
        proc = subprocess.run(
            [sys.executable, str(ENGINE), "--file", str(self.path), *argv],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        self.issued.append(argv[0])
        # The whole argv, not just the verb: every claim this control makes about what
        # it did NOT record is a claim about flags, and a flag it never wrote down is a
        # flag no assertion can reach.
        self.calls.append(tuple(argv))
        assert argv[0] in self.VERBS, f"control issued a non-sanctioned verb: {argv[0]}"
        if refused:
            assert proc.returncode != 0, f"expected a refusal, got success: {proc.stdout}"
            # Tallied HERE, on the line that issues the call the harness expects to be
            # refused — not read back from the file afterwards.
            if self._refusals is not None:
                self._refusals += 1
        else:
            assert proc.returncode == 0, f"engine refused unexpectedly: {proc.stderr}"
        return proc

    def _session(self) -> list[str]:
        return ["--session-id", f"sess-{self.work_id}"] if self.role else []

    def drive(self, ok_flag: Path) -> None:
        """The whole run. Every action is one a run mechanically requires."""
        if self.role:
            self._run(
                "claim",
                "--session-id",
                f"sess-{self.work_id}",
                "--claimed-by",
                self.role,
                "--worktree",
                ".",
            )
            self._refusals = 0  # `claim` ARMS the counter; before that it does not exist

        s = self._session()
        self._run("start", "g1", *s)
        self._run("attest", "g1", "--cond", "c1", "--which", "postconditions", *s)
        self._run("advance", "g1", "--mechanical", *s)

        self._run("start", "g2", *s)
        self._run("attest", "g2", "--cond", "c1", "--which", "postconditions", *s)
        # Three induced command failures. The flag is absent, so `test -f` exits 1, the
        # engine records a `command-output` evidence item with `exit: 1`, and the
        # advance is refused. One call, two tallies — both incremented right here.
        for _ in range(3):
            self._failed["g2"] = self._failed.get("g2", 0) + 1
            self._run("advance", "g2", "--mechanical", *s, refused=True)

        ok_flag.write_text("", encoding="utf-8", newline="\n")
        self._run("advance", "g2", "--mechanical", *s)  # exit 0 now; not a failure

        # A refusal that produces NO command evidence, so `refusals` and
        # `failed-commands` cannot be the same number by construction.
        self._run("start", "g1", *s, refused=True)  # g1 is complete

        self._reopens += 1
        self._rework["g1"] = self._rework.get("g1", 0) + 1
        self._run("reopen", "g1", "--reason", self.REOPEN_REASON, *s)

        self._run("attest", "g1", "--cond", "c1", "--which", "postconditions", *s)
        self._run("advance", "g1", "--mechanical", *s)

        self._run("start", "g2", *s)  # cascade-reset it to pending
        self._run("attest", "g2", "--cond", "c1", "--which", "postconditions", *s)
        self._run("advance", "g2", "--mechanical", *s)

        # Last action, so the seam's emitted snapshot is the freshest possible reading.
        self._reopens += 1
        self._rework["g2"] = self._rework.get("g2", 0) + 1
        self._run("reopen", "g2", "--reason", self.REOPEN_REASON, *s)

    # -- the independent expectation ---------------------------------------- #
    def expectations(self, staged: list[str]) -> dict[str, Expect]:
        step = "g2"  # the harness knows which step it left active; it does not ask
        # #360, hit live while writing this: `manifest_root()` is the checklist dir's
        # PARENT and `manifest_path` re-appends the work-id, so the file lands BESIDE
        # the checklist, not one level further down. Deriving it as
        # `<checklist dir>/<work-id>/context/` looked past the file and read as "no
        # manifest at all" — "no output produced" and "output produced somewhere you
        # did not look" are indistinguishable without checking the derivation.
        manifest = self.path.parent / "context" / f"{step}.json"
        with open(manifest, "rb") as handle:
            manifest_bytes = handle.read()
        revision = blob_oid(manifest_bytes)
        # Second, code-disjoint witness for the same OID.
        witness = _git(
            ["hash-object", "--no-filters", str(manifest)], self.repo
        ).stdout.strip()
        assert witness == revision, (
            "the harness's own blob OID disagrees with `git hash-object --no-filters`; "
            "the independent expectation is not trustworthy"
        )

        role = (
            Expect(self.role, "the --claimed-by string this harness passed to `claim`")
            if self.role
            else Expect(
                REFUSED,
                "no lease: this checklist was NEVER claimed (the production child "
                "gate-plan shape, #357), so `_lease_role` has no engine_session to read",
            )
        )
        refusals = (
            Expect(self._refusals, "count of calls this harness issued EXPECTING a refusal")
            if self._refusals is not None
            else Expect(
                REFUSED,
                "the counter is ARMED only by `claim` (checklist_engine.py:964); this "
                "checklist was never claimed, so the key never exists — note the harness "
                "still issued 4 refused calls against it, so absence here is structural, "
                "NOT 'no refusals happened'",
            )
        )
        return {
            "run": Expect(self.work_id, "the work_id this harness wrote into the plan"),
            "project": Expect(
                self.repo.name, "the directory name this harness chose for the temp repo"
            ),
            "role": role,
            "spine-step": Expect(step, "the gate this harness deliberately left active"),
            "context-manifest-ref": Expect(
                f"ctx-{self.work_id}-{step}@{revision}",
                "sha1(b'blob <n>\\\\0' + manifest bytes) computed in this harness, "
                "cross-checked against `git hash-object --no-filters` — never "
                "context_manifest.rev()",
            ),
            "refusals": refusals,
            "reopens": Expect(
                self._reopens, "count of reopens this harness issued expecting them honored"
            ),
            "rework-count": Expect(
                self._rework.get(step, 0),
                "count of reopens this harness issued against the ACTIVE step only",
            ),
            "failed-commands": Expect(
                self._failed.get(step, 0),
                "count of advances this harness issued while it had deliberately left "
                "the flag file absent, so the engine's command check had to exit 1",
            ),
            "artifact-ref": Expect(
                staged, "the exact paths this harness staged with `git add`"
            ),
        }

    def compose(self) -> dict:
        """The reading under test. Attribute lookup on the module happens HERE, at call
        time, which is what lets a red-proof monkeypatch the composer."""
        checklist = json.loads(self.path.read_text(encoding="utf-8"))
        return episode_capture.mechanical_fields(checklist, base_dir=self.path.parent)

    def manifest(self, step: str = "g2") -> dict:
        """The step's delivery manifest, as the seam wrote it (#360, see `expectations`).

        Read as bytes and decoded here rather than through `Path.read_text`, for the same
        reason `expectations` does: the file's own bytes are what `context-manifest-ref`
        pins, and a text read on Windows would not be them.
        """
        with open(self.path.parent / "context" / f"{step}.json", "rb") as handle:
            return json.loads(handle.read().decode("utf-8"))

    def snapshot(self) -> dict:
        """What the SEAM wrote on its own, with no test asking it to."""
        path = self.path.parent / "mechanical" / "g2.json"  # #360, see `expectations`
        return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def control(tmp_path_factory):
    """One real parent->child gated run, driven once for the whole module.

    The parent's `g1` carries `child_checklist`, so the child is reached the way
    production reaches it, and the child is driven WITHOUT a lease — which is what
    production does, not a shortcut taken here.
    """
    root = tmp_path_factory.mktemp("negctl")
    repo = root / "mechanical-control-repo"
    repo.mkdir()
    _git(["init", "-q", "-b", "main"], repo)
    _git(["config", "user.email", "control@example.invalid"], repo)
    _git(["config", "user.name", "control"], repo)
    (repo / "seed.txt").write_text("seed\n", encoding="utf-8", newline="\n")
    _git(["add", "seed.txt"], repo)
    _git(["commit", "-qm", "seed"], repo)

    # The one staged path, so `artifact-ref` has a value this harness chose.
    staged = ["changed_by_the_run.txt"]
    (repo / staged[0]).write_text("x\n", encoding="utf-8", newline="\n")
    _git(["add", staged[0]], repo)

    ok_flag = root / "ok.flag"
    agent_work = repo / ".agent-work"
    parent_path = agent_work / "ctl-parent" / "spine.json"
    child_path = agent_work / "ctl-child" / "execute.json"
    _write_json(parent_path, _plan("ctl-parent", ok_flag, child="ctl-child"))
    _write_json(child_path, _plan("ctl-child", ok_flag, child=None))

    parent = _ControlRun(parent_path, repo, "ctl-parent", role=PARENT_ROLE)
    child = _ControlRun(child_path, repo, "ctl-child", role=None)
    parent.drive(ok_flag)
    ok_flag.unlink()  # the child must induce its own failures, not inherit the parent's
    child.drive(ok_flag)

    return {"parent": parent, "child": child, "staged": staged}


# --------------------------------------------------------------------------- #
# The control
# --------------------------------------------------------------------------- #
def test_control_records_nothing_agent_authored(control):
    """`zero agent effort` is literal — asserted over the ACTUAL argv of every call.

    **The honest claim, stated exactly as it is:** the control supplies the engine no
    agent-authored NARRATIVE. Every string it hands over is a fixed identifier declared in
    this module — the work id, the temp repo's directory name, `PARENT_ROLE`, the
    condition ids, and one `reopen --reason` — and nothing composed at issue time. No
    `--why`, no `--note`, no `--finding`.

    The mechanical fields that echo those identifiers — `run`, `project`, `role` — are
    echoing what the run is *made of*, not prose an agent wrote *about* the run, and it
    cannot be otherwise: a run must have an id, a project and a lease holder. A guard
    demanding that no supplied string reach them would be unfalsifiable theatre.

    **What the assertion below actually checks, which is narrower than that claim:** the
    argv census. Every flag is sanctioned for its verb (closed-world), `advance` carries
    `--mechanical`, `attest` carries no `--note`, and the flags named in
    `AGENT_TEXT_FLAGS` hold exactly the two declared constants. Identifiers passed
    positionally, and `--cond`, are outside its reach — stated here because the whole
    point of this gate is that a docstring must not claim more than its code checks. Two
    earlier versions of this docstring did exactly that: "nothing agent-authored was
    recorded" (false — `reopen --reason` writes to `why_trail`), then "exactly ONE fixed
    constant, and it feeds no mechanical field" (false in both halves — `--claimed-by` is
    a second one and it *is* the `role` field). Each was corrected only after a mutation
    proved it false, which is the lesson: the sentence is not evidence, the census is.

    The previous version of this test asserted only that the issued VERB NAMES were a
    subset of `VERBS` — something `_ControlRun._run` already asserts on every call — and
    left every claim about flags in a comment. Mutation M1 (rewrite every
    `advance --mechanical` to `advance --why "<prose>"` and add a `--note` to every
    `attest`) passed it cleanly while four rows of agent prose landed in `why_trail` and
    `satisfied_by`. A guard that cannot fail is the thing this whole gate exists to
    detect, so it is now a CLOSED-WORLD census over `run.calls`: every flag token must
    be sanctioned for its verb, `advance` must positively carry `--mechanical`, `attest`
    must positively carry no `--note`, and the free-text census must come back holding
    exactly the one permitted constant.
    """
    violations: list[str] = []
    text_bearing: set[tuple[str, str, str | None]] = set()
    advances = 0

    assert set(ALLOWED_FLAGS) == set(_ControlRun.VERBS), sorted(ALLOWED_FLAGS)

    for key in ("parent", "child"):
        run = control[key]
        assert run.calls, f"{key} issued nothing at all; the census would be vacuous"
        assert [c[0] for c in run.calls] == run.issued, key
        for argv in run.calls:
            verb = argv[0]
            if verb not in ALLOWED_FLAGS:
                violations.append(f"{key}: non-sanctioned verb {verb!r} in {argv!r}")
                continue
            pairs = _flag_pairs(argv)
            flags = [flag for flag, _ in pairs]
            for flag, value in pairs:
                if flag not in ALLOWED_FLAGS[verb]:
                    violations.append(
                        f"{key}: {verb} carries un-sanctioned flag {flag}={value!r}"
                    )
                if flag in AGENT_TEXT_FLAGS:
                    text_bearing.add((verb, flag, value))
            if verb == "advance":
                advances += 1
                if "--mechanical" not in flags:
                    violations.append(f"{key}: advance without --mechanical: {argv!r}")
            if verb == "attest" and "--note" in flags:
                violations.append(f"{key}: attest carries --note: {argv!r}")

    assert violations == [], violations
    # The census is only meaningful if it actually saw the calls it is about.
    assert advances >= 8, advances
    # ...and the whole run holds exactly the TWO declared constants above, rather than
    # anything composed at issue time. The child never claims, so `--claimed-by` appears
    # once across both topologies.
    assert text_bearing == {
        ("claim", "--claimed-by", PARENT_ROLE),
        ("reopen", "--reason", _ControlRun.REOPEN_REASON),
    }, sorted(text_bearing)


def test_claimed_parent_topology_yields_the_full_mechanical_group(control):
    """(a) A claimed spine: every one of the ten fields present AND correct."""
    parent = control["parent"]
    expected = parent.expectations(control["staged"])
    assert compare_fields(expected, parent.compose()) == []
    # And the tallies are four DISTINCT numbers, so swapping any two would be caught
    # rather than passing by coincidence.
    assert [expected[f].value for f in
            ("rework-count", "reopens", "failed-commands", "refusals")] == [1, 2, 3, 4]


def test_unclaimed_child_topology_refuses_only_role_and_refusals(control):
    """(b) The PRODUCTION shape: gates live in a child gate-plan that never gets a
    lease, so `role` and `refusals` are structurally unavailable — and the other eight
    fields are still present and correct."""
    child = control["child"]
    expected = child.expectations(control["staged"])
    assert compare_fields(expected, child.compose()) == []

    actual = child.compose()
    assert "role" not in actual and "refusals" not in actual
    # Absence is structural, not "nothing happened": the harness issued four refused
    # calls against this checklist and the counter still does not exist.
    assert child.issued.count("advance") >= 3
    assert sorted(f for f in episode_capture.REQUIRED_MECHANICAL_FIELDS
                  if f not in actual) == ["refusals", "role"]


def test_the_seam_emits_the_same_group_unasked(control):
    """The group is not merely composable on demand — the seam wrote it during the run."""
    for key, refused in (("parent", []), ("child", ["refusals", "role"])):
        run = control[key]
        snapshot = run.snapshot()
        assert snapshot["step"] == "g2"
        assert compare_fields(run.expectations(control["staged"]), snapshot["mechanical"]) == []
        # A refused field is reported BY NAME, so a non-reading stays visibly distinct
        # from a field nobody tried to read.
        assert sorted(snapshot["refused"]) == refused


def test_every_field_has_a_named_independent_source(control):
    """C3: the control must be able to say, per field, what the independent source was —
    and the saying must be BACKED, in three layers of decreasing strength.

    The previous version had only the third layer: a substring scan over `exp.source`,
    which is a human-readable DESCRIPTION. That checks what the harness says about
    itself, never what it does, so mutation M5 — rewiring the oracle to read its tallies
    back out of `mechanical_fields` while leaving the description untouched — passed
    cleanly. It was also a substring scan over prose, which is the "assert against the
    FIELD, never a substring of the serialized record" trap one level up.

    **(a) Behavioural, and the one that actually carries the claim.** The expectation is
    rebuilt with every producer under test patched to raise and the seam's emitted
    snapshot made unreadable. If the oracle touches any of them it raises, and the test
    fails naming what it touched. This proves independence by execution.

    **(b) Static over CODE, not prose.** (a) is defeated by exactly one thing: a name
    bound at import time (`from episode_capture import reopen_total`), which no attribute
    patch can reach. So the expectation-building code is parsed and every identifier it
    mentions is checked against `FORBIDDEN_IDENTIFIERS`. Over the AST rather than the
    text, so a docstring saying "never `context_manifest.rev()`" — which the oracle's own
    sources do say — is not mistaken for a call to it.

    **(c) The prose check, kept.** It is cheap, it documents intent, and it catches a
    description that has drifted from its value. It is no longer the only thing standing.
    """
    # (a) --------------------------------------------------------------- behavioural
    with _independence_harness():
        expected = control["parent"].expectations(control["staged"])
    assert sorted(expected) == sorted(MECHANICAL_GROUP)

    # (b) ------------------------------------------------------- static, over the AST
    mentioned: set[str] = set()
    for func in (_ControlRun.expectations, blob_oid, _git):
        tree = ast.parse(textwrap.dedent(inspect.getsource(func)))
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                mentioned.add(node.id)
            elif isinstance(node, ast.Attribute):
                mentioned.add(node.attr)
    assert mentioned, "no identifiers parsed; the static pass would be vacuous"
    assert not (FORBIDDEN_IDENTIFIERS & mentioned), sorted(FORBIDDEN_IDENTIFIERS & mentioned)

    # (c) ------------------------------------------------------------ prose, retained
    for name, exp in expected.items():
        assert exp.source.strip(), name
        for forbidden in ("mechanical_fields", "reopen_total", "failed_command_count",
                          "cm.rev(", "the emitted snapshot"):
            assert forbidden not in exp.source, (name, forbidden)


def test_declared_context_is_delivered_and_pinned(control):
    """The delivered-context half of the manifest, EXERCISED and compared per row.

    `context-manifest-ref` is a byte-pin over the manifest's own bytes, so it stays
    correct however the rows inside come out — which is right, and is also why it can
    never be the thing that tells you the rows are wrong. This is what covers the rows:
    each declared entry must come back in declaration order, under the root token it was
    declared with, carrying a `rev` equal to a blob OID this harness computed from the
    file's own bytes.
    """
    repo = control["parent"].repo
    want = expected_rows(repo)
    # If every expected rev were null the comparison would be null-vs-null and prove
    # nothing, so the fixture's own premise is asserted first.
    assert all(row["rev"] for row in want), want

    for entry, row in zip(DECLARED_CONTEXT, want):
        witness = _git(
            ["hash-object", "--no-filters", str(repo / entry["path"])], repo
        ).stdout.strip()
        assert witness == row["rev"], (entry, witness, row)

    for key in ("parent", "child"):
        manifest = control[key].manifest()
        assert compare_manifest_rows(want, manifest) == [], (key, manifest["files"])


def test_a3_a_null_manifest_does_not_read_as_success(tmp_path):
    """Attack A3, now REACHABLE: every declared ref resolves to a missing file.

    A3 scored green before this existed, but it passed through a hole — the control's
    plan declared no `context_refs` at all, so there was no row that *could* go null. A
    fixture that cannot reach the failing condition is as vacuous as a predicate that
    cannot discriminate, so the condition is reached here deliberately and what happens
    is asserted rather than assumed.

    **The deliberate finding, stated in full.** `context-manifest-ref` remains CORRECT
    under A3, and that is not a gap: the field is a byte-pin over the manifest's own
    bytes, the bytes really did change, and the harness's independently computed OID
    tracks them. What A3 was reaching for is a level down — whether the manifest's ROWS
    are honest — and that is covered here by (1) and (2), not by the pin.
    """
    repo = tmp_path / "a3-repo"
    repo.mkdir()
    _git(["init", "-q", "-b", "main"], repo)
    _git(["config", "user.email", "control@example.invalid"], repo)
    _git(["config", "user.name", "control"], repo)
    # Deliberately absent: neither declared file is created in this repo.
    for entry in DECLARED_CONTEXT:
        assert not (repo / entry["path"]).exists(), entry

    path = repo / ".agent-work" / "a3-null" / "spine.json"
    _write_json(path, _plan("a3-null", tmp_path / "ok.flag", child=None))
    run = _ControlRun(path, repo, "a3-null", role="commander")
    session = ["--session-id", "sess-a3-null"]
    run._run("claim", *session, "--claimed-by", "commander", "--worktree", ".")
    run._run("start", "g1", *session)  # the seam emits g1's manifest right here
    manifest = run.manifest("g1")

    # (1) The declaration was HONOURED, not dropped. "declared but not delivered" and
    #     "never declared" are different facts, and only the row keeps them apart.
    assert [(r["root"], r["path"], r["rev"]) for r in manifest["files"]] == [
        ("repo", "seed.txt", None),
        ("repo", "changed_by_the_run.txt", None),
    ], manifest["files"]
    assert expected_rows(repo) == manifest["files"]  # the harness agrees, independently

    # (2) And it does NOT read as success. Compared against what the rows would say had
    #     the files been delivered, every declared path is named.
    delivered = [dict(entry, rev="a" * 40) for entry in DECLARED_CONTEXT]
    assert compare_manifest_rows(delivered, manifest) == [
        "seed.txt", "changed_by_the_run.txt",
    ]

    # (3) The pin itself is still correct, asserted rather than left implied.
    checklist = json.loads(path.read_text(encoding="utf-8"))
    fields = episode_capture.mechanical_fields(checklist, base_dir=path.parent)
    with open(path.parent / "context" / "g1.json", "rb") as handle:
        raw = handle.read()
    assert fields["context-manifest-ref"] == f"ctx-a3-null-g1@{blob_oid(raw)}"


# --------------------------------------------------------------------------- #
# PROOF THE CONTROL CAN FAIL — asserting the SPECIFIC field, never a non-zero exit
# --------------------------------------------------------------------------- #
def test_red_proof_blunt_hardcoded_composer(control, monkeypatch):
    """R1: the composer returns plausible constants. The control must name EVERY field.

    Every constant below passes `apply_episode_delta._validate_create` (isinstance plus
    non-empty), which is exactly why the validator cannot be the oracle and this control
    has to exist.
    """
    parent = control["parent"]
    expected = parent.expectations(control["staged"])
    monkeypatch.setattr(
        episode_capture,
        "mechanical_fields",
        lambda checklist, base_dir=None: {
            "run": "some-run",
            "project": "some-project",
            "role": "implementer",
            "spine-step": "g1",
            "context-manifest-ref": "ctx-some-run-g1@" + "0" * 40,
            "refusals": 0,
            "reopens": 0,
            "rework-count": 0,
            "failed-commands": 0,
            "artifact-ref": [],
        },
    )
    assert compare_fields(expected, parent.compose()) == list(MECHANICAL_GROUP)


def test_red_proof_sharp_drops_exactly_one_derivation(control, monkeypatch):
    """R2: drop EXACTLY ONE derivation. The control must name EXACTLY that field.

    `failed_command_count` is forced to a constant `0` — a value the store's validator
    accepts without complaint and no downstream reader can tell from a real one.
    """
    parent = control["parent"]
    expected = parent.expectations(control["staged"])
    monkeypatch.setattr(episode_capture, "failed_command_count", lambda task: 0)
    assert compare_fields(expected, parent.compose()) == ["failed-commands"]


def test_red_proof_sharp_fabricated_role(control, monkeypatch):
    """R3: the REFUSAL assertions must be falsifiable too, or they are the vacuum.

    `_lease_role` is forced to return a plausible constant on the unclaimed child. The
    field is now PRESENT where the honest reading is absent, and the control must name
    exactly `role` — proving `test_unclaimed_child_topology_...` is not passing merely
    because a missing field is easy to not-see.
    """
    child = control["child"]
    expected = child.expectations(control["staged"])
    monkeypatch.setattr(episode_capture, "_lease_role", lambda checklist: "implementer")
    assert compare_fields(expected, child.compose()) == ["role"]


def test_red_proof_sharp_inflated_reopens(control, monkeypatch):
    """R4: run-scoped `reopens` and step-scoped `rework-count` are two facts, not one
    written twice. Forcing `reopen_total` to the step-scoped value must be caught."""
    parent = control["parent"]
    expected = parent.expectations(control["staged"])
    monkeypatch.setattr(episode_capture, "reopen_total", lambda checklist: 1)
    assert compare_fields(expected, parent.compose()) == ["reopens"]


# --------------------------------------------------------------------------- #
# C5/C6 — CROSS-RUN RETRIEVAL, and the synthetic consolidation is THROWAWAY
#
# `capability:cross-run-retrieval` is the acceptance surface: an episode written by one
# run must be findable from another run's episode. `neighbours()` is that search, and
# the property that matters is that it SURVIVES CONSOLIDATION — retiring a member of a
# cluster into a consolidated episode must not sever the cluster, or #308's
# consolidation pass could not walk back from an archived member.
#
# Everything below runs in a TEMPORARY store. `constraint:throwaway-consolidation`: a
# test artifact must never become canon, and the real first consolidation is #308. Belt
# and braces — the temp store is one half, `test_canon_episode_store_untouched` the
# other.
# --------------------------------------------------------------------------- #
import apply_episode_delta  # noqa: E402
import query_episodes  # noqa: E402


def _create_op(run: str, role: str, step: str, artifact_refs: list[str]) -> dict:
    """A create op. `id` is deliberately absent — the writer ASSIGNS it (EPISODE_STORE
    section 2, zero agent effort) and `_validate_create` refuses a supplied one."""
    return {
        "op": "create",
        "mechanical": {
            "run": run,
            "project": "constellation-skills",
            "role": role,
            "spine-step": step,
            "context-manifest-ref": "ctx-" + run + "-" + step + "@" + "a" * 7,
            "refusals": 0,
            "reopens": 0,
            "rework-count": 0,
            "failed-commands": 0,
            "artifact-ref": artifact_refs,
        },
        "agent_supplied": {
            "task-intent": {"strength": "strong", "statement": "Seed a retrieval fixture."},
            "expected-behavior": {"strength": "medium",
                                  "statement": "Neighbours link on shared join keys."},
            "observed-behavior": {"strength": "strong", "statement": "They do."},
            "impact-cost": {"strength": "medium", "statement": "None; fixture only."},
            "workaround": {"strength": "strong", "statement": "none."},
        },
    }


@pytest.fixture(scope="module")
def seeded_store(tmp_path_factory):
    """A temp store seeded through the SANCTIONED WRITER, never by hand-placing files.

    The cluster joins on a shared `artifact-ref`; the outsider shares neither join key.
    `role+spine-step` is ALWAYS a join key, so every member carries a distinct role/step
    pair — otherwise the cluster would link on that instead and the fixture would prove
    nothing about `artifact-ref`.
    """
    root = tmp_path_factory.mktemp("epistore") / "episodes"
    apply_episode_delta.ensure_store_layout(root)
    shared = "shared/alpha.md"
    log = apply_episode_delta.apply_delta(
        root,
        {
            "work_id": "g3-retrieval-fixture",
            "ops": [
                _create_op("cluster", "implementer", "g1", [shared, "only/one.md"]),
                _create_op("cluster", "reviewer", "g2", [shared]),
                _create_op("cluster", "commander", "g3", [shared]),
                _create_op("outsider", "cartographer", "z9", ["unrelated/beta.md"]),
            ],
        },
    )
    return {"root": root, "log": log}


def test_cross_run_retrieval_links_episodes_across_runs(seeded_store):
    """The acceptance surface: an episode written by one run is reachable from another
    episode of that cluster, and the unrelated run is NOT dragged in."""
    root = seeded_store["root"]
    assert sorted(query_episodes.enumerate_episode_ids(root)) == [
        "cluster-001", "cluster-002", "cluster-003", "outsider-001",
    ]
    assert query_episodes.neighbour_ids(root, "cluster-001") == ["cluster-002", "cluster-003"]
    # Proof the join discriminates rather than matching everything to everything: the
    # outsider has NO neighbours, so a full result and an empty result are both observable.
    assert query_episodes.neighbour_ids(root, "outsider-001") == []


def test_rhyme_search_survives_consolidation(seeded_store):
    """Mark one cluster member CONSOLIDATED, then confirm rhyme-search still finds its
    neighbours. This is the property #308's consolidation pass depends on."""
    root = seeded_store["root"]
    before = query_episodes.neighbour_ids(root, "cluster-002")
    assert before == ["cluster-001", "cluster-003"]

    apply_episode_delta.apply_delta(
        root,
        {
            "work_id": "g3-retrieval-fixture",
            "ops": [{
                "op": "retire",
                "id": "cluster-002",
                "reason": "throwaway synthetic consolidation for #305 g3; #308 owns the real one",
                "consolidated-into": "cluster-001",
            }],
        },
    )

    # The anchor is fetched BY ID, so a consolidated (archived) episode can still be
    # walked back from — its surviving neighbours are intact.
    after = query_episodes.neighbour_ids(root, "cluster-002")
    assert after == before, (before, after)

    # And from the other direction: the ordinary set no longer lists the consolidated
    # member, while the history-inclusive set still reaches it. Both readings are
    # asserted, so "it vanished" and "it moved" stay distinguishable.
    assert query_episodes.neighbour_ids(root, "cluster-001") == ["cluster-003"]
    assert query_episodes.neighbour_ids(root, "cluster-001", include_retired=True) == [
        "cluster-002", "cluster-003",
    ]
    assert query_episodes.fetch_episode("cluster-002", root).consolidated_into == "cluster-001"


def test_321_observation_where_a_handed_id_is_validated(seeded_store):
    """#321: the store validates ids it LISTS but not every id it is HANDED.

    Recorded as an OBSERVATION for the Commander to rule on — deliberately NOT fixed here.
    """
    root = seeded_store["root"]
    # (1) create: there is no handed id at all. Supplying one is REFUSED outright and the
    # writer assigns the id itself, so the unvalidated-handed-id path does not exist here.
    with pytest.raises(apply_episode_delta.EpisodeDeltaError):
        op = _create_op("x", "r", "s", [])
        op["id"] = "whatever"
        apply_episode_delta.validate_delta({"work_id": "w", "ops": [op]})
    # (2) retire: the handed id IS validated, against ID_RE, before anything is applied.
    with pytest.raises(apply_episode_delta.EpisodeDeltaError):
        apply_episode_delta.validate_delta(
            {"work_id": "w", "ops": [{"op": "retire", "id": "NOT A VALID ID", "reason": "r"}]}
        )
    # (3) the READ path is where a handed id goes unvalidated: `fetch_episode` resolves
    # whatever string it is given and answers None rather than refusing, so "no such
    # episode" and "you handed me nonsense" read identically.
    assert query_episodes.fetch_episode("NOT A VALID ID", root) is None
    with pytest.raises(query_episodes.EpisodeNotFound):
        query_episodes.neighbours(root, "NOT A VALID ID")


def test_canon_episode_store_untouched(seeded_store):
    """Belt and braces (b): the tracked store's blob OIDs are READ and compared, not
    assumed. Empty-vs-empty passes a naive equality check, so the store's NON-emptiness
    is asserted first — this repo's `episodes/active/` carries real episodes plus
    `.gitkeep`, and that is what makes the comparison meaningful.

    **The property is worktree-vs-index, and only that.** `git status --porcelain` also
    reports index-vs-HEAD, so a `git add episodes/...` staged ahead of a real capture's
    commit — the normal `write -> git add -> suite -> commit` order the archive-phase
    gate requires — read as "dirty" under the old predicate though nothing untracked or
    unstaged existed. `git diff --name-only` (a tracked file changed but not staged) and
    `git ls-files --others --exclude-standard` (a file present but never staged at all)
    are the pair that stays worktree-vs-index only: a stray write or a stray untracked
    file still fails either one; a legitimate capture that is staged but not yet
    committed fails neither, because staging moves it into the index these commands
    compare against, not past it.
    """
    listing = subprocess.run(
        ["git", "ls-files", "-s", "episodes/active/"],
        cwd=str(REPO_ROOT), capture_output=True, text=True, encoding="utf-8",
    ).stdout
    tracked = {ln.split("\t")[-1]: ln.split()[1] for ln in listing.splitlines() if ln.strip()}
    assert len(tracked) >= 2, f"canon store looks empty; the comparison would be vacuous: {tracked}"
    assert any(name.endswith(".md") for name in tracked), tracked
    # Nothing this module wrote lives here: the whole exercise ran in a temp store,
    # outside the repository.
    assert REPO_ROOT not in seeded_store["root"].parents
    # Worktree-vs-index, half one: a tracked file edited but left unstaged.
    unstaged = subprocess.run(
        ["git", "diff", "--name-only", "episodes/"],
        cwd=str(REPO_ROOT), capture_output=True, text=True, encoding="utf-8",
    ).stdout.strip()
    assert unstaged == "", f"canon episode store has unstaged edits: {unstaged}"
    # Worktree-vs-index, half two: a file present in the tree but never staged at all.
    untracked = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard", "episodes/"],
        cwd=str(REPO_ROOT), capture_output=True, text=True, encoding="utf-8",
    ).stdout.strip()
    assert untracked == "", f"canon episode store has untracked files: {untracked}"
