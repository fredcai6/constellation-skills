# The prose, repaired against the code it describes

The reviewer's B4 write-up is explicit that the false prose is part of the
finding, and named the shape: **every sentence that keeps the qualifier "from
the binding" was true, and every sentence that dropped it was false**, because
that qualifier is exactly what the scan defeats. The repair below removes the
need for the qualifier instead of adding it back — the code now withholds from
the scan too, so the general sentence is the true one.

Six sentences, each checked against the branch it describes.

## 1. `decide_session_start`, the comment above the branch — the sentence B4 names

**Was** (false; measured false by the reviewer and reproduced by me):

> Owning none of the visible entries leaves `spine` None and falls through to
> the scan below, which is what the deleted worktree skip did when it skipped
> everything. Nothing another agent claimed is ever substituted: this site
> withholds rather than guessing, which is the fail-safe direction... The scan
> itself consults no binding key at all and is untouched here.

**Now** states the discriminator the code applies, names the write that made
the old sentence false, and separates the two cases explicitly — the non-empty
view the agent owns none of (hand out nothing, scan included) from the empty
view (#261, untouched). It also records why an own-but-unreadable entry keeps
the scan, which is the one case a reader would otherwise expect to be caught.

## 2. The `path comparison and spine location` section header

**Was** (false half italicised by the reviewer):

> ...a SessionStart blocks nothing and so hands out no gate from the binding at
> all *(it still falls through to the blind scan below, which reads no binding
> key and is not this rule's business)*.

**Now**: "hands out nothing" is stated without the escape clause, followed by
the correction itself — the scan reads no binding key but the branch it sits in
**writes** one, under the key this rule reads as OWN, so *a withholding that
feeds a writer is not a withholding*.

## 3. `_is_own_entry`'s docstring

**Was:** "...decide_session_start hands out no gate **from the binding**."
True, and true in the narrow way that let B4 through.

**Now:** hands out no gate, and where anything is visible does not fall through
to the scan that would bind one — with the reason stated, because for an
unidentifiable agent (#441) the old behaviour wrote an ownership record for an
agent the hook had just declined to identify.

## 4. `_own_entries`' docstring

**Was:** "What each site does when this returns EMPTY is its own business...
Folding those two fallbacks together is what would put one site's answer in the
other site's mouth."

The first clause is what the reviewer rejected: the fallbacks are uncoupled in
code and coupled in effect, through the store. **Now** keeps the two fallbacks
unshared (the reviewer endorsed that rule and so does the fix) but states the
one constraint that binds them: an empty result must not reach a writer.

## 5. `test_session_start_withholds_when_it_cannot_say_who_is_starting`

**Was:** "A session that owns nothing still falls through to
`_scan_active_spine` ... **exactly as it did before**." False in two directions
now — it does not fall through, and "exactly as before" was already false when
it was written.

**Now:** states that it no longer falls through, why, and points at the in-tree
case that pins it. The out-of-glob scoping is kept and is still stated.

## 6. `test_session_start_does_not_resume_from_a_crews_binding_it_never_claimed`

**Was:** "A session that claimed NOTHING must not be handed a gate." True of
what the test arranges, false of the code, which handed it one whenever the
scan found exactly one.

**Now:** claims only what the test measures — no gate **from the binding** —
and names its in-tree twin, which is where the general claim is now earned.

## 7. The class docstring of `OwnershipIsBindingKeyNotWorktree`

Not on the reviewer's list, but it made the same promise for the whole class
("place both spines outside the fallback scan's reach"), which stopped being
true of the class the moment I added in-tree cases. It now scopes that sentence
to the single-call cases and states why the sequence cases do the opposite —
including the one fact the reviewer said nothing in the handoff, the anchors,
the first result or the first review had connected: **`decide_session_start`'s
binding read and its scan-bind write are the same `if spine is None:` branch.**

## Check

No sentence in either file now describes the fallback as untouched by
ownership, and none claims a general withholding the code does not have. The
claim each test makes is scoped to what that test arranges, with a pointer to
the case that earns the general one. `tests/test_spine_rail.py` and
`tests/test_worktree_derivation.py`: 188 passed, 1 skipped, 25 subtests.
