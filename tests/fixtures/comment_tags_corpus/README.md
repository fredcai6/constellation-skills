# comment_tags_corpus — SYNTHETIC fixture source (gate g7, issue #456)

**`corpus.py` is hand-built and synthetic.** `C:\Programs\f1Brainz` holds the
only *real* comment-tag corpus (PR #733, six tags) but is READ-ONLY for this
gate — it may be read to shape the grammar, never copied into this repo's own
test suite. This fixture exists so the negative-extraction tests have a
committed, reviewable source file to run against, rather than an inline
string buried in `tests/test_code_map.py` (precedent: `tests/fixtures/
overread_corpus/`, and the `--fixture-directory` pattern named in the g7
handoff).

`corpus.py` is copied verbatim into an ephemeral git repo at test time (the
extractor's corpus discovery requires `git ls-files`, so a bare static read
cannot exercise the real pipeline) by `CommentTagNegativeTests` in
`tests/test_code_map.py`.

## Shape

| function | what it tests |
|---|---|
| `scaled()` | POSITIVE CONTROL — a whole-function `Rationale:` tag that MUST extract. Every negative assertion in the same test method is paired against this, so a fully-broken extractor (one that extracts nothing at all) cannot pass by accident. |
| `plain_note()` | an ordinary `# Note: ...` comment — MUST NOT extract as a tag. |
| `retired_words()` | `Assumption:`/`Constraint:` comments — valid in grammar v0, retired by gate g7's cull test (see `.agent-work/issue-456/cull-verdict.json`, verdict: collapse). MUST NOT extract post-collapse. |

Every "must not extract" assertion here was verified by *breaking* the
extractor (temporarily widening `TAG_START` to accept the retired words, or
broadening it to match any comment) and confirming the specific assertion
goes red — see `g7-implement-RESULT.md` for the count.
