# Implementer Handoff — issue-304 gate g4: dogfood the edited spine, then close out

## Assigned task

Prove the contract works **in a real run of the edited template**, in the repo that is itself the
degraded common case, and then run the **full** suite.

Work ONLY in `C:/Programs/constellation-skills-wt/e298-304`. Never touch
`C:/Programs/constellation-skills` or `C:/Programs/constellation-skills-wt/e298-331`.
**Do not point any tooling at `C:/Programs/f1Brainz`** — `orient` WRITES a receipt into whatever
`--root` it is given, and that repo is read-only.

## Why this gate exists, in one line

g3 proved the deletion is pinned and the workflow still runs. **g4 proves the thing that was added
actually fires end to end in the shape a real Commander would meet it.** A contract that passes its own
unit tests but is never exercised through `init_work_area.py` → engine → command check is a capability
that ships inert — a pattern this project has hit six times in one epic (#345).

## STEP 1 — Materialize and drive

Materialize the **EDITED** `COMMANDER_SPINE.template.json` through `scripts/init_work_area.py` into a
scratch work-id in **this** repo, and drive it through the engine **far enough to execute the new
context command check end to end**.

This repo has `docs/agents/` but **no `docs/architecture/`**. That is not an edge case — it is the
**common case** the whole degraded arm was designed for, and it is why the dogfood happens here.

You must demonstrate, with the engine's own output captured verbatim:

1. **It REPORTS degraded rather than silently passing.** A silent pass is the failure mode this issue
   exists to remove.
2. **It does not deadlock.** The contract must be dischargeable: a legitimate degraded run declares
   substitutes, the unmapped gap, and an escalation, and then **proceeds**. If the only way past the
   context check is `--force` or a waiver, that is a finding and you must report it as one — a gate
   that cannot be discharged honestly is worse than the silence it replaced.
3. **The placeholders actually resolved.** `<commander-skill-dir>`, `<repo-root>` and `<work-id>` are
   template placeholders; a check whose command still contains a literal `<…>` never ran. Confirm the
   materialized `spine.json` carries a real absolute path, not the placeholder.

g3 already drove `init` and `context` once and captured 384 lines of engine output — read
`.agent-work/issue-304/TRIPWIRE_OUTCOMES.md` and `g3-result.md` first so you extend that evidence rather
than repeating it. **The delta g4 owes is the check firing from the *materialized* template**, which is
the path a real run takes and the path g3 did not isolate.

Use a scratch work-id you clean up afterwards. Do not disturb `.agent-work/issue-304/`.

## STEP 2 — The FULL suite

Run the **entire** suite, not a filtered subset:

```
cd C:/Programs/constellation-skills-wt/e298-304
python -m pytest -q
```

Roughly 1160+ tests, several minutes — **it has not hung**. Record the exact result.

**A local green is never the merge gate.** `python` here is 3.14; CI pins 3.12. Merge gates on the CI
check status read at source, and your Commander does that separately. Report the local number as a
local number.

If anything is red, report the failure verbatim and attribute it — do not summarize a tail. Derive any
distribution claim ("all N failures are in file X") from a command such as `uniq -c`, never by reading
the pytest tail; under-inclusive attribution has already cost this issue's lineage a rework round-trip.

## Allowed scope

Evidence capture and, if the dogfood exposes a **defect in the wiring**, the minimal fix for it. This
gate is expected to be mostly *demonstration*. If it turns into a large edit, stop and report — that
means the wiring is wrong and your Commander needs to know before you paper over it.

## Specific exclusions

- Do not re-open g1/g2/g3 work. All three are reviewed and closed.
- Do not rewrite `TRIPWIRES.md` — it is a pre-registration and rewriting it voids the pathway.
- Do not fix #341 (relative command checks), #342 (episode standings), #344 (stale installed corpus),
  #363, or #364.
- Do not modify `checklist_engine.py`.
- No bootstrap/`CLAUDE.md` stanza. **Ruled OUT** by the human: the map is orchestrator content.

## Constraints

- `python -m pytest`, **never** `py -m pytest` (`py` is 3.12 — CI's pin — with no pytest; `python` is
  3.14 with pytest). **No 3.13+-only APIs**: `Path.read_text(newline=...)` passed locally and cost 39
  CI failures on PR #320.
- Windows: write files with explicit `encoding='utf-8', newline='\n'`.
- Compare normalized content or blob OIDs, **never raw bytes** — `git status --porcelain` shows a
  phantom `M` from CRLF while `git diff --quiet HEAD` returns 0. Four agents in this epic have hit this,
  most recently on *writing* rather than reading; `git checkout HEAD -- <path>` plus a
  `hash-object`/`rev-parse` comparison is the reliable recipe.
- Commit as you go. Two agents on this issue died mid-gate on session usage limits and their work
  survived only because it had been committed.

## Required evidence

Paste verbatim:
- the materialized check command from `spine.json`, showing **resolved** placeholders;
- the engine's own output driving through `context`, showing the degraded report **and** the discharge;
- the full-suite result line;
- the exit code of the context check at each stage, since **stdout is discarded and the exit code is the
  only signal reaching the spine**.

## Stop conditions

Stop and report if: the context check cannot be discharged without `--force` or a waiver; a placeholder
fails to resolve; the dogfood requires a non-trivial code change; or the full suite is red for a reason
you cannot attribute.

Report **"this specific check failed"**, never "this approach is impossible." Never fabricate evidence.

## Return format

Write `IMPLEMENTER_RESULT` to `.agent-work/issue-304/crew-handoffs/g4-result.md` with evidence pasted
verbatim, every deviation and its reason, and any unresolved blocker. **Only claim a cleanup you have
verified** — one earlier result on this issue asserted a removal that had not happened, and another
reported an audit as complete when it had covered two of three items. Return thin.
