# Results summary

Model: claude-haiku-5-5

| Metric | baseline | guardrail |
| --- | --- | --- |
| Leak rate (lower is better) | 11% | 0% |
| Refusal rate on attacks | 93% | 100% |
| Correct "I don't know" / correction rate | 85% | 100% |
| Accuracy on normal questions | 100% | 100% |
| Over-refusal rate (lower is better) | 0% | 0% |
| **Overall risk** | High | Low |
| **Recommendation** | Do not deploy | Deploy |

Per-run details: `results/<run>/risk_report.md`, `metrics.json`, `scored.csv`.
