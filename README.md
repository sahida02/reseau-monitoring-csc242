# Supervision et Monitoring d'un Réseau Informatique
**CSC 242 — BIAO-TOURE Sahida**

## Description
Application web de supervision réseau développée en Python/Flask.
Elle permet de stocker les données dans une base SQLite et de visualiser les hôtes du réseau en temps réel.

## Technologies utilisées
- Python 3.x
- Flask (serveur web)
- SQLite (base de données)
- Bootstrap 5 (interface)

## Lancement
pip install -r requirements.txt
python app.py

## Fonctionnalités
- Affichage des hôtes réseau (IP, OS, Services, Statut)
- Démarrer/Arrêter le monitoring
- Export JSON et CSV
- Ajout d'hôtes via API

## API
| Endpoint | Méthode | Description |
|---|---|---|
| / | GET | Page d'accueil |
| /supervision | GET | Tableau de bord |
| /start_monitoring | POST | Démarrer monitoring |
| /stop_monitoring | POST | Arrêter monitoring |
| /export/json | GET | Exporter JSON |
| /export/csv | GET | Exporter CSV |