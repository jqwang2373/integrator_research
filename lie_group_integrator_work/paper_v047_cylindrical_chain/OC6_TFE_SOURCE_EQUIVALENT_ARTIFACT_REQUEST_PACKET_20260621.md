# OC6 TFE Source-Equivalent Artifact Request Packet 2026-06-21

Status: `request_packet_ready_not_sent_no_source_policy_closure`.

This read-only packet prepares a source-equivalent artifact request. It has not been sent and it closes zero source-policy rows.

- Request ready: `True`.
- Request sent: `False`.
- Corresponding author email: `ekanshchat96@vt.edu`.
- Author contact emails: `csandu@vt.edu, ekanshchat96@vt.edu, sandu@cs.vt.edu`.
- Requested artifact count: `7`.
- OC6 external recheck marker: `2026-06-21/10/0/0/0/False/False`.
- OC6 publisher availability marker: `2026-06-21/True/0/0/0/0/False/False`.
- TFE runner preflight marker: `contract_entrypoints_callable_candidate_backed_source_policy_open/3/3/3/0/4`.
- Source-policy rows closed by packet: `0`.
- Source-policy reopen triggered: `False`.
- Global absence proved: `False`.
- Submission ready: `False`.

## Requested Artifacts

- `absolute_coordinate_T10_pendulum_dae_runner`: Source-code-equivalent absolute-coordinate T=10 pendulum DAE runner used for the article's index-3 frictional pendulum experiments.
- `tfe_newmark_trapezoidal_method_runners`: TFE m=1/m=2/m=3, Newmark-beta, and trapezoidal source-policy method runners with the same state, constraint, and output conventions.
- `brown_mcphee_friction_law_details`: Brown-McPhee friction law implementation details, including transition or Stribeck velocity, normal-load coupling, viscous/default policies, and any branch/tolerance conventions.
- `full_T10_endpoint_and_sampling_policy`: Full T=10 endpoint/output sampling policy for rows whose nominal step size does not land exactly on the endpoint.
- `source_reference_policy_and_h_1e_minus_4_binding`: Reference-solution policy and h=1e-4 binding used for reported error normalization, including solver tolerances and any accepted reference files.
- `work_precision_row_table_binding`: Work-precision row table binding errors, orders, runtime, Newton diagnostics, and Jacobian timing to the same source-policy rows.
- `license_permission_or_public_archive_identity`: License/permission statement or a public URL, repository commit, or archive hash that makes the supplied artifact reviewer-verifiable.

## Acceptance Boundary

- Formula-only, pseudocode-only, local candidate-only, or proxy implementations do not close OC6.
- Rows close only after validator promotion of source-equivalent evidence.
- This packet is a request handoff, not source-policy execution evidence.
