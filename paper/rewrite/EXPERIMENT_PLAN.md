# Numerical experiments for the rewrite

Status: proposal for review (2026-09-20). Costs are estimated from the measured v047 runtimes
(smooth chain: 25 ms per Gauss6 step on this machine; ASME double pendulum ≈ 7 s per run).

All experiments are standalone scripts under `numerics/v049_paper_experiments/` that import the
accepted residual/Jacobian/Newton path from `v047_cylindrical_chain_pipeline/run_v047.py` (as the
existing identity and constants checks already do) and write `results/E*.csv/json/png`. They never
touch `run_v047.py`'s campaign entry point. Each result table in the paper is generated from these
files by a small script, so the numbers cannot drift from the data.

| Id | Question the reader asks | Setup | Existing assets | New work | Cost |
| --- | --- | --- | --- | --- | --- |
| E1 | Is it really sixth order, and over a real horizon? | Smooth chain (Stribeck 0.5), `T = 1`, `h ∈ {0.1, 0.05, 0.025, 0.0125, 0.00625, 0.003125}`, reference `h_ref = 2.5e-4` with Richardson check (`h_ref` vs `2 h_ref` difference reported). Errors: position, orientation (geodesic), velocity, angular velocity, position/velocity constraint norms, reaction forces. Fit slopes over the asymptotic triples and report the full table. | `run_v047.py` stepping functions; existing 3-step sweep at `T = 0.08` | script + plot | 6 runs ≤ 320 steps + reference 4000 steps ≈ 3 min |
| E2 | Does the sixth-order method pay for itself? | Gauss family on the same chain and horizon: 1-stage (implicit midpoint, order 2), 2-stage (order 4), 3-stage (order 6) with the same FullVA stage system and endpoint reconstruction. Work = wall time and Newton iterations; precision = position error at `T = 1`. | checked: the residual, stage layout, predictor and endpoint weights all read the module constant `N_STAGES` (458 uses); the only literal-3 code is in the TFE audit paths, which E2 does not call | run the residual with `N_STAGES` overridden at import (environment variable or module reload) for 1 and 2 stages; ≤ 50 lines | ≈ 10 min |
| E3 | When does friction break the order? | Stribeck velocity sweep `v_s ∈ {0.5, 0.2, 0.1, 0.05, 0.02}`, `T = 1`, four step sizes each; report observed order and the smallest `h` at which order 6 is recovered; relate to the `h_0` measurement of the P2 lemma. | v014 sweep (fixed-pivot pendulum), v047 sharp case | script; reuse E1 driver | 20 runs ≈ 10 min |
| E4 | Does it hold on standard benchmarks, including closed loops? | Four ASME mechanisms (single pendulum, double pendulum, four-link, slider-crank) with the public rA initial conditions, `T = 1` (pendulums) and `T = 0.5` (closed loops), five step sizes, reference `h_ref = 5e-4`. Same error set as E1 plus loop-closure constraint norm. | v047 ASME method runs (`T = 0.2`, three step sizes), v048 closed-loop coarse dynamic-order rows (`T = 0.1`); `run_public_closed_loop_shard.py` already takes `--t-end`, `--reference-h`, `--step-sizes` | extend horizons and step sets; pendulum runners via `integrate_v027/v029_with_asme_*` in `run_v047.py` | ≈ 30 min |
| E5 | How does it compare with a public absolute-coordinate method? | Work/precision on the four ASME mechanisms against the public 2021 rA formulation code (order 1 in velocity, order 2 in position as measured) and, on the pendulums, against the 2022 half-implicit code, all on identical initial conditions and horizons, errors against a common fine reference. | v048 common-reference tables (`common_reference_error_summary`, `ra2021_*`, `hi2022_*`), timing rows | assemble; rerun only where horizons differ from E4 | ≈ 20 min if reusing |
| E6 | Is it stable over long times? | Smooth chain, `T = 20`, `h = 0.01`: constraint norms (position/velocity/acceleration level), energy and angular-momentum drift for the frictionless variant, Newton iterations per step. | frictionless variant already parameterized (`mu_s = mu_d = c_v = 0`); no energy/momentum helper exists for the chain | script plus a 30-line kinetic + potential energy and angular-momentum evaluator from `masses`, `Js`, `gravity` | 2000 steps ≈ 1 min |
| E7 (optional) | Is the identity visible numerically? | One line in the text plus a figure inset: reduced collocation defects at converged stages are `≤ 1e-14` (already measured). | `EXACT_STAGE_IDENTITY_NUMERICAL_CHECK` | none | 0 |

Reference-solution policy (stated once in the paper): every error is measured against a Gauss6
run at `h_ref`, with the Richardson difference between `h_ref` and `2 h_ref` reported in the table;
a fitted order is quoted only for step pairs whose errors exceed that difference by a factor of 100.

What is dropped from the current manuscript: the `T = 0.08` three-step sweep (superseded by E1),
the TFE formula-proxy comparisons and all "same-test policy" material (replaced by E5 with public
code only), the tolerance-regime sweep (folded into one sentence: the `c_η h^7` stopping rule was
exercised and gives the same slopes as a fixed `1e-10` tolerance).

## Order of work once approved

1. E1 + E6 driver (shared stepping loop, reference cache) → F3, F8, T5.
2. E2 (check `N_STAGES` generality first).
3. E3 → F5.
4. E4 → F6, T6; E5 assembly → F7, T7.
5. Manuscript rewrite section by section against the new figures; Lean table and constants table
   carried over; arXiv version regenerated.
6. New lightweight validator; ledger frozen with a pointer in `validation/README.md`.

## Execution record (2026-09-21)

Design changes after the first runs (user decision "A": keep the implementation, document the limit):

- **Horizon.** The implemented second frozen-basis pair carries the factor `n_1 · a_1(q)`, which
  vanishes at `t ≈ 0.605` on the benchmark initial state (minimum `0.34` on `[0, 0.5]`). Newton
  fails there at every `h`; this is the end of the regular branch of the frozen sliding direction,
  not a numerical failure. All chain experiments (E1, E2, E3, E6) therefore use `T = 0.5`; the
  `T = 20` long-time study is dropped and E6 becomes a regular-branch check over `[0, 0.5]`. The
  paper states the limit in the modelling section and in Limitations.
- **Orientation error.** The geodesic angle is evaluated from the quaternion chord
  (`2 asin(|p ∓ q|/2)`), not from `2 acos(p·q)`, whose resolution floor is `3e-8` rad.
- **E4.** Three of the four public mechanisms (single pendulum, four-link, slider-crank) are
  kinematically driven; Gauss6/FullVA reproduces them at roundoff (`≤ 1e-13`) for every `h`, so
  no order is fitted there and they are reported as consistency rows. The double pendulum is the
  only genuine dynamics test. The single pendulum uses the analytic driven state as reference; the
  old v027/v029 harnesses need the v048 AD-safe small-angle patch below `h ≈ 1e-3`; `T = 1` for all
  four.
- **E5.** Restricted to what can be measured against one common reference: the double pendulum on
  the public horizon `T = 3` against the cached local `h = 1e-4` reference (30 000 steps), with the
  2021 public rA/rp/reps and the 2022 half-implicit rA/rA_half codes replayed on `t_i = i h`; a
  `T = 0.1` model-alignment check; plus the driven-mechanism rows assembled from the v048 files.
  Wall-time comparisons across implementations are labelled indicative.

Results (files under `numerics/v049_paper_experiments/results/`):

| Id | Result | File |
| --- | --- | --- |
| E1 | fitted final-state orders (5 asymptotic points, floor `3e-15`): position 6.25, orientation 6.28, velocity 6.11, angular velocity 6.27; position error `2.8e-4 → 1.2e-13` over `h = 0.1 → 0.003125`; position-constraint norm `≤ 1e-7` at `h = 0.1`, `3e-15` at the finest step; velocity-constraint norm `≤ 1e-13` throughout; 5.7–6.0 Newton iterations per step | `E1_convergence.*` |
| E2 | fitted position orders 2.10 / 4.17 / 6.25 for 1 / 2 / 3 stages; Newton iterations per step identical (5.7–6.0) across the family, wall time per step nearly identical (Python/JAX overhead dominates the dense 44/88/132 solves), so at equal work the 3-stage member is 4–7 orders of magnitude more accurate at `h ≤ 0.0125`; first row of each family includes JIT compilation | `E2_gauss_family.*` |
| E3 | fitted position orders 6.25 / 4.84 / 4.74 / 3.66 / 2.47 for `v_s = 0.5 / 0.2 / 0.1 / 0.05 / 0.02`; the finest pairwise orders return to 5.3–6.7 for every `v_s`; the Neumann threshold `h_0` falls from `7.6e-4` to `7.1e-6` while the observed order-recovery step falls from `0.1` to `≈ 0.003`: `h_0` is a conservative bound by two to three orders of magnitude | `E3_friction_sweep.*` |
| E6 | conservative variant over `[0, 0.5]`, `h = 0.01`: relative energy drift `4.3e-12`, position/velocity constraint norms `1.1e-13 / 9.5e-14`, acceleration-level norms `≤ 2e-14`, quaternion unit error `2e-16`, 5 Newton iterations per step; frictional chain: same constraint levels, 5.7 iterations per step, energy decreases by 37 % (dissipation) | `E6_long_time.*` |
| E4 | driven single pendulum (analytic reference; the harness predictor is the analytic drive, so the panel measures only the Gauss-weight reconstruction and the roundoff level): position `5.9e-10, 9.3e-12, 1.5e-13` at `h = 0.1, 0.05, 0.025` (pairwise 6.0, 6.0), roundoff below; velocity errors `1e-11…1e-8` without trend because the driven stage Jacobian has condition number `1e10–1e13` (reported as such, not plotted); double pendulum (`T = 1`, reference `h = 0.1/128`): `4.6e-5 → 3.1e-13` over `h = 0.1 → 0.00625`, pairwise position orders 8.2, 7.0, 6.0, 6.0; four-link and slider-crank (driven loops): trajectory errors `1e-14`/`1e-15` at every `h` from 0.05 to 0.0016, no order measurable | `E4_asme.*` |
| E5 | double pendulum, `T = 3`, common reference = local Gauss6 `h = 1e-4`: Gauss6 `4.3e-4 → 2.2e-13` over `h = 0.1 → 0.001` (pairwise 7.2, 9.2, 6.0, 6.1, then the reference floor `~2e-13`); public 2021 rA = rε = 2022 rA: `1.84 → 0.17` (pairwise 0.2–0.9, first order only below `h = 0.002`); rp fails for `h ≥ 0.025`, `0.75 → 0.11` below; 2022 rA-half does not converge (`0.9–5.8`). Model alignment at `T = 0.1`: rA vs local `3.7e-3` (h = 0.1/16), `9.2e-4` (h = 0.1/64), first-order decrease. Driven mechanisms assembled from v048 (Gauss6 at `1e-14`, rA velocity first order). Runtime 60 min (the `h = 0.001` Gauss6 row alone 37 min) | `E5_double_pendulum.*`, `E5_driven_public_horizon.csv` |
| E7 | solver envelope on the E1 grid with the production rule (`tol 1e-11`): accepted residual `1e-14 … 8e-12` at every step; ratio to `h^7` from `8e-5` (h = 0.1) to `1.2e6` (h = 0.003125), i.e. the fixed-tolerance runs satisfy (H3) only with a large `c_eta` on fine grids; out-of-axis components of `d, d', d''` at the stages `≤ 6e-13`; the chart-defect measure of the identity check is dominated by the unprojected endpoint position drift (`~1e-7 h^6`), so the identity table keeps the tight-tolerance (`1e-13`) numbers | `E7_solver_envelope.*` |
