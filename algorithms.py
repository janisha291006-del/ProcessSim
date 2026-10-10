import copy 
import re


def _pid_sort_key(item):
    """Sort key for natural alphanumeric ordering (e.g., P1, P2, ..., P9, P10)."""
    pid = item["pid"] if isinstance(item, dict) else str(item)
    return [int(part) if part.isdigit() else part.lower() for part in re.split(r'(\d+)', pid)]


# 1. FCFS  
def fcfs(processes):
    if not processes:
        return {
            "table": [],
            "gantt": [],
            "averages": {"wt": 0, "tat": 0, "rt": 0},
            "total_time": 0,
            "context_switches": 0,
        }

    # sorting process by arrival time, then by pid for proper ordering
    sorted_processes = sorted(processes, key=lambda p: (p["at"], p["pid"]))

    current_time = 0
    table = []
    gantt = []

    for p in sorted_processes: #to iterate through sorted process
        pid = p["pid"]
        arrival_time = p["at"]
        burst_time = p["bt"]

        
        start_time = max(current_time, arrival_time) # It takes the maximum time amongst the current time and arrival time so that it can it can schedule accordingly
        completion_time = start_time + burst_time 

        turnaround_time = completion_time - arrival_time  # TAT = CT - AT
        waiting_time = turnaround_time - burst_time       # WT = TAT - BT
        response_time = start_time - arrival_time         # RT = Start - AT

    #gantt chart 

        gantt.append({                      #In every iteration of for p(from the for loop) in sorted_processes, you bundle 3 pieces of information into one dictionary
            "pid": pid,
            "start": start_time,
            "end": completion_time,
        })

    #table
        table.append({
            "pid": pid,
            "at": arrival_time,
            "bt": burst_time,
            "ct": completion_time,
            "tat": turnaround_time,
            "wt": waiting_time,
            "rt": response_time,
        })

        current_time = completion_time
    #summary averages

    total_processes = len(table)
    avg_wt = round(sum(row["wt"] for row in table) / total_processes, 2)
    avg_tat = round(sum(row["tat"] for row in table) / total_processes, 2)
    avg_rt = round(sum(row["rt"] for row in table) / total_processes, 2)
    total_time = max((row["ct"] for row in table), default=0)
    context_switches = max(len(gantt) - 1, 0)


    table.sort(key=lambda r: r["pid"]) # to sort processes in the way they were entered not on the basis of when they were scheduled 

    return {
        "table": table,
        "gantt": gantt,
        "averages": {
            "wt": avg_wt,
            "tat": avg_tat,
            "rt": avg_rt,
        },
        "total_time": total_time,
        "context_switches": context_switches,
    }


# other algos

# def _make_table_row(p, ct, first_start):
#     """Build one row of the result table from a process dict."""
#     tat = ct - p["at"]          # Turnaround Time = Completion - Arrival
#     wt = tat - p["bt"]          # Waiting Time = Turnaround - Burst
#     rt = first_start - p["at"]  # Response Time = First run start - Arrival
#     return {
#         "pid": p["pid"],
#         "at": p["at"],
#         "bt": p["bt"],
#         "ct": ct,
#         "tat": tat,
#         "wt": wt,
#         "rt": rt,
#     }


# 2. SJF (Shortest Job First - Non-Preemptive)

def sjf(processes):
    if not processes:
        return {
            "table": [],
            "gantt": [],
            "averages": {"wt": 0, "tat": 0, "rt": 0},
            "total_time": 0,
            "context_switches": 0,
        }

    n = len(processes)
    pid = [p["pid"] for p in processes]
    at = [p["at"] for p in processes]
    bt = [p["bt"] for p in processes]

    completed = [0] * n  # to store which processes have been completed
    startTime = [-1] * n 
    completionTime = [-1] * n

    currentTime = min(at)

    def pendingProcesses(at, completed, currentTime):
        # Returns indices of all pending arrived processes
        pending = []
        for i in range(n):
            if at[i] <= currentTime and completed[i] == 0:
                pending.append(i)
        return pending

    def shortestJob(pending, bt):
        # Returns index of process having minimum burst time (with tie-breaker for fairness)
        shortest = pending[0]
        for i in pending[1:]:
            if bt[i] < bt[shortest]:
                shortest = i
            elif bt[i] == bt[shortest]:
                if at[i] < at[shortest] or (at[i] == at[shortest] and _pid_sort_key(pid[i]) < _pid_sort_key(pid[shortest])):
                    shortest = i
        return shortest

    gantt = []

    while completed.count(1) != n:
        pending = pendingProcesses(at, completed, currentTime)

        if len(pending) == 0:
            # If no process has arrived yet, jump to the next earliest arrival
            uncompleted_arrivals = [at[i] for i in range(n) if completed[i] == 0]
            if uncompleted_arrivals:
                currentTime = max(currentTime + 1, min(uncompleted_arrivals))
            else:
                break
            continue

        # Select shortest job
        p = shortestJob(pending, bt)

        startTime[p] = currentTime
        completionTime[p] = currentTime + bt[p]

        gantt.append({
            "pid": pid[p],
            "start": startTime[p],
            "end": completionTime[p],
        })

        currentTime = completionTime[p]
        completed[p] = 1

    table = []
    for i in range(n):
        tat_val = completionTime[i] - at[i]
        wt_val = tat_val - bt[i]
        rt_val = startTime[i] - at[i]
        table.append({
            "pid": pid[i],
            "at": at[i],
            "bt": bt[i],
            "ct": completionTime[i],
            "tat": tat_val,
            "wt": wt_val,
            "rt": rt_val,
        })

    # Sort table naturally (P1, P2, ..., P9, P10)
    table.sort(key=_pid_sort_key)

    total_processes = len(table)
    avg_wt = round(sum(row["wt"] for row in table) / total_processes, 2)
    avg_tat = round(sum(row["tat"] for row in table) / total_processes, 2)
    avg_rt = round(sum(row["rt"] for row in table) / total_processes, 2)
    total_time = max((row["ct"] for row in table), default=0)
    context_switches = max(len(gantt) - 1, 0)

    return {
        "table": table,
        "gantt": gantt,
        "averages": {
            "wt": avg_wt,
            "tat": avg_tat,
            "rt": avg_rt,
        },
        "total_time": total_time,
        "context_switches": context_switches,
    }

def _make_table_row(p, ct, first_start):
    
    tat = ct - p["at"]  # Turnaround Time = Completion - Arrival
    wt = tat - p["bt"]  # Waiting Time = Turnaround - Burst
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


def srtf(processes):
    if not processes:
        return {
            "table": [],
            "gantt": [],
            "averages": {"wt": 0, "tat": 0, "rt": 0},
            "total_time": 0,
            "context_switches": 0,
        }

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

    while completed < n:
        ready = [
            i for i in range(n) if procs[i]["at"] <= time and remaining[i] > 0
        ]

        if not ready:
            # Flush running segment before idling
            if running_pid is not None and segment_start is not None:
                gantt.append({
                    "pid": procs[running_pid]["pid"],
                    "start": segment_start,
                    "end": time,
                })
                segment_start = None
            running_pid = None
            # Fast-forward time to next arriving process
            time = min(procs[i]["at"] for i in range(n) if remaining[i] > 0)
            continue

        # Prefer keeping the currently running process if no strictly shorter job is ready
        if running_pid is not None and remaining[running_pid] > 0 and procs[running_pid]["at"] <= time:
            min_remaining = min(remaining[i] for i in ready)
            if remaining[running_pid] == min_remaining:
                idx = running_pid
            else:
                idx = min(
                    ready, key=lambda i: (remaining[i], procs[i]["at"], procs[i]["pid"])
                )
        else:
            idx = min(
                ready, key=lambda i: (remaining[i], procs[i]["at"], procs[i]["pid"])
            )

        if first_start[idx] is None:
            first_start[idx] = time

        if running_pid != idx:
            if running_pid is not None and segment_start is not None:
                gantt.append({
                    "pid": procs[running_pid]["pid"],
                    "start": segment_start,
                    "end": time,
                })
            segment_start = time
            running_pid = idx

        remaining[idx] -= 1
        time += 1

        if remaining[idx] == 0:
            completion[idx] = time
            completed += 1
            gantt.append({
                "pid": procs[idx]["pid"],
                "start": segment_start,
                "end": time,
            })
            running_pid = None
            segment_start = None

    table = []
    for i, p in enumerate(procs):
        table.append(_make_table_row(p, completion[i], first_start[i]))

    table.sort(key=lambda r: r["pid"])

    # summary averages
    total_processes = len(table)
    avg_wt = round(sum(row["wt"] for row in table) / total_processes, 2)
    avg_tat = round(sum(row["tat"] for row in table) / total_processes, 2)
    avg_rt = round(sum(row["rt"] for row in table) / total_processes, 2)
    total_time = max((row["ct"] for row in table), default=0)
    context_switches = max(len(gantt) - 1, 0)

    return {
        "table": table,
        "gantt": gantt,
        "averages": {
            "wt": avg_wt,
            "tat": avg_tat,
            "rt": avg_rt,
        },
        "total_time": total_time,
        "context_switches": context_switches,
    }

# =====================================================================
# 4. Round Robin (RR) - Preemptive
# =====================================================================

def round_robin(processes, quantum=2):
    """
    Round Robin CPU Scheduling Algorithm.

    Parameters:
      processes: list of dicts [{"pid": "P1", "at": 0, "bt": 5}, ...]
      quantum: int (Time slice allocated per process, default=2)

    Returns:
      dict with:
        - "table": list of dicts with (pid, at, bt, ct, tat, wt, rt)
        - "gantt": list of execution slices [{"pid": "P1", "start": 0, "end": 2}, ...]
        - "averages": {"wt": avg_wt, "tat": avg_tat, "rt": avg_rt}
        - "total_time": total elapsed schedule time
        - "context_switches": number of context switches
    """
    if not processes:
        return {
            "table": [],
            "gantt": [],
            "averages": {"wt": 0, "tat": 0, "rt": 0},
            "total_time": 0,
            "context_switches": 0,
        }

    n = len(processes)
    # Sort processes by arrival time, breaking ties with natural alphanumeric PID order
    sorted_procs = sorted(processes, key=lambda p: (p["at"], _pid_sort_key(p)))

    rem_bt = {p["pid"]: p["bt"] for p in sorted_procs}
    first_start = {p["pid"]: None for p in sorted_procs}
    completion_time = {p["pid"]: None for p in sorted_procs}

    queue = []
    gantt = []
    pointer = 0
    completed = 0

    # Start clock at earliest arrival time
    current_time = sorted_procs[0]["at"]

    def enqueue_arrivals(time_limit):
        nonlocal pointer
        while pointer < n and sorted_procs[pointer]["at"] <= time_limit:
            queue.append(sorted_procs[pointer]["pid"])
            pointer += 1

    enqueue_arrivals(current_time)

    while completed < n:
        if not queue:
            # CPU is idle: fast-forward to next arrival
            if pointer < n:
                current_time = sorted_procs[pointer]["at"]
                enqueue_arrivals(current_time)
            continue

        cur_pid = queue.pop(0)

        if first_start[cur_pid] is None:
            first_start[cur_pid] = current_time

        exec_time = min(quantum, rem_bt[cur_pid])
        start_time = current_time
        current_time += exec_time
        rem_bt[cur_pid] -= exec_time

        gantt.append({
            "pid": cur_pid,
            "start": start_time,
            "end": current_time,
        })

        # New arrivals landing during or at the end of this slice join before preempted process
        enqueue_arrivals(current_time)

        if rem_bt[cur_pid] > 0:
            queue.append(cur_pid)
        else:
            completion_time[cur_pid] = current_time
            completed += 1

    table = []
    for p in sorted_procs:
        p_id = p["pid"]
        ct = completion_time[p_id]
        tat = ct - p["at"]
        wt = tat - p["bt"]
        rt = first_start[p_id] - p["at"]
        table.append({
            "pid": p_id,
            "at": p["at"],
            "bt": p["bt"],
            "ct": ct,
            "tat": tat,
            "wt": wt,
            "rt": rt,
        })

    # Sort table naturally (P1, P2, ..., P9, P10)
    table.sort(key=_pid_sort_key)

    total_processes = len(table)
    avg_wt = round(sum(row["wt"] for row in table) / total_processes, 2) if total_processes else 0
    avg_tat = round(sum(row["tat"] for row in table) / total_processes, 2) if total_processes else 0
    avg_rt = round(sum(row["rt"] for row in table) / total_processes, 2) if total_processes else 0
    total_time = max((row["ct"] for row in table), default=0)
    context_switches = max(len(gantt) - 1, 0)

    return {
        "table": table,
        "gantt": gantt,
        "averages": {
            "wt": avg_wt,
            "tat": avg_tat,
            "rt": avg_rt,
        },
        "total_time": total_time,
        "context_switches": context_switches,
    }


# =====================================================================
# Step-by-step queue snapshots (replaces the Gantt chart in the UI)
# =====================================================================

def build_steps(processes, gantt, algo):
    """
    Turn the execution slices into "steps" for the ready-queue / running-queue view.

    How long one step lasts depends on the algorithm:
      - FCFS, SJF  : non-preemptive, so no time quantum. A step is the process's full burst.
      - SRTF       : preemptive, checked every 1 ms (time quantum = 1).
      - Round Robin: one step per time-quantum slice (the algorithm already cuts them).

    Each step looks like:
      {"start": 0, "end": 5, "running": "P1" or None (idle),
       "running_remaining": 5,
       "ready": [{"pid": "P2", "remaining": 4}, ...],   # front of the queue first
       "completed": ["P3"],
       "note": "P1 completes, P2 arrives"}
    The ready queue is who is waiting: at the start of the step for SRTF/RR, and at the end of the
    burst for FCFS/SJF (they run a whole burst at once, so anyone who arrived meanwhile was waiting).
    """
    if not processes:
        return []

    info = {p["pid"]: p for p in processes}
    remaining = {p["pid"]: p["bt"] for p in processes}
    arrivals = sorted(processes, key=lambda p: (p["at"], _pid_sort_key(p)))

    # Idle gaps are shown as steps too, so the CPU never "disappears" from the view
    slices = []
    clock = min(p["at"] for p in processes)
    for seg in gantt:
        if seg["start"] > clock:
            slices.append({"pid": None, "start": clock, "end": seg["start"]})
        slices.append(seg)
        clock = seg["end"]

    rr_queue = []        # only used by Round Robin (real queue order matters there)
    in_rr_queue = set()
    completed = []

    def arrive_rr(time):
        # Round Robin keeps its own queue order: arrivals are added behind the others
        for p in arrivals:
            if p["at"] <= time and p["pid"] not in in_rr_queue:
                rr_queue.append(p["pid"])
                in_rr_queue.add(p["pid"])

    def ready_list(time, running):
        if algo == "rr":
            arrive_rr(time)
            pids = [pid for pid in rr_queue if pid != running]
        else:
            pids = [p["pid"] for p in processes
                    if p["at"] <= time and remaining[p["pid"]] > 0 and p["pid"] != running]
            if algo == "fcfs":
                key = lambda pid: (info[pid]["at"], _pid_sort_key(pid))
            elif algo == "sjf":
                key = lambda pid: (info[pid]["bt"], info[pid]["at"], _pid_sort_key(pid))
            else:  # srtf
                key = lambda pid: (remaining[pid], info[pid]["at"], _pid_sort_key(pid))
            pids.sort(key=key)
        return [{"pid": pid, "remaining": remaining[pid]} for pid in pids]

    steps = []
    for seg in slices:
        running = seg["pid"]

        # SRTF re-decides every 1 ms (time quantum = 1); every other case is one step per slice
        if algo == "srtf" and running:
            points = list(range(seg["start"], seg["end"])) + [seg["end"]]
        else:
            points = [seg["start"], seg["end"]]

        for a, b in zip(points, points[1:]):
            if algo == "rr":
                arrive_rr(a)
                if running in rr_queue:
                    rr_queue.remove(running)  # it was popped from the queue to run

            # FCFS/SJF run a whole burst at once, so show everyone who has been waiting
            # by the time it finishes. SRTF/RR show the queue as the step starts.
            ready_time = b if algo in ("fcfs", "sjf") else a

            step = {
                "start": a,
                "end": b,
                "running": running,
                "running_remaining": remaining[running] if running else None,
                "ready_at": ready_time,   # the time this ready queue snapshot belongs to
                "ready": ready_list(ready_time, running),
                "completed": list(completed),
            }

            if running:
                remaining[running] -= (b - a)

            notes = []
            if running and remaining[running] == 0:
                completed.append(running)
                notes.append(f"{running} completes")
            elif running and algo == "rr" and b == seg["end"]:
                notes.append(f"{running} goes back to the queue (quantum over)")
            arrived = [p["pid"] for p in arrivals if a < p["at"] <= b]
            if arrived:
                notes.append(f"{', '.join(arrived)} arrive{'s' if len(arrived) == 1 else ''}")
            step["note"] = ", ".join(notes)

            # Round Robin: arrivals up to the end of the slice go before the preempted process
            if algo == "rr" and b == seg["end"]:
                arrive_rr(b)
                if running and remaining[running] > 0:
                    rr_queue.append(running)

            steps.append(step)

    return steps


def build_warnings(processes):
    """Non-blocking warnings: the simulation still runs when any of these fire."""
    warnings = []
    if len(processes) > 1 and len({p["bt"] for p in processes}) == 1:
        warnings.append(
            f"All processes have the same Burst Time ({processes[0]['bt']} ms). "
            "SJF and SRTF cannot prefer a shorter job, so they will behave like FCFS."
        )
    return warnings
