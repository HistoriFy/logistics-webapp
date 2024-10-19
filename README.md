# Logistics Full Stack App

This repository provides a full-featured logistics system, consisting of both backend and frontend. The backend is built with Django Rest Framework (DRF), Docker, Celery, Redis, PostgreSQL, and the frontend uses HTML, CSS, and JavaScript.

- **Live Backend (REST APIs):** [Backend API URL](http://149.102.149.102:8000)
- **Live Backend (WebSockets):** `ws://149.102.149.102:8000`
- **Live Frontend:** [Logistics Frontend](http://https://logisticswebapprathore.fyi/)

> **Note**: If there's a communication issue between the frontend and backend due to protocol mismatch, please enable `Insecure Content` in your browser's settings. [Update settings](chrome://settings/content/siteDetails?site=https%3A%2F%2Flogisticswebapprathore.fyi).

- **Postman Collection:** [Logistics API](https://www.postman.com/rathore10/logistics)
- **DB Architecture:** [Database Diagram](https://www.blocksandarrows.com/editor/VIGNePpAxVZlFlkrr)

## 🚀 Features

### 1. **Configurable Search Algorithm**
You can modify key parameters in the search algorithm, such as:
   - **Search Radius**: The initial search radius in km.
   - **Search Time Limit**: The maximum time to search for nearby drivers, in seconds.
   - **Incremental Radius Growth**: Increase the search radius if no drivers are found within the initial area.

These parameters can be configured through environment variables, allowing flexibility in tuning for different use cases.

### 2. **GPS Simulation**
Simulates GPS locations for drivers. The simulation moves vehicles first to the pickup location and then to the drop-off using geographical calculations.

### 3. **Dockerized & Kubernetes Ready**
Fully Dockerized for easy deployment. Can also be deployed on Kubernetes clusters.

### 4. **Celery Background Tasks**
Handles background processes like:
   - Driver location updates in GPS simulation.
   - Real-time updates for users and drivers.
   - OTP generation for ride authentication.

### 5. **Redis Caching**
Leverages Redis to cache WebSocket connections and Celery tasks for efficient performance.

### 6. **Surge Pricing**
Dynamic pricing based on:
   - Afternoon heat, protecting drivers by increasing fares.
   - Reduced pricing at night
   - And in rural or small-town areas.

### 7. **Google Maps API Integration**
Seamlessly integrates with Google Maps for:
   - Place Autocomplete.
   - GPS coordinate conversions.
   - Real-time distance and ETA calculations.

### 8. **Custom JWT Authentication**
JWT-based authentication that handles different user roles, such as users, drivers, and fleet owners.

### 9. **Real-Time WebSocket Updates**
Provides real-time updates for:
   - Booking status.
   - Driver location.
   - OTP validation for trip commencement.
   - Updates for drivers on available bookings.

### 10. **Large-Scale Database**
Designed to handle large volumes of data with over 15 tables and 100+ columns for flexibility and scalability.

### 11. **OTP System**
Ensures trip authenticity by generating OTPs shared through WebSockets, which drivers must validate to start the trip.

### 12. **Custom Output Decorator and Error Handling**
Custom decorators for API responses and error handling for consistent and user-friendly responses.

## 🛠️ Prerequisites

- **Docker & Docker Compose:** Ensure both are installed on your system.
- **PostgreSQL:** If not using Docker, manually install PostgreSQL.

## ⚙️ Setup Instructions

### Step 1: Clone the Repository
```bash
git clone https://github.com/your-repo/logistics-backend.git
cd logistics-backend
```

### Step 2: Configure Environment Variables

Create an `.env` file in the root directory. Below are **mandatory** and **optional** environment variables:

#### **Mandatory Environment Variables**
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

# Redis Configuration (used for caching and background tasks)
REDIS_URL=redis://redis:6379/0

# Host and Debug Configuration
ALLOWED_HOSTS=<your_server_ip>,localhost
DEBUG=<true_or_false>
```

#### **Optional Environment Variables**
```bash
# Search Algorithm Configuration
SEARCH_RADIUS=<initial_search_radius_in_km>  # Default: 1
MAX_SEARCH_TIME=<max_search_time_in_seconds>  # Default: 300 (5 minutes)

# Simulation Configuration
DRIVER_SPEED=<driver_speed_in_meters_per_update>  # Default: 800
RANDOM_LOCATION_RADIUS=<random_location_radius_in_meters>  # Default: 2000

# WebSocket Configuration
WEBSOCKET_TIMEOUT=<timeout_for_users_in_seconds>  # Default: 3600 (1 hour)
WEBSOCKET_TIMEOUT_DRIVER=<timeout_for_drivers_in_seconds>  # Default: 3600 (1 hour)

# JWT Token Lifetime Configuration
ACCESS_TOKEN_LIFETIME=<access_token_lifetime_in_days>  # Default: 7
```

### Step 3: Build & Run Docker Containers
```bash
docker-compose up --build
```
This will:
- Build the Docker images.
- Start services for the web app, Nginx, PostgreSQL, Redis, and Celery.
- The backend will be accessible at `http://<your_server_ip>:8000`.

## 🐘 PostgreSQL Setup (Linux)

If you're installing PostgreSQL locally:

### Install PostgreSQL
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

### Create a Database & User
```bash
sudo -i -u postgres
psql
CREATE DATABASE logistics;
CREATE USER admin WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE logistics TO admin;
\q
```

## 🚀 Common Docker Commands
- **Stop containers:** `docker-compose down`
- **Rebuild without cache:** `docker-compose build --no-cache`
- **View logs:** `docker-compose logs -f`

## ⚙️ Nginx & Redis Configuration

- **Nginx:** The configuration is located in `nginx.conf`. It proxies requests to the Django app and serves static/media files.
- **Redis:** Configuration is located in `redis.conf` and handles caching and background tasks.

## ⚙️ Celery Setup
Celery is used for background tasks and operates with Redis as the broker. The worker is managed in the `celery` service within `docker-compose.yml`.