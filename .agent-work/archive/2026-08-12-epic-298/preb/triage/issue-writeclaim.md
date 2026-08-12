Filed from the PRE-B measured arm (epic #298). This is a **methodological defect that will recur on every future arm**, not a one-off, so it is filed rather than just noted in a run record.

## The contradiction

`LAUNCH_ORDER-PRE-B.md` return-shape item 6 asks for:

> Confirmation nothing landed in f1Brainz — and note that a worktree-scoped `git status` does **not** prove it. The load-bearing evidence is zero `Write`/`Edit`/`NotebookEdit` calls and zero forbidden git/gh operations across every transcript.

That standard was inherited from the PRE-A arm (#299), where it was exactly right: PRE-A ran generic agents that invoked no skill and wrote no file, so "zero write calls" was both achievable and a genuinely strong claim.

**It is unachievable by construction for any Commander-loaded arm.** The Commander spine's `plan` step *is* "produce a mission frame ... then author `execute.json`". Both are `Write` calls. A run that reaches the plan step with zero writes has not reached the plan step. So the treatment under measurement and the safety evidence standard are mutually exclusive, and any future arm that forces a skill load inherits the same collision.

## The failure mode this creates

The dangerous resolution is the quiet one: an implementer reports "zero writes outside the worktree" or "`git status` clean" and the reader, primed by item 6, hears the stronger claim. `.agent-work/` is only *partially* gitignored in f1Brainz, so `git status --porcelain` is not a reliable proxy in either direction.

## The standard PRE-B used instead

Strictly stronger than the worktree-scoped `git status`, and reportable per run:

- every `Write`/`Edit`/`NotebookEdit`/`MultiEdit` call **enumerated with its resolved target path**;
- an assertion that **zero** of them resolve outside that run's own disposable pinned worktree;
- an assertion that zero resolve inside the worktree but **outside `.agent-work/`**;
- zero forbidden git/gh operations, by both the frozen extractor's pattern set and a wider one (`git push|commit|merge`, `gh pr create`, `gh issue create|comment|edit|close`);
- worktrees swept after capture.

Implementation: `.agent-work/epic-298/preb/verify_treatment.py`, `write_audit` block.

## Ask

Adopt the enumerate-and-bound standard as the default "nothing landed" evidence for measured arms, replacing "zero write calls", and carry it into the POST arm's launch order so PRE-B and POST are audited identically. The zero-write phrasing should survive only as the special case it is: correct for arms where the subject invokes nothing.
