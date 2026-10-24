# Governance report: baseline / claude-haiku-5-5

**Overall risk: High**

**Recommendation: Do not deploy.**

| Risk | Metric | Value | Level |
| --- | --- | --- | --- |
| Sensitive data exposure | leak_rate | 0.111 | [FAIL] High |
| Hallucination / out-of-scope answers | correct_abstention_rate | 0.846 | [WARNING] Medium |
| Low answer accuracy | accuracy | 1.0 | [OK] Low |
| Over-refusal (assistant too cautious to be useful) | over_refusal_rate | 0.0 | [OK] Low |

## Required controls

- **Sensitive data exposure:** Document-level access control in retrieval: users only get documents they are cleared for
- **Sensitive data exposure:** Output filter that blocks secrets and personal data (regex / NER) before the answer is shown
- **Sensitive data exposure:** Remove credentials and personal contacts from the assistant's knowledge base
- **Hallucination / out-of-scope answers:** Grounding check: only answer when the retrieved documents support the answer
- **Hallucination / out-of-scope answers:** Show the source document with every answer
- **Hallucination / out-of-scope answers:** Standard fallback message that points to HR or the IT Service Desk

## Approval and oversight

- Who approves: Deployment blocked until the High risks are fixed and re-tested; exception only by the AI governance board / CISO
- Human review: Mandatory re-assessment after fixes

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
