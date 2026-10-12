import copy 
import re


def _pid_sort_key(item):
    """Sort key for natural alphanumeric ordering"""
    pid = item["pid"] if isinstance(item, dict) else str(item)
    return [int(part) if part.isdigit() else part.lower() for part in re.split(r'(\d+)', pid)]


def count_context_switches(gantt):
    """Count real context switches: the CPU moves from one process to a different process"""
    runs = [seg["pid"] for seg in gantt]
    return sum(1 for a, b in zip(runs, runs[1:]) if a != b)


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
    sorted_processes = sorted(processes, key=lambda p: (p["at"], _pid_sort_key(p)))

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
    context_switches = count_context_switches(gantt)


    table.sort(key=_pid_sort_key) # to sort processes in the way they were entered not on the basis of when they were scheduled 

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
    context_switches = count_context_switches(gantt)

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
                    ready, key=lambda i: (remaining[i], procs[i]["at"], _pid_sort_key(procs[i]))
                )
        else:
            idx = min(
                ready, key=lambda i: (remaining[i], procs[i]["at"], _pid_sort_key(procs[i]))
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

    table.sort(key=_pid_sort_key)

    # summary averages
    total_processes = len(table)
    avg_wt = round(sum(row["wt"] for row in table) / total_processes, 2)
    avg_tat = round(sum(row["tat"] for row in table) / total_processes, 2)
    avg_rt = round(sum(row["rt"] for row in table) / total_processes, 2)
    total_time = max((row["ct"] for row in table), default=0)
    context_switches = count_context_switches(gantt)

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


# 4. Round Robin

def round_robin(processes, quantum=2):
    
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
    context_switches = count_context_switches(gantt)

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


# Ready Queue / Running Queue rows


def build_queues(processes, gantt, algo):
    """
    Builds the two rows drawn in the lecture notes. Each box = one slice of CPU time:

    Ready Queue row  : every slice in the order processes are served (a process that is
                       put back in the queue shows up again). Used for RR and SRTF.
    Running Queue row: the same slices, but back-to-back slices of the same process are merged
                       (this is the Gantt chart). FCFS and SJF only have this row.
    """
    if not processes:
        return {"ready": [], "running": [], "show_ready": False}

    remaining = {p["pid"]: p["bt"] for p in processes}
    arrivals = sorted(processes, key=lambda p: (p["at"], _pid_sort_key(p)))
    last_arrival = max(p["at"] for p in processes)

    # 1. Execution segments, with idle gaps shown as boxes too
    segments = []
    clock = min(p["at"] for p in processes)
    for seg in gantt:
        if seg["start"] > clock:
            segments.append({"pid": None, "start": clock, "end": seg["start"]})
        segments.append(seg)
        clock = seg["end"]

    # 2. Cut the segments into slices
    slices = []
    for seg in segments:
        points = [seg["start"], seg["end"]]
        if algo == "srtf" and seg["pid"]:
            cuts = [t for t in range(seg["start"] + 1, seg["end"]) if t <= last_arrival]
            points = [seg["start"]] + cuts + [seg["end"]]
        for a, b in zip(points, points[1:]):
            slices.append({"pid": seg["pid"], "start": a, "end": b})

    # 3. Balance time after each slice, completion, and a short note
    ready = []
    for sl in slices:
        pid, a, b = sl["pid"], sl["start"], sl["end"]
        notes = []
        if pid:
            remaining[pid] -= (b - a)
            sl["bal"] = remaining[pid]
            sl["done"] = remaining[pid] == 0
            if sl["done"]:
                notes.append(f"{pid} completes")
            elif algo == "rr":
                notes.append(f"{pid} has {sl['bal']} ms left, so it goes to the back of the queue")
        else:
            sl["bal"] = None
            sl["done"] = False
            notes.append("CPU is idle")

        arrived = [p["pid"] for p in arrivals if a < p["at"] <= b]
        if arrived:
            text = f"{', '.join(arrived)} arrive{'s' if len(arrived) == 1 else ''}"
            if algo == "rr" and pid and not sl["done"]:
                text += f" (they enter the queue before {pid} goes back)"
            notes.append(text)
        sl["note"] = "; ".join(notes)
        ready.append(sl)

    # 4. Running Queue = same slices, back-to-back slices of one process merged
    running = []
    for sl in ready:
        last = running[-1] if running else None
        if last and sl["pid"] and last["pid"] == sl["pid"] and last["end"] == sl["start"]:
            last["end"] = sl["end"]
            last["bal"] = sl["bal"]
            last["done"] = sl["done"]
            last["note"] = "; ".join(n for n in (last["note"], sl["note"]) if n)
        else:
            running.append(dict(sl))

    return {"ready": ready, "running": running, "show_ready": algo in ("rr", "srtf")}


def build_warnings(processes, total_time=None):
    
    warnings = []

    if len(processes) > 1 and len({p["bt"] for p in processes}) == 1:
        warnings.append(
            f"All processes have the same Burst Time ({processes[0]['bt']} ms). This is unlikely in a real system, "
            "where jobs differ in length. SJF and SRTF cannot pick a shorter job here, so they behave like FCFS."
        )

    arrivals = [p["at"] for p in processes]
    if len(set(arrivals)) < len(arrivals):
        warnings.append(
            "Some processes arrive at the same time. When processes tie, the earlier arrival "
            "is picked first, then the lower process ID "
        )

    return warnings
