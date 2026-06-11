import re
import sqlite3
import json

DB = "data/network.db"

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    
    # Table des paquets
    c.execute("""
    CREATE TABLE IF NOT EXISTS paquets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        numero TEXT,
        temps TEXT,
        source TEXT,
        destination TEXT,
        protocole TEXT,
        taille TEXT,
        info TEXT
    )
    """)
    
    # Table des alertes
    c.execute("""
    CREATE TABLE IF NOT EXISTS alertes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT,
        source TEXT,
        description TEXT,
        niveau TEXT
    )
    """)
    
    conn.commit()
    conn.close()

def vider_tables():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("DELETE FROM paquets")
    c.execute("DELETE FROM alertes")
    conn.commit()
    conn.close()

def parser_wireshark(chemin="data/capture.txt"):
    init_db()
    vider_tables()
    
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    compteur = 0
    
    # Dictionnaire pour détecter les scans de ports
    # Format : {ip_source: [liste des ports tentés]}
    ports_par_ip = {}
    
    with open(chemin, "r") as f:
        for ligne in f:
            ligne = ligne.strip()
            
            # On ignore la ligne d'en-tête
            if ligne.startswith("No.") or not ligne:
                continue
            
            # Expression régulière pour découper chaque ligne
            # Format : numero  temps  source  destination  protocole  taille  info
            match = re.match(
                r"(\d+)\s+([\d.]+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\d+)\s+(.*)",
                ligne
            )
            
            if match:
                numero = match.group(1)
                temps = match.group(2)
                source = match.group(3)
                destination = match.group(4)
                protocole = match.group(5)
                taille = match.group(6)
                info = match.group(7)
                
                # Insérer le paquet dans la base
                c.execute("""
                INSERT INTO paquets 
                (numero, temps, source, destination, protocole, taille, info)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (numero, temps, source, destination, protocole, taille, info))
                
                compteur += 1
                
                # Détection scan de ports : cherche [SYN] dans l'info
                if "[SYN]" in info and protocole == "TCP":
                    port_match = re.search(r"> (\d+)", info)
                    if port_match:
                        port = port_match.group(1)
                        if source not in ports_par_ip:
                            ports_par_ip[source] = []
                        ports_par_ip[source].append(port)
    
    # Détecter les scans : si une IP a tenté plus de 3 ports différents
    for ip, ports in ports_par_ip.items():
        if len(ports) >= 3:
            c.execute("""
            INSERT INTO alertes (type, source, description, niveau)
            VALUES (?, ?, ?, ?)
            """, (
                "SCAN DE PORTS",
                ip,
                f"IP {ip} a tenté {len(ports)} ports : {', '.join(ports)}",
                "CRITIQUE"
            ))
    
    conn.commit()
    conn.close()
    return compteur

def get_stats():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
    SELECT protocole, COUNT(*) as total 
    FROM paquets 
    GROUP BY protocole 
    ORDER BY total DESC
    """)
    stats = c.fetchall()
    conn.close()
    return stats

def get_alertes():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT type, source, description, niveau FROM alertes")
    alertes = c.fetchall()
    conn.close()
    return alertes

def get_paquets():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT numero, temps, source, destination, protocole, taille, info FROM paquets")
    paquets = c.fetchall()
    conn.close()
    return paquets

def load_json_to_db(json_path="data/sample.json"):
    with open(json_path) as f:
        data = json.load(f)
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
    for h in data.get("hosts", []):
        c.execute("""
        INSERT OR REPLACE INTO hosts (ip, os, services, status) 
        VALUES (?, ?, ?, ?)
        """, (h.get("ip"), h.get("os"), 
              ", ".join(h.get("services", [])), 
              h.get("status", "idle")))
    conn.commit()
    conn.close()