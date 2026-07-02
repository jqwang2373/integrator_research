# Closed-Loop True-Dynamic Newton Coarse Order

Status: **coarse true dynamic order candidates available not external superiority**

- Step sizes: `0.1|0.05|0.025`; time window: `0.1`.
- Rows: `6/6` ok.
- Accepted dynamic-order candidates: `2`.
- Stage oracle used: `False`.
- Default `1e-4` required: `False`.
- External superiority claim: `False`.

These rows use the non-oracle Newton stage solver on a short coarse
trajectory window. They are local true-dynamic method rows; they still
need public-baseline work/precision comparison before any external
superiority claim is allowed.
The acceptance gate uses position, orientation, linear velocity, and
angular velocity orders; endpoint acceleration is reported only as a
diagnostic because this runner does not yet construct a collocated
endpoint acceleration state.

| Model | h | pos err | orient err | vel err | pos order | orient order | vel order | omega order | Newton iters | status |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `four_link` | `1.0000000000000001e-01` | `8.8068463632851035e-09` | `6.6941847065571380e-09` | `5.0344821200809520e-08` | `5.9548979111188078e+00` | `5.9551952274786428e+00` | `6.0848187309877098e+00` | `5.9714212386921126e+00` | `8` | `ok` |
| `four_link` | `5.0000000000000003e-02` | `1.4460210806532814e-10` | `1.0991557664041807e-10` | `7.2894623670549663e-10` | `5.9548979111188078e+00` | `5.9551952274786428e+00` | `6.0848187309877098e+00` | `5.9714212386921126e+00` | `15` | `ok` |
| `four_link` | `2.5000000000000001e-02` | `2.2888357875672227e-12` | `1.7390533457728452e-12` | `1.0927703186780491e-11` | `5.9548979111188078e+00` | `5.9551952274786428e+00` | `6.0848187309877098e+00` | `5.9714212386921126e+00` | `27` | `ok` |
| `slider_crank` | `1.0000000000000001e-01` | `4.4112151487141205e-08` | `2.0527722184465297e-07` | `2.4150834344177641e-07` | `6.1636896425143544e+00` | `6.1589799243832246e+00` | `7.3409145102638718e+00` | `6.4255003113652025e+00` | `8` | `ok` |
| `slider_crank` | `5.0000000000000003e-02` | `5.7265422959140722e-10` | `2.6785954354594267e-09` | `9.8783998342399926e-10` | `6.1636896425143544e+00` | `6.1589799243832246e+00` | `7.3409145102638718e+00` | `6.4255003113652025e+00` | `15` | `ok` |
| `slider_crank` | `2.5000000000000001e-02` | `8.5831619589527008e-12` | `4.0203638715605161e-11` | `9.1888510689308589e-12` | `6.1636896425143544e+00` | `6.1589799243832246e+00` | `7.3409145102638718e+00` | `6.4255003113652025e+00` | `25` | `ok` |
