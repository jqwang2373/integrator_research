#!/usr/bin/env python3
"""One-off: the regular-branch factor n_1 . a_1(q) along the smooth chain trajectory (Incident 3).

Runs the accepted implementation at h = 0.005 until Newton fails (t ~ 0.605) and stores t and the
factor in figures/branch_factor.npz, so make_figures.py does not need JAX.  Takes about a minute.
"""
import sys, pathlib, numpy as np
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent / "numerics" / "v049_paper_experiments"))
import common  # noqa: E402

params = common.smooth_params()
traj = common.integrate_trajectory(params, 0.005, 0.7)
bf = np.array([common.branch_factor(params, traj.r[k], traj.p[k]) for k in range(len(traj.t))])
np.savez(HERE / "figures" / "branch_factor.npz", t=traj.t, factor=bf, converged=traj.converged, failure=traj.failure,
         newton=traj.newton_iterations)
print("steps done", traj.steps, "last t", traj.t[-1], "converged", traj.converged, "| failure:", traj.failure[:120])
print("factor at t=0:", bf[0], " at 0.5:", bf[min(100, len(bf)-1)], " min:", bf.min(), " last:", bf[-1])
