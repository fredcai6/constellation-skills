# Triage candidate: a hardlink defeats any path-based containment check

- **Disposition:** `recommend-and-defer`. Not filed (`decision:no-issue-filing`). Not fixed —
  inode-identity containment is a **different mechanism**, not a refinement of the path check,
  and choosing it is beyond a rework dispatch.
- **Raised by:** the `g2` reviewer (second instance) as a non-blocking third finding, after
  confirming the two blockers. Relayed by `cmdr-567-a`.
- **Severity:** low as an exploit, high as a **claim-accuracy** issue. It does not widen the
  practical attack surface much; it does mean the isolation property cannot be stated
  unqualified.

## The finding

`spine_bind` confines a candidate to `<the door's own checkout>/.agent-work/` and additionally
refuses any candidate whose own `git rev-parse --show-toplevel` differs from the door's. The
blocking fix for B1 is to resolve before asking git — `candidate.resolve().parent` — which
closes symlinks.

**It does not close hardlinks, and nothing path-based can.**

A symlink has a *target*, so resolution reveals where the file really lives. A hardlink has
no target: it is a second **name** for the same inode. So a hardlink at
`<own checkout>/.agent-work/x.json` pointing at a nested checkout's `spine.json` genuinely
*is* a file in our work area:

- `Path(candidate).resolve()` returns the path you handed it — there is nothing to follow.
- `git rev-parse --show-toplevel` on its parent correctly answers "our checkout."
- Both names are equally real. Neither is the "true" location.

So every check that reasons about **paths** returns the right answer to the wrong question.

## Why it is nonetheless a small exploit

The attacker must already be able to:

1. **write inside the door's own `.agent-work/`** — which is the very tree the door is
   permitted to bind anyway, and
2. put the target on the **same filesystem** (hardlinks cannot cross devices), and
3. have a foreign checkout nested inside that tree in the first place, which nothing in this
   repo creates and which the reviewer measured as zero occurrences live.

An actor with write access to `.agent-work/` can already place a perfectly ordinary spine
there and have it bound. The hardlink buys them one specific extra thing: making a **foreign
checkout's** spine bindable, and therefore getting the door to write a lease and gate state
into a tree it should not touch. That is a real escalation, just a narrow one.

## Why it matters anyway: the property must be stated truthfully

`decision:isolation-not-fencing` exists to force the replacement property to be *named and
attackable* rather than assumed. Lane A has already been caught once claiming a property the
code did not have — the pre-fix statement "one checkout's work-area tree per process" was
falsified by a symlink, in the same paragraph that called the guard "what makes the isolation
claim true rather than aspirational."

So the claim should carry its limit:

> **One checkout's work-area tree per process, enforced by path.** An actor who can already
> create a hardlink inside the door's own `.agent-work/` can present a foreign checkout's
> spine as a local one.

That sentence is less satisfying and more useful. Overstating it a second time, right after
being corrected for overstating it the first time, would be the worse error by far.

## Recommendation, if someone takes it up

Two honest options, and they are genuinely different mechanisms rather than degrees:

1. **Accept the residual and document it** (what lane A does). Cheapest, and defensible: the
   attack requires write access to the tree the door may bind anyway.
2. **Containment by inode, not by path.** Compare `(st_dev, st_ino)` of the candidate against
   the set of files git reports for the door's own checkout, or verify that
   `git ls-files`/`git check-ignore` in the *candidate's own* directory agrees the file belongs
   to our checkout. Heavier, needs care about performance and about files git does not track
   (`.agent-work/` contents are tracked here, but that is a repo property, not a guarantee).

**Do not** attempt a middle path that adds more path-shaped checks. That is the exact failure
`_identity_violation`'s docstring records six times over: enumerating shapes an attack might
take, each defeated by a shape not enumerated. Hardlinks are not another spelling to add to a
list — they are evidence that the *category* of check is insufficient, which is a decision to
take deliberately or to accept deliberately, not to patch.

## Related

- The B1 symlink blocker itself: the bug was a **mismatch between two guards that resolve
  paths differently**, one resolving and one not. The hardlink finding is the deeper version of
  the same lesson — path identity is not file identity.
- `door-main-catches-only-keyerror.md` — the other reviewer-sourced candidate from this gate.
