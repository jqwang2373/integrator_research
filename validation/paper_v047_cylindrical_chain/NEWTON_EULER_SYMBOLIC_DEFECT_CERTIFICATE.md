# Newton-Euler Symbolic Defect Certificate

> Superseded on 2026-09-17 by EXACT_STAGE_IDENTITY_GATE: this artifact pinned the retired 96-row/PS2/primitive-Taylor proof route; the compacted manuscript proves the stage residual at the lifted Gauss stage is identically zero. Kept as an archived provenance record; its validator is no longer in the package chain.

Status: **OPEN - primitive/symbolic lane not closed; direct D5 route separate**.

- Certificate complete: `False`.
- Symbolic-certificate proof gap closed: `False`.
- Dynamic symbolic oracle complete: `False`.
- Stage residual O(h^7) defect proved: `False`.
- Primitive/symbolic false scope: `not proved by this primitive/symbolic certificate; the accepted theorem consumes the separate direct D5 substitution certificate together with the 96-row non-dynamic certificate`.
- Direct PC2 route source: `D5_DYNAMIC_DIRECT_SUBSTITUTION_CERTIFICATE.json`.
- Primitive/symbolic-lane certified/open rows: `0/36`.
- Active direct-route D5 closure is carried by `D5_DYNAMIC_DIRECT_SUBSTITUTION_CERTIFICATE.md`, not by this primitive/symbolic certificate.
- Rows with symbolic expansion templates: `36`.
- Runtime-mapped rows: `36`.
- Runtime row layout mapping checked: `True`.
- Runtime expression structure checked rows: `36`.
- Runtime expression structure checked: `True`.
- Runtime template instantiation checked rows: `36`.
- Runtime template instantiation checked: `True`.
- Body-specific wrench expansion checked rows: `36`.
- Body-specific wrench expansion checked: `True`.
- Virtual-work wrench sign skeleton checked rows: `36`.
- Virtual-work wrench sign skeleton checked: `True`.
- Virtual-work template identity rows: `36`.
- Virtual-work template identity proved: `True`.
- Virtual-work template identities proved: `2/2`.
- Row-expanded virtual-work identity rows: `36`.
- Row-expanded virtual-work identity proved: `True`.
- Row-expanded virtual-work identities proved: `6/6`.
- Multiplier wrench consistency closed: `True`.
- Full row-expanded virtual-work identity proved: `True`.
- Template algebraic equivalence checked rows: `36`.
- Template algebraic equivalence checked: `True`.
- Template-level C2 subcheck closed: `True`.
- Balance identity closed rows: `36`.
- Translational balance identity closed rows: `18`.
- Rotational balance identity closed rows: `18`.
- Runtime dynamic-row formula-oracle link checked: `True`.
- Runtime dynamic-row formula-oracle rows: `36`.
- Runtime formula-row AD Jacobian probes: `3`.
- AD-expanded row oracle checked rows: `36`.
- AD-expanded row oracle checked: `True`.
- AD-expanded row oracle columns per row: `132`.
- AD-expanded symbolic oracle closure: `False`.
- Row-ordering/scaling/AD equivalence closed: `True`.
- Smooth force-lift source structure checked: `True`.
- Smooth force-lift consistency closed: `True`.
- Smooth force-lift global C7 bound proved: `True`.
- Runtime algebraic equivalence proved: `True`.
- C4 manuscript link closed: `True`.
- Newton-Euler row-obligation links: `180`.
- Open/closed Newton-Euler obligations: `1/5`.
- Closed Newton-Euler obligation ids: `['translational_balance_identity', 'rotational_balance_identity', 'multiplier_wrench_consistency', 'smooth_force_lift_consistency', 'symbolic_runtime_row_equivalence']`.
- Unsatisfied close requirements: `[]`.
- Submission ready: `False`.

## Certificate Requirements

| requirement | satisfied | description |
|---|---:|---|
| `C1_row_expansion` | `True` | write the expanded symbolic Newton-Euler residual for every target row |
| `C2_runtime_equivalence` | `True` | prove the expanded symbolic row equals the implemented runtime row ordering |
| `C3_defect_bound` | `False` | prove each expanded residual evaluated on the smooth FullVA lift is O(h^7) |
| `C4_manuscript_link` | `True` | connect the open certificate scaffold to Lemma stage-residual-defect without closing C3 |

## Manuscript Link Audit

- Checked: `True`.
- Requirement: `C4_manuscript_link`.
- Scope: links the open certificate scaffold to Lemma `stage-residual-defect`; the symbolic-certificate C3 O(h^7) lane remains open while direct-route PC2 is closed separately.
- Source files: `['main_cmame.tex', 'cmame_submission_flat/main_cmame_submission.tex']`.

## Runtime Expression Structure Audit

- Source file: `v047_cylindrical_chain_pipeline/run_v047.py`.
- Residual function found: `True`.
- Structure checked: `True`.
- Checked translational/rotational rows: `18/18`.
- Scope: source-expression structure only; independent symbolic equivalence and O(h^7) defect proof remain open.
- Row-level runtime-template instantiation checked: `True`.
- Runtime-template translational/rotational rows: `18/18`.
- Template-instantiation scope: confirms target-to-template mapping and required runtime terms; algebraic equivalence and O(h^7) proof remain open.
- Body-specific wrench expansion checked: `True`.
- Body-specific body0/body1 rows: `18/18`.
- Body-specific scope: expands proximal/distal force and torque signs for traceability; algebraic equivalence and O(h^7) proof remain open.
- Virtual-work wrench sign skeleton checked: `True`.
- Virtual-work wrench sign-skeleton rows: `36`.
- Virtual-work template identity proved: `True`.
- Virtual-work template identity rows: `36`.
- Virtual-work template identities proved: `2/2`.
- Row-expanded virtual-work identity proved: `True`.
- Row-expanded virtual-work identity rows: `36`.
- Row-expanded virtual-work identities proved: `6/6`.
- Virtual-work site coverage: `9/9`.
- Multiplier wrench consistency closed: `True`.
- Virtual-work scope: checks the D3 force/torque sign skeleton, template identity, and row-expanded lower-pair multiplier-wrench identity; remaining dynamic symbolic equivalence and O(h^7) proof remain open.
- Template algebraic equivalence checked: `True`.
- Template algebraic translational/rotational rows: `18/18`.
- Template algebraic scope: verifies runtime-template/body-specific expansion equality; D1/D2 balance identity is closed, while the symbolic-certificate O(h^7) lane remains open.
- D1/D2 balance identity audit checked: `True`.
- D1/D2 balance identity closed rows: `36`.
- Runtime dynamic-row formula-oracle link checked: `True`.
- Runtime dynamic-row formula-oracle rows: `36`.
- Runtime formula-row AD Jacobian probe count: `3`.
- Runtime formula-oracle scope: links all 36 dynamic rows to formula-row and AD-Jacobian evidence; the symbolic-certificate O(h^7) lane remains open.
- AD-expanded row oracle checked: `True`.
- AD-expanded row oracle rows: `36`.
- AD-expanded row oracle columns per row: `132`.
- AD-expanded row oracle max mismatch: `3.330669e-16`.
- AD-expanded row oracle scope: row-level runtime/formula AD binding is closed for all 36 Newton-Euler rows; symbolic identity and symbolic-certificate O(h^7) lane remain open.
- Smooth force-lift source structure checked: `True`.
- Smooth branch stribeck velocity: `0.5`.
- Smooth force-lift scope: source-level Brown-McPhee smooth formula, stage-local lift structure, and compact proof-tube C7 bounds are checked for D4; the symbolic-certificate O(h^7) lane remains open.

## Open Obligations

| obligation | rows | status | blocks |
|---|---:|---|---|
| `gauss_stage_dynamic_defect_rate` | `36` | `open` | `symbolic-certificate PC2 lane` |

## Closed Sub-Obligations

| obligation | rows | status | closure evidence |
|---|---:|---|---|
| `translational_balance_identity` | `18` | `closed` | NEWTON_EULER_BALANCE_IDENTITY_AUDIT.json D1 source-level linear-momentum balance identity |
| `rotational_balance_identity` | `18` | `closed` | NEWTON_EULER_BALANCE_IDENTITY_AUDIT.json D2 source-level angular-momentum balance identity |
| `multiplier_wrench_consistency` | `36` | `closed` | NEWTON_EULER_VIRTUAL_WORK_WRENCH_AUDIT.json row-expanded lower-pair multiplier identity |
| `smooth_force_lift_consistency` | `36` | `closed` | SMOOTH_FORCE_LIFT_CERTIFICATE.json compact smooth proof-tube C7 audit |
| `symbolic_runtime_row_equivalence` | `36` | `closed` | NEWTON_EULER_ROW_ORDERING_SCALING_AD_AUDIT.json row-ordering/scaling/AD binding oracle |

## Row Certificate Slots

| row | local | stage | body | component | block | runtime source | expansion | body-specific wrench | status |
|---:|---:|---:|---:|---|---|---|---|---|---|
| `24` | `0` | `0` | `0` | `x` | `translational_newton_balance` | `body0_translational_balance_source` | `Phi_tr[s=0,i=0,c=x] = m_i a_sic - f_ext_sic - m_i g_c - (G_si^T lambda_s)_c - f_fric_sic` | `Phi_tr[s=0,body=0,c=x] = (m_0 a_0,0 - m_0 g - f_ext,0 - (F_0 - F_1))_c` | `ad_row=72`; `ad_cols=132`; `virtual_work=True`; `template_vw=True`; `row_expanded_vw=True`; `template_eq=0`; `balance_identity_closed_runtime_equivalence_closed_O_h7_bound_open` |
| `25` | `1` | `0` | `0` | `y` | `translational_newton_balance` | `body0_translational_balance_source` | `Phi_tr[s=0,i=0,c=y] = m_i a_sic - f_ext_sic - m_i g_c - (G_si^T lambda_s)_c - f_fric_sic` | `Phi_tr[s=0,body=0,c=y] = (m_0 a_0,0 - m_0 g - f_ext,0 - (F_0 - F_1))_c` | `ad_row=73`; `ad_cols=132`; `virtual_work=True`; `template_vw=True`; `row_expanded_vw=True`; `template_eq=0`; `balance_identity_closed_runtime_equivalence_closed_O_h7_bound_open` |
| `26` | `2` | `0` | `0` | `z` | `translational_newton_balance` | `body0_translational_balance_source` | `Phi_tr[s=0,i=0,c=z] = m_i a_sic - f_ext_sic - m_i g_c - (G_si^T lambda_s)_c - f_fric_sic` | `Phi_tr[s=0,body=0,c=z] = (m_0 a_0,0 - m_0 g - f_ext,0 - (F_0 - F_1))_c` | `ad_row=74`; `ad_cols=132`; `virtual_work=True`; `template_vw=True`; `row_expanded_vw=True`; `template_eq=0`; `balance_identity_closed_runtime_equivalence_closed_O_h7_bound_open` |
| `27` | `3` | `0` | `0` | `x` | `rotational_euler_balance` | `body0_rotational_balance_source` | `Phi_rot[s=0,i=0,c=x] = (J_i alpha_si + omega_si x J_i omega_si)_c - tau_ext_sic - (H_si^T lambda_s)_c - tau_fric_sic` | `Phi_rot[s=0,body=0,c=x] = (J_0 alpha_0,0 + omega_0,0 x J_0 omega_0,0 - tau_ext,0 - (s_prev,0 x R_0^T F_0 + s_next,0 x R_0^T(-F_1) + eta_0,0 axis_prev,0x + eta_0,1 axis_prev,0y - eta_1,0 axis_next,0x - eta_1,1 axis_next,0y))_c` | `ad_row=75`; `ad_cols=132`; `virtual_work=True`; `template_vw=True`; `row_expanded_vw=True`; `template_eq=0`; `balance_identity_closed_runtime_equivalence_closed_O_h7_bound_open` |
| `28` | `4` | `0` | `0` | `y` | `rotational_euler_balance` | `body0_rotational_balance_source` | `Phi_rot[s=0,i=0,c=y] = (J_i alpha_si + omega_si x J_i omega_si)_c - tau_ext_sic - (H_si^T lambda_s)_c - tau_fric_sic` | `Phi_rot[s=0,body=0,c=y] = (J_0 alpha_0,0 + omega_0,0 x J_0 omega_0,0 - tau_ext,0 - (s_prev,0 x R_0^T F_0 + s_next,0 x R_0^T(-F_1) + eta_0,0 axis_prev,0x + eta_0,1 axis_prev,0y - eta_1,0 axis_next,0x - eta_1,1 axis_next,0y))_c` | `ad_row=76`; `ad_cols=132`; `virtual_work=True`; `template_vw=True`; `row_expanded_vw=True`; `template_eq=0`; `balance_identity_closed_runtime_equivalence_closed_O_h7_bound_open` |
| `29` | `5` | `0` | `0` | `z` | `rotational_euler_balance` | `body0_rotational_balance_source` | `Phi_rot[s=0,i=0,c=z] = (J_i alpha_si + omega_si x J_i omega_si)_c - tau_ext_sic - (H_si^T lambda_s)_c - tau_fric_sic` | `Phi_rot[s=0,body=0,c=z] = (J_0 alpha_0,0 + omega_0,0 x J_0 omega_0,0 - tau_ext,0 - (s_prev,0 x R_0^T F_0 + s_next,0 x R_0^T(-F_1) + eta_0,0 axis_prev,0x + eta_0,1 axis_prev,0y - eta_1,0 axis_next,0x - eta_1,1 axis_next,0y))_c` | `ad_row=77`; `ad_cols=132`; `virtual_work=True`; `template_vw=True`; `row_expanded_vw=True`; `template_eq=0`; `balance_identity_closed_runtime_equivalence_closed_O_h7_bound_open` |
| `30` | `6` | `0` | `1` | `x` | `translational_newton_balance` | `body1_translational_balance_source` | `Phi_tr[s=0,i=1,c=x] = m_i a_sic - f_ext_sic - m_i g_c - (G_si^T lambda_s)_c - f_fric_sic` | `Phi_tr[s=0,body=1,c=x] = (m_1 a_0,1 - m_1 g - f_ext,1 - (F_1))_c` | `ad_row=78`; `ad_cols=132`; `virtual_work=True`; `template_vw=True`; `row_expanded_vw=True`; `template_eq=0`; `balance_identity_closed_runtime_equivalence_closed_O_h7_bound_open` |
| `31` | `7` | `0` | `1` | `y` | `translational_newton_balance` | `body1_translational_balance_source` | `Phi_tr[s=0,i=1,c=y] = m_i a_sic - f_ext_sic - m_i g_c - (G_si^T lambda_s)_c - f_fric_sic` | `Phi_tr[s=0,body=1,c=y] = (m_1 a_0,1 - m_1 g - f_ext,1 - (F_1))_c` | `ad_row=79`; `ad_cols=132`; `virtual_work=True`; `template_vw=True`; `row_expanded_vw=True`; `template_eq=0`; `balance_identity_closed_runtime_equivalence_closed_O_h7_bound_open` |
| `32` | `8` | `0` | `1` | `z` | `translational_newton_balance` | `body1_translational_balance_source` | `Phi_tr[s=0,i=1,c=z] = m_i a_sic - f_ext_sic - m_i g_c - (G_si^T lambda_s)_c - f_fric_sic` | `Phi_tr[s=0,body=1,c=z] = (m_1 a_0,1 - m_1 g - f_ext,1 - (F_1))_c` | `ad_row=80`; `ad_cols=132`; `virtual_work=True`; `template_vw=True`; `row_expanded_vw=True`; `template_eq=0`; `balance_identity_closed_runtime_equivalence_closed_O_h7_bound_open` |
| `33` | `9` | `0` | `1` | `x` | `rotational_euler_balance` | `body1_rotational_balance_source` | `Phi_rot[s=0,i=1,c=x] = (J_i alpha_si + omega_si x J_i omega_si)_c - tau_ext_sic - (H_si^T lambda_s)_c - tau_fric_sic` | `Phi_rot[s=0,body=1,c=x] = (J_1 alpha_0,1 + omega_0,1 x J_1 omega_0,1 - tau_ext,1 - (s_prev,1 x R_1^T F_1 + eta_1,0 axis_prev,1x + eta_1,1 axis_prev,1y))_c` | `ad_row=81`; `ad_cols=132`; `virtual_work=True`; `template_vw=True`; `row_expanded_vw=True`; `template_eq=0`; `balance_identity_closed_runtime_equivalence_closed_O_h7_bound_open` |
| `34` | `10` | `0` | `1` | `y` | `rotational_euler_balance` | `body1_rotational_balance_source` | `Phi_rot[s=0,i=1,c=y] = (J_i alpha_si + omega_si x J_i omega_si)_c - tau_ext_sic - (H_si^T lambda_s)_c - tau_fric_sic` | `Phi_rot[s=0,body=1,c=y] = (J_1 alpha_0,1 + omega_0,1 x J_1 omega_0,1 - tau_ext,1 - (s_prev,1 x R_1^T F_1 + eta_1,0 axis_prev,1x + eta_1,1 axis_prev,1y))_c` | `ad_row=82`; `ad_cols=132`; `virtual_work=True`; `template_vw=True`; `row_expanded_vw=True`; `template_eq=0`; `balance_identity_closed_runtime_equivalence_closed_O_h7_bound_open` |
| `35` | `11` | `0` | `1` | `z` | `rotational_euler_balance` | `body1_rotational_balance_source` | `Phi_rot[s=0,i=1,c=z] = (J_i alpha_si + omega_si x J_i omega_si)_c - tau_ext_sic - (H_si^T lambda_s)_c - tau_fric_sic` | `Phi_rot[s=0,body=1,c=z] = (J_1 alpha_0,1 + omega_0,1 x J_1 omega_0,1 - tau_ext,1 - (s_prev,1 x R_1^T F_1 + eta_1,0 axis_prev,1x + eta_1,1 axis_prev,1y))_c` | `ad_row=83`; `ad_cols=132`; `virtual_work=True`; `template_vw=True`; `row_expanded_vw=True`; `template_eq=0`; `balance_identity_closed_runtime_equivalence_closed_O_h7_bound_open` |
| `68` | `0` | `1` | `0` | `x` | `translational_newton_balance` | `body0_translational_balance_source` | `Phi_tr[s=1,i=0,c=x] = m_i a_sic - f_ext_sic - m_i g_c - (G_si^T lambda_s)_c - f_fric_sic` | `Phi_tr[s=1,body=0,c=x] = (m_0 a_1,0 - m_0 g - f_ext,0 - (F_0 - F_1))_c` | `ad_row=84`; `ad_cols=132`; `virtual_work=True`; `template_vw=True`; `row_expanded_vw=True`; `template_eq=0`; `balance_identity_closed_runtime_equivalence_closed_O_h7_bound_open` |
| `69` | `1` | `1` | `0` | `y` | `translational_newton_balance` | `body0_translational_balance_source` | `Phi_tr[s=1,i=0,c=y] = m_i a_sic - f_ext_sic - m_i g_c - (G_si^T lambda_s)_c - f_fric_sic` | `Phi_tr[s=1,body=0,c=y] = (m_0 a_1,0 - m_0 g - f_ext,0 - (F_0 - F_1))_c` | `ad_row=85`; `ad_cols=132`; `virtual_work=True`; `template_vw=True`; `row_expanded_vw=True`; `template_eq=0`; `balance_identity_closed_runtime_equivalence_closed_O_h7_bound_open` |
| `70` | `2` | `1` | `0` | `z` | `translational_newton_balance` | `body0_translational_balance_source` | `Phi_tr[s=1,i=0,c=z] = m_i a_sic - f_ext_sic - m_i g_c - (G_si^T lambda_s)_c - f_fric_sic` | `Phi_tr[s=1,body=0,c=z] = (m_0 a_1,0 - m_0 g - f_ext,0 - (F_0 - F_1))_c` | `ad_row=86`; `ad_cols=132`; `virtual_work=True`; `template_vw=True`; `row_expanded_vw=True`; `template_eq=0`; `balance_identity_closed_runtime_equivalence_closed_O_h7_bound_open` |
| `71` | `3` | `1` | `0` | `x` | `rotational_euler_balance` | `body0_rotational_balance_source` | `Phi_rot[s=1,i=0,c=x] = (J_i alpha_si + omega_si x J_i omega_si)_c - tau_ext_sic - (H_si^T lambda_s)_c - tau_fric_sic` | `Phi_rot[s=1,body=0,c=x] = (J_0 alpha_1,0 + omega_1,0 x J_0 omega_1,0 - tau_ext,0 - (s_prev,0 x R_0^T F_0 + s_next,0 x R_0^T(-F_1) + eta_0,0 axis_prev,0x + eta_0,1 axis_prev,0y - eta_1,0 axis_next,0x - eta_1,1 axis_next,0y))_c` | `ad_row=87`; `ad_cols=132`; `virtual_work=True`; `template_vw=True`; `row_expanded_vw=True`; `template_eq=0`; `balance_identity_closed_runtime_equivalence_closed_O_h7_bound_open` |
| `72` | `4` | `1` | `0` | `y` | `rotational_euler_balance` | `body0_rotational_balance_source` | `Phi_rot[s=1,i=0,c=y] = (J_i alpha_si + omega_si x J_i omega_si)_c - tau_ext_sic - (H_si^T lambda_s)_c - tau_fric_sic` | `Phi_rot[s=1,body=0,c=y] = (J_0 alpha_1,0 + omega_1,0 x J_0 omega_1,0 - tau_ext,0 - (s_prev,0 x R_0^T F_0 + s_next,0 x R_0^T(-F_1) + eta_0,0 axis_prev,0x + eta_0,1 axis_prev,0y - eta_1,0 axis_next,0x - eta_1,1 axis_next,0y))_c` | `ad_row=88`; `ad_cols=132`; `virtual_work=True`; `template_vw=True`; `row_expanded_vw=True`; `template_eq=0`; `balance_identity_closed_runtime_equivalence_closed_O_h7_bound_open` |
| `73` | `5` | `1` | `0` | `z` | `rotational_euler_balance` | `body0_rotational_balance_source` | `Phi_rot[s=1,i=0,c=z] = (J_i alpha_si + omega_si x J_i omega_si)_c - tau_ext_sic - (H_si^T lambda_s)_c - tau_fric_sic` | `Phi_rot[s=1,body=0,c=z] = (J_0 alpha_1,0 + omega_1,0 x J_0 omega_1,0 - tau_ext,0 - (s_prev,0 x R_0^T F_0 + s_next,0 x R_0^T(-F_1) + eta_0,0 axis_prev,0x + eta_0,1 axis_prev,0y - eta_1,0 axis_next,0x - eta_1,1 axis_next,0y))_c` | `ad_row=89`; `ad_cols=132`; `virtual_work=True`; `template_vw=True`; `row_expanded_vw=True`; `template_eq=0`; `balance_identity_closed_runtime_equivalence_closed_O_h7_bound_open` |
| `74` | `6` | `1` | `1` | `x` | `translational_newton_balance` | `body1_translational_balance_source` | `Phi_tr[s=1,i=1,c=x] = m_i a_sic - f_ext_sic - m_i g_c - (G_si^T lambda_s)_c - f_fric_sic` | `Phi_tr[s=1,body=1,c=x] = (m_1 a_1,1 - m_1 g - f_ext,1 - (F_1))_c` | `ad_row=90`; `ad_cols=132`; `virtual_work=True`; `template_vw=True`; `row_expanded_vw=True`; `template_eq=0`; `balance_identity_closed_runtime_equivalence_closed_O_h7_bound_open` |
| `75` | `7` | `1` | `1` | `y` | `translational_newton_balance` | `body1_translational_balance_source` | `Phi_tr[s=1,i=1,c=y] = m_i a_sic - f_ext_sic - m_i g_c - (G_si^T lambda_s)_c - f_fric_sic` | `Phi_tr[s=1,body=1,c=y] = (m_1 a_1,1 - m_1 g - f_ext,1 - (F_1))_c` | `ad_row=91`; `ad_cols=132`; `virtual_work=True`; `template_vw=True`; `row_expanded_vw=True`; `template_eq=0`; `balance_identity_closed_runtime_equivalence_closed_O_h7_bound_open` |
| `76` | `8` | `1` | `1` | `z` | `translational_newton_balance` | `body1_translational_balance_source` | `Phi_tr[s=1,i=1,c=z] = m_i a_sic - f_ext_sic - m_i g_c - (G_si^T lambda_s)_c - f_fric_sic` | `Phi_tr[s=1,body=1,c=z] = (m_1 a_1,1 - m_1 g - f_ext,1 - (F_1))_c` | `ad_row=92`; `ad_cols=132`; `virtual_work=True`; `template_vw=True`; `row_expanded_vw=True`; `template_eq=0`; `balance_identity_closed_runtime_equivalence_closed_O_h7_bound_open` |
| `77` | `9` | `1` | `1` | `x` | `rotational_euler_balance` | `body1_rotational_balance_source` | `Phi_rot[s=1,i=1,c=x] = (J_i alpha_si + omega_si x J_i omega_si)_c - tau_ext_sic - (H_si^T lambda_s)_c - tau_fric_sic` | `Phi_rot[s=1,body=1,c=x] = (J_1 alpha_1,1 + omega_1,1 x J_1 omega_1,1 - tau_ext,1 - (s_prev,1 x R_1^T F_1 + eta_1,0 axis_prev,1x + eta_1,1 axis_prev,1y))_c` | `ad_row=93`; `ad_cols=132`; `virtual_work=True`; `template_vw=True`; `row_expanded_vw=True`; `template_eq=0`; `balance_identity_closed_runtime_equivalence_closed_O_h7_bound_open` |
| `78` | `10` | `1` | `1` | `y` | `rotational_euler_balance` | `body1_rotational_balance_source` | `Phi_rot[s=1,i=1,c=y] = (J_i alpha_si + omega_si x J_i omega_si)_c - tau_ext_sic - (H_si^T lambda_s)_c - tau_fric_sic` | `Phi_rot[s=1,body=1,c=y] = (J_1 alpha_1,1 + omega_1,1 x J_1 omega_1,1 - tau_ext,1 - (s_prev,1 x R_1^T F_1 + eta_1,0 axis_prev,1x + eta_1,1 axis_prev,1y))_c` | `ad_row=94`; `ad_cols=132`; `virtual_work=True`; `template_vw=True`; `row_expanded_vw=True`; `template_eq=0`; `balance_identity_closed_runtime_equivalence_closed_O_h7_bound_open` |
| `79` | `11` | `1` | `1` | `z` | `rotational_euler_balance` | `body1_rotational_balance_source` | `Phi_rot[s=1,i=1,c=z] = (J_i alpha_si + omega_si x J_i omega_si)_c - tau_ext_sic - (H_si^T lambda_s)_c - tau_fric_sic` | `Phi_rot[s=1,body=1,c=z] = (J_1 alpha_1,1 + omega_1,1 x J_1 omega_1,1 - tau_ext,1 - (s_prev,1 x R_1^T F_1 + eta_1,0 axis_prev,1x + eta_1,1 axis_prev,1y))_c` | `ad_row=95`; `ad_cols=132`; `virtual_work=True`; `template_vw=True`; `row_expanded_vw=True`; `template_eq=0`; `balance_identity_closed_runtime_equivalence_closed_O_h7_bound_open` |
| `112` | `0` | `2` | `0` | `x` | `translational_newton_balance` | `body0_translational_balance_source` | `Phi_tr[s=2,i=0,c=x] = m_i a_sic - f_ext_sic - m_i g_c - (G_si^T lambda_s)_c - f_fric_sic` | `Phi_tr[s=2,body=0,c=x] = (m_0 a_2,0 - m_0 g - f_ext,0 - (F_0 - F_1))_c` | `ad_row=96`; `ad_cols=132`; `virtual_work=True`; `template_vw=True`; `row_expanded_vw=True`; `template_eq=0`; `balance_identity_closed_runtime_equivalence_closed_O_h7_bound_open` |
| `113` | `1` | `2` | `0` | `y` | `translational_newton_balance` | `body0_translational_balance_source` | `Phi_tr[s=2,i=0,c=y] = m_i a_sic - f_ext_sic - m_i g_c - (G_si^T lambda_s)_c - f_fric_sic` | `Phi_tr[s=2,body=0,c=y] = (m_0 a_2,0 - m_0 g - f_ext,0 - (F_0 - F_1))_c` | `ad_row=97`; `ad_cols=132`; `virtual_work=True`; `template_vw=True`; `row_expanded_vw=True`; `template_eq=0`; `balance_identity_closed_runtime_equivalence_closed_O_h7_bound_open` |
| `114` | `2` | `2` | `0` | `z` | `translational_newton_balance` | `body0_translational_balance_source` | `Phi_tr[s=2,i=0,c=z] = m_i a_sic - f_ext_sic - m_i g_c - (G_si^T lambda_s)_c - f_fric_sic` | `Phi_tr[s=2,body=0,c=z] = (m_0 a_2,0 - m_0 g - f_ext,0 - (F_0 - F_1))_c` | `ad_row=98`; `ad_cols=132`; `virtual_work=True`; `template_vw=True`; `row_expanded_vw=True`; `template_eq=0`; `balance_identity_closed_runtime_equivalence_closed_O_h7_bound_open` |
| `115` | `3` | `2` | `0` | `x` | `rotational_euler_balance` | `body0_rotational_balance_source` | `Phi_rot[s=2,i=0,c=x] = (J_i alpha_si + omega_si x J_i omega_si)_c - tau_ext_sic - (H_si^T lambda_s)_c - tau_fric_sic` | `Phi_rot[s=2,body=0,c=x] = (J_0 alpha_2,0 + omega_2,0 x J_0 omega_2,0 - tau_ext,0 - (s_prev,0 x R_0^T F_0 + s_next,0 x R_0^T(-F_1) + eta_0,0 axis_prev,0x + eta_0,1 axis_prev,0y - eta_1,0 axis_next,0x - eta_1,1 axis_next,0y))_c` | `ad_row=99`; `ad_cols=132`; `virtual_work=True`; `template_vw=True`; `row_expanded_vw=True`; `template_eq=0`; `balance_identity_closed_runtime_equivalence_closed_O_h7_bound_open` |
| `116` | `4` | `2` | `0` | `y` | `rotational_euler_balance` | `body0_rotational_balance_source` | `Phi_rot[s=2,i=0,c=y] = (J_i alpha_si + omega_si x J_i omega_si)_c - tau_ext_sic - (H_si^T lambda_s)_c - tau_fric_sic` | `Phi_rot[s=2,body=0,c=y] = (J_0 alpha_2,0 + omega_2,0 x J_0 omega_2,0 - tau_ext,0 - (s_prev,0 x R_0^T F_0 + s_next,0 x R_0^T(-F_1) + eta_0,0 axis_prev,0x + eta_0,1 axis_prev,0y - eta_1,0 axis_next,0x - eta_1,1 axis_next,0y))_c` | `ad_row=100`; `ad_cols=132`; `virtual_work=True`; `template_vw=True`; `row_expanded_vw=True`; `template_eq=0`; `balance_identity_closed_runtime_equivalence_closed_O_h7_bound_open` |
| `117` | `5` | `2` | `0` | `z` | `rotational_euler_balance` | `body0_rotational_balance_source` | `Phi_rot[s=2,i=0,c=z] = (J_i alpha_si + omega_si x J_i omega_si)_c - tau_ext_sic - (H_si^T lambda_s)_c - tau_fric_sic` | `Phi_rot[s=2,body=0,c=z] = (J_0 alpha_2,0 + omega_2,0 x J_0 omega_2,0 - tau_ext,0 - (s_prev,0 x R_0^T F_0 + s_next,0 x R_0^T(-F_1) + eta_0,0 axis_prev,0x + eta_0,1 axis_prev,0y - eta_1,0 axis_next,0x - eta_1,1 axis_next,0y))_c` | `ad_row=101`; `ad_cols=132`; `virtual_work=True`; `template_vw=True`; `row_expanded_vw=True`; `template_eq=0`; `balance_identity_closed_runtime_equivalence_closed_O_h7_bound_open` |
| `118` | `6` | `2` | `1` | `x` | `translational_newton_balance` | `body1_translational_balance_source` | `Phi_tr[s=2,i=1,c=x] = m_i a_sic - f_ext_sic - m_i g_c - (G_si^T lambda_s)_c - f_fric_sic` | `Phi_tr[s=2,body=1,c=x] = (m_1 a_2,1 - m_1 g - f_ext,1 - (F_1))_c` | `ad_row=102`; `ad_cols=132`; `virtual_work=True`; `template_vw=True`; `row_expanded_vw=True`; `template_eq=0`; `balance_identity_closed_runtime_equivalence_closed_O_h7_bound_open` |
| `119` | `7` | `2` | `1` | `y` | `translational_newton_balance` | `body1_translational_balance_source` | `Phi_tr[s=2,i=1,c=y] = m_i a_sic - f_ext_sic - m_i g_c - (G_si^T lambda_s)_c - f_fric_sic` | `Phi_tr[s=2,body=1,c=y] = (m_1 a_2,1 - m_1 g - f_ext,1 - (F_1))_c` | `ad_row=103`; `ad_cols=132`; `virtual_work=True`; `template_vw=True`; `row_expanded_vw=True`; `template_eq=0`; `balance_identity_closed_runtime_equivalence_closed_O_h7_bound_open` |
| `120` | `8` | `2` | `1` | `z` | `translational_newton_balance` | `body1_translational_balance_source` | `Phi_tr[s=2,i=1,c=z] = m_i a_sic - f_ext_sic - m_i g_c - (G_si^T lambda_s)_c - f_fric_sic` | `Phi_tr[s=2,body=1,c=z] = (m_1 a_2,1 - m_1 g - f_ext,1 - (F_1))_c` | `ad_row=104`; `ad_cols=132`; `virtual_work=True`; `template_vw=True`; `row_expanded_vw=True`; `template_eq=0`; `balance_identity_closed_runtime_equivalence_closed_O_h7_bound_open` |
| `121` | `9` | `2` | `1` | `x` | `rotational_euler_balance` | `body1_rotational_balance_source` | `Phi_rot[s=2,i=1,c=x] = (J_i alpha_si + omega_si x J_i omega_si)_c - tau_ext_sic - (H_si^T lambda_s)_c - tau_fric_sic` | `Phi_rot[s=2,body=1,c=x] = (J_1 alpha_2,1 + omega_2,1 x J_1 omega_2,1 - tau_ext,1 - (s_prev,1 x R_1^T F_1 + eta_1,0 axis_prev,1x + eta_1,1 axis_prev,1y))_c` | `ad_row=105`; `ad_cols=132`; `virtual_work=True`; `template_vw=True`; `row_expanded_vw=True`; `template_eq=0`; `balance_identity_closed_runtime_equivalence_closed_O_h7_bound_open` |
| `122` | `10` | `2` | `1` | `y` | `rotational_euler_balance` | `body1_rotational_balance_source` | `Phi_rot[s=2,i=1,c=y] = (J_i alpha_si + omega_si x J_i omega_si)_c - tau_ext_sic - (H_si^T lambda_s)_c - tau_fric_sic` | `Phi_rot[s=2,body=1,c=y] = (J_1 alpha_2,1 + omega_2,1 x J_1 omega_2,1 - tau_ext,1 - (s_prev,1 x R_1^T F_1 + eta_1,0 axis_prev,1x + eta_1,1 axis_prev,1y))_c` | `ad_row=106`; `ad_cols=132`; `virtual_work=True`; `template_vw=True`; `row_expanded_vw=True`; `template_eq=0`; `balance_identity_closed_runtime_equivalence_closed_O_h7_bound_open` |
| `123` | `11` | `2` | `1` | `z` | `rotational_euler_balance` | `body1_rotational_balance_source` | `Phi_rot[s=2,i=1,c=z] = (J_i alpha_si + omega_si x J_i omega_si)_c - tau_ext_sic - (H_si^T lambda_s)_c - tau_fric_sic` | `Phi_rot[s=2,body=1,c=z] = (J_1 alpha_2,1 + omega_2,1 x J_1 omega_2,1 - tau_ext,1 - (s_prev,1 x R_1^T F_1 + eta_1,0 axis_prev,1x + eta_1,1 axis_prev,1y))_c` | `ad_row=107`; `ad_cols=132`; `virtual_work=True`; `template_vw=True`; `row_expanded_vw=True`; `template_eq=0`; `balance_identity_closed_runtime_equivalence_closed_O_h7_bound_open` |

## Claim Policy

- Allowed now: row-level symbolic expansion templates, scaffold, and conditional proof accounting.
- Forbidden now: proof closure, dynamic symbolic oracle completion, O(h^7) dynamic defect proof, and submission readiness.

Validator: `validate_newton_euler_symbolic_defect_certificate.py`.
