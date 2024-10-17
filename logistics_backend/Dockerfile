# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.7.1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=false

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    libpq-dev \
    nginx \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="${POETRY_HOME}/bin:$PATH"

# Copy only the pyproject.toml and poetry.lock to leverage Docker cache for dependencies
COPY pyproject.toml poetry.lock ./

# Install Python dependencies via Poetry
RUN poetry install --no-interaction --no-ansi

# Copy the rest of the application code
COPY . .

# Copy Nginx configuration
COPY nginx.conf /etc/nginx/sites-available/default
RUN ln -sf /etc/nginx/sites-available/default /etc/nginx/sites-enabled/

# Create static and media directories
RUN mkdir -p /app/static /app/media

# Copy Redis configuration
COPY redis.conf /etc/redis/redis.conf

# Expose the necessary ports
EXPOSE 80 8000

# Start services in the start.sh script
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Define the default command
CMD ["/app/start.sh"]