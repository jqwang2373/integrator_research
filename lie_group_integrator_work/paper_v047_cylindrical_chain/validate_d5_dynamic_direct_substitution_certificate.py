#!/usr/bin/env python3
"""Validate the D5 dynamic direct-substitution certificate candidate."""

from __future__ import annotations

import json
import sys
from pathlib import Path


PAPER = Path(__file__).resolve().parent


class Checks:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def check(self, condition: bool, message: str) -> None:
        if not condition:
            self.errors.append(message)


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def main() -> int:
    checks = Checks()
    try:
        cert = read_json(PAPER / "D5_DYNAMIC_DIRECT_SUBSTITUTION_CERTIFICATE.json")
        md = read_text(PAPER / "D5_DYNAMIC_DIRECT_SUBSTITUTION_CERTIFICATE.md")
        kinematic = read_json(PAPER / "KINEMATIC_ROW_DEFECT_CERTIFICATE.json")
        balance = read_json(PAPER / "NEWTON_EULER_BALANCE_IDENTITY_AUDIT.json")
        virtual_work = read_json(PAPER / "NEWTON_EULER_VIRTUAL_WORK_WRENCH_AUDIT.json")
        smooth = read_json(PAPER / "SMOOTH_FORCE_LIFT_CERTIFICATE.json")
        d6 = read_json(PAPER / "NEWTON_EULER_ROW_ORDERING_SCALING_AD_AUDIT.json")
        obstruction = read_json(PAPER / "D5_P_STATE_PS3_H_ACC_INPUT_OBSTRUCTION_AUDIT.json")
    except Exception as exc:  # noqa: BLE001
        print(f"D5 dynamic direct-substitution certificate validation: FAIL\n- {exc}")
        return 1

    summary = cert.get("summary", {})
    closed = cert.get("closed_input_evidence", {})
    forbidden = cert.get("forbidden_shortcuts", {})
    rows = cert.get("row_proofs", [])
    row_blocks = {row.get("balance_block") for row in rows if isinstance(row, dict)}
    row_residuals = {row.get("residual_after_substitution") for row in rows if isinstance(row, dict)}

    checks.check(cert.get("schema") == "d5-dynamic-direct-substitution-certificate-v1", "schema changed")
    checks.check(
        cert.get("status") == "direct_substitution_certificate_closed",
        "status changed",
    )
    checks.check(cert.get("read_only") is True, "certificate must be read-only")
    checks.check(cert.get("submission_ready") is False, "certificate must not mark submission ready")
    checks.check(
        cert.get("direct_route_mathematical_certificate_closed") is True,
        "direct-route mathematical certificate not closed",
    )
    checks.check(cert.get("direct_route_non_circular") is True, "direct route not marked non-circular")
    checks.check(
        cert.get("stage_residual_O_h7_by_direct_route") is True,
        "direct route does not certify O(h^7)",
    )
    checks.check(summary.get("dynamic_rows") == len(rows) == 36, "dynamic row count changed")
    checks.check(summary.get("translational_rows") == 18, "translational row count changed")
    checks.check(summary.get("rotational_rows") == 18, "rotational row count changed")
    checks.check(summary.get("dynamic_zero_residual_rows") == 36, "dynamic zero rows changed")
    checks.check(summary.get("dynamic_O_h7_rows_by_zero_remainder") == 36, "O(h^7) row count changed")
    checks.check(
        summary.get("certified_non_dynamic_rows")
        == kinematic.get("proof_scope", {}).get("certified_row_count")
        == 96,
        "certified non-dynamic row count changed",
    )
    checks.check(summary.get("full_stage_rows_if_promoted") == 132, "full row count if promoted changed")
    checks.check(summary.get("forbidden_shortcuts_used") == 0, "forbidden shortcut count changed")
    checks.check(summary.get("direct_route_certificate_closed") is True, "direct route certificate not closed")
    checks.check(row_blocks == {"translational_newton_balance", "rotational_euler_balance"}, "row blocks changed")
    checks.check(row_residuals == {"0"}, "not all row residuals are zero")
    checks.check(
        all(row.get("bound_proved_by_direct_substitution") is True for row in rows if isinstance(row, dict)),
        "some row does not prove the bound by direct substitution",
    )
    checks.check(
        all(row.get("uses_state_lift_rate_input") is False for row in rows if isinstance(row, dict)),
        "state lift-rate input used by a row",
    )
    checks.check(
        all(row.get("uses_acceleration_lift_rate_input") is False for row in rows if isinstance(row, dict)),
        "acceleration lift-rate input used by a row",
    )
    checks.check(
        all(row.get("uses_multiplier_lift_rate_input") is False for row in rows if isinstance(row, dict)),
        "multiplier lift-rate input used by a row",
    )
    checks.check(
        all(row.get("uses_finite_probe_as_proof") is False for row in rows if isinstance(row, dict)),
        "finite probe used as proof by a row",
    )
    checks.check(
        all(row.get("uses_residual_to_error_promotion") is False for row in rows if isinstance(row, dict)),
        "residual-to-error promotion used by a row",
    )
    checks.check(all(value is False for value in forbidden.values()), "a forbidden shortcut is enabled")
    checks.check(
        closed.get("d1_d2_balance_identity_closed")
        == (balance.get("balance_identity_closed") is True)
        is True,
        "D1/D2 balance identity not linked closed",
    )
    checks.check(
        closed.get("d1_d2_balance_identity_closed_rows")
        == balance.get("summary", {}).get("balance_identity_closed_rows")
        == 36,
        "D1/D2 balance identity row count changed",
    )
    checks.check(
        closed.get("d3_multiplier_wrench_consistency_closed")
        == (virtual_work.get("multiplier_wrench_consistency_closed") is True)
        is True,
        "D3 multiplier wrench not linked closed",
    )
    checks.check(
        closed.get("d3_row_expanded_virtual_work_identity_proved")
        == (virtual_work.get("row_expanded_virtual_work_identity_proved") is True)
        is True,
        "D3 row-expanded identity not linked closed",
    )
    checks.check(
        closed.get("d4_smooth_force_lift_closed")
        == (smooth.get("smooth_force_lift_consistency_closed") is True)
        is True,
        "D4 smooth force lift not linked closed",
    )
    checks.check(
        closed.get("d4_c7_bound_proved")
        == (smooth.get("global_C7_tube_derivative_bound_proved") is True)
        is True,
        "D4 C7 bound not linked closed",
    )
    checks.check(
        closed.get("d6_row_ordering_scaling_ad_closed")
        == (d6.get("row_ordering_scaling_ad_closed") is True)
        is True,
        "D6 row ordering/scaling/AD not linked closed",
    )
    checks.check(
        cert.get("obstruction_resolution", {}).get("recommended_route")
        == obstruction.get("summary", {}).get("recommended_non_circular_close_route")
        == "full_132_row_dynamic_residual_route",
        "h-acceleration obstruction route not linked",
    )
    strict_taylor_status = cert.get("strict_taylor_status", "")
    checks.check(
        "direct-route residual remainder is zero" in strict_taylor_status
        and "does not certify the primitive 162-subterm Taylor lane" in strict_taylor_status,
        "direct route residual-remainder boundary missing from certificate",
    )
    checks.check(
        "row-local Taylor remainder" not in strict_taylor_status
        and "Row-local Taylor status" not in md,
        "stale direct-route Taylor-remainder wording returned",
    )
    for token in [
        "direct-substitution certificate closed",
        "zero-residual",
        "No `P_state` actual PS3 estimate is used",
        "active PC2 closure route",
        "full 132-row residual route",
        "Direct-route residual-remainder status",
        "Primitive Taylor lane status",
        "does not certify the primitive 162-subterm Taylor lane",
    ]:
        checks.check(token in md, f"missing markdown token: {token}")

    if checks.errors:
        print("D5 dynamic direct-substitution certificate validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("D5 dynamic direct-substitution certificate validation: PASS")
    print(f"dynamic_zero_residual_rows={summary.get('dynamic_zero_residual_rows')}")
    print(f"full_stage_rows_if_promoted={summary.get('full_stage_rows_if_promoted')}")
    print(f"direct_route_certificate_closed={summary.get('direct_route_certificate_closed')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
