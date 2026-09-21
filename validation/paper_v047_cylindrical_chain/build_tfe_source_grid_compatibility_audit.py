#!/usr/bin/env python3
"""Audit whether the extracted TFE source h values land exactly on T=10."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np


PAPER = Path(__file__).resolve().parent
AUTORESEARCH_ROOT = PAPER.parents[1]
SOURCE_TEXT = AUTORESEARCH_ROOT / "external" / "literature" / "s11044-026-10153-w.txt"
OUT_JSON = PAPER / "TFE_SOURCE_GRID_COMPATIBILITY_AUDIT.json"
OUT_MD = PAPER / "TFE_SOURCE_GRID_COMPATIBILITY_AUDIT.md"


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def unique_h_values(case: dict[str, Any]) -> list[float]:
    values: list[float] = []
    for key in ["comparison_step_sizes"]:
        for item in case.get(key, []):
            values.append(float(item))
    for key in ["error_sweep_h_min", "error_sweep_h_max", "large_step_stability_h"]:
        if case.get(key) is not None:
            values.append(float(case[key]))
    return sorted(set(values))


def endpoint_policy_fields(t_final: float, h: float) -> dict[str, Any]:
    exact_steps = t_final / h
    floor_steps = int(exact_steps)
    ceil_steps = floor_steps if abs(exact_steps - floor_steps) <= 1.0e-14 else floor_steps + 1
    nearest_steps = int(round(exact_steps))
    nearest_t_final = nearest_steps * h
    floor_t_final = floor_steps * h
    ceil_t_final = ceil_steps * h
    adjusted_h = t_final / nearest_steps if nearest_steps > 0 else float("nan")
    final_partial_step = t_final - floor_t_final
    return {
        "exact_steps": exact_steps,
        "nearest_integer_steps": nearest_steps,
        "nearest_integer_t_final": nearest_t_final,
        "t_final_mismatch": abs(nearest_t_final - t_final),
        "floor_integer_steps": floor_steps,
        "floor_integer_t_final": floor_t_final,
        "floor_t_final_mismatch": abs(floor_t_final - t_final),
        "ceil_integer_steps": ceil_steps,
        "ceil_integer_t_final": ceil_t_final,
        "ceil_t_final_mismatch": abs(ceil_t_final - t_final),
        "adjusted_h_for_exact_T_using_nearest_steps": adjusted_h,
        "relative_h_adjustment_for_exact_T": abs(adjusted_h - h) / h if h else float("inf"),
        "final_partial_step_size_for_exact_T": final_partial_step,
        "final_partial_step_fraction_of_h": final_partial_step / h if h else float("inf"),
    }


def row_id(case_id: str | None, h: float) -> str:
    return f"{case_id}:h={h:.12g}"


def read_text_lines(path: Path) -> list[str]:
    if not path.exists():
        return []
    return path.read_text(encoding="utf-8", errors="replace").splitlines()


def normalized(value: str) -> str:
    return " ".join(value.replace("−", "-").replace("–", "-").replace("—", "-").split()).lower()


def find_anchor(lines: list[str], needle: str, finding: str) -> dict[str, Any] | None:
    needle_norm = normalized(needle)
    for index, line in enumerate(lines, start=1):
        if needle_norm in normalized(line):
            return {
                "line": index,
                "needle": needle,
                "finding": finding,
            }
    return None


def source_text_endpoint_convention_audit(rows: list[dict[str, Any]]) -> dict[str, Any]:
    lines = read_text_lines(SOURCE_TEXT)
    anchor_specs = [
        (
            "Inputs: m, ν, t0 , tfinal",
            "Algorithm 1 takes a target final time but does not describe a last-step adjustment.",
        ),
        (
            "while tn < tfinal do",
            "Algorithm 1 uses a strict less-than final-time loop condition.",
        ),
        (
            "tn ← tn−1 + h",
            "Algorithm 1 advances by the fixed step size h.",
        ),
        (
            "h = 0.003 and h = 0.006",
            "The frictionless comparison uses published h values that do not divide T=10 exactly.",
        ),
        (
            "step-size 1e − 4",
            "The source reference step size is stated, but the endpoint convention is not.",
        ),
        (
            "tf inal = 10 s",
            "The error discussion reports values at a 10 s final time.",
        ),
        (
            "h = 0.003 and h = 0.008",
            "The frictional comparison mixes one incompatible and one compatible h value.",
        ),
        (
            "time-step h = 0.2",
            "The large-step frictional comparison uses a compatible h value.",
        ),
        (
            "Computational times for a 10 s simulation",
            "Figure captions repeatedly frame the run as a 10 s simulation.",
        ),
    ]
    anchors = [anchor for anchor in (find_anchor(lines, needle, finding) for needle, finding in anchor_specs) if anchor]
    absence_terms = [
        "partial final step",
        "last step",
        "interpolation",
        "interpolate",
        "adjusted step",
        "truncate",
        "floor",
        "ceil",
        "nearest integer",
    ]
    lower_text = "\n".join(normalized(line) for line in lines)
    negative_search = {
        term: (term in lower_text)
        for term in absence_terms
    }
    algorithm_literal_rows = []
    for row in rows:
        t_final = float(row["t_final"])
        h = float(row["h"])
        steps_to_reach_or_exceed = int(np.ceil((t_final - 1.0e-14) / h))
        literal_t_final = steps_to_reach_or_exceed * h
        algorithm_literal_rows.append(
            {
                "row_id": row["row_id"],
                "case_id": row["case_id"],
                "friction_enabled": row["friction_enabled"],
                "h": h,
                "steps_to_reach_or_exceed_T": steps_to_reach_or_exceed,
                "algorithm_literal_terminal_time": literal_t_final,
                "algorithm_literal_overshoot": literal_t_final - t_final,
                "hits_exact_T": abs(literal_t_final - t_final) <= 1.0e-12,
            }
        )
    return {
        "source_text_file": "../../external/literature/s11044-026-10153-w.txt",
        "source_text_available": bool(lines),
        "source_text_line_count": len(lines),
        "anchor_count": len(anchors),
        "anchors": anchors,
        "algorithm_literal_constant_h_until_tn_ge_tfinal": len(anchors) >= 3,
        "source_text_confirms_adjusted_h_for_exact_T": False,
        "source_text_confirms_partial_final_step": False,
        "source_text_confirms_interpolation_to_exact_T": False,
        "source_text_confirms_floor_or_nearest_endpoint_sampling": False,
        "source_endpoint_convention_resolved_for_error_sampling": False,
        "algorithm_literal_rows": algorithm_literal_rows,
        "negative_search_terms_found": negative_search,
        "interpretation": (
            "The paper text supports a fixed-h, loop-until-final-time algorithm outline, but it does not "
            "state where error/order values are sampled when h does not divide T=10. Therefore the endpoint "
            "convention is not source-policy closed."
        ),
    }


def row_level_promotion_disposition(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    dispositions = []
    for row in rows:
        compatible = bool(row["integer_step_compatible"])
        if compatible:
            endpoint_status = "endpoint_grid_resolved_pending_runner_contracts"
            required_before_promotion = [
                "source-equivalent absolute-coordinate DAE runner",
                "source-equivalent method runner for the selected TFE/Newmark/trapezoidal method",
                "source-code-equivalent Brown--McPhee friction law if the row is frictional",
                "accepted error/order/runtime/work metric binding",
            ]
        else:
            endpoint_status = "blocked_by_endpoint_sampling_policy"
            required_before_promotion = [
                "source-confirmed endpoint/output sampling convention for noninteger T/h",
                "source-equivalent absolute-coordinate DAE runner",
                "source-equivalent method runner for the selected TFE/Newmark/trapezoidal method",
                "accepted error/order/runtime/work metric binding",
            ]
        dispositions.append(
            {
                "row_id": row["row_id"],
                "case_id": row["case_id"],
                "h": row["h"],
                "friction_enabled": row["friction_enabled"],
                "integer_step_compatible": compatible,
                "endpoint_grid_disposition": endpoint_status,
                "source_policy_row_completed": False,
                "source_policy_execution_eligible_now": False,
                "source_policy_demoted_until_source_endpoint_sampling_policy": not compatible,
                "required_before_promotion": required_before_promotion,
            }
        )
    return dispositions


def endpoint_policy_acceptance_contract(
    compatible_row_ids: list[str], incompatible_row_ids: list[str]
) -> dict[str, Any]:
    return {
        "exact_T_compatible_subset_can_enter_future_execution_after_runner_contracts": True,
        "exact_T_compatible_row_ids": compatible_row_ids,
        "endpoint_incompatible_rows_blocked_until_source_sampling_policy": incompatible_row_ids,
        "endpoint_incompatible_rows_demoted_from_source_policy": incompatible_row_ids,
        "endpoint_incompatible_demotion_contract": (
            "Endpoint-incompatible published h rows are diagnostic-only and excluded from the "
            "source-policy row set unless source text, source code, or a source-equivalent runner "
            "establishes the error/output sampling convention for noninteger T/h."
        ),
        "full_T10_source_policy_promotion_requires": [
            "all published h rows use a source-confirmed endpoint/output sampling convention",
            "Algorithm-1-literal overrun rows are accepted only if source output/error sampling is confirmed at the overrun state",
            "adjusted-h, interpolation, floor/nearest, or partial-step conventions require source text, source code, or explicit demotion",
            "method-runner, DAE-runner, friction-law, and work-metric contracts close before any B4/B7 promotion",
        ],
        "forbidden_without_contract": [
            "promote endpoint-incompatible rows from diagnostic algorithm-literal probes",
            "claim exact-T source-policy errors for h rows that overrun T=10",
            "use compatible endpoint-grid rows as source-policy rows before runner equivalence is closed",
        ],
    }


def main() -> None:
    spec = read_json(PAPER / "TFE_SOURCE_POLICY_SPEC.json")
    rows: list[dict[str, Any]] = []
    tolerance = 1.0e-12
    for case in spec.get("source_policy", {}).get("cases", []):
        t_final = float(case["t_final"])
        for h in unique_h_values(case):
            endpoint_fields = endpoint_policy_fields(t_final, h)
            mismatch = float(endpoint_fields["t_final_mismatch"])
            case_id = case.get("case_id")
            rows.append(
                {
                    "row_id": row_id(case_id, h),
                    "case_id": case_id,
                    "friction_enabled": bool(case.get("friction_enabled")),
                    "t_final": t_final,
                    "h": h,
                    **endpoint_fields,
                    "integer_step_compatible": mismatch <= tolerance,
                    "source_endpoint_policy_needed_for_exact_T": mismatch > tolerance,
                }
            )

    incompatible = [row for row in rows if not row["integer_step_compatible"]]
    compatible = [row for row in rows if row["integer_step_compatible"]]
    source_text_audit = source_text_endpoint_convention_audit(rows)
    source_grid_policy_resolved_for_exact_T_compatible_rows = (
        bool(compatible)
        and source_text_audit.get("algorithm_literal_constant_h_until_tn_ge_tfinal") is True
    )
    compatible_row_ids = [row["row_id"] for row in compatible]
    incompatible_row_ids = [row["row_id"] for row in incompatible]
    row_disposition = row_level_promotion_disposition(rows)
    acceptance_contract = endpoint_policy_acceptance_contract(compatible_row_ids, incompatible_row_ids)
    endpoint_grid_subclosure = {
        "source_grid_policy_resolved_for_exact_T_compatible_rows": (
            source_grid_policy_resolved_for_exact_T_compatible_rows
        ),
        "endpoint_compatible_rows_source_endpoint_convention_resolved": len(compatible),
        "endpoint_incompatible_rows_require_source_endpoint_policy": len(incompatible),
        "source_endpoint_compatible_row_ids": compatible_row_ids,
        "source_endpoint_incompatible_row_ids": incompatible_row_ids,
        "source_endpoint_incompatible_row_ids_demoted_from_source_policy": incompatible_row_ids,
        "endpoint_incompatible_rows_demoted_from_source_policy": len(incompatible),
        "source_policy_rows_completed": 0,
        "source_grid_policy_resolved_for_full_T10": False,
        "boundary": (
            "Only rows whose published h divides T=10 exactly are endpoint-grid resolved. "
            "Rows whose published h does not divide T=10 remain demoted from source-policy "
            "promotion until the source endpoint/output sampling convention is established; "
            "no source-policy reproduction row is closed by this audit."
        ),
    }
    result = {
        "schema": "tfe-source-grid-compatibility-audit-v1",
        "status": "source_horizon_step_grid_policy_open",
        "submission_ready": False,
        "source_policy_rows_completed": 0,
        "external_superiority_claim_allowed": False,
        "source_policy_spec": "TFE_SOURCE_POLICY_SPEC.json",
        "row_count": len(rows),
        "integer_step_compatible_rows": len(compatible),
        "integer_step_incompatible_rows": len(incompatible),
        "all_source_h_values_integer_step_compatible": len(incompatible) == 0,
        "frictionless_incompatible_rows": sum(
            1 for row in incompatible if row["case_id"] == "frictionless_pendulum"
        ),
        "frictional_incompatible_rows": sum(
            1 for row in incompatible if row["case_id"] == "frictional_pendulum"
        ),
        "source_grid_policy_resolved_for_exact_T_compatible_rows": (
            source_grid_policy_resolved_for_exact_T_compatible_rows
        ),
        "endpoint_compatible_rows_source_endpoint_convention_resolved": len(compatible),
        "endpoint_incompatible_rows_require_source_endpoint_policy": len(incompatible),
        "endpoint_incompatible_rows_demoted_from_source_policy": len(incompatible),
        "source_endpoint_compatible_row_ids": compatible_row_ids,
        "source_endpoint_incompatible_row_ids": incompatible_row_ids,
        "source_endpoint_incompatible_row_ids_demoted_from_source_policy": incompatible_row_ids,
        "endpoint_grid_subclosure": endpoint_grid_subclosure,
        "row_level_promotion_disposition": row_disposition,
        "endpoint_policy_acceptance_contract": acceptance_contract,
        "source_grid_policy_resolved_for_full_T10": False,
        "source_text_endpoint_convention_audit": source_text_audit,
        "endpoint_convention_candidates": [
            {
                "policy": "nearest_integer_horizon",
                "source_equivalent": False,
                "keeps_published_h": True,
                "keeps_exact_T": False,
                "acceptance_use": "diagnostic_only_until_source_endpoint_convention_is_verified",
            },
            {
                "policy": "algorithm_literal_fixed_h_until_tn_ge_tfinal",
                "source_equivalent": False,
                "keeps_published_h": True,
                "keeps_exact_T": False,
                "acceptance_use": "diagnostic_only_because_the_text_does_not_state_error_sampling_at_noninteger_T_overruns",
            },
            {
                "policy": "adjust_h_to_hit_T_exactly",
                "source_equivalent": False,
                "keeps_published_h": False,
                "keeps_exact_T": True,
                "acceptance_use": "diagnostic_only_because_published_h_is_changed",
            },
            {
                "policy": "integer_steps_plus_final_partial_step",
                "source_equivalent": False,
                "keeps_published_h": True,
                "keeps_exact_T": True,
                "acceptance_use": "diagnostic_only_unless_source_code_or_paper_confirms_partial_final_step",
            },
        ],
        "required_to_accept_full_T10_rows": [
            "verify the source paper/source code endpoint convention for h values that do not divide T=10",
            "identify whether Algorithm 1's fixed-h loop uses overrun, interpolation, adjusted h, or a final partial step for reported errors",
            "record whether the accepted convention keeps published h, exact T, or both",
            "keep endpoint-incompatible rows demoted from the source-policy row set unless that convention is source-confirmed",
            "rerun the TFE m=1/m=2/Newmark/trapezoidal rows with the verified convention",
            "keep source_policy_rows_completed at zero until the convention and method runner are source-equivalent",
        ],
        "interpretation": (
            "The extracted source-policy horizon is T=10. Two published frictional h values "
            "divide T exactly and are endpoint-grid resolved under the source text's fixed-h "
            "loop convention, but several other published h values do not divide T exactly. "
            "Those endpoint-incompatible rows are explicitly demoted from source-policy promotion "
            "until the source paper or source code establishes the endpoint/output sampling convention."
        ),
        "rows": rows,
        "execution_policy": {
            "read_only_existing_artifacts": True,
            "default_1e_4_required": False,
            "heavy_numerical_run_invoked": False,
            "run_v047_invoked": False,
            "v048_runner_invoked": False,
        },
    }
    with OUT_JSON.open("w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")

    lines = [
        "# TFE Source Grid Compatibility Audit",
        "",
        "Status: **source horizon step-grid policy open**.",
        "",
        f"- Source-policy rows completed: `{result['source_policy_rows_completed']}`.",
        f"- Rows checked: `{result['row_count']}`.",
        f"- Integer-step compatible rows: `{result['integer_step_compatible_rows']}`.",
        f"- Integer-step incompatible rows: `{result['integer_step_incompatible_rows']}`.",
        f"- Exact-T compatible rows with endpoint-grid convention resolved: `{result['endpoint_compatible_rows_source_endpoint_convention_resolved']}`.",
        f"- Endpoint-incompatible rows requiring source endpoint policy: `{result['endpoint_incompatible_rows_require_source_endpoint_policy']}`.",
        f"- Endpoint-incompatible rows demoted from source-policy row set: `{result['endpoint_incompatible_rows_demoted_from_source_policy']}`.",
        f"- Exact-T compatible subset grid policy resolved: `{result['source_grid_policy_resolved_for_exact_T_compatible_rows']}`.",
        f"- Full T=10 grid policy resolved: `{result['source_grid_policy_resolved_for_full_T10']}`.",
        f"- External superiority claim allowed: `{result['external_superiority_claim_allowed']}`.",
        f"- Endpoint row dispositions recorded: `{len(row_disposition)}`.",
        f"- Endpoint-compatible future-execution candidates: `{len(compatible_row_ids)}`.",
        f"- Endpoint-incompatible blocked rows: `{len(incompatible_row_ids)}`.",
        f"- Endpoint-incompatible demoted rows: `{len(incompatible_row_ids)}`.",
        "",
        "## Endpoint-Grid Subclosure",
        "",
        endpoint_grid_subclosure["boundary"],
        "",
        f"- Compatible row IDs: `{compatible_row_ids}`.",
        f"- Incompatible row IDs: `{incompatible_row_ids}`.",
        f"- Demoted incompatible row IDs: `{incompatible_row_ids}`.",
        "",
        "## Rows",
        "",
        "| row id | case | friction | h | T/h | nearest steps | nearest T | mismatch | compatible |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| `{row['row_id']}` | `{row['case_id']}` | `{row['friction_enabled']}` | `{row['h']:.6g}` | "
            f"`{row['exact_steps']:.12g}` | `{row['nearest_integer_steps']}` | "
            f"`{row['nearest_integer_t_final']:.12g}` | `{row['t_final_mismatch']:.3e}` | "
            f"`{row['integer_step_compatible']}` |"
        )
    lines.extend(
        [
            "",
            "## Row-Level Promotion Disposition",
            "",
            "| row id | endpoint disposition | source-policy eligible now | required before promotion |",
            "|---|---|---:|---|",
        ]
    )
    for item in row_disposition:
        requirements = "; ".join(item["required_before_promotion"])
        lines.append(
            f"| `{item['row_id']}` | `{item['endpoint_grid_disposition']}` | "
            f"`{item['source_policy_execution_eligible_now']}` | {requirements} |"
        )
    lines.extend(
        [
            "",
            "## Endpoint Policy Acceptance Contract",
            "",
            (
                "- Exact-T compatible subset can enter future execution after runner contracts: "
                f"`{acceptance_contract['exact_T_compatible_subset_can_enter_future_execution_after_runner_contracts']}`."
            ),
            f"- Exact-T compatible row IDs: `{compatible_row_ids}`.",
            f"- Endpoint-incompatible blocked row IDs: `{incompatible_row_ids}`.",
            f"- Endpoint-incompatible demoted row IDs: `{acceptance_contract['endpoint_incompatible_rows_demoted_from_source_policy']}`.",
            f"- Demotion contract: {acceptance_contract['endpoint_incompatible_demotion_contract']}",
            "- Full T=10 source-policy promotion requires:",
        ]
    )
    lines.extend(f"  - {item}." for item in acceptance_contract["full_T10_source_policy_promotion_requires"])
    lines.extend(["", "- Forbidden without contract:"])
    lines.extend(f"  - {item}." for item in acceptance_contract["forbidden_without_contract"])
    lines.extend(["", result["interpretation"]])
    lines.extend(
        [
            "",
            "## Source-Text Endpoint Convention Audit",
            "",
            f"- Source text available/anchors: `{source_text_audit['source_text_available']}/{source_text_audit['anchor_count']}`.",
            f"- Algorithm-literal fixed-h loop detected: `{source_text_audit['algorithm_literal_constant_h_until_tn_ge_tfinal']}`.",
            f"- Endpoint convention resolved for error sampling: `{source_text_audit['source_endpoint_convention_resolved_for_error_sampling']}`.",
            f"- Adjusted-h/partial-final-step/interpolation/floor-nearest confirmation: `{source_text_audit['source_text_confirms_adjusted_h_for_exact_T']}/{source_text_audit['source_text_confirms_partial_final_step']}/{source_text_audit['source_text_confirms_interpolation_to_exact_T']}/{source_text_audit['source_text_confirms_floor_or_nearest_endpoint_sampling']}`.",
            "",
            "| line | finding |",
            "|---:|---|",
        ]
    )
    for anchor in source_text_audit["anchors"]:
        lines.append(f"| `{anchor['line']}` | {anchor['finding']} |")
    lines.extend(
        [
            "",
            "### Algorithm-Literal Terminal Times",
            "",
            "| case | h | steps | terminal time | overshoot | exact T |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for row in source_text_audit["algorithm_literal_rows"]:
        lines.append(
            f"| `{row['case_id']}` | `{row['h']:.6g}` | `{row['steps_to_reach_or_exceed_T']}` | "
            f"`{row['algorithm_literal_terminal_time']:.12g}` | `{row['algorithm_literal_overshoot']:.3e}` | "
            f"`{row['hits_exact_T']}` |"
        )
    lines.extend(
        [
            "",
            "## Endpoint Convention Candidates",
            "",
            "| policy | keeps published h | keeps exact T | source-equivalent now | accepted use |",
            "|---|---:|---:|---:|---|",
        ]
    )
    for item in result["endpoint_convention_candidates"]:
        lines.append(
            f"| `{item['policy']}` | `{item['keeps_published_h']}` | `{item['keeps_exact_T']}` | "
            f"`{item['source_equivalent']}` | {item['acceptance_use']} |"
        )
    lines.extend(
        [
            "",
            "## Required To Accept Full T=10 Rows",
            "",
        ]
    )
    for item in result["required_to_accept_full_T10_rows"]:
        lines.append(f"- {item}.")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("tfe_source_grid_compatibility_audit=written")
    print(f"rows={result['row_count']}")
    print(f"integer_step_incompatible_rows={result['integer_step_incompatible_rows']}")
    print(
        "endpoint_compatible_rows_source_endpoint_convention_resolved="
        f"{result['endpoint_compatible_rows_source_endpoint_convention_resolved']}"
    )
    print("source_grid_policy_resolved_for_full_T10=False")
    print("source_policy_rows_completed=0")


if __name__ == "__main__":
    main()
