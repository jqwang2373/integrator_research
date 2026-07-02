# Submission File Inventory

This file lists the submission package by role. It is intentionally redundant
with `SUBMISSION_ARTIFACT_MANIFEST.json`; the manifest is machine-readable, and
this inventory is for human review before sending files out.

## Primary Submission Files

| File | Role | Required |
| --- | --- | --- |
| `main_cmame.pdf` | CMAME/Elsevier compiled manuscript. | Yes |
| `main_cmame.tex` | CMAME/Elsevier `elsarticle` source manuscript. | Yes |
| `highlights_cmame.txt` | Separate editable highlights file foregrounding the direct 132-row 96+36 proof bridge. | Yes |
| `declarations_cmame.md` | Separate declaration statements. | Yes |
| `CMAME_SUBMISSION_CHECKLIST.md` | CMAME/Elsevier format checklist. | Yes |
| `CMAME_SUBMISSION_READINESS_AUDIT.md` | Submission-readiness audit against CMAME/Elsevier package expectations. | Yes |
| `CMAME_SUBMISSION_READINESS_REVIEW.md` | Critical ARS-style review; global blockers remain, while the narrowed subcheck is bounded. | Yes |
| `CMAME_PDF_STYLE_REVIEW_AUDIT.md` | PDF-read comparison against the reference paper and current manuscript; narrowed subcheck passes while global boundaries remain. | Yes |
| `CMAME_PDF_STYLE_REVIEW_AUDIT.json` | Machine-readable PDF-style review with reference/manuscript text inventories and blocker findings. | Yes |
| `CMAME_SUBMISSION_INTEGRITY_AUDIT.md` | Local citation-key, reference-heading, submission-sidecar, and external reference verification audit. | Yes |
| `CMAME_SUBMISSION_INTEGRITY_AUDIT.json` | Machine-readable local submission-integrity audit with `external_reference_web_verification_complete=true`. | Yes |
| `CMAME_BLOCKER_CLOSURE_GATE.md` | Machine-checkable blocker ledger for the ARS-style review. | Yes |
| `CMAME_BLOCKER_CLOSURE_GATE.json` | Machine-readable blocker closure status and no-default-`1e-4` policy. | Yes |
| `CMAME_EXTERNAL_BASELINE_GATE.md` | Machine-checkable external same-test comparison boundary. | Yes |
| `CMAME_EXTERNAL_BASELINE_GATE.json` | Machine-readable external baseline status: no external superiority claim, no default `1e-4`, local closed-loop order, public work/precision, and strict common-reference rows available. | Yes |
| `CMAME_PROOF_CONTRACT_GATE.md` | Machine-checkable proof contract for the conditional theorem boundary. | Yes |
| `CMAME_PROOF_CONTRACT_GATE.json` | Machine-readable proof contract: `eta_h <= c_eta h^7` condition, symbolic-oracle gap, and residual-to-error non-acceptance. | Yes |
| `CMAME_VISUAL_LEGIBILITY_AUDIT.md` | Final-PDF visual legibility audit closing B5 without any default `1e-4` campaign. | Yes |
| `CMAME_VISUAL_LEGIBILITY_AUDIT.json` | Machine-readable visual legibility audit for B5 closure and remaining blocker count. | Yes |
| `CMAME_FIGURE_SET_AUDIT.md` | B7 figure-set audit checking all 13 main/flat/PDF figure integrations while keeping source-policy baseline figures open. | Yes |
| `CMAME_FIGURE_SET_AUDIT.json` | Machine-readable figure-set audit with Figure 12 all-method matrix and Figure 13 work/precision compendium integration plus B7 non-closure. | Yes |
| `CMAME_RELATED_WORK_AUDIT.md` | Related-work depth audit closing B8 with six literature clusters and explicit non-claim positioning. | Yes |
| `CMAME_RELATED_WORK_AUDIT.json` | Machine-readable related-work audit for B8 closure and remaining blocker count. | Yes |
| `CMAME_PROSE_RESIDUE_AUDIT.md` | B6 prose-residue audit proving the main manuscript body is machine-token free while artifact details remain in the appendix. | Yes |
| `CMAME_PROSE_RESIDUE_AUDIT.json` | Machine-readable B6 prose-residue audit with no-default-`1e-4` and no-`run_v047.py` markers. | Yes |
| `CMAME_CLAIM_HYGIENE_AUDIT.md` | Claim-hygiene audit enforcing the conditional order-comparison boundary and no source-policy/external-superiority overclaim. | Yes |
| `CMAME_CLAIM_HYGIENE_AUDIT.json` | Machine-readable claim-hygiene audit with forbidden-hit counts for submission and support files. | Yes |
| `DYNAMIC_ROW_ORACLE_GATE.md` | Runtime row-layout and block-functional oracle for the accepted 132-row residual. | Yes |
| `DYNAMIC_ROW_ORACLE_GATE.json` | Machine-readable runtime row/block oracle boundary; symbolic oracle remains open. | Yes |
| `README_CMAME_FLAT_SUBMISSION.md` | Notes for the flat source package. | Yes |
| `cmame_submission_flat/main_cmame_submission.tex` | Flat Editorial-Manager-oriented `elsarticle` source. | Yes |
| `cmame_submission_flat/main_cmame_submission.pdf` | PDF built from the flat source copy. | Yes |
| `cmame_submission_flat.zip` | Upload-ready flat LaTeX source archive. | Yes |
| `cmame_submission_flat/highlights_cmame.txt` | Flat copy of the editable highlights file. | Yes |
| `cmame_submission_flat/declarations_cmame.md` | Flat copy of the declarations file. | Yes |
| `cmame_submission_flat/Figure_1_convergence.png` | Flat figure file for convergence evidence. | Yes |
| `cmame_submission_flat/Figure_2_asme_lower_pair_graph_bridge.png` | Flat figure file for four-example lower-pair bridge. | Yes |
| `cmame_submission_flat/Figure_3_asme_closed_loop_kinematic_fullva.png` | Flat figure file for closed-loop mechanism evidence. | Yes |
| `cmame_submission_flat/Figure_4_order_closure_blend.png` | Flat figure file for full-TFE non-claim diagnostic. | Yes |
| `cmame_submission_flat/Figure_5_velocity_compression.png` | Flat figure file for velocity-compression diagnostic. | Yes |
| `cmame_submission_flat/Figure_6_sparse_speed_gap.png` | Flat figure file for sparse backend caveat. | Yes |
| `cmame_submission_flat/Figure_7_strict_common_reference_work_precision.png` | Flat figure file for strict common-reference closed-loop work/precision evidence. | Yes |
| `cmame_submission_flat/Figure_8_claim_boundary_limitations.png` | Flat figure file for the claim-boundary and limitation map. | Yes |
| `cmame_submission_flat/Figure_9_coarse_baseline_work_precision.png` | Flat figure file for coarse-first baseline/work-precision evidence. | Yes |
| `cmame_submission_flat/Figure_10_closed_loop_true_dynamic_order.png` | Flat figure file for closed-loop coarse-dynamics diagnostic evidence; filename is legacy, not an accepted asymptotic order claim. | Yes |
| `cmame_submission_flat/Figure_11_method_stage_architecture.png` | Flat figure file for the accepted method architecture and no-default-`1e-4` boundary. | Yes |
| `cmame_submission_flat/Figure_12_all_method_result_matrix.png` | Flat figure file for the all-method all-example common-reference result matrix. | Yes |
| `cmame_submission_flat/Figure_13_work_precision_compendium.png` | Flat figure file for the fair candidate/common-reference work/precision compendium. | Yes |
| `figures/convergence.png` | Figure file for convergence evidence. | Yes |
| `figures/asme_lower_pair_graph_bridge.png` | Figure file for four-example lower-pair bridge. | Yes |
| `figures/asme_closed_loop_kinematic_fullva.png` | Figure file for closed-loop mechanism evidence. | Yes |
| `figures/order_closure_blend.png` | Figure file for full-TFE non-claim diagnostic. | Yes |
| `figures/velocity_compression.png` | Figure file for velocity-compression diagnostic. | Yes |
| `figures/sparse_speed_gap.png` | Figure file for sparse backend caveat. | Yes |
| `figures/strict_common_reference_work_precision.png` | Figure file for strict common-reference closed-loop work/precision evidence. | Yes |
| `figures/claim_boundary_limitations.png` | Figure file for the claim-boundary and limitation map. | Yes |
| `figures/coarse_baseline_work_precision.png` | Figure file for coarse-first baseline/work-precision evidence. | Yes |
| `figures/closed_loop_true_dynamic_order.png` | Figure file for closed-loop coarse-dynamics diagnostic evidence; filename is legacy, not an accepted asymptotic order claim. | Yes |
| `figures/method_stage_architecture.png` | Figure file for the accepted method architecture and no-default-`1e-4` boundary. | Yes |
| `figures/all_method_result_matrix.png` | Figure file for the all-method all-example common-reference result matrix. | Yes |
| `figures/work_precision_compendium.png` | Figure file for the fair candidate/common-reference work/precision compendium. | Yes |
| `COVER_LETTER.md` | Cover letter draft with accepted claim and explicit non-claims. | Yes |
| `SUBMISSION_PACKET.md` | Short submission-facing index. | Yes |
| `SUBMISSION_ARTIFACT_MANIFEST.json` | Machine-readable submission manifest carrying the narrowed archive boundary tuple `narrowed_archive_ready_not_full_source_policy_runner_archive/0/40/False/False/True`, matching `CMAME_REPRODUCIBILITY_PACKAGE_MANIFEST.json`, with blocking ids/status `OC4,OC6,OC12` / `OC4=open,OC6=partial,OC12=partial`; current archive use is `narrowed_claim_only`, not a full source-policy runner archive. The objective completion matrix remains `blocker_open_by_id=OC4:True,OC6:True,OC12:True` and `blocker_closure_allowed_by_id=OC4:False,OC6:False,OC12:False`. | Yes |
| `SUBMISSION_FILE_INVENTORY.md` | Human-readable file inventory. | Yes |
| `REVIEW_RESPONSE_TEMPLATE.md` | Pre-scoped response template for likely reviewer questions. | Yes |
| `CLAIM_BOUNDARY.json` | Machine-readable claim boundary. | Yes |

## Supporting Evidence Files

| File | Role |
| --- | --- |
| `main_concise.pdf` | Concise supporting draft retained for audit continuity. |
| `main.pdf` | Full audit/status paper. |
| `PROOF_EVIDENCE_MATRIX.md` | Proof-obligation to artifact/validator evidence map. |
| `PROOF_NUMERICAL_SCALE_AUDIT.md` | Read-only audit of smooth h-sweep global error and endpoint-closure scaling. |
| `PROOF_NUMERICAL_SCALE_AUDIT.json` | Machine-readable scale audit: smooth-error fits, endpoint closure fits, and proof non-claims. |
| `PROOF_SOLVER_SCALE_AUDIT.md` | Read-only audit of summary-level solver residual records and why they are not a scaled `eta_h <= c_eta h^7` proof. |
| `PROOF_SOLVER_SCALE_AUDIT.json` | Machine-readable solver-scale audit with `theorem_level_scaled_tolerance_sweep_recorded=false` and no-default-`1e-4` markers. |
| `PROOF_SOLVER_SCALED_TOLERANCE_PROBE.md` | Finite one-step smooth solver-scale probe using `eta_h=c_eta h^7`, with `4/4` ok rows and theorem-level solver proof closure still false. |
| `PROOF_SOLVER_SCALED_TOLERANCE_PROBE.json` | Machine-readable scaled-tolerance probe with `max_final_residual_over_h7=127.58372278641149`. |
| `PROOF_SOLVER_SCALED_TOLERANCE_PROBE.csv` | Row-level h, target residual, final residual, residual-over-h^7, Newton iteration, and condition diagnostics for the finite probe. |
| `PROOF_SOLVER_SCALED_TOLERANCE_TRAJECTORY_PROBE.md` | Finite short-trajectory solver-scale probe using `eta_h=c_eta h^7` at each step, with `4/4` ok rows, `30` checked steps, and theorem-level solver proof closure still false. |
| `PROOF_SOLVER_SCALED_TOLERANCE_TRAJECTORY_PROBE.json` | Machine-readable trajectory probe with `max_final_residual_over_h7=210.89078604575462`. |
| `PROOF_SOLVER_SCALED_TOLERANCE_TRAJECTORY_PROBE.csv` | Row-level h, trajectory-step, residual-over-h^7, Newton iteration, Jacobian-rank, and condition diagnostics for the finite trajectory probe. |
| `PROOF_SOLVER_TOLERANCE_REGIME_SWEEP.md` | Finite short-trajectory solver-policy comparison among fixed `1e-10`, `c h^7`, and `c h^8` tolerances, with `12` policy rows, `90` checked steps, and theorem-level solver proof closure still false. |
| `PROOF_SOLVER_TOLERANCE_REGIME_SWEEP.json` | Machine-readable tolerance-regime sweep with `finite_tolerance_regime_sweep_recorded=true` and no theorem-level solver proof closure. |
| `PROOF_SOLVER_TOLERANCE_REGIME_SWEEP.csv` | Row-level policy, h, tolerance, residual, error, observed-order, Newton iteration, and condition diagnostics for the finite tolerance-regime sweep. |
| `PROOF_CLAIM_TRACEABILITY_AUDIT.md` | Read-only proof-claim traceability audit over the CMAME proof labels, theorem boundary tokens, and open proof obligations. |
| `PROOF_CLAIM_TRACEABILITY_AUDIT.json` | Machine-readable proof traceability audit with `1/7` theorem interfaces submission-satisfied, `5/7` retained theorem interfaces, `1/7` open P7 nonpromotion boundary, `4/0` close requirements/unsatisfied close requirements, `96` certified non-dynamic rows, `36/0` active direct Newton--Euler closed/open rows, `36` symbolic/primitive-route Newton--Euler rows not certified by that route, and `submission_ready=false`. |
| `CMAME_BLOCKER_CLOSURE_GATE.md` | Machine-checkable blocker ledger for the ARS-style review. |
| `CMAME_BLOCKER_CLOSURE_GATE.json` | Machine-readable blocker closure status and no-default-`1e-4` policy. |
| `CMAME_EXTERNAL_BASELINE_GATE.md` | Human-readable external comparison gate for the not-yet-closed same-test campaign. |
| `CMAME_EXTERNAL_BASELINE_GATE.json` | Machine-readable external comparison gate cross-checked against v048 readiness and performance summaries. |
| `CMAME_PROOF_CONTRACT_GATE.md` | Human-readable conditional proof contract for the CMAME theorem language. |
| `CMAME_PROOF_CONTRACT_GATE.json` | Machine-readable proof contract cross-checked against the manuscript, order gate, dynamic oracle, and residual-to-error obligations. |
| `CMAME_SUBMISSION_INTEGRITY_AUDIT.md` | Local citation-key and submission-sidecar audit; records local citation integrity and external reference web verification passed. |
| `CMAME_SUBMISSION_INTEGRITY_AUDIT.json` | Machine-readable submission-integrity audit consumed by the review agent and validators. |
| `CMAME_VISUAL_LEGIBILITY_AUDIT.md` | Final-PDF visual legibility audit closing B5 without any default `1e-4` campaign. |
| `CMAME_VISUAL_LEGIBILITY_AUDIT.json` | Machine-readable visual legibility audit for B5 closure and remaining blocker count. |
| `CMAME_FIGURE_SET_AUDIT.md` | B7 figure-set audit checking all 13 main/flat/PDF figure integrations while keeping source-policy baseline figures open. |
| `CMAME_FIGURE_SET_AUDIT.json` | Machine-readable figure-set audit with Figure 12 all-method matrix and Figure 13 work/precision compendium integration plus B7 non-closure. |
| `CMAME_RELATED_WORK_AUDIT.md` | Related-work depth audit closing B8 with six literature clusters and explicit non-claim positioning. |
| `CMAME_RELATED_WORK_AUDIT.json` | Machine-readable related-work audit for B8 closure and remaining blocker count. |
| `CMAME_PROSE_RESIDUE_AUDIT.md` | Read-only B6 prose-residue audit: main-body machine-token count is zero and artifact filenames stay in the reproducibility appendix. |
| `CMAME_PROSE_RESIDUE_AUDIT.json` | Machine-readable prose-residue audit with `default_1e-4_required=false` and `run_v047_invoked=false`. |
| `CMAME_CLAIM_HYGIENE_AUDIT.md` | Read-only text audit proving the CMAME-facing claim remains a conditional formal-order comparison. |
| `CMAME_CLAIM_HYGIENE_AUDIT.json` | Machine-readable claim-hygiene audit consumed by the CMAME review agent. |
| `DYNAMIC_ROW_ORACLE_GATE.md` | Runtime row-layout and block-functional oracle for the accepted 132-row residual. |
| `DYNAMIC_ROW_ORACLE_GATE.json` | Machine-readable runtime row/block oracle boundary; symbolic oracle remains open. |
| `ORDER_ACCEPTANCE_GATE.md` | Human-readable gate separating accepted method order, four-example coverage, and open external dynamic-order evidence. |
| `ORDER_ACCEPTANCE_GATE.json` | Machine-readable order gate checked against v047/v048 summary artifacts. |
| `IMPLEMENTATION_FIDELITY_CERTIFICATE.md` | Static source-identity certificate tying the accepted 132-row residual to `residual_cylindrical_chain` and `R_JAC`. |
| `IMPLEMENTATION_PATH_AUDIT.md` | Read-only static audit of the accepted 132-row residual implementation path. |
| `IMPLEMENTATION_PATH_AUDIT.json` | Machine-readable implementation path audit with `implementation_path_check_for_132_row_residual=true`. |
| `KINEMATIC_ROW_DEFECT_CERTIFICATE.md` | Partial proof-scope certificate for the 96 non-dynamic collocation/lower-pair rows on the smooth accepted FullVA lift. |
| `KINEMATIC_ROW_DEFECT_CERTIFICATE.json` | Machine-readable partial row-defect certificate for the 96 non-dynamic rows; the later D5 direct-substitution contract closes the 36 `newton_euler_weak_balance` rows by a separate route. |
| `NEWTON_EULER_DEFECT_OBLIGATION_GATE.md` | Non-active primitive/symbolic obligation ledger for the 36 Newton-Euler rows; it records one open D5 symbolic obligation plus closed D1/D2/D3/D4/D6 sub-obligations without reopening the active direct-PC2 route. |
| `NEWTON_EULER_DEFECT_OBLIGATION_GATE.json` | Machine-readable Newton-Euler obligation gate with `open_obligation_count=1`, `closed_obligation_count=5`, and no-default-`1e-4` markers. |
| `NEWTON_EULER_BALANCE_IDENTITY_AUDIT.md` | D1/D2 source-level Newton-Euler balance-identity audit for all 36 dynamic rows; D5 remains open only in the optional symbolic lane. |
| `NEWTON_EULER_BALANCE_IDENTITY_AUDIT.json` | Machine-readable D1/D2 balance-identity audit with 36 closed identity rows and no optional-symbolic D5 closure claim. |
| `NEWTON_EULER_VIRTUAL_WORK_WRENCH_AUDIT.md` | D3 virtual-work sign-skeleton/template/row-expanded identity audit for the 36 Newton-Euler dynamic rows; it is an input to the later direct-substitution proof closure, not the full closure artifact by itself. |
| `NEWTON_EULER_VIRTUAL_WORK_WRENCH_AUDIT.json` | Machine-readable D3-only audit with `checked_rows=36`, `multiplier_wrench_consistency_closed=true`, and scoped `proof_gap_closed=false`; the local D3 marker does not reopen the active direct D5/PC2 closure. |
| `NEWTON_EULER_SYMBOLIC_DEFECT_CERTIFICATE.md` | Open primitive/symbolic certificate scaffold with 36 Newton-Euler row slots; it is not the active direct-substitution closure artifact. |
| `NEWTON_EULER_SYMBOLIC_DEFECT_CERTIFICATE.json` | Machine-readable primitive/symbolic certificate scaffold with `certificate_complete=false`, `certified_row_count=0`, and `open_row_count=36`; these fields do not reopen the accepted direct route. |
| `NEWTON_EULER_DYNAMIC_ROW_CLOSURE_CONTRACT.md` | Row-level closure contract for the 36 Newton-Euler dynamic rows: full runtime traceability is recorded and direct-substitution row-defect closure supplies the direct-PC2 theorem input for `36/36` rows. |
| `NEWTON_EULER_DYNAMIC_ROW_CLOSURE_CONTRACT.json` | Machine-readable dynamic-row closure contract with direct-route `PC1/PC2` closure and preferred `direct_pc2_proof_gap_closed=true`; the legacy `proof_gap_closed` key is retained only with that direct-PC2 scope, while the primitive/Taylor route and dynamic symbolic oracle remain open. |
| `D5_DYNAMIC_DIRECT_SUBSTITUTION_CERTIFICATE.md` | Direct-substitution D5 certificate showing the 36 Newton-Euler rows have zero residual on the smooth FullVA Gauss lift, without using `P_state`, `P_acc`, `P_lambda`, finite probes, or residual-to-error promotion. |
| `D5_DYNAMIC_DIRECT_SUBSTITUTION_CERTIFICATE.json` | Machine-readable direct-substitution certificate with `dynamic_zero_residual_rows=36`, active direct-bridge `full_stage_rows_when_assembled_by_bridge=132`, and `direct_route_certificate_closed=true`; the legacy `full_stage_rows_if_promoted` key is retained only for schema compatibility. |
| `D5_TAYLOR_TERM_BUDGET_AUDIT.md` | Term-level optional D5 Taylor budget splitting the non-active primitive/symbolic 36-row dynamic lane into 162 Taylor subterms; zero term-level bounds are certified. |
| `D5_TAYLOR_TERM_BUDGET_AUDIT.json` | Machine-readable D5 Taylor term budget with `term_rows=162`, `certified_taylor_bound_terms=0`, and `primitive_taylor_pc2_closed=false`. |
| `D5_PRIMITIVE_BOUND_REDUCTION_AUDIT.md` | Primitive-bound D5 reduction map grouping the 162 optional-lane Taylor subterms into six primitive obligations; only the compact-tube primitive is proved. |
| `D5_PRIMITIVE_BOUND_REDUCTION_AUDIT.json` | Machine-readable primitive-bound reduction audit with `term_rows_with_reduction_rule=162`, `primitive_obligations_proved=1`, and `primitive_taylor_pc2_closed=false`. |
| `D5_P_TUBE_CONSTANTS_AUDIT.md` | Compact proof-tube constants audit closing only `P_uniform_tube_constants`; five lift/bilinear primitives remain open. |
| `D5_P_TUBE_CONSTANTS_AUDIT.json` | Machine-readable P_tube audit with `primitive_obligations_closed=1`, `induced_taylor_bounds_proved=0`, and `primitive_taylor_pc2_closed=false`. |
| `D5_P_STATE_LIFT_GAP_AUDIT.md` | P_state gap audit recording that PS1, aggregate PS2, and PS4 are closed while actual PS3 still blocks the `P_state` variable-lift bound. |
| `D5_P_STATE_LIFT_GAP_AUDIT.json` | Machine-readable P_state gap audit with `primitive_closed=false`, `required_future_subproofs_closed=3`, and `primitive_taylor_pc2_closed=false`. |
| `D5_P_STATE_MAP_DEFINITION_AUDIT.md` | PS1 audit defining the non-dynamic stage map `N_h^nd(S,A)` in the accepted Lie chart while keeping the P_state lift proof open. |
| `D5_P_STATE_MAP_DEFINITION_AUDIT.json` | Machine-readable P_state map-definition audit with `ps1_map_definition_closed=true`, `primitive_closed=false`, and `primitive_taylor_pc2_closed=false`. |
| `D5_P_STATE_ANTICIRCULARITY_AUDIT.md` | PS4 audit proving the future P_state inverse/lift route cannot use the D5 dynamic residual defect, Lemma `stage-residual-defect`, or residual identities alone. |
| `D5_P_STATE_ANTICIRCULARITY_AUDIT.json` | Machine-readable P_state anti-circularity audit with `ps4_anticircularity_closed=true`, `primitive_closed=false`, and `primitive_taylor_pc2_closed=false`. |
| `D5_P_STATE_PS2_WEIGHTED_TARGET_AUDIT.md` | PS2 target-specification audit replacing the invalid full-domain inverse expectation with the weighted state estimate `||delta S|| <= C_PS2 (||delta N_h^nd|| + h ||delta A||)` while keeping the inverse/inf-sup proof open. |
| `D5_P_STATE_PS2_WEIGHTED_TARGET_AUDIT.json` | Machine-readable P_state PS2 target audit with `ps2_weighted_target_spec_closed=true`, `ps2_inverse_or_infsup_closed=false`, and `primitive_taylor_pc2_closed=false`. |
| `D5_P_STATE_PS2_AGGREGATE_PROMOTION_AUDIT.md` | Aggregate PS2 promotion audit proving the uniform weighted inverse from the component Taylor/mean-value proof while keeping PS3, P_state, and PC2 open. |
| `D5_P_STATE_PS2_AGGREGATE_PROMOTION_AUDIT.json` | Machine-readable aggregate PS2 audit with `ps2_inverse_or_infsup_closed=true`, `primitive_closed=false`, and `primitive_taylor_pc2_closed=false`. |
| `D5_P_STATE_PS2_LINEARIZATION_PROBE.md` | Finite solved-stage PS2 weighted linearization diagnostic showing full column rank for the implemented non-dynamic weighted operator while keeping the uniform inf-sup proof open. |
| `D5_P_STATE_PS2_LINEARIZATION_PROBE.json` | Machine-readable finite PS2 linearization probe with `finite_probe_full_column_rank_all=true`, `uniform_constant_proved=false`, and `primitive_taylor_pc2_closed=false`. |
| `D5_P_STATE_PS2_LINEARIZATION_PROBE.csv` | Per-step-size finite PS2 linearization probe table for `h=0.04,0.02,0.01`. |
| `D5_P_STATE_PS3_CONDITIONAL_CONVERSION_AUDIT.md` | PS3 conditional-conversion audit showing that aggregate PS2 plus instantiated residual and h-weighted acceleration inputs would imply `O(h^7)` state lift, while keeping the actual PS3 lift proof open. |
| `D5_P_STATE_PS3_CONDITIONAL_CONVERSION_AUDIT.json` | Machine-readable P_state PS3 audit with `ps3_conditional_conversion_closed=true`, `ps3_actual_state_lift_conversion_closed=false`, and `primitive_taylor_pc2_closed=false`. |
| `D5_P_STATE_PS3_ACTUAL_INSTANTIATION_GAP_AUDIT.md` | PS3 actual-instantiation gap audit showing that aggregate PS2 and the 96-row certificate are available while the independent non-circular h-weighted acceleration input remains open. |
| `D5_P_STATE_PS3_ACTUAL_INSTANTIATION_GAP_AUDIT.json` | Machine-readable P_state PS3 actual-instantiation gap audit with `input_requirements_closed=2`, `ps3_actual_state_lift_conversion_closed=false`, and `primitive_taylor_pc2_closed=false`. |
| `D5_P_STATE_PS3_H_ACC_INPUT_OBSTRUCTION_AUDIT.md` | H-acceleration input obstruction audit showing that residual-only non-dynamic rows do not supply the independent PS3 `h delta A` input. |
| `D5_P_STATE_PS3_H_ACC_INPUT_OBSTRUCTION_AUDIT.json` | Machine-readable h-acceleration input obstruction audit with residual-only nullity `12`-`12`, `finite_probe_is_proof=false`, and actual PS3/PC2 still open. |
| `D5_P_ACC_MAP_DEFINITION_AUDIT.md` | PA1 audit defining the accepted acceleration map `A_h^acc(A)` and binding it to the 36 acceleration-lift D5 rows while keeping the acceleration lift proof open. |
| `D5_P_ACC_MAP_DEFINITION_AUDIT.json` | Machine-readable P_acc map-definition audit with `pa1_map_definition_closed=true`, `primitive_closed=false`, and `primitive_taylor_pc2_closed=false`. |
| `D5_P_ACC_ROW_BINDING_AUDIT.md` | PA4 audit binding the accepted acceleration-lift rows to D6 row ordering and D5 Taylor-term rows while keeping the acceleration lift proof open. |
| `D5_P_ACC_ROW_BINDING_AUDIT.json` | Machine-readable P_acc row-binding audit with `pa4_row_binding_closed=true`, `primitive_closed=false`, and `primitive_taylor_pc2_closed=false`. |
| `D5_P_ACC_INDEPENDENCE_AUDIT.md` | PA3 audit proving the acceleration-lift proof route uses only non-dynamic FullVA rows and bars Newton-Euler balance rows as inputs while keeping PA2 open. |
| `D5_P_ACC_INDEPENDENCE_AUDIT.json` | Machine-readable P_acc independence audit with `pa3_independence_closed=true`, `primitive_closed=false`, and `primitive_taylor_pc2_closed=false`. |
| `D5_P_ACC_LIFT_OBSTRUCTION_AUDIT.md` | PA2 obstruction audit showing that velocity-collocation rows alone lose one power of `h` when inverted for acceleration differences, so the acceleration lift remains open. |
| `D5_P_ACC_LIFT_OBSTRUCTION_AUDIT.json` | Machine-readable P_acc lift-obstruction audit with `pa2_obstruction_recorded=true`, `pa2_closed=false`, current unweighted acceleration rate `O(h^6)`, and `primitive_taylor_pc2_closed=false`. |
| `D5_P_ACC_PA2_WEIGHTED_INVERSE_AUDIT.md` | PA2 weighted-inverse diagnostic recording finite projection constants for `delta S`, `delta A`, and `h delta A` while keeping the unweighted acceleration lift open. |
| `D5_P_ACC_PA2_WEIGHTED_INVERSE_AUDIT.json` | Machine-readable PA2 weighted-inverse audit with finite full-rank diagnostics, `unweighted_acceleration_uniform_control_proved=false`, `pa2_closed=false`, and `primitive_taylor_pc2_closed=false`. |
| `D5_P_LAMBDA_INTERFACE_AUDIT.md` | PL1 audit exposing the lower-pair multiplier variables and KKT/Newton-Euler column interface while keeping multiplier lift and inf-sup proofs open. |
| `D5_P_LAMBDA_INTERFACE_AUDIT.json` | Machine-readable P_lambda interface audit with `pl1_interface_closed=true`, `primitive_closed=false`, and `primitive_taylor_pc2_closed=false`. |
| `D5_P_LAMBDA_INF_SUP_PROBE.md` | Finite solved-stage multiplier-column rank diagnostic for `D_lambda R_dyn`; it supports the PL2 target while keeping the uniform inf-sup proof open. |
| `D5_P_LAMBDA_INF_SUP_PROBE.json` | Machine-readable P_lambda inf-sup probe with `finite_probe_full_column_rank_all=true`, `uniform_constant_proved=false`, and `primitive_taylor_pc2_closed=false`. |
| `D5_P_LAMBDA_INF_SUP_PROBE.csv` | Per-step-size P_lambda finite rank probe table for `h=0.04,0.02,0.01`. |
| `D5_P_LAMBDA_PL2_GEOMETRIC_MARGIN_AUDIT.md` | PL2 geometric-margin route audit separating the dynamic-lambda, translational normal-force, rotational axis-torque, and direct-sum subblocks; the compact-tube inf-sup subproof is closed while `P_lambda` remains open. |
| `D5_P_LAMBDA_PL2_GEOMETRIC_MARGIN_AUDIT.json` | Machine-readable PL2 geometric-margin audit with finite full-rank diagnostics, `pl2_uniform_inf_sup_bound_proved=true`, `primitive_closed=false`, and `primitive_taylor_pc2_closed=false`. |
| `D5_P_LAMBDA_D3_NONCIRCULARITY_AUDIT.md` | PL3 audit proving D3 wrench consistency is used only as a non-circular algebraic mapping interface while not proving the multiplier lift, `P_lambda`, or PC2. |
| `D5_P_LAMBDA_D3_NONCIRCULARITY_AUDIT.json` | Machine-readable P_lambda D3 non-circularity audit with `pl3_d3_noncircularity_closed=true`, `primitive_closed=false`, and `primitive_taylor_pc2_closed=false`. |
| `D5_P_LAMBDA_PL4_RATE_PROPAGATION_AUDIT.md` | PL4 conditional multiplier-rate propagation audit proving the Taylor/implicit-function propagation from state and acceleration lift inputs while keeping `P_lambda` open. |
| `D5_P_LAMBDA_PL4_RATE_PROPAGATION_AUDIT.json` | Machine-readable PL4 audit with `pl4_lift_propagation_closed=true`, `conditional_multiplier_lift_rate_proved=true`, `multiplier_lift_rate_proved=false`, and `primitive_taylor_pc2_closed=false`. |
| `D5_P_GEOM_CHART_REDUCTION_AUDIT.md` | Accepted-chart P_geom reduction audit closing the Lipschitz estimate for multiplier-wrench geometry while keeping the primitive open pending `P_state` and `P_lambda`. |
| `D5_P_GEOM_CHART_REDUCTION_AUDIT.json` | Machine-readable P_geom audit with `chart_reduction_closed=true`, `primitive_closed=false`, and `primitive_taylor_pc2_closed=false`. |
| `D5_P_GYRO_BILINEAR_REDUCTION_AUDIT.md` | Algebraic P_gyro reduction audit closing the bilinear Lipschitz estimate for `omega x J omega` while keeping the primitive open pending `P_state`. |
| `D5_P_GYRO_BILINEAR_REDUCTION_AUDIT.json` | Machine-readable P_gyro audit with `algebraic_reduction_closed=true`, `primitive_closed=false`, and `primitive_taylor_pc2_closed=false`. |
| `D5_OPEN_PRIMITIVE_GAP_AUDIT.md` | Five-open-primitive proof-gap ledger for `P_state`, `P_acc`, `P_lambda`, `P_geom`, and `P_gyro`; P_geom/P_gyro have conditional reductions but no primitive or PC2 closure is claimed. |
| `D5_OPEN_PRIMITIVE_GAP_AUDIT.json` | Machine-readable open primitive gap audit with `open_primitive_count=5`, `future_subproofs_closed=16`, and `primitive_taylor_pc2_closed=false`. |
| `D5_PRIMITIVE_OBLIGATION_CLOSURE_PLAN.md` | Primitive-obligation closure plan recording the six proof interfaces that would imply the 162 D5 bounds; one compact-tube primitive is proved. |
| `D5_PRIMITIVE_OBLIGATION_CLOSURE_PLAN.json` | Machine-readable closure plan with `primitive_obligations_proved=1`, `induced_taylor_bounds_proved=0`, and `primitive_taylor_pc2_closed=false`. |
| `D5_CONDITIONAL_TAYLOR_CERTIFICATE.md` | Conditional D5 Taylor certificate proving the finite implication from the five open primitive assumptions to all 162 subterm bounds while keeping actual proof closure open. |
| `D5_CONDITIONAL_TAYLOR_CERTIFICATE.json` | Machine-readable conditional Taylor certificate with `conditional_terms=162/162`, `conditional_rows=36/36`, `actual_taylor_bounds_proved=0`, and `primitive_taylor_pc2_closed=false`. |
| `NEWTON_EULER_ROW_ORDERING_SCALING_AD_AUDIT.md` | D6 closure audit proving row ordering, unweighted residual scaling, and accepted AD binding for the 36 Newton-Euler dynamic rows. |
| `NEWTON_EULER_ROW_ORDERING_SCALING_AD_AUDIT.json` | Machine-readable D6-only audit with `symbolic_runtime_row_equivalence_closed=true`; its local `stage_residual_O_h7_implementation_defect_proved=false` marker does not reopen the active direct 132-row proof route. |
| `../v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_local_row_plan.json` | Machine-readable plan-only next-row contract for four-link/slider-crank true-dynamic local rows, with no default `1e-4` execution. |
| `../v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_local_row_plan.csv` | Row-level plan for 6 local target rows and 18 public comparator rows under `h=[0.1,0.05,0.025]`. |
| `../v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_local_row_plan.md` | Human-readable explanation of the plan-only true-dynamic row contract. |
| `../v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_interface_audit.json` | Machine-readable setup-level audit proving the public/v046 dynamics interfaces instantiate without running trajectory rows. |
| `../v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_interface_audit.csv` | Row-level setup audit for kinematic and dynamic modes on four-link/slider-crank. |
| `../v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_interface_audit.md` | Human-readable explanation of the remaining local `Gauss6/FullVA` dynamic runner gap. |
| `../v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_residual_scaffold.json` | Machine-readable residual layout contract for the missing closed-loop `Gauss6/FullVA` dynamic runner. |
| `../v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_residual_scaffold.csv` | Row-level square-system dimensions: 72 unknowns/residuals per stage and 216 per Gauss6 step. |
| `../v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_residual_scaffold.md` | Human-readable explanation of the residual scaffold and its no-order/no-`1e-4` boundary. |
| `../v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_stage_residual_audit.json` | Machine-readable audit that the stage residual evaluator reaches roundoff residuals on the two closed-loop mechanisms. |
| `../v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_stage_residual_audit.csv` | Six Gauss6 stage residual-evaluator rows for four-link/slider-crank; no trajectory stepper is executed. |
| `../v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_stage_residual_audit.md` | Human-readable explanation that stage residual evaluation is verified but dynamic order remains open. |
| `../v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_one_step_smoke.json` | Machine-readable one-step Gauss6 closed-loop dynamic smoke; endpoint advancement executes but no convergence sweep is run. |
| `../v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_one_step_smoke.csv` | Two one-step smoke rows for four-link/slider-crank at `h=0.1`, with no accepted dynamic order. |
| `../v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_one_step_smoke.md` | Human-readable explanation that one-step endpoint advancement is implementation progress, not order evidence. |
| `../v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_newton_stage_smoke.json` | Machine-readable non-oracle Newton stage smoke; stage residuals converge from start-state extrapolated predictors without stage-time kinematic oracle roots. |
| `../v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_newton_stage_smoke.csv` | Two non-oracle Newton one-step smoke rows for four-link/slider-crank at `h=0.1`, with no accepted dynamic order. |
| `../v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_newton_stage_smoke.md` | Human-readable explanation that the Newton stage smoke removes the stage-time oracle but is still not order evidence. |
| `../v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_newton_coarse_order.json` | Machine-readable non-oracle local true-dynamic coarse order summary for four-link/slider-crank; external superiority remains false. |
| `../v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_newton_coarse_order_rows.csv` | Six coarse local dynamic rows at `h=[0.1,0.05,0.025]`, reference `h=0.0125`, with primary-state order candidates accepted locally. |
| `../v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_newton_coarse_order.md` | Human-readable explanation of the local order result and the remaining public comparison caveat. |
| `../v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_public_work_precision.json` | Machine-readable same-window public work/precision summary for four-link/slider-crank; external superiority remains false because it carries the historical mixed-reference caveat. |
| `../v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_public_work_precision_rows.csv` | Twenty-four raw local/public rows at `h=[0.1,0.05,0.025]`, reference `h=0.0125`, with no default `1e-4` execution. |
| `../v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_public_work_precision_summary.csv` | Eight method-level work/precision summary rows for local true-dynamic Newton and public `rA/rp/reps` baselines. |
| `../v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_public_work_precision.md` | Human-readable explanation of the public work/precision availability and strict common-reference caveat. |
| `../v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_strict_common_reference.json` | Machine-readable strict common-reference public work/precision summary for four-link/slider-crank against the v047 exact endpoint reference. |
| `../v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_strict_common_reference_rows.csv` | Twenty-four raw local/public strict common-reference rows at `h=[0.1,0.05,0.025]`; no default `1e-4` execution. |
| `../v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_strict_common_reference_summary.csv` | Eight method-level strict common-reference work/precision summary rows. |
| `../v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_strict_common_reference.md` | Human-readable explanation of the strict common-reference closure and remaining no-superiority boundary. |
| `../v048_cross_paper_same_test_benchmarks/results/closed_loop_true_dynamic_strict_common_reference_work_precision.png` | Work/precision figure generated from the strict common-reference rows; integrated as Figure 7 in the CMAME manuscript and flat package. |
| `../v048_cross_paper_same_test_benchmarks/results/closed_loop_residual_to_error_theorem_obligations.json` | Machine-readable seven-obligation gate blocking residual-to-error promotion for closed-loop dynamic order. |
| `../v048_cross_paper_same_test_benchmarks/results/closed_loop_residual_to_error_theorem_obligations.csv` | Row-level residual-to-error theorem obligations R2E-1 through R2E-7. |
| `../v048_cross_paper_same_test_benchmarks/results/closed_loop_residual_to_error_theorem_obligations.md` | Human-readable explanation that small residuals are not yet trajectory-error/order proof. |
| `SOURCE_PAPER_COMPARISON.md` | Short source-paper versus v047 comparison boundary. |
| `CROSS_PAPER_BENCHMARK_MATRIX.md` | Same-test external benchmark matrix for the original paper and Kissel/Negrut-related suites. |
| `CROSS_PAPER_BENCHMARK_SPEC.md` | Extracted public-code benchmark specification and current v047 mismatch audit. |
| `CROSS_PAPER_BENCHMARK_CASES.json` | Machine-readable same-test case inventory, including unresolved velocity-partitioning code-path discovery. |
| `EXTERNAL_SAME_TEST_RUN_QUEUE.md` | Human-readable coarse-first parallel run queue for the 17 remaining external same-test cases. |
| `EXTERNAL_SAME_TEST_RUN_QUEUE.json` | Machine-readable run queue with 20 non-default-`1e-4` parallel shards and explicit not-ready source/code batches. |
| `EXTERNAL_SAME_TEST_ACCEPTANCE_SHEET.md` | Human-readable B2/B4 acceptance sheet fixing the required same-test metrics without a default `1e-4` campaign. |
| `EXTERNAL_SAME_TEST_ACCEPTANCE_SHEET.json` | Machine-readable acceptance sheet with `accepted_external_dynamic_order_examples=0`, 20 non-default-`1e-4` shards, and no external-superiority claim. |
| `KISSEL_NEGRUT_CODE_INVENTORY.md` | Multi-paper Kissel/Negrut public-code inventory and no-merged-baseline guardrail. |
| `PAPER_RESULT_PACK.md` | Paper-facing v048 result consolidation, including the full 11-method by 4-example common-reference order/error matrix. |
| `PAPER_RESULT_PACK.json` | Machine-readable result pack used by the submission review agent. |
| `PAPER_NUMERICAL_RESULT_MATRIX.md` | Paper-facing all-method order/error matrix: `44/44` method/example cells from `132` raw rows with source-policy boundaries. |
| `PAPER_NUMERICAL_RESULT_MATRIX.json` | Machine-readable 44-cell numerical result matrix consumed by the review agent and package validators. |
| `PAPER_NUMERICAL_RESULT_MATRIX.csv` | CSV form of the paper numerical result matrix for table generation and audit reuse. |
| `RESULT_TO_MANUSCRIPT_TRACEABILITY_AUDIT.md` | Verifies that all `44/44` velocity order/error cells in the all-method matrix appear in main/flat CMAME TeX and extracted PDF text. |
| `RESULT_TO_MANUSCRIPT_TRACEABILITY_AUDIT.json` | Machine-readable result-to-manuscript traceability audit with source-policy and external-superiority gates kept open. |
| `ALL_METHOD_EXAMPLE_CLAIM_DISPOSITION_AUDIT.md` | All-method claim-disposition audit over `40/40` nonlocal method/example rows, recording `40/40` local order/error wins and `0/40` source-policy-closed nonlocal rows. |
| `ALL_METHOD_EXAMPLE_CLAIM_DISPOSITION_AUDIT.json` | Machine-readable all-method claim-disposition audit consumed by the review agent and validators. |
| `ALL_EXAMPLES_RESULT_SANITY_AUDIT.md` | All-example sanity audit over the 44-cell method/example matrix; locks the exact `15` flagged nonlocal rows that need source-policy recheck before any external-superiority claim. |
| `ALL_EXAMPLES_RESULT_SANITY_AUDIT.json` | Machine-readable all-example sanity audit consumed by the CMAME review agent. |
| `COMMON_REFERENCE_ORDER_RECOMPUTATION_AUDIT.md` | Independent recomputation of every common-reference order and finest error from the 132 raw rows. |
| `COMMON_REFERENCE_ORDER_RECOMPUTATION_AUDIT.json` | Machine-readable raw-row arithmetic audit showing 44/44 recomputed cells and zero summary mismatches. |
| `EXTERNAL_BASELINE_SOURCE_POLICY_DIAGNOSIS.md` | Diagnosis of the 15 flagged external baseline rows, separating arithmetic-verified results from source-policy mismatch risks. |
| `EXTERNAL_BASELINE_SOURCE_POLICY_DIAGNOSIS.json` | Machine-readable source-policy diagnosis used by the CMAME review agent to keep B2/B4 open. |
| `SOURCE_POLICY_CLOSURE_TRIAGE.md` | Human-readable closure triage for all 15 flagged source-policy rows across all four examples. |
| `SOURCE_POLICY_CLOSURE_TRIAGE.json` | Machine-readable fix/rerun/demote action plan for the flagged source-policy rows. |
| `SOURCE_POLICY_ROW_CLOSURE_LEDGER.md` | Row-level closure ledger listing the evidence still required for each of the 15 flagged source-policy rows. |
| `SOURCE_POLICY_ROW_CLOSURE_LEDGER.json` | Machine-readable row-level ledger with zero source-policy-closed rows, zero external-superiority-ready rows, and 20 non-default-`1e-4` parallel-ready shards. |
| `SOURCE_POLICY_LOCAL_CANDIDATE_GAP_AUDIT.md` | Read-only row-gap audit explaining why existing local Gauss6/FullVA candidate rows do not yet close RA2021, HI2022, or TFE source-policy superiority. |
| `SOURCE_POLICY_LOCAL_CANDIDATE_GAP_AUDIT.json` | Machine-readable local-candidate gap audit with RA/HI/TFE suite summaries, zero accepted source-policy dynamic-order examples, and no-run/no-claim boundary. |
| `ALL_EXAMPLES_SOURCE_POLICY_AUDIT.md` | All-example source-policy audit checking every flagged row across the four examples, including setup, fixed-grid replay, state-output source, and non-claim boundaries. |
| `ALL_EXAMPLES_SOURCE_POLICY_AUDIT.json` | Machine-readable source-policy audit: 15 flagged summary rows, 45 raw rows, four examples, and B2/B4 still open. |
| `EXTERNAL_SUITE_DISPOSITION_AUDIT.md` | Suite-level disposition audit for the original TFE and Kissel/Negrut-related external comparisons; keeps B2/B4 open until run-or-demote decisions close. |
| `EXTERNAL_SUITE_DISPOSITION_AUDIT.json` | Machine-readable suite disposition audit with four suites, zero accepted external-superiority suites, and 20 non-default-`1e-4` parallel-ready shards. |
| `EXTERNAL_SOURCE_POLICY_CLOSURE_MANIFEST.md` | Source-policy closure manifest separating bounded common-reference evidence from source-policy reproduction closure. |
| `EXTERNAL_SOURCE_POLICY_CLOSURE_MANIFEST.json` | Machine-readable source-policy closure manifest with 32/48 performance rows completed, zero strict external error-claim rows, and B2/B4 open. |
| `EXTERNAL_CASE_EVIDENCE_RECONCILIATION.md` | Reconciles case-inventory `not_run` markers with current bounded/coarse evidence for RA2021 and HI2022, while keeping source-policy closure open. |
| `EXTERNAL_CASE_EVIDENCE_RECONCILIATION.json` | Machine-readable reconciliation: RA2021/HI2022 bounded evidence present, TFE2026/VP2024 not-ready or demote, 0/15 closed rows. |
| `RA2021_SOURCE_IDENTITY_AUDIT.md` | RA2021 source-code identity audit verifying `body.r/body.dr/body.ddr` output mapping and extracting the public time-grid convention; source-policy promotion remains open. |
| `RA2021_SOURCE_IDENTITY_AUDIT.json` | Machine-readable RA2021 source-code identity audit consumed by the review agent and validators. |
| `HI2022_T8_TOLERANCE_REPAIR_AUDIT.md` | HI2022 T=8 tolerance-repair audit: relaxed tolerance plus a second non-heavy 1e-6 sweep leave combined best at 19/24 rows and 4/8 groups, source-policy still open. |
| `HI2022_T8_TOLERANCE_REPAIR_AUDIT.json` | Machine-readable HI2022 T=8 tolerance-repair audit consumed by the review agent and validators. |
| `B4_SOURCE_POLICY_POST_EXECUTION_AUDIT.md` | Post-execution audit for existing ready-command artifacts: all 13 ready-command outputs are present, but verified current authorized execution is false and 0/40 source-policy rows are promoted. |
| `B4_SOURCE_POLICY_POST_EXECUTION_AUDIT.json` | Machine-readable post-execution audit with RA2021/HI2022 output presence, promotion decision, and 20/20 ready/unaddressed row split. |
| `RA2021_DOUBLE_SOURCE_POLICY_LOW_ORDER_DIAGNOSIS.md` | RA2021 double-pendulum local source-policy candidate diagnosis; rows are complete but low-order/floor-limited and not promotable. |
| `RA2021_DOUBLE_SOURCE_POLICY_LOW_ORDER_DIAGNOSIS.json` | Machine-readable RA2021 double low-order diagnosis consumed by the B4 post-execution audit and validators. |
| `HI2022_RA_HALF_DOUBLE_SOURCE_POLICY_FAILURE_DIAGNOSIS.md` | HI2022 rA_half double-pendulum T=8 failure diagnosis; only 1/3 selected rows complete because two rows fail Newton convergence. |
| `HI2022_RA_HALF_DOUBLE_SOURCE_POLICY_FAILURE_DIAGNOSIS.json` | Machine-readable HI2022 rA_half double failure diagnosis consumed by the B4 post-execution audit and validators. |
| `B4_SOURCE_POLICY_ROW_CLOSURE_READINESS_LEDGER.md` | Row-level B4 ledger mapping all 40 external method/example cells after the guarded driver; no row is source-policy closed. |
| `B4_SOURCE_POLICY_ROW_CLOSURE_READINESS_LEDGER.json` | Machine-readable 40-row B4 source-policy readiness ledger with 20 command-mapped rows and 20 not-ready/demoted rows. |
| `B4_SOURCE_POLICY_ROW_CLOSURE_READINESS_LEDGER.csv` | CSV form of the 40-row B4 source-policy readiness ledger for reviewer-facing audit reuse. |
| `B4_SOURCE_POLICY_EXECUTION_HANDOFF_PACKAGE.md` | Read-only B4 handoff package carrying the exact approval guard and command-to-row traceability for 13 ready commands, 20 unique RA/HI rows, and 32 traced row references. |
| `B4_SOURCE_POLICY_EXECUTION_HANDOFF_PACKAGE.json` | Machine-readable B4 handoff package with OC4 command-row traceability and no execution authorization. |
| `B4_SOURCE_POLICY_COMMAND_PREFLIGHT_FREEZE_20260620.md` | Read-only B4 command preflight freeze with command hashes, 13 ready commands, 20 mapped RA/HI rows, 32 traced row references, and 21 expected artifacts; it executes no commands and closes zero source-policy rows. |
| `B4_SOURCE_POLICY_COMMAND_PREFLIGHT_FREEZE_20260620.json` | Machine-readable command preflight freeze consumed by source-policy handoff, archive-gap, and package validators. |
| `B4_SOURCE_POLICY_EXPECTED_OUTPUT_SCHEMA_AUDIT_20260620.md` | Read-only expected-output schema audit confirming 13/13 B4 command outputs and 21/21 expected artifacts are parseable and hash-matched while closing zero source-policy rows. |
| `B4_SOURCE_POLICY_EXPECTED_OUTPUT_SCHEMA_AUDIT_20260620.json` | Machine-readable expected-output schema audit consumed by handoff, archive-gap, and package validators without authorizing B4 execution. |
| `B4_EXPECTED_OUTPUT_PROMOTION_READINESS_BLOCKER_AUDIT_20260620.md` | Read-only promotion-readiness blocker audit proving the 13 schema-ready B4 expected outputs still produce zero promotion-ready commands and close zero source-policy rows. |
| `B4_EXPECTED_OUTPUT_PROMOTION_READINESS_BLOCKER_AUDIT_20260620.json` | Machine-readable promotion-readiness blocker audit consumed by archive-gap and package validators to keep schema-ready outputs separate from B4/B7 promotion evidence. |
| `FULL_SOURCE_POLICY_ROW_PROVENANCE_AUDIT.md` | Read-only OC4 row-provenance audit with `oc4_blocker_id=OC4`, `oc4_blocker_status=open`, `oc4_blocker_open=True`, `oc4_closure_allowed_now=False`, closure decision `remain_open_ready_for_authorized_execution_not_executed_not_promoted`, ready-command/mapped-row coverage `13/20`, and command traceability `20/32/32/0`; closes zero source-policy rows. |
| `FULL_SOURCE_POLICY_ROW_PROVENANCE_AUDIT.json` | Machine-readable OC4 provenance audit consumed by archive-gap and top-level validators; exposes top-level blocker/status, closure decision aliases, `ready_commands_mapped_rows=13/20`, `traceability_unique_traced_declared_mismatch=20/32/32/0`, and guarded-execution aliases without executing source-policy commands. |
| `FULL_SOURCE_POLICY_ROW_PROVENANCE_AUDIT.csv` | Flat 40-row provenance table linking source-policy rows to command refs, source roots, terminal unable-to-reproduce rows, and promotion-ready=false state. |
| `OC6_SOURCE_EQUIVALENT_REOPEN_READINESS_AUDIT_20260620.md` | Read-only OC6 source-equivalent reopen-readiness audit showing 20/20 TFE/VP rows remain unable to reproduce, with `source_equivalent_artifact_found=False`, closure decision `remain_open_no_positive_source_equivalent_artifact`, `source_policy_closed_ratio=0/20`, and aliases `oc6_blocker_id=OC6`, `oc6_blocker_status=partial`, `oc6_closure_allowed_now=False`. |
| `OC6_SOURCE_EQUIVALENT_REOPEN_READINESS_AUDIT_20260620.json` | Machine-readable OC6 reopen-readiness audit consumed by archive-gap and package validators without performing a new public-code search or source-policy execution; exposes top-level blocker/status, source-equivalent artifact, suite-specific reopen-condition alias `reopen_condition=suite_specific_source_equivalent_reopen_conditions`, latest probe boundary `latest_external_probe_boundary=0/0/4/False/False`, and runner-contract summary aliases. |
| `FULL_SOURCE_POLICY_RUNNER_ARCHIVE_GAP_AUDIT.md` | Full source-policy runner archive gap audit recording why the current archive remains narrowed/replay provenance, showing OC4/OC6/OC12 closure blockers, and keeping OC12 at `remain_partial_narrowed_replay_ready_full_source_policy_archive_not_ready` with dependency blockers `OC4,OC6`. |
| `FULL_SOURCE_POLICY_RUNNER_ARCHIVE_GAP_AUDIT.json` | Machine-readable full-source archive gap audit with action boundary, opt-in requirements, OC4 command-row traceability summary, and OC12 aliases `current_archive_usable_as_full_source_policy_runner_archive=False`, `safe_current_use=narrowed_claim_replay_and_audit_provenance_only`, and `primary_submission_package_allowed=False`. |
| `OBJECTIVE_COMPLETION_AUDIT.md` | Objective-level completion audit showing `objective_complete=false`, `submission_ready=false`, source-policy rows `0/40`, and the central blocker matrix `blocker_open_by_id=OC4:True,OC6:True,OC12:True`. |
| `OBJECTIVE_COMPLETION_AUDIT.json` | Machine-readable central completion audit preserving `blocker_closure_decision_by_id=OC4:remain_open_ready_for_authorized_execution_not_executed_not_promoted,OC6:remain_open_no_positive_source_equivalent_artifact,OC12:remain_partial_narrowed_replay_ready_full_source_policy_archive_not_ready` and `blocker_closure_allowed_by_id=OC4:False,OC6:False,OC12:False`. |
| `SOURCE_POLICY_REOPEN_CONDITION_MONITOR_20260620.md` | Read-only monitor for TFE/VP terminal reopen conditions, including current public-refresh counts and local external-mirror token scans; it closes zero source-policy rows. |
| `SOURCE_POLICY_REOPEN_CONDITION_MONITOR_20260620.json` | Machine-readable reopen-condition monitor recording 20 retained unable-to-reproduce rows, zero positive local/public reopen artifacts, and no source-policy promotion. |
| `VP2024_CODE_PATH_DISPOSITION_AUDIT.md` | Four-example VP2024 code-path disposition audit: `4/4` source-policy rows unresolved, `4/4` common-reference proxy order/error wins, and `1/4` larger-step diagnostic local error wins under a noncontrolling boundary. |
| `VP2024_CODE_PATH_DISPOSITION_AUDIT.json` | Machine-readable VP2024 disposition audit consumed by the review agent and validators. |
| `TFE_SOURCE_POLICY_SPEC.md` | Extracted original TFE pendulum source-policy setup and runner gap report. |
| `TFE_SOURCE_POLICY_SPEC.json` | Machine-readable TFE source-policy specification; source runner remains unimplemented. |
| `TFE_ENDPOINT_POLICY_BOUNDARY_CERTIFICATE.md` | Strict fixed-step endpoint boundary certificate proving exact/overrun row classification only; closes zero source-policy rows. |
| `TFE_ENDPOINT_POLICY_BOUNDARY_CERTIFICATE.json` | Machine-readable endpoint boundary certificate with exact/overrun counts and source-policy closure flags. |
| `TFE_ENDPOINT_POLICY_BOUNDARY_CERTIFICATE.csv` | Row-level endpoint boundary table for the TFE source step-size set. |
| `TFE_ENDPOINT_POLICY_SENSITIVITY_AUDIT.md` | Diagnostic four-policy endpoint sensitivity audit for the active original-TFE B2 candidate rows; closes zero source-policy rows. |
| `TFE_ENDPOINT_POLICY_SENSITIVITY_AUDIT.json` | Machine-readable endpoint-policy sensitivity audit with 16 summary rows, 48 raw rows, and external-superiority claims disallowed. |
| `TFE_ENDPOINT_POLICY_SENSITIVITY_AUDIT.csv` | Raw endpoint-policy sensitivity rows for the four candidate methods, four endpoint policies, and three nominal step sizes. |
| `TFE_FULL_T10_COARSE_CANDIDATE_SUMMARY.md` | Non-heavy full-horizon `T=10`, `h={0.1,0.05,0.025}` active-TFE candidate summary; finite/residual-ok `4/4`, source-policy rows `0`. |
| `TFE_FULL_T10_COARSE_CANDIDATE_SUMMARY.json` | Machine-readable full-T10 coarse candidate summary with method order/error rows and explicit non-source-policy claim boundary. |
| `TFE_FULL_T10_COARSE_CANDIDATE_SUMMARY.csv` | Flat row table for the four active original-TFE candidate methods in the full-T10 coarse diagnostic. |
| `COMPARISON_OBJECTIVE_CLOSURE_RECONCILIATION_AUDIT.md` | Reconciles the closed finite-grid common-reference order/error comparison with the still-open source-policy reproduction non-claim. |
| `COMPARISON_OBJECTIVE_CLOSURE_RECONCILIATION_AUDIT.json` | Machine-readable reconciliation showing 40/40 direct nonlocal order wins, 40/40 direct nonlocal error wins, and source-policy superiority still disallowed. |
| `CMAME_REVIEW_AGENT_REPORT.md` | Deterministic read-only CMAME submission-standard review report; currently blocks submission. |
| `CMAME_REVIEW_AGENT_REPORT.json` | Machine-readable review-agent report with 44-cell all-method matrix coverage checks and a submission-manifest narrowed archive boundary mirror proving manifest/reproducibility-manifest match `True`. |
| `CMAME_PROOF_STYLE_AUDIT.md` | Lie-group constrained-BDF proof-style audit confirming the Newton-Euler obligation table is present while global proof-package gates remain open. |
| `CMAME_PROOF_STYLE_AUDIT.json` | Machine-readable proof-style audit checked against `1-s2.0-S0377042719305229-main.pdf` text and current TeX. |
| `PAPER_CLAIM_LEDGER.md` | Claim-to-artifact ledger. |
| `REVIEWER_CHECKLIST.md` | Reviewer-facing read-only checklist. |
| `CURRENT_STATUS_CN.md` | Chinese current-status note. |
| `../CURRENT_PIPELINE_CONTRACT.md` | Current pipeline and command-boundary contract. |
| `../v047_cylindrical_chain_pipeline/results/summary_v047.json` | Authoritative v047 summary artifact. |

## Validators

| File | Role |
| --- | --- |
| `validate_cmame_submission.py` | Checks the CMAME/Elsevier `elsarticle` manuscript, highlights, declarations, clean log, manifest, and no-full-generator boundary. |
| `validate_submission_artifact_manifest_boundary_sync.py` | Checks that `SUBMISSION_ARTIFACT_MANIFEST.json` narrowed archive aliases and OC4 traceability match the reproducibility manifest and objective audit without source-policy execution. |
| `validate_cmame_submission_integrity_audit.py` | Checks citation-key/bibitem parity, sidecar presence, and the open external-reference-web-verification boundary. |
| `validate_full_source_policy_row_provenance_audit.py` | Checks the OC4 row-provenance audit aliases, including `oc4_blocker_id=OC4`, `oc4_blocker_status=open`, `remain_open_ready_for_authorized_execution_not_executed_not_promoted`, `oc4_blocker_open=True`, `oc4_closure_allowed_now=False`, ready commands `13/20`, traceability `20/32/32/0`, and source-policy closure `0/40`. |
| `validate_oc6_source_equivalent_reopen_readiness_audit_20260620.py` | Checks the OC6 source-equivalent reopen-readiness audit aliases, including `source_equivalent_artifact_found=False`, `remain_open_no_positive_source_equivalent_artifact`, `source_policy_closed_ratio=0/20`, `oc6_blocker_id=OC6`, `reopen_condition=suite_specific_source_equivalent_reopen_conditions`, and `latest_external_probe_boundary=0/0/4/False/False`. |
| `validate_cmame_blocker_closure_gate.py` | Checks the CMAME blocker ledger, same-test status, and no-default-`1e-4` policy. |
| `validate_cmame_external_baseline_gate.py` | Checks the external same-test comparison boundary, coarse-first evidence count, local closed-loop true-dynamic order evidence, public work/precision availability, strict common-reference availability, and no external superiority claim. |
| `validate_cmame_proof_contract_gate.py` | Checks the conditional proof contract, solver-tolerance condition, symbolic-oracle gap, and residual-to-error non-acceptance. |
| `validate_proof_numerical_scale_audit.py` | Checks the finite-run h-sweep scale audit and enforces that it is not an asymptotic solver proof. |
| `validate_proof_solver_scale_audit.py` | Checks recorded solver residual magnitudes, the `eta_h/h^7` diagnostic, and the missing scaled-tolerance sweep boundary. |
| `validate_proof_solver_scaled_tolerance_probe.py` | Checks the finite scaled-tolerance probe rows, h^7 residual bound, manifest anchors, and theorem non-closure boundary. |
| `validate_proof_solver_scaled_tolerance_trajectory_probe.py` | Checks the finite trajectory scaled-tolerance probe rows, per-step h^7 residual bound, manifest anchors, and theorem non-closure boundary. |
| `validate_proof_solver_tolerance_regime_sweep.py` | Checks the finite fixed/`h^7`/`h^8` tolerance-regime sweep, manifest anchors, policy rows, checked steps, and theorem non-closure boundary. |
| `validate_proof_claim_traceability_audit.py` | Checks the proof-claim traceability audit, including labels, boundary tokens, open assumptions, and row split. |
| `validate_cmame_visual_legibility_audit.py` | Checks the final-PDF visual legibility audit, B5 closure, remaining blocker count, and no-default-`1e-4` policy. |
| `validate_cmame_figure_set_audit.py` | Checks the 12-figure main/flat/PDF figure-set audit, Figure 12 all-method matrix integration, and B7 non-closure. |
| `validate_cmame_related_work_audit.py` | Checks the expanded related-work clusters, added reference set, B8 closure, and no-default-`1e-4` policy. |
| `validate_cmame_prose_residue_audit.py` | Checks the B6 main-body prose-residue token counts, appendix confinement, and no-default-`1e-4` policy. |
| `validate_cmame_claim_hygiene_audit.py` | Checks the conditional order-comparison boundary and absence of over-strong source-policy/external-superiority language. |
| `validate_dynamic_row_oracle_gate.py` | Imports `run_v047.py`, evaluates the accepted residual/Jacobian probe, checks the 132-row partition, and cross-checks the weighted block-functional row families. |
| `validate_concise_paper.py` | Checks the concise manuscript claim boundary. |
| `validate_paper_claims.py` | Checks the full paper claim boundary. |
| `validate_proof_evidence_matrix.py` | Checks the proof-obligation matrix and accepted theorem evidence boundary. |
| `validate_order_acceptance_gate.py` | Checks the example-level order boundary, including the `coarse_first_no_default_1e-4` policy. |
| `validate_implementation_fidelity_certificate.py` | Checks the implementation-fidelity certificate against the accepted JAX residual and AD Jacobian symbols. |
| `validate_implementation_path_audit.py` | Checks the accepted path `residual_cylindrical_chain -> R_VALUE/R_JAC -> gauss_step -> integrate/run_case -> summary_v047.json` without running `run_v047.py`. |
| `validate_kinematic_row_defect_certificate.py` | Checks the 96-row partial defect certificate and enforces that full symbolic defect proof, full TFE replacement, and submission readiness remain false. |
| `validate_newton_euler_defect_obligation_gate.py` | Checks the 36-row Newton-Euler dynamic obligation ledger and enforces that dynamic symbolic defect closure remains false. |
| `validate_newton_euler_virtual_work_wrench_audit.py` | Checks the D3 virtual-work sign-skeleton audit, enforces multiplier-wrench consistency and virtual-work identity proof, and keeps the local D3 proof-gap marker scoped false. |
| `validate_newton_euler_dynamic_row_closure_contract.py` | Checks the 36-row Newton-Euler closure contract, full runtime-traceability count, direct-route row-defect closure rows, and open primitive/Taylor boundary. |
| `validate_d5_dynamic_direct_substitution_certificate.py` | Checks the D5 direct-substitution certificate, including 36 zero dynamic rows, 132 full-stage rows if promoted, and no forbidden circular shortcut. |
| `validate_d5_taylor_term_budget_audit.py` | Checks the 162-subterm D5 Taylor budget and enforces that no term-level bound, PC2 closure, or submission-ready proof is claimed. |
| `validate_d5_primitive_bound_reduction_audit.py` | Checks the D5 primitive-bound reduction map and enforces that only P_tube is closed while zero induced primitive-route Taylor bounds are certified. |
| `validate_d5_p_tube_constants_audit.py` | Checks the compact proof-tube constants audit and enforces that it does not close PC2 or certify Taylor term bounds. |
| `validate_d5_p_state_lift_gap_audit.py` | Checks the P_state anti-circularity gate and enforces that no state-lift proof or PC2 closure is claimed. |
| `validate_d5_p_state_map_definition_audit.py` | Checks the PS1 P_state map-definition audit and enforces that no inverse, lift-rate, Taylor-bound, or PC2 closure is claimed. |
| `validate_d5_p_state_anticircularity_audit.py` | Checks the PS4 P_state anti-circularity audit and enforces that the anti-circularity proof itself does not close PS2/PS3, P_state, Taylor bounds, or PC2. |
| `validate_d5_p_state_ps2_weighted_target_audit.py` | Checks the PS2 weighted target-specification audit and enforces that the inverse/inf-sup constant, PS3 lift conversion, P_state primitive, Taylor bounds, and PC2 remain open. |
| `validate_d5_p_state_ps2_aggregate_promotion_audit.py` | Checks the aggregate PS2 promotion audit and enforces that only the weighted inverse closes while PS3, P_state, Taylor bounds, and PC2 remain open. |
| `validate_d5_p_state_ps2_linearization_probe.py` | Checks the finite PS2 weighted linearization probe and enforces that full-rank finite diagnostics do not close the uniform inf-sup proof or PC2. |
| `validate_d5_p_state_ps3_conditional_conversion_audit.py` | Checks the PS3 conditional-conversion audit and enforces that actual PS3, P_state, Taylor bounds, and PC2 remain open until the residual and acceleration-rate hypotheses are supplied. |
| `validate_d5_p_state_ps3_actual_instantiation_gap_audit.py` | Checks the PS3 actual-instantiation gap audit and enforces that the non-circular h-weighted acceleration input, actual PS3, P_state, Taylor bounds, and PC2 remain open. |
| `validate_d5_p_state_ps3_h_acc_input_obstruction_audit.py` | Checks the h-acceleration input obstruction audit and enforces that residual-only rows and finite probes do not close actual PS3, P_state, Taylor bounds, or PC2. |
| `validate_d5_p_acc_map_definition_audit.py` | Checks the PA1 P_acc map-definition audit and enforces that no acceleration lift-rate, Taylor-bound, or PC2 closure is claimed. |
| `validate_d5_p_acc_row_binding_audit.py` | Checks the PA4 P_acc row-binding audit and enforces that no acceleration lift-rate, Taylor-bound, or PC2 closure is claimed. |
| `validate_d5_p_acc_independence_audit.py` | Checks the PA3 P_acc independence audit and enforces that no acceleration lift-rate, Taylor-bound, or PC2 closure is claimed. |
| `validate_d5_p_acc_lift_obstruction_audit.py` | Checks the PA2 P_acc lift-obstruction audit, including the `h^{-1}` inversion rate loss and the retained non-closure of PA2/PC2. |
| `validate_d5_p_acc_pa2_weighted_inverse_audit.py` | Checks the PA2 weighted-inverse diagnostic and enforces that finite `h delta A` control does not close the unweighted acceleration lift, PA2, or PC2. |
| `validate_d5_p_lambda_interface_audit.py` | Checks the PL1 P_lambda interface audit and enforces that no multiplier lift-rate, inf-sup, Taylor-bound, or PC2 closure is claimed. |
| `validate_d5_p_lambda_inf_sup_probe.py` | Checks the finite P_lambda multiplier-column rank probe and enforces that full-rank finite diagnostics do not close the uniform inf-sup proof or PC2. |
| `validate_d5_p_lambda_pl2_geometric_margin_audit.py` | Checks the PL2 geometric-margin route audit and enforces that finite margin probes do not close `P_lambda` or PC2 while the symbolic compact-tube inf-sup subproof is closed. |
| `validate_d5_p_lambda_d3_noncircularity_audit.py` | Checks the PL3 P_lambda non-circular D3-use audit and enforces that the D3 identity is not used to prove PL2, PL4, multiplier lift, Taylor bounds, or PC2; PL2 is closed by its geometric-margin interface and PL4 remains conditional, while the actual multiplier lift and PC2 remain open. |
| `validate_d5_p_lambda_pl4_rate_propagation_audit.py` | Checks the PL4 conditional Taylor/implicit-function propagation audit and enforces that actual multiplier lift, Taylor bounds, `P_lambda`, and PC2 remain open. |
| `validate_d5_p_geom_chart_reduction_audit.py` | Checks the P_geom chart reduction and enforces that it remains conditional on the open P_state and P_lambda lifts. |
| `validate_d5_p_gyro_bilinear_reduction_audit.py` | Checks the P_gyro bilinear reduction and enforces that it remains conditional on the open P_state angular-velocity lift. |
| `validate_d5_open_primitive_gap_audit.py` | Checks the five-open-primitive gap ledger and enforces that only the conditional P_geom/P_gyro reductions are closed, with no lift, Taylor-bound, or PC2 closure claimed. |
| `validate_d5_primitive_obligation_closure_plan.py` | Checks the D5 primitive-obligation closure plan and enforces that it records only conditional implication interfaces, not PC2 closure. |
| `validate_d5_conditional_taylor_certificate.py` | Checks the conditional D5 Taylor certificate and enforces that 162/162 conditional subterms do not become actual PC2 or proof-gap closure. |
| `../v048_cross_paper_same_test_benchmarks/validate_closed_loop_true_dynamic_local_row_plan.py` | Checks the plan-only four-link/slider-crank true-dynamic local row contract and no-default-`1e-4` boundary. |
| `../v048_cross_paper_same_test_benchmarks/validate_closed_loop_true_dynamic_interface_audit.py` | Checks setup-level public/v046 dynamics interface availability without trajectory execution. |
| `../v048_cross_paper_same_test_benchmarks/validate_closed_loop_true_dynamic_residual_scaffold.py` | Checks the square residual layout contract for the missing local closed-loop dynamic runner. |
| `../v048_cross_paper_same_test_benchmarks/validate_closed_loop_true_dynamic_stage_residual_audit.py` | Checks the executable closed-loop dynamic stage residual evaluator without accepting trajectory order. |
| `../v048_cross_paper_same_test_benchmarks/validate_closed_loop_true_dynamic_one_step_smoke.py` | Checks the one-step Gauss6 endpoint smoke and its no-order/no-default-`1e-4` boundary. |
| `../v048_cross_paper_same_test_benchmarks/validate_closed_loop_true_dynamic_newton_stage_smoke.py` | Checks the non-oracle Newton stage smoke and its no-order/no-default-`1e-4` boundary. |
| `../v048_cross_paper_same_test_benchmarks/validate_closed_loop_true_dynamic_newton_coarse_order.py` | Checks the non-oracle local true-dynamic coarse order sweep and its no-external-superiority/no-default-`1e-4` boundary. |
| `../v048_cross_paper_same_test_benchmarks/validate_closed_loop_true_dynamic_public_work_precision.py` | Checks the same-window public work/precision rows and their no-external-superiority/no-default-`1e-4` boundary. |
| `../v048_cross_paper_same_test_benchmarks/validate_closed_loop_true_dynamic_strict_common_reference.py` | Checks strict common-reference work/precision rows, figure availability, and the no-external-superiority/no-default-`1e-4` boundary. |
| `../v048_cross_paper_same_test_benchmarks/validate_closed_loop_residual_to_error_theorem_obligations.py` | Checks the seven blocking residual-to-error theorem obligations and no-default-`1e-4` policy. |
| `validate_source_paper_comparison.py` | Checks the source-paper comparison, `m=3` expected order `5`, and v047 order-6 boundary. |
| `validate_cross_paper_benchmark_spec.py` | Checks the extracted external same-test benchmark specification and public-code source anchors. |
| `validate_cross_paper_benchmark_cases.py` | Checks the external same-test case inventory, source anchors, non-completed status, and unresolved velocity-partitioning gate. |
| `validate_external_same_test_run_queue.py` | Checks the coarse-first parallel queue, non-default-`1e-4` shard count, source-pendulum encoding blocker, and unresolved velocity-partitioning code path. |
| `validate_external_same_test_acceptance_sheet.py` | Checks the B2/B4 acceptance columns, no-default-`1e-4` policy, and no external-superiority overclaim. |
| `validate_cmame_review_agent.py` | Checks the read-only CMAME review-agent report, including 11 method rows, 44 method-example cells, PDF inclusion, and open blocker status. |
| `validate_cmame_proof_style_audit.py` | Checks the proof-style audit against the reference PDF text, proof section labels, and open proof-gap boundary. |
| `validate_paper_numerical_result_matrix.py` | Checks the paper numerical result matrix against common-reference and forensic source rows. |
| `validate_result_to_manuscript_traceability_audit.py` | Checks that the 44-cell velocity table in main/flat CMAME TeX and PDF text matches `PAPER_NUMERICAL_RESULT_MATRIX.json`. |
| `validate_all_method_example_claim_disposition_audit.py` | Checks `40/40` nonlocal method/example rows, local order/error wins, `0/40` source-policy-closed rows, and `15/40` anomaly/source-policy recheck rows. |
| `validate_all_examples_result_sanity_audit.py` | Checks the all-example sanity audit, including all four examples, local `4/4` order/error rows, and no external-superiority overclaim. |
| `validate_common_reference_order_recomputation_audit.py` | Rechecks that all common-reference summary orders and finest errors were independently recomputed from raw rows with zero mismatches. |
| `validate_external_baseline_source_policy_diagnosis.py` | Checks the source-policy diagnosis, including 15 flagged rows, 10 position-aligned velocity mismatches, and no external-superiority claim. |
| `validate_source_policy_closure_triage.py` | Checks the source-policy closure triage action counts and no-run/no-claim boundary. |
| `validate_source_policy_row_closure_ledger.py` | Checks the row-level source-policy closure ledger, exact flagged row set, all-four-example counts, 0/15 closed rows, and no external-superiority claim. |
| `validate_source_policy_local_candidate_gap_audit.py` | Checks the local-candidate source-policy gap audit, including RA public-grid/coarse/residual rows, HI T=8 coarse rows, TFE runner gaps, and the 0/40 source-policy boundary. |
| `validate_all_examples_source_policy_audit.py` | Checks the all-example source-policy audit, including all four examples, 45 raw flagged rows, three coarse step sizes, and the open B2/B4 boundary. |
| `validate_external_suite_disposition_audit.py` | Checks all four external suite dispositions, B2/B4 non-closure, and the 20 non-default-`1e-4` parallel-ready shards. |
| `validate_external_source_policy_closure_manifest.py` | Checks the source-policy closure manifest, 32/48 performance rows, zero strict external error-claim rows, and open B2/B4 status. |
| `validate_external_case_evidence_reconciliation.py` | Checks the case/evidence reconciliation so `not_run` full-campaign markers are not confused with zero bounded evidence. |
| `validate_vp2024_code_path_disposition_audit.py` | Checks all four VP2024 examples, the unresolved public code path, common-reference proxy wins, and noncontrolling larger-step diagnostic boundary. |
| `validate_ra2021_source_identity_audit.py` | Checks the RA2021 source-code identity audit, output mapping, time-grid convention, and zero source-policy rows closed. |
| `validate_hi2022_t8_tolerance_repair_audit.py` | Checks the HI2022 T=8 tolerance-repair audit, the second non-heavy sweep, 19/24 combined-best rows, 4/8 groups, and no source-policy closure. |
| `validate_tfe_source_policy_spec.py` | Checks the extracted TFE source-policy spec and unimplemented-runner boundary. |
| `validate_tfe_endpoint_policy_sensitivity_audit.py` | Checks the TFE endpoint-policy sensitivity diagnostic and enforces zero source-policy rows and no external-superiority claim. |
| `validate_comparison_objective_closure_reconciliation_audit.py` | Checks the claim split between closed common-reference order/error comparison and open source-policy reproduction. |
| `validate_submission_bundle.py` | Checks the submission bundle manifest, required files, clean logs, PDFs, and no-full-generator boundary. |
| `validate_paper_package.py` | Checks package files, submission files, paper claims, and read-only v047 validators. |
| `../validate_pipeline_outputs.py` | Checks the broader repository artifact inventory and paper package. |

## Accepted Claim Snapshot

- Accepted method: `Gauss6/FullVA`
- Method-order claim: `6`
- Smooth observed position/velocity orders: `7.161/7.066`
- Comparator: local paper-style `m=3` Gauss-Lobatto TFE formula target
- Comparator expected order: `5`
- Local method-side coverage examples: `single_pendulum`, `double_pendulum`, `four_link`,
  `slider_crank`
- Accepted dynamic order rows: `single_pendulum`, `double_pendulum`
- Coverage-only examples for dynamic order: `four_link`, `slider_crank`
- Full-TFE replacement: `full_tfe_stage_replacement=false`

## Non-Claims

- Complete source-paper residual reproduction is not claimed.
- Accepted independent full-TFE stage replacement is not claimed.
- Sparse AD being faster than dense `jacfwd` is not claimed.
- The practical coarse sharp-friction regime being solved is not claimed.

## Read-Only Check

Run:

```bash
../.venv_sbel/bin/python validate_cmame_submission.py
../.venv_sbel/bin/python validate_submission_artifact_manifest_boundary_sync.py
../.venv_sbel/bin/python validate_cmame_submission_integrity_audit.py
../.venv_sbel/bin/python validate_full_source_policy_row_provenance_audit.py
../.venv_sbel/bin/python validate_oc6_source_equivalent_reopen_readiness_audit_20260620.py
../.venv_sbel/bin/python validate_cmame_blocker_closure_gate.py
../.venv_sbel/bin/python validate_cmame_external_baseline_gate.py
../.venv_sbel/bin/python validate_cmame_proof_contract_gate.py
../.venv_sbel/bin/python validate_cmame_figure_set_audit.py
../.venv_sbel/bin/python validate_cmame_prose_residue_audit.py
../.venv_sbel/bin/python validate_dynamic_row_oracle_gate.py
../.venv_sbel/bin/python validate_submission_bundle.py
../.venv_sbel/bin/python validate_proof_evidence_matrix.py
../.venv_sbel/bin/python validate_proof_numerical_scale_audit.py
../.venv_sbel/bin/python validate_proof_solver_scale_audit.py
../.venv_sbel/bin/python validate_proof_solver_scaled_tolerance_probe.py
../.venv_sbel/bin/python validate_proof_solver_scaled_tolerance_trajectory_probe.py
../.venv_sbel/bin/python validate_proof_solver_tolerance_regime_sweep.py
../.venv_sbel/bin/python validate_proof_claim_traceability_audit.py
../.venv_sbel/bin/python validate_d5_taylor_term_budget_audit.py
../.venv_sbel/bin/python validate_d5_primitive_bound_reduction_audit.py
../.venv_sbel/bin/python validate_d5_p_tube_constants_audit.py
../.venv_sbel/bin/python validate_d5_p_state_lift_gap_audit.py
../.venv_sbel/bin/python validate_d5_p_state_map_definition_audit.py
../.venv_sbel/bin/python validate_d5_p_state_anticircularity_audit.py
../.venv_sbel/bin/python validate_d5_p_state_ps2_weighted_target_audit.py
../.venv_sbel/bin/python validate_d5_p_state_ps2_aggregate_promotion_audit.py
../.venv_sbel/bin/python validate_d5_p_state_ps2_linearization_probe.py
../.venv_sbel/bin/python validate_d5_p_state_ps3_conditional_conversion_audit.py
../.venv_sbel/bin/python validate_d5_p_state_ps3_actual_instantiation_gap_audit.py
../.venv_sbel/bin/python validate_d5_p_state_ps3_h_acc_input_obstruction_audit.py
../.venv_sbel/bin/python validate_d5_p_acc_map_definition_audit.py
../.venv_sbel/bin/python validate_d5_p_acc_row_binding_audit.py
../.venv_sbel/bin/python validate_d5_p_acc_independence_audit.py
../.venv_sbel/bin/python validate_d5_p_acc_lift_obstruction_audit.py
../.venv_sbel/bin/python validate_d5_p_lambda_interface_audit.py
../.venv_sbel/bin/python validate_d5_p_lambda_inf_sup_probe.py
../.venv_sbel/bin/python validate_d5_p_lambda_d3_noncircularity_audit.py
../.venv_sbel/bin/python validate_d5_p_geom_chart_reduction_audit.py
../.venv_sbel/bin/python validate_d5_p_gyro_bilinear_reduction_audit.py
../.venv_sbel/bin/python validate_d5_open_primitive_gap_audit.py
../.venv_sbel/bin/python validate_d5_primitive_obligation_closure_plan.py
../.venv_sbel/bin/python validate_d5_conditional_taylor_certificate.py
../.venv_sbel/bin/python validate_order_acceptance_gate.py
../.venv_sbel/bin/python validate_implementation_fidelity_certificate.py
../.venv_sbel/bin/python validate_implementation_path_audit.py
../.venv_sbel/bin/python validate_kinematic_row_defect_certificate.py
../.venv_sbel/bin/python validate_source_paper_comparison.py
../.venv_sbel/bin/python validate_cross_paper_benchmark_spec.py
../.venv_sbel/bin/python validate_cross_paper_benchmark_cases.py
../.venv_sbel/bin/python validate_external_same_test_run_queue.py
../.venv_sbel/bin/python validate_paper_numerical_result_matrix.py
../.venv_sbel/bin/python validate_result_to_manuscript_traceability_audit.py
../.venv_sbel/bin/python validate_all_examples_result_sanity_audit.py
../.venv_sbel/bin/python validate_cmame_review_agent.py
../.venv_sbel/bin/python validate_cmame_proof_style_audit.py
../.venv_sbel/bin/python validate_newton_euler_virtual_work_wrench_audit.py
../.venv_sbel/bin/python validate_newton_euler_dynamic_row_closure_contract.py
../.venv_sbel/bin/python validate_paper_package.py
```

The check reads existing artifacts, checks the flat source package, and must
not invoke `run_v047.py`.
