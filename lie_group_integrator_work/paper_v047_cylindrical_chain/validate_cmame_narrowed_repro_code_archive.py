#!/usr/bin/env python3
"""Validate the narrowed-claim reviewer-facing reproducibility code archive."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from zipfile import ZipFile


PAPER = Path(__file__).resolve().parent
MANIFEST = PAPER / "CMAME_NARROWED_REPRO_CODE_ARCHIVE_MANIFEST.json"
MANIFEST_MD = PAPER / "CMAME_NARROWED_REPRO_CODE_ARCHIVE_MANIFEST.md"
ARCHIVE = PAPER / "cmame_narrowed_repro_code_archive.zip"

EXPECTED_REQUIRED = [
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
EXPECTED_SAFE_ACTION_IDS = [
    "rebuild_read_only_audit_chain",
    "rerun_read_only_validators",
    "keep_narrowed_archive_provenance_only",
    "monitor_reopen_conditions",
]
EXPECTED_OPT_IN_ACTION_IDS = ["authorized_b4_ra_hi_source_policy_execution"]
EXPECTED_APPROVAL_STATEMENT = (
    "I explicitly approve running the B4 source-policy execution commands listed in "
    "B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json."
)
EXPECTED_GUARDED_DRIVER = "run_b4_source_policy_after_opt_in.sh"
EXPECTED_ACTION_BOUNDARY_ALIASES = {
    "source_policy_execution_allowed_now": False,
    "source_policy_execution_invoked": False,
    "exact_b4_opt_in_required_for_execution": True,
    "safe_action_ids": EXPECTED_SAFE_ACTION_IDS,
    "opt_in_action_ids": EXPECTED_OPT_IN_ACTION_IDS,
    "required_user_approval_statement": EXPECTED_APPROVAL_STATEMENT,
    "guarded_execution_driver": EXPECTED_GUARDED_DRIVER,
}
EXPECTED_BLOCKER_OPEN_BY_ID = {"OC4": True, "OC6": True, "OC12": True}
EXPECTED_BLOCKER_CLOSURE_DECISION_BY_ID = {
    "OC4": "remain_open_ready_for_authorized_execution_not_executed_not_promoted",
    "OC6": "remain_open_no_positive_source_equivalent_artifact",
    "OC12": "remain_partial_narrowed_replay_ready_full_source_policy_archive_not_ready",
}
EXPECTED_BLOCKER_CLOSURE_ALLOWED_BY_ID = {"OC4": False, "OC6": False, "OC12": False}
EXPECTED_BLOCKER_OPEN_TOKEN = "blocker_open_by_id=OC4:True,OC6:True,OC12:True"
EXPECTED_BLOCKER_CLOSURE_DECISION_TOKEN = (
    "blocker_closure_decision_by_id="
    "OC4:remain_open_ready_for_authorized_execution_not_executed_not_promoted,"
    "OC6:remain_open_no_positive_source_equivalent_artifact,"
    "OC12:remain_partial_narrowed_replay_ready_full_source_policy_archive_not_ready"
)
EXPECTED_BLOCKER_CLOSURE_ALLOWED_TOKEN = (
    "blocker_closure_allowed_by_id=OC4:False,OC6:False,OC12:False"
)


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    errors: list[str] = []
    try:
        manifest = read_json(MANIFEST)
        manifest_md = read_text(MANIFEST_MD)
        b4_handoff = read_json(PAPER / "B4_SOURCE_POLICY_EXECUTION_HANDOFF_PACKAGE.json")
        objective_completion = read_json(PAPER / "OBJECTIVE_COMPLETION_AUDIT.json")
        archive_gap = read_json(PAPER / "FULL_SOURCE_POLICY_RUNNER_ARCHIVE_GAP_AUDIT.json")
    except Exception as exc:  # noqa: BLE001
        print(f"CMAME narrowed repro code archive validation: FAIL\n- {exc}")
        return 1

    if manifest.get("schema") != "cmame-narrowed-repro-code-archive-manifest-v1":
        errors.append("manifest schema changed")
    if manifest.get("status") != "narrowed_repro_code_archive_ready_source_policy_open":
        errors.append("manifest status changed")
    if manifest.get("archive") != ARCHIVE.name:
        errors.append("archive path changed")
    if not ARCHIVE.exists() or ARCHIVE.stat().st_size == 0:
        errors.append("archive missing or empty")
    elif manifest.get("archive_bytes") != ARCHIVE.stat().st_size:
        errors.append("archive byte count stale")
    elif manifest.get("archive_sha256") != sha256_file(ARCHIVE):
        errors.append("archive sha256 stale")

    if manifest.get("narrowed_claim_reproducibility_package_ready") is not True:
        errors.append("narrowed package readiness missing")
    if manifest.get("source_policy_rows_closed") != 0 or manifest.get("source_policy_rows_total") != 40:
        errors.append("source-policy row boundary changed")
    expected_blocking_ids = ["OC4", "OC6", "OC12"]
    expected_status_by_id = {"OC4": "open", "OC6": "partial", "OC12": "partial"}
    expected_next_actions_by_id = {
        "OC4": (
            "RA/HI can only close through exact B4 opt-in authorized closeout or a new "
            "source-policy promotion artifact; TFE/VP remain unable-to-reproduce/not-promoted"
        ),
        "OC6": (
            "keep TFE source-policy terminal/unable-to-reproduce unless a new public or "
            "source-code-equivalent TFE implementation artifact appears"
        ),
        "OC12": (
            "promote the partial local runner package to a full source-policy runner "
            "archive after OC4/OC6 close"
        ),
    }
    expected_archive_status_by_id = {
        "OC4": "open",
        "OC6": "partial_terminal_not_promoted",
        "OC12": "partial_narrowed_replay_ready_full_archive_open",
    }
    expected_archive_effect_by_id = {
        "OC4": "blocks_full_archive_primary_use",
        "OC6": "blocks_tfe_rows_from_full_archive_promotion",
        "OC12": "current_archive_is_narrowed_claim_provenance_only",
    }
    expected_source_artifacts = [
        "OBJECTIVE_COMPLETION_AUDIT.json",
        "OBJECTIVE_COMPLETION_AUDIT.md",
        "FULL_SOURCE_POLICY_RUNNER_ARCHIVE_GAP_AUDIT.json",
        "FULL_SOURCE_POLICY_RUNNER_ARCHIVE_GAP_AUDIT.md",
    ]
    gap_objective_boundary = archive_gap.get("objective_archive_blocker_boundary", {})
    manifest_action_boundary_aliases = {
        key: manifest.get(key) for key in EXPECTED_ACTION_BOUNDARY_ALIASES
    }
    archive_gap_action_boundary_aliases = {
        key: archive_gap.get(key) for key in EXPECTED_ACTION_BOUNDARY_ALIASES
    }
    if not (
        manifest_action_boundary_aliases
        == archive_gap_action_boundary_aliases
        == EXPECTED_ACTION_BOUNDARY_ALIASES
    ):
        errors.append("archive manifest top-level source-policy action boundary changed")
    narrowed_boundary = manifest.get("narrowed_archive_boundary", {})
    if not (
        narrowed_boundary.get("schema") == "narrowed-repro-code-archive-boundary-v1"
        and narrowed_boundary.get("status")
        == "narrowed_archive_ready_not_full_source_policy_runner_archive"
        and narrowed_boundary.get("scope") == "narrowed_claim_only"
    ):
        errors.append("narrowed archive boundary schema/status/scope changed")
    if not (
        narrowed_boundary.get("objective_completion_status")
        == objective_completion.get("status")
        == "not_complete_submission_standard_open"
        and narrowed_boundary.get("objective_complete")
        == objective_completion.get("objective_complete")
        is False
        and narrowed_boundary.get("objective_submission_ready")
        == objective_completion.get("submission_ready")
        is False
    ):
        errors.append("objective completion state not carried into narrowed archive boundary")
    if not (
        narrowed_boundary.get("blocking_ids")
        == objective_completion.get("blocking_ids")
        == expected_blocking_ids
    ):
        errors.append("objective blocker ids not carried into narrowed archive boundary")
    if narrowed_boundary.get("objective_blocker_matrix_status") != "global_objective_blockers_remain_open":
        errors.append("objective blocker matrix status not carried into narrowed archive boundary")
    if not (
        narrowed_boundary.get("blocker_open_by_id")
        == objective_completion.get("blocker_open_by_id")
        == EXPECTED_BLOCKER_OPEN_BY_ID
    ):
        errors.append("objective blocker open map not carried into narrowed archive boundary")
    if not (
        narrowed_boundary.get("blocker_status_by_id")
        == objective_completion.get("blocker_status_by_id")
        == expected_status_by_id
    ):
        errors.append("objective blocker statuses not carried into narrowed archive boundary")
    if not (
        narrowed_boundary.get("blocker_closure_decision_by_id")
        == objective_completion.get("blocker_closure_decision_by_id")
        == EXPECTED_BLOCKER_CLOSURE_DECISION_BY_ID
    ):
        errors.append("objective blocker closure-decision map not carried into narrowed archive boundary")
    if not (
        narrowed_boundary.get("blocker_closure_allowed_by_id")
        == objective_completion.get("blocker_closure_allowed_by_id")
        == EXPECTED_BLOCKER_CLOSURE_ALLOWED_BY_ID
    ):
        errors.append("objective blocker closure-allowed map not carried into narrowed archive boundary")
    if not (
        narrowed_boundary.get("blocker_next_actions_by_id")
        == objective_completion.get("blocker_next_actions_by_id")
        == expected_next_actions_by_id
    ):
        errors.append("objective blocker next actions not carried into narrowed archive boundary")
    if narrowed_boundary.get("blocker_required_to_close_by_id") != objective_completion.get(
        "blocker_required_to_close_by_id"
    ):
        errors.append("objective blocker required-to-close map not carried into narrowed archive boundary")
    if narrowed_boundary.get("blocker_safe_next_actions_by_id") != objective_completion.get(
        "blocker_safe_next_actions_by_id"
    ):
        errors.append("objective blocker safe-next-action map not carried into narrowed archive boundary")
    if narrowed_boundary.get("blocker_opt_in_required_actions_by_id") != objective_completion.get(
        "blocker_opt_in_required_actions_by_id"
    ):
        errors.append("objective blocker opt-in-required-action map not carried into narrowed archive boundary")
    if not (
        narrowed_boundary.get("archive_closure_status_by_id")
        == gap_objective_boundary.get("archive_closure_status_by_id")
        == expected_archive_status_by_id
    ):
        errors.append("archive closure status map not carried into narrowed archive boundary")
    if not (
        narrowed_boundary.get("archive_effect_by_id")
        == gap_objective_boundary.get("archive_effect_by_id")
        == expected_archive_effect_by_id
    ):
        errors.append("archive effect map not carried into narrowed archive boundary")
    if not (
        narrowed_boundary.get("closure_allowed_by_id")
        == gap_objective_boundary.get("closure_allowed_by_id")
        == {"OC4": False, "OC6": False, "OC12": False}
    ):
        errors.append("closure-allowed map overpermits narrowed archive promotion")
    if not (
        narrowed_boundary.get("source_policy_closed_ratio")
        == objective_completion.get("source_policy_closed_ratio")
        == archive_gap.get("source_policy_closed_ratio")
        == "0/40"
    ):
        errors.append("source-policy closed ratio not carried into narrowed archive boundary")
    if not (
        narrowed_boundary.get("narrowed_claim_reproducibility_package_ready") is True
        and narrowed_boundary.get("full_source_policy_runner_package_ready") is False
        and narrowed_boundary.get("current_archive_usable_as_full_source_policy_runner_archive")
        is False
        and narrowed_boundary.get("source_policy_execution_allowed_now") is False
        and narrowed_boundary.get("source_policy_execution_invoked") is False
        and narrowed_boundary.get("exact_b4_opt_in_required_for_execution") is True
        and narrowed_boundary.get("required_user_approval_statement")
        == EXPECTED_APPROVAL_STATEMENT
        and narrowed_boundary.get("guarded_execution_driver") == EXPECTED_GUARDED_DRIVER
    ):
        errors.append("narrowed archive promotion/execution boundary changed")
    if not (
        narrowed_boundary.get("safe_action_ids")
        == gap_objective_boundary.get("safe_action_ids")
        == EXPECTED_SAFE_ACTION_IDS
        and narrowed_boundary.get("opt_in_action_ids")
        == gap_objective_boundary.get("opt_in_action_ids")
        == EXPECTED_OPT_IN_ACTION_IDS
    ):
        errors.append("narrowed archive action ids changed")
    if narrowed_boundary.get("source_artifacts") != expected_source_artifacts:
        errors.append("narrowed archive source artifact list changed")
    handoff = manifest.get("source_policy_execution_handoff", {})
    if not (
        handoff.get("status")
        == b4_handoff.get("status")
        == "source_policy_execution_handoff_ready_not_authorized_not_run"
    ):
        errors.append("source-policy handoff status not carried into archive manifest")
    if not (
        handoff.get("execution_authorized") == b4_handoff.get("execution_authorized") is False
        and handoff.get("commands_not_run_by_handoff")
        == b4_handoff.get("commands_not_run_by_handoff")
        is True
    ):
        errors.append("source-policy handoff authorization boundary changed in archive manifest")
    if (
        handoff.get("exact_required_user_approval_statement")
        != b4_handoff.get("approval_boundary", {}).get("exact_required_user_approval_statement")
        or handoff.get("exact_required_user_approval_statement") != EXPECTED_APPROVAL_STATEMENT
    ):
        errors.append("source-policy handoff exact approval not carried into archive manifest")
    b4_driver = b4_handoff.get("approval_boundary", {}).get("guarded_execution_driver", {})
    if not (
        handoff.get("guarded_execution_driver")
        == b4_driver.get("path")
        == EXPECTED_GUARDED_DRIVER
        and handoff.get("driver_requires_exact_approval")
        == b4_driver.get("requires_exact_approval_argument")
        is True
        and handoff.get("driver_does_not_authorize_execution")
        == b4_driver.get("driver_does_not_authorize_execution")
        is True
    ):
        errors.append("source-policy handoff guarded driver boundary changed in archive manifest")
    if not (
        handoff.get("opt_in_required_command_count")
        == b4_handoff.get("opt_in_required_actions", {}).get("command_count")
        == 13
        and handoff.get("opt_in_required_mapped_external_rows")
        == b4_handoff.get("opt_in_required_actions", {}).get("mapped_external_rows")
        == 20
        and handoff.get("terminal_unable_to_reproduce_rows")
        == b4_handoff.get("source_policy_row_state", {}).get("unable_to_reproduce")
        == 20
    ):
        errors.append("source-policy handoff opt-in/terminal counts changed in archive manifest")
    if handoff.get("boundary_artifacts") != [
        "B4_SOURCE_POLICY_EXECUTION_HANDOFF_PACKAGE.json",
        "B4_SOURCE_POLICY_EXECUTION_HANDOFF_PACKAGE.md",
    ]:
        errors.append("source-policy handoff boundary artifact list changed")
    if manifest.get("full_source_policy_runner_package_ready") is not False:
        errors.append("full source-policy runner package overclaimed")
    if manifest.get("submission_ready") is not False:
        errors.append("submission readiness overclaimed")
    if manifest.get("run_v047_invoked") is not False or manifest.get("run_v048_invoked") is not False:
        errors.append("archive manifest overclaims forbidden run invocation")
    if manifest.get("required_entries") != EXPECTED_REQUIRED:
        errors.append("required-entry list changed")

    if not errors:
        with ZipFile(ARCHIVE) as archive:
            names = archive.namelist()
            name_set = set(names)
            if any("__pycache__" in name or name.endswith((".pyc", ".pyo")) for name in names):
                errors.append("archive contains bytecode or pycache entries")
            if len(names) != manifest.get("entry_count"):
                errors.append("archive entry count stale")
            for item in EXPECTED_REQUIRED:
                if item not in name_set:
                    errors.append(f"required entry missing: {item}")
            internal = manifest.get("internal_manifest", {})
            internal_path = internal.get("path")
            if internal_path not in name_set:
                errors.append("internal manifest missing from archive")
            else:
                internal_bytes = archive.read(str(internal_path))
                if len(internal_bytes) != internal.get("bytes"):
                    errors.append("internal manifest byte count stale")
                if hashlib.sha256(internal_bytes).hexdigest() != internal.get("sha256"):
                    errors.append("internal manifest sha256 stale")
                internal_manifest = json.loads(internal_bytes.decode("utf-8"))
                if internal_manifest.get("status") != manifest.get("status"):
                    errors.append("internal manifest status mismatch")
                if internal_manifest.get("entrypoint") != manifest.get("entrypoint"):
                    errors.append("internal manifest entrypoint mismatch")
                if internal_manifest.get("source_policy_execution_handoff") != handoff:
                    errors.append("internal manifest source-policy handoff mismatch")
                internal_action_boundary_aliases = {
                    key: internal_manifest.get(key) for key in EXPECTED_ACTION_BOUNDARY_ALIASES
                }
                if internal_action_boundary_aliases != EXPECTED_ACTION_BOUNDARY_ALIASES:
                    errors.append("internal manifest top-level source-policy action boundary mismatch")
                if internal_manifest.get("narrowed_archive_boundary") != narrowed_boundary:
                    errors.append("internal manifest narrowed archive boundary mismatch")

            for item in handoff.get("boundary_artifacts", []):
                if item not in name_set:
                    errors.append(f"source-policy handoff boundary artifact missing: {item}")
            for item in narrowed_boundary.get("source_artifacts", []):
                if item not in name_set:
                    errors.append(f"narrowed archive source artifact missing: {item}")

            manifest_entries = {item.get("path"): item for item in manifest.get("entries", [])}
            for item in expected_source_artifacts:
                if item not in manifest_entries:
                    errors.append(f"narrowed archive source artifact missing from manifest entries: {item}")
            for path, item in manifest_entries.items():
                if path not in name_set:
                    errors.append(f"manifest entry missing in archive: {path}")
                    continue
                data = archive.read(str(path))
                if len(data) != item.get("bytes"):
                    errors.append(f"entry byte count stale: {path}")
                if hashlib.sha256(data).hexdigest() != item.get("sha256"):
                    errors.append(f"entry sha256 stale: {path}")

            if not errors:
                with tempfile.TemporaryDirectory(prefix="cmame_narrowed_repro_archive_") as tmp:
                    root = Path(tmp)
                    archive.extractall(root)
                    proc = subprocess.run(
                        [
                            sys.executable,
                            "cmame_narrowed_repro_bundle/scripts/run_narrowed_repro_bundle.py",
                        ],
                        cwd=root,
                        text=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                    )
                    if proc.returncode != 0:
                        errors.append(f"extracted archive runner failed with code {proc.returncode}")
                        errors.append(proc.stdout)
                    for token in [
                        "cmame_narrowed_repro_bundle=PASS",
                        "narrowed_claim_reproducibility_package_ready=True",
                        "source_policy_external_rows=0/40",
                        "source_policy_handoff_status=source_policy_execution_handoff_ready_not_authorized_not_run",
                        "source_policy_handoff_authorized=False",
                        "source_policy_handoff_driver=run_b4_source_policy_after_opt_in.sh",
                        "source_policy_handoff_opt_in=13/20",
                        "source_policy_execution_allowed_now=False",
                        "source_policy_execution_invoked=False",
                        "exact_b4_opt_in_required_for_execution=True",
                        "full_source_policy_runner_package_ready=False",
                        "submission_ready=False",
                    ]:
                        if token not in proc.stdout:
                            errors.append(f"extracted archive runner missing token: {token}")

    for token in [
        "Status: **narrowed_repro_code_archive_ready_source_policy_open**.",
        "Narrowed package ready: `True`.",
        "Source-policy rows closed: `0/40`.",
        "Source-policy execution allowed now/invoked/exact opt-in required: `False/False/True`.",
        "Source-policy safe/opt-in action ids: `['rebuild_read_only_audit_chain', 'rerun_read_only_validators', 'keep_narrowed_archive_provenance_only', 'monitor_reopen_conditions']/['authorized_b4_ra_hi_source_policy_execution']`.",
        "Source-policy required approval/driver: `I explicitly approve running the B4 source-policy execution commands listed in B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json./run_b4_source_policy_after_opt_in.sh`.",
        "Source-policy execution handoff exact approval/driver: `I explicitly approve running the B4 source-policy execution commands listed in B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json./run_b4_source_policy_after_opt_in.sh/True/True/13/20`.",
        "Source-policy execution handoff authorized/commands-not-run/terminal-unable: `False/True/20`.",
        "Narrowed archive boundary/status/scope: `narrowed_archive_ready_not_full_source_policy_runner_archive/narrowed_claim_only`.",
        "Narrowed archive objective blockers: `['OC4', 'OC6', 'OC12']`.",
        "Narrowed archive blocker status by id: `{'OC4': 'open', 'OC6': 'partial', 'OC12': 'partial'}`.",
        "Narrowed archive blocker next actions by id: `{'OC4': 'RA/HI can only close through exact B4 opt-in authorized closeout or a new source-policy promotion artifact; TFE/VP remain unable-to-reproduce/not-promoted'",
        "Narrowed archive blocker required-to-close by id:",
        "Narrowed archive blocker safe next actions by id:",
        "Narrowed archive blocker opt-in required actions by id:",
        "Narrowed archive blocker effects by id: `{'OC4': 'blocks_full_archive_primary_use', 'OC6': 'blocks_tfe_rows_from_full_archive_promotion', 'OC12': 'current_archive_is_narrowed_claim_provenance_only'}`.",
        "Narrowed archive current/full-source/use/execution/exact: `True/False/False/False/True`.",
        "Narrowed archive safe/opt-in action ids: `['rebuild_read_only_audit_chain', 'rerun_read_only_validators', 'keep_narrowed_archive_provenance_only', 'monitor_reopen_conditions']/['authorized_b4_ra_hi_source_policy_execution']`.",
        "## Objective Blocker Matrix",
        "This manifest records the reviewer-facing narrowed archive boundary. It does not close the global objective blockers.",
        f"`{EXPECTED_BLOCKER_OPEN_TOKEN}`",
        f"`{EXPECTED_BLOCKER_CLOSURE_DECISION_TOKEN}`",
        f"`{EXPECTED_BLOCKER_CLOSURE_ALLOWED_TOKEN}`",
        "Full source-policy runner package ready: `False`.",
        "Submission ready: `False`.",
        "not a full source-policy runner archive",
    ]:
        if token not in manifest_md:
            errors.append(f"manifest markdown missing token: {token}")

    if errors:
        print("CMAME narrowed repro code archive validation: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print("CMAME narrowed repro code archive validation: PASS")
    print(f"archive={ARCHIVE.name}")
    print(f"entries={manifest.get('entry_count')}")
    print(
        "python_files_lines="
        f"{manifest.get('python_file_count')}/{manifest.get('python_line_count')}"
    )
    print("source_policy_external_rows=0/40")
    print("full_source_policy_runner_package_ready=False")
    print(EXPECTED_BLOCKER_OPEN_TOKEN)
    print(EXPECTED_BLOCKER_CLOSURE_DECISION_TOKEN)
    print(EXPECTED_BLOCKER_CLOSURE_ALLOWED_TOKEN)
    print("submission_ready=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
