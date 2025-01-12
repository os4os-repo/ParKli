FROM python:3.11-slim-bookworm
WORKDIR /app

RUN apt-get update \
    && apt-get -y install libpq-dev gcc

COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
RUN apt-get update
CMD gunicorn -b 0.0.0.0:80 --timeout 1200 app:server --workers 10 --log-file=-
