/**
 * TypeScript interfaces for chat functionality
 */

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp?: string;
}

export interface ToolCall {
  tool: string;
  parameters: Record<string, unknown>;
  result: Record<string, unknown>;
}

export interface ChatRequest {
  conversation_id?: string;
  message: string;
}

export interface ChatResponse {
  conversation_id: string;
  response: string;
  tool_calls: ToolCall[];
}

export interface ErrorResponse {
  detail: string;
}

export interface ConversationState {
  conversationId: string | null;
  messages: ChatMessage[];
  isLoading: boolean;
  error: string | null;
}
