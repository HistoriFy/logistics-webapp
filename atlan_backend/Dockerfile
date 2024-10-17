FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.7.1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    libpq-dev \
    nginx \
    && rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="${POETRY_HOME}/bin:$PATH"

COPY pyproject.toml poetry.lock ./

RUN poetry install --no-interaction --no-ansi

COPY . .

COPY nginx.conf /etc/nginx/sites-available/default
RUN ln -sf /etc/nginx/sites-available/default /etc/nginx/sites-enabled/

RUN mkdir -p /app/static /app/media

COPY redis.conf /etc/redis/redis.conf

RUN python manage.py collectstatic --noinput

RUN python manage.py migrate

RUN echo '#!/bin/bash\n\
service nginx start\n\
service redis-server start\n\
celery -A atlan_backend worker --loglevel=info &\n\
gunicorn atlan_backend.asgi:application -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000\n'\ 
> /app/start.sh && chmod +x /app/start.sh

EXPOSE 80 8000

CMD ["/app/start.sh"]
