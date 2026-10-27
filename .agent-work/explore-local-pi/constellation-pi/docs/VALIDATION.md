# Validation

2026-10-22:

- Independent review approved the bounded first version (docs/REVIEW.md).
- 23 offline tests pass against Constellation source revision 3ac7a1ab.
- TypeScript typecheck passes.
- Live Pi SDK connection to anthropic/claude-haiku-4-5 succeeded: requested a single
  OK response with one turn and 32 output tokens maximum. Pi reported 1,367 input
  tokens, 4 output tokens, and $0.001387 cost.
- Credentials were loaded from ~/.config/constellation-pi/credentials.env without
  copying the value into this project or run records.

The ordinary human-approval pathway is covered with mocked models and the real engine.
A complete hosted Haiku Commander → Implementer → Reviewer fixture also succeeded,
using explicit parent-test-driver overrides for plan/acceptance and retaining real
implementation/review evidence checks. It exercised interrupted-session recovery and
cost $0.11070480 in addition to the connection check. See
[the live validation report](validation/live-commander-2026-10-22.md). The GPU was unused.
