FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /app

COPY pyproject.toml /app

COPY poetry.lock /app

COPY . .

RUN pip3 install poetry

RUN poetry install
