# ByteSpark Research Assistant

AI-powered research assistant for equity research in Automotive & Battery Materials sectors.

## Features

- **News Monitoring & Quick Reviews**: Automatically fetch and analyze news related to EV/battery supply chain
- **Data Update & Validation**: Track key metrics like lithium/cobalt/nickel prices, battery installation volumes
- **Report Generation**: Generate daily briefings, news commentary, and research reports
- **Workflow Automation**: Scheduled task execution with human-in-the-loop approval
- **Knowledge Management**: Integration with Obsidian for note-taking and ChromaDB for semantic search

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    User Interface                         │
│         Claude Code + Obsidian + Local Files             │
└───────────────────────┬─────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────┐
│                  Orchestrator Layer                       │
│       LangGraph Workflow + APScheduler Scheduler          │
└───────────────────────┬─────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────┐
│                   Skills Layer                            │
│   News Skill │ Data Skill │ Report Skill │ Review Skill  │
└───────────────────────┬─────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────┐
│                  Storage Layer                            │
│     Files │ Obsidian │ ChromaDB │ PostgreSQL/SQLite      │
└─────────────────────────────────────────────────────────┘
```

## Tech Stack

- **Python 3.11+**
- **LangGraph** - Workflow orchestration
- **APScheduler** - Task scheduling
- **SQLAlchemy** - Database ORM
- **ChromaDB** - Vector database
- **Anthropic API** - LLM integration

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

```bash
# Initialize database
python -m src.main --init-db

# Run a workflow manually
python -m src.main --workflow daily_briefing

# Start scheduled tasks
python -m src.main --start-scheduler
```

## Project Structure

```
src/
├── orchestrator/      # Workflow management (LangGraph, Scheduler)
├── db/               # Database models and repositories
├── services/         # Notification service
├── skills/           # Research skills (news, data, report, review)
├── storage/          # Storage layer (files, Obsidian, vector)
├── mcp/              # MCP connectors for data sources
└── main.py           # Entry point

tests/                # Unit and integration tests
knowledge/           # Obsidian templates
docs/                 # Design documents and specs
```

## Workflows

- **Daily Briefing**: News + data update → report → approval → archive
- **News Review**: News fetch → quick commentary → approval → archive
- **Data Update**: Batch data update → validation → archive

## License

MIT License - see LICENSE file

## Contributing

Contributions welcome! Please open an issue or submit a PR.