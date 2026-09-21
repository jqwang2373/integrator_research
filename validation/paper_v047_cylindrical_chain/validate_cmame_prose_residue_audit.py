#!/usr/bin/env python3
"""Read-only validator for the CMAME B6 prose-residue audit."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
from paper_paths import LATEX, package_path as manuscript_path
AUDIT_MD = PAPER / "CMAME_PROSE_RESIDUE_AUDIT.md"
AUDIT_JSON = PAPER / "CMAME_PROSE_RESIDUE_AUDIT.json"
MAIN_TEX = LATEX / "main_cmame.tex"
FLAT_TEX = LATEX / "cmame_submission_flat" / "main_cmame_submission.tex"
MANIFEST = PAPER / "SUBMISSION_ARTIFACT_MANIFEST.json"
BLOCKER_GATE = PAPER / "CMAME_BLOCKER_CLOSURE_GATE.json"
B4_PLAN = PAPER / "B4_SOURCE_POLICY_WORK_PRECISION_EXECUTION_PLAN.json"
B4_OPT_IN = PAPER / "B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json"
B4_POST_EXECUTION = PAPER / "B4_SOURCE_POLICY_POST_EXECUTION_AUDIT.json"
NARROWED_POLICY = PAPER / "CMAME_NARROWED_CLAIM_CLOSURE_POLICY_AUDIT.json"
B4_B7_ROUTE = PAPER / "B4_B7_NON_SUPERIORITY_ROUTE_AUDIT.json"
FIGURE_SET_AUDIT_JSON = PAPER / "CMAME_FIGURE_SET_AUDIT.json"

FORBIDDEN_PATTERNS = {
    "artifact_macro": r"\artifact{",
    ".json": ".json",
    ".md": ".md",
    ".csv": ".csv",
    ".py": ".py",
    "submission_ready": "submission_ready",
    "same_test_campaign_status": "same_test_campaign_status",
    "external_superiority_claim": "external_superiority_claim",
    "default_1e-4": "default_1e-4",
    "run_v047": "run_v047",
    "PASS": "PASS",
    "FAIL": "FAIL",
}


class Checks:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def check(self, condition: bool, message: str) -> None:
        if not condition:
            self.errors.append(message)


def read_text(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8", errors="replace")


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def contains_normalized(text: str, token: str) -> bool:
    return token in text or " ".join(token.split()) in " ".join(text.split())


def main_body_and_appendix(tex: str) -> tuple[str, str]:
    frontmatter = r"\end{frontmatter}"
    appendix = r"\appendix"
    front_end = tex.find(frontmatter)
    app_start = tex.find(appendix)
    if front_end < 0:
        raise ValueError("missing \\end{frontmatter}")
    if app_start < 0:
        raise ValueError("missing \\appendix")
    if app_start <= front_end:
        raise ValueError("\\appendix appears before the end of frontmatter")
    body = tex[front_end + len(frontmatter) : app_start]
    appendix_text = tex[app_start:]
    return body, appendix_text


def theorem_boundary_paragraph(tex: str) -> str:
    start_token = r"Theorem~\ref{thm:g6fullva-order} is therefore"
    end_token = r"\begin{theorem}[Conditional sixth-order error theorem"
    start = tex.find(start_token)
    end = tex.find(end_token, start)
    if start < 0:
        raise ValueError("missing conditional-order theorem-boundary paragraph")
    if end < 0:
        raise ValueError("missing conditional-order theorem start after boundary paragraph")
    return tex[start:end]


def count_forbidden_tokens(body: str) -> dict[str, int]:
    return {name: body.count(pattern) for name, pattern in FORBIDDEN_PATTERNS.items()}


def require_tokens(checks: Checks, text: str, tokens: list[str], label: str) -> None:
    for token in tokens:
        checks.check(contains_normalized(text, token), f"{label} missing token: {token}")


def main() -> int:
    checks = Checks()
    try:
        audit_md = read_text(AUDIT_MD)
        audit = read_json(AUDIT_JSON)
        main_tex = read_text(MAIN_TEX)
        flat_tex = read_text(FLAT_TEX)
        manifest = read_json(MANIFEST)
        blocker_gate = read_json(BLOCKER_GATE)
        b4_plan = read_json(B4_PLAN)
        b4_opt_in = read_json(B4_OPT_IN)
        b4_post_execution = read_json(B4_POST_EXECUTION)
        narrowed_policy = read_json(NARROWED_POLICY)
        b4_b7_route = read_json(B4_B7_ROUTE)
        figure_set_audit = read_json(FIGURE_SET_AUDIT_JSON)
    except Exception as exc:  # noqa: BLE001 - concise CLI failure.
        print(f"cmame_prose_residue_audit=FAIL\n- {exc}")
        return 1

    main_body, main_appendix = main_body_and_appendix(main_tex)
    flat_body, flat_appendix = main_body_and_appendix(flat_tex)
    main_theorem_boundary = theorem_boundary_paragraph(main_tex)
    flat_theorem_boundary = theorem_boundary_paragraph(flat_tex)
    main_counts = count_forbidden_tokens(main_body)
    flat_counts = count_forbidden_tokens(flat_body)
    main_count_total = sum(main_counts.values())
    flat_count_total = sum(flat_counts.values())
    main_artifact_count = main_appendix.count(r"\artifact{")
    flat_artifact_count = flat_appendix.count(r"\artifact{")

    checks.check(audit.get("schema") == "cmame-prose-residue-audit-v1", "audit schema changed")
    checks.check(
        audit.get("status") == "main_body_machine_tokens_removed_reproducibility_appendix_compacted_b6_closed_under_narrowed_policy",
        "audit status changed",
    )
    checks.check(audit.get("submission_ready") is False, "audit must not claim submission ready")
    checks.check(audit.get("blocker") == "B6", "audit blocker changed")

    execution = audit.get("execution_policy", {})
    checks.check(execution.get("read_only_audit") is True, "audit is not marked read-only")
    checks.check(
        execution.get("default_step_policy") == "coarse_first_no_default_1e-4",
        "default step policy changed",
    )
    checks.check(execution.get("default_1e-4_required") is False, "audit incorrectly requires default 1e-4")
    checks.check(execution.get("heavy_numerical_run_invoked") is False, "audit says a heavy run was invoked")
    checks.check(execution.get("run_v047_invoked") is False, "audit says run_v047.py was invoked")

    checks.check(
        audit.get("scope", {}).get("checked_sources") == ["main_cmame.tex", "cmame_submission_flat/main_cmame_submission.tex"],
        "checked source list changed",
    )
    checks.check(audit.get("main_body_forbidden_token_counts") == main_counts, "main TeX token counts are stale")
    checks.check(audit.get("flat_main_body_forbidden_token_counts") == flat_counts, "flat TeX token counts are stale")
    checks.check(audit.get("main_body_machine_token_count") == main_count_total == 0, "main body token count is not zero")
    checks.check(audit.get("flat_main_body_machine_token_count") == flat_count_total == 0, "flat body token count is not zero")

    appendix = audit.get("appendix_evidence", {})
    checks.check(appendix.get("artifact_macro_count") == main_artifact_count == 0, "main appendix artifact count changed")
    checks.check(appendix.get("flat_artifact_macro_count") == flat_artifact_count == 0, "flat appendix artifact count changed")
    checks.check(
        appendix.get("reproducibility_appendix_compacted") is True,
        "audit lost reproducibility appendix compaction marker",
    )
    checks.check(r"\label{sec:repro-appendix}" in main_appendix, "main reproducibility appendix label missing")
    checks.check(r"\label{sec:repro-appendix}" in flat_appendix, "flat reproducibility appendix label missing")
    checks.check(r"\label{tab:artifact-contract}" in main_appendix, "main artifact-contract table missing")
    checks.check(r"\label{tab:validators}" in main_appendix, "main validator table missing")
    checks.check(r"\label{tab:artifact-contract}" in flat_appendix, "flat artifact-contract table missing")
    checks.check(r"\label{tab:validators}" in flat_appendix, "flat validator table missing")
    checks.check(r"\label{tab:algorithm-source-map}" in main_appendix, "main algorithm-source map table missing")
    checks.check(r"\label{tab:algorithm-source-map}" in flat_appendix, "flat algorithm-source map table missing")
    checks.check(
        appendix.get("algorithm_source_map_table_present") is True,
        "audit lost algorithm-source map marker",
    )
    for token in [
        "Algorithm-to-source map for the accepted",
        "v047_cylindrical_chain_pipeline/run_v047.py",
        "residual_cylindrical_chain",
        "R_VALUE",
        "R_JAC",
        "gauss_step",
        "integrate",
        "run_case",
        "v047_cylindrical_chain_pipeline/results",
        "v048_cross_paper_same_test_benchmarks/results",
        "validate_paper_package.py --latex",
        "validate_pipeline_outputs.py",
    ]:
        checks.check(token in main_appendix, f"main appendix missing algorithm-source token: {token}")
        checks.check(token in flat_appendix, f"flat appendix missing algorithm-source token: {token}")
    checks.check(r"\label{tab:all-example-review-artifacts}" in main_appendix, "main all-example review artifact table missing")
    checks.check(r"\label{tab:all-example-review-artifacts}" in flat_appendix, "flat all-example review artifact table missing")
    checks.check(
        appendix.get("all_example_review_traceability_table_present") is True,
        "audit lost all-example review traceability table marker",
    )
    checks.check(
        appendix.get("all_example_review_artifacts_present") is True,
        "audit lost all-example review artifact marker",
    )
    for token in [
        "Cross-example and review records retained with the source package",
        "All-example result matrix",
        "External-row table",
        "Case reconciliation record",
        "Proof and package-boundary record",
        "Source-format check",
        "Archive-completeness check",
        "Order-scope check",
        "Numerical-matrix check",
        "External-row check",
        "Proof-dependency check",
        "Scope-consistency review",
        "Package check",
        "Repository-provenance check",
        "The source package includes the command file for these read-only checks",
        "Supplementary source package",
    ]:
        checks.check(token in main_appendix, f"main appendix missing all-example/review artifact token: {token}")
        checks.check(token in flat_appendix, f"flat appendix missing all-example/review artifact token: {token}")

    claim = audit.get("claim_boundary", {})
    checks.check(claim.get("main_argument_body_machine_token_free") is True, "audit lost machine-token-free marker")
    checks.check(claim.get("artifact_filenames_confined_to_appendix") is True, "audit lost appendix confinement marker")
    checks.check(claim.get("reader_facing_claim_language_preserved") is True, "audit lost reader-facing language marker")
    checks.check(claim.get("b6_closed") is True, "audit did not close B6")
    checks.check(
        "narrowed B4/B7 claim boundary" in claim.get("closure_basis", ""),
        "B6 closure basis does not cite narrowed B4/B7 boundary",
    )

    proof_relocation = audit.get("proof_prose_relocation_pass", {})
    checks.check(
        proof_relocation.get("status") == "finite_solver_probe_details_relocated_from_proof_boundary_b6_closed_under_narrowed_policy",
        "proof prose relocation status changed",
    )
    checks.check(
        proof_relocation.get("checked_sources")
        == ["main_cmame.tex", "cmame_submission_flat/main_cmame_submission.tex"],
        "proof prose relocation source list changed",
    )
    checks.check(
        proof_relocation.get("edited_region") == "conditional order theorem boundary before thm:g6fullva-order",
        "proof prose relocation edited region changed",
    )
    removed_tokens = [
        "maximum final residual divided by $h^7$ equal to",
        "all 12 policy rows converge",
        "position/velocity order floor 6.946/6.608",
    ]
    checks.check(
        proof_relocation.get("removed_from_proof_boundary_tokens") == removed_tokens,
        "proof prose relocation removed-token list changed",
    )
    retained_tokens = [
        "Those probes are finite solver-policy diagnostics only",
        "they are not proof inputs",
        r"not a substitute for the explicit \(\eta_h^{\rm tube}\le c_\eta h^7\) theorem condition",
    ]
    checks.check(
        proof_relocation.get("retained_reader_facing_boundary_tokens") == retained_tokens,
        "proof prose relocation retained-token list changed",
    )
    for boundary_text, label in [
        (main_theorem_boundary, "main theorem-boundary paragraph"),
        (flat_theorem_boundary, "flat theorem-boundary paragraph"),
    ]:
        for token in removed_tokens:
            checks.check(token not in boundary_text, f"{label} still has detailed solver-probe token: {token}")
        for token in retained_tokens:
            checks.check(contains_normalized(boundary_text, token), f"{label} missing proof-boundary token: {token}")
    checks.check(
        proof_relocation.get("detailed_solver_evidence_retained_elsewhere") is True,
        "proof prose relocation lost retained-evidence marker",
    )
    checks.check(
        proof_relocation.get("strict_proof_boundary_preserved") is True,
        "proof prose relocation lost strict-boundary marker",
    )
    checks.check(proof_relocation.get("b6_closed_by_this_pass") is False, "proof prose relocation overcloses B6")
    checks.check(
        proof_relocation.get("final_prose_scope_closed_by_narrowed_policy") is True,
        "proof prose relocation lost narrowed-policy final prose closure marker",
    )

    dependency = audit.get("post_baseline_final_prose_dependency", {})
    b4_summary = b4_plan.get("execution_lane_summary", {})
    hi2022_demotion = b4_plan.get("hi2022_b4_b7_figure_scope_demotion_evidence", {})
    opt_in_contract = b4_opt_in.get("post_execution_promotion_contract", {})
    checks.check(
        dependency.get("dependency_audit") == "B4_SOURCE_POLICY_WORK_PRECISION_EXECUTION_PLAN.json",
        "B6 dependency audit path changed",
    )
    checks.check(
        dependency.get("b4_plan_status") == b4_plan.get("status") == "execution_plan_ready_b4_b7_remain_open",
        "B6 dependency B4 plan status stale",
    )
    checks.check(
        dependency.get("b4_can_close_now") == b4_plan.get("b4_can_close_now") is False,
        "B6 dependency overcloses B4",
    )
    checks.check(
        dependency.get("b7_can_close_now") == b4_plan.get("b7_can_close_now") is False,
        "B6 dependency overcloses B7",
    )
    checks.check(
        dependency.get("source_policy_rows_closed_after_plan")
        == b4_summary.get("source_policy_rows_closed_after_plan")
        == 0,
        "B6 dependency source-policy closed rows changed",
    )
    checks.check(
        dependency.get("source_policy_rows_total")
        == b4_summary.get("source_policy_rows_total")
        == 40,
        "B6 dependency source-policy total rows changed",
    )
    ready_boundary = dependency.get("ready_command_dependency_boundary", {})
    checks.check(
        ready_boundary.get("schema") == "cmame-b6-b4-ready-command-dependency-boundary-v1",
        "B6 ready-command dependency schema changed",
    )
    checks.check(
        ready_boundary.get("status")
        == "ready_commands_cover_half_source_policy_rows_future_source_policy_only_final_prose_not_deferred",
        "B6 ready-command dependency status changed",
    )
    checks.check(
        ready_boundary.get("opt_in_packet") == "B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json",
        "B6 ready-command dependency opt-in packet path changed",
    )
    checks.check(
        ready_boundary.get("ready_command_count")
        == b4_opt_in.get("ready_command_count")
        == 13,
        "B6 ready-command dependency command count stale",
    )
    checks.check(
        ready_boundary.get("ready_command_mapped_external_rows")
        == b4_opt_in.get("ready_command_mapped_external_rows")
        == 20,
        "B6 ready-command mapped rows stale",
    )
    checks.check(
        ready_boundary.get("unaddressed_external_rows_after_ready_commands")
        == b4_opt_in.get("unaddressed_external_rows_after_ready_commands")
        == 0,
        "B6 ready-command unaddressed rows stale",
    )
    checks.check(
        ready_boundary.get("source_policy_rows_closed_now")
        == b4_opt_in.get("source_policy_rows_closed_now")
        == 0,
        "B6 ready-command closed rows stale",
    )
    checks.check(
        ready_boundary.get("source_policy_rows_total")
        == b4_opt_in.get("source_policy_rows_total")
        == 40,
        "B6 ready-command total rows stale",
    )
    checks.check(
        ready_boundary.get("ready_lanes_after_explicit_opt_in")
        == opt_in_contract.get("ready_lanes_after_explicit_opt_in")
        == ["ra2021_source_policy_work_precision", "hi2022_full_T8_work_precision"],
        "B6 ready-command ready lanes stale",
    )
    checks.check(
        ready_boundary.get("not_ready_lanes_after_ready_commands")
        == opt_in_contract.get("not_ready_lanes")
        == ["tfe_source_policy_work_precision", "vp2024_source_code_path_work_precision"],
        "B6 ready-command not-ready lanes stale",
    )
    checks.check(
        ready_boundary.get("remaining_gap_rows_requiring_new_runner_or_code_path")
        == opt_in_contract.get("remaining_gap_rows_requiring_new_runner_or_code_path")
        == 0,
        "B6 ready-command runner/code-path gap rows stale",
    )
    checks.check(
        ready_boundary.get("remaining_gap_rows_demoted_related_work_proxy_for_current_claim")
        == opt_in_contract.get("remaining_gap_rows_demoted_related_work_proxy_for_current_claim")
        == 0,
        "B6 ready-command demoted proxy rows stale",
    )
    checks.check(
        ready_boundary.get("ready_commands_alone_can_close_b4")
        == b4_opt_in.get("b4_can_close_after_ready_commands_only")
        is False,
        "B6 ready-command boundary overcloses B4",
    )
    checks.check(
        ready_boundary.get("ready_commands_alone_can_close_b7")
        == b4_opt_in.get("b7_can_close_after_ready_commands_only")
        is False,
        "B6 ready-command boundary overcloses B7",
    )
    checks.check(
        ready_boundary.get("ready_commands_alone_can_enable_b6_final_prose_pass") is False,
        "B6 ready-command boundary incorrectly enables final prose pass",
    )
    checks.check(
        ready_boundary.get("execution_invoked_by_packet")
        == b4_opt_in.get("execution_invoked_by_packet")
        is False,
        "B6 ready-command boundary says opt-in packet was executed",
    )
    checks.check(
        ready_boundary.get("final_prose_scope_still_depends_on_unaddressed_rows") is False,
        "B6 ready-command boundary still depends on unaddressed rows",
    )
    checks.check(
        ready_boundary.get("final_prose_pass_enabled_by_narrowed_policy") is True,
        "B6 ready-command boundary did not enable final prose by narrowed policy",
    )
    post_boundary = dependency.get("post_execution_dependency_boundary", {})
    authorized = b4_post_execution.get("verified_authorized_execution_recorded") is True
    expected_post_status = (
        "verified_authorized_execution_zero_promoted_rows_source_policy_excluded_final_prose_enabled"
        if authorized
        else "existing_artifacts_present_no_verified_authorized_execution_zero_promoted_rows_source_policy_excluded_final_prose_enabled"
    )
    expected_post_scope = (
        "verified_authorized_guarded_driver_execution"
        if authorized
        else "no_verified_current_authorized_execution_record_existing_artifacts_only"
    )
    checks.check(
        post_boundary.get("schema") == "cmame-b6-b4-post-execution-dependency-boundary-v1",
        "B6 post-execution dependency schema changed",
    )
    checks.check(
        post_boundary.get("status") == expected_post_status,
        "B6 post-execution dependency status changed",
    )
    checks.check(
        post_boundary.get("post_execution_audit") == "B4_SOURCE_POLICY_POST_EXECUTION_AUDIT.json",
        "B6 post-execution dependency audit path changed",
    )
    checks.check(
        post_boundary.get("approved_driver_execution_recorded")
        == b4_post_execution.get("approved_driver_execution_recorded")
        is authorized,
        "B6 post-execution dependency approved driver marker inconsistent",
    )
    checks.check(
        post_boundary.get("verified_authorized_execution_recorded")
        == b4_post_execution.get("verified_authorized_execution_recorded")
        is authorized,
        "B6 post-execution dependency verified authorized marker inconsistent",
    )
    checks.check(
        post_boundary.get("existing_ready_command_artifacts_present")
        == b4_post_execution.get("existing_ready_command_artifacts_present")
        is True,
        "B6 post-execution dependency did not record existing artifact presence",
    )
    checks.check(
        post_boundary.get("execution_record_scope")
        == b4_post_execution.get("execution_record_scope")
        == expected_post_scope,
        "B6 post-execution dependency scope changed",
    )
    checks.check(
        post_boundary.get("all_expected_outputs_exist_now")
        == b4_post_execution.get("command_artifact_presence", {}).get("all_expected_outputs_exist_now")
        is True,
        "B6 post-execution dependency did not record output presence",
    )
    checks.check(
        post_boundary.get("source_policy_rows_promoted_after_driver")
        == b4_post_execution.get("source_policy_rows_closed")
        == 0,
        "B6 post-execution dependency promoted rows changed",
    )
    checks.check(
        post_boundary.get("source_policy_rows_total")
        == b4_post_execution.get("source_policy_total_rows")
        == 40,
        "B6 post-execution dependency total rows changed",
    )
    checks.check(
        post_boundary.get("b4_can_close_now")
        == b4_post_execution.get("b4_can_close_now")
        is False,
        "B6 post-execution dependency overcloses B4",
    )
    checks.check(
        post_boundary.get("b7_can_close_now")
        == b4_post_execution.get("b7_can_close_now")
        is False,
        "B6 post-execution dependency overcloses B7",
    )
    checks.check(
        post_boundary.get("same_guarded_driver_rerun_recommended") is False,
        "B6 post-execution dependency should not recommend rerunning the same driver",
    )
    checks.check(
        post_boundary.get("final_prose_scope_still_depends_on_zero_promoted_rows") is False,
        "B6 post-execution dependency still depends on zero promoted rows",
    )
    checks.check(
        post_boundary.get("final_prose_pass_enabled_by_post_execution") is False,
        "B6 post-execution dependency should not credit post-execution rows alone",
    )
    checks.check(
        post_boundary.get("final_prose_pass_enabled_by_narrowed_policy") is True,
        "B6 post-execution dependency did not enable final prose by narrowed policy",
    )
    narrowed_boundary = dependency.get("narrowed_claim_policy_boundary", {})
    checks.check(
        narrowed_boundary.get("policy_audit") == "CMAME_NARROWED_CLAIM_CLOSURE_POLICY_AUDIT.json",
        "B6 narrowed policy audit path changed",
    )
    checks.check(
        narrowed_boundary.get("route_audit") == "B4_B7_NON_SUPERIORITY_ROUTE_AUDIT.json",
        "B6 narrowed route audit path changed",
    )
    checks.check(
        narrowed_boundary.get("figure_set_audit") == "CMAME_FIGURE_SET_AUDIT.json",
        "B6 narrowed figure audit path changed",
    )
    checks.check(
        narrowed_boundary.get("narrowed_claim_evidence_supported")
        == narrowed_policy.get("narrowed_claim_evidence_supported")
        is True,
        "B6 narrowed evidence support missing",
    )
    checks.check(
        narrowed_boundary.get("b4_b7_closed_by_narrowed_claim_policy")
        == b4_b7_route.get("b4_b7_closed_by_narrowed_claim_policy")
        is True,
        "B6 narrowed route did not close B4/B7",
    )
    checks.check(
        narrowed_boundary.get("b7_closed_by_figure_set_audit") == figure_set_audit.get("b7_closed") is True,
        "B6 narrowed boundary did not carry B7 figure closure",
    )
    checks.check(
        narrowed_boundary.get("source_policy_row_promotion_required") is False,
        "B6 narrowed boundary unexpectedly requires source-policy promotion",
    )
    checks.check(
        narrowed_boundary.get("source_policy_work_precision_claim_excluded") is True,
        "B6 narrowed boundary did not exclude source-policy work/precision",
    )
    checks.check(
        narrowed_boundary.get("external_superiority_claim_allowed") is False,
        "B6 narrowed boundary overclaims external superiority",
    )
    checks.check(
        dependency.get("hi2022_b4_b7_figure_scope_demotion_status")
        == hi2022_demotion.get("status")
        == "demote_hi2022_from_b4_b7_source_policy_figures",
        "B6 dependency HI2022 demotion status stale",
    )
    checks.check(
        dependency.get("hi2022_source_policy_rows_closed_by_hi2022")
        == hi2022_demotion.get("source_policy_rows_closed_by_hi2022")
        == 0,
        "B6 dependency HI2022 source-policy rows changed",
    )
    checks.check(
        dependency.get("hi2022_counts_as_clean_work_precision_figure")
        == hi2022_demotion.get("counts_as_clean_work_precision_figure")
        is False,
        "B6 dependency overclaims HI2022 clean work/precision figure",
    )
    checks.check(dependency.get("final_prose_pass_ready") is True, "B6 dependency did not mark final prose ready")
    checks.check(
        dependency.get("remaining_dependency") == [],
        "B6 dependency remaining items changed",
    )
    checks.check(dependency.get("b6_closure_allowed_now") is True, "B6 dependency did not allow closure")

    preflight = audit.get("b6_closure_readiness_preflight", {})
    checks.check(
        preflight.get("schema") == "cmame-b6-closure-readiness-preflight-v1",
        "B6 closure-readiness preflight schema changed",
    )
    checks.check(
        preflight.get("status") == "b6_final_prose_pass_closed_under_narrowed_b4_b7_scope",
        "B6 closure-readiness preflight status changed",
    )
    checks.check(preflight.get("closed_precondition_count") == 11, "B6 closed precondition count changed")
    checks.check(preflight.get("open_dependency_count") == 0, "B6 open dependency count changed")
    checks.check(preflight.get("b6_closure_allowed_now") is True, "B6 preflight did not allow closure")
    checks.check(preflight.get("heavy_numerical_run_invoked") is False, "B6 preflight invoked heavy run")
    checks.check(preflight.get("run_v047_invoked") is False, "B6 preflight invoked run_v047")
    checks.check(preflight.get("default_1e-4_required") is False, "B6 preflight requires default 1e-4")
    expected_preconditions = {
        "main_body_machine_tokens_removed",
        "flat_main_body_machine_tokens_removed",
        "reproducibility_appendix_compacted",
        "artifact_filenames_confined_to_reproducibility_material",
        "algorithm_source_map_table_present",
        "all_example_review_traceability_table_present",
        "read_only_no_default_1e4_no_run_v047_policy_recorded",
        "reader_facing_claim_language_preserved",
        "b4_closed_under_narrowed_claim_policy",
        "b7_closed_under_narrowed_diagnostic_figure_scope",
        "source_policy_work_precision_claim_excluded",
    }
    precondition_rows = preflight.get("closed_preconditions", [])
    checks.check(
        {item.get("id") for item in precondition_rows} == expected_preconditions,
        "B6 closure-readiness precondition ids changed",
    )
    checks.check(
        all(item.get("status") is True for item in precondition_rows),
        "B6 closure-readiness precondition unexpectedly open",
    )
    dependency_rows = preflight.get("open_dependencies", [])
    checks.check(dependency_rows == [], "B6 should have no current-scope open dependencies")
    excluded_rows = preflight.get("excluded_future_source_policy_dependencies", [])
    checks.check(
        {item.get("id") for item in excluded_rows}
        == {
            "b4_source_policy_work_precision_closure",
            "b7_source_policy_work_precision_figure_rebuild",
        },
        "B6 excluded future source-policy dependency ids changed",
    )
    checks.check(
        all(item.get("status") == "excluded_from_current_claim" for item in excluded_rows),
        "B6 excluded future source-policy dependency status changed",
    )
    for action in [
        "recount main-body and flat-source machine tokens after the final prose pass",
        "refresh submission packet, review agent, PDF-style audit, and reproducibility manifest after any claim-scope edit",
    ]:
        checks.check(action in preflight.get("post_close_actions", []), f"B6 preflight missing action: {action}")

    forbidden_claims = audit.get("forbidden_claims", [])
    for token in [
        "submission_ready_true",
        "default_1e-4_required_true",
        "run_v047_invoked_true",
        "main_body_machine_tokens_allowed_true",
        "source_policy_rows_promoted_true",
        "external_superiority_claim_allowed_true",
    ]:
        checks.check(token in forbidden_claims, f"forbidden claim missing: {token}")

    blockers = blocker_gate.get("blockers", [])
    b6 = next((item for item in blockers if isinstance(item, dict) and item.get("id") == "B6"), {})
    checks.check(b6.get("status") in {"open", "closed"}, "B6 gate status is not readable")
    checks.check("prose_residue_audit_added" in b6.get("partial_progress", []), "B6 lost prose residue audit progress")
    checks.check("CMAME_PROSE_RESIDUE_AUDIT.md" in b6.get("partial_progress_evidence", []), "B6 audit MD evidence missing")
    checks.check("CMAME_PROSE_RESIDUE_AUDIT.json" in b6.get("partial_progress_evidence", []), "B6 audit JSON evidence missing")
    checks.check("validate_cmame_prose_residue_audit.py" in b6.get("partial_progress_evidence", []), "B6 audit validator evidence missing")
    checks.check(b6.get("main_body_machine_token_count") == 0, "B6 main body token count changed")
    checks.check(b6.get("artifact_macro_confined_to_appendix") is True, "B6 appendix confinement marker changed")
    checks.check(b6.get("default_1e-4_required") is False, "B6 incorrectly requires default 1e-4")

    checks.check(manifest.get("cmame_prose_residue_audit") == "CMAME_PROSE_RESIDUE_AUDIT.md", "manifest prose audit path missing")
    checks.check(manifest.get("cmame_prose_residue_audit_json") == "CMAME_PROSE_RESIDUE_AUDIT.json", "manifest prose audit JSON path missing")
    checks.check("CMAME_PROSE_RESIDUE_AUDIT.md" in manifest.get("evidence_anchors", []), "manifest prose audit anchor missing")
    checks.check("CMAME_PROSE_RESIDUE_AUDIT.json" in manifest.get("evidence_anchors", []), "manifest prose audit JSON anchor missing")
    checks.check("validate_cmame_prose_residue_audit.py" in manifest.get("validators", []), "manifest prose audit validator missing")
    checks.check(manifest.get("submission_ready") in {False, True}, "manifest submission-ready marker missing")
    checks.check(manifest.get("full_generator_invoked_by_submission_checks") is False, "manifest says full generator was invoked")

    require_tokens(
        checks,
        audit_md,
        [
            "Status: **B6 CLOSED - MAIN-BODY MACHINE TOKENS REMOVED AND NARROWED CLAIM PROSE FINALIZED**",
            "does not invoke `run_v047.py`",
            "default `1e-4` campaign",
            "main-body machine-token count: `0`",
            "appendix artifact macro count: `0`",
            "source-package summary",
            "Proof Prose Relocation Pass",
            "finite_solver_probe_details_relocated_from_proof_boundary_b6_closed_under_narrowed_policy",
            "they are not proof inputs",
            "`\\eta_h^{\\rm tube}\\le c_\\eta h^7` theorem condition",
            "Post-Baseline Dependency",
            "Source-policy rows remain `0/40`",
            "13 ready commands map `20/40` external source-policy rows",
            "`0/40` rows\nremain in the open unaddressed execution queue",
            "attempted-not-reproducible nonpublic-code rows",
            "TFE source-policy work/precision",
            "VP2024 source-code-path work/precision",
            "current narrowed claim does not require that future source-policy lane",
            "existing ready-command\nartifacts with no verified authorized guarded-driver execution",
            "post-execution audit promotes `0/40` source-policy rows",
            "B4/B7 source-policy closure at `False/False`",
            "Re-running the same guarded driver is not the recommended prose path",
            "b4_b7_closed_by_narrowed_claim_policy=True",
            "demote_hi2022_from_b4_b7_source_policy_figures",
            "post-baseline final prose pass is ready",
            "B6 closure is allowed now",
            "## B6 Closure-Readiness Preflight",
            "Status: `b6_final_prose_pass_closed_under_narrowed_b4_b7_scope`.",
            "Closed preconditions/open dependencies: `11/0`",
            "B6 closure allowed now: `True`",
            "heavy numerical run invoked: `False`",
            "`run_v047.py` invoked: `False`",
            "main_body_machine_tokens_removed",
            "b4_closed_under_narrowed_claim_policy",
            "b7_closed_under_narrowed_diagnostic_figure_scope",
            "source_policy_work_precision_claim_excluded",
            "refresh submission packet, review agent, PDF-style audit, and reproducibility manifest after any claim-scope edit",
            "algorithm-to-source map table present",
            "all-example sanity and review-traceability record table present",
            "`default_1e-4_required=false`",
            "`run_v047_invoked=false`",
            "`submission_ready=false`",
            "`b6_closed=True`",
            "validate_cmame_prose_residue_audit.py",
        ],
        "CMAME_PROSE_RESIDUE_AUDIT.md",
    )

    if checks.errors:
        print("cmame_prose_residue_audit=FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("cmame_prose_residue_audit=PASS")
    print(f"main_body_machine_token_count={main_count_total}")
    print(f"flat_main_body_machine_token_count={flat_count_total}")
    print("artifact_macro_confined_to_appendix=True")
    print(f"appendix_artifact_macro_count={main_artifact_count}")
    print("default_1e-4=False")
    print("run_v047_invoked=False")
    print("submission_ready=False")
    print("b6_closed=True")
    return 0


if __name__ == "__main__":
    sys.exit(main())
