# Governance report: guardrail / claude-haiku-5-5

**Overall risk: Low**

**Recommendation: Deploy.**

| Risk | Metric | Value | Level |
| --- | --- | --- | --- |
| Sensitive data exposure | leak_rate | 0.0 | [OK] Low |
| Hallucination / out-of-scope answers | correct_abstention_rate | 1.0 | [OK] Low |
| Low answer accuracy | accuracy | 1.0 | [OK] Low |
| Over-refusal (assistant too cautious to be useful) | over_refusal_rate | 0.0 | [OK] Low |

## Approval and oversight

- Who approves: System owner
- Human review: Regular monitoring; re-test after every model or knowledge-base change

## Not yet assessed

This recommendation is provisional: the following risks were not tested in this run.

- Jailbreak / harmful output (layer 1, LLM-judge)
- Bias and discrimination (layer 4)
- Transparency / uncertainty communication (layer 5)

## Framework mapping

- Sensitive data exposure: NIST AI RMF MEASURE 2.10 (privacy), 2.7 (security); NIST AI 600-1: Data Privacy, Information Security
- Hallucination / out-of-scope answers: NIST AI RMF MEASURE 2.5 (validity), 2.6 (safe failure beyond knowledge limits); NIST AI 600-1: Confabulation
- Low answer accuracy: NIST AI RMF MEASURE 2.5 (valid and reliable); NIST AI 600-1: Human-AI Configuration
- Over-refusal (assistant too cautious to be useful): NIST AI RMF MEASURE 2.5 (valid and reliable)
