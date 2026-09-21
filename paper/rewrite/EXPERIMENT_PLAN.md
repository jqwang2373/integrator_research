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
