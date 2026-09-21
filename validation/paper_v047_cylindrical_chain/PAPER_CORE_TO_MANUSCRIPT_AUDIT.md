# Paper Core To Manuscript Audit

Status: **paper core results visible in TeX/PDF**.

- Core result status: `paper_core_results_consolidated_replay_only`.
- Main TeX/PDF values present: `True`.
- Main TeX/PDF structure present: `True`.
- Flat TeX/PDF core present: `True`.
- Paper-core traceability closed: `True`.
- Experiments launched: `False`.
- Submission ready: `False`.

## Value Checks

| label | main TeX | main PDF |
|---|---:|---:|
| `single_pendulum_order_error` | `True` | `True` |
| `double_pendulum_order_error` | `True` | `True` |
| `four_link_order_error` | `True` | `True` |
| `slider_crank_order_error` | `True` | `True` |
| `closed_loop_four_link_true_dynamic` | `True` | `True` |
| `closed_loop_slider_crank_true_dynamic` | `True` | `True` |
| `source_policy_boundary` | `True` | `True` |

## Structure Checks

| label | main TeX | main PDF |
|---|---:|---:|
| `common_reference_pack_table` | `True` | `True` |
| `all_method_matrix_table` | `True` | `True` |
| `strict_common_reference_figure` | `True` | `True` |
| `closed_loop_true_dynamic_figure` | `True` | `True` |
| `all_method_result_matrix_figure` | `True` | `True` |

Reading rule: this audit checks paper visibility for the non-policy core result map. It does not authorize source-policy superiority, proof closure, or submission-ready claims.
