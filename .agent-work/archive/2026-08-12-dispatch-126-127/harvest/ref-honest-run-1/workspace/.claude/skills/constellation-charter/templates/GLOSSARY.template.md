# Project Glossary

Shared conceptual baseline for humans and agents. Define current meanings only; do not include debate history or uncertain terms.

| Term | Meaning | Usage notes |
|---|---|---|
| `capability` | A current, observable thing the system does; the primary durable behavior abstraction in the map. | Present tense. Prefer over "requirement"/"use case" when naming behavior. |
| `example` / `use-case` | A concrete instance of a capability in action, recorded only under that capability. | Never a standalone requirement or its own map node. |
| `event` | A current, named signal a struct or capability emits. | Durable only when architecturally meaningful (boundary-crossing or a contract), not every runtime event. |
| `<term>` | `<short current meaning>` | `<optional note>` |

## `<term>`

**Meaning:** `<current project meaning>`  
**Do not confuse with:** `<nearby terms or omit>`  
**Usage notes:** `<only if needed for future agent behavior>`
