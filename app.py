
from flask import Flask, jsonify, render_template_string
import sqlite3
import random
from datetime import datetime

app = Flask(__name__)

DB = "sivax.db"


# ---------------- DATABASE ----------------

def init_db():
    con = sqlite3.connect(DB)
    cur = con.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cpu REAL,
            temp REAL,
            battery INTEGER,
            mode TEXT,
            reason TEXT,
            time TEXT
        )
    """)

    con.commit()
    con.close()


init_db()


# ---------------- AI DECISION SYSTEM ----------------

def ai_predict(cpu, temp, battery):

    # Decision-tree-style rules for the simulation

    if temp >= 75 or battery <= 20:
        return "Power Saver", "High temperature or low battery detected"

    elif cpu >= 75:
        return "Performance", "High CPU workload detected"

    elif battery <= 40 or cpu >= 50:
        return "Balanced", "Moderate workload or battery level"

    else:
        return "Power Saver", "Low workload detected; saving energy"


# ---------------- SYSTEM SIMULATION ----------------

def generate_data():
    return {
        "cpu": round(random.uniform(10, 95), 1),
        "temp": round(random.uniform(35, 85), 1),
        "battery": random.randint(10, 100)
    }


# ---------------- DASHBOARD ----------------

HTML = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>SIVAX POWER SAVER</title>

<style>
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    font-family: Arial, sans-serif;
}

body {
    background: #080d18;
    color: white;
    padding: 16px;
}

header {
    padding: 20px 5px;
    text-align: center;
}

header h1 {
    color: #38bdf8;
    font-size: 25px;
}

header p {
    color: #94a3b8;
    margin-top: 8px;
    font-size: 13px;
}

.container {
    max-width: 850px;
    margin: auto;
}

.status {
    background: #111c30;
    padding: 16px;
    border-radius: 15px;
    margin-bottom: 15px;
    text-align: center;
    border: 1px solid #263b5b;
}

.status span {
    color: #4ade80;
    font-weight: bold;
}

.grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
}

.card {
    background: #111c30;
    padding: 18px;
    border-radius: 15px;
    border: 1px solid #263b5b;
}

.card h3 {
    color: #94a3b8;
    font-size: 13px;
    margin-bottom: 14px;
}

.value {
    font-size: 27px;
    font-weight: bold;
}

.unit {
    color: #94a3b8;
    font-size: 13px;
}

.bar {
    height: 9px;
    background: #26364f;
    border-radius: 10px;
    margin-top: 15px;
    overflow: hidden;
}

.fill {
    height: 100%;
    width: 0%;
    background: #38bdf8;
    border-radius: 10px;
    transition: width .4s;
}

.section {
    background: #111c30;
    padding: 20px;
    border-radius: 15px;
    margin-top: 16px;
    border: 1px solid #263b5b;
}

.section h2 {
    font-size: 18px;
    margin-bottom: 15px;
}

.ai {
    color: #38bdf8;
    font-size: 22px;
    font-weight: bold;
    margin: 12px 0;
}

.reason {
    color: #94a3b8;
    font-size: 13px;
    line-height: 1.6;
}

button {
    width: 100%;
    padding: 14px;
    border: none;
    border-radius: 10px;
    margin-top: 12px;
    background: #0284c7;
    color: white;
    font-size: 15px;
    font-weight: bold;
    cursor: pointer;
}

button:active {
    transform: scale(.98);
}

.secondary {
    background: #263b5b;
}

.history-item {
    border-bottom: 1px solid #263b5b;
    padding: 12px 0;
    font-size: 13px;
    color: #cbd5e1;
    line-height: 1.8;
}

footer {
    text-align: center;
    color: #64748b;
    padding: 25px 0;
    font-size: 12px;
}

@media(max-width:380px) {
    body { padding: 10px; }
    .value { font-size: 23px; }
    .card { padding: 13px; }
}
</style>
</head>

<body>

<div class="container">

<header>
    <h1>⚡ SIVAX POWER SAVER</h1>
    <p>AI Based CPU Power Management System</p>
</header>

<div class="status">
    System Status: <span>● ONLINE</span>
    <p style="color:#94a3b8;font-size:12px;margin-top:8px">
        Simulation Environment Active
    </p>
</div>

<div class="grid">

    <div class="card">
        <h3>CPU USAGE</h3>
        <div class="value"><span id="cpu">--</span>%</div>
        <div class="bar"><div class="fill" id="cpuBar"></div></div>
    </div>

    <div class="card">
        <h3>CPU TEMPERATURE</h3>
        <div class="value"><span id="temp">--</span>°C</div>
        <div class="bar"><div class="fill" id="tempBar"></div></div>
    </div>

    <div class="card">
        <h3>BATTERY LEVEL</h3>
        <div class="value"><span id="battery">--</span>%</div>
        <div class="bar"><div class="fill" id="batteryBar"></div></div>
    </div>

    <div class="card">
        <h3>AI STATUS</h3>
        <div class="value" style="font-size:19px;color:#4ade80">
            ACTIVE
        </div>
        <p class="reason">Decision engine running</p>
    </div>

</div>

<div class="section">
    <h2>🤖 AI POWER ANALYSIS</h2>

    <p class="reason">Recommended Power Mode</p>

    <div class="ai" id="mode">Analyzing...</div>

    <p class="reason" id="reason">
        Waiting for system readings...
    </p>

    <button onclick="optimize()">
        ⚡ RUN AI OPTIMIZATION
    </button>

    <button class="secondary" onclick="refreshData()">
        ↻ REFRESH MONITORING
    </button>
</div>

<div class="section">
    <h2>📊 OPTIMIZATION HISTORY</h2>
    <div id="history">No records yet.</div>

    <button class="secondary" onclick="loadHistory()">
        VIEW HISTORY
    </button>

    <button class="secondary" onclick="resetHistory()">
        RESET HISTORY
    </button>
</div>

<footer>
    SIVAX POWER SAVER | CA PROJECT<br>
    AI Based CPU Power Management Simulation
</footer>

</div>

<script>

async function refreshData() {
    try {
        const response = await fetch('/api/status');
        const d = await response.json();

        document.getElementById('cpu').innerText = d.cpu;
        document.getElementById('temp').innerText = d.temp;
        document.getElementById('battery').innerText = d.battery;

        document.getElementById('cpuBar').style.width =
            d.cpu + '%';

        document.getElementById('tempBar').style.width =
            Math.min(d.temp / 100 * 100, 100) + '%';

        document.getElementById('batteryBar').style.width =
            d.battery + '%';

        document.getElementById('mode').innerText = d.mode;
        document.getElementById('reason').innerText = d.reason;

    } catch (error) {
        document.getElementById('reason').innerText =
            'Connection error. Please refresh.';
    }
}

async function optimize() {
    const response = await fetch('/api/optimize', {
        method: 'POST'
    });

    const d = await response.json();

    document.getElementById('cpu').innerText = d.cpu;
    document.getElementById('temp').innerText = d.temp;
    document.getElementById('battery').innerText = d.battery;

    document.getElementById('cpuBar').style.width =
        d.cpu + '%';

    document.getElementById('tempBar').style.width =
        d.temp + '%';

    document.getElementById('batteryBar').style.width =
        d.battery + '%';

    document.getElementById('mode').innerText = d.mode;
    document.getElementById('reason').innerText = d.reason;

    loadHistory();
}

async function loadHistory() {
    const response = await fetch('/api/history');
    const records = await response.json();

    const box = document.getElementById('history');

    if (records.length === 0) {
        box.innerHTML = 'No records yet.';
        return;
    }

    box.innerHTML = records.map(r =>
        `<div class="history-item">
        <b>${r.mode}</b><br>
        CPU: ${r.cpu}% |
        Temperature: ${r.temp}°C |
        Battery: ${r.battery}%<br>
        ${r.reason}<br>
        <small>${r.time}</small>
        </div>`
    ).join('');
}

async function resetHistory() {
    if (!confirm('Delete all history records?')) return;

    await fetch('/api/reset', {method:'POST'});
    loadHistory();
}

refreshData();
loadHistory();

setInterval(refreshData, 5000);

</script>

</body>
</html>
"""


@app.route("/")
def home():
    return render_template_string(HTML)


# ---------------- API: MONITORING ----------------

@app.route("/api/status")
def status():

    data = generate_data()

    mode, reason = ai_predict(
        data["cpu"],
        data["temp"],
        data["battery"]
    )

    data["mode"] = mode
    data["reason"] = reason

    return jsonify(data)


# ---------------- API: OPTIMIZATION ----------------

@app.route("/api/optimize", methods=["POST"])
def optimize():

    data = generate_data()

    mode, reason = ai_predict(
        data["cpu"],
        data["temp"],
        data["battery"]
    )

    con = sqlite3.connect(DB)

    con.execute("""
        INSERT INTO history
        (cpu, temp, battery, mode, reason, time)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        data["cpu"],
        data["temp"],
        data["battery"],
        mode,
        reason,
        datetime.now().strftime("%d-%m-%Y %I:%M:%S %p")
    ))

    con.commit()
    con.close()

    data["mode"] = mode
    data["reason"] = reason

    return jsonify(data)


# ---------------- API: HISTORY ----------------

@app.route("/api/history")
def history():

    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row

    rows = con.execute("""
        SELECT * FROM history ORDER BY id DESC LIMIT 20
    """).fetchall()

    con.close()

    return jsonify([dict(row) for row in rows])


# ---------------- API: RESET ----------------

@app.route("/api/reset", methods=["POST"])
def reset():

    con = sqlite3.connect(DB)
    con.execute("DELETE FROM history")
    con.commit()
    con.close()

    return jsonify({"message": "History reset successfully"})


# ---------------- RUN ----------------

if __name__ == "__main__":
    app.run(debug=True)
