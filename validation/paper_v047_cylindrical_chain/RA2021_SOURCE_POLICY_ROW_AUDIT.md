# RA2021 Source-Policy Row Audit

Status: **public rows complete; source-policy rows not closed**.

This audit is read-only over existing v048 and paper-package artifacts. It does not rerun RA2021.

- Active B2 flagged RA2021 rows: `0`.
- Public order groups completed: `12/12`.
- Public timing rows completed: `12/12`.
- Fixed-grid common-reference RA2021 rows: `12/12`.
- Paper-safe common-reference RA2021 rows: `12/12`.
- Source-policy reproduction rows: `0/12`.
- Per-row source-identity requirements resolved: `3`.
- Per-row source-policy promotion requirements remaining: `4`.
- Row missing evidence shrunk by identity audit: `True`.
- Source-policy closed rows: `0`.
- External-superiority-ready rows: `0`.
- Position-aligned velocity-mismatch rows in RA2021 forensic table: `9`.
- Velocity nonmonotone/floor-limited rows in RA2021 forensic table: `1`.
- Source output mapping verified from RA2021 source: `True`.
- Source time-grid policy extracted from RA2021 source: `True`.
- Closed-loop same-window public work/precision: `same_window_public_work_precision_available_reference_caveat_not_external_superiority`, available `2/2`, strict common-reference `False`, external superiority `False`, source-policy rows closed `0`.
- External superiority claim allowed: `False`.
- Default 1e-4/heavy/run_v047: `False/False/False`.
- Isolated double source-policy candidate plan: `executed_isolated_source_policy_candidate`, contract `True`, reference `ok`, JAX-safe small-angle patch `True`, rows completed `3/3`, order accepted `False`, estimated reference steps `30000`.
- Isolated double low-order diagnosis: `diagnosis_only_low_order_floor_limited_not_promoted`, fine pair floor-limited `True`, coarse h constraint threshold `False`, constraint failure components `['endpoint_velocity_constraint']`, fine-pair floor margin `0.176`, finest/reference h ratio `10.0`, rows promoted `0`.

## Local Candidate Feasibility

| example | local candidate status | key available rows | promotion blocker |
|---|---|---:|---|
| `single_pendulum` | `not_promoted_floor_limited_public_h_tranche` | `3` | floor-limited public-h tranche |
| `double_pendulum` | `not_promoted_coarse_h_and_reference_policy_mismatch` | `3` plus isolated exact candidate | isolated exact rows complete but low-order |
| `four_link` | `not_promoted_true_dynamic_not_source_policy_and_public_horizon_not_dynamic_order` | `3` plus same-window public work/precision | mixed-reference diagnostic, not source-policy promotion |
| `slider_crank` | `not_promoted_true_dynamic_not_source_policy_and_public_horizon_not_dynamic_order` | `3` plus same-window public work/precision | mixed-reference diagnostic, not source-policy promotion |

## Closure Decision

Can close RA2021 B2 requirement now: `False`.

RA2021 public order/timing rows are complete and useful as bounded common-reference evidence, and the source-code identity audit now verifies body.r/body.dr/body.ddr output mapping and extracts the public time-grid convention. Local Gauss6/FullVA candidate rows exist for single pendulum, double pendulum, and the two closed-loop examples, but they are respectively floor limited, coarse h/reference-policy rows, or bounded T=0.1 true-dynamic rows rather than promoted RA2021 source-policy dynamic-order rows. The closed-loop same-window public work/precision artifact closes the availability gap for bounded diagnostics, but mixed reference families prevent external-superiority promotion; the error/runtime/Newton policy binding is also not closed.

## Promotion Gap Drilldown

- Checked examples: `4`.
- Checked active B2 rows: `0`.
- Closed-loop same-window public work/precision checked: `True`.
- Closed-loop same-window source-policy rows closed: `0`.
- Source identity closed: `True`.
- Source-policy promotion closed: `False`.

| example | source-policy target | local candidate | promotion gap |
|---|---|---|---|
| `single_pendulum` | $T=3$, $h=\{10^{-2},10^{-3},10^{-4}\}$ | same grid, $v$ order `2.556`, finest $v$ error `7.012e-15` | floor-limited public-h tranche |
| `double_pendulum` | $T=3$, $h=\{10^{-2},2\cdot10^{-3},10^{-3}\}$, $h_{ref}=10^{-4}$ | $h=\{0.1,0.05,0.025\}$, $h_{ref}=0.0125$, $v$ order `7.042`; isolated exact rows `3/3` | isolated exact rows complete; observed order is below acceptance |
| `four_link` | $T=3$ public-horizon dynamic-order row | $T=0.1$, $h=\{0.1,0.05,0.025\}$, $v$ order `6.085` | bounded same-window public work/precision available, but mixed-reference diagnostic only |
| `slider_crank` | $T=3$ public-horizon dynamic-order row | $T=0.1$, $h=\{0.1,0.05,0.025\}$, $v$ order `7.341` | bounded same-window public work/precision available, but mixed-reference diagnostic only |

## Active Rows

| # | example | method | fixed-grid | paper-safe | source-policy | issues |
|---:|---|---|---:|---:|---:|---|

Each active RA2021 row now carries the resolved source-identity evidence separately from the still-open promotion evidence.
The RA2021 rows remain bounded common-reference diagnostics, not external-superiority evidence.
The previous output-mapping unknown is closed as a source-identity question; source-policy promotion remains open.
