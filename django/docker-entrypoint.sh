#! /usr/bin/env bash

#/bin/bash -c -- "while true; do sleep 30; done;"
python manage.py collectstatic --noinput
python manage.py makemigrations --noinput
python manage.py migrate --noinput
python manage.py compilemessages -v 0

uvicorn profileSensor.asgi:application --host 0.0.0.0 --port 8000 --timeout-keep-alive 10 --workers 1 --lifespan off