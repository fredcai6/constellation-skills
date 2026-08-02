import sys; from pathlib import Path; import numpy as np
sys.path.insert(0, str(Path(".agent-work/445/envelope").resolve()))
sys.path.insert(0, "C:/Programs/f1Brainz")
import grip_iter as GI
G=GI.G
q=GI.H.load_session(2023,1,"Q")
for car in ["VER","HAM"]:
    runs=GI.H.driver_runs(q,car)
    # take the fastest/representative run
    run=max(runs,key=lambda r:len(r["V"]))
    tc=np.asarray(run["tc"]); V=np.asarray(run["V"])
    o=np.argsort(tc); tc=tc[o]; V=V[o]
    keep=np.concatenate([[True],np.diff(tc)>1e-9]); tc=tc[keep]; V=V[keep]
    dt=np.diff(tc)
    # native adjacent-sample decel
    dec_native = -np.diff(V)/dt/G
    # peak braking from native (only braking, dt sane)
    m=(dt>0)&(dt<0.5)
    dn=dec_native[m]
    # my windowed version (7-pt linear slope) for comparison
    W=3; dw=[]
    for i in range(W,len(V)-W):
        tt=tc[i-W:i+W+1]-tc[i-W]; vv=V[i-W:i+W+1]
        if tt[-1]-tt[0]>0: dw.append(-np.polyfit(tt,vv,1)[0]/G)
    dw=np.array(dw)
    print(f"{car}: native speed dt med {np.median(dt)*1000:.0f}ms ({1/np.median(dt):.1f}Hz), "
          f"min {dt.min()*1000:.0f}ms, n={len(V)}")
    print(f"   peak decel  native(adjacent): max {dn.max():.2f}g p99 {np.percentile(dn,99):.2f}g p95 {np.percentile(dn,95):.2f}g")
    print(f"   peak decel  my 7-pt window:   max {dw.max():.2f}g p99 {np.percentile(dw,99):.2f}g p95 {np.percentile(dw,95):.2f}g")
