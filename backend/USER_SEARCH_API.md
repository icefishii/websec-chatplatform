# User Search API

New endpoints for profile names and user search functionality.

## 🔒 Security Design

**Why separate username and profile_name?**

- **username**: Used for login only, never exposed to other users (prevents enumeration attacks)
- **profile_name**: Display name shown to other users, searchable (like Discord display names)

This separation prevents attackers from learning valid login usernames through search.

---

## 📡 API Endpoints

### Updated: POST `/api/v1/register`

Registration now requires a profile name in addition to username.

**Request Body:**

```json
{
  "username": "alice_secure",           // Login credential (3-30 chars, alphanumeric + underscore)
  "profile_name": "Alice Wonderland",   // Display name (3-30 chars, letters, numbers, spaces, ._-)
  "password": "SecurePass123!"
}
```

**Response (201):**

```json
{
  "id": 1,
  "username": "alice_secure",
  "profile_name": "Alice Wonderland",
  "created_at": "2025-10-04T14:24:10.399583+00:00"
}
```

**Profile Name Validation:**

- 3-30 characters
- Allowed: letters, numbers, spaces, periods, underscores, hyphens
- Leading/trailing whitespace is trimmed
- Cannot be empty after trimming

---

### Updated: GET `/api/v1/me`

Now includes profile_name in the response.

**Response (200):**

```json
{
  "id": 1,
  "username": "alice_secure",
  "profile_name": "Alice Wonderland",
  "created_at": "2025-10-04T14:24:10.399583+00:00"
}
```

---

### NEW: GET `/api/v1/users/search`

Search for users by profile name (case-insensitive).

**Query Parameters:**

- `q` (required): Search query (1-50 characters)
- `limit` (optional): Max results (default 20, max 50)

**Example Request:**

```typescript
const response = await fetch('/api/v1/users/search?q=alice&limit=10', {
  credentials: 'include'  // Authentication required!
});

const users = await response.json();
```

**Response (200):**

```json
[
  {
    "id": 1,
    "profile_name": "Alice Wonderland"
  },
  {
    "id": 5,
    "profile_name": "Alice Cooper"
  }
]
```

**Security Features:**

- ✅ **Authentication required** - prevents anonymous user enumeration
- ✅ **Only returns profile_name and id** - login username never exposed
- ✅ **Case-insensitive search** - finds "Alice", "alice", "ALICE"
- ✅ **SQL injection protection** - special chars escaped (%, _)
- ✅ **Pagination** - limits results to prevent DOS
- ✅ **Query validation** - length constraints prevent abuse

**Errors:**

- `400` - Empty query or query too long (>50 chars)
- `401` - Not authenticated (no session cookie)

---

## 🎯 Frontend Integration Example

### Search Component (React/Next.js)

```typescript
'use client';

import { useState, useEffect } from 'react';

interface SearchResult {
  id: number;
  profile_name: string;
}

export default function UserSearch() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);

  // Debounced search
  useEffect(() => {
    if (query.length === 0) {
      setResults([]);
      return;
    }

    const timer = setTimeout(async () => {
      setLoading(true);
      try {
        const response = await fetch(
          `/api/v1/users/search?q=${encodeURIComponent(query)}&limit=20`,
          { credentials: 'include' }
        );

        if (response.ok) {
          const data = await response.json();
          setResults(data);
        } else if (response.status === 401) {
          console.error('Not authenticated');
        }
      } catch (error) {
        console.error('Search failed:', error);
      } finally {
        setLoading(false);
      }
    }, 300); // Wait 300ms after user stops typing

    return () => clearTimeout(timer);
  }, [query]);

  return (
    <div>
      <input
        type="text"
        placeholder="Search users..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        maxLength={50}
      />

      {loading && <div>Searching...</div>}

      <ul>
        {results.map((user) => (
          <li key={user.id}>
            {user.profile_name} (ID: {user.id})
          </li>
        ))}
      </ul>
    </div>
  );
}
```

### Registration Form Update

```typescript
const register = async (username: string, profileName: string, password: string) => {
  const response = await fetch('/api/v1/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({
      username: username,        // Login credential (not searchable)
      profile_name: profileName, // Display name (searchable)
      password: password
    })
  });

  if (response.ok) {
    const user = await response.json();
    console.log('Registered:', user);
  }
};
```

---

## 🧪 Testing with cURL

### Register with Profile Name

```bash
curl -k -X POST https://localhost:8443/api/v1/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alice_secure",
    "profile_name": "Alice Wonderland",
    "password": "SecurePass123!"
  }'
```

### Search Users

```bash
# Login first to get session cookie
curl -k -X POST https://localhost:8443/api/v1/login \
  -H "Content-Type: application/json" \
  -d '{"username":"alice_secure","password":"SecurePass123!"}' \
  -c cookies.txt

# Search for users
curl -k "https://localhost:8443/api/v1/users/search?q=alice&limit=10" \
  -b cookies.txt

# Search with special characters (automatically escaped)
curl -k "https://localhost:8443/api/v1/users/search?q=alice%20w" \
  -b cookies.txt
```

---

## 🔐 Security Best Practices

### For Frontend Developers

1. **Never display usernames** in search results - use profile_name only
2. **Implement debouncing** - don't search on every keystroke (prevents DOS)
3. **Handle 401 errors** - redirect to login if session expires
4. **Validate input** - enforce max length on search input (50 chars)
5. **Use relative URLs** - `/api/v1/users/search` not `http://backend:8000/users/search`

### Attack Prevention

| Attack Vector | Protection |
|--------------|------------|
| Username enumeration | Login usernames never exposed, only profile names |
| SQL injection | Parameterized queries + special char escaping |
| DOS via search spam | Requires authentication + pagination limits |
| Brute force search | TODO: Add rate limiting (see production notes) |
| Anonymous enumeration | Must be logged in to search |

---

## 🚀 Database Migration

The new `profile_name` column is added to the `users` table.

**If you have existing data:**

You need to add a migration or manually update existing users:

```sql
-- Add column (done automatically by SQLAlchemy)
ALTER TABLE users ADD COLUMN profile_name VARCHAR(50);

-- Set default for existing users (example)
UPDATE users SET profile_name = username WHERE profile_name IS NULL;

-- Make column non-nullable
ALTER TABLE users ALTER COLUMN profile_name SET NOT NULL;

-- Add index for search performance
CREATE INDEX idx_users_profile_name ON users(profile_name);
```

**For clean start (development):**

```bash
# Reset database
docker compose down -v
docker compose up -d --build
```

---

## 📋 Production TODO

Before deploying:

1. ✅ **Add rate limiting** to `/users/search` endpoint
   - Recommend: 10 searches per minute per user
   - Use middleware or FastAPI-Limiter library

2. ✅ **Add full-text search** for better performance at scale
   - PostgreSQL: Use `ts_vector` and GIN index
   - Or integrate Elasticsearch

3. ✅ **Add profile name uniqueness** (optional)
   - Decide if duplicate display names are allowed
   - If not: Add unique constraint and update validation

4. ✅ **Log search queries** for abuse detection
   - Monitor for suspicious patterns
   - Detect user enumeration attempts

5. ✅ **Add pagination offset** parameter
   - Current implementation only has limit
   - Add `offset` for "load more" functionality

6. ✅ **Consider fuzzy search** for typo tolerance
   - Use `pg_trgm` extension for PostgreSQL
   - Or Levenshtein distance

---

## 🐛 Common Issues

### "profile_name not found" error

- You have existing users in database created before adding profile_name
- Solution: Reset database or run migration SQL above

### Search returns empty results

- Check user is authenticated (session cookie sent)
- Verify profile_name is set for users in database
- Try exact match first before partial search

### CORS errors on search

- Make sure you're using relative URLs (`/api/v1/users/search`)
- Include `credentials: 'include'` in fetch
- Check nginx proxy is routing correctly

---

## 📚 Related Files

- **API Implementation**: `backend/src/main.py` (lines 198-255)
- **Database Model**: `backend/src/models.py` (User class)
- **Validation Schemas**: `backend/src/schemas.py` (UserRegister, UserSearchResult)
- **Original Auth Docs**: `README_AUTH.md`, `backend/AUTH_API.md`

---

**Last Updated**: October 4, 2025  
**API Version**: 1.0
