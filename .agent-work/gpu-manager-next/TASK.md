# Proposed next GPU manager issue: read-only consumer inventory

## Task
Prepare a concise execution plan for a bounded next issue: produce a current,
evidence-backed inventory of the configured GPU services and project consumers
that a future GPU manager would need to coordinate. This invocation is planning
only. Propose the plan and stop at the human plan gate. Do not implement anything,
start crews, approve decisions, or alter the first issue's pending workflow.

## Intent
The human asked to try the new artifact-based Pi workflow on the GPU manager and
asked what comes next there. The read-only gpu status command is already built,
reviewed and committed. Before choosing broker or service-migration behavior,
refresh the old handoff's picture of GPU ownership and consumers against source
configuration. This is a proposal for a real next slice, not a throwaway test.

## Required context
- /home/tommy/projects/GPU_MANAGER_HANDOFF.md — historical handoff dated 2026-10-22,
  describing an October 10 session. Its claim that nothing is built is obsolete.
  Its service locations, reference counts, container names, usage sizes and policy
  proposals are leads to verify, not current measured facts or new approvals.
- /home/tommy/projects/gpu-manager/AGENTS.md and docs/AGENT_GUIDE.md — existing
  project guidance. The guide scopes execution to the approved first status issue
  and names the legacy finish_crew protocol. Do not edit it in this planning pass.
  The next issue needs an explicit bounded guide update after the human approves
  its scope; preserve all restrictions on GPU workloads and secrets.
- docs/DESIGN.md, README.md, docs/VALIDATION.md — approved first-issue scope and
  evidence. Current implementation: gpu_manager/ and tests/. Do not reimplement it.
- docs/ANTHROPIC_AUTHORIZATION.md — standing authorization for relevant project
  material through the configured Claude API. Exclude secrets/unrelated data.
- First implementation commit: eeafebb. Its separate legacy Pi run,
  .constellation-pi/gpu-status-issue-1, remains at human acceptance. Do not change it.

## Candidate deliverable for the proposed issue
One small maintained GPU consumer inventory under docs/, with evidence references:
configured service/client, owning repo/configuration, known endpoint/dependencies,
GPU requirements when explicitly declared, and confidence/unknowns. Identify what
would need to move out of the journal repo versus remain client configuration.
Separate configured or declared behavior from observed running state. Do not claim
that a configured service is currently running, that a PID identifies a project,
or that the inventory proves all GPU users have been found.

Prefer a docs-only next issue if that answers this question; do not add a registry,
daemon, scheduler, container attribution code or new gpu subcommand just for it.
The inventory should make the following implementation cut clearer, while leaving
unresolved interactive/batch scheduling decisions with the human.

## Planning evidence
Read the supplied GPU manager repository and historical handoff. During this
planning invocation do not inspect other projects or live processes. The plan may
identify exact project configuration files to inspect during the approved issue,
using the handoff as a lead. Avoid broad home-directory searches. Plan source-only
verification and document known limits; no runtime or performance experiments.

## Boundaries for the proposed execution
Read-only inspection of explicitly relevant project source/configuration. Write
only the inventory, necessary README links, workbench/evidence files and the
explicitly approved bounded project-guide update. No edits to client services or
configuration in other projects. No code changes to the existing status command.
No Docker commands or sockets, network probes/inference, GPU compute, benchmarks,
model loads, root access, lifecycle operations, process signals, scheduler/daemon,
driver settings, or workload/service changes. No reading keys, .env files, process
environments or full command lines. Keep current GPU users untouched.

## Success criteria for the proposed execution
- Each concrete inventory claim cites inspected source/configuration or is clearly
  identified as historical, declared, inferred or unknown.
- Sources and exclusions are bounded; missing repositories/files become explicit
  gaps rather than guesses or reasons for broadening inspection.
- Current first-issue deliverables and unresolved broker policies are preserved.
- The document gives a useful smallest-next-cut recommendation grounded in the
  inventory and identifies decisions that still need the human.
- Separate Pi Implementer and Reviewer sessions use role handoff/result artifacts.
  Reviewer checks source references independently. Reports contain no secrets.

## Authority and stop conditions
Only the planning proposal is authorized by this input. The human has not yet
approved this proposed issue's implementation plan or changed GPU usage policy.
Do not manufacture human approval. Stop for missing scope/authority, relevant
sources unavailable within the named boundaries, or a requirement to relax the
running-workload restrictions. Store the concise plan through propose_plan; do not
send a second prose explanation of the input or turn this into a multi-issue epic.
