# notes-261.md — Commander run: #261 (bind on resume) + #202 (single-slot clobber)

Launch order: `.agent-work/epic-267/crew-handoffs/LAUNCH_ORDER-261.md` (read from main checkout,
absolute path, per Data Locations).

## Worktree isolation

`py scripts/verify_worktree_isolation.py --here "C:/Programs/constellation-skills-wt/governor-261"`
→ `worktree OK: in C:/Programs/constellation-skills-wt/governor-261`, exit 0.

## Understand — code verified against launch order's named claims (lesson:verify-launch-order-claims-against-code)

All named symbols/lines checked against HEAD (`2bbf797`) of `scripts/hooks/spine_rail.py` and
`scripts/hooks/gauge_writer_hook.py` in the worktree. Line numbers drifted by ~1 in one spot but
every named mechanism is real and matches the launch order's description:

- `handle_post_tool_use` at line 274 (matches). Verb gate at **line 287** (`if verb not in ("claim",
  "release"): return {}`) — launch order said 288, off by one, drifted.
- `decide_session_start` at line 409 (exact match). Confirmed: it reads an existing binding or falls
  back to `_scan_active_spine()`, injects `SessionStart` advisory context, and **never calls
  `save_binding`** — so a resumed/compacted session that did not itself run `claim` gets context but
  no binding, and `gauge_writer_hook.resolve_gauge_path` (keyed on `binding.get(session_id)`) returns
  `None` for that session's whole life. Confirmed live: Finding 2 in the launch order.
- `_scan_active_spine` at line 392 (exact match). Confirmed it returns the **spine dict**, not its
  path — the launch order's "one concrete constraint" is real and had to be designed around.
- `_foreign_worktree` at lines 198–214 (launch order said 199–212, close). Confirmed: compares
  `data.get("cwd")` against the binding entry's `worktree` field.
- `gauge_writer_hook.resolve_gauge_path` / `_is_contained`: confirmed exactly as described —
  single-key lookup `binding.get(session_id)`, path fenced to `.agent-work/<work_id>/gauge.json` by
  shape only (`gauge_path.parent.parent.name == ".agent-work"`), no existence check on the spine.
- `handle_post_tool_use`'s claim branch: `binding[sid] = {"spine": ..., "engine_session": ...,
  "worktree": ...}` — unconditional overwrite, single slot keyed by `sid` alone. Confirmed #202's
  diagnosis exactly: nothing before this write checks whether `sid` already owns a *different*
  worktree's binding.

Verdict: the launch order's factual claims about the code are accurate. No honest-null on "is this
issue real" — both issues reproduce exactly as described, from reading the code alone; no dispute.

## Empirical finding: does SessionStart's payload carry a usable `cwd`? — YES, but with a load-bearing wrinkle

**Docs answer (checked live against `code.claude.com/docs/en/hooks`, fetched 2026-07-27):** `cwd` is
a **common field on every hook event**, `SessionStart` included — "Current working directory when
the hook is invoked." The documented example payload for `SessionStart` includes `"cwd":
"/Users/..."`. So the field exists and is populated by contract.

**Empirical production probe (not a fixture — this session's own real hook writes), per
`lesson:verify-harness-field-and-drive-real-writer`:**

I ran the engine's `claim` verb for my own spine twice, as *separate* Bash-tool invocations (to
avoid a same-call read-before-write race), and inspected the resulting entry in the real
`.agent-work/.spine-rail-binding.json` (main-checkout copy — see below for why) after each:

1. First call used a **relative** `--file .agent-work/governor-261/spine.json` inside a compound
   `cd <worktree> && ... && claim ...` command. Result: the binding recorded `"spine":
   "C:\\Programs\\constellation-skills\\.agent-work\\governor-261\\spine.json"` — the **main
   checkout**, not my worktree, even though the shell's actual `cd` target for that command was the
   worktree. It also created a stray `.agent-work/governor-261/gauge.json` in the **main checkout**
   (gauge_writer_hook resolved against the same wrong binding and wrote there — `_is_contained` only
   checks path *shape*, not that the spine at that path actually exists, so it happily wrote into an
   orphan directory). This is a live, reproduced instance of exactly the failure class
   `decision:no-bind-on-ambiguous-scan` worries about ("a wrong binding points the gauge writer at
   the wrong work area"), just via a different causal path (bad relative-path resolution) than the
   one the ruling anticipated (ambiguous scan).
2. Second call used an **absolute** `--file`, issued as its own isolated Bash-tool call (no
   compound `&&`, no embedded read). Result: `"spine"` resolved correctly to my worktree's real
   spine path. But `"worktree"` **still** recorded the main checkout — confirmed by direct
   `Path.is_absolute()` / `_resolve_abs` unit check against the exact captured token stream (isolated
   from the hook, to rule out a tokenizer bug): the resolver logic is correct; the input it receives
   (`data.get("cwd")`) is what's wrong, or rather, differently-scoped than assumed.
3. Root cause, confirmed by reading `resolve_project_dir()`: `Path(os.environ.get("CLAUDE_PROJECT_DIR")
   or os.getcwd())`. `CLAUDE_PROJECT_DIR` is fixed for this session's whole lifetime to the main
   checkout (`C:\Programs\constellation-skills`) — it is an **env var set once at session launch**,
   not something a Bash-tool `cd` changes. This explains why the binding **file itself** lives at the
   main checkout's `.agent-work/.spine-rail-binding.json` rather than my worktree's, regardless of
   which directory I operate in.
4. For `data.get("cwd")` specifically (as opposed to `CLAUDE_PROJECT_DIR`): my second, isolated
   `claim` call ran with **no explicit `cd` prefix at all** (the Bash tool's cwd had already
   persisted at the worktree from several calls earlier — confirmed by a bare `pwd` immediately
   before it printing `/c/Programs/constellation-skills-wt/governor-261`). Yet the hook-recorded
   `"worktree"` (sourced from `data.get("cwd")`) was still the main checkout. This rules out a
   same-call read race or a tokenizer artifact as the explanation: **the harness's hook-payload
   `cwd` field is fixed for a session's lifetime (matching the session's original/declared project
   root), not the Bash tool's live/persisted subprocess working directory.**

**Conclusion — scoped, not class-spanning:** `cwd` IS present on `SessionStart` (and every hook
event) per contract and in practice — the field exists and is non-null. What it measures is **the
session's fixed project root, not "which worktree is this particular agent, right now, operating
in."** For any agent dispatched into a worktree by *instruction* (told to `cd` there in its own tool
calls) rather than by an actual harness-level working-directory parameter — which is the sanctioned,
documented pattern for this whole fleet (`skills/_shared/windows.md` §3: "provision the worktree
yourself... before dispatch") — `cwd` will read as the **launch-time root**, not the worktree, for
every hook event that session ever fires, `SessionStart` included.

This is a genuine, reproducible, load-bearing constraint the launch order's framing did not
anticipate (it assumed `cwd` would behave as a live per-agent worktree signal). It does **not** kill
either issue's core mechanism, but it rules out one specific design for #202 (see Plan).

**What I did NOT test:** whether a genuinely separate process (e.g. a headless `claude -p` CLI
launch with its own distinct cwd, or a harness that DOES thread a per-agent working-directory
parameter through to `CLAUDE_PROJECT_DIR`/`cwd`) would report a live, worktree-accurate `cwd`. The
windows.md `isolation:"worktree"` no-op note suggests the Agent-tool harness on Windows does not
reliably provision per-agent working directories at all today, which is consistent with what I
found, but I have not independently probed a `claude -p --cwd <worktree>`-style separate-process
launch to confirm whether *that* pattern behaves differently. Scoped null: this is "cwd is
session-fixed for an Agent-tool-dispatched, cd-by-instruction worktree Commander," not "cwd is
useless everywhere."

Cleanup: removed the throwaway `cwd_probe.py` hook and its `settings.local.json` wiring from my
worktree (never fired — settings changes need a session restart I could not safely trigger mid-run).
Left the stray `C:\Programs\constellation-skills\.agent-work\governor-261\gauge.json` and my (now
corrected) binding entry in the **main checkout** — the harness's own permission classifier refused
an `rm -rf` targeting a path outside my worktree, which is the correct sandbox boundary, not a bug to
route around. Flagged for the Admiral to sweep; it is harmless untracked debris (`.agent-work/` is
gitignored) but not mine to delete from outside my worktree.

## Plan implications

- **#261 (bind on resume)** does not need `cwd` at all for its core mechanism.
  `decision:no-bind-on-ambiguous-scan` already says: bind only when the scan is unambiguous (exactly
  one active-leased spine); on ambiguity, inject context but skip the bind. That comparison is a
  *count*, not a worktree match — no `cwd` dependency. Fix: teach `_scan_active_spine` to return
  `(spine, path)` (or split it), and have `decide_session_start` call `save_binding` when unambiguous.
- **#202 (per-worktree-keyed, multi-entry)** must NOT key or disambiguate by `data.get("cwd")` —
  proven unreliable above for exactly the dispatch pattern (`Commander-in-worktree`) this fix exists
  to serve. Instead: derive "worktree" identity from the **resolved absolute spine path's own
  structure** (`.agent-work/<work_id>/spine.json`'s grandparent directory — the same convention
  `gauge_writer_hook._is_contained` already leans on), which is self-consistent and requires no trust
  in any harness-supplied cwd field. On the **read** side (`gauge_writer_hook.resolve_gauge_path`),
  given a session_id bound to multiple worktrees, there is no reliable signal to pick *one* — but the
  gauge reading is a property of the session's own transcript, valid for every spine that session is
  bound to, so the principled resolution is to write the gauge for **every** currently-bound entry
  under that session_id rather than guessing.
