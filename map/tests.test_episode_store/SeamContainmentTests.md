# tests.test_episode_store:SeamContainmentTests
class, tests/test_episode_store.py:2644, 144 lines

```python
class SeamContainmentTests(QueryTestCase)
```

C2 — the ratified layout is bound at the seam set and NOWHERE else.

Pre-g4 this class read "the layout is held open, so nothing may bind it". The
decision is now bound, and the identical assertions carry a different but equally
load-bearing obligation: the binding lives in exactly ONE place. A retrieval call
site that inlines `episodes/active/...`, or greps for a `status: retired` line,
re-scatters the layout across the codebase — and it is precisely that inlining that
would have turned "bind the layout at g4" into a retrieval rewrite instead of a
four-adapter swap. The proof that it did not is that these bans still hold with the
decision bound and retirement-dependent retrieval shipped.

- [test_query_module_inlines_no_status_check_and_no_directory_check](SeamContainmentTests.test_query_module_inlines_no_status_check_and_no_directory_check.md) method: HOLE: no docstring
- [test_retrieval_reaches_the_layout_only_through_the_seams](SeamContainmentTests.test_retrieval_reaches_the_layout_only_through_the_seams.md) method: The direct proof that the binding is contained: move the layout by replacing
- [test_the_writer_names_the_directories_only_inside_the_seam_block](SeamContainmentTests.test_the_writer_names_the_directories_only_inside_the_seam_block.md) method: C2's other half. query_episodes.py may not name the directories at all; the
- [test_the_membership_seam_answers_for_both_sets](SeamContainmentTests.test_the_membership_seam_answers_for_both_sets.md) method: HOLE: no docstring

referenced by: none found
