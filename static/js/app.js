// Algorithm Descriptions & Status
const ALGO_DETAILS = {
  fcfs: `
    <div class="about-title">About FCFS Scheduling</div>
    <p class="about-desc">
      Processes are executed strictly in the order they arrive in the ready queue, following a First-In, First-Out (FIFO) queue policy.
    </p>
    <div class="about-badges">
      <span class="about-badge highlight">Non-Preemptive</span>
      <span class="about-badge">Criterion: Arrival Time (AT)</span>
      <span class="about-badge">Starvation: None</span>
    </div>
    <div class="about-subheading">Key Concepts</div>
    <ul class="about-list">
      <li><strong>Simplicity:</strong> Minimal scheduling overhead and straightforward FIFO implementation.</li>
      <li><strong>Convoy Effect:</strong> If a CPU-heavy process runs first, it delays subsequent short jobs, increasing average waiting times.</li>
      <li><strong>Deterministic:</strong> Execution order strictly mirrors arrival timestamps with zero preemption.</li>
    </ul>
    <div class="about-subheading">Formulas</div>
    <ul class="formula-list">
      <li><code>Completion Time (CT)</code> = Time when process finishes execution</li>
      <li><code>Turnaround Time (TAT)</code> = <strong>CT &minus; AT</strong></li>
      <li><code>Waiting Time (WT)</code> = <strong>TAT &minus; BT</strong></li>
      <li><code>Response Time (RT)</code> = <strong>First Start Time &minus; AT</strong></li>
    </ul>
  `,
  srtf: `
    <div class="about-title">About SRTF Scheduling</div>
    <p class="about-desc">
      Shortest Remaining Time First (SRTF) is the preemptive version of SJF. The process with the smallest remaining burst time is allocated the CPU next.
    </p>
    <div class="about-badges">
      <span class="about-badge highlight">Preemptive</span>
      <span class="about-badge">Criterion: Remaining Burst Time</span>
      <span class="about-badge">Starvation: Possible for long jobs</span>
    </div>
    <div class="about-subheading">Key Concepts</div>
    <ul class="about-list">
      <li><strong>Preemptive:</strong> A newly arriving process with a shorter remaining burst time will preempt the running process.</li>
      <li><strong>Optimal Waiting Time:</strong> Minimizes average waiting time across all processes.</li>
      <li><strong>Context Switches:</strong> Preemption can introduce frequent context switches and runtime overhead.</li>
    </ul>
    <div class="about-subheading">Formulas</div>
    <ul class="formula-list">
      <li><code>Completion Time (CT)</code> = Time when process finishes execution</li>
      <li><code>Turnaround Time (TAT)</code> = <strong>CT &minus; AT</strong></li>
      <li><code>Waiting Time (WT)</code> = <strong>TAT &minus; BT</strong></li>
      <li><code>Response Time (RT)</code> = <strong>First Start Time &minus; AT</strong></li>
    </ul>
  `,
  unsupported: (algoName) => `
    <div class="unsupported-box">
      <div class="unsupported-badge">Notice</div>
      <h3 class="unsupported-heading">Can't implement this algorithm at this moment</h3>
      <p class="unsupported-text">
        <strong>${algoName}</strong> is not available yet. Currently, only <strong>First Come First Serve (FCFS)</strong> is supported.
      </p>
    </div>
  `,
};

const ALGO_LABELS = {
  fcfs: "First Come First Serve (FCFS)",
  sjf: "Shortest Job First (SJF)",
  srtf: "Shortest Remaining Time First (SRTF)",
  rr: "Round Robin (RR)",
};

// Process block color palette (warm butter-yellow & celadon-green alternating colors)
const BLOCK_COLORS = [
  "#F3DE8A",
  "#8FBC94",
  "#F0C56B",
  "#B7D9BC",
  "#E8B44F",
  "#6FA37A",
];

const PIXELS_PER_MS = 32;

let selectedAlgo = "fcfs";
let rowCount = 0;
let lastSimData = null;
let ganttMode = "full"; // "full" or "step"
let stepIndex = 0;

// ---------------- Algorithm Selection ----------------

const algoSelect = document.getElementById("algo-select");
const aboutBox = document.getElementById("about-box");
const algoHeaderLabel = document.getElementById("results-algo-label");

function updateAlgoView() {
  selectedAlgo = algoSelect.value;
  if (algoHeaderLabel) {
    algoHeaderLabel.textContent = ALGO_LABELS[selectedAlgo] || selectedAlgo;
  }

  const errorBox = document.getElementById("run-error");
  errorBox.textContent = "";

  if (selectedAlgo === "fcfs") {
    aboutBox.innerHTML = ALGO_DETAILS.fcfs;
  } else if (selectedAlgo === "srtf") {
    aboutBox.innerHTML = ALGO_DETAILS.srtf;
  } else {
    aboutBox.innerHTML = ALGO_DETAILS.unsupported(ALGO_LABELS[selectedAlgo] || selectedAlgo);
    errorBox.textContent = "Can't implement this algorithm at this moment";
    resetResults();
  }
}

algoSelect.addEventListener("change", updateAlgoView);

// ---------------- Process Table Management ----------------

function updateRunButtonState() {
  const rows = document.querySelectorAll("#process-rows tr").length;
  document
    .getElementById("run-simulation")
    .classList.toggle("run-btn-dark", rows >= 3);
}

function addRow(pid = null, at = 0, bt = 1) {
  rowCount += 1;
  const pidValue = pid || `P${rowCount}`;
  const tr = document.createElement("tr");
  tr.innerHTML = `
    <td><input type="text" class="pid-input" value="${pidValue}"></td>
    <td><input type="number" class="at-input" value="${at}" min="0"></td>
    <td><input type="number" class="bt-input" value="${bt}" min="1"></td>
    <td class="action-col">
      <button type="button" class="row-remove" title="Remove process" aria-label="Remove process">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="3 6 5 6 21 6"></polyline>
          <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
        </svg>
      </button>
    </td>
  `;
  document.getElementById("process-rows").appendChild(tr);
  updateRunButtonState();
  resetResults();
}

// Remove row button click
document.getElementById("process-rows").addEventListener("click", (e) => {
  const btn = e.target.closest(".row-remove");
  if (btn) {
    const tr = btn.closest("tr");
    if (tr) {
      tr.remove();
      updateRunButtonState();
      resetResults();
    }
  }
});

// Add new row button
document.getElementById("add-row").addEventListener("click", () => addRow());

// Clear table button
document.getElementById("clear-table").addEventListener("click", () => {
  document.getElementById("process-rows").innerHTML = "";
  rowCount = 0;
  updateRunButtonState();
  resetResults();
});

// Clear results whenever user edits inputs
function resetResults() {
  const resultsSection = document.getElementById("results-section");
  if (resultsSection) resultsSection.style.display = "none";

  const resultsTbody = document.getElementById("results-process-rows");
  if (resultsTbody) resultsTbody.innerHTML = "";

  const summaryIds = ["sum-tat", "sum-wt", "sum-rt", "sum-total-time"];
  summaryIds.forEach((id) => {
    const el = document.getElementById(id);
    if (el) el.textContent = "\u2014";
  });

  lastSimData = null;
}

document.getElementById("process-rows").addEventListener("input", resetResults);

// ---------------- Gantt Chart Timeline Rendering ----------------

function buildPidColorMap(gantt) {
  const pidColor = {};
  let colorIdx = 0;
  gantt.forEach((seg) => {
    if (!(seg.pid in pidColor)) {
      pidColor[seg.pid] = BLOCK_COLORS[colorIdx % BLOCK_COLORS.length];
      colorIdx += 1;
    }
  });
  return pidColor;
}

function buildGanttHtml(segments) {
  let ganttHtml = "";
  let rulerHtml = "";
  const pidColor = buildPidColorMap(segments);

  segments.forEach((seg, i) => {
    const duration = seg.end - seg.start;
    const width = Math.max(duration * PIXELS_PER_MS, PIXELS_PER_MS);
    ganttHtml += `<div class="gantt-block" style="min-width:${width}px; background:${pidColor[seg.pid]}">${seg.pid}</div>`;
    rulerHtml += `<div class="ruler-tick" style="min-width:${width}px;">${seg.start}</div>`;
    if (i === segments.length - 1) {
      rulerHtml += `<div class="ruler-tick" style="min-width:0;">${seg.end}</div>`;
    }
  });

  return `
    <div class="gantt-wrap">
      <div class="gantt-ruler">${rulerHtml}</div>
      <div class="gantt-chart">${ganttHtml}</div>
    </div>
  `;
}

function renderGanttContainer() {
  if (!lastSimData) return;
  const container = document.getElementById("gantt-container");
  const gantt = lastSimData.gantt;

  document
    .getElementById("view-full-btn")
    .classList.toggle("active", ganttMode === "full");
  document
    .getElementById("view-step-btn")
    .classList.toggle("active", ganttMode === "step");

  if (ganttMode === "full") {
    container.innerHTML = buildGanttHtml(gantt);
    return;
  }

  // Step-by-step mode: show timeline up to current step
  const visible = gantt.slice(0, stepIndex + 1);
  const seg = gantt[stepIndex];
  container.innerHTML = `
    ${buildGanttHtml(visible)}
    <div class="current-seg">Executing: <strong>${seg.pid}</strong> (${seg.start}ms &rarr; ${seg.end}ms)</div>
    <div class="step-controls">
      <button type="button" class="step-btn" id="step-prev" ${stepIndex === 0 ? "disabled" : ""}>&larr; Prev</button>
      <button type="button" class="step-btn" id="step-next" ${stepIndex === gantt.length - 1 ? "disabled" : ""}>Next &rarr;</button>
      <span class="step-info">Step ${stepIndex + 1} of ${gantt.length}</span>
    </div>
  `;

  // Ensure current step is scrolled into view
  const wrap = container.querySelector(".gantt-wrap");
  if (wrap) wrap.scrollLeft = wrap.scrollWidth;

  const prevBtn = document.getElementById("step-prev");
  const nextBtn = document.getElementById("step-next");
  if (prevBtn) {
    prevBtn.addEventListener("click", () => {
      stepIndex = Math.max(stepIndex - 1, 0);
      renderGanttContainer();
    });
  }
  if (nextBtn) {
    nextBtn.addEventListener("click", () => {
      stepIndex = Math.min(stepIndex + 1, gantt.length - 1);
      renderGanttContainer();
    });
  }
}

// Gantt view mode toggles
document.getElementById("view-full-btn").addEventListener("click", () => {
  ganttMode = "full";
  renderGanttContainer();
});

document.getElementById("view-step-btn").addEventListener("click", () => {
  ganttMode = "step";
  stepIndex = 0;
  renderGanttContainer();
});

// ---------------- Results Display ----------------

function renderResults(data) {
  // 1. Gantt chart
  renderGanttContainer();

  // 2. Populate Process Calculation Table
  const resultsTbody = document.getElementById("results-process-rows");
  if (resultsTbody) {
    resultsTbody.innerHTML = "";
    data.table.forEach((r) => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td><strong>${r.pid}</strong></td>
        <td>${r.at}</td>
        <td>${r.bt}</td>
        <td>${r.ct}</td>
        <td>${r.tat}</td>
        <td>${r.wt}</td>
        <td>${r.rt}</td>
      `;
      resultsTbody.appendChild(tr);
    });
  }

  // 3. Summary Performance Metrics
  const sumWt = document.getElementById("sum-wt");
  if (sumWt) sumWt.textContent = `${data.averages.wt} ms`;

  const sumTat = document.getElementById("sum-tat");
  if (sumTat) sumTat.textContent = `${data.averages.tat} ms`;

  const sumRt = document.getElementById("sum-rt");
  if (sumRt) sumRt.textContent = `${data.averages.rt} ms`;

  const sumTotalTime = document.getElementById("sum-total-time");
  if (sumTotalTime) sumTotalTime.textContent = `${data.total_time} ms`;

  // 4. Reveal Results section
  const resultsSection = document.getElementById("results-section");
  if (resultsSection) resultsSection.style.display = "block";
}

// ---------------- Run Simulation Trigger ----------------

function collectProcesses() {
  const rows = document.querySelectorAll("#process-rows tr");
  const processes = [];
  rows.forEach((row) => {
    const pid = row.querySelector(".pid-input").value.trim();
    const at = parseInt(row.querySelector(".at-input").value, 10);
    const bt = parseInt(row.querySelector(".bt-input").value, 10);
    if (pid && !isNaN(at) && !isNaN(bt)) {
      processes.push({ pid, at, bt });
    }
  });
  return processes;
}

document
  .getElementById("run-simulation")
  .addEventListener("click", async () => {
    const errorBox = document.getElementById("run-error");
    errorBox.textContent = "";

    if (selectedAlgo !== "fcfs" && selectedAlgo !== "srtf") {
      errorBox.textContent = "Can't implement this algorithm at this moment still.";
      resetResults();
      return;
    }

    const processes = collectProcesses();
    if (processes.length === 0) {
      errorBox.textContent = "Please add at least one process to simulate.";
      return;
    }

    try {
      const res = await fetch("/api/simulate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ algorithm: selectedAlgo, processes }),
      });
      const data = await res.json();

      if (data.error) {
        errorBox.textContent = data.error;
        return;
      }

      lastSimData = data;
      ganttMode = "full";
      stepIndex = 0;
      renderResults(data);
    } catch (err) {
      errorBox.textContent = "Request failed: " + err.message;
    }
  });

// Initialize UI with default state
updateAlgoView();
addRow("P1", 0, 5);
addRow("P2", 1, 4);
addRow("P3", 2, 2);
addRow("P4", 4, 1);
