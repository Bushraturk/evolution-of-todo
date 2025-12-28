'use client';

import { useEffect, useState, useCallback } from 'react';
import type { Task, TaskFilters } from '@/types/task';
import { taskApi } from '@/services/api';
import TaskItem from './TaskItem';
import EmptyState from './EmptyState';

interface TaskListProps {
  filters?: TaskFilters;
  onEdit: (task: Task) => void;
  onDelete: (task: Task) => void;
  refreshTrigger?: number;
}

export default function TaskList({ filters, onEdit, onDelete, refreshTrigger }: TaskListProps) {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchTasks = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      console.log('Fetching tasks with filters:', filters);
      const data = await taskApi.getAll(filters);
      console.log('Tasks received:', data);
      setTasks(data || []);
    } catch (err) {
      console.error('Failed to fetch tasks:', err);
      setError('Failed to load tasks. Please check if the backend is running on http://localhost:8000');
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    fetchTasks();
  }, [fetchTasks, refreshTrigger]);

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-violet-500"></div>
        <span className="ml-3 text-purple-600">Loading tasks...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12 card">
        <svg className="mx-auto h-12 w-12 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
        <p className="text-red-500 mt-4 mb-4">{error}</p>
        <button onClick={fetchTasks} className="btn-primary">
          Try Again
        </button>
      </div>
    );
  }

  if (tasks.length === 0) {
    return <EmptyState />;
  }

  return (
    <div className="space-y-4">
      {tasks.map((task) => (
        <TaskItem
          key={task.id}
          task={task}
          onUpdate={fetchTasks}
          onEdit={onEdit}
          onDelete={onDelete}
        />
      ))}
      <p className="text-center text-sm text-purple-500 pt-4">
        {tasks.length} task{tasks.length !== 1 ? 's' : ''} •{' '}
        {tasks.filter((t) => t.completed).length} completed •{' '}
        {tasks.filter((t) => !t.completed).length} pending
      </p>
    </div>
  );
}
