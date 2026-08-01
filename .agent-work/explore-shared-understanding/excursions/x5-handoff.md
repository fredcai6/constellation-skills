# Excursion X5 — Design-it-twice: the shared-understanding mechanism

**The ONE thing being designed twice (four ways):** the *architecture* of the shared-understanding mechanism — **where the "what Fred knows" intelligence lives and how the pieces connect**: the shared concept **ledger** (entries, home, how familiarity updates), the **calibration + interleaving** core (hold a per-reader familiarity model AND blend one paragraph of explanation into a normal working message without condescending or cluttering), and the **two policies** that read the ledger — **teach** (real-world concepts, push familiarity up) and **neuter** (internal jargon, hold the dialect down; "no coined term until unlocked" = the same familiarity gate on internal terms).

**Panel of 4 — because it touches architecture** ("when in doubt, panel").

## Held FIXED for every candidate (do not redesign these — the human confirmed them)
- **Spine:** two opposite policies (teach real-world / neuter internal) over ONE shared per-concept ledger. Each concept entry carries a **real-world-vs-internal tag** + a **familiarity level**.
- **Register rule (expertise-reversal):** peer/minimal by default; add depth ONLY on a detected miss; ALWAYS surface the genuinely-new delta (expert blind spot); expertise is concept-local.
- **Familiarity is OBSERVED, not quizzed:** updated by the contingency/fading rule read off the human's OWN writing (fluent use → dial down; stumble/ask → dial up). Not a numeric score the agent guesses; not a chore the human maintains.
- **Per-project, NOT shared across projects** (projects drift apart; the human is fine being re-asked a term on each). 
- **Tutor is summoned on a miss / the human's pushback** ("no, that doesn't make sense" / "let's go back"), not always-on.
- **Anti-goals (kill-adjacent):** no heavy machinery for its own sake (scores/dashboards); no banning precise jargon; no condescension.
- **Prior art to reuse:** Pocock learning-records-as-ADRs (append-only insight records); ITS student-model-as-overlay-on-domain-model; two-tier short-then-deep; docent-style freshness stamp on any persisted explainer; Diátaxis "explanation" shape for the milestone explainer.

Read these before designing: `.agent-work/explore-shared-understanding/IDEAS_BOARD.md` and the excursion results `excursions/x1..x4-*.md`.

## The four constraints (one per agent — each designs the SAME mechanism under exactly ONE)
- **A · minimal-machinery** — the lightest thing that works. Extend existing artifacts; a plain-text ledger + a register discipline; tutor as a thin on-demand skill; NO scoring engine, NO new services. Optimize for "could ship next week, near-zero new infrastructure."
- **B · map-native overlay** — the ledger is an **overlay on the Cartographer architecture map**; familiarity annotates map nodes; teach/neuter are driven by map traversal. Optimize for locality to existing map truth.
- **C · tutor-as-service (ports-and-adapters)** — a **first-class tutor agent owns** the reader model + calibration + the jargon gate; every other agent calls it through one clean seam (e.g. `may_use(term)?`, `teach_delta(concept)`, `note_usage(text)`). Optimize for a clean, single-owner seam.
- **D · distributed-duty (no central authority)** — NO central tutor; calibration + interleaving is a **cross-cutting rule every agent applies inline** against the shared ledger; the tutor exists only as the deep-dive-on-pushback escalation. Optimize for in-flow naturalness.

## Compared on (score every candidate on all four, like-for-like)
- **Depth** — does it hide the right complexity behind the seam, or leak it up into every agent?
- **Locality** — is the change contained, or does it fan out across every skill/agent?
- **Seam placement** — is the boundary where callers and tests actually want it?
- **Testability** — can each pathway (familiarity update, teach trigger, jargon gate, interleaving) be exercised and falsified on its own?
- **Plus fit to the fixed anti-goals** — heavy-machinery risk; condescension risk; does it serve BOTH halves equally?

## Output (each agent writes ONE candidate doc)
A concrete design under your ONE constraint: the ledger entry shape + home; how familiarity updates from writing; how the teach policy and the neuter policy each read it; how calibration + interleaving actually works in a message; the tutor's trigger/seam; and an honest self-assessment on the five axes incl. where your constraint HURTS. Deep-module terms. State what you did NOT resolve.

**Result artifacts:** `excursions/x5-design-a.md` (A), `-b.md` (B), `-c.md` (C), `-d.md` (D).
**Budget:** ~20 min each; design only, build nothing. Scoped nulls on anything you leave open.
