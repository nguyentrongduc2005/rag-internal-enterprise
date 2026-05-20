#!/bin/sh
uv run celery -A app.celery_app worker --loglevel=info
