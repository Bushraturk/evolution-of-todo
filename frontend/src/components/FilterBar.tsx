'use client';

import { useState, useEffect } from 'react';
import type { TaskFilters, Priority, Category } from '@/types/task';
import { categoryApi } from '@/services/api';

interface FilterBarProps {
  filters: TaskFilters;
  onChange: (filters: Partial<TaskFilters>) => void;
  onClear: () => void;
}

export default function FilterBar({ filters, onChange, onClear }: FilterBarProps) {
  const [categories, setCategories] = useState<Category[]>([]);

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

  const hasActiveFilters =
    filters.status ||
    filters.priority ||
    filters.category_id ||
    filters.sort_by !== 'created_at' ||
    filters.sort_order !== 'desc';

  return (
    <div className="flex flex-wrap items-center gap-3">
      {/* Status Filter */}
      <select
        value={filters.status || 'all'}
        onChange={(e) => onChange({ status: e.target.value as TaskFilters['status'] || undefined })}
        className="input w-auto text-sm"
      >
        <option value="all">All Tasks</option>
        <option value="incomplete">Incomplete</option>
        <option value="completed">Completed</option>
      </select>

      {/* Priority Filter */}
      <select
        value={filters.priority || ''}
        onChange={(e) => onChange({ priority: (e.target.value as Priority) || undefined })}
        className="input w-auto text-sm"
      >
        <option value="">All Priorities</option>
        <option value="high">High</option>
        <option value="medium">Medium</option>
        <option value="low">Low</option>
      </select>

      {/* Category Filter */}
      <select
        value={filters.category_id || ''}
        onChange={(e) => onChange({ category_id: e.target.value || undefined })}
        className="input w-auto text-sm"
      >
        <option value="">All Categories</option>
        {categories.map((cat) => (
          <option key={cat.id} value={cat.id}>
            {cat.name}
          </option>
        ))}
      </select>

      {/* Sort */}
      <select
        value={`${filters.sort_by || 'created_at'}_${filters.sort_order || 'desc'}`}
        onChange={(e) => {
          const [sort_by, sort_order] = e.target.value.split('_');
          onChange({
            sort_by: sort_by as TaskFilters['sort_by'],
            sort_order: sort_order as TaskFilters['sort_order']
          });
        }}
        className="input w-auto text-sm"
      >
        <option value="created_at_desc">Newest First</option>
        <option value="created_at_asc">Oldest First</option>
        <option value="priority_desc">Priority (High to Low)</option>
        <option value="priority_asc">Priority (Low to High)</option>
        <option value="title_asc">Title (A-Z)</option>
        <option value="title_desc">Title (Z-A)</option>
      </select>

      {/* Clear Filters */}
      {hasActiveFilters && (
        <button
          onClick={onClear}
          className="text-sm text-violet-600 hover:text-purple-700 font-medium transition-colors"
        >
          Clear Filters
        </button>
      )}
    </div>
  );
}
