# Triage candidate: #613's lost-update half remains after lane A's atomicity fix

- **Disposition:** `recommend-and-defer`. Deliberately scoped out of lane A by the
  launch order, which assigns "the atomicity half."
- **Raised by:** `cmdr-567-a` at `600de020`.
- **Why it needs a record even though it is known:** the atomicity fix makes the
  remaining race *quieter*, which makes it easier to mistake for solved. That is the
  specific risk this candidate exists to prevent.

## What lane A fixed

`checklist_engine.save()` ended in a bare `Path(path).write_bytes(payload)`, which
truncates then writes. A concurrent reader could observe a partial spine, and a
crash mid-write could leave one permanently corrupt. Lane A makes the replace
atomic.

## What remains, precisely

Atomic replace guarantees a reader sees either the whole old document or the whole
new one. It does **not** serialize read-modify-write. The engine's pattern is
`load()` → mutate the dict → `save()`. Two writers interleaving as:

```
A: load()          B: load()
A: mutate, save()
                   B: mutate, save()     <- B's write is based on pre-A state
```

leaves a **well-formed** file with A's update silently gone. Nothing raises,
nothing is corrupt, and no evidence of the loss survives.

So the failure mode changes shape rather than disappearing: before the fix, a lost
update might also have been a torn file, which is loud. After the fix it is always
silent. **The fix removes the noisy symptom of a bug whose quiet symptom it does not
touch.** Anyone reading "save() atomicity fixed" as "concurrent spine writes are now
safe" will be wrong in a way the code no longer helps them notice.

## The two known second writers

1. **The parent heartbeat**, which is #613 as filed: the parent writes a spine the
   child also writes.
2. **A context-inheriting fork**, observed live this wave in lane G: its
   design-it-twice fork inherited the parent's full context, believed it was the
   Commander, and drove the Commander's `spine.json` under the identical lease id.
   Two writers, one identity, both authorized.

Case 2 shows the lease cannot be the fix. Both writers presented the same
`session_id`, so every mutating verb was correctly permitted.

## Recommendation

A compare-and-swap on save is the smallest mechanism that actually closes it: carry
the version or content hash the writer loaded, and refuse the save if the file on
disk no longer matches. The loser then reloads and reapplies rather than clobbering.
This composes with the atomic replace lane A lands, rather than replacing it — the
atomic replace is what makes the CAS window small enough to be meaningful.

Pair it with the separate write-provenance candidate
(`write-provenance-on-spine-journal.md`): CAS stops the loss, provenance explains it.
Neither substitutes for the other.

## Do not

Do not close #613 on lane A's merge. Lane A fixes one named half and says so in its
return; the issue's other half has no owner yet.
