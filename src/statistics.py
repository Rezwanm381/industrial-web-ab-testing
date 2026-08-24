"""Primary estimands, intervals, and tests for two independent proportions."""

from __future__ import annotations

import math
from statistics import NormalDist
from typing import Any

import pandas as pd


STANDARD_NORMAL = NormalDist()


def conversion_summary(
    df: pd.DataFrame,
    group_column: str = "treatment",
    outcome_column: str = "converted",
) -> pd.DataFrame:
    """Return counts, events, and conversion rates in a stable group order."""

    summary = (
        df.groupby(group_column, observed=True)[outcome_column]
        .agg(n="count", conversions="sum")
        .reindex(["control", "treatment"])
    )
    if summary.isna().any().any():
        raise ValueError("both control and treatment groups are required")
    summary["n"] = summary["n"].astype(int)
    summary["conversions"] = summary["conversions"].astype(int)
    summary["conversion_rate"] = summary["conversions"] / summary["n"]
    return summary


def absolute_difference(treatment_rate: float, control_rate: float) -> float:
    return float(treatment_rate - control_rate)


def relative_lift(treatment_rate: float, control_rate: float) -> float | None:
    if control_rate == 0:
        return None
    return float((treatment_rate - control_rate) / control_rate)


def wilson_interval(successes: int, observations: int, alpha: float = 0.05) -> tuple[float, float]:
    """Wilson score interval for one binomial proportion."""

    if observations <= 0 or not 0 <= successes <= observations:
        raise ValueError("successes and observations are inconsistent")
    if not 0 < alpha < 1:
        raise ValueError("alpha must be between 0 and 1")
    proportion = successes / observations
    z = float(STANDARD_NORMAL.inv_cdf(1 - alpha / 2))
    denominator = 1 + z**2 / observations
    center = (proportion + z**2 / (2 * observations)) / denominator
    half_width = (
        z
        * math.sqrt(
            proportion * (1 - proportion) / observations
            + z**2 / (4 * observations**2)
        )
        / denominator
    )
    return max(0.0, center - half_width), min(1.0, center + half_width)


def newcombe_difference_interval(
    treatment_successes: int,
    treatment_observations: int,
    control_successes: int,
    control_observations: int,
    alpha: float = 0.05,
) -> tuple[float, float]:
    """Newcombe hybrid-score interval for treatment minus control."""

    treatment_rate = treatment_successes / treatment_observations
    control_rate = control_successes / control_observations
    difference = treatment_rate - control_rate
    t_low, t_high = wilson_interval(treatment_successes, treatment_observations, alpha)
    c_low, c_high = wilson_interval(control_successes, control_observations, alpha)
    lower = difference - math.sqrt((treatment_rate - t_low) ** 2 + (c_high - control_rate) ** 2)
    upper = difference + math.sqrt((t_high - treatment_rate) ** 2 + (control_rate - c_low) ** 2)
    return float(lower), float(upper)


def wald_difference_interval(
    treatment_successes: int,
    treatment_observations: int,
    control_successes: int,
    control_observations: int,
    alpha: float = 0.05,
) -> tuple[float, float]:
    """Unpooled Wald interval retained only as a compact sensitivity check."""

    treatment_rate = treatment_successes / treatment_observations
    control_rate = control_successes / control_observations
    difference = treatment_rate - control_rate
    standard_error = math.sqrt(
        treatment_rate * (1 - treatment_rate) / treatment_observations
        + control_rate * (1 - control_rate) / control_observations
    )
    z = float(STANDARD_NORMAL.inv_cdf(1 - alpha / 2))
    return difference - z * standard_error, difference + z * standard_error


def two_proportion_ztest(
    treatment_successes: int,
    treatment_observations: int,
    control_successes: int,
    control_observations: int,
) -> tuple[float, float]:
    """Two-sided pooled two-sample proportion z-test for equality."""

    for successes, observations in (
        (treatment_successes, treatment_observations),
        (control_successes, control_observations),
    ):
        if observations <= 0 or not 0 <= successes <= observations:
            raise ValueError("successes and observations are inconsistent")
    pooled = (treatment_successes + control_successes) / (
        treatment_observations + control_observations
    )
    standard_error = math.sqrt(
        pooled
        * (1 - pooled)
        * (1 / treatment_observations + 1 / control_observations)
    )
    difference = (
        treatment_successes / treatment_observations
        - control_successes / control_observations
    )
    if standard_error == 0:
        if difference == 0:
            return 0.0, 1.0
        return math.copysign(math.inf, difference), 0.0
    z_statistic = difference / standard_error
    p_value = 2 * (1 - float(STANDARD_NORMAL.cdf(abs(z_statistic))))
    return float(z_statistic), p_value


def primary_analysis(df: pd.DataFrame, alpha: float = 0.05) -> dict[str, Any]:
    """Compute the pre-specified primary conversion analysis."""

    summary = conversion_summary(df)
    control_n = int(summary.loc["control", "n"])
    treatment_n = int(summary.loc["treatment", "n"])
    control_conversions = int(summary.loc["control", "conversions"])
    treatment_conversions = int(summary.loc["treatment", "conversions"])
    control_rate = float(summary.loc["control", "conversion_rate"])
    treatment_rate = float(summary.loc["treatment", "conversion_rate"])
    difference = absolute_difference(treatment_rate, control_rate)
    lift = relative_lift(treatment_rate, control_rate)
    ci_lower, ci_upper = newcombe_difference_interval(
        treatment_conversions,
        treatment_n,
        control_conversions,
        control_n,
        alpha,
    )
    z_statistic, p_value = two_proportion_ztest(
        treatment_conversions,
        treatment_n,
        control_conversions,
        control_n,
    )
    return {
        "control_n": control_n,
        "treatment_n": treatment_n,
        "control_conversions": control_conversions,
        "treatment_conversions": treatment_conversions,
        "control_rate": control_rate,
        "treatment_rate": treatment_rate,
        "absolute_difference": difference,
        "relative_lift": lift,
        "ci_lower": ci_lower,
        "ci_upper": ci_upper,
        "z_statistic": z_statistic,
        "p_value": p_value,
        "alpha": alpha,
        "statistically_significant": bool(p_value < alpha),
    }
