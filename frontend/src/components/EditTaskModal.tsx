'use client';

import { useState, useEffect } from 'react';
import type { Task, Priority, Category, UpdateTaskRequest } from '@/types/task';
import { taskApi, categoryApi } from '@/services/api';

interface EditTaskModalProps {
  task: Task;
  onSave: () => void;
  onClose: () => void;
}

export default function EditTaskModal({ task, onSave, onClose }: EditTaskModalProps) {
  const [title, setTitle] = useState(task.title);
  const [description, setDescription] = useState(task.description || '');
  const [priority, setPriority] = useState<Priority>(task.priority);
  const [categoryId, setCategoryId] = useState<string>(task.category_id || '');
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
      const request: UpdateTaskRequest = {
        title: title.trim(),
        description: description.trim() || undefined,
        priority,
        category_id: categoryId || null,
      };
      await taskApi.update(task.id, request);
      onSave();
    } catch (err) {
      console.error('Failed to update task:', err);
      setError('Failed to update task. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-purple-950/50 backdrop-blur-sm">
      <div className="bg-white dark:bg-purple-900/90 rounded-2xl shadow-2xl max-w-md w-full max-h-[90vh] overflow-y-auto border-2 border-purple-200 dark:border-purple-700">
        <form onSubmit={handleSubmit} className="p-6">
          <h2 className="text-lg font-semibold mb-4 text-purple-900 dark:text-purple-100">Edit Task</h2>

          {error && (
            <div className="mb-4 p-3 bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-200 rounded-lg text-sm">
              {error}
            </div>
          )}

          <div className="space-y-4">
            {/* Title */}
            <div>
              <label htmlFor="edit-title" className="block text-sm font-medium mb-1 text-purple-800 dark:text-purple-200">
                Title <span className="text-rose-500">*</span>
              </label>
              <input
                type="text"
                id="edit-title"
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
              <label htmlFor="edit-description" className="block text-sm font-medium mb-1 text-purple-800 dark:text-purple-200">
                Description
              </label>
              <textarea
                id="edit-description"
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
                <label htmlFor="edit-priority" className="block text-sm font-medium mb-1 text-purple-800 dark:text-purple-200">
                  Priority
                </label>
                <select
                  id="edit-priority"
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
                <label htmlFor="edit-category" className="block text-sm font-medium mb-1 text-purple-800 dark:text-purple-200">
                  Category
                </label>
                <select
                  id="edit-category"
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
                onClick={onClose}
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
                {loading ? 'Saving...' : 'Save Changes'}
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}
