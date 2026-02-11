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
  due_date: string | null;
  is_recurring: boolean;
  recurrence_id: string | null;
  parent_task_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface RecurrenceRequest {
  frequency: 'DAILY' | 'WEEKLY' | 'MONTHLY';
  interval: number;
  day_of_week?: number;
  day_of_month?: number;
  end_date?: string;
}

export interface ReminderRequest {
  offset_minutes: number;
  channel: 'EMAIL' | 'PUSH' | 'BOTH';
}

export interface CreateTaskRequest {
  title: string;
  description?: string;
  priority?: Priority;
  category_id?: string;
  due_date?: string;
  recurrence?: RecurrenceRequest;
  reminder?: ReminderRequest;
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
