# API Documentation for the Project

This API documentation provides an overview of the various endpoints, request formats, headers, sample requests, and common error responses. The API is designed for users, drivers, and fleet owners to interact with the system for booking rides, managing vehicles, and handling driver assignments.

---

## **Authentication API**

### **Register User**

- **Endpoint**: `/api/v1/auth/register/`
- **Method**: `POST`
- **Description**: Registers a new user, driver, or fleet owner.

#### Request Headers

- `Content-Type`: `application/json`

#### Request Body

```json
{
  "user_type": "user",  // Can be 'user', 'driver', or 'fleet_owner'
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "1234567890",
  "password": "strong_password",
  "license_number": "DR123456",  // Required for 'driver' type
  "company_name": "Fleet Corp"   // Required for 'fleet_owner' type
}
```

#### Response Example

```json
{
  "refresh": "jwt_refresh_token",
  "access": "jwt_access_token",
  "message": "Registration successful",
  "user_id": 1
}
```

#### Common Error Responses

- **400 Bad Request**

```json
{
  "success": false,
  "message": "Invalid user type.",
  "data": {}
}
```

---

### **Login User**

- **Endpoint**: `/api/v1/auth/login/`
- **Method**: `POST`
- **Description**: Authenticates an existing user, driver, or fleet owner and returns JWT tokens.

#### Request Headers

- `Content-Type`: `application/json`

#### Request Body

```json
{
  "user_type": "user", // Can be 'user', 'driver', or 'fleet_owner'
  "email": "john@example.com",
  "password": "strong_password"
}
```

#### Response Example

```json
{
  "refresh": "jwt_refresh_token",
  "access": "jwt_access_token",
  "message": "Login successful"
}
```

#### Common Error Responses

- **401 Unauthorized**

```json
{
  "success": false,
  "message": "Invalid credentials",
  "data": {}
}
```

---

## **Booking API**

### **Create Booking**

- **Endpoint**: `/api/v1/booking/create-booking/`
- **Method**: `POST`
- **Description**: Allows users to create a booking for a ride.

#### Request Headers

- `Authorization`: `Bearer <jwt_access_token>`
- `Content-Type`: `application/json`

#### Request Body

```json
{
  "vehicle_type_id": 1,
  "pickup_address": "123 Street, City",
  "pickup_latitude": 12.9715987,
  "pickup_longitude": 77.5945627,
  "pickup_place_name": "Home",
  "dropoff_address": "456 Avenue, City",
  "dropoff_latitude": 12.9715987,
  "dropoff_longitude": 77.5945627,
  "dropoff_place_name": "Office",
  "payment_method": "cash"
}
```

#### Response Example

```json
{
  "booking_id": 123,
  "estimated_cost": 250.00,
  "distance": 10.5,
  "estimated_duration": 1200,
  "status": "pending"
}
```

#### Common Error Responses

- **400 Bad Request**

```json
{
  "success": false,
  "message": "Pricing model not found for the selected vehicle type",
  "data": {}
}
```

---

### **Price Estimation**

- **Endpoint**: `/api/v1/booking/price-estimation/`
- **Method**: `POST`
- **Description**: Provides an estimated cost for a ride based on origin and destination locations.

#### Request Headers

- `Authorization`: `Bearer <jwt_access_token>`
- `Content-Type`: `application/json`

#### Request Body

```json
{
  "origin_place_id": "ChIJn1zUlImlZzsRwXNuB1rZBEI",
  "destination_place_id": "ChIJSxMWDBUdZzsRtmBk9Q4mI0U",
  "place_type": "city"  // Optional field for region type (city, town, village, etc.)
}
```

#### Response Example

```json
{
  "origin_place_type": "City",
  "destination_place_type": "City",
  "distance": 15.2,
  "estimated_duration_seconds": 1800,
  "price_estimations": [
    {
      "vehicle_type_id": 1,
      "vehicle_type": "2 wheeler",
      "estimated_cost": 150.75,
      "currency": "INR"
    },
    {
      "vehicle_type_id": 2,
      "vehicle_type": "3 wheeler",
      "estimated_cost": 250.25,
      "currency": "INR"
    }
  ]
}
```

#### Common Error Responses

- **400 Bad Request**

```json
{
  "success": false,
  "message": "Region 'City' not found in the database",
  "data": {}
}
```

---

### **Get Place Predictions**

- **Endpoint**: `/api/v1/booking/place-predictions/`
- **Method**: `GET`
- **Description**: Fetches location suggestions based on the input query.

#### Request Headers

- `Authorization`: `Bearer <jwt_access_token>`
- `Content-Type`: `application/json`

#### Query Parameters

- `query`: The search text for the place predictions.

#### Response Example

```json
{
  "predictions": [
    {
      "description": "Place 1, City, Country",
      "place_id": "ChIJn1zUlImlZzsRwXNuB1rZBEI"
    },
    {
      "description": "Place 2, City, Country",
      "place_id": "ChIJSxMWDBUdZzsRtmBk9Q4mI0U"
    }
  ]
}
```

#### Common Error Responses

- **400 Bad Request**

```json
{
  "success": false,
  "message": "Invalid query parameter.",
  "data": {}
}
```

---

## **Driver API**

### **Accept Booking**

- **Endpoint**: `/api/v1/driver/accept-booking/`
- **Method**: `POST`
- **Description**: Allows a driver to accept a booking request.

#### Request Headers

- `Authorization`: `Bearer <jwt_access_token>`
- `Content-Type`: `application/json`

#### Request Body

```json
{
  "booking_id": 123
}
```

#### Response Example

```json
{
  "message": "Booking accepted successfully."
}
```

#### Common Error Responses

- **403 Unauthorized**

```json
{
  "success": false,
  "message": "You are not authorized to accept this booking.",
  "data": {}
}
```

---

### **Validate OTP**

- **Endpoint**: `/api/v1/driver/validate-otp/`
- **Method**: `POST`
- **Description**: Allows the driver to validate the OTP for starting a trip.

#### Request Headers

- `Authorization`: `Bearer <jwt_access_token>`
- `Content-Type`: `application/json`

#### Request Body

```json
{
  "booking_id": 123,
  "otp": "123456"
}
```

#### Response Example

```json
{
  "message": "OTP validated. Booking status updated to on_trip."
}
```

#### Common Error Responses

- **400 Bad Request**

```json
{
  "success": false,
  "message": "Invalid OTP.",
  "data": {}
}
```

---

## **Fleet Owner API**

### **Add Driver**

- **Endpoint**: `/api/v1/fleet_owner/add_driver/`
- **Method**: `POST`
- **Description**: Allows a fleet owner to add a new driver.

#### Request Headers

- `Authorization`: `Bearer <jwt_access_token>`
- `Content-Type`: `application/json`

#### Request Body

```json
{
  "email": "driver@example.com",
  "name": "John Driver",
  "phone": "9876543210",
  "password": "driver_password",
  "license_number": "DL456789"
}
```

#### Response Example

```json
{
  "message": "Driver added successfully."
}
```

#### Common Error Responses

- **400 Bad Request**

```json
{
  "success": false,
  "message": "License number already exists.",
  "data": {}
}
```

---

### **View Drivers**

- **Endpoint**: `/api/v1/fleet_owner/view_drivers/`
- **Method**: `GET`
- **Description**: Allows a fleet owner to view all drivers under their management.

#### Request Headers

- `Authorization`: `Bearer <jwt_access_token>`

#### Response Example

```json
{
  "drivers": [
    {
      "driver_id": 1,
      "name": "John Driver",
      "email": "driver@example.com",
      "phone": "9876543210",
      "license_number": "DL456789",
      "status": "active",
      "availability_status": "available"
    }
  ]
}
```

---

## **Regular User API**

### **User Booking List**

- **

Endpoint**: `/api/v1/regular_user/bookings/`
- **Method**: `GET`
- **Description**: Retrieves all bookings for the logged-in user.

#### Request Headers

- `Authorization`: `Bearer <jwt_access_token>`

#### Response Example

```json
{
  "user_id": 1,
  "bookings": [
    {
      "booking_id": 123,
      "vehicle_type": "2 wheeler",
      "pickup_address": "123 Street, City",
      "dropoff_address": "456 Avenue, City",
      "status": "completed"
    }
  ]
}
```

---

## Common Error Codes

| Error Code | Error Message                    | Description                                          |
|------------|-----------------------------------|------------------------------------------------------|
| 400        | Bad Request                       | The request was invalid or malformed.                |
| 401        | Unauthorized                      | Authentication failed or missing token.              |
| 403        | Forbidden                         | The user does not have permission to access this resource. |
| 404        | Not Found                         | The requested resource could not be found.           |
| 500        | Internal Server Error             | An unexpected error occurred on the server.          |
