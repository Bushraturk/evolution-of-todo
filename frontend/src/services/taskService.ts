/**
 * Task API service for frontend
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface Task {
  id: string;
  title: string;
  description?: string;
  completed: boolean;
  priority: 'high' | 'medium' | 'low';
  category_id?: string;
  due_date?: string;
  is_recurring: boolean;
  parent_task_id?: string;
  recurrence_id?: string;
  created_at: string;
  updated_at: string;
}

export interface RecurrenceConfig {
  frequency: 'DAILY' | 'WEEKLY' | 'MONTHLY';
  interval: number;
  day_of_week?: number;
  day_of_month?: number;
  end_date?: string;
}

export interface CreateTaskRequest {
  title: string;
  description?: string;
  priority?: 'high' | 'medium' | 'low';
  category_id?: string;
  due_date?: string;
  recurrence?: RecurrenceConfig;
}

export interface TaskOccurrence {
  id: string;
  due_date: string;
  completed: boolean;
  completed_at?: string;
}

export interface TaskOccurrencesResponse {
  parent_task: {
    id: string;
    title: string;
    is_recurring: boolean;
  };
  occurrences: TaskOccurrence[];
  total: number;
  next_occurrence_date?: string;
}

class TaskService {
  private getAuthToken(): string | null {
    // Get token from localStorage or cookie
    return localStorage.getItem('auth_token');
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const token = this.getAuthToken();
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
      ...options.headers,
    };

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    return response.json();
  }

  async getTasks(filters?: {
    search?: string;
    status?: string;
    priority?: string;
    category_id?: string;
    sort_by?: string;
    sort_order?: string;
  }): Promise<{ data: Task[]; count: number }> {
    const params = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value) params.append(key, value);
      });
    }

    const query = params.toString();
    return this.request<{ data: Task[]; count: number }>(
      `/api/tasks${query ? `?${query}` : ''}`
    );
  }

  async getTask(taskId: string): Promise<{ data: Task }> {
    return this.request<{ data: Task }>(`/api/tasks/${taskId}`);
  }

  async createTask(task: CreateTaskRequest): Promise<{ data: Task; message: string }> {
    return this.request<{ data: Task; message: string }>('/api/tasks', {
      method: 'POST',
      body: JSON.stringify(task),
    });
  }

  async updateTask(
    taskId: string,
    updates: Partial<CreateTaskRequest>
  ): Promise<{ data: Task; message: string }> {
    return this.request<{ data: Task; message: string }>(`/api/tasks/${taskId}`, {
      method: 'PUT',
      body: JSON.stringify(updates),
    });
  }

  async deleteTask(taskId: string): Promise<{ data: Task; message: string }> {
    return this.request<{ data: Task; message: string }>(`/api/tasks/${taskId}`, {
      method: 'DELETE',
    });
  }

  async toggleTask(taskId: string): Promise<{ data: Task; message: string }> {
    return this.request<{ data: Task; message: string }>(
      `/api/tasks/${taskId}/toggle`,
      {
        method: 'PATCH',
      }
    );
  }

  async getTaskOccurrences(taskId: string): Promise<TaskOccurrencesResponse> {
    return this.request<TaskOccurrencesResponse>(
      `/api/tasks/${taskId}/occurrences`
    );
  }

  async stopRecurrence(
    taskId: string,
    options?: { delete_future?: boolean; delete_all?: boolean }
  ): Promise<{ message: string; deleted_count: number; task: any }> {
    const params = new URLSearchParams();
    if (options?.delete_future !== undefined) {
      params.append('delete_future', String(options.delete_future));
    }
    if (options?.delete_all !== undefined) {
      params.append('delete_all', String(options.delete_all));
    }

    const query = params.toString();
    return this.request<{ message: string; deleted_count: number; task: any }>(
      `/api/tasks/${taskId}/recurrence${query ? `?${query}` : ''}`,
      {
        method: 'DELETE',
      }
    );
  }
}

export const taskService = new TaskService();
