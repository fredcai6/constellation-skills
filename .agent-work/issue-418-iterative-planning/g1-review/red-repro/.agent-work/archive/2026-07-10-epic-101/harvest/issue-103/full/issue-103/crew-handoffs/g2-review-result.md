# REVIEW_RESULT — g2 Docent extraction

REVIEW_VERDICT: APPROVE

Gate: `g2` — Docent extraction. Review target: UNCOMMITTED working tree in
`C:\Programs\constellation-wt-103` (branch `constellation/issue-103`).
All claims reproduced independently; extracted text diffed against
`git show HEAD:skills/docent/SKILL.md`.

## Per-check findings (each reproduced)

### 1. New reference file exists with ALL constraints — PASS
`skills/docent/references/self-contained-html.md` exists (untracked). Diffed its
constraint text against the block removed from HEAD's SKILL.md. All four required
elements present, **verbatim** (relocation only, nothing reworded or dropped):
- No-external-resource-loads rule — inline CSS/JS, no CDN/fonts/remote images/
  `fetch`/`XHR`/**WebSocket**, `file://` under CSP, "no external *resource loads*
  not one physical file" caveat. (ref lines 10-14 == HEAD lines 75-79)
- Restrained/readable/dark-light-aware rule — `prefers-color-scheme`, system
  fonts, max-width column, inline SVG / CSS adjacency grid, **no graph library**.
  (ref lines 15-18 == HEAD lines 80-83)
- Shared-CSS-block rule — small shared block pasted into each `<head>`.
  (ref lines 19-21 == HEAD lines 84-86)
- Grep verification recipe — `http(s)://`, protocol-relative `src="//"`/`href="//"`,
  `<script src=`, `<link … href="http`, `fetch(`, `XMLHttpRequest` → none.
  (ref lines 25-28 == HEAD lines 133-136)

Confirmed: **no constraint dropped.** Body's condensed summary omits some words
(e.g. "WebSocket", "no graph library"), but those live intact in the reference,
which the criterion designates as the source of truth.

### 2. One-hop pointer in body, full block no longer inlined — PASS
`grep -c "references/self-contained-html.md" skills/docent/SKILL.md` = **2**
(line 79 in the Self-contained HTML section, line 127 in the grep step). The old
`## Self-contained HTML — hard constraints` bullet block is gone from the body,
replaced by a condensed paragraph + pointer. No second hop required.

### 3. Freshness method retained in body — PASS
Reproduced grep in SKILL.md:
- `docent_freshness.py stamp` (line 89) and `docent_freshness.py check` (lines 117, 123) both present.
- STALE banner doctrine present (line 81 heading "Freshness stamp + STALE banner", line 105 "Render the STALE banner", line 112 "Explicit stale flag").
- "stale is worse than none" preamble present (line 14: "A stale pretty site is *worse*").
Freshness protection not weakened.

### 4. Filename does NOT match `global-*.md` — PASS
`skills/docent/references/` contains only `self-contained-html.md`. No `global-*` match.

### 5. Only `skills/docent/**` changed — PASS
`git status --porcelain`:
- ` M skills/docent/SKILL.md`
- `?? skills/docent/references/` (new)
Exclusions verified untouched: `skills/commander/**`, `_shared/**`, `tests/**`,
`scripts/docent_freshness.py` — none appear in status.

### 6. Suite green — PASS
`py -m pytest tests/test_install_constellation.py tests/test_docent_freshness.py -q`
→ **47 passed, 118 subtests passed in 3.31s**.

## Blockers
None.

## Out-of-scope observations
- The body's condensed paragraph paraphrases rather than quotes the constraints
  (drops "WebSocket" and "no graph library" from the inline summary). This is
  acceptable under the task (full constraints relocated to the reference), and
  the reference retains them verbatim. Noting only for awareness; not a defect.

## Workflow feedback
- Handoff was precise and self-verifying; the explicit "diff extracted text
  against `git show HEAD`" instruction made the no-constraint-dropped check
  unambiguous and fast. No friction.
