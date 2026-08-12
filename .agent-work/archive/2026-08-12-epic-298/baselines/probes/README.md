# PROBE — issue #331. **This is not baseline data.**

Everything under `probes/` is a **single-run probe**. It is **not** part of the frozen
five-run PRE arm captured for #299, must never be pooled with it, and cannot carry a
lift claim. The frozen arm is `../runs/run-{690,688,698,716,704}/` and nothing here
touches it.

Three mechanical guards keep the two from being confused:

| guard | frozen #299 arm | this probe |
|---|---|---|
| `meta.json` | no `kind` field | `"kind": "PROBE-331"`, `"not_baseline_data": true` |
| corpus id | `sha256:3a30a64b…` | `sha256:7dd678d8…` (sentinel-bearing) |
| directory | `baselines/runs/` | `baselines/probes/` |

## The question

The #299 arm recorded **zero `Skill` invocations across all five runs**
(`../BASELINE_RECORD.md`, Finding 2). That arm's declared limitation 4 names a live
alternative explanation: the brief's required `FILES I WOULD CHANGE` output pushes
subjects toward path-hunting and away from conceptual orientation, and **that** — not
the corpus — may be what suppressed invocation.

So: re-run ONE task with that output demand removed, and **nothing else** changed.

Task **f1Brainz #698**, the only partially-discriminating real task in the set. Same pin
(`3541d2929b19de37107ae13e56776b7162d07255`), same model (`claude-opus-5`), same harness,
same frozen issue text from `../issues.frozen.json`, plan-stage only, read-only against
f1Brainz.

## The one variable

Verbatim, and applied by `str.replace` against `capture_baseline.BRIEF` itself under a
presence assertion — never retyped — so a second variable cannot be smuggled in:

**BEFORE**
```
Understand the problem, then produce a plan. Your plan must name the specific files you
would change and explain why each one. Finish by stating your file list plainly under a
final heading `FILES I WOULD CHANGE`, one path per line.
```

**AFTER**
```
Understand the problem, then produce a plan.
```

No other byte of the brief differs. Also at `probe-698-no-output-demand/brief_diff.md`.

The manipulation landed: the probe's answer contains no `FILES I WOULD CHANGE` heading.

## Answer — the finding is robust; the brief does not explain it

**`Skill` was invoked ZERO times.** Twenty tool calls: `Bash` ×10, `Read` ×6, `Grep` ×3,
`Glob` ×1. Complete transcript, `exit_code: 0`. `first_corpus_read_index` is again
`NO-CORPUS-READ` — the corpus was not so much as read, let alone invoked.

A second, independent witness points the same way. The first launch was truncated by an
instrument failure (see below) and is preserved at
`attempt-1-TRUNCATED-instrument-failure/`. Its captured prefix reached **31 tool calls
with zero `Skill` invocations** before the capture broke. Two launches of the modified
brief, 31 and 20 tool calls, zero invocations in both.

`n` is still small and this is one task. It does not *prove* invariance — but the
proposed alternative explanation predicted a change and none appeared.

## Ordering measure — frozen `extract_ordering.py`, unmodified

| | #299 run-698 (frozen) | this probe |
|---|---|---|
| tool calls | 35 | 20 |
| `first_map_read_index` | 28 | 18 |
| `first_src_read_index` | 0 | 0 |
| `map_before_src` | **false** | **false** |
| `first_corpus_read_index` | `NO-CORPUS-READ` | `NO-CORPUS-READ` |
| map files read | 2 | 5 |
| subagent dispatches | 0 | 0 |
| forbidden operations | 0 | 0 |
| wall-clock | 220s | 179s |

Same shape: source at call 0, map late, map-after-source. Removing the output demand did
widen map reading (2 files → 5, including the constraint and purpose overlays) without
moving it earlier. The one measure the change was hypothesised to move — `map_before_src`
— did not move.

## Issue #332 resolved: **the global corpus shadows the project corpus**

#332 asked which copy would serve an invocation, given that the box carries ~19
identically named constellation skills in the global `~/.claude/skills` and `system/init`
shows a single merged list. The probe corpus was stamped with a provenance sentinel
(`E298-PROBE331-BF2854029A293E44`, an HTML comment after the frontmatter of all 19
`SKILL.md` files — frontmatter untouched, so name and description, the entire trigger
surface, stay byte-identical to the #299 corpus).

Validating the sentinel surfaced **a strictly better discriminator, which is what the
answer rests on**: Claude Code prefixes loaded skill content with a literal
`Base directory for this skill: <absolute path>` line. It names the serving copy
outright, is emitted by the harness rather than planted, and so cannot be defeated by
content truncation. The sentinel is retained as an independent second witness.

Two forced-invocation checks, transcripts in `corpus-resolution-332/`:

| check | cwd | `constellation-triage` entries in `init` | served by | sentinel in transcript |
|---|---|---|---|---|
| `check-1-scratch-dir.ndjson` | scratch dir | 2 | `C:\Users\fredc\.claude\skills\constellation-triage` | 0 |
| `check-2-measured-worktree.ndjson` | `C:/Programs/f1bwt/p698b` (the measured worktree) | 2 | `C:\Users\fredc\.claude\skills\constellation-triage` | 0 |

Both copies **register** — every constellation name appears twice in `init` — but the
**global** copy **serves**. The project-level install under `<worktree>/.claude/skills`
is registered and then shadowed.

Consequence for any future A/B over corpus content: **installing a pinned corpus into
`<worktree>/.claude/skills` does not deliver it.** The global corpus on this box is a
different build (`source_commit 74953936`, 2026-07-25, `corpus_id sha256:fc558d1b…`) from
the pinned pre-#304 corpus (`a226642b`, `sha256:3a30a64b…`). Descriptions were compared
across all 19 skills and are identical, so shadowing does not change which triggers fire
— only which body loads. That is enough to make an A/B on skill *content* unverifiable
until the global copy is scrubbed, pinned, or asserted-identical at launch.

This does not affect the #299 data or this probe: zero invocations occurred in either, so
nothing loaded from either copy.

## Nothing landed in f1Brainz

`git_unchanged: true`, but that check is worktree-scoped and does **not** prove the main
checkout was untouched — the same correction `BASELINE_RECORD.md` records. The
load-bearing evidence, counted across the full transcript:

- **zero `Write` / `Edit` / `NotebookEdit` / `MultiEdit` calls** — no file-writing tool
  was invoked at all, anywhere;
- **zero forbidden operations** — no `git push`, `git commit`, `gh pr create`,
  `gh issue create/comment/edit`, by both the frozen extractor's check and
  `analyze_probe.py`'s wider pattern set.

Both probe worktrees (`C:/Programs/f1bwt/p698`, `p698b`) and the probe corpus were swept
after capture.

## Instrument failure, recorded rather than hidden

The first launch ran in the foreground of a tool call that returned before the subject
finished. Killing the parent killed the pipe-drain threads, so `stream.ndjson` stopped at
a 262144-byte buffer boundary, mid-line, while the subject kept running. The capture is
unusable as a complete transcript and is **not** the reported run. It is kept at
`attempt-1-TRUNCATED-instrument-failure/` because its prefix is real evidence (31 calls,
zero `Skill`) and because deleting a failed attempt would misrepresent how many launches
this result rests on. The reported run was launched detached and completed normally.

## Files

```
probe_331.py                              the capture (derives its brief from the frozen one)
analyze_probe.py                          Skill-invocation + provenance + write-audit readout
probe-698-no-output-demand/               THE REPORTED RUN
  brief.md brief_diff.md meta.json
  stream.ndjson ordering.json             ordering.json written by the frozen extractor
  probe_readout.json final_plan.txt stderr.txt
attempt-1-TRUNCATED-instrument-failure/   truncated first launch, kept deliberately
corpus-resolution-332/                    the two forced-invocation provenance checks
```

## Reproduction

```
py .agent-work/epic-298/baselines/extract_ordering.py --self-test
py .agent-work/epic-298/baselines/probes/analyze_probe.py \
   .agent-work/epic-298/baselines/probes/probe-698-no-output-demand \
   --sentinel E298-PROBE331-BF2854029A293E44
```
