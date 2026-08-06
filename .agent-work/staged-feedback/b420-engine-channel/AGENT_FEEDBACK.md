# Agent Feedback Log (staged — fenced write, see FENCE.md)

## 2026-08-05 — b420-engine-channel

**Run shape:** `commander (delegated)` · `10/10 spine steps closed (init through review; archive in progress)` · `Sonnet throughout (implementer, reviewer, 1 cold plan critic, all Sonnet per launch order budget)`

**Instruction adherence:** `minor deviations`
- Followed the spine/execute.json gate mechanics exactly: claimed lease, drove every step through
  `current`/`start`/`attest`/`advance`, no hand-edited JSON, no skipped gate.
- Deviation: sent the implementer a rework request via `SendMessage` to its own `agentId` rather than
  a formal engine `reopen`, because the defect surfaced during my own re-verification BEFORE I had
  advanced `g1-implement` at all — there was no completed gate to reopen yet, so `reopen` didn't
  apply. This felt like the right call (the crew's own internal plan still went through a proper
  `reopen`/rework cycle on ITS OWN plan file), but the doctrine doesn't name this exact shape
  ("found a defect in a not-yet-integrated result, still addressable by SendMessage") — worth a
  named pattern if it recurs.

**Friction / unclear:**
- `docs/agents/engine-config.json` doesn't exist in this repo (referenced by every spine/execute.json
  template's `config_ref`); the engine silently falls back to defaults (`load_config` returns `{}`
  on a missing file, no error). Harmless here, but a missing-vs-empty distinction would have been
  reassuring — I had to read `load_config`'s source to confirm this was intentional-graceful, not a
  silent misconfiguration.
- The `render_human()` docstring's own citation of `tests/test_checklist_engine.py:818` for the
  byte-exact ACTIVE-line pin was STALE (line 818 is an unrelated `require_session` lease test; the
  real pin is `GoldenOutputBriefing`, ~3779). This is exactly the "check that cannot fail" family in
  reverse — a citation nobody re-verifies drifts silently as the file grows. Fixed in this run's diff.
- `py` vs `python` on this Windows worktree: `py` resolves to an interpreter with no `pytest`
  installed; `python` has pytest 9.0.2. `_COMMON.md`'s platform invariants say "both `py` and
  `python` work" — true for the engine CLI itself, not true for running the test suite. Cost one
  failed command before I found the working interpreter.

**Crew-reported friction:**
- Implementer: none of substance in the handoff itself — called it "unusually complete," noting the
  handoff's scope-discipline clause on partial/negative results pre-empted exactly the ambiguity it
  hit when it discovered `directives` shared the unrendered-field defect class.
- Implementer: the concrete `anchors` shape (dict-of-list vs. dict-of-string vs. flat-list) had to be
  derived from a corpus grep because the handoff said "real corpus content" without naming the exact
  shapes — worth citing concrete shapes directly in a future handoff's Map Anchors section when a
  Commander has already done that inventory (I had; I should have put the three shapes in the
  handoff verbatim rather than just "real corpus content", and I initially only listed two of the
  three — the implementer's own first-pass miss on the third shape traces partly back to that gap in
  my handoff, not just to insufficient testing on the implementer's side).
- Reviewer: none of substance — "handoff unusually thorough... named the exact load-bearing shape to
  reproduce." No rediscovered context, no improvised instructions worth flagging.

**What worked:**
- The cold-plan-critic-before-approval mechanism earned its keep here: it caught a real, load-bearing
  design flaw (blanket dedup would have been false on 5 of 6 RAIL_VERBS) BEFORE any code was written,
  cheaply, in a single Sonnet dispatch — the alternative (finding it at review or in production) would
  have cost a full implement→review→rework cycle instead of a plan-time correction.
- Independent re-verification at gate-integrate genuinely caught a real defect the implementer's own
  (reasonably thorough) test suite missed: the dict-of-string anchors shape. Re-running the exact
  reproduction myself rather than trusting the pasted evidence is what caught it — this is the
  "verify claimed side-effects against the world" doctrine paying for itself concretely, not just as
  a checkbox.
- The rework round-trip via `SendMessage` to the still-live implementer agent (rather than a fresh
  dispatch) was fast (~3 minutes) and preserved full context — the implementer didn't need to be
  re-briefed on anything, it went straight to reproducing my counter-example and fixing it.

**Improvement signals:**
- When a Commander has already done a corpus-shape inventory before authoring a handoff, put the
  concrete shapes (not just "real corpus content, verified") directly in the handoff's Map Anchors or
  Constraints section → disposition: applied this run partially (added shapes to the REWORK message,
  should have been in the ORIGINAL handoff) — noted here as the concrete instance; not distilled to a
  durable lesson because this is a single Commander's own authoring discipline, not a template/doctrine
  gap (`grade: settled — a one-off self-correction, not a recurring pattern yet`).
- `render_human()`'s docstring line-citations for pinned tests are a live hazard (drift silently as
  the file grows, discovered only by manual verification) → disposition: distilled to a lesson (see
  lessons-delta.json) — this is a recurring-shape risk (any docstring citing a line number in another
  file), not a one-off, so it goes to the bank rather than being applied as a one-off doc fix here.

---
