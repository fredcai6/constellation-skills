# Reviewer Handoff

> Write per `constellation-how-to-talk` — clear, concise, grounded, one name per thing.

## Gate
`g3` — issue #603, the door cannot be bound by the session that needs it, and answers about
a demo spine when unbound. **The run's hardest gate, and the one where a weakened guard
would matter most.**

## Task statement (what was asked)

**(A) Fail closed.** Make unset, empty, non-existent, non-file and unreadable `SPINE_FILE`
one "unbound" class, and make every tool return a refusal — never a demo answer, never a
crash, never silence. Make `SPINE_ENGINE` fail closed in the same motion.

**(B) Bind on open.** Let a successful `spine_open` bind this process to the spine it just
minted, so a session that starts unbound can mint work and drive it.

**The exit criterion:** a session started with **no** `SPINE_FILE` calls `spine_open`, gets
bound, and drives a real spine end to end **without touching the CLI**.

## What was implemented

Commit `4e1f22cb`. Nine files:

| File | What |
|---|---|
| `scripts/mcp_spine_server.py` | fail-closed predicate; one named binder; lease-held rebind refusal; four import-time `SPINE` derivations made late-bound; `_primary_checkout_for_lifecycle` no longer reads `os.environ` |
| `.mcp.json` | demo default dropped → `"${SPINE_FILE:-}"` |
| `tests/test_mcp_door_unbound.py` | **new**, 12 tests |
| `tests/test_mcp_lifecycle.py` | **added** the module-wide assignment pin + mutated control, and 5 `IdentityGuardSurvivesARebindTests` |
| `tests/test_mcp_identity.py` | two controls updated: crash → refusal |
| `tests/test_mcp_door_engine_cwd.py` | removed-spine-directory test now asserts a refusal |
| `tests/test_mcp_spine_server.py` | `:588` reconciled to its replacement invariant, plus a positive control |
| `examples/mcp-interactive-demo/README.md` | opening paragraph corrected |
| `map/INDEX.md`, `map/` | rebuilt |

Full `IMPLEMENTER_RESULT`: `.agent-work/cleanup-a-door/crew-handoffs/g3-implementer-result.md`.
Evidence: `.agent-work/cleanup-a-door/evidence/g3-*.txt`.

## How to inspect the diff

```bash
cd /home/tommy/projects/constellation-skills/.worktrees/cleanup-a-door
git show 4e1f22cb --stat
git diff a69bbac4..HEAD -- scripts/mcp_spine_server.py .mcp.json
git diff a69bbac4..HEAD -- tests/
```

## Close criteria — verify each independently

1. **All five unbound-class inputs refuse**, server alive: unset, **empty `""`**, missing
   path, a directory, and unreadable (chmod 000). **Test empty FIRST** — `.mcp.json` is now
   `${SPINE_FILE:-}`, which expands to empty, not unset, so empty is what production takes.
   Enumerate the tools you called and **state the count**.
2. **An unbound refusal does not fabricate a path**; a missing/unreadable one names it.
3. **The exit criterion, end to end, in one process:** unbound refuses → `spine_open` binds
   → **`claim` succeeds**. `claim` is the load-bearing step: `run_engine` omits
   `--session-id` when `SESSION` is empty and `checklist_engine.py:1073` raises
   `claim requires a non-empty --session-id`, so **a transcript that stops at
   `spine_status` does not demonstrate binding.** Paste the transcript.
   **Clean up any worktree your probe creates** (`git worktree remove --force …` and delete
   the branch) — mine created and removed `verify-exit-criterion`.
4. **`_identity_violation` still refuses an argv naming a different spine AFTER a rebind.**
   Its semantics are **fenced** by the launch order. Test it; do not assume it. **Any
   weakening is a `BLOCK`.**
5. **All four import-time `SPINE` derivations follow the rebind.** Name and check each
   individually: `CALLLOG` (`:162`), `START_MARKER` (`:167`), `REJECTIONLOG` (`:177`), and
   `_resolve_confined`'s `bound_dir` **default argument** (`:188`). State which you
   verified. A stale one writes one spine's telemetry into another's directory.
6. **The three env overrides still work** — `SPINE_CALLLOG`, `SPINE_START_MARKER`,
   `SPINE_REJECTION_LOG` (`tests/test_mcp_lifecycle.py:102-103` relies on them).
7. **`tests/test_mcp_lifecycle.py:194` and its positive control are BYTE-IDENTICAL** to
   `a69bbac4`. Diff them. Then confirm the **new** module-wide assignment pin exists and its
   own **mutated positive control genuinely fails**.
8. **A rebind while a lease is held is refused.**
9. **The new regression test genuinely fails pre-fix.** Check it out and run it.
10. **Unset `SPINE_ENGINE` no longer kills the server at import.**
11. **`README.md`'s opening sentence** no longer claims `.mcp.json` points at the demo.
12. **`test_mcp_spine_server.py:588`'s replacement invariant is honest** — it should still
    catch a *present* default that does not resolve to a loadable spine. Confirm it can
    still fail; a guard reconciled into vacuity is the failure mode here.
13. **Full clean-env suite green.**

## Allowed scope

Review only. Report findings; do not fix.

## Specific exclusions

- `scripts/checklist_engine.py`, `scripts/hooks/**`, `scripts/run_crew.py`,
  `scripts/gauge_reader.py` — **lanes B and C, running concurrently.** Read; never modify.
- `scripts/install_constellation.py` / `COMMANDER_SPINE.template.json` **doctrine** — the
  launch order's "door-detection change" is undefined and floated to the Admiral. Its
  absence is deliberate, not an omission; do not block for it.
- `examples/mcp-interactive-demo/spine.json` and `make_demo_spine.py` — g2's, closed.
- `map/ids.jsonl` being empty — a known triage candidate, not this gate's.

## Constraints

- **Clear `__pycache__` before every measurement** (#597).
- `env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q`
- Validate against a **subprocess** you launch. `.agent-work/cleanup-a-door/door_probe.py`
  supports `--unbound` (genuinely removes the variable) and `""` (empty) — they are
  different cases and both matter.

## Map anchors (inbound)

Inherited from `g3-implement`. **Map entry point: none** — `map/ids.jsonl` is empty.

- **Structural:** `mcp_spine_server.py:145-147`, `:162/:167/:177`, `:188`, `:236-363`
  (`_identity_violation` — **FENCED**), `:593`, `:622-736`; `spine_lifecycle.py:334-340`;
  `checklist_engine.py:1073` (read only); `.mcp.json`;
  `tests/test_mcp_lifecycle.py:137,194`; `tests/test_mcp_spine_server.py:574,588`.
- **Capability:** door identity acquisition; door refusal surface when unbound.
- **Decision anchors:**
  - `decision:one-spine-per-process-stands` `@grade: settled/human · leans g3-implement,g3-review`
  - `decision:fail-closed-beats-fail-open` `@grade: settled/measured · leans g3-implement`
  - `decision:bind-on-open-over-new-verb` `@grade: guess · leans g3-implement · settle: attempt the spine_open binding first and report what it costs`
- **Evidence:** `claim:603-fails-open`.

## Evidence already produced (reproduce, do not trust)

Commander's own re-verification, all independently run at `4e1f22cb`:

- Unbound **and** empty both return
  `REFUSED: no spine is bound to this door… Call spine_open…`, `isError: true`, **EXIT 0**.
- **Exit criterion reproduced in one process:** unbound refused → `spine_open` returned
  `SPINE_FILE` + `SPINE_SESSION` → `spine_lease claim` **succeeded**
  (`claimed lease constellation/verify-exit-criterion -> active`) → `spine_status` showed
  the new spine. Throwaway worktree removed.
- `git diff a69bbac4..HEAD -- tests/test_mcp_lifecycle.py | grep "^-"` → **zero removed
  lines**, so `:194` is pure-addition intact.
- `IdentityGuardSurvivesARebindTests` → **5 passed**.
- `tests/test_mcp_door_unbound.py` against a reverted server → **12 failed**.

**Your job is not to repeat my list — it is to find what neither of us checked.** Attack
hardest: criterion 5 (is there a *fifth* stale derivation, or a path where `CALLLOG` is
`None` and g1's `OSError`-scoped guard does not catch it?); criterion 12 (is the reconciled
`:588` still able to fail, or was it reconciled into vacuity?); and whether the binder is
reachable by any route **other** than a successful `spine_open` — a second, quieter rebind
site is exactly what the new pin exists to prevent, so try to find one it misses.

## Verification commands

```bash
cd /home/tommy/projects/constellation-skills/.worktrees/cleanup-a-door
find . -name __pycache__ -type d -not -path "./.git/*" -exec rm -rf {} +
py .agent-work/cleanup-a-door/door_probe.py --unbound
py .agent-work/cleanup-a-door/door_probe.py ""
git diff a69bbac4..HEAD -- tests/test_mcp_lifecycle.py | grep -E "^-" | grep -v "^---"
env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q
```

## Suggested model tier

`stronger` — a change to how a long-lived server acquires identity, with a fenced guard that
had to stay intact while being made reachable.

## Stop conditions

Stop and return if: the diff exceeds the nine files named; a fenced file was touched;
`_identity_violation`'s semantics changed (that is a `BLOCK` **and** an Admiral float);
required evidence cannot be produced.

## Return format

Return `REVIEW_RESULT` with a verdict of **`APPROVE`** or **`BLOCK`**, findings (each with
evidence you reproduced yourself), what you checked and found sound, and what you did NOT
check as an explicit scoped null. Include a `Workflow Feedback` section.

**Delivery.** Write the full `REVIEW_RESULT` to
`.agent-work/cleanup-a-door/crew-handoffs/g3-reviewer-result.md` **before ending your
turn** — that write is the delivery.

---

# REWORK ADDENDUM — attempt 2 (read this last; it overrides delivery and scope above)

Your predecessor reviewed `4e1f22cb` and returned **`BLOCK`** with two blockers. Both are
now fixed in `359d93df`. **Its functional findings were all APPROVE-grade and reproduced —
you are re-reviewing a rework, not starting over.**

**Reviewed and reproduced already (do not redo unless you doubt it):** the six unbound-class
refusals; bind-on-open through to a successful `claim`; the regression suite red pre-fix;
`:194` byte-identical plus the new module-wide pin and its mutated control;
`IdentityGuardSurvivesARebindTests`; the env overrides; the lease-held rebind refusal.

**What changed since, and what you must verify:**

1. **The suite is green.** `359d93df` rebuilt `map/INDEX.md` after staging. Confirm:
   `env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q` — the Commander
   measured **3093 passed, 6 skipped, 1153 subtests, 0 failed**. Reproduce it.
2. **`map/` is fresh against the STAGED tree.** The trap that caused blocker 1 is that
   `code_map` enumerates via `git ls-files`, so a rebuild run while a new file is untracked
   passes its own guard. Confirm freshness holds now with everything committed.
3. **The three doc references** (`mcp_spine_server.py:685`, `:962-963`,
   `examples/mcp-interactive-demo/README.md:69`) now name what the code actually does.
4. **Run your own blast-radius sweep** for every identifier `4e1f22cb` renamed or deleted and
   **state the count** — your predecessor found three; confirm there is no fourth.
5. **Confirm the rework changed no behaviour.** `git diff 4e1f22cb..359d93df` should be docs
   plus generated `map/` pages only. Any behaviour change is a `BLOCK`.

**Do not act on the two triage candidates your predecessor refuted by measurement** (the
`SPINE_ENGINE` sibling-fallback claims); they do not reproduce.

**Delivery for THIS attempt:** write your `REVIEW_RESULT` to
`.agent-work/cleanup-a-door/crew-handoffs/g3-rereview-result.md` — **note the new
filename**, so your predecessor's BLOCK is preserved beside it rather than overwritten.

---

# REWORK-2 ADDENDUM — attempt 3 (read this LAST; it overrides everything above)

Two prior reviews returned `BLOCK`. **Both blockers are now fixed.** Their functional
findings were APPROVE-grade and fully reproduced — the substance of #603 is settled.

**Already reviewed and reproduced twice — do not redo:** the six unbound-class refusals;
bind-on-open through to a successful `claim`; the regression suite red pre-fix;
`tests/test_mcp_lifecycle.py:194` and its control byte-identical; the new module-wide
assignment pin plus its mutated control; `IdentityGuardSurvivesARebindTests`; the three env
overrides; the lease-held rebind refusal; unset `SPINE_ENGINE`; `map/` freshness.

**Blocker history:**
1. *(rework 1, `359d93df`)* full suite red — `map/INDEX.md` rebuilt before the new test file
   was staged. **Fixed and verified green.**
2. *(rework 2, `176133ac`)* `tests/test_mcp_lifecycle.py:201`'s pin **failure-message**
   claimed `_spine_open` re-reads `SPINE_FILE` fresh — false, since removing that read *is*
   the #603 fix. **Fixed.**

**Verify only these five things:**

1. **`git diff 359d93df..176133ac` touches exactly ONE file**, `tests/test_mcp_lifecycle.py`,
   and changes **only** the failure-message string — no assertion, no test logic, no
   behaviour. Anything else is a `BLOCK`.
2. **The corrected message names what `_spine_open` actually reads.** Check it against the
   AST, not against the prose: `SPINE_PARENT` re-read from the environment, and the repo root
   from `_primary_checkout_for_lifecycle` (which reads no environment). Confirm `SPINE_FILE`
   is read **zero** times in `_spine_open`.
3. **`:194` and its positive control are still byte-identical** to `a69bbac4`, and the
   module-wide pin's mutated control still fails.
4. **Run a whitespace-normalized or AST-aware sweep** — *not* a line-based `grep` — for any
   remaining invalidated claim in scope, and **state the command and the count**. This is the
   method hole that produced blocker 2: the phrase was assembled from two adjacent string
   literals, so `git grep -F 're-read fresh'` returned 0 files tree-wide while a normalized
   sweep returned 1. The Commander's own normalized sweep now returns **0**.
5. **Full clean-env suite green.** Commander measured **3093 passed, 6 skipped, 1153
   subtests, 0 failed** at `176133ac`. Reproduce it.

**Out of scope — do not block for these:** `scripts/hooks/spine_rail.py`'s invalidated claim
(**fenced**, lanes B/C; already being reported to the Admiral as a cross-lane consequence of
this change); the two episode clauses; the refuted `SPINE_ENGINE` sibling-fallback
candidates; `map/ids.jsonl` being empty; the undefined "door-detection change".

**Delivery for THIS attempt:** write your `REVIEW_RESULT` to
`.agent-work/cleanup-a-door/crew-handoffs/g3-final-review-result.md` — **note the new
filename**, so both prior BLOCKs are preserved beside it.

---

# REWORK-3 ADDENDUM — attempt 4, FINAL (read this LAST; overrides everything above)

Three prior reviews returned `BLOCK`. All blockers are fixed. **This is the last rework
within the cap — a further BLOCK escalates to the Admiral, so judge on what is actually
left, not on what could conceivably be tightened.**

**Settled by three reviews; do not redo:** the six unbound-class refusals; bind-on-open
through to a successful `claim`; the regression suite red pre-fix; `:194` and its control
byte-identical; the module-wide assignment pin and its mutated control;
`IdentityGuardSurvivesARebindTests`; the env overrides; the lease-held rebind refusal; unset
`SPINE_ENGINE`; `map/` freshness; the full suite.

**Blocker history:** (1) suite red, map rebuilt before staging — fixed. (2) the pin's
failure message claimed a read that #603 removed — fixed. (3) four further invalidated
claims, missed because the sweep was scoped to *edit permission* rather than *blast radius*
— fixed at `5a626351`.

**Verify only these, at `5a626351`:**

1. **The four claims are corrected and now describe the code that runs:**
   `scripts/mcp_spine_server.py:30` and `:129-131`; `tests/test_mcp_lifecycle.py:335-341`
   (comment **and** the inert `os.environ` write deleted together);
   `tests/test_mcp_adoption.py:98-102`; plus `tests/test_mcp_identity.py:547`'s quoted
   sentence. Check each against the **AST**, not against neighbouring prose.
2. **`docs/CHECKLIST_ENGINE_DESIGN.md` was also corrected.** It is outside the handoff's
   enumerated file list but inside the blast radius; the Commander accepted it as justified.
   Confirm the new text is accurate — that is the only question about it.
3. **No behaviour changed.** `git diff 176133ac..5a626351` must be docstrings, comments, and
   one deleted test-setup line. Anything else is a `BLOCK`.
4. **Your own AST-aware, identifier-driven sweep** (not line-based, not keyword-guessed) over
   `scripts/`, `tests/`, `examples/`, `docs/`. **State the command and the count.** Expect
   **0 live in-scope** invalidated claims. Read every hit yourself rather than trusting a
   classifier — text that *quotes* the old phrasing in order to mark that it changed is
   correct, not stale, and there are three such.
5. **Full clean-env suite green.** Commander measured **3093 passed, 6 skipped, 1153
   subtests, 0 failed** at `5a626351`.

**Known and deliberately NOT fixed — do not block for these:**

- **`scripts/run_crew.py:468-471`** still says `mcp_spine_server` *"raises KeyError if either
  is unset"*, which this change falsified. **`run_crew.py` is FENCED to lanes B/C**, so the
  implementer reported it and correctly did not touch it. Together with
  `scripts/hooks/spine_rail.py`'s equivalent claim, these are **two cross-lane consequences
  already being reported to the Admiral.**
- The reviewer-identified shotgun surgery (one fact restated in ~seven places). Real, and
  filed as a triage candidate; consolidating it is a design change beyond this gate.
- `map/ids.jsonl` empty; the undefined "door-detection change"; `episodes/` and `map/` prose.

**Delivery:** write your `REVIEW_RESULT` to
`.agent-work/cleanup-a-door/crew-handoffs/g3-final2-review-result.md`.
