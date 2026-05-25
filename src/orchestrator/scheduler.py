"""定时任务调度器"""
import logging
from typing import Optional
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
from .workflow_manager import WorkflowManager
from .workflow_states import WorkflowType
from src.db.session import db_transaction
from src.db.repositories import WorkflowRepository

logger = logging.getLogger(__name__)

class TaskScheduler:
    """定时任务调度器"""

    def __init__(self, workflow_manager: WorkflowManager):
        self.workflow_manager = workflow_manager
        self.scheduler = BackgroundScheduler()
        self._running = False

    def start(self) -> None:
        """启动调度器"""
        if not self._running:
            self.scheduler.start()
            self._running = True
            logger.info("TaskScheduler started")

    def stop(self) -> None:
        """停止调度器"""
        if self._running:
            self.scheduler.shutdown(wait=False)
            self._running = False
            logger.info("TaskScheduler stopped")

    def add_cron_job(
        self,
        job_id: str,
        workflow_type: WorkflowType,
        hour: int,
        minute: int,
        **kwargs,
    ) -> None:
        """添加 Cron 定时任务"""
        trigger = CronTrigger(hour=hour, minute=minute)
        self.scheduler.add_job(
            func=self._run_workflow,
            trigger=trigger,
            args=[workflow_type, kwargs.get("context", {})],
            id=job_id,
            name=f"{workflow_type.value} - {job_id}",
            replace_existing=True,
        )
        self._update_scheduled_task(job_id, workflow_type, f"{minute} {hour} * * *")
        logger.info(f"Added cron job: {job_id} for {workflow_type.value} at {hour}:{minute}")

    def add_interval_job(
        self,
        job_id: str,
        workflow_type: WorkflowType,
        hours: int = 0,
        minutes: int = 0,
        **kwargs,
    ) -> None:
        """添加间隔定时任务"""
        trigger = IntervalTrigger(hours=hours, minutes=minutes)
        self.scheduler.add_job(
            func=self._run_workflow,
            trigger=trigger,
            args=[workflow_type, kwargs.get("context", {})],
            id=job_id,
            name=f"{workflow_type.value} - {job_id}",
            replace_existing=True,
        )
        self._update_scheduled_task(job_id, workflow_type, f"interval {hours}h {minutes}m")
        logger.info(f"Added interval job: {job_id} for {workflow_type.value} every {hours}h {minutes}m")

    def remove_job(self, job_id: str) -> None:
        """移除定时任务"""
        try:
            self.scheduler.remove_job(job_id)
            logger.info(f"Removed job: {job_id}")
        except Exception as e:
            logger.error(f"Failed to remove job {job_id}: {e}")

    def _run_workflow(self, workflow_type: WorkflowType, context: dict) -> None:
        """运行工作流（内部方法）"""
        logger.info(f"Triggering workflow: {workflow_type.value}")
        try:
            self.workflow_manager.trigger_workflow(workflow_type, context)
        except Exception as e:
            logger.error(f"Workflow {workflow_type.value} failed: {e}")

    def _update_scheduled_task(
        self,
        job_id: str,
        workflow_type: WorkflowType,
        cron_expression: str,
    ) -> None:
        """更新定时任务记录"""
        try:
            with db_transaction() as session:
                from src.db.models import ScheduledTask
                task = session.query(ScheduledTask).filter(ScheduledTask.id == job_id).first()
                if task:
                    task.cron_expression = cron_expression
                    task.is_active = True
                else:
                    task = ScheduledTask(
                        id=job_id,
                        workflow_type=workflow_type.value,
                        cron_expression=cron_expression,
                        is_active=True,
                    )
                    session.add(task)
        except Exception as e:
            logger.error(f"Failed to update scheduled task {job_id}: {e}")

    def setup_default_jobs(self) -> None:
        """设置默认定时任务"""
        self.add_cron_job("daily_briefing", WorkflowType.DAILY_BRIEFING, hour=8, minute=0)
        self.add_cron_job("morning_news", WorkflowType.NEWS_REVIEW, hour=7, minute=30)
        self.add_cron_job("price_update", WorkflowType.DATA_UPDATE, hour=17, minute=0)
        logger.info("Setup default scheduled jobs")