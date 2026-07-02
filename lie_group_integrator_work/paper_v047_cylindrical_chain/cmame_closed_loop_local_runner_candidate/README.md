# CMAME Closed-Loop Local Runner Candidate

Compact executable candidate for the B6 closed-loop local rows.

Run from this directory:

```bash
python3 scripts/run_closed_loop_fullva_candidate.py
```

Expected markers:

- `cmame_closed_loop_local_runner_candidate=PASS`
- `rows_ok=6/6`
- `models=four_link,slider_crank`
- `source_policy_external_superiority_allowed=False`

Boundary:

- regenerates six local four-link/slider-crank closed-loop rows;
- does not import `run_v046.py`, `run_v047.py`, `run_v048.py`, or `run_v029.py`;
- does not run source-policy external benchmarks;
- keeps source-policy external rows closed at `0/40`;
- does not make the paper submission ready.
