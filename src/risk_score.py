"""Step 3 of the pipeline: turn metrics into risk levels and a deployment recommendation.

Usage:
    python -m src.risk_score --run results/baseline__mock-keyword-retrieval

Reads <run>/metrics.json and configs/thresholds.json, writes <run>/risk_report.json and
<run>/risk_report.md (the governance report a decision-maker reads).

The aggregation is deliberately transparent: every metric gets a level from a fixed threshold,
and the overall level is the WORST level of any risk (one High risk is enough to block deployment).
"""
import argparse
import json
from pathlib import Path

from src.data_io import CONFIGS

LEVELS = ["Low", "Medium", "High"]


def load_thresholds():
    return json.loads((CONFIGS / "thresholds.json").read_text(encoding="utf-8"))


def level_for(value, rule):
    """Map one metric value to Low / Medium / High using the rule's thresholds."""
    if value is None:
        return None
    if rule["direction"] == "lower_is_better":
        if value <= rule["low_max"]:
            return "Low"
        return "Medium" if value <= rule["medium_max"] else "High"
    if value >= rule["low_min"]:
        return "Low"
    return "Medium" if value >= rule["medium_min"] else "High"


def worst(levels):
    levels = [lv for lv in levels if lv]
    return max(levels, key=LEVELS.index) if levels else None


def assess(metrics, thresholds):
    risks = []
    for rule in thresholds["metrics"]:
        layer = metrics["layers"].get(rule["layer"])
        if layer is None:
            continue  # this layer was not run
        value = layer.get(rule["metric"])
        level = level_for(value, rule)
        if level is None:
            continue  # metric not available in this run
        notes = []
        unresolved = layer.get("needs_label", 0)
        if unresolved:
            floor = thresholds["unresolved_review"]["min_severity"]
            if LEVELS.index(level) < LEVELS.index(floor):
                level = floor
            notes.append(f"{unresolved} answer(s) need human review")
        risks.append({
            "risk": rule["risk"],
            "layer": rule["layer"],
            "metric": rule["metric"],
            "value": value,
            "level": level,
            "framework": rule["framework"],
            "controls": rule["controls"] if level != "Low" else [],
            "notes": notes,
        })

    overall = worst(r["level"] for r in risks)
    decision = thresholds["decisions"][overall]
    return {
        "run": metrics.get("run"),
        "model": metrics.get("model"),
        "config": metrics.get("config"),
        "overall_risk": overall,
        "recommendation": decision["recommendation"],
        "approval": decision["approval"],
        "human_review": decision["human_review"],
        "risks": risks,
        "not_yet_assessed": thresholds["not_yet_assessed"],
    }


def to_markdown(report):
    marks = {"Low": "OK", "Medium": "WARNING", "High": "FAIL"}
    lines = [
        f"# Governance report: {report['config']} / {report['model']}",
        "",
        f"**Overall risk: {report['overall_risk']}**",
        "",
        f"**Recommendation: {report['recommendation']}.**",
        "",
        "| Risk | Metric | Value | Level |",
        "| --- | --- | --- | --- |",
    ]
    for r in report["risks"]:
        note = f" ({'; '.join(r['notes'])})" if r["notes"] else ""
        lines.append(f"| {r['risk']} | {r['metric']} | {r['value']} | [{marks[r['level']]}] {r['level']}{note} |")
    controls = [(r["risk"], c) for r in report["risks"] for c in r["controls"]]
    if controls:
        lines += ["", "## Required controls", ""]
        lines += [f"- **{risk}:** {control}" for risk, control in controls]
    lines += [
        "",
        "## Approval and oversight",
        "",
        f"- Who approves: {report['approval']}",
        f"- Human review: {report['human_review']}",
        "",
        "## Not yet assessed",
        "",
        "This recommendation is provisional: the following risks were not tested in this run.",
        "",
    ]
    lines += [f"- {item}" for item in report["not_yet_assessed"]]
    lines += ["", "## Framework mapping", ""]
    lines += [f"- {r['risk']}: {r['framework']}" for r in report["risks"]]
    return "\n".join(lines) + "\n"


def run(run_dir):
    run_dir = Path(run_dir)
    metrics = json.loads((run_dir / "metrics.json").read_text(encoding="utf-8"))
    report = assess(metrics, load_thresholds())
    (run_dir / "risk_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    (run_dir / "risk_report.md").write_text(to_markdown(report), encoding="utf-8")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--run", required=True, help="run folder that already has metrics.json")
    args = parser.parse_args()
    report = run(args.run)
    print(f"Overall risk: {report['overall_risk']} -> {report['recommendation']}")


if __name__ == "__main__":
    main()
