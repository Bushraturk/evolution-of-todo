/**
 * ChatInterface component - Main chat interface using OpenAI ChatKit
 *
 * Note: This is a simplified implementation. For production, you would use
 * the actual @openai/chatkit package which requires domain allowlist configuration.
 */

'use client';

import { useState, useEffect, useRef } from 'react';
import { ChatMessage, ConversationState } from '../types/chat';
import {
  sendChatMessage,
  getConversationId,
  saveConversationId,
  clearConversationId
} from '../services/chatApi';

export default function ChatInterface() {
  const [state, setState] = useState<ConversationState>({
    conversationId: null,
    messages: [],
    isLoading: false,
    error: null
  });
  const [inputMessage, setInputMessage] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Load conversation ID on mount
  useEffect(() => {
    const conversationId = getConversationId();
    if (conversationId) {
      setState(prev => ({ ...prev, conversationId }));
    }
  }, []);

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [state.messages]);

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || state.isLoading) return;

    const userMessage: ChatMessage = {
      role: 'user',
      content: inputMessage,
      timestamp: new Date().toISOString()
    };

    // Add user message to UI
    setState(prev => ({
      ...prev,
      messages: [...prev.messages, userMessage],
      isLoading: true,
      error: null
    }));

    setInputMessage('');

    try {
      // Send message to backend
      const response = await sendChatMessage(
        inputMessage,
        state.conversationId || undefined
      );

      // Save conversation ID
      if (!state.conversationId) {
        saveConversationId(response.conversation_id);
      }

      // Add assistant response to UI
      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: response.response,
        timestamp: new Date().toISOString()
      };

      setState(prev => ({
        ...prev,
        conversationId: response.conversation_id,
        messages: [...prev.messages, assistantMessage],
        isLoading: false
      }));

    } catch (error) {
      setState(prev => ({
        ...prev,
        isLoading: false,
        error: error instanceof Error ? error.message : 'Failed to send message'
      }));
    }
  };

  const handleNewConversation = () => {
    clearConversationId();
    setState({
      conversationId: null,
      messages: [],
      isLoading: false,
      error: null
    });
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="flex flex-col h-screen max-w-4xl mx-auto p-4">
      {/* Header */}
      <div className="flex justify-between items-center mb-4 pb-4 border-b">
        <h1 className="text-2xl font-bold text-purple-600">Todo Chatbot</h1>
        <button
          onClick={handleNewConversation}
          className="px-4 py-2 bg-purple-100 text-purple-700 rounded-lg hover:bg-purple-200 transition"
        >
          New Conversation
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto mb-4 space-y-4">
        {state.messages.length === 0 && (
          <div className="text-center text-gray-500 mt-8">
            <p className="text-lg mb-2">👋 Welcome to Todo Chatbot!</p>
            <p className="text-sm">Try saying:</p>
            <ul className="text-sm mt-2 space-y-1">
              <li>"Add a task to buy groceries"</li>
              <li>"Show me all my tasks"</li>
              <li>"Mark task 1 as complete"</li>
            </ul>
          </div>
        )}

        {state.messages.map((message, index) => (
          <div
            key={index}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[70%] rounded-lg p-4 ${
                message.role === 'user'
                  ? 'bg-purple-600 text-white'
                  : 'bg-gray-100 text-gray-900'
              }`}
            >
              <p className="whitespace-pre-wrap">{message.content}</p>
              {message.timestamp && (
                <p className="text-xs mt-2 opacity-70">
                  {new Date(message.timestamp).toLocaleTimeString()}
                </p>
              )}
            </div>
          </div>
        ))}

        {state.isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 rounded-lg p-4">
              <div className="flex space-x-2">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200"></div>
              </div>
            </div>
          </div>
        )}

        {state.error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
            <p className="font-bold">Error</p>
            <p>{state.error}</p>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t pt-4">
        <div className="flex space-x-2">
          <textarea
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message... (Press Enter to send)"
            className="flex-1 p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-600 resize-none"
            rows={2}
            disabled={state.isLoading}
          />
          <button
            onClick={handleSendMessage}
            disabled={!inputMessage.trim() || state.isLoading}
            className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}
