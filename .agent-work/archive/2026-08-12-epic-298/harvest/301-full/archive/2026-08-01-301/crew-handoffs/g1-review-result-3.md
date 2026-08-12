# Review Result — RE-REVIEW (round 3)

Status values follow `skills/workbench/references/status-model.md`.

## Assigned Gate
`g1` — episode record grammar and store doctrine (issue #301, epic-298) — **THIRD REVIEW**, of a
rework (rework 2 of a 3-rework cap) that followed a second `BLOCK`
(`.agent-work/301/crew-handoffs/g1-review-result-2.md`).

## Result
`APPROVE`

VERDICT: APPROVE

Driven survey: `.agent-work/301/g1-review-3/review.json` (session `reviewer-g1-301-review3`,
claimed/consolidated/released), Fowler pass record:
`.agent-work/301/g1-review-3/fowler-pass.json` (`verify_fowler_pass.py` exit 0). Ten checks
visited (the six template checks plus four appended for this round's specific hunt: class-closure
trace, seam coherence, over-correction, no-regression). This is an independent re-review — I did
not assume the prior BLOCKs' analyses or the implementer's rework accounts were correct, and
re-derived every claim against the current text of `docs/EPISODE_STORE.md` and
`episodes/README.md`.

## Handoff compliance

**The decisive question — do binding Option A require rewriting any g3 primitive? NO,
for the four named primitives.** I traced each of the four retrieval primitives the hunt named
literally against the current text:

- **Fetch by id** = `resolve_episode_path(id)` (§7) then a direct read — no scan, no membership
  check.
- **Enumerate non-retired episodes** = `iter_episode_ids(include_retired=False)` (§7) then
  `is_episode_in_ordinary_search()` (§7) per returned id, exactly per §7's explicit "Composition
  rule" paragraph ("scan, then filter, always both steps, never one folded into the other").
- **Select by exact field value restricted to the ordinary set** and **enumerate neighbours** =
  the same `iter_episode_ids(include_retired=False)` candidate set, plus their own predicate.

Binding Option A later means writing 4 adapter bodies ("on the order of a handful of lines each,"
§7's own words) at 4 already-named seams (`apply_retirement`, `is_episode_in_ordinary_search`,
`iter_episode_ids`, `resolve_episode_path`); **no primitive's shape or description in §6/§7/§8
changes**. This closes round 2's blocker (the enumeration half was unspecified) and the
implementer's own self-found gap (fetch-by-id's path resolution was unspecified) — both verified
fixed by direct comparison against the current text, not by trusting the rework account.

**A fifth, genuine instance of the same class remains, one gate downstream (see Finding 1).**
Going beyond the four named primitives, per the handoff's instruction to check *every* concrete
mechanism: §5's worked amend-assertion write path and §10's g2-obligations bullet name **no
seam** for locating the target episode file before an amend write — unlike retire
(`apply_retirement`) and fetch (`resolve_episode_path`), both of which now do. This is real, not
polish, but it is g2's problem (the next gate), fails loudly rather than silently, and is cheap to
fix. See Finding 1 for the full trace and why it does not block this gate.

## Scope drift
None. `git status --short --untracked-files=all` shows exactly `A episodes/README.md`,
`?? docs/EPISODE_STORE.md` — the same two files as every prior round, reproduced independently.
`LESSONS.md`/`apply_lessons_delta.py` untouched. #300's manifest not designed. No capture/
consolidation code. The retirement layout itself is never chosen anywhere in the current text —
both options remain live in every one of the five seam rows in §7's table.

## Evidence verdict
All claimed side-effects independently reproduced, not taken from either report:
- `git status --short --untracked-files=all` → exactly the two allowed files.
- `git check-ignore episodes/` → exit **1** (not ignored).
- `python -m pytest tests/ -q` → **1157 passed, 2 skipped, 260 subtests passed in 31.25s** —
  exact match to the baseline and to both prior rounds.
- `grep -n -i amend docs/EPISODE_STORE.md` and `grep -n "resolve_episode_path\|apply_retirement"
  docs/EPISODE_STORE.md` — reproduced independently, confirming zero co-occurrence (the basis for
  Finding 1).

## Code/doc quality
Fowler pass (r6-fowler): 12/12 baseline smells visited, rail exits 0 (record:
`.agent-work/301/g1-review-3/fowler-pass.json`). 9 absent, 1 overridden (`primitive-obsession`,
subordinate to `decision:markdown-in-git`, same reasoning as the prior review), 2 flagged:
- `large-class` — §7 has grown to ~190 of the document's 653 lines across nine sub-topics.
  Non-blocking: the closing "full seam set" table gives a one-screen executive summary that keeps
  the section navigable despite its length. Recommend a subsection split when §4 is next touched
  (naturally, at g4).
- `shotgun-surgery` — the amend-write gap (Finding 1) is a sixth, un-enumerated touch point the
  seam sweep did not reach; resolves automatically once Finding 1 is closed.

## Map impact verdict
- **Evidence supports claimed change:** yes, verified independently.
- **Constraints not violated:** yes — markdown-in-git, mechanical-only, retired-is-excluded-not-
  deleted all honored.
- **Notes match the diff:** yes — the implementer's account of what changed (§7's two new seams,
  §3/§9 local pointers, the consolidation table) matches what the diff actually shows.
- **Decision candidates surfaced:** `decision:episode-store-shape` correctly still **not
  resolved**; every new seam is correctly framed as scaffolding for g2/g3/g4, not a resolution of
  the layout question.
- **Durable context routed:** yes — Finding 1 is explicitly routed to g2 below.

## Reconciliation check
No `docs/architecture/` packet exists in this worktree (confirmed directly). No architecture
divergence beyond Finding 1, which is a g2-scope gap, not a baseline reconciliation issue (no code
exists yet).

## Findings, most serious first

### 1. [High, non-blocking — routed to g2] g2's amend-assertion write path has no named
path-resolution seam, unlike retire and fetch

**File:** `docs/EPISODE_STORE.md`, §5 (worked dispute walk-through), §10 (g2's obligations).

§5's worked example describes g2's second write operation, `amend-assertion` ("The write path is
one `amend-assertion` op (g2's writer, out of scope here) that changes exactly `a4`"). §10's g2
obligations bullet names only that the writer's **retire** op routes through `apply_retirement()`
— it says nothing about how `amend-assertion` (or any other in-place edit of an existing episode)
locates the file it is about to modify. `grep -n -i amend docs/EPISODE_STORE.md` and
`grep -n "resolve_episode_path\|apply_retirement" docs/EPISODE_STORE.md` (both reproduced) confirm
zero co-occurrence anywhere in the document.

This matters because, unlike retire, amend does **not** have a "plausibly safe by construction"
argument available. Retire always transitions *from* a known state (an episode being retired is,
by definition, currently active), so under Option A its source path is knowable without a check —
this is exactly why round 2's reviewer rated the analogous write-side gap "Moderate, non-blocking"
rather than a blocker. Amend has no such guarantee: §6 explicitly states an episode can be
`retired` while every one of its assertions stays `lifecycle-standing: active`, and nothing in the
document forecloses disputing or auditing an already-retired episode's content later (that is, in
fact, exactly the kind of thing a downstream consolidation/audit pass at #308 would plausibly do).
So under Option A, an `amend-assertion` op genuinely cannot know in advance whether its target is
under `episodes/active/` or `episodes/retired/` — it needs the identical two-directory resolution
`resolve_episode_path()` already performs for reads, and no seam currently routes it there.

**Concretely, what breaks:** if g2 is built literally to the current text — following the flat
`episodes/<id>.md` pattern shown in every worked example, with no seam invoked for amend — and
Option A later binds, amending an already-retired episode's assertion fails to find the file at
the naive path. Fixing that is a real code change to g2's amend logic (adding a resolution step),
not an adapter swap, because no seam was ever invoked to begin with — the same "additive in
letter, a rewrite in effect" failure shape the last two rounds were both about, one gate over.

**Why this does not block gate g1:** (1) it is g2's write-path concern, not one of the four g3
retrieval primitives this round's hunt targeted, and those four are genuinely closed; (2) the
failure mode is a loud, self-diagnosing lookup miss (file not found), not round 1/2's silent-
wrong-answer shape (`ordinary search silently returns nothing`), which the repo's own inherited
doctrine treats as meaningfully less dangerous ("fail visibly rather than emit plausible wrong
output" — `global-everyone.md`); (3) the fix is one sentence, exactly symmetric to what rework 2
already did for retire and fetch-by-id; (4) g2 has its own review gate immediately next, which
would very plausibly catch this while implementing, given the document's own established
seam-naming discipline makes the omission conspicuous once a builder is actually writing the
amend path.

**Fix:** one sentence in §5 or §10 stating that g2's writer routes **every** write to an existing
episode — not only retire — through `resolve_episode_path()` to locate the current file before
amending it, mirroring what fetch-by-id already does. Cheap, narrow, does not reopen the layout
decision. Recommend doing it now, before g2 starts, since it costs nothing and closes the class
completely rather than leaving one open thread.

### 2. [Minor, cosmetic] §8's select/neighbour-enumeration bullet is slightly ambiguous about
whether it includes the per-id membership filter

**File:** `docs/EPISODE_STORE.md`, §8.

"Select by exact field value restricted to the ordinary-search set... both scan the same
`iter_episode_ids(include_retired=False)` candidate set before applying their own field/key
match — identical composition to enumeration, just with an extra predicate layered on top." Read
in isolation, the explicit clause ("scan... before applying... match") names two steps, while
"identical composition to enumeration" (defined two bullets earlier as scan-then-filter) implies
three. This matters concretely under Option B specifically: Option B's `iter_episode_ids` does
**not** filter by `include_retired` on its own ("the retired/active split is left entirely to the
per-id membership seam," §7) — so a select/neighbour implementation that dropped the
`is_episode_in_ordinary_search()` step would silently include retired episodes' matches under
Option B, while appearing to work fine under Option A (whose base scan already excludes
`retired/`). A careful reader resolves this correctly via the "identical composition to
enumeration" cross-reference and the primitive's own name ("restricted to the ordinary-search
set"), so I rate this cosmetic rather than blocking — but it is the same shape of ambiguity as
Finding 1, one level more subtle, and a one-clause tightening ("...and confirming each via
`is_episode_in_ordinary_search()`, exactly as enumeration does") would remove the ambiguity for
free in the same editing pass as Finding 1.

### 3. [Observation — carries to g4] §7 has grown large (Fowler `large-class`)
Same root cause as the density noted in the code/doc quality section above — not a defect, an
organizational observation. Non-blocking; a natural fit for the pass g4 makes when it updates §7
to record the bound retirement layout.

## What I verified as fine (independently, not taken on either report's word)
- `git check-ignore episodes/` exits 1 — reproduced myself.
- `python -m pytest tests/ -q` — reproduced myself, 1157 passed / 2 skipped / 260 subtests, exact
  match to baseline and to both prior rounds.
- `git status --short --untracked-files=all` — confirmed only the two allowed files touched.
- All three round-2 findings (base-enumeration seam, write-side retire seam, §9 local pointer)
  and the implementer's two self-found sweep fixes (§3 header, §8 fetch-by-id path resolution) —
  read in full against the current text and confirmed genuinely fixed, not merely reworded.
- The four named seams (`apply_retirement`, `is_episode_in_ordinary_search`, `iter_episode_ids`,
  `resolve_episode_path`) plus the store-root seam checked pairwise for overlap/gap/contradiction
  — none found; the seam table matches the prose row-for-row; the one place a document reader
  might confuse two seams (`is_episode_in_ordinary_search` vs `resolve_episode_path`) is
  explicitly pre-empted by the text itself ("a distinct concern from this seam, not a substitute
  for it").
- No regression: C2 (§4's literal `## ` headings + field allowlist), C4 (§6's Stratum A table
  against worked `a3`, lifecycle-standing as a separate dimension), C5 (§5's single-field dispute
  walk-through, siblings untouched, mechanical bin has no strength/standing), C6 (§1's one named
  seam, explicit non-use of `durable_root()`), C7 (§8's no-ranking/no-similarity/no-embedding
  statement, #300 obligation framed as an obligation), C8 (§2's panel-unanimity retraction), C9
  (§9's git-mechanics argument, epic-lease-exception and read-only-fence treatment) — all re-read
  in full this round against the current text (not against prior summaries) and confirmed intact.
- `episodes/README.md` re-confirmed clean: basename-only notation throughout, no bare full-path
  instance.
- No `docs/architecture/` packet exists in this worktree — confirmed directly.
- Fowler pass rail (`verify_fowler_pass.py`) exits 0 against a full 12-smell record for this
  round's text.
- All four named seams are load-bearing (each traces to a concretely identified gap from a
  specific round), not speculative generality invented ahead of need.

## What I could not check, and why
- Whether a g2 implementer would in fact hit the amend-write gap (Finding 1) versus correctly
  inferring the same resolution step by analogy to fetch-by-id and retire — this is a prediction
  about future work, not directly testable at this gate. My confidence rests on the text being
  silent on its face (confirmed by grep, no seam co-occurs with "amend" anywhere), not on who
  implements next.
- No code exists yet, so I could not execute retrieval or the writer directly — this gate is
  inspection-only by design and I did not ask for tests, per the handoff's explicit exclusion.

## Blockers
None. Finding 1 is real and should be fixed, but is g2-scope, fails loudly rather than silently,
and is cheap — it does not meet the bar for blocking this gate a third time. See Finding 1 for the
full reasoning and recommended fix.

## Out-of-scope observations
- Finding 1 — recommend closing before g2 starts (costs one sentence), but not a hold on this
  gate; g2's own review gate is the backstop if it is not.
- Finding 2 — fold into the same editing pass as Finding 1 if convenient; cosmetic on its own.
- Finding 3 — carries naturally to g4 when §7 is next touched.

## Workflow Feedback
- **Handoff gaps:** None material. The hunt's explicit section list (§2, §3, §6, §7, §8, §9, §10,
  seam table, README) omitted §5 (the amend-assertion worked walk-through), which is where
  Finding 1 actually lives — the list reads as illustrative rather than exhaustive, and the
  governing instruction ("go through EVERY concrete mechanism description") correctly overrides
  the omission, but a future hunt dispatch for this doc class might name §5 explicitly to make
  sure the write-side worked example isn't the one section a reviewer skips because it wasn't on
  the list.
- **Context rediscovered:** None — the two prior handoffs/results and the doc itself carried
  everything needed.
- **Instructions improvised around:** Same docs-only-diff situation as both prior rounds (no code
  exists to smell-test). I followed the established precedent of treating sections/mechanisms as
  the analog of methods/classes for the Fowler pass, which again produced a genuinely useful flag
  (`shotgun-surgery` pointing straight at Finding 1) rather than ceremony.
- **What would have made this easier:** Nothing structural. One suggestion, building on round 2's
  own suggestion: the "what would a builder literally write" trace is powerful enough to be worth
  running not just against the previously-flagged primitives but against **every** named write/
  read operation in the document as a fixed checklist item (create, retire, amend, fetch,
  enumerate, select, neighbours) — this round's Finding 1 was found by extending the trace one
  operation past what the handoff named (fetch/enumerate/select/neighbours) to amend, which the
  handoff's own section list didn't flag. Promoting "trace every named write/read operation, not
  just the ones already flagged" to an explicit step in this skill's checklist (or the rework
  dispatch template) would make this systematic rather than depending on a reviewer noticing the
  parallel unprompted.

## Return status
`complete`
