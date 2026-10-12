// ProcessSim - Screen 2: Comparison & Analysis
// Uses collectProcesses() from app.js (same process table).

// One fixed color per algorithm, reused in every chart
const ALGO_COLORS = {
  fcfs: "#F3DE8A",
  sjf: "#8FBC94",
  srtf: "#E8B44F",
  rr: "#6FA37A",
};

let lastCompareKey = null; // remembers the last input we compared, so switching tabs does not re-run for nothing
let compareRequestId = 0;  // lets us ignore old responses if the user clicks Compare again quickly
let lastComparePayload = null;

// Prevents user-typed text (like a PID) from being treated as HTML
function esc(text) {
  const div = document.createElement("div");
  div.textContent = String(text);
  return div.innerHTML;
}

// ---------------- Switching between the two screens ----------------

function showScreen(name) {
  document.getElementById("screen-sim").style.display = name === "sim" ? "block" : "none";
  document.getElementById("screen-compare").style.display = name === "compare" ? "block" : "none";
  document.querySelectorAll(".tab-btn").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.screen === name);
  });

  if (name === "compare") {
    // Start from the quantum chosen on the simulator screen
    document.getElementById("compare-quantum").value = document.getElementById("quantum-input").value || 2;
    runComparison(false);
  }
}

document.querySelectorAll(".tab-btn").forEach((btn) => {
  btn.addEventListener("click", () => showScreen(btn.dataset.screen));
});

// ---------------- Run the comparison ----------------

function showCompareWarnings(warnings) {
  const box = document.getElementById("compare-warning");
  if (!warnings || warnings.length === 0) {
    box.style.display = "none";
    box.textContent = "";
    return;
  }
  box.style.display = "block";
  box.innerHTML = "&#9888; " + warnings.map((w) => esc(w)).join("<br>&#9888; ");
}

function showCompareError(message) {
  showCompareWarnings([]);
  document.getElementById("compare-error").textContent = message;
  document.getElementById("compare-results").style.display = "none";
  document.getElementById("compare-empty").style.display = message ? "none" : "block";
}

// force = true when the user clicked the button (always re-run); false when just opening the tab
async function runComparison(force) {
  document.getElementById("compare-error").textContent = "";

  const processes = collectProcesses();

  if (processes.length === 0) {
    lastCompareKey = null;
    document.getElementById("compare-results").style.display = "none";
    document.getElementById("compare-empty").style.display = "block";
    return;
  }

  const quantum = document.getElementById("compare-quantum").value.trim(); // the server checks it
  const payload = { processes, quantum };
  const key = JSON.stringify(payload);
  if (!force && key === lastCompareKey) return; // same input as last time, results are already on screen

  const myRequest = ++compareRequestId;

  try {
    const res = await fetch("/api/compare", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await res.json();
    if (myRequest !== compareRequestId) return; // a newer request has started
    if (data.error) {
      showCompareError(data.error);
      return;
    }

    lastCompareKey = key;
    lastComparePayload = payload;
    document.getElementById("compare-empty").style.display = "none";
    showCompareWarnings(data.warnings);
    renderComparison(data);
    loadInsights(); // Gemini insights come last
  } catch (err) {
    showCompareError("Request failed: " + err.message);
  }
}

document.getElementById("compare-run").addEventListener("click", () => runComparison(true));
document.getElementById("compare-quantum").addEventListener("keydown", (e) => {
  if (e.key === "Enter") runComparison(true);
});

// ---------------- Helpers ----------------

// Which algorithms have the best (smallest) value for a metric? Returns [] when all are equal.
// Smaller is better for every metric here, and the screen always calls it "best".
function bestKeys(rows, field) {
  const values = rows.map((r) => r[field]);
  const min = Math.min(...values);
  if (values.every((v) => v === min)) return [];
  return rows.filter((r) => r[field] === min).map((r) => r.key);
}

// ["SJF", "SRTF"] -> "SJF and SRTF", ["FCFS","SJF","RR"] -> "FCFS, SJF and RR"
function joinNames(names) {
  if (names.length <= 1) return names.join("");
  return names.slice(0, -1).join(", ") + " and " + names[names.length - 1];
}

function labelsFor(rows, keys) {
  return joinNames(rows.filter((r) => keys.includes(r.key)).map((r) => r.label));
}

// 1.50 -> "1.5", 3 -> "3"
function formatNum(value) {
  return String(Number(Number(value).toFixed(2)));
}

// Rounds the top of a chart up to a clean number (7.75 -> 10, 4.5 -> 5)
function niceCeil(value) {
  if (value <= 0) return 1;
  const power = Math.pow(10, Math.floor(Math.log10(value)));
  const f = value / power;
  const nice = f <= 1 ? 1 : f <= 2 ? 2 : f <= 5 ? 5 : 10;
  return nice * power;
}

// ---------------- Headline tiles ----------------

function kpiTileHtml(label, rows, field, formatValue) {
  const best = bestKeys(rows, field);
  const names = best.length === 0 ? "All four tie" : labelsFor(rows, best);
  const value = Math.min(...rows.map((r) => r[field]));
  return `
    <div class="kpi">
      <div class="kpi-label">${label}</div>
      <div class="kpi-names">${esc(names)}</div>
      <div class="kpi-value">${formatValue(value)}</div>
    </div>`;
}

// ---------------- Bar charts ----------------

// Vertical bar chart.
// groups = [{ label: "FCFS", bars: [{ key: "fcfs", label: "FCFS", value: 4, best: false }] }, ...]
function barChartHtml(groups, unit, barsPerGroup, fluid = false) {
  const PLOT_HEIGHT = 190;
  const top = niceCeil(Math.max(...groups.flatMap((g) => g.bars.map((b) => b.value)), 0));

  const gridLines = [0, 1, 2, 3, 4]
    .map((i) => {
      const tick = (top * i) / 4;
      return `<div class="grid-line" style="bottom:${(tick / top) * PLOT_HEIGHT}px"><span>${formatNum(tick)}</span></div>`;
    })
    .join("");

  const columns = groups
    .map((group) => {
      const bars = group.bars
        .map((b) => {
          const height = Math.max((b.value / top) * PLOT_HEIGHT, 3);
          return `
            <div class="bar-wrap">
              <div class="bar-num${b.best ? " best" : ""}">${formatNum(b.value)}</div>
              <div class="bar${b.best ? " best" : ""}" style="height:${height}px; background:${ALGO_COLORS[b.key]}"
                   title="${esc(b.label)}: ${formatNum(b.value)}${unit}"></div>
            </div>`;
        })
        .join("");
      return `<div class="bar-group"><div class="bars">${bars}</div><div class="group-label">${esc(group.label)}</div></div>`;
    })
    .join("");

  const minWidth = fluid ? 0 : groups.length * (barsPerGroup * 34 + 36);
  return `
    <div class="chart-scroll">
      <div class="plot" style="height:${PLOT_HEIGHT}px; min-width:${minWidth}px">
        ${gridLines}
        <div class="bar-groups">${columns}</div>
      </div>
    </div>`;
}

// One small chart for one metric: one bar per algorithm, best one outlined
function metricChartHtml(rows, field, unit) {
  const best = bestKeys(rows, field);
  return barChartHtml(
    rows.map((r) => ({
      label: r.label,
      bars: [{ key: r.key, label: r.label, value: r[field], best: best.includes(r.key) }],
    })),
    unit,
    1,
    true
  );
}

// ---------------- Comparison table ----------------

function renderAlgoTable(data) {
  const rows = data.comparison;
  const cols = [
    ["ct", "Avg CT"],
    ["tat", "Avg TAT"],
    ["wt", "Avg WT"],
    ["rt", "Avg RT"],
  ];

  const head = `<tr><th>Algorithm</th>${cols.map(([, name]) => `<th>${name}</th>`).join("")}</tr>`;
  const body = rows
    .map((r) => {
      const name = r.key === "rr" ? `RR (TQ=${data.quantum})` : r.label === "Round Robin" ? "RR" : r.label;
      const cells = cols
        .map(([f]) => {
          return `<td>${formatNum(r[f])}</td>`;
        })
        .join("");
      return `<tr><td class="algo-name">${esc(name)}</td>${cells}</tr>`;
    })
    .join("");

  document.getElementById("algo-table").innerHTML = `<thead>${head}</thead><tbody>${body}</tbody>`;
}

// ---------------- Gemini insights ----------------

const insightsBox = document.getElementById("insights-container");
const refreshBtn = document.getElementById("insights-refresh");
let insightsRequestId = 0;

function insightsLoadingHtml() {
  const card = `<div class="insight-card skeleton"><div class="sk-line short"></div><div class="sk-line"></div><div class="sk-line"></div></div>`;
  return `<div class="insights-status">Gemini is reading your results&hellip;</div>
          <div class="insight-grid">${card.repeat(4)}</div>`;
}

async function loadInsights() {
  if (!lastComparePayload) return;
  const myRequest = ++insightsRequestId;
  refreshBtn.style.display = "none";
  insightsBox.innerHTML = insightsLoadingHtml();

  try {
    const res = await fetch("/api/insights", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(lastComparePayload),
    });
    const data = await res.json();
    if (myRequest !== insightsRequestId) return; // user started a newer comparison
    if (data.error) throw new Error(data.error);

    insightsBox.innerHTML =
      `<div class="insight-grid">` +
      data.insights
        .map(
          (item, i) => `
        <div class="insight-card">
          <div class="insight-num">${i + 1}</div>
          <div class="insight-title">${esc(item.title)}</div>
          <p class="insight-text">${esc(item.text)}</p>
        </div>`
        )
        .join("") +
      `</div>`;
    // no Regenerate button: the 4 insights stay fixed once shown
  } catch (err) {
    if (myRequest !== insightsRequestId) return;
    insightsBox.innerHTML = `<div class="insights-error">${esc(err.message)}</div>`;
    refreshBtn.style.display = "inline-block";
    refreshBtn.textContent = "\u21BB Try again";
    return;
  }
}

refreshBtn.addEventListener("click", loadInsights);

// ---------------- Rendering ----------------

function renderComparison(data) {
  const rows = data.comparison;

  // 0. Comparison table first
  renderAlgoTable(data);

  // 1. Headline tiles
  document.getElementById("compare-kpis").innerHTML =
    kpiTileHtml("Best avg waiting time", rows, "wt", (v) => `${formatNum(v)} ms`) +
    kpiTileHtml("Best avg response time", rows, "rt", (v) => `${formatNum(v)} ms`) +
    kpiTileHtml("Best context switches", rows, "context_switches", (v) => `${v} switch${v === 1 ? "" : "es"}`);

  // Three small charts: average TAT, WT and RT
  document.getElementById("chart-tat").innerHTML = metricChartHtml(rows, "tat", " ms");
  document.getElementById("chart-wt").innerHTML = metricChartHtml(rows, "wt", " ms");
  document.getElementById("chart-rt").innerHTML = metricChartHtml(rows, "rt", " ms");

  // 4. Show the whole results block
  document.getElementById("compare-results").style.display = "block";
}
