FROM python:3.8-alpine3.16

COPY . ./app

WORKDIR /app

RUN apk add --update --no-cache \
    build-base jpeg-dev zlib-dev libjpeg \
    gettext py3-lxml py3-pillow openldap-dev \
    python3-dev libpq-dev 
RUN apk add git
RUN apk add libseccomp libseccomp-dev libffi-dev
RUN pip install -r requirements.txt

EXPOSE 8000

RUN python manage.py migrate
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]