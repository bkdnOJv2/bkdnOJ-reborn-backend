FROM python:3.8-alpine3.16

COPY . ./app

WORKDIR /app

RUN apk add --update \
    build-base jpeg-dev zlib-dev libjpeg \
    gettext py3-lxml py3-pillow openldap-dev \
    python3-dev libpq-dev 
RUN apk add git libseccomp libseccomp-dev libffi-dev
RUN pip install -r requirements.txt

CMD ["python", "manage.py", "migrate"]