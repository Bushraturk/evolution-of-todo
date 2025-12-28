/**
 * Priority utility functions and color mappings.
 */

import type { Priority } from '@/types/task';

export const priorityColors: Record<Priority, string> = {
  high: '#EF4444',
  medium: '#F59E0B',
  low: '#6B7280',
};

export const priorityLabels: Record<Priority, string> = {
  high: 'High',
  medium: 'Medium',
  low: 'Low',
};

export const priorityBgColors: Record<Priority, string> = {
  high: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
  medium: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
  low: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200',
};
