---
name: constellation-docent
description: Generate a self-contained static HTML explainer site from Cartographer map truth, stamped so a stale site is visibly flagged. Use when a human needs to explore a codebase's architecture and the agent-facing map under docs/architecture/ is too dense to browse.
---

# Constellation Docent

The Constellation map (`docs/architecture/`) is written for agents: a long
`index.md` reconcile ledger, one packet per subsystem, sparse overlays, and
decision records. It is planning-authoritative but not something a **human** can
comfortably *explore*. Docent turns that same map truth into a navigable,
self-contained static website a human can open and read.

**Protected intent — freshness is load-bearing.** A stale pretty site is *worse*
than none: it looks authoritative while lying. Every site you generate embeds a
digest of the exact map source it was built from, and the bundled
`scripts/docent_freshness.py` proves fresh/stale by exit code. Never ship a site
without the stamp, and never hand-edit the stamp.

Docent **reads** map truth; it never edits `index.md`, packets, overlays, or
decision records. It is on-demand: a human runs it to (re)generate.

This is a **method**, not a program. You generate the site by following the
steps below using judgment — there is no large generator to run. The one shipped
tool is the deterministic freshness stamp/check.

## Inputs — read map truth in this fixed order

Locate the map root (default `docs/architecture/`). Read, in order, so later
narrative is grounded in the structural truth read first:

1. **`index.md`** — the reconcile ledger. Skim for the system's purpose, the
   subsystem list, dependency edges, and open questions. It is long; extract the
   current shape, not the history.
2. **`packets/**`** — one file per subsystem. Each has a YAML header
   (`id`, `level`, `path`, `status`, `confidence`) and prose: Responsibility,
   Key Modules, Data Flow, Dependencies, Known Limits. This is the spine of the
   per-subsystem pages.
3. **`overlays/**`** — `purposes.yml`, `constraints.yml` (and any others):
   durable purpose/constraint/claim nodes plus `relationships` edges
   (`serves`, `constrained-by`, `explained-by`, `verified-by`, …). These are the
   source for the boundaries/dependencies view and the decision links.
4. **`decisions/**`** — one record per decision (`# Architecture Decision: …`,
   a Status block with id/anchors, Question Resolved, Decision, Rationale,
   Rejected Alternatives). One card per record on the decisions page.
5. **`generated/map.json`** — **only when present.** If the project builds a
   machine map, prefer its structured nodes/edges to corroborate the prose;
   f1Brainz and many projects have none, so build directly from the packets.

Then a **light code read for narrative color** only where a packet is thin or a
boundary is unclear — enough to write an honest sentence, not a re-derivation of
the map. Map truth leads; code fills gaps.

## Page structure

Multiple pages linked by **relative** paths (preferred over one giant scroll):

- **`index.html` — Overview.** What the system is (from `index.md` + purposes),
  the subsystem list linking to each packet page, the top-level dependency
  picture, and the **freshness badge/banner**.
- **One page per packet/subsystem** (`subsystem-<id>.html` or similar): the
  packet's purpose, key modules, boundaries, dependencies, known limits, and the
  "why" — map truth first, code color where needed. One page per packet, no
  exceptions; the page count must equal the packet count.
- **`boundaries.html` — Boundaries & dependencies.** The structural edges (who
  depends on whom, cross-region constraints) as a readable adjacency/graph,
  sourced from the overlays' `relationships` and any `map.json`. Show constraint
  edges (e.g. "must not import X") prominently — they are the load-bearing rules.
- **`decisions.html` — Decisions.** One card per decision record: the question,
  the choice, the rationale, and which subsystems it governs (link back to their
  pages via the decision's structural anchors).

## Self-contained HTML

The site must open from `file://` under a CSP-locked browser: **no external
resource loads** (inline all CSS/JS, no CDN/fonts/remote images/`fetch`/`XHR`),
restrained dark/light-aware styling, and a shared inline CSS block so pages read
as one system. Full hard constraints + the self-containment grep check:
`references/self-contained-html.md`.

## Freshness stamp + STALE banner

The bundled `scripts/docent_freshness.py` (installed under this skill's
`scripts/`) owns the digest. Two steps:

1. **Compute the stamp** over the map source:

   ```
   python <this-skill>/scripts/docent_freshness.py stamp --map-root <map-root>
   ```

   It prints a 64-hex SHA-256 digest over the sorted source-map file set
   (`index.md`, `packets/**`, `overlays/**`, `decisions/**`, and
   `generated/map.json` when present).

2. **Embed it** in every page's `<head>` as the canonical marker:

   ```html
   <meta name="docent-map-stamp" content="<64-hex-digest>">
   ```

   Also record a human-readable freshness line in the overview's badge: the
   short digest, the generation date, and the map root it was built from.

3. **Render the STALE banner.** Include a prominent, normally-hidden banner
   element plus a tiny inline script. The site cannot recompute the digest from
   `file://` (it has no source tree), so the banner is driven by two honest
   signals, both inline and network-free:
   - **Age:** embed the generation date; if the page is opened many days later,
     the script softens the badge into a "generated N days ago — verify
     freshness" note. Age is a heuristic, not proof.
   - **Explicit stale flag:** the script reveals the hard STALE banner when the
     page URL carries `?stale` (or a `docent-stale` marker). A reconcile/CI step
     that ran `check` and found divergence links humans to `index.html?stale=1`.

   Tell the reader plainly in the badge: the authoritative live gate is
   `docent_freshness.py check` — the embedded stamp is authoritative only for
   *which map the site was built from*.

4. **Verify before you hand it over:**

   ```
   python <this-skill>/scripts/docent_freshness.py check <site> --map-root <map-root>
   ```

   must exit 0 (fresh) immediately after generation. Then confirm no external
   resource loads per `references/self-contained-html.md`.

## Output location

- Real projects: **`docs/explainer/`** — beside `docs/architecture/` (the
  source) without being owned by Cartographer.
- Never write into a read-only source project. When the map you read lives in
  another repo, the site still goes in *your* repo.

## Guardrails

- Read-only over the map: never edit `index.md`, packets, overlays, or
  decisions.
- No SPA/build toolchain, no live server, no marketing page.
- Page count equals packet count; every decision record gets a card; the
  boundaries view comes from the overlays' relationships, not invention.
- Ship the stamp, verify `check` exits 0, verify self-containment — every time.
