# Closed-Loop True-Dynamic Interface Audit

Status: **setup-level interface verified; no trajectory rows run**

- Models: `four_link, slider_crank`.
- Dynamic setup rows ok: `2/2`.
- Local `Gauss6/FullVA` dynamic runner exists: `False`.
- `do_step` called: `False`.
- Heavy numerical run invoked: `False`.
- Default `1e-4` required: `False`.

The public/v046 `rA` system can be constructed in `dynamics` mode for
`four_link` and `slider_crank`; the missing piece is not model access.
The missing piece is the local `Gauss6/FullVA` dynamic trajectory
stepper that couples state, velocity, acceleration, and multipliers
inside the method residual.

| Model | Mode | setup | solver | nb | nc | 6nb | public Newton dim | local runner |
|---|---|---|---|---:|---:|---:|---:|---:|
| `four_link` | `kinematics` | `ok` | `KINEMATICS` | `3` | `18` | `18` | `not_applicable` | `false` |
| `four_link` | `dynamics` | `ok` | `DYNAMICS` | `3` | `18` | `18` | `36` | `false` |
| `slider_crank` | `kinematics` | `ok` | `KINEMATICS` | `3` | `18` | `18` | `not_applicable` | `false` |
| `slider_crank` | `dynamics` | `ok` | `DYNAMICS` | `3` | `18` | `18` | `36` | `false` |

## Consequence

The next implementation should reuse the verified constraint and
mass/inertia interfaces, but it must not call the public `do_step` as
the local method. A valid row must assemble the local
`Gauss6/FullVA` dynamic residual itself and then compare the resulting
trajectory on the coarse-first row plan.
