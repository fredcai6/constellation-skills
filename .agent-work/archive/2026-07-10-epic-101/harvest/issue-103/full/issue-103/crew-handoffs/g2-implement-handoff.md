# Implementer Handoff

Concise fragments. Omit filler.

## Gate
`g2` — Docent extraction (self-contained-HTML constraint block → reference)

## Task
Extract the self-contained-HTML **constraint block** from `skills/docent/SKILL.md` into a new one-hop reference `skills/docent/references/self-contained-html.md`. The SKILL.md body keeps the **method** (inputs, page structure, freshness stamp/STALE banner, output location, guardrails) and gains a short pointer to the new reference. Meaning-preserving: no constraint is lost, only relocated.

## Protected Intent
An agent generating a Docent site still has every self-containment rule available one hop away; the SKILL.md body still reads as the complete method. Freshness/stamp doctrine (the load-bearing "stale site is worse than none" protection) stays in the body.

## Test Mode
inspection-only — doc restructure; verified by grep + word counts + suite green (`test_install_constellation.py` + `test_docent_freshness.py`).

## Close Criteria
- New file `skills/docent/references/self-contained-html.md` exists, holds the extracted constraints, and does NOT match `global-*.md`.
- `skills/docent/SKILL.md` body no longer inlines the full constraint block but carries a one-hop pointer to `references/self-contained-html.md`.
- The freshness-stamp method + the shipped-tool commands (`docent_freshness.py stamp` / `check`) stay in the SKILL.md body.
- Suite green: `py -m pytest tests/test_install_constellation.py tests/test_docent_freshness.py -q`.
- Before/after `wc -w` for SKILL.md + word count of the new reference.

## Exact edits

### 1. Create `skills/docent/references/self-contained-html.md`
Move into it, verbatim (as a self-contained reference with a short intro line), the current SKILL.md **"## Self-contained HTML — hard constraints"** section (the three bullets: no external resource loads; restrained/readable/dark-light-aware; keep CSS in a small shared block). ALSO move here the **self-containment verification recipe** currently in the SKILL.md "Freshness stamp + STALE banner" step 4 — the sentence beginning "Then confirm no external resource loads, e.g. grep the site for `http(s)://` ... `XMLHttpRequest` — there must be none." Give the reference a one-line header explaining it holds Docent's self-containment hard constraints + their verification. Keep any TOC out (it will be under ~100 lines).

### 2. Edit `skills/docent/SKILL.md`
- Replace the body of the **"## Self-contained HTML — hard constraints"** section with a 1–3 line summary + pointer, e.g.:
  > ## Self-contained HTML
  > The site must open from `file://` under a CSP-locked browser: **no external resource loads** (inline all CSS/JS, no CDN/fonts/remote images/`fetch`/`XHR`), restrained dark/light-aware styling, and a shared inline CSS block so pages read as one system. Full hard constraints + the self-containment grep check: `references/self-contained-html.md`.
- In the "Freshness stamp + STALE banner" step 4, KEEP the `docent_freshness.py check <site> --map-root` exit-0 verification; replace the inline "grep the site for http(s):// ... XMLHttpRequest" enumeration with a pointer: "then confirm no external resource loads per `references/self-contained-html.md`."
- Leave everything else (Inputs, Page structure, Freshness stamp mechanics, Output location, Guardrails) unchanged.

## Allowed Scope
`skills/docent/SKILL.md` and the new `skills/docent/references/self-contained-html.md`. Nothing else. (Note: `skills/docent/references/` may not exist yet — create it.)

## Specific Exclusions
NOT `skills/commander/**`, NOT `_shared/**`, NOT `tests/**`, NOT `scripts/docent_freshness.py`. Do not rename or move `docent_freshness.py`.

## Constraints
- New reference filename must NOT match `global-*.md` (installer glob pins bundle composition). `self-contained-html.md` is correct.
- Keep the SKILL.md pointer to the new reference (one hop).
- Do not weaken the freshness "stale is worse than none" protection or the stamp/check method.

## Map Anchors (inbound)
- **Structural:** `skills/docent/SKILL.md`, new `skills/docent/references/self-contained-html.md`.
- **Constraints:** no new `global-*.md`; docent freshness tests (`test_docent_freshness.py`) must stay green.

## Deliverable Path Check
- **Committed** — `skills/docent/SKILL.md`, `skills/docent/references/self-contained-html.md`; run `git check-ignore` on each, confirm exit 1.
- **Local-only** — `.agent-work/issue-103/crew-handoffs/g2-implement-result.md`, gitignored.

## Required Evidence
- `git check-ignore` exits for both committed files.
- `wc -w skills/docent/SKILL.md` before/after; `wc -w skills/docent/references/self-contained-html.md`.
- `grep -c "self-contained-html.md" skills/docent/SKILL.md` (expect ≥1 pointer).
- `ls skills/docent/references/self-contained-html.md` and confirm it does not match `global-*.md`.
- Suite tail: `py -m pytest tests/test_install_constellation.py tests/test_docent_freshness.py -q`.

## Verification Commands
```bash
cd /c/Programs/constellation-wt-103
git check-ignore skills/docent/references/self-contained-html.md; echo "exit:$?"
wc -w skills/docent/SKILL.md skills/docent/references/self-contained-html.md
grep -c "self-contained-html.md" skills/docent/SKILL.md
py -m pytest tests/test_install_constellation.py tests/test_docent_freshness.py -q
```

## Suggested Model Tier
`simple bounded — mechanical extraction with a pointer`

## Authority
Extraction shape decided above. Do not invent additional restructuring. If the SKILL.md section headings have drifted from the names above, adapt to the current text preserving the same extraction.

## Stop Conditions
Stop if: scope must be exceeded, the freshness method cannot stay in the body, or the suite reds for a reason outside this edit.

## Return Format
Return IMPLEMENTER_RESULT (write to `.agent-work/issue-103/crew-handoffs/g2-implement-result.md` AND make it your final message before idling): edits done, files changed, word counts, grep/ls evidence, suite tail, assumptions, stop conditions, out-of-scope observations, workflow feedback.
