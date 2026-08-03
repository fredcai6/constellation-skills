"""Fixture tests for the issue-310 surface census instrument.

Two kinds of test, deliberately:

1. **Pinned-truth tests** against IMMUTABLE tagged revisions (`baseline/304-*`).  Those
   revisions cannot move, so exact numbers are legitimate assertions here rather than
   change-detectors.
2. **Adversarial/structural tests** that make the instrument return a WRONG answer on
   purpose (a synthetic installer source, a bundle that resolves nothing) — because a
   round-trip over the real corpus proves the corpus is clean, not that the tool is
   correct.

Run: `python -m pytest .agent-work/issue-310/trends/test_measure_surface.py -q`
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))
import measure_surface as m  # noqa: E402

BASE = m.BASELINE_TAG
G2 = m.G2_TAG


@pytest.fixture(scope="module")
def blobs():
    b = m.BlobCache()
    yield b
    b.close()


@pytest.fixture(scope="module")
def base_rev():
    return m.rev(BASE)


@pytest.fixture(scope="module")
def head_rev():
    return m.rev("HEAD")


# ----------------------------------------------------------- pinned tagged truth


def test_tags_resolve_to_the_expected_commits():
    """Addressed BY TAG, never bare sha — but the sha is asserted so a moved tag is loud."""
    for tag, want in m.EXPECTED_TAG_SHA.items():
        assert m.rev(tag).startswith(want), f"{tag} moved"


def test_tagged_baselines_are_not_ancestors_of_head(base_rev, head_rev):
    """#304 squash-merged, so a rev-list walk NEVER visits the baseline.  If this ever
    becomes True the census must stop unioning them in explicitly."""
    import subprocess
    rc = subprocess.run(
        ["git", "-C", str(m.REPO), "merge-base", "--is-ancestor", base_rev, head_rev]
    ).returncode
    assert rc != 0, "baseline is now an ancestor of HEAD; the union logic is stale"
    walk = m.git("rev-list", "HEAD", "--", "skills/").split()
    assert base_rev not in walk
    assert m.rev(G2) not in walk


def test_blocking_baseline_oracle_reproduces(blobs, base_rev):
    """TREND_SNAPSHOT sec.1 at the tag: 19 / 15,831 / 100 / 63,681.  If this fails the
    whole series is VOID."""
    assert m.oracle_measure(m.snapshot(base_rev, blobs)) == m.BASELINE_ORACLE


def test_oracle_fails_on_a_decoy_revision(blobs):
    """The oracle must be able to FAIL.  A check that cannot fail is indistinguishable
    from one that passed."""
    assert m.oracle_measure(m.snapshot(m.rev(G2), blobs)) != m.BASELINE_ORACLE


def test_concatenation_vs_per_file_sum_is_explained(blobs, base_rev):
    """The published 63,681 is a CONCATENATED count; the per-file sum is 63,682 because
    exactly one file lacks a trailing newline."""
    snap = m.snapshot(base_rev, blobs)
    tree = m.ls_tree(base_rev)
    no_nl = [p for p, (o, _s) in sorted(tree.items()) if not blobs.get(o).endswith(b"\n")]
    assert len(no_nl) == 1, no_nl
    assert no_nl == ["skills/commander/templates/COMMANDER_SPINE.template.json"]
    assert snap["corpus"]["words_per_file_sum"] - snap["corpus"]["words_concatenated"] == 1


# --------------------------------------------------------------- 19 roles, not 20


@pytest.mark.parametrize("spec", [BASE, "HEAD"])
def test_nineteen_roles_and_shared_is_not_one(spec):
    """`_shared` is NOT a skill (install_constellation.py skips names starting '_').
    TREND_SNAPSHOT sec.2 lists it as a 20th role — a defect, filed as #411."""
    roles = m.roles_at(m.ls_tree(m.rev(spec)))
    assert len(roles) == 19, roles
    assert "_shared" not in roles
    assert len(set(roles)) == len(roles)


def test_role_count_is_asserted_from_a_command_not_a_constant():
    """The count comes from the tree, so a real corpus change moves it (not a literal)."""
    early = m.roles_at(m.ls_tree(m.rev("84fd28f")))
    assert len(early) == 11, early  # the corpus genuinely had 11 roles at the boundary


# ----------------------------------------------------- three bins, exact partition


@pytest.mark.parametrize("spec", [BASE, G2, "84fd28f", "84fd28f^", "HEAD"])
def test_bins_are_an_exact_partition_of_the_tracked_corpus(blobs, spec):
    r = m.rev(spec)
    tree = m.ls_tree(r)
    cls = m.classify(tree, r, blobs)
    assert set(cls["bins"]) == set(tree)
    assert set(cls["bins"].values()) <= set(m.BINS)
    counts = {b: sum(1 for v in cls["bins"].values() if v == b) for b in m.BINS}
    assert sum(counts.values()) == len(tree)
    # NARROW and WIDE-EXTRA are DISJOINT; WIDE = NARROW + WIDE-EXTRA, never a sum of
    # NARROW and WIDE.
    narrow = {p for p, v in cls["bins"].items() if v == m.NARROW}
    extra = {p for p, v in cls["bins"].items() if v == m.WIDE_EXTRA}
    assert not (narrow & extra)
    assert len(narrow | extra) == len(narrow) + len(extra)


def test_snapshot_bins_sum_to_the_corpus(blobs, head_rev):
    s = m.snapshot(head_rev, blobs)
    assert sum(v["files"] for v in s["bins"].values()) == s["corpus"]["files"]
    assert sum(v["words"] for v in s["bins"].values()) == s["corpus"]["words_per_file_sum"]
    assert sum(v["bytes"] for v in s["bins"].values()) == s["corpus"]["bytes"]


def test_narrow_bin_is_exactly_the_skill_md_set(blobs, base_rev):
    tree = m.ls_tree(base_rev)
    cls = m.classify(tree, base_rev, blobs)
    narrow = sorted(p for p, v in cls["bins"].items() if v == m.NARROW)
    assert len(narrow) == 19
    assert all(p.endswith("/SKILL.md") and p.count("/") == 2 for p in narrow)


# --------------------------------------------------- the regime boundary is REAL


def test_regime_boundary_verified_not_trusted(blobs):
    """The candidate 84fd28f was given as a candidate, not as truth.  Verify it: it must
    be the FIRST commit carrying SKILL_REFERENCE_BUNDLES, and its parent must carry none."""
    first = m.git("log", "--reverse", "--format=%H", "-S", "SKILL_REFERENCE_BUNDLES",
                  "--", "scripts/install_constellation.py").split()[0]
    assert first.startswith("84fd28f")
    assert m.bundles_at(m.rev("84fd28f^"), blobs) is None
    assert m.bundles_at(m.rev("84fd28f"), blobs) is not None


def test_pre_regime_bundled_component_is_null_never_zero(blobs):
    """Undefined is not zero.  Before the boundary, `bundled` must be None, and it must
    NOT be an empty list — an empty list would read as 'measured, and it was nothing'."""
    s = m.snapshot(m.rev("84fd28f^"), blobs)
    assert s["bundles_defined"] is False
    bundled = [r["refs"]["bundled"] for r in s["per_role"].values()]
    assert bundled and all(b is None for b in bundled)
    assert not any(b == [] for b in bundled)


def test_post_regime_bundled_component_is_a_list_not_null(blobs, head_rev):
    s = m.snapshot(head_rev, blobs)
    assert s["bundles_defined"] is True
    assert all(isinstance(r["refs"]["bundled"], list) for r in s["per_role"].values())


# -------------------------------------------- adversarial: make it answer WRONGLY


def test_parse_bundles_returns_none_when_the_mechanism_is_absent():
    assert m.parse_bundles("X = 1\n") is None


def test_parse_bundles_evaluates_name_and_concat_expressions():
    src = (
        '_GLOBAL_EVERYONE = ("a.md", "w.md")\n'
        '_GLOBAL_CREW = ("a.md", "c.md", "w.md")\n'
        'SKILL_REFERENCE_BUNDLES: dict[str, tuple[str, ...]] = {\n'
        '    "implementer": _GLOBAL_CREW,\n'
        '    "curator": _GLOBAL_EVERYONE + ("goodness.md",),\n'
        '    "literal": ("z.md",),\n'
        '}\n'
    )
    b = m.parse_bundles(src)
    assert b == {
        "implementer": ("a.md", "c.md", "w.md"),
        "curator": ("a.md", "w.md", "goodness.md"),
        "literal": ("z.md",),
    }


def test_parse_bundles_never_executes_the_source():
    """Historical installer source is PARSED, never executed — a side effect in it must
    not fire."""
    src = (
        'import pathlib\n'
        'pathlib.Path("SHOULD_NOT_EXIST_310").write_text("boom")\n'
        '_GLOBAL_EVERYONE = ("a.md",)\n'
        'SKILL_REFERENCE_BUNDLES = {"r": _GLOBAL_EVERYONE}\n'
    )
    assert m.parse_bundles(src) == {"r": ("a.md",)}
    assert not (m.REPO / "SHOULD_NOT_EXIST_310").exists()
    assert not Path("SHOULD_NOT_EXIST_310").exists()


def test_unresolved_tokens_are_counted_not_silently_dropped(blobs, head_rev):
    """A guard that loops must assert what it looped over.  The unresolved path must be
    EXERCISED by the real corpus, or it is dead code that reads as clean."""
    s = m.snapshot(head_rev, blobs)
    assert s["unresolved_ref_token_count"] > 0
    assert len(s["unresolved_ref_tokens"]) == s["unresolved_ref_token_count"]
    # every unresolved token is a CROSS-ROLE citation whose target IS already pulled
    # into WIDE by its owning role, so WIDE is not under-counted at corpus level
    assert s["unresolved_ref_tokens_uncovered_count"] == 0, s["unresolved_ref_tokens_uncovered"]


def test_shared_files_named_by_no_skill_md_land_in_conditional(blobs, head_rev):
    """A consequence of the Admiral's rule a reader may reject: the installer ships
    `_shared/windows.md` into every role, but no SKILL.md NAMES it as
    `references/windows.md`, so the rule puts it in CONDITIONALLY-LOADED."""
    r = head_rev
    cls = m.classify(m.ls_tree(r), r, blobs)
    assert "skills/_shared/windows.md" in cls["shared_files_not_named"]
    assert cls["bins"]["skills/_shared/windows.md"] == m.COND
    assert cls["bins"]["skills/_shared/global-everyone.md"] == m.WIDE_EXTRA


# ------------------------------------- gross, calibrated against #304's own event


def test_gross_is_calibrated_against_the_published_304_deletion_event(blobs):
    """#304 published this event with exact arithmetic: 172 gross words deleted, +4, net
    -168.  This instrument measures gross 5 in / 173 out, net -168 — the NET agrees
    exactly.  The +1/-1 is #304's own mixed bookkeeping (its '+4' is a NET figure for the
    retarget hunk), not instrument error."""
    a, b = m.rev(G2), m.rev(BASE)
    cls = m.classify(m.ls_tree(b), b, blobs)
    g = m.gross(a, b, cls["bins"])
    added = sum(v["added_words"] for v in g["per_file"].values())
    deleted = sum(v["deleted_words"] for v in g["per_file"].values())
    assert (added, deleted) == (5, 173)
    assert added - deleted == -168, "net must reproduce the published corpus delta exactly"


def test_the_304_deletion_landed_entirely_in_the_conditional_bin(blobs):
    """H1's single documented data point.  Both deleted files are under templates/."""
    a, b = m.rev(G2), m.rev(BASE)
    cls = m.classify(m.ls_tree(b), b, blobs)
    g = m.gross(a, b, cls["bins"])
    assert sorted(g["per_file"]) == [
        "skills/commander/templates/COMMANDER_SPINE.template.json",
        "skills/commander/templates/EXECUTE_PLAN.template.json",
    ]
    assert g["per_bin"][m.COND]["deleted_words"] == 173
    assert g["per_bin"][m.NARROW]["deleted_words"] == 0
    assert g["per_bin"][m.WIDE_EXTRA]["deleted_words"] == 0


def test_gross_is_emitted_separately_from_net_never_only_net(blobs):
    """A net-only row is a defect.  Every gross dict must carry both directions."""
    a, b = m.rev(G2), m.rev(BASE)
    cls = m.classify(m.ls_tree(b), b, blobs)
    g = m.gross(a, b, cls["bins"])
    for bin_ in m.BINS:
        for k in ("added_words", "deleted_words", "added_bytes", "deleted_bytes",
                  "added_lines", "deleted_lines"):
            assert k in g["per_bin"][bin_]


def test_gross_detects_growth_that_a_net_row_would_hide(blobs):
    """The point of gross: an interval whose NET is small can still carry large gross
    churn.  Find one in the real history and assert the instrument sees it."""
    a, b = m.rev(G2), m.rev(BASE)
    cls = m.classify(m.ls_tree(b), b, blobs)
    g = m.gross(a, b, cls["bins"])
    net = g["per_bin"][m.COND]["added_words"] - g["per_bin"][m.COND]["deleted_words"]
    gross_total = g["per_bin"][m.COND]["added_words"] + g["per_bin"][m.COND]["deleted_words"]
    assert gross_total > abs(net), "gross must exceed |net| where both directions moved"


# ---------------------------------------------------------------- determinism


def test_snapshot_is_deterministic(blobs, head_rev):
    import json
    a = json.dumps(m.snapshot(head_rev, blobs), sort_keys=True)
    b2 = m.BlobCache()
    try:
        b = json.dumps(m.snapshot(head_rev, b2), sort_keys=True)
    finally:
        b2.close()
    assert a == b


def test_snapshot_carries_no_wall_clock_field(blobs, head_rev):
    """Determinism is only achievable because nothing in the output is time-derived."""
    import json
    blob = json.dumps(m.snapshot(head_rev, blobs))
    for banned in ("taken_at", "generated_at", "timestamp", "now"):
        assert banned not in blob


# ------------------------------------ hand-authored lineage must match the census


def test_role_lineage_table_is_consistent_with_the_raw_enumeration():
    """ROLE_LINEAGE is HAND-AUTHORED judgement.  It is not exempt from checking: every
    role it claims disappeared must actually disappear in the enumeration, and the
    births-minus-deaths arithmetic must land on today's 19 roles."""
    revs = [c for c in m.git("rev-list", "--reverse", "HEAD", "--", "skills/").split() if c]
    prev: list[str] = []
    births = deaths = 0
    died: set[str] = set()
    born: set[str] = set()
    for c in revs:
        cur = m.roles_at(m.ls_tree(c))
        ent, left = set(cur) - set(prev), set(prev) - set(cur)
        births += len(ent)
        deaths += len(left)
        born |= ent
        died |= left
        prev = cur
    assert len(revs) == 184, len(revs)
    assert (births, deaths) == (25, 6), (births, deaths)
    assert births - deaths == len(prev) == 19
    claimed = {r for e in m.ROLE_LINEAGE for r in e["from"]}
    assert claimed == died, f"lineage claims {sorted(claimed)}, git shows {sorted(died)}"
    # the three walk-order artifacts must reappear, i.e. they are also births
    assert m._ARTIFACT_DEATHS <= born


def test_walk_order_artifacts_are_not_real_deletions():
    """The three 'deaths' classified as walk-order artifacts must show NO role-directory
    deletion in their own first-parent diff — that is what makes them artifacts."""
    for c in ("75ca633", "2c84955"):
        out = m.git("diff", "--name-status", "-M", "--diff-filter=D", f"{c}^", c, "--", "skills/")
        for role in m._ARTIFACT_DEATHS:
            assert f"skills/{role}/SKILL.md" not in out, (c, role)
