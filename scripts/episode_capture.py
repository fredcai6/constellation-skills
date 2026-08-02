#!/usr/bin/env python
"""Assembly seam: the context manifest as a **byproduct of starting a step**.

`context_manifest.py` knows how to build the record of *what was made available to
the agent running this step*. It deliberately ships no CLI verb and no opinion
about when it runs. This module is the other half: the one place that decides
**when** a manifest is taken, **which roots** the declaration resolves against, and
**where** the file lands — and it is wired into `checklist_engine.start()` and
`checklist_engine.reopen()`, the only two verbs that put a task into
`in-progress`.

Why those two and not a `dispatch()` chokepoint: `advance()` refuses a task that
is not `in-progress`, so on a gated spine every gate that ever advances has been
through `start` or `reopen` first. The unskippability is already in the status
machine — this seam only has to sit on it, which costs one verb of blast radius
instead of every verb. It is also the semantically right place: the manifest's own
docstring says it records what was available to the agent running *this step*, and
step activation is exactly that moment.

Three rules carry the design.

**Write-if-absent, never overwrite.** The manifest is a per-step *delivery
snapshot*, not a live index. If any later call rewrote it, it would silently
become "whatever happened to be on disk at the last verb call" and stop being the
record it exists to be. Pinning a manifest by revision is only honest because the
bytes behind that revision cannot change underneath it.

**Fail-soft, because this now runs inside every `start`.** A crash here would
break every verb for every concurrent run on this engine, and the producer has
legitimate raising paths (a malformed declaration, an unknown root token, a
checklist whose items are all terminal). So `emit_step_manifest` catches broadly.
That is a deliberate, documented departure from narrow-except style, made because
the blast radius of the alternative is the whole engine, not because the failure
modes are unknown.

**Fail-soft is not fail-silent.** A swallowed failure that wrote nothing would be
indistinguishable from a step nobody ever started, and those two readings must
stay tellable apart — a non-reading is not an uncollected one. So a failed emit
writes a *stub* recording what failed, carrying `emit_error` and `files: null`
(not `files: []`, which is the real reading "this step declared nothing").
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

sys.path.insert(0, str(Path(__file__).resolve().parent))
from agent_work_root import durable_root  # noqa: E402  — the CHECKOUT root helper.
# `durable_agent_work()` is the neighbouring one and is the WRONG one here: the
# single shipped `durable` declaration is `.agent-work/LESSONS.md`, which that
# helper would double-nest to `.agent-work/.agent-work/LESSONS.md`.

#: The installed skill directory — the parent of the `scripts/` directory this file
#: sits in, which is where `references/global-*.md` live in an installed skill.
#: Derived from `__file__` rather than configured, so it is right wherever the
#: skill was installed and there is no flag anyone can get wrong.
SKILL_ROOT = Path(__file__).resolve().parent.parent


def repo_root(base_dir: Any = None) -> Path:
    """The worktree root `repo`-rooted declarations resolve against.

    `docs/agents/ORCHESTRATOR_CONTEXT.md` and its neighbours live here, so this must
    be the worktree the run is happening in — not the main checkout, which is what
    `durable_root` deliberately resolves to instead.

    Any failure (no git on PATH, `base_dir` outside a repository, `base_dir` not a
    directory) falls back to `base_dir` itself rather than raising or guessing. That
    mirrors `agent_work_root.durable_root`'s own never-raise contract, and it keeps
    the non-repository case a manifest full of `rev: null` rows — a visible,
    truthful "these files were not there" — instead of a broken verb.
    """
    base = Path(base_dir) if base_dir is not None else Path.cwd()
    base = Path(os.path.abspath(os.fspath(base)))
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=str(base), capture_output=True, text=True, encoding="utf-8",
        )
    except OSError:
        return base
    top = (proc.stdout or "").strip()
    if proc.returncode != 0 or not top:
        return base
    return Path(os.path.abspath(top))


def resolve_roots(base_dir: Any = None) -> dict[str, Path]:
    """The three root tokens a `context_refs` entry may name, resolved mechanically.

    Mechanically is the point: there is no flag and no configuration for these. A
    flag would move the burden of getting them right onto every invoker, and the
    failure it invites is silent — a wrong root does not raise anywhere in the
    producer, it yields a structurally valid manifest with every `rev` null.

    `durable` is resolved from the REPO ROOT, never from `base_dir` directly, and
    that argument is load-bearing rather than incidental. `durable_root(start)`
    redirects to the main checkout only for a linked worktree with no active Admiral
    epic lease; on **every** other path — plain checkout, active epic lease, no git,
    any git error — its documented contract is to return `start` *unchanged*. Handed
    the checklist's own directory (`<repo>/.agent-work/<work-id>`), those fallback
    paths therefore make the durable root `<repo>/.agent-work/<work-id>`, and the one
    shipped declaration `.agent-work/LESSONS.md` lands on
    `<repo>/.agent-work/<work-id>/.agent-work/LESSONS.md` — a path that does not
    exist, which the producer records as `rev: null` without raising. Handing it the
    repo root makes every fallback resolve to the worktree root, which is correct.

    Keyed in `context_manifest.ROOT_TOKENS` order so `run.roots` stays deterministic.
    """
    repo = repo_root(base_dir)
    return {
        "skill": SKILL_ROOT,
        "repo": repo,
        "durable": durable_root(repo),
    }


def manifest_root(base_dir: Any) -> Path:
    """The `agent_work_root` handed to `context_manifest.manifest_path()`.

    `manifest_path` composes `<root>/<work-id>/context/<step>.json`, and a run's
    checklist lives at `<agent-work>/<work-id>/spine.json` — so the root is the
    checklist directory's PARENT, and the manifest lands beside the spine it
    describes, inside the same work area. Deliberately not the durable root: the
    manifest belongs to one run, and durable resolution is shared across every
    linked worktree of a repo, where concurrent runs would collide.
    """
    return Path(os.path.abspath(os.fspath(Path(base_dir)))).parent


def emit_step_manifest(
    checklist: Mapping[str, Any], iid: str, base_dir: Any = None
) -> Path | None:
    """Take this step's delivery snapshot. Called by the engine, never by an agent.

    Returns the manifest path, or `None` when nothing was written. MUST NOT raise,
    and MUST NOT change any verb's exit code or output — see the module docstring
    for why the except is broad.

    Call it AFTER the status mutation. The step is selected by the engine's own
    `active_id()`, and before `reopen` flips a complete gate back to `in-progress`
    that selector is still pointing at a later gate — so calling early would record
    the wrong step.

    A `base_dir` of `None` writes nothing at all. Without the checklist's location
    there is no work area to write into, and inventing one would scatter the record
    outside the run it belongs to; `checklist_engine.main()` always supplies it, so
    the CLI path an agent actually drives always emits.
    """
    if base_dir is None:
        return None
    try:
        # Imported here, not at module scope: `context_manifest` imports
        # `checklist_engine`, which imports this module — a top-level import would
        # close that cycle and break the engine at import time.
        import context_manifest as cm

        roots = resolve_roots(base_dir)
        manifest = cm.build_manifest(checklist, roots)
        destination = cm.manifest_path(
            manifest_root(base_dir), checklist.get("work_id"), manifest["step"]
        )
        # Write-if-absent: the snapshot belongs to the moment the step activated.
        # Checked against the path derived from the manifest we just built, so the
        # guard and the write can never disagree about which file they mean.
        if destination.exists():
            return destination
        return cm.write_manifest(manifest, destination)
    except Exception as exc:  # noqa: BLE001 — deliberate; see the module docstring.
        # Broad by design: this runs inside every `start`, on an engine other runs
        # are live on, and a manifest is provenance, never a precondition. Anything
        # that escaped here would break a verb that has nothing to do with capture.
        return _write_failure_stub(checklist, iid, base_dir, exc)


def _write_failure_stub(
    checklist: Mapping[str, Any], iid: str, base_dir: Any, exc: BaseException
) -> Path | None:
    """Record that the reading was attempted and failed, rather than writing nothing.

    "No file here" and "the record could not be taken" are different facts, and a
    later reader has no other way to tell them apart. The stub is deliberately NOT a
    valid manifest: it carries `emit_error` and `files: null`, so nothing can mistake
    it for a real delivery record or for the legitimate empty one (`files: []`).

    Never raises, and never overwrites an already-taken manifest. If it cannot write
    either — no `context_manifest` on the path at all — it returns `None`, which is
    the honest reading: the capture machinery is simply not installed here.
    """
    try:
        import context_manifest as cm

        destination = cm.manifest_path(
            manifest_root(base_dir), checklist.get("work_id"), iid
        )
        if destination.exists():
            return destination
        return cm.write_manifest(
            {
                "step": iid,
                "files": None,
                "emit_error": {
                    "error": type(exc).__name__,
                    "message": str(exc),
                },
                "run": {
                    "work_id": checklist.get("work_id"),
                    "generated_at": datetime.now(timezone.utc).strftime(
                        "%Y-%m-%dT%H:%M:%SZ"
                    ),
                },
            },
            destination,
        )
    except Exception:  # noqa: BLE001 — the fallback must not itself break a verb.
        return None


if __name__ == "__main__":
    # No CLI verb, for the same reason `context_manifest.py` has none: the manifest
    # is a byproduct of the engine's own control flow, not something anyone invokes.
    # This prints the resolved roots, which is a diagnostic, not an interface.
    print(json.dumps({k: str(v) for k, v in resolve_roots(Path.cwd()).items()}, indent=2))
