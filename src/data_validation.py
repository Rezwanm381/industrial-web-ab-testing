"""Data-contract checks for the synthetic A/B experiment."""

from __future__ import annotations

from typing import Any

import pandas as pd


REQUIRED_COLUMNS = {
    "unit_id",
    "treatment",
    "exposed",
    "exposure_count",
    "converted",
    "data_source",
    "scenario",
}
ALLOWED_TREATMENTS = {"control", "treatment"}


def validate_experiment_data(df: pd.DataFrame) -> dict[str, Any]:
    """Validate the analysis table and return machine-readable quality metrics."""

    errors: list[str] = []
    missing_columns = sorted(REQUIRED_COLUMNS.difference(df.columns))
    if missing_columns:
        raise ValueError(f"missing required columns: {missing_columns}")

    missing_cells = int(df[list(REQUIRED_COLUMNS)].isna().sum().sum())
    duplicate_units = int(df["unit_id"].duplicated(keep=False).sum())
    invalid_treatments = int((~df["treatment"].isin(ALLOWED_TREATMENTS)).sum())
    invalid_outcomes = int((~df["converted"].isin([0, 1])).sum())
    invalid_exposed = int((df["exposed"] != 1).sum())
    invalid_exposure_counts = int((df["exposure_count"] != 1).sum())
    invalid_source_labels = int((df["data_source"] != "synthetic").sum())

    if len(df) == 0:
        errors.append("dataset has no rows")
    if missing_cells:
        errors.append(f"{missing_cells} required cells are missing")
    if duplicate_units:
        errors.append(f"{duplicate_units} rows have duplicate unit IDs")
    if invalid_treatments:
        errors.append(f"{invalid_treatments} rows have invalid treatment labels")
    if invalid_outcomes:
        errors.append(f"{invalid_outcomes} rows have impossible binary outcomes")
    if invalid_exposed:
        errors.append(f"{invalid_exposed} rows are not marked exposed")
    if invalid_exposure_counts:
        errors.append(f"{invalid_exposure_counts} rows do not have one exposure")
    if invalid_source_labels:
        errors.append(f"{invalid_source_labels} rows are not labeled synthetic")

    group_counts = {
        str(key): int(value)
        for key, value in df["treatment"].value_counts().sort_index().items()
    }
    if set(group_counts) != ALLOWED_TREATMENTS:
        errors.append("both control and treatment groups must be present")

    if errors:
        raise ValueError("; ".join(errors))

    smallest = min(group_counts.values())
    largest = max(group_counts.values())
    return {
        "row_count": int(len(df)),
        "unique_unit_count": int(df["unit_id"].nunique()),
        "duplicate_unit_rows": duplicate_units,
        "missing_required_cells": missing_cells,
        "invalid_treatment_rows": invalid_treatments,
        "invalid_outcome_rows": invalid_outcomes,
        "invalid_exposure_rows": invalid_exposed,
        "invalid_exposure_count_rows": invalid_exposure_counts,
        "invalid_source_label_rows": invalid_source_labels,
        "group_counts": group_counts,
        "largest_to_smallest_group_ratio": float(largest / smallest),
        "status": "PASS",
    }

