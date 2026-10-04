from flask import Flask, render_template, request, jsonify
from algorithms import fcfs

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


def validate_processes(data):
    raw_list = data.get("processes", [])

    if not raw_list:
        raise ValueError("Please provide at least one process to simulate ")

    processes = []
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

        processes.append({"pid": pid, "at": at, "bt": bt})

    return processes


@app.route("/api/simulate", methods=["POST"])
def simulate():
    data = request.get_json(force=True)
    algo = data.get("algorithm", "fcfs").lower()

    if algo != "fcfs":
        return jsonify({"error": "Can't implement this algorithm at this moment"}), 400

    try:
        processes = validate_processes(data)
        result = fcfs(processes)
        return jsonify(result)
    except Exception as exc:  # Catches any validation or execution error
        return jsonify({"error": str(exc)}), 400  # Sends error message to frontend as JSON with HTTP 400 Bad Request status


if __name__ == "__main__":
    app.run(debug=True)
