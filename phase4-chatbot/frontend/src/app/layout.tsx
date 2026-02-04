/**
 * Root layout for Next.js application
 */

import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Todo Chatbot - AI-Powered Task Management',
  description: 'Manage your tasks through natural language conversation',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
