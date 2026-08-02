import sys; from pathlib import Path; import numpy as np
sys.path.insert(0, str(Path(".agent-work/445/envelope").resolve())); sys.path.insert(0,"C:/Programs/f1Brainz")
import grip_iter as GI
from matern_smoother import MaternSmoother
DELTA=0.06
def laps(car,rd=1):
    q=GI.H.load_session(2023,rd,"Q"); runs=GI.H.driver_runs(q,car); out=[]
    for ls,le in GI.flying_windows(q,car):
        run=next((r for r in runs if r["t0"]<=ls and r["t1"]>=le),None)
        if run is None: continue
        tp=np.asarray(run["tp"],float);X=np.asarray(run["X"],float);Y=np.asarray(run["Y"],float)
        tc=np.asarray(run["tc"],float);V=np.asarray(run["V"],float)
        mp=(tp>=ls)&(tp<=le);mc=(tc>=ls)&(tc<=le)
        if mp.sum()>=150: out.append((tp[mp],X[mp],Y[mp],tc[mc],V[mc]))
    out.sort(key=lambda L:-len(L[3])); return out[:1]
LL=laps("VER")+laps("HAM")+laps("LEC")+laps("RUS")
res=[]; acc=[]; spd=[]
for tp,X,Y,tc,V in LL:
    nc=len(tc); test=np.arange(2,nc,4); train=np.setdiff1d(np.arange(nc),test)
    sm=MaternSmoother(8.0,100.0,5.0,DELTA,order=3,iters=2).fit(tp,X,Y,tc[train],V[train],query_times=tc[test]+DELTA)
    pred=sm.speed_at(tc[test]+DELTA)
    dVdt=np.gradient(V,tc)   # local accel proxy at all car samples
    res.append(V[test]-pred); acc.append(np.abs(dVdt[test])); spd.append(V[test])
res=np.concatenate(res); acc=np.concatenate(acc); spd=np.concatenate(spd)
a=np.abs(res)
print(f"n held-out speed points = {len(res)}")
print(f"  signed mean (bias): {res.mean():+.3f} m/s")
print(f"  MAE  {a.mean():.3f} | median |e| {np.median(a):.3f} | p75 {np.percentile(a,75):.3f} | p90 {np.percentile(a,90):.3f} | p99 {np.percentile(a,99):.3f} | max {a.max():.2f}")
print(f"  RMSE {np.sqrt(np.mean(res**2)):.3f}")
# where does error live? split by local |dv/dt|
lo=acc<np.percentile(acc,50); hi=acc>=np.percentile(acc,80)
print(f"  |e| on low-accel half (|dv/dt|<median): {np.mean(a[lo]):.3f} m/s  (n={lo.sum()})")
print(f"  |e| on high-accel (top 20% |dv/dt|, braking/throttle): {np.mean(a[hi]):.3f} m/s  (n={hi.sum()})")
print(f"  corr(|e|, |dv/dt|) = {np.corrcoef(a,acc)[0,1]:+.3f}")
print(f"  median |dv/dt| over held-out pts: {np.median(acc):.2f} m/s^2 ; p90 {np.percentile(acc,90):.1f}")
