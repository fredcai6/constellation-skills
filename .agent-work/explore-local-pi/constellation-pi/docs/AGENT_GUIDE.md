# Agent guide

Constellation Pi integrates the existing Constellation checklist engine with Pi-owned
Commander and crew sessions. Keep the integration small and preserve the engine's
existing Claude Code and Codex interfaces.

## Structure

- `src/cli.ts`: terminal client and explicit human decisions.
- `src/workflow.ts`: Commander path, role/state operations, durable run bindings,
  crew handoffs, repair, overrides, and usage accounting.
- `src/pi-runtime.ts`: real Pi SDK sessions, isolated role prompts/tools,
  persistence, and request limits.
- `src/engine.ts` and `python/engine_bridge.py`: JSON transport to the existing
  engine's `state` and `main` functions. Do not duplicate engine semantics here.
- `test/`: real-engine integration tests and offline Pi runtime tests.

The first Commander path is intentionally narrower than the full Constellation
Commander skill. See README for its behavior and limits. Expansion should follow
real workflow evidence rather than importing every role's machinery at once.

## Working rules

Use the lightest model that can follow the process. Test mechanics without a paid
model first. Live API checks must be short, bounded, and reported as actual spending.
Keep credentials outside this repo. Keep an agent's work separate from its independent
review. Human or higher-level-agent direction can authorize departures; record the
principal and reason and reuse engine override operations.

Prevent specific known mistakes through simple construction; catch remaining failures
with evidence, tests, review, and recoverable state. This is workflow tooling for
fallible engineers, not a general permissions framework or security sandbox.

## Verification

```bash
CONSTELLATION_SOURCE=/path/to/constellation-skills \
CONSTELLATION_PYTHON=/path/to/working/python npm test
npm run typecheck
```

Source engine is an external local checkout selected explicitly. No engine source
is vendored or modified. Run metadata records that path; a later packaging version
should pin the tested engine revision for reproducible distribution.
