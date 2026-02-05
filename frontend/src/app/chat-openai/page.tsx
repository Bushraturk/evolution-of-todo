'use client';

import { useSession } from '@/lib/auth-client';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';

export default function ChatOpenAIPage() {
  const { data: session, isPending } = useSession();
  const router = useRouter();
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Array<{role: string, content: string}>>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!isPending && !session) {
      router.push('/auth/signin');
    }
  }, [session, isPending, router]);

  useEffect(() => {
    // Load conversation ID from localStorage
    const savedConvId = localStorage.getItem('conversationId');
    if (savedConvId) {
      setConversationId(savedConvId);
    }
  }, []);

  if (isPending) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (!session) {
    return null;
  }

  const userId = session.user.id;
  const token = localStorage.getItem('auth_token');

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput('');
    setError(null);
    setIsLoading(true);

    // Add user message to UI
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_CHAT_API_URL}/api/${userId}/chat`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            conversation_id: conversationId,
            message: userMessage,
          }),
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to send message');
      }

      const data = await response.json();

      // Save conversation ID
      if (data.conversation_id && data.conversation_id !== conversationId) {
        setConversationId(data.conversation_id);
        localStorage.setItem('conversationId', data.conversation_id);
      }

      // Add assistant response to UI
      setMessages(prev => [...prev, { role: 'assistant', content: data.response }]);

      // Log tool calls if any
      if (data.tool_calls && data.tool_calls.length > 0) {
        console.log('Tools used:', data.tool_calls);
      }

    } catch (err: unknown) {
      console.error('Chat error:', err);
      const errorMessage = err instanceof Error ? err.message : 'Failed to send message';
      setError(errorMessage);
      // Remove the user message that failed
      setMessages(prev => prev.slice(0, -1));
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const startNewConversation = () => {
    setConversationId(null);
    setMessages([]);
    localStorage.removeItem('conversationId');
    setError(null);
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b px-6 py-4 shadow-sm">
        <div className="flex items-center justify-between max-w-6xl mx-auto">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">AI Todo Assistant</h1>
            <p className="text-sm text-gray-600">Powered by OpenAI Agents SDK + Gemini</p>
          </div>
          <div className="flex gap-3">
            <button
              onClick={startNewConversation}
              className="px-4 py-2 text-sm font-medium text-purple-700 bg-purple-50 border border-purple-200 rounded-md hover:bg-purple-100"
            >
              New Chat
            </button>
            <button
              onClick={() => router.push('/dashboard')}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
            >
              Back to Dashboard
            </button>
          </div>
        </div>
      </div>

      {/* Chat Container */}
      <div className="flex-1 overflow-hidden max-w-6xl w-full mx-auto">
        <div className="h-full flex flex-col">
          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-6 space-y-4">
            {messages.length === 0 && (
              <div className="text-center py-12">
                <div className="text-6xl mb-4">🤖</div>
                <h2 className="text-2xl font-semibold text-gray-900 mb-2">
                  Welcome to AI Todo Assistant!
                </h2>
                <p className="text-gray-600 mb-6 max-w-2xl mx-auto">
                  I can help you manage your tasks using natural language. Try saying:
                </p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-w-3xl mx-auto">
                  <div className="bg-white p-4 rounded-lg border border-gray-200 text-left">
                    <p className="text-sm font-medium text-gray-900">Create tasks</p>
                    <p className="text-sm text-gray-600 mt-1">&quot;Add a task to buy groceries&quot;</p>
                  </div>
                  <div className="bg-white p-4 rounded-lg border border-gray-200 text-left">
                    <p className="text-sm font-medium text-gray-900">View tasks</p>
                    <p className="text-sm text-gray-600 mt-1">&quot;Show me all my tasks&quot;</p>
                  </div>
                  <div className="bg-white p-4 rounded-lg border border-gray-200 text-left">
                    <p className="text-sm font-medium text-gray-900">Complete tasks</p>
                    <p className="text-sm text-gray-600 mt-1">&quot;Mark task 3 as complete&quot;</p>
                  </div>
                  <div className="bg-white p-4 rounded-lg border border-gray-200 text-left">
                    <p className="text-sm font-medium text-gray-900">Update tasks</p>
                    <p className="text-sm text-gray-600 mt-1">&quot;Change task 1 to &apos;Call mom&apos;&quot;</p>
                  </div>
                </div>
              </div>
            )}

            {messages.map((message, index) => (
              <div
                key={index}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-3xl px-4 py-3 rounded-lg ${
                    message.role === 'user'
                      ? 'bg-purple-600 text-white'
                      : 'bg-white text-gray-900 border border-gray-200'
                  }`}
                >
                  <p className="whitespace-pre-wrap">{message.content}</p>
                </div>
              </div>
            ))}

            {isLoading && (
              <div className="flex justify-start">
                <div className="max-w-3xl px-4 py-3 rounded-lg bg-white border border-gray-200">
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  </div>
                </div>
              </div>
            )}

            {error && (
              <div className="flex justify-center">
                <div className="max-w-3xl px-4 py-3 rounded-lg bg-red-50 border border-red-200 text-red-800">
                  <p className="text-sm">❌ {error}</p>
                </div>
              </div>
            )}
          </div>

          {/* Input Area */}
          <div className="border-t bg-white p-4">
            <div className="max-w-4xl mx-auto flex gap-3">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask me to manage your tasks... (e.g., 'Add a task to buy groceries')"
                disabled={isLoading}
                className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
              />
              <button
                onClick={sendMessage}
                disabled={isLoading || !input.trim()}
                className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:bg-gray-300 disabled:cursor-not-allowed font-medium transition-colors"
              >
                {isLoading ? 'Sending...' : 'Send'}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
