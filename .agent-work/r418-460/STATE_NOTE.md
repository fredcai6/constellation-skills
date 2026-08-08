# Crash-resume state note — r418-460

- **step:** execute · gate `g2-implement` of `.agent-work/r418-460/execute.json`.
  **g1 is CLOSED. g2's work is DONE, COMMITTED and VERIFIED** — only the `advance g2-implement`
  call is outstanding, refused by the context governor. A `refresh-request` is filed on that gate
  (`e-g2-implement-3`, `why_ref` `w-4`), so the next agent's `advance` is unblocked.
- **slug:** r418-460 · branch `epic-418/b-460-episodes-observations` · worktree `C:/Programs/constellation-skills-wt/r418-460`
- **next command:**
  ```
  cd C:/Programs/constellation-skills-wt/r418-460
  python scripts/checklist_engine.py --file .agent-work/r418-460/execute.json current
  python scripts/checklist_engine.py --file .agent-work/r418-460/execute.json advance g2-implement --why "<understanding>"
  ```
  then register and dispatch the g2 reviewer with the handoff **already written** at
  `.agent-work/r418-460/crew-handoffs/g2-review-handoff.md`.
- **pid:** none — foreground. Crews are dispatched with `run_crew.py --backend external` and
  confirmed with `--verify-result <session-name>`.
- **expected artifact:** `.agent-work/r418-460/crew-handoffs/g2-review-result.md`, then `execute.json`
  driven to a terminal `g4-integrate`, then the spine to `archive`.

## State the successor does not have to re-derive

- **g2 result:** 48 examined / 32 in scope / **27 restated** / 5 UNGROUNDED by design / 16
  `issue-447-*` checked and correctly untouched. Committed at `7df136e6`.
- **Suite at HEAD:** `1745 passed, 4 skipped, 677 subtests`, **EXIT=0** — identical to the post-g1
  baseline, so the restatements regressed nothing. Log:
  `.agent-work/r418-460/evidence/g2-integrate-pytest.txt`.
- **g2-implement `p1` and `c1` are both attested**; evidence `e-g2-implement-1` (implementer result)
  and `e-g2-implement-2` (test run) are attached.
- **g3 needs** the pre-g2 sha `c9d9dd7c` to measure the detector against the corpus as it read
  before the rewrite, and seeds its exception list from the 5 UNGROUNDED ids.
- **g4 needs** to handle `docs/EPISODE_STORE.md`'s own canonical worked record, which carries a
  prescriptive assertion at `governor-268-003.d2` — the document defining the format models the
  shape this issue removes.

## Warning: two commanders were live on this worktree

Commits `770f3e06` (an empty no-op) and `00986ad5` / `1dfd06ae` (`notes-460.md`) landed from
another agent while this commander was working. **Nothing is damaged** — `episodes/` at HEAD is
byte-identical to `7df136e6` — and that agent's notes are accurate, but the collision is the
Admiral's to resolve before another dispatch.

_Updated: 2026-08-08T01:05:00+00:00_
