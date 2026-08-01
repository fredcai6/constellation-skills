# Crash-resume state note — 301

A fresh Commander resumes from exactly these five lines. No forensics needed.

- **step:** spine `archive`, **in-progress and DELIBERATELY HELD**. Every other step is complete: init → context → understand → plan → execute (all 13 `execute.json` tasks, four gates) → reconcile → triage → review → feedback. **PR #320 is MERGED.** Archive is held because completing it would (a) move `.agent-work/301/` — which contains the design-it-twice comparison and all four candidates the Admiral harvests — and (b) release the session lease, and the Admiral instructed explicitly: *do not sweep the worktree and do not release the lease until I have harvested; I will tell you when.*
- **slug:** work-id `301`, branch `epic-298/301`, worktree `C:/Programs/constellation-skills-wt/298-301`. PR **#320 MERGED** (squash commit `195e893b8`); branch head `6f0ccb5`, tree clean.
- **next command:** `py scripts/checklist_engine.py --file .agent-work/301/spine.json current` — then, **only once the Admiral confirms the harvest is done**: move `.agent-work/301/` to `.agent-work/archive/<date>-301/`, run `py scripts/verify_agent_feedback.py 301 --phase archive`, attest c1/c2, `advance archive`, and **release the lease as the very last action** (`release --session-id commander-301-s1`). Release must come *after* the closing advance or the terminal provenance check fails.
- **pid:** none — foreground
- **expected artifact:** all delivered. `.agent-work/verdict-301.md`; shipped and merged: `docs/EPISODE_STORE.md`, `episodes/` (`active/`+`retired/` with `.gitkeep`), `scripts/apply_episode_delta.py`, `scripts/query_episodes.py`, `tests/test_episode_store.py`.

## Do not lose these — they are gitignored and exist only here

- `.agent-work/verdict-301.md` — at the `.agent-work` root; **survives** the archive move.
- `.agent-work/staged-feedback/301/` — the trio, 12 delta ops, passes `--phase feedback` at exit 0; a **sibling** path, so it **survives** the archive move. `FENCE.md` carries my cap-drop ordering.
- `.agent-work/301/design-it-twice/` — COMPARISON.md and all four candidates. **These are INSIDE the work area and WOULD relocate** to `.agent-work/archive/<date>-301/design-it-twice/` when archive completes. This is the one thing archive disturbs.

## Two things the harvester must know

1. **The delta cannot be applied as authored.** The playbook is at **16 active against a cap of 20**, so only **4 of the 10 adds** can land — confirmed by dry-run, not assumed. My ordering, with reasons, is in `staged-feedback/301/FENCE.md`. Keep `a-panel-inherits-what-it-was-not-told-to-vary` first regardless of taste: #300's op lands as a **confirm against that id**, and dropping it forks the identity the Admiral ruled to preserve.
2. **Delta ops use `task_class` / `bank_reason` (underscores)**; the *rendered* playbook field uses hyphens. I authored the hyphen form throughout and the dry-run caught it. If you re-author ops, use underscores.

## Filed this run

**#313** (`py -m pytest` false-reds; comment adds the version numbers), **#314** (delegated Commanders cannot use the prescribed SendMessage dispatch), **#319** (working-tree bytes differ across worktrees under `core.autocrlf` — for #308; comment corrects my own proposed remedy after reading `.gitattributes`), **#321** (the store validates ids it *lists* but not ids it is *handed* — a g4 cold-panel finding, filed as a merge condition before merging), **#322** (the overview's truth-layer taxonomy omits the store — routed to #308, which owns the wording).

## Lease

`commander-301-s1` is **held on purpose**. Do **not** release it to tidy up — the release is the
final journal entry and must come after archive's closing advance. Takeover if stale:

`py scripts/checklist_engine.py --file .agent-work/301/spine.json claim --session-id <new> --claimed-by <you> --worktree . --force --reason "resuming this run"`

_Updated: 2026-08-01T16:40:00Z_
