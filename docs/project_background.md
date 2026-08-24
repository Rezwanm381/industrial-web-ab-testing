# Project Background

This portfolio project demonstrates how to analyze and communicate a binary-outcome A/B test when the observed difference is uncertain. It is an expanded rebuild derived from graduate coursework, with a new reproducible synthetic dataset replacing historical course data that cannot be redistributed.

Useful professional discussion topics include:

- **Effect size and confidence intervals:** a p-value alone does not show the magnitude or precision of an estimate; the interval makes compatible negative and positive effects visible.
- **Failure to reject:** p > 0.05 means the demonstration did not establish improvement, not that the groups are equal or that no effect exists.
- **Prospective power:** sample-size planning should occur before an experiment and should target an effect worth detecting.
- **Minimum detectable effect:** MDE translates a sample-size constraint into the smallest effect the design is planned to detect with stated power.
- **Practical significance:** a statistically detectable effect is not automatically important, and a practical threshold must be justified independently of the result.
- **Repeated peeking:** repeatedly applying an ordinary fixed-horizon test and stopping on significance can inflate false positives; monitored experiments need a prespecified valid procedure.
- **Synthetic data:** when historical rows lack redistribution permission, transparent synthetic generation can demonstrate methodology without implying real-user evidence or publishing restricted material.
