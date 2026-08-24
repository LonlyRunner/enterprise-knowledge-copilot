"""Backward-compatible Celery import.

The application has one configured Celery instance in ``app.worker.celery_app``.
Keeping this alias avoids two competing brokers/task registries.
"""

from app.worker.celery_app import celery_app


celery = celery_app

__all__ = ["celery", "celery_app"]
