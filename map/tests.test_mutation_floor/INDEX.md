# tests.test_mutation_floor
tests/test_mutation_floor.py, 445 lines, 15 holes

EXECUTED falsifiability for scripts/map_orient.py.

Falsifiability is demonstrated by execution, never asserted by the party being
graded. Each named mutation is mechanically applied to a COPY of the module,
the whole floor (tests/test_map_orient.py) is re-run against that copy, and the
run must go RED.

LOAD-BEARING -- the reason this file exists at all
--------------------------------------------------
Every mutation asserts it APPLIED **before** it asserts red:

  * the original text occurred exactly once,
  * it occurs zero times afterwards,
  * and the replacement's occurrence count went UP by exactly one
    (a count delta, not `in`, so a replacement string that already appears
    elsewhere in the module cannot fake the assertion).

If a substitution does not land, this file fails LOUDLY as a HARNESS ERROR and
never reports a killed mutant. A mutation that silently fails to match produces
a green baseline that is *indistinguishable from a killed mutant* -- this epic
already lost a round to exactly that with a non-matching `sed`. Without the
applied-assertion the check that verifies falsifiability is itself
unfalsifiable. Prove you changed the thing, THEN compare.

The unmutated baseline is asserted GREEN first, so a red result is attributable
to the mutation rather than to the harness. Each kill must also name a test in
the class the mutation is supposed to break, and the run must still have
collected and passed other tests -- otherwise a mutation that merely broke the
import would count as a kill for the wrong reason.

imports stdlib: dataclasses.dataclass, dataclasses.field, os, pathlib.Path, re, shutil, subprocess, sys, tempfile, unittest
imported by: none found

```python
ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / 'scripts' / 'map_orient.py'
FLOOR = ROOT / 'tests' / 'test_map_orient.py'
ORIGINAL = MODULE.read_text(encoding='utf-8')
MUTATIONS = (Mutation(name='degraded-completeness `all` -> `any`', why='Under `any`, a degraded rec...
```

- [HarnessError](HarnessError.md) class: The mutation did not land. NOT a killed mutant -- a broken harness.
- [Mutation](Mutation.md) class: HOLE: no docstring
- [apply_mutation](apply_mutation.md) function: Apply every substitution, refusing loudly when one does not match.
- [run_floor](run_floor.md) function: Run the whole floor with the module under test pointed at `module_path`.
- [failed_nodes](failed_nodes.md) function: HOLE: no docstring
- [passed_count](passed_count.md) function: HOLE: no docstring
- [MutationFloor](MutationFloor.md) class: HOLE: no docstring
  - [MutationFloor._copy_module](MutationFloor._copy_module.md) method: HOLE: no docstring
  - [MutationFloor.test_0_unmutated_baseline_is_green](MutationFloor.test_0_unmutated_baseline_is_green.md) method: A red below must be attributable to the mutation, not to the harness.
  - [MutationFloor.test_1_mutation_all_to_any_is_killed](MutationFloor.test_1_mutation_all_to_any_is_killed.md) method: HOLE: no docstring
  - [MutationFloor.test_2_mutation_unresolvable_root_collapse_is_killed](MutationFloor.test_2_mutation_unresolvable_root_collapse_is_killed.md) method: HOLE: no docstring
  - [MutationFloor.test_3_mutation_existence_instead_of_citable_content_is_killed](MutationFloor.test_3_mutation_existence_instead_of_citable_content_is_killed.md) method: HOLE: no docstring
  - [MutationFloor.test_4_mutation_unmapped_not_any_to_not_all_is_killed](MutationFloor.test_4_mutation_unmapped_not_any_to_not_all_is_killed.md) method: Regression: this one SURVIVED the first shipped floor.
  - [MutationFloor.test_5_mutation_sentinel_accepted_as_a_hash_pin_is_killed](MutationFloor.test_5_mutation_sentinel_accepted_as_a_hash_pin_is_killed.md) method: Regression: the B1 blocker, pinned so it cannot come back.
  - [MutationFloor.test_6_mutation_absent_frame_credited_as_a_pass_is_killed](MutationFloor.test_6_mutation_absent_frame_credited_as_a_pass_is_killed.md) method: THE vacuous pass -- the one mutation this gate exists to pin.
  - [MutationFloor.test_7_mutation_undeclared_substitute_refusal_disabled_is_killed](MutationFloor.test_7_mutation_undeclared_substitute_refusal_disabled_is_killed.md) method: HOLE: no docstring
  - [MutationFloor.test_8_mutation_known_fallback_label_on_membership_alone_is_killed](MutationFloor.test_8_mutation_known_fallback_label_on_membership_alone_is_killed.md) method: HOLE: no docstring
  - [MutationFloor.test_9_mutation_every_substitute_reported_as_verified_is_killed](MutationFloor.test_9_mutation_every_substitute_reported_as_verified_is_killed.md) method: g2 review BLOCK regression: the label must stay READ, not just written.
  - [MutationFloor.test_10_mutation_provenance_line_dropped_is_killed](MutationFloor.test_10_mutation_provenance_line_dropped_is_killed.md) method: HOLE: no docstring
  - [MutationFloor._assert_mutation_is_killed](MutationFloor._assert_mutation_is_killed.md) method: HOLE: no docstring
- [HarnessSelfCheck](HarnessSelfCheck.md) class: The harness's own failure mode must be loud, not silent.
  - [HarnessSelfCheck.test_a_non_matching_substitution_raises_a_harness_error](HarnessSelfCheck.test_a_non_matching_substitution_raises_a_harness_error.md) method: HOLE: no docstring
  - [HarnessSelfCheck.test_an_ambiguous_anchor_raises_a_harness_error](HarnessSelfCheck.test_an_ambiguous_anchor_raises_a_harness_error.md) method: HOLE: no docstring
  - [HarnessSelfCheck.test_every_named_mutation_has_a_unique_anchor_in_the_shipped_module](HarnessSelfCheck.test_every_named_mutation_has_a_unique_anchor_in_the_shipped_module.md) method: HOLE: no docstring
