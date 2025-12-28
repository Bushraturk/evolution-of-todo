'use client';

import { useState, useCallback } from 'react';
import type { Task, TaskFilters } from '@/types/task';
import TaskList from '@/components/TaskList';
import TaskForm from '@/components/TaskForm';
import EditTaskModal from '@/components/EditTaskModal';
import ConfirmDialog from '@/components/ConfirmDialog';
import SearchBar from '@/components/SearchBar';
import FilterBar from '@/components/FilterBar';
import { taskApi } from '@/services/api';

export default function Home() {
  const [showForm, setShowForm] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);
  const [deletingTask, setDeletingTask] = useState<Task | null>(null);
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [filters, setFilters] = useState<TaskFilters>({});

  const handleRefresh = useCallback(() => {
    setRefreshTrigger((prev) => prev + 1);
  }, []);

  const handleTaskCreated = useCallback(() => {
    setShowForm(false);
    handleRefresh();
  }, [handleRefresh]);

  const handleEdit = useCallback((task: Task) => {
    setEditingTask(task);
  }, []);

  const handleEditClose = useCallback(() => {
    setEditingTask(null);
  }, []);

  const handleEditSave = useCallback(() => {
    setEditingTask(null);
    handleRefresh();
  }, [handleRefresh]);

  const handleDelete = useCallback((task: Task) => {
    setDeletingTask(task);
  }, []);

  const handleDeleteConfirm = useCallback(async () => {
    if (!deletingTask) return;

    try {
      await taskApi.delete(deletingTask.id);
      setDeletingTask(null);
      handleRefresh();
    } catch (error) {
      console.error('Failed to delete task:', error);
    }
  }, [deletingTask, handleRefresh]);

  const handleDeleteCancel = useCallback(() => {
    setDeletingTask(null);
  }, []);

  const handleSearch = useCallback((search: string) => {
    setFilters((prev) => ({ ...prev, search: search || undefined }));
  }, []);

  const handleFilterChange = useCallback((newFilters: Partial<TaskFilters>) => {
    setFilters((prev) => ({ ...prev, ...newFilters }));
  }, []);

  const handleClearFilters = useCallback(() => {
    setFilters({});
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-violet-50 to-fuchsia-50 dark:from-indigo-950 dark:via-purple-950 dark:to-violet-950">
      {/* Header */}
      <header className="bg-gradient-to-r from-violet-600 via-purple-600 to-fuchsia-600 shadow-lg">
        <div className="max-w-4xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-white">
                Todo App
              </h1>
              <p className="text-sm text-purple-200">
                Phase II - Full-Stack Web Application
              </p>
            </div>
            <button
              onClick={() => setShowForm(!showForm)}
              className="btn-primary"
            >
              {showForm ? 'Cancel' : '+ Add Task'}
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 py-8">
        {/* Task Form */}
        {showForm && (
          <div className="mb-8">
            <TaskForm onSuccess={handleTaskCreated} onCancel={() => setShowForm(false)} />
          </div>
        )}

        {/* Search Bar */}
        <div className="mb-4">
          <SearchBar onSearch={handleSearch} />
        </div>

        {/* Filter Bar */}
        <div className="mb-6">
          <FilterBar
            filters={filters}
            onChange={handleFilterChange}
            onClear={handleClearFilters}
          />
        </div>

        {/* Task List */}
        <TaskList
          filters={filters}
          onEdit={handleEdit}
          onDelete={handleDelete}
          refreshTrigger={refreshTrigger}
        />
      </main>

      {/* Edit Modal */}
      {editingTask && (
        <EditTaskModal
          task={editingTask}
          onSave={handleEditSave}
          onClose={handleEditClose}
        />
      )}

      {/* Delete Confirmation */}
      {deletingTask && (
        <ConfirmDialog
          title="Delete Task"
          message={`Are you sure you want to delete "${deletingTask.title}"? This action cannot be undone.`}
          confirmText="Delete"
          onConfirm={handleDeleteConfirm}
          onCancel={handleDeleteCancel}
        />
      )}
    </div>
  );
}
