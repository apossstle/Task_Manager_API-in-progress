"use strict";
// ─────────────────────────────────────────
// Types
// ─────────────────────────────────────────
Object.defineProperty(exports, "__esModule", { value: true });
// ─────────────────────────────────────────
// Utils
// ─────────────────────────────────────────
const API = "http://127.0.0.1:8000";
function el(id) {
    return document.getElementById(id);
}
function showStatus(elementId, message, isError = false) {
    const statusEl = el(elementId);
    statusEl.textContent = message;
    statusEl.className = `status-msg show ${isError ? "error" : "success"}`;
    setTimeout(() => statusEl.classList.remove("show"), 3000);
}
function setLoading(btn, loading) {
    if (loading) {
        btn.dataset.original = btn.textContent ?? "";
        btn.innerHTML = 'ЗАГРУЗКА<span class="loading"></span>';
        btn.disabled = true;
    }
    else {
        btn.textContent = btn.dataset.original ?? "";
        btn.disabled = false;
    }
}
function toggleAuth() {
    el("login-section").classList.toggle("hidden");
    el("register-section").classList.toggle("hidden");
}
// ─────────────────────────────────────────
// Register
// ─────────────────────────────────────────
async function register(evt) {
    const email = el("reg-email").value.trim();
    const password = el("reg-pass").value;
    if (!email || !password) {
        showStatus("reg-status", "[ОШИБКА] ЗАПОЛНИТЕ ВСЕ ПОЛЯ", true);
        return;
    }
    const btn = evt.currentTarget;
    setLoading(btn, true);
    try {
        const res = await fetch(`${API}/users/register`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password }),
        });
        if (res.ok) {
            showStatus("reg-status", "[УСПЕШНО] АККАУНТ СОЗДАН");
            el("reg-email").value = "";
            el("reg-pass").value = "";
            setTimeout(toggleAuth, 1800);
        }
        else {
            const err = await res.json();
            showStatus("reg-status", `[ОШИБКА] ${err.detail.toUpperCase()}`, true);
        }
    }
    catch {
        showStatus("reg-status", "[ОШИБКА] СЕРВЕР НЕДОСТУПЕН", true);
    }
    finally {
        setLoading(btn, false);
    }
}
// ─────────────────────────────────────────
// Login
// ─────────────────────────────────────────
async function login(evt) {
    const email = el("login-email").value.trim();
    const password = el("login-pass").value;
    if (!email || !password) {
        showStatus("login-status", "[ОШИБКА] ЗАПОЛНИТЕ ВСЕ ПОЛЯ", true);
        return;
    }
    const btn = evt.currentTarget;
    setLoading(btn, true);
    try {
        const formData = new FormData();
        formData.append("username", email);
        formData.append("password", password);
        const res = await fetch(`${API}/users/login`, { method: "POST", body: formData });
        if (res.ok) {
            const data = await res.json();
            localStorage.setItem("token", data.access_token);
            window.location.href = "/tasks-page";
        }
        else {
            const err = await res.json();
            showStatus("login-status", `[ОШИБКА] ${err.detail.toUpperCase()}`, true);
        }
    }
    catch {
        showStatus("login-status", "[ОШИБКА] СЕРВЕР НЕДОСТУПЕН", true);
    }
    finally {
        setLoading(btn, false);
    }
}
// ─────────────────────────────────────────
// Bootstrap
// ─────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
    if (localStorage.getItem("token")) {
        window.location.href = "/tasks-page";
        return;
    }
    el("btn-login").addEventListener("click", login);
    el("btn-register").addEventListener("click", register);
    el("link-to-register").addEventListener("click", toggleAuth);
    el("link-to-login").addEventListener("click", toggleAuth);
    ["login-email", "login-pass"].forEach(id => {
        el(id).addEventListener("keypress", (e) => {
            if (e.key === "Enter")
                el("btn-login").click();
        });
    });
    ["reg-email", "reg-pass"].forEach(id => {
        el(id).addEventListener("keypress", (e) => {
            if (e.key === "Enter")
                el("btn-register").click();
        });
    });
});
