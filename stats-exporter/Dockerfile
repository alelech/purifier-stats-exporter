FROM python:3-alpine

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN apk add --no-cache libffi-dev libressl-dev
RUN apk add --no-cache --virtual .compile-deps gcc musl-dev \
&& pip install --no-cache-dir -r requirements.txt\
&& apk del .compile-deps

EXPOSE 8080
ENV LOG_LEVEL INFO

COPY purifier_stats_exporter.py ./

ENTRYPOINT exec python ./purifier_stats_exporter.py -p 8080 --ip $PURIFIER_IP --token $PURIFIER_ACCESS_TOKEN --log $LOG_LEVEL
