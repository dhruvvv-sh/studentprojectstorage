/* api.js — shared utilities for all pages */

const API_BASE = "/api";

/* ── Core API helper ───────────────────────────────────────────── */
const api = {
  async request(method, path, body) {
    const opts = {
      method,
      credentials: "include",
      headers: {},
    };
    if (body !== undefined) {
      opts.headers["Content-Type"] = "application/json";
      opts.body = JSON.stringify(body);
    }
    try {
      const res = await fetch(API_BASE + path, opts);
      if (res.status === 401) {
        window.location.href = "login.html";
        return null;
      }
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Request failed");
      return data;
    } catch (err) {
      throw err;
    }
  },
  get:    (path)       => api.request("GET",    path),
  post:   (path, body) => api.request("POST",   path, body),
  put:    (path, body) => api.request("PUT",    path, body),
  delete: (path)       => api.request("DELETE", path),
};

/* ── Auth guard ─────────────────────────────────────────────────── */
async function requireAuth() {
  const user = await api.get("/auth/me");
  if (!user) return null;
  document.getElementById("user-name").textContent  = user.full_name || user.username;
  document.getElementById("user-role").textContent  = user.role.replace("_", " ");
  document.getElementById("user-avatar-icon").textContent = (user.full_name || user.username)[0].toUpperCase();

  // Show/hide admin-only elements
  const isAdmin = ["admin", "lab_incharge"].includes(user.role);
  document.querySelectorAll(".admin-only").forEach(el => {
    el.style.display = isAdmin ? "" : "none";
  });
  // Hide write-only elements for guest
  if (user.role === "guest") {
    document.querySelectorAll(".write-only").forEach(el => el.style.display = "none");
  }
  return user;
}

/* ── Logout ─────────────────────────────────────────────────────── */
async function doLogout() {
  await api.post("/auth/logout");
  window.location.href = "login.html";
}

/* ── Toast notifications ─────────────────────────────────────────── */
function toast(message, type = "info") {
  const container = document.getElementById("toast-container");
  if (!container) return;
  const el = document.createElement("div");
  el.className = `toast toast-${type}`;
  const icons = { success: "✅", error: "❌", info: "ℹ️" };
  el.innerHTML = `<span>${icons[type] || "ℹ️"}</span><span>${message}</span>`;
  container.appendChild(el);
  setTimeout(() => el.remove(), 3500);
}

/* ── Modal helpers ───────────────────────────────────────────────── */
function openModal(id) {
  const el = document.getElementById(id);
  if (el) el.classList.add("open");
}
function closeModal(id) {
  const el = document.getElementById(id);
  if (el) el.classList.remove("open");
}

/* ── Badge helper ────────────────────────────────────────────────── */
function statusBadge(name) {
  if (!name) return "—";
  const cls = {
    "Available": "badge-available",
    "In Use":    "badge-inuse",
    "Borrowed":  "badge-borrowed",
  }[name] || "badge-inuse";
  return `<span class="badge ${cls}">${name}</span>`;
}

function roleBadge(role) {
  return `<span class="badge badge-${role}">${role.replace("_", " ")}</span>`;
}

/* ── Quantity bar ─────────────────────────────────────────────────── */
function qtyBar(available, total) {
  if (!total) return "0 / 0";
  const pct = Math.max(0, Math.round((available / total) * 100));
  const color = pct < 20 ? "var(--red)" : pct < 50 ? "var(--amber)" : "var(--green)";
  return `
    <div class="qty-bar">
      <span style="font-family:var(--font-mono);font-size:11px;color:var(--text-muted);min-width:40px">${available}/${total}</span>
      <div class="qty-track"><div class="qty-fill" style="width:${pct}%;background:${color}"></div></div>
    </div>`;
}

/* ── Date formatter ──────────────────────────────────────────────── */
function fmtDate(d) {
  if (!d) return "—";
  return new Date(d + "T00:00:00").toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" });
}

/* ── Days indicator ──────────────────────────────────────────────── */
function daysOut(issueDate) {
  if (!issueDate) return "";
  const diff = Math.floor((Date.now() - new Date(issueDate + "T00:00:00")) / 86400000);
  const color = diff > 7 ? "var(--red)" : diff > 3 ? "var(--amber)" : "var(--text-muted)";
  return `<span style="font-size:10px;color:${color};font-family:var(--font-mono)">${diff}d</span>`;
}

/* ── Table "no data" ─────────────────────────────────────────────── */
function noDataRow(colSpan, message = "No records found") {
  return `<tr><td colspan="${colSpan}">
    <div class="empty-state">
      <div class="empty-icon">📭</div>
      <div>${message}</div>
    </div>
  </td></tr>`;
}

/* ── Populate select ─────────────────────────────────────────────── */
function populateSelect(selectId, items, valueKey, labelKey, placeholder = "— Select —") {
  const sel = document.getElementById(selectId);
  if (!sel) return;
  sel.innerHTML = `<option value="">${placeholder}</option>` +
    items.map(i => `<option value="${i[valueKey]}">${i[labelKey]}</option>`).join("");
}
