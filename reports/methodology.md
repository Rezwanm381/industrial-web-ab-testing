# Methodology

## Project and data provenance

This project is a `STATISTICAL_DEMONSTRATION` derived from graduate analytics coursework. The public analysis uses newly generated synthetic data because historical course-data provenance and redistribution rights are unresolved. Synthetic rows are visibly labeled and are not represented as actual users or production observations.

## Experiment definition

- `EXPERIMENTAL_UNIT`: one synthetic eligible website visitor represented once by a unique ID.
- `CONTROL`: one simulated exposure to the current interface.
- `TREATMENT`: one simulated exposure to an alternative interface.
- `EXPOSURE`: a single simulated render of the assigned interface.
- `PRIMARY_OUTCOME`: binary form submission within a common fixed response window.
- `ESTIMAND`: the average absolute difference in conversion probabilities, treatment minus control.
- `NULL_HYPOTHESIS`: the absolute difference equals zero.
- `ALTERNATIVE_HYPOTHESIS`: the absolute difference is not zero.
- `ALPHA`: 0.05, two-sided.
- `PRACTICAL_EFFECT_THRESHOLD`: +1.0 percentage point, explicitly a `PORTFOLIO_SCENARIO_ASSUMPTION`.

Relative lift is a secondary descriptive measure because it depends strongly on the control denominator. Risk ratios and odds ratios are not promoted to primary estimands.

## Synthetic generation

The pre-specified scenario contains 10,000 units, exact 1:1 assignment, a 10% control conversion probability, a true +0.5 percentage-point treatment effect, and seed `20260824`. This is intentionally a little-effect scenario; it was not designed to make treatment win.

The generator derives separate child streams from the fixed seed. It shuffles assignment labels first, maps each assignment to its declared conversion probability, and then draws binary outcomes. One row and one exposure are retained per unit. No seed search, result-based tuning, missing data, segment variables, or clustering is used.

## Data quality and assignment checks

Validation rejects missing required fields, duplicate unit IDs, missing or inconsistent treatment labels, nonbinary outcomes, unexposed units, duplicate exposure counts, non-synthetic source labels, and an absent treatment group. Sample counts and allocation ratio are recorded. Changing the outcome probability while holding the seed fixed is tested not to change assignment.

## Descriptive analysis

For each group, the pipeline calculates sample size, conversion count, and conversion rate. It then reports treatment minus control in probability units and percentage points, plus relative lift when the control rate is nonzero. Observed lift is not treated as causal certainty.

## Primary inference and interval

The primary hypothesis test is a two-sided pooled two-sample proportion z-test. The primary 95% interval is the Newcombe hybrid-score interval for the difference between independent proportions, formed from Wilson score limits. The interval receives equal or greater interpretive weight than the p-value.

A separate reference module independently recomputes the p-value with an `erfc` normal-tail calculation and recomputes Wilson endpoints as roots of the score-test quadratic. Numerical agreement of the effect estimate, interval, and p-value is required before the run succeeds.

This is a separate in-repository implementation, not external validation. Method references: R. G. Newcombe (1998), “Interval estimation for the difference between independent proportions: comparison of eleven methods,” *Statistics in Medicine*, 17(8), 873–890; and J. Cohen (1988), *Statistical Power Analysis for the Behavioral Sciences*, 2nd ed.

## Statistical versus practical significance

Statistical significance is determined by the two-sided p-value and whether the interval excludes zero. Practical significance is evaluated against the declared +1.0-point scenario threshold. The pipeline distinguishes an estimate crossing the threshold from an interval clearing it with 95% confidence. No ROI, revenue, implementation-cost, or business-value claim is made.

## Prospective power and MDE planning

Prospective planning uses a two-sample normal approximation with Cohen's h for equal groups. Inputs are a 10% baseline, two-sided alpha 0.05, 80% desired power, and a +1.0-point minimum detectable effect. The smallest integer group size meeting the target is found before interpreting the generated result. A bisection calculation also reports the 80%-power MDE for 5,000 units per group.

Post-hoc observed power is intentionally not used as evidence for result validity. The relevant planning quantities are prospective power and MDE under declared scenarios.

## Assumptions

For the synthetic demonstration, the following are controlled by design where practical: one independent unit per row, assignment before outcome generation, stable binary outcome definition, common exposure and response windows, one exposure per unit, no repeated users, and no interference encoded in generation. The normal approximation is suitable at the generated event counts.

These controls do not validate the historical course experiment. Historical randomization, exposure, independence, stopping, missingness, and repeat-user behavior remain unknown.

## Multiplicity, segments, and monitoring

Only one primary hypothesis is tested, so no multiplicity correction is needed. No subgroup analysis is performed, avoiding uncontrolled segment fishing. Bayesian analysis is omitted to prioritize one coherent frequentist framework.

The analysis is treated as fixed-horizon. Repeatedly checking ordinary p-values and stopping when p < 0.05 would condition stopping on favorable noise and inflate the false-positive rate. A complex sequential framework is not added because it is not needed for the minimum defensible demonstration; a real monitored experiment would require a prespecified group-sequential or always-valid procedure.

## Robustness

Compact checks include an alternative unpooled Wald interval, exact 1:1 assignment balance, sensitivity to +0.5-, +1.0-, and +1.5-point practical thresholds, and an independently implemented numerical cross-check. No additional hypothesis tests are added for sophistication.
