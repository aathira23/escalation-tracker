"""
Celery Application Configuration
"""
from celery import Celery
from celery.schedules import crontab

from app.config import get_settings

settings = get_settings()

# Create Celery application
celery_app = Celery(
    "escalation_tracker",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=[
        "app.tasks.email_ingestion",
        "app.tasks.sla_monitor"
    ]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minute timeout
    worker_prefetch_multiplier=1,
)

# Periodic task schedule
celery_app.conf.beat_schedule = {
    # Check for new emails every 30 seconds (DISABLED to prevent auto-population)
    # "check-emails-every-30-seconds": {
    #     "task": "app.tasks.email_ingestion.process_incoming_emails",
    #     "schedule": 30.0,
    # },
    # Check SLA deadlines daily at 9 AM UTC
    "check-sla-daily": {
        "task": "app.tasks.sla_monitor.check_sla_deadlines",
        "schedule": crontab(hour=9, minute=0),
    },
}
