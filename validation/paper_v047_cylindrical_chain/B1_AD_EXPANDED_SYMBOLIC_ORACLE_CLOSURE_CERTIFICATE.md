# B1 AD-Expanded Symbolic Oracle Closure Certificate

Status: **AD-expanded symbolic oracle closed for B1; no O(h^7) overclaim**.

- AD-expanded symbolic oracle closure: `True`.
- Closed rows: `36/36`.
- Columns per row: `132`.
- Closed derivative cells: `4752/4752`.
- Independent symbolic row oracle closed: `True`.
- AD-expanded runtime formula binding checked: `True`.
- Dynamic symbolic oracle complete: `False`.
- O(h^7) symbolic-certificate proof closed by this certificate: `False`.
- Submission ready: `False`.

## Proof Rule

For each audited scalar Newton--Euler residual row, the source-template identity is already closed on the smooth proof tube.
Differentiating the closed residual identity columnwise with respect to the 132 FullVA stage variables gives the AD-expanded symbolic identity.
The finite AD probes are implementation binding checks only; they are not used as the proof of equality.

## Boundary

This closes the B1 requirement `AD_expanded_symbolic_oracle_closure`.
It does not complete the Newton--Euler symbolic-defect certificate, does not prove the symbolic-certificate O(h^7) lane, and does not make the package submission ready.

## Row Closures

| row | formula row | stage | body | component | columns | derivative cells | closed |
|---:|---:|---:|---:|---|---:|---:|---:|
| `24` | `72` | `0` | `0` | `x` | `132` | `132` | `True` |
| `25` | `73` | `0` | `0` | `y` | `132` | `132` | `True` |
| `26` | `74` | `0` | `0` | `z` | `132` | `132` | `True` |
| `27` | `75` | `0` | `0` | `x` | `132` | `132` | `True` |
| `28` | `76` | `0` | `0` | `y` | `132` | `132` | `True` |
| `29` | `77` | `0` | `0` | `z` | `132` | `132` | `True` |
| `30` | `78` | `0` | `1` | `x` | `132` | `132` | `True` |
| `31` | `79` | `0` | `1` | `y` | `132` | `132` | `True` |
| `32` | `80` | `0` | `1` | `z` | `132` | `132` | `True` |
| `33` | `81` | `0` | `1` | `x` | `132` | `132` | `True` |
| `34` | `82` | `0` | `1` | `y` | `132` | `132` | `True` |
| `35` | `83` | `0` | `1` | `z` | `132` | `132` | `True` |
| `68` | `84` | `1` | `0` | `x` | `132` | `132` | `True` |
| `69` | `85` | `1` | `0` | `y` | `132` | `132` | `True` |
| `70` | `86` | `1` | `0` | `z` | `132` | `132` | `True` |
| `71` | `87` | `1` | `0` | `x` | `132` | `132` | `True` |
| `72` | `88` | `1` | `0` | `y` | `132` | `132` | `True` |
| `73` | `89` | `1` | `0` | `z` | `132` | `132` | `True` |
| `74` | `90` | `1` | `1` | `x` | `132` | `132` | `True` |
| `75` | `91` | `1` | `1` | `y` | `132` | `132` | `True` |
| `76` | `92` | `1` | `1` | `z` | `132` | `132` | `True` |
| `77` | `93` | `1` | `1` | `x` | `132` | `132` | `True` |
| `78` | `94` | `1` | `1` | `y` | `132` | `132` | `True` |
| `79` | `95` | `1` | `1` | `z` | `132` | `132` | `True` |
| `112` | `96` | `2` | `0` | `x` | `132` | `132` | `True` |
| `113` | `97` | `2` | `0` | `y` | `132` | `132` | `True` |
| `114` | `98` | `2` | `0` | `z` | `132` | `132` | `True` |
| `115` | `99` | `2` | `0` | `x` | `132` | `132` | `True` |
| `116` | `100` | `2` | `0` | `y` | `132` | `132` | `True` |
| `117` | `101` | `2` | `0` | `z` | `132` | `132` | `True` |
| `118` | `102` | `2` | `1` | `x` | `132` | `132` | `True` |
| `119` | `103` | `2` | `1` | `y` | `132` | `132` | `True` |
| `120` | `104` | `2` | `1` | `z` | `132` | `132` | `True` |
| `121` | `105` | `2` | `1` | `x` | `132` | `132` | `True` |
| `122` | `106` | `2` | `1` | `y` | `132` | `132` | `True` |
| `123` | `107` | `2` | `1` | `z` | `132` | `132` | `True` |

## Validation

Run `validate_b1_ad_expanded_symbolic_oracle_closure_certificate.py`.
