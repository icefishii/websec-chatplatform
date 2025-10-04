# Messaging API

Simple 1-on-1 messaging system for the WebSec Chat Platform.

## 📡 API Endpoints

### POST `/api/v1/messages`

Send a message to another user.

**Authentication**: Required (session cookie)

**Request Body:**
```json
{
  "recipient_id": "f38f7f0c-c750-4f6d-86ff-6bc8224ac5ba",
  "content": "Hey, how are you?"
}
```

**Validation:**
- `recipient_id`: Must be valid UUID of existing user
- `content`: 1-5000 characters, whitespace trimmed

**Response (201):**
```json
{
  "id": "a31d5370-1b45-442f-9325-2dcfa663d32b",
  "sender_id": "cf6e9305-8d54-4319-8fd2-822182ddeed2",
  "recipient_id": "f38f7f0c-c750-4f6d-86ff-6bc8224ac5ba",
  "content": "Hey, how are you?",
  "created_at": "2025-10-04T16:50:44.123456+00:00"
}
```

**Errors:**
- `400` - Cannot send message to yourself
- `401` - Not authenticated
- `404` - Recipient not found
- `422` - Invalid request body (content too long, empty, etc.)

**Security Features:**
- ✅ Authentication required
- ✅ Prevents self-messaging
- ✅ Validates recipient exists
- ✅ Content length limit (prevents DOS)
- ✅ Input sanitization (XSS prevention)

---

### GET `/api/v1/messages/conversations`

Get list of all users you've had conversations with, sorted by most recent message.

**Authentication**: Required (session cookie)

**Response (200):**
```json
[
  {
    "id": "f38f7f0c-c750-4f6d-86ff-6bc8224ac5ba",
    "profile_name": "Bob Builder",
    "last_message": "Hi Alice! I'm doing great, thanks for asking!",
    "last_message_time": "2025-10-04T16:51:04.123456+00:00"
  },
  {
    "id": "336649b7-d395-448f-84ad-241fb9544312",
    "profile_name": "Charlie Chaplin",
    "last_message": "See you tomorrow!",
    "last_message_time": "2025-10-03T14:20:15.123456+00:00"
  }
]
```

**Features:**
- ✅ Shows only conversations you're part of
- ✅ Sorted by most recent message first
- ✅ Last message preview (truncated to 100 chars)
- ✅ Returns profile_name (not login username)

**Use Case**: Display conversation list in sidebar/inbox

---

### GET `/api/v1/messages/{user_id}`

Get all messages between you and a specific user, ordered chronologically (oldest first).

**Authentication**: Required (session cookie)

**Path Parameters:**
- `user_id` (UUID): The other user's ID

**Query Parameters:**
- `limit` (optional): Max messages to return (default 100, max 500)
- `offset` (optional): Skip first N messages for pagination (default 0)

**Example Request:**
```typescript
const response = await fetch(
  '/api/v1/messages/f38f7f0c-c750-4f6d-86ff-6bc8224ac5ba?limit=100',
  { credentials: 'include' }
);
```

**Response (200):**
```json
[
  {
    "id": "a31d5370-1b45-442f-9325-2dcfa663d32b",
    "sender_id": "cf6e9305-8d54-4319-8fd2-822182ddeed2",
    "recipient_id": "f38f7f0c-c750-4f6d-86ff-6bc8224ac5ba",
    "content": "Hey Bob, how are you?",
    "created_at": "2025-10-04T16:50:44.123456+00:00"
  },
  {
    "id": "b42e6481-2c56-553g-a436-3edgb774e13c",
    "sender_id": "cf6e9305-8d54-4319-8fd2-822182ddeed2",
    "recipient_id": "f38f7f0c-c750-4f6d-86ff-6bc8224ac5ba",
    "content": "Looking forward to hearing from you!",
    "created_at": "2025-10-04T16:50:52.123456+00:00"
  },
  {
    "id": "c53f7592-3d67-664h-b547-4fehc885f24d",
    "sender_id": "f38f7f0c-c750-4f6d-86ff-6bc8224ac5ba",
    "recipient_id": "cf6e9305-8d54-4319-8fd2-822182ddeed2",
    "content": "Hi Alice! I'm doing great, thanks for asking!",
    "created_at": "2025-10-04T16:51:04.123456+00:00"
  }
]
```

**Errors:**
- `401` - Not authenticated
- `404` - User not found

**Security Features:**
- ✅ Only returns messages where you're sender or recipient
- ✅ Cannot read other people's conversations
- ✅ Pagination support for large conversations

**Use Case**: Display full chat history when user opens a conversation

---

## 🎯 Frontend Integration Examples

### Send Message Component

```typescript
'use client';

import { useState } from 'react';

interface SendMessageProps {
  recipientId: string;
  onMessageSent?: () => void;
}

export default function SendMessage({ recipientId, onMessageSent }: SendMessageProps) {
  const [content, setContent] = useState('');
  const [sending, setSending] = useState(false);

  const sendMessage = async () => {
    if (!content.trim() || sending) return;

    setSending(true);
    try {
      const response = await fetch('/api/v1/messages', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          recipient_id: recipientId,
          content: content
        })
      });

      if (response.ok) {
        setContent('');
        onMessageSent?.();
      } else if (response.status === 400) {
        const error = await response.json();
        alert(error.detail);
      }
    } catch (error) {
      console.error('Failed to send message:', error);
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="flex gap-2">
      <input
        type="text"
        value={content}
        onChange={(e) => setContent(e.target.value)}
        onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
        placeholder="Type a message..."
        maxLength={5000}
        disabled={sending}
        className="flex-1 px-4 py-2 border rounded"
      />
      <button
        onClick={sendMessage}
        disabled={!content.trim() || sending}
        className="px-6 py-2 bg-blue-500 text-white rounded disabled:opacity-50"
      >
        {sending ? 'Sending...' : 'Send'}
      </button>
    </div>
  );
}
```

### Conversations List Component

```typescript
'use client';

import { useState, useEffect } from 'react';

interface Conversation {
  id: string;
  profile_name: string;
  last_message: string;
  last_message_time: string;
}

export default function ConversationsList() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadConversations();
  }, []);

  const loadConversations = async () => {
    try {
      const response = await fetch('/api/v1/messages/conversations', {
        credentials: 'include'
      });

      if (response.ok) {
        const data = await response.json();
        setConversations(data);
      }
    } catch (error) {
      console.error('Failed to load conversations:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Loading conversations...</div>;

  return (
    <div className="space-y-2">
      <h2 className="text-xl font-bold">Messages</h2>
      {conversations.length === 0 ? (
        <p className="text-gray-500">No conversations yet</p>
      ) : (
        conversations.map((conv) => (
          <div
            key={conv.id}
            className="p-4 border rounded hover:bg-gray-50 cursor-pointer"
            onClick={() => window.location.href = `/chat/${conv.id}`}
          >
            <div className="font-semibold">{conv.profile_name}</div>
            <div className="text-sm text-gray-600 truncate">
              {conv.last_message}
            </div>
            <div className="text-xs text-gray-400">
              {new Date(conv.last_message_time).toLocaleString()}
            </div>
          </div>
        ))
      )}
    </div>
  );
}
```

### Chat Window Component

```typescript
'use client';

import { useState, useEffect } from 'react';

interface Message {
  id: string;
  sender_id: string;
  recipient_id: string;
  content: string;
  created_at: string;
}

interface ChatWindowProps {
  userId: string;
  currentUserId: string;
}

export default function ChatWindow({ userId, currentUserId }: ChatWindowProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadMessages();
    // Optional: Set up polling or WebSocket for real-time updates
    const interval = setInterval(loadMessages, 5000);
    return () => clearInterval(interval);
  }, [userId]);

  const loadMessages = async () => {
    try {
      const response = await fetch(`/api/v1/messages/${userId}`, {
        credentials: 'include'
      });

      if (response.ok) {
        const data = await response.json();
        setMessages(data);
      }
    } catch (error) {
      console.error('Failed to load messages:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Loading messages...</div>;

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto p-4 space-y-2">
        {messages.map((msg) => {
          const isOwnMessage = msg.sender_id === currentUserId;
          return (
            <div
              key={msg.id}
              className={`flex ${isOwnMessage ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-xs px-4 py-2 rounded-lg ${
                  isOwnMessage
                    ? 'bg-blue-500 text-white'
                    : 'bg-gray-200 text-black'
                }`}
              >
                <div>{msg.content}</div>
                <div className="text-xs opacity-70 mt-1">
                  {new Date(msg.created_at).toLocaleTimeString()}
                </div>
              </div>
            </div>
          );
        })}
      </div>
      {/* Add SendMessage component here */}
    </div>
  );
}
```

---

## 🔐 Security Features

### Authentication & Authorization

| Feature | Implementation |
|---------|----------------|
| Authentication required | All endpoints require valid session cookie |
| Authorization checks | Can only read/send messages you're involved in |
| Self-messaging prevention | Cannot send messages to yourself |
| Recipient validation | Recipient must exist before sending |

### Input Validation

| Field | Validation |
|-------|------------|
| Content length | 1-5000 characters |
| Empty messages | Whitespace-only messages rejected |
| UUID validation | recipient_id must be valid UUID |
| XSS prevention | Input sanitized, React auto-escapes |

### DOS Prevention

| Measure | Limit |
|---------|-------|
| Message length | Max 5000 characters |
| Conversation pagination | Max 500 messages per request |
| Database indexes | Fast queries on sender_id, recipient_id, created_at |

**TODO for Production:**
- Add rate limiting (e.g., 10 messages/minute per user)
- Add message delivery status/read receipts
- Consider adding WebSocket for real-time updates

---

## 📊 Database Schema

### Messages Table

```sql
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sender_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    recipient_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content VARCHAR(5000) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_messages_sender ON messages(sender_id);
CREATE INDEX idx_messages_recipient ON messages(recipient_id);
CREATE INDEX idx_messages_created_at ON messages(created_at);
```

---

## 🧪 Testing with cURL

### Send Message

```bash
# Login first
curl -k -X POST https://localhost:8443/api/v1/login \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"SecurePass123!"}' \
  -c cookies.txt

# Send message
curl -k -X POST https://localhost:8443/api/v1/messages \
  -H "Content-Type: application/json" \
  -d '{"recipient_id":"f38f7f0c-c750-4f6d-86ff-6bc8224ac5ba","content":"Hello!"}' \
  -b cookies.txt
```

### Get Conversations

```bash
curl -k https://localhost:8443/api/v1/messages/conversations -b cookies.txt
```

### Get Conversation History

```bash
curl -k "https://localhost:8443/api/v1/messages/f38f7f0c-c750-4f6d-86ff-6bc8224ac5ba?limit=50" \
  -b cookies.txt
```

---

## 🚀 Future Enhancements (Out of Scope)

These features are NOT implemented but could be added later:

- ❌ Group chats
- ❌ Message editing
- ❌ Message deletion
- ❌ Read receipts
- ❌ Typing indicators
- ❌ File attachments
- ❌ Message reactions
- ❌ WebSocket for real-time updates
- ❌ Push notifications

The current implementation is intentionally simple and secure for a basic 1-on-1 chat.

---

## 📚 Related Documentation

- **Authentication**: `README_AUTH.md`, `AUTH_API.md`
- **User Search**: `USER_SEARCH_API.md`
- **UUID Migration**: `UUID_MIGRATION.md`
- **Interactive API Docs**: https://localhost:8443/api/v1/docs

---

**Last Updated**: October 4, 2025  
**API Version**: 1.0
