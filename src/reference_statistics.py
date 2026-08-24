"""Separate, standard-library-only in-repository calculations for numerical QA.

These functions intentionally do not import or call the primary statistics module.
"""

from __future__ import annotations

import math
from statistics import NormalDist


def reference_two_proportion_ztest(
    treatment_successes: int,
    treatment_observations: int,
    control_successes: int,
    control_observations: int,
) -> tuple[float, float]:
    treatment_rate = treatment_successes / treatment_observations
    control_rate = control_successes / control_observations
    pooled_rate = (treatment_successes + control_successes) / (
        treatment_observations + control_observations
    )
    variance = pooled_rate * (1 - pooled_rate) * (
        1 / treatment_observations + 1 / control_observations
    )
    z_statistic = (treatment_rate - control_rate) / math.sqrt(variance)
    p_value = math.erfc(abs(z_statistic) / math.sqrt(2))
    return float(z_statistic), float(p_value)


def _wilson_via_quadratic(successes: int, observations: int, alpha: float) -> tuple[float, float]:
    """Wilson endpoints from the quadratic score-test roots."""

    observed_rate = successes / observations
    z = NormalDist().inv_cdf(1 - alpha / 2)
    z2_over_n = z**2 / observations
    coefficient_a = 1 + z2_over_n
    coefficient_b = -(2 * observed_rate + z2_over_n)
    coefficient_c = observed_rate**2
    discriminant = coefficient_b**2 - 4 * coefficient_a * coefficient_c
    root = math.sqrt(max(0.0, discriminant))
    lower = (-coefficient_b - root) / (2 * coefficient_a)
    upper = (-coefficient_b + root) / (2 * coefficient_a)
    return lower, upper


def reference_newcombe_difference_interval(
    treatment_successes: int,
    treatment_observations: int,
    control_successes: int,
    control_observations: int,
    alpha: float = 0.05,
) -> tuple[float, float]:
    treatment_rate = treatment_successes / treatment_observations
    control_rate = control_successes / control_observations
    difference = treatment_rate - control_rate
    t_low, t_high = _wilson_via_quadratic(
        treatment_successes, treatment_observations, alpha
    )
    c_low, c_high = _wilson_via_quadratic(control_successes, control_observations, alpha)
    lower = difference - math.sqrt((treatment_rate - t_low) ** 2 + (c_high - control_rate) ** 2)
    upper = difference + math.sqrt((t_high - treatment_rate) ** 2 + (control_rate - c_low) ** 2)
    return float(lower), float(upper)
