# What the render now refuses, and whether any of it is legitimate

Measured, not argued: `m3_what_the_render_refuses.py` runs **7 topologies × 2
scan-match counts × 2 arms = 28 rows**, with each arm printing the sha256 and
byte length of the source it loaded and a guard asserting the render loop is in
one arm and not the other. Arms are `REWORK3` (`HEAD` = `52ba9940`) and
`WORKTREE`. Output: `m3-what-the-render-refuses.txt`.

```
rows measured: 28   topologies x match-counts: 14   rows whose answer this rework changed: 2
  CHANGED  n=2  B5/B6 owns an ARCHIVED entry; crew claims the scan
  CHANGED  n=2  owns an ARCHIVED entry; crew claims the LEADING match only
```

## The refusal, stated exactly

The render skips a scanned candidate **iff** `session_view_provenance(binding,
sid)` attributes that path to a binding key other than `binding_key(payload)`.
Reaching that skip at all requires the session to be on **B5's door** — it owns
a visible entry whose spine no longer loads — because:

- an **empty** view (`#261`) attributes nothing, so nothing is ever skipped;
- a **non-empty view the session owns none of** (`B4`) returns `{}` one branch
  above and never reaches the scan;
- a view whose owned entry **loads** never reaches the scan either.

So the whole refusal set is: *a session whose own spine no longer loads, offered
a candidate its own session view says belongs to another key.*

## The two changed rows

| row | before | after |
|---|---|---|
| every candidate attributed to the crew | rendered the crew's gate plus "Pick the run back up at this gate and drive it through the engine" | renders nothing (`{}`) |
| only the glob-leading candidate attributed to the crew | rendered the crew's gate | renders the **other** candidate, the one nobody has claimed |

The second row is the design choice worth naming: the repair selects the first
candidate that contradicts nobody rather than refusing outright when the leading
one does. That withholds strictly less, and the answer it gives is the same one
the old code would have given had the glob returned the other order — the point
is that **glob order no longer decides**. The reviewer's own `rev4_instrument.py`
C2 shows this directly on the current tree: `render_leaks_CREW-MARKER` goes
`true → false` while `render_leaks_THIRD-MARKER` goes `false → true`, the third
spine being the unclaimed one.

## Is any legitimate resume context withheld?

**No, on the evidence.** The only session that now gets nothing where it once
got something is one whose own spine no longer loads and every visible candidate
belongs to another key in its own view. The only context that was on offer to it
was another binding key's gate, carrying the imperative to drive that gate — the
#549 failure class this gate exists to end. Nothing it could legitimately drive
is lost, because the spine it could legitimately drive is exactly the one that
no longer loads.

Every other row is byte-identical between the arms, including:

- `#261` no binding at all → still binds and renders, at both counts;
- `tc1` archived entry + candidates claimed by **nobody** → still binds (n=1)
  and still renders (n=1, n=2), untouched, which is the recorded authority
  question left for the Admiral;
- archived entry + the candidate is the session's **own bare claim** → renders;
- `B4` owns nothing visible → still `{}`;
- `B7` cross-session claim → still binds and still renders, at both counts. The
  guard cannot see it, the prose now says so, and widening it is the Admiral's
  call.
