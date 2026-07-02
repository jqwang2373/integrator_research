# CMAME Flat Submission Folder

The `cmame_submission_flat/` folder is the Editorial-Manager-oriented LaTeX
source package. It keeps the manuscript source and every referenced figure at
one folder level, matching Elsevier's LaTeX submission guidance for systems
that do not resolve figure subfolders.

Primary files:

- `main_cmame_submission.tex`
- `main_cmame_submission.pdf`
- `highlights_cmame.txt`
- `declarations_cmame.md`
- `Figure_1_convergence.png`
- `Figure_2_asme_lower_pair_graph_bridge.png`
- `Figure_3_asme_closed_loop_kinematic_fullva.png`
- `Figure_4_order_closure_blend.png`
- `Figure_5_velocity_compression.png`
- `Figure_6_sparse_speed_gap.png`
- `Figure_7_strict_common_reference_work_precision.png`
- `Figure_8_claim_boundary_limitations.png`
- `Figure_9_coarse_baseline_work_precision.png`
- `Figure_10_closed_loop_true_dynamic_order.png`
- `Figure_11_method_stage_architecture.png`
- `Figure_12_all_method_result_matrix.png`
- `Figure_13_work_precision_compendium.png`

The flat source archive is `../cmame_submission_flat.zip`. Its entries are
flat: the TeX source and all thirteen figure files are at the archive root.
It is the editorial LaTeX archive for the narrowed-claim package, not a
global source-policy-ready submission package and not the reviewer-facing
reproducibility code package; runner scripts and audit builders stay in the
repository package.

The reviewer-facing runnable evidence for the narrowed current claim is
`cmame_narrowed_repro_bundle/`. Its launcher replays the paper matrix and runs
the four self-contained local accepted-row runners, while preserving the
source-policy boundary: external source-policy rows remain `0/40`, the full
source-policy runner package is not ready, and global submission readiness is
not claimed.

The narrowed archive boundary matches the reproducibility manifest: `True`.
Narrowed archive boundary tuple:
`narrowed_archive_ready_not_full_source_policy_runner_archive/0/40/False/False/True`.
Blocking ids/status: `OC4,OC6,OC12` /
`OC4=open,OC6=partial,OC12=partial`. Current archive use is
`narrowed_claim_only`, not a full source-policy runner archive.
Objective blocker matrix:
`blocker_open_by_id=OC4:True,OC6:True,OC12:True`;
`blocker_closure_decision_by_id=OC4:remain_open_ready_for_authorized_execution_not_executed_not_promoted,OC6:remain_open_no_positive_source_equivalent_artifact,OC12:remain_partial_narrowed_replay_ready_full_source_policy_archive_not_ready`;
`blocker_closure_allowed_by_id=OC4:False,OC6:False,OC12:False`.

The flat source is a packaging copy of `main_cmame.tex`. It preserves the same
scientific claim boundary: `Gauss6/FullVA`, conditional method order `6` under
the retained theorem interfaces, smooth orders `7.161/7.066`, local `m=3` TFE
comparator order `5`, four ASME-style examples, and
`full_tfe_stage_replacement=false`.

The proof route boundary is also unchanged: the accepted theorem uses the
direct 132-row residual-bridge/Kantorovich route, where the 96 non-dynamic
FullVA rows supply the \(O(h^7)\) block and the 36 Newton--Euler rows vanish
by direct substitution on the lifted Gauss stage. Primitive Taylor subterm
accounting is diagnostic and does not replace the retained endpoint/stability,
implementation-binding, solver-scale, and residual-to-error theorem
boundaries.

Build command from inside `cmame_submission_flat/`:

```bash
cmd.exe /c latexmk -pdf -interaction=nonstopmode main_cmame_submission.tex
```
