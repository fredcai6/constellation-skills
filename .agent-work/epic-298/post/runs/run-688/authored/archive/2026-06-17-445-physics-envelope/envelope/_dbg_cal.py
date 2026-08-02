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
LL=laps("VER")+laps("HAM")
def hs(lap,order,ell,sf,sig_pos):
    tp,X,Y,tc,V=lap; nc=len(tc); test=np.arange(2,nc,4); train=np.setdiff1d(np.arange(nc),test)
    sm=MaternSmoother(ell,sf,sig_pos,DELTA,order=order,iters=2).fit(tp,X,Y,tc[train],V[train],query_times=tc[test]+DELTA)
    pred=sm.speed_at(tc[test]+DELTA); return np.sqrt(np.mean((V[test]-pred)**2))
print("held-out speed RMSE (m/s); floor=0.49.  [o3 | o4]")
print(f"{'sig_pos':>8}{'sf':>7}{'ell':>6}   o3      o4")
for sig_pos in (0.3,1.5,5.0):
  for sf in (100.0,1000.0):
    for ell in (4.5,8.0,14.0):
        r3=np.mean([hs(L,3,ell,sf,sig_pos) for L in LL]); r4=np.mean([hs(L,4,ell,sf,sig_pos) for L in LL])
        print(f"{sig_pos:>8}{sf:>7.0f}{ell:>6.1f}  {r3:6.3f}  {r4:6.3f}")
