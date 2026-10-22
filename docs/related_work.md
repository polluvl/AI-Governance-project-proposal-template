# Related work: what exists and what is missing

Short review for the midterm ("how is this problem solved in the world?"). Numbers in brackets refer to the
proposal's reference list.

## Governance frameworks: they say *what* to control

| Source | What it gives | What is missing for a deployment decision |
|---|---|---|
| NIST AI RMF 1.0 [1] | Four functions (Govern, Map, Measure, Manage); MEASURE 2.x lists what to evaluate (validity, safety, security, privacy, fairness...) | No concrete tests, metrics or thresholds; each organisation must build them |
| NIST AI 600-1, Generative AI Profile [4] | Risks specific to generative AI (confabulation, data privacy, information security, harmful bias...) and suggested actions | Same: actions, not a measuring tool |
| ISO/IEC 42001:2023 [2] | Certifiable AI management system with Annex A controls | Process and documentation focus; no technical test suite |
| EU AI Act, Regulation 2024/1689 [3] | Legally binding, risk-based classification and obligations | Says which obligations apply, not how to test a specific assistant |

## Evaluation tools: they *measure*, but do not decide

| Tool | What it does | Limitation for governance |
|---|---|---|
| garak (NVIDIA) [6] | LLM vulnerability scanner: many attack probes (jailbreaks, prompt injection, leakage) | Produces attack results, no link to governance controls or a deploy / don't-deploy decision |
| DeepEval [7] | pytest-style LLM evaluation with metrics (G-Eval, hallucination) and red-teaming | Generic metrics; thresholds and their meaning are left to the user |
| Ragas [8] | RAG metrics (faithfulness, answer relevancy) and test-set generation | Quality of RAG answers only; no privacy or access-control view |
| AIR-Bench 2024 [9] | Safety benchmark with risk categories derived from regulations and company policies | Benchmarks models in general, not one organisation's deployment |
| TrustLLM [10] | Six dimensions of LLM trustworthiness, benchmark across models | Same: model-level, not deployment-level |

## The closest work

UNICC & EPFL, *Safety evaluation of an institutional LLM-RAG deployment* [5]: a four-layer audit
(jailbreak, out-of-scope refusal, hallucination, sycophancy) of a real institutional RAG system, with an open
pipeline and LLM-judge validation against human labels. It shows the approach works for one deployment.

## Our niche

We connect the two worlds: **test → metric → threshold → governance control → who approves**, in one
transparent, reproducible pipeline.

- Unlike the frameworks, we give concrete tests and numbers.
- Unlike the tools, every metric ends in a decision (deploy / with restrictions / do not deploy) and a list of
  required controls mapped to NIST AI RMF.
- Unlike [5], our taxonomy adds privacy / access control, bias and transparency layers, and is meant to be
  reused across different use cases.

_To do before the final report: re-read [5] and each tool's documentation and confirm every statement above._
