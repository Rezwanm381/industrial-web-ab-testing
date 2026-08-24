"""One-command rebuild for the synthetic industrial-web A/B demonstration."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from src.data_generation import SyntheticDesign, generate_synthetic_ab
from src.data_validation import validate_experiment_data
from src.power import (
    achieved_power,
    build_power_curve,
    minimum_detectable_effect,
    required_sample_size_per_group,
)
from src.reference_statistics import (
    reference_newcombe_difference_interval,
    reference_two_proportion_ztest,
)
from src.statistics import primary_analysis, wald_difference_interval
from src.visualization import (
    plot_conversion_rates,
    plot_effect_interval,
    plot_power_curve,
)


DEVELOPMENT_ROOT = Path(__file__).resolve().parent
OUTPUT_ROOT = DEVELOPMENT_ROOT / ".private_outputs"
GENERATED_DATA_DIR = DEVELOPMENT_ROOT / "data" / "generated"
REPORTS_DIR = DEVELOPMENT_ROOT / "reports"
TABLES_DIR = OUTPUT_ROOT / "tables"
FIGURES_DIR = DEVELOPMENT_ROOT / "docs" / "figures"

ALPHA = 0.05
PRACTICAL_EFFECT_THRESHOLD = 0.010
DESIRED_POWER = 0.80
PLANNING_BASELINE = 0.10
PLANNING_MDE = 0.010


def _ensure_directories() -> None:
    for path in (GENERATED_DATA_DIR, REPORTS_DIR, TABLES_DIR, FIGURES_DIR):
        path.mkdir(parents=True, exist_ok=True)


def _json_ready(value):
    if isinstance(value, dict):
        return {key: _json_ready(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_ready(item) for item in value]
    if hasattr(value, "item"):
        return value.item()
    return value


def _practical_decision(estimate: float, lower: float, upper: float, threshold: float) -> str:
    if lower >= threshold:
        return "MEETS_THRESHOLD_WITH_95_PERCENT_CONFIDENCE"
    if estimate >= threshold:
        return "ESTIMATE_MEETS_THRESHOLD_BUT_UNCERTAIN"
    if upper < threshold:
        return "DOES_NOT_MEET_THRESHOLD_WITH_95_PERCENT_CONFIDENCE"
    return "ESTIMATE_BELOW_THRESHOLD_AND_INTERVAL_CROSSES_THRESHOLD"


def _claim_language(result: dict[str, object], practical_decision: str) -> str:
    lower = float(result["ci_lower"])
    upper = float(result["ci_upper"])
    difference = float(result["absolute_difference"])
    if lower > 0 and practical_decision == "MEETS_THRESHOLD_WITH_95_PERCENT_CONFIDENCE":
        return (
            "Evidence in this synthetic demonstration supports a positive treatment effect "
            f"of approximately {difference * 100:.2f} percentage points under the stated assumptions."
        )
    if lower <= 0 <= upper:
        return (
            "The observed difference is compatible with both small negative and positive effects; "
            "the experiment does not establish improvement."
        )
    if upper < 0:
        return (
            "The interval is entirely negative in this synthetic demonstration; under the stated "
            "assumptions, the treatment is associated with a lower conversion probability."
        )
    return (
        "The interval excludes zero, but the evidence does not clear the stated practical-effect "
        "threshold with 95% confidence."
    )


def _independent_crosscheck(result: dict[str, object]) -> dict[str, object]:
    reference_z, reference_p = reference_two_proportion_ztest(
        int(result["treatment_conversions"]),
        int(result["treatment_n"]),
        int(result["control_conversions"]),
        int(result["control_n"]),
    )
    reference_ci = reference_newcombe_difference_interval(
        int(result["treatment_conversions"]),
        int(result["treatment_n"]),
        int(result["control_conversions"]),
        int(result["control_n"]),
        ALPHA,
    )
    differences = {
        "z_absolute_difference": abs(float(result["z_statistic"]) - reference_z),
        "p_absolute_difference": abs(float(result["p_value"]) - reference_p),
        "ci_lower_absolute_difference": abs(float(result["ci_lower"]) - reference_ci[0]),
        "ci_upper_absolute_difference": abs(float(result["ci_upper"]) - reference_ci[1]),
    }
    passed = (
        differences["z_absolute_difference"] < 1e-12
        and differences["p_absolute_difference"] < 1e-12
        and differences["ci_lower_absolute_difference"] < 1e-10
        and differences["ci_upper_absolute_difference"] < 1e-10
    )
    return {
        "implementation": "separate in-repository standard-library reference using erfc tails and quadratic Wilson roots",
        "reference_z": reference_z,
        "reference_p_value": reference_p,
        "reference_ci_lower": reference_ci[0],
        "reference_ci_upper": reference_ci[1],
        **differences,
        "agreement_status": "PASS" if passed else "FAIL",
    }


def _write_data_quality_report(quality: dict[str, object], design: SyntheticDesign) -> None:
    counts = quality["group_counts"]
    content = f"""# Data Quality Report

Status: **{quality['status']}**

## Data contract

- Source: newly generated synthetic demonstration data; no historical rows are included.
- Experimental unit: one synthetic eligible website visitor represented by one `unit_id`.
- Assignment: seeded 1:1 random assignment using a dedicated random-number stream.
- Exposure: one simulated render of the assigned interface; `exposed = 1` and `exposure_count = 1`.
- Primary outcome: binary `converted`, indicating a simulated form submission during the fixed response window.

## Programmatic checks

| Check | Result |
|---|---:|
| Rows | {quality['row_count']:,} |
| Unique units | {quality['unique_unit_count']:,} |
| Duplicate unit rows | {quality['duplicate_unit_rows']} |
| Missing required cells | {quality['missing_required_cells']} |
| Invalid treatment rows | {quality['invalid_treatment_rows']} |
| Invalid outcome rows | {quality['invalid_outcome_rows']} |
| Invalid exposure rows | {quality['invalid_exposure_rows']} |
| Invalid exposure-count rows | {quality['invalid_exposure_count_rows']} |
| Invalid source-label rows | {quality['invalid_source_label_rows']} |
| Control units | {counts['control']:,} |
| Treatment units | {counts['treatment']:,} |
| Largest/smallest group ratio | {quality['largest_to_smallest_group_ratio']:.3f} |

## Assignment and generation integrity

The generator spawns separate deterministic child streams from seed `{design.random_seed}`. It shuffles treatment labels before any outcomes are drawn, then generates each binary outcome from the probability assigned to that unit's treatment. Changing the treatment-effect parameter therefore does not change assignment.

All quality gates passed. These checks establish the synthetic data contract; they do not supply evidence about the unknown assignment, exposure, or independence properties of the historical course dataset.
"""
    (REPORTS_DIR / "data_quality_report.md").write_text(content, encoding="utf-8")


def _write_results_report(
    result: dict[str, object],
    practical_decision: str,
    claim: str,
    crosscheck: dict[str, object],
    power_design: dict[str, object],
    wald_ci: tuple[float, float],
) -> None:
    relative_lift = result["relative_lift"]
    statistical_decision = (
        "REJECT_NULL" if result["statistically_significant"] else "FAIL_TO_REJECT_NULL"
    )
    content = f"""# Results Summary

## Primary result

| Metric | Result |
|---|---:|
| Control n | {result['control_n']:,} |
| Treatment n | {result['treatment_n']:,} |
| Control conversions | {result['control_conversions']:,} |
| Treatment conversions | {result['treatment_conversions']:,} |
| Control rate | {result['control_rate']:.4%} |
| Treatment rate | {result['treatment_rate']:.4%} |
| Absolute difference (treatment - control) | {result['absolute_difference'] * 100:+.3f} percentage points |
| Relative lift (secondary descriptive measure) | {relative_lift:+.3%} |
| 95% Newcombe interval | [{result['ci_lower'] * 100:+.3f}, {result['ci_upper'] * 100:+.3f}] percentage points |
| Two-sided pooled z statistic | {result['z_statistic']:.6f} |
| Two-sided p-value | {result['p_value']:.6f} |
| Statistical decision at alpha = {ALPHA:.2f} | {statistical_decision} |
| Practical decision at +1.0 point | {practical_decision} |

## Interpretation

{claim}

Statistical significance and practical significance answer different questions. The statistical decision uses a two-sided 5% test. The practical decision compares the estimate and interval with a +1.0 percentage-point threshold that is explicitly a **PORTFOLIO_SCENARIO_ASSUMPTION**, not a validated business or ROI threshold.

## Prospective design

At a 10% baseline, two-sided alpha of 0.05, 80% desired power, and a +1.0 percentage-point minimum detectable effect, the prospective requirement is **{power_design['required_n_per_group']:,} units per group** ({power_design['required_total_n']:,} total). The current synthetic demonstration has {result['control_n']:,} per group and prospective power of {power_design['power_at_current_n']:.1%} for that effect; its corresponding 80%-power MDE is {power_design['mde_at_current_n'] * 100:.3f} percentage points.

Post-hoc observed power is not used to validate the result. Power and MDE are prospective design quantities tied to declared effect sizes.

## Robustness and separate numerical cross-check

- Alternative unpooled Wald interval: [{wald_ci[0] * 100:+.3f}, {wald_ci[1] * 100:+.3f}] percentage points.
- Exact 1:1 assignment balance was verified by construction and by the data-quality checks.
- Practical-threshold sensitivity is exported in `.private_outputs/tables/robustness_checks.csv`.
- The primary z statistic, p-value, and Newcombe interval were reproduced by a separate in-repository standard-library implementation using `erfc` normal tails and quadratic Wilson roots: **{crosscheck['agreement_status']}**. This is internal numerical QA, not external validation.

## Multiplicity and advanced methods

There is one primary hypothesis, so multiplicity correction is unnecessary for the primary analysis. No subgroup search, Bayesian analysis, or sequential-testing procedure was added. This deliberately keeps one coherent frequentist core. Ordinary fixed-horizon p-values would not remain valid under repeated outcome peeking and significance-based stopping.
"""
    (REPORTS_DIR / "results_summary.md").write_text(content, encoding="utf-8")


def main() -> None:
    _ensure_directories()
    design = SyntheticDesign()
    data = generate_synthetic_ab(design)
    quality = validate_experiment_data(data)
    data.to_csv(GENERATED_DATA_DIR / "synthetic_ab_experiment.csv", index=False)
    (GENERATED_DATA_DIR / "generation_config.json").write_text(
        json.dumps(design.to_dict(), indent=2), encoding="utf-8"
    )

    result = primary_analysis(data, alpha=ALPHA)
    practical_decision = _practical_decision(
        float(result["absolute_difference"]),
        float(result["ci_lower"]),
        float(result["ci_upper"]),
        PRACTICAL_EFFECT_THRESHOLD,
    )
    statistical_decision = (
        "REJECT_NULL" if result["statistically_significant"] else "FAIL_TO_REJECT_NULL"
    )
    claim = _claim_language(result, practical_decision)

    crosscheck = _independent_crosscheck(result)
    if crosscheck["agreement_status"] != "PASS":
        raise RuntimeError(f"separate in-repository numerical cross-check failed: {crosscheck}")

    wald_ci = wald_difference_interval(
        int(result["treatment_conversions"]),
        int(result["treatment_n"]),
        int(result["control_conversions"]),
        int(result["control_n"]),
        ALPHA,
    )
    required_n = required_sample_size_per_group(
        PLANNING_BASELINE, PLANNING_MDE, ALPHA, DESIRED_POWER
    )
    power_at_current_n = achieved_power(
        PLANNING_BASELINE, PLANNING_MDE, int(result["control_n"]), ALPHA
    )
    mde_at_current_n = minimum_detectable_effect(
        PLANNING_BASELINE, int(result["control_n"]), ALPHA, DESIRED_POWER
    )
    power_design = {
        "baseline_rate": PLANNING_BASELINE,
        "alpha": ALPHA,
        "desired_power": DESIRED_POWER,
        "minimum_detectable_effect": PLANNING_MDE,
        "required_n_per_group": required_n,
        "required_total_n": 2 * required_n,
        "power_at_current_n": power_at_current_n,
        "mde_at_current_n": mde_at_current_n,
    }

    result_row = {
        "Control_N": result["control_n"],
        "Treatment_N": result["treatment_n"],
        "Control_Conversions": result["control_conversions"],
        "Treatment_Conversions": result["treatment_conversions"],
        "Control_Rate": result["control_rate"],
        "Treatment_Rate": result["treatment_rate"],
        "Absolute_Difference": result["absolute_difference"],
        "Relative_Lift": result["relative_lift"],
        "CI_Lower": result["ci_lower"],
        "CI_Upper": result["ci_upper"],
        "P_Value": result["p_value"],
        "Statistical_Decision": statistical_decision,
        "Practical_Decision": practical_decision,
    }
    pd.DataFrame([result_row]).to_csv(TABLES_DIR / "results_table.csv", index=False)
    pd.DataFrame([power_design]).to_csv(TABLES_DIR / "power_analysis.csv", index=False)
    pd.DataFrame([crosscheck]).to_csv(TABLES_DIR / "independent_crosscheck.csv", index=False)

    threshold_rows = []
    for threshold in (0.005, 0.010, 0.015):
        threshold_rows.append(
            {
                "check": "practical_threshold_sensitivity",
                "threshold": threshold,
                "decision": _practical_decision(
                    float(result["absolute_difference"]),
                    float(result["ci_lower"]),
                    float(result["ci_upper"]),
                    threshold,
                ),
            }
        )
    threshold_rows.extend(
        [
            {"check": "alternative_wald_ci_lower", "threshold": None, "decision": wald_ci[0]},
            {"check": "alternative_wald_ci_upper", "threshold": None, "decision": wald_ci[1]},
            {"check": "assignment_balance", "threshold": 1.0, "decision": quality["largest_to_smallest_group_ratio"]},
        ]
    )
    pd.DataFrame(threshold_rows).to_csv(TABLES_DIR / "robustness_checks.csv", index=False)

    power_curve = build_power_curve(PLANNING_BASELINE, PLANNING_MDE, ALPHA)
    power_curve.to_csv(TABLES_DIR / "power_curve.csv", index=False)

    full_results = {
        "design": design.to_dict(),
        "quality": quality,
        "primary_analysis": result,
        "statistical_decision": statistical_decision,
        "practical_threshold": PRACTICAL_EFFECT_THRESHOLD,
        "practical_decision": practical_decision,
        "claim_language": claim,
        "power_design": power_design,
        "wald_interval": {"lower": wald_ci[0], "upper": wald_ci[1]},
        "independent_crosscheck": crosscheck,
    }
    (TABLES_DIR / "analysis_results.json").write_text(
        json.dumps(_json_ready(full_results), indent=2), encoding="utf-8"
    )

    plot_conversion_rates(data, FIGURES_DIR / "01_conversion_rates_ci.png", ALPHA)
    plot_effect_interval(
        float(result["absolute_difference"]),
        float(result["ci_lower"]),
        float(result["ci_upper"]),
        PRACTICAL_EFFECT_THRESHOLD,
        FIGURES_DIR / "02_effect_interval.png",
    )
    plot_power_curve(
        power_curve,
        required_n,
        FIGURES_DIR / "03_power_curve.png",
        DESIRED_POWER,
    )

    _write_data_quality_report(quality, design)
    _write_results_report(
        result,
        practical_decision,
        claim,
        crosscheck,
        power_design,
        wald_ci,
    )

    print(json.dumps(_json_ready(full_results), indent=2))


if __name__ == "__main__":
    main()
