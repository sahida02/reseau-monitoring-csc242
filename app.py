from flask import Flask, render_template, jsonify, request
import sqlite3
import json
from pathlib import Path

DB = "data/network.db"

def init_db():
    Path("data").mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS hosts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ip TEXT UNIQUE,
        os TEXT,
        services TEXT,
        status TEXT
    )
    """)
    conn.commit()
    conn.close()

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/supervision")
def supervision():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT id, ip, os, services, status FROM hosts")
    rows = c.fetchall()
    conn.close()
    hosts = [{"id": r[0], "ip": r[1], "os": r[2], "services": r[3], "status": r[4]} for r in rows]
    return render_template("supervision.html", hosts=hosts)

@app.route("/add_host", methods=["POST"])
def add_host():
    data = request.get_json()
    ip = data.get("ip")
    os = data.get("os", "Unknown")
    services = data.get("services", "")
    status = data.get("status", "idle")
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO hosts (ip, os, services, status) VALUES (?, ?, ?, ?)",
                  (ip, os, services, status))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    conn.close()
    return jsonify({"ok": True})

@app.route("/start_monitoring", methods=["POST"])
def start_monitoring():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("UPDATE hosts SET status = 'monitoring'")
    conn.commit()
    conn.close()
    return jsonify({"ok": True})

@app.route("/stop_monitoring", methods=["POST"])
def stop_monitoring():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("UPDATE hosts SET status = 'idle'")
    conn.commit()
    conn.close()
    return jsonify({"ok": True})

@app.route("/export/<fmt>")
def export(fmt):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT ip, os, services, status FROM hosts")
    data = c.fetchall()
    conn.close()
    if fmt == "json":
        obj = [{"ip": d[0], "os": d[1], "services": d[2], "status": d[3]} for d in data]
        return jsonify(obj)
    else:
        lines = ["ip,os,services,status"]
        lines += [f"{d[0]},{d[1]},{d[2]},{d[3]}" for d in data]
        csv = "\n".join(lines)
        return csv, 200, {"Content-Type": "text/csv"}

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)