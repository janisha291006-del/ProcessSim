const ALGO_ABOUT = {
  fcfs: `
    <p class="about-desc">Processes are executed in strict sequential order of their arrival into the ready queue, operating under a First-In, First-Out (FIFO) queue policy.</p>
    <div class="about-badges">
      <span class="about-badge highlight">Non-Preemptive</span>
      <span class="about-badge">Criterion: Arrival Time (AT)</span>
      <span class="about-badge">Starvation: None</span>
    </div>
    <div class="about-subheading">Key Characteristics</div>
    <ul class="about-list">
      <li><strong>Simplicity:</strong> Minimal scheduling overhead and straightforward FIFO implementation.</li>
      <li><strong>Convoy Effect:</strong> A CPU-heavy process running first delays all subsequent shorter jobs, sharply inflating average wait times.</li>
      <li><strong>Deterministic:</strong> Execution order strictly mirrors arrival timestamps with zero preemption interruptions.</li>
    </ul>
  `,
  sjf: `
    <p class="about-desc">Selects the available arrived process with the smallest CPU burst time. Once execution starts, the process runs uninterrupted until complete.</p>
    <div class="about-badges">
      <span class="about-badge highlight">Non-Preemptive</span>
      <span class="about-badge">Criterion: Burst Time (BT)</span>
      <span class="about-badge">Starvation: Possible for long jobs</span>
    </div>
    <div class="about-subheading">Key Characteristics</div>
    <ul class="about-list">
      <li><strong>Optimal Waiting Time:</strong> Mathematically optimal for minimizing average waiting time among all non-preemptive algorithms.</li>
      <li><strong>Starvation Risk:</strong> Long-running processes may wait indefinitely if shorter processes continuously arrive in the ready queue.</li>
      <li><strong>Estimation Required:</strong> Real-world implementations require predicting CPU burst times in advance.</li>
    </ul>
  `,
  srtf: `
    <p class="about-desc">The preemptive counterpart of SJF. Whenever a newly arrived process requires less remaining CPU time than the currently running job, the CPU immediately preempts execution.</p>
    <div class="about-badges">
      <span class="about-badge highlight">Preemptive</span>
      <span class="about-badge">Criterion: Remaining Time</span>
      <span class="about-badge">Starvation: High risk for long jobs</span>
    </div>
    <div class="about-subheading">Key Characteristics</div>
    <ul class="about-list">
      <li><strong>Peak Responsiveness:</strong> Short tasks complete almost immediately without waiting behind large CPU-bound processes.</li>
      <li><strong>Theoretical Best WT:</strong> Delivers the lowest overall average waiting time across all scheduling strategies.</li>
      <li><strong>Preemption Overhead:</strong> Frequent context switches add CPU cycles and require continuous tracking of remaining bursts.</li>
    </ul>
  `,
  rr: `
    <p class="about-desc">Tailored for time-sharing operating systems. Every ready process is allocated a fixed slice of execution time (Time Quantum) before being preempted to the back of the queue.</p>
    <div class="about-badges">
      <span class="about-badge highlight">Preemptive</span>
      <span class="about-badge">Criterion: Time Quantum (Q)</span>
      <span class="about-badge">Starvation: None (Fair Share)</span>
    </div>
    <div class="about-subheading">Key Characteristics</div>
    <ul class="about-list">
      <li><strong>High Responsiveness:</strong> Low initial response time (RT); every process quickly gets a first turn on the CPU.</li>
      <li><strong>Quantum Sensitivity:</strong> A very large quantum degrades into FCFS, whereas an excessively small quantum causes heavy switching overhead.</li>
      <li><strong>Guaranteed Fairness:</strong> Starvation-free by design, ensuring equitable CPU distribution across all processes.</li>
    </ul>
  `,
};

// Butter-yellow / celadon-green family, alternating so adjacent blocks stay distinguishable
const BLOCK_COLORS = [
  "#F3DE8A",
  "#8FBC94",
  "#F0C56B",
  "#B7D9BC",
  "#E8B44F",
  "#6FA37A",
];
const PX_PER_MS = 32;

let selectedAlgo = "fcfs";
let rowCount = 0;
let compareChart = null;

// Gantt view state (kept outside renderResults so toggle clicks don't need a fresh simulation)
let lastSimData = null;
let ganttMode = "full"; // "full" or "step"
let stepIndex = 0;

// ---------------- Tabs ----------------
document.querySelectorAll(".tab-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    document
      .querySelectorAll(".tab-btn")
      .forEach((b) => b.classList.remove("active"));
      document
      .querySelectorAll(".screen")
      .forEach((s) => s.classList.remove("active"));
    btn.classList.add("active");
    document.getElementById(btn.dataset.screen).classList.add("active");
  });
});

// ---------------- Algorithm selection (dropdown) ----------------
const algoSelect = document.getElementById("algo-select");
algoSelect.addEventListener("change", () => {
  selectedAlgo = algoSelect.value;
  document.getElementById("about-text").innerHTML = ALGO_ABOUT[selectedAlgo];
  document.getElementById("quantum-group").style.display =
    selectedAlgo === "rr" ? "flex" : "none";
});

// ---------------- Process table ----------------
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

document.getElementById("add-row").addEventListener("click", () => addRow());

document.getElementById("clear-table").addEventListener("click", () => {
  document.getElementById("process-rows").innerHTML = "";
  rowCount = 0;
  updateRunButtonState();
  resetResults();
});

// seed with 4 default processes (this already puts the run button in its "dark" state, since 4 >= 3)
addRow("P1", 0, 5);
addRow("P2", 1, 4);
addRow("P3", 2, 2);
addRow("P4", 4, 1);

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

// ---------------- Results (filled into the same screen) ----------------
// Clears old results. Called whenever the user edits the process table,
// so old results never sit next to new inputs.
function resetResults() {
  const resultsSection = document.getElementById("results-section");
  if (resultsSection) resultsSection.style.display = "none";

  const resultsTbody = document.getElementById("results-process-rows");
  if (resultsTbody) resultsTbody.innerHTML = "";

  const summaryIds = ["sum-tat", "sum-wt", "sum-rt", "sum-cs"];
  for (let i = 0; i < summaryIds.length; i++) {
    const el = document.getElementById(summaryIds[i]);
    if (el) el.textContent = "\u2014";
  }

  const algoLabel = document.getElementById("results-algo-label");
  if (algoLabel) algoLabel.textContent = "";
  lastSimData = null;
}

// any typing inside the table clears the old results
document.getElementById("process-rows").addEventListener("input", resetResults);

// Full Timeline / Step-by-Step buttons (set up once)
document.getElementById("view-full-btn").addEventListener("click", () => {
  ganttMode = "full";
  renderGanttContainer();
});
document.getElementById("view-step-btn").addEventListener("click", () => {
  ganttMode = "step";
  stepIndex = 0;
  renderGanttContainer();
});

// ---------------- Run simulation ----------------
document
  .getElementById("run-simulation")
  .addEventListener("click", async () => {
    const processes = collectProcesses();
    const quantum = parseInt(document.getElementById("quantum").value, 10) || 2;
    const errorBox = document.getElementById("run-error");
    errorBox.textContent = "";

    if (processes.length === 0) {
      errorBox.textContent = "Add at least one process first.";
      return;
    }

    try {
      const res = await fetch("/api/simulate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ algorithm: selectedAlgo, processes, quantum }),
      });
      const data = await res.json();

      if (data.error) {
        errorBox.textContent = data.error;
        return;
      }
      data.quantum_used = document.getElementById("quantum").value;
      lastSimData = data;
      ganttMode = "full";
      stepIndex = 0;
      renderResults(data);
    } catch (err) {
      errorBox.textContent = "Request failed: " + err;
    }
  });

function renderResults(data) {
  const algoLabel = document.getElementById("results-algo-label");
  if (algoLabel) algoLabel.textContent = data.algorithm_label;

  // 1. Gantt chart title & rendering
  let title = "Gantt Chart (" + data.algorithm_label;
  if (data.algorithm === "rr") {
    title = title + ", Quantum=" + data.quantum_used;
  }
  const ganttTitle = document.getElementById("gantt-title");
  if (ganttTitle) ganttTitle.textContent = title + ")";
  renderGanttContainer();

  // 2. Populate separate Process Results Table
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

  // 3. Summary metrics cards
  const sumTat = document.getElementById("sum-tat");
  if (sumTat) sumTat.textContent = data.averages.tat + " ms";
  const sumWt = document.getElementById("sum-wt");
  if (sumWt) sumWt.textContent = data.averages.wt + " ms";
  const sumRt = document.getElementById("sum-rt");
  if (sumRt) sumRt.textContent = data.averages.rt + " ms";
  const sumCs = document.getElementById("sum-cs");
  if (sumCs) sumCs.textContent = data.context_switches;

  // 4. Reveal entire results section
  const resultsSection = document.getElementById("results-section");
  if (resultsSection) resultsSection.style.display = "block";
}

// assign a stable color per PID from a gantt array
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

// builds the ruler + colored block row for a given slice of gantt segments
function buildGanttHtml(segments) {
  let ganttHtml = "";
  let rulerHtml = "";
  const pidColor = buildPidColorMap(segments);
  segments.forEach((seg, i) => {
    const width = Math.max((seg.end - seg.start) * PX_PER_MS, PX_PER_MS);
    ganttHtml += `<div class="gantt-block" style="min-width:${width}px; background:${pidColor[seg.pid]}">${seg.pid}</div>`;
    rulerHtml += `<div class="ruler-tick" style="min-width:${width}px;">${seg.start}</div>`;
    if (i === segments.length - 1) {
      rulerHtml += `<div class="ruler-tick" style="min-width:0;">${seg.end}</div>`;
    }
  });
  return `<div class="gantt-wrap">
    <div class="gantt-ruler">${rulerHtml}</div>
    <div class="gantt-chart">${ganttHtml}</div>
  </div>`;
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

  // step-by-step: reveal one Gantt segment at a time
  const visible = gantt.slice(0, stepIndex + 1);
  const seg = gantt[stepIndex];
  container.innerHTML = `
    ${buildGanttHtml(visible)}
    <div class="current-seg">Now scheduling: ${seg.pid} (${seg.start}ms &rarr; ${seg.end}ms)</div>
    <div class="step-controls">
      <button type="button" class="step-btn" id="step-prev" ${stepIndex === 0 ? "disabled" : ""}>&larr; Prev</button>
      <button type="button" class="step-btn" id="step-next" ${stepIndex === gantt.length - 1 ? "disabled" : ""}>Next &rarr;</button>
      <span class="step-info">Step ${stepIndex + 1} of ${gantt.length}</span>
    </div>
  `;

  // keep the newest block in view
  const wrap = container.querySelector(".gantt-wrap");
  wrap.scrollLeft = wrap.scrollWidth;

  const prevBtn = document.getElementById("step-prev");
  const nextBtn = document.getElementById("step-next");
  if (prevBtn)
    prevBtn.addEventListener("click", () => {
      stepIndex = Math.max(stepIndex - 1, 0);
      renderGanttContainer();
    });
  if (nextBtn)
    nextBtn.addEventListener("click", () => {
      stepIndex = Math.min(stepIndex + 1, gantt.length - 1);
      renderGanttContainer();
    });
}

// ---------------- Run comparison (Screen 2) ----------------
document.getElementById("run-compare").addEventListener("click", async () => {
  const processes = collectProcesses();
  const quantum = parseInt(document.getElementById("quantum").value, 10) || 2;
  const contentBox = document.getElementById("compare-content");

  if (processes.length === 0) {
    alert("Add at least one process on the Dashboard screen first.");
    return;
  }

  try {
    const res = await fetch("/api/compare", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ processes, quantum }),
    });
    const data = await res.json();
    if (data.error) {
      alert(data.error);
      return;
    }
    renderCompare(data.results);
    contentBox.style.display = "block";
    loadInsights(data.results, processes, quantum); // AI-written, falls back to built-in
  } catch (err) {
    alert("Request failed: " + err);
  }
});

function renderCompare(results) {
  // find the best (lowest) value per column, for highlighting
  const bestWt = Math.min(...results.map((r) => r.avg_wt));
  const bestTat = Math.min(...results.map((r) => r.avg_tat));
  const bestRt = Math.min(...results.map((r) => r.avg_rt));
  const bestCs = Math.min(...results.map((r) => r.context_switches));

  const tbody = document.querySelector("#compare-table tbody");
  tbody.innerHTML = "";
  results.forEach((r) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${r.label}</td>
      <td class="${r.avg_tat === bestTat ? "best-cell" : ""}">${r.avg_tat}</td>
      <td class="${r.avg_wt === bestWt ? "best-cell" : ""}">${r.avg_wt}</td>
      <td class="${r.avg_rt === bestRt ? "best-cell" : ""}">${r.avg_rt}</td>
      <td class="${r.context_switches === bestCs ? "best-cell" : ""}">${r.context_switches}</td>
    `;
    tbody.appendChild(tr);
  });

  const ctx = document.getElementById("compare-chart").getContext("2d");
  const labels = results.map((r) => r.algorithm.toUpperCase());

  if (compareChart) compareChart.destroy();
  compareChart = new Chart(ctx, {
    type: "bar",
    data: {
      labels,
      datasets: [
        {
          label: "Avg TAT",
          data: results.map((r) => r.avg_tat),
          backgroundColor: "#8FBC94",
        },
        {
          label: "Avg WT",
          data: results.map((r) => r.avg_wt),
          backgroundColor: "#F3DE8A",
        },
        {
          label: "Avg RT",
          data: results.map((r) => r.avg_rt),
          backgroundColor: "#E8B44F",
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { labels: { color: "#33342B", font: { family: "Segoe UI" } } },
      },
      scales: {
        x: { ticks: { color: "#7A7A63" }, grid: { color: "#E6DDA8" } },
        y: {
          ticks: { color: "#7A7A63" },
          grid: { color: "#E6DDA8" },
          beginAtZero: true,
        },
      },
    },
  });
}

// ---------------- Insight cards ("What the Numbers Don't Tell You") ----------------
// finds one algorithm's result by its key: "fcfs", "sjf", "srtf" or "rr"
function getResult(results, key) {
  for (let i = 0; i < results.length; i++) {
    if (results[i].algorithm === key) {
      return results[i];
    }
  }
  return null;
}

// "1 extra context switch" / "3 extra context switches"
function extraSwitchText(n) {
  return n === 1 ? "1 extra context switch" : n + " extra context switches";
}

// how wide a bar should be (in %), compared to the bigger value of the pair
function barPercent(value, biggest) {
  if (value === 0 || biggest === 0) {
    return 0;
  }
  return Math.max((value / biggest) * 100, 6);
}

// builds a pair of bars. The lower value is the better one (green), the higher one is yellow.
function buildBarGroup(title, a, b) {
  const biggest = Math.max(a.value, b.value);
  const aClass = a.value <= b.value ? "bar-good" : "bar-warn";
  const bClass = b.value <= a.value ? "bar-good" : "bar-warn";
  return `
    <div class="ins-group">
      <div class="ins-group-title">${title}</div>
      <div class="ins-bar-row">
        <span class="ins-bar-label">${a.label}</span>
        <div class="ins-bar-track"><div class="ins-bar ${aClass}" data-width="${barPercent(a.value, biggest)}"></div></div>
        <span class="ins-bar-value">${a.value}</span>
      </div>
      <div class="ins-bar-row">
        <span class="ins-bar-label">${b.label}</span>
        <div class="ins-bar-track"><div class="ins-bar ${bClass}" data-width="${barPercent(b.value, biggest)}"></div></div>
        <span class="ins-bar-value">${b.value}</span>
      </div>
    </div>`;
}

function computeInsights(results) {
  const fcfs = getResult(results, "fcfs");
  const sjf = getResult(results, "sjf");
  const srtf = getResult(results, "srtf");
  const rr = getResult(results, "rr");

  // ---------- Card 1: Convoy effect ----------
  // find the process that arrives first and compare its burst time with the average
  let first = fcfs.table[0];
  let totalBt = 0;
  for (let i = 0; i < fcfs.table.length; i++) {
    if (fcfs.table[i].at < first.at) {
      first = fcfs.table[i];
    }
    totalBt = totalBt + fcfs.table[i].bt;
  }
  const avgBt = totalBt / fcfs.table.length;
  const convoy = first.bt > avgBt * 1.5 && srtf.avg_wt < fcfs.avg_wt;

  const convoyCard = {
    tag: "Convoy Effect",
    headline: convoy
      ? `${first.pid} hogged the CPU and everyone else had to wait`
      : "No traffic jam this time",
    verdict: convoy ? "Convoy detected" : "No convoy",
    verdictType: convoy ? "warn" : "good",
    bars: buildBarGroup(
      "Avg waiting time (ms)",
      { label: "FCFS", value: fcfs.avg_wt },
      { label: "SRTF", value: srtf.avg_wt },
    ),
    why: convoy
      ? `Think of one customer with a full trolley at the front of a single checkout lane. ${first.pid} arrives first and needs ${first.bt} ms (the average is ${avgBt.toFixed(2)} ms), so all the small jobs behind it are stuck. SRTF can interrupt it, which is why its waiting time is so much lower.`
      : `The first process (${first.pid}, ${first.bt} ms) is not much longer than the average (${avgBt.toFixed(2)} ms), so nothing big is blocking the lane. Try making the first process very long (for example BT = 20) and compare again.`,
  };

  // ---------- Card 2: Is preemption worth it? ----------
  const wtGain = sjf.avg_wt - srtf.avg_wt;
  const extra = srtf.context_switches - sjf.context_switches;

  let preemptHeadline, preemptVerdict, preemptType, preemptWhy;
  if (wtGain < 0.01) {
    preemptHeadline = "Interrupting made no difference";
    preemptVerdict = "No gain";
    preemptType = "neutral";
    preemptWhy = `SRTF only helps when a shorter job shows up while a longer one is running. Here the processes arrive close together, or the short ones already run first, so nobody needed to be interrupted.`;
  } else if (extra > 0 && wtGain >= extra) {
    preemptHeadline = "Interrupting paid off";
    preemptVerdict = "Worth it";
    preemptType = "good";
    preemptWhy = `Like a chef who pauses a slow dish to serve a quick order. SRTF saves ${wtGain.toFixed(2)} ms of average waiting for only ${extraSwitchText(extra)}, which is a good trade.`;
  } else if (extra > 0) {
    preemptHeadline = "Small gain, extra switching";
    preemptVerdict = "Maybe not worth it";
    preemptType = "warn";
    preemptWhy = `Every switch is like the chef putting one pan down and picking up another, and in a real OS that costs time. SRTF saves ${wtGain.toFixed(2)} ms but adds ${extraSwitchText(extra)}, so the gain may disappear in practice.`;
  } else {
    preemptHeadline = "A free speed-up";
    preemptVerdict = "Worth it";
    preemptType = "good";
    preemptWhy = `SRTF saves ${wtGain.toFixed(2)} ms of average waiting time without needing any extra context switches for this process set.`;
  }

  const preemptCard = {
    tag: "SJF vs SRTF",
    headline: preemptHeadline,
    verdict: preemptVerdict,
    verdictType: preemptType,
    bars:
      buildBarGroup(
        "Avg waiting time (ms)",
        { label: "SJF", value: sjf.avg_wt },
        { label: "SRTF", value: srtf.avg_wt },
      ) +
      buildBarGroup(
        "Context switches",
        { label: "SJF", value: sjf.context_switches },
        { label: "SRTF", value: srtf.context_switches },
      ),
    why: preemptWhy,
  };

  // ---------- Card 3: Round Robin and the time quantum ----------
  const quantum = parseInt(document.getElementById("quantum").value, 10) || 2;
  let maxBt = 0;
  for (let i = 0; i < rr.table.length; i++) {
    if (rr.table[i].bt > maxBt) {
      maxBt = rr.table[i].bt;
    }
  }

  let rrHeadline, rrVerdict, rrType, rrWhy;
  if (quantum >= maxBt) {
    rrHeadline = "Quantum too big: RR became FCFS";
    rrVerdict = "Acts like FCFS";
    rrType = "neutral";
    rrWhy = `Like a teacher giving each student a speaking slot. With a ${quantum} ms slot and the longest job needing only ${maxBt} ms, nobody is ever cut off, so it is just first come, first served. Lower the quantum to see RR do its job.`;
  } else if (rr.avg_rt < fcfs.avg_rt) {
    rrHeadline = "Everyone gets a quick first turn";
    rrVerdict = "Snappier, more switching";
    rrType = "good";
    rrWhy = `Like a teacher giving each student ${quantum} ms in rotation: nobody waits long for a first turn (${rr.avg_rt} ms vs ${fcfs.avg_rt} ms for FCFS). The price is more context switches (${rr.context_switches} vs ${fcfs.context_switches}). A smaller quantum means quicker turns but even more switching.`;
  } else {
    rrHeadline = "RR brings no speed-up here";
    rrVerdict = "No response gain";
    rrType = "warn";
    rrWhy = `With quantum ${quantum} ms, RR responds no faster than FCFS (${rr.avg_rt} ms vs ${fcfs.avg_rt} ms) but still adds switching (${rr.context_switches} vs ${fcfs.context_switches}), so the extra switching buys nothing for this process set.`;
  }

  const rrCard = {
    tag: "Round Robin",
    headline: rrHeadline,
    verdict: rrVerdict,
    verdictType: rrType,
    bars:
      buildBarGroup(
        "Avg response time (ms)",
        { label: "FCFS", value: fcfs.avg_rt },
        { label: "RR", value: rr.avg_rt },
      ) +
      buildBarGroup(
        "Context switches",
        { label: "FCFS", value: fcfs.context_switches },
        { label: "RR", value: rr.context_switches },
      ),
    why: rrWhy,
  };

  return [convoyCard, preemptCard, rrCard];
}

// built-in (rule-based) insights, used when Gemini is not available
function renderInsights(results) {
  showInsightCards(computeInsights(results));
}

// draws a list of insight cards
function showInsightCards(cards) {
  const container = document.getElementById("insights-body");

  let html = "";
  for (let i = 0; i < cards.length; i++) {
    const c = cards[i];
    html += `
      <div class="ins-card" style="animation-delay:${i * 0.12}s">
        <div class="ins-top">
          <span class="ins-tag">${c.tag}</span>
          <span class="ins-badge ${c.verdictType}">${c.verdict}</span>
        </div>
        <h4 class="ins-headline">${c.headline}</h4>
        ${c.bars}
        <button type="button" class="ins-why-btn">Why? &#9662;</button>
        <p class="ins-why">${c.why}</p>
      </div>`;
  }
  container.innerHTML = html;

  // animate the bars: they start at 0 width and grow to their real size
  setTimeout(function () {
    const bars = container.querySelectorAll(".ins-bar");
    for (let i = 0; i < bars.length; i++) {
      bars[i].style.width = bars[i].dataset.width + "%";
    }
  }, 50);

  // "Why?" button opens / closes the explanation
  const buttons = container.querySelectorAll(".ins-why-btn");
  for (let i = 0; i < buttons.length; i++) {
    buttons[i].addEventListener("click", function () {
      const card = this.closest(".ins-card");
      card.classList.toggle("open");
      this.innerHTML = card.classList.contains("open")
        ? "Hide &#9652;"
        : "Why? &#9662;";
    });
  }
}

// ---------------- AI-written insights (Gemini, via the Flask backend) ----------------
const METRIC_LABELS = {
  avg_wt: "Avg waiting time (ms)",
  avg_tat: "Avg turnaround time (ms)",
  avg_rt: "Avg response time (ms)",
  context_switches: "Context switches",
  max_wt: "Longest wait of any process (ms)",
};

let insightRequestId = 0; // so a slow old answer never overwrites a newer one

// makes AI text safe to put inside HTML
function escapeHtml(text) {
  return String(text)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

// reads one number out of an algorithm's result
function getMetric(result, metric) {
  if (metric === "max_wt") {
    let biggest = 0;
    for (let i = 0; i < result.table.length; i++) {
      if (result.table[i].wt > biggest) {
        biggest = result.table[i].wt;
      }
    }
    return biggest;
  }
  return result[metric];
}

// The AI only chooses WHAT to compare. The numbers in the bars always come from the real results.
function buildBarsFromSpec(results, specs) {
  let html = "";
  for (let i = 0; i < specs.length; i++) {
    const a = getResult(results, specs[i].a);
    const b = getResult(results, specs[i].b);
    if (!a || !b) {
      continue;
    }
    html += buildBarGroup(
      METRIC_LABELS[specs[i].metric],
      { label: specs[i].a.toUpperCase(), value: getMetric(a, specs[i].metric) },
      { label: specs[i].b.toUpperCase(), value: getMetric(b, specs[i].metric) },
    );
  }
  return html;
}

function aiToCards(aiInsights, results) {
  const cards = [];
  for (let i = 0; i < aiInsights.length; i++) {
    const item = aiInsights[i];
    cards.push({
      tag: escapeHtml(item.tag),
      headline: escapeHtml(item.headline),
      verdict: escapeHtml(item.verdict),
      verdictType: item.verdictType,
      bars: buildBarsFromSpec(results, item.bars),
      why: escapeHtml(item.why),
    });
  }
  return cards;
}

async function loadInsights(results, processes, quantum) {
  insightRequestId += 1;
  const myId = insightRequestId;
  const container = document.getElementById("insights-body");
  const sourceLabel = document.getElementById("insights-source");

  sourceLabel.textContent = "";
  container.innerHTML = `<div class="ins-loading">Gemini is writing insights for your numbers...</div>`;

  // give up after 60 seconds and show the built-in insights instead
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 60000);

  try {
    const res = await fetch("/api/ai-insights", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ processes, quantum }),
      signal: controller.signal,
    });
    const data = await res.json();
    if (data.error || !data.insights) {
      throw new Error(data.error || "no insights returned");
    }
    if (myId !== insightRequestId) return; // a newer comparison was started
    showInsightCards(aiToCards(data.insights, results));
    sourceLabel.textContent = "Written by Gemini from your numbers";
  } catch (err) {
    if (myId !== insightRequestId) return;
    renderInsights(results); // fall back to the built-in insights
    sourceLabel.textContent =
      "Built-in insights (Gemini not available: " + err.message + ")";
  } finally {
    clearTimeout(timer);
  }
}
