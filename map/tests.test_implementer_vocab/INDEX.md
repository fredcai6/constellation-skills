# tests.test_implementer_vocab
tests/test_implementer_vocab.py, 56 lines, 7 holes

Light vocabulary assertion for the constellation-implementer sharpening

(DESIGN_SPEC Section D2 — vertical-slice vocabulary).

D2 is a *vocabulary* delta with NO machinery behind it (SF3/TF8): the implementer
should frame its plan chunks as vertical slices — a bite-sized, end-to-end sliver
of observable behavior — rather than horizontal layers. There is nothing to
execute, so quality is the independent reviewer's judgment; this test only pins
the vocabulary into the skill doctrine so a future edit can't silently drop it.
It is deliberately light (a doc assertion), matching the design's "no machinery".

imports stdlib: pathlib.Path, re, unittest
imported by: none found

```python
ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills' / 'implementer' / 'SKILL.md'
```

- [VerticalSliceVocabTests](VerticalSliceVocabTests.md) class: HOLE: no docstring
  - [VerticalSliceVocabTests.setUp](VerticalSliceVocabTests.setUp.md) method: HOLE: no docstring
  - [VerticalSliceVocabTests.test_skill_present](VerticalSliceVocabTests.test_skill_present.md) method: HOLE: no docstring
  - [VerticalSliceVocabTests.test_vertical_slice_vocabulary_present](VerticalSliceVocabTests.test_vertical_slice_vocabulary_present.md) method: HOLE: no docstring
  - [VerticalSliceVocabTests.test_slices_are_end_to_end_not_layers](VerticalSliceVocabTests.test_slices_are_end_to_end_not_layers.md) method: HOLE: no docstring
  - [VerticalSliceVocabTests.test_chunks_are_bite_sized](VerticalSliceVocabTests.test_chunks_are_bite_sized.md) method: HOLE: no docstring
  - [VerticalSliceVocabTests.test_no_new_machinery_claimed](VerticalSliceVocabTests.test_no_new_machinery_claimed.md) method: HOLE: no docstring
