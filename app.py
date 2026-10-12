import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, url_for
from algorithms import fcfs, srtf, sjf, round_robin, build_queues, build_warnings
from insights import get_insights, InsightError

load_dotenv()  # reads GEMINI_API_KEY from the .env file

app = Flask(__name__)


@app.context_processor
def static_with_version():
    # Adds ?v=<last edit time> to CSS/JS links, so the browser never shows an old cached copy
    def static_v(filename):
        path = os.path.join(app.static_folder, filename)
        return url_for("static", filename=filename, v=int(os.path.getmtime(path)))
    return {"static_v": static_v}


@app.route("/")
def index():
    return render_template("index.html")


def parse_whole_number(value, label, examples="0, 1 or 2"):
    """Accepts 3 or "3". Rejects 2.5, "abc" and blanks with a plain-language message."""
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    text = "" if value is None else str(value).strip()
    if text.lstrip("-").isdigit():
        return int(text)
    raise ValueError(f"{label} must be a whole number, such as {examples}.")


def validate_processes(data):
    raw_list = data.get("processes", [])

    if not raw_list:
        raise ValueError("Add at least one process to run the simulation.")

    processes = []
    used_ids = {}  # lowercase ID -> the ID as the user typed it
    last = None    # (ID, arrival time) of the row above, arrivals must not go backwards
    for num in raw_list:
        pid = str(num.get("pid", "")).strip()
        if not pid:
            raise ValueError("Every process needs an ID, such as P1 or P2.")
        if pid.lower() in used_ids:
            raise ValueError(
                f"{used_ids[pid.lower()]} and {pid} use the same ID. "
                "Give each process its own ID, such as P1, P2 or P3."
            )
        used_ids[pid.lower()] = pid

        if num.get("at") in (None, "") or num.get("bt") in (None, ""):
            raise ValueError(f"{pid} needs both an arrival time and a burst time.")

        at = parse_whole_number(num.get("at"), f"The arrival time of {pid}")
        bt = parse_whole_number(num.get("bt"), f"The burst time of {pid}")

        if at < 0:
            raise ValueError(f"The arrival time of {pid} can't be negative. Use 0 or a bigger number.")
        if bt < 1:
            raise ValueError(f"The burst time of {pid} must be at least 1 ms.")

        # A process listed below another one cannot have arrived before it
        if last is not None and at < last[1]:
            raise ValueError(
                f"{pid} arrives at {at} ms, which is earlier than {last[0]} ({last[1]} ms) listed above it. "
                "Enter processes in order of arrival time, so each arrival time is the same as or bigger than the row above."
            )
        last = (pid, at)

        processes.append({"pid": pid, "at": at, "bt": bt})

    return processes


def parse_quantum(data):
    quantum = parse_whole_number(data.get("quantum", 2), "The time quantum", examples="1, 2 or 3")
    if quantum < 1:
        raise ValueError("The time quantum must be at least 1 ms.")
    return quantum


@app.route("/api/simulate", methods=["POST"])
def simulate():
    data = request.get_json(force=True)
    algo = data.get("algorithm", "fcfs").lower()

    if algo not in ["fcfs", "srtf", "sjf", "rr"]:
        return jsonify({"error": "That algorithm isn't available yet. Pick one from the list."}), 400

    try:
        processes = validate_processes(data)
        quantum = None
        if algo == "fcfs":
            result = fcfs(processes)
        elif algo == "srtf":
            result = srtf(processes)
        elif algo == "sjf":
            result = sjf(processes)
        elif algo == "rr":
            quantum = parse_quantum(data)
            result = round_robin(processes, quantum=quantum)

        # The UI draws the Ready / Running queue rows, so the raw Gantt list is turned into those rows
        gantt = result.pop("gantt")
        result["queues"] = build_queues(processes, gantt, algo)
        result["warnings"] = build_warnings(processes, result["total_time"])  # shown, never blocks the run
        return jsonify(result)
    except Exception as exc:  # Catches any validation or execution error
        return jsonify({"error": str(exc)}), 400  # Sends error message to frontend as JSON with HTTP 400 Bad Request status


# Order and names used on the comparison screen
COMPARE_ALGOS = [
    ("fcfs", "FCFS", "Non-Preemptive"),
    ("sjf", "SJF", "Non-Preemptive"),
    ("srtf", "SRTF", "Preemptive"),
    ("rr", "Round Robin", "Preemptive"),
]


def run_all_algorithms(processes, quantum):
    """Runs the 4 algorithms on the SAME processes and keeps only what the comparison needs."""
    runners = {
        "fcfs": lambda: fcfs(processes),
        "sjf": lambda: sjf(processes),
        "srtf": lambda: srtf(processes),
        "rr": lambda: round_robin(processes, quantum=quantum),
    }
    rows = []
    for key, label, kind in COMPARE_ALGOS:
        result = runners[key]()
        rows.append({
            "key": key,
            "label": label,
            "kind": kind,
            "ct": (sum(r["ct"] for r in result["table"]) / len(result["table"])) if result["table"] else 0,
            "wt": result["averages"]["wt"],
            "tat": result["averages"]["tat"],
            "rt": result["averages"]["rt"],
            "context_switches": result["context_switches"],
            "total_time": result["total_time"],
            "wt_by_process": {r["pid"]: r["wt"] for r in result["table"]},
            "rt_by_process": {r["pid"]: r["rt"] for r in result["table"]},
        })
    return rows


@app.route("/api/compare", methods=["POST"])
def compare():
    data = request.get_json(force=True)
    try:
        processes = validate_processes(data)
        quantum = parse_quantum(data)
        comparison = run_all_algorithms(processes, quantum)
        return jsonify({
            "quantum": quantum,
            "processes": processes,
            "comparison": comparison,
            # Idle time is the same for every algorithm, so the first row is enough
            "warnings": build_warnings(processes, comparison[0]["total_time"]),
        })
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400


@app.route("/api/insights", methods=["POST"])
def insights():
    data = request.get_json(force=True)
    try:
        processes = validate_processes(data)
        quantum = parse_quantum(data)
        # Recalculate on the server so Gemini only ever sees real, trusted results
        comparison = run_all_algorithms(processes, quantum)
        return jsonify({"insights": get_insights(processes, quantum, comparison)})
    except InsightError as exc:
        return jsonify({"error": str(exc)}), 502
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400


if __name__ == "__main__":
    app.run(debug=True)
