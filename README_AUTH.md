# WebSec Chat Platform - Authentication API

Quick reference for integrating the authentication API into the frontend.

## 🚀 Quick Start

All endpoints are available at `https://localhost:8443/api/v1/` through the nginx reverse proxy.

**Important:** Always include `credentials: 'include'` in fetch requests to send/receive cookies!

## 📡 API Endpoints

### Register New User

```typescript
const response = await fetch('/api/v1/register', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  credentials: 'include',
  body: JSON.stringify({
    username: 'alice',      // 3-30 chars, alphanumeric + underscore
    password: 'SecurePass123!'  // See password requirements below
  })
});

// Response (201):
// { "id": 1, "username": "alice", "created_at": "2025-10-01T14:24:10.399583+00:00" }

// Errors:
// 400 - Username already exists or validation failed
// 422 - Invalid request body
```

**Password Requirements:**

- 8-128 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one digit
- At least one special character (!@#$%^&*(),.?":{}|<>)

---

### Login

```typescript
const response = await fetch('/api/v1/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  credentials: 'include',  // Required to receive session cookie!
  body: JSON.stringify({
    username: 'alice',
    password: 'SecurePass123!'
  })
});

// Response (200):
// { "message": "Login successful" }
// Sets HTTPOnly session cookie (automatically sent with future requests)

// Errors:
// 401 - Invalid username or password
```

**Session Cookie Details:**

- Name: `session_token`
- HTTPOnly: Yes (not accessible via JavaScript - secure!)
- Secure: Yes (HTTPS only)
- SameSite: Lax (CSRF protection)
- Expiration: 7 days

---

### Get Current User

```typescript
const response = await fetch('/api/v1/me', {
  credentials: 'include'  // Sends session cookie automatically
});

const user = await response.json();

// Response (200):
// { "id": 1, "username": "alice", "created_at": "2025-10-01T14:24:10.399583+00:00" }

// Errors:
// 401 - Not authenticated, invalid session, or session expired
```

---

### Logout

```typescript
const response = await fetch('/api/v1/logout', {
  method: 'POST',
  credentials: 'include'
});

// Response (200):
// { "message": "Logout successful" }
// Invalidates session in database and clears cookie
```

---

## 🎯 Complete React/Next.js Example

```typescript
'use client';

import { useState } from 'react';

interface User {
  id: number;
  username: string;
  created_at: string;
}

export default function AuthExample() {
  const [user, setUser] = useState<User | null>(null);
  const [error, setError] = useState('');

  const register = async (username: string, password: string) => {
    try {
      const res = await fetch('/api/v1/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ username, password })
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || 'Registration failed');
      }

      const newUser = await res.json();
      setUser(newUser);
      setError('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Registration failed');
    }
  };

  const login = async (username: string, password: string) => {
    try {
      const res = await fetch('/api/v1/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ username, password })
      });

      if (!res.ok) {
        throw new Error('Invalid credentials');
      }

      // Fetch user info after successful login
      await getCurrentUser();
      setError('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed');
    }
  };

  const getCurrentUser = async () => {
    try {
      const res = await fetch('/api/v1/me', {
        credentials: 'include'
      });

      if (!res.ok) {
        throw new Error('Not authenticated');
      }

      const userData = await res.json();
      setUser(userData);
      setError('');
    } catch (err) {
      setUser(null);
      setError(err instanceof Error ? err.message : 'Failed to get user');
    }
  };

  const logout = async () => {
    try {
      await fetch('/api/v1/logout', {
        method: 'POST',
        credentials: 'include'
      });

      setUser(null);
      setError('');
    } catch (err) {
      setError('Logout failed');
    }
  };

  return (
    <div>
      {error && <div className="error">{error}</div>}
      
      {user ? (
        <div>
          <p>Welcome, {user.username}!</p>
          <button onClick={logout}>Logout</button>
        </div>
      ) : (
        <div>
          <button onClick={() => login('alice', 'SecurePass123!')}>
            Login
          </button>
          <button onClick={() => register('alice', 'SecurePass123!')}>
            Register
          </button>
        </div>
      )}
    </div>
  );
}
```

---

## 🔒 Security Notes

### Session Management

- Sessions are stored in PostgreSQL database
- Session tokens are cryptographically secure (256-bit random)
- Tokens are stored in HTTPOnly cookies (protected from XSS)
- Sessions expire after 7 days
- Logout invalidates the session immediately

### What You Don't Need To Do

- ❌ No manual token storage in localStorage (XSS vulnerable)
- ❌ No Authorization headers to manage
- ❌ No manual cookie handling
- ✅ Browser handles everything automatically with `credentials: 'include'`

### Error Handling

Always check response status codes:

```typescript
const response = await fetch('/api/v1/login', { /* ... */ });

if (!response.ok) {
  if (response.status === 401) {
    // Unauthorized - invalid credentials or session expired
    console.log('Please log in');
  } else if (response.status === 400) {
    // Bad request - validation failed
    const error = await response.json();
    console.log('Validation error:', error.detail);
  }
}
```

---

## 🧪 Testing with cURL

```bash
# Register
curl -k -X POST https://localhost:8443/api/v1/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"SecurePass123!"}'

# Login and save cookie
curl -k -X POST https://localhost:8443/api/v1/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"SecurePass123!"}' \
  -c cookies.txt

# Get current user (uses saved cookie)
curl -k https://localhost:8443/api/v1/me -b cookies.txt

# Logout
curl -k -X POST https://localhost:8443/api/v1/logout -b cookies.txt
```

---

## 🐛 Common Issues

### "Not authenticated" error

- Make sure you're using `credentials: 'include'` in fetch
- Check that login was successful before calling `/me`
- Session may have expired (7 days)

### CORS errors

- The backend allows `http://localhost:3000` and `https://localhost`
- Make sure you're accessing through the correct origin
- Always use relative URLs (`/api/v1/...`) not absolute URLs

### "Invalid username or password"

- Username and password are case-sensitive
- Check password meets all requirements (uppercase, lowercase, digit, special char)

---

## 📚 Additional Resources

- **Interactive API Docs**: https://localhost:8443/api/v1/docs
- **Backend Source**: `backend/src/main.py`
- **Database Models**: `backend/src/models.py`
- **Validation Schemas**: `backend/src/schemas.py`

---

## 🔧 Development Setup

```bash
# Start all services
docker compose up -d --build

# View backend logs
docker compose logs -f backend

# Stop all services
docker compose down
```

Backend runs on port 8000 internally, but access it through nginx:

- **Development**: https://localhost:8443/api/v1/
- **API Docs**: https://localhost:8443/api/v1/docs
