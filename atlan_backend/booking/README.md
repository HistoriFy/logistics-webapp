# Booking API Documentation

This document provides instructions on how to use the Booking API endpoints, including sample requests, responses, and error handling. The API allows users to:

- Get place predictions based on a query string.
- Estimate prices for trips between two locations.
- Create bookings for trips.

**Note:** All endpoints require Bearer Token authentication in the request headers.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Authentication](#authentication)
- [API Endpoints](#api-endpoints)
  - [1. Place Predictions](#1-place-predictions)
  - [2. Price Estimation](#2-price-estimation)
  - [3. Booking Creation](#3-booking-creation)
- [Error Handling](#error-handling)
- [Examples](#examples)

## Prerequisites

- Python 3.6+
- Django and Django REST Framework installed
- Valid Google Maps API Key
- JWT Authentication set up in your Django project

## Authentication

All API requests must include a valid JWT Bearer Token in the `Authorization` header.

**Header Example:**

```
Authorization: Bearer your_jwt_token_here
```

## API Endpoints

### 1. Place Predictions

Retrieve a list of place predictions based on a query string.

- **URL:** `/bookings/place-predictions/`
- **Method:** `GET`
- **Headers:**
  - `Authorization: Bearer <your_jwt_token>`
- **Query Parameters:**
  - `query` (string, required): The search term for place predictions.

#### Sample Request

```
GET /bookings/place-predictions/?query=New York
Authorization: Bearer your_jwt_token_here
```

#### Sample Response

```json
{
  "success": true,
  "data": {
    "predictions": [
      {
        "description": "New York, NY, USA",
        "place_id": "ChIJOwg_06VPwokRYv534QaPC8g"
      },
      {
        "description": "New York City, NY, USA",
        "place_id": "ChIJOwg_06VPwokRYv534QaPC8g"
      },
      // More predictions...
    ]
  },
  "error": {
    "code": "",
    "message": "",
    "details": ""
  }
}
```

#### Possible Errors

- **400 Bad Request:** Invalid or missing query parameter.
- **401 Unauthorized:** Missing or invalid authentication token.

### 2. Price Estimation

Estimate trip prices between two locations for all vehicle types.

- **URL:** `/bookings/price-estimation/`
- **Method:** `POST`
- **Headers:**
  - `Authorization: Bearer <your_jwt_token>`
  - `Content-Type: application/json`
- **Request Body:**

  - `origin_place_id` (string, required): Place ID for the origin location.
  - `destination_place_id` (string, required): Place ID for the destination location.
  - `place_type` (string, optional): Type of place (`city`, `town`, `village`).

#### Sample Request

```json
POST /bookings/price-estimation/
Authorization: Bearer your_jwt_token_here
Content-Type: application/json

{
  "origin_place_id": "ChIJOwg_06VPwokRYv534QaPC8g",
  "destination_place_id": "ChIJd8BlQ2BZwokRAFUEcm_qrcA",
  "place_type": "city"
}
```

#### Sample Response

```json
{
  "success": true,
  "data": {
    "origin_place_type": "City",
    "destination_place_type": "City",
    "distance": 5.0,
    "estimated_duration_seconds": 600,
    "price_estimations": [
      {
        "vehicle_type": "2 Wheeler",
        "estimated_cost": 25.0,
        "currency": "INR"
      },
      {
        "vehicle_type": "3 Wheeler",
        "estimated_cost": 60.0,
        "currency": "INR"
      },
      {
        "vehicle_type": "Pickup 9ft",
        "estimated_cost": 100.0,
        "currency": "INR"
      },
      {
        "vehicle_type": "14ft",
        "estimated_cost": 200.0,
        "currency": "INR"
      }
    ]
  },
  "error": {
    "code": "",
    "message": "",
    "details": ""
  }
}
```

#### Possible Errors

- **400 Bad Request:** Invalid input data, missing place IDs, or region not found.
- **401 Unauthorized:** Missing or invalid authentication token.

### 3. Booking Creation

Create a new booking for a trip.

- **URL:** `/bookings/create/`
- **Method:** `POST`
- **Headers:**
  - `Authorization: Bearer <your_jwt_token>`
  - `Content-Type: application/json`
- **Request Body:**

  - `vehicle_type_id` (integer, required): ID of the selected vehicle type.
  - `pickup_address` (string, required): Address of the pickup location.
  - `pickup_latitude` (decimal, required): Latitude of the pickup location.
  - `pickup_longitude` (decimal, required): Longitude of the pickup location.
  - `pickup_place_name` (string, required): Place name of the pickup location.
  - `dropoff_address` (string, required): Address of the drop-off location.
  - `dropoff_latitude` (decimal, required): Latitude of the drop-off location.
  - `dropoff_longitude` (decimal, required): Longitude of the drop-off location.
  - `dropoff_place_name` (string, required): Place name of the drop-off location.
  - `payment_method` (string, required): Payment method for the booking.
  - `scheduled_time` (datetime, optional): Scheduled time for the trip.

#### Sample Request

```json
POST /bookings/create/
Authorization: Bearer your_jwt_token_here
Content-Type: application/json

{
  "vehicle_type_id": 1,
  "pickup_address": "123 Main St, New York, NY",
  "pickup_latitude": 40.7128,
  "pickup_longitude": -74.0060,
  "pickup_place_name": "New York",
  "dropoff_address": "456 Elm St, New York, NY",
  "dropoff_latitude": 40.7306,
  "dropoff_longitude": -73.9352,
  "dropoff_place_name": "Brooklyn",
  "payment_method": "Credit Card",
  "scheduled_time": "2024-10-20T15:30:00Z"
}
```

#### Sample Response

```json
{
  "success": true,
  "data": {
    "booking_id": 123,
    "estimated_cost": 50.0,
    "distance": 8.0,
    "estimated_duration": 900,
    "status": "pending"
  },
  "error": {
    "code": "",
    "message": "",
    "details": ""
  }
}
```

#### Possible Errors

- **400 Bad Request:** Invalid input data, missing fields, or pricing model not found.
- **401 Unauthorized:** Missing or invalid authentication token.

## Error Handling

All error responses follow the same structure:

```json
{
  "success": false,
  "data": {},
  "error": {
    "code": "ErrorType",
    "message": "Error message explaining what went wrong.",
    "details": "Additional details if available."
  }
}
```

### Common Error Codes

- **BadRequest:** The request is invalid or malformed.
- **Unauthorized:** You are not authorized to access this resource.
- **NotFound:** The requested resource was not found.
- **InternalServerError:** An unexpected error occurred on the server.

## Examples

### Example 1: Getting Place Predictions

**Request:**

```
GET /bookings/place-predictions/?query=Central Park
Authorization: Bearer your_jwt_token_here
```

**Response:**

```json
{
  "success": true,
  "data": {
    "predictions": [
      {
        "description": "Central Park, New York, NY, USA",
        "place_id": "ChIJ4zGFAZpYwokRGUGph3Mf37k"
      },
      // More predictions...
    ]
  },
  "error": {
    "code": "",
    "message": "",
    "details": ""
  }
}
```

### Example 2: Estimating Prices

**Request:**

```json
POST /bookings/price-estimation/
Authorization: Bearer your_jwt_token_here
Content-Type: application/json

{
  "origin_place_id": "ChIJ4zGFAZpYwokRGUGph3Mf37k",
  "destination_place_id": "ChIJd8BlQ2BZwokRAFUEcm_qrcA"
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "origin_place_type": "City",
    "destination_place_type": "City",
    "distance": 3.5,
    "estimated_duration_seconds": 480,
    "price_estimations": [
      {
        "vehicle_type": "2 Wheeler",
        "estimated_cost": 17.5,
        "currency": "INR"
      },
      {
        "vehicle_type": "3 Wheeler",
        "estimated_cost": 42.0,
        "currency": "INR"
      },
      {
        "vehicle_type": "Pickup 9ft",
        "estimated_cost": 70.0,
        "currency": "INR"
      },
      {
        "vehicle_type": "14ft",
        "estimated_cost": 140.0,
        "currency": "INR"
      }
    ]
  },
  "error": {
    "code": "",
    "message": "",
    "details": ""
  }
}
```

### Example 3: Creating a Booking

**Request:**

```json
POST /bookings/create/
Authorization: Bearer your_jwt_token_here
Content-Type: application/json

{
  "vehicle_type_id": 2,
  "pickup_address": "789 Broadway, New York, NY",
  "pickup_latitude": 40.7306,
  "pickup_longitude": -73.9352,
  "pickup_place_name": "Brooklyn",
  "dropoff_address": "321 Park Ave, New York, NY",
  "dropoff_latitude": 40.7128,
  "dropoff_longitude": -74.0060,
  "dropoff_place_name": "Manhattan",
  "payment_method": "Cash"
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "booking_id": 124,
    "estimated_cost": 60.0,
    "distance": 10.0,
    "estimated_duration": 1200,
    "status": "pending"
  },
  "error": {
    "code": "",
    "message": "",
    "details": ""
  }
}
```

## Additional Notes

- **Currency:** All estimated costs are in INR (Indian Rupees).
- **Time Formats:** Dates and times should be in ISO 8601 format.
- **Distance:** Distance is measured in kilometers (km).
- **Duration:** Duration is measured in seconds.

## Changes Noted

- **Currency Updated to INR:** The currency in the `price_estimations` and booking responses has been updated to `INR`.
- **API Key Retrieval:** The Google API Key is retrieved from `Settings.GOOGLE_API_KEY` instead of a hardcoded string.
- **Decorators and Helpers:** Custom decorators and helpers are used from `utils.helpers`, and exceptions from `utils.exceptions`.
- **Models Imported Correctly:** Models are imported from their respective modules, e.g., `pricing_model.models` instead of `pricing.models`.