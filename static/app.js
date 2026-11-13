// ShopQL Studio Frontend Logic

let currentAstData = null;
let currentAstMode = "visual"; // "visual" or "json"

document.addEventListener("DOMContentLoaded", () => {
  initPresets();
  initTabs();
  initEvents();
  loadCatalog();
});

// Initialize Sample Preset Queries
async function initPresets() {
  try {
    const res = await fetch("/api/samples");
    const samples = await res.json();
    const container = document.getElementById("presetButtons");
    container.innerHTML = "";

    samples.forEach((sample, idx) => {
      const chip = document.createElement("button");
      chip.className = "preset-chip";
      chip.textContent = sample.title;
      chip.title = sample.desc;
      chip.addEventListener("click", () => {
        document.getElementById("queryInput").value = sample.query;
        runQuery();
      });
      container.appendChild(chip);

      // Preload example 1 on page start
      if (idx === 0 && !document.getElementById("queryInput").value.trim()) {
        document.getElementById("queryInput").value = sample.query;
      }
    });
  } catch (err) {
    console.error("Failed to load sample queries:", err);
  }
}

// Tab Switching
function initTabs() {
  const tabButtons = document.querySelectorAll(".tab-btn");
  tabButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      tabButtons.forEach(b => b.classList.remove("active"));
      document.querySelectorAll(".tab-content").forEach(c => c.classList.remove("active"));

      btn.classList.add("active");
      const targetId = btn.getAttribute("data-tab");
      const targetTab = document.getElementById(targetId);
      if (targetTab) {
        targetTab.classList.add("active");
      }

      if (targetId === "tab-catalog") {
        loadCatalog();
      }
    });
  });

  // AST view mode toggle
  document.getElementById("btnAstVisual").addEventListener("click", () => {
    currentAstMode = "visual";
    document.getElementById("btnAstVisual").classList.add("active");
    document.getElementById("btnAstJson").classList.remove("active");
    renderAst();
  });

  document.getElementById("btnAstJson").addEventListener("click", () => {
    currentAstMode = "json";
    document.getElementById("btnAstJson").classList.add("active");
    document.getElementById("btnAstVisual").classList.remove("active");
    renderAst();
  });
}

function initEvents() {
  const queryInput = document.getElementById("queryInput");
  const btnRun = document.getElementById("btnRun");
  const btnClear = document.getElementById("btnClear");
  const btnResetCatalog = document.getElementById("btnResetCatalog");
  const closeErrorBtn = document.getElementById("closeErrorBtn");
  const catalogSearch = document.getElementById("catalogSearch");

  btnRun.addEventListener("click", runQuery);

  btnClear.addEventListener("click", () => {
    queryInput.value = "";
    queryInput.focus();
  });

  closeErrorBtn.addEventListener("click", () => {
    document.getElementById("errorPanel").style.display = "none";
  });

  // Ctrl+Enter or Cmd+Enter to run query
  queryInput.addEventListener("keydown", (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
      e.preventDefault();
      runQuery();
    }
  });

  btnResetCatalog.addEventListener("click", async () => {
    if (confirm("Reset catalog back to initial seed data?")) {
      try {
        const res = await fetch("/api/reset", { method: "POST" });
        const data = await res.json();
        alert(data.message);
        loadCatalog();
      } catch (err) {
        alert("Failed to reset store: " + err);
      }
    }
  });

  catalogSearch.addEventListener("input", (e) => {
    const q = e.target.value.toLowerCase();
    const rows = document.querySelectorAll("#catalogTableBody tr");
    rows.forEach(r => {
      const text = r.textContent.toLowerCase();
      r.style.display = text.includes(q) ? "" : "none";
    });
  });
}

// Execute Query
async function runQuery() {
  const query = document.getElementById("queryInput").value.trim();
  const errorPanel = document.getElementById("errorPanel");
  const errorText = document.getElementById("errorText");
  const metricStatus = document.getElementById("metricStatus");
  const metricCompile = document.getElementById("metricCompile");
  const metricExec = document.getElementById("metricExec");
  const metricRows = document.getElementById("metricRows");

  if (!query) return;

  metricStatus.textContent = "Executing...";
  metricStatus.style.color = "var(--warning)";

  try {
    const resp = await fetch("/api/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query })
    });
    const data = await resp.json();

    if (!data.success) {
      errorPanel.style.display = "block";
      errorText.textContent = data.error;
      metricStatus.textContent = "Error";
      metricStatus.style.color = "var(--danger)";
      metricCompile.textContent = `${data.compile_time_ms || 0} ms`;
      metricExec.textContent = "0.0 ms";
      metricRows.textContent = "0";
      return;
    }

    // Success
    errorPanel.style.display = "none";
    metricStatus.textContent = "Success";
    metricStatus.style.color = "var(--success)";
    metricCompile.textContent = `${data.compile_time_ms} ms`;
    metricExec.textContent = `${data.total_time_ms - data.compile_time_ms} ms`;

    let totalRows = 0;
    data.results.forEach(r => totalRows += (r.count || 0));
    metricRows.textContent = totalRows;

    // Save AST and render components
    currentAstData = data.ast;
    renderResults(data.results);
    renderAst();
    renderTokens(data.tokens);

    // If query was a mutating statement (ADD, UPDATE, DELETE, RESTOCK, BUY), refresh catalog
    const hasMutation = data.results.some(r => ["ADD", "UPDATE", "DELETE", "RESTOCK", "PURCHASE"].includes(r.statement_type));
    if (hasMutation) {
      loadCatalog();
    }

  } catch (err) {
    errorPanel.style.display = "block";
    errorText.textContent = "Network or Server Error: " + err.message;
    metricStatus.textContent = "Server Error";
    metricStatus.style.color = "var(--danger)";
  }
}

// Render Results View
function renderResults(results) {
  const container = document.getElementById("resultsContainer");
  container.innerHTML = "";

  if (!results || results.length === 0) {
    container.innerHTML = `<div class="placeholder-msg">No results returned.</div>`;
    return;
  }

  results.forEach(res => {
    const block = document.createElement("div");
    block.style.marginBottom = "24px";

    const title = document.createElement("div");
    title.style.display = "flex";
    title.style.justifyContent = "space-between";
    title.style.alignItems = "center";
    title.style.marginBottom = "8px";
    title.innerHTML = `
      <strong style="color: #38bdf8; font-size: 14px;">${res.statement_type} — ${res.message}</strong>
      <span style="font-size: 12px; color: var(--text-muted); font-family: var(--font-mono);">${res.execution_time_ms} ms</span>
    `;
    block.appendChild(title);

    if (res.rows && res.rows.length > 0) {
      const scrollDiv = document.createElement("div");
      scrollDiv.className = "table-scroll-container";
      const table = document.createElement("table");
      table.className = "data-table";

      // Thead
      const thead = document.createElement("thead");
      const trHead = document.createElement("tr");
      res.columns.forEach(col => {
        const th = document.createElement("th");
        th.textContent = col.toUpperCase();
        trHead.appendChild(th);
      });
      thead.appendChild(trHead);
      table.appendChild(thead);

      // Tbody
      const tbody = document.createElement("tbody");
      res.rows.forEach(r => {
        const tr = document.createElement("tr");
        res.columns.forEach(col => {
          const td = document.createElement("td");
          const val = r[col];

          if (col === "price" && val !== undefined) {
            td.innerHTML = `<span class="price-tag">$${parseFloat(val).toFixed(2)}</span>`;
          } else if (col === "rating" && val !== undefined) {
            td.innerHTML = `<span class="rating-tag">${parseFloat(val).toFixed(1)} ★</span>`;
          } else if (col === "category" && val !== undefined) {
            td.innerHTML = `<span class="badge badge-cat">${val}</span>`;
          } else if (col === "stock" && val !== undefined) {
            const stockNum = parseInt(val);
            if (stockNum === 0) {
              td.innerHTML = `<span class="badge badge-nostock">Out of Stock</span>`;
            } else if (stockNum <= 5) {
              td.innerHTML = `<span class="badge badge-lowstock">${stockNum} (Low)</span>`;
            } else {
              td.innerHTML = `<span class="badge badge-instock">${stockNum} in stock</span>`;
            }
          } else {
            td.textContent = val !== undefined ? val : "";
          }
          tr.appendChild(td);
        });
        tbody.appendChild(tr);
      });
      table.appendChild(tbody);
      scrollDiv.appendChild(table);
      block.appendChild(scrollDiv);
    }

    container.appendChild(block);
  });
}

// Render AST Visualizer
function renderAst() {
  const container = document.getElementById("astContainer");
  if (!currentAstData) {
    container.innerHTML = `<div class="placeholder-msg">Run a query to inspect the generated AST structure.</div>`;
    return;
  }

  if (currentAstMode === "json") {
    container.innerHTML = `<pre style="color: #93c5fd; overflow: auto;">${JSON.stringify(currentAstData, null, 2)}</pre>`;
    return;
  }

  // Visual Tree Mode
  container.innerHTML = "";
  currentAstData.forEach(stmt => {
    container.appendChild(createAstTreeNode(stmt));
  });
}

function createAstTreeNode(node) {
  const el = document.createElement("div");
  el.className = "ast-node";

  const pill = document.createElement("div");
  pill.className = "ast-pill";

  const typeSpan = document.createElement("span");
  typeSpan.className = "ast-pill-type";
  typeSpan.textContent = node._type || "Node";
  pill.appendChild(typeSpan);

  // Collect simple attributes
  const simpleAttrs = [];
  for (const [k, v] of Object.entries(node)) {
    if (k !== "_type" && k !== "line" && k !== "column" && typeof v !== "object") {
      simpleAttrs.push(`${k}: ${JSON.stringify(v)}`);
    }
  }

  if (simpleAttrs.length > 0) {
    const propsSpan = document.createElement("span");
    propsSpan.className = "ast-pill-props";
    propsSpan.textContent = `(${simpleAttrs.join(", ")})`;
    pill.appendChild(propsSpan);
  }

  el.appendChild(pill);

  // Recurse child nodes
  for (const [k, v] of Object.entries(node)) {
    if (k === "_type" || k === "line" || k === "column") continue;
    if (v && typeof v === "object") {
      if (Array.isArray(v)) {
        if (v.length > 0 && typeof v[0] === "object") {
          const listLabel = document.createElement("div");
          listLabel.style.fontSize = "11px";
          listLabel.style.color = "var(--text-muted)";
          listLabel.style.marginLeft = "12px";
          listLabel.textContent = `▼ ${k} [${v.length}]:`;
          el.appendChild(listLabel);
          v.forEach(child => el.appendChild(createAstTreeNode(child)));
        }
      } else {
        const fieldLabel = document.createElement("div");
        fieldLabel.style.fontSize = "11px";
        fieldLabel.style.color = "var(--text-muted)";
        fieldLabel.style.marginLeft = "12px";
        fieldLabel.textContent = `▼ ${k}:`;
        el.appendChild(fieldLabel);
        el.appendChild(createAstTreeNode(v));
      }
    }
  }

  return el;
}

// Render Scanned Token Stream
function renderTokens(tokens) {
  const tbody = document.getElementById("tokensTableBody");
  const badge = document.getElementById("tokenCountBadge");
  tbody.innerHTML = "";

  if (!tokens || tokens.length === 0) {
    tbody.innerHTML = `<tr><td colspan="5" class="text-center">No tokens generated.</td></tr>`;
    badge.textContent = "0 tokens";
    return;
  }

  badge.textContent = `${tokens.length} tokens`;

  tokens.forEach((t, i) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${i + 1}</td>
      <td><span class="badge" style="background-color: #312e81; color: #c7d2fe;">${t.type}</span></td>
      <td><code style="color: #38bdf8;">${escapeHtml(t.lexeme)}</code></td>
      <td><code style="color: #34d399;">${escapeHtml(String(t.value))}</code></td>
      <td style="color: var(--text-muted); font-family: var(--font-mono);">${t.line}:${t.column}</td>
    `;
    tbody.appendChild(tr);
  });
}

// Load Store Catalog
async function loadCatalog() {
  try {
    const res = await fetch("/api/catalog");
    const data = await res.json();
    const tbody = document.getElementById("catalogTableBody");
    tbody.innerHTML = "";

    data.products.forEach(p => {
      const tr = document.createElement("tr");
      const stockBadge = p.stock === 0 
        ? `<span class="badge badge-nostock">Out of Stock</span>`
        : p.stock <= 5 
        ? `<span class="badge badge-lowstock">${p.stock} (Low)</span>`
        : `<span class="badge badge-instock">${p.stock} in stock</span>`;

      tr.innerHTML = `
        <td>${p.id}</td>
        <td><strong>${escapeHtml(p.name)}</strong></td>
        <td><span class="badge badge-cat">${escapeHtml(p.category)}</span></td>
        <td><span class="price-tag">$${parseFloat(p.price).toFixed(2)}</span></td>
        <td>${stockBadge}</td>
        <td><span class="rating-tag">${parseFloat(p.rating).toFixed(1)} ★</span></td>
        <td style="color: var(--text-muted); font-size: 12px;">${escapeHtml(p.description || "")}</td>
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

