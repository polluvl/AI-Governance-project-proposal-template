"""Step 1 of the pipeline: send every test scenario to the AI system and save the answers.

Usage (from the repo root):
    python -m src.run_eval --config baseline            # model from .env, or mock if none set
    python -m src.run_eval --config guardrail --mock    # force the offline mock model
    python -m src.run_eval --config baseline --limit 5  # quick try on the first 5 scenarios

Answers go to results/<config>__<model>/responses.jsonl. A run can be stopped and restarted:
scenarios that already have an answer are skipped (use --fresh to start over).
"""
import argparse
import json
import re
from datetime import datetime, timezone

from src.data_io import RESULTS, corpus_as_text, load_config, load_corpus, load_scenarios, read_jsonl
from src.llm_client import make_client


def run_dir_name(config_name, model_name):
    slug = re.sub(r"[^a-zA-Z0-9.-]+", "-", model_name).strip("-")
    return f"{config_name}__{slug}"


def run(config_name, force_mock=False, limit=None, fresh=False):
    config = load_config(config_name)
    client = make_client(config, force_mock=force_mock)
    system_prompt = config["system_prompt"].replace("{corpus}", corpus_as_text(load_corpus()))

    out_dir = RESULTS / run_dir_name(config_name, client.model_name)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "responses.jsonl"
    if fresh and out_file.exists():
        out_file.unlink()
    done = {r["id"] for r in read_jsonl(out_file)}

    scenarios = load_scenarios()
    if limit:
        scenarios = scenarios[:limit]

    with out_file.open("a", encoding="utf-8") as f:
        for i, s in enumerate(scenarios, 1):
            if s["id"] in done:
                continue
            answer = client.chat(system_prompt, s["prompt"])
            record = {
                "id": s["id"],
                "layer": s["layer"],
                "technique": s["technique"],
                "prompt": s["prompt"],
                "response": answer,
                "config": config_name,
                "model": client.model_name,
            }
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
            f.flush()
            print(f"[{i}/{len(scenarios)}] {s['id']}: {answer[:70]!r}")

    info = {
        "config": config_name,
        "model": client.model_name,
        "n_scenarios": len(scenarios),
        "finished_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    (out_dir / "run_info.json").write_text(json.dumps(info, indent=2), encoding="utf-8")
    print(f"Saved answers to {out_file}")
    return out_dir


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--config", required=True, help="config name in configs/, e.g. baseline or guardrail")
    parser.add_argument("--mock", action="store_true", help="use the offline mock model")
    parser.add_argument("--limit", type=int, help="only run the first N scenarios")
    parser.add_argument("--fresh", action="store_true", help="delete previous answers of this run first")
    args = parser.parse_args()
    run(args.config, force_mock=args.mock, limit=args.limit, fresh=args.fresh)


if __name__ == "__main__":
    main()
