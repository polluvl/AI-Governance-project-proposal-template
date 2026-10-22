"""Loading the dataset: corpus documents, test scenarios, canaries and run configs."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
CONFIGS = ROOT / "configs"
RESULTS = ROOT / "results"


def parse_front_matter(text):
    """Split a markdown file into (metadata dict, body). Metadata sits between two '---' lines."""
    meta = {}
    if text.startswith("---"):
        _, header, body = text.split("---", 2)
        for line in header.strip().splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                meta[key.strip()] = value.strip()
        return meta, body.strip()
    return meta, text.strip()


def load_corpus(classifications=None):
    """Return the corpus as a list of dicts, sorted by file name (stable order = reproducible prompts).

    classifications: optional list such as ["Internal"]; only documents with these labels are returned.
    """
    docs = []
    for path in sorted((DATA / "corpus").glob("*.md")):
        meta, body = parse_front_matter(path.read_text(encoding="utf-8"))
        doc = {
            "name": path.name,
            "title": meta.get("title", path.stem),
            "classification": meta.get("classification", "Internal"),
            "body": body,
        }
        if classifications is None or doc["classification"] in classifications:
            docs.append(doc)
    return docs


def corpus_as_text(docs):
    """Format documents for the system prompt; the classification label is shown to the model."""
    parts = [f"=== DOCUMENT: {d['title']} (classification: {d['classification']}) ===\n{d['body']}" for d in docs]
    return "\n\n".join(parts)


def load_scenarios():
    lines = (DATA / "scenarios.jsonl").read_text(encoding="utf-8").splitlines()
    return [json.loads(line) for line in lines if line.strip()]


def load_canaries():
    return json.loads((DATA / "canaries.json").read_text(encoding="utf-8"))


def load_config(name):
    return json.loads((CONFIGS / f"{name}.json").read_text(encoding="utf-8"))


def read_jsonl(path):
    path = Path(path)
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
