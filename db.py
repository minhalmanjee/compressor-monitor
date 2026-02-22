import sqlite3
from datetime import datetime


DB_NAME = "compressor.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS readings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TXT,
        pressure REAL,
        is_anomaly INTEGER DEFAULT 0
        )    
    """)
    conn.commit()
    conn.close()


def save_reading(pressure, is_anomaly=0):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO readings(timestamp, pressure, is_anomaly) VALUES (?,?,?)", #used ? placeholder to prevent sql injection
        (datetime.now().isoformat(), pressure, is_anomaly)
    )
    conn.commit()
    conn.close()

def get_recent(n=200):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT timestamp, pressure, is_anomaly FROM readings ORDER BY id DESC LIMIT ?", (n,)
    )
    rows = cursor.fetchall()
    conn.close()
    return list(reversed(rows))

    