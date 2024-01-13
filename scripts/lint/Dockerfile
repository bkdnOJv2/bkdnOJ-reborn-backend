FROM python:3.8-slim-buster

#
RUN apt-get update && apt-get install -y \
    libpq-dev \
    python3-dev \
    build-essential \
    git

RUN pip install pylint==2.15.9 pylint-django==2.5.3 pylint-plugin-utils==0.7 
# Match the version of Django in your project
COPY app/requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt
