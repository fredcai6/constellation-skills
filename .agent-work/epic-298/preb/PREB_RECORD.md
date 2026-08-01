# PRE-B — the Commander-loaded pre-#304 arm (epic #298)

**Verdict: arm captured. Five runs, five verified Commander loads, corpus stable across the
whole window, nothing landed in f1Brainz.**

The headline result is a **measured negative on the orientation axis**, and it is a complete
deliverable rather than a failure: forcing the Commander to load — and with it both pathless
map-first imperatives — moved orientation **not at all**. See §4.

---

## READ THIS BEFORE READING ANY NUMBER: three arms, two series

**PRE-B's ordering measure is NOT comparable to PRE-A's (#299). PRE-B pairs with the POST
arm. It does NOT pair with PRE-A.**

PRE-A measured an agent under **no map instruction at all** — zero skill invocations across
five runs, confirmed robust by the #331 probe. PRE-B forces the Commander load, which forces
the two map-first imperatives to fire. That is a **different treatment, deliberately.**

| | PRE-A (#299) | **PRE-B (this arm)** | POST (after #304) |
|---|---|---|---|
| treatment | corpus offered, never invoked | **Commander loaded, spine driven to `plan`** | Commander loaded, **plus #304's contract** |
| series | stands alone | **pairs with POST** | **pairs with PRE-B** |

Anyone who reads the three arms as one series draws a conclusion from a comparison that was
never valid — and **once the data exists and the runs are gone, that error is undetectable.**
Guarding against it is part of this deliverable, which is why it is here and not in a
footnote.

Three further reasons the two arms are not one series, all measured rather than argued:

1. **Run length differs by ~3x.** PRE-A: 10–61 tool calls. PRE-B: 96–148. Any index-based
   measure (`first_map_read_index`) is on a different scale in each arm. Compare the
   *boolean* `map_before_src`, never the raw indices.
2. **The gradeable artifact changed shape.** The Commander externalises its reasoning into
   `.agent-work/` files, so the final answer is thinner than PRE-A's. The blind grader
   noticed this unprompted on #688 — see §6.
3. **`system/init` differs.** PRE-A installed a corpus into the worktree, so every
   constellation name appeared **twice** (36 entries, 18 duplicated). PRE-B installs
   nothing, so each appears **once** (18 entries, 0 duplicated). Recorded in every
   `treatment.json`.

---

## 1. Treatment verification — the arm's reason to exist

**All five runs: `TREATMENT-VERIFIED`.** Both witnesses agree on every run.

| task | `Skill` call | at index | served by (`Base directory for this skill:`) | verdict |
|---|---|---|---|---|
| #690 | `constellation-commander` | **0** | `C:\Users\fredc\.claude\skills\constellation-commander` | TREATMENT-VERIFIED |
| #688 | `constellation-commander` | **0** | `C:\Users\fredc\.claude\skills\constellation-commander` | TREATMENT-VERIFIED |
| #698 | `constellation-commander` | **0** | `C:\Users\fredc\.claude\skills\constellation-commander` | TREATMENT-VERIFIED |
| #716 | `constellation-commander` | **0** | `C:\Users\fredc\.claude\skills\constellation-commander` | TREATMENT-VERIFIED |
| #704 | `constellation-commander` | **0** | `C:\Users\fredc\.claude\skills\constellation-commander` | TREATMENT-VERIFIED |

The discriminator is the #331 probe's find: Claude Code prefixes loaded skill content with a
literal `Base directory for this skill: <absolute path>` line. It is emitted by the harness
rather than planted, cannot be defeated by truncation, and **names the serving copy
outright**. A `Skill` call alone is not accepted — an invocation with no matching served-by
line is `FAILED-CAPTURE-NO-COMMANDER-LOAD`.

**Every run was served by the GLOBAL copy**, as #332 predicted. `first_corpus_read_index` is
**1** on all five, against `NO-CORPUS-READ` on four of five in PRE-A: the corpus went from
untouched to load-bearing.

`skill_invocations` is 2 per run, not 1: every run loaded `constellation-commander` at call 0
and `constellation-interrogator` later, driving the spine's `understand` step as written.

**Positive control.** Before spending the arm, a standalone forced-load probe
(`preflight/`) confirmed the load works, is served by the global copy, and that
`verify_treatment.py` reports `TREATMENT-VERIFIED` on it. **Negative controls:** the same
verifier returns `FAILED-CAPTURE-NO-COMMANDER-LOAD` on PRE-A's run-704 (no skill call) and on
the #332 check-2 transcript (a `Skill` call to `constellation-triage`, correctly refused as
the treatment). `test_verify_treatment.py` adds 8 mutations, all killed — it caught a real
`lstrip("./")` character-set bug that was silently relocating every in-bounds write.

---

## 2. Corpus fingerprint — before and after, stable

No pinned install. Per #332 the global corpus shadows any worktree copy, so installing a pin
does not deliver it — it only makes the treatment *look* controlled. PRE-B measures the
corpus **as actually installed** and witnesses it instead.

| | BEFORE (pre-run 1) | AFTER (post-run 5) |
|---|---|---|
| `constellation-*` skills | 19 | 19 |
| `SKILL.md` concat sha256 | `fcb6863163c97273d021…` | `fcb6863163c97273d021…` |
| deep tree sha256 (233 files) | `4c2e6465889f8d3fd074…` | `4c2e6465889f8d3fd074…` |
| marker `source_commit` | `74953936` (2026-07-25) | `74953936` |

**Identical, shallow and deep.** All five runs are poolable. The shallow digest reproduces
the launch order's dispatch-time measurement exactly. `74953936` is behind main but genuinely
**pre-#304**, which is all this arm requires.

Method (`fingerprint_global_corpus.py`): sort `constellation-*` dirs by name, concatenate each
`SKILL.md`'s **raw bytes**, sha256. Raw bytes, not decoded text — a line-ending change is a
corpus change and decoding would hide it. `--deep` additionally covers every
`references/`, `templates/`, and `scripts/` file.

---

## 3. Per-run evidence

| task | calls | first `docs/architecture/*` | first `src/*` | **map before src?** | map artifacts | writes | wall-clock | cost |
|---|---|---|---|---|---|---|---|---|
| #690 | 108 | 36 | 23 | **no** | 4 | 6 | 1033s | $9.70 |
| #688 | 124 | 27 | 23 | **no** | 4 | 14 | 1443s | $13.83 |
| #698 | 148 | 57 | 25 | **no** | 7 | 13 | 1347s | $13.97 |
| #716 | 119 | **`NO-MAP-READ`** | **`NO-SRC-READ`** | `NO-MAP-READ` | 0 | 13 | 1160s | $10.84 |
| #704 | 96 | 23 | 7 | **no** | 6 | 11 | 886s | $8.87 |

Total: 595 tool calls, 6 275 s wall-clock (2 241 s at 3-way concurrency), **$57.21**.

`NO-MAP-READ` and `NO-SRC-READ` are **findings** — captured transcripts in which that access
did not occur. `NOT-CAPTURED` (an instrument failure) appears **nowhere**: all five
transcripts are complete and newline-terminated, `exit_code: 0`, no timeouts, zero retries.

**Map artifacts actually read**

- **#690** — `index.md`, `packets/physics.md`, `decisions/`, `decisions/c1-driver-utilization-design.md`
- **#688** — `packets/`, `packets/physics.md`, `packets/data.md`, `decisions/`
- **#698** — `packets/physics.md`, `overlays/*.yml`, `overlays/constraints.yml`, `overlays/purposes.yml`, `decisions/`, `docs/architecture/`
- **#716** — **none**
- **#704** — `docs/architecture/`, `packets/physics.md`, `index.md`, `overlays/`, `overlays/constraints.yml`, `overlays/purposes.yml`

---

## 4. THE FINDING — the imperatives fired, and orientation did not move

**`map_before_src` is `false` on every run that read source: 4 of 4. Orientation at
bootstrap: 0 of 5.** Identical to PRE-A's shape, under a completely different treatment.

Discriminated measures (`discriminate.py`; definitions in §5):

| task | read at bootstrap | map before src | **returned to map after src** | map calls | map cues cited/read | src precision named/opened |
|---|---|---|---|---|---|---|
| #690 | no | **no** (36 vs 23) | **yes** | 4 | 3/4 | 3/7 |
| #688 | no | **no** (27 vs 23) | **yes** | 3 | 4/4 | 3/7 |
| #698 | no | **no** (57 vs 25) | **yes** | 7 | 1/6 | 4/4 |
| #716 | `NO-MAP-READ` | `NO-MAP-READ` | `NO-MAP-READ` | 0 | 0/0 | n/a |
| #704 | no | **no** (23 vs 7) | **yes** | 5 | 0/5 | 1/2 |

This is the arm's substantive result, and it is a **measured negative**, reported as such:

- **The instruction was delivered.** Unlike PRE-A, where nothing instructed anything, here
  the Commander loaded at call 0 in every run and the spine's `context` and `plan`
  imperatives both fired — `COMMANDER_SPINE.template.json:22` (*"…current map read for the
  affected area…"*) and `:40` (*"Map-first: BEFORE authoring `execute.json`, produce a
  mission frame from the current map"*). Line numbers are the **serving** copy's
  (`74953936`); the launch order cites `:22`/`:48` from a different build. The imperatives
  are substantively verbatim.
- **It was obeyed as written, and it did not produce orientation.** Every run *did* produce a
  mission frame from the map, and every run read source first anyway. The instruction says
  *"before authoring `execute.json`"* — and authoring `execute.json` happens at the *end* of a
  long run. **A map-first imperative anchored to a late artifact is not a map-first
  imperative.** That is the mechanism, and it is visible in the indices: #698 read source at
  call 25 and the map at call 57.
- **Use, not orientation — same as PRE-A.** 4 of 4 runs that touched source returned to the
  map afterwards, repeatedly (3–7 map calls each). A ritual read is one touch and never
  again; this is the exact inverse. The map is a verification resource consulted after the
  seam is found, never the thing that finds it.

**Scoped, per doctrine:** *this arm, at n=1 per task, showed the Commander's pathless
map-first imperatives producing 0/5 orientation.* Not *"map-first does not work."*

### The one thing that got worse

**#716 reached `NO-MAP-READ`** — the Commander-loaded run never touched `docs/architecture/`
at all, where PRE-A's #716 did (at call 51). It also reached `NO-SRC-READ`. The Commander
correctly determined the work lives in `constellation-skills`, not f1Brainz, and spent its
119 calls there. Sensible task behaviour; a departure from a standing unconditional
instruction; one observation records both, exactly as rubric §6 frames the axis.

### What this means for #304 — locating it, not defeating it

**This sharpens #304 rather than undermining it.** The result says the *pathless, artifact-
anchored* form of the map-first instruction does not produce orientation even when it is
definitely loaded and definitely obeyed. #304's contribution is a consolidated contract and a
degraded mode. **The untested variable is whether an unconditional, sequenced instruction —
one anchored to "before you touch code" rather than "before you author `execute.json`" —
moves the measure.** PRE-B is the arm that makes that question answerable, and it is why
this arm had to exist.

Honest-null clause discharged: a measured negative here would have been a complete deliverable
either way, and the capture was not shaded toward a result.

---

## 5. Measure definitions — stated because PRE-A's were not mechanised

PRE-A's addendum reports the same four discriminators, but two of its columns were
**hand-derived** and cannot be reproduced from the archived arrays by any single rule.
`discriminate.py` fixes an explicit mechanical definition for each and applies the **same
code** to both arms.

**Therefore: compare PRE-B's numbers to POST's computed by this script. Do not compare them
to the addendum's published columns.**

| measure | definition |
|---|---|
| `read_at_bootstrap` | first map access at tool-call index **< 3**. Strict on purpose: the question is whether the map was the *starting point*. |
| `map_before_src` | verbatim from the frozen extractor. Not recomputed. |
| `returned_to_map_after_src` | ≥1 map access at an index above the first source access. |
| `map_cues_in_plan` | `cited/read` — of the distinct map artifacts the run **actually read**, how many are cited by name in the final answer. |
| `src_precision` | `named/opened` — extension-bearing `src/…` paths in the final `FILES I WOULD CHANGE` list, over those the run opened. |

**Validation against PRE-A's archived transcripts** (`preA-recomputed-discriminated.json`):
the three mechanical columns reproduce the addendum **exactly** — `read_at_bootstrap` 0/5,
`returned_to_map_after_src` yes/yes/yes/n-a/yes, map-call counts 5/5/3/1/4. `src_precision`
reproduces **4 of 5 cells exactly** (3/8, 3/8, 4/6, n/a, 1/1 against the addendum's 3/8, 3/7,
4/6, n/a, 1/1; one denominator differs by one). `map_cues_in_plan` is a genuinely different
definition (a ratio, not a raw count) and its PRE-A column does **not** match the addendum's —
by design, and flagged here rather than reconciled.

Two regex bugs were found against real data and are recorded in the source, because both
failed **silently**: a delimiter whitelist dropped backtick-quoted paths (cost 3 of PRE-A's 5
numerators), and a `/` in the negative lookbehind dropped every **absolute** path — which
PRE-A never had and PRE-B's Commander-driven subjects use throughout (cost run-698 its entire
opened-file count).

---

## 6. Blind grading

Graded by a separate agent that never saw the launch order, was not told a treatment was under
test, was not told which task is the negative control, and received only the frozen rubric's
§1–§3 verbatim plus the five claimed seams. **The author did not grade the runs.**

| task | strict reading | loose reading | deciding words |
|---|---|---|---|
| #690 | **1** | **2** | `src/physics/utilization/class_utilization_observable.py` — "the defect's home" |
| #688 | **1** | **1** | `src/physics/layer2/grip_baseline.py` present but buried in 13 files |
| #698 | **1** | **2** | `src/physics/fingerprint/store.py` — "the retyped boundary; the whole issue is its signature (g2)" |
| #716 | **ACKNOWLEDGED-MISS** | — | "All paths are in `C:\Programs\constellation-skills` … not f1Brainz" |
| #704 | **2** | **2** | `src/physics/instrument_panel/replication.py`; "The repo diff is two files." |

### The §2 tolerance ambiguity recurred — independently

**The grader flagged, unprompted and without knowing PRE-A existed, the exact ambiguity
PRE-A's grader flagged** (issue #333): whether *"up to 4 extra plausible files does not
reduce a 2"* is a hard numeric cap on all extras, or a budget that only counts genuinely
spurious ones. Two independent graders hitting the same sentence is strong evidence the
defect is in the rubric's wording, not in either grader.

**The rubric is frozen at `a226642b` and I have not edited it** — `git status` over
`baselines/` is empty, which is mechanical proof. Both readings are recorded with their
consequences. Which one governs is a ruling for the Admiral and Tommy, and it must govern
**both** PRE-B and POST identically.

### A treatment-induced grading effect, worth more than the scores

The grader noted that **#688's claim points at `.agent-work/issue-688/OWNERSHIP_SCOPE.md`
instead of reproducing its per-file justification**, while #690 and #698 argue in-line. That
is the Commander treatment showing up in the *gradeable artifact*: a Commander externalises
reasoning into files, so the final answer is systematically thinner than a generic agent's.

Consequence: PRE-B's seam scores are **not** comparable to PRE-A's on the grading axis either,
for a second and independent reason. POST will carry the same shape, so the PRE-B/POST pairing
survives — but a future packet should either inline the external artifact or state that it
was withheld. Filed as #351.

Also noted by the grader: #688's list includes `tests/unit/physics/test_class_utilization_observable.py`,
which belongs to **#690's** subsystem. **This is not cross-run contamination** — every run had
its own pinned worktree, its own process, and its own (empty) per-project memory directory,
all verified. It is the subject's own error.

---

## 7. Nothing landed in f1Brainz — and what the evidence actually is

The launch order's item 6 asks for "zero `Write`/`Edit`/`NotebookEdit` calls." **That standard
is unachievable by construction here**: the Commander's `plan` step *is* authoring a mission
frame and `execute.json`. A run with zero writes has not reached the plan step. Raised to the
Admiral before launch and filed as **#347**; this arm reports a strictly stronger, auditable
standard instead.

**57 writes across five runs. Every one enumerated with its resolved target. Exactly one out
of bounds.**

| check | result |
|---|---|
| writes inside the run's own pinned worktree | **56 of 57** |
| writes inside the worktree but outside `.agent-work/` | **0** |
| forbidden git/gh operations (`push`, `commit`, `merge`, `pr create`, `issue create/comment/edit/close`) | **0**, all five runs, both pattern sets |
| per-worktree `git status --porcelain` before sweep | exactly **one** untracked dir each — the Commander's own `.agent-work/<work-id>/` |
| f1Brainz **main** checkout | byte-identical to the session-start snapshot |
| `constellation-skills` main checkout (Tommy's uncommitted work) | byte-identical to the session-start snapshot |
| worktrees swept | all five removed, `git worktree prune` run, `C:/Programs/f1bwt` gone |

The per-worktree delta check is the strong one: each worktree's *only* change was its own
Commander directory. That proves more than a `git_unchanged` boolean, and it is why
`git_unchanged: false` on all five runs is expected rather than alarming — `.agent-work/` is
tracked in f1Brainz, so the new directory shows up.

### The one out-of-bounds write — reported, not buried

**run-698, tool call 147 of 148**, edited a Claude Code auto-memory file:

```
C:\Users\fredc\.claude\projects\C--Programs-f1Brainz\memory\editable-install-pth-worktree-trap.md
```

It appended an accurate technical note about `.pth` finder-hook editable installs. Assessment,
stated plainly:

- **Not in f1Brainz.** It is the harness's per-project memory store, not the repository. No
  git object, no tracker, no push. "Nothing landed in f1Brainz" holds.
- **It cannot have influenced this run's measures.** Call 147 of 148 — after the mission
  frame (115) and `execute.json` (122). The ordering measure, the plan, and the claimed seam
  were all fixed before it happened.
- **It cannot have influenced any other run.** Each measured worktree gets its own project key
  (`C--Programs-f1bwt-pb690` …), and **all five of those memory directories are empty**.
  Verified. Zero memory-injection hits in any transcript.
- **It is a real durable side effect on Tommy's environment**, and it *could* contaminate a
  future arm run with cwd under `C:/Programs/f1Brainz` proper.

**I have not reverted it.** The content is accurate and useful, deleting a user's memory is
destructive, and the call belongs to Tommy. Filed as **#352** so the decision is visible
rather than absorbed. The general class — a measured subject reaching outside its sandbox into
global user state — is what matters, and it will recur.

---

## 8. Declared limitations

Carried forward from the frozen rubric §6, plus what this arm added.

1. **n = 1 per task.** No replication, no variance estimate. The seam scores support a
   direction-of-travel note only, never a lift claim.
2. **Seam-lift power ≈ 1 partially-discriminating task (#698).** The issue bodies give the
   paths away; #688 and #704 behave as controls.
3. **The ordering measure is a manipulation check, not an outcome.** In PRE-A it showed the
   treatment was never delivered. Here it shows the treatment *was* delivered and produced no
   orientation — a stronger use of the same instrument.
4. **Brief confound, unchanged and carried deliberately.** The `FILES I WOULD CHANGE` demand
   pushes subjects toward path-hunting and away from conceptual orientation — i.e. **against**
   the hypothesis. It is byte-identical to PRE-A's, so it cannot explain a PRE-B/POST
   difference.
5. **Subagent-internal reads are invisible.** Moot: `subagent_dispatch_count` is **0** on all
   five runs.
6. **New — the frozen extractor's call-level corpus rule, measured rather than patched.**
   That rule credits any call touching `.claude/skills` as `skill-corpus` and nothing else. It
   was written for a corpus installed *inside* the worktree; under PRE-B the corpus is global
   and the Commander invokes its scripts constantly, so a combined call could in principle
   swallow a genuine map read. **Exposure measured: 6 calls across five runs.** All six are
   engine *attestation* commands whose `--finding` prose mentions `docs/architecture`, and
   **every one sits at an index above its run's `first_map_read_index`** (68>36, 101>36, 53>27,
   76>57, 136>57, 88>23). **The ordering measure is unaffected.** The extractor was not
   modified; it is behaving correctly.
7. **New — human-gated spine steps under a headless subject.** `constellation-commander` is
   the human-driven variant and its spine carries `user-decision` postconditions (`plan` c3
   "plan approved", c5 "findings triaged by the human"). The launch order names this skill
   explicitly, so it is what ran. The brief resolves the gate with one added clause ("no human
   is reachable … decide it yourself and carry on"); no run stalled. Recorded because it is a
   deviation from how that skill is meant to be used, not because it bit.

---

## 9. Method — what was held and what changed

**Held byte-identical to PRE-A:** the five tasks (#690, #688, #698, #716, #704) read from the
frozen `issues.frozen.json` snapshot, never live; the f1Brainz pin
`3541d2929b19de37107ae13e56776b7162d07255`, mechanically re-checked per run; the model
`claude-opus-5`; the `FILES I WOULD CHANGE` output demand; the plan-stage truncation point;
the frozen `extract_ordering.py`, `verify_capture.py`, and the rubric at `a226642b`.

**Changed — the treatment, applied by `str.replace` against `capture_baseline.BRIEF` under
presence assertions, never retyped.** Two substitutions, both diffed verbatim per run in
`runs/run-<N>/brief_diff.md`:

1. **The treatment**: load `constellation-commander`, drive the spine to `plan`, stop, plus
   the no-human-reachable clause.
2. **A scope carve-out that substitution 1 makes necessary**: the frozen blanket "do not
   modify" would forbid the mission frame and `execute.json`. Narrowed to `.agent-work/` only;
   commit / push / PR / issue-comment prohibitions untouched.

**Also changed, and forced by #332:** no corpus is installed. `capture_preb.py` *asserts* the
absence of `<worktree>/.claude/skills` — so `init` listing each name exactly once is a
positive check rather than a hope.

The subject was told nothing about epic #298, maps, architecture, or measurement beyond what
invoking the Commander requires. The environment was scrubbed of `CLAUDE_*`. Captures ran
detached, never in a foreground tool call — the failure mode that cost the #331 probe a
transcript.

---

## 10. Reproduction

```
py .agent-work/epic-298/baselines/extract_ordering.py --self-test        # 33 checks, frozen instrument
python .agent-work/epic-298/preb/test_verify_treatment.py                # 8 mutations on the treatment verifier
python .agent-work/epic-298/preb/verify_treatment.py .agent-work/epic-298/preb/runs/run-*
python .agent-work/epic-298/preb/discriminate.py .agent-work/epic-298/preb/runs/run-*
python .agent-work/epic-298/preb/fingerprint_global_corpus.py --out /tmp/now.json --expect-shallow fcb6863163c97273
```

Archive layout — `runs/run-<N>/`:

| file | what it is |
|---|---|
| `stream.ndjson` | full tool-call transcript |
| `brief.md`, `brief_diff.md` | exact prompt, and every byte that differs from PRE-A's |
| `meta.json` | arm label, pin, model, corpus mode, timings, git before/after |
| `ordering.json` | the **frozen** extractor's output |
| `treatment.json` | Commander load, serving copy, write audit, forbidden ops, suppression exposure |
| `final_answer.txt`, `claimed_seam.txt` | the plan, and the graded claim |
| `authored/` | the Commander's own `.agent-work/<work-id>/` — mission frame, `execute.json`, spine |
| `stderr.txt` | launcher stderr |

Arm-level: `corpus-fingerprint-{BEFORE,AFTER}.json`, `preB-discriminated.json`,
`preA-recomputed-discriminated.json`, `GRADER_PACKET-PREB.md`, `preflight/`,
`run_all_preb.log`.

---

## 11. Filed to the tracker

| # | what |
|---|---|
| **#346** | `constellation-diagnose` does not register its description — un-triggerable by intent (18 of 19 skills register; found via `init.skills` from a fresh process) |
| **#347** | The "zero write calls" evidence standard is unachievable for any skill-loaded measured arm; adopt enumerate-and-bound |
| **#351** | Commander runs externalise reasoning into `.agent-work/`, thinning the gradeable artifact — grading packets must inline it or declare it withheld |
| **#352** | A measured subject reached outside its worktree and edited a global auto-memory file |

## 12. Open for the Admiral and Tommy

- **The §2 tolerance ambiguity (#333) is now confirmed by two independent graders.** It must
  be ruled on **before** #307 pairs PRE-B with POST, and the same reading must govern both.
- **The map-first imperative is anchored to `execute.json`, not to touching code** (§4). If
  #304 does not change that anchor, PRE-B predicts the POST arm returns the same 0/5.
- Whether #352's memory edit should be reverted.
