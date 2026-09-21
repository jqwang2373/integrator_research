# Closed-Loop True-Dynamic Public Work/Precision

Status: **same window public work precision available reference caveat not external superiority**

- Rows: `24/24` ok.
- Public work/precision examples available: `2`.
- Public work/precision examples missing: `0`.
- Strict common-reference error columns: `False`.
- Default `1e-4` required: `False`.
- External superiority claim: `False`.

This table aligns the public 2021 closed-loop dynamics rows with the local
true-dynamic Newton rows in model, time window, and step sizes. It still
keeps a reference-family caveat: public errors are measured against the
public `rA` kinematic reference, while local errors are the already accepted
local exact-endpoint errors.

| Model | Method | ok | pos order | vel order | acc order | finest pos | finest vel | runtime sum | runtime ratio vs rA |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `four_link` | `Gauss6/FullVA-local-true-dynamic-newton` | `3/3` | `5.9548979111188078e+00` | `6.0848187309877098e+00` | `9.9466887815859806e-01` | `2.2888357875672227e-12` | `1.0927703186780491e-11` | `2.4778123860014603e+00` | `6.4794993580201236e+01` |
| `four_link` | `rA-public-dynamics` | `3/3` | `1.4685718674981961e+01` | `3.2298044345975330e-02` | `-1.0437390216492909e-01` | `6.3906124836421441e-10` | `1.5621484149989922e+00` | `4.9217856023460627e-02` | `1.0000000000000000e+00` |
| `four_link` | `reps-public-dynamics` | `3/3` | `1.2552093412220962e+01` | `1.9481804577399764e-01` | `8.9114005912867089e-01` | `1.2305886087915496e-08` | `1.2470259810935089e+00` | `9.1779897105880082e-02` | `2.6519031488061269e+00` |
| `four_link` | `rp-public-dynamics` | `3/3` | `1.2815607972489735e+01` | `1.9481660959759076e-01` | `5.8720829990254719e-01` | `8.5400677640734557e-09` | `1.2470284638788862e+00` | `6.5243688062764704e-02` | `1.4966983481933522e+00` |
| `slider_crank` | `Gauss6/FullVA-local-true-dynamic-newton` | `3/3` | `6.1636896425143544e+00` | `7.3409145102638718e+00` | `1.0541648128408896e+00` | `8.5831619589527008e-12` | `9.1888510689308589e-12` | `3.0849206619895995e+00` | `8.0798646532984932e+01` |
| `slider_crank` | `rA-public-dynamics` | `3/3` | `1.1481180658461589e+01` | `6.8495270883560233e-01` | `-3.2735984145091179e-01` | `2.8768627896580412e-09` | `8.6349646055569385e-02` | `5.3440375952050090e-02` | `1.0000000000000000e+00` |
| `slider_crank` | `reps-public-dynamics` | `3/3` | `8.1248189457292295e+00` | `6.8495405509299168e-01` | `3.7094887685011868e-01` | `3.0175206625071560e-07` | `8.6349484900595797e-02` | `5.7773243868723512e-02` | `1.2749434858430220e+00` |
| `slider_crank` | `rp-public-dynamics` | `3/3` | `8.0829224633701973e+00` | `6.8495403558138679e-01` | `6.7292592852097807e-02` | `3.1979704645523910e-07` | `8.6349487236248135e-02` | `6.7232068977318704e-02` | `1.6265922124183361e+00` |
