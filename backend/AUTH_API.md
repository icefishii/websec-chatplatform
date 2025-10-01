# Authentication API

This backend provides secure user authentication with session-based cookies.

## Endpoints

### POST `/api/v1/register`

Register a new user account.

**Request Body:**

```json
{
  "username": "string (3-30 chars, alphanumeric + underscore)",
  "password": "string (8-128 chars, must include uppercase, lowercase, digit, special char)"
}
```

**Response (201):**

```json
{
  "id": 1,
  "username": "testuser",
  "created_at": "2025-10-01T14:24:10.399583+00:00"
}
```

**Errors:**

- `400` - Username already exists or validation failed
- `422` - Invalid request body

---

### POST `/api/v1/login`

Login and receive a session cookie.

**Request Body:**

```json
{
  "username": "string",
  "password": "string"
}
```

**Response (200):**

```json
{
  "message": "Login successful"
}
```

**Sets Cookie:**

- `session_token` - HTTPOnly, Secure, SameSite=Lax, 7-day expiration

**Errors:**

- `401` - Invalid username or password

---

### POST `/api/v1/logout`

Logout and invalidate the current session.

**Requires:** Valid session cookie

**Response (200):**

```json
{
  "message": "Logout successful"
}
```

---

### GET `/api/v1/me`

Get information about the currently authenticated user.

**Requires:** Valid session cookie

**Response (200):**

```json
{
  "id": 1,
  "username": "testuser",
  "created_at": "2025-10-01T14:24:10.399583+00:00"
}
```

**Errors:**

- `401` - Not authenticated, invalid session, or session expired

---

## Security Features

### Password Security

- **Bcrypt hashing** with cost factor 12 (4096 iterations)
- **Strong password requirements**:
  - 8-128 characters
  - At least one uppercase letter
  - At least one lowercase letter
  - At least one digit
  - At least one special character

### Session Security

- **Cryptographically secure tokens** (256-bit random)
- **HTTPOnly cookies** (prevents XSS access)
- **Secure flag** (HTTPS only)
- **SameSite=Lax** (CSRF protection)
- **7-day expiration** with automatic cleanup

### Database Security

- **SQLAlchemy ORM** (prevents SQL injection)
- **Parameterized queries** only
- **No raw SQL** from user input

### Input Validation

- **Pydantic models** validate all inputs
- **Username whitelist**: alphanumeric + underscore only
- **Length constraints** on all fields
- **No sensitive data** in responses

## Frontend Integration

### JavaScript/TypeScript Example

```typescript
// Register
const registerResponse = await fetch('/api/v1/register', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  credentials: 'include', // Important: sends/receives cookies
  body: JSON.stringify({
    username: 'alice',
    password: 'SecurePass123!'
  })
});

// Login
const loginResponse = await fetch('/api/v1/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  credentials: 'include',
  body: JSON.stringify({
    username: 'alice',
    password: 'SecurePass123!'
  })
});

// Get current user (session cookie sent automatically)
const meResponse = await fetch('/api/v1/me', {
  credentials: 'include'
});
const user = await meResponse.json();

// Logout
await fetch('/api/v1/logout', {
  method: 'POST',
  credentials: 'include'
});
```

**Important:** Always use `credentials: 'include'` to send/receive cookies!

## Database Schema

### Users Table

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Sessions Table

```sql
CREATE TABLE sessions (
    id SERIAL PRIMARY KEY,
    token VARCHAR(64) UNIQUE NOT NULL,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL
);
```

## Testing with cURL

```bash
# Register
curl -k -X POST https://localhost:8443/api/v1/register \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"SecurePass123!"}'

# Login (save cookie)
curl -k -X POST https://localhost:8443/api/v1/login \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"SecurePass123!"}' \
  -c cookies.txt

# Get current user
curl -k https://localhost:8443/api/v1/me -b cookies.txt

# Logout
curl -k -X POST https://localhost:8443/api/v1/logout -b cookies.txt
```

## Production Checklist

Before deploying to production:

1. ✅ Change database credentials from hardcoded values
2. ✅ Add production domain to CORS origins in `main.py`
3. ✅ Use real SSL certificates (Let's Encrypt)
4. ⚠️ **TODO:** Add rate limiting to prevent brute force attacks
5. ⚠️ **TODO:** Add security headers in nginx (HSTS, CSP, etc.)
6. ⚠️ **TODO:** Set up logging/monitoring for security events
7. ⚠️ **TODO:** Implement account lockout after failed login attempts
8. ⚠️ **TODO:** Add email verification (if adding email field)

## Interactive API Documentation

FastAPI provides automatic interactive documentation:

- **Swagger UI**: http://localhost:8000/docs (when running backend standalone)
- **ReDoc**: http://localhost:8000/redoc

Note: Through nginx, these are available at `/api/v1/docs` and `/api/v1/redoc`
