/**
 * Chat API client for communicating with the backend
 */

import { ChatRequest, ChatResponse, ErrorResponse } from '../types/chat';

const API_URL = process.env.NEXT_PUBLIC_CHAT_API_URL || 'http://localhost:8002';

/**
 * Get JWT token from localStorage
 */
function getAuthToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('auth_token');
}

/**
 * Get user ID from localStorage or decode from token
 */
function getUserId(): string | null {
  if (typeof window === 'undefined') return null;

  // First try to get from localStorage
  let userId = localStorage.getItem('userId');

  // If not found, try to decode from JWT token
  if (!userId) {
    const token = getAuthToken();
    if (token) {
      try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        userId = payload.sub || payload.user_id || payload.id;
        // Save it for next time
        if (userId) {
          localStorage.setItem('userId', userId);
        }
      } catch (e) {
        console.error('Failed to decode token:', e);
      }
    }
  }

  return userId;
}

/**
 * Send a chat message to the backend
 */
export async function sendChatMessage(
  message: string,
  conversationId?: string
): Promise<ChatResponse> {
  const token = getAuthToken();
  const userId = getUserId();

  if (!token || !userId) {
    throw new Error('Not authenticated. Please log in.');
  }

  const request: ChatRequest = {
    message,
    ...(conversationId && { conversation_id: conversationId })
  };

  const response = await fetch(`${API_URL}/api/${userId}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(request)
  });

  if (!response.ok) {
    const error: ErrorResponse = await response.json();
    throw new Error(error.detail || 'Failed to send message');
  }

  return response.json();
}

/**
 * Save conversation ID to localStorage
 */
export function saveConversationId(conversationId: string): void {
  if (typeof window === 'undefined') return;
  localStorage.setItem('conversationId', conversationId);
}

/**
 * Get conversation ID from localStorage
 */
export function getConversationId(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('conversationId');
}

/**
 * Fetch conversation history from backend
 */
export async function fetchConversationHistory(
  conversationId: string
): Promise<{ conversation_id: string; messages: Array<{ role: string; content: string; timestamp: string }> }> {
  const token = getAuthToken();
  const userId = getUserId();

  if (!token || !userId) {
    throw new Error('Not authenticated. Please log in.');
  }

  const response = await fetch(
    `${API_URL}/api/${userId}/conversations/${conversationId}/history`,
    {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    }
  );

  if (!response.ok) {
    if (response.status === 404) {
      // Conversation not found, return empty history
      return { conversation_id: conversationId, messages: [] };
    }
    const error: ErrorResponse = await response.json();
    throw new Error(error.detail || 'Failed to fetch conversation history');
  }

  return response.json();
}

/**
 * Clear conversation ID from localStorage (start new conversation)
 */
export function clearConversationId(): void {
  if (typeof window === 'undefined') return;
  localStorage.removeItem('conversationId');
}
