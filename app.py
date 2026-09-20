import os
import json
import urllib.request
import urllib.error
import pandas as pd
from flask import Flask, render_template, request, jsonify
from algorithms import run_algorithm, ALGORITHMS

app = Flask(__name__)

ALGO_NAMES = {
    "fcfs": "First Come First Serve (FCFS)",
    "sjf": "Shortest Job First (SJF)",
    "srtf": "Shortest Remaining Time First (SRTF)",
    "rr": "Round Robin (RR)",
}

ALGO_ABOUT = {
    "fcfs": (
        '<p class="about-desc">Processes are executed in strict sequential order of their arrival '
        'into the ready queue, operating under a First-In, First-Out (FIFO) queue policy.</p>'
        '<div class="about-badges">'
        '<span class="about-badge highlight">Non-Preemptive</span>'
        '<span class="about-badge">Criterion: Arrival Time (AT)</span>'
        '<span class="about-badge">Starvation: None</span>'
        '</div>'
        '<div class="about-subheading">Key Characteristics</div>'
        '<ul class="about-list">'
        '<li><strong>Simplicity:</strong> Minimal scheduling overhead and straightforward FIFO implementation.</li>'
        '<li><strong>Convoy Effect:</strong> A CPU-heavy process running first delays all subsequent shorter jobs, sharply inflating average wait times.</li>'
        '<li><strong>Deterministic:</strong> Execution order strictly mirrors arrival timestamps with zero preemption interruptions.</li>'
        '</ul>'
    ),
    "sjf": (
        '<p class="about-desc">Selects the available arrived process with the smallest CPU burst time. '
        'Once execution starts, the process runs uninterrupted until complete.</p>'
        '<div class="about-badges">'
        '<span class="about-badge highlight">Non-Preemptive</span>'
        '<span class="about-badge">Criterion: Burst Time (BT)</span>'
        '<span class="about-badge">Starvation: Possible for long jobs</span>'
        '</div>'
        '<div class="about-subheading">Key Characteristics</div>'
        '<ul class="about-list">'
        '<li><strong>Optimal Waiting Time:</strong> Mathematically optimal for minimizing average waiting time among all non-preemptive algorithms.</li>'
        '<li><strong>Starvation Risk:</strong> Long-running processes may wait indefinitely if shorter processes continuously arrive in the ready queue.</li>'
        '<li><strong>Estimation Required:</strong> Real-world implementations require predicting CPU burst times in advance.</li>'
        '</ul>'
    ),
    "srtf": (
        '<p class="about-desc">The preemptive counterpart of SJF. Whenever a newly arrived process requires '
        'less remaining CPU time than the currently running job, the CPU immediately preempts execution.</p>'
        '<div class="about-badges">'
        '<span class="about-badge highlight">Preemptive</span>'
        '<span class="about-badge">Criterion: Remaining Time</span>'
        '<span class="about-badge">Starvation: High risk for long jobs</span>'
        '</div>'
        '<div class="about-subheading">Key Characteristics</div>'
        '<ul class="about-list">'
        '<li><strong>Peak Responsiveness:</strong> Short tasks complete almost immediately without waiting behind large CPU-bound processes.</li>'
        '<li><strong>Theoretical Best WT:</strong> Delivers the lowest overall average waiting time across all scheduling strategies.</li>'
        '<li><strong>Preemption Overhead:</strong> Frequent context switches add CPU cycles and require continuous tracking of remaining bursts.</li>'
        '</ul>'
    ),
    "rr": (
        '<p class="about-desc">Tailored for time-sharing operating systems. Every ready process is allocated a '
        'fixed slice of execution time (Time Quantum) before being preempted to the back of the queue.</p>'
        '<div class="about-badges">'
        '<span class="about-badge highlight">Preemptive</span>'
        '<span class="about-badge">Criterion: Time Quantum (Q)</span>'
        '<span class="about-badge">Starvation: None (Fair Share)</span>'
        '</div>'
        '<div class="about-subheading">Key Characteristics</div>'
        '<ul class="about-list">'
        '<li><strong>High Responsiveness:</strong> Low initial response time (RT); every process quickly gets a first turn on the CPU.</li>'
        '<li><strong>Quantum Sensitivity:</strong> A very large quantum degrades into FCFS, whereas an excessively small quantum causes heavy switching overhead.</li>'
        '<li><strong>Guaranteed Fairness:</strong> Starvation-free by design, ensuring equitable CPU distribution across all processes.</li>'
        '</ul>'
    ),
}


@app.route("/")
def index():
    return render_template("index.html", algo_names=ALGO_NAMES, algo_about=ALGO_ABOUT)


def _parse_processes(payload):
    processes = []
    for row in payload.get("processes", []):
        processes.append({
            "pid": str(row["pid"]),
            "at": int(row["at"]),
            "bt": int(row["bt"]),
        })
    if not processes:
        raise ValueError("At least one process is required.")
    return processes


@app.route("/api/simulate", methods=["POST"])
def simulate():
    payload = request.get_json(force=True)
    algo = payload.get("algorithm", "fcfs").lower()

    if algo not in ALGO_NAMES:
        return jsonify({"error": f"Unknown algorithm '{algo}'"}), 400

    try:
        processes = _parse_processes(payload)
        quantum = int(payload.get("quantum", 2))
        result = run_algorithm(algo, processes, quantum)
        result["algorithm"] = algo
        result["algorithm_label"] = ALGO_NAMES[algo]
        return jsonify(result)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400


@app.route("/api/compare", methods=["POST"])
def compare():
    payload = request.get_json(force=True)
    try:
        processes = _parse_processes(payload)
        quantum = int(payload.get("quantum", 2))
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400

    results = []
    for algo in ("fcfs", "sjf", "srtf", "rr"):
        try:
            r = run_algorithm(algo, processes, quantum)
            results.append({
                "algorithm": algo,
                "label": ALGO_NAMES[algo],
                "avg_wt": r["averages"]["wt"],
                "avg_tat": r["averages"]["tat"],
                "avg_rt": r["averages"]["rt"],
                "context_switches": r["context_switches"],
                "table": r["table"],  # per-process CT/TAT/WT/RT, needed for the insights section
            })
        except Exception as exc:
            return jsonify({"error": f"{algo}: {exc}"}), 400

    # use pandas to find the best-performing algorithm on each metric
    df = pd.DataFrame(results)
    best = {
        "wt": df.loc[df["avg_wt"].idxmin(), "algorithm"],
        "tat": df.loc[df["avg_tat"].idxmin(), "algorithm"],
        "rt": df.loc[df["avg_rt"].idxmin(), "algorithm"],
    }

    return jsonify({"results": results, "best": best})


# ---------------- Gemini (AI-written insights) ----------------
def _load_env_file():
    """Reads settings such as GEMINI_API_KEY from a file called .env next to app.py."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_env_file()

# If the first model is busy or unavailable, the next one is tried.
GEMINI_MODELS = [
    os.environ.get("GEMINI_MODEL", "gemini-flash-latest"),
    "gemini-flash-lite-latest",
    "gemini-2.5-flash",
]

ALLOWED_ALGOS = ["fcfs", "sjf", "srtf", "rr"]
ALLOWED_METRICS = ["avg_wt", "avg_tat", "avg_rt", "context_switches", "max_wt"]

JSON_SHAPE = (
    '{"insights":[{"tag":"Convoy Effect","headline":"...","verdict":"...",'
    '"verdictType":"good","why":"...","bars":[{"metric":"avg_wt","a":"fcfs","b":"srtf"}]}]}'
)


def _build_insight_prompt(processes, quantum, summary):
    lines = []
    lines.append(
        "You are a friendly operating-systems tutor. A student compared four CPU scheduling "
        "algorithms on the same processes. Write exactly 3 short insights that reveal something "
        "the average numbers alone do not show (for example: convoy effect, starvation risk, "
        "fairness, context-switch cost, effect of the time quantum, which algorithm suits which situation)."
    )
    lines.append("")
    lines.append(
        "Processes: "
        + ", ".join(f"{p['pid']}(arrival={p['at']}, burst={p['bt']})" for p in processes)
    )
    lines.append(f"Round Robin time quantum: {quantum}")
    lines.append("Results (times in ms). max_wt is the longest wait of any single process:")
    for algo in ALLOWED_ALGOS:
        s = summary[algo]
        lines.append(
            f"- {algo}: avg_wt={s['avg_wt']}, avg_tat={s['avg_tat']}, avg_rt={s['avg_rt']}, "
            f"context_switches={s['context_switches']}, max_wt={s['max_wt']} (process {s['max_wt_pid']})"
        )
    lines.append("")
    lines.append("Rules:")
    lines.append("- Use ONLY the numbers given above. Never invent numbers.")
    lines.append('- Plain language a beginner understands. Use one everyday analogy in the "why" field.')
    lines.append('- "headline": at most 9 words. "verdict": at most 3 words. "why": 2 or 3 sentences.')
    lines.append('- "verdictType" must be "good", "warn" or "neutral".')
    lines.append("- The 3 insights must be about 3 different topics.")
    lines.append(
        '- Each insight has 1 or 2 "bars". A bar compares two algorithms on one metric. '
        "Allowed metrics: avg_wt, avg_tat, avg_rt, context_switches, max_wt. "
        "Allowed algorithms: fcfs, sjf, srtf, rr."
    )
    lines.append("- Reply with JSON only (no markdown), in exactly this shape:")
    lines.append(JSON_SHAPE)
    return "\n".join(lines)


def _call_gemini(prompt):
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set")

    body = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseMimeType": "application/json", "temperature": 0.7},
    }).encode("utf-8")

    last_error = "no model answered"
    for model in GEMINI_MODELS:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        req = urllib.request.Request(
            url,
            data=body,
            headers={"Content-Type": "application/json", "x-goog-api-key": api_key},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=25) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            parts = data["candidates"][0]["content"]["parts"]
            return "".join(p.get("text", "") for p in parts if not p.get("thought"))
        except urllib.error.HTTPError as err:
            detail = err.read().decode("utf-8", errors="ignore")[:200]
            print(f"Gemini {model} -> HTTP {err.code}: {detail}")
            last_error = f"Gemini error {err.code} ({model})"
        except (urllib.error.URLError, TimeoutError):
            last_error = "could not reach Gemini (network problem or timeout)"
            break  # no point trying other models
        except (KeyError, IndexError, ValueError):
            last_error = f"unexpected answer from {model}"
    raise RuntimeError(last_error)


def _parse_json_text(text):
    text = text.strip()
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("Gemini did not return JSON")
    return json.loads(text[start:end + 1])


def _clean_insights(data):
    """Keeps only safe, expected fields so the page never receives surprises."""
    items = data.get("insights") if isinstance(data, dict) else None
    if not isinstance(items, list):
        raise ValueError("Gemini answer had no insights list")

    cleaned = []
    for item in items[:3]:
        if not isinstance(item, dict):
            continue
        bars = []
        raw_bars = item.get("bars")
        if isinstance(raw_bars, list):
            for b in raw_bars[:2]:
                if (
                    isinstance(b, dict)
                    and b.get("metric") in ALLOWED_METRICS
                    and b.get("a") in ALLOWED_ALGOS
                    and b.get("b") in ALLOWED_ALGOS
                ):
                    bars.append({"metric": b["metric"], "a": b["a"], "b": b["b"]})
        verdict_type = item.get("verdictType")
        if verdict_type not in ("good", "warn", "neutral"):
            verdict_type = "neutral"
        cleaned.append({
            "tag": str(item.get("tag", "Insight"))[:40],
            "headline": str(item.get("headline", ""))[:120],
            "verdict": str(item.get("verdict", ""))[:30],
            "verdictType": verdict_type,
            "why": str(item.get("why", ""))[:600],
            "bars": bars,
        })
    if not cleaned:
        raise ValueError("Gemini answer had no usable insights")
    return cleaned


@app.route("/api/ai-insights", methods=["POST"])
def ai_insights():
    payload = request.get_json(force=True)
    try:
        processes = _parse_processes(payload)
        quantum = int(payload.get("quantum", 2))
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400

    # the server recomputes the numbers itself, so the AI only sees real results
    summary = {}
    for algo in ALLOWED_ALGOS:
        r = run_algorithm(algo, processes, quantum)
        worst = max(r["table"], key=lambda row: row["wt"])
        summary[algo] = {
            "avg_wt": r["averages"]["wt"],
            "avg_tat": r["averages"]["tat"],
            "avg_rt": r["averages"]["rt"],
            "context_switches": r["context_switches"],
            "max_wt": worst["wt"],
            "max_wt_pid": worst["pid"],
        }

    try:
        text = _call_gemini(_build_insight_prompt(processes, quantum, summary))
        insights = _clean_insights(_parse_json_text(text))
    except Exception as exc:
        print("AI insights error:", exc)
        status = 503 if "GEMINI_API_KEY" in str(exc) else 502
        return jsonify({"error": str(exc)}), status

    return jsonify({"insights": insights})


if __name__ == "__main__":
    app.run(debug=True, port=5000)