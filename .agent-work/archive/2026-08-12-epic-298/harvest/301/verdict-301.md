# Verdict — issue #301, episode record and durable store

**commander-301 · epic-298 element C · branch `epic-298/301` · base `b69e6c8` · PR #320**

## 1. Verdict

**SHIPPED AND MERGED.** All four gates complete, green, and independently reviewed. PR **#320 is
merged** (squash `195e893b8`), gated on the CI exit code verified at source rather than a reported
local green. The retirement layout was held open across g1–g3 for the human; Tommy ruled *"move
the file, prefer to keep files clean of history unless they're historical. archives are available
strats"*, and g4 bound it.

**The spine is TERMINAL — all ten steps complete.** Archive closed and the lease released as the
final journaled action, in that order (`verify_agent_feedback --phase archive` exit 0 → attest
c2/c3 → closing `advance archive` → `release`). Engine reports `LEASE released` and `DONE: no open
items`. Work area at `.agent-work/archive/2026-08-01-301/`. The worktree was swept by the Admiral
immediately afterwards.

> **Corrected post-harvest by the Admiral, 2026-08-01.** This paragraph originally read "driven to
> `archive`, which is **deliberately held**" — accurate when harvested, false ninety seconds later
> when the commander completed archive on the harvest go-ahead. The commander had the fix written;
> its `cd` failed because the worktree was already swept, so the correction never landed and this
> harvested copy became the only copy. **This staleness is structural, not an oversight:** you must
> harvest *before* the release to be safe against a death, and the agent's last state changes *after*
> the release — so a harvested verdict is guaranteed stale by exactly the closing sequence, every
> time, for every commander. The cheap fix, and now the standing instruction: **the harvester
> re-reads the verdict's status line after the release and before the sweep** — it is the only field
> that changes in that window.

Every acceptance criterion the issue names is met and evidenced. The one remaining piece of work
is a four-adapter binding the design was deliberately shaped to make cheap.

| Gate | Deliverable | State |
|---|---|---|
| g1 | `docs/EPISODE_STORE.md` + store at git-tracked `episodes/` | closed, 3 review rounds, 2 reworks |
| g2 | `scripts/apply_episode_delta.py` — the only write path | closed, 2 review rounds, 1 rework |
| g3 | `scripts/query_episodes.py` + acceptance exercise | closed, 1 review round, APPROVE |
| g4 | bind the ratified file-move layout + retirement retrieval | closed, 2 review rounds, 1 rework |

## 2. Evidence

### 2.1 The design-it-twice comparison

**Panel N=4**, one named distinct constraint each, run in parallel with no visibility of one
another: **A** minimal-record, **B** assertion-native, **C** append-only-history, **D**
retrieval-first. Compared on depth / locality / seam placement / testability plus the pre-ruled
obligations. Full comparison at `.agent-work/301/design-it-twice/COMPARISON.md`.

**Recommendation floated (not self-applied):** D's record shape + A's retirement mechanism, with
five grafts — C's writer-enforced partition, A's always-present headings, a validated non-empty
retire reason, A's single-line enforcement, and B's per-field assertion addressability for the
agent-supplied bin only.

**The synthesis worth keeping:** *the partition itself tells you which bin needs assertion
machinery.* Agent-supplied claims get disputed, so they need individually addressable standing;
mechanical facts do not, so they stay flat `key: value` lines and pay none of B's ceremony. That
dissolved the ceremony-versus-non-foreclosure tension the panel exposed rather than trading one
against the other.

**Genuinely unanimous (verified against all four files):** one file per episode; retirement never
deletes or truncates; the LLM never writes the store directly; cause and remedy separately
attachable and optional.

**I got two claims wrong and the Admiral acted on them before I caught it** — see §5.

### 2.2 The documented mechanical / agent-supplied partition

Literal section headings, never a naming convention, and **enforced at the single write path** by
a per-bin field-name allowlist — a misfiled field is rejected, not discouraged.

- **Mechanical** (zero agent effort): run/project, role, active spine step, context manifest
  reference at a revision, refusals, reopens, rework counts, failed commands, artifact refs.
  Flat `- key: value`; no strength, no standing.
- **Agent-supplied** (deliberately small): task intent, expected behavior, observed behavior,
  impact/cost, workaround — each individually addressable with its own lifecycle standing.
- **Diagnosis**: suspected cause and proposed remedy as separate, optional, pluralizable
  assertions. An episode with no diagnosis is complete and valid.

### 2.3 The stated retirement policy

**Retired means excluded from ordinary rhyme-search and RETAINED in history. Never deletion,
never truncation.** A non-empty reason is required and validated at the write path. Retiring an
episode never touches the assertions inside it: per-episode `status` and per-assertion
`lifecycle-standing` are separate dimensions at different scopes, so retirement is a
**search-visibility switch, not a verdict on the claims**. No dormancy auto-expiry and no cap —
episodes are retired by an explicit act, never by silently aging out.

The *layout* — file-move versus status-field — is the held decision, deferred behind seams.

### 2.4 The cross-session retrieval exercise, and what it actually proved

**Exercised, not asserted.** All twelve acceptance tests pass individually.

- **Session boundary is real:** `subprocess` + `sys.executable`, three distinct OS pids observed
  (parent/writer/query), and the child reports its own `getpid()` *inside its JSON answer*, so
  the answer is tied to that process rather than assumed. The reviewer confirmed nothing is
  smuggled: the id is `<run>-<seq>` and carries none of the `observed-behavior` text the test
  asserts crossed — that sentence exists only in the file on disk.
- **Worktree boundary is real:** actual `git init` + two actual `git worktree add`; each linked
  `.git` asserted to be a *file* holding a `gitdir:` pointer; and the observed transition
  **absent → still absent after the local commit → present only after merge.** A shared
  filesystem would have leaked at step one.
- **The tests can actually fail.** The reviewer ran **eight mutations** in an out-of-repo mirror
  and confirmed each goes red — including neutering the anti-aliasing guard to test whether the
  worktree test could pass with two worktrees sharing a directory. It still went red, at the
  still-absent-after-local-commit assertion.

**What this did NOT prove:** nothing exercises a store with many episodes accumulated over real
runs — no episode has ever been captured, because capture is issue #305. Retirement-dependent
retrieval is untested because it is unbuilt (g4). And the #308 companion exercise (consolidate a
cluster, confirm neighbours of consolidated episodes stay findable) is *designed for* and not
precluded, but not run.

### 2.5 The concrete Stratum A expressibility mapping

| Stratum A dimension | Episode field | Note |
|---|---|---|
| Identified assertion | each agent-supplied field; each cause/remedy block | individually addressable — the point |
| Source | mechanical `run`/`role`/`step`, or the authoring agent/reviewer | always present |
| Supporting evidence | `artifact-ref`, `failed-command`, `context-manifest-ref@revision` | mechanically captured or cited |
| Challenging evidence | dispute entries, same shape, opposite direction | never store-computed |
| Qualitative strength | `strength` ∈ weak/medium/strong | never auto-derived; only by an attributable, cited act |
| Lifecycle standing | per-assertion `standing`, separate from per-episode `status` | different questions, different scopes |

**Proven, not promised** — `NonForeclosureTests`: disputing one agent-supplied field changes that
field's standing, leaves a sibling's standing unchanged, and leaves the sibling's stored line
**byte-identical**. The record is not rewritten to accommodate a dispute. That third clause is
what makes "without rewriting the record later" testable rather than rhetorical.

### 2.6 Test commands and exit codes

| Command | Result |
|---|---|
| `py scripts/verify_worktree_isolation.py --here …` | **exit 0** |
| `python -m pytest tests/ -q` (baseline `b69e6c8`) | 1157 passed, 2 skipped |
| `python -m pytest tests/test_episode_store.py -q` | **66 passed, 16 subtests** |
| `python -m pytest tests/ -q` (final) | **1223 passed, 2 skipped, 276 subtests** |
| `! python scripts/apply_episode_delta.py --delta tests/fixtures/episodes/misfiled-field-delta.json` | correctly **fails** |
| `! … missing-retire-reason-delta.json` | correctly **fails** |
| `! … newline-injection-delta.json` | correctly **fails** |
| `test -f docs/EPISODE_STORE.md && git ls-files episodes \| grep -q .` | **passes** — store really in git |

Both commands named per project doctrine (targeted + broader suite). Guards are proven by
`!`-negation postconditions, not self-report — applying `lesson:prove-command-fails-postcondition`,
which I initially missed despite it being pasted into my own launch order.

**PR #320**, open against `main`, **CI green**, **not merged** — g4 is outstanding and merging now
would ship a store whose retirement layout nobody has ratified. Five commits: `6a051cc`,
`7e8bdb1`, `8a8de69`, `321f3a9`, `bef88f7`.

### 2.6a The portability defect — caught by CI, not by me

The first push was locally green and **CI-red: 39 failures, one root cause.** The store used
`Path.read_text(newline=...)` / `Path.write_text(newline=...)`, kwargs pathlib only gained in
**3.13**, while `ci.yml` pins **3.12**.

**My local suite structurally could not catch it.** `python` on this host is 3.14.3 and `py` is
3.12.13 — the CI version. So local green was never evidence for CI green, and nothing said so.
The sting: that skew came from following the guidance in **#313**, which I filed — it documents
that `py -m pytest` false-reds, which routes agents onto the interpreter *further* from CI. The
documented false-red and this false-green are the same problem wearing opposite signs, and I
walked into the second while fixing the first.

**The traceback under-reported the blast radius, and that is the transferable part.** The CI
failure named **one** call site. There were **13**. The other twelve sat in files the failing
tests never reached, so nothing in the red output pointed at them. Patching the named line would
have produced a **green CI over a still-broken store** — the worst available outcome, because
that green would then have been trusted. A traceback reports where execution *stopped*, not
where the defect *lives*. When the fix is "stop using an API that turns out to be unavailable,"
the unit of repair is every use of that API, found by grep, not the line in the stack. Stated
generally, since the specific kwarg will never recur: **after an environment-shaped failure,
search for the pattern before fixing the instance.**

Fixed at all 13 call sites via `Path.open(newline=...)`, which works on every supported version.
Because `newline=""` is **load-bearing** — it is what keeps the parser's bytes identical to the
bytes on disk, which both the line-boundary guard and the byte-for-byte assertions depend on —
the replacement is centralized in two named helpers rather than scattered. That is this gate's
own earlier lesson applied again: define an invariant once, in terms of what consumes it.

**The guard:** `FloorInterpreterPortabilityTests`. A CI matrix entry would not have helped —
CI *already* ran the floor and *already* caught it; what was missing was a **local** check. It
drives a real round trip on the floor interpreter in a subprocess and asserts `REQUIRES_PYTHON`
still equals `ci.yml`'s pin. **Mutation-verified:** reintroducing the 3.13-only kwarg makes it
fail with the original `TypeError`. It skips visibly where no floor interpreter is discoverable,
and says so rather than overclaiming its reach.

Two things this turned up that matter more than the bug. First, **a launcher name resolves
differently depending on who invokes it** — `py` is 3.12 from the shell and **3.14 from inside a
pytest subprocess** — so name-based discovery is not dependable, and my first guard silently
skipped because of it. A guard that never runs reads as coverage while providing none. Second,
repairing the writer broke the write-phase atomicity test, which patched `Path.write_text` and
claimed to work "either way"; that stopped being true the moment the writer moved off that
method, so the patch stopped firing and the test went red for a reason unrelated to what it
tested. It now patches the module's own write seam — a test should track the implementation's
seam, not a stdlib detail.

**Verified on both interpreters:** 3.12 via `py -m unittest tests.test_episode_store` (68 tests,
OK) and 3.14 via pytest. CI on `bef88f7`: **1270 passed, 2 skipped, 333 subtests**.

## 3. `verify_worktree_isolation.py --here` output, pasted

```
$ py scripts/verify_worktree_isolation.py --here C:/Programs/constellation-skills-wt/298-301
worktree OK: in C:/Programs/constellation-skills-wt/298-301
EXIT=0
```

Run as the first action, before any git operation.

## 4. Map impact

The repo has no `docs/architecture/` packet map, so there is no Cartographer reconciliation to
run — recorded as a reasoned no-op, not a gap. What the structural record should now say:

- **A new tracked artifact family exists**, `episodes/`, owned by `docs/EPISODE_STORE.md`. It is
  the repo's **first durable accumulating store** — distinct in kind from `.agent-work/`, which
  is entirely untracked and disposable.
- **"Validated delta is the only write path" is now a pattern, not a one-off.**
  `apply_lessons_delta.py` had been alone; `apply_episode_delta.py` joins it. That is the
  architecturally interesting change and the thing a future author should notice and follow.
- **A seam-per-held-decision idiom** is demonstrated: five named seams keep a human decision
  genuinely deferrable in *implementation*, not just in wording, so binding it is an adapter
  swap. Worth naming as reusable technique.
- **`durable_root()` has a scope boundary worth recording:** it is right for gitignored
  worktree-local state and wrong for tracked stores, because its epic-lease exception trades
  centralization for writability.

## 5. Where I was wrong, and how it was caught

Recorded prominently because the Admiral acted on the flawed version before I corrected it.

My first comparison claimed **six** unanimous panel decisions. A cold critic found two were
manufactured and a third overstated. I verified mechanically before accepting:

```
$ for f in candidate-*.md; do grep -ic "durable_root\|durable root" "$f"; done
A:1  B:5  C:0  D:0        # I claimed all four. D was the candidate I recommended.
```

Manufactured consensus is worse than a plain recommendation: it presents the author's preference
as the panel's verdict, quietly removing a choice from the human it belongs to. Corrected, sent
to the Admiral, recorded in `COMPARISON.md` §0.

A second cold critic then found my gate plan had **no exercised test** for the priority-1
non-foreclosure obligation, and that three "the writer REJECTS X" postconditions were
attestations rather than `!`-negation checks — from a lesson **pasted into my own launch order**
that I still failed to apply. All findings from both critics were accepted; none rejected.

**Also mine to own:** I proposed `len(value.splitlines()) > 1` as the newline-guard fix; the
implementer correctly pointed out it misses the trailing-separator case and chose a better
predicate.

## 6. Triage candidates — filed to the tracker, not banked

- **#313** — 24 repo docs prescribe `py -m pytest`, which reports "No module named pytest" on
  this host while `python -m pytest` is green. One is a drill's worked example of an engine
  **command postcondition**, so copying it yields an `advance` refusal reading as a broken suite.
- **#314** — `commander-core.md` instructs delegated Commanders to have subagents reply via
  `SendMessage`, but a Commander runs as a teammate and teammates cannot spawn *named*
  subagents. All four panel dispatches failed on first attempt.
- **#319** — episode working-tree bytes differ across worktrees under `core.autocrlf`. Harmless
  for #301 (identity is the blob hash), a real hazard for **#308** if consolidation hashes or
  compares working-tree bytes — the same silently-wrong-but-green shape, displaced into a
  consumer that does not exist yet.

## 7. Workflow feedback

Full retrospective in the staged trio at `.agent-work/staged-feedback/301/`. Load-bearing items:

- **Two mechanism defects filed** (#313, #314), both of which cost real round-trips.
- **`stage_feedback.py` accepts a body its own verifier rejects.** Two undocumented
  requirements: signal sections must be **bold labels**, and — sharper — `_entry_block()`
  delimits an entry from its `##` heading to the *next* `##`, so **any `##` subheading silently
  truncates the entry to nothing**. The error message names a symptom far downstream of the
  cause. Cost two re-stage cycles.
- **`attest` succeeds on a `pending` step, then `advance` refuses it.** Hit repeatedly.
- **The rework cap (3) is per-gate and was nearly binding at g1**, which needed 2. Three review
  rounds on a *prose* gate felt expensive but was correct: every round found a real instance of
  one root cause, and g2/g3 built directly on that text.
- **Design-it-twice convergence has no verification discipline.** The brief asks for a
  recommendation with axis-by-axis reasoning; it never asks the converger to verify
  cross-candidate claims mechanically. That gap is exactly where my manufactured consensus lived.

## 8. What is needed to finish

**Tommy's ratification of the retirement layout** — file-move (`active/`↔`retired/`) versus
status-field-filtered-negatively. My recommendation, flipped once under a cold critic and stated
as a flip, is **file-move**: "which set is this episode in" is then a *filesystem* fact rather
than a *content-parsing* fact, and every silent-failure mode found in this run was a
content-parsing failure. Structural immunity beats a validated defense when the failure is
silent, because validation fails open the moment a file is hand-edited or a future write path
skips the validator.

Once ratified, g4 is bounded: bind four adapter bodies at their named seams, add
retirement-dependent retrieval and its adversarial fixtures, review, merge PR #320. The design
was shaped specifically to make that cheap.

## 9. Harvest note

> **HARVEST DISCHARGED — Admiral, 2026-08-01.** The warning below was live when written and is now
> historical. Everything named in it was collected to the main checkout **before** the worktree was
> swept: `.agent-work/epic-298/harvest/301/` holds this verdict, `design-it-twice/` (brief + all four
> candidates + comparison), the staged trio and both delta files; `harvest/301-full/` holds the
> **entire** 83-file work area including the archived spine, its journal, both amendments and every
> crew handoff and review round. The lessons delta was applied (2 confirms + 4 adds, cap-limited per
> this run's own FENCE ordering), the feedback appended to the durable logs, the branch deleted after
> a content-equality check, and issue #301 closed. Nothing in the swept worktree was the sole copy of
> anything.

`.agent-work/` is gitignored, so this verdict, `COMPARISON.md`, the four candidates, and the
staged trio exist **only in this worktree** and die when it is swept. The code and docs are
committed and pushed (PR #320) and are safe. **Harvest `.agent-work/staged-feedback/301/` and
`.agent-work/301/design-it-twice/` before sweeping.**
