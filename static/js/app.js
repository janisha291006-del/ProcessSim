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
  sjf: `
    <div class="about-title">About SJF Scheduling</div>
    <p class="about-desc">
      Shortest Job First (SJF) is a non-preemptive scheduling policy that executes the waiting process with the smallest CPU burst time next.
    </p>
    <div class="about-badges">
      <span class="about-badge highlight">Non-Preemptive</span>
      <span class="about-badge">Criterion: Burst Time (BT)</span>
      <span class="about-badge">Starvation: Possible for long jobs</span>
    </div>
    <div class="about-subheading">Key Concepts</div>
    <ul class="about-list">
      <li><strong>Non-Preemptive:</strong> Once a process is allocated the CPU, it runs uninterrupted until completion.</li>
      <li><strong>Optimal Waiting Time:</strong> Among non-preemptive algorithms, SJF gives the minimum average waiting time.</li>
      <li><strong>Convoy Reduction:</strong> Reduces the convoy effect seen in FCFS by scheduling shorter tasks earlier.</li>
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
  rr: `
    <div class="about-title">About Round Robin (RR) Scheduling</div>
    <p class="about-desc">
      Round Robin is a preemptive scheduling algorithm where every ready process is allocated a fixed slice of CPU time (Time Quantum) in cyclic order.
    </p>
    <div class="about-badges">
      <span class="about-badge highlight">Preemptive</span>
      <span class="about-badge">Criterion: Time Quantum (Q)</span>
      <span class="about-badge">Starvation: None (Fair Share)</span>
    </div>
    <div class="about-subheading">Key Concepts</div>
    <ul class="about-list">
      <li><strong>Time Slicing:</strong> If a process does not finish within its quantum, it is preempted to the back of the ready queue.</li>
      <li><strong>Responsiveness:</strong> Excellent for interactive time-sharing systems; all processes receive regular CPU time.</li>
      <li><strong>Quantum Choice:</strong> If too small, context switching overhead dominates; if too large, it degrades into FCFS.</li>
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
        <strong>${algoName}</strong> is not available yet.
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

let selectedAlgo = "fcfs";
let rowCount = 0;
let lastSimData = null;
// The Running Queue and the Ready Queue each have their own view:
// mode "full" = all steps at once, "step" = one step at a time
const queueViews = {
  running: { mode: "full", index: 0 },
  ready: { mode: "full", index: 0 },
};

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

  // Show quantum input only for Round Robin
  const quantumGroup = document.getElementById("quantum-group");
  if (quantumGroup) {
    quantumGroup.style.display = selectedAlgo === "rr" ? "block" : "none";
  }

  if (selectedAlgo === "fcfs") {
    aboutBox.innerHTML = ALGO_DETAILS.fcfs;
  } else if (selectedAlgo === "sjf") {
    aboutBox.innerHTML = ALGO_DETAILS.sjf;
  } else if (selectedAlgo === "srtf") {
    aboutBox.innerHTML = ALGO_DETAILS.srtf;
  } else if (selectedAlgo === "rr") {
    aboutBox.innerHTML = ALGO_DETAILS.rr;
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

// Soft warnings (do NOT stop the simulation)
function showWarnings(warnings) {
  const box = document.getElementById("run-warning");
  if (!warnings || warnings.length === 0) {
    box.style.display = "none";
    box.textContent = "";
    return;
  }
  box.innerHTML = "&#9888; " + warnings.join("<br>&#9888; ");
  box.style.display = "block";
}

// New rows start at the latest arrival time so the order rule is already satisfied
function latestArrivalTime() {
  let latest = 0;
  document.querySelectorAll("#process-rows .at-input").forEach((el) => {
    const v = parseInt(el.value, 10);
    if (!isNaN(v) && v > latest) latest = v;
  });
  return latest;
}

function addRow(pid = null, at = null, bt = 1) {
  if (at === null) at = latestArrivalTime();
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

  showWarnings([]);
  lastSimData = null;
}

document.getElementById("process-rows").addEventListener("input", () => {
  resetResults();
});

// ---------------- Ready Queue & Running Process View ----------------

// Warm palette: every process keeps its own color everywhere
const BLOCK_COLORS = ["#F3DE8A", "#8FBC94", "#F0C56B", "#B7D9BC", "#E8B44F", "#6FA37A"];

// Every process keeps the same color in both rows (colors are given in order of first appearance)
function buildPidColorMap(boxes) {
  const pidColor = {};
  let colorIdx = 0;
  boxes.forEach((box) => {
    if (box.pid && !(box.pid in pidColor)) {
      pidColor[box.pid] = BLOCK_COLORS[colorIdx % BLOCK_COLORS.length];
      colorIdx += 1;
    }
  });
  return pidColor;
}

// Explains how the boxes are cut for the chosen algorithm
function modeNoteHtml() {
  let text = "";
  if (selectedAlgo === "fcfs" || selectedAlgo === "sjf") {
    text = "Non-preemptive: no time quantum. Each process runs its full burst in one box. Only the Running Queue (Gantt chart) is drawn.";
  } else if (selectedAlgo === "srtf") {
    text = "Preemptive: the shortest remaining job is checked every 1 ms until the last process has arrived. After that, each process runs the rest of its burst in one box.";
  } else if (selectedAlgo === "rr") {
    const q = document.getElementById("quantum-input").value;
    text = `Preemptive: time quantum = ${q} ms. A process runs at most ${q} ms, then goes to the back of the queue. The Running Queue joins back-to-back boxes of the same process.`;
  }
  const legend = "Time: when the box starts (the last number is the end). Bal. Time: burst time left after the box. A red 0 means the process finishes there.";
  return `<div class="mode-note">${text}<br>${legend}</div>`;
}

// One column of the strip: [ box with name ], the Time under it, then Bal. Time under it
function queueColHtml({ name, color, time, endTime, bal, classes }) {
  const bg = color ? ` style="background:${color}"` : "";
  const end = endTime !== null && endTime !== undefined ? `<span class="q-time-end">${endTime}</span>` : "";
  return `
    <div class="q-col${classes}">
      <div class="q-box"${bg}>${name}</div>
      <div class="q-time">${time}${end}</div>
      <div class="q-bal${bal === 0 ? " q-bal-zero" : ""}">${bal}</div>
    </div>`;
}

// ONE row in the lecture-notes format:
//   Ready Queue :  [ P1 | P2 | P3 | ... ]
//   Time:          0    2    4   ...  12
//   Bal. Time:     3    2    0   ...
function buildTimelineHtml(boxes, colors, kind, currentIndex = -1) {
  let cols = "";
  boxes.forEach((box, i) => {
    const idle = box.pid === null;
    const classes =
      (i === currentIndex ? " current" : "") + (idle ? " idle" : "") + (box.done ? " done" : "");
    cols += queueColHtml({
      name: idle ? "Idle" : box.pid,
      color: idle ? "" : colors[box.pid],
      time: box.start,
      endTime: i === boxes.length - 1 ? box.end : null, // the last box also shows its end time
      bal: idle ? "&mdash;" : box.bal,
      classes,
    });
  });

  return `
    <div class="q-wrap">
      <div class="q-labels">
        <div class="q-label q-label-box">${kind === "running" ? "Running" : "Ready"}</div>
        <div class="q-label">Time:</div>
        <div class="q-label">Bal. Time:</div>
      </div>
      <div class="q-scroll" id="tl-scroll-${kind}">
        <div class="q-strip">${cols}</div>
      </div>
    </div>`;
}

// The line under a step-by-step row explaining the box that was just added
function stepCaptionHtml(box, index) {
  const text = box.pid
    ? `<strong>${box.pid}</strong> runs ${box.start} &rarr; ${box.end} ms, ${box.bal} ms left`
    : `CPU is idle (${box.start} &rarr; ${box.end} ms)`;
  return `<div class="current-seg">Step ${index + 1}: ${text}${box.note ? ` &middot; ${box.note}` : ""}</div>`;
}

function renderQueuePanel(kind) {
  const view = queueViews[kind];
  const boxes = lastSimData.queues[kind];
  const container = document.getElementById(`${kind}-container`);
  const colors = buildPidColorMap(lastSimData.queues.ready.length ? lastSimData.queues.ready : lastSimData.queues.running);

  document.getElementById(`${kind}-full-btn`).classList.toggle("active", view.mode === "full");
  document.getElementById(`${kind}-step-btn`).classList.toggle("active", view.mode === "step");

  // All at once: the whole row in one go
  if (view.mode === "full") {
    container.innerHTML = buildTimelineHtml(boxes, colors, kind);
    return;
  }

  // Step by step: the row grows one box at a time
  const i = view.index;
  container.innerHTML = `
    ${buildTimelineHtml(boxes.slice(0, i + 1), colors, kind, i)}
    ${stepCaptionHtml(boxes[i], i)}
    <div class="step-controls">
      <button type="button" class="step-btn" id="${kind}-prev" ${i === 0 ? "disabled" : ""}>&larr; Prev</button>
      <button type="button" class="step-btn" id="${kind}-next" ${i === boxes.length - 1 ? "disabled" : ""}>Next &rarr;</button>
      <span class="step-info">Step ${i + 1} of ${boxes.length}</span>
    </div>`;

  const scroller = document.getElementById(`tl-scroll-${kind}`);
  if (scroller) scroller.scrollLeft = scroller.scrollWidth; // keep the newest box visible

  document.getElementById(`${kind}-prev`).addEventListener("click", () => {
    view.index = Math.max(view.index - 1, 0);
    renderQueuePanel(kind);
  });
  document.getElementById(`${kind}-next`).addEventListener("click", () => {
    view.index = Math.min(view.index + 1, boxes.length - 1);
    renderQueuePanel(kind);
  });
}

function renderQueueView() {
  if (!lastSimData) return;
  document.getElementById("mode-note").innerHTML = modeNoteHtml();

  // FCFS and SJF have only the Running Queue (Gantt chart) in the lecture notes
  const showReady = lastSimData.queues.show_ready;
  document.getElementById("ready-title-row").style.display = showReady ? "flex" : "none";
  document.getElementById("ready-container").style.display = showReady ? "block" : "none";

  renderQueuePanel("running");
  if (showReady) renderQueuePanel("ready");
}

// Each row has its own All at Once / Step-by-Step toggle
["running", "ready"].forEach((kind) => {
  document.getElementById(`${kind}-full-btn`).addEventListener("click", () => {
    queueViews[kind].mode = "full";
    if (lastSimData) renderQueuePanel(kind);
  });
  document.getElementById(`${kind}-step-btn`).addEventListener("click", () => {
    queueViews[kind].mode = "step";
    queueViews[kind].index = 0;
    if (lastSimData) renderQueuePanel(kind);
  });
});

// ---------------- Results Display ----------------

function renderResults(data) {
  // 1. Ready queue & running process
  renderQueueView();

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

// Sends the text exactly as typed, so the server can reject values like 2.5 instead of rounding them
function collectProcesses() {
  const rows = document.querySelectorAll("#process-rows tr");
  const processes = [];
  rows.forEach((row) => {
    processes.push({
      pid: row.querySelector(".pid-input").value.trim(),
      at: row.querySelector(".at-input").value.trim(),
      bt: row.querySelector(".bt-input").value.trim(),
    });
  });
  return processes;
}

document
  .getElementById("run-simulation")
  .addEventListener("click", async () => {
    const errorBox = document.getElementById("run-error");
    errorBox.textContent = "";

    if (selectedAlgo !== "fcfs" && selectedAlgo !== "srtf" && selectedAlgo !== "sjf" && selectedAlgo !== "rr") {
      errorBox.textContent = "That algorithm isn't available yet. Pick one from the list.";
      resetResults();
      return;
    }

    const processes = collectProcesses();
    if (processes.length === 0) {
      errorBox.textContent = "Add at least one process to run the simulation.";
      return;
    }

    const payload = { algorithm: selectedAlgo, processes };
    if (selectedAlgo === "rr") {
      const qInput = document.getElementById("quantum-input");
      payload.quantum = qInput ? qInput.value.trim() : "2"; // the server checks it
    }

    try {
      const res = await fetch("/api/simulate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await res.json();

      if (data.error) {
        errorBox.textContent = data.error;
        return;
      }

      lastSimData = data;
      queueViews.running = { mode: "full", index: 0 };
      queueViews.ready = { mode: "full", index: 0 };
      renderResults(data);
      showWarnings(data.warnings); // warning only - the simulation has already run
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
