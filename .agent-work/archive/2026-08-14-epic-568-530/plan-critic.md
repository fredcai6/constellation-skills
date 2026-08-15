# Plan critic — #530

## Verdict: BLOCK

The narrow seam is correct in principle: derive the owning checkout from the
validated absolute spine and change only the two existing binding writers.
However, the alternatives leave two acceptance-critical behaviors ambiguous.

### Required changes before execution

1. Specify the malformed/out-of-layout contract for the helper.  “Fail closed
   or return no ownership” is not implementable at a binding writer: storing
   `None`, an empty value, or silently falling back to `cwd` can either weaken
   `_foreign_worktree` or recreate the bug.  State whether claim/SessionStart
   must skip the write (and remain fail-open), or whether a validated spine
   makes derivation mandatory and an impossible derivation is a test failure.
   In either case, explicitly prohibit a `cwd` fallback and preserve the
   binding schema expected by existing readers.

2. Add a production SessionStart assertion to the acceptance topology.  The
   mission and execute contract require both claim and bind-on-resume writers
   to use the same ownership derivation, but the `most-testable` scenario only
   exercises claim, Stop, and release; its pure helper cases cannot catch a
   SessionStart writer that still records payload `cwd`.  Use an unambiguous
   scan/bind-on-resume fixture with shared session and distinct agent identity
   (or a separate linked-worktree fixture), wrong payload `cwd`, and assert
   the newly written binding's worktree is the owning root.

3. Make the path-shape predicate exact and test it.  It should accept only a
   resolved JSON checklist at `<worktree>/.agent-work/<work-id>/<name>.json`
   (with the existing normalization conventions), reject a path merely having
   a `.agent-work` ancestor at another depth, and never infer ownership from
   observed `cd`, `--worktree`, environment, or payload.  Include a negative
   out-of-layout case and ensure release resolution remains untouched.

### Scope review

The proposed one-helper/two-writer diff, unchanged binding shape, unchanged
release lookup, and real linked-worktree red/green test are otherwise within
the launch order. Shared session plus distinct agent IDs and a deliberately
wrong child payload `cwd` are the right discrimination, and Stop should prove
the child entry is foreign while the parent entry blocks/releases normally.
Do not add locking, identity unification, reaping, migration, or other #441
behavior. Once the three points above are made explicit in the execution plan
and test, this should be APPROVE.
