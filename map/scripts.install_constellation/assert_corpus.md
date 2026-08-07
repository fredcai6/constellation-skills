# scripts.install_constellation:assert_corpus
function, scripts/install_constellation.py:1064, 4 lines

```python
def assert_corpus(run_skills_dir, expected_id: str) -> bool
```

Whether a copied skill tree hashes to ``expected_id`` (whole-tree). A

mismatch fences an eval run (corpus_mismatch), never silently counts.

calls internal: compute_corpus_id

referenced by: none found
