# P6 — Soft push/managed classifier from context signals only (2023 race data)

## Question
Does a simple context-signal soft classifier separate push laps from managed laps in
existing 2023 race data — producing separable pace distributions that reconcile with
known-push contexts?

## Answer
**No, not with this formula on this data.** A context-only push-weight built purely from
strategy/traffic signals (no pace information) does correlate with fuel-corrected pace —
Pearson r = **-0.227** between the context score and stint-relative pace headroom, driven
almost entirely by one ingredient (clean-air gap ahead). But the weight distribution is
**unimodal, not bimodal** (mushy, not two clusters), **~69% of laps sit in the ambiguous
0.3–0.7 middle**, and three of four hand-picked "known-push" sanity contexts (post-restart,
pre-pit undercut, even final-stint-clean-air vs. the "managed" mid-stint proxy) **did not
separate cleanly** or pointed the wrong way. The signal is real but weak; this specific
weighted-average formula is not good enough to trust as a soft classifier.

## Method — exact formula

**Data**: `data/damage_integrals.db::grip_bin_obs` (context: `gap_ahead_s`, `tyre_life`,
`is_last_stint_lap`, `follows_interruption`, `stint_num` — collapsed from bin-grain to
lap-grain by `MAX()` since these columns are constant across bins within a lap) joined to
`data/f1_data_2023.db::lap_times` (`lap_time`, `pit_in_time`, `pit_out_time`,
`track_status`) via `(gp_name, driver/driver_id, lap_number)`. Read-only throughout.

**Races** (2023 R, chosen for clean ~18-20-driver coverage in `grip_bin_obs`): Spain,
Hungary, Austria, Abu Dhabi, Great Britain. **5,380 scored laps** after exclusions.

**Exclusions**: lap 1 (standing start), any lap with `pit_in_time` or `pit_out_time`
not null (in/out-laps).

**Fuel correction** (per handoff: lap_number as fuel proxy, simple linear correction):
for each `(gp, driver, stint)`, OLS-fit `lap_time = a + b*lap_number` using only
`track_status == '1'` (pure green, no SC/VSC/yellow anywhere in the lap) laps in that
stint. Needs ≥4 clean points; falls back to a pooled per-`(gp,driver)` slope, then a
global pooled slope, then a literal last-resort constant (`-0.04 s/lap`) — none of the
5,380 laps hit the last-resort case in this run. `fuel_corrected = lap_time - b*(lap -
first_lap_of_stint)`. `headroom_s = fuel_corrected - min(fuel_corrected in that stint)` —
0 means "this is the fastest fuel-corrected lap of its stint," growing positive the
further a lap sits from that stint's own demonstrated ceiling.

**Four components, each mapped to [0,1]:**
- `c_gap` (clean air) = `sigmoid((min(gap_ahead_s, 30) - 2.5) / 0.8)` — soft threshold
  around the 2.5s gap-ahead cue from the handoff.
- `c_tyre` (tyre freshness) = `exp(-tyre_life / 25)`.
- `c_pos` (stint position) = `0.5 + 0.25*is_last_stint_lap + 0.25*follows_interruption`,
  clipped to 1.
- `c_pace` (pace headroom) = `exp(-headroom_s / 0.6)` — 0.6s chosen as a rough
  "meaningfully off personal-best pace" scale.

**Two weights reported, deliberately:**
- `w_full = 0.30·c_gap + 0.15·c_tyre + 0.15·c_pos + 0.40·c_pace` — as literally specified
  in the handoff (pace headroom is one of the stated ingredients).
- `w_context = ` the same three non-pace components renormalized to sum to 1 (`0.30/0.60,
  0.15/0.60, 0.15/0.60`) — **pace excluded**. This split was added because `w_full`
  bakes 40% of its own weight directly out of `headroom_s`, so "does w_full's pace
  separate by w_full" is partly circular by construction. `w_context` is the honest test
  of whether context alone predicts push behavior; it is the number that matters below.

## 1. Distribution of w

Neither is bimodal. Both are a single, roughly bell-ish hump with no visible second
cluster:

- `w_full`: mean 0.515, median 0.516, stdev 0.160. 88% of mass sits in [0.3, 0.8).
- `w_context`: mean 0.542, median 0.507, stdev 0.173. Mass spread more evenly across
  [0.3, 0.8), with a secondary local bump at [0.7, 0.8) (22.8% of laps) — the closest
  thing to bimodality in either distribution, but it's a shoulder, not a clean second
  mode, and the trough between it and the main mass is shallow.

**No formula variant here produced two separated clusters.** This alone is a partial
answer to the framing question: on this data, "push" and "managed" as this formula
defines them are not two discrete driving modes visible in context signals — more a
continuum.

## 2. Pace separation

Reported as `headroom_s` (stint-relative, seconds off that stint's own best
fuel-corrected lap) — **not** raw lap time, which was tried first and rejected: raw
fuel-corrected seconds mix circuits of very different lap length (Austria ~65s laps vs.
Great Britain ~88s laps) and swamp any real signal with track-to-track variance (stdev
~8s on raw times vs. the sub-1s effect actually being tested).

| bucket | `w_context` n | mean headroom (s) | `w_full` n | mean headroom (s) |
|---|---|---|---|---|
| high (≥0.7) | 1525 | **0.447** | 720 | 0.140 |
| mid (0.3–0.7) | 3683 | 0.619 | 4119 | 0.540 |
| low (≤0.3) | 172 | **0.989** | 541 | 1.498 |

`w_full`'s separation (0.140 vs 1.498s, r = -0.697 against headroom) is the expected
tautology — 40% of `w_full` *is* a transform of headroom, so of course it separates.
The honest number is `w_context`: **r = -0.227**, monotonic across buckets (0.447 →
0.619 → 0.989), real but modest, and the buckets **overlap heavily**: high-bucket stdev
0.358s, low-bucket stdev 0.709s, against a 0.542s mean gap. This is a shifted
distribution, not a separated one.

Per-component breakdown of where the -0.227 comes from (correlation of each raw
component against `headroom_s` alone, unweighted):
- `c_gap` (clean air) alone: r = **-0.218** — essentially all of `w_context`'s signal.
- `c_tyre` (tyre freshness) alone: r = -0.033 — contributes almost nothing.
- `c_pos` (stint position: final-stint + post-restart bump) alone: r = **+0.068** —
  wrong sign. Laps flagged as "should be pushing" by this component trend very slightly
  *slower* relative to their stint's own best, not faster.

## 3. Sanity checks against known contexts

| context | n | mean `w_context` | mean headroom (s) |
|---|---|---|---|
| final-stint clean-air (expected **push**) | 132 | 0.750 | 0.586 |
| post-restart (`follows_interruption`, expected **push**) | 92 | 0.516 | **0.794** |
| pre-pit-stop / undercut (expected **push**) | 177 | 0.606 | 0.613 |
| mid-stint clean-air, non-final (expected **managed**) | 981 | 0.699 | **0.442** |
| early-stint first 2 laps (expected **managed**, nursing) | 817 | 0.544 | 0.590 |

This is the weakest part of the result. Two of three "expected-push" contexts do **not**
show better relative pace than the "expected-managed" mid-stint proxy — in fact the
"managed" proxy has the *best* mean headroom (0.442s) of any group tested, better than
every push context including final-stint-clean-air (0.586s). Post-restart laps are the
*worst* group overall (0.794s) despite scoring a middling `w_context` — restarts in this
data are not fast relative to a driver's own stint-best, plausibly because the field is
still bunched/sorting and tyres aren't fully up to temperature right after a safety-car
restart, which the formula's `c_pos` bump doesn't capture and actively works against (see
§2's wrong-sign correlation). Pre-pit "undercut push" laps land in the middle on both
metrics — not a clean confirmation either.

Only the final-stint vs. mid-stint comparison points the expected direction on
`w_context` itself (0.750 vs 0.699), and even that gap is small and the headroom
ordering (0.586 vs 0.442) runs the *opposite* way.

## 4. The blur

- `w_context` in [0.3, 0.7]: **3,683 / 5,380 = 68.5%** of laps.
- `w_full` in [0.3, 0.7]: **4,119 / 5,380 = 76.6%** of laps.

Roughly seven laps in ten sit in the ambiguous middle under either weight. Consistent
with §1's unimodal-not-bimodal finding — there is no clean 30/70 push/managed split
sitting under a mushy label, the mush is the actual shape of the distribution.

## What was tested AND what was NOT tested

- **Tested:** the exact weighted-average formula above, on 5,380 non-out/in-lap laps
  across 5 clean-coverage 2023 races (Spain, Hungary, Austria, Abu Dhabi, Great Britain),
  with per-stint linear fuel correction fit on green-flag laps only, `headroom_s` as the
  pace metric, and 5 hand-picked sanity contexts.
- **NOT tested:** other 2023 races (only 9 have `grip_bin_obs` R coverage at all; 4 were
  dropped for lower driver coverage); the sprint (`S`) session mentioned as available;
  non-linear or per-driver-varying fuel correction; a multiplicative/AND-gate combination
  of components instead of a weighted sum (a weighted sum lets one strong ingredient,
  clean air, carry the whole score even when the others are noise or wrong-signed — an
  AND-gate would very plausibly behave differently and is the most obvious next variant);
  a two-sided clean-air definition (gap *behind*, not just ahead — the handoff specified
  `gap_ahead_s` only, but "not currently defending" is arguably as relevant to push
  intent as "not currently following"); whether laps that ran under any yellow/VSC/SC
  flag *elsewhere in the merge* (only excluded from the slope-fit, not from the scored
  population) are adding headroom noise unrelated to intent — this was not checked and
  is a plausible contributor to the overlap in §2.
- **Next variant (if pursuing further):** (1) drop or flip the `c_pos` stint-position
  component — it's wrong-signed on this data and actively hurts, not just unhelpful; (2)
  try an AND-gate/multiplicative combination in place of the weighted average so a single
  strong ingredient can't carry an otherwise-unconfirmed score; (3) add a gap-behind term
  to the clean-air component; (4) exclude yellow/VSC/SC-touched laps from the *scored*
  population, not just the fuel-correction fit, before re-running §2/§4.

## What it taught beyond the question

Building `w_context` as a genuinely pace-blind sub-score (rather than trusting the
handoff's single combined `w`) was necessary, not optional — `w_full` as literally
specified is ~40% self-referential against the very pace metric it's later validated
against, and reporting only `w_full`'s "separation" would have been a false positive by
construction. The bigger surprise: of the four context ingredients suggested, only clean
air (`gap_ahead_s`) carries any real signal (r = -0.218 alone, versus -0.227 for all
three combined) — tyre freshness and the stint-position bump are close to dead weight,
and stint-position is actively backwards. A soft classifier built from this ingredient
list is really just a noisy clean-air detector wearing a bigger jacket.

## Surviving pure module
None — this is a linear scoring formula validated against one dataset slice, not a
reusable logic module. Nothing here should be lifted into real code as-is.

## Disposition
`deleted`

**Detail:** the answer is captured above; the throwaway script
(`push_managed_spike.py`) stays only long enough for review, then should be removed —
nothing in it survives as-is given the wrong-signed `c_pos` component and the untested
AND-gate variant that's the obvious next step.

## One command to run (if not yet deleted)
```
cd C:\Programs\f1Brainz
"C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe" ".agent-work/explore-ref-utilization/excursions/scratch/P6/push_managed_spike.py"
```
