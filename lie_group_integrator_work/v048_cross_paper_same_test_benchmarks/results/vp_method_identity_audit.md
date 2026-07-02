# VP Method Identity Audit

Alias method: `vp2024_lie_group_ode_partitioning`.
Implemented method: `vp2024_coordinate_partitioning_rA`.
Alias resolved: `True`.
Distinct unresolved VP method remaining: `False`.

The VP Lie-group ODE partitioning label is resolved as the same method already implemented as vp2024_coordinate_partitioning_rA. This does not create a new independent comparison row; it removes the duplicate unresolved VP gate.

| Source | evidence | status | interpretation |
|---|---|---|---|
| `asme_2023_vp_doi` | `primary_metadata_abstract` | `matches_local_coordinate_partitioning_wrapper` | The paper title 'Using Velocity Partitioning in the rA Formulation...' and the DOI metadata describe the same coordinate-partitioning Lie-group ODE method implemented as vp2024_coordinate_partitioning_rA. |
| `easychair_performance_preprint_13546` | `reference_chain` | `no_extra_distinct_vp_method_identified` | The preprint's coordinate-partitioning method points to the ASME 2023 VP paper. It does not expose a second distinct Lie-group ODE partitioning method beyond that coordinate-partitioning VP method. |
| `local_v048_wrapper` | `implementation_identity` | `alias_resolved` | vp2024_lie_group_ode_partitioning should be treated as an alias of the accepted vp2024_coordinate_partitioning_rA wrapper, not as a separate source-unresolved baseline row. |
