# jingquan-autoresearch Workspace

This workspace is a research artifact tree. Most paths under
`lie_group_integrator_work/` are referenced by validators, reports, paper
sources, and generated JSON/CSV summaries. Prefer navigation/index cleanup
before moving files.

## Top-Level Map

| Path | Role | Move risk |
| --- | --- | --- |
| `lie_group_integrator_work/` | Main Lie-group integrator research pipeline, versions, paper package, validators, and ledgers. | High |
| `external/sbel-reproducibility/` | Local mirror of SBEL/Negrut public reproducibility code used by v046/v048. | High |
| `external/public-metadata/` | External metadata checkout used by source/code-path audits. | Medium |
| `s11044-026-10153-w.pdf` / `.txt` | Source/reference paper material for the current CMAME comparison context. | Medium |
| `1-s2.0-S0377042719305229-main.pdf` / `.txt` | Additional literature/source reference material. | Medium |
| `.agents/`, `.codex/` | Local agent/tooling context. | Low for research code, but leave in place. |

## Current Entry Points

- Research contract:
  `lie_group_integrator_work/CURRENT_PIPELINE_CONTRACT.md`
- Human status note:
  `lie_group_integrator_work/paper_v047_cylindrical_chain/CURRENT_STATUS_CN.md`
- Validation quickstart:
  `lie_group_integrator_work/VALIDATION_QUICKSTART.md`
- Folder map:
  `lie_group_integrator_work/FOLDER_MAP.md`
- Cleanup plan:
  `lie_group_integrator_work/FOLDER_CLEANUP_PLAN.md`

## Safe Cleanup Policy

1. Do not move `vNNN_*` directories, `paper_v047_cylindrical_chain/`,
   `pipeline_validation_results/`, or files named in `CURRENT_PIPELINE_CONTRACT.md`
   unless validators and references are updated in the same change.
2. Treat generated `results/` files as research evidence, not disposable build
   output.
3. `__pycache__/` directories can be removed after a validation pass if disk
   cleanup is needed.
4. Strict `1e-4` numerical reruns are opt-in only. Use read-only validators for
   routine checks.
