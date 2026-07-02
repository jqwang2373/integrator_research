# CMAME Figure Set Audit

Status: **B7 CLOSED - NARROWED COMMON-REFERENCE DIAGNOSTIC FIGURE SCOPE**.

- Figures audited: `13/13`.
- All main/flat figure files available: `True`.
- All main/flat TeX includes present: `True`.
- All main/flat PDF captions present: `True`.
- Figure 12 all-method matrix integrated: `True`.
- Figure 13 work/precision compendium integrated: `True`.
- Source-policy rows closed/total: `0/40`.
- B7 closed: `True`.
- Source-policy work/precision claim excluded: `True`.
- External superiority claim allowed: `False`.
- Submission ready from this audit: `False`.

## Figure Inventory

| no. | role | main | flat | main px | flat px | PDF captions |
|---:|---|---|---|---:|---:|---|
| 1 | `accepted-path convergence and work/precision` | `True` | `True` | `2256x1804` | `2256x1804` | `True/True` |
| 2 | `mechanism schematic` | `True` | `True` | `2028x1759` | `2028x1759` | `True/True` |
| 3 | `closed-loop kinematic evidence` | `True` | `True` | `1980x756` | `1980x756` | `True/True` |
| 4 | `full-TFE non-claim diagnostic` | `True` | `True` | `2844x756` | `2844x756` | `True/True` |
| 5 | `velocity-compression diagnostic` | `True` | `True` | `2970x827` | `2970x827` | `True/True` |
| 6 | `sparse backend caveat` | `True` | `True` | `1944x720` | `1944x720` | `True/True` |
| 7 | `strict common-reference work/precision` | `True` | `True` | `1793x767` | `1793x767` | `True/True` |
| 8 | `limitation explanation` | `True` | `True` | `2287x1804` | `2301x1804` | `True/True` |
| 9 | `coarse-first baseline/work-precision` | `True` | `True` | `2539x1939` | `2539x1939` | `True/True` |
| 10 | `closed-loop coarse dynamics diagnostics` | `True` | `True` | `2374x1804` | `2374x1804` | `True/True` |
| 11 | `method-stage architecture` | `True` | `True` | `2509x1504` | `2509x1504` | `True/True` |
| 12 | `all-method all-example result matrix` | `True` | `True` | `2524x2044` | `2524x2044` | `True/True` |
| 13 | `work/precision compendium` | `True` | `True` | `3271x1939` | `3272x1939` | `True/True` |

## Boundary

- Figure 12 makes the all-method all-example common-reference matrix visible in the PDF.
- Figure 13 consolidates fair candidate/common-reference work/precision rows and the T=10 Algorithm-1-literal Newton-work diagnostic already available in the evidence bundle.
- The figure set supports internal order evidence and bounded common-reference diagnostics.
- B7 closes under the narrowed claim because source-policy baseline comparison figures and complete external-suite work/precision curves are excluded from the current publication claim.
- This audit did not invoke `run_v047.py`, a v048 runner, or any default `1e-4` campaign.

## Post-B4 Figure Scope Plan

Status: `post_b4_source_policy_reintroduction_plan_ready_current_b7_closed`.

- Retain after caption recheck: `9` figures.
- Claim-boundary refresh after B4: `[8, 12]`.
- Blocking source-policy rebuild figures: `[9, 13]`.
- Source-policy dependent figure count: `4`.
- B7 closure allowed by this plan now: `False`.
- Current B7 scope closed without source-policy rebuild: `True`.
- Ready-command mapped/unaddressed rows: `20/0`.
- Ready/not-ready lanes after opt-in: `['ra2021_source_policy_work_precision', 'hi2022_full_T8_work_precision']` / `['tfe_source_policy_work_precision', 'vp2024_source_code_path_work_precision']`.
- Ready commands alone close B4/B7: `False/False`.

| figure | post-B4 action | source-policy dependent | reason |
|---:|---|---:|---|
| 1 | `retain_after_caption_recheck` | `False` | accepted local convergence/work-precision evidence remains part of the local-method claim |
| 2 | `retain_after_caption_recheck` | `False` | mechanism schematic is independent of external source-policy rows |
| 3 | `retain_after_caption_recheck` | `False` | closed-loop kinematic FullVA evidence is independent of external source-policy rows |
| 4 | `retain_after_caption_recheck` | `False` | full-TFE non-claim diagnostic remains a limitation figure |
| 5 | `retain_after_caption_recheck` | `False` | velocity-compression diagnostic remains a method-boundary figure |
| 6 | `retain_after_caption_recheck` | `False` | sparse backend caveat remains independent of source-policy rows |
| 7 | `retain_after_caption_recheck` | `False` | strict common-reference work/precision rows remain diagnostic and must not be promoted to source-policy closure |
| 8 | `refresh_claim_boundary_overlay_or_caption` | `True` | claim-boundary figure should reflect the final B4/B7 source-policy row status after promotion |
| 9 | `rebuild_from_promoted_source_policy_rows` | `True` | current coarse-baseline panel is diagnostic; B7 needs accepted source-policy baseline comparison rows |
| 10 | `retain_after_caption_recheck` | `False` | closed-loop coarse dynamics evidence remains a local-method diagnostic figure |
| 11 | `retain_after_caption_recheck` | `False` | method-stage architecture is independent of external source-policy rows |
| 12 | `refresh_claim_boundary_overlay_or_caption` | `True` | all-method matrix should keep any post-B4 promoted/demoted row status synchronized |
| 13 | `rebuild_from_promoted_source_policy_rows` | `True` | current compendium is diagnostic; clean source-policy work/precision curves require promoted B4 rows |

## B7 Closure-Readiness Preflight

Status: `b7_narrowed_diagnostic_common_reference_figure_scope_closed`.

- Closed preconditions/open dependencies: `13/0`.
- Source-policy rows closed/total: `0/40`.
- Source-policy rows ready for B7: `False`.
- Source-policy rows required for current B7: `False`.
- Narrowed-claim policy evidence supported: `True`.
- B7 closure allowed now: `True`.
- Heavy numerical run invoked: `False`.
- `run_v047.py` invoked: `False`.

| closed precondition | status | evidence |
|---|---:|---|
| `figure_inventory_complete` | `True` | `CMAME_FIGURE_SET_AUDIT.json` |
| `main_flat_figure_files_available` | `True` | `figures/ and cmame_submission_flat/` |
| `main_flat_tex_integration_present` | `True` | `main_cmame.tex and flat submission source` |
| `main_flat_pdf_captions_present` | `True` | `main_cmame.txt and flat PDF text` |
| `legible_figure_dimensions_present` | `True` | `PNG dimensions` |
| `limitation_explanation_figure_integrated` | `True` | `Figure 8` |
| `coarse_baseline_work_precision_figure_integrated` | `True` | `Figure 9` |
| `all_method_result_matrix_integrated` | `True` | `Figure 12` |
| `work_precision_compendium_integrated` | `True` | `Figure 13` |
| `read_only_no_heavy_no_default_1e4_policy_recorded` | `True` | `claim_boundary` |
| `narrowed_claim_policy_evidence_supported` | `True` | `CMAME_NARROWED_CLAIM_CLOSURE_POLICY_AUDIT.json` |
| `source_policy_work_precision_claim_excluded_from_current_b7_scope` | `True` | `claim_boundary` |
| `external_superiority_claim_forbidden_in_current_figure_scope` | `True` | `claim_boundary` |

| future source-policy dependency | status | reason |
|---|---|---|
| `b4_source_policy_work_precision_rows_closed` | `excluded_from_current_scope` | source-policy rows remain 0/40; retained only for future source-policy reintroduction |
| `full_source_policy_baseline_comparison_figures` | `excluded_from_current_scope` | current figures are accepted as common-reference diagnostics under the narrowed claim, not source-policy baseline comparisons |
| `clean_source_policy_work_precision_figures` | `excluded_from_current_scope` | Figure 13 remains a diagnostic compendium; clean source-policy curves are outside the current publication claim |

Post-close actions:

- keep source-policy work/precision rows excluded from the current publication claim
- recheck figure captions against the narrowed accepted claim boundary
- refresh PDF-style review, blocker gate, review agent, and submission bundle after any figure-scope edit
