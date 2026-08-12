# Launch Order: `governor-269 — #269 worktree isolation does not isolate hook code`

You start cold. Everything you need is pasted here; do not go looking for context in issue threads.

## Mission

`CLAUDE_PROJECT_DIR` is fixed at session launch and inherited by every Agent-tool subagent. So an
agent given an isolated worktree still runs the **main checkout's** hook scripts against the **main
checkout's** `.agent-work/` state. Worktree isolation — which is doctrine precisely so parallel
agents cannot interfere — does not hold for hook code, and it fails **silently**:
`verify_worktree_isolation.py` passes, git is correctly fenced, and the code under test is still not
the code running.

Your deliverable: **make this visible, then rule on whether it is fixable or only documentable.**

Three parts, in priority order:

1. **Doctrine (required).** State it where an agent will actually meet it — the launch-order
   template's Workspace section (`skills/admiral/templates/LAUNCH_ORDER.template.md`) and the
   worktree/dispatch doctrine in `references/fleet-doctrine.md`. The sentence an agent needs is
   roughly: *hook changes cannot be validated from inside the worktree that contains them; use a
   fresh-process probe.* Write it better than that.
2. **Detection (required, verdict may be "no").** Should `verify_worktree_isolation.py` also report
   **which** project dir the hooks will resolve to, so the mismatch surfaces at the moment isolation
   is claimed? Your call, with evidence. A reasoned "no" is a complete answer.
3. **The open question (do NOT prejudge, do NOT implement).** Should a worktree-scoped agent run
   *worktree* hooks at all? There are real arguments both ways — pinning to the main checkout gives
   one consistent rail; resolving per worktree makes hook fixes testable in place. **Analyze and
   recommend; do not change the resolution behaviour in this PR.** See `decision:no-resolution-change`
   below.

**How this serves the epic.** Epic #267 is making the Context Governor actually work. #269 lands
before #262 (installer opt-in wiring) because it changes how #262 must be validated: a Commander
testing installer wiring inside a worktree is not isolated from the rail it is editing. Whatever you
rule here sets the ground #262 stands on.

## Prior-Wave Verdicts (pasted)

### Wave 1 — #261/#202, merged as PR #273 (squash `2c169a5`)

The session→spine binding was single-slot per `session_id`. It is now two-level, keyed by **resolved
absolute spine path** under the session id:

```json
{"<session_id>": {"<abs spine path>": {"spine": ..., "engine_session": ..., "worktree": ..., "claimed_at": ...}}}
```

A claim writes only `binding[sid][abs_spine]` and leaves other spine entries intact. Old flat-shape
entries are detected and ignored (fail open) rather than misread as new-shape.
`decide_session_start` now writes a binding on an **unambiguous** scan (exactly one active-leased
spine); on zero or 2+ matches it injects context and writes **no** binding.

**Verified live post-merge against the Admiral session itself.** Driving the real hooks as
subprocesses: `spine_rail.py SessionStart` wrote the binding; `gauge_writer_hook.py` produced
`fill_fraction 0.081989, model claude-opus-5`; `gauge_reader.read()` returned a live `Reading`;
`thresholds_for('claude-opus-5')` -> `(0.08, 0.15)`, band SOFT. On the next tool call the reading
moved to `0.083089` **with no manual write** — the rail is now self-updating for a session that never
ran `claim`.

### Two findings from wave 1 that bear directly on your mission

**(a) The evidence for your issue is real and is preserved.** At
`.agent-work/harvest-267/governor-261/evidence-202-crosswrite-gauge.json` (main checkout) sits a
gauge record found in the wave-1 Sonnet Commander's work area carrying `"model": "claude-opus-5"` —
the Admiral's own reading, written into its subordinate's directory. Worktree isolation did not
contain it. That is your consequence #2, observed, not theorised.

**(b) A key ruling was overturned by evidence, and you should know why.** The Admiral pre-ruled that
the binding should be keyed or filtered by hook-payload `cwd`. The wave-1 Commander disproved it:
**`cwd` on a PostToolUse payload is fixed at session launch and inherited by subagents**, so parent
and child carry the same value and cwd-matching degrades to skipping both. That is the same root
cause as your issue, wearing a different hat. Do not build anything on payload `cwd` as a
per-call live signal.

**(c) A fail-open that emits nothing is indistinguishable from a broken fix.** Filed to #265. During
wave-1 verification a malformed JSON payload was silently swallowed by the hook's fail-open —
`data = {}`, no `session_id`, nothing written, **exit 0, no output** — and it looked exactly like the
merged fix not working. Relevant to you because your part 2 is a visibility question: whatever you
add must not become another silent path.

## Pre-Rulings

Ruled in advance. Each is overridable if evidence contradicts it — say so explicitly when overriding,
and show the evidence. Wave 1 overturned an Admiral ruling this way and that was the correct outcome.

- `decision:no-resolution-change` — do **not** change how `CLAUDE_PROJECT_DIR` resolves, and do not
  make hooks resolve per-worktree, in this PR. Part 3 is analysis and a recommendation only. Reason:
  it is a fleet-wide behavioural change to the rail every agent runs on, it is squarely in the
  "production defaults / user-visible behaviour" class the contract marks **surfaced**, and #262 is
  about to depend on whatever the answer is. Bring me a recommendation; I take it to the human.
  `@grade: settled/human · leans part-3`

- `decision:fail-open-is-inviolable` — every hook path must still exit 0 and never block, no matter
  what you add. A hook that can refuse is a hook that can strand a session. "Never block" and "never
  say anything" are separable; you may make silence louder, you may not make it fatal.
  `@grade: settled/inherited`

- `decision:doctrine-edit-needs-human` — you are editing shipped doctrine (`.md` / `.template.md`).
  Under the lessons doctrine a graduation into project doctrine carries `authority=human`. **For this
  mission I am pre-ratifying the doctrine edits in parts 1 and 2** — they state a fact you are
  measuring, they do not reshape how the fleet decides anything, and the epic's own imperative asks
  for exactly this text. Write them. If you find yourself wanting to change doctrine *beyond*
  recording this constraint, stop and float it.
  `@grade: settled/human · leans part-1`

- `decision:verify-by-fresh-process` — you cannot validate your own hook change from inside your
  worktree; that is the issue itself. Validate with a **fresh process** whose `CLAUDE_PROJECT_DIR`
  resolves to your worktree (the wave-1 Commander used `claude -p` headless for exactly this, and a
  plain subprocess with the env var set works for the non-agent paths). Fixture-only proof is not
  acceptable for a claim about hook resolution — drive the real writer.
  `@grade: settled/inherited · leans lesson:verify-harness-field-and-drive-real-writer`

- `decision:no-threshold-values` — do not propose, hard-code, or fixture **any** Governor threshold
  number, including in a test. If your work seems to need one, that is a float-up, not a choice.
  This is the decision the whole epic exists downstream of.
  `@grade: settled/human`

- `decision:scope-is-visibility-not-repair` — the mission is to make an invisible constraint visible.
  Resist widening into fixing worktree isolation generally, or into #257 (skills-work-installed),
  which is a sibling but not yours.
  `@grade: guess · leans scope · settle: if part 2 lands and the mismatch is legible at claim time, visibility was sufficient and record that`

## Honest-Null Clause

A measured negative on the stated question is a complete, successful deliverable. If part 2's answer
is "no, `verify_worktree_isolation.py` should not report the hook project dir" — because it would be
noise, or because the check runs at a moment where the answer isn't knowable — that is a full result,
not a failed issue. Report it with the same rigor as a win, and state explicitly **what you tested
and what you did not**.

## Inherited Latitude

From the epic's latitude contract, refreshed by the human for wave 2 on 2026-07-28.

**You may decide, without asking:** architecture and structural choices inside your scope; fix-now
triage (bounded fixes applied immediately); how to test; whether part 2 lands. Issue filing and
closing is **pre-cleared** — `gh issue create`, `gh issue comment`, `gh issue close`. File findings
straight to the tracker; **never bank them worktree-locally for me to harvest.** Full test suite and
`git push` to your `governor/*` branch are pre-cleared. Opening the PR is pre-cleared.

**You must float to me:** any scope change (issue added, dropped, or re-scoped); anything touching
production defaults or user-visible behaviour beyond the doctrine text — which explicitly includes
part 3's resolution question; any Governor threshold value; **anything writing to
`~/.claude/settings.json`** (editing `.claude/settings.local.json` inside *your own worktree* is
pre-cleared and worktree-local only); and anything that fits none of these classes — out-of-taxonomy
always escalates, with one line on why it fit no class.

Floating is not failure. Asking up is always sanctioned, at every tier. If you need context this
order does not cover, return-and-query me — I answer and continue you; it is a round trip, not a
recovery drill.

## File Ownership

Your working-notes file is **`notes-269.md`** at your worktree root. You are its sole writer this
wave.

> Name it `notes-269.md`, **never** `findings-269.md`. The harness `Write` tool refuses any path
> whose basename contains "findings" ("Subagents should return findings as text, not write report
> files") — a guard aimed at unprompted report-dumping, which cannot tell that this file was
> deliberately assigned. Three agents hit it in one epic and each worked around it with a shell
> heredoc. The guard is not ours to change; the word is.

No shared-file fences this wave — you are the only Commander dispatched. The main checkout is **not**
fenced: you may read it (you will need to, to compare hook resolution), but do not write to it.

## Workspace

**Absolute worktree path:** `C:/Programs/constellation-skills-wt/governor-269`
**Branch:** `governor/269-worktree-hook-isolation`
**Base commit:** `2c169a5` (current `origin/main`, verified fresh at dispatch — includes PR #273 and #258)

Created for you with:

```bash
git worktree add C:/Programs/constellation-skills-wt/governor-269 -b governor/269-worktree-hook-isolation
```

First step, before any git operation: run
`py scripts/verify_worktree_isolation.py --here C:/Programs/constellation-skills-wt/governor-269` —
it must exit 0, proving you are in your own worktree and not the shared checkout. Paste its output
into your return report.

Note when you run it: check the exit code **directly**, not through a pipe. Piping to `tail` or
`head` reports the *pipe's* exit code and will tell you 0 when the script exited 1. That cost the
Admiral a false read in wave 1.

NOTE: PR integration defaults to **server-side merge** (the GitHub merge on the PR itself, not a
local merge that would diverge your worktree from main).

## Inherited Context

**Platform.** Windows 11, PowerShell primary, Bash available. Both take their own syntax.

- On Windows, `gh pr create -F <file>` with the body in a temp file. **Never** a heredoc or a
  PowerShell `@'...'@` here-string for a PR `--body` — both fail. Here-strings work for
  `git commit -m` only.
- `\\` inside a bash double-quoted string collapses to a single `\`. Building JSON test payloads with
  Windows paths this way produces invalid escapes that get silently swallowed by fail-open hooks. Use
  forward slashes, or write the payload to a file with a quoted heredoc (`<<'EOF'`). This exact trap
  cost the Admiral two probes and a nearly-filed false defect during wave-1 verification.

**Active lessons bearing on this mission:**

- `lesson:verify-harness-field-and-drive-real-writer` (confirmed 3×) — when a claim depends on a
  harness-supplied field, verify the field's real value and drive the real writer. Do not prove it
  with a fixture. This is the single most load-bearing lesson for your mission.
- `lesson:crew-plan-file-shares-parent-gauge-directory` — crew plan files land in the parent's gauge
  directory; relevant if you touch anything that resolves work-area paths.
- `lesson:reviewer-old-vs-new-repro-without-mutating-file-under-review` — when reproducing old vs new
  behaviour, do it without mutating the file under review.

**Engine CLI quirks** (four hit this run — budget for them):
`--file` is a global pre-verb argument; `--session-id` goes **after** the verb; `block` takes
`--blocker` while `resume` takes `--reason`; the read-only `current` verb rejects `--session-id`
entirely.

## Pre-empted Steps

Already done by me this wave — cite this launch order rather than redoing them:

- **Context established.** The issue body, the wave-1 verdicts, and the two supporting findings are
  pasted above in full. You do not need to open the issue thread.
- **Scope frozen.** Three parts, priorities as stated, part 3 analysis-only. Any change to that is a
  scope change and floats to me.
- **Worktree provisioned and main freshness verified.** `2c169a5` is current `origin/main`.
- **Doctrine-edit authority pre-ratified** for parts 1 and 2 (see `decision:doctrine-edit-needs-human`).

## Data Locations

Worktrees do not contain untracked inputs. Absolute paths into the **main checkout** (read-only for
you):

- Wave-1 cross-write evidence: `C:/Programs/constellation-skills/.agent-work/harvest-267/governor-261/evidence-202-crosswrite-gauge.json`
- Wave-1 harvest trio: `C:/Programs/constellation-skills/.agent-work/harvest-267/governor-261/`
- Live binding file: `C:/Programs/constellation-skills/.agent-work/.spine-rail-binding.json`
- Live gauge for this epic: `C:/Programs/constellation-skills/.agent-work/epic-267/gauge.json`
- The machine-local hook wiring that actually works today: `C:/Programs/constellation-skills/.claude/settings.local.json` (gitignored — one machine, one repo; it is the reason the rail runs here at all)
- Active lessons inbox: `C:/Programs/constellation-skills/.agent-work/LESSONS.md`

## Budget

- **Model tier (required):** **Sonnet.** This is implementer-with-plan work — the investigation is
  already done and pasted, the scope is frozen, and the hard call (part 3) is explicitly
  analysis-only and floats to me. Escalate to me if you find genuine design ambiguity rather than
  silently working above tier.
- **Compute/time, session-window:** one session. You are the only Commander dispatched this wave, so
  you have the full session pool. If you approach a usage limit, return what you have with an honest
  partial rather than dying mid-run.

## Stop Conditions

Stop and return when:

- scope would exceed the three parts as frozen above;
- you need a decision outside your inherited latitude — notably anything in part 3 that would change
  resolution behaviour, any threshold value, or any `~/.claude/settings.json` write;
- evidence for a claim turns out to be impossible to obtain (say so — that is a scoped null, not a
  failure);
- your budget is crossed;
- or you need **context this launch order does not cover and cannot safely proceed without** —
  return-and-query me. I answer and continue you. Asking up is always sanctioned.

## Return Shape

Write your artifact and send your verdict **before** going idle. An idle notification with no
artifact reads as stalled, not done — deliver first. I judge completion from what you produced, not
from a message arriving after you have gone quiet.

Your return report must contain:

1. **Verdict** — per part: what you did, and for parts 2 and 3, your ruling with reasoning.
2. **Evidence** — including the `verify_worktree_isolation.py --here` output (the matched worktree
   path) as proof you worked in isolation, and your fresh-process validation for any claim about hook
   resolution. Say plainly what you tested and what you did not.
3. **Map impact** — what a future agent's mental model of the fleet has to change.
4. **Triage candidates** — anything you found and did not fix. File them to the tracker directly;
   pre-cleared.
5. **Workflow feedback** — the closeout trio (`AGENT_FEEDBACK.md`, `lessons-delta.json`,
   `CONSTELLATION_FEEDBACK.md`). If nothing is ripe for constellation export, say so with reasoning
   rather than exporting filler. Do not pre-empt the epic-tier export decision — that one is mine.

Post the verdict as a comment on issue #269 and open the PR against `main`.
