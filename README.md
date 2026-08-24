# Industrial Web A/B Testing

> **Public framing: `STATISTICAL_DEMONSTRATION`.** Every experiment unit and outcome in the reproducible analysis is synthetic. This is not a deployed company experiment, a production website case, or evidence about real customer behavior.

## Overview

This project is an expanded portfolio rebuild derived from graduate analytics and statistics coursework. It demonstrates experimental design, binary-outcome A/B testing, effect estimation, confidence intervals, hypothesis testing, prospective power analysis, practical significance, reproducible synthetic-data generation, and disciplined statistical communication.

## Why this project matters

An observed conversion-rate difference is not enough to establish improvement. A defensible decision also needs a clearly defined estimand, a measure of uncertainty, a prespecified test, adequate sample-size planning, and a practical threshold that is not confused with statistical significance. This project keeps those pieces visible and reports an inconclusive result without turning it into either a success claim or proof of no effect.

## Experiment design

| Element | Definition |
|---|---|
| Experimental unit | One unique synthetic eligible visitor |
| Control | Simulated current interface |
| Treatment | Simulated alternative interface |
| Exposure | One simulated render of the assigned interface |
| Outcome | Binary simulated form submission in a common fixed response window |
| Primary estimand | `p_treatment - p_control`, the absolute conversion-rate difference |
| Hypotheses | H0: difference = 0; H1: difference != 0 |
| Alpha | 0.05, two-sided |
| Practical threshold | +1.0 percentage point — `PORTFOLIO_SCENARIO_ASSUMPTION` |

Assignment is completed before outcome generation. The generator uses separate deterministic random streams for assignment and outcomes.

## Data strategy

The public analysis uses `SYNTHETIC_AB_DEMONSTRATION` data so the complete methodology can be reproduced without redistributing restricted course data. No real users, identities, sessions, customer behavior, company activity, or historical raw rows are represented.

The documented generation defaults are deliberately visible:

| Parameter | Default |
|---|---:|
| Total synthetic units | 10,000 |
| Assignment | Exact 1:1 control/treatment allocation |
| Marginal treatment probability | 0.50 |
| Control outcome probability | 0.100 |
| Treatment outcome probability | 0.105 |
| True generating effect | +0.005 probability units (+0.5 percentage point) |
| Fixed seed | `20260824` |

The seed and probabilities are fixed before analysis; they are not searched or changed to obtain significance.

## Statistical method

The primary estimand is the absolute treatment-minus-control conversion-rate difference. The primary inferential procedures are a two-sided pooled two-proportion z-test and a 95% Newcombe hybrid-score confidence interval for two independent proportions. Relative lift is reported only as secondary descriptive context because it depends on the control-rate denominator.

Prospective planning uses an equal-group two-sample normal approximation with Cohen's h. The analysis also reports the minimum detectable effect (MDE) at the current sample size. These planning quantities are declared independently of the observed result.

## Results

| Metric | Control | Treatment | Difference / Result |
|---|---:|---:|---:|
| Sample size | 5,000 | 5,000 | 10,000 total |
| Conversions | 474 | 517 | +43 observed events |
| Conversion rate | 9.48% | 10.34% | +0.86 percentage points |
| Absolute difference | — | — | **+0.86 percentage points** |
| Relative lift | — | — | +9.0717% — secondary descriptive metric |
| 95% Newcombe CI | — | — | **[-0.311934, +2.032678] percentage points** |
| Two-sided pooled z | — | — | 1.4391078258 |
| P-value | — | — | 0.150120 |
| Statistical decision | — | — | `FAIL_TO_REJECT_H0` |
| Practical decision | — | — | `UNRESOLVED` |

The synthetic demonstration observed a treatment-control difference of +0.86 percentage points. Because the 95% confidence interval includes zero and the two-sided p-value exceeds 0.05, the experiment does not establish a positive treatment effect. This does not prove that the groups are equal or that no effect exists.

## Practical significance

The +1.0 percentage-point practical threshold is a `PORTFOLIO_SCENARIO_ASSUMPTION`, not a company decision rule or an ROI threshold. The observed +0.86-point estimate is below it, while the confidence interval contains values both below and above it. The practical decision is therefore **UNRESOLVED**, not “treatment failed” or “no effect.”

## Power planning

Sample size should be planned before an experiment so the design has a declared ability to detect an effect worth acting on. Under a 10% baseline, +1.0-point effect, two-sided alpha of 0.05, 80% desired power, and equal allocation:

- required sample size is approximately **14,745 observations per group**;
- prospective power at 5,000 per group is approximately **37.14%**;
- the 80%-power MDE at 5,000 per group is approximately **1.743 percentage points**.

Limited prospective power makes a nonsignificant realization unsurprising, but it does not prove the null. Post-hoc observed power is not used as evidence.

## Figures

The generated figure set emphasizes estimates, uncertainty, and prospective planning:

1. [Synthetic conversion rates with 95% Wilson intervals](docs/figures/01_conversion_rates_ci.png)
2. [Synthetic treatment-effect estimate with 95% Newcombe interval and scenario threshold](docs/figures/02_effect_interval.png)
3. [Synthetic prospective power by sample size per group](docs/figures/03_power_curve.png)

## Reproducibility

From the repository root, install only the documented dependencies and run:

```powershell
python run_analysis.py
```

That command regenerates the synthetic dataset, validates its contract, computes the effect estimate, confidence interval, hypothesis test, prospective power and MDE, and rewrites all result tables and figures. It has no notebook dependency and uses the frozen defaults above.

Verification commands:

```powershell
python -m unittest discover -s tests -v
python execute_notebooks.py
```

See [docs/reproducibility.md](docs/reproducibility.md) for outputs and the frozen-seed fingerprint.

## Validation

- deterministic data regeneration verified byte for byte;
- frozen default-seed SHA-256 regression test included;
- 14/14 tests pass after professionalization;
- both notebooks execute top-to-bottom in fresh namespaces;
- z statistic, p-value, and Newcombe interval cross-checked by a separate in-repository standard-library implementation;
- the internal Module 7.5B audit found no evidence of seed shopping or result-dependent generation;
- historical and synthetic data separation verified.

## Limitations

- The data are synthetic and do not validate behavior of real users.
- There is no production deployment, business ROI, or company decision threshold.
- The design has no clustering, repeated-user complexity, attrition, noncompliance, or interference.
- No subgroup claims, multiple primary outcomes, Bayesian analysis, or machine-learning model are included.
- The analysis is fixed-horizon; no sequential inference procedure is implemented.
- The practical threshold is hypothetical and scenario-specific.

## Repository structure

```text
repository-root/
├── .private_outputs/  # ignored local runtime output created by run_analysis.py
├── data/               # synthetic dataset, generation config, schema, and rights notes
├── docs/               # design, background, claims, reproducibility, and reviewed figures
├── notebooks/          # explanatory notebooks using reusable modules
├── reports/            # methodology, results, limitations, quality, and validation
├── src/                # generation, validation, statistics, power, and visualization
├── tests/              # deterministic, contract, inferential, and power tests
├── CITATION.md
├── LICENSE_STATUS.md
├── requirements.txt
└── run_analysis.py
```

## Historical provenance

The project is an expanded portfolio rebuild derived from graduate coursework. Historical course data are preserved separately as internal provenance and are not redistributed. The public statistical demonstration uses only newly generated synthetic data.

## Skills demonstrated

- A/B testing and experimental design
- Effect estimation and confidence intervals
- Hypothesis testing and practical-significance reasoning
- Prospective power and MDE analysis
- Reproducible simulation and Python
- Statistical communication and claim discipline

## Publication status

Module 8A granted interim approval after the recorded prepublication edits, pending the final five-project Module 8B audit. Nothing has been published, and final code, synthetic-data, figure, and documentation licensing remain owner decisions.
