#!/usr/bin/env python3
"""Read-only CMAME submission-standard review agent for the paper package.

The agent is deterministic: it reads the manuscript, result pack, blocker
ledger, and package manifests, then writes a reviewer-style report. It does
not edit the manuscript and it must not mark the package submission-ready
while any blocking gate remains open.
"""

from __future__ import annotations

import json
import hashlib
import re
from collections import Counter
from pathlib import Path


PAPER = Path(__file__).resolve().parent
OUT_JSON = PAPER / "CMAME_REVIEW_AGENT_REPORT.json"
OUT_MD = PAPER / "CMAME_REVIEW_AGENT_REPORT.md"
BLOCKER_IDS = ["OC4", "OC6", "OC12"]
DIRECT_PC2_SCOPE = "direct_residual_bridge_kantorovich_route_closed_primitive_taylor_conditional_schema_open"
DIRECT_PC2_READING_RULE = (
    "The schema-only compatibility boolean proof_gap_closed is a schema-compatible "
    "shorthand for direct_pc2_proof_gap_closed under the active direct PC2 residual-bridge/"
    "Kantorovich route. It does not close the primitive/Taylor route, P6 "
    "solver-policy evidence, P7 residual-to-error promotion, source-policy "
    "readiness, or full-TFE replacement."
)

REQUIRED_CMAME_STANDARD = {
    "journal_scope": "computational methods in applied mechanics and engineering",
    "article_type": "original computational-methods paper",
    "abstract_words_max": 250,
    "keywords_min": 1,
    "keywords_max": 7,
    "requires_high_quality_numerical_evidence": True,
    "requires_reproducibility_and_data_availability": True,
    "requires_declarations_and_ai_disclosure": True,
}

REVIEWER_FACING_PYTHON_LINE_LIMIT = 2000
REVIEWER_FACING_PYTHON_FILE_LIMIT = 12
RESEARCH_AUDIT_PRIMARY_SUBMISSION_LINE_LIMIT = 20000

ALL_METHOD_MATRIX_TEX_TOKENS = [
    r"\method{}",
    r"HI 2022 $rA$",
    r"HI 2022 $rA_{\mathrm{half}}$",
    r"2021 public $rA$",
    r"2021 public $r\epsilon$",
    r"2021 public $rp$",
    r"TFE Newmark--$\beta$",
    r"TFE $m=1$",
    r"TFE $m=2$",
    "TFE trapezoidal",
    r"VP 2024 coordinate partitioning $rA$",
]

ALL_METHOD_MATRIX_PDF_TOKENS = [
    "Gauss6/FullVA",
    "HI 2022 rA",
    "HI 2022 rAhalf",
    "2021 public rA",
    "2021 public rϵ",
    "2021 public rp",
    "TFE Newmark-β",
    "TFE m = 1",
    "TFE m = 2",
    "TFE trapezoidal",
    "VP 2024 coordinate partitioning rA",
]

ALL_METHOD_MATRIX_EXAMPLE_TOKENS = [
    "Single pendulum",
    "Double pendulum",
    "Four-link",
    "Slider-crank",
]

PROOF_CONDITIONAL_BOUNDARY_TOKENS = [
    "Conditional sixth-order theorem",
    "conditional local-defect-to-global-error theorem",
    "finite-run solver data, not as an asymptotic solver-error proof",
    "proof certificates supply the accepted direct-route residual/Jacobian binding used by the bridge",
    "derivative identities used by that binding",
    "primitive/Taylor route",
    "row-template instantiation",
    "template-level algebraic equivalence subcheck",
    "runtime row-slice evidence only, not a symbolic identity proof",
    "stage-residual condition",
    "not the route that discharges the PC2 stage-residual condition",
    "proof dependencies used by the theorem",
    "finite solver probes attach only to P6",
    "residual tables are recorded only as diagnostics for the open P7 residual-to-error boundary",
    "primitive symbolic route",
    "is a separate primitive-route record",
    "not an input to the PC2 stage-residual condition",
    "implication would have to prove a bound",
    "uniform stability or inf-sup constant on the reported branch",
    "small residual norms alone are not a trajectory-error theorem",
    "residual rows remain diagnostics even when their measured norms are small",
]

PUBLICATION_FIGURE_BOUNDARY_TOKENS = [
    "one-step architecture",
    "Bounded common-reference diagnostic work/precision rows",
    "Claim-boundary and limitation map",
    "Coarse-first baseline and work/precision diagnostics",
    "Closed-loop coarse-window trajectory diagnostics",
    "All-method common-reference result matrix",
]

SOURCE_POLICY_PROGRESS_TOKENS = [
    "2021 public baseline order/timing evidence",
    "12/12 public order groups",
    "12/12 timing rows",
    "source-policy dynamic-order count is nevertheless",
    "0/4",
    "source identity is now closed",
    "RA2021 local-candidate promotion boundary",
    "double-pendulum row is a coarse self-reference run",
    "four-link/slider-crank true-dynamic rows are bounded",
    "local-candidate availability from source-policy closure",
    "coarse replay has 18/24 successful rows",
    "source-equivalent DAE/friction/output runner has not completed",
    "no source-policy-closed external same-test error row is established",
]


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def blocker_token(values: dict[str, object]) -> str:
    return ",".join(f"{blocker_id}:{values[blocker_id]}" for blocker_id in BLOCKER_IDS)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def artifact_path(path: Path) -> str:
    try:
        rel = path.relative_to(PAPER)
    except ValueError:
        rel = path
    return rel.as_posix()


def artifact_snapshot(path: Path) -> dict[str, object]:
    data = path.read_bytes()
    return {
        "path": artifact_path(path),
        "sha256": hashlib.sha256(data).hexdigest(),
        "bytes": len(data),
    }


def artifact_anchor(
    path: str,
    *,
    quoted_token: str,
    interpretation: str,
    json_pointer: str | None = None,
    tex_label: str | None = None,
    pdf_text_token: str | None = None,
) -> dict[str, str]:
    anchor = {
        "path": path,
        "quoted_token": quoted_token,
        "interpretation": interpretation,
    }
    if json_pointer is not None:
        anchor["json_pointer"] = json_pointer
    if tex_label is not None:
        anchor["tex_label"] = tex_label
    if pdf_text_token is not None:
        anchor["pdf_text_token"] = pdf_text_token
    return anchor


def format_anchor(anchor: dict[str, str]) -> str:
    for key in ["json_pointer", "tex_label", "pdf_text_token"]:
        if key in anchor:
            location = f"{key} `{anchor[key]}`"
            break
    else:
        location = "location `unspecified`"
    return (
        f"`{anchor['path']}` {location}; token `{anchor['quoted_token']}`; "
        f"{anchor['interpretation']}"
    )


def contains_normalized(text: str, token: str) -> bool:
    def normalize(value: str) -> str:
        # pdftotext may line-break explicit compound terms at a retained hyphen.
        # Preserve this paper-level term before generic dehyphenation of ordinary
        # line-wrap hyphenation such as "con-\ndition".
        value = re.sub(r"\bresidual-to-\s+error\b", "residual-to-error", value)
        value = re.sub(r"([A-Za-z])-\s+([A-Za-z])", r"\1\2", value)
        value = value.replace("$", " ")
        return " ".join(value.split()).replace("–", "-").replace("—", "-").replace("−", "-")

    return token in text or normalize(token) in normalize(text)


def missing_tokens(text: str, tokens: list[str]) -> list[str]:
    return [token for token in tokens if not contains_normalized(text, token)]


def abstract_word_count(tex: str) -> int:
    match = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", tex, flags=re.S)
    if not match:
        return 10**9
    stripped = re.sub(r"\\[a-zA-Z]+(?:\{[^{}]*\})?", " ", match.group(1))
    stripped = re.sub(r"[$^_{}\\]", " ", stripped)
    return len(re.findall(r"[A-Za-z0-9]+(?:[-/][A-Za-z0-9]+)?", stripped))


def keyword_count(tex: str) -> int:
    match = re.search(r"\\begin\{keyword\}(.*?)\\end\{keyword\}", tex, flags=re.S)
    if not match:
        return 0
    return len([item for item in match.group(1).split(r"\sep") if item.strip()])


def blocker_findings(blocker: dict) -> list[dict[str, object]]:
    findings = []
    for item in blocker.get("blockers", []):
        if item.get("status") != "open":
            continue
        severity = "major"
        if item.get("id") in {"B1", "B2", "B3", "B4"}:
            severity = "blocking"
        findings.append(
            {
                "id": item.get("id"),
                "severity": severity,
                "area": item.get("area"),
                "required_to_close": item.get("required_to_close", []),
                "evidence": item.get("partial_progress_evidence", []),
            }
        )
    return findings


def objective_blocking_findings(objective_completion: dict) -> list[dict[str, object]]:
    findings = []
    for item in objective_completion.get("requirements", []):
        if item.get("blocking_for_goal_completion") is not True:
            continue
        if item.get("status") == "satisfied":
            continue
        findings.append(
            {
                "id": item.get("id"),
                "severity": "blocking",
                "area": "global_submission_standard",
                "status": item.get("status"),
                "requirement": item.get("requirement"),
                "next_to_close": item.get("next_to_close"),
                "evidence": item.get("evidence", []),
            }
        )
    return findings


def finding_required_text(item: dict[str, object]) -> str:
    required = item.get("required_to_close")
    if isinstance(required, list) and required:
        return "; ".join(str(value) for value in required)
    next_to_close = item.get("next_to_close")
    if isinstance(next_to_close, str) and next_to_close:
        return next_to_close
    requirement = item.get("requirement")
    if isinstance(requirement, str) and requirement:
        return requirement
    return "not recorded"


def all_method_matrix_complete(result_pack: dict) -> tuple[bool, int, int]:
    matrix = result_pack.get("common_reference", {}).get("all_method_matrix", [])
    if not isinstance(matrix, list):
        return False, 0, 0
    cell_count = 0
    for item in matrix:
        examples = item.get("examples") if isinstance(item, dict) else None
        if not isinstance(examples, dict):
            continue
        cell_count += sum(1 for value in examples.values() if isinstance(value, dict))
    return len(matrix) == 11 and cell_count == 44, len(matrix), cell_count


def python_inventory(root: Path) -> dict[str, object]:
    files = sorted(root.glob("*.py"))
    line_counts = {path.name: len(read_text(path).splitlines()) for path in files}
    prefix_counts = {
        "build": sum(1 for path in files if path.name.startswith("build_")),
        "validate": sum(1 for path in files if path.name.startswith("validate_")),
        "run": sum(1 for path in files if path.name.startswith("run_")),
        "merge": sum(1 for path in files if path.name.startswith("merge_")),
    }
    return {
        "file_count": len(files),
        "line_count": sum(line_counts.values()),
        "prefix_counts": prefix_counts,
        "largest_files": [
            {"file": name, "lines": count}
            for name, count in sorted(line_counts.items(), key=lambda item: item[1], reverse=True)[:5]
        ],
    }


def review_safe_b6_post_execution_status(boundary: dict) -> object:
    status = boundary.get("status")
    final_prose_enabled = boundary.get("final_prose_pass_enabled_by_post_execution")
    if (
        status == "existing_artifacts_present_no_verified_authorized_execution_zero_promoted_rows_source_policy_excluded_final_prose_enabled"
        and final_prose_enabled is False
    ):
        return "existing_artifacts_present_no_verified_authorized_execution_zero_promoted_rows_source_policy_excluded_full_source_policy_final_prose_not_enabled"
    if (
        status == "verified_authorized_execution_zero_promoted_rows_source_policy_excluded_final_prose_enabled"
        and final_prose_enabled is False
    ):
        return "verified_authorized_execution_zero_promoted_rows_source_policy_excluded_full_source_policy_final_prose_not_enabled"
    return status


def main() -> None:
    tex = read_text(PAPER / "main_cmame.tex")
    flat_tex = read_text(PAPER / "cmame_submission_flat" / "main_cmame_submission.tex")
    pdf_text = read_text(PAPER / "main_cmame.txt")
    flat_pdf_text = read_text(PAPER / "cmame_submission_flat" / "main_cmame_submission.txt")
    readiness_review_text = read_text(PAPER / "CMAME_SUBMISSION_READINESS_REVIEW.md")
    result_pack = read_json(PAPER / "PAPER_RESULT_PACK.json")
    numerical_matrix = read_json(PAPER / "PAPER_NUMERICAL_RESULT_MATRIX.json")
    result_traceability = read_json(PAPER / "RESULT_TO_MANUSCRIPT_TRACEABILITY_AUDIT.json")
    all_method_disposition = read_json(PAPER / "ALL_METHOD_EXAMPLE_CLAIM_DISPOSITION_AUDIT.json")
    all_examples_audit = read_json(PAPER / "ALL_EXAMPLES_RESULT_SANITY_AUDIT.json")
    recomputation_audit = read_json(PAPER / "COMMON_REFERENCE_ORDER_RECOMPUTATION_AUDIT.json")
    source_policy_diagnosis = read_json(PAPER / "EXTERNAL_BASELINE_SOURCE_POLICY_DIAGNOSIS.json")
    source_policy_triage = read_json(PAPER / "SOURCE_POLICY_CLOSURE_TRIAGE.json")
    source_policy_row_ledger = read_json(PAPER / "SOURCE_POLICY_ROW_CLOSURE_LEDGER.json")
    all_examples_source_policy = read_json(PAPER / "ALL_EXAMPLES_SOURCE_POLICY_AUDIT.json")
    suite_disposition = read_json(PAPER / "EXTERNAL_SUITE_DISPOSITION_AUDIT.json")
    source_policy_closure_manifest = read_json(PAPER / "EXTERNAL_SOURCE_POLICY_CLOSURE_MANIFEST.json")
    external_case_reconciliation = read_json(PAPER / "EXTERNAL_CASE_EVIDENCE_RECONCILIATION.json")
    four_example_dashboard = read_json(PAPER / "FOUR_EXAMPLE_SOURCE_POLICY_DASHBOARD.json")
    hi2022_policy_decision = read_json(PAPER / "HI2022_POLICY_DECISION_AUDIT.json")
    vp2024_disposition = read_json(PAPER / "VP2024_CODE_PATH_DISPOSITION_AUDIT.json")
    vp2024_public_code_recheck = read_json(PAPER / "VP2024_PUBLIC_CODE_RECHECK_20260613.json")
    source_policy_public_code_refresh = read_json(PAPER / "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260614.json")
    source_policy_public_code_refresh_latest = read_json(PAPER / "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260620.json")
    external_suite_demotion = read_json(PAPER / "EXTERNAL_SUITE_DEMOTION_LEDGER.json")
    b2_remaining_work = read_json(PAPER / "B2_SOURCE_POLICY_REMAINING_WORK_MANIFEST.json")
    b4_work_precision_plan = read_json(PAPER / "B4_SOURCE_POLICY_WORK_PRECISION_EXECUTION_PLAN.json")
    b4_existing_promotion_audit = read_json(PAPER / "B4_EXISTING_ARTIFACT_PROMOTION_AUDIT.json")
    b4_post_execution_audit = read_json(PAPER / "B4_SOURCE_POLICY_POST_EXECUTION_AUDIT.json")
    ra_hi_post_execution_attempt_certificate = read_json(
        PAPER / "RA_HI_SOURCE_POLICY_POST_EXECUTION_ATTEMPT_CERTIFICATE.json"
    )
    ra_hi_source_policy_output_inventory = read_json(PAPER / "RA_HI_SOURCE_POLICY_OUTPUT_INVENTORY.json")
    ra_hi_source_policy_closeout_checklist = read_json(PAPER / "RA_HI_SOURCE_POLICY_CLOSEOUT_CHECKLIST.json")
    ra_hi_source_policy_promotion_blocker_matrix = read_json(
        PAPER / "RA_HI_SOURCE_POLICY_PROMOTION_BLOCKER_MATRIX.json"
    )
    b4_row_readiness_ledger = read_json(PAPER / "B4_SOURCE_POLICY_ROW_CLOSURE_READINESS_LEDGER.json")
    b4_execution_opt_in_packet = read_json(PAPER / "B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json")
    b4_execution_handoff = read_json(PAPER / "B4_SOURCE_POLICY_EXECUTION_HANDOFF_PACKAGE.json")
    b4_command_traceability_summary = b4_execution_handoff.get(
        "command_row_traceability", {}
    ).get("summary", {})
    external_superiority_claim_demotion = read_json(
        PAPER / "EXTERNAL_SUPERIORITY_CLAIM_DEMOTION_AUDIT.json"
    )
    ra2021_source_policy_audit = read_json(PAPER / "RA2021_SOURCE_POLICY_ROW_AUDIT.json")
    ra2021_source_identity_audit = read_json(PAPER / "RA2021_SOURCE_IDENTITY_AUDIT.json")
    hi2022_source_policy_audit = read_json(PAPER / "HI2022_SOURCE_POLICY_ROW_AUDIT.json")
    hi2022_t8_tolerance_repair_audit = read_json(PAPER / "HI2022_T8_TOLERANCE_REPAIR_AUDIT.json")
    hi2022_ra_half_double_repair_attempt_certificate = read_json(
        PAPER / "HI2022_RA_HALF_DOUBLE_REPAIR_ATTEMPT_CERTIFICATE.json"
    )
    tfe_source_policy_spec = read_json(PAPER / "TFE_SOURCE_POLICY_SPEC.json")
    tfe_source_policy_audit = read_json(PAPER / "TFE_SOURCE_POLICY_ROW_AUDIT.json")
    tfe_dae_runner_contract_gap_audit = read_json(PAPER / "TFE_DAE_RUNNER_CONTRACT_GAP_AUDIT.json")
    tfe_runner_contract_preflight = read_json(
        PAPER / "TFE_RUNNER_CONTRACT_PREFLIGHT_CERTIFICATE.json"
    )
    tfe_self_reproduction_attempt_certificate = read_json(
        PAPER / "TFE_SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_CERTIFICATE.json"
    )
    tfe_public_code_recheck = read_json(PAPER / "TFE_PUBLIC_CODE_RECHECK_20260613.json")
    tfe_source_pendulum_model_audit = read_json(PAPER / "TFE_SOURCE_PENDULUM_MODEL_AUDIT.json")
    tfe_full_t10_coarse_candidate_summary = read_json(
        PAPER / "TFE_FULL_T10_COARSE_CANDIDATE_SUMMARY.json"
    )
    tfe_source_grid_compatibility = read_json(PAPER / "TFE_SOURCE_GRID_COMPATIBILITY_AUDIT.json")
    tfe_endpoint_sensitivity = read_json(PAPER / "TFE_ENDPOINT_POLICY_SENSITIVITY_AUDIT.json")
    comparison_reconciliation = read_json(PAPER / "COMPARISON_OBJECTIVE_CLOSURE_RECONCILIATION_AUDIT.json")
    blocker = read_json(PAPER / "CMAME_BLOCKER_CLOSURE_GATE.json")
    manifest = read_json(PAPER / "SUBMISSION_ARTIFACT_MANIFEST.json")
    reproducibility_manifest = read_json(PAPER / "CMAME_REPRODUCIBILITY_PACKAGE_MANIFEST.json")
    objective_completion = read_json(PAPER / "OBJECTIVE_COMPLETION_AUDIT.json")
    objective_summary = objective_completion.get("summary", {})
    objective_blocking_ids = list(objective_completion.get("blocking_ids", []))
    objective_blockers_by_id = {
        req_id: objective_completion.get("blockers_by_id", {}).get(req_id)
        for req_id in objective_blocking_ids
    }
    objective_blocker_status_by_id = {
        req_id: objective_completion.get("blocker_status_by_id", {}).get(req_id)
        for req_id in objective_blocking_ids
    }
    objective_blocker_next_actions_by_id = {
        req_id: objective_completion.get("blocker_next_actions_by_id", {}).get(req_id)
        for req_id in objective_blocking_ids
    }
    objective_blocker_required_to_close_by_id = {
        req_id: objective_completion.get("blocker_required_to_close_by_id", {}).get(req_id)
        for req_id in objective_blocking_ids
    }
    objective_blocker_safe_next_actions_by_id = {
        req_id: objective_completion.get("blocker_safe_next_actions_by_id", {}).get(req_id)
        for req_id in objective_blocking_ids
    }
    objective_blocker_opt_in_required_actions_by_id = {
        req_id: objective_completion.get("blocker_opt_in_required_actions_by_id", {}).get(req_id)
        for req_id in objective_blocking_ids
    }
    full_source_policy_runner_archive_gap = read_json(
        PAPER / "FULL_SOURCE_POLICY_RUNNER_ARCHIVE_GAP_AUDIT.json"
    )
    minimal_candidate_path = PAPER / "CMAME_MINIMAL_REPRODUCIBILITY_CANDIDATE_MANIFEST.json"
    minimal_candidate = read_json(minimal_candidate_path) if minimal_candidate_path.exists() else {}
    runner_centered_audit = read_json(PAPER / "CMAME_RUNNER_CENTERED_REPRODUCIBILITY_AUDIT.json")
    narrowed_repro_code_archive = read_json(PAPER / "CMAME_NARROWED_REPRO_CODE_ARCHIVE_MANIFEST.json")
    proof_gate = read_json(PAPER / "CMAME_PROOF_CONTRACT_GATE.json")
    proof_style = read_json(PAPER / "CMAME_PROOF_STYLE_AUDIT.json")
    strict_proof_audit = read_json(PAPER / "CMAME_STRICT_PROOF_AUDIT.json")
    proof_closure = read_json(PAPER / "PROOF_CLOSURE_MANIFEST.json")
    newton_euler_symbolic_target = read_json(PAPER / "NEWTON_EULER_SYMBOLIC_TARGET_AUDIT.json")
    newton_euler_symbolic_defect_certificate = read_json(
        PAPER / "NEWTON_EULER_SYMBOLIC_DEFECT_CERTIFICATE.json"
    )
    b1_symbolic_row_oracle_closure = read_json(
        PAPER / "B1_SYMBOLIC_ROW_ORACLE_CLOSURE_CERTIFICATE.json"
    )
    b1_ad_expanded_symbolic_oracle_closure = read_json(
        PAPER / "B1_AD_EXPANDED_SYMBOLIC_ORACLE_CLOSURE_CERTIFICATE.json"
    )
    newton_euler_ad_expanded_row_oracle = read_json(
        PAPER / "NEWTON_EULER_AD_EXPANDED_ROW_ORACLE_AUDIT.json"
    )
    proof_traceability = read_json(PAPER / "PROOF_CLAIM_TRACEABILITY_AUDIT.json")
    proof_remaining_work = read_json(PAPER / "PROOF_REMAINING_WORK_MANIFEST.json")
    solver_scale_audit = read_json(PAPER / "PROOF_SOLVER_SCALE_AUDIT.json")
    external_gate = read_json(PAPER / "CMAME_EXTERNAL_BASELINE_GATE.json")
    claim_hygiene = read_json(PAPER / "CMAME_CLAIM_HYGIENE_AUDIT.json")
    visual_legibility = read_json(PAPER / "CMAME_VISUAL_LEGIBILITY_AUDIT.json")
    figure_set = read_json(PAPER / "CMAME_FIGURE_SET_AUDIT.json")
    prose_residue = read_json(PAPER / "CMAME_PROSE_RESIDUE_AUDIT.json")
    submission_integrity = read_json(PAPER / "CMAME_SUBMISSION_INTEGRITY_AUDIT.json")
    reference_metadata = read_json(PAPER / "REFERENCE_METADATA_AUDIT.json")
    pdf_style_review = read_json(PAPER / "CMAME_PDF_STYLE_REVIEW_AUDIT.json")
    v048_dir = PAPER.parent / "v048_cross_paper_same_test_benchmarks"
    global_policy = read_json(v048_dir / "results" / "global_comparison_policy_audit.json")

    manifest_narrowed_archive_boundary = manifest.get("narrowed_archive_boundary", {})
    reproducibility_narrowed_archive_boundary = reproducibility_manifest.get(
        "narrowed_archive_boundary", {}
    )
    submission_manifest_boundary = {
        "manifest_path": "SUBMISSION_ARTIFACT_MANIFEST.json",
        "reproducibility_manifest_path": "CMAME_REPRODUCIBILITY_PACKAGE_MANIFEST.json",
        "narrowed_archive_boundary": manifest_narrowed_archive_boundary,
        "narrowed_archive_boundary_matches_reproducibility_manifest": (
            manifest_narrowed_archive_boundary == reproducibility_narrowed_archive_boundary
        ),
        "narrowed_archive_boundary_status": manifest.get("narrowed_archive_boundary_status"),
        "narrowed_archive_boundary_source_policy_closed_ratio": manifest.get(
            "narrowed_archive_boundary_source_policy_closed_ratio"
        ),
        "narrowed_archive_boundary_current_archive_usable_as_full_source_policy_runner_archive": (
            manifest.get(
                "narrowed_archive_boundary_current_archive_usable_as_full_source_policy_runner_archive"
            )
        ),
        "narrowed_archive_boundary_source_policy_execution_allowed_now": manifest.get(
            "narrowed_archive_boundary_source_policy_execution_allowed_now"
        ),
        "narrowed_archive_boundary_exact_b4_opt_in_required_for_execution": manifest.get(
            "narrowed_archive_boundary_exact_b4_opt_in_required_for_execution"
        ),
        "narrowed_archive_boundary_safe_action_ids": manifest.get(
            "narrowed_archive_boundary_safe_action_ids", []
        ),
        "narrowed_archive_boundary_opt_in_action_ids": manifest.get(
            "narrowed_archive_boundary_opt_in_action_ids", []
        ),
        "narrowed_archive_boundary_blocking_ids": manifest_narrowed_archive_boundary.get(
            "blocking_ids", []
        ),
        "narrowed_archive_boundary_blocker_status_by_id": manifest_narrowed_archive_boundary.get(
            "blocker_status_by_id", {}
        ),
        "narrowed_archive_boundary_blocker_next_actions_by_id": manifest_narrowed_archive_boundary.get(
            "blocker_next_actions_by_id", {}
        ),
        "narrowed_archive_boundary_blocker_required_to_close_by_id": manifest_narrowed_archive_boundary.get(
            "blocker_required_to_close_by_id", {}
        ),
        "narrowed_archive_boundary_blocker_safe_next_actions_by_id": manifest_narrowed_archive_boundary.get(
            "blocker_safe_next_actions_by_id", {}
        ),
        "narrowed_archive_boundary_blocker_opt_in_required_actions_by_id": manifest_narrowed_archive_boundary.get(
            "blocker_opt_in_required_actions_by_id", {}
        ),
        "narrowed_archive_boundary_scope": manifest_narrowed_archive_boundary.get("scope"),
    }

    open_findings = blocker_findings(blocker)
    abstract_words = abstract_word_count(tex)
    keywords = keyword_count(tex)
    paper_includes_result_pack = (
        contains_normalized(tex, "All 44 common-reference summary rows pass")
        and contains_normalized(tex, "global comparison policy passes 14/14")
        and contains_normalized(tex, "Bounded common-reference velocity evidence")
        and contains_normalized(tex, "zero paper-level external direct-error claims")
        and contains_normalized(flat_tex, "All 44 common-reference summary rows pass")
        and contains_normalized(flat_tex, "global comparison policy passes 14/14")
        and contains_normalized(flat_tex, "Bounded common-reference velocity evidence")
        and contains_normalized(flat_tex, "zero paper-level external direct-error claims")
    )
    tex_all_method_missing = missing_tokens(tex, ALL_METHOD_MATRIX_TEX_TOKENS)
    flat_tex_all_method_missing = missing_tokens(flat_tex, ALL_METHOD_MATRIX_TEX_TOKENS)
    tex_all_example_missing = missing_tokens(tex, ALL_METHOD_MATRIX_EXAMPLE_TOKENS)
    flat_tex_all_example_missing = missing_tokens(flat_tex, ALL_METHOD_MATRIX_EXAMPLE_TOKENS)
    pdf_all_method_missing = missing_tokens(pdf_text, ALL_METHOD_MATRIX_PDF_TOKENS)
    flat_pdf_all_method_missing = missing_tokens(flat_pdf_text, ALL_METHOD_MATRIX_PDF_TOKENS)
    pdf_all_example_missing = missing_tokens(pdf_text, ALL_METHOD_MATRIX_EXAMPLE_TOKENS)
    flat_pdf_all_example_missing = missing_tokens(flat_pdf_text, ALL_METHOD_MATRIX_EXAMPLE_TOKENS)
    tex_proof_conditional_missing = missing_tokens(tex, PROOF_CONDITIONAL_BOUNDARY_TOKENS)
    flat_tex_proof_conditional_missing = missing_tokens(flat_tex, PROOF_CONDITIONAL_BOUNDARY_TOKENS)
    pdf_proof_conditional_missing = missing_tokens(pdf_text, PROOF_CONDITIONAL_BOUNDARY_TOKENS)
    flat_pdf_proof_conditional_missing = missing_tokens(flat_pdf_text, PROOF_CONDITIONAL_BOUNDARY_TOKENS)
    tex_publication_figure_missing = missing_tokens(tex, PUBLICATION_FIGURE_BOUNDARY_TOKENS)
    flat_tex_publication_figure_missing = missing_tokens(flat_tex, PUBLICATION_FIGURE_BOUNDARY_TOKENS)
    pdf_publication_figure_missing = missing_tokens(pdf_text, PUBLICATION_FIGURE_BOUNDARY_TOKENS)
    flat_pdf_publication_figure_missing = missing_tokens(flat_pdf_text, PUBLICATION_FIGURE_BOUNDARY_TOKENS)
    tex_source_policy_progress_missing = missing_tokens(tex, SOURCE_POLICY_PROGRESS_TOKENS)
    flat_tex_source_policy_progress_missing = missing_tokens(flat_tex, SOURCE_POLICY_PROGRESS_TOKENS)
    pdf_source_policy_progress_missing = missing_tokens(pdf_text, SOURCE_POLICY_PROGRESS_TOKENS)
    flat_pdf_source_policy_progress_missing = missing_tokens(flat_pdf_text, SOURCE_POLICY_PROGRESS_TOKENS)

    manuscript_includes_all_method_matrix = (
        "All runnable common-reference velocity rows" in tex
        and "VP 2024 coordinate partitioning" in tex
        and "All runnable common-reference velocity rows" in flat_tex
        and "VP 2024 coordinate partitioning" in flat_tex
        and not tex_all_method_missing
        and not flat_tex_all_method_missing
        and not tex_all_example_missing
        and not flat_tex_all_example_missing
    )
    pdf_includes_result_pack = (
        contains_normalized(pdf_text, "All 44 common-reference summary rows pass")
        and contains_normalized(pdf_text, "global comparison policy passes 14/14")
        and "Bounded common-reference velocity evidence" in pdf_text
        and contains_normalized(pdf_text, "zero paper-level external")
        and contains_normalized(pdf_text, "error claims")
    )
    pdf_includes_all_method_matrix = (
        "All runnable common-reference velocity rows" in pdf_text
        and "VP 2024 coordinate partitioning" in pdf_text
        and "TFE Newmark" in pdf_text
        and "All runnable common-reference velocity rows" in flat_pdf_text
        and "VP 2024 coordinate partitioning" in flat_pdf_text
        and "TFE Newmark" in flat_pdf_text
        and not pdf_all_method_missing
        and not flat_pdf_all_method_missing
        and not pdf_all_example_missing
        and not flat_pdf_all_example_missing
    )
    manuscript_includes_source_policy_diagnosis = (
        "Source-policy diagnosis for flagged common-reference baseline rows" in tex
        and "Position aligned, velocity mismatched" in tex
        and "Source-policy diagnosis for flagged common-reference baseline rows" in flat_tex
        and "Position aligned, velocity mismatched" in flat_tex
    )
    manuscript_includes_all_example_source_policy_audit = (
        "All-example source-policy status for the flagged baseline rows" in tex
        and "all 15 flagged summary" in tex
        and "45 raw coarse rows" in tex
        and "Surrogate common-reference row only" in tex
        and "not the source pendulum" in tex
        and "source error norm, Brown--McPhee friction" in tex
        and "All-example source-policy status for the flagged baseline rows" in flat_tex
        and "all 15 flagged summary" in flat_tex
        and "45 raw coarse rows" in flat_tex
        and "Surrogate common-reference row only" in flat_tex
        and "not the source pendulum" in flat_tex
        and "source error norm, Brown--McPhee friction" in flat_tex
    )
    manuscript_includes_active_tfe_b2_smoke = (
        "Bounded active-row candidate smoke for the original" in tex
        and "h=\\{0.012,0.006,0.003\\}" in tex
        and "closes zero source-policy rows" in tex
        and "Bounded active-row candidate smoke for the original" in flat_tex
        and "h=\\{0.012,0.006,0.003\\}" in flat_tex
        and "closes zero source-policy rows" in flat_tex
    )
    manuscript_includes_tfe_full_t10_coarse_candidate = (
        "Full-horizon coarse candidate probe for the original" in tex
        and "h=\\{0.1,0.05,0.025\\}" in tex
        and "closes zero source-policy rows" in tex
        and "Full-horizon coarse candidate probe for the original" in flat_tex
        and "h=\\{0.1,0.05,0.025\\}" in flat_tex
        and "closes zero source-policy rows" in flat_tex
    )
    manuscript_includes_tfe_brown_mcphee_boundary = (
        contains_normalized(tex, "Brown--McPhee velocity-based continuous friction model")
        and contains_normalized(tex, "candidate published formula")
        and contains_normalized(tex, "source-code-equivalent friction implementation")
        and contains_normalized(tex, "source-policy boundaries")
        and contains_normalized(tex, "Brown--McPhee formula is not fixed")
        and contains_normalized(tex, "transition velocity \\(v_t\\)")
        and contains_normalized(tex, "velocity scale in the \\(v/v_t\\)")
        and contains_normalized(tex, "not the normal-load/multiplier coupling")
        and contains_normalized(tex, "implementation choice, not source-policy evidence")
        and contains_normalized(tex, "candidate-friction DAE trajectory contract records 12 method-grid rows")
        and contains_normalized(tex, "56 step-residual rows")
        and contains_normalized(tex, "nonpositive friction power")
        and contains_normalized(tex, "do not implement a monolithic source-policy DAE runner")
        and contains_normalized(tex, "source-policy runner acceptance contract has six simultaneous parts")
        and contains_normalized(tex, "source-code-equivalent Brown--McPhee transition law")
        and contains_normalized(tex, "monolithic absolute-coordinate DAE time integrator")
        and contains_normalized(tex, "row-promotion rules binding error, order, runtime, and work metrics")
        and contains_normalized(tex, "accepted source-policy reproduction row")
        and contains_normalized(flat_tex, "Brown--McPhee velocity-based continuous friction model")
        and contains_normalized(flat_tex, "candidate published formula")
        and contains_normalized(flat_tex, "source-code-equivalent friction implementation")
        and contains_normalized(flat_tex, "source-policy boundaries")
        and contains_normalized(flat_tex, "Brown--McPhee formula is not fixed")
        and contains_normalized(flat_tex, "transition velocity \\(v_t\\)")
        and contains_normalized(flat_tex, "velocity scale in the \\(v/v_t\\)")
        and contains_normalized(flat_tex, "not the normal-load/multiplier coupling")
        and contains_normalized(flat_tex, "implementation choice, not source-policy evidence")
        and contains_normalized(flat_tex, "candidate-friction DAE trajectory contract records 12 method-grid rows")
        and contains_normalized(flat_tex, "56 step-residual rows")
        and contains_normalized(flat_tex, "nonpositive friction power")
        and contains_normalized(flat_tex, "do not implement a monolithic source-policy DAE runner")
        and contains_normalized(flat_tex, "source-policy runner acceptance contract has six simultaneous parts")
        and contains_normalized(flat_tex, "source-code-equivalent Brown--McPhee transition law")
        and contains_normalized(flat_tex, "monolithic absolute-coordinate DAE time integrator")
        and contains_normalized(flat_tex, "row-promotion rules binding error, order, runtime, and work metrics")
        and contains_normalized(flat_tex, "accepted source-policy reproduction row")
    )
    manuscript_includes_tfe_appendix_b_certificate = (
        contains_normalized(tex, "Appendix-B coefficient formulas")
        and contains_normalized(tex, "three checked rows")
        and contains_normalized(tex, "zero maximum absolute difference")
        and contains_normalized(tex, "does not close source-policy method-runner equivalence")
        and contains_normalized(flat_tex, "Appendix-B coefficient formulas")
        and contains_normalized(flat_tex, "three checked rows")
        and contains_normalized(flat_tex, "zero maximum absolute difference")
        and contains_normalized(flat_tex, "does not close source-policy method-runner equivalence")
    )
    manuscript_includes_tfe_m3_formula_probe = (
        contains_normalized(tex, "full-$T=10$ coarse formula probe")
        and contains_normalized(tex, "Appendix-B $m=3$ Gauss--Lobatto target")
        and contains_normalized(tex, "formal fifth-order target")
        and contains_normalized(tex, "does not invoke the source $h=10^{-4}$ reference campaign")
        and contains_normalized(flat_tex, "full-$T=10$ coarse formula probe")
        and contains_normalized(flat_tex, "Appendix-B $m=3$ Gauss--Lobatto target")
        and contains_normalized(flat_tex, "formal fifth-order target")
        and contains_normalized(flat_tex, "does not invoke the source $h=10^{-4}$ reference campaign")
    )
    manuscript_includes_comparison_reconciliation = (
        contains_normalized(tex, "finite-grid common-reference diagnostic is arithmetically complete")
        and contains_normalized(tex, "nonlocal cells remain diagnostic comparison records")
        and contains_normalized(tex, "These rows remain")
        and contains_normalized(tex, "not promoted to a CMAME paper-level")
        and contains_normalized(flat_tex, "finite-grid common-reference diagnostic is arithmetically complete")
        and contains_normalized(flat_tex, "nonlocal cells remain diagnostic comparison records")
        and contains_normalized(flat_tex, "These rows remain")
        and contains_normalized(flat_tex, "not promoted to a CMAME paper-level")
    )
    manuscript_includes_minimal_reproducibility_boundary = (
        contains_normalized(tex, "reproducibility package is therefore two-tiered")
        and contains_normalized(tex, "10-file package with one 158-line Python replay core")
        and contains_normalized(tex, "not a complete runner-centered source-policy archive")
        and contains_normalized(tex, "local accepted-row companion is human-runnable")
        and contains_normalized(tex, "12 accepted local rows")
        and contains_normalized(tex, "external source-policy runner archive would require the 40 source-policy rows")
        and contains_normalized(tex, "full development repository")
        and contains_normalized(flat_tex, "reproducibility package is therefore two-tiered")
        and contains_normalized(flat_tex, "10-file package with one 158-line Python replay core")
        and contains_normalized(flat_tex, "not a complete runner-centered source-policy archive")
        and contains_normalized(flat_tex, "local accepted-row companion is human-runnable")
        and contains_normalized(flat_tex, "12 accepted local rows")
        and contains_normalized(flat_tex, "external source-policy runner archive would require the 40 source-policy rows")
        and contains_normalized(flat_tex, "full development repository")
    )
    pdf_includes_source_policy_diagnosis = (
        "Source-policy diagnosis for flagged common-reference baseline rows" in pdf_text
        and "Position aligned, velocity" in pdf_text
        and "mismatched" in pdf_text
    )
    pdf_includes_all_example_source_policy_audit = (
        contains_normalized(pdf_text, "All-example source-policy status for the flagged baseline rows")
        and contains_normalized(pdf_text, "45 raw coarse rows")
        and contains_normalized(pdf_text, "Surrogate common-reference row")
        and contains_normalized(pdf_text, "only: RA2021 public setup")
        and contains_normalized(pdf_text, "formula proxies, not the")
        and contains_normalized(pdf_text, "source pendulum.")
        and contains_normalized(pdf_text, "error norm,")
        and contains_normalized(pdf_text, "Brown-McPhee friction")
        and contains_normalized(pdf_text, "output variables, and")
        and contains_normalized(pdf_text, "horizon, or keep these")
        and contains_normalized(flat_pdf_text, "Surrogate common-reference row")
        and contains_normalized(flat_pdf_text, "only: RA2021 public setup")
        and contains_normalized(flat_pdf_text, "formula proxies, not the")
        and contains_normalized(flat_pdf_text, "source pendulum.")
        and contains_normalized(flat_pdf_text, "error norm,")
        and contains_normalized(flat_pdf_text, "Brown-McPhee friction")
        and contains_normalized(flat_pdf_text, "output variables, and")
        and contains_normalized(flat_pdf_text, "horizon, or keep these")
    )
    pdf_includes_active_tfe_b2_smoke = (
        contains_normalized(pdf_text, "Bounded active-row candidate smoke for the original")
        and contains_normalized(pdf_text, "0.012, 0.006, 0.003")
        and contains_normalized(pdf_text, "closes zero source-policy rows")
        and contains_normalized(flat_pdf_text, "Bounded active-row candidate smoke for the original")
        and contains_normalized(flat_pdf_text, "0.012, 0.006, 0.003")
        and contains_normalized(flat_pdf_text, "closes zero source-policy rows")
    )
    pdf_includes_tfe_full_t10_coarse_candidate = (
        contains_normalized(pdf_text, "Full-horizon coarse candidate probe for the original")
        and contains_normalized(pdf_text, "0.1, 0.05, 0.025")
        and contains_normalized(pdf_text, "closes zero source-policy rows")
        and contains_normalized(flat_pdf_text, "Full-horizon coarse candidate probe for the original")
        and contains_normalized(flat_pdf_text, "0.1, 0.05, 0.025")
        and contains_normalized(flat_pdf_text, "closes zero source-policy rows")
    )
    pdf_includes_tfe_brown_mcphee_boundary = (
        contains_normalized(pdf_text, "velocity-based continuous friction model")
        and contains_normalized(pdf_text, "candidate published")
        and contains_normalized(pdf_text, "source-code-equivalent friction implementation")
        and contains_normalized(pdf_text, "source-policy boundaries")
        and contains_normalized(pdf_text, "transition velocity vt")
        and contains_normalized(pdf_text, "velocity scale in the")
        and contains_normalized(pdf_text, "v/vt Stribeck factor")
        and contains_normalized(pdf_text, "not the normal-load/multiplier coupling")
        and contains_normalized(pdf_text, "implementation choice, not source-policy evidence")
        and contains_normalized(pdf_text, "candidate-friction DAE")
        and contains_normalized(pdf_text, "trajectory contract records 12 method-grid rows")
        and contains_normalized(pdf_text, "56 step-residual rows")
        and contains_normalized(pdf_text, "nonpositive friction power")
        and contains_normalized(pdf_text, "do not implement a monolithic source-policy DAE runner")
        and contains_normalized(pdf_text, "source-policy runner acceptance contract has six simultaneous parts")
        and contains_normalized(pdf_text, "transition law, including transition velocity")
        and contains_normalized(pdf_text, "monolithic absolute-coordinate DAE time integrator")
        and contains_normalized(pdf_text, "row-promotion rules binding error, order, runtime, and work metrics")
        and contains_normalized(pdf_text, "accepted source-policy reproduction")
        and contains_normalized(flat_pdf_text, "velocity-based continuous friction model")
        and contains_normalized(flat_pdf_text, "candidate published")
        and contains_normalized(flat_pdf_text, "source-code-equivalent friction implementation")
        and contains_normalized(flat_pdf_text, "source-policy boundaries")
        and contains_normalized(flat_pdf_text, "transition velocity vt")
        and contains_normalized(flat_pdf_text, "velocity scale in the")
        and contains_normalized(flat_pdf_text, "v/vt Stribeck factor")
        and contains_normalized(flat_pdf_text, "not the normal-load/multiplier coupling")
        and contains_normalized(flat_pdf_text, "implementation choice, not source-policy evidence")
        and contains_normalized(flat_pdf_text, "candidate-friction DAE")
        and contains_normalized(flat_pdf_text, "trajectory contract records 12 method-grid rows")
        and contains_normalized(flat_pdf_text, "56 step-residual rows")
        and contains_normalized(flat_pdf_text, "nonpositive friction power")
        and contains_normalized(flat_pdf_text, "do not implement a monolithic source-policy DAE runner")
        and contains_normalized(flat_pdf_text, "source-policy runner acceptance contract has six simultaneous parts")
        and contains_normalized(flat_pdf_text, "transition law, including transition velocity")
        and contains_normalized(flat_pdf_text, "monolithic absolute-coordinate DAE time integrator")
        and contains_normalized(flat_pdf_text, "row-promotion rules binding error, order, runtime, and work metrics")
        and contains_normalized(flat_pdf_text, "accepted source-policy reproduction")
    )
    pdf_includes_tfe_appendix_b_certificate = (
        contains_normalized(pdf_text, "Appendix-B coefficient formulas")
        and contains_normalized(pdf_text, "three checked rows")
        and contains_normalized(pdf_text, "zero maximum absolute difference")
        and contains_normalized(pdf_text, "does not close source-policy method-runner equivalence")
        and contains_normalized(flat_pdf_text, "Appendix-B coefficient formulas")
        and contains_normalized(flat_pdf_text, "three checked rows")
        and contains_normalized(flat_pdf_text, "zero maximum absolute difference")
        and contains_normalized(flat_pdf_text, "does not close source-policy method-runner equivalence")
    )
    pdf_includes_tfe_m3_formula_probe = (
        contains_normalized(pdf_text, "full-T = 10 coarse formula probe")
        and contains_normalized(pdf_text, "Appendix-B m = 3 Gauss-Lobatto target")
        and contains_normalized(pdf_text, "formal fifth-order target")
        and contains_normalized(pdf_text, "does not invoke the source h = 10")
        and contains_normalized(flat_pdf_text, "full-T = 10 coarse formula probe")
        and contains_normalized(flat_pdf_text, "Appendix-B m = 3 Gauss-Lobatto target")
        and contains_normalized(flat_pdf_text, "formal fifth-order target")
        and contains_normalized(flat_pdf_text, "does not invoke the source h = 10")
    )
    pdf_includes_minimal_reproducibility_boundary = (
        contains_normalized(pdf_text, "reproducibility package is therefore two-tiered")
        and contains_normalized(pdf_text, "10-file package with one 158-line Python replay core")
        and contains_normalized(pdf_text, "not a complete runner-centered source-policy archive")
        and contains_normalized(pdf_text, "local accepted-row companion is human-runnable")
        and contains_normalized(pdf_text, "12 accepted local rows")
        and contains_normalized(pdf_text, "external source-policy runner archive would require the 40 source-policy rows")
        and contains_normalized(pdf_text, "full development repository")
        and contains_normalized(flat_pdf_text, "reproducibility package is therefore two-tiered")
        and contains_normalized(flat_pdf_text, "10-file package with one 158-line Python replay core")
        and contains_normalized(flat_pdf_text, "not a complete runner-centered source-policy archive")
        and contains_normalized(flat_pdf_text, "local accepted-row companion is human-runnable")
        and contains_normalized(flat_pdf_text, "12 accepted local rows")
        and contains_normalized(flat_pdf_text, "external source-policy runner archive would require the 40 source-policy rows")
        and contains_normalized(flat_pdf_text, "full development repository")
    )
    pdf_includes_comparison_reconciliation = (
        contains_normalized(pdf_text, "finite-grid common-reference diagnostic is arithmetically complete")
        and contains_normalized(pdf_text, "nonlocal cells remain diagnostic comparison records")
        and contains_normalized(pdf_text, "These rows remain")
        and contains_normalized(pdf_text, "not promoted to a CMAME paper-level")
        and contains_normalized(flat_pdf_text, "finite-grid common-reference diagnostic is arithmetically complete")
        and contains_normalized(flat_pdf_text, "nonlocal cells remain diagnostic comparison records")
        and contains_normalized(flat_pdf_text, "These rows remain")
        and contains_normalized(flat_pdf_text, "not promoted to a CMAME paper-level")
    )
    all_matrix_complete, all_matrix_method_count, all_matrix_cell_count = all_method_matrix_complete(result_pack)

    format_checks = {
        "elsarticle_preprint": r"\documentclass[preprint,12pt]{elsarticle}" in tex,
        "cmame_journal_marker": "Computer Methods in Applied Mechanics and Engineering" in tex,
        "abstract_words": abstract_words,
        "abstract_within_limit": abstract_words <= REQUIRED_CMAME_STANDARD["abstract_words_max"],
        "keyword_count": keywords,
        "keywords_within_limit": REQUIRED_CMAME_STANDARD["keywords_min"] <= keywords <= REQUIRED_CMAME_STANDARD["keywords_max"],
        "highlights_present": (PAPER / "highlights_cmame.txt").exists(),
        "declarations_present": (PAPER / "declarations_cmame.md").exists(),
        "flat_submission_present": (PAPER / "cmame_submission_flat" / "main_cmame_submission.tex").exists(),
    }
    prose_post_execution_boundary = prose_residue.get("post_baseline_final_prose_dependency", {}).get(
        "post_execution_dependency_boundary", {}
    )
    result_checks = {
        "paper_result_pack_present": (PAPER / "PAPER_RESULT_PACK.json").exists(),
        "paper_result_pack_schema": result_pack.get("schema"),
        "paper_includes_latest_common_reference_result": paper_includes_result_pack,
        "pdf_text_includes_latest_common_reference_result": pdf_includes_result_pack,
        "manuscript_includes_all_method_matrix": manuscript_includes_all_method_matrix,
        "pdf_text_includes_all_method_matrix": pdf_includes_all_method_matrix,
        "all_method_matrix_tex_missing_methods": tex_all_method_missing,
        "all_method_matrix_flat_tex_missing_methods": flat_tex_all_method_missing,
        "all_method_matrix_pdf_missing_methods": pdf_all_method_missing,
        "all_method_matrix_flat_pdf_missing_methods": flat_pdf_all_method_missing,
        "all_method_matrix_tex_missing_examples": tex_all_example_missing,
        "all_method_matrix_flat_tex_missing_examples": flat_tex_all_example_missing,
        "all_method_matrix_pdf_missing_examples": pdf_all_example_missing,
        "all_method_matrix_flat_pdf_missing_examples": flat_pdf_all_example_missing,
        "all_method_matrix_all_methods_visible": not (
            tex_all_method_missing
            or flat_tex_all_method_missing
            or pdf_all_method_missing
            or flat_pdf_all_method_missing
        ),
        "all_method_matrix_all_examples_visible": not (
            tex_all_example_missing
            or flat_tex_all_example_missing
            or pdf_all_example_missing
            or flat_pdf_all_example_missing
        ),
        "proof_conditional_boundary_visible": not (
            tex_proof_conditional_missing
            or flat_tex_proof_conditional_missing
            or pdf_proof_conditional_missing
            or flat_pdf_proof_conditional_missing
        ),
        "proof_conditional_tex_missing": tex_proof_conditional_missing,
        "proof_conditional_flat_tex_missing": flat_tex_proof_conditional_missing,
        "proof_conditional_pdf_missing": pdf_proof_conditional_missing,
        "proof_conditional_flat_pdf_missing": flat_pdf_proof_conditional_missing,
        "publication_figure_boundary_visible": not (
            tex_publication_figure_missing
            or flat_tex_publication_figure_missing
            or pdf_publication_figure_missing
            or flat_pdf_publication_figure_missing
        ),
        "publication_figure_tex_missing": tex_publication_figure_missing,
        "publication_figure_flat_tex_missing": flat_tex_publication_figure_missing,
        "publication_figure_pdf_missing": pdf_publication_figure_missing,
        "publication_figure_flat_pdf_missing": flat_pdf_publication_figure_missing,
        "source_policy_progress_boundary_visible": not (
            tex_source_policy_progress_missing
            or flat_tex_source_policy_progress_missing
            or pdf_source_policy_progress_missing
            or flat_pdf_source_policy_progress_missing
        ),
        "source_policy_progress_tex_missing": tex_source_policy_progress_missing,
        "source_policy_progress_flat_tex_missing": flat_tex_source_policy_progress_missing,
        "source_policy_progress_pdf_missing": pdf_source_policy_progress_missing,
        "source_policy_progress_flat_pdf_missing": flat_pdf_source_policy_progress_missing,
        "four_example_dashboard_schema": four_example_dashboard.get("schema"),
        "four_example_dashboard_status": four_example_dashboard.get("status"),
        "four_example_dashboard_local_evidence_coverage_status": four_example_dashboard.get(
            "local_evidence_coverage_status"
        ),
        "four_example_dashboard_local_evidence_coverage_examples": four_example_dashboard.get(
            "local_evidence_coverage_examples"
        ),
        "four_example_dashboard_local_evidence_coverage_names": four_example_dashboard.get(
            "local_evidence_coverage_example_names"
        ),
        "four_example_dashboard_accepted_method_dynamic_order_examples": four_example_dashboard.get(
            "accepted_method_dynamic_order_examples"
        ),
        "four_example_dashboard_accepted_method_dynamic_order_example_count": four_example_dashboard.get(
            "accepted_method_dynamic_order_example_count"
        ),
        "four_example_dashboard_mechanism_coverage_examples": four_example_dashboard.get("mechanism_coverage_examples"),
        "four_example_dashboard_mechanism_coverage_example_count": four_example_dashboard.get(
            "mechanism_coverage_example_count"
        ),
        "four_example_dashboard_local_dynamic_order_status": four_example_dashboard.get("local_dynamic_order_status"),
        "four_example_dashboard_all_four_examples_checked": four_example_dashboard.get("all_four_examples_checked"),
        "four_example_dashboard_examples": four_example_dashboard.get("examples"),
        "four_example_dashboard_row_count": four_example_dashboard.get("row_count"),
        "four_example_dashboard_local_dynamic_order_closed_examples": four_example_dashboard.get(
            "local_dynamic_order_closed_examples"
        ),
        "four_example_dashboard_local_dynamic_order_closed_names": four_example_dashboard.get(
            "local_dynamic_order_closed_example_names"
        ),
        "four_example_dashboard_method_side_order_gate_examples": four_example_dashboard.get(
            "method_side_order_gate_examples"
        ),
        "four_example_dashboard_closed_loop_true_dynamic_order_closed_examples": four_example_dashboard.get(
            "closed_loop_true_dynamic_order_closed_examples"
        ),
        "four_example_dashboard_closed_loop_true_dynamic_order_closed_names": four_example_dashboard.get(
            "closed_loop_true_dynamic_order_closed_example_names"
        ),
        "four_example_dashboard_closed_loop_true_dynamic_step_sizes": four_example_dashboard.get(
            "closed_loop_true_dynamic_step_sizes"
        ),
        "four_example_dashboard_closed_loop_true_dynamic_reference_h": four_example_dashboard.get(
            "closed_loop_true_dynamic_reference_h"
        ),
        "four_example_dashboard_closed_loop_true_dynamic_stage_oracle_used": four_example_dashboard.get(
            "closed_loop_true_dynamic_stage_oracle_used"
        ),
        "four_example_dashboard_closed_loop_true_dynamic_rows": four_example_dashboard.get(
            "closed_loop_true_dynamic_rows"
        ),
        "four_example_dashboard_common_reference_cells": four_example_dashboard.get("common_reference_cells"),
        "four_example_dashboard_nonlocal_cells": four_example_dashboard.get("common_reference_nonlocal_cells"),
        "four_example_dashboard_order_wins": four_example_dashboard.get("common_reference_local_order_wins"),
        "four_example_dashboard_error_wins": four_example_dashboard.get("common_reference_local_error_wins"),
        "four_example_dashboard_source_policy_closed_rows": four_example_dashboard.get(
            "nonlocal_source_policy_closed_rows"
        ),
        "four_example_dashboard_accepted_source_policy_dynamic_order_examples": four_example_dashboard.get(
            "accepted_source_policy_dynamic_order_examples"
        ),
        "four_example_dashboard_external_superiority_allowed": four_example_dashboard.get(
            "source_policy_external_superiority_allowed"
        ),
        "four_example_dashboard_default_1e_4_required": four_example_dashboard.get("default_1e_4_required"),
        "four_example_dashboard_heavy_run_invoked": four_example_dashboard.get("heavy_numerical_run_invoked"),
        "visual_legibility_schema": visual_legibility.get("schema"),
        "visual_legibility_status": visual_legibility.get("status"),
        "visual_legibility_b5_closed": visual_legibility.get("closed_blocker", {}).get("status") == "closed",
        "visual_legibility_b7_open": visual_legibility.get("remaining_figure_blocker", {}).get("status") == "open",
        "visual_main_figure_width_px": visual_legibility.get("figure_checks", {}).get("main_figure_width_px"),
        "visual_main_figure_height_px": visual_legibility.get("figure_checks", {}).get("main_figure_height_px"),
        "visual_flat_figure_width_px": visual_legibility.get("figure_checks", {}).get("flat_figure_width_px"),
        "visual_flat_figure_height_px": visual_legibility.get("figure_checks", {}).get("flat_figure_height_px"),
        "visual_pdf_captions_present": (
            visual_legibility.get("figure_checks", {}).get("main_pdf_text_caption_present") is True
            and visual_legibility.get("figure_checks", {}).get("flat_pdf_text_caption_present") is True
        ),
        "visual_latex_logs_clean": visual_legibility.get("figure_checks", {}).get("latex_logs_clean"),
        "figure_set_schema": figure_set.get("schema"),
        "figure_set_status": figure_set.get("status"),
        "figure_set_count": figure_set.get("figure_count"),
        "figure_set_expected_count": figure_set.get("expected_figure_count"),
        "figure_set_all_available": figure_set.get("all_figures_available"),
        "figure_set_all_integrated": figure_set.get("all_figures_integrated_main_flat"),
        "figure_set_all_pdf_captions": figure_set.get("all_pdf_captions_present"),
        "figure_set_all_legible_dimensions": figure_set.get("all_legible_dimensions"),
        "figure_set_figure12_integrated": figure_set.get("figure12_all_method_matrix_integrated"),
        "figure_set_figure13_integrated": figure_set.get("figure13_work_precision_compendium_integrated"),
        "figure_set_b7_closed": figure_set.get("b7_closed"),
        "figure_set_source_policy_rows_closed": figure_set.get("source_policy_rows_closed"),
        "figure_set_source_policy_rows_total": figure_set.get("source_policy_rows_total"),
        "figure_set_b7_preflight_status": figure_set.get("b7_closure_readiness_preflight", {}).get("status"),
        "figure_set_b7_preflight_closed_preconditions": figure_set.get(
            "b7_closure_readiness_preflight", {}
        ).get("closed_precondition_count"),
        "figure_set_b7_preflight_open_dependencies": figure_set.get(
            "b7_closure_readiness_preflight", {}
        ).get("open_dependency_count"),
        "figure_set_b7_preflight_closure_allowed": figure_set.get(
            "b7_closure_readiness_preflight", {}
        ).get("b7_closure_allowed_now"),
        "figure_set_post_b4_plan_status": figure_set.get("post_b4_figure_scope_plan", {}).get("status"),
        "figure_set_post_b4_plan_retain_figures": figure_set.get(
            "post_b4_figure_scope_plan", {}
        ).get("retain_after_caption_recheck_figures"),
        "figure_set_post_b4_plan_claim_refresh_figures": figure_set.get(
            "post_b4_figure_scope_plan", {}
        ).get("claim_boundary_refresh_figures_after_b4"),
        "figure_set_post_b4_plan_rebuild_figures": figure_set.get(
            "post_b4_figure_scope_plan", {}
        ).get("blocking_source_policy_rebuild_figures"),
        "figure_set_post_b4_plan_source_policy_dependent_count": figure_set.get(
            "post_b4_figure_scope_plan", {}
        ).get("source_policy_dependent_figure_count"),
        "figure_set_post_b4_plan_closure_allowed": figure_set.get(
            "post_b4_figure_scope_plan", {}
        ).get("b7_closure_allowed_by_this_plan_now"),
        "figure_set_post_b4_ready_command_mapped_rows": figure_set.get(
            "post_b4_figure_scope_plan", {}
        ).get("ready_command_coverage_boundary", {}).get("ready_command_mapped_external_rows"),
        "figure_set_post_b4_unaddressed_rows": figure_set.get(
            "post_b4_figure_scope_plan", {}
        ).get("ready_command_coverage_boundary", {}).get("unaddressed_external_rows_after_ready_commands"),
        "figure_set_post_b4_not_ready_lanes": figure_set.get(
            "post_b4_figure_scope_plan", {}
        ).get("ready_command_coverage_boundary", {}).get("not_ready_lanes_after_ready_commands"),
        "figure_set_post_b4_ready_commands_close_b4_b7": [
            figure_set.get("post_b4_figure_scope_plan", {})
            .get("ready_command_coverage_boundary", {})
            .get("ready_commands_alone_can_close_b4"),
            figure_set.get("post_b4_figure_scope_plan", {})
            .get("ready_command_coverage_boundary", {})
            .get("ready_commands_alone_can_close_b7"),
        ],
        "figure_set_external_superiority_allowed": figure_set.get("claim_boundary", {}).get(
            "external_superiority_claim_allowed"
        ),
        "prose_residue_schema": prose_residue.get("schema"),
        "prose_residue_status": prose_residue.get("status"),
        "prose_main_body_machine_token_count": prose_residue.get("main_body_machine_token_count"),
        "prose_flat_main_body_machine_token_count": prose_residue.get("flat_main_body_machine_token_count"),
        "prose_artifact_filenames_confined_to_appendix": prose_residue.get("claim_boundary", {}).get(
            "artifact_filenames_confined_to_appendix"
        ),
        "prose_reader_facing_claim_language_preserved": prose_residue.get("claim_boundary", {}).get(
            "reader_facing_claim_language_preserved"
        ),
        "prose_b6_closed": prose_residue.get("claim_boundary", {}).get("b6_closed"),
        "prose_appendix_artifact_macro_count": prose_residue.get("appendix_evidence", {}).get("artifact_macro_count"),
        "prose_b6_preflight_status": prose_residue.get("b6_closure_readiness_preflight", {}).get("status"),
        "prose_b6_preflight_closed_preconditions": prose_residue.get(
            "b6_closure_readiness_preflight", {}
        ).get("closed_precondition_count"),
        "prose_b6_preflight_open_dependencies": prose_residue.get(
            "b6_closure_readiness_preflight", {}
        ).get("open_dependency_count"),
        "prose_b6_preflight_closure_allowed": prose_residue.get(
            "b6_closure_readiness_preflight", {}
        ).get("b6_closure_allowed_now"),
        "prose_b6_ready_command_mapped_rows": prose_residue.get(
            "post_baseline_final_prose_dependency", {}
        ).get("ready_command_dependency_boundary", {}).get("ready_command_mapped_external_rows"),
        "prose_b6_ready_command_unaddressed_rows": prose_residue.get(
            "post_baseline_final_prose_dependency", {}
        ).get("ready_command_dependency_boundary", {}).get("unaddressed_external_rows_after_ready_commands"),
        "prose_b6_ready_command_not_ready_lanes": prose_residue.get(
            "post_baseline_final_prose_dependency", {}
        ).get("ready_command_dependency_boundary", {}).get("not_ready_lanes_after_ready_commands"),
        "prose_b6_ready_commands_enable_final_prose": prose_residue.get(
            "post_baseline_final_prose_dependency", {}
        ).get("ready_command_dependency_boundary", {}).get("ready_commands_alone_can_enable_b6_final_prose_pass"),
        "prose_b6_post_execution_status": review_safe_b6_post_execution_status(prose_post_execution_boundary),
        "prose_b6_post_execution_promoted_rows": prose_residue.get(
            "post_baseline_final_prose_dependency", {}
        ).get("post_execution_dependency_boundary", {}).get("source_policy_rows_promoted_after_driver"),
        "prose_b6_post_execution_total_rows": prose_residue.get(
            "post_baseline_final_prose_dependency", {}
        ).get("post_execution_dependency_boundary", {}).get("source_policy_rows_total"),
        "prose_b6_post_execution_close_b4_b7": [
            prose_residue.get("post_baseline_final_prose_dependency", {})
            .get("post_execution_dependency_boundary", {})
            .get("b4_can_close_now"),
            prose_residue.get("post_baseline_final_prose_dependency", {})
            .get("post_execution_dependency_boundary", {})
            .get("b7_can_close_now"),
        ],
        "prose_b6_post_execution_enable_final_prose": prose_residue.get(
            "post_baseline_final_prose_dependency", {}
        ).get("post_execution_dependency_boundary", {}).get("final_prose_pass_enabled_by_post_execution"),
        "prose_proof_relocation_status": prose_residue.get("proof_prose_relocation_pass", {}).get("status"),
        "prose_proof_relocation_strict_boundary_preserved": prose_residue.get(
            "proof_prose_relocation_pass", {}
        ).get("strict_proof_boundary_preserved"),
        "prose_proof_relocation_b6_closed": prose_residue.get("proof_prose_relocation_pass", {}).get(
            "b6_closed_by_this_pass"
        ),
        "all_method_matrix_complete": all_matrix_complete,
        "all_method_matrix_method_count": all_matrix_method_count,
        "all_method_matrix_cell_count": all_matrix_cell_count,
        "paper_numerical_matrix_schema": numerical_matrix.get("schema"),
        "paper_numerical_matrix_status": numerical_matrix.get("status"),
        "paper_numerical_matrix_row_count": numerical_matrix.get("row_count"),
        "paper_numerical_matrix_expected_row_count": numerical_matrix.get("expected_row_count"),
        "paper_numerical_matrix_method_count": numerical_matrix.get("method_count"),
        "paper_numerical_matrix_raw_row_count": numerical_matrix.get("raw_row_count"),
        "paper_numerical_matrix_source_policy_external_superiority_allowed": numerical_matrix.get(
            "source_policy_external_superiority_allowed"
        ),
        "paper_numerical_matrix_direct_error_superiority_allowed": numerical_matrix.get(
            "paper_direct_error_superiority_allowed"
        ),
        "paper_numerical_matrix_strict_external_error_claim_rows": numerical_matrix.get(
            "strict_external_error_claim_allowed_rows"
        ),
        "paper_numerical_matrix_direct_order_wins": numerical_matrix.get("direct_nonlocal_velocity_order_wins"),
        "paper_numerical_matrix_direct_order_comparisons": numerical_matrix.get(
            "direct_nonlocal_velocity_order_comparisons"
        ),
        "paper_numerical_matrix_direct_error_wins": numerical_matrix.get("direct_nonlocal_velocity_error_wins"),
        "paper_numerical_matrix_direct_error_comparisons": numerical_matrix.get(
            "direct_nonlocal_velocity_error_comparisons"
        ),
        "result_traceability_schema": result_traceability.get("schema"),
        "result_traceability_status": result_traceability.get("status"),
        "result_traceability_velocity_cells_checked": result_traceability.get("coverage", {}).get(
            "velocity_cells_checked"
        ),
        "result_traceability_main_tex_cells": result_traceability.get("coverage", {}).get(
            "main_tex_velocity_cells_matched"
        ),
        "result_traceability_flat_tex_cells": result_traceability.get("coverage", {}).get(
            "flat_tex_velocity_cells_matched"
        ),
        "result_traceability_main_pdf_cells": result_traceability.get("coverage", {}).get(
            "main_pdf_velocity_cells_matched"
        ),
        "result_traceability_flat_pdf_cells": result_traceability.get("coverage", {}).get(
            "flat_pdf_velocity_cells_matched"
        ),
        "result_traceability_closed": result_traceability.get("claim_boundary", {}).get(
            "result_to_manuscript_traceability_closed"
        ),
        "result_traceability_source_policy_reproduction_closed": result_traceability.get("claim_boundary", {}).get(
            "source_policy_reproduction_closed"
        ),
        "result_traceability_external_superiority_allowed": result_traceability.get("claim_boundary", {}).get(
            "external_superiority_claim_allowed"
        ),
        "all_method_disposition_schema": all_method_disposition.get("schema"),
        "all_method_disposition_status": all_method_disposition.get("status"),
        "all_method_disposition_nonlocal_cells": all_method_disposition.get("coverage", {}).get("nonlocal_cells"),
        "all_method_disposition_expected_nonlocal_cells": all_method_disposition.get("coverage", {}).get(
            "expected_nonlocal_cells"
        ),
        "all_method_disposition_total_cells": all_method_disposition.get("coverage", {}).get("total_cells"),
        "all_method_disposition_raw_rows_recomputed": all_method_disposition.get("coverage", {}).get(
            "raw_rows_recomputed"
        ),
        "all_method_disposition_summary_mismatches": all_method_disposition.get("coverage", {}).get(
            "summary_mismatches"
        ),
        "all_method_disposition_order_wins": all_method_disposition.get("win_counts", {}).get(
            "local_velocity_order_wins"
        ),
        "all_method_disposition_order_comparisons": all_method_disposition.get("win_counts", {}).get(
            "local_velocity_order_comparisons"
        ),
        "all_method_disposition_error_wins": all_method_disposition.get("win_counts", {}).get(
            "local_finest_velocity_error_wins"
        ),
        "all_method_disposition_error_comparisons": all_method_disposition.get("win_counts", {}).get(
            "local_finest_velocity_error_comparisons"
        ),
        "all_method_disposition_source_policy_closed_rows": all_method_disposition.get(
            "claim_boundary", {}
        ).get("nonlocal_source_policy_closed_rows"),
        "all_method_disposition_source_policy_open_rows": all_method_disposition.get(
            "claim_boundary", {}
        ).get("nonlocal_source_policy_open_rows"),
        "all_method_disposition_flagged_nonlocal_rows": all_method_disposition.get("claim_boundary", {}).get(
            "flagged_nonlocal_rows"
        ),
        "all_method_disposition_strict_external_error_rows": all_method_disposition.get(
            "claim_boundary", {}
        ).get("strict_external_error_claim_allowed_rows"),
        "all_method_disposition_source_policy_superiority_allowed": all_method_disposition.get(
            "claim_boundary", {}
        ).get("source_policy_superiority_claim_allowed"),
        "manuscript_includes_source_policy_diagnosis": manuscript_includes_source_policy_diagnosis,
        "pdf_text_includes_source_policy_diagnosis": pdf_includes_source_policy_diagnosis,
        "manuscript_includes_all_example_source_policy_audit": manuscript_includes_all_example_source_policy_audit,
        "pdf_text_includes_all_example_source_policy_audit": pdf_includes_all_example_source_policy_audit,
        "manuscript_includes_active_tfe_b2_smoke": manuscript_includes_active_tfe_b2_smoke,
        "pdf_text_includes_active_tfe_b2_smoke": pdf_includes_active_tfe_b2_smoke,
        "manuscript_includes_tfe_full_t10_coarse_candidate": manuscript_includes_tfe_full_t10_coarse_candidate,
        "pdf_text_includes_tfe_full_t10_coarse_candidate": pdf_includes_tfe_full_t10_coarse_candidate,
        "manuscript_includes_tfe_brown_mcphee_boundary": manuscript_includes_tfe_brown_mcphee_boundary,
        "pdf_text_includes_tfe_brown_mcphee_boundary": pdf_includes_tfe_brown_mcphee_boundary,
        "manuscript_includes_tfe_appendix_b_certificate": manuscript_includes_tfe_appendix_b_certificate,
        "pdf_text_includes_tfe_appendix_b_certificate": pdf_includes_tfe_appendix_b_certificate,
        "manuscript_includes_tfe_m3_formula_probe": manuscript_includes_tfe_m3_formula_probe,
        "pdf_text_includes_tfe_m3_formula_probe": pdf_includes_tfe_m3_formula_probe,
        "manuscript_includes_minimal_reproducibility_boundary": (
            manuscript_includes_minimal_reproducibility_boundary
        ),
        "pdf_text_includes_minimal_reproducibility_boundary": pdf_includes_minimal_reproducibility_boundary,
        "manuscript_includes_comparison_reconciliation": manuscript_includes_comparison_reconciliation,
        "pdf_text_includes_comparison_reconciliation": pdf_includes_comparison_reconciliation,
        "all_examples_sanity_audit_schema": all_examples_audit.get("schema"),
        "all_examples_audited": all_examples_audit.get("all_four_examples_audited"),
        "all_examples_sanity_cell_count": all_examples_audit.get("coverage", {}).get("cell_count"),
        "all_examples_sanity_method_count": all_examples_audit.get("coverage", {}).get("method_count"),
        "all_examples_local_rows_passed": all_examples_audit.get("local_method_gate", {}).get("passed_rows"),
        "all_examples_local_rows_expected": all_examples_audit.get("local_method_gate", {}).get("expected_rows"),
        "all_examples_flagged_nonlocal_rows": all_examples_audit.get("baseline_sanity", {}).get("flagged_nonlocal_count"),
        "all_examples_flagged_examples": all_examples_audit.get("baseline_sanity", {}).get("flagged_examples"),
        "all_examples_source_policy_recheck_required": all_examples_audit.get("baseline_sanity", {}).get(
            "source_policy_recheck_required"
        ),
        "all_examples_external_superiority_allowed": all_examples_audit.get("paper_claim_boundary", {}).get(
            "external_superiority_allowed"
        ),
        "order_recomputation_audit_schema": recomputation_audit.get("schema"),
        "order_recomputation_all_summary_orders_recomputed": recomputation_audit.get("all_summary_orders_recomputed"),
        "order_recomputation_cell_count": recomputation_audit.get("coverage", {}).get("method_example_cell_count"),
        "order_recomputation_raw_row_count": recomputation_audit.get("coverage", {}).get("raw_ok_row_count"),
        "order_recomputation_mismatch_count": recomputation_audit.get("verification", {}).get("mismatch_count"),
        "order_recomputation_max_order_abs_diff": recomputation_audit.get("verification", {}).get("max_order_abs_diff"),
        "order_recomputation_anomaly_rows": recomputation_audit.get("anomalies", {}).get("anomaly_row_count"),
        "order_recomputation_external_superiority_allowed": recomputation_audit.get("claim_boundary", {}).get(
            "external_superiority_allowed"
        ),
        "comparison_reconciliation_schema": comparison_reconciliation.get("schema"),
        "comparison_reconciliation_status": comparison_reconciliation.get("status"),
        "comparison_matrix_closed": comparison_reconciliation.get("comparison_matrix_closed"),
        "common_reference_claim_allowed": comparison_reconciliation.get("common_reference_claim_allowed"),
        "source_policy_superiority_claim_allowed": comparison_reconciliation.get(
            "source_policy_superiority_claim_allowed"
        ),
        "comparison_reconciliation_direct_order_wins": comparison_reconciliation.get(
            "direct_nonlocal_velocity_order_wins"
        ),
        "comparison_reconciliation_direct_order_comparisons": comparison_reconciliation.get(
            "direct_nonlocal_velocity_order_comparisons"
        ),
        "comparison_reconciliation_direct_error_wins": comparison_reconciliation.get(
            "direct_nonlocal_finest_velocity_error_wins"
        ),
        "comparison_reconciliation_direct_error_comparisons": comparison_reconciliation.get(
            "direct_nonlocal_finest_velocity_error_comparisons"
        ),
        "comparison_reconciliation_required_methods_resolved": comparison_reconciliation.get(
            "required_method_labels_resolved"
        ),
        "comparison_reconciliation_b2_b4_can_close_now": comparison_reconciliation.get(
            "b2_b4_reconciliation", {}
        ).get("paper_submission_b2_b4_can_close_now"),
        "common_reference_traceability_rows": result_pack.get("common_reference", {}).get("apples_to_apples_rows"),
        "common_reference_traceability_total_rows": result_pack.get("common_reference", {}).get(
            "apples_to_apples_total_rows"
        ),
        "source_policy_apples_to_apples_external_rows": all_method_disposition.get("claim_boundary", {}).get(
            "nonlocal_source_policy_closed_rows"
        ),
        "source_policy_apples_to_apples_external_total_rows": all_method_disposition.get("claim_boundary", {}).get(
            "nonlocal_source_policy_open_rows"
        )
        + all_method_disposition.get("claim_boundary", {}).get("nonlocal_source_policy_closed_rows"),
        "global_policy_passed": global_policy.get("reasonable_apples_to_apples_claims"),
        "global_policy_passed_count": global_policy.get("passed_count"),
        "global_policy_row_count": global_policy.get("row_count"),
        "mixed_policy_direct_error_rows": global_policy.get("mixed_policy_direct_error_vs_local_comparable_rows"),
        "paper_direct_error_rows_allowed": global_policy.get("direct_error_rows_allowed_for_paper"),
        "paper_direct_error_superiority_allowed": global_policy.get("paper_direct_error_superiority_claim_allowed"),
        "source_policy_reproduction": result_pack.get("common_reference", {}).get("source_policy_reproduction"),
        "public_code_fixed_grid_replay": result_pack.get("common_reference", {}).get("public_code_fixed_grid_replay"),
    }
    proof_checks = {
        "proof_contract_status": proof_gate.get("status"),
        "proof_style_audit_schema": proof_style.get("schema"),
        "proof_closure_manifest_schema": proof_closure.get("schema"),
        "proof_closure_manifest_status": proof_closure.get("status"),
        "proof_claim_traceability_schema": proof_traceability.get("schema"),
        "proof_claim_traceability_status": proof_traceability.get("status"),
        "proof_claim_traceability_submission_ready": proof_traceability.get("submission_ready"),
        "proof_claim_traceability_theorem_label": proof_traceability.get(
            "manuscript_theorem_traceability", {}
        ).get("accepted_theorem_label"),
        "proof_claim_traceability_theorem_labels_present": proof_traceability.get(
            "manuscript_theorem_traceability", {}
        ).get("theorem_statement_labels_present"),
        "proof_claim_traceability_theorem_boundary_present": proof_traceability.get(
            "manuscript_theorem_traceability", {}
        ).get("conditional_theorem_boundary_present"),
        "proof_claim_traceability_theorem_claims_mapped": proof_traceability.get(
            "manuscript_theorem_traceability", {}
        ).get("conditional_proof_claims_mapped_to_manuscript"),
        "proof_claim_traceability_dependency_graph_present": proof_traceability.get(
            "manuscript_theorem_traceability", {}
        ).get("proof_dependency_graph_present"),
        "proof_claim_traceability_table_present": proof_traceability.get(
            "manuscript_theorem_traceability", {}
        ).get("proof_traceability_table_present"),
        "proof_claim_traceability_dynamic_theorem_matrix_present": proof_traceability.get(
            "manuscript_theorem_traceability", {}
        ).get("dynamic_proof_closure_matrix_present"),
        "proof_claim_traceability_primitive_lane_boundary_present": proof_traceability.get(
            "manuscript_theorem_traceability", {}
        ).get("primitive_lane_boundary_present"),
        "proof_claim_traceability_residual_nonpromotion_present": proof_traceability.get(
            "manuscript_theorem_traceability", {}
        ).get("residual_nonpromotion_present"),
        "proof_claim_traceability_eta_condition_retained": proof_traceability.get(
            "manuscript_theorem_traceability", {}
        ).get("eta_h_theorem_condition_retained"),
        "proof_claim_traceability_eta_evidence_closed": proof_traceability.get(
            "manuscript_theorem_traceability", {}
        ).get("eta_h_solver_policy_evidence_closed"),
        "proof_claim_traceability_fixed_tolerance_asymptotic_proof": proof_traceability.get(
            "manuscript_theorem_traceability", {}
        ).get("fixed_tolerance_runs_are_asymptotic_proof"),
        "proof_claim_traceability_residual_to_error_not_promoted": proof_traceability.get(
            "manuscript_theorem_traceability", {}
        ).get("residual_to_error_not_promoted"),
        "proof_claim_traceability_p7_retained_nonpromotion_boundary_present": proof_traceability.get(
            "manuscript_theorem_traceability", {}
        ).get("p7_retained_nonpromotion_boundary_present"),
        "proof_claim_traceability_b1_closure_scope_boundary_present": proof_traceability.get(
            "manuscript_theorem_traceability", {}
        ).get("b1_closure_scope_boundary_present"),
        "proof_claim_traceability_p6_solver_scope_boundary_present": proof_traceability.get(
            "manuscript_theorem_traceability", {}
        ).get("p6_solver_scope_boundary_present"),
        "proof_claim_traceability_p1p2_compact_tube_boundary_present": proof_traceability.get(
            "manuscript_theorem_traceability", {}
        ).get("p1p2_compact_tube_boundary_present"),
        "proof_claim_traceability_p3p4_implementation_boundary_present": proof_traceability.get(
            "manuscript_theorem_traceability", {}
        ).get("p3p4_implementation_boundary_present"),
        "proof_claim_traceability_p5_direct_route_boundary_present": proof_traceability.get(
            "manuscript_theorem_traceability", {}
        ).get("p5_direct_route_boundary_present"),
        "proof_claim_traceability_proof_causality_ledger_present": proof_traceability.get(
            "manuscript_theorem_traceability", {}
        ).get("proof_causality_ledger_present"),
        "proof_claim_traceability_direct_route_anticircularity_ledger_present": proof_traceability.get(
            "manuscript_theorem_traceability", {}
        ).get("direct_route_anticircularity_ledger_present"),
        "proof_claim_traceability_p_interface_satisfaction_ledger_present": proof_traceability.get(
            "manuscript_theorem_traceability", {}
        ).get("p_interface_satisfaction_ledger_present"),
        "proof_claim_traceability_p7_residual_to_error_ledger_present": proof_traceability.get(
            "manuscript_theorem_traceability", {}
        ).get("p7_residual_to_error_ledger_present"),
        "proof_claim_traceability_theorem_use_rule_present": proof_traceability.get(
            "manuscript_theorem_traceability", {}
        ).get("theorem_use_rule_present"),
        "proof_claim_traceability_quantifier_domain_ledger_present": proof_traceability.get(
            "manuscript_theorem_traceability", {}
        ).get("quantifier_domain_ledger_present"),
        "proof_claim_traceability_local_global_transfer_ledger_present": proof_traceability.get(
            "manuscript_theorem_traceability", {}
        ).get("local_global_transfer_ledger_present"),
        "proof_claim_traceability_objective_completion_boundary_present": proof_traceability.get(
            "manuscript_theorem_traceability", {}
        ).get("objective_completion_boundary_present"),
        "proof_claim_traceability_constant_dependency_ledger_present": proof_traceability.get(
            "manuscript_theorem_traceability", {}
        ).get("constant_dependency_ledger_present"),
        "proof_claim_traceability_theorem_dependency_consumption_ledger_present": proof_traceability.get(
            "manuscript_theorem_traceability", {}
        ).get("theorem_dependency_consumption_ledger_present"),
        "proof_claim_traceability_branch_consistency_ledger_present": proof_traceability.get(
            "manuscript_theorem_traceability", {}
        ).get("branch_consistency_ledger_present"),
        "proof_claim_traceability_implementation_route_oracle_ledger_present": proof_traceability.get(
            "manuscript_theorem_traceability", {}
        ).get("implementation_route_oracle_ledger_present"),
        "proof_claim_traceability_nonlinear_solver_scale_ledger_present": proof_traceability.get(
            "manuscript_theorem_traceability", {}
        ).get("nonlinear_solver_scale_ledger_present"),
        "proof_claim_traceability_local_defect_decomposition_ledger_present": proof_traceability.get(
            "manuscript_theorem_traceability", {}
        ).get("local_defect_decomposition_ledger_present"),
        "proof_claim_traceability_theorem_output_scope_ledger_present": proof_traceability.get(
            "manuscript_theorem_traceability", {}
        ).get("theorem_output_scope_ledger_present"),
        "proof_claim_traceability_reporting_map_ledger_present": proof_traceability.get(
            "manuscript_theorem_traceability", {}
        ).get("reporting_map_ledger_present"),
        "proof_claim_traceability_theorem_conclusion_scope_guard_present": proof_traceability.get(
            "manuscript_theorem_traceability", {}
        ).get("theorem_conclusion_scope_guard_present"),
        "proof_claim_traceability_proof_strength_certificate_present": proof_traceability.get(
            "manuscript_theorem_traceability", {}
        ).get("proof_strength_certificate_present"),
        "proof_claim_traceability_full_residual_bridge_present": proof_traceability.get(
            "manuscript_theorem_traceability", {}
        ).get("full_residual_bridge_present"),
        "proof_claim_traceability_route_exclusivity_boundary_present": proof_traceability.get(
            "manuscript_theorem_traceability", {}
        ).get("route_exclusivity_boundary_present"),
        "proof_claim_traceability_theorem_residual_certificate_exclusivity_present": proof_traceability.get(
            "manuscript_theorem_traceability", {}
        ).get("theorem_residual_certificate_exclusivity_present"),
        "proof_claim_traceability_source_policy_or_full_tfe_not_promoted": proof_traceability.get(
            "manuscript_theorem_traceability", {}
        ).get("source_policy_or_full_tfe_not_promoted"),
        "proof_claim_traceability_no_state_change": proof_traceability.get(
            "manuscript_theorem_traceability", {}
        ).get("does_not_change_proof_closure_state"),
        "proof_claim_traceability_writing_card_status": proof_traceability.get(
            "proof_writing_boundary_card", {}
        ).get("status"),
        "proof_claim_traceability_writing_card_safe_claim": proof_traceability.get(
            "proof_writing_boundary_card", {}
        ).get("safe_reader_claim"),
        "proof_claim_traceability_writing_card_forbidden_claims": proof_traceability.get(
            "proof_writing_boundary_card", {}
        ).get("forbidden_reader_claims"),
        "proof_claim_traceability_reader_facing_manuscript_boundary_present": proof_traceability.get(
            "proof_writing_boundary_card", {}
        ).get("reader_facing_manuscript_boundary_present"),
        "proof_remaining_work_schema": proof_remaining_work.get("schema"),
        "proof_remaining_work_status": proof_remaining_work.get("status"),
        "proof_remaining_work_submission_ready": proof_remaining_work.get("submission_ready"),
        "proof_remaining_work_submission_ready_scope": proof_remaining_work.get("submission_ready_scope"),
        "proof_remaining_work_manifest_scope": proof_remaining_work.get("readiness_boundary", {}).get(
            "proof_remaining_work_manifest_scope"
        ),
        "proof_remaining_work_narrowed_claim_b4_b6_b7_statuses": proof_remaining_work.get(
            "readiness_boundary", {}
        ).get("narrowed_claim_b4_b6_b7_statuses"),
        "proof_remaining_work_global_submission_boundaries_retained": proof_remaining_work.get(
            "readiness_boundary", {}
        ).get("global_submission_boundaries_retained"),
        "proof_remaining_work_unsatisfied_close_requirements": proof_remaining_work.get("summary", {}).get(
            "unsatisfied_close_requirement_count"
        ),
        "proof_remaining_work_unsatisfied_close_requirement_ids": proof_remaining_work.get("summary", {}).get(
            "unsatisfied_close_requirement_ids"
        ),
        "proof_remaining_work_certified_non_dynamic_rows": proof_remaining_work.get("summary", {}).get(
            "certified_non_dynamic_rows"
        ),
        "proof_remaining_work_open_dynamic_rows": proof_remaining_work.get("summary", {}).get("open_dynamic_rows"),
        "proof_remaining_work_newton_euler_row_obligation_links": proof_remaining_work.get("summary", {}).get(
            "newton_euler_row_obligation_links"
        ),
        "proof_remaining_work_finite_trajectory_steps": proof_remaining_work.get("summary", {}).get(
            "finite_scaled_tolerance_trajectory_probe_steps"
        ),
        "proof_remaining_work_default_1e_4_required": proof_remaining_work.get("execution_policy", {}).get(
            "default_1e_4_required"
        ),
        "proof_remaining_work_heavy_run_invoked": proof_remaining_work.get("execution_policy", {}).get(
            "heavy_numerical_run_invoked"
        ),
        "proof_remaining_work_run_v047_invoked": proof_remaining_work.get("execution_policy", {}).get(
            "run_v047_invoked"
        ),
        "proof_remaining_work_newton_euler_certificate_present": proof_remaining_work.get("summary", {}).get(
            "newton_euler_symbolic_defect_certificate_present"
        ),
        "proof_remaining_work_newton_euler_certificate_complete": proof_remaining_work.get("summary", {}).get(
            "newton_euler_symbolic_defect_certificate_complete"
        ),
        "proof_remaining_work_newton_euler_runtime_expression_structure_checked": proof_remaining_work.get(
            "summary", {}
        ).get("newton_euler_symbolic_defect_certificate_runtime_expression_structure_checked"),
        "proof_remaining_work_newton_euler_runtime_expression_checked_rows": proof_remaining_work.get("summary", {}).get(
            "newton_euler_symbolic_defect_certificate_runtime_expression_checked_rows"
        ),
        "proof_remaining_work_newton_euler_runtime_template_instantiation_checked": proof_remaining_work.get(
            "summary", {}
        ).get("newton_euler_symbolic_defect_certificate_runtime_template_instantiation_checked"),
        "proof_remaining_work_newton_euler_runtime_template_instantiation_checked_rows": proof_remaining_work.get(
            "summary", {}
        ).get("newton_euler_symbolic_defect_certificate_runtime_template_instantiation_checked_rows"),
        "proof_remaining_work_b1_independent_symbolic_row_oracle_closed": proof_remaining_work.get(
            "summary", {}
        ).get("b1_independent_symbolic_row_oracle_closed"),
        "proof_remaining_work_b1_independent_symbolic_row_oracle_closed_rows": proof_remaining_work.get(
            "summary", {}
        ).get("b1_independent_symbolic_row_oracle_closed_rows"),
        "proof_remaining_work_b1_source_template_symbolic_identity_rows": proof_remaining_work.get(
            "summary", {}
        ).get("b1_source_template_symbolic_identity_rows"),
        "proof_remaining_work_b1_runtime_row_binding_checked_rows": proof_remaining_work.get(
            "summary", {}
        ).get("b1_runtime_row_binding_checked_rows"),
        "proof_remaining_work_b1_ad_expanded_symbolic_oracle_closure": proof_remaining_work.get(
            "summary", {}
        ).get("b1_ad_expanded_symbolic_oracle_closure"),
        "proof_remaining_work_b1_ad_expanded_symbolic_oracle_closed_rows": proof_remaining_work.get(
            "summary", {}
        ).get("b1_ad_expanded_symbolic_oracle_closed_rows"),
        "proof_remaining_work_b1_ad_expanded_symbolic_oracle_columns_per_row": proof_remaining_work.get(
            "summary", {}
        ).get("b1_ad_expanded_symbolic_oracle_columns_per_row"),
        "proof_remaining_work_b1_ad_expanded_symbolic_oracle_closed_cells": proof_remaining_work.get(
            "summary", {}
        ).get("b1_ad_expanded_symbolic_oracle_closed_cells"),
        "newton_euler_symbolic_defect_certificate_artifact_schema": newton_euler_symbolic_defect_certificate.get("schema"),
        "newton_euler_symbolic_defect_certificate_artifact_status": newton_euler_symbolic_defect_certificate.get("status"),
        "newton_euler_symbolic_defect_certificate_artifact_complete": newton_euler_symbolic_defect_certificate.get(
            "certificate_complete"
        ),
        "newton_euler_symbolic_defect_certificate_artifact_rows": newton_euler_symbolic_defect_certificate.get(
            "summary", {}
        ).get("row_count"),
        "newton_euler_symbolic_defect_certificate_artifact_certified_rows": newton_euler_symbolic_defect_certificate.get(
            "summary", {}
        ).get("certified_row_count"),
        "newton_euler_symbolic_defect_certificate_artifact_open_rows": newton_euler_symbolic_defect_certificate.get(
            "summary", {}
        ).get("open_row_count"),
        "newton_euler_symbolic_defect_certificate_artifact_open_obligations": newton_euler_symbolic_defect_certificate.get(
            "summary", {}
        ).get("open_obligation_count"),
        "newton_euler_symbolic_defect_certificate_artifact_closed_obligations": newton_euler_symbolic_defect_certificate.get(
            "summary", {}
        ).get("closed_obligation_count"),
        "newton_euler_symbolic_defect_certificate_artifact_row_obligation_links": (
            newton_euler_symbolic_defect_certificate.get("summary", {}).get("row_obligation_link_count")
        ),
        "newton_euler_symbolic_defect_certificate_artifact_runtime_expression_structure_checked": (
            newton_euler_symbolic_defect_certificate.get("summary", {}).get("runtime_expression_structure_checked")
        ),
        "newton_euler_symbolic_defect_certificate_artifact_runtime_expression_checked_rows": (
            newton_euler_symbolic_defect_certificate.get("summary", {}).get("runtime_expression_structure_checked_rows")
        ),
        "newton_euler_symbolic_defect_certificate_artifact_runtime_template_instantiation_checked": (
            newton_euler_symbolic_defect_certificate.get("summary", {}).get(
                "runtime_template_instantiation_checked"
            )
        ),
        "newton_euler_symbolic_defect_certificate_artifact_runtime_template_instantiation_checked_rows": (
            newton_euler_symbolic_defect_certificate.get("summary", {}).get(
                "runtime_template_instantiation_checked_rows"
            )
        ),
        "newton_euler_symbolic_defect_certificate_artifact_body_specific_wrench_checked": (
            newton_euler_symbolic_defect_certificate.get("summary", {}).get(
                "body_specific_wrench_expansion_checked"
            )
        ),
        "newton_euler_symbolic_defect_certificate_artifact_body_specific_wrench_rows": (
            newton_euler_symbolic_defect_certificate.get("summary", {}).get(
                "body_specific_wrench_expansion_checked_rows"
            )
        ),
        "newton_euler_symbolic_defect_certificate_artifact_body0_wrench_rows": (
            newton_euler_symbolic_defect_certificate.get("summary", {}).get("body0_wrench_expansion_rows")
        ),
        "newton_euler_symbolic_defect_certificate_artifact_body1_wrench_rows": (
            newton_euler_symbolic_defect_certificate.get("summary", {}).get("body1_wrench_expansion_rows")
        ),
        "newton_euler_symbolic_defect_certificate_artifact_template_algebraic_equivalence_checked": (
            newton_euler_symbolic_defect_certificate.get("summary", {}).get(
                "template_algebraic_equivalence_checked"
            )
        ),
        "newton_euler_symbolic_defect_certificate_artifact_template_algebraic_equivalence_checked_rows": (
            newton_euler_symbolic_defect_certificate.get("summary", {}).get(
                "template_algebraic_equivalence_checked_rows"
            )
        ),
        "newton_euler_symbolic_defect_certificate_artifact_c2_template_algebraic_equivalence_closed": (
            newton_euler_symbolic_defect_certificate.get("summary", {}).get(
                "c2_template_algebraic_equivalence_closed"
            )
        ),
        "b1_symbolic_row_oracle_closure_schema": b1_symbolic_row_oracle_closure.get("schema"),
        "b1_symbolic_row_oracle_closure_status": b1_symbolic_row_oracle_closure.get("status"),
        "b1_independent_symbolic_row_by_row_oracle_for_expanded_fullva_rows_closed": (
            b1_symbolic_row_oracle_closure.get(
                "independent_symbolic_row_by_row_oracle_for_expanded_fullva_rows_closed"
            )
        ),
        "b1_independent_symbolic_row_oracle_closed_rows": b1_symbolic_row_oracle_closure.get(
            "independent_symbolic_row_by_row_oracle_closed_rows"
        ),
        "b1_source_template_symbolic_identity_rows": b1_symbolic_row_oracle_closure.get(
            "source_template_symbolic_identity_rows"
        ),
        "b1_runtime_row_binding_checked_rows": b1_symbolic_row_oracle_closure.get(
            "runtime_row_binding_checked_rows"
        ),
        "b1_symbolic_row_oracle_ad_expanded_symbolic_oracle_closure": b1_symbolic_row_oracle_closure.get(
            "ad_expanded_symbolic_oracle_closure"
        ),
        "b1_symbolic_row_oracle_dynamic_symbolic_oracle_complete": b1_symbolic_row_oracle_closure.get(
            "dynamic_symbolic_oracle_complete"
        ),
        "b1_symbolic_row_oracle_stage_residual_O_h7_symbolic_certificate_proved": (
            b1_symbolic_row_oracle_closure.get("stage_residual_O_h7_symbolic_certificate_proved")
        ),
        "b1_symbolic_row_oracle_remaining_required_item": b1_symbolic_row_oracle_closure.get(
            "remaining_b1_required_item"
        ),
        "b1_ad_expanded_symbolic_oracle_closure_schema": b1_ad_expanded_symbolic_oracle_closure.get(
            "schema"
        ),
        "b1_ad_expanded_symbolic_oracle_closure_status": b1_ad_expanded_symbolic_oracle_closure.get(
            "status"
        ),
        "b1_ad_expanded_symbolic_oracle_closure": b1_ad_expanded_symbolic_oracle_closure.get(
            "ad_expanded_symbolic_oracle_closure"
        ),
        "b1_ad_expanded_symbolic_oracle_closed_rows": b1_ad_expanded_symbolic_oracle_closure.get(
            "ad_expanded_symbolic_oracle_closed_rows"
        ),
        "b1_ad_expanded_symbolic_oracle_columns_per_row": b1_ad_expanded_symbolic_oracle_closure.get(
            "columns_per_row"
        ),
        "b1_ad_expanded_symbolic_oracle_closed_cells": b1_ad_expanded_symbolic_oracle_closure.get(
            "ad_expanded_symbolic_oracle_closed_cells"
        ),
        "b1_ad_expanded_symbolic_oracle_dynamic_symbolic_oracle_complete": (
            b1_ad_expanded_symbolic_oracle_closure.get("dynamic_symbolic_oracle_complete")
        ),
        "b1_ad_expanded_symbolic_oracle_stage_residual_O_h7_symbolic_certificate_proved": (
            b1_ad_expanded_symbolic_oracle_closure.get("stage_residual_O_h7_symbolic_certificate_proved")
        ),
        "b1_ad_expanded_symbolic_oracle_proof_gap_closed_by_this_certificate": (
            b1_ad_expanded_symbolic_oracle_closure.get("proof_gap_closed_by_this_certificate")
        ),
        "b1_ad_expanded_symbolic_oracle_submission_ready": (
            b1_ad_expanded_symbolic_oracle_closure.get("submission_ready")
        ),
        "newton_euler_ad_expanded_row_oracle_schema": newton_euler_ad_expanded_row_oracle.get("schema"),
        "newton_euler_ad_expanded_row_oracle_status": newton_euler_ad_expanded_row_oracle.get("status"),
        "newton_euler_ad_expanded_row_oracle_closed": newton_euler_ad_expanded_row_oracle.get(
            "ad_expanded_row_oracle_closed"
        ),
        "newton_euler_ad_expanded_row_oracle_rows": newton_euler_ad_expanded_row_oracle.get(
            "ad_expanded_row_oracle_rows"
        ),
        "newton_euler_ad_expanded_row_oracle_columns_per_row": newton_euler_ad_expanded_row_oracle.get(
            "ad_expanded_row_oracle_columns_per_row"
        ),
        "newton_euler_ad_expanded_row_oracle_probe_count": newton_euler_ad_expanded_row_oracle.get(
            "formula_row_ad_jacobian_probe_count"
        ),
        "newton_euler_ad_expanded_row_oracle_max_mismatch": newton_euler_ad_expanded_row_oracle.get(
            "formula_row_ad_jacobian_max_mismatch"
        ),
        "newton_euler_ad_expanded_symbolic_oracle_closure": newton_euler_ad_expanded_row_oracle.get(
            "ad_expanded_symbolic_oracle_closure"
        ),
        "newton_euler_ad_expanded_independent_symbolic_row_oracle_closed": (
            newton_euler_ad_expanded_row_oracle.get("independent_symbolic_row_by_row_oracle_closed")
        ),
        "newton_euler_symbolic_defect_certificate_artifact_ad_expanded_rows": (
            newton_euler_symbolic_defect_certificate.get("summary", {}).get("ad_expanded_row_oracle_rows")
        ),
        "newton_euler_symbolic_defect_certificate_artifact_ad_expanded_symbolic_oracle_closure": (
            newton_euler_symbolic_defect_certificate.get("summary", {}).get(
                "ad_expanded_symbolic_oracle_closure"
            )
        ),
        "newton_euler_symbolic_defect_certificate_artifact_proof_gap_closed": newton_euler_symbolic_defect_certificate.get(
            "proof_gap_closed"
        ),
        "proof_claim_traceability_main_labels_present": proof_traceability.get("main_source", {}).get(
            "all_labels_present"
        ),
        "proof_claim_traceability_flat_labels_present": proof_traceability.get("flat_source", {}).get(
            "all_labels_present"
        ),
        "proof_claim_traceability_main_boundary_tokens_present": proof_traceability.get("main_source", {}).get(
            "all_boundary_tokens_present"
        ),
        "proof_claim_traceability_flat_boundary_tokens_present": proof_traceability.get("flat_source", {}).get(
            "all_boundary_tokens_present"
        ),
        "proof_claim_traceability_object_counts_match": proof_traceability.get("main_source", {}).get(
            "proof_object_counts_match_expected"
        )
        and proof_traceability.get("flat_source", {}).get("proof_object_counts_match_expected"),
        "proof_claim_traceability_theorem_assumptions": proof_traceability.get("theorem_assumption_count"),
        "proof_claim_traceability_unsatisfied_assumptions": proof_traceability.get(
            "unsatisfied_theorem_assumption_count"
        ),
        "proof_claim_traceability_satisfied_assumptions": proof_traceability.get("theorem_assumption_count")
        - proof_traceability.get("unsatisfied_theorem_assumption_count"),
        "proof_claim_traceability_remaining_boundary_status": proof_traceability.get(
            "remaining_claim_boundary", {}
        ).get("status"),
        "proof_claim_traceability_submission_satisfied_assumption_ids": proof_traceability.get(
            "remaining_claim_boundary", {}
        ).get("submission_satisfied_ids"),
        "proof_claim_traceability_retained_or_open_assumption_ids": proof_traceability.get(
            "remaining_claim_boundary", {}
        ).get("retained_or_open_ids"),
        "proof_claim_traceability_retained_theorem_interface_ids": proof_traceability.get(
            "remaining_claim_boundary", {}
        ).get("retained_theorem_interface_ids"),
        "proof_claim_traceability_open_nonpromotion_boundary_ids": proof_traceability.get(
            "remaining_claim_boundary", {}
        ).get("open_nonpromotion_boundary_ids"),
        "proof_claim_traceability_retained_theorem_interface_count": proof_traceability.get(
            "remaining_claim_boundary", {}
        ).get("retained_theorem_interface_count"),
        "proof_claim_traceability_open_nonpromotion_boundary_count": proof_traceability.get(
            "remaining_claim_boundary", {}
        ).get("open_nonpromotion_boundary_count"),
        "proof_claim_traceability_remaining_global_boundaries": proof_traceability.get(
            "remaining_claim_boundary", {}
        ).get("global_submission_boundaries_retained"),
        "proof_claim_traceability_manuscript_anchor_map_present": proof_traceability.get(
            "manuscript_anchor_map", {}
        ).get("all_label_anchors_present"),
        "proof_claim_traceability_manuscript_anchor_label_count": proof_traceability.get(
            "manuscript_anchor_map", {}
        ).get("label_anchor_count"),
        "proof_claim_traceability_theorem_assumption_anchor_map_present": proof_traceability.get(
            "manuscript_anchor_map", {}
        ).get("all_theorem_assumption_anchors_present"),
        "proof_claim_traceability_theorem_assumption_anchor_count": proof_traceability.get(
            "manuscript_anchor_map", {}
        ).get("theorem_assumption_anchor_count"),
        "proof_claim_traceability_theorem_assumption_anchor_ids": proof_traceability.get(
            "manuscript_anchor_map", {}
        ).get("theorem_assumption_anchor_ids"),
        "proof_closure_manuscript_anchor_map_present": proof_closure.get(
            "manuscript_anchor_map", {}
        ).get("all_label_anchors_present"),
        "proof_closure_manuscript_anchor_label_count": proof_closure.get(
            "manuscript_anchor_map", {}
        ).get("label_anchor_count"),
        "proof_closure_theorem_assumption_anchor_map_present": proof_closure.get(
            "manuscript_anchor_map", {}
        ).get("all_theorem_assumption_anchors_present"),
        "proof_closure_theorem_assumption_anchor_count": proof_closure.get(
            "manuscript_anchor_map", {}
        ).get("theorem_assumption_anchor_count"),
        "proof_closure_theorem_assumption_anchor_ids": proof_closure.get(
            "manuscript_anchor_map", {}
        ).get("theorem_assumption_anchor_ids"),
        "proof_closure_proof_claim_anchor_maps_match": proof_closure.get(
            "manuscript_anchor_map", {}
        )
        == proof_traceability.get("manuscript_anchor_map", {}),
        "proof_contract_anchor_evidence_sources": proof_gate.get(
            "manuscript_theorem_traceability", {}
        ).get("anchor_evidence_sources"),
        "proof_style_anchor_evidence_sources": proof_style.get(
            "proof_contract_theorem_traceability", {}
        ).get("anchor_evidence_sources"),
        "strict_proof_anchor_evidence_sources": strict_proof_audit.get(
            "manuscript_theorem_traceability", {}
        ).get("anchor_evidence_sources"),
        "proof_anchor_evidence_sources_match": proof_gate.get(
            "manuscript_theorem_traceability", {}
        ).get("anchor_evidence_sources")
        == proof_style.get("proof_contract_theorem_traceability", {}).get("anchor_evidence_sources")
        == strict_proof_audit.get("manuscript_theorem_traceability", {}).get(
            "anchor_evidence_sources"
        )
        == ["PROOF_CLOSURE_MANIFEST.json", "PROOF_CLAIM_TRACEABILITY_AUDIT.json"],
        "proof_claim_traceability_close_requirements": proof_traceability.get("close_requirement_count"),
        "proof_claim_traceability_satisfied_close_requirements": proof_traceability.get(
            "satisfied_close_requirement_count"
        ),
        "proof_claim_traceability_unsatisfied_close_requirements": proof_traceability.get(
            "unsatisfied_close_requirement_count"
        ),
        "proof_claim_traceability_pc3_condition_retained": any(
            item.get("id") == "PC3" and item.get("satisfied")
            for item in proof_traceability.get("close_requirements", [])
        ),
        "proof_claim_traceability_pc4_residual_promotion_avoided": any(
            item.get("id") == "PC4" and item.get("satisfied")
            for item in proof_traceability.get("close_requirements", [])
        ),
        "proof_claim_traceability_newton_euler_open_obligations": proof_traceability.get(
            "newton_euler_open_obligation_count"
        ),
        "proof_claim_traceability_open_dynamic_rows_scope": proof_traceability.get("open_dynamic_rows_scope"),
        "proof_claim_traceability_active_direct_newton_euler_closed_rows": proof_traceability.get(
            "active_direct_newton_euler_closed_rows"
        ),
        "proof_claim_traceability_active_direct_newton_euler_open_rows": proof_traceability.get(
            "active_direct_newton_euler_open_rows"
        ),
        "proof_claim_traceability_active_direct_newton_euler_open_obligations": proof_traceability.get(
            "active_direct_newton_euler_open_obligations"
        ),
        "proof_claim_traceability_symbolic_primitive_newton_euler_open_obligations": proof_traceability.get(
            "newton_euler_open_obligation_count"
        ),
        "proof_claim_traceability_newton_euler_closed_obligations": proof_traceability.get(
            "newton_euler_closed_obligation_count"
        ),
        "proof_claim_traceability_residual_to_error_blockers": proof_traceability.get(
            "residual_to_error_blocking_obligations"
        ),
        "proof_claim_traceability_certified_non_dynamic_rows": proof_traceability.get("certified_non_dynamic_rows"),
        "proof_claim_traceability_open_dynamic_rows": proof_traceability.get("open_dynamic_rows"),
        "proof_claim_traceability_row_target_map_present": proof_traceability.get(
            "newton_euler_row_target_map_present"
        ),
        "proof_claim_traceability_newton_euler_symbolic_target_rows": proof_traceability.get(
            "newton_euler_symbolic_target_rows"
        ),
        "proof_claim_traceability_newton_euler_symbolic_target_translational_rows": proof_traceability.get(
            "newton_euler_symbolic_target_translational_rows"
        ),
        "proof_claim_traceability_newton_euler_symbolic_target_rotational_rows": proof_traceability.get(
            "newton_euler_symbolic_target_rotational_rows"
        ),
        "proof_claim_traceability_newton_euler_obligation_coverage_matrix_complete": proof_traceability.get(
            "newton_euler_obligation_coverage_matrix_complete"
        ),
        "proof_claim_traceability_newton_euler_row_obligation_links": proof_traceability.get(
            "newton_euler_row_obligation_links"
        ),
        "proof_claim_traceability_newton_euler_rows_with_complete_obligation_sets": proof_traceability.get(
            "newton_euler_rows_with_complete_obligation_sets"
        ),
        "proof_claim_traceability_newton_euler_obligations_with_target_rows": proof_traceability.get(
            "newton_euler_obligations_with_target_rows"
        ),
        "proof_claim_traceability_newton_euler_obligation_coverage_proof_closure_advanced": (
            proof_traceability.get("newton_euler_obligation_coverage_proof_closure_advanced")
        ),
        "proof_claim_traceability_newton_euler_symbolic_defect_certificate_complete": proof_traceability.get(
            "newton_euler_symbolic_defect_certificate_complete"
        ),
        "proof_claim_traceability_open_symbolic_oracle_recorded": proof_traceability.get(
            "proof_evidence_matrix_mentions_open_symbolic_oracle"
        ),
        "proof_claim_traceability_dynamic_matrix_present": proof_traceability.get(
            "dynamic_proof_closure_matrix_present"
        ),
        "proof_claim_traceability_dynamic_matrix_status": proof_traceability.get(
            "dynamic_proof_closure_matrix_status"
        ),
        "proof_closure_certified_non_dynamic_rows": proof_closure.get("evidence_summary", {}).get(
            "certified_non_dynamic_rows"
        ),
        "proof_closure_open_dynamic_rows": proof_closure.get("evidence_summary", {}).get("open_dynamic_rows"),
        "proof_closure_open_dynamic_rows_scope": proof_closure.get("evidence_summary", {}).get(
            "open_dynamic_rows_scope"
        ),
        "proof_closure_active_direct_newton_euler_closed_rows": proof_closure.get("evidence_summary", {}).get(
            "active_direct_newton_euler_closed_rows"
        ),
        "proof_closure_active_direct_newton_euler_open_rows": proof_closure.get("evidence_summary", {}).get(
            "active_direct_newton_euler_open_rows"
        ),
        "proof_closure_active_direct_newton_euler_open_obligations": proof_closure.get("evidence_summary", {}).get(
            "active_direct_newton_euler_open_obligations"
        ),
        "proof_closure_newton_euler_open_obligations": proof_closure.get("evidence_summary", {}).get(
            "newton_euler_open_obligations"
        ),
        "proof_closure_newton_euler_open_obligations_scope": proof_closure.get("evidence_summary", {}).get(
            "newton_euler_open_obligations_scope"
        ),
        "proof_closure_symbolic_primitive_newton_euler_open_obligations": proof_closure.get(
            "evidence_summary", {}
        ).get("newton_euler_open_obligations"),
        "proof_closure_newton_euler_closed_obligations": proof_closure.get("evidence_summary", {}).get(
            "newton_euler_closed_obligations"
        ),
        "proof_closure_newton_euler_symbolic_target_rows": proof_closure.get("evidence_summary", {}).get(
            "newton_euler_symbolic_target_rows"
        ),
        "proof_closure_newton_euler_symbolic_target_translational_rows": proof_closure.get(
            "evidence_summary", {}
        ).get("newton_euler_symbolic_target_translational_rows"),
        "proof_closure_newton_euler_symbolic_target_rotational_rows": proof_closure.get(
            "evidence_summary", {}
        ).get("newton_euler_symbolic_target_rotational_rows"),
        "proof_closure_newton_euler_obligation_coverage_matrix_complete": proof_closure.get(
            "evidence_summary", {}
        ).get("newton_euler_obligation_coverage_matrix_complete"),
        "proof_closure_newton_euler_row_obligation_links": proof_closure.get("evidence_summary", {}).get(
            "newton_euler_row_obligation_links"
        ),
        "proof_closure_newton_euler_rows_with_complete_obligation_sets": proof_closure.get(
            "evidence_summary", {}
        ).get("newton_euler_rows_with_complete_obligation_sets"),
        "proof_closure_newton_euler_obligations_with_target_rows": proof_closure.get(
            "evidence_summary", {}
        ).get("newton_euler_obligations_with_target_rows"),
        "proof_closure_newton_euler_symbolic_target_inventory_complete": proof_closure.get(
            "oracle_state", {}
        ).get("newton_euler_symbolic_target_inventory_complete"),
        "proof_closure_residual_to_error_blocking_obligations": proof_closure.get("evidence_summary", {}).get(
            "residual_to_error_blocking_obligations"
        ),
        "proof_closure_formula_row_ad_jacobian_probe_count": proof_closure.get("evidence_summary", {}).get(
            "formula_row_ad_jacobian_probe_count"
        ),
        "proof_closure_direct_pc2_proof_gap_closed": proof_closure.get("closure_state", {}).get(
            "direct_pc2_proof_gap_closed",
            proof_closure.get("closure_state", {}).get("proof_gap_closed"),
        ),
        "proof_closure_proof_gap_closed": proof_closure.get("closure_state", {}).get("proof_gap_closed"),
        "proof_closure_proof_gap_closed_scope": proof_closure.get("closure_state", {}).get(
            "proof_gap_closed_scope", DIRECT_PC2_SCOPE
        ),
        "proof_closure_proof_gap_closed_reading_rule": DIRECT_PC2_READING_RULE,
        "proof_closure_dynamic_symbolic_oracle_complete": proof_closure.get("closure_state", {}).get(
            "dynamic_symbolic_oracle_complete"
        ),
        "proof_closure_stage_residual_O_h7_implementation_defect_proved": proof_closure.get(
            "closure_state", {}
        ).get("stage_residual_O_h7_implementation_defect_proved"),
        "proof_closure_eta_h_O_h7_solver_policy_evidence": proof_closure.get("closure_state", {}).get(
            "eta_h_O_h7_solver_policy_evidence"
        ),
        "proof_closure_theorem_statement_labels_present": proof_closure.get(
            "theorem_statement_boundary", {}
        ).get("all_required_labels_present_main_and_flat"),
        "proof_closure_theorem_statement_boundary_present": proof_closure.get(
            "theorem_statement_boundary", {}
        ).get("conditional_theorem_boundary_present_main_and_flat"),
        "proof_closure_theorem_statement_eta_condition_retained": proof_closure.get(
            "theorem_statement_boundary", {}
        ).get("eta_h_theorem_condition_retained"),
        "proof_closure_theorem_statement_eta_evidence_closed": proof_closure.get(
            "theorem_statement_boundary", {}
        ).get("eta_h_solver_policy_evidence_closed"),
        "proof_closure_theorem_statement_fixed_tolerance_asymptotic_proof": proof_closure.get(
            "theorem_statement_boundary", {}
        ).get("fixed_tolerance_runs_are_asymptotic_proof"),
        "proof_closure_theorem_statement_residual_to_error_not_promoted": proof_closure.get(
            "theorem_statement_boundary", {}
        ).get("does_not_promote_residual_to_error"),
        "proof_closure_theorem_statement_source_policy_or_full_tfe_not_promoted": proof_closure.get(
            "theorem_statement_boundary", {}
        ).get("does_not_promote_source_policy_or_full_tfe"),
        "proof_closure_manuscript_traceability_mapped": proof_closure.get(
            "manuscript_traceability", {}
        ).get("conditional_proof_claims_mapped_to_manuscript"),
        "proof_closure_manuscript_traceability_no_state_change": proof_closure.get(
            "manuscript_traceability", {}
        ).get("does_not_change_proof_closure_state"),
        "proof_closure_manuscript_traceability_dependency_graph_present": proof_closure.get(
            "manuscript_traceability", {}
        ).get("proof_dependency_graph_present_main_and_flat"),
        "proof_closure_manuscript_traceability_dynamic_matrix_present": proof_closure.get(
            "manuscript_traceability", {}
        ).get("dynamic_proof_closure_matrix_present_main_and_flat"),
        "proof_closure_manuscript_traceability_primitive_lane_boundary_present": proof_closure.get(
            "manuscript_traceability", {}
        ).get("primitive_lane_boundary_present_main_and_flat"),
        "proof_closure_manuscript_traceability_residual_nonpromotion_present": proof_closure.get(
            "manuscript_traceability", {}
        ).get("residual_to_error_nonpromotion_present_main_and_flat"),
        "proof_closure_submission_ready": proof_closure.get("submission_ready"),
        "proof_style_reference_checked": all(
            proof_style.get("reference_style_features", {}).get(key) is True
            for key in [
                "bliedf_section_present",
                "convergence_section_present",
                "taylor_local_error_lemma_present",
                "bch_perturbation_present",
                "coupled_error_recursion_present",
            ]
        ),
        "newton_euler_obligation_table_present": proof_style.get("manuscript_style_features", {}).get(
            "newton_euler_obligation_table_present"
        ),
        "newton_euler_obligation_count": len(proof_style.get("newton_euler_obligations", [])),
        "newton_euler_symbolic_target_audit_schema": newton_euler_symbolic_target.get("schema"),
        "newton_euler_symbolic_target_audit_status": newton_euler_symbolic_target.get("status"),
        "newton_euler_symbolic_target_rows": newton_euler_symbolic_target.get("row_count"),
        "newton_euler_symbolic_target_translational_rows": newton_euler_symbolic_target.get(
            "translational_row_count"
        ),
        "newton_euler_symbolic_target_rotational_rows": newton_euler_symbolic_target.get("rotational_row_count"),
        "newton_euler_symbolic_target_runtime_source_anchors_present": newton_euler_symbolic_target.get(
            "supporting_runtime_evidence", {}
        ).get("runtime_source_anchors_present"),
        "newton_euler_symbolic_target_runtime_source_anchor_path": newton_euler_symbolic_target.get(
            "supporting_runtime_evidence", {}
        )
        .get("runtime_source_anchors", {})
        .get("run_v047_path"),
        "newton_euler_symbolic_target_runtime_source_anchor_tuple_count": len(
            newton_euler_symbolic_target.get("supporting_runtime_evidence", {})
            .get("runtime_source_anchors", {})
            .get("component_tuple_anchors", [])
        ),
        "newton_euler_symbolic_target_runtime_source_anchor_dyn_extend_line": newton_euler_symbolic_target.get(
            "supporting_runtime_evidence", {}
        )
        .get("runtime_source_anchors", {})
        .get("primary_residual_dyn_extend", {})
        .get("line"),
        "newton_euler_symbolic_target_runtime_source_anchor_scope": newton_euler_symbolic_target.get(
            "supporting_runtime_evidence", {}
        )
        .get("runtime_source_anchors", {})
        .get("source_anchor_scope"),
        "newton_euler_symbolic_target_inventory_complete": newton_euler_symbolic_target.get(
            "closure_boundary", {}
        ).get("symbolic_target_inventory_complete"),
        "newton_euler_obligation_coverage_matrix_complete": newton_euler_symbolic_target.get(
            "obligation_coverage_matrix", {}
        ).get("coverage_matrix_complete"),
        "newton_euler_row_obligation_links": newton_euler_symbolic_target.get(
            "obligation_coverage_matrix", {}
        ).get("row_obligation_link_count"),
        "newton_euler_rows_with_complete_obligation_sets": newton_euler_symbolic_target.get(
            "obligation_coverage_matrix", {}
        ).get("rows_with_complete_obligation_sets"),
        "newton_euler_obligations_with_target_rows": newton_euler_symbolic_target.get(
            "obligation_coverage_matrix", {}
        ).get("obligations_with_target_rows"),
        "newton_euler_obligation_coverage_proof_closure_advanced": newton_euler_symbolic_target.get(
            "obligation_coverage_matrix", {}
        ).get("proof_closure_advanced"),
        "newton_euler_symbolic_defect_certificate_complete": newton_euler_symbolic_target.get(
            "closure_boundary", {}
        ).get("newton_euler_symbolic_defect_certificate_complete"),
        "newton_euler_symbolic_target_stage_residual_O_h7_implementation_defect_proved": (
            newton_euler_symbolic_target.get("closure_boundary", {}).get(
                "stage_residual_O_h7_implementation_defect_proved"
            )
        ),
        "newton_euler_symbolic_target_submission_ready": newton_euler_symbolic_target.get("submission_ready"),
        "proof_style_gap_narrowed": proof_style.get("proof_boundary", {}).get("proof_style_gap_narrowed"),
        "direct_pc2_proof_gap_closed": proof_style.get("proof_boundary", {}).get(
            "direct_pc2_proof_gap_closed",
            proof_style.get("proof_boundary", {}).get("proof_gap_closed"),
        ),
        "proof_gap_closed": proof_style.get("proof_boundary", {}).get("proof_gap_closed"),
        "proof_gap_closed_scope": proof_style.get("proof_boundary", {}).get(
            "proof_gap_closed_scope", DIRECT_PC2_SCOPE
        ),
        "proof_gap_closed_reading_rule": DIRECT_PC2_READING_RULE,
        "stage_residual_O_h7_implementation_defect_proved": result_pack.get("proof_status", {}).get(
            "stage_residual_O_h7_implementation_defect_proved"
        ),
        "dynamic_oracle_stage_residual_O_h7_symbolic_certificate_proved": result_pack.get(
            "proof_status", {}
        ).get("dynamic_oracle_stage_residual_O_h7_symbolic_certificate_proved"),
        "runtime_ad_oracle_complete": result_pack.get("proof_status", {}).get("runtime_ad_oracle_complete"),
        "dynamic_symbolic_oracle_complete": result_pack.get("proof_status", {}).get(
            "dynamic_symbolic_oracle_complete"
        ),
        "symbolic_oracle_complete": result_pack.get("proof_status", {}).get("symbolic_oracle_complete"),
        "scaled_tolerance_sweep_recorded": result_pack.get("proof_status", {}).get("scaled_tolerance_sweep_recorded"),
        "eta_h_O_h7_solver_policy_evidence": result_pack.get("proof_status", {}).get(
            "eta_h_O_h7_solver_policy_evidence"
        ),
        "solver_scale_submission_ready_scope": solver_scale_audit.get("submission_ready_scope"),
        "solver_scale_audit_scope": solver_scale_audit.get("readiness_boundary", {}).get(
            "solver_scale_audit_scope"
        ),
        "solver_scale_narrowed_claim_b4_b6_b7_statuses": solver_scale_audit.get(
            "readiness_boundary", {}
        ).get("narrowed_claim_b4_b6_b7_statuses"),
        "solver_scale_global_submission_boundaries_retained": solver_scale_audit.get(
            "readiness_boundary", {}
        ).get("global_submission_boundaries_retained"),
        "finite_scaled_tolerance_probe_recorded": solver_scale_audit.get("proof_boundary", {}).get(
            "finite_scaled_tolerance_probe_recorded"
        ),
        "finite_scaled_tolerance_probe_ok_rows": solver_scale_audit.get("finite_scaled_tolerance_probe", {}).get(
            "ok_row_count"
        ),
        "finite_scaled_tolerance_probe_total_rows": solver_scale_audit.get("finite_scaled_tolerance_probe", {}).get(
            "row_count"
        ),
        "finite_scaled_tolerance_probe_max_residual_over_h7": solver_scale_audit.get(
            "finite_scaled_tolerance_probe", {}
        ).get("max_final_residual_over_h7"),
        "finite_scaled_tolerance_probe_theorem_closed": solver_scale_audit.get(
            "finite_scaled_tolerance_probe", {}
        ).get("theorem_level_solver_proof_closed"),
        "finite_scaled_tolerance_trajectory_probe_recorded": solver_scale_audit.get("proof_boundary", {}).get(
            "finite_scaled_tolerance_trajectory_probe_recorded"
        ),
        "finite_scaled_tolerance_trajectory_probe_ok_rows": solver_scale_audit.get(
            "finite_scaled_tolerance_trajectory_probe", {}
        ).get("ok_row_count"),
        "finite_scaled_tolerance_trajectory_probe_total_rows": solver_scale_audit.get(
            "finite_scaled_tolerance_trajectory_probe", {}
        ).get("row_count"),
        "finite_scaled_tolerance_trajectory_probe_steps": solver_scale_audit.get(
            "finite_scaled_tolerance_trajectory_probe", {}
        ).get("total_steps_checked"),
        "finite_scaled_tolerance_trajectory_probe_max_residual_over_h7": solver_scale_audit.get(
            "finite_scaled_tolerance_trajectory_probe", {}
        ).get("max_final_residual_over_h7"),
        "finite_scaled_tolerance_trajectory_probe_theorem_closed": solver_scale_audit.get(
            "finite_scaled_tolerance_trajectory_probe", {}
        ).get("theorem_level_solver_proof_closed"),
        "finite_tolerance_regime_sweep_recorded": solver_scale_audit.get("proof_boundary", {}).get(
            "finite_tolerance_regime_sweep_recorded"
        ),
        "finite_h_scaled_tolerance_sweep_recorded": solver_scale_audit.get("proof_boundary", {}).get(
            "finite_h_scaled_tolerance_sweep_recorded"
        ),
        "finite_h_scaled_tolerance_sweep_policy_names": solver_scale_audit.get(
            "finite_tolerance_regime_sweep", {}
        ).get("finite_h_scaled_policy_names"),
        "finite_h_scaled_tolerance_sweep_rows": solver_scale_audit.get(
            "finite_tolerance_regime_sweep", {}
        ).get("finite_h_scaled_policy_rows"),
        "finite_h_scaled_tolerance_sweep_steps": solver_scale_audit.get(
            "finite_tolerance_regime_sweep", {}
        ).get("finite_h_scaled_policy_steps"),
        "finite_h_scaled_tolerance_sweep_velocity_order_floor": solver_scale_audit.get(
            "finite_tolerance_regime_sweep", {}
        ).get("finite_h_scaled_velocity_order_floor"),
        "finite_tolerance_regime_sweep_policy_count": solver_scale_audit.get(
            "finite_tolerance_regime_sweep", {}
        ).get("policy_count"),
        "finite_tolerance_regime_sweep_total_rows": solver_scale_audit.get(
            "finite_tolerance_regime_sweep", {}
        ).get("total_rows_checked"),
        "finite_tolerance_regime_sweep_total_steps": solver_scale_audit.get(
            "finite_tolerance_regime_sweep", {}
        ).get("total_steps_checked"),
        "finite_tolerance_regime_sweep_theorem_closed": solver_scale_audit.get(
            "finite_tolerance_regime_sweep", {}
        ).get("theorem_level_solver_proof_closed"),
    }
    tfe_candidate_source_boundary = tfe_source_policy_spec.get("candidate_vs_source_policy_boundary", {})
    tfe_row_candidate_source_boundary = tfe_source_policy_audit.get("candidate_vs_source_policy_boundary", {})
    tfe_dae_candidate_source_boundary = tfe_dae_runner_contract_gap_audit.get(
        "candidate_vs_source_policy_boundary", {}
    )
    tfe_attempt_candidate_source_boundary = tfe_self_reproduction_attempt_certificate.get(
        "candidate_vs_source_policy_boundary", {}
    )
    tfe_candidate_source_boundary_sources = [
        "TFE_SOURCE_POLICY_SPEC.json",
        "TFE_SOURCE_POLICY_ROW_AUDIT.json",
        "TFE_DAE_RUNNER_CONTRACT_GAP_AUDIT.json",
        "TFE_SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_CERTIFICATE.json",
    ]
    tfe_candidate_source_boundary_sources_match = (
        tfe_candidate_source_boundary
        == tfe_row_candidate_source_boundary
        == tfe_dae_candidate_source_boundary
        == tfe_attempt_candidate_source_boundary
    )
    tfe_source_policy_execution_preflight = tfe_dae_runner_contract_gap_audit.get(
        "source_policy_execution_preflight", {}
    )
    tfe_self_reproduction_execution_preflight = (
        tfe_self_reproduction_attempt_certificate.get("source_policy_execution_preflight", {})
    )
    tfe_self_reproduction_required_next_actions = (
        tfe_self_reproduction_attempt_certificate.get("required_next_actions", [])
    )
    source_policy_row_ledger_current_disposition_counts = Counter(
        str(row.get("display_action") or row.get("action_class"))
        for row in source_policy_row_ledger.get("rows", [])
        if isinstance(row, dict)
    )
    external_checks = {
        "external_baseline_status": external_gate.get("status"),
        "same_test_campaign_status": blocker.get("same_test_boundary", {}).get("same_test_campaign_status"),
        "external_superiority_claim": blocker.get("same_test_boundary", {}).get("external_superiority_claim"),
        "accepted_external_dynamic_order_examples_count": blocker.get("external_same_test_acceptance_sheet", {}).get(
            "accepted_external_dynamic_order_examples_count"
        ),
        "source_policy_diagnosis_schema": source_policy_diagnosis.get("schema"),
        "source_policy_diagnosis_status": source_policy_diagnosis.get("status"),
        "source_policy_diagnosis_flagged_rows": source_policy_diagnosis.get("coverage", {}).get("flagged_row_count"),
        "source_policy_position_aligned_velocity_mismatch_rows": source_policy_diagnosis.get("coverage", {}).get(
            "position_aligned_velocity_mismatch_count"
        ),
        "source_policy_recheck_required": source_policy_diagnosis.get("source_policy_recheck_required"),
        "source_policy_diagnosis_external_superiority_allowed": source_policy_diagnosis.get(
            "external_superiority_allowed"
        ),
        "source_policy_diagnosis_b2_b4_status": source_policy_diagnosis.get("claim_boundary", {}).get(
            "b2_b4_status"
        ),
        "source_policy_triage_schema": source_policy_triage.get("schema"),
        "source_policy_triage_status": source_policy_triage.get("status"),
        "source_policy_triage_flagged_rows": source_policy_triage.get("triage_scope", {}).get("flagged_row_count"),
        "source_policy_triage_flagged_examples": source_policy_triage.get("triage_scope", {}).get(
            "flagged_examples"
        ),
        "source_policy_triage_action_counts": source_policy_triage.get("triage_scope", {}).get("action_counts"),
        "source_policy_triage_b2_can_close_now": source_policy_triage.get("closure_boundary", {}).get(
            "b2_can_close_now"
        ),
        "source_policy_triage_b4_can_close_now": source_policy_triage.get("closure_boundary", {}).get(
            "b4_can_close_now"
        ),
        "source_policy_triage_heavy_run_invoked": source_policy_triage.get("closure_boundary", {}).get(
            "heavy_numerical_run_invoked"
        ),
        "source_policy_row_ledger_schema": source_policy_row_ledger.get("schema"),
        "source_policy_row_ledger_status": source_policy_row_ledger.get("status"),
        "source_policy_row_ledger_flagged_rows": source_policy_row_ledger.get("coverage", {}).get(
            "flagged_row_count"
        ),
        "source_policy_row_ledger_flagged_examples": source_policy_row_ledger.get("coverage", {}).get(
            "flagged_examples"
        ),
        "source_policy_row_ledger_action_counts": source_policy_row_ledger.get("coverage", {}).get("action_counts"),
        "source_policy_row_ledger_current_disposition_counts": dict(
            sorted(source_policy_row_ledger_current_disposition_counts.items())
        ),
        "source_policy_row_ledger_attempted_not_reproducible_rows": (
            source_policy_row_ledger_current_disposition_counts.get("attempted_not_reproducible_not_promoted", 0)
        ),
        "source_policy_public_code_refresh_status": source_policy_public_code_refresh.get("status"),
        "source_policy_public_code_refresh_date": source_policy_public_code_refresh.get("date_checked"),
        "source_policy_public_code_refresh_rows": source_policy_public_code_refresh.get("row_count"),
        "source_policy_public_code_refresh_public_code_available_rows": source_policy_public_code_refresh.get(
            "public_code_available_rows"
        ),
        "source_policy_public_code_refresh_self_reproduction_attempted_rows": source_policy_public_code_refresh.get(
            "self_reproduction_attempted_rows"
        ),
        "source_policy_public_code_refresh_unable_to_reproduce_rows": source_policy_public_code_refresh.get(
            "unable_to_reproduce_rows"
        ),
        "source_policy_public_code_refresh_source_policy_rows_closed": source_policy_public_code_refresh.get(
            "source_policy_rows_closed"
        ),
        "source_policy_public_code_refresh_latest_status": source_policy_public_code_refresh_latest.get("status"),
        "source_policy_public_code_refresh_latest_date": source_policy_public_code_refresh_latest.get("date_checked"),
        "source_policy_public_code_refresh_latest_rows": source_policy_public_code_refresh_latest.get("row_count"),
        "source_policy_public_code_refresh_latest_current_queries": source_policy_public_code_refresh_latest.get(
            "current_query_count"
        ),
        "source_policy_public_code_refresh_latest_positive_artifact_rows": (
            source_policy_public_code_refresh_latest.get("positive_public_code_artifact_rows")
        ),
        "source_policy_public_code_refresh_latest_source_policy_rows_closed": (
            source_policy_public_code_refresh_latest.get("source_policy_rows_closed")
        ),
        "source_policy_public_code_refresh_latest_source_policy_rows_promoted": (
            source_policy_public_code_refresh_latest.get("source_policy_rows_promoted")
        ),
        "source_policy_row_ledger_rows_closed": source_policy_row_ledger.get("coverage", {}).get(
            "rows_source_policy_closed"
        ),
        "source_policy_row_ledger_rows_external_superiority_ready": source_policy_row_ledger.get(
            "coverage", {}
        ).get("rows_external_superiority_ready"),
        "source_policy_row_ledger_parallel_ready_shards": source_policy_row_ledger.get(
            "execution_policy", {}
        ).get("parallel_ready_shards_without_default_1e_4"),
        "source_policy_row_ledger_default_1e_4_required": source_policy_row_ledger.get(
            "execution_policy", {}
        ).get("default_1e_4_required"),
        "source_policy_row_ledger_heavy_run_invoked": source_policy_row_ledger.get(
            "execution_policy", {}
        ).get("heavy_numerical_run_invoked"),
        "source_policy_row_ledger_b2_can_close_now": source_policy_row_ledger.get("closure_rule", {}).get(
            "b2_can_close_now"
        ),
        "source_policy_row_ledger_b4_can_close_now": source_policy_row_ledger.get("closure_rule", {}).get(
            "b4_can_close_now"
        ),
        "all_examples_source_policy_schema": all_examples_source_policy.get("schema"),
        "all_examples_source_policy_status": all_examples_source_policy.get("status"),
        "all_examples_source_policy_flagged_rows": all_examples_source_policy.get("coverage", {}).get(
            "flagged_row_count"
        ),
        "all_examples_source_policy_flagged_raw_rows": all_examples_source_policy.get("coverage", {}).get(
            "flagged_raw_row_count"
        ),
        "all_examples_source_policy_flagged_examples": all_examples_source_policy.get("coverage", {}).get(
            "flagged_examples"
        ),
        "all_examples_source_policy_all_four_examples": all_examples_source_policy.get("coverage", {}).get(
            "all_four_examples_covered"
        ),
        "all_examples_source_policy_all_three_step_sizes": all_examples_source_policy.get("coverage", {}).get(
            "all_flagged_rows_have_three_step_sizes"
        ),
        "all_examples_source_policy_flagged_by_suite": all_examples_source_policy.get("coverage", {}).get(
            "flagged_by_suite"
        ),
        "all_examples_source_policy_position_velocity_mismatch_rows": all_examples_source_policy.get(
            "coverage", {}
        ).get("diagnostic_category_counts", {}).get("position_aligned_velocity_mismatch"),
        "all_examples_source_policy_rows_closed": all_examples_source_policy.get("closure_boundary", {}).get(
            "all_source_policy_rows_closed"
        ),
        "all_examples_source_policy_b2_can_close_now": all_examples_source_policy.get("closure_boundary", {}).get(
            "b2_can_close_now"
        ),
        "all_examples_source_policy_b4_can_close_now": all_examples_source_policy.get("closure_boundary", {}).get(
            "b4_can_close_now"
        ),
        "all_examples_source_policy_heavy_run_invoked": all_examples_source_policy.get("execution_policy", {}).get(
            "heavy_numerical_run_invoked"
        ),
        "all_examples_source_policy_default_1e_4_required": all_examples_source_policy.get(
            "execution_policy", {}
        ).get("default_1e_4_required"),
        "suite_disposition_schema": suite_disposition.get("schema"),
        "suite_disposition_status": suite_disposition.get("status"),
        "suite_disposition_suite_count": suite_disposition.get("suite_count"),
        "suite_disposition_accepted_external_superiority_suite_count": suite_disposition.get(
            "accepted_external_superiority_suite_count"
        ),
        "suite_disposition_parallel_ready_shards_without_default_1e_4": suite_disposition.get(
            "closure_counts", {}
        ).get("parallel_ready_shards_without_default_1e_4"),
        "suite_disposition_b2_can_close_now": suite_disposition.get("b2_b4_closure", {}).get("b2_can_close_now"),
        "suite_disposition_b4_can_close_now": suite_disposition.get("b2_b4_closure", {}).get("b4_can_close_now"),
        "suite_disposition_external_superiority_allowed": suite_disposition.get("claim_boundary", {}).get(
            "external_superiority_allowed"
        ),
        "source_policy_closure_manifest_schema": source_policy_closure_manifest.get("schema"),
        "source_policy_closure_manifest_status": source_policy_closure_manifest.get("status"),
        "source_policy_closure_performance_completed_rows": source_policy_closure_manifest.get(
            "performance_matrix", {}
        ).get("completed_row_count"),
        "source_policy_closure_performance_total_rows": source_policy_closure_manifest.get(
            "performance_matrix", {}
        ).get("row_count"),
        "source_policy_closure_performance_not_complete_rows": source_policy_closure_manifest.get(
            "performance_matrix", {}
        ).get("not_complete_row_count"),
        "source_policy_closure_strict_external_error_rows": source_policy_closure_manifest.get(
            "common_reference_boundary", {}
        ).get("strict_external_error_claim_allowed_rows"),
        "source_policy_closure_parallel_ready_shards": source_policy_closure_manifest.get(
            "parallel_ready_shards_without_default_1e_4"
        ),
        "source_policy_closure_b2_can_close_now": source_policy_closure_manifest.get("b2_can_close_now"),
        "source_policy_closure_b4_can_close_now": source_policy_closure_manifest.get("b4_can_close_now"),
        "source_policy_closure_external_superiority_allowed": source_policy_closure_manifest.get(
            "external_superiority_claim_allowed"
        ),
        "source_policy_closure_runnable_parallel_suites": source_policy_closure_manifest.get(
            "runnable_parallel_suites"
        ),
        "source_policy_closure_not_ready_or_demote_suites": source_policy_closure_manifest.get(
            "not_ready_or_demote_suites"
        ),
        "external_case_reconciliation_schema": external_case_reconciliation.get("schema"),
        "external_case_reconciliation_status": external_case_reconciliation.get("status"),
        "external_case_reconciliation_case_status_counts": external_case_reconciliation.get(
            "case_inventory_status_counts"
        ),
        "external_case_reconciliation_bounded_suites": external_case_reconciliation.get(
            "bounded_or_public_evidence_suites"
        ),
        "external_case_reconciliation_not_ready_suites": external_case_reconciliation.get(
            "not_ready_or_demote_suites"
        ),
        "external_case_reconciliation_case_not_run_not_zero_evidence": external_case_reconciliation.get(
            "interpretation", {}
        ).get("case_inventory_not_run_is_not_zero_evidence"),
        "external_case_reconciliation_ra2021_baseline_groups": external_case_reconciliation.get(
            "source_policy_progress", {}
        ).get("ra2021_public_baselines", {}).get("order_groups_completed"),
        "external_case_reconciliation_ra2021_baseline_required_groups": external_case_reconciliation.get(
            "source_policy_progress", {}
        ).get("ra2021_public_baselines", {}).get("order_groups_required"),
        "external_case_reconciliation_ra2021_timing_rows": external_case_reconciliation.get(
            "source_policy_progress", {}
        ).get("ra2021_public_baselines", {}).get("timing_rows_completed"),
        "external_case_reconciliation_ra2021_timing_required_rows": external_case_reconciliation.get(
            "source_policy_progress", {}
        ).get("ra2021_public_baselines", {}).get("timing_rows_required"),
        "external_case_reconciliation_local_dynamic_order_examples": external_case_reconciliation.get(
            "source_policy_progress", {}
        ).get("ra2021_local_gauss6_rows", {}).get("accepted_external_dynamic_order_count"),
        "external_case_reconciliation_gauss_double_public_policy": external_case_reconciliation.get(
            "source_policy_progress", {}
        ).get("ra2021_local_gauss6_rows", {}).get("double_public_policy_rows_completed"),
        "external_case_reconciliation_closed_loop_row_kind": external_case_reconciliation.get(
            "source_policy_progress", {}
        ).get("ra2021_local_gauss6_rows", {}).get("closed_loop_row_kind"),
        "external_case_reconciliation_rows_closed": external_case_reconciliation.get(
            "source_policy_row_ledger", {}
        ).get("rows_source_policy_closed"),
        "external_case_reconciliation_rows_external_superiority_ready": external_case_reconciliation.get(
            "source_policy_row_ledger", {}
        ).get("rows_external_superiority_ready"),
        "external_case_reconciliation_accepted_external_dynamic_order_examples": external_case_reconciliation.get(
            "acceptance_boundary", {}
        ).get("accepted_external_dynamic_order_examples_count"),
        "external_case_reconciliation_b2_can_close_now": external_case_reconciliation.get(
            "acceptance_boundary", {}
        ).get("b2_can_close_now"),
        "external_case_reconciliation_b4_can_close_now": external_case_reconciliation.get(
            "acceptance_boundary", {}
        ).get("b4_can_close_now"),
        "external_case_reconciliation_default_1e_4_required": external_case_reconciliation.get(
            "execution_policy", {}
        ).get("default_1e_4_required"),
        "external_case_reconciliation_heavy_run_invoked": external_case_reconciliation.get(
            "execution_policy", {}
        ).get("heavy_numerical_run_invoked"),
        "hi2022_policy_decision_schema": hi2022_policy_decision.get("schema"),
        "hi2022_policy_decision_status": hi2022_policy_decision.get("status"),
        "hi2022_bounded_row_count": hi2022_policy_decision.get("existing_bounded_evidence", {}).get(
            "row_count"
        ),
        "hi2022_bounded_ok_row_count": hi2022_policy_decision.get("existing_bounded_evidence", {}).get(
            "ok_row_count"
        ),
        "hi2022_bounded_group_count": hi2022_policy_decision.get("existing_bounded_evidence", {}).get(
            "group_count"
        ),
        "hi2022_bounded_groups_with_three_step_sizes": hi2022_policy_decision.get(
            "existing_bounded_evidence", {}
        ).get("groups_with_three_step_sizes"),
        "hi2022_bounded_t_end_values": hi2022_policy_decision.get("existing_bounded_evidence", {}).get(
            "t_end_values"
        ),
        "hi2022_bounded_step_sizes": hi2022_policy_decision.get("existing_bounded_evidence", {}).get(
            "step_sizes"
        ),
        "hi2022_full_T8_policy_required": hi2022_policy_decision.get(
            "source_policy_required_before_external_superiority", {}
        ).get("full_T8_policy_required"),
        "hi2022_full_T8_policy_completed": hi2022_policy_decision.get(
            "source_policy_required_before_external_superiority", {}
        ).get("full_T8_policy_completed"),
        "hi2022_accepted_for_bounded_evidence": hi2022_policy_decision.get(
            "source_policy_required_before_external_superiority", {}
        ).get("accepted_for_bounded_evidence"),
        "hi2022_accepted_for_external_superiority": hi2022_policy_decision.get(
            "source_policy_required_before_external_superiority", {}
        ).get("accepted_for_external_superiority"),
        "hi2022_accepted_source_policy_dynamic_order_examples": hi2022_policy_decision.get(
            "source_policy_required_before_external_superiority", {}
        ).get("accepted_source_policy_dynamic_order_examples_count"),
        "hi2022_queue_parallel_shard_count": hi2022_policy_decision.get("queue_policy_decision", {}).get(
            "parallel_shard_count"
        ),
        "hi2022_decision": hi2022_policy_decision.get("decision"),
        "hi2022_default_1e_4_required": hi2022_policy_decision.get("execution_policy", {}).get(
            "default_1e_4_required"
        ),
        "hi2022_heavy_run_invoked": hi2022_policy_decision.get("execution_policy", {}).get(
            "heavy_numerical_run_invoked"
        ),
        "hi2022_run_v047_invoked": hi2022_policy_decision.get("execution_policy", {}).get("run_v047_invoked"),
        "hi2022_source_policy_audit_schema": hi2022_source_policy_audit.get("schema"),
        "hi2022_source_policy_audit_status": hi2022_source_policy_audit.get("status"),
        "hi2022_source_policy_active_b2_flagged_rows": hi2022_source_policy_audit.get("active_b2_flagged_rows"),
        "hi2022_source_policy_bounded_row_count": hi2022_source_policy_audit.get("bounded_row_count"),
        "hi2022_source_policy_bounded_ok_row_count": hi2022_source_policy_audit.get("bounded_ok_row_count"),
        "hi2022_source_policy_bounded_group_count": hi2022_source_policy_audit.get("bounded_group_count"),
        "hi2022_source_policy_bounded_groups_with_three_step_sizes": hi2022_source_policy_audit.get(
            "bounded_groups_with_three_step_sizes"
        ),
        "hi2022_source_policy_t8_coarse_rows": hi2022_source_policy_audit.get(
            "t8_coarse_horizon_evidence", {}
        ).get("row_count"),
        "hi2022_source_policy_t8_coarse_ok_rows": hi2022_source_policy_audit.get(
            "t8_coarse_horizon_evidence", {}
        ).get("ok_row_count"),
        "hi2022_source_policy_t8_coarse_complete_groups": hi2022_source_policy_audit.get(
            "t8_coarse_horizon_evidence", {}
        ).get("complete_form_model_groups"),
        "hi2022_source_policy_t8_coarse_group_count": hi2022_source_policy_audit.get(
            "t8_coarse_horizon_evidence", {}
        ).get("group_count"),
        "hi2022_source_policy_t8_coarse_source_policy_reproduction": hi2022_source_policy_audit.get(
            "t8_coarse_horizon_evidence", {}
        ).get("source_policy_reproduction"),
        "hi2022_source_policy_t8_coarse_v048_runner_invoked": hi2022_source_policy_audit.get(
            "t8_coarse_horizon_evidence", {}
        ).get("v048_runner_invoked_for_this_evidence"),
        "hi2022_t8_tolerance_repair_schema": hi2022_t8_tolerance_repair_audit.get("schema"),
        "hi2022_t8_tolerance_repair_status": hi2022_t8_tolerance_repair_audit.get("status"),
        "hi2022_t8_tolerance_repair_rows": hi2022_t8_tolerance_repair_audit.get(
            "repair_attempt", {}
        ).get("row_count"),
        "hi2022_t8_tolerance_repair_ok_rows": hi2022_t8_tolerance_repair_audit.get(
            "repair_attempt", {}
        ).get("ok_row_count"),
        "hi2022_t8_tolerance_repair_complete_groups": hi2022_t8_tolerance_repair_audit.get(
            "repair_attempt", {}
        ).get("complete_form_model_groups"),
        "hi2022_t8_tolerance_repair_group_count": hi2022_t8_tolerance_repair_audit.get(
            "repair_attempt", {}
        ).get("group_count"),
        "hi2022_t8_tolerance_repair_latest_rows": hi2022_t8_tolerance_repair_audit.get(
            "latest_repair_attempt", {}
        ).get("row_count"),
        "hi2022_t8_tolerance_repair_latest_ok_rows": hi2022_t8_tolerance_repair_audit.get(
            "latest_repair_attempt", {}
        ).get("ok_row_count"),
        "hi2022_t8_tolerance_repair_latest_complete_groups": hi2022_t8_tolerance_repair_audit.get(
            "latest_repair_attempt", {}
        ).get("complete_form_model_groups"),
        "hi2022_t8_tolerance_repair_latest_group_count": hi2022_t8_tolerance_repair_audit.get(
            "latest_repair_attempt", {}
        ).get("group_count"),
        "hi2022_t8_tolerance_repair_combined_best_rows": hi2022_t8_tolerance_repair_audit.get(
            "combined_best", {}
        ).get("row_count"),
        "hi2022_t8_tolerance_repair_combined_best_ok_rows": hi2022_t8_tolerance_repair_audit.get(
            "combined_best", {}
        ).get("ok_row_count"),
        "hi2022_t8_tolerance_repair_combined_best_complete_groups": hi2022_t8_tolerance_repair_audit.get(
            "combined_best", {}
        ).get("complete_form_model_groups"),
        "hi2022_t8_tolerance_repair_combined_best_group_count": hi2022_t8_tolerance_repair_audit.get(
            "combined_best", {}
        ).get("group_count"),
        "hi2022_t8_tolerance_repair_recovered_rows": hi2022_t8_tolerance_repair_audit.get(
            "combined_best", {}
        ).get("recovered_row_count"),
        "hi2022_t8_tolerance_repair_source_policy_closed": hi2022_t8_tolerance_repair_audit.get(
            "claim_boundary", {}
        ).get("source_policy_reproduction_closed"),
        "hi2022_t8_tolerance_repair_external_superiority_allowed": hi2022_t8_tolerance_repair_audit.get(
            "claim_boundary", {}
        ).get("external_superiority_claim_allowed"),
        "hi2022_ra_half_double_repair_attempt_status": hi2022_ra_half_double_repair_attempt_certificate.get(
            "status"
        ),
        "hi2022_ra_half_double_repair_target_ok_rows": hi2022_ra_half_double_repair_attempt_certificate.get(
            "tolerance_repair_evidence", {}
        ).get("combined_target_group", {}).get("ok_row_count"),
        "hi2022_ra_half_double_repair_target_failed_rows": hi2022_ra_half_double_repair_attempt_certificate.get(
            "tolerance_repair_evidence", {}
        ).get("combined_target_group", {}).get("failed_row_count"),
        "hi2022_ra_half_double_repair_combined_ok_rows": hi2022_ra_half_double_repair_attempt_certificate.get(
            "tolerance_repair_evidence", {}
        ).get("combined_best_ok_rows"),
        "hi2022_ra_half_double_repair_combined_row_count": hi2022_ra_half_double_repair_attempt_certificate.get(
            "tolerance_repair_evidence", {}
        ).get("combined_best_row_count"),
        "hi2022_ra_half_double_repair_combined_complete_groups": hi2022_ra_half_double_repair_attempt_certificate.get(
            "tolerance_repair_evidence", {}
        ).get("combined_best_complete_groups"),
        "hi2022_ra_half_double_repair_combined_group_count": hi2022_ra_half_double_repair_attempt_certificate.get(
            "tolerance_repair_evidence", {}
        ).get("combined_best_group_count"),
        "hi2022_ra_half_double_repair_source_policy_closed": hi2022_ra_half_double_repair_attempt_certificate.get(
            "source_policy_closed"
        ),
        "hi2022_ra_half_double_repair_rows_promoted": hi2022_ra_half_double_repair_attempt_certificate.get(
            "source_policy_rows_promoted"
        ),
        "hi2022_source_policy_reproduction_rows": hi2022_source_policy_audit.get("source_policy_closed_rows"),
        "hi2022_source_policy_external_superiority_ready_rows": hi2022_source_policy_audit.get(
            "external_superiority_ready_rows"
        ),
        "hi2022_source_policy_can_close_b2_requirement_now": hi2022_source_policy_audit.get("decision", {}).get(
            "can_close_hi2022_b2_requirement_now"
        ),
        "hi2022_source_policy_default_1e_4_required": hi2022_source_policy_audit.get("execution_policy", {}).get(
            "default_1e_4_required"
        ),
        "hi2022_source_policy_heavy_run_invoked": hi2022_source_policy_audit.get("execution_policy", {}).get(
            "heavy_numerical_run_invoked"
        ),
        "hi2022_source_policy_run_v047_invoked": hi2022_source_policy_audit.get("execution_policy", {}).get(
            "run_v047_invoked"
        ),
        "vp2024_disposition_schema": vp2024_disposition.get("schema"),
        "vp2024_disposition_status": vp2024_disposition.get("status"),
        "vp2024_examples_checked": vp2024_disposition.get("coverage", {}).get("examples_checked"),
        "vp2024_all_four_examples_checked": vp2024_disposition.get("coverage", {}).get(
            "all_four_examples_checked"
        ),
        "vp2024_source_policy_rows": vp2024_disposition.get("coverage", {}).get("source_policy_rows"),
        "vp2024_source_policy_code_path_unresolved_rows": vp2024_disposition.get("coverage", {}).get(
            "source_policy_code_path_unresolved_rows"
        ),
        "vp2024_source_policy_rows_attempted_not_reproducible": vp2024_disposition.get("coverage", {}).get(
            "source_policy_rows_attempted_not_reproducible"
        ),
        "vp2024_unable_to_reproduce_rows": vp2024_disposition.get("coverage", {}).get(
            "unable_to_reproduce_rows"
        ),
        "vp2024_common_reference_proxy_rows": vp2024_disposition.get("coverage", {}).get(
            "common_reference_proxy_rows"
        ),
        "vp2024_common_reference_local_order_wins": vp2024_disposition.get("coverage", {}).get(
            "common_reference_local_velocity_order_wins"
        ),
        "vp2024_common_reference_local_error_wins": vp2024_disposition.get("coverage", {}).get(
            "common_reference_local_finest_velocity_error_wins"
        ),
        "vp2024_large_step_local_order_wins": vp2024_disposition.get("coverage", {}).get(
            "large_step_diagnostic_local_velocity_order_wins"
        ),
        "vp2024_large_step_local_error_wins": vp2024_disposition.get("coverage", {}).get(
            "large_step_diagnostic_local_finest_velocity_error_wins"
        ),
        "vp2024_large_step_noncontrolling": vp2024_disposition.get("large_step_diagnostic_boundary", {}).get(
            "noncontrolling_mixed_reference_policy"
        ),
        "vp2024_distinct_public_code_path_found": vp2024_disposition.get(
            "source_code_path_disposition", {}
        ).get("distinct_public_vp_code_path_found"),
        "vp2024_final_nonpublic_code_disposition": vp2024_disposition.get(
            "source_code_path_disposition", {}
        ).get("final_nonpublic_code_disposition"),
        "vp2024_public_code_recheck_status": vp2024_public_code_recheck.get("status"),
        "vp2024_public_code_recheck_date": vp2024_public_code_recheck.get("date_checked"),
        "vp2024_public_code_recheck_tree_truncated": vp2024_public_code_recheck.get("coverage", {}).get(
            "tree_truncated"
        ),
        "vp2024_public_code_recheck_tree_total_paths": vp2024_public_code_recheck.get("coverage", {}).get(
            "tree_total_paths"
        ),
        "vp2024_public_code_recheck_year2024_paths": vp2024_public_code_recheck.get("coverage", {}).get(
            "year2024_path_count"
        ),
        "vp2024_public_code_recheck_keyword_hits": vp2024_public_code_recheck.get("coverage", {}).get(
            "keyword_path_hit_count"
        ),
        "vp2024_public_code_recheck_attempted_not_reproducible_rows": vp2024_public_code_recheck.get(
            "coverage", {}
        ).get("source_policy_rows_attempted_not_reproducible"),
        "vp2024_public_code_recheck_source_policy_rows_closed": vp2024_public_code_recheck.get(
            "coverage", {}
        ).get("source_policy_rows_closed"),
        "vp2024_public_code_recheck_external_superiority_allowed": vp2024_public_code_recheck.get(
            "claim_boundary", {}
        ).get("external_superiority_claim_allowed"),
        "vp2024_proxy_is_source_policy_reproduction": vp2024_disposition.get(
            "source_code_path_disposition", {}
        ).get("coordinate_partitioning_proxy_is_source_policy_reproduction"),
        "vp2024_claim_allowed_now": vp2024_disposition.get("source_code_path_disposition", {}).get(
            "claim_allowed_now"
        ),
        "vp2024_default_1e_4_required": vp2024_disposition.get("execution_policy", {}).get(
            "default_1e_4_required"
        ),
        "vp2024_heavy_run_invoked": vp2024_disposition.get("execution_policy", {}).get(
            "heavy_numerical_run_invoked"
        ),
        "vp2024_run_v047_invoked": vp2024_disposition.get("execution_policy", {}).get("run_v047_invoked"),
        "vp2024_local_sbel_top_level_directories": vp2024_disposition.get("local_repository_tree_scan", {}).get(
            "local_sbel_top_level_directories"
        ),
        "vp2024_local_sbel_year_2024_directory_present": vp2024_disposition.get(
            "local_repository_tree_scan", {}
        ).get("local_sbel_year_2024_directory_present"),
        "vp2024_local_visible_mbd_code_roots": vp2024_disposition.get("local_repository_tree_scan", {}).get(
            "local_sbel_visible_mbd_code_roots"
        ),
        "vp2024_local_velocity_partition_term_hit_count": vp2024_disposition.get(
            "local_repository_tree_scan", {}
        ).get("local_sbel_velocity_partition_term_hit_count"),
        "vp2024_local_distinct_vp2024_code_path_found": vp2024_disposition.get(
            "local_repository_tree_scan", {}
        ).get("local_sbel_distinct_vp2024_code_path_found"),
        "vp2024_local_public_metadata_visible_non_git_file_count": vp2024_disposition.get(
            "local_repository_tree_scan", {}
        ).get("local_public_metadata_visible_non_git_file_count"),
        "external_suite_demotion_schema": external_suite_demotion.get("schema"),
        "external_suite_demotion_status": external_suite_demotion.get("status"),
        "external_suite_demotion_demoted_suite_count": external_suite_demotion.get("demoted_suite_count"),
        "external_suite_demotion_b2_closed_subrequirements": external_suite_demotion.get(
            "b2_subrequirements_closed_by_demotion"
        ),
        "external_suite_demotion_b2_remaining_required": external_suite_demotion.get(
            "b2_required_to_close_after_demotions"
        ),
        "external_suite_demotion_vp2024_demoted_rows": external_suite_demotion.get(
            "vp2024_demoted_source_policy_rows"
        ),
        "external_suite_demotion_vp2024_demoted_flagged_rows": external_suite_demotion.get(
            "vp2024_demoted_source_policy_flagged_rows"
        ),
        "external_suite_demotion_hi2022_demoted_rows": external_suite_demotion.get(
            "hi2022_demoted_source_policy_rows"
        ),
        "external_suite_demotion_hi2022_demoted_flagged_rows": external_suite_demotion.get(
            "hi2022_demoted_source_policy_flagged_rows"
        ),
        "external_suite_demotion_active_flagged_rows": external_suite_demotion.get(
            "active_source_policy_flagged_rows_after_demotions"
        ),
        "external_suite_demotion_remaining_open_suites": external_suite_demotion.get("remaining_open_suites"),
        "external_suite_demotion_external_superiority_allowed": external_suite_demotion.get(
            "external_superiority_claim_allowed"
        ),
        "external_suite_demotion_default_1e_4_required": external_suite_demotion.get("execution_policy", {}).get(
            "default_1e_4_required"
        ),
        "external_suite_demotion_heavy_run_invoked": external_suite_demotion.get("execution_policy", {}).get(
            "heavy_numerical_run_invoked"
        ),
        "external_suite_demotion_run_v047_invoked": external_suite_demotion.get("execution_policy", {}).get(
            "run_v047_invoked"
        ),
        "b2_remaining_work_schema": b2_remaining_work.get("schema"),
        "b2_remaining_work_status": b2_remaining_work.get("status"),
        "b2_remaining_work_row_count": b2_remaining_work.get("row_count"),
        "b2_remaining_work_active_flagged_rows": b2_remaining_work.get("active_flagged_row_count"),
        "b2_remaining_work_demoted_flagged_rows": b2_remaining_work.get("demoted_flagged_row_count"),
        "b2_remaining_work_source_policy_closed_rows": b2_remaining_work.get("source_policy_closed_rows"),
        "b2_remaining_work_external_superiority_ready_rows": b2_remaining_work.get(
            "external_superiority_ready_rows"
        ),
        "b2_remaining_work_active_suite_counts": b2_remaining_work.get("active_suite_counts"),
        "b2_remaining_work_demoted_suite_counts": b2_remaining_work.get("demoted_suite_counts"),
        "b2_remaining_work_closed_by_demotion": b2_remaining_work.get("b2_closed_by_demotion"),
        "b2_remaining_work_remaining_requirements": b2_remaining_work.get("b2_remaining_requirements"),
        "b2_remaining_work_default_1e_4_required": b2_remaining_work.get("execution_policy", {}).get(
            "default_1e_4_required"
        ),
        "b2_remaining_work_heavy_run_invoked": b2_remaining_work.get("execution_policy", {}).get(
            "heavy_numerical_run_invoked"
        ),
        "b2_remaining_work_run_v047_invoked": b2_remaining_work.get("execution_policy", {}).get(
            "run_v047_invoked"
        ),
        "b2_closure_execution_plan_schema": b2_remaining_work.get("closure_execution_plan", {}).get("schema"),
        "b2_closure_execution_plan_all_active_suites_ready": b2_remaining_work.get(
            "closure_execution_plan", {}
        ).get("all_active_suites_ready_to_launch"),
        "b2_closure_execution_plan_explicit_1e_4_opt_in": b2_remaining_work.get(
            "closure_execution_plan", {}
        ).get("source_policy_1e_4_requires_explicit_flag"),
        "b2_closure_execution_plan_external_superiority_after_plan_only": b2_remaining_work.get(
            "closure_execution_plan", {}
        ).get("external_superiority_claim_allowed_after_plan_only"),
        "b2_closure_execution_plan_lane_count": b2_remaining_work.get("closure_execution_plan", {}).get(
            "active_suite_lane_count"
        ),
        "b4_work_precision_plan_schema": b4_work_precision_plan.get("schema"),
        "b4_work_precision_plan_status": b4_work_precision_plan.get("status"),
        "b4_work_precision_plan_open_blockers": b4_work_precision_plan.get("open_blockers_after_plan"),
        "b4_work_precision_plan_source_policy_rows_closed": b4_work_precision_plan.get(
            "current_evidence", {}
        ).get("source_policy_rows_closed"),
        "b4_work_precision_plan_source_policy_rows_total": b4_work_precision_plan.get(
            "current_evidence", {}
        ).get("source_policy_rows_total"),
        "b4_work_precision_plan_ready_lanes": b4_work_precision_plan.get("execution_lane_summary", {}).get(
            "ready_to_launch_after_explicit_opt_in_count"
        ),
        "b4_work_precision_plan_not_ready_lanes": b4_work_precision_plan.get("execution_lane_summary", {}).get(
            "not_ready_lane_count"
        ),
        "b4_work_precision_plan_heavy_run_invoked": b4_work_precision_plan.get("execution_policy", {}).get(
            "heavy_numerical_run_invoked"
        ),
        "b4_work_precision_plan_run_v047_invoked": b4_work_precision_plan.get("execution_policy", {}).get(
            "run_v047_invoked"
        ),
        "b4_work_precision_plan_v048_runner_invoked": b4_work_precision_plan.get("execution_policy", {}).get(
            "v048_runner_invoked"
        ),
        "b4_work_precision_plan_next_heavy_requires_user_opt_in": b4_work_precision_plan.get(
            "execution_policy", {}
        ).get("next_heavy_source_policy_execution_requires_user_opt_in"),
        "b4_work_precision_plan_ra2021_preflight_status": b4_work_precision_plan.get(
            "ra2021_launch_preflight", {}
        ).get("status"),
        "b4_work_precision_plan_ra2021_launch_commands": b4_work_precision_plan.get(
            "ra2021_launch_preflight", {}
        ).get("launch_command_count"),
        "b4_work_precision_plan_ra2021_cli_status": b4_work_precision_plan.get(
            "ra2021_launch_preflight", {}
        ).get("runner_cli_contract", {}).get("status"),
        "b4_work_precision_plan_ra2021_cli_runner_checks": b4_work_precision_plan.get(
            "ra2021_launch_preflight", {}
        ).get("runner_cli_contract", {}).get("runner_contract_count"),
        "b4_work_precision_plan_ra2021_cli_command_checks": b4_work_precision_plan.get(
            "ra2021_launch_preflight", {}
        ).get("runner_cli_contract", {}).get("command_contract_count"),
        "b4_work_precision_plan_hi2022_preflight_status": b4_work_precision_plan.get(
            "hi2022_launch_preflight", {}
        ).get("status"),
        "b4_work_precision_plan_hi2022_launch_commands": b4_work_precision_plan.get(
            "hi2022_launch_preflight", {}
        ).get("launch_command_count"),
        "b4_work_precision_plan_hi2022_completed_shards": b4_work_precision_plan.get(
            "hi2022_launch_preflight", {}
        ).get("completed_shard_count"),
        "b4_work_precision_plan_hi2022_missing_shards": len(
            b4_work_precision_plan.get("hi2022_launch_preflight", {}).get("missing_or_unexecuted_shards", [])
        ),
        "b4_work_precision_plan_hi2022_commands_avoid_1e_4": b4_work_precision_plan.get(
            "hi2022_launch_preflight", {}
        ).get("all_launch_commands_avoid_1e_4"),
        "b4_work_precision_plan_hi2022_cli_status": b4_work_precision_plan.get(
            "hi2022_launch_preflight", {}
        ).get("runner_cli_contract", {}).get("status"),
        "b4_work_precision_plan_hi2022_cli_runner_checks": b4_work_precision_plan.get(
            "hi2022_launch_preflight", {}
        ).get("runner_cli_contract", {}).get("runner_contract_count"),
        "b4_work_precision_plan_hi2022_cli_command_checks": b4_work_precision_plan.get(
            "hi2022_launch_preflight", {}
        ).get("runner_cli_contract", {}).get("command_contract_count"),
        "b4_work_precision_plan_hi2022_source_policy_rows_closed": b4_work_precision_plan.get(
            "hi2022_launch_preflight", {}
        ).get("source_policy_rows_closed_by_preflight"),
        "b4_work_precision_plan_hi2022_closes_b4": b4_work_precision_plan.get(
            "hi2022_launch_preflight", {}
        ).get("b4_can_close_after_preflight_only"),
        "b4_work_precision_plan_hi2022_closes_b7": b4_work_precision_plan.get(
            "hi2022_launch_preflight", {}
        ).get("b7_can_close_after_preflight_only"),
        "b4_existing_promotion_audit_schema": b4_existing_promotion_audit.get("schema"),
        "b4_existing_promotion_audit_status": b4_existing_promotion_audit.get("status"),
        "b4_existing_promotion_candidate_items": b4_existing_promotion_audit.get("candidate_item_count"),
        "b4_existing_promotion_ready_without_new_execution": b4_existing_promotion_audit.get(
            "promotion_ready_without_new_execution_count"
        ),
        "b4_existing_promotion_b4_closing_items": b4_existing_promotion_audit.get("b4_closing_item_count"),
        "b4_existing_promotion_b7_closing_items": b4_existing_promotion_audit.get("b7_closing_item_count"),
        "b4_existing_promotion_source_policy_rows_closed": b4_existing_promotion_audit.get(
            "source_policy_rows_closed_by_existing_artifacts"
        ),
        "b4_existing_promotion_source_policy_rows_total": b4_existing_promotion_audit.get(
            "source_policy_rows_total"
        ),
        "b4_existing_promotion_b4_can_close_now": b4_existing_promotion_audit.get("b4_can_close_now"),
        "b4_existing_promotion_b7_can_close_now": b4_existing_promotion_audit.get("b7_can_close_now"),
        "b4_existing_promotion_heavy_run_invoked": b4_existing_promotion_audit.get(
            "heavy_numerical_run_invoked"
        ),
        "b4_existing_promotion_run_v047_invoked": b4_existing_promotion_audit.get("run_v047_invoked"),
        "b4_existing_promotion_v048_runner_invoked": b4_existing_promotion_audit.get("v048_runner_invoked"),
        "b4_post_execution_audit_schema": b4_post_execution_audit.get("schema"),
        "b4_post_execution_audit_status": b4_post_execution_audit.get("status"),
        "b4_post_execution_approved_driver_execution_recorded": b4_post_execution_audit.get(
            "approved_driver_execution_recorded"
        ),
        "b4_post_execution_verified_authorized_execution_recorded": b4_post_execution_audit.get(
            "verified_authorized_execution_recorded"
        ),
        "b4_post_execution_existing_ready_command_artifacts_present": b4_post_execution_audit.get(
            "existing_ready_command_artifacts_present"
        ),
        "b4_post_execution_execution_record_scope": b4_post_execution_audit.get("execution_record_scope"),
        "b4_post_execution_outputs_present": b4_post_execution_audit.get(
            "command_artifact_presence", {}
        ).get("all_expected_outputs_exist_now"),
        "b4_post_execution_source_policy_rows_closed": b4_post_execution_audit.get(
            "source_policy_rows_closed"
        ),
        "b4_post_execution_source_policy_rows_total": b4_post_execution_audit.get(
            "source_policy_total_rows"
        ),
        "b4_post_execution_source_policy_rows_open": b4_post_execution_audit.get(
            "source_policy_rows_open"
        ),
        "b4_post_execution_b4_can_close_now": b4_post_execution_audit.get("b4_can_close_now"),
        "b4_post_execution_b7_can_close_now": b4_post_execution_audit.get("b7_can_close_now"),
        "b4_post_execution_external_superiority_allowed": b4_post_execution_audit.get(
            "external_superiority_claim_allowed"
        ),
        "b4_post_execution_ra2021_double_candidate_status": b4_post_execution_audit.get(
            "post_execution_artifact_evidence", {}
        ).get("ra2021_double_local_candidate_status"),
        "b4_post_execution_hi2022_selected_candidate_status": b4_post_execution_audit.get(
            "post_execution_artifact_evidence", {}
        ).get("hi2022_selected_candidate_status"),
        "b4_post_execution_hi2022_partial_or_failed_shards": b4_post_execution_audit.get(
            "post_execution_artifact_evidence", {}
        ).get("hi2022_selected_candidate_partial_or_failed_shards"),
        "ra_hi_source_policy_post_execution_attempt_certificate_status": (
            ra_hi_post_execution_attempt_certificate.get("status")
        ),
        "ra_hi_source_policy_post_execution_attempt_rows": (
            ra_hi_post_execution_attempt_certificate.get("row_count")
        ),
        "ra_hi_source_policy_post_execution_attempt_ra_rows": (
            ra_hi_post_execution_attempt_certificate.get("ra2021_row_count")
        ),
        "ra_hi_source_policy_post_execution_attempt_hi_rows": (
            ra_hi_post_execution_attempt_certificate.get("hi2022_row_count")
        ),
        "ra_hi_source_policy_post_execution_attempt_promoted_rows": (
            ra_hi_post_execution_attempt_certificate.get("source_policy_rows_promoted")
        ),
        "ra_hi_source_policy_post_execution_attempt_open_rows": (
            ra_hi_post_execution_attempt_certificate.get("rows_still_requiring_execution_or_promotion")
        ),
        "ra_hi_source_policy_closeout_checklist_schema": ra_hi_source_policy_closeout_checklist.get("schema"),
        "ra_hi_source_policy_closeout_checklist_status": ra_hi_source_policy_closeout_checklist.get("status"),
        "ra_hi_source_policy_closeout_total_rows": ra_hi_source_policy_closeout_checklist.get("coverage", {}).get(
            "source_policy_rows_total"
        ),
        "ra_hi_source_policy_closeout_ra_rows": ra_hi_source_policy_closeout_checklist.get("coverage", {}).get(
            "ra2021_rows"
        ),
        "ra_hi_source_policy_closeout_hi_rows": ra_hi_source_policy_closeout_checklist.get("coverage", {}).get(
            "hi2022_rows"
        ),
        "ra_hi_source_policy_closeout_ready_commands": ra_hi_source_policy_closeout_checklist.get("coverage", {}).get(
            "ready_command_count"
        ),
        "ra_hi_source_policy_closeout_mapped_rows": ra_hi_source_policy_closeout_checklist.get("coverage", {}).get(
            "ready_command_mapped_external_rows"
        ),
        "ra_hi_source_policy_closeout_promoted_rows": ra_hi_source_policy_closeout_checklist.get("coverage", {}).get(
            "source_policy_rows_promoted"
        ),
        "ra_hi_source_policy_closeout_completed_rows": ra_hi_source_policy_closeout_checklist.get("coverage", {}).get(
            "source_policy_rows_completed"
        ),
        "ra_hi_source_policy_closeout_external_ready_rows": ra_hi_source_policy_closeout_checklist.get(
            "coverage", {}
        ).get("external_superiority_ready_rows"),
        "ra_hi_source_policy_closeout_exact_opt_in": ra_hi_source_policy_closeout_checklist.get(
            "guarded_execution_boundary", {}
        ).get("exact_required_user_approval_statement"),
        "ra_hi_source_policy_closeout_opt_in_required": ra_hi_source_policy_closeout_checklist.get(
            "guarded_execution_boundary", {}
        ).get("explicit_user_opt_in_required_before_any_command"),
        "ra_hi_source_policy_closeout_execution_invoked": ra_hi_source_policy_closeout_checklist.get(
            "guarded_execution_boundary", {}
        ).get("execution_invoked_by_packet"),
        "ra_hi_source_policy_closeout_b4_can_close": ra_hi_source_policy_closeout_checklist.get(
            "not_promoted_disposition", {}
        ).get("b4_can_close_from_this_checklist"),
        "ra_hi_source_policy_closeout_b7_can_close": ra_hi_source_policy_closeout_checklist.get(
            "not_promoted_disposition", {}
        ).get("b7_can_close_from_this_checklist"),
        "ra_hi_source_policy_closeout_can_claim_external_superiority": ra_hi_source_policy_closeout_checklist.get(
            "not_promoted_disposition", {}
        ).get("can_claim_external_superiority_from_ra_hi_now"),
        "ra_hi_source_policy_output_inventory_status": ra_hi_source_policy_output_inventory.get("status"),
        "ra_hi_source_policy_output_inventory_command_count": ra_hi_source_policy_output_inventory.get(
            "coverage", {}
        ).get("command_count"),
        "ra_hi_source_policy_output_inventory_outputs_existing": ra_hi_source_policy_output_inventory.get(
            "coverage", {}
        ).get("expected_output_existing_count"),
        "ra_hi_source_policy_output_inventory_summaries_existing": ra_hi_source_policy_output_inventory.get(
            "coverage", {}
        ).get("expected_summary_existing_count"),
        "ra_hi_source_policy_output_inventory_csv_data_rows": ra_hi_source_policy_output_inventory.get(
            "coverage", {}
        ).get("expected_output_csv_data_rows"),
        "ra_hi_source_policy_output_inventory_hi_ok_rows": ra_hi_source_policy_output_inventory.get(
            "coverage", {}
        ).get("hi2022_summary_ok_rows"),
        "ra_hi_source_policy_output_inventory_closed_rows": ra_hi_source_policy_output_inventory.get(
            "coverage", {}
        ).get("source_policy_rows_closed_by_inventory"),
        "ra_hi_source_policy_promotion_blocker_matrix_status": ra_hi_source_policy_promotion_blocker_matrix.get(
            "status"
        ),
        "ra_hi_source_policy_promotion_blocker_matrix_rows": ra_hi_source_policy_promotion_blocker_matrix.get(
            "row_count"
        ),
        "ra_hi_source_policy_promotion_blocker_matrix_ra_rows": ra_hi_source_policy_promotion_blocker_matrix.get(
            "ra2021_row_count"
        ),
        "ra_hi_source_policy_promotion_blocker_matrix_hi_rows": ra_hi_source_policy_promotion_blocker_matrix.get(
            "hi2022_row_count"
        ),
        "ra_hi_source_policy_promotion_blocker_matrix_public_root_rows": ra_hi_source_policy_promotion_blocker_matrix.get(
            "public_source_root_available_rows"
        ),
        "ra_hi_source_policy_promotion_blocker_matrix_no_public_code_rows": ra_hi_source_policy_promotion_blocker_matrix.get(
            "no_public_code_rows_included"
        ),
        "ra_hi_source_policy_promotion_blocker_matrix_closed_rows": ra_hi_source_policy_promotion_blocker_matrix.get(
            "source_policy_rows_closed"
        ),
        "ra_hi_source_policy_promotion_blocker_matrix_not_promoted_rows": ra_hi_source_policy_promotion_blocker_matrix.get(
            "source_policy_rows_not_promoted"
        ),
        "ra_hi_source_policy_promotion_blocker_matrix_attempted_not_reproducible_rows": ra_hi_source_policy_promotion_blocker_matrix.get(
            "attempted_not_reproducible_rows"
        ),
        "ra_hi_source_policy_promotion_blocker_matrix_current_evidence_terminal_rows": ra_hi_source_policy_promotion_blocker_matrix.get(
            "current_evidence_terminal_not_promotable_rows"
        ),
        "ra_hi_source_policy_promotion_blocker_matrix_future_authorization_or_artifact_rows": ra_hi_source_policy_promotion_blocker_matrix.get(
            "future_promotion_requires_authorized_execution_or_new_artifact_rows"
        ),
        "ra_hi_source_policy_promotion_blocker_matrix_reproduction_complete_rows": ra_hi_source_policy_promotion_blocker_matrix.get(
            "source_policy_reproduction_complete_rows"
        ),
        "ra_hi_source_policy_promotion_blocker_matrix_command_mapped_rows": ra_hi_source_policy_promotion_blocker_matrix.get(
            "command_mapped_rows"
        ),
        "ra_hi_source_policy_promotion_blocker_matrix_output_present_rows": ra_hi_source_policy_promotion_blocker_matrix.get(
            "rows_with_all_command_outputs_present"
        ),
        "b4_row_readiness_ledger_schema": b4_row_readiness_ledger.get("schema"),
        "b4_row_readiness_ledger_status": b4_row_readiness_ledger.get("status"),
        "b4_row_readiness_external_rows": b4_row_readiness_ledger.get("row_count"),
        "b4_row_readiness_expected_external_rows": b4_row_readiness_ledger.get("expected_external_row_count"),
        "b4_row_readiness_source_policy_rows_closed": b4_row_readiness_ledger.get("source_policy_rows_closed"),
        "b4_row_readiness_source_policy_rows_open": b4_row_readiness_ledger.get("source_policy_rows_open"),
        "b4_row_readiness_rows_with_launch_command_refs": b4_row_readiness_ledger.get(
            "rows_with_launch_command_refs"
        ),
        "b4_row_readiness_rows_without_launch_command_refs": b4_row_readiness_ledger.get(
            "rows_without_launch_command_refs"
        ),
        "b4_row_readiness_ready_suites": b4_row_readiness_ledger.get("ready_suite_count"),
        "b4_row_readiness_not_ready_suites": b4_row_readiness_ledger.get("not_ready_suite_count"),
        "b4_row_readiness_b4_can_close_now": b4_row_readiness_ledger.get("b4_can_close_now"),
        "b4_row_readiness_b7_can_close_now": b4_row_readiness_ledger.get("b7_can_close_now"),
        "b4_row_readiness_heavy_run_invoked": b4_row_readiness_ledger.get("heavy_numerical_run_invoked"),
        "b4_row_readiness_run_v047_invoked": b4_row_readiness_ledger.get("run_v047_invoked"),
        "b4_row_readiness_v048_runner_invoked": b4_row_readiness_ledger.get("v048_runner_invoked"),
        "b4_execution_opt_in_packet_schema": b4_execution_opt_in_packet.get("schema"),
        "b4_execution_opt_in_packet_status": b4_execution_opt_in_packet.get("status"),
        "b4_execution_opt_in_explicit_user_opt_in_required": b4_execution_opt_in_packet.get(
            "explicit_user_opt_in_required_before_any_command"
        ),
        "b4_execution_opt_in_ready_command_count": b4_execution_opt_in_packet.get("ready_command_count"),
        "b4_execution_opt_in_mapped_external_rows": b4_execution_opt_in_packet.get(
            "ready_command_mapped_external_rows"
        ),
        "b4_execution_opt_in_unaddressed_external_rows": b4_execution_opt_in_packet.get(
            "unaddressed_external_rows_after_ready_commands"
        ),
        "b4_execution_opt_in_source_policy_rows_closed_now": b4_execution_opt_in_packet.get(
            "source_policy_rows_closed_now"
        ),
        "b4_execution_opt_in_source_policy_rows_total": b4_execution_opt_in_packet.get(
            "source_policy_rows_total"
        ),
        "source_policy_execution_handoff_command_traceability_summary": (
            b4_command_traceability_summary
        ),
        "source_policy_execution_handoff_unique_mapped_row_count": (
            b4_command_traceability_summary.get("unique_mapped_row_count")
        ),
        "source_policy_execution_handoff_ra_hi_unique_row_count": (
            b4_command_traceability_summary.get("ra_hi_unique_row_count")
        ),
        "source_policy_execution_handoff_ra_hi_unique_rows_all_mapped": (
            b4_command_traceability_summary.get("ra_hi_unique_rows_all_mapped")
        ),
        "source_policy_execution_handoff_declared_mapped_row_reference_total": (
            b4_command_traceability_summary.get("declared_mapped_row_reference_total")
        ),
        "source_policy_execution_handoff_traced_command_row_reference_total": (
            b4_command_traceability_summary.get("traced_command_row_reference_total")
        ),
        "source_policy_execution_handoff_declared_vs_traced_mismatch_count": (
            b4_command_traceability_summary.get("declared_vs_traced_mismatch_count")
        ),
        "source_policy_execution_handoff_terminal_rows_with_command_refs": (
            b4_command_traceability_summary.get("terminal_rows_with_command_refs")
        ),
        "source_policy_execution_handoff_traceability_closed_rows": (
            b4_command_traceability_summary.get("source_policy_closed_rows")
        ),
        "source_policy_execution_handoff_traceability_promotion_ready_rows": (
            b4_command_traceability_summary.get("promotion_ready_rows")
        ),
        "b4_execution_opt_in_b4_can_close_after_ready_commands_only": b4_execution_opt_in_packet.get(
            "b4_can_close_after_ready_commands_only"
        ),
        "b4_execution_opt_in_b7_can_close_after_ready_commands_only": b4_execution_opt_in_packet.get(
            "b7_can_close_after_ready_commands_only"
        ),
        "b4_execution_opt_in_execution_invoked_by_packet": b4_execution_opt_in_packet.get(
            "execution_invoked_by_packet"
        ),
        "b4_execution_opt_in_heavy_run_invoked": b4_execution_opt_in_packet.get("heavy_numerical_run_invoked"),
        "b4_execution_opt_in_run_v047_invoked": b4_execution_opt_in_packet.get("run_v047_invoked"),
        "b4_execution_opt_in_v048_runner_invoked": b4_execution_opt_in_packet.get("v048_runner_invoked"),
        "b4_post_execution_promotion_contract_schema": b4_execution_opt_in_packet.get(
            "post_execution_promotion_contract", {}
        ).get("schema"),
        "b4_post_execution_promotion_contract_status": b4_execution_opt_in_packet.get(
            "post_execution_promotion_contract", {}
        ).get("status"),
        "b4_post_execution_promotion_contract_rows_closed": b4_execution_opt_in_packet.get(
            "post_execution_promotion_contract", {}
        ).get("source_policy_rows_closed_now"),
        "b4_post_execution_promotion_contract_rows_total": b4_execution_opt_in_packet.get(
            "post_execution_promotion_contract", {}
        ).get("source_policy_rows_total"),
        "b4_post_execution_promotion_contract_ready_mapped_rows": b4_execution_opt_in_packet.get(
            "post_execution_promotion_contract", {}
        ).get("ready_command_mapped_external_rows"),
        "b4_post_execution_promotion_contract_unaddressed_rows": b4_execution_opt_in_packet.get(
            "post_execution_promotion_contract", {}
        ).get("unaddressed_external_rows_after_ready_commands"),
        "b4_post_execution_promotion_contract_checks_satisfied_now": b4_execution_opt_in_packet.get(
            "post_execution_promotion_contract", {}
        ).get("all_required_checks_satisfied_now"),
        "b4_post_execution_promotion_contract_b4_can_close_now": b4_execution_opt_in_packet.get(
            "post_execution_promotion_contract", {}
        ).get("b4_can_close_after_promotion_contract_now"),
        "b4_post_execution_promotion_contract_b7_can_close_now": b4_execution_opt_in_packet.get(
            "post_execution_promotion_contract", {}
        ).get("b7_can_close_after_promotion_contract_now"),
        "b4_post_execution_promotion_contract_ready_lane_count": len(
            b4_execution_opt_in_packet.get("post_execution_promotion_contract", {}).get(
                "ready_lanes_after_explicit_opt_in", []
            )
        ),
        "b4_post_execution_promotion_contract_not_ready_lane_count": len(
            b4_execution_opt_in_packet.get("post_execution_promotion_contract", {}).get(
                "not_ready_lanes", []
            )
        ),
        "b4_post_execution_promotion_contract_runner_code_path_gap_rows": b4_execution_opt_in_packet.get(
            "post_execution_promotion_contract", {}
        ).get("remaining_gap_rows_requiring_new_runner_or_code_path"),
        "claim_demotion_audit_schema": external_superiority_claim_demotion.get("schema"),
        "claim_demotion_audit_status": external_superiority_claim_demotion.get("status"),
        "claim_demotion_audit_route_b_ready": external_superiority_claim_demotion.get("route_b_ready"),
        "claim_demotion_audit_route_b_promoted_to_blocker_gate": external_superiority_claim_demotion.get(
            "route_b_promoted_to_blocker_gate"
        ),
        "claim_demotion_audit_b2_b4_gate_closed_by_this_artifact": external_superiority_claim_demotion.get(
            "b2_b4_gate_closed_by_this_artifact"
        ),
        "claim_demotion_audit_b2_gate_closed_by_route_b": external_superiority_claim_demotion.get(
            "b2_gate_closed_by_route_b_claim_demotion"
        ),
        "claim_demotion_audit_b4_gate_closed_by_route_b": external_superiority_claim_demotion.get(
            "b4_gate_closed_by_route_b_claim_demotion"
        ),
        "claim_demotion_audit_claim_after_route": external_superiority_claim_demotion.get("claim_after_route"),
        "claim_demotion_audit_external_superiority_after_route": external_superiority_claim_demotion.get(
            "external_superiority_claim_allowed_after_route"
        ),
        "claim_demotion_audit_source_policy_rows_closed": external_superiority_claim_demotion.get(
            "source_policy_execution_rows_closed"
        ),
        "claim_demotion_audit_source_policy_total_rows": external_superiority_claim_demotion.get(
            "source_policy_execution_total_rows"
        ),
        "claim_demotion_audit_current_demoted_suites": external_superiority_claim_demotion.get(
            "suite_demotions", {}
        ).get("currently_demoted_suites"),
        "claim_demotion_audit_additional_demotions_needed": external_superiority_claim_demotion.get(
            "suite_demotions", {}
        ).get("additional_demotions_needed_for_route_b"),
        "claim_demotion_audit_full_demotion_scope_after_route_b": external_superiority_claim_demotion.get(
            "suite_demotions", {}
        ).get("full_demotion_scope_after_route_b"),
        "claim_demotion_audit_formal_order_retained": external_superiority_claim_demotion.get(
            "retained_claims", {}
        ).get("formal_order_claim_retained"),
        "claim_demotion_audit_common_reference_cells": external_superiority_claim_demotion.get(
            "retained_claims", {}
        ).get("common_reference_cells"),
        "claim_demotion_audit_direct_order_wins": external_superiority_claim_demotion.get(
            "retained_claims", {}
        ).get("direct_nonlocal_order_wins"),
        "claim_demotion_audit_direct_error_wins": external_superiority_claim_demotion.get(
            "retained_claims", {}
        ).get("direct_nonlocal_error_wins"),
        "claim_demotion_audit_default_1e_4_required": external_superiority_claim_demotion.get(
            "execution_policy", {}
        ).get("default_1e_4_required"),
        "claim_demotion_audit_heavy_run_invoked": external_superiority_claim_demotion.get(
            "execution_policy", {}
        ).get("heavy_numerical_run_invoked"),
        "claim_demotion_audit_run_v047_invoked": external_superiority_claim_demotion.get(
            "execution_policy", {}
        ).get("run_v047_invoked"),
        "claim_demotion_route_b_contract_schema": external_superiority_claim_demotion.get(
            "route_b_application_contract", {}
        ).get("schema"),
        "claim_demotion_route_b_ready_to_promote": external_superiority_claim_demotion.get(
            "route_b_application_contract", {}
        ).get("ready_to_promote_to_blocker_gate_now"),
        "claim_demotion_route_b_safe_to_flip_flags": external_superiority_claim_demotion.get(
            "route_b_application_contract", {}
        ).get("safe_to_flip_gate_flags_without_other_edits"),
        "claim_demotion_route_b_satisfied_steps": external_superiority_claim_demotion.get(
            "route_b_application_contract", {}
        ).get("currently_satisfied_steps"),
        "claim_demotion_route_b_total_steps": external_superiority_claim_demotion.get(
            "route_b_application_contract", {}
        ).get("application_step_count"),
        "claim_demotion_route_b_unsatisfied_steps": external_superiority_claim_demotion.get(
            "route_b_application_contract", {}
        ).get("unsatisfied_steps"),
        "claim_demotion_route_b_creates_numerical_wins": external_superiority_claim_demotion.get(
            "route_b_application_contract", {}
        ).get("route_b_demotion_contract_creates_numerical_wins"),
        "ra2021_source_policy_audit_schema": ra2021_source_policy_audit.get("schema"),
        "ra2021_source_policy_audit_status": ra2021_source_policy_audit.get("status"),
        "ra2021_per_row_source_identity_requirements_resolved": ra2021_source_policy_audit.get(
            "per_row_source_identity_requirements_resolved"
        ),
        "ra2021_per_row_source_policy_promotion_requirements_remaining": ra2021_source_policy_audit.get(
            "per_row_source_policy_promotion_requirements_remaining"
        ),
        "ra2021_row_missing_evidence_shrunk_by_identity_audit": ra2021_source_policy_audit.get(
            "row_missing_evidence_shrunk_by_identity_audit"
        ),
        "ra2021_promotion_gap_drilldown_checked": ra2021_source_policy_audit.get(
            "promotion_gap_drilldown", {}
        ).get("checked"),
        "ra2021_promotion_gap_examples_checked": ra2021_source_policy_audit.get(
            "promotion_gap_drilldown", {}
        ).get("examples_checked"),
        "ra2021_promotion_gap_active_rows_checked": ra2021_source_policy_audit.get(
            "promotion_gap_drilldown", {}
        ).get("active_rows_checked"),
        "ra2021_promotion_gap_source_identity_closed": ra2021_source_policy_audit.get(
            "promotion_gap_drilldown", {}
        ).get("source_identity_closed"),
        "ra2021_promotion_gap_source_policy_promotion_closed": ra2021_source_policy_audit.get(
            "promotion_gap_drilldown", {}
        ).get("source_policy_promotion_closed"),
        "ra2021_promotion_gap_single_status": ra2021_source_policy_audit.get(
            "promotion_gap_drilldown", {}
        ).get("per_example", {}).get("single_pendulum", {}).get("promotion_status"),
        "ra2021_promotion_gap_double_status": ra2021_source_policy_audit.get(
            "promotion_gap_drilldown", {}
        ).get("per_example", {}).get("double_pendulum", {}).get("promotion_status"),
        "ra2021_promotion_gap_closed_loop_status": ra2021_source_policy_audit.get(
            "promotion_gap_drilldown", {}
        ).get("per_example", {}).get("four_link", {}).get("promotion_status"),
        "ra2021_source_identity_schema": ra2021_source_identity_audit.get("schema"),
        "ra2021_source_identity_status": ra2021_source_identity_audit.get("status"),
        "ra2021_source_identity_output_mapping_verified": ra2021_source_identity_audit.get(
            "claim_boundary", {}
        ).get("output_mapping_verified_from_source"),
        "ra2021_source_identity_time_grid_extracted": ra2021_source_identity_audit.get(
            "claim_boundary", {}
        ).get("time_grid_policy_extracted_from_source"),
        "ra2021_source_identity_source_policy_rows_closed": ra2021_source_identity_audit.get(
            "claim_boundary", {}
        ).get("source_policy_reproduction_rows_closed"),
        "ra2021_source_identity_external_superiority_allowed": ra2021_source_identity_audit.get(
            "claim_boundary", {}
        ).get("external_superiority_claim_allowed"),
        "ra2021_source_identity_velocity_mismatch_reinterpreted": ra2021_source_identity_audit.get(
            "claim_boundary", {}
        ).get("existing_velocity_mismatch_rows_reinterpreted_as_policy_mismatch_not_unknown_output_mapping"),
        "ra2021_source_identity_position_mismatch_rows": ra2021_source_identity_audit.get(
            "forensic_issue_counts", {}
        ).get("position_aligned_velocity_mismatch_rows"),
        "ra2021_source_identity_velocity_floor_rows": ra2021_source_identity_audit.get(
            "forensic_issue_counts", {}
        ).get("velocity_nonmonotone_or_floor_limited_rows"),
        "ra2021_active_b2_flagged_rows": ra2021_source_policy_audit.get("active_b2_flagged_rows"),
        "ra2021_public_order_groups_completed": ra2021_source_policy_audit.get(
            "public_order_groups_completed"
        ),
        "ra2021_public_order_groups_required": ra2021_source_policy_audit.get("public_order_groups_required"),
        "ra2021_public_timing_rows_completed": ra2021_source_policy_audit.get(
            "public_timing_rows_completed"
        ),
        "ra2021_public_timing_rows_required": ra2021_source_policy_audit.get("public_timing_rows_required"),
        "ra2021_fixed_grid_common_reference_rows": ra2021_source_policy_audit.get(
            "fixed_grid_common_reference_rows"
        ),
        "ra2021_paper_safe_common_reference_rows": ra2021_source_policy_audit.get(
            "paper_safe_common_reference_rows"
        ),
        "ra2021_source_policy_reproduction_rows": ra2021_source_policy_audit.get(
            "source_policy_reproduction_rows"
        ),
        "ra2021_position_aligned_velocity_mismatch_rows": ra2021_source_policy_audit.get(
            "position_aligned_velocity_mismatch_rows"
        ),
        "ra2021_velocity_nonmonotone_or_floor_limited_rows": ra2021_source_policy_audit.get(
            "velocity_nonmonotone_or_floor_limited_rows"
        ),
        "ra2021_can_close_b2_requirement_now": ra2021_source_policy_audit.get("decision", {}).get(
            "can_close_ra2021_b2_requirement_now"
        ),
        "ra2021_default_1e_4_required": ra2021_source_policy_audit.get("execution_policy", {}).get(
            "default_1e_4_required"
        ),
        "ra2021_heavy_run_invoked": ra2021_source_policy_audit.get("execution_policy", {}).get(
            "heavy_numerical_run_invoked"
        ),
        "ra2021_run_v047_invoked": ra2021_source_policy_audit.get("execution_policy", {}).get(
            "run_v047_invoked"
        ),
        "tfe_source_policy_spec_schema": tfe_source_policy_spec.get("schema"),
        "tfe_source_policy_spec_status": tfe_source_policy_spec.get("status"),
        "tfe_source_policy_reference_h": tfe_source_policy_spec.get("source_policy", {})
        .get("solver_policy", {})
        .get("source_reference_h_for_exact_reproduction"),
        "tfe_source_policy_rows_completed": tfe_source_policy_spec.get("runner_gap", {}).get(
            "source_policy_rows_completed"
        ),
        "tfe_source_policy_runner_implemented": tfe_source_policy_spec.get("runner_gap", {}).get(
            "pendulum_dae_runner_implemented"
        ),
        "tfe_source_policy_external_superiority_allowed": tfe_source_policy_spec.get("runner_gap", {}).get(
            "external_superiority_allowed"
        ),
        "tfe_public_code_recheck_status": tfe_public_code_recheck.get("status"),
        "tfe_public_code_recheck_date": tfe_public_code_recheck.get("date_checked"),
        "tfe_public_code_recheck_github_repository_search_total_count": tfe_public_code_recheck.get(
            "coverage", {}
        ).get("github_repository_search_total_count"),
        "tfe_public_code_recheck_github_user_search_total_count": tfe_public_code_recheck.get(
            "coverage", {}
        ).get("github_user_search_total_count"),
        "tfe_public_code_recheck_github_code_search_api_status": tfe_public_code_recheck.get(
            "coverage", {}
        ).get("github_code_search_api_status"),
        "tfe_public_code_recheck_attempted_not_reproducible_rows": tfe_public_code_recheck.get(
            "coverage", {}
        ).get("source_policy_rows_attempted_not_reproducible"),
        "tfe_public_code_recheck_source_policy_rows_closed": tfe_public_code_recheck.get(
            "coverage", {}
        ).get("source_policy_rows_closed"),
        "tfe_public_code_recheck_external_superiority_allowed": tfe_public_code_recheck.get(
            "claim_boundary", {}
        ).get("external_superiority_claim_allowed"),
        "tfe_candidate_source_policy_boundary": tfe_candidate_source_boundary,
        "tfe_candidate_source_policy_boundary_sources": tfe_candidate_source_boundary_sources,
        "tfe_candidate_source_policy_boundary_sources_match": tfe_candidate_source_boundary_sources_match,
        "tfe_source_policy_self_reproduction_attempt_certificate_status": (
            tfe_self_reproduction_attempt_certificate.get("status")
        ),
        "tfe_source_policy_self_reproduction_attempt_rows": (
            tfe_self_reproduction_attempt_certificate.get("self_reproduction_attempted_rows")
        ),
        "tfe_source_policy_self_reproduction_attempt_not_reproducible_rows": (
            tfe_self_reproduction_attempt_certificate.get("attempted_not_reproducible_rows")
        ),
        "tfe_source_policy_self_reproduction_attempt_closed_rows": (
            tfe_self_reproduction_attempt_certificate.get("source_policy_closed_rows")
        ),
        "tfe_source_policy_self_reproduction_preflight_status": (
            tfe_self_reproduction_execution_preflight.get("status")
        ),
        "tfe_source_policy_self_reproduction_preflight_current_route": (
            tfe_self_reproduction_execution_preflight.get("current_route")
        ),
        "tfe_source_policy_self_reproduction_preflight_reopen_condition": (
            tfe_self_reproduction_execution_preflight.get("reopen_condition")
        ),
        "tfe_source_policy_self_reproduction_preflight_execution_block_count": (
            tfe_self_reproduction_execution_preflight.get("execution_block_count")
        ),
        "tfe_source_policy_self_reproduction_preflight_ready_now": (
            tfe_self_reproduction_execution_preflight.get("ready_to_execute_source_policy_now")
        ),
        "tfe_source_policy_self_reproduction_preflight_can_promote_rows_now": (
            tfe_self_reproduction_execution_preflight.get("can_promote_any_tfe_source_policy_row_now")
        ),
        "tfe_source_policy_self_reproduction_preflight_source_policy_rows_completed": (
            tfe_self_reproduction_execution_preflight.get("source_policy_rows_completed")
        ),
        "tfe_source_policy_self_reproduction_preflight_runner_contracts_required": (
            tfe_self_reproduction_execution_preflight.get("runner_contracts_required_before_execution", [])
        ),
        "tfe_source_policy_self_reproduction_required_next_action_count": len(
            tfe_self_reproduction_required_next_actions
        ),
        "tfe_candidate_source_policy_allowed_use": tfe_candidate_source_boundary.get(
            "candidate_scaffold_allowed_use"
        ),
        "tfe_candidate_source_policy_scaffold_present": tfe_candidate_source_boundary.get(
            "candidate_scaffold_present"
        ),
        "tfe_candidate_source_policy_dae_runner_equivalent": tfe_candidate_source_boundary.get(
            "source_policy_dae_runner_equivalent"
        ),
        "tfe_candidate_source_policy_method_runner_equivalent": tfe_candidate_source_boundary.get(
            "source_policy_method_runner_equivalent"
        ),
        "tfe_candidate_source_policy_rows_completed": tfe_candidate_source_boundary.get(
            "source_policy_rows_completed"
        ),
        "tfe_candidate_source_policy_external_superiority_allowed": tfe_candidate_source_boundary.get(
            "external_superiority_allowed"
        ),
        "tfe_candidate_source_policy_runner_required_for_promotion": tfe_candidate_source_boundary.get(
            "source_policy_runner_required_for_promotion"
        ),
        "tfe_candidate_source_policy_obligation_count": len(
            tfe_candidate_source_boundary.get("source_policy_runner_obligations", [])
        ),
        "tfe_dae_runner_contract_gap_status": tfe_dae_runner_contract_gap_audit.get("status"),
        "tfe_dae_runner_contract_gap_missing_block_count": tfe_dae_runner_contract_gap_audit.get(
            "missing_contract_block_count"
        ),
        "tfe_dae_runner_contract_gap_nonheavy_blocks": tfe_dae_runner_contract_gap_audit.get(
            "nonheavy_missing_contract_blocks"
        ),
        "tfe_dae_runner_contract_gap_terminal_nonpromoted_blocks": (
            tfe_dae_runner_contract_gap_audit.get("terminal_nonpromoted_contract_blocks")
        ),
        "tfe_dae_runner_contract_gap_terminal_nonpromoted_block_count": (
            tfe_dae_runner_contract_gap_audit.get("terminal_nonpromoted_contract_block_count")
        ),
        "tfe_dae_runner_contract_gap_effective_missing_blocks": (
            tfe_dae_runner_contract_gap_audit.get("effective_missing_contract_blocks")
        ),
        "tfe_dae_runner_contract_gap_effective_missing_block_count": (
            tfe_dae_runner_contract_gap_audit.get("effective_missing_contract_block_count")
        ),
        "tfe_dae_runner_contract_gap_block_accounting": (
            tfe_dae_runner_contract_gap_audit.get("contract_block_accounting")
        ),
        "tfe_dae_runner_contract_gap_execution_blocks": (
            tfe_dae_runner_contract_gap_audit.get("source_policy_execution_missing_contract_blocks")
        ),
        "tfe_source_policy_execution_preflight": tfe_source_policy_execution_preflight,
        "tfe_source_policy_execution_preflight_status": tfe_source_policy_execution_preflight.get(
            "status"
        ),
        "tfe_source_policy_execution_preflight_opt_in_required": tfe_source_policy_execution_preflight.get(
            "explicit_user_opt_in_required"
        ),
        "tfe_source_policy_execution_preflight_nonheavy_dispositioned": (
            tfe_source_policy_execution_preflight.get("nonheavy_blocks_dispositioned_by_demotion")
        ),
        "tfe_source_policy_execution_preflight_execution_block_count": (
            tfe_source_policy_execution_preflight.get("execution_block_count")
        ),
        "tfe_source_policy_execution_preflight_can_promote_rows_now": (
            tfe_source_policy_execution_preflight.get("can_promote_any_tfe_source_policy_row_now")
        ),
        "tfe_source_policy_execution_preflight_ready_now": tfe_source_policy_execution_preflight.get(
            "ready_to_execute_source_policy_now"
        ),
        "tfe_source_policy_execution_preflight_decision": tfe_source_policy_execution_preflight.get(
            "reviewer_facing_decision"
        ),
        "tfe_runner_contract_preflight_status": tfe_runner_contract_preflight.get("status"),
        "tfe_runner_contract_preflight_entrypoints": (
            f"{tfe_runner_contract_preflight.get('callable_contract_count')}/"
            f"{tfe_runner_contract_preflight.get('entrypoint_count')}"
        ),
        "tfe_runner_contract_preflight_candidate_backed": (
            f"{tfe_runner_contract_preflight.get('candidate_backed_contract_count')}/"
            f"{tfe_runner_contract_preflight.get('entrypoint_count')}"
        ),
        "tfe_runner_contract_preflight_source_policy_rows_completed": (
            tfe_runner_contract_preflight.get("source_policy_rows_completed")
        ),
        "tfe_runner_contract_preflight_execution_blocks": (
            tfe_runner_contract_preflight.get("source_policy_execution_block_count")
        ),
        "tfe_runner_contract_preflight_safe_use": tfe_runner_contract_preflight.get(
            "safe_current_use"
        ),
        "oc12_archive_tfe_runner_contract_preflight_status": objective_summary.get(
            "full_source_policy_runner_archive_gap_tfe_runner_contract_preflight_status"
        ),
        "oc12_archive_tfe_runner_contract_preflight_entrypoints": objective_summary.get(
            "full_source_policy_runner_archive_gap_tfe_runner_contract_preflight_entrypoints"
        ),
        "oc12_archive_tfe_runner_contract_preflight_candidate_backed": objective_summary.get(
            "full_source_policy_runner_archive_gap_tfe_runner_contract_preflight_candidate_backed"
        ),
        "oc12_archive_tfe_runner_contract_preflight_source_policy_rows_completed": (
            objective_summary.get(
                "full_source_policy_runner_archive_gap_tfe_runner_contract_preflight_source_policy_rows_completed"
            )
        ),
        "oc12_archive_tfe_runner_contract_preflight_execution_blocks": objective_summary.get(
            "full_source_policy_runner_archive_gap_tfe_runner_contract_preflight_execution_blocks"
        ),
        "oc12_archive_tfe_runner_contract_preflight_safe_use": objective_summary.get(
            "full_source_policy_runner_archive_gap_tfe_runner_contract_preflight_safe_use"
        ),
        "oc12_archive_action_boundary": objective_summary.get(
            "full_source_policy_runner_archive_gap_action_boundary"
        ),
        "oc12_archive_safe_without_b4_opt_in_count": objective_summary.get(
            "full_source_policy_runner_archive_gap_safe_without_b4_opt_in_count"
        ),
        "oc12_archive_opt_in_required_action_count": objective_summary.get(
            "full_source_policy_runner_archive_gap_opt_in_required_action_count"
        ),
        "oc12_archive_source_policy_execution_allowed_now": objective_summary.get(
            "full_source_policy_runner_archive_gap_source_policy_execution_allowed_now"
        ),
        "oc12_archive_source_policy_execution_invoked": objective_summary.get(
            "full_source_policy_runner_archive_gap_source_policy_execution_invoked"
        ),
        "oc12_archive_exact_b4_opt_in_required_for_execution": objective_summary.get(
            "full_source_policy_runner_archive_gap_exact_b4_opt_in_required_for_execution"
        ),
        "oc12_archive_opt_in_required_command_count": objective_summary.get(
            "full_source_policy_runner_archive_gap_opt_in_required_command_count"
        ),
        "oc12_archive_opt_in_required_mapped_external_rows": objective_summary.get(
            "full_source_policy_runner_archive_gap_opt_in_required_mapped_external_rows"
        ),
        "oc12_archive_safe_action_ids": objective_summary.get(
            "full_source_policy_runner_archive_gap_safe_action_ids"
        ),
        "oc12_archive_opt_in_action_ids": objective_summary.get(
            "full_source_policy_runner_archive_gap_opt_in_action_ids"
        ),
        "oc6_reopen_latest_external_probe": (
            f"{full_source_policy_runner_archive_gap.get('oc6_source_equivalent_reopen_readiness_latest_external_probe_date')}/"
            f"{full_source_policy_runner_archive_gap.get('oc6_source_equivalent_reopen_readiness_latest_external_probe_count')}/"
            f"{full_source_policy_runner_archive_gap.get('oc6_source_equivalent_reopen_readiness_latest_external_probe_positive_artifact_rows')}/"
            f"{full_source_policy_runner_archive_gap.get('oc6_source_equivalent_reopen_readiness_latest_external_probe_source_policy_rows_closed')}/"
            f"{full_source_policy_runner_archive_gap.get('oc6_source_equivalent_reopen_readiness_latest_external_probe_access_limited_count')}/"
            f"{full_source_policy_runner_archive_gap.get('oc6_source_equivalent_reopen_readiness_latest_external_probe_global_absence_proved')}/"
            f"{full_source_policy_runner_archive_gap.get('oc6_source_equivalent_reopen_readiness_latest_external_probe_reopen_triggered')}"
        ),
        "oc6_reopen_latest_external_probe_date": full_source_policy_runner_archive_gap.get(
            "oc6_source_equivalent_reopen_readiness_latest_external_probe_date"
        ),
        "oc6_reopen_latest_external_probe_count": full_source_policy_runner_archive_gap.get(
            "oc6_source_equivalent_reopen_readiness_latest_external_probe_count"
        ),
        "oc6_reopen_latest_external_probe_positive_artifact_rows": full_source_policy_runner_archive_gap.get(
            "oc6_source_equivalent_reopen_readiness_latest_external_probe_positive_artifact_rows"
        ),
        "oc6_reopen_latest_external_probe_source_policy_rows_closed": full_source_policy_runner_archive_gap.get(
            "oc6_source_equivalent_reopen_readiness_latest_external_probe_source_policy_rows_closed"
        ),
        "oc6_reopen_latest_external_probe_access_limited_count": full_source_policy_runner_archive_gap.get(
            "oc6_source_equivalent_reopen_readiness_latest_external_probe_access_limited_count"
        ),
        "oc6_reopen_latest_external_probe_global_absence_proved": full_source_policy_runner_archive_gap.get(
            "oc6_source_equivalent_reopen_readiness_latest_external_probe_global_absence_proved"
        ),
        "oc6_reopen_latest_external_probe_reopen_triggered": full_source_policy_runner_archive_gap.get(
            "oc6_source_equivalent_reopen_readiness_latest_external_probe_reopen_triggered"
        ),
        "tfe_source_policy_audit_schema": tfe_source_policy_audit.get("schema"),
        "tfe_source_policy_audit_status": tfe_source_policy_audit.get("status"),
        "tfe_active_b2_flagged_rows": tfe_source_policy_audit.get("active_b2_flagged_rows"),
        "tfe_source_policy_closed_rows": tfe_source_policy_audit.get("source_policy_closed_rows"),
        "tfe_external_superiority_ready_rows": tfe_source_policy_audit.get("external_superiority_ready_rows"),
        "tfe_source_policy_spec_extracted": tfe_source_policy_audit.get("source_policy_spec_extracted"),
        "tfe_pendulum_runner_implemented": tfe_source_policy_audit.get("pendulum_dae_runner_implemented"),
        "tfe_source_grid_compatibility_status": tfe_source_grid_compatibility.get("status"),
        "tfe_source_grid_integer_step_compatible_rows": tfe_source_grid_compatibility.get(
            "integer_step_compatible_rows"
        ),
        "tfe_source_grid_integer_step_incompatible_rows": tfe_source_grid_compatibility.get(
            "integer_step_incompatible_rows"
        ),
        "tfe_source_grid_exact_T_compatible_rows_endpoint_convention_resolved": (
            tfe_source_grid_compatibility.get("endpoint_compatible_rows_source_endpoint_convention_resolved")
        ),
        "tfe_source_grid_endpoint_incompatible_rows_requiring_policy": tfe_source_grid_compatibility.get(
            "endpoint_incompatible_rows_require_source_endpoint_policy"
        ),
        "tfe_source_grid_policy_resolved_for_exact_T_compatible_rows": tfe_source_grid_compatibility.get(
            "source_grid_policy_resolved_for_exact_T_compatible_rows"
        ),
        "tfe_source_grid_endpoint_compatible_row_ids": tfe_source_grid_compatibility.get(
            "source_endpoint_compatible_row_ids"
        ),
        "tfe_source_grid_endpoint_incompatible_row_ids": tfe_source_grid_compatibility.get(
            "source_endpoint_incompatible_row_ids"
        ),
        "tfe_source_grid_policy_resolved_for_full_T10": tfe_source_grid_compatibility.get(
            "source_grid_policy_resolved_for_full_T10"
        ),
        "tfe_source_grid_endpoint_convention_candidate_count": len(
            tfe_source_grid_compatibility.get("endpoint_convention_candidates", [])
        ),
        "tfe_source_grid_endpoint_convention_policies": [
            item.get("policy") for item in tfe_source_grid_compatibility.get("endpoint_convention_candidates", [])
        ],
        "tfe_source_grid_required_to_accept_full_T10_rows": tfe_source_grid_compatibility.get(
            "required_to_accept_full_T10_rows"
        ),
        "tfe_source_grid_source_text_available": tfe_source_grid_compatibility.get(
            "source_text_endpoint_convention_audit", {}
        ).get("source_text_available"),
        "tfe_source_grid_source_text_anchor_count": tfe_source_grid_compatibility.get(
            "source_text_endpoint_convention_audit", {}
        ).get("anchor_count"),
        "tfe_source_grid_algorithm_literal_fixed_h": tfe_source_grid_compatibility.get(
            "source_text_endpoint_convention_audit", {}
        ).get("algorithm_literal_constant_h_until_tn_ge_tfinal"),
        "tfe_source_grid_endpoint_convention_resolved_for_error_sampling": tfe_source_grid_compatibility.get(
            "source_text_endpoint_convention_audit", {}
        ).get("source_endpoint_convention_resolved_for_error_sampling"),
        "tfe_endpoint_sensitivity_schema": tfe_endpoint_sensitivity.get("schema"),
        "tfe_endpoint_sensitivity_status": tfe_endpoint_sensitivity.get("status"),
        "tfe_endpoint_sensitivity_method_count": tfe_endpoint_sensitivity.get("method_count"),
        "tfe_endpoint_sensitivity_policy_count": tfe_endpoint_sensitivity.get("policy_count"),
        "tfe_endpoint_sensitivity_summary_row_count": tfe_endpoint_sensitivity.get("summary_row_count"),
        "tfe_endpoint_sensitivity_raw_row_count": tfe_endpoint_sensitivity.get("raw_row_count"),
        "tfe_endpoint_sensitivity_source_policy_rows_completed": tfe_endpoint_sensitivity.get(
            "source_policy_rows_completed"
        ),
        "tfe_endpoint_sensitivity_external_superiority_claim_allowed": tfe_endpoint_sensitivity.get(
            "external_superiority_claim_allowed"
        ),
        "tfe_endpoint_sensitivity_source_policy_runner_equivalent": tfe_endpoint_sensitivity.get(
            "source_policy_runner_equivalent"
        ),
        "tfe_endpoint_sensitivity_default_1e_4_campaign_invoked": tfe_endpoint_sensitivity.get(
            "execution_policy", {}
        ).get("default_1e_4_campaign_invoked"),
        "tfe_endpoint_sensitivity_run_v047_invoked": tfe_endpoint_sensitivity.get(
            "execution_policy", {}
        ).get("run_v047_invoked"),
        "tfe_endpoint_sensitivity_nominal_h": tfe_endpoint_sensitivity.get("nominal_h"),
        "tfe_endpoint_sensitivity_endpoint_policies": tfe_endpoint_sensitivity.get("endpoint_policies"),
        "tfe_full_t10_coarse_summary_schema": tfe_full_t10_coarse_candidate_summary.get("schema"),
        "tfe_full_t10_coarse_summary_status": tfe_full_t10_coarse_candidate_summary.get("status"),
        "tfe_full_t10_coarse_summary_row_count": tfe_full_t10_coarse_candidate_summary.get("row_count"),
        "tfe_full_t10_coarse_summary_finite_rows": tfe_full_t10_coarse_candidate_summary.get("finite_row_count"),
        "tfe_full_t10_coarse_summary_residual_ok_rows": tfe_full_t10_coarse_candidate_summary.get(
            "residual_ok_row_count"
        ),
        "tfe_full_t10_coarse_summary_source_policy_rows": tfe_full_t10_coarse_candidate_summary.get(
            "source_policy_rows_completed"
        ),
        "tfe_full_t10_coarse_summary_reference_h": tfe_full_t10_coarse_candidate_summary.get("reference_h"),
        "tfe_full_t10_coarse_summary_source_policy_reference_invoked": tfe_full_t10_coarse_candidate_summary.get(
            "source_policy_reference_invoked"
        ),
        "tfe_full_t10_coarse_summary_default_1e_4_campaign_invoked": tfe_full_t10_coarse_candidate_summary.get(
            "default_1e_4_campaign_invoked"
        ),
        "tfe_full_t10_coarse_summary_external_superiority_allowed": tfe_full_t10_coarse_candidate_summary.get(
            "external_superiority_claim_allowed"
        ),
        "tfe_source_pendulum_model_schema": tfe_source_pendulum_model_audit.get("schema"),
        "tfe_source_pendulum_model_status": tfe_source_pendulum_model_audit.get("status"),
        "tfe_source_pendulum_parameter_match": tfe_source_pendulum_model_audit.get(
            "parameter_match_source_spec"
        ),
        "tfe_source_pendulum_parameter_model_implemented": tfe_source_pendulum_model_audit.get(
            "source_pendulum_parameter_model_implemented"
        ),
        "tfe_source_pendulum_frictionless_smoke_implemented": tfe_source_pendulum_model_audit.get(
            "frictionless_planar_rhs_smoke_implemented"
        ),
        "tfe_source_pendulum_absolute_coordinate_dae_residual_smoke_implemented": tfe_source_pendulum_model_audit.get(
            "absolute_coordinate_dae_residual_smoke_implemented"
        ),
        "tfe_source_pendulum_absolute_coordinate_frictional_candidate_dae_smoke_implemented": tfe_source_pendulum_model_audit.get(
            "absolute_coordinate_frictional_candidate_dae_smoke_implemented"
        ),
        "tfe_source_pendulum_source_policy_dae_runner_equivalent": tfe_source_pendulum_model_audit.get(
            "source_policy_dae_runner_equivalent"
        ),
        "tfe_source_pendulum_source_output_time_integration_smoke_implemented": tfe_source_pendulum_model_audit.get(
            "source_output_time_integration_smoke_implemented"
        ),
        "tfe_source_pendulum_source_policy_time_integration_runner_equivalent": tfe_source_pendulum_model_audit.get(
            "source_policy_time_integration_runner_equivalent"
        ),
        "tfe_source_pendulum_source_reference_solution_policy_smoke_implemented": tfe_source_pendulum_model_audit.get(
            "source_reference_solution_policy_smoke_implemented"
        ),
        "tfe_source_pendulum_source_reference_solution_policy_smoke_full_T10": tfe_source_pendulum_model_audit.get(
            "source_reference_solution_policy_smoke_full_T10"
        ),
        "tfe_source_pendulum_source_reference_solution_policy_full_T10_probe_implemented": tfe_source_pendulum_model_audit.get(
            "source_reference_solution_policy_full_T10_probe_implemented"
        ),
        "tfe_source_pendulum_source_reference_solution_policy_full_T10_probe_completed": tfe_source_pendulum_model_audit.get(
            "source_reference_solution_policy_full_T10_probe_completed"
        ),
        "tfe_source_pendulum_source_reference_solution_policy_full_T10_probe_rows_completed": tfe_source_pendulum_model_audit.get(
            "source_reference_solution_policy_full_T10_probe_rows_completed"
        ),
        "tfe_source_pendulum_source_reference_solution_policy_full_T10_probe_steps": tfe_source_pendulum_model_audit.get(
            "source_reference_solution_policy_full_T10_probe_steps"
        ),
        "tfe_source_pendulum_source_reference_solution_policy_full_T10_probe_check_steps": tfe_source_pendulum_model_audit.get(
            "source_reference_solution_policy_full_T10_probe_check_steps"
        ),
        "tfe_source_pendulum_source_reference_solution_policy_full_T10_probe_coordinate_error": tfe_source_pendulum_model_audit.get(
            "source_reference_solution_policy_full_T10_probe_coordinate_error"
        ),
        "tfe_source_pendulum_source_reference_solution_policy_full_T10_probe_velocity_error": tfe_source_pendulum_model_audit.get(
            "source_reference_solution_policy_full_T10_probe_velocity_error"
        ),
        "tfe_source_pendulum_source_comparator_candidate_runners_implemented": tfe_source_pendulum_model_audit.get(
            "source_comparator_candidate_runners_implemented"
        ),
        "tfe_source_pendulum_newmark_beta_candidate_runner_smoke_implemented": tfe_source_pendulum_model_audit.get(
            "newmark_beta_candidate_runner_smoke_implemented"
        ),
        "tfe_source_pendulum_trapezoidal_candidate_runner_smoke_implemented": tfe_source_pendulum_model_audit.get(
            "trapezoidal_candidate_runner_smoke_implemented"
        ),
        "tfe_source_pendulum_source_policy_method_runner_equivalent": tfe_source_pendulum_model_audit.get(
            "source_policy_method_runner_equivalent"
        ),
        "tfe_source_pendulum_tfe_m1_m2_m3_candidate_runner_smoke_implemented": tfe_source_pendulum_model_audit.get(
            "tfe_m1_m2_m3_candidate_runner_smoke_implemented"
        ),
        "tfe_source_pendulum_appendix_b_coefficient_certificate_checked": tfe_source_pendulum_model_audit.get(
            "tfe_appendix_b_coefficient_certificate_checked"
        ),
        "tfe_source_pendulum_appendix_b_coefficient_certificate_rows": tfe_source_pendulum_model_audit.get(
            "tfe_appendix_b_coefficient_certificate_row_count"
        ),
        "tfe_source_pendulum_appendix_b_coefficient_certificate_max_abs_diff": tfe_source_pendulum_model_audit.get(
            "tfe_appendix_b_coefficient_certificate_max_abs_diff"
        ),
        "tfe_source_pendulum_tfe_m1_m2_m3_source_policy_runners_implemented": tfe_source_pendulum_model_audit.get(
            "tfe_m1_m2_m3_source_policy_runners_implemented"
        ),
        "tfe_source_pendulum_gauss6_candidate_smoke_implemented": tfe_source_pendulum_model_audit.get(
            "gauss6_fullva_source_pendulum_candidate_smoke_implemented"
        ),
        "tfe_source_pendulum_gauss6_absolute_coordinate_source_policy_runner_implemented": tfe_source_pendulum_model_audit.get(
            "gauss6_fullva_absolute_coordinate_source_policy_runner_implemented"
        ),
        "tfe_source_pendulum_gauss6_candidate_rows": tfe_source_pendulum_model_audit.get(
            "gauss6_fullva_source_pendulum_candidate_rows"
        ),
        "tfe_source_pendulum_gauss6_candidate_source_policy_rows_completed": tfe_source_pendulum_model_audit.get(
            "gauss6_fullva_source_pendulum_candidate_source_policy_rows_completed"
        ),
        "tfe_source_pendulum_gauss6_candidate_method_equivalent": tfe_source_pendulum_model_audit.get(
            "gauss6_fullva_source_pendulum_candidate_method_equivalent"
        ),
        "tfe_source_pendulum_bounded_source_policy_runner_api_implemented": tfe_source_pendulum_model_audit.get(
            "bounded_source_policy_runner_api_implemented"
        ),
        "tfe_source_pendulum_bounded_source_policy_runner_smoke_implemented": tfe_source_pendulum_model_audit.get(
            "bounded_source_policy_runner_smoke_implemented"
        ),
        "tfe_source_pendulum_bounded_source_policy_runner_rows": tfe_source_pendulum_model_audit.get(
            "bounded_source_policy_runner_rows"
        ),
        "tfe_source_pendulum_bounded_source_policy_runner_full_T10": tfe_source_pendulum_model_audit.get(
            "bounded_source_policy_runner_full_T10"
        ),
        "tfe_source_pendulum_bounded_source_policy_runner_source_policy_rows_completed": tfe_source_pendulum_model_audit.get(
            "bounded_source_policy_runner_source_policy_rows_completed"
        ),
        "tfe_source_pendulum_active_b2_candidate_row_smoke_implemented": tfe_source_pendulum_model_audit.get(
            "active_tfe_b2_candidate_row_smoke_implemented"
        ),
        "tfe_source_pendulum_active_b2_candidate_row_smoke_full_T10": tfe_source_pendulum_model_audit.get(
            "active_tfe_b2_candidate_row_smoke_full_T10"
        ),
        "tfe_source_pendulum_active_b2_source_policy_rows_completed": tfe_source_pendulum_model_audit.get(
            "active_tfe_b2_source_policy_rows_completed"
        ),
        "tfe_source_pendulum_active_b2_full_T10_coarse_probe_implemented": tfe_source_pendulum_model_audit.get(
            "active_tfe_b2_full_T10_coarse_candidate_probe_implemented"
        ),
        "tfe_source_pendulum_active_b2_full_T10_coarse_probe_full_T10": tfe_source_pendulum_model_audit.get(
            "active_tfe_b2_full_T10_coarse_candidate_probe_full_T10"
        ),
        "tfe_source_pendulum_active_b2_full_T10_coarse_probe_source_policy_rows": tfe_source_pendulum_model_audit.get(
            "active_tfe_b2_full_T10_coarse_candidate_probe_source_policy_rows_completed"
        ),
        "tfe_source_pendulum_active_b2_full_T10_coarse_probe_finite_rows": tfe_source_pendulum_model_audit.get(
            "active_tfe_b2_full_T10_coarse_candidate_probe_finite_rows"
        ),
        "tfe_source_pendulum_active_b2_full_T10_coarse_probe_residual_ok_rows": tfe_source_pendulum_model_audit.get(
            "active_tfe_b2_full_T10_coarse_candidate_probe_residual_ok_rows"
        ),
        "tfe_source_pendulum_active_b2_full_T10_coarse_probe_reference_invoked": not tfe_source_pendulum_model_audit.get(
            "active_tfe_b2_full_T10_coarse_candidate_probe_source_policy_reference_not_invoked"
        ),
        "tfe_source_pendulum_active_b2_source_reference_full_T10_probe_implemented": tfe_source_pendulum_model_audit.get(
            "active_tfe_b2_source_reference_full_T10_candidate_probe_implemented"
        ),
        "tfe_source_pendulum_active_b2_source_reference_full_T10_probe_full_T10": tfe_source_pendulum_model_audit.get(
            "active_tfe_b2_source_reference_full_T10_candidate_probe_full_T10"
        ),
        "tfe_source_pendulum_active_b2_source_reference_full_T10_probe_reference_invoked": tfe_source_pendulum_model_audit.get(
            "active_tfe_b2_source_reference_full_T10_candidate_probe_source_policy_reference_invoked"
        ),
        "tfe_source_pendulum_active_b2_source_reference_full_T10_probe_source_policy_rows": tfe_source_pendulum_model_audit.get(
            "active_tfe_b2_source_reference_full_T10_candidate_probe_source_policy_rows_completed"
        ),
        "tfe_source_pendulum_active_b2_source_reference_full_T10_probe_finite_rows": tfe_source_pendulum_model_audit.get(
            "active_tfe_b2_source_reference_full_T10_candidate_probe_finite_rows"
        ),
        "tfe_source_pendulum_active_b2_source_reference_full_T10_probe_residual_ok_rows": tfe_source_pendulum_model_audit.get(
            "active_tfe_b2_source_reference_full_T10_candidate_probe_residual_ok_rows"
        ),
        "tfe_source_pendulum_active_b2_source_reference_full_T10_probe_method_equivalent": tfe_source_pendulum_model_audit.get(
            "active_tfe_b2_source_reference_full_T10_candidate_probe_method_equivalent"
        ),
        "tfe_source_pendulum_tfe_m3_full_T10_formula_probe_implemented": tfe_source_pendulum_model_audit.get(
            "tfe_m3_full_T10_coarse_formula_probe_implemented"
        ),
        "tfe_source_pendulum_tfe_m3_full_T10_formula_probe_full_T10": tfe_source_pendulum_model_audit.get(
            "tfe_m3_full_T10_coarse_formula_probe_full_T10"
        ),
        "tfe_source_pendulum_tfe_m3_full_T10_formula_probe_source_policy_rows": tfe_source_pendulum_model_audit.get(
            "tfe_m3_full_T10_coarse_formula_probe_source_policy_rows_completed"
        ),
        "tfe_source_pendulum_tfe_m3_full_T10_formula_probe_finite_rows": tfe_source_pendulum_model_audit.get(
            "tfe_m3_full_T10_coarse_formula_probe_finite_rows"
        ),
        "tfe_source_pendulum_tfe_m3_full_T10_formula_probe_residual_ok_rows": tfe_source_pendulum_model_audit.get(
            "tfe_m3_full_T10_coarse_formula_probe_residual_ok_rows"
        ),
        "tfe_source_pendulum_tfe_m3_full_T10_formula_probe_expected_order": tfe_source_pendulum_model_audit.get(
            "tfe_m3_full_T10_coarse_formula_probe_formal_expected_order"
        ),
        "tfe_source_pendulum_tfe_m3_full_T10_formula_probe_reference_invoked": not tfe_source_pendulum_model_audit.get(
            "tfe_m3_full_T10_coarse_formula_probe_source_policy_reference_not_invoked"
        ),
        "tfe_source_pendulum_active_b2_candidate_row_count": len(
            tfe_source_pendulum_model_audit.get("active_tfe_b2_candidate_row_smoke", {}).get("rows", [])
        ),
        "tfe_source_pendulum_model_dae_runner_implemented": tfe_source_pendulum_model_audit.get(
            "pendulum_dae_runner_implemented"
        ),
        "tfe_source_pendulum_brown_mcphee_friction_law_implemented": tfe_source_pendulum_model_audit.get(
            "brown_mcphee_friction_law_implemented"
        ),
        "tfe_source_pendulum_brown_mcphee_candidate_friction_law_encoded": tfe_source_pendulum_model_audit.get(
            "brown_mcphee_candidate_friction_law_encoded"
        ),
        "tfe_source_pendulum_brown_mcphee_source_text_anchor_found": tfe_source_pendulum_model_audit.get(
            "brown_mcphee_source_text_anchor", {}
        ).get("source_text_found"),
        "tfe_source_pendulum_brown_mcphee_source_text_names_velocity_model": tfe_source_pendulum_model_audit.get(
            "brown_mcphee_source_text_anchor", {}
        ).get("names_velocity_based_continuous_model"),
        "tfe_source_pendulum_brown_mcphee_source_text_reports_mu_values": tfe_source_pendulum_model_audit.get(
            "brown_mcphee_source_text_anchor", {}
        ).get("reports_mu_static_dynamic"),
        "tfe_source_pendulum_brown_mcphee_published_formula_structure_encoded": tfe_source_pendulum_model_audit.get(
            "brown_mcphee_published_formula_structure_encoded"
        ),
        "tfe_source_pendulum_brown_mcphee_source_code_equivalent_law": tfe_source_pendulum_model_audit.get(
            "brown_mcphee_source_code_equivalent_law"
        ),
        "tfe_source_pendulum_brown_mcphee_transition_velocity_policy_resolved": tfe_source_pendulum_model_audit.get(
            "brown_mcphee_transition_velocity_policy_resolved_from_source"
        ),
        "tfe_source_pendulum_frictional_candidate_smoke_implemented": tfe_source_pendulum_model_audit.get(
            "frictional_planar_candidate_rhs_smoke_implemented"
        ),
        "tfe_source_pendulum_candidate_friction_law_provenance": tfe_source_pendulum_model_audit.get(
            "candidate_friction_law_provenance"
        ),
        "tfe_source_pendulum_error_output_policy_encoded": tfe_source_pendulum_model_audit.get(
            "source_error_norm_and_output_policy_encoded"
        ),
        "tfe_source_pendulum_model_rows_completed": tfe_source_pendulum_model_audit.get(
            "source_policy_rows_completed"
        ),
        "tfe_source_pendulum_setup_subrequirement_closed": tfe_source_pendulum_model_audit.get(
            "closure_boundary", {}
        ).get("can_close_source_pendulum_setup_subrequirement"),
        "tfe_can_close_b2_requirement_now": tfe_source_policy_audit.get("decision", {}).get(
            "can_close_tfe_b2_requirement_now"
        ),
        "tfe_default_1e_4_required": tfe_source_policy_audit.get("execution_policy", {}).get(
            "default_1e_4_required"
        ),
        "tfe_heavy_run_invoked": tfe_source_policy_audit.get("execution_policy", {}).get(
            "heavy_numerical_run_invoked"
        ),
        "tfe_run_v047_invoked": tfe_source_policy_audit.get("execution_policy", {}).get("run_v047_invoked"),
    }
    claim_hygiene_checks = {
        "schema": claim_hygiene.get("schema"),
        "status": claim_hygiene.get("status"),
        "audit_mode": claim_hygiene.get("audit_mode"),
        "allowed_claim": claim_hygiene.get("claim_boundary", {}).get("allowed_claim"),
        "accepted_method": claim_hygiene.get("claim_boundary", {}).get("accepted_method"),
        "accepted_method_order": claim_hygiene.get("claim_boundary", {}).get("accepted_method_order"),
        "comparator_expected_order": claim_hygiene.get("claim_boundary", {}).get("comparator_expected_order"),
        "required_missing_count": claim_hygiene.get("checks", {}).get("required_missing_count"),
        "submission_forbidden_hit_count": claim_hygiene.get("checks", {}).get("submission_forbidden_hit_count"),
        "support_forbidden_hit_count": claim_hygiene.get("checks", {}).get("support_forbidden_hit_count"),
        "source_policy_superiority_claim_allowed": claim_hygiene.get("source_policy_superiority_claim_allowed"),
        "external_superiority_claim": claim_hygiene.get("external_superiority_claim"),
        "default_1e_4_required": claim_hygiene.get("default_1e_4_required"),
        "run_v047_invoked": claim_hygiene.get("run_v047_invoked"),
        "heavy_numerical_run_invoked": claim_hygiene.get("heavy_numerical_run_invoked"),
    }
    paper_code_inventory = python_inventory(PAPER)
    v048_code_inventory = python_inventory(v048_dir)
    combined_python_line_count = paper_code_inventory["line_count"] + v048_code_inventory["line_count"]
    minimal_candidate_python_lines = int(minimal_candidate.get("candidate_python_line_count") or 0)
    minimal_candidate_python_files = int(minimal_candidate.get("candidate_python_file_count") or 0)
    minimal_candidate_code_size_ok = (
        0 < minimal_candidate_python_lines <= REVIEWER_FACING_PYTHON_LINE_LIMIT
        and 0 < minimal_candidate_python_files <= REVIEWER_FACING_PYTHON_FILE_LIMIT
    )
    minimal_candidate_replay_only = minimal_candidate.get("read_only_replay_package") is True
    minimal_candidate_runner_centered = minimal_candidate_replay_only is False
    minimal_candidate_source_policy_ready = (
        result_checks["source_policy_apples_to_apples_external_rows"]
        == result_checks["source_policy_apples_to_apples_external_total_rows"]
    )
    minimal_candidate_proof_ready = proof_checks["proof_gap_closed"] is True
    local_runner_centered_candidate_ready = (
        runner_centered_audit.get("local_runner_centered_candidate_ready") is True
    )
    full_source_policy_runner_package_ready = (
        runner_centered_audit.get("full_source_policy_runner_package_ready") is True
    )
    narrowed_repro_code_archive_ready = (
        narrowed_repro_code_archive.get("status")
        == "narrowed_repro_code_archive_ready_source_policy_open"
        and narrowed_repro_code_archive.get("narrowed_claim_reproducibility_package_ready") is True
        and narrowed_repro_code_archive.get("submission_ready") is False
        and narrowed_repro_code_archive.get("source_policy_rows_closed") == 0
        and narrowed_repro_code_archive.get("source_policy_rows_total") == 40
        and narrowed_repro_code_archive.get("full_source_policy_runner_package_ready") is False
    )
    minimal_submission_code_ready = (
        minimal_candidate.get("submission_ready") is True
        and minimal_candidate_code_size_ok
        and minimal_candidate_runner_centered
        and minimal_candidate_source_policy_ready
        and minimal_candidate_proof_ready
    )
    research_audit_repo_too_large_for_primary_submission = (
        combined_python_line_count > RESEARCH_AUDIT_PRIMARY_SUBMISSION_LINE_LIMIT
    )
    code_bloat_risk_for_submission = (
        research_audit_repo_too_large_for_primary_submission and not minimal_submission_code_ready
    )
    minimal_submission_code_dependency_boundary = {
        "schema": "minimal-submission-code-dependency-boundary-v1",
        "status": (
            "submission_code_ready"
            if minimal_submission_code_ready
            else "narrowed_repro_ready_full_source_policy_package_blocked"
            if local_runner_centered_candidate_ready and narrowed_repro_code_archive_ready
            else "candidate_replay_package_not_runner_or_source_policy_ready"
        ),
        "minimal_reproducible_submission_code_ready": minimal_submission_code_ready,
        "narrowed_repro_code_archive_ready": narrowed_repro_code_archive_ready,
        "narrowed_repro_code_archive_submission_ready": narrowed_repro_code_archive.get("submission_ready"),
        "candidate_code_size_ok": minimal_candidate_code_size_ok,
        "candidate_replay_only": minimal_candidate_replay_only,
        "candidate_runner_centered": minimal_candidate_runner_centered,
        "candidate_source_policy_ready": minimal_candidate_source_policy_ready,
        "candidate_proof_ready": minimal_candidate_proof_ready,
        "local_runner_centered_candidate_ready": local_runner_centered_candidate_ready,
        "full_source_policy_runner_package_ready": full_source_policy_runner_package_ready,
        "source_policy_rows_closed": minimal_candidate.get("source_policy_closed_rows"),
        "source_policy_rows_total": minimal_candidate.get("source_policy_total_rows"),
        "narrowed_archive_source_policy_rows_closed": narrowed_repro_code_archive.get(
            "source_policy_rows_closed"
        ),
        "narrowed_archive_source_policy_rows_total": narrowed_repro_code_archive.get(
            "source_policy_rows_total"
        ),
        "blocking_upstream_gates": [
            "OC4_source_policy_reproduction_rows",
            "OC6_TFE_source_policy_runner",
            "OC12_full_source_policy_runner_archive",
        ],
        "safe_current_package_use": (
            "narrowed_claim_replay_and_audit_provenance_only"
            if local_runner_centered_candidate_ready and narrowed_repro_code_archive_ready
            else "bounded_result_matrix_replay_only_not_runner_centered"
        ),
        "primary_submission_package_allowed": False,
    }
    code_hygiene_checks = {
        "schema": "cmame-code-hygiene-review-v1",
        "status": "research_audit_repository_not_minimal_submission_code",
        "paper_python_file_count": paper_code_inventory["file_count"],
        "paper_python_line_count": paper_code_inventory["line_count"],
        "paper_python_prefix_counts": paper_code_inventory["prefix_counts"],
        "paper_largest_python_files": paper_code_inventory["largest_files"],
        "v048_python_file_count": v048_code_inventory["file_count"],
        "v048_python_line_count": v048_code_inventory["line_count"],
        "v048_python_prefix_counts": v048_code_inventory["prefix_counts"],
        "v048_largest_python_files": v048_code_inventory["largest_files"],
        "combined_python_line_count": combined_python_line_count,
        "research_audit_primary_submission_line_limit": RESEARCH_AUDIT_PRIMARY_SUBMISSION_LINE_LIMIT,
        "research_audit_repo_too_large_for_primary_submission": research_audit_repo_too_large_for_primary_submission,
        "research_audit_repo_primary_submission_allowed": False,
        "research_audit_repo_provenance_only": True,
        "reviewer_facing_python_line_limit": REVIEWER_FACING_PYTHON_LINE_LIMIT,
        "reviewer_facing_python_file_limit": REVIEWER_FACING_PYTHON_FILE_LIMIT,
        "minimal_reproducible_submission_code_ready": minimal_submission_code_ready,
        "minimal_reproducibility_candidate_present": bool(minimal_candidate),
        "minimal_reproducibility_candidate_schema": minimal_candidate.get("schema"),
        "minimal_reproducibility_candidate_status": minimal_candidate.get("status"),
        "minimal_reproducibility_candidate_submission_ready": minimal_candidate.get("submission_ready"),
        "minimal_reproducibility_candidate_file_count": minimal_candidate.get("candidate_file_count"),
        "minimal_reproducibility_candidate_python_file_count": minimal_candidate_python_files,
        "minimal_reproducibility_candidate_python_lines": minimal_candidate_python_lines,
        "minimal_reproducibility_candidate_code_size_ok": minimal_candidate_code_size_ok,
        "minimal_reproducibility_candidate_source_policy_closed_rows": minimal_candidate.get(
            "source_policy_closed_rows"
        ),
        "minimal_reproducibility_candidate_source_policy_total_rows": minimal_candidate.get(
            "source_policy_total_rows"
        ),
        "minimal_reproducibility_candidate_proof_gap_closed": minimal_candidate.get("proof_gap_closed"),
        "minimal_reproducibility_candidate_replay_only": minimal_candidate_replay_only,
        "minimal_reproducibility_candidate_runner_centered": minimal_candidate_runner_centered,
        "local_runner_centered_candidate_ready": local_runner_centered_candidate_ready,
        "narrowed_repro_code_archive_ready": narrowed_repro_code_archive_ready,
        "narrowed_repro_code_archive_status": narrowed_repro_code_archive.get("status"),
        "narrowed_repro_code_archive_submission_ready": narrowed_repro_code_archive.get("submission_ready"),
        "narrowed_repro_code_archive_source_policy_rows_closed": narrowed_repro_code_archive.get(
            "source_policy_rows_closed"
        ),
        "narrowed_repro_code_archive_source_policy_rows_total": narrowed_repro_code_archive.get(
            "source_policy_rows_total"
        ),
        "full_source_policy_runner_package_ready": full_source_policy_runner_package_ready,
        "runner_centered_audit_status": runner_centered_audit.get("status"),
        "minimal_reproducibility_candidate_source_policy_ready": minimal_candidate_source_policy_ready,
        "minimal_reproducibility_candidate_proof_ready": minimal_candidate_proof_ready,
        "minimal_submission_code_dependency_boundary": minimal_submission_code_dependency_boundary,
        "research_audit_repo_useful": True,
        "paper_core_result_table_ready": (
            result_checks["paper_numerical_matrix_schema"] == "paper-numerical-result-matrix-v1"
            and result_checks["paper_numerical_matrix_row_count"] == 44
            and result_checks["paper_numerical_matrix_raw_row_count"] == 132
            and result_checks["result_traceability_closed"] is True
        ),
        "code_bloat_risk_for_submission": code_bloat_risk_for_submission,
        "ra2021_public_baselines_present": (
            external_checks["ra2021_public_order_groups_completed"]
            == external_checks["ra2021_public_order_groups_required"]
            == 12
            and external_checks["ra2021_public_timing_rows_completed"]
            == external_checks["ra2021_public_timing_rows_required"]
            == 12
        ),
        "hi2022_bounded_rows_present": external_checks["hi2022_bounded_ok_row_count"]
        == external_checks["hi2022_bounded_row_count"]
        == 24,
        "tfe_source_policy_runner_implemented": external_checks["tfe_pendulum_runner_implemented"],
        "tfe_source_pendulum_parameter_model_implemented": external_checks[
            "tfe_source_pendulum_parameter_model_implemented"
        ],
        "tfe_source_pendulum_frictionless_smoke_implemented": external_checks[
            "tfe_source_pendulum_frictionless_smoke_implemented"
        ],
        "tfe_source_pendulum_absolute_coordinate_dae_residual_smoke_implemented": external_checks[
            "tfe_source_pendulum_absolute_coordinate_dae_residual_smoke_implemented"
        ],
        "tfe_source_pendulum_source_policy_dae_runner_equivalent": external_checks[
            "tfe_source_pendulum_source_policy_dae_runner_equivalent"
        ],
        "tfe_source_pendulum_source_output_time_integration_smoke_implemented": external_checks[
            "tfe_source_pendulum_source_output_time_integration_smoke_implemented"
        ],
        "tfe_source_pendulum_source_policy_time_integration_runner_equivalent": external_checks[
            "tfe_source_pendulum_source_policy_time_integration_runner_equivalent"
        ],
        "tfe_source_pendulum_source_reference_solution_policy_smoke_implemented": external_checks[
            "tfe_source_pendulum_source_reference_solution_policy_smoke_implemented"
        ],
        "tfe_source_pendulum_source_reference_solution_policy_smoke_full_T10": external_checks[
            "tfe_source_pendulum_source_reference_solution_policy_smoke_full_T10"
        ],
        "tfe_source_pendulum_source_reference_solution_policy_full_T10_probe_implemented": external_checks[
            "tfe_source_pendulum_source_reference_solution_policy_full_T10_probe_implemented"
        ],
        "tfe_source_pendulum_source_reference_solution_policy_full_T10_probe_completed": external_checks[
            "tfe_source_pendulum_source_reference_solution_policy_full_T10_probe_completed"
        ],
        "tfe_source_pendulum_source_reference_solution_policy_full_T10_probe_rows_completed": external_checks[
            "tfe_source_pendulum_source_reference_solution_policy_full_T10_probe_rows_completed"
        ],
        "tfe_source_pendulum_source_reference_solution_policy_full_T10_probe_steps": external_checks[
            "tfe_source_pendulum_source_reference_solution_policy_full_T10_probe_steps"
        ],
        "tfe_source_pendulum_source_reference_solution_policy_full_T10_probe_check_steps": external_checks[
            "tfe_source_pendulum_source_reference_solution_policy_full_T10_probe_check_steps"
        ],
        "tfe_source_pendulum_source_reference_solution_policy_full_T10_probe_coordinate_error": external_checks[
            "tfe_source_pendulum_source_reference_solution_policy_full_T10_probe_coordinate_error"
        ],
        "tfe_source_pendulum_source_reference_solution_policy_full_T10_probe_velocity_error": external_checks[
            "tfe_source_pendulum_source_reference_solution_policy_full_T10_probe_velocity_error"
        ],
        "tfe_source_pendulum_source_comparator_candidate_runners_implemented": external_checks[
            "tfe_source_pendulum_source_comparator_candidate_runners_implemented"
        ],
        "tfe_source_pendulum_newmark_beta_candidate_runner_smoke_implemented": external_checks[
            "tfe_source_pendulum_newmark_beta_candidate_runner_smoke_implemented"
        ],
        "tfe_source_pendulum_trapezoidal_candidate_runner_smoke_implemented": external_checks[
            "tfe_source_pendulum_trapezoidal_candidate_runner_smoke_implemented"
        ],
        "tfe_source_pendulum_source_policy_method_runner_equivalent": external_checks[
            "tfe_source_pendulum_source_policy_method_runner_equivalent"
        ],
        "tfe_source_pendulum_tfe_m1_m2_m3_candidate_runner_smoke_implemented": external_checks[
            "tfe_source_pendulum_tfe_m1_m2_m3_candidate_runner_smoke_implemented"
        ],
        "tfe_source_pendulum_appendix_b_coefficient_certificate_checked": external_checks[
            "tfe_source_pendulum_appendix_b_coefficient_certificate_checked"
        ],
        "tfe_source_pendulum_appendix_b_coefficient_certificate_rows": external_checks[
            "tfe_source_pendulum_appendix_b_coefficient_certificate_rows"
        ],
        "tfe_source_pendulum_appendix_b_coefficient_certificate_max_abs_diff": external_checks[
            "tfe_source_pendulum_appendix_b_coefficient_certificate_max_abs_diff"
        ],
        "tfe_source_pendulum_tfe_m1_m2_m3_source_policy_runners_implemented": external_checks[
            "tfe_source_pendulum_tfe_m1_m2_m3_source_policy_runners_implemented"
        ],
        "tfe_source_pendulum_gauss6_candidate_smoke_implemented": external_checks[
            "tfe_source_pendulum_gauss6_candidate_smoke_implemented"
        ],
        "tfe_source_pendulum_gauss6_absolute_coordinate_source_policy_runner_implemented": external_checks[
            "tfe_source_pendulum_gauss6_absolute_coordinate_source_policy_runner_implemented"
        ],
        "tfe_source_pendulum_gauss6_candidate_rows": external_checks[
            "tfe_source_pendulum_gauss6_candidate_rows"
        ],
        "tfe_source_pendulum_gauss6_candidate_source_policy_rows_completed": external_checks[
            "tfe_source_pendulum_gauss6_candidate_source_policy_rows_completed"
        ],
        "tfe_source_pendulum_gauss6_candidate_method_equivalent": external_checks[
            "tfe_source_pendulum_gauss6_candidate_method_equivalent"
        ],
        "tfe_source_pendulum_bounded_source_policy_runner_smoke_implemented": external_checks[
            "tfe_source_pendulum_bounded_source_policy_runner_smoke_implemented"
        ],
        "tfe_source_pendulum_bounded_source_policy_runner_rows": external_checks[
            "tfe_source_pendulum_bounded_source_policy_runner_rows"
        ],
        "tfe_source_pendulum_bounded_source_policy_runner_full_T10": external_checks[
            "tfe_source_pendulum_bounded_source_policy_runner_full_T10"
        ],
        "tfe_source_pendulum_bounded_source_policy_runner_source_policy_rows_completed": external_checks[
            "tfe_source_pendulum_bounded_source_policy_runner_source_policy_rows_completed"
        ],
        "tfe_source_pendulum_active_b2_candidate_row_smoke_implemented": external_checks[
            "tfe_source_pendulum_active_b2_candidate_row_smoke_implemented"
        ],
        "tfe_source_pendulum_active_b2_candidate_row_smoke_full_T10": external_checks[
            "tfe_source_pendulum_active_b2_candidate_row_smoke_full_T10"
        ],
        "tfe_source_pendulum_active_b2_source_policy_rows_completed": external_checks[
            "tfe_source_pendulum_active_b2_source_policy_rows_completed"
        ],
        "tfe_source_pendulum_active_b2_full_T10_coarse_probe_implemented": external_checks[
            "tfe_source_pendulum_active_b2_full_T10_coarse_probe_implemented"
        ],
        "tfe_source_pendulum_active_b2_full_T10_coarse_probe_full_T10": external_checks[
            "tfe_source_pendulum_active_b2_full_T10_coarse_probe_full_T10"
        ],
        "tfe_source_pendulum_active_b2_full_T10_coarse_probe_source_policy_rows": external_checks[
            "tfe_source_pendulum_active_b2_full_T10_coarse_probe_source_policy_rows"
        ],
        "tfe_source_pendulum_active_b2_full_T10_coarse_probe_finite_rows": external_checks[
            "tfe_source_pendulum_active_b2_full_T10_coarse_probe_finite_rows"
        ],
        "tfe_source_pendulum_active_b2_full_T10_coarse_probe_residual_ok_rows": external_checks[
            "tfe_source_pendulum_active_b2_full_T10_coarse_probe_residual_ok_rows"
        ],
        "tfe_source_pendulum_active_b2_full_T10_coarse_probe_reference_invoked": external_checks[
            "tfe_source_pendulum_active_b2_full_T10_coarse_probe_reference_invoked"
        ],
        "tfe_source_pendulum_active_b2_source_reference_full_T10_probe_implemented": external_checks[
            "tfe_source_pendulum_active_b2_source_reference_full_T10_probe_implemented"
        ],
        "tfe_source_pendulum_active_b2_source_reference_full_T10_probe_full_T10": external_checks[
            "tfe_source_pendulum_active_b2_source_reference_full_T10_probe_full_T10"
        ],
        "tfe_source_pendulum_active_b2_source_reference_full_T10_probe_reference_invoked": external_checks[
            "tfe_source_pendulum_active_b2_source_reference_full_T10_probe_reference_invoked"
        ],
        "tfe_source_pendulum_active_b2_source_reference_full_T10_probe_source_policy_rows": external_checks[
            "tfe_source_pendulum_active_b2_source_reference_full_T10_probe_source_policy_rows"
        ],
        "tfe_source_pendulum_active_b2_source_reference_full_T10_probe_finite_rows": external_checks[
            "tfe_source_pendulum_active_b2_source_reference_full_T10_probe_finite_rows"
        ],
        "tfe_source_pendulum_active_b2_source_reference_full_T10_probe_residual_ok_rows": external_checks[
            "tfe_source_pendulum_active_b2_source_reference_full_T10_probe_residual_ok_rows"
        ],
        "tfe_source_pendulum_active_b2_source_reference_full_T10_probe_method_equivalent": external_checks[
            "tfe_source_pendulum_active_b2_source_reference_full_T10_probe_method_equivalent"
        ],
        "tfe_source_pendulum_tfe_m3_full_T10_formula_probe_implemented": external_checks[
            "tfe_source_pendulum_tfe_m3_full_T10_formula_probe_implemented"
        ],
        "tfe_source_pendulum_tfe_m3_full_T10_formula_probe_full_T10": external_checks[
            "tfe_source_pendulum_tfe_m3_full_T10_formula_probe_full_T10"
        ],
        "tfe_source_pendulum_tfe_m3_full_T10_formula_probe_source_policy_rows": external_checks[
            "tfe_source_pendulum_tfe_m3_full_T10_formula_probe_source_policy_rows"
        ],
        "tfe_source_pendulum_tfe_m3_full_T10_formula_probe_finite_rows": external_checks[
            "tfe_source_pendulum_tfe_m3_full_T10_formula_probe_finite_rows"
        ],
        "tfe_source_pendulum_tfe_m3_full_T10_formula_probe_residual_ok_rows": external_checks[
            "tfe_source_pendulum_tfe_m3_full_T10_formula_probe_residual_ok_rows"
        ],
        "tfe_source_pendulum_tfe_m3_full_T10_formula_probe_expected_order": external_checks[
            "tfe_source_pendulum_tfe_m3_full_T10_formula_probe_expected_order"
        ],
        "tfe_source_pendulum_tfe_m3_full_T10_formula_probe_reference_invoked": external_checks[
            "tfe_source_pendulum_tfe_m3_full_T10_formula_probe_reference_invoked"
        ],
        "tfe_source_pendulum_active_b2_candidate_row_count": external_checks[
            "tfe_source_pendulum_active_b2_candidate_row_count"
        ],
        "tfe_source_pendulum_error_output_policy_encoded": external_checks[
            "tfe_source_pendulum_error_output_policy_encoded"
        ],
        "tfe_source_pendulum_brown_mcphee_candidate_friction_law_encoded": external_checks[
            "tfe_source_pendulum_brown_mcphee_candidate_friction_law_encoded"
        ],
        "tfe_source_pendulum_brown_mcphee_source_text_anchor_found": external_checks[
            "tfe_source_pendulum_brown_mcphee_source_text_anchor_found"
        ],
        "tfe_source_pendulum_brown_mcphee_published_formula_structure_encoded": external_checks[
            "tfe_source_pendulum_brown_mcphee_published_formula_structure_encoded"
        ],
        "tfe_source_pendulum_brown_mcphee_source_code_equivalent_law": external_checks[
            "tfe_source_pendulum_brown_mcphee_source_code_equivalent_law"
        ],
        "tfe_source_pendulum_frictional_candidate_smoke_implemented": external_checks[
            "tfe_source_pendulum_frictional_candidate_smoke_implemented"
        ],
        "source_policy_closed_rows": result_checks["source_policy_apples_to_apples_external_rows"],
        "source_policy_total_rows": result_checks["source_policy_apples_to_apples_external_total_rows"],
        "recommended_submission_code_shape": (
            "extract a small reproducibility package around the 44-row result matrix, "
            "the four-example runner inputs, and the selected RA2021/HI2022/TFE source-policy runners; "
            "keep the many audit builders as supplementary provenance, not the primary submission API"
        ),
    }
    closeout_actionability_checks = {
        "schema": "cmame-closeout-actionability-v1",
        "status": "future_full_source_policy_reintroduction_after_narrowed_claim_closure",
        "submission_ready": False,
        "narrowed_claim_subcheck_passed": True,
        "full_source_policy_package_ready": False,
        "ordered_gates": [
            {
                "rank": 1,
                "gate": "Future B4 source-policy work-precision reintroduction",
                "status": "future_full_source_policy_only",
                "closed_rows": result_checks["source_policy_apples_to_apples_external_rows"],
                "total_rows": result_checks["source_policy_apples_to_apples_external_total_rows"],
                "blocking_reason": (
                    "source-policy rows remain 0/40; this blocks global submission readiness "
                    "and any external/source-policy claims, while the narrowed common-reference "
                    "subcheck remains only subsidiary"
                ),
                "next_evidence": [
                    "publication-grade work-precision curves on accepted baselines",
                    "matched Newton/Jacobian/linear-solve timing tables",
                    "clear source-policy or explicit-demotion labels for every baseline curve",
                ],
            },
            {
                "rank": 2,
                "gate": "Future B7 source-policy figure reintroduction",
                "status": "future_full_source_policy_only",
                "closed_rows": result_checks["figure_set_b7_preflight_closed_preconditions"],
                "total_rows": (
                    result_checks["figure_set_b7_preflight_closed_preconditions"]
                    + result_checks["figure_set_b7_preflight_open_dependencies"]
                ),
                "blocking_reason": "13 current-scope figures are integrated; source-policy baseline/work-precision figures are future-scope only",
                "next_evidence": [
                    "baseline comparison figures tied to source-policy or demoted-claim labels",
                    "clean work-precision figures once B4 evidence exists",
                    "visible limitation explanation for non-superiority source-policy boundaries",
                ],
            },
            {
                "rank": 3,
                "gate": "Future B6 full source-policy prose pass",
                "status": "future_full_source_policy_only",
                "closed_rows": result_checks["prose_b6_preflight_closed_preconditions"],
                "total_rows": (
                    result_checks["prose_b6_preflight_closed_preconditions"]
                    + result_checks["prose_b6_preflight_open_dependencies"]
                ),
                "blocking_reason": "current narrowed-claim prose is closed; a broader source-policy prose pass is future-scope only",
                "next_evidence": [
                    "final baseline-aware prose pass",
                    "move remaining machine-verification details to reproducibility material",
                    "submission-ready limitation and source-policy wording",
                ],
            },
            {
                "rank": 4,
                "gate": "Future full source-policy reproducibility package",
                "status": "future_full_source_policy_only",
                "closed_rows": code_hygiene_checks["minimal_reproducibility_candidate_file_count"],
                "total_rows": code_hygiene_checks["minimal_reproducibility_candidate_file_count"],
                "blocking_reason": (
                    "accepted-row local runner candidate is ready, but the minimal replay candidate is not the "
                    "full source-policy package and source-policy/presentation gates are open"
                    if local_runner_centered_candidate_ready
                    else "current minimal candidate is replay-only and source-policy/presentation gates are open"
                ),
                "next_evidence": [
                    "keep the local accepted-row runner synchronized with B6 evidence",
                    "source-policy runner scripts for the accepted external suites",
                    "proof and result artifacts copied with a reviewer-readable manifest",
                ],
            },
        ],
        "first_gate_to_work": "Future B4 source-policy work-precision reintroduction",
        "source_policy_closure_routes": [
            {
                "route": "source_policy_execution",
                "status": "open_requires_explicit_opt_in",
                "claim_after_route": "external_superiority_can_be_reconsidered_only_after_rows_close",
                "requires_default_1e_4": False,
                "requires_explicit_1e_4_opt_in": True,
                "current_closed_rows": result_checks["source_policy_apples_to_apples_external_rows"],
                "current_total_rows": result_checks["source_policy_apples_to_apples_external_total_rows"],
                "required_actions": [
                    "run or promote RA2021 local Gauss6 rows under the public-code source policy",
                    "encode or demote the original TFE pendulum source-policy rows",
                    "keep VP2024 and HI2022 demotions as non-win claim-boundary decisions",
                ],
            },
            {
                "route": "claim_demotion",
                "status": "applied_to_claim_boundary_b2_closed_b4_still_open",
                "claim_after_route": "formal_order_and_common_reference_diagnostics_only",
                "audit_schema": external_checks["claim_demotion_audit_schema"],
                "audit_status": external_checks["claim_demotion_audit_status"],
                "audit_route_b_ready": external_checks["claim_demotion_audit_route_b_ready"],
                "audit_promoted_to_blocker_gate": external_checks[
                    "claim_demotion_audit_route_b_promoted_to_blocker_gate"
                ],
                "audit_b2_b4_gate_closed_by_this_artifact": external_checks[
                    "claim_demotion_audit_b2_b4_gate_closed_by_this_artifact"
                ],
                "audit_b2_gate_closed_by_route_b": external_checks[
                    "claim_demotion_audit_b2_gate_closed_by_route_b"
                ],
                "audit_b4_gate_closed_by_route_b": external_checks[
                    "claim_demotion_audit_b4_gate_closed_by_route_b"
                ],
                "audit_source_policy_rows_closed": external_checks[
                    "claim_demotion_audit_source_policy_rows_closed"
                ],
                "audit_source_policy_total_rows": external_checks[
                    "claim_demotion_audit_source_policy_total_rows"
                ],
                "application_contract_schema": external_checks["claim_demotion_route_b_contract_schema"],
                "application_contract_ready_to_promote": external_checks[
                    "claim_demotion_route_b_ready_to_promote"
                ],
                "application_contract_safe_to_flip_flags": external_checks[
                    "claim_demotion_route_b_safe_to_flip_flags"
                ],
                "application_contract_satisfied_steps": external_checks[
                    "claim_demotion_route_b_satisfied_steps"
                ],
                "application_contract_total_steps": external_checks["claim_demotion_route_b_total_steps"],
                "application_contract_unsatisfied_steps": external_checks[
                    "claim_demotion_route_b_unsatisfied_steps"
                ],
                "application_contract_creates_numerical_wins": external_checks[
                    "claim_demotion_route_b_creates_numerical_wins"
                ],
                "requires_default_1e_4": False,
                "requires_explicit_1e_4_opt_in": False,
                "current_demoted_suites": sorted(
                    external_checks["b2_remaining_work_demoted_suite_counts"].keys()
                ),
                "additional_demotions_needed": external_checks[
                    "claim_demotion_audit_additional_demotions_needed"
                ],
                "required_actions": [
                    "keep RA2021, HI2022, VP2024, and TFE out of external-superiority claims",
                    "keep all 44 common-reference order/error cells as diagnostics",
                    "retain the formal order comparison against the TFE m=3 target",
                    "rerun the review agent and blocker gate after any future manuscript claim-boundary edit",
                ],
            },
        ],
        "do_not_spend_on_before_source_policy": [
            "final prose polishing",
            "submission-ready claim language",
            "large default h=1e-4 campaigns without explicit opt-in",
        ],
    }
    citation_integrity = submission_integrity.get("citation_key_integrity", {})
    submission_sidecars = submission_integrity.get("submission_sidecars", {})
    submission_boundary = submission_integrity.get("claim_boundary", {})
    reference_summary = submission_integrity.get("reference_metadata_audit", {})
    submission_integrity_checks = {
        "schema": submission_integrity.get("schema"),
        "status": submission_integrity.get("status"),
        "submission_ready": submission_integrity.get("submission_ready"),
        "local_integrity_passed": submission_integrity.get("local_integrity_passed"),
        "external_reference_web_verification_complete": submission_integrity.get(
            "external_reference_web_verification_complete"
        ),
        "external_reference_web_verification_required_for_final_submission": submission_integrity.get(
            "external_reference_web_verification_required_for_final_submission"
        ),
        "reference_metadata_schema": reference_summary.get("schema"),
        "reference_metadata_status": reference_summary.get("status"),
        "reference_metadata_reference_count": reference_summary.get("reference_count"),
        "reference_metadata_doi_reference_count": reference_summary.get("doi_reference_count"),
        "reference_metadata_doi_verified_count": reference_summary.get("doi_metadata_verified_count"),
        "reference_metadata_doi_unresolved_count": reference_summary.get("doi_metadata_unresolved_count"),
        "reference_metadata_local_non_doi_count": reference_summary.get("local_non_doi_reference_count"),
        "reference_metadata_non_doi_verified_count": reference_summary.get("non_doi_metadata_verified_count"),
        "reference_metadata_non_doi_count": reference_summary.get("non_doi_reference_count"),
        "reference_metadata_artifact_schema": reference_metadata.get("schema"),
        "reference_metadata_artifact_status": reference_metadata.get("status"),
        "main_cited_key_count": citation_integrity.get("main_cited_key_count"),
        "flat_cited_key_count": citation_integrity.get("flat_cited_key_count"),
        "main_bibitem_count": citation_integrity.get("main_bibitem_count"),
        "flat_bibitem_count": citation_integrity.get("flat_bibitem_count"),
        "main_and_flat_citation_keys_match": citation_integrity.get("main_and_flat_citation_keys_match"),
        "main_and_flat_bibitem_keys_match": citation_integrity.get("main_and_flat_bibitem_keys_match"),
        "main_dangling_citation_keys": citation_integrity.get("main_dangling_citation_keys"),
        "flat_dangling_citation_keys": citation_integrity.get("flat_dangling_citation_keys"),
        "main_orphan_bibitem_keys": citation_integrity.get("main_orphan_bibitem_keys"),
        "flat_orphan_bibitem_keys": citation_integrity.get("flat_orphan_bibitem_keys"),
        "main_unresolved_log_lines": citation_integrity.get("main_unresolved_log_lines"),
        "flat_unresolved_log_lines": citation_integrity.get("flat_unresolved_log_lines"),
        "pdf_references_heading_present": citation_integrity.get("pdf_references_heading_present"),
        "flat_pdf_references_heading_present": citation_integrity.get("flat_pdf_references_heading_present"),
        "declaration_tokens_present": submission_sidecars.get("declaration_tokens_present"),
        "flat_declaration_tokens_present": submission_sidecars.get("flat_declaration_tokens_present"),
        "highlight_count": submission_sidecars.get("highlight_count"),
        "flat_highlight_count": submission_sidecars.get("flat_highlight_count"),
        "cover_letter_mentions_journal": submission_sidecars.get("cover_letter_mentions_journal"),
        "cover_letter_mentions_recommended_pdf": submission_sidecars.get("cover_letter_mentions_recommended_pdf"),
        "local_citation_key_integrity_closed": submission_boundary.get("local_citation_key_integrity_closed"),
        "bibliographic_metadata_web_verified": submission_boundary.get("bibliographic_metadata_web_verified"),
        "submission_integrity_gate_closed": submission_boundary.get("submission_integrity_gate_closed"),
    }
    pdf_style_review_checks = {
        "schema": pdf_style_review.get("schema"),
        "status": pdf_style_review.get("status"),
        "ars_route": pdf_style_review.get("ars_route"),
        "submission_ready": pdf_style_review.get("submission_ready"),
        "submission_ready_scope": pdf_style_review.get("submission_ready_scope"),
        "submission_standard_scope": pdf_style_review.get("submission_standard_scope"),
        "submission_standard_role": pdf_style_review.get("submission_standard_role"),
        "global_submission_standard_met": pdf_style_review.get("global_submission_standard_met"),
        "readiness_boundary": pdf_style_review.get("readiness_boundary", {}),
        "remaining_gate_scope": pdf_style_review.get("remaining_gate_scope", {}),
        "reference_text_read": pdf_style_review.get("reference_text_read"),
        "manuscript_text_read": pdf_style_review.get("manuscript_text_read"),
        "flat_manuscript_text_read": pdf_style_review.get("flat_manuscript_text_read"),
        "reference_line_count": pdf_style_review.get("reference_inventory", {}).get("line_count"),
        "reference_figure_count": pdf_style_review.get("reference_inventory", {}).get("figure_count"),
        "reference_table_count": pdf_style_review.get("reference_inventory", {}).get("table_count"),
        "reference_algorithm_count": pdf_style_review.get("reference_inventory", {}).get("algorithm_count"),
        "reference_work_precision_mentions": pdf_style_review.get("reference_inventory", {}).get(
            "work_precision_mentions"
        ),
        "manuscript_line_count": pdf_style_review.get("manuscript_inventory", {}).get("line_count"),
        "manuscript_figure_count": pdf_style_review.get("manuscript_inventory", {}).get("figure_count"),
        "manuscript_table_count": pdf_style_review.get("manuscript_inventory", {}).get("table_count"),
        "manuscript_theorem_count": pdf_style_review.get("manuscript_inventory", {}).get("theorem_count"),
        "manuscript_proof_token_count": pdf_style_review.get("manuscript_inventory", {}).get("proof_token_count"),
        "manuscript_audit_residue_mentions": pdf_style_review.get("manuscript_inventory", {}).get(
            "audit_residue_mentions"
        ),
        "reference_audit_residue_mentions": pdf_style_review.get("reference_inventory", {}).get(
            "audit_residue_mentions"
        ),
        "reference_algorithm_boxes_present": pdf_style_review.get("reference_style_features", {}).get(
            "algorithm_boxes_present"
        ),
        "reference_numerical_experiments_section": pdf_style_review.get("reference_style_features", {}).get(
            "numerical_experiments_section"
        ),
        "reference_work_precision_figures": pdf_style_review.get("reference_style_features", {}).get(
            "work_precision_figures"
        ),
        "reference_data_availability_and_declarations": pdf_style_review.get("reference_style_features", {}).get(
            "data_availability_and_declarations"
        ),
        "manuscript_all_method_matrix_visible": pdf_style_review.get("manuscript_style_features", {}).get(
            "all_method_matrix_visible"
        ),
        "manuscript_theorem_present": pdf_style_review.get("manuscript_style_features", {}).get("theorem_present"),
        "manuscript_proofs_present": pdf_style_review.get("manuscript_style_features", {}).get("proofs_present"),
        "manuscript_figure_set_present": pdf_style_review.get("manuscript_style_features", {}).get(
            "figure_set_present"
        ),
        "source_policy_rows_closed": pdf_style_review.get("source_policy_rows_closed"),
        "source_policy_total_rows": pdf_style_review.get("source_policy_total_rows"),
        "external_superiority_claim_allowed": pdf_style_review.get("external_superiority_claim_allowed"),
        "direct_pc2_proof_gap_closed": pdf_style_review.get(
            "direct_pc2_proof_gap_closed", pdf_style_review.get("proof_gap_closed")
        ),
        "proof_gap_closed": pdf_style_review.get("proof_gap_closed"),
        "proof_gap_closed_scope": pdf_style_review.get("proof_gap_closed_scope", DIRECT_PC2_SCOPE),
        "proof_gap_closed_reading_rule": DIRECT_PC2_READING_RULE,
        "stage_residual_O_h7_implementation_defect_proved": pdf_style_review.get(
            "stage_residual_O_h7_implementation_defect_proved"
        ),
        "eta_h_O_h7_solver_policy_evidence": pdf_style_review.get("eta_h_O_h7_solver_policy_evidence"),
        "figure_set_b7_closed": pdf_style_review.get("figure_set_b7_closed"),
        "prose_b6_closed": pdf_style_review.get("prose_b6_closed"),
        "minimal_reproducibility_submission_ready": pdf_style_review.get(
            "minimal_reproducibility_submission_ready"
        ),
        "blocking_finding_ids": [item.get("id") for item in pdf_style_review.get("blocking_findings", [])],
        "submission_standard_met": pdf_style_review.get("submission_standard_met"),
        "quality_review_passed": pdf_style_review.get("quality_review_passed"),
        "decision": pdf_style_review.get("decision"),
    }

    global_submission_standard_candidate_met = (
        all(
            value is True
            for key, value in format_checks.items()
            if key.endswith("_present")
            or key in {"elsarticle_preprint", "cmame_journal_marker", "abstract_within_limit", "keywords_within_limit"}
        )
        and result_checks["paper_includes_latest_common_reference_result"] is True
        and result_checks["pdf_text_includes_latest_common_reference_result"] is True
        and result_checks["manuscript_includes_all_method_matrix"] is True
        and result_checks["pdf_text_includes_all_method_matrix"] is True
        and result_checks["all_method_matrix_all_methods_visible"] is True
        and result_checks["all_method_matrix_all_examples_visible"] is True
        and result_checks["proof_conditional_boundary_visible"] is True
        and result_checks["publication_figure_boundary_visible"] is True
        and result_checks["manuscript_includes_source_policy_diagnosis"] is True
        and result_checks["pdf_text_includes_source_policy_diagnosis"] is True
        and result_checks["manuscript_includes_all_example_source_policy_audit"] is True
        and result_checks["pdf_text_includes_all_example_source_policy_audit"] is True
        and result_checks["manuscript_includes_minimal_reproducibility_boundary"] is True
        and result_checks["pdf_text_includes_minimal_reproducibility_boundary"] is True
        and result_checks["manuscript_includes_comparison_reconciliation"] is True
        and result_checks["pdf_text_includes_comparison_reconciliation"] is True
        and result_checks["all_method_matrix_complete"] is True
        and result_checks["paper_numerical_matrix_schema"] == "paper-numerical-result-matrix-v1"
        and result_checks["paper_numerical_matrix_row_count"] == 44
        and result_checks["paper_numerical_matrix_raw_row_count"] == 132
        and result_checks["paper_numerical_matrix_source_policy_external_superiority_allowed"] is False
        and result_checks["paper_numerical_matrix_direct_error_superiority_allowed"] is False
        and result_checks["four_example_dashboard_local_evidence_coverage_examples"] == 4
        and result_checks["four_example_dashboard_accepted_method_dynamic_order_example_count"] == 2
        and result_checks["four_example_dashboard_mechanism_coverage_example_count"] == 2
        and result_checks["four_example_dashboard_closed_loop_true_dynamic_order_closed_examples"] == 2
        and result_checks["four_example_dashboard_closed_loop_true_dynamic_stage_oracle_used"] is False
        and result_checks["result_traceability_velocity_cells_checked"] == 44
        and result_checks["result_traceability_main_tex_cells"] == 44
        and result_checks["result_traceability_flat_tex_cells"] == 44
        and result_checks["result_traceability_main_pdf_cells"] == 44
        and result_checks["result_traceability_flat_pdf_cells"] == 44
        and result_checks["result_traceability_closed"] is True
        and result_checks["result_traceability_source_policy_reproduction_closed"] is False
        and result_checks["all_method_disposition_nonlocal_cells"] == 40
        and result_checks["all_method_disposition_order_wins"] == 40
        and result_checks["all_method_disposition_error_wins"] == 40
        and result_checks["all_method_disposition_source_policy_closed_rows"] == 0
        and result_checks["all_method_disposition_source_policy_open_rows"] == 40
        and result_checks["all_method_disposition_flagged_nonlocal_rows"] == 15
        and result_checks["all_method_disposition_source_policy_superiority_allowed"] is False
        and result_checks["all_examples_audited"] is True
        and result_checks["all_examples_sanity_cell_count"] == 44
        and result_checks["all_examples_external_superiority_allowed"] is False
        and result_checks["order_recomputation_all_summary_orders_recomputed"] is True
        and result_checks["order_recomputation_mismatch_count"] == 0
        and result_checks["order_recomputation_external_superiority_allowed"] is False
        and result_checks["visual_legibility_b5_closed"] is True
        and result_checks["visual_legibility_b7_open"] is False
        and result_checks["visual_pdf_captions_present"] is True
        and result_checks["prose_main_body_machine_token_count"] == 0
        and result_checks["prose_flat_main_body_machine_token_count"] == 0
        and result_checks["prose_artifact_filenames_confined_to_appendix"] is True
        and result_checks["prose_b6_closed"] is True
        and result_checks["global_policy_passed"] is True
        and claim_hygiene_checks["status"] == "pass"
        and claim_hygiene_checks["allowed_claim"] == "conditional_formal_order_comparison"
        and claim_hygiene_checks["required_missing_count"] == 0
        and claim_hygiene_checks["submission_forbidden_hit_count"] == 0
        and claim_hygiene_checks["support_forbidden_hit_count"] == 0
        and code_hygiene_checks["minimal_reproducible_submission_code_ready"] is True
        and code_hygiene_checks["code_bloat_risk_for_submission"] is False
        and code_hygiene_checks["tfe_source_policy_runner_implemented"] is True
        and code_hygiene_checks["source_policy_closed_rows"] == code_hygiene_checks["source_policy_total_rows"]
        and submission_integrity_checks["local_integrity_passed"] is True
        and submission_integrity_checks["external_reference_web_verification_complete"] is True
        and submission_integrity_checks["submission_integrity_gate_closed"] is True
        and pdf_style_review_checks["submission_standard_met"] is True
        and pdf_style_review_checks["quality_review_passed"] is True
        and pdf_style_review_checks["source_policy_rows_closed"] == pdf_style_review_checks["source_policy_total_rows"]
        and pdf_style_review_checks["proof_gap_closed"] is True
        and pdf_style_review_checks["figure_set_b7_closed"] is True
        and pdf_style_review_checks["prose_b6_closed"] is True
        and pdf_style_review_checks["minimal_reproducibility_submission_ready"] is True
        and external_checks["source_policy_recheck_required"] is False
        and external_checks["source_policy_diagnosis_external_superiority_allowed"] is True
        and external_checks["suite_disposition_b2_can_close_now"] is True
        and external_checks["suite_disposition_b4_can_close_now"] is True
        and external_checks["source_policy_closure_b2_can_close_now"] is True
        and external_checks["source_policy_closure_b4_can_close_now"] is True
        and external_checks["source_policy_closure_external_superiority_allowed"] is True
        and external_checks["vp2024_all_four_examples_checked"] is True
        and external_checks["vp2024_source_policy_code_path_unresolved_rows"] == 4
        and external_checks["vp2024_common_reference_local_order_wins"] == 4
        and external_checks["vp2024_common_reference_local_error_wins"] == 4
        and external_checks["vp2024_large_step_noncontrolling"] is True
        and external_checks["vp2024_distinct_public_code_path_found"] is False
        and external_checks["vp2024_proxy_is_source_policy_reproduction"] is False
        and external_checks["vp2024_heavy_run_invoked"] is False
        and proof_checks["proof_closure_proof_gap_closed"] is True
        and proof_checks["proof_claim_traceability_submission_ready"] is True
        and proof_checks["proof_closure_stage_residual_O_h7_implementation_defect_proved"] is True
        and proof_checks["proof_closure_eta_h_O_h7_solver_policy_evidence"] is True
        and objective_completion.get("objective_complete") is True
        and not open_findings
        and manifest.get("submission_ready") is True
        and manifest.get("quality_review_passed") is True
    )
    global_submission_standard_met = global_submission_standard_candidate_met
    full_source_policy_submission_standard_met = global_submission_standard_met
    narrowed_submission_standard_met = (
        blocker.get("submission_ready") is False
        and blocker.get("submission_ready_under_narrowed_claim") is True
        and blocker.get("quality_review_passed") is True
        and not open_findings
        and pdf_style_review_checks["submission_standard_met"] is True
        and pdf_style_review_checks["quality_review_passed"] is True
        and pdf_style_review_checks["source_policy_rows_closed"] == 0
        and pdf_style_review_checks["source_policy_total_rows"] == 40
        and pdf_style_review_checks["external_superiority_claim_allowed"] is False
        and pdf_style_review_checks["proof_gap_closed"] is True
        and pdf_style_review_checks["figure_set_b7_closed"] is True
        and pdf_style_review_checks["prose_b6_closed"] is True
    )
    global_open_findings = objective_blocking_findings(objective_completion)
    global_open_blocker_ids = [str(item["id"]) for item in global_open_findings]
    cmame_blocker_gate_open_findings = open_findings
    input_artifact_relative_paths = [
        "main_cmame.tex",
        "main_cmame.txt",
        "cmame_submission_flat/main_cmame_submission.tex",
        "cmame_submission_flat/main_cmame_submission.txt",
        "CMAME_SUBMISSION_READINESS_REVIEW.md",
        "OBJECTIVE_COMPLETION_AUDIT.json",
        "FULL_SOURCE_POLICY_RUNNER_ARCHIVE_GAP_AUDIT.json",
        "CMAME_STRICT_PROOF_AUDIT.json",
        "PROOF_CLAIM_TRACEABILITY_AUDIT.json",
        "RESULT_TO_MANUSCRIPT_TRACEABILITY_AUDIT.json",
        "PAPER_RESULT_PACK.json",
        "PAPER_NUMERICAL_RESULT_MATRIX.json",
        "FOUR_EXAMPLE_SOURCE_POLICY_DASHBOARD.json",
        "SOURCE_POLICY_ROW_CLOSURE_LEDGER.json",
        "TFE_SOURCE_POLICY_ROW_AUDIT.json",
        "TFE_RUNNER_CONTRACT_PREFLIGHT_CERTIFICATE.json",
        "TFE_SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_CERTIFICATE.json",
        "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260614.json",
        "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260620.json",
        "RA_HI_SOURCE_POLICY_POST_EXECUTION_ATTEMPT_CERTIFICATE.json",
        "RA_HI_SOURCE_POLICY_OUTPUT_INVENTORY.json",
        "RA_HI_SOURCE_POLICY_CLOSEOUT_CHECKLIST.json",
        "RA_HI_SOURCE_POLICY_PROMOTION_BLOCKER_MATRIX.json",
        "HI2022_RA_HALF_DOUBLE_REPAIR_ATTEMPT_CERTIFICATE.json",
        "B4_SOURCE_POLICY_POST_EXECUTION_AUDIT.json",
        "B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json",
        "B4_SOURCE_POLICY_EXECUTION_HANDOFF_PACKAGE.json",
        "CMAME_MINIMAL_REPRODUCIBILITY_CANDIDATE_MANIFEST.json",
        "CMAME_RUNNER_CENTERED_REPRODUCIBILITY_AUDIT.json",
        "CMAME_NARROWED_REPRO_CODE_ARCHIVE_MANIFEST.json",
        "CMAME_PDF_STYLE_REVIEW_AUDIT.json",
        "CMAME_SUBMISSION_INTEGRITY_AUDIT.json",
        "REFERENCE_METADATA_AUDIT.json",
        "SUBMISSION_ARTIFACT_MANIFEST.json",
        "CMAME_REPRODUCIBILITY_PACKAGE_MANIFEST.json",
        "../v048_cross_paper_same_test_benchmarks/results/global_comparison_policy_audit.json",
    ]
    input_artifact_provenance = {
        "hash_algorithm": "sha256",
        "timestamp_policy": "deterministic_no_wall_clock_timestamp",
        "input_artifacts_read": [
            artifact_snapshot(PAPER / relative_path)
            for relative_path in input_artifact_relative_paths
        ],
    }
    stale_token_scan = {
        "objective_oc9_stale_next_to_close_present": any(
            item.get("id") == "OC9"
            and item.get("status") == "satisfied"
            and "finish external reference web verification" in str(item.get("next_to_close", ""))
            for item in objective_completion.get("requirements", [])
        ),
        "readiness_review_declares_historical_context": (
            "historical quality review" in readiness_review_text
            and "Historical decision before narrowed-claim closure" in readiness_review_text
        ),
        "readiness_review_delegates_current_global_decision": (
            "current package-facing global decision is recorded" in readiness_review_text
            and "do not submit globally yet" in readiness_review_text
        ),
    }
    opt_in_boundary = {
        "packet_path": "B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json",
        "exact_required_phrase": b4_execution_opt_in_packet.get("required_user_approval_statement"),
        "packet_does_not_authorize_execution": b4_execution_opt_in_packet.get(
            "packet_does_not_authorize_execution"
        ),
        "explicit_user_opt_in_required_before_any_command": b4_execution_opt_in_packet.get(
            "explicit_user_opt_in_required_before_any_command"
        ),
        "forbidden_without_opt_in": [
            "B4 source-policy execution commands",
            "run_v048.py source-policy rows requiring --allow-source-policy-1e-4",
            "HI2022 full-T8 source-policy candidate execution shards",
            "any command promoted by the B4 packet as source-policy execution",
        ],
    }
    b4_guarded_driver_phrase = "verified authorized guarded-driver execution"
    b4_post_execution_authorized = (
        b4_post_execution_audit.get("verified_authorized_execution_recorded") is True
    )
    b4_post_execution_evidence_sentence = (
        f"B4 post-execution audit records {b4_guarded_driver_phrase} and existing ready-command "
        "artifacts, but promotes 0/40 rows"
        if b4_post_execution_authorized
        else "B4 post-execution audit records existing ready-command artifacts but no verified "
        "authorized execution, and promotes 0/40 rows"
    )
    b4_post_execution_conclusion_sentence = (
        f"The B4 post-execution audit now records {b4_guarded_driver_phrase} with existing "
        "ready-command artifacts; all expected outputs are present, but it promotes zero of 40 "
        "source-policy rows. "
        if b4_post_execution_authorized
        else "The B4 post-execution audit now records existing ready-command artifacts without "
        "verified authorized guarded-driver execution; all expected outputs are present, but it "
        "promotes zero of 40 source-policy rows. "
    )
    global_review_dimensions = [
        {
            "dimension": "method_contribution",
            "verdict": "pass_under_narrowed_claim",
            "global_effect": "supports_main_method_claim_not_global_submission_ready",
            "evidence": [
                "132-row Lie-group Gauss6/FullVA residual described in manuscript/PDF",
                "claim hygiene accepts Gauss6/FullVA conditional formal-order comparison",
                "result-to-manuscript traceability closes all 44 common-reference velocity cells",
            ],
            "artifact_anchors": [
                artifact_anchor(
                    "main_cmame.tex",
                    tex_label=r"\label{sec:method}",
                    quoted_token="132-row residual",
                    interpretation="method definition is anchored in the manuscript method section",
                ),
                artifact_anchor(
                    "RESULT_TO_MANUSCRIPT_TRACEABILITY_AUDIT.json",
                    json_pointer="/coverage/velocity_cells_checked",
                    quoted_token="44",
                    interpretation="accepted common-reference velocity cells are traced into manuscript/PDF",
                ),
            ],
            "blocking_boundary": "none_for_narrowed_method_claim",
        },
        {
            "dimension": "proof_and_theorem",
            "verdict": "conditional_pass_global_boundaries_retained",
            "global_effect": "proof writing is traceable but theorem-level submission boundaries remain",
            "evidence": [
                "direct residual-bridge/Kantorovich PC2 route closed",
                "accepted direct Newton-Euler dynamic rows closed 36/0",
                "B1 AD-expanded implementation-path certificate closes 4752 derivative cells for implementation-oracle scope while the non-active primitive/global symbolic-oracle completion record remains open",
            ],
            "artifact_anchors": [
                artifact_anchor(
                    "main_cmame.tex",
                    tex_label=r"\label{thm:g6fullva-order}",
                    quoted_token="conditional sixth-order smooth-path",
                    interpretation="the theorem statement is the proof-scope anchor",
                ),
                artifact_anchor(
                    "PROOF_CLAIM_TRACEABILITY_AUDIT.json",
                    json_pointer="/remaining_claim_boundary/status",
                    quoted_token="theorem_conditions_retained_not_submission_ready",
                    interpretation="proof traceability keeps retained theorem interfaces visible",
                ),
                artifact_anchor(
                    "CMAME_STRICT_PROOF_AUDIT.json",
                    json_pointer="/status",
                    quoted_token="strict_conditional_residual_bridge_proof_audited_b3_closed_submission_not_ready",
                    interpretation="strict proof audit is closed only under conditional/global-boundary scope",
                ),
            ],
            "blocking_boundary": "eta_h solver-policy evidence and residual-to-error theorem for mechanism rows remain retained",
        },
        {
            "dimension": "numerical_validation",
            "verdict": "partial_global_acceptance",
            "global_effect": "supports order and mechanism coverage only within bounded/local evidence scope",
            "evidence": [
                "four-example dashboard records local evidence coverage 4/4",
                "accepted method dynamic-order evidence is limited to single_pendulum and double_pendulum",
                "four_link and slider_crank are closed-loop mechanism-coverage/coarse-candidate rows",
                "all-method common-reference matrix covers 44 cells from 132 raw rows",
            ],
            "artifact_anchors": [
                artifact_anchor(
                    "PAPER_NUMERICAL_RESULT_MATRIX.json",
                    json_pointer="/row_count",
                    quoted_token="44",
                    interpretation="numerical matrix records all method/example result cells",
                ),
                artifact_anchor(
                    "FOUR_EXAMPLE_SOURCE_POLICY_DASHBOARD.json",
                    json_pointer="/status",
                    quoted_token="source_policy_dynamic_order_open",
                    interpretation="four-example numerical evidence is separated from source-policy dynamic-order closure",
                ),
            ],
            "blocking_boundary": "source-policy dynamic-order examples remain 0/4",
        },
        {
            "dimension": "comparison_and_source_policy",
            "verdict": "blocked_for_global_submission",
            "global_effect": "external-superiority and same-source comparison claims are not allowed",
            "evidence": [
                "external-suite demotion ledger removes all suites from external-superiority scope",
                "source-policy row closure ledger records 0/40 closed rows",
                b4_post_execution_evidence_sentence,
            ],
            "artifact_anchors": [
                artifact_anchor(
                    "SOURCE_POLICY_ROW_CLOSURE_LEDGER.json",
                    json_pointer="/coverage/rows_source_policy_closed",
                    quoted_token="0",
                    interpretation="source-policy row ledger keeps external/source-policy claims open",
                ),
                artifact_anchor(
                    "B4_SOURCE_POLICY_POST_EXECUTION_AUDIT.json",
                    json_pointer="/source_policy_rows_closed",
                    quoted_token="0",
                    interpretation="existing B4 ready-command artifacts do not promote source-policy rows",
                ),
            ],
            "blocking_boundary": "OC4 source-policy reproduction and OC6 original TFE runner completion remain open",
        },
        {
            "dimension": "reproducibility_and_code_package",
            "verdict": "blocked_for_global_submission",
            "global_effect": "candidate replay/local-runner artifacts are useful but not a full submission source package",
            "evidence": [
                "10-file replay candidate with one 158-line Python core is present",
                "local accepted-row runner candidate is compact and executable",
                "research/audit repository is classified as provenance-only, not primary submission code",
            ],
            "artifact_anchors": [
                artifact_anchor(
                    "CMAME_MINIMAL_REPRODUCIBILITY_CANDIDATE_MANIFEST.json",
                    json_pointer="/status",
                    quoted_token="minimal_reproducibility_candidate_present",
                    interpretation="compact replay package exists but is not the full source-policy package",
                ),
                artifact_anchor(
                    "CMAME_RUNNER_CENTERED_REPRODUCIBILITY_AUDIT.json",
                    json_pointer="/full_source_policy_runner_package_ready",
                    quoted_token="false",
                    interpretation="runner-centered audit retains the OC12 package boundary",
                ),
            ],
            "blocking_boundary": "OC12 full source-policy runner archive remains open after OC4/OC6",
        },
        {
            "dimension": "manuscript_style_and_integrity",
            "verdict": "pass_as_subsidiary_narrowed_subcheck",
            "global_effect": "format, PDF-style, reference metadata, and sidecars pass locally but cannot override global blockers",
            "evidence": [
                "PDF-style audit reads reference, main manuscript, and flat manuscript texts",
                "submission-integrity audit verifies citation/bibitem parity and sidecars",
                "reference metadata audit verifies all DOI and non-DOI entries",
            ],
            "artifact_anchors": [
                artifact_anchor(
                    "CMAME_PDF_STYLE_REVIEW_AUDIT.json",
                    json_pointer="/status",
                    quoted_token="pdf_read_review_passed_narrowed_claim_subcheck_global_boundary_retained",
                    interpretation="PDF-style review passes only as a narrowed subcheck",
                ),
                artifact_anchor(
                    "CMAME_SUBMISSION_INTEGRITY_AUDIT.json",
                    json_pointer="/external_reference_web_verification_complete",
                    quoted_token="true",
                    interpretation="reference/integrity checks are closed without overriding global blockers",
                ),
            ],
            "blocking_boundary": (
                "no style/integrity blocker; global OC blockers are source-policy/package "
                "items, while proof boundaries remain retained theorem conditions"
            ),
        },
    ]
    global_reviewer_assessment = {
        "top_level_verdict": "do_not_submit_global",
        "primary_paper_line": (
            "Gauss6/FullVA method and strict conditional proof are the paper core; "
            "source-policy audit material is boundary evidence, not the contribution"
        ),
        "claim_hierarchy": [
            {
                "rank": 1,
                "claim": "Gauss6/FullVA residual method",
                "reviewer_status": "main_claim_strongest",
                "reason": (
                    "Lie-group rotations, lower-pair constraints, FullVA rows, and "
                    "Newton-Euler dynamics are solved in one square stage residual"
                ),
            },
            {
                "rank": 2,
                "claim": "conditional sixth-order smooth-path theorem",
                "reviewer_status": "strong_conditional_claim_retained",
                "reason": (
                    "strict proof artifacts and manuscript ledgers support the conditional theorem, "
                    "while eta_h solver-policy and residual-to-error boundaries remain global"
                ),
            },
            {
                "rank": 3,
                "claim": "dynamic-order numerical evidence",
                "reviewer_status": "accepted_with_scope",
                "reason": (
                    "smooth-chain and pendulum-style rows support order evidence; closed-loop "
                    "mechanism rows are mechanism-coverage evidence unless source-policy dynamic "
                    "order is closed"
                ),
            },
            {
                "rank": 4,
                "claim": "formal TFE comparison",
                "reviewer_status": "appendix_or_diagnostic_only",
                "reason": (
                    "TFE m=3 is a formal order-five comparator target; no same-source "
                    "external-superiority claim is allowed while source-policy rows are 0/40"
                ),
            },
            {
                "rank": 5,
                "claim": "source-policy/reproducibility audit",
                "reviewer_status": "boundary_and_diagnostic_only",
                "reason": (
                    "audit artifacts prevent overclaiming but do not replace OC4/OC6/OC12 "
                    "global submission readiness"
                ),
            },
        ],
        "evidence_tiering": [
            "dynamic-order rows support the order claim",
            "mechanism-coverage rows support constraint and reaction consistency",
            "diagnostic rows expose boundary, source-policy, and package gaps",
        ],
        "global_blocker_priority": [
            "OC4 source-policy reproduction rows",
            "OC6 original TFE source-policy runner",
            "OC12 full source-policy runner package",
        ],
        "narrowed_subcheck_is_not_global_review": True,
        "global_review_rule": (
            "The review agent must lead with global submission readiness and evidence hierarchy, "
            "then record the narrowed-claim subcheck as subsidiary."
        ),
    }
    global_substantive_findings = [
        {
            "id": "GF1",
            "severity": "strength",
            "finding": "Main contribution is coherent and should lead the paper",
            "global_review_judgment": (
                "The monolithic Lie-group Gauss6/FullVA residual is the strongest paper line; "
                "it combines rotations, lower-pair constraints, FullVA rows, and Newton-Euler "
                "dynamics in one square stage solve."
            ),
            "required_action": "Keep this as the first-order narrative and contribution anchor.",
            "blocking_ids": [],
            "claim_scope": "main_method_claim_under_narrowed_global_boundary",
            "safe_disposition": "lead_the_paper_with_method_contribution",
            "artifact_anchors": [
                artifact_anchor(
                    "main_cmame.tex",
                    tex_label=r"\label{sec:method}",
                    quoted_token="132-row residual",
                    interpretation="manuscript defines the monolithic Gauss6/FullVA residual",
                ),
                artifact_anchor(
                    "main_cmame.txt",
                    pdf_text_token="Gauss6/FullVA",
                    quoted_token="Gauss6/FullVA",
                    interpretation="compiled PDF exposes the method name to reviewers",
                ),
            ],
        },
        {
            "id": "GF2",
            "severity": "conditional_pass",
            "finding": "Proof strength is acceptable only with explicit retained theorem interfaces",
            "global_review_judgment": (
                "The theorem can remain strict and detailed: P5 is discharged by the direct route; "
                "P1, P2, and P3 are retained theorem interfaces; P6 is a separate "
                "solver-scale interface; P4's binding convention is retained while "
                "its 96-row certificate is proved; P7 is an output nonclaim boundary, "
                "not a theorem input. The direct residual certificate and any separate "
                "primitive/Taylor certificate are route-exclusive same-branch certificates, "
                "so they cannot be mixed to lower constants, remove P6, or prove a P7 residual-to-error transfer theorem. "
                "The theorem statement itself consumes only one residual-value certificate; "
                "any future primitive/Taylor certificate may only replace the accepted direct "
                "certificate by proving a new same-tuple 132-row residual-value bound."
            ),
            "required_action": (
                "Preserve the proof-interface tables, route-exclusivity boundary, "
                "theorem-level residual-certificate exclusivity, and P-partition in "
                "the theorem-facing review."
            ),
            "blocking_ids": [
                "theorem_level_eta_h_solver_policy_evidence",
                "closed_residual_to_error_theorem_for_mechanism_rows",
            ],
            "claim_scope": "conditional_sixth_order_theorem_with_retained_interfaces",
            "safe_disposition": "retain_detailed_proof_without_unconditional_order_claim",
            "artifact_anchors": [
                artifact_anchor(
                    "PROOF_CLAIM_TRACEABILITY_AUDIT.json",
                    json_pointer="/remaining_claim_boundary",
                    quoted_token="P1,P2,P3,P4,P6",
                    interpretation="Theorem-interface partition is recorded in the proof traceability audit",
                ),
                artifact_anchor(
                    "PROOF_CLAIM_TRACEABILITY_AUDIT.json",
                    json_pointer="/route_exclusivity_boundary",
                    quoted_token="route_exclusivity_boundary",
                    interpretation="Traceability audit records direct/primitive route-exclusivity as a nonmixing boundary",
                ),
                artifact_anchor(
                    "PROOF_CLAIM_TRACEABILITY_AUDIT.json",
                    json_pointer="/theorem_residual_certificate_exclusivity",
                    quoted_token="theorem_residual_certificate_exclusivity",
                    interpretation="Traceability audit records that the theorem statement consumes only one residual-value certificate",
                ),
                artifact_anchor(
                    "main_cmame.tex",
                    tex_label=r"\label{lem:full-132-row-residual-bridge}",
                    quoted_token="Full 132-row residual-defect certificate bridge",
                    interpretation="new formal bridge lemma carries the 132-row residual handoff",
                ),
            ],
        },
        {
            "id": "GF3",
            "severity": "scope_boundary",
            "finding": "Numerical evidence must be tiered by claim strength",
            "global_review_judgment": (
                "Dynamic-order rows support the order claim, closed-loop mechanism rows support "
                "coverage and reaction/constraint consistency, and residual/source-policy rows "
                "remain diagnostic."
            ),
            "required_action": "Do not let four-link or slider-crank local evidence imply source-policy high order.",
            "blocking_ids": ["source_policy_dynamic_order_examples_0_of_4"],
            "claim_scope": "dynamic_order_rows_separated_from_mechanism_coverage_and_diagnostics",
            "safe_disposition": "present_closed_loop_rows_as_coverage_not_source_policy_order",
            "artifact_anchors": [
                artifact_anchor(
                    "PAPER_NUMERICAL_RESULT_MATRIX.json",
                    json_pointer="/paper_direct_error_superiority_allowed",
                    quoted_token="false",
                    interpretation="numerical matrix blocks direct source-policy/error claims",
                ),
                artifact_anchor(
                    "RESULT_TO_MANUSCRIPT_TRACEABILITY_AUDIT.json",
                    json_pointer="/coverage/source_policy_closed_nonlocal_rows",
                    quoted_token="0",
                    interpretation="traceability audit keeps nonlocal source-policy closure at zero",
                ),
            ],
        },
        {
            "id": "GF4",
            "severity": "global_blocker",
            "finding": "TFE and external comparisons are diagnostic, not a selling point",
            "global_review_judgment": (
                "The TFE material can compare formal order targets, but 0/40 source-policy rows "
                "means no same-source or external-superiority claim is available."
            ),
            "required_action": "Keep TFE/source-policy material in boundary, diagnostic, or appendix roles.",
            "blocking_ids": ["OC4", "OC6", "source_policy_rows_0_of_40"],
            "claim_scope": "formal_order_comparator_only_no_external_superiority",
            "safe_disposition": "demote_TFE_and_external_comparisons_to_diagnostic_or_appendix_roles",
            "artifact_anchors": [
                artifact_anchor(
                    "SOURCE_POLICY_ROW_CLOSURE_LEDGER.json",
                    json_pointer="/coverage/rows_source_policy_closed",
                    quoted_token="0",
                    interpretation="row ledger prevents external-superiority promotion",
                ),
                artifact_anchor(
                    "TFE_SOURCE_POLICY_ROW_AUDIT.json",
                    json_pointer="/status",
                    quoted_token="source_policy_spec_extracted_runner_rows_not_closed",
                    interpretation="TFE source-policy runner remains open",
                ),
            ],
        },
        {
            "id": "GF5",
            "severity": "blocking",
            "finding": "Global submission readiness is still blocked",
            "global_review_judgment": (
                "The narrowed proof/method package can pass as a bounded subcheck, but OC4, OC6, "
                "and OC12 dominate the whole-paper CMAME submission decision."
            ),
            "required_action": "Do not submit globally until OC4/OC6/OC12 are closed or the target scope changes.",
            "blocking_ids": ["OC4", "OC6", "OC12"],
            "claim_scope": "whole_paper_cmame_submission_standard",
            "safe_disposition": "do_not_submit_global",
            "artifact_anchors": [
                artifact_anchor(
                    "OBJECTIVE_COMPLETION_AUDIT.json",
                    json_pointer="/summary/blocking_open_count",
                    quoted_token="3",
                    interpretation="objective audit records three global blockers",
                ),
                artifact_anchor(
                    "OBJECTIVE_COMPLETION_AUDIT.json",
                    json_pointer="/requirements",
                    quoted_token="OC4,OC6,OC12",
                    interpretation="global blocker IDs dominate narrowed blocker-gate passes",
                ),
            ],
        },
    ]
    global_editorial_decision = {
        "decision": "submit_global" if global_submission_standard_met else "do_not_submit_global",
        "scope": "whole_paper_cmame_submission_standard",
        "review_basis": [
            "method contribution, proof/theorem, numerical validation, comparison/source-policy, reproducibility/code package, and manuscript integrity are reviewed together",
            "global objective-completion blockers dominate any local or narrowed blocker-gate pass",
            "the narrowed-claim result is recorded only as a subsidiary bounded subcheck",
        ],
        "ranked_global_blockers": global_open_blocker_ids,
        "non_overriding_subcheck": "narrowed_claim_blocker_gate_pass_does_not_override_global_decision",
        "safe_current_disposition": (
            "do not submit globally; use the narrowed result only to support bounded method/proof "
            "and common-reference diagnostic claims"
        ),
    }
    global_review_frame = "whole_paper_cmame_submission_standard_not_local_artifact_checklist"
    global_blocker_hierarchy = [
        {
            "rank": 1,
            "class": "global_submission_blockers",
            "ids": global_open_blocker_ids,
            "effect": "do_not_submit_global",
            "dominates_narrowed_claim": True,
        },
        {
            "rank": 2,
            "class": "retained_theorem_boundaries",
            "ids": [
                "theorem_level_eta_h_solver_policy_evidence",
                "closed_residual_to_error_theorem_for_mechanism_rows",
            ],
            "effect": "conditional_proof_only",
            "dominates_narrowed_claim": False,
        },
        {
            "rank": 3,
            "class": "partial_numerical_scope",
            "ids": ["source_policy_dynamic_order_examples_0_of_4", "source_policy_rows_0_of_40"],
            "effect": "no_external_or_source_policy_claim",
            "dominates_narrowed_claim": False,
        },
        {
            "rank": 4,
            "class": "non_overriding_local_passes",
            "ids": ["B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8"],
            "effect": "narrowed_claim_only",
            "dominates_narrowed_claim": False,
        },
    ]
    global_review_dimension_evidence = {
        item["dimension"]: item["evidence"] for item in global_review_dimensions
    }
    global_review_dimension_artifact_anchors = {
        item["dimension"]: item["artifact_anchors"] for item in global_review_dimensions
    }
    global_submission_decision_basis = {
        item["dimension"]: {
            "verdict": item["verdict"],
            "global_effect": item["global_effect"],
            "blocking_boundary": item["blocking_boundary"],
            "artifact_anchors": item["artifact_anchors"],
        }
        for item in global_review_dimensions
    }
    global_review_findings = [
        {
            "id": item["id"],
            "type": "global_substantive_review",
            "scope": "whole_paper_cmame_submission_standard",
            "severity": item["severity"],
            "finding": item["finding"],
            "judgment": item["global_review_judgment"],
            "required_action": item["required_action"],
            "blocking_ids": item["blocking_ids"],
            "safe_disposition": item["safe_disposition"],
            "artifact_anchors": item["artifact_anchors"],
        }
        for item in global_substantive_findings
    ]
    global_review_findings.extend(
        {
            "id": item["id"],
            "type": "global_blocking_requirement",
            "scope": "whole_paper_cmame_submission_standard",
            "severity": item["severity"],
            "finding": item.get("requirement") or item.get("area") or item["id"],
            "judgment": "This objective-completion requirement blocks the top-level global CMAME submission decision.",
            "required_action": finding_required_text(item),
            "blocking_ids": [item["id"]],
            "safe_disposition": "do_not_submit_global",
            "artifact_anchors": [
                artifact_anchor(
                    "OBJECTIVE_COMPLETION_AUDIT.json",
                    json_pointer="/requirements",
                    quoted_token=str(item["id"]),
                    interpretation="objective audit records this whole-paper global blocker",
                )
            ],
        }
        for item in global_open_findings
    )
    source_policy_scope = runner_centered_audit.get("source_policy_scope", {})
    global_review_semantic_invariants = {
        "contract": "whole_paper_global_review_contract",
        "top_level_decision_matches_objective_completion": (
            (objective_completion.get("objective_complete") is True and global_submission_standard_met is True)
            or (objective_completion.get("objective_complete") is not True and global_submission_standard_met is False)
        ),
        "decision_is_do_not_submit_global_iff_objective_incomplete": (
            (objective_completion.get("objective_complete") is False)
            == (global_editorial_decision["decision"] == "do_not_submit_global")
        ),
        "all_blocking_objective_requirements_reported": (
            sorted(global_open_blocker_ids)
            == sorted(
                str(item.get("id"))
                for item in objective_completion.get("requirements", [])
                if item.get("blocking_for_goal_completion") is True and item.get("status") != "satisfied"
            )
        ),
        "blocking_objective_requirement_ids": global_open_blocker_ids,
        "global_findings_include_all_blocking_requirements": (
            sorted(global_open_blocker_ids)
            == sorted(
                str(item.get("id"))
                for item in global_review_findings
                if item.get("type") == "global_blocking_requirement"
            )
        ),
        "narrowed_claim_does_not_override_global_decision": (
            narrowed_submission_standard_met is True and global_submission_standard_met is False
        ),
        "b4_opt_in_boundary_retained": (
            b4_execution_opt_in_packet.get("packet_does_not_authorize_execution") is True
            and b4_execution_opt_in_packet.get("explicit_user_opt_in_required_before_any_command") is True
        ),
        "run_v047_invoked": bool(
            b4_row_readiness_ledger.get("run_v047_invoked")
            or tfe_source_policy_audit.get("run_v047_invoked")
            or tfe_dae_runner_contract_gap_audit.get("run_v047_invoked")
        ),
        "heavy_run_invoked": bool(
            four_example_dashboard.get("heavy_numerical_run_invoked")
            or b4_row_readiness_ledger.get("heavy_numerical_run_invoked")
            or tfe_source_policy_audit.get("heavy_run_invoked")
        ),
        "source_policy_rows_closed": source_policy_scope.get("source_policy_closed_rows"),
        "source_policy_total_rows": source_policy_scope.get("source_policy_total_rows"),
        "source_policy_rows_closed_text": (
            f"{source_policy_scope.get('source_policy_closed_rows')}/"
            f"{source_policy_scope.get('source_policy_total_rows')}"
        ),
        "accepted_source_policy_dynamic_order_examples": source_policy_scope.get(
            "accepted_source_policy_dynamic_order_examples"
        ),
        "accepted_source_policy_dynamic_order_examples_text": (
            f"{source_policy_scope.get('accepted_source_policy_dynamic_order_examples')}/4"
        ),
        "full_source_policy_runner_package_ready": runner_centered_audit.get(
            "full_source_policy_runner_package_ready"
        ),
        "global_comparison_policy_artifact_included": (
            global_policy.get("schema") == "global-comparison-policy-audit-v1"
            and global_policy.get("paper_direct_error_superiority_claim_allowed") is False
        ),
        "submission_manifest_narrowed_boundary_matches_reproducibility_manifest": (
            submission_manifest_boundary[
                "narrowed_archive_boundary_matches_reproducibility_manifest"
            ]
        ),
        "submission_manifest_narrowed_boundary_status": submission_manifest_boundary[
            "narrowed_archive_boundary_status"
        ],
        "submission_manifest_narrowed_boundary_source_policy_closed_ratio": (
            submission_manifest_boundary[
                "narrowed_archive_boundary_source_policy_closed_ratio"
            ]
        ),
        "submission_manifest_narrowed_boundary_full_archive_usable": (
            submission_manifest_boundary[
                "narrowed_archive_boundary_current_archive_usable_as_full_source_policy_runner_archive"
            ]
        ),
        "submission_manifest_narrowed_boundary_source_policy_execution_allowed_now": (
            submission_manifest_boundary[
                "narrowed_archive_boundary_source_policy_execution_allowed_now"
            ]
        ),
        "submission_manifest_narrowed_boundary_exact_b4_opt_in_required_for_execution": (
            submission_manifest_boundary[
                "narrowed_archive_boundary_exact_b4_opt_in_required_for_execution"
            ]
        ),
    }
    narrowed_claim_subcheck_disposition = (
        "bounded_subcheck_satisfied_not_global_submit"
        if narrowed_submission_standard_met
        else "bounded_subcheck_failed_not_global_submit"
    )
    legacy_narrowed_claim_decision = (
        "submit_under_narrowed_claim" if narrowed_submission_standard_met else "do_not_submit_narrowed_claim"
    )
    review_evidence_summary = {
        "objective_status": objective_completion.get("status"),
        "objective_complete": objective_completion.get("objective_complete"),
        "submission_ready": objective_completion.get("submission_ready"),
        "open_blocker_count": len(global_open_findings),
        "open_blocker_ids": global_open_blocker_ids,
        "objective_blocker_required_to_close_by_id": objective_blocker_required_to_close_by_id,
        "objective_blocker_safe_next_actions_by_id": objective_blocker_safe_next_actions_by_id,
        "objective_blocker_opt_in_required_actions_by_id": objective_blocker_opt_in_required_actions_by_id,
        "source_policy_apples_to_apples_external": (
            f"{source_policy_scope.get('source_policy_closed_rows')}/"
            f"{source_policy_scope.get('source_policy_total_rows')}"
        ),
        "accepted_source_policy_dynamic_order_examples": (
            f"{source_policy_scope.get('accepted_source_policy_dynamic_order_examples')}/4"
        ),
        "tfe_runner_contract_preflight": (
            f"{tfe_runner_contract_preflight.get('status')}/"
            f"{tfe_runner_contract_preflight.get('callable_contract_count')}/"
            f"{tfe_runner_contract_preflight.get('entrypoint_count')}/"
            f"{tfe_runner_contract_preflight.get('candidate_backed_contract_count')}/"
            f"{tfe_runner_contract_preflight.get('source_policy_rows_completed')}/"
            f"{tfe_runner_contract_preflight.get('source_policy_execution_block_count')}"
        ),
        "oc12_archive_tfe_preflight": (
            f"{objective_summary.get('full_source_policy_runner_archive_gap_tfe_runner_contract_preflight_status')}/"
            f"{objective_summary.get('full_source_policy_runner_archive_gap_tfe_runner_contract_preflight_entrypoints')}/"
            f"{objective_summary.get('full_source_policy_runner_archive_gap_tfe_runner_contract_preflight_candidate_backed')}/"
            f"{objective_summary.get('full_source_policy_runner_archive_gap_tfe_runner_contract_preflight_source_policy_rows_completed')}/"
            f"{objective_summary.get('full_source_policy_runner_archive_gap_tfe_runner_contract_preflight_execution_blocks')}"
        ),
        "oc12_archive_action_boundary": (
            f"{objective_summary.get('full_source_policy_runner_archive_gap_safe_without_b4_opt_in_count')}/"
            f"{objective_summary.get('full_source_policy_runner_archive_gap_opt_in_required_action_count')}/"
            f"{objective_summary.get('full_source_policy_runner_archive_gap_source_policy_execution_allowed_now')}/"
            f"{objective_summary.get('full_source_policy_runner_archive_gap_source_policy_execution_invoked')}/"
            f"{objective_summary.get('full_source_policy_runner_archive_gap_exact_b4_opt_in_required_for_execution')}/"
            f"{objective_summary.get('full_source_policy_runner_archive_gap_opt_in_required_command_count')}/"
            f"{objective_summary.get('full_source_policy_runner_archive_gap_opt_in_required_mapped_external_rows')}"
        ),
        "oc6_reopen_latest_external_probe": (
            f"{full_source_policy_runner_archive_gap.get('oc6_source_equivalent_reopen_readiness_latest_external_probe_date')}/"
            f"{full_source_policy_runner_archive_gap.get('oc6_source_equivalent_reopen_readiness_latest_external_probe_count')}/"
            f"{full_source_policy_runner_archive_gap.get('oc6_source_equivalent_reopen_readiness_latest_external_probe_positive_artifact_rows')}/"
            f"{full_source_policy_runner_archive_gap.get('oc6_source_equivalent_reopen_readiness_latest_external_probe_source_policy_rows_closed')}/"
            f"{full_source_policy_runner_archive_gap.get('oc6_source_equivalent_reopen_readiness_latest_external_probe_access_limited_count')}/"
            f"{full_source_policy_runner_archive_gap.get('oc6_source_equivalent_reopen_readiness_latest_external_probe_global_absence_proved')}/"
            f"{full_source_policy_runner_archive_gap.get('oc6_source_equivalent_reopen_readiness_latest_external_probe_reopen_triggered')}"
        ),
        "full_source_policy_runner_package_ready": runner_centered_audit.get(
            "full_source_policy_runner_package_ready"
        ),
        "minimal_submission_code_dependency_boundary_status": code_hygiene_checks.get(
            "minimal_submission_code_dependency_boundary", {}
        ).get("status"),
        "minimal_submission_code_dependency_safe_use": code_hygiene_checks.get(
            "minimal_submission_code_dependency_boundary", {}
        ).get("safe_current_package_use"),
        "source_policy_execution_handoff_status": b4_execution_handoff.get("status"),
        "source_policy_execution_handoff_authorized": b4_execution_handoff.get(
            "execution_authorized"
        ),
        "source_policy_execution_handoff_commands_not_run": b4_execution_handoff.get(
            "commands_not_run_by_handoff"
        ),
        "source_policy_execution_handoff_command_traceability_summary": (
            b4_command_traceability_summary
        ),
        "source_policy_execution_handoff_unique_mapped_row_count": (
            b4_command_traceability_summary.get("unique_mapped_row_count")
        ),
        "source_policy_execution_handoff_ra_hi_unique_row_count": (
            b4_command_traceability_summary.get("ra_hi_unique_row_count")
        ),
        "source_policy_execution_handoff_traced_command_row_reference_total": (
            b4_command_traceability_summary.get("traced_command_row_reference_total")
        ),
        "source_policy_execution_handoff_declared_mapped_row_reference_total": (
            b4_command_traceability_summary.get("declared_mapped_row_reference_total")
        ),
        "source_policy_execution_handoff_declared_vs_traced_mismatch_count": (
            b4_command_traceability_summary.get("declared_vs_traced_mismatch_count")
        ),
        "source_policy_execution_handoff_terminal_rows_with_command_refs": (
            b4_command_traceability_summary.get("terminal_rows_with_command_refs")
        ),
        "source_policy_execution_handoff_traceability_closed_rows": (
            b4_command_traceability_summary.get("source_policy_closed_rows")
        ),
        "source_policy_execution_handoff_traceability_promotion_ready_rows": (
            b4_command_traceability_summary.get("promotion_ready_rows")
        ),
        "submission_manifest_narrowed_archive_boundary_status": (
            submission_manifest_boundary["narrowed_archive_boundary_status"]
        ),
        "submission_manifest_narrowed_archive_boundary_source_policy_closed_ratio": (
            submission_manifest_boundary[
                "narrowed_archive_boundary_source_policy_closed_ratio"
            ]
        ),
        "submission_manifest_narrowed_archive_boundary_matches_reproducibility_manifest": (
            submission_manifest_boundary[
                "narrowed_archive_boundary_matches_reproducibility_manifest"
            ]
        ),
        "submission_manifest_narrowed_archive_boundary_current_archive_usable_as_full_source_policy_runner_archive": (
            submission_manifest_boundary[
                "narrowed_archive_boundary_current_archive_usable_as_full_source_policy_runner_archive"
            ]
        ),
        "submission_manifest_narrowed_archive_boundary_source_policy_execution_allowed_now": (
            submission_manifest_boundary[
                "narrowed_archive_boundary_source_policy_execution_allowed_now"
            ]
        ),
        "submission_manifest_narrowed_archive_boundary_exact_b4_opt_in_required_for_execution": (
            submission_manifest_boundary[
                "narrowed_archive_boundary_exact_b4_opt_in_required_for_execution"
            ]
        ),
        "narrowed_claim_subcheck_disposition": narrowed_claim_subcheck_disposition,
        "decision": global_editorial_decision["decision"],
    }

    report = {
        "schema": "cmame-submission-review-agent-report-v1",
        "agent": "read_only_cmame_submission_review_agent",
        "ars_route": "academic-paper-reviewer/full plus research-pipeline submission-readiness gate",
        "read_only": True,
        "input_artifact_provenance": input_artifact_provenance,
        "stale_token_scan": stale_token_scan,
        "opt_in_boundary": opt_in_boundary,
        "submission_standard_met": global_submission_standard_met,
        "submission_standard_scope": "global_submission_standard",
        "review_scope": "global_submission_standard_review",
        "top_level_review_decision_scope": "global",
        "global_submission_standard_met": global_submission_standard_met,
        "decision": "submit_global" if global_submission_standard_met else "do_not_submit_global",
        "global_review_verdict": "submit_global" if global_submission_standard_met else "do_not_submit_global",
        "global_review_verdict_scope": "top_level_global_submission_standard",
        "source_policy_apples_to_apples_external": review_evidence_summary[
            "source_policy_apples_to_apples_external"
        ],
        "source_policy_closed_ratio": submission_manifest_boundary[
            "narrowed_archive_boundary_source_policy_closed_ratio"
        ],
        "source_policy_execution_allowed_now": submission_manifest_boundary[
            "narrowed_archive_boundary_source_policy_execution_allowed_now"
        ],
        "source_policy_execution_invoked": external_checks[
            "oc12_archive_source_policy_execution_invoked"
        ],
        "current_archive_usable_as_full_source_policy_runner_archive": (
            submission_manifest_boundary[
                "narrowed_archive_boundary_current_archive_usable_as_full_source_policy_runner_archive"
            ]
        ),
        "exact_b4_opt_in_required_for_execution": submission_manifest_boundary[
            "narrowed_archive_boundary_exact_b4_opt_in_required_for_execution"
        ],
        "required_user_approval_statement": submission_manifest_boundary[
            "narrowed_archive_boundary"
        ].get("required_user_approval_statement"),
        "guarded_execution_driver": submission_manifest_boundary[
            "narrowed_archive_boundary"
        ].get("guarded_execution_driver"),
        "scope": submission_manifest_boundary["narrowed_archive_boundary_scope"],
        "narrowed_archive_boundary_status": submission_manifest_boundary[
            "narrowed_archive_boundary_status"
        ],
        "narrowed_archive_boundary_matches_reproducibility_manifest": submission_manifest_boundary[
            "narrowed_archive_boundary_matches_reproducibility_manifest"
        ],
        "safe_action_ids": submission_manifest_boundary[
            "narrowed_archive_boundary_safe_action_ids"
        ],
        "opt_in_action_ids": submission_manifest_boundary[
            "narrowed_archive_boundary_opt_in_action_ids"
        ],
        "oc12_archive_tfe_preflight": review_evidence_summary[
            "oc12_archive_tfe_preflight"
        ],
        "oc12_archive_action_boundary": external_checks[
            "oc12_archive_action_boundary"
        ],
        "oc12_archive_action_boundary_summary": review_evidence_summary[
            "oc12_archive_action_boundary"
        ],
        "oc12_archive_safe_action_ids": external_checks[
            "oc12_archive_safe_action_ids"
        ],
        "oc12_archive_opt_in_action_ids": external_checks[
            "oc12_archive_opt_in_action_ids"
        ],
        "oc12_archive_source_policy_execution_allowed_now": external_checks[
            "oc12_archive_source_policy_execution_allowed_now"
        ],
        "oc12_archive_source_policy_execution_invoked": external_checks[
            "oc12_archive_source_policy_execution_invoked"
        ],
        "oc12_archive_exact_b4_opt_in_required_for_execution": external_checks[
            "oc12_archive_exact_b4_opt_in_required_for_execution"
        ],
        "oc12_archive_opt_in_required_command_count": external_checks[
            "oc12_archive_opt_in_required_command_count"
        ],
        "oc12_archive_opt_in_required_mapped_external_rows": external_checks[
            "oc12_archive_opt_in_required_mapped_external_rows"
        ],
        "narrowed_claim_subcheck_met": narrowed_submission_standard_met,
        "narrowed_claim_subcheck_disposition": narrowed_claim_subcheck_disposition,
        "narrowed_claim_compatibility_aliases": {
            "legacy_fields": [
                "narrowed_submission_standard_met",
                "narrowed_claim_submission_standard_met",
                "narrowed_claim_decision",
            ],
            "meaning": (
                "Compatibility aliases for the subsidiary narrowed-claim subcheck only; "
                "they are not the top-level global review decision and do not imply "
                "whole-paper CMAME submission readiness."
            ),
            "top_level_global_decision_field": "decision",
        },
        "narrowed_submission_standard_met": narrowed_submission_standard_met,
        "narrowed_claim_submission_standard_met": narrowed_submission_standard_met,
        "narrowed_claim_decision": legacy_narrowed_claim_decision,
        "narrowed_claim_role": "subsidiary_bounded_subcheck_not_top_level_review_verdict",
        "subsidiary_narrowed_claim": {
            "subcheck_met": narrowed_submission_standard_met,
            "disposition": narrowed_claim_subcheck_disposition,
            "legacy_submission_standard_met_alias": narrowed_submission_standard_met,
            "legacy_decision_alias": legacy_narrowed_claim_decision,
            "submission_standard_met": narrowed_submission_standard_met,
            "decision": legacy_narrowed_claim_decision,
            "role": "subsidiary_bounded_subcheck_not_top_level_review_verdict",
            "does_not_override_global_decision": True,
        },
        "full_source_policy_submission_standard_met": full_source_policy_submission_standard_met,
        "objective_completion_checks": {
            "schema": objective_completion.get("schema"),
            "status": objective_completion.get("status"),
            "objective_complete": objective_completion.get("objective_complete"),
            "submission_ready": objective_completion.get("submission_ready"),
            "requirement_count": objective_completion.get("summary", {}).get("requirement_count"),
            "satisfied_count": objective_completion.get("summary", {}).get("satisfied_count"),
            "partial_count": objective_completion.get("summary", {}).get("partial_count"),
            "open_count": objective_completion.get("summary", {}).get("open_count"),
            "blocking_open_count": objective_completion.get("summary", {}).get("blocking_open_count"),
            "objective_blocker_matrix_status": "global_objective_blockers_remain_open",
            "blockers_by_id": objective_blockers_by_id,
            "blocker_open_by_id": objective_completion.get("blocker_open_by_id"),
            "blocker_status_by_id": objective_blocker_status_by_id,
            "blocker_closure_decision_by_id": objective_completion.get(
                "blocker_closure_decision_by_id"
            ),
            "blocker_closure_allowed_by_id": objective_completion.get(
                "blocker_closure_allowed_by_id"
            ),
            "blocker_next_actions_by_id": objective_blocker_next_actions_by_id,
            "blocker_required_to_close_by_id": objective_blocker_required_to_close_by_id,
            "blocker_safe_next_actions_by_id": objective_blocker_safe_next_actions_by_id,
            "blocker_opt_in_required_actions_by_id": objective_blocker_opt_in_required_actions_by_id,
            "core_matrix_ready": objective_completion.get("summary", {}).get("core_matrix_ready"),
            "source_policy_closed": objective_completion.get("summary", {}).get("source_policy_closed"),
            "b2_source_policy_closed": objective_completion.get("summary", {}).get("b2_source_policy_closed"),
            "b2_source_policy_rows_closed": objective_completion.get("summary", {}).get(
                "b2_source_policy_rows_closed"
            ),
            "b2_active_suites_closed": objective_completion.get("summary", {}).get(
                "b2_active_suites_closed"
            ),
            "b2_active_suites_closed_by_demotion": objective_completion.get("summary", {}).get(
                "b2_active_suites_closed_by_demotion"
            ),
            "tfe_runner_closed": objective_completion.get("summary", {}).get("tfe_runner_closed"),
            "proof_closed": objective_completion.get("summary", {}).get("proof_closed"),
            "quality_review_closed": objective_completion.get("summary", {}).get("quality_review_closed"),
            "minimal_code_ready": objective_completion.get("summary", {}).get("minimal_code_ready"),
        },
        "format_checks": format_checks,
        "result_checks": result_checks,
        "proof_checks": proof_checks,
        "external_checks": external_checks,
        "claim_hygiene_checks": claim_hygiene_checks,
        "code_hygiene_checks": code_hygiene_checks,
        "closeout_actionability_checks": closeout_actionability_checks,
        "submission_integrity_checks": submission_integrity_checks,
        "pdf_style_review_checks": pdf_style_review_checks,
        "global_review_dimensions": global_review_dimensions,
        "global_review_dimension_evidence": global_review_dimension_evidence,
        "global_review_dimension_artifact_anchors": global_review_dimension_artifact_anchors,
        "global_submission_decision_basis": global_submission_decision_basis,
        "global_reviewer_assessment": global_reviewer_assessment,
        "global_substantive_findings": global_substantive_findings,
        "findings_scope": "whole_paper_cmame_submission_standard",
        "findings_role": "top_level_machine_readable_global_review_not_narrowed_blocker_gate",
        "findings": global_review_findings,
        "global_review_findings": global_review_findings,
        "global_editorial_decision": global_editorial_decision,
        "global_review_frame": global_review_frame,
        "global_blocker_hierarchy": global_blocker_hierarchy,
        "global_review_semantic_invariants": global_review_semantic_invariants,
        "submission_manifest_boundary": submission_manifest_boundary,
        "evidence_summary": review_evidence_summary,
        "open_blocker_count": len(global_open_findings),
        "open_blockers": [item["id"] for item in global_open_findings],
        "open_blocker_ids": global_open_blocker_ids,
        "objective_blocker_matrix_status": "global_objective_blockers_remain_open",
        "blockers_by_id": objective_blockers_by_id,
        "blocker_open_by_id": objective_completion.get("blocker_open_by_id"),
        "blocker_status_by_id": objective_blocker_status_by_id,
        "blocker_closure_decision_by_id": objective_completion.get(
            "blocker_closure_decision_by_id"
        ),
        "blocker_closure_allowed_by_id": objective_completion.get(
            "blocker_closure_allowed_by_id"
        ),
        "blocker_next_actions_by_id": objective_blocker_next_actions_by_id,
        "blocker_required_to_close_by_id": objective_blocker_required_to_close_by_id,
        "blocker_safe_next_actions_by_id": objective_blocker_safe_next_actions_by_id,
        "blocker_opt_in_required_actions_by_id": objective_blocker_opt_in_required_actions_by_id,
        "objective_blockers_by_id": objective_blockers_by_id,
        "objective_blocker_open_by_id": objective_completion.get("blocker_open_by_id"),
        "objective_blocker_status_by_id": objective_blocker_status_by_id,
        "objective_blocker_closure_decision_by_id": objective_completion.get(
            "blocker_closure_decision_by_id"
        ),
        "objective_blocker_closure_allowed_by_id": objective_completion.get(
            "blocker_closure_allowed_by_id"
        ),
        "objective_blocker_next_actions_by_id": objective_blocker_next_actions_by_id,
        "objective_blocker_required_to_close_by_id": objective_blocker_required_to_close_by_id,
        "objective_blocker_safe_next_actions_by_id": objective_blocker_safe_next_actions_by_id,
        "objective_blocker_opt_in_required_actions_by_id": objective_blocker_opt_in_required_actions_by_id,
        "blocking_findings": global_open_findings,
        "cmame_blocker_gate_open_blocker_count": len(cmame_blocker_gate_open_findings),
        "cmame_blocker_gate_open_blockers": [item["id"] for item in cmame_blocker_gate_open_findings],
        "closed_blockers_scope": "narrowed_claim_blocker_gate_not_global_submission_standard",
        "narrowed_claim_closed_blockers": [
            item.get("id") for item in blocker.get("blockers", []) if item.get("status") == "closed"
        ],
        "closed_blockers": [item.get("id") for item in blocker.get("blockers", []) if item.get("status") == "closed"],
        "review_conclusion": (
            "Global submission-standard review verdict: do not submit globally yet. "
            "The narrowed-claim package is a subsidiary bounded subcheck, not the top-level review verdict; "
            "the global standard remains open because OC4 source-policy reproduction, OC6 original TFE runner "
            "completion, and OC12 minimal source-policy runner package readiness are not closed. "
            "The latest bounded common-reference results are now included in the paper package, "
            "and a separate all-example sanity audit now checks every method/example cell. "
            "A paper numerical result matrix now records all 44 method/example order-error rows with "
            "their source-policy claim scope, and a claim-disposition audit now separates all 40 "
            "nonlocal common-reference rows from the 15 anomaly/source-policy recheck rows. "
            "The common-reference order table has also been independently recomputed from raw rows with no "
            "summary mismatches. "
            "The comparison reconciliation audit now separates the closed finite-grid common-reference "
            "order/error diagnostic statement from the still-open source-policy reproduction claim. "
            "The source-policy diagnosis explains the flagged external rows, the all-example source-policy "
            "audit checks every flagged row across all four examples, and the source-policy closure triage "
            "groups those rows into concrete fix/rerun/demote actions while keeping B4 open. "
            "A row-level source-policy closure ledger now records the missing evidence for each flagged "
            "row and confirms that zero rows are source-policy closed or external-superiority ready. "
            "The suite-level disposition audit and source-policy closure manifest make the run/demote "
            "decisions explicit. The TFE source-policy spec now extracts the original pendulum setup, "
            "reference policy, and method parameters, but no TFE source-policy rows are completed yet. "
            "The external reconciliation now distinguishes completed 2021 public baseline/timing rows "
            "from still-open local same-policy Gauss6 dynamic-order rows. "
            "The HI2022 policy-decision audit now classifies the 24 bounded T=0.1 half-implicit rows "
            "as bounded evidence only and keeps the full T=8 source-policy decision open. "
            "The HI2022 source-policy row audit now fixes the three B2-flagged rows at row level and "
            "records zero source-policy-closed or external-superiority-ready HI2022 rows. "
            "The VP2024 code-path disposition audit now checks all four examples, records no distinct "
            "public code path, marks all four source-policy rows attempted-not-reproducible/unable, "
            "and confines the coordinate-partitioning proxy to the common-reference diagnostic. "
            "The external-suite demotion ledger and Route B claim-boundary audit now demote VP2024, "
            "HI2022, RA2021, and TFE from external-superiority scope, so B2 is closed for the current "
            "non-superiority claim set while source-policy execution rows remain diagnostic. "
            "The B2 remaining-work manifest now gives every flagged source-policy row a nonempty "
            "suite/status/action and records zero active external-superiority rows after demotion. "
            "The RA2021 source-policy row audit confirms that public order/timing evidence is complete "
            "but still not a source-policy reproduction or an external-superiority closure. "
            f"{b4_post_execution_conclusion_sentence}"
            "The narrowed-claim "
            "subcheck passes only for formal-order/common-reference diagnostics and does not close the "
            "global submission blockers OC4/OC6/OC12; RA2021 double low-order and HI2022 rA_half "
            "double-shard repair or demotion remain future source-policy work. "
            "The code-hygiene review now classifies the current implementation as a research/audit "
            "repository rather than a minimal reproducible submission package: it preserves useful "
            "provenance, while the local accepted-row runners are now compact and executable; "
            "the full source-policy runner/package boundary remains a global submission blocker until "
            "source-policy package readiness is closed. "
            "The proof-closure manifest and B3 direct-proof review now close the proof-status blocker "
            "by the direct residual-bridge/Kantorovich perturbation route. "
            "The B1 AD-expanded implementation-path certificate now closes the independent B1 "
            "implementation-oracle blocker by differentiating the closed residual identities across "
            "4752 derivative cells, while the non-active primitive/global symbolic-oracle completion record remains open. "
            "The local submission-integrity audit now checks citation-key/bibitem consistency, sidecars, "
            "and external item-by-item reference metadata verification. "
            "The PDF-style review audit now reads the reference PDF and current manuscript PDF directly; "
            "it confirms the reference's algorithm/numerical/work-precision style and passes only the "
            "bounded narrowed-claim subcheck while retaining the global submission boundary. The B4/B6/B7 "
            "narrowed subcheck is recorded separately and does not override global submission readiness; "
            "source-policy work/precision and external superiority remain non-claims."
        ),
    }
    with OUT_JSON.open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, sort_keys=True)
        handle.write("\n")

    lines = [
        "# CMAME Submission Review Agent Report",
        "",
        f"Review scope: **{report['review_scope']}**.",
        f"Top-level review decision scope: `{report['top_level_review_decision_scope']}`.",
        f"Decision: **{report['decision']}**.",
        f"Global review verdict: **{report['global_review_verdict']}**; scope `{report['global_review_verdict_scope']}`.",
        f"Global submission standard met: `{report['submission_standard_met']}`.",
        f"Full source-policy package ready: `{report['full_source_policy_submission_standard_met']}`.",
        f"Read-only review: `{report['read_only']}`.",
        f"Global open blockers: `{','.join(report['open_blockers'])}`.",
        f"Objective blocker status by id: `{report['objective_blocker_status_by_id']}`.",
        f"Objective blocker required-to-close by id: `{report['objective_blocker_required_to_close_by_id']}`.",
        f"Objective blocker safe next actions by id: `{report['objective_blocker_safe_next_actions_by_id']}`.",
        f"Objective blocker opt-in required actions by id: `{report['objective_blocker_opt_in_required_actions_by_id']}`.",
        "",
        "## Objective Blocker Matrix",
        "",
        "This review records the whole-paper CMAME submission decision. It does not close the global objective blockers.",
        "",
        f"- `blocker_open_by_id={blocker_token(report['blocker_open_by_id'])}`",
        f"- `blocker_closure_decision_by_id={blocker_token(report['blocker_closure_decision_by_id'])}`",
        f"- `blocker_closure_allowed_by_id={blocker_token(report['blocker_closure_allowed_by_id'])}`",
        "",
        f"Evidence summary: source-policy `{report['evidence_summary']['source_policy_apples_to_apples_external']}`, accepted source-policy dynamic-order `{report['evidence_summary']['accepted_source_policy_dynamic_order_examples']}`, full-source runner package `{report['evidence_summary']['full_source_policy_runner_package_ready']}`, dependency boundary `{report['evidence_summary']['minimal_submission_code_dependency_boundary_status']}`.",
        f"CMAME narrowed blocker-gate open blockers: `{','.join(report['cmame_blocker_gate_open_blockers'])}`.",
        f"Narrowed blocker-gate closed blockers: `{','.join(report['narrowed_claim_closed_blockers'])}`; scope `{report['closed_blockers_scope']}`.",
        "",
        "## Input Artifact Provenance",
        "",
        f"- Hash algorithm: `{report['input_artifact_provenance']['hash_algorithm']}`.",
        f"- Timestamp policy: `{report['input_artifact_provenance']['timestamp_policy']}`.",
        f"- Input artifacts read: `{len(report['input_artifact_provenance']['input_artifacts_read'])}`.",
        "- Stale token scan OC9/reference next-action stale: "
        f"`{report['stale_token_scan']['objective_oc9_stale_next_to_close_present']}`.",
        "- Readiness review delegates current global decision: "
        f"`{report['stale_token_scan']['readiness_review_delegates_current_global_decision']}`.",
        f"- B4 opt-in packet: `{report['opt_in_boundary']['packet_path']}`.",
        f"- B4 exact opt-in phrase: `{report['opt_in_boundary']['exact_required_phrase']}`.",
        "",
        "## Global Review Semantic Contract",
        "",
        f"- Contract: `{report['global_review_semantic_invariants']['contract']}`.",
        "- Decision matches objective completion: "
        f"`{report['global_review_semantic_invariants']['top_level_decision_matches_objective_completion']}`.",
        "- Objective-incomplete iff do-not-submit-global: "
        f"`{report['global_review_semantic_invariants']['decision_is_do_not_submit_global_iff_objective_incomplete']}`.",
        "- All blocking objective requirements reported: "
        f"`{report['global_review_semantic_invariants']['all_blocking_objective_requirements_reported']}`.",
        "- Global findings include all blocking requirements: "
        f"`{report['global_review_semantic_invariants']['global_findings_include_all_blocking_requirements']}`.",
        "- Narrowed claim does not override global decision: "
        f"`{report['global_review_semantic_invariants']['narrowed_claim_does_not_override_global_decision']}`.",
        "- Source-policy rows closed: "
        f"`{report['global_review_semantic_invariants']['source_policy_rows_closed_text']}`.",
        "- Accepted source-policy dynamic-order examples: "
        f"`{report['global_review_semantic_invariants']['accepted_source_policy_dynamic_order_examples_text']}`.",
        "- Full source-policy runner package ready: "
        f"`{report['global_review_semantic_invariants']['full_source_policy_runner_package_ready']}`.",
        "- No forbidden execution flags run_v047/heavy: "
        f"`{report['global_review_semantic_invariants']['run_v047_invoked']}/"
        f"{report['global_review_semantic_invariants']['heavy_run_invoked']}`.",
        "- B4 opt-in boundary retained: "
        f"`{report['global_review_semantic_invariants']['b4_opt_in_boundary_retained']}`.",
        "- Global comparison policy artifact included: "
        f"`{report['global_review_semantic_invariants']['global_comparison_policy_artifact_included']}`.",
        "- Submission manifest narrowed archive boundary matches reproducibility manifest: "
        f"`{report['global_review_semantic_invariants']['submission_manifest_narrowed_boundary_matches_reproducibility_manifest']}`.",
        "- Submission manifest narrowed archive boundary status/source-policy/use/execution/exact: "
        f"`{report['global_review_semantic_invariants']['submission_manifest_narrowed_boundary_status']}/"
        f"{report['global_review_semantic_invariants']['submission_manifest_narrowed_boundary_source_policy_closed_ratio']}/"
        f"{report['global_review_semantic_invariants']['submission_manifest_narrowed_boundary_full_archive_usable']}/"
        f"{report['global_review_semantic_invariants']['submission_manifest_narrowed_boundary_source_policy_execution_allowed_now']}/"
        f"{report['global_review_semantic_invariants']['submission_manifest_narrowed_boundary_exact_b4_opt_in_required_for_execution']}`.",
        "- Submission manifest narrowed archive safe/opt-in action ids: "
        f"`{','.join(report['submission_manifest_boundary']['narrowed_archive_boundary_safe_action_ids'])}` / "
        f"`{','.join(report['submission_manifest_boundary']['narrowed_archive_boundary_opt_in_action_ids'])}`.",
        "- Submission manifest narrowed archive closure/action maps: "
        f"`{report['submission_manifest_boundary']['narrowed_archive_boundary_blocker_required_to_close_by_id']}/"
        f"{report['submission_manifest_boundary']['narrowed_archive_boundary_blocker_safe_next_actions_by_id']}/"
        f"{report['submission_manifest_boundary']['narrowed_archive_boundary_blocker_opt_in_required_actions_by_id']}`.",
        "- Top-level source-policy boundary aliases status/source-policy/use/execution/invoked/exact/scope: "
        f"`{report['narrowed_archive_boundary_status']}/"
        f"{report['source_policy_closed_ratio']}/"
        f"{report['current_archive_usable_as_full_source_policy_runner_archive']}/"
        f"{report['source_policy_execution_allowed_now']}/"
        f"{report['source_policy_execution_invoked']}/"
        f"{report['exact_b4_opt_in_required_for_execution']}/"
        f"{report['scope']}`.",
        "- Top-level source-policy boundary required approval/driver: "
        f"`{report['required_user_approval_statement']}/"
        f"{report['guarded_execution_driver']}`.",
        "- Top-level source-policy boundary safe/opt-in action ids: "
        f"`{','.join(report['safe_action_ids'])}` / "
        f"`{','.join(report['opt_in_action_ids'])}`.",
        "- OC12 archive action boundary safe/opt-in/allowed/invoked/exact/commands/rows: "
        f"`{report['oc12_archive_action_boundary_summary']}`.",
        "- OC12 archive action boundary safe/opt-in action ids: "
        f"`{','.join(report['oc12_archive_safe_action_ids'])}` / "
        f"`{','.join(report['oc12_archive_opt_in_action_ids'])}`.",
        "",
        "## Global Editorial Decision",
        "",
        f"- Scope: `{report['global_editorial_decision']['scope']}`.",
        f"- Decision: **{report['global_editorial_decision']['decision']}**.",
        "- Review basis: "
        + "; ".join(report["global_editorial_decision"]["review_basis"])
        + ".",
        "- Ranked global blockers: "
        + ",".join(report["global_editorial_decision"]["ranked_global_blockers"])
        + ".",
        f"- Non-overriding subcheck: `{report['global_editorial_decision']['non_overriding_subcheck']}`.",
        f"- Safe current disposition: {report['global_editorial_decision']['safe_current_disposition']}.",
        "",
        "## Global Reviewer Assessment",
        "",
        f"- Top-level verdict: `{report['global_reviewer_assessment']['top_level_verdict']}`.",
        f"- Primary paper line: {report['global_reviewer_assessment']['primary_paper_line']}.",
        f"- Global review rule: {report['global_reviewer_assessment']['global_review_rule']}",
        "- Evidence tiering: "
        + "; ".join(report["global_reviewer_assessment"]["evidence_tiering"])
        + ".",
        "- Global blocker priority: "
        + "; ".join(report["global_reviewer_assessment"]["global_blocker_priority"])
        + ".",
        "",
        "| rank | claim | reviewer status | reason |",
        "|---:|---|---|---|",
    ]
    for item in report["global_reviewer_assessment"]["claim_hierarchy"]:
        lines.append(
            "| "
            f"`{item['rank']}` | {item['claim']} | `{item['reviewer_status']}` | {item['reason']} |"
        )
    lines.extend(
        [
            "",
            "## Global Substantive Findings",
            "",
            "| id | severity | finding | global review judgment | required action | claim scope | blocking ids | safe disposition |",
            "|---|---|---|---|---|---|---|---|",
        ]
    )
    for item in report["global_substantive_findings"]:
        lines.append(
            "| "
            f"`{item['id']}` | `{item['severity']}` | {item['finding']} | "
            f"{item['global_review_judgment']} | {item['required_action']} | "
            f"`{item['claim_scope']}` | `{','.join(item['blocking_ids'])}` | "
            f"`{item['safe_disposition']}` |"
        )
    lines.extend(["", "### Global Finding Artifact Anchors", ""])
    for item in report["global_substantive_findings"]:
        lines.append(f"- `{item['id']}` anchors:")
        for anchor in item["artifact_anchors"]:
            lines.append(f"  - {format_anchor(anchor)}.")
    lines.extend(
        [
            "",
            "## Global Blocker Hierarchy",
            "",
            f"- Review mode: whole-paper CMAME submission standard, not a local proof/report artifact checklist.",
            "- Top-level blockers dominate narrowed-claim pass: "
            + ",".join(report["global_blocker_hierarchy"][0]["ids"])
            + ".",
            "- Non-overriding local passes: "
            + ",".join(report["global_blocker_hierarchy"][3]["ids"])
            + ".",
            "- Dimension priority: main contribution -> proof/theorem -> numerical validation -> "
            "comparison/source-policy -> reproducibility/code package -> manuscript style/integrity.",
            "",
            "| rank | class | ids | effect | dominates narrowed claim |",
            "|---:|---|---|---|---:|",
        ]
    )
    for item in report["global_blocker_hierarchy"]:
        lines.append(
            "| "
            f"`{item['rank']}` | `{item['class']}` | "
            f"`{','.join(item['ids'])}` | `{item['effect']}` | `{item['dominates_narrowed_claim']}` |"
        )
    lines.extend(
        [
            "",
        "## Global Review Dimensions",
        "",
        "| dimension | verdict | global effect | blocking boundary |",
        "|---|---|---|---|",
        ]
    )
    for item in report["global_review_dimensions"]:
        lines.append(
            "| "
            f"`{item['dimension']}` | `{item['verdict']}` | "
            f"{item['global_effect']} | {item['blocking_boundary']} |"
        )
    lines.extend(["", "## Global Review Dimension Evidence", ""])
    for item in report["global_review_dimensions"]:
        lines.append(f"### {item['dimension']}")
        lines.append(f"- Verdict: `{item['verdict']}`.")
        lines.append(f"- Blocking boundary: {item['blocking_boundary']}.")
        for evidence in report["global_review_dimension_evidence"][item["dimension"]]:
            lines.append(f"- Evidence: {evidence}.")
        for anchor in report["global_review_dimension_artifact_anchors"][item["dimension"]]:
            lines.append(f"- Anchor: {format_anchor(anchor)}.")
        lines.append("")
    lines.extend(["## Global Submission Decision Basis", ""])
    for dimension, basis in report["global_submission_decision_basis"].items():
        lines.append(
            f"- `{dimension}`: verdict `{basis['verdict']}`, "
            f"boundary `{basis['blocking_boundary']}`, anchors `{len(basis['artifact_anchors'])}`."
        )
    lines.append("")
    lines.extend(
        [
        "## Subsidiary Narrowed-Claim Subcheck (Not Global Review)",
        "",
        f"- Subcheck met: `{report['subsidiary_narrowed_claim']['subcheck_met']}`.",
        f"- Disposition: **{report['subsidiary_narrowed_claim']['disposition']}**.",
        "- Legacy compatibility aliases: `narrowed_claim_submission_standard_met` and "
        "`narrowed_claim_decision` describe this subcheck only, not the global review verdict.",
        f"- Role: `{report['subsidiary_narrowed_claim']['role']}`.",
        f"- Overrides global decision: `{not report['subsidiary_narrowed_claim']['does_not_override_global_decision']}`.",
        "",
        "## Objective Completion Audit",
        "",
        f"- Objective audit status: `{report['objective_completion_checks']['status']}`.",
        f"- Objective complete/submission ready: `{report['objective_completion_checks']['objective_complete']}/{report['objective_completion_checks']['submission_ready']}`.",
        f"- Requirements satisfied/partial/open: `{report['objective_completion_checks']['satisfied_count']}/{report['objective_completion_checks']['partial_count']}/{report['objective_completion_checks']['open_count']}`; blocking open `{report['objective_completion_checks']['blocking_open_count']}`.",
        f"- Objective B2 active suites/source-policy rows/demotion: `{report['objective_completion_checks']['b2_active_suites_closed']}/{report['objective_completion_checks']['b2_source_policy_rows_closed']}/{report['objective_completion_checks']['b2_active_suites_closed_by_demotion']}`.",
        f"- Core/source-policy/TFE/direct-PC2-proof/minimal-code closed: `{report['objective_completion_checks']['core_matrix_ready']}/{report['objective_completion_checks']['source_policy_closed']}/{report['objective_completion_checks']['tfe_runner_closed']}/{report['objective_completion_checks']['proof_closed']}/{report['objective_completion_checks']['minimal_code_ready']}`.",
        f"- Objective blocker required-to-close by id: `{report['objective_completion_checks']['blocker_required_to_close_by_id']}`.",
        f"- Objective blocker safe next actions by id: `{report['objective_completion_checks']['blocker_safe_next_actions_by_id']}`.",
        f"- Objective blocker opt-in required actions by id: `{report['objective_completion_checks']['blocker_opt_in_required_actions_by_id']}`.",
        "",
        "## Format Checks",
        "",
        f"- Elsevier/CMAME class marker: `{format_checks['elsarticle_preprint']}`.",
        f"- CMAME journal marker: `{format_checks['cmame_journal_marker']}`.",
        f"- Abstract words: `{format_checks['abstract_words']}`.",
        f"- Keywords: `{format_checks['keyword_count']}`.",
        f"- Highlights/declarations/flat source present: `{format_checks['highlights_present']}/{format_checks['declarations_present']}/{format_checks['flat_submission_present']}`.",
        "",
        "## PDF Style Review",
        "",
        f"- PDF-style review audit: `{pdf_style_review_checks['schema']}` / `{pdf_style_review_checks['status']}`.",
        f"- PDF-style texts read reference/main/flat: `{pdf_style_review_checks['reference_text_read']}/{pdf_style_review_checks['manuscript_text_read']}/{pdf_style_review_checks['flat_manuscript_text_read']}`.",
        f"- Reference style figures/tables/algorithms: `{pdf_style_review_checks['reference_figure_count']}/{pdf_style_review_checks['reference_table_count']}/{pdf_style_review_checks['reference_algorithm_count']}`; work-precision mentions `{pdf_style_review_checks['reference_work_precision_mentions']}`.",
        f"- Reference style algorithm/numerical/work-precision/declarations: `{pdf_style_review_checks['reference_algorithm_boxes_present']}/{pdf_style_review_checks['reference_numerical_experiments_section']}/{pdf_style_review_checks['reference_work_precision_figures']}/{pdf_style_review_checks['reference_data_availability_and_declarations']}`.",
        f"- Manuscript style figures/tables/theorems/proof tokens: `{pdf_style_review_checks['manuscript_figure_count']}/{pdf_style_review_checks['manuscript_table_count']}/{pdf_style_review_checks['manuscript_theorem_count']}/{pdf_style_review_checks['manuscript_proof_token_count']}`.",
        f"- PDF-style source-policy/direct-proof/B6/B7/minimal-code closed: `{pdf_style_review_checks['source_policy_rows_closed']}/{pdf_style_review_checks['source_policy_total_rows']}` / `{pdf_style_review_checks['proof_gap_closed']}` / `{pdf_style_review_checks['prose_b6_closed']}` / `{pdf_style_review_checks['figure_set_b7_closed']}` / `{pdf_style_review_checks['minimal_reproducibility_submission_ready']}`; eta_h solver-policy evidence, the residual-to-error theorem for mechanism rows, and full source-policy/package readiness remain separate global boundaries.",
        f"- PDF-style narrowed/global scope: `{pdf_style_review_checks['submission_standard_scope']}/{pdf_style_review_checks['global_submission_standard_met']}/{pdf_style_review_checks['submission_ready']}`; ready scope `{pdf_style_review_checks['submission_ready_scope']}`.",
        f"- PDF-style remaining gates eta_h/residual/source/no-ready: `{pdf_style_review_checks['remaining_gate_scope']['eta_h_theorem_condition_retained']}/{pdf_style_review_checks['remaining_gate_scope']['residual_to_error_blocking_obligations']}/{pdf_style_review_checks['remaining_gate_scope']['source_policy_rows_closed']}/{pdf_style_review_checks['remaining_gate_scope']['source_policy_rows_total']}/{pdf_style_review_checks['remaining_gate_scope']['submission_ready_not_claimed_by_pdf_style_audit']}`.",
        f"- PDF-style blocking findings: `{','.join(pdf_style_review_checks['blocking_finding_ids'])}`.",
        f"- PDF-style bounded-subcheck standard/quality markers: `{pdf_style_review_checks['submission_standard_met']}/{pdf_style_review_checks['quality_review_passed']}`; not global submission or global quality-review clearance.",
        f"- PDF-style bounded-subcheck compatibility alias: `{pdf_style_review_checks['decision']}`; this is not a global submission instruction and not a global submission decision.",
        "",
        "## Result Checks",
        "",
        f"- Paper result pack: `{result_checks['paper_result_pack_schema']}`.",
        f"- Manuscript includes latest common-reference result: `{result_checks['paper_includes_latest_common_reference_result']}`.",
        f"- PDF text includes latest common-reference result: `{result_checks['pdf_text_includes_latest_common_reference_result']}`.",
        f"- Manuscript/PDF include all-method matrix: `{result_checks['manuscript_includes_all_method_matrix']}/{result_checks['pdf_text_includes_all_method_matrix']}`.",
        f"- All-method matrix visible methods/examples: `{result_checks['all_method_matrix_all_methods_visible']}/{result_checks['all_method_matrix_all_examples_visible']}`.",
        f"- Publication figure boundary visible in manuscript/PDF: `{result_checks['publication_figure_boundary_visible']}`.",
        f"- Source-policy progress boundary visible in manuscript/PDF: `{result_checks['source_policy_progress_boundary_visible']}`.",
        f"- Four-example source-policy dashboard: `{result_checks['four_example_dashboard_status']}`; examples `{','.join(result_checks['four_example_dashboard_examples'])}`; local evidence coverage `{result_checks['four_example_dashboard_local_evidence_coverage_examples']}/4`; accepted method dynamic-order examples `{result_checks['four_example_dashboard_accepted_method_dynamic_order_example_count']}/4`; mechanism-coverage examples `{result_checks['four_example_dashboard_mechanism_coverage_example_count']}/4`; accepted source-policy dynamic-order examples `{result_checks['four_example_dashboard_accepted_source_policy_dynamic_order_examples']}/4`.",
        f"- Closed-loop coarse-window trajectory diagnostics: `{result_checks['four_example_dashboard_closed_loop_true_dynamic_order_closed_examples']}/2` models `{','.join(result_checks['four_example_dashboard_closed_loop_true_dynamic_order_closed_names'])}` at h=`{result_checks['four_example_dashboard_closed_loop_true_dynamic_step_sizes']}`; stage oracle used `{result_checks['four_example_dashboard_closed_loop_true_dynamic_stage_oracle_used']}`.",
        f"- Four-example dashboard common-reference wins: `{result_checks['four_example_dashboard_order_wins']}/{result_checks['four_example_dashboard_nonlocal_cells']}` order and `{result_checks['four_example_dashboard_error_wins']}/{result_checks['four_example_dashboard_nonlocal_cells']}` error; source-policy closed rows `{result_checks['four_example_dashboard_source_policy_closed_rows']}`.",
        f"- All-method matrix coverage: `{result_checks['all_method_matrix_cell_count']}` cells across `{result_checks['all_method_matrix_method_count']}` methods.",
        f"- Paper numerical result matrix: `{result_checks['paper_numerical_matrix_schema']}` with `{result_checks['paper_numerical_matrix_row_count']}/{result_checks['paper_numerical_matrix_expected_row_count']}` cells from `{result_checks['paper_numerical_matrix_raw_row_count']}` raw rows.",
        f"- Paper numerical matrix source-policy/direct-error claims allowed: `{result_checks['paper_numerical_matrix_source_policy_external_superiority_allowed']}/{result_checks['paper_numerical_matrix_direct_error_superiority_allowed']}`; strict external rows `{result_checks['paper_numerical_matrix_strict_external_error_claim_rows']}`.",
        f"- Paper numerical matrix diagnostic favorable order/error cells: `{result_checks['paper_numerical_matrix_direct_order_wins']}/{result_checks['paper_numerical_matrix_direct_order_comparisons']}` and `{result_checks['paper_numerical_matrix_direct_error_wins']}/{result_checks['paper_numerical_matrix_direct_error_comparisons']}`; not an external-superiority claim.",
        f"- Result-to-manuscript traceability audit: `{result_checks['result_traceability_schema']}` / `{result_checks['result_traceability_status']}`.",
        f"- Result-to-manuscript velocity cells checked: `{result_checks['result_traceability_velocity_cells_checked']}/44`; main TeX/PDF `{result_checks['result_traceability_main_tex_cells']}/{result_checks['result_traceability_main_pdf_cells']}`, flat TeX/PDF `{result_checks['result_traceability_flat_tex_cells']}/{result_checks['result_traceability_flat_pdf_cells']}`.",
        f"- Result-to-manuscript source-policy/external-superiority boundary: `{result_checks['result_traceability_source_policy_reproduction_closed']}` / `{result_checks['result_traceability_external_superiority_allowed']}`.",
        f"- All-method claim disposition audit: `{result_checks['all_method_disposition_schema']}` with `{result_checks['all_method_disposition_nonlocal_cells']}/{result_checks['all_method_disposition_expected_nonlocal_cells']}` nonlocal cells and `{result_checks['all_method_disposition_total_cells']}` total cells.",
        f"- All-method claim disposition diagnostic favorable order/error cells: `{result_checks['all_method_disposition_order_wins']}/{result_checks['all_method_disposition_order_comparisons']}` and `{result_checks['all_method_disposition_error_wins']}/{result_checks['all_method_disposition_error_comparisons']}`; source-policy rows remain nonpromoted.",
        f"- All-method source-policy closed/open/flagged rows: `{result_checks['all_method_disposition_source_policy_closed_rows']}/{result_checks['all_method_disposition_source_policy_open_rows']}/{result_checks['all_method_disposition_flagged_nonlocal_rows']}`; strict external rows `{result_checks['all_method_disposition_strict_external_error_rows']}`.",
        f"- All-method source-policy superiority allowed: `{result_checks['all_method_disposition_source_policy_superiority_allowed']}`.",
        f"- Manuscript/PDF include source-policy diagnosis: `{result_checks['manuscript_includes_source_policy_diagnosis']}/{result_checks['pdf_text_includes_source_policy_diagnosis']}`.",
        f"- Manuscript/PDF include all-example source-policy audit: `{result_checks['manuscript_includes_all_example_source_policy_audit']}/{result_checks['pdf_text_includes_all_example_source_policy_audit']}`.",
        f"- Manuscript/PDF include active TFE B2 candidate smoke: `{result_checks['manuscript_includes_active_tfe_b2_smoke']}/{result_checks['pdf_text_includes_active_tfe_b2_smoke']}`.",
        f"- Manuscript/PDF include TFE full-T10 coarse candidate summary: `{result_checks['manuscript_includes_tfe_full_t10_coarse_candidate']}/{result_checks['pdf_text_includes_tfe_full_t10_coarse_candidate']}`.",
        f"- Manuscript/PDF include TFE Appendix-B coefficient certificate boundary: `{result_checks['manuscript_includes_tfe_appendix_b_certificate']}/{result_checks['pdf_text_includes_tfe_appendix_b_certificate']}`.",
        f"- Manuscript/PDF include TFE m=3 full-T10 formula-probe boundary: `{result_checks['manuscript_includes_tfe_m3_formula_probe']}/{result_checks['pdf_text_includes_tfe_m3_formula_probe']}`.",
        f"- Manuscript/PDF include TFE Brown--McPhee source-policy boundary: `{result_checks['manuscript_includes_tfe_brown_mcphee_boundary']}/{result_checks['pdf_text_includes_tfe_brown_mcphee_boundary']}`.",
        f"- Manuscript/PDF include minimal reproducibility package boundary: `{result_checks['manuscript_includes_minimal_reproducibility_boundary']}/{result_checks['pdf_text_includes_minimal_reproducibility_boundary']}`.",
        f"- Manuscript/PDF include comparison reconciliation: `{result_checks['manuscript_includes_comparison_reconciliation']}/{result_checks['pdf_text_includes_comparison_reconciliation']}`.",
        f"- All-examples sanity audit: `{result_checks['all_examples_sanity_cell_count']}` cells; local rows `{result_checks['all_examples_local_rows_passed']}/{result_checks['all_examples_local_rows_expected']}`; flagged nonlocal rows `{result_checks['all_examples_flagged_nonlocal_rows']}`.",
        f"- All-examples source-policy recheck required: `{result_checks['all_examples_source_policy_recheck_required']}`.",
        f"- All-examples external superiority allowed: `{result_checks['all_examples_external_superiority_allowed']}`.",
        f"- Order recomputation audit: `{result_checks['order_recomputation_cell_count']}` cells from `{result_checks['order_recomputation_raw_row_count']}` raw rows; mismatches `{result_checks['order_recomputation_mismatch_count']}`.",
        f"- Order recomputation external superiority allowed: `{result_checks['order_recomputation_external_superiority_allowed']}`.",
        f"- Visual legibility audit: `{result_checks['visual_legibility_status']}`; B5 closed `{result_checks['visual_legibility_b5_closed']}`; legacy visual-only B7-open flag `{result_checks['visual_legibility_b7_open']}`.",
        f"- Visual figure dimensions/captions: `{result_checks['visual_main_figure_width_px']}x{result_checks['visual_main_figure_height_px']}` main, `{result_checks['visual_flat_figure_width_px']}x{result_checks['visual_flat_figure_height_px']}` flat; captions/logs `{result_checks['visual_pdf_captions_present']}/{result_checks['visual_latex_logs_clean']}`.",
        f"- Figure-set audit: `{result_checks['figure_set_status']}`; figures `{result_checks['figure_set_count']}/{result_checks['figure_set_expected_count']}`, files/integration/captions `{result_checks['figure_set_all_available']}/{result_checks['figure_set_all_integrated']}/{result_checks['figure_set_all_pdf_captions']}`.",
        f"- Figure-set B7 boundary: Figure 12 integrated `{result_checks['figure_set_figure12_integrated']}`; Figure 13 integrated `{result_checks['figure_set_figure13_integrated']}`, B7 closed `{result_checks['figure_set_b7_closed']}`, external superiority allowed `{result_checks['figure_set_external_superiority_allowed']}`.",
        f"- B7 closure-readiness preflight: `{result_checks['figure_set_b7_preflight_status']}`; closed/open `{result_checks['figure_set_b7_preflight_closed_preconditions']}/{result_checks['figure_set_b7_preflight_open_dependencies']}`; source-policy rows `{result_checks['figure_set_source_policy_rows_closed']}/{result_checks['figure_set_source_policy_rows_total']}`; closure allowed `{result_checks['figure_set_b7_preflight_closure_allowed']}`.",
        f"- B7 post-B4 figure-scope plan: `{result_checks['figure_set_post_b4_plan_status']}`; retain `{result_checks['figure_set_post_b4_plan_retain_figures']}`, refresh `{result_checks['figure_set_post_b4_plan_claim_refresh_figures']}`, rebuild `{result_checks['figure_set_post_b4_plan_rebuild_figures']}`, source-policy-dependent `{result_checks['figure_set_post_b4_plan_source_policy_dependent_count']}`, closure allowed `{result_checks['figure_set_post_b4_plan_closure_allowed']}`.",
        f"- B7 post-B4 ready-command boundary: ready/unaddressed rows `{result_checks['figure_set_post_b4_ready_command_mapped_rows']}/{result_checks['figure_set_post_b4_unaddressed_rows']}`; not-ready lanes `{result_checks['figure_set_post_b4_not_ready_lanes']}`; ready commands close B4/B7 `{result_checks['figure_set_post_b4_ready_commands_close_b4_b7']}`.",
        f"- Prose residue audit: `{result_checks['prose_residue_status']}`; main/flat machine tokens `{result_checks['prose_main_body_machine_token_count']}/{result_checks['prose_flat_main_body_machine_token_count']}`; B6 closed `{result_checks['prose_b6_closed']}`.",
        f"- Prose artifact confinement: `{result_checks['prose_artifact_filenames_confined_to_appendix']}`; appendix artifact macros `{result_checks['prose_appendix_artifact_macro_count']}`.",
        f"- B6 closure-readiness preflight: `{result_checks['prose_b6_preflight_status']}`; closed/open `{result_checks['prose_b6_preflight_closed_preconditions']}/{result_checks['prose_b6_preflight_open_dependencies']}`; closure allowed `{result_checks['prose_b6_preflight_closure_allowed']}`.",
        f"- B6 ready-command dependency: mapped/unaddressed rows `{result_checks['prose_b6_ready_command_mapped_rows']}/{result_checks['prose_b6_ready_command_unaddressed_rows']}`; not-ready lanes `{result_checks['prose_b6_ready_command_not_ready_lanes']}`; ready commands enable final prose `{result_checks['prose_b6_ready_commands_enable_final_prose']}`.",
        f"- B6 post-execution dependency: `{result_checks['prose_b6_post_execution_status']}`; promoted rows `{result_checks['prose_b6_post_execution_promoted_rows']}/{result_checks['prose_b6_post_execution_total_rows']}`; closes B4/B7 `{result_checks['prose_b6_post_execution_close_b4_b7']}`; enables final prose `{result_checks['prose_b6_post_execution_enable_final_prose']}`.",
        f"- B6 proof-prose relocation: `{result_checks['prose_proof_relocation_status']}`; strict boundary preserved `{result_checks['prose_proof_relocation_strict_boundary_preserved']}`; independently closes B6 `{result_checks['prose_proof_relocation_b6_closed']}`.",
        f"- Comparison reconciliation: matrix closed `{result_checks['comparison_matrix_closed']}`; common-reference claim allowed `{result_checks['common_reference_claim_allowed']}`; source-policy superiority allowed `{result_checks['source_policy_superiority_claim_allowed']}`.",
        f"- Direct nonlocal diagnostic favorable order/error cells: `{result_checks['comparison_reconciliation_direct_order_wins']}/{result_checks['comparison_reconciliation_direct_order_comparisons']}` and `{result_checks['comparison_reconciliation_direct_error_wins']}/{result_checks['comparison_reconciliation_direct_error_comparisons']}`; common-reference diagnostics only.",
        f"- Comparison reconciliation B2/B4 can close now: `{result_checks['comparison_reconciliation_b2_b4_can_close_now']}`.",
        f"- Common-reference traceability rows: `{result_checks['common_reference_traceability_rows']}/{result_checks['common_reference_traceability_total_rows']}`.",
        f"- Source-policy apples-to-apples external rows: `{result_checks['source_policy_apples_to_apples_external_rows']}/{result_checks['source_policy_apples_to_apples_external_total_rows']}`.",
        f"- Global comparison-policy audit: `{result_checks['global_policy_passed_count']}/{result_checks['global_policy_row_count']}`.",
        f"- Mixed-policy direct error rows: `{result_checks['mixed_policy_direct_error_rows']}`.",
        f"- Source-policy reproduction: `{result_checks['source_policy_reproduction']}`.",
        f"- Public-code fixed-grid replay: `{result_checks['public_code_fixed_grid_replay']}`.",
        "",
        "## Claim Hygiene Checks",
        "",
        f"- Claim-hygiene audit: `{claim_hygiene_checks['status']}`.",
        f"- Allowed claim: `{claim_hygiene_checks['allowed_claim']}`.",
        f"- Accepted method/order: `{claim_hygiene_checks['accepted_method']}` / `{claim_hygiene_checks['accepted_method_order']}`.",
        f"- Comparator expected order: `{claim_hygiene_checks['comparator_expected_order']}`.",
        f"- Required-token missing count: `{claim_hygiene_checks['required_missing_count']}`.",
        f"- Submission/support forbidden-hit counts: `{claim_hygiene_checks['submission_forbidden_hit_count']}/{claim_hygiene_checks['support_forbidden_hit_count']}`.",
        f"- Source-policy/external superiority allowed: `{claim_hygiene_checks['source_policy_superiority_claim_allowed']}` / `{claim_hygiene_checks['external_superiority_claim']}`.",
        f"- Default 1e-4 / heavy run invoked: `{claim_hygiene_checks['default_1e_4_required']}` / `{claim_hygiene_checks['heavy_numerical_run_invoked']}`.",
        "",
        "## Code Hygiene Checks",
        "",
        f"- Code-hygiene status: `{code_hygiene_checks['status']}`.",
        f"- Python code size: paper package `{code_hygiene_checks['paper_python_file_count']}` files / `{code_hygiene_checks['paper_python_line_count']}` lines; v048 `{code_hygiene_checks['v048_python_file_count']}` files / `{code_hygiene_checks['v048_python_line_count']}` lines; combined `{code_hygiene_checks['combined_python_line_count']}` lines.",
        f"- Python file mix: paper `{code_hygiene_checks['paper_python_prefix_counts']}`; v048 `{code_hygiene_checks['v048_python_prefix_counts']}`.",
        f"- Reviewer-facing code policy: primary supplement limit `{code_hygiene_checks['reviewer_facing_python_file_limit']}` Python files / `{code_hygiene_checks['reviewer_facing_python_line_limit']}` lines; research-audit tree is provenance-only `{code_hygiene_checks['research_audit_repo_provenance_only']}` and primary-submission allowed `{code_hygiene_checks['research_audit_repo_primary_submission_allowed']}`.",
        f"- Research-audit primary-package risk: over `{code_hygiene_checks['research_audit_primary_submission_line_limit']}` lines `{code_hygiene_checks['research_audit_repo_too_large_for_primary_submission']}`; code-bloat risk remains `{code_hygiene_checks['code_bloat_risk_for_submission']}` until the full source-policy runner package is ready.",
        f"- Minimal reproducible submission code ready: `{code_hygiene_checks['minimal_reproducible_submission_code_ready']}`; code-bloat risk for submission: `{code_hygiene_checks['code_bloat_risk_for_submission']}`.",
        f"- Minimal reproducibility candidate: present `{code_hygiene_checks['minimal_reproducibility_candidate_present']}`, status `{code_hygiene_checks['minimal_reproducibility_candidate_status']}`, files `{code_hygiene_checks['minimal_reproducibility_candidate_file_count']}`, Python files/lines `{code_hygiene_checks['minimal_reproducibility_candidate_python_file_count']}/{code_hygiene_checks['minimal_reproducibility_candidate_python_lines']}`, size-ok `{code_hygiene_checks['minimal_reproducibility_candidate_code_size_ok']}`, submission ready `{code_hygiene_checks['minimal_reproducibility_candidate_submission_ready']}`.",
        f"- Minimal reproducibility candidate boundary: source-policy `{code_hygiene_checks['minimal_reproducibility_candidate_source_policy_closed_rows']}/{code_hygiene_checks['minimal_reproducibility_candidate_source_policy_total_rows']}`, direct-PC2 route closed under retained theorem interfaces `{code_hygiene_checks['minimal_reproducibility_candidate_proof_gap_closed']}`, replay-only `{code_hygiene_checks['minimal_reproducibility_candidate_replay_only']}`, runner-centered `{code_hygiene_checks['minimal_reproducibility_candidate_runner_centered']}`.",
        f"- Minimal submission code dependency boundary: `{code_hygiene_checks['minimal_submission_code_dependency_boundary']['status']}`; safe use `{code_hygiene_checks['minimal_submission_code_dependency_boundary']['safe_current_package_use']}`; blockers `{','.join(code_hygiene_checks['minimal_submission_code_dependency_boundary']['blocking_upstream_gates'])}`.",
        f"- Local accepted-row runner/full source-policy runner ready: `{code_hygiene_checks['local_runner_centered_candidate_ready']}/{code_hygiene_checks['full_source_policy_runner_package_ready']}`; runner audit `{code_hygiene_checks['runner_centered_audit_status']}`.",
        f"- Paper core result table ready: `{code_hygiene_checks['paper_core_result_table_ready']}`; source-policy rows closed `{code_hygiene_checks['source_policy_closed_rows']}/{code_hygiene_checks['source_policy_total_rows']}`.",
        f"- Runner status: RA2021 public baselines `{code_hygiene_checks['ra2021_public_baselines_present']}`, HI2022 bounded rows `{code_hygiene_checks['hi2022_bounded_rows_present']}`, TFE source-policy runner implemented `{code_hygiene_checks['tfe_source_policy_runner_implemented']}`.",
        f"- TFE source pendulum parameter/smoke/absolute-residual/time-smoke/output/candidate friction: `{code_hygiene_checks['tfe_source_pendulum_parameter_model_implemented']}/{code_hygiene_checks['tfe_source_pendulum_frictionless_smoke_implemented']}/{code_hygiene_checks['tfe_source_pendulum_absolute_coordinate_dae_residual_smoke_implemented']}/{code_hygiene_checks['tfe_source_pendulum_source_output_time_integration_smoke_implemented']}/{code_hygiene_checks['tfe_source_pendulum_error_output_policy_encoded']}/{code_hygiene_checks['tfe_source_pendulum_brown_mcphee_candidate_friction_law_encoded']}`.",
        f"- TFE source pendulum bounded reference-policy smoke/full T=10 source run: `{code_hygiene_checks['tfe_source_pendulum_source_reference_solution_policy_smoke_implemented']}/{code_hygiene_checks['tfe_source_pendulum_source_reference_solution_policy_smoke_full_T10']}`.",
        f"- TFE source pendulum full-T=10 source-reference feasibility probe: implemented/completed/source-policy rows `{code_hygiene_checks['tfe_source_pendulum_source_reference_solution_policy_full_T10_probe_implemented']}/{code_hygiene_checks['tfe_source_pendulum_source_reference_solution_policy_full_T10_probe_completed']}/{code_hygiene_checks['tfe_source_pendulum_source_reference_solution_policy_full_T10_probe_rows_completed']}`; source/check steps `{code_hygiene_checks['tfe_source_pendulum_source_reference_solution_policy_full_T10_probe_steps']}/{code_hygiene_checks['tfe_source_pendulum_source_reference_solution_policy_full_T10_probe_check_steps']}`; coordinate/velocity check errors `{code_hygiene_checks['tfe_source_pendulum_source_reference_solution_policy_full_T10_probe_coordinate_error']:.3e}/{code_hygiene_checks['tfe_source_pendulum_source_reference_solution_policy_full_T10_probe_velocity_error']:.3e}`.",
        f"- TFE source pendulum comparator candidate runners/Newmark/trapezoidal/TFE-m-candidate/method-equivalent/TFE m=1-3 source-policy: `{code_hygiene_checks['tfe_source_pendulum_source_comparator_candidate_runners_implemented']}/{code_hygiene_checks['tfe_source_pendulum_newmark_beta_candidate_runner_smoke_implemented']}/{code_hygiene_checks['tfe_source_pendulum_trapezoidal_candidate_runner_smoke_implemented']}/{code_hygiene_checks['tfe_source_pendulum_tfe_m1_m2_m3_candidate_runner_smoke_implemented']}/{code_hygiene_checks['tfe_source_pendulum_source_policy_method_runner_equivalent']}/{code_hygiene_checks['tfe_source_pendulum_tfe_m1_m2_m3_source_policy_runners_implemented']}`.",
        f"- TFE source pendulum Gauss6 candidate smoke/absolute-coordinate source-policy runner: `{code_hygiene_checks['tfe_source_pendulum_gauss6_candidate_smoke_implemented']}/{code_hygiene_checks['tfe_source_pendulum_gauss6_absolute_coordinate_source_policy_runner_implemented']}`.",
        f"- TFE source pendulum Gauss6 candidate rows/source-policy rows/method-equivalent: `{code_hygiene_checks['tfe_source_pendulum_gauss6_candidate_rows']}/{code_hygiene_checks['tfe_source_pendulum_gauss6_candidate_source_policy_rows_completed']}/{code_hygiene_checks['tfe_source_pendulum_gauss6_candidate_method_equivalent']}`.",
        f"- TFE source pendulum Appendix-B coefficient certificate: `{code_hygiene_checks['tfe_source_pendulum_appendix_b_coefficient_certificate_checked']}`; rows/max diff `{code_hygiene_checks['tfe_source_pendulum_appendix_b_coefficient_certificate_rows']}/{code_hygiene_checks['tfe_source_pendulum_appendix_b_coefficient_certificate_max_abs_diff']:.3e}`.",
        f"- TFE source pendulum unified bounded runner rows/full T=10/source-policy rows: `{code_hygiene_checks['tfe_source_pendulum_bounded_source_policy_runner_rows']}/{code_hygiene_checks['tfe_source_pendulum_bounded_source_policy_runner_full_T10']}/{code_hygiene_checks['tfe_source_pendulum_bounded_source_policy_runner_source_policy_rows_completed']}`.",
        f"- TFE source pendulum active-B2 candidate rows/full T=10/source-policy rows: `{code_hygiene_checks['tfe_source_pendulum_active_b2_candidate_row_count']}/{code_hygiene_checks['tfe_source_pendulum_active_b2_candidate_row_smoke_full_T10']}/{code_hygiene_checks['tfe_source_pendulum_active_b2_source_policy_rows_completed']}`.",
        f"- TFE source pendulum active-B2 full-T10 coarse probe: implemented/fullT10/source-policy rows/finite/residual-ok/source-ref-invoked `{code_hygiene_checks['tfe_source_pendulum_active_b2_full_T10_coarse_probe_implemented']}/{code_hygiene_checks['tfe_source_pendulum_active_b2_full_T10_coarse_probe_full_T10']}/{code_hygiene_checks['tfe_source_pendulum_active_b2_full_T10_coarse_probe_source_policy_rows']}/{code_hygiene_checks['tfe_source_pendulum_active_b2_full_T10_coarse_probe_finite_rows']}/{code_hygiene_checks['tfe_source_pendulum_active_b2_full_T10_coarse_probe_residual_ok_rows']}/{code_hygiene_checks['tfe_source_pendulum_active_b2_full_T10_coarse_probe_reference_invoked']}`.",
        f"- TFE source pendulum active-B2 source-reference full-T10 probe: implemented/fullT10/reference-invoked/source-policy rows/finite/residual-ok/method-equivalent `{code_hygiene_checks['tfe_source_pendulum_active_b2_source_reference_full_T10_probe_implemented']}/{code_hygiene_checks['tfe_source_pendulum_active_b2_source_reference_full_T10_probe_full_T10']}/{code_hygiene_checks['tfe_source_pendulum_active_b2_source_reference_full_T10_probe_reference_invoked']}/{code_hygiene_checks['tfe_source_pendulum_active_b2_source_reference_full_T10_probe_source_policy_rows']}/{code_hygiene_checks['tfe_source_pendulum_active_b2_source_reference_full_T10_probe_finite_rows']}/{code_hygiene_checks['tfe_source_pendulum_active_b2_source_reference_full_T10_probe_residual_ok_rows']}/{code_hygiene_checks['tfe_source_pendulum_active_b2_source_reference_full_T10_probe_method_equivalent']}`.",
        f"- TFE source pendulum m=3 full-T10 formula probe: implemented/fullT10/expected/source-policy rows/finite/residual-ok/source-ref-invoked `{code_hygiene_checks['tfe_source_pendulum_tfe_m3_full_T10_formula_probe_implemented']}/{code_hygiene_checks['tfe_source_pendulum_tfe_m3_full_T10_formula_probe_full_T10']}/{code_hygiene_checks['tfe_source_pendulum_tfe_m3_full_T10_formula_probe_expected_order']}/{code_hygiene_checks['tfe_source_pendulum_tfe_m3_full_T10_formula_probe_source_policy_rows']}/{code_hygiene_checks['tfe_source_pendulum_tfe_m3_full_T10_formula_probe_finite_rows']}/{code_hygiene_checks['tfe_source_pendulum_tfe_m3_full_T10_formula_probe_residual_ok_rows']}/{code_hygiene_checks['tfe_source_pendulum_tfe_m3_full_T10_formula_probe_reference_invoked']}`.",
        f"- Recommended submission-code shape: {code_hygiene_checks['recommended_submission_code_shape']}.",
        "",
        "## Future Full Source-Policy Reintroduction Board",
        "",
        f"- Closeout status: `{closeout_actionability_checks['status']}`.",
        f"- First gate to work: `{closeout_actionability_checks['first_gate_to_work']}`.",
        "| rank | gate | status | closed/total | blocking reason |",
        "|---:|---|---:|---:|---|",
    ]
    )
    for item in closeout_actionability_checks["ordered_gates"]:
        lines.append(
            f"| `{item['rank']}` | {item['gate']} | `{item['status']}` | "
            f"`{item['closed_rows']}/{item['total_rows']}` | {item['blocking_reason']} |"
        )
    lines.extend(
        [
            "",
            f"- Do not spend on before B4/B7 closure: `{closeout_actionability_checks['do_not_spend_on_before_source_policy']}`.",
            f"- Source-policy route A: `{closeout_actionability_checks['source_policy_closure_routes'][0]['route']}` / `{closeout_actionability_checks['source_policy_closure_routes'][0]['status']}`; explicit 1e-4 opt-in `{closeout_actionability_checks['source_policy_closure_routes'][0]['requires_explicit_1e_4_opt_in']}`; rows `{closeout_actionability_checks['source_policy_closure_routes'][0]['current_closed_rows']}/{closeout_actionability_checks['source_policy_closure_routes'][0]['current_total_rows']}`.",
            f"- Source-policy route B: `{closeout_actionability_checks['source_policy_closure_routes'][1]['route']}` / `{closeout_actionability_checks['source_policy_closure_routes'][1]['status']}`; claim after route `{closeout_actionability_checks['source_policy_closure_routes'][1]['claim_after_route']}`; additional demotions `{closeout_actionability_checks['source_policy_closure_routes'][1]['additional_demotions_needed']}`.",
            f"- Route B demotion audit: `{external_checks['claim_demotion_audit_schema']}` / `{external_checks['claim_demotion_audit_status']}`; ready `{external_checks['claim_demotion_audit_route_b_ready']}`; B2/B4 closed by route `{external_checks['claim_demotion_audit_b2_gate_closed_by_route_b']}/{external_checks['claim_demotion_audit_b4_gate_closed_by_route_b']}`; source-policy execution rows `{external_checks['claim_demotion_audit_source_policy_rows_closed']}/{external_checks['claim_demotion_audit_source_policy_total_rows']}`.",
            f"- Route B application contract: `{external_checks['claim_demotion_route_b_contract_schema']}`; ready-to-promote `{external_checks['claim_demotion_route_b_ready_to_promote']}`; safe flag flip `{external_checks['claim_demotion_route_b_safe_to_flip_flags']}`; satisfied steps `{external_checks['claim_demotion_route_b_satisfied_steps']}/{external_checks['claim_demotion_route_b_total_steps']}`; unsatisfied `{external_checks['claim_demotion_route_b_unsatisfied_steps']}`.",
        "",
        "## Submission Integrity Checks",
        "",
        f"- Submission-integrity audit: `{submission_integrity_checks['schema']}` / `{submission_integrity_checks['status']}`.",
        f"- Local integrity passed/submission ready: `{submission_integrity_checks['local_integrity_passed']}` / `{submission_integrity_checks['submission_ready']}`.",
        f"- Citation keys main/flat: `{submission_integrity_checks['main_cited_key_count']}/{submission_integrity_checks['flat_cited_key_count']}`; bibitems main/flat `{submission_integrity_checks['main_bibitem_count']}/{submission_integrity_checks['flat_bibitem_count']}`.",
        f"- Citation/bibitem key parity main-flat: `{submission_integrity_checks['main_and_flat_citation_keys_match']}/{submission_integrity_checks['main_and_flat_bibitem_keys_match']}`.",
        f"- Dangling citation keys main/flat: `{len(submission_integrity_checks['main_dangling_citation_keys'])}/{len(submission_integrity_checks['flat_dangling_citation_keys'])}`; orphan bibitems main/flat `{len(submission_integrity_checks['main_orphan_bibitem_keys'])}/{len(submission_integrity_checks['flat_orphan_bibitem_keys'])}`.",
        f"- Unresolved citation/reference log lines main/flat: `{len(submission_integrity_checks['main_unresolved_log_lines'])}/{len(submission_integrity_checks['flat_unresolved_log_lines'])}`.",
        f"- References heading main/flat PDF: `{submission_integrity_checks['pdf_references_heading_present']}/{submission_integrity_checks['flat_pdf_references_heading_present']}`.",
        f"- Sidecar declarations/highlights/cover letter: `{submission_integrity_checks['declaration_tokens_present']}/{submission_integrity_checks['flat_declaration_tokens_present']}`; highlights `{submission_integrity_checks['highlight_count']}/{submission_integrity_checks['flat_highlight_count']}`; cover `{submission_integrity_checks['cover_letter_mentions_journal']}/{submission_integrity_checks['cover_letter_mentions_recommended_pdf']}`.",
        f"- Reference metadata audit: `{submission_integrity_checks['reference_metadata_status']}`; DOI metadata `{submission_integrity_checks['reference_metadata_doi_verified_count']}/{submission_integrity_checks['reference_metadata_doi_reference_count']}`; non-DOI metadata `{submission_integrity_checks['reference_metadata_non_doi_verified_count']}/{submission_integrity_checks['reference_metadata_local_non_doi_count']}`; non-DOI references open `{submission_integrity_checks['reference_metadata_non_doi_count']}`.",
        f"- External reference web verification complete: `{submission_integrity_checks['external_reference_web_verification_complete']}`.",
        f"- Submission integrity gate closed: `{submission_integrity_checks['submission_integrity_gate_closed']}`.",
        "",
        "## Proof And Baseline Checks",
        "",
        f"- Proof-closure manifest: `{proof_checks['proof_closure_manifest_schema']}`.",
        f"- Proof-closure status: `{proof_checks['proof_closure_manifest_status']}`.",
        f"- Proof-claim traceability audit: `{proof_checks['proof_claim_traceability_schema']}` / `{proof_checks['proof_claim_traceability_status']}`.",
        f"- Proof remaining-work manifest: `{proof_checks['proof_remaining_work_schema']}` / `{proof_checks['proof_remaining_work_status']}`.",
        f"- Proof remaining-work submission-ready scope: `{proof_checks['proof_remaining_work_submission_ready_scope']}`; manifest scope `{proof_checks['proof_remaining_work_manifest_scope']}`.",
        f"- Proof remaining-work narrowed B4/B6/B7 statuses: `{proof_checks['proof_remaining_work_narrowed_claim_b4_b6_b7_statuses']['B4']}/{proof_checks['proof_remaining_work_narrowed_claim_b4_b6_b7_statuses']['B6']}/{proof_checks['proof_remaining_work_narrowed_claim_b4_b6_b7_statuses']['B7']}`; global boundaries `{','.join(proof_checks['proof_remaining_work_global_submission_boundaries_retained'])}`.",
        f"- Proof remaining-work unsatisfied close requirements: `{proof_checks['proof_remaining_work_unsatisfied_close_requirements']}` / `{proof_checks['proof_remaining_work_unsatisfied_close_requirement_ids']}`.",
        f"- Proof remaining-work row split/links: `{proof_checks['proof_remaining_work_certified_non_dynamic_rows']}/{proof_checks['proof_remaining_work_open_dynamic_rows']}` rows, `{proof_checks['proof_remaining_work_newton_euler_row_obligation_links']}` Newton-Euler links.",
        f"- Proof remaining-work Newton-Euler certificate present/complete: `{proof_checks['proof_remaining_work_newton_euler_certificate_present']}/{proof_checks['proof_remaining_work_newton_euler_certificate_complete']}`.",
        f"- Proof remaining-work Newton-Euler runtime expression structure checked/rows: `{proof_checks['proof_remaining_work_newton_euler_runtime_expression_structure_checked']}/{proof_checks['proof_remaining_work_newton_euler_runtime_expression_checked_rows']}`.",
        f"- Proof remaining-work Newton-Euler runtime template instantiation checked/rows: `{proof_checks['proof_remaining_work_newton_euler_runtime_template_instantiation_checked']}/{proof_checks['proof_remaining_work_newton_euler_runtime_template_instantiation_checked_rows']}`.",
        f"- Newton-Euler symbolic defect certificate artifact: `{proof_checks['newton_euler_symbolic_defect_certificate_artifact_schema']}` / `{proof_checks['newton_euler_symbolic_defect_certificate_artifact_status']}`.",
        f"- Newton-Euler symbolic defect certificate rows certified/open/links: `{proof_checks['newton_euler_symbolic_defect_certificate_artifact_certified_rows']}/{proof_checks['newton_euler_symbolic_defect_certificate_artifact_open_rows']}` / `{proof_checks['newton_euler_symbolic_defect_certificate_artifact_row_obligation_links']}`; complete `{proof_checks['newton_euler_symbolic_defect_certificate_artifact_complete']}`.",
        f"- Newton-Euler runtime expression structure checked/rows: `{proof_checks['newton_euler_symbolic_defect_certificate_artifact_runtime_expression_structure_checked']}/{proof_checks['newton_euler_symbolic_defect_certificate_artifact_runtime_expression_checked_rows']}`; this is source-expression traceability, not proof closure.",
        f"- Newton-Euler runtime template instantiation checked/rows: `{proof_checks['newton_euler_symbolic_defect_certificate_artifact_runtime_template_instantiation_checked']}/{proof_checks['newton_euler_symbolic_defect_certificate_artifact_runtime_template_instantiation_checked_rows']}`; this is row-template traceability, not algebraic proof closure.",
        f"- Newton-Euler body-specific wrench expansion checked/rows: `{proof_checks['newton_euler_symbolic_defect_certificate_artifact_body_specific_wrench_checked']}/{proof_checks['newton_euler_symbolic_defect_certificate_artifact_body_specific_wrench_rows']}`; body0/body1 `{proof_checks['newton_euler_symbolic_defect_certificate_artifact_body0_wrench_rows']}/{proof_checks['newton_euler_symbolic_defect_certificate_artifact_body1_wrench_rows']}`; this is sign-traceability, not proof closure.",
        f"- Newton-Euler template algebraic equivalence checked/rows/C2-subcheck: `{proof_checks['newton_euler_symbolic_defect_certificate_artifact_template_algebraic_equivalence_checked']}/{proof_checks['newton_euler_symbolic_defect_certificate_artifact_template_algebraic_equivalence_checked_rows']}/{proof_checks['newton_euler_symbolic_defect_certificate_artifact_c2_template_algebraic_equivalence_closed']}`; D1/D2 balance identities, direct-route D5 O(h^7) proof, and the B1 AD-expanded implementation-path certificate are closed, while primitive/global dynamic symbolic-oracle completion remains false.",
        f"- B1 independent residual symbolic row oracle: `{proof_checks['b1_independent_symbolic_row_by_row_oracle_for_expanded_fullva_rows_closed']}` with rows/source-template/runtime-binding `{proof_checks['b1_independent_symbolic_row_oracle_closed_rows']}/{proof_checks['b1_source_template_symbolic_identity_rows']}/{proof_checks['b1_runtime_row_binding_checked_rows']}`; row-certificate-only remaining item `{proof_checks['b1_symbolic_row_oracle_remaining_required_item']}`.",
        f"- B1 AD-expanded implementation-path certificate: `{proof_checks['b1_ad_expanded_symbolic_oracle_closure']}` with rows/columns/cells `{proof_checks['b1_ad_expanded_symbolic_oracle_closed_rows']}/{proof_checks['b1_ad_expanded_symbolic_oracle_columns_per_row']}/{proof_checks['b1_ad_expanded_symbolic_oracle_closed_cells']}`; primitive/global dynamic oracle/O(h^7) symbolic certificate/submission ready `{proof_checks['b1_ad_expanded_symbolic_oracle_dynamic_symbolic_oracle_complete']}/{proof_checks['b1_ad_expanded_symbolic_oracle_stage_residual_O_h7_symbolic_certificate_proved']}/{proof_checks['b1_ad_expanded_symbolic_oracle_submission_ready']}`.",
        f"- Newton-Euler AD-expanded row oracle: `{proof_checks['newton_euler_ad_expanded_row_oracle_closed']}` with rows/columns/probes `{proof_checks['newton_euler_ad_expanded_row_oracle_rows']}/{proof_checks['newton_euler_ad_expanded_row_oracle_columns_per_row']}/{proof_checks['newton_euler_ad_expanded_row_oracle_probe_count']}` and max mismatch `{proof_checks['newton_euler_ad_expanded_row_oracle_max_mismatch']}`; symbolic closure `{proof_checks['newton_euler_ad_expanded_symbolic_oracle_closure']}`.",
        f"- Proof remaining-work execution flags default1e-4/heavy/run_v047: `{proof_checks['proof_remaining_work_default_1e_4_required']}/{proof_checks['proof_remaining_work_heavy_run_invoked']}/{proof_checks['proof_remaining_work_run_v047_invoked']}`.",
        f"- Proof-claim traceability labels present: `{proof_checks['proof_claim_traceability_main_labels_present']}/{proof_checks['proof_claim_traceability_flat_labels_present']}`; boundary tokens `{proof_checks['proof_claim_traceability_main_boundary_tokens_present']}/{proof_checks['proof_claim_traceability_flat_boundary_tokens_present']}`.",
        f"- Proof-claim theorem traceability: label `{proof_checks['proof_claim_traceability_theorem_label']}`; labels/boundary/mapped `{proof_checks['proof_claim_traceability_theorem_labels_present']}/{proof_checks['proof_claim_traceability_theorem_boundary_present']}/{proof_checks['proof_claim_traceability_theorem_claims_mapped']}`; dependency/table/dynamic `{proof_checks['proof_claim_traceability_dependency_graph_present']}/{proof_checks['proof_claim_traceability_table_present']}/{proof_checks['proof_claim_traceability_dynamic_theorem_matrix_present']}`.",
        f"- Proof-claim theorem no-promotion boundary: primitive/residual `{proof_checks['proof_claim_traceability_primitive_lane_boundary_present']}/{proof_checks['proof_claim_traceability_residual_nonpromotion_present']}`; eta condition/closure/fixed proof `{proof_checks['proof_claim_traceability_eta_condition_retained']}/{proof_checks['proof_claim_traceability_eta_evidence_closed']}/{proof_checks['proof_claim_traceability_fixed_tolerance_asymptotic_proof']}`; residual/source-policy-full-TFE not promoted `{proof_checks['proof_claim_traceability_residual_to_error_not_promoted']}/{proof_checks['proof_claim_traceability_source_policy_or_full_tfe_not_promoted']}`; no-state-change `{proof_checks['proof_claim_traceability_no_state_change']}`.",
        f"- Proof-claim P7 output nonclaim/residual-to-error boundary present: `{proof_checks['proof_claim_traceability_p7_retained_nonpromotion_boundary_present']}`.",
        f"- Proof-claim B1 closure-scope boundary present: `{proof_checks['proof_claim_traceability_b1_closure_scope_boundary_present']}`.",
        f"- Proof-claim P6 solver-scope boundary present: `{proof_checks['proof_claim_traceability_p6_solver_scope_boundary_present']}`.",
        f"- Proof-claim P1/P2 compact-tube boundary present: `{proof_checks['proof_claim_traceability_p1p2_compact_tube_boundary_present']}`.",
        f"- Proof-claim P3/P4 implementation-defect boundary present: `{proof_checks['proof_claim_traceability_p3p4_implementation_boundary_present']}`.",
        f"- Proof-claim P5 direct-route boundary present: `{proof_checks['proof_claim_traceability_p5_direct_route_boundary_present']}`.",
        f"- Proof-claim proof-causality table present: `{proof_checks['proof_claim_traceability_proof_causality_ledger_present']}`.",
        f"- Proof-claim direct-route anti-circularity table present: `{proof_checks['proof_claim_traceability_direct_route_anticircularity_ledger_present']}`.",
        f"- Proof-claim theorem-interface satisfaction table present: `{proof_checks['proof_claim_traceability_p_interface_satisfaction_ledger_present']}`.",
        f"- Proof-claim P7 output nonclaim/residual-to-error boundary table present: `{proof_checks['proof_claim_traceability_p7_residual_to_error_ledger_present']}`.",
        f"- Proof-claim theorem-use rule present: `{proof_checks['proof_claim_traceability_theorem_use_rule_present']}`.",
        f"- Proof-claim quantifier/domain table present: `{proof_checks['proof_claim_traceability_quantifier_domain_ledger_present']}`.",
        f"- Proof-claim local-to-global transfer table present: `{proof_checks['proof_claim_traceability_local_global_transfer_ledger_present']}`.",
        f"- Proof-claim objective-completion boundary present: `{proof_checks['proof_claim_traceability_objective_completion_boundary_present']}`.",
        f"- Proof-claim constant-dependency table present: `{proof_checks['proof_claim_traceability_constant_dependency_ledger_present']}`.",
        f"- Proof-claim theorem dependency consumption table present: `{proof_checks['proof_claim_traceability_theorem_dependency_consumption_ledger_present']}`.",
        f"- Proof-claim accepted-branch consistency table present: `{proof_checks['proof_claim_traceability_branch_consistency_ledger_present']}`.",
        f"- Proof-claim implementation-route/oracle separation table present: `{proof_checks['proof_claim_traceability_implementation_route_oracle_ledger_present']}`.",
        f"- Proof-claim nonlinear-solver scale table present: `{proof_checks['proof_claim_traceability_nonlinear_solver_scale_ledger_present']}`.",
        f"- Proof-claim local-defect decomposition table present: `{proof_checks['proof_claim_traceability_local_defect_decomposition_ledger_present']}`.",
        f"- Proof-claim theorem output scope table present: `{proof_checks['proof_claim_traceability_theorem_output_scope_ledger_present']}`.",
        f"- Proof-claim reporting-map/norm-equivalence table present: `{proof_checks['proof_claim_traceability_reporting_map_ledger_present']}`.",
        f"- Proof-claim scope-of-conclusion statement present: `{proof_checks['proof_claim_traceability_theorem_conclusion_scope_guard_present']}`.",
        f"- Proof-claim proof-structure statement present: `{proof_checks['proof_claim_traceability_proof_strength_certificate_present']}`.",
        f"- Proof-claim full 132-row residual-defect bridge present: `{proof_checks['proof_claim_traceability_full_residual_bridge_present']}`.",
        f"- Proof-claim route-exclusivity nonmixing boundary present: `{proof_checks['proof_claim_traceability_route_exclusivity_boundary_present']}`.",
        f"- Proof-claim theorem residual-certificate exclusivity present: `{proof_checks['proof_claim_traceability_theorem_residual_certificate_exclusivity_present']}`.",
        f"- Proof-claim traceability partition counts satisfied/total/retained-interfaces/open-nonpromotion: `{proof_checks['proof_claim_traceability_satisfied_assumptions']}/{proof_checks['proof_claim_traceability_theorem_assumptions']}/{proof_checks['proof_claim_traceability_retained_theorem_interface_count']}/{proof_checks['proof_claim_traceability_open_nonpromotion_boundary_count']}`.",
        f"- Proof-claim remaining theorem-boundary partition: `{proof_checks['proof_claim_traceability_remaining_boundary_status']}`; satisfied IDs `{','.join(proof_checks['proof_claim_traceability_submission_satisfied_assumption_ids'])}`; retained theorem-interface IDs `{','.join(proof_checks['proof_claim_traceability_retained_theorem_interface_ids'])}`; open output-boundary IDs `{','.join(proof_checks['proof_claim_traceability_open_nonpromotion_boundary_ids'])}`; global boundaries `{','.join(proof_checks['proof_claim_traceability_remaining_global_boundaries'])}`.",
        f"- Proof-claim writing boundary card: `{proof_checks['proof_claim_traceability_writing_card_status']}`; safe claim `{proof_checks['proof_claim_traceability_writing_card_safe_claim']}`; forbidden `{','.join(proof_checks['proof_claim_traceability_writing_card_forbidden_claims'])}`.",
        f"- Proof-claim reader-facing manuscript/PDF boundary present: `{proof_checks['proof_claim_traceability_reader_facing_manuscript_boundary_present']}`.",
        f"- Proof-claim manuscript anchor map: `{proof_checks['proof_claim_traceability_manuscript_anchor_map_present']}`; label anchors `{proof_checks['proof_claim_traceability_manuscript_anchor_label_count']}`; theorem-interface/P7-output-boundary anchors `{proof_checks['proof_claim_traceability_theorem_assumption_anchor_count']}`; IDs `{','.join(proof_checks['proof_claim_traceability_theorem_assumption_anchor_ids'])}`.",
        f"- Proof-closure manuscript anchor map: `{proof_checks['proof_closure_manuscript_anchor_map_present']}`; label anchors `{proof_checks['proof_closure_manuscript_anchor_label_count']}`; theorem-interface/P7-output-boundary anchors `{proof_checks['proof_closure_theorem_assumption_anchor_count']}`; IDs `{','.join(proof_checks['proof_closure_theorem_assumption_anchor_ids'])}`; proof-claim map match `{proof_checks['proof_closure_proof_claim_anchor_maps_match']}`.",
        "- Reader-facing theorem-interface split: theorem interfaces `P1--P6`; P7 is an output nonclaim/residual-to-error boundary anchor, not a theorem premise.",
        f"- Proof anchor evidence sources: contract `{','.join(proof_checks['proof_contract_anchor_evidence_sources'])}`; style `{','.join(proof_checks['proof_style_anchor_evidence_sources'])}`; strict `{','.join(proof_checks['strict_proof_anchor_evidence_sources'])}`; source match `{proof_checks['proof_anchor_evidence_sources_match']}`.",
        f"- Proof-claim traceability close requirements/unsatisfied: `{proof_checks['proof_claim_traceability_close_requirements']}/{proof_checks['proof_claim_traceability_unsatisfied_close_requirements']}`.",
        f"- Proof-claim traceability close requirements satisfied: `{proof_checks['proof_claim_traceability_satisfied_close_requirements']}`; PC3 condition retained `{proof_checks['proof_claim_traceability_pc3_condition_retained']}`; PC4 residual promotion avoided `{proof_checks['proof_claim_traceability_pc4_residual_promotion_avoided']}`.",
        f"- Proof-claim traceability active direct Newton-Euler row split: `{proof_checks['proof_claim_traceability_active_direct_newton_euler_closed_rows']}/{proof_checks['proof_claim_traceability_active_direct_newton_euler_open_rows']}` closed/open.",
        f"- Proof-claim traceability symbolic/primitive dynamic rows not certified by that route: `{proof_checks['proof_claim_traceability_open_dynamic_rows']}` with scope `{proof_checks['proof_claim_traceability_open_dynamic_rows_scope']}`.",
        f"- Proof-claim traceability row-target map: `{proof_checks['proof_claim_traceability_row_target_map_present']}`; Newton-Euler target rows `{proof_checks['proof_claim_traceability_newton_euler_symbolic_target_rows']}` (`{proof_checks['proof_claim_traceability_newton_euler_symbolic_target_translational_rows']}/{proof_checks['proof_claim_traceability_newton_euler_symbolic_target_rotational_rows']}`); defect certificate `{proof_checks['proof_claim_traceability_newton_euler_symbolic_defect_certificate_complete']}`.",
        f"- Proof-claim traceability Newton-Euler obligation coverage: matrix `{proof_checks['proof_claim_traceability_newton_euler_obligation_coverage_matrix_complete']}`, links `{proof_checks['proof_claim_traceability_newton_euler_row_obligation_links']}`, complete rows `{proof_checks['proof_claim_traceability_newton_euler_rows_with_complete_obligation_sets']}`, proof closure advanced `{proof_checks['proof_claim_traceability_newton_euler_obligation_coverage_proof_closure_advanced']}`.",
        f"- Proof-claim traceability Newton-Euler obligations: active direct open `{proof_checks['proof_claim_traceability_active_direct_newton_euler_open_obligations']}`; symbolic/primitive open/closed `{proof_checks['proof_claim_traceability_symbolic_primitive_newton_euler_open_obligations']}/{proof_checks['proof_claim_traceability_newton_euler_closed_obligations']}`; residual-to-error `{proof_checks['proof_claim_traceability_residual_to_error_blockers']}`.",
        f"- Proof-claim traceability open symbolic oracle recorded: `{proof_checks['proof_claim_traceability_open_symbolic_oracle_recorded']}`.",
        f"- Dynamic-row residual-identity table: `{proof_checks['proof_claim_traceability_dynamic_matrix_present']}` / `{proof_checks['proof_claim_traceability_dynamic_matrix_status']}`.",
        f"- Proof-closure active direct Newton-Euler row split: `{proof_checks['proof_closure_active_direct_newton_euler_closed_rows']}/{proof_checks['proof_closure_active_direct_newton_euler_open_rows']}` closed/open.",
        f"- Proof-closure symbolic/primitive dynamic rows not certified by that route: `{proof_checks['proof_closure_open_dynamic_rows']}` with scope `{proof_checks['proof_closure_open_dynamic_rows_scope']}`.",
        f"- Proof-closure Newton-Euler obligations: active direct open `{proof_checks['proof_closure_active_direct_newton_euler_open_obligations']}`; symbolic/primitive open/closed `{proof_checks['proof_closure_symbolic_primitive_newton_euler_open_obligations']}/{proof_checks['proof_closure_newton_euler_closed_obligations']}` with scope `{proof_checks['proof_closure_newton_euler_open_obligations_scope']}`; residual-to-error `{proof_checks['proof_closure_residual_to_error_blocking_obligations']}`.",
        f"- Proof-closure Newton-Euler obligation coverage: matrix `{proof_checks['proof_closure_newton_euler_obligation_coverage_matrix_complete']}`, links `{proof_checks['proof_closure_newton_euler_row_obligation_links']}`, complete rows `{proof_checks['proof_closure_newton_euler_rows_with_complete_obligation_sets']}`.",
        f"- Newton-Euler symbolic target audit: `{proof_checks['newton_euler_symbolic_target_audit_schema']}` / `{proof_checks['newton_euler_symbolic_target_audit_status']}`; rows `{proof_checks['newton_euler_symbolic_target_rows']}` (`{proof_checks['newton_euler_symbolic_target_translational_rows']}/{proof_checks['newton_euler_symbolic_target_rotational_rows']}`); inventory `{proof_checks['newton_euler_symbolic_target_inventory_complete']}`; defect certificate `{proof_checks['newton_euler_symbolic_defect_certificate_complete']}`.",
        f"- Newton-Euler runtime source anchors: `{proof_checks['newton_euler_symbolic_target_runtime_source_anchors_present']}`; path `{proof_checks['newton_euler_symbolic_target_runtime_source_anchor_path']}`; tuple anchors `{proof_checks['newton_euler_symbolic_target_runtime_source_anchor_tuple_count']}`; primary dyn.extend line `{proof_checks['newton_euler_symbolic_target_runtime_source_anchor_dyn_extend_line']}`.",
        f"- Newton-Euler symbolic target obligation coverage: matrix `{proof_checks['newton_euler_obligation_coverage_matrix_complete']}`, links `{proof_checks['newton_euler_row_obligation_links']}`, complete rows `{proof_checks['newton_euler_rows_with_complete_obligation_sets']}`, proof closure advanced `{proof_checks['newton_euler_obligation_coverage_proof_closure_advanced']}`.",
        f"- Proof-closure direct-PC2 route/stage defect/eta_h closure: `{proof_checks['proof_closure_proof_gap_closed']}/{proof_checks['proof_closure_stage_residual_O_h7_implementation_defect_proved']}/{proof_checks['proof_closure_eta_h_O_h7_solver_policy_evidence']}`.",
        f"- Proof-closure theorem/manuscript traceability: labels/boundary/mapped `{proof_checks['proof_closure_theorem_statement_labels_present']}/{proof_checks['proof_closure_theorem_statement_boundary_present']}/{proof_checks['proof_closure_manuscript_traceability_mapped']}`; dependency/dynamic/primitive/nonpromotion `{proof_checks['proof_closure_manuscript_traceability_dependency_graph_present']}/{proof_checks['proof_closure_manuscript_traceability_dynamic_matrix_present']}/{proof_checks['proof_closure_manuscript_traceability_primitive_lane_boundary_present']}/{proof_checks['proof_closure_manuscript_traceability_residual_nonpromotion_present']}`.",
        f"- Proof-closure theorem no-promotion boundary: eta condition/closure `{proof_checks['proof_closure_theorem_statement_eta_condition_retained']}/{proof_checks['proof_closure_theorem_statement_eta_evidence_closed']}`; fixed-tolerance proof `{proof_checks['proof_closure_theorem_statement_fixed_tolerance_asymptotic_proof']}`; residual/source-policy-full-TFE not promoted `{proof_checks['proof_closure_theorem_statement_residual_to_error_not_promoted']}/{proof_checks['proof_closure_theorem_statement_source_policy_or_full_tfe_not_promoted']}`; no-state-change `{proof_checks['proof_closure_manuscript_traceability_no_state_change']}`.",
        f"- Runtime AD oracle complete: `{proof_checks['runtime_ad_oracle_complete']}`.",
        f"- Proof-style audit/reference checked: `{proof_checks['proof_style_reference_checked']}`.",
        f"- Newton-Euler obligation table/count: `{proof_checks['newton_euler_obligation_table_present']}/{proof_checks['newton_euler_obligation_count']}`.",
        f"- Conditional proof boundary visible in manuscript/PDF: `{result_checks['proof_conditional_boundary_visible']}`.",
        f"- Dynamic symbolic oracle complete: `{proof_checks['dynamic_symbolic_oracle_complete']}`.",
        f"- Symbolic oracle complete: `{proof_checks['symbolic_oracle_complete']}`.",
        f"- Symbolic-certificate stage residual O(h^7) route proved: `{proof_checks['dynamic_oracle_stage_residual_O_h7_symbolic_certificate_proved']}`.",
        f"- Direct-route stage residual O(h^7) defect proved: `{proof_checks['stage_residual_O_h7_implementation_defect_proved']}`.",
        f"- Solver-scale submission-ready scope: `{proof_checks['solver_scale_submission_ready_scope']}`; audit scope `{proof_checks['solver_scale_audit_scope']}`.",
        f"- Solver-scale narrowed B4/B6/B7 statuses: `{proof_checks['solver_scale_narrowed_claim_b4_b6_b7_statuses']['B4']}/{proof_checks['solver_scale_narrowed_claim_b4_b6_b7_statuses']['B6']}/{proof_checks['solver_scale_narrowed_claim_b4_b6_b7_statuses']['B7']}`; global boundaries `{','.join(proof_checks['solver_scale_global_submission_boundaries_retained'])}`.",
        f"- Finite scaled-tolerance probe rows/max eta-h ratio: `{proof_checks['finite_scaled_tolerance_probe_ok_rows']}/{proof_checks['finite_scaled_tolerance_probe_total_rows']}` / `{proof_checks['finite_scaled_tolerance_probe_max_residual_over_h7']:.6f}`; theorem closed `{proof_checks['finite_scaled_tolerance_probe_theorem_closed']}`.",
        f"- Finite scaled-tolerance trajectory probe rows/steps/max eta-h ratio: `{proof_checks['finite_scaled_tolerance_trajectory_probe_ok_rows']}/{proof_checks['finite_scaled_tolerance_trajectory_probe_total_rows']}` / `{proof_checks['finite_scaled_tolerance_trajectory_probe_steps']}` / `{proof_checks['finite_scaled_tolerance_trajectory_probe_max_residual_over_h7']:.6f}`; theorem closed `{proof_checks['finite_scaled_tolerance_trajectory_probe_theorem_closed']}`.",
        f"- Finite tolerance-regime sweep policies/rows/steps: `{proof_checks['finite_tolerance_regime_sweep_policy_count']}` / `{proof_checks['finite_tolerance_regime_sweep_total_rows']}` / `{proof_checks['finite_tolerance_regime_sweep_total_steps']}`; theorem closed `{proof_checks['finite_tolerance_regime_sweep_theorem_closed']}`.",
        f"- Finite h-scaled tolerance-regime sweep rows/steps/velocity-order floor: `{proof_checks['finite_h_scaled_tolerance_sweep_rows']}` / `{proof_checks['finite_h_scaled_tolerance_sweep_steps']}` / `{proof_checks['finite_h_scaled_tolerance_sweep_velocity_order_floor']}`.",
        f"- Theorem-level scaled tolerance sweep recorded: `{proof_checks['scaled_tolerance_sweep_recorded']}`.",
        f"- Same-test campaign status: `{external_checks['same_test_campaign_status']}`.",
        f"- Source-policy diagnosis: `{external_checks['source_policy_diagnosis_flagged_rows']}` flagged rows; position-aligned velocity mismatches `{external_checks['source_policy_position_aligned_velocity_mismatch_rows']}`.",
        f"- Source-policy recheck required: `{external_checks['source_policy_recheck_required']}`.",
        f"- Source-policy diagnosis B2/B4 status: `{external_checks['source_policy_diagnosis_b2_b4_status']}`.",
        f"- Source-policy closure triage: `{external_checks['source_policy_triage_flagged_rows']}` flagged rows across `{','.join(external_checks['source_policy_triage_flagged_examples'])}`.",
        f"- Source-policy triage B2/B4 can close now: `{external_checks['source_policy_triage_b2_can_close_now']}/{external_checks['source_policy_triage_b4_can_close_now']}`.",
        f"- Source-policy row closure ledger: `{external_checks['source_policy_row_ledger_flagged_rows']}` flagged rows across `{','.join(external_checks['source_policy_row_ledger_flagged_examples'])}`.",
        f"- Source-policy row ledger current dispositions: `{external_checks['source_policy_row_ledger_current_disposition_counts']}`.",
        f"- Source-policy row ledger attempted-not-reproducible/not-promoted rows: `{external_checks['source_policy_row_ledger_attempted_not_reproducible_rows']}`.",
        f"- Source-policy row ledger closed/claim-ready rows: `{external_checks['source_policy_row_ledger_rows_closed']}/{external_checks['source_policy_row_ledger_rows_external_superiority_ready']}`.",
        f"- Source-policy row ledger parallel-ready shards without default 1e-4: `{external_checks['source_policy_row_ledger_parallel_ready_shards']}`.",
        f"- Source-policy row ledger B2/B4 can close now: `{external_checks['source_policy_row_ledger_b2_can_close_now']}/{external_checks['source_policy_row_ledger_b4_can_close_now']}`.",
        f"- All-example source-policy audit: `{external_checks['all_examples_source_policy_flagged_rows']}` flagged rows and `{external_checks['all_examples_source_policy_flagged_raw_rows']}` raw rows across `{','.join(external_checks['all_examples_source_policy_flagged_examples'])}`.",
        f"- All-example source-policy suite counts: `{external_checks['all_examples_source_policy_flagged_by_suite']}`.",
        f"- All-example source-policy rows closed: `{external_checks['all_examples_source_policy_rows_closed']}`.",
        f"- All-example source-policy B2/B4 can close now: `{external_checks['all_examples_source_policy_b2_can_close_now']}/{external_checks['all_examples_source_policy_b4_can_close_now']}`.",
        f"- All-example source-policy default 1e-4/heavy run: `{external_checks['all_examples_source_policy_default_1e_4_required']}/{external_checks['all_examples_source_policy_heavy_run_invoked']}`.",
        f"- External suite dispositions: `{external_checks['suite_disposition_suite_count']}` suites; accepted external-superiority suites `{external_checks['suite_disposition_accepted_external_superiority_suite_count']}`.",
        f"- Suite-disposition parallel-ready shards without default 1e-4: `{external_checks['suite_disposition_parallel_ready_shards_without_default_1e_4']}`.",
        f"- Suite-disposition B2/B4 can close now: `{external_checks['suite_disposition_b2_can_close_now']}/{external_checks['suite_disposition_b4_can_close_now']}`.",
        f"- Source-policy closure manifest: `{external_checks['source_policy_closure_performance_completed_rows']}/{external_checks['source_policy_closure_performance_total_rows']}` performance rows completed; not-complete `{external_checks['source_policy_closure_performance_not_complete_rows']}`.",
        f"- Source-policy closure strict external error rows: `{external_checks['source_policy_closure_strict_external_error_rows']}`.",
        f"- Source-policy closure runnable suites: `{external_checks['source_policy_closure_runnable_parallel_suites']}`.",
        f"- Source-policy closure not-ready/demote suites: `{external_checks['source_policy_closure_not_ready_or_demote_suites']}`.",
        f"- Source-policy closure B2/B4 can close now: `{external_checks['source_policy_closure_b2_can_close_now']}/{external_checks['source_policy_closure_b4_can_close_now']}`.",
        f"- External case evidence reconciliation: case statuses `{external_checks['external_case_reconciliation_case_status_counts']}`; bounded evidence suites `{external_checks['external_case_reconciliation_bounded_suites']}`.",
        f"- External case reconciliation not-ready/demote suites: `{external_checks['external_case_reconciliation_not_ready_suites']}`.",
        f"- External case reconciliation 2021 public baseline/timing rows: `{external_checks['external_case_reconciliation_ra2021_baseline_groups']}/{external_checks['external_case_reconciliation_ra2021_baseline_required_groups']}` groups and `{external_checks['external_case_reconciliation_ra2021_timing_rows']}/{external_checks['external_case_reconciliation_ra2021_timing_required_rows']}` timing rows.",
        f"- External case reconciliation local source-policy dynamic-order examples: `{external_checks['external_case_reconciliation_local_dynamic_order_examples']}/4`; double public policy `{external_checks['external_case_reconciliation_gauss_double_public_policy']}`; closed-loop row kind `{external_checks['external_case_reconciliation_closed_loop_row_kind']}`.",
        f"- External case reconciliation closed/claim-ready rows: `{external_checks['external_case_reconciliation_rows_closed']}/{external_checks['external_case_reconciliation_rows_external_superiority_ready']}`.",
        f"- External case reconciliation accepted dynamic-order examples and B2/B4: `{external_checks['external_case_reconciliation_accepted_external_dynamic_order_examples']}` and `{external_checks['external_case_reconciliation_b2_can_close_now']}/{external_checks['external_case_reconciliation_b4_can_close_now']}`.",
        f"- HI2022 policy decision audit: `{external_checks['hi2022_policy_decision_status']}`; bounded rows `{external_checks['hi2022_bounded_ok_row_count']}/{external_checks['hi2022_bounded_row_count']}`, bounded groups `{external_checks['hi2022_bounded_groups_with_three_step_sizes']}/{external_checks['hi2022_bounded_group_count']}`.",
        f"- HI2022 bounded policy: T values `{external_checks['hi2022_bounded_t_end_values']}`, h values `{external_checks['hi2022_bounded_step_sizes']}`; full T=8 required/completed `{external_checks['hi2022_full_T8_policy_required']}/{external_checks['hi2022_full_T8_policy_completed']}`.",
        f"- HI2022 bounded/external acceptance: `{external_checks['hi2022_accepted_for_bounded_evidence']}/{external_checks['hi2022_accepted_for_external_superiority']}`; source-policy dynamic-order examples `{external_checks['hi2022_accepted_source_policy_dynamic_order_examples']}/4`.",
        f"- HI2022 decision/shards/default 1e-4/heavy/run_v047: `{external_checks['hi2022_decision']}` / `{external_checks['hi2022_queue_parallel_shard_count']}` / `{external_checks['hi2022_default_1e_4_required']}` / `{external_checks['hi2022_heavy_run_invoked']}` / `{external_checks['hi2022_run_v047_invoked']}`.",
        f"- HI2022 source-policy row audit: `{external_checks['hi2022_source_policy_audit_schema']}` / `{external_checks['hi2022_source_policy_audit_status']}`.",
        f"- HI2022 source-policy active/closed/claim-ready rows: `{external_checks['hi2022_source_policy_active_b2_flagged_rows']}/{external_checks['hi2022_source_policy_reproduction_rows']}/{external_checks['hi2022_source_policy_external_superiority_ready_rows']}`.",
        f"- HI2022 source-policy bounded rows/groups: `{external_checks['hi2022_source_policy_bounded_ok_row_count']}/{external_checks['hi2022_source_policy_bounded_row_count']}` and `{external_checks['hi2022_source_policy_bounded_groups_with_three_step_sizes']}/{external_checks['hi2022_source_policy_bounded_group_count']}`.",
        f"- HI2022 T=8 coarse sanity rows/groups: `{external_checks['hi2022_source_policy_t8_coarse_ok_rows']}/{external_checks['hi2022_source_policy_t8_coarse_rows']}` and `{external_checks['hi2022_source_policy_t8_coarse_complete_groups']}/{external_checks['hi2022_source_policy_t8_coarse_group_count']}`; source-policy reproduction `{external_checks['hi2022_source_policy_t8_coarse_source_policy_reproduction']}`; v048 runner evidence `{external_checks['hi2022_source_policy_t8_coarse_v048_runner_invoked']}`.",
        f"- HI2022 T=8 second tolerance sweep: `{external_checks['hi2022_t8_tolerance_repair_latest_ok_rows']}/{external_checks['hi2022_t8_tolerance_repair_latest_rows']}` rows and `{external_checks['hi2022_t8_tolerance_repair_latest_complete_groups']}/{external_checks['hi2022_t8_tolerance_repair_latest_group_count']}` groups.",
        f"- HI2022 T=8 tolerance repair combined best: `{external_checks['hi2022_t8_tolerance_repair_combined_best_ok_rows']}/{external_checks['hi2022_t8_tolerance_repair_combined_best_rows']}` rows and `{external_checks['hi2022_t8_tolerance_repair_combined_best_complete_groups']}/{external_checks['hi2022_t8_tolerance_repair_combined_best_group_count']}` groups; recovered rows `{external_checks['hi2022_t8_tolerance_repair_recovered_rows']}`; source-policy reproduction `{external_checks['hi2022_t8_tolerance_repair_source_policy_closed']}`; external superiority `{external_checks['hi2022_t8_tolerance_repair_external_superiority_allowed']}`.",
        f"- HI2022 can close B2 now/default 1e-4/heavy/run_v047: `{external_checks['hi2022_source_policy_can_close_b2_requirement_now']}/{external_checks['hi2022_source_policy_default_1e_4_required']}/{external_checks['hi2022_source_policy_heavy_run_invoked']}/{external_checks['hi2022_source_policy_run_v047_invoked']}`.",
        f"- VP2024 code-path disposition: `{external_checks['vp2024_disposition_status']}`; examples `{','.join(external_checks['vp2024_examples_checked'])}`.",
        f"- VP2024 source-policy rows unresolved: `{external_checks['vp2024_source_policy_code_path_unresolved_rows']}/{external_checks['vp2024_source_policy_rows']}`; distinct public code path found `{external_checks['vp2024_distinct_public_code_path_found']}`.",
        f"- VP2024 source-policy attempted/unable/final disposition: `{external_checks['vp2024_source_policy_rows_attempted_not_reproducible']}/{external_checks['vp2024_unable_to_reproduce_rows']}/{external_checks['vp2024_final_nonpublic_code_disposition']}`.",
        f"- Source-policy public-code refresh: `{external_checks['source_policy_public_code_refresh_status']}` on `{external_checks['source_policy_public_code_refresh_date']}`; rows/public-code/attempted/unable/closed `{external_checks['source_policy_public_code_refresh_rows']}/{external_checks['source_policy_public_code_refresh_public_code_available_rows']}/{external_checks['source_policy_public_code_refresh_self_reproduction_attempted_rows']}/{external_checks['source_policy_public_code_refresh_unable_to_reproduce_rows']}/{external_checks['source_policy_public_code_refresh_source_policy_rows_closed']}`.",
        f"- Latest public-code refresh supplement: `{external_checks['source_policy_public_code_refresh_latest_status']}` on `{external_checks['source_policy_public_code_refresh_latest_date']}`; rows/queries/positive/closed/promoted `{external_checks['source_policy_public_code_refresh_latest_rows']}/{external_checks['source_policy_public_code_refresh_latest_current_queries']}/{external_checks['source_policy_public_code_refresh_latest_positive_artifact_rows']}/{external_checks['source_policy_public_code_refresh_latest_source_policy_rows_closed']}/{external_checks['source_policy_public_code_refresh_latest_source_policy_rows_promoted']}`.",
        f"- VP2024 public-code recheck: `{external_checks['vp2024_public_code_recheck_status']}` on `{external_checks['vp2024_public_code_recheck_date']}`; tree truncated `{external_checks['vp2024_public_code_recheck_tree_truncated']}`; paths/all-2024/keyword-hits `{external_checks['vp2024_public_code_recheck_tree_total_paths']}/{external_checks['vp2024_public_code_recheck_year2024_paths']}/{external_checks['vp2024_public_code_recheck_keyword_hits']}`; attempted-not-reproducible/closed `{external_checks['vp2024_public_code_recheck_attempted_not_reproducible_rows']}/{external_checks['vp2024_public_code_recheck_source_policy_rows_closed']}`; external superiority `{external_checks['vp2024_public_code_recheck_external_superiority_allowed']}`.",
        f"- VP2024 local public-code scan: sbel dirs `{','.join(external_checks['vp2024_local_sbel_top_level_directories'])}`; visible MBD roots `{len(external_checks['vp2024_local_visible_mbd_code_roots'])}`; velocity-partition hits `{external_checks['vp2024_local_velocity_partition_term_hit_count']}`; local distinct path `{external_checks['vp2024_local_distinct_vp2024_code_path_found']}`.",
        f"- VP2024 common-reference proxy diagnostic favorable local order/error cells: `{external_checks['vp2024_common_reference_local_order_wins']}/{external_checks['vp2024_common_reference_proxy_rows']}` and `{external_checks['vp2024_common_reference_local_error_wins']}/{external_checks['vp2024_common_reference_proxy_rows']}`; VP source-policy code path remains unresolved.",
        f"- VP2024 larger-step diagnostic local error wins: `{external_checks['vp2024_large_step_local_error_wins']}/{external_checks['vp2024_source_policy_rows']}`; noncontrolling `{external_checks['vp2024_large_step_noncontrolling']}`.",
        f"- VP2024 proxy/source-policy boundary: proxy reproduction `{external_checks['vp2024_proxy_is_source_policy_reproduction']}`; claim allowed `{external_checks['vp2024_claim_allowed_now']}`; default 1e-4/heavy run `{external_checks['vp2024_default_1e_4_required']}/{external_checks['vp2024_heavy_run_invoked']}`.",
        f"- External suite demotion ledger: `{external_checks['external_suite_demotion_schema']}` / `{external_checks['external_suite_demotion_status']}`.",
        f"- External suite demotion closed B2 subrequirements: `{external_checks['external_suite_demotion_b2_closed_subrequirements']}`.",
        f"- External suite demotion remaining B2 requirements: `{external_checks['external_suite_demotion_b2_remaining_required']}`.",
        f"- External suite demotion VP2024 rows/flagged rows: `{external_checks['external_suite_demotion_vp2024_demoted_rows']}/{external_checks['external_suite_demotion_vp2024_demoted_flagged_rows']}`; active flagged rows `{external_checks['external_suite_demotion_active_flagged_rows']}`.",
        f"- External suite demotion HI2022 rows/flagged rows: `{external_checks['external_suite_demotion_hi2022_demoted_rows']}/{external_checks['external_suite_demotion_hi2022_demoted_flagged_rows']}`.",
        f"- External suite demotion remaining open suites: `{external_checks['external_suite_demotion_remaining_open_suites']}`; external superiority allowed `{external_checks['external_suite_demotion_external_superiority_allowed']}`.",
        f"- External suite demotion default 1e-4/heavy/run_v047: `{external_checks['external_suite_demotion_default_1e_4_required']}/{external_checks['external_suite_demotion_heavy_run_invoked']}/{external_checks['external_suite_demotion_run_v047_invoked']}`.",
        f"- B2 source-policy remaining-work manifest: `{external_checks['b2_remaining_work_schema']}` / `{external_checks['b2_remaining_work_status']}`.",
        f"- B2 remaining-work active/demoted flagged rows: `{external_checks['b2_remaining_work_active_flagged_rows']}/{external_checks['b2_remaining_work_demoted_flagged_rows']}` from `{external_checks['b2_remaining_work_row_count']}` total.",
        f"- B2 remaining-work source-policy closed/claim-ready rows: `{external_checks['b2_remaining_work_source_policy_closed_rows']}/{external_checks['b2_remaining_work_external_superiority_ready_rows']}`.",
        f"- B2 remaining-work active suite counts: `{external_checks['b2_remaining_work_active_suite_counts']}`; demoted suite counts `{external_checks['b2_remaining_work_demoted_suite_counts']}`.",
        f"- B2 remaining-work closed by demotion: `{external_checks['b2_remaining_work_closed_by_demotion']}`.",
        f"- B2 remaining-work required to close: `{external_checks['b2_remaining_work_remaining_requirements']}`.",
        f"- B2 remaining-work default 1e-4/heavy/run_v047: `{external_checks['b2_remaining_work_default_1e_4_required']}/{external_checks['b2_remaining_work_heavy_run_invoked']}/{external_checks['b2_remaining_work_run_v047_invoked']}`.",
        f"- B2 closure execution plan: `{external_checks['b2_closure_execution_plan_schema']}`; lanes `{external_checks['b2_closure_execution_plan_lane_count']}`; all active suites ready `{external_checks['b2_closure_execution_plan_all_active_suites_ready']}`; explicit 1e-4 opt-in `{external_checks['b2_closure_execution_plan_explicit_1e_4_opt_in']}`; plan-only superiority `{external_checks['b2_closure_execution_plan_external_superiority_after_plan_only']}`.",
        f"- B4 work/precision execution plan: `{external_checks['b4_work_precision_plan_schema']}` / `{external_checks['b4_work_precision_plan_status']}`; open blockers `{external_checks['b4_work_precision_plan_open_blockers']}`; source-policy rows `{external_checks['b4_work_precision_plan_source_policy_rows_closed']}/{external_checks['b4_work_precision_plan_source_policy_rows_total']}`.",
        f"- B4 work/precision lanes and execution guard: ready/not-ready `{external_checks['b4_work_precision_plan_ready_lanes']}/{external_checks['b4_work_precision_plan_not_ready_lanes']}`; heavy/run_v047/v048 `{external_checks['b4_work_precision_plan_heavy_run_invoked']}/{external_checks['b4_work_precision_plan_run_v047_invoked']}/{external_checks['b4_work_precision_plan_v048_runner_invoked']}`; user opt-in required `{external_checks['b4_work_precision_plan_next_heavy_requires_user_opt_in']}`.",
        f"- B4 RA2021/HI2022 launch preflights: `{external_checks['b4_work_precision_plan_ra2021_preflight_status']}` commands `{external_checks['b4_work_precision_plan_ra2021_launch_commands']}`; `{external_checks['b4_work_precision_plan_hi2022_preflight_status']}` commands/completed/missing `{external_checks['b4_work_precision_plan_hi2022_launch_commands']}/{external_checks['b4_work_precision_plan_hi2022_completed_shards']}/{external_checks['b4_work_precision_plan_hi2022_missing_shards']}`.",
        f"- B4 RA2021/HI2022 CLI contracts: `{external_checks['b4_work_precision_plan_ra2021_cli_status']}` runner/command checks `{external_checks['b4_work_precision_plan_ra2021_cli_runner_checks']}/{external_checks['b4_work_precision_plan_ra2021_cli_command_checks']}`; `{external_checks['b4_work_precision_plan_hi2022_cli_status']}` runner/command checks `{external_checks['b4_work_precision_plan_hi2022_cli_runner_checks']}/{external_checks['b4_work_precision_plan_hi2022_cli_command_checks']}`.",
        f"- B4 HI2022 launch boundary: avoids 1e-4 `{external_checks['b4_work_precision_plan_hi2022_commands_avoid_1e_4']}`; source-policy rows closed `{external_checks['b4_work_precision_plan_hi2022_source_policy_rows_closed']}`; closes B4/B7 `{external_checks['b4_work_precision_plan_hi2022_closes_b4']}/{external_checks['b4_work_precision_plan_hi2022_closes_b7']}`.",
        f"- B4 existing-artifact promotion audit: `{external_checks['b4_existing_promotion_audit_status']}`; candidates `{external_checks['b4_existing_promotion_candidate_items']}`; promotion-ready `{external_checks['b4_existing_promotion_ready_without_new_execution']}`; source-policy rows `{external_checks['b4_existing_promotion_source_policy_rows_closed']}/{external_checks['b4_existing_promotion_source_policy_rows_total']}`; closes B4/B7 `{external_checks['b4_existing_promotion_b4_closing_items']}/{external_checks['b4_existing_promotion_b7_closing_items']}`.",
        f"- B4 post-execution audit: `{external_checks['b4_post_execution_audit_status']}`; verified-authorized/existing-artifacts/output-present `{external_checks['b4_post_execution_verified_authorized_execution_recorded']}/{external_checks['b4_post_execution_existing_ready_command_artifacts_present']}/{external_checks['b4_post_execution_outputs_present']}`; scope `{external_checks['b4_post_execution_execution_record_scope']}`; promoted rows `{external_checks['b4_post_execution_source_policy_rows_closed']}/{external_checks['b4_post_execution_source_policy_rows_total']}`; B4/B7 close `{external_checks['b4_post_execution_b4_can_close_now']}/{external_checks['b4_post_execution_b7_can_close_now']}`; RA2021/HI2022 status `{external_checks['b4_post_execution_ra2021_double_candidate_status']}` / `{external_checks['b4_post_execution_hi2022_selected_candidate_status']}`.",
        f"- RA/HI source-policy post-execution attempt certificate: `{external_checks['ra_hi_source_policy_post_execution_attempt_certificate_status']}`; rows RA/HI/total `{external_checks['ra_hi_source_policy_post_execution_attempt_ra_rows']}/{external_checks['ra_hi_source_policy_post_execution_attempt_hi_rows']}/{external_checks['ra_hi_source_policy_post_execution_attempt_rows']}`; promoted/open `{external_checks['ra_hi_source_policy_post_execution_attempt_promoted_rows']}/{external_checks['ra_hi_source_policy_post_execution_attempt_open_rows']}`.",
        f"- RA/HI source-policy closeout checklist: `{external_checks['ra_hi_source_policy_closeout_checklist_status']}`; rows RA/HI/total `{external_checks['ra_hi_source_policy_closeout_ra_rows']}/{external_checks['ra_hi_source_policy_closeout_hi_rows']}/{external_checks['ra_hi_source_policy_closeout_total_rows']}`; commands/mapped `{external_checks['ra_hi_source_policy_closeout_ready_commands']}/{external_checks['ra_hi_source_policy_closeout_mapped_rows']}`; promoted/completed/external-ready `{external_checks['ra_hi_source_policy_closeout_promoted_rows']}/{external_checks['ra_hi_source_policy_closeout_completed_rows']}/{external_checks['ra_hi_source_policy_closeout_external_ready_rows']}`; opt-in/executed `{external_checks['ra_hi_source_policy_closeout_opt_in_required']}/{external_checks['ra_hi_source_policy_closeout_execution_invoked']}`; closes B4/B7 `{external_checks['ra_hi_source_policy_closeout_b4_can_close']}/{external_checks['ra_hi_source_policy_closeout_b7_can_close']}`.",
        f"- RA/HI source-policy output inventory: `{external_checks['ra_hi_source_policy_output_inventory_status']}`; commands/outputs/summaries `{external_checks['ra_hi_source_policy_output_inventory_command_count']}/{external_checks['ra_hi_source_policy_output_inventory_outputs_existing']}/{external_checks['ra_hi_source_policy_output_inventory_summaries_existing']}`; csv rows/HI ok/closed `{external_checks['ra_hi_source_policy_output_inventory_csv_data_rows']}/{external_checks['ra_hi_source_policy_output_inventory_hi_ok_rows']}/{external_checks['ra_hi_source_policy_output_inventory_closed_rows']}`.",
        f"- RA/HI source-policy promotion blocker matrix: `{external_checks['ra_hi_source_policy_promotion_blocker_matrix_status']}`; rows RA/HI/total `{external_checks['ra_hi_source_policy_promotion_blocker_matrix_ra_rows']}/{external_checks['ra_hi_source_policy_promotion_blocker_matrix_hi_rows']}/{external_checks['ra_hi_source_policy_promotion_blocker_matrix_rows']}`; public-root/no-public-code `{external_checks['ra_hi_source_policy_promotion_blocker_matrix_public_root_rows']}/{external_checks['ra_hi_source_policy_promotion_blocker_matrix_no_public_code_rows']}`; closed/not-promoted/attempted-not-reproducible `{external_checks['ra_hi_source_policy_promotion_blocker_matrix_closed_rows']}/{external_checks['ra_hi_source_policy_promotion_blocker_matrix_not_promoted_rows']}/{external_checks['ra_hi_source_policy_promotion_blocker_matrix_attempted_not_reproducible_rows']}`; terminal-current/future-auth-or-artifact/reproduction-complete `{external_checks['ra_hi_source_policy_promotion_blocker_matrix_current_evidence_terminal_rows']}/{external_checks['ra_hi_source_policy_promotion_blocker_matrix_future_authorization_or_artifact_rows']}/{external_checks['ra_hi_source_policy_promotion_blocker_matrix_reproduction_complete_rows']}`; command-mapped/output-present `{external_checks['ra_hi_source_policy_promotion_blocker_matrix_command_mapped_rows']}/{external_checks['ra_hi_source_policy_promotion_blocker_matrix_output_present_rows']}`.",
        f"- HI2022 rA_half double repair-attempt certificate: `{external_checks['hi2022_ra_half_double_repair_attempt_status']}`; target ok/failed `{external_checks['hi2022_ra_half_double_repair_target_ok_rows']}/{external_checks['hi2022_ra_half_double_repair_target_failed_rows']}`; combined rows/groups `{external_checks['hi2022_ra_half_double_repair_combined_ok_rows']}/{external_checks['hi2022_ra_half_double_repair_combined_row_count']}` and `{external_checks['hi2022_ra_half_double_repair_combined_complete_groups']}/{external_checks['hi2022_ra_half_double_repair_combined_group_count']}`; promoted/source-closed `{external_checks['hi2022_ra_half_double_repair_rows_promoted']}/{external_checks['hi2022_ra_half_double_repair_source_policy_closed']}`.",
        f"- B4 source-policy row closure-readiness ledger: `{external_checks['b4_row_readiness_ledger_status']}`; external rows `{external_checks['b4_row_readiness_external_rows']}/{external_checks['b4_row_readiness_expected_external_rows']}`; closed/open `{external_checks['b4_row_readiness_source_policy_rows_closed']}/{external_checks['b4_row_readiness_source_policy_rows_open']}`; command-mapped/no-command `{external_checks['b4_row_readiness_rows_with_launch_command_refs']}/{external_checks['b4_row_readiness_rows_without_launch_command_refs']}`; ready/not-ready suites `{external_checks['b4_row_readiness_ready_suites']}/{external_checks['b4_row_readiness_not_ready_suites']}`.",
        f"- B4 execution opt-in packet: `{external_checks['b4_execution_opt_in_packet_status']}`; opt-in required `{external_checks['b4_execution_opt_in_explicit_user_opt_in_required']}`; commands `{external_checks['b4_execution_opt_in_ready_command_count']}`; mapped/unaddressed rows `{external_checks['b4_execution_opt_in_mapped_external_rows']}/{external_checks['b4_execution_opt_in_unaddressed_external_rows']}`; source-policy rows `{external_checks['b4_execution_opt_in_source_policy_rows_closed_now']}/{external_checks['b4_execution_opt_in_source_policy_rows_total']}`.",
        f"- Source-policy execution handoff traceability: unique RA/HI rows `{external_checks['source_policy_execution_handoff_unique_mapped_row_count']}/{external_checks['source_policy_execution_handoff_ra_hi_unique_row_count']}`; row refs `{external_checks['source_policy_execution_handoff_traced_command_row_reference_total']}/{external_checks['source_policy_execution_handoff_declared_mapped_row_reference_total']}`; mismatches/terminal/closed/promotion-ready `{external_checks['source_policy_execution_handoff_declared_vs_traced_mismatch_count']}/{external_checks['source_policy_execution_handoff_terminal_rows_with_command_refs']}/{external_checks['source_policy_execution_handoff_traceability_closed_rows']}/{external_checks['source_policy_execution_handoff_traceability_promotion_ready_rows']}`.",
        f"- B4 post-execution promotion contract: `{external_checks['b4_post_execution_promotion_contract_schema']}` / `{external_checks['b4_post_execution_promotion_contract_status']}`; rows `{external_checks['b4_post_execution_promotion_contract_rows_closed']}/{external_checks['b4_post_execution_promotion_contract_rows_total']}`; ready/unaddressed `{external_checks['b4_post_execution_promotion_contract_ready_mapped_rows']}/{external_checks['b4_post_execution_promotion_contract_unaddressed_rows']}`; checks satisfied `{external_checks['b4_post_execution_promotion_contract_checks_satisfied_now']}`; closes B4/B7 `{external_checks['b4_post_execution_promotion_contract_b4_can_close_now']}/{external_checks['b4_post_execution_promotion_contract_b7_can_close_now']}`.",
        f"- External-superiority claim-demotion audit: `{external_checks['claim_demotion_audit_schema']}` / `{external_checks['claim_demotion_audit_status']}`; Route B ready `{external_checks['claim_demotion_audit_route_b_ready']}`; B2/B4 closed by route `{external_checks['claim_demotion_audit_b2_gate_closed_by_route_b']}/{external_checks['claim_demotion_audit_b4_gate_closed_by_route_b']}`.",
        f"- Claim-demotion retained evidence: formal order `{external_checks['claim_demotion_audit_formal_order_retained']}`, common-reference cells `{external_checks['claim_demotion_audit_common_reference_cells']}`, diagnostic favorable order/error cells `{external_checks['claim_demotion_audit_direct_order_wins']}/{external_checks['claim_demotion_audit_direct_error_wins']}`; external-superiority remains demoted.",
        f"- Claim-demotion demotion scope: current `{external_checks['claim_demotion_audit_current_demoted_suites']}`, additional `{external_checks['claim_demotion_audit_additional_demotions_needed']}`, full `{external_checks['claim_demotion_audit_full_demotion_scope_after_route_b']}`.",
        f"- Claim-demotion default 1e-4/heavy/run_v047: `{external_checks['claim_demotion_audit_default_1e_4_required']}/{external_checks['claim_demotion_audit_heavy_run_invoked']}/{external_checks['claim_demotion_audit_run_v047_invoked']}`.",
        f"- Claim-demotion Route B application contract: `{external_checks['claim_demotion_route_b_contract_schema']}`; ready-to-promote `{external_checks['claim_demotion_route_b_ready_to_promote']}`; safe flag flip `{external_checks['claim_demotion_route_b_safe_to_flip_flags']}`; satisfied steps `{external_checks['claim_demotion_route_b_satisfied_steps']}/{external_checks['claim_demotion_route_b_total_steps']}`; creates numerical wins `{external_checks['claim_demotion_route_b_creates_numerical_wins']}`; unsatisfied `{external_checks['claim_demotion_route_b_unsatisfied_steps']}`.",
        f"- RA2021 source-policy row audit: `{external_checks['ra2021_source_policy_audit_schema']}` / `{external_checks['ra2021_source_policy_audit_status']}`.",
        f"- RA2021 per-row source-identity resolved / promotion remaining requirements: `{external_checks['ra2021_per_row_source_identity_requirements_resolved']}/{external_checks['ra2021_per_row_source_policy_promotion_requirements_remaining']}`; row missing evidence shrunk `{external_checks['ra2021_row_missing_evidence_shrunk_by_identity_audit']}`.",
        f"- RA2021 promotion-gap drilldown: checked `{external_checks['ra2021_promotion_gap_drilldown_checked']}`; examples/active rows `{external_checks['ra2021_promotion_gap_examples_checked']}/{external_checks['ra2021_promotion_gap_active_rows_checked']}`; source identity/promotion closed `{external_checks['ra2021_promotion_gap_source_identity_closed']}/{external_checks['ra2021_promotion_gap_source_policy_promotion_closed']}`.",
        f"- RA2021 promotion-gap statuses: single `{external_checks['ra2021_promotion_gap_single_status']}`, double `{external_checks['ra2021_promotion_gap_double_status']}`, closed-loop `{external_checks['ra2021_promotion_gap_closed_loop_status']}`.",
        f"- RA2021 source-identity audit: `{external_checks['ra2021_source_identity_schema']}` / `{external_checks['ra2021_source_identity_status']}`; output mapping/time-grid `{external_checks['ra2021_source_identity_output_mapping_verified']}/{external_checks['ra2021_source_identity_time_grid_extracted']}`; source-policy rows `{external_checks['ra2021_source_identity_source_policy_rows_closed']}`; external superiority `{external_checks['ra2021_source_identity_external_superiority_allowed']}`.",
        f"- RA2021 active B2 rows and public order/timing groups: `{external_checks['ra2021_active_b2_flagged_rows']}`; `{external_checks['ra2021_public_order_groups_completed']}/{external_checks['ra2021_public_order_groups_required']}` and `{external_checks['ra2021_public_timing_rows_completed']}/{external_checks['ra2021_public_timing_rows_required']}`.",
        f"- RA2021 fixed-grid/paper-safe/source-policy rows: `{external_checks['ra2021_fixed_grid_common_reference_rows']}/12`, `{external_checks['ra2021_paper_safe_common_reference_rows']}/12`, `{external_checks['ra2021_source_policy_reproduction_rows']}/12`.",
        f"- RA2021 velocity mismatch/nonmonotone rows: `{external_checks['ra2021_position_aligned_velocity_mismatch_rows']}/{external_checks['ra2021_velocity_nonmonotone_or_floor_limited_rows']}`.",
        f"- RA2021 can close B2 now/default 1e-4/heavy/run_v047: `{external_checks['ra2021_can_close_b2_requirement_now']}/{external_checks['ra2021_default_1e_4_required']}/{external_checks['ra2021_heavy_run_invoked']}/{external_checks['ra2021_run_v047_invoked']}`.",
        f"- TFE source-policy spec: `{external_checks['tfe_source_policy_spec_schema']}` / `{external_checks['tfe_source_policy_spec_status']}`.",
        f"- TFE source-policy reference h and completed rows: `{external_checks['tfe_source_policy_reference_h']}` / `{external_checks['tfe_source_policy_rows_completed']}`.",
        f"- TFE source-policy runner/external superiority allowed: `{external_checks['tfe_source_policy_runner_implemented']}` / `{external_checks['tfe_source_policy_external_superiority_allowed']}`.",
        f"- TFE public-code recheck: `{external_checks['tfe_public_code_recheck_status']}` on `{external_checks['tfe_public_code_recheck_date']}`; repo/user/code-search `{external_checks['tfe_public_code_recheck_github_repository_search_total_count']}/{external_checks['tfe_public_code_recheck_github_user_search_total_count']}/{external_checks['tfe_public_code_recheck_github_code_search_api_status']}`; attempted-not-reproducible/closed `{external_checks['tfe_public_code_recheck_attempted_not_reproducible_rows']}/{external_checks['tfe_public_code_recheck_source_policy_rows_closed']}`; external superiority `{external_checks['tfe_public_code_recheck_external_superiority_allowed']}`.",
        f"- TFE candidate/source-policy boundary sources/match/use: `{','.join(external_checks['tfe_candidate_source_policy_boundary_sources'])}/{external_checks['tfe_candidate_source_policy_boundary_sources_match']}/{external_checks['tfe_candidate_source_policy_allowed_use']}`.",
        f"- TFE self-reproduction attempt certificate: `{external_checks['tfe_source_policy_self_reproduction_attempt_certificate_status']}`; attempted/not-reproducible/closed rows `{external_checks['tfe_source_policy_self_reproduction_attempt_rows']}/{external_checks['tfe_source_policy_self_reproduction_attempt_not_reproducible_rows']}/{external_checks['tfe_source_policy_self_reproduction_attempt_closed_rows']}`.",
        f"- TFE self-reproduction preflight route/reopen/source rows: `{external_checks['tfe_source_policy_self_reproduction_preflight_current_route']}/{external_checks['tfe_source_policy_self_reproduction_preflight_reopen_condition']}/{external_checks['tfe_source_policy_self_reproduction_preflight_source_policy_rows_completed']}`.",
        f"- TFE self-reproduction preflight blocks/ready/promote/next-actions: `{external_checks['tfe_source_policy_self_reproduction_preflight_execution_block_count']}/{external_checks['tfe_source_policy_self_reproduction_preflight_ready_now']}/{external_checks['tfe_source_policy_self_reproduction_preflight_can_promote_rows_now']}/{external_checks['tfe_source_policy_self_reproduction_required_next_action_count']}`.",
        f"- TFE candidate/source-policy boundary scaffold/DAE-equivalent/method-equivalent/source rows/external-superiority: `{external_checks['tfe_candidate_source_policy_scaffold_present']}/{external_checks['tfe_candidate_source_policy_dae_runner_equivalent']}/{external_checks['tfe_candidate_source_policy_method_runner_equivalent']}/{external_checks['tfe_candidate_source_policy_rows_completed']}/{external_checks['tfe_candidate_source_policy_external_superiority_allowed']}`; promotion required `{external_checks['tfe_candidate_source_policy_runner_required_for_promotion']}` with obligations `{external_checks['tfe_candidate_source_policy_obligation_count']}`.",
        f"- TFE DAE runner contract accounting raw/non-heavy-terminal/effective-execution/source-rows: `{external_checks['tfe_dae_runner_contract_gap_block_accounting']['raw_open_contract_block_count']}/{external_checks['tfe_dae_runner_contract_gap_terminal_nonpromoted_block_count']}/{external_checks['tfe_dae_runner_contract_gap_effective_missing_block_count']}/{external_checks['tfe_dae_runner_contract_gap_block_accounting']['source_policy_rows_closed_by_accounting']}`.",
        f"- TFE DAE runner effective execution blocks: `{external_checks['tfe_dae_runner_contract_gap_effective_missing_blocks']}`.",
        f"- TFE source-policy execution preflight status/opt-in/nonheavy/execution/promote/ready: `{external_checks['tfe_source_policy_execution_preflight_status']}/{external_checks['tfe_source_policy_execution_preflight_opt_in_required']}/{external_checks['tfe_source_policy_execution_preflight_nonheavy_dispositioned']}/{external_checks['tfe_source_policy_execution_preflight_execution_block_count']}/{external_checks['tfe_source_policy_execution_preflight_can_promote_rows_now']}/{external_checks['tfe_source_policy_execution_preflight_ready_now']}`.",
        f"- TFE runner contract preflight status/entrypoints/candidate-backed/source-rows/execution-blocks: `{external_checks['tfe_runner_contract_preflight_status']}/{external_checks['tfe_runner_contract_preflight_entrypoints']}/{external_checks['tfe_runner_contract_preflight_candidate_backed']}/{external_checks['tfe_runner_contract_preflight_source_policy_rows_completed']}/{external_checks['tfe_runner_contract_preflight_execution_blocks']}`.",
        f"- OC12 full-archive TFE runner preflight status/entrypoints/candidate-backed/source-rows/execution-blocks: `{external_checks['oc12_archive_tfe_runner_contract_preflight_status']}/{external_checks['oc12_archive_tfe_runner_contract_preflight_entrypoints']}/{external_checks['oc12_archive_tfe_runner_contract_preflight_candidate_backed']}/{external_checks['oc12_archive_tfe_runner_contract_preflight_source_policy_rows_completed']}/{external_checks['oc12_archive_tfe_runner_contract_preflight_execution_blocks']}`.",
        f"- OC12 full-archive action boundary safe/opt-in/allowed/invoked/exact/commands/rows: `{external_checks['oc12_archive_safe_without_b4_opt_in_count']}/{external_checks['oc12_archive_opt_in_required_action_count']}/{external_checks['oc12_archive_source_policy_execution_allowed_now']}/{external_checks['oc12_archive_source_policy_execution_invoked']}/{external_checks['oc12_archive_exact_b4_opt_in_required_for_execution']}/{external_checks['oc12_archive_opt_in_required_command_count']}/{external_checks['oc12_archive_opt_in_required_mapped_external_rows']}`.",
        f"- OC6 reopen latest external probe carried by full-archive gap: `{external_checks['oc6_reopen_latest_external_probe']}`.",
        f"- TFE source-policy row audit: `{external_checks['tfe_source_policy_audit_schema']}` / `{external_checks['tfe_source_policy_audit_status']}`.",
        f"- TFE active/source-policy-closed/claim-ready rows: `{external_checks['tfe_active_b2_flagged_rows']}/{external_checks['tfe_source_policy_closed_rows']}/{external_checks['tfe_external_superiority_ready_rows']}`.",
        f"- TFE spec extracted/pendulum runner implemented: `{external_checks['tfe_source_policy_spec_extracted']}/{external_checks['tfe_pendulum_runner_implemented']}`.",
        f"- TFE source grid policy resolved/compatible/incompatible rows: `{external_checks['tfe_source_grid_policy_resolved_for_full_T10']}/{external_checks['tfe_source_grid_integer_step_compatible_rows']}/{external_checks['tfe_source_grid_integer_step_incompatible_rows']}`.",
        f"- TFE exact-T endpoint-grid subset resolved/requires policy: `{external_checks['tfe_source_grid_policy_resolved_for_exact_T_compatible_rows']}/{external_checks['tfe_source_grid_exact_T_compatible_rows_endpoint_convention_resolved']}/{external_checks['tfe_source_grid_endpoint_incompatible_rows_requiring_policy']}`.",
        f"- TFE source grid endpoint convention candidates: `{external_checks['tfe_source_grid_endpoint_convention_candidate_count']}` policies `{external_checks['tfe_source_grid_endpoint_convention_policies']}`.",
        f"- TFE source-text endpoint audit: source text/anchors `{external_checks['tfe_source_grid_source_text_available']}/{external_checks['tfe_source_grid_source_text_anchor_count']}`, algorithm-literal fixed-h `{external_checks['tfe_source_grid_algorithm_literal_fixed_h']}`, error-sampling convention resolved `{external_checks['tfe_source_grid_endpoint_convention_resolved_for_error_sampling']}`.",
        f"- TFE endpoint sensitivity diagnostic: `{external_checks['tfe_endpoint_sensitivity_status']}`; methods/policies/raw rows `{external_checks['tfe_endpoint_sensitivity_method_count']}/{external_checks['tfe_endpoint_sensitivity_policy_count']}/{external_checks['tfe_endpoint_sensitivity_raw_row_count']}`; source-policy rows `{external_checks['tfe_endpoint_sensitivity_source_policy_rows_completed']}`; superiority allowed `{external_checks['tfe_endpoint_sensitivity_external_superiority_claim_allowed']}`.",
        f"- TFE full-T10 coarse candidate summary: `{external_checks['tfe_full_t10_coarse_summary_status']}`; rows/finite/residual-ok/source-policy `{external_checks['tfe_full_t10_coarse_summary_row_count']}/{external_checks['tfe_full_t10_coarse_summary_finite_rows']}/{external_checks['tfe_full_t10_coarse_summary_residual_ok_rows']}/{external_checks['tfe_full_t10_coarse_summary_source_policy_rows']}`; source reference invoked `{external_checks['tfe_full_t10_coarse_summary_source_policy_reference_invoked']}`.",
        f"- TFE source pendulum model audit: `{external_checks['tfe_source_pendulum_model_schema']}` / `{external_checks['tfe_source_pendulum_model_status']}`.",
        f"- TFE source pendulum parameters/smoke/setup closed: `{external_checks['tfe_source_pendulum_parameter_model_implemented']}/{external_checks['tfe_source_pendulum_frictionless_smoke_implemented']}/{external_checks['tfe_source_pendulum_setup_subrequirement_closed']}`.",
        f"- TFE source pendulum absolute-coordinate residual/source-policy-equivalent: `{external_checks['tfe_source_pendulum_absolute_coordinate_dae_residual_smoke_implemented']}/{external_checks['tfe_source_pendulum_absolute_coordinate_frictional_candidate_dae_smoke_implemented']}` / `{external_checks['tfe_source_pendulum_source_policy_dae_runner_equivalent']}`.",
        f"- TFE source pendulum source-output time smoke/source-policy-equivalent: `{external_checks['tfe_source_pendulum_source_output_time_integration_smoke_implemented']}` / `{external_checks['tfe_source_pendulum_source_policy_time_integration_runner_equivalent']}`.",
        f"- TFE source pendulum bounded reference-policy smoke/full T=10 source run: `{external_checks['tfe_source_pendulum_source_reference_solution_policy_smoke_implemented']}/{external_checks['tfe_source_pendulum_source_reference_solution_policy_smoke_full_T10']}`.",
        f"- TFE source pendulum full-T=10 source-reference feasibility probe: implemented/completed/source-policy rows `{external_checks['tfe_source_pendulum_source_reference_solution_policy_full_T10_probe_implemented']}/{external_checks['tfe_source_pendulum_source_reference_solution_policy_full_T10_probe_completed']}/{external_checks['tfe_source_pendulum_source_reference_solution_policy_full_T10_probe_rows_completed']}`; source/check steps `{external_checks['tfe_source_pendulum_source_reference_solution_policy_full_T10_probe_steps']}/{external_checks['tfe_source_pendulum_source_reference_solution_policy_full_T10_probe_check_steps']}`; coordinate/velocity check errors `{external_checks['tfe_source_pendulum_source_reference_solution_policy_full_T10_probe_coordinate_error']:.3e}/{external_checks['tfe_source_pendulum_source_reference_solution_policy_full_T10_probe_velocity_error']:.3e}`.",
        f"- TFE source pendulum comparator candidate runners/Newmark/trapezoidal/TFE-m-candidate/method-equivalent/TFE m=1-3 source-policy: `{external_checks['tfe_source_pendulum_source_comparator_candidate_runners_implemented']}/{external_checks['tfe_source_pendulum_newmark_beta_candidate_runner_smoke_implemented']}/{external_checks['tfe_source_pendulum_trapezoidal_candidate_runner_smoke_implemented']}/{external_checks['tfe_source_pendulum_tfe_m1_m2_m3_candidate_runner_smoke_implemented']}/{external_checks['tfe_source_pendulum_source_policy_method_runner_equivalent']}/{external_checks['tfe_source_pendulum_tfe_m1_m2_m3_source_policy_runners_implemented']}`.",
        f"- TFE source pendulum Gauss6 candidate smoke/absolute-coordinate source-policy runner: `{external_checks['tfe_source_pendulum_gauss6_candidate_smoke_implemented']}/{external_checks['tfe_source_pendulum_gauss6_absolute_coordinate_source_policy_runner_implemented']}`.",
        f"- TFE source pendulum Gauss6 candidate rows/source-policy rows/method-equivalent: `{external_checks['tfe_source_pendulum_gauss6_candidate_rows']}/{external_checks['tfe_source_pendulum_gauss6_candidate_source_policy_rows_completed']}/{external_checks['tfe_source_pendulum_gauss6_candidate_method_equivalent']}`.",
        f"- TFE source pendulum Appendix-B coefficient certificate: `{external_checks['tfe_source_pendulum_appendix_b_coefficient_certificate_checked']}`; rows/max diff `{external_checks['tfe_source_pendulum_appendix_b_coefficient_certificate_rows']}/{external_checks['tfe_source_pendulum_appendix_b_coefficient_certificate_max_abs_diff']:.3e}`.",
        f"- TFE source pendulum unified bounded runner rows/full T=10/source-policy rows: `{external_checks['tfe_source_pendulum_bounded_source_policy_runner_rows']}/{external_checks['tfe_source_pendulum_bounded_source_policy_runner_full_T10']}/{external_checks['tfe_source_pendulum_bounded_source_policy_runner_source_policy_rows_completed']}`.",
        f"- TFE source pendulum active-B2 candidate rows/full T=10/source-policy rows: `{external_checks['tfe_source_pendulum_active_b2_candidate_row_count']}/{external_checks['tfe_source_pendulum_active_b2_candidate_row_smoke_full_T10']}/{external_checks['tfe_source_pendulum_active_b2_source_policy_rows_completed']}`.",
        f"- TFE source pendulum active-B2 full-T10 coarse probe: implemented/fullT10/source-policy rows/finite/residual-ok/source-ref-invoked `{external_checks['tfe_source_pendulum_active_b2_full_T10_coarse_probe_implemented']}/{external_checks['tfe_source_pendulum_active_b2_full_T10_coarse_probe_full_T10']}/{external_checks['tfe_source_pendulum_active_b2_full_T10_coarse_probe_source_policy_rows']}/{external_checks['tfe_source_pendulum_active_b2_full_T10_coarse_probe_finite_rows']}/{external_checks['tfe_source_pendulum_active_b2_full_T10_coarse_probe_residual_ok_rows']}/{external_checks['tfe_source_pendulum_active_b2_full_T10_coarse_probe_reference_invoked']}`.",
        f"- TFE source pendulum active-B2 source-reference full-T10 probe: implemented/fullT10/reference-invoked/source-policy rows/finite/residual-ok/method-equivalent `{external_checks['tfe_source_pendulum_active_b2_source_reference_full_T10_probe_implemented']}/{external_checks['tfe_source_pendulum_active_b2_source_reference_full_T10_probe_full_T10']}/{external_checks['tfe_source_pendulum_active_b2_source_reference_full_T10_probe_reference_invoked']}/{external_checks['tfe_source_pendulum_active_b2_source_reference_full_T10_probe_source_policy_rows']}/{external_checks['tfe_source_pendulum_active_b2_source_reference_full_T10_probe_finite_rows']}/{external_checks['tfe_source_pendulum_active_b2_source_reference_full_T10_probe_residual_ok_rows']}/{external_checks['tfe_source_pendulum_active_b2_source_reference_full_T10_probe_method_equivalent']}`.",
        f"- TFE source pendulum m=3 full-T10 formula probe: implemented/fullT10/expected/source-policy rows/finite/residual-ok/source-ref-invoked `{external_checks['tfe_source_pendulum_tfe_m3_full_T10_formula_probe_implemented']}/{external_checks['tfe_source_pendulum_tfe_m3_full_T10_formula_probe_full_T10']}/{external_checks['tfe_source_pendulum_tfe_m3_full_T10_formula_probe_expected_order']}/{external_checks['tfe_source_pendulum_tfe_m3_full_T10_formula_probe_source_policy_rows']}/{external_checks['tfe_source_pendulum_tfe_m3_full_T10_formula_probe_finite_rows']}/{external_checks['tfe_source_pendulum_tfe_m3_full_T10_formula_probe_residual_ok_rows']}/{external_checks['tfe_source_pendulum_tfe_m3_full_T10_formula_probe_reference_invoked']}`.",
        f"- TFE source pendulum candidate friction/smoke provenance: `{external_checks['tfe_source_pendulum_brown_mcphee_candidate_friction_law_encoded']}/{external_checks['tfe_source_pendulum_frictional_candidate_smoke_implemented']}` / `{external_checks['tfe_source_pendulum_candidate_friction_law_provenance']}`.",
        f"- TFE source pendulum Brown--McPhee anchors/formula/source-equivalent: `{external_checks['tfe_source_pendulum_brown_mcphee_source_text_anchor_found']}/{external_checks['tfe_source_pendulum_brown_mcphee_source_text_names_velocity_model']}/{external_checks['tfe_source_pendulum_brown_mcphee_source_text_reports_mu_values']}` / `{external_checks['tfe_source_pendulum_brown_mcphee_published_formula_structure_encoded']}/{external_checks['tfe_source_pendulum_brown_mcphee_source_code_equivalent_law']}`.",
        f"- TFE source pendulum DAE/friction/output rows: `{external_checks['tfe_source_pendulum_model_dae_runner_implemented']}/{external_checks['tfe_source_pendulum_brown_mcphee_friction_law_implemented']}/{external_checks['tfe_source_pendulum_error_output_policy_encoded']}`; rows `{external_checks['tfe_source_pendulum_model_rows_completed']}`.",
        f"- TFE can close B2 now/default 1e-4/heavy/run_v047: `{external_checks['tfe_can_close_b2_requirement_now']}/{external_checks['tfe_default_1e_4_required']}/{external_checks['tfe_heavy_run_invoked']}/{external_checks['tfe_run_v047_invoked']}`.",
        f"- External superiority claim: `{external_checks['external_superiority_claim']}`.",
        "",
        "## Global Blocking Findings",
        "",
        "| ID | severity | area | required to close |",
        "|---|---:|---|---|",
    ]
    )
    for item in global_open_findings:
        lines.append(
            "| "
            f"`{item['id']}` | `{item['severity']}` | `{item['area']}` | "
            f"{finding_required_text(item)} |"
        )
    lines.extend(
        [
            "",
            "## Subsidiary Narrowed Blocker-Gate Findings",
            "",
            "| ID | severity | area | required to close |",
            "|---|---:|---|---|",
        ]
    )
    for item in cmame_blocker_gate_open_findings:
        lines.append(
            "| "
            f"`{item['id']}` | `{item['severity']}` | `{item['area']}` | "
            f"{finding_required_text(item)} |"
        )
    lines.extend(["", report["review_conclusion"]])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("cmame_submission_review_agent=written")
    print(f"submission_standard_met={report['submission_standard_met']}")
    print(f"top_level_decision_scope={report['top_level_review_decision_scope']}")
    print(f"decision={report['decision']}")
    print(f"narrowed_claim_subcheck_disposition={report['narrowed_claim_subcheck_disposition']}")
    print(f"narrowed_submission_standard_met={report['narrowed_submission_standard_met']}")
    print(f"narrowed_claim_decision={report['narrowed_claim_decision']}")
    print(f"open_blocker_count={report['open_blocker_count']}")


if __name__ == "__main__":
    main()
