FROM python:3.12

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV DOMAIN=

WORKDIR /app

COPY . /app/
COPY ./requirements.txt /app/

RUN pip install -r requirements.txt

ENTRYPOINT [ "sh", "-c", "./scripts/start.sh" ]
