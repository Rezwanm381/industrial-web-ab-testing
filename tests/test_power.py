import math
import unittest

from src.power import (
    achieved_power,
    minimum_detectable_effect,
    required_sample_size_per_group,
)


class PowerTests(unittest.TestCase):
    def test_smaller_effect_requires_larger_sample(self) -> None:
        self.assertGreater(
            required_sample_size_per_group(0.10, 0.01),
            required_sample_size_per_group(0.10, 0.02),
        )

    def test_required_sample_reaches_target_power(self) -> None:
        required = required_sample_size_per_group(0.10, 0.01, desired_power=0.80)
        self.assertGreaterEqual(achieved_power(0.10, 0.01, required), 0.80)
        self.assertLess(achieved_power(0.10, 0.01, required - 1), 0.80)

    def test_mde_bisection_is_consistent_with_power(self) -> None:
        mde = minimum_detectable_effect(0.10, 5_000, desired_power=0.80)
        self.assertTrue(
            math.isclose(
                achieved_power(0.10, mde, 5_000),
                0.80,
                rel_tol=0,
                abs_tol=5e-5,
            )
        )


if __name__ == "__main__":
    unittest.main()

