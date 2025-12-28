# Todo App Frontend - Phase II

Next.js 14 frontend for the Todo App with React and Tailwind CSS.

## Features

- Modern React UI with Next.js 14 App Router
- TypeScript for type safety
- Tailwind CSS for styling
- Responsive design for mobile and desktop

## Prerequisites

- Node.js 18+
- npm or yarn

## Setup

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure Environment

Copy `.env.example` to `.env.local`:

```bash
cp .env.example .env.local
```

Edit `.env.local`:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Running the Development Server

```bash
npm run dev
```

Visit http://localhost:3000

## Building for Production

```bash
npm run build
npm start
```

## Project Structure

```
frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx       # Root layout
│   │   ├── page.tsx         # Home page
│   │   └── globals.css      # Global styles
│   ├── components/
│   │   ├── TaskList.tsx     # Task list component
│   │   ├── TaskItem.tsx     # Single task component
│   │   ├── TaskForm.tsx     # Add task form
│   │   ├── EditTaskModal.tsx # Edit task modal
│   │   ├── SearchBar.tsx    # Search component
│   │   ├── FilterBar.tsx    # Filter controls
│   │   ├── ConfirmDialog.tsx # Confirmation dialog
│   │   └── EmptyState.tsx   # Empty state
│   ├── services/
│   │   └── api.ts           # API client
│   ├── types/
│   │   └── task.ts          # TypeScript interfaces
│   └── utils/
│       └── priority.ts      # Priority utilities
├── package.json
├── tailwind.config.js
└── tsconfig.json
```

## Components

### TaskList
Displays all tasks with loading and error states.

### TaskItem
Individual task with checkbox, priority badge, and category tag.

### TaskForm
Form for creating new tasks with validation.

### EditTaskModal
Modal for editing existing tasks.

### SearchBar
Debounced search input for filtering tasks.

### FilterBar
Dropdowns for status, priority, category filters, and sorting.

## API Client

The `api.ts` service provides type-safe API calls:

```typescript
import { taskApi, categoryApi } from '@/services/api';

// Get all tasks
const tasks = await taskApi.getAll();

// Create a task
const task = await taskApi.create({ title: 'New Task' });

// Toggle completion
await taskApi.toggle(taskId);
```
