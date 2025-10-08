const API_BASE = "/api/v1";

export async function sendMessage(recipientId: string, content: string) {
  const res = await fetch(`${API_BASE}/messages`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ recipient_id: recipientId, content }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function getConversations() {
  try {
    // correct path from OpenAPI: /messages/conversations
    const res = await fetch(`${API_BASE}/messages/conversations`, { credentials: "include" });
    if (res.status === 404) {
      console.warn("getConversations: /messages/conversations not found on server, returning empty list");
      return [];
    }
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  } catch (e) {
    console.error("getConversations error:", e);
    return [];
  }
}

/* Use the documented user search endpoint: /users/search?q=... */
export async function findProfilesByName(name: string, limit = 20) {
  if (!name) return [];
  const url = `${API_BASE}/users/search?q=${encodeURIComponent(name)}&limit=${encodeURIComponent(String(limit))}`;
  try {
    const res = await fetch(url, { credentials: "include" });
    if (res.status === 404) {
      // endpoint missing on server, return empty
      return [];
    }
    if (!res.ok) {
      throw new Error(await res.text());
    }
    const data = await res.json();
    // expect array of { id, profile_name }
    if (Array.isArray(data)) return data;
    return [];
  } catch (e) {
    console.warn("findProfilesByName error:", e);
    return [];
  }
}

export async function getConversationMessages(userId: string, limit = 100, offset = 0) {
  const url = new URL(`${API_BASE}/messages/${userId}`, location.origin);
  url.searchParams.set("limit", String(limit));
  url.searchParams.set("offset", String(offset));
  const res = await fetch(url.toString(), { credentials: "include" });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}
