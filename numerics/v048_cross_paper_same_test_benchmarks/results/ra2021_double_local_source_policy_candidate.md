# RA2021 Double Local Source-Policy Candidate

Status: **executed_isolated_source_policy_candidate**.

This artifact is isolated from the existing coarse double-pendulum rows.
It does not update the canonical coarse CSV and does not close source-policy rows.

- Execution phase: `candidate`.
- Source-policy contract selected: `True`.
- Step sizes: `[0.01, 0.002, 0.001]`.
- Reference h: `0.0001`.
- T end: `3.0`.
- Estimated reference steps: `30000`.
- Estimated candidate steps: `[300, 1500, 3000]`.
- Reference cache exists: `True`.
- Reference cache: `ra2021_double_local_source_policy_candidate_reference_h0p0001_T3.npz`.
- Reference checkpoint exists: `True`.
- Reference checkpoint step: `None`.
- Reference completed: `True`.
- Reference status: `ok`.
- Reference failure kind: `None`.
- Reference failure message: `None`.
- JAX-safe small-angle patch enabled: `True`.
- JAX-safe small-angle patch id: `isolated_v013_jax_safe_small_angle_taylor_v1`.
- Rows completed in this artifact: `3`.
- Promotion ready: `False`.
- Canonical coarse output untouched by this writer: `True`.

Required before promotion:

- execute the exact h_ref=1e-4 reference and three candidate rows
- bind the error norm and output mapping to the RA2021 source policy
- bind runtime and Newton-iteration policy to the accepted rows
- produce an independent rerun or verification artifact
