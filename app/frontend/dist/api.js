"use strict";
// api.ts — HTTP-клиент для работы с backend API
Object.defineProperty(exports, "__esModule", { value: true });
exports.getToken = getToken;
exports.saveToken = saveToken;
exports.clearToken = clearToken;
exports.register = register;
exports.login = login;
exports.logout = logout;
exports.getTasks = getTasks;
exports.createTask = createTask;
exports.updateTask = updateTask;
exports.deleteTask = deleteTask;
const BASE = ''; // относительные пути — работает при запуске через FastAPI
// ── Token storage ──────────────────────────────────────────────────────────
function getToken() {
    return localStorage.getItem('token');
}
function saveToken(token, email) {
    localStorage.setItem('token', token);
    localStorage.setItem('userEmail', email);
}
function clearToken() {
    localStorage.removeItem('token');
    localStorage.removeItem('userEmail');
}
// ── Request helpers ────────────────────────────────────────────────────────
function authHeaders(json = false) {
    const h = {};
    const t = getToken();
    if (t)
        h['Authorization'] = `Bearer ${t}`;
    if (json)
        h['Content-Type'] = 'application/json';
    return h;
}
async function handleResponse(res) {
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
    if (res.status === 204)
        return {};
    return res.json();
}
// ── Auth API ───────────────────────────────────────────────────────────────
async function register(email, password) {
    const res = await fetch(`${BASE}/users/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
    });
    return handleResponse(res);
}
async function login(email, password) {
    const form = new FormData();
    form.append('username', email);
    form.append('password', password);
    const res = await fetch(`${BASE}/users/login`, { method: 'POST', body: form });
    const data = await handleResponse(res);
    saveToken(data.access_token, email);
    return data.access_token;
}
function logout() {
    clearToken();
    window.location.href = '/';
}
// ── Tasks API ──────────────────────────────────────────────────────────────
async function getTasks() {
    const res = await fetch(`${BASE}/tasks`, { headers: authHeaders() });
    return handleResponse(res);
}
async function createTask(data) {
    const res = await fetch(`${BASE}/tasks`, {
        method: 'POST',
        headers: authHeaders(true),
        body: JSON.stringify(data),
    });
    return handleResponse(res);
}
async function updateTask(id, data) {
    const res = await fetch(`${BASE}/tasks/${id}`, {
        method: 'PUT',
        headers: authHeaders(true),
        body: JSON.stringify(data),
    });
    return handleResponse(res);
}
async function deleteTask(id) {
    const res = await fetch(`${BASE}/tasks/${id}`, {
        method: 'DELETE',
        headers: authHeaders(),
    });
    return handleResponse(res);
}
