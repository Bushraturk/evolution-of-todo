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
  parameters: Record<string, any>;
  result: Record<string, any>;
}

export interface ChatRequest {
  conversation_id?: number;
  message: string;
}

export interface ChatResponse {
  conversation_id: number;
  response: string;
  tool_calls: ToolCall[];
}

export interface ErrorResponse {
  detail: string;
}

export interface ConversationState {
  conversationId: number | null;
  messages: ChatMessage[];
  isLoading: boolean;
  error: string | null;
}
