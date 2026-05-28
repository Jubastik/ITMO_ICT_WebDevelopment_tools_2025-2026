import os
from celery import Celery
from app.parser import sync_parse_and_save

redis_url = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")

celery_app = Celery("parser_tasks", broker=redis_url, backend=redis_url)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

@celery_app.task(name="parse_url_task")
def parse_url_task(url: str):
    """Задача для парсинга URL в фоне."""
    return sync_parse_and_save(url)
