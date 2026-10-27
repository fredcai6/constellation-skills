# GPU status pilot — 2026-10-22

First real repository task: implement the approved read-only AMD `gpu status`
issue in `/home/tommy/projects/gpu-manager` (local commit `eeafebb`). Pi owned
separate Commander, Implementer, and Reviewer sessions; Claude Sonnet supplied
the model. The unchanged Constellation engine owns the gates and lease.

Outcome: independent Reviewer APPROVE; 60 fixture tests pass, including a
permission-gap regression. The coordinator also ran the suite from a portable
copy, imported the packaging backend without installing dependencies, injected a
list/read disappearance race, and checked invalid CLI budgets. Live observations
were read-only. No GPU work, workload changes, Docker actions, root operations,
or service changes were performed. Full validation lives in the target repo's
`docs/VALIDATION.md`.

The run remains at human acceptance, with its lease retained. No final human
approval was inferred. Run directory:
`/home/tommy/projects/gpu-manager/.constellation-pi/gpu-status-issue-1`.
17 bounded prompt invocations; recorded model cost $4.53045225. Interrupted
provider work can incur cost beyond reported usage. Credentials were loaded only
through the configured environment and excluded from prompts and artifacts.

This was not a hands-off success. Response/turn limits interrupted code generation;
the first review blocked silent process visibility gaps and invalid budgets. The
implementer then claimed some fixes not present on disk. The coordinator verified
actual files, demonstrated a failing permission regression, directly corrected the
remaining bounded defects, and requested another independent review. Review
APPROVE applies to the corrected files, not merely the implementer's narrative.

Runtime changes prompted by this pilot:

- Persist configurable response and resume budgets; stop on truncation instead of
  repeating writes under the same cap.
- Pass bounded Commander instructions to crew sessions.
- Preserve a submitted BLOCK if a later part of the invocation fails, and allow
  explicit repair recovery from that owned BLOCK artifact. Never recover APPROVE
  from an errored invocation.

27 offline tests and TypeScript checking passed for these runtime changes. The
next workflow improvement should reduce repeated prose and redundant evidence
replay, and make reported crew claims cheaper to compare against actual artifacts.
The first narrow workflow remains plan → implement → review → human accept; it
does not claim to execute the whole installed Commander skill.
