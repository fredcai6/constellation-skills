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

**That guarantee is scoped to gated checklists, and the scope is load-bearing.**
A **survey** does not have it: `record()` carries no `in-progress` guard, so a
survey is visited and consolidated straight from `pending` and this seam never
fires. Reviewer, Cartographer, Scout and Curator all drive surveys, so surveys are
not a corner case — they are simply outside what `start`/`reopen` can cover.
Stated here because the honest claim is "unskippable on a gated spine", not
"unskippable", and a reader who takes the wider reading will believe a survey run
left a delivery record when none exists. Covering surveys means giving `record()`
the same guard, which is a design change to the survey lifecycle and deliberately
not made here.

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
# `durable_agent_work()` is the neighbouring one and is the WRONG one here: it
# returns `<root>/.agent-work`, so any `.agent-work/…`-relative durable declaration
# would double-nest to `.agent-work/.agent-work/…`. (No `durable` declaration ships
# in the corpus today — #308 cut the lessons read path, which was the only one — so
# the trap is currently unexercised by shipped data and correspondingly silent.)

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


def project_name(base_dir: Any = None) -> str | None:
    """The `project` mechanical field: the REPOSITORY's name, identical from every
    worktree — or `None`, refusing, when it cannot be sourced honestly.

    Sourced from the parent of `git rev-parse --git-common-dir`, which is repository
    *topology*: in a linked worktree it names the main checkout's `.git` regardless of
    any lease, and in a plain checkout it is `.git`, whose parent is the checkout root.

    **Deliberately NOT `durable_root()`, and the difference is not academic.** That
    helper answers a *writability* question, and it returns the worktree unchanged
    whenever an active Admiral epic lease exists (its own comment: "the main checkout
    is fenced read-only, so honor the worktree") — which is the condition every
    commander in an epic runs under. Sourcing `project` there gives the same repository
    a different name every epic (`e298-305` rather than `constellation-skills`), which
    is exactly the drift this field exists to prevent. Measured, not reasoned:
    `durable_root()` in this repo's own epic worktree resolves to the worktree.

    Refuses rather than guessing. `repo_root()` above may fall back to `base_dir`
    because a manifest full of `rev: null` is a visible, truthful non-reading — but
    there is no such visible failure here. A worktree-derived project name is a
    *plausible* value that silently poisons the one join meant to survive
    `git worktree remove`, and a fabricated mechanical fact is worse than an absent one.
    """
    base = Path(base_dir) if base_dir is not None else Path.cwd()
    base = Path(os.path.abspath(os.fspath(base)))
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "--git-common-dir"],
            cwd=str(base), capture_output=True, text=True, encoding="utf-8",
        )
    except OSError:
        return None  # no git on PATH, or base is not a usable directory
    common = (proc.stdout or "").strip()
    if proc.returncode != 0 or not common:
        return None  # not a repository
    # `--git-common-dir` is RELATIVE (".git") in a plain checkout and absolute in a
    # linked worktree, so it is resolved against `base` — the directory git was asked
    # from — rather than against this process's cwd, which is not the same thing.
    name = Path(os.path.abspath(os.path.join(str(base), common))).parent.name
    return name or None


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
    paths therefore make the durable root `<repo>/.agent-work/<work-id>`, and a
    declaration like `.agent-work/notes.md` lands on
    `<repo>/.agent-work/<work-id>/.agent-work/notes.md` — a path that does not
    exist, which the producer records as `rev: null` without raising. Handing it the
    repo root makes every fallback resolve to the worktree root, which is correct.
    (No `durable` declaration ships in the corpus today: #308 cut the lessons read
    path, which was the only one. The root token stays, and so does this contract.)

    Keyed in `context_manifest.ROOT_TOKENS` order so `run.roots` stays deterministic.
    """
    repo = repo_root(base_dir)
    return {
        "skill": SKILL_ROOT,
        "repo": repo,
        "durable": durable_root(repo),
    }


def manifest_root(base_dir: Any, work_id: Any = None) -> Path:
    """The `agent_work_root` handed to `context_manifest.manifest_path()`.

    `manifest_path` composes `<root>/<work-id>/context/<step>.json`, and a run's
    checklist lives at `<agent-work>/<work-id>/spine.json` — so the root is the
    checklist directory with the work-id STRIPPED OFF, and the manifest lands beside
    the spine it describes, inside the same work area. Deliberately not the durable
    root: the manifest belongs to one run, and durable resolution is shared across
    every linked worktree of a repo, where concurrent runs would collide.

    "Strip the work-id", not "take the parent", because a work-id may NEST: the
    epic/commander convention writes `epic-418-followon/commander-424`, and
    `manifest_path` re-appends BOTH segments. Stripping only one left the run's
    provenance at
    `.agent-work/epic-418-followon/epic-418-followon/commander-424/context/` — a
    doubled path, one level away from where every other tool looks, written in
    silence because nothing here raises.

    `work_id` is optional and the strip is conditional on the directory actually
    ENDING in it. A checklist that does not sit under its own work-id (scratch
    spines under an evidence directory do not) is a different question than this one,
    and guessing at it is how the doubled path was written in the first place; those
    keep the historical parent-of-base_dir answer exactly.
    """
    base = Path(os.path.abspath(os.fspath(Path(base_dir))))
    segments = [s for s in str(work_id).split("/") if s] if work_id else []
    node, tail = base, []
    for _ in segments:
        tail.append(node.name)
        node = node.parent
    if segments and list(reversed(tail)) == segments:
        return node
    return base.parent


# --------------------------------------------------------------------------- #
# The mechanical field composer (#305 gate g2)
#
# `docs/EPISODE_STORE.md` §4 splits an episode into a MECHANICAL bin ("zero agent
# effort, captured by the harness/engine at write time") and an agent-supplied bin
# of five irreducibly-judgment assertions. This is the mechanical half, and "zero
# agent effort" is meant literally: a field an agent can omit by forgetting is not
# mechanically captured, it is agent-supplied wearing a mechanical label.
#
# **Refuse, never fabricate.** Every field here is either read out of engine state
# or OMITTED. There is no default, no placeholder and no silent `0`. That rule is
# stricter than the store's own validator, deliberately: `_validate_create` is
# `isinstance` plus non-empty, so nine plausible constants pass it cleanly. The
# validator is a shape check on the way to the writer, not an oracle — nothing
# downstream can tell a fabricated mechanical fact from a real one, so the
# fabrication has to be refused HERE or not at all. An absent field is a visible
# gap someone can act on; a wrong one is a lie that reads as data.
# --------------------------------------------------------------------------- #

#: Bumped when the snapshot's own shape changes. Independent of the manifest's
#: contract version — the two records travel together but are not the same record.
MECHANICAL_CONTRACT_VERSION = 1


def _engine():
    """The engine module, imported LAZILY for the same reason `context_manifest` is:
    `checklist_engine` imports this module, so a top-level import would close the
    cycle and break the engine at import time."""
    import checklist_engine

    return checklist_engine


def _lease_role(checklist: Mapping[str, Any]) -> str | None:
    """`role` — the lease's `claimed_by`, or a refusal.

    A lease-less run genuinely has no role to report. Guessing one would put a
    plausible `implementer` on an episode nobody can attribute, which is the exact
    fabrication this composer exists to refuse.
    """
    session = checklist.get("engine_session")
    if not isinstance(session, dict):
        return None
    role = session.get("claimed_by")
    if not isinstance(role, str) or not role.strip():
        return None
    return role.strip()


def _artifact_refs(task: Mapping[str, Any], base_dir: Any) -> list[str] | None:
    """`artifact-ref` — the changed files, repo-relative, from the engine's own
    collector rather than from anything an agent typed.

    Deliberately NOT a new `artifact-ref` evidence type: that type has zero
    occurrences across the store's ~900 evidence items, so sourcing the field there
    would make it depend on an agent remembering to attach it — a second secretly
    agent-dependent field, which is the class this gate exists to eliminate.

    The diff policy is the step's OWN `git-change-policy` check when it has one (a
    step that already declares which diff it is about is taken at its word), and
    otherwise the engine's default `staged` mode. `[]` is a real answer — "nothing is
    staged" — and is returned as such; `None` (refusal) is reserved for a git failure,
    where the honest reading is "not knowable", not "nothing".
    """
    policy: dict = {}
    for cond in list(task.get("preconditions") or []) + list(task.get("postconditions") or []):
        check = cond.get("check") if isinstance(cond, dict) else None
        if isinstance(check, dict) and check.get("kind") == "git-change-policy":
            policy = check
            break
    try:
        files = _engine()._collect_changed_files(policy, Path(base_dir) if base_dir else None)
    except Exception:  # noqa: BLE001 — git absent, not a repo, or any collector error.
        return None
    return [f["path"] for f in files if isinstance(f, dict) and f.get("path")]


def failed_command_count(task: Mapping[str, Any]) -> int:
    """`failed-commands` — how many `command` checks the ENGINE ran and got a non-zero
    exit from, for this step.

    Read off the evidence the engine writes itself (`type: command-output`, with the
    exit code in `payload.exit`), so it counts what actually happened rather than what
    anyone remembered to report. It survives a refusal because the evidence item is
    appended BEFORE the raise and `main()` persists on the error path.

    SUPERSEDED evidence is counted. A command that failed during an attempt later
    reopened still failed during this run; `reopen` supersedes evidence to stop it
    re-satisfying a gate, which is a statement about gate satisfaction, not history.
    """
    total = 0
    for item in task.get("evidence", []) or []:
        if not isinstance(item, dict) or item.get("type") != "command-output":
            continue
        exit_code = (item.get("payload") or {}).get("exit")
        if isinstance(exit_code, int) and exit_code != 0:
            total += 1
    return total


def reopen_total(checklist: Mapping[str, Any]) -> int | None:
    """`reopens` — how many times this RUN has been reopened, summed from the
    per-task `rework_count` that the engine's `reopen` verb writes and nothing else
    in the engine touches.

    **Run-scoped, where `rework-count` is step-scoped**, and that is what keeps the
    store's two field names two facts rather than one written twice: a run may have
    reopened three gates while the step this record is about was reopened once. The
    worked example in `docs/EPISODE_STORE.md` §3 (`reopens: 1`, `rework-count: 1`) is
    the ordinary case where they coincide, not evidence that they are the same number.

    **The journal sidecar is deliberately NOT a second witness, and the reason is
    measured rather than argued.** An earlier version of this field took
    `max(journal_reopen_lines, rework_total)`, resting on the claim that both
    witnesses could only ever UNDER-count. **That claim is false.** `reopen()`'s
    rework-cap branch blocks the gate and bubbles it to the parent WITHOUT
    incrementing `rework_count`, and it returns an ordinary string rather than
    raising — so `main()` takes the success path and, because `reopen` is a
    `MUTATING_VERB`, journals a `reopen` line for a reopen its own message says did
    not happen (*"blocked and bubbled to parent (not reopened)"*). The journal
    therefore over-counts by one per escalation, and `max` is exactly the operator
    that prefers the inflated reading: a run with ONE real reopen emitted
    `"reopens": 2`. Under `decision:refuse-never-fabricate` a fabricated mechanical
    fact is the worst outcome available to this composer, so the over-counting
    witness is gone rather than compensated for. `rework_count` cannot over-count:
    the same branch that fabricates a journal line pointedly leaves it alone.

    **The cost, stated rather than hidden: this can now UNDER-count.** An `amend`
    that drops a `pending` gate carrying `rework_count > 0` takes its reopens with
    it, and that is the recovery the second witness existed for. It is accepted
    deliberately — under-counting is the direction this field's doctrine already
    concedes, and over-counting fabricates.

    `None` only when the checklist is malformed enough to have no `tasks` mapping.
    """
    tasks = checklist.get("tasks")
    if not isinstance(tasks, dict):
        return None
    total = 0
    for task in tasks.values():
        count = task.get("rework_count") if isinstance(task, dict) else None
        if isinstance(count, int) and not isinstance(count, bool) and count > 0:
            total += count
    return total


def manifest_ref(checklist: Mapping[str, Any], step: str, base_dir: Any) -> str | None:
    """`context-manifest-ref` — `ctx-<work-id>-<step>@<revision>`, per
    `docs/EPISODE_STORE.md` §8's `<manifest-ref>@<revision>` contract.

    The revision is the manifest's own blob OID over its own bytes — the doc's
    "pinning to its own blob hash at capture time", satisfied literally. This is why
    g1's write-if-absent rule is load-bearing rather than tidy: a manifest that could
    be rewritten later cannot be honestly pinned by revision, because the bytes behind
    the pin would change underneath it.

    Refuses when no manifest was taken. A `ctx-<run>-<step>@` carrying an empty or
    invented revision would look exactly like a pin and resolve to nothing.
    """
    work_id = checklist.get("work_id")
    if not work_id or not step or base_dir is None:
        return None
    try:
        import context_manifest as cm

        path = cm.manifest_path(manifest_root(base_dir, work_id), work_id, step)
        with open(path, "rb") as handle:
            revision = cm.rev(handle.read())
    except (OSError, ValueError, ImportError):
        return None
    return f"ctx-{work_id}-{step}@{revision}"


def mechanical_fields(
    checklist: Mapping[str, Any], base_dir: Any = None
) -> dict[str, Any]:
    """The mechanical field group for the checklist's ACTIVE step, from engine state.

    Returns only the fields that could be sourced honestly. A caller that finds a key
    missing is being told "this could not be read", which is information; a caller
    handed a plausible default would be told nothing at all.

    The step is `checklist_engine.active_id()` — the engine's own selector, imported
    rather than re-derived, so this can never disagree with the engine about which
    step is live. When it returns `None` (every item terminal) the step-scoped fields
    are refused as a group rather than reported against some other step.
    """
    fields: dict[str, Any] = {}

    run = checklist.get("work_id")
    if isinstance(run, str) and run.strip():
        fields["run"] = run.strip()

    project = project_name(base_dir)
    if project:
        fields["project"] = project

    role = _lease_role(checklist)
    if role:
        fields["role"] = role

    # `refusals` is CHECKLIST-scoped, unlike its step-scoped neighbours, because a
    # refusal does not always name a task. Checklist-scoped, not run-scoped, and the
    # difference is measured: the counter moves on every refused mutating verb against
    # this file, including one from a FOREIGN session — a teammate's stale-lease retry
    # takes a lease conflict and increments this run's tally. So read it as "refusals
    # taken against this checklist", which is what it honestly is. Narrowing it to the
    # leaseholder's own session is a semantics change with its own under-count (a
    # refusal where `--session-id` was forgotten is genuinely this run's), filed
    # separately rather than guessed at here.
    #
    # It is present only once `claim` has ARMED it, so absence means "this run predates
    # the counter" and is refused rather than reported as 0 — the arming is what makes
    # that distinction readable at all.
    refusals = checklist.get("refusals")
    if isinstance(refusals, int) and not isinstance(refusals, bool) and refusals >= 0:
        fields["refusals"] = refusals

    step = _engine().active_id(checklist)
    task = (checklist.get("tasks") or {}).get(step) if step else None
    if step and isinstance(task, dict):
        fields["spine-step"] = step

        rework = task.get("rework_count")
        if isinstance(rework, int) and not isinstance(rework, bool) and rework >= 0:
            fields["rework-count"] = rework

        fields["failed-commands"] = failed_command_count(task)

        reopens = reopen_total(checklist)
        if reopens is not None:
            fields["reopens"] = reopens

        ref = manifest_ref(checklist, step, base_dir)
        if ref:
            fields["context-manifest-ref"] = ref

        refs = _artifact_refs(task, base_dir)
        if refs is not None:
            fields["artifact-ref"] = refs

    return fields


#: The mechanical fields `apply_episode_delta._validate_create` requires on every
#: create. Named here ONLY so a refusal can be reported by name in the snapshot;
#: `mechanical_fields()` never consults it, so this list can never become a source of
#: values. `artifact-ref` is deliberately absent: it is list-shaped and optional, so
#: its absence is definitionally valid and reporting it as "refused" would be noise.
REQUIRED_MECHANICAL_FIELDS = (
    "run", "project", "role", "spine-step", "context-manifest-ref",
    "refusals", "reopens", "rework-count", "failed-commands",
)


def snapshot_path(base_dir: Any, work_id: Any, step: str) -> Path:
    """`<agent-work>/<work-id>/mechanical/<step>.json` — beside the step's manifest
    (`context/<step>.json`), in the same work area, under a name that says what it
    holds. Deliberately not under `episodes/`: this is the mechanical HALF of an
    episode, and a directory called `episodes` next to the real store at
    `episodes/active/` would invite exactly the wrong reading."""
    return Path(manifest_root(base_dir, work_id)) / str(work_id) / "mechanical" / f"{step}.json"


def emit_mechanical_snapshot(
    checklist: Mapping[str, Any], base_dir: Any = None
) -> Path | None:
    """Write the active step's mechanical group beside its manifest. Never raises.

    **Overwrites, where the manifest is write-if-absent — and the asymmetry is the
    point, not an inconsistency.** The manifest records what was DELIVERED to an
    agent at one instant, and pinning it by revision is only honest if its bytes
    cannot move. This record is a tally: `reopens`, `rework-count`, `failed-commands`
    and `refusals` all change as the step is worked, so a frozen copy would not be a
    preserved record, it would be a wrong number. Refreshing it costs nothing the
    manifest's guarantee depends on, because the pin is over the MANIFEST's bytes,
    not over this file's.

    **Known scope, stated rather than papered over:** the seam fires on `start` and
    `reopen`, so what lands is a STEP-ACTIVATION reading. At `start(x)` the step has
    not run yet and its tallies are legitimately near zero; `reopen(x)` refreshes them
    with the previous attempt's totals. A caller wanting live values calls
    `mechanical_fields()` directly, which always reads current state. Covering the end
    of a step would mean a seam on `advance` as well, which is a change to g1's
    ratified placement and is not made here.

    Records what it could NOT source, by name, in `refused` — the same rule as g1's
    failure stub. An absent field and a field nobody tried to read are different
    facts, and a reader has no other way to tell them apart.

    Swallows every error, including its own write failure, and deliberately does NOT
    let one escape into `emit_step_manifest`'s stub path: a broken snapshot would
    otherwise be reported as a failed MANIFEST, which is a different component's
    health and would send a reader hunting the wrong defect.
    """
    if base_dir is None:
        return None
    try:
        step = _engine().active_id(checklist)
        if not step:
            return None
        fields = mechanical_fields(checklist, base_dir=base_dir)
        destination = snapshot_path(base_dir, checklist.get("work_id"), step)
        destination.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "contract": MECHANICAL_CONTRACT_VERSION,
            "step": step,
            "mechanical": fields,
            "refused": [f for f in REQUIRED_MECHANICAL_FIELDS if f not in fields],
            "run": {
                "work_id": checklist.get("work_id"),
                "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            },
        }
        with open(destination, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
        return destination
    except Exception:  # noqa: BLE001 — a byproduct must never break its host verb.
        return None


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
            manifest_root(base_dir, checklist.get("work_id")),
            checklist.get("work_id"),
            manifest["step"],
        )
        # Write-if-absent: the snapshot belongs to the moment the step activated.
        # Checked against the path derived from the manifest we just built, so the
        # guard and the write can never disagree about which file they mean.
        if not destination.exists():
            cm.write_manifest(manifest, destination)
        # #305 gate g2: the mechanical group rides the SAME seam, and strictly AFTER
        # the manifest exists — its `context-manifest-ref` pins that file's own bytes,
        # so it has nothing to pin until the line above has run. `write_manifest`
        # returns this same `destination`, so the early-return branch above collapsed
        # into the guard with no change to the write-if-absent rule or the value
        # returned. `emit_mechanical_snapshot` swallows its own failures rather than
        # raising into this try, so a broken snapshot is never misreported as a
        # failed manifest.
        emit_mechanical_snapshot(checklist, base_dir)
        return destination
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
            manifest_root(base_dir, checklist.get("work_id")), checklist.get("work_id"), iid
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
