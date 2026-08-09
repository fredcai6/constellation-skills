# Project Glossary

Shared conceptual baseline for humans and agents — the source of truth for *one name for one thing*.
Define current meanings only; do not include debate history or uncertain terms.

| Term | Short | Meaning | Instead of | Usage notes |
|---|---|---|---|---|
| `spine` | — | The gated checklist file the engine drives a run through, one step at a time. | — | Read and change it only through the engine, never by hand. |
| `gate` | — | One step in a spine: an imperative plus the preconditions and postconditions the engine checks to open and close it. | — | Engine text also says "step"; both mean this. |
| `lease` | — | The exclusive claim one session holds on a work area, so a second agent cannot drive the same spine. | — | Release it last; a run is not done while it holds the lease. |
| `latitude` | — | The scope of actions a role may take without asking the human. | — | A lease is exclusivity; latitude is permission. |
| `gauge` | — | The context governor's written reading of one agent's context fill: the model plus the filled fraction of its window. | — | — |
| `trip` | — | The event where a gauge reading crosses a band (SOFT or HARD) and the engine restricts what the agent may do next. | — | HARD refuses the verbs that BEGIN work at a gate — `start` and `reopen` — until a refresh-request is pending; the `advance` that closes the gate you are already in is never refused, only closing it silently is. |
| `episode` | — | One stored record of something observed in a run. | — | Lives under `episodes/active/` or `episodes/retired/`. A record, never a rule. |
| `episode store` | — | The durable home of episodes. | ~~record store~~ — use **episode store** | — |
| `harvest` | — | Gathering what a run's own artifacts recorded and writing it into the episode store as episodes. | — | The direction is INTO the store. There is no reading harvested episodes back out as rules. |
| `arm` | — | One group of runs in a before-and-after comparison; the PRE arm runs before a change, the POST arm after. | ~~apparatus~~, ~~capture rig~~ — use **arm** | Borrowed from clinical-trial design. |
| `instrument` | — | The machinery that records measurements during a run. | — | As a verb, "instrumented" means fitted with that machinery. |
| `ablation` | — | An arm with one piece deliberately removed, to show whether that piece causes the effect. | — | — |
| `rhyme` | — | Two or more episodes showing the same underlying pattern. | — | Not a duplicate — a rhyme is a shared shape, not the same event twice. |
| `graduate` | — | Promote a finding from run artifacts into durable doctrine (skills or docs). | — | — |
| `supersede` | — | A newer issue or artifact replaces an older one; the older closes with a pointer to its replacement. | — | — |
| `corpus` | — | The full set of installed constellation skills, references, and templates. | — | — |
| `kernel` | — | The part of a role's prose that must always be loaded: role identity, the trigger to use the spine, and project focus. | — | — |
| `kernel-break` | — | The proposed split of a role's always-loaded prose into a kernel plus on-demand fragments (Stratum B2). | — | Not taken if deletion or relocation alone shrinks the prose enough — that outcome is success. |
| `two-bin rule` | — | Every enforced invariant sits in one of two bins: checked by a command, or attested by a named human. Prose alone enforces nothing. | — | Doctrine B0.3. |
| `conjunct` | — | One condition in a set that must all pass together. | — | A set with an untested member cannot pass. |
| `scoped null` | — | A failure verdict limited to exactly what was tested, stated together with what was NOT tested. | — | Report "this check failed", never "this approach is impossible". |
| `excursion` | — | A dispatched investigation that answers one named question during an exploration. | — | Types: research, prototype, design-it-twice. |
| `projection` | — | The engine's rendered view of spine state — what `current` prints. | — | Agents drive from the projection, never from the JSON file. |
