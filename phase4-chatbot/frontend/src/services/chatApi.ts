/**
 * Chat API client for communicating with the backend
 */

import { ChatRequest, ChatResponse, ErrorResponse } from '../types/chat';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * Get JWT token from localStorage
 */
function getAuthToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('token');
}

/**
 * Get user ID from localStorage
 */
function getUserId(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('userId');
}

/**
 * Send a chat message to the backend
 */
export async function sendChatMessage(
  message: string,
  conversationId?: number
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
export function saveConversationId(conversationId: number): void {
  if (typeof window === 'undefined') return;
  localStorage.setItem('conversationId', conversationId.toString());
}

/**
 * Get conversation ID from localStorage
 */
export function getConversationId(): number | null {
  if (typeof window === 'undefined') return null;
  const id = localStorage.getItem('conversationId');
  return id ? parseInt(id, 10) : null;
}

/**
 * Clear conversation ID from localStorage (start new conversation)
 */
export function clearConversationId(): void {
  if (typeof window === 'undefined') return;
  localStorage.removeItem('conversationId');
}
