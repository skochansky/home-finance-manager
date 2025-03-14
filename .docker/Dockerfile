FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_VERSION=1.8.4

WORKDIR /app


COPY pyproject.toml poetry.lock ./

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        gcc \
        python3-dev \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir "poetry==${POETRY_VERSION}" \
    && poetry install --no-root --no-interaction --no-ansi \
    && apt-get purge -y gcc python3-dev \
    && apt-get autoremove -y

COPY . .

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]