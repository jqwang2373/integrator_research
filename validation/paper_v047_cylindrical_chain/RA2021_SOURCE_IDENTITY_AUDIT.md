# RA2021 Source Identity Audit

Status: `source_output_time_grid_policy_extracted_promotion_still_open`.

This read-only audit inspects the public RA2021 C2 SimEngineMBD source path and the existing v048 RA2021 rows. It does not rerun `run_v047.py`, does not launch v048 runners, and does not run a default `1e-4` campaign.

## Confirmed From Source

- The public setup exposes `form in {rp,rA,reps}`, `mode in {kin,dyn,kinematics,dynamics}`, optional `--tol`, default `T=3`, and default `h=1e-3`.
- The example model output arrays store `pos_data=body.r`, `vel_data=body.dr`, and `acc_data=body.ddr` for four-link, slider-crank, and double-pendulum.
- The formulation systems assign translational velocity from the first translational block into `body.dr`.
- The public saved output time grid is `np.linspace(0, T, int(T/h), endpoint=True)`, so the saved-time interval is `T/(int(T/h)-1)` while the integrator step size remains `h`.

## Existing Artifact Alignment

- Public order summary rows: `9/9` plus double-pendulum groups `3`.
- Public order groups total: `12/12`.
- Raw order rows: `36/36`.
- Timing rows: `12/12`.
- Forms: `rA,reps,rp`.
- Models: `double_pendulum,four_link,single_pendulum,slider_crank`.
- T values: `[3.0]`.

## Claim Boundary

- Output mapping verified from source: `True`.
- Time-grid policy extracted from source: `True`.
- RA2021 forensic rows with position-aligned velocity mismatch: `9`.
- RA2021 forensic rows with velocity nonmonotone/floor-limited issues: `1`.
- The velocity-mismatch rows are no longer treated as an unknown `body.dr` output-mapping problem; they remain source-policy promotion blockers because the local Gauss6 row, error norm, time-grid, runtime, and Newton policy are not yet bound into one accepted RA2021 same-policy comparison.
- Source-policy rows closed by this audit: `0`.
- Can close RA2021 B2 requirement now: `False`.
- External-superiority claim allowed: `False`.

Validator: `validate_ra2021_source_identity_audit.py`.
