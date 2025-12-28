'use client';

import { useState, useEffect } from 'react';
import type { Priority, Category, CreateTaskRequest } from '@/types/task';
import { taskApi, categoryApi } from '@/services/api';

interface TaskFormProps {
  onSuccess: () => void;
  onCancel: () => void;
}

export default function TaskForm({ onSuccess, onCancel }: TaskFormProps) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [priority, setPriority] = useState<Priority>('medium');
  const [categoryId, setCategoryId] = useState<string>('');
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const data = await categoryApi.getAll();
        setCategories(data);
      } catch (err) {
        console.error('Failed to fetch categories:', err);
      }
    };
    fetchCategories();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!title.trim()) {
      setError('Title is required');
      return;
    }

    setLoading(true);
    try {
      const request: CreateTaskRequest = {
        title: title.trim(),
        description: description.trim() || undefined,
        priority,
        category_id: categoryId || undefined,
      };
      await taskApi.create(request);
      onSuccess();
    } catch (err) {
      console.error('Failed to create task:', err);
      setError('Failed to create task. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="card">
      <h2 className="text-lg font-semibold mb-4 text-purple-900 dark:text-purple-100">Add New Task</h2>

      {error && (
        <div className="mb-4 p-3 bg-rose-100 dark:bg-rose-900/50 text-rose-700 dark:text-rose-200 rounded-xl text-sm border border-rose-200 dark:border-rose-800">
          {error}
        </div>
      )}

      <div className="space-y-4">
        {/* Title */}
        <div>
          <label htmlFor="title" className="block text-sm font-medium mb-1 text-purple-800 dark:text-purple-200">
            Title <span className="text-rose-500">*</span>
          </label>
          <input
            type="text"
            id="title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="input"
            placeholder="What needs to be done?"
            maxLength={200}
            required
          />
        </div>

        {/* Description */}
        <div>
          <label htmlFor="description" className="block text-sm font-medium mb-1 text-purple-800 dark:text-purple-200">
            Description
          </label>
          <textarea
            id="description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="input resize-none"
            placeholder="Add more details..."
            rows={3}
            maxLength={1000}
          />
        </div>

        {/* Priority and Category */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label htmlFor="priority" className="block text-sm font-medium mb-1 text-purple-800 dark:text-purple-200">
              Priority
            </label>
            <select
              id="priority"
              value={priority}
              onChange={(e) => setPriority(e.target.value as Priority)}
              className="input"
            >
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>
          </div>

          <div>
            <label htmlFor="category" className="block text-sm font-medium mb-1 text-purple-800 dark:text-purple-200">
              Category
            </label>
            <select
              id="category"
              value={categoryId}
              onChange={(e) => setCategoryId(e.target.value)}
              className="input"
            >
              <option value="">No category</option>
              {categories.map((cat) => (
                <option key={cat.id} value={cat.id}>
                  {cat.name}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Actions */}
        <div className="flex justify-end gap-3 pt-4">
          <button
            type="button"
            onClick={onCancel}
            className="btn-secondary"
            disabled={loading}
          >
            Cancel
          </button>
          <button
            type="submit"
            className="btn-primary"
            disabled={loading}
          >
            {loading ? 'Creating...' : 'Create Task'}
          </button>
        </div>
      </div>
    </form>
  );
}
