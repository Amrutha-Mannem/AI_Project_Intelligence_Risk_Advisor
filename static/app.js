// AI Project Intelligence & Risk Advisor — Clean UI JS

// ═══════════════════════════════════════════════════
//  STATE
// ═══════════════════════════════════════════════════
let currentAnalysis = null;

// ═══════════════════════════════════════════════════
//  INIT
// ═══════════════════════════════════════════════════
document.addEventListener("DOMContentLoaded", () => {
  initNav();
  initUpload();
  initButtons();
  loadStatus();
  loadDocuments();
  loadLatestAnalysis();
});

// ═══════════════════════════════════════════════════
//  NAVIGATION
// ═══════════════════════════════════════════════════
function initNav() {
  document.querySelectorAll(".nav-item").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".nav-item").forEach(b => b.classList.remove("active"));
      document.querySelectorAll(".page").forEach(p => p.classList.remove("active"));
      btn.classList.add("active");
      const target = document.getElementById(btn.dataset.page);
      if (target) target.classList.add("active");
    });
  });
}

// ═══════════════════════════════════════════════════
//  TOAST
// ═══════════════════════════════════════════════════
function toast(msg, type = "info") {
  const wrap = document.getElementById("toast-wrap");
  const el = document.createElement("div");
  el.className = `toast ${type}`;
  el.textContent = msg;
  wrap.appendChild(el);
  setTimeout(() => el.remove(), 3500);
}

// ═══════════════════════════════════════════════════
//  STATUS
// ═══════════════════════════════════════════════════
async function loadStatus() {
  try {
    const r = await fetch("/api/export/status");
    const d = await r.json();
    const label = document.getElementById("hdr-llm-label");
    if (label) {
      label.textContent = d.active_provider || "Local Engine";
      label.style.color = (d.gemini_configured || d.openai_configured)
        ? "var(--success)" : "var(--text-muted)";
    }
    renderSysStatus(d);
  } catch {}
}

function renderSysStatus(d) {
  const el = document.getElementById("sys-status-panel");
  if (!el) return;
  el.innerHTML = `
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px">
      <div class="card card-sm">
        <div class="stat-label">Active LLM</div>
        <div style="font-weight:600;margin-top:4px">${d.active_provider || "—"}</div>
      </div>
      <div class="card card-sm">
        <div class="stat-label">Gemini Configured</div>
        <div style="margin-top:4px">${d.gemini_configured
          ? '<span class="badge badge-green">✓ Yes</span>'
          : '<span class="badge badge-gray">✗ No</span>'}</div>
      </div>
    </div>`;
}

// ═══════════════════════════════════════════════════
//  DOCUMENT MANAGEMENT
// ═══════════════════════════════════════════════════
async function loadDocuments() {
  try {
    const r = await fetch("/api/ingest/documents");
    const docs = await r.json();
    const listEl = document.getElementById("doc-list");
    const sbChunks = document.getElementById("sb-chunks");
    const sbDocs   = document.getElementById("sb-docs");

    const totalChunks = docs.reduce((s, d) => s + (d.chunks_count || 0), 0);
    if (sbChunks) sbChunks.textContent = totalChunks;
    if (sbDocs)   sbDocs.textContent   = `${docs.length} document${docs.length !== 1 ? "s" : ""} indexed`;

    if (!docs.length) {
      listEl.innerHTML = `<div class="empty-state"><div class="empty-icon">📄</div><p>No documents indexed yet</p></div>`;
      return;
    }
    listEl.innerHTML = docs.map(d => `
      <div style="display:flex;align-items:center;justify-content:space-between;padding:8px 0;border-bottom:1px solid var(--border)">
        <div>
          <div style="font-size:13px;font-weight:500">${d.file_name}</div>
          <div style="font-size:11px;color:var(--text-muted)">${d.chunks_count} chunks · ${(d.total_chars/1000).toFixed(1)}k chars</div>
        </div>
        <div style="display:flex;align-items:center;gap:8px">
          <span class="badge badge-blue">${d.file_type.toUpperCase()}</span>
          <button class="btn btn-danger btn-sm" onclick="deleteDoc('${d.document_id}')">✕</button>
        </div>
      </div>`).join("");
  } catch (e) {
    console.error("loadDocuments", e);
  }
}

async function deleteDoc(id) {
  if (!confirm("Remove this document from the knowledge base?")) return;
  const r = await fetch(`/api/ingest/documents/${id}`, { method: "DELETE" });
  if (r.ok) { toast("Document removed", "info"); loadDocuments(); }
  else toast("Failed to remove document", "error");
}

// ═══════════════════════════════════════════════════
//  UPLOAD
// ═══════════════════════════════════════════════════
function initUpload() {
  const zone  = document.getElementById("upload-zone");
  const input = document.getElementById("file-input");
  if (!zone) return;

  zone.addEventListener("click", () => input.click());
  zone.addEventListener("dragover", e => { e.preventDefault(); zone.classList.add("drag-over"); });
  zone.addEventListener("dragleave", () => zone.classList.remove("drag-over"));
  zone.addEventListener("drop", e => {
    e.preventDefault(); zone.classList.remove("drag-over");
    if (e.dataTransfer.files.length) uploadFiles(e.dataTransfer.files);
  });
  input.addEventListener("change", () => { if (input.files.length) uploadFiles(input.files); });
}

async function uploadFiles(files) {
  const resultsEl = document.getElementById("upload-results");
  resultsEl.innerHTML = `<div style="text-align:center;padding:20px"><div class="spinner"></div><p style="margin-top:8px;color:var(--text-muted)">Uploading &amp; indexing...</p></div>`;

  const form = new FormData();
  Array.from(files).forEach(f => form.append("files", f));

  try {
    const r = await fetch("/api/ingest/upload", { method: "POST", body: form });
    if (!r.ok) throw new Error(await r.text());
    const results = await r.json();

    resultsEl.innerHTML = results.map(res => `
      <div class="card card-sm" style="margin-bottom:8px;display:flex;align-items:center;justify-content:space-between">
        <div>
          <div style="font-weight:600;font-size:13px">${res.file_name}</div>
          <div style="font-size:11px;color:var(--text-muted)">${res.message}</div>
        </div>
        <span class="badge ${res.status === 'success' ? 'badge-green' : 'badge-red'}">${res.status}</span>
      </div>`).join("");

    const ok = results.filter(r => r.status === "success").length;
    toast(`${ok} file(s) indexed successfully`, "success");
    loadDocuments();
  } catch (e) {
    resultsEl.innerHTML = `<div class="badge badge-red">Upload failed: ${e.message}</div>`;
    toast("Upload failed", "error");
  }
}

// ═══════════════════════════════════════════════════
//  LOAD SAMPLE ARTIFACTS
// ═══════════════════════════════════════════════════
async function loadSamples() {
  toast("Loading sample artifacts...", "info");
  try {
    const r = await fetch("/api/ingest/load-samples", { method: "POST" });
    if (!r.ok) throw new Error(await r.text());
    const results = await r.json();
    toast(`${results.length} sample file(s) loaded`, "success");
    loadDocuments();
  } catch (e) {
    toast("Could not load samples: " + e.message, "error");
  }
}

// ═══════════════════════════════════════════════════
//  MULTI-AGENT PIPELINE
// ═══════════════════════════════════════════════════
async function runPipeline() {
  const btn = document.getElementById("btn-run-pipeline");
  const btn2 = document.getElementById("btn-agents-run");
  [btn, btn2].forEach(b => { if (b) { b.disabled = true; b.innerHTML = `<span class="spinner"></span> Running...`; } });

  toast("Running multi-agent pipeline...", "info");
  try {
    const r = await fetch("/api/agents/run", { method: "POST" });
    if (!r.ok) {
      const err = await r.json();
      throw new Error(err.detail || "Pipeline failed");
    }
    const data = await r.json();
    currentAnalysis = data;
    renderAnalysis(data);
    toast("Analysis complete!", "success");
  } catch (e) {
    toast("Analysis failed: " + e.message, "error");
  } finally {
    [btn, btn2].forEach(b => { if (b) { b.disabled = false; b.innerHTML = b.id === "btn-run-pipeline" ? "▶ Run Analysis" : "▶ Run Full Pipeline"; } });
  }
}

async function loadLatestAnalysis() {
  try {
    const r = await fetch("/api/agents/latest");
    if (!r.ok) return;
    const data = await r.json();
    if (data && data.health_report) { currentAnalysis = data; renderAnalysis(data); }
  } catch {}
}

// ═══════════════════════════════════════════════════
//  RENDER ANALYSIS
// ═══════════════════════════════════════════════════
function renderAnalysis(data) {
  if (!data) return;
  renderKPIs(data);
  renderHealthDimensions(data.health_report);
  renderForecast(data.delivery_forecast);
  renderExecSummary(data.health_report);
  renderScope(data.scope_report);
  renderRisks(data.risks);
  renderBlockers(data.blockers);
  renderActions(data.action_items);
  renderStories(data.documentation?.user_stories);
}

function renderKPIs(data) {
  const h = data.health_report || {};
  const risks = data.risks || [];
  const blockers = data.blockers || [];
  const actions = data.action_items || [];

  setText("kpi-health", h.overall_score !== undefined ? h.overall_score + "/100" : "—");
  setText("kpi-grade", h.health_grade || "");
  setText("kpi-risks", risks.length);
  setText("kpi-high-risks", `${risks.filter(r => r.severity_score >= 15).length} high severity`);
  setText("kpi-blockers", blockers.length);
  setText("kpi-crit-blockers", `${blockers.filter(b => b.severity === "critical").length} critical`);
  setText("kpi-actions", actions.length);

  const kpiH = document.getElementById("kpi-health");
  if (kpiH && h.overall_score !== undefined) {
    kpiH.style.color = h.overall_score >= 85 ? "var(--success)"
      : h.overall_score >= 70 ? "var(--accent2)"
      : h.overall_score >= 50 ? "var(--warning)"
      : "var(--danger)";
  }
}

function renderHealthDimensions(h) {
  const el = document.getElementById("dim-bars");
  if (!el || !h || !h.categories) return;

  el.innerHTML = h.categories.map(cat => {
    const pct = cat.score || 0;
    const color = pct >= 80 ? "var(--success)" : pct >= 60 ? "var(--warning)" : "var(--danger)";
    return `
      <div class="dim-row">
        <div class="dim-label">${cat.category_name}</div>
        <div class="dim-bar"><div class="dim-fill" style="width:${pct}%;background:${color}"></div></div>
        <div class="dim-score" style="color:${color}">${pct}</div>
      </div>`;
  }).join("");
}

function renderForecast(f) {
  const el = document.getElementById("forecast-panel");
  if (!el || !f) return;
  const statusColor = f.forecast_status === "On Track" ? "var(--success)"
    : f.forecast_status === "At Risk" ? "var(--warning)" : "var(--danger)";
  el.innerHTML = `
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:14px">
      <span style="font-size:28px;font-weight:700;color:${statusColor}">${f.forecast_status || "—"}</span>
    </div>
    <div style="font-size:13px;color:var(--text-muted);margin-bottom:10px">
      Estimated delay: <strong style="color:var(--text)">${f.predicted_delay_days || 0} day(s)</strong>
    </div>
    ${(f.critical_path_factors || []).length ? `
      <div style="font-size:12px;color:var(--text-muted);margin-bottom:6px;font-weight:600">CRITICAL PATH FACTORS</div>
      ${(f.critical_path_factors || []).slice(0,4).map(cp =>
        `<div style="font-size:12px;padding:4px 0;border-bottom:1px solid var(--border)">• ${cp}</div>`
      ).join("")}` : ""}`;
}

function renderExecSummary(h) {
  const el = document.getElementById("exec-summary");
  if (!el || !h) return;
  el.style.color = "var(--text)";
  el.innerHTML = `
    <p style="margin-bottom:12px">${h.executive_summary || ""}</p>
    ${(h.top_positives || []).length ? `
      <div style="margin-bottom:8px">
        <div style="font-size:11px;font-weight:600;color:var(--success);margin-bottom:4px">✓ STRENGTHS</div>
        ${h.top_positives.map(p => `<div style="font-size:12px;color:var(--text-muted);padding:2px 0">• ${p}</div>`).join("")}
      </div>` : ""}
    ${(h.top_vulnerabilities || []).length ? `
      <div>
        <div style="font-size:11px;font-weight:600;color:var(--danger);margin-bottom:4px">⚠ VULNERABILITIES</div>
        ${h.top_vulnerabilities.map(v => `<div style="font-size:12px;color:var(--text-muted);padding:2px 0">• ${v}</div>`).join("")}
      </div>` : ""}`;
}

function renderScope(s) {
  const el = document.getElementById("scope-panel");
  if (!el || !s) return;
  const items = (s.in_scope_items || []).slice(0, 6);
  if (!items.length) { el.innerHTML = "<p style='color:var(--text-muted);font-size:13px'>No scope items extracted</p>"; return; }
  el.innerHTML = `
    <div style="font-size:12px;font-weight:600;color:var(--success);margin-bottom:8px">IN SCOPE (${items.length})</div>
    ${items.map(i => `
      <div style="padding:7px 0;border-bottom:1px solid var(--border)">
        <div style="font-size:13px;font-weight:500">${i.title}</div>
        <div style="font-size:11px;color:var(--text-muted);margin-top:2px">${i.description || ""}</div>
      </div>`).join("")}`;
}

function renderRisks(risks) {
  const el = document.getElementById("risks-panel");
  if (!el) return;
  if (!risks || !risks.length) {
    el.innerHTML = `<div class="empty-state"><div class="empty-icon">✅</div><p>No risks identified</p></div>`;
    return;
  }
  el.innerHTML = `
    <table class="tbl">
      <thead><tr>
        <th>ID</th><th>Risk</th><th>Category</th><th>Severity</th><th>Mitigation</th>
      </tr></thead>
      <tbody>
        ${risks.map(r => {
          const sev = r.severity_score >= 15 ? "high" : r.severity_score >= 8 ? "medium" : "low";
          const badge = sev === "high" ? "badge-red" : sev === "medium" ? "badge-yellow" : "badge-green";
          return `<tr>
            <td style="color:var(--text-muted);font-size:11px">${r.id || "—"}</td>
            <td><strong>${r.risk_title}</strong><div style="font-size:11px;color:var(--text-muted);margin-top:2px">${r.description || ""}</div></td>
            <td><span class="badge badge-blue">${r.category || "—"}</span></td>
            <td><span class="badge ${badge}">${sev.toUpperCase()} (${r.severity_score})</span></td>
            <td style="font-size:12px;color:var(--text-muted)">${r.mitigation_strategy || "—"}</td>
          </tr>`;
        }).join("")}
      </tbody>
    </table>`;
}

function renderBlockers(blockers) {
  const el = document.getElementById("blockers-panel");
  if (!el) return;
  if (!blockers || !blockers.length) {
    el.innerHTML = `<div class="empty-state"><div class="empty-icon">✅</div><p>No blockers detected</p></div>`;
    return;
  }
  el.innerHTML = `
    <table class="tbl">
      <thead><tr><th>ID</th><th>Blocker</th><th>Severity</th><th>Owner</th><th>Resolution</th></tr></thead>
      <tbody>
        ${blockers.map(b => {
          const badge = b.severity === "critical" ? "badge-red" : b.severity === "high" ? "badge-yellow" : "badge-blue";
          return `<tr>
            <td style="color:var(--text-muted);font-size:11px">${b.id || "—"}</td>
            <td><strong>${b.title}</strong><div style="font-size:11px;color:var(--text-muted);margin-top:2px">${b.description || ""}</div></td>
            <td><span class="badge ${badge}">${(b.severity || "").toUpperCase()}</span></td>
            <td style="font-size:12px">${b.assigned_owner || "Unassigned"}</td>
            <td style="font-size:12px;color:var(--text-muted)">${b.suggested_resolution || "—"}</td>
          </tr>`;
        }).join("")}
      </tbody>
    </table>`;
}

function renderActions(actions) {
  const el = document.getElementById("actions-panel");
  if (!el) return;
  if (!actions || !actions.length) {
    el.innerHTML = `<p style="color:var(--text-muted);font-size:13px">No action items extracted</p>`;
    return;
  }
  el.innerHTML = actions.slice(0, 8).map(a => `
    <div style="padding:7px 0;border-bottom:1px solid var(--border);display:flex;justify-content:space-between;align-items:start">
      <div>
        <div style="font-size:13px;font-weight:500">${a.task_description}</div>
        <div style="font-size:11px;color:var(--text-muted);margin-top:2px">
          👤 ${a.assignee || "Unassigned"} ${a.due_date ? `· 📅 ${a.due_date}` : ""}
        </div>
      </div>
      <span class="badge ${a.priority === 'high' ? 'badge-red' : a.priority === 'medium' ? 'badge-yellow' : 'badge-blue'}">${a.priority || "—"}</span>
    </div>`).join("");
}

function renderStories(stories) {
  const el = document.getElementById("stories-panel");
  if (!el) return;
  if (!stories || !stories.length) {
    el.innerHTML = `<div class="empty-state"><p>No user stories generated yet</p></div>`;
    return;
  }
  el.innerHTML = stories.slice(0, 6).map(s => `
    <div class="card card-sm" style="margin-bottom:10px">
      <div style="display:flex;justify-content:space-between;margin-bottom:6px">
        <strong style="font-size:13px">${s.id}: ${s.title}</strong>
        <span class="badge badge-blue">${s.estimated_story_points || "?"} pts</span>
      </div>
      <div style="font-size:12px;color:var(--text-muted)">
        As a <em>${s.as_a}</em>, I want to <em>${s.i_want_to}</em> so that <em>${s.so_that}</em>
      </div>
    </div>`).join("");
}

// ═══════════════════════════════════════════════════
//  RAG SEARCH
// ═══════════════════════════════════════════════════
async function ragSearch() {
  const q = document.getElementById("rag-query-input")?.value?.trim();
  const topK = document.getElementById("rag-topk")?.value || 5;
  const el = document.getElementById("rag-results");
  if (!q) { toast("Enter a search query", "info"); return; }

  el.innerHTML = `<div style="text-align:center;padding:20px"><div class="spinner"></div></div>`;
  try {
    const r = await fetch("/api/rag/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: q, top_k: parseInt(topK) }),
    });
    const data = await r.json();
    const results = data.results || [];
    if (!results.length) {
      el.innerHTML = `<div class="empty-state"><p>No relevant chunks found. Try a different query.</p></div>`;
      return;
    }
    el.innerHTML = results.map((item, i) => `
      <div class="card card-sm" style="margin-bottom:10px">
        <div style="display:flex;justify-content:space-between;margin-bottom:6px">
          <span style="font-size:12px;font-weight:600;color:var(--text-muted)">
            📄 ${item.source_name || "Document"} · Chunk #${item.chunk_index ?? i}
          </span>
          <span class="badge badge-blue">Score: ${(item.score || 0).toFixed(3)}</span>
        </div>
        <div style="font-size:13px;line-height:1.6">${item.excerpt || item.content || ""}</div>
      </div>`).join("");
  } catch (e) {
    el.innerHTML = `<div class="badge badge-red">Search failed: ${e.message}</div>`;
    toast("Search failed", "error");
  }
}

// ═══════════════════════════════════════════════════
//  CHAT
// ═══════════════════════════════════════════════════
let chatHistory = [];

function appendBubble(role, html) {
  const msgs = document.getElementById("chat-messages");
  const div = document.createElement("div");
  div.className = `chat-bubble ${role}`;
  div.innerHTML = html;
  msgs.appendChild(div);
  msgs.scrollTop = msgs.scrollHeight;
  return div;
}

async function sendChat() {
  const input = document.getElementById("chat-input");
  const q = input?.value?.trim();
  if (!q) return;
  input.value = "";

  appendBubble("user", escHtml(q));

  const typingEl = document.getElementById("chat-typing");
  if (typingEl) typingEl.style.display = "flex";

  chatHistory.push({ role: "user", content: q });

  try {
    const r = await fetch("/api/chat/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: q, top_k: 5, conversation_history: chatHistory }),
    });
    if (!r.ok) {
      const err = await r.json();
      throw new Error(err.detail || "Chat error");
    }
    const data = await r.json();

    if (typingEl) typingEl.style.display = "none";

    // Format answer
    let html = `<div>${escHtml(data.answer || "No response")}</div>`;

    // Citations
    if (data.citations && data.citations.length) {
      html += `<div class="citation">📎 Sources: ${data.citations.map(c =>
        `<strong>${c.document_name}</strong>`
      ).join(", ")}</div>`;
    }

    // Confidence
    if (data.confidence_score !== undefined) {
      html += `<div class="citation" style="margin-top:4px">Confidence: ${(data.confidence_score * 100).toFixed(0)}%</div>`;
    }

    const botBubble = appendBubble("bot", html);
    chatHistory.push({ role: "assistant", content: data.answer || "" });

    // Suggested follow-ups
    if (data.suggested_followups && data.suggested_followups.length) {
      const followDiv = document.createElement("div");
      followDiv.style.cssText = "margin-top:6px;display:flex;flex-wrap:wrap;gap:4px";
      data.suggested_followups.forEach(fu => {
        const chip = document.createElement("span");
        chip.className = "followup-chip";
        chip.textContent = fu;
        chip.onclick = () => {
          document.getElementById("chat-input").value = fu;
          sendChat();
        };
        followDiv.appendChild(chip);
      });
      document.getElementById("chat-messages").appendChild(followDiv);
      document.getElementById("chat-messages").scrollTop = 99999;
    }
  } catch (e) {
    if (typingEl) typingEl.style.display = "none";
    appendBubble("bot", `<span style="color:var(--danger)">Error: ${escHtml(e.message)}</span>`);
    toast("Chat error: " + e.message, "error");
  }
}

// ═══════════════════════════════════════════════════
//  EXPORT
// ═══════════════════════════════════════════════════
async function exportMarkdown() {
  try {
    const r = await fetch("/api/export/markdown");
    if (!r.ok) { toast("Run analysis first!", "error"); return; }
    const blob = await r.blob();
    downloadBlob(blob, "project_intelligence_report.md");
    toast("Markdown report downloaded", "success");
  } catch (e) { toast("Export failed: " + e.message, "error"); }
}

async function exportJSON() {
  try {
    const r = await fetch("/api/export/json");
    if (!r.ok) { toast("Run analysis first!", "error"); return; }
    const blob = await r.blob();
    downloadBlob(blob, "project_intelligence_report.json");
    toast("JSON report downloaded", "success");
  } catch (e) { toast("Export failed: " + e.message, "error"); }
}

function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url; a.download = filename; a.click();
  URL.revokeObjectURL(url);
}

// ═══════════════════════════════════════════════════
//  SETTINGS — API KEYS
// ═══════════════════════════════════════════════════
function openSettings() {
  document.getElementById("settings-modal").classList.add("open");
}
function closeSettings() {
  document.getElementById("settings-modal").classList.remove("open");
}

async function saveKeys() {
  const gk = document.getElementById("input-gemini-key")?.value?.trim();
  const ok = document.getElementById("input-openai-key")?.value?.trim();
  const statusEl = document.getElementById("key-status");

  if (!gk && !ok) { statusEl.textContent = "Enter at least one API key."; statusEl.style.color = "var(--danger)"; return; }

  try {
    const r = await fetch("/api/export/settings/keys", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ gemini_api_key: gk || null, openai_api_key: ok || null }),
    });
    const d = await r.json();
    if (d.status === "success") {
      statusEl.textContent = `✓ Active provider: ${d.active_provider}`;
      statusEl.style.color = "var(--success)";
      document.getElementById("hdr-llm-label").textContent = d.active_provider;
      document.getElementById("hdr-llm-label").style.color = "var(--success)";
      toast("API key saved! Provider: " + d.active_provider, "success");
      setTimeout(closeSettings, 1200);
    }
  } catch (e) {
    statusEl.textContent = "Failed: " + e.message;
    statusEl.style.color = "var(--danger)";
  }
}

// ═══════════════════════════════════════════════════
//  INIT EVENT LISTENERS
// ═══════════════════════════════════════════════════
function initButtons() {
  // Header
  safeOn("btn-load-samples",    "click", loadSamples);
  safeOn("btn-run-pipeline",    "click", runPipeline);
  safeOn("btn-open-settings",   "click", openSettings);

  // Settings modal
  safeOn("btn-close-settings",  "click", closeSettings);
  safeOn("btn-close-settings2", "click", closeSettings);
  safeOn("btn-save-keys",       "click", saveKeys);

  // Agents page
  safeOn("btn-agents-run",      "click", runPipeline);

  // RAG
  safeOn("btn-rag-search",      "click", ragSearch);
  const ragInput = document.getElementById("rag-query-input");
  if (ragInput) ragInput.addEventListener("keydown", e => { if (e.key === "Enter") ragSearch(); });

  // Chat
  safeOn("btn-send-chat",       "click", sendChat);
  safeOn("btn-clear-chat",      "click", () => {
    chatHistory = [];
    const msgs = document.getElementById("chat-messages");
    msgs.innerHTML = `<div class="chat-bubble bot">Chat cleared. Upload documents and ask me anything!</div>`;
  });
  const chatIn = document.getElementById("chat-input");
  if (chatIn) chatIn.addEventListener("keydown", e => { if (e.key === "Enter") sendChat(); });

  // Export
  safeOn("btn-export-md",   "click", exportMarkdown);
  safeOn("btn-export-json", "click", exportJSON);

  // Close modal on overlay click
  const modal = document.getElementById("settings-modal");
  if (modal) modal.addEventListener("click", e => { if (e.target === modal) closeSettings(); });
}

// ═══════════════════════════════════════════════════
//  HELPERS
// ═══════════════════════════════════════════════════
function safeOn(id, event, fn) {
  const el = document.getElementById(id);
  if (el) el.addEventListener(event, fn);
}
function setText(id, val) {
  const el = document.getElementById(id);
  if (el) el.textContent = val;
}
function escHtml(str) {
  return String(str)
    .replace(/&/g, "&amp;").replace(/</g, "&lt;")
    .replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}
