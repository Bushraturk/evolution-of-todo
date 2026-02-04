/**
 * Landing page for the chatbot application
 */

import Link from 'next/link';

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-purple-50">
      <div className="container mx-auto px-4 py-16">
        {/* Header */}
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold text-purple-600 mb-4">
            Todo Chatbot
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Manage your tasks through natural language conversation.
            No forms, no clicks - just talk to your AI assistant.
          </p>
        </div>

        {/* Features */}
        <div className="grid md:grid-cols-3 gap-8 mb-16 max-w-5xl mx-auto">
          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="text-3xl mb-4">💬</div>
            <h3 className="text-lg font-semibold mb-2">Natural Language</h3>
            <p className="text-gray-600">
              Just say what you need to do. "Add a task to buy groceries" - it's that simple.
            </p>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="text-3xl mb-4">🤖</div>
            <h3 className="text-lg font-semibold mb-2">AI-Powered</h3>
            <p className="text-gray-600">
              Powered by OpenAI GPT-4 with MCP protocol for intelligent task management.
            </p>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="text-3xl mb-4">💾</div>
            <h3 className="text-lg font-semibold mb-2">Conversation History</h3>
            <p className="text-gray-600">
              Your conversations are saved. Pick up right where you left off.
            </p>
          </div>
        </div>

        {/* CTA */}
        <div className="text-center">
          <Link
            href="/chat"
            className="inline-block px-8 py-4 bg-purple-600 text-white text-lg font-semibold rounded-lg hover:bg-purple-700 transition shadow-lg"
          >
            Start Chatting
          </Link>
          <p className="text-sm text-gray-500 mt-4">
            Note: You'll need to be authenticated to use the chatbot
          </p>
        </div>

        {/* Examples */}
        <div className="mt-16 max-w-3xl mx-auto">
          <h2 className="text-2xl font-bold text-center mb-8">Try These Commands</h2>
          <div className="bg-white rounded-lg shadow-md p-6 space-y-4">
            <div className="border-l-4 border-purple-600 pl-4">
              <p className="font-mono text-sm text-gray-700">"Add a task to buy groceries"</p>
              <p className="text-xs text-gray-500 mt-1">Creates a new task</p>
            </div>
            <div className="border-l-4 border-purple-600 pl-4">
              <p className="font-mono text-sm text-gray-700">"Show me all my tasks"</p>
              <p className="text-xs text-gray-500 mt-1">Lists all your tasks</p>
            </div>
            <div className="border-l-4 border-purple-600 pl-4">
              <p className="font-mono text-sm text-gray-700">"Mark task 1 as complete"</p>
              <p className="text-xs text-gray-500 mt-1">Completes a specific task</p>
            </div>
            <div className="border-l-4 border-purple-600 pl-4">
              <p className="font-mono text-sm text-gray-700">"What's pending?"</p>
              <p className="text-xs text-gray-500 mt-1">Shows only incomplete tasks</p>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center mt-16 text-gray-500 text-sm">
          <p>Part of the Evolution of Todo project - Phase IV</p>
          <p className="mt-2">Built with Next.js, FastAPI, OpenAI Agents SDK, and MCP</p>
        </div>
      </div>
    </main>
  );
}
