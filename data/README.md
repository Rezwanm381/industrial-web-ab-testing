# Data

## Synthetic public dataset

`generated/synthetic_ab_experiment.csv` is newly generated, deterministic, and explicitly synthetic. Every row is an artificial experimental unit created to demonstrate statistical methodology. The file contains no real identities, users, visitors, customers, sessions, company behavior, or production observations.

Generation assumptions are visible in `src/data_generation.py` and recorded in `generated/generation_config.json`:

- 10,000 synthetic experimental units;
- exact 1:1 control/treatment allocation, giving each unit marginal treatment probability 0.50;
- control outcome probability 0.100;
- treatment outcome probability 0.105;
- predefined true generating effect +0.005 probability units (+0.5 percentage point);
- fixed seed `20260824`;
- one row and one simulated exposure per unit;
- no segments, repeated units, missing outcomes, clustering, or encoded interference.

Assignment is shuffled before outcomes are drawn. Separate child random streams derived from the fixed seed isolate assignment from the outcome probabilities. The seed and probabilities are fixed before analysis and are not searched or changed based on the observed p-value.

## Schema

| Field | Definition |
|---|---|
| `unit_id` | Unique synthetic experimental-unit identifier. |
| `treatment` | `control` or `treatment`. |
| `exposed` | Always 1; the assigned interface was simulated as rendered. |
| `exposure_count` | Always 1; repeated exposure is excluded by design. |
| `converted` | Binary simulated form-submission outcome. |
| `data_source` | Always `synthetic`. |
| `scenario` | Declared generation scenario, `near_null_effect`. |

The machine-readable contract is in `schema/synthetic_ab_experiment.schema.json`. Programmatic validation additionally rejects missing required cells, duplicate unit IDs, invalid group labels, impossible outcomes, invalid exposure counts, and non-synthetic source labels.

## Reproduction fingerprint

With the documented defaults and current required dependency versions, the generated CSV has SHA-256:

`BF554C12C5054815378A5887BBF47B93841141CF52C3676E422F805655CFD2BE`

The regression test records this fingerprint to detect accidental changes to the frozen demonstration dataset. It is a reproducibility control, not a target used to search seeds.

## Historical data exclusion

The course file `industrial_web_AB_test.csv` is `COURSE_PROVIDED` and `NOT_ALLOWED FOR REDISTRIBUTION`. It is not copied into this development data folder or generated outputs. Its public source, creator, license, assignment mechanism, and exposure process are not verified; it remains an immutable internal reference outside the public candidate.
