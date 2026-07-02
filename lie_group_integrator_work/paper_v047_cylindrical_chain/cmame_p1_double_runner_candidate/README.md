# CMAME P1 Double-Runner Candidate

Status: double-example self-contained runner candidate for the P1 local
single/double extraction gate.

This directory contains a compact JAX implementation of the ASME
double-pendulum Gauss6/FullVA double-revolute row. It regenerates the three
local double-pendulum rows used in the paper matrix without importing
`run_v047.py`, `run_v048.py`, or `run_v029.py`.

Quickstart:

```bash
python3 scripts/run_double_pendulum_fullva.py
```

Expected terminal markers:

- `p1_double_runner_candidate=PASS`
- `example=double_pendulum`
- `rows=3`
- `p1_double_only_ready=True`
- `p1_complete=False`
- `imports_v047_v048_or_v029=False`
- `source_policy_external_superiority_allowed=False`
- `local_runner_proof_gap_closed=False`

Boundary:

- The script uses JAX for the dense automatic-differentiation Newton solve.
- It regenerates only the double-pendulum local Gauss6/FullVA rows for
  `h = 0.1, 0.05, 0.025` over `T = 0.1` against a local `h = 0.0125`
  self-reference.
- It does not close any source-policy external-superiority row.
- It does not close the global direct-PC2 Newton--Euler proof boundary; that is carried by the proof manifest, not this local runner.
