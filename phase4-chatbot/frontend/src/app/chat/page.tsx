/**
 * Chat page - Main entry point for the chatbot interface
 */

import ChatInterface from '../../components/ChatInterface';

export default function ChatPage() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-purple-50 to-white">
      <ChatInterface />
    </main>
  );
}
