/**
 * Simple JWT-based authentication client.
 * Works with the backend API using JWT tokens stored in localStorage.
 */

import { useState, useEffect } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface User {
  id: string;
  email: string;
  name: string | null;
}

export interface Session {
  user: User;
  token: string;
}

// Get token from localStorage
function getToken(): string | null {
  if (typeof window !== "undefined") {
    return localStorage.getItem("auth_token");
  }
  return null;
}

// Set token in localStorage
function setToken(token: string): void {
  if (typeof window !== "undefined") {
    localStorage.setItem("auth_token", token);

    // Also decode and save userId for chatbot
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      const userId = payload.sub || payload.user_id || payload.id;
      if (userId) {
        localStorage.setItem("userId", userId);
      }
    } catch (e) {
      console.error('Failed to decode token for userId:', e);
    }
  }
}

// Remove token from localStorage
function removeToken(): void {
  if (typeof window !== "undefined") {
    localStorage.removeItem("auth_token");
    localStorage.removeItem("userId");
    localStorage.removeItem("conversationId");
  }
}

// API helper
async function fetchApi<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<{ data?: T; error?: string }> {
  const token = getToken();

  try {
    const response = await fetch(`${API_URL}${endpoint}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...options.headers,
      },
    });

    const data = await response.json();

    if (!response.ok) {
      return { error: data.detail || "Request failed" };
    }

    return { data };
  } catch {
    return { error: "Network error" };
  }
}

// Sign in
export async function signIn(email: string, password: string) {
  const result = await fetchApi<{ access_token: string; user: User }>(
    "/api/auth/login",
    {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }
  );

  if (result.data) {
    setToken(result.data.access_token);
    return { data: { session: { user: result.data.user, token: result.data.access_token } } };
  }

  return { error: result.error };
}

// Sign up
export async function signUp(email: string, password: string, name: string) {
  const result = await fetchApi<{ access_token: string; user: User }>(
    "/api/auth/register",
    {
      method: "POST",
      body: JSON.stringify({ email, password, name }),
    }
  );

  if (result.data) {
    setToken(result.data.access_token);
    return { data: { session: { user: result.data.user, token: result.data.access_token } } };
  }

  return { error: result.error };
}

// Sign out
export async function signOut() {
  removeToken();
  return { data: undefined };
}

// Get current session
export async function getSession() {
  const token = getToken();

  if (!token) {
    return { data: null };
  }

  const result = await fetchApi<User>("/api/auth/me");

  if (result.data) {
    return { data: { user: result.data, token } };
  }

  removeToken();
  return { data: null };
}

// useSession hook
export function useSession() {
  const [session, setSession] = useState<Session | null>(null);
  const [isPending, setIsPending] = useState(true);

  useEffect(() => {
    getSession().then((result) => {
      setSession(result.data ?? null);
      setIsPending(false);
    });
  }, []);

  return { data: session, isPending };
}

// Export authClient for backward compatibility
export const authClient = {
  signIn,
  signOut,
  signUp,
  getSession,
  useSession,
};

