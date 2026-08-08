# Triage recommendations — issue #465 (epic #418 wave 3, W3-A, delegated run)

Authority note: delegated run under Admiral launch order LO-465. The spine's `triage` gate
imperative gives the delegated-mode recipe directly: satisfy c2 ("user approved issue creation")
by attaching a `user-decision` evidence item citing the launch order's `Inherited Latitude`
clause. Filing follows the repo's standing instruction that Commanders file to the tracker rather
than banking findings worktree-locally for later harvest. All seven candidates below came from
`execute.json`'s `triage_candidates` (`tc1`-`tc7`), sourced from `RESULT.md` section 7 —
not re-derived.

None qualified for `fixed-now`: every candidate touches a file outside this run's fence
(`scripts/checklist_engine.py`, `skills/reviewer/**`, and the two ratified doc extensions) or was
explicitly scoped out of gate g1 by the plan.

## tc1 — interrogator zc-consolidate mirrors the reviewer's fixed placeholder/prose defect [filed]
- **Classification:** cleanup / missing doc
- **What:** `skills/interrogator/templates/INTERROGATION.template.json` `zc-consolidate` carries
  the identical placeholder defect and the identical open-fail prose claim #465 just fixed in the
  reviewer. Its template is already `type: survey`, so #465's engine fix already supplies the
  engine half; only the prose remains.
- **Filed:** https://github.com/fredcai6/constellation-skills/issues/494

## tc2 — engine journal append is still text-mode, same defect class as the fixed save() [filed]
- **Classification:** bug
- **What:** `scripts/checklist_engine.py`'s journal append (near line 2762) is still text-mode;
  same line-ending-churn risk `save()` had before #465's fix. Deliberately fenced out of g1's
  scope (scope was `save()` only).
- **Filed:** https://github.com/fredcai6/constellation-skills/issues/493

## tc3 — six repo JSON writers pass encoding but not newline [filed]
- **Classification:** bug / repo hygiene
- **What:** `collect_feedback.py:290,365`, `install_constellation.py:911,1182,1241`,
  `build_architecture_map.py:385` — against CREW_CONTEXT's always-pass-`newline` rule. Found by
  the same pass that found `save()`'s bug.
- **Filed:** https://github.com/fredcai6/constellation-skills/issues/495

## tc4 — CREW_CONTEXT's always-pass-newline rule doesn't name save()'s exception [filed]
- **Classification:** missing doc
- **What:** `save()` now satisfies the rule's intent (byte-faithful) more strongly than its
  literal mechanism (a fixed `newline=`) — the rule's prose doesn't say so, inviting a future
  "fix" that undoes #465. Same prose-contradicts-code class #465 fixed in
  `skills/reviewer/SKILL.md`, one tier up.
- **Filed:** https://github.com/fredcai6/constellation-skills/issues/496

## tc5 — amend() is a 215-line Fowler long-method [filed]
- **Classification:** cleanup / tooling
- **What:** `scripts/checklist_engine.py`'s `amend()` carries at least six op kinds in one
  function. Flagged, not overridden, by #465 (which extended it). `global-crew.md`'s
  "split a unit when its intent blurs" agrees with the smell.
- **Filed:** https://github.com/fredcai6/constellation-skills/issues/497

## tc6 — amend's type applicability is restated in six places [filed]
- **Classification:** cleanup / missing doc consolidation
- **What:** the gated-vs-survey applicability rule is restated across code and five doc/template
  sites rather than defined once and pointed at. #465's own first implementer return shipped
  missing five of the six prose sites — the reviewer caught it. The structure guarantees
  recurrence until consolidated.
- **Filed:** https://github.com/fredcai6/constellation-skills/issues/498

## tc7 — the {checklist_dir} substitution road (parked design possibility) [recommend-and-defer]
- **Classification:** unresolved decision / architecture weakness
- **What:** a `{checklist_dir}` substitution mechanism, named untaken in
  `.agent-work/w3a-465/plan-alternatives.md`, that would kill this whole "text-mode writer churns
  line endings" defect class corpus-wide. Additive, but doesn't fix the residual hand-editing case
  that drives the defect today.
- **Why deferred, not filed:** this is a cross-corpus architecture question (which writers get
  the substitution, how it interacts with `save()`'s new byte-faithful behavior, whether it's
  worth the surface area) that needs Explorer-grade shaping, not a bounded issue an implementer can
  pick up as written. It is already recorded as a `parked_possibility` in
  `.agent-work/w3a-465/REPLAN_INPUT.json`; this record cross-references that, it does not
  duplicate filing.
- **Evidence:** `.agent-work/w3a-465/RESULT.md` section 7, item 7; `plan-alternatives.md`.
