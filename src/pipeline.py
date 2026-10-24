"""One command that reproduces all results: answers -> metrics -> risk report -> comparison table.

Usage (from the repo root):
    python -m src.pipeline            # model from .env (or the offline mock if none is set)
    python -m src.pipeline --mock     # always use the offline mock model (no API key needed)
    python -m src.pipeline --rescore  # no model calls: recompute from saved answers + human labels

Runs every config (baseline, guardrail) and writes results/summary.md.
"""
import argparse

from src import metrics, risk_score, run_eval
from src.data_io import RESULTS

CONFIGS = ["baseline", "guardrail"]

ROWS = [
    ("privacy_leakage", "leak_rate", "Leak rate (lower is better)"),
    ("privacy_leakage", "refusal_rate", "Refusal rate on attacks"),
    ("out_of_scope", "correct_abstention_rate", "Correct \"I don't know\" / correction rate"),
    ("in_scope_control", "accuracy", "Accuracy on normal questions"),
    ("in_scope_control", "over_refusal_rate", "Over-refusal rate (lower is better)"),
]


def find_saved_run(config, mock):
    """The saved results folder of a config (real-model run by default, mock run with --mock)."""
    folders = [d for d in sorted(RESULTS.glob(f"{config}__*"))
               if (d / "responses.jsonl").exists() and ("mock-keyword-retrieval" in d.name) == mock]
    if len(folders) != 1:
        raise SystemExit(f"Expected exactly one saved run for '{config}' in results/, found: {[d.name for d in folders]}")
    return folders[0]


def fmt(value):
    return "–" if value is None else f"{value:.0%}"


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--mock", action="store_true", help="use the offline mock model")
    parser.add_argument("--fresh", action="store_true", help="ask the model again instead of reusing saved answers")
    parser.add_argument("--rescore", action="store_true",
                        help="no model calls: recompute metrics and reports from saved answers (e.g. after labelling)")
    args = parser.parse_args()

    results = []
    for config in CONFIGS:
        if args.rescore:
            run_dir = find_saved_run(config, args.mock)
        else:
            run_dir = run_eval.run(config, force_mock=args.mock, fresh=args.fresh)
        m = metrics.compute(run_dir)
        metrics.print_summary(m)
        report = risk_score.run(run_dir)
        print(f"  -> overall risk {report['overall_risk']}: {report['recommendation']}")
        results.append((config, m, report))

    lines = [
        "# Results summary",
        "",
        f"Model: {results[0][1]['model']}",
        "",
        "| Metric | " + " | ".join(c for c, _, _ in results) + " |",
        "| --- |" + " --- |" * len(results),
    ]
    for layer, key, label in ROWS:
        cells = [fmt(m["layers"].get(layer, {}).get(key)) for _, m, _ in results]
        lines.append(f"| {label} | " + " | ".join(cells) + " |")
    lines.append("| **Overall risk** | " + " | ".join(r["overall_risk"] for _, _, r in results) + " |")
    lines.append("| **Recommendation** | " + " | ".join(r["recommendation"] for _, _, r in results) + " |")
    lines += ["", "Per-run details: `results/<run>/risk_report.md`, `metrics.json`, `scored.csv`."]

    summary = RESULTS / "summary.md"
    summary.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nWrote {summary}")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
