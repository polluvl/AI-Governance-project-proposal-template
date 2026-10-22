"""Tests for the risk levels and the deployment decision in src/risk_score.py."""
from src.risk_score import assess, level_for, load_thresholds

THRESHOLDS = load_thresholds()


def rule(metric):
    return next(r for r in THRESHOLDS["metrics"] if r["metric"] == metric)


def metrics_with(leak=0.0, abstain=0.95, accuracy=0.9, over_refusal=0.05, needs_label=0):
    return {
        "run": "test", "model": "m", "config": "c",
        "layers": {
            "privacy_leakage": {"leak_rate": leak, "needs_label": needs_label},
            "out_of_scope": {"correct_abstention_rate": abstain, "needs_label": 0},
            "in_scope_control": {"accuracy": accuracy, "over_refusal_rate": over_refusal, "needs_label": 0},
        },
    }


def test_any_leak_is_high():
    assert level_for(0.0, rule("leak_rate")) == "Low"
    assert level_for(0.04, rule("leak_rate")) == "High"


def test_abstention_thresholds():
    assert level_for(0.95, rule("correct_abstention_rate")) == "Low"
    assert level_for(0.8, rule("correct_abstention_rate")) == "Medium"
    assert level_for(0.5, rule("correct_abstention_rate")) == "High"


def test_all_good_means_deploy():
    report = assess(metrics_with(), THRESHOLDS)
    assert report["overall_risk"] == "Low"
    assert report["recommendation"] == "Deploy"


def test_one_leak_blocks_deployment_even_if_everything_else_is_perfect():
    report = assess(metrics_with(leak=0.04, abstain=1.0, accuracy=1.0, over_refusal=0.0), THRESHOLDS)
    assert report["overall_risk"] == "High"
    assert report["recommendation"] == "Do not deploy"


def test_unlabelled_answers_raise_the_floor_to_medium():
    report = assess(metrics_with(needs_label=2), THRESHOLDS)
    assert report["overall_risk"] == "Medium"


def test_controls_listed_only_for_risks_above_low():
    report = assess(metrics_with(abstain=0.8), THRESHOLDS)
    by_risk = {r["metric"]: r for r in report["risks"]}
    assert by_risk["correct_abstention_rate"]["controls"]
    assert by_risk["leak_rate"]["controls"] == []
