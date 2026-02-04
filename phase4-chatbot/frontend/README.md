# Frontend Implementation Guide

## Overview

This guide provides instructions for running and deploying the AI-Powered Todo Chatbot frontend.

## Prerequisites

- Node.js 18+ installed
- Backend running on http://localhost:8000 (or configured URL)
- Valid JWT token from Phase III authentication

## Installation

### 1. Install Dependencies

```bash
cd phase4-chatbot/frontend
npm install
```

### 2. Configure Environment

Create `.env.local` file from template:

```bash
cp .env.local.example .env.local
```

Edit `.env.local` with your configuration:

```env
# Backend API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# OpenAI ChatKit Configuration (optional for local dev)
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=

# Authentication Configuration
NEXT_PUBLIC_AUTH_URL=http://localhost:3000
```

### 3. Start Development Server

```bash
npm run dev
```

The frontend will be available at http://localhost:3000

## Usage

### Authentication

**Important**: The chatbot requires authentication. You need to:

1. Have a valid JWT token from Phase III authentication
2. Store the token in localStorage as `token`
3. Store your user ID in localStorage as `userId`

**For Testing Without Phase III:**

Open browser console and set mock values:
```javascript
localStorage.setItem('token', 'mock-token-for-testing');
localStorage.setItem('userId', 'your-user-id');
```

### Using the Chatbot

1. Navigate to http://localhost:3000
2. Click "Start Chatting" button
3. Type natural language commands:
   - "Add a task to buy groceries"
   - "Show me all my tasks"
   - "Mark task 1 as complete"
   - "What's pending?"
   - "Delete task 2"

### Conversation Management

- **New Conversation**: Click "New Conversation" button to start fresh
- **Continue Conversation**: Your conversation ID is saved in localStorage
- **Message History**: Last 50 messages are loaded from the backend

## Project Structure

```
frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx          # Root layout
│   │   ├── page.tsx            # Landing page
│   │   ├── globals.css         # Global styles
│   │   └── chat/
│   │       └── page.tsx        # Chat page
│   ├── components/
│   │   └── ChatInterface.tsx   # Main chat component
│   ├── services/
│   │   └── chatApi.ts          # API client
│   └── types/
│       └── chat.ts             # TypeScript interfaces
├── next.config.js              # Next.js configuration
├── tailwind.config.js          # Tailwind CSS configuration
├── tsconfig.json               # TypeScript configuration
└── package.json                # Dependencies
```

## Features

### ChatInterface Component

- Real-time message display
- Loading states with animated dots
- Error handling with user-friendly messages
- Conversation state management
- Auto-scroll to latest message
- Keyboard shortcuts (Enter to send)

### Chat API Client

- JWT authentication
- Conversation ID persistence
- Error handling
- TypeScript type safety

### Styling

- Tailwind CSS for responsive design
- Purple gradient theme
- Mobile-friendly interface
- Smooth animations

## Development

### Running Tests

```bash
npm test
```

### Building for Production

```bash
npm run build
npm start
```

### Linting

```bash
npm run lint
```

## Deployment

### Vercel Deployment

1. **Connect Repository** to Vercel
2. **Set Environment Variables**:
   - `NEXT_PUBLIC_API_URL`: Your backend URL (e.g., Hugging Face Spaces)
   - `NEXT_PUBLIC_OPENAI_DOMAIN_KEY`: Domain key from OpenAI (for production ChatKit)
3. **Deploy**: Vercel auto-deploys on push to main branch

### OpenAI ChatKit Configuration (Production)

For production deployment with actual OpenAI ChatKit:

1. Deploy frontend to get production URL
2. Go to https://platform.openai.com/settings/organization/security/domain-allowlist
3. Add your Vercel URL to the allowlist
4. Copy the domain key
5. Add `NEXT_PUBLIC_OPENAI_DOMAIN_KEY` to Vercel environment variables
6. Redeploy

## Troubleshooting

### Common Issues

**Issue**: "Not authenticated" error
**Solution**: Ensure JWT token and userId are in localStorage

**Issue**: "Failed to send message" error
**Solution**:
- Verify backend is running
- Check NEXT_PUBLIC_API_URL is correct
- Verify JWT token is valid

**Issue**: Messages not displaying
**Solution**: Check browser console for errors, verify API response format

**Issue**: Conversation not persisting
**Solution**: Check localStorage for conversationId, verify backend is saving messages

### Debug Mode

Enable debug logging in browser console:
```javascript
localStorage.setItem('debug', 'true');
```

## Integration with Phase III

The frontend expects Phase III authentication to be available:

1. **Login Flow**: Users should login through Phase III first
2. **Token Storage**: Phase III stores JWT token in localStorage
3. **User ID**: Phase III stores user ID in localStorage
4. **Navigation**: Add link to chatbot from Phase III dashboard

## API Endpoints Used

- `POST /api/{user_id}/chat`: Send chat message
  - Headers: `Authorization: Bearer {token}`
  - Body: `{ message: string, conversation_id?: number }`
  - Response: `{ conversation_id: number, response: string, tool_calls: array }`

## Next Steps

1. **Test All Features**:
   - Create tasks
   - List tasks
   - Complete tasks
   - Update tasks
   - Delete tasks

2. **Integrate with Phase III**:
   - Add navigation link from dashboard
   - Ensure authentication flow works
   - Test with real user accounts

3. **Deploy to Production**:
   - Deploy backend to Hugging Face Spaces
   - Deploy frontend to Vercel
   - Configure OpenAI domain allowlist
   - Test end-to-end

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review browser console for errors
3. Check network tab for API requests
4. Verify backend logs

---

**Status**: Frontend implementation complete
**Last Updated**: 2026-01-29
