// AI Project Intelligence & Risk Advisor Client-Side Application

let radarChart = null;
let currentAnalysis = null;

// Initialize on DOM ready
document.addEventListener("DOMContentLoaded", () => {
  initIcons();
  initNavigation();
  initUploadDropzone();
  initEventListeners();
  initRadarChart();
  loadSystemStatus();
  loadDocuments();
  loadLatestAnalysis();
});

function initIcons() {
  if (window.lucide) {
    lucide.createIcons();
  }
}

// ----------------- TAB NAVIGATION -----------------
function initNavigation() {
  const tabs = document.querySelectorAll(".nav-tab");
  tabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      const targetId = tab.getAttribute("data-tab");

      // Set active tab button style
      tabs.forEach((t) => {
        t.classList.remove("active", "text-blue-400", "bg-blue-500/10");
        t.classList.add("text-slate-400");
      });
      tab.classList.add("active", "text-blue-400", "bg-blue-500/10");
      tab.classList.remove("text-slate-400");

      // Hide all contents and show active
      document.querySelectorAll(".tab-content").forEach((c) => {
        c.classList.add("hidden");
        c.classList.remove("block");
      });
      const activeContent = document.getElementById(targetId);
      if (activeContent) {
        activeContent.classList.remove("hidden");
        activeContent.classList.add("block");
      }

      // Re-render radar chart if overview tab is focused
      if (targetId === "tab-overview" && radarChart) {
        radarChart.resize();
      }
    });
  });
}

// ----------------- TOAST NOTIFICATIONS -----------------
function showToast(message, type = "info") {
  const container = document.getElementById("toast-container");
  const toast = document.createElement("div");
  const bg =
    type === "success"
      ? "bg-emerald-600"
      : type === "error"
      ? "bg-rose-600"
      : type === "warning"
      ? "bg-amber-600"
      : "bg-blue-600";

  toast.className = `${bg} text-white px-4 py-2.5 rounded-xl shadow-lg text-xs font-semibold flex items-center space-x-2 pointer-events-auto transform transition-all duration-300 translate-y-2 opacity-0`;
  toast.innerHTML = `<span>${message}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.classList.remove("translate-y-2", "opacity-0");
  }, 10);

  setTimeout(() => {
    toast.classList.add("translate-y-2", "opacity-0");
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

// ----------------- SYSTEM STATUS & SETTINGS -----------------
async function loadSystemStatus() {
  try {
    const res = await fetch("/api/export/status");
    if (res.ok) {
      const data = await res.json();
      const label = document.getElementById("active-llm-label");
      if (label) {
        label.textContent = `Engine: ${data.active_provider}`;
      }
    }
  } catch (e) {
    console.error("Failed to load system status", e);
  }
}

// ----------------- RADAR CHART -----------------
function initRadarChart() {
  const ctx = document.getElementById("healthRadarChart");
  if (!ctx) return;

  radarChart = new Chart(ctx, {
    type: "radar",
    data: {
      labels: ["Planning & Scope", "Timeline Adherence", "Risk Mitigation", "Docs Coverage", "Blocker Resolution"],
      datasets: [
        {
          label: "Health Index",
          data: [75, 65, 70, 80, 85],
          backgroundColor: "rgba(59, 130, 246, 0.25)",
          borderColor: "rgba(59, 130, 246, 0.9)",
          pointBackgroundColor: "#3b82f6",
          pointBorderColor: "#fff",
          pointHoverBackgroundColor: "#fff",
          pointHoverBorderColor: "#3b82f6",
          borderWidth: 2,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        r: {
          angleLines: { color: "rgba(255, 255, 255, 0.1)" },
          grid: { color: "rgba(255, 255, 255, 0.08)" },
          pointLabels: {
            color: "#94a3b8",
            font: { size: 10, family: "Inter" },
          },
          ticks: {
            display: false,
            min: 0,
            max: 100,
            stepSize: 20,
          },
        },
      },
      plugins: {
        legend: { display: false },
      },
    },
  });
}

function updateRadarChart(metrics) {
  if (!radarChart || !metrics) return;
  radarChart.data.datasets[0].data = [
    metrics["Planning"] || 50,
    metrics["Timeline"] || 50,
    metrics["Risk"] || 50,
    metrics["Docs"] || 50,
    metrics["Blockers"] || 50,
  ];
  radarChart.update();
}

// ----------------- LOAD LATEST OR RUN ANALYSIS -----------------
async function loadLatestAnalysis() {
  try {
    const res = await fetch("/api/agents/latest");
    if (res.ok) {
      const data = await res.json();
      if (data && data.health_report) {
        currentAnalysis = data;
        renderAllDashboardData(data);
      }
    }
  } catch (e) {
    console.error("Failed to load analysis", e);
  }
}

async function runMultiAgentPipeline() {
  const btn = document.getElementById("btn-run-pipeline");
  const origHtml = btn.innerHTML;
  btn.innerHTML = `<svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white inline" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path></svg> Running Agents...`;
  btn.disabled = true;

  try {
    showToast("Triggered Multi-Agent Pipeline (Scope, Risks, Blockers, Docs, Health)...", "info");
    const res = await fetch("/api/agents/run", { method: "POST" });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Agent execution failed");
    }
    const data = await res.json();
    currentAnalysis = data;
    renderAllDashboardData(data);
    showToast("Multi-Agent analysis completed successfully!", "success");
  } catch (e) {
    showToast(e.message, "error");
  } finally {
    btn.innerHTML = origHtml;
    btn.disabled = false;
    initIcons();
  }
}

// ----------------- RENDER ALL DASHBOARD TABS -----------------
function renderAllDashboardData(data) {
  const health = data.health_report || {};
  const forecast = data.delivery_forecast || {};
  const scope = data.scope_report || {};
  const risks = data.risks || [];
  const blockers = data.blockers || [];
  const actions = data.action_items || [];
  const docs = data.documentation || {};

  // TAB 1: OVERVIEW
  // Health Score & Grade
  const scoreVal = health.overall_score !== undefined ? health.overall_score : 70;
  document.getElementById("health-score-val").textContent = scoreVal.toFixed(1);
  document.getElementById("health-grade-badge").textContent = `Grade ${health.health_grade || "B"}`;
  document.getElementById("health-score-bar").style.width = `${Math.min(100, Math.max(0, scoreVal))}%`;

  // Forecast Cards
  document.getElementById("forecast-status-val").textContent = forecast.forecast_status || "On Track";
  document.getElementById("forecast-delay-val").textContent = `~${forecast.predicted_delay_days || 0} Days`;
  document.getElementById("forecast-subtext").textContent = forecast.forecast_narrative || "";

  // Risk & Blocker Counters
  const highRisks = risks.filter((r) => r.severity_score >= 15);
  document.getElementById("risk-count-val").textContent = highRisks.length;
  const maxSev = risks.reduce((m, r) => Math.max(m, r.severity_score), 0);
  document.getElementById("top-severity-val").textContent = `${maxSev} / 25`;

  document.getElementById("blocker-count-val").textContent = blockers.length;
  document.getElementById("action-count-val").textContent = `${actions.length} Items`;

  // Radar Chart
  if (health.radar_metrics) {
    updateRadarChart(health.radar_metrics);
  }

  // Category Progress List
  const catList = document.getElementById("category-progress-list");
  if (catList && health.categories) {
    catList.innerHTML = health.categories
      .map((c) => {
        const color =
          c.status === "healthy"
            ? "from-emerald-500 to-teal-500"
            : c.status === "warning"
            ? "from-amber-500 to-orange-500"
            : "from-rose-500 to-red-500";
        return `
          <div>
            <div class="flex justify-between text-xs mb-1">
              <span class="font-semibold text-slate-200">${c.category_name} <span class="text-slate-500">(${Math.round(c.weight * 100)}%)</span></span>
              <span class="font-bold text-slate-300">${c.score}/100</span>
            </div>
            <div class="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
              <div class="bg-gradient-to-r ${color} h-1.5 rounded-full" style="width: ${c.score}%"></div>
            </div>
            <div class="text-[11px] text-slate-400 mt-1">${c.improvement_advice || ""}</div>
          </div>
        `;
      })
      .join("");
  }

  // Executive summary
  document.getElementById("executive-summary-text").textContent =
    health.executive_summary || "Synthesized analysis across all uploaded project artifacts.";

  // Positives & Vulnerabilities
  const posList = document.getElementById("positives-list");
  if (posList && health.top_positives) {
    posList.innerHTML = health.top_positives
      .map(
        (p) => `
        <li class="flex items-start space-x-2">
          <i data-lucide="check" class="w-3.5 h-3.5 text-emerald-400 mt-0.5 flex-shrink-0"></i>
          <span>${p}</span>
        </li>
      `
      )
      .join("");
  }

  const vulnList = document.getElementById("vulnerabilities-list");
  if (vulnList && health.top_vulnerabilities) {
    vulnList.innerHTML = health.top_vulnerabilities
      .map(
        (v) => `
        <li class="flex items-start space-x-2">
          <i data-lucide="alert-triangle" class="w-3.5 h-3.5 text-rose-400 mt-0.5 flex-shrink-0"></i>
          <span>${v}</span>
        </li>
      `
      )
      .join("");
  }

  // TAB 3: RISKS & FORECASTING
  document.getElementById("forecast-header-status").textContent = `Status: ${forecast.forecast_status} (~${forecast.predicted_delay_days} Days Delay)`;
  document.getElementById("forecast-narrative-p").textContent = forecast.forecast_narrative || "";
  document.getElementById("forecast-confidence-badge").textContent = `${Math.round((forecast.confidence_level || 0.85) * 100)}%`;

  const critTags = document.getElementById("critical-factors-tags");
  if (critTags && forecast.critical_path_factors) {
    critTags.innerHTML = forecast.critical_path_factors
      .map(
        (cf) => `
        <span class="px-2.5 py-1 rounded-md bg-amber-500/20 text-amber-300 border border-amber-500/30 font-medium">
          ${cf}
        </span>
      `
      )
      .join("");
  }

  // Risk cards
  const riskCards = document.getElementById("risk-cards-container");
  if (riskCards) {
    riskCards.innerHTML = risks
      .map((r) => {
        const badgeColor =
          r.severity_score >= 15
            ? "bg-rose-500/20 text-rose-400 border-rose-500/30"
            : r.severity_score >= 8
            ? "bg-amber-500/20 text-amber-400 border-amber-500/30"
            : "bg-emerald-500/20 text-emerald-400 border-emerald-500/30";
        return `
        <div class="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2">
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-2">
              <span class="px-2 py-0.5 rounded text-[11px] font-bold font-mono ${badgeColor} border">${r.id}</span>
              <h4 class="text-xs font-bold text-white">${r.risk_title}</h4>
            </div>
            <span class="px-2.5 py-0.5 rounded-full text-[11px] font-bold ${badgeColor} border">
              Severity: ${r.severity_score} / 25
            </span>
          </div>
          <p class="text-xs text-slate-300 leading-relaxed">${r.description}</p>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs pt-2 border-t border-slate-800/80">
            <div>
              <span class="text-slate-400 font-semibold">Probability:</span> <span class="text-slate-200">${r.probability}</span> |
              <span class="text-slate-400 font-semibold">Impact:</span> <span class="text-slate-200">${r.impact}</span>
            </div>
            <div class="text-right sm:text-right">
              <span class="text-slate-400 font-semibold">Category:</span> <span class="text-blue-400 uppercase font-mono">${r.category}</span>
            </div>
          </div>
          <div class="p-2.5 rounded-lg bg-slate-950/80 border border-slate-800/80 text-xs space-y-1">
            <div><span class="text-emerald-400 font-semibold">Mitigation Strategy:</span> <span class="text-slate-300">${r.mitigation_strategy}</span></div>
            ${r.contingency_plan ? `<div><span class="text-blue-400 font-semibold">Contingency Plan:</span> <span class="text-slate-300">${r.contingency_plan}</span></div>` : ""}
          </div>
        </div>
      `;
      })
      .join("");
  }

  // TAB 4: SCOPE & DELIVERABLES
  document.getElementById("scope-project-title").textContent = scope.project_title || "Project Scope";
  document.getElementById("scope-project-obj").textContent = scope.project_objective || "";
  document.getElementById("scope-target-aud").textContent = scope.target_audience || "Engineering Team";

  const inScopeContainer = document.getElementById("in-scope-items-container");
  if (inScopeContainer && scope.in_scope_items) {
    inScopeContainer.innerHTML = scope.in_scope_items
      .map(
        (sc) => `
        <div class="p-3 rounded-lg bg-slate-900/60 border border-slate-800/80 flex items-start space-x-2 text-xs">
          <i data-lucide="check" class="w-4 h-4 text-emerald-400 mt-0.5 flex-shrink-0"></i>
          <div>
            <div class="font-semibold text-slate-200">${sc.title} <span class="text-[10px] text-blue-400 font-mono">(${sc.category})</span></div>
            <div class="text-slate-400 mt-0.5">${sc.description}</div>
          </div>
        </div>
      `
      )
      .join("");
  }

  const outScopeContainer = document.getElementById("out-of-scope-items-container");
  if (outScopeContainer && scope.out_of_scope_items) {
    outScopeContainer.innerHTML = scope.out_of_scope_items
      .map(
        (oos) => `
        <div class="p-3 rounded-lg bg-slate-900/40 border border-slate-800/60 flex items-start space-x-2 text-xs">
          <i data-lucide="minus-circle" class="w-4 h-4 text-rose-400 mt-0.5 flex-shrink-0"></i>
          <div>
            <div class="font-semibold text-slate-300">${oos.title}</div>
            <div class="text-slate-500 mt-0.5">${oos.description}</div>
          </div>
        </div>
      `
      )
      .join("");
  }

  const delivTableBody = document.getElementById("deliverables-table-body");
  if (delivTableBody && scope.key_deliverables) {
    delivTableBody.innerHTML = scope.key_deliverables
      .map(
        (d) => `
        <tr class="hover:bg-slate-800/30 transition">
          <td class="p-3 font-mono text-blue-400">${d.id}</td>
          <td class="p-3 font-semibold text-slate-200">${d.title}<div class="text-[10px] text-slate-400">${d.description}</div></td>
          <td class="p-3">${d.milestone || "Phase 1"}</td>
          <td class="p-3 text-slate-300 font-medium">${d.target_date || "Sprint"}</td>
          <td class="p-3"><span class="px-2 py-0.5 rounded text-[10px] font-mono bg-slate-800 text-slate-300">${d.deliverable_type}</span></td>
          <td class="p-3"><span class="px-2 py-0.5 rounded text-[10px] font-bold ${
            d.status === "completed" ? "bg-emerald-500/20 text-emerald-400" : d.status === "in_progress" ? "bg-blue-500/20 text-blue-400" : "bg-slate-800 text-slate-400"
          }">${d.status}</span></td>
        </tr>
      `
      )
      .join("");
  }

  // TAB 5: BLOCKERS & ACTIONS
  const blockersContainer = document.getElementById("blockers-list-container");
  if (blockersContainer) {
    blockersContainer.innerHTML = blockers
      .map((b) => {
        const sevColor =
          b.severity === "critical"
            ? "border-rose-500/40 bg-rose-500/10 text-rose-300"
            : b.severity === "high"
            ? "border-amber-500/40 bg-amber-500/10 text-amber-300"
            : "border-blue-500/40 bg-blue-500/10 text-blue-300";
        return `
        <div class="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2">
          <div class="flex items-center justify-between">
            <span class="text-xs font-bold text-white">${b.title}</span>
            <span class="px-2 py-0.5 rounded text-[10px] uppercase font-bold border ${sevColor}">${b.severity}</span>
          </div>
          <p class="text-xs text-slate-300">${b.description}</p>
          <div class="flex items-center justify-between text-[11px] text-slate-400 pt-2 border-t border-slate-800">
            <div>Owner: <span class="text-slate-200 font-semibold">${b.assigned_owner || "Unassigned"}</span> | Impacts: <span class="text-slate-200">${b.impacted_deliverable}</span></div>
          </div>
          <div class="text-xs text-emerald-300 bg-emerald-950/30 p-2 rounded border border-emerald-800/40">
            <span class="font-semibold">Resolution:</span> ${b.suggested_resolution}
          </div>
        </div>
      `;
      })
      .join("");
  }

  const actionsContainer = document.getElementById("actions-list-container");
  if (actionsContainer) {
    actionsContainer.innerHTML = actions
      .map(
        (a) => `
        <div class="p-3 rounded-lg bg-slate-900/60 border border-slate-800 flex items-center justify-between text-xs hover:border-slate-700 transition">
          <div class="flex items-center space-x-3">
            <input type="checkbox" ${a.status === "done" ? "checked" : ""} class="rounded bg-slate-800 border-slate-700 text-blue-600 focus:ring-0">
            <span class="text-slate-200 ${a.status === "done" ? "line-through text-slate-500" : ""}">${a.task_description}</span>
          </div>
          <div class="flex items-center space-x-2 text-[11px]">
            <span class="px-2 py-0.5 rounded bg-slate-800 text-slate-300">${a.assignee}</span>
            <span class="px-2 py-0.5 rounded font-bold ${a.priority === "Urgent" ? "bg-rose-500/20 text-rose-400" : a.priority === "High" ? "bg-amber-500/20 text-amber-400" : "bg-blue-500/20 text-blue-400"}">${a.priority}</span>
          </div>
        </div>
      `
      )
      .join("");
  }

  // TAB 6: DOCUMENTATION & STORIES
  const docGapsList = document.getElementById("doc-gaps-list");
  if (docGapsList && docs.missing_documentation_gaps) {
    docGapsList.innerHTML = docs.missing_documentation_gaps
      .map(
        (g) => `
        <li class="flex items-start space-x-2">
          <i data-lucide="alert-circle" class="w-3.5 h-3.5 text-blue-400 mt-0.5 flex-shrink-0"></i>
          <span>${g}</span>
        </li>
      `
      )
      .join("");
  }

  const userStoriesContainer = document.getElementById("user-stories-container");
  if (userStoriesContainer && docs.user_stories) {
    userStoriesContainer.innerHTML = docs.user_stories
      .map(
        (us) => `
        <div class="p-5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-3">
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-2">
              <span class="px-2 py-0.5 rounded text-[11px] font-mono bg-indigo-500/20 text-indigo-300 font-bold border border-indigo-500/30">${us.id}</span>
              <h4 class="text-xs font-bold text-white">${us.title}</h4>
            </div>
            <div class="flex items-center space-x-2 text-[11px]">
              <span class="px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-mono">${us.epic_tag || "Feature"}</span>
              <span class="px-2 py-0.5 rounded font-bold bg-blue-500/20 text-blue-400">${us.estimated_story_points} pts</span>
              <span class="px-2 py-0.5 rounded font-bold bg-slate-800 text-slate-300">${us.priority}</span>
            </div>
          </div>
          <div class="p-3 rounded-lg bg-slate-950/70 border border-slate-800/80 text-xs space-y-1">
            <div><span class="text-slate-400 font-semibold">As a</span> <span class="text-white">${us.as_a}</span>,</div>
            <div><span class="text-slate-400 font-semibold">I want to</span> <span class="text-blue-300">${us.i_want_to}</span>,</div>
            <div><span class="text-slate-400 font-semibold">So that</span> <span class="text-emerald-300">${us.so_that}</span>.</div>
          </div>
          <div>
            <div class="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1.5">Acceptance Criteria (Gherkin):</div>
            <ul class="space-y-1 text-xs text-slate-300">
              ${(us.acceptance_criteria || []).map((ac) => `<li class="flex items-start space-x-1.5"><span class="text-blue-400">•</span><span>${ac}</span></li>`).join("")}
            </ul>
          </div>
        </div>
      `
      )
      .join("");
  }

  initIcons();
}

// ----------------- DOCUMENT MANAGEMENT & RAG -----------------
async function loadDocuments() {
  try {
    const res = await fetch("/api/ingest/documents");
    if (res.ok) {
      const docs = await res.json();
      renderDocumentTable(docs);
    }
  } catch (e) {
    console.error("Failed to load documents", e);
  }
}

function renderDocumentTable(docs) {
  const tbody = document.getElementById("document-table-body");
  if (!tbody) return;

  if (docs.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="5" class="p-6 text-center text-slate-500 text-xs">
          No project artifacts indexed yet. Click "Load Samples" or drop your files above.
        </td>
      </tr>
    `;
    return;
  }

  tbody.innerHTML = docs
    .map(
      (doc) => `
      <tr class="hover:bg-slate-800/30 transition">
        <td class="p-3 font-medium text-slate-200 flex items-center space-x-2">
          <i data-lucide="file" class="w-4 h-4 text-blue-400"></i>
          <span>${doc.file_name}</span>
        </td>
        <td class="p-3 font-mono uppercase text-slate-400">${doc.file_type}</td>
        <td class="p-3 font-semibold text-blue-400">${doc.chunks_count} chunks</td>
        <td class="p-3 text-slate-400">${doc.total_words.toLocaleString()} words</td>
        <td class="p-3">
          <button onclick="deleteDocument('${doc.document_id}')" class="text-rose-400 hover:text-rose-300 text-xs transition">
            Delete
          </button>
        </td>
      </tr>
    `
    )
    .join("");

  initIcons();
}

async function deleteDocument(docId) {
  if (!confirm("Are you sure you want to remove this document from the knowledge base?")) return;
  try {
    const res = await fetch(`/api/ingest/documents/${docId}`, { method: "DELETE" });
    if (res.ok) {
      showToast("Document deleted from vector index", "info");
      loadDocuments();
    }
  } catch (e) {
    showToast("Error deleting document", "error");
  }
}

// ----------------- UPLOAD DROPZONE -----------------
function initUploadDropzone() {
  const dropzone = document.getElementById("dropzone");
  const fileInput = document.getElementById("file-input");

  dropzone.addEventListener("click", () => fileInput.click());

  dropzone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropzone.classList.add("border-blue-500", "bg-blue-500/10");
  });

  dropzone.addEventListener("dragleave", () => {
    dropzone.classList.remove("border-blue-500", "bg-blue-500/10");
  });

  dropzone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropzone.classList.remove("border-blue-500", "bg-blue-500/10");
    if (e.dataTransfer.files.length > 0) {
      uploadFiles(e.dataTransfer.files);
    }
  });

  fileInput.addEventListener("change", () => {
    if (fileInput.files.length > 0) {
      uploadFiles(fileInput.files);
    }
  });
}

async function uploadFiles(files) {
  const formData = new FormData();
  for (let i = 0; i < files.length; i++) {
    formData.append("files", files[i]);
  }

  showToast(`Uploading and chunking ${files.length} document(s)...`, "info");

  try {
    const res = await fetch("/api/ingest/upload", {
      method: "POST",
      body: formData,
    });
    if (!res.ok) throw new Error("Upload failed");
    const results = await res.json();
    const successful = results.filter((r) => r.status === "success").length;
    showToast(`Successfully indexed ${successful} document(s) in RAG knowledge base!`, "success");
    loadDocuments();
  } catch (e) {
    showToast(e.message, "error");
  }
}

// ----------------- RAG SEARCH TEST BAR -----------------
async function testRagSearch() {
  const input = document.getElementById("rag-search-input");
  const q = input.value.trim();
  if (!q) return;

  const container = document.getElementById("rag-search-results");
  container.classList.remove("hidden");
  container.innerHTML = `<div class="text-xs text-slate-400 p-2">Searching vector index...</div>`;

  try {
    const res = await fetch("/api/rag/search", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: q, top_k: 4 }),
    });
    if (!res.ok) throw new Error("Search failed");
    const data = await res.json();

    if (data.results.length === 0) {
      container.innerHTML = `<div class="text-xs text-slate-400 p-2">No matching chunks found.</div>`;
      return;
    }

    container.innerHTML = data.results
      .map(
        (r) => `
        <div class="p-3 rounded-lg bg-slate-900 border border-slate-800 text-xs space-y-1">
          <div class="flex items-center justify-between text-slate-400">
            <span class="font-bold text-blue-400">${r.source_name}</span>
            <span class="font-mono text-[10px] bg-blue-500/20 text-blue-300 px-1.5 py-0.5 rounded">Relevance: ${(r.score * 100).toFixed(1)}%</span>
          </div>
          <p class="text-slate-300 font-mono text-[11px] leading-relaxed">${r.excerpt}</p>
        </div>
      `
      )
      .join("");
  } catch (e) {
    container.innerHTML = `<div class="text-xs text-rose-400 p-2">${e.message}</div>`;
  }
}

// ----------------- CONVERSATIONAL ASSISTANT -----------------
async function sendChatMessage(queryText) {
  const input = document.getElementById("chat-input");
  const query = queryText || input.value.trim();
  if (!query) return;

  input.value = "";
  const container = document.getElementById("chat-messages-container");

  // Append user bubble
  const userBubble = document.createElement("div");
  userBubble.className = "flex items-start justify-end space-x-3";
  userBubble.innerHTML = `
    <div class="bg-blue-600 rounded-2xl rounded-tr-sm p-4 text-xs text-white max-w-xl leading-relaxed shadow-md">
      ${query}
    </div>
    <div class="w-8 h-8 rounded-lg bg-slate-700 flex items-center justify-center text-white text-xs font-bold flex-shrink-0">
      You
    </div>
  `;
  container.appendChild(userBubble);
  container.scrollTop = container.scrollHeight;

  // Append thinking bubble
  const thinkingBubble = document.createElement("div");
  thinkingBubble.className = "flex items-start space-x-3";
  thinkingBubble.id = "thinking-bubble";
  thinkingBubble.innerHTML = `
    <div class="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-white text-xs font-bold flex-shrink-0">
      AI
    </div>
    <div class="bg-slate-800/80 border border-slate-700/80 rounded-2xl rounded-tl-sm p-4 text-xs text-slate-400 max-w-xl">
      <div class="flex items-center space-x-1.5">
        <span class="w-1.5 h-1.5 bg-blue-400 rounded-full animate-bounce"></span>
        <span class="w-1.5 h-1.5 bg-blue-400 rounded-full animate-bounce" style="animation-delay: 0.15s"></span>
        <span class="w-1.5 h-1.5 bg-blue-400 rounded-full animate-bounce" style="animation-delay: 0.3s"></span>
        <span class="ml-2">Retrieving grounded chunks & analyzing project artifacts...</span>
      </div>
    </div>
  `;
  container.appendChild(thinkingBubble);
  container.scrollTop = container.scrollHeight;

  try {
    const res = await fetch("/api/chat/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: query, top_k: 5 }),
    });

    thinkingBubble.remove();

    if (!res.ok) throw new Error("Failed to get assistant response");
    const data = await res.json();

    // Render markdown answer
    const parsedHtml = marked.parse(data.answer);

    // Citations pills
    let citationsHtml = "";
    if (data.citations && data.citations.length > 0) {
      citationsHtml = `
        <div class="mt-3 pt-3 border-t border-slate-700/60">
          <div class="text-[10px] uppercase font-semibold text-slate-400 tracking-wider mb-1.5">Grounded Sources & Citations:</div>
          <div class="flex flex-wrap gap-1.5">
            ${data.citations
              .map(
                (cit, idx) => `
              <button onclick="showCitationModal('${cit.document_name}', '${encodeURIComponent(cit.excerpt)}')" class="inline-flex items-center px-2 py-1 rounded bg-slate-900 hover:bg-slate-950 text-slate-300 border border-slate-700 text-[10px] font-mono transition">
                <i data-lucide="bookmark" class="w-3 h-3 mr-1 text-blue-400"></i>
                <span>${cit.document_name} (${(cit.score * 100).toFixed(0)}%)</span>
              </button>
            `
              )
              .join("")}
          </div>
        </div>
      `;
    }

    const aiBubble = document.createElement("div");
    aiBubble.className = "flex items-start space-x-3";
    aiBubble.innerHTML = `
      <div class="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-white text-xs font-bold flex-shrink-0">
        AI
      </div>
      <div class="bg-slate-800/80 border border-slate-700/80 rounded-2xl rounded-tl-sm p-4 text-xs text-slate-200 max-w-2xl leading-relaxed shadow-lg">
        <div class="prose prose-invert prose-xs max-w-none">${parsedHtml}</div>
        ${citationsHtml}
      </div>
    `;
    container.appendChild(aiBubble);
    container.scrollTop = container.scrollHeight;

    // Update suggested prompts
    if (data.suggested_followups && data.suggested_followups.length > 0) {
      const promptChipsContainer = document.getElementById("suggested-prompts-container");
      if (promptChipsContainer) {
        promptChipsContainer.innerHTML = data.suggested_followups
          .map(
            (p) => `
          <button class="prompt-chip px-3 py-1.5 rounded-full bg-slate-800/80 hover:bg-slate-700 text-slate-300 border border-slate-700 transition">
            ${p}
          </button>
        `
          )
          .join("");
        bindPromptChips();
      }
    }

    initIcons();
  } catch (e) {
    thinkingBubble.remove();
    showToast(e.message, "error");
  }
}

function showCitationModal(title, excerptEncoded) {
  const modal = document.getElementById("citation-modal");
  const modalTitle = document.getElementById("citation-modal-title");
  const modalContent = document.getElementById("citation-modal-content");
  modalTitle.innerHTML = `<i data-lucide="file-text" class="w-4 h-4 mr-1.5 text-blue-400"></i> Source Citation: ${title}`;
  modalContent.textContent = decodeURIComponent(excerptEncoded);
  modal.classList.remove("hidden");
  initIcons();
}

function bindPromptChips() {
  document.querySelectorAll(".prompt-chip").forEach((btn) => {
    btn.addEventListener("click", () => {
      sendChatMessage(btn.textContent.trim());
    });
  });
}

// ----------------- EVENT LISTENERS -----------------
function initEventListeners() {
  // Load Samples
  document.getElementById("btn-load-samples").addEventListener("click", async () => {
    try {
      showToast("Loading pre-configured project artifacts...", "info");
      const res = await fetch("/api/ingest/load-samples", { method: "POST" });
      if (res.ok) {
        showToast("5 sample project artifacts indexed in RAG knowledge base!", "success");
        await loadDocuments();
        await runMultiAgentPipeline();
      } else {
        const err = await res.json();
        showToast(err.detail || "Failed to load samples", "error");
      }
    } catch (e) {
      showToast("Error loading samples", "error");
    }
  });

  // Run Pipeline Button
  document.getElementById("btn-run-pipeline").addEventListener("click", () => {
    runMultiAgentPipeline();
  });

  // Clear Knowledge Base
  document.getElementById("btn-clear-kb").addEventListener("click", async () => {
    if (!confirm("Are you sure you want to clear all documents and vector indices?")) return;
    try {
      const res = await fetch("/api/ingest/clear", { method: "DELETE" });
      if (res.ok) {
        showToast("Knowledge base cleared.", "info");
        loadDocuments();
      }
    } catch (e) {
      showToast("Error clearing KB", "error");
    }
  });

  // RAG Search
  document.getElementById("btn-rag-search").addEventListener("click", testRagSearch);
  document.getElementById("rag-search-input").addEventListener("keypress", (e) => {
    if (e.key === "Enter") testRagSearch();
  });

  // Chat Form
  document.getElementById("chat-form").addEventListener("submit", (e) => {
    e.preventDefault();
    sendChatMessage();
  });

  document.getElementById("btn-clear-chat").addEventListener("click", () => {
    const container = document.getElementById("chat-messages-container");
    container.innerHTML = "";
  });

  bindPromptChips();

  // Settings Modal
  const settingsModal = document.getElementById("settings-modal");
  document.getElementById("btn-open-settings").addEventListener("click", () => {
    settingsModal.classList.remove("hidden");
  });
  document.getElementById("btn-close-settings").addEventListener("click", () => {
    settingsModal.classList.add("hidden");
  });
  document.getElementById("btn-cancel-settings").addEventListener("click", () => {
    settingsModal.classList.add("hidden");
  });

  document.getElementById("settings-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const gKey = document.getElementById("input-gemini-key").value.trim();
    const oKey = document.getElementById("input-openai-key").value.trim();

    try {
      const res = await fetch("/api/export/settings/keys", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ gemini_api_key: gKey, openai_api_key: oKey }),
      });
      if (res.ok) {
        const data = await res.json();
        showToast(`Settings saved. Active engine: ${data.active_provider}`, "success");
        settingsModal.classList.add("hidden");
        loadSystemStatus();
      }
    } catch (e) {
      showToast("Failed to save settings", "error");
    }
  });

  // Citation Modal Close
  document.getElementById("btn-close-citation").addEventListener("click", () => {
    document.getElementById("citation-modal").classList.add("hidden");
  });

  // Copy User Stories
  document.getElementById("btn-copy-stories").addEventListener("click", () => {
    if (!currentAnalysis || !currentAnalysis.documentation || !currentAnalysis.documentation.user_stories) {
      showToast("No user stories generated yet", "warning");
      return;
    }
    const storiesText = currentAnalysis.documentation.user_stories
      .map(
        (us) =>
          `### ${us.id}: ${us.title}\nAs a ${us.as_a}, I want to ${us.i_want_to}, so that ${us.so_that}.\nAcceptance Criteria:\n` +
          us.acceptance_criteria.map((c) => `- ${c}`).join("\n")
      )
      .join("\n\n");
    navigator.clipboard.writeText(storiesText).then(() => {
      showToast("Copied user stories to clipboard!", "success");
    });
  });
}
