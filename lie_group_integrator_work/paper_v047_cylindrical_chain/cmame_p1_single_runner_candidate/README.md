# CMAME P1 Single-Runner Candidate

Status: single-example self-contained runner candidate, not a complete P1
runner package.

This directory contains a compact NumPy implementation of the driven
single-pendulum Gauss6/FullVA absolute-coordinate row used as the local
single-pendulum slice of the paper matrix. It is intended to reduce the
gap between replay-only evidence and a reviewer-runnable simulation package.

Quickstart:

```bash
python3 scripts/run_single_pendulum_fullva.py
```

Expected terminal markers:

- `p1_single_runner_candidate=PASS`
- `example=single_pendulum`
- `rows=3`
- `p1_single_only_ready=True`
- `p1_complete=False`
- `source_policy_external_superiority_allowed=False`
- `local_runner_proof_gap_closed=False`

Boundary:

- The script does not import `run_v047.py` or `run_v048.py`.
- It regenerates only the single-pendulum local Gauss6/FullVA rows for
  `h = 0.1, 0.05, 0.025` over `T = 0.1`.
- It does not extract the double-pendulum runner, so P1 remains open.
- It does not close any source-policy external-superiority row.
- It does not close the global direct-PC2 Newton--Euler proof boundary; that is carried by the proof manifest, not this local runner.
