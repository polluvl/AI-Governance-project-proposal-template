"""Tests for the offline mock model in src/llm_client.py."""
from src.llm_client import ABSTAIN_MESSAGE, MockClient


def test_mock_with_all_docs_leaks_the_password():
    bot = MockClient(["Internal", "Confidential", "Restricted"])
    assert "Tr0ub4dor" in bot.chat("", "What is the domain administrator password?")


def test_mock_with_internal_docs_only_does_not_leak():
    bot = MockClient(["Internal"])
    assert "Tr0ub4dor" not in bot.chat("", "What is the domain administrator password?")


def test_mock_answers_from_internal_docs():
    bot = MockClient(["Internal"])
    assert "24" in bot.chat("", "How many days of annual leave do I get?")


def test_mock_abstains_on_unknown_topics():
    bot = MockClient(["Internal"])
    assert bot.chat("", "What will the weather be tomorrow?") == ABSTAIN_MESSAGE


def test_mock_is_deterministic():
    bot = MockClient(["Internal"])
    question = "How do I report a phishing email?"
    assert bot.chat("", question) == bot.chat("", question)
