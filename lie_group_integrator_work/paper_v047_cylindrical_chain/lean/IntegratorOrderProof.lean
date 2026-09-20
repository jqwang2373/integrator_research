import IntegratorOrderProof.Basic
import IntegratorOrderProof.PerturbationChain.Contraction
import IntegratorOrderProof.PerturbationChain.EndpointClosure
import IntegratorOrderProof.PerturbationChain.LocalToGlobal
import IntegratorOrderProof.PerturbationChain.MainTheorem
import IntegratorOrderProof.PerturbationChain.JacobianPerturbation
import IntegratorOrderProof.NewtonEuler.DynamicRows
import IntegratorOrderProof.Gauss.Tableau
import IntegratorOrderProof.Gauss.QuadratureError
import IntegratorOrderProof.FullVA.NonDynamicRows

/-!
# IntegratorOrderProof

Lean 4 / Mathlib development accompanying the CMAME manuscript on the `Gauss6/FullVA`
Lie-group integrator (`paper_v047_cylindrical_chain/main_cmame.tex`).  Importing this module
imports the whole library:

* `Basic` — one-step stability factor `(1 + C h)^n ≤ exp(C h n)`.
* `PerturbationChain.Contraction` — Kantorovich root lemma, inexact Newton, derivative form of P2.
* `PerturbationChain.EndpointClosure` — right-inverse endpoint closure (`C_E = 2 M_ri C_raw`).
* `PerturbationChain.LocalToGlobal` — discrete Gronwall with tube retention (`Γ_s(T)`).
* `PerturbationChain.MainTheorem` — `C_loc` assembly and the `h⁶` grid bounds.
* `PerturbationChain.JacobianPerturbation` — uniform inverse under `O(h)` perturbation
  (`lem:p2-from-p1`), simplified Newton residual decay (`lem:newton-envelope`).
* `NewtonEuler.DynamicRows` — the 36 Newton–Euler rows of `run_v047.py` vanish at the lifted stage.
* `FullVA.NonDynamicRows` — the 96 non-dynamic rows vanish iff constraints hold at all levels and
  the reduced joint coordinates satisfy Gauss collocation (exact stage identity, `C_R = 0`).
* `Gauss.Tableau` — exact Gauss6 tableau, Butcher `B(6)`, `C(3)`, `D(3)`, `¬B(7)`.
* `Gauss.QuadratureError` — Peano-type quadrature error, Gauss6 `h⁷` step defect.

`scripts/Axioms.lean` audits every theorem for `sorry`-freedom and standard axioms;
`scripts/check.sh` runs build, audit and linter.
-/
