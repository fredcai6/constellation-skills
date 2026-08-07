# X5 Design B — Map-native overlay: the ledger as a familiarity layer on the Cartographer map

**Constraint (mine, exactly one): B · map-native overlay.** The shared concept ledger is an **overlay on the Cartographer architecture map**. Familiarity annotates map nodes (`struct:`/`capability:`/`constraint:`/`decision:`/`claim:`/`event:`). The **teach** and **neuter** policies are driven by **map traversal** over the map's existing edges. Optimize for **locality to existing map truth** — reuse the overlays/relationships graph rather than inventing a parallel store.

**Held FIXED (not redesigned here):** two opposite policies over ONE per-concept ledger; each entry carries a real-world-vs-internal tag + a familiarity level; register rule (expertise-reversal — peer/minimal default, depth on a detected miss, always surface the genuinely-new delta, expertise is concept-local); familiarity is OBSERVED off the human's own writing, never quizzed; per-project not cross-project; tutor summoned on a miss/pushback; anti-goals (no heavy machinery, no banning precise jargon, no condescension); prior art (Pocock learning-records-as-ADRs, ITS student-model-as-overlay, two-tier short-then-deep, docent freshness stamp, Diátaxis explanation shape).

**One-line thesis.** The ITS student-model-as-overlay-on-the-domain-model (X3 §1) is not a metaphor here — the **Cartographer map *is* the domain model**, so the familiarity ledger becomes a literal thin annotation layer keyed to real map node ids, and the concept-dependency graph the teach policy needs (X3 §5) already exists as the map's `depends-on`/`supports`/`constrained-by` edges. Where the map is rich this is the tightest, most local realization of the fixed spine. Where the map is thin or absent it degrades — honestly, and by design — toward the flat-ledger of candidate A.

---

## 1. The ledger entry shape + where it attaches

### 1.1 Home: a sibling reader-layer, same id namespace, NOT inside Cartographer's `overlays/`

The familiarity layer lives at:

```
docs/architecture/reader/familiarity.yml
```

**Why beside, not inside `overlays/`.** Cartographer *owns* `docs/architecture/overlays/*.yml` and admits a node/edge only under its **Inclusion Rule** (helps planning, boundary correctness, rule preservation, or trust). "How well does Fred know this node" serves *none* of those — it is reader-state, not structural truth. Putting it in `overlays/` would violate both Cartographer's ownership and its sparseness doctrine. So the reader layer is a **separate file in the same id namespace**: it *references* map node ids but is owned by the shared-understanding mechanism (the tutor skill), never by Cartographer. This is exactly the ITS split — **domain model (map) and student model (reader layer) annotate the same nodes but are different layers** — realized as two directories under one `docs/architecture/` root, one id space.

Per-project (fixed): one `reader/familiarity.yml` per repo; no cross-project store.

### 1.2 Entry shape

Every entry keys by a **map node id** (the anchor) and carries the two fixed fields (tag + level) plus a Pocock-style append-only observation log:

```yaml
familiarity:
  - anchor: capability:matern-covariance     # a real map node id — the domain-model anchor
    tag: real-world                           # FIXED field: real-world | internal
    level: new                                # FIXED field: new | shaky | fluent  (🔴/🟡/🟢)
    coined-term: "Matérn process"             # surface term the neuter gate matches on (optional)
    debt: true                                # 🔴 "I believe you for now, revisit later" (K5)
    last-observed: 2026-07-15                 # for time-decay
    anchor-status-seen: current               # the anchor's map status when last observed (for reconcile-decay)
    evidence:                                 # APPEND-ONLY log (learning-records-as-ADRs, X2)
      - {date: 2026-07-15, signal: ask,       source: "\"what's a Matérn process?\""}
      - {date: 2026-07-16, signal: taught,    source: "tutor session on capability:matern-covariance"}
```

- **`level` is a derived head, not authored.** It is a pure function of `evidence` + decay (replay the log → deterministic level). Humans and agents read `level`; only the observation step appends to `evidence`. This gives the co-authored, human-legible, ADR-immutable property the fixed design wants, and makes every pathway a testable pure function (§6).
- **Provenance is free.** The fixed schema wanted a `provenance` field; here it is *the anchor itself* — `capability:matern-covariance` resolves to its owning packet, whose prose is the provenance. No separate column.
- **`coined-term`** is the surface string the neuter write-guard scans for (§4). For a real-world entry it is the teachable name; for an internal entry it is the dialect token to hold down.

### 1.3 The unanchored residue (the honest fallback)

Not every concept is a map node (see §7 — this is B's core wound). Two residue classes get `anchor: null` in a second section:

```yaml
unanchored:
  - anchor: null
    coined-term: "fold-back loop"             # internal workflow dialect — no struct to hang on
    tag: internal
    level: new
    evidence: [...]
```

This section is, deliberately, **just candidate A's flat plain-text ledger**. B is therefore honestly stateable as: *"design A's flat ledger, with a map-native fast path for every concept that is a map node."* Anchored entries get all the locality/traversal wins below; unanchored ones get none and are managed flatly.

---

## 2. How familiarity updates from the human's writing

Passive observation via the **contingency/fading rule** (X3 §2), run off the human's own prose — never a quiz.

**The observation step** (a thin post-turn side effect of the interleaving discipline, §5 — not a standalone agent, to avoid T-A2 context bloat):

1. When the human's message is parsed, resolve which surface terms correspond to which **map node ids** (the term→node resolver — a fuzzy match against node labels / `coined-term` values / packet symbols; **scoped null §8.1**).
2. For each resolved node N, apply the contingency rule and **append** one evidence record (never rewrite):
   - Human uses the concept fluently/correctly in their own writing → `signal: fluent-use` → derived `level` steps *down* (new→shaky→fluent), `last-observed` refreshed.
   - Human stumbles, misuses, asks ("what is X?"), or pushes back → `signal: ask` / `stumble` → `level` steps *up*, and the teach policy is armed for N.
   - Tutor/agent introduced it → `signal: taught`; human deferred a check-in → `signal: deferred` + `debt: true`.

**Two decay drivers** collapse the derived `level`:

- **Time decay** (X1 transferable core): a `fluent` node untouched past a window softens to `shaky`.
- **Reconcile decay — the genuinely map-native mechanism.** When Cartographer reconciles the anchor node and its `status` moves to `stale`/`disputed`/`partial`, or its `explained-by` decision is superseded, the reader layer compares the node's current status against `anchor-status-seen`; a mismatch **softens familiarity** (fluent→shaky). Rationale: if the *code moved*, the human's prior understanding may now be out of date — so knowledge of a node decays **when the node itself changes**, not only with time. A flat ledger (A) cannot express this; it has no notion that the underlying truth shifted. This is B's signature capability.

---

## 3. The TEACH policy reads the overlay (Half A — real-world, teach *up*)

Teach is a **map traversal**. When an agent is about to write about a load-bearing node N that just became relevant in the current work:

1. **Read** `familiarity[N]`. Teach fires only if `tag: real-world` and (`level: new`, or `level: shaky` on a recurrence).
2. **Depth-gate by prerequisite traversal (X3 §5, realized on real edges).** Walk N's `depends-on`/`supports`/`constrained-by` edges to its prerequisites and read *their* familiarity:
   - All prerequisites `fluent` → the human owns the ground → a **peer-register pointer** suffices (expertise-reversal default: name the concept + the delta + the load-bearing consequence, then stop).
   - A prerequisite is `new` → **teach the missing prerequisite, not N** — the smallest contingent help (scaffolding). The map's edges *are* the prerequisite graph; nothing is invented.
3. **The genuinely-new delta = unheld sub-structure (expert-blind-spot guard).** Compute the delta as the child nodes / incident edges of N the human has *not* marked `fluent`. That set is exactly "what's actually new to this reader," so the agent surfaces it and skips what the human owns — no condescension, no glossing-over the one non-obvious step.
4. **Ordering.** When several new nodes land together, teach them in the map's `depends-on` topological order so each rests on established ground (free from the graph).

Teach is thus "traverse from N through held/unheld nodes and emit the shallowest unheld bridge." No scoring engine — just graph reads against a three-valued level.

---

## 4. The NEUTER policy reads the overlay (Half B — internal, hold *down*): "no coined term until unlocked"

Neuter is the **same gate, read in the opposite direction**. This is the spine's "K2 is literally the same familiarity gate applied to internal terms," made mechanical.

A **write-guard lint** over the drafted human-facing message (a pure pass at send-time):

1. Scan outgoing text for any `coined-term` whose entry has `tag: internal`.
2. Read that entry's `level`:
   - `new` → **LOCKED**. The term may not appear bare. The agent either (a) substitutes plain language, or (b) if it must introduce the term, emits a **one-line gloss** *and* appends a `taught`/introduce signal — which moves the entry toward `shaky`, i.e. **unlocks** it. "Unlocked" ≡ `level >= shaky` for an internal entry; unlock is not a separate flag, it is the same level crossing a threshold.
   - `shaky`/`fluent` → **UNLOCKED**. Use it bare; do **not** re-gloss (re-glossing an owned term is the condescension anti-goal). `fluent` means the human owns it — spend the coinage.
3. **The gloss, when required, is pulled from the map, not invented** — an internal term anchored to a `capability:`/`struct:` inherits its one-liner from the anchor's `summary`/packet `Purpose`. Locality win: the neuter policy re-uses map prose as the gloss source.

So one three-valued `level` drives both halves: teach reads "is real-world ∧ below-fluent → bridge up"; neuter reads "is internal ∧ below-shaky → hold down." One ledger, two opposite reads — the fixed spine, mechanized.

---

## 5. Calibration + interleaving inside a real message (the genuinely-novel core)

The novel problem (X2·X3·X4 verdict): hold a **standing per-reader model** *and* blend **one paragraph of explanation into a working stream** without condescending or cluttering. B supplies the substrate; the discipline is a cross-cutting rule every agent applies (it does not need a central owner — that's candidate C's job).

Composing a human-facing message that touches map nodes {N₁…N_k}:

1. **Calibrate (read the standing model).** For each Nᵢ fetch `(level, tag)` from `reader/familiarity.yml`. This is the persistent model X4 §4 found missing in IDE tools — it is *not* re-declared per message; it lives on the map and is corrected by observation.
2. **Set the interleave budget.** Default **terse/pointer** (expertise-reversal). At most **one** teach-delta paragraph per message. Select the single highest-value node: `real-world ∧ (new|recurring-shaky) ∧ load-bearing-in-this-change`, breaking ties toward the **shallowest missing prerequisite** (cheapest genuine bridge). The register dial (K4) is a coarse global multiplier on this budget: "teach-me" raises it; "peer" drives it to ~0.
3. **Interleave, don't append.** Weave the teach unit at the point the concept becomes load-bearing *in the message* (just-in-time, X3 §4) — not a bolted-on "concepts" footer. Shape it as a bounded Diátaxis explanation unit: *what it is / the delta from what you hold / the consequence that rides on it* (target grade B→C), then return to the working stream.
4. **Neuter write-guard pass (§4).** Lint the drafted message: locked internal terms → substitute or gloss-and-unlock.
5. **Observe the reply (§2).** Append familiarity deltas from the human's response, closing the contingency loop.

Everything the calibration reads and the observation writes is keyed to map node ids — the "standing model" is *physically the map plus one sibling file*, which is what makes it cheap to hold and legible to correct.

---

## 6. The tutor's trigger + seam

**Trigger (fixed):** summoned on a **miss / pushback** — "no, that doesn't make sense," "let's go back," "unpack that," or an agent detecting its own interleaved delta failed (the human re-asks). This is the same `signal: ask/stumble` the observation step already emits; the tutor is the **escalation** when one interleaved paragraph was insufficient.

**Seam — a single map node id (deep-module boundary).** The caller hands the tutor exactly one thing: the node id N that triggered the miss. From that id the tutor reaches *everything it needs* through existing map structure:

- N's **packet** (the dense agent page: Responsibility, Key Modules, Data Flow, Known Limits) — the domain content.
- N's **overlay edges** — prerequisites (`depends-on`/`supports`), governing `constraint:`s, `explained-by` `decision:` anchors (the *why* and the road-not-taken, X4 §3).
- N's **familiarity `evidence` log** — what the human has and hasn't held, and prior teach attempts.

The tutor teaches around N at ZPD depth (walk down to the shallowest unheld prerequisite, §3), then **appends `taught` signals** to the log for every node it covered. Its **input contract = one node id; its output = append-only familiarity deltas.** Pedagogy is fully hidden behind the seam; callers never see level math or log replay.

**Milestone explainer (K9) rides the same rails.** At a build milestone the tutor generates a durable explainer for the changed node set, keyed to map node ids — so **`constellation-docent`'s existing `docent_freshness.py` stamp works unchanged**: the explainer is stamped against the same map source it explains, and self-flags STALE when the map moves. Map-native locality hands us freshness/provenance for free (the fixed prior-art requirement).

---

## 7. Deep-module framing

- **Narrow interface, deep body.** Callers ask only: `familiarity(node_id) -> (level, tag)`, `neuter(draft) -> guarded_draft + unlock_deltas`, `teach_target(node_id) -> bridge_node + depth`. Behind that: contingency updates, time-decay, reconcile-decay, prerequisite traversal, topological ordering, ADR-log replay. None of it leaks to callers.
- **The seam is the map node id** — the same boundary the map already uses to hang every `capability:`/`constraint:`/`decision:` overlay off a `struct:`. B adds one more overlay layer at the boundary the architecture already established, rather than inventing a new one.

---

## 8. Honest self-assessment on the five axes (including where B HURTS)

**Depth — Strong, with one leak.** Real complexity (decay, traversal, log replay) hides behind "node id → (level, tag)." **Leak:** the **term→node resolver** (mapping "the covariance thing" in the human's prose to `capability:matern-covariance`) sits *before* the seam, is fuzzy, and is a per-agent burden the map does *not* hide (shared with candidate D). Partial leak into every observing agent.

**Locality — B's headline strength *and* headline weakness.**
- *Win:* for any concept that is a map node, familiarity annotates the single source of truth, stays in sync via Cartographer reconcile, decays when the node changes, and re-uses the existing edge graph as the prerequisite/ordering graph. Zero parallel store; the change is contained to one sibling file + a shared read/write helper. This is the most local realization of the spine of the four constraints.
- *HURT — coverage-bound:* locality is only as good as map coverage.
  - **Real-world concepts that aren't architecture** (a statistical process the code merely *assumes*, e.g. a Matérn kernel that isn't itself a struct) may have no node to anchor to — attach to the nearest node or fall into the unanchored list (degrading to A).
  - **Internal workflow dialect** — process names, agent-to-agent coinage ("fold-back loop," "neuter") — is the *bulk* of Half B's targets and mostly has **no map anchor at all**. So the neuter policy's most important inputs live *outside* the map. **The half the human cares about MORE (low tolerance for internal jargon, worse across many concurrent projects) is the half the map serves WORST.**
  - **Projects without a map** — f1brainz and most projects have no `docs/architecture/`. The overlay has no substrate; the mechanism is inert. **B is parasitic on a map many projects never build** — the single biggest cost.

**Seam placement — Good, with a fuzzy pre-stage.** The seam is the map node id, exactly where the map already draws overlay boundaries and where tests want to inject ("given this node, what is the reader state"). The neuter write-guard as a send-time draft lint is also well-placed. Weak spot: the term→node resolver upstream of the seam is fuzzy and un-clean.

**Testability — Strong (best axis for B).** Every pathway is an isolatable pure function over (overlay, input) because everything keys to node ids:
- *Familiarity update:* synthetic message + node set → assert appended signal + derived level (log replay is deterministic).
- *Reconcile-decay:* flip a node's `status` → assert its familiarity softens.
- *Teach trigger/depth:* overlay + target node → assert the chosen bridge node and depth.
- *Neuter gate:* draft + overlay → assert locked terms substituted/glossed (pure function).
- *Interleaving budget:* k nodes → assert ≤1 teach delta + the selection.

**Fit to the fixed anti-goals.**
- *Heavy-machinery risk — MODERATE.* The overlay itself is light (a YAML sibling + ADR log). But leaning on the map imports the map's ceremony, and for map-less projects there is a temptation to **build a map just to host familiarity** — heavy machinery for its own sake, the exact anti-goal. **Guard: never require a map; degrade to the flat unanchored list.** Hold that guard and risk stays moderate.
- *Condescension risk — LOW / well-served.* Expertise-reversal default (peer/pointer); unlock→fluent means owned terms are used bare and never re-glossed; teach surfaces only unheld sub-structure. Good.
- *Serves BOTH halves equally? **NO — B's honest structural failure.*** The map serves Half A (teach real-world concepts that *are* capabilities/decisions/constraints) markedly better than Half B (neuter internal dialect that mostly isn't on the map). The fixed spine insists both halves are first-class; **B structurally privileges the teachable-architecture half**, which is the deepest tension between this constraint and the confirmed design.

**Net.** B is the *right* design precisely when the concepts to teach are load-bearing architecture in a well-mapped project — then it is the most local, most testable, freshness-for-free realization of the spine. It is the *wrong* design for map-less projects and for suppressing non-architecture workflow dialect, which is a large and human-prioritized slice.

---

## 9. What I did NOT resolve (scoped nulls)

1. **Term→node resolution.** How an agent maps a surface term in the human's prose ("the Matérn thing," "that kernel") to the correct map node id — the fuzzy match gating *both* update and neuter — is unspecified (shared with candidate D). The single most load-bearing unresolved piece.
2. **The unanchored residue.** Concepts with no map node fall to a flat `unanchored` list — essentially candidate A bolted on. I did not design that list's dedup, ordering, or how the neuter gate reads it efficiently, nor reconcile the two-store UX.
3. **Map-less projects.** I assert "degrade to a flat list" but did not design the graceful-degradation path, nor when/whether a project *earns* the map-native upgrade.
4. **Cartographer ownership / dangling-anchor GC.** I placed familiarity in a sibling `reader/` layer to respect Cartographer's Inclusion Rule and `overlays/` ownership, but did not fully specify what happens when Cartographer **retires or renames** an anchored node id. The reconcile-decay hook (§2) needs Cartographer to surface node-change/rename events the reader layer subscribes to — that cross-skill contract is sketched, not specified.
5. **Register dial (K4) persistence.** Treated as a global budget multiplier; per-session vs persistent-default storage left open (shared open thread T-D).
6. **Unlock threshold semantics.** I set unlock ≡ `level >= shaky` and let a single introduce-event move new→shaky; I did not validate whether unlock should instead require an explicit human acknowledgment (open thread T-C).
7. **Reconcile-decay calibration.** *Which* map status changes should soften familiarity, and by how much (a `partial` re-scope vs a full `disputed`), is asserted qualitatively, not tuned.
