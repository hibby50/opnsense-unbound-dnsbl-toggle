From alpine:3.16.2

RUN apk add python3 py3-pip

RUN pip3 install flask requests waitress

RUN mkdir /app

COPY webapp.py /app

ADD templates /app/templates

ENTRYPOINT python3 /app/webapp.py
