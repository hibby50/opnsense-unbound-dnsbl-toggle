From alpine:3.23.3

RUN apk add python3 py3-flask py3-requests py3-waitress

RUN mkdir /app

COPY webapp.py /app

ADD templates /app/templates

ENTRYPOINT python3 /app/webapp.py
