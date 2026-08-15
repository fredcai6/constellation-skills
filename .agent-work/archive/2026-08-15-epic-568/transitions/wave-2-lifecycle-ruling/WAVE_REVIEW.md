## Lifecycle float ruling

The lifecycle cluster was correctly floated before implementation. All four triggers fired: semantic ambiguity, migration, destructive backfill risk, and multi-wave decomposition. The human retained explicit release, prohibited historical bulk mutation, chose contained child references and a nonterminal-child archive guard, and split high-risk liveness/durable-root/harvest work into later waves.

The immediate wave is now three bounded items: #530, #510, and Codex tier/worktree routing. #530 precedes #441; #510 is advisory-only; the Codex harness preserves Claude defaults while adding an explicitly selected repo-local worktree root.
