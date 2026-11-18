# Agentic-AI-L300_20260718

Companion examples for the Agentic AI L300 lab. These scripts provide
standalone, easy-to-follow demonstrations of Strands Agents concepts
covered in the lab notebooks (`Task-1.ipynb`, `Task-2.ipynb`, `Task-3.ipynb`).

## Installation

```bash
git clone https://github.com/typex1/Agentic-AI-L300_20260718.git
cd Agentic-AI-L300_20260718
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
curl -LsSf https://astral.sh/uv/install.sh | sh
./1-remove-language-versions.sh
# Add to PATH for current session
export PATH="$HOME/.local/bin:$PATH"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
curl -fsSL https://cli.kiro.dev/install | bash
kiro-cli login --use-device-flow
```

## Examples

| File | Topic |
|------|-------|
| `examples/1-agent-with-web-search.py` | Minimal Strands agent with a DuckDuckGo web search tool |
| `examples/2-deploy-to-AgentCore.py` | Deploy the web search agent to AgentCore Runtime |
| `examples/2-create-test-request.py` | Invoke the deployed AgentCore Runtime endpoint |
| `examples/2-deploy-to-AgentCore.md` | Walkthrough of the deployment steps |
| `examples/3-agentcore-memory.py` | Create AgentCore Memory, store events, retrieve records |
| `examples/3-create-test-request.py` | Query an existing AgentCore Memory interactively |
| `examples/3-agentcore-memory.md` | Walkthrough of AgentCore Memory concepts |

## Dependencies

Pinned in [`requirements.txt`](requirements.txt):

| Package | Version | Used by |
|---------|---------|---------|
| `strands-agents` | 1.65.0 | all examples |
| `strands-agents-tools` | 0.9.0 | shell tool (calculator removed) |
| `ddgs` | 9.16.1 | web search tool (example 1, 2) |
| `boto3` | 1.44.5 | AWS SDK |
| `pydantic` | 2.14.3 | structured output |
| `bedrock-agentcore` | 1.26.0 | AgentCore Memory client (example 3) |
| `bedrock-agentcore-starter-toolkit` | 0.3.14 | AgentCore Runtime deployment (example 2) |
| `requests` | 2.34.2 | HTTP invocation of AgentCore endpoints |

**Not pip-installable** (installed separately via `0-install.sh`):

| Tool | How | Used by |
|------|-----|---------|
| `uv` / `uvx` | `curl -LsSf https://astral.sh/uv/install.sh \| sh` | MCP servers, strands-shell |

## Foundation Model

This environment uses **`amazon.nova-pro-v1:0`** (inference profile:
`us.amazon.nova-pro-v1:0`). See [Lab-1_permissions.md](Lab-1_permissions.md)
for the full set of allowed AWS actions.

## MCP servers configured

`.kiro/settings/mcp.json` registers two MCP servers:

- **Strands Agents** (`uvx strands-agents-mcp-server`) — access to Strands SDK documentation
- **Bedrock AgentCore** (`uvx awslabs.amazon-bedrock-agentcore-mcp-server@latest`) — AgentCore documentation
