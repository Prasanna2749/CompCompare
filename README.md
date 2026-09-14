# Electronic Component Comparison Web Application (CompCompare)

CompCompare is a web application for browsing, searching, and comparing electronic components (resistors, capacitors, diodes, LEDs, transistors, inductors, and ICs). It also includes a Circuit Lab where users can drag components into a series strip and run simple validation problems (including an LCD `lcd.print` demo).

**Tech stack:** Python, Flask, SQLite, HTML, CSS, JavaScript  
**Database:** SQLite (created and seeded automatically on first run)  
**External services:** None required (no paid APIs)

---

## Prerequisites

Install the following before setup:

1. **Python 3.10 or newer**  
   - Download: https://www.python.org/downloads/  
   - On Windows, enable **Add python.exe to PATH** during installation  
2. **Git** (to clone the repository)  
   - Download: https://git-scm.com/downloads  
3. A modern web browser (Chrome, Edge, or Firefox)

Verify Python from a terminal:

```bash
python --version
```

If `python` is not found, try:

```bash
py -3 --version
```

or:

```bash
python3 --version
```

Use whichever command works on your system in the steps below.

---

## How to set up and run (command line)

These steps assume **no prior knowledge** of the project. Run all commands from a terminal (Command Prompt, PowerShell, or bash).

### Step 1 — Get the project

**Option A: Clone from GitHub**

```bash
git clone https://github.com/rajshreelakshmi49-sketch/CompCompare.git
cd CompCompare
```

**Option B: If you already have the folder**

```bash
cd path/to/Electronic-Component-Comparison-Web-Application
```

### Step 2 — Create a virtual environment

**Windows (Command Prompt / PowerShell):**

```bat
python -m venv .venv
.venv\Scripts\activate
```

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

When the virtual environment is active, your prompt usually shows `(.venv)`.

### Step 3 — Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

This installs Flask and pytest from `requirements.txt`.

### Step 4 — Configuration

**No manual configuration is required.**

- There is no `.env` file to create  
- There are no API keys  
- The SQLite database file `components.db` is **created automatically** the first time the app starts  
- Sample component data is inserted automatically if the database is empty  

### Step 5 — Run the application

```bash
python app.py
```

Expected result:

- The Flask development server starts on **http://127.0.0.1:5000**
- Open that URL in your browser

Stop the server with **Ctrl+C** in the terminal.

### Step 6 — (Optional) Run automated tests

With the virtual environment still activated:

```bash
pytest -v
```

---

## Windows convenience scripts (optional)

If you are on Windows, you may also use:

- `start.bat` — creates `.venv` if needed, installs dependencies, starts the server  
- `stop.bat` — stops a process listening on port 5000  

These scripts are optional. Evaluators should prefer the **command-line steps** above.

---

## Application overview

After opening http://127.0.0.1:5000:

| Page | Purpose |
|------|---------|
| **Home** | Search bar, category shortcuts, showcase comparison cards |
| **Catalog** | Browse all components; filter by category; sort; open details |
| **Compare** | Compare 2–3 components side by side (cards + table) |
| **Lab** | Drag-and-drop series circuit practice problems |
| **About** | Short project description |

### Circuit Lab quick check

1. Open **Lab**  
2. Select problem **5. Hello on LCD**  
3. Place **Battery → Resistor → LCD** in the series strip  
4. In the Program panel enter: `lcd.print("Hello ECE")`  
5. Click **Run** — the LCD panel should show the message  

For LED problems (1–4), use **Battery → Resistor → LED (forward)** and click **Run**.

---

## Project structure

```text
.
├── README.md              # This file
├── app.py                 # Flask routes and server entry point
├── database.py            # SQLite schema, seed data, queries
├── lab_problems.py        # Circuit Lab problems and validation
├── requirements.txt       # Python dependencies (includes gunicorn)
├── Procfile               # Start command for Render / Heroku-style hosts
├── runtime.txt            # Python version hint for hosting platforms
├── render.yaml            # Optional Render Blueprint
├── start.bat              # Optional Windows one-click start
├── stop.bat               # Optional Windows stop helper
├── static/                # CSS, JavaScript, images
├── templates/             # HTML templates
└── tests/                 # pytest automated tests
```

`components.db` appears after the first successful run (it is gitignored because it is regenerated automatically).

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `python` not recognized | Reinstall Python and enable PATH, or use `py -3` / `python3` |
| Port 5000 already in use | Stop the other process, or change the port in `app.py` |
| Empty / missing database | Delete `components.db` (if present) and run `python app.py` again |
| Module not found | Activate `.venv` and run `pip install -r requirements.txt` |

---

## GitHub submission notes (for authors)

Evaluators typically require:

1. Repository visibility set to **Public**  
2. Root URL only:  
   `https://github.com/rajshreelakshmi49-sketch/CompCompare`  
3. Do **not** submit tree/blob URLs such as `/tree/main/` or `/blob/`  
4. This `README.md` must remain at the **repository root**

---

## Live demo on Render (optional)

This Flask app can be hosted on [Render](https://render.com) to get a public URL.

### A. Push the project to GitHub first

1. Create a **public** GitHub repository  
2. Push this project to `main`  
3. Keep the repository root URL as:  
   `https://github.com/rajshreelakshmi49-sketch/CompCompare`

### B. Create a Render Web Service

1. Sign up / log in at https://dashboard.render.com  
2. Click **New +** → **Web Service**  
3. Connect your GitHub account and select this repository  
4. Use these settings:

| Setting | Value |
|---------|--------|
| Runtime | Python 3 |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `gunicorn app:app --bind 0.0.0.0:$PORT` |
| Instance type | Free |

5. Click **Create Web Service**  
6. Wait for the first deploy to finish  
7. Open the Render URL, for example:  
   `https://your-service-name.onrender.com`

### C. Notes about the free Render plan

- The first visit after idle time may take ~30–60 seconds (cold start)  
- SQLite data may reset when the free instance sleeps or redeploys  
- Sample components are seeded again automatically on startup  

### D. Local production-style check (optional)

```bash
pip install -r requirements.txt
gunicorn app:app --bind 127.0.0.1:5000
```

Then open http://127.0.0.1:5000
