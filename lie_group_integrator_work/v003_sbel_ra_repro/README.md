# v003 SBEL rA Reproduction Smoke Tests

This version keeps the upstream SBEL source unchanged and runs a local harness
against:

`../../external/sbel-reproducibility/2021/ASME/rA-formulation/C2`

Purpose:
- verify that the Dan Negrut/SBEL rA code path is executable in a modern Python
  environment;
- record compatibility fixes needed for current NumPy/Python packages;
- establish a baseline before replacing or augmenting the rA rotation update
  with higher-order Lie group candidates.

Local environment:
- `../.venv_sbel` created with `uv`
- packages: numpy, scipy, sympy, matplotlib

Run:

```bash
env MPLCONFIGDIR=/tmp/mplconfig PYTHONPATH=../../external/sbel-reproducibility/2021/ASME/rA-formulation/C2 ../.venv_sbel/bin/python run_v003.py
```

The script writes CSV/JSON/Markdown outputs under `results/`.
