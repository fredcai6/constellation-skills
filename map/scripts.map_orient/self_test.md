# scripts.map_orient:self_test
function, scripts/map_orient.py:1317, 324 lines

```python
def self_test() -> int
```

Falsification floor: assert the decision layer refuses what it must.

calls internal: _check x98, _cand x13, frame_verdict x12, verify_verdict x9, determine_mode x6, scan_anchors x6, substitutes_declared x6, classify_generated_map x5, build_orientation x4, degraded_record_is_complete x4, exit_code_for x4, is_source_path x4, prove_repo_root x4, unmapped_declared x4, build_receipt x3, candidate_outcome x3, classify_packets x3, classify_substitute x3, substitute_label x3, RootProof x2, candidate_is_citable x2, classify_markdown x2, is_content_hash x2, _read_text, cited_paths, render_frame_report, render_orient_report, render_verify_report
calls stdlib: builtins.dict x9, builtins.len x5, builtins.any x4, builtins.all x3, builtins.print x3, builtins.bool, builtins.set, hashlib.sha256, pathlib.Path
reads internal: EXIT_OK x14, INDEX_MD x11, RESERVED_FIRST_LINES x6, SEMANTIC_EXIT_CODES x5, EXIT_DEGRADED_UNDISCHARGED x4, EXIT_RECEIPT_UNUSABLE x4, LABEL_AGENT_DECLARED x4, MODE_DEGRADED_NO_MAP x4, EXIT_UNRESOLVABLE_ROOT x3, FRAME_MISSING x3, LABEL_KNOWN_FALLBACK x3, MODE_RESOLVED x3, FRAME_OK x2, MODE_UNRESOLVABLE_ROOT x2, EXIT_SELF_TEST_FAILED, FRAME_REFUSED, GENERATED_MAP, MODE_DEGRADED_EMPTY_MAP, MODE_DEGRADED_UNPARSEABLE, OCCUPIED_EXIT_CODES, ORIENT_MODES, OUTCOME_ABSENT, OUTCOME_EMPTY, OUTCOME_UNPARSEABLE
reads stdlib: sys (module) x2, sys.stderr x2, builtins.list, builtins.str, hashlib (module)
unresolved: 4 calls (dispatch-unknown-base), 10 reads (dispatch-unknown-base), 1 reads (unbound-name)

referenced by: 1 sites, this module only
