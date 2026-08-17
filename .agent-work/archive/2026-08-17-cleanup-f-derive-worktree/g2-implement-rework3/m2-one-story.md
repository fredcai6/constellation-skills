# C3 — the module header and `main()` tell one story

`scripts/checklist_engine.py` carries the claim twice. At `84d949eb` the two
passages contradicted each other: the header said the engine reads no location
at all, and `main()`, 3400 lines below, said the worktree is derived from the
spine's own path and that the lease was the ownership guard "as it always was".
That is B1. Both passages are quoted here in full, as they now stand, followed
by the two sentences that were replaced.

## The module header (unchanged by this rework except the consumer count)

```python
# Stamp-and-compare is RETIRED (#609 g2). `origin.worktree` used to be compared,
# on every mutating verb, against a worktree toplevel the engine resolved from
# its own ambient cwd; `origin_worktree_refusal` and the two verb sets that fed
# it are gone, along with the per-verb `git rev-parse` that supplied the other
# side. THE ENGINE NOW READS NO LOCATION AT ALL, ambient or derived. There is no
# second value that can disagree with the first, and no ambient reading a check
# command could forge by `cd`-ing first, because the engine no longer asks the
# question anywhere.
#
# The lexical rule that derives a worktree from a spine's path is NOT retired --
# only the engine's copy of it is. The rule lives in the stdlib-only hook, as
# `spine_rail._worktree_from_spine`, and `tests/test_worktree_derivation.py`'s
# case table is its specification. The engine-side copy was deleted in #609 g2
# under `ADMIRAL_RULING-2` N2: it had TWO consumers -- the shape question inside
# `origin_worktree_refusal`, deleted by that same gate, and #315's `cwd` thread,
# re-homed to #610 by `ADMIRAL_RULING-1` R3 -- and a third that
# `ADMIRAL_RULING-1` R2 withdrew before it ever existed. Three sound decisions
# in a row, and a definition nothing calls is not shipped. It re-lands in
# #610's wave together with #315 -- the consumer that threads `cwd` into the
# engine's check runner -- and re-derives against that same table.
#
# Nothing was left unguarded by that removal WHEREVER A LEASE EXISTS -- and the
# leaseless path was WIDENED. The comparison answered "where am I", never "is
# this mine": ownership is the LEASE, but only where one is actually held.
# `require_session` gates mutating verbs only once an active lease exists and
# returns early otherwise, and `_active_lease` reads a RELEASED lease as absent.
# So on a spine with NO ACTIVE LEASE -- never claimed, or claimed and since
# released -- this comparison was the sole refusal, and the engine now asserts
# nothing about location. Measured from a foreign worktree: `start` and `attach`
# on a never-claimed spine, and `start` after a release, went from refused to
# accepted, WRITING STATE INTO A TREE THE AGENT IS NOT STANDING IN. Under an
# active lease held by another session, nothing changed.
#
# That widening is ACCEPTED and deliberate, not a no-op. A `cd <worktree> &&`
# prefix defeated the comparison, so it was never a boundary -- but a forgeable
# guard is not the same as no guard. This supersedes the 2026-08-15
# worktree-identity ruling, which settled how the two sides of the comparison
# should be resolved -- a question that no longer exists.
#
# `origin.worktree` is still WRITTEN, by `spine_lifecycle.build_origin` and
# `init_work_area.instantiate_spine`. It is provenance -- what a human or a
# reconciler reads to see where a spine came from -- and nothing reads it to
# decide anything. `tests/test_spine_origin_isolation.py` pins both halves of
# that pairing and goes red if either one breaks.


# --------------------------------------------------------------------------- #```

## `main()`'s load-time comment block (repaired by this rework)

```python
    # Nothing stands between `load` and the arming below any more (#609 g2).
    # Every verb used to pay for a git toplevel read here, on the engine's
    # ambient cwd, to feed the retired `origin.worktree` comparison.
    # Both are gone: THE ENGINE NOW READS NO LOCATION AT ALL, ambient or
    # derived, so no ambient reading is taken and none can be forged -- not
    # because the reading moved somewhere cheaper, but because the engine no
    # longer asks the question anywhere. The lexical rule that derives a
    # worktree from a spine's path is not retired; it lives in the stdlib-only
    # hook as `spine_rail._worktree_from_spine`, and the engine holds no copy
    # of it (module header, above).
    #
    # Nothing is lost by vacating this position. It existed so a refusal could
    # be raised BEFORE dispatch() and returned WITHOUT save() -- main() persists
    # state on the EngineError path for every verb except `current`, so a
    # refusal raised inside dispatch() would write into the very tree it was
    # protecting. With no refusal to raise, there is nothing here to order.
    #
    # What dispatch() still enforces is the LEASE -- and the lease is the
    # ownership guard only WHERE A LEASE EXISTS. `require_session` gates
    # mutating verbs once an active lease is held and returns early otherwise,
    # and `_active_lease` reads a RELEASED lease as absent. So on a spine with
    # NO ACTIVE LEASE -- never claimed, or claimed and since released -- the
    # retired comparison was the sole refusal, and removing it WIDENED that
    # path. That widening is ACCEPTED and deliberate: a `cd <worktree> &&`
    # prefix defeated the comparison, so it was never a boundary -- but a
    # forgeable guard is not the same as no guard. Under an active lease held
    # by another session, nothing changed (`ADMIRAL_RULING-1` R1; the module
    # header above carries the same statement in full).
    #```

## The two sentences this rework replaced, quoted from `84d949eb`

```python
    # Both are gone: the worktree is derived from the spine's own path where it
    # is needed, so no ambient reading is taken and none can be forged.
    # The lease, which is the actual ownership guard, is enforced inside
    # dispatch() as it always was.```

## They now agree, clause by clause

| claim | header | `main()` |
|---|---|---|
| the engine reads no location at all, ambient or derived | yes | yes |
| ...because it no longer asks the question anywhere | yes | yes |
| the lexical rule itself is not retired; it lives in the stdlib-only hook | yes | yes |
| the lease guards ownership only where a lease exists | yes | yes |
| leaseless — never claimed, or claimed and since released — was the sole refusal | yes | yes |
| removing it WIDENED that path, and the widening is accepted and deliberate | yes | yes |
| a forgeable guard is not the same as no guard | yes | yes |
| under an active lease held by another session, nothing changed | yes | yes |

Mechanically asserted, segment by segment, by `check_claims_repaired.py`: the
header and `main()` are extracted by their own anchors, so a clause satisfied
in one cannot satisfy the other.
