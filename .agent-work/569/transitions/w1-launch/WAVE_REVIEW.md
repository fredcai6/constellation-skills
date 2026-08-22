## Wave review — boundary `w1-launch`

This is the epic's opening boundary. No wave has run, so the evidence classified here is
**measurement taken against the repository**, not returns from a completed wave. Five claims in the
epic body were checked; three held, one was smaller than filed, and one was falsified.

**Held.** Qualitative gates dominate: 65 of 105 conditions across the shipped spine templates are
`check: null` (61.9%). The corpus-wide 99.7%-on-self-assertion figure reproduces at the template
source, so the hole the epic names is real at the place the epic would fix it.

**Held, and worse than filed.** #345's built-not-wired pattern was filed as six instances. The census
finds 26 check-shaped scripts in `scripts/`, of which **13 are referenced nowhere in `skills/`** and
only **7** appear inside a machine-checked `command` condition.

**Held.** #371's wedge is confirmed by reading: `checklist_engine.py:1090` and `:3439` both compare
match fields with `==`, so a list-valued `match` is silently unsatisfiable. `validate_spine` faults a
MISSING match (#562) but never a mistyped one.

**Smaller than filed.** `APPROVE-WITH-FOLLOWUPS` — the verdict whose arrival triggered #371 — no
longer exists anywhere in the corpus. #371 is now purely the mechanism fix, not the vocabulary
reconciliation it was written as.

**Falsified.** The epic's "three-way verdict-vocabulary inconsistency across four documents" does not
reproduce. The token census is APPROVE 34, BLOCK 24, REJECT 4, COMMENT 3, with no competing
approve-flavoured verdict. Dropped.

**The finding that reorders the epic.** Work package 1's stated cheap entry point is
`generate_spine.py`, which "already REQUIRES a `because` per qualitative condition and throws it away
at compile time." Two corrections. It does not throw it away — line 521 appends it into the statement
*string*, so the basis survives as prose and dies as structure. And more consequentially,
**`generate_spine.py` has zero callers in `skills/`**; it is referenced only from
`docs/CHECKLIST_SCHEMA.md`. The epic's foundation is itself an instance of the epic's own work
package 6. Running WP1 first would build the epic's core value on ground the epic distrusts, and
#345 already wrote the warning: *"Do not fix this by adding another unwired checker. That failure
mode is available here and would be funny exactly once."*
