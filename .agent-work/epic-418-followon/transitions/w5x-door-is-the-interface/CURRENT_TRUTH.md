## Current planning truth

Agents drive their spines through the MCP door and never touch the engine CLI. The CLI is an implementation detail behind the door; anything reachable only through it is a defect.

Three of the four definition-of-done items now hold. A dispatched crew drives its own spine through the door, measured from its own call record. A respawn resumes its lease rather than force-claiming, because the lease keys on the assignment and the identity is derived from the spine's own work_id. No shipped entry definition hardcodes an interpreter: the value resolves per machine at install time, and the committed file still works as committed.

The item that does not yet hold is the one this wave is for: **agent instructions still name the CLI.** Nineteen mentions across thirteen corpus files, and nine occurrences of an `<engine>` token that nothing in the corpus defines -- every one of them inside a CLI-fallback clause. The door reaches thirteen of the engine's eighteen verbs, so removing those clauses today would strand an agent on a verb it could no longer reach. Hence the order: close the verb gap, then withhold the engine, then rewrite the instruction.

Withholding is not omission. A crew's grant includes unrestricted Bash, which reaches the engine whatever the MCP allow-list says, so enforcement needs a deny mechanism rather than a shorter list.

**Nonbinding forecast.** Once the CLI is unreachable, adoption becomes measurable for the first time: door use can no longer be explained by preference. #421 opens on the same condition. Windows launch stays parked as a standing constraint that entry definitions remain configurable, with every hardcode recorded on #539.
