#!/usr/bin/env python
"""Deterministic projection substrate: what was made available to an agent, and at
which revision.

The manifest this module produces is a record of **delivery, not use**. It says
"these files, in this order, at these revisions, were made available to the agent
running this step." It is deliberately *not* an access trace, not transcript
analysis, and not an archive of file contents — a design that widens toward
proving *use* is a different artifact, not a better version of this one.

Three properties carry the whole design:

1. **Revision identity is the git blob OID of the LF-normalised bytes**, computed
   in-process (`rev`). No `git` subprocess, and deliberately **no commit SHA**: a
   commit SHA lies about a dirty tree and says nothing at all about untracked or
   gitignored files. One function covers tracked, dirty, untracked, gitignored and
   out-of-repo files with no case analysis, and it structurally eliminates CRLF —
   this corpus's largest named irreproducibility source — rather than excluding it.
2. **Declaration order is content.** There are no globs, no directory patterns and
   no directory enumeration anywhere in this module, and paths are never sorted.
   A glob would import filesystem ordering — the second named irreproducibility
   source — into the record for no benefit. Doctrine has reading precedence
   (inherited global doctrine, *then* project deltas), so the declared order is
   part of what is being recorded.
3. **`/run` is the entire exclusion set.** Every legitimately-varying fact —
   timestamps, run ids, absolute roots, host facts — lives in the `run` subtree and
   nowhere else. Determinism is therefore checked by comparing everything outside
   one JSON pointer; a new varying field cannot become "accidentally content",
   because it has to be placed in one subtree or the other.

The single impure edge is the injected `reader` callable, which is what lets a
test point the whole producer at a fixture tree.

There is intentionally **no CLI verb** here: the manifest is a JSON file, and a
verb would touch the engine's persistence control flow for a convenience print.
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Callable, Mapping, Sequence

sys.path.insert(0, str(Path(__file__).resolve().parent))
from checklist_engine import active_id  # noqa: E402  — THE selector, never a second one

# Independent of the engine's `_STATE_CONTRACT_VERSION` (both read 1 today, and
# they are free to diverge) — same versioning idiom, different contract. Anything
# storing this downstream should name it so the two cannot be confused.
_MANIFEST_CONTRACT_VERSION = 1

#: The declaration key on a spine/plan task object. Optional: a task without it
#: contributes nothing, so every existing spine keeps working untouched.
DECLARATION_KEY = "context_refs"

#: Root tokens a declaration entry may name. Resolved through a caller-supplied
#: mapping, so absolute (environment-varying) paths never reach the content.
ROOT_TOKENS = ("skill", "repo", "durable")

#: The entire exclusion set for the determinism comparison — one JSON pointer.
RUN_POINTER = "/run"


def rev(data: bytes) -> str:
    """Git blob OID of `data` after LF normalisation.

    Equal to `git hash-object <path>` and `git rev-parse HEAD:<path>` for a tracked
    clean file under this repo's `.gitattributes` (`* text=auto`) with
    `core.autocrlf=true` — but only for content git actually normalises, and that
    takes **two** conditions, not one:

    1. **No attribute exemption.** A `-text` or `binary` attribute in
       `.gitattributes` makes git stop normalising that path.
    2. **No content-triggered refusal.** Under `text=auto` git also declines on the
       bytes alone, with no `.gitattributes` entry involved anywhere: a NUL byte
       (git auto-detects binary) or a lone CR (a carriage return not followed by a
       line feed, where normalising would not round-trip). For such content git
       stores the raw bytes, while this function normalises unconditionally — so it
       deliberately diverges there.

    The gate's `.gitattributes` grep pins condition 1 **only**; it structurally
    cannot see condition 2, which is content rather than configuration. That half is
    pinned instead by
    `RevIsGitBlobOid.test_rev_diverges_from_git_for_content_git_refuses_to_normalise`,
    which asserts the divergence rather than assuming it away. No file in any root a
    `context_refs` can name is in that class today — this corpus is markdown and
    JSON written under `* text=auto` — but the boundary is now watched mechanically
    instead of being stated more narrowly than it is.
    """
    body = data.replace(b"\r\n", b"\n")
    return hashlib.sha1(b"blob %d\x00" % len(body) + body).hexdigest()


class DeclarationError(ValueError):
    """A `context_refs` entry is malformed, names an unknown root, or escapes it.

    Raised rather than skipped: a declaration the producer cannot honour must fail
    visibly, never degrade into a plausible-looking manifest that is missing a row.
    """


# --------------------------------------------------------------------------- #
# The single impure edge.
#
# Everything else in this module is a pure function of (checklist, roots, reader).
# Injecting a different reader is what lets a test point the whole producer at a
# fixture tree without touching the real filesystem.
# --------------------------------------------------------------------------- #
def read_bytes(abs_path: str) -> bytes | None:
    """Read `abs_path`, or return None if it does not exist.

    Absence is normal here — a declared doctrine overlay is legitimately absent in
    a skill-source repo — so it yields `rev: null` with the row retained. A file
    that *is* there but cannot be read (permissions, is-a-directory, a path
    component that is not a directory) raises, so that `null` keeps meaning exactly
    one thing: the file was not there.
    """
    try:
        with open(abs_path, "rb") as handle:
            return handle.read()
    except FileNotFoundError:
        return None


def resolve(entry: Mapping[str, Any], roots: Mapping[str, Any]) -> str:
    """Absolute filesystem path for one declaration entry.

    The returned path is for *reading only* — it is environment-varying and never
    reaches the manifest content, where the row keeps the root token and the
    declared relative path instead.
    """
    if not isinstance(entry, Mapping):
        raise DeclarationError(f"declaration entry must be an object, got {entry!r}")
    missing = [key for key in ("root", "path") if key not in entry]
    if missing:
        raise DeclarationError(f"declaration entry missing {missing}: {entry!r}")
    unknown = [key for key in entry if key not in ("root", "path", "required")]
    if unknown:
        raise DeclarationError(f"declaration entry has unknown keys {unknown}: {entry!r}")

    token = entry["root"]
    if token not in ROOT_TOKENS:
        raise DeclarationError(f"unknown root token {token!r}; expected one of {ROOT_TOKENS}")
    if token not in roots:
        raise DeclarationError(f"root {token!r} is declared but the caller supplied no mapping for it")

    declared = entry["path"]
    if not isinstance(declared, str) or not declared.strip():
        raise DeclarationError(f"declaration path must be a non-empty string, got {declared!r}")
    if "\\" in declared:
        raise DeclarationError(f"declaration path must be posix-relative, got {declared!r}")
    # A colon never survives as itself. `C:/Windows/win.ini` looks relative to every
    # posix-shaped guard below — `PurePosixPath` reports it not-absolute with parts
    # ('C:', 'Windows', 'win.ini') — and `ntpath.join` then folds it to
    # `<root>\Windows\win.ini`, which is inside the root, so the escape guard would
    # pass it too. The row would then record a path that is NOT the path that was
    # read, which defeats the record's whole purpose. Non-leading colons are the
    # same hazard in a different dress: `doctrine.md:notes` is an NTFS alternate
    # data stream on Windows and an ordinary filename on POSIX, so the declaration
    # would be content-divergent across operating systems. Rejected, not folded.
    if ":" in declared:
        raise DeclarationError(
            f"declaration path must not contain ':' (drive letters and NTFS streams "
            f"resolve differently per-OS): {declared!r}"
        )
    # A glob is never expanded here — but silently recording `docs/*.md` as one
    # absent file would be plausible wrong output, so a pattern fails visibly
    # instead. Declaration order is content; filesystem order is not admissible.
    if any(ch in declared for ch in "*?[]"):
        raise DeclarationError(
            f"declaration path must be a literal path, not a pattern: {declared!r}"
        )
    relative = PurePosixPath(declared)
    if relative.is_absolute() or ".." in relative.parts:
        raise DeclarationError(f"declaration path must stay inside its root, got {declared!r}")

    base = os.path.abspath(str(roots[token]))
    target = os.path.abspath(os.path.join(base, *relative.parts))
    # Belt and braces on the platform's own join: the `..` rejection above is the
    # primary guard, and the drive-letter/stream forms are rejected outright rather
    # than left to this check — it cannot see them, because they fold to a path that
    # really is inside the root. What this catches is whatever the string form let
    # through after the platform's join and normalisation ran (odd separators, a
    # component the OS collapses), so an escape fails visibly instead of reading a
    # file the row does not name.
    if os.path.normcase(target) != os.path.normcase(base) and not os.path.normcase(
        target
    ).startswith(os.path.normcase(base) + os.sep):
        raise DeclarationError(f"declaration path escapes root {token!r}: {declared!r}")
    return target


def declaration_of(task: Mapping[str, Any]) -> tuple[Mapping[str, Any], ...]:
    """The task's ordered `context_refs`, or an empty tuple.

    Absent is the normal case and is never an error: every spine authored before
    this field existed keeps working, and simply projects nothing.
    """
    declared = task.get(DECLARATION_KEY)
    if declared is None:
        return ()
    if not isinstance(declared, Sequence) or isinstance(declared, (str, bytes)):
        raise DeclarationError(f"{DECLARATION_KEY} must be an ordered list, got {declared!r}")
    return tuple(declared)


def rows(
    declaration: Sequence[Mapping[str, Any]],
    roots: Mapping[str, Any],
    reader: Callable[[str], bytes | None] = read_bytes,
) -> list[dict]:
    """One `{root, path, rev}` row per declared entry, in declaration order.

    Declaration order is emitted verbatim — never sorted, never enumerated from the
    filesystem. `required` stays in the declaration and is deliberately not copied
    into the row: the manifest records what was delivered, not what was asked for.
    """
    out: list[dict] = []
    for entry in declaration:
        target = resolve(entry, roots)
        data = reader(target)
        out.append(
            {
                "root": entry["root"],
                "path": entry["path"],
                "rev": None if data is None else rev(data),
            }
        )
    return out


def run_facts(
    roots: Mapping[str, Any],
    work_id: str | None = None,
    session_id: str | None = None,
    now: datetime | None = None,
) -> dict:
    """The `/run` subtree: every legitimately-varying fact, and nothing else.

    Absolute roots, timestamps, host facts and run identity all live here. Nothing
    varying may live outside this subtree — that is what makes the determinism
    comparison a single-pointer exclusion instead of a maintained field list.
    """
    stamp = now if now is not None else datetime.now(timezone.utc)
    return {
        "work_id": work_id,
        "session_id": session_id,
        "generated_at": stamp.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        # ROOT_TOKENS order, not sorted() and not dict order — deterministic without
        # importing any ordering the declaration did not ask for.
        "roots": {t: Path(roots[t]).as_posix() for t in ROOT_TOKENS if t in roots},
        "host": {
            "platform": sys.platform,
            "python": platform.python_version(),
            "cwd": Path.cwd().as_posix(),
        },
    }


def build_manifest(
    checklist: Mapping[str, Any],
    roots: Mapping[str, Any],
    reader: Callable[[str], bytes | None] = read_bytes,
    step: str | None = None,
    run: Mapping[str, Any] | None = None,
) -> dict:
    """The one envelope, for the checklist's active step.

    The step is selected with the engine's own `active_id()` — never a second
    selector — unless the caller pins one explicitly. `run` defaults to
    `run_facts(roots, work_id=checklist['work_id'])`.
    """
    selected = active_id(checklist) if step is None else step
    if selected is None:
        raise ValueError("no active step: every item on this checklist is terminal")
    task = checklist.get("tasks", {}).get(selected)
    if task is None:
        raise ValueError(f"step {selected!r} is not a task on this checklist")

    return {
        "contract": _MANIFEST_CONTRACT_VERSION,
        "step": selected,
        "files": rows(declaration_of(task), roots, reader),
        "run": dict(run) if run is not None else run_facts(roots, work_id=checklist.get("work_id")),
    }


def content(manifest: Mapping[str, Any]) -> dict:
    """The manifest minus the `/run` subtree — the part that must be identical
    across environments. This is the *only* exclusion; anything else that has to be
    masked to make a determinism comparison pass belongs in `/run` instead, and its
    presence outside `/run` is a design defect, not a test to loosen."""
    return {k: v for k, v in manifest.items() if k != "run"}


def encode(obj: Any) -> str:
    """The one canonical encoder. No second encoder, no stored digest to disagree
    with its own bytes."""
    return json.dumps(obj, indent=2, ensure_ascii=False) + "\n"


def manifest_path(agent_work_root: Any, work_id: str, step: str) -> Path:
    """`<agent-work-root>/<work-id>/context/<step>.json`."""
    return Path(agent_work_root) / str(work_id) / "context" / f"{step}.json"


def write_manifest(manifest: Mapping[str, Any], path: Any) -> Path:
    """Write the manifest with LF line endings, always.

    `newline="\\n"` is load-bearing on Windows, not hygiene: without it Python
    translates every `\\n` to `\\r\\n` on write, and the file this record is about
    would not survive its own identity function.
    """
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with open(destination, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(encode(manifest))
    return destination


def produce(
    checklist: Mapping[str, Any],
    roots: Mapping[str, Any],
    agent_work_root: Any,
    reader: Callable[[str], bytes | None] = read_bytes,
    run: Mapping[str, Any] | None = None,
) -> tuple[Path, dict]:
    """Build the active step's manifest and write it. Returns `(path, manifest)`."""
    manifest = build_manifest(checklist, roots, reader=reader, run=run)
    destination = manifest_path(agent_work_root, checklist.get("work_id"), manifest["step"])
    return write_manifest(manifest, destination), manifest
