# Review Result

## Assigned Gate
`g1 — per-agent binding key in the store` (work id `issue-419-governor-identity`, branch
`epic-418/a-419-governor-identity`, commit `340c46d`).

Survey driven through the engine at
`.agent-work/issue-419-governor-identity/g1-review/review.json` (7 template checks + 8 appended,
lease `g1-reviewer-1`). Fowler pass record at `.agent-work/issue-419-governor-identity/g1-review/FOWLER_PASS.json`.

## Result
`APPROVE`

The central non-vacuity claim reproduced exactly: reverting `scripts/hooks/spine_rail.py` to the
pre-change tree turns 13 of the 16 new tests red and leaves all 61 pre-existing tests green.

## Handoff compliance

The change is what the handoff described, verified against the diff rather than the report:
`binding_key()` as the sole composer (`scripts/hooks/spine_rail.py:139-186`), `session_view()`
(`189-213`), both routed into `handle_post_tool_use`'s claim / release / empty-set-cleanup writes and
into `decide_stop` / `decide_session_start`'s reads, plus `tests/fixtures/probe_payloads.jsonl` pinned
by a sha256 test.

### Close criteria

| # | criterion | verdict | evidence I personally reproduced |
|---|---|---|---|
| 1 | three-way table implemented exactly, including bind-nothing | **met** | Read the branch, then probed `binding_key` directly with 25 of my own cases. Bind-nothing is a distinct early return, not a fallback — the only path returning the bare sid is the `agent_id not in data` branch, so a present-but-unusable id cannot reach the parent's key. |
| 2 | composite claim leaves the bare set byte-identical; two ids give two key sets | **met** | Claim path assigns `binding[key]` and never `binding[sid]`. Tests assert `json.dumps(binding[sid], sort_keys=True)` unchanged and `[len(v) for v in binding.values()] == [1, 1]` — the gauge writer's own ambiguity predicate. Both red on revert. |
| 3 | composite release removes only that agent's entry | **met** | `del binding[key]` at `spine_rail.py:453`, read directly. The cleanup test binds parent and subagent to the *same* spine path under different keys, so a wrong `del binding[sid]` would wipe a live parent's binding; after release the composite key is gone and the parent's set is json-identical. |
| 4 | unusable `agent_id` writes no binding anywhere | **met** | `if key is None: return {}` at `spine_rail.py:424` fires *before* `load_binding`, so nothing is written, deleted, or nudged. Test asserts the whole store json-identical after seven malformed claims, and that the bad spine is not under the parent's bare key. |
| 5 | `decide_stop` / `decide_session_start` still see every spine they saw before | **met** | Proved `session_view` is a strict superset by calling it myself on a bare-key-only store — identical to the old `binding.get(sid) or {}`. Plus the composite-only Stop block and the composite-only SessionStart resume. |
| 6 | every pre-existing test passes **unedited** | **met** | Not just green: a `difflib.SequenceMatcher` over the old and new test files reports **two `insert` opcodes and zero `replace`/`delete`**, so no surviving test's body was altered. Removed-test set is empty; 58 → 74 defs. |

### Non-vacuity — the check the handoff said would decide the gate

```
git checkout HEAD~1 -- scripts/hooks/spine_rail.py && python -m pytest tests/test_spine_rail.py -q
13 failed, 61 passed in 1.27s
git checkout HEAD -- scripts/hooks/spine_rail.py && python -m pytest tests/test_spine_rail.py -q
74 passed in 0.91s          # working tree clean afterwards
```

Reproduced to the test. The 13 reds are every hook-dependent new test (3 `binding_key`, 5 write-routing,
5 read-routing). All 61 pre-existing tests stay green under the revert, so the reds are caused by the
change being absent, not by a broken harness.

Note the recipe: the implementer's result says `git checkout HEAD --`, which was correct while the work
was uncommitted and is now wrong — `HEAD` is `340c46d`. Use `HEAD~1`.

The fixture pin's own failure mode reproduced separately: injecting `agent_id` into payload 0 (mutation
asserted applied) gives `6 failed, 68 passed` including `test_probe_fixture_sha256_pin`; restored via
`git checkout`, back to 74 passed with a clean tree.

### The `session_view` vacuity concern — answered

`test_session_view_merges_one_bare_and_two_composite_keys` builds a five-key store through the *real*
claim writer: one bare, two composite, plus two decoys — another session's composite key and a
`<sid>-lookalike` key that `startswith` the sid but is not a child of it. It asserts `len(view) == 3`
with the exact key set. The lookalike is what forces the prefix test to be `sid + BINDING_KEY_SEP`
rather than a bare `startswith`, and it would fail the sloppy implementation.
`test_stop_blocks_on_mid_flight_spine_held_only_under_a_composite_key` does exactly what the handoff
demanded: the bare key holds only a released complete spine, the sole mid-flight spine is under a
composite key, and `decide_stop` blocks naming that spine's gate.

### The nudge ledger — adjudicated, as asked

**The implementer's reading is right, and I would call it the only safe one.**

`.claude/settings.json` registers `spine_rail.py` on `Stop`, `SessionStart` and `PostToolUse` — *not*
`SubagentStop` — and `main()` dispatches only those three. So `nudges[sid]` is written in exactly one
place (`decide_stop`) and only ever for a **top-level** session's turn-end. The strikes are the parent's.

Without `if key == sid`, every subagent release would `del nudges[sid]`. Crew subagents release routinely
mid-run, so the parent's count would be reset over and over, could never reach 3, and a genuinely stuck
top-level session would never get its escape hatch — a live-lock strictly worse than anything before this
change. The opposite risk does not materialize: the parent's own release still clears the ledger, and
`decide_stop` rewrites `nudges[sid]` wholesale on every block, so a stale entry cannot accumulate false
strikes.

On the handoff's apparent contradiction: constraint 1 is about the ledger's **key shape**, and it is
satisfied — the ledger is still bare-keyed. Gating the **fire condition** on `key == sid` is a separate,
orthogonal decision that the required-evidence list demanded and constraint 1 never forbade. Read as two
properties rather than one rule, there is nothing to resolve.

## Scope drift

None. `git diff --stat main...HEAD`: the only non-`.agent-work/` files touched across the whole branch are
the three allowed ones — `scripts/hooks/spine_rail.py` (+156/−20), `tests/test_spine_rail.py` (+468/−0),
`tests/fixtures/probe_payloads.jsonl` (+6/−0). `scripts/hooks/gauge_writer_hook.py` appears **zero** times
in the branch's changed-file list and its `resolve_gauge_path` still reads `binding.get(session_id)` at
line 159 — the declared g2 exclusion is honored, and the interim state is the one the handoff pre-declared
as expected.

## Evidence verdict

Every number reproduced by me, not read off the report.

| command | result |
|---|---|
| `python -m pytest tests/test_spine_rail.py -q` | `74 passed in 0.92s` |
| `python -m pytest tests -q` | `1637 passed, 2 skipped, 550 subtests passed in 437.61s`, exit 0 |

1637 is exactly the handoff's expected count, so the new tests demonstrably exist (1621 would have meant
they did not). The fixture verified independently: 6 lines, all one `session_id`, decomposition **2 parent
Bash / 2 subagent / 2 parent Agent** — the handoff's provisional 3/2/1 is wrong and the implementer was
right to correct it. Normalized sha256 `b0353686…` matches the pin, and the fixture is byte-identical to
`.agent-work/issue-419-governor-identity/evidence/probe-payloads.jsonl`. Wrapper-vs-payload confirmed:
`agent_id` exists only inside `payload`, never at the wrapper's top level, and `probe_payloads()` unwraps it.

Test mode was `test-first` and the implementer attested red output at each of four sub-gates. I did not
re-derive those reds — they are historical — but the revert experiment is the stronger form of the same
claim and it reproduced.

## Code/doc quality

Against `docs/agents/CREW_CONTEXT.md`'s verification discipline, the four rules that bite here hold:

- **Cannot-fail checks** — both demonstrations reproduced above.
- **Assert behaviour, not text** — tests call the real handlers and assert on the store and the returned
  decision dict. The one string assertion (`COMPOSITE-MARKER in out["reason"]`) is an imperative the test
  itself planted in the spine, so it proves the right spine was reached.
- **Loops assert what they looped over** — every looping guard prints and asserts a count: 4 bare / 2
  composite over 6 real payloads, 12 adversarial rows each labelled, 3 merged entries out of 5 store keys,
  and a whole-store json comparison for the reject case.
- **Never compare raw working-tree bytes** — the pin hashes newline-normalized bytes and says why. I
  confirmed raw 13161 vs normalized 13155 on this checkout, so a raw pin genuinely would have been wrong.

`python` used throughout, never `py`.

**Fowler refactoring pass** (full 12-smell record, rail exits 0): one **flagged** — `handle_post_tool_use`
is now 85 lines (64 code) holding parse + resolve + claim + release + cleanup + nudge-ledger; extracting
`_apply_claim` / `_apply_release` would make the `key`/`sid` asymmetry visible at a glance instead of
eleven lines into a comment block. Non-blocking, aimed at g2, which will touch the same function. Six
**overridden** with logged standards (duplicated-code, data-clumps, primitive-obsession, shotgun-surgery,
divergent-change, comments-as-deodorant); five **absent**.

The most interesting override: the composite-key expression is deliberately restated in eight tests rather
than computed via `sr.binding_key()`. That is duplication on its face, and it is correct — deduplicating it
through the function under test would make each assertion tautological.

## Map impact verdict

- **Evidence supports claimed change:** yes. The claimed capability — the store can attribute an entry to
  the agent that produced it — is exactly what the composite-key tests demonstrate through the real writer.
- **Constraints not violated:** the stated constraint that `binding_key` is the **single** composer holds by
  command: `grep` over `scripts/` finds one composition site (`spine_rail.py:184`) and one prefix site
  (`203`), both keyed off `BINDING_KEY_SEP`, and no second composer anywhere.
- **Notes match the diff:** substantially, with three counting slips, none material — see Out-of-scope
  observations.
- **Decision candidates surfaced:** yes — `decision:agent-id-null-is-unusable` was raised for a Commander
  glance rather than decided silently. My view is recorded below.
- **Durable context routed:** yes. Seven triage candidates carried on the survey.

## Reconciliation check

No architecture baseline to diverge from — `docs/architecture/` does not exist in this repo, so there is no
Cartographer map to reconcile against. The one real documentation divergence is `docs/GAUGE_WRITER_HOOK.md`
(line 14 and line 318 still describe the store as keyed by `session_id`) and `gauge_writer_hook.py`'s
docstring. Issue #419's own item 4 already owns that file and this gate's scope forbids touching it, so it
is routed as a triage candidate rather than treated as a g1 defect.

## Blockers

- none.

## Out-of-scope observations

Seven, all carried as triage candidates on the survey.

1. **`docs/GAUGE_WRITER_HOOK.md` is now wrong for subagents** (lines 14 and 318). Issue item 4 owns it.
2. **`gauge_writer_hook.py`'s module docstring (26-33)** is stale in the same way; it sits in g2's file.
3. **The implementer's blast-radius table under-enumerates.** The grep returns 88 paths here — 77 under
   `.agent-work/`, 11 elsewhere — not "84 `.agent-work` artifacts and 5 live readers". The four unlisted
   non-`.agent-work` paths are `notes-261.md`, `notes-269.md`, `skills/_shared/windows.md` and
   `tests/test_install_constellation.py`. None is a behavioral reader, so nothing in the verdict changes,
   but the enumeration should be redone by command for g2.
4. **`_AGENT_ID_REJECT` is a hand-maintained character list**, which `CREW_CONTEXT.md` warns against by
   name. Its stated consumer is the gauge writer's `agent-{agent_id}.jsonl` path, yet `:`, `*`, `?`, `"`,
   `<`, `>`, `|` and a whitespace-only id all pass the guard and are path-hostile on Windows (probed:
   `binding_key({"session_id": "S", "agent_id": "a:b"})` returns `'S#a:b'`). g1 implemented the handoff's
   table exactly, so this is **not a g1 defect** — it routes to g2, which owns the path interpolation.
5. **An untested ordering nuance in `decide_session_start`.** It takes the first non-foreign entry from the
   merged view, and merge order is store insertion order across bare and composite keys. If a subagent
   claimed first, a resumed top-level session can now be advertised a *subagent's* spine. Same-worktree is
   required for it to bite and the consequence is cosmetic, so it fails no close criterion — but nothing
   pins the preference, and "prefer the bare key first" is a one-line change if the Commander wants it
   deterministic.
6. **Co-signing the implementer's observation 4, verified.** `tests/test_spine_rail.py:898` monkeypatches
   `_scan_active_spine` with a lambda returning a spine *dict* where the real function returns a list of
   `(spine_dict, spine_path)` tuples. Pre-existing (#261), never reaches the unpacking branch, correctly
   left alone.
7. **My view on `decision:agent-id-null-is-unusable`:** keep it as implemented. It follows the table
   literally, it is unreachable on harness 2.1.222 (which omits the key rather than sending null), and
   fail-closed is right for an identity this repo does not own. Worth recording, though: **nothing in the
   suite would detect a harness that starts sending `agent_id: null` on parent calls** — the fixture pin
   guards a static capture, not the live harness — and the symptom would be total, silent gauge blindness
   for every top-level agent. Cheap insurance, if wanted, is a g2-era assertion over a freshly *re-taken*
   capture, not a re-read of this one.

Three narrative counting slips in the implementer's result, none material and all contradicted by its own
correctly-measured printed counts: "the two remaining new tests" pass against the old hook (it is three —
`test_post_release_parent_still_clears_its_own_bare_nudge_ledger` is the third, a legitimate
unchanged-behavior guard); "84 `.agent-work` artifacts" (77); "four routed call sites" followed by a list
of five. The measured, printed numbers in that report were all correct; the prose counts around them were
not. Worth a glance from whoever reads it next.

## Workflow Feedback

- **Handoff gaps:** one that cost me a real detour. The handoff's non-vacuity instruction says reverting
  `spine_rail.py` "to HEAD" turns 13 of 16 tests red, inheriting the implementer's phrasing from when the
  work was uncommitted. It is now committed as `340c46d`, so `git checkout HEAD --` reverts to the
  **changed** file and the experiment silently proves nothing — the single most important check in the
  gate has a recipe that no longer runs. A handoff that pins an experiment to a revision should name the
  commit (`HEAD~1`, or `4767782`), never a moving ref.
- **Context rediscovered:** two things. `docs/agents/engine-config.json` does not exist in this repo even
  though every checklist's `config_ref` names it; the engine degrades quietly, but I had to check that the
  absence was benign rather than a broken instantiation. And the handoff gives verification commands but no
  Survey State Location field, so I took the path from the skill's default
  (`.agent-work/<work-id>/<gate>-review/review.json`) — worth stating explicitly, since the skill calls that
  field out as something the handoff gives.
- **Instructions improvised around:** the reviewer skill says to record the Fowler pass "to
  `templates/FOWLER_PASS.template.json`", which reads as writing into the installed skill's own template.
  I wrote an instance into the issue workbench
  (`.agent-work/issue-419-governor-identity/g1-review/FOWLER_PASS.json`) and pointed the rail at it, which
  is plainly the intent, but the wording should say "an instance of" the template. Separately, the engine's
  `append` verb has no way to place a new check before an existing one, so my eight per-criterion checks
  land after `r6-fowler` even though most of them are `r1`/`r3` refinements — harmless for a survey, worth
  knowing.
- **What would have made this easier:** pin the revert experiment to `HEAD~1` in the handoff text, and add
  the Survey State Location field the skill expects.

## Return status
`complete`
