/**
 * Task and Category TypeScript interfaces for the Todo App.
 */

export type Priority = 'high' | 'medium' | 'low';

export interface Category {
  id: string;
  name: string;
  color: string;
}

export interface Task {
  id: string;
  title: string;
  description: string | null;
  completed: boolean;
  priority: Priority;
  category_id: string | null;
  category: Category | null;
  created_at: string;
  updated_at: string;
}

export interface CreateTaskRequest {
  title: string;
  description?: string;
  priority?: Priority;
  category_id?: string;
}

export interface UpdateTaskRequest {
  title?: string;
  description?: string;
  priority?: Priority;
  category_id?: string | null;
}

export interface TaskFilters {
  search?: string;
  status?: 'all' | 'completed' | 'incomplete';
  priority?: Priority;
  category_id?: string;
  sort_by?: 'created_at' | 'priority' | 'title';
  sort_order?: 'asc' | 'desc';
}

export interface TaskListResponse {
  data: Task[];
  count: number;
}

export interface TaskResponse {
  data: Task;
  message?: string;
}

export interface CategoryListResponse {
  data: Category[];
  count: number;
}

export interface CreateCategoryRequest {
  name: string;
  color?: string;
}
