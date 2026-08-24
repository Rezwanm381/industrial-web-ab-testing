# Data Quality Report

Status: **PASS**

## Data contract

- Source: newly generated synthetic demonstration data; no historical rows are included.
- Experimental unit: one synthetic eligible website visitor represented by one `unit_id`.
- Assignment: seeded 1:1 random assignment using a dedicated random-number stream.
- Exposure: one simulated render of the assigned interface; `exposed = 1` and `exposure_count = 1`.
- Primary outcome: binary `converted`, indicating a simulated form submission during the fixed response window.

## Programmatic checks

| Check | Result |
|---|---:|
| Rows | 10,000 |
| Unique units | 10,000 |
| Duplicate unit rows | 0 |
| Missing required cells | 0 |
| Invalid treatment rows | 0 |
| Invalid outcome rows | 0 |
| Invalid exposure rows | 0 |
| Invalid exposure-count rows | 0 |
| Invalid source-label rows | 0 |
| Control units | 5,000 |
| Treatment units | 5,000 |
| Largest/smallest group ratio | 1.000 |

## Assignment and generation integrity

The generator spawns separate deterministic child streams from seed `20260824`. It shuffles treatment labels before any outcomes are drawn, then generates each binary outcome from the probability assigned to that unit's treatment. Changing the treatment-effect parameter therefore does not change assignment.

All quality gates passed. These checks establish the synthetic data contract; they do not supply evidence about the unknown assignment, exposure, or independence properties of the historical course dataset.
