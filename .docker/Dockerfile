FROM python:3.12
ENV PYTHONUNBUFFERED=1
WORKDIR /app

COPY pyproject.toml /app

COPY poetry.lock /app

COPY . /app

RUN pip3 install poetry

RUN poetry install
