### WebSocket Connection Documentation

#### 1. **User WebSocket Connection URL**

```bash
ws://<localhost>:<port>/regular_user/ws/bookings/?token=jwt_token
```

- **Purpose:** This WebSocket is used for regular users to receive real-time updates on their bookings.
- **Group Name Format:** `user_{user_id}_bookings`
- **Messages:**
  - **Booking Status Update:**
    - Triggered when the status of a user's booking changes (e.g., accepted, cancelled, on trip, etc.).
    - Example message:
      ```json
      {
        "type": "booking_status_update",
        "message": {
          "status": "on_trip",
          "booking_id": 123,
          "pickup_time": "2024-10-18 10:30:00",
          "message": "OTP Verified. Trip has started."
        }
      }
      ```
  - **OTP Update:**
    - Triggered when an OTP is sent or updated.
    - Example message:
      ```json
      {
        "type": "send_otp_update",
        "otp": "123456",
        "booking_id": 123
      }
      ```
  - **Location Update:**
    - Broadcasts driver’s real-time location to the user during the trip.
    - Example message:
      ```json
      {
        "type": "location_update",
        "driver_id": 45,
        "current_latitude": "37.7749",
        "current_longitude": "-122.4194",
        "status": "on_trip"
      }
      ```

#### 2. **Driver WebSocket Connection URL for Available Bookings**

```bash
ws://<localhost>:<port>/driver/ws/available_bookings/?token=jwt_token
```

- **Purpose:** This WebSocket is used by drivers to receive updates on available bookings.
- **Group Name Format:** `driver_{driver_id}_available_bookings`
- **Messages:**
  - **Available Booking Update:**
    - Sent when a booking is available for the driver to accept.
    - Example message:
      ```json
      {
        "type": "available_booking_update",
        "message": {
          "status": "accepted",
          "booking_id": 123,
          "pickup_location": "123 Main St",
          "phone_number": "+1234567890",
          "dropoff_location": "456 Elm St"
        }
      }
      ```
  - **Trip Start:**
    - Sent when the trip has started.
    - Example message:
      ```json
      {
        "type": "available_booking_update",
        "message": {
          "status": "on_trip",
          "booking_id": 123,
          "pickup_time": "2024-10-18 10:30:00"
        }
      }
      ```
  - **Trip Completion:**
    - Sent when the trip is completed.
    - Example message:
      ```json
      {
        "type": "available_booking_update",
        "message": {
          "status": "completed",
          "booking_id": 123,
          "dropoff_time": "2024-10-18 11:00:00"
        }
      }
      ```

#### 3. **Driver WebSocket for Confirmed Bookings**

```bash
ws://<localhost>:<port>/driver/ws/available_bookings/?token=jwt_token
```

- **Purpose:** This WebSocket is for drivers to receive updates on bookings that they have already accepted.
- **Messages:**
  - **Booking Status Update:**
    - Example message:
      ```json
      {
        "type": "booking_status_update",
        "message": {
          "status": "accepted",
          "booking_id": 123,
          "pickup_location": "123 Main St",
          "phone_number": "+1234567890",
          "dropoff_location": "456 Elm St"
        }
      }
      ```
  - **Cancel Booking:**
    - Sent when a driver cancels the booking.
    - Example message:
      ```json
      {
        "type": "booking_status_update",
        "message": {
          "status": "cancelled",
          "booking_id": 123,
          "message": "Booking has been cancelled by the driver."
        }
      }
      ```
  - **Trip Start:**
    - Sent when the trip has started after OTP verification.
    - Example message:
      ```json
      {
        "type": "booking_status_update",
        "message": {
          "status": "on_trip",
          "booking_id": 123,
          "pickup_time": "2024-10-18 10:30:00",
          "message": "OTP Verified. Trip has started."
        }
      }
      ```

#### 4. **Driver's Location Updates to Users**

- **Function:** `_broadcast_location_update(driver, booking, status)`
- **Description:** Sends real-time updates about the driver’s current location during a booking.
- **Output Example:**
  ```json
  {
    "type": "location_update",
    "driver_id": 45,
    "current_latitude": "37.7749",
    "current_longitude": "-122.4194",
    "status": "on_trip"
  }
  ```

#### 5. **Trigger for OTP Updates**

- **Function:** Updates the user’s OTP for booking verification.
- **Output Example:**
  ```json
  {
    "type": "send_otp_update",
    "otp": "123456",
    "booking_id": 123
  }
  ```

#### 6. **Driver Acceptance of Booking**

- **Function:** `notify_driver_about_booking(driver, booking)`
- **Purpose:** Notifies the driver about a newly accepted booking.
- **Output Example:**
  ```json
  {
    "type": "booking_status_update",
    "message": {
      "status": "accepted",
      "booking_id": 123,
      "pickup_location": "123 Main St",
      "phone_number": "+1234567890",
      "dropoff_location": "456 Elm St"
    }
  }
  ```

#### 7. **Booking Cancellation**

- **Function:** `send_booking_status_update(sender, instance, created, **kwargs)`
- **Purpose:** Sends a message when the booking is canceled by the driver or user.
- **Output Example:**
  ```json
  {
    "type": "booking_status_update",
    "message": {
      "status": "cancelled",
      "booking_id": 123,
      "message": "Booking has been cancelled by the driver."
    }
  }
  ```

### Summary of WebSocket Message Types

| WebSocket Type             | Purpose                                   | Example Group Name                    | Output Type                |
|----------------------------|-------------------------------------------|---------------------------------------|----------------------------|
| **User Booking Updates**    | Sends booking status updates to the user  | `user_{user_id}_bookings`             | `booking_status_update`     |
| **Driver Available Bookings** | Sends available booking updates to drivers | `driver_{driver_id}_available_bookings` | `available_booking_update`  |
| **Driver Confirmed Bookings** | Sends updates to drivers about their accepted bookings | `driver_{driver_id}_bookings` | `booking_status_update` |
| **Location Update**         | Sends driver location updates to the user | `user_{booking.user.id}_bookings` | `location_update`            |
| **OTP Update**              | Sends OTP verification updates to users  | `user_{user_id}_bookings`             | `send_otp_update`           |

