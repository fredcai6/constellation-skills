# IMPLEMENTER_RESULT — g2 Docent extraction

## Gate
`g2` — Docent self-contained-HTML constraint block → one-hop reference.

## Edits done
1. **Created** `skills/docent/references/self-contained-html.md` (new dir `references/` created).
   - Holds the extracted "## Self-contained HTML — hard constraints" three bullets verbatim (no external resource loads; restrained/readable/dark-light-aware; shared inline CSS block).
   - Also holds the relocated self-containment verification recipe (the "confirm no external resource loads, e.g. grep the site for `http(s)://` … `XMLHttpRequest` — there must be none" sentence), moved out of SKILL.md Freshness step 4.
   - One-line header explains it holds Docent's self-containment hard constraints + their verification. No TOC (file is 22 lines).
2. **Edited** `skills/docent/SKILL.md`:
   - Replaced the "## Self-contained HTML — hard constraints" section body with a "## Self-contained HTML" summary (1 short paragraph) + one-hop pointer to `references/self-contained-html.md`.
   - In "Freshness stamp + STALE banner" step 4: KEPT the `docent_freshness.py check <site> --map-root` exit-0 verification; replaced the inline grep enumeration with "then confirm no external resource loads per `references/self-contained-html.md`."
   - Everything else (Inputs, Page structure, Freshness stamp mechanics incl. `stamp`/`check` commands and STALE banner doctrine, Output location, Guardrails, protected-intent "stale is worse than none" preamble) unchanged.

## Files changed
- `skills/docent/SKILL.md` (modified)
- `skills/docent/references/self-contained-html.md` (new)

## Word counts (wc -w)
- `skills/docent/SKILL.md`: **before 1110 → after 1005** (−105).
- `skills/docent/references/self-contained-html.md`: **214**.
- Net corpus +109 words is the reference's intro/header framing; all original constraint text is preserved (relocated, not lost).

## grep / ls evidence
- `grep -c "self-contained-html.md" skills/docent/SKILL.md` → **2** (body summary pointer + freshness step-4 pointer; ≥1 required).
- `ls skills/docent/references/self-contained-html.md` → present.
- Basename `self-contained-html.md` does NOT match `global-*.md` (glob case-check: no match).

## Deliverable path check
- `git check-ignore skills/docent/references/self-contained-html.md` → exit **1** (not ignored, committable). ✓
- `git check-ignore skills/docent/SKILL.md` → exit **1** (not ignored, committable). ✓

## Suite tail
```
py -m pytest tests/test_install_constellation.py tests/test_docent_freshness.py -q
.......................... [ 55%]
.....................                                                    [100%]
47 passed, 118 subtests passed in 4.02s
```
Green.

## Assumptions
- Section headings had not drifted; adapted to the exact current text. Used the handoff's suggested summary wording nearly verbatim.
- Gave the reference a descriptive H1 header + intro line (as instructed) rather than copying the old SKILL.md heading, since it is now standalone.

## Stop conditions
None triggered. Scope stayed within the two allowed files; freshness method + stamp/check commands remain in the SKILL.md body; suite green.

## Out-of-scope observations
None. Did not touch `skills/commander/**`, `_shared/**`, `tests/**`, or `scripts/docent_freshness.py`.

## Workflow feedback
Handoff was fully self-sufficient: exact extraction shape, suggested wording, evidence list, and verification block all matched reality with no drift. `wc -w` net-increase is expected for extraction-with-framing and is worth pre-noting in future handoffs so a reviewer doesn't read the +109 as scope creep.
