#!/bin/bash

# Read environment variables
UWSGI_HTTP_ADDRESS="${UWSGI_HTTP_ADDRESS:-0.0.0.0:8000}"
UWSGI_CHEAPER_ALGO="${UWSGI_CHEAPER_ALGO:-backlog}"
UWSGI_CHEAPER="${UWSGI_CHEAPER:-2}"
UWSGI_CHEAPER_INITIAL="${UWSGI_CHEAPER_INITIAL:-4}"
UWSGI_CHEAPER_STEP="${UWSGI_CHEAPER_STEP:-2}"
UWSGI_MAX_WORKERS="${UWSGI_MAX_WORKERS:-10}"
UWSGI_CHEAPER_RSS_LIMIT_SOFT="${UWSGI_CHEAPER_RSS_LIMIT_SOFT:-201326592}"
UWSGI_CHEAPER_RSS_LIMIT_HARD="${UWSGI_CHEAPER_RSS_LIMIT_HARD:-234881024}"

# Run the uwsgi command
uwsgi --http "$UWSGI_HTTP_ADDRESS" \
    --module=bkdnoj.wsgi:application \
    --env DJANGO_SETTINGS_MODULE=bkdnoj.settings \
    --master --pidfile=/tmp/bkdnoj_v2_backend.pid \
    --static-map /media=/app/media \
    --static-map /static=/app/static \
    --cheaper-algo "$UWSGI_CHEAPER_ALGO" \
    --cheaper "$UWSGI_CHEAPER" \
    --cheaper-initial "$UWSGI_CHEAPER_INITIAL" \
    --cheaper-step "$UWSGI_CHEAPER_STEP" \
    --workers "$UWSGI_MAX_WORKERS" \
    --memory-report \
    --cheaper-rss-limit-soft "$UWSGI_CHEAPER_RSS_LIMIT_SOFT" \
    --cheaper-rss-limit-hard "$UWSGI_CHEAPER_RSS_LIMIT_HARD"
