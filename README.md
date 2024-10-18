# Logistics Full Stack App

This repository contains the backend and frontend of a logistics system built using Django Rest Framework (DRF), Docker, Celery, Redis, PostgreSQL, and a frontend using HTML, CSS, JavaScript, and Bootstrap.

## Prerequisites

- Docker and Docker Compose installed on your system.
- PostgreSQL installed (if not using Docker).

## Setup Instructions

### Step 1: Clone the Repository

```bash
git clone https://github.com/your-repo/logistics-backend.git
cd logistics-backend
```

### Step 2: Create `.env` File

Create an `.env` file in the root of your project directory with the following structure:

```bash
# Google API Key
GOOGLE_API_KEY=<your_google_api_key>

# Django Secret Key
SECRET_KEY=<your_django_secret_key>

# PostgreSQL Database Configuration
DATABASE_URL=postgresql://<your_db_user>:<your_db_password>@db/<your_db_name>
POSTGRES_USER=<your_db_user>
POSTGRES_PASSWORD=<your_db_password>
POSTGRES_DB=<your_db_name>

# Celery and Redis Configuration
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
REDASH_REDIS_URL=redis://localhost:6379/0

# Host and Debug Configuration
ALLOWED_HOSTS=<your_server_ip>,localhost
DEBUG=<true_or_false>

# Search Algorithm Configuration
SEARCH_RADIUS=<initial_search_radius_in_km>
MAX_SEARCH_TIME=<max_search_time_in_seconds>  # e.g., 300 for 5 minutes

# Simulation Configuration
DRIVER_SPEED=<driver_speed_in_meters_per_update>
RANDOM_LOCATION_RADIUS=<random_location_radius_in_meters>

# WebSocket Configuration
WEBSOCKET_TIMEOUT=<timeout_for_users_in_seconds>
WEBSOCKET_TIMEOUT_DRIVER=<timeout_for_drivers_in_seconds>

# JWT Token Lifetime Configuration
ACCESS_TOKEN_LIFETIME=<access_token_lifetime_in_days>

# Redis Configuration (Host and Port will be extracted from REDIS_URL)
REDIS_URL=redis://redis:6379/0
```

- **GOOGLE_API_KEY**: Google API key for accessing Google services (e.g., maps, geocoding).
- **SECRET_KEY**: The secret key for Django security.
- **DATABASE_URL**: PostgreSQL database connection URL.
- **POSTGRES_USER**: PostgreSQL database username.
- **POSTGRES_PASSWORD**: PostgreSQL database password.
- **POSTGRES_DB**: PostgreSQL database name.
- **CELERY_BROKER_URL**: URL for Celery broker, using Redis.
- **CELERY_RESULT_BACKEND**: URL for Celery results backend, using Redis.
- **REDASH_REDIS_URL**: URL for Redis caching (used with Redash).
- **ALLOWED_HOSTS**: Comma-separated list of allowed hosts/IPs.
- **DEBUG**: Set to `False` for production.

### Step 3: Build and Run Docker Containers

Use Docker Compose to build and run the containers:

```bash
docker-compose up --build
```

This command will:

- Build the Docker images.
- Start the web, Nginx, PostgreSQL, Redis, and Celery services.
- The Django server will be accessible at `http://<your_server_ipv4>:8000` after the containers are up and running.

### Step 4: Apply Database Migrations

Once the containers are running, open a new terminal window and run the following command to apply the migrations:

```bash
docker-compose exec web python manage.py migrate
```

### Step 5: Access the Frontend

The frontend of the app is served statically. You can access the frontend pages at the following URLs:

- Home Page: `http://<your_server_ipv4>/`
- User Dashboard: `http://<your_server_ipv4>/user-dashboard.html`
- Fleet Owner Dashboard: `http://<your_server_ipv4>/fleet-owner-dashboard.html`
- GPS Tracking: `http://<your_server_ipv4>/gps-tracking.html`
- Login: `http://<your_server_ipv4>/login.html`
- Register: `http://<your_server_ipv4>/register.html`

These pages are located in the `logistics_frontend` directory, and you can customize them further by editing the HTML, CSS, and JS files.

## Setup PostgreSQL via CLI (Linux)

If you're setting up PostgreSQL locally on a Linux machine (without Docker), follow these steps:

### Step 1: Install PostgreSQL

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

### Step 2: Start PostgreSQL Service

Start the PostgreSQL service:

```bash
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### Step 3: Switch to PostgreSQL User

Switch to the `postgres` user to manage databases:

```bash
sudo -i -u postgres
```

### Step 4: Create a Database and User

Once logged in as the `postgres` user, create the database and user for your project:

```bash
psql
CREATE DATABASE atlan;
CREATE USER attest WITH PASSWORD 'admin';
GRANT ALL PRIVILEGES ON DATABASE atlan TO attest;
```

Exit the PostgreSQL prompt by typing `\q`.

### Step 5: Modify PostgreSQL Configuration (Optional)

If you want to allow connections from other machines, modify the PostgreSQL configuration:

1. Open the PostgreSQL configuration file:

   ```bash
   sudo nano /etc/postgresql/13/main/postgresql.conf
   ```

2. Find the line `#listen_addresses = 'localhost'` and change it to:

   ```bash
   listen_addresses = '*'
   ```

3. Open the `pg_hba.conf` file:

   ```bash
   sudo nano /etc/postgresql/13/main/pg_hba.conf
   ```

4. Add the following line at the end of the file:

   ```bash
   host    all             all             0.0.0.0/0               md5
   ```

5. Restart PostgreSQL:

   ```bash
   sudo systemctl restart postgresql
   ```

Now, PostgreSQL is set up and can be accessed locally or remotely if configured.

### Step 6: Connect to PostgreSQL

You can connect to PostgreSQL from your command line using the following command:

```bash
psql -U attest -d atlan -h localhost
```

### Additional Commands

- To list databases: `\l`
- To list tables: `\dt`
- To quit: `\q`

## Common Docker Commands

- To stop the containers: `docker-compose down`
- To rebuild containers without cache: `docker-compose build --no-cache`
- To view container logs: `docker-compose logs -f`

## Nginx Configuration

The Nginx configuration is stored in the `nginx.conf` file. The Nginx service proxies requests to the Gunicorn server running the Django app and serves static and media files, along with the frontend files.

## Redis Configuration

Redis is used for background tasks and caching. The configuration is stored in the `redis.conf` file.

## Celery Configuration

Celery is configured to handle background tasks in the logistics system, with Redis as the message broker. The worker runs in the `celery` service defined in the `docker-compose.yml` file.
