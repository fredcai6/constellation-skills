# Recursive Improvement Framework — audit, survey, and proposal

Status: draft for discussion · 2026-06-10

Goal: turn Constellation's one feedback surface (Commander run retrospective) into a
layered learning system where every tier emits signal, every signal has a consumer,
and lessons compound across runs and across projects.

---

## 1. Audit of the current state

What exists today:

| Surface | Where | Captures | Consumed by |
|---|---|---|---|
| Run retrospective | spine `feedback` step → `.agent-work/AGENT_FEEDBACK.md` | adherence, friction, what worked, improvement signals | **nothing reads it** (nominal: "Charter refresh", untriggered) |
| Template Update Candidates | `WORKFLOW_CLOSEOUT.template.md` table | concrete template/interface fixes + disposition | manual; disposition is self-reported |
| Out-of-scope observations | `IMPLEMENTER_RESULT` / `REVIEW_RESULT` | project findings | Commander → Triage |
| Feedback invariant | `scripts/verify_agent_feedback.py` | file exists, mentions work-id, durable placement | spine postconditions at `feedback` and `archive` |

Gaps, by the four loops:

1. **Crew → Commander (dispatch quality).** Implementer and Reviewer results have no
   field for "what about this handoff/anchors/context made the work harder."
   `Out-of-scope observations` is project signal, not workflow signal. The exact
   moment a crew member improvises around a bad handoff is when the signal exists,
   and we currently drop it.
2. **Commander in sequence.** `AGENT_FEEDBACK.md` is write-only. No spine step reads
   prior entries; run N+1 starts as ignorant as run 1. The verifier checks placement,
   not substance — a "went fine" entry passes.
3. **Project handoff.** "Recurring entries are evidence for a Charter refresh" is
   stated but nothing counts recurrence or triggers the refresh. Template Update
   Candidates have no follow-through check.
4. **Skill-level (cross-project).** No channel at all. Lessons learned in a consuming
   repo never reach this repo. The skills can't improve from field use except when a
   human manually carries the lesson over.

Summary: we capture at one tier, enforce only existence, and consume at zero tiers.

---

## 2. Survey — what others do

- **Reflexion** (Shinn et al.): verbalized lessons from failures stored in episodic
  memory; the *next attempt is conditioned on the reflection*. The memory is a lesson,
  not a log. Key import: capture is worthless without a forced read path.
- **Voyager** (Wang et al.): successful solutions are banked as reusable skills, but
  only after *execution-validated* success, indexed for retrieval. Key import:
  lessons need provenance and validation before they become doctrine.
- **ACE — Agentic Context Engineering** (Stanford/SambaNova/Berkeley, arXiv:2510.04618):
  contexts as evolving playbooks with three roles — **Generator** (does work, emits
  trajectory), **Reflector** (distills insights), **Curator** (merges itemized delta
  updates into the playbook). Explicitly warns against wholesale rewrites
  ("context collapse") and against unbounded accumulation; uses per-item
  helpful/harmful counters and pruning. This maps almost 1:1 onto crew/Commander/Charter.
- **"Lessons Learned" multi-agent framework** (arXiv:2505.23946): agents deposit
  lessons into a shared bank; a selection step decides which lessons enter the next
  agent's context. Key import: lesson *selection* is its own problem — injecting
  everything is as bad as injecting nothing.
- **Compounding Engineering** (Every/Boris Cherny pattern): every correction gets
  codified into CLAUDE.md / slash commands / hooks so it never recurs; PR review
  comments feed the loop. Weakness in the wild: CLAUDE.md bloat without curation —
  same context-collapse failure ACE names.
- **Community self-improving-agent setups** (lessons.md + Stop hooks): correction →
  rule appended to lessons.md → SessionStart injects it. Simple, works, rots without
  a curator.

Convergent design principles:

1. **Every memory needs a reader.** Write-only retrospectives are theater.
2. **Separate the log from the playbook.** Append-only raw signal (cheap, honest) vs.
   curated distilled lessons (small, injected into context). Distillation is a
   deliberate step, not a side effect.
3. **Delta curation, not rewrites.** Add/amend/retire individual lessons; track
   whether a lesson helped; prune dead ones.
4. **Capture at the point of pain, curate centrally.** The worker emits raw
   reflection; a higher tier distills. Don't make the implementer write doctrine.
5. **Validation before promotion.** A lesson becomes binding context only after it
   recurs or is confirmed — mirrors our existing decision-candidate → decision-anchor
   pattern, which is the same shape applied to architecture.

---

## 3. Proposed framework

One capture grammar, four consumers. A **lesson candidate** is a structured item:

```
- scope: handoff | commander | project | constellation
  observed: <exact step/field/instruction that was ambiguous, missing, wrong, or improvised around>
  cost: <what it caused — rework, rediscovery, wrong assumption>
  proposal: <concrete change, if known>
```

The `scope` field is the router. Everything below reuses it.

### Loop 1 — Crew → Commander (per dispatch)

- Add a `## Workflow Feedback` section to `IMPLEMENTER_RESULT.template.md` and
  `REVIEW_RESULT.template.md`: handoff fields that were ambiguous/missing/wrong,
  context rediscovered that anchors should have carried, instructions improvised
  around. One line each, "none" allowed but the section is mandatory.
- Add the matching ask to the `Return Format` section of both handoff templates and
  one line to the Implementer/Reviewer SKILL.md prompts ("you are the only one who
  saw this friction; report it or it's lost").
- Commander's `gN-integrate` instruction gains: harvest crew Workflow Feedback into
  the run's lesson-candidate pool (alongside the existing decision/triage pools).
- Enforcement: extend the result-artifact check in `run_crew.py` (or a sibling
  verifier like `verify_agent_feedback.py`) to require the section's presence.

### Loop 2 — Commander across runs

- Split the durable store: keep `.agent-work/AGENT_FEEDBACK.md` as the append-only
  log; add `.agent-work/LESSONS.md` as the curated playbook (small, itemized lessons
  with scope tags and a `confirmed: <n>` recurrence counter).
- Spine `context` step gains a read: load `LESSONS.md` (and skim undigested log
  entries) before `understand`/`plan`. This is the Reflexion move — condition the
  next run on prior reflections.
- Spine `feedback` step gains distillation: append the raw entry as today, then do a
  **delta** update of `LESSONS.md` — new lesson, increment a recurring one, or retire
  one contradicted by this run. Never rewrite wholesale (ACE context collapse).
- `verify_agent_feedback.py` extends to check `LESSONS.md` exists/durable and that
  the entry isn't content-free (e.g., reject entries whose friction + improvement
  sections are all "none"/empty — crude, but kills "went fine").

### Loop 3 — Project handoff (Charter as Curator)

- Threshold trigger: when a lesson's `confirmed` count crosses N (start: 3), or
  undigested log entries exceed M, the `feedback` step surfaces a **Charter refresh
  recommended** user-decision instead of silently continuing. Charter is the only
  role with authority to fold lessons into ORCHESTRATOR_CONTEXT / CREW_CONTEXT /
  engine config; Commander only nominates.
- Template Update Candidates table gets a follow-through check: closeout verifier
  fails if any row has disposition left as placeholder.

### Loop 4 — Skill fold-in (cross-project, the recursive part)

- Lessons tagged `scope: constellation` (about the skills/templates/engine
  themselves, not the project) are exported by the `feedback` step into
  `.agent-work/CONSTELLATION_FEEDBACK.md` — same durable-placement invariant.
- In **this repo**, a periodic "metabolize" workflow (a normal Commander run, or
  `github-triage` issues filed from collected exports) consumes those files from your
  projects and turns them into skill/template edits. The skills repo improves using
  its own machinery — that's the recursion, and it keeps a human at the merge gate,
  which is the safety valve every survey source ends up needing.
- Practical transport (you run a handful of local projects): a small
  `scripts/collect_feedback.py` that sweeps known project roots for
  `CONSTELLATION_FEEDBACK.md` and opens issues here. `--file-issues` turns open,
  validated (recurring) findings into a GitHub-issue backlog in this repo, gated:
  it dry-runs by default and files nothing until `--confirm`; a local ledger
  (`.agent-work/CONSTELLATION_INBOX.json`) keys on the finding fingerprint so
  re-runs never duplicate. The *update* half (commenting on an existing issue when
  a finding recurs further) is still to come — it pairs with the recurrence-debt
  semantics so a recurrence reads as unpaid debt, not fresh confirmation.

### Where Claude Code hooks fit (and where they don't)

The spine engine already enforces ordering via postconditions — for Commander runs,
prefer engine postconditions over hooks (versioned with the skill, testable, visible
in the checklist). Hooks earn their keep where the engine isn't running:

- **SubagentStop**: verify a dispatched crew result contains `## Workflow Feedback`;
  warn into the transcript if absent. Covers the gap that subagents don't drive the
  spine.
- **SessionStart** (consuming projects, via Charter-seeded `.claude/settings.json`):
  inject the `LESSONS.md` digest so even ad-hoc non-Commander sessions inherit
  lessons.
- **Stop/SessionEnd** (consuming projects): if the session touched `.agent-work/`
  but no feedback entry was appended, nudge — catches abandoned/interrupted runs,
  which the spine can't see by definition.

### Sequencing

1. Loop 1 (template + prompt edits, verifier extension) — cheapest, immediate signal.
2. Loop 2 read path + LESSONS.md — makes the existing log stop being write-only.
3. Loop 4 export + collect script — start accumulating cross-project signal early
   even before the metabolize cadence is settled.
4. Loop 3 thresholds + hooks — once there's enough volume to tune N and M.

---

## 4. Refinements from discussion (2026-06-10)

Three intertwined threads from the human, with design responses.

### 4.1 Tone: mandatory engine, free judgment

The strong language exists because the skills run on mixed-capability agents; the
mandate must survive a weak model. The fix is not softening — it is **scoping the
mandate precisely**:

- **Mandatory, no exceptions:** every step goes through the engine; checkpoints are
  driven, attested, never hand-edited around. This language stays absolute.
- **Free:** judgment *within* a step — how to implement, what to explore, what
  evidence to gather beyond the floor.
- **Compliance, not deviation:** when the engine or an instruction does not fit the
  work, do the closest compliant thing and report the misfit in Workflow Feedback.
  State this explicitly in each skill, one sentence: *"Reporting that an instruction
  did not fit your work is compliance, not deviation."*

This dissolves the tension in §"survey" without weakening the mandate: the rule was
never "don't think," it was "don't skip the engine."

### 4.2 Admiral + Lessons Auditor (two new skills)

Field evidence: the f1brainz fleet runs (epics #378, #372) and
`admiral-playbook.md` in that project's memory. The playbook is a working,
hand-curated lessons file — delta-updated in-run, recurrence-validated, with
corrected revisions. It validates the whole framework empirically and is the seed
corpus for the skill.

**`constellation-admiral`** — epic-level delegate above Commander. Framework layer
(the skill) distilled from the playbook:

- Roles: Admiral dispatches/adjudicates/merges/logs, never commands an issue itself;
  Commanders = one per issue, isolated worktrees; crews per Commander doctrine.
- Launch-order template (the Admiral's handoff artifact): pasted prior-wave verdicts
  (pointers are weak, commanders start cold), pre-rulings marked overridable,
  honest-null clause, assigned findings file (one writer per doc per wave), stop
  conditions, return shape, data-location notes for untracked files.
- Wave/checkpoint protocol: present at checkpoints by default, run ahead only on
  explicit user clearance; gate merges on check exit codes; hold rebases to wave
  boundaries; stop-and-relaunch over mid-flight steering.
- Incident drills: the three kill vectors (turn-ending/background traps, plan
  session limits, host process exit), continuation-into-worktree recovery,
  TaskStop-before-continuation rule.
- **ADMIRAL_LOG as a first-class artifact** (rulings, incidents, merges, errors
  owned) — it is the Lessons Auditor's primary input.
- Closeout bookend: lessons-learned audit + architecture audit, mandatory. This is
  what moves "we observed something" to "we should do something."

Project decoration carries only genuinely local items; note that most of the current
playbook's "technical invariants" are platform/harness lessons (constellation- or
platform-scoped), not f1brainz lessons — evidence that scope-routing matters.

**`constellation-lessons-auditor`** — ACE's Reflector as a bounded Constellation
role, run as a **subagent with fresh context** at Admiral closeout (and optionally
at Commander `feedback` for heavy runs). Fresh context is the point: the agent that
lived the run is attached to its own narrative; a cold reader holding only the
artifacts (admiral log, AGENT_FEEDBACK entries, crew Workflow Feedback, closeout
tables, incident records) is the cheap defense against context collapse. Output: a
list of **scoped lesson candidates** — each with `scope`, observed/cost/proposal,
recurrence evidence, and a routing disposition:

| Scope | Routes to |
|---|---|
| `handoff` | project template delta (edit local template now) |
| `commander`/`admiral` | project LESSONS/playbook delta |
| `project` (doctrine) | Charter refresh nomination |
| `constellation` | export channel back to the skills repo (§4.3) |
| stale/contradicted | retire an existing lesson |

The auditor *nominates*; promotion authority stays where it lives (Charter for
doctrine, human for skill-repo merges). Survey grounding: this is the
Generator/Reflector/Curator split with the Reflector finally given its own context
window, plus the selection discipline of the lesson-bank work.

### 4.3 Install model: versioned templates, three-way reconcile, message-back

Premise (agreed): **the project's templates are its playbooks.** ~80% of lessons
land as template deltas; the skill stays a framework that establishes bounded roles
and lets the project decorate. The line to protect: framework in the skill,
decoration in the project.

Mechanism — treat installed templates like a vendored dependency:

1. **Version-stamp every template** at the source: a header field
   (`constellation-template: IMPLEMENTER_HANDOFF v7` + content hash; json field for
   .json templates). Installer writes `.agent-work/templates/TEMPLATES_MANIFEST.json`
   recording, per template: name, baseline version, baseline hash.
2. **Keep the pristine baseline** alongside the working copy
   (`.agent-work/templates/.baseline/`). Then two diffs are always computable:
   - **local vs baseline** = the project's accumulated lessons, machine-readable.
     This diff *is* the project playbook delta — it makes the 80% legible instead
     of being silently smeared into edited files.
   - **baseline vs upstream** = what the skill learned since install.
3. **Refresh = three-way merge** (`git merge-file` semantics: baseline-old,
   baseline-new, local). Clean hunks apply silently; conflicts mean the skill and
   the project learned different things about the same field — exactly the cases a
   human (or Charter) should adjudicate, and exactly the signal §4.4 wants.
   A `scripts/check_skill_freshness.py` compares manifest versions against the
   installed skill and nags at Commander `init`/`context` (cheap staleness check,
   answers hiccup (a)).
4. **Message-back channel (the ~5%)**: lessons the auditor scopes `constellation`
   are appended to `.agent-work/CONSTELLATION_FEEDBACK.md` with template name +
   baseline version (so this repo knows which vintage the lesson was learned
   against). Existing proof of need: f1brainz's `constellation-engine-quirks.md`
   holds ~10 engine/skill-level lessons (verb asymmetries, cp1252 crash,
   un-invokable `compact` step) that never reached this repo and will be relearned
   by every project until loop 4 exists.

Boundary rule that keeps the framework line clean: **upstream merges only structure
and role contracts; project deltas that are domain content never flow up.** A
conflict where the project hardened a field upstream wants to change is a
disagreement between two learning processes — surface it, never auto-resolve.

### Revised sequencing

1. Tone scoping pass over the skill prompts (§4.1) — small text edits.
2. Template version stamps + install manifest + baseline copies (§4.3 items 1–2) —
   prerequisite for everything that reconciles.
3. `constellation-admiral` skill distilled from the f1brainz playbook + log.
4. `constellation-lessons-auditor` skill; wire as Admiral closeout step and optional
   Commander `feedback` enhancement.
5. Refresh/three-way merge tooling + freshness check.
6. `CONSTELLATION_FEEDBACK.md` export + collect script in this repo.

Open questions for the human:

- Lesson-candidate scope vocabulary: is `handoff|commander|admiral|project|constellation`
  the right cut, or should `charter` be distinct from `project`?
- Should `LESSONS.md` injection be unconditional at `context`, or selected per
  mission frame (the lesson-selection problem from arXiv:2505.23946)? Start
  unconditional while the file is small; revisit at ~30 lessons.
- Metabolize cadence for this repo: scheduled, or manual when you feel weight?
### 4.5 Admiral spine (ruled 2026-06-10)

Three steps — **latitude → execute → closeout** — driven through the engine, with
enforcement concentrated at the bookends and the middle deliberately free. Same
shape as the Commander's architecture bookend: rigor at the edges, judgment between.

**1. `latitude`** — confirm authorization and understanding with the user before
anything launches. Sometimes the human has no strong opinions; sometimes they do.
Reuse `constellation-interrogator` here (it exists for exactly this). Output is a
**LATITUDE contract** artifact (template), covering at minimum:

- Epic intent and success shape; honest-null acceptability.
- Checkpoint protocol: default stop-and-present at wave boundaries vs. cleared to
  run ahead (and through which checkpoint).
- **Decision classes**: which kinds of choices the user wants surfaced vs. delegated
  — architecture, scope changes, merges to main, issue filing, spend/budget,
  production-default changes. This is the dial between "I don't care, go" and
  "float me the details."
- Float-up routing: when a Commander returns a `user-decision`, the contract tells
  the Admiral whether it may adjudicate (within delegated classes, logged as a
  RULING) or must escalate. This is the mechanism for "discuss details the
  commander floats" without hardcoding either behavior.
- Comms style, model/budget parameters, pre-rulings on foreseeable ambiguities.

Postcondition: latitude contract confirmed by user (engine-checked user-decision).

**2. `execute`** — relatively unconstrained: "do what ya gotta." One long engine
task, not gates. The operating rules and technical invariants from the playbook are
doctrine the Admiral carries, not engine gates. Two hard requirements only:
**ADMIRAL_LOG is maintained as the run's audit trail** (rulings, incidents, merges,
errors owned — it replaces gate structure as the accountability surface), and the
latitude contract is honored (escalations per decision class).

**3. `closeout`** — engine-enforced postconditions, the recursive-improvement
bookend:

- Lessons Auditor subagent ran over the artifacts; every candidate has a routed
  disposition (template delta / playbook delta / Charter nomination /
  constellation export / retire / drop-with-reason).
- Playbook + project template deltas applied; constellation-scoped items exported.
- Architecture audit/reconcile complete (Cartographer over the epic's net change).
- Repo hygiene: branches merged or dispositioned, worktrees swept, admiral log
  archived to main, feedback invariant verified.
- Epic summary presented; user acceptance.

**Ruled:** pristine baseline lives at `.agent-work/templates/.baseline/`.

---

## 5. Review findings and accepted revisions (2026-06-10)

Two independent lower-tier reviews (source-fidelity vs. the cited literature;
red-team over the mechanisms grounded in repo files). Convergent verdict: **the
design captures signal well but trusts it too much.** The learning layer must obey
the same doctrine as the work layer — evidence-cited claims, independent
verification, deterministic application, bounded authority. Accepted revisions:

### 5.1 Ground lessons in engine telemetry, not prose alone (severity 1)

Every cited source's gains depend on an external execution signal (Reflexion:
pass/fail; Voyager: game-state verification; ACE: API success; LessonL: measured
speedup). Prose retrospectives alone put us in the intrinsic-self-correction regime
where the literature (Kamoi et al., TACL 2024, arXiv:2406.01297) finds no reliable
gains. **But Constellation already has execution signals the design ignored:**
`rework_count` per task, BLOCK verdicts, waives/forced overrides, re-dispatches,
crew-run metadata, incident entries. Revisions:

- Every lesson candidate must **cite a grounding artifact line** (feedback entry,
  log line, engine state). No citation → confabulation → discard.
- Recurrence splits into `mentions` (raw count) and `confirmed` (validated), plus a
  symmetric `disconfirmed` counter. Confirmation requires corroborating telemetry
  (e.g., the friction co-occurs with rework/BLOCK/waive events), a fresh-context
  reader, or the human. `confirmed:5, disconfirmed:3` → Charter review, not silence.

### 5.2 Deterministic playbook merge — LLM proposes, script applies (severity 1)

ACE's Curator merges deltas with *non-LLM logic*; the design had the run's own
Commander LLM-editing LESSONS.md — Generator and Curator collapsed, the exact
failure the Reflector split prevents. Revision: the LLM (auditor or Commander)
emits structured operations — `ADD` / `AMEND <id>` / `RETIRE <id>` with
justification and grounding citation — and a script (`apply_lessons_delta.py`,
sibling of `verify_agent_feedback.py`) applies them mechanically, enforcing cap,
uniqueness, and counter rules. The LLM never writes the playbook directly.

### 5.3 Hard-bounded playbook with dormancy (severity 2)

Reflexion bounds memory at 1–3 reflections; ACE prunes; "revisit at ~30" had no
grounding. Revisions: hard cap (start 15–20, enforced by the apply script);
retire-before-add beyond the cap; `last_confirmed_run` field; lessons unconfirmed
for N runs are auto-deleted (no dormant section), except `constellation`-scoped debt, which is pinned until explicitly retired. Selection filter at
`context`: inject by `scope` overlap with the mission frame.

### 5.4 Anti-boilerplate floor on Workflow Feedback (severity 2)

All-"none" sections pass every current check. Revisions: a "none" answer requires a
run-specific reason (`confirmed none after review: <reason>`); verifier rejects the
all-literal-"none" block; template asks the specific question first ("what concrete
wording in this handoff confused you?") before the open-ended one.

### 5.5 Concurrency isolation for learning artifacts (severity 2)

Parallel Commanders under an Admiral share `.agent-work/AGENT_FEEDBACK.md` and
LESSONS.md with no locking. Revision: each run writes a per-work-id sidecar
(`AGENT_FEEDBACK.<work-id>.md` or in-work-area staging); consolidation into the
durable log and any LESSONS delta is serialized at a single point (Admiral closeout
when fleeted; Commander `feedback` when solo). Also kills cheap counter inflation
from one run repeating itself.

### 5.6 Versioning corrections (severity 2)

- Blank templates vs. filled instances: stamps/hashes are coherent on **blanks
  only**. Note honestly: today most project adaptation lives in fills and practice,
  not blank edits — the loop's *job* is to convert recurring fill-level practice
  into blank-template edits, which is what makes the local-vs-baseline diff grow
  into the legible playbook. Until then the diff under-measures lessons.
- Migration: first run with versioning generates the baseline from the
  currently-installed file, stamped `baseline-from-install`, manifest flagged for a
  freshness audit.
- `install_constellation.py` must become manifest-aware: on (re)install, refresh
  baseline copies + hashes; never leave the manifest stale after a `--force`.

### 5.7 Latitude contract: expiry + out-of-taxonomy class (severity 3)

Contracts go stale mid-epic and taxonomies never cover everything. Revisions:
`expires` field (time or event, e.g. "after wave 2 merge") forcing a refresh
user-decision; an explicit **out-of-taxonomy** decision class that always escalates
with a one-line "why this didn't fit" — unclassifiable decisions become visible
instead of absorbed into "do what ya gotta."

### 5.8 Auditor hardening + cost gating (severity 3)

- The auditor reads artifacts written by agents who knew they'd be audited
  (performative legibility bias) and lacks run-tacit knowledge. Revisions: auditor
  receives a compiled **run brief** (epic intent, which templates are
  project-customized per the manifest diff, model tiers used); every routing
  carries `confidence: high|medium|low`; low-confidence routings queue for human
  review instead of propagating.
- Cost: for solo-dev scale, the fresh-context auditor is mandatory only at Admiral
  closeout; for plain Commander runs it triggers when LESSONS.md > 5 entries or on
  request — otherwise the closeout self-audit checklist suffices. Loop 1 + the log
  (cheap, immediate) are never cut.

### 5.9 Scope-transfer honesty (accepted with pushback)

The literature shows no cross-domain lesson transfer — but that critique applies to
*task-content* lessons. Most Constellation lessons are about the shared machinery
(engine verbs, handoff fields, spine steps), where the "domain" is literally the
same artifact across projects — f1brainz's engine quirks transfer because the engine
is identical. Revision: lesson candidates carry a `task-class` tag
(`general-workflow` vs. domain-specific); only `general-workflow` and
matching-class lessons inject cross-context; domain-tagged lessons stay local.
Cross-project imports remain human-triaged.

### 5.10 Citation correction

The "Boris Cherny / CLAUDE.md corrections" attribution traces to secondary
reporting (MindStudio blog quoting Cherny), not the every.to guide; the bloat
failure mode is our inference by analogy with ACE, not a practitioner-reported
finding in that source. §2 wording stands corrected accordingly.

Dogfood note: both reviewers returned Workflow Feedback sections on their own
handoffs and both produced real signal (exploration-scope ambiguity; missing
cross-repo authorization; full-text URLs vs. arXiv IDs) — first live confirmation
that Loop 1 yields non-boilerplate feedback when the ask is specific.

Remaining open questions:
