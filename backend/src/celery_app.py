"""
Configuración de Celery para procesamiento asíncrono.
"""

import os
from celery import Celery
from src.config import settings

# Configurar Celery
celery_app = Celery(
    "facturas_boosting",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=[
        "src.tasks.ocr_tasks",
        "src.tasks.gmail_tasks",
        "src.tasks.notification_tasks"
    ]
)

# Configuración de Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutos
    task_soft_time_limit=25 * 60,  # 25 minutos
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    result_expires=3600,  # 1 hora
    task_routes={
        "src.tasks.ocr_tasks.*": {"queue": "ocr_queue"},
        "src.tasks.gmail_tasks.*": {"queue": "gmail_queue"},
        "src.tasks.notification_tasks.*": {"queue": "notification_queue"},
    },
    task_default_queue="default",
    task_queues={
        "default": {
            "exchange": "default",
            "routing_key": "default",
        },
        "ocr_queue": {
            "exchange": "ocr",
            "routing_key": "ocr",
        },
        "gmail_queue": {
            "exchange": "gmail",
            "routing_key": "gmail",
        },
        "notification_queue": {
            "exchange": "notification",
            "routing_key": "notification",
        },
    },
)

# Configuración de logging
celery_app.conf.update(
    worker_log_format="[%(asctime)s: %(levelname)s/%(processName)s] %(message)s",
    worker_task_log_format="[%(asctime)s: %(levelname)s/%(processName)s][%(task_name)s(%(task_id)s)] %(message)s",
)

if __name__ == "__main__":
    celery_app.start()
