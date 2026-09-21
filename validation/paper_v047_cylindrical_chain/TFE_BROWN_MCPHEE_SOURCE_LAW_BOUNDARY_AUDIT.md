# TFE Brown--McPhee Source-Law Boundary Audit

Status: **source formula structure encoded; surrogate is not source-code equivalent**.

This audit is read-only over existing TFE artifacts, local v021/v022 provenance, and source text.

- Candidate friction law encoded: `True`.
- Published formula structure encoded: `True`.
- Source-code-equivalent law: `False`.
- Transition velocity resolved from source: `False`.
- Source-policy rows promoted: `0`.
- Frictional source-policy rows demoted: `True`.
- Non-heavy contract block closed: `False`.
- Source-policy execution allowed now/invoked/exact opt-in required: `False/False/True`.
- Safe action ids: `rebuild_read_only_audit_chain,rerun_read_only_validators,keep_narrowed_archive_provenance_only,monitor_reopen_conditions`.
- Opt-in action ids: `authorized_b4_ra_hi_source_policy_execution`.

## Source Boundary

- Source text found: `True`.
- Source text names velocity-based continuous model: `True`.
- Source text reports mu_s/mu_d: `True`.
- Source text defers law details to Refs. 38--39: `True`.
- Source paper law details available in this artifact: `False`.
- Requires Refs. 38--39 or source code: `True`.

## Source Text Line Anchors

| id | line | found | role |
|---|---:|---|---|
| `mu_static_parameter` | `1040` | `True` | source paper reports the static friction coefficient used in the pendulum case study |
| `mu_dynamic_parameter` | `1041` | `True` | source paper reports the dynamic friction coefficient used in the pendulum case study |
| `brown_mcphee_model_family` | `1056` | `True` | source paper names the Brown--McPhee velocity-based model family |
| `details_deferred` | `1056` | `True` | source paper defers continuous-friction model details to external references |
| `reference_38_entry` | `1579` | `True` | reference 38 is the Brown--McPhee model paper, not local executable source code |
| `reference_39_entry` | `1581` | `True` | reference 39 is an additional friction-model paper, not local executable source code |

## Referenced Detail Sources

- Reference 38 local full text/source code present: `False`.
- Reference 39 local full text/source code present: `False`.
- Reference 38 boundary: bibliographic pointer only in current package; no implementation constants or code binding available.
- Reference 39 boundary: bibliographic pointer only in current package; no transition velocity or coupling policy extracted.

## Local Surrogate Provenance

- Provenance label: `v022_revolute_brown_mcphee_surrogate_not_source_policy_equivalent`.
- v021 README/function present: `True/True`.
- v022 README/function present: `True/True`.
- v022 formula matches candidate family: `True`.
- v022 local Stribeck velocity cases: `[0.5, 0.05]`.
- Accepted source-policy equivalence: `False`.

## Frictional Source-Policy Demotion Contract

- Frictional source-policy rows demoted: `True`.
- Demotion scope: all original-TFE frictional pendulum rows whose acceptance depends on a Brown--McPhee source-code-equivalent law.
- Allowed use: `local_dissipativity_residual_sensitivity_diagnostic_only`.
- Source-policy rows completed/promoted: `0/0`.
- Reason: The source paper supplies mu_s/mu_d and names the Brown--McPhee model family, but it does not provide the transition/Stribeck velocity, source-code normal-load coupling, viscous damping/default policy, or implementation-level coupling needed to bind the candidate law to source-policy rows.
- Required before promotion:
  - source-code or Refs. 38--39 transition/Stribeck velocity.
  - source-code normal-load and joint-multiplier coupling policy.
  - source-code viscous damping or zero-viscous default policy.
  - source implementation tolerance/Jacobian coupling for friction rows.
  - source-equivalent absolute-coordinate DAE and method-runner contracts.

## Candidate-Friction DAE Trajectory Contract

- Implemented: `True`.
- Rows/step residual rows/source-policy rows: `12/56/0`.
- Finite/residual-below-1e-9/friction-power-nonpositive: `True/True/True`.
- Equivalent DAE/method/source-law/monolithic: `False/False/False/False`.
- Accepted use: `candidate_frictional_dae_trajectory_contract_not_source_policy`.
- Runner scope: `candidate_brown_mcphee_friction_bound_to_stepwise_absolute_dae_residuals_not_source_policy`.

## Transition-Velocity Sensitivity

- Sensitivity rows/contracts/source-policy rows: `3/36/0`.
- Contract finite/residual/power/equivalence-false: `True/True/True/True`.
- Max endpoint coordinate/velocity delta vs baseline: `2.899e-06/2.355e-04`.
- Missing transition velocity numerically material: `True`.
- Tested Stribeck velocities/baseline: `[0.05, 0.5, 1.0]/0.5`.

## Missing For Source-Policy Equivalence

- transition/Stribeck velocity used by the source experiments
- source-code treatment of normal-load coupling and joint multipliers
- source-code treatment of viscous damping or zero-viscous default
- source implementation tolerance/Jacobian coupling for friction rows
- Brown--McPhee reference source code or Refs. 38--39 implementation details
- complete law details are not available in the TFE source paper text

## Decision

The artifact confirms that a Brown--McPhee-style candidate formula is encoded and dissipative, with local v021/v022 surrogate provenance and a bounded multi-step candidate DAE trajectory contract. A bounded transition-velocity sensitivity check also shows that the unresolved Stribeck/transition velocity changes the candidate endpoint state. The TFE source paper does not provide the transition velocity, source-code coupling, or implementation details needed to certify source-code-equivalent friction rows.

No TFE source-policy rows are promoted by this audit.
