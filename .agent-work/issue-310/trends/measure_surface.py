#!/usr/bin/env python
"""measure_surface.py — the B2 gate-(a) trend instrument for issue #310.

WHAT THIS MEASURES, AND WHOSE RULING THE BINS ARE
-------------------------------------------------
Three separately-labelled series over the `skills/` corpus. The instrument NEVER sums
NARROW and WIDE — they overlap by construction, and summing them is meaningless:

  NARROW-ALWAYS-LOADED  = `skills/<role>/SKILL.md` only.  This is issue #304's baseline
                          definition and the verdict's PRIMARY number: comparability with
                          the declared baseline is what makes this run a successor rather
                          than a second baseline.
  WIDE-ALWAYS-LOADED    = NARROW + every `references/<file>` token that a SKILL.md names,
                          resolved role-locally first, then through THAT COMMIT'S OWN
                          `SKILL_REFERENCE_BUNDLES` in `scripts/install_constellation.py`.
                          A SUPPLEMENT, never the primary.
  CONDITIONALLY-LOADED  = `templates/`, `scripts/`, and any `references/` (or `_shared/`)
                          file no SKILL.md names.

  *** The WIDE bin is a RECONSTRUCTION RULED BY THE ADMIRAL, not a contract discovered in
  the tree. Nothing in the tree declares one. *** It is recorded that way in the emitted
  manifest so a reader knows who to argue with.

RECOMBINATION ARITHMETIC (published so a reader who rejects the bin convention re-derives
without a re-run):

    WIDE_EXTRA  = WIDE - NARROW                       (the named-reference part alone)
    WIDE        = NARROW + WIDE_EXTRA
    CORPUS      = NARROW + WIDE_EXTRA + CONDITIONAL   (an exact three-way partition of
                                                       every tracked file under skills/)

Every emitted row carries NARROW, WIDE_EXTRA and CONDITIONAL as disjoint columns, so any
of the four quantities above is recoverable by addition from the committed dataset alone.

GROSS, NEVER NET
----------------
Gate (a) asks whether deletion keeps up with growth, so growth is measured DIRECTLY.
Per interval, per bin, the dataset carries `added` and `deleted` SEPARATELY (words, bytes
and lines). Endpoint differences are emitted too, but only as `net_*`, and no row is
net-only. Gross words/bytes come from `git diff --word-diff=porcelain`; gross lines from
`git diff --numstat`.

CALIBRATION OF THE GROSS MEASUREMENT (external oracle, see `--calibrate-gross`)
------------------------------------------------------------------------------
#304 published its own deletion event with exact arithmetic: 172 words deleted, +4 added,
corpus -168. This instrument measures that same interval as 173 gross deleted / 5 gross
added, net -168 — the NET agrees exactly. The +1/-1 is not instrument error: #304's "+4"
is a NET figure for the retarget hunk (`from the current map using` -> `from the map input
the context step resolved, using`, 9 words in for 5 words out = +4 net), while its "172"
counts only the dead-path block and omits the 1 word (`current`) the retarget removed.
Gross is 5 in / 173 out; 5 - 173 = -168 = 4 - 172. Both bookkeepings close on the same net.
This instrument reports the GROSS pair, and says so here rather than silently disagreeing.

A ROLE'S DEATH IS AN ORG CHANGE, NEVER DELETION PRESSURE
--------------------------------------------------------
Per interval the dataset names `roles_entered` and `roles_left` explicitly, and splits out
`deleted_words_role_departure` per bin, so:

    deletion_pressure_words = deleted_words - deleted_words_role_departure

`git log --follow` is FORBIDDEN here, so a role RENAME is unavoidably visible to git as a
death plus a birth. The correction for that is `ROLE_LINEAGE` below, which is HAND-AUTHORED
DATA, not a measurement. It is stated here, and again in the emitted manifest and in
TRENDS.md, because a reader must see it where the numbers are, not in a methods appendix.

WHAT COULD NOT BE REUSED FROM #307's INSTRUMENTS, AND WHY
---------------------------------------------------------
`.agent-work/epic-298/preb/fingerprint_global_corpus.py` is REUSED for its conventions:
raw-bytes-not-decoded-text digests, sorted path order, path-relative keys, and
`json.dumps(..., indent=2) + "\n"` written `encoding="utf-8", newline="\n"`.
Its ENUMERATION cannot be reused: it walks the INSTALLED global corpus on the filesystem
(`~/.claude/skills/constellation-*`) with no revision parameter and no git access at all,
and its output unit is a single digest, not a per-bin size. A trend across 184 revisions
cannot be taken from a filesystem that only holds one of them. Nothing else from
`.agent-work/epic-298/preb/` or `.agent-work/epic-298/post/` is rebuilt here.

NO CHECKOUT, EVER. `git ls-tree -r --long` gives blob sizes; `git cat-file --batch` gives
content; `git diff` gives gross. The working tree is never mutated.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]

# --- Addressed BY TAG, never by bare sha: these commits are NOT ancestors of main
# (#304 squash-merged), so a `rev-list` walk never visits them and a bare sha is
# GC-eligible.  The shas are recorded only as an assertion target.
BASELINE_TAG = "baseline/304-trend-snapshot"
G2_TAG = "baseline/304-g2-approve"
EXPECTED_TAG_SHA = {BASELINE_TAG: "fc1685a", G2_TAG: "a8d9467"}

# #304's merged (squashed) form on main.  The delta between this and BASELINE_TAG is
# itself a finding about what squash-merge does to a published baseline.
MERGED_304 = "5d2585b"

# TREND_SNAPSHOT.md §1, published at BASELINE_TAG.  BLOCKING external oracle.
BASELINE_ORACLE = {
    "skillmd_files": 19,
    "skillmd_words": 15831,
    "corpus_files": 100,
    "corpus_words": 63681,
}

# =========================== HAND-AUTHORED DATA — NOT A MEASUREMENT ==========================
# `git log --follow` is FORBIDDEN here, so a role RENAME reads to git as a death plus a
# birth.  This table is the correction, and it is JUDGEMENT, not measurement: the
# full-history design does not remove the hand-chosen judgement call, it RELOCATES it
# from revision-choice to role-lineage-choice.  Said here, and repeated in the emitted
# manifest and in TRENDS.md, because a reader must meet it where the numbers are.
#
# Audit it, do not trust it: `measure_surface.py --role-lineage` enumerates EVERY birth
# and death (25 births, 6 deaths, final count 19) so this table can be checked against
# the raw enumeration rather than believed.
#
# Each entry's `evidence` is the commit whose own `git diff --name-status -M` or subject
# line establishes the claim.
ROLE_LINEAGE: list[dict] = [
    {"kind": "rename", "from": ["conductor"], "to": ["pilot"], "evidence": "3c24f7c",
     "note": "commit subject: 'renamed from conductor to pilot'; R-status on all 6 files"},
    {"kind": "fold", "from": ["pilot"], "to": ["commander"], "evidence": "90cf856",
     "note": "commit subject: 'fold pilot into commander'; D-status, content diverged so "
             "git records no rename"},
    {"kind": "split", "from": ["crew"], "to": ["implementer", "reviewer"], "evidence": "a6233e6",
     "note": "R-status renames of crew/templates/* into implementer/ and reviewer/"},
    {"kind": "walk-order-artifact", "from": ["docent"], "to": ["docent"], "evidence": "75ca633",
     "note": "NOT an org change: a main-line commit ordered after a branch commit that "
             "had already introduced docent; re-appears at merge 58e5acd"},
    {"kind": "walk-order-artifact", "from": ["explorer", "prototyper"],
     "to": ["explorer", "prototyper"], "evidence": "2c84955",
     "note": "NOT an org change: same branch/main interleaving; re-appears at merge 06b7a86"},
]
# Roles whose disappearance is a walk-order artifact rather than a death at all.
_ARTIFACT_DEATHS = {r for e in ROLE_LINEAGE if e["kind"] == "walk-order-artifact" for r in e["from"]}
# ============================================================================================

# The `references/<file>` token form a SKILL.md uses to name a reference.
REF_TOKEN = re.compile(r"references/([A-Za-z0-9][A-Za-z0-9_.\-]*\.[A-Za-z0-9]+)")

BINS = ("NARROW-ALWAYS-LOADED", "WIDE-EXTRA", "CONDITIONALLY-LOADED")
NARROW, WIDE_EXTRA, COND = BINS


# --------------------------------------------------------------------------- git


def git(*args: str, binary: bool = False):
    r = subprocess.run(["git", "-C", str(REPO), *args], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} -> {r.returncode}: {r.stderr.decode(errors='replace')}")
    return r.stdout if binary else r.stdout.decode("utf-8", errors="surrogateescape")


def rev(spec: str) -> str:
    return git("rev-parse", f"{spec}^{{commit}}").strip()


class BlobCache:
    """One persistent `git cat-file --batch`; blobs repeat heavily across 184 revisions."""

    def __init__(self) -> None:
        self.p = subprocess.Popen(
            ["git", "-C", str(REPO), "cat-file", "--batch"],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
        )
        self.cache: dict[str, bytes] = {}

    def get(self, oid: str) -> bytes:
        if oid in self.cache:
            return self.cache[oid]
        self.p.stdin.write((oid + "\n").encode())
        self.p.stdin.flush()
        header = self.p.stdout.readline().decode().strip()
        parts = header.split()
        if len(parts) != 3:
            raise RuntimeError(f"cat-file refused {oid!r}: {header!r}")
        size = int(parts[2])
        data = self.p.stdout.read(size)
        self.p.stdout.read(1)  # trailing LF
        self.cache[oid] = data
        return data

    def close(self) -> None:
        try:
            self.p.stdin.close()
            self.p.wait(timeout=10)
        except Exception:
            self.p.kill()


def ls_tree(revision: str) -> dict[str, tuple[str, int]]:
    """path -> (blob oid, byte size) for every tracked file under skills/ at `revision`."""
    out = git("ls-tree", "-r", "--long", revision, "--", "skills")
    tree: dict[str, tuple[str, int]] = {}
    for line in out.split("\n"):
        if not line.strip():
            continue
        meta, path = line.split("\t", 1)
        _mode, otype, oid, size = meta.split()
        if otype != "blob":
            continue
        tree[path] = (oid, int(size))
    return tree


# --------------------------------------------------------- bundles / bins / roles


def _literal(node: ast.AST, env: dict) -> tuple:
    """Evaluate the tiny expression grammar `SKILL_REFERENCE_BUNDLES` actually uses:
    tuple literals, names bound to tuples, and `+` concatenation of those."""
    if isinstance(node, ast.Tuple):
        return tuple(ast.literal_eval(e) for e in node.elts)
    if isinstance(node, ast.Name):
        return tuple(env[node.id])
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        return _literal(node.left, env) + _literal(node.right, env)
    return tuple(ast.literal_eval(node))


def parse_bundles(src: str) -> dict[str, tuple[str, ...]] | None:
    """Parse (NEVER execute) SKILL_REFERENCE_BUNDLES out of an installer's source.

    Returns None — NOT {} — when the mechanism is absent.  Undefined is not zero, and
    the distinction is carried all the way to the emitted dataset as `null`."""
    if "SKILL_REFERENCE_BUNDLES" not in src:
        return None
    tree = ast.parse(src)
    env: dict[str, tuple] = {}
    bundles: dict[str, tuple[str, ...]] | None = None
    for node in tree.body:
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        name = getattr(targets[0], "id", None)
        if name is None or node.value is None:
            continue
        if name.startswith("_GLOBAL"):
            env[name] = _literal(node.value, env)
        elif name == "SKILL_REFERENCE_BUNDLES" and isinstance(node.value, ast.Dict):
            bundles = {
                ast.literal_eval(k): _literal(v, env)
                for k, v in zip(node.value.keys, node.value.values)
            }
    return bundles


def bundles_at(revision: str, blobs: BlobCache) -> dict[str, tuple[str, ...]] | None:
    """That commit's OWN SKILL_REFERENCE_BUNDLES.  None before the regime boundary."""
    try:
        raw = git("show", f"{revision}:scripts/install_constellation.py", binary=True)
    except RuntimeError:
        return None
    return parse_bundles(raw.decode("utf-8", errors="surrogateescape"))


def roles_at(tree: dict[str, tuple[str, int]]) -> list[str]:
    """A role is a `skills/<name>/` directory holding a SKILL.md.

    `_shared` is NOT a skill — `scripts/install_constellation.py` skips any directory
    whose name starts with `_` (see `discover_skills`).  TREND_SNAPSHOT §2 lists it as a
    20th role; that is a DEFECT, filed as #411, and this instrument deliberately diverges
    from the baseline there."""
    return sorted(
        p.split("/")[1]
        for p in tree
        if p.count("/") == 2 and p.endswith("/SKILL.md") and not p.split("/")[1].startswith("_")
    )


def classify(tree: dict[str, tuple[str, int]], revision: str, blobs: BlobCache) -> dict:
    """Partition every tracked skills/ path into exactly one of the three bins."""
    roles = roles_at(tree)
    bundles = bundles_at(revision, blobs)

    named: set[str] = set()
    unresolved: list[str] = []
    per_role_refs: dict[str, dict[str, list[str]]] = {}

    for role in roles:
        body = blobs.get(tree[f"skills/{role}/SKILL.md"][0]).decode("utf-8", errors="surrogateescape")
        local, shared, miss = [], [], []
        for token in sorted(set(REF_TOKEN.findall(body))):
            local_path = f"skills/{role}/references/{token}"
            shared_path = f"skills/_shared/{token}"
            if local_path in tree:                                   # role-local FIRST
                named.add(local_path)
                local.append(token)
            elif bundles is not None and token in bundles.get(role, ()) and shared_path in tree:
                named.add(shared_path)                               # then that commit's bundles
                shared.append(token)
            else:
                miss.append(token)
                unresolved.append(f"{role}:{token}")
        per_role_refs[role] = {
            "local": local,
            # null, never [], before the regime boundary: the mechanism does not exist
            "bundled": shared if bundles is not None else None,
            "unresolved": miss,
        }

    bins: dict[str, str] = {}
    for path in tree:
        parts = path.split("/")
        if len(parts) == 3 and parts[2] == "SKILL.md" and not parts[1].startswith("_"):
            bins[path] = NARROW
        elif path in named:
            bins[path] = WIDE_EXTRA
        else:
            bins[path] = COND

    # An unresolved token is a CROSS-ROLE citation (e.g. implementer citing workbench's
    # `references/checklist-engine.md`).  The Admiral's rule resolves role-locally then
    # through the bundle, and neither reaches another role's references/ — so the token
    # is unresolved.  It only under-counts WIDE if the target is not already pulled in
    # by its OWNING role, so that is computed rather than asserted by hand.
    uncovered = sorted(
        t for t in unresolved
        if not any(p.endswith("/references/" + t.split(":", 1)[1])
                   or p == "skills/_shared/" + t.split(":", 1)[1] for p in named)
    )

    return {
        "roles": roles,
        "bundles_defined": bundles is not None,
        "bins": bins,
        "named_refs": sorted(named),
        "unresolved_ref_tokens": sorted(unresolved),
        "unresolved_ref_tokens_uncovered": uncovered,
        # Shipped into every consuming role's references/ by the installer, yet named by
        # no SKILL.md — so the Admiral's rule puts them in CONDITIONALLY-LOADED.  Named
        # explicitly because a reader may reasonably disagree and the recombination
        # arithmetic lets them move it without a re-run.
        "shared_files_not_named": sorted(
            p for p in tree if p.startswith("skills/_shared/") and p not in named
        ),
        "per_role_refs": per_role_refs,
    }


_TREE_MEMO: dict[str, dict] = {}
_CLS_MEMO: dict[str, dict] = {}
_SNAP_MEMO: dict[str, dict] = {}
_BLOBS: BlobCache | None = None


def shared_blobs() -> BlobCache:
    """One `git cat-file --batch` for the whole process.  Pure-function memoization: a
    revision is immutable, so caching cannot change any answer."""
    global _BLOBS
    if _BLOBS is None:
        _BLOBS = BlobCache()
    return _BLOBS


def tree_of(revision: str) -> dict[str, tuple[str, int]]:
    """Memoized `ls_tree`.  Pure function of the (immutable) revision, so memoizing
    cannot change any answer — it only stops the census re-reading each tree 3x."""
    if revision not in _TREE_MEMO:
        _TREE_MEMO[revision] = ls_tree(revision)
    return _TREE_MEMO[revision]


def classified(revision: str, blobs: BlobCache) -> dict:
    if revision not in _CLS_MEMO:
        _CLS_MEMO[revision] = classify(tree_of(revision), revision, blobs)
    return _CLS_MEMO[revision]


def words(data: bytes) -> int:
    """`wc -w` semantics: runs of non-whitespace over raw bytes."""
    return len(data.split())


def lines(data: bytes) -> int:
    return data.count(b"\n")


def snapshot(revision: str, blobs: BlobCache) -> dict:
    if revision not in _SNAP_MEMO:
        _SNAP_MEMO[revision] = _snapshot(revision, blobs)
    return _SNAP_MEMO[revision]


def _snapshot(revision: str, blobs: BlobCache) -> dict:
    """Every figure at one revision, per bin and per role."""
    tree = tree_of(revision)
    cls = classified(revision, blobs)

    agg = {b: {"files": 0, "words": 0, "bytes": 0, "lines": 0} for b in BINS}
    per_role = {}
    for path, (oid, size) in sorted(tree.items()):
        data = blobs.get(oid)
        b = cls["bins"][path]
        agg[b]["files"] += 1
        agg[b]["words"] += words(data)
        agg[b]["bytes"] += size
        agg[b]["lines"] += lines(data)

    for role in cls["roles"]:
        skill_md = blobs.get(tree[f"skills/{role}/SKILL.md"][0])
        owned = [p for p in tree if p.startswith(f"skills/{role}/")]
        per_role[role] = {
            "narrow_words": words(skill_md),
            "narrow_bytes": tree[f"skills/{role}/SKILL.md"][1],
            "narrow_lines": lines(skill_md),
            "role_files": len(owned),
            "role_words": sum(words(blobs.get(tree[p][0])) for p in owned),
            "refs": cls["per_role_refs"][role],
        }

    # Corpus totals reproduced with the BASELINE'S OWN concatenation semantics
    # (`git ls-files ... | xargs -0 cat | wc -w`).  This is not pedantry: exactly one
    # file at the baseline (skills/commander/templates/COMMANDER_SPINE.template.json)
    # lacks a trailing newline, so its last word fuses with the next file's first word
    # and the CONCATENATED total is 63681 while the PER-FILE SUM is 63682.
    ordered = [blobs.get(oid) for _p, (oid, _s) in sorted(tree.items())]
    concat_words = words(b"".join(ordered))
    skillmd_paths = sorted(p for p, b in cls["bins"].items() if b == NARROW)
    concat_skillmd_words = words(b"".join(blobs.get(tree[p][0]) for p in skillmd_paths))

    return {
        "rev": revision,
        "date": git("log", "-1", "--format=%ad", "--date=short", revision).strip(),
        "subject": git("log", "-1", "--format=%s", revision).strip(),
        "roles": cls["roles"],
        "role_count": len(cls["roles"]),
        "bundles_defined": cls["bundles_defined"],
        "bins": agg,
        "corpus": {
            "files": len(tree),
            "words_per_file_sum": sum(v["words"] for v in agg.values()),
            "words_concatenated": concat_words,
            "bytes": sum(v["bytes"] for v in agg.values()),
        },
        "narrow_concatenated_words": concat_skillmd_words,
        "unresolved_ref_tokens": cls["unresolved_ref_tokens"],
        "unresolved_ref_token_count": len(cls["unresolved_ref_tokens"]),
        "unresolved_ref_tokens_uncovered": cls["unresolved_ref_tokens_uncovered"],
        "unresolved_ref_tokens_uncovered_count": len(cls["unresolved_ref_tokens_uncovered"]),
        "shared_files_not_named": cls["shared_files_not_named"],
        "named_ref_count": len(cls["named_refs"]),
        "per_role": per_role,
        "tree_digest": hashlib.sha256(
            b"".join(p.encode() + blobs.get(o) for p, (o, _s) in sorted(tree.items()))
        ).hexdigest(),
    }


# ------------------------------------------------------------------ gross deltas


def gross(prev: str, cur: str, bin_of: dict[str, str]) -> dict:
    """Gross added and gross deleted, SEPARATELY, per bin.  Never a net-only row."""
    per_bin = {b: {"added_words": 0, "deleted_words": 0, "added_bytes": 0,
                   "deleted_bytes": 0, "added_lines": 0, "deleted_lines": 0} for b in BINS}
    per_file: dict[str, dict[str, int]] = {}

    out = git("diff", "--word-diff=porcelain", "--unified=0", prev, cur, "--", "skills/")
    path, in_hunk = None, False
    for line in out.split("\n"):
        if line.startswith("diff --git "):
            path = line.split(" b/", 1)[-1]
            in_hunk = False
            per_file.setdefault(path, {"added_words": 0, "deleted_words": 0,
                                       "added_bytes": 0, "deleted_bytes": 0,
                                       "added_lines": 0, "deleted_lines": 0})
            continue
        if line.startswith("@@"):
            in_hunk = True
            continue
        if not in_hunk or path is None:
            continue
        if line.startswith("+"):
            t = line[1:]
            per_file[path]["added_words"] += len(t.split())
            per_file[path]["added_bytes"] += len(t.encode("utf-8", "surrogateescape"))
        elif line.startswith("-"):
            t = line[1:]
            per_file[path]["deleted_words"] += len(t.split())
            per_file[path]["deleted_bytes"] += len(t.encode("utf-8", "surrogateescape"))

    for line in git("diff", "--numstat", prev, cur, "--", "skills/").split("\n"):
        if not line.strip():
            continue
        a, d, p = line.split("\t", 2)
        if a == "-":  # binary
            a = d = "0"
        per_file.setdefault(p, {"added_words": 0, "deleted_words": 0, "added_bytes": 0,
                                "deleted_bytes": 0, "added_lines": 0, "deleted_lines": 0})
        per_file[p]["added_lines"] += int(a)
        per_file[p]["deleted_lines"] += int(d)

    for p, v in per_file.items():
        b = bin_of.get(p, COND)
        for k in v:
            per_bin[b][k] += v[k]
    return {"per_bin": per_bin, "per_file": per_file}


# ------------------------------------------------------------------- the census


def census(head: str = "HEAD") -> dict:
    blobs = BlobCache()
    try:
        head_rev = rev(head)
        base_rev, g2_rev = rev(BASELINE_TAG), rev(G2_TAG)
        for tag, want in EXPECTED_TAG_SHA.items():
            got = rev(tag)
            if not got.startswith(want):
                raise RuntimeError(f"tag {tag} resolves to {got}, expected {want}*")

        walk = [c for c in git("rev-list", "--reverse", head_rev, "--", "skills/").split() if c]
        walk_count = len(walk)
        # The tagged baselines are NOT ancestors of main (#304 squash-merged), so the
        # rev-list walk NEVER visits them.  Union them in explicitly, then re-sort the
        # whole set into commit-date order so the series reads chronologically.
        off_line = [c for c in (g2_rev, base_rev) if c not in walk]
        # HEAD is the measurement ENDPOINT and must be a row, but HEAD itself may not
        # have touched skills/ — in which case rev-list never yields it either.  Union
        # it in too, and record that it is not a change row (on_main_line stays False,
        # so it is never counted as one of the n changes in the window).
        head_off_line = head_rev not in walk and head_rev not in off_line
        if head_off_line:
            off_line = off_line + [head_rev]
        allrevs = walk + off_line
        order = {c: git("log", "-1", "--format=%ct", c).strip() for c in allrevs}
        allrevs.sort(key=lambda c: (int(order[c]), c))

        snaps = [snapshot(c, blobs) for c in allrevs]
        by_rev = {s["rev"]: s for s in snaps}

        rows = []
        for i, s in enumerate(snaps):
            row = {
                "i": i,
                "rev": s["rev"],
                "short": s["rev"][:7],
                "date": s["date"],
                "on_main_line": s["rev"] in walk,
                "role_count": s["role_count"],
                "bundles_defined": s["bundles_defined"],
                "levels": {b: dict(s["bins"][b]) for b in BINS},
                "corpus_files": s["corpus"]["files"],
                "corpus_words_concatenated": s["corpus"]["words_concatenated"],
                "narrow_concatenated_words": s["narrow_concatenated_words"],
                "unresolved_ref_token_count": s["unresolved_ref_token_count"],
            }
            if i == 0:
                row["interval"] = None
            else:
                prev = snaps[i - 1]
                cls_cur = classified(s["rev"], blobs)
                cls_prev = classified(prev["rev"], blobs)
                bin_of = dict(cls_prev["bins"])
                bin_of.update(cls_cur["bins"])  # bin at `cur` wins; deleted files keep `prev`'s

                g = gross(prev["rev"], s["rev"], bin_of)
                entered = sorted(set(s["roles"]) - set(prev["roles"]))
                left = sorted(set(prev["roles"]) - set(s["roles"]))

                # A role's DEATH is an ORG CHANGE and must never read as deletion
                # pressure.  Split it out so a reader can subtract it.
                dep = {b: {"deleted_words": 0, "deleted_bytes": 0, "deleted_lines": 0} for b in BINS}
                if left:
                    for p, v in g["per_file"].items():
                        r = p.split("/")[1] if p.count("/") >= 2 else ""
                        if r in left:
                            b = bin_of.get(p, COND)
                            for k in dep[b]:
                                dep[b][k] += v[k]

                row["interval"] = {
                    "from": prev["rev"],
                    "from_short": prev["rev"][:7],
                    # Classified from HAND-AUTHORED ROLE_LINEAGE, never from git.
                    "roles_left_classification": {
                        r: ("walk-order-artifact" if r in _ARTIFACT_DEATHS else "org-change")
                        for r in sorted(set(prev["roles"]) - set(s["roles"]))
                    },
                    "days": (
                        int((int(order[s["rev"]]) - int(order[prev["rev"]])) / 86400)
                    ),
                    "gross": g["per_bin"],
                    "deleted_role_departure": dep,
                    "roles_entered": entered,
                    "roles_left": left,
                    "net": {
                        b: {
                            k: s["bins"][b][k] - prev["bins"][b][k]
                            for k in ("files", "words", "bytes", "lines")
                        }
                        for b in BINS
                    },
                }
            rows.append(row)

        # ---- the enumerated DELETION-EVENT SET (§3's analogue).  May be EMPTY; an
        # empty set with its count asserted is a complete reportable result.
        deletions = []
        for row in rows:
            iv = row.get("interval")
            if not iv:
                continue
            for b in BINS:
                dw = iv["gross"][b]["deleted_words"] - iv["deleted_role_departure"][b]["deleted_words"]
                if dw > 0:
                    deletions.append({
                        "rev": row["rev"], "short": row["short"], "date": row["date"],
                        "bin": b, "deleted_words": dw,
                        "added_words": iv["gross"][b]["added_words"],
                        "net_words": iv["net"][b]["words"],
                    })

        window = window_rows(rows, base_rev, head_rev, walk)

        return {
            "schema": "issue-310-surface-census/1",
            "manifest": {
                "bin_ruling": (
                    "The WIDE bin is a RECONSTRUCTION RULED BY THE ADMIRAL, not a contract "
                    "discovered in the tree — nothing in the tree declares one."
                ),
                "never_summed": "NARROW and WIDE overlap by construction and are NEVER summed.",
                "recombination": {
                    "WIDE": "NARROW + WIDE-EXTRA",
                    "CORPUS": "NARROW + WIDE-EXTRA + CONDITIONALLY-LOADED",
                    "note": "the three emitted bins are a disjoint partition of every tracked skills/ file",
                },
                "gross_not_net": "per interval, per bin: added_* and deleted_* are separate; net_* is supplementary",
                "role_lineage_is_hand_authored": (
                    "git log --follow is forbidden, so a role RENAME reads to git as a death "
                    "plus a birth.  ROLE_LINEAGE in measure_surface.py is HAND-AUTHORED DATA, "
                    "not a measurement."
                ),
                "role_lineage": ROLE_LINEAGE,
                "per_pr_not_per_edit": (
                    "This repo SQUASH-MERGES, so the series is per-PR, not per-edit: "
                    "intra-PR grow-then-shrink is invisible to every row below."
                ),
                "shared_role_defect": (
                    "_shared is NOT a role (install_constellation.py skips names starting '_'). "
                    "TREND_SNAPSHOT §2 lists it as a 20th role; that is a defect filed as #411 "
                    "and this instrument deliberately diverges from the baseline there."
                ),
                "no_checkout": "measured entirely via ls-tree/cat-file/diff; the working tree is never touched",
                "concatenation_note": (
                    "corpus_words_concatenated reproduces the baseline's own "
                    "`xargs -0 cat | wc -w` semantics; words_per_file_sum can differ by the "
                    "number of files lacking a trailing newline."
                ),
            },
            "revisions": {
                "head": head_rev,
                "head_short": head_rev[:7],
                "baseline_tag": BASELINE_TAG,
                "baseline_rev": base_rev,
                "g2_tag": G2_TAG,
                "g2_rev": g2_rev,
                "merged_304": rev(MERGED_304),
                "merge_base_baseline_head": git("merge-base", base_rev, head_rev).strip(),
                "baseline_is_ancestor_of_head": subprocess.run(
                    ["git", "-C", str(REPO), "merge-base", "--is-ancestor", base_rev, head_rev]
                ).returncode == 0,
            },
            "counts": {
                "revlist_commits_touching_skills": walk_count,
                "off_line_baselines_unioned": len(off_line),
                "head_unioned_because_it_touches_no_skills_file": head_off_line,
                "census_rows": len(rows),
                "deletion_events": len(deletions),
                "roles_at_head": by_rev[head_rev]["role_count"],
                "unresolved_ref_tokens_at_head": by_rev[head_rev]["unresolved_ref_token_count"],
            },
            "baseline_oracle": {
                "expected": BASELINE_ORACLE,
                "measured": oracle_measure(by_rev[base_rev]),
                "reproduced": oracle_measure(by_rev[base_rev]) == BASELINE_ORACLE,
            },
            "window": window,
            "deletion_events": deletions,
            "rows": rows,
            "head_snapshot": by_rev[head_rev],
            "baseline_snapshot": by_rev[base_rev],
        }
    finally:
        blobs.close()


def oracle_measure(snap: dict) -> dict:
    return {
        "skillmd_files": snap["bins"][NARROW]["files"],
        "skillmd_words": snap["narrow_concatenated_words"],
        "corpus_files": snap["corpus"]["files"],
        "corpus_words": snap["corpus"]["words_concatenated"],
    }


def window_rows(rows: list[dict], base_rev: str, head_rev: str, walk: list[str]) -> dict:
    """The baseline..HEAD window, with n reported AMBIGUOUSLY on purpose.

    The baseline is NOT an ancestor of main, so whether `5d2585b` — #304's own
    squash-merge — counts as a change SINCE a baseline taken mid-flight WITHIN it is a
    judgement call.  This run picks NEITHER silently: both counts are emitted."""
    idx = {r["rev"]: i for i, r in enumerate(rows)}
    b, h = idx[base_rev], idx[head_rev]
    after = [r for r in rows[b + 1: h + 1] if r["on_main_line"]]
    merged = [r for r in after if r["short"].startswith(MERGED_304[:7])]

    # §3's analogue, scoped to the WINDOW: the enumerated deletion-event set.  It MAY be
    # empty; an empty set with its count asserted is a complete reportable result.
    # "Deletion pressure" excludes any deletion attributable to a role LEAVING, because a
    # role's death is an org change and must never read as deletion pressure.
    win_events = []
    for r in rows[b + 1: h + 1]:
        iv = r.get("interval")
        if not iv:
            continue
        for bin_ in BINS:
            dw = (iv["gross"][bin_]["deleted_words"]
                  - iv["deleted_role_departure"][bin_]["deleted_words"])
            if dw > 0:
                win_events.append({
                    "short": r["short"], "date": r["date"], "bin": bin_,
                    "deleted_words": dw,
                    "added_words": iv["gross"][bin_]["added_words"],
                    "net_words": iv["net"][bin_]["words"],
                })
    return {
        "deletion_events": win_events,
        "deletion_event_count": len(win_events),
        "from": base_rev,
        "from_tag": BASELINE_TAG,
        "to": head_rev,
        "n_including_squash_merge": len(after),
        "n_excluding_squash_merge": len(after) - len(merged),
        "n_is_ambiguous_because": (
            "the baseline is NOT an ancestor of main (#304 squash-merged), so whether "
            "5d2585b — #304's OWN squash-merge — counts as a change since a baseline "
            "taken mid-flight within it is a judgement call.  This run picks neither."
        ),
        "commits": [{"short": r["short"], "date": r["date"]} for r in after],
        "days": sum(r["interval"]["days"] for r in rows[b + 1: h + 1] if r.get("interval")),
        "delta": {
            "narrow_words": rows[h]["levels"][NARROW]["words"] - rows[b]["levels"][NARROW]["words"],
            "narrow_concatenated_words": rows[h]["narrow_concatenated_words"] - rows[b]["narrow_concatenated_words"],
            "wide_extra_words": rows[h]["levels"][WIDE_EXTRA]["words"] - rows[b]["levels"][WIDE_EXTRA]["words"],
            "conditional_words": rows[h]["levels"][COND]["words"] - rows[b]["levels"][COND]["words"],
            "corpus_words_concatenated": rows[h]["corpus_words_concatenated"] - rows[b]["corpus_words_concatenated"],
        },
        "gross": {
            bin_: {
                k: sum(r["interval"]["gross"][bin_][k] for r in rows[b + 1: h + 1] if r.get("interval"))
                for k in ("added_words", "deleted_words", "added_bytes", "deleted_bytes",
                          "added_lines", "deleted_lines")
            }
            for bin_ in BINS
        },
    }


# ----------------------------------------------------------------------- panel

# The panel is the REPORTING/INTERPRETATION layer over the census, NEVER the
# measurement.  Every figure it shows is recomputed from the same census functions; the
# only thing hand-chosen here is WHICH revisions are worth a reader's attention, and each
# choice carries its justification inline so the choice can be argued with.
PANEL: list[dict] = [
    {"spec": "a83a3be", "label": "corpus birth",
     "justification": "the first commit that contains skills/ at all — H2's left endpoint, "
                      "and the earliest revision the NARROW series can be compared from"},
    {"spec": "84fd28f^", "label": "last pre-regime revision",
     "justification": "the last revision at which SKILL_REFERENCE_BUNDLES and skills/_shared/ "
                      "do not exist, so the WIDE bin's bundled component is UNDEFINED (null, "
                      "not zero) and the WIDE series cannot be carried across this point"},
    {"spec": "84fd28f", "label": "regime boundary",
     "justification": "verified (not assumed) as the FIRST commit introducing both "
                      "SKILL_REFERENCE_BUNDLES and skills/_shared/; WIDE becomes defined here"},
    {"spec": G2_TAG, "label": "#304 g2 approve",
     "justification": "the left endpoint of the ONLY deletion event in this corpus documented "
                      "with exact published arithmetic — the external calibration for gross"},
    {"spec": BASELINE_TAG, "label": "#304 declared baseline",
     "justification": "the blocking oracle and the successor comparison's left endpoint; "
                      "addressed BY TAG because it is not an ancestor of main"},
    {"spec": MERGED_304, "label": "#304 squash-merge onto main",
     "justification": "the revision whose countability makes n ambiguous (2 or 3); included "
                      "so a reader can see for themselves that it is a zero-delta row"},
    {"spec": "HEAD", "label": "measurement endpoint",
     "justification": "this run's HEAD; its skills/ tree is identical to origin/main's, so "
                      "the Commander's origin/main figures and these are the same measurement"},
]


def unit_ranks(snap: dict) -> dict:
    """H3's test: does the 'biggest role' depend on the UNIT chosen?  No unit is chosen
    anywhere in the corpus, so this is not a curiosity — it decides whether any threshold
    is breached."""
    pr = snap["per_role"]
    by = {
        u: [k for k, _ in sorted(pr.items(), key=lambda kv: (-kv[1][f"narrow_{u}"], kv[0]))]
        for u in ("lines", "bytes", "words")
    }
    return {
        "argmax_by_lines": by["lines"][0],
        "argmax_by_bytes": by["bytes"][0],
        "argmax_by_words": by["words"][0],
        "reversal": by["lines"][0] != by["bytes"][0],
        "rank_by_lines": {r: i + 1 for i, r in enumerate(by["lines"])},
        "rank_by_bytes": {r: i + 1 for i, r in enumerate(by["bytes"])},
        "top5_by_lines": [(r, pr[r]["narrow_lines"]) for r in by["lines"][:5]],
        "top5_by_bytes": [(r, pr[r]["narrow_bytes"]) for r in by["bytes"][:5]],
    }


_PANEL_MEMO: dict | None = None


def build_panel() -> dict:
    global _PANEL_MEMO
    if _PANEL_MEMO is not None:
        return _PANEL_MEMO
    blobs = shared_blobs()
    if True:
        out = []
        for entry in PANEL:
            r = rev(entry["spec"])
            snap = snapshot(r, blobs)
            out.append({
                "spec": entry["spec"],
                "label": entry["label"],
                "justification": entry["justification"],
                "rev": r,
                "short": r[:7],
                "date": snap["date"],
                "role_count": snap["role_count"],
                "bundles_defined": snap["bundles_defined"],
                "narrow_words": snap["bins"][NARROW]["words"],
                "narrow_concatenated_words": snap["narrow_concatenated_words"],
                "wide_extra_words": snap["bins"][WIDE_EXTRA]["words"],
                # The BUNDLED component alone is UNDEFINED before the regime boundary —
                # null, never 0.  "0 bundled resolutions" would read as a measurement;
                # this is the absence of the mechanism that would be measured.
                "bundled_resolutions": (
                    None if not snap["bundles_defined"]
                    else sum(len(r_["refs"]["bundled"] or ()) for r_ in snap["per_role"].values())
                ),
                "conditional_words": snap["bins"][COND]["words"],
                "corpus_words_concatenated": snap["corpus"]["words_concatenated"],
                "corpus_files": snap["corpus"]["files"],
                "narrow_words_per_role_mean": round(
                    snap["bins"][NARROW]["words"] / snap["role_count"], 1),
                "unit_ranks": unit_ranks(snap),
            })
        reversals = sum(1 for e in out if e["unit_ranks"]["reversal"])
        result = {
            "schema": "issue-310-panel/1",
            "role": ("REPORTING/INTERPRETATION LAYER ONLY. The panel is never the "
                     "measurement — every figure here is recomputed by the same census "
                     "functions that produce trends.json. The only hand-chosen thing is "
                     "WHICH revisions a reader should look at, and each carries its "
                     "justification inline."),
            "revisions": out,
            "h3_unit_dependence": {
                "panel_revisions": len(out),
                "revisions_where_argmax_lines_differs_from_argmax_bytes": reversals,
                "verdict": ("PERSISTS" if reversals == len(out) else
                            "PARTIAL" if reversals else "NOT OBSERVED"),
            },
        }
        _PANEL_MEMO = result
        return result


# ------------------------------------------------------------------- entrypoints


def dump(obj: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8", newline="\n")


def cmd_reproduce_baseline(at: str) -> int:
    """BLOCKING external oracle.  If it does not reproduce, the series is VOID —
    report it, do not tune until it agrees."""
    blobs = BlobCache()
    try:
        r = rev(at)
        snap = snapshot(r, blobs)
    finally:
        blobs.close()
    got = oracle_measure(snap)
    print(f"reproducing TREND_SNAPSHOT sec.1 at {at}  (= {r[:7]})")
    ok = True
    for k, want in BASELINE_ORACLE.items():
        mark = "OK " if got[k] == want else "MISMATCH"
        if got[k] != want:
            ok = False
        print(f"  {mark:9s} {k:<16s} expected {want:>7d}  measured {got[k]:>7d}")
    print(f"  (per-file-sum corpus words = {snap['corpus']['words_per_file_sum']}, "
          f"concatenated = {snap['corpus']['words_concatenated']})")
    print(f"  roles = {snap['role_count']} (expect 19; _shared is NOT a role)")
    if snap["role_count"] != 19:
        ok = False
        print("  MISMATCH  role_count")
    print("BASELINE REPRODUCED" if ok else "BASELINE NOT REPRODUCED -> THE SERIES IS VOID")
    return 0 if ok else 1


def cmd_calibrate_gross() -> int:
    """Calibrate the gross-word measurement against #304's own published deletion event."""
    blobs = BlobCache()
    try:
        a, b = rev(G2_TAG), rev(BASELINE_TAG)
        cls = classify(ls_tree(b), b, blobs)
        g = gross(a, b, cls["bins"])
    finally:
        blobs.close()
    print(f"{G2_TAG} ({a[:7]}) -> {BASELINE_TAG} ({b[:7]})")
    for p, v in sorted(g["per_file"].items()):
        print(f"  {p}\n    +{v['added_words']}w -{v['deleted_words']}w "
              f"+{v['added_bytes']}B -{v['deleted_bytes']}B  bin={cls['bins'].get(p)}")
    tot_a = sum(v["added_words"] for v in g["per_file"].values())
    tot_d = sum(v["deleted_words"] for v in g["per_file"].values())
    print(f"  GROSS  +{tot_a}w  -{tot_d}w   net {tot_a - tot_d:+d}w")
    print("  #304 published: -172 gross deleted, +4 (a NET figure for the retarget hunk), corpus -168")
    print(f"  net agreement: {'YES' if tot_a - tot_d == -168 else 'NO'}")
    for b_ in BINS:
        print(f"  bin {b_:<22s} +{g['per_bin'][b_]['added_words']}w -{g['per_bin'][b_]['deleted_words']}w")
    return 0


def cmd_role_lineage() -> int:
    """Enumerate every role birth and death so ROLE_LINEAGE can be audited, not trusted."""
    blobs = BlobCache()
    try:
        revs = [c for c in git("rev-list", "--reverse", "HEAD", "--", "skills/").split() if c]
        prev: list[str] = []
        births = deaths = 0
        for c in revs:
            cur = roles_at(ls_tree(c))
            ent, left = sorted(set(cur) - set(prev)), sorted(set(prev) - set(cur))
            if ent or left:
                print(f"{c[:7]} {git('log','-1','--format=%ad','--date=short',c).strip()} "
                      f"+{ent} -{left}")
            births += len(ent)
            deaths += len(left)
            prev = cur
        print(f"TOTAL births={births} deaths={deaths} over {len(revs)} commits; "
              f"final role count={len(prev)}  (births-deaths={births - deaths})")
        print()
        print("HAND-AUTHORED ROLE_LINEAGE (judgement, NOT measurement) — audit it against")
        print("the enumeration above rather than trusting it:")
        for e in ROLE_LINEAGE:
            print(f"  {e['kind']:<20s} {e['from']} -> {e['to']}  @{e['evidence']}")
            print(f"    {e['note']}")
    finally:
        blobs.close()
    return 0


# ------------------------------------------------------------------ --verify


HEADLINE_RE = re.compile(r"^\s*([a-z0-9_]+@[^\s=]+)\s*=\s*(-?\d+)\s*$")
HEADLINE_BLOCK = re.compile(r"```headline-figures\n(.*?)```", re.S)


def census_aggregates(data: dict) -> dict[str, int]:
    """Whole-census aggregates.  These are computed from `data`, and `--verify` passes it
    the FRESHLY RE-DERIVED census (never the committed file), so every figure here is
    git-derived exactly like the per-revision ones."""
    import statistics

    rows = data["rows"]
    ivs = [r["interval"] for r in rows if r.get("interval")]
    agg: dict[str, int] = {
        "rows": len(rows),
        "intervals": len(ivs),
        "deletion_events": len(data["deletion_events"]),
        "narrow_words_first": rows[0]["levels"][NARROW]["words"],
        "narrow_words_last": rows[-1]["levels"][NARROW]["words"],
        "role_count_first": rows[0]["role_count"],
        "role_count_last": rows[-1]["role_count"],
        "role_births": sum(len(iv["roles_entered"]) for iv in ivs),
        "role_deaths": sum(len(iv["roles_left"]) for iv in ivs),
        "role_deaths_walk_order_artifact": sum(
            1 for iv in ivs for v in iv["roles_left_classification"].values()
            if v == "walk-order-artifact"),
    }
    slug = {NARROW: "narrow", WIDE_EXTRA: "wide_extra", COND: "conditional"}
    for b, s in slug.items():
        agg[f"gross_added_words_{s}"] = sum(iv["gross"][b]["added_words"] for iv in ivs)
        agg[f"gross_deleted_words_{s}"] = sum(iv["gross"][b]["deleted_words"] for iv in ivs)
        agg[f"deletion_pressure_words_{s}"] = sum(
            iv["gross"][b]["deleted_words"] - iv["deleted_role_departure"][b]["deleted_words"]
            for iv in ivs)

    # "Routine edit churn" is not asserted — it is MEASURED, as the distribution of
    # per-interval NARROW movement over the intervals in which NARROW moved at all.
    moving = [abs(iv["net"][NARROW]["words"]) for iv in ivs if iv["net"][NARROW]["words"]]
    agg["narrow_moving_intervals"] = len(moving)
    agg["narrow_movement_median_words"] = int(statistics.median(moving))
    agg["narrow_movement_p75_words"] = int(statistics.quantiles(moving, n=4)[2])
    agg["narrow_movement_p25_words"] = int(statistics.quantiles(moving, n=4)[0])
    agg["narrow_movement_max_words"] = max(moving)

    base, head = rev(BASELINE_TAG), data["revisions"]["head"]
    w = window_rows(rows, base, head, [])
    win = abs(w["delta"]["narrow_concatenated_words"])
    agg["intervals_moving_narrow_at_least_as_much_as_the_window"] = sum(
        1 for x in moving if x >= win)
    return agg


def derive_headline(key: str, data: dict) -> int:
    """Re-derive ONE headline figure FROM GIT.  Never from the doc, never from the
    dataset.  A key this function cannot derive is a hard failure — that is what stops
    --verify degenerating into a keyword grep."""
    name, _, at = key.partition("@")
    blobs = shared_blobs()
    if True:
        if at == "census":
            agg = census_aggregates(data)
            if name not in agg:
                raise KeyError(f"unknown census headline key: {name}")
            return agg[name]

        if at == "panel":
            pan = build_panel()
            table = {
                "panel_revisions": len(pan["revisions"]),
                "panel_revisions_with_unit_reversal":
                    pan["h3_unit_dependence"]["revisions_where_argmax_lines_differs_from_argmax_bytes"],
                "panel_revisions_with_bundled_component_undefined":
                    sum(1 for e in pan["revisions"] if e["bundled_resolutions"] is None),
            }
            if name not in table:
                raise KeyError(f"unknown panel headline key: {name}")
            return table[name]

        if at == "window":
            base, head = rev(BASELINE_TAG), data["revisions"]["head"]
            w = window_rows(data["rows"], base, head, [])
            table = {
                "n_including_squash_merge": w["n_including_squash_merge"],
                "n_excluding_squash_merge": w["n_excluding_squash_merge"],
                "narrow_delta_words": w["delta"]["narrow_concatenated_words"],
                "corpus_delta_words": w["delta"]["corpus_words_concatenated"],
                "gross_added_words": sum(w["gross"][b]["added_words"] for b in BINS),
                "gross_deleted_words": sum(w["gross"][b]["deleted_words"] for b in BINS),
                "gross_deleted_words_narrow": w["gross"][NARROW]["deleted_words"],
                "gross_deleted_words_wide_extra": w["gross"][WIDE_EXTRA]["deleted_words"],
                "gross_deleted_words_conditional": w["gross"][COND]["deleted_words"],
                "deletion_events": w["deletion_event_count"],
            }
            if name not in table:
                raise KeyError(f"unknown window headline key: {name}")
            return table[name]

        r = rev(at)
        snap = snapshot(r, blobs)
        table = {
            "corpus_files": snap["corpus"]["files"],
            "corpus_words": snap["corpus"]["words_concatenated"],
            "narrow_files": snap["bins"][NARROW]["files"],
            "narrow_words": snap["narrow_concatenated_words"],
            "wide_extra_files": snap["bins"][WIDE_EXTRA]["files"],
            "wide_extra_words": snap["bins"][WIDE_EXTRA]["words"],
            "conditional_files": snap["bins"][COND]["files"],
            "conditional_words": snap["bins"][COND]["words"],
            "role_count": snap["role_count"],
            "unresolved_ref_tokens": snap["unresolved_ref_token_count"],
        }
        ranks = unit_ranks(snap)
        for role in ranks["rank_by_lines"]:
            table[f"rank_by_lines_of_{role.replace('-', '_')}"] = ranks["rank_by_lines"][role]
            table[f"rank_by_bytes_of_{role.replace('-', '_')}"] = ranks["rank_by_bytes"][role]
        if name not in table:
            raise KeyError(f"unknown headline key: {name}")
        return table[name]


REQUIRED_HEADLINES = {
    # at the declared baseline
    f"corpus_files@{BASELINE_TAG}", f"corpus_words@{BASELINE_TAG}",
    f"narrow_files@{BASELINE_TAG}", f"narrow_words@{BASELINE_TAG}",
    f"wide_extra_files@{BASELINE_TAG}", f"wide_extra_words@{BASELINE_TAG}",
    f"conditional_words@{BASELINE_TAG}", f"role_count@{BASELINE_TAG}",
    # at #304's squash-merge — the zero-delta claim must be checkable
    f"corpus_words@{MERGED_304}", f"narrow_words@{MERGED_304}",
    f"corpus_files@{MERGED_304}",
    # at the measurement endpoint
    "corpus_files@HEAD", "corpus_words@HEAD", "narrow_files@HEAD", "narrow_words@HEAD",
    "wide_extra_files@HEAD", "wide_extra_words@HEAD", "conditional_words@HEAD",
    "role_count@HEAD", "unresolved_ref_tokens@HEAD",
    # H3: the rank reversal, in integers so it cannot be waffled
    "rank_by_lines_of_docent@HEAD", "rank_by_bytes_of_docent@HEAD",
    "rank_by_lines_of_admiral@HEAD", "rank_by_bytes_of_admiral@HEAD",
    # the window
    "n_including_squash_merge@window", "n_excluding_squash_merge@window",
    "narrow_delta_words@window", "corpus_delta_words@window",
    "gross_added_words@window", "gross_deleted_words@window",
    "gross_deleted_words_narrow@window", "gross_deleted_words_wide_extra@window",
    "gross_deleted_words_conditional@window", "deletion_events@window",
    # H1 across the whole census — the load-bearing hypothesis
    "gross_added_words_narrow@census", "gross_deleted_words_narrow@census",
    "gross_added_words_wide_extra@census", "gross_deleted_words_wide_extra@census",
    "gross_added_words_conditional@census", "gross_deleted_words_conditional@census",
    "deletion_pressure_words_narrow@census", "deletion_pressure_words_wide_extra@census",
    "deletion_pressure_words_conditional@census",
    # H2 and the org-change split
    "narrow_words_first@census", "narrow_words_last@census",
    "role_count_first@census", "role_count_last@census",
    "role_births@census", "role_deaths@census",
    "role_deaths_walk_order_artifact@census",
    # computability: routine edit churn, measured not asserted
    "rows@census", "intervals@census", "deletion_events@census",
    "narrow_moving_intervals@census", "narrow_movement_p25_words@census",
    "narrow_movement_median_words@census", "narrow_movement_p75_words@census",
    "narrow_movement_max_words@census",
    "intervals_moving_narrow_at_least_as_much_as_the_window@census",
    # panel
    "panel_revisions@panel", "panel_revisions_with_unit_reversal@panel",
    "panel_revisions_with_bundled_component_undefined@panel",
}

BANNED_BARE = re.compile(r"(?<![-A-Z])\balways-loaded\b", re.I)


def cmd_verify(data_path: Path, doc_path: Path) -> int:
    fails: list[str] = []

    if not data_path.is_file():
        print(f"FAIL dataset missing: {data_path}")
        return 1
    if not doc_path.is_file():
        print(f"FAIL doc missing: {doc_path}")
        return 1

    data = json.loads(data_path.read_text(encoding="utf-8"))
    doc = doc_path.read_text(encoding="utf-8")

    # 1. BLOCKING baseline reproduction, re-derived from git right now.
    print("[1/5] blocking baseline reproduction")
    if cmd_reproduce_baseline(BASELINE_TAG) != 0:
        fails.append("baseline reproduction FAILED -> the series is VOID")

    # 2. The committed dataset must itself re-derive from git.
    print("[2/5] dataset re-derivation from git")
    fresh = census(data["revisions"]["head"])
    a = json.dumps(fresh, indent=2, sort_keys=True)
    b = json.dumps(data, indent=2, sort_keys=True)
    if a != b:
        fails.append("committed trends.json does not re-derive from git (dataset drift)")
        for k in sorted(set(fresh) | set(data)):
            if fresh.get(k) != data.get(k):
                fails.append(f"  dataset section differs: {k}")
    else:
        print("      dataset re-derives byte-identically")

    # 3. Internal arithmetic of the dataset (the published recombination must hold).
    print("[3/5] recombination arithmetic")
    for row in data["rows"]:
        lv = row["levels"]
        tot = sum(lv[bn]["files"] for bn in BINS)
        if tot != row["corpus_files"]:
            fails.append(f"  row {row['short']}: bins are not a partition "
                         f"({tot} != {row['corpus_files']})")
    if not fails or all("partition" not in f for f in fails):
        print("      NARROW + WIDE-EXTRA + CONDITIONAL == corpus, every row")

    # 4. Every headline figure quoted in the DOC, re-derived from git.
    #    NOT a keyword grep: the required key set must be present EXACTLY, and each
    #    value is recomputed from git independently of both doc and dataset.
    print("[4/5] doc headline reconciliation")
    m = HEADLINE_BLOCK.search(doc)
    if not m:
        fails.append("doc has no ```headline-figures``` block")
    else:
        found: dict[str, int] = {}
        for line in m.group(1).split("\n"):
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            hm = HEADLINE_RE.match(line)
            if not hm:
                fails.append(f"  unparseable headline line: {line!r}")
                continue
            found[hm.group(1)] = int(hm.group(2))
        missing = REQUIRED_HEADLINES - set(found)
        extra = set(found) - REQUIRED_HEADLINES
        if missing:
            fails.append(f"  doc is missing {len(missing)} required headline figures: "
                         f"{sorted(missing)}")
        if extra:
            fails.append(f"  doc declares unknown headline figures: {sorted(extra)}")
        for k in sorted(set(found) & REQUIRED_HEADLINES):
            try:
                want = derive_headline(k, fresh)
            except Exception as e:  # noqa: BLE001
                fails.append(f"  cannot re-derive {k}: {e}")
                continue
            if found[k] != want:
                fails.append(f"  doc says {k} = {found[k]}, git says {want}")
        print(f"      {len(set(found) & REQUIRED_HEADLINES)}/{len(REQUIRED_HEADLINES)} "
              f"headline figures re-derived from git")

    # 5. The banned bare term, and the substance the doc must carry.
    print("[5/5] terminology + required substance")
    for i, line in enumerate(doc.split("\n"), 1):
        if BANNED_BARE.search(line) and "BANNED" not in line and "bare term" not in line:
            fails.append(f"  doc line {i} uses the BANNED bare term 'always-loaded': {line.strip()[:90]}")
    for needed in ("NARROW-ALWAYS-LOADED", "WIDE-ALWAYS-LOADED", "CONDITIONALLY-LOADED"):
        if needed not in doc:
            fails.append(f"  doc never mentions the {needed} bin")

    print()
    if fails:
        print(f"VERIFY FAILED ({len(fails)} problems)")
        for f in fails:
            print("  " + f)
        return 1
    print("VERIFY OK -- every figure re-derived from git and reconciled against "
          "both the dataset and the doc")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--reproduce-baseline", action="store_true")
    p.add_argument("--at", default=BASELINE_TAG, help="rev/tag for --reproduce-baseline")
    p.add_argument("--calibrate-gross", action="store_true")
    p.add_argument("--role-lineage", action="store_true")
    p.add_argument("--snapshot", default=None, metavar="REV")
    p.add_argument("--census", action="store_true")
    p.add_argument("--panel", action="store_true")
    p.add_argument("--head", default="HEAD")
    p.add_argument("--out", default=None)
    p.add_argument("--verify", action="store_true")
    p.add_argument("--data", default=None)
    p.add_argument("--doc", default=None)
    a = p.parse_args()

    if a.reproduce_baseline:
        return cmd_reproduce_baseline(a.at)
    if a.calibrate_gross:
        return cmd_calibrate_gross()
    if a.role_lineage:
        return cmd_role_lineage()
    if a.snapshot:
        blobs = BlobCache()
        try:
            print(json.dumps(snapshot(rev(a.snapshot), blobs), indent=2, sort_keys=True))
        finally:
            blobs.close()
        return 0
    if a.census:
        c = census(a.head)
        if a.out:
            dump(c, Path(a.out))
            print(f"wrote {a.out}")
        else:
            print(json.dumps(c, indent=2, sort_keys=True))
        return 0 if c["baseline_oracle"]["reproduced"] else 1
    if a.panel:
        pan = build_panel()
        if a.out:
            dump(pan, Path(a.out))
            print(f"wrote {a.out}")
        else:
            print(json.dumps(pan, indent=2, sort_keys=True))
        return 0
    if a.verify:
        if not a.data or not a.doc:
            p.error("--verify requires --data and --doc")
        return cmd_verify(Path(a.data), Path(a.doc))
    p.error("no mode selected")
    return 2


if __name__ == "__main__":
    sys.exit(main())
