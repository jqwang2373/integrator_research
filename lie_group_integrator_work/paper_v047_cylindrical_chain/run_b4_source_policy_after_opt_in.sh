#!/usr/bin/env bash
set -euo pipefail

APPROVAL_REQUIRED='I explicitly approve running the B4 source-policy execution commands listed in B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json.'

if [[ "${1:-}" != "${APPROVAL_REQUIRED}" ]]; then
  echo "Refusing to run B4 source-policy execution commands."
  echo "Pass the exact approval statement as the first argument:"
  echo "${APPROVAL_REQUIRED}"
  exit 2
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
V048_DIR="${SCRIPT_DIR}/../v048_cross_paper_same_test_benchmarks"
PY="${SCRIPT_DIR}/../.venv_sbel/bin/python"

cd "${V048_DIR}"

"${PY}" run_v048.py --reuse-existing-results --ra2021-public-timing --ra2021-timing-forms rA,rp,reps --ra2021-timing-models single_pendulum,double_pendulum,four_link,slider_crank --allow-source-policy-1e-4
"${PY}" run_v048.py --reuse-existing-results --gauss6-public-single --gauss6-public-step-sizes 1e-2,1e-3,1e-4 --allow-source-policy-1e-4
"${PY}" run_v048.py --reuse-existing-results --ra2021-double-order --allow-source-policy-1e-4
"${PY}" run_public_closed_loop_shard.py --model four_link --step-sizes 1e-2,1e-3,1e-4 --allow-source-policy-1e-4
"${PY}" run_public_closed_loop_shard.py --model slider_crank --step-sizes 1e-2,1e-3,1e-4 --allow-source-policy-1e-4

"${PY}" run_hi2022_full_t8_source_policy_candidate.py --form rA_half --model single_pendulum --execute
"${PY}" run_hi2022_full_t8_source_policy_candidate.py --form rA_half --model double_pendulum --execute
"${PY}" run_hi2022_full_t8_source_policy_candidate.py --form rA_half --model four_link --execute
"${PY}" run_hi2022_full_t8_source_policy_candidate.py --form rA_half --model slider_crank --execute
"${PY}" run_hi2022_full_t8_source_policy_candidate.py --form rA --model single_pendulum --execute
"${PY}" run_hi2022_full_t8_source_policy_candidate.py --form rA --model double_pendulum --execute
"${PY}" run_hi2022_full_t8_source_policy_candidate.py --form rA --model four_link --execute
"${PY}" run_hi2022_full_t8_source_policy_candidate.py --form rA --model slider_crank --execute

cd "${SCRIPT_DIR}"

"${PY}" build_ra2021_double_source_policy_low_order_diagnosis.py
"${PY}" build_hi2022_ra_half_double_source_policy_failure_diagnosis.py
"${PY}" build_b4_source_policy_work_precision_execution_plan.py
"${PY}" build_b4_existing_artifact_promotion_audit.py
"${PY}" build_b4_source_policy_post_execution_audit.py --record-approved-driver-execution "${APPROVAL_REQUIRED}"
"${PY}" build_b4_source_policy_row_closure_readiness_ledger.py
"${PY}" build_b4_source_policy_execution_opt_in_packet.py
"${PY}" build_cmame_figure_set_audit.py
"${PY}" build_cmame_pdf_style_review_audit.py
"${PY}" build_cmame_submission_integrity_audit.py
"${PY}" build_cmame_reproducibility_package_manifest.py
"${PY}" cmame_submission_review_agent.py

"${PY}" validate_b4_source_policy_work_precision_execution_plan.py
"${PY}" validate_b4_existing_artifact_promotion_audit.py
"${PY}" validate_ra2021_double_source_policy_low_order_diagnosis.py
"${PY}" validate_hi2022_ra_half_double_source_policy_failure_diagnosis.py
"${PY}" validate_b4_source_policy_post_execution_audit.py
"${PY}" validate_b4_source_policy_row_closure_readiness_ledger.py
"${PY}" validate_b4_source_policy_execution_opt_in_packet.py
"${PY}" validate_cmame_figure_set_audit.py
"${PY}" validate_cmame_pdf_style_review_audit.py
"${PY}" validate_cmame_submission_integrity_audit.py
"${PY}" validate_cmame_reproducibility_package_manifest.py
"${PY}" validate_cmame_review_agent.py
"${PY}" validate_submission_bundle.py
"${PY}" validate_paper_package.py
