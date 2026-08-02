import sys; from pathlib import Path; import numpy as np
sys.path.insert(0, str(Path(".agent-work/445/envelope").resolve()))
sys.path.insert(0, "C:/Programs/f1Brainz")
import grip_iter as GI
from braking_collect import _alat, W
G=GI.G
q=GI.H.load_session(2023,1,"Q")
car="VER"
runs=GI.H.driver_runs(q,car); fits={}
allslope=[]; allalat=[]; npts=0
for ls,le in GI.flying_windows(q,car):
    run=next((r for r in runs if r["t0"]<=ls and r["t1"]>=le),None)
    if run is None: continue
    key=(round(run["t0"],1),round(run["t1"],1)); ss=fits.get(key)
    if ss is None:
        ss=GI.H.StintSmoother(2.0,100.0,0.3,0.06,iters=2); ss.fit(run["tp"],run["X"],run["Y"],run["tc"],run["V"]); fits[key]=ss
    mask=(ss.kind==1)&(ss.ts>=ls)&(ss.ts<=le)
    t=ss.ts[mask]; o=np.argsort(t); t=t[o]
    keep=np.concatenate([[True],np.diff(t)>1e-9]); t=t[keep]
    X,Y=ss.pos_at(t); v=np.interp(t,run["tc"],run["V"])
    n=len(v); npts+=n
    dt=np.median(np.diff(t)) if n>1 else 0
    for i in range(n):
        c,d=i-W,i+W+1
        if c<0 or d>n: continue
        tt=t[c:d]-t[c]; vv=v[c:d]
        if tt[-1]-tt[0]<=0: continue
        slope=np.polyfit(tt,vv,1)[0]/G
        al=_alat(X,Y,v[i],i,n)
        allslope.append(slope); allalat.append(al)
print(f"median dt between nodes: {dt:.4f}s  ({1/dt:.1f} Hz)")
print(f"total candidate points: {npts}")
s=np.array(allslope); a=np.array(allalat)
print(f"decel slope (g): min {s.min():.2f} p5 {np.percentile(s,5):.2f} med {np.median(s):.2f}")
print(f"  braking points slope<-1.0: {np.sum(s<-1.0)}   slope<-1.5: {np.sum(s<-1.5)}   slope<-2.0: {np.sum(s<-2.0)}")
print(f"alat (g) on those braking(<-1.0) points: ", end="")
bm=s<-1.0
print(f"med {np.median(a[bm]):.2f} p90 {np.percentile(a[bm],90):.2f}  | alat<0.6 count {np.sum((s<-1.5)&(a<0.6))}  alat<1.5 count {np.sum((s<-1.5)&(a<1.5))}")
