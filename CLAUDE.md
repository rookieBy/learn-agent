# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`interview-agent` is a learning-driven AI Agent project for studying AI Agent development through building. It uses LangGraph's ReAct pattern (Reasoning + Acting) with MiniMax API (Claude-compatible).

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Copy and configure environment (required before first run)
cp .env.example .env
# Edit .env with your API keys

# Run all tests
pytest tests/ -v

# Run single test
pytest tests/test_agent.py -v

# Run with coverage
pytest --cov=src --cov-report=term-missing

# Start Agent (requires API key in .env)
python src/main.py

# Format code
black src/ tests/
```

## Architecture

### Core: ReAct State Machine

```
User Input → reason_node → [needs tool?] → act_node → Tools
                                    ↓
                                  No → Final Response
```

- `src/agent/agent.py` - `InterviewAgent` with `_build_graph()`, `reason_node()`, `act_node()`
- `AgentState` (TypedDict) - `messages` (Annotated with `operator.add` for accumulation), `next_action`
- The graph uses conditional edges: if "ACTION:" in response → continue to act, otherwise → END

### Tool System

Tools in `src/agent/tools/` are classes with methods decorated by `@tool`:
- `SearchTool.search_hacker_news()` - HN Algolia API
- `SearchTool.search_reddit()` - Reddit JSON API
- `SearchTool.search_all()` - Combined search

### State Accumulation

LangGraph's `operator.add` merges message lists - each node returns updates that concatenate with existing state, enabling the reason→act loop to accumulate context across iterations.

### Prompt Templates

`src/agent/prompts/agent_prompts.py` contains:
- `REACT_SYSTEM_PROMPT` - Main system prompt for the agent
- `SEARCH_PROMPT` - Template for search operations
- `ANALYZE_PROMPT` - Template for analyzing interview questions

### Configuration

- `src/config/settings.py` - API keys, endpoints via `python-dotenv`
- `.env` file required (copy from `.env.example`)
- Loguru configured in `src/main.py` → `logs/agent_{time}.log`

### Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| langgraph | >=0.0.20 | Agent orchestration |
| langchain | >=0.1.0 | LLM abstractions |
| langchain-anthropic | >=0.1.0 | MiniMax/Claude compatibility |
| chromadb | >=0.4.0 | Vector DB (planned for memory) |
| beautifulsoup4 | >=4.12.0 | Web scraping (planned) |
| loguru | >=0.7.0 | Logging |
| pytest | >=7.4.0 | Testing |

## Key Files

| File | Purpose |
|------|---------|
| `src/main.py` | Entry point, LLM init, agent setup, interactive loop |
| `src/agent/agent.py` | ReAct state machine (reason→act loop) |
| `src/agent/tools/search.py` | Search tool implementations |
| `src/agent/prompts/agent_prompts.py` | Prompt templates |
| `src/config/settings.py` | API config, proxy settings |

## Development Notes

- `src/agent/memory/` exists but is planned (not yet implemented)
- The agent uses `recursion_limit=10` in `graph.invoke()` to prevent infinite loops
- LLM parsing relies on structured output format: `ACTION: toolname\nINPUT: query` or `RESPONSE: answer`