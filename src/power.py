"""Prospective power and MDE planning using a two-sample normal approximation."""

from __future__ import annotations

import math
from statistics import NormalDist

import pandas as pd


STANDARD_NORMAL = NormalDist()


def cohen_h(rate_a: float, rate_b: float) -> float:
    """Absolute arcsine-scale separation between two binomial proportions."""

    if not 0 < rate_a < 1 or not 0 < rate_b < 1:
        raise ValueError("rates must be strictly between 0 and 1")
    return abs(2 * math.asin(math.sqrt(rate_a)) - 2 * math.asin(math.sqrt(rate_b)))


def achieved_power(
    baseline_rate: float,
    absolute_effect: float,
    n_per_group: int,
    alpha: float = 0.05,
) -> float:
    """Approximate two-sided power using Cohen's h and equal group sizes."""

    treatment_rate = baseline_rate + absolute_effect
    if n_per_group <= 1:
        raise ValueError("n_per_group must be greater than 1")
    if not 0 < alpha < 1:
        raise ValueError("alpha must be between 0 and 1")
    effect_size = cohen_h(treatment_rate, baseline_rate)
    noncentrality = effect_size * math.sqrt(n_per_group / 2)
    critical = STANDARD_NORMAL.inv_cdf(1 - alpha / 2)
    upper_tail = 1 - STANDARD_NORMAL.cdf(critical - noncentrality)
    lower_tail = STANDARD_NORMAL.cdf(-critical - noncentrality)
    return float(upper_tail + lower_tail)


def required_sample_size_per_group(
    baseline_rate: float,
    minimum_detectable_effect: float,
    alpha: float = 0.05,
    desired_power: float = 0.80,
) -> int:
    """Find the smallest integer n per group reaching desired prospective power."""

    if not 0 < desired_power < 1:
        raise ValueError("desired_power must be between 0 and 1")
    low, high = 2, 2
    while achieved_power(baseline_rate, minimum_detectable_effect, high, alpha) < desired_power:
        high *= 2
        if high > 100_000_000:
            raise ValueError("sample-size requirement exceeded the search limit")
    while low < high:
        middle = (low + high) // 2
        if achieved_power(baseline_rate, minimum_detectable_effect, middle, alpha) >= desired_power:
            high = middle
        else:
            low = middle + 1
    return low


def minimum_detectable_effect(
    baseline_rate: float,
    n_per_group: int,
    alpha: float = 0.05,
    desired_power: float = 0.80,
    tolerance: float = 1e-7,
) -> float:
    """Solve for a positive absolute MDE by deterministic bisection."""

    low = tolerance
    high = min(0.50, 1 - baseline_rate - tolerance)
    if achieved_power(baseline_rate, high, n_per_group, alpha) < desired_power:
        raise ValueError("desired power is unattainable within the search range")
    for _ in range(80):
        middle = (low + high) / 2
        if achieved_power(baseline_rate, middle, n_per_group, alpha) >= desired_power:
            high = middle
        else:
            low = middle
        if high - low <= tolerance:
            break
    return float(high)


def build_power_curve(
    baseline_rate: float,
    minimum_detectable_effect: float,
    alpha: float = 0.05,
    start: int = 1_000,
    stop: int = 25_000,
    step: int = 1_000,
) -> pd.DataFrame:
    """Return prospective power across a declared range of per-group sample sizes."""

    sample_sizes = list(range(start, stop + 1, step))
    return pd.DataFrame(
        {
            "n_per_group": sample_sizes,
            "power": [
                achieved_power(baseline_rate, minimum_detectable_effect, n, alpha)
                for n in sample_sizes
            ],
        }
    )
