import IntegratorOrderProof
/-!
# Axiom audit for every theorem of `IntegratorOrderProof`

Run with `lake env lean scripts/Axioms.lean` (after `lake build`).

The command `#axiom_audit` below enumerates **every** theorem declared in a module of the
`IntegratorOrderProof` library (auxiliary and structural declarations such as `injEq`,
`sizeOf_spec`, `match_*`, `proof_*` are skipped), prints the axioms it depends on in the
`#print axioms` format, and fails with a non-zero exit code if any theorem depends on `sorryAx`
or on any axiom other than `propext`, `Classical.choice`, `Quot.sound`.  No hand-maintained
list is involved, so a new theorem cannot escape the audit.
-/
open Lean Elab Command

namespace IntegratorOrderProof.Audit

/-- The three standard axioms of classical Mathlib developments. -/
def allowedAxioms : List Name := [``propext, ``Classical.choice, ``Quot.sound]

/-- Auto-generated companions of structures and pattern matches that are not user theorems. -/
def structuralSuffixes : List String :=
  ["injEq", "sizeOf_spec", "inj", "noConfusion", "noConfusionType", "rec", "recOn", "casesOn",
   "below", "brecOn", "eq_1", "eq_def", "ext", "ext_iff"]

/-- Declarations that are not user-facing theorems. -/
def isStructural (n : Name) : Bool :=
  n.isInternalDetail
    || n.components.any (fun c => (c.toString.startsWith "_") || (c.toString.startsWith "match_")
                                  || (c.toString.startsWith "proof_"))
    || (match n.components.getLast? with
        | some c => structuralSuffixes.contains c.toString
        | none => true)

/-- Is `n` declared in a module of this library? -/
def inLibrary (env : Environment) (n : Name) : Bool :=
  match env.getModuleIdxFor? n with
  | some idx => (`IntegratorOrderProof).isPrefixOf env.header.moduleNames[idx]!
  | none => false

/-- Enumerate the library's theorems, print their axioms, fail on non-standard axioms. -/
elab "#axiom_audit" : command => do
  let env ← getEnv
  let mut names : Array Name := #[]
  for (n, ci) in env.constants.toList do
    if inLibrary env n && !isStructural n then
      match ci with
      | .thmInfo _ => names := names.push n
      | _ => pure ()
  let sorted := names.qsort (fun a b => a.toString < b.toString)
  let mut bad : Array Name := #[]
  for n in sorted do
    let axs ← liftCoreM (collectAxioms n)
    let axs := axs.qsort Name.lt
    logInfo m!"'{n}' depends on axioms: {axs.toList}"
    if axs.any (fun a => !(allowedAxioms.contains a)) then
      bad := bad.push n
  logInfo m!"axiom audit: {sorted.size} theorems checked, {bad.size} with non-standard axioms"
  if bad.size > 0 then
    throwError "axiom audit failed: {bad.toList}"

end IntegratorOrderProof.Audit

#axiom_audit
