import os
from flask import Flask, render_template, request, jsonify, url_for
from algorithms import fcfs, srtf, sjf, round_robin, build_steps, build_warnings

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


def validate_processes(data):
    raw_list = data.get("processes", [])

    if not raw_list:
        raise ValueError("Please provide at least one process to simulate ")

    processes = []
    last_at = None  # Arrival times must not go backwards in the order processes were added
    for num in raw_list:
        pid = str(num.get("pid", "")).strip()
        if not pid:
            raise ValueError("Every process must have a valid Process ID like P1,P2,etc.")

        try:
            at = int(num["at"])
            bt = int(num["bt"])
        except (KeyError, TypeError, ValueError):
            raise ValueError(f"Arrival and Burst times for '{pid}' must be valid numbers.")

        if at < 0:
            raise ValueError(f"Arrival time for '{pid}' cannot be negative")

        if bt <= 0:
            raise ValueError(f"Burst time for '{pid}' must be greater than 0")

        if last_at is not None and at < last_at:
            raise ValueError(
                f"Arrival time for '{pid}' ({at}) cannot be less than the arrival time of "
                f"the processes added before it ({last_at})."
            )
        last_at = at

        processes.append({"pid": pid, "at": at, "bt": bt})

    return processes


@app.route("/api/simulate", methods=["POST"])
def simulate():
    data = request.get_json(force=True)
    algo = data.get("algorithm", "fcfs").lower()

    if algo not in ["fcfs", "srtf", "sjf", "rr"]:
        return jsonify({"error": "Can't implement this algorithm at this moment still."}), 400

    try:
        processes = validate_processes(data)
        if algo == "fcfs":
            result = fcfs(processes)
        elif algo == "srtf":
            result = srtf(processes)
        elif algo == "sjf":
            result = sjf(processes)
        elif algo == "rr":
            try:
                quantum = int(data.get("quantum", 2))
                if quantum <= 0:
                    raise ValueError
            except (TypeError, ValueError):
                return jsonify({"error": "Time Quantum must be a positive number greater than 0."}), 400
            result = round_robin(processes, quantum=quantum)

        # The UI shows ready/running queues step by step, so the raw Gantt slices
        # are only used to build the steps and are not sent to the browser.
        gantt = result.pop("gantt")
        result["steps"] = build_steps(processes, gantt, algo)
        result["warnings"] = build_warnings(processes)  # shown to the user, never blocks the run
        return jsonify(result)
    except Exception as exc:  # Catches any validation or execution error
        return jsonify({"error": str(exc)}), 400  # Sends error message to frontend as JSON with HTTP 400 Bad Request status


if __name__ == "__main__":
    app.run(debug=True)
