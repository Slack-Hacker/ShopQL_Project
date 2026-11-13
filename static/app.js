// ShopQL Simple & Intuitive Studio Logic

let currentResults = [];
let currentColumns = [];
let currentAst = null;
let astDisplayMode = "tree"; // "tree" or "json"
let viewMode = "cards"; // "cards" or "table"

const PRESETS = [
  { label: "🔍 Electronics < $2,000", query: 'FIND PRODUCTS\nWHERE PRICE < 2000\nAND CATEGORY = "ELECTRONICS";' },
  { label: "⭐ Rating >= 4.5 (Sort Price)", query: "SHOW PRODUCTS\nWHERE RATING >= 4.5\nORDER BY PRICE ASC;" },
  { label: "➕ Add Laptop ($55,000)", query: 'ADD PRODUCT "Laptop" PRICE 55000;' },
  { label: "🛒 Buy 2 MacBooks", query: 'BUY PRODUCT "MacBook Pro 16" QUANTITY 2;' },
  { label: "📦 Restock Laptop (+15)", query: 'RESTOCK PRODUCT "Laptop" QUANTITY 15;' },
  { label: "🎯 Complex Logic", query: 'FIND PRODUCTS\nWHERE (CATEGORY = "ELECTRONICS" OR CATEGORY = "BOOKS")\nAND PRICE BETWEEN 30 AND 500\nORDER BY RATING DESC;' },
];

document.addEventListener("DOMContentLoaded", () => {
  initPresets();
  initTabs();
  initEvents();
  // Run default query on initial load
  document.getElementById("queryInput").value = PRESETS[0].query;
  runQuery();
  loadCatalog();
});

function initPresets() {
  const container = document.getElementById("presetButtons");
  container.innerHTML = "";
  PRESETS.forEach(p => {
    const chip = document.createElement("button");
    chip.className = "chip-btn";
    chip.textContent = p.label;
    chip.addEventListener("click", () => {
      document.getElementById("queryInput").value = p.query;
      runQuery();
    });
    container.appendChild(chip);
  });
}

function initTabs() {
  const tabs = document.querySelectorAll(".tab-item");
  tabs.forEach(tab => {
    tab.addEventListener("click", () => {
      tabs.forEach(t => t.classList.remove("active"));
      document.querySelectorAll(".tab-pane").forEach(p => p.classList.remove("active"));
      
      tab.classList.add("active");
      const targetId = tab.getAttribute("data-tab");
      const pane = document.getElementById(targetId);
      if (pane) pane.classList.add("active");

      if (targetId === "tab-catalog") {
        loadCatalog();
      }
    });
  });

  // Switch Cards vs Table
  document.getElementById("btnModeCards").addEventListener("click", () => {
    viewMode = "cards";
    document.getElementById("btnModeCards").classList.add("active");
    document.getElementById("btnModeTable").classList.remove("active");
    renderResultsView();
  });

  document.getElementById("btnModeTable").addEventListener("click", () => {
    viewMode = "table";
    document.getElementById("btnModeTable").classList.add("active");
    document.getElementById("btnModeCards").classList.remove("active");
    renderResultsView();
  });

  // AST tree vs json
  document.getElementById("btnAstTree").addEventListener("click", () => {
    astDisplayMode = "tree";
    document.getElementById("btnAstTree").classList.add("active");
    document.getElementById("btnAstJson").classList.remove("active");
    renderAst();
  });

  document.getElementById("btnAstJson").addEventListener("click", () => {
    astDisplayMode = "json";
    document.getElementById("btnAstJson").classList.add("active");
    document.getElementById("btnAstTree").classList.remove("active");
    renderAst();
  });
}

function initEvents() {
  const queryInput = document.getElementById("queryInput");
  const btnRun = document.getElementById("btnRun");
  const btnClear = document.getElementById("btnClear");
  const btnResetCatalog = document.getElementById("btnResetCatalog");
  const closeErrorBtn = document.getElementById("closeErrorBtn");
  const searchInput = document.getElementById("catalogSearchInput");

  btnRun.addEventListener("click", runQuery);

  btnClear.addEventListener("click", () => {
    queryInput.value = "";
    queryInput.focus();
  });

  closeErrorBtn.addEventListener("click", () => {
    document.getElementById("errorBanner").style.display = "none";
  });

  queryInput.addEventListener("keydown", (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
      e.preventDefault();
      runQuery();
    }
  });

  btnResetCatalog.addEventListener("click", async () => {
    if (confirm("Reset catalog back to initial default seed inventory?")) {
      try {
        const resp = await fetch("/api/reset", { method: "POST" });
        const data = await resp.json();
        alert(data.message);
        loadCatalog();
        runQuery();
      } catch (err) {
        alert("Failed to reset catalog: " + err);
      }
    }
  });

  searchInput.addEventListener("input", (e) => {
    const q = e.target.value.toLowerCase();
    const rows = document.querySelectorAll("#catalogFullBody tr");
    rows.forEach(r => {
      r.style.display = r.textContent.toLowerCase().includes(q) ? "" : "none";
    });
  });
}

async function runQuery() {
  const query = document.getElementById("queryInput").value.trim();
  const errorBanner = document.getElementById("errorBanner");
  const errorText = document.getElementById("errorText");
  const timingBadge = document.getElementById("timingBadge");

  if (!query) return;

  try {
    const res = await fetch("/api/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query })
    });
    const data = await res.json();

    if (!data.success) {
      errorBanner.style.display = "block";
      errorText.textContent = data.error;
      timingBadge.style.display = "none";
      return;
    }

    // Success
    errorBanner.style.display = "none";
    timingBadge.style.display = "inline-block";
    timingBadge.textContent = `⚡ Compile: ${data.compile_time_ms}ms | Total: ${data.total_time_ms}ms`;

    const lastResult = data.results[data.results.length - 1];
    currentResults = lastResult.rows || [];
    currentColumns = lastResult.columns || [];
    currentAst = data.ast;

    // Update product count badge
    document.getElementById("productCountBadge").textContent = currentResults.length;

    // Display message
    const msgEl = document.getElementById("queryMessage");
    msgEl.style.display = "block";
    msgEl.textContent = `✔ ${lastResult.statement_type}: ${lastResult.message}`;

    renderResultsView();
    renderAst();
    renderTokens(data.tokens);

    // If query updated database, refresh catalog view
    if (["ADD", "UPDATE", "DELETE", "RESTOCK", "PURCHASE"].includes(lastResult.statement_type)) {
      loadCatalog();
    }

  } catch (err) {
    errorBanner.style.display = "block";
    errorText.textContent = "Network Error: " + err.message;
  }
}

function renderResultsView() {
  const cardsGrid = document.getElementById("cardsGrid");
  const tableView = document.getElementById("tableView");

  if (viewMode === "cards") {
    cardsGrid.style.display = "grid";
    tableView.style.display = "none";
    renderCards();
  } else {
    cardsGrid.style.display = "none";
    tableView.style.display = "block";
    renderTable();
  }
}

// Render Product Cards
function renderCards() {
  const grid = document.getElementById("cardsGrid");
  grid.innerHTML = "";

  if (currentResults.length === 0) {
    grid.innerHTML = `<div class="empty-state" style="grid-column: 1/-1;">No products found matching query.</div>`;
    return;
  }

  currentResults.forEach(p => {
    // If result is count or describe
    if (p.count !== undefined) {
      grid.innerHTML = `<div class="product-card" style="grid-column: 1/-1; text-align: center; padding: 30px;">
        <h2 style="font-size: 36px; color: var(--primary);">${p.count}</h2>
        <p style="color: var(--text-secondary);">Total Matching Products</p>
      </div>`;
      return;
    }

    const card = document.createElement("div");
    card.className = "product-card";

    const stock = parseInt(p.stock || 0);
    const stockClass = stock === 0 ? "stock-out" : stock <= 5 ? "stock-low" : "stock-in";
    const stockText = stock === 0 ? "Out of Stock" : stock <= 5 ? `${stock} left (Low)` : `${stock} in stock`;

    card.innerHTML = `
      <div>
        <div class="card-top">
          <span class="card-category">${p.category || "GENERAL"}</span>
          <span class="card-rating">★ ${parseFloat(p.rating || 5).toFixed(1)}</span>
        </div>
        <h3 class="card-title">${escapeHtml(p.name || "Product")}</h3>
        <p class="card-desc">${escapeHtml(p.description || "")}</p>
      </div>
      <div>
        <div class="card-bottom">
          <span class="card-price">$${parseFloat(p.price || 0).toFixed(2)}</span>
          <span class="stock-tag ${stockClass}">${stockText}</span>
        </div>
        <div class="card-actions">
          <button class="btn-card-buy" ${stock === 0 ? "disabled" : ""} onclick="buyProduct('${escapeHtml(p.name || "")}')">
            🛒 Buy 1 Unit
          </button>
          <button class="btn-card-buy" style="border-color: rgba(16, 185, 129, 0.4); color: #34d399;" onclick="restockProduct('${escapeHtml(p.name || "")}')">
            📦 +10 Restock
          </button>
        </div>
      </div>
    `;
    grid.appendChild(card);
  });
}

// Quick action handlers from cards
window.buyProduct = function(name) {
  document.getElementById("queryInput").value = `BUY PRODUCT "${name}" QUANTITY 1;`;
  runQuery();
};

window.restockProduct = function(name) {
  document.getElementById("queryInput").value = `RESTOCK PRODUCT "${name}" QUANTITY 10;`;
  runQuery();
};

// Render Table
function renderTable() {
  const theadRow = document.getElementById("tableHeadRow");
  const tbody = document.getElementById("tableBody");
  theadRow.innerHTML = "";
  tbody.innerHTML = "";

  if (currentResults.length === 0) {
    tbody.innerHTML = `<tr><td class="empty-state">No rows to display.</td></tr>`;
    return;
  }

  currentColumns.forEach(c => {
    const th = document.createElement("th");
    th.textContent = c.toUpperCase();
    theadRow.appendChild(th);
  });

  currentResults.forEach(r => {
    const tr = document.createElement("tr");
    currentColumns.forEach(c => {
      const td = document.createElement("td");
      const val = r[c];
      if (c === "price" && val !== undefined) {
        td.innerHTML = `<span style="color: var(--emerald); font-weight: 700; font-family: var(--font-mono);">$${parseFloat(val).toFixed(2)}</span>`;
      } else if (c === "stock" && val !== undefined) {
        const s = parseInt(val);
        td.innerHTML = `<span class="stock-tag ${s === 0 ? 'stock-out' : s <= 5 ? 'stock-low' : 'stock-in'}">${s}</span>`;
      } else if (c === "rating" && val !== undefined) {
        td.innerHTML = `<span style="color: var(--amber); font-weight: 700;">★ ${parseFloat(val).toFixed(1)}</span>`;
      } else {
        td.textContent = val !== undefined ? val : "";
      }
      tr.appendChild(td);
    });
    tbody.appendChild(tr);
  });
}

// Render AST Tree
function renderAst() {
  const container = document.getElementById("astViewContainer");
  if (!currentAst) {
    container.innerHTML = `<div class="empty-state">No AST available.</div>`;
    return;
  }

  if (astDisplayMode === "json") {
    container.innerHTML = `<pre style="color: #93c5fd; font-size: 12px;">${JSON.stringify(currentAst, null, 2)}</pre>`;
    return;
  }

  container.innerHTML = "";
  currentAst.forEach(node => {
    container.appendChild(createAstElement(node));
  });
}

function createAstElement(node) {
  const div = document.createElement("div");
  div.className = "ast-node";

  const pill = document.createElement("div");
  pill.className = "ast-pill";

  const type = document.createElement("span");
  type.className = "ast-type";
  type.textContent = node._type || "Node";
  pill.appendChild(type);

  const attrs = [];
  for (const [k, v] of Object.entries(node)) {
    if (k !== "_type" && k !== "line" && k !== "column" && typeof v !== "object") {
      attrs.push(`${k}: ${JSON.stringify(v)}`);
    }
  }

  if (attrs.length > 0) {
    const span = document.createElement("span");
    span.className = "ast-attr";
    span.textContent = `(${attrs.join(", ")})`;
    pill.appendChild(span);
  }
  div.appendChild(pill);

  for (const [k, v] of Object.entries(node)) {
    if (k === "_type" || k === "line" || k === "column") continue;
    if (v && typeof v === "object") {
      if (Array.isArray(v)) {
        v.forEach(child => {
          if (typeof child === "object") div.appendChild(createAstElement(child));
        });
      } else {
        div.appendChild(createAstElement(v));
      }
    }
  }

  return div;
}

// Render Tokens
function renderTokens(tokens) {
  const tbody = document.getElementById("tokensBody");
  tbody.innerHTML = "";
  if (!tokens || tokens.length === 0) return;

  tokens.forEach((t, i) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${i + 1}</td>
      <td><span style="color: #a78bfa; font-weight: 700;">${t.type}</span></td>
      <td><code style="color: #38bdf8;">${escapeHtml(t.lexeme)}</code></td>
      <td><code style="color: #34d399;">${escapeHtml(String(t.value))}</code></td>
      <td style="color: var(--text-muted); font-family: var(--font-mono);">${t.line}:${t.column}</td>
    `;
    tbody.appendChild(tr);
  });
}

// Load Full Catalog
async function loadCatalog() {
  try {
    const res = await fetch("/api/catalog");
    const data = await res.json();
    const tbody = document.getElementById("catalogFullBody");
    tbody.innerHTML = "";

    data.products.forEach(p => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${p.id}</td>
        <td><strong>${escapeHtml(p.name)}</strong></td>
        <td><span class="card-category">${escapeHtml(p.category)}</span></td>
        <td style="color: var(--emerald); font-weight: 700; font-family: var(--font-mono);">$${parseFloat(p.price).toFixed(2)}</td>
        <td><span class="stock-tag ${p.stock === 0 ? 'stock-out' : p.stock <= 5 ? 'stock-low' : 'stock-in'}">${p.stock}</span></td>
        <td style="color: var(--amber); font-weight: 700;">★ ${parseFloat(p.rating).toFixed(1)}</td>
        <td>
          <button class="chip-btn" style="padding: 3px 8px; font-size: 11px;" onclick="buyProduct('${escapeHtml(p.name)}')">Buy 1</button>
        </td>
      `;
      tbody.appendChild(tr);
    });
  } catch (err) {
    console.error("Failed to load catalog:", err);
  }
}

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
