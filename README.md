# ProcessSim: CPU Scheduling Simulator

An interactive, easy-to-use web simulator for the **First Come First Serve (FCFS)** and **Shortest Remaining Time First (SRTF)**  CPU process scheduling algorithm. See the Ready Queue and Running process at every step (all steps at once, or one step at a time), calculate timing metrics (CT, TAT, WT, RT), and understand how FIFO process scheduling works in Operating Systems.

## Overview

In First Come First Serve (FCFS) scheduling:
- Processes are executed non-preemptively in the exact chronological order of their arrival into the ready queue.
- If the CPU becomes idle waiting for processes to arrive, it advances time to the next arrival.
In Shortest Remaining Time First (SRTF) scheduling:
  - Processes are executed preemptively based on the shortest remaining burst time.
  - Newly arriving shorter jobs preempt currently running processes, minimizing average waiting time.
- Standard OS metrics are calculated automatically:
  - **Completion Time (CT)**: Time when the process finishes execution.
  - **Turnaround Time (TAT)**: `CT - AT`
  - **Waiting Time (WT)**: `TAT - BT`
  - **Response Time (RT)**: `First Start Time - AT`

## Features

- **Interactive Process Input Table**: Add, remove, or edit process rows with custom Arrival Time (AT) and Burst Time (BT).
- **Ready Queue & Running Process View**: Shows who is on the CPU and who is waiting in the ready queue at every step, either **all steps at once** or **step-by-step**.
- **Input Validation**: A new process cannot arrive earlier than the processes added before it. If every process has the same Burst Time, a warning is shown but the simulation still runs.
- **Process Result Table**: Clearly shows AT, BT, CT, TAT, WT, and RT for every process.
- **Summary Metrics**: Displays Average Waiting Time, Average Turnaround Time, Average Response Time, and Total Schedule Time.

## Comparison & Analysis Screen (Screen 2)

Open the **2. Comparison & Analysis** tab to run FCFS, SJF, SRTF and Round Robin on the same processes.
It shows three headline winners, charts (average times, context switches, waiting time per process)
and 4 AI insights written by Google Gemini. In every chart each algorithm keeps its own color, and the
best bar is outlined.

**Blocking validations (the simulation does not run):**

1.At least one process is required.
2.Every process needs an ID.
3.IDs must be unique, and case-insensitive (P1 and p1 clash).
4.Arrival and burst times are both required.
5.Arrival time must be a whole number.
6.Burst time must be a whole number.
7.Arrival time cannot be negative.
8.Burst time must be at least 1 ms.
9.Round Robin quantum must be a whole number.
10.Round Robin quantum must be at least 1 ms.

**Warnings (the simulation still runs):**
1.The CPU is idle for some time while waiting for processes to arrive.
2.Processes arrive at the same time, and the tie-break rule is explained.

**Gemini setup (needed only for the insights):**
1. Copy `.env.example` to `.env`
2. Put your key in it: `GEMINI_API_KEY=your_real_key` (optional: `GEMINI_MODEL=gemini-3.6-flash`; `gemini-2.5-flash` has been retired by Google)
3. Restart `python app.py`

The key stays on the server and is never sent to the browser. `.env` is already in `.gitignore`.
If Gemini is busy (HTTP 503) the app retries and then tries a backup model automatically.

## Tech Stack

- **Backend:** Python 3, Flask
- **Frontend:** HTML5, CSS3, Vanilla JavaScript

## Getting Started

### 1. Install Dependencies

Make sure you have Python 3 installed:

```bash
pip install -r requirements.txt
```

### 2. Run the Application

```bash
python app.py
```

Then open `http://localhost:5000` in your web browser.

## Project Structure

```
process-scheduler/
├── static/
│   ├── css/
│   │   └── style.css      # Design styling and layout
│   └── js/
│       ├── app.js         # Simulator screen: queue view rendering & API calls
│       └── compare.js     # Comparison screen: charts & Gemini insights
├── templates/
│   └── index.html         # Main dashboard HTML template
├── algorithms.py          # FCFS, SJF, SRTF and Round Robin logic
├── insights.py            # Gemini API call for the 4 insights
├── app.py                 # Flask server and API endpoints
├── requirements.txt       # Python dependencies (Flask, requests, python-dotenv)
└── README.md              # Project documentation
```

## License

MIT
