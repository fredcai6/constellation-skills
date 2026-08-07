# overread_corpus — SYNTHETIC fixture transcripts

**These four `.jsonl` files are hand-built, synthetic fixtures.** They are **not** captured
from real agent runs. `.agent-work/archive/` (this gate's only in-scope copy source, per the
handoff for issue-227 gate g1) contains no raw JSONL tool-call transcripts — only narrative
markdown (results, handoffs, ADMIRAL_LOG.md) and near-empty `.txt` transcripts with no tool-call
detail. See `implementer-plan.json` gate `m1-explore`'s `--why` for the search that established
this.

The real transcript schema they are modeled on — `type`, `message.content[]` blocks with
`type: "tool_use"` / `type: "tool_result"`, `isSidechain`, `session_id`, `timestamp` — is the
same schema already precedented in this repo at `tests/fixtures/golden_transcript.jsonl`
(used by `tests/test_gauge_writer.py`) and consumed in production by
`scripts/hooks/gauge_writer_hook.py`. It is also the schema the epic-226 excursion
(`.agent-work/archive/2026-07-24-explore-design-thrust/excursions/x1-overread-RESULT.md`)
used against real `C:\Users\fredc\.claude\projects\...\*.jsonl` session logs — a path outside
this gate's allowed copy sources, hence synthetic here.

Each file represents one simulated agent "run" (one transcript). Deliberately small and hand-
authored so every expected count is known and checkable by inspection:

| file | intent | expected structural reads |
|---|---|---|
| `run-clean-explorer.jsonl` | an agent that never touches engine/spine internals | **0** |
| `run-heavy-scaffolding.jsonl` | full `spine.json` read, `checklist_engine.py` source read, `cycle-2.json` read, plus 2 non-matching reads mixed in (discrimination check) | **3** |
| `run-mixed-with-journal.jsonl` | one real structural read (`spine.json`), plus a `.journal` file and a `references/*.md` read that must NOT count | **1** |
| `run-malformed-line.jsonl` | one corrupted JSON line (must be skipped, not crash the scan) alongside 2 genuine `checklist_engine.py` source reads | **2** |

Aggregate across the committed corpus: **0 + 3 + 1 + 2 = 6**.
