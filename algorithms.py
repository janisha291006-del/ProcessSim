"""
Process Scheduling Algorithms
Each function takes a list of processes: [{"pid": "P1", "at": 0, "bt": 5}, ...]
Each function returns:
    - table: list of dicts with AT, BT, CT, TAT, WT, RT for every process
    - gantt: list of dicts [{"pid": "P1", "start": 0, "end": 5}, ...] (execution order)
"""

import copy
import pandas as pd


def _make_table_row(p, ct, first_start):
    """Build one row of the result table from a process dict."""
    tat = ct - p["at"]          # Turnaround Time = Completion - Arrival
    wt = tat - p["bt"]          # Waiting Time = Turnaround - Burst
    rt = first_start - p["at"]  # Response Time = First run start - Arrival
    return {
        "pid": p["pid"],
        "at": p["at"],
        "bt": p["bt"],
        "ct": ct,
        "tat": tat,
        "wt": wt,
        "rt": rt,
    }


def fcfs(processes):
    """First Come First Serve - run processes strictly in arrival order."""
    procs = sorted(copy.deepcopy(processes), key=lambda p: (p["at"], p["pid"]))
    time = 0
    table = []
    gantt = []

    for p in procs:
        start = max(time, p["at"])
        end = start + p["bt"]
        gantt.append({"pid": p["pid"], "start": start, "end": end})
        table.append(_make_table_row(p, end, start))
        time = end

    table.sort(key=lambda r: r["pid"])
    return table, gantt


def sjf(processes):
    """Shortest Job First (non-preemptive) - pick the shortest burst time
    among all processes that have already arrived."""
    procs = copy.deepcopy(processes)
    n = len(procs)
    done = [False] * n
    time = 0
    completed = 0
    table = []
    gantt = []

    while completed < n:
        # find arrived, not-done processes
        ready = [i for i in range(n) if not done[i] and procs[i]["at"] <= time]

        if not ready:
            # nobody has arrived yet, jump to the next arrival
            next_arrival = min(procs[i]["at"] for i in range(n) if not done[i])
            time = next_arrival
            continue

        # pick the one with the smallest burst time (tie -> earliest arrival)
        idx = min(ready, key=lambda i: (procs[i]["bt"], procs[i]["at"], procs[i]["pid"]))
        p = procs[idx]

        start = time
        end = start + p["bt"]
        gantt.append({"pid": p["pid"], "start": start, "end": end})
        table.append(_make_table_row(p, end, start))

        time = end
        done[idx] = True
        completed += 1

    table.sort(key=lambda r: r["pid"])
    return table, gantt


def srtf(processes):
    """Shortest Remaining Time First (preemptive SJF).
    Simulated one time unit at a time for clarity."""
    procs = copy.deepcopy(processes)
    n = len(procs)
    remaining = [p["bt"] for p in procs]
    first_start = [None] * n
    completion = [None] * n
    completed = 0
    time = 0
    gantt = []
    running_pid = None
    segment_start = None

    max_time = sum(p["bt"] for p in procs) + max(p["at"] for p in procs) + 1

    while completed < n and time <= max_time:
        # candidates that have arrived and still have work left
        ready = [i for i in range(n) if procs[i]["at"] <= time and remaining[i] > 0]

        if not ready:
            running_pid = None
            time += 1
            continue

        idx = min(ready, key=lambda i: (remaining[i], procs[i]["at"], procs[i]["pid"]))

        if first_start[idx] is None:
            first_start[idx] = time

        # track contiguous execution segments for the Gantt chart
        if running_pid != idx:
            if running_pid is not None and segment_start is not None:
                gantt.append({"pid": procs[running_pid]["pid"], "start": segment_start, "end": time})
            segment_start = time
            running_pid = idx

        remaining[idx] -= 1
        time += 1

        if remaining[idx] == 0:
            completion[idx] = time
            completed += 1
            gantt.append({"pid": procs[idx]["pid"], "start": segment_start, "end": time})
            running_pid = None
            segment_start = None

    table = []
    for i, p in enumerate(procs):
        table.append(_make_table_row(p, completion[i], first_start[i]))

    table.sort(key=lambda r: r["pid"])
    return table, gantt


def round_robin(processes, quantum):
    """Round Robin with a fixed time quantum."""
    procs = copy.deepcopy(processes)
    n = len(procs)
    remaining = [p["bt"] for p in procs]
    first_start = [None] * n
    completion = [None] * n

    procs_sorted_idx = sorted(range(n), key=lambda i: (procs[i]["at"], procs[i]["pid"]))
    queue = []
    time = 0
    gantt = []
    in_queue = [False] * n
    pointer = 0  # points into procs_sorted_idx for processes not yet arrived
    completed = 0

    # start the clock at the first arrival
    time = procs[procs_sorted_idx[0]]["at"]

    # add every process that has arrived by "time" into the queue
    def enqueue_arrivals(current_time):
        nonlocal pointer
        while pointer < n and procs[procs_sorted_idx[pointer]]["at"] <= current_time:
            i = procs_sorted_idx[pointer]
            queue.append(i)
            in_queue[i] = True
            pointer += 1

    enqueue_arrivals(time)

    while completed < n:
        if not queue:
            # nothing ready, fast-forward to next arrival
            time = procs[procs_sorted_idx[pointer]]["at"]
            enqueue_arrivals(time)
            continue

        idx = queue.pop(0)
        if first_start[idx] is None:
            first_start[idx] = time

        run_time = min(quantum, remaining[idx])
        start = time
        time += run_time
        remaining[idx] -= run_time
        gantt.append({"pid": procs[idx]["pid"], "start": start, "end": time})

        # any process that arrived DURING this slice joins the queue now
        enqueue_arrivals(time)

        if remaining[idx] > 0:
            queue.append(idx)
        else:
            completion[idx] = time
            completed += 1

    table = []
    for i, p in enumerate(procs):
        table.append(_make_table_row(p, completion[i], first_start[i]))

    table.sort(key=lambda r: r["pid"])
    return table, gantt


ALGORITHMS = {
    "fcfs": fcfs,
    "sjf": sjf,
    "srtf": srtf,
    "rr": round_robin,
}


def _count_context_switches(gantt):
    """A context switch happens every time the CPU hands off to a
    DIFFERENT process. Consecutive Gantt segments always belong to
    different processes (the algorithms merge same-process runs into
    one segment), so this is just (number of segments - 1). CPU idle
    gaps between segments are not counted as switches."""
    return max(len(gantt) - 1, 0)


def run_algorithm(name, processes, quantum=2):
    """Dispatch to the right algorithm and also compute averages."""
    name = name.lower()
    if name == "rr":
        table, gantt = round_robin(processes, quantum)
    elif name in ALGORITHMS:
        table, gantt = ALGORITHMS[name](processes)
    else:
        raise ValueError(f"Unknown algorithm: {name}")

    # pandas does the number-crunching: put the table in a DataFrame,
    # then just ask it for column means and the max completion time.
    df = pd.DataFrame(table)
    averages = df[["wt", "tat", "rt"]].mean().round(2)
    total_time = int(df["ct"].max())

    return {
        "table": df.to_dict(orient="records"),
        "gantt": gantt,
        "averages": {"wt": averages["wt"], "tat": averages["tat"], "rt": averages["rt"]},
        "total_time": total_time,
        "context_switches": _count_context_switches(gantt),
    }