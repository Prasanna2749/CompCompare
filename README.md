# CompCompare — Electronic Component Comparison Web Application

A simple Flask web app to search, compare, and study electronic components, plus a Circuit Lab for practice.

---

## Quick start (Windows) — easiest way

### 1. Install Python
- Install **Python 3.10 or newer** from [python.org/downloads](https://www.python.org/downloads/)
- During install, check **“Add python.exe to PATH”**

### 2. Start the app
1. Open the project folder (wherever you saved it)
2. Double-click **`start.bat`**
3. Wait until you see the server start message
4. Open a browser and go to: **http://127.0.0.1:5000**

That’s it.  
`start.bat` will automatically:
- create a virtual environment (`.venv`) if needed  
- install dependencies from `requirements.txt`  
- create the SQLite database with sample data if it does not exist  
- start the Flask server  

### 3. Stop the app
- Press **Ctrl+C** in the server window, **or**
- Double-click **`stop.bat`**

---

## Optional: run from Command Prompt / PowerShell

From inside the project folder:

```bat
start.bat
```

Or manually:

```bat
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe app.py
```

Then open **http://127.0.0.1:5000**

---

## Run tests (developers)

```bat
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m pytest -v
```

---

## What you can do in the app

1. **Home** — search and browse categories  
2. **Catalog** — filter, sort, open component details  
3. **Compare** — compare 2–3 components side by side  
4. **Lab** — drag Battery / Resistor / LED / LCD and click Run  
5. **About** — project overview  

### Circuit Lab (LCD)
1. Choose problem **5. Hello on LCD**
2. Wire **Battery → Resistor → LCD**
3. Type `lcd.print("Hello ECE")`
4. Click **Run**

---

## Project structure

```text
.
├── start.bat              # Double-click to set up + run (Windows)
├── stop.bat               # Stop the server on port 5000
├── app.py                 # Flask application
├── database.py            # SQLite setup + sample data
├── lab_problems.py        # Circuit Lab problems
├── components.db          # Auto-created on first run
├── requirements.txt
├── README.md
├── static/
├── templates/
└── tests/
```

---

## Notes

- Place this folder anywhere — `start.bat` / `stop.bat` use relative paths (no fixed user path).
- `start.bat` also looks for Python under `%LOCALAPPDATA%\Programs\Python` if PATH is not set.
- No paid APIs or cloud services are required.
- Deleting `components.db` and starting again recreates the sample catalog.
- Keep the `start.bat` window open while using the website.
