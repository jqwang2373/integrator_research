# external

Third-party material used for comparisons. Nothing here is edited.

| Path | What it is | Tracked |
| --- | --- | --- |
| `sbel-reproducibility/` | Local mirror of the SBEL/Negrut public reproducibility code (2021 ASME rA formulation, 2022 half-implicit JCND suite) used by the v046/v048 benchmarks. | yes |
| `public-metadata/` | `git clone --filter=blob:none --no-checkout` of <https://github.com/uwsbel/public-metadata> (branches `master`, `user/aaron/msd`). Only the git metadata is kept; the code-path audits scan it for a velocity-partitioning implementation and record that none is present. | no (`.gitignore`); restore with the clone command |
| `literature/` | Reference papers and their `pdftotext` dumps: `s11044-026-10153-w.pdf/.txt` (Chaturvedi, Sandu, Sandu 2026, the TFE source paper) and `1-s2.0-S0377042719305229-main.pdf/.txt`. About 35 validators read the text dumps for source-policy and formula audits; keep the file names. | yes |
