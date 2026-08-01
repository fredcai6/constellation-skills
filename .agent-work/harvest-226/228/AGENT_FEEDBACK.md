# Agent Feedback Log (staged — fenced from the durable main-checkout log)

Staged per `constellation-commander-delegated`'s fenced feedback/archive closeout
convention: LAUNCH_ORDER-228.md's Data Locations section marks the main
checkout's `.agent-work/` tree read-only for this Commander, so this entry
cannot be appended directly to the durable `AGENT_FEEDBACK.md`. See `FENCE.md`
in this directory. The Admiral harvests this trio into the shared durable root.

---

## 2026-07-24 — 228

**Run shape:** commander (delegated) · execute (e0-context, g1-implement,
g1-review, g1-integrate), reconcile, triage, review, feedback · sonnet
throughout (no Fable at any tier)

**Instruction adherence:** fully followed, with one continuation wrinkle: I am
a continuation Commander who took over this work-id mid-run after a
predecessor stall (confirmed stopped by the Admiral). The predecessor had
already driven e0-context and g1-implement to completion, and was mid-review
(r0-context/r1-handoff recorded pass, r2-scope in-progress) when it stopped. I
force-reclaimed the lease on **both** `spine.json` and the nested
`g1-review/review.json` child checklist (two independent leases, not one — a
survey child checklist under a gated parent carries its own lease), then drove
r2-scope through r6-fowler, consolidated the review (APPROVE), completed
g1-integrate, and drove reconcile/triage/review/feedback myself.

**Friction / unclear:**
- `checklist_engine.py advance <gate> --from-child <path>` refused a
  **relative** path to the child checklist file ("child checklist ... not
  found") but accepted the same path given absolute — worth documenting
  explicitly in the engine's own `--help` text or the commander doctrine, since
  every other engine invocation in this run accepted a relative
  `.agent-work/...` path fine.
- `advance execute --from-child execute.json` refused with "child ... has no
  consolidation yet" — a **gated**-type child checklist (execute.json) has no
  `consolidate` step/field the way a **survey**-type child (review.json) does,
  so `--from-child` only works one level down from a survey. I had to advance
  the parent's `execute` step with a plain `attest c1` + `advance` instead.
  The gate-execution doctrine text didn't call out this survey-vs-gated
  distinction for `--from-child`; a continuation Commander without prior
  exposure to the engine's internals could plausibly get stuck here.
- Discovered ~136MB of stray untracked debris in the worktree
  (`Python/` directory + a `python_install_*.log`) left by an earlier
  `py`-launcher invocation on this host that triggered the Windows Python
  Install Manager's auto-install flow (network fetch failed, partial state
  written to the worktree's cwd). Attempted to clean it up but the harness's
  auto-mode classifier blocked an `rm -rf` on it; left in place, untracked
  (won't be committed). Worth a triage candidate — see verdict.

**Crew-reported friction (harvested from g1-implementer-result.md's Workflow
Feedback):**
- The handoff's Required Evidence item 2 wording ("PATH-shadowing, or
  monkeypatch the exact subprocess boundary") correctly anticipated two
  techniques might be needed but didn't name the one that actually works on
  Windows (mutating ambient `os.environ['PATH']`, not a restricted `env=`
  override) — the implementer discovered this empirically and it cost ~10
  minutes. Distilled into a lesson candidate (see `lessons-delta.json`,
  `windows-subprocess-env-does-not-shadow-path-resolution`) rather than fixed
  now, since this is a first observation on one host/Windows build.

**What worked:**
- The `--from-child` consolidation-attach pattern (once the absolute-path and
  survey-vs-gated wrinkles above were worked around) correctly threaded the
  review survey's verdict/summary into the parent gate's evidence without
  hand-typed duplication.
- Forced lease takeover (`claim --force --reason ...`) worked cleanly on both
  the parent spine and the nested review child checklist, and both leases'
  prior-session provenance is preserved in the journal for anyone auditing the
  continuation later.
- The Fowler-pass rail (`verify_fowler_pass.py`) caught nothing wrong with my
  first record and gave genuine, non-rubber-stamp signal (2 real flags out of
  12 smells, both correctly judged non-blocking) rather than being a checkbox
  exercise.

**Improvement signals:**
- `--from-child`: accept a path relative to the checklist file's own directory
  (or the invoking cwd) the same way every other engine verb does, or document
  the absolute-path requirement explicitly in `--help`. → disposition: distilled
  to lesson candidate below (not applied now — single occurrence, need to see
  if it recurs before touching `checklist_engine.py`, which is also fenced
  from me this wave per #227's ownership).
- `--from-child` on a gated-type child: either support attaching a gated
  child's terminal state (not just a survey's `consolidation`), or document
  that `--from-child` is survey-only in the gate-execution doctrine text so a
  continuation Commander doesn't have to discover the distinction by trial and
  error. → disposition: needs user/Admiral decision (touches
  `checklist_engine.py`, fenced from me this wave).
