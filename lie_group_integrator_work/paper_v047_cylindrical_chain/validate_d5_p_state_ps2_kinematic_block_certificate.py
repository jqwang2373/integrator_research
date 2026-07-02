#!/usr/bin/env python3
"""Validate the D5 P_state PS2 kinematic-block certificate."""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
CERT_JSON = PAPER / "D5_P_STATE_PS2_KINEMATIC_BLOCK_CERTIFICATE.json"
CERT_MD = PAPER / "D5_P_STATE_PS2_KINEMATIC_BLOCK_CERTIFICATE.md"


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


def close_to(value: object, expected: float, tol: float = 1.0e-12) -> bool:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return False
    return math.isfinite(number) and abs(number - expected) <= tol


def main() -> int:
    checks = Checks()
    try:
        cert = read_json(CERT_JSON)
        cert_md = CERT_MD.read_text(encoding="utf-8", errors="replace")
        ps2_target = read_json(PAPER / "D5_P_STATE_PS2_WEIGHTED_TARGET_AUDIT.json")
        p_state_gap = read_json(PAPER / "D5_P_STATE_LIFT_GAP_AUDIT.json")
        p_tube = read_json(PAPER / "D5_P_TUBE_CONSTANTS_AUDIT.json")
        p_state_map = read_json(PAPER / "D5_P_STATE_MAP_DEFINITION_AUDIT.json")
        p_state_anti = read_json(PAPER / "D5_P_STATE_ANTICIRCULARITY_AUDIT.json")
    except Exception as exc:  # noqa: BLE001
        print(f"D5 P_state PS2 kinematic-block certificate validation: FAIL\n- {exc}")
        return 1

    constants = cert.get("constants", {})
    dims = cert.get("dimensions", {})
    source = cert.get("source_consistency", {})
    manuscript = cert.get("manuscript_link", {})

    checks.check(cert.get("schema") == "d5-p-state-ps2-kinematic-block-certificate-v1", "schema changed")
    checks.check(
        cert.get("status") == "ps2_kinematic_block_certificate_recorded_binding_gap_open",
        "status changed",
    )
    checks.check(cert.get("read_only") is True, "certificate must be read-only")
    checks.check(cert.get("run_v047_invoked") is False, "run_v047 must not be invoked")
    checks.check(cert.get("submission_ready") is False, "submission readiness overclaimed")
    checks.check(cert.get("pc2_closed") is False, "PC2 unexpectedly closed")
    checks.check(cert.get("proof_gap_closed") is False, "proof gap unexpectedly closed")
    checks.check(cert.get("primitive_id") == "P_state_lift", "primitive id changed")
    checks.check(cert.get("primitive_closed") is False, "P_state unexpectedly closed")
    checks.check(cert.get("ps2_kinematic_block_certificate_recorded") is True, "certificate marker missing")
    checks.check(
        cert.get("certifies_uniform_euclidean_kinematic_subblock_bound") is True,
        "Euclidean kinematic subblock bound not certified",
    )
    checks.check(cert.get("certifies_full_nonlinear_ps2") is False, "full nonlinear PS2 overclaimed")
    checks.check(cert.get("ps2_inverse_or_infsup_closed") is False, "PS2 unexpectedly closed")
    checks.check(cert.get("ps3_state_lift_conversion_closed") is False, "PS3 unexpectedly closed")
    checks.check(cert.get("certifies_induced_taylor_bounds") is False, "Taylor bounds overclaimed")
    checks.check(cert.get("certifies_dynamic_row_defect") is False, "dynamic row defect overclaimed")
    checks.check(close_to(constants.get("h_max"), 0.04), "h_max changed")
    checks.check(float(constants.get("gauss_matrix_2_norm", 0.0)) > 0.6, "Gauss norm too small")
    checks.check(float(constants.get("kinematic_inverse_template_2_norm_at_h_max", 0.0)) > 1.0, "template norm too small")
    checks.check(
        float(constants.get("simple_triangle_bound", 0.0))
        >= float(constants.get("kinematic_inverse_template_2_norm_at_h_max", 0.0)),
        "triangle bound does not dominate template norm",
    )
    checks.check(dims.get("stages") == 3 and dims.get("bodies") == 2, "stage/body dimensions changed")
    checks.check(dims.get("state_block_dimension") == 72, "state dimension changed")
    checks.check(dims.get("auxiliary_acceleration_dimension") == 36, "acceleration dimension changed")
    checks.check(dims.get("kinematic_row_dimension") == 72, "kinematic row dimension changed")
    checks.check(dims.get("lower_pair_surplus_rows_not_needed_for_subblock") == 24, "lower-pair surplus rows changed")
    checks.check(dims.get("non_dynamic_row_dimension") == 96, "non-dynamic row dimension changed")
    checks.check(len(cert.get("remaining_binding_gaps", [])) == 3, "remaining binding gap list changed")
    checks.check(
        "rotational Lie-chart" in cert.get("remaining_binding_gaps", [""])[0],
        "rotational Lie-chart binding gap missing",
    )
    checks.check(source.get("ps2_target_schema") == ps2_target.get("schema"), "PS2 target source link missing")
    checks.check(
        source.get("ps2_target_spec_closed") is True and ps2_target.get("ps2_target_spec_closed") is True,
        "PS2 target spec not linked as closed",
    )
    checks.check(
        source.get("ps2_target_infsup_closed") is False
        and ps2_target.get("ps2_inverse_or_infsup_closed") is False,
        "PS2 target unexpectedly closed",
    )
    checks.check(
        source.get("p_state_gap_closed") is False and p_state_gap.get("primitive_closed") is False,
        "P_state gap unexpectedly closed",
    )
    checks.check(source.get("p_tube_closed") is True and p_tube.get("primitive_closed") is True, "P_tube not linked")
    checks.check(
        source.get("p_state_map_definition_closed") is True
        and p_state_map.get("ps1_map_definition_closed") is True,
        "P_state map definition not linked",
    )
    checks.check(
        source.get("p_state_anticircularity_closed") is True
        and p_state_anti.get("ps4_anticircularity_closed") is True,
        "P_state anti-circularity not linked",
    )
    checks.check(manuscript.get("main_tex_present") is True, "main TeX lemma missing")
    checks.check(manuscript.get("flat_tex_present") is True, "flat TeX lemma missing")

    for token in [
        "Status: **PS2 kinematic-block certificate recorded; binding gap remains open**.",
        "Kinematic subblock certificate recorded: `True`.",
        "Uniform Euclidean kinematic subblock bound certified: `True`.",
        "Full nonlinear PS2 certified: `False`.",
        "Kinematic rows / lower-pair surplus rows: `72` / `24`.",
        "Step threshold: `0 < h <= 0.04`.",
        "PS2 closed: `False`.",
        "Primitive/Taylor PC2 route closed: `False`.",
        "delta R_q = delta q - h A_G delta v",
        "delta v = delta R_v + A_G (h delta a)",
        "The full nonlinear PS2 inverse or inf-sup proof remains open.",
    ]:
        checks.check(token in cert_md, f"markdown missing token: {token}")

    if checks.errors:
        print("D5 P_state PS2 kinematic-block certificate validation: FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("D5 P_state PS2 kinematic-block certificate validation: PASS")
    print(f"kinematic_inverse_template_norm={constants.get('kinematic_inverse_template_2_norm_at_h_max'):.12e}")
    print("ps2_closed=False")
    print("pc2_closed=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
