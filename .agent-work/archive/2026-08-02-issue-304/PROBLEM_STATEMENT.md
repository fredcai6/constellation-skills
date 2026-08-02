# Problem statement — issue #304, Commander map-input contract

Framing is **pre-empted and ratified** by LAUNCH_ORDER-304 ("Problem framing — the primacy-not-path
framing above is ratified; do not re-derive it"). This restates it for the plan to build against; it
does not re-derive it.

## Protected intent

**The deficiency is primacy and contract, not path.**

A canonical entrypoint at an exact path, in the always-loaded bootstrap, already exists in f1Brainz
(`CLAUDE.md`, verbatim again at `AGENTS.md:27` and `README.md:203`, at commit `3541d292`). It is
measured NOT to produce map-first orientation: in all five #299 baseline runs the agent read source
before the map, then used the map to confirm a hypothesis it had already formed from code.

Tommy's bar: *"there is a gulf between saying 'there is a map' and 'use the map first to orient
yourself'."* Build the second thing.

A deliverable that resolves an entrypoint and stops has shipped a capability f1Brainz already had, and
is a **failure of this issue** regardless of how well it works.

## What must be true of the contract

1. **Primacy** — it establishes that map orientation happens *before* source exploration and *informs*
   it. Ordering is the property under test, not availability.
2. **One concern-owned contract** — a single canonical statement projected into Commander context and
   plan, not scattered prose. Wired at **context** and **plan**, not reconcile
   (`decision:contract-at-context-and-plan`).
3. **Reported degraded mode** — when the entrypoint cannot be resolved, the contract REPORTS it. Never
   a silent fallback to code crawling. Silent fallback *is* the measured failure mode.
4. **Degraded mode is the common case** — not an edge case, and gets at least equal design attention
   (`decision:degraded-mode-is-the-common-case`). Confirmed live: this repo has no `docs/architecture/`.
5. **The check must be able to fail** — proven by mutation, per the #300 finding.

## The join being made

- Corpus side: **pathless but primary** — `COMMANDER_SPINE.template.json:22` (context) "Read the current
  map (packets, overlays, decision anchors)" and `:48` (plan) "Map-first: BEFORE authoring execute.json,
  produce a mission frame from the current map". Both say *the current map*; neither says where it is.
- Target-repo side: **pathed but secondary** — f1Brainz's `CLAUDE.md` names an exact path, but as one of
  four "Also read" supplementary entries, a peer of a test-commands doc.

The contract is the join: pathed **and** primary.

## Folded in: #317

`decision:317-folds-in`. Corpus-wide-or-nothing. Scope corrected against the code (see notes-304.md):
the bare `config_ref` line is in **11 of 11** shipped templates; the wrong do-not-create prose is in
**2** (~112 words), both Commander-owned. And Charter ships a task that **writes** the very file
Commander says must not be created — a live contradiction, not just staleness.

## Out of scope

- Re-running the #299 baseline arm (captured, merged, pasted).
- Any `gh` write against `fredcai6/f1Brainz`; any push/PR/issue there. f1Brainz is read-only.
- Treating any #299 seam number as a target (declared power is ~1 partially-discriminating task at n=1;
  direction-of-travel only).

## Honest-null condition

If the deletion-plus-run pathway shows the superseded prose was doing nothing and the contract adds
nothing measurable, that is a complete successful deliverable and gets reported as such. A negative is
scoped to this contract shape — never to "map-first cannot be mechanized."
