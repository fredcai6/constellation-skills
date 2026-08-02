# Pre-registration — how the POST arm will be read, written BEFORE any POST number existed

**Timestamp of writing: 2026-08-02, while the five captures were still in flight.** No POST
`ordering.json`, `treatment.json` or `discriminate.py` output had been produced or inspected.
The three captures then running had `status: "launched"` and no `treatment.json`. This file is
committed so the criterion is checkable against the arm's own git history rather than trusted.

The launch order hands the verdict to Tommy. This does not pre-empt that. It fixes the
**criterion** in advance so that the table he receives is a table, not a table plus an
after-the-fact story about what counts as a win. He may overrule any line here.

---

## 1. The primary measure, and its denominator

`map_before_src`, boolean, per run, straight from the **frozen** `extract_ordering.py`. Raw
indices do not transfer between arms and are not used for any cross-arm claim.

**The measure has three possible values, not two.** `extract_ordering.py` returns the reserved
literals `NO-MAP-READ` and `NO-SRC-READ` before it ever returns a boolean. This is not an edge
case: PRE-B's run-716 produced exactly such a row (119 tool calls, `NO-MAP-READ`,
`NO-SRC-READ`), so literal-valued rows occur at 1 in 5 in this exact task set.

**Therefore, fixed in advance:**

- The **boolean comparison is over rows where both arms yield a boolean.** PRE-B's denominator
  is **4, not 5** (`run-716` is a literal row). Any prose reporting "N/5" without saying which
  denominator it means is defective.
- **Literal rows are reported as their own named category with their own count.** They are
  never silently dropped and never counted as `False`.

## 2. `NO-SRC-READ` is the contract's STRONGEST outcome, not a missing datum

This is the trap this pre-registration exists to disarm.

The best thing the #304 contract could possibly do is make a subject orient from the map, plan
from it, and **never open a source file at all**. That run scores `map_before_src =
"NO-SRC-READ"` — **not `True`**. A POST arm in which the contract worked perfectly on all five
runs would show **zero `True` values**, the same headline number as total failure.

**Fixed in advance:** a `NO-SRC-READ` row with a confirmed `map_orient` orient call and a map
read is reported as **map-only orientation — a stronger result than `True`**, and is counted
that way. A `NO-MAP-READ` row is the opposite and is reported as such. The two literals are
never pooled with each other.

## 3. The four-cell reading of the two witnesses

The primary measure and the `map_orient` audit can disagree, and the *likely* POST outcome is
a disagreement — because `commander-core.md` carries map-first **prose** one hop closer to the
subject than the spine template carries the **tool** imperative (see #393). Precedence is
fixed now rather than argued later:

| `map_before_src` | contract fired (`map_orient` orient call) | reported as |
|---|---|---|
| True / `NO-SRC-READ` | yes | **ordering moved, mechanism confirmed** |
| True / `NO-SRC-READ` | no | **ordering moved, tool not used** — the prose did it, not the contract |
| False | yes | **contract fired and ordering did not move** |
| False | no | see §4 — do not read this cell alone |

**The primary outcome is `map_before_src`. The audit is a witness for the mechanism, never a
substitute for the outcome.** A True/no-call row is a real result, not a contradiction to be
adjudicated after the fact.

## 4. The three-way, with the third branch that #393 exposed

The launch order's pre-registered three-way is *sufficient / insufficient / irrelevant*.
**#393 showed that *irrelevant* was hiding two different worlds with two different remedies.**
Delivery is three hops — the skill loads, the spine is materialized from the template, the
imperative is obeyed — and `TREATMENT-VERIFIED` proves only hop 0, because
`constellation-commander/SKILL.md` contains zero occurrences of the word "map".

| observed | verdict | remedy it points at |
|---|---|---|
| ordering moved | **sufficient** | none — the contract works |
| Commander loaded, spine materialized, `map_orient` fired, ordering did not move | **insufficient** | re-anchor or strengthen the contract |
| Commander loaded, **spine never materialized** | **irrelevant — delivery** | fix the delivery path; says nothing about the contract |
| Commander not loaded / corpus lacks the contract | **irrelevant — install** | fix the install (#344 class) |

**A null that cannot say which of the last three it is, is not a result.** The columns that
separate them are `treatment.json.verdict` (hop 0), `contract_delivered` (hop 1), and
`map_orient_confirmed_by_result` (hop 2).

## 5. Threshold, stated before the numbers

PRE-B's baseline is **0 of 4** boolean-valued rows `True`. With n = 1 per issue per arm and no
variance estimate, no threshold here can carry statistical weight, and none is claimed. It is
a **reporting rule**, so that the same table cannot be narrated two ways:

- **≥3 of 4** boolean-valued POST rows `True` (or map-only orientation) → report as
  **sufficient**, with the n = 1 limitation stated in the same breath.
- **1–2 of 4** → report as **ambiguous**, present both readings, recommend replication rather
  than a verdict.
- **0 of 4**, with the contract confirmed delivered and fired → report as **insufficient**.
- **0 of 4**, with the contract not delivered or not fired → report as **irrelevant**, and name
  which of the two branches in §4 it is.

**Tommy adjudicates. This run does not.** Where the evidence supports two readings, both are
presented.

## 6. What would invalidate the arm outright

Stated now so it cannot be rationalised later:

- any run not `TREATMENT-VERIFIED`, `status: finished`, `exit_code: 0`, transcript complete —
  a **FAILED CAPTURE**, reported, never retried until the number improves;
- a POST brief differing byte-for-byte from PRE-B's archived brief;
- the corpus deep digest differing between the five per-run witnesses;
- the `map_orient` audit returning non-zero on PRE-B (it returns **0 across 5 runs / 595 tool
  calls**, and its self-test is 7/7 including the mutants that must not count).

## 7. Declared limitation that no threshold can repair

**The manipulation is `74953936` → `3595955`: 8 days and +31 files, not #304 in isolation.**
`git merge-base --is-ancestor` proves #304 and its post-archive fix are *contained in* that
delta; it proves nothing about what else is. Any effect this arm measures is attributable to
"the newer corpus", and attributing it to the map-first contract specifically requires the
mechanism evidence in §3–§4, not the ordering number alone.
