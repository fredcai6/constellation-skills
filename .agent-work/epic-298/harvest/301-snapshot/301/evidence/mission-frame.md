# Mission Frame — issue #301, episode record and durable store

## Intent

Ship the mechanical half of an episode memory: a durable, deterministically-findable store of
structured observation records under `.agent-work/episodes/`, with an explicit
mechanical/agent-supplied partition, a stated retirement policy that excludes from ordinary
search without deleting, and a record shape that is expressible as Stratum A assertions
without a later rewrite.

**Frame scaling, stated per the template's instruction:** this repo carries **no
`docs/architecture/` packet map** — it is the constellation-skills source, not a mapped
product repo. So there are no `capability:`/`struct:`/`decision:` map nodes to cut anchors
from. This frame is therefore **shrunk and re-based on the repo's actual structural record**:
the shipped scripts, their tests, and the design docs under `docs/`. It is not skipped — the
change adds a new artifact family and a new script pair, which is not trivial — but every
anchor below is a real file, not a map node.

## Affected capabilities (as real code, no map nodes exist)

- **New: episode capture and retrieval.** No prior art at HEAD — `grep -ril "episode"` over
  `*.py`/`*.md`/`*.json` returns zero hits. This run creates the capability.
- **Adjacent, read-only: the lessons inbox** (`scripts/apply_lessons_delta.py` +
  `.agent-work/LESSONS.md`). Governs by analogy — this run copies its validated-delta write
  seam — and is **fenced from modification** by `decision:lessons-inbox-keeps-running`.
- **Adjacent, reused: durable-root resolution** (`scripts/agent_work_root.py`,
  `durable_root()`). This run depends on it so episodes written inside a worktree land in the
  main checkout rather than in N worktree-local silos.

## Structural anchors

- `scripts/apply_lessons_delta.py` — the seam being copied, never modified. 699 lines.
- `scripts/agent_work_root.py` → `durable_root()` — the cross-worktree durability mechanism.
- `tests/test_apply_lessons_delta.py` — the test shape the new tests should rhyme with.
- New: `scripts/apply_episode_delta.py`, `scripts/query_episodes.py`,
  `tests/test_episode_store.py`, `docs/EPISODE_STORE.md`, `.agent-work/episodes/`.

## Governing constraints

All inherited from the launch order's pre-rulings; none discovered here.

- **Markdown in git.** No DB, no query language. "Queryable" = findable by deterministic
  means over Markdown in git.
- **The stochastic boundary (B0.1).** The store is mechanical and never guesses. Rhyme
  detection is a downstream LLM sensor job (#308). No ranking, no similarity, no embedding.
- **Non-foreclosure is testable, not hoped.** A design that satisfies Stratum A expressibility
  only by rewriting the record later has not satisfied it.
- **Retired means excluded from ordinary search, retained in history.** Never deletion.
- **`.agent-work/LESSONS.md` and `apply_lessons_delta.py` are untouchable this run.**

## Decision anchors and decision pressure

- decision:episode-store-shape — the record shape and retirement mechanism, chosen by
  design-it-twice across four constraint-named candidates.
  `@grade: settled/human · leans plan,implement · settle: Admiral/Tommy converge the float in COMPARISON.md`
- decision:partition-enforced-at-the-writer — the mechanical/agent-supplied split is enforced
  by the single write path rejecting a misfiled field, not merely documented.
  `@grade: settled/inherited · leans g2 · settle: adversarial fixture that misfiles a field must be rejected`
- decision:agent-bin-gets-assertion-addressability-mechanical-bin-does-not — agent-supplied
  claims are individually addressable assertions with their own standing; mechanical facts
  stay flat key-value lines.
  `@grade: guess · leans g1,g2 · settle: at #308, whether a consolidation ever needs to dispute a mechanical fact`
- **Decision pressure (unsettled, floated):** the retirement mechanism — file move between
  `active/` and `retired/` versus a status field filtered negatively. Floated to the Admiral;
  my lean flipped to the file move after a cold critic. Not mine to settle.

## Claims and evidence surfaces

- claim:seeded-episode-survives-a-session-boundary — verified by a test that writes in one
  process and reads in a genuinely separate one, sharing only the working tree.
- claim:seeded-episode-survives-a-WORKTREE-boundary — **added after the cold critic**, which
  found that no candidate tested this. Verified by writing from a simulated worktree path and
  reading from the durable root.
- claim:retired-episodes-leave-ordinary-search-and-stay-in-history — verified both directions:
  absent from the ordinary enumeration, present in the history-inclusive one.
- claim:the-partition-cannot-be-misfiled — verified by an adversarial fixture that puts a
  mechanical field under agent-supplied and asserts the writer rejects the whole delta.
- claim:an-agent-supplied-claim-can-be-disputed-individually — verified by disputing one field
  while another stays active, with no rewrite of the record.

## Map confidence / staleness / disputes

- **No architecture map exists.** Stated above; this alters the plan by re-basing anchors on
  real files, and it means no gate may cite map authority for a structural claim.
- **Live external dependency: issue #300's projection manifest**, running concurrently in
  another worktree. My `context` field consumes it. I hold its shape as an *obligation*
  (enumerable `(loaded-artifact-id, canonical-revision)` pairs), not an assumption about its
  implementation, and I re-check against #300's merged shape before closing. This is the one
  genuinely unverified dependency in the run, and it is deliberately held at arm's length
  rather than silently trusted.

## Out of scope

Automated capture wiring (#305). Consolidation and the rhyme-search loop (#308). The
projection manifest itself (#300). Any migration, disabling, or rewrite of the live
`LESSONS.md` machinery — cutover is ruled at #308.
