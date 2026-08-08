# Cold plan critic — w3a-465

Ran on MISSION_FRAME.md + plan-alternatives.md + execute.json, with source access limited to the
files whose behaviour the plan asserts. No authoring context, no launch order, no issue text.
Single critic, not a panel — panel-vs-single surfaced to the Admiral in the return.

**Verdict: plan sound.** Both central factual claims verified true in source. Recommendation
survives the strongest attack the critic could mount. 19 findings, triaged below.

## Adopted into the plan before it froze

| # | Finding | Change made |
|---|---|---|
| 4 | `amend` requires `--authority`/`--reason`; the plan never said what they mean when a reviewer retexts its own check. Two bad exits: invent an authority string (cheapening `authority` everywhere) or block on every fill. | g1-implement now requires the prose to state it: authority is the dispatching Commander, named in the handoff, never invented. |
| 5 | The safety argument rests on `amend`'s `amendments` audit trail, and nothing was asked to read it. | g1-review must inspect `amendments` on the returned survey. |
| 6 | The untaken road was rejected for the wrong reason — substitution is additive, widening a verb's type guard is semantic. | plan-alternatives corrected; the ruling holds on a different axis (the residual). |
| 7 | Candidate B and C are not exclusive; naming only the repair verb makes the exceptional route read as the documented route. | g1-implement now requires BOTH paths named: resolve at instantiation (normal), `retext-check` (repair). |
| 9 | The CRLF fixture was described as non-discriminating, so an implementer might drop it — but it is the only guard against the "always write LF" over-correction. | Both fixtures now required, each with its stated job. |
| 10 | Three test shapes that cannot fail: LF fixture built with `write_text` (born CRLF on Windows); asserting on `read_text` (universal newlines make it vacuous); asserting saved bytes equal fixture bytes (`indent=2` re-serialises). | All three named and forbidden in g1-implement; assertions must be on `read_bytes`. |
| 11 | Exactly one fixture can be observed red on any one platform. | Both gates must name which fixture, on which platform. |
| 12 | **The gate structure could not fail.** `g1-implement`'s only check was "an IMPLEMENTER_RESULT exists"; `g1-integrate`'s was `pytest -q tests`, green on a suite that never gained the new tests. The frame invoked the two-bin rule to save `r6-fowler`'s check and the same rule convicted this gate. | `g1-integrate` c1 now names the four new test node ids explicitly, then runs the full suite. A missing test is a red gate. |
| 14 | c1 claimed "no engine write changes line endings", broader than the change: the journal append near line 2762 is also text-mode. | Statement narrowed to `save()`; line 2762 raised as a triage candidate. |
| 15 | Two decision grades were `settled/observed` on evidence the implementing gate is supposed to produce. A decision cannot be settled by the gate meant to constrain it. | Downgraded to `settled/read`; frame claims restated as not-yet-run with the receipt path they owe. |
| 16 | "Fixes the interrogator's defect" overclaimed — lifting the op makes the fix *available*, not applied. | Corrected to "available, not applied". |
| 17 | "A survey has no gates to replan" is a design choice dressed as a fact. | Owned as a conservative choice; the refusal message must say so. |
| 19 | `save()`'s new contract is undefined for a file that does not exist yet, or one with mixed endings. | Default stated: LF. |

## Noted, not adopted

- **#13 — the interface change is made before the Admiral answers.** Real objection: nothing in this
  structure pauses before widening a shared verb. Not adopted because LAUNCH_ORDER rules it
  directly: *"Do not treat that as a blocker; proceed and flag it."* The Admiral pre-accepted the
  ordering. Recorded here so the objection is not lost if that ruling is revisited.
- **#13, second half — the bundle mixes one high-blast-radius change with two local ones.** A BLOCK
  on any one returns all three. Accepted as a deliberate cost: the imperative rewrite is only true
  once the affordance exists, so splitting them would ship a gate whose prose lies until the next
  gate lands.
- **#1 (bonus), #18** — informational. #1: the unfilled placeholder fails as a *bash parse error*
  (`<foo>` is a redirect with no target), not as a clean check verdict, so the reviewer sees a
  confusing message. Worth knowing when writing the red capture. #18: the critic was fenced out of
  `docs/CHECKLIST_SCHEMA.md`; `consolidate()`'s own error text corroborates independently.
