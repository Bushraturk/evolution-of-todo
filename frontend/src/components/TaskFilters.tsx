import React, { useState, useEffect } from 'react';
import type { Priority } from '@/types/task';

export interface TaskFilterOptions {
  search?: string;
  status?: 'all' | 'completed' | 'incomplete';
  priority?: Priority;
  tags?: string[];
  sortBy?: 'created_at' | 'priority' | 'title' | 'due_date';
  sortOrder?: 'asc' | 'desc';
}

interface TaskFiltersProps {
  filters: TaskFilterOptions;
  onChange: (filters: TaskFilterOptions) => void;
}

interface Tag {
  id: string;
  name: string;
  color: string;
}

export default function TaskFilters({ filters, onChange }: TaskFiltersProps) {
  const [tags, setTags] = useState<Tag[]>([]);
  const [showAdvanced, setShowAdvanced] = useState(false);

  useEffect(() => {
    fetchTags();
  }, []);

  const fetchTags = async () => {
    try {
      const response = await fetch('/api/tags', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });
      const data = await response.json();
      setTags(data.data || []);
    } catch (error) {
      console.error('Failed to fetch tags:', error);
    }
  };

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onChange({ ...filters, search: e.target.value || undefined });
  };

  const handleStatusChange = (status: 'all' | 'completed' | 'incomplete') => {
    onChange({ ...filters, status: status === 'all' ? undefined : status });
  };

  const handlePriorityChange = (priority: Priority | 'all') => {
    onChange({ ...filters, priority: priority === 'all' ? undefined : priority });
  };

  const handleTagToggle = (tagId: string) => {
    const currentTags = filters.tags || [];
    const newTags = currentTags.includes(tagId)
      ? currentTags.filter(id => id !== tagId)
      : [...currentTags, tagId];
    onChange({ ...filters, tags: newTags.length > 0 ? newTags : undefined });
  };

  const handleSortChange = (sortBy: string) => {
    onChange({ ...filters, sortBy: sortBy as any });
  };

  const handleSortOrderChange = () => {
    onChange({
      ...filters,
      sortOrder: filters.sortOrder === 'asc' ? 'desc' : 'asc',
    });
  };

  const handleClearFilters = () => {
    onChange({
      search: undefined,
      status: undefined,
      priority: undefined,
      tags: undefined,
      sortBy: 'created_at',
      sortOrder: 'desc',
    });
  };

  const hasActiveFilters = !!(
    filters.search ||
    filters.status ||
    filters.priority ||
    (filters.tags && filters.tags.length > 0)
  );

  return (
    <div className="glass-card space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-purple-900 dark:text-purple-100">
          Filters
        </h3>
        {hasActiveFilters && (
          <button
            onClick={handleClearFilters}
            className="text-sm text-violet-600 hover:text-violet-700"
          >
            Clear all
          </button>
        )}
      </div>

      {/* Search */}
      <div>
        <label htmlFor="search" className="block text-sm font-medium mb-1 text-purple-800 dark:text-purple-200">
          Search
        </label>
        <input
          type="text"
          id="search"
          value={filters.search || ''}
          onChange={handleSearchChange}
          placeholder="Search tasks..."
          className="input"
        />
      </div>

      {/* Status Filter */}
      <div>
        <label className="block text-sm font-medium mb-2 text-purple-800 dark:text-purple-200">
          Status
        </label>
        <div className="flex gap-2">
          {(['all', 'incomplete', 'completed'] as const).map((status) => (
            <button
              key={status}
              onClick={() => handleStatusChange(status)}
              className={`px-3 py-1 text-sm rounded-lg transition-all ${
                (status === 'all' && !filters.status) || filters.status === status
                  ? 'bg-violet-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-300'
              }`}
            >
              {status.charAt(0).toUpperCase() + status.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Priority Filter */}
      <div>
        <label className="block text-sm font-medium mb-2 text-purple-800 dark:text-purple-200">
          Priority
        </label>
        <div className="flex gap-2">
          {(['all', 'high', 'medium', 'low'] as const).map((priority) => (
            <button
              key={priority}
              onClick={() => handlePriorityChange(priority)}
              className={`px-3 py-1 text-sm rounded-lg transition-all ${
                (priority === 'all' && !filters.priority) || filters.priority === priority
                  ? 'bg-violet-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-300'
              }`}
            >
              {priority.charAt(0).toUpperCase() + priority.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Advanced Filters Toggle */}
      <button
        onClick={() => setShowAdvanced(!showAdvanced)}
        className="text-sm text-violet-600 hover:text-violet-700 flex items-center gap-1"
      >
        {showAdvanced ? '▼' : '▶'} Advanced filters
      </button>

      {showAdvanced && (
        <div className="space-y-4 pt-2 border-t border-gray-200 dark:border-gray-700">
          {/* Tag Filter */}
          {tags.length > 0 && (
            <div>
              <label className="block text-sm font-medium mb-2 text-purple-800 dark:text-purple-200">
                Tags
              </label>
              <div className="flex flex-wrap gap-2">
                {tags.map((tag) => (
                  <button
                    key={tag.id}
                    onClick={() => handleTagToggle(tag.id)}
                    className={`px-3 py-1 text-sm rounded-full border-2 transition-all ${
                      filters.tags?.includes(tag.id)
                        ? 'border-current font-medium'
                        : 'border-transparent opacity-60 hover:opacity-100'
                    }`}
                    style={{
                      backgroundColor: filters.tags?.includes(tag.id)
                        ? `${tag.color}20`
                        : `${tag.color}10`,
                      color: tag.color,
                    }}
                  >
                    {tag.name}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Sort Options */}
          <div>
            <label className="block text-sm font-medium mb-2 text-purple-800 dark:text-purple-200">
              Sort by
            </label>
            <div className="flex gap-2">
              <select
                value={filters.sortBy || 'created_at'}
                onChange={(e) => handleSortChange(e.target.value)}
                className="input flex-1"
              >
                <option value="created_at">Created date</option>
                <option value="due_date">Due date</option>
                <option value="priority">Priority</option>
                <option value="title">Title</option>
              </select>
              <button
                onClick={handleSortOrderChange}
                className="px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-all dark:bg-gray-700 dark:hover:bg-gray-600"
                title={filters.sortOrder === 'asc' ? 'Ascending' : 'Descending'}
              >
                {filters.sortOrder === 'asc' ? '↑' : '↓'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
