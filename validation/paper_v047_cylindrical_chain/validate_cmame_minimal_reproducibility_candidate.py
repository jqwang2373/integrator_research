#!/usr/bin/env python3
"""Validate the CMAME minimal reproducibility candidate package."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
CANDIDATE = PAPER / "cmame_minimal_reproducibility_candidate"
MANIFEST_JSON = PAPER / "CMAME_MINIMAL_REPRODUCIBILITY_CANDIDATE_MANIFEST.json"
MANIFEST_MD = PAPER / "CMAME_MINIMAL_REPRODUCIBILITY_CANDIDATE_MANIFEST.md"

EXPECTED_OBJECTIVE_BLOCKER_OPEN_BY_ID = {"OC4": True, "OC6": True, "OC12": True}
EXPECTED_BLOCKER_CLOSURE_DECISION_BY_ID = {
    "OC4": "remain_open_ready_for_authorized_execution_not_executed_not_promoted",
    "OC6": "remain_open_no_positive_source_equivalent_artifact",
    "OC12": "remain_partial_narrowed_replay_ready_full_source_policy_archive_not_ready",
}
EXPECTED_BLOCKER_CLOSURE_ALLOWED_BY_ID = {"OC4": False, "OC6": False, "OC12": False}
EXPECTED_OPEN_BLOCKERS = ["OC4", "OC6", "OC12"]


class Checks:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def check(self, condition: bool, message: str) -> None:
        if not condition:
            self.errors.append(message)


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    checks = Checks()
    try:
        manifest = read_json(MANIFEST_JSON)
        candidate_manifest = read_json(CANDIDATE / "MANIFEST.json")
        manifest_md = read_text(MANIFEST_MD)
        readme = read_text(CANDIDATE / "README.md")
        matrix = read_json(CANDIDATE / "data" / "PAPER_NUMERICAL_RESULT_MATRIX.json")
        review = read_json(CANDIDATE / "data" / "CMAME_REVIEW_AGENT_REPORT.json")
        main_review = read_json(PAPER / "CMAME_REVIEW_AGENT_REPORT.json")
        package_manifest = read_json(PAPER / "CMAME_REPRODUCIBILITY_PACKAGE_MANIFEST.json")
        proof = read_json(CANDIDATE / "data" / "PROOF_CLOSURE_MANIFEST.json")
        newton = read_json(CANDIDATE / "data" / "NEWTON_EULER_SYMBOLIC_TARGET_AUDIT.json")
    except Exception as exc:  # noqa: BLE001
        print(f"cmame minimal reproducibility candidate validation: FAIL\n- {exc}")
        return 1

    checks.check(manifest == candidate_manifest, "top-level and package manifests differ")
    checks.check(manifest.get("schema") == "cmame-minimal-reproducibility-candidate-v1", "schema changed")
    checks.check(
        manifest.get("status") == "candidate_replay_package_built_not_submission_ready",
        "status changed",
    )
    checks.check(manifest.get("submission_ready") is False, "candidate must not mark submission ready")
    checks.check(manifest.get("read_only_replay_package") is True, "candidate replay marker missing")
    checks.check(manifest.get("paper_result_scope") == "bounded_common_reference_only", "result scope changed")
    checks.check(
        manifest.get("source_policy_external_superiority_allowed") is False,
        "candidate overclaims source-policy superiority",
    )
    checks.check(manifest.get("source_policy_closed_rows") == 0, "source-policy closed rows changed")
    checks.check(manifest.get("source_policy_total_rows") == 40, "source-policy total rows changed")
    checks.check(manifest.get("proof_gap_closed") is True, "candidate lost legacy direct proof closure")
    checks.check(
        manifest.get("direct_pc2_proof_gap_closed") is True,
        "candidate lost preferred direct-PC2 proof closure",
    )
    checks.check(
        manifest.get("proof_gap_closed_scope")
        == "direct_residual_bridge_kantorovich_route_closed_primitive_taylor_conditional_schema_open",
        "candidate proof closure scope missing",
    )
    checks.check(
        "active direct PC2 residual-bridge/Kantorovich proof closure"
        in manifest.get("proof_gap_closed_reading_rule", "")
        and "does not close the primitive 162-subterm Taylor lane"
        in manifest.get("proof_gap_closed_reading_rule", ""),
        "candidate proof closure reading rule missing",
    )
    schema_compat = manifest.get("schema_compatibility", {})
    checks.check(
        schema_compat.get("legacy_key") == "proof_gap_closed"
        and schema_compat.get("legacy_key_retained_for_schema_compatibility") is True
        and schema_compat.get("preferred_key") == "direct_pc2_proof_gap_closed",
        "candidate proof-gap schema compatibility missing",
    )
    checks.check(
        manifest.get("stage_residual_O_h7_implementation_defect_proved") is True,
        "candidate lost stage-residual O(h^7) direct proof",
    )
    blocker_matrix = manifest.get("objective_blocker_matrix", {})
    checks.check(
        blocker_matrix.get("blocker_open_by_id") == EXPECTED_OBJECTIVE_BLOCKER_OPEN_BY_ID,
        "candidate manifest objective blocker open map changed",
    )
    checks.check(
        blocker_matrix.get("objective_blocker_open_by_id") == EXPECTED_OBJECTIVE_BLOCKER_OPEN_BY_ID,
        "candidate manifest nested objective blocker open map changed",
    )
    checks.check(
        blocker_matrix.get("blocker_closure_decision_by_id") == EXPECTED_BLOCKER_CLOSURE_DECISION_BY_ID,
        "candidate manifest blocker closure decisions changed",
    )
    checks.check(
        blocker_matrix.get("blocker_closure_allowed_by_id") == EXPECTED_BLOCKER_CLOSURE_ALLOWED_BY_ID,
        "candidate manifest blocker closure permissions changed",
    )
    checks.check(
        blocker_matrix.get("open_blockers") == EXPECTED_OPEN_BLOCKERS,
        "candidate manifest open blocker list changed",
    )
    checks.check(
        blocker_matrix.get("decision") == "do_not_submit_global"
        and blocker_matrix.get("submission_standard_met") is False,
        "candidate manifest global submission boundary changed",
    )
    checks.check(manifest.get("minimal_submission_code_ready") is False, "candidate overclaims minimal submission code")
    checks.check(manifest.get("candidate_file_count") == 10, "candidate file count changed")
    checks.check(manifest.get("candidate_python_file_count") == 1, "candidate Python file count changed")
    checks.check(
        1 <= int(manifest.get("candidate_python_line_count", 0)) <= 220,
        "candidate replay script size changed unexpectedly",
    )
    reviewer_code_policy = manifest.get("reviewer_facing_code_policy", {})
    checks.check(
        reviewer_code_policy.get("candidate_code_size_ok") is True,
        "candidate should remain size-ok as a compact replay package",
    )
    checks.check(
        reviewer_code_policy.get("candidate_runner_centered") is False,
        "candidate must not overclaim runner-centered submission package status",
    )
    checks.check(
        reviewer_code_policy.get("candidate_replay_only") is True,
        "candidate replay-only policy missing",
    )
    checks.check(
        reviewer_code_policy.get("primary_submission_package_required") is True,
        "candidate must state that a primary runner package is still required",
    )
    checks.check(
        reviewer_code_policy.get("minimal_submission_code_ready") is False,
        "candidate must not mark minimal submission code ready",
    )
    source_repository_context = manifest.get("source_repository_context", {})
    package_summary = package_manifest.get("summary", {})
    main_code_checks = main_review.get("code_hygiene_checks", {})
    checks.check(
        source_repository_context.get("research_audit_primary_submission_allowed") is False
        and source_repository_context.get("research_audit_provenance_only") is True,
        "candidate lost research-audit provenance-only boundary",
    )
    checks.check(
        source_repository_context.get("full_audit_python_lines")
        == package_summary.get("combined_python_line_count")
        == main_code_checks.get("combined_python_line_count"),
        "candidate full-audit Python line count stale",
    )
    checks.check(
        source_repository_context.get("research_audit_primary_submission_line_limit") == 20000
        and source_repository_context.get("research_audit_too_large_for_primary_submission") is True,
        "candidate lost research-audit size boundary",
    )
    checks.check(
        source_repository_context.get("reviewer_facing_python_file_limit") == 12
        and source_repository_context.get("reviewer_facing_python_line_limit") == 2000,
        "candidate lost reviewer-facing code limits",
    )

    matrix_summary = manifest.get("matrix_summary", {})
    checks.check(matrix_summary.get("row_count") == matrix.get("row_count") == 44, "matrix row count changed")
    checks.check(matrix_summary.get("raw_row_count") == matrix.get("raw_row_count") == 132, "raw row count changed")
    checks.check(matrix_summary.get("method_count") == matrix.get("method_count") == 11, "method count changed")
    checks.check(
        matrix_summary.get("direct_nonlocal_velocity_order_wins") == 40,
        "common-reference order wins changed",
    )
    checks.check(
        matrix_summary.get("direct_nonlocal_velocity_error_wins") == 40,
        "common-reference error wins changed",
    )

    result_checks = review.get("result_checks", {})
    code_checks = review.get("code_hygiene_checks", {})
    for key in [
        "combined_python_line_count",
        "paper_python_line_count",
        "minimal_reproducibility_candidate_python_lines",
    ]:
        checks.check(
            code_checks.get(key) == main_code_checks.get(key),
            f"candidate review-agent code-size snapshot stale for {key}",
        )
    for key in [
        "blocker_open_by_id",
        "objective_blocker_open_by_id",
        "blocker_closure_decision_by_id",
        "blocker_closure_allowed_by_id",
        "open_blockers",
        "decision",
        "submission_standard_met",
    ]:
        checks.check(review.get(key) == main_review.get(key), f"candidate review-agent report stale for {key}")
    checks.check(
        review.get("blocker_open_by_id") == EXPECTED_OBJECTIVE_BLOCKER_OPEN_BY_ID,
        "candidate review objective blocker open map changed",
    )
    checks.check(
        review.get("objective_blocker_open_by_id") == EXPECTED_OBJECTIVE_BLOCKER_OPEN_BY_ID,
        "candidate review nested objective blocker open map changed",
    )
    checks.check(
        review.get("blocker_closure_decision_by_id") == EXPECTED_BLOCKER_CLOSURE_DECISION_BY_ID,
        "candidate review blocker closure decisions changed",
    )
    checks.check(
        review.get("blocker_closure_allowed_by_id") == EXPECTED_BLOCKER_CLOSURE_ALLOWED_BY_ID,
        "candidate review blocker closure permissions changed",
    )
    checks.check(review.get("open_blockers") == EXPECTED_OPEN_BLOCKERS, "candidate review open blocker list changed")
    checks.check(
        review.get("decision") == "do_not_submit_global" and review.get("submission_standard_met") is False,
        "candidate review global submission boundary changed",
    )
    checks.check(
        review.get("narrowed_submission_standard_met") is True,
        "review narrowed-claim standard not recorded",
    )
    checks.check(
        review.get("narrowed_claim_decision") == "submit_under_narrowed_claim",
        "review narrowed-claim decision changed",
    )
    checks.check(
        code_checks.get("minimal_reproducible_submission_code_ready") is False,
        "review overclaims minimal reproducible submission code",
    )
    checks.check(result_checks.get("source_policy_apples_to_apples_external_rows") == 0, "source rows changed")
    checks.check(result_checks.get("source_policy_apples_to_apples_external_total_rows") == 40, "source total changed")
    checks.check(proof.get("closure_state", {}).get("proof_gap_closed") is True, "proof manifest direct closure missing")
    checks.check(
        proof.get("closure_state", {}).get("stage_residual_O_h7_implementation_defect_proved") is True,
        "proof manifest stage-residual direct closure missing",
    )
    checks.check(proof.get("evidence_summary", {}).get("open_dynamic_rows") == 36, "open dynamic rows changed")
    checks.check(
        newton.get("obligation_coverage_matrix", {}).get("row_obligation_link_count") == 180,
        "Newton-Euler coverage links changed",
    )
    checks.check(
        newton.get("obligation_coverage_matrix", {}).get("proof_closure_advanced") is False,
        "Newton-Euler coverage overclaims proof closure",
    )
    runtime = newton.get("supporting_runtime_evidence", {})
    checks.check(
        runtime.get("runtime_source_component_layout_matches_targets") is True,
        "Newton-Euler runtime layout marker missing in candidate",
    )
    expected_layout = [
        ("body0_translational_balance_source", 0, 0, "translational_newton_balance"),
        ("body0_rotational_balance_source", 3, 0, "rotational_euler_balance"),
        ("body1_translational_balance_source", 6, 1, "translational_newton_balance"),
        ("body1_rotational_balance_source", 9, 1, "rotational_euler_balance"),
    ]
    expected_rows = []
    for stage in range(3):
        base = stage * 44 + 24
        for source, offset, body, block in expected_layout:
            for component_index, component in enumerate(["x", "y", "z"]):
                local = offset + component_index
                expected_rows.append((base + local, local, body, component, block, source))
    actual_rows = [
        (
            row.get("global_row"),
            row.get("local_block_row"),
            row.get("body"),
            row.get("component"),
            row.get("balance_block"),
            row.get("runtime_source_component"),
        )
        for row in newton.get("row_targets", [])
    ]
    checks.check(
        actual_rows == expected_rows,
        "Newton-Euler runtime row layout stale in candidate target audit",
    )

    for item in manifest.get("files", []):
        rel_path = item.get("path")
        path = CANDIDATE / str(rel_path)
        checks.check(path.exists() and path.stat().st_size > 0, f"candidate file missing: {rel_path}")
        if path.exists():
            checks.check(path.stat().st_size == item.get("bytes"), f"candidate file size changed: {rel_path}")
            checks.check(sha256(path) == item.get("sha256"), f"candidate file hash changed: {rel_path}")

    expected_files = {
        "README.md",
        "MANIFEST.json",
        *{str(item.get("path")) for item in manifest.get("files", [])},
    }
    actual_files = {
        path.relative_to(CANDIDATE).as_posix()
        for path in CANDIDATE.rglob("*")
        if path.is_file()
    }
    checks.check(actual_files == expected_files, f"candidate file set changed: {sorted(actual_files ^ expected_files)}")

    forbidden_patterns = [
        "build_*.py",
        "validate_*.py",
        "run_v047.py",
        "run_v048.py",
    ]
    for pattern in forbidden_patterns:
        matches = list(CANDIDATE.rglob(pattern))
        if pattern == "validate_*.py":
            matches = [path for path in matches if path.name != "replay_paper_matrix.py"]
        checks.check(not matches, f"candidate includes full audit/runner files matching {pattern}")

    replay = subprocess.run(
        [sys.executable, "scripts/replay_paper_matrix.py"],
        cwd=CANDIDATE,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    checks.check(replay.returncode == 0, f"replay script failed:\n{replay.stdout}")
    checks.check("cmame_minimal_candidate_replay=PASS" in replay.stdout, "replay PASS marker missing")
    checks.check("source_policy_apples_to_apples_external=0/40" in replay.stdout, "replay source boundary missing")
    checks.check("direct_pc2_proof_gap_closed=True" in replay.stdout, "replay direct-PC2 proof boundary missing")
    checks.check(
        "schema_compat_legacy_key_retained=True" in replay.stdout,
        "replay legacy compatibility marker missing",
    )
    checks.check(
        "\nproof_gap_closed=True\n" not in f"\n{replay.stdout}\n",
        "replay reintroduced naked proof_gap_closed marker",
    )
    checks.check(
        "proof_gap_scope=direct_residual_bridge_kantorovich_route_closed_primitive_taylor_conditional_schema_open"
        in replay.stdout,
        "replay proof-gap scope missing",
    )
    checks.check(
        "stage_residual_O_h7_direct_proof=True" in replay.stdout,
        "replay stage-residual proof boundary missing",
    )
    checks.check(
        "newton_euler_symbolic_defect_certificate_complete=False" in replay.stdout,
        "replay symbolic-certificate boundary missing",
    )
    checks.check("objective_blockers_open=OC4,OC6,OC12" in replay.stdout, "replay objective blockers missing")
    checks.check(
        "global_submission_decision=do_not_submit_global" in replay.stdout,
        "replay global submission decision missing",
    )

    for token in [
        "Status: **candidate_replay_package_built_not_submission_ready**.",
        "Submission ready: `False`.",
        "Candidate files: `10`.",
        "Reviewer-facing code policy: size-ok `True`, runner-centered `False`, replay-only `True`.",
        "Source-policy rows closed: `0/40`.",
        "Direct PC2 proof gap closed: `True`.",
        "Direct proof gap scope: `direct_residual_bridge_kantorovich_route_closed_primitive_taylor_conditional_schema_open`.",
        "Direct proof gap reading rule: The schema-only compatibility boolean proof_gap_closed is a schema-compatible shorthand for direct_pc2_proof_gap_closed and is scoped to the active direct PC2 residual-bridge/Kantorovich proof closure.",
        "Schema-only compatibility key `proof_gap_closed` retained: `True`; reader-facing proof status should use `direct_pc2_proof_gap_closed`.",
        "Stage residual O(h^7) direct proof: `True`.",
        "Newton-Euler coverage links: `180`.",
        "Objective blockers open: `OC4,OC6,OC12`.",
        "Global submission decision: `do_not_submit_global`.",
    ]:
        checks.check(token in manifest_md, f"candidate manifest markdown missing token: {token}")
    for token in [
        "candidate replay package, not submission ready",
        "source-policy apples-to-apples external rows: `0/40`",
        "direct-PC2 residual-bridge proof-closure artifact",
        "`proof_gap_scope=direct_residual_bridge_kantorovich_route_closed_primitive_taylor_conditional_schema_open`",
        "`direct_pc2_proof_gap_closed=True`",
        "`schema_compat_legacy_key_retained=True`",
        "direct PC2 proof gap closed: `True`",
        "legacy compatibility key retained only inside the manifest schema",
        "Newton-Euler symbolic defect certificate complete: `False`",
        "objective blockers open: `OC4,OC6,OC12`",
        "global submission decision: `do_not_submit_global`",
        "submission ready: `False`",
        "reviewer-facing code status: size-ok replay package, not a runner-centered submission package",
    ]:
        checks.check(token in readme, f"candidate README missing token: {token}")

    if checks.errors:
        print("cmame minimal reproducibility candidate validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("cmame minimal reproducibility candidate validation: PASS")
    print(f"candidate_files={manifest.get('candidate_file_count')}")
    print(f"candidate_python_lines={manifest.get('candidate_python_line_count')}")
    print(f"source_policy_closed={manifest.get('source_policy_closed_rows')}/{manifest.get('source_policy_total_rows')}")
    print(f"direct_pc2_proof_gap_closed={manifest.get('direct_pc2_proof_gap_closed')}")
    print(f"schema_compat_legacy_key_retained={manifest.get('proof_gap_closed')}")
    print("submission_ready=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
