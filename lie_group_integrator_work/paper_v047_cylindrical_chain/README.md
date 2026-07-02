# v047 Cylindrical Chain Paper Draft

This directory contains a self-contained LaTeX draft for the v047 cylindrical
lower-pair validation work.

There are three paper entry points:

- `main_cmame.tex` / `main_cmame.pdf`: the CMAME/Elsevier `elsarticle`
  narrowed-claim manuscript package, paired with `highlights_cmame.txt`,
  `declarations_cmame.md`, and `CMAME_SUBMISSION_CHECKLIST.md`. The global
  submission decision remains blocked by the source-policy/package gates
  recorded in `SUBMISSION_PACKET.md`.
- `cmame_submission_flat/main_cmame_submission.tex` /
  `cmame_submission_flat/main_cmame_submission.pdf`: a flat
  Editorial-Manager-oriented source copy with all thirteen figure files at the same
  folder level.
- `cmame_submission_flat.zip`: the flat LaTeX source archive for the
  narrowed-claim package; it is not a full source-policy-ready global
  submission package.
- `CMAME_SUBMISSION_READINESS_AUDIT.md` and
  `CMAME_BLOCKER_CLOSURE_GATE.md` /
  `CMAME_BLOCKER_CLOSURE_GATE.json`: the submission-readiness audit and
  machine-checkable blocker ledger. The blocker gate keeps the
  `coarse_first_no_default_1e-4` policy explicit.
- `DYNAMIC_ROW_ORACLE_GATE.md` / `DYNAMIC_ROW_ORACLE_GATE.json`: a runtime
  row-layout and block-functional oracle that imports `run_v047.py`,
  evaluates the accepted residual/Jacobian path, cross-checks the weighted
  block-functional row families, and supports the direct-route implementation
  traceability boundary; the primitive symbolic-oracle route remains diagnostic.
- `README_CMAME_FLAT_SUBMISSION.md`: the flat source package notes.
- `main.tex` / `main.pdf`: the full artifact-backed status paper with the
  full-TFE diagnostic audit trail.
- `main_concise.tex` / `main_concise.pdf`: a submission-style concise draft
  retained as supporting material for the conditional order comparison,
  four-example validation, comparator boundary, and open caveats.
- `SUBMISSION_PACKET.md`: the short submission-facing index saying which PDF to
  circulate, what the accepted claim is, and which statements remain non-claims.
  It preserves the objective blocker matrix
  `blocker_open_by_id=OC4:True,OC6:True,OC12:True`,
  `blocker_closure_decision_by_id=OC4:remain_open_ready_for_authorized_execution_not_executed_not_promoted,OC6:remain_open_no_positive_source_equivalent_artifact,OC12:remain_partial_narrowed_replay_ready_full_source_policy_archive_not_ready`,
  and `blocker_closure_allowed_by_id=OC4:False,OC6:False,OC12:False`.
- `COVER_LETTER.md` and `SUBMISSION_ARTIFACT_MANIFEST.json`: the cover-letter
  draft and machine-readable submission manifest for the same claim boundary.
- `SUBMISSION_FILE_INVENTORY.md`: a human-readable inventory of primary
  submission files, supporting evidence files, and validators.
- `REVIEW_RESPONSE_TEMPLATE.md`: a pre-scoped response template for likely
  reviewer questions about claim boundary, order comparison, four examples,
  reproducibility, and open caveats.
- `PROOF_EVIDENCE_MATRIX.md`: a proof-obligation to artifact/validator map for
  the accepted method theorem and conditional order-comparison proposition.
- `PROOF_NUMERICAL_SCALE_AUDIT.md/json`: a read-only finite-run h-sweep scale
  audit that supports the visible global order-six budget while keeping the
  `eta_h <= c_eta h^7` solver proof open.
- `PROOF_SOLVER_SCALE_AUDIT.md/json`: a read-only audit of existing
  summary-level solver residuals and the missing scaled-tolerance proof
  boundary.
- `CMAME_PROSE_RESIDUE_AUDIT.md/json`: a read-only B6 prose-residue audit that
  checks the CMAME and flat-source main body has zero machine-token residue,
  confines artifact macros to the reproducibility appendix, and keeps
  `default_1e-4_required=false`.
- `IMPLEMENTATION_FIDELITY_CERTIFICATE.md`: a static source-identity
  certificate tying the accepted 132-row residual to
  `residual_cylindrical_chain` and `R_JAC`.
- `IMPLEMENTATION_PATH_AUDIT.md/json`: a read-only static audit checking
  `implementation_path_check_for_132_row_residual=true` for the path
  `residual_cylindrical_chain -> R_VALUE/R_JAC -> gauss_step ->
  integrate/run_case -> summary_v047.json`; it does not invoke `run_v047.py`,
  a v048 runner, or a default `1e-4` campaign.
- `KINEMATIC_ROW_DEFECT_CERTIFICATE.md/json`: a partial proof certificate for
  the 96 non-dynamic collocation/lower-pair rows on the smooth accepted FullVA
  lift. In the primitive certificate route it leaves the 36
  `newton_euler_weak_balance` rows open, while the accepted direct
  Taylor/Kantorovich route is tracked by `PROOF_CLOSURE_MANIFEST.md/json` and
  `NEWTON_EULER_DYNAMIC_ROW_CLOSURE_CONTRACT.md/json`.
- `NEWTON_EULER_DEFECT_OBLIGATION_GATE.md/json`: an open 36-row
  primitive/symbolic proof-obligation ledger. It decomposes the Newton-Euler
  rows into six symbolic obligations for the non-active route; it is not the
  active direct proof-closure contract.
- `SOURCE_PAPER_COMPARISON.md`: a short source-paper versus v047 boundary note
  recording that the local `m=3` Gauss-Lobatto TFE target has expected order
  five, while the accepted branch-selected `Gauss6/FullVA` theorem supports
  the conditional order-six reduced/reporting-grid claim under its retained
  compact-branch, endpoint, implementation-binding, and solver-scale
  interfaces.
- `CROSS_PAPER_BENCHMARK_MATRIX.md` and
  `CROSS_PAPER_BENCHMARK_SPEC.md`: the same-test external benchmark matrix
  and extracted public-code benchmark specification for the original TFE paper
  and the Kissel/Negrut-related suites.
- `CROSS_PAPER_BENCHMARK_CASES.json`: the machine-readable external same-test
  row inventory, including unresolved Kissel/Bakke/Negrut
  velocity-partitioning code discovery.
- `EXTERNAL_SAME_TEST_RUN_QUEUE.md/json`: a read-only coarse-first parallel
  queue that compresses the 17 external cases into four batches, with 18
  non-default-`1e-4` shards and explicit not-ready source/code batches.
- `EXTERNAL_SAME_TEST_ACCEPTANCE_SHEET.md/json`: a read-only B2/B4 acceptance
  ledger that fixes the same-test columns, keeps
  `accepted_external_dynamic_order_examples=0`, and confirms no default
  `1e-4` campaign is required for the current closure path.
- `KISSEL_NEGRUT_CODE_INVENTORY.md`: a paper/code inventory that keeps the
  2021 `rA/rp/reps`, 2022 half-implicit, 2023/2024 velocity-partitioning, and
  2024 performance-comparison sources as separate comparison targets.
- `validate_submission_bundle.py`: a read-only preflight for the submission
  manifest, required files, clean LaTeX logs, PDFs, and no-full-generator
  boundary.
- `validate_cmame_submission.py`: a read-only CMAME/Elsevier preflight for the
  `elsarticle` source, PDF, highlights, declarations, and manifest.

Build from this directory with the Windows TeX Live install:

```bash
cmd.exe /c latexmk -pdf -interaction=nonstopmode main.tex
```

For the concise paper:

```bash
cmd.exe /c latexmk -pdf -interaction=nonstopmode main_concise.tex
```

For the CMAME/Elsevier manuscript:

```bash
cmd.exe /c latexmk -pdf -interaction=nonstopmode main_cmame.tex
```

For the flat CMAME/Elsevier source copy:

```bash
cd cmame_submission_flat
cmd.exe /c latexmk -pdf -interaction=nonstopmode main_cmame_submission.tex
```

Most direct human-runnable result replay:

```bash
python3 run_human_reproducibility.py
```

This prints the four-example, eleven-method, 44-row replay table and writes
`human_reproducibility_result_table.md`. It is replay-only evidence: it does
not launch `run_v047.py`, any v048 numerical campaign, or a default `1e-4`
source-policy run.

Opt-in local single/double numerical runners:

```bash
python3 run_human_reproducibility.py --include-local-runners
```

This keeps the same claim boundary but also invokes the self-contained
single- and double-pendulum Gauss6/FullVA candidate scripts, replay-checks the
four-link/slider-crank closed-loop local rows, runs the compact
self-contained closed-loop candidate, and appends their terminal markers to
`human_reproducibility_result_table.md`.

Full fast smoke replay:

```bash
bash run_reproduction_smoke.sh
```

This smoke entry point replays the 44-row paper result matrix, checks the
minimal replay package, checks the runner-adapter package, replay-checks the
closed-loop local four-link/slider-crank rows, and prints the current claim
boundary: common-reference replay only, source-policy external rows `0/40`,
direct-PC2 residual-bridge proof gap closed `True`, and submission ready `False`. It does not launch
`run_v047.py`, a v048 numerical campaign, or a default `1e-4` source-policy
run.

Run the lightweight paper package gate from this directory:

```bash
../.venv_sbel/bin/python validate_cmame_submission.py
../.venv_sbel/bin/python validate_cmame_blocker_closure_gate.py
../.venv_sbel/bin/python validate_cmame_prose_residue_audit.py
../.venv_sbel/bin/python validate_dynamic_row_oracle_gate.py
../.venv_sbel/bin/python validate_proof_evidence_matrix.py
../.venv_sbel/bin/python validate_proof_numerical_scale_audit.py
../.venv_sbel/bin/python validate_proof_solver_scale_audit.py
../.venv_sbel/bin/python validate_implementation_fidelity_certificate.py
../.venv_sbel/bin/python validate_implementation_path_audit.py
../.venv_sbel/bin/python validate_kinematic_row_defect_certificate.py
../.venv_sbel/bin/python validate_source_paper_comparison.py
../.venv_sbel/bin/python validate_cross_paper_benchmark_spec.py
../.venv_sbel/bin/python validate_cross_paper_benchmark_cases.py
../.venv_sbel/bin/python validate_external_same_test_run_queue.py
../.venv_sbel/bin/python validate_external_same_test_acceptance_sheet.py
../.venv_sbel/bin/python validate_submission_bundle.py
../.venv_sbel/bin/python validate_paper_package.py
```

This wrapper runs the paper-claim validator, runs the concise-paper validator,
runs the CMAME submission validator, runs the proof-evidence matrix validator,
runs the CMAME blocker-closure validator, runs the B6 prose-residue audit,
runs the proof solver-scale audit, runs the dynamic row-oracle
validator, runs the source-paper comparison validator, runs the cross-paper benchmark
specification and case-inventory validators, runs the submission-bundle
validator, runs the minimal four-ASME validator, runs
the full-TFE gap validator, runs the full-TFE repair-spec validator, runs the
full read-only v047 artifact validator, and checks that the current LaTeX log has no `Overfull`,
`LaTeX Warning`, `Package ... Warning`, or `pdfTeX warning` lines. It does not
invoke `run_v047.py`. By default it checks the existing PDFs; pass `--latex` to
also attempt PDF rebuilds from the wrapper.
The standalone
`cmd.exe /c latexmk ...` command above is the most direct PDF build path under
WSL.

The claim/evidence boundary is recorded in `PAPER_CLAIM_LEDGER.md` and in the
machine-readable `CLAIM_BOUNDARY.json`. The paper-claim validator checks that
these stay synchronized with the current summary, paper text, figures, PDF, and
the short Chinese status note `CURRENT_STATUS_CN.md`. For a reviewer-facing
command list, use `REVIEWER_CHECKLIST.md`; for a submit-or-circulate index, use
`SUBMISSION_PACKET.md`. These separate accepted claims, diagnostic evidence,
open claims, and the full-regeneration boundary.

Current status in one page:

- Primary paper claim: this is a conditional formal-order comparison and
  sixth-order FullVA method result, not a full reproduction of the source
  paper's residual and not an implemented source-paper superiority claim. The
  accepted `Gauss6/FullVA` path follows the conditional sixth-order theorem and
  records smooth position/velocity orders `7.161/7.066`; the local paper-style `m=3`
  Lobatto-TFE formula target has expected order five. The full-TFE replacement
  audit is therefore an optional stronger reproduction gate, not a prerequisite
  for the main method-order claim.
- Plain-language boundary: the original Chaturvedi--Sandu--Sandu paper has its
  own full TFE formulation. In this repository, `full TFE replacement` means a
  stricter implementation target: replace the currently accepted
  `Gauss6/FullVA` nonlinear stage residual with paper-derived TFE weak rows.
  That target is still open; the accepted validation below is the
  `Gauss6/FullVA` path.
- Terminology: `TFE` means temporal finite element. `FTE` is not a separate
  method in this package; if it appears in notes, read it as a typo for `TFE`.
  The phrase `full TFE replacement` specifically means replacing the accepted
  `Gauss6/FullVA` 132-row stage residual with paper-derived temporal
  finite-element weak rows.
- Four ASME-style examples are accepted on the `Gauss6/FullVA` method path:
  `single_pendulum`, `double_pendulum`, `four_link`, and `slider_crank`.
  The paper now includes the quantitative gate summary: single minimum order
  `6.024`, double minimum self-reference order `6.089`, closed-loop max
  constraint norm `1.052e-14`, and reaction residual `1.338e-13`.
- The accepted production method is sixth-order Gauss6/FullVA; the smooth
  h-sweep records observed position/velocity orders `7.161/7.066`.
- The paper `m=3` Lobatto-TFE formula mapping has expected order five, but that
  is a different claim from the accepted Gauss6/FullVA method.
- The proof status is conditional for the accepted Gauss6/FullVA path and is
  recorded in `ORDER_PROOF_LEDGER.md`; the independent paper-TFE replacement
  remains an open proof obligation.
- The paper proof section now has an explicit assumption-lemma-theorem-corollary
  chain. The accepted method theorem states the conditional sixth-order
  `Gauss6/FullVA` result, and a separate conditional proposition compares its
  formal order against the local `m=3` TFE target. This does not claim complete
  source-paper residual reproduction or external superiority.
- The cross-paper same-test gate is active but not closed. v048 now has all
  9/9 2021 public-code order trios for `rA/rp/reps` on `single_pendulum`,
  `four_link`, and `slider_crank`, and one bounded
  same-mechanism `Gauss6/FullVA` pilot with orders `6.073/6.033/6.055/6.024`,
  plus one exact public-horizon single-pendulum `Gauss6/FullVA` row at
  `T=3`, `h=1e-2` (`1/3` public h rows), plus 6/6 selected closed-loop
  `Gauss6/FullVA` residual rows on the 2021
  `four_link` and `slider_crank` mechanisms. Those closed-loop rows verify
  constraint/reaction residuals, not dynamic order/work superiority. v048 also
  has 12/12 selected same-window comparison rows for public `rA` dynamics
  versus local `Gauss6/FullVA` residual rows at `T=0.2`,
  `h=[0.02,0.01,0.005]`; these are table-shape evidence and do not replace the
  exact public `T=3` dynamic campaign. It also derives 9-row public order/work
  and 4-row same-window work/precision summaries for paper tables. v048 also
  has a bounded 2022 half-implicit `double_pendulum` pilot with 6/6
  `rA/rA_half` rows and a negative-order `rA_half` caveat; the full
  original-TFE, 2022 Kissel/Negrut, and velocity-partitioning campaigns
  remain open.
- `full_tfe_stage_replacement=false` remains the open research gate. The
  current source-free terminal closure closes endpoint velocity but is still
  order-limited.
- The latest component-split pose-acceleration probe is diagnostic only:
  translation-only pose shifts remain at residual `5.298e-06`, angular-only
  `angposeaccel_p0p002` reaches `9.6511e-06`, and no branch spans the terminal
  bridge.
- The latest component-split velocity-acceleration probe is also diagnostic
  only: `transvelaccel_m0p01` reaches residual `2.138e-04`, the tiny
  `transvelaccel_m0p0005` scale reaches `9.8175e-06`, and no branch spans the
  terminal bridge.
- The latest component-mixed pose/velocity Taylor probe is diagnostic only:
  `angpose_transvelaccel_p0p0005_m0p0005` reaches residual `9.987e-06`, still
  worse than the uncorrected terminal-limit `5.298e-06`, and no branch spans
  the terminal bridge.
- The latest stage-2-fixed/delta acceleration velocity-shift probe is also
  diagnostic only: `transvelaccelstage2_m0p0005` reaches `9.8175e-06`, the
  best `transvelacceldelta20_m0p0005` branch reaches `1.0119e-05`, and no
  branch spans the terminal bridge.
- The latest nonfinal terminal velocity/source predictor probe is diagnostic:
  `nonfinal_velocity_terminal_euler1_z` reaches only `0.923466`, with the
  missing direction concentrated in stage-2 `translation_velocity_v`; no branch
  spans the terminal bridge.
- Promoting nonfinal velocity/source predictors into the bounded trajectory
  smoke is also negative. The stage0/1 set runs in `135.3` seconds with rank
  `132`, but the best terminal velocity is only `1.770e-07`; the stage0/1/2 set
  runs in `101.1` seconds and briefly reaches `2.559e-11` at `h=0.04`, but
  jumps to `1.328e-07` at `h=0.02`, so `terminal_velocity_closed=false`.
- The latest stage-2 source-to-velocity transport probe is the strongest
  nonterminal transport clue so far: the scaled
  `0p00_sourceliftmatrixdiff_historydelta_m0p0001` law reaches `1.251e-06`,
  but it still has independent target rank `6` and no terminal-bridge span.
- The latest angular-pose combined follow-up does not improve that clue:
  `0p00_sourceliftmatrixdiff_historydelta_m0p0001_angposeaccel_p0p0001`
  reaches only `1.296e-06`, returns the independent target rank to `8`, and
  still has no terminal-bridge span.
- A bare endpoint-pose velocity check resolves the limit of that transport
  family: `stage02_convex_pose_velocity_0p00_z` spans the local terminal bridge
  at residual `1.327e-15` in a `31.7` second, three-row JSON-only probe. This
  is local row-space evidence only; no nonlinear h-sweep or order proof has
  accepted it, so `full_tfe_stage_replacement=false` remains unchanged.
- A bounded nonlinear trajectory smoke now tests that row inside the full
  `132`-row residual. The smooth three-h short sweep closes terminal velocity
  to `8.124e-17`, but position/velocity orders are only `4.142/2.305`; the
  nearby nonterminal `stage02_convex_pose_velocity_0p01_z` row leaves terminal
  velocity at `6.255e-06`.
- The non-projection extrapolated `0p01/0p02` row is a useful trajectory clue:
  it reduces terminal velocity to `1.254e-07`, but the three-h smooth orders
  are only `4.054/2.364`, so it remains diagnostic. Pushing the extrapolation
  points much closer to the endpoint closes terminal velocity at
  `stage02_convex_pose_velocity_extrapolate_0p00001_0p00002_z`
  (`1.254e-13` without projection), but the three-h order is still
  `4.142/2.305`.
- A new quadratic nonterminal extrapolation law reaches the same boundary:
  `stage02_convex_pose_velocity_quadextrapolate_0p002_0p005_0p01_z` closes
  terminal velocity without projection (`2.029e-13`, finest-h `8.254e-15`),
  but the three-h order remains `4.142/2.305`.
- The terminal-tangent projection diagnostic is also negative and is
  projection-like by construction: full `0p01_terminalproj` diverges at
  `6.739e+08`; damped `p0p1` and `p0p5` variants leave terminal velocities
  `7.028e-06` and `1.321e-05` with low orders.
- `run_v047.py` is an accumulated audit harness and artifact generator, not a
  compact reference implementation. Do not run it just to validate the four
  examples or rebuild the paper.
- The paper does not claim sparse AD is already faster, nor that the sharp
  Brown--McPhee coarse-step regime is solved; both remain caveats.

Next full-TFE repair target:

- Derive a nonterminal endpoint-pose predictor that closes terminal velocity on
  trajectory without the order loss seen in the bare `0p00` endpoint row.
- Keep the construction stage-local: no endpoint-boundary source data, no
  terminal-row replacement, no projection, and no target-direction oracle.
- Promote the candidate from local tangent probes to a nonlinear h-sweep over
  `h=[0.04,0.02,0.01]` against `reference_h=0.005`.
- Accept only if terminal endpoint velocity closes and the paper-TFE order
  target is restored. The current source-free terminal-closed candidate still
  fails this because its smooth position order is `3.523`.

This paper build does not require rerunning the full v047 numerical pipeline.
The latest recorded full regeneration time in `summary_v047.json` is about
2386.76 seconds, because `run_v047.py` now contains the accumulated historical
audit suite. For paper edits or evidence checks, use the existing result
artifacts plus the read-only validator:

```bash
../.venv_sbel/bin/python validate_paper_package.py
../.venv_sbel/bin/python validate_proof_evidence_matrix.py
../.venv_sbel/bin/python validate_source_paper_comparison.py
../.venv_sbel/bin/python validate_submission_bundle.py
../.venv_sbel/bin/python validate_paper_claims.py
```

For generated v047 evidence checks, use the existing result artifacts plus the
read-only validators:

```bash
cd ../v047_cylindrical_chain_pipeline
../.venv_sbel/bin/python validate_four_asme_minimal.py
../.venv_sbel/bin/python validate_full_tfe_gap.py
../.venv_sbel/bin/python validate_full_tfe_repair_spec.py
../.venv_sbel/bin/python validate_v047_outputs.py
```

The minimal validator checks only the four ASME method gate. The full-TFE gap
validator checks the current open replacement boundary and the exact next
repair target. The repair-spec validator checks the 132-row/16+8 lower-pair
implementation contract for the next candidate. The full
`validate_v047_outputs.py` check remains the broader generated-artifact gate.

The next full-TFE candidate also has a bounded smoke target that does not run
the full generator or update artifacts:

```bash
V047_TARGET_AUDIT=lower_pair_recurrent_weak_closure_smoke ../.venv_sbel/bin/python run_v047.py
```

This prints static wiring JSON by default. Add
`V047_RECURRENT_WEAK_SMOKE_NUMERIC=1` only when a one-step numerical smoke is
wanted.

The same scaffold has a short trajectory smoke that still avoids the full
generator and still writes no artifacts:

```bash
V047_TARGET_AUDIT=lower_pair_recurrent_weak_closure_trajectory_smoke ../.venv_sbel/bin/python run_v047.py
```

It runs smooth and sharp at `h=0.04`, `t_final=0.08`, then prints JSON with
`terminal_velocity_closed=false` and `full_tfe_stage_replacement=false`.

The bounded h-sweep smoke adds a fast convergence trend check without writing
artifacts:

```bash
V047_TARGET_AUDIT=lower_pair_recurrent_weak_closure_h_sweep_smoke ../.venv_sbel/bin/python run_v047.py
```

It defaults to smooth and sharp over `h=[0.04,0.02]` against
`reference_h=0.01`. The full acceptance-shaped sweep remains explicit opt-in
with `V047_RECURRENT_WEAK_H_SWEEP_FULL=1`. The latest full-shaped run converged
but still reported max raw terminal endpoint velocity `8.234e-06` and
`accepted_h_sweep_present=false`.

The one-step recurrent/terminal blend screen checks whether the recurrent
closure and final-stage velocity closure have a useful intermediate gamma:

```bash
V047_TARGET_AUDIT=lower_pair_recurrent_terminal_blend_one_step_smoke ../.venv_sbel/bin/python run_v047.py
```

It currently shows that gamma `1.0` terminal-closes at one step, while gamma
`0.5` has the best residual but does not close terminal velocity.

The recurrent/terminal blend h-sweep smoke promotes that screen to a bounded
trajectory check while still avoiding the full generator:

```bash
V047_TARGET_AUDIT=lower_pair_recurrent_terminal_blend_h_sweep_smoke ../.venv_sbel/bin/python run_v047.py
```

For a shorter smooth-only check, set
`V047_RECURRENT_TERMINAL_BLEND_H_SWEEP_CASES=cylindrical_smooth`. The latest
default smooth+sharp bounded run converged in 62.2 seconds, found terminal
closure at gamma `1.0` with smooth/sharp terminal velocities
`3.049e-16`/`2.941e-16`, but still had smooth minimum order `4.397` and sharp
velocity order `-0.428`; it remains diagnostic with
`accepted_h_sweep_present=false`.

A denser scalar-gamma exclusion screen can be run with:

```bash
V047_TARGET_AUDIT=lower_pair_recurrent_terminal_blend_h_sweep_smoke V047_RECURRENT_TERMINAL_BLEND_H_SWEEP_GAMMAS=0,0.25,0.5,0.75,1 ../.venv_sbel/bin/python run_v047.py
```

The latest dense bounded run converged in 114.2 seconds over 60 short-trajectory
steps. It found best smooth-order gamma `0.75` with smooth minimum order
`4.414`, while terminal closure stayed at gamma `1.0`; no scalar gamma in this
bracket closes the full-TFE gate.

The near-terminal scalar-policy check uses:

```bash
V047_TARGET_AUDIT=lower_pair_recurrent_terminal_blend_h_sweep_smoke V047_RECURRENT_TERMINAL_BLEND_H_SWEEP_GAMMAS=0.9,0.99,0.999,1 ../.venv_sbel/bin/python run_v047.py
```

The latest near-terminal bounded run converged in 91.6 seconds over 48
short-trajectory steps. Best smooth-order gamma was `0.99` with smooth minimum
order `4.415`, but terminal velocity remained `3.081e-06` on the sharp branch;
gamma `0.999` still had terminal velocity `4.678e-07`, so only gamma `1.0`
terminal-closes and it remains order-limited.

The component-wise one-step gamma sensitivity check uses:

```bash
V047_TARGET_AUDIT=lower_pair_recurrent_terminal_component_one_step_smoke ../.venv_sbel/bin/python run_v047.py
```

The latest run completed in 31.6 seconds over 20 one-step rows. It preserved
rank `132` with max residual `1.766e-12`; `component_2_release_0p999` gave the
best nontrivial terminal velocity `3.456e-17`, while
`component_7_release_0p999` was worst at `1.234e-11`. This is a sensitivity
screen only: `accepted_h_sweep_present=false` and
`full_tfe_stage_replacement=false`.

The component-wise trajectory gamma h-sweep uses:

```bash
V047_TARGET_AUDIT=lower_pair_recurrent_terminal_component_h_sweep_smoke ../.venv_sbel/bin/python run_v047.py
```

The latest default run completed in 98.4 seconds over 48 short-trajectory
steps. It kept rank `132` with max residual `4.766e-12`; the best terminal
vector was `component_2_release_0p999` at `2.696e-16`, while the best
smooth-order vector was `all_0p999` at `4.401` and still left terminal velocity
`4.678e-07`. Thus `order_terminal_intersection_present=false`.

The recurrent history-gamma trajectory screen uses:

```bash
V047_TARGET_AUDIT=lower_pair_recurrent_history_gamma_h_sweep_smoke ../.venv_sbel/bin/python run_v047.py
```

The latest default smooth-only run completed in 38.9 seconds over 12
short-trajectory steps. It kept rank `132` with max residual `2.586e-12`; the
best history-gamma branch had terminal velocity `1.451e-07` and smooth
minimum order `4.402`. A signed-policy follow-up completed in 36.9 seconds
with max residual `3.869e-12`, best terminal velocity `1.452e-07`, and best
smooth order `4.415`. This simple explicit recurrent history-gamma law still
has `order_terminal_intersection_present=false`,
`accepted_h_sweep_present=false`, and `full_tfe_stage_replacement=false`.

The recurrent weak-row differential audit uses:

```bash
V047_TARGET_AUDIT=lower_pair_recurrent_weak_differential_audit ../.venv_sbel/bin/python run_v047.py
```

The latest default smooth run completed in 26.0 seconds over the `zero_initial`
and `post_one_step` history modes at `h=0.04`. It kept rank `132` with max
residual `2.483e-12`. The current recurrent weak row does not span the
terminal bridge: projection residuals are `0.899` to `0.974`, while the
final-stage terminal row projects at `1.456e-15`; the missing direction is
stage-2-local and dominated by `translation_velocity_v`. This is the current
reason the next repair must change the analytical weak row formula.

The stage-2 coefficient-gradient differential audit uses:

```bash
V047_TARGET_AUDIT=lower_pair_recurrent_stage2_gradient_differential_audit ../.venv_sbel/bin/python run_v047.py
```

The latest default smooth run completed in 35.3 seconds over 8 local rows. It
kept rank `132` with max residual `2.483e-12`, but no source/history-modulated
stage-2 velocity coefficient-gradient row spanned the terminal bridge:
`any_candidate_spans_terminal_bridge=false`, best projection residual `0.899`,
best gain `1e12`, and independent target rank `8`.

The stage-2 matrix-gradient differential audit uses:

```bash
V047_TARGET_AUDIT=lower_pair_recurrent_stage2_matrix_gradient_differential_audit ../.venv_sbel/bin/python run_v047.py
```

The latest default smooth run completed in 68.1 seconds over 32 local rows. It
kept rank `132` with max residual `2.483e-12`, but no target-free row/column/
bilinear matrix mixing of the stage-2 velocity row spanned the terminal bridge:
`any_candidate_spans_terminal_bridge=false`, best law
`diagonal_plus_row_broadcast_feature`, best gain `1e12`, best projection
residual `0.898873`, independent target rank `8`, and max closure-value delta
`4.005e-09`.

An active-velocity extension reuses the same target with:

```bash
V047_TARGET_AUDIT=lower_pair_recurrent_stage2_matrix_gradient_differential_audit V047_RECURRENT_STAGE2_MATRIX_LAWS=stage2_velocity_row_broadcast_feature,stage2_velocity_column_broadcast_feature,stage2_minus_stage1_velocity_row_broadcast_feature,velocity_curvature_diagonal_plus_row_broadcast_feature V047_RECURRENT_STAGE2_MATRIX_GAINS=1e8,1e12 ../.venv_sbel/bin/python run_v047.py
```

That run completed in 46.6 seconds over 16 local rows. It improved the best
projection residual to `0.585746` with
`stage2_velocity_column_broadcast_feature` and gain `1e12`, but independent
target rank stayed `8` and `any_candidate_spans_terminal_bridge=false`.

An expanded active-law grid reuses the same target with five stage-velocity
matrix laws. It completed in 51.2 seconds over 20 local rows. The best law was
`stage2_velocity_shifted_column_broadcast_feature` at gain `1e12`, with
projection residual `0.576548`; independent target rank remained `8` and
`any_candidate_spans_terminal_bridge=false`.

A JSON-only missing-direction decomposition reran that best law/gain without
the full pipeline. It completed in 27.8 seconds over 2 local rows. The best
post-one-step row kept projection residual `0.576548` and missing-direction
rank `8`, with dominant variable family `angular_velocity_w` at fraction
`0.502991` and stage fractions `0.018511`, `0.018451`, and `0.963038`.
The zero-initial row had residual `0.909693`, dominant variable family
`translation_velocity_v` at fraction `0.487135`, and stage-2 fraction
`0.964696`. This localizes the remaining gap to a stage-2 angular-velocity
coupling target, not another generic matrix-law sweep.

A stage-2 angular-velocity mask follow-up reuses the same target with four
angular-only matrix laws and gain `1e12`. It completed in 35.3 seconds over 8
local rows. The best law was
`stage2_angular_velocity_shifted_column_broadcast_feature`, with projection
residual `0.752997`; independent target rank remained `8` and
`any_candidate_spans_terminal_bridge=false`. The best remaining direction
shifted back to dominant variable family `translation_velocity_v` at fraction
`0.660361`, with stage-2 fraction `0.978093`. This excludes simple
angular-only masking and points to coupled translation/angular stage-2 weak-row
structure.

A direct translation/angular cross-coupling follow-up reuses the same target
with four outer-cross matrix laws and gain `1e12`. It completed in 35.3
seconds over 8 local rows. The best law was
`stage2_velocity_angular_to_translation_cross_feature`, with projection
residual `0.898812`; independent target rank remained `8` and
`any_candidate_spans_terminal_bridge=false`. The best remaining direction was
again dominated by `translation_velocity_v` at fraction `0.556004`, with
stage-2 fraction `0.999994`. This excludes the tested simple cross-coupled
matrix laws.

An endpoint-pose generalized-velocity predictor follow-up then tested five
terminal velocity predictor variants over both history modes. It completed in
31.2 seconds over 10 local rows. The best law was
`paper_endpoint_pose_positive_lagrange_z`, with projection residual
`0.117782`; independent target rank remained `8` and
`any_candidate_spans_terminal_bridge=false`. The best remaining direction was
dominated by `translation_velocity_v` at fraction `0.514237`, with stage
fractions `0.961546`, `0.004167`, and `0.034287`. This is the best current
local repair probe, but it remains diagnostic rather than an accepted full-TFE
replacement.

A near-terminal stage-0/stage-2 convex predictor follow-up then tested seven
predictor weights over both history modes. It completed in 31.7 seconds over
14 local rows. The stage-2-only law `paper_endpoint_pose_stage02_convex_0p00_z`
spanned at roundoff, but it is terminal-bridge equivalent and therefore not an
independent replacement. The best nonterminal law was
`paper_endpoint_pose_stage02_convex_0p05_z`, with projection residual
`0.049317`; independent target rank remained `8`,
`nonterminal_span_row_count=0`, and
`any_nonterminal_candidate_spans_terminal_bridge=false`.
Focused h-scaling reruns at `h=0.02` and `h=0.01` keep the terminal-equivalent
0p00 row at roundoff span, while the same nonterminal 0p05 row remains rank
`8` with residuals `0.051890` and `0.052472`. The paper therefore treats the
near-terminal result as a persistent nonterminal weak-row gap, not as evidence
that the terminal bridge can be accepted as a full TFE replacement.
The synchronized pose/velocity variant improves the best local residual to
`0.009512` with `stage02_convex_pose_velocity_0p01_z`, but remains rank `8` and
no-span. Its `h=0.02` and `h=0.01` residuals are `0.009978` and `0.010085`,
and larger offsets `0p02/0p05/0p10` give `0.019205/0.049390/0.103464`, so it
is a near-terminal asymptote rather than an accepted replacement.
The terminal-limit extrapolation `stage02_convex_pose_velocity_extrapolate_0p01_0p02_z`
reduces the residual to `4.699e-06`, then `2.335e-06` and `1.168e-06` at
`h=0.02` and `h=0.01`, but still has no span and is marked
terminal-bridge-equivalent.
Direct `-1/+1` mean-acceleration bridge corrections worsen the best residual
to `0.076159` or above and shift the missing direction to `lie_position_u`, so
the existing acceleration bridge term is not the missing independent row.

A bilinear active-velocity outer-product follow-up reuses the same target with
six feature/stage-2-velocity matrix laws. It completed in 57.3 seconds over 24
local rows. The best law was
`stage2_velocity_feature_outer_stage2_velocity` at gain `1e12`, with
projection residual `0.898720`; independent target rank remained `8` and
`any_candidate_spans_terminal_bridge=false`. This rules out the tested simple
outer-product coupling family and does not supersede the previous `0.576548`
active shifted-column localization result.

A componentwise active-velocity diagonal follow-up reuses the same target with
six Hadamard/shifted-diagonal matrix laws. It completed in 56.7 seconds over
24 local rows. The best law was
`stage2_velocity_diagonal_plus_hadamard_row_feature_stage2_velocity` at gain
`1e12`, with projection residual `0.898530`; independent target rank remained
`8` and `any_candidate_spans_terminal_bridge=false`.

Two small acceleration-correction follow-ups then test the synchronized
`stage02_convex_pose_velocity_0p01/0p02` family. Direct signed
mean-acceleration closure corrections and generalized-velocity Taylor shifts
each cover 18 local rows, keep rank 132, and keep
`nonterminal_span_row_count=0`. In both cases the uncorrected
`stage02_convex_pose_velocity_0p01_z` row remains best at `0.009512`; the best
acceleration-corrected row reaches only `0.012376`, and unit corrections are no
better than `0.077874`.

A kinematic pose-slope predictor follow-up then uses `(q2-q0)/(h*(c2-c0))` as
a stage-local velocity estimate for the same synchronized rows. It completed
26 local rows in 37.1 seconds, again with `nonterminal_span_row_count=0`. The
uncorrected `stage02_convex_pose_velocity_0p01_z` row remains best at
`0.009512`; the best pose-slope row is
`stage02_convex_pose_velocity_0p02_poseslope_m0p1_z` with residual `0.878519`.

A source-to-velocity lift follow-up maps source rows through the current
endpoint velocity matrix into minimum-norm generalized-velocity shifts. It
completed 34 local rows in 76.4 seconds, again with
`nonterminal_span_row_count=0`. The uncorrected
`stage02_convex_pose_velocity_0p01_z` row remains best at `0.009512`; the best
source-lift corrections are
`stage02_convex_pose_velocity_0p01_sourcelift_historydelta_p1_z` and
`stage02_convex_pose_velocity_0p01_sourcelift_source0_p1_z`, both at
`0.609803`.

A matrix-difference source-to-velocity lift follow-up maps the same source
rows through stage-0 and stage-2 `C_v` matrices and inserts the difference of
the two velocity shifts. The first 14-row screen runs in 58.7 seconds and
reaches coarse-scale residual `0.042593`. A refined 26-row scale sweep runs in
92.5 seconds over `0.1`, `1`, and `10` gains, keeps
`nonterminal_span_row_count=0`, leaves the uncorrected
`stage02_convex_pose_velocity_0p01_z` row best at `0.009512`, and gives best
corrected row
`stage02_convex_pose_velocity_0p01_sourceliftmatrixdiff_historydelta_p0p1_z`
at `0.009527`.

A normalized-history source-direction variant replaces `source0-history` by
its direction scaled by `||source0||` before the same matrix-difference lift.
It covers 10 local rows in 49.4 seconds, keeps
`nonterminal_span_row_count=0`, leaves the uncorrected
`stage02_convex_pose_velocity_0p01_z` row best at `0.009512`, and gives best
corrected row
`stage02_convex_pose_velocity_0p01_sourceliftmatrixdiff_historyunitdelta_p0p1_z`
at `0.009590`.

A near-terminal slope follow-up tests the finite-difference slope of the
same synchronized convex pose/velocity family. It covers 4 local rows in 25.8
seconds at `h=0.04`, keeps rank `132`, and has
`any_candidate_spans_terminal_bridge=false`. The best law is
`stage02_convex_pose_velocity_slope_0p01_0p05_z`, with residual `0.677034`,
independent target rank `8`, and dominant remaining family
`translation_velocity_v`.

A near-terminal curvature follow-up tests the second finite-difference
curvature of the same synchronized convex pose/velocity family. It covers 4
local rows in 26.7 seconds at `h=0.04`, keeps rank `132`, and has
`any_candidate_spans_terminal_bridge=false`. The best law is
`stage02_convex_pose_velocity_curvature_0p01_0p05_0p10_z`, with residual
`0.871228`, independent target rank `8`, and dominant remaining family
`translation_velocity_v`.

A source/history coefficient-feature matrix follow-up tests recurrent source
features as shifted-column coefficient matrices on the stage-2 lower-pair
velocity row. It covers 16 local rows in 44.8 seconds at `h=0.04`, keeps rank
`132`, and has `any_candidate_spans_terminal_bridge=false`. The best law is
`source_curvature_shifted_column_broadcast_feature`, with residual `0.898873`,
independent target rank `8`, dominant remaining family
`translation_velocity_v`, and stage-2 fraction `1.000000`.

A nonlinear recurrent curvature/history matrix-feature follow-up tests
source-curvature minus history-delta, source/history Hadamard, unit-Hadamard,
and normalized curvature-plus-history feature prefixes. It covers 16 local
rows in 45.5 seconds at `h=0.04`, keeps rank `132`, and has
`any_candidate_spans_terminal_bridge=false`. The best law is
`source_curvature_minus_history_delta_diagonal_plus_row_broadcast_feature`,
with residual `0.898865`, independent target rank `8`, dominant remaining
family `translation_velocity_v`, and stage-2 fraction `0.999996`.

A terminal-limit source-lift matrix-difference follow-up tests whether the
best near-terminal extrapolated intercept can be repaired by adding a
stage-local `C_v` source-to-velocity lift before extrapolation. It covers 8
local rows in 47.5 seconds at `h=0.04`, keeps rank `132`, and has
`any_candidate_spans_terminal_bridge=false`. The best law is
`stage02_convex_pose_velocity_extrapolate_0p01_0p02_sourceliftmatrixdiff_curvature_m0p1_z`,
with residual `5.298e-06`, independent target rank `8`, and dominant
remaining family `translation_acceleration_a`.

A Gauss endpoint-pose velocity-predictor screen is also negative. It covers 7
local rows in 28.7 seconds at `h=0.04`, keeps rank `132`, and has
`any_candidate_spans_terminal_bridge=false`. The best law is
`gauss_endpoint_pose_positive_lagrange_z`, with residual `0.208599`,
independent target rank `8`, dominant remaining family `lie_position_u`, and
stage fractions `0.524567/0.209731/0.265702`.

A remaining Gauss endpoint-pose completion screen covers 11 untried quarter,
stage1-half, convex, and mean predictor rows in 31.5 seconds at `h=0.04`. It
also has `any_candidate_spans_terminal_bridge=false`; the best law is
`gauss_endpoint_pose_stage02_convex_0p00_z`, with residual `0.172659`,
independent target rank `6`, dominant remaining family `lie_position_u`, and
stage fractions `0.320394/0.305625/0.373981`.

Only rerun `../.venv_sbel/bin/python run_v047.py` after changing numerical
method code or artifact-producing audit code.

The draft uses a local figure snapshot under:

```text
figures/
```

Refresh those PNGs from `../v047_cylindrical_chain_pipeline/results/` after a
new full v047 regeneration if the plotted artifacts change.

The current paper status is intentionally conservative: the Gauss6/FullVA
method and four ASME method rows are reported as accepted, while the independent
full TFE stage replacement is reported as an open gate. The source-free
final-stage velocity closure is included as a terminal-closed but order-limited
TFE diagnostic, the velocity-compression figure records the selector-degeneracy
check showing the fixed fits collapse to the final-stage row, and the
non-degenerate compression figure records the failed fixed stage-0/stage-1
injection probe, the state-dependent compression figure records the failed
diagonal state-local direction-oracle probe, and the component-mixing figure
records the failed non-final full-mixing probe. The value-level compression
figure records that row values can be balanced, but meaningful non-final
value-balanced fits still fail the tangent span. The derivative-aware
compression figure records the local coefficient-gradient oracle that closes
the tangent gap for meaningful non-final rows while remaining short of a
bounded nonlinear row formula. The bounded-gradient compression figure records
that practical gradient caps do not recover all local spans and that full local
coverage requires cap 1e18. The bounded-formula compression figure records
that explicit tanh and rational saturation laws preserve value balance but
still need cap 1e22 for full local coverage and still use a target-direction
oracle. The target-free compression figure records that 12 source-derived,
stage-extrapolated, and all-active component direction laws avoid the target Jacobian in the formula
but still produce 0 local spans, with best residual 9.82e-01. The
direction-capacity figure records that all-stage velocity features span 72
rows while non-final active/source features span 0 rows, localizing the next
repair to nonlinear or second-differential non-final source features. The
nonlinear-capacity figure records that six finite-difference source-feature
families over 216 rows still produce 0 spans, with best projection/correction
residuals 6.95e-01/7.01e-01, localizing the next repair to higher-order or
nonlocal non-final source features. The higher-order, one-step history,
two-step history, recurrent history-capacity, and weak-row structure-capacity
figures record that the tested third-differential, transported, curvature,
bilinear, cross-Gram, Hadamard, and shifted-commutator source/velocity feature
spaces also produce 0 spans. The row-space compression figure records that
target-free SVD, row-norm, and stage-balanced frozen eight-row compressions
over the all-stage/non-final velocity row space also produce 0 spans, with
best projection residual 7.38e-01 and best non-final residual 9.82e-01,
leaving the next repair at a revised analytical weak-row formula or richer
recurrent nonlinear source law. The
order/closure blend figure records the
targeted beta sweep that confirms the current terminal-closure and
order-preservation properties remain split.

The latest bare endpoint-pose velocity check adds
`stage02_convex_pose_velocity_0p00_z` next to the ultra-fine source transport
row. It covers 3 JSON-only local rows in 31.7 seconds and spans the terminal
bridge locally at residual `1.327e-15`, with `span_row_count=1`. This confirms
that the `m0p0001` source-transport row was converging toward the bare endpoint
row, but it is still local-span-not-full-TFE evidence because no nonlinear
h-sweep or order proof has accepted it.

The follow-up bounded nonlinear h-sweep target
`lower_pair_endpoint_pose_velocity_predictor_h_sweep_smoke` inserts the same
predictor family into the `132`-row residual without writing artifacts. The
default smooth-only `0p00` smoke runs in 21.5 seconds over `h=[0.04,0.02]` and
closes terminal velocity to `7.29e-17`, but the two-point velocity order is
only `4.508`. A smooth-only three-h refinement runs in 28.6 seconds over
`h=[0.04,0.02,0.01]` against `reference_h=0.005`; it closes terminal velocity
to `8.124e-17`, but gives only `4.142/2.305` position/velocity order. The
nearby `0p01` row converges but leaves terminal velocity at `6.255e-06` with
orders `2.345/1.878`. This moves the evidence from local span to trajectory
diagnostic and keeps `full_tfe_stage_replacement=false`.

A source-transport trajectory follow-up compares the bare `0p00` row against
the best local source-only transport row and the angular-pose combined row. It
runs in 74.1 seconds, keeps rank `132`, uses `projection_used=false`, writes no
artifacts, and still does not pass. The source-only transported row has orders
`6.588/4.508`, but max terminal velocity `8.020e-12`, above the `1e-12`
tolerance. The angular-pose combined row worsens terminal velocity to
`2.102e-07` and velocity order to `2.820`.

A three-h refinement of the source-only transported row runs in 46.4 seconds
over `h=[0.04,0.02,0.01]` against `reference_h=0.005`, converges all 7
requested steps, keeps rank `132`, and uses `projection_used=false`; however,
max terminal velocity remains `8.020e-12` despite a finest-h value
`5.904e-13`, and the orders drop to `4.142/2.305`. This matches the bare
endpoint-row order loss rather than an accepted full-TFE replacement.

Shrinking that coefficient to
`stage02_convex_pose_velocity_0p00_sourceliftmatrixdiff_historydelta_m0p00001_z`
closes the terminal tolerance in the same three-h smoke: elapsed `43.6`
seconds, rank `132`, `projection_used=false`, max/finest terminal velocity
`8.021e-13`/`5.910e-14`, and all 7 steps converged. It still has
`smooth_order_ok=false` with orders `4.142/2.305`, so coefficient shrinking
only recovers terminal closure, not the missing full-TFE order.

The non-projection terminal-limit extrapolation
`stage02_convex_pose_velocity_extrapolate_0p01_0p02_z` is a useful
near-miss. Its default two-h smoke runs in 21.8 seconds, keeps rank `132`,
uses `projection_used=false`, reduces max terminal velocity to `1.254e-07`,
and gives orders `6.412/3.775`. A three-h smooth refinement runs in 28.9
seconds, converges all 7 requested steps, keeps rank `132`, reaches finest-h
terminal velocity `1.244e-08`, but has only `4.054/2.364` position/velocity
order. It improves the nonterminal terminal error but still fails both terminal
closure and smooth-order acceptance.

Closer non-projection extrapolation confirms the same limit. A default two-h
smoke over `0p005/0p01`, `0p002/0p005`, and `0p001/0p002` runs in 55.2 seconds
with `projection_used=false`, rank `132`, and terminal velocities
`3.135e-08`/`6.270e-09`/`1.254e-09`, but velocity orders remain
`4.648`/`4.566`/`4.521`. The three-h refinement for `0p001/0p002` gives
`4.143/2.307` order. The ultra-near `0p00001/0p00002` row closes terminal
velocity without projection at `1.254e-13` and finest-h `1.254e-14`, but the
three-h order is still `4.142/2.305`, so this is terminal-equivalent limiting
evidence, not an accepted full-TFE replacement.

The quadratic nonterminal extrapolation follow-up tests whether a higher-order
weight extrapolation avoids that degeneration. It adds
`stage02_convex_pose_velocity_quadextrapolate_*` laws that use three strictly
nonterminal rows and no projection. The default two-h smoke over
`0p01/0p02/0p05`, `0p005/0p01/0p02`, and `0p002/0p005/0p01` runs in 57.0
seconds, keeps rank `132`, and gives terminal velocities
`2.029e-11`/`2.029e-12`/`2.029e-13`, but velocity orders stay near `4.508`.
The best three-h refinement,
`stage02_convex_pose_velocity_quadextrapolate_0p002_0p005_0p01_z`, has
`terminal_velocity_closed=true`, max terminal velocity `2.029e-13`, finest-h
terminal velocity `8.254e-15`, and order `4.142/2.305`, so it is also
terminal-equivalent limiting evidence.

The nonfinal velocity/source predictor trajectory follow-up rules out a
different route. The original stage0/1 set
`linear01/euler0/euler1/ab01/source01mean0/source01linear0/source01linear1/hermite01`
runs in 135.3 seconds, keeps rank `132`, and converges all `24` rows, but the
best max terminal velocity is `1.770e-07`; the higher-order-looking
`euler1/ab01/source01linear1` rows stay at `3.584e-07`. Adding the third Gauss
stage with `linear012/euler2/ab12/source12mean2/source12linear2/hermite12` runs
in 101.1 seconds and converges all `18` rows, but the apparent
`2.559e-11` coarse terminal velocity jumps to `1.328e-07` at `h=0.02`; the
stable `linear012` branch is only `1.134e-07`.

A follow-up projection-like terminal-tangent diagnostic is also negative. The
full `stage02_convex_pose_velocity_0p01_terminalproj_z` correction fails in
the reference run with residual divergence `6.739e+08`. Damped corrections
converge but worsen the target split: `terminalproj_p0p1` gives terminal
velocity `7.028e-06` with orders `2.301/1.788`, and `terminalproj_p0p5` gives
`1.321e-05` with orders `2.158/1.433`. These runs set `projection_used=true`,
so they are diagnostic only even aside from the poor numbers.
