import sys; from pathlib import Path; import numpy as np
sys.path.insert(0,"C:/Programs/f1Brainz"); sys.path.insert(0, str(Path(".agent-work/445/envelope").resolve()))
import grip_iter as GI
from src.preprocessing.trajectory.calibration import heldout_chi2_full, fit_stint_hp, session_offset
q=GI.H.load_session(2023,1,"Q")
runs=GI.H.driver_runs(q,"VER")
r=max(runs,key=lambda r:len(r["X"]))
tp=np.asarray(r["tp"],float);X=np.asarray(r["X"],float);Y=np.asarray(r["Y"],float)
tc=np.asarray(r["tc"],float);V=np.asarray(r["V"],float)
print("MY hardcoded HPs (ell=2, sf=100, sig_pos=0.3, delta=0.06):")
cp,cs,np_,ns=heldout_chi2_full(2.0,100.0,0.3,0.06,tp,X,Y,tc,V,iters=3)
print(f"  chi2_pos={cp:.2f}  chi2_spd={cs:.2f}   (target=1.0; >>1 = over-trusting/noise-leak)")
d,diag=session_offset([(tp,X,Y,tc,V)])
print(f"\nCalibrated session delta = {d:.3f}s  (I assumed 0.06)  grid-scores n_win={diag['nwin']}")
hp=fit_stint_hp(tp,X,Y,tc,V,delta=d,iters=3)
print(f"\nCalibrated HPs (fit_stint_hp, chi2-target):")
print(f"  ell={hp['ell']:.2f}  sf={hp['sf']:.0f}  sig_pos={hp['sig_pos']:.2f}m  delta={hp['delta']:.3f}")
print(f"  chi2_pos={hp['chi2_pos']:.2f}  chi2_spd={hp['chi2_spd']:.2f}  (both -> ~1 if clean)")
