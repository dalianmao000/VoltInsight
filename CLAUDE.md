# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ByteSpark Research Assistant is an AI-powered system for equity research in Automotive & Battery Materials sectors. It uses a multi-layer architecture with LangGraph workflow orchestration and scheduled task execution.

## Common Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/ -v

# Run specific test file
pytest tests/test_orchestrator.py -v

# Initialize database
python -m src.main --init-db

# Run a workflow manually
python -m src.main --workflow daily_briefing
python -m src.main --workflow news_review
python -m src.main --workflow data_update

# Start scheduled task scheduler
python -m src.main --start-scheduler
```

## Architecture

### Layer Structure

```
User Interface (Claude Code + Obsidian + Local Files)
           ↓
Orchestrator Layer (LangGraph + APScheduler)
           ↓
Skills Layer (News/Data/Report/Review Skills)
           ↓
Storage Layer (Files + Obsidian + ChromaDB + SQLAlchemy)
```

### Core Components

| Layer | Component | Purpose |
|-------|-----------|---------|
| Orchestrator | `workflow_manager.py` | LangGraph state machine, workflow execution |
| Orchestrator | `scheduler.py` | APScheduler定时任务 |
| Orchestrator | `workflow_states.py` | WorkflowState dataclass, status/type enums |
| Orchestrator | `nodes.py` | Individual workflow nodes (fetch_news, generate_report, etc.) |
| Skills | `skills/*.py` | Research skills (news, data, report, review) |
| Skills | `skills/base.py` | BaseSkill abstract class, SkillContext, SkillResult |
| DB | `db/models.py` | SQLAlchemy ORM models |
| DB | `db/repositories.py` | Data access layer (WorkflowRepository, etc.) |
| DB | `db/session.py` | Database session management (SQLite/PostgreSQL) |
| Storage | `storage/file_storage.py` | Local file operations |
| Storage | `storage/vector_storage.py` | ChromaDB vector storage |
| Storage | `storage/obsidian_storage.py` | Obsidian vault management |

### Workflow State Machine

```
PENDING → RUNNING → WAITING_APPROVAL → COMPLETED
                  ↘ FAILED
```

### Workflow Types (WorkflowType enum)
- `daily_briefing` - Daily morning report
- `news_review` - News quick commentary
- `data_update` - Data batch update
- `daily_summary` - Evening summary

## Key Conventions

1. **All numerical calculations via Python code** - Never let LLM generate numbers directly; use Python execution sandbox
2. **Human-in-the-loop for approvals** - Workflow pauses at `await_approval` node, requires manual confirmation
3. **Database session via context manager** - Always use `db_transaction()` or `get_db_session()` for DB operations
4. **Storage path sanitization** - Always sanitize filenames before path construction to prevent traversal
5. **Notification on workflow completion** - WorkflowManager sends notifications for completed/failed/approval_required states

## Database

- Development: SQLite at `data/research_assistant.db`
- Production: PostgreSQL (set `DATABASE_URL` env var)
- Models defined in `src/db/models.py`
- Use repositories from `src/db/repositories.py` for data access

## Testing

- Unit tests in `tests/` directory
- Use `PYTHONPATH=. pytest tests/ -v` to run
- Key test files: `test_orchestrator.py`, `test_db.py`, `test_storage.py`

## Design Documents

- Specs: `docs/superpowers/specs/`
- Plans: `docs/superpowers/plans/`
- Phase 1: Skills + Storage foundation
- Phase 2: Orchestrator + Scheduler + DB persistence
- Phase 3+ (planned): Bloomberg/Wind API, Multi-agent, Team collaboration