# Prep 302: Catastrophic-Class Invariant Inventory (for Tommy's adjudication)

Status: COMPLETE

Scope note (how the search was bounded): read the canonical shared doctrine in full
(`skills/_shared/global-everyone.md`, `global-crew.md`, `global-orchestrator.md`,
`windows.md`, `skill-goodness.md`), the Admiral harness-survival doctrine in full
(`skills/admiral/references/fleet-doctrine.md`), and the CI/mechanism layer
(`.github/workflows/ci.yml`, `.claude/settings.json`, `scripts/checklist_engine.py`,
`scripts/hooks/spine_rail.py`, and the `scripts/verify_*.py` family). For every
candidate invariant I traced the *actual wiring* — not just a docstring's claim — by
grepping every `templates/*.json` spine/survey for `"kind": "command"` (real
engine-run checks) versus `"check": null` (self-attestation) and by reading the
engine functions (`attest`, `record`, `consolidate`, `_run_check_command`,
`_check_condition`) that decide what "satisfied" actually means. I did **not**
exhaustively read every `skills/*/SKILL.md` and every `references/*.md` in the
corpus (e.g. `commander-core.md`, `charter/references/engineering-rubric.md`'s
project-selectable rubric dials were skimmed and excluded because they're
project-configurable posture choices, not fixed corpus doctrine). This is a
representative, wiring-verified sample of the serious catastrophic-class candidates,
not an exhaustive line-by-line pass over the whole corpus.

A structural finding shows up repeatedly enough to state once, up front, rather than
per-row: **`checklist_engine.py` supports two entirely different strengths of
"enforced."** A `"gated"`-type spine (Admiral, Commander, Explorer) can carry a
postcondition with `"check": {"kind": "command", "command": "..."}` — the engine
itself runs that script and refuses `start`/`advance` on a non-zero exit
(`_check_condition`, `checklist_engine.py:678-700`). A `"survey"`-type checklist
(Interrogator, Reviewer, and any skill with no checklist at all) instead uses the
`record(result, finding)` verb, which does nothing but store whatever the agent
types (`checklist_engine.py:1652-1661` — `t["result"] = result`, no check invoked).
Several doctrine passages call a `verify_*.py` script a "RAIL" or "mechanically
enforced" while it is in fact only wired the second way — a real script that
*would* catch a violation exists, but nothing forces it to run and nothing catches
an agent that skips it or lies about the result. This distinction is the spine of
sections 1 and 2 below.

## 1. Inventory table

| # | Invariant | Where it lives (doctrine) | Enforcing mechanism, if any | Read |
|---|---|---|---|---|
| 1 | A crash-resume state note (step/slug/next-cmd/PID/artifact) must exist and be filled before an Admiral or Commander enters detach-heavy execute work | `global-everyone.md` §Detached and long work; `fleet-doctrine.md` §State-note-before-detach | `scripts/verify_state_note.py`, wired as a literal `"check": {"kind": "command", ...}` **precondition** `p2` on the `execute` step in `skills/admiral/templates/ADMIRAL_SPINE.template.json:37` and `skills/commander/templates/COMMANDER_SPINE.template.json:58`. Confirmed by reading the JSON directly — the engine's `_check_condition` runs this command and blocks `start`/`advance` on nonzero exit. | **MECHANISM-OWNED** |
| 2 | No work is cut from an unconfirmed design spec | `skills/explorer` DESIGN_SPEC doctrine 3 | `scripts/verify_spec_confirmed.py`, wired as postcondition `c1` (`review` phase) and `c2` (`confirm` phase) in `skills/explorer/templates/EXPLORER_SPINE.template.json:56,67`, both `"kind": "command"`. | **MECHANISM-OWNED** |
| 3 | Exploration cannot close having run zero cycles or with any cycle left unconsolidated (premature convergence) | `skills/explorer` DESIGN_SPEC, spine table | `scripts/verify_cycles.py`, wired as postcondition `c2` on the `explore` step, `EXPLORER_SPINE.template.json:37`, `"kind": "command"`. | **MECHANISM-OWNED** |
| 4 | Every threshold-ripe lesson has a terminal disposition before a Commander/Admiral run closes; durable feedback log exists | `fleet-doctrine.md`, closeout doctrine | `scripts/verify_lessons_applied.py` / `scripts/verify_agent_feedback.py`, wired as `"kind": "command"` postconditions on Commander closeout (`COMMANDER_SPINE.template.json:99-100,110`) and Admiral closeout (`ADMIRAL_SPINE.template.json:53,57`). | **MECHANISM-OWNED** |
| 5 | A `command`-kind check's POSIX-form text (`grep`/`&&`/pipe) must never be silently misinterpreted by `cmd.exe` on a Windows box without bash | `global-everyone.md` §Engine verbs | `checklist_engine.py:_run_check_command` (lines 651-675): probes for a POSIX shell; if none is found, returns a **synthetic failed result (returncode 127)** naming the missing shell rather than ever calling `subprocess.run` through `cmd.exe`. Read the function body directly. | **MECHANISM-OWNED** |
| 6 | An agent must never silently end its turn while a spine gate is genuinely mid-flight ("wait-by-ending-turn") | `global-everyone.md` §Detached and long work; `fleet-doctrine.md` §Watcher-sleep | `scripts/hooks/spine_rail.py`'s `decide_stop()`, registered as the **Stop hook** in `.claude/settings.json` (`"py .../spine_rail.py Stop"`). Read the function: it inspects the spine state file directly, and when mid-flight it returns `{"decision": "block", "reason": ...}` — a real, live-wired Claude Code hook that blocks the turn-end, not prose. A documented 3-strike escape hatch exists so a genuinely stuck agent isn't trapped forever. | **MECHANISM-OWNED** |
| 7 | No undocumented pytest skip reaches CI green | `scripts/verify_skip_guard.py` docstring | `.github/workflows/ci.yml` runs `python scripts/verify_skip_guard.py junit-report.xml` as an explicit CI step after the test run; confirmed by reading the workflow file — nonzero exit fails the build. | **MECHANISM-OWNED** |
| 8 | A malformed cut-work issue set (unconfirmed spec, no dependency edge, dangling edge) can never reach a tracker | `constellation-to-issues` DESIGN_SPEC Section A | `scripts/verify_issue_set.py`, hard-called as `"rail first, always"` inside `scripts/file_issue_set.py:main()` (line 336) **before** any filing logic runs, raising `IssueSetError` on failure. This is composition-gated (not engine-gated) but genuinely blocks the actual filing action in code — confirmed by reading `file_issue_set.py` directly. | **MECHANISM-OWNED** |
| 9 | An interrogation record can never be marked consolidated with a self-answered `decision` or without the counterpart's explicit sign-off | `constellation-interrogator` DESIGN_SPEC Section D1 | `scripts/verify_interrogation.py` genuinely contains this logic, and the imperative text on `zc-consolidate` instructs the agent to run it and exit 0 first. But `skills/interrogator/templates/INTERROGATION.template.json` gives **every item, including `zc-consolidate`, `"preconditions": [], "postconditions": []`** — confirmed by reading the whole file. The survey's `record()` verb (`checklist_engine.py:1652`) just stores whatever `result` the agent types; the engine never invokes the rail script itself. | **PROSE-ONLY at the engine layer** (a real script exists; nothing forces or checks its use) |
| 10 | Every Fowler baseline code smell gets a rendered verdict; an override needs a logged repo-standard + reason | `constellation-reviewer` DESIGN_SPEC Section D3 | `scripts/verify_fowler_pass.py` implements this. `skills/reviewer/templates/REVIEW_SURVEY.template.json`'s `r6-fowler` item also has `"preconditions": [], "postconditions": []` (confirmed by reading the file) — same self-attested `record()` path as row 9. | **PROSE-ONLY at the engine layer** |
| 11 | A cause is never called `confirmed` without a named falsifier and an observed result ("reproduce-before-you-claim") | `constellation-diagnose` DESIGN_SPEC Section B; `skills/diagnose/SKILL.md` | `scripts/verify_diagnosis.py` implements this. `skills/diagnose` has **no checklist/spine template at all** — its `SKILL.md` says explicitly this is a manual loop, not a gated engine. The doctrine's own backstop is a "fresh-context reviewer" checking the cut at the routing step, not a machine gate. | **PROSE-ONLY**, reviewer-backstopped (not machine-verified) |
| 12 | A minted skill must not be mechanically broken or an unregistered dead seam (missing from `install_constellation.py`'s bundles) | `constellation-write-a-skill` DESIGN_SPEC Section C | `scripts/verify_skill_registered.py` implements this. `skills/write-a-skill/SKILL.md:11` states explicitly: **"No checklist. Work the draft directly — a lean chat pass, not a gated engine. One rail is enforced"** — "enforced" here means the human/agent is instructed to run the command and it must pass, not that any engine gate forces it. | **PROSE-ONLY**, same self-attested-instruction pattern |
| 13 | Two Constellation agents (Admiral/Commander waves) must never occupy the same git worktree; isolation must be verified before a parallel wave dispatches | `windows.md` hazard #3 ("that is data loss, not friction"); `fleet-doctrine.md` §Worktree isolation | `scripts/verify_worktree_isolation.py` is a real, exit-code-driven script, but it is **invoked only by prose instruction** (`LAUNCH_ORDER.template.md:41`, `fleet-doctrine.md` steps 1-3) — I grepped every `templates/*.json` spine for `verify_worktree_isolation` and got **zero hits**: it is wired into no engine precondition anywhere. The doctrine says so itself: *"The gate is the mechanical guarantee; `--here` is the Commander's own risk-reduction... (Agent-tool dispatch has no engine chokepoint to refuse at)."* | **PROSE-ONLY, self-acknowledged in the doctrine itself** |
| 14 | Never hand-edit the checklist JSON directly, and never read `spine.json` state instead of the engine's `current` output | `global-everyone.md` §Engine verbs, §Engine output is the state channel | A SHA-256 hash-chained journal sidecar exists (`checklist_engine.py:2418-2454`, "tampering with any earlier line invalidates every hash after") — but its own comment says **"The engine NEVER reads it back for its own operation... Only the eval provenance check cross-verifies it."** The doctrine text itself says: *"Enforcement lint is deliberately deferred until post-ship `measure_overread.py` evidence shows the rule is broken often enough to justify the machinery — its absence is a decision, not an oversight."* | **PROSE-ONLY, explicitly deferred by design** |
| 15 | A `settled/human` or `settled/inherited` decision cannot be silently revised at execution time; only the ruling tier unsettles it | `global-everyone.md` §Decision fixedness, §Lint loud execute safe | `scripts/grade_lint.py` lints the *presence* of a grade tag pre-flight ("lint loud"), but the doctrine states outright: **"Nothing enforces the execution-time half in code — `checklist_engine.py` does not parse these tags. It is doctrine you follow by reading the decision."** `--mode execute` is explicitly "a diagnostic... certifies nothing about runtime behavior." | **PROSE-ONLY, explicitly by design** |
| 16 | A "completed"/idle subagent must be confirmed dead before its worktree is reused or a continuation is launched into it (double-occupancy corrupts engine state) | `fleet-doctrine.md` §The sleeper hazard; `global-orchestrator.md` §Idle subagent adjudication | No script found. Enforcement is entirely the Admiral/Commander's own discipline (TaskStop, PID check) before reuse. | **PROSE-ONLY** |

## 2. The gaps — catastrophic-class, PROSE-ONLY (Tommy's priority rows)

These are rows 9-16 above. Grouped by what a mechanism would need to check, and how expensive that looks:

- **Rows 9, 10 (interrogation self-answer guard, Fowler-pass completeness).** Cheap. The
  scripts already exist, already do exactly the right check, and `checklist_engine.py`
  already supports `"kind": "command"` postconditions on exactly this shape of item —
  it is used this way in seven other places in the same codebase (rows 1-4). This is a
  **missing five-minute wiring change**, not a new capability: add
  `"check": {"kind": "command", "command": "python .../verify_interrogation.py <record>"}`
  to `zc-consolidate`'s postcondition and the same for `r6-fowler`. Low cost, high
  confidence fix.

- **Row 11 (diagnose reproduce-before-you-claim).** Moderate. `diagnose` has no spine at
  all by design ("lean chat pass"). Mechanizing this either means giving diagnose a
  minimal survey checklist (a bigger design change than rows 9/10) or making the
  downstream consumer (triage/reviewer) refuse to act on a finding record whose
  `status == confirmed` without independently re-running `verify_diagnosis.py` against
  it. The second option is cheap and composition-gated, same pattern as row 8
  (`file_issue_set.py`).

- **Row 12 (write-a-skill mint gate).** Moderate, lower urgency — a broken/unregistered
  skill is a corpus-quality defect, not itself a "cannot afford to observe once"
  event (nothing downstream trusts an unregistered skill silently; it just fails to
  install). I'd flag this as the weakest catastrophic-class claim on the list; it may
  belong in the ordinary prose bin rather than this audit at all.

- **Row 13 (worktree isolation).** This is the one I'd put at the top of Tommy's list.
  The doctrine calls a worktree collision "data loss, not friction," and the mechanism
  that would catch it (`verify_worktree_isolation.py`) already exists and already
  works — it is simply never invoked except by an agent choosing to follow an
  instruction. It is **not** structurally unmechanizable: Claude Code hooks can fire
  `PreToolUse` on any tool name, including the `Agent` tool used for dispatch (the
  same mechanism `spine_rail.py` already uses for `Bash`/`PostToolUse`, row 6). A
  `PreToolUse` hook on `Agent` dispatch that shells out to `verify_worktree_isolation.py`
  before allowing a wave-dispatch call is a real, buildable gate — the doctrine's "no
  engine chokepoint to refuse at" is true of `checklist_engine.py` specifically, not
  of the harness as a whole. Moderate cost (new hook, needs to parse dispatch
  intent), not cheap, but demonstrably not impossible.

- **Rows 14, 15 (hand-edit/read-around guard; settled-decision guard).** Both are
  **explicitly, deliberately** left prose-only in the doctrine's own words, pending
  field evidence (`measure_overread.py`) that the rule is broken often enough to
  justify building the machinery. This is a considered, stated engineering choice
  already, not an oversight — worth noting to Tommy as "already decided," distinct
  from rows 9/10/13 which look like plain gaps nobody has revisited.

- **Row 16 (dead-agent worktree reuse).** Hard-ish. Confirming a PID is truly dead
  from inside a different process/session, cross-platform, is a real systems problem
  (not a judgment problem) — plausible to mechanize (a "confirm-dead" script analogous
  to `verify_worktree_isolation.py --here`) but nobody has built it yet.

## 3. Third-bin candidates — catastrophic-class, genuinely NOT mechanizable

I looked hard for this bin and found **one strong candidate and one weaker one**, not
zero, which matters for Assumption 6:

- **"Fail visibly rather than emit plausible wrong output; no hidden fallback"**
  (`global-everyone.md` §Universal posture). This is stated as an absolute
  ("fail visibly... no hidden fallback"), and a silent plausible-wrong-output is
  exactly a "cannot afford to observe this failing even once" event — it's the
  textbook case for the catastrophic bin. But no validator in this corpus, and I
  believe no validator *could* exist in general, judges whether a given output is
  "plausible but wrong" versus "genuinely correct" without already knowing the
  ground truth — at which point the check is trivial and the violation couldn't have
  happened. Any mechanization I can imagine (a fixed list of known-bad fallback
  patterns, a "did an exception get swallowed" static check) catches a *subset* of
  violations, not the invariant itself — the residual is unbounded and semantic. I
  believe this is a genuine third-bin member, not just an unmechanized gap.

- **"A negative result kills that specific test, never the idea class"** (Scoped
  nulls, `global-everyone.md`). Whether an agent's prose correctly scopes a null
  result (this variant failed vs. this whole approach is impossible) is a semantic
  judgment about the relationship between what was tested and the broader claim
  space — no generic mechanism can verify that scoping without understanding the
  domain. I rate this weaker than the first, though: the failure mode here is
  "wasted future effort re-litigating a falsely-closed branch," which is costly but
  recoverable, not obviously "cannot afford even once" in the same way a
  worktree-collision data loss or a plausible-wrong-output is. Borderline; Tommy's
  call whether it belongs in the catastrophic bin at all.

I did **not** find a third-bin candidate for any of the rows in section 2 — every
prose-only gap I found (rows 9-16) has at least a plausible, describable mechanism,
even where nobody has built it yet.

## 4. Recommended disposition for Assumption 6

**Undecided-pending-Tommy, but leaning toward "supported, with one live counter-example
that forces a scoped exception rather than a wholesale rework."**

Strongest evidence *for* the assumption: `verify_worktree_isolation.py` (row 13) — the
doctrine's own text asserts the harness has "no engine chokepoint to refuse at" for
this class of invariant, yet the same repo already demonstrates a working
`PreToolUse`/`PostToolUse` hook (`spine_rail.py`, row 6) intercepting the exact
Agent-tool/Bash boundary this would need. The "no chokepoint" claim looks locally true
of `checklist_engine.py` but not true of the harness as a whole — i.e., the corpus
already contains proof-by-construction that a catastrophic invariant which *looks*
unmechanizable from inside one component is mechanizable from a different vantage
point. That is direct evidence the two-bin rule's premise holds more often than the
doctrine's own hedged language suggests.

Strongest evidence *against* full support: "no hidden fallback / no plausible wrong
output" (section 3, first candidate). I could not construct even a sketch of a general
mechanism for it, and I don't believe one exists in principle without begging the
question. If Tommy agrees this genuinely belongs in the catastrophic bin (not just
"good practice" prose), Assumption 6 as stated ("every catastrophic-class invariant...
can be mechanized") is **contradicted**, and the two-bin rule needs a named third
bin — not smoothed away, per the brief — for invariants whose violation-detection is
semantically unbounded rather than merely unbuilt.

My recommendation: rule the "plausible wrong output" item explicitly (in or out of the
catastrophic bin), since that single ruling flips the disposition between "supported
with a punch-list of cheap fixes" and "contradicted, two-bin rule needs a third bin."
Everything else in this inventory (rows 9-16) reads as ordinary unbuilt-mechanism gaps,
not counterexamples to the assumption.
