const API_BASE = '/api/v1';

export async function sendMessage(recipientId: string, content: string) {
  const res = await fetch(`${API_BASE}/messages`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({ recipient_id: recipientId, content }),
  });
  if (!res.ok) throw await res.json();
  return res.json();
}

export async function getConversations() {
  const res = await fetch(`${API_BASE}/messages/conversations`, {
    credentials: 'include',
  });
  if (!res.ok) throw await res.json();
  return res.json();
}

export async function getConversationMessages(
  userId: string,
  limit = 100,
  offset = 0
) {
  const params = new URLSearchParams({
    limit: limit.toString(),
    offset: offset.toString(),
  });
  const res = await fetch(`${API_BASE}/messages/${userId}?${params.toString()}`, {
    credentials: 'include',
  });
  if (!res.ok) throw await res.json();
  return res.json();
}
