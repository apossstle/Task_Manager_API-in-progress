// ─────────────────────────────────────────
// Types
// ─────────────────────────────────────────

interface LoginResponse {
  access_token: string;
  token_type: string;
}

interface ApiError {
  detail: string;
}

// ─────────────────────────────────────────
// Utils
// ─────────────────────────────────────────

const API = "http://127.0.0.1:8000";

function el<T extends HTMLElement>(id: string): T {
  return document.getElementById(id) as T;
}

function showStatus(elementId: string, message: string, isError = false): void {
  const statusEl = el<HTMLDivElement>(elementId);
  statusEl.textContent = message;
  statusEl.className = `status-msg show ${isError ? "error" : "success"}`;
  setTimeout(() => statusEl.classList.remove("show"), 3000);
}

function setLoading(btn: HTMLButtonElement, loading: boolean): void {
  if (loading) {
    btn.dataset.original = btn.textContent ?? "";
    btn.innerHTML = 'ЗАГРУЗКА<span class="loading"></span>';
    btn.disabled = true;
  } else {
    btn.textContent = btn.dataset.original ?? "";
    btn.disabled = false;
  }
}

function toggleAuth(): void {
  el("login-section").classList.toggle("hidden");
  el("register-section").classList.toggle("hidden");
}

// ─────────────────────────────────────────
// Register
// ─────────────────────────────────────────

async function register(evt: Event): Promise<void> {
  const email = el<HTMLInputElement>("reg-email").value.trim();
  const password = el<HTMLInputElement>("reg-pass").value;
  if (!email || !password) { showStatus("reg-status", "[ОШИБКА] ЗАПОЛНИТЕ ВСЕ ПОЛЯ", true); return; }
  const btn = evt.currentTarget as HTMLButtonElement;
  setLoading(btn, true);
  try {
    const res = await fetch(`${API}/users/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    if (res.ok) {
      showStatus("reg-status", "[УСПЕШНО] АККАУНТ СОЗДАН");
      el<HTMLInputElement>("reg-email").value = "";
      el<HTMLInputElement>("reg-pass").value = "";
      setTimeout(toggleAuth, 1800);
    } else {
      const err: ApiError = await res.json();
      showStatus("reg-status", `[ОШИБКА] ${err.detail.toUpperCase()}`, true);
    }
  } catch { showStatus("reg-status", "[ОШИБКА] СЕРВЕР НЕДОСТУПЕН", true); }
  finally { setLoading(btn, false); }
}

// ─────────────────────────────────────────
// Login
// ─────────────────────────────────────────

async function login(evt: Event): Promise<void> {
  const email = el<HTMLInputElement>("login-email").value.trim();
  const password = el<HTMLInputElement>("login-pass").value;
  if (!email || !password) { showStatus("login-status", "[ОШИБКА] ЗАПОЛНИТЕ ВСЕ ПОЛЯ", true); return; }
  const btn = evt.currentTarget as HTMLButtonElement;
  setLoading(btn, true);
  try {
    const formData = new FormData();
    formData.append("username", email);
    formData.append("password", password);
    const res = await fetch(`${API}/users/login`, { method: "POST", body: formData });
    if (res.ok) {
      const data: LoginResponse = await res.json();
      localStorage.setItem("token", data.access_token);
      window.location.href = "/tasks-page";
    } else {
      const err: ApiError = await res.json();
      showStatus("login-status", `[ОШИБКА] ${err.detail.toUpperCase()}`, true);
    }
  } catch { showStatus("login-status", "[ОШИБКА] СЕРВЕР НЕДОСТУПЕН", true); }
  finally { setLoading(btn, false); }
}

// ─────────────────────────────────────────
// Bootstrap
// ─────────────────────────────────────────

document.addEventListener("DOMContentLoaded", () => {
  if (localStorage.getItem("token")) { window.location.href = "/tasks-page"; return; }
  el("btn-login").addEventListener("click", login );
  el("btn-register").addEventListener("click", register );
  el("link-to-register").addEventListener("click", toggleAuth);
  el("link-to-login").addEventListener("click", toggleAuth);
  ["login-email", "login-pass"].forEach(id => {
    el<HTMLInputElement>(id).addEventListener("keypress", (e: KeyboardEvent) => {
      if (e.key === "Enter") el<HTMLButtonElement>("btn-login").click();
    });
  });
  ["reg-email", "reg-pass"].forEach(id => {
    el<HTMLInputElement>(id).addEventListener("keypress", (e: KeyboardEvent) => {
      if (e.key === "Enter") el<HTMLButtonElement>("btn-register").click();
    });
  });
});
export {};
