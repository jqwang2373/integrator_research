# numerics

The integrator implementation, every numerical result reported in the paper, the cross-paper
benchmark harness, and the development history. One directory per version; nothing is
overwritten, new work gets a new `vNNN_*` directory.

| Path | Role |
| --- | --- |
| `v047_cylindrical_chain_pipeline/` | **The accepted method (Gauss6/FullVA)**: `run_v047.py` is the residual, Jacobian and Newton solver for the cylindrical chain and the four ASME examples; `results/` holds the convergence sweeps, ASME gates, closure diagnostics and `v047_report.md`; `validate_v047_outputs.py` checks them. Do not run `run_v047.py` as a routine check (it is the full historical campaign, hours long); the validators are read-only. |
| `v048_cross_paper_same_test_benchmarks/` | Cross-paper same-test benchmark layer: public RA2021 / HI2022 baselines, TFE proxies, common-reference order tables, work/precision curves (`run_v048.py`, `results/`). No external superiority claim; source-policy rows are `0/40`. |
| `reproduction/` | Human-runnable rebuild of the summary tables from the checked v047/v048 artifacts (`run_reproduction.py`, no heavy generators). |
| `v001_…` – `v046_…` | Development history: SO(3) benchmarks, Lie-group DAE prototypes, friction laws, sparse Jacobians, lower-pair mechanisms, the four-ASME anchor. Each has its own `README.md` and `results/`. Indexed in `../validation/docs/VERSION_LEDGER.md` and `VERSION_TREE.md`. |
| `scratch_v046_cylindrical_chain_pending/` | Historical scratch context for v046. |

## Running

The Python environment is the `uv` virtualenv at the repository root (`../.venv_sbel`, Python 3.11,
jax 0.10). From a version directory:

```bash
../../.venv_sbel/bin/python validate_v047_outputs.py          # read-only checks of results/
../../.venv_sbel/bin/python run_v048.py --help                # benchmark harness (coarse-first by default)
```

Strict public-policy `h = 1e-4` reruns and the B4 source-policy campaign are opt-in only; the rules
and the exact approval sentence are in `../validation/CURRENT_PIPELINE_CONTRACT.md`.

## Relation to the other folders

- `../paper/` cites these results through the records in `../validation/paper_v047_cylindrical_chain/`
  (result matrices, gates, traceability audits), never directly.
- `../proof/` formalizes the algebra of the residual implemented in `run_v047.py`
  (`residual_cylindrical_chain`, `R_VALUE`, `R_JAC`); the row transcription is documented there.
- `../external/` holds the public code the benchmarks compare against.
