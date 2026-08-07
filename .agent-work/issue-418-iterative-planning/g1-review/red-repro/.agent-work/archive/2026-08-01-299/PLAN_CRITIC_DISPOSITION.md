# Cold plan critic — findings and disposition (#299)

Critic: fresh Opus subagent, no authoring context, given only `RUBRIC.md`,
`extract_ordering.py`, `capture_baseline.py` and the measurement question. Run **before**
the rubric froze, per `lesson:cold-critic-mandatory-for-measurement-dependent-plans` (this
plan's acceptance IS a before/after measurement, so the critic is mandatory, not bias-to-yes).

Delegated triage: in delegated mode the Admiral is the ratifying tier and the human ratifies
at the epic boundary. Findings that exceed my latitude are **floated**, not self-disposed.

| # | Severity | Finding | Disposition |
|---|---|---|---|
| **B1** | blocking | Arm label false — f1Brainz `CLAUDE.md:7` already names `docs/architecture/index.md`, so the pre arm is not "no canonical entrypoint"; #304 adds a *contract*, not an entrypoint. | **VERIFIED against the world, then FLOATED (F1).** Contradicts a `settled/human` pre-ruling; doctrine says only the ruling tier unsettles it. Rubric §0 records the corrected fact and the float. Capture proceeds — transcripts are valid under either label. |
| **B2** | blocking | The losing conditions do not tile the outcome space; L4/L5 carry no quantifier, so their firing would be decided after seeing data. | **ACCEPTED, FIXED.** L4/L5 quantified to "≥1 scored real test"; **L6 added** for the uncovered region (map read but not first, scores already decent); expected outcome pre-registered so a surprise is declared, not retrofitted. |
| **B3** | blocking | L3 decorative — #704's score is capped at 2 so post-arm lift is bounded at 0; it could only fire when L1 already had. | **ACCEPTED, FIXED.** Replaced with **L3′**, keyed to `map_before_src` on the control — an axis with headroom, and it catches the failure a canonical-entrypoint contract actually risks (ritual compliance). |
| **B4** | blocking | Code bug: an absent **source** read was recorded with `NO-MAP-READ`, and the self-test *asserted* the defect. | **ACCEPTED, FIXED.** Distinct `NO-SRC-READ` literal added; M4 rewritten to assert the correct behaviour. Four reserved literals now verified mutually distinct. |
| **B5** | blocking | Blind-grading leaks — §1 said "(NEGATIVE CONTROL)" and "A map should not help here." | **ACCEPTED, FIXED.** All design-role annotations stripped from the grader-facing sections. §7 now states the honest limit: the control is blinded, the coverage probe cannot be (the grader must apply §3 to it). |
| **B6** | blocking | Named surviving mutant: `_synth` only ever used `input.command`, so field extraction for `file_path`/`pattern` was untested. | **ACCEPTED, FIXED — and it was real.** Verified against an actual transcript: Read uses `file_path`, Glob uses `pattern`. A real fixture is now checked in at `fixtures/real-stream-excerpt.ndjson`; restricting extraction to `command` drives **9 checks red**. Also added: near-miss under `docs/` is not the map; `Grep(path="src")` counts. |
| **B7** | blocking | §6's power table wrong — #690 is give-away'd (`class_utilization_observable` *is* the filename), and the coverage axis is give-away'd too. Real power ≈1 task, not two. | **ACCEPTED, FIXED + FLOATED (F3).** Table corrected, #690 moved to degraded, coverage axis declared dead. My first float to the Admiral under-reported this and has been corrected. |
| **B8** | blocking | n=1 per task, no variance estimate; a 1→2 movement is indistinguishable from noise. | **ACCEPTED, DECLARED + FLOATED (F2).** Rubric now states the seam-lift measure cannot support a lift claim, only direction-of-travel. k=3 is affordable only while the window is open — the Admiral's call. |
| **S1** | serious | `prompt`/`query` counted as reads (fabricates map reads); subagent-internal reads invisible (hides real ones). | **ACCEPTED, FIXED.** `mention` bucket, excluded from both indices; `subagent_dispatch_count` reported so a low map count on a subagent-heavy run is flagged as possibly-hidden. The invisibility limit is declared in §4 rather than papered over. |
| **S2** | serious | `src/` regex missed `Grep(path="src")`; the miss biased `map_before_src` toward True — i.e. toward the hypothesis. | **ACCEPTED, FIXED.** Regex accepts a bare `src`. M7 covers it. |
| **S3** | serious | Token-level corpus strip defeated by `Grep(pattern="docs/architecture", path=".claude/skills")` — the exact case the split existed for. | **ACCEPTED, FIXED.** Classification is now **call-level**: any path argument under `.claude/skills` makes the whole call `skill-corpus`. M5b covers it. |
| **S4** | serious | `first_map_read_index` could be an integer while `map_files_read` said `NO-MAP-READ`. | **ACCEPTED, FIXED.** `map_files_read` is derived from the index, so the two cannot contradict; a directory-only touch records `docs/architecture/`. M11 covers it. |
| **S5** | serious | The ordering measure is a manipulation check, not an outcome, and §6 promoted it to primary. | **ACCEPTED, FIXED.** §4 now labels it a manipulation check explicitly and tells #307 not to build a value claim on it. This matters more given B1. |
| **S6** | serious | Issue bodies fetched live; the arms could silently diverge on their most load-bearing shared input. | **ACCEPTED, FIXED.** `freeze_issues.py` snapshots all five to `issues.frozen.json`, committed with the rubric; `capture_baseline.py` reads only the snapshot. |
| **S7** | serious | No declared disposition for a timed-out run. | **ACCEPTED, FIXED.** §4: `NOT-CAPTURED` on the seam axis, ordering data retained, re-run once, second failure excluded from means in both arms. |
| **S8** | serious | Cross-run contamination in a reused worktree with writes enabled. | **ACCEPTED, FIXED.** One fresh worktree per run (already mandated by the order); `capture_baseline.py` now **refuses to launch** into a non-pristine worktree. Permission mode left at `acceptEdits` deliberately — `plan` mode is a different mode with different prompting and would confound the measure. |
| **S9** | serious | Whether the treatment was delivered at all was computed then discarded. | **ACCEPTED, FIXED.** `first_corpus_read_index` + `NO-CORPUS-READ` added. |
| minor | minor | `See §5` mis-citation; truncated evidence; #698 tolerance too tight; `store.py:97-98` cites the wrong class. | **ACCEPTED.** Mis-cite and leaky sentence deleted with B5; matched evidence recorded per call; #698 tolerance widened to 4 and H2/H3 explicitly excluded from the spurious budget; the wrong line-cite removed rather than corrected, since the seam file was never in doubt. |
| brief | declare | `FILES I WOULD CHANGE` pushes toward path-hunting and away from conceptual orientation. | **ACCEPTED as declare-not-fix**, per the critic's own read: the bias runs *against* the hypothesis so it cannot manufacture a win. Declared in §6. |

**Critic findings judged sound and left alone:** §1 ground truth (independently re-verified at
the pin, every seam confirmed), the `NO-MAP-READ`/`NOT-CAPTURED` separation for the map index,
corpus-strip ordering, and `capture_baseline.py`'s pin assertion / corpus round-trip / env scrub.

**Net:** 8 blocking findings, 9 serious. Three floated, the rest fixed before the freeze. Two
would have silently destroyed the measurement (B4+B6 together turn total instrument failure
into a clean-looking `NO-MAP-READ` finding). Fourth confirmation of
`lesson:cold-critic-mandatory-for-measurement-dependent-plans`, and the first where the critic
caught a defect in the *measuring instrument* rather than the plan around it.
