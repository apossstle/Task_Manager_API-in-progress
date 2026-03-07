// api.ts — HTTP-клиент для работы с backend API

import type { Task, TaskCreate, TaskUpdate, User, TokenResponse } from './types';

const BASE = '';  // относительные пути — работает при запуске через FastAPI

// ── Token storage ──────────────────────────────────────────────────────────

export function getToken(): string | null {
  return localStorage.getItem('token');
}

export function saveToken(token: string, email: string): void {
  localStorage.setItem('token', token);
  localStorage.setItem('userEmail', email);
}

export function clearToken(): void {
  localStorage.removeItem('token');
  localStorage.removeItem('userEmail');
}

// ── Request helpers ────────────────────────────────────────────────────────

function authHeaders(json = false): HeadersInit {
  const h: Record<string, string> = {};
  const t = getToken();
  if (t) h['Authorization'] = `Bearer ${t}`;
  if (json) h['Content-Type'] = 'application/json';
  return h;
}

async function handleResponse<T>(res: Response): Promise<T> {
  if (res.status === 401) {
    clearToken();
    window.location.href = '/';
    throw new Error('Unauthorized');
  }
  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: 'Неизвестная ошибка' }));
    const msg = typeof body.detail === 'string' ? body.detail : JSON.stringify(body.detail);
    throw new Error(msg);
  }
  if (res.status === 204) return {} as T;
  return res.json() as Promise<T>;
}

// ── Auth API ───────────────────────────────────────────────────────────────

export async function register(email: string, password: string): Promise<User> {
  const res = await fetch(`${BASE}/users/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });
  return handleResponse<User>(res);
}

export async function login(email: string, password: string): Promise<string> {
  const form = new FormData();
  form.append('username', email);
  form.append('password', password);
  const res = await fetch(`${BASE}/users/login`, { method: 'POST', body: form });
  const data = await handleResponse<TokenResponse>(res);
  saveToken(data.access_token, email);
  return data.access_token;
}

export function logout(): void {
  clearToken();
  window.location.href = '/';
}

// ── Tasks API ──────────────────────────────────────────────────────────────

export async function getTasks(): Promise<Task[]> {
  const res = await fetch(`${BASE}/tasks`, { headers: authHeaders() });
  return handleResponse<Task[]>(res);
}

export async function createTask(data: TaskCreate): Promise<Task> {
  const res = await fetch(`${BASE}/tasks`, {
    method: 'POST',
    headers: authHeaders(true),
    body: JSON.stringify(data),
  });
  return handleResponse<Task>(res);
}

export async function updateTask(id: number, data: TaskUpdate): Promise<Task> {
  const res = await fetch(`${BASE}/tasks/${id}`, {
    method: 'PUT',
    headers: authHeaders(true),
    body: JSON.stringify(data),
  });
  return handleResponse<Task>(res);
}

export async function deleteTask(id: number): Promise<void> {
  const res = await fetch(`${BASE}/tasks/${id}`, {
    method: 'DELETE',
    headers: authHeaders(),
  });
  return handleResponse<void>(res);
}
