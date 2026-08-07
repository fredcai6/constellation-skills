# Initial Wave

Complete one coherent why-capture, gauge-read, and trip-policy execution-and-validation loop.

## Exit criteria
- Why-capture, gauge-reader, and trip-policy acceptance evidence is independently observable.
- The loop preserves the frozen design's fail-safe and human-authority boundaries.

## Independently observable issues
- **CG-A — Why-capture + refresh primitives: engine schema (checklist_engine.py)**: The named original acceptance statements pass through the shipped public interfaces.
- **CG-C — Gauge reader: plain read() -> Reading|None + model-keyed thresholds**: The named original acceptance statements pass through the shipped public interfaces.
- **CG-D — Trip: two-band gate policy (SOFT stop-question + HARD refuse-advance)**: The named original acceptance statements pass through the shipped public interfaces.
