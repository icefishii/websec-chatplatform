type SuccessResult<T> = readonly [T, null];

type ErrorResult<E = Error> = readonly [null, E];

type Result<T, E = Error> = SuccessResult<T> | ErrorResult<E>;

export async function tryCatch<T, E = Error>(prosmise: Promise<T>): Promise<Result<T, E>> {
  try {
    const data = await prosmise;
    return [data, null] as const;
  } catch (error) {
    return [null, error as E] as const;
  }
}

export interface Conversation {
  id: string;
  profile_name: string;
  last_message?: string;
  last_message_time?: string;
}

export interface User {
  id: string;
  username: string;
  lastMessage?: string;
  isOnline?: boolean;
}

export interface SearchResult {
  id: string;
  profile_name: string;
}

export interface ChatMessage {
  id?: string;
  sender_id?: string | null;
  recipient_id?: string | null;
  content: string;
  created_at?: string;
}

export interface AuthUser {
  id: string;
  username: string;
  // allow other unknown fields from the backend without using `any`
  [key: string]: unknown;
}
