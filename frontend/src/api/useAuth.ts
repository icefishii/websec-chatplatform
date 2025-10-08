import { ref } from "vue";
import type { AuthUser } from "./utils";

const currentUser = ref<AuthUser | null>(null);
let pendingFetch: Promise<AuthUser | null> | null = null;

export async function fetchCurrentUser(force = false): Promise<AuthUser | null> {
  // If we already have a user and not forcing, return it
  if (!force && currentUser.value !== null) return currentUser.value;
  // If a fetch is already in progress, return the same promise
  if (pendingFetch) return pendingFetch;

  pendingFetch = (async () => {
    try {
      const res = await fetch("/api/v1/me", { credentials: "include" });
      if (res.status === 401) {
        currentUser.value = null;
        return null;
      }
      if (!res.ok) {
        const txt = await res.text();
        throw new Error(txt || res.statusText);
      }
      const data = (await res.json()) as AuthUser;
      currentUser.value = data;
      return data;
    } catch (err) {
      console.error("fetchCurrentUser error:", err);
      currentUser.value = null;
      return null;
    } finally {
      pendingFetch = null;
    }
  })();

  return pendingFetch;
}

export async function logout(): Promise<void> {
  try {
    await fetch("/api/v1/logout", { method: "POST", credentials: "include" });
  } catch (e) {
    console.error("logout error", e);
  } finally {
    currentUser.value = null;
  }
}

export function useAuth() {
  return { currentUser, fetchCurrentUser, logout };
}
