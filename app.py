from flask import Flask, render_template, jsonify, request
import sqlite3
from pathlib import Path
from parser import parser_wireshark, get_stats, get_alertes, get_paquets, init_db, load_json_to_db

DB = "data/network.db"

app = Flask(__name__)
init_db()
load_json_to_db()

def get_hosts():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT id, ip, os, services, status FROM hosts")
    rows = c.fetchall()
    conn.close()
    return [{"id": r[0], "ip": r[1], "os": r[2], "services": r[3], "status": r[4]} for r in rows]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/supervision")
def supervision():
    hosts = get_hosts()
    stats = get_stats()
    alertes = get_alertes()
    paquets = get_paquets()
    return render_template("supervision.html",
                           hosts=hosts,
                           stats=stats,
                           alertes=alertes,
                           paquets=paquets)

@app.route("/importer", methods=["POST"])
def importer():
    nb = parser_wireshark("data/capture.txt")
    return jsonify({"message": f"{nb} paquets importés", "ok": True})

@app.route("/add_host", methods=["POST"])
def add_host():
    data = request.get_json()
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO hosts (ip, os, services, status) VALUES (?,?,?,?)",
                  (data.get("ip"), data.get("os", "Unknown"),
                   data.get("services", ""), data.get("status", "idle")))
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
        return "\n".join(lines), 200, {"Content-Type": "text/csv"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)