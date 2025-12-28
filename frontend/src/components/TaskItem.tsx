'use client';

import { useState } from 'react';
import type { Task } from '@/types/task';
import { taskApi } from '@/services/api';

interface TaskItemProps {
  task: Task;
  onUpdate: () => void;
  onEdit: (task: Task) => void;
  onDelete: (task: Task) => void;
}

const priorityColors = {
  high: 'bg-gradient-to-r from-rose-100 to-pink-100 text-rose-700 dark:from-rose-900/50 dark:to-pink-900/50 dark:text-rose-300 border border-rose-200 dark:border-rose-800',
  medium: 'bg-gradient-to-r from-amber-100 to-yellow-100 text-amber-700 dark:from-amber-900/50 dark:to-yellow-900/50 dark:text-amber-300 border border-amber-200 dark:border-amber-800',
  low: 'bg-gradient-to-r from-purple-100 to-violet-100 text-purple-700 dark:from-purple-900/50 dark:to-violet-900/50 dark:text-purple-300 border border-purple-200 dark:border-purple-800',
};

export default function TaskItem({ task, onUpdate, onEdit, onDelete }: TaskItemProps) {
  const [isToggling, setIsToggling] = useState(false);

  const handleToggle = async () => {
    if (isToggling) return;

    setIsToggling(true);
    try {
      await taskApi.toggle(task.id);
      onUpdate();
    } catch (error) {
      console.error('Failed to toggle task:', error);
    } finally {
      setIsToggling(false);
    }
  };

  return (
    <div
      className={`card flex items-start gap-4 transition-opacity ${
        task.completed ? 'opacity-60' : ''
      }`}
    >
      {/* Checkbox */}
      <div className="flex-shrink-0 pt-1">
        <input
          type="checkbox"
          checked={task.completed}
          onChange={handleToggle}
          disabled={isToggling}
          className="w-5 h-5 rounded border-purple-300 text-violet-600 focus:ring-violet-500 cursor-pointer disabled:cursor-wait accent-violet-600"
        />
      </div>

      {/* Content */}
      <div className="flex-grow min-w-0">
        <div className="flex items-center gap-2 flex-wrap">
          <h3
            className={`font-medium text-lg ${
              task.completed ? 'line-through text-gray-500' : ''
            }`}
          >
            {task.title}
          </h3>

          {/* Priority Badge */}
          <span
            className={`px-2 py-0.5 text-xs font-medium rounded-full ${
              priorityColors[task.priority]
            }`}
          >
            {task.priority.charAt(0).toUpperCase() + task.priority.slice(1)}
          </span>

          {/* Category Tag */}
          {task.category && (
            <span
              className="px-2 py-0.5 text-xs font-medium rounded-full"
              style={{
                backgroundColor: `${task.category.color}20`,
                color: task.category.color,
              }}
            >
              {task.category.name}
            </span>
          )}
        </div>

        {task.description && (
          <p
            className={`mt-1 text-sm text-gray-600 dark:text-gray-400 ${
              task.completed ? 'line-through' : ''
            }`}
          >
            {task.description}
          </p>
        )}

        <p className="mt-2 text-xs text-gray-400">
          Created: {new Date(task.created_at).toLocaleDateString()}
        </p>
      </div>

      {/* Actions */}
      <div className="flex-shrink-0 flex gap-2">
        <button
          onClick={() => onEdit(task)}
          className="p-2 text-purple-400 hover:text-violet-600 hover:bg-purple-100 rounded-lg transition-all duration-200"
          title="Edit task"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
          </svg>
        </button>
        <button
          onClick={() => onDelete(task)}
          className="p-2 text-purple-400 hover:text-rose-600 hover:bg-rose-100 rounded-lg transition-all duration-200"
          title="Delete task"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
        </button>
      </div>
    </div>
  );
}
