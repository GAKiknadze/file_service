#!/bin/bash
set -e

case "$1" in
    "api")
        exec uvicorn src:rest_app --host 0.0.0.0 --port 8000
        ;;
    "worker")
        exec celery -A src:worker_app worker --pool=prefork --loglevel=info
        ;;
    *)
        echo "Unknown command: $1"
        echo "Usage: $0 {api|worker}"
        exit 1
        ;;
esac
