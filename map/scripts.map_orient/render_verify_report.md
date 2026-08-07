# scripts.map_orient:render_verify_report
function, scripts/map_orient.py:923, 54 lines

```python
def render_verify_report(first_line: str, code: int, problems: Sequence[str], receipt_rel: str, substitutes: Sequence[object] = ()) -> list[str]
```

PURE. stdout lines; line 0 is always a reserved literal.

Reports each substitute's PROVENANCE, not merely its path. The receipt
distinguishes "resolved from the known fallback set" (the filesystem
agreed) from "the agent said so", and a distinction no reader is ever shown
is a distinction that does not exist -- this is the REPORTED half of
reported-degraded-mode, which is the whole point of the mode.

Decoding is deliberately lenient (`substitute_label`): a receipt written
before the label existed, or carrying an unrecognised value, reads as the
conservative `agent-declared`. An omission can therefore never be read as
verification -- the failure direction is always toward "unverified".

No anchor id can reach this output: a substitute is a PATH, and it was
declared by the agent in the first place, so echoing it back hands over
nothing the tool was not already given.

calls internal: substitute_label
calls stdlib: builtins.isinstance, builtins.len
reads internal: EXIT_DEGRADED_UNDISCHARGED, EXIT_OK, EXIT_UNRESOLVABLE_ROOT, LABEL_KNOWN_FALLBACK
reads stdlib: builtins.dict
unresolved: 7 calls (dispatch-unknown-base)

referenced by: 2 sites, this module only
