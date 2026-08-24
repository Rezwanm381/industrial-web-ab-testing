# Reproducibility

## Environment

The validated environment was Windows with Python 3.12.13, NumPy 2.3.5, pandas 3.0.1, and Pillow 12.3.0. The supported ranges remain in `requirements.txt`; other versions are not asserted to be byte-identical. The project uses the Python standard library for inference, power calculations, tests, and notebook execution.

## One-command analysis

From the repository root:

```powershell
python run_analysis.py
```

The command uses `SyntheticDesign()` defaults and regenerates:

- `data/generated/synthetic_ab_experiment.csv`;
- `data/generated/generation_config.json`;
- result, power, robustness, and numerical cross-check tables in the ignored local `.private_outputs/tables` directory;
- three reviewed PNG figures in `docs/figures`;
- the generated data-quality and results reports.

No notebook output is used as an analysis dependency.

## Verification

```powershell
python -m unittest discover -s tests -v
python execute_notebooks.py
```

The test suite includes a path-independent frozen-seed regression test. Serializing the default generated table to UTF-8 CSV must produce SHA-256 `BF554C12C5054815378A5887BBF47B93841141CF52C3676E422F805655CFD2BE`. This detects accidental changes to the validated default dataset; it is not used to choose a seed.

## Determinism boundaries

The frozen fingerprint assumes the declared defaults and supported dependency versions. Intentionally changing NumPy/pandas serialization behavior or the generator requires an explicit review and new validation rather than silently updating the expected hash.
