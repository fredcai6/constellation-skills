# Binding-store sweep plan (#419, dry run)

Read at: 2026-08-06T05:22:15Z
Store: `C:\Programs\constellation-skills\.agent-work\.spine-rail-binding.json`

**Totals: 6 keys, 64 entries.** KEEP 1, DROP 63.

The store is a **moving target** — sibling runs claim and release continuously, and it was measured at 54 entries when this run was planned and 64 now. Every count here is pinned to this read.

**What the spec's UNCONDITIONAL rule would have dropped: 64 entries** (every bare-key entry). This sweep drops 63 instead, sparing 1 bare-key entries that are live right now — including this epic's own in-flight runs. See the module docstring for why.

## DROP

| key | spine | exists | reason |
|---|---|---|---|
| `05c5ec39-68b1-45f0-a55f-d78261009133` | `C:\Programs\constellation-skills\.agent-work\epic-267\spine.json` | True | lease not active (status='released') |
| `05c5ec39-68b1-45f0-a55f-d78261009133` | `C:\Programs\constellation-skills\.agent-work\governor-262\spine.json` | False | spine file does not exist |
| `05c5ec39-68b1-45f0-a55f-d78261009133` | `C:\Programs\constellation-skills\.agent-work\governor-264\spine.json` | False | spine file does not exist |
| `05c5ec39-68b1-45f0-a55f-d78261009133` | `C:\Programs\constellation-skills\.agent-work\governor-262\g1-review\review.json` | False | spine file does not exist |
| `05c5ec39-68b1-45f0-a55f-d78261009133` | `C:\Programs\constellation-skills\.agent-work\governor-264\crew-plans\g1-implement-plan.json` | False | spine file does not exist |
| `05c5ec39-68b1-45f0-a55f-d78261009133` | `C:\Programs\constellation-skills\.agent-work\governor-264\crew-plans\g2-implement-plan.json` | False | spine file does not exist |
| `05c5ec39-68b1-45f0-a55f-d78261009133` | `C:\Programs\constellation-skills\.agent-work\governor-264\g2-review\review.json` | False | spine file does not exist |
| `05c5ec39-68b1-45f0-a55f-d78261009133` | `C:\Programs\constellation-skills\.agent-work\governor-264\crew-plans\g3-implement-plan.json` | False | spine file does not exist |
| `05c5ec39-68b1-45f0-a55f-d78261009133` | `C:\Programs\constellation-skills\.agent-work\governor-264\g3-review\review.json` | False | spine file does not exist |
| `05c5ec39-68b1-45f0-a55f-d78261009133` | `C:\Programs\constellation-skills\.agent-work\governor-264\crew-plans\g4-implement-plan.json` | False | spine file does not exist |
| `adcabce1-b0c1-4ef0-b3d8-085e157af6ca` | `C:\Programs\constellation-skills\.agent-work\301\spine.json` | False | spine file does not exist |
| `adcabce1-b0c1-4ef0-b3d8-085e157af6ca` | `C:\Programs\constellation-skills\.agent-work\300\spine.json` | False | spine file does not exist |
| `adcabce1-b0c1-4ef0-b3d8-085e157af6ca` | `C:\Programs\constellation-skills\.agent-work\issue-303\execute.json` | False | spine file does not exist |
| `adcabce1-b0c1-4ef0-b3d8-085e157af6ca` | `C:\Programs\constellation-skills\.agent-work\301\g1-review-2\review.json` | False | spine file does not exist |
| `adcabce1-b0c1-4ef0-b3d8-085e157af6ca` | `C:\Programs\constellation-skills\.agent-work\301\crew-handoffs\g2-implementer-plan.json` | False | spine file does not exist |
| `adcabce1-b0c1-4ef0-b3d8-085e157af6ca` | `C:\Programs\constellation-skills\.agent-work\301\g2-review\review.json` | False | spine file does not exist |
| `adcabce1-b0c1-4ef0-b3d8-085e157af6ca` | `C:\Programs\constellation-skills\.agent-work\301\g2-review-2\review.json` | False | spine file does not exist |
| `adcabce1-b0c1-4ef0-b3d8-085e157af6ca` | `C:\Programs\constellation-skills\.agent-work\301\crew-handoffs\g3-implementer-plan.json` | False | spine file does not exist |
| `adcabce1-b0c1-4ef0-b3d8-085e157af6ca` | `C:\Programs\constellation-skills\.agent-work\301\crew-handoffs\g4-implementer-plan.json` | False | spine file does not exist |
| `adcabce1-b0c1-4ef0-b3d8-085e157af6ca` | `C:\Programs\constellation-skills\.agent-work\301\g4-review\review.json` | False | spine file does not exist |
| `adcabce1-b0c1-4ef0-b3d8-085e157af6ca` | `C:\Programs\constellation-skills\.agent-work\301\crew-handoffs\g4-rework-plan.json` | False | spine file does not exist |
| `adcabce1-b0c1-4ef0-b3d8-085e157af6ca` | `C:\Programs\constellation-skills\.agent-work\300\g3-implement\PLAN.json` | False | spine file does not exist |
| `adcabce1-b0c1-4ef0-b3d8-085e157af6ca` | `C:\Programs\constellation-skills\.agent-work\300\g3-review\review.json` | False | spine file does not exist |
| `adcabce1-b0c1-4ef0-b3d8-085e157af6ca` | `C:\Programs\constellation-skills\.agent-work\300\g1-implement\PLAN-rework2.json` | False | spine file does not exist |
| `adcabce1-b0c1-4ef0-b3d8-085e157af6ca` | `C:\Programs\constellation-skills\.agent-work\299\spine.json` | False | spine file does not exist |
| `adcabce1-b0c1-4ef0-b3d8-085e157af6ca` | `C:\Programs\constellation-skills\.agent-work\issue-304\spine.json` | False | spine file does not exist |
| `adcabce1-b0c1-4ef0-b3d8-085e157af6ca` | `C:\Programs\constellation-skills\.agent-work\issue-309\spine.json` | False | spine file does not exist |
| `adcabce1-b0c1-4ef0-b3d8-085e157af6ca` | `C:\Programs\constellation-skills\.agent-work\issue-305\spine.json` | False | spine file does not exist |
| `adcabce1-b0c1-4ef0-b3d8-085e157af6ca` | `C:\Programs\constellation-skills\.agent-work\issue-304\g1-review-2\review.json` | False | spine file does not exist |
| `adcabce1-b0c1-4ef0-b3d8-085e157af6ca` | `C:\Programs\constellation-skills\x.json` | False | spine file does not exist |
| `adcabce1-b0c1-4ef0-b3d8-085e157af6ca` | `C:\Programs\constellation-skills\.agent-work\issue-305\g1-review-rework\review.json` | False | spine file does not exist |
| `adcabce1-b0c1-4ef0-b3d8-085e157af6ca` | `C:\Programs\constellation-skills\.agent-work\issue-305\crew\g2-implement-plan.json` | False | spine file does not exist |
| `adcabce1-b0c1-4ef0-b3d8-085e157af6ca` | `C:\Programs\constellation-skills\.agent-work\issue-304\g4-implementer-plan.json` | False | spine file does not exist |
| `adcabce1-b0c1-4ef0-b3d8-085e157af6ca` | `C:\Programs\constellation-skills\.agent-work\issue-305\crew\g2-implement-rework-plan.json` | False | spine file does not exist |
| `adcabce1-b0c1-4ef0-b3d8-085e157af6ca` | `C:\Programs\constellation-skills\x` | False | spine file does not exist |
| `adcabce1-b0c1-4ef0-b3d8-085e157af6ca` | `C:\Programs\constellation-skills\.agent-work\issue-305\g2-review-rework\review.json` | False | spine file does not exist |
| `adcabce1-b0c1-4ef0-b3d8-085e157af6ca` | `C:\Programs\constellation-skills\.agent-work\issue-305\g3-review\review.json` | False | spine file does not exist |
| `adcabce1-b0c1-4ef0-b3d8-085e157af6ca` | `C:\Programs\constellation-skills\$P` | False | spine file does not exist |
| `adcabce1-b0c1-4ef0-b3d8-085e157af6ca` | `C:\Programs\constellation-skills\.agent-work\issue-305\execute.json` | False | spine file does not exist |
| `adcabce1-b0c1-4ef0-b3d8-085e157af6ca` | `C:\Programs\constellation-skills\.agent-work\issue-305\g4-review\review.json` | False | spine file does not exist |
| `adcabce1-b0c1-4ef0-b3d8-085e157af6ca` | `C:\Programs\constellation-skills\.agent-work\issue-308\spine.json` | False | spine file does not exist |
| `adcabce1-b0c1-4ef0-b3d8-085e157af6ca` | `C:\Programs\constellation-skills\.agent-work\issue-307\spine.json` | False | spine file does not exist |
| `adcabce1-b0c1-4ef0-b3d8-085e157af6ca` | `C:\Programs\constellation-skills\.agent-work\issue-308\execute.json` | False | spine file does not exist |
| `adcabce1-b0c1-4ef0-b3d8-085e157af6ca` | `C:\Programs\constellation-skills\.agent-work\issue-308\crew-handoffs\g5-implement-plan.json` | False | spine file does not exist |
| `adcabce1-b0c1-4ef0-b3d8-085e157af6ca` | `C:\Programs\constellation-skills\.agent-work\issue-310\spine.json` | False | spine file does not exist |
| `adcabce1-b0c1-4ef0-b3d8-085e157af6ca` | `C:\Programs\constellation-skills\.agent-work\issue-310\g1-implementer-plan.json` | False | spine file does not exist |
| `3a4f3d5c-6d29-4e12-ae9a-287ecb603d1f` | `C:\Programs\constellation-skills\.agent-work\explore-post-phase1\spine.json` | False | spine file does not exist |
| `9cbc67f4-bd23-4507-955f-e873fbe42d6f` | `C:\Programs\constellation-skills\.agent-work\epic-267\spine.json` | True | lease not active (status='released') |
| `ac5ce24b-915b-42be-bafe-18644b7f0713` | `C:\Programs\constellation-skills\.agent-work\epic-267\spine.json` | True | lease not active (status='released') |
| `e8249451-5c48-417b-9f38-cf2dd40d405c` | `C:\Programs\constellation-skills\$E` | False | spine file does not exist |
| `e8249451-5c48-417b-9f38-cf2dd40d405c` | `C:\Programs\constellation-skills\.agent-work\issue-422-wire-invariants\spine.json` | False | spine file does not exist |
| `e8249451-5c48-417b-9f38-cf2dd40d405c` | `C:\Programs\constellation-skills\.agent-work\b420-engine-channel\spine.json` | False | spine file does not exist |
| `e8249451-5c48-417b-9f38-cf2dd40d405c` | `C:\Programs\constellation-skills\.agent-work\issue-419-governor-identity\spine.json` | False | spine file does not exist |
| `e8249451-5c48-417b-9f38-cf2dd40d405c` | `C:\Programs\constellation-skills\.agent-work\b420-engine-channel\crew-handoffs\g1-implement\IMPLEMENTER_PLAN.json` | False | spine file does not exist |
| `e8249451-5c48-417b-9f38-cf2dd40d405c` | `C:\Programs\constellation-skills\.agent-work\b420-engine-channel\execute.json` | False | spine file does not exist |
| `e8249451-5c48-417b-9f38-cf2dd40d405c` | `C:\Programs\constellation-skills\.agent-work\issue-419-governor-identity\g2-IMPLEMENTER_PLAN.json` | False | spine file does not exist |
| `e8249451-5c48-417b-9f38-cf2dd40d405c` | `C:\Programs\constellation-skills\.agent-work\issue-419-governor-identity\g2-review\review.json` | False | spine file does not exist |
| `e8249451-5c48-417b-9f38-cf2dd40d405c` | `C:\Programs\constellation-skills\.agent-work\issue-419-governor-identity\g3-IMPLEMENTER_PLAN.json` | False | spine file does not exist |
| `e8249451-5c48-417b-9f38-cf2dd40d405c` | `C:\Programs\constellation-skills\.agent-work\issue-419-governor-identity\g3-review\review.json` | False | spine file does not exist |
| `e8249451-5c48-417b-9f38-cf2dd40d405c` | `C:\Programs\constellation-skills\.agent-work\issue-419-governor-identity\g3r2-review\review.json` | False | spine file does not exist |
| `e8249451-5c48-417b-9f38-cf2dd40d405c` | `C:\Programs\constellation-skills\x` | False | spine file does not exist |
| `e8249451-5c48-417b-9f38-cf2dd40d405c` | `C:\Programs\constellation-skills\.agent-work\issue-419-governor-identity\g4-IMPLEMENTER_PLAN.json` | False | spine file does not exist |
| `e8249451-5c48-417b-9f38-cf2dd40d405c` | `C:\Programs\constellation-skills\.agent-work\issue-419-governor-identity\g4-review\review.json` | False | spine file does not exist |

## KEEP

| key | spine | exists | reason |
|---|---|---|---|
| `e8249451-5c48-417b-9f38-cf2dd40d405c` | `C:\Programs\constellation-skills\.agent-work\epic-418\spine.json` | True | lease active (admiral-epic-418) |
