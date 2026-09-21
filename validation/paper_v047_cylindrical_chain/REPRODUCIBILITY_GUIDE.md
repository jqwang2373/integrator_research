# Reproducibility Guide

Status: human-runnable replay structure for the bounded common-reference
results, not an experiment campaign.

The quickest path for a reader is `python3 run_human_reproducibility.py`.
It reproduces the recorded 44-row matrix covering four examples and eleven
methods from embedded artifacts, writes a markdown result table, and checks
that no source-policy superiority or submission-ready claim is promoted. It
carries the current direct-PC2 residual-bridge proof-closure artifact. To also
rerun the self-contained local single- and double-pendulum Gauss6/FullVA
candidate scripts, replay-check the four-link/slider-crank local closed-loop
rows, and run the compact self-contained closed-loop candidate, use
`python3 run_human_reproducibility.py --include-local-runners`.

This directory currently separates seven roles:

1. `PAPER_CORE_RESULT_CONSOLIDATION.md`
   - canonical non-policy paper-core result map;
   - summarizes four-example local order, common-reference comparison wins, closed-loop true-dynamic coarse evidence, core figures, proof boundary, and submission boundary;
   - generated from existing artifacts only.

2. `cmame_minimal_reproducibility_candidate/`
   - smallest reviewer-facing replay package;
   - one Python script, embedded result/proof/review artifacts;
   - verifies the 44-row paper matrix, 11 methods, four examples, `40/40` common-reference order/error wins, direct proof closure true, and submission-ready boundary false.

3. `cmame_runner_adapter_candidate/`
   - compact adapter package around the paper matrix and v048 report artifacts;
   - one Python script;
   - checks embedded common-reference summaries and can optionally call a local v048 report-only runner, but the default run does not call external code.

4. `cmame_p1_single_runner_candidate/` and `cmame_p1_double_runner_candidate/`
   - self-contained runners for the local single- and double-pendulum Gauss6/FullVA rows;
   - regenerate all six P1 local rows for `h = 0.1, 0.05, 0.025`;
   - do not import `run_v047.py`, `run_v048.py`, or `run_v029.py`;
   - close the P1 local single/double runner extraction gate, but not source-policy or proof gates.

5. `cmame_closed_loop_local_runner_candidate/`
   - compact self-contained closed-loop runner candidate for four-link and slider-crank local Gauss6/FullVA rows;
   - regenerates six closed-loop local rows without importing `run_v046.py`, `run_v047.py`, `run_v048.py`, or `run_v029.py`;
   - passes the compact B6 closed-loop local runner gate while keeping source-policy rows closed at `0/40`.

6. `cmame_local_accepted_runner_companion/`
   - small launcher/index for the minimal replay and all four local accepted-row runner candidates;
   - preserves the minimal replay-only boundary while exposing one command for the existing self-contained runner packages;
   - keeps source-policy rows closed at `0/40`, full source-policy runner package ready `False`, and submission ready `False`.

7. Full research audit tree
   - all `build_*.py`, `validate_*.py`, v047/v048 runners, source-policy ledgers, proof audits, and paper-package validators;
   - useful as provenance, but too large and noisy as reviewer-facing primary code.

## One-Command Core Replay

From this directory:

```bash
python3 run_human_reproducibility.py
```

This is the most direct human-facing entry point. It runs the bounded
common-reference replay, prints the four-example/eleven-method result table,
and writes `human_reproducibility_result_table.md`. It does not launch a
numerical campaign or invoke `run_v047.py`/`run_v048.py`.

Expected boundary:

- examples/methods/matrix rows: `4/11/44`;
- common-reference order/error wins: `40/40`, `40/40`;
- source-policy external rows closed: `0/40`;
- source-policy external superiority allowed: `False`;
- direct-PC2 residual-bridge proof gap closed: `True`;
- proof gap scope: `direct_residual_bridge_kantorovich_route_closed_primitive_taylor_conditional_schema_open`;
- Newton-Euler symbolic defect certificate complete: `False`;
- submission ready: `False`.

For an opt-in local numerical smoke that still stays inside the bounded
non-source-policy claim boundary:

```bash
python3 run_human_reproducibility.py --include-local-runners
```

This runs the replay table and then directly invokes:

- `cmame_p1_single_runner_candidate/scripts/run_single_pendulum_fullva.py`;
- `cmame_p1_double_runner_candidate/scripts/run_double_pendulum_fullva.py`.
- `cmame_runner_adapter_candidate/scripts/replay_closed_loop_local_rows.py`.
- `cmame_closed_loop_local_runner_candidate/scripts/run_closed_loop_fullva_candidate.py`.
- `cmame_local_accepted_runner_companion/scripts/run_local_accepted_runner_companion.py`.

Expected additional boundary:

- local runners invoked: `True`;
- closed-loop local replay invoked: `True`;
- experiments launched: `local_p1_single_double_plus_closed_loop_replay`;
- P1 local single/double rows regenerated: `6/6`;
- closed-loop local four-link/slider-crank rows replayed: `6/6`;
- compact closed-loop self-contained candidate rows regenerated: `6/6`;
- local accepted-row runner companion rows checked: `12/12`;
- source-policy external rows closed: `0/40`;
- direct-PC2 residual-bridge proof gap closed: `True`;
- proof gap scope: `direct_residual_bridge_kantorovich_route_closed_primitive_taylor_conditional_schema_open`;
- Newton-Euler symbolic defect certificate complete: `False`;
- submission ready: `False`.

For the full smoke suite:

```bash
bash run_reproduction_smoke.sh
```

This runs the human-facing replay table, the core paper replay, the minimal
package replay, the runner-adapter embedded check, the closed-loop local
four-link/slider-crank replay, the compact closed-loop local runner candidate,
the P1 single/double runner candidates, and the package validators without
launching a full numerical campaign.

For the core replay alone:

```bash
python3 replay_reproducibility_core.py
```

Expected boundary:

- experiments launched: `False`;
- `run_v047.py` invoked: `False`;
- `run_v048.py` invoked: `False`;
- embedded matrix rows: `44`;
- methods/examples: `11/4`;
- common-reference order/error wins: `40/40`, `40/40`;
- source-policy external rows closed: `0/40`;
- direct-PC2 residual-bridge proof gap closed: `True`;
- proof gap scope: `direct_residual_bridge_kantorovich_route_closed_primitive_taylor_conditional_schema_open`;
- Newton-Euler symbolic defect certificate complete: `False`;
- submission ready: `False`.

## Human-Readable Result Replay

To reproduce the reviewer-facing result table from the embedded artifacts
without launching a numerical campaign:

```bash
python3 replay_reproducibility_core.py --table
```

To write the same replay table as markdown:

```bash
python3 replay_reproducibility_core.py --table --markdown-report /tmp/cmame_replay_result_table.md
```

The table enumerates all four examples and the eleven recorded methods:
`local_Gauss6_FullVA`, `hi2022_rA`, `hi2022_rA_half`, `ra2021_rA`,
`ra2021_reps`, `ra2021_rp`, `tfe2026_Newmark_beta`, `tfe2026_TFE_m1`,
`tfe2026_TFE_m2`, `tfe2026_trapezoidal`, and
`vp2024_coordinate_partitioning_rA`. Each row reports position order,
velocity order, finest velocity error, claim scope, and whether the row is a
source-policy-closed row. This is a compact reproduction of the bounded
common-reference result matrix; it is not a rerun of the source-paper
benchmarks.

For the smallest standalone replay package:

```bash
cd cmame_minimal_reproducibility_candidate
python3 scripts/replay_paper_matrix.py
```

For the compact adapter that checks both the paper matrix and embedded v048
common-reference summaries:

```bash
cd cmame_runner_adapter_candidate
python3 scripts/run_four_example_matrix_adapter.py
```

Optional local v048 report-only replay, if the adjacent v048 tree is present:

```bash
cd cmame_runner_adapter_candidate
python3 scripts/run_four_example_matrix_adapter.py --external-v048-root ../../v048_cross_paper_same_test_benchmarks
```

For the self-contained single-pendulum numerical candidate:

```bash
cd cmame_p1_single_runner_candidate
python3 scripts/run_single_pendulum_fullva.py
```

Expected boundary:

- single-pendulum candidate rows: `3/6` P1 local rows;
- `p1_single_only_ready=True`;
- `p1_complete=False`;
- source-policy external superiority allowed: `False`;
- local-runner proof closure by this candidate: `False`;
- paper proof artifacts close only the direct-PC2 residual-bridge proof gap: `True`.

For the self-contained double-pendulum numerical candidate:

```bash
cd cmame_p1_double_runner_candidate
python3 scripts/run_double_pendulum_fullva.py
```

Expected boundary:

- double-pendulum candidate rows: `3/6` P1 local rows;
- combined P1 local single/double rows: `6/6`;
- `p1_double_only_ready=True`;
- `p1_complete=False`;
- source-policy external superiority allowed: `False`;
- local-runner proof closure by this candidate: `False`;
- paper proof artifacts close only the direct-PC2 residual-bridge proof gap: `True`.

For the local accepted-row runner companion:

```bash
cd cmame_local_accepted_runner_companion
python3 scripts/run_local_accepted_runner_companion.py
```

Expected boundary:

- minimal replay boundary preserved: `True`;
- self-contained examples: `single_pendulum,double_pendulum,four_link,slider_crank`;
- local accepted-row checks: `12/12`;
- source-policy external rows closed: `0/40`;
- full source-policy runner package ready: `False`;
- submission ready: `False`.

## Claim Boundary

The replay structure supports the non-policy paper core:

- four-example local order evidence for `Gauss6/FullVA`;
- common-reference comparison against accepted runnable rows;
- self-contained regeneration of the single- and double-pendulum local Gauss6/FullVA rows;
- traceability between result tables and manuscript artifacts;
- explicit proof and submission-readiness boundaries.
- D5 `P_acc` PA2 weighted-inverse diagnostics, recording finite control of
  `h delta A` while keeping the primitive/Taylor unweighted acceleration lift,
  PA2, and PC2 route open.
- finite D5 `P_lambda` multiplier-column rank evidence, without claiming a
  uniform inf-sup theorem or closing PC2.
- D5 `P_lambda` PL2 geometric-margin route evidence, with finite
  dynamic-lambda, translational normal-force, rotational axis-torque, and
  direct-sum margin diagnostics but no compact-tube inf-sup closure.
- D5 `P_lambda` non-circular D3-use evidence closing PL3 only, while PL2,
  PL4, `P_lambda`, and primitive/Taylor-route PC2 remain open.

It does not support these claims:

- strict source-paper policy superiority;
- source-policy apples-to-apples closure;
- completed Newton-Euler symbolic defect certificate or residual-to-error theorem;
- submission-ready status.

## Reviewer-Facing Code Policy

The primary reviewer-facing structure should stay small:

- prefer one replay script plus data artifacts;
- keep full audit and experiment runners as provenance only;
- do not include default numerical campaigns in the replay entrypoint;
- keep optional external runners opt-in and visibly labeled.
