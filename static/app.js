// AI Project Intelligence & Risk Advisor — Enterprise Corporate Frontend
// Infosys Professional Theme | Strict Document Grounding | No Emojis

// ═══════════════════════════════════════════════════
//  GLOBAL STATE
// ═══════════════════════════════════════════════════
let currentAnalysis = null;
let chatHistory = [];

// ═══════════════════════════════════════════════════
//  APPLICATION INITIALIZATION
// ═══════════════════════════════════════════════════
document.addEventListener("DOMContentLoaded", () => {
  initNav();
  initUpload();
  initButtons();
  loadStatus();
  loadDocuments();
  loadAnalysisHistory();
  // Clean dynamic start: only load cached analysis if explicitly requested or present
  checkExistingAnalysis();
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

function navigateTo(pageId) {
  const btn = document.querySelector(`.nav-item[data-page="${pageId}"]`);
  if (btn) btn.click();
}

// ═══════════════════════════════════════════════════
//  TOAST NOTIFICATIONS
// ═══════════════════════════════════════════════════
function toast(msg, type = "info") {
  const wrap = document.getElementById("toasts");
  if (!wrap) return;
  const el = document.createElement("div");
  el.className = `toast ${type}`;
  el.textContent = msg;
  wrap.appendChild(el);
  setTimeout(() => {
    el.style.opacity = "0";
    el.style.transition = "opacity 0.3s";
    setTimeout(() => el.remove(), 300);
  }, 3500);
}

// ═══════════════════════════════════════════════════
//  SYSTEM & PROVIDER STATUS
// ═══════════════════════════════════════════════════
async function loadStatus() {
  try {
    const r = await fetch("/api/export/status");
    if (!r.ok) return;
    const d = await r.json();
    const label = document.getElementById("hdr-llm-label");
    if (label) {
      const provider = d.active_provider || "Local Reasoning Engine";
      label.textContent = `Provider: ${provider}`;
      label.style.color = (d.gemini_configured || d.openai_configured) ? "var(--success)" : "var(--text-muted)";
    }
    renderSysStatus(d);
  } catch (e) {
    console.error("loadStatus error:", e);
  }
}

function renderSysStatus(d) {
  const el = document.getElementById("sys-status-panel");
  if (!el) return;
  el.innerHTML = `
    <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(180px, 1fr));gap:12px">
      <div class="card card-sm">
        <div class="card-label">Active Provider</div>
        <div style="font-weight:600;margin-top:4px;color:var(--text)">${d.active_provider || "Local Fallback"}</div>
      </div>
      <div class="card card-sm">
        <div class="card-label">Gemini API Status</div>
        <div style="margin-top:4px">${d.gemini_configured ? '<span class="badge badge-green">Configured</span>' : '<span class="badge badge-gray">Not Set</span>'}</div>
      </div>
      <div class="card card-sm">
        <div class="card-label">OpenAI Status</div>
        <div style="margin-top:4px">${d.openai_configured ? '<span class="badge badge-green">Configured</span>' : '<span class="badge badge-gray">Not Set</span>'}</div>
      </div>
      <div class="card card-sm">
        <div class="card-label">Vector Storage</div>
        <div style="margin-top:4px"><span class="badge badge-blue">${d.vector_index_type || "Numpy Dense"}</span></div>
      </div>
    </div>`;
}

// ═══════════════════════════════════════════════════
//  DOCUMENT MANAGEMENT (INGESTION & SAMPLES)
// ═══════════════════════════════════════════════════
async function loadDocuments() {
  try {
    const r = await fetch("/api/ingest/documents");
    if (!r.ok) return;
    const docs = await r.json();
    const listEl = document.getElementById("doc-list");
    const sbChunks = document.getElementById("sb-chunks");
    const sbDocs   = document.getElementById("sb-docs");

    const totalChunks = docs.reduce((s, d) => s + (d.chunks_count || 0), 0);
    if (sbChunks) sbChunks.textContent = totalChunks;
    if (sbDocs)   sbDocs.textContent   = `${docs.length} document${docs.length !== 1 ? "s" : ""} indexed`;

    if (!docs.length) {
      if (listEl) listEl.innerHTML = `<div class="empty"><p>No documents indexed yet. Upload project files or load sample data.</p></div>`;
      return;
    }

    if (listEl) {
      listEl.innerHTML = `
        <div class="tbl-wrap">
          <table class="tbl">
            <thead>
              <tr>
                <th>Document Name</th>
                <th>Format</th>
                <th>Chunks</th>
                <th>Size</th>
                <th style="text-align:right">Action</th>
              </tr>
            </thead>
            <tbody>
              ${docs.map(d => `
                <tr>
                  <td>
                    <div style="font-weight:600;color:var(--text)">${escHtml(d.file_name)}</div>
                    <div style="font-size:11px;color:var(--text-dim)">ID: ${escHtml(d.document_id)}</div>
                  </td>
                  <td><span class="badge badge-blue">${escHtml(d.file_type.toUpperCase())}</span></td>
                  <td><span style="font-weight:600">${d.chunks_count}</span> chunks</td>
                  <td style="color:var(--text-muted)">${(d.total_chars / 1000).toFixed(1)} KB</td>
                  <td style="text-align:right">
                    <button class="btn btn-danger btn-sm" onclick="deleteDoc('${d.document_id}')">Remove</button>
                  </td>
                </tr>`).join("")}
            </tbody>
          </table>
        </div>`;
    }
  } catch (e) {
    console.error("loadDocuments error:", e);
  }
}

async function deleteDoc(id) {
  if (!confirm("Remove this document from the vector knowledge base?")) return;
  try {
    const r = await fetch(`/api/ingest/documents/${id}`, { method: "DELETE" });
    if (r.ok) {
      toast("Document removed from knowledge base", "info");
      loadDocuments();
    } else {
      toast("Failed to remove document", "error");
    }
  } catch (e) {
    toast("Deletion error: " + e.message, "error");
  }
}

function initUpload() {
  const zone  = document.getElementById("upload-zone");
  const input = document.getElementById("file-input");
  if (!zone || !input) return;

  zone.addEventListener("click", () => input.click());
  zone.addEventListener("dragover", e => { e.preventDefault(); zone.classList.add("drag-over"); });
  zone.addEventListener("dragleave", () => zone.classList.remove("drag-over"));
  zone.addEventListener("drop", e => {
    e.preventDefault();
    zone.classList.remove("drag-over");
    if (e.dataTransfer.files.length) uploadFiles(e.dataTransfer.files);
  });
  input.addEventListener("change", () => {
    if (input.files.length) uploadFiles(input.files);
  });
}

async function uploadFiles(files) {
  const resultsEl = document.getElementById("upload-results");
  if (resultsEl) {
    resultsEl.innerHTML = `
      <div style="display:flex;align-items:center;gap:8px;padding:12px;background:var(--surface2);border-radius:4px">
        <span class="spin"></span>
        <span style="font-size:12.5px;color:var(--text-muted)">Ingesting and chunking ${files.length} document(s)...</span>
      </div>`;
  }

  const form = new FormData();
  Array.from(files).forEach(f => form.append("files", f));

  try {
    const r = await fetch("/api/ingest/upload", { method: "POST", body: form });
    if (!r.ok) throw new Error(await r.text());
    const results = await r.json();

    if (resultsEl) {
      resultsEl.innerHTML = results.map(res => `
        <div style="display:flex;align-items:center;justify-content:space-between;padding:8px 12px;background:var(--surface2);border-radius:4px;margin-bottom:6px;border:1px solid var(--border)">
          <div>
            <div style="font-weight:600;font-size:12.5px">${escHtml(res.file_name)}</div>
            <div style="font-size:11px;color:var(--text-muted)">${escHtml(res.message)}</div>
          </div>
          <span class="badge ${res.status === 'success' ? 'badge-green' : 'badge-red'}">${res.status.toUpperCase()}</span>
        </div>`).join("");
    }

    const successCount = results.filter(res => res.status === "success").length;
    toast(`${successCount} document(s) uploaded and indexed`, "success");
    loadDocuments();
  } catch (e) {
    if (resultsEl) {
      resultsEl.innerHTML = `<div style="padding:10px;background:rgba(239,68,68,0.1);color:var(--danger);border-radius:4px;font-size:12px">Upload failed: ${escHtml(e.message)}</div>`;
    }
    toast("Upload failed", "error");
  }
}

async function loadSamples() {
  toast("Loading enterprise sample project artifacts...", "info");
  try {
    const r = await fetch("/api/ingest/load-samples", { method: "POST" });
    if (!r.ok) throw new Error(await r.text());
    const results = await r.json();
    toast(`${results.length} sample artifacts indexed successfully`, "success");
    loadDocuments();
  } catch (e) {
    toast("Could not load samples: " + e.message, "error");
  }
}

async function clearAllDocs() {
  if (!confirm("Are you sure you want to clear all indexed documents from the knowledge base?")) return;
  try {
    const r = await fetch("/api/ingest/clear", { method: "POST" });
    if (r.ok) {
      currentAnalysis = null;
      toast("Knowledge base cleared. Starting fresh.", "info");
      loadDocuments();
      resetViewsToEmpty();
    }
  } catch (e) {
    toast("Error clearing knowledge base: " + e.message, "error");
  }
}

function resetViewsToEmpty() {
  // Reset KPI cards
  setText("kpi-health", "—");
  setText("kpi-grade", "Analysis pending");
  setText("kpi-risks", "—");
  setText("kpi-high-risks", "0 high severity");
  setText("kpi-blockers", "—");
  setText("kpi-crit-blockers", "0 critical");
  setText("kpi-actions", "—");

  // Reset panels
  const dimBars = document.getElementById("dim-bars");
  if (dimBars) dimBars.innerHTML = `<div class="empty"><p>No health metrics computed. Upload documents and run analysis.</p></div>`;

  const forecast = document.getElementById("forecast-panel");
  if (forecast) forecast.innerHTML = `<div class="empty"><p>No delivery forecast available. Run analysis to compute milestone predictions.</p></div>`;

  const rfForecast = document.getElementById("risk-forecast-panel");
  if (rfForecast) rfForecast.innerHTML = `<div class="empty"><p>Upload project documents and run analysis to view delivery forecast.</p></div>`;

  const exec = document.getElementById("exec-summary");
  if (exec) exec.innerHTML = `Upload project artifacts (proposals, SRS, sprint notes, task backlog) and execute the multi-agent pipeline to generate an executive intelligence summary.`;

  const risksEl = document.getElementById("risks-panel");
  if (risksEl) risksEl.innerHTML = `<div class="empty"><p>No risks analyzed yet. Run analysis to populate the risk register.</p></div>`;

  const objTextEl = document.getElementById("scope-objective-text");
  if (objTextEl) objTextEl.innerHTML = `Upload project specifications or proposals and run analysis to extract the core project objective and target audience.`;

  const inScope = document.getElementById("scope-in-panel");
  if (inScope) inScope.innerHTML = `<div class="empty"><p>Run analysis to view in-scope items.</p></div>`;

  const deliv = document.getElementById("scope-deliv-panel");
  if (deliv) deliv.innerHTML = `<div class="empty"><p>Run analysis to view deliverables and milestones.</p></div>`;

  const outScope = document.getElementById("scope-out-panel");
  if (outScope) outScope.innerHTML = `<div class="empty"><p>Run analysis to view out-of-scope boundaries.</p></div>`;

  const blk = document.getElementById("blockers-panel");
  if (blk) blk.innerHTML = `<div class="empty"><p>Run analysis to view detected blockers.</p></div>`;

  const act = document.getElementById("actions-panel");
  if (act) act.innerHTML = `<div class="empty"><p>Run analysis to view assigned action items.</p></div>`;

  const st = document.getElementById("stories-panel");
  if (st) st.innerHTML = `<div class="empty"><p>Run analysis to generate user stories.</p></div>`;
}

// ═══════════════════════════════════════════════════
//  MULTI-AGENT EXECUTION PIPELINE
// ═══════════════════════════════════════════════════
async function runPipeline() {
  const btnHeader = document.getElementById("btn-run-pipeline");
  const btnAgents = document.getElementById("btn-agents-run");
  [btnHeader, btnAgents].forEach(b => {
    if (b) {
      b.disabled = true;
      b.innerHTML = `<span class="spin"></span> Analyzing...`;
    }
  });

  toast("Executing 4-agent collaborative intelligence pipeline...", "info");
  try {
    const r = await fetch("/api/agents/run", { method: "POST" });
    if (!r.ok) {
      const err = await r.json();
      throw new Error(err.detail || "Pipeline failed");
    }
    const data = await r.json();
    currentAnalysis = data;
    renderAnalysis(data);
    loadAnalysisHistory();
    toast("Full multi-agent analysis complete!", "success");
  } catch (e) {
    toast("Analysis failed: " + e.message, "error");
  } finally {
    if (btnHeader) { btnHeader.disabled = false; btnHeader.textContent = "Run Analysis"; }
    if (btnAgents) { btnAgents.disabled = false; btnAgents.textContent = "Run Full Pipeline"; }
  }
}

async function checkExistingAnalysis() {
  try {
    const r = await fetch("/api/agents/latest");
    if (!r.ok) return;
    const data = await r.json();
    if (data && data.health_report && data.status !== "empty") {
      currentAnalysis = data;
      renderAnalysis(data);
    }
  } catch (e) {
    console.error("checkExistingAnalysis error:", e);
  }
}

async function loadLatestAnalysis() {
  toast("Refreshing latest analysis...", "info");
  try {
    const r = await fetch("/api/agents/latest");
    if (!r.ok) return;
    const data = await r.json();
    if (data && data.health_report && data.status !== "empty") {
      currentAnalysis = data;
      renderAnalysis(data);
      toast("Dashboard refreshed", "success");
    } else {
      toast("No prior analysis found. Please run analysis.", "info");
    }
  } catch (e) {
    toast("Refresh failed: " + e.message, "error");
  }
}

async function loadAnalysisHistory() {
  try {
    const r = await fetch("/api/agents/history");
    if (!r.ok) return;
    const history = await r.json();
    const select = document.getElementById("analysis-history-select");
    if (!select) return;

    if (!history || !history.length) {
      select.style.display = "none";
      return;
    }

    select.style.display = "inline-block";
    select.innerHTML = `<option value="">Analysis History (${history.length})</option>` +
      history.slice().reverse().map(h => `
        <option value="${escHtml(h.id)}">${escHtml(h.timestamp.slice(11, 16))}: ${escHtml(h.project_title.slice(0, 24))} (${h.overall_score}/100)</option>
      `).join("");

    select.onchange = async () => {
      const val = select.value;
      if (!val) return;
      toast("Loading past analysis from history...", "info");
      try {
        const resp = await fetch(`/api/agents/history/${val}`);
        if (resp.ok) {
          const item = await resp.json();
          currentAnalysis = item;
          renderAnalysis(item);
          toast("Loaded past analysis: " + val, "success");
        }
      } catch (err) {
        toast("Could not load historical run", "error");
      }
    };
  } catch (e) {
    console.error("loadAnalysisHistory error:", e);
  }
}

async function runSingleAgent(agentType) {
  toast(`Running ${agentType} agent...`, "info");
  try {
    const r = await fetch(`/api/agents/${agentType}`, { method: "POST" });
    if (!r.ok) {
      const err = await r.json();
      throw new Error(err.detail || "Agent execution failed");
    }
    const res = await r.json();
    toast(`${agentType.toUpperCase()} agent completed`, "success");

    if (agentType === "scope") {
      renderScope(res);
      navigateTo("page-scope");
    } else if (agentType === "risks") {
      renderRisks(res.risks, res.delivery_forecast);
      navigateTo("page-risks");
    } else if (agentType === "blockers") {
      renderBlockers(res.blockers);
      renderActions(res.action_items);
      navigateTo("page-blockers");
    } else if (agentType === "documentation") {
      renderStories(res.user_stories);
      navigateTo("page-agents");
    }
  } catch (e) {
    toast(`Agent error: ${e.message}`, "error");
  }
}

// ═══════════════════════════════════════════════════
//  RENDER ANALYSIS ACROSS ALL PAGES
// ═══════════════════════════════════════════════════
function renderAnalysis(data) {
  if (!data) return;
  renderHomeProjectDetails(data);
  renderKPIs(data);
  renderHealthDimensions(data.health_report);
  renderForecast(data.delivery_forecast);
  renderExecSummary(data.health_report);
  renderScope(data.scope_report);
  renderRisks(data.risks, data.delivery_forecast);
  renderBlockers(data.blockers);
  renderActions(data.action_items);
  renderStories(data.documentation?.user_stories);
}

// 0. Active Home Project Details
function renderHomeProjectDetails(data) {
  const scope = data.scope_report || {};
  const risks = data.risks || [];
  const pTitle = document.getElementById("home-project-title");
  const pDesc = document.getElementById("home-project-desc");
  const sFile = document.getElementById("home-source-file");
  const dType = document.getElementById("home-doc-type");
  const iStat = document.getElementById("home-intel-status");

  if (pTitle && scope.project_title) {
    pTitle.textContent = scope.project_title;
  }
  if (pDesc && scope.project_objective) {
    pDesc.textContent = scope.project_objective;
  }
  if (sFile) {
    const src = risks[0]?.source_reference || scope.in_scope_items?.[0]?.source_reference || "Uploaded Artifact";
    sFile.textContent = src;
  }
  if (dType) {
    dType.textContent = "Parsed & Vector Indexed";
  }
  if (iStat) {
    iStat.textContent = "Active & Grounded";
  }
}

// 1. KPIs
function renderKPIs(data) {
  const h = data.health_report || {};
  const risks = data.risks || [];
  const blockers = data.blockers || [];
  const actions = data.action_items || [];

  const kpiHealth = document.getElementById("kpi-health");
  const kpiGrade  = document.getElementById("kpi-grade");
  if (kpiHealth) {
    kpiHealth.textContent = h.overall_score !== undefined ? `${h.overall_score}/100` : "—";
    kpiHealth.style.color = h.overall_score >= 80 ? "var(--success)"
      : h.overall_score >= 65 ? "#4da6ff"
      : h.overall_score >= 50 ? "var(--warning)"
      : "var(--danger)";
  }
  if (kpiGrade) kpiGrade.textContent = h.health_grade ? `Health Grade: ${h.health_grade}` : "Analysis complete";

  setText("kpi-risks", risks.length);
  const highRisks = risks.filter(r => r.severity_score >= 15).length;
  setText("kpi-high-risks", `${highRisks} critical severity (score >= 15)`);

  setText("kpi-blockers", blockers.length);
  const critBlockers = blockers.filter(b => b.severity === "critical").length;
  setText("kpi-crit-blockers", `${critBlockers} critical severity`);

  setText("kpi-actions", actions.length);
}

// 2. Health Dimensions
function renderHealthDimensions(h) {
  const el = document.getElementById("dim-bars");
  if (!el) return;
  if (!h || !h.categories || !h.categories.length) {
    el.innerHTML = `<div class="empty"><p>No dimension scores available.</p></div>`;
    return;
  }
  el.innerHTML = h.categories.map(cat => {
    const score = cat.score || 0;
    const color = score >= 80 ? "var(--success)" : score >= 60 ? "var(--warning)" : "var(--danger)";
    return `
      <div class="dim-row">
        <div class="dim-label">${escHtml(cat.category_name)}</div>
        <div class="dim-track">
          <div class="dim-fill" style="width:${score}%;background:${color}"></div>
        </div>
        <div class="dim-pct" style="color:${color}">${score}%</div>
      </div>`;
  }).join("");
}

// 3. Delivery Forecast
function renderForecast(f) {
  const el = document.getElementById("forecast-panel");
  const rfEl = document.getElementById("risk-forecast-panel");
  if (!f) return;

  const statusColor = f.forecast_status === "On Track" ? "var(--success)"
    : f.forecast_status === "At Risk" ? "var(--warning)" : "var(--danger)";

  const content = `
    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;padding-bottom:10px;border-bottom:1px solid var(--border)">
      <div>
        <div style="font-size:11px;font-weight:700;color:var(--text-dim);text-transform:uppercase">Schedule Status</div>
        <div style="font-size:20px;font-weight:700;color:${statusColor}">${escHtml(f.forecast_status || "Undetermined")}</div>
      </div>
      <div style="text-align:right">
        <div style="font-size:11px;font-weight:700;color:var(--text-dim);text-transform:uppercase">Predicted Variance</div>
        <div style="font-size:18px;font-weight:700;color:var(--text)">${f.predicted_delay_days || 0} Days Delay</div>
      </div>
    </div>
    <div style="font-size:12.5px;line-height:1.6;color:var(--text);margin-bottom:12px">
      ${escHtml(f.forecast_narrative || "No forecast narrative generated.")}
    </div>
    ${(f.critical_path_factors || []).length ? `
      <div style="font-size:11px;font-weight:700;color:var(--text-dim);text-transform:uppercase;margin-bottom:6px">Critical Path Bottlenecks</div>
      <div style="display:flex;flex-direction:column;gap:5px">
        ${f.critical_path_factors.map(cp => `
          <div style="font-size:12px;color:var(--text-muted);padding:4px 8px;background:var(--surface2);border-radius:3px;border-left:2px solid var(--warning)">
            ${escHtml(cp)}
          </div>`).join("")}
      </div>` : ""}`;

  if (el) el.innerHTML = content;
  if (rfEl) rfEl.innerHTML = content;
}

// 4. Executive Summary
function renderExecSummary(h) {
  const el = document.getElementById("exec-summary");
  if (!el || !h) return;
  el.innerHTML = `
    <div style="font-size:13.5px;color:var(--text);line-height:1.7;margin-bottom:14px">
      ${escHtml(h.executive_summary || "Executive summary unavailable.")}
    </div>
    <div class="g2" style="margin-top:10px">
      ${(h.top_positives || []).length ? `
        <div style="background:var(--surface2);padding:12px 14px;border-radius:4px;border-left:3px solid var(--success)">
          <div style="font-size:11px;font-weight:700;color:var(--success);text-transform:uppercase;margin-bottom:6px">Project Strengths</div>
          ${h.top_positives.map(p => `<div style="font-size:12px;color:var(--text-muted);margin-bottom:3px">[+] ${escHtml(p)}</div>`).join("")}
        </div>` : ""}
      ${(h.top_vulnerabilities || []).length ? `
        <div style="background:var(--surface2);padding:12px 14px;border-radius:4px;border-left:3px solid var(--danger)">
          <div style="font-size:11px;font-weight:700;color:var(--danger);text-transform:uppercase;margin-bottom:6px">Key Vulnerabilities</div>
          ${h.top_vulnerabilities.map(v => `<div style="font-size:12px;color:var(--text-muted);margin-bottom:3px">[-] ${escHtml(v)}</div>`).join("")}
        </div>` : ""}
    </div>`;
}

// 5. Scope & Objectives (Strict Layout Order: Objective First, In-Scope, Deliverables, Out-of-Scope)
function renderScope(s) {
  if (!s) return;

  // 1. Primary Objective Block (Prominent)
  const objTextEl = document.getElementById("scope-objective-text");
  if (objTextEl) {
    objTextEl.innerHTML = `
      <div style="font-size:15px;font-weight:700;color:#fff;margin-bottom:4px">
        ${escHtml(s.project_title || "Enterprise Software Initiative")}
      </div>
      <div style="font-size:13px;color:var(--text);line-height:1.6;margin-bottom:8px">
        ${escHtml(s.project_objective || "Establish an intelligent project intelligence and risk advisory platform.")}
      </div>
      <div style="font-size:11.5px;color:var(--text-dim)">
        <strong>Target Stakeholders:</strong> ${escHtml(s.target_audience || "Engineering teams, product owners, and leadership")}
      </div>`;
  }

  // 2. In-Scope Items Table
  const inScopeEl = document.getElementById("scope-in-panel");
  if (inScopeEl) {
    const items = s.in_scope_items || [];
    if (!items.length) {
      inScopeEl.innerHTML = `<div class="empty"><p>No in-scope items detected.</p></div>`;
    } else {
      inScopeEl.innerHTML = `
        <div class="tbl-wrap">
          <table class="tbl">
            <thead>
              <tr>
                <th style="width:70px">ID</th>
                <th>Requirement / Feature</th>
                <th>Category</th>
                <th>Source Document</th>
              </tr>
            </thead>
            <tbody>
              ${items.map(item => `
                <tr>
                  <td style="color:var(--text-dim);font-family:monospace">${escHtml(item.id)}</td>
                  <td>
                    <div style="font-weight:600;color:var(--text)">${escHtml(item.title)}</div>
                    <div style="font-size:11.5px;color:var(--text-muted);margin-top:2px">${escHtml(item.description || "")}</div>
                  </td>
                  <td><span class="badge badge-blue">${escHtml(item.category || "core_feature")}</span></td>
                  <td><span class="source-tag">${escHtml(item.source_reference || "System Specification")}</span></td>
                </tr>`).join("")}
            </tbody>
          </table>
        </div>`;
    }
  }

  // 3. Key Deliverables Table
  const delivEl = document.getElementById("scope-deliv-panel");
  if (delivEl) {
    const delivs = s.key_deliverables || [];
    if (!delivs.length) {
      delivEl.innerHTML = `<div class="empty"><p>No deliverables recorded.</p></div>`;
    } else {
      delivEl.innerHTML = `
        <div class="tbl-wrap">
          <table class="tbl">
            <thead>
              <tr>
                <th style="width:70px">ID</th>
                <th>Deliverable Description</th>
                <th>Milestone</th>
                <th>Target Date</th>
                <th>Type</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              ${delivs.map(d => {
                const statusBadge = d.status === "completed" ? "badge-green" : d.status === "in_progress" ? "badge-blue" : "badge-gray";
                return `
                  <tr>
                    <td style="color:var(--text-dim);font-family:monospace">${escHtml(d.id)}</td>
                    <td>
                      <div style="font-weight:600;color:var(--text)">${escHtml(d.title)}</div>
                      <div style="font-size:11.5px;color:var(--text-muted);margin-top:2px">${escHtml(d.description || "")}</div>
                    </td>
                    <td><span class="badge badge-gray">${escHtml(d.milestone || "Phase 1")}</span></td>
                    <td style="font-weight:500">${escHtml(d.target_date || "Sprint Schedule")}</td>
                    <td><span class="badge badge-blue">${escHtml(d.deliverable_type || "feature")}</span></td>
                    <td><span class="badge ${statusBadge}">${escHtml((d.status || "pending").toUpperCase())}</span></td>
                  </tr>`;
              }).join("")}
            </tbody>
          </table>
        </div>`;
    }
  }

  // 4. Out-of-Scope Constraints Table
  const outEl = document.getElementById("scope-out-panel");
  if (outEl) {
    const outItems = s.out_of_scope_items || [];
    if (!outItems.length) {
      outEl.innerHTML = `<div class="empty"><p>No out-of-scope boundaries defined.</p></div>`;
    } else {
      outEl.innerHTML = `
        <div class="tbl-wrap">
          <table class="tbl">
            <thead>
              <tr>
                <th style="width:70px">ID</th>
                <th>Constraint / Excluded Scope</th>
                <th>Rationale / Guardrail</th>
                <th>Source Document</th>
              </tr>
            </thead>
            <tbody>
              ${outItems.map(item => `
                <tr>
                  <td style="color:var(--text-dim);font-family:monospace">${escHtml(item.id)}</td>
                  <td style="font-weight:600;color:var(--text)">${escHtml(item.title)}</td>
                  <td style="font-size:12px;color:var(--text-muted)">${escHtml(item.description || "Excluded from current release")}</td>
                  <td><span class="source-tag">${escHtml(item.source_reference || "Scope Guardrails")}</span></td>
                </tr>`).join("")}
            </tbody>
          </table>
        </div>`;
    }
  }
}

// 6. Risk Register & 5x5 Matrix (with Source File Column)
function renderRisks(risks, forecast) {
  renderRiskMatrixGrid(risks);
  const el = document.getElementById("risks-panel");
  if (!el) return;
  if (!risks || !risks.length) {
    el.innerHTML = `<div class="empty"><p>No project risks analyzed yet. Run analysis to populate.</p></div>`;
    return;
  }

  el.innerHTML = `
    <div class="tbl-wrap">
      <table class="tbl">
        <thead>
          <tr>
            <th style="width:65px">ID</th>
            <th>Risk Title &amp; Description</th>
            <th>Source Document</th>
            <th>Category</th>
            <th>Prob.</th>
            <th>Impact</th>
            <th>Severity (P x I)</th>
            <th>Status</th>
            <th>Mitigation Strategy</th>
          </tr>
        </thead>
        <tbody>
          ${risks.map(r => {
            const score = r.severity_score || 10;
            const sevClass = score >= 15 ? "sev-high" : score >= 8 ? "sev-medium" : "sev-low";
            const sevLabel = score >= 15 ? "HIGH" : score >= 8 ? "MEDIUM" : "LOW";
            return `
              <tr>
                <td style="font-family:monospace;color:var(--text-dim)">${escHtml(r.id || "RSK")}</td>
                <td>
                  <div style="font-weight:600;color:var(--text)">${escHtml(r.risk_title)}</div>
                  <div style="font-size:11.5px;color:var(--text-muted);margin-top:2px">${escHtml(r.description || "")}</div>
                </td>
                <td><span class="source-tag">${escHtml(r.source_reference || "Uploaded Artifact")}</span></td>
                <td><span class="badge badge-gray">${escHtml(r.category || "General")}</span></td>
                <td style="font-size:11.5px">${escHtml(r.probability || "Med")}</td>
                <td style="font-size:11.5px">${escHtml(r.impact || "Med")}</td>
                <td>
                  <span class="sev-pill ${sevClass}">${score} (${sevLabel})</span>
                </td>
                <td><span class="badge badge-blue">${escHtml((r.status || "identified").toUpperCase())}</span></td>
                <td style="font-size:12px;color:var(--text);line-height:1.4">${escHtml(r.mitigation_strategy || "Standard monitoring")}</td>
              </tr>`;
          }).join("")}
        </tbody>
      </table>
    </div>`;
}

function renderRiskMatrixGrid(risks) {
  const container = document.getElementById("risk-matrix-grid-container");
  if (!container) return;
  if (!risks || !risks.length) {
    container.innerHTML = `<div class="empty"><p>Analyze project artifacts to view mapped 5x5 severity matrix.</p></div>`;
    return;
  }

  // Map probability & impact strings or numbers to 1-5
  function toRank(val) {
    if (typeof val === "number") return Math.min(5, Math.max(1, Math.round(val)));
    const s = String(val || "").toLowerCase();
    if (s.includes("crit") || s.includes("very high") || s === "5") return 5;
    if (s.includes("high") || s === "4") return 4;
    if (s.includes("med") || s === "3") return 3;
    if (s.includes("low-med") || s === "2") return 2;
    return 1;
  }

  // Group risks by (prob, impact)
  const cellRisks = {};
  risks.forEach(r => {
    const p = toRank(r.probability);
    const i = toRank(r.impact);
    const key = `${p}_${i}`;
    if (!cellRisks[key]) cellRisks[key] = [];
    cellRisks[key].push(r);
  });

  // Build 5x5 Grid (Rows = Prob 5 down to 1, Cols = Impact 1 up to 5)
  let gridHtml = `
    <div style="display:flex;gap:20px;flex-wrap:wrap;align-items:flex-start">
      <div style="flex:1;min-width:320px;max-width:540px;background:var(--surface2);border:1px solid var(--border);border-radius:var(--radius);padding:14px">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
          <span style="font-size:10px;font-weight:700;color:var(--text-dim);text-transform:uppercase">Probability (1-5) &darr; vs Impact (1-5) &rarr;</span>
          <span style="font-size:11px;color:var(--primary-lt);font-weight:600">${risks.length} Mapped Risks</span>
        </div>
        <div style="display:grid;grid-template-columns:repeat(5, 1fr);gap:4px;text-align:center">`;

  for (let p = 5; p >= 1; p--) {
    for (let i = 1; i <= 5; i++) {
      const score = p * i;
      const key = `${p}_${i}`;
      const mapped = cellRisks[key] || [];
      const hasRisks = mapped.length > 0;

      let bg = "rgba(34,197,94,0.12)";
      let color = "#86efac";
      let border = "1px solid rgba(34,197,94,0.2)";

      if (score >= 15) {
        bg = hasRisks ? "rgba(239,68,68,0.35)" : "rgba(239,68,68,0.15)";
        color = "#fca5a5";
        border = hasRisks ? "1px solid #ef4444" : "1px solid rgba(239,68,68,0.25)";
      } else if (score >= 8) {
        bg = hasRisks ? "rgba(245,158,11,0.3)" : "rgba(245,158,11,0.12)";
        color = "#fde047";
        border = hasRisks ? "1px solid #f59e0b" : "1px solid rgba(245,158,11,0.25)";
      } else {
        if (hasRisks) {
          bg = "rgba(34,197,94,0.3)";
          border = "1px solid #22c55e";
        }
      }

      const riskBadge = hasRisks 
        ? `<div style="margin-top:2px;font-size:10px;font-weight:700;background:rgba(0,0,0,0.5);border-radius:3px;padding:1px 3px;color:#fff">${mapped.map(m => escHtml(m.id)).join(", ")}</div>`
        : "";

      gridHtml += `
        <div style="background:${bg};border:${border};color:${color};border-radius:4px;padding:6px 2px;min-height:48px;display:flex;flex-direction:column;justify-content:center;align-items:center" title="P:${p} x I:${i} = ${score}${hasRisks ? ' | ' + mapped.map(m => m.risk_title).join(', ') : ''}">
          <div style="font-size:11px;font-weight:700">${score}</div>
          ${riskBadge}
        </div>`;
    }
  }

  gridHtml += `
        </div>
        <div style="display:flex;justify-content:space-between;margin-top:8px;font-size:10.5px;color:var(--text-dim)">
          <span>Impact 1 (Low)</span>
          <span>Impact 3 (Medium)</span>
          <span>Impact 5 (Critical)</span>
        </div>
      </div>
      <div style="flex:1;min-width:280px">
        <div style="font-size:12px;font-weight:600;color:var(--text);margin-bottom:8px">Active Risk Severity Breakdown</div>
        <div style="display:flex;flex-direction:column;gap:8px">
          ${risks.map(r => {
            const sc = r.severity_score || 10;
            const sevColor = sc >= 15 ? "var(--danger)" : sc >= 8 ? "var(--warning)" : "var(--success)";
            return `
              <div style="display:flex;align-items:center;justify-content:space-between;padding:8px 10px;background:var(--surface2);border-left:3px solid ${sevColor};border-radius:var(--radius-sm)">
                <div>
                  <div style="font-weight:600;font-size:12px;color:var(--text)"><span style="font-family:monospace;color:var(--text-dim)">${escHtml(r.id)}:</span> ${escHtml(r.risk_title)}</div>
                  <div style="font-size:11px;color:var(--text-muted)">Source: ${escHtml(r.source_reference || "Document")} | Cat: ${escHtml(r.category || "General")}</div>
                </div>
                <div style="font-size:12px;font-weight:700;color:${sevColor}">${sc} (P:${r.probability || 'M'} &times; I:${r.impact || 'M'})</div>
              </div>`;
          }).join("")}
        </div>
      </div>
    </div>`;

  container.innerHTML = gridHtml;
}

// 7. Blockers & Action Items
function renderBlockers(blockers) {
  const el = document.getElementById("blockers-panel");
  if (!el) return;
  if (!blockers || !blockers.length) {
    el.innerHTML = `<div class="empty"><p>No blockers detected across project documents.</p></div>`;
    return;
  }
  el.innerHTML = `
    <div class="tbl-wrap">
      <table class="tbl">
        <thead>
          <tr>
            <th style="width:65px">ID</th>
            <th>Blocker Description</th>
            <th>Source Document</th>
            <th>Severity</th>
            <th>Assigned Owner</th>
            <th>Resolution Plan</th>
          </tr>
        </thead>
        <tbody>
          ${blockers.map(b => {
            const badgeClass = b.severity === "critical" ? "badge-red" : b.severity === "high" ? "badge-amber" : "badge-blue";
            return `
              <tr>
                <td style="font-family:monospace;color:var(--text-dim)">${escHtml(b.id || "BLK")}</td>
                <td>
                  <div style="font-weight:600;color:var(--text)">${escHtml(b.title)}</div>
                  <div style="font-size:11.5px;color:var(--text-muted);margin-top:2px">${escHtml(b.description || "")}</div>
                </td>
                <td><span class="source-tag">${escHtml(b.source_reference || "Meeting Notes")}</span></td>
                <td><span class="badge ${badgeClass}">${escHtml((b.severity || "medium").toUpperCase())}</span></td>
                <td style="font-weight:500;color:var(--text)">${escHtml(b.assigned_owner || "Unassigned")}</td>
                <td style="font-size:12px;color:var(--text-muted)">${escHtml(b.suggested_resolution || "Under review")}</td>
              </tr>`;
          }).join("")}
        </tbody>
      </table>
    </div>`;
}

function renderActions(actions) {
  const el = document.getElementById("actions-panel");
  if (!el) return;
  if (!actions || !actions.length) {
    el.innerHTML = `<div class="empty"><p>No action items extracted from documents.</p></div>`;
    return;
  }
  el.innerHTML = `
    <div class="tbl-wrap">
      <table class="tbl">
        <thead>
          <tr>
            <th style="width:65px">ID</th>
            <th>Task Description</th>
            <th>Assignee</th>
            <th>Priority</th>
            <th>Due Date</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          ${actions.map(a => {
            const pBadge = a.priority === "Urgent" || a.priority === "high" ? "badge-red"
              : a.priority === "Medium" ? "badge-amber" : "badge-blue";
            return `
              <tr>
                <td style="font-family:monospace;color:var(--text-dim)">${escHtml(a.id || "ACT")}</td>
                <td style="font-weight:500;color:var(--text)">${escHtml(a.task_description)}</td>
                <td style="color:var(--text)">${escHtml(a.assignee || "Team")}</td>
                <td><span class="badge ${pBadge}">${escHtml((a.priority || "Med").toUpperCase())}</span></td>
                <td style="color:var(--text-muted);font-size:11.5px">${escHtml(a.due_date || "Sprint End")}</td>
                <td><span class="badge badge-gray">${escHtml((a.status || "todo").toUpperCase())}</span></td>
              </tr>`;
          }).join("")}
        </tbody>
      </table>
    </div>`;
}

// 8. User Stories
function renderStories(stories) {
  const el = document.getElementById("stories-panel");
  if (!el) return;
  if (!stories || !stories.length) {
    el.innerHTML = `<div class="empty"><p>No user stories generated yet.</p></div>`;
    return;
  }
  el.innerHTML = `
    <div style="display:flex;flex-direction:column;gap:14px">
      ${stories.map(s => `
        <div class="card card-sm" style="border-left:3px solid var(--primary);background:var(--surface2)">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;flex-wrap:wrap;gap:8px">
            <div style="display:flex;gap:8px;align-items:center">
              <span style="font-family:monospace;font-size:11px;font-weight:700;background:rgba(0,102,204,0.15);color:var(--primary-lt);border:1px solid rgba(0,102,204,0.3);padding:2px 6px;border-radius:4px">${escHtml(s.id)}</span>
              <span style="font-weight:700;font-size:13.5px;color:var(--text)">${escHtml(s.title)}</span>
            </div>
            <div style="display:flex;gap:6px;align-items:center">
              <span class="badge badge-gray" style="font-family:monospace">${escHtml(s.epic_tag || "Feature")}</span>
              <span class="badge badge-blue">${s.estimated_story_points || 3} Story Points</span>
              <span class="badge badge-amber">${escHtml(s.priority || "Must Have")}</span>
            </div>
          </div>
          <div style="background:var(--surface);padding:10px 12px;border-radius:var(--radius-sm);border:1px solid var(--border);font-size:12.5px;margin-bottom:10px;line-height:1.6">
            <div style="margin-bottom:2px"><strong style="color:var(--text-muted)">As a</strong> <span style="color:var(--text);font-weight:600">${escHtml(s.as_a)}</span>,</div>
            <div style="margin-bottom:2px"><strong style="color:var(--text-muted)">I want to</strong> <span style="color:#60a5fa">${escHtml(s.i_want_to)}</span>,</div>
            <div><strong style="color:var(--text-muted)">So that</strong> <span style="color:var(--success)">${escHtml(s.so_that)}</span>.</div>
          </div>
          <div>
            <div style="font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;color:var(--text-dim);margin-bottom:6px">Gherkin Acceptance Criteria:</div>
            <ul style="list-style:none;padding:0;margin:0;display:flex;flex-direction:column;gap:5px">
              ${(s.acceptance_criteria || []).map(ac => `
                <li style="display:flex;gap:8px;align-items:flex-start;font-size:12px;line-height:1.5;color:var(--text)">
                  <span style="color:var(--primary-lt);font-weight:700">&bull;</span>
                  <span>${escHtml(ac)}</span>
                </li>`).join("")}
            </ul>
          </div>
        </div>`).join("")}
    </div>`;
}

// ═══════════════════════════════════════════════════
//  RAG SEMANTIC SEARCH
// ═══════════════════════════════════════════════════
async function ragSearch() {
  const q = document.getElementById("rag-query-input")?.value?.trim();
  const topK = document.getElementById("rag-topk")?.value || 5;
  const el = document.getElementById("rag-results");
  if (!q) { toast("Please enter a search query", "info"); return; }

  el.innerHTML = `<div style="text-align:center;padding:24px"><span class="spin"></span><p style="margin-top:8px;color:var(--text-muted)">Executing vector similarity retrieval...</p></div>`;

  try {
    const r = await fetch("/api/rag/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: q, top_k: parseInt(topK) }),
    });
    if (!r.ok) throw new Error(await r.text());
    const data = await r.json();
    const results = data.results || [];

    if (!results.length) {
      el.innerHTML = `<div class="empty"><p>No matching chunks found for query "${escHtml(q)}".</p></div>`;
      return;
    }

    el.innerHTML = results.map((item, i) => `
      <div class="card card-sm" style="margin-bottom:10px">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">
          <span class="source-tag">${escHtml(item.source_name || "Document")} (Chunk #${item.chunk_index ?? i})</span>
          <span class="badge badge-blue">Similarity Score: ${(item.score || 0).toFixed(3)}</span>
        </div>
        <div style="font-size:12.5px;color:var(--text);line-height:1.6;white-space:pre-wrap">${escHtml(item.excerpt || item.content || "")}</div>
      </div>`).join("");
  } catch (e) {
    el.innerHTML = `<div style="padding:12px;background:rgba(239,68,68,0.1);color:var(--danger);border-radius:4px;font-size:12px">Search failed: ${escHtml(e.message)}</div>`;
    toast("Search error", "error");
  }
}

// ═══════════════════════════════════════════════════
//  GROUNDED CONVERSATIONAL ASSISTANT
// ═══════════════════════════════════════════════════
function appendChatBubble(role, html) {
  const msgs = document.getElementById("chat-messages");
  if (!msgs) return null;
  const row = document.createElement("div");
  row.className = `msg-row ${role}`;
  row.innerHTML = `<div class="msg-bubble">${html}</div>`;
  msgs.appendChild(row);
  msgs.scrollTop = msgs.scrollHeight;
  return row;
}

async function sendChat() {
  const input = document.getElementById("chat-input");
  const q = input?.value?.trim();
  if (!q) return;
  input.value = "";

  // Append user message
  appendChatBubble("user", escHtml(q));
  chatHistory.push({ role: "user", content: q });

  const typingEl = document.getElementById("chat-typing");
  if (typingEl) typingEl.style.display = "flex";

  try {
    const r = await fetch("/api/chat/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: q, top_k: 5, conversation_history: chatHistory }),
    });
    if (!r.ok) {
      const err = await r.json();
      throw new Error(err.detail || "Chat request failed");
    }
    const data = await r.json();
    if (typingEl) typingEl.style.display = "none";

    let html = `<div>${escHtml(data.answer || "No response received.")}</div>`;

    // Render citations if available
    if (data.citations && data.citations.length) {
      html += `
        <div class="msg-meta">
          <strong>Verified Citations:</strong><br>
          ${data.citations.map(c => `• <span class="source-tag">${escHtml(c.document_name)}</span> (Chunk #${c.chunk_index}, Relevance: ${(c.score * 100).toFixed(0)}%)`).join("<br>")}
        </div>`;
    }

    if (data.confidence_score !== undefined) {
      html += `
        <div style="font-size:10.5px;color:var(--text-dim);margin-top:5px">
          Grounding Confidence: ${(data.confidence_score * 100).toFixed(0)}%
        </div>`;
    }

    appendChatBubble("bot", html);
    chatHistory.push({ role: "assistant", content: data.answer || "" });

    // Render suggested follow-ups
    const followWrap = document.getElementById("chat-followups");
    if (followWrap) {
      followWrap.innerHTML = "";
      if (data.suggested_followups && data.suggested_followups.length) {
        data.suggested_followups.forEach(fu => {
          const pill = document.createElement("button");
          pill.className = "followup-pill";
          pill.textContent = fu;
          pill.onclick = () => {
            document.getElementById("chat-input").value = fu;
            sendChat();
          };
          followWrap.appendChild(pill);
        });
      }
    }
  } catch (e) {
    if (typingEl) typingEl.style.display = "none";
    appendChatBubble("bot", `<span style="color:var(--danger)">Error: ${escHtml(e.message)}</span>`);
    toast("Chat error: " + e.message, "error");
  }
}

// ═══════════════════════════════════════════════════
//  EXPORT REPORTS
// ═══════════════════════════════════════════════════
async function exportMarkdown() {
  try {
    const r = await fetch("/api/export/markdown");
    if (!r.ok) { toast("Execute analysis before exporting reports.", "error"); return; }
    const blob = await r.blob();
    downloadBlob(blob, "Project_Intelligence_Report.md");
    toast("Markdown report downloaded", "success");
  } catch (e) {
    toast("Export failed: " + e.message, "error");
  }
}

async function exportJSON() {
  try {
    const r = await fetch("/api/export/json");
    if (!r.ok) { toast("Execute analysis before exporting data.", "error"); return; }
    const blob = await r.blob();
    downloadBlob(blob, "Project_Intelligence_Data.json");
    toast("JSON report downloaded", "success");
  } catch (e) {
    toast("Export failed: " + e.message, "error");
  }
}

function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

// ═══════════════════════════════════════════════════
//  SETTINGS & API KEY CONFIGURATION
// ═══════════════════════════════════════════════════
function openSettings() {
  const m = document.getElementById("settings-modal");
  if (m) m.classList.add("open");
}
function closeSettings() {
  const m = document.getElementById("settings-modal");
  if (m) m.classList.remove("open");
}

async function saveKeys() {
  const gk = document.getElementById("input-gemini-key")?.value?.trim();
  const ok = document.getElementById("input-openai-key")?.value?.trim();
  const statusEl = document.getElementById("key-status");

  if (!gk && !ok) {
    if (statusEl) {
      statusEl.textContent = "Please enter at least one API key.";
      statusEl.style.color = "var(--danger)";
    }
    return;
  }

  try {
    const r = await fetch("/api/export/settings/keys", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ gemini_api_key: gk || null, openai_api_key: ok || null }),
    });
    const d = await r.json();
    if (d.status === "success") {
      if (statusEl) {
        statusEl.textContent = `Provider active: ${d.active_provider}`;
        statusEl.style.color = "var(--success)";
      }
      toast(`Keys configured. Active: ${d.active_provider}`, "success");
      loadStatus();
      setTimeout(closeSettings, 1000);
    }
  } catch (e) {
    if (statusEl) {
      statusEl.textContent = "Failed to update keys: " + e.message;
      statusEl.style.color = "var(--danger)";
    }
  }
}

// ═══════════════════════════════════════════════════
//  EVENT LISTENERS BINDING
// ═══════════════════════════════════════════════════
function initButtons() {
  // Header buttons
  safeOn("btn-load-samples",      "click", loadSamples);
  safeOn("btn-load-samples-page", "click", loadSamples);
  safeOn("btn-clear-all-docs",    "click", clearAllDocs);
  safeOn("btn-run-pipeline",      "click", runPipeline);
  safeOn("btn-open-settings",     "click", openSettings);

  // Dashboard refresh
  safeOn("btn-refresh-dashboard", "click", loadLatestAnalysis);

  // Settings modal
  safeOn("btn-close-settings",  "click", closeSettings);
  safeOn("btn-close-settings2", "click", closeSettings);
  safeOn("btn-save-keys",       "click", saveKeys);

  // Agents page
  safeOn("btn-agents-run",      "click", runPipeline);

  // RAG Search
  safeOn("btn-rag-search",      "click", ragSearch);
  const ragInput = document.getElementById("rag-query-input");
  if (ragInput) ragInput.addEventListener("keydown", e => { if (e.key === "Enter") ragSearch(); });

  // Grounded Chat
  safeOn("btn-send-chat",       "click", sendChat);
  safeOn("btn-clear-chat",      "click", () => {
    chatHistory = [];
    const msgs = document.getElementById("chat-messages");
    if (msgs) {
      msgs.innerHTML = `
        <div class="msg-row bot">
          <div class="msg-bubble">Conversation history cleared. Upload documents or ask a question regarding the project.</div>
        </div>`;
    }
    const followWrap = document.getElementById("chat-followups");
    if (followWrap) followWrap.innerHTML = "";
    toast("Chat cleared", "info");
  });
  const chatInput = document.getElementById("chat-input");
  if (chatInput) chatInput.addEventListener("keydown", e => { if (e.key === "Enter") sendChat(); });

  // Export buttons
  safeOn("btn-export-md",   "click", exportMarkdown);
  safeOn("btn-export-json", "click", exportJSON);

  // Close modal on outside click
  const modal = document.getElementById("settings-modal");
  if (modal) modal.addEventListener("click", e => { if (e.target === modal) closeSettings(); });
}

// ═══════════════════════════════════════════════════
//  UTILITY HELPERS
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
  return String(str ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
