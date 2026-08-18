# Triage candidate — `current` does not tell an agent a gate is frozen

**Not filed.** `decision:no-issue-filing-mid-run` — staged only.

## Observation — measured at `392b7917`

`bookend: true` changes what `amend` will accept, but the engine's **projection** — what `current`
prints — never mentions it. Verified directly against a copy of the shipped Commander template,
which declares `init` and `archive`:

```
$ ... py scripts/checklist_engine.py --file $COPY current | grep -i bookend
(no output)
```

`type`: **measured**, by running `current` and grepping its output. `rev`: `392b7917`.

## Why it matters

`global-everyone.md` calls `current` "the complete gate briefing" and names it the **only**
sanctioned way to read spine state: *"Opening `spine.json` to read state is a violation."* So an
agent deciding whether to re-plan its middle has no sanctioned way to learn which gates are frozen.
The freeze is discoverable only by attempting an `amend` and being refused.

That is a small but real instance of the thing #634 is trying to reduce: work left on the agent
that a mechanism could carry.

## Correction to an earlier draft of this candidate

An earlier version of this file claimed the field was **invisible to the test suite**, citing
`TaskFieldCompleteness`'s stated residual limit ("a field introduced only by a template … is still
invisible to the property"). **That was wrong, and I am correcting it rather than shipping it.**

That hole was already closed by #475's `TemplateOnlyFieldAllowlist`
(`tests/test_checklist_engine.py:5841`), which walks the real shipped templates and fails on any
template-only field not in a stated allowlist. The g2 crew hit that guard and registered `bookend`
in it, with a comment explaining why. So the field **is** covered by a check that can fail — the
suite passing at `392b7917` is genuine, not vacuous.

What survives is the narrower, verified claim above: **registered is not rendered.** The allowlist
proves the field is *known*; it says nothing about the projection showing it.

I found this only because the g2 crew's Workflow Feedback named the guard, which is the argument
for harvesting crew feedback rather than skimming it.

## Possible fix (hypothesis, not a spec)

Render the frozen gates in `current` — a marker on the gate, or one line naming which gates are
frozen — so an agent can see the shape of its own plan without opening the file.

## Disposition

`recommend-and-defer`. Fails the fix-now ladder on **no architecture/production-default impact**:
the projection is what every role reads, so changing it is wider than #634's ask. It is also
badly timed — the human has **not yet chosen the declaration form**
(`decision:design-it-twice`, comparison returned unconverged), and rendering a field the human may
replace would bake in the wrong name. **Do this after the declaration form is settled.**

## Not claimed

I did not attempt the change or measure its size. I did not check whether the MCP door's
`spine_status` differs from the CLI's `current` in this respect.
