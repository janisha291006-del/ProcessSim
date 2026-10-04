#1. FCFS  

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


#SJF 
# def sjf(processes):
#     
#     import copy
#     procs = copy.deepcopy(processes)
#     n = len(procs)
#     done = [False] * n
#     time = 0
#     completed = 0
#     table = []
#     gantt = []
#
#     while completed < n:
#         
#         ready = [i for i in range(n) if not done[i] and procs[i]["at"] <= time]
#
#         if not ready:
#             
#             next_arrival = min(procs[i]["at"] for i in range(n) if not done[i])
#             time = next_arrival
#             continue
#
#         
#         idx = min(ready, key=lambda i: (procs[i]["bt"], procs[i]["at"], procs[i]["pid"]))
#         p = procs[idx]
#
#         start = time
#         end = start + p["bt"]
#         gantt.append({"pid": p["pid"], "start": start, "end": end})
#         table.append(_make_table_row(p, end, start))
#
#         time = end
#         done[idx] = True
#         completed += 1
#
#     table.sort(key=lambda r: r["pid"])
#     return table, gantt


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