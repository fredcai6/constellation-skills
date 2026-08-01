# Obligations toward issue #301

Two-part statement of what #301 may and may not rely on when it consumes a manifest produced by
`scripts/context_manifest.py`. Drawn from `.agent-work/300/DIT-COMPARISON.md`
("Cross-interface risks toward #301" and its ADDENDUM) — stated cleanly here, not re-derived.

This is a local working artifact, intentionally gitignored under `.agent-work/`. The Admiral
harvests it; it is not shipped in #300's diff and a reviewer should not expect it there.

## What #301 may rely on

- **Contract version.** The manifest envelope carries `contract: 1`
  (`_MANIFEST_CONTRACT_VERSION` in `scripts/context_manifest.py`), independent of the engine's own
  `_STATE_CONTRACT_VERSION` — both happen to read `1` today, and they are free to diverge.
  Whatever #301 stores should name this contract explicitly so the two version numbers cannot be
  confused with each other later.
- **Row shape.** Every entry in `files` is exactly `{root, path, rev}` — three keys, no more, no
  fewer. `rev` is either a git blob OID string (of the LF-normalised bytes, computed in-process,
  no `git` subprocess) or `null` when the declared file does not exist. `required` lives in the
  declaration only; it is never copied into the manifest row.
- **Order stability.** `files` is emitted in **declaration order**, verbatim — never sorted, never
  re-derived from the filesystem or from any other ordering. A doctrine reordering is a genuine
  content change; #301 may treat a permutation of the same paths as a real difference, not noise.
- **Every declared entry is retained, including absent ones.** A declared path whose target file
  does not exist on disk still yields a row, `{root, path, rev: null}` — it is never dropped. #301
  may rely on `len(files) == len(context_refs)` for the step's declaration; row count is not a
  function of what happens to exist on this particular machine.
- **How an episode addresses one.** One manifest belongs to exactly one spine **step**, named by
  the `step` field, selected through the engine's own `active_id(cl)` (never a second selector).
  `manifest_path(agent_work_root, work_id, step)` gives the canonical on-disk address for the
  run-local copy — `<agent-work-root>/<work-id>/context/<step>.json` — and that is the only
  addressing scheme #300 ships or plans.

## What #301 may not rely on

- **Anything under `/run`.** The `run` subtree (`work_id`, `session_id`, `generated_at`, `roots`,
  `host`) is the manifest's declared exclusion set — every legitimately-varying fact lives there
  and nowhere else. #301 must not treat any `run` field as stable across environments or re-runs,
  and must not fold it into a durable identity key for anything it stores.
- **The on-disk pretty-printing.** The two-space `json.dumps(..., indent=2, ensure_ascii=False)`
  plus trailing-newline formatting (`encode()` in `scripts/context_manifest.py`) is presentation,
  not contract. #301 must consume the parsed structure, never compare raw bytes or whitespace.
- **The file path, if the work-area layout moves.** `manifest_path()`'s
  `<agent-work-root>/<work-id>/context/<step>.json` shape is #300's current layout, not a frozen
  address. If `.agent-work/` layout ever changes, this path changes with it. #301 must go through
  the producer's own API (`produce()` / `manifest_path()`) rather than hardcoding the path shape.

## Three facts #301 will otherwise be surprised by

1. **Durability.** The manifest lives under `.agent-work/`, which is gitignored and destroyed by
   `git worktree remove`. Whether #301 inlines a copy of a manifest at capture time or stores a
   reference to it is **#301's call**, not #300's — the rows are deliberately small
   (`{root, path, rev}` only, never file contents) precisely so inlining is affordable. A
   reference-only store dangles the moment the worktree that produced the manifest is cleaned up.
2. **Cardinality.** #300 ships **one manifest per spine step**, not one per episode. If #301's
   episode record assumes a single `context` field per episode, and an episode spans several
   steps, #301 gets N manifests where it may have expected one. Collapsing to one-per-episode would
   destroy the per-step attribution that keying by `active_id(cl)` exists to preserve. If #301 has
   already assumed cardinality 1, **one of the two designs must change** — that is an Admiral
   float, not something either side fixes unilaterally.
3. **Delivery, not use.** The manifest records what was made available, at which revision, in
   which order. It carries **no** claim that the agent read, opened, or acted on anything named in
   `files`. #301 must not present a manifest as evidence that an agent used its declared context —
   that is a different artifact (transcript/access analysis), deliberately out of scope for this
   substrate.

---
Sources: `.agent-work/300/DIT-COMPARISON.md` (§"Cross-interface risks toward #301" and the
ADDENDUM); `scripts/context_manifest.py` (module docstring, `build_manifest`, `produce`,
`manifest_path`).
