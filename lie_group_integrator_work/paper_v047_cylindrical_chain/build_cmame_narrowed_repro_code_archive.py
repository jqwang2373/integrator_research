#!/usr/bin/env python3
"""Build the narrowed-claim reviewer-facing reproducibility code archive."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo


PAPER = Path(__file__).resolve().parent
from paper_paths import LATEX, package_path as manuscript_path
OUT_ZIP = PAPER / "cmame_narrowed_repro_code_archive.zip"
OUT_JSON = PAPER / "CMAME_NARROWED_REPRO_CODE_ARCHIVE_MANIFEST.json"
OUT_MD = PAPER / "CMAME_NARROWED_REPRO_CODE_ARCHIVE_MANIFEST.md"
INTERNAL_MANIFEST = "CMAME_NARROWED_REPRO_CODE_ARCHIVE_INTERNAL_MANIFEST.json"
BLOCKER_IDS = ["OC4", "OC6", "OC12"]

SOURCE_DIRS = [
    "cmame_minimal_reproducibility_candidate",
    "cmame_runner_adapter_candidate",
    "cmame_p1_single_runner_candidate",
    "cmame_p1_double_runner_candidate",
    "cmame_closed_loop_local_runner_candidate",
    "cmame_local_accepted_runner_companion",
    "cmame_narrowed_repro_bundle",
]

SOURCE_FILES = [
    "REPRODUCIBILITY_GUIDE.md",
    "replay_reproducibility_core.py",
    "run_human_reproducibility.py",
    "human_reproducibility_result_table.md",
    "CLAIM_BOUNDARY.json",
    "PAPER_NUMERICAL_RESULT_MATRIX.json",
    "PAPER_NUMERICAL_RESULT_MATRIX.csv",
    "PAPER_NUMERICAL_RESULT_MATRIX.md",
    "CMAME_REVIEW_AGENT_REPORT.json",
    "PROOF_CLOSURE_MANIFEST.json",
    "OBJECTIVE_COMPLETION_AUDIT.json",
    "OBJECTIVE_COMPLETION_AUDIT.md",
    "FULL_SOURCE_POLICY_RUNNER_ARCHIVE_GAP_AUDIT.json",
    "FULL_SOURCE_POLICY_RUNNER_ARCHIVE_GAP_AUDIT.md",
    "CMAME_NARROWED_REPRODUCIBILITY_PACKAGE_AUDIT.json",
    "CMAME_NARROWED_REPRODUCIBILITY_PACKAGE_AUDIT.md",
    "B4_SOURCE_POLICY_EXECUTION_HANDOFF_PACKAGE.json",
    "B4_SOURCE_POLICY_EXECUTION_HANDOFF_PACKAGE.md",
    "CMAME_MINIMAL_REPRODUCIBILITY_CANDIDATE_MANIFEST.json",
    "CMAME_MINIMAL_REPRODUCIBILITY_CANDIDATE_MANIFEST.md",
    "CMAME_RUNNER_ADAPTER_CANDIDATE_MANIFEST.json",
    "CMAME_RUNNER_ADAPTER_CANDIDATE_MANIFEST.md",
    "CMAME_P1_LOCAL_RUNNER_EXTRACTION_AUDIT.json",
    "CMAME_P1_LOCAL_RUNNER_EXTRACTION_AUDIT.md",
    "CMAME_CLOSED_LOOP_LOCAL_RUNNER_CANDIDATE_MANIFEST.json",
    "CMAME_CLOSED_LOOP_LOCAL_RUNNER_CANDIDATE_MANIFEST.md",
    "CMAME_LOCAL_ACCEPTED_RUNNER_COMPANION_MANIFEST.json",
    "CMAME_LOCAL_ACCEPTED_RUNNER_COMPANION_MANIFEST.md",
    "B6_FOUR_EXAMPLE_LOCAL_EVIDENCE_SUMMARY.json",
    "B6_FOUR_EXAMPLE_LOCAL_EVIDENCE_SUMMARY.md",
    "validate_cmame_narrowed_repro_bundle.py",
    "validate_cmame_minimal_reproducibility_candidate.py",
    "validate_cmame_runner_adapter_candidate.py",
    "validate_cmame_p1_single_runner_candidate.py",
    "validate_cmame_p1_double_runner_candidate.py",
    "validate_cmame_closed_loop_local_runner_candidate.py",
    "validate_cmame_local_accepted_runner_companion.py",
]

REQUIRED_ENTRIES = [
    "run_human_reproducibility.py",
    "replay_reproducibility_core.py",
    "cmame_narrowed_repro_bundle/scripts/run_narrowed_repro_bundle.py",
    "cmame_minimal_reproducibility_candidate/scripts/replay_paper_matrix.py",
    "cmame_runner_adapter_candidate/scripts/run_four_example_matrix_adapter.py",
    "cmame_runner_adapter_candidate/scripts/replay_closed_loop_local_rows.py",
    "cmame_p1_single_runner_candidate/scripts/run_single_pendulum_fullva.py",
    "cmame_p1_double_runner_candidate/scripts/run_double_pendulum_fullva.py",
    "cmame_closed_loop_local_runner_candidate/scripts/run_closed_loop_fullva_candidate.py",
    "cmame_local_accepted_runner_companion/scripts/run_local_accepted_runner_companion.py",
]


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def blocker_token(values: dict) -> str:
    return ",".join(f"{blocker_id}:{values[blocker_id]}" for blocker_id in BLOCKER_IDS)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def should_skip(path: Path) -> bool:
    parts = set(path.parts)
    return "__pycache__" in parts or path.suffix in {".pyc", ".pyo"}


def source_entries() -> list[Path]:
    entries: list[Path] = []
    for rel in SOURCE_FILES:
        path = manuscript_path(rel)
        if not path.exists() or path.stat().st_size == 0:
            raise FileNotFoundError(rel)
        entries.append(path)
    for rel_dir in SOURCE_DIRS:
        root = manuscript_path(rel_dir)
        if not root.exists():
            raise FileNotFoundError(rel_dir)
        for path in sorted(root.rglob("*")):
            if path.is_file() and not should_skip(path):
                entries.append(path)
    dedup: dict[str, Path] = {}
    for path in entries:
        dedup[path.relative_to(PAPER).as_posix()] = path
    return [dedup[key] for key in sorted(dedup)]


def zip_write_bytes(archive: ZipFile, arcname: str, data: bytes) -> None:
    info = ZipInfo(arcname)
    info.date_time = (1980, 1, 1, 0, 0, 0)
    info.compress_type = ZIP_DEFLATED
    archive.writestr(info, data)


def zip_write_file(archive: ZipFile, path: Path, arcname: str) -> None:
    zip_write_bytes(archive, arcname, path.read_bytes())


def main() -> None:
    narrowed = read_json(PAPER / "CMAME_NARROWED_REPRODUCIBILITY_PACKAGE_AUDIT.json")
    objective_completion = read_json(PAPER / "OBJECTIVE_COMPLETION_AUDIT.json")
    archive_gap = read_json(PAPER / "FULL_SOURCE_POLICY_RUNNER_ARCHIVE_GAP_AUDIT.json")
    b4_handoff = read_json(PAPER / "B4_SOURCE_POLICY_EXECUTION_HANDOFF_PACKAGE.json")
    b4_driver = b4_handoff.get("approval_boundary", {}).get("guarded_execution_driver", {})
    source_policy_execution_handoff = {
        "status": b4_handoff.get("status"),
        "execution_authorized": b4_handoff.get("execution_authorized"),
        "commands_not_run_by_handoff": b4_handoff.get("commands_not_run_by_handoff"),
        "exact_required_user_approval_statement": b4_handoff.get(
            "approval_boundary", {}
        ).get("exact_required_user_approval_statement"),
        "guarded_execution_driver": b4_driver.get("path"),
        "driver_requires_exact_approval": b4_driver.get("requires_exact_approval_argument"),
        "driver_does_not_authorize_execution": b4_driver.get(
            "driver_does_not_authorize_execution"
        ),
        "opt_in_required_command_count": b4_handoff.get("opt_in_required_actions", {}).get(
            "command_count"
        ),
        "opt_in_required_mapped_external_rows": b4_handoff.get(
            "opt_in_required_actions", {}
        ).get("mapped_external_rows"),
        "terminal_unable_to_reproduce_rows": b4_handoff.get("source_policy_row_state", {}).get(
            "unable_to_reproduce"
        ),
        "boundary_artifacts": [
            "B4_SOURCE_POLICY_EXECUTION_HANDOFF_PACKAGE.json",
            "B4_SOURCE_POLICY_EXECUTION_HANDOFF_PACKAGE.md",
        ],
    }
    action_boundary_aliases = {
        "source_policy_execution_allowed_now": archive_gap.get(
            "source_policy_execution_allowed_now",
            archive_gap.get("action_boundary", {}).get("source_policy_execution_allowed_now"),
        ),
        "source_policy_execution_invoked": archive_gap.get("source_policy_execution_invoked"),
        "exact_b4_opt_in_required_for_execution": archive_gap.get(
            "exact_b4_opt_in_required_for_execution",
            archive_gap.get("action_boundary", {}).get(
                "exact_b4_opt_in_required_for_execution"
            ),
        ),
        "safe_action_ids": archive_gap.get("safe_action_ids"),
        "opt_in_action_ids": archive_gap.get("opt_in_action_ids"),
        "required_user_approval_statement": archive_gap.get(
            "required_user_approval_statement",
            source_policy_execution_handoff.get("exact_required_user_approval_statement"),
        ),
        "guarded_execution_driver": archive_gap.get(
            "guarded_execution_driver",
            source_policy_execution_handoff.get("guarded_execution_driver"),
        ),
    }
    objective_blocking_ids = ["OC4", "OC6", "OC12"]
    objective_status_by_id = {
        blocker_id: objective_completion.get("blocker_status_by_id", {}).get(blocker_id)
        for blocker_id in objective_blocking_ids
    }
    objective_next_actions_by_id = {
        blocker_id: objective_completion.get("blocker_next_actions_by_id", {}).get(blocker_id)
        for blocker_id in objective_blocking_ids
    }
    objective_required_to_close_by_id = {
        blocker_id: objective_completion.get("blocker_required_to_close_by_id", {}).get(blocker_id)
        for blocker_id in objective_blocking_ids
    }
    objective_safe_next_actions_by_id = {
        blocker_id: objective_completion.get("blocker_safe_next_actions_by_id", {}).get(blocker_id)
        for blocker_id in objective_blocking_ids
    }
    objective_opt_in_required_actions_by_id = {
        blocker_id: objective_completion.get("blocker_opt_in_required_actions_by_id", {}).get(blocker_id)
        for blocker_id in objective_blocking_ids
    }
    objective_archive_boundary = archive_gap.get("objective_archive_blocker_boundary", {})
    archive_closure_status_by_id = {
        blocker_id: objective_archive_boundary.get("archive_closure_status_by_id", {}).get(
            blocker_id
        )
        for blocker_id in objective_blocking_ids
    }
    archive_effect_by_id = {
        blocker_id: objective_archive_boundary.get("archive_effect_by_id", {}).get(blocker_id)
        for blocker_id in objective_blocking_ids
    }
    closure_allowed_by_id = {
        blocker_id: objective_archive_boundary.get("closure_allowed_by_id", {}).get(blocker_id)
        for blocker_id in objective_blocking_ids
    }
    blocker_open_by_id = {
        blocker_id: objective_completion.get("blocker_open_by_id", {}).get(blocker_id)
        for blocker_id in objective_blocking_ids
    }
    blocker_closure_decision_by_id = {
        blocker_id: objective_completion.get("blocker_closure_decision_by_id", {}).get(
            blocker_id
        )
        for blocker_id in objective_blocking_ids
    }
    blocker_closure_allowed_by_id = {
        blocker_id: objective_completion.get("blocker_closure_allowed_by_id", {}).get(
            blocker_id
        )
        for blocker_id in objective_blocking_ids
    }
    narrowed_archive_boundary = {
        "schema": "narrowed-repro-code-archive-boundary-v1",
        "status": "narrowed_archive_ready_not_full_source_policy_runner_archive",
        "scope": "narrowed_claim_only",
        "objective_blocker_matrix_status": "global_objective_blockers_remain_open",
        "objective_completion_status": objective_completion.get("status"),
        "objective_complete": objective_completion.get("objective_complete"),
        "objective_submission_ready": objective_completion.get("submission_ready"),
        "blocking_ids": objective_blocking_ids,
        "blocker_open_by_id": blocker_open_by_id,
        "blocker_status_by_id": objective_status_by_id,
        "blocker_closure_decision_by_id": blocker_closure_decision_by_id,
        "blocker_closure_allowed_by_id": blocker_closure_allowed_by_id,
        "blocker_next_actions_by_id": objective_next_actions_by_id,
        "blocker_required_to_close_by_id": objective_required_to_close_by_id,
        "blocker_safe_next_actions_by_id": objective_safe_next_actions_by_id,
        "blocker_opt_in_required_actions_by_id": objective_opt_in_required_actions_by_id,
        "archive_closure_status_by_id": archive_closure_status_by_id,
        "archive_effect_by_id": archive_effect_by_id,
        "closure_allowed_by_id": closure_allowed_by_id,
        "source_policy_closed_ratio": objective_completion.get("source_policy_closed_ratio"),
        "narrowed_claim_reproducibility_package_ready": narrowed.get(
            "narrowed_claim_reproducibility_package_ready"
        ),
        "full_source_policy_runner_package_ready": False,
        "current_archive_usable_as_full_source_policy_runner_archive": archive_gap.get(
            "closure_conditions", {}
        ).get("can_use_current_archive_as_full_source_policy_runner_archive"),
        "source_policy_execution_allowed_now": action_boundary_aliases[
            "source_policy_execution_allowed_now"
        ],
        "source_policy_execution_invoked": action_boundary_aliases[
            "source_policy_execution_invoked"
        ],
        "exact_b4_opt_in_required_for_execution": action_boundary_aliases[
            "exact_b4_opt_in_required_for_execution"
        ],
        "safe_action_ids": action_boundary_aliases["safe_action_ids"],
        "opt_in_action_ids": action_boundary_aliases["opt_in_action_ids"],
        "required_user_approval_statement": action_boundary_aliases[
            "required_user_approval_statement"
        ],
        "guarded_execution_driver": action_boundary_aliases["guarded_execution_driver"],
        "source_artifacts": [
            "OBJECTIVE_COMPLETION_AUDIT.json",
            "OBJECTIVE_COMPLETION_AUDIT.md",
            "FULL_SOURCE_POLICY_RUNNER_ARCHIVE_GAP_AUDIT.json",
            "FULL_SOURCE_POLICY_RUNNER_ARCHIVE_GAP_AUDIT.md",
        ],
    }
    entries = source_entries()
    entry_records = [
        {
            "path": path.relative_to(PAPER).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
            "role": "python_source" if path.suffix == ".py" else "supporting_artifact",
        }
        for path in entries
    ]
    entry_paths = {item["path"] for item in entry_records}
    missing_required = [item for item in REQUIRED_ENTRIES if item not in entry_paths]
    if missing_required:
        raise FileNotFoundError(", ".join(missing_required))

    python_file_count = sum(1 for path in entries if path.suffix == ".py")
    python_line_count = sum(
        len(path.read_text(encoding="utf-8", errors="replace").splitlines())
        for path in entries
        if path.suffix == ".py"
    )
    internal_manifest = {
        "schema": "cmame-narrowed-repro-code-archive-internal-manifest-v1",
        "status": "narrowed_repro_code_archive_ready_source_policy_open",
        "entrypoint": "cmame_narrowed_repro_bundle/scripts/run_narrowed_repro_bundle.py",
        "scope": "narrowed_claim_only",
        "narrowed_claim_reproducibility_package_ready": narrowed.get(
            "narrowed_claim_reproducibility_package_ready"
        ),
        "source_policy_rows_closed": narrowed.get("source_policy_rows_closed"),
        "source_policy_rows_total": narrowed.get("source_policy_rows_total"),
        "source_policy_execution_handoff": source_policy_execution_handoff,
        **action_boundary_aliases,
        "narrowed_archive_boundary": narrowed_archive_boundary,
        "full_source_policy_runner_package_ready": narrowed.get(
            "full_source_policy_runner_package_ready"
        ),
        "submission_ready": False,
        "run_v047_invoked": False,
        "run_v048_invoked": False,
        "entry_count_without_internal_manifest": len(entry_records),
        "python_file_count": python_file_count,
        "python_line_count": python_line_count,
        "required_entries": REQUIRED_ENTRIES,
        "entries": entry_records,
    }
    internal_bytes = json.dumps(internal_manifest, indent=2, sort_keys=True).encode("utf-8") + b"\n"

    with ZipFile(OUT_ZIP, "w", ZIP_DEFLATED) as archive:
        for path in entries:
            zip_write_file(archive, path, path.relative_to(PAPER).as_posix())
        zip_write_bytes(archive, INTERNAL_MANIFEST, internal_bytes)

    manifest = {
        "schema": "cmame-narrowed-repro-code-archive-manifest-v1",
        "status": "narrowed_repro_code_archive_ready_source_policy_open",
        "archive": OUT_ZIP.name,
        "archive_bytes": OUT_ZIP.stat().st_size,
        "archive_sha256": sha256_file(OUT_ZIP),
        "entrypoint": internal_manifest["entrypoint"],
        "scope": "narrowed_claim_only",
        "narrowed_claim_reproducibility_package_ready": internal_manifest[
            "narrowed_claim_reproducibility_package_ready"
        ],
        "source_policy_rows_closed": internal_manifest["source_policy_rows_closed"],
        "source_policy_rows_total": internal_manifest["source_policy_rows_total"],
        "source_policy_execution_handoff": source_policy_execution_handoff,
        **action_boundary_aliases,
        "narrowed_archive_boundary": narrowed_archive_boundary,
        "full_source_policy_runner_package_ready": False,
        "source_policy_external_superiority_allowed": False,
        "submission_ready": False,
        "run_v047_invoked": False,
        "run_v048_invoked": False,
        "entry_count": len(entry_records) + 1,
        "python_file_count": python_file_count,
        "python_line_count": python_line_count,
        "required_entries": REQUIRED_ENTRIES,
        "internal_manifest": {
            "path": INTERNAL_MANIFEST,
            "bytes": len(internal_bytes),
            "sha256": sha256_bytes(internal_bytes),
        },
        "entries": entry_records,
    }
    OUT_JSON.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# CMAME Narrowed Reproducibility Code Archive Manifest",
        "",
        f"Status: **{manifest['status']}**.",
        f"Archive: `{manifest['archive']}`.",
        f"Entries: `{manifest['entry_count']}`.",
        f"Python files/lines: `{manifest['python_file_count']}/{manifest['python_line_count']}`.",
        f"Narrowed package ready: `{manifest['narrowed_claim_reproducibility_package_ready']}`.",
        f"Source-policy rows closed: `{manifest['source_policy_rows_closed']}/{manifest['source_policy_rows_total']}`.",
        f"Source-policy execution allowed now/invoked/exact opt-in required: `{manifest['source_policy_execution_allowed_now']}/{manifest['source_policy_execution_invoked']}/{manifest['exact_b4_opt_in_required_for_execution']}`.",
        f"Source-policy safe/opt-in action ids: `{manifest['safe_action_ids']}/{manifest['opt_in_action_ids']}`.",
        f"Source-policy required approval/driver: `{manifest['required_user_approval_statement']}/{manifest['guarded_execution_driver']}`.",
        f"Source-policy execution handoff exact approval/driver: `{source_policy_execution_handoff['exact_required_user_approval_statement']}/{source_policy_execution_handoff['guarded_execution_driver']}/{source_policy_execution_handoff['driver_requires_exact_approval']}/{source_policy_execution_handoff['driver_does_not_authorize_execution']}/{source_policy_execution_handoff['opt_in_required_command_count']}/{source_policy_execution_handoff['opt_in_required_mapped_external_rows']}`.",
        f"Source-policy execution handoff authorized/commands-not-run/terminal-unable: `{source_policy_execution_handoff['execution_authorized']}/{source_policy_execution_handoff['commands_not_run_by_handoff']}/{source_policy_execution_handoff['terminal_unable_to_reproduce_rows']}`.",
        f"Narrowed archive boundary/status/scope: `{narrowed_archive_boundary['status']}/{narrowed_archive_boundary['scope']}`.",
        f"Narrowed archive objective blockers: `{narrowed_archive_boundary['blocking_ids']}`.",
        f"Narrowed archive blocker status by id: `{narrowed_archive_boundary['blocker_status_by_id']}`.",
        f"Narrowed archive blocker next actions by id: `{narrowed_archive_boundary['blocker_next_actions_by_id']}`.",
        f"Narrowed archive blocker required-to-close by id: `{narrowed_archive_boundary['blocker_required_to_close_by_id']}`.",
        f"Narrowed archive blocker safe next actions by id: `{narrowed_archive_boundary['blocker_safe_next_actions_by_id']}`.",
        f"Narrowed archive blocker opt-in required actions by id: `{narrowed_archive_boundary['blocker_opt_in_required_actions_by_id']}`.",
        f"Narrowed archive blocker effects by id: `{narrowed_archive_boundary['archive_effect_by_id']}`.",
        f"Narrowed archive current/full-source/use/execution/exact: `{narrowed_archive_boundary['narrowed_claim_reproducibility_package_ready']}/{narrowed_archive_boundary['full_source_policy_runner_package_ready']}/{narrowed_archive_boundary['current_archive_usable_as_full_source_policy_runner_archive']}/{narrowed_archive_boundary['source_policy_execution_allowed_now']}/{narrowed_archive_boundary['exact_b4_opt_in_required_for_execution']}`.",
        f"Narrowed archive safe/opt-in action ids: `{narrowed_archive_boundary['safe_action_ids']}/{narrowed_archive_boundary['opt_in_action_ids']}`.",
        "",
        "## Objective Blocker Matrix",
        "",
        "This manifest records the reviewer-facing narrowed archive boundary. It does not close the global objective blockers.",
        "",
        f"- `blocker_open_by_id={blocker_token(narrowed_archive_boundary['blocker_open_by_id'])}`",
        f"- `blocker_closure_decision_by_id={blocker_token(narrowed_archive_boundary['blocker_closure_decision_by_id'])}`",
        f"- `blocker_closure_allowed_by_id={blocker_token(narrowed_archive_boundary['blocker_closure_allowed_by_id'])}`",
        "",
        f"Full source-policy runner package ready: `{manifest['full_source_policy_runner_package_ready']}`.",
        f"Submission ready: `{manifest['submission_ready']}`.",
        "",
        "Run after extraction from the archive root:",
        "",
        "```bash",
        "python cmame_narrowed_repro_bundle/scripts/run_narrowed_repro_bundle.py",
        "```",
        "",
        "Boundary: this is a runnable narrowed-claim archive, not a full source-policy runner archive.",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("cmame_narrowed_repro_code_archive=written")
    print(f"archive={OUT_ZIP.name}")
    print(f"entries={manifest['entry_count']}")
    print(f"python_files_lines={python_file_count}/{python_line_count}")
    print(f"source_policy_rows={manifest['source_policy_rows_closed']}/{manifest['source_policy_rows_total']}")
    print(f"source_policy_execution_allowed_now={manifest['source_policy_execution_allowed_now']}")
    print(f"source_policy_execution_invoked={manifest['source_policy_execution_invoked']}")
    print(
        "exact_b4_opt_in_required_for_execution="
        f"{manifest['exact_b4_opt_in_required_for_execution']}"
    )
    print("full_source_policy_runner_package_ready=False")
    print("submission_ready=False")


if __name__ == "__main__":
    main()
