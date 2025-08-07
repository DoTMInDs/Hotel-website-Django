#!/usr/bin/env bash
set -o errexit

# pip install -r requirements.txt

python hotelapp/manage.py collectstatic --no-input

python hotelapp/manage.py migrate

if [ "$DJANGO_CREATEUSER" == "1" ]; then 
    python hotelapp/manage.py createsuperuser --noinput
fi

python hotelapp/manage.py runserver 0.0.0.0:$PORT
# python -m gunicorn hotelapp.asgi:application -k uvicorn.workers.UvicornWorker
