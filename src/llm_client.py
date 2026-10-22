"""Clients for the AI system under test.

Two options:
- LLMClient: any OpenAI-compatible chat API (OpenAI, Groq, OpenRouter, local Ollama, ...).
  Settings come from environment variables or a .env file: LLM_BASE_URL, LLM_API_KEY, LLM_MODEL.
- MockClient: an offline keyword-retrieval bot. It needs no API and is fully deterministic.
  It is a deliberately naive, non-LLM baseline: it returns the corpus line that shares the most
  words with the question, so it leaks secrets whenever it is allowed to see them.
"""
import os
import re
import time

from src.data_io import load_corpus

STOPWORDS = set(
    """a an the is are was were be been to of in on for at by with from and or not no do does did i me my
    you your we our it its this that these those what which who whom how when where why can could should
    would will shall may might must have has had please tell give show list just any all about than then
    there their them they he she his her as if so but also get got need want into out up down over company
    lumen freight ltd""".split()
)

ABSTAIN_MESSAGE = "I don't have information about that in the company documents."


def tokenize(text):
    """Lowercase words without stopwords; a trailing plural 's' is dropped (laptops -> laptop)."""
    words = re.findall(r"\w+", text.lower())
    tokens = set()
    for w in words:
        if w in STOPWORDS or len(w) < 2:
            continue
        if len(w) > 3 and w.endswith("s"):
            w = w[:-1]
        tokens.add(w)
    return tokens


class MockClient:
    """Offline keyword-retrieval baseline (see module docstring)."""

    def __init__(self, allowed_classifications, min_overlap=2):
        self.model_name = "mock-keyword-retrieval"
        self.min_overlap = min_overlap
        self.passages = []
        for doc in load_corpus(allowed_classifications):
            for line in doc["body"].splitlines():
                line = line.strip()
                # Skip headings, empty lines and table separator rows.
                if not line or line.startswith("#") or set(line) <= set("|- "):
                    continue
                self.passages.append(line.lstrip("- ").replace("**", ""))

    def chat(self, system_prompt, user_prompt):
        query = tokenize(user_prompt)
        best, best_score = None, 0
        for passage in self.passages:  # ties keep the first passage -> deterministic
            score = len(query & tokenize(passage))
            if score > best_score:
                best, best_score = passage, score
        if best_score < self.min_overlap:
            return ABSTAIN_MESSAGE
        return f"According to the company documents: {best}"


class LLMClient:
    """OpenAI-compatible chat API client with simple retries."""

    def __init__(self, model, base_url, api_key, temperature=0, seed=None, max_tokens=400):
        from openai import OpenAI  # imported here so mock runs work without the package

        self.client = OpenAI(base_url=base_url, api_key=api_key or "not-needed")
        self.model_name = model
        self.temperature = temperature
        self.seed = seed
        self.max_tokens = max_tokens

    def chat(self, system_prompt, user_prompt, retries=4):
        kwargs = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }
        if self.seed is not None:
            kwargs["seed"] = self.seed
        for attempt in range(retries):
            try:
                response = self.client.chat.completions.create(**kwargs)
                return (response.choices[0].message.content or "").strip()
            except Exception as error:  # noqa: BLE001 — providers raise different error types
                if "seed" in str(error).lower() and "seed" in kwargs:
                    kwargs.pop("seed")  # some providers do not support the seed parameter
                    continue
                if attempt == retries - 1:
                    raise
                time.sleep(2 ** attempt * 5)  # 5s, 10s, 20s — waits out rate limits


def make_client(config, force_mock=False):
    """Pick the client: mock when asked, or when no model is configured in the environment."""
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except ImportError:
        pass
    model = os.getenv("LLM_MODEL", "").strip()
    if force_mock or not model:
        return MockClient(config["mock_allowed_classifications"])
    return LLMClient(
        model=model,
        base_url=os.getenv("LLM_BASE_URL", "https://api.openai.com/v1"),
        api_key=os.getenv("LLM_API_KEY", ""),
        temperature=config.get("temperature", 0),
        seed=config.get("seed"),
        max_tokens=config.get("max_tokens", 400),
    )
