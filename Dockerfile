FROM python:3.11-slim-buster as base

ENV PYTHONBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

RUN apt-get update
RUN pip3 install --upgrade pip

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

FROM base as dev

RUN mkdir "opt/app"
ENV PYTHONPATH /opt/app:/opt

COPY app /opt/app
COPY tests /opt/app/tests

WORKDIR /opt/app

EXPOSE 5000

RUN chmod +x deploy/run.sh
ENTRYPOINT ["deploy/run.sh"]