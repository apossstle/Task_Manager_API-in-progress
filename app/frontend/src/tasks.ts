// ─────────────────────────────────────────
// Types
// ─────────────────────────────────────────

type TaskStatus = "todo" | "in_progress" | "done";
type TaskPriority = 1 | 2 | 3;

interface Task {
  id: number;
  title: string;
  description: string | null;
  status: TaskStatus;
  priority: TaskPriority;
  due_date: string | null;
  owner_id: number;
}

interface TaskCreatePayload {
  title: string;
  description?: string;
  priority: TaskPriority;
  due_date?: string;
}

interface TaskUpdatePayload {
  title?: string;
  description?: string;
  status?: TaskStatus;
  priority?: TaskPriority;
}

interface FilterState {
  status: TaskStatus | "all";
  priority: TaskPriority | 0;
}

// ─────────────────────────────────────────
// State
// ─────────────────────────────────────────

const API = "http://127.0.0.1:8000";
let token: string = localStorage.getItem("token") ?? "";
let allTasks: Task[] = [];
let filters: FilterState = { status: "all", priority: 0 };

// ─────────────────────────────────────────
// Utils
// ─────────────────────────────────────────

function el<T extends HTMLElement>(id: string): T {
  return document.getElementById(id) as T;
}

function authHeaders(): HeadersInit {
  return { Authorization: `Bearer ${token}`, "Content-Type": "application/json" };
}

function escapeHtml(text: string): string {
  const d = document.createElement("div");
  d.textContent = text;
  return d.innerHTML;
}

function formatDate(iso: string | null): string {
  if (!iso) return "";
  return new Date(iso).toLocaleDateString("ru-RU", { day: "2-digit", month: "2-digit", year: "numeric" });
}

const STATUS_NEXT: Record<TaskStatus, TaskStatus> = {
  todo: "in_progress",
  in_progress: "done",
  done: "todo",
};

const STATUS_LABEL: Record<TaskStatus, string> = {
  todo: "[  ] TODO",
  in_progress: "[--] В РАБОТЕ",
  done: "[XX] ГОТОВО",
};

const PRIORITY_LABEL: Record<TaskPriority, string> = {
  1: "LOW",
  2: "MED",
  3: "HIGH",
};

// ─────────────────────────────────────────
// API calls
// ─────────────────────────────────────────

async function fetchTasks(): Promise<void> {
  try {
    const res = await fetch(`${API}/tasks`, { headers: authHeaders() });
    if (res.status === 401) { logout(); return; }
    if (res.ok) { allTasks = await res.json(); renderAll(); }
  } catch { showToast("ОШИБКА ЗАГРУЗКИ", true); }
}

async function createTask(): Promise<void> {
  const titleEl = el<HTMLInputElement>("task-title");
  const descEl = el<HTMLInputElement>("task-desc");
  const prioEl = el<HTMLSelectElement>("task-priority");
  const dueEl = el<HTMLInputElement>("task-due");
  const title = titleEl.value.trim();
  if (!title) { titleEl.classList.add("shake"); setTimeout(() => titleEl.classList.remove("shake"), 400); return; }
  const payload: TaskCreatePayload = {
    title,
    priority: parseInt(prioEl.value) as TaskPriority,
  };
  if (descEl.value.trim()) payload.description = descEl.value.trim();
  if (dueEl.value) payload.due_date = new Date(dueEl.value).toISOString();
  try {
    const res = await fetch(`${API}/tasks`, {
      method: "POST",
      headers: authHeaders(),
      body: JSON.stringify(payload),
    });
    if (res.ok) {
      titleEl.value = ""; descEl.value = ""; dueEl.value = "";
      showToast("ЗАДАЧА ДОБАВЛЕНА");
      await fetchTasks();
    }
  } catch { showToast("ОШИБКА СОЗДАНИЯ", true); }
}

async function updateTaskStatus(id: number, currentStatus: TaskStatus): Promise<void> {
  const payload: TaskUpdatePayload = { status: STATUS_NEXT[currentStatus] };
  try {
    const res = await fetch(`${API}/tasks/${id}`, {
      method: "PUT", headers: authHeaders(), body: JSON.stringify(payload),
    });
    if (res.ok) await fetchTasks();
  } catch { showToast("ОШИБКА ОБНОВЛЕНИЯ", true); }
}

async function deleteTask(id: number): Promise<void> {
  const confirmed = await showConfirm("УДАЛИТЬ ЗАДАЧУ?");
  if (!confirmed) return;
  try {
    const res = await fetch(`${API}/tasks/${id}`, {
      method: "DELETE", headers: { Authorization: `Bearer ${token}` },
    });
    if (res.ok) { showToast("ЗАДАЧА УДАЛЕНА"); await fetchTasks(); }
  } catch { showToast("ОШИБКА УДАЛЕНИЯ", true); }
}

// ─────────────────────────────────────────
// Render
// ─────────────────────────────────────────

function applyFilters(tasks: Task[]): Task[] {
  return tasks.filter(t => {
    const statusOk = filters.status === "all" || t.status === filters.status;
    const prioOk = filters.priority === 0 || t.priority === filters.priority;
    return statusOk && prioOk;
  });
}

function renderAll(): void {
  renderStats();
  renderTasks(applyFilters(allTasks));
}

function renderStats(): void {
  const todo = allTasks.filter(t => t.status === "todo").length;
  const inprog = allTasks.filter(t => t.status === "in_progress").length;
  const done = allTasks.filter(t => t.status === "done").length;
  el("stat-total").textContent = String(allTasks.length);
  el("stat-todo").textContent = String(todo);
  el("stat-inprog").textContent = String(inprog);
  el("stat-done").textContent = String(done);
}

function renderTasks(tasks: Task[]): void {
  const list = el<HTMLUListElement>("tasks-list");
  if (tasks.length === 0) {
    list.innerHTML = `<li class="empty-state">[ ЗАДАЧ НЕТ ]</li>`;
    return;
  }
  list.innerHTML = tasks.map(task => `
    <li class="task-item priority-${task.priority}" data-id="${task.id}">
      <div class="task-main">
        <div class="task-badges">
          <span class="badge badge-status status-${task.status}">${STATUS_LABEL[task.status]}</span>
          <span class="badge badge-priority prio-${task.priority}">${PRIORITY_LABEL[task.priority as TaskPriority]}</span>
          ${task.due_date ? `<span class="badge badge-due">📅 ${formatDate(task.due_date)}</span>` : ""}
        </div>
        <div class="task-title">${escapeHtml(task.title)}</div>
        ${task.description ? `<div class="task-desc">${escapeHtml(task.description)}</div>` : ""}
      </div>
      <div class="task-actions">
        <button class="task-btn btn-cycle" data-id="${task.id}" data-status="${task.status}" title="Следующий статус">◯</button>
        <button class="task-btn btn-delete" data-id="${task.id}" title="Удалить">✕</button>
      </div>
    </li>
  `).join("");

  list.querySelectorAll<HTMLButtonElement>(".btn-cycle").forEach(btn => {
    btn.addEventListener("click", () => {
      updateTaskStatus(Number(btn.dataset.id), btn.dataset.status as TaskStatus);
    });
  });
  list.querySelectorAll<HTMLButtonElement>(".btn-delete").forEach(btn => {
    btn.addEventListener("click", () => deleteTask(Number(btn.dataset.id)));
  });
}

// ─────────────────────────────────────────
// Toast
// ─────────────────────────────────────────

function showToast(msg: string, isError = false): void {
  const t = document.createElement("div");
  t.className = `toast ${isError ? "toast-error" : "toast-ok"}`;
  t.textContent = msg;
  document.body.appendChild(t);
  requestAnimationFrame(() => t.classList.add("toast-show"));
  setTimeout(() => { t.classList.remove("toast-show"); setTimeout(() => t.remove(), 400); }, 2500);
}

// ─────────────────────────────────────────
// Confirm dialog
// ─────────────────────────────────────────

function showConfirm(msg: string): Promise<boolean> {
  return new Promise(resolve => {
    const overlay = document.createElement("div");
    overlay.className = "confirm-overlay";
    overlay.innerHTML = `
      <div class="confirm-box">
        <div class="confirm-msg">${msg}</div>
        <div class="confirm-btns">
          <button class="btn" id="confirm-yes">ДА</button>
          <button class="btn btn-outline" id="confirm-no">НЕТ</button>
        </div>
      </div>`;
    document.body.appendChild(overlay);
    overlay.querySelector("#confirm-yes")!.addEventListener("click", () => { overlay.remove(); resolve(true); });
    overlay.querySelector("#confirm-no")!.addEventListener("click", () => { overlay.remove(); resolve(false); });
  });
}

// ─────────────────────────────────────────
// Filters
// ─────────────────────────────────────────

function setFilter(type: "status" | "priority", value: string): void {
  if (type === "status") filters.status = value as FilterState["status"];
  else filters.priority = parseInt(value) as FilterState["priority"];

  document.querySelectorAll<HTMLButtonElement>(`[data-filter-${type}]`).forEach(btn => {
    btn.classList.toggle("active", btn.dataset[`filter${type.charAt(0).toUpperCase() + type.slice(1)}`] === value);
  });
  renderAll();
}

// ─────────────────────────────────────────
// Auth
// ─────────────────────────────────────────

function logout(): void {
  localStorage.removeItem("token");
  window.location.href = "/";
}

// ─────────────────────────────────────────
// Bootstrap
// ─────────────────────────────────────────

document.addEventListener("DOMContentLoaded", () => {
  if (!token) { window.location.href = "/"; return; }

  el("btn-add").addEventListener("click", createTask);
  el("btn-logout").addEventListener("click", logout);
  el<HTMLInputElement>("task-title").addEventListener("keypress", (e: KeyboardEvent) => {
    if (e.key === "Enter") createTask();
  });

  // Filter buttons
  document.querySelectorAll<HTMLButtonElement>("[data-filter-status]").forEach(btn => {
    btn.addEventListener("click", () => setFilter("status", btn.dataset.filterStatus!));
  });
  document.querySelectorAll<HTMLButtonElement>("[data-filter-priority]").forEach(btn => {
    btn.addEventListener("click", () => setFilter("priority", btn.dataset.filterPriority!));
  });

  fetchTasks();
});
export {};
