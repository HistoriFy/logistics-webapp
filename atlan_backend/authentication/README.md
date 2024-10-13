#### **Register a New User, Driver, or Fleet Owner**

**Endpoint**: `/register/`

**Method**: `POST`

**Description**: This endpoint allows the registration of a new user, driver, or fleet owner based on the `user_type` provided. Depending on the `user_type`, additional fields such as `license_number` for drivers or `company_name` for fleet owners are required.

**Request Body Parameters**:
- `user_type` (string, required): The type of user to be registered. Possible values are `"user"`, `"driver"`, or `"fleet_owner"`.
- `name` (string, required): The full name of the user.
- `email` (string, required): The user's email address.
- `phone` (string, required): The user's phone number.
- `password` (string, required): The user's password, which will be securely hashed.
- `license_number` (string, required for `"driver"` only): The driver's license number. This field is required if registering a driver.
- `company_name` (string, required for `"fleet_owner"` only): The fleet owner's company name. This field is required if registering a fleet owner.

**Example Requests**:
- **User Registration**:
  ```json
  {
      "user_type": "user",
      "name": "John Doe",
      "email": "johndoe@example.com",
      "phone": "1234567890",
      "password": "strongpassword123"
  }
  ```

- **Driver Registration**:
  ```json
  {
      "user_type": "driver",
      "name": "Jane Driver",
      "email": "janedriver@example.com",
      "phone": "0987654321",
      "password": "anotherpassword123",
      "license_number": "DRIV123456"
  }
  ```

- **Fleet Owner Registration**:
  ```json
  {
      "user_type": "fleet_owner",
      "name": "Alice Fleet",
      "email": "alicefleet@example.com",
      "phone": "5432167890",
      "password": "securepassword123",
      "company_name": "FleetX"
  }
  ```

**Success Response**:
```json
{
    "refresh": "refresh_token_string",
    "access": "access_token_string",
    "message": "Registration successful",
    "user_id": 1
}
```

**Error Response**:
- **Invalid `user_type`**:
  ```json
  {
      "detail": {
          "user_type": ["Invalid user type."]
      }
  }
  ```

- **Missing or Invalid Fields**:
  ```json
  {
      "detail": {
          "email": ["This field is required."],
          "password": ["This field is required."]
      }
  }
  ```

---

#### **Login**

**Endpoint**: `/login/`

**Method**: `POST`

**Description**: This endpoint handles authentication for a user, driver, or fleet owner by verifying the provided credentials (email and password).

**Request Body Parameters**:
- `user_type` (string, required): The type of user logging in. Possible values are `"user"`, `"driver"`, or `"fleet_owner"`.
- `email` (string, required): The email address of the user.
- `password` (string, required): The user's password.

**Example Request**:
```json
{
    "user_type": "user",
    "email": "johndoe@example.com",
    "password": "strongpassword123"
}
```

**Success Response**:
```json
{
    "refresh": "refresh_token_string",
    "access": "access_token_string",
    "message": "Login successful"
}
```

**Error Response**:
- **Invalid Credentials**:
  ```json
  {
      "detail": "Invalid credentials."
  }
  ```

- **Invalid `user_type`**:
  ```json
  {
      "detail": {
          "user_type": ["Invalid user type."]
      }
  }
  ```

---

### Custom Exceptions

- **BadRequest**: Raised when the request is invalid or contains incorrect/malformed data (e.g., missing required fields, invalid `user_type`). This exception returns a 400 status code.

  **Example**:
  ```json
  {
      "detail": {
          "email": ["This field is required."],
          "password": ["This field is required."]
      }
  }
  ```

- **Unauthorized**: Raised when the user provides incorrect login credentials or tries to access a protected resource without proper authorization. This exception returns a 401 status code.

  **Example**:
  ```json
  {
      "detail": "Invalid credentials."
  }
  ```