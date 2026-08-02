import sys; from pathlib import Path; import numpy as np
sys.path.insert(0, str(Path(".agent-work/445/envelope").resolve())); sys.path.insert(0,"C:/Programs/f1Brainz")
import grip_iter as GI
from matern_smoother import MaternSmoother
DELTA=0.06
def laps(car,rd):
    q=GI.H.load_session(2023,rd,"Q"); runs=GI.H.driver_runs(q,car); out=[]
    for ls,le in GI.flying_windows(q,car):
        run=next((r for r in runs if r["t0"]<=ls and r["t1"]>=le),None)
        if run is None: continue
        tp=np.asarray(run["tp"],float);X=np.asarray(run["X"],float);Y=np.asarray(run["Y"],float)
        tc=np.asarray(run["tc"],float);V=np.asarray(run["V"],float)
        mp=(tp>=ls)&(tp<=le);mc=(tc>=ls)&(tc<=le)
        if mp.sum()>=150: out.append((tp[mp],X[mp],Y[mp],tc[mc],V[mc]))
    out.sort(key=lambda L:-len(L[3])); return out[:1]
LL=[]
for rd in (1,17):
    for c in ("VER","HAM","LEC","RUS"): LL+=laps(c,rd)
def resids(order,ell,sig_pos=1.5,sf=100.0):
    R=[]
    for tp,X,Y,tc,V in LL:
        nc=len(tc); test=np.arange(2,nc,4); train=np.setdiff1d(np.arange(nc),test)
        sm=MaternSmoother(ell,sf,sig_pos,DELTA,order=order,iters=2).fit(tp,X,Y,tc[train],V[train],query_times=tc[test]+DELTA)
        R.append(V[test]-sm.speed_at(tc[test]+DELTA))
    return np.abs(np.concatenate(R))
print(f"{len(LL)} laps. Robust held-out SPEED error (floor 0.49 m/s). [median |e| / MAE / %glitch>5]")
print(f"{'ell':>5} | {'5/2 med':>8}{'5/2 MAE':>8}{'5/2 g%':>7} | {'7/2 med':>8}{'7/2 MAE':>8}{'7/2 g%':>7}")
for ell in (3.0,4.5,6.0,8.0,11.0):
    a3=resids(3,ell); a4=resids(4,ell)
    print(f"{ell:>5.1f} | {np.median(a3):>8.3f}{a3.mean():>8.3f}{100*np.mean(a3>5):>7.1f} | "
          f"{np.median(a4):>8.3f}{a4.mean():>8.3f}{100*np.mean(a4>5):>7.1f}")
