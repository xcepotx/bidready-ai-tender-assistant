import os
from celery import Celery

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

celery_app = Celery(
    "tender_worker",
    broker=REDIS_URL,
    backend=REDIS_URL,
)

@celery_app.task
def ping_worker():
    return {"status": "ok", "worker": "tender_worker"}
