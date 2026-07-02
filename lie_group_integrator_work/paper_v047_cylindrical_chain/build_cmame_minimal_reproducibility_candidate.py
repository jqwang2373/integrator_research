#!/usr/bin/env python3
"""Build a small reproducibility-candidate package from current paper artifacts.

The candidate package is intentionally a replay/check package, not a submission
ready source-policy runner package.  It keeps the 44-cell result table, proof
boundary, and review-agent output together with one small replay script so the
current paper evidence can be inspected without shipping the full audit tree.
"""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path


PAPER = Path(__file__).resolve().parent
CANDIDATE = PAPER / "cmame_minimal_reproducibility_candidate"
OUT_JSON = PAPER / "CMAME_MINIMAL_REPRODUCIBILITY_CANDIDATE_MANIFEST.json"
OUT_MD = PAPER / "CMAME_MINIMAL_REPRODUCIBILITY_CANDIDATE_MANIFEST.md"

DATA_FILES = [
    "PAPER_NUMERICAL_RESULT_MATRIX.csv",
    "PAPER_NUMERICAL_RESULT_MATRIX.json",
    "PAPER_NUMERICAL_RESULT_MATRIX.md",
    "FOUR_EXAMPLE_SOURCE_POLICY_DASHBOARD.json",
    "RESULT_TO_MANUSCRIPT_TRACEABILITY_AUDIT.json",
    "CMAME_REVIEW_AGENT_REPORT.json",
    "PROOF_CLOSURE_MANIFEST.json",
    "NEWTON_EULER_SYMBOLIC_TARGET_AUDIT.json",
    "CLAIM_BOUNDARY.json",
]

GENERATED_RELATIVE_PATHS = {
    "README.md",
    "MANIFEST.json",
    "scripts/replay_paper_matrix.py",
    *{f"data/{file_name}" for file_name in DATA_FILES},
}

EXPECTED_OBJECTIVE_BLOCKER_OPEN_BY_ID = {"OC4": True, "OC6": True, "OC12": True}
EXPECTED_BLOCKER_CLOSURE_DECISION_BY_ID = {
    "OC4": "remain_open_ready_for_authorized_execution_not_executed_not_promoted",
    "OC6": "remain_open_no_positive_source_equivalent_artifact",
    "OC12": "remain_partial_narrowed_replay_ready_full_source_policy_archive_not_ready",
}
EXPECTED_BLOCKER_CLOSURE_ALLOWED_BY_ID = {"OC4": False, "OC6": False, "OC12": False}
EXPECTED_OPEN_BLOCKERS = ["OC4", "OC6", "OC12"]


REPLAY_SCRIPT = r'''#!/usr/bin/env python3
"""Replay consistency checks for the CMAME minimal reproducibility candidate."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def main() -> int:
    errors: list[str] = []
    matrix = read_json(DATA / "PAPER_NUMERICAL_RESULT_MATRIX.json")
    review = read_json(DATA / "CMAME_REVIEW_AGENT_REPORT.json")
    proof = read_json(DATA / "PROOF_CLOSURE_MANIFEST.json")
    traceability = read_json(DATA / "RESULT_TO_MANUSCRIPT_TRACEABILITY_AUDIT.json")
    dashboard = read_json(DATA / "FOUR_EXAMPLE_SOURCE_POLICY_DASHBOARD.json")
    newton = read_json(DATA / "NEWTON_EULER_SYMBOLIC_TARGET_AUDIT.json")

    with (DATA / "PAPER_NUMERICAL_RESULT_MATRIX.csv").open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    expected_examples = {"single_pendulum", "double_pendulum", "four_link", "slider_crank"}
    expected_methods = {
        "local_Gauss6_FullVA",
        "hi2022_rA",
        "hi2022_rA_half",
        "ra2021_rA",
        "ra2021_reps",
        "ra2021_rp",
        "tfe2026_Newmark_beta",
        "tfe2026_TFE_m1",
        "tfe2026_TFE_m2",
        "tfe2026_trapezoidal",
        "vp2024_coordinate_partitioning_rA",
    }
    expected_blocker_open = {"OC4": True, "OC6": True, "OC12": True}
    expected_blocker_decisions = {
        "OC4": "remain_open_ready_for_authorized_execution_not_executed_not_promoted",
        "OC6": "remain_open_no_positive_source_equivalent_artifact",
        "OC12": "remain_partial_narrowed_replay_ready_full_source_policy_archive_not_ready",
    }
    expected_blocker_allowed = {"OC4": False, "OC6": False, "OC12": False}
    expected_open_blockers = ["OC4", "OC6", "OC12"]

    if len(rows) != 44:
        errors.append(f"CSV row count is {len(rows)}, expected 44")
    if matrix.get("row_count") != 44 or matrix.get("raw_row_count") != 132:
        errors.append("matrix row/raw-row counts changed")
    if set(matrix.get("examples", [])) != expected_examples:
        errors.append("matrix example set changed")
    if set(matrix.get("methods", [])) != expected_methods:
        errors.append("matrix method set changed")
    if matrix.get("direct_nonlocal_velocity_order_wins") != 40:
        errors.append("common-reference order wins changed")
    if matrix.get("direct_nonlocal_velocity_error_wins") != 40:
        errors.append("common-reference error wins changed")
    if matrix.get("source_policy_external_superiority_allowed") is not False:
        errors.append("source-policy superiority was overclaimed")
    if any(row.get("strict_external_error_claim_allowed") == "True" for row in rows):
        errors.append("CSV contains a strict external error claim")

    result_checks = review.get("result_checks", {})
    code_checks = review.get("code_hygiene_checks", {})
    proof_checks = review.get("proof_checks", {})
    if (
        review.get("narrowed_submission_standard_met") is not True
        or review.get("narrowed_claim_decision") != "submit_under_narrowed_claim"
    ):
        errors.append("review-agent narrowed-claim boundary changed")
    if review.get("blocker_open_by_id") != expected_blocker_open:
        errors.append("review-agent objective blocker open map is stale")
    if review.get("objective_blocker_open_by_id") != expected_blocker_open:
        errors.append("review-agent nested objective blocker open map is stale")
    if review.get("blocker_closure_decision_by_id") != expected_blocker_decisions:
        errors.append("review-agent blocker closure decisions changed")
    if review.get("blocker_closure_allowed_by_id") != expected_blocker_allowed:
        errors.append("review-agent blocker closure permissions changed")
    if review.get("open_blockers") != expected_open_blockers:
        errors.append("review-agent open blocker list changed")
    if review.get("decision") != "do_not_submit_global" or review.get("submission_standard_met") is not False:
        errors.append("review-agent global submission boundary changed")
    if code_checks.get("minimal_reproducible_submission_code_ready") is not False:
        errors.append("minimal reproducible submission code was overclaimed")
    if result_checks.get("source_policy_apples_to_apples_external_rows") != 0:
        errors.append("source-policy rows unexpectedly closed")
    if result_checks.get("source_policy_apples_to_apples_external_total_rows") != 40:
        errors.append("source-policy row total changed")
    if proof_checks.get("proof_closure_proof_gap_closed") is not True:
        errors.append("proof gap closure missing in review")
    if proof_checks.get("proof_closure_stage_residual_O_h7_implementation_defect_proved") is not True:
        errors.append("stage-residual direct proof closure missing in review")

    if traceability.get("claim_boundary", {}).get("result_to_manuscript_traceability_closed") is not True:
        errors.append("result-to-manuscript traceability is not closed")
    if dashboard.get("source_policy_dynamic_order_examples") not in (0, None):
        errors.append("dashboard overclosed source-policy dynamic-order examples")

    proof_state = proof.get("closure_state", {})
    if proof_state.get("proof_gap_closed") is not True:
        errors.append("proof manifest direct closure missing")
    if proof_state.get("stage_residual_O_h7_implementation_defect_proved") is not True:
        errors.append("proof manifest stage-residual direct closure missing")
    if proof.get("evidence_summary", {}).get("open_dynamic_rows") != 36:
        errors.append("open dynamic-row count changed")
    coverage = newton.get("obligation_coverage_matrix", {})
    if coverage.get("coverage_matrix_complete") is not True:
        errors.append("Newton-Euler obligation coverage matrix missing")
    if coverage.get("row_obligation_link_count") != 180:
        errors.append("Newton-Euler row-obligation link count changed")
    if coverage.get("proof_closure_advanced") is not False:
        errors.append("coverage matrix overclaims proof closure")
    runtime = newton.get("supporting_runtime_evidence", {})
    if runtime.get("runtime_source_component_layout_matches_targets") is not True:
        errors.append("Newton-Euler runtime source layout marker missing")
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
    if actual_rows != expected_rows:
        errors.append("Newton-Euler runtime row layout is stale or inconsistent")

    if errors:
        print("cmame_minimal_candidate_replay=FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print("cmame_minimal_candidate_replay=PASS")
    print("rows=44")
    print("methods=11")
    print("examples=4")
    print("common_reference_order_error_wins=40/40,40/40")
    print("source_policy_apples_to_apples_external=0/40")
    print("direct_pc2_proof_gap_closed=True")
    print("schema_compat_legacy_key_retained=True")
    print("proof_gap_scope=direct_residual_bridge_kantorovich_route_closed_primitive_taylor_conditional_schema_open")
    print("stage_residual_O_h7_direct_proof=True")
    print("newton_euler_symbolic_defect_certificate_complete=False")
    print("objective_blockers_open=OC4,OC6,OC12")
    print("global_submission_decision=do_not_submit_global")
    print("submission_ready=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
'''


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def copy_data_files() -> list[dict[str, object]]:
    copied: list[dict[str, object]] = []
    data_dir = CANDIDATE / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    for file_name in DATA_FILES:
        source = PAPER / file_name
        target = data_dir / file_name
        shutil.copyfile(source, target)
        copied.append(
            {
                "path": f"data/{file_name}",
                "source": file_name,
                "role": "paper_evidence_artifact",
                "bytes": target.stat().st_size,
                "sha256": sha256(target),
            }
        )
    return copied


def remove_stale_generated_files() -> None:
    if not CANDIDATE.exists():
        return
    for path in sorted(CANDIDATE.rglob("*"), reverse=True):
        if path.is_file() and path.relative_to(CANDIDATE).as_posix() not in GENERATED_RELATIVE_PATHS:
            path.unlink()
        elif path.is_dir() and not any(path.iterdir()):
            path.rmdir()


def python_line_count(path: Path) -> int:
    return len(path.read_text(encoding="utf-8", errors="replace").splitlines())


def main() -> None:
    CANDIDATE.mkdir(parents=True, exist_ok=True)
    remove_stale_generated_files()
    files = copy_data_files()

    replay_path = CANDIDATE / "scripts" / "replay_paper_matrix.py"
    write_text(replay_path, REPLAY_SCRIPT)
    files.append(
        {
            "path": "scripts/replay_paper_matrix.py",
            "source": "generated",
            "role": "bounded_common_reference_result_replay",
            "bytes": replay_path.stat().st_size,
            "sha256": sha256(replay_path),
            "python_lines": python_line_count(replay_path),
        }
    )

    matrix = read_json(PAPER / "PAPER_NUMERICAL_RESULT_MATRIX.json")
    review = read_json(PAPER / "CMAME_REVIEW_AGENT_REPORT.json")
    proof = read_json(PAPER / "PROOF_CLOSURE_MANIFEST.json")
    package_manifest = read_json(PAPER / "CMAME_REPRODUCIBILITY_PACKAGE_MANIFEST.json")
    result_checks = review.get("result_checks", {})
    proof_checks = review.get("proof_checks", {})
    objective_blocker_matrix = {
        "blocker_open_by_id": review.get("blocker_open_by_id"),
        "objective_blocker_open_by_id": review.get("objective_blocker_open_by_id"),
        "blocker_closure_decision_by_id": review.get("blocker_closure_decision_by_id"),
        "blocker_closure_allowed_by_id": review.get("blocker_closure_allowed_by_id"),
        "open_blockers": review.get("open_blockers"),
        "decision": review.get("decision"),
        "submission_standard_met": review.get("submission_standard_met"),
    }

    manifest = {
        "schema": "cmame-minimal-reproducibility-candidate-v1",
        "status": "candidate_replay_package_built_not_submission_ready",
        "submission_ready": False,
        "read_only_replay_package": True,
        "package_dir": "cmame_minimal_reproducibility_candidate",
        "paper_result_scope": "bounded_common_reference_only",
        "source_policy_external_superiority_allowed": False,
        "source_policy_closed_rows": result_checks.get("source_policy_apples_to_apples_external_rows"),
        "source_policy_total_rows": result_checks.get("source_policy_apples_to_apples_external_total_rows"),
        "proof_gap_closed": proof_checks.get("proof_closure_proof_gap_closed"),
        "direct_pc2_proof_gap_closed": proof_checks.get("proof_closure_proof_gap_closed"),
        "proof_gap_closed_scope": proof.get("closure_state", {}).get("proof_gap_closed_scope"),
        "proof_gap_closed_reading_rule": (
            "The schema-only compatibility boolean proof_gap_closed is a "
            "schema-compatible shorthand for direct_pc2_proof_gap_closed and "
            "is scoped to the active direct PC2 residual-bridge/Kantorovich "
            "proof closure. Reader-facing proof status should use "
            "direct_pc2_proof_gap_closed. The compatibility boolean does not "
            "close the primitive 162-subterm Taylor lane, source-policy rows, "
            "P6 solver-policy evidence, or P7 residual-to-error promotion."
        ),
        "schema_compatibility": {
            "legacy_key": "proof_gap_closed",
            "legacy_key_retained_for_schema_compatibility": True,
            "preferred_key": "direct_pc2_proof_gap_closed",
        },
        "objective_blocker_matrix": objective_blocker_matrix,
        "stage_residual_O_h7_implementation_defect_proved": proof_checks.get(
            "proof_closure_stage_residual_O_h7_implementation_defect_proved"
        ),
        "minimal_submission_code_ready": False,
        "matrix_summary": {
            "row_count": matrix.get("row_count"),
            "raw_row_count": matrix.get("raw_row_count"),
            "method_count": matrix.get("method_count"),
            "examples": matrix.get("examples"),
            "methods": matrix.get("methods"),
            "direct_nonlocal_velocity_order_wins": matrix.get("direct_nonlocal_velocity_order_wins"),
            "direct_nonlocal_velocity_order_comparisons": matrix.get(
                "direct_nonlocal_velocity_order_comparisons"
            ),
            "direct_nonlocal_velocity_error_wins": matrix.get("direct_nonlocal_velocity_error_wins"),
            "direct_nonlocal_velocity_error_comparisons": matrix.get(
                "direct_nonlocal_velocity_error_comparisons"
            ),
        },
        "proof_summary": {
            "open_dynamic_rows": proof.get("evidence_summary", {}).get("open_dynamic_rows"),
            "certified_non_dynamic_rows": proof.get("evidence_summary", {}).get("certified_non_dynamic_rows"),
            "newton_euler_obligation_coverage_matrix_complete": proof.get("evidence_summary", {}).get(
                "newton_euler_obligation_coverage_matrix_complete"
            ),
            "newton_euler_row_obligation_links": proof.get("evidence_summary", {}).get(
                "newton_euler_row_obligation_links"
            ),
        },
        "source_repository_context": {
            "full_audit_python_lines": package_manifest.get("summary", {}).get("combined_python_line_count"),
            "full_audit_code_bloat_risk_for_submission": package_manifest.get("summary", {}).get(
                "code_bloat_risk_for_submission"
            ),
            "research_audit_primary_submission_allowed": package_manifest.get("summary", {}).get(
                "research_audit_repo_primary_submission_allowed"
            ),
            "research_audit_provenance_only": package_manifest.get("summary", {}).get(
                "research_audit_repo_provenance_only"
            ),
            "research_audit_primary_submission_line_limit": package_manifest.get("summary", {}).get(
                "research_audit_primary_submission_line_limit"
            ),
            "research_audit_too_large_for_primary_submission": package_manifest.get("summary", {}).get(
                "research_audit_repo_too_large_for_primary_submission"
            ),
            "reviewer_facing_python_file_limit": package_manifest.get("summary", {}).get(
                "reviewer_facing_python_file_limit"
            ),
            "reviewer_facing_python_line_limit": package_manifest.get("summary", {}).get(
                "reviewer_facing_python_line_limit"
            ),
        },
        "reviewer_facing_code_policy": {
            "candidate_code_size_ok": True,
            "candidate_runner_centered": False,
            "candidate_replay_only": True,
            "primary_submission_package_required": True,
            "minimal_submission_code_ready": False,
        },
        "candidate_file_count": len(files),
        "candidate_python_file_count": 1,
        "candidate_python_line_count": python_line_count(replay_path),
        "files": files,
        "forbidden_claims": [
            "submission_ready_true",
            "source_policy_external_superiority_true",
            "minimal_submission_code_ready_true",
            "accepted_residual_to_error_theorem_true",
        ],
    }

    write_text(CANDIDATE / "MANIFEST.json", json.dumps(manifest, indent=2, sort_keys=True) + "\n")

    readme = [
        "# CMAME Minimal Reproducibility Candidate",
        "",
        "Status: candidate replay package, not submission ready.",
        "",
        "This directory is a shrink target for the current paper evidence. It",
        "contains the 44-cell paper result matrix, traceability and proof-boundary",
        "artifacts, and one replay script. It does not contain a full source-policy",
        "runner and does not upgrade any external-superiority claim. It carries",
        "the current direct-PC2 residual-bridge proof-closure artifact, while the symbolic",
        "Newton-Euler defect certificate remains a provenance boundary.",
        "",
        "Human-runnable quickstart:",
        "",
        "```bash",
        "python scripts/replay_paper_matrix.py",
        "```",
        "",
        "Expected terminal markers:",
        "",
        "- `cmame_minimal_candidate_replay=PASS`.",
        "- `rows=44`.",
        "- `methods=11`.",
        "- `examples=4`.",
        "- `common_reference_order_error_wins=40/40,40/40`.",
        "- `source_policy_apples_to_apples_external=0/40`.",
        "- `direct_pc2_proof_gap_closed=True`.",
        "- `schema_compat_legacy_key_retained=True`.",
        "- `proof_gap_scope=direct_residual_bridge_kantorovich_route_closed_primitive_taylor_conditional_schema_open`.",
        "- `stage_residual_O_h7_direct_proof=True`.",
        "- `newton_euler_symbolic_defect_certificate_complete=False`.",
        "- `objective_blockers_open=OC4,OC6,OC12`.",
        "- `global_submission_decision=do_not_submit_global`.",
        "- `submission_ready=False`.",
        "",
        "Run:",
        "",
        "```bash",
        "python scripts/replay_paper_matrix.py",
        "```",
        "",
        "Expected boundary:",
        "",
        "- common-reference order/error wins: `40/40` and `40/40`.",
        "- source-policy apples-to-apples external rows: `0/40`.",
        "- direct PC2 proof gap closed: `True`.",
        "- legacy compatibility key retained only inside the manifest schema.",
        "- Newton-Euler symbolic defect certificate complete: `False`.",
        "- objective blockers open: `OC4,OC6,OC12`.",
        "- global submission decision: `do_not_submit_global`.",
        "- submission ready: `False`.",
        "- reviewer-facing code status: size-ok replay package, not a runner-centered submission package.",
    ]
    write_text(CANDIDATE / "README.md", "\n".join(readme) + "\n")
    write_text(OUT_JSON, json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    write_text(
        OUT_MD,
        "\n".join(
            [
                "# CMAME Minimal Reproducibility Candidate Manifest",
                "",
                f"Status: **{manifest['status']}**.",
                f"Submission ready: `{manifest['submission_ready']}`.",
                f"Candidate files: `{manifest['candidate_file_count']}`.",
                f"Candidate Python size: `{manifest['candidate_python_file_count']}` file / `{manifest['candidate_python_line_count']}` lines.",
                f"Reviewer-facing code policy: size-ok `{manifest['reviewer_facing_code_policy']['candidate_code_size_ok']}`, runner-centered `{manifest['reviewer_facing_code_policy']['candidate_runner_centered']}`, replay-only `{manifest['reviewer_facing_code_policy']['candidate_replay_only']}`.",
                f"Source-policy rows closed: `{manifest['source_policy_closed_rows']}/{manifest['source_policy_total_rows']}`.",
                f"Direct PC2 proof gap closed: `{manifest['direct_pc2_proof_gap_closed']}`.",
                f"Direct proof gap scope: `{manifest['proof_gap_closed_scope']}`.",
                f"Direct proof gap reading rule: {manifest['proof_gap_closed_reading_rule']}",
                f"Schema-only compatibility key `proof_gap_closed` retained: `{manifest['schema_compatibility']['legacy_key_retained_for_schema_compatibility']}`; reader-facing proof status should use `{manifest['schema_compatibility']['preferred_key']}`.",
                f"Stage residual O(h^7) direct proof: `{manifest['stage_residual_O_h7_implementation_defect_proved']}`.",
                f"Newton-Euler coverage links: `{manifest['proof_summary']['newton_euler_row_obligation_links']}`.",
                f"Objective blockers open: `{','.join(manifest['objective_blocker_matrix']['open_blockers'])}`.",
                f"Global submission decision: `{manifest['objective_blocker_matrix']['decision']}`.",
                "",
                "Reading rule: this is a compact replay package for confirmed bounded-common-reference artifacts, not a source-policy runner package.",
            ]
        )
        + "\n",
    )

    print("cmame_minimal_reproducibility_candidate=written")
    print(f"candidate_files={manifest['candidate_file_count']}")
    print(f"candidate_python_lines={manifest['candidate_python_line_count']}")
    print(f"source_policy_closed={manifest['source_policy_closed_rows']}/{manifest['source_policy_total_rows']}")
    print("submission_ready=False")


if __name__ == "__main__":
    main()
