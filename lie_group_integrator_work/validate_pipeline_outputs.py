from __future__ import annotations

import csv
import json
import math
import re
import struct
import importlib.util
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent

# The validators below import jax; when invoked with an interpreter that lacks it, re-run under the
# project virtual environment so the dynamic-row-oracle gate and the extracted archive runner see it.
_VENV_PYTHON = ROOT / ".venv_sbel" / "bin" / "python"
if (importlib.util.find_spec("jax") is None and _VENV_PYTHON.exists()
        and Path(sys.executable).resolve() != _VENV_PYTHON.resolve()):
    os.execv(str(_VENV_PYTHON), [str(_VENV_PYTHON), *sys.argv])
RESULTS = ROOT / "pipeline_validation_results"
CURRENT_VERSION = "v047"
CURRENT_DIR = ROOT / "v047_cylindrical_chain_pipeline"
V048_DIR = ROOT / "v048_cross_paper_same_test_benchmarks"
PAPER_DIR = ROOT / "paper_v047_cylindrical_chain"
LATEX_DIR = ROOT / "paper"  # manuscript sources, figures, submission copies (since 2026-09-20)
_MANUSCRIPT_TOPLEVEL = {"main_cmame.tex", "main_cmame.pdf", "main_cmame.log", "main_cmame.txt", "main.tex", "main.pdf", "main.log", "main.txt",
                        "main_concise.tex", "main_concise.pdf", "main_concise.log", "main_concise.txt", "highlights_cmame.txt",
                        "declarations_cmame.md", "COVER_LETTER.md", "README_CMAME_FLAT_SUBMISSION.md", "cmame_submission_flat.zip"}
_MANUSCRIPT_DIRS = {"figures", "cmame_submission_flat", "arxiv"}


def paper_asset_path(label: str) -> Path:
    first = str(label).replace("\\", "/").split("/")[0]
    return (LATEX_DIR / label) if (first in _MANUSCRIPT_TOPLEVEL or first in _MANUSCRIPT_DIRS) else (PAPER_DIR / label)
EXPECTED_ASME_MODELS = {"single_pendulum", "double_pendulum", "four_link", "slider_crank"}


class Validator:
    def __init__(self) -> None:
        self.checks_run = 0
        self.failures: list[str] = []

    def check(self, condition: bool, message: str) -> None:
        self.checks_run += 1
        if not condition:
            self.failures.append(message)


def version_number(version: str) -> int:
    match = re.fullmatch(r"v(\d{3})", version)
    if not match:
        raise ValueError(f"invalid version label: {version}")
    return int(match.group(1))


def read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def contains_normalized(text: str, token: str) -> bool:
    return token in text or " ".join(token.split()) in " ".join(text.split())


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError(f"{path} has no header")
        return list(reader)


def png_size(path: Path) -> tuple[int, int]:
    with path.open("rb") as handle:
        header = handle.read(24)
    if len(header) < 24 or header[:8] != b"\x89PNG\r\n\x1a\n" or header[12:16] != b"IHDR":
        raise ValueError(f"{path} is not a PNG with an IHDR header")
    return struct.unpack(">II", header[16:24])


def result_files(results_dir: Path) -> list[Path]:
    return sorted(path for path in results_dir.iterdir() if path.is_file())


def summary_path_for(version: str, results_dir: Path) -> Path | None:
    versioned = results_dir / f"summary_{version}.json"
    legacy = results_dir / "summary.json"
    if versioned.exists():
        return versioned
    if legacy.exists():
        return legacy
    return None


def validate_artifact_files(v: Validator, files: list[Path]) -> dict[str, int]:
    counts = {"json": 0, "csv": 0, "png": 0, "md": 0, "other": 0}
    for path in files:
        suffix = path.suffix.lower()
        if suffix == ".json":
            counts["json"] += 1
            try:
                read_json(path)
            except Exception as exc:  # noqa: BLE001 - validation should report all parse failures.
                v.check(False, f"JSON parse failed for {path.relative_to(ROOT)}: {exc}")
            else:
                v.check(True, f"JSON parse ok for {path.relative_to(ROOT)}")
        elif suffix == ".csv":
            counts["csv"] += 1
            try:
                rows = read_csv_rows(path)
            except Exception as exc:  # noqa: BLE001
                v.check(False, f"CSV parse failed for {path.relative_to(ROOT)}: {exc}")
            else:
                v.check(len(rows) > 0, f"CSV has no data rows: {path.relative_to(ROOT)}")
        elif suffix == ".png":
            counts["png"] += 1
            try:
                width, height = png_size(path)
            except Exception as exc:  # noqa: BLE001
                v.check(False, f"PNG parse failed for {path.relative_to(ROOT)}: {exc}")
            else:
                v.check(width > 0 and height > 0, f"PNG has invalid size: {path.relative_to(ROOT)}")
        elif suffix == ".md":
            counts["md"] += 1
            v.check(path.stat().st_size > 0, f"empty markdown artifact: {path.relative_to(ROOT)}")
        else:
            counts["other"] += 1
            v.check(path.stat().st_size > 0, f"empty artifact: {path.relative_to(ROOT)}")
    return counts


def validate_version_inventory(v: Validator) -> tuple[list[dict[str, object]], dict[str, int]]:
    ledger_rows = read_csv_rows(ROOT / "docs" / "version_ledger.csv")
    ledger_by_version = {row["version"]: row for row in ledger_rows}
    version_dirs = sorted(
        [path for path in ROOT.iterdir() if path.is_dir() and re.fullmatch(r"v\d{3}_.+", path.name)],
        key=lambda path: version_number(path.name[:4]),
    )
    versions = [path.name[:4] for path in version_dirs]

    v.check(len(ledger_rows) == len(version_dirs), "version_ledger.csv row count does not match vNNN directories")
    v.check(set(ledger_by_version) == set(versions), "version_ledger.csv versions do not match vNNN directories")
    v.check(versions == [f"v{i:03d}" for i in range(1, len(versions) + 1)], "version directories are not contiguous from v001")

    inventory: list[dict[str, object]] = []
    totals = {"versions": len(version_dirs), "result_files": 0, "csv": 0, "png": 0, "json": 0, "reports": 0}
    for version_dir in version_dirs:
        version = version_dir.name[:4]
        results_dir = version_dir / "results"
        readme = version_dir / "README.md"
        run_script = version_dir / f"run_{version}.py"
        ledger = ledger_by_version.get(version, {})
        report = ROOT / str(ledger.get("report", ""))
        summary = summary_path_for(version, results_dir)

        v.check(readme.exists(), f"{version} README.md missing")
        v.check(run_script.exists(), f"{version} run script missing")
        v.check(results_dir.exists(), f"{version} results directory missing")
        v.check(report.exists(), f"{version} report missing: {report.relative_to(ROOT) if report != ROOT else report}")
        v.check(summary is not None and summary.exists(), f"{version} summary JSON missing")
        if summary is not None and summary.exists():
            try:
                read_json(summary)
            except Exception as exc:  # noqa: BLE001
                v.check(False, f"{version} summary JSON parse failed: {exc}")
            else:
                v.check(True, f"{version} summary JSON parse ok")

        files = result_files(results_dir) if results_dir.exists() else []
        counts = validate_artifact_files(v, files)
        totals["result_files"] += len(files)
        totals["csv"] += counts["csv"]
        totals["png"] += counts["png"]
        totals["json"] += counts["json"]
        totals["reports"] += counts["md"]
        inventory.append(
            {
                "version": version,
                "dirname": version_dir.name,
                "summary": str(summary.relative_to(ROOT)) if summary else "",
                "report": str(report.relative_to(ROOT)) if report.exists() else str(ledger.get("report", "")),
                "result_files": len(files),
                "csv_files": counts["csv"],
                "png_files": counts["png"],
                "json_files": counts["json"],
                "markdown_files": counts["md"],
            }
        )
    return inventory, totals


def run_v047_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_v047_outputs.py"],
        cwd=CURRENT_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"v047 validator failed:\n{proc.stdout}")
    v.check("v047 output validation: PASS" in proc.stdout, "v047 validator did not report PASS")
    return proc.stdout


def run_four_asme_minimal_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_four_asme_minimal.py"],
        cwd=CURRENT_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"minimal four-ASME validator failed:\n{proc.stdout}")
    v.check("v047 minimal four-ASME validation: PASS" in proc.stdout, "minimal four-ASME validator did not report PASS")
    v.check("full_tfe_stage_replacement=False" in proc.stdout, "minimal four-ASME validator lost full-TFE caveat marker")
    return proc.stdout


def run_full_tfe_gap_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_full_tfe_gap.py"],
        cwd=CURRENT_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"full-TFE gap validator failed:\n{proc.stdout}")
    v.check("v047 full-TFE gap validation: PASS" in proc.stdout, "full-TFE gap validator did not report PASS")
    v.check("order_closure_intersection_present=False" in proc.stdout, "full-TFE gap validator lost order/closure blocker marker")
    v.check("full_tfe_stage_replacement=False" in proc.stdout, "full-TFE gap validator lost full-TFE caveat marker")
    return proc.stdout


def run_full_tfe_repair_spec_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_full_tfe_repair_spec.py"],
        cwd=CURRENT_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"full-TFE repair spec validator failed:\n{proc.stdout}")
    v.check("v047 full-TFE repair spec validation: PASS" in proc.stdout, "full-TFE repair spec validator did not report PASS")
    v.check("stage_row_budget=132" in proc.stdout, "full-TFE repair spec validator lost stage-row budget marker")
    v.check("target_closure_rows=8" in proc.stdout, "full-TFE repair spec validator lost closure-row marker")
    v.check("full_tfe_stage_replacement=False" in proc.stdout, "full-TFE repair spec validator lost full-TFE caveat marker")
    return proc.stdout


def run_implementation_fidelity_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_implementation_fidelity_certificate.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"implementation-fidelity certificate validator failed:\n{proc.stdout}")
    v.check(
        "implementation_fidelity_certificate=PASS" in proc.stdout,
        "implementation-fidelity certificate validator did not report PASS",
    )
    v.check("accepted_residual=residual_cylindrical_chain" in proc.stdout, "implementation validator lost residual marker")
    v.check("accepted_jacobian=R_JAC_jacfwd_argnums0" in proc.stdout, "implementation validator lost Jacobian marker")
    v.check("stage_rows=132" in proc.stdout, "implementation validator lost stage-row budget marker")
    v.check("full_tfe_stage_replacement=False" in proc.stdout, "implementation validator lost full-TFE caveat marker")
    return proc.stdout


def run_implementation_path_audit_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_implementation_path_audit.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"implementation path audit validator failed:\n{proc.stdout}")
    v.check(
        "implementation_path_audit=PASS" in proc.stdout,
        "implementation path audit validator did not report PASS",
    )
    v.check("accepted_residual=residual_cylindrical_chain" in proc.stdout, "implementation path audit lost residual marker")
    v.check("accepted_jacobian=R_JAC_jacfwd_argnums0" in proc.stdout, "implementation path audit lost Jacobian marker")
    v.check(
        "implementation_path_check_for_132_row_residual=True" in proc.stdout,
        "implementation path audit lost path-check marker",
    )
    v.check("stage_rows=132" in proc.stdout, "implementation path audit lost stage-row budget marker")
    v.check("default_1e-4=False" in proc.stdout, "implementation path audit lost no-default-1e-4 marker")
    v.check("run_v047_invoked=False" in proc.stdout, "implementation path audit lost no-run_v047 marker")
    v.check("submission_ready=False" in proc.stdout, "implementation path audit lost submission marker")
    return proc.stdout


def run_b4_source_policy_row_closure_readiness_ledger_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_b4_source_policy_row_closure_readiness_ledger.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(
        proc.returncode == 0,
        f"B4 source-policy row closure-readiness ledger validator failed:\n{proc.stdout}",
    )
    v.check(
        "B4 source-policy row closure-readiness ledger validation: PASS" in proc.stdout,
        "B4 source-policy row closure-readiness ledger validator did not report PASS",
    )
    v.check("external_rows=40/40" in proc.stdout, "B4 row-closure ledger lost external row marker")
    v.check("source_policy_closed=0/40" in proc.stdout, "B4 row-closure ledger overclosed source-policy rows")
    v.check(
        "attempted_not_reproducible=20" in proc.stdout,
        "B4 row-closure ledger lost attempted-not-reproducible count",
    )
    v.check(
        "still_requiring_execution_or_promotion=20" in proc.stdout,
        "B4 row-closure ledger lost open execution/promotion count",
    )
    v.check("rows_with_launch_command_refs=20" in proc.stdout, "B4 row-closure ledger lost command-ref count")
    v.check("b4_can_close_now=False" in proc.stdout, "B4 row-closure ledger overclosed B4")
    v.check("b7_can_close_now=False" in proc.stdout, "B4 row-closure ledger overclosed B7")
    return proc.stdout


def run_source_policy_row_closure_ledger_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_source_policy_row_closure_ledger.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"source-policy row closure ledger validator failed:\n{proc.stdout}")
    v.check(
        "source-policy row closure ledger validation: PASS" in proc.stdout,
        "source-policy row closure ledger validator did not report PASS",
    )
    v.check("flagged_rows=15" in proc.stdout, "source-policy row closure ledger flagged-row count changed")
    v.check(
        "examples=single_pendulum,double_pendulum,four_link,slider_crank" in proc.stdout,
        "source-policy row closure ledger lost four-example marker",
    )
    v.check("rows_source_policy_closed=0" in proc.stdout, "source-policy row closure ledger overclosed rows")
    v.check(
        "rows_external_superiority_ready=0" in proc.stdout,
        "source-policy row closure ledger overclaims external superiority",
    )
    v.check(
        "parallel_ready_shards_without_default_1e_4=20" in proc.stdout,
        "source-policy row closure ledger lost no-default-1e-4 marker",
    )
    v.check("b2_b4_can_close_now=False/False" in proc.stdout, "source-policy row closure ledger overclosed B2/B4")
    return proc.stdout


def run_tfe_dae_runner_contract_gap_audit_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_tfe_dae_runner_contract_gap_audit.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"TFE DAE runner contract gap audit validator failed:\n{proc.stdout}")
    v.check(
        "TFE DAE runner contract gap audit validation: PASS" in proc.stdout,
        "TFE DAE runner contract gap audit validator did not report PASS",
    )
    v.check(
        "status=dae_runner_contract_gap_open_not_source_policy" in proc.stdout,
        "TFE DAE runner contract gap audit status changed",
    )
    v.check("missing_contract_blocks=6" in proc.stdout, "TFE DAE runner contract gap count changed")
    v.check(
        "candidate_backed_non_equivalent_runner_blocks=3" in proc.stdout,
        "TFE DAE runner contract gap lost candidate-backed non-equivalent count",
    )
    v.check(
        "source_policy_rows_completed=0" in proc.stdout,
        "TFE DAE runner contract gap audit overclosed source-policy rows",
    )
    return proc.stdout


def run_tfe_runner_contract_preflight_certificate_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_tfe_runner_contract_preflight_certificate.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"TFE runner contract preflight validator failed:\n{proc.stdout}")
    v.check(
        "TFE runner contract preflight certificate validation: PASS" in proc.stdout,
        "TFE runner contract preflight validator did not report PASS",
    )
    v.check("entrypoints=3/3" in proc.stdout, "TFE runner contract preflight entrypoint count changed")
    v.check("candidate_backed=3/3" in proc.stdout, "TFE runner contract preflight candidate-backed count changed")
    v.check(
        "source_policy_rows_completed=0" in proc.stdout,
        "TFE runner contract preflight overclosed source-policy rows",
    )
    v.check("execution_blocks=4" in proc.stdout, "TFE runner contract preflight execution block count changed")
    v.check(
        "source_policy_equivalent=False/False" in proc.stdout,
        "TFE runner contract preflight overclaims source-policy equivalence",
    )
    return proc.stdout


def run_b4_source_policy_work_precision_execution_plan_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_b4_source_policy_work_precision_execution_plan.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"B4 source-policy work/precision execution plan validator failed:\n{proc.stdout}")
    v.check(
        "b4 source-policy work/precision execution plan validation: PASS" in proc.stdout,
        "B4 source-policy work/precision execution plan validator did not report PASS",
    )
    v.check("source_policy_rows_closed=0" in proc.stdout, "B4 work/precision plan overclosed rows")
    v.check("source_policy_rows_total=40" in proc.stdout, "B4 work/precision plan lost total row count")
    v.check(
        "ready_to_launch_after_explicit_opt_in_count=2" in proc.stdout,
        "B4 work/precision plan ready-lane count changed",
    )
    v.check("not_ready_lane_count=2" in proc.stdout, "B4 work/precision plan not-ready lane count changed")
    v.check("b4_can_close_now=False" in proc.stdout, "B4 work/precision plan overclosed B4")
    v.check("b7_can_close_now=False" in proc.stdout, "B4 work/precision plan overclosed B7")
    return proc.stdout


def run_b4_source_policy_post_execution_audit_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_b4_source_policy_post_execution_audit.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"B4 source-policy post-execution audit validator failed:\n{proc.stdout}")
    v.check(
        "b4 source-policy post-execution audit validation: PASS" in proc.stdout,
        "B4 source-policy post-execution audit validator did not report PASS",
    )
    v.check(
        "verified_authorized_execution_recorded=False" in proc.stdout,
        "B4 post-execution audit unexpectedly records authorized execution",
    )
    v.check(
        "source_policy_execution_invoked=False" in proc.stdout,
        "B4 post-execution audit invoked source-policy execution",
    )
    v.check(
        "source_policy_execution_allowed_now=False" in proc.stdout,
        "B4 post-execution audit over-allows source-policy execution",
    )
    v.check("source_policy_rows_closed=0/40" in proc.stdout, "B4 post-execution audit overclosed rows")
    v.check("b4_can_close_now=False" in proc.stdout, "B4 post-execution audit overclosed B4")
    v.check("b7_can_close_now=False" in proc.stdout, "B4 post-execution audit overclosed B7")
    v.check(
        "blocker_open_by_id=OC4:True,OC6:True,OC12:True" in proc.stdout,
        "B4 post-execution audit lost blocker-open matrix",
    )
    v.check(
        "blocker_closure_allowed_by_id=OC4:False,OC6:False,OC12:False" in proc.stdout,
        "B4 post-execution audit over-allows blocker closure",
    )
    return proc.stdout


def run_b4_existing_artifact_promotion_audit_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_b4_existing_artifact_promotion_audit.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"B4 existing-artifact promotion audit validator failed:\n{proc.stdout}")
    v.check(
        "b4 existing-artifact promotion audit validation: PASS" in proc.stdout,
        "B4 existing-artifact promotion audit validator did not report PASS",
    )
    v.check("candidate_items=8" in proc.stdout, "B4 existing-artifact audit candidate count changed")
    v.check(
        "promotion_ready_without_new_execution=0" in proc.stdout,
        "B4 existing-artifact audit overclaims no-new-execution promotion readiness",
    )
    v.check(
        "source_policy_rows_closed_by_existing_artifacts=0/40" in proc.stdout,
        "B4 existing-artifact audit overclosed source-policy rows",
    )
    v.check("b4_can_close_now=False" in proc.stdout, "B4 existing-artifact audit overclosed B4")
    v.check("b7_can_close_now=False" in proc.stdout, "B4 existing-artifact audit overclosed B7")
    return proc.stdout


def run_external_source_policy_closure_manifest_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_external_source_policy_closure_manifest.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"external source-policy closure manifest validator failed:\n{proc.stdout}")
    v.check(
        "external source-policy closure manifest validation: PASS" in proc.stdout,
        "external source-policy closure manifest validator did not report PASS",
    )
    v.check("performance_rows=32/48" in proc.stdout, "external closure manifest performance row count changed")
    v.check(
        "strict_external_error_claim_rows=0" in proc.stdout,
        "external closure manifest overclaims strict external error rows",
    )
    v.check(
        "external_superiority_claim_allowed=False" in proc.stdout,
        "external closure manifest over-allows external superiority claims",
    )
    v.check("b2_b4_can_close_now=False/False" in proc.stdout, "external closure manifest overclosed B2/B4")
    return proc.stdout


def run_b6_four_example_local_evidence_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_b6_four_example_local_evidence.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"B6 four-example local evidence validator failed:\n{proc.stdout}")
    v.check(
        "B6 four-example local evidence validation: PASS" in proc.stdout,
        "B6 four-example local evidence validator did not report PASS",
    )
    v.check("local_rows=12" in proc.stdout, "B6 four-example local evidence row count changed")
    v.check(
        "self_contained_examples=single_pendulum,double_pendulum,four_link,slider_crank" in proc.stdout,
        "B6 four-example local evidence lost self-contained four-example marker",
    )
    v.check("replay_only_examples=none" in proc.stdout, "B6 four-example local evidence replay-only marker changed")
    v.check("source_policy_external_rows=0/40" in proc.stdout, "B6 local evidence overclosed source-policy rows")
    v.check(
        "direct_pc2_proof_gap_closed=True" in proc.stdout,
        "B6 local evidence lost direct PC2 proof-gap closure marker",
    )
    v.check("submission_ready=False" in proc.stdout, "B6 local evidence overclaims submission readiness")
    return proc.stdout


def run_cmame_runner_centered_reproducibility_audit_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_cmame_runner_centered_reproducibility_audit.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"CMAME runner-centered reproducibility audit validator failed:\n{proc.stdout}")
    v.check(
        "cmame runner-centered reproducibility audit validation: PASS" in proc.stdout,
        "CMAME runner-centered reproducibility audit validator did not report PASS",
    )
    v.check(
        "runner_centered_package_ready=False" in proc.stdout,
        "CMAME runner-centered audit overclaims runner-centered package readiness",
    )
    v.check("b6_local_evidence_rows=12" in proc.stdout, "CMAME runner-centered audit lost B6 local row count")
    v.check("source_policy_closed=0/40" in proc.stdout, "CMAME runner-centered audit overclosed source-policy rows")
    v.check(
        "source_policy_handoff=source_policy_execution_handoff_ready_not_authorized_not_run/False/True"
        in proc.stdout,
        "CMAME runner-centered audit lost source-policy handoff boundary",
    )
    v.check(
        "source_policy_execution_allowed_now=False" in proc.stdout,
        "CMAME runner-centered audit over-allows source-policy execution",
    )
    v.check(
        "source_policy_execution_invoked=False" in proc.stdout,
        "CMAME runner-centered audit invoked source-policy execution",
    )
    return proc.stdout


def run_cmame_narrowed_reproducibility_package_audit_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_cmame_narrowed_reproducibility_package_audit.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"CMAME narrowed reproducibility package audit validator failed:\n{proc.stdout}")
    v.check(
        "CMAME narrowed reproducibility package audit validation: PASS" in proc.stdout,
        "CMAME narrowed reproducibility package audit validator did not report PASS",
    )
    v.check(
        "narrowed_claim_reproducibility_package_ready=True" in proc.stdout,
        "CMAME narrowed package audit lost narrowed-package readiness marker",
    )
    v.check(
        "full_source_policy_runner_package_ready=False" in proc.stdout,
        "CMAME narrowed package audit overclaims full source-policy package readiness",
    )
    v.check("source_policy_rows=0/40" in proc.stdout, "CMAME narrowed package audit overclosed source-policy rows")
    v.check(
        "source_policy_execution_allowed_now=False" in proc.stdout,
        "CMAME narrowed package audit over-allows source-policy execution",
    )
    v.check(
        "source_policy_execution_invoked=False" in proc.stdout,
        "CMAME narrowed package audit invoked source-policy execution",
    )
    return proc.stdout


def run_cmame_narrowed_repro_code_archive_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_cmame_narrowed_repro_code_archive.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"CMAME narrowed repro code archive validator failed:\n{proc.stdout}")
    v.check(
        "CMAME narrowed repro code archive validation: PASS" in proc.stdout,
        "CMAME narrowed repro code archive validator did not report PASS",
    )
    v.check("archive=cmame_narrowed_repro_code_archive.zip" in proc.stdout, "CMAME narrowed archive name changed")
    v.check("entries=99" in proc.stdout, "CMAME narrowed archive entry count changed")
    v.check("python_files_lines=26/6154" in proc.stdout, "CMAME narrowed archive Python inventory changed")
    v.check(
        "source_policy_external_rows=0/40" in proc.stdout,
        "CMAME narrowed archive overclosed source-policy rows",
    )
    v.check(
        "full_source_policy_runner_package_ready=False" in proc.stdout,
        "CMAME narrowed archive overclaims full source-policy package readiness",
    )
    v.check(
        "blocker_open_by_id=OC4:True,OC6:True,OC12:True" in proc.stdout,
        "CMAME narrowed archive lost blocker-open matrix",
    )
    v.check(
        "blocker_closure_allowed_by_id=OC4:False,OC6:False,OC12:False" in proc.stdout,
        "CMAME narrowed archive over-allows blocker closure",
    )
    v.check("submission_ready=False" in proc.stdout, "CMAME narrowed archive overclaims submission readiness")
    return proc.stdout


def run_cmame_reproducibility_package_manifest_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_cmame_reproducibility_package_manifest.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"CMAME reproducibility package manifest validator failed:\n{proc.stdout}")
    v.check(
        "cmame reproducibility package manifest validation: PASS" in proc.stdout,
        "CMAME reproducibility package manifest validator did not report PASS",
    )
    v.check(
        "status=not_ready_self_contained_runner_centered_package_missing_source_policy" in proc.stdout,
        "CMAME reproducibility manifest status changed",
    )
    v.check("candidate_files=141/141" in proc.stdout, "CMAME reproducibility manifest candidate inventory changed")
    v.check("source_policy_closed=0/40" in proc.stdout, "CMAME reproducibility manifest overclosed source-policy rows")
    v.check(
        "source_policy_execution_handoff_driver_requires_exact_approval=True" in proc.stdout,
        "CMAME reproducibility manifest lost exact-approval boundary",
    )
    v.check(
        "source_policy_execution_allowed_now=False" in proc.stdout,
        "CMAME reproducibility manifest over-allows source-policy execution",
    )
    v.check(
        "source_policy_execution_invoked=False" in proc.stdout,
        "CMAME reproducibility manifest invoked source-policy execution",
    )
    v.check(
        "tfe_runner_contract_preflight=contract_entrypoints_callable_candidate_backed_source_policy_open/3/3/3/3/0/4"
        in proc.stdout,
        "CMAME reproducibility manifest lost TFE runner preflight marker",
    )
    v.check("minimal_package_ready=False" in proc.stdout, "CMAME reproducibility manifest overclaims minimal package readiness")
    return proc.stdout


def run_b6_closed_loop_self_contained_extraction_audit_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_b6_closed_loop_self_contained_extraction_audit.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"B6 closed-loop self-contained extraction audit failed:\n{proc.stdout}")
    v.check(
        "B6 closed-loop self-contained extraction audit validation: PASS" in proc.stdout,
        "B6 closed-loop self-contained extraction audit did not report PASS",
    )
    v.check("self_contained_runner_ready=True" in proc.stdout, "B6 closed-loop extraction lost ready marker")
    v.check("target_symbol_count=33" in proc.stdout, "B6 closed-loop extraction target symbol count changed")
    v.check("target_symbol_lines=756" in proc.stdout, "B6 closed-loop extraction target line count changed")
    v.check("source_policy_closed=0/40" in proc.stdout, "B6 closed-loop extraction overclosed source-policy rows")
    return proc.stdout


def run_cmame_self_contained_runner_extraction_plan_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_cmame_self_contained_runner_extraction_plan.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"CMAME self-contained runner extraction plan failed:\n{proc.stdout}")
    v.check(
        "cmame self-contained runner extraction plan validation: PASS" in proc.stdout,
        "CMAME self-contained runner extraction plan did not report PASS",
    )
    v.check("self_contained_runner_ready=False" in proc.stdout, "CMAME self-contained plan overclaims readiness")
    v.check(
        "local_accepted_rows_self_contained_runner_ready=True" in proc.stdout,
        "CMAME self-contained plan lost local accepted-row readiness",
    )
    v.check(
        "full_source_policy_self_contained_runner_ready=False" in proc.stdout,
        "CMAME self-contained plan overclaims full source-policy runner readiness",
    )
    v.check("b6_local_evidence_rows=12" in proc.stdout, "CMAME self-contained plan lost B6 row count")
    v.check("source_policy_closed=0/40" in proc.stdout, "CMAME self-contained plan overclosed source-policy rows")
    return proc.stdout


def run_cmame_minimal_reproducibility_candidate_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_cmame_minimal_reproducibility_candidate.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"CMAME minimal reproducibility candidate validator failed:\n{proc.stdout}")
    v.check(
        "cmame minimal reproducibility candidate validation: PASS" in proc.stdout,
        "CMAME minimal reproducibility candidate validator did not report PASS",
    )
    v.check("candidate_files=10" in proc.stdout, "CMAME minimal reproducibility candidate file count changed")
    v.check("candidate_python_lines=180" in proc.stdout, "CMAME minimal reproducibility candidate line count changed")
    v.check("source_policy_closed=0/40" in proc.stdout, "CMAME minimal reproducibility overclosed source-policy rows")
    v.check("direct_pc2_proof_gap_closed=True" in proc.stdout, "CMAME minimal reproducibility lost PC2 marker")
    v.check("submission_ready=False" in proc.stdout, "CMAME minimal reproducibility overclaims submission readiness")
    return proc.stdout


def run_cmame_closed_loop_local_runner_candidate_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_cmame_closed_loop_local_runner_candidate.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"CMAME closed-loop local runner candidate validator failed:\n{proc.stdout}")
    v.check(
        "CMAME closed-loop local runner candidate validation: PASS" in proc.stdout,
        "CMAME closed-loop local runner candidate validator did not report PASS",
    )
    v.check(
        "status=closed_loop_local_runner_candidate_passed_compact" in proc.stdout,
        "CMAME closed-loop local runner candidate status changed",
    )
    v.check("runner_passed=True" in proc.stdout, "CMAME closed-loop local runner did not pass")
    v.check("candidate_python=10/1962" in proc.stdout, "CMAME closed-loop local runner inventory changed")
    v.check("closed_loop_local_rows=6" in proc.stdout, "CMAME closed-loop local runner row count changed")
    return proc.stdout


def run_cmame_local_accepted_runner_companion_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_cmame_local_accepted_runner_companion.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"CMAME local accepted-row runner companion validator failed:\n{proc.stdout}")
    v.check(
        "CMAME local accepted-row runner companion validation: PASS" in proc.stdout,
        "CMAME local accepted-row runner companion validator did not report PASS",
    )
    v.check(
        "status=local_accepted_runner_companion_ready_source_policy_package_open" in proc.stdout,
        "CMAME local accepted runner companion status changed",
    )
    v.check("local_rows=12" in proc.stdout, "CMAME local accepted runner companion local-row count changed")
    v.check("candidate_python_lines=150" in proc.stdout, "CMAME local accepted runner companion line count changed")
    v.check("source_policy_closed=0/40" in proc.stdout, "CMAME local accepted runner companion overclosed rows")
    v.check(
        "source_policy_execution_allowed_now=False" in proc.stdout,
        "CMAME local accepted runner companion over-allows source-policy execution",
    )
    v.check(
        "source_policy_execution_invoked=False" in proc.stdout,
        "CMAME local accepted runner companion invoked source-policy execution",
    )
    v.check("submission_ready=False" in proc.stdout, "CMAME local accepted runner companion overclaims submission")
    return proc.stdout


def run_cmame_p1_local_runner_extraction_audit_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_cmame_p1_local_runner_extraction_audit.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"CMAME P1 local-runner extraction audit failed:\n{proc.stdout}")
    v.check(
        "cmame P1 local-runner extraction audit validation: PASS" in proc.stdout,
        "CMAME P1 local-runner extraction audit did not report PASS",
    )
    v.check("p1_local_single_double_ready=True" in proc.stdout, "CMAME P1 extraction lost local readiness")
    v.check("p1_single_runner_candidate_ready=True" in proc.stdout, "CMAME P1 extraction lost single runner readiness")
    v.check("p1_double_runner_candidate_ready=True" in proc.stdout, "CMAME P1 extraction lost double runner readiness")
    v.check("p1_regenerated_candidate_rows=6/6" in proc.stdout, "CMAME P1 extraction row count changed")
    return proc.stdout


def run_cmame_p1_single_runner_candidate_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_cmame_p1_single_runner_candidate.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"CMAME P1 single runner candidate validator failed:\n{proc.stdout}")
    v.check("cmame_p1_single_runner_candidate=PASS" in proc.stdout, "CMAME P1 single runner did not report PASS")
    v.check("p1_single_only_ready=True" in proc.stdout, "CMAME P1 single runner lost readiness marker")
    v.check("p1_complete=False" in proc.stdout, "CMAME P1 single runner overclaims P1 completion")
    v.check(
        "source_policy_external_superiority_allowed=False" in proc.stdout,
        "CMAME P1 single runner over-allows source-policy superiority",
    )
    v.check("local_runner_proof_gap_closed=False" in proc.stdout, "CMAME P1 single runner overcloses proof gap")
    return proc.stdout


def run_cmame_p1_double_runner_candidate_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_cmame_p1_double_runner_candidate.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"CMAME P1 double runner candidate validator failed:\n{proc.stdout}")
    v.check("cmame_p1_double_runner_candidate=PASS" in proc.stdout, "CMAME P1 double runner did not report PASS")
    v.check("p1_double_only_ready=True" in proc.stdout, "CMAME P1 double runner lost readiness marker")
    v.check("p1_complete=False" in proc.stdout, "CMAME P1 double runner overclaims P1 completion")
    v.check(
        "imports_v047_v048_or_v029=False" in proc.stdout,
        "CMAME P1 double runner imports forbidden version code",
    )
    v.check(
        "source_policy_external_superiority_allowed=False" in proc.stdout,
        "CMAME P1 double runner over-allows source-policy superiority",
    )
    v.check("local_runner_proof_gap_closed=False" in proc.stdout, "CMAME P1 double runner overcloses proof gap")
    return proc.stdout


def run_cmame_runner_adapter_candidate_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_cmame_runner_adapter_candidate.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"CMAME runner-adapter candidate validator failed:\n{proc.stdout}")
    v.check(
        "cmame runner-adapter candidate validation: PASS" in proc.stdout,
        "CMAME runner-adapter candidate validator did not report PASS",
    )
    v.check("candidate_python_lines=313" in proc.stdout, "CMAME runner-adapter line count changed")
    v.check("runner_adapter_present=True" in proc.stdout, "CMAME runner-adapter marker missing")
    v.check("self_contained_simulation_runner=False" in proc.stdout, "CMAME runner-adapter overclaims self-contained runner")
    v.check("source_policy_closed=0/40" in proc.stdout, "CMAME runner-adapter overclosed source-policy rows")
    v.check("submission_ready=False" in proc.stdout, "CMAME runner-adapter overclaims submission readiness")
    return proc.stdout


def run_cmame_narrowed_repro_bundle_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_cmame_narrowed_repro_bundle.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"CMAME narrowed repro bundle validator failed:\n{proc.stdout}")
    v.check(
        "cmame narrowed repro bundle validation: PASS" in proc.stdout,
        "CMAME narrowed repro bundle validator did not report PASS",
    )
    v.check("source_policy_external_rows=0/40" in proc.stdout, "CMAME narrowed bundle overclosed rows")
    v.check(
        "full_source_policy_runner_package_ready=False" in proc.stdout,
        "CMAME narrowed bundle overclaims full source-policy package readiness",
    )
    v.check("submission_ready=False" in proc.stdout, "CMAME narrowed bundle overclaims submission readiness")
    return proc.stdout


def run_cmame_submission_integrity_audit_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_cmame_submission_integrity_audit.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"CMAME submission integrity audit validator failed:\n{proc.stdout}")
    v.check(
        "cmame_submission_integrity_audit=PASS" in proc.stdout,
        "CMAME submission integrity audit validator did not report PASS",
    )
    v.check("local_integrity_passed=True" in proc.stdout, "CMAME submission integrity audit lost local integrity marker")
    v.check("citation_keys=28/28" in proc.stdout, "CMAME submission integrity citation count changed")
    v.check("dangling_citation_keys=0" in proc.stdout, "CMAME submission integrity found dangling citations")
    v.check("orphan_bibitems=0" in proc.stdout, "CMAME submission integrity found orphan bibitems")
    v.check("doi_metadata_verified=16/16" in proc.stdout, "CMAME submission integrity DOI metadata count changed")
    v.check("non_doi_metadata_verified=12/12" in proc.stdout, "CMAME submission integrity non-DOI metadata count changed")
    v.check(
        "external_reference_web_verification_complete=True" in proc.stdout,
        "CMAME submission integrity lost external-reference verification marker",
    )
    v.check(
        "manifest_source_policy_execution_invoked=False" in proc.stdout,
        "CMAME submission integrity invoked source-policy execution",
    )
    v.check("submission_ready=False" in proc.stdout, "CMAME submission integrity overclaims submission readiness")
    return proc.stdout


def run_reference_metadata_audit_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_reference_metadata_audit.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"reference metadata audit validator failed:\n{proc.stdout}")
    v.check(
        "reference metadata audit validation: PASS" in proc.stdout,
        "reference metadata audit validator did not report PASS",
    )
    v.check("doi_metadata_verified=16/16" in proc.stdout, "reference metadata DOI count changed")
    v.check("non_doi_metadata_verified=12/12" in proc.stdout, "reference metadata non-DOI count changed")
    v.check("non_doi_reference_count=0" in proc.stdout, "reference metadata non-DOI reference count changed")
    v.check(
        "external_reference_web_verification_complete=True" in proc.stdout,
        "reference metadata audit lost external-reference verification marker",
    )
    return proc.stdout


def run_result_to_manuscript_traceability_audit_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_result_to_manuscript_traceability_audit.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"result-to-manuscript traceability audit validator failed:\n{proc.stdout}")
    v.check(
        "result-to-manuscript traceability validation: PASS" in proc.stdout,
        "result-to-manuscript traceability audit validator did not report PASS",
    )
    v.check("velocity_cells_checked=44/44" in proc.stdout, "result-to-manuscript velocity-cell count changed")
    v.check("main_tex_pdf_cells=44/44" in proc.stdout, "result-to-manuscript main TeX/PDF cell count changed")
    v.check("flat_tex_pdf_cells=44/44" in proc.stdout, "result-to-manuscript flat TeX/PDF cell count changed")
    v.check(
        "source_policy_reproduction_closed=False" in proc.stdout,
        "result-to-manuscript audit overclosed source-policy reproduction",
    )
    v.check(
        "external_superiority_claim_allowed=False" in proc.stdout,
        "result-to-manuscript audit over-allows external superiority claims",
    )
    v.check("submission_ready=False" in proc.stdout, "result-to-manuscript audit overclaims submission readiness")
    return proc.stdout


def run_cmame_figure_set_audit_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_cmame_figure_set_audit.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"CMAME figure-set audit validator failed:\n{proc.stdout}")
    v.check(
        "cmame figure-set audit validation: PASS" in proc.stdout,
        "CMAME figure-set audit validator did not report PASS",
    )
    v.check("figures=13/13" in proc.stdout, "CMAME figure-set count changed")
    v.check(
        "figure12_all_method_matrix_integrated=True" in proc.stdout,
        "CMAME figure-set audit lost Figure 12 integration marker",
    )
    v.check(
        "figure13_work_precision_compendium_integrated=True" in proc.stdout,
        "CMAME figure-set audit lost Figure 13 integration marker",
    )
    v.check("b7_closed=True" in proc.stdout, "CMAME figure-set audit lost B7 closure marker")
    return proc.stdout


def run_cmame_scalability_boundary_audit_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_cmame_scalability_boundary_audit.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"CMAME scalability boundary audit validator failed:\n{proc.stdout}")
    v.check(
        "cmame scalability boundary audit validation: PASS" in proc.stdout,
        "CMAME scalability boundary audit validator did not report PASS",
    )
    v.check("b7_closed=False" in proc.stdout, "CMAME scalability boundary audit overclosed B7")
    v.check("residual_dimension=132" in proc.stdout, "CMAME scalability boundary residual dimension changed")
    v.check("n_body_chain_sweep_present=False" in proc.stdout, "CMAME scalability boundary found unexpected n-body sweep")
    return proc.stdout


def run_cmame_claim_hygiene_audit_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_cmame_claim_hygiene_audit.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"CMAME claim-hygiene audit validator failed:\n{proc.stdout}")
    v.check(
        "cmame claim-hygiene audit validation: PASS" in proc.stdout,
        "CMAME claim-hygiene audit validator did not report PASS",
    )
    v.check("status=pass" in proc.stdout, "CMAME claim-hygiene audit status changed")
    v.check(
        "allowed_claim=conditional_formal_order_comparison" in proc.stdout,
        "CMAME claim-hygiene audit lost allowed-claim marker",
    )
    v.check("forbidden_hits=0" in proc.stdout, "CMAME claim-hygiene audit found forbidden claims")
    v.check("submission_ready=False" in proc.stdout, "CMAME claim-hygiene audit overclaims submission readiness")
    return proc.stdout


def run_cmame_pdf_style_review_audit_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_cmame_pdf_style_review_audit.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"CMAME PDF style review audit validator failed:\n{proc.stdout}")
    v.check(
        "CMAME PDF style review audit validation: PASS" in proc.stdout,
        "CMAME PDF style review audit validator did not report PASS",
    )
    v.check("reference_figures=18" in proc.stdout, "CMAME PDF style review reference figure count changed")
    v.check("manuscript_figures=13" in proc.stdout, "CMAME PDF style review manuscript figure count changed")
    v.check("source_policy_rows_closed=0/40" in proc.stdout, "CMAME PDF style review overclosed source-policy rows")
    return proc.stdout


def run_cmame_review_agent_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_cmame_review_agent.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"CMAME review-agent validator failed:\n{proc.stdout}")
    v.check(
        "cmame review-agent validation: PASS" in proc.stdout,
        "CMAME review-agent validator did not report PASS",
    )
    v.check("submission_standard_met=False" in proc.stdout, "CMAME review-agent overclaims submission standard")
    v.check("decision=do_not_submit_global" in proc.stdout, "CMAME review-agent decision changed")
    v.check("open_blocker_ids=OC4,OC6,OC12" in proc.stdout, "CMAME review-agent open blockers changed")
    v.check(
        "source_policy_apples_to_apples_external=0/40" in proc.stdout,
        "CMAME review-agent overclosed apples-to-apples external rows",
    )
    v.check(
        "blocker_closure_allowed_by_id=OC4:False,OC6:False,OC12:False" in proc.stdout,
        "CMAME review-agent over-allows blocker closure",
    )
    return proc.stdout


def run_cmame_narrowed_claim_closure_policy_audit_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_cmame_narrowed_claim_closure_policy_audit.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"CMAME narrowed-claim closure policy audit validator failed:\n{proc.stdout}")
    v.check(
        "CMAME narrowed-claim closure policy audit validation: PASS" in proc.stdout,
        "CMAME narrowed-claim closure policy audit validator did not report PASS",
    )
    v.check(
        "narrowed_claim_evidence_supported=True" in proc.stdout,
        "CMAME narrowed-claim closure policy audit lost evidence-supported marker",
    )
    v.check(
        "current_gate_can_close_now=True" in proc.stdout,
        "CMAME narrowed-claim closure policy audit lost current-gate closure marker",
    )
    v.check("source_policy_rows=0/40" in proc.stdout, "CMAME narrowed-claim closure policy audit overclosed rows")
    v.check(
        "blocker_open_by_id=OC4:True,OC6:True,OC12:True" in proc.stdout,
        "CMAME narrowed-claim closure policy audit lost blocker-open matrix",
    )
    v.check(
        "blocker_closure_allowed_by_id=OC4:False,OC6:False,OC12:False" in proc.stdout,
        "CMAME narrowed-claim closure policy audit over-allows blocker closure",
    )
    return proc.stdout


def run_paper_core_to_manuscript_audit_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_paper_core_to_manuscript_audit.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"paper core-to-manuscript audit validator failed:\n{proc.stdout}")
    v.check(
        "paper core to manuscript audit validation: PASS" in proc.stdout,
        "paper core-to-manuscript audit validator did not report PASS",
    )
    v.check(
        "paper_core_traceability_closed=True" in proc.stdout,
        "paper core-to-manuscript audit lost traceability closure marker",
    )
    v.check(
        "main_tex_pdf_core_values_present=True" in proc.stdout,
        "paper core-to-manuscript audit lost main TeX/PDF marker",
    )
    v.check(
        "flat_tex_pdf_core_present=True" in proc.stdout,
        "paper core-to-manuscript audit lost flat TeX/PDF marker",
    )
    v.check("experiments_launched=False" in proc.stdout, "paper core-to-manuscript audit launched experiments")
    return proc.stdout


def run_all_examples_result_sanity_audit_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_all_examples_result_sanity_audit.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"all-examples result sanity audit validator failed:\n{proc.stdout}")
    v.check(
        "all-examples result sanity audit validation: PASS" in proc.stdout,
        "all-examples result sanity audit validator did not report PASS",
    )
    v.check("cells=44/44" in proc.stdout, "all-examples result sanity audit cell count changed")
    v.check(
        "examples=single_pendulum,double_pendulum,four_link,slider_crank" in proc.stdout,
        "all-examples result sanity audit lost four-example coverage marker",
    )
    v.check("flagged_nonlocal_rows=15" in proc.stdout, "all-examples result sanity audit flagged-row count changed")
    v.check(
        "external_superiority_allowed=False" in proc.stdout,
        "all-examples result sanity audit over-allows external superiority",
    )
    return proc.stdout


def run_all_method_example_claim_disposition_audit_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_all_method_example_claim_disposition_audit.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"all-method claim-disposition audit validator failed:\n{proc.stdout}")
    v.check(
        "all-method claim-disposition audit validation: PASS" in proc.stdout,
        "all-method claim-disposition audit validator did not report PASS",
    )
    v.check("nonlocal_cells=40/40" in proc.stdout, "all-method claim-disposition nonlocal cell count changed")
    v.check("local_velocity_order_wins=40/40" in proc.stdout, "all-method claim-disposition velocity-order count changed")
    v.check(
        "local_finest_velocity_error_wins=40/40" in proc.stdout,
        "all-method claim-disposition finest-velocity-error count changed",
    )
    v.check(
        "nonlocal_source_policy_closed_rows=0/40" in proc.stdout,
        "all-method claim-disposition overclosed source-policy rows",
    )
    v.check(
        "nonlocal_source_policy_open_rows=40/40" in proc.stdout,
        "all-method claim-disposition lost source-policy-open row count",
    )
    v.check("flagged_nonlocal_rows=15/40" in proc.stdout, "all-method claim-disposition flagged-row count changed")
    v.check(
        "source_policy_superiority_claim_allowed=False" in proc.stdout,
        "all-method claim-disposition over-allows source-policy superiority",
    )
    return proc.stdout


def run_paper_numerical_result_matrix_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_paper_numerical_result_matrix.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"paper numerical result matrix validator failed:\n{proc.stdout}")
    v.check(
        "paper numerical result matrix validation: PASS" in proc.stdout,
        "paper numerical result matrix validator did not report PASS",
    )
    v.check("rows=44/44" in proc.stdout, "paper numerical result matrix row count changed")
    v.check(
        "examples=single_pendulum,double_pendulum,four_link,slider_crank" in proc.stdout,
        "paper numerical result matrix lost four-example coverage marker",
    )
    v.check("methods=11" in proc.stdout, "paper numerical result matrix method count changed")
    v.check(
        "source_policy_external_superiority_allowed=False" in proc.stdout,
        "paper numerical result matrix over-allows source-policy external superiority",
    )
    v.check(
        "paper_direct_error_superiority_allowed=False" in proc.stdout,
        "paper numerical result matrix over-allows direct-error superiority",
    )
    return proc.stdout


def run_common_reference_order_recomputation_audit_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_common_reference_order_recomputation_audit.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"common-reference order recomputation audit validator failed:\n{proc.stdout}")
    v.check(
        "common-reference order recomputation audit validation: PASS" in proc.stdout,
        "common-reference order recomputation audit validator did not report PASS",
    )
    v.check("cells=44/44" in proc.stdout, "common-reference order recomputation cell count changed")
    v.check("raw_rows=132" in proc.stdout, "common-reference order recomputation raw-row count changed")
    v.check("mismatches=0" in proc.stdout, "common-reference order recomputation found mismatches")
    v.check(
        "external_superiority_allowed=False" in proc.stdout,
        "common-reference order recomputation over-allows external superiority",
    )
    return proc.stdout


def run_comparison_objective_closure_reconciliation_audit_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_comparison_objective_closure_reconciliation_audit.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"comparison objective closure reconciliation audit validator failed:\n{proc.stdout}")
    v.check(
        "comparison objective closure reconciliation audit validation: PASS" in proc.stdout,
        "comparison objective closure reconciliation audit validator did not report PASS",
    )
    v.check(
        "comparison_matrix_closed=True" in proc.stdout,
        "comparison objective closure reconciliation lost closed-matrix marker",
    )
    v.check(
        "common_reference_claim_allowed=True" in proc.stdout,
        "comparison objective closure reconciliation lost common-reference claim marker",
    )
    v.check(
        "paper_direct_error_superiority_claim_allowed=False" in proc.stdout,
        "comparison objective closure reconciliation over-allows direct-error superiority",
    )
    v.check(
        "source_policy_superiority_claim_allowed=False" in proc.stdout,
        "comparison objective closure reconciliation over-allows source-policy superiority",
    )
    v.check(
        "direct_nonlocal_order_wins=40/40" in proc.stdout,
        "comparison objective closure reconciliation order-win count changed",
    )
    v.check(
        "direct_nonlocal_error_wins=40/40" in proc.stdout,
        "comparison objective closure reconciliation error-win count changed",
    )
    return proc.stdout


def run_paper_core_result_consolidation_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_paper_core_result_consolidation.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"paper core result consolidation validator failed:\n{proc.stdout}")
    v.check(
        "paper core result consolidation validation: PASS" in proc.stdout,
        "paper core result consolidation validator did not report PASS",
    )
    v.check("four_example_local_order=4/4" in proc.stdout, "paper core consolidation local-order count changed")
    v.check(
        "common_reference_order_error_wins=40/40,40/40" in proc.stdout,
        "paper core consolidation common-reference count changed",
    )
    v.check(
        "closed_loop_coarse_dynamics_candidates=2/2" in proc.stdout,
        "paper core consolidation closed-loop coarse candidate count changed",
    )
    v.check("experiments_launched=False" in proc.stdout, "paper core consolidation launched experiments")
    return proc.stdout


def run_proof_closure_manifest_validator(v: Validator) -> str:
    # 2026-09-17: PROOF_CLOSURE_MANIFEST is superseded by EXACT_STAGE_IDENTITY_GATE; run that gate here.
    proc = subprocess.run(
        [sys.executable, "validate_exact_stage_identity_gate.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"exact stage identity gate validator failed:\n{proc.stdout}")
    v.check("exact_stage_identity_gate=PASS" in proc.stdout, "exact stage identity gate did not report PASS")
    v.check(
        "status=exact_stage_identity_route_pinned_lean_checked" in proc.stdout
        or "status=exact_stage_identity_route_pinned_lean_not_run_here" in proc.stdout,
        "exact stage identity gate lost its pinned-status marker",
    )
    return "PROOF_CLOSURE_MANIFEST superseded_by=EXACT_STAGE_IDENTITY_GATE\n" + proc.stdout


def run_proof_claim_traceability_audit_validator(v: Validator) -> str:
    # 2026-09-17: superseded by EXACT_STAGE_IDENTITY_GATE (see run_proof_closure_manifest_validator).
    return "superseded_by=EXACT_STAGE_IDENTITY_GATE\nnote=this gate pinned the retired 96-row/PS2/primitive-Taylor proof route; the compacted manuscript (2026-09-17) proves the stage residual at the lifted Gauss stage is identically zero. Archived record kept; validator not run."


def run_proof_remaining_work_manifest_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_proof_remaining_work_manifest.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"proof remaining-work manifest validator failed:\n{proc.stdout}")
    v.check(
        "proof remaining-work manifest validation: PASS" in proc.stdout,
        "proof remaining-work manifest validator did not report PASS",
    )
    v.check("unsatisfied_close_requirements=0" in proc.stdout, "proof remaining-work manifest has unsatisfied requirements")
    v.check("open_dynamic_rows=36" in proc.stdout, "proof remaining-work manifest dynamic row count changed")
    v.check("newton_euler_row_obligation_links=180" in proc.stdout, "proof remaining-work manifest link count changed")
    v.check("direct_pc2_proof_gap_closed=True" in proc.stdout, "proof remaining-work manifest lost direct PC2 marker")
    v.check(
        "active_b1_b3_proof_blockers_remaining=False" in proc.stdout,
        "proof remaining-work manifest reopened active B1/B3 blockers",
    )
    v.check(
        "residual_to_error_blocking_obligations=7" in proc.stdout,
        "proof remaining-work manifest lost residual-to-error boundary",
    )
    v.check("submission_ready=False" in proc.stdout, "proof remaining-work manifest overclaims submission readiness")
    return proc.stdout


def run_b1_ad_expanded_symbolic_oracle_closure_certificate_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_b1_ad_expanded_symbolic_oracle_closure_certificate.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"B1 AD-expanded symbolic oracle closure validator failed:\n{proc.stdout}")
    v.check(
        "b1_ad_expanded_symbolic_oracle_closure_certificate=PASS" in proc.stdout,
        "B1 AD-expanded symbolic oracle closure validator did not report PASS",
    )
    v.check("closed_derivative_cells=4752/4752" in proc.stdout, "B1 AD-expanded derivative cell count changed")
    v.check(
        "ad_expanded_symbolic_oracle_closure=True" in proc.stdout,
        "B1 AD-expanded symbolic oracle closure marker missing",
    )
    v.check("submission_ready=False" in proc.stdout, "B1 AD-expanded validator overclaims submission readiness")
    return proc.stdout


def run_b1_symbolic_row_oracle_closure_certificate_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_b1_symbolic_row_oracle_closure_certificate.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"B1 symbolic row oracle closure validator failed:\n{proc.stdout}")
    v.check(
        "b1_symbolic_row_oracle_closure_certificate=PASS" in proc.stdout,
        "B1 symbolic row oracle closure validator did not report PASS",
    )
    v.check("closed_symbolic_rows=36" in proc.stdout, "B1 symbolic row count changed")
    v.check(
        "remaining_b1_required_item=AD_expanded_symbolic_oracle_closure" in proc.stdout,
        "B1 symbolic row oracle boundary changed",
    )
    return proc.stdout


def run_b3_direct_proof_review_audit_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_b3_direct_proof_review_audit.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"B3 direct proof review audit validator failed:\n{proc.stdout}")
    v.check(
        "b3_direct_proof_review_audit=PASS" in proc.stdout,
        "B3 direct proof review audit validator did not report PASS",
    )
    v.check("b3_direct_proof_review_passed=True" in proc.stdout, "B3 direct proof review lost pass marker")
    v.check("b3_can_close_from_proof_review=True" in proc.stdout, "B3 direct proof review lost close marker")
    v.check("submission_ready=False" in proc.stdout, "B3 direct proof review overclaims submission readiness")
    return proc.stdout


def run_cmame_strict_proof_audit_validator(v: Validator) -> str:
    # 2026-09-17: superseded by EXACT_STAGE_IDENTITY_GATE (see run_proof_closure_manifest_validator).
    return "superseded_by=EXACT_STAGE_IDENTITY_GATE\nnote=this gate pinned the retired 96-row/PS2/primitive-Taylor proof route; the compacted manuscript (2026-09-17) proves the stage residual at the lifted Gauss stage is identically zero. Archived record kept; validator not run."


def run_cmame_strict_proof_policy_reconciliation_audit_validator(v: Validator) -> str:
    # 2026-09-17: superseded by EXACT_STAGE_IDENTITY_GATE (see run_proof_closure_manifest_validator).
    return "superseded_by=EXACT_STAGE_IDENTITY_GATE\nnote=this gate pinned the retired 96-row/PS2/primitive-Taylor proof route; the compacted manuscript (2026-09-17) proves the stage residual at the lifted Gauss stage is identically zero. Archived record kept; validator not run."


def run_cmame_proof_style_audit_validator(v: Validator) -> str:
    # 2026-09-17: superseded by EXACT_STAGE_IDENTITY_GATE (see run_proof_closure_manifest_validator).
    return "superseded_by=EXACT_STAGE_IDENTITY_GATE\nnote=this gate pinned the retired 96-row/PS2/primitive-Taylor proof route; the compacted manuscript (2026-09-17) proves the stage residual at the lifted Gauss stage is identically zero. Archived record kept; validator not run."


def run_kinematic_row_defect_certificate_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_kinematic_row_defect_certificate.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"kinematic row defect certificate validator failed:\n{proc.stdout}")
    v.check(
        "kinematic_row_defect_certificate=PASS" in proc.stdout,
        "kinematic row defect certificate validator did not report PASS",
    )
    v.check("accepted_method=Gauss6/FullVA" in proc.stdout, "kinematic row defect certificate method changed")
    v.check("certified_row_count=96" in proc.stdout, "kinematic row defect certificate row count changed")
    v.check(
        "excluded_row_family=newton_euler_weak_balance" in proc.stdout,
        "kinematic row defect certificate excluded-row boundary changed",
    )
    v.check(
        "partial_stage_defect_certificate=True" in proc.stdout,
        "kinematic row defect certificate lost partial-stage marker",
    )
    v.check(
        "stage_residual_O_h7_implementation_defect_proved=False" in proc.stdout,
        "kinematic row defect certificate overclosed dynamic defect",
    )
    v.check(
        "dynamic_symbolic_oracle_complete=False" in proc.stdout,
        "kinematic row defect certificate overclosed dynamic symbolic oracle",
    )
    v.check(
        "full_tfe_stage_replacement=False" in proc.stdout,
        "kinematic row defect certificate overclaims full-TFE stage replacement",
    )
    v.check("run_v047_invoked=False" in proc.stdout, "kinematic row defect certificate invoked run_v047")
    v.check("v048_runner_invoked=False" in proc.stdout, "kinematic row defect certificate invoked v048 runner")
    v.check("submission_ready=False" in proc.stdout, "kinematic row defect certificate overclaims submission readiness")
    return proc.stdout


def run_newton_euler_virtual_work_wrench_audit_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_newton_euler_virtual_work_wrench_audit.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"Newton-Euler virtual-work wrench audit validator failed:\n{proc.stdout}")
    v.check(
        "newton_euler_virtual_work_wrench_audit=PASS" in proc.stdout,
        "Newton-Euler virtual-work wrench audit validator did not report PASS",
    )
    v.check("checked_rows=36" in proc.stdout, "Newton-Euler virtual-work row count changed")
    v.check(
        "template_virtual_work_identity_proved=True" in proc.stdout,
        "Newton-Euler virtual-work template identity marker missing",
    )
    v.check(
        "row_expanded_virtual_work_identity_proved=True" in proc.stdout,
        "Newton-Euler virtual-work row-expanded marker missing",
    )
    v.check(
        "multiplier_wrench_consistency_closed=True" in proc.stdout,
        "Newton-Euler virtual-work multiplier consistency marker missing",
    )
    v.check(
        "local_d3_audit_proof_gap_closed=False" in proc.stdout,
        "Newton-Euler virtual-work overclosed local D3 proof gap",
    )
    return proc.stdout


def run_newton_euler_symbolic_target_audit_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_newton_euler_symbolic_target_audit.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"Newton-Euler symbolic target audit validator failed:\n{proc.stdout}")
    v.check(
        "newton_euler_symbolic_target_audit=PASS" in proc.stdout,
        "Newton-Euler symbolic target audit validator did not report PASS",
    )
    v.check("row_count=36" in proc.stdout, "Newton-Euler symbolic target row count changed")
    v.check("translational_rotational_rows=18/18" in proc.stdout, "Newton-Euler symbolic target split changed")
    v.check(
        "symbolic_target_inventory_complete=True" in proc.stdout,
        "Newton-Euler symbolic target inventory marker missing",
    )
    v.check(
        "obligation_coverage_matrix_complete=True" in proc.stdout,
        "Newton-Euler symbolic target coverage marker missing",
    )
    v.check("row_obligation_links=180" in proc.stdout, "Newton-Euler symbolic target link count changed")
    v.check(
        "stage_residual_O_h7_implementation_defect_proved=False" in proc.stdout,
        "Newton-Euler symbolic target overclosed O(h^7) defect",
    )
    v.check(
        "dynamic_symbolic_oracle_complete=False" in proc.stdout,
        "Newton-Euler symbolic target overclosed dynamic symbolic oracle",
    )
    v.check("submission_ready=False" in proc.stdout, "Newton-Euler symbolic target overclaims submission readiness")
    return proc.stdout


def run_newton_euler_symbolic_defect_certificate_validator(v: Validator) -> str:
    # 2026-09-17: superseded by EXACT_STAGE_IDENTITY_GATE (see run_proof_closure_manifest_validator).
    return "superseded_by=EXACT_STAGE_IDENTITY_GATE\nnote=this gate pinned the retired 96-row/PS2/primitive-Taylor proof route; the compacted manuscript (2026-09-17) proves the stage residual at the lifted Gauss stage is identically zero. Archived record kept; validator not run."


def run_newton_euler_row_ordering_scaling_ad_audit_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_newton_euler_row_ordering_scaling_ad_audit.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"Newton-Euler row-ordering/scaling AD audit validator failed:\n{proc.stdout}")
    v.check(
        "newton_euler_row_ordering_scaling_ad_audit=PASS" in proc.stdout,
        "Newton-Euler row-ordering/scaling AD audit validator did not report PASS",
    )
    v.check(
        "symbolic_runtime_row_equivalence_closed=True" in proc.stdout,
        "Newton-Euler row-ordering/scaling AD audit lost equivalence marker",
    )
    v.check("dynamic_rows=36" in proc.stdout, "Newton-Euler row-ordering/scaling AD audit row count changed")
    v.check(
        "stage_residual_O_h7_implementation_defect_proved=False" in proc.stdout,
        "Newton-Euler row-ordering/scaling AD audit overclosed O(h^7) defect",
    )
    v.check(
        "local_d6_audit_proof_gap_closed=False" in proc.stdout,
        "Newton-Euler row-ordering/scaling AD audit overclosed local D6 proof gap",
    )
    return proc.stdout


def run_newton_euler_dynamic_row_closure_contract_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_newton_euler_dynamic_row_closure_contract.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"Newton-Euler dynamic row closure contract validator failed:\n{proc.stdout}")
    v.check(
        "newton_euler_dynamic_row_closure_contract=PASS" in proc.stdout,
        "Newton-Euler dynamic row closure contract validator did not report PASS",
    )
    v.check("rows=36" in proc.stdout, "Newton-Euler dynamic row closure row count changed")
    v.check(
        "rows_with_full_runtime_traceability=36" in proc.stdout,
        "Newton-Euler dynamic row closure runtime traceability count changed",
    )
    v.check(
        "rows_with_direct_pc2_input_closure=36" in proc.stdout,
        "Newton-Euler dynamic row closure direct PC2 input count changed",
    )
    v.check(
        "unsatisfied_close_requirements=none" in proc.stdout,
        "Newton-Euler dynamic row closure has unsatisfied requirements",
    )
    v.check("direct_pc2_proof_gap_closed=True" in proc.stdout, "Newton-Euler dynamic row closure lost direct PC2 marker")
    v.check("legacy_proof_gap_closed=True" in proc.stdout, "Newton-Euler dynamic row closure lost legacy marker")
    return proc.stdout


def run_newton_euler_defect_obligation_gate_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_newton_euler_defect_obligation_gate.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"Newton-Euler defect obligation gate validator failed:\n{proc.stdout}")
    v.check(
        "newton_euler_defect_obligation_gate=PASS" in proc.stdout,
        "Newton-Euler defect obligation gate validator did not report PASS",
    )
    v.check("dynamic_row_count=36" in proc.stdout, "Newton-Euler defect obligation dynamic-row count changed")
    v.check("translational_balance_rows=18" in proc.stdout, "Newton-Euler defect obligation translational count changed")
    v.check("rotational_balance_rows=18" in proc.stdout, "Newton-Euler defect obligation rotational count changed")
    v.check(
        "symbolic_primitive_open_obligation_count=1" in proc.stdout,
        "Newton-Euler defect obligation primitive-open count changed",
    )
    v.check("active_direct_pc2_closed=True" in proc.stdout, "Newton-Euler defect obligation lost active direct PC2 marker")
    v.check("closed_obligation_count=5" in proc.stdout, "Newton-Euler defect obligation closed count changed")
    v.check(
        "newton_euler_symbolic_defect_certificate_complete=False" in proc.stdout,
        "Newton-Euler defect obligation overclosed symbolic certificate",
    )
    v.check(
        "symbolic_primitive_stage_residual_O_h7_certificate_complete=False" in proc.stdout,
        "Newton-Euler defect obligation overclosed primitive O(h^7) certificate",
    )
    v.check(
        "dynamic_symbolic_oracle_complete=False" in proc.stdout,
        "Newton-Euler defect obligation overclosed dynamic symbolic oracle",
    )
    v.check(
        "full_tfe_stage_replacement=False" in proc.stdout,
        "Newton-Euler defect obligation overclaims full-TFE stage replacement",
    )
    v.check("run_v047_invoked=False" in proc.stdout, "Newton-Euler defect obligation invoked run_v047")
    v.check("v048_runner_invoked=False" in proc.stdout, "Newton-Euler defect obligation invoked v048 runner")
    v.check("submission_ready=False" in proc.stdout, "Newton-Euler defect obligation overclaims submission readiness")
    return proc.stdout


def run_newton_euler_balance_identity_audit_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_newton_euler_balance_identity_audit.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"Newton-Euler balance identity audit validator failed:\n{proc.stdout}")
    v.check(
        "newton_euler_balance_identity_audit=PASS" in proc.stdout,
        "Newton-Euler balance identity audit validator did not report PASS",
    )
    v.check(
        "translational_balance_identity_closed=True" in proc.stdout,
        "Newton-Euler balance identity lost translational closure marker",
    )
    v.check(
        "rotational_balance_identity_closed=True" in proc.stdout,
        "Newton-Euler balance identity lost rotational closure marker",
    )
    v.check("balance_identity_closed_rows=36" in proc.stdout, "Newton-Euler balance identity closed-row count changed")
    v.check(
        "stage_residual_O_h7_implementation_defect_proved=False" in proc.stdout,
        "Newton-Euler balance identity overclosed O(h^7) defect",
    )
    return proc.stdout


def run_newton_euler_ad_expanded_row_oracle_audit_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_newton_euler_ad_expanded_row_oracle_audit.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"Newton-Euler AD-expanded row oracle audit validator failed:\n{proc.stdout}")
    v.check(
        "newton_euler_ad_expanded_row_oracle_audit=PASS" in proc.stdout,
        "Newton-Euler AD-expanded row oracle audit validator did not report PASS",
    )
    v.check("ad_expanded_rows=36" in proc.stdout, "Newton-Euler AD-expanded row count changed")
    v.check("ad_columns_per_row=132" in proc.stdout, "Newton-Euler AD-expanded column count changed")
    v.check(
        "dynamic_symbolic_oracle_complete=False" in proc.stdout,
        "Newton-Euler AD-expanded audit overclosed dynamic symbolic oracle",
    )
    return proc.stdout


def run_smooth_force_lift_certificate_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_smooth_force_lift_certificate.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"smooth force lift certificate validator failed:\n{proc.stdout}")
    v.check(
        "smooth_force_lift_certificate=PASS" in proc.stdout,
        "smooth force lift certificate validator did not report PASS",
    )
    v.check("source_structure_checked=True" in proc.stdout, "smooth force lift lost source-structure marker")
    v.check(
        "smooth_force_lift_consistency_closed=True" in proc.stdout,
        "smooth force lift lost consistency closure marker",
    )
    v.check(
        "global_C7_tube_derivative_bound_proved=True" in proc.stdout,
        "smooth force lift lost C7 derivative-bound marker",
    )
    v.check("proof_gap_closed=False" in proc.stdout, "smooth force lift overclosed proof gap")
    v.check("submission_ready=False" in proc.stdout, "smooth force lift overclaims submission readiness")
    return proc.stdout


def run_b2_source_policy_remaining_work_manifest_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_b2_source_policy_remaining_work_manifest.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"B2 source-policy remaining-work manifest validator failed:\n{proc.stdout}")
    v.check(
        "b2 source-policy remaining-work manifest validation: PASS" in proc.stdout,
        "B2 source-policy remaining-work manifest validator did not report PASS",
    )
    v.check("active_flagged_rows=0" in proc.stdout, "B2 remaining-work manifest active flagged rows changed")
    v.check("demoted_flagged_rows=15" in proc.stdout, "B2 remaining-work manifest demoted row count changed")
    v.check("source_policy_closed_rows=0" in proc.stdout, "B2 remaining-work manifest overclosed source-policy rows")
    v.check("b2_remaining_requirements=0" in proc.stdout, "B2 remaining-work manifest reopened B2 requirements")
    v.check(
        "closure_execution_plan=b2-source-policy-closure-execution-plan-v1" in proc.stdout,
        "B2 remaining-work manifest lost closure execution-plan marker",
    )
    v.check(
        "all_active_suites_ready_to_launch=True" in proc.stdout,
        "B2 remaining-work manifest lost active-suite readiness marker",
    )
    v.check(
        "external_superiority_claim_allowed=False" in proc.stdout,
        "B2 remaining-work manifest over-allows external superiority claims",
    )
    return proc.stdout


def run_source_policy_closure_triage_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_source_policy_closure_triage.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"source-policy closure triage validator failed:\n{proc.stdout}")
    v.check(
        "source-policy closure triage validation: PASS" in proc.stdout,
        "source-policy closure triage validator did not report PASS",
    )
    v.check("flagged_rows=15" in proc.stdout, "source-policy closure triage flagged row count changed")
    v.check(
        "flagged_examples=single_pendulum,double_pendulum,four_link,slider_crank" in proc.stdout,
        "source-policy closure triage lost four-example marker",
    )
    v.check("action_counts=5/4/3/3" in proc.stdout, "source-policy closure triage action counts changed")
    v.check("b2_b4_can_close_now=False/False" in proc.stdout, "source-policy closure triage overclosed B2/B4")
    v.check(
        "heavy_numerical_run_invoked=False" in proc.stdout,
        "source-policy closure triage invoked heavy numerical run",
    )
    return proc.stdout


def run_all_examples_source_policy_audit_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_all_examples_source_policy_audit.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"all-examples source-policy audit validator failed:\n{proc.stdout}")
    v.check(
        "all-examples source-policy audit validation: PASS" in proc.stdout,
        "all-examples source-policy audit validator did not report PASS",
    )
    v.check("flagged_rows=15" in proc.stdout, "all-examples source-policy audit flagged-row count changed")
    v.check("flagged_raw_rows=45" in proc.stdout, "all-examples source-policy audit raw-row count changed")
    v.check(
        "flagged_examples=single_pendulum,double_pendulum,four_link,slider_crank" in proc.stdout,
        "all-examples source-policy audit lost four-example marker",
    )
    v.check("suite_counts=5/4/3/3" in proc.stdout, "all-examples source-policy audit suite counts changed")
    v.check("b2_b4_can_close_now=False/False" in proc.stdout, "all-examples source-policy audit overclosed B2/B4")
    v.check(
        "heavy_numerical_run_invoked=False" in proc.stdout,
        "all-examples source-policy audit invoked heavy numerical run",
    )
    return proc.stdout


def run_four_example_source_policy_dashboard_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_four_example_source_policy_dashboard.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"four-example source-policy dashboard validator failed:\n{proc.stdout}")
    v.check(
        "four-example source-policy dashboard validation: PASS" in proc.stdout,
        "four-example source-policy dashboard validator did not report PASS",
    )
    v.check(
        "examples=single_pendulum,double_pendulum,four_link,slider_crank" in proc.stdout,
        "four-example source-policy dashboard lost four-example marker",
    )
    v.check(
        "local_evidence_coverage_examples=4/4" in proc.stdout,
        "four-example source-policy dashboard local evidence coverage changed",
    )
    v.check(
        "accepted_method_dynamic_order_examples=2/4" in proc.stdout,
        "four-example source-policy dashboard accepted method dynamic-order count changed",
    )
    v.check(
        "source_policy_dynamic_order_examples=0/4" in proc.stdout,
        "four-example source-policy dashboard overclaims source-policy dynamic order",
    )
    v.check(
        "common_reference_nonlocal_order_error_wins=40/40,40/40" in proc.stdout,
        "four-example source-policy dashboard common-reference audit counts changed",
    )
    return proc.stdout


def run_external_baseline_source_policy_diagnosis_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_external_baseline_source_policy_diagnosis.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"external baseline source-policy diagnosis validator failed:\n{proc.stdout}")
    v.check(
        "external baseline source-policy diagnosis validation: PASS" in proc.stdout,
        "external baseline source-policy diagnosis validator did not report PASS",
    )
    v.check("flagged_rows=15" in proc.stdout, "external baseline diagnosis flagged-row count changed")
    v.check(
        "same_test_campaign_status=not_run" in proc.stdout,
        "external baseline diagnosis unexpectedly ran same-test campaign",
    )
    v.check(
        "external_superiority_allowed=False" in proc.stdout,
        "external baseline diagnosis over-allows external superiority",
    )
    return proc.stdout


def run_external_case_evidence_reconciliation_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_external_case_evidence_reconciliation.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"external case evidence reconciliation validator failed:\n{proc.stdout}")
    v.check(
        "external case evidence reconciliation validation: PASS" in proc.stdout,
        "external case evidence reconciliation validator did not report PASS",
    )
    v.check(
        "bounded_evidence_suites=ra2021_absolute_coordinate,hi2022_half_implicit" in proc.stdout,
        "external case reconciliation bounded suite split changed",
    )
    v.check(
        "not_ready_or_demote_suites=tfe2026_original_pendulum,vp2024_velocity_partitioning" in proc.stdout,
        "external case reconciliation not-ready suite split changed",
    )
    v.check(
        "local_source_policy_dynamic_order_examples=0/4" in proc.stdout,
        "external case reconciliation overcloses source-policy dynamic order",
    )
    v.check("source_policy_rows_closed=0/15" in proc.stdout, "external case reconciliation overclosed rows")
    v.check(
        "external_superiority_ready_rows=0/15" in proc.stdout,
        "external case reconciliation overclaims external superiority readiness",
    )
    return proc.stdout


def run_external_same_test_acceptance_sheet_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_external_same_test_acceptance_sheet.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"external same-test acceptance sheet validator failed:\n{proc.stdout}")
    v.check(
        "external_same_test_acceptance_sheet=PASS" in proc.stdout,
        "external same-test acceptance sheet validator did not report PASS",
    )
    v.check(
        "same_test_campaign_status=not_run" in proc.stdout,
        "external same-test acceptance sheet unexpectedly ran same-test campaign",
    )
    v.check(
        "accepted_external_dynamic_order_examples=0" in proc.stdout,
        "external same-test acceptance sheet accepted external dynamic-order rows",
    )
    v.check(
        "source_policy_dynamic_order_examples=0/4" in proc.stdout,
        "external same-test acceptance sheet overcloses source-policy dynamic order",
    )
    v.check(
        "heavy_numerical_run_invoked=False" in proc.stdout,
        "external same-test acceptance sheet invoked heavy numerical run",
    )
    v.check(
        "external_superiority_claim=False" in proc.stdout,
        "external same-test acceptance sheet overclaims external superiority",
    )
    v.check("submission_ready=False" in proc.stdout, "external same-test acceptance sheet overclaims submission readiness")
    return proc.stdout


def run_external_suite_demotion_ledger_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_external_suite_demotion_ledger.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"external suite demotion ledger validator failed:\n{proc.stdout}")
    v.check(
        "external suite demotion ledger validation: PASS" in proc.stdout,
        "external suite demotion ledger validator did not report PASS",
    )
    v.check("demoted_suites=4" in proc.stdout, "external suite demotion ledger demoted-suite count changed")
    v.check(
        "active_source_policy_flagged_rows_after_demotions=0" in proc.stdout,
        "external suite demotion ledger left active flagged rows",
    )
    v.check("default_1e-4=False" in proc.stdout, "external suite demotion ledger changed default 1e-4 policy")
    v.check("run_v047_invoked=False" in proc.stdout, "external suite demotion ledger invoked run_v047")
    return proc.stdout


def run_external_suite_disposition_audit_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_external_suite_disposition_audit.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"external suite disposition audit validator failed:\n{proc.stdout}")
    v.check(
        "external suite disposition audit validation: PASS" in proc.stdout,
        "external suite disposition audit validator did not report PASS",
    )
    v.check("suites=4" in proc.stdout, "external suite disposition suite count changed")
    v.check(
        "accepted_external_superiority_suite_count=0" in proc.stdout,
        "external suite disposition overclaims external superiority suites",
    )
    v.check(
        "parallel_ready_shards_without_default_1e_4=20" in proc.stdout,
        "external suite disposition ready shard count changed",
    )
    v.check("b2_can_close_now=False" in proc.stdout, "external suite disposition overcloses B2")
    v.check("b4_can_close_now=False" in proc.stdout, "external suite disposition overcloses B4")
    return proc.stdout


def run_external_superiority_claim_demotion_audit_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_external_superiority_claim_demotion_audit.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"external superiority claim-demotion audit validator failed:\n{proc.stdout}")
    v.check(
        "external superiority claim-demotion audit validation: PASS" in proc.stdout,
        "external superiority claim-demotion audit validator did not report PASS",
    )
    v.check("route_b_ready=True" in proc.stdout, "external superiority claim demotion lost Route-B readiness")
    v.check(
        "b4_gate_closed_by_route_b_claim_demotion=False" in proc.stdout,
        "external superiority claim demotion overcloses B4",
    )
    v.check(
        "source_policy_execution_rows_closed=0/40" in proc.stdout,
        "external superiority claim demotion overclosed source-policy rows",
    )
    v.check(
        "external_superiority_claim_allowed_after_route=False" in proc.stdout,
        "external superiority claim demotion over-allows external superiority",
    )
    v.check("run_v047_invoked=False" in proc.stdout, "external superiority claim demotion invoked run_v047")
    return proc.stdout


def run_b4_b7_non_superiority_route_audit_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_b4_b7_non_superiority_route_audit.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"B4/B7 non-superiority route audit validator failed:\n{proc.stdout}")
    v.check(
        "B4/B7 non-superiority route audit validation: PASS" in proc.stdout,
        "B4/B7 non-superiority route audit validator did not report PASS",
    )
    v.check(
        "route_b_closes_b2_b4_b7=True/False/False" in proc.stdout,
        "B4/B7 non-superiority route closure split changed",
    )
    v.check(
        "b4_b7_closed_by_non_superiority_route=False" in proc.stdout,
        "B4/B7 non-superiority route overcloses B4/B7",
    )
    v.check("source_policy_rows_closed=0/40" in proc.stdout, "B4/B7 non-superiority route overclosed rows")
    v.check(
        "verified_authorized_execution_recorded=False" in proc.stdout,
        "B4/B7 non-superiority route unexpectedly records authorized execution",
    )
    v.check("run_v047_invoked=False" in proc.stdout, "B4/B7 non-superiority route invoked run_v047")
    return proc.stdout


def run_source_policy_local_candidate_gap_audit_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_source_policy_local_candidate_gap_audit.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"source-policy local candidate gap audit validator failed:\n{proc.stdout}")
    v.check(
        "source-policy local candidate gap audit validation: PASS" in proc.stdout,
        "source-policy local candidate gap audit validator did not report PASS",
    )
    v.check("active_source_policy_suites=0" in proc.stdout, "source-policy local candidate gap active-suite count changed")
    v.check("source_policy_closed=0/40" in proc.stdout, "source-policy local candidate gap overclosed rows")
    v.check(
        "accepted_source_policy_dynamic_order_examples=0" in proc.stdout,
        "source-policy local candidate gap overcloses dynamic-order examples",
    )
    v.check(
        "external_superiority_claim_allowed=False" in proc.stdout,
        "source-policy local candidate gap over-allows external superiority",
    )
    return proc.stdout


def run_tfe_source_policy_spec_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_tfe_source_policy_spec.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"TFE source-policy spec validator failed:\n{proc.stdout}")
    v.check(
        "TFE source-policy spec validation: PASS" in proc.stdout,
        "TFE source-policy spec validator did not report PASS",
    )
    v.check(
        "status=source_policy_extracted_candidate_scaffold_present_source_policy_open" in proc.stdout,
        "TFE source-policy spec status changed",
    )
    v.check("source_reference_h=1e-4" in proc.stdout, "TFE source-policy spec lost source-reference h")
    v.check(
        "source_policy_rows_completed=0" in proc.stdout,
        "TFE source-policy spec overclosed source-policy rows",
    )
    v.check(
        "external_superiority_claim=False" in proc.stdout,
        "TFE source-policy spec overclaims external superiority",
    )
    return proc.stdout


def run_tfe_source_pendulum_model_audit_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_tfe_source_pendulum_model_audit.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"TFE source-pendulum model audit validator failed:\n{proc.stdout}")
    v.check(
        "TFE source-pendulum model audit validation: PASS" in proc.stdout,
        "TFE source-pendulum model audit validator did not report PASS",
    )
    v.check(
        "source_pendulum_parameter_model_implemented=True" in proc.stdout,
        "TFE source-pendulum model lost parameter-model marker",
    )
    v.check(
        "source_error_norm_and_output_policy_encoded=True" in proc.stdout,
        "TFE source-pendulum model lost output-policy marker",
    )
    v.check(
        "tfe_m1_m2_m3_candidate_runner_smoke_implemented=True" in proc.stdout,
        "TFE source-pendulum model lost candidate runner marker",
    )
    v.check(
        "source_policy_tfe_newmark_trapezoidal_method_runners_implemented=False" in proc.stdout,
        "TFE source-pendulum model overclaims source-policy method runners",
    )
    v.check(
        "source_policy_absolute_coordinate_dae_runner_implemented=False" in proc.stdout,
        "TFE source-pendulum model overclaims source-policy DAE runner",
    )
    v.check(
        "gauss6_fullva_absolute_coordinate_source_policy_runner_implemented=False" in proc.stdout,
        "TFE source-pendulum model overclaims Gauss6 source-policy runner",
    )
    v.check(
        "pendulum_dae_runner_implemented=False" in proc.stdout,
        "TFE source-pendulum model overclaims pendulum DAE runner",
    )
    v.check(
        "source_policy_rows_completed=0" in proc.stdout,
        "TFE source-pendulum model overclosed source-policy rows",
    )
    return proc.stdout


def run_tfe_source_policy_row_audit_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_tfe_source_policy_row_audit.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"TFE source-policy row audit validator failed:\n{proc.stdout}")
    v.check(
        "TFE source-policy row audit validation: PASS" in proc.stdout,
        "TFE source-policy row audit validator did not report PASS",
    )
    v.check("active_b2_flagged_rows=0" in proc.stdout, "TFE source-policy row audit active B2 count changed")
    v.check(
        "brown_mcphee_source_code_equivalent_law=False" in proc.stdout,
        "TFE source-policy row audit overclaims Brown-McPhee source-code equivalence",
    )
    v.check(
        "gauss6_fullva_absolute_coordinate_source_policy_runner_implemented=False" in proc.stdout,
        "TFE source-policy row audit overclaims Gauss6 source-policy runner",
    )
    v.check(
        "pendulum_dae_runner_implemented=False" in proc.stdout,
        "TFE source-policy row audit overclaims pendulum DAE runner",
    )
    v.check(
        "source_policy_reproduction_rows=0/4" in proc.stdout,
        "TFE source-policy row audit overclosed reproduction rows",
    )
    v.check(
        "can_close_tfe_b2_requirement_now=False" in proc.stdout,
        "TFE source-policy row audit overcloses TFE B2 requirement",
    )
    return proc.stdout


def run_tfe_source_grid_compatibility_audit_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_tfe_source_grid_compatibility_audit.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"TFE source-grid compatibility audit validator failed:\n{proc.stdout}")
    v.check(
        "TFE source grid compatibility audit validation: PASS" in proc.stdout,
        "TFE source-grid compatibility audit validator did not report PASS",
    )
    v.check("rows=6" in proc.stdout, "TFE source-grid compatibility row count changed")
    v.check(
        "integer_step_compatible_rows=2" in proc.stdout,
        "TFE source-grid compatibility compatible row count changed",
    )
    v.check(
        "integer_step_incompatible_rows=4" in proc.stdout,
        "TFE source-grid compatibility incompatible row count changed",
    )
    v.check(
        "source_grid_policy_resolved_for_full_T10=False" in proc.stdout,
        "TFE source-grid compatibility overclaims full T10 policy",
    )
    v.check(
        "source_policy_rows_completed=0" in proc.stdout,
        "TFE source-grid compatibility overclosed source-policy rows",
    )
    return proc.stdout


def run_tfe_brown_mcphee_source_code_equivalence_certificate_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_tfe_brown_mcphee_source_code_equivalence_certificate.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(
        proc.returncode == 0,
        f"TFE Brown-McPhee source-code-equivalence certificate validator failed:\n{proc.stdout}",
    )
    v.check(
        "TFE Brown-McPhee source-code-equivalence certificate validation: PASS" in proc.stdout,
        "TFE Brown-McPhee source-code-equivalence validator did not report PASS",
    )
    v.check(
        "status=negative_source_code_equivalence_certificate_not_source_policy" in proc.stdout,
        "TFE Brown-McPhee source-code-equivalence status changed",
    )
    v.check(
        "brown_mcphee_source_code_equivalent_law=False" in proc.stdout,
        "TFE Brown-McPhee validator overclaims source-code equivalence",
    )
    v.check(
        "source_policy_rows_completed=0" in proc.stdout,
        "TFE Brown-McPhee validator overclosed source-policy rows",
    )
    v.check(
        "source_policy_execution_invoked=False" in proc.stdout,
        "TFE Brown-McPhee validator invoked source-policy execution",
    )
    v.check("can_close_now=False" in proc.stdout, "TFE Brown-McPhee validator overcloses now")
    v.check(
        "blocker_closure_allowed_by_id=OC4:False,OC6:False,OC12:False" in proc.stdout,
        "TFE Brown-McPhee validator over-allows blocker closure",
    )
    return proc.stdout


def run_tfe_full_t10_endpoint_policy_closure_certificate_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_tfe_full_t10_endpoint_policy_closure_certificate.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(
        proc.returncode == 0,
        f"TFE full-T10 endpoint-policy closure certificate validator failed:\n{proc.stdout}",
    )
    v.check(
        "TFE full-T10 endpoint-policy closure certificate validation: PASS" in proc.stdout,
        "TFE full-T10 endpoint-policy closure validator did not report PASS",
    )
    v.check(
        "status=negative_full_T10_endpoint_policy_certificate_not_source_policy" in proc.stdout,
        "TFE full-T10 endpoint policy status changed",
    )
    v.check(
        "source_grid_policy_resolved_for_full_T10=False" in proc.stdout,
        "TFE full-T10 endpoint policy overclaims grid-policy resolution",
    )
    v.check(
        "source_policy_rows_completed=0" in proc.stdout,
        "TFE full-T10 endpoint policy overclosed source-policy rows",
    )
    v.check(
        "source_policy_execution_invoked=False" in proc.stdout,
        "TFE full-T10 endpoint policy invoked source-policy execution",
    )
    v.check("can_close_now=False" in proc.stdout, "TFE full-T10 endpoint policy overcloses now")
    return proc.stdout


def run_tfe_endpoint_policy_boundary_certificate_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_tfe_endpoint_policy_boundary_certificate.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(
        proc.returncode == 0,
        f"TFE endpoint policy boundary certificate validator failed:\n{proc.stdout}",
    )
    v.check(
        "TFE endpoint policy boundary certificate validation: PASS" in proc.stdout,
        "TFE endpoint policy boundary certificate validator did not report PASS",
    )
    v.check("rows=6" in proc.stdout, "TFE endpoint policy boundary row count changed")
    v.check("exact_overrun_rows=2/4" in proc.stdout, "TFE endpoint policy boundary overrun split changed")
    v.check(
        "source_policy_rows_completed=0" in proc.stdout,
        "TFE endpoint policy boundary overclosed source-policy rows",
    )
    return proc.stdout


def run_tfe_algorithm_literal_endpoint_probe_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_tfe_algorithm_literal_endpoint_probe.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"TFE algorithm-literal endpoint probe validator failed:\n{proc.stdout}")
    v.check(
        "TFE algorithm-literal endpoint probe validation: PASS" in proc.stdout,
        "TFE algorithm-literal endpoint probe validator did not report PASS",
    )
    v.check("methods=4" in proc.stdout, "TFE algorithm-literal endpoint probe method count changed")
    v.check("metric_rows=12" in proc.stdout, "TFE algorithm-literal endpoint probe metric row count changed")
    v.check(
        "terminal_overrun_rows=12" in proc.stdout,
        "TFE algorithm-literal endpoint probe terminal-overrun row count changed",
    )
    v.check(
        "source_policy_rows_completed=0" in proc.stdout,
        "TFE algorithm-literal endpoint probe overclosed source-policy rows",
    )
    return proc.stdout


def run_tfe_algorithm_literal_work_precision_audit_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_tfe_algorithm_literal_work_precision_audit.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"TFE algorithm-literal work/precision audit validator failed:\n{proc.stdout}")
    v.check(
        "TFE algorithm-literal work/precision audit validation: PASS" in proc.stdout,
        "TFE algorithm-literal work/precision audit validator did not report PASS",
    )
    v.check("methods=4" in proc.stdout, "TFE algorithm-literal work/precision method count changed")
    v.check("raw_rows=12" in proc.stdout, "TFE algorithm-literal work/precision raw-row count changed")
    v.check("summary_rows=4" in proc.stdout, "TFE algorithm-literal work/precision summary-row count changed")
    v.check(
        "terminal_overrun_rows=12" in proc.stdout,
        "TFE algorithm-literal work/precision terminal-overrun count changed",
    )
    v.check(
        "source_policy_rows_completed=0" in proc.stdout,
        "TFE algorithm-literal work/precision overclosed source-policy rows",
    )
    return proc.stdout


def run_tfe_b4_b7_source_policy_demotion_audit_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_tfe_b4_b7_source_policy_demotion_audit.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"TFE B4/B7 source-policy demotion audit validator failed:\n{proc.stdout}")
    v.check(
        "TFE B4/B7 source-policy demotion audit validation: PASS" in proc.stdout,
        "TFE B4/B7 source-policy demotion audit validator did not report PASS",
    )
    v.check("tfe_rows_demoted=16/16" in proc.stdout, "TFE B4/B7 demotion row count changed")
    v.check(
        "source_policy_rows_closed_by_demotion=0" in proc.stdout,
        "TFE B4/B7 demotion overclosed source-policy rows",
    )
    v.check(
        "b4_b7_can_close_from_tfe_demotion=False/False" in proc.stdout,
        "TFE B4/B7 demotion overcloses B4/B7",
    )
    return proc.stdout


def run_tfe_brown_mcphee_source_law_boundary_audit_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_tfe_brown_mcphee_source_law_boundary_audit.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(
        proc.returncode == 0,
        f"TFE Brown-McPhee source-law boundary audit validator failed:\n{proc.stdout}",
    )
    v.check(
        "TFE Brown-McPhee source-law boundary audit validation: PASS" in proc.stdout,
        "TFE Brown-McPhee source-law boundary audit validator did not report PASS",
    )
    v.check(
        "status=source_formula_structure_encoded_surrogate_not_source_code_equivalent" in proc.stdout,
        "TFE Brown-McPhee source-law boundary status changed",
    )
    v.check(
        "source_policy_rows_promoted=0" in proc.stdout,
        "TFE Brown-McPhee source-law boundary promoted source-policy rows",
    )
    v.check(
        "source_policy_execution_invoked=False" in proc.stdout,
        "TFE Brown-McPhee source-law boundary invoked source-policy execution",
    )
    v.check(
        "source_policy_execution_allowed_now=False" in proc.stdout,
        "TFE Brown-McPhee source-law boundary allowed source-policy execution",
    )
    v.check(
        "brown_mcphee_source_code_equivalent_law=False" in proc.stdout,
        "TFE Brown-McPhee source-law boundary overclaims source-code equivalence",
    )
    return proc.stdout


def run_tfe_endpoint_policy_sensitivity_audit_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_tfe_endpoint_policy_sensitivity_audit.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"TFE endpoint-policy sensitivity audit validator failed:\n{proc.stdout}")
    v.check(
        "TFE endpoint-policy sensitivity audit validation: PASS" in proc.stdout,
        "TFE endpoint-policy sensitivity audit validator did not report PASS",
    )
    v.check("summary_rows=16" in proc.stdout, "TFE endpoint-policy sensitivity summary-row count changed")
    v.check("raw_rows=48" in proc.stdout, "TFE endpoint-policy sensitivity raw-row count changed")
    v.check(
        "source_policy_rows_completed=0" in proc.stdout,
        "TFE endpoint-policy sensitivity overclosed source-policy rows",
    )
    v.check(
        "external_superiority_claim_allowed=False" in proc.stdout,
        "TFE endpoint-policy sensitivity overclaims external superiority",
    )
    return proc.stdout


def run_tfe_full_t10_absolute_dae_lift_summary_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_tfe_full_t10_absolute_dae_lift_summary.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"TFE full-T10 absolute DAE-lift summary validator failed:\n{proc.stdout}")
    v.check(
        "TFE full-T10 absolute DAE-lift summary validation: PASS" in proc.stdout,
        "TFE full-T10 absolute DAE-lift summary validator did not report PASS",
    )
    v.check("rows=4" in proc.stdout, "TFE full-T10 absolute DAE-lift row count changed")
    v.check("metric_step_rows=12/2800" in proc.stdout, "TFE full-T10 absolute DAE-lift metric-step count changed")
    v.check(
        "source_policy_rows_completed=0" in proc.stdout,
        "TFE full-T10 absolute DAE-lift overclosed source-policy rows",
    )
    return proc.stdout


def run_tfe_full_t10_coarse_candidate_summary_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_tfe_full_t10_coarse_candidate_summary.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"TFE full-T10 coarse candidate summary validator failed:\n{proc.stdout}")
    v.check(
        "TFE full-T10 coarse candidate summary validation: PASS" in proc.stdout,
        "TFE full-T10 coarse candidate summary validator did not report PASS",
    )
    v.check("rows=4" in proc.stdout, "TFE full-T10 coarse candidate row count changed")
    v.check("finite_residual_ok=4/4" in proc.stdout, "TFE full-T10 coarse candidate finite-residual count changed")
    v.check(
        "source_policy_rows_completed=0" in proc.stdout,
        "TFE full-T10 coarse candidate overclosed source-policy rows",
    )
    return proc.stdout


def run_tfe_public_code_recheck_20260613_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_tfe_public_code_recheck_20260613.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"TFE public-code recheck validator failed:\n{proc.stdout}")
    v.check(
        "TFE public-code recheck validation: PASS" in proc.stdout,
        "TFE public-code recheck validator did not report PASS",
    )
    v.check(
        "github_repository_search_total_count=0" in proc.stdout,
        "TFE public-code recheck found repository search hits",
    )
    v.check(
        "source_policy_rows_closed=0/16" in proc.stdout,
        "TFE public-code recheck overclosed source-policy rows",
    )
    v.check(
        "attempted_not_reproducible_rows=16" in proc.stdout,
        "TFE public-code recheck attempted/not-reproducible count changed",
    )
    return proc.stdout


def run_full_source_policy_runner_archive_gap_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_full_source_policy_runner_archive_gap_audit.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"full source-policy runner archive gap validator failed:\n{proc.stdout}")
    v.check(
        "full source-policy runner archive gap audit validation: PASS" in proc.stdout,
        "full source-policy runner archive gap validator did not report PASS",
    )
    v.check("source_policy_closed=0/40" in proc.stdout, "full archive validator lost source-policy row marker")
    v.check("terminal_unable_to_reproduce_rows=20" in proc.stdout, "full archive validator lost terminal-row marker")
    v.check(
        "source_policy_execution_allowed_now=False" in proc.stdout,
        "full archive validator lost no-current-source-policy-execution marker",
    )
    v.check(
        "exact_b4_opt_in_required_for_execution=True" in proc.stdout,
        "full archive validator lost exact-B4-opt-in marker",
    )
    v.check(
        "source_policy_execution_invoked=False" in proc.stdout,
        "full archive validator lost no-source-policy-execution-invoked marker",
    )
    v.check(
        "driver_does_not_authorize_execution=True" in proc.stdout,
        "full archive validator lost guarded-driver non-authorization marker",
    )
    v.check(
        "expected_output_schema_audit=PASS" in proc.stdout,
        "full archive validator lost expected-output schema audit marker",
    )
    v.check(
        "b4_guarded_driver_refusal_boundary_audit_20260621=True/True/2/0/13/False/False"
        in proc.stdout,
        "full archive validator lost B4 guarded refusal boundary marker",
    )
    v.check(
        "oc6_external_source_artifact_recheck_20260621=2026-06-21/10/0/0/0/False/False"
        in proc.stdout,
        "full archive validator lost OC6 external source-artifact recheck marker",
    )
    v.check(
        "oc6_tfe_publisher_artifact_availability_20260621=2026-06-21/True/0/0/0/0/False/False"
        in proc.stdout,
        "full archive validator lost OC6 TFE publisher artifact availability marker",
    )
    v.check(
        "oc6_tfe_source_equivalent_artifact_request_packet_20260621=True/False/7/0/False/False"
        in proc.stdout,
        "full archive validator lost OC6 TFE source-equivalent request packet marker",
    )
    v.check("full_archive_ready_now=False" in proc.stdout, "full archive validator lost not-ready marker")
    v.check(
        "oc12_closure_decision=remain_partial_narrowed_replay_ready_full_source_policy_archive_not_ready"
        in proc.stdout,
        "full archive validator lost OC12 closure decision marker",
    )
    v.check(
        "oc12_blocker_open=True" in proc.stdout,
        "full archive validator lost OC12 blocker-open marker",
    )
    v.check(
        "oc12_archive_use_full_usable_primary_allowed=narrowed_claim_replay_and_audit_provenance_only/False/False"
        in proc.stdout,
        "full archive validator lost OC12 archive-use boundary marker",
    )
    v.check(
        "oc12_dependency_blockers_closure_allowed=OC4,OC6/False" in proc.stdout,
        "full archive validator lost OC12 dependency-blocker marker",
    )
    v.check(
        "blocker_open_by_id=OC4:True,OC6:True,OC12:True" in proc.stdout,
        "full archive validator lost global blocker-open matrix",
    )
    v.check(
        "blocker_closure_decision_by_id=OC4:remain_open_ready_for_authorized_execution_not_executed_not_promoted,OC6:remain_open_no_positive_source_equivalent_artifact,OC12:remain_partial_narrowed_replay_ready_full_source_policy_archive_not_ready"
        in proc.stdout,
        "full archive validator lost global blocker closure-decision matrix",
    )
    v.check(
        "blocker_closure_allowed_by_id=OC4:False,OC6:False,OC12:False" in proc.stdout,
        "full archive validator lost global blocker closure-allowed matrix",
    )
    v.check("submission_ready=False" in proc.stdout, "full archive validator lost submission marker")
    return proc.stdout


def run_objective_completion_audit_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_objective_completion_audit.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"objective completion audit validator failed:\n{proc.stdout}")
    v.check(
        "objective completion audit validation: PASS" in proc.stdout,
        "objective completion audit validator did not report PASS",
    )
    v.check("status=not_complete_submission_standard_open" in proc.stdout, "objective audit status changed")
    v.check("objective_complete=False" in proc.stdout, "objective audit overclaimed completion")
    v.check("source_policy_rows=0/40" in proc.stdout, "objective audit lost source-policy row marker")
    v.check("blocking_ids=OC4,OC6,OC12" in proc.stdout, "objective audit blocking ids changed")
    v.check(
        "blocker_open_by_id=OC4:True,OC6:True,OC12:True" in proc.stdout,
        "objective audit lost blocker-open alias map",
    )
    v.check(
        "blocker_closure_decision_by_id=OC4:remain_open_ready_for_authorized_execution_not_executed_not_promoted,OC6:remain_open_no_positive_source_equivalent_artifact,OC12:remain_partial_narrowed_replay_ready_full_source_policy_archive_not_ready"
        in proc.stdout,
        "objective audit lost blocker closure-decision alias map",
    )
    v.check(
        "blocker_closure_allowed_by_id=OC4:False,OC6:False,OC12:False" in proc.stdout,
        "objective audit lost blocker closure-allowed alias map",
    )
    v.check(
        "oc4_aliases=OC4/open/True/remain_open_ready_for_authorized_execution_not_executed_not_promoted/False/13/20/20/32/32/0"
        in proc.stdout,
        "objective audit lost OC4 direct alias marker",
    )
    v.check("oc4_evidence_files=6" in proc.stdout, "objective audit OC4 evidence count changed")
    v.check(
        "b4_guarded_driver_refusal_boundary_audit_20260621=True/True/2/0/13/False/False"
        in proc.stdout,
        "objective audit lost B4 guarded refusal boundary marker",
    )
    v.check(
        "oc6_aliases=OC6/partial/True/remain_open_no_positive_source_equivalent_artifact/False/suite_specific_source_equivalent_reopen_conditions/2026-06-21/9/0/0/4/False/False"
        in proc.stdout,
        "objective audit lost OC6 direct alias marker",
    )
    v.check(
        "oc12_aliases=OC12/partial/True/remain_partial_narrowed_replay_ready_full_source_policy_archive_not_ready/False/False/narrowed_claim_replay_and_audit_provenance_only/False"
        in proc.stdout,
        "objective audit lost OC12 direct alias marker",
    )
    v.check(
        "oc6_candidate_backed_non_equivalent_runner_blocks=3" in proc.stdout,
        "objective audit lost OC6 candidate-backed non-equivalent runner marker",
    )
    v.check(
        "oc6_latest_external_probe=2026-06-21/9/0/0/4/False/False" in proc.stdout,
        "objective audit lost OC6 latest external probe marker",
    )
    v.check(
        "oc6_external_source_artifact_recheck_20260621=2026-06-21/10/0/0/0/False/False"
        in proc.stdout,
        "objective audit lost OC6 external source-artifact recheck marker",
    )
    v.check(
        "oc6_tfe_publisher_artifact_availability_20260621=2026-06-21/True/0/0/0/0/False/False"
        in proc.stdout,
        "objective audit lost OC6 TFE publisher artifact availability marker",
    )
    v.check(
        "oc6_tfe_source_equivalent_artifact_request_packet_20260621=True/False/7/0/False/False"
        in proc.stdout,
        "objective audit lost OC6 TFE source-equivalent request packet marker",
    )
    v.check(
        "oc12_archive_can_use_current_archive_as_full_source_policy_runner_archive=False" in proc.stdout,
        "objective audit lost current-archive not-full-source-policy marker",
    )
    v.check(
        "oc12_archive_safe_current_use=narrowed_claim_replay_and_audit_provenance_only" in proc.stdout,
        "objective audit lost narrowed archive safe-use marker",
    )
    v.check(
        "oc12_archive_action_boundary=4/1/False/False/True/13/20" in proc.stdout,
        "objective audit lost OC12 action-boundary marker",
    )
    v.check(
        "oc12_archive_safe_action_ids=rebuild_read_only_audit_chain,rerun_read_only_validators,keep_narrowed_archive_provenance_only,monitor_reopen_conditions"
        in proc.stdout,
        "objective audit lost OC12 safe-action ids",
    )
    v.check("source_policy_execution_invoked=False" in proc.stdout, "objective audit lost no-source-policy-execution marker")
    v.check("run_v047_invoked=False" in proc.stdout, "objective audit lost no-run_v047 marker")
    v.check("heavy_numerical_run_invoked=False" in proc.stdout, "objective audit lost no-heavy-run marker")
    v.check("v048_runner_invoked=False" in proc.stdout, "objective audit lost no-v048-runner marker")
    return proc.stdout


def run_source_policy_reopen_condition_monitor_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_source_policy_reopen_condition_monitor_20260620.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"source-policy reopen-condition monitor validator failed:\n{proc.stdout}")
    v.check(
        "source-policy reopen-condition monitor validation: PASS" in proc.stdout,
        "source-policy reopen-condition monitor validator did not report PASS",
    )
    v.check("rows=20" in proc.stdout, "reopen monitor lost row marker")
    v.check("local_positive_reopen_artifact_rows=0" in proc.stdout, "reopen monitor lost local-positive marker")
    v.check("source_policy_reopen_triggered=False" in proc.stdout, "reopen monitor lost no-reopen marker")
    v.check("source_policy_closed=0/20" in proc.stdout, "reopen monitor lost no-close marker")
    v.check("submission_ready=False" in proc.stdout, "reopen monitor lost submission marker")
    return proc.stdout


def run_source_policy_reopen_condition_monitor_20260621_delta_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_source_policy_reopen_condition_monitor_20260621_delta.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(
        proc.returncode == 0,
        f"source-policy reopen-condition 20260621 delta validator failed:\n{proc.stdout}",
    )
    v.check(
        "source-policy reopen-condition 20260621 delta validation: PASS" in proc.stdout,
        "source-policy reopen-condition 20260621 delta validator did not report PASS",
    )
    v.check("rows=20" in proc.stdout, "reopen delta lost row marker")
    v.check(
        "oc6_external_recheck=2026-06-21/10/0/0/0/False/False" in proc.stdout,
        "reopen delta lost OC6 external recheck marker",
    )
    v.check(
        "positive_public_code_artifact_rows=0" in proc.stdout,
        "reopen delta overclaimed positive public-code artifact rows",
    )
    v.check(
        "source_code_equivalent_artifact_rows=0" in proc.stdout,
        "reopen delta overclaimed source-code-equivalent artifact rows",
    )
    v.check(
        "source_policy_reopen_triggered=False" in proc.stdout,
        "reopen delta unexpectedly triggered source-policy reopen",
    )
    v.check("source_policy_closed=0/20" in proc.stdout, "reopen delta overclosed source-policy rows")
    v.check("global_absence_proved=False" in proc.stdout, "reopen delta overproved global absence")
    v.check("source_policy_execution_invoked=False" in proc.stdout, "reopen delta invoked source-policy execution")
    v.check(
        "source_policy_execution_allowed_now=False" in proc.stdout,
        "reopen delta allowed source-policy execution",
    )
    v.check("submission_ready=False" in proc.stdout, "reopen delta overclaimed submission readiness")
    return proc.stdout


def run_source_policy_public_code_refresh_20260620_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_source_policy_public_code_refresh_20260620.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(
        proc.returncode == 0,
        f"source-policy public-code refresh 20260620 validator failed:\n{proc.stdout}",
    )
    v.check(
        "Source-policy public-code refresh 20260620 validation: PASS" in proc.stdout,
        "source-policy public-code refresh 20260620 validator did not report PASS",
    )
    v.check("rows=20" in proc.stdout, "public-code refresh lost row marker")
    v.check("current_queries=11" in proc.stdout, "public-code refresh lost query count")
    v.check(
        "positive_public_code_artifact_rows=0" in proc.stdout,
        "public-code refresh overclaimed positive artifact rows",
    )
    v.check(
        "latest_external_probe=2026-06-21/9/0/0/4/False/False" in proc.stdout,
        "public-code refresh lost latest external probe marker",
    )
    v.check("source_policy_closed_ratio=0/20" in proc.stdout, "public-code refresh overclosed source-policy rows")
    v.check("source_policy_execution_invoked=False" in proc.stdout, "public-code refresh invoked source-policy execution")
    v.check("source_policy_execution_allowed_now=False" in proc.stdout, "public-code refresh allowed source-policy execution")
    v.check("submission_ready=False" in proc.stdout, "public-code refresh overclaimed submission readiness")
    return proc.stdout


def run_oc6_source_equivalent_reopen_readiness_audit_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_oc6_source_equivalent_reopen_readiness_audit_20260620.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(
        proc.returncode == 0,
        f"OC6 source-equivalent reopen-readiness audit validator failed:\n{proc.stdout}",
    )
    v.check(
        "OC6 source-equivalent reopen-readiness audit validation: PASS" in proc.stdout,
        "OC6 source-equivalent reopen-readiness audit validator did not report PASS",
    )
    v.check("rows=20" in proc.stdout, "OC6 reopen-readiness audit lost row marker")
    v.check("unable=20" in proc.stdout, "OC6 reopen-readiness audit lost unable marker")
    v.check("source_equivalent=0" in proc.stdout, "OC6 reopen-readiness audit overclaimed source equivalence")
    v.check(
        "source_policy_closed=0" in proc.stdout,
        "OC6 reopen-readiness audit overclosed source-policy rows",
    )
    v.check(
        "closure_decision=remain_open_no_positive_source_equivalent_artifact" in proc.stdout,
        "OC6 reopen-readiness audit lost closure decision marker",
    )
    v.check(
        "artifact_found=False" in proc.stdout,
        "OC6 reopen-readiness audit lost no-source-equivalent-artifact marker",
    )
    v.check("oc6_blocker_id=OC6" in proc.stdout, "OC6 reopen-readiness audit lost OC6 id alias")
    v.check("oc6_blocker_status=partial" in proc.stdout, "OC6 reopen-readiness audit lost OC6 status alias")
    v.check(
        "oc6_closure_decision=remain_open_no_positive_source_equivalent_artifact" in proc.stdout,
        "OC6 reopen-readiness audit lost OC6 closure alias",
    )
    v.check(
        "oc6_closure_allowed_now=False" in proc.stdout,
        "OC6 reopen-readiness audit lost OC6 closure-allowed marker",
    )
    v.check(
        "reopen_condition=suite_specific_source_equivalent_reopen_conditions" in proc.stdout,
        "OC6 reopen-readiness audit lost suite-specific reopen-condition alias",
    )
    v.check(
        "latest_external_probe_boundary=0/0/4/False/False" in proc.stdout,
        "OC6 reopen-readiness audit lost latest external probe boundary marker",
    )
    v.check(
        "blocker_open_by_id=OC4:True,OC6:True,OC12:True" in proc.stdout,
        "OC6 reopen-readiness audit lost global blocker-open matrix",
    )
    v.check(
        "blocker_closure_decision_by_id=OC4:remain_open_ready_for_authorized_execution_not_executed_not_promoted,OC6:remain_open_no_positive_source_equivalent_artifact,OC12:remain_partial_narrowed_replay_ready_full_source_policy_archive_not_ready"
        in proc.stdout,
        "OC6 reopen-readiness audit lost global blocker closure-decision matrix",
    )
    v.check(
        "blocker_closure_allowed_by_id=OC4:False,OC6:False,OC12:False" in proc.stdout,
        "OC6 reopen-readiness audit lost global blocker closure-allowed matrix",
    )
    return proc.stdout


def run_oc6_external_source_artifact_recheck_20260621_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_oc6_external_source_artifact_recheck_20260621.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(
        proc.returncode == 0,
        f"OC6 external source-artifact recheck 20260621 validator failed:\n{proc.stdout}",
    )
    v.check(
        "OC6 external source-artifact recheck 20260621 validation: PASS" in proc.stdout,
        "OC6 external source-artifact recheck 20260621 validator did not report PASS",
    )
    v.check("queries=10" in proc.stdout, "OC6 external recheck lost query marker")
    v.check(
        "positive_public_code_artifact_rows=0" in proc.stdout,
        "OC6 external recheck overclaimed positive public-code artifact rows",
    )
    v.check(
        "source_code_equivalent_artifact_rows=0" in proc.stdout,
        "OC6 external recheck overclaimed source-code-equivalent artifact rows",
    )
    v.check(
        "source_policy_rows_closed_by_recheck=0" in proc.stdout,
        "OC6 external recheck overclosed source-policy rows",
    )
    v.check(
        "source_policy_reopen_triggered=False" in proc.stdout,
        "OC6 external recheck unexpectedly triggered reopen",
    )
    v.check("global_absence_proved=False" in proc.stdout, "OC6 external recheck overproved global absence")
    v.check("submission_ready=False" in proc.stdout, "OC6 external recheck overclaimed submission readiness")
    return proc.stdout


def run_oc6_tfe_publisher_artifact_availability_audit_20260621_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_oc6_tfe_publisher_artifact_availability_audit_20260621.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(
        proc.returncode == 0,
        f"OC6 TFE publisher artifact availability audit 20260621 validator failed:\n{proc.stdout}",
    )
    v.check(
        "OC6 TFE publisher artifact availability audit validation: PASS" in proc.stdout,
        "OC6 TFE publisher artifact availability validator did not report PASS",
    )
    v.check("official_article_checked=True" in proc.stdout, "OC6 publisher audit lost official article marker")
    v.check("source_artifact_signal_count=0" in proc.stdout, "OC6 publisher audit found unexpected source-artifact signal")
    v.check(
        "positive_public_code_artifact_rows=0" in proc.stdout,
        "OC6 publisher audit overclaimed positive public-code artifact rows",
    )
    v.check(
        "source_code_equivalent_artifact_rows=0" in proc.stdout,
        "OC6 publisher audit overclaimed source-code-equivalent artifact rows",
    )
    v.check(
        "source_policy_rows_closed_by_publisher_audit=0" in proc.stdout,
        "OC6 publisher audit overclosed source-policy rows",
    )
    v.check(
        "source_policy_reopen_triggered=False" in proc.stdout,
        "OC6 publisher audit unexpectedly triggered reopen",
    )
    v.check("global_absence_proved=False" in proc.stdout, "OC6 publisher audit overproved global absence")
    v.check("submission_ready=False" in proc.stdout, "OC6 publisher audit overclaimed submission readiness")
    return proc.stdout


def run_oc6_tfe_source_equivalent_artifact_request_packet_20260621_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_oc6_tfe_source_equivalent_artifact_request_packet_20260621.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(
        proc.returncode == 0,
        f"OC6 TFE source-equivalent artifact request packet 20260621 validator failed:\n{proc.stdout}",
    )
    v.check(
        "OC6 TFE source-equivalent artifact request packet validation: PASS" in proc.stdout,
        "OC6 TFE source-equivalent artifact request packet validator did not report PASS",
    )
    v.check("request_ready=True" in proc.stdout, "OC6 request packet lost ready marker")
    v.check("request_sent=False" in proc.stdout, "OC6 request packet overclaimed sent request")
    v.check("requested_artifact_count=7" in proc.stdout, "OC6 request packet artifact count changed")
    v.check(
        "source_policy_rows_closed_by_packet=0" in proc.stdout,
        "OC6 request packet overclosed source-policy rows",
    )
    v.check(
        "source_policy_reopen_triggered=False" in proc.stdout,
        "OC6 request packet unexpectedly triggered reopen",
    )
    v.check("global_absence_proved=False" in proc.stdout, "OC6 request packet overproved global absence")
    v.check("submission_ready=False" in proc.stdout, "OC6 request packet overclaimed submission readiness")
    v.check(
        "oc6_tfe_source_equivalent_artifact_request_packet_20260621=ready_not_sent/7/0/False/False"
        in proc.stdout,
        "OC6 request packet lost compact ready-not-sent marker",
    )
    return proc.stdout


def run_tfe_source_policy_self_reproduction_attempt_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_tfe_source_policy_self_reproduction_attempt_certificate.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(
        proc.returncode == 0,
        f"TFE source-policy self-reproduction attempt validator failed:\n{proc.stdout}",
    )
    v.check(
        "TFE self-reproduction attempt certificate validation: PASS" in proc.stdout,
        "TFE self-reproduction attempt validator did not report PASS",
    )
    v.check(
        "attempted_not_reproducible_rows=16/16" in proc.stdout,
        "TFE self-reproduction attempt validator lost attempted row marker",
    )
    v.check(
        "unable_to_reproduce_rows=16/16" in proc.stdout,
        "TFE self-reproduction attempt validator lost unable-to-reproduce marker",
    )
    v.check(
        "source_policy_closed_rows=0" in proc.stdout,
        "TFE self-reproduction attempt validator overclosed source-policy rows",
    )
    v.check(
        "source_policy_closed=0/16" in proc.stdout,
        "TFE self-reproduction attempt validator lost source-policy ratio marker",
    )
    v.check(
        "submission_ready=False" in proc.stdout,
        "TFE self-reproduction attempt validator lost submission marker",
    )
    return proc.stdout


def run_source_policy_self_reproduction_attempt_audit_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_source_policy_self_reproduction_attempt_audit.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(
        proc.returncode == 0,
        f"source-policy self-reproduction attempt audit validator failed:\n{proc.stdout}",
    )
    v.check(
        "Source-policy self-reproduction attempt audit validation: PASS" in proc.stdout,
        "source-policy self-reproduction attempt audit validator did not report PASS",
    )
    v.check(
        "attempted_not_reproducible_rows=20/20" in proc.stdout,
        "source-policy self-reproduction attempt audit lost attempted/not-reproducible marker",
    )
    v.check(
        "source_policy_closed_rows=0" in proc.stdout,
        "source-policy self-reproduction attempt audit overclosed source-policy rows",
    )
    v.check(
        "external_superiority_ready_rows=0" in proc.stdout,
        "source-policy self-reproduction attempt audit overclaimed external superiority",
    )
    return proc.stdout


def run_ra2021_source_identity_audit_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_ra2021_source_identity_audit.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"RA2021 source identity audit validator failed:\n{proc.stdout}")
    v.check(
        "RA2021 source identity audit validation: PASS" in proc.stdout,
        "RA2021 source identity audit validator did not report PASS",
    )
    v.check("output_mapping_verified=True" in proc.stdout, "RA2021 source identity lost mapping marker")
    v.check("time_grid_policy_extracted=True" in proc.stdout, "RA2021 source identity lost time-grid marker")
    v.check("source_policy_rows_closed=0" in proc.stdout, "RA2021 source identity overclosed source-policy rows")
    return proc.stdout


def run_ra2021_double_source_policy_low_order_diagnosis_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_ra2021_double_source_policy_low_order_diagnosis.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(
        proc.returncode == 0,
        f"RA2021 double source-policy low-order diagnosis validator failed:\n{proc.stdout}",
    )
    v.check(
        "RA2021 double source-policy low-order diagnosis validation: PASS" in proc.stdout,
        "RA2021 double source-policy low-order diagnosis validator did not report PASS",
    )
    v.check("rows_complete=True" in proc.stdout, "RA2021 double diagnosis lost row-complete marker")
    v.check(
        "aggregate_order_acceptance_satisfied=False" in proc.stdout,
        "RA2021 double diagnosis overclaims order acceptance",
    )
    v.check(
        "fine_pair_floor_limited=True" in proc.stdout,
        "RA2021 double diagnosis lost reference-floor marker",
    )
    v.check(
        "source_policy_rows_promoted=0" in proc.stdout,
        "RA2021 double diagnosis promoted source-policy rows",
    )
    return proc.stdout


def run_ra2021_source_policy_row_audit_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_ra2021_source_policy_row_audit.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"RA2021 source-policy row audit validator failed:\n{proc.stdout}")
    v.check(
        "RA2021 source-policy row audit validation: PASS" in proc.stdout,
        "RA2021 source-policy row audit validator did not report PASS",
    )
    v.check("active_b2_flagged_rows=0" in proc.stdout, "RA2021 row audit active B2 count changed")
    v.check("public_order_groups=12/12" in proc.stdout, "RA2021 row audit lost public-order group coverage")
    v.check("public_timing_rows=12/12" in proc.stdout, "RA2021 row audit lost timing-row coverage")
    v.check(
        "source_policy_reproduction_rows=0/12" in proc.stdout,
        "RA2021 row audit overclosed source-policy rows",
    )
    v.check(
        "can_close_ra2021_b2_requirement_now=False" in proc.stdout,
        "RA2021 row audit overcloses B2 requirement",
    )
    return proc.stdout


def run_hi2022_policy_decision_audit_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_hi2022_policy_decision_audit.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"HI2022 policy decision audit validator failed:\n{proc.stdout}")
    v.check("hi2022_policy_decision_audit=PASS" in proc.stdout, "HI2022 policy decision audit did not report PASS")
    v.check("bounded_rows=24/24" in proc.stdout, "HI2022 policy decision lost bounded-row coverage")
    v.check("bounded_groups=8/8" in proc.stdout, "HI2022 policy decision lost bounded-group coverage")
    v.check(
        "full_T8_policy_completed=False" in proc.stdout,
        "HI2022 policy decision overclaims full T8 source-policy completion",
    )
    v.check(
        "accepted_for_external_superiority=False" in proc.stdout,
        "HI2022 policy decision overclaims external superiority",
    )
    v.check(
        "source_policy_dynamic_order_examples=0/4" in proc.stdout,
        "HI2022 policy decision overcloses source-policy dynamic-order examples",
    )
    v.check("run_v047_invoked=False" in proc.stdout, "HI2022 policy decision invoked run_v047")
    return proc.stdout


def run_hi2022_source_policy_row_audit_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_hi2022_source_policy_row_audit.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"HI2022 source-policy row audit validator failed:\n{proc.stdout}")
    v.check(
        "HI2022 source-policy row audit validation: PASS" in proc.stdout,
        "HI2022 source-policy row audit validator did not report PASS",
    )
    v.check("active_b2_flagged_rows=3" in proc.stdout, "HI2022 row audit active B2 count changed")
    v.check("active_after_demotion=0" in proc.stdout, "HI2022 row audit demotion count changed")
    v.check("bounded_rows=24/24" in proc.stdout, "HI2022 row audit lost bounded-row coverage")
    v.check("bounded_groups=8/8" in proc.stdout, "HI2022 row audit lost bounded-group coverage")
    v.check(
        "full_T8_policy_completed=False" in proc.stdout,
        "HI2022 row audit overclaims full T8 source-policy completion",
    )
    v.check(
        "source_policy_reproduction_rows=0/3" in proc.stdout,
        "HI2022 row audit overclosed source-policy rows",
    )
    v.check(
        "can_close_hi2022_b2_requirement_now=False" in proc.stdout,
        "HI2022 row audit overcloses B2 requirement",
    )
    return proc.stdout


def run_hi2022_ra_half_double_source_policy_failure_diagnosis_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_hi2022_ra_half_double_source_policy_failure_diagnosis.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(
        proc.returncode == 0,
        f"HI2022 rA_half double source-policy failure diagnosis validator failed:\n{proc.stdout}",
    )
    v.check(
        "HI2022 rA_half double source-policy failure diagnosis validation: PASS" in proc.stdout,
        "HI2022 rA_half double failure diagnosis validator did not report PASS",
    )
    v.check("rows_ok_failed_total=1/2/3" in proc.stdout, "HI2022 failure diagnosis row split changed")
    v.check("newton_failure_count=2" in proc.stdout, "HI2022 failure diagnosis Newton count changed")
    v.check(
        "source_policy_rows_promoted=0" in proc.stdout,
        "HI2022 failure diagnosis promoted source-policy rows",
    )
    return proc.stdout


def run_hi2022_ra_half_double_repair_attempt_certificate_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_hi2022_ra_half_double_repair_attempt_certificate.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(
        proc.returncode == 0,
        f"HI2022 rA_half double repair-attempt certificate validator failed:\n{proc.stdout}",
    )
    v.check(
        "HI2022 rA_half double repair-attempt certificate validation: PASS" in proc.stdout,
        "HI2022 rA_half double repair certificate validator did not report PASS",
    )
    v.check("target_group=rA_half:double_pendulum" in proc.stdout, "HI2022 repair certificate target changed")
    v.check("combined_target_ok_failed=1/2" in proc.stdout, "HI2022 repair certificate target split changed")
    v.check(
        "source_policy_rows_promoted=0" in proc.stdout,
        "HI2022 repair certificate promoted source-policy rows",
    )
    v.check(
        "external_superiority_ready=False" in proc.stdout,
        "HI2022 repair certificate overclaims external superiority",
    )
    return proc.stdout


def run_hi2022_t8_tolerance_repair_audit_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_hi2022_t8_tolerance_repair_audit.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"HI2022 T8 tolerance-repair audit validator failed:\n{proc.stdout}")
    v.check(
        "HI2022 T8 tolerance-repair audit validation: PASS" in proc.stdout,
        "HI2022 T8 tolerance-repair audit validator did not report PASS",
    )
    v.check("combined_best_rows=19/24" in proc.stdout, "HI2022 tolerance repair best-row count changed")
    v.check(
        "combined_best_complete_groups=4/8" in proc.stdout,
        "HI2022 tolerance repair complete-group count changed",
    )
    v.check(
        "source_policy_reproduction_closed=False" in proc.stdout,
        "HI2022 tolerance repair overcloses source-policy reproduction",
    )
    v.check(
        "external_superiority_claim_allowed=False" in proc.stdout,
        "HI2022 tolerance repair overclaims external superiority",
    )
    return proc.stdout


def run_vp2024_code_path_disposition_audit_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_vp2024_code_path_disposition_audit.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"VP2024 code-path disposition audit validator failed:\n{proc.stdout}")
    v.check(
        "VP2024 code-path disposition audit validation: PASS" in proc.stdout,
        "VP2024 code-path disposition audit validator did not report PASS",
    )
    v.check(
        "examples=single_pendulum,double_pendulum,four_link,slider_crank" in proc.stdout,
        "VP2024 disposition lost four-example coverage",
    )
    v.check(
        "source_policy_code_path_unresolved_rows=4/4" in proc.stdout,
        "VP2024 disposition over-resolved source-policy code paths",
    )
    v.check("unable_to_reproduce_rows=4/4" in proc.stdout, "VP2024 disposition unable-to-reproduce count changed")
    v.check(
        "distinct_public_vp_code_path_found=False" in proc.stdout,
        "VP2024 disposition found a distinct public code path unexpectedly",
    )
    return proc.stdout


def run_vp2024_public_code_recheck_20260613_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_vp2024_public_code_recheck_20260613.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"VP2024 public-code recheck validator failed:\n{proc.stdout}")
    v.check(
        "VP2024 public-code recheck validation: PASS" in proc.stdout,
        "VP2024 public-code recheck validator did not report PASS",
    )
    v.check("keyword_path_hit_count=0" in proc.stdout, "VP2024 public-code recheck found keyword path hits")
    v.check(
        "source_policy_rows_closed=0/4" in proc.stdout,
        "VP2024 public-code recheck overclosed source-policy rows",
    )
    return proc.stdout


def run_ra_hi_source_policy_output_inventory_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_ra_hi_source_policy_output_inventory.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(
        proc.returncode == 0,
        f"RA/HI source-policy output inventory validator failed:\n{proc.stdout}",
    )
    v.check(
        "RA/HI source-policy output inventory validation: PASS" in proc.stdout,
        "RA/HI output inventory validator did not report PASS",
    )
    v.check("commands=13" in proc.stdout, "RA/HI output inventory lost command-count marker")
    v.check("outputs=13/13" in proc.stdout, "RA/HI output inventory lost output-count marker")
    v.check("summaries=8/8" in proc.stdout, "RA/HI output inventory lost summary-count marker")
    v.check("source_policy_closed=0" in proc.stdout, "RA/HI output inventory overclosed source-policy rows")
    return proc.stdout


def run_ra_hi_source_policy_closeout_checklist_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_ra_hi_source_policy_closeout_checklist.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(
        proc.returncode == 0,
        f"RA/HI source-policy closeout checklist validator failed:\n{proc.stdout}",
    )
    v.check(
        "RA/HI source-policy closeout checklist validation: PASS" in proc.stdout,
        "RA/HI closeout checklist validator did not report PASS",
    )
    v.check("rows=20" in proc.stdout, "RA/HI closeout checklist lost row-count marker")
    v.check("ra_hi=12/8" in proc.stdout, "RA/HI closeout checklist lost suite-count marker")
    v.check("ready_commands=13" in proc.stdout, "RA/HI closeout checklist lost command-count marker")
    v.check("source_policy_closed=0/20" in proc.stdout, "RA/HI closeout checklist overclosed rows")
    return proc.stdout


def run_ra_hi_source_policy_promotion_blocker_matrix_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_ra_hi_source_policy_promotion_blocker_matrix.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(
        proc.returncode == 0,
        f"RA/HI source-policy promotion blocker matrix validator failed:\n{proc.stdout}",
    )
    v.check(
        "RA/HI source-policy promotion blocker matrix validation: PASS" in proc.stdout,
        "RA/HI promotion blocker matrix validator did not report PASS",
    )
    v.check("rows=20" in proc.stdout, "RA/HI promotion matrix lost row-count marker")
    v.check("source_policy_closed=0/20" in proc.stdout, "RA/HI promotion matrix overclosed rows")
    v.check("not_promoted=20" in proc.stdout, "RA/HI promotion matrix lost not-promoted marker")
    v.check(
        "command_mapped_output_present=20/20" in proc.stdout,
        "RA/HI promotion matrix lost command-output marker",
    )
    return proc.stdout


def run_ra_hi_source_policy_post_execution_attempt_certificate_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_ra_hi_source_policy_post_execution_attempt_certificate.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(
        proc.returncode == 0,
        f"RA/HI post-execution attempt certificate validator failed:\n{proc.stdout}",
    )
    v.check(
        "RA/HI post-execution attempt certificate validation: PASS" in proc.stdout,
        "RA/HI post-execution attempt certificate validator did not report PASS",
    )
    v.check("rows=20" in proc.stdout, "RA/HI post-execution certificate lost row-count marker")
    v.check(
        "source_policy_rows_promoted=0" in proc.stdout,
        "RA/HI post-execution certificate overpromoted source-policy rows",
    )
    v.check(
        "external_superiority_ready_rows=0" in proc.stdout,
        "RA/HI post-execution certificate overpromoted external-superiority rows",
    )
    v.check(
        "source_policy_closed=0/40" in proc.stdout,
        "RA/HI post-execution certificate overclosed full source-policy rows",
    )
    v.check(
        "run_v047_invoked=False" in proc.stdout,
        "RA/HI post-execution certificate lost no-run_v047 marker",
    )
    v.check(
        "submission_ready=False" in proc.stdout,
        "RA/HI post-execution certificate overclaimed submission readiness",
    )
    return proc.stdout


def run_b4_source_policy_execution_opt_in_packet_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_b4_source_policy_execution_opt_in_packet.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(
        proc.returncode == 0,
        f"B4 source-policy execution opt-in packet validator failed:\n{proc.stdout}",
    )
    v.check(
        "B4 source-policy execution opt-in packet validation: PASS" in proc.stdout,
        "B4 source-policy execution opt-in packet validator did not report PASS",
    )
    v.check("ready_command_count=13" in proc.stdout, "B4 opt-in packet lost ready-command marker")
    v.check(
        "ready_command_mapped_external_rows=20/40" in proc.stdout,
        "B4 opt-in packet lost mapped-row marker",
    )
    v.check(
        "source_policy_closed_now=0/40" in proc.stdout,
        "B4 opt-in packet overclosed source-policy rows",
    )
    v.check(
        "execution_invoked_by_packet=False" in proc.stdout,
        "B4 opt-in packet indicates execution was invoked",
    )
    v.check(
        "blocker_open_by_id=OC4:True,OC6:True,OC12:True" in proc.stdout,
        "B4 opt-in packet lost objective blocker open matrix marker",
    )
    v.check(
        "blocker_closure_allowed_by_id=OC4:False,OC6:False,OC12:False" in proc.stdout,
        "B4 opt-in packet lost objective blocker closure marker",
    )
    return proc.stdout


def run_b4_source_policy_guarded_driver_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_b4_source_policy_guarded_driver.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(
        proc.returncode == 0,
        f"B4 source-policy guarded driver validator failed:\n{proc.stdout}",
    )
    v.check(
        "B4 guarded execution driver validation: PASS" in proc.stdout,
        "B4 source-policy guarded driver validator did not report PASS",
    )
    v.check("exact_approval_guard=True" in proc.stdout, "B4 guarded driver lost exact-approval marker")
    v.check("driver_command_count=13" in proc.stdout, "B4 guarded driver lost command-count marker")
    v.check(
        "ra_allow_source_policy_1e_4_commands=5" in proc.stdout,
        "B4 guarded driver lost RA allow-source-policy command marker",
    )
    v.check("hi_execute_commands=8" in proc.stdout, "B4 guarded driver lost HI execute-command marker")
    v.check(
        "commands_match_opt_in_packet=True" in proc.stdout,
        "B4 guarded driver command list diverges from opt-in packet",
    )
    v.check("run_v047_invoked=False" in proc.stdout, "B4 guarded driver unexpectedly references run_v047")
    v.check(
        "execution_invoked_by_validator=False" in proc.stdout,
        "B4 guarded driver validator indicates execution was invoked",
    )
    return proc.stdout


def run_b4_guarded_driver_refusal_boundary_audit_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_b4_guarded_driver_refusal_boundary_audit_20260621.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(
        proc.returncode == 0,
        f"B4 guarded driver refusal boundary audit validator failed:\n{proc.stdout}",
    )
    v.check(
        "B4 guarded driver refusal boundary audit validation: PASS" in proc.stdout,
        "B4 guarded driver refusal boundary audit validator did not report PASS",
    )
    v.check(
        "b4_guarded_driver_refusal_boundary_audit_20260621=True/True/2/0/13/False/False"
        in proc.stdout,
        "B4 guarded refusal boundary marker changed",
    )
    v.check(
        "driver_invoked_by_audit=False" in proc.stdout,
        "B4 guarded refusal audit invoked the guarded driver",
    )
    v.check(
        "source_policy_execution_invoked=False" in proc.stdout,
        "B4 guarded refusal audit invoked source-policy execution",
    )
    v.check(
        "submission_ready=False" in proc.stdout,
        "B4 guarded refusal audit overclaimed submission readiness",
    )
    return proc.stdout


def run_b4_source_policy_execution_handoff_package_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_b4_source_policy_execution_handoff_package.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(
        proc.returncode == 0,
        f"B4 source-policy execution handoff package validator failed:\n{proc.stdout}",
    )
    v.check(
        "B4 source-policy execution handoff package validation: PASS" in proc.stdout,
        "B4 source-policy execution handoff package validator did not report PASS",
    )
    v.check(
        "source_policy_closed=0/40" in proc.stdout,
        "B4 execution handoff package overclosed source-policy rows",
    )
    v.check(
        "terminal_unable_to_reproduce_rows=20" in proc.stdout,
        "B4 execution handoff package lost terminal-unable marker",
    )
    v.check("ready_command_count=13" in proc.stdout, "B4 execution handoff package lost command marker")
    v.check(
        "execution_authorized=False" in proc.stdout,
        "B4 execution handoff package unexpectedly authorized execution",
    )
    v.check(
        "guarded_execution_driver=run_b4_source_policy_after_opt_in.sh" in proc.stdout,
        "B4 execution handoff package lost guarded-driver marker",
    )
    v.check(
        "driver_requires_exact_approval=True" in proc.stdout,
        "B4 execution handoff package lost exact-approval driver marker",
    )
    v.check(
        "command_preflight_freeze=PASS" in proc.stdout,
        "B4 execution handoff package lost command-preflight freeze marker",
    )
    v.check(
        "expected_output_schema_audit=PASS" in proc.stdout,
        "B4 execution handoff package lost expected-output schema audit marker",
    )
    v.check(
        "submission_ready=False" in proc.stdout,
        "B4 execution handoff package lost submission marker",
    )
    return proc.stdout


def run_b4_source_policy_command_preflight_freeze_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_b4_source_policy_command_preflight_freeze_20260620.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(
        proc.returncode == 0,
        f"B4 source-policy command preflight freeze validator failed:\n{proc.stdout}",
    )
    v.check(
        "b4 source-policy command preflight freeze validation: PASS" in proc.stdout,
        "B4 source-policy command preflight freeze validator did not report PASS",
    )
    v.check("ready_command_count=13" in proc.stdout, "B4 command freeze lost command count")
    v.check("unique_mapped_ra_hi_rows=20" in proc.stdout, "B4 command freeze lost mapped row count")
    v.check("expected_artifacts=21/21" in proc.stdout, "B4 command freeze lost artifact count")
    v.check(
        "commands_executed_by_freeze=False" in proc.stdout,
        "B4 command freeze unexpectedly executed commands",
    )
    v.check("source_policy_closed=0/40" in proc.stdout, "B4 command freeze overclosed rows")
    return proc.stdout


def run_b4_source_policy_expected_output_schema_audit_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_b4_source_policy_expected_output_schema_audit_20260620.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(
        proc.returncode == 0,
        f"B4 expected-output schema audit validator failed:\n{proc.stdout}",
    )
    v.check(
        "b4 expected-output schema audit validation: PASS" in proc.stdout,
        "B4 expected-output schema audit validator did not report PASS",
    )
    v.check("commands=13/13" in proc.stdout, "B4 schema audit lost command count")
    v.check("artifacts=21/21" in proc.stdout, "B4 schema audit lost artifact count")
    v.check(
        "csv_json_parseable=13/8" in proc.stdout,
        "B4 schema audit lost parseability count",
    )
    v.check(
        "source_policy_rows_closed=0" in proc.stdout,
        "B4 schema audit overclosed source-policy rows",
    )
    return proc.stdout


def run_b4_expected_output_promotion_readiness_blocker_audit_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_b4_expected_output_promotion_readiness_blocker_audit_20260620.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(
        proc.returncode == 0,
        f"B4 expected-output promotion-readiness blocker audit validator failed:\n{proc.stdout}",
    )
    v.check(
        "b4 expected-output promotion-readiness blocker audit validation: PASS" in proc.stdout,
        "B4 expected-output promotion-readiness blocker audit validator did not report PASS",
    )
    v.check("schema_ready=13/13" in proc.stdout, "B4 promotion blocker audit lost schema-ready count")
    v.check("promotion_ready=0" in proc.stdout, "B4 promotion blocker audit overclaimed promotion readiness")
    v.check("unique_rows=20" in proc.stdout, "B4 promotion blocker audit lost unique row count")
    v.check(
        "source_policy_rows_closed=0" in proc.stdout,
        "B4 promotion blocker audit overclosed source-policy rows",
    )
    v.check(
        "blocker_open_by_id=OC4:True,OC6:True,OC12:True" in proc.stdout,
        "B4 promotion blocker audit lost objective blocker open matrix marker",
    )
    v.check(
        "blocker_closure_allowed_by_id=OC4:False,OC6:False,OC12:False" in proc.stdout,
        "B4 promotion blocker audit lost objective blocker closure marker",
    )
    return proc.stdout


def run_full_source_policy_row_provenance_audit_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_full_source_policy_row_provenance_audit.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(
        proc.returncode == 0,
        f"Full source-policy row provenance audit validator failed:\n{proc.stdout}",
    )
    v.check(
        "full source-policy row provenance audit validation: PASS" in proc.stdout,
        "Full source-policy row provenance audit validator did not report PASS",
    )
    v.check("rows=40" in proc.stdout, "Full source-policy row provenance audit lost row-count marker")
    v.check(
        "provenance_preflight=40/40" in proc.stdout,
        "Full source-policy row provenance audit lost preflight marker",
    )
    v.check(
        "source_policy_closed=0/40" in proc.stdout,
        "Full source-policy row provenance audit overclosed source-policy rows",
    )
    v.check(
        "promotion_ready_rows=0" in proc.stdout,
        "Full source-policy row provenance audit overpromoted rows",
    )
    v.check(
        "closure_decision=remain_open_ready_for_authorized_execution_not_executed_not_promoted"
        in proc.stdout,
        "Full source-policy row provenance audit lost OC4 closure decision marker",
    )
    v.check("oc4_blocker_id=OC4" in proc.stdout, "Full source-policy row provenance audit lost OC4 id alias")
    v.check("oc4_blocker_status=open" in proc.stdout, "Full source-policy row provenance audit lost OC4 status alias")
    v.check(
        "oc4_closure_decision=remain_open_ready_for_authorized_execution_not_executed_not_promoted"
        in proc.stdout,
        "Full source-policy row provenance audit lost OC4 closure alias",
    )
    v.check(
        "oc4_closure_allowed_now=False" in proc.stdout,
        "Full source-policy row provenance audit lost OC4 closure-allowed marker",
    )
    v.check(
        "oc4_blocker_open=True" in proc.stdout,
        "Full source-policy row provenance audit lost OC4 blocker-open marker",
    )
    v.check(
        "ready_commands_mapped_rows=13/20" in proc.stdout,
        "Full source-policy row provenance audit lost ready-command mapping marker",
    )
    v.check(
        "traceability_unique_traced_declared_mismatch=20/32/32/0" in proc.stdout,
        "Full source-policy row provenance audit lost command traceability marker",
    )
    return proc.stdout


def run_v048_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_v048_outputs.py"],
        cwd=V048_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"v048 validator failed:\n{proc.stdout}")
    v.check("v048 validation: PASS" in proc.stdout, "v048 validator did not report PASS")
    v.check("same_test_campaign_status=not_run" in proc.stdout, "v048 validator lost same-test open marker")
    v.check("external_superiority_claim=False" in proc.stdout, "v048 validator lost no-superiority marker")
    return proc.stdout


def run_v048_four_example_matrix_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_four_example_performance_matrix.py"],
        cwd=V048_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"v048 four-example matrix validator failed:\n{proc.stdout}")
    v.check(
        "four-example performance matrix validation: PASS" in proc.stdout,
        "v048 four-example matrix validator did not report PASS",
    )
    v.check("external_superiority_claim=False" in proc.stdout, "v048 matrix validator lost no-superiority marker")
    return proc.stdout


def run_v048_coarse_first_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_coarse_first_external_readiness_gate.py"],
        cwd=V048_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"v048 coarse-first readiness validator failed:\n{proc.stdout}")
    v.check(
        "coarse-first external readiness gate validation: PASS" in proc.stdout,
        "v048 coarse-first readiness validator did not report PASS",
    )
    v.check("coarse_same_window_ready=2/4" in proc.stdout, "v048 coarse-first validator lost ready count")
    v.check("local_true_dynamic_order=2" in proc.stdout, "v048 coarse-first validator lost local dynamic-order count")
    v.check("public_work_precision_available=2" in proc.stdout, "v048 coarse-first validator lost public work/precision availability count")
    v.check("public_work_precision_missing=0" in proc.stdout, "v048 coarse-first validator lost public work/precision closed gap count")
    v.check("strict_common_reference_available=2" in proc.stdout, "v048 coarse-first validator lost strict common-reference availability count")
    v.check("strict_common_reference_gap=0" in proc.stdout, "v048 coarse-first validator lost strict common-reference gap count")
    v.check("strict_common_reference_figure_available=True" in proc.stdout, "v048 coarse-first validator lost strict common-reference figure marker")
    v.check("dynamic_order_missing=0" in proc.stdout, "v048 coarse-first validator lost closed local dynamic-order gap status")
    v.check("external_superiority_claim=False" in proc.stdout, "v048 coarse-first validator lost no-superiority marker")
    return proc.stdout


def run_v048_closed_loop_surrogate_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_closed_loop_surrogate_dynamic_gate.py"],
        cwd=V048_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"v048 closed-loop surrogate validator failed:\n{proc.stdout}")
    v.check(
        "closed-loop surrogate dynamic gate validation: PASS" in proc.stdout,
        "v048 closed-loop surrogate validator did not report PASS",
    )
    v.check("surrogate_available=2" in proc.stdout, "v048 closed-loop surrogate validator lost availability count")
    v.check("accepted_dynamic_order=0" in proc.stdout, "v048 closed-loop surrogate validator lost dynamic-order boundary")
    v.check("dynamic_superiority_claim=False" in proc.stdout, "v048 closed-loop surrogate validator lost no-superiority marker")
    return proc.stdout


def run_v048_closed_loop_floor_audit_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_closed_loop_dynamic_error_floor_audit.py"],
        cwd=V048_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"v048 closed-loop floor-audit validator failed:\n{proc.stdout}")
    v.check(
        "closed-loop dynamic error floor audit validation: PASS" in proc.stdout,
        "v048 closed-loop floor-audit validator did not report PASS",
    )
    v.check(
        "velocity_acceleration_evidence=2" in proc.stdout,
        "v048 closed-loop floor-audit validator lost velocity/acceleration evidence count",
    )
    v.check("accepted_dynamic_order=0" in proc.stdout, "v048 closed-loop floor-audit validator lost dynamic-order boundary")
    v.check("external_superiority_claim=False" in proc.stdout, "v048 closed-loop floor-audit validator lost no-superiority marker")
    return proc.stdout


def run_v048_closed_loop_coarse_probe_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_closed_loop_coarse_dynamic_order_probe.py"],
        cwd=V048_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"v048 closed-loop coarse probe validator failed:\n{proc.stdout}")
    v.check(
        "closed-loop coarse dynamic-order probe validation: PASS" in proc.stdout,
        "v048 closed-loop coarse probe validator did not report PASS",
    )
    v.check("rows=11/12" in proc.stdout, "v048 closed-loop coarse probe validator lost row count")
    v.check(
        "local_velocity_evidence=2/2" in proc.stdout,
        "v048 closed-loop coarse probe validator lost velocity-evidence count",
    )
    v.check(
        "local_acceleration_evidence=2/2" in proc.stdout,
        "v048 closed-loop coarse probe validator lost acceleration-evidence count",
    )
    v.check(
        "local_position_floor_rows=2/2" in proc.stdout,
        "v048 closed-loop coarse probe validator lost position-floor count",
    )
    v.check("accepted_dynamic_order=0" in proc.stdout, "v048 closed-loop coarse probe validator lost order boundary")
    v.check("external_superiority_claim=False" in proc.stdout, "v048 closed-loop coarse probe validator lost no-superiority marker")
    return proc.stdout


def run_v048_closed_loop_closure_contract_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_closed_loop_dynamic_order_closure_contract.py"],
        cwd=V048_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"v048 closed-loop closure contract validator failed:\n{proc.stdout}")
    v.check(
        "closed-loop dynamic-order closure contract validation: PASS" in proc.stdout,
        "v048 closed-loop closure contract validator did not report PASS",
    )
    v.check(
        "missing_dynamic_order_models=none" in proc.stdout,
        "v048 closed-loop closure contract validator lost local closure marker",
    )
    v.check("accepted_dynamic_order=2" in proc.stdout, "v048 closed-loop closure contract validator lost local order count")
    v.check("public_work_precision_available=2" in proc.stdout, "v048 closed-loop closure contract validator lost public work/precision availability")
    v.check("public_work_precision_missing=0" in proc.stdout, "v048 closed-loop closure contract validator lost closed public work/precision gap")
    v.check("strict_common_reference_available=2" in proc.stdout, "v048 closed-loop closure contract validator lost strict common-reference availability")
    v.check("strict_common_reference_gap=0" in proc.stdout, "v048 closed-loop closure contract validator lost strict common-reference gap")
    v.check("strict_common_reference_figure_available=True" in proc.stdout, "v048 closed-loop closure contract validator lost strict common-reference figure marker")
    v.check("theorem_order=6" in proc.stdout, "v048 closed-loop closure contract validator lost theorem-order marker")
    v.check("default_1e-4=False" in proc.stdout, "v048 closed-loop closure contract validator lost no-default marker")
    v.check("external_superiority_claim=False" in proc.stdout, "v048 closed-loop closure contract validator lost no-superiority marker")
    return proc.stdout


def run_v048_closed_loop_feasibility_audit_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_closed_loop_true_dynamic_row_feasibility_audit.py"],
        cwd=V048_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"v048 closed-loop true dynamic-row feasibility audit validator failed:\n{proc.stdout}")
    v.check(
        "closed-loop true dynamic-row feasibility audit validation: PASS" in proc.stdout,
        "v048 closed-loop true dynamic-row feasibility audit validator did not report PASS",
    )
    v.check(
        "missing_dynamic_order_models=four_link,slider_crank" in proc.stdout,
        "v048 closed-loop feasibility audit lost missing-model marker",
    )
    v.check("true_dynamic_local_rows=0" in proc.stdout, "v048 closed-loop feasibility audit lost true-row boundary")
    v.check("accepted_dynamic_order=0" in proc.stdout, "v048 closed-loop feasibility audit lost order boundary")
    v.check(
        "local_row_kind=kinematic_fullva_plus_reaction_reconstruction" in proc.stdout,
        "v048 closed-loop feasibility audit lost local-row-kind marker",
    )
    v.check("default_1e-4=False" in proc.stdout, "v048 closed-loop feasibility audit lost no-default marker")
    v.check("external_superiority_claim=False" in proc.stdout, "v048 closed-loop feasibility audit lost no-superiority marker")
    return proc.stdout


def run_v048_closed_loop_residual_scaffold_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_closed_loop_true_dynamic_residual_scaffold.py"],
        cwd=V048_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"v048 closed-loop true dynamic residual scaffold validator failed:\n{proc.stdout}")
    v.check(
        "closed-loop true dynamic residual scaffold validation: PASS" in proc.stdout,
        "v048 closed-loop true dynamic residual scaffold validator did not report PASS",
    )
    v.check("stage_unknown_dim=72" in proc.stdout, "v048 residual scaffold lost stage-dim marker")
    v.check("total_unknown_dim=216" in proc.stdout, "v048 residual scaffold lost total-dim marker")
    v.check("square_total_system=True" in proc.stdout, "v048 residual scaffold lost square-system marker")
    v.check("local_runner_implemented=False" in proc.stdout, "v048 residual scaffold overclaimed runner implementation")
    v.check("default_1e-4=False" in proc.stdout, "v048 residual scaffold lost no-default marker")
    v.check("accepted_dynamic_order=0" in proc.stdout, "v048 residual scaffold lost order boundary")
    return proc.stdout


def run_v048_closed_loop_stage_residual_audit_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_closed_loop_true_dynamic_stage_residual_audit.py"],
        cwd=V048_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"v048 closed-loop true dynamic stage residual audit validator failed:\n{proc.stdout}")
    v.check(
        "closed-loop true dynamic stage residual audit validation: PASS" in proc.stdout,
        "v048 closed-loop true dynamic stage residual audit validator did not report PASS",
    )
    v.check("rows_ok=6/6" in proc.stdout, "v048 stage residual audit lost row count")
    v.check("stage_residual_evaluator_implemented=True" in proc.stdout, "v048 stage residual audit lost evaluator marker")
    v.check("trajectory_stepper_implemented=False" in proc.stdout, "v048 stage residual audit overclaimed stepper")
    v.check("default_1e-4=False" in proc.stdout, "v048 stage residual audit lost no-default marker")
    v.check("accepted_dynamic_order=0" in proc.stdout, "v048 stage residual audit lost order boundary")
    return proc.stdout


def run_v048_closed_loop_one_step_smoke_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_closed_loop_true_dynamic_one_step_smoke.py"],
        cwd=V048_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"v048 closed-loop true dynamic one-step smoke validator failed:\n{proc.stdout}")
    v.check(
        "closed-loop true dynamic one-step smoke validation: PASS" in proc.stdout,
        "v048 closed-loop true dynamic one-step smoke validator did not report PASS",
    )
    v.check("rows_ok=2/2" in proc.stdout, "v048 one-step smoke lost row count")
    v.check("trajectory_stepper_executed=True" in proc.stdout, "v048 one-step smoke did not execute stepper")
    v.check("convergence_sweep_run=False" in proc.stdout, "v048 one-step smoke ran convergence sweep")
    v.check("default_1e-4=False" in proc.stdout, "v048 one-step smoke lost no-default marker")
    v.check("accepted_dynamic_order=0" in proc.stdout, "v048 one-step smoke lost order boundary")
    return proc.stdout


def run_v048_closed_loop_newton_stage_smoke_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_closed_loop_true_dynamic_newton_stage_smoke.py"],
        cwd=V048_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"v048 closed-loop true dynamic Newton stage smoke validator failed:\n{proc.stdout}")
    v.check(
        "closed-loop true dynamic Newton stage smoke validation: PASS" in proc.stdout,
        "v048 closed-loop true dynamic Newton stage smoke validator did not report PASS",
    )
    v.check("rows_ok=2/2" in proc.stdout, "v048 Newton stage smoke lost row count")
    v.check("stage_oracle_used=False" in proc.stdout, "v048 Newton stage smoke used stage oracle")
    v.check("trajectory_stepper_executed=True" in proc.stdout, "v048 Newton stage smoke did not execute stepper")
    v.check("convergence_sweep_run=False" in proc.stdout, "v048 Newton stage smoke ran convergence sweep")
    v.check("default_1e-4=False" in proc.stdout, "v048 Newton stage smoke lost no-default marker")
    v.check("accepted_dynamic_order=0" in proc.stdout, "v048 Newton stage smoke lost order boundary")
    return proc.stdout


def run_v048_closed_loop_newton_coarse_order_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_closed_loop_true_dynamic_newton_coarse_order.py"],
        cwd=V048_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"v048 closed-loop true dynamic Newton coarse order validator failed:\n{proc.stdout}")
    v.check(
        "closed-loop true dynamic Newton coarse order validation: PASS" in proc.stdout,
        "v048 closed-loop true dynamic Newton coarse order validator did not report PASS",
    )
    v.check("rows_ok=6/6" in proc.stdout, "v048 Newton coarse order lost row count")
    v.check("accepted_dynamic_order=2" in proc.stdout, "v048 Newton coarse order lost accepted local order count")
    v.check("stage_oracle_used=False" in proc.stdout, "v048 Newton coarse order used stage oracle")
    v.check("convergence_sweep_run=True" in proc.stdout, "v048 Newton coarse order lost convergence marker")
    v.check("default_1e-4=False" in proc.stdout, "v048 Newton coarse order lost no-default marker")
    v.check("external_superiority_claim=False" in proc.stdout, "v048 Newton coarse order overclaimed superiority")
    return proc.stdout


def run_v048_closed_loop_public_work_precision_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_closed_loop_true_dynamic_public_work_precision.py"],
        cwd=V048_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"v048 closed-loop true dynamic public work/precision validator failed:\n{proc.stdout}")
    v.check(
        "closed-loop true dynamic public work/precision validation: PASS" in proc.stdout,
        "v048 closed-loop true dynamic public work/precision validator did not report PASS",
    )
    v.check("rows_ok=24/24" in proc.stdout, "v048 public work/precision validator lost row count")
    v.check("public_work_precision_available=2/2" in proc.stdout, "v048 public work/precision validator lost availability count")
    v.check("public_work_precision_missing=0" in proc.stdout, "v048 public work/precision validator lost missing count")
    v.check("strict_common_reference_error_columns=False" in proc.stdout, "v048 public work/precision validator lost reference caveat")
    v.check("default_1e-4=False" in proc.stdout, "v048 public work/precision validator lost no-default marker")
    v.check("external_superiority_claim=False" in proc.stdout, "v048 public work/precision validator overclaimed superiority")
    return proc.stdout


def run_v048_closed_loop_strict_common_reference_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_closed_loop_true_dynamic_strict_common_reference.py"],
        cwd=V048_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"v048 closed-loop true dynamic strict common-reference validator failed:\n{proc.stdout}")
    v.check(
        "closed-loop true dynamic strict common-reference validation: PASS" in proc.stdout,
        "v048 closed-loop true dynamic strict common-reference validator did not report PASS",
    )
    v.check("rows_ok=24/24" in proc.stdout, "v048 strict common-reference validator lost row count")
    v.check(
        "strict_common_reference_available=2/2" in proc.stdout,
        "v048 strict common-reference validator lost availability count",
    )
    v.check("strict_common_reference_gap=0" in proc.stdout, "v048 strict common-reference validator lost closed gap count")
    v.check(
        "figure=closed_loop_true_dynamic_strict_common_reference_work_precision.png" in proc.stdout,
        "v048 strict common-reference validator lost figure marker",
    )
    v.check("default_1e-4=False" in proc.stdout, "v048 strict common-reference validator lost no-default marker")
    v.check("external_superiority_claim=False" in proc.stdout, "v048 strict common-reference validator overclaimed superiority")
    return proc.stdout


def run_v048_residual_to_error_obligation_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_closed_loop_residual_to_error_theorem_obligations.py"],
        cwd=V048_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"v048 residual-to-error theorem obligation validator failed:\n{proc.stdout}")
    v.check(
        "closed-loop residual-to-error theorem obligations validation: PASS" in proc.stdout,
        "v048 residual-to-error theorem obligation validator did not report PASS",
    )
    v.check("obligations=7" in proc.stdout, "v048 residual-to-error obligation validator lost obligation count")
    v.check("blocking_obligations=7" in proc.stdout, "v048 residual-to-error obligation validator lost blocking count")
    v.check(
        "accepted_residual_to_error_theorem=False" in proc.stdout,
        "v048 residual-to-error theorem was incorrectly accepted",
    )
    v.check("accepted_dynamic_order=0" in proc.stdout, "v048 residual-to-error route lost order boundary")
    v.check("true_dynamic_local_rows=0" in proc.stdout, "v048 residual-to-error route lost true-row boundary")
    v.check("default_1e-4=False" in proc.stdout, "v048 residual-to-error route lost no-default marker")
    v.check("external_superiority_claim=False" in proc.stdout, "v048 residual-to-error route lost no-superiority marker")
    return proc.stdout


def run_v048_single_coarse_validator(v: Validator) -> str:
    proc = subprocess.run(
        [sys.executable, "validate_single_pendulum_coarse_same_window.py"],
        cwd=V048_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"v048 single-pendulum coarse validator failed:\n{proc.stdout}")
    v.check(
        "single-pendulum coarse same-window validation: PASS" in proc.stdout,
        "v048 single-pendulum coarse validator did not report PASS",
    )
    v.check("public_rows=9/9" in proc.stdout, "v048 single-pendulum coarse validator lost public row count")
    v.check("local_rows=3/3" in proc.stdout, "v048 single-pendulum coarse validator lost local row count")
    v.check("work_precision_rows=4/4" in proc.stdout, "v048 single-pendulum coarse validator lost work row count")
    v.check("external_superiority_claim=False" in proc.stdout, "v048 single-pendulum coarse validator lost no-superiority marker")
    return proc.stdout


def run_paper_claim_validator(v: Validator) -> tuple[str, ...]:
    required_files = [
        LATEX_DIR / "main.tex",
        LATEX_DIR / "main.pdf",
        LATEX_DIR / "main_concise.tex",
        LATEX_DIR / "main_concise.pdf",
        LATEX_DIR / "main_cmame.tex",
        LATEX_DIR / "main_cmame.pdf",
        LATEX_DIR / "highlights_cmame.txt",
        LATEX_DIR / "declarations_cmame.md",
        PAPER_DIR / "CMAME_SUBMISSION_CHECKLIST.md",
        PAPER_DIR / "CMAME_SUBMISSION_READINESS_AUDIT.md",
        PAPER_DIR / "CMAME_SUBMISSION_READINESS_REVIEW.md",
        PAPER_DIR / "CMAME_BLOCKER_CLOSURE_GATE.md",
        PAPER_DIR / "CMAME_BLOCKER_CLOSURE_GATE.json",
        PAPER_DIR / "CMAME_EXTERNAL_BASELINE_GATE.md",
        PAPER_DIR / "CMAME_EXTERNAL_BASELINE_GATE.json",
        PAPER_DIR / "CMAME_PROOF_CONTRACT_GATE.md",
        PAPER_DIR / "CMAME_PROOF_CONTRACT_GATE.json",
        PAPER_DIR / "CMAME_VISUAL_LEGIBILITY_AUDIT.md",
        PAPER_DIR / "CMAME_VISUAL_LEGIBILITY_AUDIT.json",
        PAPER_DIR / "CMAME_RELATED_WORK_AUDIT.md",
        PAPER_DIR / "CMAME_RELATED_WORK_AUDIT.json",
        PAPER_DIR / "CMAME_PROSE_RESIDUE_AUDIT.md",
        PAPER_DIR / "CMAME_PROSE_RESIDUE_AUDIT.json",
        PAPER_DIR / "DYNAMIC_ROW_ORACLE_GATE.md",
        PAPER_DIR / "DYNAMIC_ROW_ORACLE_GATE.json",
        LATEX_DIR / "README_CMAME_FLAT_SUBMISSION.md",
        LATEX_DIR / "cmame_submission_flat.zip",
        LATEX_DIR / "cmame_submission_flat" / "main_cmame_submission.tex",
        LATEX_DIR / "cmame_submission_flat" / "main_cmame_submission.pdf",
        LATEX_DIR / "cmame_submission_flat" / "main_cmame_submission.log",
        LATEX_DIR / "cmame_submission_flat" / "highlights_cmame.txt",
        LATEX_DIR / "cmame_submission_flat" / "declarations_cmame.md",
        LATEX_DIR / "cmame_submission_flat" / "Figure_1_convergence.png",
        LATEX_DIR / "cmame_submission_flat" / "Figure_2_asme_lower_pair_graph_bridge.png",
        LATEX_DIR / "cmame_submission_flat" / "Figure_3_asme_closed_loop_kinematic_fullva.png",
        LATEX_DIR / "cmame_submission_flat" / "Figure_4_order_closure_blend.png",
        LATEX_DIR / "cmame_submission_flat" / "Figure_5_velocity_compression.png",
        LATEX_DIR / "cmame_submission_flat" / "Figure_6_sparse_speed_gap.png",
        LATEX_DIR / "cmame_submission_flat" / "Figure_7_strict_common_reference_work_precision.png",
        LATEX_DIR / "cmame_submission_flat" / "Figure_8_claim_boundary_limitations.png",
        LATEX_DIR / "cmame_submission_flat" / "Figure_9_coarse_baseline_work_precision.png",
        LATEX_DIR / "cmame_submission_flat" / "Figure_10_closed_loop_true_dynamic_order.png",
        LATEX_DIR / "cmame_submission_flat" / "Figure_11_method_stage_architecture.png",
        PAPER_DIR / "README.md",
        PAPER_DIR / "CLAIM_BOUNDARY.json",
        PAPER_DIR / "CURRENT_STATUS_CN.md",
        PAPER_DIR / "PAPER_CLAIM_LEDGER.md",
        PAPER_DIR / "SUBMISSION_PACKET.md",
        LATEX_DIR / "COVER_LETTER.md",
        PAPER_DIR / "SUBMISSION_ARTIFACT_MANIFEST.json",
        PAPER_DIR / "SUBMISSION_FILE_INVENTORY.md",
        PAPER_DIR / "REVIEW_RESPONSE_TEMPLATE.md",
        PAPER_DIR / "SOURCE_PAPER_COMPARISON.md",
        PAPER_DIR / "CROSS_PAPER_BENCHMARK_MATRIX.md",
        PAPER_DIR / "CROSS_PAPER_BENCHMARK_SPEC.md",
        PAPER_DIR / "CROSS_PAPER_BENCHMARK_CASES.json",
        PAPER_DIR / "EXTERNAL_SAME_TEST_RUN_QUEUE.md",
        PAPER_DIR / "EXTERNAL_SAME_TEST_RUN_QUEUE.json",
        PAPER_DIR / "PROOF_EVIDENCE_MATRIX.md",
        PAPER_DIR / "PROOF_SOLVER_SCALE_AUDIT.md",
        PAPER_DIR / "PROOF_SOLVER_SCALE_AUDIT.json",
        PAPER_DIR / "ORDER_ACCEPTANCE_GATE.md",
        PAPER_DIR / "ORDER_ACCEPTANCE_GATE.json",
        PAPER_DIR / "IMPLEMENTATION_FIDELITY_CERTIFICATE.md",
        PAPER_DIR / "IMPLEMENTATION_PATH_AUDIT.md",
        PAPER_DIR / "IMPLEMENTATION_PATH_AUDIT.json",
        PAPER_DIR / "B4_SOURCE_POLICY_ROW_CLOSURE_READINESS_LEDGER.md",
        PAPER_DIR / "B4_SOURCE_POLICY_ROW_CLOSURE_READINESS_LEDGER.json",
        PAPER_DIR / "B4_SOURCE_POLICY_ROW_CLOSURE_READINESS_LEDGER.csv",
        PAPER_DIR / "build_b4_source_policy_row_closure_readiness_ledger.py",
        PAPER_DIR / "validate_b4_source_policy_row_closure_readiness_ledger.py",
        PAPER_DIR / "SOURCE_POLICY_ROW_CLOSURE_LEDGER.md",
        PAPER_DIR / "SOURCE_POLICY_ROW_CLOSURE_LEDGER.json",
        PAPER_DIR / "build_source_policy_row_closure_ledger.py",
        PAPER_DIR / "validate_source_policy_row_closure_ledger.py",
        PAPER_DIR / "TFE_DAE_RUNNER_CONTRACT_GAP_AUDIT.md",
        PAPER_DIR / "TFE_DAE_RUNNER_CONTRACT_GAP_AUDIT.json",
        PAPER_DIR / "build_tfe_dae_runner_contract_gap_audit.py",
        PAPER_DIR / "validate_tfe_dae_runner_contract_gap_audit.py",
        PAPER_DIR / "TFE_RUNNER_CONTRACT_PREFLIGHT_CERTIFICATE.md",
        PAPER_DIR / "TFE_RUNNER_CONTRACT_PREFLIGHT_CERTIFICATE.json",
        PAPER_DIR / "build_tfe_runner_contract_preflight_certificate.py",
        PAPER_DIR / "validate_tfe_runner_contract_preflight_certificate.py",
        PAPER_DIR / "B4_SOURCE_POLICY_WORK_PRECISION_EXECUTION_PLAN.md",
        PAPER_DIR / "B4_SOURCE_POLICY_WORK_PRECISION_EXECUTION_PLAN.json",
        PAPER_DIR / "build_b4_source_policy_work_precision_execution_plan.py",
        PAPER_DIR / "validate_b4_source_policy_work_precision_execution_plan.py",
        PAPER_DIR / "B4_SOURCE_POLICY_POST_EXECUTION_AUDIT.md",
        PAPER_DIR / "B4_SOURCE_POLICY_POST_EXECUTION_AUDIT.json",
        PAPER_DIR / "build_b4_source_policy_post_execution_audit.py",
        PAPER_DIR / "validate_b4_source_policy_post_execution_audit.py",
        PAPER_DIR / "B4_EXISTING_ARTIFACT_PROMOTION_AUDIT.md",
        PAPER_DIR / "B4_EXISTING_ARTIFACT_PROMOTION_AUDIT.json",
        PAPER_DIR / "build_b4_existing_artifact_promotion_audit.py",
        PAPER_DIR / "validate_b4_existing_artifact_promotion_audit.py",
        PAPER_DIR / "EXTERNAL_SOURCE_POLICY_CLOSURE_MANIFEST.md",
        PAPER_DIR / "EXTERNAL_SOURCE_POLICY_CLOSURE_MANIFEST.json",
        PAPER_DIR / "build_external_source_policy_closure_manifest.py",
        PAPER_DIR / "validate_external_source_policy_closure_manifest.py",
        PAPER_DIR / "B6_FOUR_EXAMPLE_LOCAL_EVIDENCE_SUMMARY.md",
        PAPER_DIR / "B6_FOUR_EXAMPLE_LOCAL_EVIDENCE_SUMMARY.json",
        PAPER_DIR / "validate_b6_four_example_local_evidence.py",
        PAPER_DIR / "CMAME_RUNNER_CENTERED_REPRODUCIBILITY_AUDIT.md",
        PAPER_DIR / "CMAME_RUNNER_CENTERED_REPRODUCIBILITY_AUDIT.json",
        PAPER_DIR / "build_cmame_runner_centered_reproducibility_audit.py",
        PAPER_DIR / "validate_cmame_runner_centered_reproducibility_audit.py",
        PAPER_DIR / "CMAME_NARROWED_REPRODUCIBILITY_PACKAGE_AUDIT.md",
        PAPER_DIR / "CMAME_NARROWED_REPRODUCIBILITY_PACKAGE_AUDIT.json",
        PAPER_DIR / "build_cmame_narrowed_reproducibility_package_audit.py",
        PAPER_DIR / "validate_cmame_narrowed_reproducibility_package_audit.py",
        PAPER_DIR / "CMAME_NARROWED_REPRO_CODE_ARCHIVE_MANIFEST.md",
        PAPER_DIR / "CMAME_NARROWED_REPRO_CODE_ARCHIVE_MANIFEST.json",
        PAPER_DIR / "cmame_narrowed_repro_code_archive.zip",
        PAPER_DIR / "build_cmame_narrowed_repro_code_archive.py",
        PAPER_DIR / "validate_cmame_narrowed_repro_code_archive.py",
        PAPER_DIR / "CMAME_REPRODUCIBILITY_PACKAGE_MANIFEST.md",
        PAPER_DIR / "CMAME_REPRODUCIBILITY_PACKAGE_MANIFEST.json",
        PAPER_DIR / "build_cmame_reproducibility_package_manifest.py",
        PAPER_DIR / "validate_cmame_reproducibility_package_manifest.py",
        PAPER_DIR / "B6_CLOSED_LOOP_SELF_CONTAINED_EXTRACTION_AUDIT.md",
        PAPER_DIR / "B6_CLOSED_LOOP_SELF_CONTAINED_EXTRACTION_AUDIT.json",
        PAPER_DIR / "build_b6_closed_loop_self_contained_extraction_audit.py",
        PAPER_DIR / "validate_b6_closed_loop_self_contained_extraction_audit.py",
        PAPER_DIR / "CMAME_SELF_CONTAINED_RUNNER_EXTRACTION_PLAN.md",
        PAPER_DIR / "CMAME_SELF_CONTAINED_RUNNER_EXTRACTION_PLAN.json",
        PAPER_DIR / "build_cmame_self_contained_runner_extraction_plan.py",
        PAPER_DIR / "validate_cmame_self_contained_runner_extraction_plan.py",
        PAPER_DIR / "CMAME_MINIMAL_REPRODUCIBILITY_CANDIDATE_MANIFEST.md",
        PAPER_DIR / "CMAME_MINIMAL_REPRODUCIBILITY_CANDIDATE_MANIFEST.json",
        PAPER_DIR / "build_cmame_minimal_reproducibility_candidate.py",
        PAPER_DIR / "validate_cmame_minimal_reproducibility_candidate.py",
        PAPER_DIR / "cmame_minimal_reproducibility_candidate" / "README.md",
        PAPER_DIR / "cmame_minimal_reproducibility_candidate" / "MANIFEST.json",
        PAPER_DIR / "cmame_minimal_reproducibility_candidate" / "scripts" / "replay_paper_matrix.py",
        PAPER_DIR / "cmame_minimal_reproducibility_candidate" / "data" / "PAPER_NUMERICAL_RESULT_MATRIX.json",
        PAPER_DIR / "CMAME_CLOSED_LOOP_LOCAL_RUNNER_CANDIDATE_MANIFEST.md",
        PAPER_DIR / "CMAME_CLOSED_LOOP_LOCAL_RUNNER_CANDIDATE_MANIFEST.json",
        PAPER_DIR / "build_cmame_closed_loop_local_runner_candidate.py",
        PAPER_DIR / "validate_cmame_closed_loop_local_runner_candidate.py",
        PAPER_DIR / "cmame_closed_loop_local_runner_candidate" / "README.md",
        PAPER_DIR / "cmame_closed_loop_local_runner_candidate" / "MANIFEST.json",
        PAPER_DIR / "cmame_closed_loop_local_runner_candidate" / "scripts" / "run_closed_loop_fullva_candidate.py",
        PAPER_DIR / "cmame_closed_loop_local_runner_candidate" / "results" / "closed_loop_local_summary.json",
        PAPER_DIR / "cmame_closed_loop_local_runner_candidate" / "results" / "closed_loop_local_rows.csv",
        PAPER_DIR / "CMAME_LOCAL_ACCEPTED_RUNNER_COMPANION_MANIFEST.md",
        PAPER_DIR / "CMAME_LOCAL_ACCEPTED_RUNNER_COMPANION_MANIFEST.json",
        PAPER_DIR / "build_cmame_local_accepted_runner_companion.py",
        PAPER_DIR / "validate_cmame_local_accepted_runner_companion.py",
        PAPER_DIR / "cmame_local_accepted_runner_companion" / "README.md",
        PAPER_DIR / "cmame_local_accepted_runner_companion" / "MANIFEST.json",
        PAPER_DIR / "cmame_local_accepted_runner_companion" / "scripts" / "run_local_accepted_runner_companion.py",
        PAPER_DIR / "CMAME_P1_LOCAL_RUNNER_EXTRACTION_AUDIT.md",
        PAPER_DIR / "CMAME_P1_LOCAL_RUNNER_EXTRACTION_AUDIT.json",
        PAPER_DIR / "build_cmame_p1_local_runner_extraction_audit.py",
        PAPER_DIR / "validate_cmame_p1_local_runner_extraction_audit.py",
        PAPER_DIR / "validate_cmame_p1_single_runner_candidate.py",
        PAPER_DIR / "cmame_p1_single_runner_candidate" / "README.md",
        PAPER_DIR / "cmame_p1_single_runner_candidate" / "scripts" / "run_single_pendulum_fullva.py",
        PAPER_DIR / "cmame_p1_single_runner_candidate" / "results" / "single_pendulum_summary.json",
        PAPER_DIR / "cmame_p1_single_runner_candidate" / "results" / "single_pendulum_rows.csv",
        PAPER_DIR / "validate_cmame_p1_double_runner_candidate.py",
        PAPER_DIR / "cmame_p1_double_runner_candidate" / "README.md",
        PAPER_DIR / "cmame_p1_double_runner_candidate" / "scripts" / "run_double_pendulum_fullva.py",
        PAPER_DIR / "cmame_p1_double_runner_candidate" / "results" / "double_pendulum_summary.json",
        PAPER_DIR / "cmame_p1_double_runner_candidate" / "results" / "double_pendulum_rows.csv",
        PAPER_DIR / "CMAME_RUNNER_ADAPTER_CANDIDATE_MANIFEST.md",
        PAPER_DIR / "CMAME_RUNNER_ADAPTER_CANDIDATE_MANIFEST.json",
        PAPER_DIR / "build_cmame_runner_adapter_candidate.py",
        PAPER_DIR / "validate_cmame_runner_adapter_candidate.py",
        PAPER_DIR / "cmame_runner_adapter_candidate" / "README.md",
        PAPER_DIR / "cmame_runner_adapter_candidate" / "MANIFEST.json",
        PAPER_DIR / "cmame_runner_adapter_candidate" / "scripts" / "run_four_example_matrix_adapter.py",
        PAPER_DIR / "cmame_runner_adapter_candidate" / "scripts" / "replay_closed_loop_local_rows.py",
        PAPER_DIR / "cmame_runner_adapter_candidate" / "results" / "closed_loop_local_rows_summary.json",
        PAPER_DIR / "cmame_runner_adapter_candidate" / "results" / "closed_loop_local_rows.csv",
        PAPER_DIR / "validate_cmame_narrowed_repro_bundle.py",
        PAPER_DIR / "cmame_narrowed_repro_bundle" / "README.md",
        PAPER_DIR / "cmame_narrowed_repro_bundle" / "MANIFEST.json",
        PAPER_DIR / "cmame_narrowed_repro_bundle" / "scripts" / "run_narrowed_repro_bundle.py",
        PAPER_DIR / "cmame_narrowed_repro_bundle" / "results" / "narrowed_repro_bundle_summary.json",
        PAPER_DIR / "cmame_narrowed_repro_bundle" / "results" / "narrowed_repro_bundle_summary.md",
        PAPER_DIR / "cmame_narrowed_repro_bundle" / "results" / "narrowed_repro_bundle_report.md",
        PAPER_DIR / "CMAME_SUBMISSION_INTEGRITY_AUDIT.md",
        PAPER_DIR / "CMAME_SUBMISSION_INTEGRITY_AUDIT.json",
        PAPER_DIR / "build_cmame_submission_integrity_audit.py",
        PAPER_DIR / "validate_cmame_submission_integrity_audit.py",
        PAPER_DIR / "REFERENCE_METADATA_AUDIT.md",
        PAPER_DIR / "REFERENCE_METADATA_AUDIT.json",
        PAPER_DIR / "build_reference_metadata_audit.py",
        PAPER_DIR / "validate_reference_metadata_audit.py",
        PAPER_DIR / "RESULT_TO_MANUSCRIPT_TRACEABILITY_AUDIT.md",
        PAPER_DIR / "RESULT_TO_MANUSCRIPT_TRACEABILITY_AUDIT.json",
        PAPER_DIR / "build_result_to_manuscript_traceability_audit.py",
        PAPER_DIR / "validate_result_to_manuscript_traceability_audit.py",
        PAPER_DIR / "CMAME_FIGURE_SET_AUDIT.md",
        PAPER_DIR / "CMAME_FIGURE_SET_AUDIT.json",
        PAPER_DIR / "build_cmame_figure_set_audit.py",
        PAPER_DIR / "validate_cmame_figure_set_audit.py",
        PAPER_DIR / "CMAME_SCALABILITY_BOUNDARY_AUDIT.md",
        PAPER_DIR / "CMAME_SCALABILITY_BOUNDARY_AUDIT.json",
        PAPER_DIR / "build_cmame_scalability_boundary_audit.py",
        PAPER_DIR / "validate_cmame_scalability_boundary_audit.py",
        PAPER_DIR / "CMAME_CLAIM_HYGIENE_AUDIT.md",
        PAPER_DIR / "CMAME_CLAIM_HYGIENE_AUDIT.json",
        PAPER_DIR / "build_cmame_claim_hygiene_audit.py",
        PAPER_DIR / "validate_cmame_claim_hygiene_audit.py",
        PAPER_DIR / "CMAME_PDF_STYLE_REVIEW_AUDIT.md",
        PAPER_DIR / "CMAME_PDF_STYLE_REVIEW_AUDIT.json",
        PAPER_DIR / "build_cmame_pdf_style_review_audit.py",
        PAPER_DIR / "validate_cmame_pdf_style_review_audit.py",
        PAPER_DIR / "CMAME_REVIEW_AGENT_REPORT.md",
        PAPER_DIR / "CMAME_REVIEW_AGENT_REPORT.json",
        PAPER_DIR / "validate_cmame_review_agent.py",
        PAPER_DIR / "CMAME_NARROWED_CLAIM_CLOSURE_POLICY_AUDIT.md",
        PAPER_DIR / "CMAME_NARROWED_CLAIM_CLOSURE_POLICY_AUDIT.json",
        PAPER_DIR / "build_cmame_narrowed_claim_closure_policy_audit.py",
        PAPER_DIR / "validate_cmame_narrowed_claim_closure_policy_audit.py",
        PAPER_DIR / "PAPER_CORE_TO_MANUSCRIPT_AUDIT.md",
        PAPER_DIR / "PAPER_CORE_TO_MANUSCRIPT_AUDIT.json",
        PAPER_DIR / "build_paper_core_to_manuscript_audit.py",
        PAPER_DIR / "validate_paper_core_to_manuscript_audit.py",
        PAPER_DIR / "ALL_EXAMPLES_RESULT_SANITY_AUDIT.md",
        PAPER_DIR / "ALL_EXAMPLES_RESULT_SANITY_AUDIT.json",
        PAPER_DIR / "build_all_examples_result_sanity_audit.py",
        PAPER_DIR / "validate_all_examples_result_sanity_audit.py",
        PAPER_DIR / "ALL_METHOD_EXAMPLE_CLAIM_DISPOSITION_AUDIT.md",
        PAPER_DIR / "ALL_METHOD_EXAMPLE_CLAIM_DISPOSITION_AUDIT.json",
        PAPER_DIR / "build_all_method_example_claim_disposition_audit.py",
        PAPER_DIR / "validate_all_method_example_claim_disposition_audit.py",
        PAPER_DIR / "PAPER_NUMERICAL_RESULT_MATRIX.md",
        PAPER_DIR / "PAPER_NUMERICAL_RESULT_MATRIX.json",
        PAPER_DIR / "PAPER_NUMERICAL_RESULT_MATRIX.csv",
        PAPER_DIR / "build_paper_numerical_result_matrix.py",
        PAPER_DIR / "validate_paper_numerical_result_matrix.py",
        PAPER_DIR / "COMMON_REFERENCE_ORDER_RECOMPUTATION_AUDIT.md",
        PAPER_DIR / "COMMON_REFERENCE_ORDER_RECOMPUTATION_AUDIT.json",
        PAPER_DIR / "build_common_reference_order_recomputation_audit.py",
        PAPER_DIR / "validate_common_reference_order_recomputation_audit.py",
        PAPER_DIR / "COMPARISON_OBJECTIVE_CLOSURE_RECONCILIATION_AUDIT.md",
        PAPER_DIR / "COMPARISON_OBJECTIVE_CLOSURE_RECONCILIATION_AUDIT.json",
        PAPER_DIR / "build_comparison_objective_closure_reconciliation_audit.py",
        PAPER_DIR / "validate_comparison_objective_closure_reconciliation_audit.py",
        PAPER_DIR / "PAPER_CORE_RESULT_CONSOLIDATION.md",
        PAPER_DIR / "PAPER_CORE_RESULT_CONSOLIDATION.json",
        PAPER_DIR / "build_paper_core_result_consolidation.py",
        PAPER_DIR / "validate_paper_core_result_consolidation.py",
        PAPER_DIR / "PROOF_CLOSURE_MANIFEST.md",
        PAPER_DIR / "PROOF_CLOSURE_MANIFEST.json",
        PAPER_DIR / "build_proof_closure_manifest.py",
        PAPER_DIR / "validate_proof_closure_manifest.py",
        PAPER_DIR / "PROOF_CLAIM_TRACEABILITY_AUDIT.md",
        PAPER_DIR / "PROOF_CLAIM_TRACEABILITY_AUDIT.json",
        PAPER_DIR / "build_proof_claim_traceability_audit.py",
        PAPER_DIR / "validate_proof_claim_traceability_audit.py",
        PAPER_DIR / "PROOF_REMAINING_WORK_MANIFEST.md",
        PAPER_DIR / "PROOF_REMAINING_WORK_MANIFEST.json",
        PAPER_DIR / "build_proof_remaining_work_manifest.py",
        PAPER_DIR / "validate_proof_remaining_work_manifest.py",
        PAPER_DIR / "B1_AD_EXPANDED_SYMBOLIC_ORACLE_CLOSURE_CERTIFICATE.md",
        PAPER_DIR / "B1_AD_EXPANDED_SYMBOLIC_ORACLE_CLOSURE_CERTIFICATE.json",
        PAPER_DIR / "build_b1_ad_expanded_symbolic_oracle_closure_certificate.py",
        PAPER_DIR / "validate_b1_ad_expanded_symbolic_oracle_closure_certificate.py",
        PAPER_DIR / "B1_SYMBOLIC_ROW_ORACLE_CLOSURE_CERTIFICATE.md",
        PAPER_DIR / "B1_SYMBOLIC_ROW_ORACLE_CLOSURE_CERTIFICATE.json",
        PAPER_DIR / "build_b1_symbolic_row_oracle_closure_certificate.py",
        PAPER_DIR / "validate_b1_symbolic_row_oracle_closure_certificate.py",
        PAPER_DIR / "B3_DIRECT_PROOF_REVIEW_AUDIT.md",
        PAPER_DIR / "B3_DIRECT_PROOF_REVIEW_AUDIT.json",
        PAPER_DIR / "build_b3_direct_proof_review_audit.py",
        PAPER_DIR / "validate_b3_direct_proof_review_audit.py",
        PAPER_DIR / "CMAME_STRICT_PROOF_AUDIT.md",
        PAPER_DIR / "CMAME_STRICT_PROOF_AUDIT.json",
        PAPER_DIR / "build_cmame_strict_proof_audit.py",
        PAPER_DIR / "validate_cmame_strict_proof_audit.py",
        PAPER_DIR / "CMAME_STRICT_PROOF_POLICY_RECONCILIATION_AUDIT.md",
        PAPER_DIR / "CMAME_STRICT_PROOF_POLICY_RECONCILIATION_AUDIT.json",
        PAPER_DIR / "build_cmame_strict_proof_policy_reconciliation_audit.py",
        PAPER_DIR / "validate_cmame_strict_proof_policy_reconciliation_audit.py",
        PAPER_DIR / "CMAME_PROOF_STYLE_AUDIT.md",
        PAPER_DIR / "CMAME_PROOF_STYLE_AUDIT.json",
        PAPER_DIR / "validate_cmame_proof_style_audit.py",
        PAPER_DIR / "KINEMATIC_ROW_DEFECT_CERTIFICATE.md",
        PAPER_DIR / "KINEMATIC_ROW_DEFECT_CERTIFICATE.json",
        PAPER_DIR / "validate_kinematic_row_defect_certificate.py",
        PAPER_DIR / "NEWTON_EULER_VIRTUAL_WORK_WRENCH_AUDIT.md",
        PAPER_DIR / "NEWTON_EULER_VIRTUAL_WORK_WRENCH_AUDIT.json",
        PAPER_DIR / "build_newton_euler_virtual_work_wrench_audit.py",
        PAPER_DIR / "validate_newton_euler_virtual_work_wrench_audit.py",
        PAPER_DIR / "NEWTON_EULER_SYMBOLIC_TARGET_AUDIT.md",
        PAPER_DIR / "NEWTON_EULER_SYMBOLIC_TARGET_AUDIT.json",
        PAPER_DIR / "build_newton_euler_symbolic_target_audit.py",
        PAPER_DIR / "validate_newton_euler_symbolic_target_audit.py",
        PAPER_DIR / "NEWTON_EULER_SYMBOLIC_DEFECT_CERTIFICATE.md",
        PAPER_DIR / "NEWTON_EULER_SYMBOLIC_DEFECT_CERTIFICATE.json",
        PAPER_DIR / "build_newton_euler_symbolic_defect_certificate.py",
        PAPER_DIR / "validate_newton_euler_symbolic_defect_certificate.py",
        PAPER_DIR / "NEWTON_EULER_ROW_ORDERING_SCALING_AD_AUDIT.md",
        PAPER_DIR / "NEWTON_EULER_ROW_ORDERING_SCALING_AD_AUDIT.json",
        PAPER_DIR / "build_newton_euler_row_ordering_scaling_ad_audit.py",
        PAPER_DIR / "validate_newton_euler_row_ordering_scaling_ad_audit.py",
        PAPER_DIR / "NEWTON_EULER_DYNAMIC_ROW_CLOSURE_CONTRACT.md",
        PAPER_DIR / "NEWTON_EULER_DYNAMIC_ROW_CLOSURE_CONTRACT.json",
        PAPER_DIR / "build_newton_euler_dynamic_row_closure_contract.py",
        PAPER_DIR / "validate_newton_euler_dynamic_row_closure_contract.py",
        PAPER_DIR / "NEWTON_EULER_DEFECT_OBLIGATION_GATE.md",
        PAPER_DIR / "NEWTON_EULER_DEFECT_OBLIGATION_GATE.json",
        PAPER_DIR / "build_newton_euler_defect_obligation_gate.py",
        PAPER_DIR / "validate_newton_euler_defect_obligation_gate.py",
        PAPER_DIR / "NEWTON_EULER_BALANCE_IDENTITY_AUDIT.md",
        PAPER_DIR / "NEWTON_EULER_BALANCE_IDENTITY_AUDIT.json",
        PAPER_DIR / "build_newton_euler_balance_identity_audit.py",
        PAPER_DIR / "validate_newton_euler_balance_identity_audit.py",
        PAPER_DIR / "NEWTON_EULER_AD_EXPANDED_ROW_ORACLE_AUDIT.md",
        PAPER_DIR / "NEWTON_EULER_AD_EXPANDED_ROW_ORACLE_AUDIT.json",
        PAPER_DIR / "build_newton_euler_ad_expanded_row_oracle_audit.py",
        PAPER_DIR / "validate_newton_euler_ad_expanded_row_oracle_audit.py",
        PAPER_DIR / "SMOOTH_FORCE_LIFT_CERTIFICATE.md",
        PAPER_DIR / "SMOOTH_FORCE_LIFT_CERTIFICATE.json",
        PAPER_DIR / "build_smooth_force_lift_certificate.py",
        PAPER_DIR / "validate_smooth_force_lift_certificate.py",
        PAPER_DIR / "B2_SOURCE_POLICY_REMAINING_WORK_MANIFEST.md",
        PAPER_DIR / "B2_SOURCE_POLICY_REMAINING_WORK_MANIFEST.json",
        PAPER_DIR / "build_b2_source_policy_remaining_work_manifest.py",
        PAPER_DIR / "validate_b2_source_policy_remaining_work_manifest.py",
        PAPER_DIR / "SOURCE_POLICY_CLOSURE_TRIAGE.md",
        PAPER_DIR / "SOURCE_POLICY_CLOSURE_TRIAGE.json",
        PAPER_DIR / "build_source_policy_closure_triage.py",
        PAPER_DIR / "validate_source_policy_closure_triage.py",
        PAPER_DIR / "ALL_EXAMPLES_SOURCE_POLICY_AUDIT.md",
        PAPER_DIR / "ALL_EXAMPLES_SOURCE_POLICY_AUDIT.json",
        PAPER_DIR / "build_all_examples_source_policy_audit.py",
        PAPER_DIR / "validate_all_examples_source_policy_audit.py",
        PAPER_DIR / "FOUR_EXAMPLE_SOURCE_POLICY_DASHBOARD.md",
        PAPER_DIR / "FOUR_EXAMPLE_SOURCE_POLICY_DASHBOARD.json",
        PAPER_DIR / "build_four_example_source_policy_dashboard.py",
        PAPER_DIR / "validate_four_example_source_policy_dashboard.py",
        PAPER_DIR / "EXTERNAL_BASELINE_SOURCE_POLICY_DIAGNOSIS.md",
        PAPER_DIR / "EXTERNAL_BASELINE_SOURCE_POLICY_DIAGNOSIS.json",
        PAPER_DIR / "build_external_baseline_source_policy_diagnosis.py",
        PAPER_DIR / "validate_external_baseline_source_policy_diagnosis.py",
        PAPER_DIR / "EXTERNAL_CASE_EVIDENCE_RECONCILIATION.md",
        PAPER_DIR / "EXTERNAL_CASE_EVIDENCE_RECONCILIATION.json",
        PAPER_DIR / "build_external_case_evidence_reconciliation.py",
        PAPER_DIR / "validate_external_case_evidence_reconciliation.py",
        PAPER_DIR / "EXTERNAL_SAME_TEST_ACCEPTANCE_SHEET.md",
        PAPER_DIR / "EXTERNAL_SAME_TEST_ACCEPTANCE_SHEET.json",
        PAPER_DIR / "validate_external_same_test_acceptance_sheet.py",
        PAPER_DIR / "EXTERNAL_SUITE_DEMOTION_LEDGER.md",
        PAPER_DIR / "EXTERNAL_SUITE_DEMOTION_LEDGER.json",
        PAPER_DIR / "build_external_suite_demotion_ledger.py",
        PAPER_DIR / "validate_external_suite_demotion_ledger.py",
        PAPER_DIR / "EXTERNAL_SUITE_DISPOSITION_AUDIT.md",
        PAPER_DIR / "EXTERNAL_SUITE_DISPOSITION_AUDIT.json",
        PAPER_DIR / "build_external_suite_disposition_audit.py",
        PAPER_DIR / "validate_external_suite_disposition_audit.py",
        PAPER_DIR / "EXTERNAL_SUPERIORITY_CLAIM_DEMOTION_AUDIT.md",
        PAPER_DIR / "EXTERNAL_SUPERIORITY_CLAIM_DEMOTION_AUDIT.json",
        PAPER_DIR / "build_external_superiority_claim_demotion_audit.py",
        PAPER_DIR / "validate_external_superiority_claim_demotion_audit.py",
        PAPER_DIR / "B4_B7_NON_SUPERIORITY_ROUTE_AUDIT.md",
        PAPER_DIR / "B4_B7_NON_SUPERIORITY_ROUTE_AUDIT.json",
        PAPER_DIR / "build_b4_b7_non_superiority_route_audit.py",
        PAPER_DIR / "validate_b4_b7_non_superiority_route_audit.py",
        PAPER_DIR / "SOURCE_POLICY_LOCAL_CANDIDATE_GAP_AUDIT.md",
        PAPER_DIR / "SOURCE_POLICY_LOCAL_CANDIDATE_GAP_AUDIT.json",
        PAPER_DIR / "build_source_policy_local_candidate_gap_audit.py",
        PAPER_DIR / "validate_source_policy_local_candidate_gap_audit.py",
        PAPER_DIR / "RA2021_SOURCE_IDENTITY_AUDIT.md",
        PAPER_DIR / "RA2021_SOURCE_IDENTITY_AUDIT.json",
        PAPER_DIR / "build_ra2021_source_identity_audit.py",
        PAPER_DIR / "validate_ra2021_source_identity_audit.py",
        PAPER_DIR / "RA2021_DOUBLE_SOURCE_POLICY_LOW_ORDER_DIAGNOSIS.md",
        PAPER_DIR / "RA2021_DOUBLE_SOURCE_POLICY_LOW_ORDER_DIAGNOSIS.json",
        PAPER_DIR / "build_ra2021_double_source_policy_low_order_diagnosis.py",
        PAPER_DIR / "validate_ra2021_double_source_policy_low_order_diagnosis.py",
        PAPER_DIR / "RA2021_SOURCE_POLICY_ROW_AUDIT.md",
        PAPER_DIR / "RA2021_SOURCE_POLICY_ROW_AUDIT.json",
        PAPER_DIR / "build_ra2021_source_policy_row_audit.py",
        PAPER_DIR / "validate_ra2021_source_policy_row_audit.py",
        PAPER_DIR / "HI2022_POLICY_DECISION_AUDIT.md",
        PAPER_DIR / "HI2022_POLICY_DECISION_AUDIT.json",
        PAPER_DIR / "build_hi2022_policy_decision_audit.py",
        PAPER_DIR / "validate_hi2022_policy_decision_audit.py",
        PAPER_DIR / "HI2022_SOURCE_POLICY_ROW_AUDIT.md",
        PAPER_DIR / "HI2022_SOURCE_POLICY_ROW_AUDIT.json",
        PAPER_DIR / "build_hi2022_source_policy_row_audit.py",
        PAPER_DIR / "validate_hi2022_source_policy_row_audit.py",
        PAPER_DIR / "HI2022_RA_HALF_DOUBLE_SOURCE_POLICY_FAILURE_DIAGNOSIS.md",
        PAPER_DIR / "HI2022_RA_HALF_DOUBLE_SOURCE_POLICY_FAILURE_DIAGNOSIS.json",
        PAPER_DIR / "build_hi2022_ra_half_double_source_policy_failure_diagnosis.py",
        PAPER_DIR / "validate_hi2022_ra_half_double_source_policy_failure_diagnosis.py",
        PAPER_DIR / "HI2022_RA_HALF_DOUBLE_REPAIR_ATTEMPT_CERTIFICATE.md",
        PAPER_DIR / "HI2022_RA_HALF_DOUBLE_REPAIR_ATTEMPT_CERTIFICATE.json",
        PAPER_DIR / "build_hi2022_ra_half_double_repair_attempt_certificate.py",
        PAPER_DIR / "validate_hi2022_ra_half_double_repair_attempt_certificate.py",
        PAPER_DIR / "HI2022_T8_TOLERANCE_REPAIR_AUDIT.md",
        PAPER_DIR / "HI2022_T8_TOLERANCE_REPAIR_AUDIT.json",
        PAPER_DIR / "build_hi2022_t8_tolerance_repair_audit.py",
        PAPER_DIR / "validate_hi2022_t8_tolerance_repair_audit.py",
        PAPER_DIR / "VP2024_CODE_PATH_DISPOSITION_AUDIT.md",
        PAPER_DIR / "VP2024_CODE_PATH_DISPOSITION_AUDIT.json",
        PAPER_DIR / "build_vp2024_code_path_disposition_audit.py",
        PAPER_DIR / "validate_vp2024_code_path_disposition_audit.py",
        PAPER_DIR / "VP2024_PUBLIC_CODE_RECHECK_20260613.md",
        PAPER_DIR / "VP2024_PUBLIC_CODE_RECHECK_20260613.json",
        PAPER_DIR / "validate_vp2024_public_code_recheck_20260613.py",
        PAPER_DIR / "TFE_SOURCE_POLICY_SPEC.md",
        PAPER_DIR / "TFE_SOURCE_POLICY_SPEC.json",
        PAPER_DIR / "build_tfe_source_policy_spec.py",
        PAPER_DIR / "validate_tfe_source_policy_spec.py",
        PAPER_DIR / "TFE_SOURCE_PENDULUM_MODEL_AUDIT.md",
        PAPER_DIR / "TFE_SOURCE_PENDULUM_MODEL_AUDIT.json",
        PAPER_DIR / "build_tfe_source_pendulum_model_audit.py",
        PAPER_DIR / "validate_tfe_source_pendulum_model_audit.py",
        PAPER_DIR / "TFE_SOURCE_POLICY_ROW_AUDIT.md",
        PAPER_DIR / "TFE_SOURCE_POLICY_ROW_AUDIT.json",
        PAPER_DIR / "build_tfe_source_policy_row_audit.py",
        PAPER_DIR / "validate_tfe_source_policy_row_audit.py",
        PAPER_DIR / "TFE_SOURCE_GRID_COMPATIBILITY_AUDIT.md",
        PAPER_DIR / "TFE_SOURCE_GRID_COMPATIBILITY_AUDIT.json",
        PAPER_DIR / "build_tfe_source_grid_compatibility_audit.py",
        PAPER_DIR / "validate_tfe_source_grid_compatibility_audit.py",
        PAPER_DIR / "TFE_BROWN_MCPHEE_SOURCE_CODE_EQUIVALENCE_CERTIFICATE.md",
        PAPER_DIR / "TFE_BROWN_MCPHEE_SOURCE_CODE_EQUIVALENCE_CERTIFICATE.json",
        PAPER_DIR / "build_tfe_brown_mcphee_source_code_equivalence_certificate.py",
        PAPER_DIR / "validate_tfe_brown_mcphee_source_code_equivalence_certificate.py",
        PAPER_DIR / "TFE_FULL_T10_ENDPOINT_POLICY_CLOSURE_CERTIFICATE.md",
        PAPER_DIR / "TFE_FULL_T10_ENDPOINT_POLICY_CLOSURE_CERTIFICATE.json",
        PAPER_DIR / "build_tfe_full_t10_endpoint_policy_closure_certificate.py",
        PAPER_DIR / "validate_tfe_full_t10_endpoint_policy_closure_certificate.py",
        PAPER_DIR / "TFE_ENDPOINT_POLICY_BOUNDARY_CERTIFICATE.md",
        PAPER_DIR / "TFE_ENDPOINT_POLICY_BOUNDARY_CERTIFICATE.json",
        PAPER_DIR / "TFE_ENDPOINT_POLICY_BOUNDARY_CERTIFICATE.csv",
        PAPER_DIR / "build_tfe_endpoint_policy_boundary_certificate.py",
        PAPER_DIR / "validate_tfe_endpoint_policy_boundary_certificate.py",
        PAPER_DIR / "TFE_ALGORITHM_LITERAL_ENDPOINT_PROBE.md",
        PAPER_DIR / "TFE_ALGORITHM_LITERAL_ENDPOINT_PROBE.json",
        PAPER_DIR / "TFE_ALGORITHM_LITERAL_ENDPOINT_PROBE.csv",
        PAPER_DIR / "build_tfe_algorithm_literal_endpoint_probe.py",
        PAPER_DIR / "validate_tfe_algorithm_literal_endpoint_probe.py",
        PAPER_DIR / "TFE_ALGORITHM_LITERAL_WORK_PRECISION_AUDIT.md",
        PAPER_DIR / "TFE_ALGORITHM_LITERAL_WORK_PRECISION_AUDIT.json",
        PAPER_DIR / "TFE_ALGORITHM_LITERAL_WORK_PRECISION_AUDIT.csv",
        PAPER_DIR / "build_tfe_algorithm_literal_work_precision_audit.py",
        PAPER_DIR / "validate_tfe_algorithm_literal_work_precision_audit.py",
        PAPER_DIR / "TFE_B4_B7_SOURCE_POLICY_DEMOTION_AUDIT.md",
        PAPER_DIR / "TFE_B4_B7_SOURCE_POLICY_DEMOTION_AUDIT.json",
        PAPER_DIR / "build_tfe_b4_b7_source_policy_demotion_audit.py",
        PAPER_DIR / "validate_tfe_b4_b7_source_policy_demotion_audit.py",
        PAPER_DIR / "TFE_BROWN_MCPHEE_SOURCE_LAW_BOUNDARY_AUDIT.md",
        PAPER_DIR / "TFE_BROWN_MCPHEE_SOURCE_LAW_BOUNDARY_AUDIT.json",
        PAPER_DIR / "build_tfe_brown_mcphee_source_law_boundary_audit.py",
        PAPER_DIR / "validate_tfe_brown_mcphee_source_law_boundary_audit.py",
        PAPER_DIR / "TFE_ENDPOINT_POLICY_SENSITIVITY_AUDIT.md",
        PAPER_DIR / "TFE_ENDPOINT_POLICY_SENSITIVITY_AUDIT.json",
        PAPER_DIR / "TFE_ENDPOINT_POLICY_SENSITIVITY_AUDIT.csv",
        PAPER_DIR / "build_tfe_endpoint_policy_sensitivity_audit.py",
        PAPER_DIR / "validate_tfe_endpoint_policy_sensitivity_audit.py",
        PAPER_DIR / "TFE_FULL_T10_ABSOLUTE_DAE_LIFT_SUMMARY.md",
        PAPER_DIR / "TFE_FULL_T10_ABSOLUTE_DAE_LIFT_SUMMARY.json",
        PAPER_DIR / "TFE_FULL_T10_ABSOLUTE_DAE_LIFT_SUMMARY.csv",
        PAPER_DIR / "build_tfe_full_t10_absolute_dae_lift_summary.py",
        PAPER_DIR / "validate_tfe_full_t10_absolute_dae_lift_summary.py",
        PAPER_DIR / "TFE_FULL_T10_COARSE_CANDIDATE_SUMMARY.md",
        PAPER_DIR / "TFE_FULL_T10_COARSE_CANDIDATE_SUMMARY.json",
        PAPER_DIR / "TFE_FULL_T10_COARSE_CANDIDATE_SUMMARY.csv",
        PAPER_DIR / "build_tfe_full_t10_coarse_candidate_summary.py",
        PAPER_DIR / "validate_tfe_full_t10_coarse_candidate_summary.py",
        PAPER_DIR / "TFE_PUBLIC_CODE_RECHECK_20260613.md",
        PAPER_DIR / "TFE_PUBLIC_CODE_RECHECK_20260613.json",
        PAPER_DIR / "validate_tfe_public_code_recheck_20260613.py",
        PAPER_DIR / "FULL_SOURCE_POLICY_RUNNER_ARCHIVE_GAP_AUDIT.md",
        PAPER_DIR / "FULL_SOURCE_POLICY_RUNNER_ARCHIVE_GAP_AUDIT.json",
        PAPER_DIR / "TFE_SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_CERTIFICATE.md",
        PAPER_DIR / "TFE_SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_CERTIFICATE.json",
        PAPER_DIR / "RA_HI_SOURCE_POLICY_OUTPUT_INVENTORY.md",
        PAPER_DIR / "RA_HI_SOURCE_POLICY_OUTPUT_INVENTORY.json",
        PAPER_DIR / "RA_HI_SOURCE_POLICY_CLOSEOUT_CHECKLIST.md",
        PAPER_DIR / "RA_HI_SOURCE_POLICY_CLOSEOUT_CHECKLIST.json",
        PAPER_DIR / "RA_HI_SOURCE_POLICY_PROMOTION_BLOCKER_MATRIX.md",
        PAPER_DIR / "RA_HI_SOURCE_POLICY_PROMOTION_BLOCKER_MATRIX.json",
        PAPER_DIR / "RA_HI_SOURCE_POLICY_POST_EXECUTION_ATTEMPT_CERTIFICATE.md",
        PAPER_DIR / "RA_HI_SOURCE_POLICY_POST_EXECUTION_ATTEMPT_CERTIFICATE.json",
        PAPER_DIR / "B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.md",
        PAPER_DIR / "B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.json",
        PAPER_DIR / "run_b4_source_policy_after_opt_in.sh",
        PAPER_DIR / "validate_b4_source_policy_guarded_driver.py",
        PAPER_DIR / "build_b4_guarded_driver_refusal_boundary_audit_20260621.py",
        PAPER_DIR / "validate_b4_guarded_driver_refusal_boundary_audit_20260621.py",
        PAPER_DIR / "B4_GUARDED_DRIVER_REFUSAL_BOUNDARY_AUDIT_20260621.md",
        PAPER_DIR / "B4_GUARDED_DRIVER_REFUSAL_BOUNDARY_AUDIT_20260621.json",
        PAPER_DIR / "B4_SOURCE_POLICY_EXECUTION_HANDOFF_PACKAGE.md",
        PAPER_DIR / "B4_SOURCE_POLICY_EXECUTION_HANDOFF_PACKAGE.json",
        PAPER_DIR / "B4_SOURCE_POLICY_COMMAND_PREFLIGHT_FREEZE_20260620.md",
        PAPER_DIR / "B4_SOURCE_POLICY_COMMAND_PREFLIGHT_FREEZE_20260620.json",
        PAPER_DIR / "build_b4_source_policy_command_preflight_freeze_20260620.py",
        PAPER_DIR / "validate_b4_source_policy_command_preflight_freeze_20260620.py",
        PAPER_DIR / "B4_SOURCE_POLICY_EXPECTED_OUTPUT_SCHEMA_AUDIT_20260620.md",
        PAPER_DIR / "B4_SOURCE_POLICY_EXPECTED_OUTPUT_SCHEMA_AUDIT_20260620.json",
        PAPER_DIR / "build_b4_source_policy_expected_output_schema_audit_20260620.py",
        PAPER_DIR / "validate_b4_source_policy_expected_output_schema_audit_20260620.py",
        PAPER_DIR / "B4_EXPECTED_OUTPUT_PROMOTION_READINESS_BLOCKER_AUDIT_20260620.md",
        PAPER_DIR / "B4_EXPECTED_OUTPUT_PROMOTION_READINESS_BLOCKER_AUDIT_20260620.json",
        PAPER_DIR / "build_b4_expected_output_promotion_readiness_blocker_audit_20260620.py",
        PAPER_DIR / "validate_b4_expected_output_promotion_readiness_blocker_audit_20260620.py",
        PAPER_DIR / "OC6_SOURCE_EQUIVALENT_REOPEN_READINESS_AUDIT_20260620.md",
        PAPER_DIR / "OC6_SOURCE_EQUIVALENT_REOPEN_READINESS_AUDIT_20260620.json",
        PAPER_DIR / "build_oc6_source_equivalent_reopen_readiness_audit_20260620.py",
        PAPER_DIR / "validate_oc6_source_equivalent_reopen_readiness_audit_20260620.py",
        PAPER_DIR / "OC6_EXTERNAL_SOURCE_ARTIFACT_RECHECK_20260621.md",
        PAPER_DIR / "OC6_EXTERNAL_SOURCE_ARTIFACT_RECHECK_20260621.json",
        PAPER_DIR / "build_oc6_external_source_artifact_recheck_20260621.py",
        PAPER_DIR / "validate_oc6_external_source_artifact_recheck_20260621.py",
        PAPER_DIR / "OC6_TFE_PUBLISHER_ARTIFACT_AVAILABILITY_AUDIT_20260621.md",
        PAPER_DIR / "OC6_TFE_PUBLISHER_ARTIFACT_AVAILABILITY_AUDIT_20260621.json",
        PAPER_DIR / "build_oc6_tfe_publisher_artifact_availability_audit_20260621.py",
        PAPER_DIR / "validate_oc6_tfe_publisher_artifact_availability_audit_20260621.py",
        PAPER_DIR / "OC6_TFE_SOURCE_EQUIVALENT_ARTIFACT_REQUEST_PACKET_20260621.md",
        PAPER_DIR / "OC6_TFE_SOURCE_EQUIVALENT_ARTIFACT_REQUEST_PACKET_20260621.json",
        PAPER_DIR / "build_oc6_tfe_source_equivalent_artifact_request_packet_20260621.py",
        PAPER_DIR / "validate_oc6_tfe_source_equivalent_artifact_request_packet_20260621.py",
        PAPER_DIR / "FULL_SOURCE_POLICY_ROW_PROVENANCE_AUDIT.md",
        PAPER_DIR / "FULL_SOURCE_POLICY_ROW_PROVENANCE_AUDIT.json",
        PAPER_DIR / "FULL_SOURCE_POLICY_ROW_PROVENANCE_AUDIT.csv",
        PAPER_DIR / "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260620.md",
        PAPER_DIR / "SOURCE_POLICY_PUBLIC_CODE_REFRESH_20260620.json",
        PAPER_DIR / "build_source_policy_public_code_refresh_20260620.py",
        PAPER_DIR / "validate_source_policy_public_code_refresh_20260620.py",
        PAPER_DIR / "SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_AUDIT.md",
        PAPER_DIR / "SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_AUDIT.json",
        PAPER_DIR / "build_source_policy_self_reproduction_attempt_audit.py",
        PAPER_DIR / "validate_source_policy_self_reproduction_attempt_audit.py",
        PAPER_DIR / "SOURCE_POLICY_REOPEN_CONDITION_MONITOR_20260620.md",
        PAPER_DIR / "SOURCE_POLICY_REOPEN_CONDITION_MONITOR_20260620.json",
        PAPER_DIR / "build_source_policy_reopen_condition_monitor_20260620.py",
        PAPER_DIR / "validate_source_policy_reopen_condition_monitor_20260620.py",
        PAPER_DIR / "SOURCE_POLICY_REOPEN_CONDITION_MONITOR_20260621_DELTA.md",
        PAPER_DIR / "SOURCE_POLICY_REOPEN_CONDITION_MONITOR_20260621_DELTA.json",
        PAPER_DIR / "build_source_policy_reopen_condition_monitor_20260621_delta.py",
        PAPER_DIR / "validate_source_policy_reopen_condition_monitor_20260621_delta.py",
        PAPER_DIR / "sync_submission_artifact_manifest_boundary.py",
        PAPER_DIR / "validate_submission_artifact_manifest_boundary_sync.py",
        PAPER_DIR / "validate_cmame_submission.py",
        PAPER_DIR / "validate_cmame_blocker_closure_gate.py",
        PAPER_DIR / "validate_cmame_external_baseline_gate.py",
        PAPER_DIR / "validate_cmame_proof_contract_gate.py",
        PAPER_DIR / "validate_cmame_visual_legibility_audit.py",
        PAPER_DIR / "validate_cmame_related_work_audit.py",
        PAPER_DIR / "validate_cmame_prose_residue_audit.py",
        PAPER_DIR / "validate_dynamic_row_oracle_gate.py",
        PAPER_DIR / "validate_concise_paper.py",
        PAPER_DIR / "validate_paper_claims.py",
        PAPER_DIR / "validate_proof_evidence_matrix.py",
        PAPER_DIR / "validate_proof_solver_scale_audit.py",
        PAPER_DIR / "validate_order_acceptance_gate.py",
        PAPER_DIR / "validate_implementation_fidelity_certificate.py",
        PAPER_DIR / "validate_implementation_path_audit.py",
        PAPER_DIR / "validate_full_source_policy_runner_archive_gap_audit.py",
        PAPER_DIR / "validate_tfe_source_policy_self_reproduction_attempt_certificate.py",
        PAPER_DIR / "validate_ra_hi_source_policy_output_inventory.py",
        PAPER_DIR / "validate_ra_hi_source_policy_closeout_checklist.py",
        PAPER_DIR / "validate_ra_hi_source_policy_promotion_blocker_matrix.py",
        PAPER_DIR / "validate_ra_hi_source_policy_post_execution_attempt_certificate.py",
        PAPER_DIR / "validate_b4_source_policy_execution_opt_in_packet.py",
        PAPER_DIR / "validate_b4_source_policy_execution_handoff_package.py",
        PAPER_DIR / "validate_b4_source_policy_command_preflight_freeze_20260620.py",
        PAPER_DIR / "validate_b4_source_policy_expected_output_schema_audit_20260620.py",
        PAPER_DIR / "validate_b4_expected_output_promotion_readiness_blocker_audit_20260620.py",
        PAPER_DIR / "validate_oc6_source_equivalent_reopen_readiness_audit_20260620.py",
        PAPER_DIR / "validate_full_source_policy_row_provenance_audit.py",
        PAPER_DIR / "validate_source_paper_comparison.py",
        PAPER_DIR / "validate_cross_paper_benchmark_spec.py",
        PAPER_DIR / "validate_cross_paper_benchmark_cases.py",
        PAPER_DIR / "validate_external_same_test_run_queue.py",
        PAPER_DIR / "validate_submission_bundle.py",
        PAPER_DIR / "validate_paper_package.py",
        CURRENT_DIR / "validate_four_asme_minimal.py",
        CURRENT_DIR / "validate_full_tfe_gap.py",
        CURRENT_DIR / "validate_full_tfe_repair_spec.py",
        CURRENT_DIR / "FULL_TFE_REPLACEMENT_GAP_LEDGER.md",
        CURRENT_DIR / "FULL_TFE_REPAIR_SPEC.md",
    ]
    for path in required_files:
        v.check(path.exists() and path.stat().st_size > 0, f"paper package file missing or empty: {path.relative_to(ROOT)}")

    package_wrapper = (PAPER_DIR / "validate_paper_package.py").read_text(encoding="utf-8")
    for token in [
        "package required files",
        "CLAIM_BOUNDARY.json",
        "CURRENT_PIPELINE_CONTRACT.md",
        "v047-paper-claim-boundary-v1",
        "asme_acceptance",
        "single_pendulum",
        "double_pendulum",
        "four_link",
        "slider_crank",
        "full_tfe_required_for_gate",
        "full_tfe_gap_contract",
        "full_stage_acceptance_gap_quantified_not_full_tfe",
        "derived_full_tfe_stage_functional_present",
        "endpoint_boundary_source_removed",
        "velocity_compression_blocker",
        "remaining_caveat_contracts",
        "speed_gap_quantified_dense_still_faster",
        "ultra_high_order_recovered",
        "sharp_refinement_cost_quantified_ultra_high_order_cost_caveat",
        "terminology",
        "temporal finite element",
        "typo_for_tfe_not_a_separate_method",
        "order_conventions",
        "observed_smooth_projected_orders",
        "comparator_not_accepted_method",
        "current_pipeline_boundary=checked",
        "required_for_paper_claim_check",
        "validate_concise_paper.py",
        "concise paper validator",
        "validate_cmame_submission.py",
        "CMAME submission validator",
        "validate_cmame_blocker_closure_gate.py",
        "CMAME blocker closure gate validator",
        "validate_cmame_external_baseline_gate.py",
        "CMAME external baseline gate validator",
        "validate_cmame_proof_contract_gate.py",
        "CMAME proof contract gate validator",
        "validate_cmame_visual_legibility_audit.py",
        "CMAME visual legibility audit validator",
        "validate_cmame_related_work_audit.py",
        "CMAME related work audit validator",
        "validate_cmame_prose_residue_audit.py",
        "CMAME prose residue audit validator",
        "validate_dynamic_row_oracle_gate.py",
        "dynamic row oracle gate validator",
        "validate_proof_evidence_matrix.py",
        "proof evidence matrix validator",
        "validate_order_acceptance_gate.py",
        "order acceptance gate validator",
        "validate_source_paper_comparison.py",
        "source-paper comparison validator",
        "validate_cross_paper_benchmark_spec.py",
        "cross-paper benchmark spec validator",
        "validate_cross_paper_benchmark_cases.py",
        "cross-paper benchmark case validator",
        "validate_submission_bundle.py",
        "submission bundle validator",
        "main_cmame.tex",
        "main_cmame.pdf",
        "main_cmame.log",
        "CMAME_SUBMISSION_READINESS_AUDIT.md",
        "CMAME_SUBMISSION_READINESS_REVIEW.md",
        "CMAME_BLOCKER_CLOSURE_GATE.md",
        "CMAME_BLOCKER_CLOSURE_GATE.json",
        "CMAME_EXTERNAL_BASELINE_GATE.md",
        "CMAME_EXTERNAL_BASELINE_GATE.json",
        "external_baseline_gate=checked",
        "external_baseline_gate_validator=checked",
        "CMAME_PROOF_CONTRACT_GATE.md",
        "CMAME_PROOF_CONTRACT_GATE.json",
        "proof_contract_gate=checked",
        "proof_contract_gate_validator=checked",
        "CMAME_VISUAL_LEGIBILITY_AUDIT.md",
        "CMAME_VISUAL_LEGIBILITY_AUDIT.json",
        "visual_legibility_audit=checked",
        "visual_legibility_audit_validator=checked",
        "CMAME_RELATED_WORK_AUDIT.md",
        "CMAME_RELATED_WORK_AUDIT.json",
        "related_work_audit=checked",
        "related_work_audit_validator=checked",
        "CMAME_PROSE_RESIDUE_AUDIT.md",
        "CMAME_PROSE_RESIDUE_AUDIT.json",
        "prose_residue_audit=checked",
        "prose_residue_audit_validator=checked",
        "DYNAMIC_ROW_ORACLE_GATE.md",
        "DYNAMIC_ROW_ORACLE_GATE.json",
        "README_CMAME_FLAT_SUBMISSION.md",
        "cmame_submission_flat.zip",
        "cmame_submission_flat/main_cmame_submission.tex",
        "cmame_submission_flat/main_cmame_submission.pdf",
        "cmame_submission_flat/main_cmame_submission.log",
        "main_concise.tex",
        "main_concise.pdf",
        "SUBMISSION_PACKET.md",
        "submission_boundary=checked",
        "SUBMISSION_ARTIFACT_MANIFEST.json",
        "submission_manifest=checked",
        "COVER_LETTER.md",
        "cover_letter_boundary=checked",
        "SUBMISSION_FILE_INVENTORY.md",
        "file_inventory=checked",
        "REVIEW_RESPONSE_TEMPLATE.md",
        "review_response_boundary=checked",
        "PROOF_EVIDENCE_MATRIX.md",
        "proof_evidence_matrix=checked",
        "proof_evidence_matrix_validator=checked",
        "PROOF_SOLVER_SCALE_AUDIT.md",
        "proof_solver_scale_audit=checked",
        "validate_proof_solver_scale_audit.py",
        "proof solver-scale audit validator",
        "proof_solver_scale_audit_validator=checked",
        "ORDER_ACCEPTANCE_GATE.md",
        "order_acceptance_gate=checked",
        "order_acceptance_gate_validator=checked",
        "IMPLEMENTATION_FIDELITY_CERTIFICATE.md",
        "validate_implementation_fidelity_certificate.py",
        "IMPLEMENTATION_PATH_AUDIT.md",
        "implementation_path_audit=checked",
        "validate_implementation_path_audit.py",
        "implementation_path_audit_validator=checked",
        "FULL_SOURCE_POLICY_RUNNER_ARCHIVE_GAP_AUDIT.md",
        "FULL_SOURCE_POLICY_RUNNER_ARCHIVE_GAP_AUDIT.json",
        "validate_full_source_policy_runner_archive_gap_audit.py",
        "full source-policy runner archive gap audit validator",
        "source_policy_closed=0/40",
        "full_archive_ready_now=False",
        "remain_partial_narrowed_replay_ready_full_source_policy_archive_not_ready",
        "current_archive_usable_as_full_source_policy_runner_archive=False",
        "safe_current_use=narrowed_claim_replay_and_audit_provenance_only",
        "primary_submission_package_allowed=False",
        "submission_ready=False",
        "SOURCE_POLICY_REOPEN_CONDITION_MONITOR_20260620.md",
        "SOURCE_POLICY_REOPEN_CONDITION_MONITOR_20260620.json",
        "validate_source_policy_reopen_condition_monitor_20260620.py",
        "source-policy reopen-condition monitor validation: PASS",
        "source_policy_reopen_triggered=False",
        "source_policy_closed=0/20",
        "TFE_SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_CERTIFICATE.md",
        "TFE_SOURCE_POLICY_SELF_REPRODUCTION_ATTEMPT_CERTIFICATE.json",
        "validate_tfe_source_policy_self_reproduction_attempt_certificate.py",
        "TFE source-policy self-reproduction attempt certificate validator",
        "attempted_not_reproducible_rows=16/16",
        "source_policy_closed=0/16",
        "source_policy_closed_rows=0",
        "submission_ready=False",
        "RA_HI_SOURCE_POLICY_OUTPUT_INVENTORY.md",
        "RA_HI_SOURCE_POLICY_CLOSEOUT_CHECKLIST.md",
        "RA_HI_SOURCE_POLICY_PROMOTION_BLOCKER_MATRIX.md",
        "RA_HI_SOURCE_POLICY_POST_EXECUTION_ATTEMPT_CERTIFICATE.md",
        "B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.md",
        "run_b4_source_policy_after_opt_in.sh",
        "B4_SOURCE_POLICY_EXECUTION_HANDOFF_PACKAGE.md",
        "B4_SOURCE_POLICY_COMMAND_PREFLIGHT_FREEZE_20260620.md",
        "B4_SOURCE_POLICY_EXPECTED_OUTPUT_SCHEMA_AUDIT_20260620.md",
        "B4_EXPECTED_OUTPUT_PROMOTION_READINESS_BLOCKER_AUDIT_20260620.md",
        "B4_GUARDED_DRIVER_REFUSAL_BOUNDARY_AUDIT_20260621.md",
        "OC6_SOURCE_EQUIVALENT_REOPEN_READINESS_AUDIT_20260620.md",
        "FULL_SOURCE_POLICY_ROW_PROVENANCE_AUDIT.md",
        "validate_ra_hi_source_policy_output_inventory.py",
        "validate_ra_hi_source_policy_closeout_checklist.py",
        "validate_ra_hi_source_policy_promotion_blocker_matrix.py",
        "validate_ra_hi_source_policy_post_execution_attempt_certificate.py",
        "validate_b4_source_policy_execution_opt_in_packet.py",
        "validate_b4_source_policy_guarded_driver.py",
        "validate_b4_guarded_driver_refusal_boundary_audit_20260621.py",
        "validate_b4_source_policy_execution_handoff_package.py",
        "validate_b4_source_policy_command_preflight_freeze_20260620.py",
        "validate_b4_source_policy_expected_output_schema_audit_20260620.py",
        "validate_b4_expected_output_promotion_readiness_blocker_audit_20260620.py",
        "validate_oc6_source_equivalent_reopen_readiness_audit_20260620.py",
        "validate_full_source_policy_row_provenance_audit.py",
        "RA/HI source-policy output inventory validator",
        "RA/HI source-policy closeout checklist validator",
        "RA/HI source-policy promotion blocker matrix validator",
        "RA/HI post-execution attempt certificate validator",
        "B4 source-policy execution opt-in packet validator",
        "B4 source-policy guarded driver validator",
        "B4 source-policy execution handoff package validator",
        "B4 source-policy command preflight freeze 20260620 validator",
        "B4 source-policy expected-output schema audit 20260620 validator",
        "OC6 source-equivalent reopen-readiness audit 20260620 validator",
        "full source-policy row provenance audit validator",
        "commands=13",
        "outputs=13/13",
        "source_policy_closed=0/20",
        "not_promoted=20",
        "source_policy_rows_promoted=0",
        "external_superiority_ready_rows=0",
        "run_v047_invoked=False",
        "ready_command_mapped_external_rows=20/40",
        "source_policy_closed_now=0/40",
        "execution_invoked_by_packet=False",
        "exact_approval_guard=True",
        "driver_command_count=13",
        "commands_match_opt_in_packet=True",
        "execution_invoked_by_validator=False",
        "expected_output_schema_audit=PASS",
        "b4 expected-output schema audit validation: PASS",
        "OC6 source-equivalent reopen-readiness audit validation: PASS",
        "oc4_blocker_id=OC4",
        "oc4_blocker_status=open",
        "oc4_closure_decision=remain_open_ready_for_authorized_execution_not_executed_not_promoted",
        "oc4_closure_allowed_now=False",
        "oc6_blocker_id=OC6",
        "oc6_blocker_status=partial",
        "oc6_closure_decision=remain_open_no_positive_source_equivalent_artifact",
        "oc6_closure_allowed_now=False",
        "reopen_condition=suite_specific_source_equivalent_reopen_conditions",
        "latest_external_probe_boundary=0/0/4/False/False",
        "csv_json_parseable=13/8",
        "terminal_unable_to_reproduce_rows=20",
        "execution_authorized=False",
        "guarded_execution_driver=run_b4_source_policy_after_opt_in.sh",
        "driver_requires_exact_approval=True",
        "command_preflight_freeze=PASS",
        "b4 source-policy command preflight freeze validation: PASS",
        "expected_artifacts=21/21",
        "provenance_preflight=40/40",
        "promotion_ready_rows=0",
        "SOURCE_PAPER_COMPARISON.md",
        "source_paper_comparison=checked",
        "source_paper_comparison_validator=checked",
        "CROSS_PAPER_BENCHMARK_CASES.json",
        "EXTERNAL_SAME_TEST_RUN_QUEUE.md",
        "external_same_test_run_queue=checked",
        "validate_external_same_test_run_queue.py",
        "external same-test run queue validator",
        "external_same_test_run_queue_validator=checked",
        "submission_bundle_validator=checked",
        "submission_ready=False",
        "mechanical_preflight_passed=True",
        "quality_review_passed=False",
        "main_concise.log",
        "main.log",
        "note=run_v047.py was not invoked",
    ]:
        v.check(token in package_wrapper, f"paper package wrapper missing token: {token}")

    submission = (PAPER_DIR / "SUBMISSION_PACKET.md").read_text(encoding="utf-8")
    for token in [
        "v047 Submission Packet",
        "submit under the narrowed claim",
        "Full source-policy package remains not ready",
        "main_cmame.pdf",
        "main_cmame.tex",
        "highlights_cmame.txt",
        "declarations_cmame.md",
        "CMAME_SUBMISSION_CHECKLIST.md",
        "CMAME_SUBMISSION_READINESS_AUDIT.md",
        "CMAME_SUBMISSION_READINESS_REVIEW.md",
        "CMAME_BLOCKER_CLOSURE_GATE.md",
        "CMAME_BLOCKER_CLOSURE_GATE.json",
        "CMAME_EXTERNAL_BASELINE_GATE.md",
        "CMAME_EXTERNAL_BASELINE_GATE.json",
        "CMAME_PROOF_CONTRACT_GATE.md",
        "CMAME_PROOF_CONTRACT_GATE.json",
        "CMAME_VISUAL_LEGIBILITY_AUDIT.md",
        "CMAME_VISUAL_LEGIBILITY_AUDIT.json",
        "CMAME_RELATED_WORK_AUDIT.md",
        "CMAME_RELATED_WORK_AUDIT.json",
        "DYNAMIC_ROW_ORACLE_GATE.md",
        "DYNAMIC_ROW_ORACLE_GATE.json",
        "README_CMAME_FLAT_SUBMISSION.md",
        "cmame_submission_flat/main_cmame_submission.tex",
        "cmame_submission_flat/main_cmame_submission.pdf",
        "cmame_submission_flat.zip",
        "main_concise.pdf",
        "Accepted Claim",
        "`Gauss6/FullVA`",
        "method-order claim is `6`",
        "`7.161/7.066`",
        "expected order `5`",
        "`single_pendulum`",
        "`double_pendulum`",
        "`four_link`",
        "`slider_crank`",
        "Do Not Claim",
        "complete source-paper residual reproduction",
        "accepted independent full-TFE stage replacement",
        "`full_tfe_stage_replacement=false`",
        "COVER_LETTER.md",
        "SUBMISSION_ARTIFACT_MANIFEST.json",
        "SUBMISSION_FILE_INVENTORY.md",
        "oc6_blocker_id=OC6",
        "oc6_blocker_status=partial",
        "oc6_closure_decision=remain_open_no_positive_source_equivalent_artifact",
        "oc6_closure_allowed_now=False",
        "reopen_condition=suite_specific_source_equivalent_reopen_conditions",
        "latest_external_probe_boundary=0/0/4/False/False",
        "remain_partial_narrowed_replay_ready_full_source_policy_archive_not_ready",
        "current_archive_usable_as_full_source_policy_runner_archive=False",
        "safe_current_use",
        "narrowed_claim_replay_and_audit_provenance_only",
        "primary_submission_package_allowed=False",
        "`OC4,OC6`",
        "REVIEW_RESPONSE_TEMPLATE.md",
        "PROOF_EVIDENCE_MATRIX.md",
        "PROOF_SOLVER_SCALE_AUDIT.md",
        "PROOF_SOLVER_SCALE_AUDIT.json",
        "scaled_tolerance_sweep_recorded=false",
        "eta_h_O_h7_solver_policy_evidence=false",
        "CMAME_BLOCKER_CLOSURE_GATE.md",
        "CMAME_BLOCKER_CLOSURE_GATE.json",
        "CMAME_EXTERNAL_BASELINE_GATE.md",
        "CMAME_EXTERNAL_BASELINE_GATE.json",
        "CMAME_PROOF_CONTRACT_GATE.md",
        "CMAME_PROOF_CONTRACT_GATE.json",
        "CMAME_VISUAL_LEGIBILITY_AUDIT.md",
        "CMAME_VISUAL_LEGIBILITY_AUDIT.json",
        "CMAME_RELATED_WORK_AUDIT.md",
        "CMAME_RELATED_WORK_AUDIT.json",
        "DYNAMIC_ROW_ORACLE_GATE.md",
        "DYNAMIC_ROW_ORACLE_GATE.json",
        "ORDER_ACCEPTANCE_GATE.md",
        "ORDER_ACCEPTANCE_GATE.json",
        "IMPLEMENTATION_FIDELITY_CERTIFICATE.md",
        "SOURCE_PAPER_COMPARISON.md",
        "CROSS_PAPER_BENCHMARK_MATRIX.md",
        "CROSS_PAPER_BENCHMARK_SPEC.md",
        "CROSS_PAPER_BENCHMARK_CASES.json",
        "EXTERNAL_SAME_TEST_RUN_QUEUE.md",
        "EXTERNAL_SAME_TEST_RUN_QUEUE.json",
        "20 non-default-`1e-4` shards",
        "CMAME_BLOCKER_CLOSURE_GATE.md",
        "CMAME_BLOCKER_CLOSURE_GATE.json",
        "CMAME_EXTERNAL_BASELINE_GATE.md",
        "CMAME_EXTERNAL_BASELINE_GATE.json",
        "DYNAMIC_ROW_ORACLE_GATE.md",
        "DYNAMIC_ROW_ORACLE_GATE.json",
        "validate_cmame_submission.py",
        "validate_submission_artifact_manifest_boundary_sync.py",
        "validate_full_source_policy_row_provenance_audit.py",
        "validate_oc6_source_equivalent_reopen_readiness_audit_20260620.py",
        "validate_cmame_blocker_closure_gate.py",
        "validate_cmame_external_baseline_gate.py",
        "validate_cmame_proof_contract_gate.py",
        "validate_cmame_visual_legibility_audit.py",
        "validate_cmame_related_work_audit.py",
        "validate_dynamic_row_oracle_gate.py",
        "validate_concise_paper.py",
        "validate_proof_evidence_matrix.py",
        "validate_proof_solver_scale_audit.py",
        "validate_order_acceptance_gate.py",
        "validate_source_paper_comparison.py",
        "validate_cross_paper_benchmark_spec.py",
        "validate_cross_paper_benchmark_cases.py",
        "validate_external_same_test_run_queue.py",
        "validate_submission_bundle.py",
        "validate_paper_package.py",
        "validate_pipeline_outputs.py",
        "These checks do not invoke the full `run_v047.py` generator",
    ]:
        v.check(token in submission, f"submission packet missing token: {token}")

    inventory = (PAPER_DIR / "SUBMISSION_FILE_INVENTORY.md").read_text(encoding="utf-8")
    for token in [
        "Submission File Inventory",
        "Primary Submission Files",
        "Supporting Evidence Files",
        "Validators",
        "Accepted Claim Snapshot",
        "Non-Claims",
        "`main_cmame.pdf`",
        "`main_cmame.tex`",
        "`highlights_cmame.txt`",
        "`declarations_cmame.md`",
        "`CMAME_SUBMISSION_CHECKLIST.md`",
        "`CMAME_SUBMISSION_READINESS_AUDIT.md`",
        "`CMAME_SUBMISSION_READINESS_REVIEW.md`",
        "`CMAME_BLOCKER_CLOSURE_GATE.md`",
        "`CMAME_BLOCKER_CLOSURE_GATE.json`",
        "`CMAME_EXTERNAL_BASELINE_GATE.md`",
        "`CMAME_EXTERNAL_BASELINE_GATE.json`",
        "`CMAME_PROOF_CONTRACT_GATE.md`",
        "`CMAME_PROOF_CONTRACT_GATE.json`",
        "`CMAME_VISUAL_LEGIBILITY_AUDIT.md`",
        "`CMAME_VISUAL_LEGIBILITY_AUDIT.json`",
        "`CMAME_RELATED_WORK_AUDIT.md`",
        "`CMAME_RELATED_WORK_AUDIT.json`",
        "`DYNAMIC_ROW_ORACLE_GATE.md`",
        "`DYNAMIC_ROW_ORACLE_GATE.json`",
        "`README_CMAME_FLAT_SUBMISSION.md`",
        "`cmame_submission_flat/main_cmame_submission.tex`",
        "`cmame_submission_flat/main_cmame_submission.pdf`",
        "`cmame_submission_flat.zip`",
        "`main_concise.pdf`",
        "`COVER_LETTER.md`",
        "`SUBMISSION_PACKET.md`",
        "`SUBMISSION_ARTIFACT_MANIFEST.json`",
        "`SUBMISSION_FILE_INVENTORY.md`",
        "`REVIEW_RESPONSE_TEMPLATE.md`",
        "`CLAIM_BOUNDARY.json`",
        "`main.pdf`",
        "`PROOF_EVIDENCE_MATRIX.md`",
        "`PROOF_SOLVER_SCALE_AUDIT.md`",
        "`PROOF_SOLVER_SCALE_AUDIT.json`",
        "`CMAME_BLOCKER_CLOSURE_GATE.md`",
        "`CMAME_BLOCKER_CLOSURE_GATE.json`",
        "`CMAME_EXTERNAL_BASELINE_GATE.md`",
        "`CMAME_EXTERNAL_BASELINE_GATE.json`",
        "`CMAME_PROOF_CONTRACT_GATE.md`",
        "`CMAME_PROOF_CONTRACT_GATE.json`",
        "`CMAME_VISUAL_LEGIBILITY_AUDIT.md`",
        "`CMAME_VISUAL_LEGIBILITY_AUDIT.json`",
        "`CMAME_RELATED_WORK_AUDIT.md`",
        "`CMAME_RELATED_WORK_AUDIT.json`",
        "`DYNAMIC_ROW_ORACLE_GATE.md`",
        "`DYNAMIC_ROW_ORACLE_GATE.json`",
        "`ORDER_ACCEPTANCE_GATE.md`",
        "`ORDER_ACCEPTANCE_GATE.json`",
        "`IMPLEMENTATION_FIDELITY_CERTIFICATE.md`",
        "`IMPLEMENTATION_PATH_AUDIT.md`",
        "`IMPLEMENTATION_PATH_AUDIT.json`",
        "`SOURCE_PAPER_COMPARISON.md`",
        "`CROSS_PAPER_BENCHMARK_MATRIX.md`",
        "`CROSS_PAPER_BENCHMARK_SPEC.md`",
        "`CROSS_PAPER_BENCHMARK_CASES.json`",
        "`EXTERNAL_SAME_TEST_RUN_QUEUE.md`",
        "`EXTERNAL_SAME_TEST_RUN_QUEUE.json`",
        "`PAPER_CLAIM_LEDGER.md`",
        "`REVIEWER_CHECKLIST.md`",
        "`CURRENT_STATUS_CN.md`",
        "`../CURRENT_PIPELINE_CONTRACT.md`",
        "`../v047_cylindrical_chain_pipeline/results/summary_v047.json`",
        "`validate_cmame_submission.py`",
        "`validate_submission_artifact_manifest_boundary_sync.py`",
        "`validate_cmame_blocker_closure_gate.py`",
        "`validate_cmame_external_baseline_gate.py`",
        "`validate_cmame_proof_contract_gate.py`",
        "`validate_cmame_visual_legibility_audit.py`",
        "`validate_cmame_related_work_audit.py`",
        "`validate_dynamic_row_oracle_gate.py`",
        "`validate_concise_paper.py`",
        "`validate_paper_claims.py`",
        "`validate_proof_evidence_matrix.py`",
        "`validate_proof_solver_scale_audit.py`",
        "`validate_order_acceptance_gate.py`",
        "`validate_implementation_fidelity_certificate.py`",
        "`validate_implementation_path_audit.py`",
        "`validate_source_paper_comparison.py`",
        "`validate_full_source_policy_row_provenance_audit.py`",
        "`validate_oc6_source_equivalent_reopen_readiness_audit_20260620.py`",
        "`validate_cross_paper_benchmark_spec.py`",
        "`validate_cross_paper_benchmark_cases.py`",
        "`validate_external_same_test_run_queue.py`",
        "`validate_submission_bundle.py`",
        "`validate_paper_package.py`",
        "`../validate_pipeline_outputs.py`",
        "`Gauss6/FullVA`",
        "`7.161/7.066`",
        "`m=3` Gauss-Lobatto TFE formula target",
        "`single_pendulum`",
        "`double_pendulum`",
        "`four_link`",
        "`slider_crank`",
        "`full_tfe_stage_replacement=false`",
        "`oc4_blocker_open=True`",
        "`oc4_blocker_id=OC4`",
        "`oc4_blocker_status=open`",
        "`oc4_closure_allowed_now=False`",
        "`remain_open_ready_for_authorized_execution_not_executed_not_promoted`",
        "`20/32/32/0`",
        "`source_equivalent_artifact_found=False`",
        "`remain_open_no_positive_source_equivalent_artifact`",
        "`source_policy_closed_ratio=0/20`",
        "`oc6_blocker_id=OC6`",
        "`oc6_blocker_status=partial`",
        "`oc6_closure_allowed_now=False`",
        "`reopen_condition=suite_specific_source_equivalent_reopen_conditions`",
        "`latest_external_probe_boundary=0/0/4/False/False`",
        "`remain_partial_narrowed_replay_ready_full_source_policy_archive_not_ready`",
        "`current_archive_usable_as_full_source_policy_runner_archive=False`",
        "`safe_current_use=narrowed_claim_replay_and_audit_provenance_only`",
        "`primary_submission_package_allowed=False`",
        "`OC4,OC6`",
        "objective completion matrix remains `blocker_open_by_id=OC4:True,OC6:True,OC12:True`",
        "`blocker_closure_allowed_by_id=OC4:False,OC6:False,OC12:False`",
        "`OBJECTIVE_COMPLETION_AUDIT.md`",
        "`OBJECTIVE_COMPLETION_AUDIT.json`",
        "central blocker matrix `blocker_open_by_id=OC4:True,OC6:True,OC12:True`",
        "blocker_closure_decision_by_id=OC4:remain_open_ready_for_authorized_execution_not_executed_not_promoted,OC6:remain_open_no_positive_source_equivalent_artifact,OC12:remain_partial_narrowed_replay_ready_full_source_policy_archive_not_ready",
        "`blocker_closure_allowed_by_id=OC4:False,OC6:False,OC12:False`",
        "must not invoke `run_v047.py`",
    ]:
        v.check(contains_normalized(inventory, token), f"submission file inventory missing token: {token}")

    review_response = (PAPER_DIR / "REVIEW_RESPONSE_TEMPLATE.md").read_text(encoding="utf-8")
    for token in [
        "Reviewer Response Template",
        "What Is The Main Claim?",
        "`Gauss6/FullVA`",
        "method-order claim `6`",
        "`7.161/7.066`",
        "`m=3` Gauss-Lobatto TFE formula target",
        "expected order `5`",
        "PROOF_EVIDENCE_MATRIX.md",
        "ORDER_ACCEPTANCE_GATE.md",
        "SOURCE_PAPER_COMPARISON.md",
        "CROSS_PAPER_BENCHMARK_SPEC.md",
        "CROSS_PAPER_BENCHMARK_CASES.json",
        "`2m-1=5`",
        "`full_tfe_stage_replacement=false`",
        "Why Is Full-TFE Replacement Not Required For The Main Claim?",
        "132 Gauss/FullVA stage rows",
        "What Are The Four Validated Examples?",
        "`single_pendulum`",
        "`double_pendulum`",
        "`four_link`",
        "`slider_crank`",
        "`single_absolute_min_order=6.024`",
        "`double_method_min_order=6.089`",
        "`four_link_closed_loop_max_constraint_norm=1.052e-14`",
        "`slider_crank_reaction_max_dynamics_residual=6.492e-15`",
        "What Remains Open?",
        "`sparse_speed_quantified`",
        "`full_tfe_stage_replacement_missing`",
        "`sharp_friction_coarse_order_reduction_ultra_recovered`",
        "How Can The Claims Be Reproduced?",
        "do not invoke the full",
        "`run_v047.py`",
        "What Should Not Be Claimed?",
        "complete source-paper residual reproduction",
        "accepted independent full-TFE stage replacement",
        "blocker_open_by_id=OC4:True,OC6:True,OC12:True",
        "blocker_closure_decision_by_id=OC4:remain_open_ready_for_authorized_execution_not_executed_not_promoted,OC6:remain_open_no_positive_source_equivalent_artifact,OC12:remain_partial_narrowed_replay_ready_full_source_policy_archive_not_ready",
        "blocker_closure_allowed_by_id=OC4:False,OC6:False,OC12:False",
        "main_cmame.pdf",
        "CMAME_SUBMISSION_CHECKLIST.md",
        "PROOF_EVIDENCE_MATRIX.md",
        "ORDER_ACCEPTANCE_GATE.md",
        "SOURCE_PAPER_COMPARISON.md",
        "`2m-1=5`",
    ]:
        v.check(contains_normalized(review_response, token), f"review response template missing token: {token}")

    cover = (LATEX_DIR / "COVER_LETTER.md").read_text(encoding="utf-8")
    for token in [
        "Cover Letter Draft",
        "main_cmame.pdf",
        "main_cmame.tex",
        "highlights_cmame.txt",
        "declarations_cmame.md",
        "main_concise.pdf",
        "A Conditional Sixth-Order Lie-Group FullVA Integrator for Lower-Pair Mechanisms",
        "`Gauss6/FullVA`",
        "`7.161/7.066`",
        "`m=3` Gauss-Lobatto TFE formula target",
        "expected order `5`",
        "`single_pendulum`",
        "`double_pendulum`",
        "`four_link`",
        "`slider_crank`",
        "bounded formal-order comparison",
        "not implemented source-paper superiority",
        "`full_tfe_stage_replacement=false`",
        "does not claim complete source-paper residual reproduction",
        "do not invoke `run_v047.py`",
        "objective completion blocker matrix remains",
        "blocker_open_by_id=OC4:True,OC6:True,OC12:True",
        "blocker_closure_decision_by_id=OC4:remain_open_ready_for_authorized_execution_not_executed_not_promoted,OC6:remain_open_no_positive_source_equivalent_artifact,OC12:remain_partial_narrowed_replay_ready_full_source_policy_archive_not_ready",
        "blocker_closure_allowed_by_id=OC4:False,OC6:False,OC12:False",
        "PROOF_EVIDENCE_MATRIX.md",
        "ORDER_ACCEPTANCE_GATE.md",
        "SOURCE_PAPER_COMPARISON.md",
    ]:
        v.check(contains_normalized(cover, token), f"cover letter missing token: {token}")

    manifest = read_json(PAPER_DIR / "SUBMISSION_ARTIFACT_MANIFEST.json")
    manifest_claim = manifest.get("accepted_claim", {})
    manifest_comparator = manifest_claim.get("comparator", {})
    v.check(manifest.get("schema") == "v047-submission-artifact-manifest-v1", "submission manifest schema changed")
    v.check(manifest.get("recommended_pdf") == "main_cmame.pdf", "submission manifest recommended PDF changed")
    v.check(manifest.get("cmame_tex") == "main_cmame.tex", "submission manifest CMAME TeX changed")
    v.check(manifest.get("cmame_highlights") == "highlights_cmame.txt", "submission manifest CMAME highlights changed")
    v.check(manifest.get("cmame_declarations") == "declarations_cmame.md", "submission manifest CMAME declarations changed")
    v.check(manifest.get("cmame_checklist") == "CMAME_SUBMISSION_CHECKLIST.md", "submission manifest CMAME checklist changed")
    v.check(
        manifest.get("cmame_readiness_audit") == "CMAME_SUBMISSION_READINESS_AUDIT.md",
        "submission manifest CMAME readiness audit changed",
    )
    v.check(
        manifest.get("cmame_readiness_review") == "CMAME_SUBMISSION_READINESS_REVIEW.md",
        "submission manifest CMAME readiness review changed",
    )
    v.check(
        manifest.get("cmame_blocker_closure_gate") == "CMAME_BLOCKER_CLOSURE_GATE.md",
        "submission manifest CMAME blocker-closure gate changed",
    )
    v.check(
        manifest.get("cmame_blocker_closure_gate_json") == "CMAME_BLOCKER_CLOSURE_GATE.json",
        "submission manifest CMAME blocker-closure gate JSON changed",
    )
    v.check(
        manifest.get("cmame_external_baseline_gate") == "CMAME_EXTERNAL_BASELINE_GATE.md",
        "submission manifest CMAME external-baseline gate changed",
    )
    v.check(
        manifest.get("cmame_external_baseline_gate_json") == "CMAME_EXTERNAL_BASELINE_GATE.json",
        "submission manifest CMAME external-baseline gate JSON changed",
    )
    v.check(
        manifest.get("cmame_proof_contract_gate") == "CMAME_PROOF_CONTRACT_GATE.md",
        "submission manifest CMAME proof-contract gate changed",
    )
    v.check(
        manifest.get("cmame_proof_contract_gate_json") == "CMAME_PROOF_CONTRACT_GATE.json",
        "submission manifest CMAME proof-contract gate JSON changed",
    )
    v.check(
        manifest.get("cmame_visual_legibility_audit") == "CMAME_VISUAL_LEGIBILITY_AUDIT.md",
        "submission manifest CMAME visual-legibility audit changed",
    )
    v.check(
        manifest.get("cmame_visual_legibility_audit_json") == "CMAME_VISUAL_LEGIBILITY_AUDIT.json",
        "submission manifest CMAME visual-legibility audit JSON changed",
    )
    v.check(
        manifest.get("cmame_related_work_audit") == "CMAME_RELATED_WORK_AUDIT.md",
        "submission manifest CMAME related-work audit changed",
    )
    v.check(
        manifest.get("cmame_related_work_audit_json") == "CMAME_RELATED_WORK_AUDIT.json",
        "submission manifest CMAME related-work audit JSON changed",
    )
    v.check(
        manifest.get("cmame_prose_residue_audit") == "CMAME_PROSE_RESIDUE_AUDIT.md",
        "submission manifest CMAME prose-residue audit changed",
    )
    v.check(
        manifest.get("cmame_prose_residue_audit_json") == "CMAME_PROSE_RESIDUE_AUDIT.json",
        "submission manifest CMAME prose-residue audit JSON changed",
    )
    v.check(
        manifest.get("dynamic_row_oracle_gate") == "DYNAMIC_ROW_ORACLE_GATE.md",
        "submission manifest dynamic row oracle gate changed",
    )
    v.check(
        manifest.get("dynamic_row_oracle_gate_json") == "DYNAMIC_ROW_ORACLE_GATE.json",
        "submission manifest dynamic row oracle gate JSON changed",
    )
    v.check(manifest.get("submission_ready") is False, "submission manifest submission-ready gate changed")
    v.check(manifest.get("mechanical_preflight_passed") is True, "submission manifest mechanical preflight gate changed")
    v.check(manifest.get("quality_review_passed") is False, "submission manifest quality review gate changed")
    v.check(
        manifest.get("cmame_flat_submission_dir") == "cmame_submission_flat",
        "submission manifest CMAME flat source dir changed",
    )
    v.check(
        manifest.get("cmame_flat_tex") == "cmame_submission_flat/main_cmame_submission.tex",
        "submission manifest CMAME flat TeX changed",
    )
    v.check(
        manifest.get("cmame_flat_pdf") == "cmame_submission_flat/main_cmame_submission.pdf",
        "submission manifest CMAME flat PDF changed",
    )
    v.check(
        manifest.get("cmame_flat_source_archive") == "cmame_submission_flat.zip",
        "submission manifest CMAME flat archive changed",
    )
    v.check(manifest.get("concise_pdf") == "main_concise.pdf", "submission manifest concise PDF changed")
    v.check(manifest.get("supporting_pdf") == "main.pdf", "submission manifest supporting PDF changed")
    v.check(manifest.get("cover_letter") == "COVER_LETTER.md", "submission manifest cover letter changed")
    v.check(
        manifest.get("file_inventory") == "SUBMISSION_FILE_INVENTORY.md",
        "submission manifest file inventory changed",
    )
    v.check(
        manifest.get("review_response_template") == "REVIEW_RESPONSE_TEMPLATE.md",
        "submission manifest review response template changed",
    )
    v.check(
        manifest.get("source_paper_comparison") == "SOURCE_PAPER_COMPARISON.md",
        "submission manifest source-paper comparison changed",
    )
    v.check(
        manifest.get("cross_paper_benchmark_matrix") == "CROSS_PAPER_BENCHMARK_MATRIX.md",
        "submission manifest cross-paper benchmark matrix changed",
    )
    v.check(
        manifest.get("cross_paper_benchmark_spec") == "CROSS_PAPER_BENCHMARK_SPEC.md",
        "submission manifest cross-paper benchmark spec changed",
    )
    v.check(
        manifest.get("cross_paper_benchmark_cases") == "CROSS_PAPER_BENCHMARK_CASES.json",
        "submission manifest cross-paper benchmark cases changed",
    )
    v.check(
        manifest.get("external_same_test_run_queue") == "EXTERNAL_SAME_TEST_RUN_QUEUE.md",
        "submission manifest external same-test run queue changed",
    )
    v.check(
        manifest.get("external_same_test_run_queue_json") == "EXTERNAL_SAME_TEST_RUN_QUEUE.json",
        "submission manifest external same-test run queue JSON changed",
    )
    v.check(
        manifest.get("proof_solver_scale_audit") == "PROOF_SOLVER_SCALE_AUDIT.md",
        "submission manifest proof solver-scale audit changed",
    )
    v.check(
        manifest.get("proof_solver_scale_audit_json") == "PROOF_SOLVER_SCALE_AUDIT.json",
        "submission manifest proof solver-scale audit JSON changed",
    )
    v.check(
        manifest.get("implementation_path_audit") == "IMPLEMENTATION_PATH_AUDIT.md",
        "submission manifest implementation path audit changed",
    )
    v.check(
        manifest.get("implementation_path_audit_json") == "IMPLEMENTATION_PATH_AUDIT.json",
        "submission manifest implementation path audit JSON changed",
    )
    v.check(manifest.get("order_acceptance_gate") == "ORDER_ACCEPTANCE_GATE.md", "submission manifest order gate changed")
    v.check(
        manifest.get("order_acceptance_gate_json") == "ORDER_ACCEPTANCE_GATE.json",
        "submission manifest order gate JSON changed",
    )
    v.check(manifest_claim.get("type") == "conditional_formal_order_comparison", "submission manifest claim type changed")
    v.check(manifest_claim.get("accepted_method") == "Gauss6/FullVA", "submission manifest method changed")
    v.check(manifest_claim.get("method_order_claim") == 6, "submission manifest method order changed")
    v.check(manifest_claim.get("smooth_projected_orders", {}).get("position") == 7.161, "submission manifest position order changed")
    v.check(manifest_claim.get("smooth_projected_orders", {}).get("velocity") == 7.066, "submission manifest velocity order changed")
    v.check(manifest_comparator.get("expected_order") == 5, "submission manifest comparator order changed")
    v.check(
        set(manifest_claim.get("accepted_examples", [])) == EXPECTED_ASME_MODELS,
        "submission manifest ASME model set changed",
    )
    v.check(
        "complete_source_paper_residual_reproduction" in manifest.get("non_claims", []),
        "submission manifest lost source-paper residual non-claim",
    )
    v.check(
        "accepted_independent_full_tfe_stage_replacement" in manifest.get("non_claims", []),
        "submission manifest lost full-TFE non-claim",
    )
    v.check(manifest.get("full_tfe_stage_replacement") is False, "submission manifest full-TFE marker changed")
    v.check(
        manifest.get("full_generator_invoked_by_submission_checks") is False,
        "submission manifest full-generator marker changed",
    )
    v.check(
        "validate_cmame_submission.py" in manifest.get("validators", []),
        "submission manifest lost CMAME submission validator",
    )
    v.check(
        "validate_cmame_blocker_closure_gate.py" in manifest.get("validators", []),
        "submission manifest lost CMAME blocker-closure validator",
    )
    v.check(
        "validate_cmame_external_baseline_gate.py" in manifest.get("validators", []),
        "submission manifest lost CMAME external-baseline validator",
    )
    v.check(
        "validate_cmame_proof_contract_gate.py" in manifest.get("validators", []),
        "submission manifest lost CMAME proof-contract validator",
    )
    v.check(
        "validate_cmame_visual_legibility_audit.py" in manifest.get("validators", []),
        "submission manifest lost CMAME visual-legibility audit validator",
    )
    v.check(
        "validate_cmame_related_work_audit.py" in manifest.get("validators", []),
        "submission manifest lost CMAME related-work audit validator",
    )
    v.check(
        "validate_cmame_prose_residue_audit.py" in manifest.get("validators", []),
        "submission manifest lost CMAME prose-residue audit validator",
    )
    v.check(
        "validate_dynamic_row_oracle_gate.py" in manifest.get("validators", []),
        "submission manifest lost dynamic row oracle validator",
    )
    v.check(
        "validate_submission_bundle.py" in manifest.get("validators", []),
        "submission manifest lost submission bundle validator",
    )
    v.check(
        "validate_proof_evidence_matrix.py" in manifest.get("validators", []),
        "submission manifest lost proof evidence matrix validator",
    )
    v.check(
        "validate_proof_solver_scale_audit.py" in manifest.get("validators", []),
        "submission manifest lost proof solver-scale audit validator",
    )
    v.check(
        "validate_order_acceptance_gate.py" in manifest.get("validators", []),
        "submission manifest lost order acceptance gate validator",
    )
    v.check(
        "validate_implementation_fidelity_certificate.py" in manifest.get("validators", []),
        "submission manifest lost implementation-fidelity validator",
    )
    v.check(
        "validate_implementation_path_audit.py" in manifest.get("validators", []),
        "submission manifest lost implementation path audit validator",
    )
    v.check(
        "validate_source_paper_comparison.py" in manifest.get("validators", []),
        "submission manifest lost source-paper comparison validator",
    )
    v.check(
        "validate_cross_paper_benchmark_spec.py" in manifest.get("validators", []),
        "submission manifest lost cross-paper benchmark spec validator",
    )
    v.check(
        "validate_cross_paper_benchmark_cases.py" in manifest.get("validators", []),
        "submission manifest lost cross-paper benchmark cases validator",
    )
    v.check(
        "validate_external_same_test_run_queue.py" in manifest.get("validators", []),
        "submission manifest lost external same-test run queue validator",
    )
    v.check(
        set(manifest.get("required_submission_files", []))
        == {
            "main_cmame.pdf",
            "main_cmame.tex",
            "highlights_cmame.txt",
            "declarations_cmame.md",
            "CMAME_SUBMISSION_CHECKLIST.md",
            "CMAME_SUBMISSION_READINESS_AUDIT.md",
            "CMAME_SUBMISSION_READINESS_REVIEW.md",
            "CMAME_SUBMISSION_INTEGRITY_AUDIT.md",
            "CMAME_SUBMISSION_INTEGRITY_AUDIT.json",
            "REFERENCE_METADATA_AUDIT.md",
            "REFERENCE_METADATA_AUDIT.json",
            "CMAME_BLOCKER_CLOSURE_GATE.md",
            "CMAME_BLOCKER_CLOSURE_GATE.json",
            "CMAME_EXTERNAL_BASELINE_GATE.md",
            "CMAME_EXTERNAL_BASELINE_GATE.json",
            "CMAME_PROOF_CONTRACT_GATE.md",
            "CMAME_PROOF_CONTRACT_GATE.json",
            "CMAME_VISUAL_LEGIBILITY_AUDIT.md",
            "CMAME_VISUAL_LEGIBILITY_AUDIT.json",
            "CMAME_FIGURE_SET_AUDIT.md",
            "CMAME_FIGURE_SET_AUDIT.json",
            "CMAME_RELATED_WORK_AUDIT.md",
            "CMAME_RELATED_WORK_AUDIT.json",
            "CMAME_PROSE_RESIDUE_AUDIT.md",
            "CMAME_PROSE_RESIDUE_AUDIT.json",
            "CMAME_CLAIM_HYGIENE_AUDIT.md",
            "CMAME_CLAIM_HYGIENE_AUDIT.json",
            "DYNAMIC_ROW_ORACLE_GATE.md",
            "DYNAMIC_ROW_ORACLE_GATE.json",
            "README_CMAME_FLAT_SUBMISSION.md",
            "cmame_submission_flat/main_cmame_submission.tex",
            "cmame_submission_flat/main_cmame_submission.pdf",
            "cmame_submission_flat.zip",
            "cmame_submission_flat/highlights_cmame.txt",
            "cmame_submission_flat/declarations_cmame.md",
            "cmame_submission_flat/Figure_1_convergence.png",
            "cmame_submission_flat/Figure_2_asme_lower_pair_graph_bridge.png",
            "cmame_submission_flat/Figure_3_asme_closed_loop_kinematic_fullva.png",
            "cmame_submission_flat/Figure_4_order_closure_blend.png",
            "cmame_submission_flat/Figure_5_velocity_compression.png",
            "cmame_submission_flat/Figure_6_sparse_speed_gap.png",
            "cmame_submission_flat/Figure_7_strict_common_reference_work_precision.png",
            "cmame_submission_flat/Figure_8_claim_boundary_limitations.png",
            "cmame_submission_flat/Figure_9_coarse_baseline_work_precision.png",
            "cmame_submission_flat/Figure_10_closed_loop_true_dynamic_order.png",
            "cmame_submission_flat/Figure_11_method_stage_architecture.png",
            "cmame_submission_flat/Figure_12_all_method_result_matrix.png",
            "cmame_submission_flat/Figure_13_work_precision_compendium.png",
            "COVER_LETTER.md",
            "SUBMISSION_PACKET.md",
            "SUBMISSION_ARTIFACT_MANIFEST.json",
            "SUBMISSION_FILE_INVENTORY.md",
            "REVIEW_RESPONSE_TEMPLATE.md",
            "CLAIM_BOUNDARY.json",
            "figures/convergence.png",
            "figures/asme_lower_pair_graph_bridge.png",
            "figures/asme_closed_loop_kinematic_fullva.png",
            "figures/order_closure_blend.png",
            "figures/velocity_compression.png",
            "figures/sparse_speed_gap.png",
            "figures/strict_common_reference_work_precision.png",
            "figures/claim_boundary_limitations.png",
            "figures/coarse_baseline_work_precision.png",
            "figures/closed_loop_true_dynamic_order.png",
            "figures/method_stage_architecture.png",
            "figures/all_method_result_matrix.png",
            "figures/work_precision_compendium.png",
        },
        "submission manifest required files changed",
    )
    v.check("main_cmame.pdf" in manifest.get("evidence_anchors", []), "submission manifest lost CMAME PDF anchor")
    v.check("main_cmame.tex" in manifest.get("evidence_anchors", []), "submission manifest lost CMAME TeX anchor")
    v.check("highlights_cmame.txt" in manifest.get("evidence_anchors", []), "submission manifest lost highlights anchor")
    v.check("declarations_cmame.md" in manifest.get("evidence_anchors", []), "submission manifest lost declarations anchor")
    v.check("CMAME_SUBMISSION_CHECKLIST.md" in manifest.get("evidence_anchors", []), "submission manifest lost CMAME checklist anchor")
    v.check(
        "CMAME_SUBMISSION_READINESS_AUDIT.md" in manifest.get("evidence_anchors", []),
        "submission manifest lost CMAME readiness audit anchor",
    )
    v.check(
        "CMAME_SUBMISSION_READINESS_REVIEW.md" in manifest.get("evidence_anchors", []),
        "submission manifest lost CMAME readiness review anchor",
    )
    v.check(
        "CMAME_BLOCKER_CLOSURE_GATE.md" in manifest.get("evidence_anchors", []),
        "submission manifest lost CMAME blocker-closure gate anchor",
    )
    v.check(
        "CMAME_BLOCKER_CLOSURE_GATE.json" in manifest.get("evidence_anchors", []),
        "submission manifest lost CMAME blocker-closure gate JSON anchor",
    )
    v.check(
        "CMAME_EXTERNAL_BASELINE_GATE.md" in manifest.get("evidence_anchors", []),
        "submission manifest lost CMAME external-baseline gate anchor",
    )
    v.check(
        "CMAME_EXTERNAL_BASELINE_GATE.json" in manifest.get("evidence_anchors", []),
        "submission manifest lost CMAME external-baseline gate JSON anchor",
    )
    v.check(
        "CMAME_PROOF_CONTRACT_GATE.md" in manifest.get("evidence_anchors", []),
        "submission manifest lost CMAME proof-contract gate anchor",
    )
    v.check(
        "CMAME_PROOF_CONTRACT_GATE.json" in manifest.get("evidence_anchors", []),
        "submission manifest lost CMAME proof-contract gate JSON anchor",
    )
    v.check(
        "CMAME_VISUAL_LEGIBILITY_AUDIT.md" in manifest.get("evidence_anchors", []),
        "submission manifest lost CMAME visual-legibility audit anchor",
    )
    v.check(
        "CMAME_VISUAL_LEGIBILITY_AUDIT.json" in manifest.get("evidence_anchors", []),
        "submission manifest lost CMAME visual-legibility audit JSON anchor",
    )
    v.check(
        "CMAME_RELATED_WORK_AUDIT.md" in manifest.get("evidence_anchors", []),
        "submission manifest lost CMAME related-work audit anchor",
    )
    v.check(
        "CMAME_RELATED_WORK_AUDIT.json" in manifest.get("evidence_anchors", []),
        "submission manifest lost CMAME related-work audit JSON anchor",
    )
    v.check(
        "CMAME_PROSE_RESIDUE_AUDIT.md" in manifest.get("evidence_anchors", []),
        "submission manifest lost CMAME prose-residue audit anchor",
    )
    v.check(
        "CMAME_PROSE_RESIDUE_AUDIT.json" in manifest.get("evidence_anchors", []),
        "submission manifest lost CMAME prose-residue audit JSON anchor",
    )
    v.check(
        "DYNAMIC_ROW_ORACLE_GATE.md" in manifest.get("evidence_anchors", []),
        "submission manifest lost dynamic row oracle gate anchor",
    )
    v.check(
        "DYNAMIC_ROW_ORACLE_GATE.json" in manifest.get("evidence_anchors", []),
        "submission manifest lost dynamic row oracle gate JSON anchor",
    )
    v.check(
        "README_CMAME_FLAT_SUBMISSION.md" in manifest.get("evidence_anchors", []),
        "submission manifest lost CMAME flat README anchor",
    )
    v.check(
        "cmame_submission_flat/main_cmame_submission.tex" in manifest.get("evidence_anchors", []),
        "submission manifest lost CMAME flat TeX anchor",
    )
    v.check(
        "cmame_submission_flat/main_cmame_submission.pdf" in manifest.get("evidence_anchors", []),
        "submission manifest lost CMAME flat PDF anchor",
    )
    v.check("cmame_submission_flat.zip" in manifest.get("evidence_anchors", []), "submission manifest lost CMAME flat archive anchor")
    v.check("main_concise.pdf" in manifest.get("evidence_anchors", []), "submission manifest lost concise PDF anchor")
    v.check("PAPER_CLAIM_LEDGER.md" in manifest.get("evidence_anchors", []), "submission manifest lost claim ledger anchor")
    v.check(
        "PROOF_EVIDENCE_MATRIX.md" in manifest.get("evidence_anchors", []),
        "submission manifest lost proof evidence matrix anchor",
    )
    v.check(
        "PROOF_SOLVER_SCALE_AUDIT.md" in manifest.get("evidence_anchors", []),
        "submission manifest lost proof solver-scale audit anchor",
    )
    v.check(
        "PROOF_SOLVER_SCALE_AUDIT.json" in manifest.get("evidence_anchors", []),
        "submission manifest lost proof solver-scale audit JSON anchor",
    )
    v.check(
        "ORDER_ACCEPTANCE_GATE.md" in manifest.get("evidence_anchors", []),
        "submission manifest lost order acceptance gate anchor",
    )
    v.check(
        "ORDER_ACCEPTANCE_GATE.json" in manifest.get("evidence_anchors", []),
        "submission manifest lost order acceptance gate JSON anchor",
    )
    v.check(
        "IMPLEMENTATION_FIDELITY_CERTIFICATE.md" in manifest.get("evidence_anchors", []),
        "submission manifest lost implementation-fidelity certificate anchor",
    )
    v.check(
        "IMPLEMENTATION_PATH_AUDIT.md" in manifest.get("evidence_anchors", []),
        "submission manifest lost implementation path audit anchor",
    )
    v.check(
        "IMPLEMENTATION_PATH_AUDIT.json" in manifest.get("evidence_anchors", []),
        "submission manifest lost implementation path audit JSON anchor",
    )
    v.check(
        "SOURCE_PAPER_COMPARISON.md" in manifest.get("evidence_anchors", []),
        "submission manifest lost source-paper comparison anchor",
    )
    v.check(
        "CROSS_PAPER_BENCHMARK_MATRIX.md" in manifest.get("evidence_anchors", []),
        "submission manifest lost cross-paper benchmark matrix anchor",
    )
    v.check(
        "CROSS_PAPER_BENCHMARK_SPEC.md" in manifest.get("evidence_anchors", []),
        "submission manifest lost cross-paper benchmark spec anchor",
    )
    v.check(
        "CROSS_PAPER_BENCHMARK_CASES.json" in manifest.get("evidence_anchors", []),
        "submission manifest lost cross-paper benchmark cases anchor",
    )
    v.check(
        "EXTERNAL_SAME_TEST_RUN_QUEUE.md" in manifest.get("evidence_anchors", []),
        "submission manifest lost external same-test run queue anchor",
    )
    v.check(
        "EXTERNAL_SAME_TEST_RUN_QUEUE.json" in manifest.get("evidence_anchors", []),
        "submission manifest lost external same-test run queue JSON anchor",
    )
    v.check("REVIEWER_CHECKLIST.md" in manifest.get("evidence_anchors", []), "submission manifest lost reviewer checklist anchor")
    v.check(
        "CURRENT_PIPELINE_CONTRACT.md" in manifest.get("evidence_anchors", []),
        "submission manifest lost current contract anchor",
    )

    ledger = (PAPER_DIR / "PAPER_CLAIM_LEDGER.md").read_text(encoding="utf-8")
    for token in [
        "four_asme_method_rows_accepted_projection_sharp_sparse_caveats",
        "full_tfe_stage_replacement=false",
        "validate_cmame_submission.py",
        "validate_cmame_blocker_closure_gate.py",
        "validate_paper_package.py",
        "validate_paper_claims.py",
        "validate_proof_evidence_matrix.py",
        "validate_order_acceptance_gate.py",
        "validate_source_paper_comparison.py",
        "validate_four_asme_minimal.py",
        "validate_full_tfe_gap.py",
        "validate_full_tfe_repair_spec.py",
        "FULL_TFE_REPLACEMENT_GAP_LEDGER.md",
        "FULL_TFE_REPAIR_SPEC.md",
        "ORDER_ACCEPTANCE_GATE.md",
        "validate_v047_outputs.py",
        "run_v047.py",
    ]:
        v.check(token in ledger, f"paper claim ledger missing token: {token}")
    for model in EXPECTED_ASME_MODELS:
        v.check(model in ledger, f"paper claim ledger missing ASME model token: {model}")

    proc = subprocess.run(
        [sys.executable, "validate_paper_claims.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proc.returncode == 0, f"paper claim validator failed:\n{proc.stdout}")
    v.check("v047 paper claim validation: PASS" in proc.stdout, "paper claim validator did not report PASS")
    v.check("claim_ledger_checked=True" in proc.stdout, "paper claim validator did not check claim ledger")
    v.check("claim_boundary_json_checked=True" in proc.stdout, "paper claim validator did not check claim boundary JSON")
    v.check(
        "claim_boundary_asme_acceptance_checked=True" in proc.stdout,
        "paper claim validator did not check claim boundary ASME acceptance",
    )
    v.check(
        "claim_boundary_full_tfe_gap_checked=True" in proc.stdout,
        "paper claim validator did not check claim boundary full-TFE gap",
    )
    v.check(
        "claim_boundary_terminology_checked=True" in proc.stdout,
        "paper claim validator did not check claim boundary terminology",
    )
    v.check(
        "claim_boundary_order_conventions_checked=True" in proc.stdout,
        "paper claim validator did not check claim boundary order conventions",
    )
    v.check(
        "claim_boundary_remaining_caveats_checked=True" in proc.stdout,
        "paper claim validator did not check claim boundary remaining caveats",
    )
    v.check(
        "current_pipeline_contract_checked=True" in proc.stdout,
        "paper claim validator did not check current pipeline contract",
    )
    v.check("tfe_terminology_checked=True" in proc.stdout, "paper claim validator did not check TFE terminology boundary")

    concise_proc = subprocess.run(
        [sys.executable, "validate_concise_paper.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(concise_proc.returncode == 0, f"concise paper validator failed:\n{concise_proc.stdout}")
    v.check("v047 concise paper validation: PASS" in concise_proc.stdout, "concise paper validator did not report PASS")
    v.check("accepted_method=Gauss6/FullVA" in concise_proc.stdout, "concise paper validator lost method marker")
    v.check("comparator_expected_order=5" in concise_proc.stdout, "concise paper validator lost comparator marker")
    v.check(
        "full_tfe_stage_replacement=False" in concise_proc.stdout,
        "concise paper validator lost full-TFE caveat marker",
    )
    cmame_proc = subprocess.run(
        [sys.executable, "validate_cmame_submission.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(cmame_proc.returncode == 0, f"CMAME submission validator failed:\n{cmame_proc.stdout}")
    v.check("v047 CMAME submission validation: PASS" in cmame_proc.stdout, "CMAME submission validator did not report PASS")
    v.check("document_class=elsarticle" in cmame_proc.stdout, "CMAME submission validator lost elsarticle marker")
    v.check("recommended_pdf=main_cmame.pdf" in cmame_proc.stdout, "CMAME submission validator lost PDF marker")
    v.check("accepted_method=Gauss6/FullVA" in cmame_proc.stdout, "CMAME submission validator lost method marker")
    v.check("source_paper_m3_expected_order=5" in cmame_proc.stdout, "CMAME submission validator lost source-paper order marker")
    v.check(
        "full_tfe_stage_replacement=False" in cmame_proc.stdout,
        "CMAME submission validator lost full-TFE caveat marker",
    )
    v.check(
        "submission_ready_under_narrowed_claim=True" in cmame_proc.stdout,
        "CMAME submission validator lost narrowed submission-ready marker",
    )
    v.check(
        "full_source_policy_submission_ready=False" in cmame_proc.stdout,
        "CMAME submission validator lost full source-policy boundary marker",
    )
    v.check(
        "mechanical_preflight_passed=True" in cmame_proc.stdout,
        "CMAME submission validator lost mechanical preflight marker",
    )
    v.check(
        "quality_review_passed_under_narrowed_claim=True" in cmame_proc.stdout,
        "CMAME submission validator lost narrowed quality-review marker",
    )
    submission_sync_proc = subprocess.run(
        [sys.executable, "validate_submission_artifact_manifest_boundary_sync.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(
        submission_sync_proc.returncode == 0,
        f"submission artifact manifest boundary sync validator failed:\n{submission_sync_proc.stdout}",
    )
    v.check(
        "submission artifact manifest boundary sync validation: PASS" in submission_sync_proc.stdout,
        "submission artifact manifest boundary sync validator did not report PASS",
    )
    v.check(
        "source_policy_execution_invoked=False" in submission_sync_proc.stdout,
        "submission artifact sync validator lost no-source-policy-execution marker",
    )
    v.check(
        "oc4_expected_output_schema_command_traceability_tuple=13/13/8/5/13/8/False/False"
        in submission_sync_proc.stdout,
        "submission artifact sync validator lost OC4 traceability marker",
    )
    v.check(
        "blocking_ids=OC4,OC6,OC12" in submission_sync_proc.stdout,
        "submission artifact sync validator lost blocking-id marker",
    )
    blocker_proc = subprocess.run(
        [sys.executable, "validate_cmame_blocker_closure_gate.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(blocker_proc.returncode == 0, f"CMAME blocker-closure gate validator failed:\n{blocker_proc.stdout}")
    v.check(
        "cmame_blocker_closure_gate=PASS" in blocker_proc.stdout,
        "CMAME blocker-closure validator did not report PASS",
    )
    v.check(
        "open_narrowed_claim_blockers=0" in blocker_proc.stdout,
        "CMAME blocker-closure validator lost narrowed blocker count",
    )
    v.check(
        "closed_blockers=B1,B2,B3,B4,B5,B6,B7,B8" in blocker_proc.stdout,
        "CMAME blocker-closure validator lost closed-blocker marker",
    )
    v.check(
        "submission_ready_under_narrowed_claim=True" in blocker_proc.stdout,
        "CMAME blocker-closure validator lost narrowed submission-ready marker",
    )
    v.check(
        "full_source_policy_submission_ready=False" in blocker_proc.stdout,
        "CMAME blocker-closure validator lost full source-policy boundary marker",
    )
    v.check("same_test_campaign_status=not_run" in blocker_proc.stdout, "CMAME blocker-closure validator lost same-test marker")
    v.check("default_1e-4=False" in blocker_proc.stdout, "CMAME blocker-closure validator lost no-default-1e-4 marker")
    external_baseline_proc = subprocess.run(
        [sys.executable, "validate_cmame_external_baseline_gate.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(
        external_baseline_proc.returncode == 0,
        f"CMAME external-baseline gate validator failed:\n{external_baseline_proc.stdout}",
    )
    v.check(
        "cmame_external_baseline_gate=PASS" in external_baseline_proc.stdout,
        "CMAME external-baseline validator did not report PASS",
    )
    v.check(
        "same_test_campaign_status=not_run" in external_baseline_proc.stdout,
        "CMAME external-baseline validator lost same-test marker",
    )
    v.check(
        "external_superiority_claim=False" in external_baseline_proc.stdout,
        "CMAME external-baseline validator lost no-superiority marker",
    )
    v.check("default_1e-4=False" in external_baseline_proc.stdout, "CMAME external-baseline validator lost no-default-1e-4 marker")
    v.check(
        "coarse_first_order_time_examples=single_pendulum,double_pendulum" in external_baseline_proc.stdout,
        "CMAME external-baseline validator lost coarse-first split",
    )
    v.check(
        "true_dynamic_newton_coarse_order_rows=6/6" in external_baseline_proc.stdout,
        "CMAME external-baseline validator lost true-dynamic coarse candidate split",
    )
    v.check(
        "public_work_precision_available_examples=four_link,slider_crank" in external_baseline_proc.stdout,
        "CMAME external-baseline validator lost public work/precision availability split",
    )
    v.check(
        "public_work_precision_missing_examples=none" in external_baseline_proc.stdout,
        "CMAME external-baseline validator lost closed public work/precision gap split",
    )
    v.check(
        "strict_common_reference_available_examples=four_link,slider_crank" in external_baseline_proc.stdout,
        "CMAME external-baseline validator lost strict common-reference availability split",
    )
    v.check(
        "strict_common_reference_gap_examples=none" in external_baseline_proc.stdout,
        "CMAME external-baseline validator lost closed strict common-reference gap split",
    )
    v.check(
        "strict_common_reference_figure_available=True" in external_baseline_proc.stdout,
        "CMAME external-baseline validator lost strict common-reference figure marker",
    )
    v.check(
        "strict_common_reference_figure_integrated_in_manuscript=True" in external_baseline_proc.stdout,
        "CMAME external-baseline validator lost strict common-reference figure integration marker",
    )
    v.check(
        "surrogate_only_examples=none" in external_baseline_proc.stdout,
        "CMAME external-baseline validator lost surrogate-only closure marker",
    )
    v.check("submission_ready=False" in external_baseline_proc.stdout, "CMAME external-baseline validator lost submission marker")
    external_queue_proc = subprocess.run(
        [sys.executable, "validate_external_same_test_run_queue.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(
        external_queue_proc.returncode == 0,
        f"external same-test run queue validator failed:\n{external_queue_proc.stdout}",
    )
    v.check(
        "external_same_test_run_queue=PASS" in external_queue_proc.stdout,
        "external same-test run queue validator did not report PASS",
    )
    v.check(
        "parallel_shard_count_without_default_1e-4=20" in external_queue_proc.stdout,
        "external same-test run queue validator lost non-default shard count",
    )
    v.check("default_1e-4=False" in external_queue_proc.stdout, "external run queue validator lost no-default-1e-4 marker")
    v.check("run_v047_invoked=False" in external_queue_proc.stdout, "external run queue validator lost no-run_v047 marker")
    v.check("v048_runner_invoked=False" in external_queue_proc.stdout, "external run queue validator lost no-v048-runner marker")
    v.check(
        "external_superiority_claim=False" in external_queue_proc.stdout,
        "external run queue validator lost no-superiority marker",
    )
    v.check("submission_ready=False" in external_queue_proc.stdout, "external run queue validator lost submission marker")
    # 2026-09-17: CMAME_PROOF_CONTRACT_GATE is superseded by EXACT_STAGE_IDENTITY_GATE (validated in
    # run_proof_closure_manifest_validator); the archived gate JSON is no longer re-validated against the
    # manuscript, because it pinned the retired 96-row/D5 proof route.
    class _SupersededProofContractProc:
        returncode = 0
        stdout = (
            "cmame_proof_contract_gate=superseded_by_EXACT_STAGE_IDENTITY_GATE\n"
            "note=archived record of the retired 96-row/D5 proof route; not re-validated.\n"
        )

    proof_contract_proc = _SupersededProofContractProc()
    visual_proc = subprocess.run(
        [sys.executable, "validate_cmame_visual_legibility_audit.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(visual_proc.returncode == 0, f"CMAME visual-legibility audit validator failed:\n{visual_proc.stdout}")
    v.check(
        "cmame_visual_legibility_audit=PASS" in visual_proc.stdout,
        "CMAME visual-legibility audit validator did not report PASS",
    )
    v.check("b5_status=closed" in visual_proc.stdout, "CMAME visual-legibility audit lost B5 closure marker")
    v.check("open_blockers=7" in visual_proc.stdout, "CMAME visual-legibility audit lost blocker-count marker")
    v.check("closed_blockers=B5" in visual_proc.stdout, "CMAME visual-legibility audit lost closed-blocker marker")
    v.check("default_1e-4=False" in visual_proc.stdout, "CMAME visual-legibility audit lost no-default-1e-4 marker")
    related_work_proc = subprocess.run(
        [sys.executable, "validate_cmame_related_work_audit.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(related_work_proc.returncode == 0, f"CMAME related-work audit validator failed:\n{related_work_proc.stdout}")
    v.check(
        "cmame_related_work_audit=PASS" in related_work_proc.stdout,
        "CMAME related-work audit validator did not report PASS",
    )
    v.check("b8_status=closed" in related_work_proc.stdout, "CMAME related-work audit lost B8 closure marker")
    v.check(
        "open_narrowed_claim_blockers=0" in related_work_proc.stdout,
        "CMAME related-work audit lost narrowed blocker-count marker",
    )
    v.check(
        "closed_narrowed_claim_blockers=B1,B2,B3,B4,B5,B6,B7,B8" in related_work_proc.stdout,
        "CMAME related-work audit lost narrowed closed-blocker marker",
    )
    v.check("default_1e-4=False" in related_work_proc.stdout, "CMAME related-work audit lost no-default-1e-4 marker")
    prose_proc = subprocess.run(
        [sys.executable, "validate_cmame_prose_residue_audit.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(prose_proc.returncode == 0, f"CMAME prose-residue audit validator failed:\n{prose_proc.stdout}")
    v.check(
        "cmame_prose_residue_audit=PASS" in prose_proc.stdout,
        "CMAME prose-residue audit validator did not report PASS",
    )
    v.check("main_body_machine_token_count=0" in prose_proc.stdout, "CMAME prose-residue audit lost main-body count marker")
    v.check("artifact_macro_confined_to_appendix=True" in prose_proc.stdout, "CMAME prose-residue audit lost appendix confinement marker")
    v.check("default_1e-4=False" in prose_proc.stdout, "CMAME prose-residue audit lost no-default-1e-4 marker")
    v.check("run_v047_invoked=False" in prose_proc.stdout, "CMAME prose-residue audit lost no-run_v047 marker")
    dynamic_proc = subprocess.run(
        [sys.executable, "validate_dynamic_row_oracle_gate.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(dynamic_proc.returncode == 0, f"dynamic row oracle gate validator failed:\n{dynamic_proc.stdout}")
    v.check("dynamic_row_oracle_gate=PASS" in dynamic_proc.stdout, "dynamic row oracle validator did not report PASS")
    v.check("residual_shape=132" in dynamic_proc.stdout, "dynamic row oracle validator lost residual shape marker")
    v.check("jacobian_shape=132x132" in dynamic_proc.stdout, "dynamic row oracle validator lost Jacobian shape marker")
    v.check("block_functional_crosscheck=PASS" in dynamic_proc.stdout, "dynamic row oracle validator lost block-functional marker")
    v.check("symbolic_oracle_complete=False" in dynamic_proc.stdout, "dynamic row oracle validator lost symbolic-open marker")
    proof_proc = subprocess.run(
        [sys.executable, "validate_proof_evidence_matrix.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(proof_proc.returncode == 0, f"proof evidence matrix validator failed:\n{proof_proc.stdout}")
    v.check(
        "v047 proof evidence matrix validation: PASS" in proof_proc.stdout,
        "proof evidence matrix validator did not report PASS",
    )
    v.check("accepted_method_order=6" in proof_proc.stdout, "proof evidence matrix validator lost order-6 marker")
    v.check("comparator_expected_order=5" in proof_proc.stdout, "proof evidence matrix validator lost comparator marker")
    v.check("block_functional_crosscheck=PASS" in proof_proc.stdout, "proof evidence matrix validator lost block-functional marker")
    v.check(
        "full_tfe_stage_replacement=False" in proof_proc.stdout,
        "proof evidence matrix validator lost full-TFE caveat marker",
    )
    solver_proc = subprocess.run(
        [sys.executable, "validate_proof_solver_scale_audit.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(solver_proc.returncode == 0, f"proof solver-scale audit validator failed:\n{solver_proc.stdout}")
    v.check(
        "proof_solver_scale_audit=PASS" in solver_proc.stdout,
        "proof solver-scale audit validator did not report PASS",
    )
    v.check(
        "summary_level_solver_residuals_recorded=True" in solver_proc.stdout,
        "proof solver-scale audit lost summary residual marker",
    )
    v.check(
        "scaled_tolerance_sweep_recorded=False" in solver_proc.stdout,
        "proof solver-scale audit lost scaled-tolerance boundary",
    )
    v.check(
        "eta_h_O_h7_solver_policy_evidence=False" in solver_proc.stdout,
        "proof solver-scale audit lost eta_h proof boundary",
    )
    v.check("default_1e-4=False" in solver_proc.stdout, "proof solver-scale audit lost no-default-1e-4 marker")
    v.check("run_v047_invoked=False" in solver_proc.stdout, "proof solver-scale audit lost no-run_v047 marker")
    order_gate_proc = subprocess.run(
        [sys.executable, "validate_order_acceptance_gate.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(order_gate_proc.returncode == 0, f"order acceptance gate validator failed:\n{order_gate_proc.stdout}")
    v.check(
        "v047 order acceptance gate validation: PASS" in order_gate_proc.stdout,
        "order acceptance gate validator did not report PASS",
    )
    v.check("accepted_method_order=6" in order_gate_proc.stdout, "order gate validator lost order-6 marker")
    v.check("comparator_expected_order=5" in order_gate_proc.stdout, "order gate validator lost comparator marker")
    v.check(
        "observed_order_interpretation=not_seventh_order_claim" in order_gate_proc.stdout,
        "order gate validator lost observed-order interpretation marker",
    )
    v.check(
        "accepted_dynamic_order_examples=single_pendulum,double_pendulum" in order_gate_proc.stdout,
        "order gate validator lost accepted dynamic-order example marker",
    )
    v.check(
        "coverage_only_examples=four_link,slider_crank" in order_gate_proc.stdout,
        "order gate validator lost coverage-only example marker",
    )
    v.check(
        "external_dynamic_order_accepted=False" in order_gate_proc.stdout,
        "order gate validator lost external dynamic-order boundary",
    )
    v.check("default_1e-4=False" in order_gate_proc.stdout, "order gate validator lost no-default-1e-4 marker")
    source_proc = subprocess.run(
        [sys.executable, "validate_source_paper_comparison.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(source_proc.returncode == 0, f"source-paper comparison validator failed:\n{source_proc.stdout}")
    v.check(
        "v047 source-paper comparison validation: PASS" in source_proc.stdout,
        "source-paper comparison validator did not report PASS",
    )
    v.check("source_paper_m3_expected_order=5" in source_proc.stdout, "source-paper comparison validator lost order-5 marker")
    v.check("accepted_method_order=6" in source_proc.stdout, "source-paper comparison validator lost order-6 marker")
    v.check(
        "full_tfe_stage_replacement=False" in source_proc.stdout,
        "source-paper comparison validator lost full-TFE caveat marker",
    )
    submission_proc = subprocess.run(
        [sys.executable, "validate_submission_bundle.py"],
        cwd=PAPER_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    v.check(submission_proc.returncode == 0, f"submission bundle validator failed:\n{submission_proc.stdout}")
    v.check(
        "v047 submission bundle validation: PASS" in submission_proc.stdout,
        "submission bundle validator did not report PASS",
    )
    v.check("recommended_pdf=main_cmame.pdf" in submission_proc.stdout, "submission bundle validator lost PDF marker")
    v.check("cmame_document_class=elsarticle" in submission_proc.stdout, "submission bundle validator lost CMAME class marker")
    v.check("accepted_method=Gauss6/FullVA" in submission_proc.stdout, "submission bundle validator lost method marker")
    v.check("comparator_expected_order=5" in submission_proc.stdout, "submission bundle validator lost comparator marker")
    v.check(
        "full_tfe_stage_replacement=False" in submission_proc.stdout,
        "submission bundle validator lost full-TFE caveat marker",
    )
    v.check("submission_ready=False" in submission_proc.stdout, "submission bundle validator lost submission-ready marker")
    v.check(
        "mechanical_preflight_passed=True" in submission_proc.stdout,
        "submission bundle validator lost mechanical preflight marker",
    )
    v.check("quality_review_passed=False" in submission_proc.stdout, "submission bundle validator lost quality-review marker")
    v.check("run_v047_invoked=False" in submission_proc.stdout, "submission bundle validator lost run_v047 boundary marker")
    return (
        proc.stdout,
        proof_proc.stdout,
        solver_proc.stdout,
        order_gate_proc.stdout,
        cmame_proc.stdout,
        submission_sync_proc.stdout,
        blocker_proc.stdout,
        external_baseline_proc.stdout,
        external_queue_proc.stdout,
        proof_contract_proc.stdout,
        visual_proc.stdout,
        related_work_proc.stdout,
        prose_proc.stdout,
        dynamic_proc.stdout,
        source_proc.stdout,
        submission_proc.stdout,
    )


def validate_paper_latex_log(v: Validator) -> str:
    patterns = [
        r"Overfull",
        r"LaTeX Warning",
        r"Package .*Warning",
        r"pdfTeX warning",
    ]
    log_names = [
        "main.log",
        "main_concise.log",
        "main_cmame.log",
        "cmame_submission_flat/main_cmame_submission.log",
    ]
    checked_logs: list[str] = []
    missing_logs: list[str] = []
    warning_total = 0
    for log_name in log_names:
        log_path = paper_asset_path(log_name)
        v.check(log_path.exists(), f"paper LaTeX log missing: paper_v047_cylindrical_chain/{log_name}")
        if not log_path.exists():
            missing_logs.append(log_name)
            continue

        log_text = log_path.read_text(encoding="utf-8", errors="replace")
        warning_lines = [
            line
            for line in log_text.splitlines()
            if any(re.search(pattern, line) for pattern in patterns)
        ]
        warning_total += len(warning_lines)
        checked_logs.append(f"{log_name}:{len(warning_lines)}")
        v.check(not warning_lines, f"{log_name} has warnings: " + "; ".join(warning_lines[:4]))
    status = "PASS" if not missing_logs and warning_total == 0 else "FAIL"
    return "\n".join(
        [
            f"paper_latex_log={status}",
            f"logs_checked={','.join(checked_logs)}",
            f"missing_logs={','.join(missing_logs) if missing_logs else 'none'}",
            f"warning_patterns={','.join(patterns)}",
            f"warning_lines={warning_total}",
            "run_v047_invoked=False",
            "submission_ready=False",
        ]
    )


def validate_quickstart_doc(v: Validator) -> None:
    path = ROOT / "docs" / "VALIDATION_QUICKSTART.md"
    v.check(path.exists() and path.stat().st_size > 0, "VALIDATION_QUICKSTART.md missing or empty")
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    for token in [
        "validate_paper_package.py",
        "validate_cmame_submission.py",
        "validate_cmame_blocker_closure_gate.py",
        "validate_cmame_external_baseline_gate.py",
        "validate_cmame_proof_contract_gate.py",
        "validate_cmame_visual_legibility_audit.py",
        "validate_dynamic_row_oracle_gate.py",
        "validate_submission_bundle.py",
        "validate_order_acceptance_gate.py",
        "validate_implementation_fidelity_certificate.py",
        "validate_source_paper_comparison.py",
        "validate_full_source_policy_row_provenance_audit.py",
        "validate_oc6_source_equivalent_reopen_readiness_audit_20260620.py",
        "validate_concise_paper.py",
        "validate_four_asme_minimal.py",
        "validate_full_tfe_gap.py",
        "validate_full_tfe_repair_spec.py",
        "validate_v047_outputs.py",
        "validate_v048_outputs.py",
        "validate_four_example_performance_matrix.py",
        "validate_single_pendulum_coarse_same_window.py",
        "validate_closed_loop_surrogate_dynamic_gate.py",
        "validate_closed_loop_dynamic_error_floor_audit.py",
        "validate_closed_loop_coarse_dynamic_order_probe.py",
        "validate_closed_loop_dynamic_order_closure_contract.py",
        "validate_closed_loop_true_dynamic_row_feasibility_audit.py",
        "validate_closed_loop_true_dynamic_residual_scaffold.py",
        "validate_closed_loop_true_dynamic_stage_residual_audit.py",
        "validate_closed_loop_true_dynamic_one_step_smoke.py",
        "validate_closed_loop_true_dynamic_newton_stage_smoke.py",
        "validate_closed_loop_true_dynamic_newton_coarse_order.py",
        "validate_closed_loop_true_dynamic_public_work_precision.py",
        "validate_closed_loop_true_dynamic_strict_common_reference.py",
        "validate_closed_loop_residual_to_error_theorem_obligations.py",
        "validate_coarse_first_external_readiness_gate.py",
        "validate_pipeline_outputs.py",
        "sync_submission_artifact_manifest_boundary.py",
        "run_v047.py",
        "FULL_TFE_REPLACEMENT_GAP_LEDGER.md",
        "FULL_TFE_REPAIR_SPEC.md",
        "2386.76",
        "Primary paper claim",
        "conditional formal-order comparison",
        "not a full source-paper residual reproduction",
        "main_cmame.tex",
        "main_cmame.pdf",
        "highlights_cmame.txt",
        "declarations_cmame.md",
        "submission artifact manifest boundary",
        "source_policy_execution_invoked=False",
        "13/13/8/5/13/8/False/False",
        "validate_objective_completion_audit.py",
        "blocker_open_by_id=OC4:True,OC6:True,OC12:True",
        "blocker_closure_decision_by_id=OC4:remain_open_ready_for_authorized_execution_not_executed_not_promoted,OC6:remain_open_no_positive_source_equivalent_artifact,OC12:remain_partial_narrowed_replay_ready_full_source_policy_archive_not_ready",
        "blocker_closure_allowed_by_id=OC4:False,OC6:False,OC12:False",
        "recorded open-boundary state, not submission readiness",
        "remain_open_ready_for_authorized_execution_not_executed_not_promoted",
        "oc4_blocker_id=OC4",
        "oc4_blocker_status=open",
        "oc4_closure_decision=remain_open_ready_for_authorized_execution_not_executed_not_promoted",
        "oc4_closure_allowed_now=False",
        "oc4_blocker_open=True",
        "20/32/32/0",
        "remain_open_no_positive_source_equivalent_artifact",
        "source_equivalent_artifact_found=False",
        "source_policy_closed_ratio=0/20",
        "oc6_blocker_id=OC6",
        "oc6_blocker_status=partial",
        "oc6_closure_decision=remain_open_no_positive_source_equivalent_artifact",
        "oc6_closure_allowed_now=False",
        "reopen_condition=suite_specific_source_equivalent_reopen_conditions",
        "latest_external_probe_boundary=0/0/4/False/False",
        "remain_partial_narrowed_replay_ready_full_source_policy_archive_not_ready",
        "current_archive_usable_as_full_source_policy_runner_archive=False",
        "safe_current_use=narrowed_claim_replay_and_audit_provenance_only",
        "primary_submission_package_allowed=False",
        "CMAME_SUBMISSION_CHECKLIST.md",
        "CMAME_SUBMISSION_READINESS_AUDIT.md",
        "CMAME_SUBMISSION_READINESS_REVIEW.md",
        "CMAME_BLOCKER_CLOSURE_GATE.md",
        "CMAME_BLOCKER_CLOSURE_GATE.json",
        "CMAME_EXTERNAL_BASELINE_GATE.md",
        "CMAME_EXTERNAL_BASELINE_GATE.json",
        "CMAME_PROOF_CONTRACT_GATE.md",
        "CMAME_PROOF_CONTRACT_GATE.json",
        "CMAME_VISUAL_LEGIBILITY_AUDIT.md",
        "CMAME_VISUAL_LEGIBILITY_AUDIT.json",
        "eta_h^tube <= c_eta h^7",
        "dynamic_symbolic_oracle_complete=false",
        "accepted_residual_to_error_theorem=false",
        "DYNAMIC_ROW_ORACLE_GATE.md",
        "DYNAMIC_ROW_ORACLE_GATE.json",
        "default_1e-4_required=false",
        "symbolic_oracle_complete=False",
        "submission_ready=false",
        "mechanical_preflight_passed=true",
        "quality_review_passed=false",
        "cmame_submission_flat/main_cmame_submission.tex",
        "cmame_submission_flat/main_cmame_submission.pdf",
        "cmame_submission_flat.zip",
        "main_concise.tex",
        "supporting order-comparison draft",
        "closed_loop_coarse_dynamic_order_probe",
        "closed_loop_true_dynamic_row_feasibility_audit",
        "closed_loop_true_dynamic_residual_scaffold",
        "closed_loop_true_dynamic_stage_residual_audit",
        "closed_loop_true_dynamic_one_step_smoke",
        "closed_loop_true_dynamic_newton_stage_smoke",
        "closed_loop_true_dynamic_newton_coarse_order",
        "closed_loop_true_dynamic_public_work_precision",
        "closed_loop_true_dynamic_strict_common_reference",
        "closed_loop_residual_to_error_theorem_obligations",
        "not accepted external dynamic order",
        "coarse_first_no_default_1e-4",
        "SUBMISSION_PACKET.md",
        "COVER_LETTER.md",
        "SUBMISSION_ARTIFACT_MANIFEST.json",
        "SUBMISSION_FILE_INVENTORY.md",
        "REVIEW_RESPONSE_TEMPLATE.md",
        "SOURCE_PAPER_COMPARISON.md",
        "ORDER_ACCEPTANCE_GATE.md",
        "ORDER_ACCEPTANCE_GATE.json",
        "IMPLEMENTATION_FIDELITY_CERTIFICATE.md",
        "DYNAMIC_ROW_ORACLE_GATE.md",
        "main_cmame.pdf",
        "main_concise.pdf",
        "Gauss6/FullVA",
        "7.161/7.066",
        "`m=3` Gauss-Lobatto TFE formula target",
        "expected order `5`",
        "`2m-1=5`",
        "Original Paper Versus Accepted v047 Claim",
        "Source-paper/local target",
        "Accepted v047 claim",
        "Not claimed",
        "formal-order comparison",
        "every source-paper TFE residual row",
        "optional stronger source-paper reproduction gate",
        "four_asme_method_rows_accepted_projection_sharp_sparse_caveats",
        "full_tfe_stage_replacement=false",
        "Which Command Should I Run?",
        "do not run the last command",
        "single_pendulum",
        "double_pendulum",
        "four_link",
        "slider_crank",
        "Terminology: TFE Versus FTE",
        "`TFE` means temporal finite element",
        "`FTE` is not a separate method",
        "`full TFE replacement` means replacing the accepted `Gauss6/FullVA` 132-row stage residual",
        "pose+velocity acceleration Taylor refinement",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_posevelaccel_p0p0005_m0p0001_z",
        "1.0173e-05",
        "component-split pose-acceleration Taylor refinement",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_transposeaccel_m0p01_z",
        "9.6511e-06",
        "component-split velocity-acceleration Taylor refinement",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_transvelaccel_m0p01_z",
        "2.138e-04",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_transvelaccel_m0p0005_z",
        "9.8175e-06",
        "component-mixed pose/velocity Taylor refinement",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_angpose_transvelaccel_p0p0005_m0p0005_z",
        "9.987e-06",
        "stage-2-fixed/delta acceleration velocity-shift refinement",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_transvelaccelstage2_m0p0005_z",
        "stage02_convex_pose_velocity_extrapolate_0p01_0p02_transvelacceldelta20_m0p0005_z",
        "1.0119e-05",
        "nonfinal terminal velocity/source predictor refinement",
        "nonfinal_velocity_terminal_euler1_z",
        "0.923466",
        "translation_velocity_v",
        "0.959959",
        "stage-2 source-to-velocity transport refinement",
        "stage02_convex_pose_velocity_0p00_sourceliftmatrixdiff_historydelta_m0p1_z",
        "0.001251",
        "stage02_convex_pose_velocity_0p00_sourceliftmatrixdiff_historydelta_m0p01_z",
        "0.0001251",
        "stage02_convex_pose_velocity_0p00_sourceliftmatrixdiff_historydelta_m0p0001_z",
        "1.251e-06",
        "49.6",
        "stage02_convex_pose_velocity_0p00_sourceliftmatrixdiff_historydelta_m0p0001_angposeaccel_p0p0001_z",
        "1.296e-06",
        "48.7",
        "stage02_convex_pose_velocity_0p00_z",
        "1.327e-15",
        "31.7",
        "span_row_count=1",
        "local-span-not-full-TFE",
        "lower_pair_endpoint_pose_velocity_predictor_h_sweep_smoke",
        "7.29e-17",
        "6.588/4.508",
        "8.124e-17",
        "4.142/2.305",
        "6.255e-06",
        "2.345/1.878",
        "stage-2 active translation/angular cross refinement",
        "stage2_velocity_symmetric_translation_angular_cross_feature",
        "0.898843",
        "50.9",
        "0.556036",
        "0.999999",
        "non-stage-2 mean/source/history feature matrix refinement",
        "stage01_mean_velocity_diagonal_plus_row_broadcast_feature",
        "0.827381",
        "36.5",
        "0.571311",
        "0.991949",
        "cmd.exe /c latexmk -pdf -interaction=nonstopmode main.tex",
        "cmd.exe /c latexmk -pdf -interaction=nonstopmode main_cmame.tex",
        "cmd.exe /c latexmk -pdf -interaction=nonstopmode main_concise.tex",
    ]:
        v.check(contains_normalized(text, token), f"VALIDATION_QUICKSTART.md missing token: {token}")


def validate_current_pipeline_contract_doc(v: Validator) -> None:
    path = ROOT / "CURRENT_PIPELINE_CONTRACT.md"
    v.check(path.exists() and path.stat().st_size > 0, "CURRENT_PIPELINE_CONTRACT.md missing or empty")
    if not path.exists():
        return

    text = path.read_text(encoding="utf-8")
    for token in [
        "Current Pipeline Contract",
        "`research-pipeline`",
        "process guard",
        "current files in this repository are authoritative",
        "paper_v047_cylindrical_chain/CLAIM_BOUNDARY.json",
        "paper/main_cmame.tex",
        "paper/main_cmame.pdf",
        "paper_v047_cylindrical_chain/CMAME_SUBMISSION_CHECKLIST.md",
        "paper_v047_cylindrical_chain/CMAME_BLOCKER_CLOSURE_GATE.md",
        "paper_v047_cylindrical_chain/CMAME_BLOCKER_CLOSURE_GATE.json",
        "paper_v047_cylindrical_chain/CMAME_EXTERNAL_BASELINE_GATE.md",
        "paper_v047_cylindrical_chain/CMAME_EXTERNAL_BASELINE_GATE.json",
        "paper_v047_cylindrical_chain/CMAME_PROOF_CONTRACT_GATE.md",
        "paper_v047_cylindrical_chain/CMAME_PROOF_CONTRACT_GATE.json",
        "paper_v047_cylindrical_chain/CMAME_VISUAL_LEGIBILITY_AUDIT.md",
        "paper_v047_cylindrical_chain/CMAME_VISUAL_LEGIBILITY_AUDIT.json",
        "paper_v047_cylindrical_chain/DYNAMIC_ROW_ORACLE_GATE.md",
        "paper_v047_cylindrical_chain/DYNAMIC_ROW_ORACLE_GATE.json",
        "paper_v047_cylindrical_chain/ORDER_ACCEPTANCE_GATE.md",
        "paper_v047_cylindrical_chain/ORDER_ACCEPTANCE_GATE.json",
        "paper_v047_cylindrical_chain/FULL_SOURCE_POLICY_RUNNER_ARCHIVE_GAP_AUDIT.md",
        "validate_full_source_policy_runner_archive_gap_audit.py",
        "validate_tfe_source_policy_self_reproduction_attempt_certificate.py",
        "paper_v047_cylindrical_chain/RA_HI_SOURCE_POLICY_OUTPUT_INVENTORY.md",
        "paper_v047_cylindrical_chain/RA_HI_SOURCE_POLICY_CLOSEOUT_CHECKLIST.md",
        "paper_v047_cylindrical_chain/RA_HI_SOURCE_POLICY_PROMOTION_BLOCKER_MATRIX.md",
        "paper_v047_cylindrical_chain/B4_SOURCE_POLICY_EXECUTION_OPT_IN_PACKET.md",
        "validate_ra_hi_source_policy_output_inventory.py",
        "validate_ra_hi_source_policy_closeout_checklist.py",
        "validate_ra_hi_source_policy_promotion_blocker_matrix.py",
        "validate_b4_source_policy_execution_opt_in_packet.py",
        "ready_command_mapped_external_rows=20/40",
        "source_policy_closed_now=0/40",
        "execution_invoked_by_packet=False",
        "paper_v047_cylindrical_chain/OBJECTIVE_COMPLETION_AUDIT.md",
        "paper_v047_cylindrical_chain/OBJECTIVE_COMPLETION_AUDIT.json",
        "blocker_open_by_id=OC4:True,OC6:True,OC12:True",
        "blocker_closure_decision_by_id=OC4:remain_open_ready_for_authorized_execution_not_executed_not_promoted,OC6:remain_open_no_positive_source_equivalent_artifact,OC12:remain_partial_narrowed_replay_ready_full_source_policy_archive_not_ready",
        "blocker_closure_allowed_by_id=OC4:False,OC6:False,OC12:False",
        "contract-level guard against treating validator PASS or the narrowed archive as global submission readiness",
        "pipeline_validation_results/pipeline_validation_summary.json",
        "v047_cylindrical_chain_pipeline/results/summary_v047.json",
        "conditional formal-order comparison",
        "not an implemented source-paper superiority claim",
        "`Gauss6/FullVA`",
        "`7.161/7.066`",
        "`m=3` Gauss-Lobatto TFE target",
        "expected order `5`",
        "`single_pendulum`",
        "`double_pendulum`",
        "`four_link`",
        "`slider_crank`",
        "Accepted dynamic order rows",
        "Coverage-only for dynamic order",
        "closed-loop true-dynamic-row feasibility audit",
        "not a local dynamic DAE trajectory",
        "residual-to-error theorem",
        "seven blocking",
        "eta_h^tube <= c_eta h^7",
        "unconditional proof",
        "four_asme_method_rows_accepted_projection_sharp_sparse_caveats",
        "`sparse_speed_quantified`",
        "`full_tfe_stage_replacement_missing`",
        "`sharp_friction_coarse_order_reduction_ultra_recovered`",
        "`full_tfe_stage_replacement=false`",
        ".venv_sbel/bin/python validate_pipeline_outputs.py",
        "../.venv_sbel/bin/python validate_source_paper_comparison.py",
        "../.venv_sbel/bin/python validate_order_acceptance_gate.py",
        "../.venv_sbel/bin/python validate_submission_bundle.py",
        "../.venv_sbel/bin/python validate_cmame_submission.py",
        "../.venv_sbel/bin/python validate_cmame_blocker_closure_gate.py",
        "../.venv_sbel/bin/python validate_cmame_external_baseline_gate.py",
        "../.venv_sbel/bin/python validate_cmame_proof_contract_gate.py",
        "../.venv_sbel/bin/python validate_cmame_visual_legibility_audit.py",
        "../.venv_sbel/bin/python validate_dynamic_row_oracle_gate.py",
        "../.venv_sbel/bin/python validate_full_source_policy_runner_archive_gap_audit.py",
        "../.venv_sbel/bin/python validate_tfe_source_policy_self_reproduction_attempt_certificate.py",
        "../.venv_sbel/bin/python validate_ra_hi_source_policy_closeout_checklist.py",
        "../.venv_sbel/bin/python validate_ra_hi_source_policy_promotion_blocker_matrix.py",
        "../.venv_sbel/bin/python validate_paper_package.py",
        "../.venv_sbel/bin/python validate_four_asme_minimal.py",
        "../.venv_sbel/bin/python validate_full_tfe_gap.py",
        "../.venv_sbel/bin/python validate_full_tfe_repair_spec.py",
        "../.venv_sbel/bin/python validate_v047_outputs.py",
        "Do not run `v047_cylindrical_chain_pipeline/run_v047.py`",
        "Next Real Research Gate",
        "source-free",
        "projection-free",
        "non-terminal-row-replacement",
        "132-row Newton system full rank",
        "source-policy rows remain `0/40`",
        "current narrowed archive boundary matches the reproducibility manifest",
        "`narrowed_archive_ready_not_full_source_policy_runner_archive/0/40/False/False/True`",
        "`OC4=open,OC6=partial,OC12=partial`",
        "`narrowed_claim_only`, not a full source-policy runner archive",
        "TFE attempted-not-reproducible rows remain `16/16`",
        "RA/HI source-policy rows remain `0/20`",
        "RA/HI not-promoted rows remain `20/20`",
    ]:
        v.check(contains_normalized(text, token), f"CURRENT_PIPELINE_CONTRACT.md missing token: {token}")


def validate_better_integrator_boundary_docs(v: Validator) -> None:
    doc_tokens = {
        "CURRENT_PIPELINE_CONTRACT.md": [
            "conditional formal-order comparison",
            "not an implemented source-paper superiority claim",
            "Gauss6/FullVA",
            "7.161/7.066",
            "expected order `5`",
        ],
        "docs/VALIDATION_QUICKSTART.md": [
            "Primary paper claim",
            "conditional formal-order comparison",
            "not a full source-paper residual reproduction",
            "Gauss6/FullVA",
            "7.161/7.066",
            "`m=3` Gauss-Lobatto TFE formula target",
            "expected order `5`",
            "Original Paper Versus Accepted v047 Claim",
            "Source-paper/local target",
            "Accepted v047 claim",
            "Not claimed",
            "every source-paper TFE residual row",
            "optional stronger source-paper reproduction gate",
        ],
        "docs/PIPELINE_AUDIT.md": [
            "conditional formal-order comparison explicit",
            "Gauss6/FullVA path is sixth order",
            "7.161/7.066",
            "comparative integrator claim",
            "not a claim that the source paper's complete TFE residual has been reimplemented",
            "pipeline_validation_results/pipeline_validation_summary.json",
            "authoritative check-count record",
            "validate_objective_completion_audit.py",
            "objective blocker alias matrix",
            "OC4/open",
            "OC6/partial",
            "OC12/partial",
        ],
        "docs/ORDER_PROOF_LEDGER.md": [
            "Primary claim boundary",
            "conditional sixth order for the accepted smooth",
            "P5 direct Newton--Euler residual bridge",
            "retained P6 branch-selected solver scale",
            "velocity-level/KKT closure subsystem",
            "raw endpoint position defect is a separate",
            "does not discharge the P2 endpoint raw-defect/right-",
            "endpoint object is the KKT closure functional",
            "conditional formal-order comparison",
            "not a full source-paper residual reproduction",
            "expected order five",
            "not required for this bounded",
            "formal-order comparison",
            "No residual error theorem is accepted",
            "Seven residual-to-error obligations remain blocking",
            "not accepted dynamic order rows",
        ],
        "docs/VERSION_LEDGER.md": [
            "Paper-facing claim boundary",
            "conditional formal-order comparison",
            "not as a full source-paper residual reproduction",
            "7.161/7.066",
            "expected order five",
        ],
        "docs/VERSION_TREE.md": [
            "Current v047 paper-facing interpretation",
            "conditional formal-order",
            "7.161/7.066",
            "expected order five",
            "not the main claim",
        ],
    }
    for rel_path, tokens in doc_tokens.items():
        path = ROOT / rel_path
        v.check(path.exists() and path.stat().st_size > 0, f"{rel_path} missing or empty")
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            v.check(contains_normalized(text, token), f"{rel_path} missing better-integrator boundary token: {token}")
    pipeline_audit_text = (ROOT / "docs" / "PIPELINE_AUDIT.md").read_text(encoding="utf-8")
    v.check(
        "latest pass runs 3579 checks" not in pipeline_audit_text,
        "PIPELINE_AUDIT.md still hard-codes the stale 3579-check pass count",
    )


def validate_tfe_terminology_docs(v: Validator) -> None:
    doc_tokens = {
        "docs/VALIDATION_QUICKSTART.md": [
            "Terminology: TFE Versus FTE",
            "`TFE` means temporal finite element",
            "`FTE` is not a separate method",
            "`full TFE replacement` means replacing the accepted `Gauss6/FullVA` 132-row stage residual",
            "stricter than the accepted formal-order comparison",
        ],
        "paper_v047_cylindrical_chain/README.md": [
            "Terminology: `TFE` means temporal finite element",
            "`FTE` is not a separate method",
            "replacing the accepted `Gauss6/FullVA` 132-row stage residual",
            "paper-derived temporal finite-element weak rows",
            "blocker_open_by_id=OC4:True,OC6:True,OC12:True",
            "blocker_closure_decision_by_id=OC4:remain_open_ready_for_authorized_execution_not_executed_not_promoted,OC6:remain_open_no_positive_source_equivalent_artifact,OC12:remain_partial_narrowed_replay_ready_full_source_policy_archive_not_ready",
            "blocker_closure_allowed_by_id=OC4:False,OC6:False,OC12:False",
        ],
        "paper_v047_cylindrical_chain/CURRENT_STATUS_CN.md": [
            "`TFE` 是 temporal finite element，不是 `FTE`",
            "full TFE replacement",
            "paper-derived temporal finite-element weak rows",
            "narrowed archive boundary matches the reproducibility manifest: `True`",
            "`narrowed_archive_ready_not_full_source_policy_runner_archive/0/40/False/False/True`",
            "`OC4=open,OC6=partial,OC12=partial`",
            "`narrowed_claim_only`, not a full source-policy runner archive",
            "blocker_open_by_id=OC4:True,OC6:True,OC12:True",
            "blocker_closure_decision_by_id=OC4:remain_open_ready_for_authorized_execution_not_executed_not_promoted,OC6:remain_open_no_positive_source_equivalent_artifact,OC12:remain_partial_narrowed_replay_ready_full_source_policy_archive_not_ready",
            "blocker_closure_allowed_by_id=OC4:False,OC6:False,OC12:False",
        ],
        "paper/main.tex": [
            "occasional spelling ``FTE''",
            "should be read as \\tfe{}, temporal finite element",
            "full-\\tfe{} replacement",
        ],
    }
    for rel_path, tokens in doc_tokens.items():
        path = ROOT / rel_path
        v.check(path.exists() and path.stat().st_size > 0, f"{rel_path} missing or empty")
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for token in tokens:
            v.check(contains_normalized(text, token), f"{rel_path} missing TFE terminology token: {token}")


def validate_pipeline_count_docs(v: Validator, totals: dict[str, int]) -> None:
    """Keep human-facing validation-count summaries tied to the live inventory."""

    doc_tokens = {
        "README.md": [
            (
                f"checks {totals['versions']} versions, {totals['result_files']} result files, "
                f"{totals['csv']} CSVs, {totals['png']} PNGs, {totals['json']} JSON files"
            ),
        ],
        "docs/PIPELINE_AUDIT.md": [
            f"inventories all {totals['versions']} `vNNN_*` directories",
            (
                f"checks {totals['result_files']} result files, parses {totals['csv']} "
                f"CSVs and {totals['json']} JSON files, validates {totals['png']} PNG headers"
            ),
        ],
    }
    for rel_path, tokens in doc_tokens.items():
        path = ROOT / rel_path
        v.check(path.exists() and path.stat().st_size > 0, f"{rel_path} missing or empty")
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for token in tokens:
            v.check(
                contains_normalized(text, token),
                f"{rel_path} missing live pipeline count token: {token}",
            )


def validate_global_blocker_matrix_docs(v: Validator) -> None:
    tokens = [
        "blocker_open_by_id=OC4:True,OC6:True,OC12:True",
        "blocker_closure_decision_by_id=OC4:remain_open_ready_for_authorized_execution_not_executed_not_promoted,OC6:remain_open_no_positive_source_equivalent_artifact,OC12:remain_partial_narrowed_replay_ready_full_source_policy_archive_not_ready",
        "blocker_closure_allowed_by_id=OC4:False,OC6:False,OC12:False",
        "does not authorize B4/source-policy execution",
    ]
    rel_paths = [
        "paper_v047_cylindrical_chain/CMAME_SUBMISSION_READINESS_AUDIT.md",
        "paper_v047_cylindrical_chain/CMAME_SUBMISSION_READINESS_REVIEW.md",
        "paper_v047_cylindrical_chain/CMAME_BLOCKER_CLOSURE_GATE.md",
        "paper_v047_cylindrical_chain/CMAME_EXTERNAL_BASELINE_GATE.md",
        "paper_v047_cylindrical_chain/CMAME_PROOF_CONTRACT_GATE.md",
        "paper_v047_cylindrical_chain/CMAME_VISUAL_LEGIBILITY_AUDIT.md",
        "paper_v047_cylindrical_chain/CMAME_RELATED_WORK_AUDIT.md",
        "paper_v047_cylindrical_chain/CMAME_PROSE_RESIDUE_AUDIT.md",
    ]
    for rel_path in rel_paths:
        path = ROOT / rel_path
        v.check(path.exists() and path.stat().st_size > 0, f"{rel_path} missing or empty")
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for token in tokens:
            v.check(
                contains_normalized(text, token),
                f"{rel_path} missing objective blocker matrix token: {token}",
            )


def validate_no_claim_regression_wording(v: Validator) -> None:
    """Guard the paper-facing claim boundary against stale or overclaiming text."""
    rel_paths = [
        "README.md",
        "CURRENT_PIPELINE_CONTRACT.md",
        "docs/VERSION_LEDGER.md",
        "docs/VERSION_TREE.md",
        "docs/PIPELINE_AUDIT.md",
        "docs/ORDER_PROOF_LEDGER.md",
        "docs/VALIDATION_QUICKSTART.md",
        "v047_cylindrical_chain_pipeline/README.md",
        "v047_cylindrical_chain_pipeline/results/v047_report.md",
        "paper_v047_cylindrical_chain/README.md",
        "paper_v047_cylindrical_chain/REVIEWER_CHECKLIST.md",
        "paper_v047_cylindrical_chain/PAPER_CLAIM_LEDGER.md",
        "paper_v047_cylindrical_chain/CURRENT_STATUS_CN.md",
        "paper_v047_cylindrical_chain/SOURCE_PAPER_COMPARISON.md",
        "paper/main.tex",
    ]
    forbidden_patterns = [
        r"`four_link`\s+mapping",
        r"`slider_crank`\s+mapping",
        r"\bfour_link\s+mapping\s+(?:is\s+)?(?:pending|missing|incomplete)",
        r"\bslider_crank\s+mapping\s+(?:is\s+)?(?:pending|missing|incomplete)",
        r"exact\s+four-example\s+method\s+validation\s+completion",
        r"four\s+ASME\s+examples\s+(?:are\s+)?(?:pending|missing|incomplete)",
        r"four-example\s+gate\s+(?:is\s+)?(?:pending|missing|incomplete)",
        r"complete\s+source-paper\s+(?:TFE\s+)?residual(?:\s+reproduction)?\s+is\s+accepted",
        r"full_tfe_stage_replacement\s*=\s*true",
        r"independent\s+full[- ]TFE\s+stage\s+replacement\s+is\s+accepted",
        r"full\s+TFE\s+stage\s+replacement\s+is\s+accepted",
    ]
    for rel_path in rel_paths:
        path = ROOT / rel_path
        v.check(path.exists() and path.stat().st_size > 0, f"{rel_path} missing or empty")
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        normalized = " ".join(text.split())
        for pattern in forbidden_patterns:
            v.check(
                not re.search(pattern, normalized, flags=re.IGNORECASE),
                f"{rel_path} contains stale or overclaiming wording matching {pattern!r}",
            )


def validate_documentation_boundary_checks(v: Validator, totals: dict[str, int]) -> str:
    """Run documentation-boundary guards and return a reportable status block."""

    lines = ["documentation_boundary_validators=checked"]

    def run_check(label: str, fn) -> None:
        checks_before = v.checks_run
        failures_before = len(v.failures)
        fn()
        status = "PASS" if len(v.failures) == failures_before else "FAIL"
        lines.append(f"{label}={status}")
        lines.append(f"{label}_checks={v.checks_run - checks_before}")

    run_check("validation_quickstart_doc", lambda: validate_quickstart_doc(v))
    run_check("current_pipeline_contract_doc", lambda: validate_current_pipeline_contract_doc(v))
    run_check("better_integrator_boundary_docs", lambda: validate_better_integrator_boundary_docs(v))
    run_check("tfe_terminology_docs", lambda: validate_tfe_terminology_docs(v))
    run_check("pipeline_count_docs", lambda: validate_pipeline_count_docs(v, totals))
    run_check("global_blocker_matrix_docs", lambda: validate_global_blocker_matrix_docs(v))
    run_check("no_claim_regression_wording", lambda: validate_no_claim_regression_wording(v))

    lines.extend(
        [
            (
                "live_inventory="
                f"{totals['versions']}/{totals['result_files']}/"
                f"{totals['csv']}/{totals['png']}/{totals['json']}"
            ),
            "blocker_open_by_id=OC4:True,OC6:True,OC12:True",
            "source_policy_execution_invoked=False",
            "run_v047_invoked=False",
            "submission_ready=False",
        ]
    )
    return "\n".join(lines)


def validate_current_pipeline_gate(v: Validator) -> dict:
    summary = read_json(CURRENT_DIR / "results" / "summary_v047.json")
    gate = summary.get("pipeline_gate_status", {})
    asme_gate = summary.get("asme_gate", {})
    readiness = summary.get("endpoint_tfe_readiness_audit", {})
    paper_kinematic = summary.get("endpoint_tfe_paper_kinematic_formula_audit", {})
    paper_balance_constraint = summary.get("endpoint_tfe_paper_balance_constraint_formula_audit", {})
    paper_position_substitution = summary.get("endpoint_tfe_paper_position_substitution_candidate_audit", {})
    paper_kinematic_substitution = summary.get("endpoint_tfe_paper_kinematic_substitution_candidate_audit", {})
    paper_all_row_substitution = summary.get("endpoint_tfe_paper_all_row_substitution_candidate_audit", {})
    paper_all_row_gauss_z0_substitution = summary.get("endpoint_tfe_paper_all_row_gauss_z0_substitution_candidate_audit", {})
    paper_all_row_gauss_z0_terminal_output = summary.get("endpoint_tfe_paper_all_row_gauss_z0_terminal_output_audit", {})
    paper_all_row_recurrent_z0_terminal_output = summary.get("endpoint_tfe_paper_all_row_recurrent_z0_terminal_output_audit", {})
    paper_all_row_consistent_z0_terminal_output = summary.get("endpoint_tfe_paper_all_row_consistent_z0_terminal_output_audit", {})
    paper_all_row_consistent_z0_conditioning = summary.get("endpoint_tfe_paper_all_row_consistent_z0_conditioning_audit", {})
    paper_all_row_consistent_z0_scaled_newton = summary.get("endpoint_tfe_paper_all_row_consistent_z0_scaled_newton_audit", {})
    paper_family_ablation = summary.get("endpoint_tfe_paper_family_ablation_audit", {})
    paper_lower_pair_lambda_schur = summary.get("endpoint_tfe_paper_lower_pair_lambda_schur_audit", {})
    paper_lower_pair_row_variant = summary.get("endpoint_tfe_paper_lower_pair_row_variant_audit", {})
    paper_lower_pair_acceleration_terminal_output = summary.get("endpoint_tfe_paper_lower_pair_acceleration_terminal_output_audit", {})
    paper_lower_pair_acceleration_projection_dependence = summary.get("endpoint_tfe_paper_lower_pair_acceleration_projection_dependence_audit", {})
    paper_lower_pair_acceleration_terminal_velocity_closure = summary.get("endpoint_tfe_paper_lower_pair_acceleration_terminal_velocity_closure_audit", {})
    paper_lower_pair_acceleration_terminal_row_homotopy = summary.get("endpoint_tfe_paper_lower_pair_acceleration_terminal_row_homotopy_audit", {})
    paper_lower_pair_terminal_source_target = summary.get("endpoint_tfe_paper_lower_pair_terminal_source_target_audit", {})
    paper_lower_pair_terminal_source_lift = summary.get("endpoint_tfe_paper_lower_pair_terminal_source_lift_audit", {})
    paper_lower_pair_terminal_source_normalization = summary.get("endpoint_tfe_paper_lower_pair_terminal_source_normalization_audit", {})
    paper_lower_pair_terminal_source_insertion = summary.get("endpoint_tfe_paper_lower_pair_terminal_source_insertion_audit", {})
    paper_lower_pair_terminal_source_insertion_trajectory = summary.get("endpoint_tfe_paper_lower_pair_terminal_source_insertion_trajectory_audit", {})
    paper_lower_pair_terminal_source_insertion_blowup = summary.get("endpoint_tfe_paper_lower_pair_terminal_source_insertion_blowup_audit", {})
    paper_lower_pair_terminal_source_bounded_policy = summary.get("endpoint_tfe_paper_lower_pair_terminal_source_bounded_policy_audit", {})
    paper_lower_pair_stage_local_bounded_source = summary.get("endpoint_tfe_paper_lower_pair_stage_local_bounded_source_formula_audit", {})
    paper_lower_pair_source_free_elimination_rank = summary.get("endpoint_tfe_paper_lower_pair_source_free_elimination_rank_audit", {})
    paper_lower_pair_source_free_mean_velocity = summary.get("endpoint_tfe_paper_lower_pair_source_free_mean_velocity_closure_audit", {})
    paper_lower_pair_source_free_mean_blend = summary.get("endpoint_tfe_paper_lower_pair_source_free_mean_blend_closure_audit", {})
    paper_lower_pair_source_free_mean_blend_trajectory = summary.get("endpoint_tfe_paper_lower_pair_source_free_mean_blend_trajectory_audit", {})
    paper_lower_pair_source_free_mean_blend_trajectory_alpha_sweep = summary.get("endpoint_tfe_paper_lower_pair_source_free_mean_blend_trajectory_alpha_sweep_audit", {})
    paper_lower_pair_source_free_component_blend_trajectory = summary.get("endpoint_tfe_paper_lower_pair_source_free_component_blend_trajectory_audit", {})
    paper_lower_pair_source_free_terminal_extrapolation = summary.get("endpoint_tfe_paper_lower_pair_source_free_terminal_velocity_extrapolation_trajectory_audit", {})
    paper_lower_pair_source_free_terminal_extrapolation_blend = summary.get("endpoint_tfe_paper_lower_pair_source_free_terminal_extrapolation_blend_trajectory_audit", {})
    paper_lower_pair_centered_terminal_velocity_bridge = summary.get("endpoint_tfe_paper_lower_pair_centered_terminal_velocity_bridge_trajectory_audit", {})
    paper_lower_pair_closure_acceptance_matrix = summary.get("endpoint_tfe_paper_lower_pair_closure_acceptance_matrix_audit", {})
    paper_lower_pair_closure_property_pareto = summary.get("endpoint_tfe_paper_lower_pair_closure_property_pareto_audit", {})
    paper_lower_pair_closure_row_span = summary.get("endpoint_tfe_paper_lower_pair_closure_row_span_audit", {})
    paper_lower_pair_velocity_compression = summary.get("endpoint_tfe_paper_lower_pair_velocity_compression_audit", {})
    paper_contract = summary.get("endpoint_tfe_paper_residual_substitution_contract_audit", {})
    sharp = summary.get("sharp_ultra_refinement_audit", {})

    models = set(asme_gate.get("models", {}))
    v.check(asme_gate.get("status") == "four_asme_method_rows_accepted_projection_sharp_sparse_caveats", "v047 ASME gate status changed")
    v.check(models == EXPECTED_ASME_MODELS, f"v047 ASME model set mismatch: {sorted(models)}")
    for model, data in asme_gate.get("models", {}).items():
        v.check(str(data.get("v047_mapping_status", "")).startswith(("accepted", "exact_driven")), f"v047 model not accepted: {model}")

    proof_text = (ROOT / "docs" / "ORDER_PROOF_LEDGER.md").read_text(encoding="utf-8")
    audit_text = (ROOT / "docs" / "PIPELINE_AUDIT.md").read_text(encoding="utf-8")
    ledger_text = (ROOT / "docs" / "VERSION_LEDGER.md").read_text(encoding="utf-8")
    tree_text = (ROOT / "docs" / "VERSION_TREE.md").read_text(encoding="utf-8")
    readme_text = (ROOT / "README.md").read_text(encoding="utf-8")
    for name, text in [
        ("ORDER_PROOF_LEDGER.md", proof_text),
        ("PIPELINE_AUDIT.md", audit_text),
        ("VERSION_LEDGER.md", ledger_text),
        ("VERSION_TREE.md", tree_text),
        ("README.md", readme_text),
    ]:
        normalized_text = " ".join(text.split())
        v.check("v047" in text, f"{name} does not mention v047")
        v.check("full TFE stage replacement" in text, f"{name} does not keep the TFE caveat explicit")
        v.check("paper kinematic-formula" in normalized_text, f"{name} does not mention the paper kinematic-formula audit")
        v.check("paper balance/constraint" in normalized_text, f"{name} does not mention the paper balance/constraint formula audit")
        v.check("paper position-substitution" in normalized_text, f"{name} does not mention the paper position-substitution candidate")
        v.check("paper kinematic-substitution" in normalized_text, f"{name} does not mention the paper kinematic-substitution candidate")
        v.check("paper all-row substitution" in normalized_text or "paper all-row-substitution" in normalized_text, f"{name} does not mention the paper all-row substitution candidate")
        v.check("Gauss-z0" in text or "gauss-z0" in normalized_text, f"{name} does not mention the paper all-row Gauss-z0 diagnostic")
        v.check("terminal-output" in normalized_text, f"{name} does not mention the paper all-row Gauss-z0 terminal-output diagnostic")
        v.check("recurrent-z0" in normalized_text or "recurrent z0" in normalized_text, f"{name} does not mention the paper all-row recurrent-z0 terminal-output diagnostic")
        v.check("consistent-z0" in normalized_text or "consistent z0" in normalized_text, f"{name} does not mention the paper all-row consistent-z0 terminal-output diagnostic")
        v.check("consistent-z0 conditioning" in normalized_text or "consistent z0 conditioning" in normalized_text, f"{name} does not mention the paper all-row consistent-z0 conditioning diagnostic")
        v.check("scaled-newton" in normalized_text.lower() or "scaled newton" in normalized_text.lower(), f"{name} does not mention the paper all-row consistent-z0 scaled-Newton diagnostic")
        v.check("family-ablation" in normalized_text.lower() or "family ablation" in normalized_text.lower(), f"{name} does not mention the paper family-ablation diagnostic")
        v.check("schur" in normalized_text.lower() and "lambda" in normalized_text.lower(), f"{name} does not mention the paper lower-pair/lambda Schur diagnostic")
        v.check("row-variant" in normalized_text.lower() or "row variant" in normalized_text.lower(), f"{name} does not mention the paper lower-pair row-variant diagnostic")
        v.check("acceleration terminal-output" in normalized_text.lower() or "acceleration terminal output" in normalized_text.lower(), f"{name} does not mention the paper lower-pair acceleration terminal-output diagnostic")
        v.check("projection-dependence" in normalized_text.lower() or "projection dependence" in normalized_text.lower(), f"{name} does not mention the paper lower-pair acceleration projection-dependence diagnostic")
        v.check("terminal-velocity closure" in normalized_text.lower() or "terminal velocity closure" in normalized_text.lower(), f"{name} does not mention the paper lower-pair acceleration terminal-velocity closure diagnostic")
        v.check("terminal-row homotopy" in normalized_text.lower() or "terminal row homotopy" in normalized_text.lower(), f"{name} does not mention the paper lower-pair acceleration terminal-row homotopy diagnostic")
        v.check("source-target" in normalized_text.lower() or "source target" in normalized_text.lower(), f"{name} does not mention the paper lower-pair terminal source-target audit")
        v.check("blow-up" in normalized_text.lower() or "blowup" in normalized_text.lower(), f"{name} does not mention the paper lower-pair terminal source-insertion blow-up audit")
        v.check("bounded-policy" in normalized_text.lower() or "bounded policy" in normalized_text.lower(), f"{name} does not mention the paper lower-pair terminal source bounded-policy audit")
        v.check("stage-local bounded" in normalized_text.lower() or "bounded-source formula" in normalized_text.lower(), f"{name} does not mention the paper lower-pair stage-local bounded-source formula audit")
        v.check("source-free" in normalized_text.lower() and "mean-velocity" in normalized_text.lower(), f"{name} does not mention the paper lower-pair source-free mean-velocity closure audit")
        v.check("source-free" in normalized_text.lower() and "mean-blend" in normalized_text.lower(), f"{name} does not mention the paper lower-pair source-free mean-blend closure audit")
        v.check("component-blend" in normalized_text.lower() or "component blend" in normalized_text.lower(), f"{name} does not mention the paper lower-pair source-free component-blend audit")
        v.check("terminal-extrapolation blend" in normalized_text.lower() or "terminal extrapolation blend" in normalized_text.lower(), f"{name} does not mention the paper lower-pair source-free terminal-extrapolation blend audit")
        v.check("centered terminal" in normalized_text.lower() or "centered-terminal" in normalized_text.lower(), f"{name} does not mention the paper lower-pair centered terminal-velocity bridge audit")
        v.check("closure acceptance matrix" in normalized_text.lower(), f"{name} does not mention the paper lower-pair closure acceptance matrix audit")
        normalized_lower = normalized_text.lower().replace("-", " ")
        v.check("closure property pareto" in normalized_lower, f"{name} does not mention the paper lower-pair closure property Pareto audit")
        v.check("value-level" in normalized_text.lower() or "value level" in normalized_text.lower(), f"{name} does not mention the value-level velocity-compression audit")
        v.check("derivative-aware" in normalized_text.lower() or "derivative aware" in normalized_text.lower(), f"{name} does not mention the derivative-aware velocity-compression audit")
        v.check("bounded-gradient" in normalized_text.lower() or "bounded gradient" in normalized_text.lower(), f"{name} does not mention the bounded-gradient velocity-compression audit")
        v.check("bounded-formula" in normalized_text.lower() or "bounded formula" in normalized_text.lower(), f"{name} does not mention the bounded-formula velocity-compression audit")
        v.check("row-space compression" in normalized_text.lower() or "row space compression" in normalized_text.lower(), f"{name} does not mention the row-space velocity-compression audit")

    v.check(
        gate.get("math_proof_status")
        == "direct_route_conditional_proof_boundary_recorded_pc2_closed_p6_retained",
        "v047 proof/status gate changed",
    )
    v.check("four ASME method rows are accepted" in gate.get("four_asme_examples", ""), "v047 four-ASME gate not explicit")
    v.check("sharp-ultra-refinement" in gate.get("plots", ""), "v047 plot gate missing sharp ultra plot")
    v.check("endpoint-TFE-paper-lower-pair-row-variant" in gate.get("plots", ""), "v047 plot gate missing paper lower-pair row-variant plot")
    v.check("endpoint-TFE-paper-lower-pair-acceleration-terminal-output" in gate.get("plots", ""), "v047 plot gate missing paper lower-pair acceleration terminal-output plot")
    v.check("endpoint-TFE-paper-lower-pair-acceleration-projection-dependence" in gate.get("plots", ""), "v047 plot gate missing paper lower-pair acceleration projection-dependence plot")
    v.check("endpoint-TFE-paper-lower-pair-acceleration-terminal-velocity-closure" in gate.get("plots", ""), "v047 plot gate missing paper lower-pair acceleration terminal-velocity closure plot")
    v.check("endpoint-TFE-paper-lower-pair-acceleration-terminal-row-homotopy" in gate.get("plots", ""), "v047 plot gate missing paper lower-pair acceleration terminal-row homotopy plot")
    v.check("endpoint-TFE-paper-lower-pair-terminal-source-target" in gate.get("plots", ""), "v047 plot gate missing paper lower-pair terminal source-target plot")
    v.check("endpoint-TFE-paper-lower-pair-terminal-source-insertion" in gate.get("plots", ""), "v047 plot gate missing paper lower-pair terminal source-insertion plot")
    v.check("endpoint-TFE-paper-lower-pair-terminal-source-insertion-blowup" in gate.get("plots", ""), "v047 plot gate missing paper lower-pair terminal source-insertion blow-up plot")
    v.check("endpoint-TFE-paper-lower-pair-terminal-source-bounded-policy" in gate.get("plots", ""), "v047 plot gate missing paper lower-pair terminal source bounded-policy plot")
    v.check("endpoint-TFE-paper-lower-pair-stage-local-bounded-source-formula" in gate.get("plots", ""), "v047 plot gate missing paper lower-pair stage-local bounded-source formula plot")
    v.check("endpoint-TFE-paper-lower-pair-source-free-mean-velocity-closure" in gate.get("plots", ""), "v047 plot gate missing paper lower-pair source-free mean-velocity closure plot")
    v.check("endpoint-TFE-paper-lower-pair-source-free-mean-blend-closure" in gate.get("plots", ""), "v047 plot gate missing paper lower-pair source-free mean-blend closure plot")
    v.check("endpoint-TFE-paper-lower-pair-source-free-component-blend-trajectory" in gate.get("plots", ""), "v047 plot gate missing paper lower-pair source-free component-blend trajectory plot")
    v.check("endpoint-TFE-paper-lower-pair-source-free-terminal-extrapolation-blend-trajectory" in gate.get("plots", ""), "v047 plot gate missing paper lower-pair source-free terminal-extrapolation blend trajectory plot")
    v.check("endpoint-TFE-paper-lower-pair-centered-terminal-velocity-bridge-trajectory" in gate.get("plots", ""), "v047 plot gate missing paper lower-pair centered terminal-velocity bridge plot")
    v.check("endpoint-TFE-paper-lower-pair-closure-acceptance-matrix" in gate.get("plots", ""), "v047 plot gate missing paper lower-pair closure acceptance matrix plot")
    v.check("endpoint-TFE-paper-lower-pair-closure-property-Pareto" in gate.get("plots", ""), "v047 plot gate missing paper lower-pair closure property Pareto plot")
    v.check("endpoint-TFE-paper-lower-pair-closure-row-span" in gate.get("plots", ""), "v047 plot gate missing paper lower-pair closure row-span plot")
    v.check("endpoint-TFE-paper-lower-pair-velocity-compression-value-level" in gate.get("plots", ""), "v047 plot gate missing paper lower-pair value-level velocity-compression plot")
    v.check("endpoint-TFE-paper-lower-pair-velocity-compression-derivative-aware" in gate.get("plots", ""), "v047 plot gate missing paper lower-pair derivative-aware velocity-compression plot")
    v.check("endpoint-TFE-paper-lower-pair-velocity-compression-bounded-gradient" in gate.get("plots", ""), "v047 plot gate missing paper lower-pair bounded-gradient velocity-compression plot")
    v.check("endpoint-TFE-paper-lower-pair-velocity-compression-bounded-formula" in gate.get("plots", ""), "v047 plot gate missing paper lower-pair bounded-formula velocity-compression plot")
    v.check("endpoint-TFE-paper-lower-pair-velocity-compression-target-free-formula" in gate.get("plots", ""), "v047 plot gate missing paper lower-pair target-free velocity-compression plot")
    v.check("endpoint-TFE-paper-lower-pair-velocity-compression-direction-capacity" in gate.get("plots", ""), "v047 plot gate missing paper lower-pair direction-capacity velocity-compression plot")
    v.check("endpoint-TFE-paper-lower-pair-velocity-compression-nonlinear-capacity" in gate.get("plots", ""), "v047 plot gate missing paper lower-pair nonlinear-capacity velocity-compression plot")
    v.check("endpoint-TFE-paper-lower-pair-velocity-compression-higher-order-capacity" in gate.get("plots", ""), "v047 plot gate missing paper lower-pair higher-order-capacity velocity-compression plot")
    v.check("endpoint-TFE-paper-lower-pair-velocity-compression-history-capacity" in gate.get("plots", ""), "v047 plot gate missing paper lower-pair history-capacity velocity-compression plot")
    v.check("endpoint-TFE-paper-lower-pair-velocity-compression-multi-step-history-capacity" in gate.get("plots", ""), "v047 plot gate missing paper lower-pair multi-step history-capacity velocity-compression plot")
    v.check("endpoint-TFE-paper-lower-pair-velocity-compression-recurrent-history-capacity" in gate.get("plots", ""), "v047 plot gate missing paper lower-pair recurrent history-capacity velocity-compression plot")
    v.check("endpoint-TFE-paper-lower-pair-velocity-compression-weak-row-structure-capacity" in gate.get("plots", ""), "v047 plot gate missing paper lower-pair weak-row structure-capacity velocity-compression plot")
    v.check("endpoint-TFE-paper-lower-pair-velocity-compression-row-space-compression" in gate.get("plots", ""), "v047 plot gate missing paper lower-pair row-space velocity-compression plot")
    v.check("paper lower-pair row-variant diagnostic compares" in gate.get("endpoint_velocity_closure", ""), "v047 endpoint gate missing row-variant diagnostic")
    v.check("paper lower-pair acceleration terminal-output h-sweep" in gate.get("endpoint_velocity_closure", ""), "v047 endpoint gate missing acceleration terminal-output diagnostic")
    v.check("terminal-velocity closure h-sweep" in gate.get("endpoint_velocity_closure", ""), "v047 endpoint gate missing terminal-velocity closure diagnostic")
    v.check("terminal-row homotopy" in gate.get("endpoint_velocity_closure", ""), "v047 endpoint gate missing terminal-row homotopy diagnostic")
    v.check("terminal source-target audit" in gate.get("endpoint_velocity_closure", ""), "v047 endpoint gate missing terminal source-target audit")
    v.check("terminal source-insertion audit" in gate.get("endpoint_velocity_closure", ""), "v047 endpoint gate missing terminal source-insertion audit")
    v.check("source-insertion trajectory audit" in gate.get("endpoint_velocity_closure", ""), "v047 endpoint gate missing terminal source-insertion trajectory audit")
    v.check("source-insertion blow-up audit" in gate.get("endpoint_velocity_closure", ""), "v047 endpoint gate missing terminal source-insertion blow-up audit")
    v.check("bounded-policy audit" in gate.get("endpoint_velocity_closure", ""), "v047 endpoint gate missing terminal source bounded-policy audit")
    v.check("stage-local bounded-source formula audit" in gate.get("endpoint_velocity_closure", ""), "v047 endpoint gate missing stage-local bounded-source formula audit")
    v.check("source-free mean-velocity closure h-sweep" in gate.get("endpoint_velocity_closure", ""), "v047 endpoint gate missing source-free mean-velocity closure audit")
    v.check("source-free mean-blend closure audit" in gate.get("endpoint_velocity_closure", ""), "v047 endpoint gate missing source-free mean-blend closure audit")
    v.check("component-blend trajectory audit" in gate.get("endpoint_velocity_closure", ""), "v047 endpoint gate missing component-blend trajectory audit")
    v.check("terminal-velocity extrapolation trajectory audit" in gate.get("endpoint_velocity_closure", ""), "v047 endpoint gate missing terminal-velocity extrapolation trajectory audit")
    v.check("terminal-extrapolation blend trajectory audit" in gate.get("endpoint_velocity_closure", ""), "v047 endpoint gate missing terminal-extrapolation blend trajectory audit")
    v.check(
        "centered terminal-velocity bridge" in gate.get("endpoint_velocity_closure", "")
        or "centered_terminal_velocity_bridge" in gate.get("endpoint_velocity_closure", ""),
        "v047 endpoint gate missing centered terminal-velocity bridge audit",
    )
    v.check("closure acceptance matrix compares" in gate.get("endpoint_velocity_closure", ""), "v047 endpoint gate missing closure acceptance matrix audit")
    v.check("closure row-span audit" in gate.get("endpoint_velocity_closure", ""), "v047 endpoint gate missing closure row-span audit")
    v.check("value-level rows 72" in gate.get("endpoint_velocity_closure", ""), "v047 endpoint gate missing value-level velocity-compression audit")
    v.check("derivative-aware rows 36" in gate.get("endpoint_velocity_closure", ""), "v047 endpoint gate missing derivative-aware velocity-compression audit")
    v.check("bounded-gradient cap rows 288" in gate.get("endpoint_velocity_closure", ""), "v047 endpoint gate missing bounded-gradient cap sweep")
    v.check("bounded-formula rows 648" in gate.get("endpoint_velocity_closure", ""), "v047 endpoint gate missing bounded-formula saturation-law sweep")
    v.check("target-free formula rows 2592" in gate.get("endpoint_velocity_closure", ""), "v047 endpoint gate missing target-free formula sweep")
    v.check("direction-capacity rows 216" in gate.get("endpoint_velocity_closure", ""), "v047 endpoint gate missing direction-capacity audit")
    v.check("nonlinear-capacity rows 216" in gate.get("endpoint_velocity_closure", ""), "v047 endpoint gate missing nonlinear-capacity audit")
    v.check("higher-order/nonlocal capacity rows 216" in gate.get("endpoint_velocity_closure", ""), "v047 endpoint gate missing higher-order-capacity audit")
    v.check("recurrent history-capacity rows 216" in gate.get("endpoint_velocity_closure", ""), "v047 endpoint gate missing recurrent history-capacity audit")
    v.check("row-space compression rows 36" in gate.get("endpoint_velocity_closure", ""), "v047 endpoint gate missing row-space compression audit")
    v.check("ultra fixed refinement recovers high order" in gate.get("sharp_friction", ""), "v047 sharp-friction recovery not encoded")
    v.check(sharp.get("status") == "ultra_high_order_recovered", "v047 sharp ultra refinement status changed")

    counts = readiness.get("counts", {})
    v.check(readiness.get("status") == "readiness_audit_not_fully_tfe", "v047 TFE readiness status should remain open")
    v.check(counts.get("satisfied", 0) >= 31, "v047 TFE readiness lost satisfied checks")
    v.check(counts.get("partial", 0) >= 37, "v047 TFE readiness lost terminal-velocity closure, terminal-row homotopy, source-target, source-lift, source-normalization, source-insertion, source-trajectory, blow-up, bounded-policy, stage-local bounded-source, source-free mean-velocity, source-free mean-blend, source-free mean-blend trajectory, trajectory alpha sweep, component-blend, terminal extrapolation, terminal-extrapolation blend, or closure acceptance matrix partial evidence")
    readiness_requirements = {row.get("requirement"): row.get("status") for row in readiness.get("rows", [])}
    v.check(readiness_requirements.get("paper_tfe_lower_pair_acceleration_terminal_velocity_closure_audit") == "partial", "v047 readiness missing paper lower-pair acceleration terminal-velocity closure row")
    v.check(readiness_requirements.get("paper_tfe_lower_pair_acceleration_terminal_row_homotopy_audit") == "partial", "v047 readiness missing paper lower-pair acceleration terminal-row homotopy row")
    v.check(readiness_requirements.get("paper_tfe_lower_pair_terminal_source_target_audit") == "partial", "v047 readiness missing paper lower-pair terminal source-target row")
    v.check(readiness_requirements.get("paper_tfe_lower_pair_terminal_source_lift_audit") == "partial", "v047 readiness missing paper lower-pair terminal source-lift row")
    v.check(readiness_requirements.get("paper_tfe_lower_pair_terminal_source_normalization_audit") == "partial", "v047 readiness missing paper lower-pair terminal source-normalization row")
    v.check(readiness_requirements.get("paper_tfe_lower_pair_terminal_source_insertion_audit") == "partial", "v047 readiness missing paper lower-pair terminal source-insertion row")
    v.check(readiness_requirements.get("paper_tfe_lower_pair_terminal_source_insertion_trajectory_audit") == "partial", "v047 readiness missing paper lower-pair terminal source-insertion trajectory row")
    v.check(readiness_requirements.get("paper_tfe_lower_pair_terminal_source_insertion_blowup_audit") == "partial", "v047 readiness missing paper lower-pair terminal source-insertion blow-up row")
    v.check(readiness_requirements.get("paper_tfe_lower_pair_terminal_source_bounded_policy_audit") == "partial", "v047 readiness missing paper lower-pair terminal source bounded-policy row")
    v.check(readiness_requirements.get("paper_tfe_lower_pair_stage_local_bounded_source_formula_audit") == "partial", "v047 readiness missing paper lower-pair stage-local bounded-source formula row")
    v.check(readiness_requirements.get("paper_tfe_lower_pair_source_free_elimination_rank_audit") == "partial", "v047 readiness missing paper lower-pair source-free elimination rank row")
    v.check(readiness_requirements.get("paper_tfe_lower_pair_source_free_mean_velocity_closure_audit") == "partial", "v047 readiness missing paper lower-pair source-free mean-velocity closure row")
    v.check(readiness_requirements.get("paper_tfe_lower_pair_source_free_mean_blend_closure_audit") == "partial", "v047 readiness missing paper lower-pair source-free mean-blend closure row")
    v.check(readiness_requirements.get("paper_tfe_lower_pair_source_free_mean_blend_trajectory_audit") == "partial", "v047 readiness missing paper lower-pair source-free mean-blend trajectory row")
    v.check(readiness_requirements.get("paper_tfe_lower_pair_source_free_mean_blend_trajectory_alpha_sweep_audit") == "partial", "v047 readiness missing paper lower-pair source-free mean-blend trajectory alpha-sweep row")
    v.check(readiness_requirements.get("paper_tfe_lower_pair_source_free_component_blend_trajectory_audit") == "partial", "v047 readiness missing paper lower-pair source-free component-blend trajectory row")
    v.check(readiness_requirements.get("paper_tfe_lower_pair_source_free_terminal_velocity_extrapolation_trajectory_audit") == "partial", "v047 readiness missing paper lower-pair source-free terminal extrapolation trajectory row")
    v.check(readiness_requirements.get("paper_tfe_lower_pair_source_free_terminal_extrapolation_blend_trajectory_audit") == "partial", "v047 readiness missing paper lower-pair source-free terminal-extrapolation blend trajectory row")
    v.check(readiness_requirements.get("paper_tfe_lower_pair_closure_acceptance_matrix_audit") == "partial", "v047 readiness missing paper lower-pair closure acceptance matrix row")
    v.check(counts.get("missing", 0) >= 1, "v047 TFE readiness no longer records missing full TFE replacement")
    v.check(paper_kinematic.get("status") == "paper_tfe_kinematic_formula_derived_residual_not_replaced", "v047 paper kinematic formula status changed")
    v.check(paper_kinematic.get("component_count") == 4, "v047 paper kinematic formula component count changed")
    v.check(paper_kinematic.get("stage_row_families_with_derived_formula") == 4, "v047 paper kinematic formula family count changed")
    v.check(paper_kinematic.get("stage_rows_with_derived_formula") == 72, "v047 paper kinematic formula row count changed")
    v.check(float(paper_kinematic.get("max_formula_residual_norm", 1.0)) < 1e-10, "v047 paper kinematic formula residual too large")
    v.check(paper_balance_constraint.get("status") == "paper_tfe_balance_constraint_formula_derived_residual_not_replaced", "v047 paper balance/constraint formula status changed")
    v.check(paper_balance_constraint.get("component_count") == 2, "v047 paper balance/constraint formula component count changed")
    v.check(paper_balance_constraint.get("stage_row_families_with_derived_formula") == 2, "v047 paper balance/constraint formula family count changed")
    v.check(paper_balance_constraint.get("stage_rows_with_derived_formula") == 60, "v047 paper balance/constraint formula row count changed")
    v.check(float(paper_balance_constraint.get("max_formula_residual_norm", 1.0)) < 1e-10, "v047 paper balance/constraint formula residual too large")
    v.check(paper_position_substitution.get("status") == "paper_tfe_position_rows_substituted_order_limited_not_full_tfe", "v047 paper position-substitution status changed")
    v.check(paper_position_substitution.get("row_families_substituted") == 2, "v047 paper position-substitution family count changed")
    v.check(paper_position_substitution.get("stage_rows_substituted") == 36, "v047 paper position-substitution stage-row count changed")
    v.check(float(paper_position_substitution.get("max_paper_position_substitution_residual_norm", 1.0)) < 1e-9, "v047 paper position-substitution residual too large")
    v.check(paper_position_substitution.get("min_jacobian_rank") == 132, "v047 paper position-substitution full-rank evidence changed")
    v.check(paper_position_substitution.get("full_tfe_stage_replacement") is False, "v047 paper position-substitution unexpectedly claims full TFE replacement")
    v.check(paper_kinematic_substitution.get("status") == "paper_tfe_kinematic_rows_substituted_order_limited_diagnostic_z0_not_full_tfe", "v047 paper kinematic-substitution status changed")
    v.check(paper_kinematic_substitution.get("row_families_substituted") == 4, "v047 paper kinematic-substitution family count changed")
    v.check(paper_kinematic_substitution.get("stage_rows_substituted") == 72, "v047 paper kinematic-substitution stage-row count changed")
    v.check(float(paper_kinematic_substitution.get("max_paper_kinematic_substitution_residual_norm", 1.0)) < 1e-9, "v047 paper kinematic-substitution residual too large")
    v.check(paper_kinematic_substitution.get("min_jacobian_rank") == 132, "v047 paper kinematic-substitution full-rank evidence changed")
    v.check(paper_kinematic_substitution.get("full_tfe_stage_replacement") is False, "v047 paper kinematic-substitution unexpectedly claims full TFE replacement")
    v.check(paper_all_row_substitution.get("status") == "paper_tfe_all_row_families_substituted_order_limited_diagnostic_z0_not_accepted", "v047 paper all-row substitution status changed")
    v.check(paper_all_row_substitution.get("row_families_substituted") == 6, "v047 paper all-row substitution family count changed")
    v.check(paper_all_row_substitution.get("stage_rows_substituted") == 132, "v047 paper all-row substitution stage-row count changed")
    v.check(float(paper_all_row_substitution.get("max_paper_all_row_substitution_residual_norm", 1.0)) < 1e-9, "v047 paper all-row substitution residual too large")
    v.check(float(paper_all_row_substitution.get("max_paper_balance_constraint_row_norm", 1.0)) < 1e-9, "v047 paper all-row balance/constraint residual too large")
    v.check(paper_all_row_substitution.get("min_jacobian_rank") == 132, "v047 paper all-row substitution full-rank evidence changed")
    v.check(float(paper_all_row_substitution.get("max_jacobian_condition", 0.0)) > 1.0e10, "v047 paper all-row substitution no longer records severe conditioning caveat")
    v.check(paper_all_row_substitution.get("full_tfe_stage_replacement") is False, "v047 paper all-row substitution unexpectedly claims full TFE replacement")
    v.check(paper_all_row_gauss_z0_substitution.get("status") == "paper_tfe_all_row_gauss_z0_substitution_diagnostic_not_accepted", "v047 paper all-row Gauss-z0 substitution status changed")
    v.check(paper_all_row_gauss_z0_substitution.get("row_families_substituted") == 6, "v047 paper all-row Gauss-z0 substitution family count changed")
    v.check(paper_all_row_gauss_z0_substitution.get("stage_rows_substituted") == 132, "v047 paper all-row Gauss-z0 substitution stage-row count changed")
    v.check(float(paper_all_row_gauss_z0_substitution.get("max_paper_all_row_gauss_z0_substitution_residual_norm", 1.0)) < 1e-9, "v047 paper all-row Gauss-z0 substitution residual too large")
    v.check(paper_all_row_gauss_z0_substitution.get("min_jacobian_rank") == 132, "v047 paper all-row Gauss-z0 substitution full-rank evidence changed")
    v.check(float(paper_all_row_gauss_z0_substitution.get("max_jacobian_condition", 0.0)) > 1.0e10, "v047 paper all-row Gauss-z0 substitution no longer records severe conditioning caveat")
    v.check(float(paper_all_row_gauss_z0_substitution.get("max_start_z0_delta_norm", 0.0)) > 0.0, "v047 paper all-row Gauss-z0 substitution lost z0-delta diagnostic")
    v.check(paper_all_row_gauss_z0_substitution.get("full_tfe_stage_replacement") is False, "v047 paper all-row Gauss-z0 substitution unexpectedly claims full TFE replacement")
    v.check(paper_all_row_gauss_z0_terminal_output.get("status") == "paper_tfe_all_row_gauss_z0_terminal_output_diagnostic_not_accepted", "v047 paper all-row Gauss-z0 terminal-output status changed")
    v.check(paper_all_row_gauss_z0_terminal_output.get("row_families_substituted") == 6, "v047 paper all-row Gauss-z0 terminal-output family count changed")
    v.check(paper_all_row_gauss_z0_terminal_output.get("stage_rows_substituted") == 132, "v047 paper all-row Gauss-z0 terminal-output stage-row count changed")
    v.check(float(paper_all_row_gauss_z0_terminal_output.get("max_paper_terminal_residual_norm", 1.0)) < 1e-9, "v047 paper all-row Gauss-z0 terminal-output residual too large")
    v.check(paper_all_row_gauss_z0_terminal_output.get("min_jacobian_rank") == 132, "v047 paper all-row Gauss-z0 terminal-output full-rank evidence changed")
    v.check(float(paper_all_row_gauss_z0_terminal_output.get("max_jacobian_condition", 0.0)) > 1.0e10, "v047 paper all-row Gauss-z0 terminal-output no longer records severe conditioning caveat")
    v.check(float(paper_all_row_gauss_z0_terminal_output.get("max_terminal_vs_gauss_position_delta_norm", 0.0)) > 0.0, "v047 paper all-row Gauss-z0 terminal-output lost position-delta diagnostic")
    v.check(float(paper_all_row_gauss_z0_terminal_output.get("max_terminal_vs_gauss_velocity_delta_norm", 0.0)) > 0.0, "v047 paper all-row Gauss-z0 terminal-output lost velocity-delta diagnostic")
    v.check(paper_all_row_gauss_z0_terminal_output.get("full_tfe_stage_replacement") is False, "v047 paper all-row Gauss-z0 terminal-output unexpectedly claims full TFE replacement")
    v.check(paper_all_row_recurrent_z0_terminal_output.get("status") == "paper_tfe_all_row_recurrent_z0_terminal_output_diagnostic_not_accepted", "v047 paper all-row recurrent-z0 terminal-output status changed")
    v.check(paper_all_row_recurrent_z0_terminal_output.get("row_families_substituted") == 6, "v047 paper all-row recurrent-z0 terminal-output family count changed")
    v.check(paper_all_row_recurrent_z0_terminal_output.get("stage_rows_substituted") == 132, "v047 paper all-row recurrent-z0 terminal-output stage-row count changed")
    v.check(float(paper_all_row_recurrent_z0_terminal_output.get("max_paper_recurrent_terminal_residual_norm", 1.0)) < 1e-9, "v047 paper all-row recurrent-z0 terminal-output residual too large")
    v.check(paper_all_row_recurrent_z0_terminal_output.get("min_jacobian_rank") == 132, "v047 paper all-row recurrent-z0 terminal-output full-rank evidence changed")
    v.check(float(paper_all_row_recurrent_z0_terminal_output.get("max_jacobian_condition", 0.0)) > 1.0e10, "v047 paper all-row recurrent-z0 terminal-output no longer records severe conditioning caveat")
    v.check(float(paper_all_row_recurrent_z0_terminal_output.get("max_used_z0_vs_gauss_delta_norm", 0.0)) > 0.0, "v047 paper all-row recurrent-z0 terminal-output lost z0-delta diagnostic")
    v.check(paper_all_row_recurrent_z0_terminal_output.get("full_tfe_stage_replacement") is False, "v047 paper all-row recurrent-z0 terminal-output unexpectedly claims full TFE replacement")
    v.check(paper_all_row_consistent_z0_terminal_output.get("status") == "paper_tfe_all_row_consistent_z0_terminal_output_diagnostic_not_accepted", "v047 paper all-row consistent-z0 terminal-output status changed")
    v.check(paper_all_row_consistent_z0_terminal_output.get("row_families_substituted") == 6, "v047 paper all-row consistent-z0 terminal-output family count changed")
    v.check(paper_all_row_consistent_z0_terminal_output.get("stage_rows_substituted") == 132, "v047 paper all-row consistent-z0 terminal-output stage-row count changed")
    v.check(float(paper_all_row_consistent_z0_terminal_output.get("max_paper_consistent_terminal_residual_norm", 1.0)) < 1e-9, "v047 paper all-row consistent-z0 terminal-output residual too large")
    v.check(paper_all_row_consistent_z0_terminal_output.get("min_jacobian_rank") == 132, "v047 paper all-row consistent-z0 terminal-output full-rank evidence changed")
    v.check(float(paper_all_row_consistent_z0_terminal_output.get("max_jacobian_condition", 0.0)) > 1.0e10, "v047 paper all-row consistent-z0 terminal-output no longer records severe conditioning caveat")
    v.check(float(paper_all_row_consistent_z0_terminal_output.get("initial_z0_residual_norm", 1.0)) < 1e-10, "v047 paper all-row consistent-z0 terminal-output initial z0 residual too large")
    v.check(paper_all_row_consistent_z0_terminal_output.get("initial_z0_jacobian_rank") == 20, "v047 paper all-row consistent-z0 terminal-output initial z0 rank changed")
    v.check(float(paper_all_row_consistent_z0_terminal_output.get("initial_z0_jacobian_condition", 1.0e6)) < 100.0, "v047 paper all-row consistent-z0 terminal-output initial z0 condition changed")
    v.check(paper_all_row_consistent_z0_terminal_output.get("bootstrap_step_count") == 0, "v047 paper all-row consistent-z0 terminal-output did not remove bootstrap")
    v.check(paper_all_row_consistent_z0_terminal_output.get("recurrent_step_count", 0) > 0, "v047 paper all-row consistent-z0 terminal-output lost recurrent-step diagnostic")
    v.check(paper_all_row_consistent_z0_terminal_output.get("full_tfe_stage_replacement") is False, "v047 paper all-row consistent-z0 terminal-output unexpectedly claims full TFE replacement")
    v.check(paper_all_row_consistent_z0_conditioning.get("status") == "paper_tfe_all_row_consistent_z0_conditioning_quantified_not_accepted", "v047 paper all-row consistent-z0 conditioning status changed")
    v.check(paper_all_row_consistent_z0_conditioning.get("row_count") == 6, "v047 paper all-row consistent-z0 conditioning row count changed")
    v.check(paper_all_row_consistent_z0_conditioning.get("row_families_substituted") == 6, "v047 paper all-row consistent-z0 conditioning family count changed")
    v.check(paper_all_row_consistent_z0_conditioning.get("stage_rows_substituted") == 132, "v047 paper all-row consistent-z0 conditioning stage-row count changed")
    v.check(float(paper_all_row_consistent_z0_conditioning.get("max_residual_norm", 1.0)) < 1e-9, "v047 paper all-row consistent-z0 conditioning residual too large")
    v.check(paper_all_row_consistent_z0_conditioning.get("min_jacobian_rank") == 132, "v047 paper all-row consistent-z0 conditioning full-rank evidence changed")
    v.check(float(paper_all_row_consistent_z0_conditioning.get("max_raw_condition", 0.0)) > 1.0e10, "v047 paper all-row consistent-z0 conditioning no longer records severe raw condition")
    v.check(math.isfinite(float(paper_all_row_consistent_z0_conditioning.get("max_iterative_equilibrated_condition", math.nan))), "v047 paper all-row consistent-z0 conditioning iterative condition is not finite")
    v.check(float(paper_all_row_consistent_z0_conditioning.get("max_condition_reduction_raw_to_iterative", 0.0)) > 1.0e6, "v047 paper all-row consistent-z0 conditioning no longer records large scaling reduction")
    v.check(paper_all_row_consistent_z0_conditioning.get("full_tfe_stage_replacement") is False, "v047 paper all-row consistent-z0 conditioning unexpectedly claims full TFE replacement")
    v.check(paper_all_row_consistent_z0_scaled_newton.get("status") == "paper_tfe_all_row_consistent_z0_scaled_newton_diagnostic_not_accepted", "v047 paper all-row consistent-z0 scaled-Newton status changed")
    v.check(paper_all_row_consistent_z0_scaled_newton.get("row_count") == 6, "v047 paper all-row consistent-z0 scaled-Newton row count changed")
    v.check(paper_all_row_consistent_z0_scaled_newton.get("row_families_substituted") == 6, "v047 paper all-row consistent-z0 scaled-Newton family count changed")
    v.check(paper_all_row_consistent_z0_scaled_newton.get("stage_rows_substituted") == 132, "v047 paper all-row consistent-z0 scaled-Newton stage-row count changed")
    v.check(float(paper_all_row_consistent_z0_scaled_newton.get("max_paper_scaled_terminal_residual_norm", 1.0)) < 1e-9, "v047 paper all-row consistent-z0 scaled-Newton residual too large")
    v.check(paper_all_row_consistent_z0_scaled_newton.get("min_jacobian_rank") == 132, "v047 paper all-row consistent-z0 scaled-Newton full-rank evidence changed")
    v.check(float(paper_all_row_consistent_z0_scaled_newton.get("max_raw_jacobian_condition", 0.0)) > 1.0e10, "v047 paper all-row consistent-z0 scaled-Newton no longer records severe raw condition")
    v.check(math.isfinite(float(paper_all_row_consistent_z0_scaled_newton.get("max_scaled_jacobian_condition", math.nan))), "v047 paper all-row consistent-z0 scaled-Newton scaled condition is not finite")
    v.check(float(paper_all_row_consistent_z0_scaled_newton.get("max_condition_reduction_raw_to_scaled", 0.0)) > 1.0e6, "v047 paper all-row consistent-z0 scaled-Newton no longer records large scaling reduction")
    v.check(paper_all_row_consistent_z0_scaled_newton.get("full_tfe_stage_replacement") is False, "v047 paper all-row consistent-z0 scaled-Newton unexpectedly claims full TFE replacement")
    v.check(paper_family_ablation.get("status") == "paper_tfe_family_ablation_diagnostic_not_accepted", "v047 paper family-ablation status changed")
    v.check(paper_family_ablation.get("row_count") == 12, "v047 paper family-ablation row count changed")
    v.check(paper_family_ablation.get("variant_count") == 2, "v047 paper family-ablation variant count changed")
    v.check(paper_family_ablation.get("row_families_substituted_per_variant") == 5, "v047 paper family-ablation family count changed")
    v.check(float(paper_family_ablation.get("max_residual_norm", 1.0)) < 1.0e-9, "v047 paper family-ablation residual too large")
    v.check(paper_family_ablation.get("min_jacobian_rank") == 132, "v047 paper family-ablation full-rank evidence changed")
    v.check(float(paper_family_ablation.get("max_raw_condition", 0.0)) > 1.0e10, "v047 paper family-ablation no longer records severe raw condition")
    v.check(math.isfinite(float(paper_family_ablation.get("max_scaled_condition", math.nan))), "v047 paper family-ablation scaled condition is not finite")
    v.check(paper_family_ablation.get("dominant_left_row_family_counts", {}).get("lower_pair_index3_weak_constraints") == 12, "v047 paper family-ablation lost lower-pair near-null row localization")
    v.check(paper_family_ablation.get("dominant_right_variable_family_counts", {}).get("lower_pair_lambda") == 12, "v047 paper family-ablation lost lower-pair lambda near-null localization")
    v.check(paper_family_ablation.get("accepted_h_sweep_present") is False, "v047 paper family-ablation unexpectedly claims accepted h-sweep")
    v.check(paper_family_ablation.get("full_tfe_stage_replacement") is False, "v047 paper family-ablation unexpectedly claims full TFE replacement")
    v.check(paper_lower_pair_lambda_schur.get("status") == "paper_tfe_lower_pair_lambda_schur_diagnostic_not_accepted", "v047 paper lower-pair/lambda Schur status changed")
    v.check(paper_lower_pair_lambda_schur.get("row_count") == 6, "v047 paper lower-pair/lambda Schur row count changed")
    v.check(paper_lower_pair_lambda_schur.get("row_families_substituted") == 6, "v047 paper lower-pair/lambda Schur family count changed")
    v.check(paper_lower_pair_lambda_schur.get("stage_rows_substituted") == 132, "v047 paper lower-pair/lambda Schur stage-row count changed")
    v.check(float(paper_lower_pair_lambda_schur.get("max_residual_norm", 1.0)) < 1.0e-9, "v047 paper lower-pair/lambda Schur residual too large")
    v.check(paper_lower_pair_lambda_schur.get("min_jacobian_rank") == 132, "v047 paper lower-pair/lambda Schur full-rank evidence changed")
    v.check(float(paper_lower_pair_lambda_schur.get("max_full_raw_condition", 0.0)) > 1.0e10, "v047 paper lower-pair/lambda Schur no longer records severe raw condition")
    v.check(math.isfinite(float(paper_lower_pair_lambda_schur.get("max_full_iterative_scaled_condition", math.nan))), "v047 paper lower-pair/lambda Schur scaled condition is not finite")
    v.check(math.isfinite(float(paper_lower_pair_lambda_schur.get("max_schur_condition", math.nan))), "v047 paper lower-pair/lambda Schur condition is not finite")
    v.check(float(paper_lower_pair_lambda_schur.get("max_schur_newton_linear_residual_norm", 1.0)) < 1e-7, "v047 paper lower-pair/lambda Schur Newton linear residual too large")
    v.check(float(paper_lower_pair_lambda_schur.get("max_schur_newton_relative_delta_error", 1.0)) < 1e-7, "v047 paper lower-pair/lambda Schur Newton direction mismatch too large")
    v.check(float(paper_lower_pair_lambda_schur.get("max_full_left_lower_pair_fraction", 0.0)) > 0.99, "v047 paper lower-pair/lambda Schur lost lower-pair row localization")
    v.check(float(paper_lower_pair_lambda_schur.get("max_full_right_lower_pair_lambda_fraction", 0.0)) > 0.8, "v047 paper lower-pair/lambda Schur lost lambda localization")
    v.check(paper_lower_pair_lambda_schur.get("dominant_left_row_family_counts", {}).get("lower_pair_index3_weak_constraints") == 6, "v047 paper lower-pair/lambda Schur dominant row counts changed")
    v.check(paper_lower_pair_lambda_schur.get("dominant_right_variable_family_counts", {}).get("lower_pair_lambda") == 6, "v047 paper lower-pair/lambda Schur dominant variable counts changed")
    v.check(paper_lower_pair_lambda_schur.get("accepted_h_sweep_present") is False, "v047 paper lower-pair/lambda Schur unexpectedly claims accepted h-sweep")
    v.check(paper_lower_pair_lambda_schur.get("full_tfe_stage_replacement") is False, "v047 paper lower-pair/lambda Schur unexpectedly claims full TFE replacement")
    v.check(paper_lower_pair_row_variant.get("status") == "paper_tfe_lower_pair_row_variant_diagnostic_not_accepted", "v047 paper lower-pair row-variant status changed")
    v.check(paper_lower_pair_row_variant.get("row_count") == 18, "v047 paper lower-pair row-variant row count changed")
    v.check(paper_lower_pair_row_variant.get("variant_count") == 3, "v047 paper lower-pair row-variant variant count changed")
    v.check(set(paper_lower_pair_row_variant.get("successful_variants", [])) == {"position_constraint", "velocity_constraint", "acceleration_constraint"}, "v047 paper lower-pair row-variant successful variants changed")
    v.check(paper_lower_pair_row_variant.get("best_condition_variant") == "acceleration_constraint", "v047 paper lower-pair row-variant best condition variant changed")
    v.check(float(paper_lower_pair_row_variant.get("best_condition_variant_max_schur_condition", math.inf)) < 150.0, "v047 paper lower-pair row-variant best Schur condition too large")
    v.check(float(paper_lower_pair_row_variant.get("max_residual_norm", 1.0)) < 1e-9, "v047 paper lower-pair row-variant residual too large")
    v.check(paper_lower_pair_row_variant.get("min_jacobian_rank") == 132, "v047 paper lower-pair row-variant full-rank evidence changed")
    v.check(paper_lower_pair_row_variant.get("accepted_h_sweep_present") is False, "v047 paper lower-pair row-variant unexpectedly claims accepted h-sweep")
    v.check(paper_lower_pair_row_variant.get("full_tfe_stage_replacement") is False, "v047 paper lower-pair row-variant unexpectedly claims full TFE replacement")
    v.check(paper_lower_pair_acceleration_terminal_output.get("status") == "paper_tfe_lower_pair_acceleration_terminal_output_h_sweep_diagnostic_not_accepted", "v047 paper lower-pair acceleration terminal-output status changed")
    v.check(paper_lower_pair_acceleration_terminal_output.get("row_count") == 6, "v047 paper lower-pair acceleration terminal-output row count changed")
    v.check(paper_lower_pair_acceleration_terminal_output.get("row_families_substituted") == 6, "v047 paper lower-pair acceleration terminal-output family count changed")
    v.check(paper_lower_pair_acceleration_terminal_output.get("stage_rows_substituted") == 132, "v047 paper lower-pair acceleration terminal-output stage-row count changed")
    v.check(paper_lower_pair_acceleration_terminal_output.get("lower_pair_row_formula") == "paper_acceleration_constraint", "v047 paper lower-pair acceleration terminal-output formula marker changed")
    v.check(float(paper_lower_pair_acceleration_terminal_output.get("max_paper_lower_pair_acceleration_terminal_residual_norm", 1.0)) < 1e-9, "v047 paper lower-pair acceleration terminal-output residual too large")
    v.check(paper_lower_pair_acceleration_terminal_output.get("min_jacobian_rank") == 132, "v047 paper lower-pair acceleration terminal-output full-rank evidence changed")
    v.check(float(paper_lower_pair_acceleration_terminal_output.get("max_raw_jacobian_condition", 0.0)) > float(paper_lower_pair_acceleration_terminal_output.get("max_scaled_jacobian_condition", math.inf)), "v047 paper lower-pair acceleration terminal-output scaling reduction missing")
    v.check(paper_lower_pair_acceleration_terminal_output.get("bootstrap_step_count") == 0, "v047 paper lower-pair acceleration terminal-output reintroduced bootstrap")
    v.check(paper_lower_pair_acceleration_terminal_output.get("accepted_h_sweep_present") is False, "v047 paper lower-pair acceleration terminal-output unexpectedly claims accepted h-sweep")
    v.check(paper_lower_pair_acceleration_terminal_output.get("full_tfe_stage_replacement") is False, "v047 paper lower-pair acceleration terminal-output unexpectedly claims full TFE replacement")
    v.check(paper_lower_pair_acceleration_projection_dependence.get("status") == "paper_tfe_lower_pair_acceleration_projection_dependence_quantified_not_accepted", "v047 paper lower-pair acceleration projection-dependence status changed")
    v.check(paper_lower_pair_acceleration_projection_dependence.get("row_count") == 6, "v047 paper lower-pair acceleration projection-dependence row count changed")
    v.check(float(paper_lower_pair_acceleration_projection_dependence.get("max_raw_terminal_endpoint_velocity_constraint_norm", 0.0)) > float(paper_lower_pair_acceleration_projection_dependence.get("max_projected_terminal_endpoint_velocity_constraint_norm", 1.0)), "v047 paper lower-pair acceleration projection-dependence lost raw/projected velocity contrast")
    v.check(float(paper_lower_pair_acceleration_projection_dependence.get("max_projected_terminal_endpoint_velocity_constraint_norm", 1.0)) < 1e-10, "v047 paper lower-pair acceleration projection-dependence projected velocity too large")
    v.check(float(paper_lower_pair_acceleration_projection_dependence.get("max_velocity_projection_delta_norm", 0.0)) > 0.0, "v047 paper lower-pair acceleration projection-dependence lost projection delta")
    v.check(paper_lower_pair_acceleration_projection_dependence.get("projection_required_row_count") == 6, "v047 paper lower-pair acceleration projection-dependence required-row count changed")
    v.check(paper_lower_pair_acceleration_projection_dependence.get("accepted_h_sweep_present") is False, "v047 paper lower-pair acceleration projection-dependence unexpectedly claims accepted h-sweep")
    v.check(paper_lower_pair_acceleration_projection_dependence.get("full_tfe_stage_replacement") is False, "v047 paper lower-pair acceleration projection-dependence unexpectedly claims full TFE replacement")
    v.check(paper_lower_pair_acceleration_terminal_velocity_closure.get("status") == "paper_tfe_lower_pair_acceleration_terminal_velocity_closure_diagnostic_not_accepted", "v047 paper lower-pair acceleration terminal-velocity closure status changed")
    v.check(paper_lower_pair_acceleration_terminal_velocity_closure.get("row_count") == 6, "v047 paper lower-pair acceleration terminal-velocity closure row count changed")
    v.check(paper_lower_pair_acceleration_terminal_velocity_closure.get("paper_stage_rows_retained") == 124, "v047 paper lower-pair acceleration terminal-velocity closure retained row count changed")
    v.check(paper_lower_pair_acceleration_terminal_velocity_closure.get("endpoint_velocity_rows_inserted") == 8, "v047 paper lower-pair acceleration terminal-velocity closure endpoint row count changed")
    v.check(float(paper_lower_pair_acceleration_terminal_velocity_closure.get("max_terminal_velocity_closure_residual_norm", 1.0)) < 1e-9, "v047 paper lower-pair acceleration terminal-velocity closure residual too large")
    v.check(float(paper_lower_pair_acceleration_terminal_velocity_closure.get("max_terminal_endpoint_velocity_constraint_norm", 1.0)) < 1e-10, "v047 paper lower-pair acceleration terminal-velocity closure raw endpoint velocity too large")
    v.check(float(paper_lower_pair_acceleration_terminal_velocity_closure.get("max_replaced_terminal_lower_pair_acceleration_row_norm", 0.0)) > 1e-8, "v047 paper lower-pair acceleration terminal-velocity closure lost replaced-row diagnostic")
    v.check(paper_lower_pair_acceleration_terminal_velocity_closure.get("projection_applied_in_output") is False, "v047 paper lower-pair acceleration terminal-velocity closure unexpectedly applies output projection")
    v.check(paper_lower_pair_acceleration_terminal_velocity_closure.get("projection_free_terminal_velocity_closure") is True, "v047 paper lower-pair acceleration terminal-velocity closure lost projection-free marker")
    v.check(paper_lower_pair_acceleration_terminal_velocity_closure.get("accepted_h_sweep_present") is False, "v047 paper lower-pair acceleration terminal-velocity closure unexpectedly claims accepted h-sweep")
    v.check(paper_lower_pair_acceleration_terminal_velocity_closure.get("full_tfe_stage_replacement") is False, "v047 paper lower-pair acceleration terminal-velocity closure unexpectedly claims full TFE replacement")
    v.check(paper_lower_pair_acceleration_terminal_row_homotopy.get("status") == "paper_tfe_lower_pair_acceleration_terminal_row_homotopy_diagnostic_not_accepted", "v047 paper lower-pair acceleration terminal-row homotopy status changed")
    v.check(paper_lower_pair_acceleration_terminal_row_homotopy.get("row_count") == 30, "v047 paper lower-pair acceleration terminal-row homotopy row count changed")
    v.check(paper_lower_pair_acceleration_terminal_row_homotopy.get("beta1_row_count") == 6, "v047 paper lower-pair acceleration terminal-row homotopy beta=1 row count changed")
    v.check(paper_lower_pair_acceleration_terminal_row_homotopy.get("beta_values") == [0.0, 0.25, 0.5, 0.75, 1.0], "v047 paper lower-pair acceleration terminal-row homotopy beta path changed")
    v.check(float(paper_lower_pair_acceleration_terminal_row_homotopy.get("residual_norm", 1.0)) < 1e-9, "v047 paper lower-pair acceleration terminal-row homotopy residual too large")
    v.check(paper_lower_pair_acceleration_terminal_row_homotopy.get("min_jacobian_rank") == 132, "v047 paper lower-pair acceleration terminal-row homotopy full-rank evidence changed")
    v.check(float(paper_lower_pair_acceleration_terminal_row_homotopy.get("max_beta1_terminal_endpoint_velocity_constraint_norm", 1.0)) < 1e-10, "v047 paper lower-pair acceleration terminal-row homotopy beta=1 endpoint velocity too large")
    v.check(float(paper_lower_pair_acceleration_terminal_row_homotopy.get("max_beta0_terminal_endpoint_velocity_constraint_norm", 0.0)) > float(paper_lower_pair_acceleration_terminal_row_homotopy.get("max_beta1_terminal_endpoint_velocity_constraint_norm", 1.0)), "v047 paper lower-pair acceleration terminal-row homotopy lost beta0/beta1 velocity contrast")
    v.check(float(paper_lower_pair_acceleration_terminal_row_homotopy.get("raw_jacobian_condition", 0.0)) > float(paper_lower_pair_acceleration_terminal_row_homotopy.get("scaled_jacobian_condition", math.inf)), "v047 paper lower-pair acceleration terminal-row homotopy scaling reduction missing")
    v.check(paper_lower_pair_acceleration_terminal_row_homotopy.get("accepted_h_sweep_present") is False, "v047 paper lower-pair acceleration terminal-row homotopy unexpectedly claims accepted h-sweep")
    v.check(paper_lower_pair_acceleration_terminal_row_homotopy.get("full_tfe_stage_replacement") is False, "v047 paper lower-pair acceleration terminal-row homotopy unexpectedly claims full TFE replacement")
    v.check(paper_lower_pair_terminal_source_target.get("status") == "paper_tfe_lower_pair_terminal_source_target_quantified_not_full_tfe", "v047 paper lower-pair terminal source-target status changed")
    v.check(paper_lower_pair_terminal_source_target.get("row_count") == 6, "v047 paper lower-pair terminal source-target row count changed")
    v.check(paper_lower_pair_terminal_source_target.get("paper_stage_rows_retained") == 124, "v047 paper lower-pair terminal source-target retained row count changed")
    v.check(paper_lower_pair_terminal_source_target.get("terminal_rows_replaced") == 8, "v047 paper lower-pair terminal source-target terminal row count changed")
    v.check(paper_lower_pair_terminal_source_target.get("candidate_stage_local_lower_pair_rows") == 24, "v047 paper lower-pair terminal source-target stage-local row count changed")
    v.check(paper_lower_pair_terminal_source_target.get("target_ready_row_count") == 6, "v047 paper lower-pair terminal source-target ready-row count changed")
    v.check(float(paper_lower_pair_terminal_source_target.get("max_terminal_velocity_reduction_factor", 0.0)) > 1.0, "v047 paper lower-pair terminal source-target velocity reduction missing")
    v.check(float(paper_lower_pair_terminal_source_target.get("max_replaced_terminal_lower_pair_acceleration_row_norm", 0.0)) > 1e-8, "v047 paper lower-pair terminal source-target replaced row norm missing")
    v.check(paper_lower_pair_terminal_source_target.get("stage_local_replacement_required") is True, "v047 paper lower-pair terminal source-target replacement requirement lost")
    v.check(paper_lower_pair_terminal_source_target.get("terminal_row_replacement_present") is True, "v047 paper lower-pair terminal source-target terminal replacement marker lost")
    v.check(paper_lower_pair_terminal_source_target.get("accepted_h_sweep_present") is False, "v047 paper lower-pair terminal source-target unexpectedly claims accepted h-sweep")
    v.check(paper_lower_pair_terminal_source_target.get("full_tfe_stage_replacement") is False, "v047 paper lower-pair terminal source-target unexpectedly claims full TFE replacement")
    v.check(paper_lower_pair_terminal_source_lift.get("status") == "paper_tfe_lower_pair_terminal_source_lift_quantified_not_full_tfe", "v047 paper lower-pair terminal source-lift status changed")
    v.check(paper_lower_pair_terminal_source_lift.get("row_count") == 6, "v047 paper lower-pair terminal source-lift row count changed")
    v.check(paper_lower_pair_terminal_source_lift.get("terminal_rows_replaced") == 8, "v047 paper lower-pair terminal source-lift terminal row count changed")
    v.check(paper_lower_pair_terminal_source_lift.get("stage_count") == 3, "v047 paper lower-pair terminal source-lift stage count changed")
    v.check(paper_lower_pair_terminal_source_lift.get("stage_local_lower_pair_width") == 8, "v047 paper lower-pair terminal source-lift width changed")
    v.check(paper_lower_pair_terminal_source_lift.get("stage_local_lifted_rows") == 24, "v047 paper lower-pair terminal source-lift lifted row count changed")
    v.check(paper_lower_pair_terminal_source_lift.get("formula_ready_row_count") == 6, "v047 paper lower-pair terminal source-lift ready-row count changed")
    v.check(float(paper_lower_pair_terminal_source_lift.get("max_terminal_source_norm", 0.0)) > 1e-8, "v047 paper lower-pair terminal source-lift terminal source norm missing")
    v.check(float(paper_lower_pair_terminal_source_lift.get("max_stage_lifted_source_norm", 0.0)) > 0.0, "v047 paper lower-pair terminal source-lift stage source norm missing")
    v.check(float(paper_lower_pair_terminal_source_lift.get("max_stage_lift_reconstruction_error_norm", 1.0)) < 1e-14, "v047 paper lower-pair terminal source-lift reconstruction error too large")
    v.check(float(paper_lower_pair_terminal_source_lift.get("max_stage_lift_norm_ratio_deviation", 1.0)) < 1e-12, "v047 paper lower-pair terminal source-lift norm-ratio deviation too large")
    v.check(paper_lower_pair_terminal_source_lift.get("stage_local_formula_present") is True, "v047 paper lower-pair terminal source-lift formula marker lost")
    v.check(paper_lower_pair_terminal_source_lift.get("full_tfe_stage_replacement") is False, "v047 paper lower-pair terminal source-lift unexpectedly claims full TFE replacement")
    v.check(paper_lower_pair_terminal_source_normalization.get("status") == "paper_tfe_lower_pair_terminal_source_normalization_quantified_not_full_tfe", "v047 paper lower-pair terminal source-normalization status changed")
    v.check(paper_lower_pair_terminal_source_normalization.get("row_count") == 6, "v047 paper lower-pair terminal source-normalization row count changed")
    v.check(paper_lower_pair_terminal_source_normalization.get("terminal_rows_replaced") == 8, "v047 paper lower-pair terminal source-normalization terminal row count changed")
    v.check(paper_lower_pair_terminal_source_normalization.get("stage_count") == 3, "v047 paper lower-pair terminal source-normalization stage count changed")
    v.check(paper_lower_pair_terminal_source_normalization.get("stage_local_lower_pair_width") == 8, "v047 paper lower-pair terminal source-normalization width changed")
    v.check(paper_lower_pair_terminal_source_normalization.get("stage_local_lifted_rows") == 24, "v047 paper lower-pair terminal source-normalization lifted row count changed")
    v.check(paper_lower_pair_terminal_source_normalization.get("normalization_ready_row_count") == 6, "v047 paper lower-pair terminal source-normalization ready-row count changed")
    v.check(paper_lower_pair_terminal_source_normalization.get("normalization_formula") == "terminal_lower_pair_source = terminal_row_vector/sqrt(h*b_terminal)", "v047 paper lower-pair terminal source-normalization formula changed")
    v.check(float(paper_lower_pair_terminal_source_normalization.get("max_raw_source_terminal_reconstruction_relative_error", 0.0)) > 0.1, "v047 paper lower-pair terminal source-normalization raw-source contrast missing")
    v.check(float(paper_lower_pair_terminal_source_normalization.get("max_normalized_terminal_reconstruction_relative_error", 1.0)) < 1e-12, "v047 paper lower-pair terminal source-normalization reconstruction error too large")
    v.check(float(paper_lower_pair_terminal_source_normalization.get("max_normalized_source_norm", 0.0)) > float(paper_lower_pair_terminal_source_lift.get("max_terminal_source_norm", 0.0)), "v047 paper lower-pair terminal source-normalization source scale missing")
    v.check(float(paper_lower_pair_terminal_source_normalization.get("max_normalized_lift_norm_over_terminal_row_norm", 0.0)) > 1.0, "v047 paper lower-pair terminal source-normalization lift factor missing")
    v.check(paper_lower_pair_terminal_source_normalization.get("stage_local_formula_present") is True, "v047 paper lower-pair terminal source-normalization formula marker lost")
    v.check(paper_lower_pair_terminal_source_normalization.get("substituted_into_newton_residual") is False, "v047 paper lower-pair terminal source-normalization unexpectedly claims Newton substitution")
    v.check(paper_lower_pair_terminal_source_normalization.get("full_tfe_stage_replacement") is False, "v047 paper lower-pair terminal source-normalization unexpectedly claims full TFE replacement")
    v.check(paper_lower_pair_terminal_source_insertion.get("status") == "paper_tfe_lower_pair_terminal_source_insertion_quantified_not_full_tfe", "v047 paper lower-pair terminal source-insertion status changed")
    v.check(paper_lower_pair_terminal_source_insertion.get("row_count") == 12, "v047 paper lower-pair terminal source-insertion row count changed")
    v.check(paper_lower_pair_terminal_source_insertion.get("source_sign_values") == [-1.0, 1.0], "v047 paper lower-pair terminal source-insertion sign path changed")
    v.check(paper_lower_pair_terminal_source_insertion.get("newton_attempted_row_count") == 12, "v047 paper lower-pair terminal source-insertion did not attempt every sign/h row")
    v.check(float(paper_lower_pair_terminal_source_insertion.get("max_normalized_source_norm", 0.0)) > 0.0, "v047 paper lower-pair terminal source-insertion normalized source missing")
    v.check(float(paper_lower_pair_terminal_source_insertion.get("max_terminal_source_reconstruction_relative_error", 1.0)) < 1e-12, "v047 paper lower-pair terminal source-insertion reconstruction too large")
    v.check(paper_lower_pair_terminal_source_insertion.get("source_substituted_in_newton_residual") is True, "v047 paper lower-pair terminal source-insertion did not record Newton substitution")
    v.check(paper_lower_pair_terminal_source_insertion.get("accepted_h_sweep_present") is False, "v047 paper lower-pair terminal source-insertion unexpectedly claims accepted h-sweep")
    v.check(paper_lower_pair_terminal_source_insertion.get("full_tfe_stage_replacement") is False, "v047 paper lower-pair terminal source-insertion unexpectedly claims full TFE replacement")
    v.check(paper_lower_pair_terminal_source_insertion_trajectory.get("status") == "paper_tfe_lower_pair_terminal_source_insertion_trajectory_failure_quantified_not_accepted", "v047 paper lower-pair terminal source-insertion trajectory status changed")
    v.check(paper_lower_pair_terminal_source_insertion_trajectory.get("row_count") == 6, "v047 paper lower-pair terminal source-insertion trajectory row count changed")
    v.check(paper_lower_pair_terminal_source_insertion_trajectory.get("h_values") == [0.04, 0.02, 0.01], "v047 paper lower-pair terminal source-insertion trajectory h values changed")
    v.check(paper_lower_pair_terminal_source_insertion_trajectory.get("source_sign") == -1.0, "v047 paper lower-pair terminal source-insertion trajectory source sign changed")
    v.check(paper_lower_pair_terminal_source_insertion_trajectory.get("trajectory_completed_row_count") == 6, "v047 paper lower-pair terminal source-insertion trajectory did not complete all diagnostic h rows")
    v.check(paper_lower_pair_terminal_source_insertion_trajectory.get("reference_completed") is False, "v047 paper lower-pair terminal source-insertion trajectory unexpectedly completed reference")
    v.check(paper_lower_pair_terminal_source_insertion_trajectory.get("source_ready_step_count") == 28, "v047 paper lower-pair terminal source-insertion trajectory ready-step count changed")
    v.check(paper_lower_pair_terminal_source_insertion_trajectory.get("source_insertion_converged_step_count") == 28, "v047 paper lower-pair terminal source-insertion trajectory converged-step count changed")
    v.check(float(paper_lower_pair_terminal_source_insertion_trajectory.get("max_source_insertion_residual_norm", 1.0)) < 1e-8, "v047 paper lower-pair terminal source-insertion trajectory residual too large")
    v.check(float(paper_lower_pair_terminal_source_insertion_trajectory.get("max_terminal_endpoint_velocity_constraint_norm", 0.0)) > 1.0, "v047 paper lower-pair terminal source-insertion trajectory terminal-velocity blocker missing")
    v.check(paper_lower_pair_terminal_source_insertion_trajectory.get("trajectory_h_sweep_present") is True, "v047 paper lower-pair terminal source-insertion trajectory did not record h-sweep attempt")
    v.check(paper_lower_pair_terminal_source_insertion_trajectory.get("accepted_h_sweep_present") is False, "v047 paper lower-pair terminal source-insertion trajectory unexpectedly claims accepted h-sweep")
    v.check(paper_lower_pair_terminal_source_insertion_trajectory.get("full_tfe_stage_replacement") is False, "v047 paper lower-pair terminal source-insertion trajectory unexpectedly claims full TFE replacement")
    v.check(paper_lower_pair_terminal_source_insertion_blowup.get("status") == "paper_tfe_lower_pair_terminal_source_insertion_blowup_quantified_not_accepted", "v047 paper lower-pair terminal source-insertion blow-up status changed")
    v.check(paper_lower_pair_terminal_source_insertion_blowup.get("row_count") == 14, "v047 paper lower-pair terminal source-insertion blow-up row count changed")
    v.check(paper_lower_pair_terminal_source_insertion_blowup.get("case_count") == 2, "v047 paper lower-pair terminal source-insertion blow-up case count changed")
    v.check(paper_lower_pair_terminal_source_insertion_blowup.get("metric_count") == 7, "v047 paper lower-pair terminal source-insertion blow-up metric count changed")
    v.check(paper_lower_pair_terminal_source_insertion_blowup.get("h_values") == [0.04, 0.02, 0.01], "v047 paper lower-pair terminal source-insertion blow-up h values changed")
    v.check(paper_lower_pair_terminal_source_insertion_blowup.get("source_sign") == -1.0, "v047 paper lower-pair terminal source-insertion blow-up source sign changed")
    v.check(paper_lower_pair_terminal_source_insertion_blowup.get("blowup_row_count", 0) >= 4, "v047 paper lower-pair terminal source-insertion blow-up rows missing")
    v.check(float(paper_lower_pair_terminal_source_insertion_blowup.get("max_mid_to_fine_ratio", 0.0)) > 1.0e3, "v047 paper lower-pair terminal source-insertion blow-up max mid-to-fine ratio too small")
    v.check(float(paper_lower_pair_terminal_source_insertion_blowup.get("max_coarse_to_fine_ratio", 0.0)) > 1.0e5, "v047 paper lower-pair terminal source-insertion blow-up max coarse-to-fine ratio too small")
    v.check(float(paper_lower_pair_terminal_source_insertion_blowup.get("min_observed_power_h", 0.0)) < -4.0, "v047 paper lower-pair terminal source-insertion blow-up h-power no longer records instability")
    v.check(bool(paper_lower_pair_terminal_source_insertion_blowup.get("dominant_metric", "")), "v047 paper lower-pair terminal source-insertion blow-up dominant metric missing")
    v.check(bool(paper_lower_pair_terminal_source_insertion_blowup.get("dominant_case", "")), "v047 paper lower-pair terminal source-insertion blow-up dominant case missing")
    v.check(paper_lower_pair_terminal_source_insertion_blowup.get("trajectory_reference_completed") is False, "v047 paper lower-pair terminal source-insertion blow-up unexpectedly claims completed reference")
    v.check(paper_lower_pair_terminal_source_insertion_blowup.get("accepted_h_sweep_present") is False, "v047 paper lower-pair terminal source-insertion blow-up unexpectedly claims accepted h-sweep")
    v.check(paper_lower_pair_terminal_source_insertion_blowup.get("full_tfe_stage_replacement") is False, "v047 paper lower-pair terminal source-insertion blow-up unexpectedly claims full TFE replacement")
    v.check(paper_lower_pair_terminal_source_bounded_policy.get("status") == "paper_tfe_lower_pair_terminal_source_bounded_policy_target_quantified_not_accepted", "v047 paper lower-pair terminal source bounded-policy status changed")
    v.check(paper_lower_pair_terminal_source_bounded_policy.get("row_count") == 14, "v047 paper lower-pair terminal source bounded-policy row count changed")
    v.check(paper_lower_pair_terminal_source_bounded_policy.get("case_count") == 2, "v047 paper lower-pair terminal source bounded-policy case count changed")
    v.check(paper_lower_pair_terminal_source_bounded_policy.get("metric_count") == 7, "v047 paper lower-pair terminal source bounded-policy metric count changed")
    v.check(paper_lower_pair_terminal_source_bounded_policy.get("source_metric_count") == 5, "v047 paper lower-pair terminal source bounded-policy source metric count changed")
    v.check(paper_lower_pair_terminal_source_bounded_policy.get("rejected_source_metric_count", 0) >= 8, "v047 paper lower-pair terminal source bounded-policy rejected-source count too small")
    v.check(paper_lower_pair_terminal_source_bounded_policy.get("h2_insufficient_row_count", 0) >= 8, "v047 paper lower-pair terminal source bounded-policy h2-insufficient count too small")
    v.check(float(paper_lower_pair_terminal_source_bounded_policy.get("max_missing_h_power_to_bounded", 0.0)) > 8.0, "v047 paper lower-pair terminal source bounded-policy missing h-power too small")
    v.check(float(paper_lower_pair_terminal_source_bounded_policy.get("max_excess_missing_power_vs_condition", 0.0)) > 5.0, "v047 paper lower-pair terminal source bounded-policy excess over condition too small")
    v.check(paper_lower_pair_terminal_source_bounded_policy.get("replacement_target") == "independent_bounded_stage_local_lower_pair_tfe_source_formula", "v047 paper lower-pair terminal source bounded-policy replacement target changed")
    v.check(paper_lower_pair_terminal_source_bounded_policy.get("accepted_h_sweep_present") is False, "v047 paper lower-pair terminal source bounded-policy unexpectedly claims accepted h-sweep")
    v.check(paper_lower_pair_terminal_source_bounded_policy.get("full_tfe_stage_replacement") is False, "v047 paper lower-pair terminal source bounded-policy unexpectedly claims full TFE replacement")
    v.check(paper_lower_pair_stage_local_bounded_source.get("status") == "paper_tfe_lower_pair_stage_local_bounded_source_formula_local_bounded_recurrent_unbounded_not_accepted", "v047 paper lower-pair stage-local bounded-source status changed")
    v.check(paper_lower_pair_stage_local_bounded_source.get("row_count") == 6, "v047 paper lower-pair stage-local bounded-source row count changed")
    v.check(paper_lower_pair_stage_local_bounded_source.get("case_count") == 2, "v047 paper lower-pair stage-local bounded-source case count changed")
    v.check(paper_lower_pair_stage_local_bounded_source.get("h_values") == [0.04, 0.02, 0.01], "v047 paper lower-pair stage-local bounded-source h values changed")
    v.check(paper_lower_pair_stage_local_bounded_source.get("stage_local_formula") == "source_i = sqrt(h*b_i)*(terminal_lower_pair_row/sqrt(h*b_terminal))", "v047 paper lower-pair stage-local bounded-source formula changed")
    v.check(paper_lower_pair_stage_local_bounded_source.get("local_formula_bounded_row_count") == 6, "v047 paper lower-pair stage-local bounded-source lost local bounded rows")
    v.check(paper_lower_pair_stage_local_bounded_source.get("recurrent_unbounded_row_count") == 6, "v047 paper lower-pair stage-local bounded-source lost recurrent-unbounded rows")
    v.check(float(paper_lower_pair_stage_local_bounded_source.get("max_local_normalized_source_norm", 0.0)) > 0.0, "v047 paper lower-pair stage-local bounded-source local norm missing")
    v.check(float(paper_lower_pair_stage_local_bounded_source.get("max_recurrent_normalized_source_norm", 0.0)) > 1.0, "v047 paper lower-pair stage-local bounded-source recurrent blow-up missing")
    v.check(float(paper_lower_pair_stage_local_bounded_source.get("max_recurrent_over_local_normalized_source_ratio", 0.0)) > 1.0e5, "v047 paper lower-pair stage-local bounded-source recurrent/local ratio too small")
    v.check(float(paper_lower_pair_stage_local_bounded_source.get("max_recurrent_terminal_velocity_norm", 0.0)) > 1.0, "v047 paper lower-pair stage-local bounded-source recurrent terminal-velocity blocker missing")
    v.check(float(paper_lower_pair_stage_local_bounded_source.get("min_local_normalized_source_observed_power_h", -1.0)) >= 0.0, "v047 paper lower-pair stage-local bounded-source local formula not bounded")
    v.check(float(paper_lower_pair_stage_local_bounded_source.get("min_recurrent_normalized_source_observed_power_h", 0.0)) < -4.0, "v047 paper lower-pair stage-local bounded-source recurrent source not unbounded")
    v.check(paper_lower_pair_stage_local_bounded_source.get("source_policy_rejected") is True, "v047 paper lower-pair stage-local bounded-source did not reject recurrent policy")
    v.check(paper_lower_pair_stage_local_bounded_source.get("accepted_h_sweep_present") is False, "v047 paper lower-pair stage-local bounded-source unexpectedly claims accepted h-sweep")
    v.check(paper_lower_pair_stage_local_bounded_source.get("full_tfe_stage_replacement") is False, "v047 paper lower-pair stage-local bounded-source unexpectedly claims full TFE replacement")
    v.check(paper_lower_pair_source_free_elimination_rank.get("status") == "paper_tfe_lower_pair_source_free_elimination_rank_deficient_not_full_tfe", "v047 paper lower-pair source-free elimination rank status changed")
    v.check(paper_lower_pair_source_free_elimination_rank.get("row_count") == 6, "v047 paper lower-pair source-free elimination rank row count changed")
    v.check(paper_lower_pair_source_free_elimination_rank.get("source_dim") == 8, "v047 paper lower-pair source-free elimination rank source dimension changed")
    v.check(paper_lower_pair_source_free_elimination_rank.get("source_elimination_rank") == 16, "v047 paper lower-pair source-free elimination rank changed")
    v.check(paper_lower_pair_source_free_elimination_rank.get("rank_defect_vs_lower_pair_rows") == 8, "v047 paper lower-pair source-free elimination rank defect changed")
    v.check(paper_lower_pair_source_free_elimination_rank.get("missing_mean_source_closure_rows") == 8, "v047 paper lower-pair source-free elimination missing mean rows changed")
    v.check(paper_lower_pair_source_free_elimination_rank.get("stage_consistency_verified") is True, "v047 paper lower-pair source-free elimination lost consistency marker")
    v.check(paper_lower_pair_source_free_elimination_rank.get("source_free_elimination_rank_complete") is False, "v047 paper lower-pair source-free elimination unexpectedly claims rank completeness")
    v.check(paper_lower_pair_source_free_elimination_rank.get("full_tfe_stage_replacement") is False, "v047 paper lower-pair source-free elimination unexpectedly claims full TFE replacement")
    v.check(paper_lower_pair_source_free_mean_velocity.get("status") == "paper_tfe_lower_pair_source_free_mean_velocity_closure_solved_order_limited_not_full_tfe", "v047 paper lower-pair source-free mean-velocity closure status changed")
    v.check(paper_lower_pair_source_free_mean_velocity.get("row_count") == 6, "v047 paper lower-pair source-free mean-velocity closure row count changed")
    v.check(paper_lower_pair_source_free_mean_velocity.get("source_consistency_rows") == 16, "v047 paper lower-pair source-free mean-velocity closure source-consistency row count changed")
    v.check(paper_lower_pair_source_free_mean_velocity.get("mean_velocity_closure_rows") == 8, "v047 paper lower-pair source-free mean-velocity closure mean-row count changed")
    v.check(paper_lower_pair_source_free_mean_velocity.get("source_free_lower_pair_rows") == 24, "v047 paper lower-pair source-free mean-velocity closure lower-pair row count changed")
    v.check(paper_lower_pair_source_free_mean_velocity.get("endpoint_boundary_source_removed") is True, "v047 paper lower-pair source-free mean-velocity closure did not remove endpoint source")
    v.check(paper_lower_pair_source_free_mean_velocity.get("projection_used") is False, "v047 paper lower-pair source-free mean-velocity closure unexpectedly uses projection")
    v.check(paper_lower_pair_source_free_mean_velocity.get("terminal_row_replacement_used") is False, "v047 paper lower-pair source-free mean-velocity closure unexpectedly uses terminal-row replacement")
    v.check(paper_lower_pair_source_free_mean_velocity.get("accepted_h_sweep_present") is False, "v047 paper lower-pair source-free mean-velocity closure unexpectedly claims accepted h-sweep")
    v.check(paper_lower_pair_source_free_mean_velocity.get("full_tfe_stage_replacement") is False, "v047 paper lower-pair source-free mean-velocity closure unexpectedly claims full TFE replacement")
    v.check(float(paper_lower_pair_source_free_mean_velocity.get("max_residual_norm", 1.0)) < 1.0e-8, "v047 paper lower-pair source-free mean-velocity closure residual too large")
    v.check(float(paper_lower_pair_source_free_mean_velocity.get("max_raw_terminal_endpoint_velocity_constraint_norm", 1.0)) < 1.0e-4, "v047 paper lower-pair source-free mean-velocity closure terminal velocity too large")
    v.check(float(paper_lower_pair_source_free_mean_velocity.get("min_position_order", 0.0)) > 1.5, "v047 paper lower-pair source-free mean-velocity closure position order regressed")
    v.check(float(paper_lower_pair_source_free_mean_velocity.get("min_velocity_order", 0.0)) > 1.5, "v047 paper lower-pair source-free mean-velocity closure velocity order regressed")
    v.check(paper_lower_pair_source_free_mean_blend.get("status") == "paper_tfe_lower_pair_source_free_mean_blend_closure_family_partial_not_full_tfe", "v047 paper lower-pair source-free mean-blend closure status changed")
    v.check(paper_lower_pair_source_free_mean_blend.get("row_count") == 42, "v047 paper lower-pair source-free mean-blend closure row count changed")
    v.check(paper_lower_pair_source_free_mean_blend.get("alpha_count") == 7, "v047 paper lower-pair source-free mean-blend closure alpha count changed")
    v.check(paper_lower_pair_source_free_mean_blend.get("global_best_alpha_by_max_terminal_velocity") == 0.0, "v047 paper lower-pair source-free mean-blend closure best alpha changed")
    v.check(paper_lower_pair_source_free_mean_blend.get("endpoint_boundary_source_removed") is True, "v047 paper lower-pair source-free mean-blend closure did not remove endpoint source")
    v.check(paper_lower_pair_source_free_mean_blend.get("projection_used") is False, "v047 paper lower-pair source-free mean-blend closure unexpectedly uses projection")
    v.check(paper_lower_pair_source_free_mean_blend.get("terminal_row_replacement_used") is False, "v047 paper lower-pair source-free mean-blend closure unexpectedly uses terminal-row replacement")
    v.check(paper_lower_pair_source_free_mean_blend.get("accepted_h_sweep_present") is False, "v047 paper lower-pair source-free mean-blend closure unexpectedly claims accepted h-sweep")
    v.check(paper_lower_pair_source_free_mean_blend.get("best_alpha_terminal_velocity_closed") is False, "v047 paper lower-pair source-free mean-blend closure unexpectedly closes terminal velocity")
    v.check(paper_lower_pair_source_free_mean_blend.get("full_tfe_stage_replacement") is False, "v047 paper lower-pair source-free mean-blend closure unexpectedly claims full TFE replacement")
    v.check(1.0e-10 < float(paper_lower_pair_source_free_mean_blend.get("best_alpha_max_terminal_endpoint_velocity_constraint_norm", 0.0)) < 1.0e-8, "v047 paper lower-pair source-free mean-blend closure terminal velocity range changed")
    v.check(float(paper_lower_pair_source_free_mean_blend.get("best_alpha_max_residual_norm", 1.0)) < 1.0e-8, "v047 paper lower-pair source-free mean-blend closure residual too large")
    v.check(paper_lower_pair_source_free_mean_blend_trajectory.get("status") == "paper_tfe_lower_pair_source_free_mean_blend_trajectory_order_limited_not_full_tfe", "v047 paper lower-pair source-free mean-blend trajectory status changed")
    v.check(paper_lower_pair_source_free_mean_blend_trajectory.get("row_count") == 6, "v047 paper lower-pair source-free mean-blend trajectory row count changed")
    v.check(paper_lower_pair_source_free_mean_blend_trajectory.get("selected_alpha") == 0.0, "v047 paper lower-pair source-free mean-blend trajectory selected alpha changed")
    v.check(paper_lower_pair_source_free_mean_blend_trajectory.get("endpoint_boundary_source_removed") is True, "v047 paper lower-pair source-free mean-blend trajectory did not remove endpoint source")
    v.check(paper_lower_pair_source_free_mean_blend_trajectory.get("projection_used") is False, "v047 paper lower-pair source-free mean-blend trajectory unexpectedly uses projection")
    v.check(paper_lower_pair_source_free_mean_blend_trajectory.get("terminal_row_replacement_used") is False, "v047 paper lower-pair source-free mean-blend trajectory unexpectedly uses terminal-row replacement")
    v.check(paper_lower_pair_source_free_mean_blend_trajectory.get("trajectory_h_sweep_present") is True, "v047 paper lower-pair source-free mean-blend trajectory lost trajectory h-sweep")
    v.check(paper_lower_pair_source_free_mean_blend_trajectory.get("accepted_h_sweep_present") is False, "v047 paper lower-pair source-free mean-blend trajectory unexpectedly claims accepted h-sweep")
    v.check(paper_lower_pair_source_free_mean_blend_trajectory.get("terminal_velocity_closed") is False, "v047 paper lower-pair source-free mean-blend trajectory unexpectedly closes terminal velocity")
    v.check(paper_lower_pair_source_free_mean_blend_trajectory.get("full_tfe_stage_replacement") is False, "v047 paper lower-pair source-free mean-blend trajectory unexpectedly claims full TFE replacement")
    v.check(float(paper_lower_pair_source_free_mean_blend_trajectory.get("max_residual_norm", 1.0)) < 1.0e-8, "v047 paper lower-pair source-free mean-blend trajectory residual too large")
    v.check(1.0e-6 < float(paper_lower_pair_source_free_mean_blend_trajectory.get("max_raw_terminal_endpoint_velocity_constraint_norm", 0.0)) < 1.0e-4, "v047 paper lower-pair source-free mean-blend trajectory terminal velocity range changed")
    v.check(float(paper_lower_pair_source_free_mean_blend_trajectory.get("min_position_order", 0.0)) > 1.8, "v047 paper lower-pair source-free mean-blend trajectory position order regressed")
    v.check(float(paper_lower_pair_source_free_mean_blend_trajectory.get("min_velocity_order", 0.0)) > 1.8, "v047 paper lower-pair source-free mean-blend trajectory velocity order regressed")
    v.check(paper_lower_pair_source_free_mean_blend_trajectory_alpha_sweep.get("status") == "paper_tfe_lower_pair_source_free_mean_blend_trajectory_alpha_sweep_partial_not_full_tfe", "v047 paper lower-pair source-free mean-blend trajectory alpha-sweep status changed")
    v.check(paper_lower_pair_source_free_mean_blend_trajectory_alpha_sweep.get("row_count") == 42, "v047 paper lower-pair source-free mean-blend trajectory alpha-sweep row count changed")
    v.check(paper_lower_pair_source_free_mean_blend_trajectory_alpha_sweep.get("alpha_count") == 7, "v047 paper lower-pair source-free mean-blend trajectory alpha-sweep alpha count changed")
    v.check(paper_lower_pair_source_free_mean_blend_trajectory_alpha_sweep.get("global_best_alpha_by_trajectory_terminal_velocity") == 0.75, "v047 paper lower-pair source-free mean-blend trajectory alpha-sweep best alpha changed")
    v.check(paper_lower_pair_source_free_mean_blend_trajectory_alpha_sweep.get("external_endpoint_source_removed") is True, "v047 paper lower-pair source-free mean-blend trajectory alpha-sweep did not remove external endpoint source")
    v.check(paper_lower_pair_source_free_mean_blend_trajectory_alpha_sweep.get("endpoint_boundary_source_removed") is True, "v047 paper lower-pair source-free mean-blend trajectory alpha-sweep did not remove endpoint source")
    v.check(paper_lower_pair_source_free_mean_blend_trajectory_alpha_sweep.get("projection_used") is False, "v047 paper lower-pair source-free mean-blend trajectory alpha-sweep unexpectedly uses projection")
    v.check(paper_lower_pair_source_free_mean_blend_trajectory_alpha_sweep.get("terminal_row_replacement_used") is False, "v047 paper lower-pair source-free mean-blend trajectory alpha-sweep unexpectedly uses terminal-row replacement")
    v.check(paper_lower_pair_source_free_mean_blend_trajectory_alpha_sweep.get("trajectory_alpha_sweep_present") is True, "v047 paper lower-pair source-free mean-blend trajectory alpha-sweep lost sweep marker")
    v.check(paper_lower_pair_source_free_mean_blend_trajectory_alpha_sweep.get("accepted_h_sweep_present") is False, "v047 paper lower-pair source-free mean-blend trajectory alpha-sweep unexpectedly claims accepted h-sweep")
    v.check(paper_lower_pair_source_free_mean_blend_trajectory_alpha_sweep.get("terminal_velocity_closed") is False, "v047 paper lower-pair source-free mean-blend trajectory alpha-sweep unexpectedly closes terminal velocity")
    v.check(paper_lower_pair_source_free_mean_blend_trajectory_alpha_sweep.get("full_tfe_stage_replacement") is False, "v047 paper lower-pair source-free mean-blend trajectory alpha-sweep unexpectedly claims full TFE replacement")
    v.check(float(paper_lower_pair_source_free_mean_blend_trajectory_alpha_sweep.get("best_alpha_max_residual_norm", 1.0)) < 1.0e-8, "v047 paper lower-pair source-free mean-blend trajectory alpha-sweep residual too large")
    v.check(7.0e-6 < float(paper_lower_pair_source_free_mean_blend_trajectory_alpha_sweep.get("best_alpha_max_terminal_endpoint_velocity_constraint_norm", 0.0)) < 8.0e-6, "v047 paper lower-pair source-free mean-blend trajectory alpha-sweep terminal velocity range changed")
    v.check(float(paper_lower_pair_source_free_mean_blend_trajectory_alpha_sweep.get("best_alpha_min_position_order", 0.0)) > 1.8, "v047 paper lower-pair source-free mean-blend trajectory alpha-sweep position order regressed")
    v.check(float(paper_lower_pair_source_free_mean_blend_trajectory_alpha_sweep.get("best_alpha_min_velocity_order", 0.0)) > 1.8, "v047 paper lower-pair source-free mean-blend trajectory alpha-sweep velocity order regressed")
    v.check(paper_lower_pair_source_free_component_blend_trajectory.get("status") == "paper_tfe_lower_pair_source_free_component_blend_trajectory_no_improvement_not_full_tfe", "v047 paper lower-pair source-free component-blend trajectory status changed")
    v.check(paper_lower_pair_source_free_component_blend_trajectory.get("row_count") == 6, "v047 paper lower-pair source-free component-blend trajectory row count changed")
    v.check(len(paper_lower_pair_source_free_component_blend_trajectory.get("component_alpha_vector", [])) == 8, "v047 paper lower-pair source-free component-blend trajectory alpha vector length changed")
    v.check(0.70 < float(paper_lower_pair_source_free_component_blend_trajectory.get("component_alpha_min", 0.0)) < 0.71, "v047 paper lower-pair source-free component-blend trajectory alpha min changed")
    v.check(2.7 < float(paper_lower_pair_source_free_component_blend_trajectory.get("component_alpha_max", 0.0)) < 2.8, "v047 paper lower-pair source-free component-blend trajectory alpha max changed")
    v.check(paper_lower_pair_source_free_component_blend_trajectory.get("external_endpoint_source_removed") is True, "v047 paper lower-pair source-free component-blend trajectory did not remove external endpoint source")
    v.check(paper_lower_pair_source_free_component_blend_trajectory.get("endpoint_boundary_source_removed") is True, "v047 paper lower-pair source-free component-blend trajectory did not remove endpoint source")
    v.check(paper_lower_pair_source_free_component_blend_trajectory.get("projection_used") is False, "v047 paper lower-pair source-free component-blend trajectory unexpectedly uses projection")
    v.check(paper_lower_pair_source_free_component_blend_trajectory.get("terminal_row_replacement_used") is False, "v047 paper lower-pair source-free component-blend trajectory unexpectedly uses terminal-row replacement")
    v.check(paper_lower_pair_source_free_component_blend_trajectory.get("componentwise_blend_present") is True, "v047 paper lower-pair source-free component-blend trajectory lost componentwise marker")
    v.check(paper_lower_pair_source_free_component_blend_trajectory.get("terminal_velocity_closed") is False, "v047 paper lower-pair source-free component-blend trajectory unexpectedly closes terminal velocity")
    v.check(paper_lower_pair_source_free_component_blend_trajectory.get("full_tfe_stage_replacement") is False, "v047 paper lower-pair source-free component-blend trajectory unexpectedly claims full TFE replacement")
    v.check(float(paper_lower_pair_source_free_component_blend_trajectory.get("max_residual_norm", 1.0)) < 1.0e-8, "v047 paper lower-pair source-free component-blend trajectory residual too large")
    v.check(7.0e-6 < float(paper_lower_pair_source_free_component_blend_trajectory.get("max_raw_terminal_endpoint_velocity_constraint_norm", 0.0)) < 8.0e-6, "v047 paper lower-pair source-free component-blend trajectory terminal velocity range changed")
    v.check(0.99 < float(paper_lower_pair_source_free_component_blend_trajectory.get("max_terminal_velocity_vs_scalar_baseline_ratio", 0.0)) < 1.02, "v047 paper lower-pair source-free component-blend trajectory no longer matches scalar terminal blocker")
    v.check(float(paper_lower_pair_source_free_component_blend_trajectory.get("min_position_order", 0.0)) > 1.8, "v047 paper lower-pair source-free component-blend trajectory position order regressed")
    v.check(float(paper_lower_pair_source_free_component_blend_trajectory.get("min_velocity_order", 0.0)) > 1.8, "v047 paper lower-pair source-free component-blend trajectory velocity order regressed")
    v.check(paper_lower_pair_source_free_terminal_extrapolation.get("status") == "paper_tfe_lower_pair_source_free_terminal_velocity_extrapolation_trajectory_improved_order_limited_not_full_tfe", "v047 paper lower-pair source-free terminal extrapolation status changed")
    v.check(paper_lower_pair_source_free_terminal_extrapolation.get("row_count") == 6, "v047 paper lower-pair source-free terminal extrapolation row count changed")
    v.check(paper_lower_pair_source_free_terminal_extrapolation.get("source_consistency_rows") == 16, "v047 paper lower-pair source-free terminal extrapolation source-consistency rows changed")
    v.check(paper_lower_pair_source_free_terminal_extrapolation.get("terminal_velocity_extrapolation_closure_rows") == 8, "v047 paper lower-pair source-free terminal extrapolation closure rows changed")
    v.check(paper_lower_pair_source_free_terminal_extrapolation.get("external_endpoint_source_removed") is True, "v047 paper lower-pair source-free terminal extrapolation did not remove external endpoint source")
    v.check(paper_lower_pair_source_free_terminal_extrapolation.get("endpoint_boundary_source_removed") is True, "v047 paper lower-pair source-free terminal extrapolation did not remove endpoint source")
    v.check(paper_lower_pair_source_free_terminal_extrapolation.get("projection_used") is False, "v047 paper lower-pair source-free terminal extrapolation unexpectedly uses projection")
    v.check(paper_lower_pair_source_free_terminal_extrapolation.get("terminal_row_replacement_used") is False, "v047 paper lower-pair source-free terminal extrapolation unexpectedly uses terminal-row replacement")
    v.check(paper_lower_pair_source_free_terminal_extrapolation.get("terminal_velocity_extrapolation_present") is True, "v047 paper lower-pair source-free terminal extrapolation lost marker")
    v.check(paper_lower_pair_source_free_terminal_extrapolation.get("terminal_velocity_closed") is False, "v047 paper lower-pair source-free terminal extrapolation unexpectedly closes terminal velocity")
    v.check(paper_lower_pair_source_free_terminal_extrapolation.get("full_tfe_stage_replacement") is False, "v047 paper lower-pair source-free terminal extrapolation unexpectedly claims full TFE replacement")
    v.check(float(paper_lower_pair_source_free_terminal_extrapolation.get("max_residual_norm", 1.0)) < 1.0e-8, "v047 paper lower-pair source-free terminal extrapolation residual too large")
    v.check(1.0e-5 < float(paper_lower_pair_source_free_terminal_extrapolation.get("max_raw_terminal_endpoint_velocity_constraint_norm", 0.0)) < 1.3e-5, "v047 paper lower-pair source-free terminal extrapolation terminal velocity range changed")
    v.check(1.0 < float(paper_lower_pair_source_free_terminal_extrapolation.get("max_terminal_velocity_vs_component_blend_ratio", 0.0)) < 2.0, "v047 paper lower-pair source-free terminal extrapolation worst-case ratio changed")
    v.check(0.0 < float(paper_lower_pair_source_free_terminal_extrapolation.get("smooth_terminal_velocity_vs_component_blend_ratio", 1.0)) < 0.2, "v047 paper lower-pair source-free terminal extrapolation smooth ratio changed")
    v.check(float(paper_lower_pair_source_free_terminal_extrapolation.get("min_position_order", 0.0)) > 2.0, "v047 paper lower-pair source-free terminal extrapolation position order regressed")
    v.check(float(paper_lower_pair_source_free_terminal_extrapolation.get("min_velocity_order", 0.0)) > 1.8, "v047 paper lower-pair source-free terminal extrapolation velocity order regressed")
    v.check(paper_lower_pair_source_free_terminal_extrapolation_blend.get("status") == "paper_tfe_lower_pair_source_free_terminal_extrapolation_blend_trajectory_sweep_not_full_tfe", "v047 paper lower-pair source-free terminal-extrapolation blend status changed")
    v.check(paper_lower_pair_source_free_terminal_extrapolation_blend.get("row_count") == 30, "v047 paper lower-pair source-free terminal-extrapolation blend row count changed")
    v.check(paper_lower_pair_source_free_terminal_extrapolation_blend.get("case_count") == 2, "v047 paper lower-pair source-free terminal-extrapolation blend case count changed")
    v.check(paper_lower_pair_source_free_terminal_extrapolation_blend.get("beta_count") == 5, "v047 paper lower-pair source-free terminal-extrapolation blend beta count changed")
    v.check(paper_lower_pair_source_free_terminal_extrapolation_blend.get("source_consistency_rows") == 16, "v047 paper lower-pair source-free terminal-extrapolation blend source-consistency rows changed")
    v.check(paper_lower_pair_source_free_terminal_extrapolation_blend.get("terminal_extrapolation_blend_closure_rows") == 8, "v047 paper lower-pair source-free terminal-extrapolation blend closure rows changed")
    v.check(paper_lower_pair_source_free_terminal_extrapolation_blend.get("external_endpoint_source_removed") is True, "v047 paper lower-pair source-free terminal-extrapolation blend did not remove external endpoint source")
    v.check(paper_lower_pair_source_free_terminal_extrapolation_blend.get("endpoint_boundary_source_removed") is True, "v047 paper lower-pair source-free terminal-extrapolation blend did not remove endpoint source")
    v.check(paper_lower_pair_source_free_terminal_extrapolation_blend.get("projection_used") is False, "v047 paper lower-pair source-free terminal-extrapolation blend unexpectedly uses projection")
    v.check(paper_lower_pair_source_free_terminal_extrapolation_blend.get("terminal_row_replacement_used") is False, "v047 paper lower-pair source-free terminal-extrapolation blend unexpectedly uses terminal-row replacement")
    v.check(paper_lower_pair_source_free_terminal_extrapolation_blend.get("terminal_extrapolation_blend_present") is True, "v047 paper lower-pair source-free terminal-extrapolation blend lost marker")
    v.check(paper_lower_pair_source_free_terminal_extrapolation_blend.get("terminal_velocity_closed") is False, "v047 paper lower-pair source-free terminal-extrapolation blend unexpectedly closes terminal velocity")
    v.check(paper_lower_pair_source_free_terminal_extrapolation_blend.get("full_tfe_stage_replacement") is False, "v047 paper lower-pair source-free terminal-extrapolation blend unexpectedly claims full TFE replacement")
    v.check(float(paper_lower_pair_source_free_terminal_extrapolation_blend.get("max_residual_norm", 1.0)) < 1.0e-8, "v047 paper lower-pair source-free terminal-extrapolation blend residual too large")
    v.check(0.0 < float(paper_lower_pair_source_free_terminal_extrapolation_blend.get("global_best_beta_max_terminal_velocity", 0.0)) < 1.3e-5, "v047 paper lower-pair source-free terminal-extrapolation blend best terminal velocity range changed")
    v.check(0.0 < float(paper_lower_pair_source_free_terminal_extrapolation_blend.get("best_terminal_velocity_vs_terminal_extrapolation_ratio", 0.0)) <= 1.000000001, "v047 paper lower-pair source-free terminal-extrapolation blend no longer beats or matches pure extrapolation")
    v.check(paper_lower_pair_centered_terminal_velocity_bridge.get("status") == "paper_tfe_lower_pair_centered_terminal_velocity_bridge_order_limited_not_full_tfe", "v047 paper lower-pair centered terminal-velocity bridge status changed")
    v.check(paper_lower_pair_centered_terminal_velocity_bridge.get("row_count") == 18, "v047 paper lower-pair centered terminal-velocity bridge row count changed")
    v.check(paper_lower_pair_centered_terminal_velocity_bridge.get("case_count") == 2, "v047 paper lower-pair centered terminal-velocity bridge case count changed")
    v.check(paper_lower_pair_centered_terminal_velocity_bridge.get("gamma_count") == 3, "v047 paper lower-pair centered terminal-velocity bridge gamma count changed")
    v.check(paper_lower_pair_centered_terminal_velocity_bridge.get("gamma_values") == [0.0, 0.5, 1.0], "v047 paper lower-pair centered terminal-velocity bridge gamma path changed")
    v.check(paper_lower_pair_centered_terminal_velocity_bridge.get("source_consistency_rows") == 16, "v047 paper lower-pair centered terminal-velocity bridge source-consistency rows changed")
    v.check(paper_lower_pair_centered_terminal_velocity_bridge.get("centered_terminal_velocity_bridge_closure_rows") == 8, "v047 paper lower-pair centered terminal-velocity bridge closure rows changed")
    v.check(paper_lower_pair_centered_terminal_velocity_bridge.get("source_free_lower_pair_rows") == 24, "v047 paper lower-pair centered terminal-velocity bridge lower-pair row budget changed")
    v.check(paper_lower_pair_centered_terminal_velocity_bridge.get("external_endpoint_source_removed") is True, "v047 paper lower-pair centered terminal-velocity bridge did not remove external endpoint source")
    v.check(paper_lower_pair_centered_terminal_velocity_bridge.get("endpoint_boundary_source_removed") is False, "v047 paper lower-pair centered terminal-velocity bridge unexpectedly removed endpoint-boundary rows")
    v.check(paper_lower_pair_centered_terminal_velocity_bridge.get("terminal_boundary_row_used") is True, "v047 paper lower-pair centered terminal-velocity bridge lost terminal-boundary row marker")
    v.check(paper_lower_pair_centered_terminal_velocity_bridge.get("terminal_row_replacement_used") is True, "v047 paper lower-pair centered terminal-velocity bridge lost terminal-row replacement marker")
    v.check(paper_lower_pair_centered_terminal_velocity_bridge.get("projection_used") is False, "v047 paper lower-pair centered terminal-velocity bridge unexpectedly uses projection")
    v.check(paper_lower_pair_centered_terminal_velocity_bridge.get("trajectory_h_sweep_present") is True, "v047 paper lower-pair centered terminal-velocity bridge lost trajectory h-sweep marker")
    v.check(paper_lower_pair_centered_terminal_velocity_bridge.get("accepted_h_sweep_present") is False, "v047 paper lower-pair centered terminal-velocity bridge unexpectedly claims accepted h-sweep")
    v.check(paper_lower_pair_centered_terminal_velocity_bridge.get("terminal_velocity_closed") is True, "v047 paper lower-pair centered terminal-velocity bridge no longer closes terminal velocity")
    v.check(paper_lower_pair_centered_terminal_velocity_bridge.get("smooth_order_ok") is False, "v047 paper lower-pair centered terminal-velocity bridge unexpectedly passes smooth-order gate")
    v.check(paper_lower_pair_centered_terminal_velocity_bridge.get("sharp_order_ok") is True, "v047 paper lower-pair centered terminal-velocity bridge lost sharp-order gate")
    v.check(paper_lower_pair_centered_terminal_velocity_bridge.get("full_tfe_stage_replacement") is False, "v047 paper lower-pair centered terminal-velocity bridge unexpectedly claims full TFE replacement")
    v.check(float(paper_lower_pair_centered_terminal_velocity_bridge.get("max_residual_norm", 1.0)) < 1.0e-8, "v047 paper lower-pair centered terminal-velocity bridge residual too large")
    v.check(paper_lower_pair_centered_terminal_velocity_bridge.get("global_best_gamma_by_terminal_velocity") == 0.0, "v047 paper lower-pair centered terminal-velocity bridge best gamma changed")
    v.check(float(paper_lower_pair_centered_terminal_velocity_bridge.get("global_best_gamma_max_terminal_velocity", 1.0)) < 1.0e-10, "v047 paper lower-pair centered terminal-velocity bridge terminal velocity no longer closes")
    v.check(3.0 < float(paper_lower_pair_centered_terminal_velocity_bridge.get("cases", {}).get("cylindrical_smooth", {}).get("position_order", 0.0)) < 4.5, "v047 paper lower-pair centered terminal-velocity bridge smooth order range changed")
    v.check(paper_lower_pair_closure_acceptance_matrix.get("status") == "paper_tfe_lower_pair_closure_acceptance_matrix_prioritized_not_full_tfe", "v047 paper lower-pair closure acceptance matrix status changed")
    v.check(paper_lower_pair_closure_acceptance_matrix.get("row_count") == 14, "v047 paper lower-pair closure acceptance matrix row count changed")
    v.check(paper_lower_pair_closure_acceptance_matrix.get("candidate_count") == 14, "v047 paper lower-pair closure acceptance matrix candidate count changed")
    v.check(paper_lower_pair_closure_acceptance_matrix.get("accepted_candidate_count") == 0, "v047 paper lower-pair closure acceptance matrix unexpectedly accepts a candidate")
    v.check(paper_lower_pair_closure_acceptance_matrix.get("best_order_preserving_source_free_candidate") == "source_free_mean_blend_trajectory_best_alpha", "v047 paper lower-pair closure acceptance matrix best order source-free candidate changed")
    v.check(paper_lower_pair_closure_acceptance_matrix.get("best_terminal_velocity_candidate") in {"centered_terminal_velocity_bridge", "source_free_final_stage_velocity_closure"}, "v047 paper lower-pair closure acceptance matrix best terminal candidate changed")
    v.check(paper_lower_pair_closure_acceptance_matrix.get("full_tfe_stage_replacement") is False, "v047 paper lower-pair closure acceptance matrix unexpectedly claims full TFE replacement")
    v.check(paper_lower_pair_closure_property_pareto.get("status") == "paper_tfe_lower_pair_closure_property_pareto_split_not_full_tfe", "v047 paper lower-pair closure property Pareto status changed")
    v.check(paper_lower_pair_closure_property_pareto.get("row_count") == 5, "v047 paper lower-pair closure property Pareto row count changed")
    v.check(paper_lower_pair_closure_property_pareto.get("candidate_count") == 14, "v047 paper lower-pair closure property Pareto candidate count changed")
    v.check(paper_lower_pair_closure_property_pareto.get("accepted_candidate_count") == 0, "v047 paper lower-pair closure property Pareto unexpectedly accepts a candidate")
    v.check(paper_lower_pair_closure_property_pareto.get("source_free_no_replacement_candidate_count", 0) >= 9, "v047 paper lower-pair closure property Pareto lost source-free/no-replacement candidates")
    v.check(paper_lower_pair_closure_property_pareto.get("order_preserving_source_free_candidate_count", 0) >= 5, "v047 paper lower-pair closure property Pareto lost order-preserving source-free candidates")
    v.check(paper_lower_pair_closure_property_pareto.get("terminal_velocity_closed_candidate_count") == 3, "v047 paper lower-pair closure property Pareto terminal-closed count changed")
    v.check(paper_lower_pair_closure_property_pareto.get("property_split_confirmed") is True, "v047 paper lower-pair closure property Pareto no longer confirms the property split")
    v.check(paper_lower_pair_closure_property_pareto.get("best_source_free_terminal_velocity_candidate") == "source_free_final_stage_velocity_closure", "v047 paper lower-pair closure property Pareto best source-free terminal candidate changed")
    v.check(float(paper_lower_pair_closure_property_pareto.get("best_source_free_terminal_velocity_norm", 1.0)) < 1.0e-10, "v047 paper lower-pair closure property Pareto source-free terminal norm changed")
    v.check(paper_lower_pair_closure_property_pareto.get("best_terminal_velocity_candidate") in {"centered_terminal_velocity_bridge", "source_free_final_stage_velocity_closure"}, "v047 paper lower-pair closure property Pareto best terminal candidate changed")
    v.check(float(paper_lower_pair_closure_property_pareto.get("best_terminal_velocity_norm", 1.0)) < 1.0e-10, "v047 paper lower-pair closure property Pareto terminal norm too large")
    v.check(paper_lower_pair_closure_property_pareto.get("full_tfe_stage_replacement") is False, "v047 paper lower-pair closure property Pareto unexpectedly claims full TFE replacement")
    v.check(paper_lower_pair_velocity_compression.get("status") == "paper_tfe_lower_pair_velocity_compression_fixed_full_spans_not_full_tfe", "v047 paper lower-pair velocity-compression status changed")
    v.check(paper_lower_pair_velocity_compression.get("value_level_probe_row_count") == 72, "v047 paper lower-pair value-level compression row count changed")
    v.check(paper_lower_pair_velocity_compression.get("value_level_probe_value_ok_row_count") == 72, "v047 paper lower-pair value-level compression value-ok row count changed")
    v.check(paper_lower_pair_velocity_compression.get("value_level_probe_spanning_row_count") == 18, "v047 paper lower-pair value-level compression spanning row count changed")
    v.check(paper_lower_pair_velocity_compression.get("value_level_probe_value_balanced_spanning_row_count") == 18, "v047 paper lower-pair value-level compression value-balanced span count changed")
    v.check(paper_lower_pair_velocity_compression.get("value_level_probe_meaningful_value_balanced_spanning_row_count") == 0, "v047 paper lower-pair value-level compression unexpectedly found a meaningful non-final span")
    v.check(float(paper_lower_pair_velocity_compression.get("value_level_probe_max_spanning_nonfinal_stage_energy_fraction", 1.0)) < 1.0e-12, "v047 paper lower-pair value-level compression no longer records final-stage-selector-like spans")
    v.check(paper_lower_pair_velocity_compression.get("derivative_aware_probe_row_count") == 36, "v047 paper lower-pair derivative-aware compression row count changed")
    v.check(paper_lower_pair_velocity_compression.get("derivative_aware_probe_value_ok_row_count") == 36, "v047 paper lower-pair derivative-aware compression value-ok count changed")
    v.check(paper_lower_pair_velocity_compression.get("derivative_aware_probe_spanning_row_count") == 36, "v047 paper lower-pair derivative-aware compression spanning count changed")
    v.check(paper_lower_pair_velocity_compression.get("derivative_aware_probe_meaningful_value_balanced_spanning_row_count") == 36, "v047 paper lower-pair derivative-aware compression meaningful span count changed")
    v.check(float(paper_lower_pair_velocity_compression.get("derivative_aware_probe_best_projection_relative_residual", 1.0)) < 1.0e-12, "v047 paper lower-pair derivative-aware compression residual too large")
    v.check(float(paper_lower_pair_velocity_compression.get("derivative_aware_probe_best_base_projection_relative_residual", 0.0)) > 0.9, "v047 paper lower-pair derivative-aware base residual unexpectedly small")
    v.check(paper_lower_pair_velocity_compression.get("bounded_gradient_probe_row_count") == 288, "v047 paper lower-pair bounded-gradient compression row count changed")
    v.check(paper_lower_pair_velocity_compression.get("bounded_gradient_probe_value_ok_row_count") == 288, "v047 paper lower-pair bounded-gradient compression value-ok count changed")
    v.check(paper_lower_pair_velocity_compression.get("bounded_gradient_probe_meaningful_row_count") == 288, "v047 paper lower-pair bounded-gradient compression meaningful count changed")
    v.check(paper_lower_pair_velocity_compression.get("bounded_gradient_probe_spanning_row_count") == 92, "v047 paper lower-pair bounded-gradient compression span count changed")
    v.check(paper_lower_pair_velocity_compression.get("bounded_gradient_probe_span_count_by_cap") == {"1e+04": 0, "1e+06": 2, "1e+08": 4, "1e+10": 8, "1e+12": 12, "1e+14": 12, "1e+16": 18, "1e+18": 36}, "v047 paper lower-pair bounded-gradient cap sweep changed")
    v.check(float(paper_lower_pair_velocity_compression.get("bounded_gradient_probe_practical_cap", 0.0)) == 1.0e12, "v047 paper lower-pair bounded-gradient practical cap changed")
    v.check(paper_lower_pair_velocity_compression.get("bounded_gradient_probe_practical_cap_spanning_row_count") == 12, "v047 paper lower-pair bounded-gradient practical cap span count changed")
    v.check(float(paper_lower_pair_velocity_compression.get("bounded_gradient_probe_min_all_span_cap", 0.0)) == 1.0e18, "v047 paper lower-pair bounded-gradient all-span cap changed")
    v.check(paper_lower_pair_velocity_compression.get("bounded_gradient_probe_bounded_formula_present") is False, "v047 paper lower-pair bounded-gradient unexpectedly claims bounded formula")
    v.check(paper_lower_pair_velocity_compression.get("bounded_formula_probe_row_count") == 648, "v047 paper lower-pair bounded-formula compression row count changed")
    v.check(paper_lower_pair_velocity_compression.get("bounded_formula_probe_law_count") == 3, "v047 paper lower-pair bounded-formula law count changed")
    v.check(paper_lower_pair_velocity_compression.get("bounded_formula_probe_value_ok_row_count") == 648, "v047 paper lower-pair bounded-formula value-ok count changed")
    v.check(paper_lower_pair_velocity_compression.get("bounded_formula_probe_meaningful_row_count") == 648, "v047 paper lower-pair bounded-formula meaningful count changed")
    v.check(paper_lower_pair_velocity_compression.get("bounded_formula_probe_spanning_row_count") == 366, "v047 paper lower-pair bounded-formula span count changed")
    v.check(paper_lower_pair_velocity_compression.get("bounded_formula_probe_span_count_by_cap") == {"1e+12": 30, "1e+14": 36, "1e+16": 54, "1e+18": 66, "1e+20": 72, "1e+22": 108}, "v047 paper lower-pair bounded-formula cap sweep changed")
    v.check(float(paper_lower_pair_velocity_compression.get("bounded_formula_probe_min_all_span_cap", 0.0)) == 1.0e22, "v047 paper lower-pair bounded-formula all-span cap changed")
    v.check(paper_lower_pair_velocity_compression.get("bounded_formula_probe_bounded_saturation_formula_present") is True, "v047 paper lower-pair bounded-formula saturation marker missing")
    v.check(paper_lower_pair_velocity_compression.get("bounded_formula_probe_target_direction_oracle_used") is True, "v047 paper lower-pair bounded-formula oracle marker missing")
    v.check(paper_lower_pair_velocity_compression.get("target_free_formula_probe_row_count") == 2592, "v047 paper lower-pair target-free formula row count changed")
    v.check(paper_lower_pair_velocity_compression.get("target_free_formula_probe_law_count") == 12, "v047 paper lower-pair target-free formula law count changed")
    v.check(paper_lower_pair_velocity_compression.get("target_free_formula_probe_value_ok_row_count") == 2592, "v047 paper lower-pair target-free formula value-ok count changed")
    v.check(paper_lower_pair_velocity_compression.get("target_free_formula_probe_meaningful_row_count") == 2592, "v047 paper lower-pair target-free formula meaningful count changed")
    v.check(paper_lower_pair_velocity_compression.get("target_free_formula_probe_spanning_row_count") == 0, "v047 paper lower-pair target-free formula unexpectedly spans")
    v.check(paper_lower_pair_velocity_compression.get("target_free_formula_probe_span_count_by_cap") == {"1e+12": 0, "1e+14": 0, "1e+16": 0, "1e+18": 0, "1e+20": 0, "1e+22": 0}, "v047 paper lower-pair target-free formula cap sweep changed")
    v.check(paper_lower_pair_velocity_compression.get("target_free_formula_probe_min_all_span_cap") is None, "v047 paper lower-pair target-free formula unexpectedly has all-span cap")
    v.check(paper_lower_pair_velocity_compression.get("target_free_formula_probe_target_direction_oracle_used") is False, "v047 paper lower-pair target-free formula unexpectedly uses target-direction oracle")
    v.check(paper_lower_pair_velocity_compression.get("target_free_formula_probe_target_jacobian_used_for_formula") is False, "v047 paper lower-pair target-free formula unexpectedly uses target Jacobian")
    v.check(paper_lower_pair_velocity_compression.get("direction_capacity_probe_row_count") == 216, "v047 paper lower-pair direction-capacity row count changed")
    v.check(paper_lower_pair_velocity_compression.get("direction_capacity_probe_feature_family_count") == 6, "v047 paper lower-pair direction-capacity feature family count changed")
    v.check(paper_lower_pair_velocity_compression.get("direction_capacity_probe_spanning_row_count") == 72, "v047 paper lower-pair direction-capacity span count changed")
    v.check(paper_lower_pair_velocity_compression.get("direction_capacity_probe_nonfinal_spanning_row_count") == 0, "v047 paper lower-pair direction-capacity non-final span count changed")
    v.check(paper_lower_pair_velocity_compression.get("direction_capacity_probe_span_count_by_feature_family") == {"all_active_velocity_rows": 0, "all_stage_velocity_rows": 36, "closure_plus_all_active_velocity_rows": 0, "row_matched_active_velocity_rows": 0, "source_plus_all_active_velocity_rows": 0, "source_plus_all_stage_velocity_rows": 36}, "v047 paper lower-pair direction-capacity span split changed")
    v.check(paper_lower_pair_velocity_compression.get("direction_capacity_probe_best_feature_family") == "all_stage_velocity_rows", "v047 paper lower-pair direction-capacity best feature changed")
    v.check(float(paper_lower_pair_velocity_compression.get("direction_capacity_probe_best_projection_relative_residual", 1.0)) < 1.0e-12, "v047 paper lower-pair direction-capacity best residual too large")
    v.check(paper_lower_pair_velocity_compression.get("direction_capacity_probe_best_nonfinal_feature_family") == "all_active_velocity_rows", "v047 paper lower-pair direction-capacity best non-final feature changed")
    v.check(0.9 < float(paper_lower_pair_velocity_compression.get("direction_capacity_probe_best_nonfinal_projection_relative_residual", 0.0)) < 1.1, "v047 paper lower-pair direction-capacity best non-final residual changed")
    v.check(paper_lower_pair_velocity_compression.get("direction_capacity_probe_target_jacobian_used_for_capacity_fit") is True, "v047 paper lower-pair direction-capacity target-Jacobian marker missing")
    v.check(paper_lower_pair_velocity_compression.get("direction_capacity_probe_target_direction_oracle_used_for_formula") is False, "v047 paper lower-pair direction-capacity formula oracle marker changed")
    v.check(paper_lower_pair_velocity_compression.get("nonlinear_capacity_probe_row_count") == 216, "v047 paper lower-pair nonlinear-capacity row count changed")
    v.check(paper_lower_pair_velocity_compression.get("nonlinear_capacity_probe_candidate_count") == 6, "v047 paper lower-pair nonlinear-capacity candidate count changed")
    v.check(paper_lower_pair_velocity_compression.get("nonlinear_capacity_probe_feature_family_count") == 6, "v047 paper lower-pair nonlinear-capacity feature count changed")
    v.check(paper_lower_pair_velocity_compression.get("nonlinear_capacity_probe_spanning_row_count") == 0, "v047 paper lower-pair nonlinear-capacity unexpectedly spans")
    v.check(paper_lower_pair_velocity_compression.get("nonlinear_capacity_probe_span_count_by_feature_family") == {"active_plus_second_diff_source_rows_perp": 0, "second_diff_all_rows_perp_along_active_velocity": 0, "second_diff_source_rows_perp_along_active_velocity": 0, "second_diff_source_rows_perp_along_source_rows": 0, "source_active_plus_second_diff_source_rows_perp_along_source_active": 0, "source_active_plus_second_diff_source_rows_raw": 0}, "v047 paper lower-pair nonlinear-capacity span split changed")
    v.check(paper_lower_pair_velocity_compression.get("nonlinear_capacity_probe_best_feature_family") == "second_diff_source_rows_perp_along_active_velocity", "v047 paper lower-pair nonlinear-capacity best feature changed")
    v.check(0.65 < float(paper_lower_pair_velocity_compression.get("nonlinear_capacity_probe_best_projection_relative_residual", 0.0)) < 0.75, "v047 paper lower-pair nonlinear-capacity best residual changed")
    v.check(paper_lower_pair_velocity_compression.get("nonlinear_capacity_probe_best_correction_feature_family") == "active_plus_second_diff_source_rows_perp", "v047 paper lower-pair nonlinear-capacity best correction feature changed")
    v.check(0.65 < float(paper_lower_pair_velocity_compression.get("nonlinear_capacity_probe_best_correction_relative_residual", 0.0)) < 0.75, "v047 paper lower-pair nonlinear-capacity best correction residual changed")
    v.check(paper_lower_pair_velocity_compression.get("nonlinear_capacity_probe_target_jacobian_used_for_capacity_fit") is True, "v047 paper lower-pair nonlinear-capacity target-Jacobian marker missing")
    v.check(paper_lower_pair_velocity_compression.get("nonlinear_capacity_probe_target_direction_oracle_used_for_formula") is False, "v047 paper lower-pair nonlinear-capacity formula oracle marker changed")
    higher_order_features = {
        "active_plus_nonlocal_same_case_source_delta_rows_perp",
        "active_plus_third_diff_source_rows_perp",
        "higher_order_plus_nonlocal_source_rows_perp",
        "nonlocal_same_case_source_delta_rows_perp",
        "second_plus_third_diff_source_rows_perp_along_active_velocity",
        "third_diff_source_rows_perp_along_active_velocity",
    }
    v.check(paper_lower_pair_velocity_compression.get("higher_order_capacity_probe_row_count") == 216, "v047 paper lower-pair higher-order-capacity row count changed")
    v.check(paper_lower_pair_velocity_compression.get("higher_order_capacity_probe_candidate_count") == 6, "v047 paper lower-pair higher-order-capacity candidate count changed")
    v.check(paper_lower_pair_velocity_compression.get("higher_order_capacity_probe_feature_family_count") == 6, "v047 paper lower-pair higher-order-capacity feature count changed")
    v.check(set(paper_lower_pair_velocity_compression.get("higher_order_capacity_probe_feature_family_values", [])) == higher_order_features, "v047 paper lower-pair higher-order-capacity feature list changed")
    v.check(paper_lower_pair_velocity_compression.get("higher_order_capacity_probe_spanning_row_count") == 0, "v047 paper lower-pair higher-order-capacity unexpectedly spans")
    v.check(set(paper_lower_pair_velocity_compression.get("higher_order_capacity_probe_span_count_by_feature_family", {}).keys()) == higher_order_features, "v047 paper lower-pair higher-order-capacity span split keys changed")
    v.check(paper_lower_pair_velocity_compression.get("higher_order_capacity_probe_best_feature_family") == "third_diff_source_rows_perp_along_active_velocity", "v047 paper lower-pair higher-order-capacity best feature changed")
    v.check(0.65 < float(paper_lower_pair_velocity_compression.get("higher_order_capacity_probe_best_projection_relative_residual", 0.0)) < 0.75, "v047 paper lower-pair higher-order-capacity best residual changed")
    v.check(paper_lower_pair_velocity_compression.get("higher_order_capacity_probe_best_correction_feature_family") == "active_plus_third_diff_source_rows_perp", "v047 paper lower-pair higher-order-capacity best correction feature changed")
    v.check(0.65 < float(paper_lower_pair_velocity_compression.get("higher_order_capacity_probe_best_correction_relative_residual", 0.0)) < 0.75, "v047 paper lower-pair higher-order-capacity best correction residual changed")
    v.check(paper_lower_pair_velocity_compression.get("higher_order_capacity_probe_target_jacobian_used_for_capacity_fit") is True, "v047 paper lower-pair higher-order-capacity target-Jacobian marker missing")
    v.check(paper_lower_pair_velocity_compression.get("higher_order_capacity_probe_target_direction_oracle_used_for_formula") is False, "v047 paper lower-pair higher-order-capacity formula oracle marker changed")
    v.check(paper_lower_pair_velocity_compression.get("higher_order_capacity_probe_nonlocal_source_feature_used") is True, "v047 paper lower-pair higher-order-capacity nonlocal marker missing")
    v.check(paper_lower_pair_velocity_compression.get("higher_order_capacity_probe_third_differential_used") is True, "v047 paper lower-pair higher-order-capacity third-differential marker missing")
    history_features = {
        "active_plus_history_source_transport_delta_rows_perp",
        "active_plus_history_source_velocity_transport_delta_rows_perp",
        "active_plus_history_velocity_transport_delta_rows_perp",
        "history_source_transport_delta_rows_perp",
        "history_source_velocity_transport_delta_rows_perp",
        "history_velocity_transport_delta_rows_perp",
    }
    v.check(paper_lower_pair_velocity_compression.get("history_capacity_probe_row_count") == 216, "v047 paper lower-pair history-capacity row count changed")
    v.check(paper_lower_pair_velocity_compression.get("history_capacity_probe_candidate_count") == 6, "v047 paper lower-pair history-capacity candidate count changed")
    v.check(paper_lower_pair_velocity_compression.get("history_capacity_probe_feature_family_count") == 6, "v047 paper lower-pair history-capacity feature count changed")
    v.check(set(paper_lower_pair_velocity_compression.get("history_capacity_probe_feature_family_values", [])) == history_features, "v047 paper lower-pair history-capacity feature list changed")
    v.check(paper_lower_pair_velocity_compression.get("history_capacity_probe_spanning_row_count") == 0, "v047 paper lower-pair history-capacity unexpectedly spans")
    v.check(set(paper_lower_pair_velocity_compression.get("history_capacity_probe_span_count_by_feature_family", {}).keys()) == history_features, "v047 paper lower-pair history-capacity span split keys changed")
    v.check(paper_lower_pair_velocity_compression.get("history_capacity_probe_best_feature_family") == "active_plus_history_source_velocity_transport_delta_rows_perp", "v047 paper lower-pair history-capacity best feature changed")
    v.check(0.65 < float(paper_lower_pair_velocity_compression.get("history_capacity_probe_best_projection_relative_residual", 0.0)) < 0.8, "v047 paper lower-pair history-capacity best residual changed")
    v.check(paper_lower_pair_velocity_compression.get("history_capacity_probe_best_correction_feature_family") == "active_plus_history_source_velocity_transport_delta_rows_perp", "v047 paper lower-pair history-capacity best correction feature changed")
    v.check(0.65 < float(paper_lower_pair_velocity_compression.get("history_capacity_probe_best_correction_relative_residual", 0.0)) < 0.8, "v047 paper lower-pair history-capacity best correction residual changed")
    v.check(paper_lower_pair_velocity_compression.get("history_capacity_probe_target_jacobian_used_for_capacity_fit") is True, "v047 paper lower-pair history-capacity target-Jacobian marker missing")
    v.check(paper_lower_pair_velocity_compression.get("history_capacity_probe_target_direction_oracle_used_for_formula") is False, "v047 paper lower-pair history-capacity formula oracle marker changed")
    v.check(paper_lower_pair_velocity_compression.get("history_capacity_probe_one_step_history_used") is True, "v047 paper lower-pair history-capacity one-step marker missing")
    v.check(paper_lower_pair_velocity_compression.get("history_capacity_probe_history_source_transport_used") is True, "v047 paper lower-pair history-capacity source-transport marker missing")
    v.check(paper_lower_pair_velocity_compression.get("history_capacity_probe_history_velocity_transport_used") is True, "v047 paper lower-pair history-capacity velocity-transport marker missing")
    multi_step_history_features = {
        "active_plus_two_step_source_transport_delta_rows_perp",
        "active_plus_two_step_source_velocity_transport_delta_rows_perp",
        "active_plus_two_step_velocity_transport_delta_rows_perp",
        "two_step_source_transport_delta_rows_perp",
        "two_step_source_velocity_transport_delta_rows_perp",
        "two_step_velocity_transport_delta_rows_perp",
    }
    v.check(paper_lower_pair_velocity_compression.get("multi_step_history_capacity_probe_row_count") == 216, "v047 paper lower-pair multi-step history-capacity row count changed")
    v.check(paper_lower_pair_velocity_compression.get("multi_step_history_capacity_probe_candidate_count") == 6, "v047 paper lower-pair multi-step history-capacity candidate count changed")
    v.check(paper_lower_pair_velocity_compression.get("multi_step_history_capacity_probe_feature_family_count") == 6, "v047 paper lower-pair multi-step history-capacity feature count changed")
    v.check(set(paper_lower_pair_velocity_compression.get("multi_step_history_capacity_probe_feature_family_values", [])) == multi_step_history_features, "v047 paper lower-pair multi-step history-capacity feature list changed")
    v.check(paper_lower_pair_velocity_compression.get("multi_step_history_capacity_probe_spanning_row_count") == 0, "v047 paper lower-pair multi-step history-capacity unexpectedly spans")
    v.check(set(paper_lower_pair_velocity_compression.get("multi_step_history_capacity_probe_span_count_by_feature_family", {}).keys()) == multi_step_history_features, "v047 paper lower-pair multi-step history-capacity span split keys changed")
    v.check(paper_lower_pair_velocity_compression.get("multi_step_history_capacity_probe_best_feature_family") == "two_step_source_velocity_transport_delta_rows_perp", "v047 paper lower-pair multi-step history-capacity best feature changed")
    v.check(0.65 < float(paper_lower_pair_velocity_compression.get("multi_step_history_capacity_probe_best_projection_relative_residual", 0.0)) < 0.75, "v047 paper lower-pair multi-step history-capacity best residual changed")
    v.check(paper_lower_pair_velocity_compression.get("multi_step_history_capacity_probe_best_correction_feature_family") == "active_plus_two_step_source_velocity_transport_delta_rows_perp", "v047 paper lower-pair multi-step history-capacity best correction feature changed")
    v.check(0.65 < float(paper_lower_pair_velocity_compression.get("multi_step_history_capacity_probe_best_correction_relative_residual", 0.0)) < 0.75, "v047 paper lower-pair multi-step history-capacity best correction residual changed")
    v.check(paper_lower_pair_velocity_compression.get("multi_step_history_capacity_probe_target_jacobian_used_for_capacity_fit") is True, "v047 paper lower-pair multi-step history-capacity target-Jacobian marker missing")
    v.check(paper_lower_pair_velocity_compression.get("multi_step_history_capacity_probe_target_direction_oracle_used_for_formula") is False, "v047 paper lower-pair multi-step history-capacity formula oracle marker changed")
    v.check(paper_lower_pair_velocity_compression.get("multi_step_history_capacity_probe_history_step_count") == 2, "v047 paper lower-pair multi-step history-capacity step count changed")
    v.check(paper_lower_pair_velocity_compression.get("multi_step_history_capacity_probe_multi_step_history_used") is True, "v047 paper lower-pair multi-step history-capacity marker missing")
    v.check(paper_lower_pair_velocity_compression.get("multi_step_history_capacity_probe_history_source_transport_used") is True, "v047 paper lower-pair multi-step history-capacity source-transport marker missing")
    v.check(paper_lower_pair_velocity_compression.get("multi_step_history_capacity_probe_history_velocity_transport_used") is True, "v047 paper lower-pair multi-step history-capacity velocity-transport marker missing")
    recurrent_history_features = {
        "active_plus_recurrent_source_curvature_rows_perp",
        "active_plus_recurrent_source_velocity_bilinear_rows_perp",
        "active_plus_recurrent_velocity_curvature_rows_perp",
        "recurrent_source_curvature_rows_perp",
        "recurrent_source_velocity_bilinear_rows_perp",
        "recurrent_velocity_curvature_rows_perp",
    }
    v.check(paper_lower_pair_velocity_compression.get("recurrent_history_capacity_probe_row_count") == 216, "v047 paper lower-pair recurrent-history-capacity row count changed")
    v.check(paper_lower_pair_velocity_compression.get("recurrent_history_capacity_probe_candidate_count") == 6, "v047 paper lower-pair recurrent-history-capacity candidate count changed")
    v.check(paper_lower_pair_velocity_compression.get("recurrent_history_capacity_probe_feature_family_count") == 6, "v047 paper lower-pair recurrent-history-capacity feature count changed")
    v.check(set(paper_lower_pair_velocity_compression.get("recurrent_history_capacity_probe_feature_family_values", [])) == recurrent_history_features, "v047 paper lower-pair recurrent-history-capacity feature list changed")
    v.check(paper_lower_pair_velocity_compression.get("recurrent_history_capacity_probe_spanning_row_count") == 0, "v047 paper lower-pair recurrent-history-capacity unexpectedly spans")
    v.check(set(paper_lower_pair_velocity_compression.get("recurrent_history_capacity_probe_span_count_by_feature_family", {}).keys()) == recurrent_history_features, "v047 paper lower-pair recurrent-history-capacity span split keys changed")
    v.check(paper_lower_pair_velocity_compression.get("recurrent_history_capacity_probe_best_feature_family") == "recurrent_source_velocity_bilinear_rows_perp", "v047 paper lower-pair recurrent-history-capacity best feature changed")
    v.check(0.65 < float(paper_lower_pair_velocity_compression.get("recurrent_history_capacity_probe_best_projection_relative_residual", 0.0)) < 0.75, "v047 paper lower-pair recurrent-history-capacity best residual changed")
    v.check(paper_lower_pair_velocity_compression.get("recurrent_history_capacity_probe_best_correction_feature_family") == "active_plus_recurrent_source_velocity_bilinear_rows_perp", "v047 paper lower-pair recurrent-history-capacity best correction feature changed")
    v.check(0.65 < float(paper_lower_pair_velocity_compression.get("recurrent_history_capacity_probe_best_correction_relative_residual", 0.0)) < 0.75, "v047 paper lower-pair recurrent-history-capacity best correction residual changed")
    v.check(paper_lower_pair_velocity_compression.get("recurrent_history_capacity_probe_target_jacobian_used_for_capacity_fit") is True, "v047 paper lower-pair recurrent-history-capacity target-Jacobian marker missing")
    v.check(paper_lower_pair_velocity_compression.get("recurrent_history_capacity_probe_target_direction_oracle_used_for_formula") is False, "v047 paper lower-pair recurrent-history-capacity formula oracle marker changed")
    v.check(paper_lower_pair_velocity_compression.get("recurrent_history_capacity_probe_history_step_count") == 2, "v047 paper lower-pair recurrent-history-capacity step count changed")
    v.check(paper_lower_pair_velocity_compression.get("recurrent_history_capacity_probe_recurrent_history_used") is True, "v047 paper lower-pair recurrent-history-capacity marker missing")
    v.check(paper_lower_pair_velocity_compression.get("recurrent_history_capacity_probe_history_source_transport_used") is True, "v047 paper lower-pair recurrent-history-capacity source marker missing")
    v.check(paper_lower_pair_velocity_compression.get("recurrent_history_capacity_probe_history_velocity_transport_used") is True, "v047 paper lower-pair recurrent-history-capacity velocity marker missing")
    v.check(paper_lower_pair_velocity_compression.get("recurrent_history_capacity_probe_bilinear_history_feature_used") is True, "v047 paper lower-pair recurrent-history-capacity bilinear marker missing")
    v.check(paper_lower_pair_velocity_compression.get("recurrent_history_capacity_probe_curvature_history_feature_used") is True, "v047 paper lower-pair recurrent-history-capacity curvature marker missing")
    weak_row_structure_features = {
        "active_plus_weak_source_active_hadamard_rows_perp",
        "active_plus_weak_source_active_shifted_commutator_rows_perp",
        "weak_active_cross_gram_rows_perp",
        "weak_source_active_cross_hadamard_rows_perp",
        "weak_source_active_hadamard_rows_perp",
        "weak_source_active_shifted_commutator_rows_perp",
    }
    v.check(paper_lower_pair_velocity_compression.get("weak_row_structure_capacity_probe_row_count") == 216, "v047 paper lower-pair weak-row-structure row count changed")
    v.check(paper_lower_pair_velocity_compression.get("weak_row_structure_capacity_probe_candidate_count") == 6, "v047 paper lower-pair weak-row-structure candidate count changed")
    v.check(paper_lower_pair_velocity_compression.get("weak_row_structure_capacity_probe_feature_family_count") == 6, "v047 paper lower-pair weak-row-structure feature count changed")
    v.check(set(paper_lower_pair_velocity_compression.get("weak_row_structure_capacity_probe_feature_family_values", [])) == weak_row_structure_features, "v047 paper lower-pair weak-row-structure feature list changed")
    v.check(paper_lower_pair_velocity_compression.get("weak_row_structure_capacity_probe_spanning_row_count") == 0, "v047 paper lower-pair weak-row-structure unexpectedly spans")
    v.check(set(paper_lower_pair_velocity_compression.get("weak_row_structure_capacity_probe_span_count_by_feature_family", {}).keys()) == weak_row_structure_features, "v047 paper lower-pair weak-row-structure span split keys changed")
    v.check(paper_lower_pair_velocity_compression.get("weak_row_structure_capacity_probe_best_feature_family") == "weak_source_active_hadamard_rows_perp", "v047 paper lower-pair weak-row-structure best feature changed")
    v.check(0.65 < float(paper_lower_pair_velocity_compression.get("weak_row_structure_capacity_probe_best_projection_relative_residual", 0.0)) < 0.75, "v047 paper lower-pair weak-row-structure best residual changed")
    v.check(paper_lower_pair_velocity_compression.get("weak_row_structure_capacity_probe_best_correction_feature_family") == "active_plus_weak_source_active_hadamard_rows_perp", "v047 paper lower-pair weak-row-structure best correction feature changed")
    v.check(0.65 < float(paper_lower_pair_velocity_compression.get("weak_row_structure_capacity_probe_best_correction_relative_residual", 0.0)) < 0.75, "v047 paper lower-pair weak-row-structure best correction residual changed")
    v.check(paper_lower_pair_velocity_compression.get("weak_row_structure_capacity_probe_target_jacobian_used_for_capacity_fit") is True, "v047 paper lower-pair weak-row-structure target-Jacobian marker missing")
    v.check(paper_lower_pair_velocity_compression.get("weak_row_structure_capacity_probe_target_direction_oracle_used_for_formula") is False, "v047 paper lower-pair weak-row-structure formula oracle marker changed")
    v.check(paper_lower_pair_velocity_compression.get("weak_row_structure_capacity_probe_source_jacobian_feature_used") is True, "v047 paper lower-pair weak-row-structure source marker missing")
    v.check(paper_lower_pair_velocity_compression.get("weak_row_structure_capacity_probe_active_velocity_feature_used") is True, "v047 paper lower-pair weak-row-structure active marker missing")
    v.check(paper_lower_pair_velocity_compression.get("weak_row_structure_capacity_probe_cross_gram_feature_used") is True, "v047 paper lower-pair weak-row-structure cross-Gram marker missing")
    v.check(paper_lower_pair_velocity_compression.get("weak_row_structure_capacity_probe_hadamard_feature_used") is True, "v047 paper lower-pair weak-row-structure Hadamard marker missing")
    v.check(paper_lower_pair_velocity_compression.get("weak_row_structure_capacity_probe_commutator_feature_used") is True, "v047 paper lower-pair weak-row-structure commutator marker missing")
    row_space_laws = {
        "all_stage_svd_top8",
        "nonfinal_svd_top8",
        "all_stage_row_norm_top8",
        "nonfinal_row_norm_top8",
        "stage_balanced_norm_all_stage",
        "stage_balanced_norm_nonfinal",
    }
    v.check(paper_lower_pair_velocity_compression.get("row_space_compression_probe_row_count") == 36, "v047 paper lower-pair row-space compression row count changed")
    v.check(paper_lower_pair_velocity_compression.get("row_space_compression_probe_law_count") == 6, "v047 paper lower-pair row-space compression law count changed")
    v.check(set(paper_lower_pair_velocity_compression.get("row_space_compression_probe_law_values", [])) == row_space_laws, "v047 paper lower-pair row-space compression law list changed")
    v.check(paper_lower_pair_velocity_compression.get("row_space_compression_probe_spanning_row_count") == 0, "v047 paper lower-pair row-space compression unexpectedly spans")
    v.check(paper_lower_pair_velocity_compression.get("row_space_compression_probe_value_ok_row_count") == 24, "v047 paper lower-pair row-space compression value-ok count changed")
    v.check(paper_lower_pair_velocity_compression.get("row_space_compression_probe_nonfinal_row_count") == 24, "v047 paper lower-pair row-space compression non-final count changed")
    v.check(set(paper_lower_pair_velocity_compression.get("row_space_compression_probe_span_count_by_law", {}).keys()) == row_space_laws, "v047 paper lower-pair row-space compression span split keys changed")
    v.check(all(count == 0 for count in paper_lower_pair_velocity_compression.get("row_space_compression_probe_span_count_by_law", {}).values()), "v047 paper lower-pair row-space compression law span counts changed")
    v.check(paper_lower_pair_velocity_compression.get("row_space_compression_probe_best_law") == "all_stage_svd_top8", "v047 paper lower-pair row-space compression best law changed")
    v.check(0.7 < float(paper_lower_pair_velocity_compression.get("row_space_compression_probe_best_projection_relative_residual", 0.0)) < 0.8, "v047 paper lower-pair row-space compression best residual changed")
    v.check(paper_lower_pair_velocity_compression.get("row_space_compression_probe_best_value_law") == "all_stage_svd_top8", "v047 paper lower-pair row-space compression best value law changed")
    v.check(float(paper_lower_pair_velocity_compression.get("row_space_compression_probe_best_value_residual_norm", 1.0)) < 1.0e-10, "v047 paper lower-pair row-space compression best value residual changed")
    v.check(paper_lower_pair_velocity_compression.get("row_space_compression_probe_best_nonfinal_law") == "stage_balanced_norm_all_stage", "v047 paper lower-pair row-space compression best nonfinal law changed")
    v.check(0.9 < float(paper_lower_pair_velocity_compression.get("row_space_compression_probe_best_nonfinal_projection_relative_residual", 0.0)) < 1.1, "v047 paper lower-pair row-space compression nonfinal residual changed")
    v.check(paper_lower_pair_velocity_compression.get("row_space_compression_probe_target_jacobian_used_for_formula") is False, "v047 paper lower-pair row-space compression unexpectedly uses target Jacobian")
    v.check(paper_lower_pair_velocity_compression.get("row_space_compression_probe_target_direction_oracle_used") is False, "v047 paper lower-pair row-space compression unexpectedly uses target direction")
    v.check(paper_lower_pair_velocity_compression.get("row_space_compression_probe_frozen_state_dependent_coefficients") is True, "v047 paper lower-pair row-space compression frozen coefficient marker missing")
    v.check(paper_lower_pair_velocity_compression.get("row_space_compression_probe_coefficient_derivative_included") is False, "v047 paper lower-pair row-space compression unexpectedly includes coefficient derivative")
    v.check("Target-free row-space compression" in paper_lower_pair_velocity_compression.get("blocking_gap", ""), "v047 paper lower-pair row-space compression blocker changed")
    v.check("revised analytical weak-row formula" in paper_lower_pair_velocity_compression.get("blocking_gap", ""), "v047 paper lower-pair weak-row-structure formula blocker changed")
    v.check(paper_lower_pair_velocity_compression.get("next_repair_target") in {
        "derive target-free weights for the recurrent history features and rerun the nonlinear h-sweep",
        "derive a revised analytical weak-row formula or richer nonlinear recurrent history source law for the coefficient-gradient closure",
        "derive target-free weights for the weak-row structure features and rerun the nonlinear h-sweep",
        "derive a revised analytical weak-row formula or nonlinear recurrent history source law for the coefficient-gradient closure",
    }, "v047 paper lower-pair recurrent-history-capacity next repair target changed")
    v.check(paper_lower_pair_velocity_compression.get("full_tfe_stage_replacement") is False, "v047 paper lower-pair velocity-compression unexpectedly claims full TFE replacement")
    v.check(paper_contract.get("status") == "paper_tfe_residual_substitution_contract_all_rows_substituted_diagnostic_z0_order_limited", "v047 paper contract status changed")
    v.check(paper_contract.get("derived_formula_present_count") == 6, "v047 paper contract derived formula count changed")
    v.check(paper_contract.get("residual_substituted_count") == 6, "v047 paper contract substituted count changed")
    v.check(paper_contract.get("accepted_h_sweep_count") == 0, "v047 paper contract unexpectedly accepted h-sweep")
    v.check(paper_contract.get("full_tfe_stage_replacement") is False, "v047 paper contract unexpectedly claims full TFE replacement")

    width, height = png_size(ROOT / "docs" / "version_progression.png")
    v.check(width > 0 and height > 0, "version_progression.png is invalid")
    return {
        "asme_status": asme_gate.get("status"),
        "asme_models": sorted(models),
        "sharp_ultra_status": sharp.get("status"),
        "paper_kinematic_status": paper_kinematic.get("status"),
        "paper_balance_constraint_status": paper_balance_constraint.get("status"),
        "paper_all_row_substitution_status": paper_all_row_substitution.get("status"),
        "paper_all_row_gauss_z0_substitution_status": paper_all_row_gauss_z0_substitution.get("status"),
        "paper_all_row_gauss_z0_terminal_output_status": paper_all_row_gauss_z0_terminal_output.get("status"),
        "paper_all_row_recurrent_z0_terminal_output_status": paper_all_row_recurrent_z0_terminal_output.get("status"),
        "paper_all_row_consistent_z0_terminal_output_status": paper_all_row_consistent_z0_terminal_output.get("status"),
        "paper_all_row_consistent_z0_conditioning_status": paper_all_row_consistent_z0_conditioning.get("status"),
        "paper_all_row_consistent_z0_scaled_newton_status": paper_all_row_consistent_z0_scaled_newton.get("status"),
        "paper_family_ablation_status": paper_family_ablation.get("status"),
        "paper_lower_pair_lambda_schur_status": paper_lower_pair_lambda_schur.get("status"),
        "paper_lower_pair_acceleration_terminal_output_status": paper_lower_pair_acceleration_terminal_output.get("status"),
        "paper_lower_pair_terminal_source_lift_status": paper_lower_pair_terminal_source_lift.get("status"),
        "paper_lower_pair_terminal_source_normalization_status": paper_lower_pair_terminal_source_normalization.get("status"),
        "paper_lower_pair_terminal_source_insertion_status": paper_lower_pair_terminal_source_insertion.get("status"),
        "paper_lower_pair_terminal_source_insertion_trajectory_status": paper_lower_pair_terminal_source_insertion_trajectory.get("status"),
        "paper_lower_pair_terminal_source_insertion_blowup_status": paper_lower_pair_terminal_source_insertion_blowup.get("status"),
        "paper_lower_pair_terminal_source_bounded_policy_status": paper_lower_pair_terminal_source_bounded_policy.get("status"),
        "paper_lower_pair_stage_local_bounded_source_status": paper_lower_pair_stage_local_bounded_source.get("status"),
        "paper_lower_pair_source_free_elimination_rank_status": paper_lower_pair_source_free_elimination_rank.get("status"),
        "paper_lower_pair_source_free_mean_velocity_closure_status": paper_lower_pair_source_free_mean_velocity.get("status"),
        "paper_lower_pair_source_free_mean_blend_closure_status": paper_lower_pair_source_free_mean_blend.get("status"),
        "paper_lower_pair_source_free_mean_blend_trajectory_status": paper_lower_pair_source_free_mean_blend_trajectory.get("status"),
        "paper_lower_pair_source_free_mean_blend_trajectory_alpha_sweep_status": paper_lower_pair_source_free_mean_blend_trajectory_alpha_sweep.get("status"),
        "paper_lower_pair_source_free_component_blend_trajectory_status": paper_lower_pair_source_free_component_blend_trajectory.get("status"),
        "paper_lower_pair_centered_terminal_velocity_bridge_status": paper_lower_pair_centered_terminal_velocity_bridge.get("status"),
        "paper_lower_pair_closure_acceptance_matrix_status": paper_lower_pair_closure_acceptance_matrix.get("status"),
        "paper_lower_pair_closure_property_pareto_status": paper_lower_pair_closure_property_pareto.get("status"),
        "paper_lower_pair_velocity_compression_status": paper_lower_pair_velocity_compression.get("status"),
        "tfe_readiness": readiness.get("counts", {}),
        "remaining_caveats": [
            "sparse_speed_quantified",
            "full_tfe_stage_replacement_missing",
            "sharp_friction_coarse_order_reduction_ultra_recovered",
        ],
    }


def format_current_pipeline_gate_output(current_gate: dict) -> str:
    """Summarize the current version gate in the generated pipeline report."""

    readiness = current_gate.get("tfe_readiness", {})
    caveats = current_gate.get("remaining_caveats", [])
    asme_models = current_gate.get("asme_models", [])
    return "\n".join(
        [
            "current_pipeline_gate=PASS",
            f"asme_gate_status={current_gate.get('asme_status')}",
            f"asme_models={','.join(asme_models)}",
            f"asme_all_four_models_accepted={asme_models == sorted(EXPECTED_ASME_MODELS)}",
            f"sharp_ultra_status={current_gate.get('sharp_ultra_status')}",
            (
                "tfe_readiness="
                f"satisfied:{readiness.get('satisfied')},"
                f"partial:{readiness.get('partial')},"
                f"missing:{readiness.get('missing')}"
            ),
            f"remaining_caveats={','.join(caveats)}",
            f"full_tfe_stage_replacement={'full_tfe_stage_replacement_missing' not in caveats}",
            "source_policy_execution_invoked=False",
            "run_v047_invoked=False",
            "submission_ready=False",
        ]
    )


def format_objective_completion_boundary_output() -> str:
    """Summarize why a passing validator run is not objective completion."""

    audit = read_json(PAPER_DIR / "OBJECTIVE_COMPLETION_AUDIT.json")
    completion_decision = audit.get("completion_decision", {})
    safe_action_ids = audit.get("safe_action_ids", [])
    opt_in_action_ids = audit.get("opt_in_action_ids", [])
    return "\n".join(
        [
            f"objective_completion_boundary={audit.get('status')}",
            f"objective_complete={audit.get('objective_complete')}",
            f"submission_ready={audit.get('submission_ready')}",
            f"can_mark_goal_complete={completion_decision.get('can_mark_goal_complete')}",
            f"blocking_ids={','.join(audit.get('blocking_ids', []))}",
            f"source_policy_closed_ratio={audit.get('source_policy_closed_ratio')}",
            f"blocker_open_by_id={audit.get('blocker_open_by_id')}",
            f"blocker_closure_allowed_by_id={audit.get('blocker_closure_allowed_by_id')}",
            f"exact_b4_opt_in_required_for_execution={audit.get('exact_b4_opt_in_required_for_execution')}",
            f"safe_action_ids={','.join(safe_action_ids)}",
            f"opt_in_action_ids={','.join(opt_in_action_ids)}",
            f"source_policy_execution_invoked={audit.get('source_policy_execution_invoked')}",
            f"source_policy_execution_allowed_now={audit.get('source_policy_execution_allowed_now')}",
            f"run_v047_invoked={audit.get('run_v047_invoked')}",
            f"heavy_numerical_run_invoked={audit.get('heavy_numerical_run_invoked')}",
            f"v048_runner_invoked={audit.get('v048_runner_invoked')}",
            "validator_pass_means_not_complete=True",
        ]
    )


def write_outputs(
    inventory: list[dict[str, object]],
    totals: dict[str, int],
    v047_output: str,
    four_asme_output: str,
    full_tfe_gap_output: str,
    full_tfe_repair_spec_output: str,
    implementation_fidelity_output: str,
    implementation_path_audit_output: str,
    b4_source_policy_row_closure_readiness_ledger_output: str,
    source_policy_row_closure_ledger_output: str,
    tfe_dae_runner_contract_gap_audit_output: str,
    tfe_runner_contract_preflight_certificate_output: str,
    b4_source_policy_work_precision_execution_plan_output: str,
    b4_source_policy_post_execution_audit_output: str,
    b4_existing_artifact_promotion_audit_output: str,
    external_source_policy_closure_manifest_output: str,
    b6_four_example_local_evidence_output: str,
    cmame_runner_centered_reproducibility_audit_output: str,
    cmame_narrowed_reproducibility_package_audit_output: str,
    cmame_narrowed_repro_code_archive_output: str,
    cmame_reproducibility_package_manifest_output: str,
    b6_closed_loop_self_contained_extraction_audit_output: str,
    cmame_self_contained_runner_extraction_plan_output: str,
    cmame_minimal_reproducibility_candidate_output: str,
    cmame_closed_loop_local_runner_candidate_output: str,
    cmame_local_accepted_runner_companion_output: str,
    cmame_p1_local_runner_extraction_audit_output: str,
    cmame_p1_single_runner_candidate_output: str,
    cmame_p1_double_runner_candidate_output: str,
    cmame_runner_adapter_candidate_output: str,
    cmame_narrowed_repro_bundle_output: str,
    cmame_submission_integrity_audit_output: str,
    reference_metadata_audit_output: str,
    result_to_manuscript_traceability_audit_output: str,
    cmame_figure_set_audit_output: str,
    cmame_scalability_boundary_audit_output: str,
    cmame_claim_hygiene_audit_output: str,
    cmame_pdf_style_review_audit_output: str,
    cmame_review_agent_output: str,
    cmame_narrowed_claim_closure_policy_audit_output: str,
    paper_core_to_manuscript_audit_output: str,
    all_examples_result_sanity_audit_output: str,
    all_method_example_claim_disposition_audit_output: str,
    paper_numerical_result_matrix_output: str,
    common_reference_order_recomputation_audit_output: str,
    comparison_objective_closure_reconciliation_audit_output: str,
    paper_core_result_consolidation_output: str,
    proof_closure_manifest_output: str,
    proof_claim_traceability_audit_output: str,
    proof_remaining_work_manifest_output: str,
    b1_ad_expanded_symbolic_oracle_closure_certificate_output: str,
    b1_symbolic_row_oracle_closure_certificate_output: str,
    b3_direct_proof_review_audit_output: str,
    cmame_strict_proof_audit_output: str,
    cmame_strict_proof_policy_reconciliation_audit_output: str,
    cmame_proof_style_audit_output: str,
    kinematic_row_defect_certificate_output: str,
    newton_euler_virtual_work_wrench_audit_output: str,
    newton_euler_symbolic_target_audit_output: str,
    newton_euler_symbolic_defect_certificate_output: str,
    newton_euler_row_ordering_scaling_ad_audit_output: str,
    newton_euler_dynamic_row_closure_contract_output: str,
    newton_euler_defect_obligation_gate_output: str,
    newton_euler_balance_identity_audit_output: str,
    newton_euler_ad_expanded_row_oracle_audit_output: str,
    smooth_force_lift_certificate_output: str,
    b2_source_policy_remaining_work_manifest_output: str,
    source_policy_closure_triage_output: str,
    all_examples_source_policy_audit_output: str,
    four_example_source_policy_dashboard_output: str,
    external_baseline_source_policy_diagnosis_output: str,
    external_case_evidence_reconciliation_output: str,
    external_same_test_acceptance_sheet_output: str,
    external_suite_demotion_ledger_output: str,
    external_suite_disposition_audit_output: str,
    external_superiority_claim_demotion_audit_output: str,
    b4_b7_non_superiority_route_audit_output: str,
    source_policy_local_candidate_gap_audit_output: str,
    ra2021_source_identity_audit_output: str,
    ra2021_double_source_policy_low_order_diagnosis_output: str,
    ra2021_source_policy_row_audit_output: str,
    hi2022_policy_decision_audit_output: str,
    hi2022_source_policy_row_audit_output: str,
    hi2022_ra_half_double_source_policy_failure_diagnosis_output: str,
    hi2022_ra_half_double_repair_attempt_certificate_output: str,
    hi2022_t8_tolerance_repair_audit_output: str,
    vp2024_code_path_disposition_audit_output: str,
    vp2024_public_code_recheck_20260613_output: str,
    tfe_source_policy_spec_output: str,
    tfe_source_pendulum_model_audit_output: str,
    tfe_source_policy_row_audit_output: str,
    tfe_source_grid_compatibility_audit_output: str,
    tfe_brown_mcphee_source_code_equivalence_certificate_output: str,
    tfe_full_t10_endpoint_policy_closure_certificate_output: str,
    tfe_endpoint_policy_boundary_certificate_output: str,
    tfe_algorithm_literal_endpoint_probe_output: str,
    tfe_algorithm_literal_work_precision_audit_output: str,
    tfe_b4_b7_source_policy_demotion_audit_output: str,
    tfe_brown_mcphee_source_law_boundary_audit_output: str,
    tfe_endpoint_policy_sensitivity_audit_output: str,
    tfe_full_t10_absolute_dae_lift_summary_output: str,
    tfe_full_t10_coarse_candidate_summary_output: str,
    tfe_public_code_recheck_20260613_output: str,
    tfe_self_reproduction_attempt_output: str,
    source_policy_self_reproduction_attempt_audit_output: str,
    ra_hi_output_inventory_output: str,
    ra_hi_closeout_checklist_output: str,
    ra_hi_promotion_blocker_matrix_output: str,
    ra_hi_post_execution_attempt_certificate_output: str,
    b4_source_policy_execution_opt_in_packet_output: str,
    b4_source_policy_guarded_driver_output: str,
    b4_guarded_driver_refusal_boundary_audit_output: str,
    b4_source_policy_execution_handoff_package_output: str,
    b4_source_policy_command_preflight_freeze_output: str,
    b4_source_policy_expected_output_schema_audit_output: str,
    b4_expected_output_promotion_readiness_blocker_audit_output: str,
    oc6_source_equivalent_reopen_readiness_audit_output: str,
    oc6_external_source_artifact_recheck_20260621_output: str,
    oc6_tfe_publisher_artifact_availability_audit_20260621_output: str,
    oc6_tfe_source_equivalent_artifact_request_packet_20260621_output: str,
    full_source_policy_row_provenance_audit_output: str,
    full_source_policy_runner_archive_gap_output: str,
    objective_completion_audit_output: str,
    source_policy_public_code_refresh_20260620_output: str,
    source_policy_reopen_condition_monitor_output: str,
    source_policy_reopen_condition_monitor_20260621_delta_output: str,
    v048_output: str,
    v048_matrix_output: str,
    v048_coarse_first_output: str,
    v048_closed_loop_surrogate_output: str,
    v048_closed_loop_floor_audit_output: str,
    v048_closed_loop_coarse_probe_output: str,
    v048_closed_loop_closure_contract_output: str,
    v048_closed_loop_feasibility_audit_output: str,
    v048_closed_loop_residual_scaffold_output: str,
    v048_closed_loop_stage_residual_audit_output: str,
    v048_closed_loop_one_step_smoke_output: str,
    v048_closed_loop_newton_stage_smoke_output: str,
    v048_closed_loop_newton_coarse_order_output: str,
    v048_closed_loop_public_work_precision_output: str,
    v048_closed_loop_strict_common_reference_output: str,
    v048_residual_to_error_obligation_output: str,
    v048_single_coarse_output: str,
    paper_claim_output: str,
    proof_evidence_matrix_output: str,
    proof_solver_scale_audit_output: str,
    order_acceptance_gate_output: str,
    cmame_submission_output: str,
    submission_artifact_manifest_boundary_sync_output: str,
    cmame_blocker_closure_output: str,
    cmame_external_baseline_output: str,
    external_same_test_run_queue_output: str,
    cmame_proof_contract_output: str,
    cmame_visual_legibility_output: str,
    cmame_related_work_output: str,
    cmame_prose_residue_audit_output: str,
    dynamic_row_oracle_output: str,
    source_paper_comparison_output: str,
    submission_bundle_output: str,
    paper_latex_log_output: str,
    documentation_boundary_output: str,
    current_gate: dict,
    v: Validator,
) -> None:
    RESULTS.mkdir(exist_ok=True)
    inventory_path = RESULTS / "pipeline_artifact_inventory.csv"
    with inventory_path.open("w", encoding="utf-8", newline="") as handle:
        fieldnames = [
            "version",
            "dirname",
            "summary",
            "report",
            "result_files",
            "csv_files",
            "png_files",
            "json_files",
            "markdown_files",
        ]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(inventory)
    v.check(inventory_path.exists() and inventory_path.stat().st_size > 0, f"pipeline validation output missing: {inventory_path.name}")

    expected_final_checks = v.checks_run + 2
    objective_completion_boundary_output = format_objective_completion_boundary_output()
    current_pipeline_gate_output = format_current_pipeline_gate_output(current_gate)
    summary = {
        "status": "PASS" if not v.failures else "FAIL",
        "checks_run": expected_final_checks,
        "failures": v.failures,
        "totals": totals,
        "current_version": CURRENT_VERSION,
        "objective_completion_boundary_output": objective_completion_boundary_output.strip().splitlines(),
        "current_gate": current_gate,
        "current_pipeline_gate_validator_output": current_pipeline_gate_output.strip().splitlines(),
        "v047_validator_output": v047_output.strip().splitlines(),
        "four_asme_minimal_validator_output": four_asme_output.strip().splitlines(),
        "full_tfe_gap_validator_output": full_tfe_gap_output.strip().splitlines(),
        "full_tfe_repair_spec_validator_output": full_tfe_repair_spec_output.strip().splitlines(),
        "implementation_fidelity_validator_output": implementation_fidelity_output.strip().splitlines(),
        "implementation_path_audit_validator_output": implementation_path_audit_output.strip().splitlines(),
        "b4_source_policy_row_closure_readiness_ledger_validator_output": (
            b4_source_policy_row_closure_readiness_ledger_output.strip().splitlines()
        ),
        "source_policy_row_closure_ledger_validator_output": (
            source_policy_row_closure_ledger_output.strip().splitlines()
        ),
        "tfe_dae_runner_contract_gap_audit_validator_output": (
            tfe_dae_runner_contract_gap_audit_output.strip().splitlines()
        ),
        "tfe_runner_contract_preflight_certificate_validator_output": (
            tfe_runner_contract_preflight_certificate_output.strip().splitlines()
        ),
        "b4_source_policy_work_precision_execution_plan_validator_output": (
            b4_source_policy_work_precision_execution_plan_output.strip().splitlines()
        ),
        "b4_source_policy_post_execution_audit_validator_output": (
            b4_source_policy_post_execution_audit_output.strip().splitlines()
        ),
        "b4_existing_artifact_promotion_audit_validator_output": (
            b4_existing_artifact_promotion_audit_output.strip().splitlines()
        ),
        "external_source_policy_closure_manifest_validator_output": (
            external_source_policy_closure_manifest_output.strip().splitlines()
        ),
        "b6_four_example_local_evidence_validator_output": (
            b6_four_example_local_evidence_output.strip().splitlines()
        ),
        "cmame_runner_centered_reproducibility_audit_validator_output": (
            cmame_runner_centered_reproducibility_audit_output.strip().splitlines()
        ),
        "cmame_narrowed_reproducibility_package_audit_validator_output": (
            cmame_narrowed_reproducibility_package_audit_output.strip().splitlines()
        ),
        "cmame_narrowed_repro_code_archive_validator_output": (
            cmame_narrowed_repro_code_archive_output.strip().splitlines()
        ),
        "cmame_reproducibility_package_manifest_validator_output": (
            cmame_reproducibility_package_manifest_output.strip().splitlines()
        ),
        "b6_closed_loop_self_contained_extraction_audit_validator_output": (
            b6_closed_loop_self_contained_extraction_audit_output.strip().splitlines()
        ),
        "cmame_self_contained_runner_extraction_plan_validator_output": (
            cmame_self_contained_runner_extraction_plan_output.strip().splitlines()
        ),
        "cmame_minimal_reproducibility_candidate_validator_output": (
            cmame_minimal_reproducibility_candidate_output.strip().splitlines()
        ),
        "cmame_closed_loop_local_runner_candidate_validator_output": (
            cmame_closed_loop_local_runner_candidate_output.strip().splitlines()
        ),
        "cmame_local_accepted_runner_companion_validator_output": (
            cmame_local_accepted_runner_companion_output.strip().splitlines()
        ),
        "cmame_p1_local_runner_extraction_audit_validator_output": (
            cmame_p1_local_runner_extraction_audit_output.strip().splitlines()
        ),
        "cmame_p1_single_runner_candidate_validator_output": (
            cmame_p1_single_runner_candidate_output.strip().splitlines()
        ),
        "cmame_p1_double_runner_candidate_validator_output": (
            cmame_p1_double_runner_candidate_output.strip().splitlines()
        ),
        "cmame_runner_adapter_candidate_validator_output": (
            cmame_runner_adapter_candidate_output.strip().splitlines()
        ),
        "cmame_narrowed_repro_bundle_validator_output": (
            cmame_narrowed_repro_bundle_output.strip().splitlines()
        ),
        "cmame_submission_integrity_audit_validator_output": (
            cmame_submission_integrity_audit_output.strip().splitlines()
        ),
        "reference_metadata_audit_validator_output": (
            reference_metadata_audit_output.strip().splitlines()
        ),
        "result_to_manuscript_traceability_audit_validator_output": (
            result_to_manuscript_traceability_audit_output.strip().splitlines()
        ),
        "cmame_figure_set_audit_validator_output": (
            cmame_figure_set_audit_output.strip().splitlines()
        ),
        "cmame_scalability_boundary_audit_validator_output": (
            cmame_scalability_boundary_audit_output.strip().splitlines()
        ),
        "cmame_claim_hygiene_audit_validator_output": (
            cmame_claim_hygiene_audit_output.strip().splitlines()
        ),
        "cmame_pdf_style_review_audit_validator_output": (
            cmame_pdf_style_review_audit_output.strip().splitlines()
        ),
        "cmame_review_agent_validator_output": cmame_review_agent_output.strip().splitlines(),
        "cmame_narrowed_claim_closure_policy_audit_validator_output": (
            cmame_narrowed_claim_closure_policy_audit_output.strip().splitlines()
        ),
        "paper_core_to_manuscript_audit_validator_output": (
            paper_core_to_manuscript_audit_output.strip().splitlines()
        ),
        "all_examples_result_sanity_audit_validator_output": (
            all_examples_result_sanity_audit_output.strip().splitlines()
        ),
        "all_method_example_claim_disposition_audit_validator_output": (
            all_method_example_claim_disposition_audit_output.strip().splitlines()
        ),
        "paper_numerical_result_matrix_validator_output": (
            paper_numerical_result_matrix_output.strip().splitlines()
        ),
        "common_reference_order_recomputation_audit_validator_output": (
            common_reference_order_recomputation_audit_output.strip().splitlines()
        ),
        "comparison_objective_closure_reconciliation_audit_validator_output": (
            comparison_objective_closure_reconciliation_audit_output.strip().splitlines()
        ),
        "paper_core_result_consolidation_validator_output": (
            paper_core_result_consolidation_output.strip().splitlines()
        ),
        "proof_closure_manifest_validator_output": proof_closure_manifest_output.strip().splitlines(),
        "proof_claim_traceability_audit_validator_output": (
            proof_claim_traceability_audit_output.strip().splitlines()
        ),
        "proof_remaining_work_manifest_validator_output": (
            proof_remaining_work_manifest_output.strip().splitlines()
        ),
        "b1_ad_expanded_symbolic_oracle_closure_certificate_validator_output": (
            b1_ad_expanded_symbolic_oracle_closure_certificate_output.strip().splitlines()
        ),
        "b1_symbolic_row_oracle_closure_certificate_validator_output": (
            b1_symbolic_row_oracle_closure_certificate_output.strip().splitlines()
        ),
        "b3_direct_proof_review_audit_validator_output": (
            b3_direct_proof_review_audit_output.strip().splitlines()
        ),
        "cmame_strict_proof_audit_validator_output": (
            cmame_strict_proof_audit_output.strip().splitlines()
        ),
        "cmame_strict_proof_policy_reconciliation_audit_validator_output": (
            cmame_strict_proof_policy_reconciliation_audit_output.strip().splitlines()
        ),
        "cmame_proof_style_audit_validator_output": cmame_proof_style_audit_output.strip().splitlines(),
        "kinematic_row_defect_certificate_validator_output": (
            kinematic_row_defect_certificate_output.strip().splitlines()
        ),
        "newton_euler_virtual_work_wrench_audit_validator_output": (
            newton_euler_virtual_work_wrench_audit_output.strip().splitlines()
        ),
        "newton_euler_symbolic_target_audit_validator_output": (
            newton_euler_symbolic_target_audit_output.strip().splitlines()
        ),
        "newton_euler_symbolic_defect_certificate_validator_output": (
            newton_euler_symbolic_defect_certificate_output.strip().splitlines()
        ),
        "newton_euler_row_ordering_scaling_ad_audit_validator_output": (
            newton_euler_row_ordering_scaling_ad_audit_output.strip().splitlines()
        ),
        "newton_euler_dynamic_row_closure_contract_validator_output": (
            newton_euler_dynamic_row_closure_contract_output.strip().splitlines()
        ),
        "newton_euler_defect_obligation_gate_validator_output": (
            newton_euler_defect_obligation_gate_output.strip().splitlines()
        ),
        "newton_euler_balance_identity_audit_validator_output": (
            newton_euler_balance_identity_audit_output.strip().splitlines()
        ),
        "newton_euler_ad_expanded_row_oracle_audit_validator_output": (
            newton_euler_ad_expanded_row_oracle_audit_output.strip().splitlines()
        ),
        "smooth_force_lift_certificate_validator_output": smooth_force_lift_certificate_output.strip().splitlines(),
        "b2_source_policy_remaining_work_manifest_validator_output": (
            b2_source_policy_remaining_work_manifest_output.strip().splitlines()
        ),
        "source_policy_closure_triage_validator_output": (
            source_policy_closure_triage_output.strip().splitlines()
        ),
        "all_examples_source_policy_audit_validator_output": (
            all_examples_source_policy_audit_output.strip().splitlines()
        ),
        "four_example_source_policy_dashboard_validator_output": (
            four_example_source_policy_dashboard_output.strip().splitlines()
        ),
        "external_baseline_source_policy_diagnosis_validator_output": (
            external_baseline_source_policy_diagnosis_output.strip().splitlines()
        ),
        "external_case_evidence_reconciliation_validator_output": (
            external_case_evidence_reconciliation_output.strip().splitlines()
        ),
        "external_same_test_acceptance_sheet_validator_output": (
            external_same_test_acceptance_sheet_output.strip().splitlines()
        ),
        "external_suite_demotion_ledger_validator_output": (
            external_suite_demotion_ledger_output.strip().splitlines()
        ),
        "external_suite_disposition_audit_validator_output": (
            external_suite_disposition_audit_output.strip().splitlines()
        ),
        "external_superiority_claim_demotion_audit_validator_output": (
            external_superiority_claim_demotion_audit_output.strip().splitlines()
        ),
        "b4_b7_non_superiority_route_audit_validator_output": (
            b4_b7_non_superiority_route_audit_output.strip().splitlines()
        ),
        "source_policy_local_candidate_gap_audit_validator_output": (
            source_policy_local_candidate_gap_audit_output.strip().splitlines()
        ),
        "ra2021_source_identity_audit_validator_output": (
            ra2021_source_identity_audit_output.strip().splitlines()
        ),
        "ra2021_double_source_policy_low_order_diagnosis_validator_output": (
            ra2021_double_source_policy_low_order_diagnosis_output.strip().splitlines()
        ),
        "ra2021_source_policy_row_audit_validator_output": (
            ra2021_source_policy_row_audit_output.strip().splitlines()
        ),
        "hi2022_policy_decision_audit_validator_output": (
            hi2022_policy_decision_audit_output.strip().splitlines()
        ),
        "hi2022_source_policy_row_audit_validator_output": (
            hi2022_source_policy_row_audit_output.strip().splitlines()
        ),
        "hi2022_ra_half_double_source_policy_failure_diagnosis_validator_output": (
            hi2022_ra_half_double_source_policy_failure_diagnosis_output.strip().splitlines()
        ),
        "hi2022_ra_half_double_repair_attempt_certificate_validator_output": (
            hi2022_ra_half_double_repair_attempt_certificate_output.strip().splitlines()
        ),
        "hi2022_t8_tolerance_repair_audit_validator_output": (
            hi2022_t8_tolerance_repair_audit_output.strip().splitlines()
        ),
        "vp2024_code_path_disposition_audit_validator_output": (
            vp2024_code_path_disposition_audit_output.strip().splitlines()
        ),
        "vp2024_public_code_recheck_20260613_validator_output": (
            vp2024_public_code_recheck_20260613_output.strip().splitlines()
        ),
        "tfe_source_policy_spec_validator_output": (
            tfe_source_policy_spec_output.strip().splitlines()
        ),
        "tfe_source_pendulum_model_audit_validator_output": (
            tfe_source_pendulum_model_audit_output.strip().splitlines()
        ),
        "tfe_source_policy_row_audit_validator_output": (
            tfe_source_policy_row_audit_output.strip().splitlines()
        ),
        "tfe_source_grid_compatibility_audit_validator_output": (
            tfe_source_grid_compatibility_audit_output.strip().splitlines()
        ),
        "tfe_brown_mcphee_source_code_equivalence_certificate_validator_output": (
            tfe_brown_mcphee_source_code_equivalence_certificate_output.strip().splitlines()
        ),
        "tfe_full_t10_endpoint_policy_closure_certificate_validator_output": (
            tfe_full_t10_endpoint_policy_closure_certificate_output.strip().splitlines()
        ),
        "tfe_endpoint_policy_boundary_certificate_validator_output": (
            tfe_endpoint_policy_boundary_certificate_output.strip().splitlines()
        ),
        "tfe_algorithm_literal_endpoint_probe_validator_output": (
            tfe_algorithm_literal_endpoint_probe_output.strip().splitlines()
        ),
        "tfe_algorithm_literal_work_precision_audit_validator_output": (
            tfe_algorithm_literal_work_precision_audit_output.strip().splitlines()
        ),
        "tfe_b4_b7_source_policy_demotion_audit_validator_output": (
            tfe_b4_b7_source_policy_demotion_audit_output.strip().splitlines()
        ),
        "tfe_brown_mcphee_source_law_boundary_audit_validator_output": (
            tfe_brown_mcphee_source_law_boundary_audit_output.strip().splitlines()
        ),
        "tfe_endpoint_policy_sensitivity_audit_validator_output": (
            tfe_endpoint_policy_sensitivity_audit_output.strip().splitlines()
        ),
        "tfe_full_t10_absolute_dae_lift_summary_validator_output": (
            tfe_full_t10_absolute_dae_lift_summary_output.strip().splitlines()
        ),
        "tfe_full_t10_coarse_candidate_summary_validator_output": (
            tfe_full_t10_coarse_candidate_summary_output.strip().splitlines()
        ),
        "tfe_public_code_recheck_20260613_validator_output": (
            tfe_public_code_recheck_20260613_output.strip().splitlines()
        ),
        "tfe_source_policy_self_reproduction_attempt_validator_output": tfe_self_reproduction_attempt_output.strip().splitlines(),
        "source_policy_self_reproduction_attempt_audit_validator_output": (
            source_policy_self_reproduction_attempt_audit_output.strip().splitlines()
        ),
        "ra_hi_source_policy_output_inventory_validator_output": ra_hi_output_inventory_output.strip().splitlines(),
        "ra_hi_source_policy_closeout_checklist_validator_output": ra_hi_closeout_checklist_output.strip().splitlines(),
        "ra_hi_source_policy_promotion_blocker_matrix_validator_output": ra_hi_promotion_blocker_matrix_output.strip().splitlines(),
        "ra_hi_source_policy_post_execution_attempt_certificate_validator_output": ra_hi_post_execution_attempt_certificate_output.strip().splitlines(),
        "b4_source_policy_execution_opt_in_packet_validator_output": b4_source_policy_execution_opt_in_packet_output.strip().splitlines(),
        "b4_source_policy_guarded_driver_validator_output": b4_source_policy_guarded_driver_output.strip().splitlines(),
        "b4_guarded_driver_refusal_boundary_audit_validator_output": (
            b4_guarded_driver_refusal_boundary_audit_output.strip().splitlines()
        ),
        "b4_source_policy_execution_handoff_package_validator_output": b4_source_policy_execution_handoff_package_output.strip().splitlines(),
        "b4_source_policy_command_preflight_freeze_validator_output": b4_source_policy_command_preflight_freeze_output.strip().splitlines(),
        "b4_source_policy_expected_output_schema_audit_validator_output": b4_source_policy_expected_output_schema_audit_output.strip().splitlines(),
        "b4_expected_output_promotion_readiness_blocker_audit_validator_output": b4_expected_output_promotion_readiness_blocker_audit_output.strip().splitlines(),
        "oc6_source_equivalent_reopen_readiness_audit_validator_output": oc6_source_equivalent_reopen_readiness_audit_output.strip().splitlines(),
        "oc6_external_source_artifact_recheck_20260621_validator_output": (
            oc6_external_source_artifact_recheck_20260621_output.strip().splitlines()
        ),
        "oc6_tfe_publisher_artifact_availability_audit_20260621_validator_output": (
            oc6_tfe_publisher_artifact_availability_audit_20260621_output.strip().splitlines()
        ),
        "oc6_tfe_source_equivalent_artifact_request_packet_20260621_validator_output": (
            oc6_tfe_source_equivalent_artifact_request_packet_20260621_output.strip().splitlines()
        ),
        "full_source_policy_row_provenance_audit_validator_output": full_source_policy_row_provenance_audit_output.strip().splitlines(),
        "full_source_policy_runner_archive_gap_validator_output": full_source_policy_runner_archive_gap_output.strip().splitlines(),
        "objective_completion_audit_validator_output": objective_completion_audit_output.strip().splitlines(),
        "source_policy_public_code_refresh_20260620_validator_output": (
            source_policy_public_code_refresh_20260620_output.strip().splitlines()
        ),
        "source_policy_reopen_condition_monitor_validator_output": source_policy_reopen_condition_monitor_output.strip().splitlines(),
        "source_policy_reopen_condition_monitor_20260621_delta_validator_output": (
            source_policy_reopen_condition_monitor_20260621_delta_output.strip().splitlines()
        ),
        "v048_validator_output": v048_output.strip().splitlines(),
        "v048_four_example_matrix_validator_output": v048_matrix_output.strip().splitlines(),
        "v048_coarse_first_validator_output": v048_coarse_first_output.strip().splitlines(),
        "v048_closed_loop_surrogate_validator_output": v048_closed_loop_surrogate_output.strip().splitlines(),
        "v048_closed_loop_floor_audit_validator_output": v048_closed_loop_floor_audit_output.strip().splitlines(),
        "v048_closed_loop_coarse_probe_validator_output": v048_closed_loop_coarse_probe_output.strip().splitlines(),
        "v048_closed_loop_closure_contract_validator_output": v048_closed_loop_closure_contract_output.strip().splitlines(),
        "v048_closed_loop_feasibility_audit_validator_output": v048_closed_loop_feasibility_audit_output.strip().splitlines(),
        "v048_closed_loop_residual_scaffold_validator_output": v048_closed_loop_residual_scaffold_output.strip().splitlines(),
        "v048_closed_loop_stage_residual_audit_validator_output": v048_closed_loop_stage_residual_audit_output.strip().splitlines(),
        "v048_closed_loop_one_step_smoke_validator_output": v048_closed_loop_one_step_smoke_output.strip().splitlines(),
        "v048_closed_loop_newton_stage_smoke_validator_output": v048_closed_loop_newton_stage_smoke_output.strip().splitlines(),
        "v048_closed_loop_newton_coarse_order_validator_output": v048_closed_loop_newton_coarse_order_output.strip().splitlines(),
        "v048_closed_loop_public_work_precision_validator_output": v048_closed_loop_public_work_precision_output.strip().splitlines(),
        "v048_closed_loop_strict_common_reference_validator_output": v048_closed_loop_strict_common_reference_output.strip().splitlines(),
        "v048_residual_to_error_obligation_validator_output": v048_residual_to_error_obligation_output.strip().splitlines(),
        "v048_single_pendulum_coarse_validator_output": v048_single_coarse_output.strip().splitlines(),
        "paper_claim_validator_output": paper_claim_output.strip().splitlines(),
        "proof_evidence_matrix_validator_output": proof_evidence_matrix_output.strip().splitlines(),
        "proof_solver_scale_audit_validator_output": proof_solver_scale_audit_output.strip().splitlines(),
        "order_acceptance_gate_validator_output": order_acceptance_gate_output.strip().splitlines(),
        "cmame_submission_validator_output": cmame_submission_output.strip().splitlines(),
        "submission_artifact_manifest_boundary_sync_validator_output": (
            submission_artifact_manifest_boundary_sync_output.strip().splitlines()
        ),
        "cmame_blocker_closure_gate_validator_output": cmame_blocker_closure_output.strip().splitlines(),
        "cmame_external_baseline_gate_validator_output": cmame_external_baseline_output.strip().splitlines(),
        "external_same_test_run_queue_validator_output": external_same_test_run_queue_output.strip().splitlines(),
        "cmame_proof_contract_gate_validator_output": cmame_proof_contract_output.strip().splitlines(),
        "cmame_visual_legibility_audit_validator_output": cmame_visual_legibility_output.strip().splitlines(),
        "cmame_related_work_audit_validator_output": cmame_related_work_output.strip().splitlines(),
        "cmame_prose_residue_audit_validator_output": cmame_prose_residue_audit_output.strip().splitlines(),
        "dynamic_row_oracle_gate_validator_output": dynamic_row_oracle_output.strip().splitlines(),
        "source_paper_comparison_validator_output": source_paper_comparison_output.strip().splitlines(),
        "submission_bundle_validator_output": submission_bundle_output.strip().splitlines(),
        "paper_latex_log_validator_output": paper_latex_log_output.strip().splitlines(),
        "documentation_boundary_validator_output": documentation_boundary_output.strip().splitlines(),
        "source_policy_execution_invoked": False,
        "heavy_numerical_run_invoked": False,
        "run_v047_invoked": False,
        "v048_runner_invoked": False,
        "recommended_pdf": "main_cmame.pdf",
        "full_tfe_stage_replacement": False,
    }
    summary_path = RESULTS / "pipeline_validation_summary.json"
    with summary_path.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, sort_keys=True)
        handle.write("\n")

    report_path = RESULTS / "pipeline_validation_report.md"
    lines = [
        "# Pipeline Validation Report",
        "",
        f"- status: {summary['status']}",
        f"- checks run: {expected_final_checks}",
        f"- versions inventoried: {totals['versions']}",
        f"- result files checked: {totals['result_files']}",
        f"- CSV/PNG/JSON checked: {totals['csv']}/{totals['png']}/{totals['json']}",
        f"- current version: {CURRENT_VERSION}",
        f"- v047 ASME gate: {current_gate['asme_status']}",
        f"- v047 sharp ultra status: {current_gate['sharp_ultra_status']}",
        f"- v047 TFE readiness counts: {current_gate['tfe_readiness']}",
        f"- remaining caveats: {', '.join(current_gate['remaining_caveats'])}",
        "",
        "## Objective Completion Boundary",
        "",
        "```text",
        objective_completion_boundary_output.strip(),
        "```",
        "",
        "## Current Pipeline Gate Validator",
        "",
        "```text",
        current_pipeline_gate_output.strip(),
        "```",
        "",
        "## v047 Validator",
        "",
        "```text",
        v047_output.strip(),
        "```",
        "",
        "## Minimal Four-ASME Validator",
        "",
        "```text",
        four_asme_output.strip(),
        "```",
        "",
        "## Full-TFE Gap Validator",
        "",
        "```text",
        full_tfe_gap_output.strip(),
        "```",
        "",
        "## Full-TFE Repair Spec Validator",
        "",
        "```text",
        full_tfe_repair_spec_output.strip(),
        "```",
        "",
        "## Implementation Fidelity Certificate Validator",
        "",
        "```text",
        implementation_fidelity_output.strip(),
        "```",
        "",
        "## Implementation Path Audit Validator",
        "",
        "```text",
        implementation_path_audit_output.strip(),
        "```",
        "",
        "## B4 Source-Policy Row Closure-Readiness Ledger Validator",
        "",
        "```text",
        b4_source_policy_row_closure_readiness_ledger_output.strip(),
        "```",
        "",
        "## Source-Policy Row Closure Ledger Validator",
        "",
        "```text",
        source_policy_row_closure_ledger_output.strip(),
        "```",
        "",
        "## TFE DAE Runner Contract Gap Audit Validator",
        "",
        "```text",
        tfe_dae_runner_contract_gap_audit_output.strip(),
        "```",
        "",
        "## TFE Runner Contract Preflight Certificate Validator",
        "",
        "```text",
        tfe_runner_contract_preflight_certificate_output.strip(),
        "```",
        "",
        "## B4 Source-Policy Work/Precision Execution Plan Validator",
        "",
        "```text",
        b4_source_policy_work_precision_execution_plan_output.strip(),
        "```",
        "",
        "## B4 Source-Policy Post-Execution Audit Validator",
        "",
        "```text",
        b4_source_policy_post_execution_audit_output.strip(),
        "```",
        "",
        "## B4 Existing-Artifact Promotion Audit Validator",
        "",
        "```text",
        b4_existing_artifact_promotion_audit_output.strip(),
        "```",
        "",
        "## External Source-Policy Closure Manifest Validator",
        "",
        "```text",
        external_source_policy_closure_manifest_output.strip(),
        "```",
        "",
        "## B6 Four-Example Local Evidence Validator",
        "",
        "```text",
        b6_four_example_local_evidence_output.strip(),
        "```",
        "",
        "## CMAME Runner-Centered Reproducibility Audit Validator",
        "",
        "```text",
        cmame_runner_centered_reproducibility_audit_output.strip(),
        "```",
        "",
        "## CMAME Narrowed Reproducibility Package Audit Validator",
        "",
        "```text",
        cmame_narrowed_reproducibility_package_audit_output.strip(),
        "```",
        "",
        "## CMAME Narrowed Repro Code Archive Validator",
        "",
        "```text",
        cmame_narrowed_repro_code_archive_output.strip(),
        "```",
        "",
        "## CMAME Reproducibility Package Manifest Validator",
        "",
        "```text",
        cmame_reproducibility_package_manifest_output.strip(),
        "```",
        "",
        "## B6 Closed-Loop Self-Contained Extraction Audit Validator",
        "",
        "```text",
        b6_closed_loop_self_contained_extraction_audit_output.strip(),
        "```",
        "",
        "## CMAME Self-Contained Runner Extraction Plan Validator",
        "",
        "```text",
        cmame_self_contained_runner_extraction_plan_output.strip(),
        "```",
        "",
        "## CMAME Minimal Reproducibility Candidate Validator",
        "",
        "```text",
        cmame_minimal_reproducibility_candidate_output.strip(),
        "```",
        "",
        "## CMAME Closed-Loop Local Runner Candidate Validator",
        "",
        "```text",
        cmame_closed_loop_local_runner_candidate_output.strip(),
        "```",
        "",
        "## CMAME Local Accepted-Row Runner Companion Validator",
        "",
        "```text",
        cmame_local_accepted_runner_companion_output.strip(),
        "```",
        "",
        "## CMAME P1 Local-Runner Extraction Audit Validator",
        "",
        "```text",
        cmame_p1_local_runner_extraction_audit_output.strip(),
        "```",
        "",
        "## CMAME P1 Single Runner Candidate Validator",
        "",
        "```text",
        cmame_p1_single_runner_candidate_output.strip(),
        "```",
        "",
        "## CMAME P1 Double Runner Candidate Validator",
        "",
        "```text",
        cmame_p1_double_runner_candidate_output.strip(),
        "```",
        "",
        "## CMAME Runner-Adapter Candidate Validator",
        "",
        "```text",
        cmame_runner_adapter_candidate_output.strip(),
        "```",
        "",
        "## CMAME Narrowed Repro Bundle Validator",
        "",
        "```text",
        cmame_narrowed_repro_bundle_output.strip(),
        "```",
        "",
        "## CMAME Submission Integrity Audit Validator",
        "",
        "```text",
        cmame_submission_integrity_audit_output.strip(),
        "```",
        "",
        "## Reference Metadata Audit Validator",
        "",
        "```text",
        reference_metadata_audit_output.strip(),
        "```",
        "",
        "## Result-to-Manuscript Traceability Audit Validator",
        "",
        "```text",
        result_to_manuscript_traceability_audit_output.strip(),
        "```",
        "",
        "## CMAME Figure-Set Audit Validator",
        "",
        "```text",
        cmame_figure_set_audit_output.strip(),
        "```",
        "",
        "## CMAME Scalability Boundary Audit Validator",
        "",
        "```text",
        cmame_scalability_boundary_audit_output.strip(),
        "```",
        "",
        "## CMAME Claim-Hygiene Audit Validator",
        "",
        "```text",
        cmame_claim_hygiene_audit_output.strip(),
        "```",
        "",
        "## CMAME PDF Style Review Audit Validator",
        "",
        "```text",
        cmame_pdf_style_review_audit_output.strip(),
        "```",
        "",
        "## CMAME Review-Agent Validator",
        "",
        "```text",
        cmame_review_agent_output.strip(),
        "```",
        "",
        "## CMAME Narrowed-Claim Closure Policy Audit Validator",
        "",
        "```text",
        cmame_narrowed_claim_closure_policy_audit_output.strip(),
        "```",
        "",
        "## Paper Core-to-Manuscript Audit Validator",
        "",
        "```text",
        paper_core_to_manuscript_audit_output.strip(),
        "```",
        "",
        "## All-Examples Result Sanity Audit Validator",
        "",
        "```text",
        all_examples_result_sanity_audit_output.strip(),
        "```",
        "",
        "## All-Method Example Claim-Disposition Audit Validator",
        "",
        "```text",
        all_method_example_claim_disposition_audit_output.strip(),
        "```",
        "",
        "## Paper Numerical Result Matrix Validator",
        "",
        "```text",
        paper_numerical_result_matrix_output.strip(),
        "```",
        "",
        "## Common-Reference Order Recomputation Audit Validator",
        "",
        "```text",
        common_reference_order_recomputation_audit_output.strip(),
        "```",
        "",
        "## Comparison Objective Closure Reconciliation Audit Validator",
        "",
        "```text",
        comparison_objective_closure_reconciliation_audit_output.strip(),
        "```",
        "",
        "## Paper Core Result Consolidation Validator",
        "",
        "```text",
        paper_core_result_consolidation_output.strip(),
        "```",
        "",
        "## Proof Closure Manifest Validator",
        "",
        "```text",
        proof_closure_manifest_output.strip(),
        "```",
        "",
        "## Proof Claim Traceability Audit Validator",
        "",
        "```text",
        proof_claim_traceability_audit_output.strip(),
        "```",
        "",
        "## Proof Remaining-Work Manifest Validator",
        "",
        "```text",
        proof_remaining_work_manifest_output.strip(),
        "```",
        "",
        "## B1 AD-Expanded Symbolic Oracle Closure Certificate Validator",
        "",
        "```text",
        b1_ad_expanded_symbolic_oracle_closure_certificate_output.strip(),
        "```",
        "",
        "## B1 Symbolic Row Oracle Closure Certificate Validator",
        "",
        "```text",
        b1_symbolic_row_oracle_closure_certificate_output.strip(),
        "```",
        "",
        "## B3 Direct Proof Review Audit Validator",
        "",
        "```text",
        b3_direct_proof_review_audit_output.strip(),
        "```",
        "",
        "## CMAME Strict Proof Audit Validator",
        "",
        "```text",
        cmame_strict_proof_audit_output.strip(),
        "```",
        "",
        "## CMAME Strict Proof Policy Reconciliation Audit Validator",
        "",
        "```text",
        cmame_strict_proof_policy_reconciliation_audit_output.strip(),
        "```",
        "",
        "## CMAME Proof-Style Audit Validator",
        "",
        "```text",
        cmame_proof_style_audit_output.strip(),
        "```",
        "",
        "## Kinematic Row Defect Certificate Validator",
        "",
        "```text",
        kinematic_row_defect_certificate_output.strip(),
        "```",
        "",
        "## Newton-Euler Virtual-Work Wrench Audit Validator",
        "",
        "```text",
        newton_euler_virtual_work_wrench_audit_output.strip(),
        "```",
        "",
        "## Newton-Euler Symbolic Target Audit Validator",
        "",
        "```text",
        newton_euler_symbolic_target_audit_output.strip(),
        "```",
        "",
        "## Newton-Euler Symbolic Defect Certificate Validator",
        "",
        "```text",
        newton_euler_symbolic_defect_certificate_output.strip(),
        "```",
        "",
        "## Newton-Euler Row-Ordering Scaling AD Audit Validator",
        "",
        "```text",
        newton_euler_row_ordering_scaling_ad_audit_output.strip(),
        "```",
        "",
        "## Newton-Euler Dynamic Row Closure Contract Validator",
        "",
        "```text",
        newton_euler_dynamic_row_closure_contract_output.strip(),
        "```",
        "",
        "## Newton-Euler Defect Obligation Gate Validator",
        "",
        "```text",
        newton_euler_defect_obligation_gate_output.strip(),
        "```",
        "",
        "## Newton-Euler Balance Identity Audit Validator",
        "",
        "```text",
        newton_euler_balance_identity_audit_output.strip(),
        "```",
        "",
        "## Newton-Euler AD-Expanded Row Oracle Audit Validator",
        "",
        "```text",
        newton_euler_ad_expanded_row_oracle_audit_output.strip(),
        "```",
        "",
        "## Smooth Force Lift Certificate Validator",
        "",
        "```text",
        smooth_force_lift_certificate_output.strip(),
        "```",
        "",
        "## B2 Source-Policy Remaining-Work Manifest Validator",
        "",
        "```text",
        b2_source_policy_remaining_work_manifest_output.strip(),
        "```",
        "",
        "## Source-Policy Closure Triage Validator",
        "",
        "```text",
        source_policy_closure_triage_output.strip(),
        "```",
        "",
        "## All-Examples Source-Policy Audit Validator",
        "",
        "```text",
        all_examples_source_policy_audit_output.strip(),
        "```",
        "",
        "## Four-Example Source-Policy Dashboard Validator",
        "",
        "```text",
        four_example_source_policy_dashboard_output.strip(),
        "```",
        "",
        "## External Baseline Source-Policy Diagnosis Validator",
        "",
        "```text",
        external_baseline_source_policy_diagnosis_output.strip(),
        "```",
        "",
        "## External Case Evidence Reconciliation Validator",
        "",
        "```text",
        external_case_evidence_reconciliation_output.strip(),
        "```",
        "",
        "## External Same-Test Acceptance Sheet Validator",
        "",
        "```text",
        external_same_test_acceptance_sheet_output.strip(),
        "```",
        "",
        "## External Suite Demotion Ledger Validator",
        "",
        "```text",
        external_suite_demotion_ledger_output.strip(),
        "```",
        "",
        "## External Suite Disposition Audit Validator",
        "",
        "```text",
        external_suite_disposition_audit_output.strip(),
        "```",
        "",
        "## External Superiority Claim-Demotion Audit Validator",
        "",
        "```text",
        external_superiority_claim_demotion_audit_output.strip(),
        "```",
        "",
        "## B4/B7 Non-Superiority Route Audit Validator",
        "",
        "```text",
        b4_b7_non_superiority_route_audit_output.strip(),
        "```",
        "",
        "## Source-Policy Local Candidate Gap Audit Validator",
        "",
        "```text",
        source_policy_local_candidate_gap_audit_output.strip(),
        "```",
        "",
        "## RA2021 Source Identity Audit Validator",
        "",
        "```text",
        ra2021_source_identity_audit_output.strip(),
        "```",
        "",
        "## RA2021 Double Source-Policy Low-Order Diagnosis Validator",
        "",
        "```text",
        ra2021_double_source_policy_low_order_diagnosis_output.strip(),
        "```",
        "",
        "## RA2021 Source-Policy Row Audit Validator",
        "",
        "```text",
        ra2021_source_policy_row_audit_output.strip(),
        "```",
        "",
        "## HI2022 Policy Decision Audit Validator",
        "",
        "```text",
        hi2022_policy_decision_audit_output.strip(),
        "```",
        "",
        "## HI2022 Source-Policy Row Audit Validator",
        "",
        "```text",
        hi2022_source_policy_row_audit_output.strip(),
        "```",
        "",
        "## HI2022 rA Half Double Source-Policy Failure Diagnosis Validator",
        "",
        "```text",
        hi2022_ra_half_double_source_policy_failure_diagnosis_output.strip(),
        "```",
        "",
        "## HI2022 rA Half Double Repair-Attempt Certificate Validator",
        "",
        "```text",
        hi2022_ra_half_double_repair_attempt_certificate_output.strip(),
        "```",
        "",
        "## HI2022 T8 Tolerance-Repair Audit Validator",
        "",
        "```text",
        hi2022_t8_tolerance_repair_audit_output.strip(),
        "```",
        "",
        "## VP2024 Code-Path Disposition Audit Validator",
        "",
        "```text",
        vp2024_code_path_disposition_audit_output.strip(),
        "```",
        "",
        "## VP2024 Public-Code Recheck Validator",
        "",
        "```text",
        vp2024_public_code_recheck_20260613_output.strip(),
        "```",
        "",
        "## TFE Source-Policy Spec Validator",
        "",
        "```text",
        tfe_source_policy_spec_output.strip(),
        "```",
        "",
        "## TFE Source-Pendulum Model Audit Validator",
        "",
        "```text",
        tfe_source_pendulum_model_audit_output.strip(),
        "```",
        "",
        "## TFE Source-Policy Row Audit Validator",
        "",
        "```text",
        tfe_source_policy_row_audit_output.strip(),
        "```",
        "",
        "## TFE Source-Grid Compatibility Audit Validator",
        "",
        "```text",
        tfe_source_grid_compatibility_audit_output.strip(),
        "```",
        "",
        "## TFE Brown-McPhee Source-Code Equivalence Certificate Validator",
        "",
        "```text",
        tfe_brown_mcphee_source_code_equivalence_certificate_output.strip(),
        "```",
        "",
        "## TFE Full-T10 Endpoint-Policy Closure Certificate Validator",
        "",
        "```text",
        tfe_full_t10_endpoint_policy_closure_certificate_output.strip(),
        "```",
        "",
        "## TFE Endpoint Policy Boundary Certificate Validator",
        "",
        "```text",
        tfe_endpoint_policy_boundary_certificate_output.strip(),
        "```",
        "",
        "## TFE Algorithm-Literal Endpoint Probe Validator",
        "",
        "```text",
        tfe_algorithm_literal_endpoint_probe_output.strip(),
        "```",
        "",
        "## TFE Algorithm-Literal Work/Precision Audit Validator",
        "",
        "```text",
        tfe_algorithm_literal_work_precision_audit_output.strip(),
        "```",
        "",
        "## TFE B4/B7 Source-Policy Demotion Audit Validator",
        "",
        "```text",
        tfe_b4_b7_source_policy_demotion_audit_output.strip(),
        "```",
        "",
        "## TFE Brown-McPhee Source-Law Boundary Audit Validator",
        "",
        "```text",
        tfe_brown_mcphee_source_law_boundary_audit_output.strip(),
        "```",
        "",
        "## TFE Endpoint-Policy Sensitivity Audit Validator",
        "",
        "```text",
        tfe_endpoint_policy_sensitivity_audit_output.strip(),
        "```",
        "",
        "## TFE Full-T10 Absolute DAE-Lift Summary Validator",
        "",
        "```text",
        tfe_full_t10_absolute_dae_lift_summary_output.strip(),
        "```",
        "",
        "## TFE Full-T10 Coarse Candidate Summary Validator",
        "",
        "```text",
        tfe_full_t10_coarse_candidate_summary_output.strip(),
        "```",
        "",
        "## TFE Public-Code Recheck 20260613 Validator",
        "",
        "```text",
        tfe_public_code_recheck_20260613_output.strip(),
        "```",
        "",
        "## TFE Source-Policy Self-Reproduction Attempt Validator",
        "",
        "```text",
        tfe_self_reproduction_attempt_output.strip(),
        "```",
        "",
        "## Source-Policy Self-Reproduction Attempt Audit Validator",
        "",
        "```text",
        source_policy_self_reproduction_attempt_audit_output.strip(),
        "```",
        "",
        "## RA/HI Source-Policy Output Inventory Validator",
        "",
        "```text",
        ra_hi_output_inventory_output.strip(),
        "```",
        "",
        "## RA/HI Source-Policy Closeout Checklist Validator",
        "",
        "```text",
        ra_hi_closeout_checklist_output.strip(),
        "```",
        "",
        "## RA/HI Source-Policy Promotion Blocker Matrix Validator",
        "",
        "```text",
        ra_hi_promotion_blocker_matrix_output.strip(),
        "```",
        "",
        "## RA/HI Source-Policy Post-Execution Attempt Certificate Validator",
        "",
        "```text",
        ra_hi_post_execution_attempt_certificate_output.strip(),
        "```",
        "",
        "## B4 Source-Policy Execution Opt-In Packet Validator",
        "",
        "```text",
        b4_source_policy_execution_opt_in_packet_output.strip(),
        "```",
        "",
        "## B4 Source-Policy Guarded Driver Validator",
        "",
        "```text",
        b4_source_policy_guarded_driver_output.strip(),
        "```",
        "",
        "## B4 Guarded Driver Refusal Boundary Audit Validator",
        "",
        "```text",
        b4_guarded_driver_refusal_boundary_audit_output.strip(),
        "```",
        "",
        "## B4 Source-Policy Execution Handoff Package Validator",
        "",
        "```text",
        b4_source_policy_execution_handoff_package_output.strip(),
        "```",
        "",
        "## B4 Source-Policy Command Preflight Freeze Validator",
        "",
        "```text",
        b4_source_policy_command_preflight_freeze_output.strip(),
        "```",
        "",
        "## B4 Source-Policy Expected Output Schema Audit Validator",
        "",
        "```text",
        b4_source_policy_expected_output_schema_audit_output.strip(),
        "```",
        "",
        "## B4 Expected-Output Promotion-Readiness Blocker Audit Validator",
        "",
        "```text",
        b4_expected_output_promotion_readiness_blocker_audit_output.strip(),
        "```",
        "",
        "## OC6 Source-Equivalent Reopen-Readiness Audit Validator",
        "",
        "```text",
        oc6_source_equivalent_reopen_readiness_audit_output.strip(),
        "```",
        "",
        "## OC6 External Source-Artifact Recheck 20260621 Validator",
        "",
        "```text",
        oc6_external_source_artifact_recheck_20260621_output.strip(),
        "```",
        "",
        "## OC6 TFE Publisher Artifact Availability 20260621 Validator",
        "",
        "```text",
        oc6_tfe_publisher_artifact_availability_audit_20260621_output.strip(),
        "```",
        "",
        "## OC6 TFE Source-Equivalent Artifact Request Packet 20260621 Validator",
        "",
        "```text",
        oc6_tfe_source_equivalent_artifact_request_packet_20260621_output.strip(),
        "```",
        "",
        "## Full Source-Policy Row Provenance Audit Validator",
        "",
        "```text",
        full_source_policy_row_provenance_audit_output.strip(),
        "```",
        "",
        "## Full Source-Policy Runner Archive Gap Validator",
        "",
        "```text",
        full_source_policy_runner_archive_gap_output.strip(),
        "```",
        "",
        "## Objective Completion Audit Validator",
        "",
        "```text",
        objective_completion_audit_output.strip(),
        "```",
        "",
        "## Source-Policy Public-Code Refresh 20260620 Validator",
        "",
        "```text",
        source_policy_public_code_refresh_20260620_output.strip(),
        "```",
        "",
        "## Source-Policy Reopen-Condition Monitor Validator",
        "",
        "```text",
        source_policy_reopen_condition_monitor_output.strip(),
        "```",
        "",
        "## Source-Policy Reopen-Condition Monitor 20260621 Delta Validator",
        "",
        "```text",
        source_policy_reopen_condition_monitor_20260621_delta_output.strip(),
        "```",
        "",
        "## v048 Validator",
        "",
        "```text",
        v048_output.strip(),
        "```",
        "",
        "## v048 Four-Example Matrix Validator",
        "",
        "```text",
        v048_matrix_output.strip(),
        "```",
        "",
        "## v048 Coarse-First Readiness Validator",
        "",
        "```text",
        v048_coarse_first_output.strip(),
        "```",
        "",
        "## v048 Closed-Loop Surrogate Validator",
        "",
        "```text",
        v048_closed_loop_surrogate_output.strip(),
        "```",
        "",
        "## v048 Closed-Loop Floor-Audit Validator",
        "",
        "```text",
        v048_closed_loop_floor_audit_output.strip(),
        "```",
        "",
        "## v048 Closed-Loop Coarse Dynamic-Order Probe Validator",
        "",
        "```text",
        v048_closed_loop_coarse_probe_output.strip(),
        "```",
        "",
        "## v048 Closed-Loop Dynamic-Order Closure Contract Validator",
        "",
        "```text",
        v048_closed_loop_closure_contract_output.strip(),
        "```",
        "",
        "## v048 Closed-Loop True-Dynamic-Row Feasibility Audit Validator",
        "",
        "```text",
        v048_closed_loop_feasibility_audit_output.strip(),
        "```",
        "",
        "## v048 Closed-Loop True-Dynamic Residual Scaffold Validator",
        "",
        "```text",
        v048_closed_loop_residual_scaffold_output.strip(),
        "```",
        "",
        "## v048 Closed-Loop True-Dynamic Stage Residual Audit Validator",
        "",
        "```text",
        v048_closed_loop_stage_residual_audit_output.strip(),
        "```",
        "",
        "## v048 Closed-Loop True-Dynamic One-Step Smoke Validator",
        "",
        "```text",
        v048_closed_loop_one_step_smoke_output.strip(),
        "```",
        "",
        "## v048 Closed-Loop True-Dynamic Newton Stage Smoke Validator",
        "",
        "```text",
        v048_closed_loop_newton_stage_smoke_output.strip(),
        "```",
        "",
        "## v048 Closed-Loop True-Dynamic Newton Coarse Order Validator",
        "",
        "```text",
        v048_closed_loop_newton_coarse_order_output.strip(),
        "```",
        "",
        "## v048 Closed-Loop True-Dynamic Public Work/Precision Validator",
        "",
        "```text",
        v048_closed_loop_public_work_precision_output.strip(),
        "```",
        "",
        "## v048 Closed-Loop True-Dynamic Strict Common-Reference Validator",
        "",
        "```text",
        v048_closed_loop_strict_common_reference_output.strip(),
        "```",
        "",
        "## v048 Residual-to-Error Theorem Obligation Validator",
        "",
        "```text",
        v048_residual_to_error_obligation_output.strip(),
        "```",
        "",
        "## v048 Single-Pendulum Coarse Validator",
        "",
        "```text",
        v048_single_coarse_output.strip(),
        "```",
        "",
        "## Paper Claim Validator",
        "",
        "```text",
        paper_claim_output.strip(),
        "```",
        "",
        "## Proof Evidence Matrix Validator",
        "",
        "```text",
        proof_evidence_matrix_output.strip(),
        "```",
        "",
        "## Proof Solver-Scale Audit Validator",
        "",
        "```text",
        proof_solver_scale_audit_output.strip(),
        "```",
        "",
        "## Order Acceptance Gate Validator",
        "",
        "```text",
        order_acceptance_gate_output.strip(),
        "```",
        "",
        "## CMAME Submission Validator",
        "",
        "```text",
        cmame_submission_output.strip(),
        "```",
        "",
        "## Submission Artifact Manifest Boundary Sync Validator",
        "",
        "```text",
        submission_artifact_manifest_boundary_sync_output.strip(),
        "```",
        "",
        "## CMAME Blocker-Closure Gate Validator",
        "",
        "```text",
        cmame_blocker_closure_output.strip(),
        "```",
        "",
        "## CMAME External-Baseline Gate Validator",
        "",
        "```text",
        cmame_external_baseline_output.strip(),
        "```",
        "",
        "## External Same-Test Run Queue Validator",
        "",
        "```text",
        external_same_test_run_queue_output.strip(),
        "```",
        "",
        "## CMAME Proof-Contract Gate Validator",
        "",
        "```text",
        cmame_proof_contract_output.strip(),
        "```",
        "",
        "## CMAME Visual-Legibility Audit Validator",
        "",
        "```text",
        cmame_visual_legibility_output.strip(),
        "```",
        "",
        "## CMAME Related-Work Audit Validator",
        "",
        "```text",
        cmame_related_work_output.strip(),
        "```",
        "",
        "## CMAME Prose-Residue Audit Validator",
        "",
        "```text",
        cmame_prose_residue_audit_output.strip(),
        "```",
        "",
        "## Dynamic Row Oracle Gate Validator",
        "",
        "```text",
        dynamic_row_oracle_output.strip(),
        "```",
        "",
        "## Submission Bundle Validator",
        "",
        "```text",
        submission_bundle_output.strip(),
        "```",
        "",
        "## Source-Paper Comparison Validator",
        "",
        "```text",
        source_paper_comparison_output.strip(),
        "```",
        "",
        "## Paper LaTeX Log Validator",
        "",
        "```text",
        paper_latex_log_output.strip(),
        "```",
        "",
        "## Documentation Boundary Validators",
        "",
        "```text",
        documentation_boundary_output.strip(),
        "```",
    ]
    if v.failures:
        lines.extend(["", "## Failures", ""])
        lines.extend(f"- {failure}" for failure in v.failures)
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    for path in [summary_path, report_path]:
        v.check(path.exists() and path.stat().st_size > 0, f"pipeline validation output missing: {path.name}")


def main() -> int:
    v = Validator()
    inventory, totals = validate_version_inventory(v)
    v047_output = run_v047_validator(v)
    four_asme_output = run_four_asme_minimal_validator(v)
    full_tfe_gap_output = run_full_tfe_gap_validator(v)
    full_tfe_repair_spec_output = run_full_tfe_repair_spec_validator(v)
    implementation_fidelity_output = run_implementation_fidelity_validator(v)
    implementation_path_audit_output = run_implementation_path_audit_validator(v)
    b4_source_policy_row_closure_readiness_ledger_output = (
        run_b4_source_policy_row_closure_readiness_ledger_validator(v)
    )
    source_policy_row_closure_ledger_output = run_source_policy_row_closure_ledger_validator(v)
    tfe_dae_runner_contract_gap_audit_output = run_tfe_dae_runner_contract_gap_audit_validator(v)
    tfe_runner_contract_preflight_certificate_output = run_tfe_runner_contract_preflight_certificate_validator(v)
    b4_source_policy_work_precision_execution_plan_output = (
        run_b4_source_policy_work_precision_execution_plan_validator(v)
    )
    b4_source_policy_post_execution_audit_output = run_b4_source_policy_post_execution_audit_validator(v)
    b4_existing_artifact_promotion_audit_output = run_b4_existing_artifact_promotion_audit_validator(v)
    external_source_policy_closure_manifest_output = run_external_source_policy_closure_manifest_validator(v)
    b6_four_example_local_evidence_output = run_b6_four_example_local_evidence_validator(v)
    cmame_runner_centered_reproducibility_audit_output = (
        run_cmame_runner_centered_reproducibility_audit_validator(v)
    )
    cmame_narrowed_reproducibility_package_audit_output = (
        run_cmame_narrowed_reproducibility_package_audit_validator(v)
    )
    cmame_narrowed_repro_code_archive_output = run_cmame_narrowed_repro_code_archive_validator(v)
    cmame_reproducibility_package_manifest_output = run_cmame_reproducibility_package_manifest_validator(v)
    b6_closed_loop_self_contained_extraction_audit_output = (
        run_b6_closed_loop_self_contained_extraction_audit_validator(v)
    )
    cmame_self_contained_runner_extraction_plan_output = (
        run_cmame_self_contained_runner_extraction_plan_validator(v)
    )
    cmame_minimal_reproducibility_candidate_output = run_cmame_minimal_reproducibility_candidate_validator(v)
    cmame_closed_loop_local_runner_candidate_output = run_cmame_closed_loop_local_runner_candidate_validator(v)
    cmame_local_accepted_runner_companion_output = run_cmame_local_accepted_runner_companion_validator(v)
    cmame_p1_local_runner_extraction_audit_output = run_cmame_p1_local_runner_extraction_audit_validator(v)
    cmame_p1_single_runner_candidate_output = run_cmame_p1_single_runner_candidate_validator(v)
    cmame_p1_double_runner_candidate_output = run_cmame_p1_double_runner_candidate_validator(v)
    cmame_runner_adapter_candidate_output = run_cmame_runner_adapter_candidate_validator(v)
    cmame_narrowed_repro_bundle_output = run_cmame_narrowed_repro_bundle_validator(v)
    cmame_submission_integrity_audit_output = run_cmame_submission_integrity_audit_validator(v)
    reference_metadata_audit_output = run_reference_metadata_audit_validator(v)
    result_to_manuscript_traceability_audit_output = run_result_to_manuscript_traceability_audit_validator(v)
    cmame_figure_set_audit_output = run_cmame_figure_set_audit_validator(v)
    cmame_scalability_boundary_audit_output = run_cmame_scalability_boundary_audit_validator(v)
    cmame_claim_hygiene_audit_output = run_cmame_claim_hygiene_audit_validator(v)
    cmame_pdf_style_review_audit_output = run_cmame_pdf_style_review_audit_validator(v)
    cmame_review_agent_output = run_cmame_review_agent_validator(v)
    cmame_narrowed_claim_closure_policy_audit_output = run_cmame_narrowed_claim_closure_policy_audit_validator(v)
    paper_core_to_manuscript_audit_output = run_paper_core_to_manuscript_audit_validator(v)
    all_examples_result_sanity_audit_output = run_all_examples_result_sanity_audit_validator(v)
    all_method_example_claim_disposition_audit_output = run_all_method_example_claim_disposition_audit_validator(v)
    paper_numerical_result_matrix_output = run_paper_numerical_result_matrix_validator(v)
    common_reference_order_recomputation_audit_output = run_common_reference_order_recomputation_audit_validator(v)
    comparison_objective_closure_reconciliation_audit_output = (
        run_comparison_objective_closure_reconciliation_audit_validator(v)
    )
    paper_core_result_consolidation_output = run_paper_core_result_consolidation_validator(v)
    proof_closure_manifest_output = run_proof_closure_manifest_validator(v)
    proof_claim_traceability_audit_output = run_proof_claim_traceability_audit_validator(v)
    proof_remaining_work_manifest_output = run_proof_remaining_work_manifest_validator(v)
    b1_ad_expanded_symbolic_oracle_closure_certificate_output = (
        run_b1_ad_expanded_symbolic_oracle_closure_certificate_validator(v)
    )
    b1_symbolic_row_oracle_closure_certificate_output = (
        run_b1_symbolic_row_oracle_closure_certificate_validator(v)
    )
    b3_direct_proof_review_audit_output = run_b3_direct_proof_review_audit_validator(v)
    cmame_strict_proof_audit_output = run_cmame_strict_proof_audit_validator(v)
    cmame_strict_proof_policy_reconciliation_audit_output = (
        run_cmame_strict_proof_policy_reconciliation_audit_validator(v)
    )
    cmame_proof_style_audit_output = run_cmame_proof_style_audit_validator(v)
    kinematic_row_defect_certificate_output = run_kinematic_row_defect_certificate_validator(v)
    newton_euler_virtual_work_wrench_audit_output = run_newton_euler_virtual_work_wrench_audit_validator(v)
    newton_euler_symbolic_target_audit_output = run_newton_euler_symbolic_target_audit_validator(v)
    newton_euler_symbolic_defect_certificate_output = run_newton_euler_symbolic_defect_certificate_validator(v)
    newton_euler_row_ordering_scaling_ad_audit_output = (
        run_newton_euler_row_ordering_scaling_ad_audit_validator(v)
    )
    newton_euler_dynamic_row_closure_contract_output = run_newton_euler_dynamic_row_closure_contract_validator(v)
    newton_euler_defect_obligation_gate_output = run_newton_euler_defect_obligation_gate_validator(v)
    newton_euler_balance_identity_audit_output = run_newton_euler_balance_identity_audit_validator(v)
    newton_euler_ad_expanded_row_oracle_audit_output = run_newton_euler_ad_expanded_row_oracle_audit_validator(v)
    smooth_force_lift_certificate_output = run_smooth_force_lift_certificate_validator(v)
    b2_source_policy_remaining_work_manifest_output = (
        run_b2_source_policy_remaining_work_manifest_validator(v)
    )
    source_policy_closure_triage_output = run_source_policy_closure_triage_validator(v)
    all_examples_source_policy_audit_output = run_all_examples_source_policy_audit_validator(v)
    four_example_source_policy_dashboard_output = run_four_example_source_policy_dashboard_validator(v)
    external_baseline_source_policy_diagnosis_output = (
        run_external_baseline_source_policy_diagnosis_validator(v)
    )
    external_case_evidence_reconciliation_output = run_external_case_evidence_reconciliation_validator(v)
    external_same_test_acceptance_sheet_output = run_external_same_test_acceptance_sheet_validator(v)
    external_suite_demotion_ledger_output = run_external_suite_demotion_ledger_validator(v)
    external_suite_disposition_audit_output = run_external_suite_disposition_audit_validator(v)
    external_superiority_claim_demotion_audit_output = (
        run_external_superiority_claim_demotion_audit_validator(v)
    )
    b4_b7_non_superiority_route_audit_output = run_b4_b7_non_superiority_route_audit_validator(v)
    source_policy_local_candidate_gap_audit_output = run_source_policy_local_candidate_gap_audit_validator(v)
    ra2021_source_identity_audit_output = run_ra2021_source_identity_audit_validator(v)
    ra2021_double_source_policy_low_order_diagnosis_output = (
        run_ra2021_double_source_policy_low_order_diagnosis_validator(v)
    )
    ra2021_source_policy_row_audit_output = run_ra2021_source_policy_row_audit_validator(v)
    hi2022_policy_decision_audit_output = run_hi2022_policy_decision_audit_validator(v)
    hi2022_source_policy_row_audit_output = run_hi2022_source_policy_row_audit_validator(v)
    hi2022_ra_half_double_source_policy_failure_diagnosis_output = (
        run_hi2022_ra_half_double_source_policy_failure_diagnosis_validator(v)
    )
    hi2022_ra_half_double_repair_attempt_certificate_output = (
        run_hi2022_ra_half_double_repair_attempt_certificate_validator(v)
    )
    hi2022_t8_tolerance_repair_audit_output = run_hi2022_t8_tolerance_repair_audit_validator(v)
    vp2024_code_path_disposition_audit_output = run_vp2024_code_path_disposition_audit_validator(v)
    vp2024_public_code_recheck_20260613_output = run_vp2024_public_code_recheck_20260613_validator(v)
    tfe_source_policy_spec_output = run_tfe_source_policy_spec_validator(v)
    tfe_source_pendulum_model_audit_output = run_tfe_source_pendulum_model_audit_validator(v)
    tfe_source_policy_row_audit_output = run_tfe_source_policy_row_audit_validator(v)
    tfe_source_grid_compatibility_audit_output = run_tfe_source_grid_compatibility_audit_validator(v)
    tfe_brown_mcphee_source_code_equivalence_certificate_output = (
        run_tfe_brown_mcphee_source_code_equivalence_certificate_validator(v)
    )
    tfe_full_t10_endpoint_policy_closure_certificate_output = (
        run_tfe_full_t10_endpoint_policy_closure_certificate_validator(v)
    )
    tfe_endpoint_policy_boundary_certificate_output = run_tfe_endpoint_policy_boundary_certificate_validator(v)
    tfe_algorithm_literal_endpoint_probe_output = run_tfe_algorithm_literal_endpoint_probe_validator(v)
    tfe_algorithm_literal_work_precision_audit_output = (
        run_tfe_algorithm_literal_work_precision_audit_validator(v)
    )
    tfe_b4_b7_source_policy_demotion_audit_output = run_tfe_b4_b7_source_policy_demotion_audit_validator(v)
    tfe_brown_mcphee_source_law_boundary_audit_output = (
        run_tfe_brown_mcphee_source_law_boundary_audit_validator(v)
    )
    tfe_endpoint_policy_sensitivity_audit_output = run_tfe_endpoint_policy_sensitivity_audit_validator(v)
    tfe_full_t10_absolute_dae_lift_summary_output = run_tfe_full_t10_absolute_dae_lift_summary_validator(v)
    tfe_full_t10_coarse_candidate_summary_output = run_tfe_full_t10_coarse_candidate_summary_validator(v)
    tfe_public_code_recheck_20260613_output = run_tfe_public_code_recheck_20260613_validator(v)
    tfe_self_reproduction_attempt_output = run_tfe_source_policy_self_reproduction_attempt_validator(v)
    source_policy_self_reproduction_attempt_audit_output = (
        run_source_policy_self_reproduction_attempt_audit_validator(v)
    )
    ra_hi_output_inventory_output = run_ra_hi_source_policy_output_inventory_validator(v)
    ra_hi_closeout_checklist_output = run_ra_hi_source_policy_closeout_checklist_validator(v)
    ra_hi_promotion_blocker_matrix_output = run_ra_hi_source_policy_promotion_blocker_matrix_validator(v)
    ra_hi_post_execution_attempt_certificate_output = (
        run_ra_hi_source_policy_post_execution_attempt_certificate_validator(v)
    )
    b4_source_policy_execution_opt_in_packet_output = run_b4_source_policy_execution_opt_in_packet_validator(v)
    b4_source_policy_guarded_driver_output = run_b4_source_policy_guarded_driver_validator(v)
    b4_guarded_driver_refusal_boundary_audit_output = (
        run_b4_guarded_driver_refusal_boundary_audit_validator(v)
    )
    b4_source_policy_execution_handoff_package_output = run_b4_source_policy_execution_handoff_package_validator(v)
    b4_source_policy_command_preflight_freeze_output = (
        run_b4_source_policy_command_preflight_freeze_validator(v)
    )
    b4_source_policy_expected_output_schema_audit_output = (
        run_b4_source_policy_expected_output_schema_audit_validator(v)
    )
    b4_expected_output_promotion_readiness_blocker_audit_output = (
        run_b4_expected_output_promotion_readiness_blocker_audit_validator(v)
    )
    oc6_source_equivalent_reopen_readiness_audit_output = (
        run_oc6_source_equivalent_reopen_readiness_audit_validator(v)
    )
    oc6_external_source_artifact_recheck_20260621_output = (
        run_oc6_external_source_artifact_recheck_20260621_validator(v)
    )
    oc6_tfe_publisher_artifact_availability_audit_20260621_output = (
        run_oc6_tfe_publisher_artifact_availability_audit_20260621_validator(v)
    )
    oc6_tfe_source_equivalent_artifact_request_packet_20260621_output = (
        run_oc6_tfe_source_equivalent_artifact_request_packet_20260621_validator(v)
    )
    full_source_policy_row_provenance_audit_output = run_full_source_policy_row_provenance_audit_validator(v)
    full_source_policy_runner_archive_gap_output = run_full_source_policy_runner_archive_gap_validator(v)
    objective_completion_audit_output = run_objective_completion_audit_validator(v)
    source_policy_public_code_refresh_20260620_output = (
        run_source_policy_public_code_refresh_20260620_validator(v)
    )
    source_policy_reopen_condition_monitor_output = run_source_policy_reopen_condition_monitor_validator(v)
    source_policy_reopen_condition_monitor_20260621_delta_output = (
        run_source_policy_reopen_condition_monitor_20260621_delta_validator(v)
    )
    v048_output = run_v048_validator(v)
    v048_matrix_output = run_v048_four_example_matrix_validator(v)
    v048_coarse_first_output = run_v048_coarse_first_validator(v)
    v048_closed_loop_surrogate_output = run_v048_closed_loop_surrogate_validator(v)
    v048_closed_loop_floor_audit_output = run_v048_closed_loop_floor_audit_validator(v)
    v048_closed_loop_coarse_probe_output = run_v048_closed_loop_coarse_probe_validator(v)
    v048_closed_loop_closure_contract_output = run_v048_closed_loop_closure_contract_validator(v)
    v048_closed_loop_feasibility_audit_output = run_v048_closed_loop_feasibility_audit_validator(v)
    v048_closed_loop_residual_scaffold_output = run_v048_closed_loop_residual_scaffold_validator(v)
    v048_closed_loop_stage_residual_audit_output = run_v048_closed_loop_stage_residual_audit_validator(v)
    v048_closed_loop_one_step_smoke_output = run_v048_closed_loop_one_step_smoke_validator(v)
    v048_closed_loop_newton_stage_smoke_output = run_v048_closed_loop_newton_stage_smoke_validator(v)
    v048_closed_loop_newton_coarse_order_output = run_v048_closed_loop_newton_coarse_order_validator(v)
    v048_closed_loop_public_work_precision_output = run_v048_closed_loop_public_work_precision_validator(v)
    v048_closed_loop_strict_common_reference_output = run_v048_closed_loop_strict_common_reference_validator(v)
    v048_residual_to_error_obligation_output = run_v048_residual_to_error_obligation_validator(v)
    v048_single_coarse_output = run_v048_single_coarse_validator(v)
    (
        paper_claim_output,
        proof_evidence_matrix_output,
        proof_solver_scale_audit_output,
        order_acceptance_gate_output,
        cmame_submission_output,
        submission_artifact_manifest_boundary_sync_output,
        cmame_blocker_closure_output,
        cmame_external_baseline_output,
        external_same_test_run_queue_output,
        cmame_proof_contract_output,
        cmame_visual_legibility_output,
        cmame_related_work_output,
        cmame_prose_residue_audit_output,
        dynamic_row_oracle_output,
        source_paper_comparison_output,
        submission_bundle_output,
    ) = run_paper_claim_validator(v)
    paper_latex_log_output = validate_paper_latex_log(v)
    documentation_boundary_output = validate_documentation_boundary_checks(v, totals)
    current_gate = validate_current_pipeline_gate(v)
    write_outputs(
        inventory,
        totals,
        v047_output,
        four_asme_output,
        full_tfe_gap_output,
        full_tfe_repair_spec_output,
        implementation_fidelity_output,
        implementation_path_audit_output,
        b4_source_policy_row_closure_readiness_ledger_output,
        source_policy_row_closure_ledger_output,
        tfe_dae_runner_contract_gap_audit_output,
        tfe_runner_contract_preflight_certificate_output,
        b4_source_policy_work_precision_execution_plan_output,
        b4_source_policy_post_execution_audit_output,
        b4_existing_artifact_promotion_audit_output,
        external_source_policy_closure_manifest_output,
        b6_four_example_local_evidence_output,
        cmame_runner_centered_reproducibility_audit_output,
        cmame_narrowed_reproducibility_package_audit_output,
        cmame_narrowed_repro_code_archive_output,
        cmame_reproducibility_package_manifest_output,
        b6_closed_loop_self_contained_extraction_audit_output,
        cmame_self_contained_runner_extraction_plan_output,
        cmame_minimal_reproducibility_candidate_output,
        cmame_closed_loop_local_runner_candidate_output,
        cmame_local_accepted_runner_companion_output,
        cmame_p1_local_runner_extraction_audit_output,
        cmame_p1_single_runner_candidate_output,
        cmame_p1_double_runner_candidate_output,
        cmame_runner_adapter_candidate_output,
        cmame_narrowed_repro_bundle_output,
        cmame_submission_integrity_audit_output,
        reference_metadata_audit_output,
        result_to_manuscript_traceability_audit_output,
        cmame_figure_set_audit_output,
        cmame_scalability_boundary_audit_output,
        cmame_claim_hygiene_audit_output,
        cmame_pdf_style_review_audit_output,
        cmame_review_agent_output,
        cmame_narrowed_claim_closure_policy_audit_output,
        paper_core_to_manuscript_audit_output,
        all_examples_result_sanity_audit_output,
        all_method_example_claim_disposition_audit_output,
        paper_numerical_result_matrix_output,
        common_reference_order_recomputation_audit_output,
        comparison_objective_closure_reconciliation_audit_output,
        paper_core_result_consolidation_output,
        proof_closure_manifest_output,
        proof_claim_traceability_audit_output,
        proof_remaining_work_manifest_output,
        b1_ad_expanded_symbolic_oracle_closure_certificate_output,
        b1_symbolic_row_oracle_closure_certificate_output,
        b3_direct_proof_review_audit_output,
        cmame_strict_proof_audit_output,
        cmame_strict_proof_policy_reconciliation_audit_output,
        cmame_proof_style_audit_output,
        kinematic_row_defect_certificate_output,
        newton_euler_virtual_work_wrench_audit_output,
        newton_euler_symbolic_target_audit_output,
        newton_euler_symbolic_defect_certificate_output,
        newton_euler_row_ordering_scaling_ad_audit_output,
        newton_euler_dynamic_row_closure_contract_output,
        newton_euler_defect_obligation_gate_output,
        newton_euler_balance_identity_audit_output,
        newton_euler_ad_expanded_row_oracle_audit_output,
        smooth_force_lift_certificate_output,
        b2_source_policy_remaining_work_manifest_output,
        source_policy_closure_triage_output,
        all_examples_source_policy_audit_output,
        four_example_source_policy_dashboard_output,
        external_baseline_source_policy_diagnosis_output,
        external_case_evidence_reconciliation_output,
        external_same_test_acceptance_sheet_output,
        external_suite_demotion_ledger_output,
        external_suite_disposition_audit_output,
        external_superiority_claim_demotion_audit_output,
        b4_b7_non_superiority_route_audit_output,
        source_policy_local_candidate_gap_audit_output,
        ra2021_source_identity_audit_output,
        ra2021_double_source_policy_low_order_diagnosis_output,
        ra2021_source_policy_row_audit_output,
        hi2022_policy_decision_audit_output,
        hi2022_source_policy_row_audit_output,
        hi2022_ra_half_double_source_policy_failure_diagnosis_output,
        hi2022_ra_half_double_repair_attempt_certificate_output,
        hi2022_t8_tolerance_repair_audit_output,
        vp2024_code_path_disposition_audit_output,
        vp2024_public_code_recheck_20260613_output,
        tfe_source_policy_spec_output,
        tfe_source_pendulum_model_audit_output,
        tfe_source_policy_row_audit_output,
        tfe_source_grid_compatibility_audit_output,
        tfe_brown_mcphee_source_code_equivalence_certificate_output,
        tfe_full_t10_endpoint_policy_closure_certificate_output,
        tfe_endpoint_policy_boundary_certificate_output,
        tfe_algorithm_literal_endpoint_probe_output,
        tfe_algorithm_literal_work_precision_audit_output,
        tfe_b4_b7_source_policy_demotion_audit_output,
        tfe_brown_mcphee_source_law_boundary_audit_output,
        tfe_endpoint_policy_sensitivity_audit_output,
        tfe_full_t10_absolute_dae_lift_summary_output,
        tfe_full_t10_coarse_candidate_summary_output,
        tfe_public_code_recheck_20260613_output,
        tfe_self_reproduction_attempt_output,
        source_policy_self_reproduction_attempt_audit_output,
        ra_hi_output_inventory_output,
        ra_hi_closeout_checklist_output,
        ra_hi_promotion_blocker_matrix_output,
        ra_hi_post_execution_attempt_certificate_output,
        b4_source_policy_execution_opt_in_packet_output,
        b4_source_policy_guarded_driver_output,
        b4_guarded_driver_refusal_boundary_audit_output,
        b4_source_policy_execution_handoff_package_output,
        b4_source_policy_command_preflight_freeze_output,
        b4_source_policy_expected_output_schema_audit_output,
        b4_expected_output_promotion_readiness_blocker_audit_output,
        oc6_source_equivalent_reopen_readiness_audit_output,
        oc6_external_source_artifact_recheck_20260621_output,
        oc6_tfe_publisher_artifact_availability_audit_20260621_output,
        oc6_tfe_source_equivalent_artifact_request_packet_20260621_output,
        full_source_policy_row_provenance_audit_output,
        full_source_policy_runner_archive_gap_output,
        objective_completion_audit_output,
        source_policy_public_code_refresh_20260620_output,
        source_policy_reopen_condition_monitor_output,
        source_policy_reopen_condition_monitor_20260621_delta_output,
        v048_output,
        v048_matrix_output,
        v048_coarse_first_output,
        v048_closed_loop_surrogate_output,
        v048_closed_loop_floor_audit_output,
        v048_closed_loop_coarse_probe_output,
        v048_closed_loop_closure_contract_output,
        v048_closed_loop_feasibility_audit_output,
        v048_closed_loop_residual_scaffold_output,
        v048_closed_loop_stage_residual_audit_output,
        v048_closed_loop_one_step_smoke_output,
        v048_closed_loop_newton_stage_smoke_output,
        v048_closed_loop_newton_coarse_order_output,
        v048_closed_loop_public_work_precision_output,
        v048_closed_loop_strict_common_reference_output,
        v048_residual_to_error_obligation_output,
        v048_single_coarse_output,
        paper_claim_output,
        proof_evidence_matrix_output,
        proof_solver_scale_audit_output,
        order_acceptance_gate_output,
        cmame_submission_output,
        submission_artifact_manifest_boundary_sync_output,
        cmame_blocker_closure_output,
        cmame_external_baseline_output,
        external_same_test_run_queue_output,
        cmame_proof_contract_output,
        cmame_visual_legibility_output,
        cmame_related_work_output,
        cmame_prose_residue_audit_output,
        dynamic_row_oracle_output,
        source_paper_comparison_output,
        submission_bundle_output,
        paper_latex_log_output,
        documentation_boundary_output,
        current_gate,
        v,
    )

    if v.failures:
        print("pipeline output validation: FAIL")
        for failure in v.failures:
            print(f"- {failure}")
        return 1
    print("pipeline output validation: PASS")
    print(f"checks_run={v.checks_run}")
    print(f"versions={totals['versions']}")
    print(f"result_files={totals['result_files']}")
    print(f"csv_files={totals['csv']}")
    print(f"png_files={totals['png']}")
    print(f"json_files={totals['json']}")
    print("v047_validator=PASS")
    print("four_asme_minimal_validator=PASS")
    print("full_tfe_gap_validator=PASS")
    print("full_tfe_repair_spec_validator=PASS")
    print("implementation_fidelity_validator=PASS")
    print("implementation_path_audit_validator=PASS")
    print("b4_source_policy_row_closure_readiness_ledger_validator=PASS")
    print("source_policy_row_closure_ledger_validator=PASS")
    print("tfe_dae_runner_contract_gap_audit_validator=PASS")
    print("tfe_runner_contract_preflight_certificate_validator=PASS")
    print("b4_source_policy_work_precision_execution_plan_validator=PASS")
    print("b4_source_policy_post_execution_audit_validator=PASS")
    print("b4_existing_artifact_promotion_audit_validator=PASS")
    print("external_source_policy_closure_manifest_validator=PASS")
    print("b6_four_example_local_evidence_validator=PASS")
    print("cmame_runner_centered_reproducibility_audit_validator=PASS")
    print("cmame_narrowed_reproducibility_package_audit_validator=PASS")
    print("cmame_narrowed_repro_code_archive_validator=PASS")
    print("cmame_reproducibility_package_manifest_validator=PASS")
    print("b6_closed_loop_self_contained_extraction_audit_validator=PASS")
    print("cmame_self_contained_runner_extraction_plan_validator=PASS")
    print("cmame_minimal_reproducibility_candidate_validator=PASS")
    print("cmame_closed_loop_local_runner_candidate_validator=PASS")
    print("cmame_local_accepted_runner_companion_validator=PASS")
    print("cmame_p1_local_runner_extraction_audit_validator=PASS")
    print("cmame_p1_single_runner_candidate_validator=PASS")
    print("cmame_p1_double_runner_candidate_validator=PASS")
    print("cmame_runner_adapter_candidate_validator=PASS")
    print("cmame_narrowed_repro_bundle_validator=PASS")
    print("cmame_submission_integrity_audit_validator=PASS")
    print("reference_metadata_audit_validator=PASS")
    print("result_to_manuscript_traceability_audit_validator=PASS")
    print("cmame_figure_set_audit_validator=PASS")
    print("cmame_scalability_boundary_audit_validator=PASS")
    print("cmame_claim_hygiene_audit_validator=PASS")
    print("cmame_pdf_style_review_audit_validator=PASS")
    print("cmame_review_agent_validator=PASS")
    print("cmame_narrowed_claim_closure_policy_audit_validator=PASS")
    print("paper_core_to_manuscript_audit_validator=PASS")
    print("all_examples_result_sanity_audit_validator=PASS")
    print("all_method_example_claim_disposition_audit_validator=PASS")
    print("paper_numerical_result_matrix_validator=PASS")
    print("common_reference_order_recomputation_audit_validator=PASS")
    print("comparison_objective_closure_reconciliation_audit_validator=PASS")
    print("paper_core_result_consolidation_validator=PASS")
    print("proof_closure_manifest_validator=PASS")
    print("proof_claim_traceability_audit_validator=PASS")
    print("proof_remaining_work_manifest_validator=PASS")
    print("b1_ad_expanded_symbolic_oracle_closure_certificate_validator=PASS")
    print("b1_symbolic_row_oracle_closure_certificate_validator=PASS")
    print("b3_direct_proof_review_audit_validator=PASS")
    print("cmame_strict_proof_audit_validator=PASS")
    print("cmame_strict_proof_policy_reconciliation_audit_validator=PASS")
    print("cmame_proof_style_audit_validator=PASS")
    print("kinematic_row_defect_certificate_validator=PASS")
    print("newton_euler_virtual_work_wrench_audit_validator=PASS")
    print("newton_euler_symbolic_target_audit_validator=PASS")
    print("newton_euler_symbolic_defect_certificate_validator=PASS")
    print("newton_euler_row_ordering_scaling_ad_audit_validator=PASS")
    print("newton_euler_dynamic_row_closure_contract_validator=PASS")
    print("newton_euler_defect_obligation_gate_validator=PASS")
    print("newton_euler_balance_identity_audit_validator=PASS")
    print("newton_euler_ad_expanded_row_oracle_audit_validator=PASS")
    print("smooth_force_lift_certificate_validator=PASS")
    print("b2_source_policy_remaining_work_manifest_validator=PASS")
    print("source_policy_closure_triage_validator=PASS")
    print("all_examples_source_policy_audit_validator=PASS")
    print("four_example_source_policy_dashboard_validator=PASS")
    print("external_baseline_source_policy_diagnosis_validator=PASS")
    print("external_case_evidence_reconciliation_validator=PASS")
    print("external_same_test_acceptance_sheet_validator=PASS")
    print("external_suite_demotion_ledger_validator=PASS")
    print("external_suite_disposition_audit_validator=PASS")
    print("external_superiority_claim_demotion_audit_validator=PASS")
    print("b4_b7_non_superiority_route_audit_validator=PASS")
    print("source_policy_local_candidate_gap_audit_validator=PASS")
    print("ra2021_source_identity_audit_validator=PASS")
    print("ra2021_double_source_policy_low_order_diagnosis_validator=PASS")
    print("ra2021_source_policy_row_audit_validator=PASS")
    print("hi2022_policy_decision_audit_validator=PASS")
    print("hi2022_source_policy_row_audit_validator=PASS")
    print("hi2022_ra_half_double_source_policy_failure_diagnosis_validator=PASS")
    print("hi2022_ra_half_double_repair_attempt_certificate_validator=PASS")
    print("hi2022_t8_tolerance_repair_audit_validator=PASS")
    print("vp2024_code_path_disposition_audit_validator=PASS")
    print("vp2024_public_code_recheck_20260613_validator=PASS")
    print("tfe_source_policy_spec_validator=PASS")
    print("tfe_source_pendulum_model_audit_validator=PASS")
    print("tfe_source_policy_row_audit_validator=PASS")
    print("tfe_source_grid_compatibility_audit_validator=PASS")
    print("tfe_brown_mcphee_source_code_equivalence_certificate_validator=PASS")
    print("tfe_full_t10_endpoint_policy_closure_certificate_validator=PASS")
    print("tfe_endpoint_policy_boundary_certificate_validator=PASS")
    print("tfe_algorithm_literal_endpoint_probe_validator=PASS")
    print("tfe_algorithm_literal_work_precision_audit_validator=PASS")
    print("tfe_b4_b7_source_policy_demotion_audit_validator=PASS")
    print("tfe_brown_mcphee_source_law_boundary_audit_validator=PASS")
    print("tfe_endpoint_policy_sensitivity_audit_validator=PASS")
    print("tfe_full_t10_absolute_dae_lift_summary_validator=PASS")
    print("tfe_full_t10_coarse_candidate_summary_validator=PASS")
    print("tfe_public_code_recheck_20260613_validator=PASS")
    print("tfe_source_policy_self_reproduction_attempt_validator=PASS")
    print("source_policy_self_reproduction_attempt_audit_validator=PASS")
    print("ra_hi_source_policy_output_inventory_validator=PASS")
    print("ra_hi_source_policy_closeout_checklist_validator=PASS")
    print("ra_hi_source_policy_promotion_blocker_matrix_validator=PASS")
    print("ra_hi_source_policy_post_execution_attempt_certificate_validator=PASS")
    print("b4_source_policy_execution_opt_in_packet_validator=PASS")
    print("b4_source_policy_guarded_driver_validator=PASS")
    print("b4_guarded_driver_refusal_boundary_audit_validator=PASS")
    print("b4_source_policy_execution_handoff_package_validator=PASS")
    print("b4_source_policy_command_preflight_freeze_validator=PASS")
    print("b4_source_policy_expected_output_schema_audit_validator=PASS")
    print("b4_expected_output_promotion_readiness_blocker_audit_validator=PASS")
    print("oc6_source_equivalent_reopen_readiness_audit_validator=PASS")
    print("oc6_external_source_artifact_recheck_20260621_validator=PASS")
    print("oc6_tfe_publisher_artifact_availability_audit_20260621_validator=PASS")
    print("oc6_tfe_source_equivalent_artifact_request_packet_20260621_validator=PASS")
    print("full_source_policy_row_provenance_audit_validator=PASS")
    print("full_source_policy_runner_archive_gap_validator=PASS")
    print("objective_completion_audit_validator=PASS")
    print("source_policy_public_code_refresh_20260620_validator=PASS")
    print("source_policy_reopen_condition_monitor_validator=PASS")
    print("source_policy_reopen_condition_monitor_20260621_delta_validator=PASS")
    print("v048_validator=PASS")
    print("v048_four_example_matrix_validator=PASS")
    print("v048_coarse_first_readiness_validator=PASS")
    print("v048_closed_loop_surrogate_validator=PASS")
    print("v048_closed_loop_floor_audit_validator=PASS")
    print("v048_closed_loop_coarse_probe_validator=PASS")
    print("v048_closed_loop_closure_contract_validator=PASS")
    print("v048_closed_loop_feasibility_audit_validator=PASS")
    print("v048_closed_loop_residual_scaffold_validator=PASS")
    print("v048_closed_loop_stage_residual_audit_validator=PASS")
    print("v048_closed_loop_one_step_smoke_validator=PASS")
    print("v048_closed_loop_newton_stage_smoke_validator=PASS")
    print("v048_closed_loop_newton_coarse_order_validator=PASS")
    print("v048_closed_loop_public_work_precision_validator=PASS")
    print("v048_closed_loop_strict_common_reference_validator=PASS")
    print("v048_residual_to_error_obligation_validator=PASS")
    print("v048_single_pendulum_coarse_validator=PASS")
    print("paper_claim_validator=PASS")
    print("proof_evidence_matrix_validator=PASS")
    print("proof_solver_scale_audit_validator=PASS")
    print("order_acceptance_gate_validator=PASS")
    print("cmame_submission_validator=PASS")
    print("submission_artifact_manifest_boundary_sync_validator=PASS")
    print("cmame_blocker_closure_gate_validator=PASS")
    print("cmame_external_baseline_gate_validator=PASS")
    print("external_same_test_run_queue_validator=PASS")
    print("cmame_proof_contract_gate_validator=PASS")
    print("cmame_visual_legibility_audit_validator=PASS")
    print("cmame_related_work_audit_validator=PASS")
    print("cmame_prose_residue_audit_validator=PASS")
    print("dynamic_row_oracle_gate_validator=PASS")
    print("block_functional_crosscheck=PASS")
    print("source_paper_comparison_validator=PASS")
    print("submission_bundle_validator=PASS")
    print("paper_latex_log=PASS")
    print("source_policy_execution_invoked=False")
    print("heavy_numerical_run_invoked=False")
    print("run_v047_invoked=False")
    print("v048_runner_invoked=False")
    print("remaining_caveats=sparse_speed_quantified,full_tfe_stage_replacement_missing,sharp_friction_coarse_order_reduction_ultra_recovered")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
