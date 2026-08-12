# Docent self-containment — hard constraints + verification

Docent's generated site must be a self-contained static artifact: it opens from
`file://` under a CSP-locked browser with **no external resource loads**. These
are the hard constraints the SKILL.md body points to, plus the grep check that
verifies self-containment before hand-off.

## Hard constraints

- **No external resource loads.** Inline all CSS in a `<style>` and all JS in a
  `<script>`; no CDN, no external fonts, no remote images, no `fetch`/`XHR`/
  WebSocket. The site must open from `file://` under a CSP-locked browser.
  "Self-contained" means no external *resource loads*, not one physical file —
  relative links between local pages are fine.
- **Restrained, readable, dark/light aware.** A docs artifact, not a landing
  page. Use `prefers-color-scheme`, system fonts, generous line-height, a
  max-width column. If you draw the dependency graph, prefer inline SVG or a CSS
  adjacency grid — no graph library.
- Keep the CSS in a small shared block you paste into each page's `<head>` (or a
  single inlined `styles` string you emit into every page) so the pages read as
  one system.

## Self-containment verification recipe

After `docent_freshness.py check` exits 0, confirm no external resource loads,
e.g. grep the site for `http(s)://`, protocol-relative `src="//"`/`href="//"`,
`<script src=`, `<link … href="http`, `fetch(`, `XMLHttpRequest` — there must be
none.
