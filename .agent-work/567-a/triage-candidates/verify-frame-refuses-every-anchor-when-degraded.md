# Triage candidate: `verify-frame` refuses the template it is paired with

- **Disposition:** `recommend-and-defer`. Not filed (`decision:no-issue-filing`).
  Not fixed: `scripts/map_orient.py` is not lane A's this wave, and the fix is a
  design choice, not a mechanical repair.
- **Raised by:** `cmdr-567-a` at `600de020`.
- **Severity:** medium, but it is a *rigor-inverting* defect, which makes it worth
  more than its severity suggests.

## The defect

In `map_orient.py`'s `frame_verdict`, when the orientation receipt's mode is
anything other than `RESOLVED`, the function loops over every token matching
`ANCHOR_RE` — `struct|capability|event|constraint|assumption|claim|decision`
followed by `:<id>` — and appends a problem for each, unconditionally:

> `<anchor> cannot resolve: this run oriented <mode>, so no map was read and there
> is nothing for a map anchor to be a member of`

There is no branch on which an anchor id is accepted when the mode is degraded.

Separately, the same function requires `backing` to be non-empty: the frame must
cite at least one path the receipt hash-pinned as a substitute.

**Net effect:** under a degraded map, `verify-frame` passes only a frame that
contains **zero anchor-id tokens** and cites the substitute paths. A frame carrying
real governing constraints and graded decision anchors always refuses.

## Why this is a contradiction and not just a limitation

`templates/MISSION_FRAME.template.md`, the template the `plan` step orders the
author to use, says in bold: **"Grade every anchor with an `@grade` child line"**,
and its own worked examples are `- decision:md-decision-is-a-list-item …`. Those
are `decision:` tokens. `ANCHOR_RE` matches them.

**Following the mandated template guarantees `FRAME-REFUSED` whenever the map is
degraded.** The two artifacts are shipped together and disagree.

The `plan` step's imperative also mis-describes the check. It says anchors "must be
one of the substitutes the receipt hash-pinned there, so the frame is compared
against a committed prior declaration instead of a same-breath assertion." That
describes the `backing` path-citation check. An author reading it reasonably
concludes that anchors backed by a pinned substitute resolve. They do not — the
anchor loop refuses them regardless.

## Measured — both halves, by experiment rather than by reading the code

**The rigorous frame is refused.** `cmdr-567-a`'s frame cites 15 anchors:

```
FRAME-REFUSED
frame: .agent-work/epic-567-door/cmdr-a/MISSION_FRAME.md
orientation: DEGRADED-UNPARSEABLE
frame citations do NOT resolve -- REFUSED
problems: 15
  - constraint:one-spine-per-process cannot resolve: this run oriented
    DEGRADED-UNPARSEABLE, so no map was read and there is nothing for a map
    anchor to be a member of
  ... (15 identical-shaped problems, one per anchor)
exit 10
```

**The empty frame passes.** To confirm the inversion rather than infer it, I wrote a
five-line throwaway frame under a scratch work id, with a copy of the same DEGRADED
receipt, **zero anchor-id tokens**, and one citation of a hash-pinned substitute:

```
# Mission Frame

## Intent
Prove what verify-frame accepts under a DEGRADED receipt.

## Structural Anchors
Read docs/agents/ORCHESTRATOR_CONTEXT.md as the declared substitute.

## Governing Constraints
Stated in prose only, with no anchor-id syntax anywhere.
```

Result:

```
FRAME-OK
orientation: DEGRADED-UNPARSEABLE
frame citations resolve -- contract SATISFIED
problems: 0
exit 0
```

So the gate is not merely broken under a degraded map — **it actively prefers the
emptier artifact.** A five-line frame naming no constraints and no decisions passes;
a frame carrying 15 governing constraints and graded decision anchors is refused. The
scratch work area was removed after the measurement.

The previous lane A (`cleanup/a-door`) hit the same wall at `a69bbac4` and recorded
it as "cannot be satisfied by any frame", which is close but not exact, and the
inexactness matters: it *can* be satisfied — by a worse frame. That is a sharper and
more actionable statement than "the gate is broken."

## The rigor inversion, which is the real point

The gate rewards removing content. To pass it under a degraded map, an author
deletes the constraint and decision anchors — the part of the frame that carries
what must not be violated — and keeps the prose. `global-orchestrator.md` warns
about "a check that cannot fail"; this is the neighbouring failure: **a check that
fails the better artifact.** An author who does not notice will quietly learn to
write frames without anchors.

## Recommendation

Pick one, deliberately, and make the template and the imperative agree with it:

1. **Accept anchor ids under a degraded receipt when the frame also cites a pinned
   substitute** — treat the substitute citation as the committed prior the anchors
   hang from. This matches what the step's imperative already claims to do, so it
   is the smallest change to make the shipped artifacts consistent.
2. **Or keep refusing anchors when degraded, and change the template** to say that
   a degraded frame states constraints in prose without anchor-id syntax.

Option 1 is the recommendation. Option 2 makes the frame worse in exactly the way
described above.

Whichever is chosen, also fix the imperative's description, which currently
promises behaviour the code does not implement.

## Minor, same file, worth folding in

`verify-frame`'s semantic exit code (10) is invisible through a pipe: `... | tail`
reports `tail`'s 0. A refusing gate reads as green to anyone who pipes the output,
which is the normal way to read a long refusal. Not a defect in the tool's
contract, but a documented gotcha would be cheap.

## Not disputed

The gate's stated purpose — "a regression floor so map-IGNORING cannot silently
return" — is sound, and its own check text is unusually honest about what it is not
(it states its measured sensitivity as 0/4 and specificity as 0/1 for
map-lateness). This candidate is about the degraded branch only.
