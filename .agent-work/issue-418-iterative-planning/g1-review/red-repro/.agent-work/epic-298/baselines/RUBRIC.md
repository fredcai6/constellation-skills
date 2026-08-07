# Frozen grading rubric — epic #298 map-first measurement

**FROZEN BEFORE ANY MEASURED RUN EXECUTED.** Committed in its own commit, ahead of any
commit carrying run output, so git history proves the ordering. A rubric written after
seeing results grades the results.

Hardened by a cold adversarial critic (no authoring context) before freezing. Findings it
raised are resolved in-place below; the three it could not resolve locally are floated to
the Admiral in §8 and are flagged where they bite.

- **Corpus:** f1Brainz, pinned at `3541d2929b19de37107ae13e56776b7162d07255`
  (2026-08-01 09:52 -0700). Both arms MUST use this pin.
- **Briefs:** frozen at `issues.frozen.json`. Both arms MUST read briefs from that
  snapshot, never live from `gh` — the commit is pinned but issue text is not, and the
  brief is where every path give-away lives.
- **Also pinned for both arms:** model (`claude-opus-5`), permission mode (`acceptEdits`),
  one fresh worktree per run, corpus installed at `<worktree>/.claude/skills`.
- **Arm captured here:** PRE-change (before #304's contract merges).
- **Author:** commander-299. **Grader:** a separate agent that never saw LAUNCH_ORDER-299
  and never sees §5–§8 of this file.

---

## 0. What the PRE arm actually is — corrected before capture

**The launch order's arm label does not survive contact with the corpus, and the correction
matters more than any other line in this file.**

The order labels this arm *"scattered prose, no canonical entrypoint, no degraded-mode
contract"* and rules (`decision:baseline-is-informal-map-not-no-map`, `@grade: settled/human`)
that it must never be called "no map." The "never no map" half is right and is reinforced
below. **The "no canonical entrypoint" half is false.**

`git show 3541d292:CLAUDE.md` — the file Claude Code auto-loads into every session in this
repo — line 7, under the heading *"Also read before touching an area:"*:

```
- `docs/architecture/index.md` — structural map: module boundaries, relationships, dead paths
```

Verbatim again at `AGENTS.md:27`, and again at `README.md:203`. So a canonical
architecture-map entrypoint **is already named, at an exact path, in the always-loaded
bootstrap file**, before #304 does anything.

Separately, the pre-#304 corpus already instructs map-first orientation — pathlessly — at
two points: `context` ("Read the current map (packets, overlays, decision anchors) for the
area the ask touches") and `plan` ("Map-first: BEFORE authoring execute.json, produce a
mission frame from the current map").

**Therefore the true PRE arm is:** *canonical entrypoint already present in the target
repo's auto-loaded CLAUDE.md, plus a pathless map-first instruction in the corpus, with no
consolidated contract and no degraded-mode behaviour.*

What #304 adds on top of that is **a contract and a degraded mode — not an entrypoint.**
The measurement question it can actually answer is therefore *"does a contract help when an
entrypoint already exists"*, which is narrower than the order's framing and has a much
smaller expected effect on the ordering measure.

This contradicts a `settled/human` pre-ruling, which per decision-fixedness doctrine is not
mine to unsettle. It is **floated to the Admiral (§8, F1)**. The capture proceeds because
the transcripts are valid raw data under either framing — only the label on them changes.

---

## 1. Ground truth — the correct seam per task  *(grader sees this section)*

Determined by the author reading f1Brainz at the pin, **before the runs**, and independently
re-verified by a cold critic against the same commit. Every path was located with
`git grep` / `git show` against `3541d292`.

### #690
**Primary seam: `src/physics/utilization/class_utilization_observable.py`**
Boundary counterpart: `src/physics/layer2/grip_store.py` (`get_grip_at`).

Evidence: `class_utilization_observable.py:122` is
`return float(math.hypot(float(mu), float(sigma)))` — the σ⁺ scale at issue. Line 77 imports
`get_grip_at` from `src.physics.layer2.grip_store`; line 188 consumes it. The change belongs
on the **utilization** side (how G is scaled into a per-class band), not in `grip_store`.

*2*: names `class_utilization_observable.py`. *1*: names only `grip_store.py`, or only
`src/physics/utilization/` without the file. *0*: neither.

### #688
**Seam: `src/physics/layer2/grip_baseline.py`** (`rain_flag_from_raw`).
Evidence: `git grep -ln rain_flag_from_raw 3541d292 -- src/*` returns exactly this file.

*2*: names `grip_baseline.py`. *1*: names `src/physics/layer2/` without the file. *0*: neither.

### #698 — scored on seam-finding ONLY
**Seam: `src/physics/fingerprint/store.py`**, with `src/physics/fingerprint/address.py`
(`CellAddress`) as the type the API must be tightened onto.
Evidence: `git grep -ln 'class DriverFingerprintStore' 3541d292` → `src/physics/fingerprint/store.py`;
`class CellAddress` → `src/physics/fingerprint/address.py`. Both unique at the pin.

Sub-concerns H2 (a script's `sys.path` guard) and H3 (gitignore) are **not scored** — score
only the component that owns the store API. Naming H2's script or `.gitignore` is neither
credit nor penalty, and does **not** count against the spurious-file budget.

*2*: names `store.py`. *1*: names `src/physics/fingerprint/` without the file, or only
`address.py`. *0*: neither.

### #716
**Ground truth: there is no seam in this repository.**
Evidence: `git ls-tree -r --name-only 3541d292 | grep -E '(run_crew|verify_agent_feedback)\.py'`
returns nothing; neither script exists in f1Brainz at the pin. `work_id` appears nowhere
under `src/` or `scripts/`.

Because no in-repo seam exists, this task is scored on the **§3 axis instead of §2** — a run
cannot name a correct f1Brainz file, because there is none.

### #704
**Seam: `src/physics/instrument_panel/replication.py`** (`_axis_means` L103,
`main_effect_margin_uncertainty` L408). Evidence: `git grep -n` at the pin returns both
definitions in that one file, and only there.

*2*: names `replication.py`. *1*: names `src/physics/instrument_panel/` without the file.
*0*: neither.

---

## 2. Scoring scale — seam identification  *(grader sees this section)*

| Score | Meaning |
|---|---|
| **2** | Names the ground-truth owning file. No material miss. |
| **1** | Partial — names the owning component/directory but not the file; or the right file inside a materially spurious list; or only the far side of a cross-module boundary. |
| **0** | Wrong seam — neither the owning file nor its component. |
| **n/a** | Tasks with no in-repo seam; scored on §3 instead. |

Spurious-file tolerance: up to **4** extra plausible files does not reduce a 2. Beyond that,
or a claim centred on an unrelated component, drops to 1.

Score the claimed file list **as written**. Do not credit intent, and do not penalise a run
for naming files that a task's own text told it to consider.

## 3. Coverage axis  *(grader sees this section)*

For any task scored `n/a` under §2:

| Value | Meaning |
|---|---|
| **ACKNOWLEDGED-MISS** | The run states the work is not in this repo, or that it cannot locate a seam here, explicitly. |
| **SILENT-CRAWL** | The run proposes an in-repo seam anyway without stating the gap. |
| **CONFUSED** | Neither — no locatable position taken. |

---

## 4. Ordering measure — mechanical, and a MANIPULATION CHECK, not an outcome

Extracted by `extract_ordering.py` from each run's `stream-json` tool-call sequence. Not
graded, not judged.

- `first_map_read_index` — first tool call touching `docs/architecture/**`
- `first_src_read_index` — first tool call touching `src/**`
- `first_corpus_read_index` — first touch of the installed corpus (`.claude/skills/**`)
- `map_files_read` — every `docs/architecture/**` path touched, in order
- `subagent_dispatch_count`

**Four reserved literals, mutually distinct, never blank and never zero:** `NO-MAP-READ`,
`NO-SRC-READ`, `NO-CORPUS-READ` (captured, absent — each a **finding**) and `NOT-CAPTURED`
(no usable transcript — a **missing datum**). A non-reading is not a low reading, and an
instrument failure must never be able to present as a clean result.

Classification is **call-level**: any call with a path argument under `.claude/skills` is
`skill-corpus` and credits nothing else. `prompt`/`query` text is `mention`, never a read —
a subagent dispatch that names a map path did not read it.

**What this measure cannot see, declared up front:** reads performed *inside* a dispatched
subagent never reach the parent stream. `subagent_dispatch_count` is reported so a low map
count on a subagent-heavy run is flagged as possibly-hidden rather than read as a finding.

**Status of this measure (critic finding S5, accepted).** The treatment is *"tell the agent
to consult a canonical map entrypoint"*; this measure asks *"did the agent consult the map
first."* Post-treatment movement therefore confirms **the treatment was delivered**, not
that it produced better work. It is a **manipulation check**. The **outcome** is the §2 seam
score. #307 must not build a value claim on this measure alone — combined with §0 (the
entrypoint already exists pre-change) its expected movement is small and its interpretation
is weak.

**Timeout / non-completion disposition.** A run that terminates without emitting
`FILES I WOULD CHANGE` is `NOT-CAPTURED` on the seam axis, **retains** its ordering data, and
is re-run once. A second failure is recorded `NOT-CAPTURED` and excluded from means in both
arms.

**Falsification floor.** `extract_ordering.py --self-test` runs 33 checks including a
checked-in **real** `claude -p --output-format stream-json` excerpt
(`fixtures/real-stream-excerpt.ndjson`). Both were verified to go red under deliberate
mutation — collapsing `NO-MAP-READ` to `0` kills 1 check; restricting field extraction to
`input.command` kills 9. The real fixture is load-bearing: the first version of the
extractor was tested only against synthetic `command` inputs and would have silently missed
every `Read(file_path=...)` in a live run, reporting total instrument failure as a clean
`NO-MAP-READ` finding.

---

## 5. What would show the map did NOT help — the losing conditions

Stated in advance. Four of six are decidable on the PRE arm alone, so this rubric can lose
on the data being collected here, not only on data someone else collects later.

| id | Losing condition | Decidable on |
|---|---|---|
| **L1 — no lift** | Post-arm mean seam score ≤ pre-arm mean seam score across the scored real tests. | pre + post |
| **L2 — ceiling** | The PRE arm scores 2 on **every** scored real test. No headroom exists, so #304 cannot demonstrate value on this instrument regardless of the post arm. | **PRE ALONE** |
| **L3′ — ritual control** | Post-arm `map_before_src` on **#704** ≥ post-arm `map_before_src` on the real tests. The contract would then be inducing map consultation even where §1 says the map cannot help — ritual compliance, not map value. | pre + post |
| **L4 — orientation without the map** | **≥1** scored real test where a PRE run reaches `NO-MAP-READ` and still scores 2. Correct orientation demonstrably does not require the map on this corpus. | **PRE ALONE** |
| **L5 — read but useless** | **≥1** scored real test where a PRE run has `map_before_src == true` and still scores 0–1. Map *access* is not the binding constraint, so easier access cannot fix it. | **PRE ALONE** |
| **L6 — map as confirmation, not orientation** | PRE runs reach the map only **after** source (`map_before_src == false`) on ≥2 scored real tests while their mean seam score is ≥1.5. The map is then a confirmation step on work already correctly placed, and cheaper access does not change placement. | **PRE ALONE** |

L3 in the pre-critic draft was *"post-arm seam lift on #704 ≥ lift on the real tests."* That
condition was **decorative and has been replaced**: #704's body names its file verbatim, so
the PRE arm scores 2, lift is bounded at 0, and the condition could never fire except when
L1 already had. L3′ moves the control onto an axis with actual headroom.

**Pre-registered expectation (so any other result is a declared surprise, not a retrofitted
narrative):** given §0 and §6, I expect the PRE arm to score at or near 2 on #688 and #704,
1–2 on #690, 1 on #698, ACKNOWLEDGED-MISS on #716, and map reads to be **present but not
first** on most tasks. That expectation makes **L6 the most likely losing condition to fire**.

---

## 6. Known power limitations — declared before the runs, not after

The seam-lift measure is substantially weaker than the frozen task set implies. #307 must
not read it as five equal data points.

**Cause.** The launch order's per-task grain reasoning is title-level, but a realistic brief
carries the issue **body**, and the bodies give paths away:

| task | body hands over the target? | seam-lift power |
|---|---|---|
| #690 | **yes** — `class_utilization_observable` is the filename minus `.py`, in the body's first sentence; the body also rules `grip_store` out of scope | **degraded** |
| #698 | partial — names classes (`DriverFingerprintStore`, `CellAddress`), not paths | **partial — the only real one** |
| #688 | **yes** — `src/physics/layer2/grip_baseline.py` verbatim | degraded |
| #716 | **yes** — body states the scripts are not in this repo | dead on both axes |
| #704 | yes — by design (control) | control |

**Honest total: ~1 partially-discriminating task (#698), not five and not two.** The
pre-critic draft claimed "roughly two" and put #690 in the *full* column; that was wrong —
a run can score 2 on #690 by transcribing the body's opening clause, and a blind grader
cannot distinguish transcription from derivation.

**The coverage axis (§3) is also give-away'd.** #716's body says outright that the scripts
live in the constellation-skills install, so `ACKNOWLEDGED-MISS` is transcription rather than
detection. §3 retains near-zero discriminating power. It is still recorded, because a run
that manages a SILENT-CRAWL *despite* being told would be a strong finding.

**Replication: n = 1 per task.** No repeats are captured. Run-to-run variance in "which files
would you change" is large and here entirely unestimated, so a single 1→2 movement between
arms is indistinguishable from noise. **The seam-lift measure as captured cannot support a
lift claim — only a direction-of-travel note.** Raising k is floated in §8 (F2).

**Brief confound, declared (critic finding, accepted as declare-not-fix).** The brief demands
a final `FILES I WOULD CHANGE` list. Naming a path list as the deliverable pushes a subject
toward path-hunting (grep/glob for filenames) and away from conceptual orientation — i.e.
**away** from the behaviour a map is meant to produce. The bias runs *against* the
hypothesis, so it cannot manufacture a win, but it depresses map-reading in both arms and
#307 should read the ordering measure with that in mind.

---

## 7. Grading protocol

The grader is a separate Sonnet agent that:
1. never saw LAUNCH_ORDER-299 and never sees §0 or §5–§8 of this file,
2. receives only §1, §2, §3, and each run's claimed seam text,
3. is **not** told which task is the control, and receives §1 with the design-role
   annotations removed (they were present in the pre-critic draft and are gone from §1 above —
   the headings, the phrase "negative control," and "a map should not help here" all leaked
   it directly),
4. returns a score plus the quoted words that decided it.

**Honest limit of the blinding:** a grader applying §3 necessarily learns that #716 has no
in-repo seam. That leak is unavoidable — §3 must be applied to it — and is recorded rather
than papered over. The **control** (#704) is genuinely blinded; the **coverage probe** is not.

The author does not grade the runs.

## 8. Floated to the Admiral — unresolved at freeze time

- **F1 — the arm label.** §0. Contradicts a `settled/human` pre-ruling; only the ruling tier
  may unsettle it. Capture proceeds; the label on the captured data is the open question.
- **F2 — replication.** §6. n=1 cannot support a lift claim. k=3 is affordable only while
  the pre-change window is open (i.e. before #304 merges) and is unrecoverable after.
- **F3 — instrument power.** §6. ~1 discriminating task. Whether that is worth pairing at
  #307, or whether the task set needs re-cutting *before* the post arm is spent, is the
  Admiral's and Tommy's call, not mine.
