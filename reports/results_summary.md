# Results Summary

## Primary result

| Metric | Result |
|---|---:|
| Control n | 5,000 |
| Treatment n | 5,000 |
| Control conversions | 474 |
| Treatment conversions | 517 |
| Control rate | 9.4800% |
| Treatment rate | 10.3400% |
| Absolute difference (treatment - control) | +0.860 percentage points |
| Relative lift (secondary descriptive measure) | +9.072% |
| 95% Newcombe interval | [-0.312, +2.033] percentage points |
| Two-sided pooled z statistic | 1.439108 |
| Two-sided p-value | 0.150120 |
| Statistical decision at alpha = 0.05 | FAIL_TO_REJECT_NULL |
| Practical decision at +1.0 point | ESTIMATE_BELOW_THRESHOLD_AND_INTERVAL_CROSSES_THRESHOLD |

## Interpretation

The observed difference is compatible with both small negative and positive effects; the experiment does not establish improvement.

Statistical significance and practical significance answer different questions. The statistical decision uses a two-sided 5% test. The practical decision compares the estimate and interval with a +1.0 percentage-point threshold that is explicitly a **PORTFOLIO_SCENARIO_ASSUMPTION**, not a validated business or ROI threshold.

## Prospective design

At a 10% baseline, two-sided alpha of 0.05, 80% desired power, and a +1.0 percentage-point minimum detectable effect, the prospective requirement is **14,745 units per group** (29,490 total). The current synthetic demonstration has 5,000 per group and prospective power of 37.1% for that effect; its corresponding 80%-power MDE is 1.743 percentage points.

Post-hoc observed power is not used to validate the result. Power and MDE are prospective design quantities tied to declared effect sizes.

## Robustness and separate numerical cross-check

- Alternative unpooled Wald interval: [-0.311, +2.031] percentage points.
- Exact 1:1 assignment balance was verified by construction and by the data-quality checks.
- Practical-threshold sensitivity is exported in `.private_outputs/tables/robustness_checks.csv`.
- The primary z statistic, p-value, and Newcombe interval were reproduced by a separate in-repository standard-library implementation using `erfc` normal tails and quadratic Wilson roots: **PASS**. This is internal numerical QA, not external validation.

## Multiplicity and advanced methods

There is one primary hypothesis, so multiplicity correction is unnecessary for the primary analysis. No subgroup search, Bayesian analysis, or sequential-testing procedure was added. This deliberately keeps one coherent frequentist core. Ordinary fixed-horizon p-values would not remain valid under repeated outcome peeking and significance-based stopping.
