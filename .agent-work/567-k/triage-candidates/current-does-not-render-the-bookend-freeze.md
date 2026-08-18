# Triage candidate — `current` does not tell an agent a gate is frozen

**Not filed.** `decision:no-issue-filing-mid-run` — staged only.

## Observation

`bookend: true` now changes what `amend` will accept, but the engine's projection — what `current`
prints, which `global-everyone.md` calls "the complete gate briefing" and the **only** sanctioned
way to read spine state — does not mention it. An agent deciding whether to re-plan cannot see
which gates are frozen without opening `spine.json`, and opening `spine.json` to read state is
itself named a violation in that same doctrine.

So the freeze is discoverable only by attempting an `amend` and being refused.

## This was predicted, in writing, by the doc I just reconciled

`docs/CHECKLIST_SCHEMA.md`'s Rendering section describes `TaskFieldCompleteness`, the property
test that fails when a populated Task field goes unrendered — and names its own residual limit:

> a field introduced only by a template — carried in a shipped checklist JSON but built by neither
> the amend-task builder nor `append()` — is still invisible to the property and needs a human to
> add it to the fixture.

`bookend` is exactly that field. The full suite passed at `eb94b150` **because** the property
cannot see it, not because the field is rendered. This is a live instance of a
check-that-cannot-fail that the codebase had already documented and accepted.

## Candidate remedy

Render the frozen gates in `current` (one line, or a marker on the gate), and add `bookend` to the
`TaskFieldCompleteness` fixture so the property covers it from then on.

## Disposition

`recommend-and-defer`. Not taken this run for two reasons, both scope rather than difficulty:
rendering changes the projection every role reads, which is wider than #634's stated ask; and the
declaration form is **still the human's to choose** (`decision:design-it-twice` — the comparison is
returned unconverged), so rendering a field the human may replace would bake in the wrong name.
Do this after the human picks the declaration form.

## Not claimed

I did not attempt the change or measure how large it is. I confirmed only that the suite passes
without it and that the schema doc predicted the blind spot.
