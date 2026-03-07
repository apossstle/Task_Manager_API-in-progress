// types.ts — общие типы для всего фронтенда

export interface Task {
  id: number;
  title: string;
  description: string | null;
  status: TaskStatus;
  priority: TaskPriority;
  owner_id: number;
  due_date: string | null;
}

export interface TaskCreate {
  title: string;
  description?: string;
  priority?: TaskPriority;
  due_date?: string;
}

export interface TaskUpdate {
  title?: string;
  description?: string;
  status?: TaskStatus;
  priority?: TaskPriority;
}

export interface User {
  id: number;
  email: string;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export type TaskStatus = 'todo' | 'in_progress' | 'done';
export type TaskPriority = 1 | 2 | 3;
export type StatusFilter = 'all' | TaskStatus;
export type PriorityFilter = 0 | TaskPriority;  // 0 = все
