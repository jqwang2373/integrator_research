#!/usr/bin/env python3
"""Read-only validator for the external same-test run queue."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
from paper_paths import LATEX, package_path as manuscript_path
QUEUE_JSON = PAPER / "EXTERNAL_SAME_TEST_RUN_QUEUE.json"
QUEUE_MD = PAPER / "EXTERNAL_SAME_TEST_RUN_QUEUE.md"
CROSS_CASES = PAPER / "CROSS_PAPER_BENCHMARK_CASES.json"
EXTERNAL_GATE = PAPER / "CMAME_EXTERNAL_BASELINE_GATE.json"
BLOCKER_GATE = PAPER / "CMAME_BLOCKER_CLOSURE_GATE.json"
FOUR_EXAMPLE_DASHBOARD = PAPER / "FOUR_EXAMPLE_SOURCE_POLICY_DASHBOARD.json"
MANIFEST = PAPER / "SUBMISSION_ARTIFACT_MANIFEST.json"

EXPECTED_MODELS = ["single_pendulum", "double_pendulum", "four_link", "slider_crank"]
EXPECTED_FORMS_2021 = ["rA", "rp", "reps"]
EXPECTED_COARSE_STEPS = [0.1, 0.05, 0.025]


class Checks:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def check(self, condition: bool, message: str) -> None:
        if not condition:
            self.errors.append(message)


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def read_text(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8", errors="replace")


def contains_normalized(text: str, token: str) -> bool:
    return token in text or " ".join(token.split()) in " ".join(text.split())


def require_tokens(checks: Checks, text: str, tokens: list[str], label: str) -> None:
    for token in tokens:
        checks.check(contains_normalized(text, token), f"{label} missing token: {token}")


def blocker_by_id(blocker_gate: dict[str, Any], blocker_id: str) -> dict[str, Any]:
    for blocker in blocker_gate.get("blockers", []):
        if isinstance(blocker, dict) and blocker.get("id") == blocker_id:
            return blocker
    return {}


def batch_by_id(queue: dict[str, Any], batch_id: str) -> dict[str, Any]:
    for batch in queue.get("batch_queue", []):
        if isinstance(batch, dict) and batch.get("batch_id") == batch_id:
            return batch
    return {}


def main() -> int:
    checks = Checks()
    try:
        queue = read_json(QUEUE_JSON)
        queue_md = read_text(QUEUE_MD)
        cross_cases = read_json(CROSS_CASES)
        external_gate = read_json(EXTERNAL_GATE)
        blocker_gate = read_json(BLOCKER_GATE)
        four_example_dashboard = read_json(FOUR_EXAMPLE_DASHBOARD)
        manifest = read_json(MANIFEST)
    except Exception as exc:  # noqa: BLE001 - concise CLI failure.
        print(f"external_same_test_run_queue=FAIL\n- {exc}")
        return 1

    execution = queue.get("execution_policy", {})
    counts = queue.get("coverage_counts", {})
    cases = cross_cases.get("cases", [])
    sources = cross_cases.get("external_sources", [])
    batches = queue.get("batch_queue", [])
    b2 = blocker_by_id(blocker_gate, "B2")
    external_source_files = external_gate.get("source_files", {})

    checks.check(queue.get("schema") == "external-same-test-run-queue-v1", "queue schema changed")
    checks.check(
        queue.get("status") == "coarse_first_parallel_queue_ready_not_run",
        "queue status changed",
    )
    checks.check(queue.get("submission_ready") is False, "queue incorrectly claims submission ready")
    checks.check(queue.get("accepted_method") == "Gauss6/FullVA", "accepted method changed")
    checks.check(queue.get("source_cases") == "CROSS_PAPER_BENCHMARK_CASES.json", "source cases path changed")
    checks.check(queue.get("same_test_campaign_status") == "not_run", "queue overclaims same-test campaign")
    checks.check(queue.get("external_superiority_claim") is False, "queue overclaims external superiority")
    local_boundary = queue.get("local_dynamic_order_boundary", {})
    checks.check(
        local_boundary.get("local_evidence_coverage_examples_count")
        == four_example_dashboard.get("local_evidence_coverage_examples")
        == 4,
        "queue local evidence coverage count changed",
    )
    checks.check(
        local_boundary.get("local_evidence_coverage_examples")
        == four_example_dashboard.get("local_evidence_coverage_example_names")
        == EXPECTED_MODELS,
        "queue local evidence coverage examples changed",
    )
    checks.check(
        local_boundary.get("accepted_method_dynamic_order_examples_count")
        == four_example_dashboard.get("accepted_method_dynamic_order_example_count")
        == 2,
        "queue accepted method dynamic-order count changed",
    )
    checks.check(
        local_boundary.get("accepted_method_dynamic_order_examples")
        == four_example_dashboard.get("accepted_method_dynamic_order_examples")
        == ["single_pendulum", "double_pendulum"],
        "queue accepted method dynamic-order examples changed",
    )
    checks.check(
        local_boundary.get("mechanism_coverage_examples_count")
        == four_example_dashboard.get("mechanism_coverage_example_count")
        == 2,
        "queue mechanism coverage count changed",
    )
    checks.check(
        local_boundary.get("mechanism_coverage_examples")
        == four_example_dashboard.get("mechanism_coverage_examples")
        == ["four_link", "slider_crank"],
        "queue mechanism coverage examples changed",
    )
    checks.check(
        local_boundary.get("local_dynamic_order_closed_examples_count")
        == four_example_dashboard.get("local_dynamic_order_closed_examples")
        == 2,
        "queue local dynamic-order count changed",
    )
    checks.check(
        local_boundary.get("local_dynamic_order_closed_examples")
        == four_example_dashboard.get("local_dynamic_order_closed_example_names")
        == ["single_pendulum", "double_pendulum"],
        "queue local dynamic-order examples changed",
    )
    checks.check(
        local_boundary.get("accepted_source_policy_dynamic_order_examples_count")
        == four_example_dashboard.get("accepted_source_policy_dynamic_order_examples")
        == 0,
        "queue source-policy dynamic-order count changed",
    )
    checks.check(local_boundary.get("external_superiority_claim") is False, "queue local boundary overclaims superiority")

    checks.check(execution.get("read_only_queue") is True, "queue lost read-only marker")
    checks.check(execution.get("default_step_policy") == "coarse_first_no_default_1e-4", "default policy changed")
    checks.check(execution.get("coarse_step_sizes") == EXPECTED_COARSE_STEPS, "coarse step sizes changed")
    checks.check(execution.get("coarse_reference_h") == 0.0125, "coarse reference changed")
    checks.check(execution.get("strict_public_policy_1e-4") == "opt_in_only", "strict public policy changed")
    checks.check(execution.get("default_1e-4_required") is False, "queue incorrectly requires default 1e-4")
    checks.check(execution.get("heavy_numerical_run_invoked") is False, "queue invoked heavy run")
    checks.check(execution.get("run_v047_invoked") is False, "queue invoked run_v047")
    checks.check(execution.get("v048_runner_invoked") is False, "queue invoked v048 runner")

    checks.check(cross_cases.get("schema") == "cross-paper-benchmark-cases-v1", "cross cases schema changed")
    checks.check(cross_cases.get("same_test_campaign_status") == "not_run", "cross cases overclaim same-test campaign")
    checks.check(cross_cases.get("external_superiority_claim") is False, "cross cases overclaim superiority")
    checks.check(cross_cases.get("default_1e-4_required") is False, "cross cases overclaim default 1e-4")
    checks.check(len(sources) == counts.get("external_source_count") == 4, "external source count changed")
    checks.check(len(cases) == counts.get("required_case_count") == 17, "required case count changed")
    checks.check(len(batches) == counts.get("queue_batch_count") == 4, "queue batch count changed")
    checks.check(counts.get("parallel_ready_batch_count") == 2, "parallel-ready batch count changed")
    checks.check(counts.get("not_ready_batch_count") == 2, "not-ready batch count changed")
    checks.check(counts.get("parallel_shard_count_without_default_1e-4") == 20, "parallel shard count changed")
    checks.check(counts.get("source_policy_1e-4_opt_in_batch_count") == 1, "source-policy opt-in count changed")
    checks.check(counts.get("code_path_unresolved_batch_count") == 1, "code-path unresolved count changed")

    ra_batch = batch_by_id(queue, "ra2021_coarse_same_window_order_time")
    hi_batch = batch_by_id(queue, "hi2022_halfimplicit_full_policy_decision")
    tfe_batch = batch_by_id(queue, "tfe2026_original_pendulum_encoding")
    vp_batch = batch_by_id(queue, "vp2024_velocity_partitioning_code_resolution")

    checks.check(ra_batch.get("queue_status") == "parallel_ready_existing_interfaces", "RA2021 queue status changed")
    checks.check(ra_batch.get("models") == EXPECTED_MODELS, "RA2021 model set changed")
    checks.check(ra_batch.get("public_forms") == EXPECTED_FORMS_2021, "RA2021 public forms changed")
    checks.check(ra_batch.get("step_sizes") == EXPECTED_COARSE_STEPS, "RA2021 step sizes changed")
    checks.check(ra_batch.get("reference_h") == 0.0125, "RA2021 reference changed")
    checks.check(ra_batch.get("parallel_shard_count") == 12, "RA2021 shard count changed")
    checks.check(ra_batch.get("can_parallelize") is True, "RA2021 should remain parallelizable")
    checks.check(ra_batch.get("source_policy_1e-4_required") is False, "RA2021 queue overclaims source 1e-4 need")
    reading = ra_batch.get("current_reading_after_reconciliation", {})
    checks.check(reading.get("local_evidence_coverage_examples") == "4/4", "RA2021 local evidence coverage reading changed")
    checks.check(reading.get("accepted_method_dynamic_order_examples") == "2/4", "RA2021 accepted method dynamic-order reading changed")
    checks.check(reading.get("mechanism_coverage_examples") == "2/4", "RA2021 mechanism coverage reading changed")
    checks.check(reading.get("local_dynamic_order_examples") == "2/4", "RA2021 local dynamic-order reading changed")
    checks.check(
        reading.get("source_policy_external_dynamic_order_examples") == "0/4",
        "RA2021 source-policy dynamic-order reading changed",
    )
    for artifact in ra_batch.get("current_evidence", []):
        checks.check((manuscript_path(artifact)).resolve().exists(), f"RA2021 evidence missing: {artifact}")

    checks.check(
        hi_batch.get("queue_status") == "parallel_ready_after_policy_selection",
        "HI2022 queue status changed",
    )
    checks.check(hi_batch.get("models") == EXPECTED_MODELS, "HI2022 model set changed")
    checks.check(hi_batch.get("public_forms") == ["rA_half", "rA"], "HI2022 public forms changed")
    checks.check(hi_batch.get("time_horizon") == 8.0, "HI2022 time horizon changed")
    checks.check(hi_batch.get("parallel_shard_count") == 8, "HI2022 shard count changed")
    checks.check(hi_batch.get("can_parallelize") is True, "HI2022 should remain parallelizable")
    checks.check(hi_batch.get("source_policy_1e-4_required") is False, "HI2022 queue overclaims source 1e-4 need")
    for artifact in hi_batch.get("current_evidence", []):
        checks.check((manuscript_path(artifact)).resolve().exists(), f"HI2022 evidence missing: {artifact}")

    checks.check(
        tfe_batch.get("queue_status") == "not_ready_source_setup_encoding_required",
        "TFE queue status changed",
    )
    checks.check(tfe_batch.get("parallel_shard_count") == 0, "TFE batch should not have runnable shards yet")
    checks.check(tfe_batch.get("can_parallelize") is False, "TFE batch should not be runnable before encoding")
    checks.check(
        tfe_batch.get("source_policy_1e-4_required") == "unknown_until_source_policy_encoded",
        "TFE source policy boundary changed",
    )

    checks.check(vp_batch.get("queue_status") == "not_ready_code_path_unresolved", "VP2024 queue status changed")
    checks.check(vp_batch.get("parallel_shard_count") == 0, "VP2024 batch should not have runnable shards")
    checks.check(vp_batch.get("can_parallelize") is False, "VP2024 batch should not be runnable before code resolution")
    checks.check(vp_batch.get("source_policy_1e-4_required") is False, "VP2024 source policy changed")
    for artifact in vp_batch.get("current_evidence", []):
        checks.check((manuscript_path(artifact)).resolve().exists(), f"VP2024 evidence missing: {artifact}")

    acceptance = queue.get("acceptance_rules", {})
    for key in [
        "order_and_time_required",
        "same_test_setup_required",
        "common_reference_or_declared_reference_policy_required",
        "residual_only_rows_do_not_count_as_dynamic_order",
        "full_external_superiority_requires_all_included_suites_closed",
        "suite_demotions_must_be_stated_in_manuscript",
    ]:
        checks.check(acceptance.get(key) is True, f"acceptance rule changed: {key}")

    checks.check(
        external_gate.get("same_test_boundary", {}).get("same_test_campaign_status") == "not_run",
        "external gate overclaims same-test campaign",
    )
    checks.check(
        external_gate.get("same_test_boundary", {}).get("external_superiority_claim") is False,
        "external gate overclaims superiority",
    )
    checks.check(
        external_gate.get("execution_policy", {}).get("default_1e-4_required") is False,
        "external gate overclaims default 1e-4",
    )
    checks.check(
        external_source_files.get("external_same_test_run_queue") == "EXTERNAL_SAME_TEST_RUN_QUEUE.json",
        "external gate lost run queue source file",
    )
    checks.check("external_same_test_run_queue_added" in b2.get("partial_progress", []), "B2 lost run queue progress marker")
    checks.check("EXTERNAL_SAME_TEST_RUN_QUEUE.md" in b2.get("partial_progress_evidence", []), "B2 run queue MD evidence missing")
    checks.check("EXTERNAL_SAME_TEST_RUN_QUEUE.json" in b2.get("partial_progress_evidence", []), "B2 run queue JSON evidence missing")
    checks.check("validate_external_same_test_run_queue.py" in b2.get("partial_progress_evidence", []), "B2 run queue validator missing")

    checks.check(manifest.get("external_same_test_run_queue") == "EXTERNAL_SAME_TEST_RUN_QUEUE.md", "manifest run queue path missing")
    checks.check(
        manifest.get("external_same_test_run_queue_json") == "EXTERNAL_SAME_TEST_RUN_QUEUE.json",
        "manifest run queue JSON path missing",
    )
    checks.check("EXTERNAL_SAME_TEST_RUN_QUEUE.md" in manifest.get("evidence_anchors", []), "manifest run queue anchor missing")
    checks.check("EXTERNAL_SAME_TEST_RUN_QUEUE.json" in manifest.get("evidence_anchors", []), "manifest run queue JSON anchor missing")
    checks.check("validate_external_same_test_run_queue.py" in manifest.get("validators", []), "manifest run queue validator missing")

    require_tokens(
        checks,
        queue_md,
        [
            "External Same-Test Run Queue",
            "COARSE-FIRST PARALLEL QUEUE READY - NOT RUN",
            "does not invoke `run_v047.py`",
            "default `1e-4` campaign",
            "same_test_campaign_status=not_run",
            "external_superiority_claim=false",
            "required case count from `CROSS_PAPER_BENCHMARK_CASES.json`: `17`",
            "parallel shards without default `1e-4`: `20`",
            "local evidence coverage examples: `4/4`",
            "accepted method dynamic-order examples: `2/4`",
            "mechanism-coverage examples: `2/4`",
            "source-policy external dynamic-order examples: `0/4`",
            "`ra2021_coarse_same_window_order_time`",
            "`hi2022_halfimplicit_full_policy_decision`",
            "`tfe2026_original_pendulum_encoding`",
            "`vp2024_velocity_partitioning_code_resolution`",
            "order and time are both required",
            "residual-only rows do not count as dynamic order",
            "validate_external_same_test_run_queue.py",
        ],
        "EXTERNAL_SAME_TEST_RUN_QUEUE.md",
    )

    forbidden = set(queue.get("forbidden_claims", []))
    for token in [
        "external_superiority_claim_true",
        "same_test_campaign_status_complete",
        "default_1e-4_required_true",
        "run_v047_invoked_true",
        "residual_only_rows_count_as_dynamic_order_true",
        "submission_ready_true",
    ]:
        checks.check(token in forbidden, f"forbidden claim missing: {token}")

    if checks.errors:
        print("external_same_test_run_queue=FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("external_same_test_run_queue=PASS")
    print("required_case_count=17")
    print("parallel_ready_batch_count=2")
    print("parallel_shard_count_without_default_1e-4=20")
    print("local_evidence_coverage_examples=4/4")
    print("accepted_method_dynamic_order_examples=2/4")
    print("mechanism_coverage_examples=2/4")
    print("source_policy_dynamic_order_examples=0/4")
    print("ra2021_parallel_shards=12")
    print("hi2022_parallel_shards=8")
    print("tfe2026_encoding_required=True")
    print("vp2024_code_path_unresolved=True")
    print("default_1e-4=False")
    print("run_v047_invoked=False")
    print("v048_runner_invoked=False")
    print("external_superiority_claim=False")
    print("submission_ready=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
