# Experimental Design

## Scope

This is a fixed-horizon `STATISTICAL_DEMONSTRATION` using entirely synthetic units and outcomes. It is not a reconstruction of a deployed experiment and does not represent real customer behavior.

## Design contract

- **Experimental unit:** one unique synthetic eligible visitor.
- **Assignment:** exact 1:1 control/treatment allocation, shuffled with a dedicated random stream before outcomes are generated.
- **Control:** simulated current interface.
- **Treatment:** simulated alternative interface.
- **Exposure:** one simulated render of the assigned interface.
- **Outcome:** binary simulated form submission in a common fixed response window.
- **Primary estimand:** `p_treatment - p_control`, in probability units and percentage points.
- **Null hypothesis:** `p_treatment - p_control = 0`.
- **Alternative hypothesis:** `p_treatment - p_control != 0`.
- **Primary test:** two-sided pooled two-proportion z-test at alpha 0.05.
- **Primary interval:** 95% Newcombe hybrid-score interval for independent proportions.
- **Practical threshold:** +1.0 percentage point, explicitly a `PORTFOLIO_SCENARIO_ASSUMPTION`.

## Outcome generation

The frozen design contains 10,000 units, control probability 0.100, treatment probability 0.105, and seed `20260824`. Separate deterministic child streams govern assignment and Bernoulli outcomes. The true generating effect is +0.5 percentage point; it is distinct from the observed sample effect of +0.86 percentage points.

## Prospective planning

For a 10% baseline and +1.0-point effect, a two-sided equal-group normal approximation at alpha 0.05 and 80% desired power requires 14,745 observations per group. At 5,000 per group, prospective power is 37.14% and the 80%-power MDE is 1.743 points. These are planning quantities, not evidence derived from the observed result.

## Assumptions and real-experiment requirements

The generator controls one row per unit, assignment before outcome, one exposure, a stable binary outcome, no missingness, and no encoded interference. A real experiment would additionally require verified eligibility, identity persistence, exposure instrumentation, randomization logging, noncompliance handling, guardrail metrics, interference assessment, a prespecified stopping plan, privacy controls, and an organization-approved practical threshold.
