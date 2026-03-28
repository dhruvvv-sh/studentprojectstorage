/* sidebar.js — injects shared sidebar + toast container */

function buildSidebar(activePage) {
  const nav = [
    { id: "dashboard",  href: "dashboard.html",  icon: "📊", label: "Dashboard"   },
    { id: "inventory",  href: "inventory.html",  icon: "📦", label: "Inventory"   },
    { id: "usage",      href: "usage.html",       icon: "🔄", label: "Issue / Return" },
    { id: "reports",    href: "reports.html",     icon: "📋", label: "Reports"     },
    { id: "admin",      href: "admin.html",       icon: "🛠️", label: "Admin",  adminOnly: true },
  ];

  const navHtml = nav.map(n => {
    const hide = n.adminOnly ? ' class="nav-item admin-only' + (n.id === activePage ? " active" : "") + '"'
                             : ` class="nav-item${n.id === activePage ? " active" : ""}"`;
    return `<a href="${n.href}"${hide}><span class="nav-icon">${n.icon}</span><span>${n.label}</span></a>`;
  }).join("");

  const html = `
    <aside class="sidebar">
      <div class="sidebar-logo">
        <span class="logo-icon">⚙️</span>
        <div class="logo-title">Robotics Lab</div>
        <div class="logo-sub">Inventory System</div>
      </div>
      <nav class="sidebar-nav">
        <div class="nav-section-label">Navigation</div>
        ${navHtml}
      </nav>
      <div class="sidebar-footer">
        <div class="sidebar-user">
          <div class="user-avatar"><span id="user-avatar-icon">?</span></div>
          <div>
            <div class="user-info-name" id="user-name">Loading…</div>
            <div class="user-info-role" id="user-role"></div>
          </div>
        </div>
        <button class="btn-logout" onclick="doLogout()">⏻ Logout</button>
      </div>
    </aside>
    <div class="toast-container" id="toast-container"></div>
  `;

  document.body.insertAdjacentHTML("afterbegin", html);
}