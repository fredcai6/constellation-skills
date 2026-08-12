## Wave review -- w5-door-only

Six issues merged: N1, A (9a056105), B (90b39e2b), D1 (3c0fc7d2), E1 (094f573a) and C1 (0ab7ecab). Suite on merged main: 2689 passed, 3 skipped, 1121 subtests. #555 carried unworked for a third wave; its disposition is still the human's.

**The wave did what it set out to do.** All eighteen engine verbs are reachable through the door. A crew dispatched with a spine and no handoff document drives it and is recorded as succeeding. A crew that cannot satisfy a check blocks, records a parent, and is reported as blocked rather than as failed. And for the first time a test asks whether a shipped template's gates are satisfiable by a real run.

**Cold review earned its cost.** Three of six workstreams were blocked and reworked; one was blocked twice. Two of the blocks caught a fix that had flipped its defect's sign rather than removed it -- a gate that could not fail replaced by one that could not pass, and a launcher that recorded a successful crew as failed. Neither would have been caught by reading the diff; both reviewers found them by running something.

**The finding that changes the plan is about the Admiral, not the code.** Roughly ten work spines and seven review surveys were hand-authored this wave, and four carried checks that could not do their job: an unquoted selector, a probe importing a module that needs a bound spine, a call using a parameter name the signature does not have, and a population filter wrong twice. Each was caught downstream -- by a crew, a reviewer, or argparse -- and none by its author. The epic's thesis is that prose instruction is a liability because the reader may be weaker than the writer. This is the same defect one level up: the check is only as good as the hand that wrote it, and that hand is unchecked.

C1 shipped the tool that can refuse a bad spine. Nothing yet writes a good one. That is wave 6.

**Two contradictions are settled by ruling rather than carried forward.** B's test treats `<exact test command>` as a legitimate authoring-time slot; C1's lint reports the same occurrences as faults. Both are right about different things: a placeholder in a template is a slot, and a placeholder surviving into an instantiated spine is a check that can never run. The lint keys on which it is looking at. Separately, `validate_spine --sweep` reports `falsifiable-all-null` on the context gate of nine of twelve role templates -- a gate that cannot refuse anything. Its uniformity is a default, not a decision, because no template states the choice. A gate with no checkable postcondition must say it is qualitative; silence is refused.

**Carried:** #555 unworked and verbatim. Windows launch parked as a standing constraint. Crew-to-crew messaging parked: a headless crew is on the peer graph but cannot reach a parent named by a descriptive string, so the durable blocked-gate path E1 shipped is the mechanism and messaging is an optimisation nothing may depend on.
