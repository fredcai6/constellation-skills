## Wave review — boundary w3x-door-binding

The planned wave was #555, on the belief that the door not launching on Windows was what blocked adoption. That belief is falsified for this host, and the replacement finding is smaller and more actionable.

**The door works.** It is connected in an interactive session with all 7 tools, and a direct JSON-RPC handshake with `SPINE_FILE` set returns this epic's own `execute` gate and live lease. Nothing is wrong with the server.

**It binds to the wrong spine.** Through the approved door, `spine_status` returns the scratch demo's gate g1. The server binds `SPINE_FILE` at launch from the environment and deliberately refuses to be redirected per call. `grep -rln SPINE_FILE scripts/` returns exactly one file — the server that reads it. `run_crew.py` has zero MCP references. The only places the variable has ever been set are three throwaway measurement scripts under `commander-f2/evidence/g4b/`. That is why F2's arm 3 succeeded and why no dispatched crew ever has.

**Identity is hand-typed and has already drifted four times inside this epic:** a session UUID on the Admiral spine, a never-claimed `None` on the commander spine, and `g2-implement-session` / `g4a-implement-session` on the two implementer spines — while the Admiral spine's own `init` imperative asks for the stable `admiral-epic-418-followon`. Two successive sessions read that instruction and typed a UUID anyway. A typed identity drifts; a derived one cannot.

**Both halves of the fix already exist and were never connected.** `run_crew.py::session_name` mints `constellation/<work-id>/<gate>/<role>/attempt-<n>`, nesting-aware. `checklist_engine.py::claim` already gives idempotent same-id resume, refusal on a different active id, force-with-reason takeover, and staleness self-yield — the exact conflict construct specified. The wave is one wire, plus dropping the `attempt-<n>` tail from the lease identity so a respawn resumes instead of force-claiming.

Windows launch stays parked as a real but separate defect. PR #555's fix at `6b947546` is CI-green, unverified and unreviewed, and still owed a cold review.
