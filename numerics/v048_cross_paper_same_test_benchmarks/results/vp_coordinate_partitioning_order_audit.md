# VP Coordinate-Partitioning Order Audit

This audit separates finest-step velocity error from observed velocity order.

Local velocity-order wins: `4/4`.
VP finest-step velocity-error wins: `3/4`.
Larger-step local velocity-order wins: `4/4`.
Larger-step local finest-velocity-error wins: `1/4`.

| Example | local vel errors | VP vel errors | local order | VP order | VP finest/error local | interpretation |
|---|---:|---:|---:|---:|---:|---|
| `single_pendulum` | `3.5925301219345963e-09|5.5708166814780595e-11|1.1551877762897842e-12` | `5.5511151231257827e-17|5.5511151231257827e-17|5.5511151231257827e-17` | `5.8013285781956512e+00` | `2.7082010409952339e-15` | `4.8053790362591748e-05` | VP has the smaller finest-step velocity error and a low observed order on this grid. This row is a pointwise VP error win, not evidence that VP is high order. |
| `double_pendulum` | `9.7376654656367023e-10|1.5220038770968891e-11|2.3455890008072799e-13` | `7.5786259486214924e-03|3.2480195656038159e-03|1.0826277865644317e-03` | `6.0097049897199657e+00` | `1.4036994905031275e+00` | `4.6155903109701843e+09` | Local method has higher observed velocity order. |
| `four_link` | `5.0344821200809520e-08|7.2894623670549663e-10|1.0927703186780491e-11` | `8.5780271774638095e-12|5.4454218911814678e-12|2.3741009158584347e-12` | `6.0848187309877098e+00` | `9.2663231296479098e-01` | `2.1725525257040679e-01` | VP has the smaller finest-step velocity error and a low observed order on this grid. This row is a pointwise VP error win, not evidence that VP is high order. |
| `slider_crank` | `2.4150834344177641e-07|9.8783998342399926e-10|9.1888510689308589e-12` | `2.4450927393893096e-13|1.7681689445936399e-13|9.7866159620707549e-14` | `7.3409145102638718e+00` | `6.6050359651248636e-01` | `1.0650532790939495e-02` | VP has the smaller finest-step velocity error and a low observed order on this grid. This row is a pointwise VP error win, not evidence that VP is high order. |

Local Gauss6 FullVA has higher observed velocity order on all four VP-coordinate comparison rows. VP coordinate partitioning wins three finest-step velocity-error rows on this grid. The larger-step diagnostic keeps the same order conclusion but also keeps the boundary that local does not win every finest-step error row.
