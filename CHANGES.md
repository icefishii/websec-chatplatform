# Recent Changes - Profile Names & User Search & UUIDs

## Summary

Added profile name support, user search functionality, and migrated to UUID-based user IDs for enhanced security.

## ✅ What Changed

### 1. **Profile Names Added** (Security Enhancement)

**Why?** Separates login credentials from display names to prevent username enumeration attacks.

- **username**: Used for login only (never shown to other users)
- **profile_name**: Display name shown to everyone (searchable)

**Example:**

- Login with: `alice_secure` (secret)
- Others see: `Alice Wonderland` (public)

### 2. **UUIDs Instead of Integer IDs** (Security Enhancement)

**Why?** Prevents user enumeration and IDOR attacks.

- **Before**: Sequential IDs (1, 2, 3...) - predictable and enumerable
- **After**: UUIDs (`148fc4c1-0b5f-4367-9099-fa5e16296f2b`) - random and secure

**Security Benefits:**

- ✅ Cannot guess valid user IDs
- ✅ Doesn't reveal user count
- ✅ Makes IDOR attacks much harder
- ✅ Cryptographically secure randomness

### 3. **New Search Endpoint** (Backend Implementation)

**Endpoint:** `GET /api/v1/users/search?q=<query>&limit=<number>`

**Why backend search?**
- ✅ Security: Never exposes full user list to client
- ✅ Performance: Handles thousands of users efficiently
- ✅ Privacy: Users only see what they search for

**Features:**
- Case-insensitive search
- Pagination (max 50 results)
- Requires authentication
- SQL injection protected

### 3. **Updated Registration**

Now requires profile_name:

```json
{
  "username": "alice_secure",      // NEW: Login credential
  "profile_name": "Alice Wonderland", // NEW: Display name
  "password": "SecurePass123!"
}
```

## 📁 Files Modified

1. **backend/src/models.py**
   - Added `profile_name` column to User model
   - **Changed `id` from Integer to UUID**
   - **Updated Session.user_id foreign key to UUID**

2. **backend/src/schemas.py**
   - Updated `UserRegister` to include profile_name
   - Added `UserSearchResult` schema
   - Added validation for profile names
   - **Updated UserResponse and UserSearchResult to use UUID type**

3. **backend/src/main.py**
   - Updated `/register` endpoint
   - Updated `/me` endpoint
   - Added NEW `/users/search` endpoint

4. **backend/USER_SEARCH_API.md** (NEW)
   - Complete documentation for frontend integration

5. **UUID_MIGRATION.md** (NEW)
   - Complete UUID migration documentation and test results

## 🚀 How to Test

### Option 1: Reset Database (Recommended for Development)

```powershell
# Make sure Docker Desktop is running first!
docker compose down -v
docker compose up -d --build
```

### Option 2: Register New Test Users

```bash
# Register user 1
curl -k -X POST https://localhost:8443/api/v1/register \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","profile_name":"Alice Wonderland","password":"SecurePass123!"}'

# Register user 2
curl -k -X POST https://localhost:8443/api/v1/register \
  -H "Content-Type: application/json" \
  -d '{"username":"bob","profile_name":"Bob Builder","password":"SecurePass123!"}'

# Login
curl -k -X POST https://localhost:8443/api/v1/login \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"SecurePass123!"}' \
  -c cookies.txt

# Search users
curl -k "https://localhost:8443/api/v1/users/search?q=bob" -b cookies.txt
```

## 🎯 Next Steps for Frontend

1. **Update Registration Form**
   - Add "Display Name" field
   - Keep username separate

2. **Create Search Component**
   - See `backend/USER_SEARCH_API.md` for React example
   - Implement debouncing (300ms)
   - Show search results with profile_name only

3. **Update User Display**
   - Show profile_name in chat messages
   - Never display login username to other users

## 🔐 Security Notes

### Attack Prevention

| Risk | Mitigation |
|------|------------|
| Username enumeration | Login usernames never exposed in search |
| SQL injection | Parameterized queries + escaped special chars |
| Anonymous scraping | Must be authenticated to search |
| DOS via search spam | Pagination limits + auth requirement |

### Production TODOs

- [ ] Add rate limiting (10 searches/min per user)
- [ ] Add logging for search queries
- [ ] Consider fuzzy search for typos
- [ ] Add "load more" pagination with offset

## 📚 Documentation

- **Complete API Docs**: `backend/USER_SEARCH_API.md`
- **Auth API Docs**: `README_AUTH.md`, `backend/AUTH_API.md`
- **Interactive Docs**: https://localhost:8443/api/v1/docs

---

**Created**: October 4, 2025  
**Breaking Change**: Yes - registration now requires profile_name field
