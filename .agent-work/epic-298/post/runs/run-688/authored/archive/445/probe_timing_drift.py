"""Probe: is the inter-stream timing offset CONSTANT or DRIFTING along the lap?

Motivation: the position along-track residual reads as ~47 ms timing jitter, but
the speed-scaled calibrator lands sig_t ~ 65 ms on the same Monza VER Q lap.  A
single sig_t lumps any slow within-lap CLOCK DRIFT into the jitter estimate and
inflates it.  Two independent probes:

  (A) INTER-STREAM lag drift (decisive for common-mode clock drift): windowed
      cross-correlation of position-derived speed vs the speed-stream speed.
      Windowing averages out the per-sample jitter and exposes the slow lag.
      Flat lag(distance) => one global delta is fine.  Ramping lag => the two
      clocks drift apart and a constant delta leaves structure on the table.

  (B) WITHIN-STREAM along-residual time-error eps_i = along_i / speed_i vs lap
      distance.  Pure jitter => zero-mean white, std flat.  A slow trend =>
      structured (partly recoverable) drift; the detrended std is the true
      jitter floor and should drop toward ~47 ms, explaining the 65 ms inflation.
"""
import sys
import warnings
import logging

sys.path.insert(0, '.agent-work/445/envelope')
sys.path.insert(0, '.')
warnings.filterwarnings('ignore')
logging.getLogger('fastf1').setLevel(logging.ERROR)

import numpy as np

from src.preprocessing.trajectory.loaders import driver_num, driver_streams, load_session
from src.preprocessing.trajectory.calibration import session_offset, fit_stint_hp
from src.preprocessing.trajectory.smoother import StintSmoother

print("Loading VER Monza 2023 Q...")
q = load_session(2023, 'Italy', 'Q')
num = driver_num(q, 'VER')
laps = q.laps.pick_drivers('VER')
valid = laps[laps['LapTime'].notna()]
fast = valid.loc[valid['LapTime'].dt.total_seconds().idxmin()]
t0 = float(fast['LapStartTime'].total_seconds())
t1 = float(fast['Time'].total_seconds())
print(f"Lap window: {t0:.1f} -> {t1:.1f} s ({t1-t0:.1f} s)")

pos_d, spd_d = driver_streams(q, num)
PAD = 2.0
mp = (pos_d['t'] >= t0 - PAD) & (pos_d['t'] <= t1 + PAD)
mc = (spd_d['t'] >= t0 - PAD) & (spd_d['t'] <= t1 + PAD)
tp, X, Y = pos_d['t'][mp], pos_d['X'][mp], pos_d['Y'][mp]
tc, V = spd_d['t'][mc], spd_d['V'][mc]
print(f"Pos samples: {len(tp)}, speed samples: {len(tc)}")
print(f"Pos dt: median={np.median(np.diff(tp))*1000:.0f} ms  Speed dt: median={np.median(np.diff(tc))*1000:.0f} ms")


# ---------------------------------------------------------------------------
# (A) INTER-STREAM lag drift via windowed cross-correlation
# ---------------------------------------------------------------------------
print("\n" + "=" * 70)
print("(A) INTER-STREAM LAG DRIFT  (position-speed vs stream-speed)")
print("=" * 70)

# Uniform 20 Hz grid over the lap (exclude the pad)
GRID = 0.05
tg = np.arange(t0, t1, GRID)
Xg = np.interp(tg, tp, X)
Yg = np.interp(tg, tp, Y)
# position-derived speed (light 5-pt smooth to tame interpolation noise)
vpx = np.gradient(Xg, tg)
vpy = np.gradient(Yg, tg)
v_pos = np.hypot(vpx, vpy)
k = np.ones(5) / 5.0
v_pos = np.convolve(v_pos, k, mode='same')
# speed-stream speed on the same grid (m/s; V is km/h)
v_spd = np.interp(tg, tc, V) / 3.6

MAXLAG = 8  # +/- 8 samples = +/- 0.4 s


def best_lag(a, b):
    """Sub-sample lag tau (s) s.t. b(t) ~ a(t - tau), via normalised xcorr peak.
    Positive tau => b lags a (stream-speed later than position-speed)."""
    a = a - a.mean()
    b = b - b.mean()
    na = np.sqrt(np.sum(a * a))
    nb = np.sqrt(np.sum(b * b))
    if na < 1e-6 or nb < 1e-6:
        return np.nan
    lags = np.arange(-MAXLAG, MAXLAG + 1)
    cc = np.array([
        np.sum(a[max(0, L):len(a) + min(0, L)] * b[max(0, -L):len(b) + min(0, -L)])
        for L in lags
    ]) / (na * nb)
    j = int(np.argmax(cc))
    if 0 < j < len(cc) - 1:  # parabolic sub-sample refinement
        y0, y1, y2 = cc[j - 1], cc[j], cc[j + 1]
        denom = (y0 - 2 * y1 + y2)
        shift = 0.5 * (y0 - y2) / denom if abs(denom) > 1e-9 else 0.0
    else:
        shift = 0.0
    return (lags[j] + shift) * GRID


# global lag for reference
print(f"Global xcorr lag (whole lap): {best_lag(v_pos, v_spd)*1000:+.0f} ms")
print(f"Calibrated session delta:     {session_offset([(tp, X, Y, tc, V)])[0]*1000:+.0f} ms")

# windowed
NWIN = 6
edges = np.linspace(0, len(tg), NWIN + 1).astype(int)
dist = np.concatenate([[0], np.cumsum(0.5 * (v_spd[1:] + v_spd[:-1]) * np.diff(tg))])
print(f"\n{'window':>6}  {'t_mid(s)':>9}  {'dist(m)':>8}  {'v_mean(km/h)':>12}  {'lag(ms)':>8}")
lags_w = []
dmid_w = []
for w in range(NWIN):
    s = slice(edges[w], edges[w + 1])
    if edges[w + 1] - edges[w] < 2 * MAXLAG + 4:
        continue
    lag = best_lag(v_pos[s], v_spd[s])
    tmid = float(np.mean(tg[s])) - t0
    dmid = float(np.mean(dist[s]))
    vmean = float(np.mean(v_spd[s])) * 3.6
    lags_w.append(lag)
    dmid_w.append(dmid)
    print(f"{w:>6}  {tmid:>9.1f}  {dmid:>8.0f}  {vmean:>12.1f}  {lag*1000:>+8.0f}")

lags_w = np.array(lags_w)
dmid_w = np.array(dmid_w)
if len(lags_w) >= 3:
    sl, ic = np.polyfit(dmid_w, lags_w * 1000, 1)  # ms per metre
    print(f"\nLag trend: slope = {sl*1000:+.2f} ms/km,  spread(max-min) = "
          f"{(lags_w.max()-lags_w.min())*1000:.0f} ms,  std = {np.std(lags_w)*1000:.1f} ms")
    print("  -> FLAT lag (spread within a sample ~50ms) = one global delta is fine.")
    print("  -> RAMPING lag = the two clocks drift apart along the lap.")


# ---------------------------------------------------------------------------
# (B) WITHIN-STREAM along-residual time-error vs distance
# ---------------------------------------------------------------------------
print("\n" + "=" * 70)
print("(B) WITHIN-STREAM along-residual eps = along/speed  vs lap distance")
print("=" * 70)

delta, _ = session_offset([(tp, X, Y, tc, V)])
hp = fit_stint_hp(tp, X, Y, tc, V, delta=delta, iters=3, order=4)
print(f"HPs: ell={hp['ell']:.2f} sig_pos={hp['sig_pos']:.3f} "
      f"chi2_pos={hp['chi2_pos']:.2f} chi2_spd={hp['chi2_spd']:.2f}")
iso = StintSmoother(hp['ell'], hp['sf'], hp['sig_pos'], delta, iters=3, order=4)
iso.fit(tp, X, Y, tc, V)

# restrict residual analysis to the flying lap (drop the pad)
inlap = (tp >= t0) & (tp <= t1)
tpl = tp[inlap]
Xh, Yh = iso.pos_at(tpl)
vx, vy = iso.vel_at(tpl)
spd = np.hypot(vx, vy)
ex, ey = vx / spd, vy / spd
along = (X[inlap] - Xh) * ex + (Y[inlap] - Yh) * ey
eps = along / spd  # per-sample time error (s)
# distance along lap at each pos sample
distp = np.concatenate([[0], np.cumsum(0.5 * (spd[1:] + spd[:-1]) * np.diff(tpl))])

# fit slow trend: linear + quadratic in distance
A = np.column_stack([np.ones_like(distp), distp, distp ** 2])
coef, *_ = np.linalg.lstsq(A, eps, rcond=None)
trend = A @ coef
detr = eps - trend

print(f"\neps mean = {np.mean(eps)*1000:+.1f} ms  (near 0 => jitter not offset)")
print(f"eps std  (raw)       = {np.std(eps)*1000:.1f} ms")
print(f"eps std  (detrended) = {np.std(detr)*1000:.1f} ms  "
      f"(if << raw, a slow drift inflated the raw jitter)")
print(f"trend swing over lap = {(trend.max()-trend.min())*1000:.0f} ms "
      f"(linear+quad in distance)")

# per-sixth means to see the shape
NB = 6
be = np.linspace(0, len(eps), NB + 1).astype(int)
print(f"\n{'sixth':>6}  {'dist(m)':>8}  {'eps_mean(ms)':>12}  {'eps_std(ms)':>11}")
for b in range(NB):
    s = slice(be[b], be[b + 1])
    print(f"{b:>6}  {np.mean(distp[s]):>8.0f}  {np.mean(eps[s])*1000:>+12.1f}  {np.std(eps[s])*1000:>11.1f}")

print("\nDone.")
