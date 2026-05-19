# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`interview-agent` is a learning-driven AI Agent project for studying AI Agent development through building. It uses LangGraph's ReAct pattern and MiniMax API (Claude-compatible).

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/ -v

# Run single test
pytest tests/test_agent.py -v

# Start Agent (requires API key in .env)
python src/main.py

# Format code
black src/ tests/
```

## Architecture

### Core: ReAct Workflow

```
User Input → Reason Node → [Need info?] → Act Node → Tools
                                      ↓
                                    No → Response
```

- `src/agent/agent.py` - InterviewAgent with `_build_graph()`, `reason_node()`, `act_node()`
- `AgentState` (TypedDict) - `messages` (Annotated with `operator.add`), `next_action`

### Tool System

Tools in `src/agent/tools/` are classes with methods decorated by `@tool`. Currently:
- `SearchTool.search_hacker_news()` - HN Algolia API
- `SearchTool.search_reddit()` - Reddit JSON API

### Configuration

- `src/config/settings.py` - API keys, endpoints via `python-dotenv`
- `.env` file required (copy from `.env.example`)

### Dependencies

- **LangGraph** >=0.0.20 - Agent orchestration
- **LangChain** >=0.1.0 - LLM abstractions
- **langchain-anthropic** - MiniMax/Claude compatibility layer
- **Chromadb** - Vector DB (memory system, planned)
- **BeautifulSoup** - Web scraping (planned)

## Key Files

| File | Purpose |
|------|---------|
| `src/main.py` | Entry point, LLM init, agent setup |
| `src/agent/agent.py` | ReAct state machine (reason→act loop) |
| `src/agent/tools/search.py` | Search tool implementations |
| `src/config/settings.py` | API config, proxy settings |

## State Management

State uses LangGraph's `operator.add` for message accumulation - each node returns updates that merge with existing state, allowing the reason→act loop to accumulate context.