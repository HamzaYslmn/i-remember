# i-remember API

A temporary data storage API service that allows you to store, retrieve, update and delete data with automatic expiration. Perfect for temporary data sharing or caching needs.

## Features

- 🪙 **FREE**: Free short-term data storage
- 🕐 **Automatic Expiration**: Data automatically expires after specified time (1 minute to 7 days)
- 🔐 **JWT Authentication**: Secure access with JSON Web Tokens
- 🌐 **IP-based Access Control**: One document per IP address
- 📝 **CRUD Operations**: Full Create, Read, Update, Delete support
- ⚡ **FastAPI**: High-performance async API
- 🐳 **Docker Ready**: Containerized deployment

## API Documentation

### Base URL
[https://i-remember.onrender.com/](https://i-remember.onrender.com/)

## Endpoints

### 1. Create Document

Creates a new temporary document with automatic expiration.

**Endpoint:** `POST /i-remember`

**Request Body:**
```json
{
  "data": {
    "key": "value"
  },
  "valid": 60
}
```

**Parameters:**
- `data` (object, required): Any JSON object containing your data
- `valid` (integer, required): Expiration time in minutes (1-10080, default: 1)
  - Minimum: 1 minute
  - Maximum: 10080 minutes (7 days)

---

### 2. Get Document

Retrieves the stored document.

**Endpoint:** `GET /i-remember`

**Headers:**
- `Authorization`: JWT token (required)

---

### 3. Update Document

Updates the stored document and optionally extends expiration. (now + minutes)

**Endpoint:** `PUT /i-remember`

**Headers:**
- `Authorization`: JWT token (required)

**Request Body:**
```json
{
  "data": {
    "location": "Ankara",
    "temperature": 22
  },
  "valid": 120
}
```

**Parameters:**
- `data` (object, required): New data to replace existing data
- `valid` (integer, optional): New expiration time in minutes (1-10080)

---

### 4. Delete Document

Deletes the stored document.

**Endpoint:** `DELETE /i-remember`

**Headers:**
- `Authorization`: JWT token (required)

**Request Body:**
```json
{"Authorization": "<your_jwt_token>"}
```

---

### 5. Health Check

Check API status.

**Endpoint:** `GET /status`

**Response:**
- **Status:** 200 OK
- **Body:**
```json
{
  "status": "online",
  "output": "Welcome to the HamzaYslmn API Service! 🏔️",
  "message": "Or perhaps you're looking for the answer to the ultimate question of life, the universe, and everything? 🌌"
}
```

## Data Types

### Request/Response Data Types

| Field | Type | Required | Description | Constraints |
|-------|------|----------|-------------|-------------|
| `data` | object | Yes | Any valid JSON object | No specific structure required |
| `valid` | integer | No | Expiration time in minutes | 1 ≤ value ≤ 10080 |
| `Authorization` | string | Yes (except POST) | JWT token from POST response | Valid JWT format |

---

Common HTTP status codes:
- `200`: Success
- `201`: Created successfully
- `400`: Bad request (invalid data, IP already has document)
- `401`: Unauthorized (invalid JWT)
- `500`: Internal server error

## Rate Limiting

- Two documents per IP address
- Document automatically expires based on `valid` parameter
- JWT tokens have the same expiration as the document, auto delete after expiration. You can extend the expiration by updating the document.

---

## License

This project is licensed under the AFFERO License - see the LICENSE file for details.
