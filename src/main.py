"""Phase 2 主入口"""
import argparse
import logging
from pathlib import Path

from src.db.session import init_db
from src.storage import FileStorage, VectorStorage, ObsidianStorage
from src.services.notification import NotificationService
from src.orchestrator import WorkflowManager, TaskScheduler, WorkflowType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_workflow_manager() -> WorkflowManager:
    """创建工作流管理器"""
    project_root = Path(__file__).parent.parent

    file_storage = FileStorage(project_root)
    vector_storage = VectorStorage(project_root / "vector_db")
    obsidian_storage = ObsidianStorage(
        project_root / "knowledge",
        project_root / "knowledge" / "templates"
    )
    notification_service = NotificationService(project_root / "notifications")

    return WorkflowManager(
        file_storage=file_storage,
        vector_storage=vector_storage,
        obsidian_storage=obsidian_storage,
        notification_service=notification_service,
    )

def main():
    parser = argparse.ArgumentParser(description="Research Assistant AI Agent - Phase 2")
    parser.add_argument("--init-db", action="store_true", help="Initialize database")
    parser.add_argument("--workflow", type=str, choices=["daily_briefing", "news_review", "data_update"], help="Run specific workflow")
    parser.add_argument("--start-scheduler", action="store_true", help="Start the scheduler")
    args = parser.parse_args()

    if args.init_db:
        logger.info("Initializing database...")
        init_db()
        logger.info("Database initialized")
        return

    if args.workflow:
        logger.info(f"Running workflow: {args.workflow}")
        manager = create_workflow_manager()
        workflow_type = WorkflowType(args.workflow)
        result = manager.trigger_workflow(workflow_type)
        logger.info(f"Workflow completed: {result.status}")
        return

    if args.start_scheduler:
        logger.info("Starting scheduler...")
        manager = create_workflow_manager()
        scheduler = TaskScheduler(manager)
        scheduler.setup_default_jobs()
        scheduler.start()
        logger.info("Scheduler started. Press Ctrl+C to stop.")
        try:
            import time
            while True:
                time.sleep(60)
        except KeyboardInterrupt:
            scheduler.stop()
            logger.info("Scheduler stopped")
        return

    parser.print_help()

if __name__ == "__main__":
    main()