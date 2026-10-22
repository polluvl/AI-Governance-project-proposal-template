# AI Governance & Assurance

A practical technical framework for checking whether an AI system is safe enough to deploy.
UCU course "Штучний інтелект", semester project 2026.

**Team:** Лукашенко Поліна, Мандрик Софія, Онопрієнко Дарина · **Mentor:** Шумський Дмитро

## Problem

Organisations deploy LLM assistants on internal documents, but governance frameworks (NIST AI RMF, ISO/IEC 42001,
EU AI Act) say *what* to control, not *how to measure it*. We build a reproducible pipeline that turns test
results into measurable risks, risk levels and a deployment recommendation.

**Input:** an AI system (model + system prompt + documents) and a set of test scenarios.
**Output:** a governance report: risks found, a metric per risk, overall risk level, required controls, who approves,
and a recommendation: *deploy* / *deploy with restrictions* / *do not deploy*.

## How it works

```
data/scenarios.jsonl ──► src/run_eval.py ──► src/metrics.py ──► src/risk_score.py ──► risk_report.md
   (70 test prompts)     (ask the model)    (score answers)    (thresholds → levels)   (recommendation)
                                    configs/baseline.json        configs/thresholds.json
                                    configs/guardrail.json       docs/taxonomy.md
```

| Folder | What is inside |
|---|---|
| `data/` | Synthetic company documents, 14 planted "canary" secrets, 70 test scenarios — see [data/README.md](data/README.md) |
| `configs/` | The two system setups we compare, and the risk thresholds |
| `src/` | The pipeline (one file per step) |
| `docs/taxonomy.md` | Risk → Test → Metric → Threshold → Control table with NIST mapping |
| `results/` | Answers, scores and governance reports of each run |
| `tests/` | Unit tests (`python -m pytest -q`) |
| `docs/proposal/` | LaTeX source of our proposal |

**Use case 1:** an internal employee assistant for a fictional company. Its context contains all documents,
including Confidential and Restricted ones (a RAG deployment without access control). We test two setups:

- **baseline**: "answer from the documents", no protection;
- **guardrail**: the same plus a safety system prompt (access rules, "I don't know" when unsure, premise checking).

**Risk layers measured now:** privacy leakage (27 attack prompts), out-of-scope / hallucination (26),
plus 17 normal questions that check the assistant is still useful. Jailbreak judging, bias and transparency
come next (see [docs/taxonomy.md](docs/taxonomy.md)).

## How to run

```bash
pip install -r requirements.txt
python -m src.pipeline --mock      # offline, no API key needed — reproduces the mock numbers below
```

To test a real LLM: copy `.env.example` to `.env`, fill in `LLM_BASE_URL`, `LLM_API_KEY`, `LLM_MODEL`
(any OpenAI-compatible API, or local Ollama), then run `python -m src.pipeline`.
Results go to `results/summary.md` and `results/<config>__<model>/risk_report.md`.

Single steps: `python -m src.run_eval --config baseline`, `python -m src.metrics --run <folder>`,
`python -m src.risk_score --run <folder>`, `python -m src.label --run <folder>` (human labelling).
Dataset check: `python data/validate_dataset.py`.

## Results

Offline mock model (a keyword-retrieval bot, no LLM; deterministic). It sets the floor any LLM must beat:

| Metric | baseline | guardrail |
|---|---|---|
| Leak rate (lower is better) | 37% | 0% |
| Refusal rate on attacks | 33% | 78% |
| Correct "I don't know" / correction rate | 73% | 73% |
| Accuracy on normal questions | 76% | 76% |
| Over-refusal rate | 12% | 12% |
| **Overall risk** | High | Medium |
| **Recommendation** | Do not deploy | Deploy with restrictions |

LLM results: _to be added after the first real run._

## Limitations

- One use case, 70 scenarios: results are indicative, not statistically strong.
- Automatic checks are heuristics (regex, keyword lists). They miss paraphrased and encoded leaks; human labels
  (`results/<run>/labels.csv`) override them. Measuring how reliable the checks are (Cohen's κ) is planned.
- Thresholds reflect our judgement for this use case; another organisation should set its own.

## AI usage

- **Claude (Anthropic)** was used to draft the synthetic dataset, the pipeline code, tests, the taxonomy text
  and this README.
- **How we checked it:** we ran the pipeline and tests ourselves, read every file, edited what we disagreed with,
  verified the NIST AI RMF subcategory numbers against the framework, and labelled uncertain answers by hand.
  Each of us can explain the parts we committed.
- The tool is also visible in commit messages ("drafted with Claude").

## Contribution statement

| Member | Share | Responsibilities |
|---|---|---|
| Лукашенко Поліна | 33.3% | Evaluation pipeline (`src/run_eval.py`, `src/llm_client.py`, `src/metrics.py`), repo setup, tests, reproducibility |
| Мандрик Софія | 33.3% | Risk taxonomy and thresholds (`docs/taxonomy.md`, `configs/thresholds.json`), risk scoring and governance report (`src/risk_score.py`, `src/pipeline.py`), README |
| Онопрієнко Дарина | 33.3% | Literature review, evaluation dataset (`data/`), human labelling (`src/label.py`), final report |

All three members agree with this distribution.
