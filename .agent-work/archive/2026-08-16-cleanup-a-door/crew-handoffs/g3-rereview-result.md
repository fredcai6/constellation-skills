# Review Result

## Assigned Gate
`g3` — issue #603, the door cannot be bound by the session that needs it. **Re-review, attempt 2**,
of the rework commit `359d93df` on top of `4e1f22cb`.

## Result
`BLOCK`

One blocker. It is a one-line fix to a **test failure message** — no behaviour, no test logic, no
map rebuild. Both of my predecessor's blockers are genuinely closed and I reproduced each one
myself. The gate's actual subject matter — fail-closed, bind-on-open, the fenced guard — is sound,
and I could not break it either.

I blocked on the **method**, not the typo. The rework's own blast-radius sweep reported *"AFTER: 0
stranded references in scope"*. That claim does not reproduce: I measure **1**, and it is invisible
to the sweep's own command by construction.

Survey driven through the engine at
`.agent-work/cleanup-a-door/g3-rereview-review/review.json` (session
`constellation/cleanup-a-door/g3-rereview/reviewer/attempt-1`): 7 items, 6 pass, 1 fail,
consolidated `BLOCK`. My probes are at `.agent-work/cleanup-a-door/g3-rereview-review/*.py`.

---

## Handoff compliance

All five REWORK ADDENDUM items were verified independently. I did not re-litigate `4e1f22cb`'s
substance beyond the spot-checks noted, per the addendum.

**Item 1 — the suite is green. Reproduced exactly.**

```
find . -name __pycache__ -type d -not -path "./.git/*" -exec rm -rf {} +
env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q
3093 passed, 6 skipped, 1153 subtests passed in 127.44s     EXIT=0
```

Identical to the claimed count. I confirmed it measured the **committed** tree: `git status` shows
no tracked modification outside `.agent-work/`, so nothing of mine contaminated it.

**Item 2 — `map/` is fresh against the staged tree, and the guard can still fail.** A fresh
`py -m scripts.code_map build --root .` produces a **zero-byte diff** — which a hand-edited index
would not. Freshness alone proves little, so I mutated `map/INDEX.md`'s entity count
(`4743` → `4742`), asserted the mutation applied, and watched
`MapTreeFreshnessTests::test_map_tree_freshness_root_index_matches_a_fresh_build` go **red**, then
restored byte-identically (`git status` clean). The trap's precondition is also gone: there is no
untracked `.py` outside `.agent-work/`, and I confirmed at source that
`scripts/code_map/discovery.py:16` excludes `.agent-work/` from the mappable corpus, so my own five
probe scripts cannot fire it a third time.

**Item 3 — the three doc references now name the mechanism that runs.** Checked as *claims about
code*, by AST, never by grep — `CREW_CONTEXT.md`: *assert against behaviour, never against text that
describes it*. All 11 checks pass:

- `_rejectionlog()` exists, `_log_rejection` actually calls it, and `REJECTIONLOG` is gone as an
  identifier;
- `_primary_checkout_for_lifecycle` contains **zero** `os.environ`/`getenv` reads and does fall back
  to `__file__`;
- the cited test `test_mcp_json_spine_file_is_overridable_and_any_default_loads` genuinely exists,
  and the deleted name appears nowhere in the README;
- the tense fix is correct on the merits — `.mcp.json` really is `"${SPINE_FILE:-}"`, so *"points
  at"* was false and *"pointed at"* is true. The implementer declared this one-word departure; it is
  the same defect class in the same sentence, and it should stand.

**Item 4 — my own blast-radius sweep. See *Blockers*; this is where the finding is.**

**Item 5 — the rework changed no behaviour. Proven, not eyeballed.** The only `.py` file it touches
is **AST-identical** to `4e1f22cb` once docstrings are stripped. The probe asserts the two sources
genuinely differ before stripping, so it cannot pass by comparing a file to itself. All 8 changed
lines sit inside docstrings.

**Spot-checks of the gate's core, because the rework edited a docstring inside the function the
identifier ban polices.** The ban at `tests/test_mcp_lifecycle.py:194` is **AST-scoped** —
`_referenced_names(fn, BANNED_IDENTIFIERS)` over `ast.Name` nodes — so a docstring mentioning
`SPINE_FILE` cannot trip it. I confirmed that by reading the pin, not by trusting the claim. Against
subprocess doors I launched: both `--unbound` and empty `""` return
`REFUSED: no spine is bound to this door…`, `isError: true`, **EXIT 0**, empty stderr, no fabricated
path.

**Stop conditions:** none fired.

## Scope drift

None. Both g3 commits together (`408e6d26..HEAD`) touch **exactly nine files** — the nine the
handoff named, with `map/` represented by its only committable artifact. The rework itself is three.

Zero fenced or excluded paths appear in the g3 range: `checklist_engine.py`, `scripts/hooks/**`,
`run_crew.py`, `gauge_reader.py`, `install_constellation.py`, `COMMANDER_SPINE.template.json`.
(`make_demo_spine.py` and `examples/mcp-interactive-demo/spine.json` appear in the wider
`a69bbac4..HEAD` range but belong to g2, which is closed and excluded.)

**One handoff instruction was impossible, and the implementer was right to say so.** The rework
handoff asked for the two `map/scripts.mcp_spine_server/` pages to be committed. I verified at
source: `.gitignore:73` is `map/*` with only `!map/INDEX.md` and `!map/ids.jsonl` un-ignored, and
`git check-ignore` exits 0 on those pages. They cannot appear in any commit. They are correct on
disk — the generated `_log_rejection.md` picked up the new docstring.

## Evidence verdict

**Two of three claims reproduce exactly. The third does not, and that is the blocker.**

| claim | verdict |
|---|---|
| full clean-env suite `3093 / 6 skipped / 1153 subtests` | **reproduced exactly** |
| diffstat `3 files, 13+/9-`, `map/INDEX.md` at 3+/2- | **reproduced** |
| blast-radius sweep, *"AFTER: 0 stranded references in scope"* | **does not reproduce — I measure 1** |

The three rework evidence files exist and are fresh (`08:03`–`08:06`, against a commit at
`08:05:58`).

**A note on ordering, since it caused blocker 1 last time.** `g3-rework-full-suite.txt` is stamped
`08:03`, again *before* the `08:05:58` commit. It was harmless here only because the rework changed
no file's tracked status, which is the precondition the trap needs. My own suite run is the one that
actually closes item 1: it is post-commit, on the committed tree.

## Code/doc quality

The rework is clean. No write site is touched at all, so the `utf-8`/`newline` rule has no new
surface; `git diff --check` finds no trailing whitespace; there is no lint config to violate and the
README lines sit at ~100 columns, matching the paragraph around them. The prose is a genuine
improvement — each replacement names the mechanism that actually runs.

**Fowler pass:** `.agent-work/cleanup-a-door/FOWLER_PASS.json`, `verify_fowler_pass.py` **exit 0** —
12 smells visited, **flagged** `feature-envy` + `comments-as-deodorant`, **overridden**
`duplicated-code`, `data-clumps`, `primitive-obsession`, `divergent-change`,
`speculative-generality`, each with its standard and reason logged. I proved the rail can refuse
rather than assuming it: dropping a smell gives `REFUSED: visit-every-item`, blanking an override
reason gives `REFUSED: OVERRIDE-LOG`; record restored byte-identically.

Two verdicts moved rather than restating my predecessor. **`shotgun-surgery` is absent because this
gate cured it** — four import-time derivations collapsed into one `_telemetry_path`, and an AST scan
finds zero function defaults referencing `SPINE`/`SESSION`/`ENGINE` at HEAD. The **`data-clumps`
override** is the one worth reading: the obvious `Identity` value object is exactly the refactoring
that would blind the module-wide AST pin guarding this gate's core invariant, because the pin can
only enumerate assignments to two named globals.

**One trivial style nit, not worth a rework on its own:** `_start_marker` and `_rejectionlog`
(`:238`, `:245`) are separated by one blank line where the rest of the module uses two. No linter
enforces it here. Fold it in if you touch the file for the blocker.

## Map impact verdict

- **Evidence supports claimed change:** Yes. *"No symbol added, removed, renamed or re-signatured"*
  is proven rather than accepted — AST identity after docstring-stripping makes a symbol move
  impossible. The *"behaviour: no"* claim rests on the same proof.
- **Constraints not violated:** Confirmed. The fenced `_identity_violation` is untouched by the
  rework, and the AST-scoped ban it lives under cannot be weakened by a docstring edit.
- **Notes match the diff:** Yes. Three files, two docstrings, one README paragraph, one regenerated
  index — exactly what the diff contains.
- **Decision candidates surfaced:** Yes. The three decision anchors are untouched by this commit, as
  claimed. The implementer's assumption about the untracked map pages is correct and I verified it.
- **Durable context routed:** Yes, and their `tc1` is right. I add one they missed — see below.

Not a BLOCK on map grounds.

## Reconciliation check

The gate introduces no divergence Commander must reconcile inside its own scope. Two divergences sit
outside it, recorded as `tc1`/`tc2` in the survey.

## Blockers

1. **`tests/test_mcp_lifecycle.py:201` — the fourth stranded claim, in scope, and the same class the
   rework existed to eliminate.**

   The pin's failure message still tells a future debugger:

   ```
   "purely on ambient, server-launch-time state (SPINE_FILE/SPINE_PARENT re-read "
   "fresh) and never on the identity THIS door happens to be bound to, ..."
   ```

   Measured against the AST at HEAD, `_spine_open` reads `SPINE_PARENT` from `os.environ` **once**
   (still true) and `SPINE_FILE` **zero times** — because removing that read *is* the #603 fix. This
   is the same invalidated claim, in the same words, that the rework fixed at
   `mcp_spine_server.py:962-963`.

   **Why it survived, and why this is the real finding.** The sweep ran
   `git grep -n 're-read fresh'` and got nothing. The message is assembled from two adjacent string
   literals split as `"…re-read "` + `"fresh)…"`, so the phrase appears on **no single line**. My
   control makes this exact:

   ```
   git grep -F 're-read fresh'   ->  0 files, tree-wide
   whitespace-normalized sweep   ->  1 file  (tests/test_mcp_lifecycle.py)
   ```

   This is `CREW_CONTEXT.md`'s own warned hazard — *"a grep for a message string is not a test of the
   branch that emits it"* — firing against the sweep that was supposed to enforce the blast-radius
   rule. The instance is one line; the hole in the method is what will recur.

   **Fix:** correct the parenthetical to name what `_spine_open` actually reads (`SPINE_PARENT` re-read
   fresh; the repo root from `_primary_checkout_for_lifecycle`, which reads no environment). The
   surrounding claim — that `spine_open` must never touch the bound identity — is still exactly
   right and should not change. No behaviour, no test logic, no map rebuild.

   **Sweep counts, stated as asked.** From the commit itself: **7** identifiers removed, **5**
   re-bound elsewhere (moved, not stranded), **2** genuinely gone; **0** live stranded *identifier*
   references at HEAD — my predecessor's three are all genuinely fixed. Widening to *invalidated
   claims*, which is what the doctrine actually requires, there are **4** live: this one (in scope,
   the blocker), `scripts/hooks/spine_rail.py` (fenced, `tc2`), and two clauses in one active
   episode (`tc1`).

## Out-of-scope observations

1. **`tc1` — an active episode assertion that #603 falsified, which nobody has recorded.**
   `episodes/active/epic-559_c2-generate-the-spine-006.md` assertion `a3` (`observed-behavior`,
   `strong`, `lifecycle-standing: active`) states *"The door binds exactly one file at import time —
   `SPINE = Path(os.environ['SPINE_FILE']).resolve()`"*. Bind-on-open makes the import-time-only half
   false and that expression is deleted. Per `docs/EPISODE_STORE.md`, `lifecycle-standing` answers
   *"is this specific claim still believed?"* — so this is a **live belief, not a dated record**, and
   the governed op is `amend-assertion` → `superseded` via `scripts/apply_episode_delta.py`, never a
   hand edit.
   **Attribution, carefully:** only the binding clause is #603 drift. The same assertion also says
   the door has *nine* tools, and that was already wrong at the gate base — I counted **11** tool
   declarations at `a69bbac4`, `4e1f22cb` and HEAD alike.

2. **`tc2` — `scripts/hooks/spine_rail.py:1081`, and the substantive half matters more than the
   stale quote.** `_handle_door_lease` quotes the deleted expression as the door's *"existing
   contract"*, but the real problem is its **inference**: it resolves the claimed spine from the hook
   process's own `SPINE_FILE`. After bind-on-open, `_bind_process_to` rewrites `SPINE_FILE` inside
   the **door** process only; a hook process spawned by the harness keeps its launch-time value, so
   after a rebind the hook can record a lease binding against the **wrong spine**. This feeds
   `decision:door-binding-source-of-truth`. Fenced to lanes B/C and correctly left untouched — route
   it as correctness, not tidiness. The implementer flagged this themselves and was right to.

3. **Pre-existing, explicitly not this gate's:** `episodes/` carries all eight `epic-559 c2` episodes
   **twice** — under `active/` with underscore ids and under `retired/` with hyphen ids, bodies
   differing. No `episodes/` file appears anywhere in `a69bbac4..HEAD`, so this predates the run
   entirely. Noted only because I tripped over it while sweeping.

4. **The map-rebuild-before-commit ordering recurred** in the rework (suite at `08:03`, commit at
   `08:05:58`) and was harmless only by luck of no tracked-status change. My predecessor's
   recommendation stands: make "rebuild the map last, after staging" a hook or doctrine rather than a
   remembered step.

## What I did NOT check — explicit scoped nulls

- **`4e1f22cb`'s behavioural surface, beyond spot-checks.** Per the addendum I did not re-run the
  six-input unbound sweep, the end-to-end bind-on-open-through-`claim` transcript, the lease-held
  rebind refusal, the env overrides, or the pre-fix red run. My basis for carrying my predecessor's
  results forward is not trust — it is the AST proof that the rework changed no behaviour, which
  makes those measurements still-valid at HEAD. I did independently re-run the unbound and empty
  refusals and re-read the identifier ban.
- **Windows, and running as root.** Every measurement is Linux, uid 1000, Python 3.12.3.
- **Concurrency.** No two doors against one spine, no rebind racing another session's lease claim.
- **`map/ids.jsonl` being empty** — excluded by the handoff; not investigated.
- **The floated `install_constellation.py` door-detection doctrine** — excluded; not examined.
- **g2's demo spine and `make_demo_spine.py`** — closed; not re-reviewed.
- **Whether `tc2` is exploitable in practice.** I established the mechanism by reading both sides;
  I did not build a live harness+door rebind to observe a mis-recorded binding.

## Workflow Feedback

- **Handoff gaps:** The addendum's item 4 asks me to *"confirm there is no fourth"* — phrasing that
  presumes the answer. There is a fourth; the implementer's own result already said so (their `tc1`,
  in a fenced file) **before** this handoff was written, so the addendum contradicted a document it
  was built on. A neutral *"state your count and disposition"* would not have primed for a
  confirmation. Separately, the addendum told me to treat the implementer's sweep as settled while
  also asking me to redo it — those pull opposite ways, and redoing it is what found the blocker.
- **Context rediscovered:** That the rework's evidence for a *"0 stranded references"* claim was
  produced by a **line-oriented grep**. The claim is stated as a count in the result; the command
  behind it is in an evidence file. A count and the command that produced it should sit together,
  because the count is only as good as the command's blind spots — here, adjacent string literals.
- **Instructions improvised around:** Three.
  (a) `run_crew.py` again dispatched me with the **Commander's** spine bound (`SPINE_FILE` →
  `execute/commander`, active gate = the Commander's own `execute` imperative). The reviewer skill
  says a dispatched crew must not author its own survey when a spine is bound; that branch does not
  cover *"a spine is bound, but it is your parent's."* I followed the g1/g2/g3 precedent, built my
  own survey under the issue workbench, drove it through the CLI, and ran no mutating verb against
  the Commander's `spine.json`. **This is now the fourth crew in this run to report the same
  conflict** — g3's implementer, g3's reviewer, g3's rework implementer, and me. It is a confirmed
  structural gap, not a rhyme.
  (b) `REVIEW_SURVEY.template.json`'s `r6-fowler` postcondition still resolves the Fowler record to
  the per-**work-id** path `.agent-work/<work-id>/FOWLER_PASS.json`, so writing mine would have
  destroyed the g3 attempt-1 record. I copied theirs to
  `.agent-work/cleanup-a-door/g3-review/FOWLER_PASS.json` first. My predecessor reported this exact
  defect and it reached me unfixed; the path should be `<work-id>/<gate>-review/FOWLER_PASS.json`.
  (c) The engine's `--finding` argument ate my first `r3-evidence` record: the text contained
  backticks, bash consumed them as command substitution, and the survey stored a finding with the
  contents of `FOWLER_PASS.json` spliced into it. I re-recorded through the engine with the backticks
  removed — never by hand-editing the JSON. **This repo already knows about this failure**: episode
  `epic-559_c2-generate-the-spine-006` assertion `a4` records the identical accident against `--why`,
  and cites it as an argument for the door's JSON-string tools over the CLI. It is still live for
  `--finding`.
- **What would have made this easier:** Have the handoff require that any *"N stranded references
  remain"* claim ship with **the command that produced it**, and prefer a whitespace-normalized
  sweep over a line-oriented `grep` for prose claims. The one blocker in this review is exactly the
  gap between those two methods, and it is invisible in the count alone.

## Return status
`complete`
