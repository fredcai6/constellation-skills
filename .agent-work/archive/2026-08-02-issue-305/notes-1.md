# commander-305e — working notes 1: independent verification of the g3 rework

Continuation of commander-305d (confirmed dead). Artifacts were complete at `9644fb3`;
the gate was uningested. This file records what I **reproduced myself** rather than
inherited, per the epic's standing standard.

## Method note that changed my own results (#319, three times)

The worktree file is **CRLF on all 1119 lines**. Every text pattern I wrote with `\n`
silently matched **zero** sites and would have read as "mutation applied, still green" —
a false negative-control result produced by the tooling rather than the code. Two further
variants of the same trap bit me:

* `git show HEAD:<path>` returns **LF**, the worktree is **CRLF**, so a line-ending
  computed from one base does not apply to the other. EOL must be derived per base.
* `git hash-object` compares true across the CRLF/LF boundary because its clean filter
  normalises. That is exactly why blob OID is the right instrument and raw bytes are not.

Two of my mutation scripts also died *before* their restore step — once on a cp1252
`UnicodeEncodeError` while printing pytest output, once on a broken pipe from `| head`.
Both left the tree mutated. **Restore belongs in a `finally:`, and the tree must be
OID-checked after every battery, not after the last one.**

## What I verified

| claim | how | result |
|---|---|---|
| suite numbers | `python -m pytest -q`, run by me | `1487 passed, 2 skipped, 472 subtests` — matches |
| control file count | counted test defs | 13 -> 15, the +2 are FIX 3's two tests |
| restoration | blob OID vs HEAD, six files | all MATCH |
| red-proofs | re-run against the **shipped** file | see below |

**A gap in the inherited evidence:** the crew's red-proofs ran against intermediate
revisions `49059be` and `fb9dfc2`. Neither is the shipped file (`667b5e4`). The shipped
artifact had never itself been red-proofed. Re-running was not ceremony.

### My attacks — each asserted on its SPECIFIC assertion text, never a non-zero exit

* **V1** (their M1 shape, vs the shipped file): every `advance --mechanical` -> `--why <prose>`,
  every `attest` given `--note <prose>`. **RED**, `assert violations == []`, 44 violations.
* **V2 — novel.** `attest --evidence "ev-control-1"`. A real engine flag carrying an
  agent-supplied string that is **absent from `AGENT_TEXT_FLAGS`**, so a blacklist census
  misses it entirely. **RED**, 8 violations, caught by the closed-world arm alone. This is
  the first direct attack on the closed-world property; the rework asserted it but never
  tested it.
* **V3** oracle self-comparison with every `source` description untouched. **RED**,
  naming `the oracle called episode_capture.reopen_total`.

## What I found that the rework's sweep missed

The rework reports "**no third vacuous guard found**". Mine found one more thing — not a
vacuous guard, but the same family in a different costume.

`test_control_records_nothing_agent_authored` docstring claimed: *the only agent-authored
text in the entire control is ONE fixed constant, `reopen --reason "control"`, and it
feeds no mechanical field.* **False in both halves.**

`claim --claimed-by "commander"` is a second agent-supplied string, and
`episode_capture._lease_role` (`scripts/episode_capture.py:233`) reads `session["claimed_by"]`
**straight into the `role` mechanical field**. The oracle says so itself — `role`'s declared
source is *"the --claimed-by string this harness passed to `claim`"*. The census could not
see it: `--claimed-by` is sanctioned in `ALLOWED_FLAGS["claim"]` and was absent from
`AGENT_TEXT_FLAGS`, so it never entered `text_bearing`.

**V4, measured not reasoned:** I replaced the role constant with the sentence
*"a role string I typed by hand as narrative prose"*. Result **`15 passed`, exit 0** — a
hand-authored sentence lands in a mechanical field while the guard named "records nothing
agent authored" stays fully green.

This is the Admiral's ruling-1 corollary in its purest form: **a docstring claiming more
than the code checks.** It is *not* a tenth vacuous guard — the guard fires hard on
V1/V2/V3.

## The fix I landed

1. `--claimed-by` added to `AGENT_TEXT_FLAGS`, so the census counts it.
2. `PARENT_ROLE` promoted to a module constant — the assertion names that value, so it is
   declared where the claim about it is.
3. The census asserts **exactly two** declared constants.
4. The docstring corrected to the true claim.

Deliberately **not** done: a guard that fires when the role string "looks like prose".
`role` must be *some* supplied string, so that would be unfalsifiable theatre. The honest
property is "exactly two, both declared"; V1/V2 prove a third is caught.

### V5 — before/after, because a fix whose before/after is not measured is a claim

Same mutation both ways: the harness **composes** the `--claimed-by` value at issue time.

| base | census result |
|---|---|
| **HEAD** (pre-fix) | **`1 passed`, exit 0** — blind |
| **my worktree** (post-fix) | **`1 failed`** — `Extra items in the left set: ('claim', '--claimed-by', 'commander composed at issue time')` |

V1/V2/V3 all re-confirmed **still RED** against the fixed file, so falsifiability did not
regress.

## Corrected wording for the PR body

Replacing the ratified sentence, which does not survive verification:

> The control hands the engine exactly **two** agent-supplied strings, both fixed
> constants: `claim --claimed-by <role>`, which **is** the `role` mechanical field by
> definition since `role` is the lease-holder's declared identity, and
> `reopen --reason "control"`, which writes to `why_trail` and feeds no mechanical field.
