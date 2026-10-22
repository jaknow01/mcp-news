"""The `news` MCP server instance and its tool guide."""

from jarvis_mcp_kit import ToolServer

INSTRUCTIONS = (
    "News and market-news search. Use search_news to find current or past events and "
    "summarize them from reputable sources. Write the query in English (the search engine "
    "works best in English) even if the user writes in another language, pick topic 'news' "
    "for politics/sport/history and 'finance' for markets, currencies, commodities and crypto, "
    "and use search_depth 'basic' only when the user asks for a short answer. Cite where facts "
    "come from and do not add facts the results do not contain."
)

server = ToolServer("news", title="Jarvis News", instructions=INSTRUCTIONS)
