FROM python:3.8-alpine3.16

ENV UWSGI_HTTP=:8000
ENV UWSGI_WSGI_FILE=bkdnoj.wsgi:application
ENV UWSGI_CHEAPER_ALGO=backlog
ENV UWSGI_CHEAPER=2
ENV UWSGI_CHEAPER_INITIAL=4
ENV UWSGI_CHEAPER_STEP=2
ENV UWSGI_CHEAPER_MAX=10

COPY . ./app
WORKDIR /app

RUN apk add --update \
    build-base jpeg-dev zlib-dev libjpeg \
    gettext py3-lxml py3-pillow openldap-dev \
    python3-dev libpq-dev 
RUN apk add git libseccomp libseccomp-dev libffi-dev
RUN pip install -r requirements.txt

EXPOSE 8000
CMD ["uwsgi", "--http", "${UWSGI_HTTP}", \
        "--wsgi-file", "${UWSGI_WSGI_FILE}", \
        "--cheaper-algo", "${UWSGI_CHEAPER_ALGO}", \
        "--cheaper", "${UWSGI_CHEAPER}", \
        "--cheaper-initial", "${UWSGI_CHEAPER_INITIAL}", \
        "--cheaper-step", "${UWSGI_CHEAPER_STEP}", \
        "--cheaper-max", "${UWSGI_CHEAPER_MAX}"]
