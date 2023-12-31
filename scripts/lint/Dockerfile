FROM python:3.8-slim-buster

#
RUN apt-get update && apt-get install -y \
    python3-dev \
    build-essential

RUN pip install pylint==2.15.9 pylint-django==2.5.3 pylint-plugin-utils==0.7 
# Match the version of Django in your project

RUN pip install backports.zoneinfo
RUN pip install Django==4.0.4
