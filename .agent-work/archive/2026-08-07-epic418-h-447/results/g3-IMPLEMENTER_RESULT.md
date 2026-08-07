# IMPLEMENTER_RESULT — g3: rewire the closeout obligations onto episode capture

**Issue** #447, epic-418 workstream H · **worktree** `C:/Programs/constellation-skills-wt/epic418-h-447`
· **branch** `epic-418/h-447-episodes-retirement` · **base** `dbf9a23` · **not committed** (Commander commits)

**Verdict: COMPLETE.** All nine close criteria met. Unresolved blockers: **none**. One gap found that is
**not mine to fix** and needs a ruling before g5 can close — see *Escalation* below.

Engine plan driven end to end: `.agent-work/epic418-h-447/crew-plans/g3-implementer.json`
(8 items, lease `g3-impl-447`).

---

## Diff summary — 5 files, all inside the allowed scope

```
 scripts/install_constellation.py                        | 25 ++++++-
 skills/admiral/templates/ADMIRAL_SPINE.template.json     |  9 +--
 skills/commander/templates/COMMANDER_SPINE.template.json |  9 +--
 tests/data/store_mentions.approved.txt                   | 63 ++++++++++++++++
 tests/test_install_constellation.py                      | 85 ++++++++++++++++++--
 5 files changed, 171 insertions(+), 20 deletions(-)
```

`git status --porcelain` over `skills/ scripts/ tests/` shows exactly those five modified paths and
nothing else. No fenced file was read or touched.

### `skills/commander/templates/COMMANDER_SPINE.template.json` — 4 insertions, 5 deletions of 136 lines

- **`feedback` imperative.** Kept verbatim: the honest-reflection opening, the crew Workflow Feedback
  harvest from each `gN-integrate`, and the run-specific-`none` requirement. Everything from the
  `AGENT_FEEDBACK.md` append onward — apply-or-defer, ripeness, `bank_reason`, dormancy,
  export/resolve/defer, the delta-op vocabulary, `apply_lessons_delta.py`, `authority=human` —
  **deleted, not translated**. In its place: capture one episode **per distinct thing that happened**
  (not one per run, not a summary) stating `task-intent` / `expected-behavior` / `observed-behavior` /
  `impact-cost` / `workaround`, written through `apply_episode_delta.py --store-root episodes`.
  The required sentence is present **verbatim** (asserted by string equality, not by eye):
  > An episode is a record, not a rule: write what you observed, and do NOT write a rule for a future
  > agent to follow — a rule to follow belongs in docs/agents/\* and is a human's call.
- One clause reworded rather than deleted: `bare 'none' entries fail the invariant check` →
  `a bare 'none' does not close this step`. The rule survives; the check it named does not.
- **`feedback.c1` — retargeted in place** onto `verify_episode_captured.py … --phase feedback`.
- **`feedback.c2` — deleted.** Terminal, so nothing renumbered. `feedback` postconditions are now `[c1]`.
- **`archive` imperative.** The commit sentence now names this run's episodes under `episodes/` as the
  durable record — a tracked repo-root path that survives `git worktree remove` and a fresh clone — and
  the whole is-`.agent-work`-gitignored branch is gone. The invariant-check sentence became the
  archive-phase capture gate, saying explicitly that it additionally requires git to *track* the episode.
  PR-body-on-Windows, work-area move, `c4` waiver path and lease-release-last ordering are byte-identical.
- **`archive.c1` — retargeted in place** onto `--phase archive`. `archive` postconditions still
  `[c1, c2, c2b, c3, c4]`.
- **`archive.c4` `deny_globs` — untouched, byte-identical.** Both retired paths kept; `episodes/`
  deliberately **not** added (episodes are meant to be committed).

### `skills/admiral/templates/ADMIRAL_SPINE.template.json` — 4 insertions, 5 deletions of 67 lines

- **The `constellation-lessons-auditor` dispatch and its entire disposition-routing paragraph are
  DELETED.** Not repointed. Gone with it: the run brief, graduate-and-retire, template delta, Charter
  nomination, constellation export, lesson-inbox delta, drop-with-reason, `apply_lessons_delta.py`,
  the `authority=human` apply rules, and `bank_reason`. Before cutting, the span was asserted to contain
  each of those tokens **and** asserted *not* to contain `episodes` — so the excised text could not
  possibly have been an already-repointed version.
- Closeout now reads: 1) write the epic's record as episodes (same record-not-a-rule sentence, same
  `--store-root episodes` writer, then the capture gate); 2) the surgical-raw-text rule for shipped
  compact JSON, kept because it is generally true; 3) cartographer reconcile; 4) hygiene; 5) user
  acceptance; then the lease release. Steps 3–5 and the release are byte-identical.
- **`closeout.c1`** — statement rewritten, `check` still `null`. **`closeout.c2`** — retargeted onto the
  capture gate. **`closeout.c6` — deleted** (terminal). `c3`/`c4`/`c5` untouched. Postconditions are now
  `[c1, c2, c3, c4, c5]`.

### `scripts/install_constellation.py`

`SKILL_SCRIPT_BUNDLES`: `admiral` and `commander` drop `apply_lessons_delta.py`,
`verify_lessons_applied.py` and `verify_agent_feedback.py`, and gain `apply_episode_delta.py` and
`verify_episode_captured.py`. The `lessons-auditor` entry is deleted from `SKILL_SCRIPT_BUNDLES` **and**
from `SKILL_REFERENCE_BUNDLES`. `query_episodes.py` is **not** bundled, with a comment at the bundle
(lines 141–159) stating in as many words that the omission is a **default, not a boundary**, and naming
all four measured routes around it: repo-relative execution, plain `Read`/`Grep` on a tracked path, the
unfiltered `copytree`, and `SCRIPT_RUNTIME_COMPANIONS`.

### `tests/test_install_constellation.py`

- **New, general:** `test_every_spine_command_names_an_installed_script`. Installs both spine-owning
  skills, walks **both** condition lists of every task, pulls every `*.py` token out of each
  `kind: "command"` check, and asserts the owning skill installs that script. No name is enumerated, so
  it protects every future rewiring rather than this one. A command with no `.py` token (`archive.c2b`'s
  `gh pr list`) is skipped by design; a `checked > 0` assertion means an empty walk cannot read as a pass.
- **New, per-name, deliberately kept narrow:** `test_episode_write_path_bundled_into_commander_and_admiral`
  (replacing `test_lessons_gate_verifier_bundled_into_commander_and_admiral`). This exists because
  `apply_episode_delta.py` is named only in a spine **imperative** — no check runs it — so the general
  test structurally cannot see it. It also asserts the retired trio is **absent** from both installs.
- Two existing assertions repaired because this rewiring deliberately invalidated them:
  `test_installed_templates_use_absolute_bundled_script_paths` (feedback/archive `c1` now name
  `verify_episode_captured.py`) and
  `test_codex_project_scope_installs_all_skills_under_project_codex_skills` (commander now ships
  `verify_episode_captured.py`).

### `tests/data/store_mentions.approved.txt`

19 approvals appended under four honest reasons — all write-side, none a read instruction. The sites were
re-derived through the guard's **own** `store_mention_sites()` + `normalize()` and written
programmatically, never retyped, so an approval cannot exist in a form the guard would not recognize.
File stays pure-LF as it was.

---

## Every evidence command, with its REAL exit code

Exit codes captured by redirecting to a file and echoing `$?` — never through a pipe.

| # | Command | Exit | Result |
|---|---------|------|--------|
| 1 | `python -m pytest tests/test_install_constellation.py -q` | **0** | 103 passed, 371 subtests passed |
| 2 | `python -c "import json;[json.load(open(p,encoding='utf-8')) for p in (both spines)]"` | **0** | both still parse |
| 3 | `python scripts/verify_retirement.py` | **1** | 122 violations, all g4/g5's (see census) |
| 4 | `python scripts/verify_retirement.py \| cut -f1 \| sort -u` | — | `replacement-absent` **GONE**, `unapproved-store-mention` **GONE** |
| 5 | `python -m pytest tests/test_retirement_guard.py -q` | **0** | 12 passed, 1 xfailed |
| 6 | `FORCE_COLOR=0 NO_COLOR=1 python -m pytest -q` | **0** | **1716 passed, 2 skipped, 1 xfailed, 559 subtests passed** in 283s |
| 7 | `python …/constellation-commander/scripts/verify_agent_feedback.py epic418-h-447 --phase feedback` | **1 → 1** | unchanged; not stranded |

Transcripts: `.agent-work/epic418-h-447/evidence/g3-*.txt`.

`verify_retirement.py` exits 1 by design: two legs are **g4/g5's work**, not this gate's — the retired
files are still tracked and still named in prose this gate may not touch.

## Guard leg distribution, before and after

| leg | before (`dbf9a23`) | after | owner |
|---|---|---|---|
| `replacement-absent` | 4 | **0** | **this gate — closed** |
| `unapproved-store-mention` | 9 | **0** | **this gate — closed** |
| `retired-name-on-shipped-surface` | 130 | 117 | g4/g5 (13 fell out of this gate's deletions) |
| `retired-path-still-tracked` | 5 | 5 | g4 (`git rm --cached`) |

The last `replacement-absent` needed a real fix rather than a bundle edit, and it is worth naming:
`verify_retirement._spine_names_replacement` reads task **imperatives**, not check commands — deliberately,
per its own docstring ("a script named only in a postcondition's check command is wired but unspoken").
Wiring the admiral's `closeout.c2` alone left the leg red. The admiral imperative now tells its agent to
run the capture gate, matching the commander's.

## Red proof for the new install test

Pointed `commander` `execute.p2` at `scripts/verify_no_such_script.py` (raw-text swap on a byte backup),
then ran the new test alone:

```
AssertionError: False is not true : commander spine execute.p2 runs verify_no_such_script.py,
which SKILL_SCRIPT_BUNDLES does not install into …/constellation-commander/scripts
1 failed, 1 passed, 8 subtests passed        exit 1
```

Transcript: `.agent-work/epic418-h-447/evidence/g3-redproof.txt`. The decoy landed on a **precondition**,
which is the half a postconditions-only walk would have missed — so the red proof also proves the walk's
breadth, not just that it can fail. Restored from the byte backup: JSON parses, CRLF back to 134, zero
bare LF, `numstat` back to 4/5, decoy string absent.

## The trap: the machinery I was editing

`verify_agent_feedback.py` at
`C:/Users/fredc/.claude/skills/constellation-commander/scripts/verify_agent_feedback.py` — **before: exit 1,
after: exit 1**, same message. Verified by running it, not assumed. Dropping the script from
`SKILL_SCRIPT_BUNDLES` does not touch the already-installed copy, and no install ran in this gate.
This Commander's own closeout is **not** stranded.

## Diff shape — raw-text, not a reflow

Both spines: **4 insertions, 5 deletions** on files of 136 and 67 lines. The single net line lost in each
is the deleted terminal postcondition. No `json.load`/`json.dump` round-trip anywhere: every span was
located by start/end markers and sliced out of the raw text, with a uniqueness assertion on each marker so
a drifted anchor raises instead of silently editing nothing. Read and written with
`encoding="utf-8", newline=""`, so CRLF survived: **135 → 134** CRLF on the commander, **66 → 65** on the
admiral, **zero bare LF in either**, checked after every write. Edit scripts kept for review at
`.agent-work/epic418-h-447/g3-edit-commander.py` and `g3-edit-admiral.py`.

---

## Escalation — one gap, not mine to fix

**The handoff's §4 asks for something the guard cannot express.** It says to add
`.agent-work/LESSONS.md` and `.agent-work/AGENT_FEEDBACK.md` — kept in `archive.c4`'s `deny_globs` — to
"the guard's approved list". There is no such list for them. `tests/data/store_mentions.approved.txt` is
the census for the **`unapproved-store-mention`** leg only; `_leg_retired_name` in
`scripts/verify_retirement.py` has **no approval mechanism at all**, and `SCOPE_EXCLUSIONS` covers only
`tests/` and the guard itself.

Consequence, and it lands on g5 rather than here: those two `deny_globs` entries are a permanent
`retired-name-on-shipped-surface` violation, so that leg can never reach zero and
`test_canon_is_clean`'s `xfail(strict=True)` can never XPASS — which is the marker whose whole purpose is
to outlive nothing. **The `deny_globs` entries are right and should stay** (after g4 they mean "do not
re-stage the retired files", a stronger reason than the one they were added for). What needs a ruling is
the guard: it needs either a reason-carrying approval census for the retired-name leg, or a narrow
exclusion for the two spine templates' `deny_globs`. `scripts/verify_retirement.py` is outside my allowed
scope and I did not touch it.

## Corner cases declined, with their comment site

1. **`query_episodes.py` unbundled is a default, not a boundary** — comment at
   `scripts/install_constellation.py:141-159`, naming all four routes around it. Deliberately not
   closed: an overclaim here would be worse than no claim.
2. **The archive imperative's "leaving the unified `AGENT_FEEDBACK.md` at the agent-work root" clause was
   trimmed** — one clause beyond the handoff's letter. Left in, it would have contradicted the
   `archive.c1` I had just retargeted away from a work-area-root feedback log. The work-area move itself
   is untouched.
3. **Admiral closeout numbering.** The auditor was step 1 and is gone; episode capture is now step 1 and
   the surgical-JSON rule is step 2, so the list stays 1–5 and steps 3/4/5 are byte-identical. The
   handoff called the retrospective "step 2"; the content is what it asked for, at a different index.
4. **`--store-root episodes` added to the check commands, not only the imperatives.** The handoff's
   literal text for `feedback.c1` omits it. Both `apply_episode_delta.store_root()` and
   `verify_episode_captured.main()` carry a comment naming **g3** as the gate that must pass it, and
   without it an installed copy resolves the store to
   `~/.claude/skills/constellation-<role>/episodes` and the gate exits **2 (REFUSED)** on every run — the
   same `#308` failure shape the handoff's own §1a calls non-negotiable. Deviating toward the handoff's
   stated rationale rather than its literal string. Flagging it because a reviewer diffing against the
   literal text will see the extra flag.
5. **`tests/data/store_mentions.approved.txt` and `text=auto`.** Git warns that the file's LF will become
   CRLF on a future checkout. Harmless — `parse_approved` strips per line and `normalize()` collapses
   whitespace — so not chased.

## Workflow Feedback

- **The handoff gave a literal check-command string that contradicted its own §1a rationale.** §1a is
  emphatic that `--store-root` is non-negotiable for the writer and explains exactly why; §1b then spells
  the `feedback.c1` command without it, for a script whose source comment says spine commands must pass it.
  I followed the rationale. A handoff that quotes an exact string should quote the one it wants shipped —
  this is the field most likely to be copied verbatim by an implementer who trusts it.
- **§4's "add them to the guard's approved list" is not implementable** — see *Escalation*. This is the
  one instruction I could not do the closest compliant thing for, because the mechanism does not exist.
- **The handoff did not say what happens to the `AGENT_FEEDBACK.md` mention inside the archive imperative's
  work-area-move sentence.** It said to leave the work-area move untouched, and the move sentence contained
  a retired filename. I trimmed the clause and reported it; a line in the handoff would have saved the
  judgment call.
- **The "keep the epic retrospective (step 2)" instruction assumed a step numbering that stops existing
  once step 1 is deleted.** Minor, but it forced an unbriefed choice about how the list renumbers.
- **What worked, and is worth reusing:** the handoff's insistence on re-deriving the store-mention line
  numbers rather than trusting the ones it printed. They happened to be right, but deriving them through
  the guard's own `store_mention_sites()`/`normalize()` is also what made the approvals correct by
  construction rather than by transcription.

## Map Impact

- **`struct:skills/commander/templates/COMMANDER_SPINE.template.json`**,
  **`struct:skills/admiral/templates/ADMIRAL_SPINE.template.json`** — both closeout paths changed owner.
  Condition inventories moved: commander `feedback` `[c1,c2]`→`[c1]`, admiral `closeout`
  `[c1..c6]`→`[c1..c5]`.
- **`struct:scripts/install_constellation.py`** (bundle level) — `admiral`/`commander` bundles swapped
  three retired scripts for two episode-store scripts; the `lessons-auditor` skill now has **no** script
  or reference bundle, which is the installer-visible half of its g4 deletion.
- **`capability:run-closeout-learning`** — **changed owner in this gate.** Its write path is no longer
  `.agent-work/LESSONS.md` + `.agent-work/AGENT_FEEDBACK.md` adjudicated by an auditor; it is
  `apply_episode_delta.py` into `episodes/`, gated by `verify_episode_captured.py`. There is **no
  successor read path** and none was created.
- **`capability:episode-store`** — gains its first two shipped consumers, both write-side.
- **`constraint:episodes-are-not-prescriptions`** — honoured by deletion at every site: no instruction in
  either spine tells an agent to read `episodes/`, and every one of the 19 census approvals is a write
  path, a bundle entry, or an honest note about one.
- **`constraint:doctrine-lives-in-docs-agents`** — now stated in the spines themselves, in the verbatim
  record-not-a-rule sentence carried by both.
- **`decision:episodes-replace-both`** (`@grade: settled/human`) — implemented, not contradicted. No
  successor playbook was created.
- **Candidate contradiction to float, not to revise:** `docs/agents/CREW_CONTEXT.md:60` still reads
  *"Read them with `scripts/query_episodes.py` and the engine's `current` verb."* That is a shipped
  surface instructing an agent to read the store. It is `docs/` prose and therefore explicitly g4/g5's,
  not mine, and it is already an approved census entry — so it will not show up as a violation. Recording
  it here so it is not rediscovered late.
