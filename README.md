# Process Scheduler Simulator

An interactive web-based simulator for classic CPU process scheduling algorithms — visualize Gantt charts, compare performance metrics, and see which scheduling strategy works best for a given set of processes.

## Overview

Process Scheduler Simulator lets you input a set of processes (with arrival time and burst time) and see exactly how the CPU would execute them under different scheduling algorithms. Instead of manually working through Gantt charts and timing tables, this tool computes everything instantly — making it a handy study aid for Operating Systems coursework or a quick way to sanity-check scheduling problems.

Beyond running a single algorithm, the simulator can compare all four algorithms side-by-side on the same process set and automatically highlight which one performs best on each metric.

## Features

- **Four scheduling algorithms**
  - First Come First Serve (FCFS)
  - Shortest Job First (SJF) — non-preemptive
  - Shortest Remaining Time First (SRTF) — preemptive
  - Round Robin (RR) — with configurable time quantum
- **Per-process metrics** — Completion Time (CT), Turnaround Time (TAT), Waiting Time (WT), and Response Time (RT) for every process
- **Gantt chart output** — see the exact execution order and timing
- **Algorithm comparison mode** — runs all four algorithms at once on the same input and picks the best performer per metric (WT, TAT, RT) using pandas
- **Context switch tracking** — counts context switches for preemptive algorithms
- **Simple web interface** — add processes, pick an algorithm, and get results instantly

## Tech Stack

- **Backend:** Python, Flask
- **Data processing:** pandas
- **Frontend:** HTML, CSS, JavaScript

## Getting Started

### Prerequisites

- Python 3.10+

### Installation

```bash
git clone https://github.com/janisha291006-del/ProcessSim.git
cd ProcessSim
pip install -r requirements.txt
```

### Environment setup

Copy the example env file and fill in your own values:

```bash
cp .env.example .env
```

### Run the app

```bash
python app.py
```

Then open `http://localhost:5000` in your browser.

## Usage

1. Add processes with their **arrival time** and **burst time**
2. Choose a scheduling algorithm (and time quantum, if using Round Robin)
3. Click **Simulate** to see the Gantt chart and per-process metrics
4. Or use **Compare All** to see how all four algorithms stack up and which one wins on each metric

## API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Renders the main web interface |
| `/api/simulate` | POST | Runs a single algorithm on the given process list |
| `/api/compare` | POST | Runs all four algorithms and returns the best performer per metric |

## Project Structure

```
process-scheduler/
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── app.js
├── templates/
│   └── index.html
├── algorithms.py
├── app.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you'd like to change.

## License

MIT
