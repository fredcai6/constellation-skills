# Trend snapshot — corpus size and per-role surface

**Taken at:** `fc1685a`, 2026-08-01 (issue #304 gate g3, worktree `e298-304`).
**Status:** the standing aggregate baseline. Every figure below is **derived from a git command**, and
the command is printed next to its output so the successor can re-derive rather than re-invent.

---

## 0. Who this is for — read this first

A baseline with no declared successor is a number nobody ever compares against, so this section is not
preamble, it is the point of the file.

- **Consumer: the NEXT trend snapshot.** Not a human reading it once, not this issue's review. Its job is
  to run the *same commands* against a later commit and subtract. Nothing else consumes this file, and
  it should be deleted rather than maintained if that successor is never taken.
- **When the successor is expected: at EPIC-298 CLOSE.** That is the binding date, and #304 sits *inside*
  epic #298, so it is genuinely close — the first successor is owed at the close of the epic this
  snapshot was taken during, not the one after it.

  **After that, the standing rule: each subsequent epic that changes `skills/`.**

  Both clauses schedule a successor, which is the point; they differ only in how soon the first one
  falls due. Which is binding, and why, stated so a successor understands the rule rather than merely
  obeying a date:

  - **`epic-298 close` binds because it is what was ratified.** It comes from the Admiral amendment that
    put this successor clause into the gate plan in the first place. This file originally shipped only
    the looser rule below, because the amendment's *substance* (name the consumer, name the successor,
    state the retire-if-unread rule) reached the g3 handoff while its *named date* did not. A ratified
    date outranks a derived one; the near date wins.
  - **The standing rule is the general case, and it is epoch-bound on purpose.** The corpus only moves
    when an epic moves it, so a calendar cadence would produce identical numbers on a quiet month and
    read as false stability. Once the epic-298 successor is taken, that is the rule that carries the
    series forward.
- **What the successor must do to be a successor at all:** re-run §1–§3 verbatim against its own HEAD,
  paste both numbers, and state the delta. A successor that reports only its own figures is a second
  baseline, not a trend.
- **Deliberately not claimed:** this snapshot says nothing about whether the corpus is the *right* size.
  It is a measuring stick, not a verdict, and "words went down" is not by itself an improvement.

---

## 1. Corpus size

```
$ git ls-files 'skills/**' | wc -l
100

$ git ls-files 'skills/**' -z | xargs -0 cat | wc -w
63681
```

**100 tracked files, 63,681 words** across the whole skills corpus.

The always-loaded subset — the surface an agent pays for on *every* dispatch, before any reference or
template is opened:

```
$ git ls-files 'skills/*/SKILL.md' | wc -l
19

$ git ls-files 'skills/*/SKILL.md' -z | xargs -0 cat | wc -w
15831
```

**19 `SKILL.md` files, 15,831 words** — 24.9% of the corpus. This split is the one worth trending: total
corpus growth is cheap (references are loaded on demand), always-loaded growth is not.

## 2. Per-role surface

```
$ for d in $(git ls-files 'skills/*' | cut -d/ -f2 | sort -u); do
    printf "%-28s %4s files %8s words\n" "$d" \
      "$(git ls-files "skills/$d" | wc -l)" \
      "$(git ls-files "skills/$d" -z | xargs -0 cat | wc -w)"
  done
```

```
_shared                         6 files     6729 words
admiral                         6 files     7733 words
cartographer                    7 files     3786 words
charter                        15 files     6293 words
commander                       9 files    10603 words
commander-delegated             1 files     1036 words
curator                         1 files      617 words
diagnose                        3 files     1011 words
docent                          2 files     1219 words
explorer                        8 files     5778 words
implementer                     3 files     1626 words
interrogator                    3 files     1512 words
lessons-auditor                 4 files     2188 words
prototyper                      6 files     2537 words
reviewer                        4 files     2253 words
scout                           4 files     1382 words
to-issues                       3 files      955 words
triage                          2 files      771 words
workbench                       9 files     4663 words
write-a-skill                   4 files      989 words
```

The row above is what the command printed — kept verbatim so a successor who re-runs it gets a
matching block, per this file's own §0 reproducibility contract. **But `_shared` is not a role,
and the table above is 19 roles, not 20** (#411): `install_constellation.py` excludes any
`skills/` directory starting with `_` when enumerating skills (`_shared holds bundled refs, not
a skill`). `_shared` is **bundled shared surface** instead: 6 files / 6,729 words that
`install_constellation.py`'s `SKILL_REFERENCE_BUNDLES` copies into a majority of roles'
`references/` at install time, so those words already count toward the roles that bundle them,
not toward a 20th role's own surface. This snapshot does not attribute each role's bundled
`_shared` files individually — that recomputation is unresolved.

**Nothing here stops the mistake recurring** — this note only corrects THIS reading of THIS
block. The `for d in ...` command has no `_shared` exclusion of its own, so anyone re-running it
gets the same unlabeled 20-row output and must rediscover, from this note or from #411, that the
first row isn't a role. The propagation path #411 names is closed only if the command itself (or
its successor) excludes `_`-prefixed directories, or a later snapshot format labels the row
inline instead of relying on a reader finding this paragraph.

Two features a successor should watch rather than re-notice:

- **`commander` is the largest single role at 10,603 words** — 16.6% of the corpus in one role, and it is
  the role this epic keeps editing. If any role drifts, it will be this one.
- **`charter` carries the most files (15) with middling word count**, and `commander-delegated` and
  `curator` are single-file roles. File count and word count trend differently; report both.

Supporting surfaces, for context on what fraction of the repo the corpus actually is:

```
$ printf "tests/   %s files %s words\n" "$(git ls-files 'tests/*' | wc -l)" "$(git ls-files 'tests/*' -z | xargs -0 cat | wc -w)"
tests/   57 files 110307 words

$ printf "scripts/ %s files %s words\n" "$(git ls-files 'scripts/*' | wc -l)" "$(git ls-files 'scripts/*' -z | xargs -0 cat | wc -w)"
scripts/ 39 files 94939 words
```

## 3. What gate g3 itself moved

Recorded here because a baseline taken by the same run that changed the numbers must say so, or the
successor will attribute this delta to the wrong cause.

```
$ for f in skills/commander/templates/COMMANDER_SPINE.template.json \
           skills/commander/templates/EXECUTE_PLAN.template.json; do
    printf "%-46s before=%5s after=%5s\n" "$(basename $f)" \
      "$(git show a8d9467:$f | wc -w)" "$(git show HEAD:$f | wc -w)"
  done
```

```
COMMANDER_SPINE.template.json                  before= 3539 after= 3457
EXECUTE_PLAN.template.json                     before=  708 after=  622
```

```
$ git ls-tree -r a8d9467 --name-only -- skills | xargs -I{} git show a8d9467:{} | wc -w
63849
$ git ls-files 'skills/**' -z | xargs -0 cat | wc -w
63681
```

- **Spine: −82 words.** 86 deleted (the dead-path block) plus 4 added (T3's four-for-four retarget of
  `from the current map using` → `from the map input the context step resolved, using`).
- **Execute plan: −86 words.** The byte-parallel block, nothing added.
- **Corpus total: 63,849 → 63,681, −168 words.**

**A note the successor needs, because the arithmetic does not close on its own:** the deletion was
**172 words** (86 + 86, by `wc -w` over both captured blocks), and the corpus moved **168**. The
difference is the +4 retarget, not a miscount. `a8d9467` is g3's own starting commit, deliberately — not
the pre-registration `0119fa4`, because gate g2 landed several hundred words of `verify-frame` prose in
between, and measuring from `0119fa4` would report the spine as having *grown* and silently attribute g2's
addition to g3's deletion.

## 4. Episode store

```
$ ls episodes/active/*.md | wc -l
5
```

The store went from **0 to 5** at this gate (`issue-304-g3-001` … `-005`, one per tripwire). It was empty
before, so this is the store's first real content and the first number a successor can trend at all.

---

## 5. The comparison the successor should make

Ranked, so a successor short on time still measures the thing that matters most:

1. **Always-loaded surface** (§1, `SKILL.md` total) — the only figure with a direct per-dispatch cost.
2. **`commander`'s share** (§2) — the role under active edit; the likeliest place for unnoticed drift.
3. **Corpus total** (§1) — context, and the weakest signal of the three on its own.
4. **Episode count** (§4) — whether episode capture became routine or stopped dead at this one gate.
