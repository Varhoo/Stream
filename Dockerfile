FROM python:3.8-slim

MAINTAINER Pavel Studenik <studenik@varhoo.cz>

RUN mkdir /app
WORKDIR /app

ENV BUILD_DEPS="build-essential"
COPY requirements.txt /app/
RUN apt update && apt install -y $BUILD_DEPS && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get -y remove $BUILD_DEPS && \
    apt -y autoremove && apt-get clean && \
    rm -rf /tmp/* /var/tmp/* /var/cache/* /var/lib/apt/lists/*

COPY . /app

ARG version
ENV WEB_CONCURRENCY=9 \
    VERSION=$version

CMD ["gunicorn", "--config", ".misc/gunicorn_conf.py", "vh.app:application"]
EXPOSE 7779

LABEL name=stream version=dev
