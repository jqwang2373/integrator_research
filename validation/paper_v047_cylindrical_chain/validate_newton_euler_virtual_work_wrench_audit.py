#!/usr/bin/env python3
"""Validate the D3 virtual-work wrench row-expanded identity audit."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
AUDIT_JSON = PAPER / "NEWTON_EULER_VIRTUAL_WORK_WRENCH_AUDIT.json"
AUDIT_MD = PAPER / "NEWTON_EULER_VIRTUAL_WORK_WRENCH_AUDIT.md"


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


def expected_rows() -> list[int]:
    rows: list[int] = []
    for stage in range(3):
        rows.extend(range(stage * 44 + 24, stage * 44 + 36))
    return rows


def main() -> int:
    checks = Checks()
    try:
        audit = read_json(AUDIT_JSON)
        audit_md = read_text(AUDIT_MD)
        manifest = read_json(PAPER / "SUBMISSION_ARTIFACT_MANIFEST.json")
    except Exception as exc:  # noqa: BLE001
        print(f"newton_euler_virtual_work_wrench_audit=FAIL\n- {exc}")
        return 1

    summary = audit.get("summary", {})
    runtime = audit.get("runtime_source_audit", {})
    template_identity = audit.get("template_virtual_work_identity_audit", {})
    row_expanded_identity = audit.get("row_expanded_virtual_work_identity_audit", {})
    rows = audit.get("row_audit", [])
    sites = audit.get("site_summaries", [])

    checks.check(audit.get("schema") == "newton-euler-virtual-work-wrench-audit-v1", "schema changed")
    checks.check(
        audit.get("status") == "d3_row_expanded_virtual_work_identity_checked_dynamic_defect_open",
        "status changed",
    )
    checks.check(audit.get("submission_ready") is False, "submission readiness overclaimed")
    checks.check(audit.get("proof_gap_closed") is False, "proof gap unexpectedly closed")
    checks.check(
        audit.get("proof_gap_closed_scope")
        == (
            "local_d3_virtual_work_audit_only; this audit is an input to the later "
            "direct D5/PC2 closure and does not by itself close the dynamic O(h^7) "
            "defect"
        ),
        "D3 local proof-gap scope missing",
    )
    checks.check(
        "Local D3 audit proof gap closed" in audit_md
        and "Proof gap closed scope" in audit_md,
        "D3 proof-gap wording not scoped in markdown",
    )
    checks.check(
        audit.get("dynamic_symbolic_oracle_complete") is False,
        "dynamic symbolic oracle unexpectedly complete",
    )
    checks.check(
        audit.get("stage_residual_O_h7_implementation_defect_proved") is False,
        "O(h^7) implementation defect unexpectedly proved",
    )
    checks.check(
        audit.get("multiplier_wrench_consistency_closed") is True,
        "multiplier wrench consistency not closed",
    )
    checks.check(
        audit.get("template_virtual_work_identity_proved") is True,
        "template virtual-work identity not proved",
    )
    checks.check(
        audit.get("row_expanded_virtual_work_identity_proved") is True,
        "row-expanded virtual-work identity not proved",
    )
    checks.check(
        audit.get("full_row_expanded_virtual_work_identity_proved") is True,
        "full row-expanded virtual-work identity not proved",
    )
    checks.check(summary.get("row_count") == 36, "row count changed")
    checks.check(summary.get("checked_rows") == 36, "checked row count changed")
    checks.check(
        summary.get("template_virtual_work_identity_rows") == 36,
        "template virtual-work identity row count changed",
    )
    checks.check(
        summary.get("template_virtual_work_identity_proved") is True,
        "summary template virtual-work identity not proved",
    )
    checks.check(summary.get("template_identity_count") == 2, "template identity count changed")
    checks.check(summary.get("template_identity_count_proved") == 2, "proved template identity count changed")
    checks.check(
        summary.get("row_expanded_virtual_work_identity_rows") == 36,
        "row-expanded virtual-work identity row count changed",
    )
    checks.check(
        summary.get("row_expanded_virtual_work_identity_proved") is True,
        "summary row-expanded virtual-work identity not proved",
    )
    checks.check(summary.get("row_expanded_identity_count") == 6, "row-expanded identity count changed")
    checks.check(
        summary.get("row_expanded_identity_count_proved") == 6,
        "proved row-expanded identity count changed",
    )
    checks.check(summary.get("row_expanded_point_identity_count") == 3, "point identity count changed")
    checks.check(summary.get("row_expanded_axis_identity_count") == 3, "axis identity count changed")
    checks.check(summary.get("translational_row_count") == 18, "translational row count changed")
    checks.check(summary.get("rotational_row_count") == 18, "rotational row count changed")
    checks.check(summary.get("body0_rows_checked") == 18, "body0 checked rows changed")
    checks.check(summary.get("body1_rows_checked") == 18, "body1 checked rows changed")
    checks.check(summary.get("site_count") == 9, "site count changed")
    checks.check(summary.get("site_count_checked") == 9, "checked site count changed")
    checks.check(summary.get("virtual_work_sign_skeleton_checked") is True, "sign skeleton not checked")
    checks.check(
        summary.get("multiplier_wrench_consistency_closed") is True,
        "summary multiplier wrench consistency not closed",
    )
    checks.check(
        summary.get("full_row_expanded_virtual_work_identity_proved") is True,
        "summary row-expanded virtual-work proof not closed",
    )

    checks.check(runtime.get("source_file") == "v047_cylindrical_chain_pipeline/run_v047.py", "runtime source changed")
    checks.check(runtime.get("residual_function_found") is True, "residual function not found")
    checks.check(runtime.get("sign_skeleton_source_checked") is True, "runtime sign skeleton source not checked")
    runtime_checks = runtime.get("checks", {})
    for key in [
        "body_force_initialized_from_local_joint",
        "body0_distal_force_subtracted",
        "proximal_moment_arm_uses_positive_joint_force",
        "body0_distal_moment_arm_uses_negative_joint1_force",
        "proximal_axis_torque_uses_positive_eta",
        "body0_distal_axis_torque_uses_joint1_eta",
        "rotational_residual_sign_pattern",
    ]:
        checks.check(runtime_checks.get(key) is True, f"runtime source check not satisfied: {key}")
    checks.check("not an O(h^7) defect certificate" in runtime.get("scope", ""), "runtime scope boundary missing")

    checks.check(template_identity.get("checked") is True, "template identity audit not checked")
    checks.check(template_identity.get("identity_count") == 2, "template identity count changed")
    checks.check(template_identity.get("proved_identity_count") == 2, "template proved identity count changed")
    for item in template_identity.get("identities", []):
        checks.check(item.get("proved") is True, f"template identity {item.get('id')} not proved")
        checks.check(item.get("simplified_difference") == "0", f"template identity {item.get('id')} not zero")
    checks.check(
        "does not prove row-expanded runtime equivalence" in template_identity.get("scope", ""),
        "template identity scope boundary missing",
    )

    checks.check(row_expanded_identity.get("checked") is True, "row-expanded identity audit not checked")
    checks.check(row_expanded_identity.get("identity_count") == 6, "row-expanded identity count changed")
    checks.check(
        row_expanded_identity.get("proved_identity_count") == 6,
        "row-expanded proved identity count changed",
    )
    checks.check(row_expanded_identity.get("point_identity_count") == 3, "point row-expanded identity count changed")
    checks.check(row_expanded_identity.get("axis_identity_count") == 3, "axis row-expanded identity count changed")
    for item in row_expanded_identity.get("identities", []):
        checks.check(item.get("proved") is True, f"row-expanded identity {item.get('id')} not proved")
        checks.check(item.get("simplified_difference") == "0", f"row-expanded identity {item.get('id')} not zero")
    checks.check(
        "does not include Brown-McPhee friction" in row_expanded_identity.get("scope", ""),
        "row-expanded identity scope boundary missing friction exclusion",
    )
    checks.check(
        "O(h^7) dynamic-row defect proof" in row_expanded_identity.get("scope", ""),
        "row-expanded identity scope boundary missing dynamic-defect exclusion",
    )

    checks.check([row.get("global_row") for row in rows] == expected_rows(), "global row sequence changed")
    for row in rows:
        checks.check(row.get("virtual_work_sign_skeleton_checked") is True, f"row {row.get('global_row')} unchecked")
        checks.check(
            row.get("template_virtual_work_identity_proved") is True,
            f"row {row.get('global_row')} missing template identity",
        )
        checks.check(
            row.get("row_expanded_virtual_work_identity_proved") is True,
            f"row {row.get('global_row')} missing row-expanded identity",
        )
        checks.check(
            row.get("multiplier_wrench_consistency_closed") is True,
            f"row {row.get('global_row')} did not close multiplier consistency",
        )
        checks.check(
            row.get("full_row_expanded_virtual_work_identity_proved") is True,
            f"row {row.get('global_row')} did not prove row-expanded virtual-work identity",
        )
        checks.check(
            row.get("stage_residual_O_h7_implementation_defect_proved") is False,
            f"row {row.get('global_row')} overclaims O(h^7)",
        )
        sites_for_row = row.get("expected_virtual_work_sites", [])
        if row.get("balance_block") == "translational_newton_balance" and row.get("body") == 0:
            checks.check(
                sites_for_row == ["joint0_child_body0_force_plus", "joint1_parent_body0_force_minus"],
                f"row {row.get('global_row')} body0 translational sites changed",
            )
        if row.get("balance_block") == "translational_newton_balance" and row.get("body") == 1:
            checks.check(
                sites_for_row == ["joint1_child_body1_force_plus"],
                f"row {row.get('global_row')} body1 translational sites changed",
            )

    site_counts = {site.get("site"): site.get("covered_rows") for site in sites}
    expected_site_counts = {
        "joint0_child_body0_force_plus": 9,
        "joint1_child_body1_force_plus": 9,
        "joint1_parent_body0_force_minus": 9,
        "joint0_child_body0_moment_plus": 9,
        "joint1_child_body1_moment_plus": 9,
        "joint1_parent_body0_moment_minus": 9,
        "joint0_child_body0_axis_torque_plus": 9,
        "joint1_child_body1_axis_torque_plus": 9,
        "joint1_parent_body0_axis_torque_minus": 9,
    }
    checks.check(site_counts == expected_site_counts, "virtual-work site coverage changed")

    for token in [
        "D3 row-expanded virtual-work identity checked, dynamic-defect proof open",
        "Virtual-work sign skeleton checked rows: `36`",
        "Template virtual-work identity rows: `36`",
        "Template virtual-work identity proved: `True`",
        "Template identities proved: `2/2`",
        "Row-expanded virtual-work identity rows: `36`",
        "Row-expanded virtual-work identity proved: `True`",
        "Row-expanded identities proved: `6/6`",
        "Multiplier wrench consistency closed: `True`",
        "Full row-expanded virtual-work identity proved: `True`",
        "Stage residual O(h^7) implementation defect proved: `False`",
        "Validator: `validate_newton_euler_virtual_work_wrench_audit.py`.",
    ]:
        checks.check(token in audit_md, f"MD missing token: {token}")

    checks.check(
        manifest.get("newton_euler_virtual_work_wrench_audit")
        == "NEWTON_EULER_VIRTUAL_WORK_WRENCH_AUDIT.md",
        "manifest missing virtual-work audit path",
    )
    checks.check(
        manifest.get("newton_euler_virtual_work_wrench_audit_json")
        == "NEWTON_EULER_VIRTUAL_WORK_WRENCH_AUDIT.json",
        "manifest missing virtual-work audit JSON path",
    )
    checks.check(
        "NEWTON_EULER_VIRTUAL_WORK_WRENCH_AUDIT.md" in manifest.get("evidence_anchors", []),
        "manifest missing virtual-work audit anchor",
    )
    checks.check(
        "NEWTON_EULER_VIRTUAL_WORK_WRENCH_AUDIT.json" in manifest.get("evidence_anchors", []),
        "manifest missing virtual-work audit JSON anchor",
    )
    checks.check(
        "validate_newton_euler_virtual_work_wrench_audit.py" in manifest.get("validators", []),
        "manifest missing virtual-work audit validator",
    )

    if checks.errors:
        print("newton_euler_virtual_work_wrench_audit=FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("newton_euler_virtual_work_wrench_audit=PASS")
    print("checked_rows=36")
    print("template_virtual_work_identity_proved=True")
    print("row_expanded_virtual_work_identity_proved=True")
    print("multiplier_wrench_consistency_closed=True")
    print("full_row_expanded_virtual_work_identity_proved=True")
    print("local_d3_audit_proof_gap_closed=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
