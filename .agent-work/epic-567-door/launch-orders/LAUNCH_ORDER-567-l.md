# Launch Order: `cmdr-567-l` — finish wave 3: three bounded changes the human ruled on

Epic **#567**, wave 3, finishing lane **L**. You are the only lane running. You start cold;
everything is pasted here.

**You are working on lane J's branch**, `feat/567-j-launcher-declared-defaults`, which already
carries J's delivered work and has `origin/main` (including lane K's merged bookends) merged into
it. Your pushes update **PR #637**. Do not open a new PR.

## Mission — three changes, all small, all already decided

### 1. Unblock J's merge gate — one assertion, one word

`tests/test_episode_observations.py::RealStoreTests` fails twice on this branch. Located exactly:

```
OFFENDER 567-j-004 a5 (workaround) imperative: 'run'
```

Lane J wrote six episodes at its `feedback` step, and `567-j-004`'s `workaround` assertion carries
a bare verb the observation guard reads as an instruction rather than a record.

**Rephrase it so the guard passes.** Use `apply_episode_delta.py`'s `restate-assertion` op — the
store has exactly one write path and hand-editing is forbidden. The op takes **exactly**
`op, id, assertion, statement, history` — no more, no less — and `assertion` is the bare id
(`a5`), not the qualified one. Put the reason in `history`.

**Do NOT add a twelfth entry to `guard.EXCEPTIONS`.** It already carries 11 across five runs, and
growing it is the decay path this epic has been recording all week.

### 2. The commander tier row — the human's ruling, verbatim

In `scripts/run_crew.py`'s `ROLE_MODEL_TIERS`, under harness `"claude"`:

```python
"commander": {"default": "sonnet", "allowed": frozenset({"sonnet", "opus"})},
```

His words: *"commander should be sonnet or opus allowed, haiku can't handle it."* So the change is
**upward only** — haiku out, opus in, default unchanged at sonnet.

**Everything else in the table stands exactly as J shipped it.** `admiral` stays
`{"default": "opus", "allowed": {"opus"}}` — he confirmed that directly. The `implementer`,
`reviewer`, `critic` and `cartographer` rows stay `{sonnet, haiku}`.

Update whatever test pins the table's contents.

### 3. Build the lint — and it is more load-bearing than it looks

Lane K staged this as its fifth triage candidate and did not build it: a **template lint for an
undeclared role spine**, the mitigation for form B's silent-permissive failure. The human approved
**"B plus lint"**, so this is the half that makes his choice safe.

**It is not hypothetical. The Admiral hit it minutes after merging K:**

```
repo   skills/commander/templates/COMMANDER_SPINE.template.json   "bookend": true  x2
installed ~/.claude/skills/constellation-commander/templates/...  x0
```

`init_work_area.py` mints spines from the **installed** copy, so **every spine created between K's
merge and a corpus reinstall is undeclared and silently unprotected** — including this lane's own.
The declarations do nothing until the corpus is reinstalled.

**So the lint should catch both:** a role spine template that declares no bookends at all, **and**
repo-versus-installed drift in those declarations, because the second is how the first happens in
practice. `check_skill_freshness.py` already exists for drift detection generally — reuse it rather
than reimplementing if it fits; say so if it does not.

**Scope it to role spine templates.** A plan with no declaration must keep reading as
not-a-bookend at runtime — K made that deliberate so existing plans are unaffected — so the lint
is a corpus check, not a runtime refusal. Do not change `_is_bookend()`'s permissive default.

## Pre-Rulings

- `decision:no-issue-filing-mid-run` — file nothing. Stage candidates under
  `.agent-work/567-l/triage-candidates/`. `@grade: settled/human`
- `decision:no-doctrine-promotion` — do not write into `docs/agents/*`. `@grade: settled/project`
- `decision:map-index-is-admiral-owned` — do not regenerate or hand-edit `map/INDEX.md` (#544).
  Your branch is accepted green **except** `MapTreeFreshnessTests`. `@grade: settled/doctrine`
- `decision:no-exception-list-growth` — the observation guard's exception list does not grow.
  Rephrase instead. `@grade: settled/human`
- `decision:pass-model-explicitly` — pass `--model sonnet` on any crew you dispatch. Given the size
  of this work, **consider whether it needs a crew at all** — three bounded edits with existing
  tests as the acceptance bar may be smaller than the machinery of dispatching.
  `@grade: settled/human`

## Honest-Null Clause

If any of the three turns out to be wrong or already done, say so with the evidence rather than
manufacturing a change. A measured negative is a complete deliverable.

## Inherited Context

- **Suite gate:** full suite in a **clean detached worktree of your branch**, with
  `env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT -u CREW_SCRATCH_DIR`. A crew's own
  `CREW_SCRATCH_DIR` otherwise reds `ScratchDirResumeTests`, a test your change does not touch.
- **`episodes/` order is write → `git add` → suite → commit.** `test_canon_episode_store_untouched`
  is worktree-vs-index only, so running the suite between the write and the stage trips it with a
  message that reads like store corruption.
- **GitHub returns intermittent 503s.** Retry, and gate each retry on whether the world actually
  changed rather than on the command's own output.
- **Your own spine is undeclared**, per the finding above. That is expected and is the thing you
  are building the lint for. Do not "fix" it by hand-editing your spine.

## Return Shape

Write to `.agent-work/epic-567-door/results/lane-l-RETURN.md`, committed on this branch. Include:
the three changes with before/after; the lint's own red-proof (it must fail on an undeclared
template and pass on a declared one); the suite tally with the `^FAILED` grep and the commit sha;
touched paths; any triage candidates; and your own mistakes.

Then push and tell the Admiral the head sha — it gates on the exact head, not the reported one.
