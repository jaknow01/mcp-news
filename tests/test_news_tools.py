"""search_news with the Tavily client mocked (no network)."""

import asyncio
import json

import pytest

from conftest import call_tools, text_of
from mcp_news import tools


class _Client:
    calls: list = []
    fail: set = set()

    def __init__(self, api_key):
        assert api_key == "test"

    def search(self, **kwargs):
        _Client.calls.append(kwargs)
        domains = kwargs.get("include_domains")
        if ("reputable" if domains else "general") in _Client.fail:
            raise RuntimeError("401 for key tvly-SECRET")
        return {"answer": "A", "results": [{"title": "T", "url": "https://x"}], "domains": domains}


@pytest.fixture
def tavily(monkeypatch):
    _Client.calls, _Client.fail = [], set()
    monkeypatch.setenv("TAVILY_API_KEY", "test")
    monkeypatch.setattr(tools, "TavilyClient", _Client)
    return _Client


def test_two_searches_general_and_reputable(tavily):
    out = asyncio.run(tools.search_news("ECB rate decision", "finance"))
    assert out["general_search"]["answer"] == "A"
    assert out["reputable source"]["domains"] == ["bloomberg.com"]
    assert {c["topic"] for c in tavily.calls} == {"finance", "news"}
    assert all(c["search_depth"] == "advanced" and c["timeout"] == 30 for c in tavily.calls)


def test_news_topic_uses_reuters(tavily):
    out = asyncio.run(tools.search_news("election", "news", "basic"))
    assert out["reputable source"]["domains"] == ["reuters.com"]


def test_partial_failure_keeps_the_other_result_without_leaking(tavily):
    tavily.fail = {"reputable"}
    out = asyncio.run(tools.search_news("x", "news"))
    assert out["general_search"]["answer"] == "A"
    assert out["reputable source"] == {"error": "search failed (RuntimeError)"}
    assert "SECRET" not in json.dumps(out)


def test_total_failure(tavily):
    tavily.fail = {"general", "reputable"}
    out = asyncio.run(tools.search_news("x", "news"))
    assert "unavailable" in out["tip"] and "SECRET" not in json.dumps(out)


def test_not_configured(monkeypatch):
    monkeypatch.delenv("TAVILY_API_KEY", raising=False)
    assert "not configured" in asyncio.run(tools.search_news("x", "news"))["error"]


def test_over_mcp(app, keys, tavily):
    (result,) = call_tools(app, keys["friend"], [("search_news", {"query": "x", "topic": "news"})])
    assert not result.is_error and "general_search" in text_of(result)
