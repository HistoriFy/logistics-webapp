FROM python:3.12-slim

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
    openssl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="${POETRY_HOME}/bin:$PATH"

# Copy only the pyproject.toml and poetry.lock to leverage Docker cache for dependencies
COPY pyproject.toml poetry.lock ./

# Install Python dependencies via Poetry
RUN poetry install --no-interaction --no-ansi

# Create necessary directories
RUN mkdir -p /app/static /app/media /app/logs /etc/nginx/ssl

# Generate SSL certificate
RUN openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/nginx/ssl/nginx.key \
    -out /etc/nginx/ssl/nginx.crt \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost" \
    && chmod 644 /etc/nginx/ssl/nginx.crt \
    && chmod 644 /etc/nginx/ssl/nginx.key

# Copy the rest of the application code
COPY . .

# Copy Nginx configuration
COPY /docker-compose-config/nginx.conf /etc/nginx/sites-available/default
RUN ln -sf /etc/nginx/sites-available/default /etc/nginx/sites-enabled/

# Copy Redis configuration
COPY /docker-compose-config/redis.conf /etc/redis/redis.conf

# Set permissions
RUN chmod -R 777 /app/logs

# Copy and set permissions for start script
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Expose both HTTP and HTTPS ports
EXPOSE 80 443 8000

# Define the default command
CMD ["/app/start.sh"]