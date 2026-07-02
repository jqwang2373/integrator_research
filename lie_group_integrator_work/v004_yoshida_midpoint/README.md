# v004 Yoshida-Composed Lie Midpoint

Purpose: test a higher-order structure-preserving candidate for mechanical
rigid-body dynamics while keeping the v002 prescribed-omega SO(3) benchmark for
continuity.

Main new method:
- `lie_midpoint_yoshida4`: symmetric fourth-order Yoshida/triple-jump
  composition of the second-order implicit Lie midpoint step.

Why this version matters:
- v002 showed that CF4/RKMK4 give fourth-order orientation accuracy for
  prescribed angular velocity, but do not settle long-time mechanical structure.
- v003 showed the SBEL/Negrut rA baseline is reproducible and approximately
  first order in the tested dynamics metrics.
- v004 checks whether a simple geometric composition can combine high order with
  the excellent invariant behavior of Lie midpoint on a conservative rigid body.

Expected caveat:
- Yoshida composition uses a negative substep. That is acceptable for smooth
  conservative tests, but it is a serious warning sign for nonsmooth friction,
  impacts, and dissipative contact models.

Run with the local uv environment:

```bash
../.venv_sbel/bin/python run_v004.py
```

Results are written under `results/`.
