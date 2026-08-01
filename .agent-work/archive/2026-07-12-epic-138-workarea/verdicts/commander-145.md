# Commander Verdict — issue #145 (three measurement arms, #138 D6)

**Status: COMPLETE — measurement analyzed. Kill-condition EVIDENCE presented; the shrink/kill call is the HUMAN's (no removal recommendation here).**
Commander: commander-145 (delegated, opus). The measurement was run by the human interactively (see "Blocker history"); this Commander did the arm-construction design, the analysis, and this verdict.

This is a **diagnosis pass (N=3), not certification.** It does not decide any removal.

---

## Per-arm results (N=3, strict terminal completion)

Strict terminal completion = all three process checks pass (`artifact_present` + `tests_green` + `spine_completed`, the last requiring an engine-provenance terminal spine: 10/10 tasks `complete`, monotonic lease **released**, `e-<task>-<n>` evidence grammar, hash-chained journal).

| Arm | Strict completion | Fenced (excluded) | corpus_id | Rail | Hooks |
|---|---|---|---|---|---|
| **corpus-only** (clamps only) | **2 / 3** | 4 (session-limit) | `sha256:ad7d24b8…` | absent (verified) | none |
| **+rail** (clamps+rail) | **3 / 3** | 0 | `sha256:f0c95f4c…` | present (verified) | none |
| **+rail+hooks** (clamps+rail+hooks) | **3 / 3** | 4 (session-limit) | `sha256:2c283df1…` | present (verified) | fire in-sandbox |

Baseline for comparison (#129 arc): ~1/3 pre-clamp → 3/3 post-clamp, N=3. All three arms here carry the clamps, so all three sit at or near that post-clamp 3/3 ceiling.

## Failure-shade breakdown (derived by commands; the one failure is the whole signal)

Exactly **one** non-fenced failure across all 9 counted runs: **corpus-only / run-1**.

**Which process check failed** (command, pasted):
```
$ py evals/euler-1-multiples/checks/artifact_present.py  <corpus-only/run-1>   → PASS  (exit 0)
$ py evals/euler-1-multiples/checks/tests_green.py       <corpus-only/run-1>   → PASS  (exit 0)
$ py evals/euler-1-multiples/checks/spine_completed.py   <corpus-only/run-1>   → FAIL:
    "found 1 spine(s) but none is an engine-driven terminal spine
     (last: not all tasks reached `complete` …)"
```
So the Euler deliverable was **done** (solution.py + green pytest); only the **workflow** was abandoned.

**How far the spine got** (command over engine truth — spine JSON + journal):
```
spine: run-1/workspace/.agent-work/euler-problem-1/spine.json
  status tally: {complete: 4, in-progress: 1, pending: 5}
  per-step: init✔ context✔ understand✔ plan✔ execute[in-progress] reconcile/triage/review/feedback/archive[pending]
  lease status: ACTIVE   (never released)
$ tail -3 spine.json.journal   → seq 20 = {"verb":"start","task":"execute", …}   (last recorded action)
```
The transcript (`corpus-only/run-1/transcript.txt`, 8 lines) captured only a nested **reviewer** crew's tail ("Reviewer work complete … APPROVE … Lease released" — that is the *reviewer's* child lease, not the commander's). So the reliable shade signal is the **engine state**, which is exactly what `spine_completed` keys on.

**Shade = "the working solution is the MIDDLE, not the end" abandonment at `execute`.** The commander drove init→plan, dispatched crews at execute, the implementer produced a green solution and the reviewer APPROVED — and the commander then **stopped the moment the code existed**: it never integrated the crew result, advanced `execute`, drove reconcile→archive, or released its lease. This is the single most common failure this tier is warned about, and it is **precisely** the shade #138's engine-side channels target — the rail's mid-flight string ("A working solution is the MIDDLE of this run — you are N steps from done") and the Stop hook (refuse a mid-flight turn-end while the lease is active). In this arm neither existed; the agent took exactly that exit.

**Provenance quality of the 8 passers (command scan):** uniform across all arms — every passing run is 10/10 `complete`, lease `released`, journal 44–45 lines. **No shade-shift among passers, no fabrication, no barely-passing gap between arms.** The only difference between corpus-only and the two channel-bearing arms is the single abandonment.

## Arm-construction record (verified; reproducible)

Construction by **subtraction** from merged main (c9b1cf99), matching the traced mechanic that the corpus's bundled engine copy is taken from `REPO_ROOT/scripts/` of **whichever checkout runs `run_skill_eval.py`** (not `--worktree`):

- **corpus-only** — ran from scratch worktree `C:/Programs/constellation-wt-145-corpusonly` (detached @ c9b1cf99) whose `_rail()` was edited to `return ""` (human-authorized in the loop, dated provenance comment in the file). **Behaviorally verified:** the installed corpus engine emits **0 RAIL lines** on `current`. Clamps intact (skill text at c9b1cf99).
- **+rail** — ran from merged `wt-145` as-is. **Behaviorally verified:** installed corpus engine emits **1 RAIL line** on `current`.
- **+rail+hooks** — merged corpus + `.claude/settings.json` + `scripts/hooks/spine_rail.py` injected into each run's workspace via a scenario fixture overlay (`euler-1-hooked`, **task.md byte-identical**). Hooks fire in the untrusted eval workspace (the condition #141 already proved).

Verification commands used:
```
# rail presence, behavioral:
$ py <arm>/skills/constellation-commander/scripts/checklist_engine.py --file <spine> current | grep -c 'RAIL:'
   corpus-only → 0 ;  +rail → 1
# suppression provenance (corpus-only engine):
$ sed -n '/def _rail/,/check-failure/p'  →  "# MEASUREMENT ARM (corpus-only, #145): rail suppressed …
                                              human-authorized in the loop, 2026-07-12" ; return ""
```

**Corpus-hash caveat (methodological, matters for certification).** The three corpus_ids all differ, but **not only for doctrine reasons**: `install_constellation.rewrite_installed_skill_paths` bakes each install's **absolute path** into every skill file, so two byte-identical corpora installed to different temp dirs hash differently. Verified: the +rail vs +rail+hooks corpora differ **only** in the `arm-rail`↔`arm-railhooks` path substring (doctrine content identical). Consequence: the whole-tree `corpus_id` is **not** a clean cross-arm doctrine fingerprint, so D6's "rolling accumulation across same-corpus-hash runs" for N≥8 certification needs a fix (install to a canonical path, or hash with path-normalization) before hashes are comparable across runs. Flagged as a triage candidate.

## Transcript / evidence locations
- Arms: `…/scratchpad/arm-corpusonly`, `…/scratchpad/arm-rail`, `…/scratchpad/arm-railhooks` (each: `run-0..2/` + `final-verdict.json`; corpus-only & railhooks also `fenced-session-limit/run-1..4/`).
- The load-bearing failure: `…/arm-corpusonly/run-1/` — `transcript.txt`, `stderr.txt`, `workspace/` (green solution), `workspace/.agent-work/euler-problem-1/spine.json(.journal)` (the abandoned spine).
- Hooked fixture: `…/scratchpad/euler-1-hooked` (task.md byte-identical to `evals/euler-1-multiples/task.md`).

## Interpretation limits (stated up front — bound every claim above)
- **Arms are NESTED** (D1 clamps in all three): they answer the **shipping** question ("does adding this layer to what ships help?"), NOT the isolation question ("would this channel suffice alone"). A channel can be redundant-with-clamps yet effective alone; a removal decision must name which claim it rests on (spec TS4).
- **N=3 is diagnosis, not certification.** 2/3 vs 3/3 vs 3/3 is a **one-run** difference; x3 recorded 8–10pt swings from formatting alone, so this is **within noise** and does NOT statistically attribute the gap to the rail/hooks. Shrink/removal needs N≥8 rolling certification per D6; **this run decides nothing about removal.**
- **SessionStart-compact re-injection is UNMEASURED** in the +hooks arm — no scenario forces a compaction (spec TS6); the arm attributes nothing to that component. The +hooks arm's Stop/PostToolUse are exercised; compact is not.
- **Corpus hashes are install-path-polluted** (above) — not yet a clean same-corpus-hash key for certification.
- Environmental: corpus-only and +rail+hooks each fenced 4 session-limit casualties (the interactive session hit usage limits); correctly excluded — infra flake can only fence, never FAIL a corpus.

## Kill-condition EVIDENCE for the human (no recommendation)
The standing #138 kill condition: *"if the corpus-only arm alone hits target, the engine-side channels shrink to the cheapest defensible core."* Target = the #129 post-clamp 3/3.

What the diagnosis shows, stated as evidence only:
1. **corpus-only did NOT alone hit the full 3/3 target** (it hit 2/3); both channel-bearing arms hit 3/3.
2. The **single** corpus-only shortfall is **exactly the shade the engine-side channels are designed to catch** (mid-flight abandonment at execute, lease left active), and that shade appears in **neither** channel-bearing arm.
3. BUT this is a **single run at N=3**, inside documented noise, with **nested** arms — so it can neither confirm the channels are load-bearing nor that they are redundant. It is **directional signal, not a verdict.**
4. Therefore the kill condition's own trigger ("adds nothing measurable" = no completion-rate gain **and** no shade-shift, **at certification N**) is **not reached** — because certification N was not run, not because the channels proved worthless.

The honest read for the human's call: to actually invoke or reject the kill condition, run the arms to **N≥8 certification** (after fixing the corpus-hash path pollution so the rolling accumulation is valid). This N=3 pass points, weakly, **toward the channels catching a real shade** rather than toward shrinking them — but that is one run, and the decision is yours.

## Isolation-check output (first step, before any git op)
```
worktree OK: in C:/Programs/constellation-wt-145
EXIT: 0
```
No harness fix was needed; no branch/PR opened. Worktree `wt-145`, branch `issue-145`, base c9b1cf99.

## Blocker history (honest run record)
The measurement was initially blocked: this Commander runs in **auto mode**, and the box's safety classifier refused (1) the `_rail()`→`""` scratch edit as `[Auto Mode Bypass]` and (2) a direct `claude -p` probe as `[Create Unsafe Agents]`, both directing that they be run outside auto mode. Per delegate-not-replacement doctrine I **did not work around the safety gate** — I floated to the Admiral, who relayed the human's ruling: **option (a)**, run the arms interactively in the human's own session under the classifier's named remedy. That is how the arm runs above were produced. (The harness *wrapper* itself is not classifier-blocked — it spawns subjects via `subprocess.Popen`; only a hand-rolled `claude -p` and the scratch edit were. One `+rail` run I launched pre-escalation became this arm's run-0.)

## Cleanup state
- `C:/Programs/constellation-wt-145-corpusonly` — scratch worktree, engine rail-suppressed (throwaway install source; `git worktree remove` when done).
- `…/scratchpad/{arm-corpusonly,arm-rail,arm-railhooks,euler-1-hooked}` — arm results + hooked fixture (preserve until the human's kill-condition call; they are the transcripts of record).
