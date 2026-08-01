# Baseline record — epic #298 PRE-change arm (issue #299)

**This record captures evidence. It does not issue the pathway verdict — that is #307's,
and Tommy's.**

## The pin — the single most load-bearing number here

```
3541d2929b19de37107ae13e56776b7162d07255   (f1Brainz, 2026-08-01 09:52 -0700)
```

**All five runs used it.** Verified mechanically per run, not asserted:
`capture_baseline.py` refuses to launch into a worktree that is not at the pin, and
`verify_capture.py` re-checks `git_after.head == PIN` for every run. The post-#304 arm
must use this same pin.

| | |
|---|---|
| Corpus fingerprint (PRE-#304) | `sha256:3a30a64b02df4dfad896e68aba2c1e46d3f080caaaf6ab98d1fab284d91f0c2d` |
| Corpus source commit | `a226642b` (the rubric-freeze commit; skills tree unmodified from base `c2e16a87`) |
| Model | `claude-opus-5`, all five runs |
| Briefs | frozen at `issues.frozen.json`, read from the snapshot, never live |
| Rubric frozen at | `a226642b` — **before** any run. `git log` proves the order. |
| Nothing landed in f1Brainz | verified: `git_unchanged: true` on all five, zero forbidden operations |

## Per-run evidence

| task | tool calls | first `docs/architecture/*` | first `src/*` | map before src? | corpus read | seam score | wall-clock |
|---|---|---|---|---|---|---|---|
| #690 | 43 | **5** | **2** | **no** | `NO-CORPUS-READ` | 1 | 364s |
| #688 | 35 | **23** | **0** | **no** | `NO-CORPUS-READ` | 1 | 325s |
| #698 | 35 | **28** | **0** | **no** | `NO-CORPUS-READ` | 1 | 220s |
| #716 | 61 | **51** | `NO-SRC-READ` | n/a | 0 | ACKNOWLEDGED-MISS | 371s |
| #704 | 10 | **4** | **0** | **no** | `NO-CORPUS-READ` | 2 | 108s |

`NO-SRC-READ` and `NO-CORPUS-READ` are **findings** — captured transcripts in which that
access did not occur. They are distinct literals from `NOT-CAPTURED` (a datum the
instrument failed to collect), which appears nowhere in this arm: all five transcripts were
captured in full.

**Map files actually read**

- **#690** — `decisions/`, `decisions/tyre-age-g-track-design.md`, `packets/physics.md`, `docs/architecture/`, `reference/physics-unit-conventions.md`
- **#688** — `packets/physics.md`, `overlays/constraints.yml`, `decisions/`, `docs/architecture/`
- **#698** — `packets/physics.md`, `index.md`
- **#716** — `docs/architecture/` (directory listing only)
- **#704** — `docs/architecture/`, `index.md`

**Claimed seams** (verbatim in `runs/run-<N>/claimed_seam.txt`; graded blind)

- **#690** — `src/physics/utilization/class_utilization_observable.py` "the core", + 6 more
- **#688** — `src/physics/layer2/grip_baseline.py` + 9 more
- **#698** — `src/physics/fingerprint/store.py`, `address.py` + ~12 more
- **#716** — ten paths, every one rooted in `C:\Programs\constellation-skills\`, none in f1Brainz
- **#704** — `src/physics/instrument_panel/replication.py`, and nothing else

---

## Finding 1 — every run read source before the map, and every run did read the map

`map_before_src` is **false in every case where source was read at all** (4 of 4). Yet
**no run reached `NO-MAP-READ`** — all five touched `docs/architecture/`. The map was
consulted, consistently, and consistently **after** the source crawl had already begun.
Three of five reached it only after 20+ tool calls.

The shape is uniform: orient by `grep`/`ls` into `src/`, form a hypothesis, then open the
packet to check it. On this corpus, in this arm, the architecture map functioned as a
**confirmation step, not an orientation step.**

## Finding 2 — the corpus was offered and never invoked. This is the important one.

**Zero skill invocations across all five runs.** Not one `Skill` call.

This is not an instrument failure — the treatment was delivered and declined. The
`system/init` event of every transcript shows the `Skill` tool present in `tools` and all
19 constellation skills enumerated in both `skills` and `slash_commands`. Four of the five
runs never read a corpus file either (`NO-CORPUS-READ`); the fifth (#716) read the corpus
only because its issue is literally *about* constellation scripts.

**Why this matters more than any score in the table:** #304 lands its contract *inside
Commander doctrine*. A run that never invokes the Commander never sees that doctrine. If
the post-#304 arm is instrumented the way this one was, **it will produce a null by
construction** — not because a canonical entrypoint fails to help, but because the change
never reaches the subject. A null from that setup would be uninterpretable and would look
exactly like a null from a genuinely ineffective contract.

Given an ordinary planning brief, a Claude Code agent with the full corpus installed simply
plans directly. That is a real behavioural finding about the corpus, and it is arguably the
most actionable thing this baseline produced.

## Finding 3 — the negative control behaves like the real tests on the ordering measure

**Calling this out loudly, as the launch order asks, rather than burying it.**

#704 is the deliberate negative control: single file, function-level, named in its own
title, and a map should not help. On the **ordering measure it is indistinguishable from
the real tests** — source at call 0, map at call 4, `map_before_src: false`. Same shape as
#690, #688, #698.

Read carefully, this cuts two ways:

- It does **not** yet invalidate the instrument. In this arm every run shares that shape,
  so the ordering measure is not *discriminating* between control and real tests — but
  nothing here shows it is measuring the wrong thing. Non-discrimination in a single arm
  is uninformative, not disqualifying.
- It **does** put the pre-registered `L3′` on notice. If the post arm shows map-before-src
  rising on #704 as much as on the real tests, that is ritual compliance — the contract
  inducing map consultation exactly where the rubric says the map cannot help — and `L3′`
  fires.

Also worth stating plainly: #704 was the **cheapest and cleanest run in the set** — 10 tool
calls, 108 seconds, and the only single-file answer, which scored 2. The task the map
should not help with is the task that went best.

## Finding 4 — the losing conditions, evaluated honestly

Evaluated against §5 of the frozen rubric. Real tests = #690, #688, #698.

| id | fires? | why |
|---|---|---|
| **L2 — ceiling** | **no** | Scores are 1/1/1, not 2 across the board. Headroom exists. |
| **L4 — orientation without the map** | **no** | Requires `NO-MAP-READ` with a score of 2. No run reached `NO-MAP-READ`. |
| **L5 — read but useless** | **no** | Requires `map_before_src == true` with a low score. No run read the map first. |
| **L6 — map as confirmation, not orientation** | **depends on a rubric ambiguity — see below** | The `map_before_src == false on ≥2 real tests` half is satisfied 3/3. The `mean seam ≥ 1.5` half is **not** satisfied under the grader's strict reading (mean 1.0) and **is** satisfied under the looser reading (mean 2.0). |
| L1, L3′ | pending | require the post arm |

**No losing condition fires under the grading as delivered.** That is the honest result,
and it is close to the uninformative outcome the cold critic warned about before capture.

### The ambiguity that decides L6 — declared, not resolved

The blind grader flagged, unprompted, that §2's spurious-file tolerance ("up to 4 extra
plausible files does not reduce a 2") is ambiguous in a way that swings **3 of 5 scores by
a full point**:

- **Strict** (what was delivered): any named file beyond the seam counts — tests, docs,
  companion scripts included. #690/#688/#698 all name the correct ground-truth file
  prominently, then exceed the budget with their own tests and docs. Scores 1/1/1, mean 1.0.
- **Loose**: only *competing candidate seams* count as spurious; a thorough plan's own
  tests and docs for the correctly-identified file do not. Scores 2/2/2, mean 2.0.

Under strict, **L6 does not fire**. Under loose, **L6 fires.** The rubric's own wording is
the deciding variable, which is a genuine defect in it.

**The rubric was frozen at `a226642b` and I have not edited it.** A rubric changed after
results exist grades the results, and that prohibition does not weaken when the change
would be convenient. Both readings are recorded here with their consequences; which one
governs is a ruling for the Admiral and Tommy, not a call I get to make after seeing which
way it goes.

Note the perverse incentive the strict reading creates: a plan is penalised for proposing
to update the tests and the architecture packet for the file it correctly identified. Both
#688 and #698 listed `docs/architecture/packets/*.md` among their edits — i.e. they were
map-aware enough to plan to *maintain* the map, and the tolerance rule scored them down for it.

---

## What this arm is — the label

**Not "no map."** Per `decision:baseline-is-informal-map-not-no-map`, and the data agrees:
all five runs read the map.

**And not "no canonical entrypoint" either** — the launch order's label is contradicted by
the corpus. `git show 3541d292:CLAUDE.md` line 7, in the file Claude Code auto-loads into
every session:

```
- `docs/architecture/index.md` — structural map: module boundaries, relationships, dead paths
```

Verbatim again at `AGENTS.md:27` and `README.md:203`. A canonical entrypoint, at an exact
path, in the always-loaded bootstrap file, before #304 does anything.

**Accurate label for this arm:**

> Canonical map entrypoint already present in the target repo's auto-loaded `CLAUDE.md`;
> pathless map-first instruction present in the corpus; **no consolidated contract, no
> degraded mode, and in practice no corpus invocation at all.**

This contradicts a `settled/human` pre-ruling and is floated to the Admiral (F1),
**not** overridden here. What #304 adds on top of this baseline is a *contract and a
degraded mode*, not an entrypoint — a narrower claim than the epic's framing, and one whose
expected effect on the ordering measure is small.

## Declared limitations — stated before the runs, not after

Frozen in rubric §6 ahead of capture:

1. **Seam-lift power ≈ 1 partially-discriminating task (#698), not five.** The issue bodies
   give the paths away: #688 names its file verbatim, #690 names the module basename in its
   first sentence, #716 states the work is out-of-repo, #704 is the control by design.
2. **n = 1 per task.** No replication, no variance estimate. **The seam scores cannot
   support a lift claim — only a direction-of-travel note.** A single 1→2 movement between
   arms is indistinguishable from noise.
3. **The ordering measure is a manipulation check, not an outcome.** It asks whether the
   treatment was delivered, not whether it produced better work. Given Finding 2, it did not
   get delivered at all in this arm.
4. **Brief confound**, declared: the required `FILES I WOULD CHANGE` output pushes subjects
   toward path-hunting and away from conceptual orientation — i.e. **against** the
   hypothesis. It cannot manufacture a win, but it depresses map-reading in both arms.
5. **Subagent-internal reads are invisible** to the ordering measure. Moot here:
   `subagent_dispatch_count` is 0 on all five runs, so nothing was hidden.

## Instrument defect found during capture (affects the POST arm, not this data)

The corpus was installed to `<worktree>/.claude/skills`, but the box also carries 19
constellation skills in the **global** `~/.claude/skills`. The `init` event shows a single
merged skill list, so had any run invoked a skill, **it is not established which copy would
have loaded** — the pinned pre-#304 corpus or whatever is globally installed at run time.

Zero invocations occurred, so **this arm's data is unaffected**. But the post-#304 arm must
resolve it or its treatment is unverifiable. Filed as a triage candidate.

---

## Correction to the "nothing landed" check — scope of what was actually verified

The per-run `git_unchanged` check compares `git -C <worktree> status --porcelain` before and
after. That is scoped to the **worktree**, so it would **not** have caught a write to the
f1Brainz **main** checkout. Stating that plainly rather than letting the green check stand
for more than it proves.

The stronger evidence, checked across all five transcripts after the fact:

- **Zero `Write` / `Edit` / `NotebookEdit` calls in any run** — no run invoked a file-writing
  tool at all.
- **Zero forbidden git/gh operations** (push, PR, commit, issue comment).
- 7 references to the main checkout total, **all read-only** (`ls`, `grep`): #716 read
  `C:/Programs/f1Brainz/.agent-work/epic-659/` researching the work_id bug it was asked
  about, and #690 listed `data/*.db`. Reading the main checkout was not forbidden; writing
  to it was, and none occurred.

f1Brainz main was left dirty (`.agent-work/AGENT_FEEDBACK.md`, `.agent-work/LESSONS.md`, and
a new `archive/2026-08-01-r3-721-consumer-units/`) with mtimes just after this capture window.
**Those are not from these runs** — a separate f1Brainz agent was active concurrently in a
locked `fix-721-grip-band-units` worktree throughout. The zero-write finding above is what
rules this capture out as their source, not the timing.

---

## Reproduction

```
py .agent-work/epic-298/baselines/extract_ordering.py --self-test    # 33 checks incl. a real transcript
py .agent-work/epic-298/baselines/verify_capture.py                  # re-verifies all five runs
```

Archive layout: `runs/run-<N>/` holds `stream.ndjson` (full tool-call transcript),
`ordering.json` (extracted measure), `claimed_seam.txt`, `brief.md` (exact prompt),
`meta.json` (pin, corpus id, model, timings, git before/after), `stderr.txt`.
