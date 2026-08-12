# Implementer Handoff

## Gate
`g2` — the validated episode writer (issue #301, epic-298)

## Task

Build **`scripts/apply_episode_delta.py`** — the **only** write path into the episode store —
plus its tests in **`tests/test_episode_store.py`** and adversarial fixtures under
**`tests/fixtures/episodes/`**.

Contract, mirroring the existing `scripts/apply_lessons_delta.py`: the LLM proposes operations
in a **JSON delta file**; this script validates every op and applies them **mechanically and
all-or-nothing** — any invalid op rejects the whole delta and leaves the store byte-for-byte
unchanged. The LLM never writes the store directly.

**Read `docs/EPISODE_STORE.md` first — it is the frozen contract this gate implements.** It was
reviewed three times and is authoritative over anything in this handoff that appears to
conflict; if you find a genuine conflict, stop and tell me.

## Protected Intent

1. **Non-foreclosure.** An agent-supplied claim must be disputable **individually**, without
   rewriting the record. This is a pre-ruled acceptance obligation, not a nice-to-have.
2. **The partition is enforced, not documented.** A misfiled field must be *impossible* to
   write, not merely discouraged.
3. **Retirement never deletes.** And it always carries a reason.
4. **The retirement layout stays unbound.** See the seam rule below — this is the constraint
   most likely to be violated by accident.

## Test Mode

**TDD strongly preferred, test-after acceptable.** Every guard below must have a test that
proves it *rejects* bad input — a green suite that only exercises the happy path does not
satisfy this gate. Per `lesson:round-trip-tests-prove-artifacts-not-parsers`, a round-trip test
over well-formed input proves the input was clean, not that your validator is correct. **Pair
every round-trip test with an adversarial fixture authored to make a naive implementation
return a WRONG answer** — either a false accept (silent PASS on invalid input) or a false
reject (FAIL on valid input).

## Close Criteria

Each is a gate postcondition I will verify independently.

- **C2 — the partition is enforced.** The writer **REJECTS** a delta that files a mechanical
  field under the agent-supplied bin, or an agent-supplied field under the mechanical bin, via
  a **per-bin field-name allowlist**. Proven by an adversarial fixture, not by inspection.
- **C3 — the two content guards.** The writer **REJECTS** (a) a `retire` op whose reason is
  missing or whitespace-only, and (b) any agent-supplied value containing a **newline**. Guard
  (b) is the injection defense: an `observed-behavior` field that quotes a transcript
  containing the literal line `- status: retired` would otherwise let a free-text field forge a
  status line and silently drop a fully active episode out of ordinary search.
- **C4 — all-or-nothing.** An invalid op **anywhere** in a multi-op delta leaves the store
  byte-for-byte unchanged. Proven by a fixture that asserts no partial write — capture file
  bytes before and after and assert equality.
- **C5 — the store root resolves through the g1 seam**, at the git-tracked `episodes/` path.
  **Do NOT call `durable_root()`** — under an active Admiral epic lease it returns the worktree
  root, which would silo the store per worktree.
- **C6 — the dispute op exists and is surgical.** The writer accepts an op that disputes **one
  named agent-supplied field**, changing only that field's lifecycle standing. A sibling
  field's stored line must be **byte-identical** before and after.
- **C7 — the adversarial fixtures exist at these exact paths** (the gate's closeout runs them
  directly, so the paths are part of the contract):
  - `tests/fixtures/episodes/misfiled-field-delta.json`
  - `tests/fixtures/episodes/missing-retire-reason-delta.json`
  - `tests/fixtures/episodes/newline-injection-delta.json`
- **C8 — the retirement layout stays unbound.** The retire op's layout effect routes through
  the **`apply_retirement(episode_id, reason)`** seam named in `docs/EPISODE_STORE.md` §7, with
  the layout-independent field diff separated from the layout-dependent file effect. **Neither
  Option A nor Option B may be hard-coded.** Gate g4 binds one adapter after human
  ratification.

## The seam rule — the constraint most likely to be violated by accident

`docs/EPISODE_STORE.md` §7 names a seam set. Your writer must **call** these, never inline
their mechanics:

| Seam | What it hides |
|---|---|
| store root | where `episodes/` lives |
| `apply_retirement(episode_id, reason)` | the layout-dependent effect of retiring |
| `resolve_episode_path(episode_id)` | which on-disk path holds an episode |
| `iter_episode_ids(include_retired)` | the base enumeration scan |
| `is_episode_in_ordinary_search(episode_id)` | per-id membership (mostly g3's concern) |

Since the layout is unbound, the adapters cannot be *chosen* yet. Implement each seam as a
**single named function with the layout-dependent branch clearly isolated** and a documented
`TODO(g4)` marking where the ratified adapter binds. A reasonable shape: one module-level
constant or resolver that both adapters would swap at, so g4 changes one place.

**A reviewer finding carried forward from g1, fix it here:** the **amend/dispute write path**
must also resolve its target file through **`resolve_episode_path()`**. Retire and fetch
already do; amend was missed. It matters because §6 explicitly anticipates disputing an
already-**retired** episode's content, so under Option A the target may live in either
subdirectory. Without this, amend fails with file-not-found once Option A binds.

## Allowed Scope

- `scripts/apply_episode_delta.py` (new)
- `tests/test_episode_store.py` (new)
- `tests/fixtures/episodes/*.json` (new)
- `episodes/` — only as the store your tests write into. **Tests must not leave episodes
  behind**: write to a temp store root (pytest `tmp_path`) rather than the real `episodes/`
  directory, so the repo stays clean and the suite is order-independent.
- `docs/EPISODE_STORE.md` — **only** if you find a genuine contract conflict, and then only the
  minimal correction, flagged loudly in your result.

## Specific Exclusions

- **Do NOT modify `scripts/apply_lessons_delta.py` or `.agent-work/LESSONS.md`** (owned by the
  live lessons machinery; cutover is ruled at issue #308). **Read** `apply_lessons_delta.py` as
  the pattern to mirror — its `validate_delta`, its all-or-nothing discipline, its
  `retire`-requires-reason rule, its `- field: value` grammar. Mirror it; do not import from it
  in a way that couples the two, and do not edit it.
- **Do NOT build retrieval** — that is g3 (`scripts/query_episodes.py`). You may write only the
  minimum reading needed for the writer itself (parse an existing episode to amend it).
- **Do NOT bind the retirement layout** — g4, after human ratification.
- **Do NOT build capture wiring** (#305) or consolidation (#308).
- **Do NOT design issue #300's manifest** — store `context-manifest-ref` as an opaque
  `<ref>@<revision>` string.

## Constraints

- **Markdown in git only.** No database, no query language, no index.
- **The store never guesses** — no ranking, no similarity, no embedding.
- **Deterministic and attributable**: same delta plus same starting state yields the same
  bytes. No timestamps generated inside the writer unless the delta supplies them, or your
  tests will be flaky and non-reproducible.
- **Windows/POSIX**: this repo runs on Windows with Git Bash. Use `pathlib`, write files with
  explicit `encoding="utf-8"`, and be deliberate about newline handling — `\r\n` translation is
  a real hazard for a byte-for-byte-unchanged assertion (C4) and for single-line enforcement
  (C3b). Consider `newline=""` where it matters and state what you chose.
- If your tests drive concurrent file I/O, `lesson:test-harness-concurrency-failsafe` applies:
  `try/except` with a guaranteed stop-signal in `finally`, and `daemon=True` helper threads —
  a writer thread dying without signaling stop hangs the whole pytest process.

## Map Anchors (inbound)

- **Structural:** `scripts/apply_lessons_delta.py` (the mirrored seam — read, never edit);
  `tests/test_apply_lessons_delta.py` (the test shape to rhyme with); `docs/EPISODE_STORE.md`
  (the frozen contract); new: `scripts/apply_episode_delta.py`, `tests/test_episode_store.py`.
- **Capability:** episode capture — the single validated write path.
- **Constraints:** `constraint:llm-never-writes-the-store-directly`;
  `constraint:partition-enforced-at-the-writer`; `constraint:markdown-in-git`.
- **Decision anchors:**
  - `decision:episode-store-shape` — record shape and retirement mechanism.
    `@grade: settled/human · leans g1,g2,g3,g4 · settle: held for Tommy; NOT yours to choose`
  - `decision:partition-enforced-at-the-writer` — enforcement at the single write path.
    `@grade: settled/inherited · leans g2 · settle: the misfiled-field fixture must be rejected`
  - `decision:store-lives-at-a-tracked-path` — commander decision, closed at g1.
    `@grade: settled/measured · leans g1,g2 · settle: git ls-files episodes returns non-empty`
- **Evidence expectations:** `claim:the-partition-cannot-be-misfiled`;
  `claim:all-or-nothing-leaves-no-partial-write`;
  `claim:an-agent-supplied-claim-can-be-disputed-individually`.

## Deliverable Path Check

- **Committed** — `scripts/apply_episode_delta.py`, `tests/test_episode_store.py`,
  `tests/fixtures/episodes/*.json`. I verified `git check-ignore` exits **1** for `scripts/`,
  `tests/`, and `episodes/` (none ignored).
- All are **new** files: untracked until staged, so they appear in `git status`, not `git diff`.

## Required Evidence

**Load-bearing — prove these rigorously, with pasted command output:**

1. **Each of the three negation checks fails correctly.** Run and paste:
   ```bash
   ! python scripts/apply_episode_delta.py --delta tests/fixtures/episodes/misfiled-field-delta.json
   ! python scripts/apply_episode_delta.py --delta tests/fixtures/episodes/missing-retire-reason-delta.json
   ! python scripts/apply_episode_delta.py --delta tests/fixtures/episodes/newline-injection-delta.json
   ```
   Each must exit **non-zero** with a clear message. The gate's closeout runs exactly these.
2. **C4 all-or-nothing**: show the before/after byte comparison in the test, and paste the test
   name and result.
3. **C6 surgical dispute**: paste the assertion showing the sibling field's line is
   byte-identical across the dispute.

**Confirmatory — a spot-check suffices:** C5, C7, C8.

Do not pad the evidence list beyond this — I would rather have three things proven properly
than eight asserted.

## Verification Commands

```bash
python -m pytest tests/test_episode_store.py -q
python -m pytest tests/ -q      # expect 1157 passed + your new tests, 2 skipped
git status --short              # expect only your new files
```

Use `python`, **not** `py` — on this host `py` has no pytest and reports "No module named
pytest", which reads like a broken suite.

## Suggested Model Tier

`simple bounded` — the contract is frozen and the design decisions are made or explicitly held;
this is careful mechanical implementation against a written spec.

## Authority

**Already decided — do not re-litigate:** Markdown in git; the store at tracked `episodes/`;
the record grammar and partition (frozen in `docs/EPISODE_STORE.md`); the validated
all-or-nothing delta contract; the store is mechanical.

**You must NOT decide alone — stop and return:** the retirement layout (held for human
ratification); any change to the record grammar; anything touching `LESSONS.md`,
`apply_lessons_delta.py`, or issue #300.

**You may decide** (log it): the delta JSON's exact op vocabulary and field names; the internal
module structure; error message wording; the test layout and fixture contents; how the
layout-dependent branch is isolated behind each seam.

## Stop Conditions

Stop and return if: allowed scope must be exceeded; a specific exclusion must be touched;
required evidence cannot be produced; a decision outside the given authority is needed; or
**you find that satisfying any close criterion appears to require binding the retirement
layout** — it should not, and if it does that is a finding I need rather than a decision you
should make.

## Return Format

Return **IMPLEMENTER_RESULT** at `.agent-work/301/crew-handoffs/g2-result.md` with a literal
`VERDICT: COMPLETE` (or `VERDICT: BLOCKED` plus the reason) line, and: completed slice, files
changed, test mode satisfied, evidence produced with pasted output, assumptions used, stop
conditions hit, out-of-scope observations, and a **non-empty Workflow Feedback** section —
what in this handoff or the workflow made the work harder than it needed to be. That section is
harvested into the run's lesson pool.

Do not commit; I integrate and commit.
