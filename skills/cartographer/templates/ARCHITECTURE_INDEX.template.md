# Architecture Index

Dense navigation for the current-only structural map.

## Structural Hierarchy

- `struct:<system-context>` `<label>`
  - `struct:<container>` `<label>`
    - `struct:<component>` `<label>`
      - `struct:<code-path>` `<label>`
        - `struct:<module>` `<path>`

## Node Inventory

| Node | Level | Parent | Packet | Status | Confidence |
|---|---|---|---|---|---|
| `struct:<id>` | `<level>` | `struct:<id> | none` | `packets/<name>.md` | `<status>` | `<confidence>` |

## Unmapped / Disputed / Stale

| Node/path | Class | Current truth | Next route |
|---|---|---|---|
| `<struct:<id> or path>` | `<mismatch>` | `<fact>` | `Cartographer | Triage | user question` |

## Overlay Anchors

| Anchor | Kind | Parent | Structural links |
|---|---|---|---|
| `purpose:<id>` | `purpose` | `<purpose:<id> or none>` | `struct:<id>` |
| `constraint:<id>` | `constraint` | `<purpose:<id> | constraint:<id> | none>` | `struct:<id>` |

## Generated Map Artifacts

- `MAP_BUILD.md`: `<configured | not configured>`
- `docs/architecture/generated/map.json`: `<current | stale | absent | not configured>`
- Generated Markdown views: `<path or not configured>`

## Source Rules

- Packets and overlays are dense current-state agent context.
- Generated map artifacts are derived from packets, overlays, and repo source tree.
- Diagrams and rendered pages are derivative views.
- Future work, backlog, redesign, and missing implementation route to Triage.
