# Staged constellation feedback — wave4-626 (fenced closeout)

Delegated commander run under Admiral epic #601; fenced off the shared main-checkout durable root
(launch order scopes my writes to the verdict + worktree workbench; sibling commanders concurrent). This
staged export is harvested by the Admiral into the shared root at closeout.

## Constellation lessons confirmed this run — disposition

- **`engine-artifact-attest`** (confirmed this run: review-result/user-decision/implementer-result artifact
  checks satisfied via `attach` not `attest` across g1-g5). **DISPOSITION: already resolved upstream** per
  the 2026-07-17 curator sweep recorded in `.agent-work/CONSTELLATION_FEEDBACK.md` ("Already resolved
  upstream: engine-artifact-attest ... attest precondition/postcondition fallback"). The recurrence-debt
  counter increments mechanically on confirm, but the underlying behaviour is understood and the upstream
  fix is noted as shipped — NOT re-exported as a fresh defect. No new upstream action required from this run.

## New workflow observation (banked in AGENT_FEEDBACK.md, NOT added to the capped playbook)

- **Agent-tool crew self-send is a no-op.** All 6 crews dispatched as synchronous Agent-tool subagents were
  told (per mission-frame doctrine) to SendMessage their result to the dispatching commander's team-name
  ("ShipE-626"); each correctly recognized this as a self-send and routed to "main", while the Agent-tool
  result returned directly. The SendMessage-delivery instruction is only meaningful for CLI-backed crews.
  Not added to the Active playbook (cap 20 reached; its fix is a shared crew-dispatch handoff-template change
  = doctrine = human call in delegated mode). Recorded in AGENT_FEEDBACK.md 2026-07-18 wave4-626 for the
  Admiral / a future Charter refresh to adjudicate.
