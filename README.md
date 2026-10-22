# mcp-news

News and market-news search (Tavily) as an [MCP](https://modelcontextprotocol.io) server.

| Tool | What it does |
|---|---|
| `search_news` | Tavily search with an answer, plus the same query on a reputable source (Reuters for news, Bloomberg for finance) |
| `whoami` | which client your key belongs to |

Needs `TAVILY_API_KEY`. Uses the official `tavily-python` client.

Part of the Jarvis tool servers; built on
[jarvis-mcp-kit](https://github.com/jaknow01/jarvis-mcp-kit) (API keys, rate limits, logs).

## Run

```bash
cp .env.example .env                              # set TAVILY_API_KEY
cp config/clients.example.yaml config/clients.yaml
uv run jarvis-mcp-keys new me --servers news      # paste the block into config/clients.yaml
uv run --env-file .env mcp-news serve             # http://localhost:8010/mcp/news
```

Docker: `docker run -p 8010:8010 --env-file .env -v $PWD/config:/config ghcr.io/jaknow01/mcp-news:latest`.
Kubernetes: `deploy/kubernetes.yaml`.

## Connect

- **Claude Code:** `claude mcp add --transport http news https://<host>/mcp/news --header "Authorization: Bearer jvk_…"`
- **Claude app (custom connector):** URL `https://<host>/mcp/news/jvk_…`
- **Jarvis:** an entry in its `config/subagents.yaml`.
