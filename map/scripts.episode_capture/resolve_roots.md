# scripts.episode_capture:resolve_roots
function, scripts/episode_capture.py:149, 30 lines

```python
def resolve_roots(base_dir: Any = None) -> dict[str, Path]
```

The three root tokens a `context_refs` entry may name, resolved mechanically.

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

calls internal: repo_root
calls third-party: agent_work_root.durable_root
reads internal: SKILL_ROOT

referenced by: 2 sites, this module only
