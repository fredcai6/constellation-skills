# scripts.curate_corpus:check_description
function, scripts/curate_corpus.py:239, 39 lines

```python
def check_description(skill: str, meta: dict[str, str]) -> list[Finding]
```

Mechanical description lint: length, person-pronoun shortlist, when-to-use

marker presence, and (confusable-pairs only) exclusion-clause presence.

calls internal: Finding x6, _exclusion_present, _person_tokens
calls stdlib: builtins.len x2, builtins.any
reads internal: STATUS_FLAGGED x4, DESCRIPTION_MAX_CHARS x2, DESCRIPTION_MAX_WORDS x2, CONFUSABLE_SKILLS, Finding, STATUS_INFO, STATUS_SHORTLIST, WHEN_TO_USE_MARKERS
reads stdlib: builtins.list
unresolved: 10 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
