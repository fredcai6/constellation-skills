# Mission Frame — issue #307, POST arm

**Frame authored under a DEGRADED map input.** `constellation-skills` carries no
`docs/architecture/` at all, so every anchor below is cut from the three substitutes the
context step hash-pinned into `.agent-work/issue-307/map-orientation.json`, not from a map
inventory. That is a declared reading, not a licence — recorded before any source file opened.

## Intent

Run the POST arm of the epic-298 map-first measurement and compile a **paired evidence
package** in which POST differs from PRE-B in exactly one variable — the installed corpus —
and hand the three-way verdict (sufficient / insufficient / irrelevant) to Tommy unadjudicated.

## Affected Capabilities

- **measurement capture** — drive five `claude -p` subjects on pinned f1Brainz worktrees at
  `3541d292`; unchanged from PRE-B except the corpus they load.
- **treatment verification** — prove per run, from the transcript, that the Commander loaded.
  This is the arm's spine, not a hygiene step: it is the only thing separating *insufficient*
  from *irrelevant*.
- **ordering scoring** — the boolean `map_before_src` and the four discriminated measures.
- **corpus identity** — fingerprint before and after so the arm proves which corpus it measured.

## Examples / Events

- **#331** — an ordinary brief declines the corpus entirely; the arm nulls by construction.
  Answered by explicitly invoking the Commander.
- **#344** — the contract was merged but absent from the *installed* corpus; an arm run then
  would have blamed the contract for a delivery failure. Answered by fingerprinting and by
  `git merge-base --is-ancestor 5d2585b <corpus source_commit>`.
- **`DEGRADED-NO-MAP` reproduced in this repo at the context step** — independent second
  confirmation, after `commander-308`, that the #304 contract is reachable and firing.

## Structural Anchors

- `.agent-work/epic-298/preb/PREB_RECORD.md` — the pairing arm's record; fixes the measures,
  the comparability rules, and the PRE-B numbers POST must be read against.
- `.agent-work/LESSONS.md` — the Active section; `verify-launch-order-claims-against-code`
  governs this run's baseline check.
- `docs/agents/ORCHESTRATOR_CONTEXT.md` — project deltas; evidence standards and repo action
  authority (pushes need approval, which is why this run declares FINAL and hands the merge up).

Instruments held at their PRE-B revisions, **verified blob-to-blob at `6774181` vs `HEAD`**
rather than asserted: `baselines/extract_ordering.py` (frozen), `baselines/capture_baseline.py`,
`baselines/issues.frozen.json` (the frozen brief source), `baselines/RUBRIC.md`,
`baselines/verify_capture.py`, `preb/verify_treatment.py`, `preb/discriminate.py`,
`preb/fingerprint_global_corpus.py` — **all nine byte-identical**. The single exception is
`preb/capture_preb.py`, which gained the declared label-only `--arm` flag (+16/−6); digests for
both revisions are recorded in `post/instrument-digests.json` and asserted by the `g2` gate.
(The working tree shows CRLF against the blobs' LF, so a working-tree digest comparison
reports every file changed — the comparison must be blob-to-blob, and is.)

## Governing Constraints / Assumptions

- **constraint: one variable.** Brief bytes, argv, model, pin, task set, env scrub and every
  scorer are identical to PRE-B. A rebuilt scorer would give a POST/PRE-B difference two
  candidate causes and the arm could not separate them.
- **constraint: boolean only across arms.** Run lengths are 10–61 (PRE-A) and 96–148 (PRE-B).
  Raw indices are not comparable; only `map_before_src` transfers.
- **constraint: install only, never `--wire-hooks`.** `settings.json` is Tommy's.
- **constraint: the frozen extractor is not modified.** Its corpus rule is a declared,
  measured limitation, not a bug to patch mid-arm.
- **assumption (verified, not assumed): the installed corpus contains #304.**
  `git merge-base --is-ancestor 5d2585b 3595955` returns true, as does `9a0cb17`.
- **assumption (verified): f1Brainz HAS a map** — `docs/architecture/{index.md,packets,overlays,
  decisions}` present at the pin, so subjects hit the RESOLVED path, not the degraded one.

## Decision Anchors & Decision Pressure

**Anchors are written WITHOUT the `type:id` spelling deliberately.** Under a DEGRADED
orientation `verify-frame` refuses every typed anchor unconditionally, while this template
mandates graded decision anchors — the two contracts contradict each other on the degraded
path. Filed rather than absorbed; the substance is kept, only the spelling yields.

- **post-pairs-with-preb-not-prea** — three arms, two series; PRE-A stands alone.
  `@grade: settled/measured · leans capture · settle: already settled by .agent-work/epic-298/preb/PREB_RECORD.md §"three arms, two series"`
- **post-runs-on-constellation-commander** — matches PRE-B; re-capture of PRE-B on the
  delegated variant was declined.
  `@grade: settled/ruled · leans capture · settle: Admiral ruling, carried in LAUNCH_ORDER-307 "Method requirements"`
- **enumerate-and-bound-writes** — the "zero write calls" standard is unachievable for any
  skill-loaded arm (#347); the boundary assertion replaces it and is strictly stronger.
  `@grade: settled/ruled · leans safety · settle: already ruled for PRE-B, governs POST too`
- **decision pressure — the single additive instrument change.** `capture_preb.py` gains an
  `--arm` label flag defaulting to `"PRE-B"`, and `run_all_post.py` is derived from
  `run_all_preb.py` differing only in worktree path and output dir. Surfaced to the Admiral in
  writing BEFORE the arm ran, per the launch order.
- **decision pressure — the `map_orient`-invisible-to-the-extractor hazard.** Resolved by an
  additive supplementary audit applied to BOTH arms with the same code, never by touching the
  frozen extractor. Surfaced here rather than absorbed.
- **decision pressure — the rubric §2 tolerance ambiguity (#333)**, confirmed by two
  independent graders. Not this run's to rule; it must govern both arms identically.

## Claims / Evidence Surfaces

- **treatment-landed** — every run shows a `Skill` call to a Commander variant **and** a
  matching `Base directory for this skill:` line. Checked by `verify_treatment.py`; a run
  failing it is a **FAILED CAPTURE**, reported, never silently dropped.
- **corpus-identity** — BEFORE and AFTER fingerprints recorded and compared; any drift
  across the window makes the runs non-poolable and must be said so.
- **orientation-order** — `map_before_src` per run from the frozen extractor, unmodified.
- **nothing-landed-in-f1brainz** — every write enumerated with its resolved target and
  asserted inside that run's own disposable pinned worktree under `.agent-work/`.
- **contract-actually-fired** — `map_orient` invocation audit, the second witness that
  separates *insufficient* from *irrelevant*.

## Map Confidence / Staleness / Disputes

- **`docs/architecture/` in `constellation-skills`: ABSENT.** Confidence zero — there is no map
  to be stale. The plan compensates by anchoring on the three hash-pinned substitutes and by
  asserting against **behaviour** (running `map_orient`, `git merge-base`, fingerprints) rather
  than against text describing behaviour.
- **`baselines/CORPUS_FINGERPRINT_{PRE,POST}_INSTALL.json`: named in the launch order, absent
  from the tree.** Does not block; the arm takes its own fingerprints, which it needs anyway.
- **`preb/PREB_RECORD.md` §12 lists four items open for the Admiral and Tommy.** Two are
  settled by this launch order (variant choice, write standard); #333 and #352 remain open and
  are not this run's to close.

## Out of Scope

- The degraded path as a subject of study — a different question, explicitly not to be mixed.
- Re-capturing PRE-B. Ruling on #333. Reverting #352's memory edit.
- Adjudicating the B3 verdict. **HITL: Tommy adjudicates.**
- Merging, and `--wire-hooks`.
