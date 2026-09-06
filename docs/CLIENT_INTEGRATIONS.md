# Client integrations

GEO-Scope exposes a standard MCP stdio server. This works when the client can
start a local process: Codex Desktop/CLI, Claude Desktop, Cursor, Windsurf,
Antigravity and other MCP clients. The client receives the same three tools and
the provider controls described by `geo-scope providers`.

## Install once

From a checkout, use an absolute path so the client does not depend on its
working directory:

```bash
python3 -m venv .venv
.venv/bin/pip install -e .
.venv/bin/geo-scope mcp
```

Use `/absolute/path/to/geo-scope/.venv/bin/geo-scope` as the command in client
configuration. Do not put API keys in JSON configuration; set them in the
client's environment or a protected secret store.

## Claude Desktop, Cursor, Windsurf and Antigravity

These clients accept the common MCP server shape. Add this entry to the
client's MCP configuration (the file location varies by product):

```json
{
  "mcpServers": {
    "geo-scope": {
      "command": "/absolute/path/to/geo-scope/.venv/bin/geo-scope",
      "args": ["mcp"],
      "env": {
        "GEO_SCOPE_NONCOMMERCIAL": "0"
      }
    }
  }
}
```

For a no-cloud-key local run, start Ollama separately and call the tool with
`{"mode":"live","models":["ollama_local"]}`. For the user-run keyless
wrapper, start that wrapper first and call with
`{"mode":"live","models":["keyless_local"]}`. The latter remains labeled
as unverified search mediation.

## Codex

Codex can use the same stdio command when MCP servers are enabled in its local
configuration. Add `geo-scope` as an MCP server with the absolute command and
`mcp` argument above. Then ask Codex to call `audit_ai_visibility` with an
explicit `mode` and `models` list. Keep `simulate` for an offline demo and
select `live` only when the provider is configured.

## Cloud and remote clients

Cloud clients cannot launch a process on this computer. They need a deployed,
authenticated MCP HTTP endpoint. The repository currently ships the safe
stdio transport only; it does not claim a public cloud endpoint. Deploy the
container behind HTTPS and an authentication gateway, then add a thin MCP
Streamable HTTP transport that forwards to the same tool handler. Do not expose
the unauthenticated FastAPI dashboard or put provider keys in a public image.

The current Docker dashboard is useful for a private network or local server:

```bash
docker compose up --build
```

It is not, by itself, a Cloud MCP server. A cloud deployment must also define
authentication, request limits, tenant isolation, secret injection, and a
publicly reachable MCP transport before it is advertised to other users.

## Smoke test

The stdio protocol can be checked without a provider or network call:

```bash
printf '%s\n' \
  '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' \
  '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}' \
  | /absolute/path/to/geo-scope/.venv/bin/geo-scope mcp
```

The response must contain `serverInfo.name` equal to `geo-scope-mcp` and the
three tool names. A tools/list response proves protocol compatibility, not
that any cloud provider key or web search is available.
