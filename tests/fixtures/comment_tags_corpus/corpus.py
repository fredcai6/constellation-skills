"""Fixture corpus for gate g7's comment-tag negative tests (issue #456).

Committed here rather than built inline, per the handoff's fixture-directory
precedent (tests/fixtures/overread_corpus/). Every shape below is read by
tests/test_code_map.py's CommentTagNegativeTests, each negative case paired
with a positive-control sibling in the SAME test method that DOES extract --
so a broken extractor (one that extracts nothing at all) cannot pass by
accident.
"""

DOUBLE = 2


# Rationale: this value is doubled at read time, not at write time -- the
# positive control every negative assertion in this file is paired against.
def scaled():
    """Doubles DOUBLE."""
    return DOUBLE * 2


def plain_note():
    """A negative control: an ordinary comment must not extract as a tag."""
    # Note: this is just a comment, not a tag -- must NOT extract. Sits
    # directly above an assignment (a real tag_check call site), so a
    # regex-only break of the keyword list is what this test actually
    # exercises.
    value = 1
    return value


def retired_words():
    """A negative control: Assumption:/Constraint: are retired keywords post
    cull-test collapse (see .agent-work/issue-456/cull-verdict.json) -- must
    NOT extract as tags."""
    # Assumption: this used to be a valid tag keyword before the cull test
    # collapsed it into Rationale:.
    value = 1
    # Constraint: same story -- this word is retired too.
    other = 2
    return value + other
