"""Deterministic synthetic data generation for the portfolio experiment."""

from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class SyntheticDesign:
    """Pre-specified design inputs for one fixed-horizon A/B demonstration."""

    number_of_units: int = 10_000
    treatment_fraction: float = 0.50
    baseline_conversion_probability: float = 0.10
    treatment_effect_absolute: float = 0.005
    random_seed: int = 20_260_824
    scenario_name: str = "near_null_effect"

    def validate(self) -> None:
        if self.number_of_units < 4:
            raise ValueError("number_of_units must be at least 4")
        if not 0 < self.treatment_fraction < 1:
            raise ValueError("treatment_fraction must be between 0 and 1")
        treatment_probability = (
            self.baseline_conversion_probability + self.treatment_effect_absolute
        )
        if not 0 <= self.baseline_conversion_probability <= 1:
            raise ValueError("baseline_conversion_probability must be in [0, 1]")
        if not 0 <= treatment_probability <= 1:
            raise ValueError("treatment conversion probability must be in [0, 1]")

    def to_dict(self) -> dict[str, object]:
        self.validate()
        return asdict(self)


def generate_synthetic_ab(design: SyntheticDesign) -> pd.DataFrame:
    """Generate one row per synthetic unit with assignment before outcome.

    Separate child random-number streams are spawned for assignment and outcome.
    Consequently, changing an outcome probability cannot change assignment.
    """

    design.validate()
    n_treatment = int(round(design.number_of_units * design.treatment_fraction))
    n_control = design.number_of_units - n_treatment
    if n_control == 0 or n_treatment == 0:
        raise ValueError("both groups must contain at least one unit")

    assignment_seed, outcome_seed = np.random.SeedSequence(design.random_seed).spawn(2)
    assignment_rng = np.random.default_rng(assignment_seed)
    outcome_rng = np.random.default_rng(outcome_seed)

    assignments = np.array(
        ["control"] * n_control + ["treatment"] * n_treatment,
        dtype=object,
    )
    assignment_rng.shuffle(assignments)

    probabilities = np.where(
        assignments == "treatment",
        design.baseline_conversion_probability + design.treatment_effect_absolute,
        design.baseline_conversion_probability,
    )
    outcomes = outcome_rng.binomial(1, probabilities).astype(int)

    return pd.DataFrame(
        {
            "unit_id": [f"SYN-{i:06d}" for i in range(1, design.number_of_units + 1)],
            "treatment": assignments,
            "exposed": np.ones(design.number_of_units, dtype=int),
            "exposure_count": np.ones(design.number_of_units, dtype=int),
            "converted": outcomes,
            "data_source": "synthetic",
            "scenario": design.scenario_name,
        }
    )

