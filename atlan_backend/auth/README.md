#### **POST** `/register/`

**Description**: Registers a new user, driver, or fleet owner based on the `user_type`.

**Request Body**:

- **user_type** (string, required): The type of user being registered. Possible values: `"user"`, `"driver"`, `"fleet_owner"`.
- **name** (string, required): The name of the user.
- **email** (string, required): The email address of the user.
- **phone** (string, required): The phone number of the user.
- **password** (string, required): The password for the user. This will be hashed before being stored.
- **license_number** (string, required for `"driver"`, optional for others): The license number of the driver.
- **company_name** (string, required for `"fleet_owner"`, optional for others): The company name of the fleet owner.

**Example Request (for a `user`)**:
```json
{
    "user_type": "user",
    "name": "John Doe",
    "email": "johndoe@example.com",
    "phone": "1234567890",
    "password": "strongpassword123"
}
```

**Example Request (for a `driver`)**:
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

**Example Request (for a `fleet_owner`)**:
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
- **Status**: `200 OK`
- **Body**:
```json
{
    "refresh": "refresh_token_string",
    "access": "access_token_string",
    "message": "Registration successful",
    "user_id": 1
}
```

**Error Response**:
- **Status**: `400 Bad Request`
- **Body**:
```json
{
    "message": "Invalid user type."
}
```

---

#### **POST** `/login/`

**Description**: Authenticates a user, driver, or fleet owner based on the provided credentials.

**Request Body**:

- **user_type** (string, required): The type of user logging in. Possible values: `"user"`, `"driver"`, `"fleet_owner"`.
- **email** (string, required): The email of the user.
- **password** (string, required): The password of the user.

**Example Request (for a `user`)**:
```json
{
    "user_type": "user",
    "email": "johndoe@example.com",
    "password": "strongpassword123"
}
```

**Success Response**:
- **Status**: `200 OK`
- **Body**:
```json
{
    "refresh": "refresh_token_string",
    "access": "access_token_string",
    "message": "Login successful"
}
```

**Error Response**:
- **Status**: `401 Unauthorized`
- **Body**:
```json
{
    "message": "Invalid credentials."
}
```