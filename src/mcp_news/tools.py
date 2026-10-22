"""News / market-news search via Tavily (official `tavily-python` client, run in threads)."""

import asyncio
import logging
import os
from typing import Literal

from tavily import TavilyClient

from mcp_news.server import server

logger = logging.getLogger(__name__)

_SEARCH_TIMEOUT = 30


def _failure(exc: BaseException) -> dict:
    # Type only: never echo client error text back to callers.
    return {"error": f"search failed ({type(exc).__name__})"}


@server.tool()
async def search_news(query: str,
                      topic: Literal["news", "finance"],
                      search_depth: Literal["basic", "advanced"] = "advanced") -> dict:
    """
    Description:
        This tool is used to crawl through varius reputable news sources in search for current and historical events to
        find an answer to the user's query.

    Parameters:
    query: str
        Defines the matter or event that interests the user. Should be structured in natural language
        and reflect exactly what the user wants to know.
        For better search results this parameter
        **must** be written entirely in english as it's the most optimal language for the search engine

    topic: Literal["news", "finance"]
        Controls what is the general topic of the user's query. All political, sports, history-related etc. queries should be designated as 'news'
        wheras all stock market, commodities, currencies, cryptocurrencies related queries etc. should be treated as 'finance'

    search_depth: Literal["basic", "advanced"] = "advanced"
        The level of detail that should be extracted by the search engine.
        Value 'basic' should be used when user requests a quick and short summary - should only
        be used when user clearly asks for a short anwser.
        Value 'advanced' is the default value which provides more details.

    Output:
        JSON with two result sets: `general_search` (Tavily's answer plus the matching
        articles with titles, URLs and content snippets) and `reputable source` (the same
        query restricted to Reuters for news or Bloomberg for finance).
    """
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return {"error": "News search is not configured on this server (no Tavily key)."}
    client = TavilyClient(api_key=api_key)
    logger.info("News search (%s, %s)", topic, search_depth)

    def _search(**kwargs):
        return client.search(query=query, include_answer="advanced", search_depth=search_depth,
                             timeout=_SEARCH_TIMEOUT, **kwargs)

    response, reputable = await asyncio.gather(
        asyncio.to_thread(_search, topic=topic),
        asyncio.to_thread(_search, topic="news",
                          include_domains=["reuters.com"] if topic == "news" else ["bloomberg.com"]),
        return_exceptions=True,
    )
    if isinstance(response, Exception) and isinstance(reputable, Exception):
        logger.warning("News search failed (%s)", type(response).__name__)
        return {
            "error": f"News search failed ({type(response).__name__})",
            "tip": "The search source is unavailable right now — report that instead of retrying.",
        }
    if isinstance(response, Exception):
        response = _failure(response)
    if isinstance(reputable, Exception):
        reputable = _failure(reputable)
    return {"general_search": response, "reputable source": reputable}
