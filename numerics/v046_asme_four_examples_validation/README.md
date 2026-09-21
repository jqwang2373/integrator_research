# v046 ASME Four Examples Validation

This version validates the SBEL/Negrut 2021 ASME `rA` formulation on all four
example mechanisms in the reproducibility repository:

- single pendulum;
- double pendulum;
- four link;
- slider crank.

It uses the upstream C2 code path with runtime compatibility patches only. The
validation compares rA dynamics against a nested fine reference and records
trajectory errors, observed orders, constraint norms, SO(3) orthogonality, and
Newton iterations.

Run:

```bash
../.venv_sbel/bin/python run_v046.py
```

Outputs:

- `results/v046_report.md`
- `results/summary_v046.json`
- `results/asme_four_examples_validation.csv`
- `results/asme_four_examples_orders.png`
- `results/asme_four_examples_invariants.png`
