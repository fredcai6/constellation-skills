# Project Glossary

Shared conceptual baseline for humans and agents — the source of truth for *one name for one thing*.
Define current meanings only; do not include debate history or uncertain terms.

| Term | Short | Meaning | Instead of | Usage notes |
|---|---|---|---|---|
| `capability` | — | A current, observable thing the system does; the primary durable behavior abstraction in the map. | ~~requirement~~, ~~use case~~ — use **capability** for behavior | Present tense. |
| `example` / `use-case` | — | A concrete instance of a capability in action, recorded only under that capability. | — | Never a standalone requirement or its own map node. |
| `event` | — | A current, named signal a struct or capability emits. | — | Durable only when architecturally meaningful (boundary-crossing or a contract), not every runtime event. |
| `<term>` | `<ABBR or —>` | `<short current meaning>` | `~~<variant>~~ — use **<term>**` | `<optional note>` |

## Fields

- **Term** — the full canonical name; the one true name for the concept.
- **Short** — its accepted abbreviation or acronym, or `—`. Term and Short together are the expansion.
- **Meaning** — one line, current. Says what the thing *is*, not what it is "responsible for."
- **Instead of** — variants a reader might meet elsewhere, each a one-way redirect: *not this → use
  **Term***. It retires a variant; it never offers a synonym to swap in, so a term with an *Instead of*
  entry has exactly one accepted form — the Term.
- **Usage notes** — any other constraint on use (tense, when the term is durable) kept only when it
  changes future agent behavior.

## `<term>`

A detail block, only for a term that needs more than a table row.

**Meaning:** `<current project meaning>`  
**Do not confuse with:** `<nearby but distinct term — a different concept, not a variant to retire>`  
**Usage notes:** `<only if needed for future agent behavior>`
