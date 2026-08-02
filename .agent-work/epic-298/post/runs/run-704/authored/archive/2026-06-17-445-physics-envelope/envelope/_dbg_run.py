import sys; from pathlib import Path; import numpy as np
sys.path.insert(0, str(Path(".agent-work/445/envelope").resolve())); sys.path.insert(0,"C:/Programs/f1Brainz")
import grip_iter as GI
from matern_smoother import MaternSmoother
q=GI.H.load_session(2023,1,"Q")
runs=GI.H.driver_runs(q,"VER")
print(f"VER: {len(runs)} runs")
for k,r in enumerate(runs):
    tp=np.asarray(r["tp"],float)
    print(f"  run{k}: nX={len(r['X'])} tspan={tp[-1]-tp[0]:.1f}s maxdt={np.diff(tp).max():.3f}s "
          f"keys={list(r.keys())}")
r=max(runs,key=lambda r:len(r["X"]))
tp=np.asarray(r["tp"],float);X=np.asarray(r["X"],float);Y=np.asarray(r["Y"],float)
tc=np.asarray(r["tc"],float);V=np.asarray(r["V"],float)
# full fit residual at observed points
sm=MaternSmoother(2.0,100.0,0.3,0.06,order=3,iters=2).fit(tp,X,Y,tc,V)
px,py=sm.pos_at(tp)
print(f"FULL-fit pos residual at obs: RMSE={np.sqrt(np.mean((X-px)**2+(Y-py)**2))*1000:.1f}mm")
# held-out at ell=2
n=len(tp);test=np.arange(0,n,4);train=np.setdiff1d(np.arange(n),test)
sm2=MaternSmoother(2.0,100.0,0.3,0.06,order=3,iters=2).fit(tp[train],X[train],Y[train],tc,V,query_times=tp[test])
qx,qy=sm2.pos_at(tp[test])
err=np.sqrt((X[test]-qx)**2+(Y[test]-qy)**2)
print(f"HELD-OUT ell=2: RMSE={np.sqrt(np.mean(err**2)):.3f}m  median={np.median(err):.3f}m  max={err.max():.1f}m")
print(f"  worst 5 test errors (m): {np.sort(err)[-5:]}")
print(f"  speed range {V.min():.0f}-{V.max():.0f} m/s; pos span X {X.max()-X.min():.0f}m Y {Y.max()-Y.min():.0f}m")
