FROM python:3.8-alpine3.16

# Configs
ENV UWSGI_HTTP_ADDRESS=0.0.0.0:8000

# Cheaper subsystem
ENV UWSGI_CHEAPER_ALGO=backlog
ENV UWSGI_CHEAPER=2
ENV UWSGI_CHEAPER_INITIAL=4
ENV UWSGI_CHEAPER_STEP=2
ENV UWSGI_MAX_WORKERS=10
ENV UWSGI_CHEAPER_RSS_LIMIT_SOFT=201326592
ENV UWSGI_CHEAPER_RSS_LIMIT_HARD=234881024

COPY . ./app
WORKDIR /app

RUN apk add --update \
    build-base jpeg-dev zlib-dev libjpeg \
    gettext py3-lxml py3-pillow openldap-dev \
    python3-dev libpq-dev 
RUN apk add git libseccomp libseccomp-dev libffi-dev
RUN pip install -r requirements.txt

CMD ["sh", "./run_prod_server.sh"]
