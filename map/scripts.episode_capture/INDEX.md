# scripts.episode_capture
scripts/episode_capture.py, 616 lines

Assembly seam: the context manifest as a **byproduct of starting a step**.

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

imports stdlib: __future__.annotations, datetime.datetime, datetime.timezone, json, os, pathlib.Path, subprocess, sys, typing.Any, typing.Mapping
imports third-party: agent_work_root.durable_root, checklist_engine, context_manifest
imported by: none found

```python
SKILL_ROOT = Path(__file__).resolve().parent.parent
MECHANICAL_CONTRACT_VERSION = 1
REQUIRED_MECHANICAL_FIELDS = ('run', 'project', 'role', 'spine-step', 'context-manifest-ref', 'refusals', 'reopens',...
```

- [repo_root](repo_root.md) function: The worktree root `repo`-rooted declarations resolve against.
- [project_name](project_name.md) function: The `project` mechanical field: the REPOSITORY's name, identical from every
- [resolve_roots](resolve_roots.md) function: The three root tokens a `context_refs` entry may name, resolved mechanically.
- [manifest_root](manifest_root.md) function: The `agent_work_root` handed to `context_manifest.manifest_path()`.
- [_engine](_engine.md) function: The engine module, imported LAZILY for the same reason `context_manifest` is:
- [_lease_role](_lease_role.md) function: `role` — the lease's `claimed_by`, or a refusal.
- [_artifact_refs](_artifact_refs.md) function: `artifact-ref` — the changed files, repo-relative, from the engine's own
- [failed_command_count](failed_command_count.md) function: `failed-commands` — how many `command` checks the ENGINE ran and got a non-zero
- [reopen_total](reopen_total.md) function: `reopens` — how many times this RUN has been reopened, summed from the
- [manifest_ref](manifest_ref.md) function: `context-manifest-ref` — `ctx-<work-id>-<step>@<revision>`, per
- [mechanical_fields](mechanical_fields.md) function: The mechanical field group for the checklist's ACTIVE step, from engine state.
- [snapshot_path](snapshot_path.md) function: `<agent-work>/<work-id>/mechanical/<step>.json` — beside the step's manifest
- [emit_mechanical_snapshot](emit_mechanical_snapshot.md) function: Write the active step's mechanical group beside its manifest. Never raises.
- [emit_step_manifest](emit_step_manifest.md) function: Take this step's delivery snapshot. Called by the engine, never by an agent.
- [_write_failure_stub](_write_failure_stub.md) function: Record that the reading was attempted and failed, rather than writing nothing.
