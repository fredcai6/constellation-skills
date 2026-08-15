# Plan alternatives — #510

The change is a genuinely trivial local advisory/test correction under a frozen human-ratified launch order. The named untaken roads are:

- `smallest-diff` versus `most-testable`: not dispatched in parallel because the required outcome fixes both: change only `_trip_advisory`, and execute the legal sequence in its direct regression test.
- `best-seam-placement`: not dispatched because the launch order fixes the seam to `_trip_advisory` and `TripHardGuardsBeginNotClose`; moving a seam would violate `decision:no-runtime-expansion`.

Recommendation: one focused implement/review gate. A single candidate is proportionate to the local wording correction; independent review remains mandatory.
