import math
import unittest

import pandas as pd

from src.reference_statistics import (
    reference_newcombe_difference_interval,
    reference_two_proportion_ztest,
)
from src.statistics import (
    absolute_difference,
    conversion_summary,
    newcombe_difference_interval,
    relative_lift,
    two_proportion_ztest,
)


class StatisticsTests(unittest.TestCase):
    def test_conversion_rate_and_effect_calculations(self) -> None:
        data = pd.DataFrame(
            {
                "treatment": ["control"] * 10 + ["treatment"] * 10,
                "converted": [1, 1] + [0] * 8 + [1, 1, 1] + [0] * 7,
            }
        )
        summary = conversion_summary(data)
        self.assertEqual(summary.loc["control", "conversion_rate"], 0.2)
        self.assertEqual(summary.loc["treatment", "conversion_rate"], 0.3)
        self.assertTrue(math.isclose(absolute_difference(0.3, 0.2), 0.1))
        self.assertTrue(math.isclose(relative_lift(0.3, 0.2), 0.5))

    def test_known_two_sided_reference(self) -> None:
        z_statistic, p_value = two_proportion_ztest(60, 500, 50, 500)
        self.assertTrue(math.isclose(z_statistic, 1.010668, rel_tol=0, abs_tol=1e-6))
        self.assertTrue(math.isclose(p_value, 0.312175, rel_tol=0, abs_tol=1e-6))

    def test_z_test_matches_independent_reference(self) -> None:
        custom = two_proportion_ztest(125, 1_000, 101, 1_000)
        reference = reference_two_proportion_ztest(125, 1_000, 101, 1_000)
        self.assertTrue(math.isclose(custom[0], reference[0], rel_tol=0, abs_tol=1e-12))
        self.assertTrue(math.isclose(custom[1], reference[1], rel_tol=0, abs_tol=1e-12))

    def test_newcombe_interval_matches_independent_reference(self) -> None:
        custom = newcombe_difference_interval(125, 1_000, 101, 1_000)
        reference = reference_newcombe_difference_interval(125, 1_000, 101, 1_000)
        self.assertTrue(math.isclose(custom[0], reference[0], rel_tol=0, abs_tol=1e-10))
        self.assertTrue(math.isclose(custom[1], reference[1], rel_tol=0, abs_tol=1e-10))


if __name__ == "__main__":
    unittest.main()
