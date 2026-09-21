# VP2024 Code-Path Disposition Audit

Status: **ALL FOUR EXAMPLES CHECKED; NO DISTINCT PUBLIC CODE; UNABLE TO REPRODUCE; NOT PROMOTED**.

Examples checked: `single_pendulum, double_pendulum, four_link, slider_crank`.
Source-policy VP rows unresolved: `4/4`.
Source-policy VP rows attempted-not-reproducible/unable: `4/4`.
Final nonpublic-code disposition: `unable_to_reproduce_not_promoted`.
Common-reference proxy rows ok: `4/4`.
Common-reference proxy local velocity-order wins: `4/4`.
Common-reference proxy local finest-velocity-error wins: `4/4`.
Larger-step diagnostic local velocity-order wins: `4/4`.
Larger-step diagnostic local finest-velocity-error wins: `1/4`.
Distinct public VP code path found: `False`.
Proxy is source-policy reproduction: `False`.
Claim allowed now: `code-path-unresolved_related_work_only`.
Default `1e-4` required: `False`.
Heavy numerical run invoked: `False`.

## Four-Example Disposition

| example | source-policy status | common-ref local order | common-ref VP order | common-ref local velocity error | common-ref VP velocity error | local order win | local error win |
|---|---:|---:|---:|---:|---:|---:|---:|
| `single_pendulum` | `code_path_unresolved` | `5.80133` | `6.149e-15` | `1.155e-12` | `3.163e-11` | `True` | `True` |
| `double_pendulum` | `code_path_unresolved` | `6.0097` | `1.00005` | `2.346e-13` | `0.00216512` | `True` | `True` |
| `four_link` | `code_path_unresolved` | `6.08482` | `-5.332e-04` | `1.093e-11` | `1.087e-08` | `True` | `True` |
| `slider_crank` | `code_path_unresolved` | `7.34091` | `-3.253e-07` | `9.189e-12` | `1.332e-07` | `True` | `True` |

## Interpretation

The source-policy VP2024 rows are all unresolved because no distinct public velocity-partitioning code path has been located. The coordinate-partitioning proxy is useful for a finite-grid common-reference diagnostic, but it is not a source-policy reproduction of the paper's published code package.

The controlling apples-to-apples table is the common-reference matrix, where the local method wins all four VP proxy velocity-order rows and all four VP proxy finest-velocity-error rows. The older larger-step VP diagnostic remains noncontrolling and only preserves the warning that mixed-reference finest-error rows should not be used for a universal direct-error claim.

## Public Code Search

Search evidence rows: `18`.
Search evidence source: `../../numerics/v048_cross_paper_same_test_benchmarks/results/velocity_partitioning_code_search.csv`.
Public web search status: `no_distinct_repo_found`.
Public web search evidence rows: `1`.
GitHub code-search auth boundary: `True`.
V048 code-path summary status: `not_resolved_in_local_sbel_or_public_metadata_tree`.
Reference points to 2021 rA repo: `True`.
Distinct VP repo found: `False`.
2024 public repo directory names from the API spot check: `CPD, IROSImuGps, MNODE-code, PathFollowingSim2real, RSSworkshop`.
Local sbel-reproducibility top-level directories: `2021, 2022`.
Local visible MBD code roots: `2021/ASME/rA-formulation, 2021/ASME/rA-formulation/C2, 2022/HalfImplicit_JCND`.
Local velocity-partition search hits: `0`.
Local distinct VP2024 code path found: `False`.
