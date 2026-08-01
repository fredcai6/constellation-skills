# Review Result

Status values follow `skills/workbench/references/status-model.md`.

VERDICT: BLOCK

## Assigned Gate
`g2` — the validated episode writer (issue #301, epic-298)

## Result
`BLOCK`

Survey driven end-to-end through the checklist engine at
`.agent-work/301/g2-review/review.json` (10 items: the 6 standard reviewer checks r0–r5,
the required Fowler pass r6, plus 4 handoff-specific checks appended for this gate's
"HUNT THESE SPECIFICALLY" list — r7 layout-default, r8 wrong-answer probes, r9
write-phase atomicity, r10 test quality). Consolidated `verdict=BLOCK`, lease released.
Fowler pass recorded at `.agent-work/301/g2-review/fowler-pass.json`, cleared
`verify_fowler_pass.py`.

## Handoff compliance

All 8 close criteria (C2–C8, C7) verified independently and hold under normal
operation:

- **C2** (per-bin field-name allowlist): confirmed both directions via the fixture and
  9 own probes (casing variant, whitespace variant, unknown mechanical field, unknown
  agent-supplied kind, mechanical field name smuggled into agent-supplied).
- **C3a** (non-empty retire reason): confirmed via fixture + probe; a whitespace-only
  reason is rejected, a punctuation-only reason (`"---"`, `"."`) is accepted — this
  matches the doc's literal "non-empty reason" wording, not a bug.
- **C3b** (newline injection defense): confirmed for literal `\n`/`\r` and a lone `\r`.
  **Found a real gap in the same guard — see Blockers.**
- **C4** (all-or-nothing): confirmed for every validation-time failure path, including a
  new probe against a pre-existing CRLF file (byte-for-byte unchanged, CRLF preserved,
  across both a structurally-invalid op and an apply-time "no such episode" failure).
  **Found the guarantee does not extend to a write-phase I/O failure — see Blockers.**
- **C5** (store root seam, no `durable_root()`): confirmed; `durable_root` appears only
  in a docstring (2 grep hits, lines 374–375), `store_root()` uses the literal
  `episodes/` path.
- **C6** (surgical single-field dispute): confirmed via suite + reasoning; sibling
  assertion block is byte-identical across a dispute.
- **C7** (fixtures at exact paths): confirmed, all three exist.
- **C8** (retirement routes through `apply_retirement()`): confirmed; the retire op
  never inlines a file-move or in-place-only write at the call site.

**Layout-default judgment call — independent ruling (the item you most wanted a second
opinion on):** I agree with your provisional lean. This is genuinely "unbound with a
placeholder," not "Option B, bound, with a comment saying otherwise." Three properties
distinguish a real placeholder from a disguised decision, and all three hold here: (1)
reversal cost is zero today — `episodes/` holds only `README.md`; (2) the switch is
real, not decorative — all 6 layout-dependent seams (the 5 EPISODE_STORE.md §7 names,
plus the implementer's honestly self-flagged 6th, `_new_episode_path()`) gate off one
`_LAYOUT_ADAPTER` constant, and two suite tests flip it at runtime and exercise Option A
end-to-end successfully — a hypothetical seam would have one adapter; this has two,
proven; (3) every branch is marked `TODO(g4)` and both the module docstring and
EPISODE_STORE.md §7 state in prose that this is held for ratification. A CLI-exposed
`--layout` flag would not be materially better — it adds configuration surface without
removing the need for some default when unset, and nothing outside the test suite calls
this module today. One cheap, non-blocking refinement: a stderr note when the placeholder
default is exercised on a real (non-test) write would give #305's future unattended
capture wiring a visible signal that it's running against an unratified layout.

## Scope drift
None. `git status --short` shows exactly the 3 documented new/untracked paths. No edit to
`LESSONS.md`, `apply_lessons_delta.py`, or issue #300's manifest. No retrieval code
(g3). The retirement layout was not ratified.

## Evidence verdict
All of the handoff's own evidence commands reproduce exactly, including the full-suite
count (`1175 passed, 2 skipped` — matches the claimed baseline precisely) and the
`durable_root` grep (2 hits, both inside the docstring). Went beyond re-running the
suite per `lesson:round-trip-tests-prove-artifacts-not-parsers`: authored 19 new
adversarial delta inputs not in the handoff's evidence list (see Blockers/Out-of-scope
observations for what they found).

## Code/doc quality
Determinism constraint held (no `date.today()`/`datetime.now()`/wall-clock call in the
module; the one grep hit is the docstring naming the constraint). No hidden fallback —
every validation failure raises `EpisodeDeltaError` to a nonzero exit. `newline=""` used
consistently on every read/write, as documented. Fowler pass (r6, required item):
recorded and cleared the rail. Two non-blocking refinements flagged: `parse_episode()`
is a ~110-line function with a nested closure that could be split; `apply_delta()` and
`_dry_run_log()` duplicate the exact same 3-branch op-kind dispatch verbatim (extract a
shared `_dispatch_ops()` helper). Two smells present but overridden against
EPISODE_STORE.md's own frozen obligations (the mechanical-bin data clump is the
record grammar itself; the dual-adapter "speculative" generality is contract-mandated by
§7's seam table, not implementer scope-creep) — both logged with standard + reason in
`fowler-pass.json`.

## Map impact verdict
- **Evidence supports claimed change:** yes — every claim in the Map Impact section
  (partition-cannot-be-misfiled, all-or-nothing, surgical dispute) is backed by the
  named tests, independently reproduced.
- **Constraints not violated:** yes — `constraint:llm-never-writes-the-store-directly`,
  `constraint:partition-enforced-at-the-writer`, `constraint:markdown-in-git` all held.
- **Notes match the diff:** yes, with one honestly self-reported gap: `_new_episode_path()`
  is a 6th layout-dependent seam not named in EPISODE_STORE.md §7's 5-seam table.
  Implemented consistently with the other 5 (same switch), so additive, not a
  contradiction — flagged as a triage candidate below.
- **Decision candidates surfaced:** yes — the layout stays explicitly un-bound;
  own-latitude decisions (op vocabulary, no delta-supplied id, no wall-clock reads) are
  logged, not silently made.
- **Durable context routed:** yes, via the triage candidate below.

## Reconciliation check
No divergence from the recorded architecture beyond the additive 6th seam noted above.

## Blockers

1. **[HIGH] Silent data corruption via a line-boundary character the newline guard
   doesn't check for (touches C3b).** `_reject_newline()`
   (`scripts/apply_episode_delta.py:116–126`) only checks for the literal characters
   `\n` and `\r`. But `parse_episode()` sections and extracts fields using
   `str.splitlines()` throughout, and Python's `splitlines()` treats a **wider**
   character set as line boundaries: `\v`, `\f`, `\x1c`–`\x1e`, `\x85` (NEL), `U+2028`
   (LINE SEPARATOR), `U+2029` (PARAGRAPH SEPARATOR). **Demonstrated:** a `create` op
   with `observed-behavior.statement = "safe text - status: retired"` contains
   neither `\n` nor `\r`, so it passes the guard and writes successfully. The file on
   disk is written correctly the first time (the raw string is emitted as one `f-string`
   substitution, no OS line break inserted). But the **next** time that episode is
   touched by any op — an `amend-assertion`, a `retire`, or literally the same
   `parse_episode()` call any read path uses — `splitlines()` treats the embedded
   `U+2028` as a line break, so the assertion's `statement` field silently truncates to
   `"safe text"`; the rest is dropped into an unused dict key and discarded when the
   `Assertion` dataclass is built. No error, no crash, no exit code — `render(parse(text))
   == text` (the suite's own round-trip invariant) fails for this input, but nothing in
   the writer surfaces that. This is exactly the injection/corruption class
   EPISODE_STORE.md §7 names as the reason single-line enforcement exists — the
   demonstrated instance isn't the doc's exact named scenario (forging a literal
   `- status: retired` line past the Option-B membership check, which actually reads the
   header's `status=` token, not a body-line grep — so that specific downstream exposure
   does not fire here) — but it is the same root cause (the guard's line-boundary
   definition doesn't match the parser's), and it demonstrably corrupts stored content.
   **Suggested fix:** replace the character-set check with the parser's own line-boundary
   definition, e.g. `if len(value.splitlines()) > 1: raise ...`, closing the whole class
   rather than one more character at a time.

2. **[MEDIUM] All-or-nothing does not hold across a write-phase failure (touches C4).**
   `_Transaction.commit()` (`scripts/apply_episode_delta.py` ~684–690) iterates
   `writes.items()` and calls `path.write_text()` once per touched file with no staging
   or rollback. **Demonstrated:** with two individually-valid `create` ops touching two
   different files, monkeypatching `Path.write_text` to raise on the second call
   (simulating a real OS-level failure — disk full, permission denied, a locked file,
   any of which are real hazards on Windows) leaves the **first** file's write landed on
   disk, while `apply_delta()` still raises and the CLI still returns exit 1. The
   validate-then-write **separation** is real and complete (confirmed independently: a
   structurally-invalid op, and an apply-time "no such episode" failure, both leave a
   pre-existing file byte-for-byte unchanged, including a simulated pre-existing CRLF
   file). What's missing is that the **write step itself** is not atomic across multiple
   files. This contradicts the module docstring's own unconditional claim ("applies them
   mechanically, all-or-nothing... leaves the store byte-for-byte unchanged") for this
   one failure class. Lower likelihood than #1 (requires an actual OS I/O failure, not
   just adversarial input), and the failure is not silent to the immediate caller (exit
   code 1) — but the store itself is left partially mutated with no automatic recovery.
   **Suggested fix:** write every touched file to a temp path first (or a scratch
   staging dir), and only `rename()`/move into final place once every write has
   succeeded — the ordinary temp-then-rename atomic-write pattern.

Both are mechanical, scoped fixes to the same module — I would expect this to return to
review quickly once addressed, not a design-level rework.

## Out-of-scope observations
- **Triage candidate (already flagged in the engine survey, `tc1`):** EPISODE_STORE.md
  §7's seam table names 5 layout-dependent seams; g2 needed a 6th
  (`_new_episode_path()`), implemented consistently with the other 5. No code risk — the
  doc's table should gain a 6th row next time EPISODE_STORE.md is touched.
- Top-level unrecognized keys on a `create`/`retire`/`amend-assertion` op (outside the
  `mechanical`/`agent_supplied`/`diagnosis` sub-dicts) are silently accepted and ignored
  — e.g. `{"op": "retire", "id": "...", "reason": "...", "sneaky-field": "..."}` succeeds.
  Not a data-corruption risk (the stray key is genuinely unused), and
  `apply_lessons_delta.py` has the identical laxity at its own op level, so this is not a
  regression — worth a minor tightening pass at the next touch of this file, not urgent.
- Duplicate ops targeting the same assertion/episode within one delta (e.g. two
  `amend-assertion` ops on the same `a1` in one delta) are accepted; the second silently
  wins. Not contractually prohibited by EPISODE_STORE.md, and arguably reasonable
  last-write-wins semantics within a single delta — flagging only because it was untested
  behavior before this review.

## Workflow Feedback
Mandatory section. A `none` answer requires a run-specific reason: `none — confirmed
after review: <what you checked>`; a bare `none` is treated as an unfilled field. This
is workflow signal, not project signal: you are the only one who saw this friction — if
you do not report it here, it is lost.

- **Handoff gaps:** None load-bearing. The handoff's evidence-reproduction commands were
  exact and all reproduced cleanly on the first try — no ambiguity there.
- **Context rediscovered:** None — EPISODE_STORE.md's §7 seam table and the handoff's own
  "HUNT THESE SPECIFICALLY" list pointed directly at the productive probes; the
  U+2028 finding came from generalizing the doc's own stated *reason* for the
  single-line-enforcement obligation ("a naive line-oriented parser...") past the literal
  character the guard checks for, which the doc itself invites by explaining the
  mechanism rather than just stating the rule.
- **Instructions improvised around:** The "Survey State Location" convention named in the
  `constellation-reviewer` skill (`.agent-work/<work-id>/<gate>-review/review.json`)
  isn't explicit in this handoff (which only names the final result file's path). I used
  `.agent-work/301/g2-review/review.json`, matching the skill's own stated convention —
  worth confirming this is the intended location, or having the handoff name it
  explicitly so a reviewer doesn't have to infer it.
- **What would have made this easier:** Nothing significant — the handoff's "HUNT THESE
  SPECIFICALLY" section (especially the explicit invitation to author new adversarial
  inputs rather than re-run the suite) is exactly what made the two blocking findings
  possible; more handoffs at this gate tier would benefit from the same shape.

## Return status
`complete`
