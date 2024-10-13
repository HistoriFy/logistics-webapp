### **Add Driver API**

**Endpoint:** `/api/add-driver/`  
**Method:** `POST`  
**Authentication:** JWT Token required (IsAuthenticated)  
**Description:** This endpoint allows fleet owners to add a new driver to their fleet.

#### Headers:
```plaintext
Authorization: Bearer <JWT-Token>
```

#### Request Body:
```json
{
    "email": "driver@example.com",
    "name": "Driver Name",
    "phone": "+123456789",
    "password": "driverpassword",
    "license_number": "DL1234567890"
}
```

#### Response:

**Success:**
```json
{
    "status": "success",
    "message": "Driver added successfully."
}
```

**Errors:**

- **Unauthorized (401):**
    ```json
    {
        "status": "error",
        "message": "You are not authorized to perform this action."
    }
    ```

- **BadRequest (400):**
    ```json
    {
        "status": "error",
        "message": "Invalid request data."
    }
    ```

- **Other Exceptions:**
    ```json
    {
        "status": "error",
        "message": "An unexpected error occurred."
    }
    ```

---

### **Add Vehicle API**

**Endpoint:** `/api/add-vehicle/`  
**Method:** `POST`  
**Authentication:** JWT Token required (IsAuthenticated)  
**Description:** This endpoint allows fleet owners to add a new vehicle to their fleet.

#### Headers:
```plaintext
Authorization: Bearer <JWT-Token>
```

#### Request Body:
```json
{
    "vehicle_type_id": 1,
    "license_plate": "ABC1234",
    "capacity": 1000,
    "make": "Toyota",
    "model": "HiAce",
    "year": 2021,
    "color": "White"
}
```

#### Response:

**Success:**
```json
{
    "status": "success",
    "message": "Vehicle added successfully."
}
```

**Errors:**

- **Unauthorized (401):**
    ```json
    {
        "status": "error",
        "message": "You are not authorized to perform this action."
    }
    ```

- **BadRequest (400):**
    ```json
    {
        "status": "error",
        "message": "Invalid request data."
    }
    ```

- **Other Exceptions:**
    ```json
    {
        "status": "error",
        "message": "An unexpected error occurred."
    }
    ```

---

### **Assign Vehicle to Driver API**

**Endpoint:** `/api/assign-vehicle/`  
**Method:** `POST`  
**Authentication:** JWT Token required (IsAuthenticated)  
**Description:** This endpoint allows fleet owners to assign a vehicle to a driver.

#### Headers:
```plaintext
Authorization: Bearer <JWT-Token>
```

#### Request Body:
```json
{
    "driver_id": 1,
    "vehicle_id": 2
}
```

#### Response:

**Success:**
```json
{
    "status": "success",
    "message": "Vehicle assigned to driver successfully."
}
```

**Errors:**

- **Unauthorized (401):**
    ```json
    {
        "status": "error",
        "message": "Driver does not belong to you."
    }
    ```

- **Unauthorized (401):**
    ```json
    {
        "status": "error",
        "message": "Vehicle does not belong to you."
    }
    ```

- **BadRequest (400):**
    ```json
    {
        "status": "error",
        "message": "Invalid request data."
    }
    ```

- **Other Exceptions:**
    ```json
    {
        "status": "error",
        "message": "An unexpected error occurred."
    }
    ```

---

### **View Drivers API**

**Endpoint:** `/api/view-drivers/`  
**Method:** `GET`  
**Authentication:** JWT Token required (IsAuthenticated)  
**Description:** This endpoint allows fleet owners to view all drivers in their fleet.

#### Headers:
```plaintext
Authorization: Bearer <JWT-Token>
```

#### Response:

**Success:**
```json
{
    "status": "success",
    "drivers": [
        {
            "driver_id": 1,
            "name": "Driver Name",
            "email": "driver@example.com",
            "phone": "+123456789",
            "license_number": "DL1234567890",
            "status": "active",
            "availability_status": true
        },
        {
            "driver_id": 2,
            "name": "Driver Name 2",
            "email": "driver2@example.com",
            "phone": "+987654321",
            "license_number": "DL0987654321",
            "status": "active",
            "availability_status": false
        }
    ]
}
```

**Errors:**

- **Unauthorized (401):**
    ```json
    {
        "status": "error",
        "message": "You are not authorized to perform this action."
    }
    ```

- **Other Exceptions:**
    ```json
    {
        "status": "error",
        "message": "An unexpected error occurred."
    }
    ```

---

### **View Vehicles API**

**Endpoint:** `/api/view-vehicles/`  
**Method:** `GET`  
**Authentication:** JWT Token required (IsAuthenticated)  
**Description:** This endpoint allows fleet owners to view all vehicles in their fleet.

#### Headers:
```plaintext
Authorization: Bearer <JWT-Token>
```

#### Response:

**Success:**
```json
{
    "status": "success",
    "vehicles": [
        {
            "vehicle_id": 1,
            "license_plate": "ABC1234",
            "vehicle_type": "Pickup Truck",
            "capacity": 1000,
            "make": "Toyota",
            "model": "HiAce",
            "year": 2021,
            "color": "White",
            "driver": "Driver Name"
        },
        {
            "vehicle_id": 2,
            "license_plate": "XYZ5678",
            "vehicle_type": "Van",
            "capacity": 1500,
            "make": "Ford",
            "model": "Transit",
            "year": 2020,
            "color": "Blue",
            "driver": null
        }
    ]
}
```

**Errors:**

- **Unauthorized (401):**
    ```json
    {
        "status": "error",
        "message": "You are not authorized to perform this action."
    }
    ```

- **Other Exceptions:**
    ```json
    {
        "status": "error",
        "message": "An unexpected error occurred."
    }
    ```

---

### **General Notes:**

1. **Authentication:**  
   All API calls require JWT-based authentication using the `Authorization: Bearer <token>` header.

2. **Error Handling:**  
   - The `Unauthorized` exception is raised when a fleet owner attempts to access resources or perform actions that they are not authorized to handle.
   - The `BadRequest` exception is raised for invalid request data, and a proper message is returned to the user.

3. **Transaction Management:**  
   All operations involving database modifications (driver addition, vehicle addition, vehicle assignment) are wrapped in atomic transactions to ensure data consistency.

4. **Validation:**  
   The request data is validated using Django REST Framework serializers before proceeding with the business logic. Errors encountered during validation will raise appropriate `BadRequest` exceptions.

5. **Custom Exception and Response Handling:**  
   Custom exceptions such as `Unauthorized` and `BadRequest` are used along with a decorator-based response handling (`format_response`) to ensure consistent response formatting across all API views.