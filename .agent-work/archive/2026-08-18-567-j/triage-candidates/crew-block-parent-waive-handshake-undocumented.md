# Triage candidate: crew-blocks/parent-waives handshake has no documented protocol

**Found at:** 567-j `plan` gate, `c6` (mission-frame map-verification).

**What happened:** `plan.c6` (map_orient.py `verify-frame`) genuinely refuses in this
repo — no architecture map exists at all (`map/ids.jsonl` is 0 bytes), so every
citation in an otherwise-complete mission frame reads as unresolvable. The
declared escape is a recorded waiver. But `spine_evidence action=waive` on my
own bound spine is refused unconditionally by the door: "a crew must not waive
its own bound spine check -- always ask up." The two paths the refusal's own
recovery text names for the parent to act on the child's spine are both filed
defects: passing the child's session id (`#632`, impersonation — the exact
mechanism a rogue subagent used against lane H) and `claim --force` (`#369`,
erases actor attribution).

**What actually worked**, executed by hand between this lane and the Admiral
over SendMessage:

1. Child (`567-j`) calls `spine_lease action=release` and does nothing else.
2. Child tells the parent it released.
3. Parent claims the child's spine as `admiral` (its own real identity, no
   impersonation, no force), waives the check with the full reason, releases.
4. Parent tells the child it's clear.
5. Child re-claims as `commander`, calls `spine_halt action=resume`, carries on.

This is not written down anywhere. The engine's own refusal message assumes
the parent can act on the child's spine and offers only the two bad routes;
neither route it names is actually usable, and the real fix (a full
release-reclaim round trip) has to be independently derived and coordinated
live over a side channel every time this happens.

**Why it matters:** every `settled/doctrine`-graded self-waive refusal on a
spine a Commander is actively driving hits this exact wall. Without a
documented protocol, the next pair either reinvents this exchange from
scratch, or — worse — someone reaches for one of the two named-defect routes
because it's the only thing the refusal message itself suggests trying next.

**Recommendation (not mine to decide or file):** document the
release → parent-claims → parent-waives → parent-releases → child-reclaims
sequence as the sanctioned recovery for "crew blocks a self-waive-refused
check," either in the door's own refusal text (name the five steps, not just
the two dead ends) or in `references/global-everyone.md`'s reach-up section
beside the existing `refresh-request` primitive it already documents for the
sibling case (trip-forced idle). Possibly also worth asking whether the door
should offer a real third route instead (e.g. a `waive-by-parent` verb that
checks `SPINE_PARENT` linkage without requiring a lease handoff at all) —
that's an engine-owned scope call, lane K's fence, not mine.

**Disposition:** staged only, per `decision:no-issue-filing-mid-run`. Filed
nowhere; the human or Admiral routes this from here.
