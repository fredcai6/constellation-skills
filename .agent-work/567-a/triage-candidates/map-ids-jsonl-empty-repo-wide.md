# Triage candidate: `map/ids.jsonl` is empty, so every run in this repo orients DEGRADED

- **Disposition:** `recommend-and-defer`. Re-raised, not newly discovered.
- **Raised by:** `cmdr-567-a` at `600de020`. Previously raised by lane
  `cleanup/a-door` at `a69bbac4`.
- **Note on status:** this has now survived a full epic as a known, filed,
  unactioned defect. That persistence is the reason to re-raise rather than assume
  it is in hand.

## Measured

At `600de020`:

- `map/ids.jsonl` — tracked, **0 bytes**.
- `map/INDEX.md` — tracked, 29,449 bytes of generated structure.

`map_orient.py orient` therefore returns `DEGRADED-UNPARSEABLE` for **any** work id
in this repo, with `anchor_count: 0`. Its candidate probe reports `map/INDEX.md` as
"content but no citable anchor id (unfilled template?)" and `map/ids.jsonl` as
"empty file". The four `docs/architecture/` candidates are all absent — this repo
uses the `map/` code-map form, not the packet-map form.

## Consequences, both of which bit this run

1. **Every commander must discharge a degraded orientation** with substitutes,
   unmapped statements and an escalation. That is the designed path and it works,
   but it is paid on every run in the repo, forever, for a defect with a single
   cause.
2. **The `plan` step's `c6` verify-frame gate cannot be satisfied by a frame that
   follows the mandated template**, so it is taken as a recorded waiver. See the
   separate candidate `verify-frame-refuses-every-anchor-when-degraded.md` — that is
   a distinct defect, but an empty `ids.jsonl` is what makes it reachable on every
   run instead of never.

## Why it is not fixed here

`map/` is not lane A's this wave, and `scripts/code_map/render.py` is the generator
that would have to run. Fixing it inside a fenced lane would also mean committing a
large generated artifact from a lane whose review criteria say nothing about it.

## Recommendation

Run the code-map generator and commit the result, as its own small change with its
own review. `map/INDEX.md` already has content, so the generator evidently runs —
the question is why `ids.jsonl` came out empty beside a populated index, and that is
worth one look before regenerating blindly. A regeneration that produces an empty
`ids.jsonl` again would mean the defect is in the generator, not in the committed
state.

## The more important find, now measured rather than suspected

I recommended checking whether `tests/test_code_map.py` — the suite described as
holding the map fresh — passes against a 0-byte `ids.jsonl`, then ran it instead of
leaving it as a suggestion:

```
py -m pytest tests/test_code_map.py -q
148 passed, 63 subtests passed in 14.18s     (exit 0)
```

**It is fully green while the map it guards is empty.** This is the
"check that cannot fail" family from `global-orchestrator.md`, in its **vacuity**
form: the guard passes on an empty set. A 148-test suite reports the code map
healthy, on every run, in a repo where no anchor id exists for any area.

That reorders the priority. The empty `ids.jsonl` is a one-time data defect. The
suite that cannot see it is a standing defect, and it is the reason the data defect
survived a full epic while being reported twice — nothing in CI ever disagreed with
it.

**Recommendation, revised:** fix the suite first. Per the mechanical detector in
`global-orchestrator.md`, "any guard that loops must assert what it looped over" —
the suite should assert a non-zero anchor count and state it, so an empty map fails
loudly. Regenerating the map without that assertion just resets the clock on the
same silent failure.
