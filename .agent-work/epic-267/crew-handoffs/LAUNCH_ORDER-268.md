# Launch Order: `governor-268 — #268 Admiral spine points the state-note precondition at a path that does not exist`

You start cold. Everything you need is pasted here; do not go looking for context in issue threads.

> **Workspace fields marked `[FILLED AT DISPATCH]` are completed by the Admiral immediately before
> this order is handed to you.** If you are reading one unfilled, stop and query the Admiral — do not
> guess a branch or a base commit.

## Mission

`skills/admiral/templates/ADMIRAL_SPINE.template.json:34` tells the Admiral to write the crash-resume
state note "from `.agent-work/templates/STATE_NOTE.template.md`". **That path does not exist** — not
in this repo, and not in a fresh install. `.agent-work/templates/` is a project overlay that only
appears once something seeds it. The template actually ships at
`skills/workbench/templates/STATE_NOTE.template.md` (installed as
`.claude/skills/constellation-workbench/templates/STATE_NOTE.template.md`).

This is not cosmetic. `execute` precondition p2 is a hard `command` check (`verify_state_note.py`)
that refuses to enter the dispatch phase until the note is filled. **The one step the engine will not
let an Admiral skip points at a file that isn't there.**

It was already fixed once, for the other role.
`skills/commander/templates/COMMANDER_SPINE.template.json:55` carries the correct wording:

> ... from `.agent-work/templates/STATE_NOTE.template.md`, **or the bundled
> `skills/workbench/templates/STATE_NOTE.template.md` when the project has no `.agent-work/templates/`
> overlay**

Your deliverable, two parts:

1. **Apply the Commander spine's fallback wording to the Admiral spine template.** Match the existing
   wording rather than inventing new phrasing — the point is that these two templates stop
   disagreeing.
2. **Sweep the class.** Check whether any *other* role template names an `.agent-work/templates/`
   path without a bundled fallback. `docs/superpowers/drills/dogfood-context-paths-absent.md`
   documents this exact failure class, and names the `execute` STATE_NOTE substep at line 37. A fix
   that landed on one spine and skipped its sibling is evidence the class was never swept. Report
   what you found even if the answer is "nothing else" — that is a complete result.

**How this serves the epic.** Epic #267 is making the Context Governor actually work, and its
recurring theme is *a fail-safe that became a silent failure*. This is the same shape in the doctrine
layer: a hard precondition, correctly enforced, pointing at nothing. It was found by driving the epic,
not by looking for it.

## Prior-Wave Verdicts (pasted)

### How this issue was found — 2026-07-27, live

The Admiral of epic #267 reached the `execute` gate, followed the imperative to the named path, and
got:

```
ls: cannot access '.agent-work/templates': No such file or directory
```

The Admiral then wrote the state note from `skills/workbench/templates/STATE_NOTE.template.md` and
filed this issue. `verify_state_note.py epic-267` has exited 0 on every run since, so the precondition
itself is sound — only the pointer is wrong.

### Wave 1 — #261/#202, merged as PR #273 (squash `2c169a5`)

Not a dependency of your mission; pasted so you know the ground under you. The session→spine binding
was re-keyed from single-slot-per-`session_id` to two-level, keyed by resolved absolute spine path,
and `decide_session_start` now writes a binding on an unambiguous scan. Verified live. Nothing in it
touches templates or spines.

### Concurrent work — do not collide

`governor-269` is working the same wave on `CLAUDE_PROJECT_DIR` / worktree hook isolation. It has
**write ownership of** `skills/admiral/templates/LAUNCH_ORDER.template.md` and
`references/fleet-doctrine.md` and `scripts/verify_worktree_isolation.py`. You own
`skills/admiral/templates/ADMIRAL_SPINE.template.json` and whatever your sweep turns up. **If your
sweep finds a fix needed in one of governor-269's files, do not make it — report it to the Admiral,
who will route it.** See `decision:respect-concurrent-ownership`.

## Pre-Rulings

Ruled in advance. Each is overridable if evidence contradicts it — say so explicitly when overriding,
and show the evidence.

- `decision:surgical-json-edit` — `ADMIRAL_SPINE.template.json` is a **shipped compact-format JSON
  template**. Edit the raw text surgically. **Never** round-trip it through `json.load` /
  `json.dump` — that reflows the whole file and destroys blame. Re-validate with `json.load` after
  editing, as a check, not as a rewrite. This is standing project doctrine, not a preference.
  `@grade: settled/inherited`

- `decision:match-dont-invent` — copy the Commander spine's fallback phrasing rather than authoring
  a better sentence. Two templates saying the same thing differently is how this class survives a
  sweep.
  `@grade: settled`

- `decision:doctrine-edit-pre-ratified` — you are editing shipped doctrine, which normally carries
  `authority=human`. **For this mission the Admiral pre-ratifies it**: you are correcting a factual
  path to one that already ships, using wording a human already ratified on the sibling template. If
  your sweep turns up something that would *change what a role is told to do*, rather than fix where
  it is told to look, stop and float it.
  `@grade: settled/human`

- `decision:respect-concurrent-ownership` — `governor-269` owns
  `skills/admiral/templates/LAUNCH_ORDER.template.md`, `references/fleet-doctrine.md`, and
  `scripts/verify_worktree_isolation.py` this wave. Report, do not edit.
  `@grade: settled`

- `decision:sweep-is-in-scope-repair-is-not` — the sweep's *finding* is required. Fixing every
  instance it turns up is not automatically in scope: fix the ones that are the same
  missing-fallback-path defect, and float anything larger.
  `@grade: guess · leans part-2 · settle: if the sweep finds zero or one additional instance, scope was right; if it finds many, the class needed its own issue and record that`

- `decision:no-threshold-values` — do not propose, hard-code, or fixture **any** Governor threshold
  number, including in a test. If your work seems to need one, that is a float-up, not a choice.
  Inherited epic-wide; unlikely to bind you, stated for completeness.
  `@grade: settled/human`

## Honest-Null Clause

A measured negative on the stated question is a complete, successful deliverable. If the sweep finds
**no** other role template with this defect, that is a full result — report it with the same rigor as
a win, and state explicitly what you searched, how, and what you did not cover. "I grepped for
`.agent-work/templates` across `skills/**` and `docs/**` and found N hits, of which M lacked a
fallback" is the shape of a good null.

## Inherited Latitude

From the epic's latitude contract, refreshed by the human for wave 2 on 2026-07-28.

**You may decide, without asking:** how to implement and test within scope; fix-now triage of bounded
defects. Issue filing and closing is **pre-cleared** — `gh issue create`, `gh issue comment`,
`gh issue close`. File findings straight to the tracker; **never bank them worktree-locally for the
Admiral to harvest.** Full test suite and `git push` to your `governor/*` branch are pre-cleared.
Opening the PR is pre-cleared.

**You must float to the Admiral:** any scope change; anything that changes what a role is *told to
do* rather than where it is told to look; anything touching a file owned by `governor-269` this wave;
any Governor threshold value; **anything writing to `~/.claude/settings.json`**; and anything fitting
none of these classes — out-of-taxonomy always escalates, with one line on why it fit no class.

Floating is not failure. Asking up is always sanctioned, at every tier. If you need context this
order does not cover, return-and-query the Admiral — it answers and continues you; a round trip, not
a recovery drill.

## File Ownership

Your working-notes file is **`notes-268.md`** at your worktree root. You are its sole writer.

> Name it `notes-268.md`, **never** `findings-268.md`. The harness `Write` tool refuses any path whose
> basename contains "findings" ("Subagents should return findings as text, not write report files") —
> a guard aimed at unprompted report-dumping, which cannot tell that this file was deliberately
> assigned. Three agents hit it in one epic and each worked around it with a shell heredoc. The guard
> is not ours to change; the word is.

**New this wave, and required:** before you open your PR, post the substantive content of
`notes-268.md` as a comment on issue #268, then `git rm notes-268.md` in your final commit. Two prior
Commanders left their notes files permanently in `main` (`notes-261.md`, `notes-269.md`) because the old
convention had no removal step — an Admiral template defect, filed as #278, not a Commander failure.
This closes it without waiting on the convention decision. The notes stay durable and addressable on the
issue; the repo tree stays clean.

You own `skills/admiral/templates/ADMIRAL_SPINE.template.json`. Fences as described under "Concurrent
work" above. The main checkout is **not** fenced for reading; do not write to it.

## Workspace

**Absolute worktree path:** `C:/Programs/constellation-skills-wt/governor-268`
**Branch:** `governor/268-admiral-spine-template-path`
**Base commit:** `e3f6a5c` (current `origin/main`, verified fresh at dispatch 2026-07-28 — includes
PR #276, the #269 doctrine edits to `LAUNCH_ORDER.template.md` and `skills/admiral/references/fleet-doctrine.md`)

Created for you with:

```bash
git worktree add C:/Programs/constellation-skills-wt/governor-268 -b governor/268-admiral-spine-template-path
```

First step, before any git operation: run
`py scripts/verify_worktree_isolation.py --here C:/Programs/constellation-skills-wt/governor-268` —
it must exit 0, proving you are in your own worktree and not the shared checkout. Paste its output
into your return report.

Check its exit code **directly**, not through a pipe. Piping to `tail` or `head` reports the *pipe's*
exit code and will tell you 0 when the script exited 1. That cost the Admiral a false read in wave 1.

**Know this about your worktree, because it is this wave's other issue:** `CLAUDE_PROJECT_DIR` is
pinned at session launch, so hook scripts you run resolve to the **main checkout**, not to your
worktree. It does not bind your mission — you are editing a template, not hook code — but do not
assume a hook you trigger is running your copy of anything.

NOTE: PR integration defaults to **server-side merge** (the GitHub merge on the PR itself, not a local
merge that would diverge your worktree from main).

## Inherited Context

**Platform.** Windows 11, PowerShell primary, Bash available. Both take their own syntax.

- On Windows, `gh pr create -F <file>` with the body in a temp file. **Never** a heredoc or a
  PowerShell `@'...'@` here-string for a PR `--body` — both fail. Here-strings work for
  `git commit -m` only.
- `\\` inside a bash double-quoted string collapses to a single `\`. Building JSON with Windows paths
  this way produces invalid escapes. Use forward slashes, or a quoted heredoc (`<<'EOF'`).

**Active lessons bearing on this mission:**

- `lesson:verify-harness-field-and-drive-real-writer` (confirmed 3×) — when a claim depends on a
  harness-supplied field or path, verify the real value. For you that means: after editing, actually
  confirm the fallback path you wrote **exists on disk** and that `json.load` still parses the file.
  Do not prove the fix by reading your own diff.
- `lesson:reviewer-old-vs-new-repro-without-mutating-file-under-review` — when reproducing old vs new
  behaviour, do it without mutating the file under review.

**Engine CLI quirks** (four hit this run — budget for them): `--file` is a global pre-verb argument;
`--session-id` goes **after** the verb; `block` takes `--blocker` while `resume` takes `--reason`; the
read-only `current` verb rejects `--session-id` entirely.

## Pre-empted Steps

Already done by the Admiral — cite this launch order rather than redoing them:

- **Context established.** Issue body and grounding pasted above in full; you need not open the
  thread.
- **Scope frozen.** Two parts: apply the fallback wording, sweep the class. Changes to that are a
  scope change and float.
- **The correct fallback wording is identified and pasted** (Commander spine line 55).
- **Doctrine-edit authority pre-ratified** for the path correction (see
  `decision:doctrine-edit-pre-ratified`).
- **Concurrent file ownership adjudicated** — see "Concurrent work".

## Data Locations

Worktrees do not contain untracked inputs. Absolute paths into the **main checkout** (read-only for
you):

- Active lessons inbox: `C:/Programs/constellation-skills/.agent-work/LESSONS.md`
- The live epic work area, if you need to see a real filled state note as a reference:
  `C:/Programs/constellation-skills/.agent-work/epic-267/STATE_NOTE.md`
- Wave-1 harvest trio (precedent for your own closeout trio's shape):
  `C:/Programs/constellation-skills/.agent-work/harvest-267/governor-261/`

Everything else you need is tracked and present in your worktree.

## Budget

- **Model tier (required):** **Sonnet.** Implementer-with-plan — the investigation is done and
  pasted, the correct wording is identified, the scope is frozen. Escalate to the Admiral if you find
  genuine design ambiguity rather than silently working above tier.
- **Compute/time, session-window:** one session, and this should be a short one. If the sweep balloons
  into something large, that is a signal to float rather than to keep going.

## Stop Conditions

Stop and return when: scope would exceed the two parts as frozen; you need a decision outside your
inherited latitude; a fix your sweep wants lives in a file `governor-269` owns; evidence for a claim
turns out to be impossible to obtain (say so — a scoped null, not a failure); your budget is crossed;
or you need **context this launch order does not cover and cannot safely proceed without** —
return-and-query the Admiral. Asking up is always sanctioned.

## Return Shape

Write your artifact and send your verdict **before** going idle. An idle notification with no artifact
reads as stalled, not done — deliver first. The Admiral judges completion from what you produced, not
from a message arriving after you have gone quiet.

Your return report must contain:

1. **Verdict** — part 1: the edit, with the before/after text. Part 2: what you swept, how, and what
   you found (including "nothing else", if that is the answer).
2. **Evidence** — the `verify_worktree_isolation.py --here` output (the matched worktree path); proof
   the file still parses as JSON after a surgical edit; proof the fallback path you wrote actually
   exists on disk; test suite result.
3. **Map impact** — what a future agent's mental model has to change.
4. **Triage candidates** — anything found and not fixed. File to the tracker directly; pre-cleared.
5. **Workflow feedback** — the closeout trio (`AGENT_FEEDBACK.md`, `lessons-delta.json`,
   `CONSTELLATION_FEEDBACK.md`). If nothing is ripe for constellation export, say so with reasoning
   rather than exporting filler. Do not pre-empt the epic-tier export decision — that one is the
   Admiral's.

Post the verdict as a comment on issue #268 and open the PR against `main`.
