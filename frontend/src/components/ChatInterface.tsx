/**
 * ChatInterface component - Main chat interface for AI assistant
 */

'use client';

import { useState, useEffect, useRef } from 'react';
import { ChatMessage, ConversationState } from '../types/chat';
import {
  sendChatMessage,
  getConversationId,
  saveConversationId,
  fetchConversationHistory
} from '../services/chatApi';

export default function ChatInterface() {
  const [state, setState] = useState<ConversationState>({
    conversationId: null,
    messages: [],
    isLoading: false,
    error: null
  });
  const [inputMessage, setInputMessage] = useState('');
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Load conversation ID and history on mount
  useEffect(() => {
    const loadConversation = async () => {
      const conversationId = getConversationId();
      if (conversationId) {
        setState(prev => ({ ...prev, conversationId }));

        // Fetch conversation history
        setIsLoadingHistory(true);
        try {
          const history = await fetchConversationHistory(conversationId);
          const messages: ChatMessage[] = history.messages.map(msg => ({
            role: msg.role as 'user' | 'assistant',
            content: msg.content,
            timestamp: msg.timestamp
          }));

          setState(prev => ({
            ...prev,
            conversationId: history.conversation_id,
            messages
          }));
        } catch (error) {
          console.error('Failed to load conversation history:', error);
          // If history load fails, continue with empty messages
          // User can still send new messages
        } finally {
          setIsLoadingHistory(false);
        }
      }
    };

    loadConversation();
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

    setState(prev => ({
      ...prev,
      messages: [...prev.messages, userMessage],
      isLoading: true,
      error: null
    }));

    setInputMessage('');

    try {
      const response = await sendChatMessage(
        inputMessage,
        state.conversationId || undefined
      );

      if (!state.conversationId) {
        saveConversationId(response.conversation_id);
      }

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

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="flex flex-col h-full bg-white">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {isLoadingHistory && (
          <div className="text-center text-gray-500 mt-8">
            <div className="flex justify-center mb-4">
              <div className="w-8 h-8 border-4 border-purple-200 border-t-purple-600 rounded-full animate-spin"></div>
            </div>
            <p className="text-sm">Loading conversation history...</p>
          </div>
        )}

        {!isLoadingHistory && state.messages.length === 0 && (
          <div className="text-center text-gray-500 mt-8">
            <div className="text-4xl mb-4">👋</div>
            <p className="text-sm mb-4 font-medium">Hi! I&apos;m your AI assistant.</p>
            <div className="text-xs space-y-2">
              <p className="font-semibold text-gray-700">Try saying:</p>
              <div className="space-y-1">
                <p className="text-purple-600">&quot;Add a task to buy groceries&quot;</p>
                <p className="text-purple-600">&quot;Show me all my tasks&quot;</p>
                <p className="text-purple-600">&quot;What&apos;s pending?&quot;</p>
                <p className="text-purple-600">&quot;Mark task 1 as complete&quot;</p>
              </div>
            </div>
          </div>
        )}

        {state.messages.map((message, index) => (
          <div
            key={index}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                message.role === 'user'
                  ? 'bg-purple-600 text-white rounded-br-none'
                  : 'bg-gray-100 text-gray-900 rounded-bl-none'
              }`}
            >
              <p className="text-sm whitespace-pre-wrap">{message.content}</p>
              {message.timestamp && (
                <p className="text-xs mt-1 opacity-70">
                  {new Date(message.timestamp).toLocaleTimeString([], {
                    hour: '2-digit',
                    minute: '2-digit'
                  })}
                </p>
              )}
            </div>
          </div>
        ))}

        {state.isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 rounded-2xl rounded-bl-none px-4 py-3">
              <div className="flex space-x-2">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
              </div>
            </div>
          </div>
        )}

        {state.error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
            <p className="font-semibold">Error</p>
            <p>{state.error}</p>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t p-4 bg-gray-50">
        <div className="flex space-x-2">
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message..."
            className="flex-1 px-4 py-2 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-purple-600 focus:border-transparent text-sm"
            disabled={state.isLoading}
          />
          <button
            onClick={handleSendMessage}
            disabled={!inputMessage.trim() || state.isLoading}
            className="px-6 py-2 bg-purple-600 text-white rounded-full hover:bg-purple-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition text-sm font-medium"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}
