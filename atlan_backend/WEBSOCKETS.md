# WebSocket API Documentation for Project

This documentation provides an overview of the WebSocket connections used for real-time communication between regular users, drivers, and the backend system. It includes information on connecting, sending, and receiving data through WebSocket channels for both users and drivers.

## **WebSocket Connection Overview**

This project uses WebSockets to provide real-time updates to users and drivers. The WebSocket connections are authenticated using JWT (JSON Web Tokens) and are used for various purposes, such as updating the status of bookings, notifying drivers about new available bookings, and sending OTPs for trip confirmations.

---

## **General WebSocket Structure**

To establish a WebSocket connection, a client needs to provide a valid JWT token in the headers, as these connections are secured by middleware for regular users and drivers.

### **WebSocket URL Format**

- **User WebSocket**: `ws://<host>/ws/bookings/`
- **Driver WebSocket**: `ws://<host>/ws/driver/bookings/`
- **Driver Available Bookings**: `ws://<host>/ws/driver/available_bookings/`

### **JWT Authentication Middleware**

The WebSocket connection requires the JWT token to authenticate users or drivers:

- **Regular Users**: Use the `JWTAuthMiddleware`.
- **Drivers**: Use the `DriverJWTAuthMiddleware`.

When connecting, include the JWT token as a part of the WebSocket connection headers.

---

## **WebSocket for Regular Users**

### **Endpoint**: `/ws/bookings/`

This WebSocket channel allows regular users to receive real-time updates on their bookings, such as status changes and OTP notifications.

### **Usage**

1. **Connect to WebSocket**

   - **URL**: `ws://<host>/ws/bookings/`
   - **Method**: `CONNECT`
   - **Headers**:
     - `Authorization`: `Bearer <jwt_access_token>`

2. **Receive Booking Status Update**

   Once connected, users will receive updates on their booking status, such as "pending," "accepted," or "completed."

   **Sample Message Format**:

   ```json
   {
     "booking_id": 123,
     "status": "accepted",
     "message": "Your booking has been accepted by the driver."
   }
   ```

3. **Receive OTP Update**

   When the booking is accepted, the user will also receive the OTP required to start the trip.

   **Sample OTP Message**:

   ```json
   {
     "otp": "123456",
     "message": "Your booking has been accepted. Here is your OTP to start the trip."
   }
   ```

---

## **WebSocket for Drivers**

### **Endpoint 1**: `/ws/driver/bookings/`

This WebSocket channel allows drivers to receive updates about bookings they have accepted, including changes in status or OTP updates.

### **Usage**

1. **Connect to WebSocket**

   - **URL**: `ws://<host>/ws/driver/bookings/`
   - **Method**: `CONNECT`
   - **Headers**:
     - `Authorization`: `Bearer <jwt_access_token>`

2. **Receive Booking Status Update**

   Drivers will receive updates about the status of their assigned bookings.

   **Sample Message Format**:

   ```json
   {
     "booking_id": 123,
     "status": "on_trip",
     "message": "The trip has started. Please proceed to the destination."
   }
   ```

---

### **Endpoint 2**: `/ws/driver/available_bookings/`

This WebSocket channel allows drivers to receive real-time notifications when new bookings are available within their area.

### **Usage**

1. **Connect to WebSocket**

   - **URL**: `ws://<host>/ws/driver/available_bookings/`
   - **Method**: `CONNECT`
   - **Headers**:
     - `Authorization`: `Bearer <jwt_access_token>`

2. **Receive Available Booking Update**

   Drivers will receive updates about new bookings that are available for them to accept.

   **Sample Message Format**:

   ```json
   {
     "booking_id": 456,
     "pickup_location": "123 Street, City",
     "dropoff_location": "456 Avenue, City",
     "estimated_cost": 300.00,
     "message": "A new booking is available."
   }
   ```

---

## **Common WebSocket Events**

### **1. Booking Status Update**

- **Event Trigger**: Sent to both users and drivers when the booking status changes (e.g., when a booking is accepted, started, or completed).
  
- **Message Format**:

```json
{
  "booking_id": 123,
  "status": "on_trip",
  "message": "The trip has started."
}
```

### **2. OTP Update (User)**

- **Event Trigger**: Sent to the user when their booking has been accepted, along with the OTP to start the trip.

- **Message Format**:

```json
{
  "otp": "123456",
  "message": "Your booking has been accepted. Here is your OTP to start the trip."
}
```

### **3. Available Booking Update (Driver)**

- **Event Trigger**: Sent to the driver when a new booking becomes available for them to accept.

- **Message Format**:

```json
{
  "booking_id": 456,
  "pickup_location": "123 Street, City",
  "dropoff_location": "456 Avenue, City",
  "estimated_cost": 300.00,
  "message": "A new booking is available."
}
```

---

## **WebSocket Disconnection**

When the WebSocket connection is closed, the user or driver will be automatically removed from the group, and no more messages will be sent until they reconnect.

### **Example Disconnection Event (Driver)**:

```json
{
  "message": "Driver disconnected from the available bookings group."
}
```

### **Common Disconnection Scenarios**:
- User or driver closes the connection.
- JWT token is expired or invalid, leading to forced disconnection.
- Server shuts down or restarts.

---

## **Error Handling**

### **Connection Errors**

- **401 Unauthorized**: This occurs if the JWT token is invalid or expired when attempting to connect.

  **Message Format**:

  ```json
  {
    "success": false,
    "message": "Invalid or expired token."
  }
  ```

### **400 Bad Request**

- If the request does not follow the expected format, the connection will be rejected.

  **Message Format**:

  ```json
  {
    "success": false,
    "message": "Malformed WebSocket request."
  }
  ```

---

## **Conclusion**

The WebSocket integration enables real-time interaction for both regular users and drivers, providing instant updates on bookings and available rides. Make sure to handle JWT token expiration and reconnections properly to maintain a seamless user experience.