import hashlib
import unittest

import pandas as pd

from src.data_generation import SyntheticDesign, generate_synthetic_ab
from src.data_validation import validate_experiment_data


class DataGenerationTests(unittest.TestCase):
    def test_generation_is_deterministic(self) -> None:
        design = SyntheticDesign(number_of_units=200, random_seed=12345)
        pd.testing.assert_frame_equal(generate_synthetic_ab(design), generate_synthetic_ab(design))

    def test_default_seed_matches_validated_dataset_fingerprint(self) -> None:
        """Guard the frozen public demonstration against accidental generation drift."""

        csv_bytes = generate_synthetic_ab(SyntheticDesign()).to_csv(index=False).encode("utf-8")
        fingerprint = hashlib.sha256(csv_bytes).hexdigest().upper()
        self.assertEqual(
            fingerprint,
            "BF554C12C5054815378A5887BBF47B93841141CF52C3676E422F805655CFD2BE",
        )

    def test_units_are_unique_and_assignments_are_balanced(self) -> None:
        data = generate_synthetic_ab(SyntheticDesign(number_of_units=1_000, random_seed=7))
        self.assertTrue(data["unit_id"].is_unique)
        self.assertEqual(data["treatment"].value_counts().to_dict(), {"control": 500, "treatment": 500})
        self.assertTrue(set(data["converted"].unique()).issubset({0, 1}))

    def test_assignment_is_invariant_to_outcome_probability(self) -> None:
        base = SyntheticDesign(number_of_units=500, treatment_effect_absolute=0.0, random_seed=99)
        changed = SyntheticDesign(number_of_units=500, treatment_effect_absolute=0.10, random_seed=99)
        pd.testing.assert_series_equal(
            generate_synthetic_ab(base)["treatment"],
            generate_synthetic_ab(changed)["treatment"],
        )

    def test_validation_accepts_valid_data(self) -> None:
        quality = validate_experiment_data(
            generate_synthetic_ab(SyntheticDesign(number_of_units=100, random_seed=5))
        )
        self.assertEqual(quality["status"], "PASS")
        self.assertEqual(quality["duplicate_unit_rows"], 0)

    def test_validation_rejects_malformed_values(self) -> None:
        data = generate_synthetic_ab(SyntheticDesign(number_of_units=100, random_seed=5))
        for malformed in (
            data.assign(converted=2),
            data.assign(treatment="unknown"),
            data.assign(exposure_count=2),
        ):
            with self.assertRaises(ValueError):
                validate_experiment_data(malformed)

    def test_validation_rejects_duplicate_units(self) -> None:
        data = generate_synthetic_ab(SyntheticDesign(number_of_units=100, random_seed=5))
        data.loc[1, "unit_id"] = data.loc[0, "unit_id"]
        with self.assertRaisesRegex(ValueError, "duplicate"):
            validate_experiment_data(data)


if __name__ == "__main__":
    unittest.main()
