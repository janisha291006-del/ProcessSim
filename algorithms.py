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

    # sorting process by arrival time, then by pid using natural sort
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
    context_switches = max(len(gantt) - 1, 0)

    # Sort table naturally (P1, P2, ..., P9, P10)
    table.sort(key=_pid_sort_key)

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


import copy


def _make_table_row(p, ct, first_start):
    """Build one row of the result table from a process dict."""
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

    max_time = sum(p["bt"] for p in procs) + max(p["at"] for p in procs) + 1

    while completed < n and time <= max_time:
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
            time += 1
            continue

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

    # Sort table naturally (P1, P2, ..., P9, P10)
    table.sort(key=_pid_sort_key)

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

# RR
# def round_robin(processes, quantum=2):
#     
#     import copy
#     procs = copy.deepcopy(processes)
#     n = len(procs)
#     remaining = [p["bt"] for p in procs]
#     first_start = [None] * n
#     completion = [None] * n
#
#     procs_sorted_idx = sorted(range(n), key=lambda i: (procs[i]["at"], procs[i]["pid"]))
#     queue = []
#     gantt = []
#     pointer = 0
#     completed = 0
#
#     time = procs[procs_sorted_idx[0]]["at"]
#
#     def enqueue_arrivals(current_time):
#         nonlocal pointer
#         while pointer < n and procs[procs_sorted_idx[pointer]]["at"] <= current_time:
#             queue.append(procs_sorted_idx[pointer])
#             pointer += 1
#
#     enqueue_arrivals(time)
#
#     while completed < n:
#         if not queue:
#             time = procs[procs_sorted_idx[pointer]]["at"]
#             enqueue_arrivals(time)
#             continue
#
#         idx = queue.pop(0)
#         if first_start[idx] is None:
#             first_start[idx] = time
#
#         run_time = min(quantum, remaining[idx])
#         start = time
#         time += run_time
#         remaining[idx] -= run_time
#         gantt.append({"pid": procs[idx]["pid"], "start": start, "end": time})
#
#         enqueue_arrivals(time)
#
#         if remaining[idx] > 0:
#             queue.append(idx)
#         else:
#             completion[idx] = time
#             completed += 1
#
#     table = []
#     for i, p in enumerate(procs):
#         table.append(_make_table_row(p, completion[i], first_start[i]))
#
#     table.sort(key=lambda r: r["pid"])
#     return table, gantt