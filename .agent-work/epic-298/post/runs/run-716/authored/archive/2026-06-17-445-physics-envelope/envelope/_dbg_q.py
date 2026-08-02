import sys; from pathlib import Path; import numpy as np
sys.path.insert(0, str(Path(".agent-work/445/envelope").resolve())); sys.path.insert(0,"C:/Programs/f1Brainz")
import grip_iter as GI
from matern_smoother import MaternSmoother
from src.preprocessing.trajectory.smoother import StintSmoother
q=GI.H.load_session(2023,1,"Q")
runs=GI.H.driver_runs(q,"VER")
best=None
for ls,le in GI.flying_windows(q,"VER"):
    run=next((r for r in runs if r["t0"]<=ls and r["t1"]>=le),None)
    if run is None: continue
    tp=np.asarray(run["tp"],float);X=np.asarray(run["X"],float);Y=np.asarray(run["Y"],float)
    tc=np.asarray(run["tc"],float);V=np.asarray(run["V"],float)
    mp=(tp>=ls)&(tp<=le);mc=(tc>=ls)&(tc<=le)
    if mp.sum()>=150:
        cand=(tp[mp],X[mp],Y[mp],tc[mc],V[mc],np.diff(tp[mp]).max())
        if best is None or mp.sum()>len(best[0]): best=cand
tp,X,Y,tc,V,mdt=best
print(f"lap: {len(tp)} pos, {len(tc)} spd, dt med {np.median(np.diff(tp)):.3f}s max {mdt:.3f}s span {tp[-1]-tp[0]:.1f}s spd {V.min():.0f}-{V.max():.0f}")
for name,mk in [("prod",lambda:StintSmoother(2.0,100.0,0.3,0.06,iters=2)),("mine",lambda:MaternSmoother(2.0,100.0,0.3,0.06,order=3,iters=2))]:
    sm=mk().fit(tp,X,Y,tc,V); px,py=sm.pos_at(tp)
    print(f"  FULL {name}: RMSE {np.sqrt(np.mean((X-px)**2+(Y-py)**2))*1000:.1f}mm")
n=len(tp);test=np.arange(2,n,4);train=np.setdiff1d(np.arange(n),test)
for name,mk in [("prod",lambda:StintSmoother(2.0,100.0,0.3,0.06,iters=2)),("mine",lambda:MaternSmoother(2.0,100.0,0.3,0.06,order=3,iters=2))]:
    sm=mk().fit(tp[train],X[train],Y[train],tc,V,query_times=tp[test]); px,py=sm.pos_at(tp[test])
    err=np.sqrt((X[test]-px)**2+(Y[test]-py)**2)
    print(f"  HELDOUT-pos {name}: RMSE {np.sqrt(np.mean(err**2))*1000:.1f}mm median {np.median(err)*1000:.1f}mm max {err.max()*1000:.0f}mm")
