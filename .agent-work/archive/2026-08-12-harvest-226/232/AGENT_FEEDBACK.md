# Agent Feedback Log (staged — see FENCE.md)

Staged under the Admiral epic-226 fence (main checkout `.agent-work/` is
read-only while the Admiral's epic lease is active); the Admiral harvests
this entry into the shared durable `.agent-work/AGENT_FEEDBACK.md` at
epic closeout.

---

## `2026-07-25` — `232`

**Run shape:** `commander (delegated)` · `10/10 spine steps closed (init,
context, understand, plan, execute [3 gates: g1/g2/g3], reconcile, triage,
review, feedback, archive) · 3/3 build items shipped` · `sonnet` throughout
(Commander + all 4 crew dispatches, per LAUNCH_ORDER-232.md budget)

**Instruction adherence:** `fully followed`
- Drove the engine start-to-finish via `claim`/`current`/`start`/`attest`/
  `attach`/`advance` on both `spine.json` and the child `execute.json` —
  never hand-edited either JSON.
- Independently re-verified all three PR-7 findings against current code
  before planning (not just trusted the launch order's pasted findings) —
  all confirmed accurate, including the one line-number drift
  (`install_constellation.py:430-431` -> `:531-533`) the order itself
  flagged.
- design-it-twice and the cold plan critic were both skipped at `plan`,
  each recorded as a named untaken road (postconditions c4/c5) citing
  `LAUNCH_ORDER-232.md`'s own Pre-empted Steps section — not a silent
  skip.

**Friction / unclear:**
- `checklist_engine.py attach --payload-file` requires the payload to be
  **JSON**, not the Markdown `IMPLEMENTER_RESULT`/`REVIEW_RESULT` files
  the crew handoffs actually produce. My first `attach ... --payload-file
  .agent-work/232/g1-implementer-result.md` failed with
  `json.decoder.JSONDecodeError`. Worked around by using `--field
  status=... --field artifact=<path> --field summary=...` instead
  (pointer-plus-summary, not the full markdown). This is a real
  ergonomics gap: the doctrine explicitly wants "return thin, write fat"
  (pointer to the durable artifact, not a copy inline) — `--field`-based
  attach IS that pointer shape — but nothing in `commander-core.md` or
  `crew-dispatch.md` states this up front, so a Commander discovers the
  JSON-only constraint only by hitting the traceback.
- `checklist_engine.py <verb> --why "... `break` ..."` (a `--why` string
  containing a backtick-wrapped code identifier) triggers Git-Bash command
  substitution when invoked through this harness's Bash tool with double
  quotes — the word inside backticks silently vanishes from the recorded
  digest even though the engine call itself still succeeds. Hit this once
  in gate g2 (an implementer crew's own workflow-feedback note, harvested
  below) and avoided it afterward by not backtick-quoting code identifiers
  inside `--why`/`--note` strings passed through Bash.

**Crew-reported friction** (harvested from IMPLEMENTER_RESULT/REVIEW_RESULT
Workflow Feedback sections at each `gN-integrate`):
- g1-implement: the handoff's verbatim `-k glob_to_regex` verification
  command silently collects zero tests if the new test class/method names
  don't literally contain that substring (pytest `-k` is substring-only,
  case/underscore-sensitive) — cost one dead-end run, fixed by renaming
  methods to a `test_glob_to_regex_*` prefix. Suggestion: handoffs pasting
  a verbatim `-k` filter should note the substring-match constraint
  alongside it.
- g1-review: none reported beyond a light note that the mandatory Fowler
  pass felt heavy for a 98-line additive-test diff (all 12 smells
  trivially absent) — but running it in full (rather than self-granting a
  skip) is what the skill requires, and it did surface one real, if minor,
  naming-convention observation a lighter pass would have missed.
- g2-implement: the `--why "...`break`..."` backtick issue above (this is
  where I first hit it, via the implementer's own engine-drive inside its
  plan).
- g2-review: two catches, both non-blocking but both real: (1) my own
  g2-reviewer-handoff.md stated a derived baseline count ("1047") that was
  off by one (should have been 1046 = 1037-true-baseline + 9 from g1) —
  the reviewer caught it by independently checking out the true pre-g2
  commit into a throwaway detached worktree rather than trusting my
  arithmetic; (2) a map-anchor line number I wrote at plan time
  (`_adjudicate_orphan` at `:1042`) drifted by ~16 lines once g2's own
  edit shifted the file — anchors captured at plan time can go stale
  *within* the same run as earlier gates edit the file, not just across
  runs (a narrower case than the existing verify-before-plan lesson, which
  is about trusting a *prior run's* claims).

**What worked:**
- The crew-verification loop (implementer claims a number, reviewer
  independently reproduces it, Commander re-verifies before advancing)
  caught two of the two accuracy nits above without any of them reaching
  the shipped diff or this verdict silently.
- `lesson:verify-harness-field-and-drive-real-writer` applied cleanly and
  concretely to g2: the handoff named the exact mechanism required (call
  the real `_write_meta`, then corrupt its real bytes), the implementer
  followed it exactly, and the reviewer independently confirmed the test
  body does what it claims rather than trusting the label.
- Treating item (c) as a reasoning gate (no crew) for a purely comment-only,
  grep-verifiable edit was proportionate — three pre-authored command
  postconditions (grep-absence checks) gave the same machine-checked
  rigor as a crew review would have, at a fraction of the wall-clock cost.

**Improvement signals:**
- `attach --payload-file` accepting only JSON, when the produced artifacts
  are Markdown by the templates' own convention, is a documentation gap →
  disposition: mentioned here, not distilled to a formal lesson this run
  (single data point, low severity, workaround is one line) — a Charter
  refresh candidate if it recurs.
- The `--why`/`--note` backtick-in-Bash-double-quotes footgun → disposition:
  mentioned here; genuinely a harness/shell interaction, not a doctrine
  gap, so likely belongs as a one-line callout in `windows.md`'s existing
  shell-hazards section rather than a new lesson entry — flagged, not
  applied this run (fenced from the shared doctrine file this run; see
  FENCE.md).
