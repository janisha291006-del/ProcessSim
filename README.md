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
│       └── app.js         # Frontend logic, queue view rendering & API calls
├── templates/
│   └── index.html         # Main dashboard HTML template
├── algorithms.py          # Clean FCFS simulation logic
├── app.py                 # Flask server and API endpoints
├── requirements.txt       # Python dependencies (Flask)
└── README.md              # Project documentation
```

## License

MIT
