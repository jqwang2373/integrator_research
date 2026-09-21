from __future__ import annotations

import json
from pathlib import Path

import jax.numpy as jnp
import numpy as np

import run_v032 as v032


RESULTS = Path(__file__).resolve().parent / "results"


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    rows = []
    rng = np.random.default_rng(20260526)
    for case_name, vs in v032.CASES.items():
        params = v032.v029.make_params(vs)
        state = v032.v029.initial_state(params)
        x = v032.v029.stage_guess(state, v032.H, params, 3)
        args = v032.v031.build_args(state, v032.H, params)
        vec = rng.standard_normal(x.size)
        x_jax = jnp.asarray(x, dtype=jnp.float64)
        vec_jax = jnp.asarray(vec, dtype=jnp.float64)
        dense_jac = np.asarray(v032.v029.R3_FULL_JAC(x_jax, *args), dtype=float)
        dense_jv = dense_jac @ vec
        jvp_jv = np.asarray(v032.jvp3_full(x_jax, vec_jax, *args), dtype=float)
        diff = jvp_jv - dense_jv
        rows.append(
            {
                "case": case_name,
                "dimension": int(x.size),
                "dense_jv_norm": float(np.linalg.norm(dense_jv)),
                "diff_norm": float(np.linalg.norm(diff)),
                "relative_error": float(np.linalg.norm(diff) / max(np.linalg.norm(dense_jv), 1.0e-30)),
                "max_abs_error": float(np.max(np.abs(diff))),
            }
        )
    output = {"check": "v032 JVP vs dense Jacobian-vector product", "rows": rows}
    (RESULTS / "jvp_consistency.json").write_text(json.dumps(output, indent=2, sort_keys=True), encoding="utf-8")
    for row in rows:
        print(
            row["case"],
            "relative_error",
            f"{row['relative_error']:.3e}",
            "max_abs_error",
            f"{row['max_abs_error']:.3e}",
        )


if __name__ == "__main__":
    main()
