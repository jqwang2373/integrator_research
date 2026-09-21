#!/usr/bin/env python3
"""Runtime row-layout oracle for the accepted v047 Gauss6/FullVA residual."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


PAPER = Path(__file__).resolve().parent
ROOT = PAPER.parent
RUN = ROOT.parent / "numerics" / "v047_cylindrical_chain_pipeline" / "run_v047.py"
GATE_MD = PAPER / "DYNAMIC_ROW_ORACLE_GATE.md"
GATE_JSON = PAPER / "DYNAMIC_ROW_ORACLE_GATE.json"
CERT = PAPER / "IMPLEMENTATION_FIDELITY_CERTIFICATE.md"
BLOCKER = PAPER / "CMAME_BLOCKER_CLOSURE_GATE.json"
MANIFEST = PAPER / "SUBMISSION_ARTIFACT_MANIFEST.json"


EXPECTED_LAYOUT = [
    ("translational_position_weak_defect", 0, 6, 18),
    ("rotational_lie_position_weak_defect", 6, 6, 18),
    ("translational_velocity_weak_defect", 12, 6, 18),
    ("angular_velocity_weak_defect", 18, 6, 18),
    ("newton_euler_weak_balance", 24, 12, 36),
    ("lower_pair_index3_weak_constraints", 36, 8, 24),
]

FORMULA_ORACLE_FAMILIES = [
    "translational_position_weak_defect",
    "rotational_lie_position_weak_defect",
    "translational_velocity_weak_defect",
    "angular_velocity_weak_defect",
    "lower_pair_index3_weak_constraints",
]

FULL_FORMULA_ORACLE_FAMILIES = [
    "translational_position_weak_defect",
    "rotational_lie_position_weak_defect",
    "translational_velocity_weak_defect",
    "angular_velocity_weak_defect",
    "newton_euler_weak_balance",
    "lower_pair_index3_weak_constraints",
]


class Checks:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def check(self, condition: bool, message: str) -> None:
        if not condition:
            self.errors.append(message)


def read_text(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8", errors="replace")


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a JSON object")
    return data


def contains_normalized(text: str, token: str) -> bool:
    return token in text or " ".join(token.split()) in " ".join(text.split())


def import_run_module() -> Any:
    spec = importlib.util.spec_from_file_location("run_v047_dynamic_row_oracle", RUN)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load import spec for {RUN}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def build_probe_args(module: Any) -> tuple[Any, ...]:
    params = module.make_params(0.50)
    state = module.initial_state(params)
    state0 = (
        module.jnp.asarray(state.r),
        module.jnp.asarray(state.p),
        module.jnp.asarray(state.v),
        module.jnp.asarray(state.w),
    )
    return (
        state0,
        0.04,
        module.jnp.asarray(params.masses),
        module.jnp.asarray(params.Js),
        module.jnp.asarray(params.s_prev),
        module.jnp.asarray(params.s_next),
        module.jnp.asarray(params.axis_prev),
        module.jnp.asarray(params.axis_next),
        module.jnp.asarray(params.twist_prev),
        module.jnp.asarray(params.twist_next),
        module.jnp.asarray(params.ground_axis),
        module.jnp.asarray(params.ground_twist),
        module.jnp.asarray(params.joint_basis),
        module.jnp.asarray(params.gravity),
        module.jnp.asarray(params.external_forces_world),
        module.jnp.asarray(params.external_torques_body),
        params.mu_s,
        params.mu_d,
        params.stribeck_velocity,
        params.viscous_damping,
        params.friction_radius,
    )


def weighted_family_from_residual(module: Any, residual: Any, h: float, family_name: str) -> Any:
    _, _, b = module.qp._gauss_legendre_coefficients_jax(module.N_STAGES, residual.dtype)
    h_value = module.jnp.asarray(h, dtype=residual.dtype)
    pieces = []
    for stage, row_slice in enumerate(module.stage_row_family_slices_np()[family_name]):
        weight = module.jnp.sqrt(h_value * b[stage])
        pieces.append(weight * residual[row_slice])
    return module.jnp.concatenate(pieces)


def residual_family(module: Any, residual: Any, family_name: str) -> Any:
    return module.jnp.concatenate([residual[row_slice] for row_slice in module.stage_row_family_slices_np()[family_name]])


def accepted_residual_family_major(module: Any, residual: Any) -> Any:
    return module.jnp.concatenate([residual_family(module, residual, name) for name in FULL_FORMULA_ORACLE_FAMILIES])


def deterministic_probe_vectors(module: Any) -> list[tuple[str, Any]]:
    grid = module.jnp.arange(module.DIM, dtype=module.jnp.float64) + 1.0
    return [
        ("deterministic_small_sine_DIM_vector", 1.0e-3 * module.jnp.sin(grid)),
        ("deterministic_small_cosine_DIM_vector", 7.5e-4 * module.jnp.cos(1.7 * grid)),
        ("deterministic_mixed_sine_cosine_DIM_vector", 5.0e-4 * (module.jnp.sin(0.5 * grid) + module.jnp.cos(2.3 * grid))),
    ]


def independent_formula_rows(module: Any, x: Any, *args: Any) -> dict[str, Any]:
    """Reassemble formula rows without reading residual or block slices."""
    (
        state0,
        h,
        masses,
        Js,
        s_prev,
        s_next,
        axis_prev,
        axis_next,
        twist_prev,
        twist_next,
        ground_axis,
        ground_twist,
        joint_basis,
        gravity,
        external_forces_world,
        external_torques_body,
        mu_s,
        mu_d,
        stribeck_velocity,
        viscous_damping,
        friction_radius,
    ) = args
    r0, p0, v0, w0 = state0
    h_value = module.jnp.asarray(h, dtype=x.dtype)
    _, A, _ = module.qp._gauss_legendre_coefficients_jax(module.N_STAGES, x.dtype)
    stages = module.unpack_stages(x)
    params_arrays = (
        s_prev,
        s_next,
        axis_prev,
        axis_next,
        twist_prev,
        twist_next,
        ground_axis,
        ground_twist,
        joint_basis,
    )

    stage_kin = []
    for st in stages:
        p = [module.compose_right_quat_jax_safe(p0[i], st["u"][i]) for i in range(module.N_BODIES)]
        rotations = [module.qp.quat_to_rot_jax(p[i]) for i in range(module.N_BODIES)]
        stage_kin.append(module.joint_kinematics_jax(st, rotations, params_arrays, x.dtype))

    initial_state = {
        "r": r0,
        "v": v0,
        "w": w0,
        "a": module.jnp.zeros_like(v0),
        "alpha": module.jnp.zeros_like(w0),
    }
    initial_rotations = [module.qp.quat_to_rot_jax(p0[i]) for i in range(module.N_BODIES)]
    initial_kin = module.joint_kinematics_jax(initial_state, initial_rotations, params_arrays, x.dtype)

    rows: dict[str, list[Any]] = {name: [] for name in FULL_FORMULA_ORACLE_FAMILIES}
    for si in range(module.N_STAGES):
        kin = stage_kin[si]
        st = stages[si]
        R = [module.qp.quat_to_rot_jax(module.compose_right_quat_jax_safe(p0[i], st["u"][i])) for i in range(module.N_BODIES)]
        joint_force = []
        for joint in range(module.N_JOINTS):
            lam = st["lambda"][joint]
            normal_force = lam[0] * joint_basis[joint, 0] + lam[1] * joint_basis[joint, 1]
            normal_load = module.jnp.sqrt(normal_force @ normal_force + module.jnp.array(1.0e-24, dtype=x.dtype))
            slide_vel = kin["rel_vel"][joint] @ kin["parent_axis"][joint]
            friction = module.brown_mcphee_scalar_jax(
                slide_vel,
                normal_load,
                mu_s,
                mu_d,
                stribeck_velocity,
                viscous_damping,
                friction_radius,
            )
            joint_force.append(normal_force + friction * kin["parent_axis"][joint])

        pvel = []
        u_block = []
        pacc = []
        w_block = []
        dyn = []
        constraints = []
        for joint in range(module.N_JOINTS):
            axis = kin["parent_axis"][joint]
            r_coll_axis = (
                kin["rel_point"][joint]
                - initial_kin["rel_point"][joint]
                - h_value * sum(A[si, sj] * stage_kin[sj]["rel_vel"][joint] for sj in range(module.N_STAGES))
            ) @ axis
            v_coll_axis = (
                kin["rel_vel"][joint]
                - initial_kin["rel_vel"][joint]
                - h_value * sum(A[si, sj] * stage_kin[sj]["rel_acc"][joint] for sj in range(module.N_STAGES))
            ) @ axis
            spin_coll_axis = (
                kin["twist_angle"][joint]
                - initial_kin["twist_angle"][joint]
                - h_value * sum(A[si, sj] * stage_kin[sj]["rel_spin_vel"][joint] for sj in range(module.N_STAGES))
            )
            spin_acc_coll_axis = (
                kin["rel_spin_vel"][joint]
                - initial_kin["rel_spin_vel"][joint]
                - h_value * sum(A[si, sj] * stage_kin[sj]["rel_spin_acc"][joint] for sj in range(module.N_STAGES))
            )
            pvel.append(
                module.jnp.array(
                    [
                        kin["rel_vel"][joint] @ joint_basis[joint, 0],
                        kin["rel_vel"][joint] @ joint_basis[joint, 1],
                        r_coll_axis,
                    ],
                    dtype=x.dtype,
                )
            )
            u_block.append(module.jnp.concatenate([kin["axis_rate"][joint], module.jnp.array([spin_coll_axis], dtype=x.dtype)]))
            pacc.append(
                module.jnp.array(
                    [
                        kin["rel_acc"][joint] @ joint_basis[joint, 0],
                        kin["rel_acc"][joint] @ joint_basis[joint, 1],
                        v_coll_axis,
                    ],
                    dtype=x.dtype,
                )
            )
            w_block.append(module.jnp.concatenate([kin["axis_acc"][joint], module.jnp.array([spin_acc_coll_axis], dtype=x.dtype)]))
            constraints.append(module.jnp.concatenate([joint_basis[joint] @ kin["rel_point"][joint], kin["axis_res"][joint]]))
        for body in range(module.N_BODIES):
            force = joint_force[body]
            if body == 0:
                force = force - joint_force[1]
            trans = masses[body] * st["a"][body] - masses[body] * gravity - external_forces_world[body] - force
            prox_torque = module.jnp.cross(s_prev[body], R[body].T @ joint_force[body])
            if body == 0:
                distal_torque = module.jnp.cross(s_next[0], R[0].T @ (-joint_force[1]))
            else:
                distal_torque = module.jnp.zeros(3, dtype=x.dtype)
            eta_prox = st["lambda"][body, 2:4]
            axis_torque = eta_prox[0] * module.jnp.cross(axis_prev[body], R[body].T @ joint_basis[body, 0])
            axis_torque += eta_prox[1] * module.jnp.cross(axis_prev[body], R[body].T @ joint_basis[body, 1])
            if body == 0:
                eta_dist = st["lambda"][1, 2:4]
                dist_axis_torque = eta_dist[0] * module.jnp.cross(axis_next[0], R[0].T @ joint_basis[1, 0])
                dist_axis_torque += eta_dist[1] * module.jnp.cross(axis_next[0], R[0].T @ joint_basis[1, 1])
            else:
                dist_axis_torque = module.jnp.zeros(3, dtype=x.dtype)
            rot = (
                Js[body] @ st["alpha"][body]
                + module.jnp.cross(st["w"][body], Js[body] @ st["w"][body])
                - prox_torque
                - distal_torque
                - axis_torque
                + dist_axis_torque
                - external_torques_body[body]
            )
            dyn.extend([trans, rot])
        rows["translational_position_weak_defect"].append(module.jnp.concatenate(pvel))
        rows["rotational_lie_position_weak_defect"].append(module.jnp.concatenate(u_block))
        rows["translational_velocity_weak_defect"].append(module.jnp.concatenate(pacc))
        rows["angular_velocity_weak_defect"].append(module.jnp.concatenate(w_block))
        rows["newton_euler_weak_balance"].append(module.jnp.concatenate(dyn))
        rows["lower_pair_index3_weak_constraints"].append(module.jnp.concatenate(constraints))

    return {name: module.jnp.concatenate(parts) for name, parts in rows.items()}


def independent_formula_family_major_vector(module: Any, x: Any, *args: Any) -> Any:
    rows = independent_formula_rows(module, x, *args)
    return module.jnp.concatenate([rows[name] for name in FULL_FORMULA_ORACLE_FAMILIES])


def accepted_jacobian_family_major(module: Any, jacobian: Any) -> Any:
    pieces = []
    slices = module.stage_row_family_slices_np()
    for family_name in FULL_FORMULA_ORACLE_FAMILIES:
        pieces.extend(jacobian[row_slice, :] for row_slice in slices[family_name])
    return module.jnp.concatenate(pieces, axis=0)


def main() -> int:
    checks = Checks()
    try:
        gate_md = read_text(GATE_MD)
        gate = read_json(GATE_JSON)
        cert = read_text(CERT)
        blocker = read_json(BLOCKER)
        manifest = read_json(MANIFEST)
        module = import_run_module()
    except Exception as exc:  # noqa: BLE001 - concise CLI failure.
        print(f"dynamic_row_oracle_gate=FAIL\n- {exc}")
        return 1

    checks.check(gate.get("schema") == "dynamic-row-oracle-gate-v2", "gate schema changed")
    checks.check(
        gate.get("status") == "runtime_row_and_block_oracle_passable_symbolic_oracle_open",
        "gate status changed",
    )
    checks.check(
        "runtime/symbolic-oracle gate only" in gate.get("scope_note", ""),
        "dynamic row oracle scope note missing",
    )
    checks.check(gate.get("accepted_method") == "Gauss6/FullVA", "accepted method changed")
    checks.check(gate.get("accepted_residual") == "residual_cylindrical_chain", "accepted residual changed")
    checks.check(gate.get("accepted_jacobian") == "R_JAC_jacfwd_argnums0", "accepted Jacobian changed")
    checks.check(
        gate.get("accepted_block_functional") == "R_INDEPENDENT_STAGE_FUNCTIONAL_BLOCKS",
        "accepted block-functional path changed",
    )

    checks.check(module.N_BODIES == 2, "N_BODIES changed")
    checks.check(module.N_JOINTS == 2, "N_JOINTS changed")
    checks.check(module.N_STAGES == 3, "N_STAGES changed")
    checks.check(module.BODY_SIZE == 18, "BODY_SIZE changed")
    checks.check(module.LAMBDA_SIZE == 4, "LAMBDA_SIZE changed")
    checks.check(module.STAGE_SIZE == 44, "STAGE_SIZE changed")
    checks.check(module.DIM == 132, "DIM changed")
    checks.check(list(module.STAGE_FUNCTIONAL_BLOCK_LAYOUT) == [(name, offset, width) for name, offset, width, _ in EXPECTED_LAYOUT], "stage layout changed")

    slices = module.stage_row_family_slices_np()
    covered: list[int] = []
    for name, offset, width, total_rows in EXPECTED_LAYOUT:
        family_slices = slices.get(name)
        checks.check(family_slices is not None and len(family_slices) == module.N_STAGES, f"{name} slice count changed")
        if family_slices is None:
            continue
        family_rows: list[int] = []
        for stage, row_slice in enumerate(family_slices):
            expected_start = stage * module.STAGE_SIZE + offset
            expected_stop = expected_start + width
            checks.check(row_slice.start == expected_start and row_slice.stop == expected_stop, f"{name} stage {stage} slice changed")
            family_rows.extend(range(row_slice.start, row_slice.stop))
        checks.check(len(family_rows) == total_rows, f"{name} total row count changed")
        covered.extend(family_rows)
    checks.check(sorted(covered) == list(range(module.DIM)), "row slices do not exactly cover 0..131")
    checks.check(len(set(covered)) == module.DIM, "row slices overlap")

    try:
        x = module.jnp.zeros((module.DIM,), dtype=module.jnp.float64)
        args = build_probe_args(module)
        residual = module.residual_cylindrical_chain(x, *args)
        jacobian = module.R_JAC(x, *args)
        residual_norm = float(module.jnp.linalg.norm(residual))
        jacobian_norm = float(module.jnp.linalg.norm(jacobian))
    except Exception as exc:  # noqa: BLE001 - reports runtime oracle failures.
        checks.check(False, f"runtime residual/Jacobian probe failed: {exc}")
        residual = None
        jacobian = None
        residual_norm = float("nan")
        jacobian_norm = float("nan")

    block_errors: dict[str, float] = {}
    max_block_error = float("nan")
    formula_errors: dict[str, float] = {}
    max_formula_error = float("nan")
    full_formula_errors: dict[str, float] = {}
    max_full_formula_error = float("nan")
    max_formula_jacobian_error = float("nan")
    multi_probe_count = 0
    try:
        probe_vectors = deterministic_probe_vectors(module)
        cross_x = probe_vectors[0][1]
        cross_residual = module.residual_cylindrical_chain(cross_x, *args)
        cross_blocks = module.R_INDEPENDENT_STAGE_FUNCTIONAL_BLOCKS(cross_x, *args)
        checks.check(len(cross_blocks) == len(EXPECTED_LAYOUT), "block-functional family count changed")
        for block, (name, _, _, total_rows) in zip(cross_blocks, EXPECTED_LAYOUT, strict=True):
            expected_family = weighted_family_from_residual(module, cross_residual, float(args[1]), name)
            diff = block - expected_family
            error = float(module.jnp.max(module.jnp.abs(diff)))
            block_errors[name] = error
            checks.check(tuple(block.shape) == (total_rows,), f"{name} block-functional shape changed")
            checks.check(bool(module.jnp.all(module.jnp.isfinite(block))), f"{name} block-functional values are non-finite")
        max_block_error = max(block_errors.values()) if block_errors else float("nan")
        formula_rows = independent_formula_rows(module, cross_x, *args)
        for name in FORMULA_ORACLE_FAMILIES:
            expected_family = residual_family(module, cross_residual, name)
            diff = formula_rows[name] - expected_family
            error = float(module.jnp.max(module.jnp.abs(diff)))
            formula_errors[name] = error
            checks.check(tuple(formula_rows[name].shape) == tuple(expected_family.shape), f"{name} formula row shape changed")
            checks.check(bool(module.jnp.all(module.jnp.isfinite(formula_rows[name]))), f"{name} formula rows are non-finite")
        max_formula_error = max(formula_errors.values()) if formula_errors else float("nan")
        for name in FULL_FORMULA_ORACLE_FAMILIES:
            expected_family = residual_family(module, cross_residual, name)
            diff = formula_rows[name] - expected_family
            error = float(module.jnp.max(module.jnp.abs(diff)))
            full_formula_errors[name] = error
            checks.check(tuple(formula_rows[name].shape) == tuple(expected_family.shape), f"{name} full formula row shape changed")
            checks.check(bool(module.jnp.all(module.jnp.isfinite(formula_rows[name]))), f"{name} full formula rows are non-finite")
        max_full_formula_error = max(full_formula_errors.values()) if full_formula_errors else float("nan")
        formula_jacobian = module.jax.jacfwd(lambda z: independent_formula_family_major_vector(module, z, *args))(cross_x)
        accepted_jacobian = accepted_jacobian_family_major(module, module.R_JAC(cross_x, *args))
        jacobian_diff = formula_jacobian - accepted_jacobian
        max_formula_jacobian_error = float(module.jnp.max(module.jnp.abs(jacobian_diff)))
        checks.check(tuple(formula_jacobian.shape) == (module.DIM, module.DIM), "formula Jacobian shape changed")
        checks.check(tuple(accepted_jacobian.shape) == (module.DIM, module.DIM), "accepted reordered Jacobian shape changed")
        checks.check(bool(module.jnp.all(module.jnp.isfinite(formula_jacobian))), "formula Jacobian has non-finite values")
        multi_probe_count = 1
        for probe_name, probe_x in probe_vectors[1:]:
            probe_residual = module.residual_cylindrical_chain(probe_x, *args)
            probe_formula_vector = independent_formula_family_major_vector(module, probe_x, *args)
            probe_expected_vector = accepted_residual_family_major(module, probe_residual)
            probe_formula_error = float(module.jnp.max(module.jnp.abs(probe_formula_vector - probe_expected_vector)))
            max_full_formula_error = max(max_full_formula_error, probe_formula_error)
            probe_formula_jacobian = module.jax.jacfwd(lambda z: independent_formula_family_major_vector(module, z, *args))(probe_x)
            probe_accepted_jacobian = accepted_jacobian_family_major(module, module.R_JAC(probe_x, *args))
            probe_jacobian_error = float(module.jnp.max(module.jnp.abs(probe_formula_jacobian - probe_accepted_jacobian)))
            max_formula_jacobian_error = max(max_formula_jacobian_error, probe_jacobian_error)
            checks.check(tuple(probe_formula_vector.shape) == (module.DIM,), f"{probe_name} formula vector shape changed")
            checks.check(tuple(probe_formula_jacobian.shape) == (module.DIM, module.DIM), f"{probe_name} formula Jacobian shape changed")
            checks.check(bool(module.jnp.all(module.jnp.isfinite(probe_formula_vector))), f"{probe_name} formula vector has non-finite values")
            checks.check(bool(module.jnp.all(module.jnp.isfinite(probe_formula_jacobian))), f"{probe_name} formula Jacobian has non-finite values")
            multi_probe_count += 1
    except Exception as exc:  # noqa: BLE001 - reports runtime oracle failures.
        checks.check(False, f"runtime block/formula cross-check failed: {exc}")
        max_block_error = float("nan")
        max_formula_error = float("nan")
        max_full_formula_error = float("nan")
        max_formula_jacobian_error = float("nan")
        multi_probe_count = 0

    if residual is not None and jacobian is not None:
        checks.check(tuple(residual.shape) == (132,), "runtime residual shape changed")
        checks.check(tuple(jacobian.shape) == (132, 132), "runtime Jacobian shape changed")
        checks.check(bool(module.jnp.all(module.jnp.isfinite(residual))), "runtime residual has non-finite values")
        checks.check(bool(module.jnp.all(module.jnp.isfinite(jacobian))), "runtime Jacobian has non-finite values")
        checks.check(residual_norm > 0.0, "runtime residual norm should be positive for the zero-stage probe")
        checks.check(jacobian_norm > 0.0, "runtime Jacobian norm should be positive")
        for name, *_ in EXPECTED_LAYOUT:
            family_values = module.jnp.concatenate([residual[row_slice] for row_slice in slices[name]])
            checks.check(bool(module.jnp.all(module.jnp.isfinite(family_values))), f"{name} runtime values are non-finite")

    boundary = gate.get("acceptance_boundary", {})
    checks.check(boundary.get("runtime_residual_shape_checked") is True, "runtime residual shape boundary changed")
    checks.check(boundary.get("runtime_jacobian_shape_checked") is True, "runtime Jacobian shape boundary changed")
    checks.check(boundary.get("runtime_row_partition_checked") is True, "runtime row partition boundary changed")
    checks.check(boundary.get("runtime_finite_values_checked") is True, "runtime finite-values boundary changed")
    checks.check(boundary.get("runtime_block_functional_crosscheck_checked") is True, "runtime block-functional boundary changed")
    checks.check(
        boundary.get("partial_independent_formula_rows_checked") is True,
        "partial formula-row oracle boundary changed",
    )
    checks.check(
        boundary.get("full_independent_formula_rows_checked") is True,
        "full formula-row oracle boundary changed",
    )
    checks.check(
        boundary.get("formula_row_ad_jacobian_checked") is True,
        "formula-row AD Jacobian boundary changed",
    )
    checks.check(
        boundary.get("formula_row_ad_jacobian_multi_probe_checked") is True,
        "formula-row AD Jacobian multi-probe boundary changed",
    )
    checks.check(
        boundary.get("partial_kinematic_stage_defect_certificate_checked") is True,
        "partial kinematic stage-defect certificate boundary changed",
    )
    checks.check(
        boundary.get("block_functional_is_gauss6_equivalent_not_symbolic") is True,
        "block-functional caveat boundary changed",
    )
    checks.check(boundary.get("independent_symbolic_row_oracle_complete") is False, "symbolic oracle incorrectly marked complete")
    checks.check(boundary.get("stage_residual_O_h7_implementation_defect_proved") is False, "O(h^7) implementation defect incorrectly marked proved")
    checks.check(
        "direct-substitution sidecars close" in boundary.get(
            "stage_residual_O_h7_implementation_defect_proved_scope", ""
        ),
        "stage-residual scope note missing from dynamic row oracle gate",
    )
    checks.check(boundary.get("full_tfe_stage_replacement") is False, "full-TFE replacement marker changed")
    checks.check(boundary.get("submission_ready") is False, "submission-ready marker changed")

    crosscheck = gate.get("runtime_block_functional_crosscheck", {})
    tolerance = float(crosscheck.get("tolerance", 1.0e-10))
    checks.check(crosscheck.get("checked") is True, "block-functional cross-check marker changed")
    checks.check(crosscheck.get("stage_vector") == "deterministic_small_sine_DIM_vector", "block-functional stage vector changed")
    checks.check(crosscheck.get("row_family_count") == 6, "block-functional row-family count changed")
    checks.check(crosscheck.get("symbolic_oracle_complete") is False, "block-functional cross-check incorrectly closes symbolic oracle")
    checks.check(max_block_error <= tolerance, f"block-functional mismatch too large: {max_block_error:.3e} > {tolerance:.3e}")

    formula_oracle = gate.get("partial_independent_formula_row_oracle", {})
    formula_tolerance = float(formula_oracle.get("tolerance", 1.0e-10))
    checks.check(formula_oracle.get("checked") is True, "partial formula-row oracle marker changed")
    checks.check(formula_oracle.get("stage_vector") == "deterministic_small_sine_DIM_vector", "partial formula-row stage vector changed")
    checks.check(formula_oracle.get("row_families") == FORMULA_ORACLE_FAMILIES, "partial formula-row family list changed")
    checks.check(formula_oracle.get("row_count") == 96, "partial formula-row count changed")
    checks.check(formula_oracle.get("excluded_row_family") == "newton_euler_weak_balance", "partial formula-row exclusion changed")
    checks.check(formula_oracle.get("symbolic_oracle_complete") is False, "partial formula-row oracle incorrectly closes symbolic oracle")
    checks.check(max_formula_error <= formula_tolerance, f"formula-row mismatch too large: {max_formula_error:.3e} > {formula_tolerance:.3e}")

    full_formula_oracle = gate.get("full_independent_formula_row_oracle", {})
    full_formula_tolerance = float(full_formula_oracle.get("tolerance", 1.0e-10))
    checks.check(full_formula_oracle.get("checked") is True, "full formula-row oracle marker changed")
    checks.check(full_formula_oracle.get("stage_vector") == "deterministic_small_sine_DIM_vector", "full formula-row stage vector changed")
    checks.check(full_formula_oracle.get("row_families") == FULL_FORMULA_ORACLE_FAMILIES, "full formula-row family list changed")
    checks.check(full_formula_oracle.get("row_count") == 132, "full formula-row count changed")
    checks.check(full_formula_oracle.get("added_row_family") == "newton_euler_weak_balance", "full formula-row added family changed")
    checks.check(full_formula_oracle.get("runtime_formula_row_oracle_complete") is True, "full formula-row runtime-complete marker changed")
    checks.check(full_formula_oracle.get("symbolic_oracle_complete") is False, "full formula-row oracle incorrectly closes symbolic oracle")
    checks.check(
        full_formula_oracle.get("stage_residual_O_h7_implementation_defect_proved") is False,
        "full formula-row oracle incorrectly proves O(h^7) implementation defect",
    )
    checks.check(
        max_full_formula_error <= full_formula_tolerance,
        f"full formula-row mismatch too large: {max_full_formula_error:.3e} > {full_formula_tolerance:.3e}",
    )

    formula_jacobian_oracle = gate.get("formula_row_ad_jacobian_oracle", {})
    formula_jacobian_tolerance = float(formula_jacobian_oracle.get("tolerance", 1.0e-10))
    checks.check(formula_jacobian_oracle.get("checked") is True, "formula-row AD Jacobian oracle marker changed")
    checks.check(formula_jacobian_oracle.get("stage_vector") == "deterministic_small_sine_DIM_vector", "formula-row AD Jacobian stage vector changed")
    checks.check(formula_jacobian_oracle.get("multi_probe_checked") is True, "formula-row AD Jacobian multi-probe marker changed")
    checks.check(formula_jacobian_oracle.get("probe_count") == 3, "formula-row AD Jacobian probe count changed")
    checks.check(formula_jacobian_oracle.get("row_count") == 132, "formula-row AD Jacobian row count changed")
    checks.check(formula_jacobian_oracle.get("column_count") == 132, "formula-row AD Jacobian column count changed")
    checks.check(
        formula_jacobian_oracle.get("relation_checked")
        == "jax.jacfwd(independent_formula_family_major_vector) equals accepted R_JAC in row-family-major order",
        "formula-row AD Jacobian relation changed",
    )
    checks.check(formula_jacobian_oracle.get("symbolic_oracle_complete") is False, "formula-row AD Jacobian oracle incorrectly closes symbolic oracle")
    checks.check(
        formula_jacobian_oracle.get("stage_residual_O_h7_implementation_defect_proved") is False,
        "formula-row AD Jacobian oracle incorrectly proves O(h^7) implementation defect",
    )
    checks.check(
        max_formula_jacobian_error <= formula_jacobian_tolerance,
        f"formula-row AD Jacobian mismatch too large: {max_formula_jacobian_error:.3e} > {formula_jacobian_tolerance:.3e}",
    )
    checks.check(multi_probe_count == 3, f"formula-row AD Jacobian probe count runtime changed: {multi_probe_count}")

    partial_defect = gate.get("partial_kinematic_stage_defect_certificate", {})
    checks.check(partial_defect.get("checked") is True, "partial kinematic defect certificate marker changed")
    checks.check(
        partial_defect.get("source") == "KINEMATIC_ROW_DEFECT_CERTIFICATE.json",
        "partial kinematic defect certificate source changed",
    )
    checks.check(partial_defect.get("row_families") == FORMULA_ORACLE_FAMILIES, "partial kinematic defect families changed")
    checks.check(partial_defect.get("row_count") == 96, "partial kinematic defect row count changed")
    checks.check(
        partial_defect.get("excluded_row_family") == "newton_euler_weak_balance",
        "partial kinematic defect excluded family changed",
    )
    checks.check(
        partial_defect.get("partial_stage_defect_certificate") is True,
        "partial kinematic stage-defect marker missing",
    )
    checks.check(partial_defect.get("symbolic_oracle_complete") is False, "partial kinematic defect overclaims symbolic oracle")
    checks.check(
        partial_defect.get("stage_residual_O_h7_implementation_defect_proved") is False,
        "partial kinematic defect overclaims full O(h^7) proof",
    )

    for token in [
        "Dynamic Row Oracle Gate",
        "RUNTIME ROW AND BLOCK-FUNCTIONAL ORACLE PASSABLE - SYMBOLIC ORACLE OPEN",
        "residual_cylindrical_chain",
        "R_JAC = jax.jacfwd(residual_cylindrical_chain, argnums=0)",
        "R_INDEPENDENT_STAGE_FUNCTIONAL_BLOCKS",
        "residual shape: `(132,)`",
        "Jacobian shape: `(132,132)`",
        "block-functional cross-check",
        "partial independent formula-row oracle",
        "96 non-dynamic rows",
        "full independent formula-row oracle",
        "132 runtime formula rows",
        "formula-row AD Jacobian oracle",
        "multi-probe formula-row AD Jacobian oracle",
        "Partial Kinematic Defect Certificate",
        "KINEMATIC_ROW_DEFECT_CERTIFICATE.md/json",
        "max formula-row Jacobian mismatch",
        "max weighted-family mismatch",
        "max formula-row mismatch",
        "max full formula-row mismatch",
        "independent symbolic row oracle remains open",
        "stage_residual_O_h7_proved_by_this_runtime_gate=false",
        "dynamic_symbolic_oracle_complete_by_this_runtime_gate=false",
        "direct-substitution proof sidecars record the accepted direct stage-residual route separately",
        "validate_dynamic_row_oracle_gate.py",
    ]:
        checks.check(contains_normalized(gate_md, token), f"DYNAMIC_ROW_ORACLE_GATE.md missing token: {token}")

    checks.check("static source-identity audit" in cert, "implementation certificate lost static-audit marker")
    checks.check(
        blocker.get("blockers", [{}])[0].get("id") == "B1",
        "blocker ledger B1 ordering changed",
    )
    checks.check(
        "DYNAMIC_ROW_ORACLE_GATE.md" in manifest.get("evidence_anchors", []),
        "manifest missing dynamic row oracle evidence anchor",
    )
    checks.check(
        "DYNAMIC_ROW_ORACLE_GATE.json" in manifest.get("evidence_anchors", []),
        "manifest missing dynamic row oracle JSON anchor",
    )
    checks.check(
        "validate_dynamic_row_oracle_gate.py" in manifest.get("validators", []),
        "manifest missing dynamic row oracle validator",
    )
    checks.check(
        "KINEMATIC_ROW_DEFECT_CERTIFICATE.md" in manifest.get("evidence_anchors", []),
        "manifest missing partial kinematic defect certificate anchor",
    )
    checks.check(
        "validate_kinematic_row_defect_certificate.py" in manifest.get("validators", []),
        "manifest missing partial kinematic defect certificate validator",
    )

    if checks.errors:
        print("dynamic_row_oracle_gate=FAIL")
        for error in checks.errors:
            print(f"- {error}")
        return 1

    print("dynamic_row_oracle_gate=PASS")
    print("accepted_residual=residual_cylindrical_chain")
    print("accepted_jacobian=R_JAC_jacfwd_argnums0")
    print("residual_shape=132")
    print("jacobian_shape=132x132")
    print("row_family_count=6")
    print("partial_formula_row_oracle=PASS")
    print("partial_formula_row_count=96")
    print(f"max_formula_row_mismatch={max_formula_error:.6e}")
    print("full_formula_row_oracle=PASS")
    print("full_formula_row_count=132")
    print(f"max_full_formula_row_mismatch={max_full_formula_error:.6e}")
    print("formula_row_ad_jacobian_oracle=PASS")
    print("formula_row_ad_jacobian_probe_count=3")
    print(f"max_formula_row_jacobian_mismatch={max_formula_jacobian_error:.6e}")
    print("partial_kinematic_stage_defect_certificate_checked=True")
    print("partial_kinematic_stage_defect_rows=96")
    print(f"runtime_residual_norm={residual_norm:.6e}")
    print(f"runtime_jacobian_norm={jacobian_norm:.6e}")
    print("block_functional_crosscheck=PASS")
    print(f"max_block_functional_mismatch={max_block_error:.6e}")
    print("symbolic_oracle_complete=False")
    print("block_functional_symbolic_oracle=False")
    print("runtime_symbolic_lane_stage_residual_O_h7_implementation_defect_proved=False")
    print("full_tfe_stage_replacement=False")
    return 0


if __name__ == "__main__":
    sys.exit(main())
