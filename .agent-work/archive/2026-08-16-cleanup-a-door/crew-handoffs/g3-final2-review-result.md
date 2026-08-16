# Review Result

## Assigned Gate

`g3` — issue #603, the door cannot be bound by the session that needs it. Final review,
attempt 4, at `5a626351`. Scoped by the REWORK-3 addendum to five items.

Survey driven through the engine at
`.agent-work/cleanup-a-door/g3-final2-review/review.json`, session
`constellation/cleanup-a-door/g3-final2/reviewer/attempt-1`. All seven items visited,
consolidated `APPROVE` with one recorded `fail` carried by an explicit `--override-reason`.

## Result

`APPROVE`

## Handoff compliance

The five REWORK-3 items, each verified independently. Every claim below is something I ran,
not something I read in a report.

### Item 1 — the four corrected claims, checked against the AST

**`scripts/mcp_spine_server.py:30-38`.** "`_bind_process_to`, the one place `SPINE` and
`SESSION` are assigned outside module scope" is exact. An `ast.walk` over the whole module
finds assignments to those two names at exactly four sites — `:201`/`:202` at module scope
and `:914`/`:915` inside `_bind_process_to`, which carries the module's only
`global SPINE, SESSION` (`:913`). No fifth site.

**`scripts/mcp_spine_server.py:131-143`.** Three separable claims, all true:

- `_spine_open`'s own source references none of `SPINE`, `SESSION`, `run_engine` — its
  `ast.Name` set is `{OSError, Path, RuntimeError, _bind_process_to, _lifecycle_result,
  _primary_checkout_for_lifecycle, _rebind_refusal, _require, _resolve_confined, _tool_error,
  args, base, blocked, candidate, dict, err, escapes, exc, isinstance, opened, os, parent,
  root, spec, spine_lifecycle, str, work_id, wt_root}`.
- It takes the primary checkout from `_primary_checkout_for_lifecycle` (`:1012`).
- That helper "reads no environment at all" is **literally** true: its `ast.Name` set is
  `{Path, SPINE, __file__, _git_rev_parse, anchor, common}` — the name `os` does not occur in
  it. Its body at `:857` is
  `anchor = SPINE.parent if SPINE is not None else Path(__file__).resolve().parent`, which is
  the bound spine's directory when there is one and this script's own when there is not,
  exactly as the docstring says.

**`SPINE_FILE` is read zero times in `_spine_open`.** Its only `os.environ` node is
`os.environ.get('SPINE_PARENT')` at `:1031`; the only `'SPINE_FILE'` literal in the function
is the subscript `opened['SPINE_FILE']` at `:1041`, a key on `open_work`'s return value.

**`tests/test_mcp_lifecycle.py:335-341`.** Comment and the `os.environ["SPINE_FILE"]` write
are both gone. I proved inertness my own way rather than accepting the implementer's mutation
probe: I ran `SpineOpenContainmentTests` under three different ambient `SPINE_FILE` values —
unset, `/nonexistent/poison/spine.json`, and a real unrelated spine — and got `3 passed` each
time. The test does not depend on that variable under any of them.

**`tests/test_mcp_adoption.py:98-105` and `:169-181`.** Both replacement rationales check out
against source: `SPINE: Path | None = _spine_from_env()` and
`sys.path.insert(0, str(ENGINE.parent))` are both present at module scope, so "importing is
not side-effect-free" names two real side effects, and "with neither variable named the
module-scope binding is simply `SPINE = None`" is what `_spine_from_env` returns.

**`tests/test_mcp_identity.py:551`.** The quoted sentence is a verbatim,
whitespace-normalized substring of the live module docstring — checked by comparing against
`ast.get_docstring`, not by eye.

### Item 2 — `docs/CHECKLIST_ENGINE_DESIGN.md`

Corrected, and **not fully accurate**. This is the one finding; see Blockers-and-findings
below. Its presence outside the enumerated nine-file list is justified and I rule it in
bounds.

### Item 3 — no behaviour changed

`git diff 176133ac..5a626351 --stat` touches five files. Every `scripts/mcp_spine_server.py`
hunk falls inside the module docstring, which spans `:2-144`. The test-file hunks are
docstrings and comments except the one deleted setup line, proved inert above. No executable
statement was added anywhere in the rework.

### Item 4 — my own blast-radius sweep

**Command and count, both passes.** Script at `/tmp/sweep.py`, method reproduced here so it
can be re-run:

- For `.py` files, parse the AST and take every `ast.Constant` string plus every
  `tokenize.COMMENT`. Python already concatenates implicitly-joined adjacent string literals
  into **one** `Constant` — that is precisely the hole that hid blocker 2 from a line-based
  `grep`.
- For `.md`/`.json`/`.txt`, take the whole file.
- Whitespace-normalize every unit with `re.sub(r"\s+", " ", u)` before matching, so a claim
  wrapped across source lines still matches.
- Identifier list taken **by command**:
  `git diff a69bbac4..4e1f22cb -- scripts/mcp_spine_server.py | grep -E '^[-+](def |[A-Z_]+ *[:=])'`
  → deleted `CALLLOG`, `START_MARKER`, `REJECTIONLOG`; changed contract on `SPINE` and
  `ENGINE`; plus the dropped `.mcp.json` demo default.

**Pass 1** over `scripts/ tests/ examples/ docs/`: **207 files, 36 raw hits**, every one read
by hand.
**Pass 2** added the pattern pass 1 missed — prose that quotes the deleted module-scope *code
form* (`os.environ["SPINE_FILE"]`, `SPINE = Path(os.environ...)`): **198 files, 7 hits**.

> I found that gap the honest way: pass 1 returned nothing from
> `scripts/hooks/spine_rail.py`, which the addendum told me held a live claim. Rather than
> assume the addendum was wrong, I asked why my method could not see it. It was matching
> claim *phrasings* and not quoted *code*. Stating this because a sweep that silently misses
> a known instance is the same failure mode as the three it was built to catch.

**COUNT: live in-scope invalidated claims = 0.**

Classification of every hit, read individually rather than trusted to the classifier:

| Hits | Verdict |
|---|---|
| `mcp_spine_server.py:157`, `:798`, `:879`; `test_mcp_identity.py:494` | Correct, not stale — they frame the old form **historically** ("this used to be…", "this used to read…") or quote it to mark that it changed. These are the ones the addendum predicted. |
| ~14 `KeyError` hits across `test_checklist_engine.py`, `test_crew_launcher.py`, `test_crew_worktree_cwd.py`, `test_explorer_templates.py`, `test_gauge_chain_writer_to_trip.py`, `test_install_constellation.py`, `validate_spine.py` | Unrelated subjects — the engine's own missing-`items` `KeyError`, crew-resume legacy entries, template drift. Not blast radius. |
| `mcp_spine_server.py:732`, `test_mcp_identity.py:1048` | **False positives of my own classifier.** Both describe `call_tool`'s `raise KeyError(name)` on an *unknown tool name* — which is still the last statement of `call_tool` and still live. Nothing to do with the import-time death. |
| `test_install_constellation.py:4021`, `test_wire_mcp_interpreter.py:42` | Carry the old demo-default string, but only as arbitrary **fixture data** for interpreter-placeholder rewriting. They assert nothing about the shipped `.mcp.json`. |
| `examples/mcp-interactive-demo/README.md:10` | Correct. The demo path survives only as the explicit `SPINE_FILE=… claude` launch line that dropping the default now *requires*, and the paragraph above it says `.mcp.json` no longer defaults to it. |
| `test_mcp_identity.py:861` | Still true. "Moving `SPINE_FILE` in the environment cannot move where the door points" holds, because `_unbound_refusal` reads the module global `SPINE` per call and never re-reads the env. |
| `test_mcp_lifecycle.py:200` | **Accurate — this is the implementer's explicit "the reviewer should rule" question, and I rule it sound.** `SPINE_PARENT` genuinely is re-read fresh at `:1031` and genuinely is *not* touched by `_bind_process_to`, so it is still server-launch-time state; the parenthetical names exactly what is read. No correction needed. |
| `scripts/hooks/spine_rail.py:1081` | Live invalidated claim. **Fenced, out of scope**, already floated. |
| `tests/test_spine_rail.py:2698` | Live invalidated claim, **not previously named** — see observations. |

### Item 5 — full clean-env suite

Reproduced. `__pycache__` cleared first
(`find . -name __pycache__ -type d -not -path "./.git/*" -exec rm -rf {} +`, per #597), tree
clean for `scripts/ tests/ docs/ examples/ map/ .mcp.json`, `git rev-parse HEAD` =
`5a6263510c532cdd5464d1867f5a9c8db7aa13e5`:

```
$ env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q
3093 passed, 6 skipped, 1153 subtests passed in 128.40s (0:02:08)
EXIT=0
```

Exactly the Commander's number. Saved to
`.agent-work/cleanup-a-door/evidence/g3-final2-suite.txt`.

## Scope drift

`git diff 176133ac..5a626351 --stat` → 5 files, 54 insertions, 31 deletions.
`git diff --name-only a69bbac4..5a626351` matches **none** of `scripts/checklist_engine.py`,
`scripts/run_crew.py`, `scripts/gauge_reader.py`, `scripts/hooks/**`. The implementer read
`run_crew.py:468-471` and `spine_rail.py` and correctly reported rather than touched them.

**Ruling on the implementer's three declared departures — all three in bounds.** They asked
for a ruling rather than deciding silently, which is the right move:

- `tests/test_mcp_adoption.py:172-179` — same file, same claim, different lines. Fixing four
  of five and reporting the fifth would reproduce the exact mistake this rework exists to
  correct.
- `tests/test_mcp_identity.py:18-23` — same file, same claim class, prose in a module
  docstring, no assertion touched.
- `docs/CHECKLIST_ENGINE_DESIGN.md:295` — `docs/` is named in the close criterion and is not
  fenced.

All three are prose-only and revert independently. Their being outside the handoff's
enumerated file list is a handoff-enumeration gap, not scope drift.

## Evidence verdict

Sufficient, and I reproduced rather than accepted it. Per the addendum I did **not** re-derive
what three prior reviews already reproduced: the six unbound-class refusals, bind-on-open
through to a successful `claim`, the regression suite red pre-fix, the module-wide assignment
pin's mutated control, `IdentityGuardSurvivesARebindTests`, the three env overrides, the
lease-held rebind refusal, unset `SPINE_ENGINE`, and `map/` freshness. That is an explicit
scoped null: **not re-tested by me this attempt**, carried on three prior reviews' evidence.

**One implementer claim does not reproduce as stated.** The result says
`tests/test_mcp_lifecycle.py:194` "and its positive control are byte-identical — `diff` over
lines 183-300 against HEAD is empty." Checked block-by-block against `a69bbac4`:

- the **positive control** `test_the_spine_open_identity_pin_can_fail` — byte-identical: **true**
- the **pin itself** `test_spine_open_never_references_spine_session_or_run_engine` —
  byte-identical: **false**. Its failure message changed at `176133ac`, three lines out, five
  in.

That change is the sanctioned blocker-2 fix, so nothing is wrong with the *code*; the claim is
just stated too absolutely (it is true of `5a626351`, not of `a69bbac4..HEAD`). The REWORK-3
addendum repeats the same over-broad phrasing. Recording it so the next reader does not
inherit it — no action needed.

## Code/doc quality

Fowler refactoring pass rendered independently over the gate's whole change and written to
`.agent-work/cleanup-a-door/FOWLER_PASS.json`;
`py scripts/verify_fowler_pass.py .agent-work/cleanup-a-door/FOWLER_PASS.json` exits 0
(`smells=12, flagged=['shotgun-surgery'], overridden=['duplicated-code', 'data-clumps',
'primitive-obsession', 'comments-as-deodorant']`), each override carrying its documented
standard and reason.

**One smell flagged: shotgun surgery**, and it is evidenced rather than asserted. One fact —
when and how the door acquires identity — is restated as unchecked prose across **23 distinct
sites** by measured AST-and-comment sweep (12 in `mcp_spine_server.py`, 9 across four test
modules, 2 in `docs/CHECKLIST_ENGINE_DESIGN.md`). That is an upper bound, since the pattern
also catches refusal text and test names; a prior reviewer's tighter count was about seven.
Either count, the consequence is measured: **three of this gate's four rework cycles were one
of those restatements drifting from the code, and my own finding below is a fourth.** Only two
sites are mechanically tied to the code by AST pins; the rest drift silently and repeatedly
have. Recorded `flagged` rather than `overridden` because no repo standard sanctions it —
`CREW_CONTEXT.md`'s "assert against behaviour, never against text that describes it" points
the other way. Already a triage candidate and acknowledged in the handoff as beyond this gate;
I concur it is out of scope to fix here.

## Map impact verdict

- **Evidence supports claimed change:** yes. "No behaviour changed" is backed by construction
  (all hunks inside docstrings/comments) and by my own three-way inertness probe on the one
  deleted statement, not by assertion.
- **Constraints not violated:** yes. `_identity_violation` untouched, no fenced file touched,
  `map/**` and `episodes/**` untouched.
- **Notes match the diff:** yes, with one correction — the notes' "`:194` … byte-identical"
  is over-broad, as measured above.
- **Decision candidates surfaced:** yes. `decision:bind-on-open-over-new-verb` and
  `decision:one-spine-per-process-stands` are now described correctly at
  `scripts/mcp_spine_server.py:30`; the handoff-conflict reading (0 live claims in `scripts/`
  vs `run_crew.py` being both in `scripts/` and fenced) was surfaced rather than silently
  resolved, which is correct.
- **Durable context routed:** yes, and I extended it — three triage candidates recorded on
  the survey (`tc1`, `tc2`, `tc3`).

## Reconciliation check

**The finding.** `docs/CHECKLIST_ENGINE_DESIGN.md:295-298` now reads:

> The server binds `SPINE_FILE`, `SPINE_ENGINE` and `SPINE_SESSION` from its environment when
> it launches, and — since issue #603 — again when a successful `spine_open` binds the process
> to the spine it just minted (`_bind_process_to`, …).

`_bind_process_to`'s entire body (`mcp_spine_server.py:913-917`) is:

```python
global SPINE, SESSION
SPINE = Path(spine_file).resolve()
SESSION = session
os.environ["SPINE_FILE"] = str(SPINE)
os.environ["SPINE_SESSION"] = session
```

Two clauses do not describe that:

1. **`SPINE_ENGINE` is not among what is bound "again."** `ENGINE` is derived once at module
   scope by `_engine_from_env()`; `_bind_process_to` never touches it or the `SPINE_ENGINE`
   variable. The sentence enumerates three where the second moment binds two.
2. **"from its environment … and again when `spine_open`" has the direction backwards** for
   the second moment. Those two values come from `open_work`'s **return value** (`:1041`
   passes `opened['SPINE_FILE']`, `opened['SPINE_SESSION']`) and are **written into** the
   environment, not read from it.

The load-bearing half of the paragraph is accurate and I verified it: there really are two
binding moments, `_bind_process_to` really is the second, neither is a tool argument, and
`_rebind_refusal` really does block the swap while a lease is held.

**Why this is not a fourth BLOCK.** It is the same defect class as blocker 2 — prose that does
not describe the code that runs — at materially lower severity: design-doc narrative rather
than a test-failure message a future debugger would act on, and a two-word class of fix.
Everything #603 actually asked for is verified and green. Blocking a fourth time on this,
at the rework cap, would be disproportionate. So it is recorded as a `fail` on `r5` and
carried past consolidation by an explicit `--override-reason` — never downgraded to `pass` —
and filed as triage candidate `tc1` so it cannot be lost. There is a wry note here worth
recording: this doc paragraph was the implementer's own "finding 7," the one they said no
predicate caught and they found only by reading by hand. The correction to it introduced the
next imprecision. That is the shotgun-surgery smell producing its next instance in real time.

## Blockers

- none

## Out-of-scope observations

- **`tc2` — the Admiral float is one site short.** The Commander is reporting **two**
  cross-lane consequences (`scripts/run_crew.py:468-471`,
  `scripts/hooks/spine_rail.py:1081`). There is a **third**: `tests/test_spine_rail.py:2698`
  comments *"The MCP door … reads SPINE_FILE/SPINE_SESSION from its OWN environment
  (`scripts/mcp_spine_server.py: SPINE = Path(os.environ["SPINE_FILE"]).resolve()`)"* — the
  same quoted, now-deleted module-scope form, in the same lane's test file. **The float should
  name three sites, not two.** Nothing to fix here (same lane, correctly untouched), but the
  report to the Admiral is incomplete without it.
- **`tc1`** — the `docs/CHECKLIST_ENGINE_DESIGN.md` imprecision above.
- **`tc3` — dead scaffolding left behind.** `tests/test_mcp_lifecycle.py:335` and `:343-346`
  capture and restore `saved_spine_file`, but `5a626351` deleted the only statement in the
  `try` block that wrote `os.environ["SPINE_FILE"]`. Harmless, and arguably defensible as a
  guard should `_spine_open` ever reach `_bind_process_to` from this test — but it is the
  residue of the deleted line, and "the comment **and** the inert write deleted together" did
  not account for it.
- **Shotgun surgery** — flagged in the Fowler pass, already a triage candidate, concur it is
  beyond this gate.

## Workflow Feedback

- **Handoff gaps:** The four stacked addenda are readable but the "do not redo" lists drifted
  from the tree. REWORK-3's settled list still asserts "`:194` and its control byte-identical"
  — true of the control, false of the pin since `176133ac`, which is *the addendum's own
  blocker-2 fix*. A settled-list entry that the very rework it introduces invalidates is a
  small instance of the same shotgun-surgery smell this gate is about. Suggest settled lists
  be pinned to the revision they were measured at, per `global-everyone.md`'s "pin a claim to
  the revision you read it at."
- **Context rediscovered:** Which spine to drive. `SPINE_FILE`/`SPINE_SESSION` in my
  environment name the **Commander's `execute` spine**, not a review survey, so the skill's
  "a dispatched crew's spine is bound for you — do not author a survey of your own" reads as
  an instruction to drive my parent's gated spine, which would have been destructive. I
  authored my own survey at `.agent-work/cleanup-a-door/g3-final2-review/review.json`, the
  convention the three prior reviewers used. The handoff has no "Survey State Location" field
  even though the skill names one.
- **Instructions improvised around:** `spine_survey_result` is survey-only and my bound spine
  is `gated`, so I drove the survey through the `checklist_engine.py` CLI instead of the MCP
  door. Also: the reviewer survey's `r6-fowler` postcondition resolves a **fixed** path,
  `.agent-work/<work-id>/FOWLER_PASS.json`, so each successive review attempt on one gate
  **overwrites its predecessor's** Fowler record. Three prior passes on this gate are now
  recoverable only from git history. A per-attempt path would preserve them.
- **What would have made this easier:** Two small things. (1) `checklist_engine.py` takes
  `--session-id` **after** the verb, not as a global flag; my first three calls were refused
  for putting it before. (2) `advance` refuses on a survey with "use `record`" — correct, but
  the reviewer skill's own text says "integrate it, `advance` that check," which sends you
  straight into that refusal. Wording the skill as "`record` each item, then `consolidate`"
  would remove it.

## Return status

`complete`
