/**
 * API client for Todo App backend with JWT authentication.
 */

import type {
  Task,
  Category,
  CreateTaskRequest,
  UpdateTaskRequest,
  TaskFilters,
  CreateCategoryRequest,
} from '@/types/task';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * Custom error class for API errors.
 */
export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public details?: unknown
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

/**
 * Get JWT token from localStorage.
 */
function getToken(): string | null {
  if (typeof window !== 'undefined') {
    return localStorage.getItem('auth_token');
  }
  return null;
}

/**
 * Generic fetch wrapper with error handling and JWT authentication.
 */
async function fetchApi<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_URL}${endpoint}`;

  const token = getToken();

  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  // Add Authorization header if token is available
  if (token) {
    (headers as Record<string, string>)['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let errorMessage = `HTTP ${response.status}`;
    try {
      const errorData = await response.json();
      errorMessage = errorData.detail || errorMessage;
    } catch {
      errorMessage = response.statusText || errorMessage;
    }
    throw new ApiError(errorMessage, response.status);
  }

  // Handle 204 No Content
  if (response.status === 204) {
    return {} as T;
  }

  return response.json();
}

/**
 * Task API functions.
 */
export const taskApi = {
  /**
   * Get all tasks with optional filters.
   */
  async getAll(filters?: TaskFilters): Promise<Task[]> {
    const params = new URLSearchParams();

    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== '') {
          params.append(key, String(value));
        }
      });
    }

    const query = params.toString();
    const endpoint = `/api/tasks${query ? `?${query}` : ''}`;

    const response = await fetchApi<{ data: Task[]; count: number }>(endpoint);
    return response.data;
  },

  /**
   * Get a single task by ID.
   */
  async getById(id: string): Promise<Task> {
    const response = await fetchApi<{ data: Task }>(`/api/tasks/${id}`);
    return response.data;
  },

  /**
   * Create a new task.
   */
  async create(task: CreateTaskRequest): Promise<Task> {
    const response = await fetchApi<{ data: Task; message: string }>(
      '/api/tasks',
      {
        method: 'POST',
        body: JSON.stringify(task),
      }
    );
    return response.data;
  },

  /**
   * Update an existing task.
   */
  async update(id: string, task: UpdateTaskRequest): Promise<Task> {
    const response = await fetchApi<{ data: Task; message: string }>(
      `/api/tasks/${id}`,
      {
        method: 'PUT',
        body: JSON.stringify(task),
      }
    );
    return response.data;
  },

  /**
   * Delete a task.
   */
  async delete(id: string): Promise<void> {
    await fetchApi<{ message: string }>(`/api/tasks/${id}`, {
      method: 'DELETE',
    });
  },

  /**
   * Toggle task completion status.
   */
  async toggle(id: string): Promise<Task> {
    const response = await fetchApi<{ data: Task; message: string }>(
      `/api/tasks/${id}/toggle`,
      {
        method: 'PATCH',
      }
    );
    return response.data;
  },
};

/**
 * Category API functions.
 */
export const categoryApi = {
  /**
   * Get all categories.
   */
  async getAll(): Promise<Category[]> {
    const response = await fetchApi<{ data: Category[]; count: number }>(
      '/api/categories'
    );
    return response.data;
  },

  /**
   * Create a new category.
   */
  async create(category: CreateCategoryRequest): Promise<Category> {
    const response = await fetchApi<{ data: Category; message: string }>(
      '/api/categories',
      {
        method: 'POST',
        body: JSON.stringify(category),
      }
    );
    return response.data;
  },
};
