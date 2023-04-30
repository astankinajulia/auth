FROM python:3.11-slim-buster as base

ENV PYTHONBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

RUN apt-get update
RUN pip3 install --upgrade pip

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

FROM base as dev

RUN mkdir "opt/app"

COPY app /opt/app

WORKDIR /opt/app

#EXPOSE 8000

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]

#CMD ["gunicorn", "main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b 0.0.0.0:8000"]


