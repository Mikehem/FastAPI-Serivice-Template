#! /usr/bin/env sh

exec uvicorn $APP_MODULE --workers $WORKERS_PER_CORE --port $PORT --host $HOST $@

