# Crash-resume state note — 300

- **step:** execute · gate `g1-implement` — **UNBLOCKED 2026-08-01.** Tommy ruled: manifest lives under `.agent-work/`, **no** committed per-role artifact. `g2` dropped via the engine `amend` verb (amendment 2). Spine init/context/understand/plan complete.
- **slug:** work-id 300 · branch `epic-298/300` · worktree `C:/Programs/constellation-skills-wt/298-300` · base `b69e6c8`
- **next command:** `cd C:/Programs/constellation-skills-wt/298-300 && py scripts/checklist_engine.py --file .agent-work/300/execute.json current` — drive the 8 remaining gates (`e0-context`, g1 triple, g3 triple, `g4-cold-panel`). Dispatch implementer/reviewer via `py scripts/run_crew.py`; run `py scripts/recover_crews.py 300` before **each** dispatch and only launch when it reports no unresolved crew. Crew plan files go in their **own** subdirectory (`.agent-work/300/g1-implement/`), never the work-id root — a plan file there shares this spine's `gauge.json`.
- **pid:** none — foreground
- **expected artifact:** `.agent-work/300/IMPLEMENTER_RESULT-g1.md`, then `REVIEW_RESULT-g1.md`; finally `.agent-work/verdict-300.md` updated at closeout

**Read before resuming, in this order:** `.agent-work/300/PROBLEM_STATEMENT.md`,
`.agent-work/300/MISSION_FRAME.md`, `.agent-work/300/DIT-COMPARISON.md` (incl. its ADDENDUM and
Errata), `.agent-work/300/PLAN_CRITIC_DISPOSITION.md`.

**The ruling, and what survives it.** No committed `CONTEXT_PROJECTION.json`; one envelope, not two;
`rev` always resolves from the **bytes actually delivered**, never the git object DB. Everything else
stands: the minimal `{root, path, rev}` row, the blob-OID identity computed in-process, the optional
ordered `context_refs` declaration on the spine task, no globs, prose retained with the lint pinning
declaration against prose, metadata-only, the injectable resolver as the single impure edge, and the
`.gitattributes` guard (`g1-implement.c7`). Full cold-panel review class **still applies** — it does
not downgrade because the diff shrank.

**Three shell facts that will bite otherwise.** Use `python -m pytest`, never `py -m pytest` (the
`py` shim's runtime has no pytest here). Every command postcondition assumes cwd = the worktree root;
the engine does not pass `cwd=`. **CI pins Python 3.12** while this host is 3.14.3 — do not use
`Path.read_text(newline=)`/`write_text(newline=)`, which are 3.13+; a sibling issue shipped a red CI
on exactly that.

**Do not sweep this worktree or release the lease.** Every artifact lives in gitignored
`.agent-work/`; the Admiral harvests first and will say when.

_Updated: 2026-08-01T14:40:00Z_
