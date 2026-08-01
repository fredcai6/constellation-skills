# Launch Order: `commander-261 — #261 (bind on resume) with #202 (single-slot clobber) folded in`

You start cold. Everything you need is pasted below — nothing here requires you to open an issue
link or reconstruct a prior conversation.

## Mission

Make the Context Governor gauge a session that did **not** personally run `claim`, and stop a
subagent's claim from blinding its parent. Two issues, one commander, because they are the same
question — *who owns a binding slot, and when* — and fixing either alone re-breaks the other.

**#261** — `gauge_writer_hook.resolve_gauge_path()` finds the gauge path by looking up `session_id`
in `.agent-work/.spine-rail-binding.json`. That binding is written **only** by
`spine_rail.handle_post_tool_use()`, and only for engine `claim`/`release`
(`scripts/hooks/spine_rail.py:288` — `if verb not in ("claim", "release")`).
`decide_session_start()` re-injects run context on resume/compaction and correctly locates the
active spine, but **never writes a binding**. So a session that resumes, is compacted, or continues
a run it did not itself claim has no entry, `resolve_gauge_path` returns `None`, and the writer
skips on **every tool call for that session's entire life** — no gauge, no Trip, no advisory, and
no signal that anything is missing.

**#202** — the binding is a single slot keyed by `session_id`. An Agent-tool subagent shares its
parent's `session_id`, so the subagent's `claim` **overwrites** the parent's entry. PR #201 fixed
the worst symptom (the parent is no longer Stop-blocked on the subagent's spine, via the
`_foreign_worktree` comparison at `spine_rail.py:199-212`) but the parent's own claimed spine is
left unwatched — and now, ungauged — for the whole overlap window. Fix direction from the original
filing: make the binding **per-worktree-keyed and multi-entry** (one session may legitimately hold
one binding per distinct worktree). That subsumes #201's guard, since the guard falls out of keying
by worktree.

**How this serves the epic.** Epic #267 exists because the Governor is code-complete and
operationally inert. This issue ships **alone and first** — see the pre-ruling below — because the
Governor's own refresh path relaunches a fresh agent that runs `current`, not `claim`. Until this
lands, every context Trip hands off to a permanently blind successor, and the epic cannot supervise
its own repair.

## Prior-Wave Verdicts (pasted)

No prior wave — you are wave 1. What follows is the live evidence the epic was scoped on, gathered
by hand on 2026-07-27. Treat it as findings, not as gospel: `lesson:verify-launch-order-claims-against-code`
(pasted below) applies to this document too.

**Finding 1 — the math is correct, the plumbing is dead.** Running the writer by hand against a
live session transcript:

```
find_latest_usage -> ('claude-opus-5', 89481, '2026-07-27T16:23:16.365Z')
compute_record   -> {'schema_version': 1, 'fill_fraction': 0.089481,
                     'model': 'claude-opus-5', 'observed_at': '2026-07-27T16:23:16.365Z'}
```

89K against a real 1M window. Correct and correctly scaled. Nothing is wrong with the measurement.

**Finding 2 — the binding file holds only claim-created entries.**
`.agent-work/.spine-rail-binding.json` held 4 sessions, every one created by a `claim`. The session
that ran the audit (`05c5ec39`) had been alive for hours against an active lease, received the
SessionStart re-injection, and was **absent** from the binding. Zero gauge writes for its entire
lifetime.

**Finding 3 — every `gauge.json` on disk read `fill_fraction: 1.0`**, all pre-#252, saturated
against the old 200K default denominator; newest 2026-07-25 02:46, before the fix landed. There was
not one post-fix reading anywhere in the repo until this epic's own Admiral session produced one.

**Finding 4 — the fix works once a binding exists.** The Admiral ran `claim` for epic-267, which
wrote a binding, and the Governor immediately produced its first correct live readings: `0.125617`,
then `0.157` (a HARD trip that genuinely blocked `advance`), then `0.057168` after the human
compacted manually. Arm and clear, both correct. **The binding is the only broken link.**

## Pre-Rulings

Ruled in advance. Each is overridable if evidence contradicts it — say so explicitly when you
override, and float the surfaced ones rather than deciding them.

- decision:261-goes-first — this work ships and merges **alone**, before any other epic-267 issue is
  dispatched. Do not widen scope into #262 (installer wiring), #263 (subagent measurement), #264
  (end-to-end assertion) or #265 (visible non-reading), however tempting the adjacency. If you find
  something belonging to those, file it or comment on the existing issue and move on.
  `@grade: settled/human · leans wave-1`

- decision:no-bind-on-ambiguous-scan — `decide_session_start` falls back to `_scan_active_spine()`
  (`spine_rail.py:392`), which returns the **first** `.agent-work/*/spine.json` with an active lease.
  Injecting advisory context on a guess is cheap; **binding** on a guess is not — a wrong binding
  points the gauge writer at the wrong work area and produces a confident wrong record, which is the
  #252 failure class this epic exists to prevent. So: when the scan is ambiguous (more than one
  active-leased spine), **inject context as today but write no binding**. Skip-on-uncertainty, the
  same doctrine the writer hook already follows. An unambiguous single active spine may bind.
  `@grade: settled · leans the decide_session_start change · settle: if you find the scan cannot in practice be ambiguous, say so with evidence and bind unconditionally`

- decision:binding-schema-may-change — the epic freezes the **gauge record** schema (the four-field
  `gauge.json`). It does **not** freeze `.spine-rail-binding.json`. Re-keying that file for #202 is
  in scope and expected. Handle the existing on-disk entries: a stale old-shape file must not crash
  either hook, and must not silently resolve to a wrong path. Fail-open beats guessing.
  `@grade: settled · leans the #202 half`

- decision:fail-open-is-inviolable — neither hook may ever block a tool call, raise into the harness,
  or fabricate a reading. Every existing `except Exception: return {}` stays. If your fix has a
  failure mode, its failure must be *silence plus a visible marker*, never a wrong number and never
  an exception. (Making silence visible is #265's job, not yours — do not build it here, but do not
  make it harder either.)
  `@grade: settled/inherited · leans both halves`

- decision:no-threshold-values — you may not introduce, change, or hard-code any soft/hard cap or
  window value, **including in a test fixture**. If your tests need a threshold, use the values
  already in `_PROFILES`/`MODEL_WINDOWS` or float the question up. This is the one decision the
  whole epic sits downstream of and it is reserved to the human.
  `@grade: settled/human · leans testing`

## Honest-Null Clause

A measured negative on the stated question is a complete, successful deliverable — report it with
the same rigor as a win. Concretely: if you find that SessionStart's payload does **not** carry a
usable `cwd` (see the harness-field lesson below), or that binding at SessionStart is unsafe for a
reason the scoping missed, that is a full result. State what you tested, under what conditions, and
what you did **not** test. A negative kills that specific approach under those conditions — never
the idea class, and never "this is impossible."

## Inherited Latitude

**Yours to decide** (from the epic's latitude contract, inherited):
- Architecture and structure of the fix, including re-keying the binding file.
- Filing and closing issues — `gh issue create` / `gh issue comment` / `gh issue close` are
  **pre-cleared**. File findings to the tracker directly; **never** bank them worktree-locally for
  someone else to harvest.
- Fix-now triage on bounded adjacent defects you trip over, within the no-widening ruling above.
- Running the full suite (`py -m pytest`) and pushing to your `governor/*` branch — pre-cleared.
- Editing `.claude/settings.local.json` **inside your own worktree** for wiring tests — pre-cleared,
  worktree-local only.

**Float to the Admiral, do not decide:**
- Any threshold value, anywhere, including test fixtures.
- Anything that would write the user's `~/.claude/settings.json`. Worktree-local settings are yours;
  the user's home settings are never touched.
- Any change to the four-field gauge record schema.
- Scope changes — adding, dropping, or re-scoping an issue.
- Anything that fits none of these classes: it is out-of-taxonomy, escalate it with one line on why
  it fit no class.

Floating up is always sanctioned and never counts against you. The Admiral answers and continues
you — it is a round trip, not a failure.

## File Ownership

Your working-notes file, sole writer this wave: **`notes-261.md`** at your worktree root.

> Name it `notes-261.md`, **never** `findings-261.md`. The harness `Write` tool refuses any path
> whose basename contains "findings" — a guard aimed at unprompted report-dumping that cannot tell
> this file was deliberately assigned. Three agents hit it in one epic and each burned a turn
> working around it with a shell heredoc. The guard is not ours to change; the word is.

No shared-file fences this wave — you are the only Commander dispatched.

## Workspace

**`C:/Programs/constellation-skills-wt/governor-261`** — provisioned for you, branch
`governor/261-bind-on-resume`, based on `2bbf797` (verified fresh against `origin/main` at dispatch).

Created with:
```bash
git worktree add -b governor/261-bind-on-resume "C:/Programs/constellation-skills-wt/governor-261" 2bbf797
```

**First step, before any git operation**, from inside that directory:
```bash
py scripts/verify_worktree_isolation.py --here "C:/Programs/constellation-skills-wt/governor-261"
```
It must exit 0. Paste its output into your return report. (Verified at dispatch that it exits 1 from
the shared checkout and prints which worktree you should be in — so a 0 is real evidence.)

PR integration defaults to **server-side merge** — the GitHub merge on the PR itself, never a local
merge that would diverge your worktree from main.

## Inherited Context

### Active lessons that bear directly on this mission

**`lesson:verify-harness-field-and-drive-real-writer`** — *this is the single most important line in
this launch order.* When a hook depends on a harness-supplied payload field, verify the field's
presence against the harness contract (docs) **and** make the regression test drive the **real**
writer path that populates it, not a hand-injected fixture. A hand-set fixture asserts the field is
present and passes green even if production never delivers it, hiding a silent no-op fix. Grounding:
the #151 Stop-hook fix rode an unverified assumption that Stop carries `cwd`; injected-`cwd` unit
tests passed green regardless. **Your fix depends on exactly this**: binding at SessionStart needs a
worktree value, and `decide_session_start` today reads only `data.get("session_id")`. Whether
SessionStart carries `cwd` is an empirical question you must answer before building on it — and
answering it "no" is an honest null, not a failure.

**`lesson:verify-launch-order-claims-against-code`** — verify this order's **named** defect against
current code (grep the named symbol) **before** planning, and verify any named edit target actually
exists at the named address. A headline mechanism already shipped becomes an honest-null; a
named-but-nonexistent target is a naming slip, not a build task. Confirmed 4× across two epics. Line
numbers in this document were read at dispatch and may drift — grep, don't trust them.

**`lesson:round-trip-tests-prove-artifacts-not-parsers`** — a test over real shipped artifacts proves
those artifacts are clean, not that the tool is correct. Pair it with **adversarial fixtures**
authored to make the tool return a wrong answer: a binding that resolves to the wrong work area, a
stale entry pointing at a deleted spine, two sessions racing the same slot.

**`lesson:windows-subprocess-env-does-not-shadow-path-resolution`** — on Windows, passing a
restricted `env={'PATH': ...}` into `subprocess.run()` does **not** change which executable an
unqualified command resolves to; CreateProcess resolves against the calling process's real
environment. To make something genuinely unresolvable, mutate ambient `os.environ['PATH']`.

**`lesson:prove-command-fails-postcondition`** — to prove a guard correctly *refuses* something, a
`! <command>` bash-negation wrapper turns "the guard fired" into a mechanical check rather than a
self-reported attestation.

**`lesson:test-harness-concurrency-failsafe`** — if you write a test doing real concurrent file I/O
on the binding file: wrap per-iteration work in try/except with a guaranteed stop-signal in
`finally`, and mark helper threads `daemon=True`. A writer thread dying on a transient Windows
`os.replace` sharing violation without signaling stop leaves a non-daemon reader spinning and hangs
pytest forever. This has already happened once in this repo.

### Technical invariants

- **Windows / PowerShell.** For PR bodies, write to a temp file and use `gh pr create -F <file>` —
  never a heredoc, never a PowerShell `@'...'@` here-string with `--body`. Here-strings work for
  `git commit -m` only.
- The engine's `--file` is a **global** argument and must come **before** the verb:
  `py scripts/checklist_engine.py --file <spine> current`, not `current --file <spine>`. Also
  `claim` takes `--claimed-by`, not `--by`. Both cost the Admiral a turn this session.
- `gauge_writer_hook._is_contained()` requires `gauge_path.parent.parent.name == ".agent-work"` —
  gauge writes are fenced to `.agent-work/<work-id>/gauge.json`. Any binding change must keep
  resolved paths inside that fence.
- `find_latest_usage()` skips `isSidechain` entries and tails `TAIL_BYTES = 2_000_000` of the
  transcript.
- A test pins `MODEL_WINDOWS` (writer) and `_PROFILES` (reader) to the same key set. If you touch
  either, expect that test.

### Files you will care about

- `scripts/hooks/spine_rail.py` — `handle_post_tool_use` (~274), `decide_session_start` (~409),
  `_scan_active_spine` (~392), `_foreign_worktree` (~199), `load_binding`/`save_binding`.
- `scripts/hooks/gauge_writer_hook.py` — `resolve_gauge_path()`, the binding consumer. **If you
  re-key the binding for #202, this is the function that breaks.** It currently looks up by
  `session_id` alone and will need to disambiguate by worktree.
- `scripts/gauge_reader.py` — the read half. You should not need to change it; if you think you do,
  that is worth floating.

### One concrete constraint the scoping surfaced

`_scan_active_spine()` returns the **spine dict**, not its path. A binding entry needs the spine's
absolute path (`binding[sid]["spine"]`). So the fallback must be taught to return the path alongside
the dict, or be split. This is the thing that turns "one-line fix" into a real change — budget for
it.

## Pre-empted Steps

The Admiral has already performed these; cite this launch order rather than redoing them:

- **Issue triage and scoping** — #261 and #202 are confirmed live-reproduced (Findings 1–4 above),
  not speculative. You do not need to re-establish that the Governor is broken.
- **Worktree provisioning** — created and verified; do not create another.
- **Main freshness** — `origin/main` confirmed at `2bbf797` at dispatch. PR #258 is open but touches
  `init_work_area` only; no overlap with your files.
- **The pairing decision** — that #202 rides with #261 rather than shipping separately is ruled, not
  yours to revisit.

You still own: planning, a cold plan critic if your plan's acceptance depends on a
before/after measurement (`lesson:cold-critic-mandatory-for-measurement-dependent-plans` — two
commanders independently found it caught plan-invalidating defects before any crew was dispatched),
implementation, review, tests, and the PR.

## Data Locations

Worktrees do not contain untracked inputs. Absolute paths into the main checkout:

- Live binding file (the real, currently-4-entry artifact):
  `C:/Programs/constellation-skills/.agent-work/.spine-rail-binding.json`
- Real produced gauge records, including this epic's correct ones:
  `C:/Programs/constellation-skills/.agent-work/epic-267/gauge.json` (and `.agent-work/*/gauge.json`
  for the saturated pre-#252 corpus — useful as adversarial fixture material)
- The only working hook wiring anywhere, gitignored and machine-local:
  `C:/Programs/constellation-skills/.claude/settings.local.json`
- Session transcripts (real `usage` records):
  `C:/Users/fredc/.claude/projects/C--Programs-constellation-skills/*.jsonl`
- Epic work area, for context: `C:/Programs/constellation-skills/.agent-work/epic-267/`

**Read these; do not write to any of them.** Your writes stay inside your worktree.

## Budget

- **Model tier (required):** **Sonnet.** This is a well-characterized fix in a small, well-understood
  surface with the diagnosis already done. Escalate to Opus only if the #202 re-keying turns out to
  have a genuine interface-design question underneath it — and float that escalation rather than
  taking it silently.
- **Compute/time, session-window:** one session-window. You are the only dispatch in this wave, so
  the account's session pool is entirely yours. If you approach a context limit, file a
  refresh-request and hand off rather than degrading — you are, after all, fixing the machinery that
  makes handoffs work.

## Stop Conditions

Stop and return when:
- The fix is complete, tested, and the PR is open — the normal exit.
- You need a decision reserved to the Admiral or the human (see Inherited Latitude).
- Scope would have to widen past #261 + #202 to make progress.
- Evidence for a claim turns out to be impossible to obtain — say so with what you tried.
- You need **context this launch order does not cover and cannot safely proceed without** —
  return-and-query the Admiral; it answers and continues you. **Asking up is always sanctioned.**

Do not quietly abandon, and do not fabricate evidence. Those are the two forbidden exits.

## Return Shape

Write `notes-261.md` and send your verdict **before** going idle — an idle notification with no
artifact reads as stalled, not done. The Admiral judges completion from what you produced.

Your return report must carry:

1. **Verdict** — what shipped, or the honest null, in plain English.
2. **The `verify_worktree_isolation.py --here` output**, including the matched worktree path, as
   evidence you worked in isolation.
3. **Evidence** — the empirical answer to *does SessionStart carry `cwd`?*, with how you determined
   it; test names and pass/fail; and the PR number and its check status.
4. **The live proof.** Unit tests are necessary and not sufficient here — this whole epic exists
   because a well-formed record from a wrong denominator passed every unit test for eight days.
   Show a **real binding written by a real SessionStart**, not a fixture: the before/after content of
   a binding file that a genuinely resumed or compacted session caused to be written.
5. **Map impact** — anything a future agent's mental model of this code should change about.
6. **Triage candidates** — bounded adjacent defects you found and did not fix. File them (pre-cleared)
   and list the issue numbers.
7. **Workflow feedback** — where this launch order was wrong, thin, or misleading, and what would
   have helped. Including: any line number in this document that had drifted by the time you grepped
   it.

Post the verdict as a comment on **#261**, and open the PR against `main` referencing both #261 and
#202.
