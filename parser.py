import json
import sqlite3
DB = "data/network.db"

def load_json_to_db(json_path="data/sample.json"):
    with open(json_path) as f:
        data = json.load(f)
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    for h in data.get("hosts", []):
        c.execute("INSERT OR REPLACE INTO hosts (ip, os, services, status) VALUES (?, ?, ?, ?)",
                  (h.get("ip"), h.get("os"), ", ".join(h.get("services", [])), h.get("status", "idle")))
    conn.commit()
    conn.close()
